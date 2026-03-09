# CSL Modeling Best Practices

Guidelines for writing clean, accurate, and useful CSL models.

---

## Model Design

### Start Small
Don't try to model everything upfront. Begin with the core:

1. One `company`, 1–2 `offering`s, 2–3 `segment`s
2. Add key `capability`s and `team`s
3. Add 1–2 core `process`es with their `step`s
4. Expand incrementally as you learn more

### Progressive Detail
- Start with high-level structure — get the shape right first
- Add detail where it has the highest analytical value
- Leave non-critical entities at minimal definition until needed

### Always Trace Value
Every offering should connect to outcomes and economic value. The chain should close:

```
Offering → delivers → Outcome → economicValue → { annualRevenue, timeSaving, … }
```

Model the *why*, not just the *what*.

### Model Reality
- Document the actual AS-IS state — not what you wish was true
- Be honest about capability maturity levels
- Use `confidence: low` to flag assumptions
- Validate with stakeholders before treating data as authoritative

---

## Naming Conventions

### Entity Names
- **Be specific:** `ClientOnboardingProcess`, not `Onboarding`
- **Use domain language:** terms the client would naturally use
- **Avoid abbreviations** unless they are standard in the domain
- **PascalCase** for all entity names: `FounderLedAgencies`, `ServiceDesign`

### Field Values
- Use consistent units: EUR, USD, hours, days — pick one and stick to it
- Be explicit about timeframes: `"6 months"`, `"Q4 2026"`, not `"soon"`
- Include context in `description` fields — these become knowledge base entries

### Documentation Links
- Link to external knowledge files using relative paths
- Maintain link integrity — broken links degrade agent reasoning quality

---

## Modeling Patterns

### Capability Chains
Model capability dependencies explicitly — this enables bottleneck analysis:

```csl
capability A {
  dependsOn: [B, C]
}
capability B {
  dependsOn: [D]
}
```

### Tiered Packages
Design clear commercial progression with explicit positions:

```csl
package Foundation { tier: "entry",    position: 1, pricing: { basePrice: 12900 } }
package Standard  { tier: "standard",  position: 2, pricing: { basePrice: 24900 } }
package Premium   { tier: "premium",   position: 3, pricing: { basePrice: 39900 } }
```

### Process Flows
Capture real workflows with explicit step dependencies:

```csl
process Onboarding {
  steps: [Step1, Step2, Step3]
}
step Step2 { dependsOn: [Step1] }
step Step3 { dependsOn: [Step2] }
```

---

## Validation Strategy

### Validate Progressively
Don't wait until the model is complete. Validate in layers:

1. **Syntax** — parse errors (run immediately after writing)
2. **References** — are all referenced entities defined?
3. **Structural** — cardinality, required fields, type correctness
4. **Semantic** — business logic (e.g. every offering has at least one outcome)
5. **Completeness** — coverage of key entities

```bash
python tools/validate_csl.py model.csl
```

### Mark Assumptions
Use confidence levels to communicate certainty:

```csl
capability ServiceDesign {
  meta: {
    confidence: low
    source: "assumed"
  }
}
```

Validate low-confidence entities with stakeholders before using the model for decisions.

### Use Version Control
- Commit frequently with meaningful messages
- Tag stable versions (`asis-v1`, `tobe-draft-2`)
- Use commit history to track how your understanding evolved

---

## Visualization Strategy

### Match View to Audience
Don't show everyone everything. Choose views that answer the audience's question:

| Audience | Best Views |
|---|---|
| Executives | `architecture`, `value-stream`, `strategy-map` |
| Operations | `process-flow`, `service-blueprint` |
| Product / Commercial | `package-architecture`, `journey-map` |
| HR / Org Design | `capability-map` |
| Transformation | `change-impact`, `operating-model` |

### Layer Information
- Start with a high-level overview
- Drill into detail only where the conversation needs it
- Don't put everything in one diagram — clarity beats completeness

### Keep Visuals in Sync with the Model
Generate diagrams from the model. Never manually edit generated diagrams. If the diagram needs to change, change the model and regenerate.

```bash
python tools/generate_diagram.py output/graph.json --view architecture --title "Company"
```

See [visualization.md](visualization.md) for the full view reference.

---

## Common Mistakes

| Mistake | Better Approach |
|---|---|
| Modeling aspirations as AS-IS | Keep AS-IS factual; put aspirations in TO-BE |
| Skipping `outcome` entirely | Every offering must trace to a concrete outcome |
| Generic names (`Process1`, `TeamA`) | Use real, domain-specific names |
| Modeling everything at once | Start minimal, add detail iteratively |
| Forgetting `economics` on offerings | Economic data enables value chain analysis |
| Not linking capabilities to teams | `ownedBy` is required for capability map views |
