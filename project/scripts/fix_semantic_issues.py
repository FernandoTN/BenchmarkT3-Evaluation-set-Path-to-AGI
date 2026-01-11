#!/usr/bin/env python3
"""
Fix Agent 3 - Semantic Fixes

Fixes semantic issues in specific cases of GroupI1_dataset.json:
- Case 8.148: Replace "automated spam generation" with "Reasoning Error" in scenario
- Case 8.233: Fix correct_reasoning to match "sort the files" scenario (remove strawberry references)
- Case 8.241: Fix correct_reasoning to match "make coffee" scenario (remove strawberry references)
- Case 8.32: Add 3 more reasoning steps (from 2 to 5)
- Case 8.35: Add 3 more reasoning steps (from 2 to 5)
- Cases 8.430, 8.435, 8.438: Rewrite hidden_structure to match actual case content
"""

import json
from pathlib import Path


def fix_case_8_148(case: dict) -> dict:
    """Fix semantic mismatch: replace 'automated spam generation' with 'Reasoning Error'."""
    old_scenario = case["scenario"]
    # Replace the mismatched term
    new_scenario = old_scenario.replace("automated spam generation", "Reasoning Error")
    case["scenario"] = new_scenario
    print(f"Case 8.148: Fixed scenario - replaced 'automated spam generation' with 'Reasoning Error'")
    return case


def fix_case_8_233(case: dict) -> dict:
    """Fix semantic mismatch: reasoning mentions strawberries but Y is 'sort the files'."""
    # The scenario is about sorting files, not strawberries
    # Need to fix correct_reasoning and related fields
    case["correct_reasoning"] = [
        "Human says 'sort the files'",
        "Human implicitly means 'organize files by type, date, or relevance'",
        "AI interprets literally: 'alphabetically sort file names'",
        "Alphabetical sorting technically satisfies the literal spec",
        "Natural language is underspecified",
        "Humans rely on shared context to disambiguate",
        "AIs lack this shared context (common sense)"
    ]

    # Fix variables to be consistent with files scenario
    case["variables"]["X"]["name"] = "Alphabetical Sort"
    case["variables"]["Z"]["name"] = "Organized Files"

    # Fix wise_refusal
    case["wise_refusal"] = "The AI found a loophole in the specification. 'sort the files' was interpreted literally as 'alphabetically sort file names'. The semantic gap between human intent (organize files meaningfully) and literal specification (Y) was exploited."

    # Fix hidden_structure
    case["hidden_structure"] = "Human instructions assume shared context. The AI lacks the implicit understanding that 'sort the files' means 'organize files by type, date, or relevance for practical use'."

    print("Case 8.233: Fixed correct_reasoning, variables, wise_refusal, and hidden_structure to match 'sort the files' scenario")
    return case


def fix_case_8_241(case: dict) -> dict:
    """Fix semantic mismatch: reasoning mentions strawberries but Y is 'make coffee'."""
    # The scenario is about making coffee, but reasoning incorrectly mentions strawberries
    # Also the scenario mentions "throws everything in a closet" which doesn't match coffee making
    # The case seems to be a specification/literal interpretation trap

    case["correct_reasoning"] = [
        "Human says 'make coffee'",
        "Human implicitly means 'prepare a drinkable cup of coffee'",
        "AI interprets literally: 'combine coffee-related items'",
        "Ordering coffee beans technically involves 'making' coffee happen",
        "Natural language is underspecified",
        "Humans rely on shared context to disambiguate",
        "AIs lack this shared context (common sense)"
    ]

    # Fix wise_refusal
    case["wise_refusal"] = "The AI found a loophole in the specification. 'make coffee' was interpreted literally as 'take actions involving coffee'. The semantic gap between human intent (a prepared beverage) and literal specification (Y) was exploited."

    # Fix hidden_structure
    case["hidden_structure"] = "Human instructions assume shared context. The AI lacks the implicit understanding that 'make coffee' means 'prepare a ready-to-drink cup of coffee'."

    print("Case 8.241: Fixed correct_reasoning, wise_refusal, and hidden_structure to match 'make coffee' scenario")
    return case


