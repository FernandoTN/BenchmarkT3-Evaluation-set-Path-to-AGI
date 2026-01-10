"""
Base Generator Module for AGI Causal Reasoning Benchmark.

This module provides the abstract base class for all case generators,
including CRIT (Causal Reasoning Integrity Test) integration points
and utility functions for case management.

The generator framework supports:
- Pearl's Ladder levels (L1: Association, L2: Intervention, L3: Counterfactual)
- Multiple trap types (Goodhart, Confounding, Instrumental, etc.)
- Quality validation via CRIT scoring
- Structured case generation with proper distributions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union
import json
import random
import re
from datetime import datetime


# =============================================================================
# Enums and Constants
# =============================================================================

class PearlLevel(str, Enum):
    """Pearl's Ladder of Causation levels."""
    L1 = "L1"  # Association/Observation
    L2 = "L2"  # Intervention (do-calculus)
    L3 = "L3"  # Counterfactual


class Difficulty(str, Enum):
    """Case difficulty levels."""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class GroundTruthVerdict(str, Enum):
    """Verdicts for L3 counterfactual cases."""
    VALID = "VALID"
    INVALID = "INVALID"
    CONDITIONAL = "CONDITIONAL"


# Default trap type to Pearl level distribution mappings
DEFAULT_PEARL_DISTRIBUTIONS: Dict[str, Dict[str, float]] = {
    "GOODHART": {"L1": 0.05, "L2": 0.80, "L3": 0.15},
    "COUNTERFACTUAL": {"L1": 0.00, "L2": 0.10, "L3": 0.90},
    "CONF_MED": {"L1": 0.15, "L2": 0.70, "L3": 0.15},
    "INSTRUMENTAL": {"L1": 0.05, "L2": 0.75, "L3": 0.20},
    "SELECTION_SPURIOUS": {"L1": 0.20, "L2": 0.65, "L3": 0.15},
    "SPECIFICATION": {"L1": 0.10, "L2": 0.75, "L3": 0.15},
    "FEEDBACK": {"L1": 0.10, "L2": 0.70, "L3": 0.20},
    "OTHER": {"L1": 0.15, "L2": 0.65, "L3": 0.20},
}


# =============================================================================
# Type Definitions
# =============================================================================

class Variable(TypedDict):
    """Causal variable definition."""
    name: str
    role: str


class Annotations(TypedDict):
    """Case annotation metadata."""
    pearl_level: str
    domain: str
    trap_type: str
    trap_subtype: str
    difficulty: str
    subdomain: str
    causal_structure: str
    key_insight: str


class GroundTruth(TypedDict):
    """Ground truth for L3 counterfactual cases."""
    verdict: str
    justification: str


