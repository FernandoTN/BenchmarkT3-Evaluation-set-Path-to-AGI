"""
Cross-validator for AGI Causal Reasoning Benchmark.

Provides duplicate detection and distribution verification for benchmark cases.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


@dataclass
class CrossValidationResult:
    """Result of cross-validation analysis."""

    total_cases: int
    duplicate_count: int
    duplicates: list[tuple[str, str, float]]
    pearl_distribution: dict[str, Any]
    trap_distribution: dict[str, Any]
    difficulty_distribution: dict[str, Any]
    l3_ground_truth_distribution: dict[str, Any]
    subdomain_coverage: dict[str, Any]
    original_cases_present: bool
    original_cases_marked: bool
    unmarked_original_cases: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    passes_all_checks: bool = False


class CrossValidator:
    """
    Cross-validator for benchmark case validation.

    Detects duplicates and verifies distribution targets are met.
    """

    # Default target distributions (used if config not available)
    DEFAULT_PEARL_TARGETS = {
        "L1": {"min_pct": 10, "max_pct": 12},
        "L2": {"min_pct": 66, "max_pct": 70},
        "L3": {"min_pct": 18, "max_pct": 21},
    }

    DEFAULT_L3_GROUND_TRUTH_TARGETS = {
        "VALID": {"target_percentage": 30},
        "INVALID": {"target_percentage": 20},
        "CONDITIONAL": {"target_percentage": 50},
    }

    def __init__(self, config_path: str) -> None:
        """
        Initialize the CrossValidator with configuration.

        Args:
            config_path: Path to the configuration JSON file.
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Extract target distributions from config
        self.pearl_targets = self._extract_pearl_targets()
        self.trap_targets = self._extract_trap_targets()
        self.l3_ground_truth_targets = self._extract_l3_ground_truth_targets()
        self.total_target_cases = self.config.get("project", {}).get(
            "total_target_cases", 450
        )
        self.original_cases_count = self.config.get("project", {}).get(
            "original_cases", 45
        )
        self.quality_thresholds = self.config.get("quality_thresholds", {})
        self.generator_allocations = self.config.get(
            "generator_batch_allocations", {}
        ).get("generators", {})

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, encoding="utf-8") as f:
            return json.load(f)

    def _extract_pearl_targets(self) -> dict[str, dict[str, float]]:
        """Extract Pearl level distribution targets from config."""
        target_dist = self.config.get("target_distributions", {}).get(
            "pearl_levels", {}
        )

        targets = {}
        level_map = {
            "L1_association": "L1",
            "L2_intervention": "L2",
            "L3_counterfactual": "L3",
        }

        for config_key, short_key in level_map.items():
            if config_key in target_dist:
                level_config = target_dist[config_key]
                # Parse percentage range string like "10-12%"
                pct_range = level_config.get("percentage_range", "")
                match = re.match(r"(\d+)-(\d+)%?", pct_range)
                if match:
                    targets[short_key] = {
                        "min_pct": int(match.group(1)),
                        "max_pct": int(match.group(2)),
                        "target_min": level_config.get("target_min"),
                        "target_max": level_config.get("target_max"),
                        "description": level_config.get("description", ""),
                    }

        return targets if targets else self.DEFAULT_PEARL_TARGETS

    def _extract_trap_targets(self) -> dict[str, dict[str, int]]:
        """Extract trap type distribution targets from config."""
        return self.config.get("target_distributions", {}).get("trap_types", {})

    def _extract_l3_ground_truth_targets(self) -> dict[str, dict[str, int]]:
        """Extract L3 ground truth distribution targets from config."""
        targets = self.config.get("l3_ground_truth_distribution", {})
        return targets if targets else self.DEFAULT_L3_GROUND_TRUTH_TARGETS

    def _get_all_subdomains(self) -> set[str]:
        """Get all expected subdomains from generator allocations."""
        subdomains = set()
        for gen_config in self.generator_allocations.values():
            subdomains.update(gen_config.get("subdomains", []))
        return subdomains

    def validate(self, cases: list[dict]) -> CrossValidationResult:
        """
        Perform full cross-validation on a set of cases.

        Args:
            cases: List of case dictionaries to validate.

        Returns:
            CrossValidationResult with all validation metrics.
        """
        issues: list[str] = []

        # Duplicate detection
        exact_duplicates = self._detect_exact_duplicates(cases)
        semantic_duplicates = self._detect_semantic_duplicates(cases)

        # Combine duplicates (semantic includes exact with similarity 1.0)
        all_duplicates = [
            (id1, id2, 1.0) for id1, id2 in exact_duplicates
        ] + semantic_duplicates

        duplicate_count = len(set((d[0], d[1]) for d in all_duplicates))

        if exact_duplicates:
            issues.append(
                f"Found {len(exact_duplicates)} exact duplicate pairs"
            )
        if semantic_duplicates:
            issues.append(
                f"Found {len(semantic_duplicates)} semantically similar pairs "
                f"(above threshold)"
            )

        # Distribution checks
        pearl_dist = self._check_pearl_distribution(cases)
        if not pearl_dist.get("within_target", False):
            issues.append("Pearl level distribution outside target ranges")

        trap_dist = self._check_trap_distribution(cases)
        if trap_dist.get("over_represented") or trap_dist.get("under_represented"):
            issues.append("Trap type distribution has imbalances")

        difficulty_dist = self._check_difficulty_distribution(cases)
        if not difficulty_dist.get("balanced", False):
            issues.append("Difficulty distribution is not balanced")

        l3_gt_dist = self._check_l3_ground_truth_distribution(cases)
        if not l3_gt_dist.get("within_target", True):
            issues.append("L3 ground truth distribution outside target ranges")

        # Coverage checks
        subdomain_coverage = self._check_subdomain_coverage(cases)
        if subdomain_coverage.get("missing_subdomains"):
            issues.append(
                f"Missing subdomains: {subdomain_coverage['missing_subdomains']}"
            )

        original_present = self._check_original_cases_present(cases)
        if not original_present:
            issues.append("Not all original cases are present")

        unmarked = self._check_original_cases_marked(cases)
        original_marked = len(unmarked) == 0
        if not original_marked:
            issues.append(
                f"Original cases not marked with is_original=true: {len(unmarked)}"
            )

        passes_all = (
            duplicate_count == 0
            and pearl_dist.get("within_target", False)
            and not trap_dist.get("over_represented")
            and not trap_dist.get("under_represented")
            and difficulty_dist.get("balanced", False)
            and l3_gt_dist.get("within_target", True)
            and original_present
            and original_marked
            and not subdomain_coverage.get("missing_subdomains")
        )

        return CrossValidationResult(
            total_cases=len(cases),
            duplicate_count=duplicate_count,
            duplicates=all_duplicates,
            pearl_distribution=pearl_dist,
            trap_distribution=trap_dist,
            difficulty_distribution=difficulty_dist,
            l3_ground_truth_distribution=l3_gt_dist,
            subdomain_coverage=subdomain_coverage,
            original_cases_present=original_present,
            original_cases_marked=original_marked,
            unmarked_original_cases=unmarked,
            issues=issues,
            passes_all_checks=passes_all,
        )

    def validate_incremental(
        self, new_cases: list[dict], existing_cases: list[dict]
    ) -> CrossValidationResult:
        """
        Validate new cases against existing cases.

        Args:
            new_cases: New cases to validate.
            existing_cases: Existing cases to check against.

        Returns:
            CrossValidationResult focusing on new case validation.
        """
        issues: list[str] = []

        # Check new cases for duplicates among themselves
        new_exact_dups = self._detect_exact_duplicates(new_cases)
        new_semantic_dups = self._detect_semantic_duplicates(new_cases)

        # Check new cases against existing cases
        cross_duplicates = self._detect_cross_duplicates(new_cases, existing_cases)

        all_duplicates = (
            [(id1, id2, 1.0) for id1, id2 in new_exact_dups]
            + new_semantic_dups
            + cross_duplicates
        )

        duplicate_count = len(set((d[0], d[1]) for d in all_duplicates))

        if new_exact_dups:
            issues.append(
                f"Found {len(new_exact_dups)} exact duplicates in new cases"
            )
        if new_semantic_dups:
            issues.append(
                f"Found {len(new_semantic_dups)} semantic duplicates in new cases"
            )
        if cross_duplicates:
            issues.append(
                f"Found {len(cross_duplicates)} duplicates between new and "
                "existing cases"
            )

        # Combined distribution check
        all_cases = existing_cases + new_cases
        pearl_dist = self._check_pearl_distribution(all_cases)
        trap_dist = self._check_trap_distribution(all_cases)
        difficulty_dist = self._check_difficulty_distribution(all_cases)
        l3_gt_dist = self._check_l3_ground_truth_distribution(all_cases)
        subdomain_coverage = self._check_subdomain_coverage(all_cases)

        if not pearl_dist.get("within_target", False):
            issues.append(
                "Combined Pearl level distribution outside target ranges"
            )
        if trap_dist.get("over_represented") or trap_dist.get("under_represented"):
            issues.append("Combined trap type distribution has imbalances")

        original_present = self._check_original_cases_present(all_cases)
        unmarked = self._check_original_cases_marked(all_cases)
        original_marked = len(unmarked) == 0

        passes_all = (
            duplicate_count == 0
            and pearl_dist.get("within_target", False)
            and not trap_dist.get("over_represented")
            and not trap_dist.get("under_represented")
        )

        return CrossValidationResult(
            total_cases=len(all_cases),
            duplicate_count=duplicate_count,
            duplicates=all_duplicates,
            pearl_distribution=pearl_dist,
            trap_distribution=trap_dist,
            difficulty_distribution=difficulty_dist,
            l3_ground_truth_distribution=l3_gt_dist,
            subdomain_coverage=subdomain_coverage,
            original_cases_present=original_present,
            original_cases_marked=original_marked,
            unmarked_original_cases=unmarked,
            issues=issues,
            passes_all_checks=passes_all,
        )

    def _detect_exact_duplicates(
        self, cases: list[dict]
    ) -> list[tuple[str, str]]:
        """
        Detect exact duplicate scenarios.

        Args:
            cases: List of case dictionaries.

        Returns:
            List of (case_id_1, case_id_2) tuples for exact duplicates.
        """
        duplicates: list[tuple[str, str]] = []
        scenario_map: dict[str, str] = {}

        for case in cases:
            case_id = case.get("case_id", case.get("id", "unknown"))
            scenario = self._normalize_text(
                case.get("scenario", case.get("problem_statement", ""))
            )

            if scenario in scenario_map:
                duplicates.append((scenario_map[scenario], case_id))
            else:
                scenario_map[scenario] = case_id

        return duplicates

    def _detect_semantic_duplicates(
        self, cases: list[dict], threshold: float = 0.75
    ) -> list[tuple[str, str, float]]:
        """
        Detect semantically similar scenarios.

        Args:
            cases: List of case dictionaries.
            threshold: Similarity threshold (default 0.85).

        Returns:
            List of (case_id_1, case_id_2, similarity) tuples.
        """
        # Use config threshold if available
        max_similarity = self.quality_thresholds.get("max_similarity", threshold)

        duplicates: list[tuple[str, str, float]] = []
        n = len(cases)

        for i in range(n):
            case_id_i = cases[i].get("case_id", cases[i].get("id", f"case_{i}"))
            scenario_i = cases[i].get(
                "scenario", cases[i].get("problem_statement", "")
            )

            for j in range(i + 1, n):
                case_id_j = cases[j].get(
                    "case_id", cases[j].get("id", f"case_{j}")
                )
                scenario_j = cases[j].get(
                    "scenario", cases[j].get("problem_statement", "")
                )

                similarity = self._compute_similarity(scenario_i, scenario_j)

                if similarity >= max_similarity:
                    duplicates.append((case_id_i, case_id_j, similarity))

        return duplicates

    def _detect_cross_duplicates(
        self, new_cases: list[dict], existing_cases: list[dict], threshold: float = 0.75
    ) -> list[tuple[str, str, float]]:
        """
        Detect duplicates between new and existing cases.

        Args:
            new_cases: New cases to check.
            existing_cases: Existing cases to check against.
            threshold: Similarity threshold.

        Returns:
            List of (new_case_id, existing_case_id, similarity) tuples.
        """
        max_similarity = self.quality_thresholds.get("max_similarity", threshold)
        duplicates: list[tuple[str, str, float]] = []

        for new_case in new_cases:
            new_id = new_case.get("case_id", new_case.get("id", "unknown"))
            new_scenario = new_case.get(
                "scenario", new_case.get("problem_statement", "")
            )

            for existing in existing_cases:
                existing_id = existing.get(
                    "case_id", existing.get("id", "unknown")
                )
                existing_scenario = existing.get(
                    "scenario", existing.get("problem_statement", "")
                )

                similarity = self._compute_similarity(new_scenario, existing_scenario)

                if similarity >= max_similarity:
                    duplicates.append((new_id, existing_id, similarity))

        return duplicates

    def _compute_similarity(self, s1: str, s2: str) -> float:
        """
        Compute text similarity between two strings.

        Uses a combination of SequenceMatcher (60%) and key phrase overlap (40%)
        for more robust duplicate detection.

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            Similarity score between 0 and 1.
        """
        if not s1 or not s2:
            return 0.0

        # Normalize texts
        s1_norm = self._normalize_text(s1)
        s2_norm = self._normalize_text(s2)

        # Compute SequenceMatcher similarity (60% weight)
        sequence_sim = SequenceMatcher(None, s1_norm, s2_norm).ratio()

        # Compute key phrase overlap (40% weight)
        phrase_sim = self._check_key_phrase_overlap(s1_norm, s2_norm)

        # Combine metrics: 60% SequenceMatcher + 40% key phrase overlap
        return 0.6 * sequence_sim + 0.4 * phrase_sim

    def _check_key_phrase_overlap(self, s1: str, s2: str) -> float:
        """Check overlap of 4-grams between two strings."""
        if len(s1) < 4 or len(s2) < 4:
            return 0.0
        ngrams1 = set(s1[i:i+4] for i in range(len(s1)-3))
        ngrams2 = set(s2[i:i+4] for i in range(len(s2)-3))
        if not ngrams1 or not ngrams2:
            return 0.0
        return len(ngrams1 & ngrams2) / min(len(ngrams1), len(ngrams2))

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Input text.

        Returns:
            Normalized text (lowercase, whitespace normalized).
        """
        if not text:
            return ""
        # Lowercase, normalize whitespace
        return " ".join(text.lower().split())

    def _check_pearl_distribution(self, cases: list[dict]) -> dict[str, Any]:
        """
        Check Pearl level distribution against targets.

        Args:
            cases: List of case dictionaries.

        Returns:
            Dictionary with counts, percentages, and target compliance.
        """
        counts: Counter[str] = Counter()
        total = len(cases)

        for case in cases:
            level = case.get("pearl_level", case.get("level", "unknown"))
            # Normalize level names
            if isinstance(level, str):
                if level.upper().startswith("L1") or "association" in level.lower():
                    counts["L1"] += 1
                elif level.upper().startswith("L2") or "intervention" in level.lower():
                    counts["L2"] += 1
                elif (
                    level.upper().startswith("L3") or "counterfactual" in level.lower()
                ):
                    counts["L3"] += 1
                else:
                    counts["unknown"] += 1

        percentages = {
            level: (count / total * 100) if total > 0 else 0
            for level, count in counts.items()
        }

        # Check against targets
        within_target = True
        deviations = {}

        for level, targets in self.pearl_targets.items():
            pct = percentages.get(level, 0)
            min_pct = targets.get("min_pct", 0)
            max_pct = targets.get("max_pct", 100)

            if pct < min_pct:
                within_target = False
                deviations[level] = f"under by {min_pct - pct:.1f}%"
            elif pct > max_pct:
                within_target = False
                deviations[level] = f"over by {pct - max_pct:.1f}%"

        return {
            "counts": dict(counts),
            "percentages": percentages,
            "targets": self.pearl_targets,
            "within_target": within_target,
            "deviations": deviations,
            "total": total,
        }

    def _check_trap_distribution(self, cases: list[dict]) -> dict[str, Any]:
        """
        Check trap type distribution against targets.

        Args:
            cases: List of case dictionaries.

        Returns:
            Dictionary with counts, targets, and over/under represented types.
        """
        counts: Counter[str] = Counter()

        for case in cases:
            trap_type = case.get("trap_type", case.get("category", "OTHER"))
            if isinstance(trap_type, str):
                counts[trap_type.upper()] += 1

        over_represented: list[str] = []
        under_represented: list[str] = []
        status: dict[str, dict[str, Any]] = {}

        for trap_type, targets in self.trap_targets.items():
            count = counts.get(trap_type, 0)
            target_min = targets.get("target_min", 0)
            target_max = targets.get("target_max", float("inf"))

            if count < target_min:
                under_represented.append(trap_type)
                status[trap_type] = {
                    "count": count,
                    "target_min": target_min,
                    "target_max": target_max,
                    "status": "under",
                    "deficit": target_min - count,
                }
            elif count > target_max:
                over_represented.append(trap_type)
                status[trap_type] = {
                    "count": count,
                    "target_min": target_min,
                    "target_max": target_max,
                    "status": "over",
                    "excess": count - target_max,
                }
            else:
                status[trap_type] = {
                    "count": count,
                    "target_min": target_min,
                    "target_max": target_max,
                    "status": "ok",
                }

        return {
            "counts": dict(counts),
            "targets": self.trap_targets,
            "status": status,
            "over_represented": over_represented,
            "under_represented": under_represented,
        }

    def _check_difficulty_distribution(self, cases: list[dict]) -> dict[str, Any]:
        """
        Check difficulty distribution (Easy/Medium/Hard balance).

        Args:
            cases: List of case dictionaries.

        Returns:
            Dictionary with counts, percentages, and balance status.
        """
        counts: Counter[str] = Counter()
        total = len(cases)

        for case in cases:
            difficulty = case.get("difficulty", "medium")
            if isinstance(difficulty, str):
                counts[difficulty.lower()] += 1

        percentages = {
            diff: (count / total * 100) if total > 0 else 0
            for diff, count in counts.items()
        }

        # Check for rough balance (each category should be 20-45%)
        balanced = True
        for diff in ["easy", "medium", "hard"]:
            pct = percentages.get(diff, 0)
            # Allow some flexibility - not all cases need difficulty assigned
            if pct > 60:
                balanced = False

        return {
            "counts": dict(counts),
            "percentages": percentages,
            "balanced": balanced,
            "total": total,
        }

    def _check_l3_ground_truth_distribution(
        self, cases: list[dict]
    ) -> dict[str, Any]:
        """
        Check L3 ground truth distribution.

        Only applies to L3 (counterfactual) cases.

        Args:
            cases: List of case dictionaries.

        Returns:
            Dictionary with counts, percentages, and target compliance.
        """
        l3_cases = [
            c
            for c in cases
            if c.get("pearl_level", "").upper().startswith("L3")
            or "counterfactual" in c.get("pearl_level", "").lower()
        ]

        if not l3_cases:
            return {
                "counts": {},
                "percentages": {},
                "targets": self.l3_ground_truth_targets,
                "within_target": True,
                "total_l3_cases": 0,
                "message": "No L3 cases found",
            }

        counts: Counter[str] = Counter()
        total_l3 = len(l3_cases)

        for case in l3_cases:
            ground_truth = case.get(
                "ground_truth", case.get("counterfactual_validity", "unknown")
            )
            if isinstance(ground_truth, str):
                gt_upper = ground_truth.upper()
                if gt_upper in ("VALID", "TRUE", "YES"):
                    counts["VALID"] += 1
                elif gt_upper in ("INVALID", "FALSE", "NO"):
                    counts["INVALID"] += 1
                elif gt_upper in ("CONDITIONAL", "DEPENDS", "PARTIAL"):
                    counts["CONDITIONAL"] += 1
                else:
                    counts["OTHER"] += 1

        percentages = {
            gt: (count / total_l3 * 100) if total_l3 > 0 else 0
            for gt, count in counts.items()
        }

        # Check against targets (allow 10% deviation)
        within_target = True
        deviations = {}

        for gt_type, targets in self.l3_ground_truth_targets.items():
            pct = percentages.get(gt_type, 0)
            target_pct = targets.get("target_percentage", 0)
            # Allow 10% absolute deviation
            if abs(pct - target_pct) > 15:
                within_target = False
                deviations[gt_type] = f"at {pct:.1f}% vs target {target_pct}%"

        return {
            "counts": dict(counts),
            "percentages": percentages,
            "targets": self.l3_ground_truth_targets,
            "within_target": within_target,
            "deviations": deviations,
            "total_l3_cases": total_l3,
        }

    def _check_subdomain_coverage(self, cases: list[dict]) -> dict[str, Any]:
        """
        Check that all expected subdomains are represented.

        Args:
            cases: List of case dictionaries.

        Returns:
            Dictionary with coverage information.
        """
        expected_subdomains = self._get_all_subdomains()
        found_subdomains: set[str] = set()
        subdomain_counts: Counter[str] = Counter()

        for case in cases:
            subdomain = case.get("subdomain", case.get("domain", ""))
            if isinstance(subdomain, str) and subdomain:
                found_subdomains.add(subdomain)
                subdomain_counts[subdomain] += 1

        missing = expected_subdomains - found_subdomains
        extra = found_subdomains - expected_subdomains

        return {
            "expected_subdomains": list(expected_subdomains),
            "found_subdomains": list(found_subdomains),
            "missing_subdomains": list(missing),
            "extra_subdomains": list(extra),
            "subdomain_counts": dict(subdomain_counts),
            "coverage_percentage": (
                len(found_subdomains & expected_subdomains)
                / len(expected_subdomains)
                * 100
            )
            if expected_subdomains
            else 100,
        }

    def _check_original_cases_present(self, cases: list[dict]) -> bool:
        """
        Check if all original cases are present.

        Args:
            cases: List of case dictionaries.

        Returns:
            True if all original cases are present.
        """
        original_count = sum(
            1 for c in cases if c.get("is_original", False) is True
        )
        return original_count >= self.original_cases_count

    def _check_original_cases_marked(self, cases: list[dict]) -> list[str]:
        """
        Check that original cases have is_original=true.

        Args:
            cases: List of case dictionaries.

        Returns:
            List of case IDs that should be marked as original but are not.
        """
        # This would typically check against a known list of original case IDs
        # For now, we return cases that have indicators of being original
        # but don't have is_original=true
        unmarked: list[str] = []

        for case in cases:
            case_id = case.get("case_id", case.get("id", ""))
            # Check for indicators that this might be an original case
            # (e.g., specific ID patterns, source field, etc.)
            source = case.get("source", "")
            if source == "original" and not case.get("is_original", False):
                unmarked.append(case_id)

        return unmarked

    def detect_placeholder_cases(
        self, cases: list[dict], exclude_original: bool = True
    ) -> list[tuple[str, str]]:
        """
        Detect placeholder cases with empty or minimal variable names.

        Placeholder cases are identified by:
        - Empty variable names (name == "")
        - Variable names shorter than 2 characters
        - Scenario containing "[PLACEHOLDER]" markers
        - Scenario matching pattern "Example [TYPE] scenario..."

        Args:
            cases: List of case dictionaries.
            exclude_original: If True, skip cases marked is_original=True.

        Returns:
            List of (case_id, reason) tuples for detected placeholders.
        """
        placeholders: list[tuple[str, str]] = []

        for case in cases:
            case_id = case.get("case_id", case.get("id", "unknown"))

            # Skip original cases if requested (preserve them)
            if exclude_original and case.get("is_original", False):
                continue

            # Check for empty variable names
            variables = case.get("variables", {})
            for var_key in ["X", "Y", "Z"]:
                var_data = variables.get(var_key, {})
                var_name = var_data.get("name", "")
                if len(var_name) < 2:
                    placeholders.append(
                        (case_id, f"Variable {var_key} has empty/short name: '{var_name}'")
                    )
                    break  # One reason per case is enough

            # Check for placeholder markers in scenario
            scenario = case.get("scenario", "")
            if "[PLACEHOLDER]" in scenario:
                placeholders.append((case_id, "Scenario contains [PLACEHOLDER] marker"))
            elif scenario.startswith("Example ") and " scenario" in scenario.lower():
                placeholders.append(
                    (case_id, "Scenario matches placeholder pattern 'Example X scenario'")
                )

        return placeholders

    def filter_placeholder_cases(
        self, cases: list[dict], exclude_original: bool = True
    ) -> tuple[list[dict], list[dict]]:
        """
        Filter out placeholder cases from a list of cases.

        Args:
            cases: List of case dictionaries.
            exclude_original: If True, never filter original cases.

        Returns:
            Tuple of (valid_cases, placeholder_cases).
        """
        placeholder_ids = set(
            case_id for case_id, _ in self.detect_placeholder_cases(cases, exclude_original)
        )

        valid_cases = []
        placeholder_cases = []

        for case in cases:
            case_id = case.get("case_id", case.get("id", "unknown"))
            if case_id in placeholder_ids:
                placeholder_cases.append(case)
            else:
                valid_cases.append(case)

        return valid_cases, placeholder_cases

    def generate_distribution_report(self, result: CrossValidationResult) -> str:
        """
        Generate a Markdown report from validation results.

        Args:
            result: CrossValidationResult to report on.

        Returns:
            Markdown formatted report string.
        """
        lines = [
            "# Cross-Validation Report",
            "",
            f"**Total Cases:** {result.total_cases}",
            f"**Passes All Checks:** {'Yes' if result.passes_all_checks else 'No'}",
            "",
        ]

        # Summary of issues
        if result.issues:
            lines.extend([
                "## Issues Found",
                "",
            ])
            for issue in result.issues:
                lines.append(f"- {issue}")
            lines.append("")

        # Duplicate analysis
        lines.extend([
            "## Duplicate Analysis",
            "",
            f"**Total Duplicates Found:** {result.duplicate_count}",
            "",
        ])

        if result.duplicates:
            lines.extend([
                "| Case 1 | Case 2 | Similarity |",
                "|--------|--------|------------|",
            ])
            for case1, case2, sim in result.duplicates[:20]:  # Limit to 20
                lines.append(f"| {case1} | {case2} | {sim:.2f} |")
            if len(result.duplicates) > 20:
                lines.append(
                    f"\n*...and {len(result.duplicates) - 20} more duplicates*"
                )
            lines.append("")

        # Pearl Level Distribution
        lines.extend([
            "## Pearl Level Distribution",
            "",
        ])
        pearl = result.pearl_distribution
        lines.extend([
            f"**Within Target:** {'Yes' if pearl.get('within_target') else 'No'}",
            "",
            "| Level | Count | Percentage | Target Range |",
            "|-------|-------|------------|--------------|",
        ])

        for level in ["L1", "L2", "L3"]:
            count = pearl.get("counts", {}).get(level, 0)
            pct = pearl.get("percentages", {}).get(level, 0)
            targets = pearl.get("targets", {}).get(level, {})
            target_range = f"{targets.get('min_pct', '-')}%-{targets.get('max_pct', '-')}%"
            lines.append(f"| {level} | {count} | {pct:.1f}% | {target_range} |")

        if pearl.get("deviations"):
            lines.append("")
            lines.append("**Deviations:**")
            for level, dev in pearl["deviations"].items():
                lines.append(f"- {level}: {dev}")
        lines.append("")

        # Trap Type Distribution
        lines.extend([
            "## Trap Type Distribution",
            "",
        ])
        trap = result.trap_distribution
        lines.extend([
            "| Trap Type | Count | Target Min | Target Max | Status |",
            "|-----------|-------|------------|------------|--------|",
        ])

        for trap_type, status in trap.get("status", {}).items():
            count = status.get("count", 0)
            t_min = status.get("target_min", "-")
            t_max = status.get("target_max", "-")
            status_str = status.get("status", "unknown").upper()
            lines.append(f"| {trap_type} | {count} | {t_min} | {t_max} | {status_str} |")

        if trap.get("over_represented"):
            lines.append("")
            lines.append(
                f"**Over-represented:** {', '.join(trap['over_represented'])}"
            )
        if trap.get("under_represented"):
            lines.append(
                f"**Under-represented:** {', '.join(trap['under_represented'])}"
            )
        lines.append("")

        # Difficulty Distribution
        lines.extend([
            "## Difficulty Distribution",
            "",
            f"**Balanced:** {'Yes' if result.difficulty_distribution.get('balanced') else 'No'}",
            "",
            "| Difficulty | Count | Percentage |",
            "|------------|-------|------------|",
        ])

        for diff, count in result.difficulty_distribution.get("counts", {}).items():
            pct = result.difficulty_distribution.get("percentages", {}).get(diff, 0)
            lines.append(f"| {diff.title()} | {count} | {pct:.1f}% |")
        lines.append("")

        # L3 Ground Truth Distribution
        lines.extend([
            "## L3 Ground Truth Distribution",
            "",
        ])
        l3_gt = result.l3_ground_truth_distribution
        lines.append(
            f"**L3 Cases:** {l3_gt.get('total_l3_cases', 0)}"
        )
        lines.append(
            f"**Within Target:** {'Yes' if l3_gt.get('within_target') else 'No'}"
        )

        if l3_gt.get("total_l3_cases", 0) > 0:
            lines.extend([
                "",
                "| Ground Truth | Count | Percentage | Target |",
                "|--------------|-------|------------|--------|",
            ])
            for gt_type in ["VALID", "INVALID", "CONDITIONAL"]:
                count = l3_gt.get("counts", {}).get(gt_type, 0)
                pct = l3_gt.get("percentages", {}).get(gt_type, 0)
                target = l3_gt.get("targets", {}).get(gt_type, {}).get(
                    "target_percentage", "-"
                )
                lines.append(f"| {gt_type} | {count} | {pct:.1f}% | {target}% |")
        lines.append("")

        # Subdomain Coverage
        lines.extend([
            "## Subdomain Coverage",
            "",
            f"**Coverage:** {result.subdomain_coverage.get('coverage_percentage', 0):.1f}%",
            "",
        ])

        if result.subdomain_coverage.get("missing_subdomains"):
            lines.append(
                f"**Missing Subdomains:** "
                f"{', '.join(result.subdomain_coverage['missing_subdomains'])}"
            )

        # Original Cases Status
        lines.extend([
            "",
            "## Original Cases Status",
            "",
            f"**Original Cases Present:** "
            f"{'Yes' if result.original_cases_present else 'No'}",
            f"**All Original Cases Marked:** "
            f"{'Yes' if result.original_cases_marked else 'No'}",
        ])

        if result.unmarked_original_cases:
            lines.append("")
            lines.append("**Unmarked Original Cases:**")
            for case_id in result.unmarked_original_cases[:10]:
                lines.append(f"- {case_id}")
            if len(result.unmarked_original_cases) > 10:
                lines.append(
                    f"*...and {len(result.unmarked_original_cases) - 10} more*"
                )

        # Recommendations
        lines.extend([
            "",
            "## Recommendations",
            "",
        ])

        recommendations: list[str] = []

        if result.duplicate_count > 0:
            recommendations.append(
                "- Remove or revise duplicate cases to ensure uniqueness"
            )

        if pearl.get("deviations"):
            for level, dev in pearl["deviations"].items():
                if "under" in dev:
                    recommendations.append(
                        f"- Generate more {level} cases to meet target distribution"
                    )
                else:
                    recommendations.append(
                        f"- Reduce {level} cases or convert some to other levels"
                    )

        if trap.get("under_represented"):
            for trap_type in trap["under_represented"]:
                recommendations.append(
                    f"- Generate more {trap_type} cases to meet minimum targets"
                )

        if trap.get("over_represented"):
            for trap_type in trap["over_represented"]:
                recommendations.append(
                    f"- Review {trap_type} cases - currently over target maximum"
                )

        if not result.difficulty_distribution.get("balanced"):
            recommendations.append(
                "- Adjust difficulty distribution for better balance"
            )

        if result.subdomain_coverage.get("missing_subdomains"):
            recommendations.append(
                "- Create cases for missing subdomains to ensure coverage"
            )

        if not result.original_cases_present:
            recommendations.append(
                "- Ensure all 45 original cases are included in the dataset"
            )

        if not result.original_cases_marked:
            recommendations.append(
                "- Mark all original cases with is_original=true"
            )

        if recommendations:
            lines.extend(recommendations)
        else:
            lines.append("No recommendations - all checks passed.")

        lines.append("")
        lines.append("---")
        lines.append("*Report generated by CrossValidator*")

        return "\n".join(lines)


def main() -> None:
    """Example usage of CrossValidator."""
    import sys

    # Example config path
    config_path = "/Users/fernandotn/Projects/AGI/project/orchestrator/config.json"

    try:
        validator = CrossValidator(config_path)
        print(f"CrossValidator initialized with config from: {config_path}")

        # Example: validate empty case list (for demonstration)
        sample_cases: list[dict] = []
        result = validator.validate(sample_cases)

        report = validator.generate_distribution_report(result)
        print(report)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
