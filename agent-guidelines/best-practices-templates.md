# Best Practices & Templates

Guidelines for quality CSL modeling and reusable templates for common patterns.

---

## 1. Modeling Best Practices

### 1.1 Start with the Core, Expand Later

Begin every model with the minimum viable set:
1. One `company`
2. One or two core `offering` entities
3. Two or three `segment` entities
4. Key `capability` entities (3–5)
5. One `team` per capability cluster
6. Packages for each offering

Expand to processes, steps, journeys, metrics, and objectives in a second pass.

---

### 1.2 Always Trace Value

Every offering must connect to an outcome, which must connect to economic value. Without this chain, the model is structurally incomplete.

```
offering → delivers → outcome → economicValue
```

Always fill in `outcome.economicValue` — even rough estimates are better than nothing. A model with estimates (marked `confidence: "low"`) is more useful than one with gaps.

---

### 1.3 Model Reality, Not Aspirations

The AS-IS model should reflect current state honestly:
- Mark capabilities as they are today, not how they should be
- Use real performance numbers if available; use `confidence: "low"` if estimated
- Note gaps explicitly with `meta.notes` rather than omitting them

Use the TO-BE model for aspirations.

---

### 1.4 Use Confidence Levels

Every entity supports `meta.confidence`. Use it:

| Level | When to use |
|---|---|
| `high` | Confirmed by documentary evidence or stakeholder sign-off |
| `medium` | Based on credible inference or single source |
| `low` | Assumption, estimate, or needs verification |

---

### 1.5 Keep Names Precise

| ❌ Vague | ✅ Precise |
|---|---|
| `Onboarding` | `ClientOnboardingProcess` |
| `Service` | `ServiceProductization` |
| `Analysis` | `MarketFitAnalysis` |
| `Team1` | `StrategyTeam` |

Use names that would be unambiguous to someone reading the model months later.

---

### 1.6 Consistent Units

Pick a currency for the entire model and stick to it. Do the same for time units.

| Measurement | Convention |
|---|---|
| Money | EUR or USD (set in `pricing.currency`) |
| Duration (process/step) | Days for processes, minutes for steps |
| Effort (step) | Hours |
| Rates | Decimals: `0.65` not `65%` |
| Scores | 0–1 range |

---

### 1.7 Version Control Strategy

- Store `.csl` files in Git
- One commit per meaningful model change
- Use branch names like `asis-v1`, `tobe-v1`, `tobe-v2`
- Tag stable model versions: `git tag asis-v1.0`

---

## 2. Naming Convention Templates

| Entity | Pattern | Example |
|---|---|---|
| company | `CompanyName` | `AcmeConsulting` |
| offering | `[Adjective]ServiceName` or `[Verb]Service` | `ServiceProductization`, `StrategyAdvisory` |
| segment | `[Descriptor]CustomerType` | `FounderLedAgencies`, `MidMarketSaaS` |
| market | `[Geography]` or `[Industry]Market` | `Europe`, `B2BSoftwareMarket` |
| outcome | `[AdjOrVerb]Result` | `RevenueGrowth`, `ReducedFounderDependency` |
| capability | `[Noun]Skill` or `[Verb]Capability` | `ServiceDesign`, `PricingStrategy` |
| process | `[Purpose]Process` or `[Action]` | `ClientOnboarding`, `ProposalDevelopment` |
| step | `[Action][Object]` | `KickoffWorkshop`, `DiscoveryPreparation` |
| team | `[Function]Team` | `StrategyTeam`, `ClientSuccessTeam` |
| role | `[Seniority][Function]` | `PrincipalConsultant`, `SeniorAnalyst` |
| package | `[Tier]Package` or `[Name]Package` | `FoundationPackage`, `AgencyPackage` |
| system | `[ToolName]` or `[Category]` | `CRM`, `ProjectManagement`, `Miro` |
| objective | `[Verb][Metric/Goal]` | `GrowARR`, `ImproveMargins`, `ReduceChurn` |
| metric | `[MetricName]` | `ARR`, `MRR`, `ChurnRate`, `PackageConversionRate` |

---

## 3. Templates

### 3.1 New Offering Template

Use when adding any new service or product to the model.

```csl
offering NewOfferingName {
  description: "What this offering does and who it is for"

  targets: [TargetSegment] with {
    TargetSegment: { priority: primary, fitScore: 0.80 }
  }

  operatesIn: [MarketName]

  requires: [
    RequiredCapability1 with { proficiency: advanced, criticality: high },
    RequiredCapability2 with { proficiency: intermediate, criticality: medium }
  ]

  delivers: [PrimaryOutcome]

  economics: {
    avgDealSize: 0             // TODO: fill in
    avgDeliveryHours: 0        // TODO: fill in
    targetMargin: 0.60
    clientLifetimeValue: 0     // TODO: fill in
  }

  performance: {
    conversionRate: 0.30
    avgSalesCycle: 14
    clientRetention: 0.80
  }

  packages: [StarterPackage, ProPackage]

  meta: { confidence: "medium", source: "assumption" }
  status: "draft"
}
```

