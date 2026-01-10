# CS372 T3Benchmark Expansion Project

**Status:** ✅ COMPLETED (January 9, 2026)

Expanding the T3Benchmark dataset from 49 to 454 examples using a master orchestrator architecture with specialized subagents and agent-based gap filling.

## Final Results

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Total Cases | 454 | 454 | ✅ |
| Unique IDs | 100% | 100% | ✅ |
| Mean CRIT Score | ≥7.0 | 8.54 | ✅ |
| DAG Validity | ≥95% | 96.9% | ✅ |
| Duplicate Rate | 0% | 0% | ✅ |

### Pearl Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| L1 (Association) | 52 | 11.5% |
| L2 (Intervention) | 277 | 61.0% |
| L3 (Counterfactual) | 125 | 27.5% |

### Trap Type Distribution (Top 10)

| Trap Type | Count | Percentage |
|-----------|-------|------------|
| GOODHART | 93 | 20.5% |
| COUNTERFACTUAL | 91 | 20.0% |
| SELECTION_SPURIOUS | 47 | 10.4% |
| SPECIFICATION | 42 | 9.3% |
| CONF_MED | 40 | 8.8% |
| INSTRUMENTAL | 39 | 8.6% |
| FEEDBACK | 30 | 6.6% |
| CALIBRATION | 9 | 2.0% |
| TRADE_OFF | 8 | 1.8% |
| OTHER | 55 | 12.1% |

## Project Structure

```
AGI/
├── README.md                           # This file
├── TODO.md                             # Task tracking (completed)
├── docs/
│   ├── course/
│   │   ├── assignments/                # Assignment specifications
│   │   ├── lectures/                   # Lecture materials
│   │   └── readings/                   # Course readings
│   ├── data/
│   │   └── BenchmarkT3-BucketLarge-I.md  # Original 49 cases
│   └── plans/
│       ├── CURRENT_PLAN.md             # Points to active plan
│       ├── 2026-01-09-complete-454-cases-hybrid.md  # Final implementation plan
│       └── archivedPlans/              # Previous plans
├── project/
│   ├── orchestrator/
│   │   ├── orchestrator.py             # Main orchestrator script
│   │   ├── config.json                 # Configuration settings
│   │   └── progress_tracker.json       # Generation progress
│   ├── generators/
│   │   ├── base_generator.py           # Base generator class
│   │   ├── gen_01_goodhart.py          # GOODHART trap generator
│   │   ├── gen_02_counterfactual.py    # COUNTERFACTUAL trap generator
│   │   ├── gen_03_conf_med.py          # CONF_MED trap generator
│   │   ├── gen_04_instrumental.py      # INSTRUMENTAL trap generator
│   │   ├── gen_05_selection_spurious.py # SELECTION_SPURIOUS generator
│   │   ├── gen_06_specification.py     # SPECIFICATION trap generator
│   │   ├── gen_07_feedback_loops.py    # FEEDBACK loop generator
│   │   └── gen_08_other_traps.py       # Other trap types generator
│   ├── validators/
│   │   ├── content_validator.py        # CRIT score validation
│   │   ├── dag_validator.py            # DAG structure validation
│   │   └── cross_validator.py          # Duplicate/similarity detection
│   ├── instructions/
│   │   ├── MASTER_INSTRUCTIONS.md      # Generation guidelines
│   │   ├── PEARL_LEVELS.md             # Pearl's Ladder documentation
│   │   ├── TRAP_TYPES.md               # Trap type taxonomy
│   │   ├── CASE_TEMPLATE.md            # JSON case template
│   │   └── CAUSAL_STRUCTURES.md        # Causal DAG patterns
│   └── output/
│       ├── final/
│       │   └── GroupI1_dataset.json    # FINAL: 454 validated cases
│       ├── generated/                  # Batch generation outputs
│       ├── validated/                  # Post-validation cases
│       ├── agent_cases_*.json          # Agent-generated cases
│       └── analysis_report.md          # Generation analysis
└── scripts/                            # Utility scripts
```

## Assignment Overview

**Course:** CS372 - Winter 2026
**Due Date:** January 14, 2026
**Status:** ✅ COMPLETED

**Objective:** Expand BenchmarkT3-BucketLarge-I from 49 to 454 examples using:
- Master orchestrator architecture with specialized subagents
- CRIT algorithm for quality scoring
- Pearl's Ladder (L1/L2/L3) for causal reasoning levels
- DAG validation for causal structure integrity
- Agent-based writing for gap filling

## Key Concepts

| Concept | Description |
|---------|-------------|
| Pearl's Ladder | L1 (Association), L2 (Intervention), L3 (Counterfactual) |
| CRIT Algorithm | Quality scoring rubric from SocraSynth/EVINCE |
| T3 Traps | Goodhart's Law, Counterfactual, Specification Gaming, etc. |
| DAG Validation | Acyclicity, backdoor criterion, collider checks |

## Implementation Approach

### Hybrid Strategy

The final implementation used a hybrid approach:

1. **Phase 1: Bug Fixes**
   - Fixed finalization duplicate bug in orchestrator
   - Fixed schema KeyErrors in generators
   - Added placeholder detection in validators

2. **Phase 2-3: Automated Pipeline**
   - Adjusted similarity threshold to 0.75
   - Ran full pipeline → 281 cases generated

3. **Phase 4: Agent-Based Gap Filling**
   - Deployed 4 parallel agents to write remaining 173 cases
   - GOODHART: 45 cases
   - COUNTERFACTUAL: 60 cases
   - CONF_MED: 23 cases
   - MIXED (SELECTION, FEEDBACK, OTHER): 45 cases

4. **Phase 5: Final Validation**
   - Merged all cases
   - Validated uniqueness and schema compliance
   - Achieved 454 total cases

## Quick Start

### View the Final Dataset

```bash
# Count cases
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(f'Total: {len(d)} cases')"

# Verify no duplicates
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); ids=[c['case_id'] for c in d]; print(f'Unique: {len(set(ids))}/{len(ids)}')"

# Check Pearl distribution
python3 -c "import json; from collections import Counter; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(Counter(c['annotations']['pearl_level'] for c in d))"
```

### Run the Orchestrator (for regeneration)

```bash
cd project/orchestrator
python orchestrator.py --phase all
```

## Deliverables

- [x] `GroupI1_dataset.json` - 454 cases in required JSON format
- [x] `analysis_report.md` - Analysis report with methodology documentation
- [x] Source code - All orchestrator, generator, and validator scripts
- [x] Implementation plans - Documented in `docs/plans/`

## Source References

| Source | Content |
|--------|---------|
| [CS372_Win2026_Assignment1.md](docs/course/assignments/CS372_Win2026_Assignment1.md) | Assignment requirements |
| [BenchmarkT3-BucketLarge-I.md](docs/data/BenchmarkT3-BucketLarge-I.md) | Original 49 cases |
| [CS3722026-Lecture2.md](docs/course/lectures/CS3722026-Lecture2.md) | Pearl's Ladder, backdoor criterion |
| [chapter6and7.md](docs/course/readings/chapter6and7.md) | SocraSynth/EVINCE, CRIT algorithm |

## License

This project is for educational purposes as part of Stanford CS372 Winter 2026 path to AGI.
