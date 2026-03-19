# Agent-Specific Recommendations

Guidance for AI agents, RPA bots, and software systems generating, processing, and reasoning over CSL models.

---

## 1. AI Language Model Agents (LLM-based)

### 1.1 Recommended Context Loading Order

When an LLM agent needs to generate or analyze a CSL model, load context in this priority order:

1. [entity-mapping.md](entity-mapping.md) — which entity types exist and how data maps to them
2. [syntax-structure.md](syntax-structure.md) — how to write syntactically valid CSL
3. [validation-error-handling.md](validation-error-handling.md) — what makes a model valid
4. [best-practices-templates.md](best-practices-templates.md) — quality patterns
5. The graph model JSON of the existing company (if available) — for reasoning and analysis

**Do not** load the raw `.csl` source as reasoning context. Load the graph model JSON instead — it is structured and unambiguous.

---

### 1.2 System Prompt Template for CSL Generation

Use this system prompt when asking an LLM to generate CSL from company data:

```
You are a CSL (Company Specification Language) modeling expert. Your task is to generate 
a valid CSL model from the company data provided.

Rules:
1. Every entity name must be PascalCase (e.g., ServiceProductization, StrategyTeam).
2. Every field name must be camelCase (e.g., targets, performedBy).
3. The model must have exactly one 'company' entity.
4. Every 'offering' must have at least one target segment, one required capability, 
   and one delivered outcome.
5. Every 'capability' must have an 'ownedBy' field referencing a team.
6. Every 'package' must reference an offering and have a pricing.basePrice.
7. All entity references must resolve — only reference entities you have defined.
8. If data is missing for a required field, add a comment: // TODO: <field> — <reason>
9. Set status: "draft" and meta.confidence: "low" on any entity with missing or 
   estimated data.
10. Output only valid CSL. Do not include explanations outside of CSL comments.
11. NEVER use 'requires' on a process or step. 'requires' is only valid on offering.
    Express capability dependencies via: offering { requires: [CapabilityName] }
12. NEVER use 'contributesTo' on any entity. It has been removed.
    Link objectives via: objective { achievedThrough: [OfferingName] }
13. NEVER use 'capability.supports', 'team.owns', 'outcome.achievedThrough',
    'process.supports', 'system.usedBy', 'system.supports', or 'offering.packages'.
    These fields are deprecated. Use the canonical directions:
    - offering.requires (not capability.supports)
    - offering.delivers (not outcome.achievedThrough)
    - capability.ownedBy (not team.owns)
    - objective.achievedThrough (not offering.contributesTo)
    - package.offering (not offering.packages)
    - process.uses (not system.supports / system.usedBy)
14. NEVER use 'targets', 'delivers', or 'operatesIn' on a process, capability, or step.
    These fields are only valid on offering.
15. Every 'company' entity must include: name, description, industry, size, stage.
16. Every 'segment' entity must include: description, size, operatesIn.
17. Every 'objective' entity must include: description, timeframe, measuredBy, achievedThrough.
18. Every 'process' entity must include: description, performedBy, measuredBy.
19. Every 'step' entity must include: description, partOf, performedBy, order.
20. Every 'metric' entity should use flat fields: target, baseline, frequency (not nested targets{}/measurement{}).
```

---

### 1.3 Prompting for CSL from Interview / Discovery Notes

```
Given the following discovery notes about a company, generate a complete CSL model.

Focus on:
- Extracting all mentioned services/products as 'offering' entities
- Identifying customer groups as 'segment' entities
- Identifying key skills/capabilities the company uses
- Identifying teams and who does what
- Identifying business goals as 'objective' entities

Discovery Notes:
[INSERT NOTES HERE]

Generate the CSL model. Start with the company entity, then markets/segments, 
then outcomes, then offerings, then capabilities, teams, processes, and packages.
```

---

### 1.4 Prompting for Analysis

Once a graph model JSON exists, agents can reason over it directly:

```
You are analyzing a company model in CSL Graph Model JSON format.

The model represents a service company. Analyze it and answer:
1. What are the most central capabilities (highest centralityScore)?
2. Which offerings have the highest economic impact?
3. Are there any orphan entities (nodes with no edges)?
4. Which capabilities are critical but have low maturity?
5. Are there any offerings that lack packages?

Graph Model JSON:
[INSERT GRAPH MODEL JSON HERE]
```

---

### 1.5 Incremental Generation Strategy

For large companies, generate the model incrementally rather than all at once:

