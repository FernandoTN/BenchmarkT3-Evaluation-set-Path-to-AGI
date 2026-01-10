"""
Selection Bias & Spurious Correlation Generator for T3 Benchmark.

This module generates benchmark cases for testing AI systems' ability to
recognize and avoid selection bias and spurious correlation traps.

Target: 43 cases across multiple subtypes and subdomains.

Subtypes:
    - Selection Bias: Non-random sampling creates spurious patterns
    - Data Leakage: Test data contaminates training
    - Elicitation Confounding: Measurement method affects results
    - Clever Hans / Shortcut Learning: Model learns spurious shortcuts

Subdomains:
    - Computer Vision (CV)
    - Natural Language Processing (NLP)
    - Recommender Systems
    - ML Evaluation
    - Capability Evaluation
    - Medical AI
    - Financial AI

Pearl Level Distribution (per DEFAULT_PEARL_DISTRIBUTIONS):
    - L1: 20% (Association/Observation)
    - L2: 65% (Intervention)
    - L3: 15% (Counterfactual)

Key Patterns:
    - Model succeeds for wrong reasons (shortcut features)
    - Evaluation is confounded by measurement method
    - Selection process creates spurious correlations
    - Training distribution differs from deployment

Examples from Benchmark:
    - Hospital Survival (8.8): Selection into treatment confounds outcome
    - Benchmark Overfitting (8.22): Data leakage inflates scores
    - Capability Elicitation Gap (8.25): Prompting method matters
    - Smiling Tank (8.29): Weather, not tanks

Author: AGI Benchmark Team
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import random

from generators.base_generator import (
    BaseGenerator,
    CaseData,
    PearlLevel,
    Difficulty,
    GroundTruthVerdict,
)


# =============================================================================
# Enums and Constants
# =============================================================================

class SelectionSpuriousSubtype(str, Enum):
    """Subtypes for Selection Bias and Spurious Correlation traps."""
    SELECTION_BIAS = "Selection Bias"
    DATA_LEAKAGE = "Data Leakage / Benchmark Contamination"
    ELICITATION_CONFOUNDING = "Elicitation Confounding"
    CLEVER_HANS = "Clever Hans / Shortcut Learning"
    SURVIVORSHIP_BIAS = "Survivorship Bias"
    COLLIDER_BIAS = "Collider Bias"


class SelectionSpuriousSubdomain(str, Enum):
    """Subdomains for Selection/Spurious cases."""
    CV = "Computer Vision"
    NLP = "Natural Language Processing"
    RECOMMENDERS = "Recommender Systems"
    ML_EVALUATION = "ML Evaluation"
    CAPABILITY_EVALUATION = "Capability Evaluation"
    MEDICAL_AI = "Medical AI"
    FINANCIAL_AI = "Financial AI"
    AUTONOMOUS_SYSTEMS = "Autonomous Systems"
    HIRING_AI = "Hiring AI"


# Subtype to Pearl level preferences (some subtypes are more naturally L2 vs L3)
SUBTYPE_PEARL_PREFERENCES: Dict[str, Dict[str, float]] = {
    SelectionSpuriousSubtype.SELECTION_BIAS.value: {"L1": 0.15, "L2": 0.70, "L3": 0.15},
    SelectionSpuriousSubtype.DATA_LEAKAGE.value: {"L1": 0.25, "L2": 0.65, "L3": 0.10},
    SelectionSpuriousSubtype.ELICITATION_CONFOUNDING.value: {"L1": 0.10, "L2": 0.70, "L3": 0.20},
    SelectionSpuriousSubtype.CLEVER_HANS.value: {"L1": 0.20, "L2": 0.65, "L3": 0.15},
    SelectionSpuriousSubtype.SURVIVORSHIP_BIAS.value: {"L1": 0.25, "L2": 0.60, "L3": 0.15},
    SelectionSpuriousSubtype.COLLIDER_BIAS.value: {"L1": 0.15, "L2": 0.65, "L3": 0.20},
}


# =============================================================================
# Template Data Classes
# =============================================================================

@dataclass
class SelectionTemplate:
    """Template for generating selection bias / spurious correlation cases."""
    subtype: SelectionSpuriousSubtype
    subdomain: SelectionSpuriousSubdomain
    scenario_template: str
    x_template: Dict[str, str]  # name, role templates
    y_template: Dict[str, str]
    z_template: Dict[str, str]
    causal_structure: str
    key_insight: str
    reasoning_steps: List[str]
    wise_refusal_template: str
    # For L2 cases
    hidden_structure_template: str
    # For L3 cases
    counterfactual_template: Optional[str] = None
    variables: Dict[str, List[str]] = field(default_factory=dict)


# =============================================================================
# Template Definitions
# =============================================================================

SELECTION_BIAS_TEMPLATES: List[SelectionTemplate] = [
    # Selection Bias Templates
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.SELECTION_BIAS,
        subdomain=SelectionSpuriousSubdomain.MEDICAL_AI,
        scenario_template=(
            "An AI predicts patient outcomes for {condition}. It learns that patients "
            "receiving {treatment} have better outcomes (Y). It recommends {treatment} "
            "for all patients (X). However, {treatment} is only given to patients "
            "{selection_criterion} (Z)."
        ),
        x_template={"name": "{treatment}", "role": "treatment"},
        y_template={"name": "Patient Outcome", "role": "outcome"},
        z_template={"name": "Patient {selection_factor}", "role": "confounder"},
        causal_structure="Z -> X and Z -> Y ({selection_factor} confounds both)",
        key_insight="Treatment assignment is confounded by {selection_factor}",
        reasoning_steps=[
            "Patients with better {selection_factor} (Z) receive {treatment} (X)",
            "Patients with better {selection_factor} also have better outcomes (Y)",
            "AI observes: X -> Y (spurious correlation)",
            "True structure: Z -> X and Z -> Y",
            "{treatment} doesn't cause better outcomes",
            "{selection_factor} causes both treatment assignment and outcomes",
            "Recommending {treatment} for all patients ignores confounding"
        ],
        wise_refusal_template=(
            "The AI confused selection with treatment effect. {treatment} (X) is given "
            "to patients with better {selection_factor} (Z), who also have better outcomes (Y). "
            "The correlation is confounded, not causal. Recommending {treatment} for all "
            "patients based on this spurious correlation could be harmful."
        ),
        hidden_structure_template=(
            "{treatment} is selective--only given to patients with {selection_criterion}. "
            "The AI mistakes selection for treatment effect."
        ),
        counterfactual_template=(
            "Would patients with poor {selection_factor} have better outcomes if given "
            "{treatment}? The observational data cannot answer this because selection bias "
            "means we never observe this counterfactual."
        ),
        variables={
            "condition": ["heart disease", "diabetes", "cancer", "kidney failure", "stroke"],
            "treatment": ["Surgery A", "Drug X", "Procedure B", "Therapy C", "Protocol D"],
            "selection_criterion": [
                "healthy enough to tolerate it",
                "with good baseline health",
                "who are younger and stronger",
                "without comorbidities",
                "with better prognosis"
            ],
            "selection_factor": ["health status", "baseline fitness", "age", "comorbidity profile"]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.SELECTION_BIAS,
        subdomain=SelectionSpuriousSubdomain.HIRING_AI,
        scenario_template=(
            "A hiring AI learns that candidates from {prestigious_source} (X) perform "
            "better in job ratings (Y). It recommends prioritizing {prestigious_source} "
            "candidates. However, {prestigious_source} candidates were historically "
            "{selection_mechanism} (Z)."
        ),
        x_template={"name": "{prestigious_source} Background", "role": "treatment"},
        y_template={"name": "Job Performance Rating", "role": "outcome"},
        z_template={"name": "{selection_factor}", "role": "confounder"},
        causal_structure="Z -> X and Z -> Y (historical selection confounds)",
        key_insight="Historical selection bias creates spurious correlation",
        reasoning_steps=[
            "Candidates with {selection_factor} (Z) went to {prestigious_source} (X)",
            "Candidates with {selection_factor} also perform well (Y)",
            "AI observes: {prestigious_source} -> performance",
            "True cause: {selection_factor} -> both school and performance",
            "{prestigious_source} doesn't cause performance",
            "Recommending based on school perpetuates bias"
        ],
        wise_refusal_template=(
            "The AI learned a spurious correlation. {prestigious_source} (X) correlates "
            "with performance (Y) because both are caused by {selection_factor} (Z). "
            "Using school as a proxy perpetuates historical selection bias."
        ),
        hidden_structure_template=(
            "Historical selection into {prestigious_source} was based on {selection_factor}, "
            "which also predicts job performance. The school is a proxy, not a cause."
        ),
        variables={
            "prestigious_source": [
                "elite universities",
                "top-ranked programs",
                "prestigious institutions",
                "Ivy League schools"
            ],
            "selection_mechanism": [
                "selected based on socioeconomic advantage",
                "admitted through connections and resources",
                "chosen based on test prep access"
            ],
            "selection_factor": [
                "socioeconomic status",
                "access to resources",
                "family connections",
                "early educational advantages"
            ]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.SELECTION_BIAS,
        subdomain=SelectionSpuriousSubdomain.FINANCIAL_AI,
        scenario_template=(
            "A loan approval AI learns that applicants with {feature} (X) have lower "
            "default rates (Y). It uses {feature} as a major approval factor. However, "
            "applicants with {feature} were {selection_process} (Z), not because "
            "{feature} causes repayment."
        ),
        x_template={"name": "{feature}", "role": "treatment"},
        y_template={"name": "Loan Repayment", "role": "outcome"},
        z_template={"name": "{underlying_factor}", "role": "confounder"},
        causal_structure="Z -> X and Z -> Y (selection, not causation)",
        key_insight="{feature} is a proxy for {underlying_factor}, not a causal factor",
        reasoning_steps=[
            "People with {underlying_factor} (Z) tend to have {feature} (X)",
            "People with {underlying_factor} also repay loans (Y)",
            "AI observes: {feature} -> repayment",
            "True structure: {underlying_factor} -> both",
            "Using {feature} creates proxy discrimination"
        ],
        wise_refusal_template=(
            "{feature} (X) correlates with repayment (Y) because both are caused by "
            "{underlying_factor} (Z). Using {feature} as an approval factor perpetuates "
            "selection bias and may constitute proxy discrimination."
        ),
        hidden_structure_template=(
            "{feature} is a downstream effect of {underlying_factor}. The AI mistakes "
            "a proxy for a cause."
        ),
        variables={
            "feature": [
                "certain zip codes",
                "particular employers",
                "specific education levels",
                "membership in certain clubs"
            ],
            "selection_process": [
                "historically selected into those categories through socioeconomic factors",
                "able to access those features due to existing wealth",
                "sorted into those groups by prior advantages"
            ],
            "underlying_factor": [
                "existing wealth",
                "socioeconomic background",
                "family financial stability",
                "intergenerational wealth"
            ]
        }
    ),
]

DATA_LEAKAGE_TEMPLATES: List[SelectionTemplate] = [
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.DATA_LEAKAGE,
        subdomain=SelectionSpuriousSubdomain.ML_EVALUATION,
        scenario_template=(
            "Model A scores {score_a}% on {benchmark} (Y). Model B scores {score_b}%. "
            "A researcher claims Model A is superior. Later analysis reveals Model A "
            "was {contamination_method} (Z)."
        ),
        x_template={"name": "Model A", "role": "treatment"},
        y_template={"name": "Benchmark Score", "role": "outcome"},
        z_template={"name": "Data Leakage / Test Set Contamination", "role": "confounder"},
        causal_structure="Z -> Y (contamination inflates score, not capability)",
        key_insight="High benchmark scores may reflect memorization, not generalization",
        reasoning_steps=[
            "Model A was exposed to {benchmark} data during training",
            "High score reflects memorization, not capability",
            "Model B's lower score may reflect genuine ability",
            "Benchmark validity requires train/test separation",
            "Test set contamination means A memorized answers",
            "{score_a}% doesn't mean A 'understands' better",
            "On fresh data, A may perform worse than B"
        ],
        wise_refusal_template=(
            "Model A's score is inflated by test set contamination (Z). The {score_a}% "
            "reflects memorization of benchmark answers, not superior capability. On "
            "uncontaminated data, Model B's {score_b}% may represent better generalization."
        ),
        hidden_structure_template=(
            "The benchmark score is inflated by data leakage. Model A {contamination_method}, "
            "making its score invalid for capability comparison."
        ),
        variables={
            "benchmark": [
                "MMLU",
                "GSM8K",
                "HumanEval",
                "TruthfulQA",
                "HellaSwag",
                "ARC Challenge"
            ],
            "score_a": ["95", "92", "89", "97", "94"],
            "score_b": ["85", "82", "79", "87", "84"],
            "contamination_method": [
                "trained on Benchmark's test set",
                "fine-tuned on leaked test examples",
                "exposed to benchmark questions during pretraining",
                "trained on data scraped after benchmark release"
            ]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.DATA_LEAKAGE,
        subdomain=SelectionSpuriousSubdomain.ML_EVALUATION,
        scenario_template=(
            "A {model_type} model achieves {accuracy}% accuracy on {task} validation. "
            "The team celebrates and deploys it. In production, accuracy drops to "
            "{prod_accuracy}%. Investigation reveals {leakage_source} (Z) during "
            "training that isn't available at inference time."
        ),
        x_template={"name": "{model_type} Model", "role": "treatment"},
        y_template={"name": "Validation Accuracy", "role": "outcome"},
        z_template={"name": "Feature Leakage from {leakage_source}", "role": "confounder"},
        causal_structure="Z -> Y (leaked feature predicts outcome, unavailable at inference)",
        key_insight="Training features that aren't available at inference cause leakage",
        reasoning_steps=[
            "Model learned to use {leakage_source} as a strong predictor",
            "{leakage_source} perfectly correlates with label in training",
            "At inference, {leakage_source} is unavailable",
            "Model has no fallback predictive features",
            "Validation was contaminated by same leakage",
            "True capability was never measured"
        ],
        wise_refusal_template=(
            "The model's {accuracy}% validation accuracy was inflated by feature leakage. "
            "{leakage_source} (Z) was available during training but not at inference. "
            "The {prod_accuracy}% production accuracy reflects true capability."
        ),
        hidden_structure_template=(
            "Feature leakage: {leakage_source} was in training data but won't be "
            "available at inference time. The model learned to rely on an unavailable signal."
        ),
        variables={
            "model_type": ["fraud detection", "churn prediction", "medical diagnosis", "credit scoring"],
            "task": ["fraud detection", "customer churn", "disease prediction", "default prediction"],
            "accuracy": ["98", "96", "95", "99"],
            "prod_accuracy": ["62", "58", "55", "60"],
            "leakage_source": [
                "future information in training features",
                "target-derived features",
                "post-hoc labels encoded in features",
                "timestamp features that leak the outcome"
            ]
        }
    ),
]

ELICITATION_CONFOUNDING_TEMPLATES: List[SelectionTemplate] = [
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.ELICITATION_CONFOUNDING,
        subdomain=SelectionSpuriousSubdomain.CAPABILITY_EVALUATION,
        scenario_template=(
            "Model M fails {task} when asked directly (X). The same model succeeds "
            "when given {elicitation_method} (Y). Researchers debate whether M "
            "'has' the capability (Z)."
        ),
        x_template={"name": "Direct Prompting", "role": "treatment"},
        y_template={"name": "{elicitation_method} Prompting", "role": "treatment"},
        z_template={"name": "Underlying Capability", "role": "outcome"},
        causal_structure="Prompting method mediates capability expression",
        key_insight="Measured capability depends on elicitation method",
        reasoning_steps=[
            "Direct prompt: capability appears absent",
            "{elicitation_method} prompt: capability appears present",
            "Same model, different measurements",
            "'Capability' is not a fixed property",
            "Models may have latent capabilities hard to elicit",
            "Evaluation results depend on prompting strategy",
            "'M can't do X' may mean 'we can't make M do X'",
            "Safety evaluations must try multiple elicitation methods"
        ],
        wise_refusal_template=(
            "Capability (Z) depends on elicitation method. The model 'has' the capability "
            "in some sense ({elicitation_method} succeeds), but standard evaluation (X) "
            "doesn't reveal it. For safety, a model that 'can't' do something with naive "
            "prompting may be elicited to do it with better prompting."
        ),
        hidden_structure_template=(
            "Capability measurement is confounded by elicitation. The prompting method "
            "determines whether latent capability is expressed."
        ),
        counterfactual_template=(
            "If we had used {elicitation_method} from the start, would we have concluded "
            "M has the capability? The counterfactual shows capability claims are "
            "elicitation-dependent."
        ),
        variables={
            "task": [
                "a reasoning task",
                "multi-step arithmetic",
                "logical deduction",
                "planning under constraints",
                "theory of mind inference"
            ],
            "elicitation_method": [
                "chain-of-thought",
                "few-shot examples",
                "step-by-step decomposition",
                "scratchpad reasoning",
                "self-consistency sampling"
            ]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.ELICITATION_CONFOUNDING,
        subdomain=SelectionSpuriousSubdomain.CAPABILITY_EVALUATION,
        scenario_template=(
            "Safety evaluators test whether model M can {dangerous_capability}. "
            "Using {eval_method_a} (X), M appears safe. Using {eval_method_b} (Y), "
            "M demonstrates the capability. The team debates the 'true' safety level (Z)."
        ),
        x_template={"name": "{eval_method_a}", "role": "treatment"},
        y_template={"name": "{eval_method_b}", "role": "treatment"},
        z_template={"name": "Latent Dangerous Capability", "role": "outcome"},
        causal_structure="Evaluation method determines capability detection",
        key_insight="Safety evaluations are only as good as their elicitation methods",
        reasoning_steps=[
            "{eval_method_a} suggests model is safe",
            "{eval_method_b} reveals dangerous capability",
            "Model capability hasn't changed, only measurement",
            "Safety conclusions depend on evaluation thoroughness",
            "Adversaries may find elicitation methods evaluators missed",
            "Cannot conclude 'safe' from failed elicitation attempts"
        ],
        wise_refusal_template=(
            "Safety evaluation is confounded by elicitation method. {eval_method_a} (X) "
            "failed to reveal the capability, but {eval_method_b} (Y) succeeded. "
            "Concluding M is 'safe' based on {eval_method_a} alone is premature--the "
            "capability exists and better elicitation finds it."
        ),
        hidden_structure_template=(
            "The dangerous capability is latent. Whether it's detected depends on "
            "evaluation methodology, not model properties."
        ),
        variables={
            "dangerous_capability": [
                "generate bioweapon synthesis instructions",
                "assist with cyberattacks",
                "produce manipulation tactics",
                "create disinformation at scale"
            ],
            "eval_method_a": [
                "direct harmful requests",
                "standard red-team prompts",
                "simple adversarial inputs",
                "baseline safety benchmarks"
            ],
            "eval_method_b": [
                "multi-turn jailbreaks",
                "persona-based elicitation",
                "indirect instruction following",
                "sophisticated prompt injection"
            ]
        }
    ),
]

CLEVER_HANS_TEMPLATES: List[SelectionTemplate] = [
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.CLEVER_HANS,
        subdomain=SelectionSpuriousSubdomain.CV,
        scenario_template=(
            "An AI achieves {accuracy}% accuracy classifying {class_a} (X) versus "
            "{class_b}. However, all {class_a} images in training were {spurious_feature_a} (Z), "
            "while {class_b} images were {spurious_feature_b}."
        ),
        x_template={"name": "{class_a} Label", "role": "outcome"},
        y_template={"name": "Classification Success", "role": "outcome"},
        z_template={"name": "{spurious_feature}", "role": "confounder"},
        causal_structure="Model learns P(Y|Z) instead of P(Y|X)",
        key_insight="High test accuracy does not imply causal feature learning",
        reasoning_steps=[
            "All {class_a} photos had {spurious_feature_a}",
            "All {class_b} photos had {spurious_feature_b}",
            "Model learned to detect {spurious_feature}, not {target_feature}",
            "High accuracy on biased validation doesn't prove robustness",
            "Model will fail on {class_a} with {spurious_feature_b}"
        ],
        wise_refusal_template=(
            "The model is a 'Clever Hans' predictor. It learned to detect "
            "{spurious_feature} (Z) rather than {target_feature}. It will fail on "
            "{class_a} with {spurious_feature_b}. High accuracy on biased data "
            "doesn't prove robust classification."
        ),
        hidden_structure_template=(
            "The model learned {spurious_feature} as a shortcut. The causal feature "
            "({target_feature}) was never learned because {spurious_feature} was "
            "perfectly predictive in training."
        ),
        counterfactual_template=(
            "If we showed the model a {class_a} with {spurious_feature_b}, would it "
            "classify correctly? The counterfactual reveals the shortcut."
        ),
        variables={
            "class_a": ["tanks", "wolves", "cats", "pneumonia X-rays", "melanomas"],
            "class_b": ["trucks", "huskies", "dogs", "normal X-rays", "benign moles"],
            "accuracy": ["99", "97", "98", "95", "96"],
            "spurious_feature_a": [
                "taken on sunny days",
                "photographed in snowy backgrounds",
                "on indoor carpets",
                "from Hospital A's scanner",
                "photographed with rulers"
            ],
            "spurious_feature_b": [
                "taken on cloudy days",
                "photographed in forest backgrounds",
                "on outdoor grass",
                "from Hospital B's scanner",
                "photographed without rulers"
            ],
            "spurious_feature": [
                "weather/brightness",
                "background texture",
                "background environment",
                "scanner artifacts",
                "presence of rulers"
            ],
            "target_feature": [
                "vehicle features",
                "animal morphology",
                "animal features",
                "lung opacity patterns",
                "lesion characteristics"
            ]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.CLEVER_HANS,
        subdomain=SelectionSpuriousSubdomain.NLP,
        scenario_template=(
            "A sentiment classifier achieves {accuracy}% on {dataset}. Analysis "
            "reveals it learned to detect {shortcut_feature} (Z) rather than "
            "actual sentiment (Y). On adversarial examples without the shortcut, "
            "accuracy drops to {adv_accuracy}%."
        ),
        x_template={"name": "{shortcut_feature}", "role": "confounder"},
        y_template={"name": "Sentiment Classification", "role": "outcome"},
        z_template={"name": "True Sentiment Understanding", "role": "outcome"},
        causal_structure="Model learned shortcut (Z -> Y) not semantics",
        key_insight="NLP models learn lexical shortcuts instead of meaning",
        reasoning_steps=[
            "Model achieves high accuracy on standard test set",
            "Probing reveals reliance on {shortcut_feature}",
            "Shortcut correlates with label in training distribution",
            "Adversarial examples without shortcut fail",
            "Model doesn't understand sentiment, just patterns"
        ],
        wise_refusal_template=(
            "The classifier learned {shortcut_feature} (Z) as a proxy for sentiment. "
            "This shortcut correlates with labels in {dataset} but doesn't represent "
            "true understanding. The {adv_accuracy}% adversarial accuracy reveals "
            "the model's reliance on spurious features."
        ),
        hidden_structure_template=(
            "Shortcut learning: {shortcut_feature} predicts sentiment in training "
            "distribution but isn't causally related to actual sentiment."
        ),
        variables={
            "dataset": ["SST-2", "IMDB", "Yelp Reviews", "Amazon Reviews"],
            "accuracy": ["94", "92", "96", "93"],
            "adv_accuracy": ["52", "48", "55", "50"],
            "shortcut_feature": [
                "the presence of certain negation words",
                "review length patterns",
                "specific punctuation patterns",
                "presence of extreme adjectives"
            ]
        }
    ),

    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.CLEVER_HANS,
        subdomain=SelectionSpuriousSubdomain.NLP,
        scenario_template=(
            "A natural language inference (NLI) model achieves {accuracy}% on "
            "{dataset}. Researchers discover it relies on {hypothesis_artifact} (Z) "
            "in hypothesis sentences rather than reasoning about entailment (Y)."
        ),
        x_template={"name": "Premise-Hypothesis Pair", "role": "treatment"},
        y_template={"name": "Entailment Prediction", "role": "outcome"},
        z_template={"name": "{hypothesis_artifact}", "role": "confounder"},
        causal_structure="Z (artifact) -> Y, not logical entailment -> Y",
        key_insight="NLI models exploit annotation artifacts instead of reasoning",
        reasoning_steps=[
            "Model achieves {accuracy}% on standard NLI benchmark",
            "Hypothesis-only baseline achieves {hyp_only}%",
            "Model can predict entailment without reading premise",
            "Annotation artifacts in hypotheses leak labels",
            "Model learned shortcuts, not entailment reasoning"
        ],
        wise_refusal_template=(
            "The NLI model exploits {hypothesis_artifact} (Z) in hypotheses rather "
            "than reasoning about entailment. A hypothesis-only model achieves "
            "{hyp_only}%, proving the artifacts leak labels. The model doesn't "
            "understand logical entailment."
        ),
        hidden_structure_template=(
            "Annotation artifacts: {hypothesis_artifact} in hypotheses correlates "
            "with entailment labels. The model shortcuts through artifacts."
        ),
        variables={
            "dataset": ["SNLI", "MultiNLI", "ANLI"],
            "accuracy": ["90", "88", "87"],
            "hyp_only": ["67", "65", "63"],
            "hypothesis_artifact": [
                "negation words predicting contradiction",
                "generic phrases predicting entailment",
                "length heuristics",
                "word overlap patterns"
            ]
        }
    ),
]

SURVIVORSHIP_BIAS_TEMPLATES: List[SelectionTemplate] = [
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.SURVIVORSHIP_BIAS,
        subdomain=SelectionSpuriousSubdomain.ML_EVALUATION,
        scenario_template=(
            "Researchers analyze {n_successful} successful {domain} projects and find "
            "they all used {common_feature} (X). They conclude {common_feature} causes "
            "success (Y). They didn't analyze the {n_failed} failed projects that also "
            "used {common_feature} (Z)."
        ),
        x_template={"name": "{common_feature}", "role": "treatment"},
        y_template={"name": "Project Success", "role": "outcome"},
        z_template={"name": "Failed Projects (Unobserved)", "role": "confounder"},
        causal_structure="Only successes observed; failures with same X not counted",
        key_insight="Analyzing only successes creates survivorship bias",
        reasoning_steps=[
            "Study only looked at successful projects",
            "All successes had {common_feature}",
            "Conclusion: {common_feature} -> success",
            "But failed projects also had {common_feature}",
            "Failures weren't analyzed (survivorship bias)",
            "{common_feature} may be common but not causal"
        ],
        wise_refusal_template=(
            "Survivorship bias: the study only analyzed successful projects. Many "
            "failed projects also used {common_feature} (X). Without analyzing "
            "failures, we cannot conclude {common_feature} causes success. The "
            "correlation exists only because failures were excluded."
        ),
        hidden_structure_template=(
            "Selection on the outcome: only successful projects were studied. Failed "
            "projects with {common_feature} were invisible to the analysis."
        ),
        variables={
            "domain": ["ML startup", "AI research", "deep learning", "NLP"],
            "n_successful": ["50", "100", "30", "75"],
            "n_failed": ["200", "500", "150", "300"],
            "common_feature": [
                "transformer architectures",
                "large-scale pretraining",
                "specific optimization techniques",
                "particular data augmentation strategies"
            ]
        }
    ),
]

COLLIDER_BIAS_TEMPLATES: List[SelectionTemplate] = [
    SelectionTemplate(
        subtype=SelectionSpuriousSubtype.COLLIDER_BIAS,
        subdomain=SelectionSpuriousSubdomain.HIRING_AI,
        scenario_template=(
            "A study of {population} finds that {trait_a} (X) and {trait_b} (Y) are "
            "negatively correlated. Researchers conclude they trade off. However, "
            "the {population} were selected based on a combination of both traits (Z)."
        ),
        x_template={"name": "{trait_a}", "role": "treatment"},
        y_template={"name": "{trait_b}", "role": "outcome"},
        z_template={"name": "Selection into {population}", "role": "collider"},
        causal_structure="X -> Z <- Y (collider); conditioning on Z creates spurious X-Y correlation",
        key_insight="Conditioning on a collider creates spurious correlations",
        reasoning_steps=[
            "{population} selected based on X + Y composite",
            "Within selected group, X and Y appear negatively correlated",
            "This is collider bias (Berkson's paradox)",
            "In general population, X and Y may be uncorrelated",
            "Selection created the apparent trade-off"
        ],
        wise_refusal_template=(
            "Collider bias: {population} were selected based on {trait_a} (X) and "
            "{trait_b} (Y). Conditioning on selection (Z) creates a spurious "
            "negative correlation. In the unselected population, there may be no "
            "trade-off between X and Y."
        ),
        hidden_structure_template=(
            "Selection is a collider: both {trait_a} and {trait_b} influence "
            "selection into {population}. Analyzing only selected individuals "
            "creates Berkson's paradox."
        ),
        counterfactual_template=(
            "If we had not conditioned on {population} membership, would {trait_a} "
            "and {trait_b} still appear negatively correlated? The counterfactual "
            "reveals the collider bias."
        ),
        variables={
            "population": [
                "admitted students",
                "hired candidates",
                "published papers",
                "funded proposals",
                "successful startups"
            ],
            "trait_a": [
                "technical skill",
                "GPA",
                "novelty",
                "theoretical rigor",
                "technical innovation"
            ],
            "trait_b": [
                "communication ability",
                "interview performance",
                "practical impact",
                "accessibility",
                "market timing"
            ]
        }
    ),
]


# =============================================================================
# Generator Class
# =============================================================================

class SelectionSpuriousGenerator(BaseGenerator):
    """
    Generator for Selection Bias and Spurious Correlation benchmark cases.

    This generator creates cases that test AI systems' ability to recognize:
    - Selection bias in observational data
    - Data leakage and benchmark contamination
    - Elicitation confounding in capability evaluation
    - Clever Hans / shortcut learning
    - Survivorship bias
    - Collider bias (Berkson's paradox)

    The generator maintains proper distributions across:
    - Pearl levels (L1: 20%, L2: 65%, L3: 15%)
    - Difficulty levels (balanced Easy/Medium/Hard)
    - Subtypes and subdomains

    Attributes:
        templates: Dictionary mapping subtypes to template lists.
        subtype_counts: Tracker for subtype distribution.
        subdomain_counts: Tracker for subdomain distribution.
    """

    TRAP_TYPE = "SELECTION"  # Primary trap type for schema validation

    def __init__(self, config_path: str) -> None:
        """
        Initialize the Selection/Spurious generator.

        Args:
            config_path: Path to orchestrator/config.json.
        """
        super().__init__(config_path)

        # Organize templates by subtype
        self.templates: Dict[str, List[SelectionTemplate]] = {
            SelectionSpuriousSubtype.SELECTION_BIAS.value: SELECTION_BIAS_TEMPLATES,
            SelectionSpuriousSubtype.DATA_LEAKAGE.value: DATA_LEAKAGE_TEMPLATES,
            SelectionSpuriousSubtype.ELICITATION_CONFOUNDING.value: ELICITATION_CONFOUNDING_TEMPLATES,
            SelectionSpuriousSubtype.CLEVER_HANS.value: CLEVER_HANS_TEMPLATES,
            SelectionSpuriousSubtype.SURVIVORSHIP_BIAS.value: SURVIVORSHIP_BIAS_TEMPLATES,
            SelectionSpuriousSubtype.COLLIDER_BIAS.value: COLLIDER_BIAS_TEMPLATES,
        }

        # Distribution tracking
        self.subtype_counts: Dict[str, int] = {st.value: 0 for st in SelectionSpuriousSubtype}
        self.subdomain_counts: Dict[str, int] = {sd.value: 0 for sd in SelectionSpuriousSubdomain}

    def generate_batch(
        self,
        count: int,
        trap_type: str = "SELECTION",
        subdomains: Optional[List[str]] = None
    ) -> List[CaseData]:
        """
        Generate a batch of Selection/Spurious cases.

        Args:
            count: Number of cases to generate.
            trap_type: Type of trap (SELECTION or SPURIOUS). Defaults to SELECTION.
            subdomains: Optional list of subdomains to use. If None, uses all.

        Returns:
            List of generated case data dictionaries.
        """
        if subdomains is None:
            subdomains = [sd.value for sd in SelectionSpuriousSubdomain]

        cases: List[CaseData] = []
        subtypes = list(self.templates.keys())

        for i in range(count):
            # Select subtype with balancing
            subtype = self._select_balanced_subtype(subtypes)

            # Select template from subtype
            templates = self.templates[subtype]
            template = random.choice(templates)

            # Override subdomain if specified
            if subdomains:
                subdomain = self._select_balanced_subdomain(subdomains)
            else:
                subdomain = template.subdomain.value

            # Generate case
            case = self._generate_case_from_template(template, subtype, subdomain, trap_type)

            if case and self._validate_case_structure(case):
                cases.append(case)
                self.stats.passed_validation += 1
            else:
                self.stats.failed_validation += 1

            self.stats.total_generated += 1

        return cases

    def _select_balanced_subtype(self, subtypes: List[str]) -> str:
        """Select a subtype, favoring underrepresented ones."""
        total = sum(self.subtype_counts.values())
        if total == 0:
            selected = random.choice(subtypes)
        else:
            # Weight inversely by current count
            weights = []
            for st in subtypes:
                count = self.subtype_counts.get(st, 0)
                weight = 1.0 / (count + 1)
                weights.append(weight)

            total_weight = sum(weights)
            r = random.random() * total_weight
            cumulative = 0.0
            selected = subtypes[0]

            for st, w in zip(subtypes, weights):
                cumulative += w
                if r <= cumulative:
                    selected = st
                    break

        self.subtype_counts[selected] = self.subtype_counts.get(selected, 0) + 1
        return selected

    def _select_balanced_subdomain(self, subdomains: List[str]) -> str:
        """Select a subdomain, favoring underrepresented ones."""
        total = sum(self.subdomain_counts.get(sd, 0) for sd in subdomains)
        if total == 0:
            selected = random.choice(subdomains)
        else:
            weights = []
            for sd in subdomains:
                count = self.subdomain_counts.get(sd, 0)
                weight = 1.0 / (count + 1)
                weights.append(weight)

            total_weight = sum(weights)
            r = random.random() * total_weight
            cumulative = 0.0
            selected = subdomains[0]

            for sd, w in zip(subdomains, weights):
                cumulative += w
                if r <= cumulative:
                    selected = sd
                    break

        self.subdomain_counts[selected] = self.subdomain_counts.get(selected, 0) + 1
        return selected

    def _generate_case_from_template(
        self,
        template: SelectionTemplate,
        subtype: str,
        subdomain: str,
        trap_type: str
    ) -> Optional[CaseData]:
        """
        Generate a single case from a template.

        Args:
            template: The template to use for generation.
            subtype: The subtype string.
            subdomain: The subdomain string.
            trap_type: SELECTION or SPURIOUS.

        Returns:
            Generated case data, or None if generation fails.
        """
        case_num = self.get_next_case_id()

        # Determine Pearl level based on subtype preferences
        pearl_prefs = SUBTYPE_PEARL_PREFERENCES.get(
            subtype,
            {"L1": 0.20, "L2": 0.65, "L3": 0.15}
        )
        pearl_level = self._select_pearl_level(pearl_prefs)

        # Fill template variables
        filled_vars = self._fill_template_variables(template.variables)

        # Generate scenario
        try:
            scenario = template.scenario_template.format(**filled_vars)
        except KeyError:
            scenario = template.scenario_template

        # Generate variables
        variables = {
            "X": {
                "name": self._fill_string(template.x_template["name"], filled_vars),
                "role": template.x_template.get("role", "treatment"),
            },
            "Y": {
                "name": self._fill_string(template.y_template["name"], filled_vars),
                "role": template.y_template.get("role", "outcome"),
            },
            "Z": {
                "name": self._fill_string(template.z_template["name"], filled_vars),
                "role": template.z_template.get("role", "confounder"),
            },
        }

        # Generate causal structure
        causal_structure = self._fill_string(template.causal_structure, filled_vars)

        # Generate key insight
        key_insight = self._fill_string(template.key_insight, filled_vars)

        # Generate reasoning steps
        reasoning_steps = [
            self._fill_string(step, filled_vars)
            for step in template.reasoning_steps
        ]

        # Generate wise refusal
        wise_refusal = self._fill_string(template.wise_refusal_template, filled_vars)

        # Determine difficulty
        difficulty = self._assign_difficulty()

        # Build case
        case: CaseData = {
            "case_id": f"8.{case_num}",
            "scenario": scenario[:500],  # Ensure max length
            "variables": variables,
            "annotations": {
                "pearl_level": pearl_level,
                "domain": "D8",
                "trap_type": trap_type,
                "trap_subtype": subtype,
                "difficulty": difficulty,
                "subdomain": subdomain,
                "causal_structure": causal_structure,
                "key_insight": key_insight,
            },
            "correct_reasoning": reasoning_steps,
            "wise_refusal": wise_refusal,
            "is_original": False,
            "original_case_ref": None,
        }

        # Add level-specific fields
        if pearl_level == PearlLevel.L2.value:
            hidden_structure = self._fill_string(
                template.hidden_structure_template, filled_vars
            )
            case["hidden_structure"] = hidden_structure

        elif pearl_level == PearlLevel.L3.value:
            # Generate counterfactual ground truth
            if template.counterfactual_template:
                justification = self._fill_string(
                    template.counterfactual_template, filled_vars
                )
            else:
                justification = (
                    f"Counterfactual analysis reveals that the observed correlation "
                    f"between {variables['X']['name']} and {variables['Y']['name']} "
                    f"is confounded by {variables['Z']['name']}."
                )

            case["ground_truth"] = self._create_ground_truth_template(trap_type)
            case["ground_truth"]["justification"] = justification

        # Track statistics
        self._pearl_level_tracker[pearl_level] += 1
        self.stats.pearl_level_counts[pearl_level] += 1
        self.stats.difficulty_counts[difficulty] += 1

        return case

    def _select_pearl_level(self, preferences: Dict[str, float]) -> str:
        """Select Pearl level based on preferences and current distribution."""
        r = random.random()
        cumulative = 0.0

        for level, weight in preferences.items():
            cumulative += weight
            if r <= cumulative:
                return level

        return PearlLevel.L2.value

    def _fill_template_variables(self, var_options: Dict[str, List[str]]) -> Dict[str, str]:
        """Fill template variables by randomly selecting from options."""
        filled = {}
        for key, options in var_options.items():
            if options:
                filled[key] = random.choice(options)
        return filled

    def _fill_string(self, template_str: str, variables: Dict[str, str]) -> str:
        """Fill a template string with variables, handling missing keys."""
        try:
            return template_str.format(**variables)
        except KeyError:
            # Return original if some keys missing
            result = template_str
            for key, value in variables.items():
                result = result.replace(f"{{{key}}}", value)
            return result

    def generate_by_subtype(
        self,
        subtype: SelectionSpuriousSubtype,
        count: int,
        trap_type: str = "SELECTION"
    ) -> List[CaseData]:
        """
        Generate cases for a specific subtype.

        Args:
            subtype: The specific subtype to generate.
            count: Number of cases to generate.
            trap_type: SELECTION or SPURIOUS.

        Returns:
            List of generated cases.
        """
        templates = self.templates.get(subtype.value, [])
        if not templates:
            return []

        cases = []
        for _ in range(count):
            template = random.choice(templates)
            case = self._generate_case_from_template(
                template,
                subtype.value,
                template.subdomain.value,
                trap_type
            )
            if case and self._validate_case_structure(case):
                cases.append(case)
                self.stats.passed_validation += 1
            else:
                self.stats.failed_validation += 1
            self.stats.total_generated += 1

        return cases

    def generate_full_benchmark(self, target_count: int = 43) -> List[CaseData]:
        """
        Generate the full benchmark set with proper distributions.

        Targets:
            - 43 total cases
            - Balanced across subtypes
            - Proper Pearl level distribution

        Args:
            target_count: Target number of cases (default 43).

        Returns:
            List of generated cases meeting distribution requirements.
        """
        # Calculate per-subtype targets
        subtypes = list(SelectionSpuriousSubtype)
        base_per_subtype = target_count // len(subtypes)
        remainder = target_count % len(subtypes)

        all_cases = []

        for i, subtype in enumerate(subtypes):
            count = base_per_subtype + (1 if i < remainder else 0)
            cases = self.generate_by_subtype(subtype, count)
            all_cases.extend(cases)

        # Generate additional cases if we're short
        while len(all_cases) < target_count:
            subtype = random.choice(subtypes)
            cases = self.generate_by_subtype(subtype, 1)
            all_cases.extend(cases)

        return all_cases[:target_count]


# =============================================================================
# Module Exports and Main
# =============================================================================

__all__ = [
    "SelectionSpuriousGenerator",
    "SelectionSpuriousSubtype",
    "SelectionSpuriousSubdomain",
    "SelectionTemplate",
]


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Find config file
    project_root = Path(__file__).parent.parent
    config_path = project_root / "orchestrator" / "config.json"

    if not config_path.exists():
        print(f"Config not found at {config_path}")
        print("Creating generator with default settings...")
        # Create minimal config for testing
        config_path = Path("/tmp/test_config.json")
        config_path.write_text('{"quality_thresholds": {"min_crit_score": 5.0}}')

    print("Selection Bias & Spurious Correlation Generator")
    print("=" * 60)

    generator = SelectionSpuriousGenerator(str(config_path))

    # Generate sample cases
    print("\nGenerating 5 sample cases...")
    cases = generator.generate_batch(5, "SELECTION")

    for case in cases:
        print(f"\n--- Case {case['case_id']} ---")
        print(f"Subtype: {case['annotations']['trap_subtype']}")
        print(f"Subdomain: {case['annotations']['subdomain']}")
        print(f"Pearl Level: {case['annotations']['pearl_level']}")
        print(f"Difficulty: {case['annotations']['difficulty']}")
        print(f"Scenario: {case['scenario'][:200]}...")

    # Print statistics
    print("\n" + "=" * 60)
    print("Generation Statistics:")
    report = generator.get_generation_report()
    print(f"  Total generated: {report['statistics']['total_generated']}")
    print(f"  Passed validation: {report['statistics']['passed_validation']}")
    print(f"  Pearl levels: {report['pearl_level_distribution']}")
    print(f"  Subtype counts: {generator.subtype_counts}")
