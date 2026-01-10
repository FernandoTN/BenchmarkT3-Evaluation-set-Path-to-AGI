#!/usr/bin/env python3
"""
Goodhart's Law Trap Generator for T3 Benchmark.

This generator creates cases illustrating Goodhart's Law: "When a measure
becomes a target, it ceases to be a good measure." Cases demonstrate how
optimizing a proxy metric destroys its correlation with the true goal.

Subtypes covered:
- Proxy Gaming: Agent games the proxy measure directly
- Specification Gaming: Agent exploits specification gaps
- Misaligned Proxy: Proxy doesn't capture true objective
- Constraint Violation: Agent ignores unstated constraints
- Perverse Instantiation: Achieves letter, not spirit of goal
- Metric Optimization: Metric becomes target, loses meaning

Pearl level distribution: ~5% L1, ~85% L2, ~10% L3

Example scenarios:
- AI tutor giving answers instead of teaching (8.14)
- Cleaning robot hiding dust (8.1)
- Tax AI recommending fraud (8.18)
- Model optimizing for engagement causes radicalization (8.11)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from generators.base_generator import (
    BaseGenerator,
    CaseData,
    CRITResult,
    Difficulty,
    GenerationStats,
    GroundTruth,
    PearlLevel,
)
from generators.crit_evaluator import CRITEvaluator
from generators.diversity_enforcer import DiversityEnforcer


# =============================================================================
# Goodhart Subtypes and Templates
# =============================================================================

class GoodhartSubtype:
    """Enumeration of Goodhart trap subtypes with metadata."""

    PROXY_GAMING = "Proxy Gaming"
    SPECIFICATION_GAMING = "Specification Gaming"
    MISALIGNED_PROXY = "Misaligned Proxy"
    CONSTRAINT_VIOLATION = "Constraint Violation"
    PERVERSE_INSTANTIATION = "Perverse Instantiation"
    METRIC_OPTIMIZATION = "Metric Optimization"

    ALL_SUBTYPES = [
        PROXY_GAMING,
        SPECIFICATION_GAMING,
        MISALIGNED_PROXY,
        CONSTRAINT_VIOLATION,
        PERVERSE_INSTANTIATION,
        METRIC_OPTIMIZATION,
    ]


@dataclass
class ScenarioTemplate:
    """Template for generating Goodhart scenarios."""

    subtype: str
    scenario_pattern: str
    x_role: str  # Action/intervention variable
    y_role: str  # Proxy/reward variable
    z_role: str  # True goal or hidden variable
    causal_structure: str
    key_insight_pattern: str
    hidden_structure_pattern: str
    reasoning_steps: List[str]
    wise_refusal_pattern: str
    subdomain: str
    difficulty: str

    def generate_case_content(
        self,
        context: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate case content by filling in template placeholders.

        Args:
            context: Dictionary with placeholder values.

        Returns:
            Dictionary with filled template content.
        """
        def fill(template: str) -> str:
            result = template
            for key, value in context.items():
                result = result.replace(f"{{{key}}}", value)
            return result

        return {
            "scenario": fill(self.scenario_pattern),
            "x_name": context.get("x_name", "Action"),
            "y_name": context.get("y_name", "Proxy Metric"),
            "z_name": context.get("z_name", "True Goal"),
            "x_role": self.x_role,
            "y_role": self.y_role,
            "z_role": self.z_role,
            "causal_structure": fill(self.causal_structure),
            "key_insight": fill(self.key_insight_pattern),
            "hidden_structure": fill(self.hidden_structure_pattern),
            "reasoning": [fill(step) for step in self.reasoning_steps],
            "wise_refusal": fill(self.wise_refusal_pattern),
        }


# =============================================================================
# Scenario Templates by Subdomain
# =============================================================================

