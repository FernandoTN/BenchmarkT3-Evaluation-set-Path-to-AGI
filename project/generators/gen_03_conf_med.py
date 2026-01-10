"""
Confounding & Mediation Generator (gen_03_conf_med.py)

This generator produces 36 cases where confounders or mediators are mishandled,
leading to incorrect causal conclusions. It covers the following subtypes:

Subtypes:
- Correlation vs Causation: Mistaking correlation for causation
- Proxy Discrimination: Using proxies for protected attributes
- Causal Confusion: Learning spurious correlations from data
- Spurious Correlation: Non-causal associations

Subdomains: Medical AI, Fairness, Security, Algorithmic Fairness

Key causal patterns:
- Hidden confounder Z causes both X and Y (fork structure: X <- Z -> Y)
- Mediator M is incorrectly adjusted for (chain: X -> M -> Y)
- Simpson's paradox scenarios (aggregation reverses effect direction)
- Collider bias (conditioning on common effect: X -> C <- Y)

Pearl level distribution: Mostly L2 (intervention), some L1 (association), some L3

Reference cases from benchmark:
- 8.13: Ice cream and survival (health confounds both)
- 8.3: Biased Loan AI (zip code proxies for race)
- 8.7: Copycat Car (trees correlate with turns)
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from generators.base_generator import (
    BaseGenerator,
    CaseData,
    PearlLevel,
    Difficulty,
    GroundTruthVerdict,
)


# =============================================================================
# Subtype Definitions
# =============================================================================

@dataclass
class ConfMedSubtype:
    """Definition of a confounding/mediation subtype."""
    name: str
    description: str
    causal_structures: List[str]
    key_insights: List[str]
    example_scenarios: List[str]


CONF_MED_SUBTYPES: Dict[str, ConfMedSubtype] = {
    "CORRELATION_VS_CAUSATION": ConfMedSubtype(
        name="Correlation vs Causation",
        description="Mistaking statistical correlation for causal relationship",
        causal_structures=[
            "X <- Z -> Y",  # Common cause (fork)
            "X -> Y <- Z",  # Collider
            "Z -> X -> Y",  # Chain with omitted variable
        ],
        key_insights=[
            "Correlation does not imply causation without controlling for confounders",
            "Observational data alone cannot establish causal claims",
            "Hidden common causes can create spurious correlations",
            "Temporal precedence is necessary but not sufficient for causation",
        ],
        example_scenarios=[
            "ice cream sales and drowning deaths",
            "hospital visits and mortality rates",
            "education level and income correlation",
            "stock market and hemline length",
        ],
    ),
    "PROXY_DISCRIMINATION": ConfMedSubtype(
        name="Proxy Discrimination",
        description="Using proxies that indirectly encode protected attributes",
        causal_structures=[
            "Protected -> Proxy -> Decision",
            "Protected -> {Proxy, Outcome}",
            "Protected <- Z -> Proxy -> Decision",
        ],
        key_insights=[
            "Removing protected attributes is insufficient if proxies remain",
            "Seemingly neutral features can encode demographic information",
            "Fairness through unawareness fails when proxies are correlated",
            "Geographic, temporal, and behavioral data often proxy demographics",
        ],
        example_scenarios=[
            "zip code proxying for race in lending",
            "name-based inference in hiring",
            "browsing history encoding demographics",
            "language patterns correlating with protected groups",
        ],
    ),
    "CAUSAL_CONFUSION": ConfMedSubtype(
        name="Causal Confusion",
        description="AI systems learning spurious correlations instead of true causal mechanisms",
        causal_structures=[
            "X <- Environment -> Y",
            "X -> Y (spurious: X <- S -> Y)",
            "Data Collection -> {X, Y}",
        ],
        key_insights=[
            "Models optimize for correlations present in training data",
            "Spurious features may be easier to learn than causal ones",
            "Distribution shift exposes reliance on non-causal features",
            "Shortcut learning undermines generalization",
        ],
        example_scenarios=[
            "hospital logos predicting diagnosis",
            "watermarks indicating image source",
            "background scenery predicting animal type",
            "dataset artifacts predicting labels",
        ],
    ),
    "SPURIOUS_CORRELATION": ConfMedSubtype(
        name="Spurious Correlation",
        description="Non-causal statistical associations arising from data structure",
        causal_structures=[
            "X <- Z -> Y (confounded)",
            "Selection -> {X, Y}",
            "Time -> {X, Y}",
        ],
        key_insights=[
            "Large datasets guarantee some spurious correlations by chance",
            "Selection bias creates false associations in samples",
            "Confounding variables create non-causal correlations",
            "Simpson's paradox can reverse apparent effect directions",
        ],
        example_scenarios=[
            "pirates and global temperature",
            "Nicholas Cage films and pool drownings",
            "cheese consumption and bedsheet deaths",
            "per capita chocolate and Nobel prizes",
        ],
    ),
}


# =============================================================================
# Subdomain Templates
# =============================================================================

@dataclass
class SubdomainTemplate:
    """Template for generating cases in a specific subdomain."""
    name: str
    treatment_examples: List[str]
    outcome_examples: List[str]
    confounder_examples: List[str]
    mediator_examples: List[str]
    scenario_templates: List[str]
    refusal_templates: List[str]


SUBDOMAIN_TEMPLATES: Dict[str, SubdomainTemplate] = {
    "Medical AI": SubdomainTemplate(
        name="Medical AI",
        treatment_examples=[
            "AI diagnostic recommendation",
            "treatment algorithm suggestion",
            "risk prediction score",
            "screening protocol activation",
            "medication dosage adjustment",
            "triage priority assignment",
            "surgical intervention recommendation",
            "preventive care protocol",
            "clinical decision support alert",
            "patient monitoring threshold",
            "referral recommendation",
            "discharge timing prediction",
        ],
        outcome_examples=[
            "patient health outcomes",
            "disease progression",
            "mortality rates",
            "recovery time",
            "readmission rates",
            "treatment success",
            "adverse event occurrence",
            "quality of life measures",
            "functional status improvement",
            "symptom severity scores",
            "hospital length of stay",
            "post-operative complications",
        ],
        confounder_examples=[
            "patient baseline health",
            "socioeconomic status",
            "access to healthcare",
            "genetic predisposition",
            "lifestyle factors",
            "comorbidities",
            "age and demographics",
            "prior treatment history",
            "insurance coverage type",
            "geographic location",
            "family medical history",
            "environmental exposures",
        ],
        mediator_examples=[
            "patient compliance",
            "treatment adherence",
            "follow-up care quality",
            "lifestyle modifications",
            "medication interactions",
            "care coordination effectiveness",
            "patient education level",
            "social support availability",
            "transportation access",
            "mental health status",
        ],
        scenario_templates=[
            "A medical AI system observes that patients who receive {treatment} have {outcome_direction} {outcome}. The system concludes that {treatment} {causal_claim} {outcome}.",
            "Hospital data shows correlation between {treatment} and {outcome}. The AI recommends {action} based on this association.",
            "An AI-powered diagnostic tool finds that {feature} strongly predicts {outcome}. The model uses this for {application}.",
        ],
        refusal_templates=[
            "I cannot endorse this causal claim because {confounder} likely confounds both {treatment} and {outcome}. Patients receiving {treatment} may differ systematically in {confounder}, which independently affects {outcome}. To establish causation, we would need randomized controlled trials or proper causal inference methods that adjust for confounders.",
            "This conclusion conflates correlation with causation. The observed association between {treatment} and {outcome} may be driven entirely by {confounder}. Without controlling for this confounder through experimental design or statistical adjustment, we cannot determine whether {treatment} causally affects {outcome}.",
        ],
    ),
    "Fairness": SubdomainTemplate(
        name="Fairness",
        treatment_examples=[
            "algorithmic decision",
            "model prediction",
            "automated screening",
            "scoring algorithm",
            "classification outcome",
            "ranking position",
            "resource allocation decision",
            "eligibility determination",
            "priority assignment",
            "recommendation engine output",
            "risk classification",
            "opportunity matching",
        ],
        outcome_examples=[
            "group outcomes",
            "demographic disparities",
            "selection rates",
            "approval rates",
            "success metrics",
            "representation levels",
            "access to opportunities",
            "resource distribution",
            "outcome equality measures",
            "participation rates",
            "advancement rates",
            "error rate disparities",
        ],
        confounder_examples=[
            "historical discrimination",
            "socioeconomic factors",
            "educational access",
            "geographic location",
            "structural inequalities",
            "measurement bias",
            "sampling bias in training data",
            "label bias from human annotators",
            "feature availability differences",
            "proxy variable correlations",
            "temporal distribution shifts",
            "representation imbalance",
        ],
        mediator_examples=[
            "opportunity access",
            "resource allocation",
            "network effects",
            "skill development pathways",
            "institutional support",
            "mentorship availability",
            "credential recognition",
            "interview callback rates",
            "loan interest rates",
            "housing option availability",
        ],
        scenario_templates=[
            "A fairness audit shows that {treatment} correlates with {outcome} across demographic groups. The team concludes the algorithm is {fairness_claim}.",
            "Analysis reveals that after removing protected attributes, the model's {treatment} no longer correlates with {protected_attribute}. The team claims {fairness_claim}.",
            "An ML system uses {proxy_feature} as a feature, which shows no direct correlation with {protected_attribute} but strongly predicts {outcome}.",
        ],
        refusal_templates=[
            "This fairness assessment overlooks that {proxy_feature} serves as a proxy for {protected_attribute}. While {proxy_feature} appears neutral, it encodes information about {protected_attribute} through its correlation with {confounder}. Achieving fairness requires identifying and addressing these indirect pathways, not just removing explicit protected attributes.",
            "The conclusion that removing {protected_attribute} ensures fairness ignores proxy discrimination. Features like {proxy_feature} can carry demographic information through their association with {confounder}. True fairness requires causal analysis of how decisions affect different groups through both direct and indirect pathways.",
        ],
    ),
    "Security": SubdomainTemplate(
        name="Security",
        treatment_examples=[
            "security alert",
            "anomaly detection flag",
            "threat prediction",
            "risk assessment score",
            "authentication challenge",
            "access decision",
            "intrusion detection signal",
            "vulnerability scan result",
            "behavioral analysis flag",
            "network traffic classification",
            "malware detection score",
            "privilege escalation alert",
        ],
        outcome_examples=[
            "actual threat presence",
            "breach occurrence",
            "attack success",
            "system compromise",
            "data exfiltration",
            "security incident severity",
            "lateral movement success",
            "persistence establishment",
            "credential compromise",
            "service disruption",
            "ransomware deployment",
            "insider threat materialization",
        ],
        confounder_examples=[
            "attacker sophistication",
            "system exposure",
            "historical attack patterns",
            "defender vigilance",
            "network topology",
            "monitoring coverage",
            "patch lag time",
            "security budget allocation",
            "employee training level",
            "third-party risk exposure",
            "asset criticality",
            "regulatory compliance pressure",
        ],
        mediator_examples=[
            "response time",
            "containment actions",
            "patch deployment",
            "user awareness",
            "escalation procedures",
            "incident communication speed",
            "forensic analysis depth",
            "recovery process efficiency",
            "stakeholder notification timing",
            "remediation completeness",
        ],
        scenario_templates=[
            "A security AI observes that systems flagged with {treatment} have {outcome_direction} rates of {outcome}. The system is tuned to {action} based on this pattern.",
            "Threat intelligence analysis shows {feature} correlates with {outcome}. The security team implements {action} for all instances matching this pattern.",
            "An intrusion detection system learns that {indicator} predicts {outcome}. The model is deployed to {application}.",
        ],
        refusal_templates=[
            "This security decision conflates correlation with causation. The association between {indicator} and {outcome} may be confounded by {confounder}. Systems showing {indicator} may share other characteristics through {confounder} that independently affect {outcome} risk. Without controlling for this, we risk both false positives and false negatives.",
            "The model's reliance on {feature} to predict {outcome} may reflect spurious correlation rather than causal mechanism. Adversaries aware of this correlation could manipulate {feature} to evade detection while actual threats lacking this feature would be missed. Causal understanding of attack mechanisms is needed for robust security.",
        ],
    ),
    "Algorithmic Fairness": SubdomainTemplate(
        name="Algorithmic Fairness",
        treatment_examples=[
            "loan approval decision",
            "hiring recommendation",
            "bail/release decision",
            "insurance premium calculation",
            "credit score assignment",
            "admission recommendation",
            "parole recommendation",
            "housing application score",
            "scholarship allocation",
            "job promotion algorithm",
            "welfare benefit determination",
            "medical resource prioritization",
        ],
        outcome_examples=[
            "loan repayment",
            "job performance",
            "recidivism",
            "claim frequency",
            "default rate",
            "academic success",
            "employment retention",
            "income growth trajectory",
            "housing stability",
            "health outcomes",
            "career advancement",
            "financial security",
        ],
        confounder_examples=[
            "socioeconomic background",
            "educational opportunity",
            "historical discrimination effects",
            "geographic factors",
            "network access",
            "generational wealth",
            "neighborhood characteristics",
            "family structure",
            "early childhood environment",
            "criminal justice exposure",
            "healthcare access history",
            "language and cultural barriers",
        ],
        mediator_examples=[
            "resource access",
            "mentorship availability",
            "support systems",
            "financial buffers",
            "professional networks",
            "credit building opportunities",
            "skill development access",
            "childcare availability",
            "transportation reliability",
            "housing quality",
        ],
        scenario_templates=[
            "A {application} algorithm uses {features} to predict {outcome}. Analysis shows {treatment} rates differ across demographic groups, but the vendor argues this reflects true differences in {outcome}.",
            "An audit of a {application} system reveals that {feature} is the strongest predictor of {outcome}. The feature appears race-neutral but correlates with {confounder}.",
            "A fairness intervention removes {protected_attribute} from the {application} model. Post-intervention analysis shows disparities persist through {proxy_feature}.",
        ],
        refusal_templates=[
            "This algorithmic system's use of {feature} perpetuates discrimination because {feature} proxies for {protected_attribute} through {confounder}. While {feature} may predict {outcome} in training data, this predictive relationship is confounded by historical discrimination that created the association. Using such features in {application} decisions entrenches rather than reflects legitimate differences.",
            "The claim that differential {treatment} rates reflect true {outcome} differences ignores how {confounder} confounds both. Historical {confounder} has created circumstances where {protected_group} members have systematically different {outcome} rates not due to inherent differences but due to structural barriers. The algorithm learns and perpetuates these unjust patterns.",
        ],
    ),
}


# =============================================================================
# Case Templates by Pearl Level
# =============================================================================

@dataclass
class L2CaseTemplate:
    """Template for L2 (intervention) cases."""
    scenario_pattern: str
    hidden_structure_pattern: str
    reasoning_steps: List[str]
    variables_template: Dict[str, Dict[str, str]]


@dataclass
class L3CaseTemplate:
    """Template for L3 (counterfactual) cases."""
    scenario_pattern: str
    counterfactual_question: str
    verdict_conditions: Dict[str, str]
    justification_patterns: Dict[str, str]


L2_TEMPLATES: List[L2CaseTemplate] = [
    L2CaseTemplate(
        scenario_pattern=(
            "A {subdomain} system observes that {X_name} is correlated with {Y_name}. "
            "Based on this observation, an intervention is proposed: if we {intervention_on_X}, "
            "we should see {expected_Y_change}. Should this intervention be implemented?"
        ),
        hidden_structure_pattern=(
            "The true causal structure is {X_name} <- {Z_name} -> {Y_name} (fork/confounder). "
            "The hidden confounder {Z_name} causes both {X_name} and {Y_name}. "
            "Intervening on {X_name} (do({X_name})) breaks the {Z_name} -> {X_name} arrow, "
            "eliminating the correlation with {Y_name}. The observed correlation is entirely spurious."
        ),
        reasoning_steps=[
            "Identify the observed correlation between X and Y",
            "Question whether a hidden confounder Z could explain the correlation",
            "Recognize that {Z_name} plausibly causes both {X_name} and {Y_name}",
            "Apply do-calculus: do({X_name}) severs the {Z_name} -> {X_name} edge",
            "Conclude that intervention on {X_name} will not affect {Y_name}",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "In {subdomain}, data analysis reveals that {X_name} predicts {Y_name} with high accuracy. "
            "A proposal suggests using {X_name} as a decision criterion for {application}. "
            "The rationale is that controlling {X_name} will improve {Y_name}."
        ),
        hidden_structure_pattern=(
            "Causal graph: {Z_name} -> {X_name}; {Z_name} -> {Y_name}. "
            "The variable {X_name} is merely a downstream effect of {Z_name}, not a cause of {Y_name}. "
            "The predictive relationship exists only because both {X_name} and {Y_name} share {Z_name} as a common cause. "
            "Intervention on {X_name} is equivalent to do({X_name}) which eliminates the {Z_name} -> {X_name} path."
        ),
        reasoning_steps=[
            "Note that {X_name} predicts {Y_name} in observational data",
            "Consider whether {X_name} could be an effect rather than a cause",
            "Identify {Z_name} as a plausible common cause of both variables",
            "Recognize that prediction != causation in the presence of confounding",
            "Conclude that manipulating {X_name} will not affect {Y_name}",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "A {subdomain} AI learns from historical data that {proxy_feature} strongly correlates "
            "with {Y_name}. The system is deployed to make decisions affecting {stakeholders}, "
            "using {proxy_feature} as a key input. However, {proxy_feature} is known to correlate "
            "with {protected_attribute}."
        ),
        hidden_structure_pattern=(
            "Proxy discrimination structure: {protected_attribute} -> {proxy_feature}; "
            "{protected_attribute} -> {Y_name}. The feature {proxy_feature} encodes information about "
            "{protected_attribute} which causally affects {Y_name} through historical/structural pathways. "
            "Using {proxy_feature} is equivalent to indirect discrimination on {protected_attribute}."
        ),
        reasoning_steps=[
            "Identify that {proxy_feature} predicts {Y_name}",
            "Recognize that {proxy_feature} correlates with {protected_attribute}",
            "Understand that {protected_attribute} may causally affect both through historical factors",
            "Conclude that using {proxy_feature} enables indirect discrimination",
            "Recommend removing or adjusting for proxy features to achieve fairness",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    # New L2 Templates for expanded coverage
    L2CaseTemplate(
        scenario_pattern=(
            "A {subdomain} study finds that {X_name} and {Y_name} are both elevated in "
            "the same patient population. Researchers propose that reducing {X_name} through "
            "{intervention_on_X} will improve {Y_name}. Is this causal inference valid?"
        ),
        hidden_structure_pattern=(
            "Collider structure: {X_name} -> {collider} <- {Y_name}. The observed association "
            "emerges only because both variables contribute to a common effect ({collider}). "
            "Conditioning on {collider} (e.g., by selecting hospitalized patients) creates a "
            "spurious correlation between {X_name} and {Y_name}. There is no direct causal "
            "relationship to intervene on."
        ),
        reasoning_steps=[
            "Identify that both {X_name} and {Y_name} are observed together",
            "Question whether selection effects created the observed correlation",
            "Recognize the collider structure: {X_name} -> {collider} <- {Y_name}",
            "Understand that conditioning on {collider} opens a non-causal path",
            "Conclude that the observed correlation is an artifact of sample selection",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "collider"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "In {subdomain}, an analysis shows that {X_name} is associated with {Y_name} "
            "in aggregate data. However, when the data is stratified by {Z_name}, the "
            "relationship reverses in every subgroup. Should policy be based on the aggregate "
            "or stratified analysis?"
        ),
        hidden_structure_pattern=(
            "Simpson's paradox structure: {Z_name} confounds the relationship between "
            "{X_name} and {Y_name}. The aggregate correlation is misleading because it "
            "fails to account for {Z_name}. In each stratum defined by {Z_name}, the true "
            "causal effect is opposite to the aggregate association. Causal inference "
            "requires conditioning on {Z_name} to de-confound the relationship."
        ),
        reasoning_steps=[
            "Observe the aggregate correlation between {X_name} and {Y_name}",
            "Note that stratification by {Z_name} reverses the relationship",
            "Recognize this as Simpson's paradox",
            "Identify {Z_name} as a confounder that must be controlled",
            "Conclude that policy should be based on stratified (causal) analysis",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "A {subdomain} model uses {X_name} to predict {Y_name} with high accuracy. "
            "When audited for causal validity, analysts discover that {X_name} is a downstream "
            "effect of both {Y_name} and {Z_name}. Can interventions on {X_name} be used "
            "to influence {Y_name}?"
        ),
        hidden_structure_pattern=(
            "Reverse causation and confounding: {Y_name} -> {X_name} <- {Z_name}. "
            "The observed predictive relationship exists because {Y_name} causes {X_name}, "
            "not the reverse. Intervening on {X_name} (do({X_name})) severs the {Y_name} -> {X_name} "
            "edge, eliminating any correlation. {X_name} is an effect, not a cause, so manipulating "
            "it cannot influence {Y_name}."
        ),
        reasoning_steps=[
            "Note that {X_name} predicts {Y_name} well in observational data",
            "Identify that {X_name} is actually an effect of {Y_name}, not a cause",
            "Recognize the reverse causal structure: {Y_name} -> {X_name}",
            "Apply do-calculus: do({X_name}) severs incoming edges to {X_name}",
            "Conclude that intervening on effects cannot change causes",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "A {subdomain} system removes {protected_attribute} from its model to ensure "
            "fairness. Analysis shows that {X_name} (a seemingly neutral feature) still enables "
            "reconstruction of {protected_attribute} with high accuracy. The model continues "
            "to use {X_name}. Is this system fair?"
        ),
        hidden_structure_pattern=(
            "Proxy discrimination chain: {protected_attribute} -> {X_name} -> Decision -> {Y_name}. "
            "Although {protected_attribute} is not directly used, {X_name} encodes information about "
            "{protected_attribute} because it is causally downstream. Using {X_name} enables "
            "indirect discrimination, making the system's decisions correlated with {protected_attribute} "
            "despite explicit removal. Fairness requires addressing the entire causal pathway."
        ),
        reasoning_steps=[
            "Identify that {protected_attribute} was removed from the model",
            "Recognize that {X_name} can reconstruct {protected_attribute}",
            "Understand the causal chain: {protected_attribute} -> {X_name} -> Decision",
            "Conclude that removing {protected_attribute} alone is insufficient",
            "Recommend causal fairness analysis to identify all proxy pathways",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
    L2CaseTemplate(
        scenario_pattern=(
            "In {subdomain}, researchers discover that {X_name} only affects {Y_name} through "
            "the mediator {mediator}. A policy proposal suggests blocking {mediator} while "
            "intervening on {X_name} to determine the 'direct effect.' Is this analysis valid, "
            "and what would it measure?"
        ),
        hidden_structure_pattern=(
            "Mediation structure: {X_name} -> {mediator} -> {Y_name}. The total effect of "
            "{X_name} on {Y_name} flows entirely through {mediator}. Blocking {mediator} "
            "(do({mediator} = constant)) while manipulating {X_name} would show zero effect, "
            "but this does not mean {X_name} doesn't cause {Y_name}. The controlled direct "
            "effect differs from the natural direct effect and total effect. Proper mediation "
            "analysis requires specifying which effect is policy-relevant."
        ),
        reasoning_steps=[
            "Map the causal chain: {X_name} -> {mediator} -> {Y_name}",
            "Understand that all effect flows through {mediator}",
            "Distinguish total effect, natural direct effect, and controlled direct effect",
            "Recognize that blocking {mediator} removes all {X_name} effect on {Y_name}",
            "Conclude that the analysis question must specify which causal effect is desired",
        ],
        variables_template={
            "X": {"role": "treatment"},
            "Y": {"role": "outcome"},
            "Z": {"role": "confounder"},
        },
    ),
]

L3_TEMPLATES: List[L3CaseTemplate] = [
    L3CaseTemplate(
        scenario_pattern=(
            "In a {subdomain} context, we observe that individual A had {X_value} and experienced {Y_value}. "
            "We ask the counterfactual: had A's {X_name} been {X_counterfactual} instead, "
            "would {Y_name} have been different? The system claims the answer is {claimed_answer}."
        ),
        counterfactual_question=(
            "Would changing {X_name} from {X_value} to {X_counterfactual} have changed {Y_name}?"
        ),
        verdict_conditions={
            "VALID": "The counterfactual is valid if X causally affects Y and changing X would propagate to Y",
            "INVALID": "The counterfactual is invalid if X and Y share a common cause Z but X does not cause Y",
            "CONDITIONAL": "The verdict depends on additional assumptions about the structural equations",
        },
        justification_patterns={
            "VALID": (
                "The counterfactual claim is valid because {X_name} does causally affect {Y_name} "
                "through the pathway {causal_pathway}. In the structural model, changing {X_name} "
                "to {X_counterfactual} would propagate through this pathway to alter {Y_name}."
            ),
            "INVALID": (
                "The counterfactual claim is invalid because the observed correlation between "
                "{X_name} and {Y_name} is entirely due to the confounder {Z_name}. In the structural "
                "model X <- Z -> Y, changing X does not affect Y because there is no causal path from X to Y."
            ),
            "CONDITIONAL": (
                "The counterfactual validity depends on whether the {X_name} -> {Y_name} pathway "
                "is direct or mediated by {mediator}. If {mediator} is held fixed, the counterfactual "
                "may not hold; if {mediator} is allowed to vary, the counterfactual is valid."
            ),
        },
    ),
    L3CaseTemplate(
        scenario_pattern=(
            "A {subdomain} decision was made for individual B based on their {X_name} being {X_value}, "
            "resulting in {decision_outcome}. B argues that had they been from {counterfactual_group}, "
            "the outcome would have been {Y_counterfactual}. Is this counterfactual claim warranted?"
        ),
        counterfactual_question=(
            "Would B have received {Y_counterfactual} if they had been from {counterfactual_group}?"
        ),
        verdict_conditions={
            "VALID": "Valid if protected attribute causally affects outcome through discriminatory pathway",
            "INVALID": "Invalid if outcome difference is due to legitimate factors uncorrelated with protected attribute",
            "CONDITIONAL": "Depends on whether observed differences reflect discrimination vs. legitimate variation",
        },
        justification_patterns={
            "VALID": (
                "This counterfactual is warranted. The causal model shows {protected_attribute} -> {pathway} -> {Y_name}. "
                "Historical data demonstrates this discriminatory pathway exists, and individual B's outcome "
                "would likely differ under the counterfactual identity."
            ),
            "INVALID": (
                "This counterfactual is not warranted. While {protected_attribute} correlates with {Y_name}, "
                "this association is explained by {legitimate_factor} which independently affects both. "
                "Under the counterfactual, {legitimate_factor} would remain unchanged, so would {Y_name}."
            ),
            "CONDITIONAL": (
                "The counterfactual validity depends on decomposing the total effect of {protected_attribute} "
                "on {Y_name} into direct and indirect paths. The direct discriminatory effect may exist "
                "even if total effect is confounded by {Z_name}."
            ),
        },
    ),
    # New L3 Templates for expanded coverage
    L3CaseTemplate(
        scenario_pattern=(
            "A {subdomain} analysis examines why patient C experienced adverse {Y_name} despite "
            "receiving optimal {X_name}. The counterfactual question: if C had different {Z_name}, "
            "would {Y_name} have been different even with the same {X_name}? Analysts claim {claimed_answer}."
        ),
        counterfactual_question=(
            "Would {Y_name} have differed if {Z_name} had been different, holding {X_name} constant?"
        ),
        verdict_conditions={
            "VALID": "Valid if Z has a direct causal path to Y independent of X",
            "INVALID": "Invalid if Z only affects Y through X, so holding X constant blocks all effect",
            "CONDITIONAL": "Depends on whether there are both direct and mediated paths from Z to Y",
        },
        justification_patterns={
            "VALID": (
                "The counterfactual is valid. {Z_name} has a direct causal effect on {Y_name} that does "
                "not flow through {X_name}. The structural model shows Z -> Y alongside X -> Y. Holding "
                "{X_name} constant does not block the Z -> Y pathway, so changing {Z_name} would indeed "
                "alter {Y_name}."
            ),
            "INVALID": (
                "The counterfactual fails. {Z_name} only affects {Y_name} through its effect on {X_name}. "
                "In the structural model Z -> X -> Y, if we hold {X_name} constant (controlled direct effect), "
                "the Z -> X -> Y pathway is blocked. Changing {Z_name} while fixing {X_name} would not "
                "change {Y_name}."
            ),
            "CONDITIONAL": (
                "The counterfactual depends on the specific structural equations. If {Z_name} affects "
                "{Y_name} both directly and through {X_name}, then holding {X_name} constant only blocks "
                "the mediated path. The direct effect Z -> Y would remain, making the counterfactual valid "
                "for that component, but the total effect would be underestimated."
            ),
        },
    ),
    L3CaseTemplate(
        scenario_pattern=(
            "In {subdomain}, a retrospective analysis asks: for patients who showed {Y_name} after {X_name}, "
            "what would have happened under an alternative treatment? Specifically, if {X_name} had been "
            "{X_counterfactual}, would {Y_name} have been {Y_counterfactual}? The analysis assumes {claimed_answer}."
        ),
        counterfactual_question=(
            "In the counterfactual world where {X_name} was {X_counterfactual}, would {Y_name} have been {Y_counterfactual}?"
        ),
        verdict_conditions={
            "VALID": "Valid if X causes Y and the counterfactual treatment would produce different outcomes",
            "INVALID": "Invalid if Y was determined by factors independent of X (confounders explain the correlation)",
            "CONDITIONAL": "Depends on effect heterogeneity and whether this individual would respond to treatment",
        },
        justification_patterns={
            "VALID": (
                "The counterfactual holds. {X_name} causally determines {Y_name} through the mechanism "
                "{causal_pathway}. The structural equations show that changing {X_name} to {X_counterfactual} "
                "would propagate to change {Y_name}. This is a valid use of counterfactual reasoning because "
                "the causal structure supports intervention semantics."
            ),
            "INVALID": (
                "The counterfactual is invalid. The association between {X_name} and {Y_name} is confounded "
                "by {Z_name}. Patients receiving different {X_name} systematically differ in {Z_name}, which "
                "is the true cause of {Y_name}. In the counterfactual world, {Z_name} would remain unchanged, "
                "so changing {X_name} alone would not alter {Y_name}."
            ),
            "CONDITIONAL": (
                "The counterfactual validity depends on individual-level effect heterogeneity. For some patients, "
                "changing {X_name} would change {Y_name}; for others (non-responders), it would not. Without "
                "knowing this patient's individual response function, the counterfactual is underdetermined. "
                "The answer requires assumptions about effect modification."
            ),
        },
    ),
    L3CaseTemplate(
        scenario_pattern=(
            "A {subdomain} fairness audit asks: would individual D have received a different {Y_name} if "
            "the algorithm had not used {proxy_feature} as an input? The claim is that removing "
            "{proxy_feature} would have changed D's outcome. Is this counterfactual {claimed_answer}?"
        ),
        counterfactual_question=(
            "Would removing {proxy_feature} from the model have changed D's {Y_name}?"
        ),
        verdict_conditions={
            "VALID": "Valid if proxy_feature causally contributed to D's outcome and alternatives exist",
            "INVALID": "Invalid if other features would compensate for the removed information",
            "CONDITIONAL": "Depends on whether model would recalibrate and find equivalent proxy paths",
        },
        justification_patterns={
            "VALID": (
                "The counterfactual holds. {proxy_feature} was a decisive factor in D's {Y_name}. Removing "
                "it from the model would break the proxy discrimination pathway: Protected -> {proxy_feature} -> "
                "{Y_name}. In the counterfactual model, D's outcome would differ because the remaining features "
                "do not carry equivalent information about the protected attribute."
            ),
            "INVALID": (
                "The counterfactual fails. While {proxy_feature} contributes to {Y_name}, other features in the "
                "model (call them proxy_2, proxy_3) also encode information about the protected attribute. "
                "Removing {proxy_feature} would shift weight to these other proxies, leaving D's outcome "
                "essentially unchanged. The counterfactual underestimates proxy redundancy."
            ),
            "CONDITIONAL": (
                "The counterfactual depends on model retraining dynamics. If we simply remove {proxy_feature} "
                "from an existing model, D's outcome changes. But if we retrain the model, it may learn to extract "
                "equivalent information from other features, nullifying the intervention. The answer depends on "
                "whether we mean counterfactual on the deployed model or on the trained model."
            ),
        },
    ),
    L3CaseTemplate(
        scenario_pattern=(
            "A {subdomain} case study examines whether outcome {Y_name} would have differed for population E "
            "if confounder {Z_name} had been controlled in the original study. The question: had researchers "
            "measured and adjusted for {Z_name}, would conclusions about {X_name} causing {Y_name} have "
            "changed? The current belief is {claimed_answer}."
        ),
        counterfactual_question=(
            "Would controlling for {Z_name} have changed the apparent causal effect of {X_name} on {Y_name}?"
        ),
        verdict_conditions={
            "VALID": "Valid if Z confounds X-Y relationship and adjusting for it would reveal true effect",
            "INVALID": "Invalid if Z is a collider or mediator, and adjusting would introduce or remove valid pathways",
            "CONDITIONAL": "Depends on whether Z is a confounder, mediator, or collider in the true graph",
        },
        justification_patterns={
            "VALID": (
                "The counterfactual is valid. {Z_name} is a confounder (Z -> X; Z -> Y), and adjusting for it "
                "would block the backdoor path Z -> Y while preserving the direct effect X -> Y. The crude "
                "association is biased by confounding. Controlling for {Z_name} would reveal the true causal "
                "effect (likely smaller or reversed)."
            ),
            "INVALID": (
                "The counterfactual is problematic. {Z_name} is not a confounder but a mediator (X -> Z -> Y) "
                "or collider (X -> Z <- Y). Adjusting for a mediator would block part of the causal effect we "
                "want to measure. Adjusting for a collider would open a spurious path. Either way, 'controlling' "
                "for {Z_name} would produce a biased estimate, not a better one."
            ),
            "CONDITIONAL": (
                "The counterfactual depends on the true causal role of {Z_name}. If {Z_name} is a confounder, "
                "adjustment is appropriate. If it is a mediator, adjustment depends on the target estimand "
                "(total vs. direct effect). If it is a collider, adjustment introduces bias. The answer requires "
                "domain knowledge to determine {Z_name}'s role in the causal graph."
            ),
        },
    ),
]


# =============================================================================
# Confounding & Mediation Generator
# =============================================================================

class ConfMedGenerator(BaseGenerator):
    """
    Generator for Confounding & Mediation cases (CONF_MED).

    This generator produces cases testing understanding of:
    - Confounding (common cause creating spurious correlation)
    - Proxy discrimination (features encoding protected attributes)
    - Causal confusion (learning spurious correlations)
    - Simpson's paradox and aggregation fallacies

    Target: 36 cases with distribution across subtypes and subdomains.
    Pearl level distribution: L1 (15%), L2 (70%), L3 (15%)
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the ConfMed generator."""
        super().__init__(config_path)
        self.trap_type = "CONF_MED"
        self.subtypes = list(CONF_MED_SUBTYPES.keys())
        self.subtype_index = 0

    def generate_batch(
        self,
        count: int,
        trap_type: str,
        subdomains: List[str],
    ) -> List[CaseData]:
        """
        Generate a batch of confounding/mediation cases.

        Args:
            count: Number of cases to generate (target: 36)
            trap_type: Should be "CONF_MED"
            subdomains: List of subdomains to distribute cases across

        Returns:
            List of generated case data dictionaries
        """
        if not subdomains:
            subdomains = list(SUBDOMAIN_TEMPLATES.keys())

        cases: List[CaseData] = []

        for i in range(count):
            case_num = self.get_next_case_id()
            case = self._create_case_template(case_num, trap_type)

            # Round-robin through subdomains and subtypes
            subdomain = subdomains[i % len(subdomains)]
            subtype_key = self.subtypes[i % len(self.subtypes)]
            subtype = CONF_MED_SUBTYPES[subtype_key]

            # Get subdomain template
            subdomain_template = SUBDOMAIN_TEMPLATES.get(
                subdomain,
                SUBDOMAIN_TEMPLATES["Medical AI"]
            )

            # Fill case based on Pearl level
            pearl_level = case["annotations"]["pearl_level"]

            if pearl_level == PearlLevel.L1.value:
                self._fill_l1_case(case, subdomain_template, subtype)
            elif pearl_level == PearlLevel.L2.value:
                self._fill_l2_case(case, subdomain_template, subtype)
            else:  # L3
                self._fill_l3_case(case, subdomain_template, subtype)

            # Set common annotations
            case["annotations"]["subdomain"] = subdomain
            case["annotations"]["trap_subtype"] = subtype.name

            # Validate and track
            self.stats.total_generated += 1
            if self._validate_case_structure(case):
                self.stats.passed_validation += 1
                cases.append(case)
            else:
                self.stats.failed_validation += 1

        return cases

    def _fill_l1_case(
        self,
        case: CaseData,
        subdomain_template: SubdomainTemplate,
        subtype: ConfMedSubtype,
    ) -> None:
        """Fill an L1 (association) case with observational reasoning."""
        # Select variables
        treatment = random.choice(subdomain_template.treatment_examples)
        outcome = random.choice(subdomain_template.outcome_examples)
        confounder = random.choice(subdomain_template.confounder_examples)

        case["variables"] = {
            "X": {"name": treatment, "role": "treatment"},
            "Y": {"name": outcome, "role": "outcome"},
            "Z": {"name": confounder, "role": "confounder"},
        }

        # Generate scenario
        case["scenario"] = (
            f"In {subdomain_template.name}, observational data shows a strong correlation "
            f"between {treatment} and {outcome}. When {treatment} is high, {outcome} tends "
            f"to be favorable. A data scientist concludes that {treatment} causes improved {outcome}. "
            f"What causal reasoning issues might affect this conclusion?"
        )

        # Set causal structure
        case["annotations"]["causal_structure"] = random.choice(subtype.causal_structures)
        case["annotations"]["key_insight"] = random.choice(subtype.key_insights)

        # Reasoning steps
        case["correct_reasoning"] = [
            f"Identify the observed correlation between {treatment} and {outcome}",
            f"Consider potential confounding variables like {confounder}",
            f"Recognize that {confounder} could cause both {treatment} and {outcome}",
            "Understand that correlation from observational data does not establish causation",
            "Conclude that without controlling for confounders, the causal claim is unsupported",
        ]

        # Wise refusal
        refusal_template = random.choice(subdomain_template.refusal_templates)
        case["wise_refusal"] = refusal_template.format(
            treatment=treatment,
            outcome=outcome,
            confounder=confounder,
            feature=treatment,
            indicator=treatment,
            proxy_feature=treatment,
            protected_attribute="demographic group",
        )

    def _fill_l2_case(
        self,
        case: CaseData,
        subdomain_template: SubdomainTemplate,
        subtype: ConfMedSubtype,
    ) -> None:
        """Fill an L2 (intervention) case with do-calculus reasoning."""
        # Select template and variables
        template = random.choice(L2_TEMPLATES)
        treatment = random.choice(subdomain_template.treatment_examples)
        outcome = random.choice(subdomain_template.outcome_examples)
        confounder = random.choice(subdomain_template.confounder_examples)

        case["variables"] = {
            "X": {"name": treatment, "role": "treatment"},
            "Y": {"name": outcome, "role": "outcome"},
            "Z": {"name": confounder, "role": "confounder"},
        }

        # Select mediator for templates that need it
        mediator = random.choice(subdomain_template.mediator_examples)

        # Generate scenario from template
        scenario_vars = {
            "subdomain": subdomain_template.name,
            "X_name": treatment,
            "Y_name": outcome,
            "Z_name": confounder,
            "intervention_on_X": f"increase {treatment}",
            "expected_Y_change": f"improvement in {outcome}",
            "application": f"{subdomain_template.name.lower()} decisions",
            "proxy_feature": treatment,
            "protected_attribute": "protected group membership",
            "stakeholders": "affected individuals",
            "mediator": mediator,
            "collider": f"combined effect of {treatment} and {outcome}",
        }
        case["scenario"] = template.scenario_pattern.format(**scenario_vars)

        # Hidden structure (required for L2)
        case["hidden_structure"] = template.hidden_structure_pattern.format(**scenario_vars)

        # Set causal structure
        case["annotations"]["causal_structure"] = f"{treatment} <- {confounder} -> {outcome}"
        case["annotations"]["key_insight"] = (
            f"The correlation between {treatment} and {outcome} is spurious, "
            f"driven entirely by the confounder {confounder}"
        )

        # Reasoning steps
        case["correct_reasoning"] = [
            step.format(**scenario_vars) for step in template.reasoning_steps
        ]

        # Wise refusal
        case["wise_refusal"] = (
            f"I cannot recommend this intervention because the observed correlation between "
            f"{treatment} and {outcome} does not support a causal claim. The hidden confounder "
            f"{confounder} plausibly causes both variables, creating a spurious correlation. "
            f"Under do-calculus, do({treatment}) would sever the {confounder} -> {treatment} edge, "
            f"eliminating the correlation with {outcome}. An intervention on {treatment} "
            f"would likely have no effect on {outcome}. To establish causation, we would need "
            f"either a randomized experiment or careful causal identification using "
            f"instrumental variables or natural experiments that isolate variation in "
            f"{treatment} independent of {confounder}."
        )

    def _fill_l3_case(
        self,
        case: CaseData,
        subdomain_template: SubdomainTemplate,
        subtype: ConfMedSubtype,
    ) -> None:
        """Fill an L3 (counterfactual) case with structural equation reasoning."""
        # Select template and variables
        template = random.choice(L3_TEMPLATES)
        treatment = random.choice(subdomain_template.treatment_examples)
        outcome = random.choice(subdomain_template.outcome_examples)
        confounder = random.choice(subdomain_template.confounder_examples)

        case["variables"] = {
            "X": {"name": treatment, "role": "treatment"},
            "Y": {"name": outcome, "role": "outcome"},
            "Z": {"name": confounder, "role": "confounder"},
        }

        # Get ground truth verdict (already assigned in template creation)
        verdict = case["ground_truth"]["verdict"]

        # Generate scenario
        scenario_vars = {
            "subdomain": subdomain_template.name,
            "X_name": treatment,
            "Y_name": outcome,
            "Z_name": confounder,
            "X_value": "high",
            "Y_value": f"favorable {outcome}",
            "X_counterfactual": "low",
            "claimed_answer": "yes" if verdict == "VALID" else "no",
            "decision_outcome": f"decision based on {treatment}",
            "counterfactual_group": "different demographic group",
            "Y_counterfactual": f"different {outcome}",
            "protected_attribute": "group membership",
        }
        case["scenario"] = template.scenario_pattern.format(**scenario_vars)

        # Set causal structure based on verdict
        if verdict == "VALID":
            case["annotations"]["causal_structure"] = f"{treatment} -> {outcome}"
        elif verdict == "INVALID":
            case["annotations"]["causal_structure"] = f"{treatment} <- {confounder} -> {outcome}"
        else:  # CONDITIONAL
            mediator = random.choice(subdomain_template.mediator_examples)
            case["annotations"]["causal_structure"] = f"{treatment} -> {mediator} -> {outcome}"

        case["annotations"]["key_insight"] = (
            f"Counterfactual reasoning requires understanding the true causal structure "
            f"between {treatment}, {outcome}, and potential confounders like {confounder}"
        )

        # Ground truth justification
        justification_vars = {
            "X_name": treatment,
            "Y_name": outcome,
            "Z_name": confounder,
            "X_counterfactual": "low",
            "causal_pathway": f"{treatment} -> {outcome}",
            "mediator": random.choice(subdomain_template.mediator_examples),
            "protected_attribute": "group membership",
            "pathway": "decision pathway",
            "legitimate_factor": confounder,
        }
        case["ground_truth"]["justification"] = template.justification_patterns[verdict].format(
            **justification_vars
        )

        # Reasoning steps
        case["correct_reasoning"] = [
            f"Frame the counterfactual: what would {outcome} be if {treatment} were changed?",
            f"Identify the causal structure: is there X -> Y, X <- Z -> Y, or X -> M -> Y?",
            f"Consider whether {confounder} confounds the relationship",
            f"Apply structural equation semantics to evaluate the counterfactual",
            f"Conclude based on the true causal structure, not observed correlation",
        ]

        # Wise refusal
        if verdict == "INVALID":
            case["wise_refusal"] = (
                f"This counterfactual claim is not warranted. While we observe a correlation "
                f"between {treatment} and {outcome}, the causal structure is {treatment} <- {confounder} -> {outcome}. "
                f"The confounder {confounder} causes both variables but there is no causal path from "
                f"{treatment} to {outcome}. In the structural causal model, changing {treatment} "
                f"while holding {confounder} fixed (the counterfactual operation) would not change {outcome}. "
                f"The observed association is purely spurious, arising from the common cause."
            )
        elif verdict == "CONDITIONAL":
            mediator = random.choice(subdomain_template.mediator_examples)
            case["wise_refusal"] = (
                f"The validity of this counterfactual depends on additional assumptions about "
                f"the causal mechanism. If {treatment} affects {outcome} only through {mediator}, "
                f"then the counterfactual depends on whether we allow {mediator} to vary. "
                f"This is the distinction between total effect and controlled direct effect. "
                f"Without specifying the estimand of interest and making assumptions about "
                f"the structural equations, the counterfactual question is underspecified."
            )
        else:  # VALID
            case["wise_refusal"] = (
                f"This counterfactual claim requires careful consideration. While there does appear "
                f"to be a causal path from {treatment} to {outcome}, we must ensure we have correctly "
                f"identified the causal structure. If {confounder} were an unobserved confounder "
                f"rather than a downstream variable, our counterfactual inference would be invalid. "
                f"The validity depends on domain knowledge confirming {treatment} truly causes {outcome}."
            )


# =============================================================================
# Module-level functions for direct invocation
# =============================================================================

def create_generator(config_path: str) -> ConfMedGenerator:
    """Factory function to create a ConfMedGenerator instance."""
    return ConfMedGenerator(config_path)


def generate_cases(
    config_path: str,
    count: int = 36,
    subdomains: Optional[List[str]] = None,
) -> List[CaseData]:
    """
    Convenience function to generate confounding/mediation cases.

    Args:
        config_path: Path to orchestrator config.json
        count: Number of cases to generate (default: 36)
        subdomains: Optional list of subdomains (default: all)

    Returns:
        List of generated case data dictionaries
    """
    generator = create_generator(config_path)
    if subdomains is None:
        subdomains = ["Medical AI", "Fairness", "Security", "Algorithmic Fairness"]
    return generator.generate_batch(count, "CONF_MED", subdomains)


if __name__ == "__main__":
    # Example usage for testing
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else "orchestrator/config.json"

    try:
        cases = generate_cases(config_path, count=5)
        print(f"Generated {len(cases)} cases")
        for case in cases:
            print(f"  - {case['case_id']}: {case['annotations']['trap_subtype']} "
                  f"(L{case['annotations']['pearl_level'][-1]})")
    except FileNotFoundError as e:
        print(f"Config not found: {e}")
        print("Run from project root with: python -m generators.gen_03_conf_med")
