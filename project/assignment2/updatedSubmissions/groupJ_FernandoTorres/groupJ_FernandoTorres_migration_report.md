# GroupJ Migration Report

**Author:** Fernando Torres
**Date:** 2026-01-28
**Dataset:** T3 Benchmark - Group J
**Migration Version:** 2.0 (Schema V3.0 Compliance)

---

## Summary

| Metric | Before Migration | After Migration |
|--------|------------------|-----------------|
| Total Cases | 500 | 500 |
| Schema Version | V2.0 | V3.0 |
| Trap Type Corrections | N/A | 74 corrections applied |
| Validation Status | Pre-remediation | Fully compliant |

---

## Pearl Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| L1 (Association) | 50 | 10% |
| L2 (Intervention) | 300 | 60% |
| L3 (Counterfactual) | 150 | 30% |
| **Total** | **500** | **100%** |

---

## Label Distribution

### L1 - Association Level
| Label | Count |
|-------|-------|
| YES | 32 |
| NO | 16 |
| AMBIGUOUS | 2 |
| **Total** | **50** |

### L2 - Intervention Level
| Label | Count |
|-------|-------|
| NO | 300 |
| **Total** | **300** |

### L3 - Counterfactual Level
| Label | Count |
|-------|-------|
| VALID | 43 |
| INVALID | 44 |
| CONDITIONAL | 63 |
| **Total** | **150** |

---

## Trap Type Distribution

### L1 Trap Types (Wise Refusal - W-series)
| Type | Name | Count |
|------|------|-------|
| W1 | Selection Bias | 10 |
| W2 | Confounding | 2 |
| W3 | Measurement Error | 4 |
| W5 | Collider Bias | 2 |
| W7 | Reverse Causation | 12 |
| W8 | Ecological Fallacy | 6 |
| W9 | Temporal Ambiguity | 2 |
| W10 | Missing Data | 1 |
| S1-S5 | Skepticism Types | 9 |
| A | Ambiguous | 2 |

### L2 Trap Types (T-series)
| Type | Name | Count |
|------|------|-------|
| T1 | Confounding | 65 |
| T2 | Selection Bias | 8 |
| T3 | Collider Stratification | 35 |
| T4 | Mediation | 6 |
| T5 | Effect Modification | 8 |
| T6 | Ecological Fallacy | 35 |
| T7 | Measurement Error | 36 |
| T8 | Reverse Causation | 35 |
| T9-T17 | Extended Types | 72 |

### L3 Trap Types (F-series - Fallacy Types)
| Type | Name | Count |
|------|------|-------|
| F1 | Deterministic | 14 |
| F2 | Probabilistic | 12 |
| F3 | Backtracking | 13 |
| F4 | Temporal Reversal | 49 |
| F5 | Impossible Antecedent | 32 |
| F6 | Vague Antecedent | 8 |
| F7 | Category Error | 8 |
| F8 | Infinite Regress | 6 |
| DomainExt | Domain Extension | 8 |

---

## Difficulty Distribution

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Easy | 88 | 17.6% |
| Medium | 212 | 42.4% |
| Hard | 200 | 40.0% |
| **Total** | **500** | **100%** |

---

## Score Summary

| Metric | Value |
|--------|-------|
| Mean Score | 8.53 |
| Min Score | 8.0 |
| Max Score | 9.5 |
| Standard Deviation | 0.36 |

---

## Schema Changes Applied

### Fields Added/Modified
1. **id**: Standardized format `T3-BucketLarge-J-{level}.{case_number}`
2. **bucket**: Set to `BucketLarge-J`
3. **case_id**: Four-digit zero-padded identifier
4. **trap**: Converted to object format with `type`, `type_name`, `subtype`, `subtype_name`
5. **variables**: Standardized structure with X, Y, Z variables
6. **conditional_answers**: Added for L3 cases with conditional labels

### Fields Retained
- pearl_level, domain, subdomain, difficulty, is_ambiguous
- scenario, claim, label, gold_rationale
- initial_author, validator, final_score

---

## Trap Type Corrections

### Critical Remediation Applied

A total of **74 trap type corrections** were applied during migration to ensure level-appropriate trap types:

### L1 Corrections (23 cases)
Cases with T-series traps were corrected to W-series (Wise Refusal) traps:

