# T3 Benchmark V3.0: Methodology Report

**CS372: Artificial General Intelligence for Reasoning, Planning, and Decision Making**
**Stanford University - Winter 2026**

**Authors:** Fernando Torres, Alessandro Balzi
**Group:** I1
**Date:** January 22, 2026
**Version:** 3.0

---

## 1. Introduction

This report describes the methodology for updating the T3 Benchmark dataset from V2.0 (454 cases) to V3.0, adding new required fields per the CS372 Assignment 1 Updated requirements. The V3.0 schema introduces explicit causal claim extraction, label assignment, and structured annotation metadata.

---

## 2. Schema Changes (V2.0 → V3.0)

### 2.1 New Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier in format `T3-BucketI-XXXX` |
| `bucket` | string | Constant `"BucketLarge-I"` |
| `claim` | string | The causal claim being tested (AI-extracted) |
| `label` | enum | `YES`, `NO`, or `AMBIGUOUS` (AI-determined) |
| `is_ambiguous` | boolean | `true` if label is `AMBIGUOUS` |
| `trap` | object | Nested `{type, subtype}` structure |
| `gold_rationale` | string | Expert explanation of label correctness |
| `annotation` | object | Author metadata block |

### 2.2 Restructured Fields

| V2.0 Location | V3.0 Location |
|---------------|---------------|
| `annotations.trap_type` | `trap.type` |
| `annotations.trap_subtype` | `trap.subtype` |
| `annotations.pearl_level` | `pearl_level` (top-level) |

### 2.3 Preserved Fields (Hybrid Approach)

All existing V2.0 fields were preserved:
- `case_id`, `scenario`, `variables`
- `annotations` (full object with legacy metadata)
- `hidden_structure` (L2 cases)
- `ground_truth` (L3 cases)
- `correct_reasoning`, `wise_refusal`

---

## 3. Methodology

### 3.1 Transformation Pipeline

We employed a five-phase hybrid strategy with parallel agent processing:

**Phase 1: Setup & Archive**
- Created archive directory for V2.0 files
- Created intermediate directory for transformation outputs

**Phase 2: Original Case Identification**
- Parsed `BenchmarkT3-BucketLarge-I.md` to identify 49 original Stanford CS372 cases
- Used scenario text matching for author attribution

**Phase 3: Parallel Transformation (8 Agents)**
Each agent specialized in a trap type:

| Agent | Trap Type | Cases |
|-------|-----------|-------|
| 1 | GOODHART | 93 |
| 2 | COUNTERFACTUAL | 91 |
| 3 | SELECTION_SPURIOUS | 47 |
| 4 | SPECIFICATION | 42 |
| 5 | CONF_MED | 40 |
| 6 | INSTRUMENTAL | 39 |
| 7 | FEEDBACK | 30 |
| 8 | OTHER (22+ types) | 72 |

**Phase 4: Parallel Validation (8 Agents)**
Each validator verified:
1. New field presence
2. Field value constraints
3. Label consistency
4. Existing field integrity
5. Pearl level requirements

**Phase 5: Merge & Finalize**
- Aggregated all transformed cases
- Sorted by numeric ID
- Added V3.0 metadata

### 3.2 AI Analysis Functions

**Claim Extraction:**
For each scenario, the AI agent extracted the implicit causal claim being tested. Example:

> Scenario: "A cleaning robot is rewarded for minimizing visible dust. It learns to sweep dust under the rug."
>
> Extracted Claim: "Minimizing visible dust leads to actual cleanliness."

**Label Determination:**
Labels were assigned based on analysis of each case:

| Label | Criteria |
|-------|----------|
| `YES` | Claim is supported by scenario evidence |
| `NO` | Claim is invalid due to identified causal trap |
| `AMBIGUOUS` | Cannot be determined from available information |

For COUNTERFACTUAL cases, labels were derived from `ground_truth.verdict`:
- `VALID` → `YES`
- `INVALID` → `NO`
- `CONDITIONAL` → `AMBIGUOUS`

### 3.3 Author Attribution

| Condition | Author |
|-----------|--------|
| Original Stanford benchmark case | `Stanford CS372` |
| Generated case, odd numeric ID | `Fernando Torres` |
| Generated case, even numeric ID | `Alessandro Balzi` |

---

## 4. Results

### 4.1 Dataset Statistics

| Metric | Value |
|--------|-------|
| Total Cases | 454 |
| Schema Version | V3.0 |
| File Size | 1.3 MB |

### 4.2 Label Distribution

| Label | Count | Percentage |
|-------|-------|------------|
| NO | 385 | 84.8% |
| AMBIGUOUS | 38 | 8.4% |
| YES | 31 | 6.8% |

### 4.3 Pearl Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| L1 (Association) | 52 | 11.5% |
| L2 (Intervention) | 277 | 61.0% |
| L3 (Counterfactual) | 125 | 27.5% |

### 4.4 Author Distribution

| Author | Count | Percentage |
|--------|-------|------------|
| Stanford CS372 | 49 | 10.8% |
| Fernando Torres | 202 | 44.5% |
| Alessandro Balzi | 203 | 44.7% |

### 4.5 Top Trap Types

| Trap Type | Count |
|-----------|-------|
| GOODHART | 93 |
| COUNTERFACTUAL | 91 |
| SELECTION_SPURIOUS | 47 |
| SPECIFICATION | 42 |
| CONF_MED | 40 |

---

## 5. Quality Assurance

### 5.1 Validation Results

All 454 cases passed validation across all checks:

| Check | Pass Rate |
|-------|-----------|
| New Field Presence | 100% |
| ID Format | 100% |
| Bucket Value | 100% |
| Label Values | 100% |
| is_ambiguous Consistency | 100% |
| Trap Fields | 100% |
| Annotation Fields | 100% |
| Label Consistency | 100% |
| Existing Field Integrity | 100% |
| Pearl Level Requirements | 100% |

### 5.2 Verification Checklist

- [x] Total cases: 454
- [x] All new required fields present
- [x] All existing fields preserved
- [x] Label values valid (YES/NO/AMBIGUOUS)
- [x] trap.type matches original annotations
- [x] Author distribution balanced
- [x] Schema V3.0 compliant

---

## 6. Deliverables

| File | Description |
|------|-------------|
| `GroupI1_datasetV3.0.json` | 454 validated cases with V3.0 schema |
| `GroupI1_methodology_V3.0.md` | This methodology report |
| `case_schema_v3.json` | JSON Schema for V3.0 validation |

---

## 7. Conclusion

We successfully updated the T3 Benchmark from V2.0 to V3.0, adding explicit causal claims, labels, and structured metadata while preserving all existing content. The parallel agent architecture enabled efficient processing of all 454 cases with comprehensive validation.

---

*Group I1 - Stanford CS372 Winter 2026*
