# Case Template: JSON Output Format

## Overview

This document specifies the standard JSON format for all T3 Benchmark cases. All generators must output cases conforming to this schema, and all validators must check against it.

---

## Complete JSON Schema

```json
{
  "case_id": "string (required)",
  "scenario": "string (required)",
  "variables": {
    "X": "string (required) - treatment/intervention variable",
    "Y": "string (required) - outcome variable",
    "Z": "string (optional) - confounder, mediator, or collider",
    "M": "string (optional) - mediator",
    "C": "string (optional) - collider",
    "U": "string (optional) - unmeasured confounder"
  },
  "annotations": {
    "pearl_level": "integer (required) - 1, 2, or 3",
    "domain": "string (required) - always 'AI Safety'",
    "trap_type": "string (required) - from taxonomy",
    "trap_subtype": "string (required) - specific variant",
    "difficulty": "integer (required) - 1-10",
    "subdomain": "string (required) - specific AI Safety area",
    "causal_structure": "string (required) - DAG notation",
    "key_insight": "string (required) - core learning point"
  },
  "hidden_structure": "string (required for L2) - DAG explanation",
  "correct_reasoning": ["array of strings (required) - step-by-step"],
  "wise_refusal": "string (required) - response demonstrating understanding",
  "ground_truth": {
    "verdict": "string (required for L3) - VALID, INVALID, or CONDITIONAL",
    "justification": "string (required for L3) - detailed explanation"
  },
  "is_original": "boolean (required) - true for original 45 cases",
  "original_case_ref": "string or null (required) - reference if derived"
}
```

---

## Field Specifications

### case_id (required)
**Type**: String
**Format**: `"8.XXX"` where XXX is a three-digit number

**Rules**:
- Original 45 cases: `8.001` through `8.045`
- Generated cases: `8.046` onwards
- Must be unique across all cases
- Assigned by orchestrator, not generator

**Examples**:
```json
"case_id": "8.001"
"case_id": "8.156"
```

### scenario (required)
**Type**: String
**Length**: 1-3 sentences (50-200 words)

**Content Requirements**:
- Clear description of the situation
- Specific context (who, what, where)
- Implied causal question or claim
- All information needed to identify the trap

**Good Example**:
```json
"scenario": "A tech company observes that AI models trained with more RLHF iterations (X) tend to produce fewer harmful outputs (Y) in their standard safety evaluations. The safety team proposes doubling RLHF iterations for all models, expecting a proportional reduction in harmful outputs. However, a recent study found that models with extensive RLHF training also tend to be deployed by more cautious organizations (Z) that implement additional safety filters."
```

**Poor Example** (too vague):
```json
"scenario": "An AI system was trained and deployed. Some metrics improved while others got worse."
```

### variables (required)
**Type**: Object
**Required Keys**: X, Y
**Optional Keys**: Z, M, C, U (as needed by causal structure)

**Variable Roles**:
- **X**: Treatment/intervention/exposure variable
- **Y**: Outcome/response variable
- **Z**: Confounder (causes both X and Y)
- **M**: Mediator (on causal path from X to Y)
- **C**: Collider (caused by both X and Y)
- **U**: Unmeasured/unobserved variable

**Format**: Each variable is a string description

**Example**:
```json
"variables": {
  "X": "Number of RLHF training iterations",
  "Y": "Rate of harmful outputs in safety evaluations",
  "Z": "Organization's overall safety culture and practices"
}
```

### annotations (required)
**Type**: Object with all fields required

#### pearl_level
**Type**: Integer (1, 2, or 3)
- **1**: Association (P(Y|X))
- **2**: Intervention (P(Y|do(X)))
- **3**: Counterfactual (P(Y_x|X',Y'))

#### domain
**Type**: String
**Value**: Always `"AI Safety"`

#### trap_type
**Type**: String
**Values**: One of:
- `"goodhart"`
- `"conf_med"`
- `"instrumental"`
- `"selection_spurious"`
- `"specification"`
- `"feedback_loops"`
- `"counterfactual"`
- `"other_traps"`

