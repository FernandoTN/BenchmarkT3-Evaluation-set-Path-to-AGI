#!/usr/bin/env python3
"""
T3 Benchmark V4.0 Case Validator
Validates cases against schema and quality criteria
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Valid trap types by level
L1_WOLF_TYPES = {'W1', 'W2', 'W3', 'W5', 'W7', 'W9', 'W10'}
L1_SHEEP_TYPES = {'S1', 'S2', 'S3', 'S4', 'S5'}
L2_TRAP_TYPES = {f'T{i}' for i in range(1, 18)}
L3_FAMILIES = {f'F{i}' for i in range(1, 9)} | {'DomainExt'}

# Family mappings for L2
L2_FAMILY_MAP = {
    'T1': 'F1', 'T2': 'F1', 'T3': 'F1', 'T4': 'F1',  # Selection
    'T5': 'F2', 'T6': 'F2',  # Statistical
    'T7': 'F3', 'T8': 'F3', 'T9': 'F3',  # Confounding
    'T10': 'F4', 'T11': 'F4', 'T12': 'F4',  # Direction
    'T13': 'F5', 'T14': 'F5',  # Information
    'T15': 'F6', 'T16': 'F6', 'T17': 'F6',  # Mechanism
}


def validate_case(case: Dict, idx: int) -> List[str]:
    """Validate a single case and return list of errors"""
    errors = []
    case_id = case.get('case_id', f'Case #{idx}')

    # Required fields
    required = ['case_id', 'pearl_level', 'domain', 'difficulty', 'trap_type',
                'scenario', 'variables', 'label', 'wise_refusal',
                'initial_author', 'validator', 'final_score']

    for field in required:
        if field not in case:
            errors.append(f"{case_id}: Missing required field '{field}'")

    # Pearl level validation
    level = case.get('pearl_level')
    if level not in {'L1', 'L2', 'L3'}:
        errors.append(f"{case_id}: Invalid pearl_level '{level}'")

    # Difficulty validation
    if case.get('difficulty') not in {'Easy', 'Medium', 'Hard'}:
        errors.append(f"{case_id}: Invalid difficulty '{case.get('difficulty')}'")

    # Level-specific validations
    if level == 'L1':
        trap = case.get('trap_type', '')
        label = case.get('label', '')
        if trap.startswith('W') and label != 'W':
            errors.append(f"{case_id}: WOLF trap type should have label 'W'")
        if trap.startswith('S') and label != 'S':
            errors.append(f"{case_id}: SHEEP trap type should have label 'S'")
        if trap == 'A' and label != 'A':
            errors.append(f"{case_id}: AMBIGUOUS trap type should have label 'A'")

    elif level == 'L2':
        if case.get('label') != 'NO':
            errors.append(f"{case_id}: L2 cases must have label 'NO'")
        if 'hidden_question' not in case:
            errors.append(f"{case_id}: L2 cases require 'hidden_question'")
        if 'conditional_answers' not in case:
            errors.append(f"{case_id}: L2 cases require 'conditional_answers'")
        trap = case.get('trap_type', '')
        if trap not in L2_TRAP_TYPES:
            errors.append(f"{case_id}: Invalid L2 trap type '{trap}'")

    elif level == 'L3':
        if case.get('label') not in {'VALID', 'INVALID', 'CONDITIONAL'}:
            errors.append(f"{case_id}: L3 cases must have label VALID/INVALID/CONDITIONAL")
        if 'counterfactual_claim' not in case:
            errors.append(f"{case_id}: L3 cases require 'counterfactual_claim'")
        if 'invariants' not in case:
            errors.append(f"{case_id}: L3 cases require 'invariants'")
        if 'ground_truth' not in case:
            errors.append(f"{case_id}: L3 cases require 'ground_truth'")
        if 'justification' not in case:
            errors.append(f"{case_id}: L3 cases require 'justification'")

    # Variables validation
    variables = case.get('variables', {})
    if not isinstance(variables, dict):
        errors.append(f"{case_id}: 'variables' must be an object")
    elif 'X' not in variables or 'Y' not in variables:
        errors.append(f"{case_id}: 'variables' must contain X and Y")

    # Score validation
    score = case.get('final_score')
    if score is not None and (not isinstance(score, (int, float)) or score < 0 or score > 10):
        errors.append(f"{case_id}: 'final_score' must be 0-10")

    # Content quality checks
    scenario = case.get('scenario', '')
    if len(scenario) < 50:
        errors.append(f"{case_id}: Scenario too short (min 50 chars)")

    refusal = case.get('wise_refusal', '')
    if len(refusal) < 50:
        errors.append(f"{case_id}: Wise refusal too short (min 50 chars)")

    return errors


def validate_dataset(cases: List[Dict]) -> Tuple[int, int, List[str]]:
    """Validate entire dataset, return (passed, failed, errors)"""
    all_errors = []
    passed = 0
    failed = 0

    case_ids = set()

    for idx, case in enumerate(cases):
        errors = validate_case(case, idx)

        # Check for duplicate IDs
        cid = case.get('case_id')
        if cid in case_ids:
            errors.append(f"{cid}: Duplicate case_id")
        case_ids.add(cid)

        if errors:
            all_errors.extend(errors)
            failed += 1
        else:
            passed += 1

    return passed, failed, all_errors


def check_distribution(cases: List[Dict], target_l1: int = 50, target_l2: int = 300, target_l3: int = 150):
    """Check if distribution meets targets"""
    counts = {'L1': 0, 'L2': 0, 'L3': 0}
    difficulty_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
    trap_counts = {}

    for case in cases:
        level = case.get('pearl_level')
        if level in counts:
            counts[level] += 1

        diff = case.get('difficulty')
        if diff in difficulty_counts:
            difficulty_counts[diff] += 1

        trap = case.get('trap_type', 'Unknown')
        trap_counts[trap] = trap_counts.get(trap, 0) + 1

    print(f"\n=== Distribution Analysis ===")
    print(f"By Pearl Level:")
    print(f"  L1: {counts['L1']}/{target_l1} ({'OK' if counts['L1'] >= target_l1 else 'NEED MORE'})")
    print(f"  L2: {counts['L2']}/{target_l2} ({'OK' if counts['L2'] >= target_l2 else 'NEED MORE'})")
    print(f"  L3: {counts['L3']}/{target_l3} ({'OK' if counts['L3'] >= target_l3 else 'NEED MORE'})")

    total = sum(counts.values())
    print(f"  Total: {total}/500")

    print(f"\nBy Difficulty:")
    for diff, count in difficulty_counts.items():
        print(f"  {diff}: {count} ({100*count/total:.1f}%)" if total > 0 else f"  {diff}: {count}")

    print(f"\nBy Trap Type (top 10):")
    for trap, count in sorted(trap_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {trap}: {count}")

    return counts, difficulty_counts, trap_counts


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_cases.py <dataset.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        data = json.load(f)

    # Handle both array format and object with metadata
    if isinstance(data, list):
        cases = data
    elif isinstance(data, dict) and 'cases' in data:
        cases = data['cases']
        print(f"Dataset has metadata header with {data.get('metadata', {}).get('dataset_info', {}).get('total_cases', 'N/A')} cases")
    else:
        print("Error: Dataset must be a JSON array or object with 'cases' key")
        sys.exit(1)

    print(f"Validating {len(cases)} cases from {filepath.name}...")

    passed, failed, errors = validate_dataset(cases)

    print(f"\n=== Validation Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors[:20]:  # Show first 20 errors
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors")

    check_distribution(cases)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
