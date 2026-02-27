# Project Anatomy: 270-10-1 Work Force Hub Air Quality Permitting

## Project Summary

| Field | Value |
|-------|-------|
| BQE Code | 270-10-1 |
| Client | Lithium Nevada LLC / Target Logistics Management LLC |
| Project Name | Work Force Hub Air Quality Permitting |
| Permit Type | Nevada Class II Air Quality Operating Permit (AQOP) |
| Regulatory Agency | Nevada Division of Environmental Protection (NDEP) |
| Permit Number | AP7041-4757 |
| Application Number | A2497 |
| Contract Amount | $41,200 |
| Total Hours Billed | 224.5 |
| Active Billing Period | November 2024 – May 2025 |
| Permit Issued | September 22, 2025 |
| Project Manager | Elizabeth Huelson |
| Location | Northwestern Nevada (Winnemucca area) |

## Facility Description

The Work Force Hub (WFH) is an industrial support facility associated with Lithium Nevada's mining operations. The facility required air quality permitting for equipment including:

- Diesel engines (backup generator and fire pump)
- Propane-fired heating systems
- Liquid storage tanks (propane)

Two technology options were evaluated:
1. **Generator Option:** Dual 1000 kW Cummins diesel generators for primary power, plus fire pump
2. **Line Power Option (selected):** Grid connection for primary power, single backup diesel fire pump engine

The Line Power option was selected for the permit application, resulting in significantly lower emissions.

## Personnel and Effort

| Person | Hours | Role (inferred from tasks) |
|--------|-------|---------------------------|
| Alyssa D. Stanley | 73.2 | Senior technical analyst (modeling, calculations) |
| Timothy S. Martin | 70.5 | Technical analyst (modeling, report writing) |
| Elizabeth M. Huelson | 58.2 | Project manager, regulatory liaison, QA |
| Max M. Hampson | 11.2 | Modeling support |
| Holly A. Saucier | 9.5 | Technical review |
| Dulce Gonzalez-Beltran | 1.2 | Administrative/review support |
| Ruben V. Teasyatwho | 0.5 | Support |

## Monthly Effort Distribution

```
Nov 2024:   1.2 hrs  #           (project initiation)
Dec 2024:  14.5 hrs  ##########  (data gathering, setup)
Jan 2025: 151.2 hrs  ########################################  (bulk of analysis)
Feb 2025:  48.0 hrs  #############  (application preparation and submission)
Mar 2025:   1.8 hrs  #           (RFI response)
Apr 2025:   0.2 hrs  #           (minimal activity)
May 2025:   7.5 hrs  ###         (draft permit review, compliance setup)
```

The project shows a characteristic "front-loaded" pattern: heavy analytical work in January, submission in February, then minimal effort during NDEP review with brief engagement for the RFI response and draft permit review.

## Project File Structure

**Root directory:** `/Volumes/qdrive2/Projects/270-NW_Nevada_Project/10_Work Force Hub/`

```
10_Work Force Hub/
├── 00_Compliance/          Post-permit compliance documents
│   ├── Compliance workbooks (2025, 2026)
│   ├── Generator operating policy
│   └── Startup notifications (System 1 & 2)
│
├── 00_EI/                  Emissions Inventory
│   ├── Current workbooks (Line Power R1, NDEP submission version)
│   ├── Archive/ (earlier revisions showing iteration history)
│   └── Reference/ (AP-42 factors, CFR references, engine specs)
│
├── 00_GIS/                 Geographic Information System data
│   ├── QGIS project file (.qgz)
│   ├── Shapefiles (buildings, sources, parcel boundary)
│   ├── Source coordinates (CSV with UTM)
│   └── Report figures (PNG maps for both technology options)
│
├── 00_Permit/              Final permit and SAD
│   ├── Signed permit (AP7041-4757, Sept 22, 2025)
│   └── Source Applicability Determination
│
├── 01-Permitting/          Permit application and analysis
│   ├── Archive/ (submitted application packages)
│   ├── Equipment Specs/ (engine specs, fire pump specs)
│   ├── Forms/ (NDEP application forms, calculations)
│   │   ├── Line Power option (SUBMITTED)
│   │   │   ├── Combustion equipment forms & calculations
│   │   │   ├── GHG calculations
│   │   │   ├── HAP calculations
│   │   │   ├── PTE (Potential to Emit) analysis
│   │   │   └── Tank forms
│   │   └── Generator option (NOT SUBMITTED, archived)
│   ├── Modeling/ (AERMOD dispersion modeling)
│   │   ├── To NDEP - February 2025/ (submitted package)
│   │   │   ├── AERMOD input/output for 9 pollutant scenarios
│   │   │   ├── Building downwash calculations
│   │   │   ├── Meteorological data (2017-2021, Winnemucca)
│   │   │   ├── Receptor grids (boundary, near-field, far-field)
│   │   │   └── NED elevation data
│   │   ├── NOT SUBMITTED - Impact Analysis - Gens/ (generator option)
│   │   ├── Iteration01 through Iteration05/ (model refinement history)
│   │   ├── QA/ (quality assurance checks)
│   │   └── README.txt
│   ├── Narrative/ (technical narratives for both options)
│   ├── Reference/ (correspondence, RFI responses)
│   └── Report/ (Class II Air Quality Impact Reports)
│
├── 99-Project Support/     Administrative records
│   ├── Invoices (Dec 2024 - May 2025, all paid)
│   ├── Project Setup Form
│   └── Purchase Order
│
└── Lift Station Notes/     Client correspondence
```

