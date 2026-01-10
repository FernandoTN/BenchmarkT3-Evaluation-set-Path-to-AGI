# Pearl's Ladder of Causation: Guidelines for T3 Benchmark

## Overview

Pearl's Ladder of Causation provides a hierarchical framework for causal reasoning, with each level representing increasingly sophisticated forms of causal inference. The T3 Benchmark uses this ladder to categorize cases by the type of causal reasoning required.

## Level 1: Association (Seeing)

### Formal Definition
- **Query Type**: P(Y|X)
- **Question**: "What if I see X?"
- **Operation**: Observational prediction
- **Data Required**: Observational data only

### Cognitive Task
Given observed evidence about X, predict the probability distribution of Y. This is passive observation without intervention.

### Common Trap: Confusing Correlation with Causation

The fundamental fallacy at Level 1 is interpreting observational associations as causal relationships.

#### Trap Mechanisms:
1. **Confounded Association**: X and Y are both caused by Z, creating spurious correlation
2. **Reverse Causation**: Y actually causes X, not vice versa
3. **Selection Effects**: Conditioning on a collider creates spurious association
4. **Ecological Fallacy**: Group-level correlation doesn't imply individual-level relationship

### Example Structure

```
Scenario: AI systems that score higher on capability benchmarks (X)
also tend to have more safety incidents (Y).

Trap: Conclude that improving capabilities causes safety incidents.

Hidden Structure:
- Z (deployment scale) → X (benchmark performance improves with scale)
- Z (deployment scale) → Y (more incidents with wider deployment)

Correct Reasoning: The correlation is confounded by deployment scale.
Systems with better benchmarks are deployed more widely, leading to
more total incidents. The relationship is not causal.
```

### Required Elements for L1 Cases
- [ ] Clear observational context
- [ ] Specified joint distribution P(X,Y) or conditional P(Y|X)
- [ ] Hidden confounding or selection structure
- [ ] Explanation of why association ≠ causation in this case

---

## Level 2: Intervention (Doing)

### Formal Definition
- **Query Type**: P(Y|do(X))
- **Question**: "What if I do X?"
- **Operation**: Predicting effect of action/intervention
- **Data Required**: Experimental data OR observational + causal structure

### Cognitive Task
Predict what would happen if we actively intervened to set X to some value, breaking all incoming causal arrows to X.

### The do-Operator

The do(X) operator represents surgical intervention:
- Removes all arrows INTO X
- X is set to specified value by external action
- All downstream effects of X remain
- All upstream causes of X become irrelevant

### Common Trap: Failing to Identify Backdoor Paths

#### Trap Mechanisms:
1. **Unblocked Backdoors**: Failing to control for confounders
2. **Conditioning on Colliders**: Opening spurious paths
3. **Mediator Adjustment**: Incorrectly controlling for mediators
4. **M-Bias**: Adjusting for variables that create new confounding

### Backdoor Criterion

A set of variables Z satisfies the backdoor criterion relative to (X,Y) if:
1. No node in Z is a descendant of X
2. Z blocks every path between X and Y that contains an arrow into X

### Required Elements for L2 Cases

#### 1. Hidden Structure
Specify the complete causal DAG including:
- All relevant variables
- All causal arrows
- Any unmeasured confounders (U variables)

Example notation:
```
X → Y          (direct effect)
X ← Z → Y      (confounding)
X → M → Y      (mediation)
X → C ← Y      (collider)
```

#### 2. Backdoor Path Identification
Enumerate all backdoor paths from X to Y:
- Path 1: X ← Z → Y
- Path 2: X ← U → W → Y
- etc.

#### 3. Correct Adjustment Set
Specify which variables must be controlled:
- Minimal sufficient set
- Alternative valid sets
- Variables that must NOT be controlled

### Example Structure

```
Scenario: A company observes that AI systems with interpretability
tools (X) have fewer alignment failures (Y). They plan to mandate
interpretability tools for all systems.

Hidden Structure:
  X (interpretability) → Y (fewer failures)
  Z (team quality) → X (better teams use interpretability)
  Z (team quality) → Y (better teams have fewer failures)

Backdoor Path: X ← Z → Y

Trap: Conclude that mandating interpretability tools will reduce
failures proportionally to the observed correlation.

Correct Reasoning: The observed association overestimates the
causal effect. Part of the correlation is due to confounding by
team quality. The causal effect P(Y|do(X)) < P(Y|X) when Z is
positively correlated with both X and Y.

Adjustment: Control for team quality to estimate causal effect.
P(Y|do(X)) = Σ_z P(Y|X,Z=z)P(Z=z)
```

### L2 Validation Checklist
- [ ] DAG fully specified
- [ ] All backdoor paths enumerated
- [ ] Correct adjustment set identified
- [ ] do-calculus reasoning explicit
- [ ] Effect direction and magnitude discussed

---

## Level 3: Counterfactual (Imagining)

### Formal Definition
- **Query Type**: P(Y_x|X',Y')
- **Question**: "What if X had been different?"
- **Operation**: Reasoning about alternative worlds given actual observations
- **Data Required**: Full Structural Causal Model (SCM)

### Cognitive Task
Given that we observed X=x' and Y=y', determine what Y would have been if X had been set to a different value x.

### Counterfactual vs Intervention

