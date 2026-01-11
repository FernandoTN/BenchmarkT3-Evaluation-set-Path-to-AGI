#!/usr/bin/env python3
"""Remove [REVISED] prefix from scenario field for specific cases."""

import json
from pathlib import Path

# Cases that need the [REVISED] prefix removed
CASES_TO_FIX = [
    "8.56", "8.57", "8.58", "8.59", "8.60", "8.61", "8.62", "8.63", "8.66",
    "8.73", "8.74", "8.75", "8.76", "8.77", "8.78", "8.79", "8.80", "8.81",
    "8.82", "8.83", "8.91", "8.92", "8.93", "8.94", "8.95", "8.96", "8.97",
    "8.98", "8.99", "8.110", "8.111", "8.112", "8.113", "8.114", "8.115",
    "8.124", "8.125", "8.126", "8.127", "8.128", "8.129", "8.130", "8.131",
    "8.135", "8.136", "8.137", "8.138", "8.139", "8.140", "8.141", "8.142",
    "8.143", "8.144"
]

PREFIX = "[REVISED] "

def main():
    json_path = Path("/Users/fernandotn/Projects/AGI/project/output/final/GroupI1_dataset.json")

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixed_count = 0
    cases_to_fix_set = set(CASES_TO_FIX)

    for case in data:
        case_id = case.get("case_id", "")
        if case_id in cases_to_fix_set:
            scenario = case.get("scenario", "")
            if scenario.startswith(PREFIX):
                case["scenario"] = scenario[len(PREFIX):]
                fixed_count += 1
                print(f"Fixed case {case_id}")
            else:
                print(f"Case {case_id}: No [REVISED] prefix found")

    # Save back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nTotal cases fixed: {fixed_count}")
    print(f"Expected to fix: {len(CASES_TO_FIX)}")

if __name__ == "__main__":
    main()
