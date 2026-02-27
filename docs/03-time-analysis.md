# Time Entry Analysis: 270-10-1 Work Force Hub

## Overview

All time charged to project 270-10-1 was pulled from BQE Core via the time entry API. Every entry includes the date, employee, hours, billing rate, and a memo describing the work performed.

**Source data:** `data/270-10-1_time_entries_raw.json` (86 entries)

## Financial Summary

| Metric | Value |
|--------|-------|
| Total entries | 86 |
| Total hours | 224.5 |
| Total billed | $43,848 |
| Contract amount | $41,200 |
| Over/under | +$2,648 (6.4% over budget) |
| Active billing period | Nov 21, 2024 – May 23, 2025 |
| Calendar duration | 183 days (~6 months) |

## Personnel

| Person | Role | Bill Rate | Hours | Cost | % of Hours |
|--------|------|-----------|-------|------|------------|
| Alyssa D. Stanley | Support I/II | $70-98/hr | 73.2 | $5,512 | 32.6% |
| Timothy S. Martin | Principal II | $258-265/hr | 70.5 | $18,632 | 31.4% |
| Elizabeth M. Huelson | Principal II (PM) | $258-265/hr | 58.2 | $15,386 | 25.9% |
| Max M. Hampson | Associate | $209/hr | 11.2 | $2,351 | 5.0% |
| Holly A. Saucier | Senior | $181/hr | 9.5 | $1,720 | 4.2% |
| Dulce Gonzalez-Beltran | Staff | $148/hr | 1.2 | $185 | 0.5% |
| Ruben V. Teasyatwho | Assistant | $124/hr | 0.5 | $62 | 0.2% |

**Key observation:** The three primary contributors (Stanley, Martin, Huelson) account for 90% of hours but their cost profiles are very different. Stanley at $70-98/hr performed the most hours but only 12.6% of cost. Martin and Huelson at $258-265/hr performed fewer hours but 77.6% of cost. This reflects a leverage model where junior staff execute volume tasks (GIS, forms, figures) while senior staff handle technical judgment (emissions calculations, modeling, regulatory strategy).

## Role Mapping

Based on the memo descriptions, each person's actual role on this project was:

| Person | Functional Role | Key Tasks |
|--------|----------------|-----------|
| **Elizabeth Huelson** | Project manager, technical lead | Client communication, emissions inventory, source characterization, regulatory strategy, QA, narrative writing, application assembly, RFI responses, draft permit review, compliance setup |
| **Timothy Martin** | Dispersion modeler | AERMOD setup, met data processing, receptor grids, model iterations (01-05), model debugging, modeling report writing, NDEP file compilation |
| **Alyssa Stanley** | GIS/forms/figures analyst | QGIS mapping, BPIP file construction, receptor grid generation, Class II application forms, modeling report figures, application compilation |
| **Max Hampson** | Model QA reviewer | Independent model review, building downwash routine revision, results verification |
| **Holly Saucier** | Technical reviewer/support | Application form review, HAP calculations, figure updates, formatting assistance, spec sheet research |
| **Dulce Gonzalez-Beltran** | QA support | Emissions inventory quality assurance |
| **Ruben Teasyatwho** | Support | Compliance log QA, spec sheet research |

## Complete Time Entry Log

Every time entry is listed below, organized chronologically. This is the primary record of work performed.

### Phase 1: Project Initiation and Data Gathering (Nov 21 – Dec 20, 2024)

**14.5 hours | 1 person (Huelson + 1 entry Gonzalez-Beltran)**

This phase was entirely driven by the project manager. Work consisted of client meetings, data requests, preliminary calculations, and permitting strategy discussions.

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| Nov 21 | Huelson | 1.25 | Participated in work force hub air permitting kickoff meeting. Sent data needs for air permitting to J. Schonlau. |
| Dec 4 | Huelson | 0.50 | Reviewed information on propane combustion units, calculated emission estimates, and replied on potential generator restrictions. |
| Dec 5 | Huelson | 0.75 | Reviewed updated heater data and replied to J. Orta. |
| Dec 9 | Huelson | 0.50 | Reviewed insignificant source regulations and responded to J. Orta regarding WFH propane combustion units. |
| Dec 10 | Huelson | 0.25 | Discussed WFH permitting status and options with J. Schonlau. |
| Dec 12 | Huelson | 0.75 | Discussed permitting strategy and timing with LNC team. |
| Dec 16 | Huelson | 0.75 | Began working on generator emissions. |
| Dec 17 | Gonzalez-Beltran | 1.25 | Assured quality of emission inventory to ensure number of units and formulas are correct. |
| Dec 17 | Huelson | 1.50 | Finished calculating generator emissions and added propane combustion units to the emission inventory. |
| Dec 20 | Huelson | 1.00 | Discussed permitting strategy, data needs, and timing with LNC team. Began working on emergency generator information for permitting. |