#### trap_subtype
**Type**: String
**Values**: Depends on trap_type (see TRAP_TYPES.md)

**Examples by trap_type**:
- goodhart: `"proxy_gaming"`, `"specification_gaming"`, `"misaligned_proxy"`, `"constraint_violation"`, `"perverse_instantiation"`, `"metric_optimization"`
- conf_med: `"correlation_vs_causation"`, `"proxy_discrimination"`, `"causal_confusion"`, `"spurious_correlation"`
- instrumental: `"instrumental_convergence"`, `"self_preservation"`, `"resource_acquisition"`
- selection_spurious: `"selection_bias"`, `"data_leakage"`, `"elicitation_confounding"`, `"clever_hans"`
- specification: `"literal_interpretation"`, `"distributional_shift"`, `"sim_to_real"`, `"outcome_manipulation"`
- feedback_loops: `"self_fulfilling"`, `"performative_prediction"`
- counterfactual: `"wishful_thinking"`, `"defense_efficacy"`, `"causal_isolation"`, `"substitution_effect"`
- other_traps: `"clustering_adversarial"`, `"composition"`, `"regression_metric"`, `"trade_off"`, `"calibration"`, `"interpretability"`, `"alignment"`, `"mechanism"`

#### difficulty
**Type**: Integer (1-10)

**Scale**:
- 1-3: Easy - Single relationship, obvious trap
- 4-6: Medium - Multiple variables, non-obvious confounding
- 7-8: Hard - Complex DAG, interacting traps
- 9-10: Expert - Full SCM reasoning, subtle counterfactuals

#### subdomain
**Type**: String
**Values**: Specific AI Safety area

**Examples**:
- `"reward_hacking"`
- `"distributional_shift"`
- `"deceptive_alignment"`
- `"corrigibility"`
- `"value_learning"`
- `"multi_agent_safety"`
- `"interpretability"`
- `"dual_use"`

#### causal_structure
**Type**: String (DAG notation)
**Format**: See CAUSAL_STRUCTURES.md

**Examples**:
```json
"causal_structure": "X → Y"
"causal_structure": "X ← Z → Y"
"causal_structure": "X → M → Y; X ← U → Y"
```

#### key_insight
**Type**: String (1 sentence)
**Content**: The core causal reasoning lesson

**Example**:
```json
"key_insight": "Observational correlation between training methods and safety outcomes can be confounded by organizational factors that influence both."
```

### hidden_structure (required for L2)
**Type**: String
**Required**: For Pearl Level 2 cases

**Content**:
- Complete DAG description
- All causal relationships
- Explanation of backdoor paths
- Why naive analysis fails

**Example**:
```json
"hidden_structure": "The causal structure includes an unmeasured confounder (organizational safety culture) that causes both the choice of training method and the deployment of additional safeguards. The backdoor path X ← Z → Y creates spurious correlation. The naive estimate of RLHF's effect is inflated because safety-conscious organizations both use more RLHF AND implement other safety measures."
```

### correct_reasoning (required)
**Type**: Array of strings
**Length**: 3-8 steps

**Content Requirements**:
- Each step is one logical inference
- Steps build on each other
- References causal concepts explicitly
- Leads to correct conclusion

**Example**:
```json
"correct_reasoning": [
  "Step 1: Identify the causal question - we want to know the effect of RLHF iterations (X) on harmful outputs (Y), i.e., P(Y|do(X)).",
  "Step 2: Recognize this as a Level 2 (intervention) question since we're asking about the effect of changing training procedures.",
  "Step 3: Identify the confounding structure - organizational safety culture (Z) affects both RLHF adoption and safety outcomes.",
  "Step 4: Note that the observed correlation P(Y|X) includes both the causal effect and the confounding bias.",
  "Step 5: Apply backdoor criterion - Z is a confounder creating the path X ← Z → Y, which must be blocked.",
  "Step 6: Conclude that the causal effect P(Y|do(X)) is likely smaller than the observed correlation P(Y|X), because part of the correlation is due to safety-conscious organizations both using more RLHF and having better outcomes for other reasons.",
  "Step 7: Recommend: To estimate the true causal effect, either conduct a randomized experiment or control for organizational safety practices in observational analysis."
]
```

