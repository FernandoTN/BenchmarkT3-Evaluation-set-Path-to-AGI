#!/usr/bin/env python3
"""
Schema Migration Script for CS372 Assignment 2

Migrates existing V4.0 datasets to the new Assignment 2 schema specification (Appendix B).

Key transformations:
1. Generate new ID fields (id, bucket, case_id)
2. Transform variables.Z from object to array of strings
3. Restructure flat trap fields into nested trap object
4. Transform L1 labels: W→NO, S→YES, A→AMBIGUOUS
5. Correct L1 trap types for GroupJ (T1→W1, T7→W7, T8→W8)
6. Add missing required fields
7. Remove development metadata fields
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


# =============================================================================
# TRAP TYPE MAPPINGS
# =============================================================================

# GroupJ L1 cases incorrectly have L2 trap types - correct them
L1_TRAP_TYPE_CORRECTION = {
    "T1": "W1",   # Selection Bias (L2) -> Selection Bias (L1 Wolf)
    "T7": "W7",   # Confounder (L2) -> Confounding (L1 Wolf)
    "T8": "W8",   # Simpson's Paradox (L2) -> Simpson's Paradox (L1 Wolf)
}

# GroupJ L3 cases incorrectly have L2 trap types - map to appropriate L3 families
L3_TRAP_TYPE_CORRECTION = {
    "T7": "F4",    # Confounder -> Structural (confounding is a structural issue)
    "T9": "F4",    # Confounding-Mediation -> Structural
    "T10": "F5",   # Reverse Causation -> Temporal
    "T11": "F5",   # Feedback Loop -> Temporal
    "T12": "F5",   # Temporal Precedence -> Temporal
}

TRAP_TYPE_NAMES = {
    # L1 WOLF (Spurious/Unjustified claims)
    "W1": "Selection Bias",
    "W2": "Survivorship Bias",
    "W3": "Healthy User Bias",
    "W4": "Regression to Mean",
    "W5": "Ecological Fallacy",
    "W6": "Base Rate Neglect",
    "W7": "Confounding",
    "W8": "Simpson's Paradox",
    "W9": "Reverse Causation",
    "W10": "Post Hoc Fallacy",
    # L1 SHEEP (Valid/Justified claims)
    "S1": "RCT",
    "S2": "Natural Experiment",
    "S3": "Lottery/Quasi-Random",
    "S4": "Controlled Ablation",
    "S5": "Mechanism + Dose",
    "S6": "Instrumental Variable",
    "S7": "Diff-in-Diff",
    "S8": "Regression Discontinuity",
    # L1 Ambiguous
    "A": "Ambiguous",
    # L2 Traps
    "T1": "Selection Bias",
    "T2": "Survivorship Bias",
    "T3": "Collider Bias",
    "T4": "Immortal Time Bias",
    "T5": "Regression to Mean",
    "T6": "Ecological Fallacy",
    "T7": "Confounder",
    "T8": "Simpson's Paradox",
    "T9": "Confounding-Mediation",
    "T10": "Reverse Causation",
    "T11": "Feedback Loop",
    "T12": "Temporal Precedence",
    "T13": "Measurement Error",
    "T14": "Recall Bias",
    "T15": "Mechanism Confusion",
    "T16": "Goodhart's Law",
    "T17": "Backfire Effect",
    # L3 Families
    "F1": "Deterministic",
    "F2": "Probabilistic",
    "F3": "Overdetermination",
    "F4": "Structural",
    "F5": "Temporal",
    "F6": "Epistemic",
    "F7": "Attribution",
    "F8": "Moral/Legal",
    "DomainExt": "Domain Extension",
}

TRAP_SUBTYPE_NAMES = {
    # Common subtypes - lookup table
    "Asymptotic Failure / Extrapolation": "Extrapolation Error",
    "Alignment Tax / Trade-Off Fallacy": "Trade-Off Fallacy",
    "Sampling-on-the-Outcome": "Sampling Bias",
    # Default: return the subtype itself if no mapping
}

# L1 Label transformation
L1_LABEL_MAP = {
    "W": "NO",
    "S": "YES",
    "A": "AMBIGUOUS",
}

# Fields to remove (development metadata)
FIELDS_TO_REMOVE = [
    "_original_id",
    "_original_title",
    "_questions",
    "_expected_analysis",
    "trap_family",     # Subsumed into trap object
    "trap_type",       # Subsumed into trap object
    "trap_subtype",    # Subsumed into trap object
]


# =============================================================================
# TRANSFORMATION FUNCTIONS
# =============================================================================

def transform_ids(old_case_id: str, group: str) -> Dict[str, str]:
    """
    Transform case_id format and generate new id/bucket fields.

    Old: case_id = "T3-I-L1-0001"
    New: id = "T3-BucketLarge-I-1.1", case_id = "0001", bucket = "BucketLarge-I"
    """
    # Parse old format: "T3-I-L1-0001" or "T3-J-L2-0150"
    match = re.match(r'T3-([IJ])-L(\d)-(\d+)', old_case_id)
    if not match:
        raise ValueError(f"Invalid case_id format: {old_case_id}")

    group_letter = match.group(1)
    level_num = match.group(2)
    seq = int(match.group(3))

    return {
        "id": f"T3-BucketLarge-{group_letter}-{level_num}.{seq}",
        "bucket": f"BucketLarge-{group_letter}",
        "case_id": match.group(3),  # Keep as "0001"
    }


def transform_z_variable(z_value: Any) -> List[str]:
    """
    Transform variables.Z from object to array of strings.

    Old: "Z": {"name": "Hallucination Rate", "role": "..."}
    New: "Z": ["Hallucination Rate"]
    """
    if isinstance(z_value, dict):
        name = z_value.get("name", "")
        return [name] if name else []
    elif isinstance(z_value, list):
        # Already an array - ensure all items are strings
        return [str(item) if not isinstance(item, str) else item for item in z_value]
    elif isinstance(z_value, str):
        return [z_value]
    return []


def correct_trap_type(trap_type: str, pearl_level: str) -> str:
    """
    Correct cases that incorrectly have wrong trap types.
    - L1 cases with T-types -> W-types (GroupJ L1 bug)
    - L3 cases with T-types -> F-types (GroupJ L3 bug)
    """
    if pearl_level == "L1" and trap_type in L1_TRAP_TYPE_CORRECTION:
        return L1_TRAP_TYPE_CORRECTION[trap_type]
    if pearl_level == "L3" and trap_type in L3_TRAP_TYPE_CORRECTION:
        return L3_TRAP_TYPE_CORRECTION[trap_type]
    return trap_type


def get_trap_type_name(trap_type: str) -> str:
    """Get the human-readable name for a trap type."""
    return TRAP_TYPE_NAMES.get(trap_type, trap_type)


def get_trap_subtype_name(subtype: str) -> str:
    """Get the human-readable name for a trap subtype."""
    return TRAP_SUBTYPE_NAMES.get(subtype, subtype if subtype else "")


def create_trap_object(case: Dict[str, Any], corrected_trap_type: str) -> Dict[str, str]:
    """
    Create nested trap object from flat fields.

    Old: trap_type = "W3", trap_subtype = "...", trap_family = "F1"
    New: trap = {type: "W3", type_name: "Healthy User Bias", subtype: "...", subtype_name: "..."}
    """
    subtype = case.get("trap_subtype", "")

    return {
        "type": corrected_trap_type,
        "type_name": get_trap_type_name(corrected_trap_type),
        "subtype": subtype,
        "subtype_name": get_trap_subtype_name(subtype),
    }


def transform_l1_label(label: str, pearl_level: str) -> str:
    """
    Transform L1 labels: W→NO, S→YES, A→AMBIGUOUS.
    L2 and L3 labels remain unchanged.
    """
    if pearl_level == "L1" and label in L1_LABEL_MAP:
        return L1_LABEL_MAP[label]
    return label


def generate_missing_fields(case: Dict[str, Any]) -> Dict[str, Any]:
    """Generate missing required fields with appropriate defaults."""
    label = case.get("label", "")

    return {
        "is_ambiguous": label in ["A", "AMBIGUOUS"],
        "gold_rationale": case.get("wise_refusal", ""),  # Copy from wise_refusal
        "hidden_timestamp": case.get("hidden_question", ""),  # Use hidden_question if present
        "conditional_answers": case.get("conditional_answers", {
            "answer_if_condition_1": "",
            "answer_if_condition_2": ""
        }),
    }


def clean_extra_fields(case: Dict[str, Any]) -> Dict[str, Any]:
    """Remove development metadata and legacy fields."""
    for field in FIELDS_TO_REMOVE:
        case.pop(field, None)
    return case


# =============================================================================
# MAIN TRANSFORMATION
# =============================================================================

def transform_case(case: Dict[str, Any], group: str) -> Dict[str, Any]:
    """
    Apply all transformations to a single case.
    Returns a new transformed case dict.
    """
    pearl_level = case.get("pearl_level", "")
    old_case_id = case.get("case_id", "")

    # 1. Transform IDs
    id_fields = transform_ids(old_case_id, group)

    # 2. Correct trap type for L1 cases
    original_trap_type = case.get("trap_type", "")
    corrected_trap_type = correct_trap_type(original_trap_type, pearl_level)

    # 3. Create trap object
    trap_object = create_trap_object(case, corrected_trap_type)

    # 4. Transform label
    original_label = case.get("label", "")
    new_label = transform_l1_label(original_label, pearl_level)

    # 5. Transform variables.Z
    variables = case.get("variables", {}).copy()
    if "Z" in variables:
        variables["Z"] = transform_z_variable(variables["Z"])

    # 6. Generate missing fields
    missing_fields = generate_missing_fields(case)

    # 7. Build transformed case with correct field order
    transformed = {
        "id": id_fields["id"],
        "bucket": id_fields["bucket"],
        "case_id": id_fields["case_id"],
        "pearl_level": pearl_level,
        "domain": case.get("domain", ""),
        "subdomain": case.get("subdomain", ""),
        "difficulty": case.get("difficulty", ""),
        "is_ambiguous": missing_fields["is_ambiguous"],
        "scenario": case.get("scenario", ""),
        "claim": case.get("claim", ""),
        "variables": variables,
        "trap": trap_object,
        "label": new_label,
        "causal_structure": case.get("causal_structure", ""),
        "key_insight": case.get("key_insight", ""),
        "gold_rationale": missing_fields["gold_rationale"],
        "wise_refusal": case.get("wise_refusal", ""),
        "hidden_timestamp": missing_fields["hidden_timestamp"],
        "conditional_answers": missing_fields["conditional_answers"],
        "initial_author": case.get("initial_author", ""),
        "validator": case.get("validator", ""),
        "final_score": case.get("final_score", 0.0),
    }

    # Add L2-specific fields if present
    if pearl_level == "L2" and "hidden_structure" in case:
        transformed["hidden_structure"] = case["hidden_structure"]

    # Add L3-specific fields if present
    if pearl_level == "L3" and "ground_truth" in case:
        transformed["ground_truth"] = case["ground_truth"]

    return transformed


def migrate_dataset(
    input_path: str,
    output_path: str,
    group: str,
    level_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Migrate a dataset file, optionally filtering by pearl level.

    Args:
        input_path: Path to source dataset JSON
        output_path: Path to output transformed JSON
        group: Group identifier ("I" or "J")
        level_filter: Optional pearl level to filter ("L1", "L2", "L3")

    Returns:
        Statistics dict with transformation counts
    """
    # Load source data
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Access cases array (handle both flat array and nested structure)
    if isinstance(data, dict) and 'cases' in data:
        cases = data['cases']
    elif isinstance(data, list):
        cases = data
    else:
        raise ValueError(f"Unexpected data structure in {input_path}")

    # Filter by level if specified
    if level_filter:
        cases = [c for c in cases if c.get('pearl_level') == level_filter]

    # Transform each case
    transformed_cases = []
    errors = []
    trap_corrections = 0
    label_transformations = 0

    for case in cases:
        try:
            original_trap = case.get('trap_type', '')
            original_label = case.get('label', '')

            transformed = transform_case(case, group)
            transformed_cases.append(transformed)

            # Track statistics
            if transformed['trap']['type'] != original_trap:
                trap_corrections += 1
            if transformed['label'] != original_label:
                label_transformations += 1

        except Exception as e:
            errors.append({
                "case_id": case.get('case_id', 'unknown'),
                "error": str(e)
            })

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transformed_cases, f, indent=2, ensure_ascii=False)

    return {
        "input_path": input_path,
        "output_path": output_path,
        "group": group,
        "level_filter": level_filter,
        "total_input": len(cases),
        "total_transformed": len(transformed_cases),
        "trap_corrections": trap_corrections,
        "label_transformations": label_transformations,
        "errors": errors,
    }


