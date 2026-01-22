#!/usr/bin/env python3
"""
Validation script for transformed GOODHART cases.

Validates the schema and data integrity of transformed_goodhart.json.
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
    field: str
    issue: str
    severity: str = "ERROR"


@dataclass
class ValidationResult:
    """Aggregated validation results."""
    total_cases: int = 0
    checks: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)

    def add_check(self, name: str, passed: int, failed: int) -> None:
        self.checks[name] = {"passed": passed, "failed": failed}

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    @property
    def overall_pass(self) -> bool:
        return len(self.issues) == 0


class GoodhartValidator:
    """Validator for transformed GOODHART cases."""

    # Required new fields (Task 3 schema)
    NEW_REQUIRED_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]

    # Existing required fields (must be preserved)
    EXISTING_REQUIRED_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]

    # Valid label values
    VALID_LABELS = ["YES", "NO", "AMBIGUOUS"]

    # Valid annotation authors
    VALID_AUTHORS = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]

    # ID pattern: T3-BucketI-XXXX (4 digits, zero-padded)
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.cases: list[dict] = []
        self.result = ValidationResult()

    def load_data(self) -> bool:
        """Load and parse the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.cases = json.load(f)
            self.result.total_cases = len(self.cases)
            return True
        except json.JSONDecodeError as e:
            self.result.add_issue(ValidationIssue(
                case_id="N/A",
                field="file",
                issue=f"Invalid JSON: {e}",
                severity="FATAL"
            ))
            return False
        except FileNotFoundError:
            self.result.add_issue(ValidationIssue(
                case_id="N/A",
                field="file",
                issue=f"File not found: {self.file_path}",
                severity="FATAL"
            ))
            return False

    def validate_new_field_presence(self) -> tuple[int, int]:
        """Check that every case has all required new fields."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", case.get("id", "UNKNOWN"))
            missing = [f for f in self.NEW_REQUIRED_FIELDS if f not in case]

            if missing:
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="new_fields",
                    issue=f"Missing required fields: {missing}"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_id_format(self) -> tuple[int, int]:
        """Validate id format: T3-BucketI-XXXX."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            id_value = case.get("id", "")

            if not self.ID_PATTERN.match(id_value):
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="id",
                    issue=f"Invalid id format '{id_value}', expected T3-BucketI-XXXX"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_bucket(self) -> tuple[int, int]:
        """Validate bucket is exactly 'BucketLarge-I'."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            bucket = case.get("bucket", "")

            if bucket != "BucketLarge-I":
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="bucket",
                    issue=f"Invalid bucket '{bucket}', expected 'BucketLarge-I'"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_label(self) -> tuple[int, int]:
        """Validate label is in [YES, NO, AMBIGUOUS]."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            label = case.get("label", "")

            if label not in self.VALID_LABELS:
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="label",
                    issue=f"Invalid label '{label}', expected one of {self.VALID_LABELS}"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_is_ambiguous(self) -> tuple[int, int]:
        """Validate is_ambiguous is boolean and matches label == 'AMBIGUOUS'."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            is_ambiguous = case.get("is_ambiguous")
            label = case.get("label", "")

            # Check type
            if not isinstance(is_ambiguous, bool):
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="is_ambiguous",
                    issue=f"is_ambiguous must be boolean, got {type(is_ambiguous).__name__}"
                ))
                continue

            # Check consistency with label
            expected = (label == "AMBIGUOUS")
            if is_ambiguous != expected:
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="is_ambiguous",
                    issue=f"is_ambiguous={is_ambiguous} doesn't match label='{label}'"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_trap(self) -> tuple[int, int]:
        """Validate trap.type and trap.subtype are non-empty strings."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            trap = case.get("trap", {})

            issues_found = False

            # Validate trap.type
            trap_type = trap.get("type", "")
            if not isinstance(trap_type, str) or not trap_type.strip():
                issues_found = True
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="trap.type",
                    issue=f"trap.type must be a non-empty string, got '{trap_type}'"
                ))

            # Validate trap.subtype
            trap_subtype = trap.get("subtype", "")
            if not isinstance(trap_subtype, str) or not trap_subtype.strip():
                issues_found = True
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="trap.subtype",
                    issue=f"trap.subtype must be a non-empty string, got '{trap_subtype}'"
                ))

            if issues_found:
                failed += 1
            else:
                passed += 1

        return passed, failed

    def validate_annotation(self) -> tuple[int, int]:
        """Validate annotation fields: author, num_annotators, adjudicated."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            annotation = case.get("annotation", {})

            issues_found = False

            # Validate author
            author = annotation.get("author", "")
            if author not in self.VALID_AUTHORS:
                issues_found = True
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="annotation.author",
                    issue=f"Invalid author '{author}', expected one of {self.VALID_AUTHORS}"
                ))

            # Validate num_annotators
            num_annotators = annotation.get("num_annotators")
            if not isinstance(num_annotators, int) or num_annotators < 1:
                issues_found = True
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="annotation.num_annotators",
                    issue=f"num_annotators must be integer >= 1, got {num_annotators}"
                ))

            # Validate adjudicated
            adjudicated = annotation.get("adjudicated")
            if not isinstance(adjudicated, bool):
                issues_found = True
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="annotation.adjudicated",
                    issue=f"adjudicated must be boolean, got {type(adjudicated).__name__}"
                ))

            if issues_found:
                failed += 1
            else:
                passed += 1

        return passed, failed

    def validate_label_consistency(self) -> tuple[int, int]:
        """Validate label consistency with trap type and scenario."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            label = case.get("label", "")
            trap = case.get("trap", {})
            trap_type = trap.get("type", "")

            # If label="NO" -> trap.type should not be "NONE" or empty
            if label == "NO":
                if trap_type.upper() in ["NONE", ""] or not trap_type.strip():
                    failed += 1
                    self.result.add_issue(ValidationIssue(
                        case_id=case_id,
                        field="label_consistency",
                        issue=f"label='NO' but trap.type is '{trap_type}' (should identify the trap)"
                    ))
                else:
                    passed += 1
            elif label == "YES":
                # For YES cases, we just verify it has a scenario (basic check)
                scenario = case.get("scenario", "")
                if not scenario.strip():
                    failed += 1
                    self.result.add_issue(ValidationIssue(
                        case_id=case_id,
                        field="label_consistency",
                        issue="label='YES' but scenario is empty"
                    ))
                else:
                    passed += 1
            else:
                # AMBIGUOUS cases - pass through
                passed += 1

        return passed, failed

    def validate_existing_fields(self) -> tuple[int, int]:
        """Validate all existing required fields are present."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", case.get("id", "UNKNOWN"))
            missing = [f for f in self.EXISTING_REQUIRED_FIELDS if f not in case]

            if missing:
                failed += 1
                self.result.add_issue(ValidationIssue(
                    case_id=case_id,
                    field="existing_fields",
                    issue=f"Missing required existing fields: {missing}"
                ))
            else:
                passed += 1

        return passed, failed

    def validate_pearl_level_requirements(self) -> tuple[int, int]:
        """Validate Pearl level specific requirements."""
        passed = 0
        failed = 0

        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            pearl_level = case.get("pearl_level", "")

            issues_found = False

            # L2 cases must have hidden_structure
            if pearl_level == "L2":
                hidden_structure = case.get("hidden_structure", "")
                if not hidden_structure or not str(hidden_structure).strip():
                    issues_found = True
                    self.result.add_issue(ValidationIssue(
                        case_id=case_id,
                        field="hidden_structure",
                        issue="L2 case missing 'hidden_structure'"
                    ))

            # L3 cases must have ground_truth with verdict and justification
            elif pearl_level == "L3":
                ground_truth = case.get("ground_truth", {})

                if not ground_truth:
                    issues_found = True
                    self.result.add_issue(ValidationIssue(
                        case_id=case_id,
                        field="ground_truth",
                        issue="L3 case missing 'ground_truth'"
                    ))
                else:
                    verdict = ground_truth.get("verdict", "")
                    justification = ground_truth.get("justification", "")

                    if not verdict or not str(verdict).strip():
                        issues_found = True
                        self.result.add_issue(ValidationIssue(
                            case_id=case_id,
                            field="ground_truth.verdict",
                            issue="L3 case missing 'ground_truth.verdict'"
                        ))

                    if not justification or not str(justification).strip():
                        issues_found = True
                        self.result.add_issue(ValidationIssue(
                            case_id=case_id,
                            field="ground_truth.justification",
                            issue="L3 case missing 'ground_truth.justification'"
                        ))

            if issues_found:
                failed += 1
            else:
                passed += 1

        return passed, failed

    def run_all_validations(self) -> ValidationResult:
        """Run all validation checks and return the result."""
        if not self.load_data():
            return self.result

        # Run each validation check
        checks = [
            ("new_field_presence", self.validate_new_field_presence),
            ("id_format", self.validate_id_format),
            ("bucket_value", self.validate_bucket),
            ("label_value", self.validate_label),
            ("is_ambiguous", self.validate_is_ambiguous),
            ("trap_fields", self.validate_trap),
            ("annotation_fields", self.validate_annotation),
            ("label_consistency", self.validate_label_consistency),
            ("existing_fields", self.validate_existing_fields),
            ("pearl_level_requirements", self.validate_pearl_level_requirements),
        ]

        for check_name, check_func in checks:
            passed, failed = check_func()
            self.result.add_check(check_name, passed, failed)

        return self.result


def print_report(result: ValidationResult) -> None:
    """Print the validation report."""
    print("=" * 70)
    print("GOODHART CASES VALIDATION REPORT")
    print("=" * 70)
    print()

    print(f"Total cases validated: {result.total_cases}")
    print()

    print("-" * 70)
    print("CHECK RESULTS")
    print("-" * 70)
    print(f"{'Check Name':<30} {'Passed':>10} {'Failed':>10} {'Status':>10}")
    print("-" * 70)

    for check_name, counts in result.checks.items():
        passed = counts["passed"]
        failed = counts["failed"]
        status = "PASS" if failed == 0 else "FAIL"
        print(f"{check_name:<30} {passed:>10} {failed:>10} {status:>10}")

    print("-" * 70)
    print()

    if result.issues:
        print("-" * 70)
        print(f"ISSUES FOUND ({len(result.issues)} total)")
        print("-" * 70)

        # Group issues by case_id for readability
        issues_by_case: dict[str, list[ValidationIssue]] = {}
        for issue in result.issues:
            if issue.case_id not in issues_by_case:
                issues_by_case[issue.case_id] = []
            issues_by_case[issue.case_id].append(issue)

        for case_id, issues in sorted(issues_by_case.items()):
            print(f"\nCase {case_id}:")
            for issue in issues:
                print(f"  - [{issue.field}] {issue.issue}")
    else:
        print("No issues found.")

    print()
    print("=" * 70)
    overall_status = "PASS" if result.overall_pass else "FAIL"
    print(f"OVERALL STATUS: {overall_status}")
    print("=" * 70)


def main():
    """Main entry point."""
    file_path = "/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_goodhart.json"

    validator = GoodhartValidator(file_path)
    result = validator.run_all_validations()
    print_report(result)

    # Return exit code based on validation result
    return 0 if result.overall_pass else 1


if __name__ == "__main__":
    exit(main())
