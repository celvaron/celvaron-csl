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
3. **Transform** — AST → Graph Model (JSON)
4. **Enrich** — Add computed fields (centrality scores, impact scores, etc.)
5. **Generate** — Graph → Views (Mermaid diagrams, SVG, React)
6. **Analyze** — Run queries, comparisons, simulations

The `tools/` directory provides reference implementations for steps 1–5:

| Tool | Stage | Command |
|---|---|---|
| `validate_csl.py` | Parse + Validate | `python tools/validate_csl.py model.csl` |
| `transform_csl.py` | Transform | `python tools/transform_csl.py model.csl -o output/graph.json` |
| `generate_diagram.py` | Generate | `python tools/generate_diagram.py output/graph.json --view architecture` |
| `parse_input.py` | Pre-parse (CSV/JSON → CSL) | `python tools/parse_input.py input.csv -o model.csl` |

See [tool-usage.md](tool-usage.md) for full command reference.