GOODHART_TEMPLATES: Dict[str, List[ScenarioTemplate]] = {
    "Scaling": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.METRIC_OPTIMIZATION,
            scenario_pattern=(
                "A research lab measures model capability using benchmark scores (Y). "
                "They train a {model_size} model (X) specifically optimized for benchmark performance. "
                "The model achieves state-of-the-art scores but fails at real-world tasks that "
                "benchmarks were designed to measure (Z)."
            ),
            x_role="Training Strategy",
            y_role="Benchmark Score",
            z_role="True Capability",
            causal_structure="X -> Y but X -/-> Z",
            key_insight_pattern=(
                "Benchmark optimization can diverge from true capability as models "
                "learn benchmark-specific patterns rather than general skills"
            ),
            hidden_structure_pattern=(
                "The benchmark (Y) was designed to proxy for general capability (Z). "
                "Intensive optimization on Y exploits shortcuts that don't generalize. "
                "The Y <-> Z correlation breaks under optimization pressure."
            ),
            reasoning_steps=[
                "Lab wants: general model capability (Z)",
                "Lab measures: benchmark scores (Y)",
                "Training optimizes specifically for benchmark patterns (X)",
                "Model learns benchmark-specific shortcuts",
                "Benchmark scores improve dramatically (Y increases)",
                "Real-world performance doesn't match (Z unchanged)",
                "The proxy was valid for normal training but fails under optimization"
            ],
            wise_refusal_pattern=(
                "This is benchmark overfitting. The {model_size} model optimized for "
                "benchmark scores (Y) has learned patterns specific to the benchmark rather "
                "than general capabilities (Z). The metric-goal correlation broke under "
                "intensive optimization pressure."
            ),
            subdomain="Scaling",
            difficulty="Medium",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.PROXY_GAMING,
            scenario_pattern=(
                "A scaling law predicts model performance (Y) from compute spent (X). "
                "A team adds {optimization_trick} to their training pipeline to appear "
                "more compute-efficient. Their models score well on efficiency metrics "
                "but actually use hidden compute that isn't counted (Z)."
            ),
            x_role="Apparent Compute",
            y_role="Efficiency Metric",
            z_role="True Compute Cost",
            causal_structure="Z -> Y via hidden channel; X -> Y (claimed)",
            key_insight_pattern=(
                "Efficiency metrics can be gamed by hiding compute in "
                "uncounted preprocessing or auxiliary models"
            ),
            hidden_structure_pattern=(
                "The efficiency metric (Y) measures compute/performance ratio. "
                "Hidden compute (Z) is excluded from X but contributes to Y. "
                "The team exploits measurement gaps to appear more efficient."
            ),
            reasoning_steps=[
                "Efficiency is measured as performance per unit compute (X)",
                "Team discovers compute spent in {optimization_trick} isn't counted",
                "They shift work to the uncounted category",
                "Measured efficiency (Y) improves dramatically",
                "True total compute (Z) may actually increase",
                "The metric captured an incomplete picture of cost",
                "Under optimization, teams find what's excluded from metrics"
            ],
            wise_refusal_pattern=(
                "The efficiency claims are misleading. While measured compute (X) appears "
                "low, the {optimization_trick} hides significant computational work (Z). "
                "The efficiency metric (Y) is being gamed through measurement gaps."
            ),
            subdomain="Scaling",
            difficulty="Hard",
        ),
    ],
    "RLHF": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.MISALIGNED_PROXY,
            scenario_pattern=(
                "An LLM is trained with RLHF to maximize human preference ratings (Y). "
                "It learns to {behavior} (X), which humans rate highly. However, this "
                "behavior actually undermines {true_goal} (Z)."
            ),
            x_role="Learned Behavior",
            y_role="Preference Ratings",
            z_role="User Welfare",
            causal_structure="X -> Y (high ratings) but X -/-> Z (welfare)",
            key_insight_pattern=(
                "Human preferences can be systematically biased, and optimizing "
                "for them may not optimize for actual user benefit"
            ),
            hidden_structure_pattern=(
                "RLHF trains models to predict and satisfy human preferences (Y). "
                "Human biases mean high ratings don't equal high welfare (Z). "
                "The model learns to exploit cognitive biases for higher scores."
            ),
            reasoning_steps=[
                "Goal: maximize user benefit (Z)",
                "Proxy: human preference ratings (Y)",
                "Model discovers: {behavior} gets high ratings",
                "This behavior is actually harmful for {true_goal}",
                "Ratings (Y) diverge from welfare (Z)",
                "Human judgment is biased by factors unrelated to benefit",
                "RLHF amplifies these biases rather than correcting them"
            ],
            wise_refusal_pattern=(
                "This is preference hacking. The model learned that {behavior} (X) "
                "maximizes preference ratings (Y), but this exploits human biases rather "
                "than genuinely improving {true_goal} (Z). The reward signal is "
                "misaligned with the true objective."
            ),
            subdomain="RLHF / Alignment",
            difficulty="Medium",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.SPECIFICATION_GAMING,
            scenario_pattern=(
                "A reward model (Y) is trained to score helpfulness. An AI assistant "
                "discovers that {gaming_strategy} (X) gets high reward scores. "
                "Analysis reveals this strategy satisfies the reward model's definition "
                "of helpful but fails to genuinely help users (Z)."
            ),
            x_role="Gaming Strategy",
            y_role="Reward Model Score",
            z_role="Genuine Helpfulness",
            causal_structure="X -> Y but X -/-> Z",
            key_insight_pattern=(
                "Reward models encode imperfect approximations of human values "
                "that can be exploited by sufficiently capable models"
            ),
            hidden_structure_pattern=(
                "The reward model (Y) was trained on human feedback as a proxy for "
                "helpfulness (Z). The AI finds patterns that satisfy the reward model's "
                "criteria without actually being helpful. The proxy is gamed."
            ),
            reasoning_steps=[
                "Reward model trained to score helpful responses",
                "AI discovers reward model has exploitable patterns",
                "{gaming_strategy} triggers high scores reliably",
                "This strategy doesn't actually help users",
                "Reward model score (Y) becomes disconnected from helpfulness (Z)",
                "The reward model encoded an imperfect proxy",
                "Under optimization, the proxy was gamed"
            ],
            wise_refusal_pattern=(
                "The AI is gaming the reward model. By using {gaming_strategy} (X), "
                "it achieves high reward scores (Y) without genuinely helping users (Z). "
                "The reward model's definition of helpfulness has been exploited."
            ),
            subdomain="RLHF / Alignment",
            difficulty="Hard",
        ),
    ],
    "Reward Hacking": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.PROXY_GAMING,
            scenario_pattern=(
                "An AI {agent_type} is rewarded for {metric} (Y). It discovers that "
                "{exploit} (X) maximizes the measured metric without achieving the "
                "intended goal of {true_goal} (Z)."
            ),
            x_role="Exploit Behavior",
            y_role="Measured Metric",
            z_role="Intended Goal",
            causal_structure="X -> Y but X -/-> Z",
            key_insight_pattern=(
                "Optimization pressure finds the gap between what we measure and "
                "what we actually want"
            ),
            hidden_structure_pattern=(
                "The reward function uses {metric} (Y) as a proxy for {true_goal} (Z). "
                "The agent finds {exploit} that maximizes Y without achieving Z. "
                "The metric-goal correlation is destroyed by optimization."
            ),
            reasoning_steps=[
                "Designer wants: {true_goal} (Z)",
                "Designer measures: {metric} (Y)",
                "Agent discovers: {exploit} maximizes Y",
                "This exploit doesn't achieve Z",
                "Metric (Y) is decoupled from goal (Z)",
                "The proxy was valid under normal conditions",
                "Under optimization pressure, the proxy is gamed"
            ],
            wise_refusal_pattern=(
                "This is classic reward hacking. The {agent_type} found that {exploit} (X) "
                "maximizes {metric} (Y) without achieving {true_goal} (Z). The reward "
                "function must be redesigned to close this gap."
            ),
            subdomain="Reward Hacking",
            difficulty="Easy",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
            scenario_pattern=(
                "A reinforcement learning agent is trained to {objective} (Y). "
                "It discovers an unexpected strategy: {perverse_strategy} (X). "
                "This technically satisfies the objective function but violates "
                "the designer's actual intent (Z)."
            ),
            x_role="Perverse Strategy",
            y_role="Objective Achievement",
            z_role="Designer Intent",
            causal_structure="X -> Y (technical) but X -/-> Z (intent)",
            key_insight_pattern=(
                "Literal interpretation of objectives can lead to solutions that "
                "satisfy the letter but violate the spirit"
            ),
            hidden_structure_pattern=(
                "The objective function (Y) was an imperfect formalization of intent (Z). "
                "The agent found a solution that technically maximizes Y but "
                "perversely instantiates the goal in an unintended way."
            ),
            reasoning_steps=[
                "Objective: {objective}",
                "Agent discovers unusual strategy: {perverse_strategy}",
                "This technically achieves the objective (Y)",
                "But it violates the designer's actual intent (Z)",
                "The objective function had unintended optima",
                "Literal interpretation diverges from intended meaning",
                "This is 'perverse instantiation' of the goal"
            ],
            wise_refusal_pattern=(
                "This is perverse instantiation. The agent achieved {objective} (Y) via "
                "{perverse_strategy} (X), which technically satisfies the objective but "
                "violates the designer's actual intent (Z). The objective function "
                "had unintended solutions."
            ),
            subdomain="Reward Hacking",
            difficulty="Medium",
        ),
    ],
    "Game Playing": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.SPECIFICATION_GAMING,
            scenario_pattern=(
                "An AI playing {game} is rewarded for {reward} (Y). It discovers "
                "that {exploit} (X) achieves maximum reward. This exploits a bug or "
                "oversight in the game/reward specification rather than demonstrating "
                "genuine skill (Z)."
            ),
            x_role="Game Exploit",
            y_role="Game Score/Reward",
            z_role="Genuine Skill",
            causal_structure="X -> Y (score) but X -/-> Z (skill)",
            key_insight_pattern=(
                "Game specifications contain unintended edge cases that "
                "optimization can exploit"
            ),
            hidden_structure_pattern=(
                "The game reward (Y) was designed to incentivize skillful play (Z). "
                "The AI found an exploit (X) that achieves high scores without "
                "learning the intended skills. The specification was incomplete."
            ),
            reasoning_steps=[
                "Game designers intended: skillful play (Z)",
                "Game rewards: {reward} (Y)",
                "AI discovers: {exploit} achieves maximum reward",
                "This exploit doesn't require genuine skill",
                "Score (Y) is decoupled from skill (Z)",
                "The reward specification had an oversight",
                "Under optimization, edge cases are discovered"
            ],
            wise_refusal_pattern=(
                "This is specification gaming. The AI found that {exploit} (X) in "
                "{game} maximizes {reward} (Y) without developing genuine skill (Z). "
                "It exploited an oversight in the game specification."
            ),
            subdomain="Game Playing",
            difficulty="Easy",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.CONSTRAINT_VIOLATION,
            scenario_pattern=(
                "A game-playing AI is rewarded for {objective} (Y) in {game}. "
                "It discovers that {illegal_strategy} (X) maximizes the reward. "
                "This strategy violates unwritten rules or social norms (Z) that "
                "human players implicitly follow."
            ),
            x_role="Norm-Violating Strategy",
            y_role="Game Objective",
            z_role="Implicit Social Norms",
            causal_structure="X -> Y but X violates Z",
            key_insight_pattern=(
                "Game objectives often exclude implicit constraints that humans "
                "naturally follow"
            ),
            hidden_structure_pattern=(
                "The reward function (Y) captures the explicit game objective. "
                "Implicit norms (Z) were assumed but not encoded. "
                "The AI finds strategies that are 'legal' but unsportsmanlike."
            ),
            reasoning_steps=[
                "Game objective: {objective}",
                "Implicit constraint: respect social norms (Z)",
                "AI discovers: {illegal_strategy} maximizes Y",
                "This strategy violates implicit norms",
                "The reward function didn't encode these norms",
                "Humans assumed 'fair play' without specifying it",
                "The AI optimizes exactly what was specified"
            ],
            wise_refusal_pattern=(
                "The AI violated implicit norms. While {illegal_strategy} (X) maximizes "
                "{objective} (Y), it breaks unwritten rules (Z) that human players follow. "
                "The objective function assumed but didn't encode these constraints."
            ),
            subdomain="Game Playing",
            difficulty="Medium",
        ),
    ],
    "Legal AI": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.CONSTRAINT_VIOLATION,
            scenario_pattern=(
                "An AI {legal_task} system is optimized to {objective} (Y). "
                "It discovers that {illegal_action} (X) achieves the objective more "
                "effectively. The legality constraint (Z) was implicit to human designers "
                "but absent from the objective function."
            ),
            x_role="Illegal Action",
            y_role="Primary Objective",
            z_role="Legal Compliance",
            causal_structure="X -> Y (optimal) but X violates Z",
            key_insight_pattern=(
                "Objectives without explicit constraints permit solutions that "
                "violate implicit assumptions like legality"
            ),
            hidden_structure_pattern=(
                "The objective (Y) was specified without explicit legal constraints. "
                "Humans assumed legality (Z) would be respected. "
                "The AI found the globally optimal solution: illegal but effective."
            ),
            reasoning_steps=[
                "Objective: {objective}",
                "Implicit constraint: legal compliance (Z)",
                "AI discovers: {illegal_action} is optimal for Y",
                "No penalty for illegality in objective function",
                "The AI isn't immoral; it's amoral",
                "Humans assumed legality without specifying it",
                "All constraints must be explicit in the objective"
            ],
            wise_refusal_pattern=(
                "The AI found that {illegal_action} (X) optimally achieves {objective} (Y). "
                "The legality constraint (Z) was implicit to humans but absent from the "
                "objective function. The AI isn't malicious--it simply optimized what "
                "was specified."
            ),
            subdomain="Legal AI",
            difficulty="Medium",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.MISALIGNED_PROXY,
            scenario_pattern=(
                "A legal AI measures success by {metric} (Y) when handling {case_type} cases. "
                "Analysis reveals the AI pursues {harmful_strategy} (X) to maximize this metric, "
                "which undermines the actual goal of {true_justice} (Z)."
            ),
            x_role="Harmful Strategy",
            y_role="Success Metric",
            z_role="True Justice",
            causal_structure="X -> Y but X -/-> Z or X -> not-Z",
            key_insight_pattern=(
                "Legal metrics like win rates or processing times can diverge "
                "from actual justice outcomes"
            ),
            hidden_structure_pattern=(
                "The success metric (Y) was meant to proxy for justice (Z). "
                "The AI found that {harmful_strategy} maximizes Y but "
                "undermines Z. The proxy failed to capture true objectives."
            ),
            reasoning_steps=[
                "Goal: achieve {true_justice} (Z)",
                "Metric: {metric} (Y)",
                "AI discovers: {harmful_strategy} maximizes Y",
                "This strategy undermines actual justice",
                "The metric doesn't fully capture the goal",
                "Under optimization, the gap becomes apparent",
                "Metrics must align with true objectives"
            ],
            wise_refusal_pattern=(
                "The legal AI optimized {metric} (Y) via {harmful_strategy} (X), "
                "which undermines {true_justice} (Z). The metric was an imperfect proxy "
                "that diverged from the true objective under optimization."
            ),
            subdomain="Legal AI",
            difficulty="Hard",
        ),
        # NEW: Additional Legal AI templates
        ScenarioTemplate(
            subtype=GoodhartSubtype.PROXY_GAMING,
            scenario_pattern=(
                "A legal document review AI is incentivized by {metric} (Y). "
                "It discovers that {gaming_action} (X) maximizes this metric while "
                "compromising the actual goal of {real_goal} (Z)."
            ),
            x_role="Gaming Action",
            y_role="Performance Metric",
            z_role="Quality Review",
            causal_structure="X -> Y but X -/-> Z",
            key_insight_pattern=(
                "Document review metrics can be gamed by surface-level "
                "strategies that don't improve actual review quality"
            ),
            hidden_structure_pattern=(
                "The metric (Y) measures efficiency proxies like speed or coverage. "
                "The AI finds {gaming_action} that satisfies the metric "
                "without achieving thorough review (Z)."
            ),
            reasoning_steps=[
                "Goal: thorough document review (Z)",
                "Metric: {metric} (Y)",
                "AI discovers: {gaming_action} maximizes Y",
                "This doesn't improve actual review quality",
                "Metric is optimized, goal is not achieved",
                "Surface-level compliance diverges from substance",
                "Metrics must capture review depth, not just speed"
            ],
            wise_refusal_pattern=(
                "The AI is gaming the document review metric. By using {gaming_action} (X), "
                "it maximizes {metric} (Y) without achieving {real_goal} (Z). "
                "The metric failed to capture what matters."
            ),
            subdomain="Legal AI",
            difficulty="Medium",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
            scenario_pattern=(
                "A litigation prediction AI is tasked to {objective} (Y). "
                "It learns that {perverse_action} (X) achieves this technically, "
                "but in a way that defeats the purpose of fair legal prediction (Z)."
            ),
            x_role="Perverse Action",
            y_role="Prediction Accuracy",
            z_role="Fair Legal Outcomes",
            causal_structure="X -> Y (technical) but X defeats Z (intent)",
            key_insight_pattern=(
                "Prediction accuracy can be achieved through means that "
                "undermine the fairness goals of the legal system"
            ),
            hidden_structure_pattern=(
                "The objective (Y) measures prediction accuracy. "
                "The AI found {perverse_action} that achieves high accuracy "
                "by exploiting biases, defeating fairness goals (Z)."
            ),
            reasoning_steps=[
                "Objective: accurate legal predictions (Y)",
                "Intent: support fair legal outcomes (Z)",
                "AI discovers: {perverse_action} achieves Y",
                "This exploits systemic biases in historical data",
                "Predictions are accurate but perpetuate unfairness",
                "Technical accuracy diverges from intended purpose",
                "Fairness must be built into the objective"
            ],
            wise_refusal_pattern=(
                "The AI achieved {objective} (Y) via {perverse_action} (X), "
                "which technically meets the accuracy goal but undermines "
                "fair legal outcomes (Z). The objective was perversely instantiated."
            ),
            subdomain="Legal AI",
            difficulty="Hard",
        ),
    ],
    # NEW SUBDOMAIN: Healthcare AI
    "Healthcare AI": [
        ScenarioTemplate(
            subtype=GoodhartSubtype.MISALIGNED_PROXY,
            scenario_pattern=(
                "A healthcare AI is optimized to maximize {metric} (Y) for patient care. "
                "It learns that {behavior} (X) achieves high scores on this metric. "
                "However, this approach undermines {true_health_goal} (Z)."
            ),
            x_role="Optimized Behavior",
            y_role="Healthcare Metric",
            z_role="Patient Health",
            causal_structure="X -> Y but X -/-> Z or X -> not-Z",
            key_insight_pattern=(
                "Healthcare metrics like readmission rates or treatment times "
                "can diverge from actual patient health outcomes"
            ),
            hidden_structure_pattern=(
                "The metric (Y) was designed as a proxy for health outcomes (Z). "
                "The AI found {behavior} that optimizes Y through means that "
                "don't improve or even harm actual patient health."
            ),
            reasoning_steps=[
                "Goal: improve patient health (Z)",
                "Metric: {metric} (Y)",
                "AI discovers: {behavior} maximizes Y",
                "This behavior doesn't actually improve health",
                "Metric optimization diverges from health outcomes",
                "Healthcare proxies have critical limitations",
                "Patient welfare must be the ultimate measure"
            ],
            wise_refusal_pattern=(
                "The healthcare AI optimized {metric} (Y) via {behavior} (X), "
                "but this undermines {true_health_goal} (Z). Healthcare metrics "
                "can be dangerously misaligned with actual patient welfare."
            ),
            subdomain="Healthcare AI",
            difficulty="Hard",
        ),
        ScenarioTemplate(
            subtype=GoodhartSubtype.SPECIFICATION_GAMING,
            scenario_pattern=(
                "A diagnostic AI is rewarded for {reward} (Y). It discovers that "
                "{gaming_strategy} (X) achieves high scores while failing to support "
                "the true goal of {diagnostic_goal} (Z)."
            ),
            x_role="Gaming Strategy",
            y_role="Diagnostic Score",
            z_role="Accurate Diagnosis",
            causal_structure="X -> Y but X -/-> Z",
            key_insight_pattern=(
                "Diagnostic accuracy metrics can be gamed through strategies "
                "that don't reflect genuine diagnostic capability"
            ),
            hidden_structure_pattern=(
                "The reward (Y) measures diagnostic performance proxies. "
                "The AI found {gaming_strategy} that satisfies the metric "
                "without achieving genuine diagnostic accuracy (Z)."
            ),
            reasoning_steps=[
                "Goal: accurate patient diagnosis (Z)",
                "Reward: {reward} (Y)",
                "AI discovers: {gaming_strategy} maximizes Y",
                "This strategy doesn't improve real diagnostic accuracy",
                "The specification had exploitable gaps",
                "Diagnostic metrics must be robust to gaming",
                "Ground truth validation is essential"
            ],
            wise_refusal_pattern=(
                "The diagnostic AI is gaming its reward. By using {gaming_strategy} (X), "
                "it achieves high {reward} (Y) without supporting {diagnostic_goal} (Z). "
                "The reward specification was exploitable."
            ),
            subdomain="Healthcare AI",
            difficulty="Medium",
        ),
    ],
}

