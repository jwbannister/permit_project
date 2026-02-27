# Success Criteria

## Purpose

This document defines what "success" means for the AI-assisted permitting tool at each level of evaluation. The tool is validated against a completed reference project (270-10-1: Work Force Hub), but success is not defined as reproducing that project — it is defined as building a generalizable system that *happens to* produce correct outputs for the reference case.

## Distinction: Reproduction vs. Generalization

The reference project (270-10-1) serves as a test suite, not a product specification. A system that can only reproduce 270-10-1 by hardcoding its specific inputs and outputs has failed. A system that applies general permitting logic and arrives at the same outputs has succeeded.

This distinction matters at every level of evaluation:

| Approach | Example | Verdict |
|----------|---------|---------|
| Hardcoded lookup | "If source is S2.002, PM factor = 0.3" | Failure — not generalizable |
| Rule-based selection | "If diesel engine, kW < 560, Tier 3 → PM = 0.3 g/bkW-hr per 40 CFR 60 Table 4" | Success — same answer, general method |
| Correct method, different result | Selects correct regulatory tier but uses updated factor table → PM = 0.28 | Qualified success — method is right, reference may be outdated |

## Three Tiers of Success

### Tier 1: Calculation Correctness

The engineering floor. Numeric outputs match reference values within defined tolerance.

**Applies to:** EI-POP, RESULTS, FORMS, COMPLY modules

**Criteria:**
- Emission rates (lb/hr, ton/yr) within 0.1% of reference values
- Stack parameters (velocity, flow rate, temperature) within 0.1%
- Unit conversions exact (these are deterministic arithmetic)
- PTE totals match reference Summary sheet

**How measured:** Cell-by-cell comparison of populated workbook against reference workbook. Automated validation script produces a pass/fail table for every active cell.

**Important:** Tolerance accounts for floating-point rounding, not for methodological differences. If a value is off by more than tolerance, the cause must be diagnosed — is it a rounding path difference (acceptable) or a wrong input/formula (failure)?

### Tier 2: Regulatory Equivalence

The professional standard. Outputs would pass regulatory review — correct methods applied, defensible factor selections, compliant documentation.

**Applies to:** All modules, but especially EI-POP (factor selection), DOC-GEN (regulatory narrative), AERMOD-RUN (modeling options)

**Criteria:**
- Emission factors selected from the correct regulatory source (NSPS standards where applicable, AP-42 as fallback, mass balance where required)
- Factor selection is traceable — every factor has a citation (regulation, table, row)
- Modeling options follow EPA regulatory defaults
- Compliance demonstration is arithmetically correct (modeled + background < NAAQS)
- Technical narrative makes no false regulatory claims

**How measured:** Human expert review of factor selections and regulatory citations. Comparison of method choices (not just numeric outputs) against reference project methodology. A qualified air quality professional should be able to sign the outputs.

**Why this matters:** Two different consultants working the same project might select slightly different AP-42 sub-tables or use different stack parameter assumptions and both be defensible. Exact numeric match with the reference is less important than regulatory defensibility. The tool must produce outputs a professional would endorse, not necessarily outputs identical to one specific professional's work.

### Tier 3: Generalizability

The real goal. The system handles new projects — different equipment types, different states, different permit classes — without modification to its core logic.

**Applies to:** The system as a whole

**Criteria:**
- Handles equipment types not in the reference project (e.g., natural gas turbines, coating operations, material handling)
- Handles different emission factor sources (state-specific factors, manufacturer test data)
- Handles different regulatory jurisdictions (different states have different permit forms, thresholds, and modeling requirements)
- Does not contain 270-10-1-specific logic in its core modules (project-specific configuration is acceptable; project-specific code is not)

**How measured:** Apply the system to a second permitting project with different characteristics. This is a future milestone — Tier 3 validation requires a second reference project, which we have not yet selected.

**Current status:** Not testable until the system works for 270-10-1. But design decisions should be evaluated against this tier during development. Every implementation choice should answer: "Would this work for a different project, or am I baking in assumptions specific to 270-10-1?"

## Module-Level Success Criteria

Each module has specific acceptance criteria tied to the tiers above:

| Module | Tier 1 (Calculation) | Tier 2 (Regulatory) | Tier 3 (Generalization) |
|--------|---------------------|---------------------|------------------------|
| EI-POP | Emission rates within 0.1% | Correct factor hierarchy applied, all factors cited | Handles diesel, propane, natural gas source types |
| AERMOD-RUN | INP files diff-match reference | Regulatory default options used | Handles different pollutant sets, receptor configurations |
| SITE-CHAR | Coordinates within 5m of reference | Receptor grid meets regulatory spacing requirements | Handles different site geometries and coordinate systems |
| RESULTS | Concentrations exact-match reference | Correct statistical processing per pollutant | Handles different NAAQS standards and background sources |
| FORMS | All form fields match reference | Forms are complete and submission-ready | Handles different state form templates |
| DOC-GEN | Data tables match reference | Regulatory claims are accurate and defensible | Handles different report structures and regulatory contexts |
| GIS-FIG | All data elements present and correctly located | Figures meet submission quality standards | Handles different projections, base maps, symbology |
| COMPLY | Permit conditions correctly extracted | All obligations tracked with correct deadlines | Handles different permit structures and condition formats |

## EI-POP Prototype: Specific Acceptance Criteria

For the first milestone (diesel fire pump S2.002, Proc sheet row 7):

**Pass:**
- All 7 pollutant emission rates (PM, PM10, PM2.5, CO, NOx, SO2, VOC) match reference within 0.1% for all time periods (lb/hr, lb/day, ton/yr)
- Stack parameters (exit temp, velocity, flow rate, diameter) match reference within 0.1%
- AERMOD model-ready emission rates (g/s) match reference within 0.1%
- Emission factors are selected by general rule (40 CFR Tier lookup by kW range + manufacture year), not hardcoded
- Factor provenance is logged — each factor traces to a specific regulation/table/row
- Excel template is populated without corrupting formulas or VBA

**Qualified pass:**
- Numeric outputs match but one or more factors required manual investigation to determine source (e.g., VOC = 1.5292 g/bkW-hr derivation still unclear)
- System flags uncertainty rather than guessing

**Fail:**
- Any emission rate off by more than 1% without explanation
- Factor selected from wrong regulatory source (e.g., using AP-42 generic when NSPS Tier standard applies)
- Excel template corrupted (broken formulas, lost VBA, shifted cells)
- System produces correct numbers through hardcoded values rather than general calculation logic

## Evolving This Document

These criteria will be refined as development progresses. Expected additions:
- Tier 3 validation plan once a second reference project is selected
- Performance criteria (execution time, token cost for AI-assisted steps)
- Iteration workflow criteria (how many review-revise cycles before convergence)
- Multi-source criteria (extending beyond single source to full 21-source workbook)
