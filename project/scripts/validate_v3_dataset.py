#!/usr/bin/env python3
"""
V3.0 Dataset Validation Script
Validates GroupI1_datasetV3.0.json against case_schema_v3.json
"""

import json
import re
from pathlib import Path
from typing import Any

# Try to import jsonschema, fall back to manual validation if not available
try:
    import jsonschema
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Using manual validation.")


def load_json(filepath: str) -> Any:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_id_pattern(case_id: str) -> bool:
    """Validate id matches T3-BucketI-XXXX pattern."""
    return bool(re.match(r'^T3-BucketI-[0-9]{4}$', case_id))


def validate_case_id_pattern(case_id: str) -> bool:
    """Validate case_id matches 8.XXX pattern."""
    return bool(re.match(r'^8\.[0-9]{1,3}$', case_id))


def validate_case(case: dict, case_num: int) -> list[str]:
    """Validate a single case and return list of violations."""
    violations = []
    case_id = case.get('id', f'case_{case_num}')

    # Required fields check
    required_fields = [
        'id', 'bucket', 'pearl_level', 'case_id', 'scenario', 'claim',
        'label', 'is_ambiguous', 'trap', 'variables', 'gold_rationale',
        'annotation', 'annotations', 'correct_reasoning', 'wise_refusal'
    ]

    for field in required_fields:
        if field not in case:
            violations.append(f"{case_id}: Missing required field '{field}'")

    # ID pattern validation
    if 'id' in case:
        if not isinstance(case['id'], str):
            violations.append(f"{case_id}: 'id' must be a string")
        elif not validate_id_pattern(case['id']):
            violations.append(f"{case_id}: 'id' does not match pattern T3-BucketI-XXXX (got: {case['id']})")

    # Bucket validation
    if 'bucket' in case:
        if case['bucket'] != 'BucketLarge-I':
            violations.append(f"{case_id}: 'bucket' must be 'BucketLarge-I' (got: {case['bucket']})")

    # Pearl level validation
    if 'pearl_level' in case:
        if case['pearl_level'] not in ['L1', 'L2', 'L3']:
            violations.append(f"{case_id}: 'pearl_level' must be L1, L2, or L3 (got: {case['pearl_level']})")

    # Case ID pattern validation
    if 'case_id' in case:
        if not validate_case_id_pattern(case['case_id']):
            violations.append(f"{case_id}: 'case_id' does not match pattern 8.XXX (got: {case['case_id']})")

    # Label validation
    if 'label' in case:
        if case['label'] not in ['YES', 'NO', 'AMBIGUOUS']:
            violations.append(f"{case_id}: 'label' must be YES, NO, or AMBIGUOUS (got: {case['label']})")

    # is_ambiguous validation
    if 'is_ambiguous' in case:
        if not isinstance(case['is_ambiguous'], bool):
            violations.append(f"{case_id}: 'is_ambiguous' must be boolean (got: {type(case['is_ambiguous']).__name__})")
        elif 'label' in case:
            expected = (case['label'] == 'AMBIGUOUS')
            if case['is_ambiguous'] != expected:
                violations.append(f"{case_id}: 'is_ambiguous' should be {expected} when label is {case['label']} (got: {case['is_ambiguous']})")

    # Trap validation
    if 'trap' in case:
        trap = case['trap']
        if not isinstance(trap, dict):
            violations.append(f"{case_id}: 'trap' must be an object")
        else:
            if 'type' not in trap:
                violations.append(f"{case_id}: 'trap' missing required field 'type'")
            if 'subtype' not in trap:
                violations.append(f"{case_id}: 'trap' missing required field 'subtype'")
            # Check for extra fields
            allowed_trap_fields = {'type', 'subtype'}
            extra_fields = set(trap.keys()) - allowed_trap_fields
            if extra_fields:
                violations.append(f"{case_id}: 'trap' has extra fields: {extra_fields}")

    # Variables validation
    if 'variables' in case:
        variables = case['variables']
        if not isinstance(variables, dict):
            violations.append(f"{case_id}: 'variables' must be an object")
        else:
            for var in ['X', 'Y', 'Z']:
                if var not in variables:
                    violations.append(f"{case_id}: 'variables' missing required field '{var}'")
                elif isinstance(variables[var], dict):
                    if 'name' not in variables[var]:
                        violations.append(f"{case_id}: 'variables.{var}' missing 'name'")
                    if 'role' not in variables[var]:
                        violations.append(f"{case_id}: 'variables.{var}' missing 'role'")

    # Gold rationale validation
    if 'gold_rationale' in case:
        if not isinstance(case['gold_rationale'], str):
            violations.append(f"{case_id}: 'gold_rationale' must be a string")
        elif len(case['gold_rationale']) < 50:
            violations.append(f"{case_id}: 'gold_rationale' too short (min 50 chars, got {len(case['gold_rationale'])})")

    # Claim validation
    if 'claim' in case:
        if not isinstance(case['claim'], str):
            violations.append(f"{case_id}: 'claim' must be a string")
        elif len(case['claim']) < 10:
            violations.append(f"{case_id}: 'claim' too short (min 10 chars, got {len(case['claim'])})")

    # Scenario validation
    if 'scenario' in case:
        if not isinstance(case['scenario'], str):
            violations.append(f"{case_id}: 'scenario' must be a string")
        elif len(case['scenario']) < 10:
            violations.append(f"{case_id}: 'scenario' too short (min 10 chars)")
        elif len(case['scenario']) > 500:
            violations.append(f"{case_id}: 'scenario' too long (max 500 chars, got {len(case['scenario'])})")

    # Annotation validation
    if 'annotation' in case:
        ann = case['annotation']
        if not isinstance(ann, dict):
            violations.append(f"{case_id}: 'annotation' must be an object")
        else:
            if 'author' not in ann:
                violations.append(f"{case_id}: 'annotation' missing required field 'author'")
            elif ann['author'] not in ['Stanford CS372', 'Fernando Torres', 'Alessandro Balzi']:
                violations.append(f"{case_id}: 'annotation.author' invalid value: {ann['author']}")

            if 'num_annotators' not in ann:
                violations.append(f"{case_id}: 'annotation' missing required field 'num_annotators'")
            elif not isinstance(ann['num_annotators'], int) or ann['num_annotators'] < 1:
                violations.append(f"{case_id}: 'annotation.num_annotators' must be integer >= 1")

            if 'adjudicated' not in ann:
                violations.append(f"{case_id}: 'annotation' missing required field 'adjudicated'")
            elif not isinstance(ann['adjudicated'], bool):
                violations.append(f"{case_id}: 'annotation.adjudicated' must be boolean")

    # Annotations (legacy) validation
    if 'annotations' in case:
        anns = case['annotations']
        if not isinstance(anns, dict):
            violations.append(f"{case_id}: 'annotations' must be an object")
        else:
            req_ann_fields = ['pearl_level', 'domain', 'trap_type', 'trap_subtype',
                             'difficulty', 'subdomain', 'causal_structure', 'key_insight']
            for field in req_ann_fields:
                if field not in anns:
                    violations.append(f"{case_id}: 'annotations' missing field '{field}'")

            if 'domain' in anns and anns['domain'] != 'D8':
                violations.append(f"{case_id}: 'annotations.domain' must be 'D8' (got: {anns['domain']})")

            if 'difficulty' in anns and anns['difficulty'] not in ['Easy', 'Medium', 'Hard']:
                violations.append(f"{case_id}: 'annotations.difficulty' must be Easy/Medium/Hard")

    # correct_reasoning validation
    if 'correct_reasoning' in case:
        cr = case['correct_reasoning']
        if not isinstance(cr, list):
            violations.append(f"{case_id}: 'correct_reasoning' must be an array")
        elif len(cr) < 1:
            violations.append(f"{case_id}: 'correct_reasoning' must have at least 1 item")
        else:
            for i, item in enumerate(cr):
                if not isinstance(item, str):
                    violations.append(f"{case_id}: 'correct_reasoning[{i}]' must be a string")

    # wise_refusal validation
    if 'wise_refusal' in case:
        if not isinstance(case['wise_refusal'], str):
            violations.append(f"{case_id}: 'wise_refusal' must be a string")
        elif len(case['wise_refusal']) < 50:
            violations.append(f"{case_id}: 'wise_refusal' too short (min 50 chars, got {len(case['wise_refusal'])})")

    # Pearl level constraints
    pearl_level = case.get('pearl_level')
    has_hidden_structure = 'hidden_structure' in case
    has_ground_truth = 'ground_truth' in case

    if pearl_level == 'L1':
        if has_hidden_structure:
            violations.append(f"{case_id}: L1 case should NOT have 'hidden_structure'")
        if has_ground_truth:
            violations.append(f"{case_id}: L1 case should NOT have 'ground_truth'")

    elif pearl_level == 'L2':
        if not has_hidden_structure:
            violations.append(f"{case_id}: L2 case MUST have 'hidden_structure'")
        if has_ground_truth:
            violations.append(f"{case_id}: L2 case should NOT have 'ground_truth'")
        # Validate hidden_structure content
        if has_hidden_structure and not isinstance(case['hidden_structure'], str):
            violations.append(f"{case_id}: 'hidden_structure' must be a string")

    elif pearl_level == 'L3':
        if not has_ground_truth:
            violations.append(f"{case_id}: L3 case MUST have 'ground_truth'")
        if has_hidden_structure:
            violations.append(f"{case_id}: L3 case should NOT have 'hidden_structure'")
        # Validate ground_truth structure
        if has_ground_truth:
            gt = case['ground_truth']
            if not isinstance(gt, dict):
                violations.append(f"{case_id}: 'ground_truth' must be an object")
            else:
                if 'verdict' not in gt:
                    violations.append(f"{case_id}: 'ground_truth' missing 'verdict'")
                elif gt['verdict'] not in ['VALID', 'INVALID', 'CONDITIONAL']:
                    violations.append(f"{case_id}: 'ground_truth.verdict' must be VALID/INVALID/CONDITIONAL")

                if 'justification' not in gt:
                    violations.append(f"{case_id}: 'ground_truth' missing 'justification'")
                elif not isinstance(gt['justification'], str) or len(gt['justification']) < 20:
                    violations.append(f"{case_id}: 'ground_truth.justification' must be string >= 20 chars")

    return violations


