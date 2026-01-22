#!/usr/bin/env python3
"""
Validation script for transformed CONF_MED cases.

Validates:
1. New field presence (id, bucket, claim, label, is_ambiguous, trap, gold_rationale, annotation)
2. Field values (formats, allowed values, consistency)
3. Label consistency
4. Existing field integrity
5. Pearl level requirements
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
    """Aggregates validation results for a specific check."""
    check_name: str
    passed: int = 0
    failed: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_pass(self) -> None:
        self.passed += 1

    def add_fail(self, case_id: str, description: str) -> None:
        self.failed += 1
        self.issues.append(ValidationIssue(case_id, self.check_name, description))


class ConfMedValidator:
    """Validator for transformed CONF_MED cases."""

    REQUIRED_NEW_FIELDS = ["id", "bucket", "claim", "label", "is_ambiguous", "trap", "gold_rationale", "annotation"]
    REQUIRED_EXISTING_FIELDS = ["case_id", "scenario", "variables", "annotations", "wise_refusal", "correct_reasoning"]
    VALID_LABELS = ["YES", "NO", "AMBIGUOUS"]
    VALID_AUTHORS = ["Stanford CS372", "Fernando Torres", "Alessandro Balzi"]
    ID_PATTERN = re.compile(r"^T3-BucketI-\d{4}$")

    def __init__(self, data: list[dict[str, Any]]):
        self.data = data
        self.results: dict[str, ValidationResult] = {}

    def _get_case_id(self, case: dict) -> str:
        """Get a readable identifier for error reporting."""
        return case.get("id") or case.get("case_id") or "UNKNOWN"

    def validate_new_field_presence(self) -> ValidationResult:
        """Check that all new required fields are present."""
        result = ValidationResult("New Field Presence")

        for case in self.data:
            case_id = self._get_case_id(case)
            missing = [f for f in self.REQUIRED_NEW_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing fields: {missing}")
            else:
                result.add_pass()

        return result

    def validate_id_format(self) -> ValidationResult:
        """Check that id follows format T3-BucketI-XXXX."""
        result = ValidationResult("ID Format")

        for case in self.data:
            case_id = self._get_case_id(case)
            id_val = case.get("id", "")

            if not self.ID_PATTERN.match(id_val):
                result.add_fail(case_id, f"Invalid id format: '{id_val}' (expected T3-BucketI-XXXX)")
            else:
                result.add_pass()

        return result

    def validate_bucket(self) -> ValidationResult:
        """Check that bucket is exactly 'BucketLarge-I'."""
        result = ValidationResult("Bucket Value")

        for case in self.data:
            case_id = self._get_case_id(case)
            bucket = case.get("bucket")

            if bucket != "BucketLarge-I":
                result.add_fail(case_id, f"Invalid bucket: '{bucket}' (expected 'BucketLarge-I')")
            else:
                result.add_pass()

        return result

    def validate_label(self) -> ValidationResult:
        """Check that label is in allowed values."""
        result = ValidationResult("Label Value")

        for case in self.data:
            case_id = self._get_case_id(case)
            label = case.get("label")

            if label not in self.VALID_LABELS:
                result.add_fail(case_id, f"Invalid label: '{label}' (expected one of {self.VALID_LABELS})")
            else:
                result.add_pass()

        return result

    def validate_is_ambiguous(self) -> ValidationResult:
        """Check that is_ambiguous is boolean and matches label."""
        result = ValidationResult("is_ambiguous Consistency")

        for case in self.data:
            case_id = self._get_case_id(case)
            is_ambiguous = case.get("is_ambiguous")
            label = case.get("label")

            if not isinstance(is_ambiguous, bool):
                result.add_fail(case_id, f"is_ambiguous must be boolean, got: {type(is_ambiguous).__name__}")
            elif label == "AMBIGUOUS" and not is_ambiguous:
                result.add_fail(case_id, "label='AMBIGUOUS' but is_ambiguous=false")
            elif label != "AMBIGUOUS" and is_ambiguous:
                result.add_fail(case_id, f"label='{label}' but is_ambiguous=true")
            else:
                result.add_pass()

        return result

    def validate_trap(self) -> ValidationResult:
        """Check trap.type and trap.subtype are non-empty strings."""
        result = ValidationResult("Trap Fields")

        for case in self.data:
            case_id = self._get_case_id(case)
            trap = case.get("trap", {})
            issues = []

            if not isinstance(trap, dict):
                issues.append(f"trap must be object, got: {type(trap).__name__}")
            else:
                trap_type = trap.get("type", "")
                trap_subtype = trap.get("subtype", "")

                if not trap_type or not isinstance(trap_type, str):
                    issues.append(f"trap.type must be non-empty string, got: '{trap_type}'")
                if not trap_subtype or not isinstance(trap_subtype, str):
                    issues.append(f"trap.subtype must be non-empty string, got: '{trap_subtype}'")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_annotation(self) -> ValidationResult:
        """Check annotation fields."""
        result = ValidationResult("Annotation Fields")

        for case in self.data:
            case_id = self._get_case_id(case)
            annotation = case.get("annotation", {})
            issues = []

            if not isinstance(annotation, dict):
                issues.append(f"annotation must be object, got: {type(annotation).__name__}")
            else:
                author = annotation.get("author")
                num_annotators = annotation.get("num_annotators")
                adjudicated = annotation.get("adjudicated")

                if author not in self.VALID_AUTHORS:
                    issues.append(f"annotation.author '{author}' not in {self.VALID_AUTHORS}")
                if not isinstance(num_annotators, int) or num_annotators < 1:
                    issues.append(f"annotation.num_annotators must be int >= 1, got: {num_annotators}")
                if not isinstance(adjudicated, bool):
                    issues.append(f"annotation.adjudicated must be boolean, got: {type(adjudicated).__name__}")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_label_consistency(self) -> ValidationResult:
        """Check label consistency with trap type."""
        result = ValidationResult("Label Consistency")

        for case in self.data:
            case_id = self._get_case_id(case)
            label = case.get("label")
            trap = case.get("trap", {})
            trap_type = trap.get("type", "") if isinstance(trap, dict) else ""
            issues = []

            # If label=NO, trap.type should not be NONE or empty
            if label == "NO":
                if not trap_type or trap_type.upper() == "NONE":
                    issues.append(f"label='NO' but trap.type is empty or 'NONE'")

            # If label=YES, verify scenario supports the claim (basic check)
            if label == "YES":
                scenario = case.get("scenario", "")
                claim = case.get("claim", "")
                gold_rationale = case.get("gold_rationale", "")

                # Check that gold_rationale doesn't contradict YES label
                negative_indicators = ["spurious", "does not cause", "no causal", "correlation is not"]
                if any(ind.lower() in gold_rationale.lower() for ind in negative_indicators):
                    issues.append(f"label='YES' but gold_rationale contains negative causal indicators")

            if issues:
                result.add_fail(case_id, "; ".join(issues))
            else:
                result.add_pass()

        return result

    def validate_existing_field_integrity(self) -> ValidationResult:
        """Check that all existing required fields are present."""
        result = ValidationResult("Existing Field Integrity")

        for case in self.data:
            case_id = self._get_case_id(case)
            missing = [f for f in self.REQUIRED_EXISTING_FIELDS if f not in case]

            if missing:
                result.add_fail(case_id, f"Missing existing fields: {missing}")
            else:
                result.add_pass()

        return result

    def validate_pearl_level_requirements(self) -> ValidationResult:
        """Check Pearl level specific requirements."""
        result = ValidationResult("Pearl Level Requirements")

        for case in self.data:
            case_id = self._get_case_id(case)
            pearl_level = case.get("pearl_level") or case.get("annotations", {}).get("pearl_level")
            issues = []

            if pearl_level == "L2":
                if "hidden_structure" not in case:
                    issues.append("L2 case missing 'hidden_structure'")
                elif not case.get("hidden_structure"):
                    issues.append("L2 case has empty 'hidden_structure'")

            elif pearl_level == "L3":
                ground_truth = case.get("ground_truth")
                if not ground_truth:
                    issues.append("L3 case missing 'ground_truth'")
                elif not isinstance(ground_truth, dict):
                    issues.append(f"L3 ground_truth must be object, got: {type(ground_truth).__name__}")
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

    def validate_gold_rationale(self) -> ValidationResult:
        """Check that gold_rationale is a non-empty string."""
        result = ValidationResult("Gold Rationale")

        for case in self.data:
            case_id = self._get_case_id(case)
            gold_rationale = case.get("gold_rationale")

            if not gold_rationale or not isinstance(gold_rationale, str):
                result.add_fail(case_id, f"gold_rationale must be non-empty string, got: '{gold_rationale}'")
            elif len(gold_rationale) < 20:
                result.add_fail(case_id, f"gold_rationale too short ({len(gold_rationale)} chars)")
            else:
                result.add_pass()

        return result

    def run_all_validations(self) -> dict[str, ValidationResult]:
        """Run all validation checks."""
        validations = [
            self.validate_new_field_presence,
            self.validate_id_format,
            self.validate_bucket,
            self.validate_label,
            self.validate_is_ambiguous,
            self.validate_trap,
            self.validate_annotation,
            self.validate_label_consistency,
            self.validate_existing_field_integrity,
            self.validate_pearl_level_requirements,
            self.validate_gold_rationale,
        ]

        for validation in validations:
            result = validation()
            self.results[result.check_name] = result

        return self.results

    def generate_report(self) -> str:
        """Generate a validation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("CONF_MED TRANSFORMATION VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Total cases validated: {len(self.data)}")
        lines.append("")

        # Summary table
        lines.append("-" * 70)
        lines.append(f"{'Check Name':<35} {'Passed':>10} {'Failed':>10} {'Status':>10}")
        lines.append("-" * 70)

        total_passed = 0
        total_failed = 0
        all_issues: list[ValidationIssue] = []

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

            # Group issues by case
            issues_by_case: dict[str, list[ValidationIssue]] = {}
            for issue in all_issues:
                if issue.case_id not in issues_by_case:
                    issues_by_case[issue.case_id] = []
                issues_by_case[issue.case_id].append(issue)

            for case_id, issues in sorted(issues_by_case.items()):
                lines.append(f"\nCase: {case_id}")
                for issue in issues:
                    lines.append(f"  [{issue.check_name}] {issue.description}")
        else:
            lines.append("No issues found.")

        lines.append("")
        lines.append("=" * 70)
        overall_status = "PASS" if total_failed == 0 else "FAIL"
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    input_path = Path("/Users/fernandotn/Projects/AGI/project/output/intermediate/transformed_conf_med.json")

    print(f"Loading data from: {input_path}")

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"ERROR: Expected a list of cases, got: {type(data).__name__}")
        return 1

    print(f"Loaded {len(data)} cases")
    print()

    validator = ConfMedValidator(data)
    validator.run_all_validations()
    report = validator.generate_report()

    print(report)

    # Return exit code based on validation result
    has_failures = any(r.failed > 0 for r in validator.results.values())
    return 1 if has_failures else 0


if __name__ == "__main__":
    exit(main())
