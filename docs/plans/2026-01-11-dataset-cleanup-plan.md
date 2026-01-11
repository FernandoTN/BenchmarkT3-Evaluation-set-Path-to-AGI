# Plan: Clean and Finalize GroupI1_dataset.json

**Status:** ✅ IMPLEMENTED - Ready for Final Review

**Implementation Date:** 2026-01-11

## Objective
Create a deliverable final JSON file from `project/output/final/GroupI1_dataset.json` with the following fixes:
1. Renumber all case IDs to be sequential (8.1 to 8.454)
2. Remove unnecessary fields: `is_original`, `original_case_ref`, `_generator_id`
3. Ensure `hidden_structure` is present for L2 cases and `ground_truth` for L3 cases
4. Update documentation to trace the changes

## Current State Analysis
- **Total cases**: 454
- **Current ID range**: 8.1 to 8.673 (with 219 gaps)
- **Fields to remove**: `is_original` (454), `original_case_ref` (454), `_generator_id` (45)
- **Pearl distribution**: L1=52, L2=277, L3=125

### Edge Cases Identified
| Issue | Count | Case IDs |
|-------|-------|----------|
| L2 cases missing `hidden_structure` | 4 | 8.647, 8.649, 8.654, 8.657 |
| L3 cases missing `ground_truth` | 2 | 8.650, 8.653 |
| L1 cases with extra `hidden_structure` | 13 | 8.127, 8.145, 8.146, 8.149, 8.455, 8.621-8.624, 8.661, 8.666, 8.669, 8.671 |
| L1 cases with extra `ground_truth` | 2 | 8.144, 8.500 |

## Implementation Steps

### Step 1: Backup and Verification
1. Create backup of current `GroupI1_dataset.json` to `GroupI1_dataset_backup_2026-01-11.json`
2. Verify current dataset statistics:
   - Count total cases (expected: 454)
   - Verify Pearl level distribution
   - Document current ID range and gaps

### Step 2: Generate Missing Required Fields (Agent Task)
Use specialized agents to analyze and generate missing content for 6 cases:

**L2 cases missing `hidden_structure` (4 cases):**
- 8.647, 8.649, 8.654, 8.657
- Agent reads scenario, variables, causal_structure, key_insight
- Agent generates appropriate `hidden_structure` explaining the causal mechanism

**L3 cases missing `ground_truth` (2 cases):**
- 8.650, 8.653
- Agent reads scenario, variables, correct_reasoning, wise_refusal
- Agent generates `ground_truth` with verdict (VALID/INVALID/CONDITIONAL) and justification

### Step 3: Clean Fields by Pearl Level
**L1 cases (52 total):**
- REMOVE `hidden_structure` from 13 cases: 8.127, 8.145, 8.146, 8.149, 8.455, 8.621-8.624, 8.661, 8.666, 8.669, 8.671
- REMOVE `ground_truth` from 2 cases: 8.144, 8.500

**All cases:**
- REMOVE `is_original` (454 cases)
- REMOVE `original_case_ref` (454 cases)
- REMOVE `_generator_id` (45 cases)

### Step 4: Renumber Case IDs Sequentially
1. Sort cases by current numeric ID (8.1, 8.2, ..., 8.673)
2. Assign new sequential IDs: 8.1, 8.2, 8.3, ..., 8.454
3. Create mapping of old_id -> new_id for traceability

### Step 5: Verification
Run verification checks:
```bash
# Count cases
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(f'Total: {len(d)}')"
# Expected: 454

# Verify sequential IDs
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); ids=[c['case_id'] for c in d]; expected=['8.'+str(i) for i in range(1,455)]; print('Sequential:', ids==expected)"
# Expected: True

# Verify removed fields are gone
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); bad=[c['case_id'] for c in d if 'is_original' in c or 'original_case_ref' in c or '_generator_id' in c]; print('Cases with removed fields:', len(bad))"
# Expected: 0

# Verify L1 cases do NOT have hidden_structure or ground_truth
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); l1_bad=[c['case_id'] for c in d if c['annotations']['pearl_level']=='L1' and ('hidden_structure' in c or 'ground_truth' in c)]; print('L1 with extra fields:', len(l1_bad))"
# Expected: 0

# Verify L2 cases have hidden_structure
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); l2_missing=[c['case_id'] for c in d if c['annotations']['pearl_level']=='L2' and 'hidden_structure' not in c]; print('L2 missing hidden_structure:', len(l2_missing))"
# Expected: 0

# Verify L3 cases have ground_truth
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); l3_missing=[c['case_id'] for c in d if c['annotations']['pearl_level']=='L3' and 'ground_truth' not in c]; print('L3 missing ground_truth:', len(l3_missing))"
# Expected: 0
```