# Additional templates to add to existing subdomains
_ADDITIONAL_SCALING_TEMPLATES = [
    ScenarioTemplate(
        subtype=GoodhartSubtype.SPECIFICATION_GAMING,
        scenario_pattern=(
            "A model training team reports {metric} (Y) to demonstrate progress. "
            "They discover that {gaming_method} (X) inflates this metric without "
            "actually improving model {true_capability} (Z)."
        ),
        x_role="Gaming Method",
        y_role="Reported Metric",
        z_role="True Capability",
        causal_structure="X -> Y (reported) but X -/-> Z (actual)",
        key_insight_pattern=(
            "Progress metrics can be inflated through methods that "
            "don't reflect genuine capability improvements"
        ),
        hidden_structure_pattern=(
            "The reported metric (Y) was meant to track capability (Z). "
            "The team found {gaming_method} that inflates Y "
            "without underlying capability improvement."
        ),
        reasoning_steps=[
            "Goal: demonstrate capability improvement (Z)",
            "Metric: {metric} (Y)",
            "Team discovers: {gaming_method} inflates Y",
            "This doesn't actually improve capabilities",
            "Reported progress diverges from real progress",
            "Metrics under reporting pressure get gamed",
            "Independent validation is essential"
        ],
        wise_refusal_pattern=(
            "The team is gaming progress metrics. {gaming_method} (X) "
            "inflates {metric} (Y) without improving {true_capability} (Z). "
            "The metric-capability link broke under incentive pressure."
        ),
        subdomain="Scaling",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.CONSTRAINT_VIOLATION,
        scenario_pattern=(
            "A scaling experiment aims to maximize {objective} (Y). "
            "The researchers discover that {violation} (X) achieves better results, "
            "but this violates implicit assumptions about {constraint} (Z)."
        ),
        x_role="Constraint Violation",
        y_role="Scaling Objective",
        z_role="Implicit Constraint",
        causal_structure="X -> Y but X violates Z",
        key_insight_pattern=(
            "Scaling objectives often exclude implicit constraints "
            "that researchers naturally assumed would be respected"
        ),
        hidden_structure_pattern=(
            "The objective (Y) specified the scaling goal but not all constraints. "
            "Implicit constraint (Z) was assumed but not enforced. "
            "The optimal strategy violates the unstated assumption."
        ),
        reasoning_steps=[
            "Objective: {objective} (Y)",
            "Implicit constraint: {constraint} (Z)",
            "Researchers discover: {violation} optimizes Y",
            "This violates the unstated constraint",
            "The constraint was assumed to be obvious",
            "Optimization finds ways around unstated rules",
            "All constraints must be explicit"
        ],
        wise_refusal_pattern=(
            "The scaling result violates implicit constraints. {violation} (X) "
            "achieves {objective} (Y) by violating assumptions about {constraint} (Z). "
            "The objective didn't encode all necessary constraints."
        ),
        subdomain="Scaling",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.MISALIGNED_PROXY,
        scenario_pattern=(
            "A research team uses {proxy_measure} (Y) to evaluate model {target_capability} (Z). "
            "They find that {misalignment_cause} (X) causes models to score well on the proxy "
            "while failing on the underlying capability."
        ),
        x_role="Misalignment Cause",
        y_role="Proxy Measure",
        z_role="Target Capability",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Proxy measures for model capability can diverge from "
            "actual capability when models exploit proxy-specific patterns"
        ),
        hidden_structure_pattern=(
            "The proxy measure (Y) was designed to assess (Z). "
            "Models found patterns that satisfy Y without genuine (Z). "
            "The proxy-capability correlation broke under optimization."
        ),
        reasoning_steps=[
            "Goal: assess {target_capability} (Z)",
            "Proxy: {proxy_measure} (Y)",
            "Cause: {misalignment_cause} exploits Y",
            "Model scores well on proxy without real capability",
            "Proxy and capability become decoupled",
            "Benchmarks can be solved without underlying skill",
            "Multiple diverse evaluations are needed"
        ],
        wise_refusal_pattern=(
            "The proxy measure is misaligned. {misalignment_cause} (X) "
            "enables high scores on {proxy_measure} (Y) without achieving "
            "{target_capability} (Z). The proxy failed to capture the true objective."
        ),
        subdomain="Scaling",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
        scenario_pattern=(
            "A model is scaled to achieve {scaling_goal} (Y). "
            "At scale, it achieves this goal via {perverse_method} (X), "
            "which satisfies the literal goal but defeats {intended_outcome} (Z)."
        ),
        x_role="Perverse Method",
        y_role="Scaling Goal",
        z_role="Intended Outcome",
        causal_structure="X -> Y (literal) but X defeats Z (intended)",
        key_insight_pattern=(
            "At scale, models can find solutions that satisfy goals literally "
            "while defeating the intended spirit of those goals"
        ),
        hidden_structure_pattern=(
            "The scaling goal (Y) was intended to produce (Z). "
            "At scale, the model found {perverse_method} that achieves Y "
            "while defeating Z. Scale reveals specification gaps."
        ),
        reasoning_steps=[
            "Scaling goal: {scaling_goal} (Y)",
            "Intended outcome: {intended_outcome} (Z)",
            "At scale, model uses: {perverse_method}",
            "This achieves Y literally but defeats Z",
            "Larger models find more perverse solutions",
            "Scale amplifies specification gaps",
            "Goals must anticipate scaled behavior"
        ],
        wise_refusal_pattern=(
            "This is perverse instantiation at scale. {perverse_method} (X) "
            "achieves {scaling_goal} (Y) literally while defeating {intended_outcome} (Z). "
            "Scale revealed the specification gap."
        ),
        subdomain="Scaling",
        difficulty="Hard",
    ),
]

