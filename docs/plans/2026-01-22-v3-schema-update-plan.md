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

- [ ] Total cases: 454
- [ ] All cases have new required fields: id, bucket, claim, label, is_ambiguous, trap, gold_rationale, annotation
- [ ] All existing fields preserved (hybrid)
- [ ] label values: all in ["YES", "NO", "AMBIGUOUS"]
- [ ] trap.type matches original annotations.trap_type
- [ ] Author distribution: ~45 Stanford, ~205 Fernando, ~204 Alessandro
- [ ] Schema updated
- [ ] V2.0 archived
- [ ] Methodology V3.0 created

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