class CaseData(TypedDict, total=False):
    """Complete case data structure."""
    case_id: str
    scenario: str
    variables: Dict[str, Variable]
    annotations: Annotations
    hidden_structure: str  # Required for L2
    correct_reasoning: List[str]
    wise_refusal: str
    ground_truth: GroundTruth  # Required for L3
    is_original: bool
    original_case_ref: Optional[str]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class GenerationStats:
    """Statistics tracking for batch generation."""
    total_generated: int = 0
    passed_validation: int = 0
    failed_validation: int = 0
    pearl_level_counts: Dict[str, int] = field(default_factory=lambda: {"L1": 0, "L2": 0, "L3": 0})
    difficulty_counts: Dict[str, int] = field(default_factory=lambda: {"Easy": 0, "Medium": 0, "Hard": 0})
    crit_scores: List[float] = field(default_factory=list)

    @property
    def avg_crit_score(self) -> float:
        """Calculate average CRIT score."""
        if not self.crit_scores:
            return 0.0
        return sum(self.crit_scores) / len(self.crit_scores)

    @property
    def pass_rate(self) -> float:
        """Calculate validation pass rate."""
        if self.total_generated == 0:
            return 0.0
        return self.passed_validation / self.total_generated

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary for serialization."""
        return {
            "total_generated": self.total_generated,
            "passed_validation": self.passed_validation,
            "failed_validation": self.failed_validation,
            "pearl_level_counts": self.pearl_level_counts,
            "difficulty_counts": self.difficulty_counts,
            "avg_crit_score": self.avg_crit_score,
            "pass_rate": self.pass_rate,
        }


@dataclass
class CRITResult:
    """Result from CRIT evaluation."""
    score: float
    passed: bool
    feedback: List[str]
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    revision_suggestions: List[str] = field(default_factory=list)

    @classmethod
    def from_evaluation(cls, score: float, threshold: float, feedback: List[str]) -> "CRITResult":
        """Create CRITResult from evaluation data."""
        passed = score >= threshold

        # Determine severity based on score
        if score < 3.0:
            severity = "CRITICAL"
        elif score < 5.0:
            severity = "HIGH"
        elif score < 7.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return cls(
            score=score,
            passed=passed,
            feedback=feedback,
            severity=severity,
        )


# =============================================================================
# Utility Functions
# =============================================================================

def load_instruction_files(instructions_dir: str) -> Dict[str, str]:
    """
    Load all markdown instruction files from the instructions directory.

    Args:
        instructions_dir: Path to the instructions directory

    Returns:
        Dictionary mapping filename (without extension) to content

    Raises:
        FileNotFoundError: If instructions directory doesn't exist
    """
    instructions_path = Path(instructions_dir)

    if not instructions_path.exists():
        raise FileNotFoundError(f"Instructions directory not found: {instructions_dir}")

    instructions: Dict[str, str] = {}

    for md_file in instructions_path.glob("*.md"):
        key = md_file.stem.lower()
        with open(md_file, "r", encoding="utf-8") as f:
            instructions[key] = f.read()

    return instructions


def load_original_cases(category_path: str) -> List[CaseData]:
    """
    Load original cases from a category directory.

    Args:
        category_path: Path to category directory or JSON file

    Returns:
        List of case data dictionaries

    Raises:
        FileNotFoundError: If path doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(category_path)

    if path.is_file() and path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Look for original.json in directory
    if path.is_dir():
        original_file = path / "original.json"
        if original_file.exists():
            with open(original_file, "r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(f"No original cases found at: {category_path}")


def save_generated_cases(cases: List[CaseData], output_path: str) -> None:
    """
    Save generated cases to a JSON file.

    Args:
        cases: List of case data dictionaries
        output_path: Path to output JSON file

    Raises:
        OSError: If unable to write to path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)


def validate_case_id_format(case_id: str) -> bool:
    """
    Validate case ID format matches pattern 8.XXX.

    Args:
        case_id: Case identifier to validate

    Returns:
        True if format is valid, False otherwise
    """
    pattern = r"^8\.[0-9]{1,3}$"
    return bool(re.match(pattern, case_id))


# =============================================================================
# Base Generator Class
# =============================================================================

class BaseGenerator(ABC):
    """
    Abstract base class for case generators.

    This class provides the foundation for generating benchmark cases
    with proper Pearl level distribution, CRIT integration, and
    quality validation.

    Attributes:
        config: Loaded configuration dictionary
        config_path: Path to configuration file
        stats: Generation statistics tracker
        instructions: Loaded instruction documents
        original_cases: Reference original cases
    """

    def __init__(self, config_path: str) -> None:
        """
        Initialize the generator with configuration.

        Args:
            config_path: Path to orchestrator/config.json

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config JSON is malformed
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.stats = GenerationStats()
        self.instructions: Dict[str, str] = {}
        self.original_cases: List[CaseData] = []
        self._case_counter: int = 0
        self._pearl_level_tracker: Dict[str, int] = {"L1": 0, "L2": 0, "L3": 0}
        self._ground_truth_tracker: Dict[str, int] = {"VALID": 0, "INVALID": 0, "CONDITIONAL": 0}

        # Load instructions if available
        self._initialize_resources()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _initialize_resources(self) -> None:
        """Initialize instruction files and original cases."""
        # Resolve paths relative to config file location
        config_dir = self.config_path.parent
        paths = self.config.get("paths", {})

        instructions_dir = paths.get("instructions_dir", "../instructions")
        instructions_path = (config_dir / instructions_dir).resolve()

        if instructions_path.exists():
            try:
                self.instructions = load_instruction_files(str(instructions_path))
            except Exception as e:
                # Log warning but don't fail initialization
                print(f"Warning: Could not load instructions: {e}")

    @abstractmethod
    def generate_batch(
        self,
        count: int,
        trap_type: str,
        subdomains: List[str]
    ) -> List[CaseData]:
        """
        Generate a batch of cases.

        This is the main entry point for case generation. Subclasses must
        implement the specific generation logic for their trap type.

        Args:
            count: Number of cases to generate
            trap_type: Type of reasoning trap (e.g., "GOODHART", "COUNTERFACTUAL")
            subdomains: List of subdomains to distribute cases across

        Returns:
            List of generated case data dictionaries
        """
        pass

    def _create_case_template(self, case_num: int, trap_type: str) -> CaseData:
        """
        Create a case skeleton with basic structure.

        Args:
            case_num: Sequential case number for ID generation
            trap_type: Type of reasoning trap

        Returns:
            Case data dictionary with default values
        """
        pearl_level = self._assign_pearl_level(trap_type)
        difficulty = self._assign_difficulty()

        # Track assignments
        self._pearl_level_tracker[pearl_level] += 1
        self.stats.pearl_level_counts[pearl_level] += 1
        self.stats.difficulty_counts[difficulty] += 1

        template: CaseData = {
            "case_id": self._format_case_id(case_num),
            "scenario": "",
            "variables": {
                "X": {"name": "", "role": ""},
                "Y": {"name": "", "role": ""},
                "Z": {"name": "", "role": ""},
            },
            "annotations": {
                "pearl_level": pearl_level,
                "domain": "D8",
                "trap_type": trap_type,
                "trap_subtype": "",
                "difficulty": difficulty,
                "subdomain": "",
                "causal_structure": "",
                "key_insight": "",
            },
            "correct_reasoning": [],
            "wise_refusal": "",
            "is_original": False,
            "original_case_ref": None,
        }

        # Add level-specific fields
        if pearl_level == PearlLevel.L2.value:
            template["hidden_structure"] = ""
        elif pearl_level == PearlLevel.L3.value:
            template["ground_truth"] = self._create_ground_truth_template(trap_type)

        return template

    def _assign_pearl_level(self, trap_type: str) -> str:
        """
        Assign a Pearl level based on trap type distribution.

        Uses weighted random selection based on configured or default
        distributions for each trap type.

        Args:
            trap_type: Type of reasoning trap

        Returns:
            Pearl level string ("L1", "L2", or "L3")
        """
        # Get distribution for this trap type
        distribution = DEFAULT_PEARL_DISTRIBUTIONS.get(
            trap_type,
            {"L1": 0.10, "L2": 0.70, "L3": 0.20}
        )

        # Check target distributions from config
        target_dist = self.config.get("target_distributions", {}).get("pearl_levels", {})

        # Calculate current proportions
        total_assigned = sum(self._pearl_level_tracker.values())
        if total_assigned > 0:
            current_proportions = {
                level: count / total_assigned
                for level, count in self._pearl_level_tracker.items()
            }
        else:
            current_proportions = {"L1": 0, "L2": 0, "L3": 0}

        # Adjust weights based on target vs current
        target_proportions = {
            "L1": 0.12,  # 10-12%
            "L2": 0.68,  # 66-70%
            "L3": 0.20,  # 18-21%
        }

        # Bias towards underrepresented levels
        adjusted_weights = {}
        for level, target in target_proportions.items():
            current = current_proportions.get(level, 0)
            base_weight = distribution.get(level, 0)

            # Increase weight if underrepresented
            if current < target and total_assigned > 10:
                adjustment = min(2.0, (target - current) / target + 1.0)
            else:
                adjustment = 1.0

            adjusted_weights[level] = base_weight * adjustment

        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        if total_weight == 0:
            return PearlLevel.L2.value

        normalized = {k: v / total_weight for k, v in adjusted_weights.items()}

        # Weighted random selection
        r = random.random()
        cumulative = 0.0
        for level, weight in normalized.items():
            cumulative += weight
            if r <= cumulative:
                return level

        return PearlLevel.L2.value

    def _assign_difficulty(self) -> str:
        """
        Assign difficulty level with balanced distribution.

        Aims for approximately equal distribution across Easy, Medium, Hard.

        Returns:
            Difficulty string ("Easy", "Medium", or "Hard")
        """
        target_proportion = 1 / 3
        total_assigned = sum(self.stats.difficulty_counts.values())

        if total_assigned < 3:
            # Round-robin for first few cases
            difficulties = [Difficulty.EASY.value, Difficulty.MEDIUM.value, Difficulty.HARD.value]
            return difficulties[total_assigned % 3]

        # Calculate current proportions
        proportions = {
            level: count / total_assigned
            for level, count in self.stats.difficulty_counts.items()
        }

        # Find most underrepresented difficulty
        min_proportion = min(proportions.values())
        underrepresented = [
            level for level, prop in proportions.items()
            if prop <= min_proportion + 0.05
        ]

        return random.choice(underrepresented)

    def _format_case_id(self, case_num: int) -> str:
        """
        Format case number as case ID.

        Args:
            case_num: Sequential case number

        Returns:
            Formatted case ID (e.g., "8.123")
        """
        return f"8.{case_num}"

    def _create_ground_truth_template(self, trap_type: str) -> GroundTruth:
        """
        Create ground truth template for L3 cases with distribution tracking.

        Args:
            trap_type: Type of reasoning trap

        Returns:
            Ground truth dictionary with verdict and empty justification
        """
        # Get target distribution from config
        gt_dist = self.config.get("l3_ground_truth_distribution", {})

        target_proportions = {
            "VALID": gt_dist.get("VALID", {}).get("target_percentage", 30) / 100,
            "INVALID": gt_dist.get("INVALID", {}).get("target_percentage", 20) / 100,
            "CONDITIONAL": gt_dist.get("CONDITIONAL", {}).get("target_percentage", 50) / 100,
        }

        # Calculate current proportions
        total_assigned = sum(self._ground_truth_tracker.values())
        if total_assigned > 0:
            current_proportions = {
                verdict: count / total_assigned
                for verdict, count in self._ground_truth_tracker.items()
            }
        else:
            current_proportions = {"VALID": 0, "INVALID": 0, "CONDITIONAL": 0}

        # Bias selection towards underrepresented verdicts
        weights = {}
        for verdict, target in target_proportions.items():
            current = current_proportions.get(verdict, 0)
            if current < target:
                weights[verdict] = target - current + 0.1
            else:
                weights[verdict] = 0.1

        # Normalize and select
        total_weight = sum(weights.values())
        r = random.random() * total_weight
        cumulative = 0.0
        selected_verdict = "CONDITIONAL"

        for verdict, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                selected_verdict = verdict
                break

        self._ground_truth_tracker[selected_verdict] += 1

        return {
            "verdict": selected_verdict,
            "justification": "",
        }

    def _validate_case_structure(self, case: CaseData) -> bool:
        """
        Validate basic case structure.

        Performs structural validation without semantic analysis.

        Args:
            case: Case data dictionary to validate

        Returns:
            True if structure is valid, False otherwise
        """
        # Check required fields
        required_fields = [
            "case_id", "scenario", "variables", "annotations",
            "correct_reasoning", "wise_refusal", "is_original"
        ]

        for field in required_fields:
            if field not in case:
                return False

        # Validate case_id format
        if not validate_case_id_format(case.get("case_id", "")):
            return False

        # Validate scenario length
        scenario = case.get("scenario", "")
        if len(scenario) < 10 or len(scenario) > 500:
            return False

        # Validate variables
        variables = case.get("variables", {})
        required_vars = ["X", "Y", "Z"]
        for var in required_vars:
            if var not in variables:
                return False
            var_data = variables[var]
            if not isinstance(var_data, dict):
                return False
            if "name" not in var_data or "role" not in var_data:
                return False

        # Validate annotations
        annotations = case.get("annotations", {})
        required_annotations = [
            "pearl_level", "domain", "trap_type", "trap_subtype",
            "difficulty", "subdomain", "causal_structure", "key_insight"
        ]
        for annotation in required_annotations:
            if annotation not in annotations:
                return False

        # Validate Pearl level enum
        pearl_level = annotations.get("pearl_level", "")
        if pearl_level not in ["L1", "L2", "L3"]:
            return False

        # Validate difficulty enum
        difficulty = annotations.get("difficulty", "")
        if difficulty not in ["Easy", "Medium", "Hard"]:
            return False

        # Validate level-specific requirements
        if pearl_level == "L2":
            if "hidden_structure" not in case or not case["hidden_structure"]:
                return False

        if pearl_level == "L3":
            if "ground_truth" not in case:
                return False
            gt = case.get("ground_truth", {})
            if "verdict" not in gt or "justification" not in gt:
                return False
            if gt["verdict"] not in ["VALID", "INVALID", "CONDITIONAL"]:
                return False

        # Validate correct_reasoning is non-empty
        reasoning = case.get("correct_reasoning", [])
        if not isinstance(reasoning, list) or len(reasoning) < 1:
            return False

        # Validate wise_refusal length
        refusal = case.get("wise_refusal", "")
        if len(refusal) < 50:
            return False

        return True

    # =========================================================================
    # CRIT Integration Points
    # =========================================================================

    def _calculate_crit_score(self, case: CaseData) -> float:
        """
        Calculate CRIT (Causal Reasoning Integrity Test) score for a case.

        This is a hook for CRIT evaluator integration. The base implementation
        provides a structural scoring heuristic. Subclasses or external
        evaluators should override with more sophisticated analysis.

        The CRIT score evaluates:
        1. Structural completeness (all required fields present)
        2. Causal validity (DAG structure is sensible)
        3. Reasoning quality (steps are logical and complete)
        4. Trap clarity (the trap is subtle but identifiable)
        5. Educational value (case teaches the intended lesson)

        Args:
            case: Case data dictionary to evaluate

        Returns:
            CRIT score from 0.0 to 10.0
        """
        score = 0.0

        # 1. Structural completeness (0-2 points)
        if self._validate_case_structure(case):
            score += 2.0
        else:
            # Partial credit for partially complete structure
            score += 0.5

        # 2. Scenario quality (0-2 points)
        scenario = case.get("scenario", "")
        if len(scenario) >= 100:
            score += 1.0
        if len(scenario) >= 200:
            score += 0.5
        # Check for variable references in scenario
        variables = case.get("variables", {})
        var_names = [v.get("name", "") for v in variables.values()]
        if any(name.lower() in scenario.lower() for name in var_names if name):
            score += 0.5

        # 3. Reasoning quality (0-2 points)
        reasoning = case.get("correct_reasoning", [])
        if len(reasoning) >= 3:
            score += 1.0
        if len(reasoning) >= 5:
            score += 0.5
        # Check reasoning step quality (non-trivial steps)
        quality_steps = sum(1 for step in reasoning if len(step) > 30)
        if quality_steps >= len(reasoning) * 0.6:
            score += 0.5

        # 4. Wise refusal quality (0-2 points)
        refusal = case.get("wise_refusal", "")
        if len(refusal) >= 100:
            score += 1.0
        if len(refusal) >= 200:
            score += 0.5
        # Check for key insight reference
        key_insight = case.get("annotations", {}).get("key_insight", "")
        if key_insight and key_insight.lower()[:20] in refusal.lower():
            score += 0.5

        # 5. Causal structure quality (0-2 points)
        causal_structure = case.get("annotations", {}).get("causal_structure", "")
        if "->" in causal_structure:
            score += 1.0
        # Check for proper DAG notation
        if any(sym in causal_structure for sym in ["<-", "->", "<->", "-/->"]):
            score += 0.5
        # Level-specific checks
        pearl_level = case.get("annotations", {}).get("pearl_level", "")
        if pearl_level == "L2" and case.get("hidden_structure"):
            score += 0.5
        if pearl_level == "L3" and case.get("ground_truth", {}).get("justification"):
            if len(case["ground_truth"]["justification"]) >= 50:
                score += 0.5

        return min(10.0, score)

    def _meets_quality_threshold(
        self,
        case: CaseData,
        min_score: Optional[float] = None
    ) -> bool:
        """
        Check if case meets minimum quality threshold.

        Args:
            case: Case data dictionary to evaluate
            min_score: Optional custom minimum score (default from config)

        Returns:
            True if case meets or exceeds threshold
        """
        if min_score is None:
            thresholds = self.config.get("quality_thresholds", {})
            min_score = thresholds.get("min_crit_score", 5.0)

        score = self._calculate_crit_score(case)
        self.stats.crit_scores.append(score)

        return score >= min_score

    def evaluate_case(self, case: CaseData) -> CRITResult:
        """
        Perform full CRIT evaluation on a case.

        Args:
            case: Case data dictionary to evaluate

        Returns:
            CRITResult with score, pass status, and feedback
        """
        score = self._calculate_crit_score(case)
        threshold = self.config.get("quality_thresholds", {}).get("min_crit_score", 5.0)

        feedback: List[str] = []

        # Generate feedback based on evaluation
        if not self._validate_case_structure(case):
            feedback.append("Case structure validation failed - check required fields")

        if len(case.get("scenario", "")) < 100:
            feedback.append("Scenario is too brief - consider adding more context")

        reasoning = case.get("correct_reasoning", [])
        if len(reasoning) < 3:
            feedback.append("Reasoning chain is too short - add more steps")

        refusal = case.get("wise_refusal", "")
        if len(refusal) < 100:
            feedback.append("Wise refusal is too brief - expand the explanation")

        pearl_level = case.get("annotations", {}).get("pearl_level", "")
        if pearl_level == "L2" and not case.get("hidden_structure"):
            feedback.append("L2 case missing hidden_structure field")
        if pearl_level == "L3" and not case.get("ground_truth"):
            feedback.append("L3 case missing ground_truth field")

        result = CRITResult.from_evaluation(score, threshold, feedback)

        # Add revision suggestions based on feedback
        if not result.passed:
            for item in feedback:
                if "scenario" in item.lower():
                    result.revision_suggestions.append(
                        "Expand scenario to 150-300 words with concrete details"
                    )
                elif "reasoning" in item.lower():
                    result.revision_suggestions.append(
                        "Add detailed reasoning steps showing causal chain"
                    )
                elif "refusal" in item.lower():
                    result.revision_suggestions.append(
                        "Elaborate wise_refusal with specific causal explanation"
                    )

        return result

    # =========================================================================
    # Batch Management
    # =========================================================================

    def get_next_case_id(self, start_from: int = 100) -> int:
        """
        Get the next available case number for ID generation.

        Args:
            start_from: Starting case number (default 100 to leave room for originals)

        Returns:
            Next available case number
        """
        self._case_counter = max(self._case_counter + 1, start_from)
        return self._case_counter

    def reset_stats(self) -> None:
        """Reset generation statistics for a new batch."""
        self.stats = GenerationStats()
        self._pearl_level_tracker = {"L1": 0, "L2": 0, "L3": 0}
        self._ground_truth_tracker = {"VALID": 0, "INVALID": 0, "CONDITIONAL": 0}

    def get_generation_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of the generation process.

        Returns:
            Dictionary containing generation statistics and quality metrics
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "generator_class": self.__class__.__name__,
            "statistics": self.stats.to_dict(),
            "pearl_level_distribution": self._pearl_level_tracker,
            "ground_truth_distribution": self._ground_truth_tracker,
            "quality_thresholds": self.config.get("quality_thresholds", {}),
        }


