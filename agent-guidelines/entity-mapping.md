# Entity Mapping Guide

How to map real-world company data to CSL entities and relationships.

---

## Overview

When an agent or software system receives company data, it must identify which CSL entity type each piece of data corresponds to. This guide provides mapping tables and rules for every entity type.

---

## 1. Core Mapping Logic

The mapping process follows this order:

1. Identify the **company** — always the starting point
2. Identify **markets** and **segments** — who the company serves
3. Identify **offerings** — what the company delivers
4. Identify **outcomes** — what transformations offerings create
5. Identify **capabilities** — what the company must be able to do
6. Identify **teams** and **roles** — who does the work
7. Identify **processes** and **steps** — how work gets done
8. Identify **packages** — how offerings are bundled and priced
9. Identify **systems** — what tools support the work
10. Identify **objectives** and **metrics** — how success is measured

---

## 2. Entity Mapping Tables

### 2.1 Company

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Company / organization name | `name` | string | ✅ |
| Short description of what the company does | `description` | string | ✅ |
| Industry or sector (e.g. "Professional Services", "SaaS", "FinTech") | `industry` | string | ✅ |
| Company size tier | `size` | `startup`/`scale-up`/`mid-market`/`enterprise` | ✅ |
| Current growth phase | `stage` | `idea`/`pre-revenue`/`growth`/`established`/`mature` | ✅ |
| City, country of headquarters | `headquarters` | string | — |
| Year the business was started | `founded` | number | — |
| List of geographic or industry markets | `markets` | [market references] | — |
| List of services or products offered | `offerings` | [offering references] | — |
| Strategic goals | `objectives` | [objective references] | — |
| Past client engagements (social proof) | `caseStudies` | [caseStudy references] | — |

**Rule:** There is exactly one `company` entity per model.

#### 2.1.1 `voice` Block (nested in `company`)

Captures the company's tone of voice for use in proposal generation.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Overall writing style description | `voice.tone` | string | — |
| Register / formality level | `voice.formality` | `formal`/`semi-formal`/`conversational` | — |
| Grammatical person used in copy | `voice.perspective` | `we`/`third-person` | — |
| Primary language(s) | `voice.language` | `pl`/`en`/`both` | — |
| Writing behaviours to adopt | `voice.dos` | [string list] | — |
| Writing behaviours to avoid | `voice.donts` | [string list] | — |
| Illustrative phrases in desired tone | `voice.examplePhrases` | [string list] | — |

---

### 2.2 Offering

An offering is any service, product, or program the company sells or delivers.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Service / product name | entity name (PascalCase) | identifier | ✅ |
| Description of what it does | `description` | string | ✅ |
| Customer groups it serves | `targets` | [segment references] | ✅ |
| Geographic / industry markets | `operatesIn` | [market references] | — |
| Skills / abilities needed to deliver | `requires` | [capability references] | ✅ |
| Changes or results it creates for clients | `delivers` | [outcome references] | ✅ |
| KPIs used to measure success | `measuredBy` | [metric references] | — |
| Average contract / project value | `economics.avgDealSize` | number | ✅ |
| Average hours to deliver | `economics.avgDeliveryHours` | number | — |
| Gross margin percentage | `economics.targetMargin` | number (0–1) | ✅ |
| Revenue per client over their lifetime | `economics.clientLifetimeValue` | number | — |
| % of prospects who convert to clients | `performance.conversionRate` | number (0–1) | — |
| Average days from first contact to signed deal | `performance.avgSalesCycle` | number | — |
| % of clients who renew | `performance.clientRetention` | number (0–1) | — |

**Naming rule:** Convert to PascalCase. "Service Productization" → `ServiceProductization`

---

### 2.3 Segment

A segment is a distinct group of potential customers.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Segment / customer group name | entity name | identifier | ✅ |
| Description of the group | `description` | string | ✅ |
| Number of companies or people in this segment | `size` | number | ✅ |
| Market this segment operates within | `operatesIn` | market reference | ✅ |
| Industry / sector | `characteristics.industry` | string | — |
| Annual revenue range | `characteristics.revenueRange` | [min, max] | — |
| Team size range | `characteristics.teamSize` | [min, max] | — |
| Years in business range | `characteristics.businessAge` | [min, max] | — |
| Location / geography | `characteristics.geography` | [string list] | — |
| Pain points, problems they face | `problems` | [string list] | — |
| Desired outcomes / motivations | `motivations` | [string list] | — |
| Who makes the buying decision | `buyingBehavior.decisionMaker` | string | — |
| Average days to decide | `buyingBehavior.avgDecisionTime` | number | — |
| Price sensitivity | `buyingBehavior.priceSensitivity` | `low`/`medium`/`high` | — |
| Driven by referrals? | `buyingBehavior.referralDriven` | boolean | — |

---

### 2.4 Market

