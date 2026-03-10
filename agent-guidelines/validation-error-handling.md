# Validation & Error Handling

Rules for validating CSL models and strategies for handling errors and incomplete data.

---

## 1. Validation Layers

CSL validation runs in five layers, from most fundamental to most nuanced. Agents should run them in this order and stop at the first layer with blocking errors before proceeding.

| Layer | Type | Stops generation? |
|---|---|---|
| 1 | Syntax — can the file be parsed? | ✅ Yes (ERROR) |
| 2 | References — do all references resolve? | ✅ Yes (ERROR) |
| 3 | Structure — are cardinality and type rules met? | ✅ Yes (ERROR) |
| 4 | Semantics — does the business logic make sense? | ⚠️ Warning only |
| 5 | Completeness — is the model sufficiently detailed? | ⚠️ Warning only |

---

## 2. Layer 1: Syntax Validation

These are hard errors. A model with syntax errors cannot be processed further.

### 2.1 Naming Errors

| Rule | Error Code | Message |
|---|---|---|
| Entity name does not match `[A-Z][A-Za-z0-9]*` | E001 | `Entity name "{name}" is not valid PascalCase` |
| Entity name starts with a digit | E002 | `Entity name "{name}" must not start with a digit` |
| Entity name is a reserved keyword | E003 | `"{name}" is a reserved keyword and cannot be used as entity name` |
| Field name does not match `[a-z][A-Za-z0-9]*` | E004 | `Field name "{name}" is not valid camelCase` |
| Duplicate entity name within same entity type | E005 | `Duplicate {type} name: "{name}". Entity names must be unique within their type` |

### 2.2 Structural Parse Errors

| Rule | Error Code | Message |
|---|---|---|
| Unknown entity type keyword | E006 | `Unknown entity type: "{keyword}". Valid types are: company, offering, segment, ...` |
| Missing opening brace | E007 | `Expected "{" after entity declaration "{type} {name}"` |
| Missing closing brace | E008 | `Unclosed block for entity "{type} {name}"` |
| Invalid value type for field | E009 | `Field "{field}" expects {expectedType}, got {actualType}` |
| List syntax error | E010 | `Malformed list in field "{field}": {detail}` |
| Object syntax error | E011 | `Malformed object in field "{field}": {detail}` |

### 2.3 Handling Syntax Errors

When a syntax error is found:
1. Record the error with line number if available
2. Attempt to recover and continue parsing remaining entities (to surface all errors at once)
3. Do not produce a graph model output
4. Return the full error list to the user

---

## 3. Layer 2: Reference Validation

These are hard errors. All entity references in the model must resolve.

| Rule | Error Code | Message |
|---|---|---|
| Reference to undefined entity | E101 | `Undefined reference: "{Name}" in {sourceType}:{sourceName}.{field}. No {targetType} named "{Name}" found` |
| Reference to wrong entity type | E102 | `Type mismatch: {sourceType}:{sourceName}.{field} must reference a {expectedType}, but "{Name}" is a {actualType}` |
| Circular step dependency | E103 | `Circular dependency detected in step chain: {step1} → {step2} → ... → {step1}` |

### 3.1 Handling Reference Errors

The most common cause is referencing an entity before declaring it. CSL allows out-of-order declarations, so agents should do a two-pass parse:
1. **Pass 1:** Collect all entity names and types
2. **Pass 2:** Validate all references against the collected names

If a reference is unresolvable, flag it as E101 and suggest the closest declared entity name (fuzzy match by edit distance).

---

## 4. Layer 3: Structural Validation

These are hard errors based on cardinality and type rules.

### 4.1 Cardinality Rules

