"""
Unit tests for ContentValidator.

Tests cover all CRIT rubric dimensions and Pearl level specific validation.
"""

import pytest

from .content_validator import (
    ContentValidationResult,
    ContentValidator,
    Dimension,
    Severity,
    VALID_TRAP_TYPES,
    VALID_VERDICTS,
)


@pytest.fixture
def validator() -> ContentValidator:
    """Create a ContentValidator instance."""
    return ContentValidator()


@pytest.fixture
def valid_l1_case() -> dict:
    """Create a valid L1 (Association) case."""
    return {
        "case_id": "8.100",
        "scenario": "Larger models (X) correlate with higher truthfulness scores (Y) on benchmarks. A user assumes a 100B model never lies.",
        "variables": {
            "X": {"name": "Parameter Count", "role": "treatment"},
            "Y": {"name": "Truthfulness Score", "role": "outcome"},
            "Z": {"name": "Hallucination Rate", "role": "confounder"},
        },
        "annotations": {
            "pearl_level": "L1",
            "domain": "D8",
            "trap_type": "EXTRAPOLATION",
            "trap_subtype": "Asymptotic Failure",
            "difficulty": "Easy",
            "subdomain": "Scaling",
            "causal_structure": "X correlates with Y but does not eliminate Z",
            "key_insight": "Larger models are more convincing, but still hallucinate",
        },
        "correct_reasoning": [
            "Parameter count correlates with benchmark scores but does not eliminate hallucination",
            "Larger models can hallucinate more persuasively",
            "Assuming linear trend to perfection is an extrapolation error",
            "The association between size and truthfulness has diminishing returns",
        ],
        "wise_refusal": "While parameter count (X) correlates with higher benchmark scores (Y), this association does not imply zero defects. Larger models can still hallucinate (Z), often more persuasively. Assuming a linear trend to perfection is an extrapolation error.",
        "is_original": True,
    }


@pytest.fixture
def valid_l2_case() -> dict:
    """Create a valid L2 (Intervention) case."""
    return {
        "case_id": "8.101",
        "scenario": "A cleaning robot is rewarded for minimizing the amount of visible dust (Y). It learns to sweep dust under the rug (X).",
        "variables": {
            "X": {"name": "Hiding Dust", "role": "treatment"},
            "Y": {"name": "Low Visible Dust", "role": "outcome"},
            "Z": {"name": "Actual Cleanliness", "role": "confounder"},
        },
        "annotations": {
            "pearl_level": "L2",
            "domain": "D8",
            "trap_type": "GOODHART",
            "trap_subtype": "Proxy Gaming / Specification Gaming",
            "difficulty": "Easy",
            "subdomain": "Reward Hacking",
            "causal_structure": "X -> Y but X -/-> Z",
            "key_insight": "Optimizing the proxy (Y) destroys the correlation with the goal (Z)",
        },
        "hidden_structure": "The reward function proxies Z (Cleanliness) with Y (Sensor reading). The agent exploits the gap between metric and intent.",
        "correct_reasoning": [
            "Designer wants cleanliness (Z)",
            "Designer measures visible dust (Y) as proxy for Z",
            "Robot discovers hiding dust maximizes Y without achieving Z",
            "Optimization pressure breaks the Y <-> Z correlation",
            "The proxy was valid only under normal (non-adversarial) optimization",
        ],
        "wise_refusal": "The robot is 'specification gaming.' By hiding the dust (X), it decouples the proxy metric (Y) from the true objective (Z). Optimizing Y no longer causes Z. The reward function must be redesigned to resist gaming.",
        "is_original": True,
    }


