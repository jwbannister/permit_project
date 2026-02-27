# Agent Design: Modular Architecture for AI-Assisted Permit Reproduction

## Purpose

This document defines the modular agent architecture for an AI-assisted air quality permitting tool. The goal is a generalizable system that can execute permitting projects end-to-end — not a script that reproduces one specific project. However, we validate the system by running it against a completed reference project (270-10-1: Work Force Hub) where both the inputs and correct outputs are known.

The architecture follows directly from the deliverable chain mapped in [04-deliverable-chain.md](04-deliverable-chain.md) and the time analysis in [03-time-analysis.md](03-time-analysis.md). Module boundaries align with the natural seams in the permitting workflow where data formats change or professional judgment is required.

## Design Principles

### 1. Modular, not monolithic

Each module is independently developed, tested, and validated. A module can fail or be downgraded to a lower automation level without affecting the rest of the pipeline. This means an honest assessment of AI capability — some modules may prove unsuitable for full automation, and that is a valid finding.

### 2. Automation spectrum, not binary

For every module, we evaluate three levels of AI involvement:

| Level | Description | Human Role |
|-------|-------------|------------|
| **Full automation** | AI completes the task end-to-end | Reviews output for correctness |
| **AI-assisted** | AI handles mechanical/tedious parts | Provides judgment at decision points |
| **AI-prepared** | AI gathers data, pre-populates, sets up workspace | Does the core work, but faster |

Even modules rated "low" for full automation may be excellent candidates for AI assistance. The goal is to find the highest-value role AI can play in each step.

### 3. Validate against known outputs

Each module is tested by feeding it the same inputs the human team used on 270-10-1 and comparing its outputs to the actual project deliverables. This is the only credible way to assess capability — not hypothetical reasoning about what AI "should" be able to do, but direct comparison against known-good work product.

### 4. Iterative by design, validated in single-pass

Real permitting projects are not linear pipelines. The reference project went through 5 modeling iterations over ~4 weeks — draft outputs were reviewed, errors found, inputs revised, and downstream work rerun. This is normal, not exceptional. The architecture must treat iteration as a first-class concern:

- **Modules produce draft outputs, not final outputs.** Every module's output is subject to review (human or automated QA) and revision. The interface is not just `execute()` — it is `execute() → review() → revise()`.
- **Upstream corrections propagate downstream.** When an emission factor is changed in Module 1, affected AERMOD inputs (Module 2), results (Module 4), forms (Module 5), and reports (Module 6) must be identifiable and re-generable. Modules track which upstream values they depend on.
- **Each module exposes a revision interface.** Beyond initial population, modules must support targeted updates — changing one source's emission factor without re-running the entire pipeline, or updating one pollutant's modeling scenario without regenerating all 45 INP files.
- **State is persistent and inspectable.** Between iterations, the system retains its current state (populated workbook, generated files, validation results) so that a reviewer can examine intermediate outputs, flag issues, and request targeted corrections.

For the 270-10-1 validation, we run the system in single-pass mode — inputs in, outputs out, compare to reference. But the system is designed so that when applied to a new project with unknown outputs, the review-revise cycle works naturally. The reference project tests the calculation engine; real-world use tests the iteration workflow.

## Module Overview

| # | Module | Description | Full Auto | AI-Assisted | Build Phase |
|---|--------|-------------|-----------|-------------|-------------|
| 1 | **EI-POP** | Emissions Inventory Population | Medium-High | High | A |
| 2 | **AERMOD-RUN** | Model Configuration & Execution | High | High | B |
| 3 | **SITE-CHAR** | Source & Site Characterization | Low-Medium | **Medium-High** | A |
| 4 | **RESULTS** | Results Processing & Compliance | High | High | B |
| 5 | **FORMS** | Merge Data & Form Generation | High | High | C |
| 6 | **DOC-GEN** | Technical Document Generation | Medium | **High** | C |
| 7 | **GIS-FIG** | GIS Figure Generation | Medium | **High** | C |
| 8 | **COMPLY** | Post-Permit Compliance Package | Medium-High | High | D |

**Bold** AI-Assisted ratings highlight modules where the assisted mode is significantly more viable than full automation — meaning the human-AI collaboration approach may be the practical target even if full automation is attempted first.

