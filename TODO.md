# TODO Now

## CS372 Assignment 1: T³Benchmark Expansion (Due: January 14, 2026)

**Objective:** Expand BenchmarkT3-BucketLarge-I from 45 → 450 examples using master orchestrator architecture with subagents.

**Plan Reference:** [docs/plans/memoized-beaming-barto.md](docs/plans/memoized-beaming-barto.md)

---

## Phase 1: Setup

- [ ] Create project directory structure
  ```
  project/
  ├── orchestrator/
  ├── instructions/
  ├── generators/
  ├── validators/
  ├── categories/
  ├── output/
  └── reports/
  ```
- [ ] Write instruction files for subagent context:
  - [ ] MASTER_INSTRUCTIONS.md (overall methodology)
  - [ ] PEARL_LEVELS.md (L1/L2/L3 guidelines)
  - [ ] TRAP_TYPES.md (all trap type definitions)
  - [ ] CASE_TEMPLATE.md (JSON output format)
  - [ ] CAUSAL_STRUCTURES.md (DAG patterns guide)
- [ ] Parse original 45 cases from BenchmarkT3-BucketLarge-I.md to JSON
- [ ] Mark original cases with `is_original: true`
- [ ] Create orchestrator/config.json with target distributions

---

## Phase 2: Generator Implementation

- [ ] Implement `generators/base_generator.py` with CRIT integration
- [ ] Implement `generators/crit_evaluator.py` (quality scoring)
- [ ] Implement `generators/diversity_enforcer.py` (similarity checks)
- [ ] Implement 8 category-specific generators:
  - [ ] gen_01: Goodhart's Law (85 cases) - Scaling, RLHF, Reward Hacking
  - [ ] gen_02: Counterfactual (85 cases) - Alignment, Philosophy, Safety
  - [ ] gen_03: Conf-Med (40 cases) - Medical AI, Fairness, Security
  - [ ] gen_04: Instrumental (40 cases) - Multi-Agent, Corrigibility
  - [ ] gen_05: Selection/Spurious (55 cases) - CV, NLP, Recommenders
  - [ ] gen_06: Specification (45 cases) - Autonomous Vehicles, Game Playing
  - [ ] gen_07: Feedback Loops (30 cases) - Educational AI, Social Systems
  - [ ] gen_08: Other Traps (35 cases) - Model Compression, Prompt Eng
- [ ] Implement `orchestrator/orchestrator.py` (main coordinator)
- [ ] Run generation phase producing 405 new cases

---

## Phase 3: Validator Implementation

- [ ] Implement `validators/dag_validator.py`:
  - [ ] DAG-01: Acyclicity check
  - [ ] DAG-02: Backdoor criterion validation
  - [ ] DAG-03: Collider conditioning warning
  - [ ] DAG-04: Variable role consistency
- [ ] Implement `validators/content_validator.py` (CRIT rubric scoring)
- [ ] Implement `validators/cross_validator.py`:
  - [ ] Exact duplicate detection
  - [ ] Semantic similarity check (threshold < 0.85)
  - [ ] Distribution balance verification
- [ ] Run 8 validation batches (one per trap type category)

---

## Phase 4: Revision & Finalization

- [ ] Implement revision workflow:
  - [ ] CRITICAL failures → Regenerate
  - [ ] HIGH severity → Major revision
  - [ ] MEDIUM severity → Minor revision
  - [ ] LOW severity → Polish
- [ ] Process revision queue (max 3 cycles per case)
- [ ] Merge validated cases with original 45
- [ ] Generate `output/final/GroupI1_dataset.json` (450 cases)
- [ ] Generate `reports/analysis_report.md`

---

## Phase 5: Verification

- [ ] Validate JSON schema compliance
- [ ] Verify total count = 450
- [ ] Verify original 45 cases marked with `is_original: true`
- [ ] Check Pearl level distribution:
  - [ ] L1 (Association): 10-12%
  - [ ] L2 (Intervention): 66-70%
  - [ ] L3 (Counterfactual): 18-21%
- [ ] Confirm zero duplicates
- [ ] Check difficulty distribution (Easy/Medium/Hard balanced)
- [ ] Verify L3 ground truth distribution (~30% VALID, ~20% INVALID, ~50% CONDITIONAL)
- [ ] Manual quality review of 10% random sample

---

## Deliverables

- [ ] `GroupI1_dataset.json` - 450 cases in required JSON format
- [ ] `GroupI1_report.pdf` - Analysis report with methodology documentation
- [ ] Source code - All orchestrator, generator, and validator scripts

---

## Quality Targets

| Metric | Target |
|--------|--------|
| Mean CRIT score | ≥ 7.0 |
| Structure validation pass rate | ≥ 95% |
| DAG validity rate | ≥ 98% |
| Duplicate rate | 0% |
| First-pass validation rate | ≥ 70% |
| Revision success rate | ≥ 90% |

---

## Source References

| Source | Content |
|--------|---------|
| [docs/course/assignments/CS372_Win2026_Assignment1.md](docs/course/assignments/CS372_Win2026_Assignment1.md) | Assignment requirements |
| [docs/data/BenchmarkT3-BucketLarge-I.md](docs/data/BenchmarkT3-BucketLarge-I.md) | Original 45 cases |
| [docs/course/lectures/CS3722026-Lecture2.md](docs/course/lectures/CS3722026-Lecture2.md) | Pearl's Ladder, backdoor criterion |
| [docs/course/readings/chapter6and7.md](docs/course/readings/chapter6and7.md) | SocraSynth/EVINCE, CRIT algorithm |