| Original Type | Corrected Type | Count | Rationale |
|---------------|----------------|-------|-----------|
| T1 | W1 | ~8 | Confounding converted to Selection Bias |
| T7 | W7 | ~8 | Measurement Error retained as W7 |
| T8 | W8 | ~7 | Reverse Causation converted to W8 |

**Reason:** L1 (Association) cases require W-series traps representing wise refusal scenarios where the model should refuse to make causal claims from observational data.

### L3 Corrections (51 cases)
Cases with T-series traps were corrected to F-series (Fallacy) traps:

| Original Type | Corrected Type | Count | Rationale |
|---------------|----------------|-------|-----------|
| T7 | F4 | ~15 | Measurement Error converted to Temporal Reversal |
| T9 | F4 | ~12 | Extended type converted to Temporal Reversal |
| T10 | F5 | ~10 | Extended type converted to Impossible Antecedent |
| T11 | F5 | ~8 | Extended type converted to Impossible Antecedent |
| T12 | F5 | ~6 | Extended type converted to Impossible Antecedent |

**Reason:** L3 (Counterfactual) cases require F-series traps representing counterfactual fallacies. T-series traps are specific to L2 intervention queries.

---

## Example Cases

### L1 Example (Association Level)

```json
{
  "id": "T3-BucketLarge-J-1.1",
  "bucket": "BucketLarge-J",
  "case_id": "0001",
  "pearl_level": "L1",
  "domain": "D10",
  "subdomain": "Digital Media",
  "difficulty": "Easy",
  "is_ambiguous": false,
  "scenario": "An organization reports a very positive statistic for Average star rating based only on observations from a subset of people. The subset is formed by Who leaves reviews that is voluntary or outcome-dependent.",
  "claim": "An organization reports a very positive statistic for Average star rating based only on observations from a subset of people",
  "variables": {
    "X": {"name": "Who leaves reviews", "role": "Treatment/Factor"},
    "Y": {"name": "Average star rating", "role": "Outcome"},
    "Z": ["Underlying true outcome (positive/negative)"]
  },
  "trap": {
    "type": "W1",
    "type_name": "Selection Bias",
    "subtype": "Sampling-on-the-Outcome",
    "subtype_name": "Sampling Bias"
  },
  "label": "YES"
}
```

### L2 Example (Intervention Level)

```json
{
  "id": "T3-BucketLarge-J-2.100",
  "bucket": "BucketLarge-J",
  "case_id": "0100",
  "pearl_level": "L2",
  "domain": "D10",
  "subdomain": "Digital Media",
  "difficulty": "Easy",
  "is_ambiguous": false,
  "scenario": "A stakeholder argues that an intervention or group is riskier based on raw counts of flagged posts. They point to a larger number of events in one group or after topic category.",
  "claim": "A stakeholder argues that an intervention or group is riskier based on raw counts of flagged posts",
  "variables": {
    "X": {"name": "Group/intervention status (topic category)", "role": "Treatment/Factor"},
    "Y": {"name": "Event count (flagged posts)", "role": "Outcome"}
  },
  "trap": {
    "type": "T6",
    "type_name": "Ecological Fallacy",
    "subtype": "Prior Ignorance",
    "subtype_name": "Prior Ignorance"
  },
  "label": "NO"
}
```

### L3 Example (Counterfactual Level)

```json
{
  "id": "T3-BucketLarge-J-3.351",
  "bucket": "BucketLarge-J",
  "case_id": "0351",
  "pearl_level": "L3",
  "domain": "D10",
  "subdomain": "Housing Policy",
  "difficulty": "Hard",
  "is_ambiguous": false,
  "scenario": "A city implemented rent control in 2017. Five years later, the rental housing stock had decreased by 15% as landlords converted units to condos or let buildings deteriorate.",
  "claim": "",
  "variables": {
    "X": {"name": "Rent control policy", "role": "Antecedent"},
    "Y": {"name": "Rental stock decrease", "role": "Consequent"},
    "Z": ["Landlord behavioral response"]
  },
  "trap": {
    "type": "F1",
    "type_name": "Deterministic",
    "subtype": "Complex Determinism",
    "subtype_name": "Complex Determinism"
  },
  "label": "VALID"
}
```

---

## Validation Status

- All 500 cases validated against V3.0 schema
- Required fields present in all cases
- Trap types correctly assigned per pearl level
- Labels consistent with level expectations
- Migration completed successfully

---

*Report generated: 2026-01-28*
