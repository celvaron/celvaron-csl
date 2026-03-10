# Transformation Pipeline

How to take raw input data through the full pipeline from parsing to graph model to outputs.

---

## 1. Pipeline Overview

```
Raw Input Data
     │
     ▼
[Step 1] Parse Input
     │  Extract structured data from user-provided source (CSV, JSON, text, interview notes)
     ▼
[Step 2] Map to CSL Entities
     │  Apply entity-mapping rules to produce CSL entity blocks
     ▼
[Step 3] Generate CSL Source (.csl)
     │  Write syntactically valid CSL text
     ▼
[Step 4] Validate CSL
     │  Run all 5 validation layers; fix errors before proceeding
     ▼
[Step 5] Transform to Graph Model (JSON)
     │  Parse validated CSL into canonical node/edge JSON
     ▼
[Step 6] Enrich Graph Model
     │  Compute derived fields: centralityScore, impactScore, criticalPath, etc.
     ▼
[Step 7] Generate Outputs
        ├─ Diagrams (Mermaid / SVG)
        ├─ Reports (HTML / Markdown)
        ├─ Exports (Neo4j Cypher, CSV, etc.)
        └─ AI Reasoning Context
```

---

## 2. Step 1: Parse Input

Accept input in any of these formats:

| Format | How to Handle |
|---|---|
| JSON object | Map keys directly to entity fields using entity-mapping guide |
| CSV file | Each row is one entity; columns are fields |
| Free-text / interview notes | Use NLP / LLM extraction to identify entities and relationships |
| Existing CSL file | Skip to Step 4 (validate) |
| Graph model JSON | Skip to Step 6 (enrich) |

### Input Parsing Rules

1. Strip extraneous whitespace and formatting
2. Normalize names to PascalCase (see naming rules in entity-mapping guide)
3. Detect implicit relationships (e.g., "Team A runs Process B" → `process.performedBy: TeamA`)
4. Flag ambiguous data for human review using `meta.confidence: "low"`

### Pseudocode

```python
def parse_input(source, format):
    if format == "json":
        data = json.load(source)
    elif format == "csv":
        data = list(csv.DictReader(source))
    elif format == "text":
        data = extract_entities_from_text(source)  # LLM extraction step
    return data
```

---

## 3. Step 2: Map to CSL Entities

For each parsed data item, determine the entity type and field mapping.

### Decision Tree

```
Does it describe the whole organization?
  └─ Yes → company

Does it describe a group of customers?
  └─ Yes → segment

Does it describe a geographic/industry market?
  └─ Yes → market

Does it describe something the company sells/delivers?
  └─ Yes → offering

Does it describe a transformation/result for clients?
  └─ Yes → outcome

Does it describe an organizational skill or ability?
  └─ Yes → capability

Does it describe a group of people who own work?
  └─ Yes → team

Does it describe how work gets done step by step?
  └─ Yes → process (and steps)

Does it describe how an offering is bundled and priced?
  └─ Yes → package

Does it describe a technology tool or platform?
  └─ Yes → system

Does it describe a strategic company goal?
  └─ Yes → objective

Does it describe a KPI or measurement?
  └─ Yes → metric
```

### Pseudocode

```python
def map_to_entities(parsed_data, entity_type_hints=None):
    entities = []
    for item in parsed_data:
        entity_type = detect_entity_type(item, entity_type_hints)
        entity_name = to_pascal_case(item.get("name", "Unknown"))
        fields = apply_field_mapping(item, entity_type)
        entities.append(CSLEntity(type=entity_type, name=entity_name, fields=fields))
    return entities
```

---

## 4. Step 3: Generate CSL Source

Convert the mapped entity list into valid CSL text.

### Generation Rules

1. One entity per block
2. Only include fields where data exists (no empty fields)
3. Add `status: "draft"` and `meta.confidence: "low"` to entities with incomplete data
4. Add `// TODO:` comments for required fields that are missing
5. Sort entities: company first, then markets, segments, outcomes, offerings, capabilities, teams, roles, processes, steps, packages, systems, objectives, metrics

### Template Pattern