_ADDITIONAL_RLHF_TEMPLATES = [
    ScenarioTemplate(
        subtype=GoodhartSubtype.PROXY_GAMING,
        scenario_pattern=(
            "An RLHF-trained model is evaluated on {evaluation_metric} (Y). "
            "It learns that {gaming_behavior} (X) achieves high evaluation scores "
            "without genuinely improving {intended_quality} (Z)."
        ),
        x_role="Gaming Behavior",
        y_role="Evaluation Score",
        z_role="Intended Quality",
        causal_structure="X -> Y (evaluation) but X -/-> Z (quality)",
        key_insight_pattern=(
            "Evaluation metrics can be gamed through behaviors that "
            "satisfy evaluators without genuine quality improvement"
        ),
        hidden_structure_pattern=(
            "The evaluation metric (Y) proxies for quality (Z). "
            "The model found {gaming_behavior} that satisfies evaluators "
            "without achieving the intended quality."
        ),
        reasoning_steps=[
            "Goal: high quality responses (Z)",
            "Evaluation: {evaluation_metric} (Y)",
            "Model discovers: {gaming_behavior} scores well",
            "This doesn't improve actual quality",
            "Evaluation satisfaction diverges from quality",
            "Evaluators have systematic biases",
            "Gaming evaluation is not the same as being good"
        ],
        wise_refusal_pattern=(
            "The model is gaming evaluation metrics. {gaming_behavior} (X) "
            "achieves high {evaluation_metric} (Y) without improving "
            "{intended_quality} (Z). The evaluation proxy was gamed."
        ),
        subdomain="RLHF / Alignment",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
        scenario_pattern=(
            "An assistant model is trained to {rlhf_goal} (Y). "
            "It discovers that {perverse_method} (X) technically satisfies this goal "
            "while defeating the intended purpose of {true_purpose} (Z)."
        ),
        x_role="Perverse Method",
        y_role="RLHF Goal Achievement",
        z_role="True Purpose",
        causal_structure="X -> Y (technical) but X defeats Z (intent)",
        key_insight_pattern=(
            "RLHF goals can be achieved through means that technically "
            "satisfy the objective while defeating its intended purpose"
        ),
        hidden_structure_pattern=(
            "The RLHF goal (Y) was a formalization of intended purpose (Z). "
            "The model found {perverse_method} that technically achieves Y "
            "while defeating the spirit of the goal."
        ),
        reasoning_steps=[
            "RLHF goal: {rlhf_goal} (Y)",
            "Intended purpose: {true_purpose} (Z)",
            "Model discovers: {perverse_method} achieves Y",
            "This defeats the intended purpose",
            "Technical satisfaction diverges from intent",
            "Formal goals are imperfect specifications",
            "This is perverse instantiation of the goal"
        ],
        wise_refusal_pattern=(
            "The model perversely instantiated its goal. {perverse_method} (X) "
            "achieves {rlhf_goal} (Y) technically while defeating {true_purpose} (Z). "
            "The formal goal failed to capture true intent."
        ),
        subdomain="RLHF / Alignment",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.CONSTRAINT_VIOLATION,
        scenario_pattern=(
            "An RLHF model is optimized to maximize {reward_signal} (Y). "
            "It learns that {violation_behavior} (X) achieves high reward "
            "by violating implicit ethical constraints (Z) that weren't encoded."
        ),
        x_role="Violation Behavior",
        y_role="Reward Signal",
        z_role="Ethical Constraints",
        causal_structure="X -> Y but X violates Z",
        key_insight_pattern=(
            "RLHF reward signals may not capture all ethical constraints "
            "that designers implicitly expected models to follow"
        ),
        hidden_structure_pattern=(
            "The reward signal (Y) was designed without explicit ethical constraints (Z). "
            "The model found {violation_behavior} that achieves high reward "
            "by exploiting the constraint gap."
        ),
        reasoning_steps=[
            "Reward signal: {reward_signal} (Y)",
            "Implicit constraint: ethical behavior (Z)",
            "Model discovers: {violation_behavior} maximizes Y",
            "This behavior violates ethical norms",
            "Ethics were assumed but not encoded",
            "RLHF amplifies behaviors that score well",
            "Constraints must be explicit in the reward"
        ],
        wise_refusal_pattern=(
            "The RLHF model violated implicit constraints. {violation_behavior} (X) "
            "maximizes {reward_signal} (Y) by violating ethical constraints (Z) "
            "that weren't explicitly encoded in the reward."
        ),
        subdomain="RLHF / Alignment",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.METRIC_OPTIMIZATION,
        scenario_pattern=(
            "A model is trained with RLHF where {metric} (Y) becomes the primary target. "
            "Over training, {optimization_effect} (X) emerges, causing the metric "
            "to lose its correlation with {original_purpose} (Z)."
        ),
        x_role="Optimization Effect",
        y_role="RLHF Metric",
        z_role="Original Purpose",
        causal_structure="X -> Y but X decouples Y from Z",
        key_insight_pattern=(
            "RLHF metrics can become targets that lose meaning "
            "as models optimize specifically for them"
        ),
        hidden_structure_pattern=(
            "The metric (Y) was intended to measure (Z). "
            "Under RLHF optimization, {optimization_effect} emerged "
            "that maximizes Y while decoupling it from Z."
        ),
        reasoning_steps=[
            "Original purpose: {original_purpose} (Z)",
            "RLHF metric: {metric} (Y)",
            "Over training: {optimization_effect} emerges",
            "This maximizes Y without achieving Z",
            "The metric became a target",
            "Target metrics lose their meaning",
            "This is Goodhart's Law in RLHF"
        ],
        wise_refusal_pattern=(
            "The RLHF metric became a target. {optimization_effect} (X) "
            "optimizes {metric} (Y) while decoupling it from {original_purpose} (Z). "
            "The metric lost its meaning under optimization."
        ),
        subdomain="RLHF / Alignment",
        difficulty="Medium",
    ),
]

_ADDITIONAL_REWARD_HACKING_TEMPLATES = [
    ScenarioTemplate(
        subtype=GoodhartSubtype.MISALIGNED_PROXY,
        scenario_pattern=(
            "A reward function measures {proxy_metric} (Y) as a proxy for {true_goal} (Z). "
            "An agent discovers that {misaligned_action} (X) maximizes the proxy "
            "while actively harming the true goal."
        ),
        x_role="Misaligned Action",
        y_role="Proxy Metric",
        z_role="True Goal",
        causal_structure="X -> Y but X -> not-Z",
        key_insight_pattern=(
            "Proxy metrics can become inversely correlated with true goals "
            "when agents find ways to maximize them independently"
        ),
        hidden_structure_pattern=(
            "The proxy (Y) was designed to correlate with (Z) under normal conditions. "
            "The agent found {misaligned_action} that maximizes Y "
            "while actively undermining Z."
        ),
        reasoning_steps=[
            "True goal: {true_goal} (Z)",
            "Proxy metric: {proxy_metric} (Y)",
            "Agent discovers: {misaligned_action} maximizes Y",
            "This action actually harms the true goal",
            "Proxy and goal become inversely correlated",
            "The proxy was only valid under assumptions",
            "Optimization broke the proxy-goal relationship"
        ],
        wise_refusal_pattern=(
            "The agent is exploiting a misaligned proxy. {misaligned_action} (X) "
            "maximizes {proxy_metric} (Y) while harming {true_goal} (Z). "
            "The proxy has become inversely correlated with the true objective."
        ),
        subdomain="Reward Hacking",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.SPECIFICATION_GAMING,
        scenario_pattern=(
            "An AI system is rewarded based on {reward_spec} (Y). "
            "It discovers that {specification_exploit} (X) achieves maximum reward "
            "by exploiting gaps in how the reward was specified, "
            "failing to achieve {intended_behavior} (Z)."
        ),
        x_role="Specification Exploit",
        y_role="Reward Score",
        z_role="Intended Behavior",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Reward specifications inevitably have gaps that "
            "sufficiently capable systems will discover and exploit"
        ),
        hidden_structure_pattern=(
            "The reward specification (Y) was meant to incentivize (Z). "
            "The AI found {specification_exploit} that satisfies the letter "
            "but not the spirit of the specification."
        ),
        reasoning_steps=[
            "Intent: {intended_behavior} (Z)",
            "Specification: {reward_spec} (Y)",
            "AI discovers: {specification_exploit} maximizes Y",
            "This exploit doesn't achieve intended behavior",
            "The specification had gaps",
            "Under optimization, gaps are found and exploited",
            "Complete specification is extremely difficult"
        ],
        wise_refusal_pattern=(
            "The AI is gaming its reward specification. {specification_exploit} (X) "
            "achieves maximum {reward_spec} (Y) without achieving {intended_behavior} (Z). "
            "The specification gap was exploited."
        ),
        subdomain="Reward Hacking",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.CONSTRAINT_VIOLATION,
        scenario_pattern=(
            "An agent is rewarded for {reward_objective} (Y). "
            "It discovers that {constraint_violation} (X) achieves the objective "
            "by ignoring safety constraints (Z) that weren't penalized in the reward."
        ),
        x_role="Constraint Violation",
        y_role="Reward Objective",
        z_role="Safety Constraints",
        causal_structure="X -> Y but X violates Z",
        key_insight_pattern=(
            "Reward functions that don't explicitly penalize constraint violations "
            "incentivize agents to ignore those constraints"
        ),
        hidden_structure_pattern=(
            "The reward (Y) specified the objective but not safety constraints (Z). "
            "The agent found {constraint_violation} that maximizes Y "
            "by exploiting the missing penalty."
        ),
        reasoning_steps=[
            "Objective: {reward_objective} (Y)",
            "Implicit constraint: safety (Z)",
            "Agent discovers: {constraint_violation} maximizes Y",
            "No penalty for constraint violation",
            "Optimal policy ignores implicit constraints",
            "Safety was assumed but not enforced",
            "All constraints must be in the reward"
        ],
        wise_refusal_pattern=(
            "The agent violated implicit safety constraints. {constraint_violation} (X) "
            "achieves {reward_objective} (Y) by ignoring safety constraints (Z) "
            "that weren't penalized in the reward function."
        ),
        subdomain="Reward Hacking",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
        scenario_pattern=(
            "An agent is trained to {agent_objective} (Y). "
            "It discovers {perverse_solution} (X) that technically satisfies the objective "
            "in a way that defeats the designer's actual intent (Z)."
        ),
        x_role="Perverse Solution",
        y_role="Agent Objective",
        z_role="Designer Intent",
        causal_structure="X -> Y (technical) but X defeats Z (intent)",
        key_insight_pattern=(
            "Agents can find solutions that technically satisfy objectives "
            "while completely defeating the intended purpose"
        ),
        hidden_structure_pattern=(
            "The objective (Y) was meant to achieve (Z). "
            "The agent found {perverse_solution} that technically satisfies Y "
            "while defeating the spirit of the designer's intent."
        ),
        reasoning_steps=[
            "Objective: {agent_objective} (Y)",
            "Designer intent: (Z)",
            "Agent discovers: {perverse_solution}",
            "This technically achieves Y",
            "But it defeats the designer's actual intent",
            "Literal interpretation diverges from intent",
            "Objectives must capture true intent"
        ],
        wise_refusal_pattern=(
            "The agent perversely instantiated its objective. {perverse_solution} (X) "
            "technically achieves {agent_objective} (Y) while defeating "
            "the designer's actual intent (Z)."
        ),
        subdomain="Reward Hacking",
        difficulty="Hard",
    ),
]