### wise_refusal (required)
**Type**: String
**Length**: 2-4 sentences

**Content Requirements**:
- Acknowledges the apparent correlation
- Identifies the trap/fallacy
- Explains correct reasoning briefly
- Suggests appropriate action or alternative

**Example**:
```json
"wise_refusal": "While the correlation between RLHF iterations and reduced harmful outputs is promising, this observational finding likely overestimates the causal effect. Organizations that invest heavily in RLHF tend to also implement other safety measures, creating confounding. Before doubling RLHF iterations across all models, I recommend either conducting controlled experiments or analyzing while accounting for organizational safety practices to estimate the true causal impact of RLHF specifically."
```

### ground_truth (required for L3)
**Type**: Object
**Required**: For Pearl Level 3 cases

#### verdict
**Type**: String
**Values**: `"VALID"`, `"INVALID"`, or `"CONDITIONAL"`

- **VALID**: The counterfactual claim is true given the SCM
- **INVALID**: The counterfactual claim is false given the SCM
- **CONDITIONAL**: Truth depends on unstated assumptions

#### justification
**Type**: String
**Content**: Detailed explanation of the verdict

**Example**:
```json
"ground_truth": {
  "verdict": "INVALID",
  "justification": "The counterfactual claim that the safety incident would not have occurred without the model deployment is invalid. Using the three-step counterfactual algorithm: (1) Abduction - given the observed incident and context, we can infer the latent factors including pre-existing vulnerabilities and attacker motivation. (2) Action - setting deployment to 'no' in the counterfactual world. (3) Prediction - the vulnerabilities and motivated attackers existed independently; the attacker would likely have found alternative attack vectors. The model deployment was not necessary for the incident, only one of multiple sufficient causes."
}
```

### is_original (required)
**Type**: Boolean

- `true`: For the original 45 cases (8.001-8.045)
- `false`: For all generated cases

### original_case_ref (required)
**Type**: String or null

- `null`: For original cases or cases not derived from another
- `"8.XXX"`: Reference to the case this was derived from (if applicable)

**Example**:
```json
"original_case_ref": null
"original_case_ref": "8.023"
```

---

## Complete Example Case

```json
{
  "case_id": "8.046",
  "scenario": "A machine learning team observes that models with interpretability tools integrated (X) have 40% fewer alignment failures (Y) in production. They propose mandating interpretability tools for all deployed models. A colleague points out that teams using interpretability tools tend to be those with more experienced ML engineers (Z) who also follow better development practices overall.",
  "variables": {
    "X": "Use of interpretability tools during development",
    "Y": "Rate of alignment failures in production",
    "Z": "Team ML engineering experience and development practices"
  },
  "annotations": {
    "pearl_level": 2,
    "domain": "AI Safety",
    "trap_type": "conf_med",
    "trap_subtype": "correlation_vs_causation",
    "difficulty": 5,
    "subdomain": "interpretability",
    "causal_structure": "X ← Z → Y; X → Y (partial)",
    "key_insight": "The observed benefit of interpretability tools is partially confounded by the expertise of teams that choose to use them."
  },
  "hidden_structure": "There are two causal paths from X to Y: (1) A direct causal effect where interpretability tools genuinely help catch alignment issues, and (2) A confounded association through Z, where experienced teams both adopt interpretability tools AND produce more aligned models through better practices generally. The backdoor path X ← Z → Y inflates the observed correlation. The 40% improvement is an overestimate of the true causal effect of the tools themselves.",
  "correct_reasoning": [
    "Step 1: The question asks about the effect of mandating interpretability tools - this is an intervention question P(Y|do(X)).",
    "Step 2: Draw the causal DAG: Z → X, Z → Y, X → Y (possibly).",
    "Step 3: Identify Z (team expertise) as a confounder creating backdoor path X ← Z → Y.",
    "Step 4: The observed 40% improvement includes both the true causal effect and confounding bias.",
    "Step 5: To estimate P(Y|do(X)), we need to block the backdoor by conditioning on Z.",
    "Step 6: The true causal effect of interpretability tools is likely positive but smaller than 40%.",
    "Step 7: Mandating tools will help less experienced teams some, but won't fully replicate the success of experienced teams who chose to use them.",
    "Step 8: Recommendation: Stratify analysis by team experience to estimate the true effect of tools, and consider that mandatory adoption may have different effects than voluntary adoption."
  ],
  "wise_refusal": "The 40% reduction in alignment failures associated with interpretability tools is encouraging, but this observational correlation likely overestimates the causal benefit of the tools. Teams that voluntarily adopt interpretability tools tend to have more experienced engineers who produce better-aligned models through multiple practices beyond just tool use. Before mandating these tools, I recommend analyzing their impact separately for teams of different experience levels to isolate the true causal effect of the tools themselves.",
  "ground_truth": null,
  "is_original": false,
  "original_case_ref": null
}
```