**What happened:** Huelson gathered equipment specifications from the client (propane heaters, generators, fire pump), evaluated regulatory applicability (insignificant source thresholds), calculated preliminary emissions, and aligned on permitting strategy. The emissions inventory was started and QA'd by Gonzalez-Beltran.

### Phase 2: Modeling Setup (Dec 26 – Dec 29, 2024)

**7.25 hours | 1 person (Martin)**

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| Dec 26 | Martin | 2.50 | Worked on modeling files setup. Worked on project mapping setup. Prepared files for aermap with version 24142. |
| Dec 27 | Martin | 2.50 | Continued work on modeling files setup. Reviewed the latest version of meteorological data provided by NDEP for the Winnemucca airport. Continued work on project mapping setup. |
| Dec 29 | Martin | 2.25 | Continued work on modeling files setup and mapping. Prepared for aermap receptor processing needs. Finalized review of the Winnemucca meteorological data for use in modeling. |

**What happened:** Martin set up the AERMOD modeling infrastructure: configured AERMAP for terrain processing, reviewed and validated the NDEP-provided meteorological data (Winnemucca surface + Elko upper air, 2017-2021), and prepared the base mapping/coordinate framework.

### Phase 3: Full Team Analysis Sprint (Jan 6 – Jan 27, 2025)

**151.25 hours | 6 people**

This was the core production phase. The full team worked intensely over 3 weeks.

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| Jan 6 | Huelson | 0.25 | Reviewed data needs and replied to J. Schonlau. |
| Jan 8 | Stanley | 0.50 | Met with E. Huelson to begin WFH georeferenced map. |
| Jan 8 | Huelson | 3.50 | Added emergency generator and diesel tank to inventory. Began working on source characterization for modeling. Discussed building layout and characterization for modeling with A. Stanley. |
| Jan 8 | Saucier | 1.50 | Assisted R. Teasyatwho with finding a generator spec sheet. |
| Jan 8 | Martin | 0.25 | Reviewed model source configurations for building heater and communicated with E. Huelson. |
| Jan 9 | Stanley | 7.00 | Continued building WFH model for E. Huelson in QGIS. Began building BPIP file in Excel. |
| Jan 9 | Huelson | 2.00 | Continued working on source characterization for modeling. Completed HAP emission calculations. |
| Jan 9 | Saucier | 1.75 | Assisted A. Stanley with georeferencing site map and creating sources and buildings in QGIS. |
| Jan 10 | Stanley | 7.75 | Finished building BPIP file and began charting receptor grids in QGIS for E. Huelson. |
| Jan 10 | Huelson | 1.25 | Worked on bpip setup with A. Stanley. Worked with A. Stanley and T. Martin on model setup, including building downwash inputs and receptors. |
| Jan 13 | Stanley | 6.75 | Modeled WFH receptor grids with Lakes AERMOD for E. Huelson. |
| Jan 14 | Stanley | 0.75 | Made QGIS figure with receptor grids for E. Huelson. |
| Jan 14 | Huelson | 3.00 | Finished draft inventory with source and building characterization and sent to T. Martin for modeling. Discussed application forms with A. Stanley and H. Saucier. |
| Jan 14 | Saucier | 0.50 | Assisted A. Stanley with receptor processing and input into QGIS. |
| Jan 14 | Martin | 10.00 | Communicated with E. Huelson. Worked on project mapping. Worked on receptor processing. Worked on the draft modeling report. Worked on modeling files setup. |
| Jan 15 | Huelson | 0.50 | Sent list of application data needs to J. Schonlau. Discussed initial model results with T. Martin. |
| Jan 15 | Martin | 12.00 | Continued work on modeling files setup. Set up the modeling tab in the emissions inventory. Worked on model debugging. Worked on automated results processing. |
| Jan 16 | Stanley | 2.25 | Began populating Class II operating permit forms for E. Huelson. |
| Jan 16 | Huelson | 2.75 | Updated characterization of building heaters based on initial model results. Worked on draft modeling report. |
| Jan 16 | Saucier | 2.00 | Assisted A. Stanley with Class II application form population. |
| Jan 16 | Martin | 9.00 | Worked on iteration 01 model runs, including sensitivity runs to show compliance with the 1-hour NO2 standards. Communicated with E. Huelson. |
| Jan 17 | Stanley | 2.50 | Continued populating Class II operating permit forms for E. Huelson. |
| Jan 17 | Huelson | 0.75 | Updated EI for 2nd iteration of release parameters for building heaters. Worked on modeling report. |
| Jan 17 | Martin | 1.75 | Worked on modeling iteration 03. Worked on compilation of electronic modeling files. |
| Jan 20 | Stanley | 5.00 | WFH Model QA with M. Hampson. |
| Jan 20 | Huelson | 0.50 | Summarized compliance and reporting requirement for Target. |
| Jan 20 | Hampson | 6.25 | Performed model review and quality checks with A. Stanley. Completed initial review of modeling, summarized results, and provided notes to T. Martin. Call with T. Martin. |
| Jan 21 | Stanley | 6.75 | WFH Class II forms for E. Huelson. Model QA with M. Hampson. |
| Jan 21 | Huelson | 0.75 | Reviewed modeling status. Finished initial draft of modeling report. |
| Jan 21 | Hampson | 5.00 | Revised building downwash generation routine as requested by T. Martin. |
| Jan 21 | Martin | 7.50 | Updated the draft modeling report. Worked on project mapping. Communicated with M. Hampson and E. Huelson. |
| Jan 22 | Stanley | 8.00 | Modeling report figures and Class II application forms for E. Huelson. |
| Jan 22 | Huelson | 1.25 | Worked on model report figures with A. Stanley. |
| Jan 23 | Stanley | 7.75 | Modeling report figures and Class II applications for E. Huelson. |
| Jan 23 | Huelson | 2.75 | Reviewed updated modeling figures and incorporated into report. Worked on Class II Application. Discussed model update with T. Martin and adjusted EI. |
| Jan 23 | Saucier | 2.00 | Assisted A. Stanley with modeling report figures updates, HAPs calculation form, and tanks form completion. |
| Jan 23 | Martin | 1.00 | Discussed stack parameter issues with E. Huelson and prepared files for iteration 04. |
| Jan 24 | Stanley | 4.50 | Compiled WFH application for E. Huelson. |
| Jan 24 | Huelson | 4.25 | Continued working on Class II Application. Finalized modeling report. Worked on narrative. |
| Jan 24 | Martin | 3.50 | Worked on iteration 04 and updated all deliverables. Communicated with E. Huelson and A. Stanley. |
| Jan 27 | Stanley | 1.75 | Class II application for E. Huelson. |
| Jan 27 | Huelson | 0.75 | Participated in meeting on WFH power update and discussed best path forward. |
| Jan 27 | Saucier | 1.00 | Assisted A. Stanley with finalizing application updates and formatting. |

