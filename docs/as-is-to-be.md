# AS-IS / TO-BE Modeling

CSL supports two model states: the **AS-IS** (current reality) and the **TO-BE** (desired future state). Together they form the basis for structured transformation work.

---

## Model States

| State | Description |
|---|---|
| **AS-IS** | What the company looks like today — honest, validated, no aspirations |
| **TO-BE** | The designed future state — what you're building toward |

Both are full CSL models. The difference is not the language — it's the data inside.

---

## Recommended File Structure

```
project/
├── asis/
│   └── model.csl
├── tobe/
│   └── model.csl
└── comparison/
    └── delta.json
```

Keep the two models in sibling directories. The `comparison/` folder holds the computed delta between them.

---

## Tracking Changes on Entities

Every CSL entity accepts change metadata when used inside a TO-BE model:

```csl
capability ServiceDesign {
  ownedBy: StrategyTeam
  
  changeType: "enhanced"
  
  changes: {
    from: {
      owner: "FounderOnly"
      maturity: "intermediate"
    }
    to: {
      owner: "StrategyTeam"
      maturity: "advanced"
    }
    rationale: "Delegation required to scale delivery"
    expectedImpact: "Enable 3x capacity increase"
    riskLevel: "medium"
  }
}
```

### Change Types

| Value | Meaning |
|---|---|
| `new` | Entity doesn't exist in AS-IS |
| `removed` | Entity exists in AS-IS but not in TO-BE |
| `enhanced` | Entity improved or upgraded |
| `reduced` | Entity downgraded or simplified |
| `unchanged` | No change |

---

## Delta Computation

The delta between AS-IS and TO-BE is computed automatically and written to `comparison/delta.json`:

```json
{
  "addedNodes": [
    { "id": "offering:NewOffering", "type": "offering", "impact": "high" }
  ],
  "removedNodes": [
    { "id": "offering:LegacyOffering", "type": "offering", "reason": "discontinued" }
  ],
  "modifiedNodes": [
    {
      "id": "capability:ServiceDesign",
      "changes": {
        "ownedBy": { "from": "company:CEO", "to": "team:StrategyTeam" },
        "maturity": { "from": "intermediate", "to": "advanced" }
      }
    }
  ],
  "addedEdges": [],
  "removedEdges": [],
  "metrics": {
    "totalChanges": 47,
    "criticalChanges": 8,
    "riskScore": 0.65
  }
}
```

Use the `change-impact` view in `generate_diagram.py` to visualize this delta:

```bash
python tools/generate_diagram.py comparison/delta.json --view change-impact --title "Acme Transformation"
```

---

## Transformation Roadmap

Link changes to concrete implementation work using `initiative` entities:

```csl
initiative BuildStrategyTeam {
  description: "Hire and train strategy team"
  
  enables: [
    "capability:ServiceDesign with { changeType: enhanced }",
    "capability:ProcessMapping with { changeType: enhanced }"
  ]
  
  phases: [
    {
      name: "Hire"
      duration: 60
      milestones: ["Senior hire", "Junior hire"]
    },
    {
      name: "Train"
      duration: 90
      milestones: ["Framework training", "Client shadowing"]
    }
  ]
  
  dependencies: [
    DefineStrategyRoles,
    CreateTrainingMaterials
  ]
  
  riskMitigation: "Overlap with founder during transition"
}
```

Initiatives connect the strategic TO-BE design to an actionable delivery plan.

---

## Modeling Tips

- **Model AS-IS first.** Always start from reality before designing the future state.
- **Be honest.** Mark low-confidence data with `confidence: low`. Don't improve AS-IS to make it look better.
- **Annotate every change.** Use `rationale` and `expectedImpact` on change entities — this becomes the transformation narrative.
- **Use `riskLevel`.** Identifying high-risk changes early prevents surprises.
- **Version control both models.** Commit AS-IS and TO-BE separately so you can track the evolution of both.
