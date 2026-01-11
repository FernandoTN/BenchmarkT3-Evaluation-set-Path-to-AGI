#!/usr/bin/env python3
"""
Fix variable naming in specific cases of GroupI1_dataset.json.
Renames variables to use Z/U convention for consistency.
"""

import json
from pathlib import Path


def rename_variable_in_case(case: dict, old_var: str, new_var: str) -> list[str]:
    """
    Rename a variable in a case's variables dict and all text fields.
    Returns a list of changes made.
    """
    changes = []

    # 1. Update variables dictionary
    if old_var in case.get("variables", {}):
        case["variables"][new_var] = case["variables"].pop(old_var)
        changes.append(f"  variables.{old_var} -> variables.{new_var}")

    # 2. Update text fields that may contain the variable reference
    text_fields = ["scenario", "wise_refusal"]
    list_fields = ["correct_reasoning"]
    nested_fields = [("ground_truth", "justification")]

    pattern_old = f"({old_var})"
    pattern_new = f"({new_var})"

    for field in text_fields:
        if field in case and pattern_old in case[field]:
            case[field] = case[field].replace(pattern_old, pattern_new)
            changes.append(f"  {field}: ({old_var}) -> ({new_var})")

    for field in list_fields:
        if field in case:
            for i, item in enumerate(case[field]):
                if pattern_old in item:
                    case[field][i] = item.replace(pattern_old, pattern_new)
                    changes.append(f"  {field}[{i}]: ({old_var}) -> ({new_var})")

    for parent, child in nested_fields:
        if parent in case and child in case[parent]:
            if pattern_old in case[parent][child]:
                case[parent][child] = case[parent][child].replace(pattern_old, pattern_new)
                changes.append(f"  {parent}.{child}: ({old_var}) -> ({new_var})")

    # 3. Update hidden_structure if present
    if "hidden_structure" in case and pattern_old in case["hidden_structure"]:
        case["hidden_structure"] = case["hidden_structure"].replace(pattern_old, pattern_new)
        changes.append(f"  hidden_structure: ({old_var}) -> ({new_var})")

    # 4. Update causal_structure in annotations if present
    if "annotations" in case and "causal_structure" in case["annotations"]:
        causal = case["annotations"]["causal_structure"]
        # Check for patterns like "X -> Y" or just the letter
        if old_var in causal:
            # Replace standalone variable letters carefully
            # Use word boundary approach: only replace if it's standalone
            import re
            new_causal = re.sub(rf'\b{old_var}\b', new_var, causal)
            if new_causal != causal:
                case["annotations"]["causal_structure"] = new_causal
                changes.append(f"  annotations.causal_structure: {old_var} -> {new_var}")

    return changes


def main():
    filepath = Path("/Users/fernandotn/Projects/AGI/project/output/final/GroupI1_dataset.json")

    print(f"Loading {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Define the renaming rules for each case
    rename_rules = {
        "8.32": [("L", "Z")],
        "8.33": [("K", "Z")],
        "8.34": [("T", "Z"), ("K", "U")],
        "8.35": [("W", "Z"), ("A", "U")],
        "8.36": [("S", "Z")],
        "8.42": [("R", "Z")],
        "8.44": [("A", "Z")],
    }

    # Find and update each case
    cases_updated = 0
    for case in data:
        case_id = case.get("case_id", "")
        if case_id in rename_rules:
            print(f"\n=== Case {case_id} ===")
            all_changes = []
            for old_var, new_var in rename_rules[case_id]:
                changes = rename_variable_in_case(case, old_var, new_var)
                all_changes.extend(changes)

            if all_changes:
                for change in all_changes:
                    print(change)
                cases_updated += 1
            else:
                print("  No changes needed (variables may already be renamed)")

    # Save the updated data
    print(f"\n=== Saving to {filepath} ===")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Updated {cases_updated} cases.")


if __name__ == "__main__":
    main()
