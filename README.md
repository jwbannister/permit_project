# AI-Assisted Air Quality Permit Reproduction

Can an AI agent reproduce the deliverables of a completed air quality permitting project?

## What This Is

This project documents an experiment to evaluate whether an AI assistant can replicate the work product of Air Sciences Inc. — specifically, a Nevada Class II Air Quality Operating Permit (AQOP) application.

We selected a completed project (270-10-1: Work Force Hub), analyzed its structure, deliverables, and workflow, and are building toward an AI agent that can reproduce similar work given equivalent inputs.

## Why This Matters

Air quality permitting is a knowledge-intensive process that combines:
- Regulatory expertise (EPA, state agency requirements)
- Technical analysis (emissions calculations, dispersion modeling)
- Engineering data interpretation (equipment specs, fuel consumption)
- Professional document preparation (applications, narratives, reports)
- Regulatory communication (agency correspondence, RFI responses)

If an AI agent can meaningfully assist with or reproduce portions of this workflow, it has significant implications for how environmental consulting work is performed.

## Documentation

| Document | Description |
|----------|-------------|
| [01-project-selection.md](docs/01-project-selection.md) | How we identified and selected the reference project |
| [02-project-anatomy.md](docs/02-project-anatomy.md) | Detailed analysis of the reference project's structure and deliverables |
| [03-time-analysis.md](docs/03-time-analysis.md) | Complete time entry log with work descriptions and workflow reconstruction |
| [04-deliverable-chain.md](docs/04-deliverable-chain.md) | Complete input/output mapping for every deliverable |
| [05-agent-design.md](docs/05-agent-design.md) | Modular agent architecture — 8 modules with automation assessments |
| [06-success-criteria.md](docs/06-success-criteria.md) | Three-tier success definition: calculation, regulatory, generalization |

## Reference Project

**270-10-1: Work Force Hub Air Quality Permitting**
- Nevada Class II AQOP for an industrial support facility
- Contract: $41,200 | 225 hours | 6 months
- Outcome: Permit AP7041-4757 issued September 2025
- Complete lifecycle: initiation through post-permit compliance

## Status

- [x] Project selection methodology documented
- [x] Reference project anatomy documented
- [x] Time entry analysis and workflow reconstruction
- [x] Deliverable chain mapping (inputs/outputs per phase)
- [x] AI agent design specification
- [x] Success criteria defined (three tiers)
- [ ] **EI-POP prototype (in progress)** — emissions inventory population, single source (fire pump S2.002)
- [ ] Validation against reference project
- [ ] Expand to full source inventory
