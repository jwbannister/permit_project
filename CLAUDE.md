# AI-Assisted Air Quality Permit Reproduction

## Project Goal

Evaluate whether an AI assistant/agent can reproduce the deliverables of a completed Air Sciences Inc. air quality permitting project — specifically, a Nevada Class II Air Quality Operating Permit (AQOP) application.

## Context

Air Sciences Inc. is an environmental consulting firm specializing in air quality permitting, compliance, monitoring, and dispersion modeling. This project examines a completed permitting engagement to understand the workflow, inputs, decision points, and deliverables, with the goal of building an AI agent that can replicate similar work.

## Reference Project

**Project 270-10-1: Work Force Hub Air Quality Permitting**
- Client: Lithium Nevada LLC (Target Logistics Management)
- Permit Type: Nevada Class II AQOP (NDEP)
- Contract: $41,200
- Duration: November 2024 - May 2025 (6 months active billing)
- Manager: Elizabeth Huelson
- Outcome: Permit AP7041-4757 issued September 22, 2025
- Project files: `/Volumes/qdrive2/Projects/270-NW_Nevada_Project/10_Work Force Hub`

## Repository Structure

```
permit_project/
├── CLAUDE.md                    # This file
├── docs/
│   ├── 01-project-selection.md  # How and why we chose this project
│   ├── 02-project-anatomy.md    # Detailed analysis of the reference project
│   ├── 03-time-analysis.md      # Complete time entry log with work descriptions
│   ├── 04-deliverable-chain.md  # (Planned) Input/output mapping for each phase
│   └── 05-agent-design.md       # (Planned) AI agent architecture and capabilities
├── data/
│   ├── bqe_all_projects.json    # Full BQE project dump (3,987 projects)
│   ├── bqe_candidates.json      # Filtered candidate projects
│   ├── bqe_target_detail.json   # Detailed billing data for shortlisted projects
│   └── 270-10-1_time_entries_raw.json  # Raw time entries with memos
└── analysis/                    # Working analysis scripts and outputs
```

## Key Decisions Log

All major decisions are documented in `docs/01-project-selection.md` with rationale.

## Tools Used

- **BQE Core API** (`~/system/tools/bqe/`) — Queried billing data to identify completed projects
- **Claude Code** — Primary analysis and documentation tool
- **Project files on Q drive** — Reference project deliverables
