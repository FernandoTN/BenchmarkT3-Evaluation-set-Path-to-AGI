#!/usr/bin/env python3
"""
Detailed V3.0 Dataset Validation - Categorized Analysis
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

    dataset = load_json(dataset_path)
    cases = dataset['cases'] if isinstance(dataset, dict) and 'cases' in dataset else dataset

    # Categorize violations
    violations_by_type = defaultdict(list)

    for case in cases:
        case_id = case.get('id', 'unknown')
        pearl_level = case.get('pearl_level')
        has_hidden_structure = 'hidden_structure' in case
        has_ground_truth = 'ground_truth' in case

        # Pearl level constraint violations
        if pearl_level == 'L1':
            if has_hidden_structure:
                violations_by_type['L1_has_hidden_structure'].append(case_id)
            if has_ground_truth:
                violations_by_type['L1_has_ground_truth'].append(case_id)

        elif pearl_level == 'L2':
            if not has_hidden_structure:
                violations_by_type['L2_missing_hidden_structure'].append(case_id)
            if has_ground_truth:
                violations_by_type['L2_has_ground_truth'].append(case_id)

        elif pearl_level == 'L3':
            if has_hidden_structure:
                violations_by_type['L3_has_hidden_structure'].append(case_id)
            if not has_ground_truth:
                violations_by_type['L3_missing_ground_truth'].append(case_id)

        # Claim length
        claim = case.get('claim', '')
        if isinstance(claim, str) and len(claim) < 10:
            violations_by_type['claim_too_short'].append(f"{case_id} (len={len(claim)})")

        # Variables check
        variables = case.get('variables', {})
        for var in ['X', 'Y', 'Z']:
            if var not in variables:
                violations_by_type[f'missing_variable_{var}'].append(case_id)

        # is_ambiguous consistency
        label = case.get('label')
        is_ambiguous = case.get('is_ambiguous')
        if label and is_ambiguous is not None:
            expected = (label == 'AMBIGUOUS')
            if is_ambiguous != expected:
                violations_by_type['is_ambiguous_mismatch'].append(
                    f"{case_id} (label={label}, is_ambiguous={is_ambiguous})")

    # Print categorized report
    print("=" * 70)
    print("CATEGORIZED VIOLATION ANALYSIS")
    print("=" * 70)
    print()

    total_violations = 0
    for category, cases_list in sorted(violations_by_type.items()):
        count = len(cases_list)
        total_violations += count
        print(f"{category}: {count} violations")
        if count <= 10:
            for c in cases_list:
                print(f"    - {c}")
        else:
            for c in cases_list[:5]:
                print(f"    - {c}")
            print(f"    ... and {count - 5} more")
        print()

    print("=" * 70)
    print(f"TOTAL UNIQUE VIOLATIONS: {total_violations}")
    print("=" * 70)

    # Summary of Pearl level constraint issues
    print()
    print("PEARL LEVEL CONSTRAINT SUMMARY:")
    print("-" * 40)

    l1_issues = len(violations_by_type.get('L1_has_hidden_structure', [])) + \
                len(violations_by_type.get('L1_has_ground_truth', []))
    l2_issues = len(violations_by_type.get('L2_missing_hidden_structure', [])) + \
                len(violations_by_type.get('L2_has_ground_truth', []))
    l3_issues = len(violations_by_type.get('L3_has_hidden_structure', [])) + \
                len(violations_by_type.get('L3_missing_ground_truth', []))

    print(f"  L1 constraint violations: {l1_issues}")
    print(f"  L2 constraint violations: {l2_issues}")
    print(f"  L3 constraint violations: {l3_issues}")

    # The main issue seems to be hidden_structure present where it shouldn't be
    # Let's check if this is a schema interpretation issue
    print()
    print("ANALYSIS NOTE:")
    print("-" * 40)

    # Count how many cases have hidden_structure
    hs_count = sum(1 for c in cases if 'hidden_structure' in c)
    gt_count = sum(1 for c in cases if 'ground_truth' in c)
    print(f"  Cases with hidden_structure: {hs_count} / {len(cases)}")
    print(f"  Cases with ground_truth: {gt_count} / {len(cases)}")

    # Check if the constraint might be too strict
    # Perhaps hidden_structure is allowed for all levels?
    print()
    print("  Current schema constraints:")
    print("    - L1: NO hidden_structure, NO ground_truth")
    print("    - L2: REQUIRES hidden_structure, NO ground_truth")
    print("    - L3: REQUIRES ground_truth, NO hidden_structure")


if __name__ == '__main__':
    main()
