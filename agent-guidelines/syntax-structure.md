# Syntax & Structure

Complete reference of CSL syntax rules for agents and software generating valid CSL.

---

## 1. File Structure

A CSL model is a plain-text file with the `.csl` extension. It contains a sequence of entity blocks. There is no root wrapper — entities are declared at the top level.

```csl
// Optional imports
import "./segments.csl"

// Entity declarations (in any order)
company AcmeConsulting { ... }
segment FounderLedAgencies { ... }
offering ServiceProductization { ... }
```

**File encoding:** UTF-8  
**Line endings:** LF or CRLF both accepted  
**File extension:** `.csl`

---

## 2. Entity Block Syntax

```
entityType EntityName {
  fieldName: value
}
```

- `entityType` — one of the 16 valid entity keywords (lowercase)
- `EntityName` — PascalCase identifier unique within that entity type
- All fields are on their own line, indented with spaces or tabs (2 or 4 spaces recommended)
- Opening brace `{` must be on the same line as the declaration
- Closing brace `}` must be on its own line

---

## 3. Entity Name Rules

| Rule | Detail |
|---|---|
| Case | PascalCase — start with uppercase, no spaces |
| Pattern | `[A-Z][A-Za-z0-9]*` |
| Uniqueness | Unique within entity type (two offerings cannot share a name; an offering and a team can share a name but this is discouraged) |
| Max length | No hard limit; keep under 50 characters for readability |
| Reserved words | Cannot use `import`, `export`, `true`, `false`, `null`, `with` |
| No numbers at start | `2ndService` is invalid — use `SecondService` |

**Valid examples:**
```
CompanyName         ✅
ServiceProductization  ✅
CFOAdvisory         ✅
B2BSaaSAdvisory     ✅
```

**Invalid examples:**
```
service_productization  ❌  (underscores not allowed)
Service-Productization  ❌  (hyphens not allowed)
2ndOffering         ❌  (starts with digit)
true                ❌  (reserved word)
```

---

## 4. Field Name Rules

| Rule | Detail |
|---|---|
| Case | camelCase — start with lowercase |
| Pattern | `[a-z][A-Za-z0-9]*` |
| Uniqueness | Unique within an entity block |

**Valid:**
```
targets       ✅
performedBy   ✅
avgDealSize   ✅
```

**Invalid:**
```
Targets       ❌  (uppercase start)
performed_by  ❌  (underscore)
avg-deal-size ❌  (hyphen)
```

---

## 5. Value Types

### 5.1 String

Quoted with double quotes. Single quotes are not supported.

```csl
description: "This is a string value"
name: "Acme Consulting"
```

Escape characters inside strings:
- `\"` — literal double quote
- `\\` — literal backslash
- `\n` — newline

---

### 5.2 Number

Integers and decimals, no quotes.

```csl
basePrice: 12900
targetMargin: 0.65
avgDealSize: 24900
duration: 30
```

Negative numbers:
```csl
costDelta: -5000
```

---

### 5.3 Boolean

Lowercase `true` or `false`, no quotes.

```csl
delegatable: true
differentiator: false
referralDriven: true
```

---

### 5.4 Entity Reference

A bare identifier pointing to another entity. No quotes.

```csl
ownedBy: StrategyTeam
performedBy: PrincipalConsultant
partOf: ClientOnboarding
```

The referenced entity must be declared somewhere in the model (same file or imported file).

---

### 5.5 List

Square brackets, comma-separated. Items can be entity references, strings, or numbers.

```csl
// List of entity references
targets: [FounderLedAgencies, SolopreneurConsultants]

// List of strings
problems: ["Stuck in hourly billing", "Cannot scale without founder"]

// List of numbers
revenueRange: [500000, 5000000]

// Mixed strings (objects in a list use object syntax)
countries: ["DE", "UK", "FR", "NL"]
```

Trailing commas are allowed:
```csl
targets: [FounderLedAgencies, SolopreneurConsultants,]
```

---

### 5.6 Object (Inline Block)

Curly braces with key-value pairs.

```csl
economics: {
  avgDealSize: 24900
  avgDeliveryHours: 120
  targetMargin: 0.65
}
```

Objects can be nested:
```csl
target: {
  metric: "MRR"
  value: 85000
  unit: "EUR"
  timeframe: "6 months"
}
```

---

### 5.7 List of Objects

Used for phases in journeys, add-ons in pricing, etc.