```python
def generate_csl_block(entity):
    lines = []
    lines.append(f"{entity.type} {entity.name} {{")
    for field, value in entity.fields.items():
        lines.append(f"  {field}: {format_value(value)}")
    if entity.has_missing_required_fields():
        for field in entity.missing_required_fields():
            lines.append(f"  // TODO: {field} (required — must be added before validation)")
    lines.append("}")
    return "\n".join(lines)

def format_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, list):
        items = ", ".join(format_value(v) for v in value)
        return f"[{items}]"
    elif isinstance(value, dict):
        inner = "\n    ".join(f"{k}: {format_value(v)}" for k, v in value.items())
        return "{\n    " + inner + "\n  }"
    else:
        return str(value)
```

---

## 5. Step 4: Validate CSL

Run all 5 validation layers in order. See [validation-error-handling.md](validation-error-handling.md) for full rules.

```python
def validate(csl_source):
    result = ValidationResult()

    # Layer 1: Syntax
    ast, syntax_errors = parse_csl(csl_source)
    result.add(syntax_errors)
    if result.has_blocking_errors():
        return result  # stop here

    # Layer 2: References
    ref_errors = validate_references(ast)
    result.add(ref_errors)
    if result.has_blocking_errors():
        return result

    # Layer 3: Structure
    struct_errors = validate_structure(ast)
    result.add(struct_errors)
    if result.has_blocking_errors():
        return result

    # Layer 4: Semantics
    semantic_warnings = validate_semantics(ast)
    result.add(semantic_warnings)

    # Layer 5: Completeness
    completeness_suggestions = validate_completeness(ast)
    result.add(completeness_suggestions)

    return result
```

**Fix loop:** If errors are returned, fix them in the CSL source and re-run validation before proceeding to Step 5.

---

## 6. Step 5: Transform to Graph Model (JSON)

Convert the validated CSL AST to the canonical JSON graph model.

### Node Generation

For each entity in the AST:

```python
def entity_to_node(entity):
    return {
        "id": f"{entity.type}:{entity.name}",
        "type": entity.type,
        "name": entity.name,
        "attributes": {
            field: value
            for field, value in entity.fields.items()
            if not is_relationship_field(field)
        }
    }
```

### Edge Generation

For each relationship field on each entity:

```python
RELATIONSHIP_FIELDS = {
    "targets": ("offering", "segment", "targets"),
    "operatesIn": ("offering", "market", "operatesIn"),
    "delivers": ("offering", "outcome", "delivers"),
    "requires": ("offering", "capability", "requires"),
    "ownedBy": ("capability", "team", "ownedBy"),
    "dependsOn": ("capability|step", "capability|step", "dependsOn"),
    "supports": ("capability", "offering", "supports"),
    "performedBy": ("process|step", "team|role", "performedBy"),
    "uses": ("process|step", "system", "uses"),
    "hasStep": ("process", "step", "hasStep"),
    "partOf": ("step", "process", "partOf"),
    "owns": ("team", "capability", "owns"),
    "measuredBy": ("offering|objective", "metric", "measuredBy"),
    "contributesTo": ("offering|capability", "objective", "contributesTo"),
    "achievedThrough": ("outcome", "offering", "achievedThrough"),
}

def entity_to_edges(entity):
    edges = []
    for field, value in entity.fields.items():
        if field in RELATIONSHIP_FIELDS:
            refs = value if isinstance(value, list) else [value]
            for ref in refs:
                edges.append({
                    "from": f"{entity.type}:{entity.name}",
                    "to": f"{get_target_type(field)}:{ref.name}",
                    "type": field,
                    "attributes": ref.attributes if hasattr(ref, "attributes") else {}
                })
    return edges
```

### Graph Model Assembly

```python
def build_graph_model(ast, meta_overrides=None):
    nodes = [entity_to_node(e) for e in ast.entities]
    edges = [edge for e in ast.entities for edge in entity_to_edges(e)]

    meta = {
        "modelVersion": "1.0",
        "cslVersion": "1.0",
        "companyId": slugify(ast.get_company().name),
        "state": meta_overrides.get("state", "asis"),
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "generator": "csl-transformer-v1.0"
    }
    if meta_overrides:
        meta.update(meta_overrides)

    return {"meta": meta, "nodes": nodes, "edges": edges}
```

---

## 7. Step 6: Enrich Graph Model

