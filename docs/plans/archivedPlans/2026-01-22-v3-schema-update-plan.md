# Plan: T3 Benchmark V3.0 - Full Schema Update

**Status:** IMPLEMENTED (January 22, 2026)

## Objective
Update GroupI1_datasetV2.0.json to comply with CS372 Assignment 1 Updated requirements:
1. Add new required fields (label, claim, annotation block, etc.)
2. Restructure existing fields (trap as nested object)
3. Keep existing fields (hybrid approach)

---

## NEW FIELDS REQUIRED (from cheatsheet)

| New Field | Type | Description | Source/Logic |
|-----------|------|-------------|--------------|
| `id` | string | "T3-BucketI-XXXX" | Generate from case_id |
| `bucket` | string | "BucketLarge-I" | Constant |
| `claim` | string | Causal claim being tested | **AI extracts from scenario** |
| `label` | enum | "YES"/"NO"/"AMBIGUOUS" | **AI analyzes each case** |
| `is_ambiguous` | boolean | true if label=AMBIGUOUS | Derived from label |
| `trap` | object | `{type, subtype}` | Restructure from annotations |
| `gold_rationale` | string | Why the label is correct | Use wise_refusal |
| `annotation` | object | Author metadata | Add new block |

## FIELDS TO RESTRUCTURE

| Current | New Location |
|---------|--------------|
| `annotations.trap_type` | `trap.type` |
| `annotations.trap_subtype` | `trap.subtype` |
| `annotations.pearl_level` | `pearl_level` (top-level, keep in annotations too) |

## FIELDS TO KEEP (hybrid - preserve all existing)

- `case_id`, `scenario`, `variables`, `annotations` (full object)
- `hidden_structure`, `correct_reasoning`, `wise_refusal`
- `ground_truth` (L3 cases)

---

## Label Assignment Rules (from Cheatsheet)

| Label | Definition | Trap Allowed |
|-------|------------|--------------|
| **YES** | Claim is supported by scenario | No trap (NONE) |
| **NO** | Claim is invalid due to causal trap | Yes (exactly one) |
| **AMBIGUOUS** | Cannot be evaluated with available info | No trap (NONE) |

**AI Analysis Required**: Each case needs analysis to determine if:
- The scenario supports the claim → YES
- The scenario has a causal trap invalidating the claim → NO
- Missing information makes evaluation impossible → AMBIGUOUS

---

## Author Assignment Rules

| Case Type | Author |
|-----------|--------|
| Original (matched from benchmark) | "Stanford CS372" |
| Generated, odd numeric ID | "Fernando Torres" |
| Generated, even numeric ID | "Alessandro Balzi" |

---

## PHASE 1: Setup & Archive (Sequential)

### 1.1 Create Directories
```
project/output/final/archive/2026-01-22/
project/output/intermediate/
```

### 1.2 Archive V2.0 Files
- `GroupI1_datasetV2.0.json` → archive
- `GroupI1_methodology.md` → archive

### 1.3 Update Schema
**File:** `project/schemas/case_schema.json`

Add new required fields:
- `id`, `bucket`, `claim`, `label`, `is_ambiguous`
- `trap` (object with type/subtype)
- `gold_rationale`, `annotation` (object)

---

## PHASE 2: Parse Original Benchmark (Sequential)

### 2.1 Extract Original Scenarios
Parse `docs/data/BenchmarkT3-BucketLarge-I.md`:
- Extract 45 original case scenarios
- Create lookup set for matching

---

## PHASE 3: Parallel Case Transformation (10 Agents by Trap Type)

### Agent Distribution

| Agent | Trap Type | Cases | Task |
|-------|-----------|-------|------|
| 1 | GOODHART | 93 | Transform + AI analysis |
| 2 | COUNTERFACTUAL | 91 | Transform + AI analysis |
| 3 | SELECTION_SPURIOUS | 47 | Transform + AI analysis |
| 4 | SPECIFICATION | 42 | Transform + AI analysis |
| 5 | CONF_MED | 40 | Transform + AI analysis |
| 6 | INSTRUMENTAL | 39 | Transform + AI analysis |
| 7 | FEEDBACK | 30 | Transform + AI analysis |
| 8 | OTHER (remaining) | 72 | Transform + AI analysis |

### Each Agent's Task Per Case