```csl
phases: [
  {
    name: "Awareness"
    duration: 7
    clientState: "Recognizes scaling problem"
  },
  {
    name: "Evaluation"
    duration: 14
    clientState: "Evaluating fit and ROI"
  }
]
```

---

## 6. Relationship Attributes (`with` syntax)

Entity references in list fields can carry inline attribute objects.

### Form 1: Per-entity attributes on a list

```csl
targets: [SegmentA, SegmentB] with {
  SegmentA: { priority: primary, fitScore: 0.95 }
  SegmentB: { priority: secondary, fitScore: 0.75 }
}
```

### Form 2: Per-item attribute on a single reference

```csl
requires: [
  ServiceDesign with { proficiency: expert, criticality: high },
  ProcessMapping with { proficiency: intermediate, criticality: medium }
]
```

### Form 3: Single reference with attribute

```csl
achievedThrough: [
  ServiceProductization with { impact: 0.70 }
]
```

---

## 7. Comments

### Single-line

```csl
// This is a single-line comment
description: "Some description" // inline comment
```

### Multi-line

```csl
/*
  This is a multi-line comment.
  Use it for documentation blocks.
*/
offering ServiceProductization {
  ...
}
```

---

## 8. Imports

To split a large model across files:

```csl
import "./segments.csl"
import "./capabilities.csl"
import "./processes.csl"
```

- Path is relative to the current file
- Circular imports are not allowed
- All entities referenced in the main file must be declared in the imported file or another already-imported file

---

## 9. Inline Entity Definitions

For simple entities used in only one place, they can be defined inline:

```csl
capability ServiceDesign {
  ownedBy: inline team MicroTeam {
    description: "Small focused group"
    roles: [Designer]
  }
}
```

Inline entities are not referenceable from other entities. Use only for nested, non-shared entities.

---

## 9. File-Level Metadata

A CSL file can start with an optional metadata comment block before any entity declarations:

```csl
// version: 1.2
// author: Jane Smith
// description: AS-IS model for Veloxa HR Tech
// state: as-is        // as-is | to-be | target
// date: 2025-03-01
```

These are freeform `//` comments — they are not parsed as structured fields but are preserved by tooling and visible to agents.

For AS-IS / TO-BE models, each entity can carry a `changeType` annotation as a direct field:

```csl
capability WorkflowAutomation {
  changeType: "new"     // new | enhanced | retired
  description: "..."
  ownedBy: TechTeam
  maturity: { current: "basic" }
}
```

---

## 10. Complete Entity Syntax Reference

### company
```csl
company EntityName {
  name: "string"                      // required
  description: "string"               // required
  industry: "string"                  // required (e.g. "Professional Services", "SaaS")
  size: "startup"                     // required: startup | scale-up | mid-market | enterprise
  stage: "growth"                     // required: idea | pre-revenue | growth | established | mature
  headquarters: "City, Country"
  founded: number
  markets: [market refs]
  offerings: [offering refs]
  objectives: [objective refs]
  caseStudies: [caseStudy refs]
  voice: {
    tone: "string"
    formality: "semi-formal"          // formal | semi-formal | conversational
    perspective: "we"                 // we | third-person
    language: "en"                    // pl | en | both
    dos: ["...", "..."]
    donts: ["...", "..."]
    examplePhrases: ["..."]
  }
  meta: { ... }
  status: "draft|validated|active|deprecated"
  doc: "path/to/doc.md"
}
```

### offering
```csl
offering EntityName {
  description: "string"               // required
  targets: [segment refs] with { ... }    // required (≥1)
  operatesIn: [market refs]
  requires: [capability refs with { proficiency, criticality }]  // required (≥1)
  delivers: [outcome refs]                // required (≥1)
  measuredBy: [metric refs]
  economics: {
    avgDealSize: number                   // required
    avgDeliveryHours: number
    targetMargin: number                  // required (0–1)
    clientLifetimeValue: number
  }
  performance: {
    conversionRate: number
    avgSalesCycle: number
    clientRetention: number
    referralRate: number
  }
  meta: { ... }
  status: "..."
  doc: "..."
}
```

### segment
```csl
segment EntityName {
  description: "string"               // required
  size: number                        // required: total number of companies or people
  operatesIn: market ref              // required: market this segment belongs to
  characteristics: {
    industry: "string"
    revenueRange: [min, max]
    teamSize: [min, max]
    businessAge: [min, max]
    geography: ["string list"]
  }
  problems: ["string list"]
  motivations: ["string list"]
  buyingBehavior: {
    decisionMaker: "string"
    avgDecisionTime: number
    priceSensitivity: "low|medium|high"
    referralDriven: boolean
  }
  meta: { ... }
}
```

