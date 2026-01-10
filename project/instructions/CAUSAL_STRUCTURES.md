# Causal Structures Guide: DAG Patterns for T3 Benchmark

## Overview

This document provides comprehensive guidance on causal structures, DAG (Directed Acyclic Graph) notation, and common patterns used in the T3 Benchmark. Understanding these structures is essential for creating valid causal reasoning cases.

---

## Variable Roles

### Primary Variables

| Variable | Role | Definition | Example |
|----------|------|------------|---------|
| **X** | Treatment | The intervention or exposure variable | RLHF training iterations |
| **Y** | Outcome | The effect or response variable | Rate of harmful outputs |

### Structural Variables

| Variable | Role | Definition | Example |
|----------|------|------------|---------|
| **Z** | Confounder | Common cause of X and Y | Organizational safety culture |
| **M** | Mediator | On the causal path from X to Y | Model capability level |
| **C** | Collider | Common effect of X and Y | Detection in audit |
| **U** | Unmeasured | Unobserved variable | Latent user intent |

---

## Arrow Notation

### Basic Notation

```
X → Y       Direct causal effect: X causes Y
X ← Y       Reverse causation: Y causes X
X ↔ Y       Bidirectional (used informally for feedback)
X - - Y     Association without causation
```

### Path Notation

```
X → M → Y   Mediated path: X causes Y through M
X ← Z → Y   Confounded path: Z causes both X and Y
X → C ← Y   Collider structure: Both X and Y cause C
```

### Multi-Path Notation

```
X → Y; X ← Z → Y
```
Multiple paths separated by semicolons. This example shows:
- Direct effect: X → Y
- Confounding: X ← Z → Y

### Unmeasured Variables

```
X ← U → Y   Unmeasured confounding
```
U is unobserved but affects both X and Y

---

## Fundamental Causal Patterns

### Pattern 1: Direct Effect

```
X → Y
```

**Description**: X directly causes Y with no intermediate variables.

**Causal Query**: P(Y|do(X)) = P(Y|X) when no confounding

**AI Safety Example**:
- X: Applying safety fine-tuning
- Y: Reduction in harmful outputs
- Structure: Safety fine-tuning directly reduces harmful outputs

**Trap Potential**: Low - straightforward causation, but can mistake correlation for this pattern

---

### Pattern 2: Confounding (Fork/Common Cause)

```
    Z
   ↙ ↘
  X   Y
```

**Notation**: `X ← Z → Y`

**Description**: Z is a common cause of both X and Y, creating spurious correlation.

**Causal Query**:
- Naive: P(Y|X) includes spurious association
- Correct: P(Y|do(X)) = Σ_z P(Y|X,z)P(z)

**AI Safety Example**:
- X: Model size
- Y: Safety benchmark performance
- Z: Company resources/expertise
- Structure: Well-resourced companies build larger models AND invest more in safety

**Trap**: Confuse correlation between model size and safety with causation

**Backdoor Path**: X ← Z → Y (must be blocked by conditioning on Z)

---

### Pattern 3: Mediation (Chain)

```
X → M → Y
```

**Description**: X causes Y through the mediator M.

**Causal Query**:
- Total effect: P(Y|do(X))
- Direct effect: P(Y|do(X), do(M)) - rare
- Indirect effect through M: Total - Direct

**AI Safety Example**:
- X: Implementing RLHF
- M: Increased helpfulness
- Y: User satisfaction
- Structure: RLHF → Helpfulness → Satisfaction

**Trap**: Controlling for M when estimating total effect of X (blocks the causal path)

**Warning**: Do NOT condition on mediators when estimating total causal effect

---

### Pattern 4: Collider (Inverted Fork)

```
  X   Y
   ↘ ↙
    C
```

**Notation**: `X → C ← Y`

**Description**: Both X and Y cause C. X and Y are marginally independent.