## Build Sequence

```
Phase A: EI-POP [1] + SITE-CHAR [3]       Foundation — source data and site geometry
Phase B: AERMOD-RUN [2] + RESULTS [4]      Modeling pipeline — dispersion runs and compliance
Phase C: FORMS [5] + DOC-GEN [6] + GIS-FIG [7]   Document production — forms, reports, maps
Phase D: COMPLY [8]                        Post-permit — compliance package from issued permit
```

Phases are sequential (B depends on A outputs, C on B, D on issued permit). Modules within a phase can be developed in parallel.

---

## Module 1: EI-POP — Emissions Inventory Population

### Scope

Populate the 14-sheet emissions inventory workbook (`LN WFH EmisInv_LnPwr_r1_NDEP.xlsm`) from client-provided equipment data and EPA reference factors. This is the foundational data engine — every downstream module reads from it.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Equipment specifications | Client datasheets | Manufacturer spec sheets in project files |
| Fuel types and consumption rates | Client operating parameters | Client data package |
| Operating hours (annual) | Client / regulatory assumptions | Proposal or client correspondence |
| Emission factors (hierarchical) | NSPS/CFR standards, AP-42, mass balance | 40 CFR 60 Subpart IIII (diesel Tier standards), AP-42 Chapters 1.5/3.3/3.4, fuel sulfur mass balance |
| GHG emission factors | 40 CFR Part 98 | EPA mandatory reporting rule |
| HAP speciation profiles | EPA speciation data | Diesel exhaust HAP fractions |
| Regulatory thresholds | Nevada Class II permit rules | NDEP guidance documents |

### Outputs

| Output | Reference File |
|--------|----------------|
| Populated EI workbook (all 14 sheets) | `00_EI/LN WFH EmisInv_LnPwr_r1_NDEP.xlsm` |
| Calculated emission rates (lb/hr, ton/yr) | Proc sheet, columns AK-EX |
| PTE determination | Summary sheet |
| Source parameters for AERMOD | Proc sheet, source ID columns |
| BPIPPRM building data | BPIP sheet |

### Full Automation Approach

AI reads client equipment data (PDFs, spreadsheets, emails), identifies each emission source, selects the correct emission factor from the applicable regulatory hierarchy, and populates every cell in the Proc sheet's 154 columns. It then propagates calculated values to HAP&GHG, Tanks, Summary, and other dependent sheets.

**Key challenge:** Emission factor selection follows a regulatory hierarchy, not a single lookup table. For equipment subject to New Source Performance Standards (NSPS), federal standards (e.g., 40 CFR 60 Subpart IIII Tier standards for diesel engines in g/bkW-hr) take precedence over generic AP-42 factors. Some pollutants use mass balance calculations (e.g., SO2 from fuel sulfur content). AP-42 serves as the fallback for pollutants not covered by NSPS or mass balance (e.g., VOC). The agent must determine which source applies for each pollutant on each piece of equipment — matching equipment type, manufacture date, power rating, and fuel to the correct regulatory tier and factor table.

**Feasibility:** Medium-High. The emission factor selection is well-documented in EPA guidance and the calculation formulas are deterministic. The 154-column Proc sheet is large but each column follows a repeatable pattern. The main risk is edge cases in factor selection.

### AI-Assisted Approach

AI pre-populates the workbook with its best emission factor selections and calculated values. Human reviews the factor choices (especially for non-standard equipment), corrects any mismatches, and validates the PTE determination. AI handles the mechanical column propagation.

**Value proposition:** The Proc sheet alone has 154 columns per source. Manual population involves looking up each factor, entering it, and verifying the downstream calculation. AI handling the lookup-and-populate cycle — even if a human reviews every factor choice — eliminates the most tedious part of the work.

### Module Form

Python script that:
1. Parses equipment data from client-provided documents
2. Queries an AP-42 factor database to select emission factors
3. Writes values into an Excel template using `openpyxl`
4. Propagates calculated fields through dependent sheets

### Validation Method

Compare AI-populated workbook cell-by-cell against the actual `_r1_NDEP` version. Key metrics:
- Emission factor selection accuracy (correct AP-42 table/row)
- Calculated emission rate accuracy (lb/hr, ton/yr per pollutant per source)
- PTE totals match

