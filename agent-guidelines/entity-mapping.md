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
| Short description of what the company does | `description` | string | — |
| City, country of headquarters | `headquarters` | string | — |
| Year the business was started | `founded` | number | — |
| List of geographic or industry markets | `markets` | [market references] | — |
| List of services or products offered | `offerings` | [offering references] | — |
| Strategic goals | `objectives` | [objective references] | — |

**Rule:** There is exactly one `company` entity per model.

---

### 2.2 Offering

An offering is any service, product, or program the company sells or delivers.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Service / product name | entity name (PascalCase) | identifier | ✅ |
| Description of what it does | `description` | string | — |
| Customer groups it serves | `targets` | [segment references] | ✅ |
| Geographic / industry markets | `operatesIn` | [market references] | — |
| Skills / abilities needed to deliver | `requires` | [capability references] | ✅ |
| Changes or results it creates for clients | `delivers` | [outcome references] | ✅ |
| KPIs used to measure success | `measuredBy` | [metric references] | — |
| Strategic goals it contributes to | `contributesTo` | [objective references] | — |
| Average contract / project value | `economics.avgDealSize` | number | — |
| Average hours to deliver | `economics.avgDeliveryHours` | number | — |
| Gross margin percentage | `economics.targetMargin` | number (0–1) | — |
| Revenue per client over their lifetime | `economics.clientLifetimeValue` | number | — |
| % of prospects who convert to clients | `performance.conversionRate` | number (0–1) | — |
| Average days from first contact to signed deal | `performance.avgSalesCycle` | number | — |
| % of clients who renew | `performance.clientRetention` | number (0–1) | — |
| Pricing tiers / packages | `packages` | [package references] | — |

**Naming rule:** Convert to PascalCase. "Service Productization" → `ServiceProductization`

---

### 2.3 Segment

A segment is a distinct group of potential customers.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Segment / customer group name | entity name | identifier | ✅ |
| Description of the group | `description` | string | — |
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
| Offerings that create this outcome | `achievedThrough` | [offering references] | — |
| Metrics that track this outcome | `measuredBy` | [metric references] | — |
| Annual revenue impact | `economicValue.annualRevenue` | number | — |
| Annual cost reduction | `economicValue.costReduction` | number | — |
| Hours saved per year | `economicValue.timeSaving` | number | — |
| Risk value protected | `economicValue.riskMitigation` | number | — |
| Capacity multiplier | `economicValue.capacityExpansion` | number | — |
| Client situation before engagement | `clientState.before` | string | — |
| Client situation after engagement | `clientState.after` | string | — |

**Outcome type values:**  
`revenue_increase` | `cost_reduction` | `time_saving` | `risk_mitigation` | `capacity_expansion` | `quality_improvement` | `customer_satisfaction`

---

### 2.6 Capability

A capability is something the organization must be able to do.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Capability / skill name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Team that owns this capability | `ownedBy` | team reference | ✅ |
| Offerings this capability enables | `supports` | [offering references] | — |
| Other capabilities this depends on | `dependsOn` | [capability references] | — |
| Current maturity level | `maturity.current` | maturity enum | — |
| Target maturity level | `maturity.target` | maturity enum | — |
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
| Description | `description` | string | — |
| Team that runs this process | `performedBy` | team reference | ✅ |
| Tools / systems used | `uses` | [system references] | — |
| Offerings this process supports | `supports` | [offering references] | — |
| Ordered list of steps | `steps` | [step references] | ✅ (≥1) |
| Average days to complete | `metrics.avgDuration` | number | — |
| % of runs that succeed | `metrics.successRate` | number (0–1) | — |
| Average client satisfaction score | `metrics.clientSatisfaction` | number | — |
| Automation level | `automation.level` | `none`/`partial`/`full` | — |
| Automated steps | `automation.automated` | [string list] | — |
| Manual steps | `automation.manual` | [string list] | — |

> ❌ **Not valid on `process`:** `requires`, `contributesTo`
> - `process.requires` is **E215** — only `offering` may declare `requires`. Capabilities needed by a process are modelled by the capability declaring `supports: [OfferingName]`.
> - `process.contributesTo` is **E216** — only `offering` and `capability` may link to objectives. If this process serves a strategic goal, place `contributesTo` on the offering or capability it supports.

---

### 2.8 Step

A step is a single atomic activity inside a process.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Step name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Process this step belongs to | `partOf` | process reference | ✅ |
| Role or team who performs this | `performedBy` | team/role reference | ✅ |
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
> - A step inherits the offering-level `requires` through the process and capability chain. Do not add `requires` directly to a step.
> - `contributesTo` applies at offering/capability level only, not at the individual step level.

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
| Description | `description` | string | — |
| Roles in this team | `roles` | [role references] | — |
| Capabilities this team owns | `owns` | [capability references] | — |
| Current headcount | `size.current` | number | — |
| Target headcount | `size.target` | number | — |
| Billable hours per month per person | `capacity.billableHours` | number | — |
| Utilization rate | `capacity.utilization` | number (0–1) | — |
| Lead role | `structure.leadRole` | role reference | — |
| Reports to | `structure.reportingTo` | string | — |

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
| Description | `description` | string | — |
| Type of system | `type` | `saas`/`internal`/`infrastructure`/`custom` | — |
| Vendor name | `vendor` | string | — |
| Teams that use this | `usedBy` | [team references] | — |
| Processes this supports | `supports` | [process references] | — |
| Monthly cost | `cost.monthly` | number | — |
| Annual cost | `cost.annual` | number | — |
| Connected systems | `integration.connectedTo` | [system references] | — |
| API available? | `integration.apiAvailable` | boolean | — |

---

### 2.13 Objective

A strategic company goal.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Objective name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Type of objective | `type` | `financial`/`operational`/`strategic`/`customer` | — |
| Metric being targeted | `target.metric` | metric reference | — |
| Current value | `target.current` | number | — |
| Target value | `target.target` | number | — |
| Deadline | `target.deadline` | ISO date string | — |
| Metrics that track this | `measuredBy` | [metric references] | — |
| Offerings that contribute | `contributedBy` | [offering refs with impact] | — |

---

### 2.14 Metric

A performance measurement.

| Input Data Field | CSL Field | Type | Required |
|---|---|---|---|
| Metric name | entity name | identifier | ✅ |
| Description | `description` | string | — |
| Type of metric | `type` | `financial`/`operational`/`customer`/`quality`/`growth` | — |
| Unit of measurement | `unit` | string | — |
| Calculation formula | `calculation` | string | — |
| Current value | `targets.current` | number | — |
| Period targets | `targets.q1`, `targets.q4`, etc. | number | — |
| Measurement frequency | `measurement.frequency` | string | — |
| Data source | `measurement.source` | string | — |
| Metric owner | `measurement.owner` | string | — |

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

### `contributedBy` on `objective`

| Input Data | Attribute | Type |
|---|---|---|
| % of objective achieved by this offering | `impact` | number (0–1) |

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