Add computed fields that enable analysis. These are calculated from the graph structure, not stored in CSL source.

### Node Computed Fields

| Field | How to Compute |
|---|---|
| `centralityScore` | Degree centrality: `(in_degree + out_degree) / (total_nodes - 1)` |
| `impactScore` | Sum of `fitScore` from targets edges + `impact` from contributesTo edges, normalized 0–1 |
| `complexity` | Count of dependsOn/requires edges: 0 = `low`, 1–3 = `medium`, 4+ = `high` |
| `riskScore` | For capabilities: if `maturity.current` is `basic` and `criticality` is `high`, riskScore = 0.9 |

### Edge Computed Fields

| Field | How to Compute |
|---|---|
| `weight` | Default 1.0; increase by 0.1 for each attribute that signals importance (criticality: high, priority: primary) |
| `criticalPath` | True if this edge is on the shortest path between the company node and any high-impact outcome node |

### Enrichment Pseudocode

```python
def enrich_graph(graph):
    G = build_networkx_graph(graph)

    for node in graph["nodes"]:
        node_id = node["id"]
        node["computed"] = {
            "centralityScore": round(nx.degree_centrality(G)[node_id], 4),
            "impactScore": compute_impact_score(node, graph),
            "complexity": compute_complexity(node, graph)
        }

    critical_edges = compute_critical_paths(G)
    for edge in graph["edges"]:
        edge_key = (edge["from"], edge["to"])
        edge["computed"] = {
            "weight": compute_edge_weight(edge),
            "criticalPath": edge_key in critical_edges
        }

    return graph
```

---

## 8. Step 7: Generate Outputs

### 8.1 Mermaid Diagram

```python
def generate_mermaid(graph, view_type):
    view_config = VIEWS[view_type]
    filtered_nodes = filter_nodes(graph["nodes"], view_config["focus"])
    filtered_edges = filter_edges(graph["edges"], view_config["relationships"], filtered_nodes)

    lines = ["graph TD"]
    for node in filtered_nodes:
        label = f'{node["name"]} ({node["type"]})'
        safe_id = node["id"].replace(":", "_")
        lines.append(f'    {safe_id}["{label}"]')

    for edge in filtered_edges:
        from_id = edge["from"].replace(":", "_")
        to_id = edge["to"].replace(":", "_")
        lines.append(f"    {from_id} --> {to_id}")

    return "\n".join(lines)
```

### 8.2 JSON Export

Simply serialize the enriched graph model to JSON:

```python
import json

def export_json(graph, path, pretty=True):
    with open(path, "w") as f:
        json.dump(graph, f, indent=2 if pretty else None)
```

### 8.3 Neo4j Cypher Export

```python
def export_cypher(graph):
    lines = []
    for node in graph["nodes"]:
        props = json.dumps(node["attributes"])
        lines.append(f'CREATE (:{node["type"]} {{id: "{node["id"]}", {props}}});')

    for edge in graph["edges"]:
        lines.append(
            f'MATCH (a {{id: "{edge["from"]}"}}) MATCH (b {{id: "{edge["to"]}"}}) '
            f'CREATE (a)-[:{edge["type"].upper()}]->(b);'
        )
    return "\n".join(lines)
```

---

## 9. Full Pipeline Example

```python
# 1. Load input
with open("data/company.json") as f:
    raw_data = json.load(f)

# 2. Map to entities
entities = map_to_entities(raw_data, entity_type_hints={"root": "company"})

# 3. Generate CSL
csl_source = "\n\n".join(generate_csl_block(e) for e in entities)
with open("draft/model.csl", "w") as f:
    f.write(csl_source)

# 4. Validate
result = validate(csl_source)
if result.has_blocking_errors():
    print(result.format_errors())
    sys.exit(1)

# 5. Transform
ast = parse_csl(csl_source)
graph = build_graph_model(ast, meta_overrides={"state": "asis", "author": "agent"})

# 6. Enrich
graph = enrich_graph(graph)

# 7. Generate outputs
export_json(graph, "output/graph.json", pretty=True)
mermaid = generate_mermaid(graph, view_type="architecture")
with open("output/architecture.md", "w") as f:
    f.write(f"```mermaid\n{mermaid}\n```\n")

print("Pipeline complete.")
```
