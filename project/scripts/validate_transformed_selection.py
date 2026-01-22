#!/usr/bin/env python3
"""
Validation script for transformed SELECTION_SPURIOUS cases.

Validates the structure and content of transformed cases according to
the T3-BucketI schema requirements.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a case."""
    case_id: str
    check_name: str
    description: str


@dataclass
class ValidationResult:
    """Aggregates validation results for all checks."""
    total_cases: int = 0
    checks: dict[str, dict[str, int]] = field(default_factory=dict)
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_check_result(self, check_name: str, passed: bool):
        """Record a check result."""
        if check_name not in self.checks:
            self.checks[check_name] = {"pass": 0, "fail": 0}
        if passed:
            self.checks[check_name]["pass"] += 1
        else:
            self.checks[check_name]["fail"] += 1

    def add_issue(self, case_id: str, check_name: str, description: str):
        """Record a validation issue."""
        self.issues.append(ValidationIssue(case_id, check_name, description))

    @property
    def overall_passed(self) -> bool:
        """Returns True if no issues were found."""
        return len(self.issues) == 0


class TransformedSelectionValidator:
    """Validator for transformed SELECTION_SPURIOUS cases."""

    # Required new fields
    NEW_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]

    # Required existing fields
    EXISTING_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]

    # Valid label values
    VALID_LABELS = ["YES", "NO", "AMBIGUOUS"]

    # Valid annotation authors
    VALID_AUTHORS = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]

    # ID pattern: T3-BucketI-XXXX (4 digits, zero-padded)
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.result = ValidationResult()
        self.cases: list[dict[str, Any]] = []

    def load_data(self) -> bool:
        """Load JSON data from file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.cases = json.load(f)
            self.result.total_cases = len(self.cases)
            return True
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in file: {e}")
            return False
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.file_path}")
            return False

    def validate_new_field_presence(self, case: dict) -> None:
        """Check that all required new fields are present."""
        case_id = case.get("case_id", case.get("id", "UNKNOWN"))

        for field_name in self.NEW_FIELDS:
            check_name = f"new_field_{field_name}"
            if field_name in case:
                self.result.add_check_result(check_name, True)
            else:
                self.result.add_check_result(check_name, False)
                self.result.add_issue(case_id, check_name, f"Missing required field: {field_name}")

    def validate_id_format(self, case: dict) -> None:
        """Validate id format: T3-BucketI-XXXX."""
        case_id = case.get("case_id", "UNKNOWN")
        check_name = "id_format"

        id_value = case.get("id", "")
        if self.ID_PATTERN.match(id_value):
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")

    def validate_bucket(self, case: dict) -> None:
        """Validate bucket is exactly 'BucketLarge-I'."""
        case_id = case.get("case_id", "UNKNOWN")
        check_name = "bucket_value"

        bucket = case.get("bucket", "")
        if bucket == "BucketLarge-I":
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")

    def validate_label(self, case: dict) -> None:
        """Validate label is in valid set."""
        case_id = case.get("case_id", "UNKNOWN")
        check_name = "label_value"

        label = case.get("label", "")
        if label in self.VALID_LABELS:
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")

    def validate_is_ambiguous(self, case: dict) -> None:
        """Validate is_ambiguous is boolean and matches label."""
        case_id = case.get("case_id", "UNKNOWN")

        # Check boolean type
        check_name = "is_ambiguous_type"
        is_ambiguous = case.get("is_ambiguous")
        if isinstance(is_ambiguous, bool):
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"is_ambiguous must be boolean, got: {type(is_ambiguous).__name__}")
            return  # Skip consistency check if type is wrong

        # Check consistency with label
        check_name = "is_ambiguous_consistency"
        label = case.get("label", "")
        expected_ambiguous = (label == "AMBIGUOUS")
        if is_ambiguous == expected_ambiguous:
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(
                case_id, check_name,
                f"is_ambiguous={is_ambiguous} inconsistent with label='{label}' (expected is_ambiguous={expected_ambiguous})"
            )

    def validate_trap(self, case: dict) -> None:
        """Validate trap.type and trap.subtype are non-empty strings."""
        case_id = case.get("case_id", "UNKNOWN")
        trap = case.get("trap", {})

        # Check trap.type
        check_name = "trap_type"
        trap_type = trap.get("type", "") if isinstance(trap, dict) else ""
        if isinstance(trap_type, str) and trap_type.strip():
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"trap.type must be non-empty string, got: '{trap_type}'")

        # Check trap.subtype
        check_name = "trap_subtype"
        trap_subtype = trap.get("subtype", "") if isinstance(trap, dict) else ""
        if isinstance(trap_subtype, str) and trap_subtype.strip():
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"trap.subtype must be non-empty string, got: '{trap_subtype}'")

    def validate_annotation(self, case: dict) -> None:
        """Validate annotation fields."""
        case_id = case.get("case_id", "UNKNOWN")
        annotation = case.get("annotation", {})

        # Check author
        check_name = "annotation_author"
        author = annotation.get("author", "") if isinstance(annotation, dict) else ""
        if author in self.VALID_AUTHORS:
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"Invalid annotation.author: '{author}' (expected one of {self.VALID_AUTHORS})")

        # Check num_annotators
        check_name = "annotation_num_annotators"
        num_annotators = annotation.get("num_annotators") if isinstance(annotation, dict) else None
        if isinstance(num_annotators, int) and num_annotators >= 1:
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"annotation.num_annotators must be integer >= 1, got: {num_annotators}")

        # Check adjudicated
        check_name = "annotation_adjudicated"
        adjudicated = annotation.get("adjudicated") if isinstance(annotation, dict) else None
        if isinstance(adjudicated, bool):
            self.result.add_check_result(check_name, True)
        else:
            self.result.add_check_result(check_name, False)
            self.result.add_issue(case_id, check_name, f"annotation.adjudicated must be boolean, got: {type(adjudicated).__name__}")

    def validate_label_consistency(self, case: dict) -> None:
        """Validate label consistency with trap type."""
        case_id = case.get("case_id", "UNKNOWN")
        label = case.get("label", "")
        trap = case.get("trap", {})
        trap_type = trap.get("type", "") if isinstance(trap, dict) else ""

        # If label="NO", trap.type should not be "NONE" or empty
        check_name = "label_trap_consistency"
        if label == "NO":
            if trap_type and trap_type.upper() != "NONE":
                self.result.add_check_result(check_name, True)
            else:
                self.result.add_check_result(check_name, False)
                self.result.add_issue(case_id, check_name, f"label='NO' but trap.type is '{trap_type}' (should be non-empty and not 'NONE')")
        else:
            # For YES and AMBIGUOUS labels, just pass this check
            self.result.add_check_result(check_name, True)

    def validate_existing_field_integrity(self, case: dict) -> None:
        """Check that all required existing fields are present."""
        case_id = case.get("case_id", case.get("id", "UNKNOWN"))

        for field_name in self.EXISTING_FIELDS:
            check_name = f"existing_field_{field_name}"
            if field_name in case:
                self.result.add_check_result(check_name, True)
            else:
                self.result.add_check_result(check_name, False)
                self.result.add_issue(case_id, check_name, f"Missing required existing field: {field_name}")

    def validate_pearl_level_requirements(self, case: dict) -> None:
        """Validate Pearl level specific requirements."""
        case_id = case.get("case_id", "UNKNOWN")
        pearl_level = case.get("pearl_level", case.get("annotations", {}).get("pearl_level", ""))

        # L2 cases must have hidden_structure
        if pearl_level == "L2":
            check_name = "l2_hidden_structure"
            hidden_structure = case.get("hidden_structure", "")
            if hidden_structure and isinstance(hidden_structure, str) and hidden_structure.strip():
                self.result.add_check_result(check_name, True)
            else:
                self.result.add_check_result(check_name, False)
                self.result.add_issue(case_id, check_name, "L2 case missing or empty 'hidden_structure' field")

        # L3 cases must have ground_truth with verdict and justification
        if pearl_level == "L3":
            check_name = "l3_ground_truth"
            ground_truth = case.get("ground_truth", {})

            if isinstance(ground_truth, dict):
                verdict = ground_truth.get("verdict", "")
                justification = ground_truth.get("justification", "")

                if verdict and justification:
                    self.result.add_check_result(check_name, True)
                else:
                    self.result.add_check_result(check_name, False)
                    missing = []
                    if not verdict:
                        missing.append("verdict")
                    if not justification:
                        missing.append("justification")
                    self.result.add_issue(case_id, check_name, f"L3 case ground_truth missing: {', '.join(missing)}")
            else:
                self.result.add_check_result(check_name, False)
                self.result.add_issue(case_id, check_name, "L3 case missing 'ground_truth' object")

    def validate_case(self, case: dict) -> None:
        """Run all validations on a single case."""
        self.validate_new_field_presence(case)
        self.validate_id_format(case)
        self.validate_bucket(case)
        self.validate_label(case)
        self.validate_is_ambiguous(case)
        self.validate_trap(case)
        self.validate_annotation(case)
        self.validate_label_consistency(case)
        self.validate_existing_field_integrity(case)
        self.validate_pearl_level_requirements(case)

    def validate_all(self) -> ValidationResult:
        """Run validation on all cases."""
        if not self.load_data():
            return self.result

        for case in self.cases:
            self.validate_case(case)

        return self.result

    def generate_report(self) -> str:
        """Generate a formatted validation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION REPORT: Transformed SELECTION_SPURIOUS Cases")
        lines.append("=" * 70)
        lines.append(f"File: {self.file_path}")
        lines.append(f"Total cases validated: {self.result.total_cases}")
        lines.append("")

        # Check results summary
        lines.append("-" * 70)
        lines.append("CHECK RESULTS SUMMARY")
        lines.append("-" * 70)

        # Group checks by category
        check_categories = {
            "New Field Presence": [k for k in self.result.checks if k.startswith("new_field_")],
            "Field Values": ["id_format", "bucket_value", "label_value", "is_ambiguous_type",
                           "is_ambiguous_consistency", "trap_type", "trap_subtype",
                           "annotation_author", "annotation_num_annotators", "annotation_adjudicated"],
            "Label Consistency": ["label_trap_consistency"],
            "Existing Field Integrity": [k for k in self.result.checks if k.startswith("existing_field_")],
            "Pearl Level Requirements": ["l2_hidden_structure", "l3_ground_truth"],
        }

        for category, check_names in check_categories.items():
            lines.append(f"\n{category}:")
            for check_name in check_names:
                if check_name in self.result.checks:
                    stats = self.result.checks[check_name]
                    total = stats["pass"] + stats["fail"]
                    status = "PASS" if stats["fail"] == 0 else "FAIL"
                    lines.append(f"  [{status}] {check_name}: {stats['pass']}/{total} passed")

        # Issues list
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"ISSUES FOUND: {len(self.result.issues)}")
        lines.append("-" * 70)

        if self.result.issues:
            # Group issues by case_id
            issues_by_case: dict[str, list[ValidationIssue]] = {}
            for issue in self.result.issues:
                if issue.case_id not in issues_by_case:
                    issues_by_case[issue.case_id] = []
                issues_by_case[issue.case_id].append(issue)

            for case_id, issues in sorted(issues_by_case.items()):
                lines.append(f"\nCase {case_id}:")
                for issue in issues:
                    lines.append(f"  - [{issue.check_name}] {issue.description}")
        else:
            lines.append("\nNo issues found!")

        # Overall status
        lines.append("")
        lines.append("=" * 70)
        overall_status = "PASS" if self.result.overall_passed else "FAIL"
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    """Main entry point."""
    file_path = "/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_selection.json"

    validator = TransformedSelectionValidator(file_path)
    validator.validate_all()

    report = validator.generate_report()
    print(report)

    # Return exit code based on validation result
    return 0 if validator.result.overall_passed else 1


if __name__ == "__main__":
    exit(main())
