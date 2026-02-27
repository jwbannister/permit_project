# Project Selection Process

## Objective

Select a completed Air Sciences Inc. project with a clear start-to-finish lifecycle that would be a good candidate for AI-assisted reproduction of deliverables. The ideal project should have:

- Definitive start and end dates (no ongoing or ambiguous timelines)
- Representative deliverables typical of Air Sciences' work
- Complete project files available for examination
- Sufficient complexity to be meaningful, but scoped enough to be tractable

## Methodology

### Step 1: Identify the Universe of Completed Projects

**Tool:** BQE Core API (Air Sciences' billing and project management system)

**Approach:** We built a general-purpose BQE API CLI tool (`~/system/tools/bqe/`) to query all Air Sciences project data. This tool was adapted from an existing Owens Lake project-specific BQE client and generalized for company-wide queries.

**Initial query results:**
- Total projects in BQE: **3,987**
- All retrieved projects showed `isActive: false` in the API response (BQE's `isActive` field appears to reflect something other than current activity — the `status` field is more reliable)
- Status distribution:
  - Status 0 (active): 386 projects
  - Status 4 (closed/completed): 3,600 projects
  - Status 6 (unknown): 1 project
- Unique clients: 955

**Data file:** `data/bqe_all_projects.json`

### Step 2: Filter to Recent, Completed Projects

**Criteria applied:**
1. **Started within the last 2 years** (on or after February 26, 2024) — ensures the project reflects current workflows, standards, and practices
2. **Status = 4** (closed in BQE) — indicates the project reached completion
3. **Contract amount > $0** — excludes internal/overhead projects

**Results:** 65 individual project codes matching these criteria, representing approximately $1.3M in total contract value.

**Data file:** `data/bqe_candidates.json`

### Step 3: Group Related Projects and Filter by Size

Many projects in BQE are subtasks of a larger engagement (e.g., `447-2-1` Permitting and `447-2-2` Compliance are part of the same client engagement). We grouped by parent project code and filtered to groups with >$5,000 total contract value.

**Results:** 41 project groups, ranging from $5,000 to $180,000 in contract value.

**Key project groups identified:**

| Project Group | Description | Total Contract | Manager |
|---------------|-------------|---------------|---------|
| 59-43F (6 tasks) | Carlin Complex Air Compliance/Permitting | $180,100 | Huelson |
| 134-31A | CC&V Air Permitting and Compliance | $94,430 | Steen |
| 134-31B | CC&V Air Dispersion Modeling Support | $94,900 | Steen |
| 235-17B-12 | AQIA Prefeasibility | $91,300 | Steen |
| 447-2 (2 tasks) | Keenesburg Mine Permitting + Compliance | $85,500 | Steen |
| 437-2-1 | Monitoring and Field Support | $67,340 | Bannister |
| 448-1 (5 tasks) | DRCOG Classification Algorithm + Dashboard | $52,366 | DeMarco |
| 450-2-1 | QLNG Pre-FEED Air Quality Support | $50,000 | Huelson |
| 281-25-1 | General Air Quality Support | $45,000 | Lewis |
| 270-10-1 | Workforce Hub Air Quality Permitting | $41,200 | Huelson |
| 434-6-1 | Compliance Reports | $39,220 | Gonzalez-Beltran |

### Step 4: Select Shortlist for Detailed Analysis

**Decision:** Focus on projects that represent core Air Sciences workflows — permitting, compliance, and modeling — rather than specialized or research-heavy work.

**Projects selected for detailed billing analysis:**
1. **447-2** (Keenesburg Mine) — Permitting + Compliance pair, $86K
2. **134-31A** (CC&V Permitting) — Large permitting project, $94K
3. **134-31B** (CC&V Modeling) — Dispersion modeling project, $95K
4. **450-2-1** (QLNG Pre-FEED) — Pre-FEED air quality support, $50K
5. **270-10-1** (Workforce Hub) — Air quality permitting, $41K
6. **434-6-1** (Compliance Reports) — Compliance-focused, $39K

**Rationale for this shortlist:**
- Mix of project types (permitting, modeling, compliance, pre-FEED)
- Range of sizes ($39K - $95K)
- Multiple project managers represented
- All clearly closed in BQE

### Step 5: Detailed Billing Analysis

We queried BQE for time entry data on each shortlisted project to understand:
- Actual date ranges of work performed
- Personnel involved and their roles (by hours)
- Monthly effort distribution (work intensity patterns)

**Data file:** `data/bqe_target_detail.json`

**Billing summary:**

| Project | Active Period | Hours | Personnel | Intensity Pattern |
|---------|--------------|-------|-----------|-------------------|
| 447-2-1 | Mar 2024 – Aug 2025 | 181 hrs | 7 people | Sporadic, long tail |
| 447-2-2 | Mar 2024 – Dec 2025 | 232 hrs | 8 people | Sporadic, long tail |
| 134-31A-1 | Jan 2025 – Aug 2025 | 276 hrs | 9 people | Front-loaded, Jan peak |
| 134-31B-1 | Jan 2025 – Jul 2025 | 287 hrs | 6 people | Back-loaded, Jun spike |
| 450-2-1 | Aug 2025 – Sep 2025 | 170 hrs | 5 people | Intense, 2 months |
| 270-10-1 | Nov 2024 – May 2025 | 225 hrs | 7 people | Front-loaded, Jan peak |
| 434-6-1 | Jan 2025 – Dec 2025 | 258 hrs | 4 people | One person, 98% of hours |

**Key observations:**
- **447-2** had a very long active period (21 months for a $15K compliance task) with sporadic billing — suggests ongoing/reactive work, not a clean project lifecycle
- **134-31A/B** are large but represent ongoing client relationships with CC&V (a mining operation) — hard to isolate as standalone engagements
- **434-6-1** is essentially one person's compliance work — limited team dynamics to study
- **450-2-1** is intense and short but is only a pre-FEED study with deliverables extending years into the future
- **270-10-1** has the cleanest billing profile — concentrated work, clear start/stop, reasonable team size

### Step 6: File System Review

**Decision:** Narrow to the two cleanest candidates — **270-10-1** and **450-2-1** — and examine their actual project files on the network drive.

**Project directories:**
- 270-10-1: `/Volumes/qdrive2/Projects/270-NW_Nevada_Project/10_Work Force Hub`
- 450-2-1: `/Volumes/qdrive2/Projects/450-Owl Ridge/02_Novus`

We performed a comprehensive review of both directory structures, file types, deliverable contents, and project lifecycle completeness.

### Step 7: Final Selection

**Selected: Project 270-10-1 (Work Force Hub Air Quality Permitting)**

**Reasons for selection:**

1. **Complete lifecycle.** The project covers every phase of a Class II air quality permitting engagement:
   - Project initiation and scope definition
   - Equipment specification gathering
   - Emissions inventory preparation (multiple iterations)
   - AERMOD dispersion modeling (5 model iterations, 9 pollutant scenarios)
   - Permit application form preparation
   - Technical narrative and impact report writing
   - NDEP submission and regulatory review
   - RFI response
   - Draft permit review
   - Final permit issuance (signed September 22, 2025)
   - Post-permit compliance setup (workbooks, startup notifications)

2. **Clean start and stop.** Billing ran from December 2024 to May 2025 (6 monthly invoices). The permit was issued in September 2025. No lingering charges or ambiguous scope.

3. **Dual-scenario analysis.** The project evaluated two technology options (diesel generators vs. line power), providing two complete worked examples of the same workflow with different inputs. This is valuable for understanding how the process adapts to different scenarios.

4. **Standard, repeatable workflow.** Nevada Class II AQOP applications follow a well-defined regulatory process. The forms, calculations, and modeling approach are directly applicable to similar facilities across Nevada and other states with analogous programs.

5. **Reasonable complexity.** At $41,200 and 225 hours, this is a substantial but bounded engagement — not so small as to be trivial, not so large as to be unwieldy.

6. **Complete file archive.** ~3,340 files organized in a clear directory structure, including all modeling inputs/outputs, all application forms, all correspondence, and all administrative records.

**Reasons 450-2-1 was not selected:**

1. **Incomplete lifecycle.** The QLNG project is a pre-FEED study — the actual permitting, monitoring, and modeling work extends to 2029. The deliverables produced (regulatory strategy memo, draft QAPPs) represent planning documents, not executed permits.

2. **Research-heavy, not process-heavy.** The bulk of the project files are reference documents, regulatory research, and historical precedents. While valuable, this type of work is harder to systematize into a reproducible AI workflow.

3. **Ongoing work.** The QAPPs are drafts awaiting ADEC approval, and the project has active follow-on proposals (February 2026). It's not truly "done."

## Assumptions and Limitations

1. **BQE data reflects billing, not all work.** Some project work (client meetings, informal reviews, administrative overhead) may not appear in time entries. We used billing data as a proxy for project activity timelines.

2. **Project status in BQE is approximate.** Status=4 (closed) means no more billing is expected, but doesn't guarantee all deliverables were accepted or that the project was successful. We confirmed success through the presence of a signed permit in the 270-10-1 files.

3. **We did not interview project personnel.** Our assessment of project completeness and quality is based solely on file review and billing data. The project manager (Elizabeth Huelson) and team members may have additional context about decisions, challenges, or lessons learned.

4. **Network drive availability.** Project files are on a network-attached drive (`/Volumes/qdrive2/`). Analysis depends on this drive being mounted and accessible.

5. **File readability.** Many deliverables are in Word (.docx) and Excel (.xlsx/.xlsm) format, which are binary files not directly readable by text-based tools. PDF versions of key documents were available and reviewed. Full content analysis of Word documents would require additional tooling.

6. **Scope of "reproduction."** We have not yet defined precisely what "reproduce" means — whether the AI agent needs to generate identical documents, functionally equivalent documents, or just follow the same analytical process. This will be addressed in subsequent documentation.

## Date

This analysis was performed on February 27, 2026.