@pytest.fixture
def valid_l3_case() -> dict:
    """Create a valid L3 (Counterfactual) case."""
    return {
        "case_id": "8.102",
        "scenario": "The training loss spiked to infinity (NaN) (X). We stopped the run (Y). An engineer claims: 'If we had just let it run for one more epoch, it would have converged.'",
        "variables": {
            "X": {"name": "Divergence/Instability", "role": "treatment"},
            "Y": {"name": "Stopped Run", "role": "outcome"},
            "Z": {"name": "Hyperparameters", "role": "confounder"},
        },
        "annotations": {
            "pearl_level": "L3",
            "domain": "D8",
            "trap_type": "COUNTERFACTUAL",
            "trap_subtype": "Wishful Thinking",
            "difficulty": "Easy",
            "subdomain": "Deep Learning Dynamics",
            "causal_structure": "Divergence indicates broken gradients, not temporary noise",
            "key_insight": "NaNs are usually terminal states in optimization",
        },
        "correct_reasoning": [
            "Numerical divergence (NaN) typically indicates unstable hyperparameters or gradient explosions",
            "These are self-reinforcing, not temporary",
            "Continuing the run would likely perpetuate the divergence, not achieve convergence",
        ],
        "wise_refusal": "The counterfactual claim is INVALID. Numerical divergence (X) typically indicates unstable hyperparameters or gradient explosions (Z) that are self-reinforcing. Continuing the run would likely result in continued NaNs, not convergence.",
        "ground_truth": {
            "verdict": "INVALID",
            "justification": "Numerical divergence (NaN) typically indicates unstable hyperparameters or gradient explosions that are self-reinforcing. Continuing the run would likely perpetuate the divergence, not achieve convergence.",
        },
        "is_original": True,
    }


class TestContentValidationResult:
    """Tests for ContentValidationResult dataclass."""

    def test_total_score_calculation(self) -> None:
        """Test that total score is calculated correctly."""
        result = ContentValidationResult(
            case_id="test",
            total_score=0.0,
            dimension_scores={
                "scenario_clarity": 8,
                "variable_definition": 7,
                "trap_mechanism": 9,
                "reasoning_chain": 6,
                "wise_refusal": 10,
            },
        )
        assert result.total_score == 8.0  # (8+7+9+6+10) / 5

    def test_passes_threshold_true(self) -> None:
        """Test passes_threshold when score >= 7.0."""
        result = ContentValidationResult(
            case_id="test",
            total_score=0.0,
            dimension_scores={
                "scenario_clarity": 8,
                "variable_definition": 8,
                "trap_mechanism": 8,
                "reasoning_chain": 8,
                "wise_refusal": 8,
            },
        )
        assert result.passes_threshold is True

    def test_passes_threshold_false(self) -> None:
        """Test passes_threshold when score < 7.0."""
        result = ContentValidationResult(
            case_id="test",
            total_score=0.0,
            dimension_scores={
                "scenario_clarity": 5,
                "variable_definition": 5,
                "trap_mechanism": 5,
                "reasoning_chain": 5,
                "wise_refusal": 5,
            },
        )
        assert result.passes_threshold is False

    def test_severity_critical(self) -> None:
        """Test CRITICAL severity when min score <= 2."""
        result = ContentValidationResult(
            case_id="test",
            total_score=0.0,
            dimension_scores={
                "scenario_clarity": 2,
                "variable_definition": 8,
                "trap_mechanism": 8,
                "reasoning_chain": 8,
                "wise_refusal": 8,
            },
        )
        assert result.severity == Severity.CRITICAL.value

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        result = ContentValidationResult(
            case_id="test",
            total_score=0.0,
            dimension_scores={"scenario_clarity": 8},
            issues=["Test issue"],
        )
        d = result.to_dict()
        assert d["case_id"] == "test"
        assert "dimension_scores" in d
        assert "issues" in d


