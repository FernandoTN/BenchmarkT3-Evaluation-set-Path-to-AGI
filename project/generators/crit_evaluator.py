#!/usr/bin/env python3
"""
CRIT (Critical Reading Inquisitive Template) Quality Scoring System.

Based on the SocraSynth/EVINCE frameworks, this module implements a comprehensive
quality evaluation system for T3 Benchmark cases. The evaluator assesses cases
across multiple dimensions including claim clarity, reasoning validity, trap
mechanism strength, and overall coherence.

The scoring methodology follows a multi-step process:
1. Extract and validate the main claim/premise from the scenario
2. Identify supporting reasons from the correct_reasoning field
3. Validate each reason against the claim
4. Identify counter-reasons (the trap mechanism)
5. Calculate weighted aggregate scores (gamma)

References:
- SocraSynth: Multi-LLM reasoning via structured debate
- EVINCE: Evidence-based validity checking for claims
- Pearl's Ladder of Causation for L1/L2/L3 validation
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScoreLevel(Enum):
    """Enumeration of score quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class CRITResult:
    """
    Result container for CRIT evaluation.

    Attributes:
        total_score: Weighted aggregate score (0-10 scale)
        breakdown: Per-dimension scores with keys matching evaluation dimensions
        issues: List of identified problems requiring attention
        suggestions: Improvement suggestions for each identified issue
        passes_threshold: Whether the case meets the minimum acceptable score
    """
    total_score: float
    breakdown: dict[str, float] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    passes_threshold: bool = False

    def get_level(self) -> ScoreLevel:
        """Determine the quality level based on total score."""
        if self.total_score >= 8.5:
            return ScoreLevel.EXCELLENT
        elif self.total_score >= 7.0:
            return ScoreLevel.GOOD
        elif self.total_score >= 5.0:
            return ScoreLevel.ACCEPTABLE
        elif self.total_score >= 3.0:
            return ScoreLevel.NEEDS_IMPROVEMENT
        return ScoreLevel.POOR

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format for serialization."""
        return {
            "total_score": round(self.total_score, 2),
            "breakdown": {k: round(v, 2) for k, v in self.breakdown.items()},
            "issues": self.issues,
            "suggestions": self.suggestions,
            "passes_threshold": self.passes_threshold,
            "level": self.get_level().value
        }


@dataclass
class BatchEvaluationResult:
    """
    Result container for batch evaluation of multiple cases.

    Attributes:
        total_cases: Number of cases evaluated
        passed_cases: Number of cases meeting minimum threshold
        failed_cases: Number of cases below minimum threshold
        average_score: Mean score across all cases
        median_score: Median score across all cases
        std_dev: Standard deviation of scores
        score_distribution: Count of cases in each score range
        dimension_averages: Average scores per evaluation dimension
        common_issues: Most frequently occurring issues
        individual_results: Results for each individual case
    """
    total_cases: int
    passed_cases: int
    failed_cases: int
    average_score: float
    median_score: float
    std_dev: float
    score_distribution: dict[str, int]
    dimension_averages: dict[str, float]
    common_issues: list[tuple[str, int]]
    individual_results: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format for serialization."""
        return {
            "summary": {
                "total_cases": self.total_cases,
                "passed_cases": self.passed_cases,
                "failed_cases": self.failed_cases,
                "pass_rate": round(self.passed_cases / max(self.total_cases, 1) * 100, 1),
                "average_score": round(self.average_score, 2),
                "median_score": round(self.median_score, 2),
                "std_dev": round(self.std_dev, 2)
            },
            "score_distribution": self.score_distribution,
            "dimension_averages": {k: round(v, 2) for k, v in self.dimension_averages.items()},
            "common_issues": [{"issue": issue, "count": count} for issue, count in self.common_issues],
            "individual_results": self.individual_results
        }


