#!/usr/bin/env python3
"""
Validation script for transformed FEEDBACK cases.
Validates schema compliance, field values, and logical consistency.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    case_id: str
    check_name: str
    description: str


@dataclass
class ValidationResult:
    """Holds results for a specific validation check."""
    check_name: str
    passed: int = 0
    failed: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_pass(self) -> None:
        self.passed += 1

    def add_fail(self, case_id: str, description: str) -> None:
        self.failed += 1
        self.issues.append(ValidationIssue(case_id, self.check_name, description))


class FeedbackCaseValidator:
    """Validator for transformed FEEDBACK cases."""

    # Expected new fields
    NEW_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]

    # Expected existing fields
    EXISTING_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]

    # Valid values
    VALID_LABELS = ["YES", "NO", "AMBIGUOUS"]
    VALID_AUTHORS = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]

    # ID pattern: T3-BucketI-XXXX (4 digits, zero-padded)
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.cases: list[dict[str, Any]] = []
        self.results: dict[str, ValidationResult] = {}

    def load_cases(self) -> bool:
        """Load cases from JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.cases = json.load(f)
            return True
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}")
            return False

    def _get_case_identifier(self, case: dict[str, Any]) -> str:
        """Get a readable identifier for a case."""
        return case.get("id", case.get("case_id", "UNKNOWN"))

    def _init_result(self, check_name: str) -> ValidationResult:
        """Initialize or get a validation result."""
        if check_name not in self.results:
            self.results[check_name] = ValidationResult(check_name)
        return self.results[check_name]

    def validate_new_field_presence(self) -> None:
        """Check that all new required fields are present."""
        result = self._init_result("New Field Presence")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            missing = [f for f in self.NEW_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing new fields: {missing}")
            else:
                result.add_pass()

    def validate_existing_field_integrity(self) -> None:
        """Check that all existing required fields are present."""
        result = self._init_result("Existing Field Integrity")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            missing = [f for f in self.EXISTING_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing existing fields: {missing}")
            else:
                result.add_pass()

    def validate_id_format(self) -> None:
        """Check that id follows format T3-BucketI-XXXX."""
        result = self._init_result("ID Format")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            id_value = case.get("id", "")

            if not self.ID_PATTERN.match(id_value):
                result.add_fail(case_id, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")
            else:
                result.add_pass()

    def validate_bucket_value(self) -> None:
        """Check that bucket is exactly 'BucketLarge-I'."""
        result = self._init_result("Bucket Value")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            bucket = case.get("bucket", "")

            if bucket != "BucketLarge-I":
                result.add_fail(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")
            else:
                result.add_pass()

    def validate_label_value(self) -> None:
        """Check that label is YES, NO, or AMBIGUOUS."""
        result = self._init_result("Label Value")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            label = case.get("label", "")

            if label not in self.VALID_LABELS:
                result.add_fail(case_id, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")
            else:
                result.add_pass()

    def validate_is_ambiguous_consistency(self) -> None:
        """Check that is_ambiguous matches (label == 'AMBIGUOUS')."""
        result = self._init_result("is_ambiguous Consistency")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            label = case.get("label", "")
            is_ambiguous = case.get("is_ambiguous")

            expected = label == "AMBIGUOUS"

            if not isinstance(is_ambiguous, bool):
                result.add_fail(case_id, f"is_ambiguous is not a boolean: {type(is_ambiguous).__name__}")
            elif is_ambiguous != expected:
                result.add_fail(
                    case_id,
                    f"is_ambiguous mismatch: is_ambiguous={is_ambiguous}, label='{label}' (expected is_ambiguous={expected})"
                )
            else:
                result.add_pass()

    def validate_trap_fields(self) -> None:
        """Check that trap.type and trap.subtype are non-empty strings."""
        result = self._init_result("Trap Fields")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            trap = case.get("trap", {})

            issues = []

            trap_type = trap.get("type", "")
            if not isinstance(trap_type, str) or not trap_type.strip():
                issues.append("trap.type is empty or not a string")

            trap_subtype = trap.get("subtype", "")
            if not isinstance(trap_subtype, str) or not trap_subtype.strip():
                issues.append("trap.subtype is empty or not a string")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

    def validate_annotation_fields(self) -> None:
        """Check annotation.author, num_annotators, and adjudicated."""
        result = self._init_result("Annotation Fields")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            annotation = case.get("annotation", {})

            issues = []

            author = annotation.get("author", "")
            if author not in self.VALID_AUTHORS:
                issues.append(f"Invalid author: '{author}' (expected one of {self.VALID_AUTHORS})")

            num_annotators = annotation.get("num_annotators")
            if not isinstance(num_annotators, int) or num_annotators < 1:
                issues.append(f"Invalid num_annotators: {num_annotators} (expected integer >= 1)")

            adjudicated = annotation.get("adjudicated")
            if not isinstance(adjudicated, bool):
                issues.append(f"adjudicated is not a boolean: {type(adjudicated).__name__}")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

    def validate_label_consistency(self) -> None:
        """Check logical consistency between label and trap.type."""
        result = self._init_result("Label Consistency")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            label = case.get("label", "")
            trap = case.get("trap", {})
            trap_type = trap.get("type", "")

            issues = []

            # If label="NO", trap.type should not be "NONE" or empty
            if label == "NO":
                if not trap_type or trap_type.upper() == "NONE":
                    issues.append(f"label='NO' but trap.type is '{trap_type}' (expected non-empty, non-NONE)")

            # If label="YES", verify scenario supports the claim (basic check)
            if label == "YES":
                scenario = case.get("scenario", "")
                claim = case.get("claim", "")
                if not scenario or not claim:
                    issues.append("label='YES' but scenario or claim is empty")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

    def validate_pearl_level_requirements(self) -> None:
        """Check Pearl level-specific requirements."""
        result = self._init_result("Pearl Level Requirements")

        for case in self.cases:
            case_id = self._get_case_identifier(case)
            pearl_level = case.get("pearl_level", "")

            issues = []

            # L2 cases must have hidden_structure
            if pearl_level == "L2":
                hidden_structure = case.get("hidden_structure", "")
                if not isinstance(hidden_structure, str):
                    issues.append("L2 case missing hidden_structure field")
                elif not hidden_structure.strip():
                    issues.append("L2 case has empty hidden_structure (should contain explanation)")

            # L3 cases must have ground_truth with verdict and justification
            if pearl_level == "L3":
                ground_truth = case.get("ground_truth", {})
                if not ground_truth:
                    issues.append("L3 case missing ground_truth")
                else:
                    verdict = ground_truth.get("verdict", "")
                    justification = ground_truth.get("justification", "")

                    if not verdict:
                        issues.append("L3 case ground_truth missing verdict")
                    if not justification:
                        issues.append("L3 case ground_truth missing justification")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

    def run_all_validations(self) -> None:
        """Run all validation checks."""
        self.validate_new_field_presence()
        self.validate_existing_field_integrity()
        self.validate_id_format()
        self.validate_bucket_value()
        self.validate_label_value()
        self.validate_is_ambiguous_consistency()
        self.validate_trap_fields()
        self.validate_annotation_fields()
        self.validate_label_consistency()
        self.validate_pearl_level_requirements()

    def generate_report(self) -> str:
        """Generate a validation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("FEEDBACK CASES VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append(f"\nFile: {self.file_path}")
        lines.append(f"Total cases validated: {len(self.cases)}")
        lines.append("")

        # Summary table
        lines.append("-" * 70)
        lines.append(f"{'Check Name':<35} {'Passed':>10} {'Failed':>10} {'Status':>10}")
        lines.append("-" * 70)

        total_passed = 0
        total_failed = 0
        all_issues = []

        for check_name, result in self.results.items():
            status = "PASS" if result.failed == 0 else "FAIL"
            lines.append(f"{check_name:<35} {result.passed:>10} {result.failed:>10} {status:>10}")
            total_passed += result.passed
            total_failed += result.failed
            all_issues.extend(result.issues)

        lines.append("-" * 70)
        lines.append(f"{'TOTAL':<35} {total_passed:>10} {total_failed:>10}")
        lines.append("")

        # Issues detail
        if all_issues:
            lines.append("=" * 70)
            lines.append("ISSUES FOUND")
            lines.append("=" * 70)

            # Group by check name
            issues_by_check: dict[str, list[ValidationIssue]] = {}
            for issue in all_issues:
                if issue.check_name not in issues_by_check:
                    issues_by_check[issue.check_name] = []
                issues_by_check[issue.check_name].append(issue)

            for check_name, issues in issues_by_check.items():
                lines.append(f"\n[{check_name}]")
                for issue in issues:
                    lines.append(f"  - {issue.case_id}: {issue.description}")
        else:
            lines.append("\nNo issues found!")

        # Overall status
        lines.append("")
        lines.append("=" * 70)
        overall_status = "PASS" if total_failed == 0 else "FAIL"
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    file_path = "/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_feedback.json"

    validator = FeedbackCaseValidator(file_path)

    if not validator.load_cases():
        print("\nOVERALL STATUS: FAIL (could not load file)")
        return

    validator.run_all_validations()
    report = validator.generate_report()
    print(report)


if __name__ == "__main__":
    main()