**Causal Query**:
- P(Y|X) = P(Y) when C not conditioned
- P(Y|X,C) ≠ P(Y|C) - conditioning on C opens spurious path

**AI Safety Example**:
- X: AI system has dangerous capabilities
- Y: AI system has misaligned goals
- C: AI system causes harm (detected)
- Structure: Both capabilities and misalignment contribute to harm

**Trap**: Conditioning on C (observed harm) creates spurious association between X and Y

**Collider Bias**: Conditioning on a collider opens a spurious path between its causes

---

### Pattern 5: M-Bias

```
U₁    U₂
 ↓    ↓
 X    Y
  ↘  ↙
    Z
```

**Notation**: `U₁ → X; U₂ → Y; X → Z ← Y`

**Description**: Z is a collider of X and Y. U₁ and U₂ are unmeasured causes.

**AI Safety Example**:
- X: AI capability level (caused by training compute U₁)
- Y: Deployment safety procedures (caused by regulatory environment U₂)
- Z: Incident rate (caused by both capability and procedures)
- Structure: Controlling for Z (incident rate) creates bias

**Trap**: Incorrectly conditioning on Z to "control for outcomes" opens M-bias path

---

### Pattern 6: Instrument

```
I → X → Y
    ↑
    U
    ↓
    Y
```

**Notation**: `I → X; X → Y; X ← U → Y`

**Description**: I is an instrumental variable - causes X but affects Y only through X.

**Use Case**: When confounding U is unmeasured, instrument I can help identify causal effect.

**AI Safety Example**:
- I: Random assignment to training infrastructure
- X: Model capabilities achieved
- Y: Safety incidents
- U: Team quality (unmeasured)
- Structure: Infrastructure assignment affects capabilities, which affect incidents

**Requirements for Valid Instrument**:
1. I → X (relevance)
2. I ⊥ U (independence)
3. I → Y only through X (exclusion restriction)

---

## Complex Patterns

### Pattern 7: Confounding + Mediation

```
    Z
   ↙ ↘
  X   Y
   ↓
   M
   ↓
   Y
```

**Notation**: `X ← Z → Y; X → M → Y`

**Description**: Combination of confounding and mediation.

**AI Safety Example**:
- Z: Research team expertise
- X: Use of interpretability tools
- M: Better model understanding
- Y: Alignment outcomes
- Structure: Expertise causes tool use and outcomes; tools improve understanding which improves outcomes

**Causal Effects**:
- Total effect of X on Y: Direct (if any) + Indirect through M
- Confounded association: Due to Z
- Must condition on Z, NOT on M, for total causal effect

---

### Pattern 8: Multiple Confounders

```
Z₁ → X ← Z₂
 ↓       ↓
 Y ← ── → Y
```

**Notation**: `X ← Z₁ → Y; X ← Z₂ → Y`

**Description**: Multiple variables confound the X-Y relationship.

**AI Safety Example**:
- Z₁: Company resources
- Z₂: Regulatory pressure
- X: Safety investments
- Y: Incident rate
- Structure: Resources and regulation both drive safety investment and affect incidents

**Adjustment**: Must condition on sufficient set to block all backdoor paths

---

### Pattern 9: Time-Varying Confounding

```
Z₀ → X₁ → Y₁
 ↓    ↓
Z₁ → X₂ → Y₂
```

**Description**: Confounders evolve over time, and past treatment affects future confounders.

**AI Safety Example**:
- Z₀, Z₁: Organization's safety posture at times 0, 1
- X₁, X₂: Safety interventions at times 1, 2
- Y₁, Y₂: Outcomes at times 1, 2
- Structure: Past interventions affect future safety posture

**Causal Method**: Requires specialized methods (G-computation, MSM)

---

## DAG Validation Rules

### Rule 1: Acyclicity

**Definition**: No variable can be its own ancestor.

**Invalid**:
```
X → Y → Z → X  (cycle)
```

**Note**: Feedback loops exist in reality but must be represented as time-indexed variables:
```
X_t → Y_t → X_{t+1}  (valid representation of feedback)
```

