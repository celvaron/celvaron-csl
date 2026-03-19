# CSL Complete Example

This is a fully worked CSL model for **Acme Consulting** — a strategy and operations advisory firm. It demonstrates all major entity types and relationship patterns.

---

## The Company

Acme Consulting is a Berlin-based advisory firm founded in 2018. It serves founder-led agencies and consulting firms in Europe and North America, helping them productize their services.

**Strategic objectives:**
- Grow ARR from €800k to €2M by end of 2026
- Improve gross margins from 55% to 70%
- Reduce founder dependency in delivery

---

## Full CSL Model

```csl
// ============================================
// ACME CONSULTING - AS-IS MODEL
// ============================================

company AcmeConsulting {
  name: "Acme Consulting"
  description: "Strategy and operations advisory for service businesses"
  headquarters: "Berlin, Germany"
  founded: 2018
  
  markets: [Europe, NorthAmerica]
  offerings: [ServiceProductization, StrategyAdvisory]
  objectives: [GrowARR, ImproveMargins, ReduceFounderTime]
}

// ============================================
// MARKETS & SEGMENTS
// ============================================

market Europe {
  type: "geographic"
  region: "EU"
  countries: ["DE", "UK", "FR", "NL"]
  
  size: {
    estimatedCompanies: 45000
    addressableMarket: 2300000000
  }
}

segment FounderLedAgencies {
  description: "Marketing agencies with founder-led delivery model"
  
  characteristics: {
    industry: "Professional Services"
    revenueRange: [500000, 5000000]
    teamSize: [5, 50]
    geography: ["EU", "US"]
  }
  
  problems: [
    "Stuck in hourly billing",
    "Unable to scale without founder",
    "Inconsistent margins"
  ]
  
  buyingBehavior: {
    decisionMaker: "Founder/CEO"
    avgDecisionTime: 14
    pricesensitivity: "medium"
    referralDriven: true
  }
}

// ============================================
// OUTCOMES
// ============================================

outcome RevenueGrowth {
  description: "Increase MRR through packaged offerings"
  type: "revenue_increase"
  
  baseline: { metric: "MRR", value: 50000, unit: "EUR" }
  target: { metric: "MRR", value: 85000, timeframe: "6 months" }
  
  achievedThrough: [ServiceProductization]
  measuredBy: [MRR, CustomerLifetimeValue]
  
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

// ============================================
// OFFERINGS
// ============================================

offering ServiceProductization {
  description: "Transform custom services into packaged offerings"
  
  targets: [FounderLedAgencies] with {
    FounderLedAgencies: { priority: primary, fitScore: 0.95 }
  }
  
  operatesIn: [Europe, NorthAmerica]
  
  requires: [
    ServiceDesign with { proficiency: expert, criticality: high },
    PricingStrategy with { proficiency: advanced, criticality: high },
    ProcessMapping with { proficiency: intermediate, criticality: medium }
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

// ============================================
// PACKAGES & PRICING
// ============================================

package FoundationPackage {
  offering: ServiceProductization
  tier: "entry"
  position: 1
  
  description: "Core productization framework"
  
  includes: [
    OutcomeArchitecture,
    ProblemSolutionFit,
    MethodExtraction,
    BasicPackageDesign
  ]
  
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
  }
  
  boundaries: {
    maxRevisions: 2
    responseTime: "24 hours"
    scope: "Single core offering"
  }
  
  targets: [FounderLedAgencies]
}

package AgencyPackage {
  offering: ServiceProductization
  tier: "standard"
  position: 2
  
  pricing: {
    model: "fixed_project"
    basePrice: 24900
    currency: "EUR"
  }
  
  delivery: {
    duration: 45
    format: "hybrid"
    meetings: 8
  }
}

pricingModel FixedProject {
  type: "fixed_project"
  
  calculation: {
    basis: "value"
    methodology: "economic_impact"
    valueCapture: 0.15
  }
  
  terms: {
    payment: "milestone"
    refundPolicy: "satisfaction_guarantee"
  }
}

// ============================================
// CAPABILITIES
// ============================================

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

capability PricingStrategy {
  description: "Design value-based pricing models"
  ownedBy: StrategyTeam
  criticality: "high"
}

capability ProcessMapping {
  description: "Map and optimize operational processes"
  ownedBy: DeliveryTeam
  criticality: "medium"
}

// ============================================
// PROCESSES
// ============================================

process ClientOnboarding {
  description: "30-day structured onboarding"
  
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
}

// ============================================
// STEPS
// ============================================

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
    "Client articulates transformation",
    "Value quantified"
  ]
  
  delegatable: false
}

step DiscoveryPreparation {
  description: "Research and prep before kickoff"
  partOf: ClientOnboarding
  performedBy: Analyst
  duration: 240
  estimatedEffort: 4
  delegatable: true
}

step KickoffScheduling {
  description: "Schedule and confirm kickoff"
  partOf: ClientOnboarding
  performedBy: ClientSuccessManager
  duration: 30
  estimatedEffort: 0.5
  delegatable: true
}

// ============================================
// JOURNEY
// ============================================

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
    },
    {
      name: "Evaluation"
      duration: 14
      clientState: "Evaluating fit and ROI"
      touchpoints: [AuditCall, ProposalReview]
      processes: [InitialDiscovery]
      conversionBarriers: [
        { barrier: "Price concern", mitigation: "ROI demo" }
      ]
    },
    {
      name: "Onboarding"
      duration: 30
      processes: [ClientOnboarding]
      successCriteria: ["Framework completed"]
    }
  ]
  
  metrics: {
    awarenessToEval: 0.15
    evalToClose: 0.35
    overallConversion: 0.0525
  }
}

// ============================================
// TEAMS & ROLES
// ============================================

team StrategyTeam {
  description: "Core consulting delivery"
  
  roles: [PrincipalConsultant, SeniorConsultant]
  
  size: {
    current: 3
    target: 5
  }
  
  capacity: {
    billableHours: 120
    utilization: 0.75
  }
}

team ClientSuccessTeam {
  description: "Client relationship management"
  roles: [ClientSuccessManager]
  size: { current: 2, target: 3 }
}

team DeliveryTeam {
  description: "Operational execution"
  roles: [Analyst, ProjectManager]
  size: { current: 2, target: 4 }
}

role PrincipalConsultant {
  description: "Leads engagements"
  
  responsibilities: [
    "Client ownership",
    "Strategic guidance",
    "Quality assurance"
  ]
  
  capabilities: [
    ServiceDesign with { level: expert },
    PricingStrategy with { level: expert }
  ]
}

role ClientSuccessManager {
  description: "Manages client relationships"
  responsibilities: ["Onboarding", "Check-ins", "Renewals"]
}

// ============================================
// SYSTEMS
// ============================================

system CRM {
  description: "Customer relationship management"
  type: "saas"
  vendor: "HubSpot"
  
  cost: {
    monthly: 450
    annual: 5400
  }
}

system Miro {
  description: "Visual collaboration platform"
  type: "saas"
  cost: { monthly: 120 }
}

system ProjectManagement {
  description: "Project tracking"
  type: "saas"
  vendor: "Notion"
}

// ============================================
// OBJECTIVES & METRICS
// ============================================

objective GrowARR {
  description: "Grow annual recurring revenue"
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

objective ImproveMargins {
  description: "Increase gross margins"
  type: "financial"
  
  target: {
    metric: "GrossMargin"
    current: 0.55
    target: 0.70
  }
  
  measuredBy: [GrossMargin]
}

metric ARR {
  description: "Annual Recurring Revenue"
  type: "financial"
  unit: "EUR"
  
  calculation: "SUM(mrr * 12)"
  
  targets: {
    current: 800000
    q4: 2000000
  }
  
  measurement: {
    frequency: "monthly"
    source: "CRM"
  }
}

metric MRR {
  description: "Monthly Recurring Revenue"
  type: "financial"
  unit: "EUR"
  measurement: { frequency: "monthly" }
}

metric PackageConversionRate {
  description: "% of prospects who buy packages"
  type: "operational"
  unit: "percentage"
  
  targets: {
    current: 0.35
    target: 0.50
  }
}
```

