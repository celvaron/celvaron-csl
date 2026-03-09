# Celvaron CSL — Company Specification Language

An open standard for describing companies as structured, machine-readable models.

---

## What is CSL?

CSL (Company Specification Language) is a domain-specific language for capturing the complete structure, operation, and commercial model of a service-based company in a format that both humans and machines can read, validate, and reason over.

A CSL model describes:
- **Who** you serve (segments, markets)
- **What** you deliver (offerings, packages, outcomes)
- **How** you deliver it (capabilities, teams, processes, steps)
- **Why it matters** (objectives, metrics, economic value)

---

## Key Concepts

| Concept | Description |
|---|---|
| **Entity** | A named block representing a real business element (company, offering, team, etc.) |
| **Relationship** | A directional link between entities (targets, requires, ownedBy, etc.) |
| **Graph Model** | The canonical JSON representation of the entire CSL model |
| **AS-IS / TO-BE** | Two model states: current reality vs. desired future state |

---

## Why Use CSL?

Traditional company documentation is scattered and inconsistent. CSL provides:

- **One source of truth** — one model, many outputs
- **Validation** — syntax and semantic rules enforced automatically
- **Multiple views** — architecture, capability map, process flow, journey map, and more
- **Agent-ready** — structured format that AI agents can directly parse and reason over
- **Version control** — track changes, compare AS-IS vs. TO-BE, plan transformations

---

## Repository Structure

```
celvaron-csl/
├── README.md                           ← You are here
│
├── docs/
│   ├── csl_specification.md            ← Full CSL language specification
│   ├── csl_quick_reference.md          ← Syntax cheatsheet and examples
│   ├── tool-usage.md                   ← Guide to using the provided tools
│   ├── architecture.md                 ← System architecture and project layout
│   ├── visualization.md                ← All diagram views explained
│   ├── as-is-to-be.md                  ← AS-IS / TO-BE modeling workflow
│   ├── complete-example.md             ← Full worked example (Acme Consulting)
│   └── best-practices.md               ← Modeling guidelines and patterns
│
├── agent-guidelines/
│   ├── entity-mapping.md               ← How to map data to CSL entities
│   ├── syntax-structure.md             ← Syntax rules and structure overview
│   ├── validation-error-handling.md    ← Validation rules and error handling
│   ├── transformation-pipeline.md      ← From raw data to CSL to outputs
│   ├── output-formats.md               ← Supported output formats
│   ├── best-practices-templates.md     ← Modeling best practices
│   └── agent-specific-recommendations.md ← AI/RPA/bot-specific guidance
│
├── templates/
│   ├── company.csl
│   ├── offering.csl
│   ├── team.csl
│   ├── package.csl
│   ├── process.csl
│   └── value_chain.csl
│
├── examples/
│   ├── minimal_model.csl               ← Smallest valid CSL model
│   ├── advanced_model.csl              ← Full-featured model
│   ├── as_is_model.csl                 ← Current state example
│   └── to_be_model.csl                 ← Future state example
│
└── tools/
    ├── validate_csl.py                 ← Validate a .csl file
    ├── transform_csl.py                ← Transform CSL to graph model JSON
    ├── generate_diagram.py             ← Generate Mermaid diagrams from model
    └── parse_input.py                  ← Convert CSV/JSON input to CSL
```

---

## Quick Start

### 1. Write a minimal CSL model

```csl
company MyCompany {
  name: "My Company"
  offerings: [WebsiteRedesign]
}

segment SmallBusinesses {
  description: "Local businesses with 5-20 employees"
}

outcome FasterLead {
  type: "revenue_increase"
  baseline: { metric: "ConversionRate", value: 0.02 }
  target: { metric: "ConversionRate", value: 0.06, timeframe: "3 months" }
}

offering WebsiteRedesign {
  targets: [SmallBusinesses]
  delivers: [FasterLead]
  requires: [WebDesign]
}

capability WebDesign {
  ownedBy: DesignTeam
}

team DesignTeam {
  roles: [Designer]
}

package Starter {
  offering: WebsiteRedesign
  tier: "entry"
  pricing: { model: "fixed_project", basePrice: 2500 }
}
```

### 2. Validate it

```bash
python tools/validate_csl.py examples/minimal_model.csl
```

### 3. Transform to graph model

```bash
python tools/transform_csl.py examples/minimal_model.csl -o output/graph.json
```

### 4. Generate a diagram

```bash
python tools/generate_diagram.py output/graph.json --view architecture -o output/diagram.md
```

---

## CSL Entity Types

| Entity | Purpose |
|---|---|
| `company` | Top-level company (exactly one per model) |
| `offering` | Service or product delivered to clients |
| `segment` | Customer group |
| `market` | Geographic or industry market |
| `outcome` | Business transformation an offering delivers |
| `capability` | Organizational skill/ability |
| `process` | Repeatable operational workflow |
| `step` | Atomic task inside a process |
| `team` | Group of people who own work |
| `role` | Responsibility within a team |
| `package` | How an offering is bundled and priced |
| `pricingModel` | Pricing structure for a package |
| `journey` | Client journey through evaluation and buying |
| `system` | Technology tool or platform |
| `objective` | Strategic company goal |
| `metric` | Measurement of performance |

---

## Documentation

| Doc | What it covers |
|---|---|
| [docs/csl_specification.md](docs/csl_specification.md) | Full language specification — all entity types, relationships, syntax rules |
| [docs/csl_quick_reference.md](docs/csl_quick_reference.md) | Syntax cheatsheet — quick lookup while writing models |
| [docs/architecture.md](docs/architecture.md) | System architecture, processing pipeline, recommended project layout |
| [docs/visualization.md](docs/visualization.md) | All diagram views, when to use each, audience guide |
| [docs/as-is-to-be.md](docs/as-is-to-be.md) | AS-IS / TO-BE modeling, change tracking, delta computation |
| [docs/complete-example.md](docs/complete-example.md) | Full worked example of a real company model end-to-end |
| [docs/best-practices.md](docs/best-practices.md) | Modeling guidelines, naming conventions, common mistakes |
| [docs/tool-usage.md](docs/tool-usage.md) | Full CLI reference for all tools |

---

## For Agents & Software

If you are an AI agent or software system consuming this repository, start with:

1. [agent-guidelines/entity-mapping.md](agent-guidelines/entity-mapping.md) — understand how data maps to CSL
2. [agent-guidelines/syntax-structure.md](agent-guidelines/syntax-structure.md) — learn the syntax rules
3. [agent-guidelines/transformation-pipeline.md](agent-guidelines/transformation-pipeline.md) — understand the processing pipeline
4. [agent-guidelines/agent-specific-recommendations.md](agent-guidelines/agent-specific-recommendations.md) — agent-specific guidance

---

## License

Open source under MIT License. 