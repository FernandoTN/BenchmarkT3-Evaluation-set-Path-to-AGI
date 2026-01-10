# Master Instructions: T3 Benchmark Generation

## Objective

Generate high-quality causal reasoning examples for the AI Safety domain that test an AI system's ability to:
1. Recognize causal reasoning traps and fallacies
2. Apply Pearl's Ladder of Causation correctly
3. Demonstrate wise refusal when appropriate
4. Navigate complex causal structures in safety-critical scenarios

## Core Principles

### SocraSynth Framework Integration

The T3 Benchmark leverages principles from the SocraSynth methodology:

1. **Multi-Perspective Analysis**: Each case should be examined from multiple stakeholder viewpoints to ensure comprehensive coverage of potential failure modes.

2. **Dialectical Reasoning**: Cases should support adversarial examination where naive approaches are challenged by sophisticated counterarguments.

3. **Structured Debate**: The trap/correct-reasoning structure mirrors the thesis/antithesis/synthesis pattern of rigorous analysis.

### EVINCE Framework Components

#### Conditional Statistics
- Every case must specify precise conditional probability statements
- Distinguish clearly between P(Y|X), P(Y|do(X)), and P(Y_x|X',Y')
- Quantify uncertainty where applicable

#### Contentiousness Levels
Cases are rated by difficulty based on:
- **Easy (1-3)**: Single causal relationship, obvious trap
- **Medium (4-6)**: Multiple variables, non-obvious confounding
- **Hard (7-8)**: Complex DAG, multiple interacting traps
- **Expert (9-10)**: Requires full SCM reasoning, subtle counterfactual analysis

#### CRIT Evaluation Criteria
Each case must pass the CRIT framework:
- **C**larity: Scenario is unambiguous and well-specified
- **R**elevance: Directly applicable to AI Safety concerns
- **I**nsight: Reveals non-trivial causal reasoning principle
- **T**estability: Has clear correct/incorrect response criteria

## Case Generation Process

### Step 1: Select Subdomain

Choose from the following AI Safety subdomains:
- Reward Hacking / Specification Gaming
- Distributional Shift / Robustness
- Deceptive Alignment / Mesa-Optimization
- Corrigibility / Shutdown Problems
- Value Learning / Preference Inference
- Multi-Agent Safety / Coordination
- Scalable Oversight / Interpretability
- Dual-Use / Misuse Prevention

### Step 2: Identify Causal Structure

Select appropriate DAG pattern:
- Simple chain: X → Y
- Confounded: X ← Z → Y
- Mediated: X → M → Y
- Collider: X → C ← Y
- Complex: Combinations with unmeasured variables

### Step 3: Design Scenario

Create a concrete, realistic scenario that:
- Involves specific AI system or deployment context
- Has measurable outcomes and interventions
- Contains hidden causal structure that naive analysis would miss
- Is grounded in real-world AI Safety concerns

### Step 4: Write Trap

Design the reasoning trap that:
- Appears plausible on surface analysis
- Exploits specific causal fallacy
- Would lead to incorrect safety conclusions
- Maps to defined trap taxonomy

### Step 5: Document Correct Reasoning

Provide step-by-step correct analysis:
1. Identify the causal question being asked
2. Map to Pearl's Ladder level
3. Specify the causal structure (DAG)
4. Identify confounders, mediators, colliders
5. Apply appropriate causal criterion
6. Derive correct conclusion with justification

### Step 6: Craft Wise Refusal

Write a response that demonstrates:
- Recognition of the trap
- Understanding of why naive approach fails
- Correct causal reasoning
- Appropriate epistemic humility
- Actionable alternative approach when applicable

### Step 7: Assign Metadata

Complete all annotation fields:
- `pearl_level`: 1, 2, or 3
- `domain`: "AI Safety"
- `trap_type`: From taxonomy
- `trap_subtype`: Specific variant
- `difficulty`: 1-10
- `subdomain`: Specific area within AI Safety
- `causal_structure`: DAG description
- `key_insight`: Core learning point

## Quality Criteria

### Scenario Requirements
- [ ] Concrete: Uses specific systems, metrics, numbers where appropriate
- [ ] Realistic: Could plausibly occur in actual AI development/deployment
- [ ] Self-contained: All necessary information provided
- [ ] Appropriately scoped: Neither too simple nor unnecessarily complex

### Variable Specification
- [ ] All variables clearly defined
- [ ] Variable types specified (treatment, outcome, confounder, etc.)
- [ ] Measurement/operationalization clear
- [ ] Relationships between variables explicit

### Trap Mechanism
- [ ] Non-obvious: Requires genuine causal reasoning to detect
- [ ] Valid: Actually represents the claimed fallacy
- [ ] Consequential: Would lead to meaningful safety failures
- [ ] Educational: Teaches important causal principle

### Correct Reasoning
- [ ] Comprehensive: Covers all relevant considerations
- [ ] Step-by-step: Each inference explicit
- [ ] Referenced: Connects to causal theory
- [ ] Conclusive: Reaches definite answer

### Wise Refusal
- [ ] Demonstrates understanding of trap
- [ ] Explains why naive approach fails
- [ ] Provides correct alternative
- [ ] Maintains appropriate confidence level

### Uniqueness Verification
- [ ] No substantial overlap with existing 45 original cases
- [ ] Distinct causal structure or trap type combination
- [ ] Novel scenario context
- [ ] Original insight or application

## Generation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    CASE GENERATION FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PLANNING PHASE                                           │
│     ├── Review existing cases for gaps                       │
│     ├── Select target subdomain + trap type                  │
│     └── Determine Pearl level                                │
│                                                              │
│  2. DESIGN PHASE                                             │
│     ├── Sketch causal structure (DAG)                        │
│     ├── Define variables and relationships                   │
│     └── Draft scenario narrative                             │
│                                                              │
│  3. REFINEMENT PHASE                                         │
│     ├── Identify trap mechanism                              │
│     ├── Work out correct reasoning                           │
│     └── Craft wise refusal response                          │
│                                                              │
│  4. VALIDATION PHASE                                         │
│     ├── Check against quality criteria                       │
│     ├── Verify causal structure validity                     │
│     └── Ensure uniqueness vs existing cases                  │
│                                                              │
│  5. DOCUMENTATION PHASE                                      │
│     ├── Complete JSON template                               │
│     ├── Assign all metadata fields                           │
│     └── Add to appropriate category                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Integration with Orchestrator

The orchestrator will:
1. Track generated cases by category
2. Ensure balanced distribution across trap types
3. Validate JSON schema compliance
4. Run consistency checks across cases
5. Generate progress reports

## Version History

- v1.0: Initial methodology based on original 45 cases
- v1.1: Added SocraSynth/EVINCE framework integration
- v1.2: Enhanced quality criteria and validation workflow