| Rule | Error Code | Message |
|---|---|---|
| More than one `company` entity | E201 | `Multiple company entities found. Exactly one company is allowed per model` |
| No `company` entity | E202 | `No company entity found. Every model must declare exactly one company` |
| `offering.targets` is empty | E203 | `{offering} must have at least one target segment` |
| `offering.requires` is empty | E204 | `{offering} must have at least one required capability` |
| `offering.delivers` is empty | E205 | `{offering} must deliver at least one outcome` |
| `capability.ownedBy` is missing | E206 | `{capability} must have exactly one owning team (ownedBy field required)` |
| `process.performedBy` is missing | E207 | `{process} must have a performedBy team or role` |
| `process.steps` is empty | E208 | `{process} must have at least one step` |
| `step.partOf` is missing | E209 | `{step} must declare the process it belongs to (partOf field required)` |
| `step.performedBy` is missing | E210 | `{step} must declare who performs it` |
| `package.offering` is missing | E211 | `{package} must reference the offering it packages` |
| `package.pricing` is missing or `pricing.basePrice` is missing | E212 | `{package} must have a pricing block with a basePrice` |
| Package `basePrice` ≤ 0 | E213 | `{package} basePrice must be greater than 0` |
| Duplicate package position in same offering | E214 | `Packages {pkg1} and {pkg2} in offering {offering} have the same position` |

### 4.2 Handling Structural Errors

These errors indicate incomplete modeling. When detected:
1. Flag explicitly with code and context
2. Where possible, suggest the fix (e.g., "Add at least one capability reference to `requires:`")
3. Do not produce partial graph model output

---

### 4.3 Relationship Type Restrictions

These are hard errors. Every reference field is only valid on specific source entity types. Using a field on the wrong entity type must be flagged immediately — these violations are not detectable as reference errors (E101/E102) and require a separate type-source check.

| Rule | Error Code | Message |
|---|---|---|
| `requires` used on any entity other than `offering` | E215 | `{type}:{name} uses 'requires' but only offering may declare requires. Did you mean capability.supports: [offering]?` |
| `contributesTo` used on any entity other than `offering` or `capability` | E216 | `{type}:{name} uses 'contributesTo' but only offering and capability may link to objectives. Move contributesTo to the relevant offering or capability.` |
| `targets` used on any entity other than `offering` | E217 | `{type}:{name} uses 'targets' but only offering may target segments` |
| `delivers` used on any entity other than `offering` | E218 | `{type}:{name} uses 'delivers' but only offering may deliver outcomes` |
| `ownedBy` used on any entity other than `capability` | E219 | `{type}:{name} uses 'ownedBy' but only capability may declare ownedBy. Use team.owns for the inverse.` |
| `achievedThrough` used on any entity other than `outcome` | E220 | `{type}:{name} uses 'achievedThrough' but only outcome may declare achievedThrough` |
| `partOf` used on any entity other than `step` | E221 | `{type}:{name} uses 'partOf' but only step may declare partOf` |

### 4.4 Handling Type Restriction Errors

When a type restriction error is found:
1. Flag with the appropriate code (E215–E221)
2. Identify the correct fix from the table in `syntax-structure.md` section 11
3. The most common pair to watch for: `process.requires` (→ E215) and `process.contributesTo` (→ E216)

---

## 5. Layer 4: Semantic Warnings

These are not blocking but indicate potential issues with the business model.

| Rule | Warning Code | Message |
|---|---|---|
| Offering has no packages | W001 | `{offering} has no packages defined. Clients cannot buy an offering without packages` |
| Offering has no performance metrics | W002 | `{offering} is missing a performance block. Without metrics, the model cannot be analyzed` |
| Offering margin is unusually low | W003 | `{offering}.economics.targetMargin = {value} is below 0.20. Verify this is intentional` |
| Offering margin is unusually high | W004 | `{offering}.economics.targetMargin = {value} exceeds 0.90. Verify this is correct` |
| Conversion rate is outside expected range | W005 | `{offering}.performance.conversionRate = {value} is outside 0.01–0.99. Check this value` |
| Capability has no supporting processes | W006 | `{capability} is not referenced by any process. How is this capability exercised?` |
| Process has no metrics | W007 | `{process} has no metrics block. Consider adding avgDuration and successRate` |
| Package has no target segments | W008 | `{package} has no targets field. Who is this package designed for?` |
| Journey phase has no conversion tracking | W009 | `Journey {journey} is missing conversion metrics` |
| Orphan entity (no edges) | W010 | `{type}:{name} is not referenced by any other entity. It may be disconnected from the model` |
| `process` uses `requires` field | W011 | `{process} declares requires, which is only valid on offering. To express that a process depends on a capability, ensure that capability declares supports: [OfferingName]` |
| `process` or `step` uses `contributesTo` field | W012 | `{type}:{name} declares contributesTo, which is only valid on offering and capability. Move contributesTo to the offering or capability that owns this objective link.` |