### Key Risks

- AP-42 factor selection for non-standard equipment (e.g., Tier 4 engines, LPG heaters with variable sizing)
- Interpreting client-provided data that may be incomplete or ambiguous
- The VBA macro on INPUT_05_linepwr sheet generates AERMOD files — reproducing that logic requires understanding the macro

---

## Module 2: AERMOD-RUN — Model Configuration & Execution

### Scope

Generate AERMOD input files from the emissions inventory data, execute dispersion model runs, and produce raw model output. This covers the complete modeling pipeline from INP file generation through batch execution.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Source parameters | EI workbook Proc sheet | From Module 1 output |
| Receptor grid coordinates | EI workbook RE_grid, RE_bndry sheets | From Module 1 output |
| Meteorological data | AERMET-processed .SFC and .PFL files | `Met Data/` directory (5 years: 2017-2021) |
| Building downwash parameters | BPIPPRM output | From Module 3 output |
| Terrain elevations | AERMAP-processed NED data | `Terrain/` directory |
| Modeling options | EPA regulatory defaults | AERMOD guidance |

### Outputs

| Output | Reference File |
|--------|----------------|
| 45 AERMOD .INP files | `AERMOD Files - it05/` subdirectories |
| 45 AERMOD .OUT files | Paired with each .INP |
| .PLT plot files | Concentration isopleths for GIS mapping |
| Batch execution scripts | `.bat` files for run automation |

### Full Automation Approach

AI generates the complete set of 45 INP files (9 pollutant/averaging scenarios x 5 met years) by reading source parameters from the EI workbook and formatting them into AERMOD's five-section syntax (CO, SO, RE, ME, OU). It then generates batch scripts and executes all runs.

**Key strength:** AERMOD input file syntax is rigid and well-documented. The INP file structure is mechanical — source definitions, receptor grids, met file paths, and output options follow a fixed template. The VBA macro that currently does this is essentially a format-and-write routine.

**Feasibility:** High. The transformation from EI data to INP files is deterministic. AERMOD execution is a black-box batch process. The main complexity is getting the file naming convention and directory structure right for the 9 scenarios.

### AI-Assisted Approach

Same as full automation — this module has minimal judgment requirements. The assisted mode would mainly apply if the INP file generation encounters unexpected source types or configurations not covered by the template.

### Module Form

Python script that:
1. Reads source parameters from the EI workbook (Module 1 output)
2. Generates INP files using AERMOD syntax templates
3. Creates batch execution scripts
4. Executes AERMOD runs (requires `aermod.exe` — Windows or Wine on macOS)
5. Validates run completion (checks for errors in .OUT files)

### Validation Method

- Diff AI-generated INP files against the actual `it05` INP files (section by section)
- Compare model output concentrations (should be identical given identical inputs)
- Verify all 45 runs complete without errors

### Key Risks

- AERMOD is a Windows executable — execution environment needs Wine or a Windows VM on macOS
- Meteorological data files must be in exact AERMET format with correct file paths
- The 5-iteration history in the reference project suggests modeling often requires debugging — the first run rarely works perfectly

---

## Module 3: SITE-CHAR — Source & Site Characterization

### Scope

Extract source coordinates, building footprints, receptor grid geometry, and terrain data from site plans and engineering drawings. This is the spatial foundation that feeds into the EI workbook, BPIPPRM, and GIS modules.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Site plan / layout drawing | Client-provided engineering drawings | PDF/CAD files in project folder |
| Property boundary survey | Surveyor data or client GIS | Boundary coordinates |
| Equipment location specifications | Client / site plan annotations | Source XY locations |
| Topographic data | USGS NED 1/3-arc-second | Via AERMAP processing |

### Outputs

| Output | Reference File |
|--------|----------------|
| Source coordinates (UTM Zone 11N) | EI workbook Sources sheet |
| Building footprint vertices and heights | EI workbook BPIP sheet |
| Receptor grid coordinates (boundary, near-field, far-field) | EI workbook RE_grid, RE_bndry sheets |
| BPIPPRM input file | `01-Permitting/Modeling/Setup/` |
| BPIPPRM output (36-direction building profiles) | Downwash parameters for AERMOD INP files |