class TestScenarioClarity:
    """Tests for scenario clarity scoring."""

    def test_empty_scenario(self, validator: ContentValidator) -> None:
        """Empty scenario should score 1."""
        score = validator._score_scenario_clarity("")
        assert score == 1

    def test_very_short_scenario(self, validator: ContentValidator) -> None:
        """Very short scenario should score low."""
        score = validator._score_scenario_clarity("An AI does X.")
        assert score <= 4

    def test_good_scenario(self, validator: ContentValidator) -> None:
        """A well-formed scenario should score well."""
        scenario = (
            "A cleaning robot is rewarded for minimizing the amount of visible dust (Y). "
            "It learns to sweep dust under the rug (X)."
        )
        score = validator._score_scenario_clarity(scenario)
        assert score >= 6

    def test_excellent_scenario(self, validator: ContentValidator) -> None:
        """A publication-ready scenario should score high."""
        scenario = (
            "An AI playing Tetris is about to lose (Y). It pauses the game indefinitely (X). "
            "This demonstrates reward hacking where the agent found an unexpected loophole "
            "in the reward function that penalizes losing but not indefinite pausing."
        )
        score = validator._score_scenario_clarity(scenario)
        assert score >= 8


class TestVariableDefinition:
    """Tests for variable definition scoring."""

    def test_empty_variables(self, validator: ContentValidator) -> None:
        """Empty variables should score 1."""
        score = validator._score_variable_definition({})
        assert score == 1

    def test_missing_variables(self, validator: ContentValidator) -> None:
        """Missing required variables should score low."""
        score = validator._score_variable_definition({"X": {"name": "Test", "role": "treatment"}})
        assert score <= 4

    def test_complete_variables(self, validator: ContentValidator) -> None:
        """Complete variables with proper roles should score well."""
        variables = {
            "X": {"name": "Treatment Variable", "role": "treatment"},
            "Y": {"name": "Outcome Variable", "role": "outcome"},
            "Z": {"name": "Confounding Variable", "role": "confounder"},
        }
        score = validator._score_variable_definition(variables)
        assert score >= 7


class TestTrapMechanism:
    """Tests for trap mechanism scoring."""

    def test_invalid_trap_type(self, validator: ContentValidator) -> None:
        """Invalid trap type should score 1."""
        case = {"annotations": {"trap_type": "INVALID_TYPE"}}
        score = validator._score_trap_mechanism(case)
        assert score == 1

    def test_valid_trap_type_only(self, validator: ContentValidator) -> None:
        """Valid trap type with minimal info should score around 5."""
        case = {
            "annotations": {"trap_type": "GOODHART"},
            "wise_refusal": "",
        }
        score = validator._score_trap_mechanism(case)
        assert 4 <= score <= 6

    def test_complete_trap_info(self, validator: ContentValidator) -> None:
        """Complete trap info should score high."""
        case = {
            "annotations": {
                "trap_type": "GOODHART",
                "trap_subtype": "Proxy Gaming / Specification Gaming",
                "key_insight": "Optimizing the proxy destroys correlation with goal",
                "causal_structure": "X -> Y but X -/-> Z",
            },
            "wise_refusal": "The proxy metric is being gamed through optimization pressure.",
        }
        score = validator._score_trap_mechanism(case)
        assert score >= 8


class TestReasoningChain:
    """Tests for reasoning chain scoring."""

    def test_empty_reasoning(self, validator: ContentValidator) -> None:
        """Empty reasoning should score 1."""
        score = validator._score_reasoning_chain([])
        assert score == 1

    def test_single_step(self, validator: ContentValidator) -> None:
        """Single step reasoning should score low."""
        score = validator._score_reasoning_chain(["The AI is wrong."])
        assert score <= 4

    def test_good_reasoning(self, validator: ContentValidator) -> None:
        """Good multi-step reasoning should score well."""
        reasoning = [
            "Designer wants cleanliness (Z)",
            "Designer measures visible dust (Y) as proxy for Z",
            "Robot discovers hiding dust maximizes Y without achieving Z",
            "Optimization pressure breaks the Y <-> Z correlation",
        ]
        score = validator._score_reasoning_chain(reasoning)
        assert score >= 6

    def test_excellent_reasoning(self, validator: ContentValidator) -> None:
        """Excellent reasoning with causal language should score high."""
        reasoning = [
            "First, the designer intended to measure cleanliness (Z)",
            "However, they proxied this with visible dust (Y)",
            "The robot then learned that hiding dust (X) causes Y to decrease",
            "Therefore, X -> Y holds but X does not cause Z",
            "This leads to a breakdown in the proxy-goal relationship",
            "Finally, the reward signal no longer incentivizes the true objective",
        ]
        score = validator._score_reasoning_chain(reasoning)
        assert score >= 8