---

### 3.2 Tiered Package Structure (3-tier)

Standard entry/standard/premium tier structure for any offering.

```csl
package StarterPackage {
  offering: NewOfferingName
  tier: "entry"
  position: 1

  description: "Core features, ideal for getting started"

  includes: [CoreFeatureA, CoreFeatureB]
  excludes: [AdvancedFeatureA, PremiumSupport]

  pricing: {
    model: "monthly_retainer"       // or fixed_project, value_based
    basePrice: 1500
    currency: "EUR"
    paymentTerms: "Monthly, cancel anytime"
  }

  delivery: {
    duration: 30
    format: "remote"
    meetings: 2
  }

  boundaries: {
    maxRevisions: 2
    responseTime: "48 hours"
    scope: "Single primary use case"
  }

  targets: [TargetSegment]
}

package ProPackage {
  offering: NewOfferingName
  tier: "standard"
  position: 2

  description: "Full feature set for growing teams"

  includes: [CoreFeatureA, CoreFeatureB, AdvancedFeatureA]
  excludes: [EnterpriseFeatureA]

  pricing: {
    model: "monthly_retainer"
    basePrice: 3500
    currency: "EUR"
  }

  delivery: {
    duration: 30
    format: "remote"
    meetings: 4
  }

  boundaries: {
    maxRevisions: 3
    responseTime: "24 hours"
  }

  targets: [TargetSegment]
}

package EnterprisePackage {
  offering: NewOfferingName
  tier: "premium"
  position: 3

  description: "Full access, priority support, custom scope"

  includes: [CoreFeatureA, CoreFeatureB, AdvancedFeatureA, EnterpriseFeatureA, PremiumSupport]

  pricing: {
    model: "custom"
    basePrice: 8500
    currency: "EUR"
    paymentTerms: "Annual contract, quarterly invoicing"
  }

  delivery: {
    duration: 30
    format: "hybrid"
    meetings: 8
    async_work: true
  }

  boundaries: {
    responseTime: "4 hours"
    scope: "Unlimited within agreed framework"
  }

  targets: [TargetSegment]
}
```

---

### 3.3 Process with Step Dependencies

Standard sequential-with-branching process template.

```csl
process CoreDeliveryProcess {
  description: "Main delivery workflow for [offering name]"

  performedBy: DeliveryTeam

  uses: [ProjectManagement, CRM]

  supports: [YourOffering]

  steps: [
    Step1Discovery,
    Step2Analysis,
    Step3DesignA,
    Step3DesignB,
    Step4Delivery,
    Step5Review
  ]

  metrics: {
    avgDuration: 21
    successRate: 0.90
    clientSatisfaction: 4.5
  }

  automation: {
    level: "partial"
    automated: ["Step1Discovery"]
    manual: ["Step2Analysis", "Step3DesignA", "Step4Delivery", "Step5Review"]
  }
}

step Step1Discovery {
  description: "Initial discovery and requirements capture"
  partOf: CoreDeliveryProcess
  performedBy: SeniorConsultant
  duration: 60
  estimatedEffort: 1
  delegatable: true
  automationPotential: "high"
}

step Step2Analysis {
  description: "Analyze findings and prepare recommendations"
  partOf: CoreDeliveryProcess
  performedBy: SeniorConsultant
  duration: 240
  estimatedEffort: 4
  dependsOn: [Step1Discovery]
  delegatable: false
}

step Step3DesignA {
  description: "Design solution component A"
  partOf: CoreDeliveryProcess
  performedBy: DeliveryTeam
  duration: 480
  estimatedEffort: 8
  dependsOn: [Step2Analysis]
  delegatable: true
}

step Step3DesignB {
  description: "Design solution component B (parallel to A)"
  partOf: CoreDeliveryProcess
  performedBy: DeliveryTeam
  duration: 480
  estimatedEffort: 8
  dependsOn: [Step2Analysis]
  delegatable: true
}

step Step4Delivery {
  description: "Deliver and present solution to client"
  partOf: CoreDeliveryProcess
  performedBy: SeniorConsultant
  duration: 120
  estimatedEffort: 3
  dependsOn: [Step3DesignA, Step3DesignB]
  deliverables: ["Client-ready report", "Presentation deck"]
  delegatable: false
}

step Step5Review {
  description: "Internal quality review and client feedback collection"
  partOf: CoreDeliveryProcess
  performedBy: QualityTeam
  duration: 60
  estimatedEffort: 1
  dependsOn: [Step4Delivery]
  delegatable: true
}
```

---

### 3.4 Value Chain (Market → Revenue)

Full end-to-end value chain template.

