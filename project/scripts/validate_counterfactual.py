#!/usr/bin/env python3
"""
Validation script for transformed COUNTERFACTUAL cases.
Validates schema compliance, field values, and data integrity.
"""

import json
import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Stores validation results for reporting."""
    total_cases: int = 0
    checks: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)

    def add_check(self, check_name: str, passed: bool) -> None:
        if check_name not in self.checks:
            self.checks[check_name] = {"passed": 0, "failed": 0}
        if passed:
            self.checks[check_name]["passed"] += 1
        else:
            self.checks[check_name]["failed"] += 1

    def add_issue(self, case_id: str, issue: str) -> None:
        self.issues.append({"case_id": case_id, "issue": issue})

    @property
    def overall_passed(self) -> bool:
        return len(self.issues) == 0


def validate_id_format(case: dict, result: ValidationResult) -> bool:
    """Validate id format: T3-BucketI-XXXX (4 digits, zero-padded)."""
    case_id = case.get("case_id", "UNKNOWN")
    id_value = case.get("id", "")

    pattern = r"^T3-BucketI-\d{4}$"
    passed = bool(re.match(pattern, id_value))
    result.add_check("id_format", passed)

    if not passed:
        result.add_issue(case_id, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")

    return passed


def validate_bucket(case: dict, result: ValidationResult) -> bool:
    """Validate bucket is exactly 'BucketLarge-I'."""
    case_id = case.get("case_id", "UNKNOWN")
    bucket = case.get("bucket", "")

    passed = bucket == "BucketLarge-I"
    result.add_check("bucket_value", passed)

    if not passed:
        result.add_issue(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")

    return passed


def validate_label(case: dict, result: ValidationResult) -> bool:
    """Validate label is in [YES, NO, AMBIGUOUS]."""
    case_id = case.get("case_id", "UNKNOWN")
    label = case.get("label", "")

    valid_labels = ["YES", "NO", "AMBIGUOUS"]
    passed = label in valid_labels
    result.add_check("label_value", passed)

    if not passed:
        result.add_issue(case_id, f"Invalid label: '{label}' (expected one of {valid_labels})")

    return passed


def validate_is_ambiguous(case: dict, result: ValidationResult) -> bool:
    """Validate is_ambiguous matches (label == AMBIGUOUS)."""
    case_id = case.get("case_id", "UNKNOWN")
    label = case.get("label", "")
    is_ambiguous = case.get("is_ambiguous")

    expected = (label == "AMBIGUOUS")
    passed = is_ambiguous == expected
    result.add_check("is_ambiguous_consistency", passed)

    if not passed:
        result.add_issue(
            case_id,
            f"is_ambiguous mismatch: is_ambiguous={is_ambiguous}, label='{label}' (expected is_ambiguous={expected})"
        )

    return passed


def validate_trap(case: dict, result: ValidationResult) -> bool:
    """Validate trap.type and trap.subtype are non-empty strings."""
    case_id = case.get("case_id", "UNKNOWN")
    trap = case.get("trap", {})

    trap_type = trap.get("type", "")
    trap_subtype = trap.get("subtype", "")

    type_valid = isinstance(trap_type, str) and len(trap_type.strip()) > 0
    subtype_valid = isinstance(trap_subtype, str) and len(trap_subtype.strip()) > 0

    passed = type_valid and subtype_valid
    result.add_check("trap_fields", passed)

    if not type_valid:
        result.add_issue(case_id, f"Invalid trap.type: '{trap_type}' (must be non-empty string)")
    if not subtype_valid:
        result.add_issue(case_id, f"Invalid trap.subtype: '{trap_subtype}' (must be non-empty string)")

    return passed


def validate_annotation(case: dict, result: ValidationResult) -> bool:
    """Validate annotation fields."""
    case_id = case.get("case_id", "UNKNOWN")
    annotation = case.get("annotation", {})

    valid_authors = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]

    author = annotation.get("author", "")
    num_annotators = annotation.get("num_annotators")
    adjudicated = annotation.get("adjudicated")

    issues_found = []

    # Check author
    author_valid = author in valid_authors
    if not author_valid:
        issues_found.append(f"Invalid annotation.author: '{author}' (expected one of {valid_authors})")

    # Check num_annotators
    num_valid = isinstance(num_annotators, int) and num_annotators >= 1
    if not num_valid:
        issues_found.append(f"Invalid annotation.num_annotators: {num_annotators} (expected integer >= 1)")

    # Check adjudicated
    adj_valid = isinstance(adjudicated, bool)
    if not adj_valid:
        issues_found.append(f"Invalid annotation.adjudicated: {adjudicated} (expected boolean)")

    passed = author_valid and num_valid and adj_valid
    result.add_check("annotation_fields", passed)

    for issue in issues_found:
        result.add_issue(case_id, issue)

    return passed


def validate_new_fields_presence(case: dict, result: ValidationResult) -> bool:
    """Validate all new required fields are present."""
    case_id = case.get("case_id", "UNKNOWN")
    required_fields = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]

    missing = [f for f in required_fields if f not in case]
    passed = len(missing) == 0
    result.add_check("new_fields_presence", passed)

    if not passed:
        result.add_issue(case_id, f"Missing new fields: {missing}")

    return passed


def validate_existing_fields_integrity(case: dict, result: ValidationResult) -> bool:
    """Validate existing required fields are present."""
    case_id = case.get("case_id", "UNKNOWN")
    required_fields = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]

    missing = [f for f in required_fields if f not in case]
    passed = len(missing) == 0
    result.add_check("existing_fields_integrity", passed)

    if not passed:
        result.add_issue(case_id, f"Missing existing fields: {missing}")

    return passed


def validate_label_consistency(case: dict, result: ValidationResult) -> bool:
    """Validate label consistency with trap.type."""
    case_id = case.get("case_id", "UNKNOWN")
    label = case.get("label", "")
    trap = case.get("trap", {})
    trap_type = trap.get("type", "")

    passed = True

    # If label="NO" -> trap.type should not be "NONE" or empty
    if label == "NO":
        if trap_type.upper() == "NONE" or not trap_type.strip():
            passed = False
            result.add_issue(
                case_id,
                f"Label consistency error: label='NO' but trap.type='{trap_type}' (should not be NONE or empty)"
            )

    result.add_check("label_consistency", passed)
    return passed


def validate_pearl_level_requirements(case: dict, result: ValidationResult) -> bool:
    """Validate Pearl level specific requirements."""
    case_id = case.get("case_id", "UNKNOWN")
    pearl_level = case.get("pearl_level", "")

    passed = True

    # L2 cases must have hidden_structure
    if pearl_level == "L2":
        if "hidden_structure" not in case or not case.get("hidden_structure"):
            passed = False
            result.add_issue(case_id, f"L2 case missing 'hidden_structure' field")

    # L3 cases must have ground_truth with verdict and justification
    if pearl_level == "L3":
        ground_truth = case.get("ground_truth", {})
        if not ground_truth:
            passed = False
            result.add_issue(case_id, f"L3 case missing 'ground_truth' field")
        else:
            if "verdict" not in ground_truth:
                passed = False
                result.add_issue(case_id, f"L3 case ground_truth missing 'verdict'")
            if "justification" not in ground_truth:
                passed = False
                result.add_issue(case_id, f"L3 case ground_truth missing 'justification'")

    result.add_check("pearl_level_requirements", passed)
    return passed


def validate_case(case: dict, result: ValidationResult) -> bool:
    """Run all validations on a single case."""
    all_passed = True

    # New field presence
    all_passed &= validate_new_fields_presence(case, result)

    # Field values
    all_passed &= validate_id_format(case, result)
    all_passed &= validate_bucket(case, result)
    all_passed &= validate_label(case, result)
    all_passed &= validate_is_ambiguous(case, result)
    all_passed &= validate_trap(case, result)
    all_passed &= validate_annotation(case, result)

    # Label consistency
    all_passed &= validate_label_consistency(case, result)

    # Existing field integrity
    all_passed &= validate_existing_fields_integrity(case, result)

    # Pearl level requirements
    all_passed &= validate_pearl_level_requirements(case, result)

    return all_passed


def generate_report(result: ValidationResult) -> str:
    """Generate a formatted validation report."""
    lines = []
    lines.append("=" * 70)
    lines.append("COUNTERFACTUAL CASES VALIDATION REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Summary
    lines.append(f"Total cases validated: {result.total_cases}")
    lines.append("")

    # Pass/Fail counts per check
    lines.append("-" * 70)
    lines.append("CHECK RESULTS")
    lines.append("-" * 70)
    lines.append(f"{'Check Name':<35} {'Passed':>10} {'Failed':>10}")
    lines.append("-" * 70)

    for check_name, counts in sorted(result.checks.items()):
        lines.append(f"{check_name:<35} {counts['passed']:>10} {counts['failed']:>10}")

    lines.append("-" * 70)
    lines.append("")

    # Issues found
    lines.append("-" * 70)
    lines.append("ISSUES FOUND")
    lines.append("-" * 70)

    if result.issues:
        for i, issue in enumerate(result.issues, 1):
            lines.append(f"{i:3}. Case {issue['case_id']}: {issue['issue']}")
    else:
        lines.append("No issues found.")

    lines.append("-" * 70)
    lines.append("")

    # Overall status
    status = "PASS" if result.overall_passed else "FAIL"
    lines.append("=" * 70)
    lines.append(f"OVERALL STATUS: {status}")
    lines.append(f"Total issues: {len(result.issues)}")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main validation entry point."""
    input_path = Path("/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_counterfactual.json")

    # Load data
    print(f"Loading data from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Loaded {len(cases)} cases")

    # Validate
    result = ValidationResult()
    result.total_cases = len(cases)

    for case in cases:
        validate_case(case, result)

    # Generate and print report
    report = generate_report(result)
    print(report)

    # Return exit code based on validation
    return 0 if result.overall_passed else 1


if __name__ == "__main__":
    exit(main())