### market
```csl
market EntityName {
  description: "string"
  type: "geographic|industry|niche"
  region: "string"                    // required
  countries: ["string list"]
  size: number                        // plain TAM number, OR use nested form:
  // size: {
  //   estimatedCompanies: number
  //   addressableMarket: number
  // }
  characteristics: {
    maturity: "string"
    competition: "string"
    regulation: "string"
  }
  meta: { ... }
}
```

### outcome
```csl
outcome EntityName {
  description: "string"               // required
  type: "revenue_increase|cost_reduction|time_saving|risk_mitigation|capacity_expansion|quality_improvement|customer_satisfaction"
  // Short aliases also accepted: financial | efficiency | growth | risk
  measuredBy: [metric refs]           // required (≥1)
  baseline: { metric: "string", value: number, unit: "string" }
  target: { metric: "string", value: number, unit: "string", timeframe: "string" }
  economicValue: {
    annualRevenue: number
    costReduction: number
    timeSaving: number
    riskMitigation: number
    capacityExpansion: number
  }
  clientState: { before: "string", after: "string" }
  meta: { ... }
}
```

### capability
```csl
capability EntityName {
  description: "string"               // required
  ownedBy: team ref                   // required
  dependsOn: [capability refs]
  maturity: { current: "basic|intermediate|advanced|expert", target: "..." }  // current required
  resources: {
    toolsUsed: [system refs]
    peopleRequired: number
    avgTimePerExecution: number
  }
  criticality: "low|medium|high|critical"
  differentiator: boolean
  meta: { ... }
}
```

### process
```csl
process EntityName {
  description: "string"               // required
  performedBy: team or role ref       // required
  measuredBy: metric ref              // required
  uses: [system refs]
  steps: [step refs]                  // required (≥1)
  metrics: {
    avgDuration: number
    successRate: number
    clientSatisfaction: number
  }
  automation: {
    level: "none|partial|full"
    automated: ["string list"]
    manual: ["string list"]
  }
  meta: { ... }
}
```

### step
```csl
step EntityName {
  description: "string"               // required
  partOf: process ref                 // required
  performedBy: team or role ref       // required
  order: number                       // required (1-based sequence position)
  duration: number
  estimatedEffort: number
  dependsOn: [step refs]
  inputs: ["string list"]
  outputs: ["string list"]
  deliverables: ["string list"]
  uses: [system refs]
  successCriteria: ["string list"]
  delegatable: boolean
  automationPotential: "low|medium|high"
  meta: { ... }
}
```

### package
```csl
package EntityName {
  description: "string"
  offering: offering ref              // required
  tier: "entry|standard|premium|enterprise"
  position: number
  includes: ["string list"]
  excludes: ["string list"]
  pricing: {
    model: "fixed_project|monthly_retainer|value_based|tiered_subscription|usage_based|hybrid"
    basePrice: number                 // required
    currency: "string"
    paymentTerms: "string"
  }
  delivery: {
    duration: number
    format: "remote|onsite|hybrid"
    meetings: number
    async_work: boolean
  }
  boundaries: {
    maxRevisions: number
    responseTime: "string"
    scope: "string"
  }
  targets: [segment refs]
  meta: { ... }
}
```

### team
```csl
team EntityName {
  description: "string"               // required
  size: number                        // required: plain number, OR nested:
  // size: { current: number, target: number }
  roles: [role refs]
  capacity: { billableHours: number, utilization: number }
  structure: { leadRole: role ref, reportingTo: "string" }
  meta: { ... }
}
```

### role
```csl
role EntityName {
  description: "string"
  responsibilities: ["string list"]
  capabilities: [capability refs with { level: "..." }]
  compensation: { type: "string", range: [min, max] }
  meta: { ... }
}
```

### system
```csl
system EntityName {
  description: "string"               // required
  type: "saas|internal|infrastructure|custom|external"  // required
  vendor: "string"
  cost: { monthly: number, annual: number }
  integration: { connectedTo: [system refs], apiAvailable: boolean }
  meta: { ... }
}
```

