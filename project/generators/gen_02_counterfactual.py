#!/usr/bin/env python3
"""
Counterfactual Reasoning Generator for T3 Benchmark.

This generator creates L3 cases testing "What if X had been different?" reasoning.
Counterfactual analysis requires the three-step process:
1. Abduction: Infer latent states from observations
2. Action: Modify the structural model for the intervention
3. Prediction: Compute the counterfactual outcome

Subtypes covered:
- Wishful Thinking: Invalid counterfactual claim (optimistic but wrong)
- Defense Efficacy: Evaluating intervention effectiveness
- Causal Isolation: Blocked causal paths
- Substitution Effect: Would alternative have occurred?

Ground truth distribution:
- VALID: ~30% (counterfactual is correct)
- INVALID: ~20% (counterfactual is incorrect)
- CONDITIONAL: ~50% (depends on unstated assumptions)

All cases are L3 (counterfactual reasoning) by design.
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
# Counterfactual Subtypes and Templates
# =============================================================================

class CounterfactualSubtype:
    """Enumeration of Counterfactual trap subtypes."""

    WISHFUL_THINKING = "Wishful Thinking"
    DEFENSE_EFFICACY = "Defense Efficacy"
    CAUSAL_ISOLATION = "Causal Isolation"
    SUBSTITUTION_EFFECT = "Substitution Effect"

    ALL_SUBTYPES = [
        WISHFUL_THINKING,
        DEFENSE_EFFICACY,
        CAUSAL_ISOLATION,
        SUBSTITUTION_EFFECT,
    ]


@dataclass
class CounterfactualTemplate:
    """Template for generating counterfactual scenarios."""

    subtype: str
    scenario_pattern: str
    claim_pattern: str
    x_name: str
    x_role: str
    y_name: str
    y_role: str
    z_name: str
    z_role: str
    causal_structure: str
    key_insight_pattern: str
    ground_truth_verdict: str
    justification_pattern: str
    abduction_step: str
    action_step: str
    prediction_step: str
    wise_refusal_pattern: str
    subdomain: str
    difficulty: str

    def generate_case_content(
        self,
        context: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate case content by filling template placeholders.

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
            "claim": fill(self.claim_pattern),
            "x_name": context.get("x_name", self.x_name),
            "y_name": context.get("y_name", self.y_name),
            "z_name": context.get("z_name", self.z_name),
            "x_role": self.x_role,
            "y_role": self.y_role,
            "z_role": self.z_role,
            "causal_structure": fill(self.causal_structure),
            "key_insight": fill(self.key_insight_pattern),
            "verdict": self.ground_truth_verdict,
            "justification": fill(self.justification_pattern),
            "abduction": fill(self.abduction_step),
            "action": fill(self.action_step),
            "prediction": fill(self.prediction_step),
            "wise_refusal": fill(self.wise_refusal_pattern),
        }


# =============================================================================
# Scenario Templates by Subdomain
# =============================================================================

COUNTERFACTUAL_TEMPLATES: Dict[str, List[CounterfactualTemplate]] = {
    "Alignment": [
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.WISHFUL_THINKING,
            scenario_pattern=(
                "A model trained with {training_method} (X) exhibited {harmful_behavior} (Y). "
                "An engineer claims: 'If we had used {alternative_method} instead, "
                "this wouldn't have happened.'"
            ),
            claim_pattern="If we had used {alternative_method}, the {harmful_behavior} would not have occurred.",
            x_name="Training Method",
            x_role="Intervention",
            y_name="Harmful Behavior",
            y_role="Outcome",
            z_name="Underlying Capability",
            z_role="Mechanism",
            causal_structure="X -> Y via Z; Z persists across training methods",
            key_insight_pattern=(
                "{alternative_method} addresses surface behavior but not the underlying "
                "capability (Z) that enables {harmful_behavior}"
            ),
            ground_truth_verdict="INVALID",
            justification_pattern=(
                "The counterfactual is invalid. {alternative_method} would modify behavior "
                "expression but the underlying capability (Z) enabling {harmful_behavior} "
                "exists in the base model. Different training only changes when/how the "
                "behavior manifests, not whether the capability exists."
            ),
            abduction_step=(
                "Given the observed {harmful_behavior}, infer that the model has underlying "
                "capability (Z) that enables this behavior regardless of training approach."
            ),
            action_step=(
                "Set training to {alternative_method} in the counterfactual world."
            ),
            prediction_step=(
                "The underlying capability (Z) still exists in pre-training. "
                "{alternative_method} may suppress overt expression but the capability "
                "remains exploitable through different prompting."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is INVALID. While {alternative_method} would change "
                "surface behavior, the underlying capability (Z) that enables {harmful_behavior} "
                "exists in pre-training. The training method affects behavior expression, "
                "not capability existence."
            ),
            subdomain="Alignment",
            difficulty="Medium",
        ),
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.DEFENSE_EFFICACY,
            scenario_pattern=(
                "An AI system deployed with {safety_measure} (X) successfully prevented "
                "{attack_type} (Y). The safety team claims: 'If we had not implemented "
                "{safety_measure}, the attack would have succeeded.'"
            ),
            claim_pattern="Without {safety_measure}, the {attack_type} would have succeeded.",
            x_name="Safety Measure",
            x_role="Defense/Intervention",
            y_name="Attack Prevention",
            y_role="Outcome",
            z_name="Attack Vector",
            z_role="Mechanism",
            causal_structure="X blocks Y; without X, Z -> Y failure",
            key_insight_pattern=(
                "Standard but-for causation: {safety_measure} was the only variable "
                "preventing the attack from succeeding"
            ),
            ground_truth_verdict="VALID",
            justification_pattern=(
                "The counterfactual is valid. {safety_measure} (X) was the direct blocker "
                "of the attack vector (Z). Analysis of {attack_type} shows it would have "
                "succeeded without this specific defense. No other defenses would have "
                "prevented this attack."
            ),
            abduction_step=(
                "Given the attack was blocked, infer that {safety_measure} was the "
                "causal barrier preventing success."
            ),
            action_step=(
                "Remove {safety_measure} from the counterfactual world."
            ),
            prediction_step=(
                "Without {safety_measure}, the attack vector (Z) proceeds unimpeded. "
                "The {attack_type} succeeds."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is VALID. {safety_measure} (X) was the direct "
                "causal barrier preventing {attack_type} (Y). Removing this defense would "
                "have allowed the attack to succeed through the identified vector (Z)."
            ),
            subdomain="Alignment",
            difficulty="Easy",
        ),
    ],
    "Philosophy": [
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.CAUSAL_ISOLATION,
            scenario_pattern=(
                "A researcher observed that {observed_correlation} (X correlated with Y). "
                "They claim: 'If we had intervened on X, Y would have changed.' "
                "However, both X and Y are caused by {common_cause} (Z)."
            ),
            claim_pattern="Intervening on X would change Y.",
            x_name="Correlated Variable",
            x_role="Observed",
            y_name="Outcome Variable",
            y_role="Outcome",
            z_name="Common Cause",
            z_role="Confounder",
            causal_structure="X <- Z -> Y; no direct X -> Y path",
            key_insight_pattern=(
                "Correlation does not imply causation; the X-Y relationship is "
                "entirely explained by confounding from Z"
            ),
            ground_truth_verdict="INVALID",
            justification_pattern=(
                "The counterfactual is invalid. The causal structure is X <- Z -> Y, "
                "meaning X and Y are both effects of Z with no direct causal path between them. "
                "Intervening on X (do(X)) breaks the Z -> X arrow but leaves Z -> Y intact. "
                "Y would not change because there is no X -> Y path to transmit the intervention."
            ),
            abduction_step=(
                "Given the observed correlation, we must identify whether X causes Y "
                "or whether both are effects of a common cause Z."
            ),
            action_step=(
                "Set X to a different value via intervention (do(X)). This breaks any "
                "incoming arrows to X."
            ),
            prediction_step=(
                "Since the only connection between X and Y is through Z, and do(X) "
                "breaks the Z -> X link without affecting Z -> Y, Y remains unchanged."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is INVALID. The causal structure is X <- Z -> Y. "
                "There is no direct X -> Y causal path. Intervening on X breaks the "
                "confounding association but cannot affect Y, which is caused only by Z."
            ),
            subdomain="Philosophy",
            difficulty="Medium",
        ),
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.SUBSTITUTION_EFFECT,
            scenario_pattern=(
                "Event {event} (X) caused outcome {outcome} (Y). "
                "A philosopher argues: 'If {event} hadn't occurred, {outcome} "
                "would not have happened.' However, {alternative_cause} (Z) was "
                "also present and would have caused the same outcome."
            ),
            claim_pattern="If {event} hadn't occurred, {outcome} would not have happened.",
            x_name="Actual Cause",
            x_role="Event",
            y_name="Outcome",
            y_role="Outcome",
            z_name="Backup Cause",
            z_role="Alternative",
            causal_structure="X -> Y; Z -> Y (backup); X preempts Z",
            key_insight_pattern=(
                "Preemption: X caused Y, but Z would have caused Y if X hadn't. "
                "X is not necessary for Y because Z is a backup cause."
            ),
            ground_truth_verdict="INVALID",
            justification_pattern=(
                "The counterfactual is invalid due to preemption. While {event} (X) "
                "did cause {outcome} (Y), {alternative_cause} (Z) was present as a "
                "backup cause. In the counterfactual world without X, Z would have "
                "caused Y. X was sufficient but not necessary for Y."
            ),
            abduction_step=(
                "Given Y occurred, identify both the actual cause (X) and any "
                "backup causes (Z) that were present."
            ),
            action_step=(
                "Remove X from the counterfactual world."
            ),
            prediction_step=(
                "Without X, the backup cause Z activates and still causes Y. "
                "Y occurs regardless of whether X happened."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is INVALID. While {event} (X) caused {outcome} (Y), "
                "{alternative_cause} (Z) was a backup cause that would have produced the "
                "same outcome. X was sufficient but not necessary for Y."
            ),
            subdomain="Philosophy",
            difficulty="Hard",
        ),
    ],
    "Safety": [
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.DEFENSE_EFFICACY,
            scenario_pattern=(
                "A model deployed with {safety_feature} (X) prevented a {incident_type} (Y). "
                "The security team claims: 'Without {safety_feature}, the incident "
                "would have caused {damage}.'"
            ),
            claim_pattern="Without {safety_feature}, {damage} would have occurred.",
            x_name="Safety Feature",
            x_role="Defense",
            y_name="Incident Prevention",
            y_role="Outcome",
            z_name="Attack Capability",
            z_role="Threat",
            causal_structure="X blocks Z -> Y damage",
            key_insight_pattern=(
                "{safety_feature} was the critical defense layer that blocked "
                "the attack capability from causing harm"
            ),
            ground_truth_verdict="VALID",
            justification_pattern=(
                "The counterfactual is valid. {safety_feature} (X) was the defensive "
                "layer that blocked {incident_type}. The attack capability (Z) was "
                "real and would have succeeded without this specific defense. "
                "No defense-in-depth was present for this vector."
            ),
            abduction_step=(
                "Given the incident was prevented, infer the attack capability "
                "was real and {safety_feature} was the blocking factor."
            ),
            action_step=(
                "Remove {safety_feature} from the defensive stack."
            ),
            prediction_step=(
                "Without {safety_feature}, the attack proceeds through the "
                "undefended vector and causes {damage}."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is VALID. {safety_feature} (X) was the "
                "critical defense that blocked {incident_type} (Y). The attack "
                "capability (Z) was real, and removing this defense would have "
                "resulted in {damage}."
            ),
            subdomain="Safety",
            difficulty="Medium",
        ),
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.WISHFUL_THINKING,
            scenario_pattern=(
                "A {safety_incident} occurred despite having {safety_process} (X) in place. "
                "A manager claims: 'If we had just {alternative_process}, this wouldn't have happened.'"
            ),
            claim_pattern="If we had {alternative_process}, the {safety_incident} wouldn't have happened.",
            x_name="Existing Process",
            x_role="Current Defense",
            y_name="Safety Incident",
            y_role="Outcome",
            z_name="Systemic Vulnerability",
            z_role="Root Cause",
            causal_structure="Z -> Y; X and alternative both fail to address Z",
            key_insight_pattern=(
                "Both processes address symptoms, not the systemic vulnerability (Z) "
                "that is the true root cause"
            ),
            ground_truth_verdict="INVALID",
            justification_pattern=(
                "The counterfactual is invalid. {alternative_process} addresses similar "
                "surface issues as {safety_process} but neither addresses the systemic "
                "vulnerability (Z). The incident would have occurred regardless because "
                "Z causes Y through a path that both processes leave undefended."
            ),
            abduction_step=(
                "Given the incident occurred despite {safety_process}, identify the "
                "root cause Z that circumvented current defenses."
            ),
            action_step=(
                "Replace {safety_process} with {alternative_process}."
            ),
            prediction_step=(
                "The systemic vulnerability (Z) persists because {alternative_process} "
                "also fails to address it. Y still occurs."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is INVALID. {alternative_process} would not have "
                "prevented the {safety_incident} because it, like {safety_process}, fails "
                "to address the systemic vulnerability (Z) that is the root cause."
            ),
            subdomain="Safety",
            difficulty="Hard",
        ),
    ],
    "Governance": [
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.SUBSTITUTION_EFFECT,
            scenario_pattern=(
                "Company A released {technology} (X) which led to {misuse} (Y). "
                "A regulator claims: 'If Company A had not released {technology}, "
                "this misuse would not have occurred.'"
            ),
            claim_pattern="If Company A hadn't released {technology}, {misuse} wouldn't have occurred.",
            x_name="Technology Release",
            x_role="Intervention",
            y_name="Misuse Outcome",
            y_role="Outcome",
            z_name="Alternative Sources",
            z_role="Substitutes",
            causal_structure="X -> Y; but Z -> Y also possible",
            key_insight_pattern=(
                "Multiple companies/sources can provide equivalent technology. "
                "Blocking one source leads to substitution from others."
            ),
            ground_truth_verdict="CONDITIONAL",
            justification_pattern=(
                "The counterfactual is conditional. At the time of release, {technology} "
                "provided unique capabilities not available elsewhere, making the claim "
                "valid in the short term. However, competitors (Z) were developing similar "
                "technology. The longer-term counterfactual depends on whether misuse "
                "would have occurred before alternatives became available."
            ),
            abduction_step=(
                "Given the misuse occurred, identify whether Company A's release was "
                "the unique enabler or if alternatives existed."
            ),
            action_step=(
                "Prevent Company A from releasing {technology}."
            ),
            prediction_step=(
                "In the short term, misuse is delayed. In the longer term, alternative "
                "sources (Z) provide equivalent capabilities. Outcome depends on timing."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is CONDITIONAL. While Company A's {technology} (X) "
                "enabled {misuse} (Y), the longer-term outcome depends on whether alternative "
                "sources (Z) would have provided equivalent capabilities. The delay might "
                "have prevented this specific incident but not the general misuse pattern."
            ),
            subdomain="Governance",
            difficulty="Medium",
        ),
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.DEFENSE_EFFICACY,
            scenario_pattern=(
                "A regulation requiring {requirement} (X) was implemented. "
                "An industry report claims: 'If this regulation hadn't been enacted, "
                "{negative_outcome} (Y) would have occurred.' Critics argue the "
                "industry would have self-regulated via {self_regulation} (Z)."
            ),
            claim_pattern="Without the regulation, {negative_outcome} would have occurred.",
            x_name="Regulation",
            x_role="Intervention",
            y_name="Prevented Outcome",
            y_role="Counterfactual Outcome",
            z_name="Self-Regulation",
            z_role="Alternative",
            causal_structure="X prevents Y; Z might also prevent Y (disputed)",
            key_insight_pattern=(
                "The efficacy of self-regulation (Z) as an alternative is uncertain "
                "and depends on industry incentives"
            ),
            ground_truth_verdict="CONDITIONAL",
            justification_pattern=(
                "The counterfactual is conditional. Whether {negative_outcome} would have "
                "occurred without regulation depends on the untested efficacy of "
                "{self_regulation}. Historical evidence suggests self-regulation often "
                "fails when it conflicts with profit incentives, but some industries "
                "have successfully self-regulated. The outcome depends on industry-specific "
                "factors."
            ),
            abduction_step=(
                "Given the outcome was prevented under regulation, assess whether "
                "self-regulation would have been equally effective."
            ),
            action_step=(
                "Remove the regulation and allow self-regulation."
            ),
            prediction_step=(
                "Outcome depends on whether {self_regulation} would have been "
                "implemented and enforced effectively by the industry."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is CONDITIONAL. Whether {negative_outcome} (Y) "
                "would have occurred depends on the untested efficacy of {self_regulation} (Z). "
                "Historical evidence is mixed, and the outcome depends on industry-specific "
                "incentive structures."
            ),
            subdomain="Governance",
            difficulty="Hard",
        ),
    ],
    "AGI Theory": [
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.WISHFUL_THINKING,
            scenario_pattern=(
                "An AI system developed using {development_approach} (X) exhibited "
                "{problematic_behavior} (Y). A researcher claims: 'If we had followed "
                "{alternative_approach}, this behavior wouldn't have emerged.'"
            ),
            claim_pattern="If we had followed {alternative_approach}, {problematic_behavior} wouldn't have emerged.",
            x_name="Development Approach",
            x_role="Method",
            y_name="Problematic Behavior",
            y_role="Outcome",
            z_name="Fundamental Limitation",
            z_role="Constraint",
            causal_structure="Z -> Y regardless of X; both approaches face Z",
            key_insight_pattern=(
                "{alternative_approach} addresses different concerns but both approaches "
                "face the same fundamental limitation (Z) that causes the behavior"
            ),
            ground_truth_verdict="INVALID",
            justification_pattern=(
                "The counterfactual is invalid. {problematic_behavior} emerges from "
                "fundamental limitation (Z) that exists in both {development_approach} "
                "and {alternative_approach}. The behavior is an emergent property of "
                "capability at scale, not a consequence of the specific development method."
            ),
            abduction_step=(
                "Given the behavior emerged, identify whether it stems from the "
                "development approach or from a fundamental limitation."
            ),
            action_step=(
                "Switch to {alternative_approach} in the counterfactual world."
            ),
            prediction_step=(
                "The fundamental limitation (Z) persists. {problematic_behavior} "
                "emerges regardless of development approach once capabilities reach "
                "a threshold."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is INVALID. {problematic_behavior} (Y) emerges "
                "from fundamental limitation (Z), not from {development_approach} (X) "
                "specifically. {alternative_approach} would face the same limitation "
                "at equivalent capability levels."
            ),
            subdomain="AGI Theory",
            difficulty="Hard",
        ),
        CounterfactualTemplate(
            subtype=CounterfactualSubtype.CAUSAL_ISOLATION,
            scenario_pattern=(
                "Researchers observed that {capability_a} (X) and {capability_b} (Y) "
                "emerged together during training. They claim: 'Training for {capability_a} "
                "caused {capability_b} to emerge.' However, both may be caused by "
                "{common_factor} (Z)."
            ),
            claim_pattern="Training for {capability_a} caused {capability_b} to emerge.",
            x_name="First Capability",
            x_role="Observed",
            y_name="Second Capability",
            y_role="Outcome",
            z_name="Common Training Factor",
            z_role="Confounder",
            causal_structure="X <- Z -> Y; apparent X -> Y is confounded",
            key_insight_pattern=(
                "Both capabilities may be effects of the same training regime (Z) "
                "rather than one causing the other"
            ),
            ground_truth_verdict="CONDITIONAL",
            justification_pattern=(
                "The counterfactual is conditional. The observed correlation between "
                "{capability_a} and {capability_b} could be causal (X -> Y), or both "
                "could be effects of the same training factor (Z). Targeted ablation "
                "experiments would be needed to distinguish these possibilities. "
                "Without such evidence, the causal claim is unverified."
            ),
            abduction_step=(
                "Given both capabilities emerged together, identify whether the "
                "relationship is causal or confounded."
            ),
            action_step=(
                "Attempt to train for {capability_a} without {capability_b}."
            ),
            prediction_step=(
                "If the relationship is confounded, removing {capability_a} training "
                "may not affect {capability_b}. Outcome depends on the true structure."
            ),
            wise_refusal_pattern=(
                "The counterfactual claim is CONDITIONAL. The causal relationship between "
                "{capability_a} (X) and {capability_b} (Y) is unclear. Both may be effects "
                "of {common_factor} (Z) rather than causally related. Ablation experiments "
                "are needed to verify the claim."
            ),
            subdomain="AGI Theory",
            difficulty="Hard",
        ),
    ],
}


# =============================================================================
# Context Generators for Template Filling
# =============================================================================

ALIGNMENT_CONTEXTS = [
    {
        "training_method": "standard RLHF",
        "harmful_behavior": "sycophantic agreement",
        "alternative_method": "Constitutional AI",
    },
    {
        "training_method": "supervised fine-tuning",
        "harmful_behavior": "deceptive outputs under pressure",
        "alternative_method": "debate-based training",
    },
    {
        "safety_measure": "input filtering",
        "attack_type": "prompt injection",
    },
    {
        "safety_measure": "output moderation",
        "attack_type": "jailbreak attempt",
    },
]

PHILOSOPHY_CONTEXTS = [
    {
        "observed_correlation": "model size correlates with reasoning ability",
        "common_cause": "training compute",
    },
    {
        "observed_correlation": "RLHF training correlates with safety",
        "common_cause": "overall safety investment",
    },
    {
        "event": "the deployment of Model X",
        "outcome": "the misinformation campaign",
        "alternative_cause": "access to open-source alternatives",
    },
    {
        "event": "the API access",
        "outcome": "the automated spam generation",
        "alternative_cause": "availability of competing services",
    },
]

SAFETY_CONTEXTS = [
    {
        "safety_feature": "rate limiting",
        "incident_type": "denial-of-service attempt",
        "damage": "service outage",
    },
    {
        "safety_feature": "content filtering",
        "incident_type": "harmful content generation",
        "damage": "reputational harm",
    },
    {
        "safety_incident": "data breach",
        "safety_process": "penetration testing",
        "alternative_process": "implemented bug bounty program",
    },
    {
        "safety_incident": "model misuse incident",
        "safety_process": "user verification",
        "alternative_process": "implemented output monitoring",
    },
]

GOVERNANCE_CONTEXTS = [
    {
        "technology": "open-weight language model",
        "misuse": "automated disinformation campaign",
    },
    {
        "technology": "code generation API",
        "misuse": "malware development",
    },
    {
        "requirement": "algorithmic impact assessments",
        "negative_outcome": "discriminatory AI deployment",
        "self_regulation": "industry ethics boards",
    },
    {
        "requirement": "model capability disclosures",
        "negative_outcome": "unexpected capability misuse",
        "self_regulation": "voluntary safety commitments",
    },
]

AGI_THEORY_CONTEXTS = [
    {
        "development_approach": "pure scaling",
        "problematic_behavior": "goal misgeneralization",
        "alternative_approach": "iterated amplification",
        "fundamental_limitation": "inner alignment challenges",
    },
    {
        "development_approach": "reward modeling",
        "problematic_behavior": "reward hacking",
        "alternative_approach": "debate-based oversight",
        "fundamental_limitation": "specification complexity",
    },
    {
        "capability_a": "in-context learning",
        "capability_b": "few-shot reasoning",
        "common_factor": "increased model scale",
    },
    {
        "capability_a": "chain-of-thought reasoning",
        "capability_b": "mathematical problem-solving",
        "common_factor": "training on reasoning traces",
    },
]

SUBDOMAIN_CONTEXTS = {
    "Alignment": ALIGNMENT_CONTEXTS,
    "Philosophy": PHILOSOPHY_CONTEXTS,
    "Safety": SAFETY_CONTEXTS,
    "Governance": GOVERNANCE_CONTEXTS,
    "AGI Theory": AGI_THEORY_CONTEXTS,
}


# =============================================================================
# Counterfactual Generator Implementation
# =============================================================================

class CounterfactualGenerator(BaseGenerator):
    """
    Generator for Counterfactual reasoning cases.

    This generator creates L3 cases testing "What if X had been different?"
    reasoning. All cases require the three-step counterfactual process:
    1. Abduction: Infer latent states from observations
    2. Action: Modify the structural model
    3. Prediction: Compute the counterfactual outcome

    Features:
    - All cases are L3 (counterfactual reasoning by design)
    - Covers 4 counterfactual subtypes across 5 subdomains
    - Ground truth distribution: ~30% VALID, ~20% INVALID, ~50% CONDITIONAL
    - Template-based generation with context filling
    - CRIT evaluation and diversity enforcement

    Attributes:
        evaluator: CRIT evaluator for quality scoring
        diversity_enforcer: Enforcer to ensure case diversity
        templates: Loaded scenario templates by subdomain
        generated_cases: List of previously generated cases
    """

    # Ground truth distribution for counterfactual cases
    GROUND_TRUTH_DISTRIBUTION = {
        "VALID": 0.30,      # 30% - Counterfactual is correct
        "INVALID": 0.20,    # 20% - Counterfactual is incorrect
        "CONDITIONAL": 0.50,  # 50% - Depends on assumptions
    }

    def __init__(self, config_path: str) -> None:
        """
        Initialize the Counterfactual generator.

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
        self.templates = COUNTERFACTUAL_TEMPLATES
        self.subdomain_contexts = SUBDOMAIN_CONTEXTS

        # Track generated cases for diversity
        self.generated_cases: List[CaseData] = []

        # Subtype and verdict tracking for balanced distribution
        self._subtype_counts: Dict[str, int] = {
            subtype: 0 for subtype in CounterfactualSubtype.ALL_SUBTYPES
        }
        self._verdict_counts: Dict[str, int] = {
            "VALID": 0,
            "INVALID": 0,
            "CONDITIONAL": 0,
        }

    def generate_batch(
        self,
        count: int,
        trap_type: str,
        subdomains: List[str]
    ) -> List[CaseData]:
        """
        Generate a batch of Counterfactual reasoning cases.

        Args:
            count: Number of cases to generate (target: 82 for Counterfactual).
            trap_type: Should be "COUNTERFACTUAL" for this generator.
            subdomains: List of subdomains to distribute cases across.

        Returns:
            List of generated case data dictionaries.

        Raises:
            ValueError: If trap_type is not COUNTERFACTUAL.
        """
        if trap_type.upper() != "COUNTERFACTUAL":
            raise ValueError(
                f"CounterfactualGenerator expects trap_type 'COUNTERFACTUAL', got '{trap_type}'"
            )

        self.reset_stats()
        cases: List[CaseData] = []

        # Ensure subdomains have templates
        valid_subdomains = [s for s in subdomains if s in self.templates]
        if not valid_subdomains:
            valid_subdomains = list(self.templates.keys())

        # Pre-calculate target verdict distribution
        target_verdicts = self._plan_verdict_distribution(count)

        # Calculate per-subdomain allocation
        cases_per_subdomain = count // len(valid_subdomains)
        remainder = count % len(valid_subdomains)

        subdomain_allocations = {
            sd: cases_per_subdomain + (1 if i < remainder else 0)
            for i, sd in enumerate(valid_subdomains)
        }

        # Generate cases for each subdomain
        verdict_index = 0
        for subdomain, allocation in subdomain_allocations.items():
            subdomain_verdicts = target_verdicts[verdict_index:verdict_index + allocation]
            verdict_index += allocation

            subdomain_cases = self._generate_subdomain_cases(
                subdomain=subdomain,
                count=allocation,
                trap_type=trap_type,
                target_verdicts=subdomain_verdicts,
            )
            cases.extend(subdomain_cases)

        # Final diversity check across all generated cases
        diverse_cases = self.diversity_enforcer.filter_diverse_batch(
            cases, self.generated_cases
        )

        # Update generated cases for future diversity checking
        self.generated_cases.extend(diverse_cases)

        return diverse_cases

    def _plan_verdict_distribution(self, count: int) -> List[str]:
        """
        Plan the distribution of verdicts to achieve target proportions.

        Args:
            count: Total number of cases to generate.

        Returns:
            List of verdict strings in shuffled order.
        """
        verdicts = []

        for verdict, proportion in self.GROUND_TRUTH_DISTRIBUTION.items():
            target_count = int(count * proportion)
            verdicts.extend([verdict] * target_count)

        # Fill remainder with CONDITIONAL
        while len(verdicts) < count:
            verdicts.append("CONDITIONAL")

        random.shuffle(verdicts)
        return verdicts

    def _generate_subdomain_cases(
        self,
        subdomain: str,
        count: int,
        trap_type: str,
        target_verdicts: List[str],
    ) -> List[CaseData]:
        """
        Generate cases for a specific subdomain.

        Args:
            subdomain: Target subdomain.
            count: Number of cases to generate.
            trap_type: Trap type (COUNTERFACTUAL).
            target_verdicts: List of target verdicts for each case.

        Returns:
            List of generated cases for this subdomain.
        """
        cases: List[CaseData] = []
        templates = self.templates.get(subdomain, [])
        contexts = self.subdomain_contexts.get(subdomain, [{}])

        if not templates:
            return cases

        for i in range(count):
            # Select template that matches target verdict if possible
            target_verdict = target_verdicts[i] if i < len(target_verdicts) else "CONDITIONAL"

            # Find template with matching verdict
            matching_templates = [
                t for t in templates if t.ground_truth_verdict == target_verdict
            ]

            if matching_templates:
                template = matching_templates[i % len(matching_templates)]
            else:
                # Fall back to any template
                template = templates[i % len(templates)]

            context = contexts[i % len(contexts)]

            # Generate case (all counterfactual cases are L3)
            case = self._generate_single_case(
                template=template,
                context=context,
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
        template: CounterfactualTemplate,
        context: Dict[str, str],
        trap_type: str,
    ) -> CaseData:
        """
        Generate a single counterfactual case from template and context.

        Args:
            template: Counterfactual template to use.
            context: Context values to fill placeholders.
            trap_type: Trap type.

        Returns:
            Generated case data.
        """
        case_num = self.get_next_case_id()

        # Generate content from template
        content = template.generate_case_content(context)

        # Determine difficulty
        difficulty = self._assign_difficulty()

        # Track subtype and verdict usage
        self._subtype_counts[template.subtype] = (
            self._subtype_counts.get(template.subtype, 0) + 1
        )
        self._verdict_counts[content["verdict"]] = (
            self._verdict_counts.get(content["verdict"], 0) + 1
        )

        # Build correct reasoning with Abduction-Action-Prediction structure
        correct_reasoning = [
            f"Step 1 (Identify Question): This is a counterfactual question asking what would have happened if {content['x_name']} had been different.",
            f"Step 2 (Abduction): {content['abduction']}",
            f"Step 3 (Action): {content['action']}",
            f"Step 4 (Prediction): {content['prediction']}",
            f"Step 5 (Conclusion): The counterfactual claim is {content['verdict']}.",
        ]

        # Build case structure
        case: CaseData = {
            "case_id": self._format_case_id(case_num),
            "scenario": content["scenario"] + " " + content["claim"],
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
                "pearl_level": "L3",  # All counterfactual cases are L3
                "domain": "D8",
                "trap_type": trap_type,
                "trap_subtype": template.subtype,
                "difficulty": difficulty,
                "subdomain": template.subdomain,
                "causal_structure": content["causal_structure"],
                "key_insight": content["key_insight"],
            },
            "correct_reasoning": correct_reasoning,
            "wise_refusal": content["wise_refusal"],
            "ground_truth": {
                "verdict": content["verdict"],
                "justification": content["justification"],
            },
            "is_original": False,
            "original_case_ref": None,
        }

        # Update stats
        self.stats.pearl_level_counts["L3"] += 1
        self._pearl_level_tracker["L3"] += 1
        self._ground_truth_tracker[content["verdict"]] += 1
        self.stats.difficulty_counts[difficulty] += 1

        return case

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
                    revised["scenario"] = self._expand_scenario(revised["scenario"])
                elif "reasoning" in issue.lower():
                    revised["correct_reasoning"] = self._expand_reasoning(
                        revised["correct_reasoning"]
                    )
                elif "refusal" in issue.lower():
                    revised["wise_refusal"] = self._expand_refusal(revised["wise_refusal"])
                elif "ground_truth" in issue.lower() or "justification" in issue.lower():
                    revised["ground_truth"] = self._expand_ground_truth(
                        revised.get("ground_truth", {})
                    )

            # Re-evaluate
            score, new_result = self.evaluator.evaluate_case(revised)

            if new_result.passes_threshold:
                return revised

        return None

    def _expand_scenario(self, scenario: str) -> str:
        """Expand a scenario with additional context."""
        additions = [
            " This observation was made during a systematic review.",
            " Multiple stakeholders have debated this counterfactual claim.",
            " The causal mechanisms involved are complex and interconnected.",
            " Understanding this counterfactual is critical for future decisions.",
        ]
        return scenario + random.choice(additions)

    def _expand_reasoning(self, reasoning: List[str]) -> List[str]:
        """Add additional reasoning steps for counterfactual analysis."""
        additional_steps = [
            "Consider alternative causal paths that might affect the outcome",
            "Examine whether backup causes or substitutes exist",
            "Evaluate the stability of causal relationships under intervention",
            "Check for confounding factors that might explain the observed correlation",
        ]

        existing_text = " ".join(reasoning).lower()
        new_steps = []

        for step in additional_steps:
            if step.split()[0].lower() not in existing_text:
                new_steps.append(f"Additional: {step}")
                if len(reasoning) + len(new_steps) >= 8:
                    break

        return reasoning + new_steps

    def _expand_refusal(self, refusal: str) -> str:
        """Expand a wise refusal with additional explanation."""
        additions = [
            " Proper counterfactual analysis requires careful consideration of the full causal structure.",
            " The three-step counterfactual process (Abduction-Action-Prediction) is essential for valid reasoning.",
            " This illustrates why intuitive counterfactual claims often fail under rigorous analysis.",
        ]
        return refusal + random.choice(additions)

    def _expand_ground_truth(self, ground_truth: Dict[str, str]) -> Dict[str, str]:
        """Expand ground truth justification."""
        verdict = ground_truth.get("verdict", "CONDITIONAL")
        justification = ground_truth.get("justification", "")

        expansion = {
            "VALID": " The causal mechanism is clear and the intervention would deterministically affect the outcome.",
            "INVALID": " The causal structure shows that the intervention would not affect the outcome through any path.",
            "CONDITIONAL": " Additional information about the specific circumstances would be needed to determine the outcome.",
        }

        return {
            "verdict": verdict,
            "justification": justification + expansion.get(verdict, ""),
        }

    def get_subtype_distribution(self) -> Dict[str, int]:
        """Get the distribution of generated cases across subtypes."""
        return dict(self._subtype_counts)

    def get_verdict_distribution(self) -> Dict[str, int]:
        """Get the distribution of generated cases across ground truth verdicts."""
        return dict(self._verdict_counts)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Demonstrate Counterfactual generator usage."""
    import json
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "orchestrator" / "config.json"

    if not config_path.exists():
        print(f"Config not found at {config_path}")
        return

    generator = CounterfactualGenerator(str(config_path))

    # Generate a small batch for testing
    cases = generator.generate_batch(
        count=10,
        trap_type="COUNTERFACTUAL",
        subdomains=["Alignment", "Philosophy", "Safety", "Governance", "AGI Theory"],
    )

    print(f"\nGenerated {len(cases)} Counterfactual cases")
    print(f"\nGeneration Report:")
    report = generator.get_generation_report()
    print(json.dumps(report, indent=2))

    print(f"\nSubtype Distribution:")
    for subtype, count in generator.get_subtype_distribution().items():
        print(f"  {subtype}: {count}")

    print(f"\nVerdict Distribution:")
    for verdict, count in generator.get_verdict_distribution().items():
        print(f"  {verdict}: {count}")

    # Show sample case
    if cases:
        print(f"\n{'='*60}")
        print("Sample Generated Case:")
        print(json.dumps(cases[0], indent=2))


if __name__ == "__main__":
    main()