**File counts by type (approximate):**
- AERMOD model files (INP/OUT/PLT): ~2,500
- GIS shapefiles: ~50
- Word documents (.docx): ~43
- Spreadsheets (.xlsx/.xlsm): ~62
- PDFs: ~59
- Email messages (.msg): ~28
- Batch files (.bat): ~334
- Total: ~3,340 files

## Deliverable Inventory

### Primary Deliverables (submitted to NDEP)

1. **Permit Application Package** (February 2025)
   - Cover letter
   - NDEP Class II application forms
   - Combustion equipment forms and calculations
   - GHG calculations
   - HAP calculations
   - Potential to Emit (PTE) analysis
   - Liquid storage tank forms

2. **Technical Narrative** (`WFH_Narrative_LnPwr.pdf`)
   - Project description
   - Equipment inventory
   - Emissions calculations methodology
   - Regulatory applicability analysis

3. **Air Quality Impact Report** (`WFH_ClassII_Air_Quality_Impact_Report_LnPwr.pdf`)
   - AERMOD dispersion modeling methodology
   - Meteorological data summary
   - Receptor grid description
   - Modeling results and impact assessment
   - Comparison to NAAQS and significance levels
   - Appendix A with detailed results tables

4. **AERMOD Modeling Package** (1.3 GB compressed)
   - Complete input files for all pollutant scenarios
   - Output files with concentration predictions
   - Meteorological data files
   - Receptor grid definitions
   - Building downwash calculations
   - Model executables

5. **Emissions Inventory Workbook** (`LN WFH EmisInv_LnPwr_r1_NDEP.xlsm`)
   - Source-by-source emissions calculations
   - AP-42 emission factors with citations
   - Equipment specifications and operating parameters

### Supporting Deliverables

6. **RFI Response** (March 25, 2025)
   - Boundary coordinates document
   - Building parameters document
   - Responsive letter

7. **GIS Figures**
   - Facility layout maps
   - Maximum modeled impacts maps
   - Receptor location maps
   - Project location maps

### Post-Permit Deliverables

8. **Compliance Workbooks** (annual tracking spreadsheets)
9. **Generator Operating Policy**
10. **Startup Notification Letters** (anticipated and actual startup for Systems 1 & 2)

## Regulatory Timeline

```
Sep 2024    Application forms initially prepared (generator option)
Nov 2024    Project initiated under line power option
Jan 2025    Emissions inventory finalized; AERMOD modeling completed
Feb 2025    Permit application submitted to NDEP
Mar 2025    RFI #1 received and responded to (same day turnaround)
May 2025    Draft permit issued by NDEP; public notice period
Sep 2025    FINAL PERMIT ISSUED (AP7041-4757, signed Sept 22)
Dec 2025    System 1 anticipated startup notification filed
Feb 2026    System 1 actual startup notification filed
```

## Technical Specifications

### Emissions Modeling (AERMOD)

| Parameter | Value |
|-----------|-------|
| Model | AERMOD (EPA regulatory dispersion model) |
| Version | v23132 |
| Met Station (surface) | Winnemucca, Nevada |
| Met Station (upper air) | Elko, Nevada |
| Met Data Period | 5 years (2017-2021) |
| Terrain Data | NED 1/3-arc-second resolution |
| Receptor Grid - Boundary | 25m spacing along property line |
| Receptor Grid - Near Field | 200m spacing to 1 km |
| Receptor Grid - Far Field | 500m spacing to 3 km |
| Building Downwash | BPIPPRM |
| Pollutants | CO, NOx, PM10, PM2.5, SO2 |
| Averaging Periods | 1-hr, 3-hr, 8-hr, 24-hr, annual (as applicable) |
| Model Iterations | 5 (refinement history preserved) |

### Emission Sources

| Source | Equipment | Fuel | Status |
|--------|-----------|------|--------|
| Backup Generator (S2.001) | Cummins 1000 kW Tier 4 diesel | ULSD | Permitted |
| Fire Pump (S2.002) | Clarke JU6H-UFABL0, 129 kW diesel | ULSD | Permitted |
| Heating Systems (IA1.xxx) | Multiple propane units | LPG | Permitted |
| Storage Tanks | Propane storage | LPG | Permitted |
