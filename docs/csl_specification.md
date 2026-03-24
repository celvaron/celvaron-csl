# CSL Language Specification

**Version:** 1.0  
**Status:** Production Ready

---

## Table of Contents

1. [Language Overview](#1-language-overview)
2. [Entity Types](#2-entity-types)
3. [Schema Block](#3-schema-block)
4. [Relationship Types](#4-relationship-types)
5. [Syntax Rules](#5-syntax-rules)
6. [Graph Model Schema](#6-graph-model-schema)
7. [Validation Rules](#7-validation-rules)
8. [Visualization System](#8-visualization-system)
9. [AS-IS / TO-BE Modeling](#9-as-is--to-be-modeling)
10. [Best Practices](#10-best-practices)
11. [Quotera Export](#11-quotera-export)

---

## 1. Language Overview

### What CSL Models

CSL models a company as a **directed graph**. Every business element is a node. Every relationship between elements is a directed edge.

```
Nodes  = entities (offerings, capabilities, teams, markets, etc.)
Edges  = relationships (targets, requires, ownedBy, performedBy, etc.)
```

### Three Modeling Dimensions

| Dimension | Question | Entities |
|---|---|---|
| Structural | What exists? | company, offering, segment, market, team, role, system |
| Operational | How does work flow? | capability, process, step |
| Commercial | How does value flow? | outcome, package, pricingModel, journey, metric, objective |

### Value Chain

```
Market Need → Segment → Offering → Outcome → Economic Value
                            ↓
                       Capability → Process → Step → Team
                            ↓
                       Package → Pricing → Revenue
```

---

## 2. Entity Types

### 2.1 `company`

The top-level entity. **Exactly one per model.**

```csl
company AcmeConsulting {
  name: "Acme Consulting"
  description: "Strategy advisory for service businesses"
  headquarters: "Berlin, Germany"
  founded: 2018
  markets: [Europe, NorthAmerica]
  offerings: [ServiceProductization, StrategyAdvisory]
  objectives: [GrowARR, ImproveMargins]
  caseStudies: [AgencyRebrand, FinTechLaunch]

  voice: {
    tone: "Direct and confident. We speak like senior practitioners, not salespeople."
    formality: "semi-formal"          // formal | semi-formal | conversational
    perspective: "we"                 // we | third-person
    language: "en"                    // pl | en | both
    dos: [
      "Lead with outcomes, not activities",
      "Use concrete numbers and examples"
    ]
    donts: [
      "Avoid buzzwords and empty superlatives",
      "No passive voice"
    ]
    examplePhrases: [
      "We help founders turn custom work into scalable products.",
      "Our clients typically 3× their capacity within six months."
    ]
  }
}
```

**Required fields:** `name`  
**Constraint:** Unique per model file

**`voice` block fields:**

| Field | Type | Description |
|---|---|---|
| `tone` | string | 2–3 sentences describing the overall writing style |
| `formality` | `formal` / `semi-formal` / `conversational` | Register for written communications |
| `perspective` | `we` / `third-person` | Grammatical person used in copy |
| `language` | `pl` / `en` / `both` | Primary language(s) |
| `dos` | [string list] | Writing behaviours to adopt |
| `donts` | [string list] | Writing behaviours to avoid |
| `examplePhrases` | [string list] | Short illustrative phrases in the desired tone |

---

### 2.2 `offering`

A product or service delivered to customers.

```csl
offering ServiceProductization {
  description: "Transform custom services into packaged offerings"
  targets: [FounderLedAgencies] with {
    FounderLedAgencies: { priority: primary, fitScore: 0.95 }
  }
  operatesIn: [Europe, NorthAmerica]
  requires: [
    ServiceDesign with { proficiency: expert, criticality: high },
    PricingStrategy with { proficiency: advanced, criticality: high }
  ]
  delivers: [RevenueGrowth, ReducedFounderDependency]
  measuredBy: [ClientARR, PackageConversionRate]
  economics: {
    avgDealSize: 24900
    avgDeliveryHours: 120
    targetMargin: 0.65
    clientLifetimeValue: 180000
  }
  performance: {
    conversionRate: 0.35
    avgSalesCycle: 14
    clientRetention: 0.82
  }
}
```

**Required fields:** `targets` (≥1), `requires` (≥1), `delivers` (≥1), `economics.avgDealSize`, `economics.targetMargin`

---

### 2.3 `segment`

A customer group with shared characteristics.

```csl
segment FounderLedAgencies {
  description: "Marketing agencies with founder-led delivery"
  characteristics: {
    industry: "Professional Services"
    revenueRange: [500000, 5000000]
    teamSize: [5, 50]
    geography: ["EU", "US"]
  }
  problems: [
    "Stuck in hourly billing",
    "Cannot scale without founder"
  ]
  motivations: [
    "Increase profitability",
    "Reduce founder dependency"
  ]
  buyingBehavior: {
    decisionMaker: "Founder/CEO"
    avgDecisionTime: 14
    priceSensitivity: "medium"
    referralDriven: true
  }
}
```

---

### 2.4 `market`

A geographic or industry market.

```csl
market Europe {
  description: "European B2B professional services market"
  type: "geographic"
  region: "EU"
  countries: ["DE", "UK", "FR", "NL", "ES"]
  size: {
    estimatedCompanies: 45000
    addressableMarket: 2300000000
  }
  characteristics: {
    maturity: "growing"
    competition: "fragmented"
    regulation: "moderate"
  }
}
```

**Market types:** `geographic`, `industry`, `niche`

---

### 2.5 `outcome`

The transformation or value an offering delivers to clients.

```csl
outcome RevenueGrowth {
  description: "Increase MRR through packaged services"
  type: "revenue_increase"
  baseline: { metric: "MRR", value: 50000, unit: "EUR" }
  target: { metric: "MRR", value: 85000, unit: "EUR", timeframe: "6 months" }
  achievedThrough: [ServiceProductization]
  measuredBy: [MRR]
  economicValue: {
    annualRevenue: 420000
    timeSaving: 480
    capacityExpansion: 2.5
  }
  clientState: {
    before: "Trading time for money"
    after: "Scalable packages with delegatable delivery"
  }
}
```

**Outcome types:** `revenue_increase`, `cost_reduction`, `time_saving`, `risk_mitigation`, `capacity_expansion`, `quality_improvement`, `customer_satisfaction`

---

### 2.6 `capability`

Something the organization must be able to do.

```csl
capability ServiceDesign {
  description: "Design productized service offerings"
  ownedBy: StrategyTeam
  dependsOn: [ClientResearch, ValueCalculation]
  maturity: {
    current: "advanced"
    target: "expert"
  }
  resources: {
    toolsUsed: [Miro, Figma]
    peopleRequired: 2
    avgTimePerExecution: 40
  }
  criticality: "high"
  differentiator: true
}
```

**Required fields:** `ownedBy`, `maturity.current`  
**Maturity levels:** `basic`, `intermediate`, `advanced`, `expert`  
**Criticality values:** `low`, `medium`, `high`, `critical`

---

### 2.7 `process`

A repeatable operational workflow.

```csl
process ClientOnboarding {
  description: "30-day structured client onboarding"
  performedBy: ClientSuccessTeam
  measuredBy: ClientSatisfactionScore
  uses: [CRM, ProjectManagement]
  steps: [
    KickoffScheduling,
    DiscoveryPreparation,
    KickoffWorkshop,
    FrameworkImplementation,
    FirstDeliverable
  ]
  metrics: {
    avgDuration: 30
    successRate: 0.92
    clientSatisfaction: 4.6
  }
  automation: {
    level: "partial"
    automated: ["KickoffScheduling"]
    manual: ["KickoffWorkshop", "FirstDeliverable"]
  }
}
```

**Required fields:** `performedBy`, `measuredBy`, at least one `step` entity with `partOf` pointing to this process

---

### 2.8 `step`

An atomic activity inside a process.

```csl
step KickoffWorkshop {
  description: "2-hour outcome mapping workshop"
  partOf: ClientOnboarding
  performedBy: PrincipalConsultant
  duration: 120
  estimatedEffort: 4
  dependsOn: [DiscoveryPreparation]
  inputs: [ClientQuestionnaire, IndustryResearch]
  outputs: [OutcomeArchitecture, ValueCalculation]
  deliverables: [
    "Outcome mapping canvas",
    "Economic value calculation"
  ]
  uses: [Miro]
  successCriteria: [
    "Client can articulate their primary transformation",
    "Economic value quantified"
  ]
  delegatable: false
  automationPotential: "low"
}
```

**Required fields:** `partOf`, `performedBy`  
**Duration/effort:** in minutes and hours respectively

---

### 2.9 `package`

How an offering is bundled and priced.

```csl
package FoundationPackage {
  description: "Core productization framework"
  offering: ServiceProductization
  tier: "entry"
  position: 1
  includes: [OutcomeArchitecture, ProblemSolutionFit, BasicPackageDesign]
  excludes: [AdvancedPricing, DeliveryAutomation]
  pricing: {
    model: "fixed_project"
    basePrice: 12900
    currency: "EUR"
    paymentTerms: "50% upfront, 50% on delivery"
  }
  delivery: {
    duration: 30
    format: "hybrid"
    meetings: 4
    async_work: true
  }
  boundaries: {
    maxRevisions: 2
    responseTime: "24 hours"
    scope: "Single core offering only"
  }
  targets: [FounderLedAgencies]
}
```

**Required fields:** `offering`, `pricing`  
**Tiers:** `entry`, `standard`, `premium`, `enterprise`

---

### 2.10 `pricingModel`

Defines how a package is priced.

```csl
pricingModel FixedProject {
  type: "fixed_project"
  description: "One-time project with fixed deliverables"
  calculation: {
    basis: "value"
    methodology: "economic_impact"
    valueCapture: 0.15
  }
  structure: {
    basePrice: 12900
    addOns: [
      { name: "Additional offering", price: 3000 }
    ]
  }
  terms: {
    payment: "milestone"
    refundPolicy: "satisfaction_guarantee"
    priceAdjustment: "annual"
  }
}
```

**Pricing types:** `fixed_project`, `monthly_retainer`, `value_based`, `tiered_subscription`, `usage_based`, `hybrid`

---

### 2.11 `journey`

How a client moves from awareness to purchase and beyond.

```csl
journey ServiceProductizationJourney {
  for: [FounderLedAgencies]
  offering: ServiceProductization
  phases: [
    {
      name: "Awareness"
      duration: 7
      clientState: "Recognizes scaling problem"
      touchpoints: [LinkedInContent, ReferralConversation]
      keyQuestions: ["Can this work for me?"]
      content: [CaseStudy, ROICalculator]
    },
    {
      name: "Evaluation"
      duration: 14
      clientState: "Evaluating fit and ROI"
      touchpoints: [AuditCall, ProposalReview]
      processes: [InitialDiscovery]
      conversionBarriers: [
        { barrier: "Price concern", mitigation: "ROI demonstration" }
      ]
      exitCriteria: "Signed proposal or explicit no"
    },
    {
      name: "Onboarding"
      duration: 30
      processes: [ClientOnboarding]
      successCriteria: ["Framework completed", "First package launched"]
    }
  ]
  metrics: {
    awarenessToEval: 0.15
    evalToClose: 0.35
    overallConversion: 0.0525
    avgTimeToClose: 21
  }
}
```

---

### 2.12 `team`

An organizational unit that owns work.

```csl
team StrategyTeam {
  description: "Core consulting delivery"
  roles: [PrincipalConsultant, SeniorConsultant]
  size: { current: 3, target: 5 }
  capacity: {
    billableHours: 120
    utilization: 0.75
  }
  structure: {
    leadRole: PrincipalConsultant
    reportingTo: "CEO"
  }
}
```

---

### 2.13 `role`

A responsibility profile within a team.

```csl
role PrincipalConsultant {
  description: "Leads client engagements independently"
  responsibilities: [
    "Client relationship ownership",
    "Strategic guidance and framework design",
    "Quality assurance on deliverables"
  ]
  capabilities: [
    ServiceDesign with { level: expert },
    PricingStrategy with { level: advanced }
  ]
  compensation: {
    type: "salary_bonus"
    range: [120000, 180000]
  }
}
```

---

### 2.14 `system`

A technology platform or tool.

```csl
system CRM {
  description: "Customer relationship management"
  type: "saas"
  vendor: "HubSpot"
  cost: { monthly: 450, annual: 5400 }
  integration: {
    connectedTo: [EmailPlatform, ProjectManagement]
    apiAvailable: true
  }
}
```

**System types:** `saas`, `internal`, `infrastructure`, `custom`, `external`

---

### 2.15 `objective`

A strategic company goal.

```csl
objective GrowARR {
  description: "Grow annual recurring revenue to €2M"
  type: "financial"
  timeframe: "FY2026"
  target: {
    metric: "ARR"
    current: 800000
    target: 2000000
    deadline: "2026-12-31"
  }
  measuredBy: [ARR, MRR]
  achievedThrough: [ServiceProductization, StrategyAdvisory]
}
```

**Objective types:** `financial`, `operational`, `strategic`, `customer`  
**Required fields:** `description`, `timeframe`, `measuredBy` (≥1), `achievedThrough` (≥1)

---

### 2.16 `metric`

A performance measurement.

```csl
metric ARR {
  description: "Annual Recurring Revenue"
  type: "financial"
  unit: "EUR"
  calculation: "SUM(mrr * 12)"
  targets: {
    current: 800000
    q1: 1000000
    q4: 2000000
  }
  measurement: {
    frequency: "monthly"
    source: "CRM"
    owner: "CFO"
  }
}
```

**Metric types:** `financial`, `operational`, `customer`, `quality`, `growth`

---

### 2.17 `caseStudy`

A past client engagement used as social proof in proposals.

```csl
caseStudy AgencyRebrand {
  client: "NorthLight Agency"
  industry: "Marketing & Creative"
  challenge: "Stuck in hourly billing — founder handling all client work personally"
  solution: "Designed three packaged service tiers and trained delivery team over 8 weeks"
  outcome: "Revenue up 40% in 6 months; founder now works on the business, not in it"
  technologies: ["Notion", "Stripe", "HubSpot"]
}
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `client` | string | ✅ | Client or project name |
| `industry` | string | — | Industry or sector |
| `challenge` | string | ✅ | Problem the client faced |
| `solution` | string | ✅ | What was built or delivered |
| `outcome` | string | ✅ | Measurable results or key success indicators |
| `technologies` | [string list] | — | Tools and technologies involved |

**Rule:** `caseStudy` entities are referenced from `company.caseStudies`. They are not graph nodes in the main model — they are company content used solely for proposal generation.

---

### 2.18 Shared Attributes

All entities support:

```csl
entity SomeEntity {
  // entity-specific fields...

  meta: {
    confidence: "high" | "medium" | "low"
    source: "client_interview" | "document_analysis" | "workshop" | "assumption"
    lastReviewed: "2024-03-15"
    reviewer: "principal_consultant"
    tags: ["core", "differentiator"]
    notes: "Additional context"
  }
  status: "draft" | "validated" | "active" | "deprecated"
  doc: "knowledge/offerings/my-offering.md"
}
```

---

## 3. Schema Block

### 3.1 Purpose and Backward Compatibility

The `schema` block is an optional top-level construct that makes three previously implicit platform conventions machine-readable:

| Concern | Without schema | With schema |
|---|---|---|
| Section membership | Platform hardcodes entity→section mapping | Declared in `sections` block |
| Relation semantics | All field references treated identically | Each field assigned a named `kind` |
| Reverse traversal | Heuristics or hardcoded conventions | Declared via `inverse` field |

**Backward compatibility:** A CSL file without a `schema` block is fully valid. The parser produces a complete graph model and all downstream tools continue to apply their existing default inference. The schema block is purely additive.

---

### 3.2 Placement and Syntax

The `schema` block appears at most once per model, after file-level metadata and before the first entity block:

```csl
version: "1.0"
state: "current"
author: "Author Name"
description: "Model description"

schema {
  sections: { ... }
  relations: { ... }
}

company MyCompany {
  // entity blocks follow
}
```

**Constraints:**
- At most one `schema` block per model — **ERROR** if a second block is encountered
- Must appear before any entity block — **ERROR** if placed after an entity
- Import files may not contain a `schema` block — **ERROR**; schema is model-scope only

**Top-level fields:**

| Field | Type | Level | Notes |
|---|---|---|---|
| `sections` | mapping block | O | Entity type → display section assignment |
| `relations` | mapping block | O | Field reference → relation kind declaration |

Both fields are optional; a `schema` block may declare only one of them.

---

### 3.3 `sections`

Maps stable section identifiers to lists of entity type keywords. Consumers use this to group entities into the correct display section without hardcoding.

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
}
```

**Section key rules:**
- PascalCase: `[A-Z][A-Za-z0-9]*` — **ERROR** if not matching
- Unique within the schema block — **ERROR** if duplicated
- Keys serve as stable API identifiers; display labels are derived from the key by consumers

**Entity type list rules:**
- Each value must be a known CSL entity type keyword — **ERROR** if unknown type
- An entity type may appear in exactly one section — **ERROR** if listed in two sections
- Entity types not assigned to any section generate a **WARNING** per unassigned type
- If `sections` is omitted entirely, the platform applies its built-in default grouping — no warning

---

### 3.4 `relations`

Maps `entityType.fieldName` references to a relation kind and, optionally, their inverse. This is the mechanism for communicating rendering intent and parent–child traversal without altering field syntax.

```csl
schema {
  relations: {
    // Composition: child is owned by parent, nested under it in views
    process.steps:             { kind: composition, inverse: step.partOf }
    offering.packages:         { kind: composition, inverse: package.offering }
    team.roles:                { kind: composition, inverse: role.memberOf }
    objective.measuredBy:      { kind: composition, inverse: metric.measures }
    market.segments:           { kind: composition }

    // Association: cross-reference between independent peer entities
    capability.ownedBy:        { kind: association, target: team }
    process.performedBy:       { kind: association, target: team }
    offering.delivers:         { kind: association, target: outcome }
    offering.targets:          { kind: association, target: segment }
    offering.requires:         { kind: association, target: capability }
    outcome.achievedThrough:   { kind: association, target: offering }
    objective.achievedThrough: { kind: association, target: offering }

    // Dependency: directional prerequisite, may form a DAG
    capability.dependsOn:      { kind: dependency }
    step.dependsOn:            { kind: dependency }

    // Extension: optional specialisation/augmentation link
    // offering.extends:       { kind: extension, target: offering }
  }
}
```

**Entry key format:** `entityType.fieldName`
- `entityType` must be a known CSL entity type — **ERROR**
- `fieldName` must be a valid camelCase identifier — **ERROR** if malformed
- Each `entityType.fieldName` pair may appear at most once — **ERROR** if duplicated
- A field may not be declared under two different `kind` values — **ERROR**

**Entry value fields:**

| Field | Type | Level | Notes |
|---|---|---|---|
| `kind` | `composition` \| `association` \| `dependency` \| `extension` | R | Semantic classification |
| `inverse` | `entityType.fieldName` | O | Reverse declaration on the counterpart entity |
| `target` | entity type keyword | O | Optional target entity type annotation |

---

### 3.5 Relation Kinds

Four built-in relation kinds are recognised. All existing CSL field names remain syntactically valid; `kind` is declarative metadata layered on top of existing syntax, not a replacement for it.

#### `composition`

The child entity is owned by and logically nested within the parent. Platforms render composition as a parent → child hierarchy in tree, detail, and service blueprint views.

| Property | Value |
|---|---|
| Rendering | Child nested under parent in hierarchical views |
| Cardinality default | One parent per child (hard cardinality set per entity in §7.3) |
| Graph edge `relationKind` | `"composition"` |
| `inverse` | Strongly recommended |

#### `association`

A cross-reference between independent peer entities. Neither is nested under the other. Platforms render as linked badges, chips, or cross-reference arrows on entity cards.

| Property | Value |
|---|---|
| Rendering | Linked badge or chip on entity card; cross-reference panel |
| Graph edge `relationKind` | `"association"` |

#### `dependency`

A directional prerequisite: the source requires the target to exist or be completed first. Forms a DAG. Platforms may use for critical-path and sequencing analysis.

| Property | Value |
|---|---|
| Rendering | Directed arrow; critical-path indicator |
| Graph edge `relationKind` | `"dependency"` |
| Cycles | Compile-time **ERROR** (same rule as circular step dependencies in §7.2) |

#### `extension`

The source entity optionally specialises or augments the target, inheriting context while remaining independently valid. Useful for offering variants, process templates, or capability specialisations.

| Property | Value |
|---|---|
| Rendering | Dashed specialisation link in architecture views |
| Graph edge `relationKind` | `"extension"` |

---

### 3.6 `inverse` Declarations

The `inverse` field identifies the reverse-direction declaration on the counterpart entity, enabling bidirectional traversal without heuristics.

```csl
// Declares that step.partOf is the reverse of process.steps
process.steps: { kind: composition, inverse: step.partOf }
```

**Syntax:** `inverse: entityType.fieldName`

| Rule | Severity |
|---|---|
| Referenced `entityType` is not a known CSL entity type | ERROR |
| Referenced `fieldName` is not a valid camelCase identifier | ERROR |
| Self-inverse: a field declares itself as its own inverse | ERROR |
| Asymmetric pair: A declares `inverse: B`, B does not declare `inverse: A` | WARNING — one-way traversal |
| Inverse field absent from counterpart entity definitions | WARNING — parse continues |
| Child instance populated, reverse field absent on child | WARNING — one-way edge emitted |

**On missing reverse fields:** When a `composition` inverse is declared but the child's reverse field is absent, the platform **nests the child using the parent-side list as authoritative**. Missing reverse fields never block rendering.

---

### 3.7 Schema vs. Inference Precedence

When a `schema` block is present, its declarations override platform inference for covered fields:

| Condition | Resolution |
|---|---|
| Schema declares `kind: composition`; inference would treat field as flat reference | Schema wins |
| Schema assigns entity type to a section; platform default disagrees | Schema wins |
| Field not covered by schema; platform applies inference | Inference applies |
| Schema block absent entirely | All inference applies (legacy behaviour) |

---

## 4. Relationship Types

### 4.1 Commercial Relationships

| Relationship | From | To | Meaning | Attributes |
|---|---|---|---|---|
| `targets` | offering | segment | Offering serves segment | priority, fitScore |
| `operatesIn` | offering | market | Offering active in market | penetration |
| `delivers` | offering | outcome | Offering delivers outcome | certainty, timeframe |
| `bundledIn` | offering | package | Offering included in package | — |
| `pricedBy` | package | pricingModel | Package uses pricing model | — |

### 4.2 Capability Relationships

| Relationship | From | To | Meaning | Attributes |
|---|---|---|---|---|
| `requires` | offering | capability | Offering needs capability | proficiency, criticality |
| `supports` | capability | offering | Capability enables offering | impact |
| `ownedBy` | capability | team | Team owns capability | — |
| `dependsOn` | capability | capability | Capability depends on another | — |

### 4.3 Operational Relationships

| Relationship | From | To | Meaning | Attributes |
|---|---|---|---|---|
| `performedBy` | process / step | team / role | Work executed by | — |
| `uses` | process / step | system | Technology used | frequency |
| `hasStep` | process | step | Process contains step | order, required |
| `partOf` | step | process | Step belongs to process | — |
| `dependsOn` | step | step | Step dependency | type: blocking / preferential |

### 4.4 Organizational Relationships

| Relationship | From | To | Meaning | Attributes |
|---|---|---|---|---|
| `hasRole` | team | role | Team contains role | count |
| `ownedBy` | capability | team | Team owns this capability | — |
| `reportingTo` | team | team | Structural reporting | — |

### 4.5 Strategic Relationships

| Relationship | From | To | Meaning | Attributes |
|---|---|---|---|---|
| `measuredBy` | offering / objective / process | metric | Success tracked by metric | weight |
| `achievedThrough` | objective | offering | Objective realized via offering | — |
| `delivers` | offering | outcome | Offering delivers this outcome | — |
| `requires` | offering | capability | Offering depends on capability | proficiency, criticality |

---

## 5. Syntax Rules

### 5.1 Basic Structure

```csl
entityType EntityName {
  fieldName: value
  fieldName: [listValue1, listValue2]
  fieldName: { nestedKey: nestedValue }
}
```

### 5.2 Entity Names

- PascalCase: `[A-Z][A-Za-z0-9]*`
- Unique within entity type
- No spaces, underscores, or hyphens
- Cannot start with a digit
- Reserved: `import`, `export`, `true`, `false`, `null`

✅ `ClientOnboarding`, `ServiceProductization`, `CFOAdvisory`  
❌ `client_onboarding`, `Service-Productization`, `2ndOffering`

### 5.3 Field Names

- camelCase: `[a-z][A-Za-z0-9]*`

✅ `targets`, `performedBy`, `avgDealSize`  
❌ `Targets`, `performed_by`

### 5.4 Value Types

| Type | Example |
|---|---|
| String | `"This is a string"` |
| Number | `12900`, `0.35` |
| Boolean | `true`, `false` |
| List | `[SegmentA, SegmentB]`, `["tag1", "tag2"]` |
| Object | `{ metric: "MRR", value: 50000 }` |
| Entity reference | `performedBy: StrategyTeam` |

### 5.5 Relationship Attributes

```csl
targets: [SegmentA, SegmentB] with {
  SegmentA: { priority: primary, fitScore: 0.95 }
  SegmentB: { priority: secondary, fitScore: 0.75 }
}

requires: [
  ServiceDesign with { proficiency: expert, criticality: high },
  PricingStrategy with { proficiency: advanced, criticality: medium }
]
```

### 5.6 Comments

```csl
// Single-line comment

/*
  Multi-line comment
*/
```

### 5.7 Imports

```csl
import "./segments.csl"
import "./capabilities.csl"
```

---

## 6. Graph Model Schema

The canonical output of parsing a CSL file is a JSON graph model.

### 6.1 Top-Level Structure

```json
{
  "meta": { },
  "nodes": [ ],
  "edges": [ ]
}
```

### 6.2 Meta Object

```json
{
  "meta": {
    "modelVersion": "1.0",
    "cslVersion": "1.0",
    "companyId": "acme-consulting",
    "state": "asis",
    "snapshotDate": "2024-03-15T10:30:00Z",
    "generatedAt": "2024-03-15T10:30:00Z",
    "generator": "csl-parser-v1.0",
    "author": "consultant_name",
    "project": "acme-transformation-2024",
    "schema": {
      "present": false,
      "sections": null,
      "relations": null
    }
  }
}
```

### 6.3 Node Object

```json
{
  "id": "offering:ServiceProductization",
  "type": "offering",
  "name": "ServiceProductization",
  "attributes": {
    "description": "Transform custom services into packaged offerings",
    "economics": {
      "avgDealSize": 24900,
      "targetMargin": 0.65
    }
  },
  "computed": {
    "centralityScore": 0.92,
    "impactScore": 0.88,
    "complexity": "high"
  }
}
```

**Node ID format:** `<entityType>:<EntityName>`

### 6.4 Edge Object

```json
{
  "from": "offering:ServiceProductization",
  "to": "segment:FounderLedAgencies",
  "type": "targets",
  "relationKind": "association",
  "attributes": {
    "priority": "primary",
    "fitScore": 0.95
  },
  "computed": {
    "weight": 1.0,
    "criticalPath": true
  }
}
```

**Node ID format:** `<entityType>:<EntityName>`

---

### 6.5 Schema Output

When a `schema` block is present in the source model, the parser emits its contents under `meta.schema`. Downstream consumers (renderers, analytics) read this to avoid hardcoding section assignments and relation semantics.

**`meta.schema` when schema block is absent:**

```json
"schema": { "present": false, "sections": null, "relations": null }
```

**`meta.schema` when schema block is present:**

```json
"schema": {
  "present": true,
  "sections": {
    "Offerings": ["offering", "package", "pricingModel"],
    "Processes": ["process", "step"]
  },
  "relations": {
    "process.steps": { "kind": "composition", "inverse": "step.partOf" },
    "capability.ownedBy": { "kind": "association", "target": "team" },
    "capability.dependsOn": { "kind": "dependency" }
  }
}
```

**`edge.relationKind`** is populated from the schema `relations` map if a matching entry exists for the edge's `type + from-entity-type`. If no schema entry exists, `relationKind` is `null` and consumer falls back to inference.

---

## 7. Validation Rules

### 7.1 Naming Rules

- Entity names match `[A-Z][A-Za-z0-9]*`
- Field names match `[a-z][A-Za-z0-9]*`
- Entity names unique within their type - ERROR if duplicated
- No reserved keywords as names - ERROR

### 7.2 Reference Rules

- All referenced entities must be declared in the model - ERROR
- References must point to the correct entity type - ERROR
- No circular step dependencies - ERROR

### 7.3 Cardinality Rules

| Entity | Field | Rule |
|---|---|---|
| `company` | (entity itself) | Exactly 1 per model |
| `offering` | `targets` | ≥ 1 |
| `offering` | `requires` | ≥ 1 |
| `offering` | `delivers` | ≥ 1 |
| `capability` | `ownedBy` | Exactly 1 |
| `process` | `performedBy` | Exactly 1 |
| `process` | `steps` | ≥ 1 |
| `step` | `partOf` | Exactly 1 |
| `package` | `offering` | Exactly 1 |
| `package` | `pricing` | Exactly 1 |

### 7.4 Semantic Warnings

- Offering without packages — WARNING
- Offering without performance metrics — WARNING
- Capability with no supporting processes — WARNING
- Package with no target segments — WARNING
- Process without metrics — WARNING
- Margin < 0.20 or > 0.90 — WARNING
- ConversionRate < 0.01 or > 0.99 — WARNING

### 7.5 Minimum Viable Model

A complete model should contain:

- ✅ 1 `company`
- ✅ ≥1 `offering`
- ✅ ≥1 `segment`
- ✅ ≥1 `outcome`
- ✅ ≥1 `capability`
- ✅ ≥1 `team`
- ✅ ≥1 `process`
- ⚠️ Warning if fewer than 3 offerings
- ⚠️ Warning if fewer than 5 capabilities

---

### 7.6 Schema Block Rules

Applied when a `schema` block is present. Schema rules run **after** syntax and reference validation.

**Structural rules (ERROR severity):**

| Rule | Notes |
|---|---|
| More than one `schema` block in a model | Second block rejected |
| `schema` block declared after an entity block | Must precede all entities |
| `schema` block in an imported file | Schema is model-scope only |
| `sections` key does not match `[A-Z][A-Za-z0-9]*` | Invalid identifier |
| `sections` key duplicated within the same schema | Duplicate section keys |
| `sections` lists an unknown entity type keyword | Typos caught here |
| Same entity type listed in two sections | Only one section per type |
| `relations` entry key is not `entityType.fieldName` format | Malformed entry key |
| `relations` entry `entityType` is unknown | Undefined entity type |
| `relations` entry `fieldName` is not camelCase | Malformed field name |
| Same `entityType.fieldName` declared twice | Duplicate relation entry |
| Same field declared under two different `kind` values | Ambiguous dual-kind |
| `inverse` references unknown `entityType` | Undefined entity type |
| `inverse` references malformed `fieldName` | Must be camelCase |
| Self-inverse (a field is its own inverse) | Circular self-reference |
| `dependency` relation forms a cycle in the model graph | Compile-time cycle |

**Consistency rules (WARNING severity — parse continues):**

| Rule | Notes |
|---|---|
| Entity type not assigned to any section | One WARNING per unassigned type |
| Asymmetric inverse pair (A→B but B does not declare →A) | One-way traversal only |
| Declared inverse field absent from counterpart entity definition | Missing reverse field |
| Entity instance has parent-side composition list populated but child has no reverse field | One-way edge emitted |

**Precedence matrix:**

| Schema present? | Field covered by schema? | Behaviour |
|---|---|---|
| No | — | Full inference (legacy) |
| Yes | Yes | Schema wins |
| Yes | No | Inference applies for uncovered fields |

---

## 8. Visualization System

### 8.1 Standard Views

| View | Focus | Audience |
|---|---|---|
| Company Architecture | Segments → Offerings → Capabilities → Teams | Executives |
| Capability Map | Teams × Capabilities × Offerings matrix | Ops / HR |
| Process Flow | Process → Steps → Dependencies | Operations |
| Service Blueprint | Swim lanes: Client / Front / Back / Tech | Service Design |
| Value Stream | Offerings → Outcomes → Economic Value | Strategy |
| Strategy Map | Objectives → Metrics → Contributions | Executives |
| Package Architecture | Offering → Package tiers + Pricing | Sales |
| Client Journey | Awareness → Evaluation → Purchase → Onboarding | Marketing |
| Change Impact Map | AS-IS vs TO-BE delta with color coding | Transformation |

### 8.2 View Configuration

```json
{
  "viewId": "capability-map",
  "focus": ["team", "capability", "offering"],
  "exclude": ["step", "system"],
  "relationships": ["owns", "supports", "requires"],
  "layout": { "type": "matrix", "groupBy": "team" },
  "filters": { "capability.criticality": ["high"] },
  "styling": { "colorBy": "team", "nodeSize": "impact" }
}
```

---

## 9. AS-IS / TO-BE Modeling

### 9.1 File Structure

```
project/
├── asis/model.csl
├── tobe/model.csl
└── comparison/delta.json
```

### 9.2 Change Types

| Value | Meaning |
|---|---|
| `new` | Doesn't exist in AS-IS |
| `removed` | Exists in AS-IS, not in TO-BE |
| `enhanced` | Improved/upgraded entity |
| `reduced` | Downgraded/simplified entity |
| `unchanged` | No change |

### 9.3 Change Metadata on Entities

```csl
capability ServiceDesign {
  ownedBy: StrategyTeam
  changeType: "enhanced"
  changes: {
    from: { maturity: "intermediate" }
    to: { maturity: "advanced" }
    rationale: "Delegation required to scale delivery"
    expectedImpact: "Enable 3x capacity increase"
    riskLevel: "medium"
    riskMitigation: "Overlap with founder during transition"
  }
}
```

---

## 10. Best Practices

- **Start small:** Company + 1-2 offerings + key capabilities, then expand
- **Use confidence levels:** Mark assumptions with `confidence: low`
- **Trace value:** Always connect offerings → outcomes → economic value
- **Model reality:** Document the AS-IS honestly, not aspirationally
- **Name precisely:** `ClientOnboardingProcess`, not `Onboarding`
- **Use consistent units:** EUR or USD, hours, days — pick and stick
- **Version control:** Commit CSL files to Git; tag stable versions
- **Progressive validation:** Syntax → References → Structure → Semantics → Completeness