```csl
market TargetMarket {
  type: "geographic"
  region: "EU"
  countries: ["DE", "UK", "FR"]
  size: {
    estimatedCompanies: 10000
    addressableMarket: 500000000
  }
}

segment CoreSegment {
  description: "Primary customer group"
  characteristics: {
    industry: "Professional Services"
    revenueRange: [500000, 5000000]
    teamSize: [5, 50]
  }
  problems: ["Problem A", "Problem B"]
  motivations: ["Motivation A", "Motivation B"]
  buyingBehavior: {
    decisionMaker: "CEO/Founder"
    avgDecisionTime: 14
    priceSensitivity: "medium"
    referralDriven: true
  }
}

outcome PrimaryOutcome {
  type: "revenue_increase"
  baseline: { metric: "MRR", value: 20000 }
  target: { metric: "MRR", value: 40000, timeframe: "6 months" }
  economicValue: {
    annualRevenue: 240000
    capacityExpansion: 2.0
  }
  clientState: {
    before: "Current pain state"
    after: "Desired transformed state"
  }
}

offering CoreOffering {
  targets: [CoreSegment] with {
    CoreSegment: { priority: primary, fitScore: 0.88 }
  }
  operatesIn: [TargetMarket]
  delivers: [PrimaryOutcome]
  requires: [CoreCapability]
  economics: {
    avgDealSize: 15000
    targetMargin: 0.65
    clientLifetimeValue: 75000
  }
  performance: {
    conversionRate: 0.30
    avgSalesCycle: 21
    clientRetention: 0.80
  }
  packages: [EntryPackage, CorePackage]
}

objective GrowRevenue {
  type: "financial"
  target: {
    metric: "ARR"
    current: 300000
    target: 1000000
    deadline: "2026-12-31"
  }
  measuredBy: [ARR]
  contributedBy: [
    CoreOffering with { impact: 0.80 }
  ]
}

metric ARR {
  type: "financial"
  unit: "EUR"
  calculation: "SUM(mrr * 12)"
  targets: { current: 300000, q4: 1000000 }
  measurement: { frequency: "monthly", source: "CRM" }
}
```

---

### 3.5 Client Journey Template

Standard 4-phase buying journey.

```csl
journey BuyingJourney {
  for: [CoreSegment]
  offering: CoreOffering

  phases: [
    {
      name: "Awareness"
      duration: 7
      clientState: "Client recognizes the problem"
      touchpoints: [ContentChannel, ReferralNetwork]
      keyQuestions: [
        "Can this be solved?",
        "Who solves this?"
      ]
      content: [CaseStudies, ProblemFramework]
    },
    {
      name: "Evaluation"
      duration: 14
      clientState: "Comparing options and building confidence"
      touchpoints: [DiscoveryCall, ProposalReview, ReferenceCheck]
      processes: [InitialDiscovery, ProposalDevelopment]
      conversionBarriers: [
        { barrier: "Price objection", mitigation: "Show ROI calculation clearly" },
        { barrier: "Time concern", mitigation: "Offer fast-start option" }
      ]
      exitCriteria: "Signed proposal or explicit no"
    },
    {
      name: "Purchase"
      duration: 7
      clientState: "Finalizing agreement"
      touchpoints: [ContractReview, Onboarding]
      processes: [ContractProcessing]
    },
    {
      name: "Onboarding"
      duration: 30
      clientState: "Getting started and achieving first value"
      processes: [CoreDeliveryProcess]
      successCriteria: [
        "First deliverable completed",
        "Client sees initial results"
      ]
    }
  ]

  metrics: {
    awarenessToEval: 0.15
    evalToClose: 0.30
    overallConversion: 0.045
    avgTimeToClose: 28
  }
}
```

---

### 3.6 AS-IS → TO-BE Capability Change

Template for documenting a capability transformation.

```csl
// In tobe/model.csl

capability ImprovedCapabilityName {
  description: "Enhanced version of the capability"
  ownedBy: ImprovedTeam

  maturity: {
    current: "intermediate"   // where you are at start of TO-BE plan
    target: "advanced"
  }

  resources: {
    toolsUsed: [NewToolA, NewToolB]
    peopleRequired: 2
    avgTimePerExecution: 8   // vs 40 in AS-IS
  }

  criticality: "high"
  differentiator: true

  changeType: "enhanced"
  changes: {
    from: {
      name: "OldCapabilityName"
      effort: 40
      maturity: "basic"
    }
    to: {
      name: "ImprovedCapabilityName"
      effort: 8
      maturity: "advanced"
    }
    rationale: "Explain why this change is happening"
    expectedImpact: "Quantify the expected improvement"
    riskLevel: "medium"
    riskMitigation: "How you will manage the risk"
  }
}
```

---

## 4. Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| One mega-offering with everything included | Unanalyzable, hard to price, hard to sell | Split into 3–5 focused offerings |
| Capabilities with no owning team | Cannot assign accountability | Always set `ownedBy` |
| Packages without pricing | Commercially incomplete | Always set `pricing.basePrice` |
| Outcomes without economic value | Model cannot be analyzed for ROI | Fill in at least one `economicValue` field |
| Steps with no `dependsOn` | Process flow is ambiguous | Chain steps explicitly |
| All entities with `confidence: "low"` | Model is unreliable for decisions | Re-validate with stakeholders before using for decisions |
| Vague descriptions | Model is uninterpretable | Use specific, concrete language |
| Orphan entities | Disconnected from graph | Every entity must relate to at least one other |