def validate_with_jsonschema(cases: list, schema: dict) -> list[str]:
    """Validate using jsonschema library."""
    violations = []
    validator = Draft7Validator(schema)

    for i, case in enumerate(cases):
        errors = list(validator.iter_errors(case))
        for error in errors:
            path = '.'.join(str(p) for p in error.absolute_path) or 'root'
            violations.append(f"{case.get('id', f'case_{i}')}: [{path}] {error.message}")

    return violations


def main():
    # Paths
    base_path = Path('/Users/fernandotn/Projects/AGI/project')
    dataset_path = base_path / 'output' / 'final' / 'GroupI1_datasetV3.0.json'
    schema_path = base_path / 'schemas' / 'case_schema_v3.json'

    print("=" * 70)
    print("T3 Benchmark V3.0 Dataset Validation Report")
    print("=" * 70)
    print()

    # Load files
    print("Loading files...")
    try:
        dataset = load_json(dataset_path)
        schema = load_json(schema_path)
        print(f"  Dataset: {dataset_path}")
        print(f"  Schema:  {schema_path}")
    except Exception as e:
        print(f"ERROR loading files: {e}")
        return

    # Handle different dataset structures
    if isinstance(dataset, dict) and 'cases' in dataset:
        cases = dataset['cases']
        print(f"  Dataset structure: object with 'cases' array")
    elif isinstance(dataset, list):
        cases = dataset
        print(f"  Dataset structure: array of cases")
    else:
        print(f"ERROR: Unexpected dataset structure")
        return

    print(f"  Total cases: {len(cases)}")
    print()

    # Collect all violations
    all_violations = []

    # Manual validation (comprehensive)
    print("Running manual validation...")
    for i, case in enumerate(cases):
        violations = validate_case(case, i)
        all_violations.extend(violations)

    # jsonschema validation (if available)
    if HAS_JSONSCHEMA:
        print("Running jsonschema validation...")
        schema_violations = validate_with_jsonschema(cases, schema)
        # Add unique violations not already captured
        for v in schema_violations:
            if v not in all_violations:
                all_violations.append(v)

    # Statistics
    print()
    print("-" * 70)
    print("VALIDATION STATISTICS")
    print("-" * 70)

    # Count by Pearl level
    l1_count = sum(1 for c in cases if c.get('pearl_level') == 'L1')
    l2_count = sum(1 for c in cases if c.get('pearl_level') == 'L2')
    l3_count = sum(1 for c in cases if c.get('pearl_level') == 'L3')

    print(f"  Total cases validated: {len(cases)}")
    print(f"    L1 (Association):    {l1_count}")
    print(f"    L2 (Intervention):   {l2_count}")
    print(f"    L3 (Counterfactual): {l3_count}")
    print()

    # Count by label
    yes_count = sum(1 for c in cases if c.get('label') == 'YES')
    no_count = sum(1 for c in cases if c.get('label') == 'NO')
    amb_count = sum(1 for c in cases if c.get('label') == 'AMBIGUOUS')

    print(f"  Label distribution:")
    print(f"    YES:       {yes_count}")
    print(f"    NO:        {no_count}")
    print(f"    AMBIGUOUS: {amb_count}")
    print()

    # Violations report
    print("-" * 70)
    print("VIOLATIONS REPORT")
    print("-" * 70)

    if all_violations:
        print(f"  Total violations: {len(all_violations)}")
        print()

        # Group by case
        violations_by_case = {}
        for v in all_violations:
            case_id = v.split(':')[0]
            if case_id not in violations_by_case:
                violations_by_case[case_id] = []
            violations_by_case[case_id].append(v)

        print(f"  Cases with violations: {len(violations_by_case)}")
        print()

        # Print first 20 violations (or all if fewer)
        print("  Violation details (showing first 20):")
        for i, v in enumerate(all_violations[:20]):
            print(f"    {i+1}. {v}")

        if len(all_violations) > 20:
            print(f"    ... and {len(all_violations) - 20} more violations")
    else:
        print("  No violations found!")

    print()
    print("=" * 70)

    # Final verdict
    if all_violations:
        print("VERDICT: FAIL")
        print(f"  {len(all_violations)} schema violation(s) detected")
    else:
        print("VERDICT: PASS")
        print("  All cases conform to V3.0 schema")

    print("=" * 70)

    return len(all_violations) == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
