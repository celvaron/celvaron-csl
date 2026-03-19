# CSL Quick Reference

**Version:** 1.0

---

## Syntax at a Glance

```
entityType EntityName {
  field: "string"
  field: 42
  field: true
  field: [RefA, RefB]
  field: { nestedKey: value }
}
```

---

## All Entity Types

| Keyword | Purpose |
|---|---|
| `company` | Top-level company (1 per model) |
| `offering` | Service or product delivered to clients |
| `segment` | Customer group |
| `market` | Geographic or industry market |
| `outcome` | Business transformation an offering delivers |
| `capability` | Organizational ability/skill |
| `process` | Repeatable operational workflow |
| `step` | Atomic task inside a process |
| `team` | Group that owns work |
| `role` | Responsibility within a team |
| `package` | How an offering is bundled and priced |
| `pricingModel` | Pricing structure |
| `journey` | Client journey phases |
| `system` | Technology platform or tool |
| `objective` | Strategic company goal |
| `metric` | Performance measurement |

---

## Minimal Working Model

The smallest valid CSL model:

```csl
company AcmeServices {
  name: "Acme Services"
}

segment SmallBusinesses {
  description: "Local businesses, 5-20 employees"
}

outcome IncreasedRevenue {
  type: "revenue_increase"
  baseline: { metric: "MRR", value: 10000 }
  target: { metric: "MRR", value: 20000, timeframe: "6 months" }
}

offering BusinessConsulting {
  targets: [SmallBusinesses]
  delivers: [IncreasedRevenue]
  requires: [StrategyCapability]
}

capability StrategyCapability {
  ownedBy: ConsultingTeam
}

team ConsultingTeam {
  roles: [Consultant]
}

package BasicPackage {
  offering: BusinessConsulting
  tier: "entry"
  pricing: {
    model: "monthly_retainer"
    basePrice: 2500
  }
}
```

---

## Key Relationships

| Relationship | Example |
|---|---|
| `targets` | offering → segment |
| `operatesIn` | offering → market |
| `delivers` | offering → outcome |
| `requires` | offering → capability |
| `ownedBy` | capability → team |
| `dependsOn` | capability → capability, step → step |
| `performedBy` | process/step → team/role |
| `uses` | process/step → system |
| `hasStep` | process → step |
| `partOf` | step → process |
| `measuredBy` | offering/objective/process → metric |
| `achievedThrough` | objective → offering |

---

## Relationship with Attributes

```csl
// Inline attributes on list relationships
targets: [SegmentA, SegmentB] with {
  SegmentA: { priority: primary, fitScore: 0.95 }
  SegmentB: { priority: secondary, fitScore: 0.75 }
}

// Per-item attributes
requires: [
  ServiceDesign with { proficiency: expert, criticality: high },
  ProcessMapping with { proficiency: intermediate, criticality: medium }
]
```

---

## Outcome Types

`revenue_increase` | `cost_reduction` | `time_saving` | `risk_mitigation` | `capacity_expansion` | `quality_improvement` | `customer_satisfaction`

---

## Package Tiers

`entry` | `standard` | `premium` | `enterprise`

---

## Pricing Models

`fixed_project` | `monthly_retainer` | `value_based` | `tiered_subscription` | `usage_based` | `hybrid`

---

## Maturity Levels

`basic` | `intermediate` | `advanced` | `expert`

---

## Change Types (AS-IS / TO-BE)

`new` | `removed` | `enhanced` | `reduced` | `unchanged`

---

## Common Patterns

### Tiered Package Structure

```csl
offering MyService {
  packages: [Starter, Professional, Enterprise]
}

package Starter {
  offering: MyService
  tier: "entry"
  position: 1
  pricing: { model: "monthly_retainer", basePrice: 1500 }
  boundaries: { maxUsers: 3, responseTime: "48 hours" }
}

package Professional {
  offering: MyService
  tier: "standard"
  position: 2
  pricing: { model: "monthly_retainer", basePrice: 3500 }
  boundaries: { maxUsers: 10, responseTime: "24 hours" }
}

package Enterprise {
  offering: MyService
  tier: "premium"
  position: 3
  pricing: { model: "custom", basePrice: 8500 }
  boundaries: { maxUsers: 999, responseTime: "4 hours" }
}
```

---

### Process with Step Dependencies

```csl
process OnboardingProcess {
  performedBy: OnboardingTeam
  steps: [StepA, StepB, StepC]
  metrics: { avgDuration: 14, successRate: 0.95 }
}

step StepA {
  partOf: OnboardingProcess
  performedBy: SalesRep
  duration: 30
  delegatable: true
}

step StepB {
  partOf: OnboardingProcess
  performedBy: OnboardingSpecialist
  duration: 120
  dependsOn: [StepA]
  delegatable: true
}

step StepC {
  partOf: OnboardingProcess
  performedBy: AccountManager
  duration: 60
  dependsOn: [StepB]
}
```

---

### Capability Chain

```csl
offering PremiumOffering {
  requires: [Advanced]
}

capability Advanced {
  ownedBy: ExpertTeam
  dependsOn: [Mid1, Mid2]
  maturity: { current: "advanced", target: "expert" }
  criticality: "high"
  differentiator: true
}

capability Mid1 {
  ownedBy: SpecialistTeam
  dependsOn: [Foundation1]
  maturity: { current: "intermediate", target: "advanced" }
}

capability Foundation1 {
  ownedBy: CoreTeam
  maturity: { current: "advanced", target: "advanced" }
}
```

---

### AS-IS → TO-BE Entity

```csl
// In tobe/model.csl
capability AutomatedReporting {
  description: "Automated reporting with dashboards"
  ownedBy: AnalyticsTeam
  maturity: { current: "basic", target: "advanced" }
  changeType: "new"
  changes: {
    from: { name: "ManualReporting", effort: 40 }
    to: { name: "AutomatedReporting", effort: 2 }
    rationale: "Free 38 hours/month for analysis"
    expectedImpact: "95% time reduction"
    riskLevel: "medium"
    riskMitigation: "Parallel run for 2 months"
  }
}
```

---

## Meta Attributes (Any Entity)

```csl
entity AnyEntity {
  // ... fields

  meta: {
    confidence: "high"        // high | medium | low
    source: "client_interview" // client_interview | document_analysis | workshop | assumption
    lastReviewed: "2024-03-15"
    reviewer: "principal_consultant"
    tags: ["core", "differentiator"]
    notes: "Any additional context"
  }
  status: "active"            // draft | validated | active | deprecated
  doc: "knowledge/offerings/my-offering.md"
}
```

---

## Validation Checklist

### Minimum Requirements
- [ ] 1 `company` entity
- [ ] ≥1 `offering`
- [ ] ≥1 `segment`
- [ ] ≥1 `outcome`
- [ ] ≥1 `capability`
- [ ] ≥1 `team`
- [ ] ≥1 `package`

### Quality Checks
- [ ] All offerings have packages
- [ ] All offerings deliver measurable outcomes
- [ ] All capabilities have owners (team)
- [ ] All processes have at least one step and metrics
- [ ] Economics data present on offerings
- [ ] Performance data present on offerings

### Relationship Checks
- [ ] All entity references resolve
- [ ] No orphaned entities (unconnected nodes)
- [ ] Capability chains complete
- [ ] Process step dependencies are acyclic