### Full Automation Approach

AI reads site plan PDFs/CAD drawings, identifies building outlines and equipment locations, georeferences them to UTM coordinates, defines a receptor grid at appropriate spacing, and runs BPIPPRM to generate building downwash profiles.

**Key challenge:** Georeferencing engineering drawings is genuinely hard. Site plans may have inconsistent scales, partial coordinate references, or hand annotations. Extracting precise UTM coordinates from a PDF site plan requires interpretation that goes beyond OCR.

**Feasibility:** Low-Medium. While AI vision models can read site plans, the precision required for AERMOD source locations (meters matter for near-field concentrations) makes fully automated extraction risky without human verification.

### AI-Assisted Approach

AI proposes source coordinates and building footprints from site plan analysis, presents them on an interactive map for human review and correction, then formats all corrected data into the EI workbook sheets and BPIPPRM input files. Human corrects positions on a map interface rather than manually typing UTM coordinates.

**Value proposition:** In the reference project, GIS work and site characterization consumed 7+ hours across multiple staff members. The tedious part is not identifying where sources are (a human can see that on a site plan) — it is converting visual positions to UTM coordinates, defining receptor grids at correct spacing, formatting BPIP vertex tables, and ensuring spatial consistency across all downstream files. AI handles all the formatting and coordinate math; human provides the spatial judgment.

**Feasibility:** Medium-High. The human-in-the-loop eliminates the georeferencing risk while AI handles all downstream propagation.

### Module Form

Python script with optional map UI that:
1. Reads site plan images/PDFs and proposes source locations
2. Presents locations for human review (map interface or coordinate table)
3. Generates receptor grid at specified spacing around property boundary
4. Formats BPIP input and runs BPIPPRM
5. Writes all spatial data to EI workbook sheets

### Validation Method

- Compare AI-proposed coordinates against actual EI workbook Sources sheet values
- Compare receptor grid geometry against actual RE_grid and RE_bndry sheets
- Compare BPIPPRM output against actual building downwash parameters
- Tolerance: source locations within 5m, receptor grid structure matches

### Key Risks

- Site plan quality varies dramatically between projects — some are precise CAD drawings, others are annotated aerial photos
- Receptor grid design requires regulatory knowledge (boundary spacing, extent)
- Building footprint vertex ordering must be consistent for BPIPPRM

---

## Module 4: RESULTS — Results Processing & Compliance

### Scope

Read AERMOD output files, extract maximum concentrations, compare against NAAQS and significance thresholds, add background concentrations, and determine compliance for each pollutant/averaging period combination.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| AERMOD .PLT plot files | Model run outputs | From Module 2 output |
| AERMOD .OUT files | Model run outputs | From Module 2 output |
| NAAQS thresholds | EPA regulatory tables | Federal standards by pollutant/averaging period |
| Significance levels | EPA/NDEP guidance | Modeling significance thresholds |
| Background concentrations | NDEP-provided or EPA monitoring data | Ambient monitoring records |

### Outputs

| Output | Reference File |
|--------|----------------|
| Maximum modeled concentrations (by pollutant/period) | Grab_Plots workbook summary tables |
| Compliance determination (project + background vs. NAAQS) | Grab_Plots workbook |
| Summary tables formatted for impact report | Tables used in Module 6 |
| Data for GIS impact maps | Concentration data for Module 7 |

### Full Automation Approach

AI reads all 45 .PLT and .OUT files, extracts the maximum concentration at any receptor for each pollutant/averaging period/met year combination, selects the controlling year, adds applicable background concentrations, and compares against NAAQS. Produces the same summary tables as the Grab_Plots workbook.

**Key strength:** This is a well-defined data extraction and comparison task. The .PLT file format is fixed, the NAAQS thresholds are published, and the compliance test is arithmetic (modeled + background < standard). The Grab_Plots workbook is essentially a structured reader for AERMOD output.

**Feasibility:** High. The reference project's Grab_Plots workbook (6 versions) shows this was iterated, but each iteration was driven by changes in model inputs, not changes in the extraction logic itself. The extraction and comparison logic is stable.

