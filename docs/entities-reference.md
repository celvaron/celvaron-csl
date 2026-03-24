# CSL Entities Reference

Complete field reference for all 16 CSL entity types.

**Legend:** R = Required (error if missing) | W = Recommended (warning if missing) | O = Optional

---

## Table of Contents

1. [File-Level Metadata](#file-level-metadata)
2. [Shared Fields (all entities)](#shared-fields)
3. [Entity Index](#entity-index)
4. [capability](#capability)
5. [caseStudy](#casestudy)
6. [company](#company)
7. [journey](#journey)
8. [market](#market)
9. [metric](#metric)
10. [objective](#objective)
11. [offering](#offering)
12. [package](#package)
13. [pricingModel](#pricingmodel)
14. [process](#process)
15. [role](#role)
16. [segment](#segment)
17. [step](#step)
18. [system](#system)
19. [team](#team)
20. [Relationship Quick-Reference](#relationship-quick-reference)

---

## File-Level Metadata

Declared at the top of any CSL file, outside any entity block.

```csl
version: "1.0"
state: "current"             // current | as-is | to-be
author: "Author Name"
description: "Short description of what this file models"
```

| Field | Type | Notes |
|---|---|---|
| `version` | string | Semantic version of this model file |
| `state` | `current` \| `as-is` \| `to-be` | Omit for current-state models |
| `author` | string | Creator or last editor |
| `description` | string | One-line summary of what is modelled |

---

## Schema Block (Optional)

The `schema` block may follow file-level metadata and must appear before the first entity block. It is entirely optional; omitting it has no effect on parsing.

```csl
schema {
  sections: {
    Company:      [company]
    Teams:        [team, role]
    Strategy:     [objective, metric]
    Markets:      [market, segment]
    Offerings:    [offering, package, pricingModel]
    Processes:    [process, step]
    Capabilities: [capability]
    Systems:      [system]
    Outcomes:     [outcome, caseStudy]
    Journeys:     [journey]
  }

  relations: {
    process.steps:        { kind: composition, inverse: step.partOf }
    offering.packages:    { kind: composition, inverse: package.offering }
    team.roles:           { kind: composition, inverse: role.memberOf }
    capability.ownedBy:   { kind: association, target: team }
    offering.requires:    { kind: association, target: capability }
    capability.dependsOn: { kind: dependency }
    step.dependsOn:       { kind: dependency }
  }
}
```

### `sections` fields

| Field | Type | Level | Notes |
|---|---|---|---|
| section key (e.g. `Teams`) | PascalCase identifier | O | Stable display-section identifier |
| section value | list of entity type keywords | O | All types assigned to this section |

### `relations` fields

| Field | Type | Level | Notes |
|---|---|---|---|
| entry key | `entityType.fieldName` | R | The field being classified |
| `kind` | `composition` \| `association` \| `dependency` \| `extension` | R | Semantic classification |
| `inverse` | `entityType.fieldName` | O | Reverse-direction field on counterpart entity |
| `target` | entity type keyword | O | Expected target entity type (annotation only) |

**Relation kind summary:**

| Kind | Platform rendering | Typical use |
|---|---|---|
| `composition` | Child nested under parent in hierarchy views | `process.steps`, `team.roles`, `offering.packages` |
| `association` | Linked badge / cross-reference chip | `capability.ownedBy`, `offering.targets`, `offering.requires` |
| `dependency` | Directed prerequisite arrow | `capability.dependsOn`, `step.dependsOn` |
| `extension` | Dashed specialisation link | Offering variants, process templates |

See the [CSL Language Specification §3](csl_specification.md#3-schema-block) for full syntax rules, validation severities, and inverse declaration semantics.

---

## Shared Fields

Available on every entity. All optional unless noted.

| Field | Type | Level | Notes |
|---|---|---|---|
| `meta.confidence` | `high` \| `medium` \| `low` | W | How reliable is this data |
| `meta.source` | `client_interview` \| `document_analysis` \| `workshop` \| `assumption` | W | Where the data came from |
| `meta.lastReviewed` | ISO date | O | |
| `meta.reviewer` | string | O | |
| `meta.tags` | [string list] | O | Free-form tagging |
| `meta.notes` | string | O | Internal notes |
| `status` | `draft` \| `validated` \| `active` \| `deprecated` | O | Lifecycle state |
| `doc` | string (path) | O | Link to source document |
| `changeType` | `new` \| `enhanced` \| `retired` | O | AS-IS/TO-BE models only |

---

## Entity Index

| Entity | Purpose |
|---|---|
| [capability](#capability) | A skill, process, or technical function the company can perform |
| [caseStudy](#casestudy) | A documented proof point showing outcome delivery for a client |
| [company](#company) | The organisation being modelled — root entity |
| [journey](#journey) | The staged lifecycle a customer segment moves through |
| [market](#market) | A defined addressable market with size and geography |
| [metric](#metric) | A quantitative measure used to track outcomes or objectives |
| [objective](#objective) | A strategic goal with a measurable target and timeframe |
| [offering](#offering) | A product or service the company sells to a segment |
| [package](#package) | A priced, scoped bundle of one offering with specific inclusions |
| [pricingModel](#pricingmodel) | A named pricing structure referenced by packages |
| [process](#process) | A repeatable sequence of steps performed to deliver value |
| [role](#role) | A named function or job type within a team |
| [segment](#segment) | A defined group of target customers within a market |
| [step](#step) | A single action within a process |
| [system](#system) | A software system or tool used within the business |
| [team](#team) | A group of people responsible for a function or capability |

---

## capability

**Purpose:** Represents a skill, function, or technical capability the company possesses. Capabilities are owned by teams and required by offerings.

**Canonical relationship direction:** `capability.ownedBy: TeamName` (not `team.owns`). Offerings reference capabilities via `offering.requires`.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `ownedBy` | team ref | R | The team responsible for this capability |
| `maturity.current` | `basic` \| `intermediate` \| `advanced` \| `expert` | R | Current maturity level |
| `maturity.target` | `basic` \| `intermediate` \| `advanced` \| `expert` | W | Aspirational maturity level |
| `criticality` | `low` \| `medium` \| `high` \| `critical` | W | Business impact if capability fails |
| `differentiator` | boolean | O | Is this a source of competitive advantage |
| `dependsOn` | [capability refs] | O | Other capabilities this one requires |
| `resources.toolsUsed` | [system refs] | O | Systems used to exercise this capability |
| `resources.headcount` | number | O | FTEs currently involved |
| `resources.externalDependencies` | [string list] | O | Third-party inputs/vendors |

### Minimal Example

```csl
capability InvoicingAndBilling {
  description: "Draft-to-paid invoice lifecycle including partial billing and retainer management"
  ownedBy: ProductEngineering
  maturity: {
    current: "advanced"
  }
  dependsOn: TimeAndExpenseCapture
}
```

### Common Mistakes

- `supports: [OfferingName]` — **deprecated**. Declare the relationship from the offering via `offering.requires`.
- Omitting `maturity.current` — required field.
- Setting `ownedBy` to a role instead of a team. Use `team` entities only.

---

## caseStudy

**Purpose:** A documented proof point demonstrating how the company delivered a named outcome for a real or composite client.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `client` | string | R | Client name or anonymised placeholder |
| `industry` | string | R | Industry the client operates in |
| `challenge` | string | R | The problem before engagement |
| `solution` | string | R | What was delivered |
| `outcome` | string | R | Measurable result achieved |
| `technologies` | [string list] | O | CSL entity names or product names used |

### Minimal Example

```csl
caseStudy NorthernLogisticsTransformation {
  client: "Northern Logistics Co."
  industry: "Supply Chain & Logistics"
  challenge: "Manual route planning taking 4 hours per day per planner"
  solution: "Deployed route optimisation module integrated with their existing TMS"
  outcome: "Planning time reduced from 4 hours to 20 minutes; fuel costs down 12%"
}
```

### Common Mistakes

- Leaving `outcome` vague — include at least one quantified result.

---

## company

**Purpose:** The root entity representing the organisation being modelled. Every CSL file should contain exactly one `company` block.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | One-sentence company description |
| `industry` | string | R | Industry category (e.g. "HR Technology") |
| `size` | `startup` \| `small-business` \| `scale-up` \| `mid-market` \| `enterprise` | R | Company size tier |
| `stage` | `idea` \| `pre-revenue` \| `growth` \| `established` \| `mature` | R | Business lifecycle stage |
| `headquarters` | string | W | City, Country format |
| `founded` | number | W | Year founded |
| `markets` | [market refs] | W | Markets the company operates in |
| `offerings` | [offering refs] | W | Products and services |
| `objectives` | [objective refs] | W | Strategic objectives |
| `caseStudies` | [caseStudy refs] | O | Proof points |
| `voice.tone` | string | W | How the company communicates |
| `voice.formality` | `formal` \| `semi-formal` \| `conversational` | W | |
| `voice.perspective` | `we` \| `third-person` | W | |
| `voice.language` | `pl` \| `en` \| `both` | W | Primary language |
| `voice.dos` | [string list] | W | Communication guidelines — what to do |
| `voice.donts` | [string list] | W | Communication guidelines — what to avoid |
| `voice.examplePhrases` | [string list] | W | Sample copy illustrating voice |

### Minimal Example

```csl
company Nexara {
  industry: "Professional Services Software"
  size: "scale-up"
  stage: "growth"
  description: "B2B SaaS platform for project-based professional services firms"
}
```

### Common Mistakes

- Omitting `industry`, `size`, or `stage` — all required.
- Using free-form strings for `size` or `stage`; must match the enum values above.

---

## journey

**Purpose:** Models the staged lifecycle a customer segment moves through — from awareness to advocacy. Used to align touchpoints, goals, and conversion barriers at each stage.

**Note:** Use `stages` (not `phases`) and `targets` (not `for`).

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `targets` | [segment refs] | W | Segment(s) this journey applies to |
| `offering` | offering ref | O | Primary offering the journey leads toward |
| `stages` | list of stage objects | R | Use `stages`, not `phases` |
| `stages[].name` | string | R | Stage name (e.g. "Awareness") |
| `stages[].touchpoints` | [string list] | W | Channels and interactions at this stage |
| `stages[].goal` | string | W | What must happen for the prospect to advance |
| `stages[].duration` | number (days) | O | Typical time in this stage |
| `stages[].clientState` | string | O | What the prospect experiences |
| `stages[].conversionBarriers` | [{ barrier, mitigation }] | O | Known friction points |
| `stages[].exitCriteria` | string | O | Condition for moving to next stage |
| `stages[].successCriteria` | [string list] | O | |
| `metrics.awarenessToEval` | number (0–1) | O | Conversion rate from awareness to evaluation |
| `metrics.evalToClose` | number (0–1) | O | Conversion rate from evaluation to close |
| `metrics.overallConversion` | number (0–1) | O | |
| `metrics.avgTimeToClose` | number (days) | O | |

### Minimal Example

```csl
journey MidMarketBuyerJourney {
  description: "Lifecycle from first awareness to signed contract for a mid-market consulting firm"
  targets: MidMarketConsultingFirms
  stages: [
    {
      name: "Awareness"
      touchpoints: ["Content marketing", "LinkedIn ads"]
      goal: "Prospect learns about the company and primary use case"
    },
    {
      name: "Evaluation"
      touchpoints: ["Free trial", "Demo call"]
      goal: "Prospect validates fit through a 14-day trial"
    },
    {
      name: "Purchase"
      touchpoints: ["Proposal", "Contract signature"]
      goal: "Deal closed; plan selected"
    }
  ]
}
```

### Common Mistakes

- Using `phases` instead of `stages` — invalid keyword.
- Using `for` instead of `targets` — invalid keyword.

---

## market

**Purpose:** Defines an addressable market with geography and size. Segments reference markets via `segment.operatesIn`.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `region` | string | R | Geographic coverage |
| `size` | number (TAM) OR `{ estimatedCompanies, addressableMarket }` | R | Plain number = TAM in currency units |
| `type` | `geographic` \| `industry` \| `niche` | W | |
| `countries` | [string list] | O | ISO country codes: "DE", "UK", "US" |
| `characteristics.maturity` | string | W | `growing` \| `mature` \| `declining` |
| `characteristics.competition` | string | O | `fragmented` \| `consolidated` |
| `characteristics.regulation` | string | O | `low` \| `moderate` \| `high` |

### Minimal Example

```csl
market HRTechMarket {
  region: "Europe, North America"
  size: 32000000000
  description: "Software for HR teams managing distributed workforces"
}
```

### Common Mistakes

- Using string for `size` — must be a number (TAM in base currency units, e.g. USD/EUR).

---

## metric

**Purpose:** A quantitative measure used to track progress toward outcomes or objectives.

**Canonical form:** Flat fields (`target`, `baseline`, `frequency`) are preferred. The nested form (`targets { }`, `measurement { }`) is also valid but not recommended for new models.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `unit` | string | R | `%`, `days`, `count`, `EUR`, `hours/week`, etc. |
| `target` | number | R | The goal value |
| `baseline` | number | R | The current or starting value |
| `frequency` | string | R | `daily` \| `weekly` \| `monthly` \| `quarterly` \| `per-hire` \| etc. |
| `type` | `financial` \| `operational` \| `customer` \| `quality` \| `growth` \| `retention` \| `activation` \| `reliability` | W | |
| `calculation` | string | O | Formula or description of how the metric is calculated |

### Minimal Example

```csl
metric TimeToHireNewCountry {
  description: "Calendar days to complete all onboarding steps for an employee in a new country"
  unit: "days"
  target: 3
  baseline: 14
  frequency: "per-hire"
}
```

### Common Mistakes

- Omitting `baseline` — required even when starting from zero (use `baseline: 0`).
- Omitting `frequency` — required.
- Using nested `targets {}` form when the flat form suffices.

---

## objective

**Purpose:** A strategic goal connecting measurable metrics to the offerings that contribute to achieving it. Objectives belong to the `company`.

**Canonical relationship direction:** `objective.achievedThrough: [OfferingRefs]` (not `offering.contributesTo` or `objective.contributedBy`).

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `timeframe` | string | R | e.g. `"FY2025"`, `"Q1–Q4 2025"` |
| `measuredBy` | [metric refs] | R | One or more metrics |
| `achievedThrough` | [offering refs] | R | Offerings that contribute to this objective |
| `type` | `financial` \| `operational` \| `strategic` \| `customer` | W | |
| `target.value` | number | O | Quantified goal value |
| `target.deadline` | ISO date string | W | e.g. `"2025-12-31"` |
| `target.currency` | string | O | Required if target.value is monetary |

### Minimal Example

```csl
objective GrowAnnualRecurringRevenue {
  description: "Reach $30M ARR by end of fiscal year"
  timeframe: "FY2025"
  measuredBy: [NetRevenueRetention, BillableUtilisationRate]
  achievedThrough: [ProjectIntelligencePlatform, ClientPortal]
}
```

### Common Mistakes

- Using `contributedBy` or `contributesTo` — **deprecated**. Use `achievedThrough` on the objective.
- Omitting `timeframe` — required.
- `achievedThrough` points to capabilities or processes — must point to offerings.

---

## offering

**Purpose:** A product or service the company sells. Offerings target segments, require capabilities, and deliver outcomes.

**Canonical relationship directions:**
- `offering.requires: [capability]` (not `capability.supports`)
- `offering.delivers: [outcome]` (not `outcome.achievedThrough`)
- `objective.achievedThrough: [offering]` (not `offering.contributesTo`)

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `targets` | [segment refs] | R | One or more segments |
| `requires` | [capability refs] | R | Capabilities needed to deliver this offering |
| `delivers` | [outcome refs] | R | Outcomes this offering achieves |
| `operatesIn` | [market refs] | O | Markets this offering is sold into |
| `measuredBy` | [metric refs] | W | Metrics that track offering performance |
| `economics.avgDealSize` | number | R | Average ACV or deal value |
| `economics.targetMargin` | number (0–1) | R | Target gross margin as a decimal |
| `economics.avgDeliveryHours` | number | W | For services: average hours to deliver |
| `economics.clientLifetimeValue` | number | W | Average LTV |
| `performance.conversionRate` | number (0–1) | W | Close rate from qualified opportunity |
| `performance.avgSalesCycle` | number (days) | W | |
| `performance.clientRetention` | number (0–1) | W | Annual renewal rate |
| `performance.referralRate` | number (0–1) | O | |
| `performance.avgDeliveryWeeks` | number | W | For products: time to value |
| `performance.reworkRate` | number (0–1) | O | Rate of rework or revisions required |
| `targets with { priority, fitScore }` | `priority: primary\|secondary`, `fitScore: 0–1` | W | Attributes on each target reference |
| `requires with { proficiency, criticality }` | `proficiency: basic\|intermediate\|advanced\|expert`, `criticality: low\|medium\|high` | W | Attributes on each capability reference |

### Minimal Example

```csl
offering ProjectIntelligencePlatform {
  description: "Core project management, time-tracking, and profitability analytics platform"
  targets: MidMarketConsultingFirms
  requires: [TimeAndExpenseCapture, ProjectProfitabilityEngine]
  delivers: ImproveProjectProfitability
  economics: {
    avgDealSize: 15000
    targetMargin: 0.72
  }
}
```

### Common Mistakes

- Omitting `economics` block — `avgDealSize` and `targetMargin` are required.
- `type: "saas"` — **not a valid field**. Offering has no `type` field; describe the delivery model in `description`.
- `contributesTo: [ObjectiveName]` — **deprecated**. Use `objective.achievedThrough` instead.
- `packages: [PackageName]` — **deprecated**. Use `package.offering` instead.

---

## package

**Purpose:** A priced, scoped bundle of a single offering. Packages define what is included, at what price, and under what terms.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | One-line summary of what this package offers |
| `offering` | offering ref | R | The single offering this package bundles |
| `tier` | `entry` \| `standard` \| `premium` \| `advanced` \| `enterprise` | R | |
| `position` | number | R | Ordering (1 = lowest tier) |
| `includes` | [string list] | R | Feature or service inclusions |
| `excludes` | [string list] | O | Explicitly excluded items |
| `pricing.model` | `fixed_project` \| `monthly_retainer` \| `value_based` \| `tiered_subscription` \| `usage_based` \| `hybrid` \| `custom` | R | |
| `pricing.basePrice` | number | R | Base price; use 1 as placeholder for custom |
| `pricing.currency` | string | R | `EUR`, `USD`, `GBP`, etc. |
| `pricing.paymentTerms` | string | W | e.g. `"monthly"`, `"annual"` |
| `delivery.duration` | number (days) | W | Delivery timeline |
| `delivery.format` | `remote` \| `onsite` \| `hybrid` | W | |
| `delivery.meetings` | number | O | Expected meeting count |
| `delivery.async_work` | boolean | O | |
| `boundaries.maxRevisions` | number | O | |
| `boundaries.responseTime` | string | W | SLA response time |
| `boundaries.scope` | string | W | Scope description |
| `targets` | [segment refs] | O | If targeting a sub-set of the offering's segments |

### Minimal Example

```csl
package GrowthPlan {
  tier: "standard"
  position: 2
  offering: GlobalOnboardingModule
  description: "Per employee/month — includes full onboarding and HR portal"
  pricing: {
    model: "tiered_subscription"
    basePrice: 15
    currency: "USD"
    paymentTerms: "monthly, per employee"
  }
  includes: [
    "Onboarding workflows for 60+ countries",
    "AI contract generation",
    "Employee self-service"
  ]
}
```

### Common Mistakes

- Omitting `description`.
- Setting `basePrice: 0` for enterprise packages — use `1` as a placeholder with a comment.
- Using invalid `pricing.model` values (e.g. `"per-seat"`, `"usage-based"`) — use enum values from the table above.

---

## pricingModel

**Purpose:** A named, reusable pricing structure. Packages reference a `pricingModel` via `pricing.model`; `pricingModel` entities document the structure in detail.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `type` | `fixed_project` \| `monthly_retainer` \| `value_based` \| `tiered_subscription` \| `usage_based` \| `hybrid` | R | |
| `description` | string | R | |
| `calculation.basis` | string | O | What the price is calculated on |
| `calculation.methodology` | string | O | How the price is derived |
| `calculation.valueCapture` | number (0–1) | O | Fraction of value captured as price |
| `structure.basePrice` | number | O | |
| `structure.addOns` | [{ name, price }] | O | |
| `terms.payment` | string | O | |
| `terms.refundPolicy` | string | O | |
| `terms.priceAdjustment` | string | O | |

### Minimal Example

```csl
pricingModel PerSeatSubscription {
  type: "tiered_subscription"
  description: "Monthly or annual subscription priced per active user seat — annual gives 20% discount"
}
```

### Common Mistakes

- `type: "per-seat"` — not valid. Use `"tiered_subscription"`.
- `type: "usage-based"` — not valid. Use `"usage_based"` (underscore).

---

## process

**Purpose:** A repeatable sequence of steps that delivers value to a customer or the business. Processes are performed by teams or roles and measured by metrics.

**Note:** `process.supports` is deprecated. Processes are linked to offerings via capability chains (`offering.requires → capability`).

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `performedBy` | team or role ref | R | Primary team or role responsible |
| `measuredBy` | metric ref | R | The metric that tracks this process's performance |
| `uses` | [system refs] | O | Systems involved in this process |
| `metrics.avgDuration` | number (days) | W | Typical end-to-end duration |
| `metrics.successRate` | number (0–1) | O | |
| `metrics.clientSatisfaction` | number | O | |
| `automation.level` | `none` \| `partial` \| `full` | O | |
| `automation.automated` | [string list] | O | Step names that are automated |
| `automation.manual` | [string list] | O | Step names that are manual |

### Minimal Example

```csl
process CustomerOnboarding {
  description: "End-to-end process from contract signature to first live project"
  performedBy: CustomerSuccessManager
  measuredBy: TimeToOnboard
}
```

### Common Mistakes

- Omitting `measuredBy` — required.
- `supports: [OfferingName]` — **deprecated**. Remove.
- Steps must be declared as separate `step` entities, not inline.

---

## role

**Purpose:** A named job function within a team. Roles are referenced by processes and steps as the `performedBy` target.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `responsibilities` | [string list] | R | Key accountabilities |
| `capabilities` | [capability refs] | O | Capabilities this role must have |
| `capabilities with { level }` | `basic` \| `intermediate` \| `advanced` \| `expert` | O | Proficiency attribute |
| `compensation.type` | `salary_only` \| `salary_bonus` \| `hourly` \| `salary_equity` | O | |
| `compensation.range` | [min, max] | O | Annual compensation range |

### Minimal Example

```csl
role CustomerSuccessManager {
  description: "Owns post-sale relationship, onboarding, and renewal"
  responsibilities: [
    "Run onboarding processes for new customers",
    "Conduct quarterly business reviews",
    "Manage renewal and expansion pipeline"
  ]
}
```

### Common Mistakes

- Omitting `responsibilities` — required.

---

## segment

**Purpose:** A defined group of target customers within a market. Segments are referenced by offerings (`offering.targets`) and journeys (`journey.targets`).

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `size` | number | R | Total count of companies or people in this segment |
| `operatesIn` | market ref | R | The market this segment is part of |
| `characteristics.companySize` | string | W | e.g. `"50–500 employees"` |
| `characteristics.revenue` | string | W | e.g. `"$5M–$50M"` |
| `characteristics.geographies` | [string list] | W | |
| `characteristics.industry` | string | W | — if narrower than the market |
| `problems` | [string list] | W | Key pain points |
| `motivations` | [string list] | W | Drivers for buying |
| `buyingBehavior.decisionCycle` | string | W | Typical buying timeline |
| `buyingBehavior.primaryTrigger` | string | W | What causes the buyer to act |
| `buyingBehavior.keyDecisionMaker` | string | W | Job title or function |
| `buyingBehavior.preferredEngagementModel` | string | W | e.g. `"Self-serve"`, `"Annual contract"` |
| `buyingBehavior.priceSensitivity` | `low` \| `medium` \| `high` | W | |
| `buyingBehavior.referralDriven` | boolean | O | |

### Minimal Example

```csl
segment MidMarketConsultingFirms {
  description: "Consulting firms with 50–500 employees running complex multi-project engagements"
  size: 45000
  operatesIn: ProfessionalServicesMarket
}
```

### Common Mistakes

- Omitting `size` or `operatesIn` — both required.
- Using string for `size` — must be a number.
- Setting `operatesIn` to a company or offering — must reference a `market` entity.

---

## step

**Purpose:** A single action within a process. Steps must declare their order and the process they belong to.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `partOf` | process ref | R | The process this step belongs to |
| `performedBy` | team or role ref | R | |
| `order` | number | R | 1-based sequential position |
| `dependsOn` | [step refs] | W | Required for non-first steps |
| `duration` | number (minutes) | W | |
| `estimatedEffort` | number (hours) | W | |
| `inputs` | [string list] | O | |
| `outputs` | [string list] | O | |
| `deliverables` | [string list] | W | Tangible outputs produced |
| `successCriteria` | [string list] | W | What "done" looks like |
| `uses` | [system refs] | O | Systems used in this step |
| `delegatable` | boolean | O | |
| `automationPotential` | `low` \| `medium` \| `high` | O | |

### Minimal Example

```csl
step KickoffCall {
  description: "30-minute onboarding call to align scope, integrations, and launch date"
  order: 2
  partOf: CustomerOnboarding
  performedBy: CustomerSuccessManager
  dependsOn: ContractHandoff
}
```

### Common Mistakes

- Omitting `order` — required.
- Omitting `partOf` — required.
- Non-first steps omitting `dependsOn` — strongly recommended.

---

## system

**Purpose:** A software system, tool, or infrastructure component used by the business. Systems are referenced by processes and steps via `uses`.

**Note:** `system.supports`, `system.usedBy`, and `system.uses: [capability refs]` are deprecated. Systems should not reference other entities directly; processes and steps reference systems via `process.uses` / `step.uses`.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `type` | `saas` \| `internal` \| `infrastructure` \| `custom` \| `external` | R | `external` = third-party system not operated by the company |
| `vendor` | string | W | For `saas` and `external` types |
| `cost` | number (annual) | O | Annual cost in base currency |
| `integration.connectedTo` | [system refs] | O | Other systems this is integrated with |
| `integration.apiAvailable` | boolean | O | |

### Minimal Example

```csl
system StripePayments {
  description: "Third-party payment processing for subscription billing and invoice collection"
  type: "external"
  vendor: "Stripe"
  cost: 48000
}
```

### Common Mistakes

- `uses: [CapabilityRefs]` — **invalid**. Systems do not reference capabilities; remove this field.
- `supports: [ProcessName]` or `usedBy: [TeamName]` — **deprecated**. Remove both.
- Omitting `type` — required.

---

## team

**Purpose:** A group of people responsible for one or more capabilities or functions. Teams own capabilities via `capability.ownedBy`.

**Canonical relationship direction:** `capability.ownedBy: TeamName` (not `team.owns`). Teams should not reference capabilities directly.

### Fields

| Field | Type | Level | Notes |
|---|---|---|---|
| `description` | string | R | |
| `size` | number OR `{ current: number, target: number }` | R | Plain number OR nested with current/target |
| `roles` | [role refs] | W | Roles in this team |
| `capacity.billableHours` | number | W | Billable hours per person per month |
| `capacity.utilization` | number (0–1) | W | Current utilisation rate |
| `structure.leadRole` | role ref | O | |
| `structure.reportingTo` | string | O | |

### Minimal Example

```csl
team ProductEngineering {
  size: 28
  description: "Core platform development across web, mobile, and API"
}
```

### Size with target:

```csl
team HROperations {
  size: {
    current: 8
    target: 4
  }
  description: "HR ops team — planned reduction as automation covers routine tasks"
}
```

### Common Mistakes

- `owns: [CapabilityName]` — **deprecated**. Declare ownership from the capability via `ownedBy`.
- Omitting `description` — required.
- Using string for `size` — must be a number or `{ current, target }` object.

---

## Relationship Quick-Reference

This table shows every cross-entity relationship and which entity declares it.

| Relationship | Declared on | Field | Points to |
|---|---|---|---|
| Offering ← Capability | **offering** | `requires: [capability]` | capability |
| Offering → Outcome | **offering** | `delivers: [outcome]` | outcome |
| Offering → Segment | **offering** | `targets: [segment]` | segment |
| Capability ← Team | **capability** | `ownedBy: team` | team |
| Capability ← Capability | **capability** | `dependsOn: [capability]` | capability |
| Objective ← Offering | **objective** | `achievedThrough: [offering]` | offering |
| Objective → Metric | **objective** | `measuredBy: [metric]` | metric |
| Outcome → Metric | **outcome** | `measuredBy: [metric]` | metric |
| Package → Offering | **package** | `offering: offering` | offering |
| Process → System | **process** | `uses: [system]` | system |
| Process → Metric | **process** | `measuredBy: metric` | metric |
| Process ← Step | **step** | `partOf: process` | process |
| Step → System | **step** | `uses: [system]` | system |
| Step ← Step | **step** | `dependsOn: [step]` | step |
| Segment → Market | **segment** | `operatesIn: market` | market |
| Journey → Segment | **journey** | `targets: [segment]` | segment |
| Company → CaseStudy | **company** | `caseStudies: [caseStudy]` | caseStudy |
| Capability → System | **capability** | `resources.toolsUsed: [system]` | system |

### Deprecated Fields (do not use)

| Field | Status | Canonical replacement |
|---|---|---|
| `capability.supports: [offering]` | Deprecated (W013) | `offering.requires: [capability]` |
| `team.owns: [capability]` | Deprecated (W014) | `capability.ownedBy: team` |
| `outcome.achievedThrough: [offering]` | Deprecated (W015) | `offering.delivers: [outcome]` |
| `offering.contributesTo: [objective]` | Deprecated (W016) | `objective.achievedThrough: [offering]` |
| `process.supports: [offering]` | Deprecated (W017) | Not needed — inferred through capability chain |
| `system.supports: [process]` | Deprecated (W018) | `process.uses: [system]` |
| `system.usedBy: [team]` | Deprecated (W018) | Not needed |
| `objective.contributedBy: [offering]` | Deprecated (W019) | `objective.achievedThrough: [offering]` |
| `offering.packages: [package]` | Deprecated (W020) | `package.offering: offering` |
| `system.uses: [capability]` | Invalid | Remove entirely |
| `offering.type: "saas"` | Invalid field | Remove entirely |