A market is a geographic region or industry the company operates in.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Market name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Geographic or industry market | `type` | `geographic`/`industry`/`niche` | — |
| Region name | `region` | string | — |
| Country codes | `countries` | [string list] | — |
| Estimated number of target companies | `size.estimatedCompanies` | number | — |
| Total addressable market (currency) | `size.addressableMarket` | number | — |
| Market growth stage | `characteristics.maturity` | string | — |
| Level of competition | `characteristics.competition` | string | — |

---

### 2.5 Outcome

An outcome is the transformation or value delivered to a client.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Outcome name | entity name | identifier | ✅ |
| Description of the transformation | `description` | string | — |
| Type of improvement | `type` | outcome type enum | — |
| Current state of the metric | `baseline.metric`, `baseline.value` | string, number | — |
| Target state of the metric | `target.metric`, `target.value`, `target.timeframe` | string, number, string | — |
| Metrics that track this outcome | `measuredBy` | [metric references] | ✅ |
| Annual revenue impact | `economicValue.annualRevenue` | number | — |
| Annual cost reduction | `economicValue.costReduction` | number | — |
| Hours saved per year | `economicValue.timeSaving` | number | — |
| Risk value protected | `economicValue.riskMitigation` | number | — |
| Capacity multiplier | `economicValue.capacityExpansion` | number | — |
| Client situation before engagement | `clientState.before` | string | — |
| Client situation after engagement | `clientState.after` | string | — |

**Outcome type values:**  
`revenue_increase` | `cost_reduction` | `time_saving` | `risk_mitigation` | `capacity_expansion` | `quality_improvement` | `customer_satisfaction`

Short aliases (also accepted): `financial` | `efficiency` | `growth` | `risk`

---

### 2.6 Capability

A capability is something the organization must be able to do.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Capability / skill name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Team that owns this capability | `ownedBy` | team reference | ✅ |
| Other capabilities this depends on | `dependsOn` | [capability references] | — |
| Current maturity level | `maturity.current` | `basic`/`intermediate`/`advanced`/`expert` | ✅ |
| Target maturity level | `maturity.target` | `basic`/`intermediate`/`advanced`/`expert` | — |
| Tools used to perform this | `resources.toolsUsed` | [system references] | — |
| Number of people needed | `resources.peopleRequired` | number | — |
| Average hours to execute once | `resources.avgTimePerExecution` | number | — |
| How critical is this? | `criticality` | `low`/`medium`/`high`/`critical` | — |
| Is this a market differentiator? | `differentiator` | boolean | — |

**Maturity levels:** `basic` | `intermediate` | `advanced` | `expert`

---

### 2.7 Process

A process is a repeatable operational workflow.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Process name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Team or role that runs this process | `performedBy` | team or role reference | ✅ |
| Metric that tracks this process | `measuredBy` | metric reference | ✅ |
| Tools / systems used | `uses` | [system references] | — |
| Ordered list of steps | `steps` | [step references] | ✅ (≥1) |
| Average days to complete | `metrics.avgDuration` | number | — |
| % of runs that succeed | `metrics.successRate` | number (0–1) | — |
| Average client satisfaction score | `metrics.clientSatisfaction` | number | — |
| Automation level | `automation.level` | `none`/`partial`/`full` | — |
| Automated steps | `automation.automated` | [string list] | — |
| Manual steps | `automation.manual` | [string list] | — |

> ❌ **Not valid on `process`:** `requires`, `contributesTo`
> - `process.requires` is **E215** — only `offering` may declare `requires`. To express that a process depends on a capability, ensure the offering declares `offering.requires: [CapabilityName]`. Do not use the deprecated `capability.supports`.
> - `process.contributesTo` is **E216** — process entities may not link to objectives. Strategic goals are connected via `objective.achievedThrough: [OfferingName]`. Place this on the `objective` entity, not on the process.

---

### 2.8 Step

A step is a single atomic activity inside a process.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Step name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Process this step belongs to | `partOf` | process reference | ✅ |
| Role or team who performs this | `performedBy` | team/role reference | ✅ |
| Sequence position (1 = first) | `order` | number | ✅ |
| Duration in minutes | `duration` | number | — |
| Estimated hours of effort | `estimatedEffort` | number | — |
| Steps that must complete first | `dependsOn` | [step references] | — |
| Inputs consumed | `inputs` | [string list] | — |
| Outputs produced | `outputs` | [string list] | — |
| Tangible deliverables | `deliverables` | [string list] | — |
| Tools used | `uses` | [system references] | — |
| Criteria for success | `successCriteria` | [string list] | — |
| Can be delegated to a junior? | `delegatable` | boolean | — |
| Automation potential | `automationPotential` | `low`/`medium`/`high` | — |