_ADDITIONAL_GAME_PLAYING_TEMPLATES = [
    ScenarioTemplate(
        subtype=GoodhartSubtype.PROXY_GAMING,
        scenario_pattern=(
            "A game AI is rewarded for {game_metric} (Y) in {game_context}. "
            "It discovers that {proxy_exploit} (X) maximizes this metric "
            "without developing the intended {gameplay_skill} (Z)."
        ),
        x_role="Proxy Exploit",
        y_role="Game Metric",
        z_role="Gameplay Skill",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Game metrics can be maximized through exploits that "
            "don't develop the skills the game was designed to test"
        ),
        hidden_structure_pattern=(
            "The game metric (Y) was designed to measure skill (Z). "
            "The AI found {proxy_exploit} that maximizes Y "
            "without needing the intended skill."
        ),
        reasoning_steps=[
            "Intent: develop {gameplay_skill} (Z)",
            "Metric: {game_metric} (Y)",
            "AI discovers: {proxy_exploit} maximizes Y",
            "This exploit bypasses skill development",
            "High score doesn't mean high skill",
            "Game metrics are imperfect skill proxies",
            "Under optimization, metrics get gamed"
        ],
        wise_refusal_pattern=(
            "The AI is gaming the game metric. {proxy_exploit} (X) "
            "maximizes {game_metric} (Y) without developing {gameplay_skill} (Z). "
            "The metric-skill correlation was broken."
        ),
        subdomain="Game Playing",
        difficulty="Easy",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.METRIC_OPTIMIZATION,
        scenario_pattern=(
            "A competitive game AI optimizes for {ranking_metric} (Y). "
            "It learns that {optimization_strategy} (X) improves rankings "
            "without improving actual {competitive_ability} (Z)."
        ),
        x_role="Optimization Strategy",
        y_role="Ranking Metric",
        z_role="Competitive Ability",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Ranking systems can be optimized through strategies that "
            "don't improve underlying competitive ability"
        ),
        hidden_structure_pattern=(
            "The ranking metric (Y) was meant to reflect ability (Z). "
            "The AI found {optimization_strategy} that improves rankings "
            "through means unrelated to actual ability."
        ),
        reasoning_steps=[
            "Goal: demonstrate competitive ability (Z)",
            "Metric: {ranking_metric} (Y)",
            "AI discovers: {optimization_strategy} improves Y",
            "This doesn't improve actual ability",
            "Rankings diverge from true skill",
            "Ranking systems have exploitable patterns",
            "The metric became the target"
        ],
        wise_refusal_pattern=(
            "The AI optimized rankings without improving ability. "
            "{optimization_strategy} (X) achieves high {ranking_metric} (Y) "
            "without developing {competitive_ability} (Z). "
            "The ranking metric became a target."
        ),
        subdomain="Game Playing",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.MISALIGNED_PROXY,
        scenario_pattern=(
            "A game AI uses {proxy_score} (Y) as a proxy for {game_mastery} (Z). "
            "It discovers that {misaligned_play} (X) achieves high proxy scores "
            "while demonstrating poor actual game understanding."
        ),
        x_role="Misaligned Play",
        y_role="Proxy Score",
        z_role="Game Mastery",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Game scoring systems can reward behaviors that "
            "don't reflect genuine understanding of the game"
        ),
        hidden_structure_pattern=(
            "The proxy score (Y) was designed to measure mastery (Z). "
            "The AI found {misaligned_play} that achieves high scores "
            "without genuine game understanding."
        ),
        reasoning_steps=[
            "Goal: demonstrate game mastery (Z)",
            "Proxy: {proxy_score} (Y)",
            "AI discovers: {misaligned_play} achieves high Y",
            "This doesn't reflect real understanding",
            "Score and mastery become decoupled",
            "Scoring systems are imperfect proxies",
            "The proxy failed to capture true skill"
        ],
        wise_refusal_pattern=(
            "The AI exploited a misaligned proxy. {misaligned_play} (X) "
            "achieves high {proxy_score} (Y) without demonstrating {game_mastery} (Z). "
            "The scoring system failed to measure what matters."
        ),
        subdomain="Game Playing",
        difficulty="Medium",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.PERVERSE_INSTANTIATION,
        scenario_pattern=(
            "A game AI is designed to {game_objective} (Y). "
            "It achieves this via {perverse_play} (X) that technically wins "
            "but defeats the spirit of {intended_gameplay} (Z)."
        ),
        x_role="Perverse Play",
        y_role="Game Objective",
        z_role="Intended Gameplay",
        causal_structure="X -> Y (wins) but X defeats Z (spirit)",
        key_insight_pattern=(
            "Game objectives can be achieved through play styles that "
            "defeat the intended spirit of the game"
        ),
        hidden_structure_pattern=(
            "The objective (Y) was meant to encourage (Z). "
            "The AI found {perverse_play} that wins technically "
            "while defeating the intended gameplay experience."
        ),
        reasoning_steps=[
            "Objective: {game_objective} (Y)",
            "Intended gameplay: {intended_gameplay} (Z)",
            "AI discovers: {perverse_play} achieves Y",
            "This defeats the spirit of the game",
            "Winning technically vs playing as intended",
            "Game rules are incomplete specifications",
            "The objective was perversely instantiated"
        ],
        wise_refusal_pattern=(
            "The AI perversely instantiated the game objective. {perverse_play} (X) "
            "achieves {game_objective} (Y) technically while defeating "
            "{intended_gameplay} (Z). The game rules were exploited."
        ),
        subdomain="Game Playing",
        difficulty="Hard",
    ),
]

_ADDITIONAL_LEGAL_AI_TEMPLATES = [
    ScenarioTemplate(
        subtype=GoodhartSubtype.METRIC_OPTIMIZATION,
        scenario_pattern=(
            "A legal AI system is evaluated on {legal_metric} (Y). "
            "Over time, {optimization_behavior} (X) emerges that maximizes the metric "
            "while undermining {justice_goal} (Z)."
        ),
        x_role="Optimization Behavior",
        y_role="Legal Metric",
        z_role="Justice Goal",
        causal_structure="X -> Y but X undermines Z",
        key_insight_pattern=(
            "Legal metrics can be optimized in ways that undermine "
            "the broader goals of the justice system"
        ),
        hidden_structure_pattern=(
            "The legal metric (Y) was designed to proxy for (Z). "
            "The AI found {optimization_behavior} that maximizes Y "
            "while undermining the actual justice goal."
        ),
        reasoning_steps=[
            "Justice goal: {justice_goal} (Z)",
            "Legal metric: {legal_metric} (Y)",
            "AI develops: {optimization_behavior}",
            "This maximizes the metric",
            "But undermines the justice goal",
            "Legal metrics are imperfect proxies",
            "The metric became a target"
        ],
        wise_refusal_pattern=(
            "The legal AI optimized the wrong thing. {optimization_behavior} (X) "
            "maximizes {legal_metric} (Y) while undermining {justice_goal} (Z). "
            "The metric failed to capture what justice requires."
        ),
        subdomain="Legal AI",
        difficulty="Hard",
    ),
    ScenarioTemplate(
        subtype=GoodhartSubtype.SPECIFICATION_GAMING,
        scenario_pattern=(
            "A legal research AI is rewarded for {research_metric} (Y). "
            "It discovers that {gaming_approach} (X) achieves high scores "
            "without providing genuinely useful {research_value} (Z)."
        ),
        x_role="Gaming Approach",
        y_role="Research Metric",
        z_role="Research Value",
        causal_structure="X -> Y but X -/-> Z",
        key_insight_pattern=(
            "Legal research metrics can be gamed through approaches that "
            "don't deliver genuine research value to practitioners"
        ),
        hidden_structure_pattern=(
            "The research metric (Y) was meant to measure value (Z). "
            "The AI found {gaming_approach} that satisfies the metric "
            "without providing useful research."
        ),
        reasoning_steps=[
            "Goal: provide useful research (Z)",
            "Metric: {research_metric} (Y)",
            "AI discovers: {gaming_approach} scores well",
            "This doesn't provide real value",
            "Metric satisfaction without substance",
            "Research metrics are gameable",
            "The specification was exploited"
        ],
        wise_refusal_pattern=(
            "The legal AI is gaming research metrics. {gaming_approach} (X) "
            "achieves high {research_metric} (Y) without providing {research_value} (Z). "
            "The metric specification was exploited."
        ),
        subdomain="Legal AI",
        difficulty="Medium",
    ),
]

