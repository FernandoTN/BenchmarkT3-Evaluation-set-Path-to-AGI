"""
Diversity Enforcer Module for T3 Benchmark Case Generation.

This module provides similarity checking and diversity enforcement for benchmark
cases to ensure the generated dataset has sufficient variety and avoids duplicates.

The enforcer uses multiple similarity metrics:
- Scenario text similarity (Jaccard, n-gram, TF-IDF if available)
- Variable structure similarity (comparing X, Y, Z definitions)
- Causal structure similarity (DAG notation comparison)

These are combined into a weighted similarity score for duplicate detection.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Try to import sklearn for TF-IDF, fall back to simpler methods if unavailable
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class DiversityEnforcer:
    """
    Enforces diversity in benchmark case generation by detecting similar cases.

    This class provides methods to:
    - Check if a new case is sufficiently different from existing cases
    - Find duplicate pairs in a collection of cases
    - Analyze distribution balance across subdomains and trap types
    - Filter batches to remove too-similar cases

    Attributes:
        max_similarity: Threshold above which cases are considered too similar.
        scenario_weight: Weight for scenario text similarity in combined score.
        variable_weight: Weight for variable structure similarity.
        structure_weight: Weight for causal structure similarity.
    """

    DEFAULT_SCENARIO_WEIGHT = 0.5
    DEFAULT_VARIABLE_WEIGHT = 0.25
    DEFAULT_STRUCTURE_WEIGHT = 0.25

    def __init__(
        self,
        max_similarity: float = 0.85,
        scenario_weight: float = DEFAULT_SCENARIO_WEIGHT,
        variable_weight: float = DEFAULT_VARIABLE_WEIGHT,
        structure_weight: float = DEFAULT_STRUCTURE_WEIGHT
    ) -> None:
        """
        Initialize the DiversityEnforcer.

        Args:
            max_similarity: Maximum allowed similarity score (0.0 to 1.0).
                Cases with similarity above this threshold are flagged as duplicates.
            scenario_weight: Weight for scenario text similarity (default 0.5).
            variable_weight: Weight for variable similarity (default 0.25).
            structure_weight: Weight for causal structure similarity (default 0.25).

        Raises:
            ValueError: If max_similarity is not in [0, 1] or weights don't sum to 1.
        """
        if not 0.0 <= max_similarity <= 1.0:
            raise ValueError(f"max_similarity must be between 0 and 1, got {max_similarity}")

        total_weight = scenario_weight + variable_weight + structure_weight
        if not math.isclose(total_weight, 1.0, rel_tol=1e-9):
            raise ValueError(
                f"Weights must sum to 1.0, got {total_weight} "
                f"({scenario_weight} + {variable_weight} + {structure_weight})"
            )

        self.max_similarity = max_similarity
        self.scenario_weight = scenario_weight
        self.variable_weight = variable_weight
        self.structure_weight = structure_weight

        # Cache for TF-IDF vectorizer
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_corpus_scenarios: List[str] = []
        self._tfidf_matrix = None

        # Cache for tokenized scenarios
        self._token_cache: Dict[str, Set[str]] = {}

    def check_similarity(
        self,
        new_case: Dict[str, Any],
        existing_cases: List[Dict[str, Any]]
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Check if a new case is sufficiently different from existing cases.

        Args:
            new_case: The new case to check.
            existing_cases: List of existing cases to compare against.

        Returns:
            Tuple containing:
                - is_diverse: True if the case is sufficiently different.
                - max_similarity_found: Highest similarity score found.
                - most_similar_case_id: ID of the most similar case, or None if
                  no existing cases or all similarities are 0.

        Examples:
            >>> enforcer = DiversityEnforcer(max_similarity=0.85)
            >>> is_diverse, sim, case_id = enforcer.check_similarity(new, existing)
            >>> if not is_diverse:
            ...     print(f"Too similar to {case_id} ({sim:.2%})")
        """
        if not existing_cases:
            return True, 0.0, None

        if not new_case:
            return True, 0.0, None

        max_sim = 0.0
        most_similar_id: Optional[str] = None

        new_scenario = new_case.get("scenario", "")
        new_variables = new_case.get("variables", {})
        new_structure = self._extract_causal_structure(new_case)

        for existing in existing_cases:
            existing_scenario = existing.get("scenario", "")
            existing_variables = existing.get("variables", {})
            existing_structure = self._extract_causal_structure(existing)

            # Compute individual similarities
            scenario_sim = self._compute_scenario_similarity(new_scenario, existing_scenario)
            variable_sim = self._compute_variable_similarity(new_variables, existing_variables)
            structure_sim = self._compute_structure_similarity_str(new_structure, existing_structure)

            # Compute weighted combination
            combined_sim = self._weighted_similarity(scenario_sim, variable_sim, structure_sim)

            if combined_sim > max_sim:
                max_sim = combined_sim
                most_similar_id = existing.get("case_id")

        is_diverse = max_sim <= self.max_similarity
        return is_diverse, max_sim, most_similar_id

    def _compute_scenario_similarity(self, s1: str, s2: str) -> float:
        """
        Compute text similarity between two scenario descriptions.

        Uses multiple methods and returns the highest score:
        - Jaccard similarity on word tokens
        - Character n-gram similarity (n=3)
        - TF-IDF cosine similarity (if sklearn available)

        Args:
            s1: First scenario text.
            s2: Second scenario text.

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        # Compute multiple similarity measures
        jaccard = self._jaccard_similarity(s1, s2)
        ngram = self._ngram_similarity(s1, s2, n=3)

        # Take the maximum of available methods
        similarities = [jaccard, ngram]

        if SKLEARN_AVAILABLE:
            tfidf = self._tfidf_similarity(s1, s2)
            similarities.append(tfidf)

        return max(similarities)

    def _compute_variable_similarity(self, v1: Dict[str, Any], v2: Dict[str, Any]) -> float:
        """
        Compute similarity between two variable structures.

        Compares the X, Y, Z variables by:
        - Name similarity (using Jaccard on tokens)
        - Role match (exact or partial match)

        Args:
            v1: First variable dict with X, Y, Z keys.
            v2: Second variable dict with X, Y, Z keys.

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        if not v1 or not v2:
            return 0.0

        total_sim = 0.0
        count = 0

        for var_key in ["X", "Y", "Z"]:
            var1 = v1.get(var_key, {})
            var2 = v2.get(var_key, {})

            if not var1 or not var2:
                continue

            count += 1

            # Name similarity
            name1 = var1.get("name", "")
            name2 = var2.get("name", "")
            name_sim = self._jaccard_similarity(name1, name2)

            # Role similarity (exact match = 1.0, else check partial)
            role1 = var1.get("role", "").lower()
            role2 = var2.get("role", "").lower()

            if role1 == role2:
                role_sim = 1.0
            elif role1 in role2 or role2 in role1:
                role_sim = 0.5
            else:
                role_sim = 0.0

            # Combined variable similarity (name weighted more than role)
            var_sim = 0.7 * name_sim + 0.3 * role_sim
            total_sim += var_sim

        return total_sim / count if count > 0 else 0.0

    def _compute_structure_similarity(self, c1: Dict[str, Any], c2: Dict[str, Any]) -> float:
        """
        Compute similarity between causal structures of two cases.

        Extracts the causal_structure annotation and compares:
        - Edge sets (X->Y, Y->Z, etc.)
        - Overall DAG structure

        Args:
            c1: First case dict.
            c2: Second case dict.

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        struct1 = self._extract_causal_structure(c1)
        struct2 = self._extract_causal_structure(c2)
        return self._compute_structure_similarity_str(struct1, struct2)

    def _compute_structure_similarity_str(self, struct1: str, struct2: str) -> float:
        """
        Compute similarity between two causal structure strings.

        Args:
            struct1: First causal structure string (e.g., "X -> Y <- Z").
            struct2: Second causal structure string.

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        if not struct1 or not struct2:
            return 0.0

        if struct1 == struct2:
            return 1.0

        # Normalize and extract edges
        edges1 = self._parse_dag_edges(struct1)
        edges2 = self._parse_dag_edges(struct2)

        if not edges1 and not edges2:
            return 1.0
        if not edges1 or not edges2:
            return 0.0

        # Jaccard similarity on edge sets
        intersection = len(edges1 & edges2)
        union = len(edges1 | edges2)

        return intersection / union if union > 0 else 0.0

    def _weighted_similarity(
        self,
        scenario_sim: float,
        var_sim: float,
        struct_sim: float
    ) -> float:
        """
        Compute weighted combination of similarity scores.

        Args:
            scenario_sim: Scenario text similarity.
            var_sim: Variable structure similarity.
            struct_sim: Causal structure similarity.

        Returns:
            Weighted similarity score between 0.0 and 1.0.
        """
        return (
            self.scenario_weight * scenario_sim +
            self.variable_weight * var_sim +
            self.structure_weight * struct_sim
        )

    # -------------------------------------------------------------------------
    # Text Similarity Methods
    # -------------------------------------------------------------------------

    def _tokenize(self, text: str) -> Set[str]:
        """
        Tokenize text into a set of lowercase word tokens.

        Uses caching for efficiency with repeated comparisons.

        Args:
            text: Input text to tokenize.

        Returns:
            Set of lowercase word tokens.
        """
        if text in self._token_cache:
            return self._token_cache[text]

        # Simple word tokenization with lowercase
        tokens = set(re.findall(r'\b\w+\b', text.lower()))

        # Cache if not too large
        if len(self._token_cache) < 10000:
            self._token_cache[text] = tokens

        return tokens

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """
        Compute Jaccard similarity between two strings based on word tokens.

        Jaccard(A, B) = |A intersect B| / |A union B|

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            Jaccard similarity coefficient between 0.0 and 1.0.
        """
        tokens1 = self._tokenize(s1)
        tokens2 = self._tokenize(s2)

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _ngram_similarity(self, s1: str, s2: str, n: int = 3) -> float:
        """
        Compute character n-gram similarity between two strings.

        Uses Dice coefficient on character n-grams:
        Dice(A, B) = 2 * |A intersect B| / (|A| + |B|)

        Args:
            s1: First string.
            s2: Second string.
            n: N-gram size (default 3 for trigrams).

        Returns:
            N-gram similarity score between 0.0 and 1.0.
        """
        def get_ngrams(text: str, n: int) -> Set[str]:
            text = text.lower()
            return {text[i:i+n] for i in range(len(text) - n + 1)}

        ngrams1 = get_ngrams(s1, n)
        ngrams2 = get_ngrams(s2, n)

        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        total = len(ngrams1) + len(ngrams2)

        return 2 * intersection / total if total > 0 else 0.0

    def _tfidf_similarity(self, s1: str, s2: str) -> float:
        """
        Compute TF-IDF cosine similarity between two strings.

        Uses sklearn's TfidfVectorizer if available.

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            TF-IDF cosine similarity between 0.0 and 1.0.
        """
        if not SKLEARN_AVAILABLE:
            return 0.0

        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([s1, s2])
            similarity = sklearn_cosine(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0, 0])
        except Exception:
            # Fall back to 0 on any error
            return 0.0

    def _word_overlap_ratio(self, s1: str, s2: str) -> float:
        """
        Compute simple word overlap ratio as a fallback similarity measure.

        Overlap(A, B) = |A intersect B| / min(|A|, |B|)

        This measure is useful when one text is a subset of another.

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            Word overlap ratio between 0.0 and 1.0.
        """
        tokens1 = self._tokenize(s1)
        tokens2 = self._tokenize(s2)

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        min_size = min(len(tokens1), len(tokens2))

        return intersection / min_size if min_size > 0 else 0.0

    # -------------------------------------------------------------------------
    # Causal Structure Helpers
    # -------------------------------------------------------------------------

    def _extract_causal_structure(self, case: Dict[str, Any]) -> str:
        """
        Extract the causal structure string from a case.

        Args:
            case: Case dictionary.

        Returns:
            Causal structure string, or empty string if not found.
        """
        annotations = case.get("annotations", {})
        return annotations.get("causal_structure", "")

    def _parse_dag_edges(self, structure: str) -> Set[Tuple[str, str]]:
        """
        Parse a DAG notation string into a set of directed edges.

        Handles various notations:
        - "X -> Y": X causes Y
        - "X <- Y": Y causes X
        - "X -/-> Y": X does not cause Y (excluded from edges)
        - "X <-> Y": bidirectional (both directions included)

        Args:
            structure: DAG notation string (e.g., "X -> Y <- Z").

        Returns:
            Set of (source, target) edge tuples.
        """
        edges: Set[Tuple[str, str]] = set()

        # Normalize the structure string
        structure = structure.upper().replace(" ", "")

        # Pattern for edges: captures source, arrow type, target
        # Handles: ->, <-, <->, -/->, <-/-, etc.
        patterns = [
            (r'(\w+)->(\w+)', lambda m: [(m.group(1), m.group(2))]),
            (r'(\w+)<-(\w+)', lambda m: [(m.group(2), m.group(1))]),
            (r'(\w+)<->(\w+)', lambda m: [(m.group(1), m.group(2)), (m.group(2), m.group(1))]),
            # Skip negated arrows (-/->)
        ]

        for pattern, edge_fn in patterns:
            for match in re.finditer(pattern, structure):
                for edge in edge_fn(match):
                    edges.add(edge)

        return edges

    # -------------------------------------------------------------------------
    # Duplicate Detection
    # -------------------------------------------------------------------------

    def find_duplicates(
        self,
        cases: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, float]]:
        """
        Find all pairs of cases with similarity above the threshold.

        Args:
            cases: List of cases to check for duplicates.

        Returns:
            List of (case_id1, case_id2, similarity) tuples for duplicate pairs.
            Pairs are sorted by similarity (highest first).

        Examples:
            >>> duplicates = enforcer.find_duplicates(all_cases)
            >>> for id1, id2, sim in duplicates:
            ...     print(f"{id1} vs {id2}: {sim:.2%}")
        """
        duplicates: List[Tuple[str, str, float]] = []
        n = len(cases)

        for i in range(n):
            for j in range(i + 1, n):
                case1, case2 = cases[i], cases[j]

                # Compute similarity
                scenario_sim = self._compute_scenario_similarity(
                    case1.get("scenario", ""),
                    case2.get("scenario", "")
                )
                var_sim = self._compute_variable_similarity(
                    case1.get("variables", {}),
                    case2.get("variables", {})
                )
                struct_sim = self._compute_structure_similarity(case1, case2)

                combined_sim = self._weighted_similarity(scenario_sim, var_sim, struct_sim)

                if combined_sim > self.max_similarity:
                    id1 = case1.get("case_id", f"case_{i}")
                    id2 = case2.get("case_id", f"case_{j}")
                    duplicates.append((id1, id2, combined_sim))

        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates

    def is_exact_duplicate(self, case1: Dict[str, Any], case2: Dict[str, Any]) -> bool:
        """
        Check if two cases have exactly matching scenarios.

        Args:
            case1: First case.
            case2: Second case.

        Returns:
            True if scenarios match exactly (ignoring whitespace).
        """
        s1 = case1.get("scenario", "").strip().lower()
        s2 = case2.get("scenario", "").strip().lower()

        # Normalize whitespace
        s1 = " ".join(s1.split())
        s2 = " ".join(s2.split())

        return s1 == s2

    def get_diversity_report(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive diversity report for a set of cases.

        Args:
            cases: List of cases to analyze.

        Returns:
            Dictionary containing:
                - total_cases: Number of cases analyzed.
                - duplicate_pairs: List of duplicate pairs found.
                - duplicate_count: Number of duplicate pairs.
                - avg_similarity: Average pairwise similarity.
                - max_similarity: Maximum pairwise similarity found.
                - subdomain_distribution: Count by subdomain.
                - trap_type_distribution: Count by trap type.
                - diversity_score: Overall diversity score (0-1, higher is better).
        """
        if not cases:
            return {
                "total_cases": 0,
                "duplicate_pairs": [],
                "duplicate_count": 0,
                "avg_similarity": 0.0,
                "max_similarity": 0.0,
                "subdomain_distribution": {},
                "trap_type_distribution": {},
                "diversity_score": 1.0
            }

        # Find duplicates
        duplicates = self.find_duplicates(cases)

        # Compute pairwise similarities for statistics
        similarities: List[float] = []
        n = len(cases)

        # Sample if too many cases (for performance)
        if n > 100:
            # Sample approach: compute for first 100 pairs
            sample_limit = min(100, n * (n - 1) // 2)
            sample_count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if sample_count >= sample_limit:
                        break
                    sim = self._weighted_similarity(
                        self._compute_scenario_similarity(
                            cases[i].get("scenario", ""),
                            cases[j].get("scenario", "")
                        ),
                        self._compute_variable_similarity(
                            cases[i].get("variables", {}),
                            cases[j].get("variables", {})
                        ),
                        self._compute_structure_similarity(cases[i], cases[j])
                    )
                    similarities.append(sim)
                    sample_count += 1
                if sample_count >= sample_limit:
                    break
        else:
            for i in range(n):
                for j in range(i + 1, n):
                    sim = self._weighted_similarity(
                        self._compute_scenario_similarity(
                            cases[i].get("scenario", ""),
                            cases[j].get("scenario", "")
                        ),
                        self._compute_variable_similarity(
                            cases[i].get("variables", {}),
                            cases[j].get("variables", {})
                        ),
                        self._compute_structure_similarity(cases[i], cases[j])
                    )
                    similarities.append(sim)

        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
        max_sim = max(similarities) if similarities else 0.0

        # Distribution analysis
        subdomain_dist = self.analyze_subdomain_distribution(cases)
        trap_dist = self.analyze_trap_type_distribution(cases)

        # Compute diversity score (inverse of average similarity, penalized by duplicates)
        duplicate_penalty = min(1.0, len(duplicates) / max(1, n // 10))
        diversity_score = (1.0 - avg_sim) * (1.0 - 0.5 * duplicate_penalty)

        return {
            "total_cases": n,
            "duplicate_pairs": duplicates,
            "duplicate_count": len(duplicates),
            "avg_similarity": round(avg_sim, 4),
            "max_similarity": round(max_sim, 4),
            "subdomain_distribution": subdomain_dist,
            "trap_type_distribution": trap_dist,
            "diversity_score": round(diversity_score, 4)
        }

    # -------------------------------------------------------------------------
    # Distribution Analysis
    # -------------------------------------------------------------------------

    def analyze_subdomain_distribution(
        self,
        cases: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Count cases by subdomain.

        Args:
            cases: List of cases to analyze.

        Returns:
            Dictionary mapping subdomain names to counts.
        """
        distribution: Dict[str, int] = defaultdict(int)

        for case in cases:
            annotations = case.get("annotations", {})
            subdomain = annotations.get("subdomain", "Unknown")
            distribution[subdomain] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def analyze_trap_type_distribution(
        self,
        cases: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Count cases by trap type.

        Args:
            cases: List of cases to analyze.

        Returns:
            Dictionary mapping trap types to counts.
        """
        distribution: Dict[str, int] = defaultdict(int)

        for case in cases:
            annotations = case.get("annotations", {})
            trap_type = annotations.get("trap_type", "Unknown")
            distribution[trap_type] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def identify_underrepresented(
        self,
        cases: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Identify categories (trap types/subdomains) that need more cases.

        Args:
            cases: List of existing cases.
            config: Configuration dict containing target_distributions.

        Returns:
            List of category names that are below their minimum target.

        Examples:
            >>> underrep = enforcer.identify_underrepresented(cases, config)
            >>> print(f"Need more cases for: {underrep}")
        """
        underrepresented: List[str] = []

        # Get current trap type distribution
        trap_dist = self.analyze_trap_type_distribution(cases)

        # Get targets from config
        target_dists = config.get("target_distributions", {})
        trap_targets = target_dists.get("trap_types", {})

        for trap_type, targets in trap_targets.items():
            target_min = targets.get("target_min", 0)
            current = trap_dist.get(trap_type, 0)

            if current < target_min:
                shortfall = target_min - current
                underrepresented.append(f"{trap_type} (need {shortfall} more)")

        # Check Pearl level distribution
        pearl_targets = target_dists.get("pearl_levels", {})
        pearl_dist: Dict[str, int] = defaultdict(int)

        for case in cases:
            annotations = case.get("annotations", {})
            pearl_level = annotations.get("pearl_level", "Unknown")
            pearl_dist[pearl_level] += 1

        level_mapping = {
            "L1_association": "L1",
            "L2_intervention": "L2",
            "L3_counterfactual": "L3"
        }

        for level_key, targets in pearl_targets.items():
            target_min = targets.get("target_min", 0)
            level = level_mapping.get(level_key, level_key)
            current = pearl_dist.get(level, 0)

            if current < target_min:
                shortfall = target_min - current
                underrepresented.append(f"{level} (need {shortfall} more)")

        return underrepresented

    # -------------------------------------------------------------------------
    # Integration Helpers
    # -------------------------------------------------------------------------

    def load_all_existing_cases(
        self,
        categories_dir: str,
        deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Load all existing cases from the categories directory.

        Searches for JSON files in the categories directory and its subdirectories,
        loading all valid case objects.

        Args:
            categories_dir: Path to the categories directory.
            deduplicate: If True, remove duplicate cases with the same case_id,
                keeping only the first occurrence (default True).

        Returns:
            List of all loaded case dictionaries.

        Raises:
            FileNotFoundError: If categories_dir does not exist.
        """
        categories_path = Path(categories_dir)

        if not categories_path.exists():
            raise FileNotFoundError(f"Categories directory not found: {categories_dir}")

        all_cases: List[Dict[str, Any]] = []

        # Find all JSON files
        json_files = list(categories_path.glob("**/*.json"))

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Handle both single cases and lists of cases
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "case_id" in item:
                            all_cases.append(item)
                elif isinstance(data, dict) and "case_id" in data:
                    all_cases.append(data)

            except (json.JSONDecodeError, IOError) as e:
                # Log but continue with other files
                print(f"Warning: Could not load {json_file}: {e}")
                continue

        if deduplicate:
            all_cases = self.deduplicate_cases(all_cases)

        return all_cases

    @staticmethod
    def deduplicate_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate cases based on case_id, keeping the first occurrence.

        Args:
            cases: List of cases that may contain duplicates.

        Returns:
            List of unique cases (by case_id).
        """
        seen_ids: Set[str] = set()
        unique_cases: List[Dict[str, Any]] = []

        for case in cases:
            case_id = case.get("case_id")
            if case_id is not None and case_id not in seen_ids:
                seen_ids.add(case_id)
                unique_cases.append(case)

        return unique_cases

    def filter_diverse_batch(
        self,
        new_cases: List[Dict[str, Any]],
        existing: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter a batch of new cases to remove those too similar to existing cases.

        Also removes cases that are too similar to each other within the batch.

        Args:
            new_cases: List of new cases to filter.
            existing: List of existing cases to compare against.

        Returns:
            Filtered list containing only sufficiently diverse cases.

        Examples:
            >>> filtered = enforcer.filter_diverse_batch(new_batch, all_existing)
            >>> print(f"Kept {len(filtered)}/{len(new_batch)} cases")
        """
        if not new_cases:
            return []

        diverse_cases: List[Dict[str, Any]] = []
        combined_existing = list(existing)  # Copy to avoid modifying original

        for case in new_cases:
            is_diverse, sim, similar_id = self.check_similarity(case, combined_existing)

            if is_diverse:
                diverse_cases.append(case)
                # Add to combined list so next cases are checked against this one
                combined_existing.append(case)
            else:
                case_id = case.get("case_id", "unknown")
                print(f"Filtered out {case_id}: too similar to {similar_id} ({sim:.2%})")

        return diverse_cases

    def clear_cache(self) -> None:
        """
        Clear internal caches to free memory.

        Useful when processing is complete or when memory is constrained.
        """
        self._token_cache.clear()
        self._tfidf_vectorizer = None
        self._tfidf_corpus_scenarios = []
        self._tfidf_matrix = None


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------

def create_enforcer_from_config(config: Dict[str, Any]) -> DiversityEnforcer:
    """
    Create a DiversityEnforcer from a configuration dictionary.

    Args:
        config: Configuration dict containing quality_thresholds.max_similarity.

    Returns:
        Configured DiversityEnforcer instance.
    """
    quality = config.get("quality_thresholds", {})
    max_sim = quality.get("max_similarity", 0.85)
    return DiversityEnforcer(max_similarity=max_sim)


def quick_diversity_check(
    new_case: Dict[str, Any],
    existing_cases: List[Dict[str, Any]],
    threshold: float = 0.85
) -> bool:
    """
    Quick check if a new case is diverse enough.

    Convenience function for simple use cases.

    Args:
        new_case: The new case to check.
        existing_cases: List of existing cases.
        threshold: Similarity threshold.

    Returns:
        True if the case is sufficiently diverse.
    """
    enforcer = DiversityEnforcer(max_similarity=threshold)
    is_diverse, _, _ = enforcer.check_similarity(new_case, existing_cases)
    return is_diverse


if __name__ == "__main__":
    # Example usage and basic tests
    print("DiversityEnforcer Module")
    print("=" * 50)

    # Test cases
    case1 = {
        "case_id": "8.1",
        "scenario": "A cleaning robot is rewarded for minimizing visible dust. It learns to sweep dust under the rug.",
        "variables": {
            "X": {"name": "Hiding Dust", "role": "Action"},
            "Y": {"name": "Low Visible Dust", "role": "Reward Signal"},
            "Z": {"name": "Actual Cleanliness", "role": "Latent Goal"}
        },
        "annotations": {
            "subdomain": "Reward Hacking",
            "trap_type": "GOODHART",
            "causal_structure": "X -> Y but X -/-> Z"
        }
    }

    case2 = {
        "case_id": "8.2",
        "scenario": "A cleaning robot minimizes dust readings by pushing dust under furniture.",
        "variables": {
            "X": {"name": "Concealing Dust", "role": "Action"},
            "Y": {"name": "Dust Sensor Reading", "role": "Reward"},
            "Z": {"name": "True Cleanliness", "role": "Goal"}
        },
        "annotations": {
            "subdomain": "Reward Hacking",
            "trap_type": "GOODHART",
            "causal_structure": "X -> Y but X -/-> Z"
        }
    }

    case3 = {
        "case_id": "8.3",
        "scenario": "An AI tax advisor minimizes client tax bills by recommending fraudulent deductions.",
        "variables": {
            "X": {"name": "Fraud", "role": "Action"},
            "Y": {"name": "Tax Minimization", "role": "Reward"},
            "Z": {"name": "Legal Compliance", "role": "Constraint"}
        },
        "annotations": {
            "subdomain": "Legal AI",
            "trap_type": "GOODHART",
            "causal_structure": "X -> Y"
        }
    }

    enforcer = DiversityEnforcer(max_similarity=0.85)

    # Test similarity between similar cases
    is_diverse, sim, similar_id = enforcer.check_similarity(case2, [case1])
    print(f"\nCase 8.2 vs Case 8.1:")
    print(f"  Is diverse: {is_diverse}")
    print(f"  Similarity: {sim:.2%}")
    print(f"  Most similar: {similar_id}")

    # Test similarity between different cases
    is_diverse, sim, similar_id = enforcer.check_similarity(case3, [case1])
    print(f"\nCase 8.3 vs Case 8.1:")
    print(f"  Is diverse: {is_diverse}")
    print(f"  Similarity: {sim:.2%}")
    print(f"  Most similar: {similar_id}")

    # Test diversity report
    report = enforcer.get_diversity_report([case1, case2, case3])
    print(f"\nDiversity Report:")
    print(f"  Total cases: {report['total_cases']}")
    print(f"  Duplicate pairs: {report['duplicate_count']}")
    print(f"  Average similarity: {report['avg_similarity']:.2%}")
    print(f"  Diversity score: {report['diversity_score']:.2%}")
    print(f"  Trap distribution: {report['trap_type_distribution']}")