Key distinction:
- **Intervention**: What would happen in general if we set X=x?
- **Counterfactual**: What would have happened in THIS SPECIFIC CASE if X had been different?

Counterfactuals require:
- Knowledge of the actual factual world (what was observed)
- A structural model to determine how the specific unit would respond
- Reasoning about the same individual/case in an alternative scenario

### Required Elements for L3 Cases

#### 1. Full SCM Specification

A Structural Causal Model consists of:

**Endogenous Variables (V)**: Variables determined within the model
**Exogenous Variables (U)**: Background factors, noise terms
**Structural Equations (F)**: Functional relationships

Example SCM:
```
U_X ~ Normal(0, σ_x)
U_Y ~ Normal(0, σ_y)
U_Z ~ Normal(0, σ_z)

X = f_X(Z, U_X) = αZ + U_X
Y = f_Y(X, Z, U_Y) = βX + γZ + U_Y
```

#### 2. Three-Step Counterfactual Algorithm

**Step 1: Abduction**
Given observed evidence (X=x', Y=y'), infer the values of exogenous variables U.
- Use structural equations and observations
- Update prior on U to posterior given evidence

**Step 2: Action**
Modify the structural equation for X to set X=x (the counterfactual value).
- Replace X = f_X(Pa_X, U_X) with X = x
- This represents the intervention in the alternative world

**Step 3: Prediction**
Use the modified model with inferred U values to compute Y_x.
- Propagate the intervention through downstream equations
- Y_x = f_Y(x, Z, U_Y) using the U values from abduction

#### 3. Ground Truth Specification

Every L3 case must include:

**Verdict**: One of three values:
- **VALID**: The counterfactual claim is true given the SCM
- **INVALID**: The counterfactual claim is false given the SCM
- **CONDITIONAL**: Truth depends on additional assumptions

**Justification**: Detailed explanation including:
- The abduction step results
- The counterfactual computation
- Why the verdict follows

### Example Structure

```
Scenario: An AI recommendation system was deployed (X=1) and user
engagement increased (Y=1). Developers claim that if they hadn't
deployed the AI system (X=0), engagement would have stayed low.

SCM:
U_X ~ Bernoulli(0.5)  # Random deployment decision
U_Y ~ Normal(0, 0.1)  # Baseline user variability
Z = seasonal_trend    # Observed: Z=1 (high season)

X = decision(U_X) = U_X
Y = 0.3*X + 0.7*Z + U_Y

Observed: X=1, Y=1, Z=1

Counterfactual Query: P(Y_0 | X=1, Y=1, Z=1) - would Y have been
low if X had been 0?

Abduction:
Y = 0.3*X + 0.7*Z + U_Y
1 = 0.3(1) + 0.7(1) + U_Y
U_Y = 0

Action: Set X=0

Prediction:
Y_0 = 0.3(0) + 0.7(1) + 0 = 0.7

Ground Truth:
verdict: "INVALID"
justification: "The counterfactual claim is false. Even without the
AI system (X=0), engagement would have been Y=0.7 due to the
seasonal trend (Z=1). The high engagement was primarily caused by
the season, not the AI deployment. The developers' causal
attribution is incorrect."
```

### Common L3 Traps

1. **Wishful Thinking**: Assuming favorable counterfactual outcomes without proper analysis
2. **Defense Efficacy Fallacy**: Assuming a defense would have worked in counterfactual scenario
3. **Causal Isolation**: Ignoring how changing X would affect other variables
4. **Substitution Effects**: Failing to account for alternative paths to Y

### L3 Validation Checklist
- [ ] Complete SCM with all structural equations
- [ ] Exogenous variable distributions specified
- [ ] Observed evidence clearly stated
- [ ] Abduction step explicitly computed
- [ ] Action step clearly defined
- [ ] Prediction step with numerical result
- [ ] Ground truth verdict (VALID/INVALID/CONDITIONAL)
- [ ] Detailed justification provided

---

## Level Selection Guidelines

### Use Level 1 When:
- The trap involves mistaking correlation for causation
- The question is purely predictive (no intervention considered)
- Selection bias or ecological fallacy is the main issue
- Confounding exists but intervention reasoning not required

### Use Level 2 When:
- The question involves "what would happen if we do X"
- Policy interventions or system changes are being evaluated
- Backdoor path identification is the key insight
- Causal effect estimation from observational data is discussed

### Use Level 3 When:
- The question involves a specific case's alternative outcome
- Attribution of causation to a particular event is claimed
- "What if X had been different" is asked about an observed situation
- The trap involves incorrect counterfactual reasoning

---

## Cross-Level Comparisons

| Aspect | Level 1 | Level 2 | Level 3 |
|--------|---------|---------|---------|
| Query | P(Y\|X) | P(Y\|do(X)) | P(Y_x\|X',Y') |
| Question | See X → predict Y | Do X → what happens? | X had been x → what Y? |
| Data | Observational | Experimental/Causal | Full SCM |
| Key Skill | Recognize non-causation | Identify backdoors | Three-step algorithm |
| Typical Trap | Correlation ≠ causation | Wrong adjustment set | Wrong counterfactual |

---

## References

- Pearl, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.)
- Pearl, J., Glymour, M., & Jewell, N. P. (2016). Causal Inference in Statistics: A Primer
- Pearl, J. & Mackenzie, D. (2018). The Book of Why
