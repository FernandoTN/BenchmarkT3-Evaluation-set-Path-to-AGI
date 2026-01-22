#!/usr/bin/env python3
"""
Validation script for transformed OTHER trap cases.
Validates structure, field values, consistency, and Pearl level requirements.
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
        self.issues.append({"case_id": case_id, "issue": issue})

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0


class TransformedOtherValidator:
    """Validator for transformed OTHER trap cases."""

    REQUIRED_NEW_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]
    REQUIRED_EXISTING_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]
    VALID_LABELS = ["YES", "NO", "AMBIGUOUS"]
    VALID_AUTHORS = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data: list[dict[str, Any]] = []
        self.results: dict[str, ValidationResult] = {}

    def load_data(self) -> bool:
        """Load JSON data from file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"ERROR: Failed to load file: {e}")
            return False

    def _init_results(self) -> None:
        """Initialize validation result trackers."""
        checks = [
            "new_field_presence",
            "id_format",
            "bucket_value",
            "label_value",
            "is_ambiguous_consistency",
            "trap_type_non_empty",
            "trap_subtype_non_empty",
            "annotation_author",
            "annotation_num_annotators",
            "annotation_adjudicated",
            "existing_field_integrity",
            "label_trap_consistency",
            "l2_hidden_structure",
            "l3_ground_truth",
        ]
        for check in checks:
            self.results[check] = ValidationResult(name=check)

    def validate_new_field_presence(self, case: dict) -> None:
        """Check that all new required fields are present."""
        result = self.results["new_field_presence"]
        case_id = case.get("case_id", "UNKNOWN")
        missing = [f for f in self.REQUIRED_NEW_FIELDS if f not in case]
        if missing:
            result.add_fail(case_id, f"Missing new fields: {missing}")
        else:
            result.add_pass()

    def validate_id_format(self, case: dict) -> None:
        """Check id format: T3-BucketI-XXXX (4 digits, zero-padded)."""
        result = self.results["id_format"]
        case_id = case.get("case_id", "UNKNOWN")
        id_value = case.get("id", "")
        if self.ID_PATTERN.match(id_value):
            result.add_pass()
        else:
            result.add_fail(case_id, f"Invalid id format: '{id_value}' (expected T3-BucketI-XXXX)")

    def validate_bucket_value(self, case: dict) -> None:
        """Check bucket is exactly 'BucketLarge-I'."""
        result = self.results["bucket_value"]
        case_id = case.get("case_id", "UNKNOWN")
        bucket = case.get("bucket", "")
        if bucket == "BucketLarge-I":
            result.add_pass()
        else:
            result.add_fail(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")

    def validate_label_value(self, case: dict) -> None:
        """Check label is one of YES, NO, AMBIGUOUS."""
        result = self.results["label_value"]
        case_id = case.get("case_id", "UNKNOWN")
        label = case.get("label", "")
        if label in self.VALID_LABELS:
            result.add_pass()
        else:
            result.add_fail(case_id, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")

    def validate_is_ambiguous_consistency(self, case: dict) -> None:
        """Check is_ambiguous matches (label == 'AMBIGUOUS')."""
        result = self.results["is_ambiguous_consistency"]
        case_id = case.get("case_id", "UNKNOWN")
        label = case.get("label", "")
        is_ambiguous = case.get("is_ambiguous")

        if not isinstance(is_ambiguous, bool):
            result.add_fail(case_id, f"is_ambiguous is not boolean: {type(is_ambiguous).__name__}")
            return

        expected = label == "AMBIGUOUS"
        if is_ambiguous == expected:
            result.add_pass()
        else:
            result.add_fail(case_id, f"is_ambiguous={is_ambiguous} but label='{label}'")

    def validate_trap_type_non_empty(self, case: dict) -> None:
        """Check trap.type is a non-empty string."""
        result = self.results["trap_type_non_empty"]
        case_id = case.get("case_id", "UNKNOWN")
        trap = case.get("trap", {})
        trap_type = trap.get("type", "") if isinstance(trap, dict) else ""
        if isinstance(trap_type, str) and trap_type.strip():
            result.add_pass()
        else:
            result.add_fail(case_id, f"trap.type is empty or invalid: '{trap_type}'")

    def validate_trap_subtype_non_empty(self, case: dict) -> None:
        """Check trap.subtype is a non-empty string."""
        result = self.results["trap_subtype_non_empty"]
        case_id = case.get("case_id", "UNKNOWN")
        trap = case.get("trap", {})
        trap_subtype = trap.get("subtype", "") if isinstance(trap, dict) else ""
        if isinstance(trap_subtype, str) and trap_subtype.strip():
            result.add_pass()
        else:
            result.add_fail(case_id, f"trap.subtype is empty or invalid: '{trap_subtype}'")

    def validate_annotation_author(self, case: dict) -> None:
        """Check annotation.author is valid."""
        result = self.results["annotation_author"]
        case_id = case.get("case_id", "UNKNOWN")
        annotation = case.get("annotation", {})
        author = annotation.get("author", "") if isinstance(annotation, dict) else ""
        if author in self.VALID_AUTHORS:
            result.add_pass()
        else:
            result.add_fail(case_id, f"Invalid annotation.author: '{author}' (expected one of {self.VALID_AUTHORS})")

    def validate_annotation_num_annotators(self, case: dict) -> None:
        """Check annotation.num_annotators is integer >= 1."""
        result = self.results["annotation_num_annotators"]
        case_id = case.get("case_id", "UNKNOWN")
        annotation = case.get("annotation", {})
        num = annotation.get("num_annotators") if isinstance(annotation, dict) else None
        if isinstance(num, int) and num >= 1:
            result.add_pass()
        else:
            result.add_fail(case_id, f"Invalid annotation.num_annotators: {num} (expected int >= 1)")

    def validate_annotation_adjudicated(self, case: dict) -> None:
        """Check annotation.adjudicated is boolean."""
        result = self.results["annotation_adjudicated"]
        case_id = case.get("case_id", "UNKNOWN")
        annotation = case.get("annotation", {})
        adjudicated = annotation.get("adjudicated") if isinstance(annotation, dict) else None
        if isinstance(adjudicated, bool):
            result.add_pass()
        else:
            result.add_fail(case_id, f"annotation.adjudicated is not boolean: {type(adjudicated).__name__}")

    def validate_existing_field_integrity(self, case: dict) -> None:
        """Check all existing required fields are present."""
        result = self.results["existing_field_integrity"]
        case_id = case.get("case_id", "UNKNOWN")
        missing = [f for f in self.REQUIRED_EXISTING_FIELDS if f not in case]
        if missing:
            result.add_fail(case_id, f"Missing existing fields: {missing}")
        else:
            result.add_pass()

    def validate_label_trap_consistency(self, case: dict) -> None:
        """Check label/trap consistency rules."""
        result = self.results["label_trap_consistency"]
        case_id = case.get("case_id", "UNKNOWN")
        label = case.get("label", "")
        trap = case.get("trap", {})
        trap_type = trap.get("type", "") if isinstance(trap, dict) else ""

        if label == "NO":
            # trap.type should not be "NONE" or empty
            if trap_type.upper() == "NONE" or not trap_type.strip():
                result.add_fail(case_id, f"label='NO' but trap.type is '{trap_type}' (should identify the trap)")
            else:
                result.add_pass()
        elif label == "YES":
            # Just verify trap info exists (scenario should support claim)
            if trap_type.strip():
                result.add_pass()
            else:
                result.add_fail(case_id, f"label='YES' but trap.type is empty")
        else:
            # AMBIGUOUS cases - just pass for now
            result.add_pass()

    def validate_l2_hidden_structure(self, case: dict) -> None:
        """L2 cases must have hidden_structure field."""
        result = self.results["l2_hidden_structure"]
        case_id = case.get("case_id", "UNKNOWN")
        pearl_level = case.get("pearl_level", "")

        if pearl_level == "L2":
            if "hidden_structure" in case:
                result.add_pass()
            else:
                result.add_fail(case_id, "L2 case missing 'hidden_structure' field")
        else:
            # Not L2, skip this check (count as pass for reporting)
            result.add_pass()

    def validate_l3_ground_truth(self, case: dict) -> None:
        """L3 cases must have ground_truth with verdict and justification."""
        result = self.results["l3_ground_truth"]
        case_id = case.get("case_id", "UNKNOWN")
        pearl_level = case.get("pearl_level", "")

        if pearl_level == "L3":
            ground_truth = case.get("ground_truth", {})
            if not isinstance(ground_truth, dict):
                result.add_fail(case_id, f"L3 case 'ground_truth' is not a dict: {type(ground_truth).__name__}")
                return

            has_verdict = "verdict" in ground_truth and ground_truth["verdict"]
            has_justification = "justification" in ground_truth and ground_truth["justification"]

            if has_verdict and has_justification:
                result.add_pass()
            else:
                missing = []
                if not has_verdict:
                    missing.append("verdict")
                if not has_justification:
                    missing.append("justification")
                result.add_fail(case_id, f"L3 case ground_truth missing: {missing}")
        else:
            # Not L3, skip this check (count as pass for reporting)
            result.add_pass()

    def validate_case(self, case: dict) -> None:
        """Run all validations on a single case."""
        self.validate_new_field_presence(case)
        self.validate_id_format(case)
        self.validate_bucket_value(case)
        self.validate_label_value(case)
        self.validate_is_ambiguous_consistency(case)
        self.validate_trap_type_non_empty(case)
        self.validate_trap_subtype_non_empty(case)
        self.validate_annotation_author(case)
        self.validate_annotation_num_annotators(case)
        self.validate_annotation_adjudicated(case)
        self.validate_existing_field_integrity(case)
        self.validate_label_trap_consistency(case)
        self.validate_l2_hidden_structure(case)
        self.validate_l3_ground_truth(case)

    def validate_all(self) -> bool:
        """Run validation on all cases."""
        if not self.load_data():
            return False

        self._init_results()

        for case in self.data:
            self.validate_case(case)

        return True

    def generate_report(self) -> str:
        """Generate validation report."""
        lines = [
            "=" * 70,
            "VALIDATION REPORT: transformed_other.json",
            "=" * 70,
            "",
            f"Total cases validated: {len(self.data)}",
            "",
            "-" * 70,
            "CHECK RESULTS",
            "-" * 70,
        ]

        # Summary table
        all_passed = True
        for name, result in self.results.items():
            status = "PASS" if result.failed == 0 else "FAIL"
            if result.failed > 0:
                all_passed = False
            lines.append(f"  {name:<35} {result.passed:>4}/{result.total:<4} {status}")

        # Issues section
        lines.extend(["", "-" * 70, "ISSUES FOUND", "-" * 70])

        total_issues = sum(len(r.issues) for r in self.results.values())
        if total_issues == 0:
            lines.append("  No issues found.")
        else:
            for name, result in self.results.items():
                if result.issues:
                    lines.append(f"\n  [{name}]")
                    for issue in result.issues:
                        lines.append(f"    - case_id={issue['case_id']}: {issue['issue']}")

        # Overall status
        lines.extend([
            "",
            "=" * 70,
            f"OVERALL STATUS: {'PASS' if all_passed else 'FAIL'}",
            f"Total issues: {total_issues}",
            "=" * 70,
        ])

        return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    file_path = "/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_other.json"

    validator = TransformedOtherValidator(file_path)
    if validator.validate_all():
        report = validator.generate_report()
        print(report)

        # Return exit code based on validation result
        all_passed = all(r.failed == 0 for r in validator.results.values())
        exit(0 if all_passed else 1)
    else:
        exit(1)


if __name__ == "__main__":
    main()