---

## 6. Layer 5: Completeness Checks

These surface gaps in model coverage.

| Check | Suggestion Code | Message |
|---|---|---|
| Fewer than 3 offerings | S001 | `Model has only {n} offering(s). A complete company model typically has 3+` |
| Fewer than 5 capabilities | S002 | `Model has only {n} capability(ies). Consider expanding capability coverage` |
| No journey entities | S003 | `No client journeys defined. Journeys help model buying behavior and conversion` |
| No metrics entities | S004 | `No metrics defined. Consider adding KPIs to measure business performance` |
| No objectives entities | S005 | `No objectives defined. Objectives link offerings to strategic goals` |
| No systems entities | S006 | `No systems defined. Systems document technology dependencies` |
| Some offerings have no economics data | S007 | `{offering} has no economics block. Add avgDealSize, targetMargin for analysis` |

---

## 7. Handling Incomplete Input Data

When an agent receives incomplete input data, use these strategies:

### 7.1 Missing Required Fields

If a required field cannot be inferred from input data:
1. Generate the entity with a placeholder comment
2. Mark it as `status: "draft"` and `meta.confidence: "low"`
3. Add a `meta.notes` explaining what is missing

```csl
offering WebConsulting {
  // TODO: targets — no segment data provided, please specify customer group
  targets: [UnknownSegment]
  // TODO: requires — no capability data provided
  requires: [UnknownCapability]
  delivers: [ImprovedVisibility]

  status: "draft"
  meta: {
    confidence: "low"
    notes: "Targets and capabilities must be defined before this model is complete"
  }
}
```

### 7.2 Missing Optional Fields

Do not generate fields for which there is no data. Omitting optional fields is valid.

### 7.3 Ambiguous or Inferred Data

When data exists but requires interpretation:
1. Generate the best-fit value
2. Set `meta.confidence: "medium"` or `"low"`
3. Note the inference in `meta.notes`

```csl
outcome RevenueGrowth {
  type: "revenue_increase"
  baseline: { metric: "MRR", value: 10000 }
  target: { metric: "MRR", value: 20000, timeframe: "6 months" }
  meta: {
    confidence: "medium"
    source: "assumption"
    notes: "Target value inferred from client statement 'double revenue'. Verify exact figures."
  }
}
```

### 7.4 Unknown/Unmappable Data

When input data has no clear CSL mapping:
1. Use `meta.notes` on the closest relevant entity
2. Do not create non-standard entity types
3. Document in a `// NOTE:` comment in the file

---

## 8. Validation Error Response Format

When validation is run programmatically, errors should be returned in this structure:

```json
{
  "valid": false,
  "errors": [
    {
      "code": "E101",
      "severity": "error",
      "entity": "offering:ServiceProductization",
      "field": "requires",
      "message": "Undefined reference: 'ServiceDesignCapability'. No capability named 'ServiceDesignCapability' found.",
      "suggestion": "Did you mean 'ServiceDesign'?"
    }
  ],
  "warnings": [
    {
      "code": "W001",
      "severity": "warning",
      "entity": "offering:StrategyAdvisory",
      "message": "StrategyAdvisory has no packages defined.",
      "suggestion": "Add at least one package to make this offering purchasable."
    }
  ],
  "suggestions": [
    {
      "code": "S001",
      "severity": "suggestion",
      "message": "Model has only 1 offering. A complete company model typically has 3+."
    }
  ]
}
```

---

## 9. Recovery Strategies for Agents

| Situation | Strategy |
|---|---|
| Reference not found | Try fuzzy name match → suggest closest match → generate with `// TODO` comment |
| Missing required field | Generate placeholder entity → set `status: "draft"` → note in `meta.notes` |
| Ambiguous data | Pick most likely interpretation → set `confidence: "low"` → note in `meta.notes` |
| Unknown entity type needed | Use closest standard type → annotate in comments |
| Model below minimum viable | Generate minimal extra scaffolding with `status: "draft"` to meet minimums |
| Conflicting data sources | Document conflict in `meta.notes`, use more authoritative source, flag for review |
