#!/usr/bin/env python3
"""
Validation script for transformed SPECIFICATION cases.

Validates the structure and content of transformed_specification.json
according to the T3 schema requirements.
"""

import json
import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    case_id: str
    check_name: str
    description: str


@dataclass
class ValidationResult:
    """Aggregates validation results for a single check."""
    check_name: str
    passed: int = 0
    failed: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_pass(self) -> None:
        self.passed += 1

    def add_fail(self, case_id: str, description: str) -> None:
        self.failed += 1
        self.issues.append(ValidationIssue(case_id, self.check_name, description))


class SpecificationValidator:
    """Validator for transformed SPECIFICATION cases."""

    VALID_LABELS = {"YES", "NO", "AMBIGUOUS"}
    VALID_AUTHORS = {"Stanford CS372", "Fernando Torres", "Alessandro Balzi"}
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    NEW_REQUIRED_FIELDS = {
        "id", "bucket", "claim", "label", "is_ambiguous",
        "trap", "gold_rationale", "annotation"
    }

    EXISTING_REQUIRED_FIELDS = {
        "case_id", "scenario", "variables", "annotations",
        "wise_refusal", "correct_reasoning"
    }

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.cases: list[dict[str, Any]] = []
        self.results: dict[str, ValidationResult] = {}

    def load_data(self) -> bool:
        """Load and parse the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.cases = json.load(f)
            return True
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.file_path}")
            return False

    def _init_result(self, check_name: str) -> ValidationResult:
        """Initialize or get a validation result."""
        if check_name not in self.results:
            self.results[check_name] = ValidationResult(check_name)
        return self.results[check_name]

    def _get_case_id(self, case: dict) -> str:
        """Get case identifier for error reporting."""
        return case.get("id", case.get("case_id", "UNKNOWN"))

    def validate_new_field_presence(self, case: dict) -> None:
        """Check that all new required fields are present."""
        result = self._init_result("new_field_presence")
        case_id = self._get_case_id(case)

        missing = self.NEW_REQUIRED_FIELDS - set(case.keys())
        if missing:
            result.add_fail(case_id, f"Missing new fields: {sorted(missing)}")
        else:
            result.add_pass()

    def validate_id_format(self, case: dict) -> None:
        """Validate id field format: T3-BucketI-XXXX."""
        result = self._init_result("id_format")
        case_id = self._get_case_id(case)

        id_value = case.get("id", "")
        if not self.ID_PATTERN.match(str(id_value)):
            result.add_fail(case_id, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")
        else:
            result.add_pass()

    def validate_bucket(self, case: dict) -> None:
        """Validate bucket field is exactly 'BucketLarge-I'."""
        result = self._init_result("bucket_value")
        case_id = self._get_case_id(case)

        bucket = case.get("bucket", "")
        if bucket != "BucketLarge-I":
            result.add_fail(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")
        else:
            result.add_pass()

    def validate_label(self, case: dict) -> None:
        """Validate label field is one of YES, NO, AMBIGUOUS."""
        result = self._init_result("label_value")
        case_id = self._get_case_id(case)

        label = case.get("label", "")
        if label not in self.VALID_LABELS:
            result.add_fail(case_id, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")
        else:
            result.add_pass()

    def validate_is_ambiguous(self, case: dict) -> None:
        """Validate is_ambiguous matches (label == 'AMBIGUOUS')."""
        result = self._init_result("is_ambiguous_consistency")
        case_id = self._get_case_id(case)

        is_ambiguous = case.get("is_ambiguous")
        label = case.get("label", "")
        expected = (label == "AMBIGUOUS")

        if not isinstance(is_ambiguous, bool):
            result.add_fail(case_id, f"is_ambiguous is not boolean: {type(is_ambiguous).__name__}")
        elif is_ambiguous != expected:
            result.add_fail(
                case_id,
                f"is_ambiguous mismatch: is_ambiguous={is_ambiguous} but label='{label}'"
            )
        else:
            result.add_pass()

    def validate_trap(self, case: dict) -> None:
        """Validate trap.type and trap.subtype are non-empty strings."""
        result = self._init_result("trap_fields")
        case_id = self._get_case_id(case)

        trap = case.get("trap", {})
        issues = []

        if not isinstance(trap, dict):
            result.add_fail(case_id, f"trap is not a dict: {type(trap).__name__}")
            return

        trap_type = trap.get("type", "")
        trap_subtype = trap.get("subtype", "")

        if not trap_type or not isinstance(trap_type, str):
            issues.append(f"trap.type is empty or not a string: '{trap_type}'")

        if not trap_subtype or not isinstance(trap_subtype, str):
            issues.append(f"trap.subtype is empty or not a string: '{trap_subtype}'")

        if issues:
            result.add_fail(case_id, "; ".join(issues))
        else:
            result.add_pass()

    def validate_annotation(self, case: dict) -> None:
        """Validate annotation fields: author, num_annotators, adjudicated."""
        result = self._init_result("annotation_fields")
        case_id = self._get_case_id(case)

        annotation = case.get("annotation", {})
        issues = []

        if not isinstance(annotation, dict):
            result.add_fail(case_id, f"annotation is not a dict: {type(annotation).__name__}")
            return

        author = annotation.get("author", "")
        if author not in self.VALID_AUTHORS:
            issues.append(f"Invalid author: '{author}' (expected one of {self.VALID_AUTHORS})")

        num_annotators = annotation.get("num_annotators")
        if not isinstance(num_annotators, int) or num_annotators < 1:
            issues.append(f"Invalid num_annotators: {num_annotators} (expected int >= 1)")

        adjudicated = annotation.get("adjudicated")
        if not isinstance(adjudicated, bool):
            issues.append(f"adjudicated is not boolean: {type(adjudicated).__name__}")

        if issues:
            result.add_fail(case_id, "; ".join(issues))
        else:
            result.add_pass()

    def validate_label_consistency(self, case: dict) -> None:
        """Validate label consistency with trap type."""
        result = self._init_result("label_consistency")
        case_id = self._get_case_id(case)

        label = case.get("label", "")
        trap = case.get("trap", {})
        trap_type = trap.get("type", "") if isinstance(trap, dict) else ""

        # If label="NO" -> trap.type should not be "NONE" or empty
        if label == "NO":
            if not trap_type or trap_type.upper() == "NONE":
                result.add_fail(
                    case_id,
                    f"label='NO' but trap.type is empty or 'NONE': '{trap_type}'"
                )
                return

        # If label="YES" -> verify scenario supports the claim (basic check)
        if label == "YES":
            scenario = case.get("scenario", "")
            # Basic heuristic: YES cases should not describe obvious failures
            failure_indicators = ["fails", "crashes", "doesn't work", "catastrophic"]
            scenario_lower = scenario.lower()
            for indicator in failure_indicators:
                if indicator in scenario_lower:
                    result.add_fail(
                        case_id,
                        f"label='YES' but scenario contains failure indicator: '{indicator}'"
                    )
                    return

        result.add_pass()

    def validate_existing_field_integrity(self, case: dict) -> None:
        """Check that all existing required fields are present."""
        result = self._init_result("existing_field_integrity")
        case_id = self._get_case_id(case)

        missing = self.EXISTING_REQUIRED_FIELDS - set(case.keys())
        if missing:
            result.add_fail(case_id, f"Missing existing fields: {sorted(missing)}")
        else:
            result.add_pass()

    def validate_pearl_level_requirements(self, case: dict) -> None:
        """Validate Pearl Level specific requirements."""
        result = self._init_result("pearl_level_requirements")
        case_id = self._get_case_id(case)

        pearl_level = case.get("pearl_level", "")

        # L2 cases must have hidden_structure
        if pearl_level == "L2":
            hidden_structure = case.get("hidden_structure")
            if hidden_structure is None:
                result.add_fail(case_id, "L2 case missing 'hidden_structure' field")
                return
            # Note: empty string is allowed, just field must exist

        # L3 cases must have ground_truth with verdict and justification
        if pearl_level == "L3":
            ground_truth = case.get("ground_truth")
            if not ground_truth:
                result.add_fail(case_id, "L3 case missing 'ground_truth' field")
                return

            if not isinstance(ground_truth, dict):
                result.add_fail(case_id, f"ground_truth is not a dict: {type(ground_truth).__name__}")
                return

            issues = []
            if "verdict" not in ground_truth:
                issues.append("ground_truth missing 'verdict'")
            if "justification" not in ground_truth:
                issues.append("ground_truth missing 'justification'")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
                return

        result.add_pass()

    def validate_all(self) -> bool:
        """Run all validations on all cases."""
        if not self.load_data():
            return False

        for case in self.cases:
            # New field checks
            self.validate_new_field_presence(case)
            self.validate_id_format(case)
            self.validate_bucket(case)
            self.validate_label(case)
            self.validate_is_ambiguous(case)
            self.validate_trap(case)
            self.validate_annotation(case)

            # Label consistency
            self.validate_label_consistency(case)

            # Existing field integrity
            self.validate_existing_field_integrity(case)

            # Pearl level requirements
            self.validate_pearl_level_requirements(case)

        return True

    def generate_report(self) -> str:
        """Generate a validation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION REPORT: transformed_specification.json")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"File: {self.file_path}")
        lines.append(f"Total cases validated: {len(self.cases)}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("VALIDATION RESULTS BY CHECK")
        lines.append("-" * 70)

        total_passed = 0
        total_failed = 0
        all_issues: list[ValidationIssue] = []

        for check_name, result in sorted(self.results.items()):
            status = "PASS" if result.failed == 0 else "FAIL"
            lines.append(f"  {check_name}: {status} ({result.passed} passed, {result.failed} failed)")
            total_passed += result.passed
            total_failed += result.failed
            all_issues.extend(result.issues)

        lines.append("")
        lines.append("-" * 70)
        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"  Total checks passed: {total_passed}")
        lines.append(f"  Total checks failed: {total_failed}")

        if all_issues:
            lines.append("")
            lines.append("-" * 70)
            lines.append(f"ISSUES FOUND ({len(all_issues)} total)")
            lines.append("-" * 70)
            for issue in all_issues:
                lines.append(f"  [{issue.case_id}] {issue.check_name}: {issue.description}")

        lines.append("")
        lines.append("=" * 70)
        overall_status = "PASS" if total_failed == 0 else "FAIL"
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    file_path = Path("/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_specification.json")

    validator = SpecificationValidator(file_path)

    if validator.validate_all():
        report = validator.generate_report()
        print(report)

        # Exit with appropriate code
        total_failed = sum(r.failed for r in validator.results.values())
        exit(0 if total_failed == 0 else 1)
    else:
        exit(1)


if __name__ == "__main__":
    main()