**What happened:** This phase moved from data assembly through completed deliverables:

- **Jan 8-10:** GIS setup — Stanley built the georeferenced facility map in QGIS, constructed the BPIP (building profile) input file, and generated receptor grids. Huelson added sources to the emissions inventory and characterized them for modeling.
- **Jan 13-14:** Handoff to modeling — Huelson completed the draft EI with source characterization and sent it to Martin. Stanley processed receptor grids through AERMAP.
- **Jan 14-16:** First model runs — Martin ran iteration 01 including NO2 sensitivity analysis. Huelson refined source parameters based on results. Stanley and Saucier began populating NDEP application forms.
- **Jan 17:** Model iterations 02-03 — Martin refined modeling, Huelson updated release parameters for building heaters.
- **Jan 20-21:** QA checkpoint — Hampson performed an independent model QA review with Stanley, identified issues, and revised the building downwash routine. Martin updated deliverables.
- **Jan 22-24:** Deliverable production — Stanley generated all report figures and compiled application forms. Huelson assembled the narrative, finalized the modeling report, and worked on the Class II application. Martin ran iteration 04.
- **Jan 27:** Line power option introduced — client meeting changed the power strategy. Forms finalized for original generator option.

### Phase 4: Dual-Option Application Development (Jan 30 – Feb 18, 2025)

**48.0 hours | 4 people**

