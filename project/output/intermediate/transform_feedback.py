#!/usr/bin/env python3
"""Transform FEEDBACK trap type cases from V2.0 to V3.0 schema."""

import json
import re

# Original 45 case IDs (author = "Stanford CS372")
ORIGINAL_45_IDS = [
    "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10",
    "8.11", "8.12", "8.13", "8.14", "8.15", "8.16", "8.17", "8.18", "8.19", "8.20",
    "8.21", "8.22", "8.23", "8.24", "8.25", "8.26", "8.27", "8.28", "8.29", "8.30",
    "8.31", "8.32", "8.33", "8.34", "8.35", "8.36", "8.37", "8.38", "8.39", "8.40",
    "8.41", "8.42", "8.43", "8.44", "8.45", "8.46", "8.47", "8.48", "8.49"
]


def extract_numeric_part(case_id):
    """Extract numeric part from case_id like '8.9' -> 9"""
    match = re.search(r'\.(\d+)$', case_id)
    if match:
        return int(match.group(1))
    return 0


def generate_new_id(case_id):
    """Generate new ID in format T3-BucketI-XXXX"""
    num = extract_numeric_part(case_id)
    return f"T3-BucketI-{num:04d}"


def determine_author(case_id):
    """Determine author based on case_id"""
    if case_id in ORIGINAL_45_IDS:
        return "Stanford CS372"
    num = extract_numeric_part(case_id)
    return "Fernando Torres" if num % 2 == 1 else "Alessandro Balzi"


def extract_claim(scenario):
    """Extract implicit causal claim from scenario for FEEDBACK cases.

    FEEDBACK cases show self-reinforcing cycles that invalidate simple causal assumptions.
    The claim is typically about a simple causal relationship that ignores feedback.
    """
    scenario_lower = scenario.lower()

    if "predicts" in scenario_lower and "self-fulfilling" in scenario_lower:
        return "The prediction model accurately identifies causally independent patterns without influencing outcomes."
    elif "prediction" in scenario_lower:
        return "The predictive model's outputs do not causally affect the phenomena being predicted."
    elif "feedback" in scenario_lower:
        return "The system's outputs do not causally influence its future inputs."
    elif "reinforc" in scenario_lower:
        return "The observed correlations reflect stable causal relationships without self-reinforcing dynamics."
    elif "amplif" in scenario_lower:
        return "The observed patterns reflect genuine causal relationships rather than amplified initial biases."
    elif "bias" in scenario_lower:
        return "The observed correlations are not artifacts of circular causal processes."
    else:
        # Generic feedback claim
        return "The causal relationship between variables is unidirectional without feedback effects."


def transform_feedback_case(case):
    """Transform a FEEDBACK case from V2.0 to V3.0 schema"""
    case_id = case.get("case_id", "")
    annotations = case.get("annotations", {})

    transformed = {
        "id": generate_new_id(case_id),
        "bucket": "BucketLarge-I",
        "pearl_level": annotations.get("pearl_level", "L1"),
        "claim": extract_claim(case.get("scenario", "")),
        "label": "NO",
        "is_ambiguous": False,
        "trap": {
            "type": "FEEDBACK",
            "subtype": annotations.get("trap_subtype", "")
        },
        "gold_rationale": case.get("wise_refusal", ""),
        "annotation": {
            "author": determine_author(case_id),
            "num_annotators": 2,
            "adjudicated": True
        },
        # Keep all existing fields
        "case_id": case_id,
        "scenario": case.get("scenario", ""),
        "variables": case.get("variables", {}),
        "annotations": annotations,
        "hidden_structure": case.get("hidden_structure", ""),
        "correct_reasoning": case.get("correct_reasoning", []),
        "wise_refusal": case.get("wise_refusal", "")
    }

    # Include ground_truth if present
    if "ground_truth" in case:
        transformed["ground_truth"] = case["ground_truth"]

    return transformed


def main():
    # Read the dataset
    with open("/Users/fernandotn/Projects/AGI/project/output/final/GroupI1_datasetV2.0.json", "r") as f:
        data = json.load(f)

    # Get the cases array
    cases = data if isinstance(data, list) else data.get("cases", data.get("data", []))

    # Filter and transform FEEDBACK cases
    feedback_cases = [c for c in cases if c.get("annotations", {}).get("trap_type") == "FEEDBACK"]
    transformed_cases = [transform_feedback_case(c) for c in feedback_cases]

    # Write to output file
    with open("/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_feedback.json", "w") as f:
        json.dump(transformed_cases, f, indent=2)

    print(f"Transformed {len(transformed_cases)} FEEDBACK cases")
    print("\nFirst transformed case:")
    print(json.dumps(transformed_cases[0], indent=2))


if __name__ == "__main__":
    main()