---

## Generated Graph Model (excerpt)

After running `transform_csl.py`, the above produces a graph model like this:

```json
{
  "meta": {
    "modelVersion": "1.0",
    "cslVersion": "1.0",
    "companyId": "acme-consulting",
    "state": "asis",
    "snapshotDate": "2024-03-15T10:00:00Z"
  },
  "nodes": [
    {
      "id": "company:AcmeConsulting",
      "type": "company",
      "name": "AcmeConsulting",
      "attributes": {
        "name": "Acme Consulting",
        "headquarters": "Berlin, Germany",
        "founded": 2018
      }
    },
    {
      "id": "offering:ServiceProductization",
      "type": "offering",
      "name": "ServiceProductization",
      "attributes": {
        "economics": {
          "avgDealSize": 24900,
          "targetMargin": 0.65,
          "clientLifetimeValue": 180000
        }
      },
      "computed": {
        "centralityScore": 0.92,
        "impactScore": 0.88
      }
    },
    {
      "id": "segment:FounderLedAgencies",
      "type": "segment",
      "name": "FounderLedAgencies"
    },
    {
      "id": "capability:ServiceDesign",
      "type": "capability",
      "name": "ServiceDesign",
      "attributes": {
        "criticality": "high",
        "differentiator": true
      }
    }
  ],
  "edges": [
    {
      "from": "offering:ServiceProductization",
      "to": "segment:FounderLedAgencies",
      "type": "targets",
      "attributes": { "priority": "primary", "fitScore": 0.95 }
    },
    {
      "from": "offering:ServiceProductization",
      "to": "capability:ServiceDesign",
      "type": "requires",
      "attributes": { "proficiency": "expert", "criticality": "high" }
    },
    {
      "from": "capability:ServiceDesign",
      "to": "team:StrategyTeam",
      "type": "ownedBy"
    },
    {
      "from": "process:ClientOnboarding",
      "to": "step:KickoffWorkshop",
      "type": "hasStep",
      "attributes": { "order": 3, "required": true }
    }
  ]
}
```

---

## Try It

Run this example end-to-end (save the CSL above as `output/acme.csl`):

```bash
# Validate
python tools/validate_csl.py output/acme.csl

# Transform to graph
python tools/transform_csl.py output/acme.csl -o output/acme_graph.json

# Generate views
python tools/generate_diagram.py output/acme_graph.json --view architecture --title "Acme Consulting"
python tools/generate_diagram.py output/acme_graph.json --view capability-map --title "Acme Consulting"
python tools/generate_diagram.py output/acme_graph.json --view value-stream --title "Acme Consulting"
python tools/generate_diagram.py output/acme_graph.json --view package-architecture --title "Acme Consulting"
```

See [visualization.md](visualization.md) for all available views and when to use each.