The client decided to pursue line power instead of generators, requiring a parallel set of deliverables.

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| Jan 30 | Huelson | 0.25 | Discussed latest plan to permitting including two application options (line power or generators). |
| Jan 31 | Huelson | 0.50 | Updated emission inventory for "Line Power" permitting option and provided to T. Martin for modeling. |
| Feb 3 | Stanley | 3.00 | Class II application form revisions for E. Huelson. Generated model report figures for Line Power application. |
| Feb 3 | Huelson | 3.50 | QA'ed Class II Application forms and discussed Line Power application option with A. Stanley. Finalized draft narrative for Generator option and worked on modeling report. |
| Feb 4 | Stanley | 4.00 | WFH Line Power option application and figures for E. Huelson. QA on Generator Option Application. QA on Line Power option application. |
| Feb 4 | Huelson | 4.00 | Drafted modeling report and narrative for Line Power option. Discussed application with A. Stanley. Finalized draft application for Generator option. Finalized draft application for Line Power. |
| Feb 4 | Saucier | 0.25 | Reviewed application narrative for E. Huelson. |
| Feb 5 | Huelson | 0.25 | Discussed application public notice and signature requirements with J. Schonlau. |
| Feb 5 | Martin | 10.50 | Worked on Iteration 04 for the line power scenario and finalized all modeling deliverables. Worked on a draft modeling report for the new scenario. Worked on project mapping. Compiled electronic files for NDEP. Communicated with E. Huelson. |
| Feb 6 | Huelson | 0.25 | Responded to questions on WFH application. |
| Feb 10 | Huelson | 0.75 | Participated in meeting with Target to discuss permitting questions. |
| Feb 11 | Huelson | 0.50 | Reviewed fire pump specifications and followed up with G. Young (Target). |
| Feb 12 | Huelson | 1.00 | Visited work force hub and discussed permitting plan going forward. Reviewed fire pump engine label and replied to G. Young. |
| Feb 14 | Stanley | 3.00 | Updated WFH line power application to include new sources for E. Huelson. |
| Feb 14 | Huelson | 2.75 | Updated emission inventory with fire water pump and sent to T. Martin for modeling. Worked on updating narrative and modeling report. Discussed application forms with A. Stanley. |
| Feb 14 | Saucier | 0.50 | Reviewed fire pump engine calculations and updated HAPs for E. Huelson. |
| Feb 16 | Martin | 7.75 | Worked on Iteration 05 for the updated line power scenario and finalized all modeling deliverables. Updated the draft modeling report for the new scenario. Worked on project mapping. Compiled electronic files for NDEP. Communicated with E. Huelson. |
| Feb 17 | Stanley | 2.00 | Updated WFH Line power application figures and Class II forms for E. Huelson. |
| Feb 17 | Huelson | 3.75 | Finalized WFH Class II AQOP application and sent to Lithium Nevada and Target to review. |
| Feb 18 | Huelson | 0.25 | Updated RO in cover letter and application and sent to J. Schonlau for signature. |

**What happened:** The team pivoted to produce two complete application packages simultaneously:

- **Jan 30-31:** Huelson learned the client wanted to consider line power; updated the EI accordingly.
- **Feb 3-4:** Dual-track work — finalized the generator option application while building the line power version. Both application packages, narratives, and modeling reports prepared in parallel.
- **Feb 5:** Martin ran iteration 04 for line power and compiled the full NDEP electronic submission package.
- **Feb 11-14:** Fire pump added to line power option — Huelson visited the site, got engine specs from fire pump label. EI updated again, iteration 05 run.
- **Feb 17-18:** Final application sent to client for review, then to NDEP with cover letter.

### Phase 5: Regulatory Review Period (Mar 10 – Apr 3, 2025)

**2.0 hours | 1 person (Huelson)**

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| Mar 10 | Huelson | 0.75 | Provided requested plant boundary and building parameter tables to send to BAPC. |
| Mar 25 | Huelson | 1.00 | Drafted response to RFI #1 for WFH. |
| Apr 3 | Huelson | 0.25 | Replied to J. Orta on the emergency engine size included in the application. |

**What happened:** NDEP reviewed the application. One formal RFI was received (March 25) requesting boundary coordinates and building parameters — both easily provided from existing project data. One follow-up question on engine size was answered. Total effort: 2 hours over 24 days.

### Phase 6: Draft Permit Review and Compliance Setup (May 12 – May 23, 2025)

**7.5 hours | 2 people**

| Date | Person | Hrs | Memo |
|------|--------|-----|------|
| May 12 | Huelson | 3.25 | Reviewed draft permit and provided comments. |
| May 13 | Huelson | 2.00 | Began creating compliance log to track generators and calculate annual emissions for reporting QA. Added conditional formatting for compliance checks. |
| May 13 | Teasyatwho | 0.50 | QA'ed compliance log and made adjustments. |
| May 15 | Huelson | 0.25 | Finalized WFH compliance tracker and sent to J. Schonlau for review. |
| May 16 | Huelson | 1.00 | Reviewed compliance and notification requirements with Target. Drafted anticipated startup notice for System 2. |
| May 19 | Huelson | 0.25 | Reviewed updated draft permit and replied to J. Schonlau. |
| May 23 | Huelson | 0.25 | Discussed public notice process and upcoming permit with T. Crowley. |