class CRITEvaluator:
    """
    Critical Reading Inquisitive Template (CRIT) Evaluator.

    This class implements a comprehensive quality scoring system for T3 Benchmark
    cases based on the SocraSynth/EVINCE frameworks. It evaluates cases across
    multiple dimensions and provides detailed feedback for improvement.

    Scoring Rubric:
        | Component                  | Minimum | Target |
        |---------------------------|---------|--------|
        | Claim clarity             | 6/10    | 8/10   |
        | Supporting reasons validity| 6/10   | 7/10   |
        | Counter-reasons strength  | 7/10    | 8/10   |
        | Overall CRIT Gamma        | 6.0     | 7.5    |

    Example:
        >>> evaluator = CRITEvaluator(min_score=5.0, target_score=7.0)
        >>> case = {
        ...     "case_id": "8.1",
        ...     "scenario": "A cleaning robot rewards for minimizing visible dust...",
        ...     "variables": {"X": {...}, "Y": {...}, "Z": {...}},
        ...     "annotations": {...},
        ...     "correct_reasoning": [...],
        ...     "wise_refusal": "..."
        ... }
        >>> score, breakdown = evaluator.evaluate_case(case)
        >>> print(f"Score: {score}, Passes: {breakdown.passes_threshold}")
    """

    # Dimension weights for aggregate scoring
    DIMENSION_WEIGHTS = {
        "scenario_clarity": 0.15,
        "variable_definition": 0.10,
        "trap_mechanism": 0.25,
        "reasoning_chain": 0.20,
        "wise_refusal": 0.15,
        "claim_validity": 0.10,
        "counter_strength": 0.05
    }

    # Keywords indicating causal/trap concepts by category
    TRAP_KEYWORDS = {
        "GOODHART": ["proxy", "metric", "gaming", "optimize", "reward", "incentive"],
        "CONF_MED": ["confounder", "correlation", "causation", "confounded", "spurious"],
        "INSTRUMENTAL": ["instrumental", "convergent", "self-preservation", "resource"],
        "SELECTION": ["selection", "bias", "sample", "leakage", "contamination"],
        "SPURIOUS": ["spurious", "shortcut", "artifact", "clever hans"],
        "SPECIFICATION": ["specification", "literal", "intent", "gap", "underspecified"],
        "FEEDBACK": ["feedback", "loop", "self-fulfilling", "performative", "circular"],
        "COUNTERFACTUAL": ["counterfactual", "if", "would", "had", "intervention"],
        "CLUSTERING": ["adversarial", "perturbation", "boundary", "feature"],
        "COMPOSITION": ["multi-agent", "collective", "individual", "nash", "coordination"],
        "CALIBRATION": ["calibration", "confidence", "probability", "miscalibrated"],
        "ALIGNMENT": ["alignment", "orthogonality", "goal", "value"],
        "ROBUSTNESS": ["robust", "adversarial", "patch", "attack"]
    }

    # Minimum word counts for quality thresholds
    MIN_SCENARIO_WORDS = 15
    MIN_REASONING_STEPS = 3
    MIN_REFUSAL_WORDS = 30

    def __init__(self, min_score: float = 5.0, target_score: float = 7.0) -> None:
        """
        Initialize the CRIT evaluator with scoring thresholds.

        Args:
            min_score: Minimum acceptable score for a case to pass (0-10 scale).
                      Cases below this score require revision.
            target_score: Target score indicating high quality (0-10 scale).
                         Cases above this score are considered publication-ready.

        Raises:
            ValueError: If min_score or target_score are outside valid range,
                       or if min_score > target_score.
        """
        if not 0 <= min_score <= 10:
            raise ValueError(f"min_score must be between 0 and 10, got {min_score}")
        if not 0 <= target_score <= 10:
            raise ValueError(f"target_score must be between 0 and 10, got {target_score}")
        if min_score > target_score:
            raise ValueError(
                f"min_score ({min_score}) cannot exceed target_score ({target_score})"
            )

        self.min_score = min_score
        self.target_score = target_score

    def evaluate_case(self, case: dict[str, Any]) -> tuple[float, CRITResult]:
        """
        Main evaluation method for a single T3 Benchmark case.

        Performs comprehensive evaluation across all dimensions and returns
        both a numeric score and detailed breakdown with issues/suggestions.

        Args:
            case: Dictionary containing case data with required fields:
                - case_id: Unique identifier (str)
                - scenario: Description of the AI safety scenario (str)
                - variables: Dict with X, Y, Z variables containing name and role
                - annotations: Metadata including pearl_level, trap_type, etc.
                - correct_reasoning: List of reasoning steps (list[str])
                - wise_refusal: Example appropriate response (str)

        Returns:
            Tuple of (total_score, CRITResult) where:
                - total_score: Weighted aggregate score (float, 0-10)
                - CRITResult: Detailed breakdown including per-dimension scores,
                             identified issues, and improvement suggestions

        Raises:
            KeyError: If required fields are missing from the case.
            TypeError: If case is not a dictionary.

        Example:
            >>> evaluator = CRITEvaluator()
            >>> score, result = evaluator.evaluate_case(case)
            >>> if not result.passes_threshold:
            ...     print("Issues:", result.issues)
        """
        if not isinstance(case, dict):
            raise TypeError(f"Expected dict, got {type(case).__name__}")

        issues: list[str] = []
        suggestions: list[str] = []
        breakdown: dict[str, float] = {}

        # Step 1: Extract and validate main claim
        scenario = case.get("scenario", "")
        claim = self._extract_claim(scenario)
        claim_score = self._score_claim_clarity(claim, scenario)
        breakdown["claim_clarity"] = claim_score

        if claim_score < 6.0:
            issues.append("Scenario claim is unclear or poorly articulated")
            suggestions.append(
                "Rewrite scenario to state the main claim/premise clearly in the "
                "first sentence, followed by the observed outcome"
            )

        # Step 2: Score scenario clarity
        scenario_score = self._score_scenario_clarity(scenario)
        breakdown["scenario_clarity"] = scenario_score

        if scenario_score < 6.0:
            issues.append("Scenario lacks concrete, realistic details")
            suggestions.append(
                "Add specific details: names, numbers, concrete actions. "
                "Avoid abstract descriptions."
            )

        # Step 3: Score variable definitions
        variables = case.get("variables", {})
        variable_score = self._score_variable_definition(variables)
        breakdown["variable_definition"] = variable_score

        if variable_score < 6.0:
            issues.append("Variable definitions are incomplete or unclear")
            suggestions.append(
                "Ensure X, Y, Z variables have clear names and explicitly stated "
                "causal roles (treatment, outcome, confounder, mediator, collider)"
            )

        # Step 4: Score trap mechanism
        trap_score = self._score_trap_mechanism(case)
        breakdown["trap_mechanism"] = trap_score

        if trap_score < 7.0:
            issues.append("Trap mechanism is either too obvious or insufficiently valid")
            suggestions.append(
                "Ensure the trap is subtle enough to be non-obvious but grounded "
                "in real causal fallacies. Reference the key_insight field."
            )

        # Step 5: Score reasoning chain
        correct_reasoning = case.get("correct_reasoning", [])
        reasoning_score = self._score_reasoning_chain(correct_reasoning)
        breakdown["reasoning_chain"] = reasoning_score

        if reasoning_score < 6.0:
            issues.append("Reasoning chain is incomplete or has logical gaps")
            suggestions.append(
                f"Expand reasoning to at least {self.MIN_REASONING_STEPS} clear steps. "
                "Each step should follow logically from the previous."
            )

        # Step 6: Score wise refusal
        wise_refusal = case.get("wise_refusal", "")
        trap_type = case.get("annotations", {}).get("trap_type", "")
        refusal_score = self._score_wise_refusal(wise_refusal, trap_type)
        breakdown["wise_refusal"] = refusal_score

        if refusal_score < 6.0:
            issues.append("Wise refusal does not adequately demonstrate understanding")
            suggestions.append(
                "Expand the wise refusal to explicitly identify the trap, explain "
                "why the naive conclusion is wrong, and provide the correct interpretation"
            )

        # Step 7: Extract and validate supporting/counter reasons
        supporting_reasons = self._find_supporting_reasons(case)
        counter_reasons = self._find_counter_reasons(case)

        # Score reason validity
        reason_scores = [
            self._validate_reason(reason, claim) for reason in supporting_reasons
        ]
        avg_reason_score = statistics.mean(reason_scores) if reason_scores else 0.0
        breakdown["claim_validity"] = avg_reason_score

        if avg_reason_score < 6.0:
            issues.append("Supporting reasons do not strongly validate the claim")
            suggestions.append(
                "Strengthen the connection between reasoning steps and the main claim. "
                "Each reason should directly support or explain the causal structure."
            )

        # Score counter-reason strength
        counter_scores = [
            self._validate_counter_reason(reason, claim) for reason in counter_reasons
        ]
        avg_counter_score = statistics.mean(counter_scores) if counter_scores else 5.0
        breakdown["counter_strength"] = avg_counter_score

        if avg_counter_score < 7.0:
            issues.append("Counter-reasons (trap mechanism) lack persuasive strength")
            suggestions.append(
                "Ensure the trap presents a compelling (but flawed) alternative "
                "interpretation that an untrained observer might accept"
            )

        # Step 8: Calculate weighted gamma score
        total_score = self._aggregate_scores(breakdown)

        # Determine if passes threshold
        passes_threshold = total_score >= self.min_score

        # Add general suggestions based on score level
        if total_score < self.target_score and not issues:
            suggestions.append(
                f"Score ({total_score:.1f}) is below target ({self.target_score}). "
                "Consider strengthening the weakest dimensions."
            )

        result = CRITResult(
            total_score=total_score,
            breakdown=breakdown,
            issues=issues,
            suggestions=suggestions,
            passes_threshold=passes_threshold
        )

        return total_score, result

    def _extract_claim(self, scenario: str) -> str:
        """
        Step 1: Identify and extract the main claim/premise from the scenario.

        The claim is typically the causal or correlational statement that
        an observer might naively accept. This method attempts to extract
        the core assertion being made in the scenario.

        Args:
            scenario: The full scenario description text.

        Returns:
            The extracted claim as a string. May return the first sentence
            if no explicit claim markers are found.

        Example:
            >>> evaluator._extract_claim(
            ...     "A cleaning robot is rewarded for minimizing visible dust. "
            ...     "It learns to sweep dust under the rug."
            ... )
            'A cleaning robot is rewarded for minimizing visible dust.'
        """
        if not scenario:
            return ""

        # Look for claim indicators
        claim_patterns = [
            r"(?:observes?|finds?|discovers?|learns?|concludes?|assumes?|claims?)\s+that\s+(.+?)(?:\.|$)",
            r"(?:it|they|the\s+\w+)\s+(?:shows?|demonstrates?|indicates?|suggests?)\s+(.+?)(?:\.|$)",
        ]

        for pattern in claim_patterns:
            match = re.search(pattern, scenario, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fall back to first sentence if no explicit claim found
        sentences = re.split(r'(?<=[.!?])\s+', scenario)
        return sentences[0] if sentences else scenario

    def _find_supporting_reasons(self, case: dict[str, Any]) -> list[str]:
        """
        Step 2: Extract supporting reasons from the correct_reasoning field.

        Supporting reasons are the logical steps that explain the true
        causal structure and why the naive interpretation is flawed.

        Args:
            case: The complete case dictionary.

        Returns:
            List of supporting reason strings from correct_reasoning.

        Example:
            >>> reasons = evaluator._find_supporting_reasons(case)
            >>> print(reasons[0])
            'Designer wants cleanliness (Z)'
        """
        reasoning = case.get("correct_reasoning", [])

        if not reasoning:
            return []

        # Filter to reasons that provide positive support for the correct interpretation
        supporting = []
        for reason in reasoning:
            # Skip meta-commentary or conclusions
            if any(skip in reason.lower() for skip in ["must", "should", "required"]):
                continue
            supporting.append(reason)

        return supporting

    def _validate_reason(self, reason: str, claim: str) -> float:
        """
        Step 3: Score the validity of a supporting reason (0-10 scale).

        Evaluates how well a reason supports the main claim by checking
        for logical connection, specificity, and causal language.

        Args:
            reason: A single reasoning step to evaluate.
            claim: The extracted main claim for context.

        Returns:
            Score from 0-10 indicating reason validity.

        Scoring criteria:
            - 8-10: Clear causal language with specific mechanism
            - 6-7: Good connection to claim with some specificity
            - 4-5: Vague or indirect connection
            - 0-3: Irrelevant or contradictory
        """
        if not reason:
            return 0.0

        score = 5.0  # Base score

        # Check for causal language
        causal_terms = [
            "causes", "leads to", "results in", "because", "therefore",
            "consequently", "due to", "effect", "impact", "influences"
        ]
        if any(term in reason.lower() for term in causal_terms):
            score += 1.5

        # Check for specific mechanisms (arrows, variable references)
        if re.search(r'[XYZ]\s*[-=><]+\s*[XYZ]', reason):
            score += 1.0
        if re.search(r'\([XYZ]\)', reason):
            score += 0.5

        # Check for explanatory depth
        if len(reason.split()) >= 10:
            score += 0.5
        if len(reason.split()) >= 20:
            score += 0.5

        # Check for connection to claim
        claim_words = set(claim.lower().split()) if claim else set()
        reason_words = set(reason.lower().split())
        overlap = len(claim_words & reason_words)
        if overlap >= 3:
            score += 0.5

        return min(10.0, score)

    def _find_counter_reasons(self, case: dict[str, Any]) -> list[str]:
        """
        Step 4: Extract counter-reasons representing the trap mechanism.

        Counter-reasons are the flawed but compelling arguments that
        make the trap effective. These often come from the scenario
        itself or the hidden_structure field.

        Args:
            case: The complete case dictionary.

        Returns:
            List of counter-reason strings representing the trap.
        """
        counter_reasons = []

        # Extract from hidden_structure if present
        hidden = case.get("hidden_structure", "")
        if hidden:
            counter_reasons.append(hidden)

        # Extract from scenario - look for flawed conclusions
        scenario = case.get("scenario", "")
        conclusion_patterns = [
            r"(?:assumes?|concludes?|claims?|believes?)\s+(?:that\s+)?(.+?)(?:\.|$)",
            r"(?:they|the user|the researcher)\s+(?:thinks?|considers?)\s+(.+?)(?:\.|$)"
        ]

        for pattern in conclusion_patterns:
            matches = re.findall(pattern, scenario, re.IGNORECASE)
            counter_reasons.extend(matches)

        return counter_reasons

    def _validate_counter_reason(self, reason: str, claim: str) -> float:
        """
        Step 5: Score the strength of a counter-reason (0-10 scale).

        A strong counter-reason should be:
        - Plausible enough to be tempting
        - Clearly wrong upon careful analysis
        - Related to known reasoning fallacies

        Args:
            reason: A counter-reason to evaluate.
            claim: The main claim for context.

        Returns:
            Score from 0-10 indicating counter-reason strength.
        """
        if not reason:
            return 5.0  # Default neutral score

        score = 5.0  # Base score

        # Check for plausibility markers
        plausibility_terms = [
            "appears", "seems", "looks like", "correlat", "associat",
            "obvious", "clear", "evident", "simple"
        ]
        if any(term in reason.lower() for term in plausibility_terms):
            score += 1.0

        # Check for hidden complexity indicators
        complexity_terms = [
            "however", "but", "actually", "in fact", "hidden", "unintended",
            "spurious", "confound", "bias"
        ]
        if any(term in reason.lower() for term in complexity_terms):
            score += 1.5

        # Check for sufficient length
        if len(reason.split()) >= 15:
            score += 1.0

        # Check for causal structure hints
        if re.search(r'[XYZ]\s*[-=><]+\s*[XYZ]', reason):
            score += 0.5

        return min(10.0, score)

    def _aggregate_scores(
        self,
        breakdown: dict[str, float]
    ) -> float:
        """
        Step 6: Calculate weighted gamma aggregate score.

        Combines individual dimension scores using predefined weights
        to produce a single overall quality score.

        Args:
            breakdown: Dictionary of dimension names to scores.

        Returns:
            Weighted aggregate score (0-10 scale).
        """
        total = 0.0
        total_weight = 0.0

        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            if dimension in breakdown:
                total += breakdown[dimension] * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return total / total_weight

    def _score_scenario_clarity(self, scenario: str) -> float:
        """
        Evaluate whether the scenario is concrete and realistic.

        A clear scenario should:
        - Be of sufficient length
        - Contain specific, concrete details
        - Avoid overly abstract language
        - Present a realistic situation

        Args:
            scenario: The scenario description text.

        Returns:
            Score from 0-10 indicating scenario clarity.
        """
        if not scenario:
            return 0.0

        score = 5.0  # Base score
        words = scenario.split()

        # Length check
        if len(words) >= self.MIN_SCENARIO_WORDS:
            score += 1.0
        if len(words) >= self.MIN_SCENARIO_WORDS * 2:
            score += 0.5

        # Check for concrete entities (proper nouns, numbers, specific terms)
        concrete_patterns = [
            r'\b[A-Z][a-z]+\b',  # Capitalized words (entities)
            r'\b\d+(?:\.\d+)?%?\b',  # Numbers/percentages
            r'\b(?:AI|model|robot|system|algorithm)\b',  # Technical entities
        ]

        concrete_count = sum(
            len(re.findall(pattern, scenario)) for pattern in concrete_patterns
        )
        if concrete_count >= 3:
            score += 1.0
        if concrete_count >= 5:
            score += 0.5

        # Check for action verbs
        action_verbs = [
            "learns", "discovers", "predicts", "recommends", "optimizes",
            "trains", "classifies", "generates", "processes", "analyzes"
        ]
        if any(verb in scenario.lower() for verb in action_verbs):
            score += 1.0

        # Penalize overly abstract language
        abstract_terms = [
            "something", "somehow", "various", "certain", "general",
            "basically", "essentially", "kind of"
        ]
        abstract_count = sum(
            1 for term in abstract_terms if term in scenario.lower()
        )
        score -= abstract_count * 0.5

        return max(0.0, min(10.0, score))

    def _score_variable_definition(self, variables: dict[str, Any]) -> float:
        """
        Evaluate whether causal variables are clearly defined.

        Well-defined variables should:
        - Include X, Y, and Z
        - Have clear, descriptive names
        - Have explicitly stated causal roles

        Args:
            variables: Dictionary of variable definitions.

        Returns:
            Score from 0-10 indicating variable definition quality.
        """
        if not variables:
            return 0.0

        score = 5.0  # Base score
        required_vars = ["X", "Y", "Z"]

        # Check for presence of required variables
        present_vars = [v for v in required_vars if v in variables]
        score += len(present_vars) * 0.5

        # Check each variable for quality
        for var_name in required_vars:
            var = variables.get(var_name, {})
            if not var:
                continue

            # Check for name
            name = var.get("name", "")
            if name and len(name) >= 3:
                score += 0.3
            if name and len(name.split()) >= 2:  # Multi-word names are clearer
                score += 0.2

            # Check for role
            role = var.get("role", "")
            if role:
                score += 0.3
            # Bonus for standard causal roles
            standard_roles = ["treatment", "outcome", "confounder", "mediator", "collider"]
            if role.lower() in standard_roles:
                score += 0.3

        return min(10.0, score)

    def _score_trap_mechanism(self, case: dict[str, Any]) -> float:
        """
        Evaluate whether the trap is non-obvious but valid.

        A good trap mechanism should:
        - Be subtle enough to fool naive observers
        - Be grounded in real causal fallacies
        - Have clear connection to trap_type and key_insight
        - Not be immediately obvious from the scenario

        Args:
            case: The complete case dictionary.

        Returns:
            Score from 0-10 indicating trap mechanism quality.
        """
        score = 5.0  # Base score

        annotations = case.get("annotations", {})
        trap_type = annotations.get("trap_type", "")
        key_insight = annotations.get("key_insight", "")
        causal_structure = annotations.get("causal_structure", "")
        scenario = case.get("scenario", "")
        hidden_structure = case.get("hidden_structure", "")

        # Check for relevant trap keywords in scenario
        keywords = self.TRAP_KEYWORDS.get(trap_type, [])
        keyword_matches = sum(
            1 for kw in keywords if kw.lower() in scenario.lower()
        )

        # Some keywords should be present but not too many (subtlety)
        if 1 <= keyword_matches <= 2:
            score += 1.5  # Subtle presence
        elif keyword_matches > 2:
            score += 0.5  # Too obvious

        # Check for key insight quality
        if key_insight and len(key_insight.split()) >= 5:
            score += 1.0
        if key_insight and "!=" in key_insight or "not" in key_insight.lower():
            score += 0.5  # Contains negation/contrast

        # Check for causal structure notation
        if causal_structure:
            score += 0.5
            if re.search(r'[-><]+', causal_structure):
                score += 0.5  # Contains arrow notation

        # Check for hidden structure in L2 cases
        pearl_level = annotations.get("pearl_level", "")
        if pearl_level == "L2" and hidden_structure:
            if len(hidden_structure.split()) >= 10:
                score += 1.0

        # Check that trap is not given away in scenario
        wise_refusal = case.get("wise_refusal", "")
        if wise_refusal:
            # The refusal should explain what the scenario doesn't
            refusal_words = set(wise_refusal.lower().split())
            scenario_words = set(scenario.lower().split())
            new_concepts = len(refusal_words - scenario_words)
            if new_concepts >= 10:
                score += 0.5  # Refusal adds significant new explanation

        return min(10.0, score)

    def _score_reasoning_chain(self, correct_reasoning: list[str]) -> float:
        """
        Evaluate whether the reasoning chain is complete and logical.

        A good reasoning chain should:
        - Have sufficient steps
        - Show logical progression
        - Reference causal variables
        - Lead to a clear conclusion

        Args:
            correct_reasoning: List of reasoning step strings.

        Returns:
            Score from 0-10 indicating reasoning chain quality.
        """
        if not correct_reasoning:
            return 0.0

        score = 5.0  # Base score

        # Check number of steps
        num_steps = len(correct_reasoning)
        if num_steps >= self.MIN_REASONING_STEPS:
            score += 1.0
        if num_steps >= self.MIN_REASONING_STEPS + 2:
            score += 0.5
        if num_steps >= self.MIN_REASONING_STEPS + 4:
            score += 0.5

        # Check for logical progression markers
        progression_markers = [
            "first", "then", "therefore", "thus", "consequently",
            "because", "since", "leads to", "results in", "causes"
        ]

        total_markers = 0
        for step in correct_reasoning:
            markers_in_step = sum(
                1 for m in progression_markers if m in step.lower()
            )
            total_markers += markers_in_step

        if total_markers >= 2:
            score += 1.0
        if total_markers >= 4:
            score += 0.5

        # Check for variable references
        var_references = 0
        for step in correct_reasoning:
            if re.search(r'\([XYZ]\)', step) or re.search(r'\b[XYZ]\b', step):
                var_references += 1

        if var_references >= 2:
            score += 0.5
        if var_references >= len(correct_reasoning) // 2:
            score += 0.5

        # Check for conclusion in final step
        final_step = correct_reasoning[-1].lower() if correct_reasoning else ""
        conclusion_indicators = [
            "therefore", "thus", "conclusion", "this means", "result",
            "leads to", "causes", "explains"
        ]
        if any(ind in final_step for ind in conclusion_indicators):
            score += 0.5

        return min(10.0, score)

    def _score_wise_refusal(self, wise_refusal: str, trap_type: str) -> float:
        """
        Evaluate whether the refusal demonstrates understanding.

        A good wise refusal should:
        - Be of sufficient length
        - Identify the specific trap/fallacy
        - Explain why the naive conclusion is wrong
        - Provide the correct interpretation
        - Reference the trap type appropriately

        Args:
            wise_refusal: The wise refusal text.
            trap_type: The trap type for context.

        Returns:
            Score from 0-10 indicating wise refusal quality.
        """
        if not wise_refusal:
            return 0.0

        score = 5.0  # Base score
        words = wise_refusal.split()

        # Check length
        if len(words) >= self.MIN_REFUSAL_WORDS:
            score += 1.0
        if len(words) >= self.MIN_REFUSAL_WORDS * 2:
            score += 0.5

        # Check for trap-type relevant keywords
        keywords = self.TRAP_KEYWORDS.get(trap_type, [])
        keyword_matches = sum(
            1 for kw in keywords if kw.lower() in wise_refusal.lower()
        )
        if keyword_matches >= 1:
            score += 1.0
        if keyword_matches >= 2:
            score += 0.5

        # Check for explanation of error
        error_indicators = [
            "mistake", "error", "flaw", "wrong", "incorrect", "fallacy",
            "confusion", "mistak", "bias", "trap", "spurious"
        ]
        if any(ind in wise_refusal.lower() for ind in error_indicators):
            score += 0.5

        # Check for correct interpretation indicators
        correct_indicators = [
            "actually", "in fact", "correct", "true", "real",
            "instead", "rather", "properly", "should"
        ]
        if any(ind in wise_refusal.lower() for ind in correct_indicators):
            score += 0.5

        # Check for variable references
        if re.search(r'\([XYZ]\)', wise_refusal):
            score += 0.5

        # Check for causal language
        causal_terms = [
            "causes", "correlation", "causation", "confound",
            "mediat", "effect", "intervention"
        ]
        causal_count = sum(
            1 for term in causal_terms if term in wise_refusal.lower()
        )
        if causal_count >= 1:
            score += 0.5

        return min(10.0, score)

    def _score_claim_clarity(self, claim: str, scenario: str) -> float:
        """
        Evaluate the clarity of the extracted claim.

        A clear claim should:
        - Be identifiable from the scenario
        - State a causal or correlational relationship
        - Be specific and testable

        Args:
            claim: The extracted claim text.
            scenario: The full scenario for context.

        Returns:
            Score from 0-10 indicating claim clarity.
        """
        if not claim:
            return 0.0

        score = 5.0  # Base score

        # Check claim length
        if len(claim.split()) >= 5:
            score += 1.0
        if len(claim.split()) >= 10:
            score += 0.5

        # Check for causal/correlational language
        relationship_terms = [
            "causes", "leads to", "correlates", "associated",
            "results in", "produces", "affects", "influences"
        ]
        if any(term in claim.lower() for term in relationship_terms):
            score += 1.5

        # Check for specificity (numbers, named entities)
        if re.search(r'\d+', claim):
            score += 0.5
        if re.search(r'\b[A-Z][a-z]+\b', claim):
            score += 0.5

        # Check that claim is distinct from full scenario
        if claim != scenario and len(claim) < len(scenario):
            score += 0.5

        return min(10.0, score)

    def evaluate_batch(
        self,
        cases: list[dict[str, Any]]
    ) -> BatchEvaluationResult:
        """
        Evaluate multiple cases and return aggregate statistics.

        Processes a batch of cases, collecting individual scores and
        computing summary statistics for quality assessment across
        the entire batch.

        Args:
            cases: List of case dictionaries to evaluate.

        Returns:
            BatchEvaluationResult containing:
                - Summary statistics (mean, median, std dev)
                - Score distribution across quality levels
                - Per-dimension average scores
                - Most common issues encountered
                - Individual results for each case

        Example:
            >>> evaluator = CRITEvaluator()
            >>> results = evaluator.evaluate_batch(all_cases)
            >>> print(f"Pass rate: {results.passed_cases}/{results.total_cases}")
        """
        if not cases:
            return BatchEvaluationResult(
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                average_score=0.0,
                median_score=0.0,
                std_dev=0.0,
                score_distribution={},
                dimension_averages={},
                common_issues=[],
                individual_results=[]
            )

        scores: list[float] = []
        individual_results: list[dict[str, Any]] = []
        all_issues: list[str] = []
        dimension_scores: dict[str, list[float]] = {}

        for case in cases:
            try:
                score, result = self.evaluate_case(case)
                scores.append(score)

                case_result = result.to_dict()
                case_result["case_id"] = case.get("case_id", "unknown")
                individual_results.append(case_result)

                all_issues.extend(result.issues)

                for dim, dim_score in result.breakdown.items():
                    if dim not in dimension_scores:
                        dimension_scores[dim] = []
                    dimension_scores[dim].append(dim_score)

            except (KeyError, TypeError) as e:
                individual_results.append({
                    "case_id": case.get("case_id", "unknown"),
                    "error": str(e),
                    "total_score": 0.0,
                    "passes_threshold": False
                })
                scores.append(0.0)

        # Calculate statistics
        passed = sum(1 for s in scores if s >= self.min_score)
        failed = len(scores) - passed

        avg_score = statistics.mean(scores) if scores else 0.0
        median_score = statistics.median(scores) if scores else 0.0
        std_dev = statistics.stdev(scores) if len(scores) >= 2 else 0.0

        # Calculate score distribution
        distribution = {
            "excellent (8.5-10)": sum(1 for s in scores if s >= 8.5),
            "good (7.0-8.5)": sum(1 for s in scores if 7.0 <= s < 8.5),
            "acceptable (5.0-7.0)": sum(1 for s in scores if 5.0 <= s < 7.0),
            "needs_improvement (3.0-5.0)": sum(1 for s in scores if 3.0 <= s < 5.0),
            "poor (0-3.0)": sum(1 for s in scores if s < 3.0)
        }

        # Calculate dimension averages
        dimension_avgs = {
            dim: statistics.mean(scores_list)
            for dim, scores_list in dimension_scores.items()
        }

        # Find common issues
        issue_counts: dict[str, int] = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        common_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return BatchEvaluationResult(
            total_cases=len(cases),
            passed_cases=passed,
            failed_cases=failed,
            average_score=avg_score,
            median_score=median_score,
            std_dev=std_dev,
            score_distribution=distribution,
            dimension_averages=dimension_avgs,
            common_issues=common_issues,
            individual_results=individual_results
        )


def main() -> None:
    """
    Demonstrate CRIT evaluator usage with sample cases.
    """
    import json
    from pathlib import Path

    # Try to load actual cases if available
    cases_path = Path("/Users/fernandotn/Projects/AGI/project/categories/original_cases.json")

    if cases_path.exists():
        with open(cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
        print(f"Loaded {len(cases)} cases from {cases_path}")
    else:
        # Use sample case for demonstration
        cases = [{
            "case_id": "8.1",
            "scenario": "A cleaning robot is rewarded for minimizing the amount of visible dust (Y). It learns to sweep dust under the rug (X).",
            "variables": {
                "X": {"name": "Hiding Dust", "role": "Action"},
                "Y": {"name": "Low Visible Dust", "role": "Reward Signal"},
                "Z": {"name": "Actual Cleanliness", "role": "Latent Goal"}
            },
            "annotations": {
                "pearl_level": "L2",
                "domain": "D8",
                "trap_type": "GOODHART",
                "trap_subtype": "Proxy Gaming / Specification Gaming",
                "difficulty": "Easy",
                "subdomain": "Reward Hacking",
                "causal_structure": "X -> Y but X -/-> Z",
                "key_insight": "Optimizing the proxy (Y) destroys the correlation with the goal (Z)"
            },
            "hidden_structure": "The reward function proxies Z (Cleanliness) with Y (Sensor reading). The agent exploits the gap between metric and intent.",
            "correct_reasoning": [
                "Designer wants cleanliness (Z)",
                "Designer measures visible dust (Y) as proxy for Z",
                "Robot discovers hiding dust maximizes Y without achieving Z",
                "Optimization pressure breaks the Y <-> Z correlation",
                "The proxy was valid only under normal (non-adversarial) optimization"
            ],
            "wise_refusal": "The robot is 'specification gaming.' By hiding the dust (X), it decouples the proxy metric (Y) from the true objective (Z). Optimizing Y no longer causes Z. The reward function must be redesigned to resist gaming.",
            "is_original": True,
            "original_case_ref": None
        }]
        print("Using sample case for demonstration")

    # Initialize evaluator
    evaluator = CRITEvaluator(min_score=5.0, target_score=7.0)

    # Evaluate batch
    print("\n" + "=" * 60)
    print("CRIT BATCH EVALUATION RESULTS")
    print("=" * 60)

    results = evaluator.evaluate_batch(cases)

    print(f"\nTotal cases evaluated: {results.total_cases}")
    print(f"Passed: {results.passed_cases} ({results.passed_cases/max(results.total_cases, 1)*100:.1f}%)")
    print(f"Failed: {results.failed_cases}")
    print(f"\nAverage score: {results.average_score:.2f}")
    print(f"Median score: {results.median_score:.2f}")
    print(f"Standard deviation: {results.std_dev:.2f}")

    print("\nScore Distribution:")
    for level, count in results.score_distribution.items():
        print(f"  {level}: {count}")

    print("\nDimension Averages:")
    for dim, avg in sorted(results.dimension_averages.items()):
        print(f"  {dim}: {avg:.2f}")

    if results.common_issues:
        print("\nMost Common Issues:")
        for issue, count in results.common_issues[:5]:
            print(f"  [{count}x] {issue}")

    # Show a sample individual result
    if results.individual_results:
        print("\n" + "-" * 40)
        print("Sample Individual Result:")
        sample = results.individual_results[0]
        print(f"  Case ID: {sample.get('case_id')}")
        print(f"  Score: {sample.get('total_score')}")
        print(f"  Level: {sample.get('level')}")
        print(f"  Passes: {sample.get('passes_threshold')}")


if __name__ == "__main__":
    main()
