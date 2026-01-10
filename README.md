# CS372 T3Benchmark Expansion Project

Expanding the T3Benchmark dataset from 45 to 450 examples using a master orchestrator architecture with subagents.

## Project Structure

```
AGI/
├── README.md                    # This file
├── TODO.md                      # Task tracking and progress
├── docs/
│   ├── course/
│   │   ├── assignments/         # Assignment specifications
│   │   │   ├── CS372_Win2026_Assignment1.md
│   │   │   └── CS372_Win2026_Assignment1.pdf
│   │   ├── lectures/            # Lecture materials
│   │   │   ├── CS3722026-Lecture2.md
│   │   │   ├── CS3722026-Lecture2.pdf
│   │   │   └── lecture2slidesSummary.pdf
│   │   └── readings/            # Course readings
│   │       ├── chapter6and7.md
│   │       ├── chapter6and7.pdf
│   │       └── chapter6and7Summary.pdf
│   ├── data/                    # Benchmark data
│   │   ├── BenchmarkT3-BucketLarge-I.md
│   │   └── BenchmarkT3-BucketLarge-I.pdf
│   └── plans/                   # Implementation plans
│       └── memoized-beaming-barto.md
└── scripts/                     # Utility scripts
    ├── pdf_to_markdown.py
    └── pdf_to_markdown_v2.py
```

## Assignment Overview

**Course:** CS372 - Winter 2026
**Due Date:** January 14, 2026

**Objective:** Expand BenchmarkT3-BucketLarge-I from 45 to 450 examples using:
- Master orchestrator architecture with specialized subagents
- CRIT algorithm for quality scoring
- Pearl's Ladder (L1/L2/L3) for causal reasoning levels
- DAG validation for causal structure integrity

## Key Concepts

| Concept | Description |
|---------|-------------|
| Pearl's Ladder | L1 (Association), L2 (Intervention), L3 (Counterfactual) |
| CRIT Algorithm | Quality scoring rubric from SocraSynth/EVINCE |
| T3 Traps | Goodhart's Law, Counterfactual, Specification Gaming, etc. |
| DAG Validation | Acyclicity, backdoor criterion, collider checks |

## Quality Targets

| Metric | Target |
|--------|--------|
| Mean CRIT score | >= 7.0 |
| Structure validation pass rate | >= 95% |
| DAG validity rate | >= 98% |
| Duplicate rate | 0% |

## Getting Started

1. Review the [assignment requirements](docs/course/assignments/CS372_Win2026_Assignment1.md)
2. Study the [original 45 cases](docs/data/BenchmarkT3-BucketLarge-I.md)
3. Check the [implementation plan](docs/plans/memoized-beaming-barto.md)
4. Track progress in [TODO.md](TODO.md)

## Deliverables

- `GroupI1_dataset.json` - 450 cases in required JSON format
- `GroupI1_report.pdf` - Analysis report with methodology documentation
- Source code - All orchestrator, generator, and validator scripts