> ❌ **Not valid on `step`:** `requires`, `contributesTo`
> - A step inherits the capability requirements through the offering chain. Do not add `requires` directly to a step.
> - Objective links go on `objective.achievedThrough`, not on steps.

---

### 2.9 Package

A package is how an offering is bundled and sold.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Package name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Which offering this packages | `offering` | offering reference | ✅ |
| Tier in the lineup | `tier` | `entry`/`standard`/`premium`/`enterprise` | — |
| Position (1=lowest) | `position` | number | — |
| What is included | `includes` | [string list] | — |
| What is excluded | `excludes` | [string list] | — |
| Pricing model type | `pricing.model` | pricing model enum | ✅ |
| Base price | `pricing.basePrice` | number | ✅ |
| Currency | `pricing.currency` | string | — |
| Payment terms | `pricing.paymentTerms` | string | — |
| Duration in days | `delivery.duration` | number | — |
| Delivery format | `delivery.format` | `remote`/`onsite`/`hybrid` | — |
| Number of meetings | `delivery.meetings` | number | — |
| Max revisions allowed | `boundaries.maxRevisions` | number | — |
| Response time SLA | `boundaries.responseTime` | string | — |
| Scope description | `boundaries.scope` | string | — |
| Who this is designed for | `targets` | [segment references] | — |

---

### 2.10 Team

A team is an organizational unit that owns work.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Team name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Headcount | `size` | number OR `{ current: number, target: number }` | ✅ |
| Roles in this team | `roles` | [role references] | — |
| Billable hours per month per person | `capacity.billableHours` | number | — |
| Utilization rate | `capacity.utilization` | number (0–1) | — |
| Lead role | `structure.leadRole` | role reference | — |
| Reports to | `structure.reportingTo` | string | — |

> **Capabilities** are linked from the capability entity via `capability.ownedBy: TeamName`. Do not use `team.owns` — it is deprecated in favour of `capability.ownedBy`.

---

### 2.11 Role

A role is a responsibility profile within a team.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Role title | entity name | identifier | ✅ |
| Description | `description` | string | — |
| List of responsibilities | `responsibilities` | [string list] | — |
| Capabilities required for this role | `capabilities` | [capability refs with level] | — |
| Compensation type | `compensation.type` | string | — |
| Salary / compensation range | `compensation.range` | [min, max] | — |

---

### 2.12 System

A system is a technology platform or tool.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| System / tool name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Type of system | `type` | `saas`/`internal`/`infrastructure`/`custom`/`external` | ✅ |
| Vendor name | `vendor` | string | — |
| Monthly cost | `cost.monthly` | number | — |
| Annual cost | `cost.annual` | number | — |
| Connected systems | `integration.connectedTo` | [system references] | — |
| API available? | `integration.apiAvailable` | boolean | — |

> Systems are referenced from `process.uses` and `step.uses` — do not add `usedBy` or `supports` on system entities. Those fields are deprecated.

---

### 2.13 Objective

A strategic company goal.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Objective name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Time period covered (e.g. "FY2025", "Q1–Q4 2025") | `timeframe` | string | ✅ |
| Type of objective | `type` | `financial`/`operational`/`strategic`/`customer` | — |
| Metric being targeted | `target.metric` | string | — |
| Current value | `target.current` | number | — |
| Target value | `target.target` | number | — |
| Deadline | `target.deadline` | ISO date string | — |
| Metrics that track this | `measuredBy` | [metric references] | ✅ |
| Offerings that achieve this objective | `achievedThrough` | [offering references] | ✅ |

---

### 2.14 Metric

A performance measurement.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Metric name | entity name | identifier | ✅ |
| Description | `description` | string | ✅ |
| Unit of measurement | `unit` | string | ✅ |
| Target value | `target` | number | ✅ |
| Baseline / current value | `baseline` | number | ✅ |
| Measurement frequency | `frequency` | string | ✅ |
| Type of metric | `type` | `financial`/`operational`/`customer`/`quality`/`growth` | — |
| Calculation formula | `calculation` | string | — |
| Current value (nested alternative) | `targets.current` | number | — |
| Period targets (nested alternative) | `targets.q1`, `targets.q4`, etc. | number | — |
| Frequency (nested alternative) | `measurement.frequency` | string | — |
| Data source (nested alternative) | `measurement.source` | string | — |
| Metric owner (nested alternative) | `measurement.owner` | string | — |

> **Canonical form:** Use flat `target`, `baseline`, `frequency` fields. The nested `targets{}`/`measurement{}` form is also valid for richer data but not required.

---

### 2.15 Journey

