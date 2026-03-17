---
mode: agent
description: Export a TO-BE model as Quotera-ready company knowledge files. Usage — /export-company-profile MODEL_FILE COMPANY_SLUG
tools:
  - readFile
  - editFiles
---

Export a CSL TO-BE model as the five Markdown knowledge files consumed by [celvaron-quotera](https://github.com/celvaron/celvaron-quotera). From the user's message extract two arguments:

- **MODEL_FILE** — path to the `.csl` file (default: `examples/to_be_model.csl`)
- **COMPANY_SLUG** — lowercase slug for the company folder (e.g. `celvaron`, `veloxa`)

---

## Step 1 — Read the model

Read **MODEL_FILE** in full. Parse all entity blocks:

- `company` — name, description, industry, size, stage, headquarters, founded, website, voice block, caseStudies references
- `offering` — all active offerings (exclude changeType: "retired" / "removed"); record name, description, targets, delivers, changeType
- `capability` — all capabilities; note `differentiator: true` if present, maturityLevel, description
- `package` — tier, price, billingCycle, currency, features, partOf, description
- `pricingModel` — type, description
- `objective` — description, timeframe (first objective used as mission statement)
- `team` — size (used to compute total headcount)
- `system` — type, description
- `caseStudy` — client, industry, challenge, solution, outcome, technologies

If MODEL_FILE does not exist, stop and tell the user:
> Model file `{MODEL_FILE}` not found. Provide a valid path to a `.csl` file.

---

## Step 2 — Derive computed values

Before writing files, compute:

- **Total team size** — sum of `size` field across all `team` entities (use "not specified" if no teams have size)
- **Active offerings** — all offerings where changeType is NOT "retired" or "removed"
- **Retired offerings** — offerings where changeType is "retired" or "removed"
- **Differentiator capabilities** — capabilities with `differentiator: true`; if none exist, use all capabilities with `maturityLevel` of "optimised" or "expert" or "scaling"

---

## Step 3 — Write `exports/{COMPANY_SLUG}/knowledge/about.md`

```markdown
# About {company.name or COMPANY_SLUG}

## Company Overview
{company.description} — {company.industry if present}, {company.stage if present}.
Headquartered in {company.headquarters if present}. Founded {company.founded if present}.

## Mission
{first objective's description — or placeholder comment if no objectives}

## Key Facts
- **Founded:** {company.founded}
- **Team size:** {total team size computed above}
- **Headquarters:** {company.headquarters}
- **Website:** {company.website — omit line if not present}

## Core Differentiators
{one bullet per differentiator capability: "• {capability description}"}

## Technology & Approach
{one bullet per system entity: "• **{system name}** ({system.type}) — {system.description}"}
{if no systems: placeholder comment}
```

---

## Step 4 — Write `exports/{COMPANY_SLUG}/knowledge/services.md`

```markdown
# Services — {company.name or COMPANY_SLUG}

## Service Areas

{for each active offering:}
## {offering name}
{offering.description}

**Key outcomes:** {comma-separated list of outcome names from offering.delivers}
**Available tiers:** {comma-separated list of package names whose partOf references this offering}

## What We Don't Do
{one bullet per retired/removed offering: "• {offering name} — {offering.description}"}
{if no retired offerings: omit section entirely}
```

---

## Step 5 — Write `exports/{COMPANY_SLUG}/knowledge/pricing-guidelines.md`

```markdown
# Pricing Guidelines — {company.name or COMPANY_SLUG}

## Packages

| Package | Tier | Price | Billing | Currency |
|---------|------|-------|---------|----------|
{one row per package entity}

## Package Details

{for each package entity:}
### {package name} ({package.tier})
{package.description if present}

**Includes:**
{bullet list from package.features}

## Pricing Model
{for each pricingModel entity: "**{pricingModel name}** — {pricingModel.type}: {pricingModel.description}"}
{if no pricingModel entities: omit section}

## Notes for Agents
- Always express prices in {currency from first package, or "the company's primary currency"}
{any meta.notes from company or pricingModel entities that are relevant to pricing agents}
```

---

## Step 6 — Write `exports/{COMPANY_SLUG}/knowledge/tone-of-voice.md`

If `company.voice` block is present:

```markdown
# Tone of Voice — {company.name or COMPANY_SLUG}

## Overall Tone
{company.voice.tone}

## Voice Characteristics
- **Formality:** {company.voice.formality}
- **Perspective:** {company.voice.perspective}
- **Language:** {company.voice.language}

## Do
{bullet list from company.voice.dos}

## Don't
{bullet list from company.voice.donts}

## Example Phrases
{bullet list from company.voice.examplePhrases}
```

If `company.voice` block is **not present**, generate:

```markdown
# Tone of Voice — {company.name or COMPANY_SLUG}

## Overall Tone
<!-- Describe the overall writing style in 2–3 sentences. -->

## Voice Characteristics
- **Formality:** <!-- Formal / Semi-formal / Conversational -->
- **Perspective:** <!-- First person plural (we) / Third person -->
- **Language:** <!-- pl / en / both -->

## Do
<!-- Things the writing should do -->
-

## Don't
<!-- Things to avoid -->
-

## Example Phrases
<!-- A few short examples of the desired tone. -->
```

---

## Step 7 — Write `exports/{COMPANY_SLUG}/knowledge/case-studies.md`

If `caseStudy` entities are present:

```markdown
# Case Studies — {company.name or COMPANY_SLUG}

{for each caseStudy entity:}
## {caseStudy.client}
- **Industry:** {caseStudy.industry}
- **Challenge:** {caseStudy.challenge}
- **Solution:** {caseStudy.solution}
- **Outcome:** {caseStudy.outcome}
- **Technologies:** {caseStudy.technologies joined by ", "}
```

If **no** `caseStudy` entities are present, generate:

```markdown
# Case Studies — {company.name or COMPANY_SLUG}

<!-- Add one section per notable project. Agents use these to write the "Why {COMPANY}" section. -->

## {Client / Project Name}
- **Industry:**
- **Challenge:** <!-- What problem did the client face? -->
- **Solution:** <!-- What did the company build or deliver? -->
- **Outcome:** <!-- Measurable results, impact, or key success indicators. -->
- **Technologies:**
```

---

## Step 8 — Confirm

After writing all five files, tell the user:

> ✓ Company profile exported to `exports/{COMPANY_SLUG}/knowledge/`:
>
> - `about.md`
> - `services.md`
> - `pricing-guidelines.md`
> - `tone-of-voice.md`
> - `case-studies.md`
>
> **Next step:** Copy `exports/{COMPANY_SLUG}/knowledge/` into Quotera's `companies/{COMPANY_SLUG}/knowledge/`.
> Then run `/new-proposal CLIENTNAME PROJECTNAME {COMPANY_SLUG}` in Quotera to generate a proposal.

---

## Rules

- Never invent data not present in the model. Use placeholder comments for missing optional fields.
- Write only the 5 output files — no other files.
- Each output file must exactly match Quotera's `_template/knowledge/` structure so the proposal-writer agent can consume it without modification.
- If a field is a list of entity references (e.g. `delivers: [OutcomeA, OutcomeB]`), resolve to their names as plain strings — do not copy entity internal IDs.
- Do not include `changeType`, `meta`, `status`, `doc`, or other CSL model-management fields in any output file.