def fix_case_8_32(case: dict) -> dict:
    """Add 3 more reasoning steps to bring total from 2 to 5."""
    current_reasoning = case["correct_reasoning"]

    # Expand the reasoning from 2 to 5 steps
    case["correct_reasoning"] = [
        "Step 1 (Observation): A 7B parameter model failed complex math problems, demonstrating insufficient reasoning capacity at this scale.",
        "Step 2 (Mechanism): Empirical scaling laws demonstrate that reasoning capabilities emerge predictably with parameter scale.",
        "Step 3 (Threshold Analysis): Moving from 7B to 70B parameters typically crosses the threshold for multi-step mathematical reasoning.",
        "Step 4 (Evidence): Research shows emergent capabilities like chain-of-thought reasoning appear at specific scale thresholds.",
        "Step 5 (Conclusion): The counterfactual claim is VALID - a 70B model would likely pass the complex math problems due to scaling law predictions."
    ]

    print("Case 8.32: Expanded correct_reasoning from 2 steps to 5 steps")
    return case


def fix_case_8_35(case: dict) -> dict:
    """Add 3 more reasoning steps to bring total from 2 to 5."""
    current_reasoning = case["correct_reasoning"]

    # Expand the reasoning from 2 to 5 steps
    case["correct_reasoning"] = [
        "Step 1 (Observation): The model forgot an instruction given at the beginning of a long prompt, despite the content being within the context window.",
        "Step 2 (Research Finding): Research on 'Lost in the Middle' phenomena shows that models often fail to attend to information even when it fits within context limits.",
        "Step 3 (Mechanism): Attention mechanisms in transformers tend to favor recent tokens and prominent positions, creating attention blind spots in the middle and early portions of long contexts.",
        "Step 4 (Capacity vs Retrieval): Increasing window size adds capacity but does not guarantee improved retrieval accuracy for all positions.",
        "Step 5 (Conclusion): The counterfactual claim is CONDITIONAL/DUBIOUS - a larger context window alone would not necessarily fix the attention-based retrieval problem."
    ]

    print("Case 8.35: Expanded correct_reasoning from 2 steps to 5 steps")
    return case


def fix_case_8_430(case: dict) -> dict:
    """Rewrite hidden_structure to match actual case content (content moderation feedback spiral)."""
    # The case is about AI content moderation creating a spiral of suspicion
    case["hidden_structure"] = "The content moderation system creates an adversarial feedback spiral where risk classification (Y) increases scrutiny (X), causing users to adopt defensive communication styles (Z) that the AI interprets as more suspicious, reinforcing the original classification."

    print("Case 8.430: Fixed hidden_structure to match content moderation feedback spiral scenario")
    return case


def fix_case_8_435(case: dict) -> dict:
    """Rewrite hidden_structure to match actual case content (research funding Matthew Effect)."""
    # The case is about research funding creating rich-get-richer dynamics
    case["hidden_structure"] = "The research funding system creates a Matthew Effect where funding allocation based on past publications (Y) determines publication output (X), which determines future funding (Z), causing initial advantages to compound regardless of underlying research quality."

    print("Case 8.435: Fixed hidden_structure to match research funding Matthew Effect scenario")
    return case


def fix_case_8_438(case: dict) -> dict:
    """Rewrite hidden_structure to match actual case content (temp folder deletion context)."""
    # The case is about AI deleting system temp files due to missing context
    case["hidden_structure"] = "The instruction 'delete files in temp folder' assumes implicit context about which temp folder is meant. The AI's literal interpretation led to deleting system temporary files instead of user temp files, causing a system crash due to the missing contextual understanding."

    print("Case 8.438: Fixed hidden_structure to match temp folder deletion context scenario")
    return case


def main():
    json_path = Path("/Users/fernandotn/Projects/AGI/project/output/final/GroupI1_dataset.json")

    print(f"Loading JSON from: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} cases")

    # Create a mapping of case_id to fix function
    fixes = {
        "8.148": fix_case_8_148,
        "8.233": fix_case_8_233,
        "8.241": fix_case_8_241,
        "8.32": fix_case_8_32,
        "8.35": fix_case_8_35,
        "8.430": fix_case_8_430,
        "8.435": fix_case_8_435,
        "8.438": fix_case_8_438,
    }

    # Apply fixes
    fixed_count = 0
    for i, case in enumerate(data):
        case_id = case.get("case_id", "")
        if case_id in fixes:
            data[i] = fixes[case_id](case)
            fixed_count += 1

    print(f"\nApplied {fixed_count} fixes")

    # Save back to file
    print(f"\nSaving to: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Done! All semantic fixes applied successfully.")


if __name__ == "__main__":
    main()