### AI-Assisted Approach

Same as full automation — this module has minimal judgment requirements. A human would review the final compliance table to confirm background concentration selections and verify that the correct met year governs each pollutant.

### Module Form

Python script that:
1. Parses AERMOD .PLT and .OUT files for maximum concentrations
2. Organizes results by pollutant, averaging period, and met year
3. Applies multi-year statistical processing where required (e.g., 98th percentile for 1-hr NO2)
4. Adds background concentrations
5. Generates compliance summary table
6. Exports formatted tables for the impact report

### Validation Method

- Compare extracted concentrations against Grab_Plots workbook values (exact match expected)
- Compare compliance determinations (pass/fail) for all 9 scenarios
- Verify background concentration values match those used in the reference project

### Key Risks

- NO2 1-hr processing requires ARM2 (Ambient Ratio Method 2) with ratio bounds — this is a model-specific statistical method, not simple max extraction
- Multi-year processing rules differ by pollutant (some use highest year, some use multi-year average)
- Background concentration selection requires knowledge of appropriate monitoring stations

---

## Module 5: FORMS — Merge Data & Form Generation

### Scope

Populate NDEP Class II permit application forms from emissions inventory data using a structured merge data approach. This replicates the mail-merge workflow where `Merge Data.xlsx` feeds into Word document templates.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Emission rates by source/pollutant | EI workbook [Module 1] | Proc sheet calculated values |
| Equipment specifications | Client data | Manufacturer spec sheets |
| PTE calculations | EI workbook [Module 1] | Summary sheet |
| NDEP form templates | NDEP website / project templates | C2-prefix template documents |

### Outputs

| Output | Reference File |
|--------|----------------|
| Merge Data.xlsx | `01-Permitting/Forms/Line Power Option/Merge Data.xlsx` |
| Combustion Equipment Application Form | `Combustion Equipment Application Form.docx` |
| Combustion Equipment Detailed Calculations | `COMBUSTION EQUIPMENT DETAILED CALCULATIONS.docx` |
| Greenhouse Gases form | `GREENHOUSE GASES.docx` |
| Hazardous Air Pollutants form | `HAZARDOUS AIR POLLUTANTS.docx` |
| PTE Analysis | PTE form document |
| Liquid Storage Tank Application Form | `Liquid Storage Tank Application Form.docx` |

### Full Automation Approach

AI reads emission rates and equipment data from the EI workbook, structures them into the Merge Data.xlsx format, then populates each NDEP template form. The merge field mapping is fixed per template — once the data is structured correctly, form population is deterministic.

**Key strength:** The NDEP Class II form templates have fixed fields. The mapping from EI workbook data to merge fields is a one-time schema definition. The actual population is mechanical.

**Feasibility:** High. The reference project shows this consumed ~10 hours across Stanley and Saucier (forms, figures, compilation). The forms are well-structured and the data sources are clearly defined in the EI workbook.

### AI-Assisted Approach

Same as full automation. Human reviews populated forms for completeness and formatting before final output.

### Module Form

Python script that:
1. Reads emission rates and equipment data from the EI workbook
2. Generates Merge Data.xlsx with correct field structure
3. Populates Word templates using `python-docx` and merge field substitution
4. Exports populated forms as Word documents

### Validation Method

- Compare Merge Data.xlsx field values against reference
- Compare each populated form document against reference versions (field-by-field)
- Verify all required fields are populated with no blanks

### Key Risks

- NDEP may update form templates between projects — template version management needed
- Merge field names must exactly match between Merge Data.xlsx and templates
- Some form fields may require reformatting (e.g., rounding conventions, unit labels)

---

## Module 6: DOC-GEN — Technical Document Generation

### Scope

Generate the technical narrative and air quality impact report from structured data. These are the two primary professional documents in the application package.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Facility description | Client data | Project correspondence |
| Equipment inventory and emissions summary | EI workbook [Module 1] | Proc and Summary sheets |
| Modeling configuration details | AERMOD INP files [Module 2] | INP file headers and options |
| Results summary tables | Results processing [Module 4] | Compliance tables |
| Meteorological data summary | Met data processing notes | AERMET output |
| GIS figures | GIS module [Module 7] | Impact maps for report figures |
| Regulatory applicability analysis | Professional knowledge | Nevada/federal rule assessment |