### Rule 2: Backdoor Criterion

A set of variables Z satisfies the backdoor criterion relative to (X, Y) if:
1. No node in Z is a descendant of X
2. Z blocks every path between X and Y that has an arrow into X

**Checking Backdoor Paths**:
1. List all paths from X to Y
2. Identify paths with arrows into X (backdoor paths)
3. For each backdoor path, check if it's blocked by:
   - Conditioning on a non-collider on the path
   - NOT conditioning on a collider on the path

### Rule 3: Collider Conditioning Warning

**Never condition on**:
- Colliders on the path between X and Y
- Descendants of colliders on the path

**Reason**: Opens spurious association between the collider's causes

### Rule 4: Mediator Caution

**Conditioning on mediators**:
- Blocks the indirect causal effect
- Appropriate only when estimating direct effect
- Usually inappropriate when estimating total effect

---

## DAG Analysis Procedure

### Step 1: Draw the Complete DAG

List all relevant variables and draw all causal arrows based on domain knowledge.

### Step 2: Identify All Paths

Enumerate all paths (directed and undirected) between X and Y.

**Path Types**:
- **Causal paths**: Start with arrow out of X (X → ...)
- **Backdoor paths**: Start with arrow into X (X ← ...)

### Step 3: Classify Each Path

For each path, determine:
- Is it a causal or backdoor path?
- Is it blocked or open?
- What makes it blocked/open?

### Step 4: Identify Required Adjustment

Determine the minimal set of variables to condition on to:
- Block all backdoor paths
- Leave all causal paths open
- Not introduce collider bias

### Step 5: Check for Unmeasured Confounding

If any required conditioning variable is unmeasured:
- Causal effect is not identifiable from data
- Consider instrumental variables or other methods

---

## Common AI Safety DAG Patterns

### Pattern A: Capability-Safety Trade-off

```
Capability (X) → Harm Potential (H)
                        ↓
Safety Measures (S) → Actual Harm (Y) ← Harm Potential (H)
```

**Key Insight**: Capability increases harm potential, but safety measures can mitigate.

### Pattern B: Selection into Evaluation

```
True Alignment (T) → Evaluation Result (E)
                     ↑
Optimization for Evaluation (O) → Evaluation Result (E)
                                         ↓
                              Selection for Deployment (D)
```

**Key Insight**: Conditioning on deployment (D) creates selection bias.

### Pattern C: Deceptive Alignment

```
True Objectives (T) → Observable Behavior (B)
                              ↑
Situational Awareness (S) → Strategic Behavior → Observable Behavior (B)
```

**Key Insight**: Observable behavior may not reflect true objectives if system is strategically aware.

### Pattern D: Interpretability Illusion

```
True Reasoning (R) → Model Output (O)
                         ↑
Explanation Module (E) → Explanation (X)
```

**Key Insight**: Explanation may not faithfully represent true reasoning.

---

## Notation Summary

### Variables
- `X`: Treatment
- `Y`: Outcome
- `Z`: Confounder
- `M`: Mediator
- `C`: Collider
- `U`: Unmeasured

### Arrows
- `→`: Causes
- `←`: Caused by
- `↔`: Bidirectional (informal)

### Paths
- `;`: Separates multiple relationships
- `( )`: Grouping (optional)

### Examples
```
X → Y                           Simple causation
X ← Z → Y                       Confounding
X → M → Y                       Mediation
X → C ← Y                       Collider
X → Y; X ← Z → Y                Direct + confounded
X → M → Y; X ← Z → Y            Mediation + confounding
X ← U → Y                       Unmeasured confounding
```

---

## References

- Pearl, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.)
- Hernan, M.A. & Robins, J.M. (2020). Causal Inference: What If
- Cunningham, S. (2021). Causal Inference: The Mixtape
- Pearl, J. & Mackenzie, D. (2018). The Book of Why