1. **Pass 1 — Skeleton:** Generate company + all offering/segment names (no details)
2. **Pass 2 — Offerings:** Fill in each offering with targets, requires, delivers
3. **Pass 3 — Capabilities + Teams:** For each capability referenced, generate the entity
4. **Pass 4 — Processes + Steps:** Generate operational workflows
5. **Pass 5 — Packages + Pricing:** Generate commercial structure
6. **Pass 6 — Objectives + Metrics:** Add strategic layer

After each pass, validate before proceeding to the next.

---

### 1.7 Post-Generation Self-Audit Checklist

Before outputting the final CSL model, iterate over every entity in the draft and run these checks. Do not skip this step.

**For every `process` and `step` entity:**
- [ ] Does it contain `requires`? → **Remove it.** Use `offering { requires: [CapabilityName] }` to express the dependency.
- [ ] Does it contain `contributesTo`? → **Remove it.** Link via `objective { achievedThrough: [OfferingName] }` instead.
- [ ] Does it contain `supports`? → **Remove `process.supports`.** This field is deprecated and should not appear.

**For every `capability` entity:**
- [ ] Does it contain `supports`? → **Remove it.** The canonical direction is `offering.requires: [CapabilityName]`.
- [ ] Does it have `ownedBy`? → **Required.** Every capability must declare `ownedBy: TeamName`.
- [ ] Does it have `maturity.current`? → **Required.** Add `maturity: { current: "basic|intermediate|advanced|expert" }`.

**For every `team` entity:**
- [ ] Does it contain `owns`? → **Remove it.** Use `capability.ownedBy: TeamName` on each capability instead.
- [ ] Does it have `size`? → **Required.** Add `size: N` (plain number or `{ current: N, target: N }`).

**For every `offering` entity:**
- [ ] Does it contain `contributesTo`? → **Remove it.** Deprecated.
- [ ] Does it contain `packages`? → **Remove it.** Deprecated. Use `package.offering: OfferingName` on each package.
- [ ] Does it have `economics.avgDealSize` and `economics.targetMargin`? → **Required.**

**For every `objective` entity:**
- [ ] Does it contain `contributedBy`? → **Remove it.** Replace with `achievedThrough: [OfferingName]`.
- [ ] Does it have `timeframe`? → **Required.**
- [ ] Does it have `measuredBy` and `achievedThrough`? → **Required.**

**For every `system` entity:**
- [ ] Does it contain `usedBy` or `supports`? → **Remove both.** Reference systems via `process.uses` instead.

**For every entity that is NOT `offering`:**
- [ ] Does it contain `targets`? → **Remove it.** Only `offering` may target segments.
- [ ] Does it contain `delivers`? → **Remove it.** Only `offering` delivers outcomes.
- [ ] Does it contain `operatesIn`? → **Remove it.** Only `offering` operates in markets.

**For every entity reference in the model:**
- [ ] Is the referenced entity declared somewhere in the model? If not, either declare it or replace with a `// TODO` comment.

Only proceed to output after all checks pass.

---

### 1.6 Hallucination Prevention Rules

| Risk | Prevention |
|---|---|
| Agent invents entity names that don't exist | Only reference entities already declared in the model |
| Agent uses wrong field names | Always verify against [syntax-structure.md](syntax-structure.md) |
| Agent uses wrong entity type | Confirm entity type with the decision tree in [entity-mapping.md](entity-mapping.md) |
| Agent generates circular references | Check step dependencies are acyclic before outputting |
| Agent omits required fields | Explicitly check required fields per entity type before finalizing |

---

## 2. RPA (Robotic Process Automation) Agents

### 2.1 Recommended Workflow

RPA agents work best with structured input data (CRMs, spreadsheets, databases). The recommended pipeline:

```
CRM / Spreadsheet / Database
        │
        ▼
[Extract] → Pull company, team, service, client data
        │
        ▼
[Map] → Apply field mapping tables from entity-mapping.md
        │
        ▼
[Generate] → Build CSL blocks using syntax templates
        │
        ▼
[Validate] → Run validate_csl.py
        │
        ▼
[Store] → Commit .csl file to repository
        │
        ▼
[Transform] → Run transform_csl.py → graph.json
        │
        ▼
[Report] → Generate diagrams or reports as needed
```

---

### 2.2 Field Extraction Rules for CRM Data

| CRM Field | CSL Entity | CSL Field |
|---|---|---|
| Company Name | company | name |
| Industry | segment | characteristics.industry |
| Annual Revenue | segment | characteristics.revenueRange |
| Employee Count | team | size.current |
| Product/Service Name | offering | entity name |
| Deal Value | package | pricing.basePrice |
| Win Rate | offering | performance.conversionRate |
| Sales Cycle (days) | offering | performance.avgSalesCycle |
| Customer Since | — | meta.lastReviewed |
| Renewal Rate | offering | performance.clientRetention |