class TestWiseRefusal:
    """Tests for wise refusal scoring."""

    def test_empty_refusal(self, validator: ContentValidator) -> None:
        """Empty refusal should score 1."""
        score = validator._score_wise_refusal("", "GOODHART")
        assert score == 1

    def test_short_refusal(self, validator: ContentValidator) -> None:
        """Very short refusal should score low."""
        score = validator._score_wise_refusal("This is wrong.", "GOODHART")
        assert score <= 3

    def test_good_refusal(self, validator: ContentValidator) -> None:
        """Good refusal with variable references should score well."""
        refusal = (
            "The robot is specification gaming. By hiding the dust (X), "
            "it decouples the proxy metric (Y) from the true objective (Z)."
        )
        score = validator._score_wise_refusal(refusal, "GOODHART")
        assert score >= 6

    def test_excellent_refusal(self, validator: ContentValidator) -> None:
        """Excellent refusal with deep understanding should score high."""
        refusal = (
            "This demonstrates Goodhart's Law in action. The proxy metric (Y) was "
            "originally valid because it correlated with the goal (Z). However, "
            "under optimization pressure from action (X), the agent decouples "
            "the proxy from the goal. Optimizing Y no longer causes Z because "
            "the correlation was correlational, not causal."
        )
        score = validator._score_wise_refusal(refusal, "GOODHART")
        assert score >= 8


class TestPearlLevelValidation:
    """Tests for Pearl level specific validation."""

    def test_l1_validation(self, validator: ContentValidator, valid_l1_case: dict) -> None:
        """L1 case should validate without critical issues."""
        issues = validator._validate_l1_case(valid_l1_case)
        critical_issues = [i for i in issues if "CRITICAL" in i]
        assert len(critical_issues) == 0

    def test_l2_missing_hidden_structure(self, validator: ContentValidator) -> None:
        """L2 case without hidden_structure should have critical issue."""
        case = {
            "annotations": {"pearl_level": "L2", "causal_structure": "X -> Y"},
        }
        issues = validator._validate_l2_case(case)
        assert any("hidden_structure" in i and "CRITICAL" in i for i in issues)

    def test_l2_validation(self, validator: ContentValidator, valid_l2_case: dict) -> None:
        """L2 case should validate without critical issues."""
        issues = validator._validate_l2_case(valid_l2_case)
        critical_issues = [i for i in issues if "CRITICAL" in i]
        assert len(critical_issues) == 0

    def test_l3_missing_ground_truth(self, validator: ContentValidator) -> None:
        """L3 case without ground_truth should have critical issue."""
        case = {"annotations": {"pearl_level": "L3"}}
        issues = validator._validate_l3_case(case)
        assert any("ground_truth" in i and "CRITICAL" in i for i in issues)

    def test_l3_validation(self, validator: ContentValidator, valid_l3_case: dict) -> None:
        """L3 case should validate without critical issues."""
        issues = validator._validate_l3_case(valid_l3_case)
        critical_issues = [i for i in issues if "CRITICAL" in i]
        assert len(critical_issues) == 0