def merge_temp_files(
    temp_dir: str,
    group: str,
    output_path: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge temporary level files into final dataset with metadata.
    """
    all_cases = []

    # Load each level file
    for level in ["L1", "L2", "L3"]:
        level_file = os.path.join(temp_dir, f"group{group}_{level}.json")
        if os.path.exists(level_file):
            with open(level_file, 'r', encoding='utf-8') as f:
                cases = json.load(f)
                all_cases.extend(cases)

    # Sort by id for consistent ordering
    all_cases.sort(key=lambda c: c.get('id', ''))

    # Build final dataset structure
    final_dataset = {
        "metadata": metadata,
        "cases": all_cases
    }

    # Write final output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)

    return {
        "output_path": output_path,
        "total_cases": len(all_cases),
        "by_level": {
            "L1": len([c for c in all_cases if c.get('pearl_level') == 'L1']),
            "L2": len([c for c in all_cases if c.get('pearl_level') == 'L2']),
            "L3": len([c for c in all_cases if c.get('pearl_level') == 'L3']),
        }
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_transformed_case(case: Dict[str, Any]) -> List[str]:
    """
    Validate a transformed case against the new schema requirements.
    Returns list of validation errors (empty if valid).
    """
    errors = []
    pearl_level = case.get('pearl_level', '')

    # Required fields
    required_fields = [
        'id', 'bucket', 'case_id', 'pearl_level', 'domain', 'subdomain',
        'difficulty', 'is_ambiguous', 'scenario', 'claim', 'variables',
        'trap', 'label', 'gold_rationale', 'initial_author', 'validator', 'final_score'
    ]

    for field in required_fields:
        if field not in case:
            errors.append(f"Missing required field: {field}")

    # Validate id format
    if 'id' in case:
        if not re.match(r'T3-BucketLarge-[IJ]-[123]\.\d+', case['id']):
            errors.append(f"Invalid id format: {case['id']}")

    # Validate bucket format
    if 'bucket' in case:
        if case['bucket'] not in ['BucketLarge-I', 'BucketLarge-J']:
            errors.append(f"Invalid bucket: {case['bucket']}")

    # Validate is_ambiguous is boolean
    if 'is_ambiguous' in case:
        if not isinstance(case['is_ambiguous'], bool):
            errors.append(f"is_ambiguous must be boolean, got: {type(case['is_ambiguous'])}")

    # Validate variables.Z is array
    if 'variables' in case and 'Z' in case['variables']:
        if not isinstance(case['variables']['Z'], list):
            errors.append(f"variables.Z must be array, got: {type(case['variables']['Z'])}")

    # Validate trap object structure
    if 'trap' in case:
        trap = case['trap']
        if not isinstance(trap, dict):
            errors.append("trap must be object")
        else:
            for trap_field in ['type', 'type_name']:
                if trap_field not in trap:
                    errors.append(f"trap missing field: {trap_field}")

    # Validate label by level
    if pearl_level == 'L1':
        if case.get('label') not in ['YES', 'NO', 'AMBIGUOUS']:
            errors.append(f"L1 label must be YES/NO/AMBIGUOUS, got: {case.get('label')}")
        # Validate trap type for L1
        trap_type = case.get('trap', {}).get('type', '')
        if not (trap_type.startswith('W') or trap_type.startswith('S') or trap_type == 'A'):
            errors.append(f"L1 trap type must be W1-W10, S1-S8, or A, got: {trap_type}")

    elif pearl_level == 'L2':
        if case.get('label') != 'NO':
            errors.append(f"L2 label must be NO, got: {case.get('label')}")
        # Validate trap type for L2
        trap_type = case.get('trap', {}).get('type', '')
        if not trap_type.startswith('T'):
            errors.append(f"L2 trap type must be T1-T17, got: {trap_type}")

    elif pearl_level == 'L3':
        if case.get('label') not in ['VALID', 'INVALID', 'CONDITIONAL']:
            errors.append(f"L3 label must be VALID/INVALID/CONDITIONAL, got: {case.get('label')}")
        # Validate trap type for L3
        trap_type = case.get('trap', {}).get('type', '')
        if not (trap_type.startswith('F') or trap_type == 'DomainExt'):
            errors.append(f"L3 trap type must be F1-F8 or DomainExt, got: {trap_type}")

    return errors


def validate_dataset(dataset_path: str) -> Dict[str, Any]:
    """
    Validate an entire dataset file.
    Returns validation report.
    """
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cases = data.get('cases', data) if isinstance(data, dict) else data

    total_errors = []
    valid_count = 0

    for case in cases:
        errors = validate_transformed_case(case)
        if errors:
            total_errors.append({
                "case_id": case.get('case_id', case.get('id', 'unknown')),
                "errors": errors
            })
        else:
            valid_count += 1

    return {
        "dataset_path": dataset_path,
        "total_cases": len(cases),
        "valid_cases": valid_count,
        "invalid_cases": len(total_errors),
        "validation_errors": total_errors[:10],  # Limit output
        "pass_rate": f"{(valid_count / len(cases) * 100):.1f}%" if cases else "N/A"
    }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migrate_to_v2_schema.py <command> [args...]")
        print()
        print("Commands:")
        print("  migrate <input> <output> <group> [level]  - Migrate dataset")
        print("  validate <dataset_path>                   - Validate dataset")
        print("  merge <temp_dir> <group> <output>         - Merge temp files")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate":
        if len(sys.argv) < 5:
            print("Usage: migrate <input> <output> <group> [level]")
            sys.exit(1)

        input_path = sys.argv[2]
        output_path = sys.argv[3]
        group = sys.argv[4]
        level = sys.argv[5] if len(sys.argv) > 5 else None

        result = migrate_dataset(input_path, output_path, group, level)
        print(json.dumps(result, indent=2))

    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: validate <dataset_path>")
            sys.exit(1)

        dataset_path = sys.argv[2]
        result = validate_dataset(dataset_path)
        print(json.dumps(result, indent=2))

    elif command == "merge":
        if len(sys.argv) < 5:
            print("Usage: merge <temp_dir> <group> <output>")
            sys.exit(1)

        temp_dir = sys.argv[2]
        group = sys.argv[3]
        output_path = sys.argv[4]

        # Basic metadata - will be enhanced by caller
        metadata = {
            "version": "2.0",
            "migrated_date": datetime.now().isoformat(),
            "total_cases": 500
        }

        result = merge_temp_files(temp_dir, group, output_path, metadata)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
