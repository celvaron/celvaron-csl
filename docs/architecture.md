# CSL Architecture Overview

---

## System Architecture

```
┌─────────────────┐
│   CSL Source    │  (.csl files - human-authored)
│     Files       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   CSL Parser    │  (validates, transforms)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Graph Model    │  (canonical JSON representation)
│   {meta, nodes, │
│    edges}       │
└────────┬────────┘
         │
         ├──────────────┬──────────────┬───────────────┐
         ↓              ↓              ↓               ↓
┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
│Visualization│  │ Validation│  │ Analytics│  │   Agent    │
│  Engines    │  │   Tools   │  │  Tools   │  │  Reasoning │
└─────────────┘  └──────────┘  └──────────┘  └────────────┘
         │              │              │               │
         ↓              ↓              ↓               ↓
   Diagrams        Reports       Insights        Recommendations
```

CSL source files are authored by humans (or agents). The parser validates and transforms them into the **Graph Model** — a canonical JSON representation that all downstream tools consume. From the graph, you can generate visualizations, run validation, perform analytics, or feed agent reasoning.

---

## Recommended Project Structure

When working on a real engagement, organize files as follows:

```
project/
├── asis/
│   ├── model.csl                 # Current state model
│   └── knowledge/
│       ├── offerings/
│       ├── capabilities/
│       └── processes/
├── tobe/
│   ├── model.csl                 # Future state model
│   └── knowledge/
├── evidence/
│   ├── interviews/
│   ├── documents/
│   └── data/
└── output/
    ├── graphs/
    ├── diagrams/
    └── reports/
```

- `asis/` and `tobe/` each have their own model and a knowledge base of supporting detail
- `evidence/` holds raw source material — interview notes, documents, data files
- `output/` is generated and should not be committed (or kept separately)

See [as-is-to-be.md](as-is-to-be.md) for guidance on working with two model states.

---

## Processing Pipeline

Each CSL model goes through these stages:

1. **Parse** — CSL source → Abstract Syntax Tree (AST)
2. **Validate** — Check syntax, entity references, and constraint rules
3. **Schema resolve** — If a `schema` block is present, validate it and attach section/relation metadata to the AST; if absent, mark all fields for inference
4. **Transform** — AST → Graph Model (JSON); each edge gains a `relationKind` field (`"composition"`, `"association"`, `"dependency"`, `"extension"`, or `null` when inferred)
5. **Enrich** — Add computed fields (centrality scores, impact scores, etc.)
6. **Generate** — Graph → Views (Mermaid diagrams, SVG, React)
7. **Analyze** — Run queries, comparisons, simulations

The `tools/` directory provides reference implementations for steps 1–5:

| Tool | Stage | Command |
|---|---|---|
| `validate_csl.py` | Parse + Validate | `python tools/validate_csl.py model.csl` |
| `transform_csl.py` | Transform | `python tools/transform_csl.py model.csl -o output/graph.json` |
| `generate_diagram.py` | Generate | `python tools/generate_diagram.py output/graph.json --view architecture` |
| `parse_input.py` | Pre-parse (CSV/JSON → CSL) | `python tools/parse_input.py input.csv -o model.csl` |

See [tool-usage.md](tool-usage.md) for full command reference.

---

## Schema-Aware Rendering

When the `schema` block is present in a model, the graph model carries its declarations in `meta.schema`. Downstream consumers should use this to avoid hardcoding section assignments and relation semantics:

| Consumer task | Without schema | With schema |
|---|---|---|
| Assign entity to display section | Apply built-in type→section map | Read `meta.schema.sections` |
| Decide whether to nest a child under parent | Heuristic (field name pattern matching) | Read `meta.schema.relations[field].kind` — `composition` = nest |
| Render cross-reference as badge vs. arrow | Heuristic | `association` = badge/chip; `dependency` = arrow; `extension` = dashed link |
| Traverse from child to parent | Hardcoded reverse-field conventions | Read `meta.schema.relations[field].inverse` |

Consumers that do not understand the `schema` block should ignore `meta.schema` and fall back to their existing inference logic. This ensures backward compatibility for all consumer implementations.