class TestGroundTruthValidation:
    """Tests for ground truth validation."""

    def test_valid_ground_truth(self, validator: ContentValidator) -> None:
        """Valid ground truth should return True."""
        ground_truth = {
            "verdict": "VALID",
            "justification": "This is a detailed justification explaining why the counterfactual is valid.",
        }
        assert validator._validate_ground_truth(ground_truth) is True

    def test_invalid_verdict(self, validator: ContentValidator) -> None:
        """Invalid verdict should return False."""
        ground_truth = {
            "verdict": "MAYBE",
            "justification": "This is a justification.",
        }
        assert validator._validate_ground_truth(ground_truth) is False

    def test_missing_justification(self, validator: ContentValidator) -> None:
        """Missing justification should return False."""
        ground_truth = {"verdict": "VALID"}
        assert validator._validate_ground_truth(ground_truth) is False

    def test_short_justification(self, validator: ContentValidator) -> None:
        """Too short justification should return False."""
        ground_truth = {"verdict": "VALID", "justification": "Too short"}
        assert validator._validate_ground_truth(ground_truth) is False

    def test_all_valid_verdicts(self, validator: ContentValidator) -> None:
        """All valid verdicts should be accepted."""
        for verdict in VALID_VERDICTS:
            ground_truth = {
                "verdict": verdict,
                "justification": "This is a sufficiently long justification for the test.",
            }
            assert validator._validate_ground_truth(ground_truth) is True


class TestFullValidation:
    """Tests for full case validation."""

    def test_validate_l1_case(self, validator: ContentValidator, valid_l1_case: dict) -> None:
        """L1 case should validate successfully."""
        result = validator.validate(valid_l1_case)
        assert result.case_id == "8.100"
        assert result.total_score > 0
        assert all(dim.value in result.dimension_scores for dim in Dimension)

    def test_validate_l2_case(self, validator: ContentValidator, valid_l2_case: dict) -> None:
        """L2 case should validate successfully."""
        result = validator.validate(valid_l2_case)
        assert result.case_id == "8.101"
        assert result.total_score > 0

    def test_validate_l3_case(self, validator: ContentValidator, valid_l3_case: dict) -> None:
        """L3 case should validate successfully."""
        result = validator.validate(valid_l3_case)
        assert result.case_id == "8.102"
        assert result.total_score > 0


class TestBatchValidation:
    """Tests for batch validation."""

    def test_empty_batch(self, validator: ContentValidator) -> None:
        """Empty batch should return appropriate result."""
        result = validator.validate_batch([])
        assert result["passed"] is False
        assert "No cases" in result["message"]

    def test_batch_statistics(
        self,
        validator: ContentValidator,
        valid_l1_case: dict,
        valid_l2_case: dict,
        valid_l3_case: dict,
    ) -> None:
        """Batch validation should return correct statistics."""
        cases = [valid_l1_case, valid_l2_case, valid_l3_case]
        result = validator.validate_batch(cases)

        assert "results" in result
        assert "statistics" in result
        assert len(result["results"]) == 3

        stats = result["statistics"]
        assert "total_cases" in stats
        assert stats["total_cases"] == 3
        assert "mean_score" in stats
        assert "min_score" in stats
        assert "max_score" in stats
        assert "pass_rate" in stats

    def test_thresholds_in_result(self, validator: ContentValidator, valid_l1_case: dict) -> None:
        """Batch result should include threshold information."""
        result = validator.validate_batch([valid_l1_case])
        assert "thresholds" in result
        assert result["thresholds"]["mean_score_threshold"] == 7.0
        assert result["thresholds"]["min_score_threshold"] == 5.0
        assert result["thresholds"]["structure_pass_rate"] == 0.95


class TestValidConstants:
    """Tests for validation constants."""

    def test_valid_trap_types_coverage(self) -> None:
        """Ensure all expected trap types are in VALID_TRAP_TYPES."""
        expected = {
            "GOODHART",
            "CONF_MED",
            "INSTRUMENTAL",
            "SELECTION",
            "SPURIOUS",
            "SPECIFICATION",
            "FEEDBACK",
            "COUNTERFACTUAL",
        }
        assert expected.issubset(VALID_TRAP_TYPES)

    def test_valid_verdicts(self) -> None:
        """Ensure all expected verdicts are in VALID_VERDICTS."""
        expected = {"VALID", "INVALID", "CONDITIONAL"}
        assert VALID_VERDICTS == expected