---

### 2.3 Trigger-Based Updates

RPA agents should regenerate and re-validate the CSL model when:
- A new service/offering is added to the CRM catalog
- Team structure changes (headcount, roles)
- Pricing is updated
- A new major customer segment is identified
- Quarterly performance data is refreshed

---

## 3. Software Systems (APIs, Microservices)

### 3.1 API Integration Pattern

Systems consuming CSL models should work with the graph model JSON, not raw CSL:

```python
import requests
import json

# Load graph model from storage
with open("output/graph.json") as f:
    graph = json.load(f)

# Query specific nodes by type
offerings = [n for n in graph["nodes"] if n["type"] == "offering"]

# Find relationships
def get_targets(offering_id, graph):
    return [
        e["to"] for e in graph["edges"]
        if e["from"] == offering_id and e["type"] == "targets"
    ]

# Get all segments for ServiceProductization
targets = get_targets("offering:ServiceProductization", graph)
```

---

### 3.2 Graph Query Patterns

Common queries on the graph model JSON:

```python
# 1. Find all offerings and their packages
def get_offering_packages(graph):
    result = {}
    for node in graph["nodes"]:
        if node["type"] == "offering":
            packages = [
                e["from"] for e in graph["edges"]
                if e["to"] == node["id"] and e["type"] == "bundledIn"
            ]
            result[node["name"]] = packages
    return result

# 2. Find capabilities with no owning team
def find_unowned_capabilities(graph):
    owned = {e["from"] for e in graph["edges"] if e["type"] == "ownedBy"}
    all_caps = {n["id"] for n in graph["nodes"] if n["type"] == "capability"}
    return all_caps - owned

# 3. Find the most central node (highest centralityScore)
def top_central_nodes(graph, n=5):
    return sorted(
        graph["nodes"],
        key=lambda x: x.get("computed", {}).get("centralityScore", 0),
        reverse=True
    )[:n]

# 4. Trace the value chain from an offering to outcomes
def trace_value_chain(offering_name, graph):
    offering_id = f"offering:{offering_name}"
    outcomes = [
        e["to"] for e in graph["edges"]
        if e["from"] == offering_id and e["type"] == "delivers"
    ]
    return outcomes
```

---

### 3.3 Webhook / Event-Driven Updates

For systems that need to stay in sync with the CSL model:

```python
# When the model changes, re-process downstream systems
def on_model_update(csl_path):
    # 1. Validate
    result = validate(csl_path)
    if result.has_blocking_errors():
        notify_team(result.errors)
        return

    # 2. Transform
    graph = transform(csl_path)
    save("output/graph.json", graph)

    # 3. Enrich
    graph = enrich(graph)
    save("output/graph_enriched.json", graph)

    # 4. Generate outputs
    for view in ["architecture", "capability-map", "value-stream"]:
        mermaid = generate_mermaid(graph, view)
        save(f"output/{view}.md", mermaid)

    # 5. Notify consumers
    emit_event("model.updated", {"graph_path": "output/graph.json"})
```

---

## 4. Cross-Agent Collaboration

When multiple agents work with the same CSL model:

### 4.1 Read Model (any agent)
- Always load the graph model JSON, not raw CSL
- Use the `meta.snapshotDate` to check model freshness
- If older than 24 hours, consider re-running the transformation pipeline

### 4.2 Write Model (LLM agent)
1. Load current `model.csl`
2. Output modified or new entities as a CSL patch (new blocks only)
3. Validate the patch against the existing model
4. If valid, the orchestrating system merges the patch into `model.csl`
5. Re-run transformation pipeline

### 4.3 Conflict Resolution
- If two agents update the same entity, the later write wins by default
- Use `meta.lastReviewed` and `meta.reviewer` to track provenance
- Flag conflicts in `meta.notes` with timestamp

---

## 5. Quality Assurance for Agent-Generated Models

Before accepting any agent-generated CSL model as production-ready:

| Check | Method |
|---|---|
| Syntax valid | Run `validate_csl.py` — must pass with 0 errors |
| All required fields present | Run `validate_csl.py --strict` |
| No orphan entities | Check validation output for W010 warnings |
| Offerings have packages | Check for W001 warnings |
| Value chain complete | All offerings → outcomes → economicValue |
| Names are meaningful | Human review of entity names for vagueness |
| Confidence levels set | All `meta.confidence` fields populated |
| Draft entities flagged | All incomplete entities have `status: "draft"` |

A model should only be marked `status: "active"` after all these checks pass and a human reviewer has signed off.