### Outputs

| Output | Reference File |
|--------|----------------|
| Technical Narrative (~4 pages) | `01-Permitting/Narrative/WFH_Narrative_LnPwr.docx` |
| Air Quality Impact Report (~17 pages + appendix) | `01-Permitting/Modeling/Report/Line Power Option/WFH_ClassII_Air_Quality_Impact_Report_LnPwr.docx` |
| Appendix A — Detailed results tables | `AppendixA_LnPwr.pdf` |

### Full Automation Approach

AI generates complete draft documents from structured data inputs — the narrative from the EI workbook data, the impact report from modeling results and configuration details. Both documents follow recognizable templates: the narrative describes facility, sources, emissions, and regulatory applicability; the impact report describes methodology, presents results, and demonstrates compliance.

**Key challenge:** The professional tone and regulatory framing require domain expertise. Phrases like "the facility's potential to emit is below the major source threshold" must be precisely correct — not approximately correct. Regulatory applicability analysis (NSPS, NESHAP, PSD, Title V) requires understanding which rules apply to which source types.

**Feasibility:** Medium. The document structures are template-like, and the data that fills them is well-defined. But the regulatory analysis sections and professional framing require judgment that is hard to validate automatically.

### AI-Assisted Approach

AI drafts all sections from structured data. For data-driven sections (source inventory tables, results tables, meteorological data summary), the draft is likely near-final. For judgment-intensive sections (regulatory applicability, methodology narrative, compliance conclusions), human edits for professional tone and regulatory accuracy.

**Value proposition:** The impact report alone is ~17 pages. The mechanical parts — generating tables from model output, describing the receptor grid, listing AERMOD options — are straightforward for AI. Even if the regulatory narrative sections need human editing, the time savings from automated table generation and boilerplate sections is significant. In the reference project, report writing consumed ~20 hours across Martin and Huelson.

**Feasibility:** High. The assisted mode is where this module delivers the most reliable value.

### Module Form

Python script or Claude prompt workflow that:
1. Reads structured data from upstream modules
2. Generates narrative sections using document templates and data insertion
3. Builds result tables from Module 4 output
4. Assembles complete Word documents using `python-docx`
5. Flags sections requiring human review (regulatory analysis, conclusions)

### Validation Method

- Compare document structure (section headings, table count) against reference
- Compare data tables (emission rates, modeling results) for accuracy
- Human review of narrative sections for regulatory correctness
- Word count and section length comparison

### Key Risks

- Regulatory applicability analysis requires current knowledge of Nevada rules
- Professional writing conventions in air quality consulting are not well-documented — they are learned through practice
- The impact report includes figures from Module 7 — timing dependency

---

## Module 7: GIS-FIG — GIS Figure Generation

### Scope

Generate publication-quality GIS figures for the permit application: facility layout, source locations, receptor grids, and maximum impact contour maps.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Site boundary coordinates | Survey data / client GIS | Module 3 output |
| Source locations (UTM) | EI workbook Sources sheet | Module 1 output |
| Building footprints | EI workbook BPIP sheet | Module 1 output |
| Receptor grid layout | EI workbook RE_grid sheet | Module 1 output |
| AERMOD concentration contours | .PLT files | Module 2 output |
| Base map imagery | TIFF / online tile services | Background imagery |

### Outputs

| Output | Reference File |
|--------|----------------|
| Facility layout map | `00_GIS/` output figures |
| Source location map | `00_GIS/` output figures |
| Maximum impact maps (by pollutant) | `00_GIS/` output figures |
| Receptor grid map | `00_GIS/` output figures |
| Project vicinity map | `00_GIS/` output figures |

### Full Automation Approach

AI generates all figures programmatically — plotting source locations, building outlines, receptor grids, and concentration contours on a base map with appropriate symbology, labels, scale bars, and north arrows.

**Key challenge:** Cartographic conventions in air quality permit applications are not formally standardized but follow professional norms: specific symbol styles, label placement, contour color ramps, legend formatting. Getting these "right" requires matching the expectations of NDEP reviewers.