### objective
```csl
objective EntityName {
  description: "string"               // required
  timeframe: "FY2025"                 // required (e.g. "FY2025", "Q1–Q4 2025")
  type: "financial|operational|strategic|customer"
  target: {
    metric: "string"
    current: number
    target: number
    deadline: "YYYY-MM-DD"
  }
  measuredBy: [metric refs]           // required (≥1)
  achievedThrough: [offering refs]    // required (≥1) — replaces the deprecated contributedBy
  meta: { ... }
}
```

### metric
```csl
// Canonical flat form (recommended):
metric EntityName {
  description: "string"               // required
  unit: "string"                      // required (e.g. "EUR", "%", "days")
  target: number                      // required
  baseline: number                    // required
  frequency: "monthly"                // required (daily|weekly|monthly|quarterly|per-hire|...)
  type: "financial|operational|customer|quality|growth"
  calculation: "string"
  meta: { ... }
}

// Nested alternative form (also valid, for richer data):
metric EntityName {
  description: "string"
  unit: "string"
  type: "financial|operational|customer|quality|growth"
  calculation: "string"
  targets: { current: number, q1: number, q2: number, q3: number, q4: number }
  measurement: { frequency: "string", source: "string", owner: "string" }
  meta: { ... }
}
```

### pricingModel
```csl
pricingModel EntityName {
  type: "fixed_project|monthly_retainer|value_based|tiered_subscription|usage_based|hybrid"
  description: "string"
  calculation: { basis: "string", methodology: "string", valueCapture: number }
  structure: {
    basePrice: number
    addOns: [{ name: "string", price: number }]
  }
  terms: { payment: "string", refundPolicy: "string", priceAdjustment: "string" }
  meta: { ... }
}
```

### journey
```csl
journey EntityName {
  targets: [segment refs]            // who this journey is for (≥1 recommended)
  offering: offering ref
  stages: [                          // use 'stages' (not 'phases')
    {
      name: "string"                 // required per stage
      goal: "string"
      touchpoints: ["string list"]
      duration: number
      clientState: "string"
      conversionBarriers: [{ barrier: "string", mitigation: "string" }]
      exitCriteria: "string"
      successCriteria: ["string list"]
    }
  ]
  metrics: {
    awarenessToEval: number
    evalToClose: number
    overallConversion: number
    avgTimeToClose: number
  }
  meta: { ... }
}
```

---

## 11. Relationship Field Restrictions

Every reference field has a fixed set of **allowed source entity types** and a fixed **target entity type**. Using a reference field on the wrong entity type is a hard error (E215–E221).

| Field | Allowed on | Points to | ❌ Common mistake |
|---|---|---|---|
| `targets` | `offering` | `segment` | `process.targets`, `capability.targets` |
| `operatesIn` | `offering` | `market` | `capability.operatesIn`, `process.operatesIn` |
| `delivers` | `offering` | `outcome` | `process.delivers`, `capability.delivers` |
| `requires` | `offering` | `capability` | **`process.requires` ← very common error** |
| `ownedBy` | `capability` | `team` | `process.ownedBy`, `offering.ownedBy` |
| `dependsOn` | `capability` → `capability`; `step` → `step` | capability / step | mixing source or target types |
| `achievedThrough` | `objective` | `offering` | **`outcome.achievedThrough` ← deprecated; `offering.achievedThrough` ← invalid** |
| `measuredBy` | `offering`, `objective`, `outcome`, `process` | `metric` | `capability.measuredBy` |
| `performedBy` | `process`, `step` | `team` / `role` | `capability.performedBy`, `offering.performedBy` |
| `uses` | `process`, `step` | `system` | `capability.uses`, `offering.uses` |
| `partOf` | `step` | `process` | `capability.partOf`, `offering.partOf` |

### Key Rules to Memorise

- **`requires` is offering-only.** A `process` cannot declare `requires`. To express that a process depends on a capability, ensure the offering declares `offering.requires: [CapabilityName]`.
- **`achievedThrough` is objective-only.** An `outcome` cannot declare `achievedThrough`. The canonical direction is `offering.delivers: [OutcomeName]`.
- **`ownedBy` is capability-only.** Do not use `team.owns` — use `capability.ownedBy: TeamName`.
- **`measuredBy` is valid on `process`.** `process.measuredBy: MetricName` is explicitly allowed and required.
- **No reverse relationship fields on `system`.** Do not add `system.usedBy` or `system.supports`. Reference systems from `process.uses` and `step.uses` instead.
- **`contributesTo` is removed.** Do not use `offering.contributesTo` or `process.contributesTo`. Link objectives via `objective.achievedThrough: [OfferingName]`.