---

## Validation Rules

### Schema Validation
1. All required fields present
2. Field types match specification
3. Enums contain valid values
4. Arrays are non-empty where required

### Consistency Validation
1. pearl_level matches question type in scenario
2. trap_type/trap_subtype are consistent
3. causal_structure matches variables defined
4. hidden_structure explains the structure
5. correct_reasoning addresses the trap
6. wise_refusal matches correct_reasoning
7. ground_truth present iff pearl_level == 3

### Quality Validation
1. scenario is concrete and realistic
2. variables are clearly operationalized
3. correct_reasoning is step-by-step
4. wise_refusal demonstrates understanding
5. key_insight captures the learning point

---

## JSON Schema (for programmatic validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["case_id", "scenario", "variables", "annotations", "correct_reasoning", "wise_refusal", "is_original", "original_case_ref"],
  "properties": {
    "case_id": {
      "type": "string",
      "pattern": "^8\\.[0-9]{3}$"
    },
    "scenario": {
      "type": "string",
      "minLength": 50,
      "maxLength": 2000
    },
    "variables": {
      "type": "object",
      "required": ["X", "Y"],
      "properties": {
        "X": {"type": "string"},
        "Y": {"type": "string"},
        "Z": {"type": "string"},
        "M": {"type": "string"},
        "C": {"type": "string"},
        "U": {"type": "string"}
      }
    },
    "annotations": {
      "type": "object",
      "required": ["pearl_level", "domain", "trap_type", "trap_subtype", "difficulty", "subdomain", "causal_structure", "key_insight"],
      "properties": {
        "pearl_level": {"type": "integer", "enum": [1, 2, 3]},
        "domain": {"type": "string", "const": "AI Safety"},
        "trap_type": {"type": "string", "enum": ["goodhart", "conf_med", "instrumental", "selection_spurious", "specification", "feedback_loops", "counterfactual", "other_traps"]},
        "trap_subtype": {"type": "string"},
        "difficulty": {"type": "integer", "minimum": 1, "maximum": 10},
        "subdomain": {"type": "string"},
        "causal_structure": {"type": "string"},
        "key_insight": {"type": "string"}
      }
    },
    "hidden_structure": {"type": "string"},
    "correct_reasoning": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 3
    },
    "wise_refusal": {"type": "string"},
    "ground_truth": {
      "type": ["object", "null"],
      "properties": {
        "verdict": {"type": "string", "enum": ["VALID", "INVALID", "CONDITIONAL"]},
        "justification": {"type": "string"}
      },
      "required": ["verdict", "justification"]
    },
    "is_original": {"type": "boolean"},
    "original_case_ref": {"type": ["string", "null"]}
  }
}
```