**Feasibility:** Medium. The data processing (converting .PLT files to contours, plotting coordinates) is straightforward. The styling and layout conventions are the uncertain part.

### AI-Assisted Approach

AI builds all map layers and data, generates initial figures with default styling. Human adjusts symbology, label placement, and layout in a GIS environment (QGIS) or reviews/edits generated figures. AI exports final versions.

**Value proposition:** In the reference project, GIS work consumed ~15 hours across Stanley. The time-consuming part is not adding data to a map — it is georeferencing source locations (Module 3), building receptor grids (Module 3), and processing concentration contours. If those upstream steps are handled, the actual figure generation becomes assembly and styling. AI can handle assembly; human fine-tunes style.

**Feasibility:** High for the assisted mode. The data layers are well-defined from upstream modules.

### Module Form

Python script using `matplotlib`/`cartopy` or QGIS scripting that:
1. Creates base map with appropriate projection (UTM Zone 11N)
2. Plots facility boundary, buildings, sources from Module 1/3 data
3. Plots receptor grid from Module 1 data
4. Generates concentration contours from Module 2 .PLT files
5. Applies styling template (symbology, labels, legend, scale bar)
6. Exports figures as PNG at publication resolution

### Validation Method

- Visual comparison of AI-generated figures against reference project figures
- Verify all data elements are present (sources, buildings, receptors, contours)
- Verify coordinate accuracy by spot-checking known locations
- Confirm figure dimensions and resolution meet submission requirements

### Key Risks

- Cartographic styling conventions vary between consulting firms and regulatory agencies
- Concentration contour interpolation from AERMOD grid data requires careful processing
- Base map imagery sourcing and licensing
- Label placement for readability is a design judgment

---

## Module 8: COMPLY — Post-Permit Compliance Package

### Scope

Parse issued permit conditions into trackable compliance obligations and generate the compliance tracking workbooks, operating policies, and notification letters required after permit issuance.

### Inputs

| Input | Source | Reference File |
|-------|--------|----------------|
| Final permit conditions | NDEP Permit AP7041-4757 | Issued permit document |
| Equipment operating parameters | Client data / permit conditions | Operating limits |
| Compliance reporting requirements | Permit conditions | Reporting schedules |
| Startup dates | Client notification | Actual vs. anticipated startup |

### Outputs

| Output | Reference File |
|--------|----------------|
| Annual compliance workbooks (2025, 2026) | `00_Compliance/` workbooks |
| Generator operating policy | `00_Compliance/` policy document |
| System 1 anticipated startup notification | `00_Compliance/` notification letter |
| System 1 actual startup notification | `00_Compliance/` notification letter |
| System 2 anticipated startup notification | `00_Compliance/` notification letter |

### Full Automation Approach

AI reads the issued permit PDF, extracts every condition with a compliance obligation (emission limits, monitoring requirements, recordkeeping, reporting deadlines, notification requirements), and generates:
- Compliance workbooks with formulas tied to permit-specific limits
- Template operating policy documents that reference specific permit conditions
- Notification letter drafts with correct regulatory references and deadlines

**Key challenge:** Permit conditions are written in regulatory language that must be parsed precisely. Missing a condition or misinterpreting a deadline could result in a compliance violation. The permit document is the source of truth and there is no room for paraphrasing.

**Feasibility:** Medium-High. The permit conditions follow a standardized structure (NDEP Class II permits use a consistent format). The main risk is missing a condition — completeness rather than accuracy of interpretation.

### AI-Assisted Approach

AI extracts all permit conditions into a structured checklist, generates draft compliance workbooks and notification letters. Human reviews the condition extraction for completeness and verifies that every obligation has a corresponding tracking mechanism.

### Module Form

Python script or Claude prompt workflow that:
1. Reads permit PDF and extracts conditions with regulatory references
2. Categorizes conditions (emission limits, monitoring, recordkeeping, reporting, notifications)
3. Generates Excel compliance workbooks with formulas for each tracked parameter
4. Drafts operating policy from permit requirements
5. Generates notification letter templates with correct dates and references

### Validation Method

- Compare extracted conditions list against manual reading of permit
- Compare compliance workbook structure and formulas against reference
- Verify all notification deadlines are correctly calculated
- Compare generated letters against reference project letters

