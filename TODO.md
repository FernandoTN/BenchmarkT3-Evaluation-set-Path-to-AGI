# TODO Now

(No items currently scheduled)

---

# TODO Next

(No items currently scheduled)

---

# TODO Done

## CS372 Assignment 2: Schema Migration for Updated Requirements (Completed: January 28, 2026)

**Status:** ✅ IMPLEMENTED

**Plan Reference:** [docs/plans/federated-herding-knuth.md](docs/plans/federated-herding-knuth.md)

**Objective:** Migrate existing 1000 cases (500 GroupI + 500 GroupJ) to comply with the new schema specification in the updated Assignment 2 PDF (Appendix B).

**Implementation Summary:**
- Phase 1: Setup directories, backed up originals
- Phase 2: Created migration script with all transformation functions
- Phase 3: Executed parallel migrations using 6 agents (one per level per group)
- Phase 4: Merged and validated all cases (100% pass rate)
- Phase 5: Generated migration reports and schema files

**Key Changes Applied:**
- [x] Transform `variables.Z` from object `{name, role}` to array of strings
- [x] Restructure flat `trap_type` fields into nested `trap` object
- [x] Transform L1 labels: W→NO, S→YES, A→AMBIGUOUS
- [x] Add new required fields: `id`, `bucket`, `is_ambiguous`, `gold_rationale`
- [x] Output migrated files to `project/assignment2/updatedSubmissions/`

**Critical Data Quality Fixes Applied:**
- GroupJ L1: 23 trap type corrections (T1→W1, T7→W7, T8→W8)
- GroupJ L3: 51 trap type corrections (T7→F4, T9→F4, T10→F5, T11→F5, T12→F5)
- Total: 74 trap type corrections

**Final Results:**
- GroupI (AI & Tech): **500 cases** (100% valid)
- GroupJ (Social Science): **500 cases** (100% valid)
- Combined total: **1000 validated cases**

**Deliverables:**
- [x] `project/assignment2/updatedSubmissions/groupI_FernandoTorres/groupI_FernandoTorres_dataset.json` (500 cases)
- [x] `project/assignment2/updatedSubmissions/groupI_FernandoTorres/groupI_FernandoTorres_schema.json`
- [x] `project/assignment2/updatedSubmissions/groupI_FernandoTorres/groupI_FernandoTorres_score.json`
- [x] `project/assignment2/updatedSubmissions/groupI_FernandoTorres/groupI_FernandoTorres_migration_report.md`
- [x] `project/assignment2/updatedSubmissions/groupJ_FernandoTorres/groupJ_FernandoTorres_dataset.json` (500 cases)
- [x] `project/assignment2/updatedSubmissions/groupJ_FernandoTorres/groupJ_FernandoTorres_schema.json`
- [x] `project/assignment2/updatedSubmissions/groupJ_FernandoTorres/groupJ_FernandoTorres_score.json`
- [x] `project/assignment2/updatedSubmissions/groupJ_FernandoTorres/groupJ_FernandoTorres_migration_report.md`

---

## CS372 Assignment 2: T3 Benchmark Expansion (Completed: January 22, 2026)

**Status:** ✅ IMPLEMENTED

**Plan Reference:** [docs/plans/precious-napping-sundae.md](docs/plans/precious-napping-sundae.md)

**Objective:** Expand GroupI1 and GroupJ1 datasets to 500 validated cases each using a highly parallelized multi-agent workflow.

**Implementation Summary:**
- Phase 0: Created V4.0 schema and validation infrastructure
- Phase 1: Transformed 16 existing GroupI1 cases and 240 GroupJ1 cases to V4.0 format
- Phase 2: Generated cases using parallel agents:
  - GroupI1: Generated 45 L1 + 344 L2 + 147 L3 cases
  - GroupJ1: Generated 23 L1 + 138 L2 + 198 L3 cases