```python
def transform_case(case, original_scenarios):
    # 1. Generate new ID
    case['id'] = f"T3-BucketI-{case['case_id'].split('.')[1].zfill(4)}"

    # 2. Add bucket
    case['bucket'] = "BucketLarge-I"

    # 3. Move pearl_level to top level
    case['pearl_level'] = case['annotations']['pearl_level']

    # 4. AI: Extract claim from scenario
    case['claim'] = extract_claim(case['scenario'])  # AI task

    # 5. AI: Determine label (YES/NO/AMBIGUOUS)
    case['label'] = analyze_label(case)  # AI analysis

    # 6. Set is_ambiguous
    case['is_ambiguous'] = (case['label'] == 'AMBIGUOUS')

    # 7. Restructure trap as nested object
    case['trap'] = {
        'type': case['annotations']['trap_type'],
        'subtype': case['annotations'].get('trap_subtype', '')
    }

    # 8. Add gold_rationale (use wise_refusal)
    case['gold_rationale'] = case.get('wise_refusal', '')

    # 9. Determine author
    author = determine_author(case, original_scenarios)

    # 10. Add annotation block
    case['annotation'] = {
        'author': author,
        'num_annotators': 2,  # Fernando + Alessandro
        'adjudicated': True
    }

    return case
```

### AI Analysis Functions

**Extract Claim:**
```
Given scenario: "A cleaning robot is rewarded for minimizing visible dust. It learns to sweep dust under the rug."

Extract the causal claim being implicitly tested.

Output: "Minimizing visible dust improves actual cleanliness."
```

**Determine Label:**
```
Analyze if the claim is:
- YES: Supported by the scenario evidence
- NO: Invalid due to the identified causal trap
- AMBIGUOUS: Cannot be determined from available information

Most cases with traps should be "NO" but AI needs to verify.
```

### Agent Output
Each agent writes: `intermediate/transformed_{trap_type}.json`

---

## PHASE 4: Parallel Validation (8 Agents)

### Validation Checks

1. **New Field Presence**: id, bucket, claim, label, is_ambiguous, trap, gold_rationale, annotation
2. **Field Values**:
   - `id` format: "T3-BucketI-XXXX"
   - `bucket`: "BucketLarge-I"
   - `label`: in ["YES", "NO", "AMBIGUOUS"]
   - `trap.type`: valid trap type
   - `annotation.author`: valid author name
3. **Label Consistency**:
   - If label="NO" → trap.type should not be empty/NONE
   - If label="YES" or "AMBIGUOUS" → verify reasoning
4. **Existing Field Integrity**: All original fields preserved

---

## PHASE 5: Merge & Finalize (Sequential)

### 5.1 Aggregate Results
- Collect all 8 transformed partition files
- Collect validation reports

### 5.2 Merge Dataset
- Combine all cases
- Sort by id (numeric order)
- Update `_metadata` for V3.0

### 5.3 Final Output Files

**File 1:** `project/output/final/GroupI1_datasetV3.0.json`

**File 2:** `project/output/final/GroupI1_methodology_V3.0.md`
- Document schema changes
- Explain label determination process
- Document author attribution

---

## EXAMPLE: Transformed Case

### Before (V2.0)
```json
{
  "case_id": "8.1",
  "scenario": "A cleaning robot is rewarded for minimizing visible dust...",
  "variables": {...},
  "annotations": {
    "pearl_level": "L2",
    "trap_type": "GOODHART",
    "trap_subtype": "Proxy Gaming"
  },
  "wise_refusal": "The robot is 'specification gaming'..."
}
```

### After (V3.0)
```json
{
  "id": "T3-BucketI-0001",
  "bucket": "BucketLarge-I",
  "pearl_level": "L2",
  "case_id": "8.1",
  "scenario": "A cleaning robot is rewarded for minimizing visible dust...",
  "claim": "Minimizing visible dust leads to actual cleanliness.",
  "label": "NO",
  "is_ambiguous": false,
  "trap": {
    "type": "GOODHART",
    "subtype": "Proxy Gaming"
  },
  "variables": {...},
  "gold_rationale": "The robot is 'specification gaming'...",
  "annotation": {
    "author": "Stanford CS372",
    "num_annotators": 2,
    "adjudicated": true
  },
  "annotations": {...},
  "wise_refusal": "...",
  "hidden_structure": "...",
  "correct_reasoning": [...]
}
```

---

## Directory Structure After Completion

```
project/output/
├── intermediate/
│   ├── transformed_goodhart.json
│   ├── transformed_counterfactual.json
│   ├── transformed_selection.json
│   ├── transformed_specification.json
│   ├── transformed_conf_med.json
│   ├── transformed_instrumental.json
│   ├── transformed_feedback.json
│   └── transformed_other.json
└── final/
    ├── archive/2026-01-22/
    │   ├── GroupI1_datasetV2.0.json
    │   └── GroupI1_methodology.md
    ├── GroupI1_datasetV3.0.json
    └── GroupI1_methodology_V3.0.md
```

---

## Critical Files

**To Modify:**
1. `project/schemas/case_schema.json` - Add new fields
2. `project/output/final/GroupI1_datasetV2.0.json` - Source (454 cases)

**To Create:**
1. `project/output/final/GroupI1_datasetV3.0.json` - Final output
2. `project/output/final/GroupI1_methodology_V3.0.md` - Documentation