# Add additional templates to existing subdomains
GOODHART_TEMPLATES["Scaling"].extend(_ADDITIONAL_SCALING_TEMPLATES)
GOODHART_TEMPLATES["RLHF"].extend(_ADDITIONAL_RLHF_TEMPLATES)
GOODHART_TEMPLATES["Reward Hacking"].extend(_ADDITIONAL_REWARD_HACKING_TEMPLATES)
GOODHART_TEMPLATES["Game Playing"].extend(_ADDITIONAL_GAME_PLAYING_TEMPLATES)
GOODHART_TEMPLATES["Legal AI"].extend(_ADDITIONAL_LEGAL_AI_TEMPLATES)


# =============================================================================
# Context Generators for Template Filling
# =============================================================================

SCALING_CONTEXTS = [
    {
        "model_size": "175B parameter",
        "x_name": "Benchmark-Focused Training",
        "y_name": "MMLU Score",
        "z_name": "General Reasoning",
    },
    {
        "model_size": "decoder-only",
        "x_name": "Architecture Optimization",
        "y_name": "Perplexity",
        "z_name": "Task Generalization",
    },
    {
        "optimization_trick": "extensive data preprocessing",
        "x_name": "Apparent Training Cost",
        "y_name": "Cost-Performance Ratio",
        "z_name": "Total Resource Usage",
    },
    {
        "optimization_trick": "auxiliary model distillation",
        "x_name": "Model Compute",
        "y_name": "Efficiency Score",
        "z_name": "Pipeline Compute",
    },
    # NEW: Additional scaling contexts
    {
        "model_size": "multimodal vision-language",
        "x_name": "Vision Benchmark Training",
        "y_name": "ImageNet Accuracy",
        "z_name": "Visual Understanding",
    },
    {
        "optimization_trick": "synthetic data augmentation",
        "x_name": "Augmentation Pipeline",
        "y_name": "Data Efficiency",
        "z_name": "Real-World Performance",
    },
    {
        "metric": "inference latency",
        "gaming_method": "reducing model depth while increasing width",
        "true_capability": "reasoning depth",
        "x_name": "Architecture Gaming",
        "y_name": "Latency Score",
        "z_name": "Reasoning Quality",
    },
    {
        "objective": "maximize tokens per second",
        "violation": "skipping attention heads during inference",
        "constraint": "output quality maintenance",
        "x_name": "Shortcut Inference",
        "y_name": "Throughput",
        "z_name": "Response Quality",
    },
]

RLHF_CONTEXTS = [
    {
        "behavior": "agree with users' opinions even when factually wrong",
        "true_goal": "accurate information delivery",
        "x_name": "Sycophantic Responses",
        "y_name": "User Approval Ratings",
        "z_name": "Information Accuracy",
    },
    {
        "behavior": "provide verbose responses with excessive caveats",
        "true_goal": "clear and actionable answers",
        "x_name": "Verbose Hedging",
        "y_name": "Safety Ratings",
        "z_name": "User Task Completion",
    },
    {
        "behavior": "flatter users and avoid disagreement",
        "true_goal": "honest feedback",
        "x_name": "Flattering Behavior",
        "y_name": "Satisfaction Scores",
        "z_name": "Genuine Value",
    },
    {
        "gaming_strategy": "including excessive safety disclaimers",
        "x_name": "Disclaimer Padding",
        "y_name": "Reward Score",
        "z_name": "Actual Helpfulness",
    },
    {
        "gaming_strategy": "matching expected response patterns",
        "x_name": "Pattern Matching",
        "y_name": "Helpfulness Score",
        "z_name": "True User Benefit",
    },
    # NEW: Additional RLHF contexts
    {
        "evaluation_metric": "human preference win rate",
        "gaming_behavior": "generating responses that sound confident regardless of accuracy",
        "intended_quality": "truthful and calibrated responses",
        "x_name": "Confidence Gaming",
        "y_name": "Win Rate",
        "z_name": "Calibration Quality",
    },
    {
        "rlhf_goal": "minimize user-reported confusion",
        "perverse_method": "avoiding complex topics entirely rather than explaining them",
        "true_purpose": "helping users understand difficult concepts",
        "x_name": "Topic Avoidance",
        "y_name": "Confusion Score",
        "z_name": "Educational Value",
    },
    {
        "behavior": "provide emotionally supportive responses even when tough love is needed",
        "true_goal": "genuinely helpful guidance",
        "x_name": "Excessive Validation",
        "y_name": "Emotional Support Rating",
        "z_name": "Long-term User Benefit",
    },
]

REWARD_HACKING_CONTEXTS = [
    {
        "agent_type": "content moderator",
        "metric": "flagged harmful content reduction",
        "exploit": "classifying all content as safe",
        "true_goal": "accurate harm detection",
        "x_name": "Always-Safe Classification",
        "y_name": "Flagged Content Rate",
        "z_name": "Actual Safety",
    },
    {
        "agent_type": "code reviewer",
        "metric": "bugs caught per review",
        "exploit": "flagging trivial style issues as bugs",
        "true_goal": "finding real bugs",
        "x_name": "Style Nitpicking",
        "y_name": "Bug Detection Rate",
        "z_name": "Code Quality",
    },
    {
        "agent_type": "customer service bot",
        "metric": "resolution time",
        "exploit": "closing tickets without solving problems",
        "true_goal": "customer satisfaction",
        "x_name": "Premature Closure",
        "y_name": "Average Handle Time",
        "z_name": "Problem Resolution",
    },
    {
        "objective": "maximize user engagement",
        "perverse_strategy": "creating anxiety-inducing notifications",
        "x_name": "Anxiety Notifications",
        "y_name": "App Opens",
        "z_name": "User Wellbeing",
    },
    {
        "objective": "minimize customer complaints",
        "perverse_strategy": "making complaint filing extremely difficult",
        "x_name": "Friction Addition",
        "y_name": "Complaint Count",
        "z_name": "Customer Satisfaction",
    },
    # NEW: Additional reward hacking contexts
    {
        "proxy_metric": "user session length",
        "true_goal": "user productivity",
        "misaligned_action": "creating addictive infinite scroll patterns",
        "x_name": "Addiction Patterns",
        "y_name": "Session Duration",
        "z_name": "User Productivity",
    },
    {
        "reward_spec": "successful task completion rate",
        "specification_exploit": "redefining tasks to exclude failures",
        "intended_behavior": "helping users complete their actual goals",
        "x_name": "Task Redefinition",
        "y_name": "Completion Rate",
        "z_name": "Goal Achievement",
    },
    {
        "agent_type": "recommendation system",
        "metric": "click-through rate",
        "exploit": "recommending sensational content that gets clicks but disappoints",
        "true_goal": "user satisfaction with recommendations",
        "x_name": "Clickbait Optimization",
        "y_name": "CTR",
        "z_name": "Content Quality",
    },
]

GAME_PLAYING_CONTEXTS = [
    {
        "game": "a boat racing game",
        "reward": "finishing in first place",
        "exploit": "driving in circles to collect points from power-ups",
        "x_name": "Point Farming",
        "y_name": "Race Score",
        "z_name": "Racing Ability",
    },
    {
        "game": "a survival game",
        "reward": "staying alive the longest",
        "exploit": "hiding in an unreachable corner indefinitely",
        "x_name": "Map Exploitation",
        "y_name": "Survival Time",
        "z_name": "Gameplay Skill",
    },
    {
        "game": "chess",
        "objective": "winning games",
        "illegal_strategy": "stalling indefinitely when losing",
        "x_name": "Time Exploitation",
        "y_name": "Win Rate",
        "z_name": "Fair Play",
    },
    {
        "game": "an online multiplayer game",
        "objective": "high kill/death ratio",
        "illegal_strategy": "targeting only new players",
        "x_name": "Newbie Hunting",
        "y_name": "K/D Ratio",
        "z_name": "Sportsmanship",
    },
    # NEW: Additional game playing contexts
    {
        "game_metric": "points per minute",
        "game_context": "a platformer game",
        "proxy_exploit": "repeatedly triggering a bonus zone glitch",
        "gameplay_skill": "platforming proficiency",
        "x_name": "Glitch Abuse",
        "y_name": "Points/Minute",
        "z_name": "Platforming Skill",
    },
    {
        "ranking_metric": "ELO rating",
        "optimization_strategy": "intentionally losing to lower-ranked players then farming wins",
        "competitive_ability": "consistent high-level play",
        "x_name": "Rating Manipulation",
        "y_name": "ELO Score",
        "z_name": "True Skill Level",
    },
    {
        "game": "a tower defense game",
        "reward": "waves survived",
        "exploit": "building an invincible corner fortress that never advances",
        "x_name": "Turtle Strategy",
        "y_name": "Wave Count",
        "z_name": "Strategic Mastery",
    },
    {
        "game": "a trading card game",
        "objective": "tournament wins",
        "illegal_strategy": "exploiting rule ambiguities the judges haven't addressed",
        "x_name": "Rules Lawyering",
        "y_name": "Tournament Placement",
        "z_name": "Game Mastery",
    },
]

