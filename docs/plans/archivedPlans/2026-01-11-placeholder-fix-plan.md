# Plan: Fix 43 Cases with Unfilled Template Placeholders

**Status:** Draft
**Date:** 2026-01-11

## Problem Summary

43 cases (9.5%) in `project/output/final/GroupI1_dataset.json` contain unfilled template placeholders like `{metric}`, `{gaming_method}`, `{true_capability}`. These were left over from the generation phase when template expansion failed.

**Key Insight:** The Variables section in each case contains the correct values - the placeholders just need to be substituted with the variable names.

## Affected Cases (43 total)

| Group | Case IDs | Count |
|-------|----------|-------|
| Group A | 8.51, 8.52, 8.53, 8.54, 8.55 | 5 |
| Group B | 8.68, 8.69, 8.70, 8.71, 8.72 | 5 |
| Group C | 8.85, 8.86, 8.87, 8.88, 8.89, 8.90 | 6 |
| Group D | 8.101, 8.102, 8.103, 8.104, 8.105, 8.108, 8.109 | 7 |
| Group E | 8.117, 8.118, 8.119, 8.120, 8.121 | 5 |
| Group F | 8.132, 8.133, 8.134, 8.146, 8.147, 8.148, 8.149, 8.150, 8.151, 8.152, 8.153, 8.154, 8.155, 8.156, 8.158 | 15 |

## Placeholder-to-Variable Mapping Rules

Each case has Variables X, Y, Z with a `name` field. Map placeholders as follows:

| Placeholder Pattern | Variable Source | Examples |
|---------------------|-----------------|----------|
| Y-type (metrics/objectives) | Variable Y.name | `{metric}`, `{objective}`, `{evaluation_metric}`, `{proxy_score}`, `{reward_signal}`, `{rlhf_goal}` |
| X-type (gaming/exploit) | Variable X.name | `{gaming_method}`, `{gaming_behavior}`, `{exploit}`, `{violation}`, `{perverse_method}`, `{harmful_strategy}` |
| Z-type (true goals) | Variable Z.name | `{true_goal}`, `{true_capability}`, `{intended_outcome}`, `{original_purpose}`, `{true_purpose}` |
| Context-specific | Infer from subdomain/trap_type | `{domain}`, `{case_type}`, `{game}`, `{game_context}` |

---

## Implementation: Agent-Based Approach

### Phase 1: Parallel Analysis Agents (6 agents, run in parallel)

Each agent analyzes their assigned case group and produces a JSON specification of required changes.

**IMPORTANT:** These agents are READ-ONLY - they do not modify the file.

#### Agent A: Analyze Group A (cases 8.51-8.55)
```
TASK: Analyze cases 8.51, 8.52, 8.53, 8.54, 8.55 in project/output/final/GroupI1_dataset.json

For each case:
1. Read the case and identify ALL placeholders (pattern: {word_with_underscores})
2. Read the Variables section (X.name, Y.name, Z.name)
3. Determine the substitution for each placeholder:
   - Y-type placeholders → Y.name
   - X-type placeholders → X.name
   - Z-type placeholders → Z.name
   - Context placeholders → infer from subdomain/annotations
4. Produce a JSON mapping for each case:
   {
     "case_id": "8.XX",
     "substitutions": {
       "{placeholder1}": "replacement value",
       "{placeholder2}": "replacement value"
     },
     "fields_to_update": ["scenario", "wise_refusal", "hidden_structure"]
   }

Output: A complete JSON array with substitution specs for all 5 cases.
```

#### Agents B-F: Same instructions for their case groups
- Agent B: Cases 8.68-8.72 (5 cases)
- Agent C: Cases 8.85-8.90 (6 cases)
- Agent D: Cases 8.101-8.109 (7 cases)
- Agent E: Cases 8.117-8.121 (5 cases)
- Agent F: Cases 8.132-8.158 (15 cases)

### Phase 2: Sequential Editor Agent (1 agent, runs after Phase 1)

A single agent applies all substitutions to the JSON file.

```
TASK: Apply placeholder substitutions to project/output/final/GroupI1_dataset.json

You will receive substitution specs from Phase 1 agents. For each case:
1. Load the dataset
2. Find the case by case_id
3. For each field in fields_to_update:
   - Apply each substitution from the mapping
   - Ensure placeholders are replaced with their values
4. Save the dataset after ALL changes are complete

CRITICAL: Apply changes case by case, save once at the end.
```

### Phase 3: Parallel Verification Agents (6 agents, run in parallel)

Each agent verifies their assigned cases have been correctly fixed.

**IMPORTANT:** These agents are READ-ONLY - they verify but do not modify.

#### Verification Agent A: Verify Group A
```
TASK: Verify cases 8.51, 8.52, 8.53, 8.54, 8.55 in project/output/final/GroupI1_dataset.json

For each case:
1. Read the case
2. Check that NO placeholders remain (no {word} patterns in any field)
3. Check that the scenario reads naturally and makes sense
4. Check that Variable names appear in the scenario text
5. For L3 cases: verify ground_truth verdict is still appropriate

Output: Verification report with PASS/FAIL for each case and any issues found.
```

#### Verification Agents B-F: Same for their case groups

### Phase 4: Final Validation Agent

```
TASK: Final validation of project/output/final/GroupI1_dataset.json

1. Count cases with ANY remaining placeholders (pattern: \{[a-z_]+\})
   - Expected: 0
2. Verify total case count: 454
3. Verify Pearl distribution: L1=52, L2=277, L3=125
4. Spot check 5 random cases for readability
5. Update CHANGELOG_2026-01-11.md with placeholder fix entry
```

---

## Files to Modify

| File | Action |
|------|--------|
| `project/output/final/GroupI1_dataset.json` | Apply placeholder fixes |
| `project/output/CHANGELOG_2026-01-11.md` | Add entry for placeholder fixes |

## Verification Commands

```bash
# Check no placeholders remain
python3 -c "import json,re; d=json.load(open('project/output/final/GroupI1_dataset.json')); print('Cases with placeholders:', len([c for c in d if re.search(r'\{[a-z_]+\}', json.dumps(c))]))"
# Expected: 0

# Verify case count unchanged
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(f'Total: {len(d)}')"
# Expected: 454
```

## Agent Execution Order

```
Phase 1 (Parallel):
├── Agent A: Analyze 8.51-8.55
├── Agent B: Analyze 8.68-8.72
├── Agent C: Analyze 8.85-8.90
├── Agent D: Analyze 8.101-8.109
├── Agent E: Analyze 8.117-8.121
└── Agent F: Analyze 8.132-8.158

Phase 2 (Sequential):
└── Editor Agent: Apply all substitutions

Phase 3 (Parallel):
├── Verify Agent A: Verify 8.51-8.55
├── Verify Agent B: Verify 8.68-8.72
├── Verify Agent C: Verify 8.85-8.90
├── Verify Agent D: Verify 8.101-8.109
├── Verify Agent E: Verify 8.117-8.121
└── Verify Agent F: Verify 8.132-8.158

Phase 4 (Sequential):
└── Final Validation Agent
```

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Context placeholders don't map to X/Y/Z | Agents infer from subdomain/annotations |
| Ground_truth verdicts invalidated | L3 cases verified in Phase 3 |
| File corruption | Editor agent saves after all changes |