**What happened:** NDEP issued a draft permit in early May. Huelson reviewed it and provided comments (3.25 hours — suggests substantive review). She then created the annual compliance tracking workbook and drafted the System 2 startup notification. The final signed permit was issued September 22, 2025 with no additional billable work.

## Workflow Reconstruction

Based on the time entries, the project followed this sequence:

```
PHASE 1: Initiation (Nov-Dec)           14.5 hrs    6.5%
  ├── Kickoff meeting
  ├── Data requests to client
  ├── Equipment spec review
  ├── Preliminary emissions calculations
  ├── Regulatory applicability checks
  └── Emissions inventory (draft) + QA

PHASE 2: Modeling Setup (Dec)             7.25 hrs   3.2%
  ├── AERMOD file structure setup
  ├── AERMAP terrain processing
  ├── Met data review (NDEP Winnemucca)
  └── Base coordinate framework

PHASE 3: Production Sprint (Jan)        151.25 hrs  67.4%
  ├── GIS facility mapping (QGIS)
  ├── BPIP building profile generation
  ├── Receptor grid construction
  ├── Source characterization → EI finalization
  ├── AERMOD iterations 01-04
  ├── NO2 sensitivity analysis
  ├── Independent model QA (Hampson)
  ├── Building downwash revision
  ├── Class II application form population
  ├── Modeling report writing
  ├── Report figure generation
  ├── Technical narrative writing
  └── Application compilation

PHASE 4: Dual-Option Pivot (Feb)         48.0 hrs  21.4%
  ├── Line power EI update
  ├── Line power modeling (iterations 04-05)
  ├── Fire pump addition (site visit)
  ├── Parallel application packages
  ├── Narrative and report for both options
  ├── NDEP electronic file compilation
  └── Final application submission

PHASE 5: Regulatory Review (Mar-Apr)      2.0 hrs   0.9%
  ├── RFI #1 response
  └── Follow-up question

PHASE 6: Permit & Compliance (May)        7.5 hrs   3.3%
  ├── Draft permit review + comments
  ├── Compliance workbook creation
  ├── Startup notification drafting
  └── Public notice coordination
```

## Observations for AI Reproduction

### What an AI agent could likely handle

1. **Emissions calculations** — AP-42 emission factors, fuel consumption calculations, and PTE analysis follow deterministic formulas. The EI workbook is essentially a structured calculation engine.
2. **Application form population** — The Class II forms require transferring data from the EI and source characterization into standardized fields. This is mechanical.
3. **Report figure generation** — GIS maps with standard layers (facility layout, receptors, modeled impacts) follow a repeatable template.
4. **Compliance workbook creation** — Structured spreadsheet with permit conditions, emission limits, and tracking formulas.
5. **RFI responses** — The RFI asked for data that already existed in the project files (boundary coordinates, building parameters). Retrieval and formatting.

### What would require human judgment or external interaction

1. **Client communication and data gathering** — The project depended on back-and-forth with the client (J. Schonlau, J. Orta, G. Young) to obtain equipment specs, operating parameters, and design decisions. An AI can't call or email clients.
2. **Permitting strategy** — Deciding between generator vs. line power options, evaluating insignificant source thresholds, and advising the client required professional judgment about regulatory risk.
3. **Site visit** — Huelson visited the facility (Feb 12) to verify fire pump specifications from the engine label. Physical inspection cannot be replicated.
4. **Model debugging and iteration** — Martin spent significant time debugging model runs and running sensitivity analyses. While AERMOD execution is mechanical, interpreting unexpected results and deciding how to adjust requires expertise.
5. **Independent QA review** — Hampson's model review was a professional judgment exercise, not a checklist.
6. **Draft permit review** — Huelson spent 3.25 hours reviewing NDEP's draft permit, which requires understanding permit conditions in the context of the specific facility.
7. **Mid-project scope changes** — The pivot from generators to line power was driven by a client decision during the project. Adapting required re-evaluating the entire analysis chain.

### Cost structure insight

The billing data reveals that **67% of hours and cost occurred in a 3-week January sprint**. An AI agent that could accelerate even portions of this sprint (e.g., form population, figure generation, report drafting) could meaningfully reduce project timelines and cost, even if it cannot handle the full workflow autonomously.

## Date

Analysis performed February 27, 2026. Data sourced from BQE Core API.
