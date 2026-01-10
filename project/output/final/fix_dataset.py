#!/usr/bin/env python3
"""Fix T3 Benchmark dataset issues:
1. Remove duplicate scenarios (keep first occurrence)
2. Reassign sequential case_ids (original cases keep their IDs, new cases get 8.50+)
3. Remove any cases with unexpanded template patterns
"""

import json
import re
from collections import Counter
from pathlib import Path


def load_dataset(filepath: str) -> list[dict]:
    """Load the JSON dataset."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_dataset(filepath: str, data: list[dict]) -> None:
    """Save the JSON dataset."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def has_unexpanded_template(case: dict) -> bool:
    """Check if a case has unexpanded template placeholders."""
    scenario = case.get('scenario', '')
    # Check for common unexpanded patterns
    patterns = [
        r'\{TRAP_TYPE\}',
        r'\{DOMAIN\}',
        r'\{SUBDOMAIN\}',
        r'\{[A-Z_]+\}',  # Generic placeholder pattern
        r'Example\s+\{',
    ]
    for pattern in patterns:
        if re.search(pattern, scenario):
            return True
    return False


def fix_dataset(filepath: str) -> dict:
    """Fix the dataset and return statistics."""
    data = load_dataset(filepath)

    stats = {
        'before': {
            'total_cases': len(data),
            'unique_ids': len(set(c['case_id'] for c in data)),
            'unique_scenarios': len(set(c['scenario'] for c in data)),
            'original_cases': sum(1 for c in data if c.get('is_original', False)),
            'generated_cases': sum(1 for c in data if not c.get('is_original', False)),
        }
    }

    # Count ID duplicates
    id_counts = Counter(c['case_id'] for c in data)
    stats['before']['duplicate_ids'] = sum(1 for c in id_counts.values() if c > 1)
    stats['before']['most_common_id'] = id_counts.most_common(1)[0] if id_counts else None

    # Count scenario duplicates
    scenario_counts = Counter(c['scenario'] for c in data)
    stats['before']['duplicate_scenarios'] = sum(1 for c in scenario_counts.values() if c > 1)

    # Track Pearl level distribution before
    pearl_before = Counter(c.get('annotations', {}).get('pearl_level', 'Unknown') for c in data)
    stats['before']['pearl_distribution'] = dict(pearl_before)

    # Step 1: Separate original and generated cases
    original_cases = [c for c in data if c.get('is_original', False)]
    generated_cases = [c for c in data if not c.get('is_original', False)]

    # Step 2: Remove cases with unexpanded templates
    template_removed = []
    clean_generated = []
    for case in generated_cases:
        if has_unexpanded_template(case):
            template_removed.append(case['scenario'][:80])
        else:
            clean_generated.append(case)

    stats['template_removed_count'] = len(template_removed)
    stats['template_removed_examples'] = template_removed[:3]

    # Step 3: Remove duplicate scenarios from generated cases
    # Keep track of all scenarios (including originals)
    seen_scenarios = set(c['scenario'] for c in original_cases)

    unique_generated = []
    duplicate_removed = []
    for case in clean_generated:
        if case['scenario'] not in seen_scenarios:
            seen_scenarios.add(case['scenario'])
            unique_generated.append(case)
        else:
            duplicate_removed.append(case['scenario'][:80])

    stats['duplicates_removed'] = len(duplicate_removed)
    stats['duplicate_examples'] = duplicate_removed[:5]

    # Step 4: Reassign case_ids
    # Original cases keep their IDs (should be 8.1 through 8.49)
    # Sort originals by their numeric ID to maintain order
    def get_numeric_id(case):
        try:
            return float(case['case_id'])
        except (ValueError, TypeError):
            return 999.0

    original_cases.sort(key=get_numeric_id)

    # Verify original IDs are in expected range
    original_ids = [c['case_id'] for c in original_cases]
    stats['original_id_range'] = f"{min(original_ids)} to {max(original_ids)}" if original_ids else "N/A"

    # Assign new sequential IDs to generated cases starting from 8.50
    next_id = 50
    for case in unique_generated:
        case['case_id'] = f"8.{next_id}"
        next_id += 1

    # Step 5: Combine and save
    fixed_data = original_cases + unique_generated

    # Calculate after statistics
    stats['after'] = {
        'total_cases': len(fixed_data),
        'unique_ids': len(set(c['case_id'] for c in fixed_data)),
        'unique_scenarios': len(set(c['scenario'] for c in fixed_data)),
        'original_cases': len(original_cases),
        'generated_cases': len(unique_generated),
    }

    # Pearl level distribution after
    pearl_after = Counter(c.get('annotations', {}).get('pearl_level', 'Unknown') for c in fixed_data)
    stats['after']['pearl_distribution'] = dict(pearl_after)

    # ID range after
    all_ids = [c['case_id'] for c in fixed_data]
    stats['after']['id_range'] = f"{min(all_ids, key=lambda x: float(x.split('.')[-1]))} to {max(all_ids, key=lambda x: float(x.split('.')[-1]))}"

    # Save fixed dataset
    save_dataset(filepath, fixed_data)

    return stats


def main():
    filepath = "/Users/fernandotn/Projects/AGI/project/output/final/GroupI1_dataset.json"

    print("=" * 70)
    print("T3 BENCHMARK DATASET FIX")
    print("=" * 70)

    stats = fix_dataset(filepath)

    print("\n### BEFORE FIX ###")
    print(f"  Total cases:        {stats['before']['total_cases']}")
    print(f"  Unique IDs:         {stats['before']['unique_ids']}")
    print(f"  Unique scenarios:   {stats['before']['unique_scenarios']}")
    print(f"  Original cases:     {stats['before']['original_cases']}")
    print(f"  Generated cases:    {stats['before']['generated_cases']}")
    print(f"  Duplicate IDs:      {stats['before']['duplicate_ids']}")
    if stats['before']['most_common_id']:
        print(f"  Most common ID:     {stats['before']['most_common_id'][0]} ({stats['before']['most_common_id'][1]} occurrences)")
    print(f"  Duplicate scenarios: {stats['before']['duplicate_scenarios']}")
    print(f"\n  Pearl distribution: {stats['before']['pearl_distribution']}")

    print("\n### CHANGES ###")
    print(f"  Template patterns removed: {stats['template_removed_count']}")
    if stats['template_removed_examples']:
        for ex in stats['template_removed_examples']:
            print(f"    - {ex}...")
    print(f"  Duplicate scenarios removed: {stats['duplicates_removed']}")
    if stats['duplicate_examples']:
        for ex in stats['duplicate_examples'][:3]:
            print(f"    - {ex}...")
    print(f"  Original ID range preserved: {stats['original_id_range']}")

    print("\n### AFTER FIX ###")
    print(f"  Total cases:        {stats['after']['total_cases']}")
    print(f"  Unique IDs:         {stats['after']['unique_ids']}")
    print(f"  Unique scenarios:   {stats['after']['unique_scenarios']}")
    print(f"  Original cases:     {stats['after']['original_cases']}")
    print(f"  Generated cases:    {stats['after']['generated_cases']}")
    print(f"  ID range:           {stats['after']['id_range']}")
    print(f"\n  Pearl distribution: {stats['after']['pearl_distribution']}")

    print("\n" + "=" * 70)
    print("Dataset fixed and saved!")
    print("=" * 70)


if __name__ == "__main__":
    main()