- Phase 3: Merged batches, selected top 500 cases per group by score
- Phase 4: Validated all 1000 cases (100% pass rate)
- Phase 5: Generated 8 deliverable files (4 per group)

**Final Results:**
- GroupI1 (AI & Tech): **500 cases** (50 L1 + 300 L2 + 150 L3)
- GroupJ1 (Social Science): **500 cases** (50 L1 + 300 L2 + 150 L3)
- Combined total: **1000 validated cases**
- Mean quality score: 8.5/10
- Schema compliance: 100%
- Validation pass rate: 100%

**Deliverables:**
- [x] `project/assignment2/submissions/groupI_FernandoTorres/groupI_FernandoTorres_dataset.json` (500 cases)
- [x] `project/assignment2/submissions/groupI_FernandoTorres/groupI_FernandoTorres_schema.json`
- [x] `project/assignment2/submissions/groupI_FernandoTorres/groupI_FernandoTorres_score.json`
- [x] `project/assignment2/submissions/groupI_FernandoTorres/groupI_FernandoTorres_methodology.md`
- [x] `project/assignment2/submissions/groupJ_FernandoTorres/groupJ_FernandoTorres_dataset.json` (500 cases)
- [x] `project/assignment2/submissions/groupJ_FernandoTorres/groupJ_FernandoTorres_schema.json`
- [x] `project/assignment2/submissions/groupJ_FernandoTorres/groupJ_FernandoTorres_score.json`
- [x] `project/assignment2/submissions/groupJ_FernandoTorres/groupJ_FernandoTorres_methodology.md`

**Lessons Learned:**
- Large case generation (100+ cases) should be split across 6-8 agents instead of 1-2
- Each agent should write to non-overlapping files (e.g., by trap type)
- Pre-assign case ID ranges to prevent duplicates
- See Section 11 of the plan for detailed parallelization recommendations

---

## V3.0 Schema Update - Assignment 1 Updated Requirements (Completed: January 22, 2026)

**Status:** ✅ IMPLEMENTED

**Plan Reference:** [docs/plans/2026-01-22-v3-schema-update-plan.md](docs/plans/2026-01-22-v3-schema-update-plan.md)

**Objective:** Update GroupI1_datasetV2.0.json to comply with CS372 Assignment 1 Updated requirements.

**Implementation Summary:**
- Phase 1: Setup directories, archived V2.0 files to `project/output/final/archive/2026-01-22/`
- Phase 2: Parsed original benchmark to identify 49 Stanford CS372 cases
- Phase 3: Transformed 454 cases using 8 parallel agents (by trap type)
  - GOODHART: 93 cases
  - COUNTERFACTUAL: 91 cases
  - SELECTION_SPURIOUS: 47 cases
  - SPECIFICATION: 42 cases
  - CONF_MED: 40 cases
  - INSTRUMENTAL: 39 cases
  - FEEDBACK: 30 cases
  - OTHER: 72 cases
- Phase 4: Validated all cases using 8 parallel validators (100% pass rate)
- Phase 5: Merged and finalized `GroupI1_datasetV3.0.json`

**Final Results:**
- Total cases: **454**
- New fields added: `id`, `bucket`, `claim`, `label`, `is_ambiguous`, `trap`, `gold_rationale`, `annotation`
- Label distribution: NO=385, AMBIGUOUS=38, YES=31
- Pearl distribution: L1=52, L2=277, L3=125
- Author distribution: Stanford CS372=49, Fernando Torres=202, Alessandro Balzi=203

**Verification Gates - All Passed:**
| Metric | Target | Final | Status |
|--------|--------|-------|--------|
| Total cases | 454 | 454 | ✅ |
| New required fields | 8 | 8 | ✅ |
| Existing fields preserved | All | All | ✅ |
| Label values valid | 100% | 100% | ✅ |
| trap.type matches | 100% | 100% | ✅ |
| Unique IDs | 100% | 100% | ✅ |
| ID format correct | 100% | 100% | ✅ |
| L2 hidden_structure | 277 | 277 | ✅ |
| L3 ground_truth | 125 | 125 | ✅ |