### Key Risks

- Permit condition parsing must be exhaustive — missing one condition is a compliance failure
- Deadline calculations depend on actual startup dates (variable input)
- Operating policy must precisely reference permit condition numbers

---

## Items Not Proposed as Standalone Modules

### Application Assembly

Compiling the final PDF application package from individual deliverables (cover letter, forms, narrative, impact report, figures, spec sheets) is a mechanical assembly step — not a module requiring AI intelligence. It is a build step that concatenates outputs from Modules 5, 6, and 7 with standard components (cover letter, equipment spec sheets). Handled as a final step in the build pipeline rather than a separate module.

### RFI Response

Requests for Information from NDEP are ad hoc — the agency asks unpredictable questions about the submitted application. In the reference project, the RFI asked for boundary coordinates and building parameters — data that already existed in the EI workbook and GIS files. Rather than building a module for RFI response, we treat RFI scenarios as validation tests for data accessibility: if the upstream modules produce well-structured, queryable data, RFI responses become data retrieval rather than new analysis. The question becomes "can we quickly find and extract the requested information from our data?" — which tests the quality of upstream module outputs.

---

## Cross-Module Data Flow

```
Client Data
│
├──► [3] SITE-CHAR ──► Source coordinates, building footprints, receptor grids
│         │
│         ▼
├──► [1] EI-POP ────► Populated EI workbook (emissions, parameters, spatial data)
│         │
│         ├──► [2] AERMOD-RUN ──► .INP files, .OUT files, .PLT files
│         │         │
│         │         ├──► [4] RESULTS ──► Compliance tables, summary data
│         │         │         │
│         │         │         └──► [6] DOC-GEN ──► Impact report, narrative
│         │         │
│         │         └──► [7] GIS-FIG ──► Impact contour maps
│         │
│         └──► [5] FORMS ──► Populated application forms
│
│                               ┌──────────────────────────────┐
│                               │ Application Assembly (build) │
│                               │ Forms + Narrative + Report   │
│                               │ + Figures + Cover Letter     │
│                               └──────────┬───────────────────┘
│                                          │
│                                          ▼
│                                    NDEP Submission
│                                          │
│                                          ▼
│                                    Permit Issued
│                                          │
└──────────────────────────────────► [8] COMPLY ──► Compliance package
```

## Effort vs. Automation Assessment

Mapping AI automation potential against actual hours spent in the reference project:

| Module | Ref. Hours (est.) | Full Auto | AI-Assisted | Primary Value |
|--------|-------------------|-----------|-------------|---------------|
| EI-POP | ~40 hrs | Medium-High | High | Eliminates tedious factor lookup and column population |
| AERMOD-RUN | ~35 hrs | High | High | Replaces VBA macro and batch scripting with reproducible pipeline |
| SITE-CHAR | ~15 hrs | Low-Medium | Medium-High | Converts 7+ hrs of manual GIS/coordinate work to 1-2 hrs of review |
| RESULTS | ~10 hrs | High | High | Automates mechanical extraction and comparison |
| FORMS | ~10 hrs | High | High | Eliminates manual mail-merge with programmatic form population |
| DOC-GEN | ~20 hrs | Medium | High | Automates table generation and boilerplate; human edits narrative |
| GIS-FIG | ~15 hrs | Medium | High | AI builds data layers; human adjusts cartographic styling |
| COMPLY | ~10 hrs | Medium-High | High | Automates permit condition extraction and workbook generation |

**Note:** Hour estimates are approximate, derived from the time analysis in [03-time-analysis.md](03-time-analysis.md) and mapped to module scope. The reference project total was 224.5 hours; some hours (project management, client communication, QA coordination) don't map to any module.

## Next Steps

1. **Phase A prototype** — Build EI-POP and SITE-CHAR modules using 270-10-1 reference data
2. **Validate against known outputs** — Compare module outputs to actual project deliverables
3. **Assess automation levels** — After prototype validation, confirm or adjust the Full Auto / AI-Assisted ratings
4. **Phase B development** — Build AERMOD-RUN and RESULTS, feeding from Phase A outputs
5. **End-to-end integration** — Chain all modules and test the complete pipeline