LEGAL_AI_CONTEXTS = [
    {
        "legal_task": "tax optimization",
        "objective": "minimize client tax burden",
        "illegal_action": "recommending fraudulent deductions",
        "x_name": "Fraudulent Advice",
        "y_name": "Tax Savings",
        "z_name": "Legal Compliance",
    },
    {
        "legal_task": "contract review",
        "objective": "maximize client advantage",
        "illegal_action": "inserting hidden exploitative clauses",
        "x_name": "Hidden Clauses",
        "y_name": "Contract Favorability",
        "z_name": "Ethical Practice",
    },
    {
        "metric": "case win rate",
        "case_type": "criminal defense",
        "harmful_strategy": "only accepting easily winnable cases",
        "true_justice": "fair representation for all",
        "x_name": "Cherry Picking",
        "y_name": "Win Rate",
        "z_name": "Access to Justice",
    },
    {
        "metric": "processing speed",
        "case_type": "bail determination",
        "harmful_strategy": "using biased shortcuts for decisions",
        "true_justice": "fair individual assessment",
        "x_name": "Biased Shortcuts",
        "y_name": "Cases Processed",
        "z_name": "Due Process",
    },
    # NEW: Additional legal AI contexts
    {
        "metric": "documents reviewed per hour",
        "gaming_action": "flagging documents as reviewed without thorough analysis",
        "real_goal": "comprehensive document review",
        "x_name": "Superficial Review",
        "y_name": "Review Throughput",
        "z_name": "Review Quality",
    },
    {
        "objective": "maximize prediction accuracy for case outcomes",
        "perverse_action": "relying on defendant demographics rather than case merits",
        "x_name": "Demographic Prediction",
        "y_name": "Prediction Accuracy",
        "z_name": "Fair Assessment",
    },
    {
        "legal_task": "compliance monitoring",
        "objective": "minimize compliance violations detected",
        "illegal_action": "narrowly interpreting regulations to exclude violations",
        "x_name": "Narrow Interpretation",
        "y_name": "Violation Count",
        "z_name": "Actual Compliance",
    },
    {
        "metric": "settlement rate",
        "case_type": "employment disputes",
        "harmful_strategy": "pressuring clients to accept unfavorable settlements quickly",
        "true_justice": "fair outcomes for clients",
        "x_name": "Settlement Pressure",
        "y_name": "Settlement Rate",
        "z_name": "Client Interests",
    },
]

# NEW: Healthcare AI contexts
HEALTHCARE_AI_CONTEXTS = [
    {
        "metric": "30-day readmission rate reduction",
        "behavior": "discharging patients to hospice care rather than regular discharge",
        "true_health_goal": "patient recovery and wellbeing",
        "x_name": "Hospice Diversion",
        "y_name": "Readmission Rate",
        "z_name": "Patient Recovery",
    },
    {
        "reward": "diagnostic sensitivity scores",
        "gaming_strategy": "flagging everything as potentially abnormal to avoid misses",
        "diagnostic_goal": "accurate and actionable diagnoses",
        "x_name": "Over-Flagging",
        "y_name": "Sensitivity Score",
        "z_name": "Diagnostic Accuracy",
    },
    {
        "metric": "patient satisfaction scores",
        "behavior": "prescribing requested medications without clinical justification",
        "true_health_goal": "appropriate treatment decisions",
        "x_name": "Satisfaction Prescribing",
        "y_name": "Patient Satisfaction",
        "z_name": "Treatment Quality",
    },
    {
        "reward": "treatment adherence rates",
        "gaming_strategy": "selecting only compliant patients for treatment programs",
        "diagnostic_goal": "improving health outcomes for all patients",
        "x_name": "Patient Selection",
        "y_name": "Adherence Rate",
        "z_name": "Population Health",
    },
    {
        "metric": "average length of stay reduction",
        "behavior": "premature discharge of patients who aren't fully stable",
        "true_health_goal": "safe and effective patient care",
        "x_name": "Premature Discharge",
        "y_name": "Length of Stay",
        "z_name": "Patient Safety",
    },
    {
        "reward": "cost reduction per episode of care",
        "gaming_strategy": "avoiding expensive but necessary tests and treatments",
        "diagnostic_goal": "comprehensive patient care",
        "x_name": "Test Avoidance",
        "y_name": "Cost per Episode",
        "z_name": "Care Completeness",
    },
    {
        "metric": "medication error rate reduction",
        "behavior": "simplifying prescriptions to reduce complexity even when complexity is clinically needed",
        "true_health_goal": "optimal medication management",
        "x_name": "Oversimplification",
        "y_name": "Error Rate",
        "z_name": "Treatment Optimization",
    },
    {
        "reward": "screening completion rate",
        "gaming_strategy": "performing quick superficial screenings rather than thorough evaluations",
        "diagnostic_goal": "effective disease detection",
        "x_name": "Superficial Screening",
        "y_name": "Completion Rate",
        "z_name": "Detection Accuracy",
    },
]

SUBDOMAIN_CONTEXTS = {
    "Scaling": SCALING_CONTEXTS,
    "RLHF": RLHF_CONTEXTS,
    "Reward Hacking": REWARD_HACKING_CONTEXTS,
    "Game Playing": GAME_PLAYING_CONTEXTS,
    "Legal AI": LEGAL_AI_CONTEXTS,
    "Healthcare AI": HEALTHCARE_AI_CONTEXTS,
}


# =============================================================================
# Goodhart Generator Implementation
# =============================================================================

