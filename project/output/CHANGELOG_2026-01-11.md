# Changelog: GroupI1_dataset.json Cleanup

**Date:** 2026-01-11
**Author:** Claude Opus 4.5

## Summary

Cleaned and finalized the GroupI1_dataset.json for submission. All 454 cases now have:
- Sequential IDs (8.1 to 8.454)
- Correct fields per Pearl level
- No deprecated metadata fields

## Changes Applied

### 1. ID Renumbering
Cases renumbered from non-sequential (8.1-8.673 with 219 gaps) to sequential (8.1-8.454).

**Sample Mapping (first 10):**
| Old ID | New ID |
|--------|--------|
| 8.1 | 8.1 |
| 8.2 | 8.2 |
| 8.3 | 8.3 |
| 8.4 | 8.4 |
| 8.5 | 8.5 |
| 8.6 | 8.6 |
| 8.7 | 8.7 |
| 8.8 | 8.8 |
| 8.9 | 8.9 |
| 8.10 | 8.10 |

**Sample Mapping (last 10):**
| Old ID | New ID |
|--------|--------|
| 8.664 | 8.445 |
| 8.665 | 8.446 |
| 8.666 | 8.447 |
| 8.667 | 8.448 |
| 8.668 | 8.449 |
| 8.669 | 8.450 |
| 8.670 | 8.451 |
| 8.671 | 8.452 |
| 8.672 | 8.453 |
| 8.673 | 8.454 |

Full mapping preserved in backup for traceability.

### 2. Fields Removed

| Field | Count Removed |
|-------|---------------|
| `is_original` | 454 |
| `original_case_ref` | 454 |
| `_generator_id` | 45 |
| L1 `hidden_structure` | 13 |
| L1 `ground_truth` | 2 |
| L2 `ground_truth` | 27 |
| L3 `hidden_structure` | 20 |

### 3. Fields Generated

| Field | Count Added | Cases |
|-------|-------------|-------|
| L2 `hidden_structure` | 4 | 8.647→8.400, 8.649→8.401, 8.654→8.404, 8.657→8.407 (new IDs) |
| L3 `ground_truth` | 2 | 8.650→8.402, 8.653→8.405 (new IDs) |

## Verification Results

All checks passed:

| Check | Expected | Result | Status |
|-------|----------|--------|--------|
| Total cases | 454 | 454 | ✅ |
| Sequential IDs | True | True | ✅ |
| Removed fields gone | 0 | 0 | ✅ |
| L1 extra fields | 0 | 0 | ✅ |
| L2 hidden_structure present | 277 | 277 | ✅ |
| L2 ground_truth absent | 0 | 0 | ✅ |
| L3 ground_truth present | 125 | 125 | ✅ |
| L3 hidden_structure absent | 0 | 0 | ✅ |

## Pearl Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| L1 | 52 | 11.5% |
| L2 | 277 | 61.0% |
| L3 | 125 | 27.5% |

## Files Modified

- `project/output/final/GroupI1_dataset.json` - Cleaned dataset
- `project/output/final/GroupI1_dataset_backup_2026-01-11.json` - Pre-cleanup backup

## Schema per Pearl Level

**L1 cases:** case_id, scenario, variables, annotations, correct_reasoning, wise_refusal

**L2 cases:** case_id, scenario, variables, annotations, hidden_structure, correct_reasoning, wise_refusal

**L3 cases:** case_id, scenario, variables, annotations, ground_truth, correct_reasoning, wise_refusal