### Step 6: Update Documentation
1. Create a changelog entry in `project/output/` documenting:
   - Date of changes
   - ID renumbering mapping (summary)
   - Fields removed
   - Fields generated for missing cases
   - Validation results

## Files Modified
- `project/output/final/GroupI1_dataset.json` - Main dataset (cleaned)
- `project/output/final/GroupI1_dataset_backup_2026-01-11.json` - Backup (new)
- `project/output/CHANGELOG_2026-01-11.md` - Change documentation (new)

## Expected Final Schema per Case
```json
{
  "case_id": "8.X",           // Sequential from 8.1 to 8.454
  "scenario": "...",
  "variables": {...},
  "annotations": {
    "pearl_level": "L1|L2|L3",
    "domain": "D8",
    "trap_type": "...",
    "trap_subtype": "...",
    "difficulty": "Easy|Medium|Hard",
    "subdomain": "...",
    "causal_structure": "...",
    "key_insight": "..."
  },
  "hidden_structure": "...",    // Only for L2
  "ground_truth": {...},        // Only for L3
  "correct_reasoning": [...],
  "wise_refusal": "..."
}
```

## Risk Mitigation
- Backup created before any modifications
- ID mapping preserved for traceability
- Validation checks run after each step
- All changes documented in changelog

---

## Implementation Results

### Checklist Status

- [x] **Step 1:** Backup created at `GroupI1_dataset_backup_2026-01-11.json`
- [x] **Step 2:** Generated missing fields for 6 cases
  - [x] 4 L2 cases: hidden_structure generated
  - [x] 2 L3 cases: ground_truth generated (verdict: INVALID for both)
- [x] **Step 3:** Cleaned fields by Pearl level
  - [x] Removed hidden_structure from 13 L1 cases
  - [x] Removed ground_truth from 2 L1 cases
  - [x] Removed is_original from 454 cases
  - [x] Removed original_case_ref from 454 cases
  - [x] Removed _generator_id from 45 cases
- [x] **Step 4:** Renumbered IDs from 8.1-8.673 (219 gaps) to 8.1-8.454 (sequential)
- [x] **Step 5:** All verification checks passed
- [x] **Step 6:** Changelog created at `project/output/CHANGELOG_2026-01-11.md`

### Verification Results

| Check | Expected | Result | Status |
|-------|----------|--------|--------|
| Total cases | 454 | 454 | ✅ |
| Sequential IDs | True | True | ✅ |
| Removed fields gone | 0 | 0 | ✅ |
| L1 extra fields | 0 | 0 | ✅ |
| L2 hidden_structure present | 277 | 277 | ✅ |
| L3 ground_truth present | 125 | 125 | ✅ |

### Files Created/Modified

| File | Action |
|------|--------|
| `project/output/final/GroupI1_dataset.json` | Modified (cleaned) |
| `project/output/final/GroupI1_dataset_backup_2026-01-11.json` | Created (backup) |
| `project/output/CHANGELOG_2026-01-11.md` | Created (documentation) |

---

## Review Findings / Fixes

**Review Round 1** (Post-implementation validation by reviewer agents)

The original plan analysis was incomplete. Additional schema violations were discovered:

| Issue | Count | Action |
|-------|-------|--------|
| L2 cases with forbidden `ground_truth` | 27 | Removed |
| L3 cases with forbidden `hidden_structure` | 20 | Removed |
| Cases with non-X/Y/Z variable names | 9 | Kept (original cases use alternative naming) |

**Root cause:** The original analysis only checked L1 cases for extra fields, but did not verify that L2 cases lacked `ground_truth` and L3 cases lacked `hidden_structure`.

**Resolution:** Applied additional cleanup to remove cross-level field contamination. All verification checks now pass.

### Final Verification Results (Post-Fix)

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