A journey maps the client's experience through the buying and delivery lifecycle.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Journey name | entity name | identifier | ✅ |
| Target segments | `targets` | [segment references] | — (≥1 recommended) |
| Related offering | `offering` | offering reference | — |
| Journey stages | `stages` | list of stage objects | ✅ (≥1) |
| Stage name | `stages[].name` | string | ✅ |
| Stage goal | `stages[].goal` | string | — |
| Stage touchpoints | `stages[].touchpoints` | [string list] | — |
| Stage duration | `stages[].duration` | number (days) | — |
| Client state during stage | `stages[].clientState` | string | — |
| Conversion barriers | `stages[].conversionBarriers` | [{ barrier, mitigation }] | — |
| Exit criteria | `stages[].exitCriteria` | string | — |
| Success criteria | `stages[].successCriteria` | [string list] | — |
| Awareness to eval conversion | `metrics.awarenessToEval` | number (0–1) | — |
| Eval to close conversion | `metrics.evalToClose` | number (0–1) | — |
| Overall conversion rate | `metrics.overallConversion` | number (0–1) | — |
| Average days to close | `metrics.avgTimeToClose` | number | — |

> **Note:** Use `stages` (not `phases`) as the field name for the list of journey steps.

---

### 2.16 PricingModel

A pricing model describes the commercial logic behind how offerings are priced.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| PricingModel name | entity name | identifier | ✅ |
| Pricing type | `type` | pricing model type enum | ✅ |
| Description | `description` | string | ✅ |
| Calculation basis | `calculation.basis` | string | — |
| Calculation methodology | `calculation.methodology` | string | — |
| Value capture ratio | `calculation.valueCapture` | number (0–1) | — |
| Base price | `structure.basePrice` | number | — |
| Add-ons | `structure.addOns` | [{ name: string, price: number }] | — |
| Payment terms | `terms.payment` | string | — |
| Refund policy | `terms.refundPolicy` | string | — |
| Price adjustment policy | `terms.priceAdjustment` | string | — |

**Type values:** `fixed_project` | `monthly_retainer` | `value_based` | `tiered_subscription` | `usage_based` | `hybrid`

---

## 3. Relationship Attribute Mappings

### `targets` (offering → segment)

| Input Data | Attribute | Type |
|---|---|---|
| Primary or secondary target? | `priority` | `primary` / `secondary` |
| How well does offering fit segment? (0–1) | `fitScore` | number |

### `requires` (offering → capability)

| Input Data | Attribute | Type |
|---|---|---|
| Required skill level | `proficiency` | `basic`/`intermediate`/`advanced`/`expert` |
| How critical is this capability? | `criticality` | `low`/`medium`/`high` |

### `capabilities` on `role` entity

| Input Data | Attribute | Type |
|---|---|---|
| Proficiency level of this role in this capability | `level` | `basic`/`intermediate`/`advanced`/`expert` |

### `achievedThrough` on `objective`

References the offering entities that collectively achieve this objective. No inline attributes are needed — add offerings to the list directly.

```csl
objective GrowRevenue {
  achievedThrough: [ServiceProductization, AdvisoryRetainer]
}
```

---

## 4. Ambiguous Data — Resolution Rules

| Situation | Rule |
|---|---|
| A service has sub-components | Model main service as `offering`, sub-components as included items in `package.includes` |
| A team both owns capabilities AND runs processes | Create both `capability` (ownedBy team) and `process` (performedBy team) |
| A process is shared across offerings | Create one `process` and reference it from multiple `offering.packages` |
| An outcome maps to multiple offerings | Create one `outcome` and reference it in each `offering.delivers` |
| A segment overlaps with another | Create distinct `segment` entities; the offering can `targets` both |
| Data doesn't have a clear CSL equivalent | Use `meta.notes` to annotate the closest entity with the extra context |

---

## 5. Name Generation Rules

When converting raw names to CSL entity names:

1. Remove all punctuation
2. Capitalize the first letter of each word (PascalCase)
3. Join without spaces

| Raw Name | CSL Name |
|---|---|
| "Service Productization" | `ServiceProductization` |
| "Founder-Led Agencies" | `FounderLedAgencies` |
| "CRM (HubSpot)" | `CRM` |
| "B2B SaaS Advisory" | `B2BSaaSAdvisory` |
| "2nd Offering" | `SecondOffering` (never start with a number) |

---

## 6. Case Study Mapping

### 2.X CaseStudy

A `caseStudy` represents a past client engagement used as social proof in proposals.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Client or project name | `client` | string | ✅ |
| Industry / sector | `industry` | string | — |
| Problem the client faced | `challenge` | string | ✅ |
| What was built or delivered | `solution` | string | ✅ |
| Measurable results / success indicators | `outcome` | string | ✅ |
| Tools and technologies involved | `technologies` | [string list] | — |

**Rule:** Name using PascalCase describing the engagement — e.g. `AgencyRebrand`, `FinTechPlatformLaunch`. Reference from `company.caseStudies`.

**Note:** `caseStudy` entities are **not** graph nodes in the main structural model. They are company content entities used solely for proposal generation output. Do not create relationship edges from `caseStudy` to other entity types.
