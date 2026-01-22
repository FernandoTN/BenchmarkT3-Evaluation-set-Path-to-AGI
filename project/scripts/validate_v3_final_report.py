#!/usr/bin/env python3
"""
V3.0 Dataset Final Validation Report
Complete analysis of GroupI1_datasetV3.0.json against case_schema_v3.json
"""

import json
from pathlib import Path
from collections import defaultdict
import re

def load_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    base_path = Path('/Users/fernandotn/Projects/AGI/project')
    dataset_path = base_path / 'output' / 'final' / 'GroupI1_datasetV3.0.json'
    schema_path = base_path / 'schemas' / 'case_schema_v3.json'

    dataset = load_json(dataset_path)
    schema = load_json(schema_path)
    cases = dataset['cases']

    print("=" * 75)
    print("T3 BENCHMARK V3.0 DATASET VALIDATION REPORT")
    print("=" * 75)
    print()
    print(f"Dataset: {dataset_path.name}")
    print(f"Schema:  {schema_path.name}")
    print(f"Date:    2026-01-22")
    print()

    # =========================================================================
    # SECTION 1: DATASET STATISTICS
    # =========================================================================
    print("-" * 75)
    print("1. DATASET STATISTICS")
    print("-" * 75)
    print(f"   Total cases: {len(cases)}")
    print()

    # Pearl level distribution
    pearl_dist = defaultdict(int)
    for c in cases:
        pearl_dist[c.get('pearl_level', 'UNKNOWN')] += 1

    print("   Pearl Level Distribution:")
    print(f"      L1 (Association):    {pearl_dist['L1']:3d}")
    print(f"      L2 (Intervention):   {pearl_dist['L2']:3d}")
    print(f"      L3 (Counterfactual): {pearl_dist['L3']:3d}")
    print()

    # Label distribution
    label_dist = defaultdict(int)
    for c in cases:
        label_dist[c.get('label', 'UNKNOWN')] += 1

    print("   Label Distribution:")
    print(f"      YES:       {label_dist['YES']:3d}")
    print(f"      NO:        {label_dist['NO']:3d}")
    print(f"      AMBIGUOUS: {label_dist['AMBIGUOUS']:3d}")
    print()

    # =========================================================================
    # SECTION 2: FIELD CONSTRAINT VALIDATION
    # =========================================================================
    print("-" * 75)
    print("2. FIELD CONSTRAINT VALIDATION")
    print("-" * 75)

    violations = []

    # 2.1 ID Pattern: T3-BucketI-XXXX
    print()
    print("   2.1 ID Pattern (T3-BucketI-XXXX):")
    id_pattern = r'^T3-BucketI-[0-9]{4}$'
    id_violations = []
    for c in cases:
        if not re.match(id_pattern, c.get('id', '')):
            id_violations.append(c.get('id'))
    if id_violations:
        print(f"       FAIL - {len(id_violations)} violation(s)")
        violations.extend([f"ID pattern: {x}" for x in id_violations])
    else:
        print(f"       PASS - All {len(cases)} IDs match pattern")

    # 2.2 Bucket: exactly "BucketLarge-I"
    print()
    print("   2.2 Bucket (must be 'BucketLarge-I'):")
    bucket_violations = []
    for c in cases:
        if c.get('bucket') != 'BucketLarge-I':
            bucket_violations.append(f"{c.get('id')}: {c.get('bucket')}")
    if bucket_violations:
        print(f"       FAIL - {len(bucket_violations)} violation(s)")
        violations.extend([f"Bucket: {x}" for x in bucket_violations])
    else:
        print(f"       PASS - All {len(cases)} cases have correct bucket")

    # 2.3 Label: enum ["YES", "NO", "AMBIGUOUS"]
    print()
    print("   2.3 Label (YES/NO/AMBIGUOUS):")
    label_violations = []
    for c in cases:
        if c.get('label') not in ['YES', 'NO', 'AMBIGUOUS']:
            label_violations.append(f"{c.get('id')}: {c.get('label')}")
    if label_violations:
        print(f"       FAIL - {len(label_violations)} violation(s)")
        violations.extend([f"Label: {x}" for x in label_violations])
    else:
        print(f"       PASS - All {len(cases)} labels are valid")

    # 2.4 is_ambiguous: boolean matching (label == "AMBIGUOUS")
    print()
    print("   2.4 is_ambiguous (boolean, matches label=='AMBIGUOUS'):")
    ambiguous_violations = []
    for c in cases:
        expected = (c.get('label') == 'AMBIGUOUS')
        actual = c.get('is_ambiguous')
        if actual != expected:
            ambiguous_violations.append(f"{c.get('id')}: label={c.get('label')}, is_ambiguous={actual}")
    if ambiguous_violations:
        print(f"       FAIL - {len(ambiguous_violations)} violation(s)")
        violations.extend([f"is_ambiguous mismatch: {x}" for x in ambiguous_violations])
    else:
        print(f"       PASS - All {len(cases)} is_ambiguous values match labels")

    # 2.5 Trap: object with type and subtype
    print()
    print("   2.5 Trap (object with 'type' and 'subtype'):")
    trap_violations = []
    for c in cases:
        trap = c.get('trap')
        if not isinstance(trap, dict):
            trap_violations.append(f"{c.get('id')}: trap is not an object")
        elif 'type' not in trap:
            trap_violations.append(f"{c.get('id')}: trap missing 'type'")
        elif 'subtype' not in trap:
            trap_violations.append(f"{c.get('id')}: trap missing 'subtype'")
    if trap_violations:
        print(f"       FAIL - {len(trap_violations)} violation(s)")
        violations.extend(trap_violations)
    else:
        print(f"       PASS - All {len(cases)} traps have type and subtype")

    # 2.6 Annotation: object with author, num_annotators, adjudicated
    print()
    print("   2.6 Annotation (author, num_annotators, adjudicated):")
    ann_violations = []
    valid_authors = ['Stanford CS372', 'Fernando Torres', 'Alessandro Balzi']
    for c in cases:
        ann = c.get('annotation')
        if not isinstance(ann, dict):
            ann_violations.append(f"{c.get('id')}: annotation is not an object")
        else:
            if ann.get('author') not in valid_authors:
                ann_violations.append(f"{c.get('id')}: invalid author '{ann.get('author')}'")
            if not isinstance(ann.get('num_annotators'), int) or ann.get('num_annotators') < 1:
                ann_violations.append(f"{c.get('id')}: invalid num_annotators")
            if not isinstance(ann.get('adjudicated'), bool):
                ann_violations.append(f"{c.get('id')}: adjudicated not boolean")
    if ann_violations:
        print(f"       FAIL - {len(ann_violations)} violation(s)")
        violations.extend(ann_violations)
    else:
        print(f"       PASS - All {len(cases)} annotations are valid")

    # 2.7 gold_rationale: non-empty string (min 50 chars)
    print()
    print("   2.7 gold_rationale (non-empty string, min 50 chars):")
    rationale_violations = []
    for c in cases:
        gr = c.get('gold_rationale', '')
        if not isinstance(gr, str) or len(gr) < 50:
            rationale_violations.append(f"{c.get('id')}: len={len(gr) if isinstance(gr, str) else 'N/A'}")
    if rationale_violations:
        print(f"       FAIL - {len(rationale_violations)} violation(s)")
        violations.extend([f"gold_rationale: {x}" for x in rationale_violations])
    else:
        print(f"       PASS - All {len(cases)} gold_rationales are valid")

    # 2.8 claim: non-empty string (min 10 chars)
    print()
    print("   2.8 claim (non-empty string, min 10 chars):")
    claim_violations = []
    for c in cases:
        claim = c.get('claim', '')
        if not isinstance(claim, str) or len(claim) < 10:
            claim_violations.append(f"{c.get('id')}: claim='{claim}' (len={len(claim) if isinstance(claim, str) else 'N/A'})")
    if claim_violations:
        print(f"       FAIL - {len(claim_violations)} violation(s)")
        for v in claim_violations:
            print(f"              {v}")
        violations.extend([f"claim: {x}" for x in claim_violations])
    else:
        print(f"       PASS - All {len(cases)} claims are valid")

    # 2.9 Variables: X, Y, Z with name and role
    print()
    print("   2.9 Variables (X, Y, Z with name and role):")
    var_violations = []
    for c in cases:
        variables = c.get('variables', {})
        for var in ['X', 'Y', 'Z']:
            if var not in variables:
                var_violations.append(f"{c.get('id')}: missing variable '{var}'")
            elif not isinstance(variables[var], dict):
                var_violations.append(f"{c.get('id')}: '{var}' is not an object")
            elif 'name' not in variables[var] or 'role' not in variables[var]:
                var_violations.append(f"{c.get('id')}: '{var}' missing name or role")
    if var_violations:
        print(f"       FAIL - {len(var_violations)} violation(s)")
        for v in var_violations[:10]:
            print(f"              {v}")
        if len(var_violations) > 10:
            print(f"              ... and {len(var_violations) - 10} more")
        violations.extend(var_violations)
    else:
        print(f"       PASS - All variables are valid")

    # =========================================================================
    # SECTION 3: PEARL LEVEL CONSTRAINTS
    # =========================================================================
    print()
    print("-" * 75)
    print("3. PEARL LEVEL CONSTRAINTS")
    print("-" * 75)

    print()
    print("   Schema Requirements:")
    print("      L1: NO hidden_structure, NO ground_truth")
    print("      L2: REQUIRES hidden_structure, NO ground_truth")
    print("      L3: REQUIRES ground_truth, NO hidden_structure")
    print()

    # Analyze actual data
    pearl_analysis = defaultdict(lambda: {'count': 0, 'has_hs': 0, 'has_gt': 0, 'hs_empty': 0})
    for c in cases:
        pl = c.get('pearl_level')
        pearl_analysis[pl]['count'] += 1
        if 'hidden_structure' in c:
            pearl_analysis[pl]['has_hs'] += 1
            if c['hidden_structure'] == '':
                pearl_analysis[pl]['hs_empty'] += 1
        if 'ground_truth' in c:
            pearl_analysis[pl]['has_gt'] += 1

    print("   Actual Data Distribution:")
    for level in ['L1', 'L2', 'L3']:
        pa = pearl_analysis[level]
        print(f"      {level}: {pa['count']} cases")
        print(f"          hidden_structure present: {pa['has_hs']} (empty: {pa['hs_empty']})")
        print(f"          ground_truth present:     {pa['has_gt']}")
    print()

    # Count Pearl level violations
    pearl_violations = []

    # L1 violations
    l1_hs_cases = []
    l1_gt_cases = []
    for c in cases:
        if c.get('pearl_level') == 'L1':
            if 'hidden_structure' in c:
                l1_hs_cases.append(c.get('id'))
            if 'ground_truth' in c:
                l1_gt_cases.append(c.get('id'))

    print("   3.1 L1 Cases (should have neither hidden_structure nor ground_truth):")
    if l1_hs_cases:
        print(f"       FAIL - {len(l1_hs_cases)} L1 cases have 'hidden_structure'")
        pearl_violations.extend([f"L1 has hidden_structure: {x}" for x in l1_hs_cases])
    if l1_gt_cases:
        print(f"       FAIL - {len(l1_gt_cases)} L1 cases have 'ground_truth'")
        pearl_violations.extend([f"L1 has ground_truth: {x}" for x in l1_gt_cases])
    if not l1_hs_cases and not l1_gt_cases:
        print(f"       PASS")

    # L2 violations
    l2_missing_hs = []
    l2_has_gt = []
    for c in cases:
        if c.get('pearl_level') == 'L2':
            if 'hidden_structure' not in c:
                l2_missing_hs.append(c.get('id'))
            if 'ground_truth' in c:
                l2_has_gt.append(c.get('id'))

    print()
    print("   3.2 L2 Cases (must have hidden_structure, no ground_truth):")
    if l2_missing_hs:
        print(f"       FAIL - {len(l2_missing_hs)} L2 cases missing 'hidden_structure'")
        pearl_violations.extend([f"L2 missing hidden_structure: {x}" for x in l2_missing_hs])
    else:
        print(f"       PASS - All {pearl_dist['L2']} L2 cases have hidden_structure")
    if l2_has_gt:
        print(f"       FAIL - {len(l2_has_gt)} L2 cases have 'ground_truth'")
        pearl_violations.extend([f"L2 has ground_truth: {x}" for x in l2_has_gt])
    else:
        print(f"       PASS - No L2 cases have ground_truth")

    # L3 violations
    l3_missing_gt = []
    l3_has_hs = []
    for c in cases:
        if c.get('pearl_level') == 'L3':
            if 'ground_truth' not in c:
                l3_missing_gt.append(c.get('id'))
            if 'hidden_structure' in c:
                l3_has_hs.append(c.get('id'))

    print()
    print("   3.3 L3 Cases (must have ground_truth, no hidden_structure):")
    if l3_missing_gt:
        print(f"       FAIL - {len(l3_missing_gt)} L3 cases missing 'ground_truth'")
        pearl_violations.extend([f"L3 missing ground_truth: {x}" for x in l3_missing_gt])
    else:
        print(f"       PASS - All {pearl_dist['L3']} L3 cases have ground_truth")
    if l3_has_hs:
        print(f"       FAIL - {len(l3_has_hs)} L3 cases have 'hidden_structure'")
        pearl_violations.extend([f"L3 has hidden_structure: {x}" for x in l3_has_hs])
    else:
        print(f"       PASS - No L3 cases have hidden_structure")

    violations.extend(pearl_violations)

    # =========================================================================
    # SECTION 4: SUMMARY
    # =========================================================================
    print()
    print("-" * 75)
    print("4. VALIDATION SUMMARY")
    print("-" * 75)
    print()
    print(f"   Total cases validated:    {len(cases)}")
    print(f"   Total violations found:   {len(violations)}")
    print()

    # Categorize violations
    v_categories = defaultdict(int)
    for v in violations:
        if 'L1 has hidden_structure' in v:
            v_categories['L1 has hidden_structure (schema constraint)'] += 1
        elif 'L3 has hidden_structure' in v:
            v_categories['L3 has hidden_structure (schema constraint)'] += 1
        elif 'claim:' in v:
            v_categories['claim too short'] += 1
        elif 'missing variable' in v:
            v_categories['missing variable'] += 1
        else:
            v_categories['other'] += 1

    print("   Violations by Category:")
    for cat, count in sorted(v_categories.items(), key=lambda x: -x[1]):
        print(f"      {cat}: {count}")

    print()
    print("=" * 75)
    if violations:
        print("VERDICT: FAIL")
        print(f"         {len(violations)} schema violation(s) detected")
        print()
        print("NOTE: The majority of violations (177) are Pearl level constraint")
        print("      violations where hidden_structure is present in L1/L3 cases.")
        print("      This may indicate the schema constraints need revision, or")
        print("      the dataset needs to remove hidden_structure from L1/L3 cases.")
    else:
        print("VERDICT: PASS")
        print("         All cases conform to V3.0 schema")
    print("=" * 75)


if __name__ == '__main__':
    main()