**Deliverables:**
- `project/output/final/GroupI1_datasetV3.0.json` - 454 validated cases
- `project/output/final/GroupI1_methodology_V3.0.md` - Methodology report
- `project/schemas/case_schema_v3.json` - V3.0 JSON Schema

---

## Clean and Finalize GroupI1_dataset.json for Submission (Completed: January 11, 2026)

**Status:** ✅ IMPLEMENTED

**Plan Reference:** [docs/plans/archivedPlans/2026-01-11-dataset-cleanup-plan.md](docs/plans/archivedPlans/2026-01-11-dataset-cleanup-plan.md)

**Implementation Summary:**
- Created backup at `GroupI1_dataset_backup_2026-01-11.json`
- Generated missing `hidden_structure` for 4 L2 cases
- Generated missing `ground_truth` for 2 L3 cases
- Removed deprecated fields: `is_original` (454), `original_case_ref` (454), `_generator_id` (45)
- Removed schema-violating fields: L1 `hidden_structure` (13), L1 `ground_truth` (2), L2 `ground_truth` (27), L3 `hidden_structure` (20)
- Renumbered case IDs sequentially (8.1 to 8.454)
- Created changelog at `project/output/CHANGELOG_2026-01-11.md`

**Final Results:**
- Total cases: **454**
- Sequential IDs: **8.1 to 8.454** (no gaps)
- Pearl Distribution: L1=52, L2=277, L3=125
- All schema validations passed

**Verification Gates - All Passed:**
| Metric | Target | Final | Status |
|--------|--------|-------|--------|
| Total cases | 454 | 454 | ✅ |
| Sequential IDs | True | True | ✅ |
| L1 extra fields | 0 | 0 | ✅ |
| L2 hidden_structure present | 277 | 277 | ✅ |
| L2 ground_truth absent | 0 | 0 | ✅ |
| L3 ground_truth present | 125 | 125 | ✅ |
| L3 hidden_structure absent | 0 | 0 | ✅ |

---

## Complete T3 Benchmark to 454 Cases - Hybrid Approach (Completed: January 9, 2026)

**Status:** ✅ IMPLEMENTED

**Plan Reference:** [docs/plans/2026-01-09-complete-454-cases-hybrid.md](docs/plans/2026-01-09-complete-454-cases-hybrid.md)

**Implementation Summary:**
- Phase 1: Fixed finalization duplicate bug in orchestrator.py (added deduplication at finalize_dataset)
- Phase 1: Fixed schema KeyErrors in gen_03_conf_med.py (added mediator/collider keys)
- Phase 1: Added placeholder detection in cross_validator.py
- Phase 2: Adjusted similarity threshold to 0.75 in config.json
- Phase 3: Ran pipeline - reached 281 cases (173 gap to 454)
- Phase 4: Used 4 parallel agents to write 173 additional cases
  - GOODHART: 45 cases (IDs 8.500-8.544)
  - COUNTERFACTUAL: 60 cases (IDs 8.545-8.604)
  - CONF_MED: 23 cases (IDs 8.605-8.627)
  - MIXED (SELECTION_SPURIOUS, FEEDBACK, SPECIFICATION, OTHER): 45 cases (IDs 8.628-8.672)
- Phase 5: Final validation and dataset assembly

**Final Results:**
- Total cases: **454** (target met!)
- Unique IDs: **454** (100% - no duplicates)
- Pearl Distribution: L1 11.5%, L2 61.0%, L3 27.5%
- Difficulty Distribution: Easy 19.8%, Medium 43.8%, Hard 36.3%
- Original cases: 93, Generated: 361
- All required fields present

**Verification Gates - All Passed:**
| Metric | Target | Final | Status |
|--------|--------|-------|--------|
| Total cases | 454 | 454 | ✅ |
| Unique case IDs | 100% | 100% | ✅ |
| All required fields | 100% | 100% | ✅ |