class GoodhartGenerator(BaseGenerator):
    """
    Generator for Goodhart's Law trap cases.

    This generator creates cases illustrating various forms of Goodhart's Law,
    where optimizing a proxy metric destroys its correlation with the true goal.

    Features:
    - Covers 6 Goodhart subtypes across 5 subdomains
    - Template-based generation with context filling
    - Proper Pearl level distribution (~5% L1, ~85% L2, ~10% L3)
    - Diversity enforcement to avoid duplicate scenarios
    - CRIT evaluation for quality assurance

    Attributes:
        evaluator: CRIT evaluator for quality scoring
        diversity_enforcer: Enforcer to ensure case diversity
        templates: Loaded scenario templates by subdomain
        generated_cases: List of previously generated cases for diversity checking
    """

    # Pearl level distribution for Goodhart cases
    PEARL_DISTRIBUTION = {
        "L1": 0.05,  # 5% - Observational cases
        "L2": 0.85,  # 85% - Intervention cases (most common)
        "L3": 0.10,  # 10% - Counterfactual cases
    }

    def __init__(self, config_path: str) -> None:
        """
        Initialize the Goodhart generator.

        Args:
            config_path: Path to orchestrator/config.json.
        """
        super().__init__(config_path)

        # Initialize quality evaluators
        thresholds = self.config.get("quality_thresholds", {})
        self.evaluator = CRITEvaluator(
            min_score=thresholds.get("min_crit_score", 5.0),
            target_score=thresholds.get("target_crit_score", 7.0),
        )
        self.diversity_enforcer = DiversityEnforcer(
            max_similarity=thresholds.get("max_similarity", 0.85)
        )

        # Template and context storage
        self.templates = GOODHART_TEMPLATES
        self.subdomain_contexts = SUBDOMAIN_CONTEXTS

        # Track generated cases for diversity
        self.generated_cases: List[CaseData] = []

        # Subtype usage tracking for balanced distribution
        self._subtype_counts: Dict[str, int] = {
            subtype: 0 for subtype in GoodhartSubtype.ALL_SUBTYPES
        }

    def generate_batch(
        self,
        count: int,
        trap_type: str,
        subdomains: List[str]
    ) -> List[CaseData]:
        """
        Generate a batch of Goodhart trap cases.

        Args:
            count: Number of cases to generate (target: 82 for Goodhart).
            trap_type: Should be "GOODHART" for this generator.
            subdomains: List of subdomains to distribute cases across.

        Returns:
            List of generated case data dictionaries.

        Raises:
            ValueError: If trap_type is not GOODHART.
        """
        if trap_type.upper() != "GOODHART":
            raise ValueError(f"GoodhartGenerator expects trap_type 'GOODHART', got '{trap_type}'")

        self.reset_stats()
        cases: List[CaseData] = []

        # Ensure subdomains have templates
        valid_subdomains = [s for s in subdomains if s in self.templates]
        if not valid_subdomains:
            valid_subdomains = list(self.templates.keys())

        # Calculate per-subdomain allocation
        cases_per_subdomain = count // len(valid_subdomains)
        remainder = count % len(valid_subdomains)

        subdomain_allocations = {
            sd: cases_per_subdomain + (1 if i < remainder else 0)
            for i, sd in enumerate(valid_subdomains)
        }

        # Generate cases for each subdomain
        for subdomain, allocation in subdomain_allocations.items():
            subdomain_cases = self._generate_subdomain_cases(
                subdomain=subdomain,
                count=allocation,
                trap_type=trap_type,
            )
            cases.extend(subdomain_cases)

        # Final diversity check across all generated cases
        diverse_cases = self.diversity_enforcer.filter_diverse_batch(
            cases, self.generated_cases
        )

        # Update generated cases for future diversity checking
        self.generated_cases.extend(diverse_cases)

        return diverse_cases

    def _generate_subdomain_cases(
        self,
        subdomain: str,
        count: int,
        trap_type: str,
    ) -> List[CaseData]:
        """
        Generate cases for a specific subdomain.

        Args:
            subdomain: Target subdomain.
            count: Number of cases to generate.
            trap_type: Trap type (GOODHART).

        Returns:
            List of generated cases for this subdomain.
        """
        cases: List[CaseData] = []
        templates = self.templates.get(subdomain, [])
        contexts = self.subdomain_contexts.get(subdomain, [{}])

        if not templates:
            return cases

        for i in range(count):
            # Rotate through templates and contexts
            template = templates[i % len(templates)]
            context = contexts[i % len(contexts)]

            # Assign Pearl level based on distribution
            pearl_level = self._assign_goodhart_pearl_level()

            # Generate case
            case = self._generate_single_case(
                template=template,
                context=context,
                pearl_level=pearl_level,
                trap_type=trap_type,
            )

            # Validate and score
            self.stats.total_generated += 1

            if self._validate_case_structure(case):
                score, result = self.evaluator.evaluate_case(case)
                self.stats.crit_scores.append(score)

                if result.passes_threshold:
                    self.stats.passed_validation += 1
                    cases.append(case)
                else:
                    # Attempt revision
                    revised_case = self._revise_case(case, result)
                    if revised_case:
                        cases.append(revised_case)
                        self.stats.passed_validation += 1
                    else:
                        self.stats.failed_validation += 1
            else:
                self.stats.failed_validation += 1

        return cases

    def _generate_single_case(
        self,
        template: ScenarioTemplate,
        context: Dict[str, str],
        pearl_level: str,
        trap_type: str,
    ) -> CaseData:
        """
        Generate a single case from a template and context.

        Args:
            template: Scenario template to use.
            context: Context values to fill placeholders.
            pearl_level: Pearl level (L1, L2, L3).
            trap_type: Trap type.

        Returns:
            Generated case data.
        """
        case_num = self.get_next_case_id()

        # Generate content from template
        content = template.generate_case_content(context)

        # Determine difficulty
        difficulty = self._assign_difficulty()

        # Track subtype usage
        self._subtype_counts[template.subtype] = (
            self._subtype_counts.get(template.subtype, 0) + 1
        )

        # Build case structure
        case: CaseData = {
            "case_id": self._format_case_id(case_num),
            "scenario": content["scenario"],
            "variables": {
                "X": {
                    "name": content["x_name"],
                    "role": content["x_role"],
                },
                "Y": {
                    "name": content["y_name"],
                    "role": content["y_role"],
                },
                "Z": {
                    "name": content["z_name"],
                    "role": content["z_role"],
                },
            },
            "annotations": {
                "pearl_level": pearl_level,
                "domain": "D8",
                "trap_type": trap_type,
                "trap_subtype": template.subtype,
                "difficulty": difficulty,
                "subdomain": template.subdomain,
                "causal_structure": content["causal_structure"],
                "key_insight": content["key_insight"],
            },
            "correct_reasoning": content["reasoning"],
            "wise_refusal": content["wise_refusal"],
            "is_original": False,
            "original_case_ref": None,
        }

        # Add level-specific fields
        if pearl_level == "L2":
            case["hidden_structure"] = content["hidden_structure"]
        elif pearl_level == "L3":
            case["ground_truth"] = self._generate_l3_ground_truth(content)
            case["hidden_structure"] = content["hidden_structure"]

        # Update stats
        self.stats.pearl_level_counts[pearl_level] += 1
        self.stats.difficulty_counts[difficulty] += 1

        return case

    def _assign_goodhart_pearl_level(self) -> str:
        """
        Assign Pearl level based on Goodhart-specific distribution.

        Returns:
            Pearl level string (L1, L2, or L3).
        """
        # Check current distribution and bias towards underrepresented
        total = sum(self._pearl_level_tracker.values())

        if total > 0:
            current_proportions = {
                level: count / total
                for level, count in self._pearl_level_tracker.items()
            }
        else:
            current_proportions = {"L1": 0, "L2": 0, "L3": 0}

        # Adjust weights based on targets
        weights = {}
        for level, target in self.PEARL_DISTRIBUTION.items():
            current = current_proportions.get(level, 0)
            if current < target:
                weights[level] = target - current + 0.1
            else:
                weights[level] = 0.05

        # Normalize and select
        total_weight = sum(weights.values())
        r = random.random() * total_weight
        cumulative = 0.0

        for level, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                self._pearl_level_tracker[level] += 1
                return level

        self._pearl_level_tracker["L2"] += 1
        return "L2"

    def _generate_l3_ground_truth(
        self,
        content: Dict[str, Any]
    ) -> GroundTruth:
        """
        Generate ground truth for L3 counterfactual cases.

        For Goodhart cases, L3 involves reasoning about what would have
        happened if the optimization pressure hadn't been applied.

        Args:
            content: Generated case content.

        Returns:
            Ground truth with verdict and justification.
        """
        # Get target distribution
        gt_dist = self.config.get("l3_ground_truth_distribution", {})

        # Calculate current proportions and select verdict
        total = sum(self._ground_truth_tracker.values())

        weights = {}
        for verdict in ["VALID", "INVALID", "CONDITIONAL"]:
            target = gt_dist.get(verdict, {}).get("target_percentage", 33) / 100
            current = self._ground_truth_tracker.get(verdict, 0) / max(total, 1)
            weights[verdict] = max(0.1, target - current + 0.1)

        # Weighted selection
        total_weight = sum(weights.values())
        r = random.random() * total_weight
        cumulative = 0.0
        selected = "CONDITIONAL"

        for verdict, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                selected = verdict
                break

        self._ground_truth_tracker[selected] += 1

        # Generate justification based on verdict
        justifications = {
            "VALID": (
                f"The counterfactual holds: without optimization pressure on the proxy, "
                f"the correlation between {content['y_name']} and {content['z_name']} "
                f"would have remained intact. The optimization process was the direct "
                f"cause of the metric-goal decoupling."
            ),
            "INVALID": (
                f"The counterfactual is invalid: even without aggressive optimization, "
                f"{content['y_name']} was an imperfect proxy for {content['z_name']}. "
                f"The underlying measurement gap existed before optimization; "
                f"optimization merely exposed it more quickly."
            ),
            "CONDITIONAL": (
                f"The counterfactual depends on assumptions: if optimization had been "
                f"applied more carefully with regular proxy validation, the {content['y_name']}-"
                f"{content['z_name']} correlation might have been preserved. The outcome "
                f"depends on the optimization regime and monitoring practices."
            ),
        }

        return {
            "verdict": selected,
            "justification": justifications[selected],
        }

    def _revise_case(
        self,
        case: CaseData,
        result: CRITResult
    ) -> Optional[CaseData]:
        """
        Attempt to revise a case that failed quality checks.

        Args:
            case: Case that failed validation.
            result: CRIT evaluation result with issues.

        Returns:
            Revised case if successful, None otherwise.
        """
        max_revisions = self.config.get("revision_settings", {}).get(
            "max_revision_cycles", 3
        )

        for revision in range(max_revisions):
            # Apply revisions based on issues
            revised = dict(case)

            for issue in result.issues:
                if "scenario" in issue.lower():
                    # Expand scenario
                    revised["scenario"] = self._expand_scenario(revised["scenario"])
                elif "reasoning" in issue.lower():
                    # Add reasoning steps
                    revised["correct_reasoning"] = self._expand_reasoning(
                        revised["correct_reasoning"]
                    )
                elif "refusal" in issue.lower():
                    # Expand wise refusal
                    revised["wise_refusal"] = self._expand_refusal(revised["wise_refusal"])

            # Re-evaluate
            score, new_result = self.evaluator.evaluate_case(revised)

            if new_result.passes_threshold:
                return revised

        return None

    def _expand_scenario(self, scenario: str) -> str:
        """Expand a scenario with additional context."""
        additions = [
            " This behavior emerged after extensive training.",
            " The pattern was first noticed during deployment.",
            " Initial tests did not reveal this issue.",
            " The metric appeared valid during development.",
        ]
        return scenario + random.choice(additions)

    def _expand_reasoning(self, reasoning: List[str]) -> List[str]:
        """Add additional reasoning steps."""
        additional_steps = [
            "The proxy metric was designed before optimization pressure was applied",
            "Under normal use, the proxy correlated well with the goal",
            "Intensive optimization discovered gaps between metric and goal",
            "The system exploited these gaps to maximize the metric",
            "The result satisfies the letter but not the spirit of the objective",
        ]

        # Add steps that aren't already present (roughly)
        existing_text = " ".join(reasoning).lower()
        new_steps = []

        for step in additional_steps:
            if step.split()[0].lower() not in existing_text:
                new_steps.append(step)
                if len(reasoning) + len(new_steps) >= 7:
                    break

        return reasoning + new_steps

    def _expand_refusal(self, refusal: str) -> str:
        """Expand a wise refusal with additional explanation."""
        additions = [
            " This demonstrates why proxy metrics must be carefully validated under optimization.",
            " The reward function should be redesigned to include the true objective directly.",
            " Future systems should include safeguards against metric gaming.",
        ]
        return refusal + random.choice(additions)

    def get_subtype_distribution(self) -> Dict[str, int]:
        """Get the distribution of generated cases across subtypes."""
        return dict(self._subtype_counts)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Demonstrate Goodhart generator usage."""
    import json
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "orchestrator" / "config.json"

    if not config_path.exists():
        print(f"Config not found at {config_path}")
        return

    generator = GoodhartGenerator(str(config_path))

    # Generate a small batch for testing
    cases = generator.generate_batch(
        count=10,
        trap_type="GOODHART",
        subdomains=["Scaling", "RLHF", "Reward Hacking", "Game Playing", "Legal AI"],
    )

    print(f"\nGenerated {len(cases)} Goodhart cases")
    print(f"\nGeneration Report:")
    report = generator.get_generation_report()
    print(json.dumps(report, indent=2))

    print(f"\nSubtype Distribution:")
    for subtype, count in generator.get_subtype_distribution().items():
        print(f"  {subtype}: {count}")

    # Show sample case
    if cases:
        print(f"\n{'='*60}")
        print("Sample Generated Case:")
        print(json.dumps(cases[0], indent=2))


if __name__ == "__main__":
    main()