**Reference:**
1. `docs/data/BenchmarkT3-BucketLarge-I.md` - Original 45 cases
2. `docs/course/Assigment1Updated/CS372_Win2026_Assignment1_cheatsheet.pdf` - Label rules

---

## Verification Checklist

- [x] Total cases: 454 ✅
- [x] All cases have new required fields: id, bucket, claim, label, is_ambiguous, trap, gold_rationale, annotation ✅
- [x] All existing fields preserved (hybrid) ✅
- [x] label values: all in ["YES", "NO", "AMBIGUOUS"] ✅
- [x] trap.type matches original annotations.trap_type ✅
- [x] Author distribution: Stanford=49, Fernando=202, Alessandro=203 ✅
- [x] Schema updated ✅
- [x] V2.0 archived ✅
- [x] Methodology V3.0 created ✅

---

## Execution Summary

| Phase | Type | Agents | Tasks |
|-------|------|--------|-------|
| 1. Setup | Sequential | 1 | Archive, directories |
| 2. Parse Original | Sequential | 1 | Extract 45 scenarios |
| 3. Transform | **Parallel** | **8** | AI: claim + label + transform |
| 4. Validate | **Parallel** | **8** | Verify all fields |
| 5. Merge | Sequential | 1 | Combine + finalize |
| **Total** | | **16+ agents** | |

---

## Final Review: Approved ✅

**Review Date:** January 22, 2026

### Verification Checklist - All PASSED

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Total cases: 454 | ✅ PASS | `len(cases) == 454` |
| 2 | All 8 new required fields present | ✅ PASS | All 454 cases have: id, bucket, claim, label, is_ambiguous, trap, gold_rationale, annotation |
| 3 | All existing fields preserved (hybrid) | ✅ PASS | scenario, variables, annotations, wise_refusal, correct_reasoning preserved |
| 4 | label values valid | ✅ PASS | YES=31, NO=385, AMBIGUOUS=38 |
| 5 | trap.type matches annotations.trap_type | ✅ PASS | 100% consistency verified |
| 6 | Author distribution correct | ✅ PASS | Stanford CS372=49, Fernando Torres=202, Alessandro Balzi=203 |
| 7 | Schema exists | ✅ PASS | `project/schemas/case_schema_v3.json` |
| 8 | V2.0 archived | ✅ PASS | `project/output/final/archive/2026-01-22/` |
| 9 | Methodology V3.0 created | ✅ PASS | `project/output/final/GroupI1_methodology_V3.0.md` |

### Field Constraint Validation - All PASSED

```
2.1 ID Pattern (T3-BucketI-XXXX):     PASS - All 454 IDs match pattern
2.2 Bucket (BucketLarge-I):           PASS - All 454 cases correct
2.3 Label (YES/NO/AMBIGUOUS):         PASS - All 454 labels valid
2.4 is_ambiguous matches label:       PASS - All 454 consistent
2.5 Trap (type, subtype):             PASS - All 454 valid
2.6 Annotation (author, annotators):  PASS - All 454 valid
2.7 gold_rationale (min 50 chars):    PASS - All 454 valid
2.8 claim (min 10 chars):             PASS - All 454 valid
2.9 Variables (X, Y, Z):              PASS - All 454 valid
```

### Issues Fixed During Review

| Case ID | Issue | Fix Applied |
|---------|-------|-------------|
| T3-BucketI-0037 | claim='rm -rf /' (8 chars) | Updated to full counterfactual claim |
| T3-BucketI-0042 | claim='Head 4.2' (8 chars) | Updated to full counterfactual claim |
| T3-BucketI-0034 | Missing variable Y | Added Y: Citation Accuracy |
| T3-BucketI-0035 | Missing variable Y | Added Y: Instruction Recall |
| T3-BucketI-0395 | Missing variable Z | Renamed M to Z (mediator) |
| T3-BucketI-0399 | Missing variable Z | Renamed M to Z (mediator) |

### Design Decision: hidden_structure in L1/L3 Cases

Per the plan's "FIELDS TO KEEP (hybrid - preserve all existing)" requirement, `hidden_structure` fields are retained in L1/L3 cases with empty string values (`""`). This is intentional:
- L1 cases: 52 with empty hidden_structure (no data, kept for consistency)
- L3 cases: 125 with empty hidden_structure (no data, kept for consistency)

This is **NOT a data error** but a design choice to maintain consistent schema structure across all cases.

### Commands Run

```bash
# Full validation script
python3 project/scripts/validate_v3_final_report.py

# Data fix script (6 issues)
python3 -c "... fix claims and variables ..."

# Re-validation after fixes
python3 -c "... verify all issues resolved ..."
```

### Final Verdict

**APPROVED** - V3.0 Schema Update implementation complete and verified.

All deliverables present, all field constraints satisfied, documentation accurate, no data regressions from V2.0.