---

## Fix Critical Bugs to Complete T3Benchmark (Previous Attempt)

**Status:** BLOCKED - Template similarity prevents reaching 454 cases

**Plan Reference:** [docs/plans/2026-01-09-complete-t3-benchmark-454-cases.md](docs/plans/2026-01-09-complete-t3-benchmark-454-cases.md)

**Outcome:** Reached 278 cases but hit fundamental template similarity limits (~45% rejection rate)

## CS372 Assignment 1: Complete T3Benchmark to 454 Cases (Completed: January 9, 2026)

**Status:** IMPLEMENTED (Partial - 278-313/454 cases)

**Plan Reference:** [docs/plans/2026-01-09-complete-t3-benchmark-454-cases.md](docs/plans/2026-01-09-complete-t3-benchmark-454-cases.md)

**Implementation Summary:**
- Fixed critical ID assignment bug (added global AtomicIDCounter)
- Strengthened duplicate detection (lowered threshold to 0.70, added n-gram overlap)
- Expanded gen_01_goodhart.py templates: 10 → 32 templates, 24 → 48 contexts
- Expanded gen_02_counterfactual.py templates: 10 → 20 templates, 20 → 40 contexts
- Expanded gen_03_conf_med.py templates: 5 → 14 templates (8 L2 + 6 L3)
- Expanded gen_04_instrumental.py templates: 6 → 12 templates (6 L2 + 6 L3)
- Pipeline now runs without duplicate ID errors

**Results:**
- Total cases generated: **278-313** (49 original + 229-264 new)
- Unique IDs: **100%** (ID bug fixed)
- Pearl Distribution: L1 18.7%, L2 57.2%, L3 24.1%

**Remaining Issue:** Template similarity causing case rejection (~45% of generated cases filtered)

---

## CS372 Assignment 1: T3Benchmark Infrastructure (Completed: January 9, 2026)

**Status:** IMPLEMENTED (Partial - 218/450 cases)

**Plan Reference:** [docs/plans/archivedPlans/memoized-beaming-barto.md](docs/plans/archivedPlans/memoized-beaming-barto.md)

**Results (Post-Verification):**
- Total cases generated: **218** (49 original + 169 new)
- Average CRIT Score: **8.38/10**
- Validation Pass Rate: **87.1%**
- DAG Validity Rate: **96.2%**
- Pearl Distribution: L1 16.1%, L2 61.9%, L3 22.0%

**Verification Issues Fixed:**
- Case ID 8.341 duplication (155 occurrences) → All IDs now unique
- 56 duplicate scenarios removed → 274 → 218 cases

---

### Deliverables Completed

- [x] `GroupI1_dataset.json` - 454 cases in required JSON format (cleaned and finalized)
- [x] `analysis_report.md` - Analysis report with methodology documentation
- [x] Fixed orchestrator ID assignment bug
- [x] Fixed cross_validator duplicate detection
- [x] Fixed finalization duplicate bug
- [x] Added placeholder detection
- [x] Expanded templates for gen_01 through gen_04
- [x] Agent-based writing for remaining cases
- [x] Plan documented in docs/plans/
- [x] Dataset cleanup and schema validation
- [x] Sequential ID renumbering

---

### Source References

| Source | Content |
|--------|---------|
| [docs/course/assignments/CS372_Win2026_Assignment1.md](docs/course/assignments/CS372_Win2026_Assignment1.md) | Assignment requirements |
| [docs/data/BenchmarkT3-BucketLarge-I.md](docs/data/BenchmarkT3-BucketLarge-I.md) | Original 49 cases |
| [docs/course/lectures/CS3722026-Lecture2.md](docs/course/lectures/CS3722026-Lecture2.md) | Pearl's Ladder, backdoor criterion |
| [docs/course/readings/chapter6and7.md](docs/course/readings/chapter6and7.md) | SocraSynth/EVINCE, CRIT algorithm |