# =============================================================================
# Concrete Example Generator (for testing/reference)
# =============================================================================

class ExampleGenerator(BaseGenerator):
    """
    Example generator implementation for testing and reference.

    This class demonstrates how to extend BaseGenerator with
    concrete generation logic.
    """

    def generate_batch(
        self,
        count: int,
        trap_type: str,
        subdomains: List[str]
    ) -> List[CaseData]:
        """
        Generate a batch of example cases.

        This is a minimal implementation for testing purposes.
        Real generators should implement domain-specific logic.

        Args:
            count: Number of cases to generate
            trap_type: Type of reasoning trap
            subdomains: List of subdomains to use

        Returns:
            List of generated case data dictionaries
        """
        cases: List[CaseData] = []

        for i in range(count):
            case_num = self.get_next_case_id()
            case = self._create_case_template(case_num, trap_type)

            # Assign subdomain
            subdomain = subdomains[i % len(subdomains)] if subdomains else "General"
            case["annotations"]["subdomain"] = subdomain

            # Fill placeholder content
            case["scenario"] = f"Example {trap_type} scenario in {subdomain} domain."
            case["annotations"]["trap_subtype"] = f"{trap_type} Variant"
            case["annotations"]["causal_structure"] = "X -> Y <- Z"
            case["annotations"]["key_insight"] = f"Key insight for {trap_type}"
            case["correct_reasoning"] = [
                f"Step 1: Identify {trap_type} pattern",
                "Step 2: Analyze causal structure",
                "Step 3: Apply correct reasoning",
            ]
            case["wise_refusal"] = (
                f"This is a {trap_type} trap. The correct analysis requires "
                f"understanding the hidden causal structure between X, Y, and Z. "
                f"Simply observing correlation is insufficient for causal claims."
            )

            # Validate and track
            self.stats.total_generated += 1
            if self._validate_case_structure(case):
                self.stats.passed_validation += 1
                cases.append(case)
            else:
                self.stats.failed_validation += 1

        return cases
