#!/usr/bin/env python3
"""
Validation script for transformed INSTRUMENTAL cases.
Validates schema compliance, field values, and consistency rules.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Holds validation results for a single check."""
    name: str
    passed: int = 0
    failed: int = 0
    issues: list = field(default_factory=list)

    def add_pass(self) -> None:
        self.passed += 1

    def add_fail(self, case_id: str, issue: str) -> None:
        self.failed += 1
        self.issues.append((case_id, issue))

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def is_passing(self) -> bool:
        return self.failed == 0


class InstrumentalValidator:
    """Validator for transformed instrumental cases."""

    # Required new fields
    NEW_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]

    # Required existing fields
    EXISTING_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]

    # Valid values
    VALID_LABELS = {"YES", "NO", "AMBIGUOUS"}
    VALID_AUTHORS = {"Stanford CS372", "Fernando Torres", "Alessandro Balzi"}

    # ID pattern: T3-BucketI-XXXX (4 digits, zero-padded)
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data: list[dict[str, Any]] = []
        self.results: dict[str, ValidationResult] = {}

    def load_data(self) -> bool:
        """Load JSON data from file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"ERROR: Failed to load file: {e}")
            return False

    def _init_result(self, name: str) -> ValidationResult:
        """Initialize a validation result."""
        result = ValidationResult(name=name)
        self.results[name] = result
        return result

    def validate_new_field_presence(self) -> ValidationResult:
        """Check that all new required fields are present."""
        result = self._init_result("New Field Presence")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            missing = [f for f in self.NEW_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing new fields: {missing}")
            else:
                result.add_pass()

        return result

    def validate_existing_field_integrity(self) -> ValidationResult:
        """Check that all existing required fields are present."""
        result = self._init_result("Existing Field Integrity")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            missing = [f for f in self.EXISTING_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing existing fields: {missing}")
            else:
                result.add_pass()

        return result

    def validate_id_format(self) -> ValidationResult:
        """Validate id format: T3-BucketI-XXXX."""
        result = self._init_result("ID Format")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            id_value = case.get("id", "")

            if not self.ID_PATTERN.match(id_value):
                result.add_fail(case_id, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")
            else:
                result.add_pass()

        return result

    def validate_bucket_value(self) -> ValidationResult:
        """Validate bucket is exactly 'BucketLarge-I'."""
        result = self._init_result("Bucket Value")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            bucket = case.get("bucket", "")

            if bucket != "BucketLarge-I":
                result.add_fail(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")
            else:
                result.add_pass()

        return result

    def validate_label_values(self) -> ValidationResult:
        """Validate label is in valid set."""
        result = self._init_result("Label Values")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            label = case.get("label", "")

            if label not in self.VALID_LABELS:
                result.add_fail(case_id, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")
            else:
                result.add_pass()

        return result

    def validate_is_ambiguous_consistency(self) -> ValidationResult:
        """Validate is_ambiguous matches (label == 'AMBIGUOUS')."""
        result = self._init_result("is_ambiguous Consistency")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            label = case.get("label", "")
            is_ambiguous = case.get("is_ambiguous")

            expected = (label == "AMBIGUOUS")

            if not isinstance(is_ambiguous, bool):
                result.add_fail(case_id, f"is_ambiguous is not boolean: {type(is_ambiguous).__name__}")
            elif is_ambiguous != expected:
                result.add_fail(case_id, f"is_ambiguous={is_ambiguous} but label='{label}' (expected is_ambiguous={expected})")
            else:
                result.add_pass()

        return result

    def validate_trap_fields(self) -> ValidationResult:
        """Validate trap.type and trap.subtype are non-empty strings."""
        result = self._init_result("Trap Fields")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            trap = case.get("trap", {})

            issues = []

            trap_type = trap.get("type", "")
            if not trap_type or not isinstance(trap_type, str):
                issues.append(f"trap.type is empty or not a string: '{trap_type}'")

            trap_subtype = trap.get("subtype", "")
            if not trap_subtype or not isinstance(trap_subtype, str):
                issues.append(f"trap.subtype is empty or not a string: '{trap_subtype}'")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_annotation_fields(self) -> ValidationResult:
        """Validate annotation object fields."""
        result = self._init_result("Annotation Fields")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            annotation = case.get("annotation", {})

            issues = []

            # Check author
            author = annotation.get("author", "")
            if author not in self.VALID_AUTHORS:
                issues.append(f"Invalid annotation.author: '{author}' (expected one of {self.VALID_AUTHORS})")

            # Check num_annotators
            num_annotators = annotation.get("num_annotators")
            if not isinstance(num_annotators, int) or num_annotators < 1:
                issues.append(f"Invalid annotation.num_annotators: {num_annotators} (expected int >= 1)")

            # Check adjudicated
            adjudicated = annotation.get("adjudicated")
            if not isinstance(adjudicated, bool):
                issues.append(f"annotation.adjudicated is not boolean: {type(adjudicated).__name__}")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_label_consistency(self) -> ValidationResult:
        """Validate label consistency with trap and scenario."""
        result = self._init_result("Label Consistency")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            label = case.get("label", "")
            trap = case.get("trap", {})

            issues = []

            # If label="NO" -> trap.type should not be "NONE" or empty
            if label == "NO":
                trap_type = trap.get("type", "")
                if not trap_type or trap_type.upper() == "NONE":
                    issues.append(f"label='NO' but trap.type is '{trap_type}' (should indicate a trap)")

            # If label="YES" -> verify scenario supports the claim (basic check)
            if label == "YES":
                scenario = case.get("scenario", "")
                claim = case.get("claim", "")
                if not scenario or not claim:
                    issues.append("label='YES' but scenario or claim is empty")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_pearl_level_requirements(self) -> ValidationResult:
        """Validate Pearl level specific requirements."""
        result = self._init_result("Pearl Level Requirements")

        for case in self.data:
            case_id = case.get("case_id", "UNKNOWN")
            pearl_level = case.get("pearl_level", case.get("annotations", {}).get("pearl_level", ""))

            issues = []

            # L2 cases must have hidden_structure
            if pearl_level == "L2":
                if "hidden_structure" not in case or not case.get("hidden_structure"):
                    issues.append("L2 case missing 'hidden_structure' field")

            # L3 cases must have ground_truth with verdict and justification
            if pearl_level == "L3":
                ground_truth = case.get("ground_truth", {})
                if not ground_truth:
                    issues.append("L3 case missing 'ground_truth' field")
                else:
                    if "verdict" not in ground_truth:
                        issues.append("L3 ground_truth missing 'verdict'")
                    if "justification" not in ground_truth:
                        issues.append("L3 ground_truth missing 'justification'")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def run_all_validations(self) -> None:
        """Run all validation checks."""
        self.validate_new_field_presence()
        self.validate_existing_field_integrity()
        self.validate_id_format()
        self.validate_bucket_value()
        self.validate_label_values()
        self.validate_is_ambiguous_consistency()
        self.validate_trap_fields()
        self.validate_annotation_fields()
        self.validate_label_consistency()
        self.validate_pearl_level_requirements()

    def generate_report(self) -> str:
        """Generate validation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("TRANSFORMED INSTRUMENTAL CASES - VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append(f"\nFile: {self.file_path}")
        lines.append(f"Total cases validated: {len(self.data)}")

        # Pearl level breakdown
        l2_count = sum(1 for c in self.data if c.get("pearl_level") == "L2")
        l3_count = sum(1 for c in self.data if c.get("pearl_level") == "L3")
        lines.append(f"  - L2 cases: {l2_count}")
        lines.append(f"  - L3 cases: {l3_count}")

        lines.append("\n" + "-" * 70)
        lines.append("VALIDATION RESULTS BY CHECK")
        lines.append("-" * 70)

        all_passed = True
        total_issues = []

        for name, result in self.results.items():
            status = "PASS" if result.is_passing else "FAIL"
            if not result.is_passing:
                all_passed = False
            lines.append(f"\n{name}:")
            lines.append(f"  Status: {status}")
            lines.append(f"  Passed: {result.passed}/{result.total}")
            lines.append(f"  Failed: {result.failed}/{result.total}")

            if result.issues:
                total_issues.extend(result.issues)

        # List all issues
        if total_issues:
            lines.append("\n" + "-" * 70)
            lines.append("DETAILED ISSUES")
            lines.append("-" * 70)
            for case_id, issue in total_issues:
                lines.append(f"\n  Case {case_id}:")
                lines.append(f"    {issue}")

        # Overall status
        lines.append("\n" + "=" * 70)
        overall_status = "PASS" if all_passed else "FAIL"
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append(f"Total issues found: {len(total_issues)}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    """Main entry point."""
    file_path = "/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_instrumental.json"

    validator = InstrumentalValidator(file_path)

    if not validator.load_data():
        print("VALIDATION FAILED: Could not load data file")
        return 1

    validator.run_all_validations()
    report = validator.generate_report()
    print(report)

    # Return exit code based on overall status
    all_passed = all(r.is_passing for r in validator.results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
