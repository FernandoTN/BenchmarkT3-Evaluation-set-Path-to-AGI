"""
AGI Causal Reasoning Benchmark - Generators Package.

This package provides the case generation framework for creating
benchmark cases that test AI systems' causal reasoning capabilities.

The generator framework is designed around Pearl's Ladder of Causation:
- L1 (Association): Observational/correlational reasoning
- L2 (Intervention): Interventional do-calculus reasoning
- L3 (Counterfactual): Counterfactual reasoning with structural equations

Each generator specializes in a specific trap type while maintaining
proper distributions across Pearl levels and difficulty.

Modules:
    base_generator: Abstract base class and utilities for all generators

Classes:
    BaseGenerator: Abstract base class for case generators
    ExampleGenerator: Reference implementation for testing
    GenerationStats: Statistics tracking dataclass
    CRITResult: CRIT evaluation result dataclass

Type Definitions:
    CaseData: TypedDict for complete case structure
    Variable: TypedDict for causal variable definition
    Annotations: TypedDict for case metadata
    GroundTruth: TypedDict for L3 counterfactual verdicts

Enums:
    PearlLevel: L1, L2, L3 enumeration
    Difficulty: Easy, Medium, Hard enumeration
    GroundTruthVerdict: VALID, INVALID, CONDITIONAL enumeration

Utility Functions:
    load_instruction_files: Load markdown instruction documents
    load_original_cases: Load reference cases from JSON
    save_generated_cases: Save generated cases to JSON
    validate_case_id_format: Validate case ID format (8.XXX)

Usage:
    from generators import BaseGenerator, CaseData, PearlLevel
    from generators import load_original_cases, save_generated_cases

Example:
    >>> from generators import ExampleGenerator
    >>> generator = ExampleGenerator("orchestrator/config.json")
    >>> cases = generator.generate_batch(10, "GOODHART", ["RLHF", "Scaling"])
    >>> save_generated_cases(cases, "output/batch_001.json")
"""

from generators.base_generator import (
    # Main classes
    BaseGenerator,
    ExampleGenerator,

    # Data classes
    GenerationStats,
    CRITResult,

    # Enums
    PearlLevel,
    Difficulty,
    GroundTruthVerdict,

    # Type definitions
    CaseData,
    Variable,
    Annotations,
    GroundTruth,

    # Utility functions
    load_instruction_files,
    load_original_cases,
    save_generated_cases,
    validate_case_id_format,

    # Constants
    DEFAULT_PEARL_DISTRIBUTIONS,
)

# Category-specific generators
from generators.gen_03_conf_med import (
    ConfMedGenerator,
    CONF_MED_SUBTYPES,
    generate_cases as generate_conf_med_cases,
)

from generators.gen_04_instrumental import (
    InstrumentalGenerator,
    INSTRUMENTAL_SUBTYPES,
    generate_cases as generate_instrumental_cases,
)

from generators.gen_05_selection_spurious import (
    SelectionSpuriousGenerator,
    SelectionSpuriousSubtype,
    SelectionSpuriousSubdomain,
    SelectionTemplate,
)

from generators.gen_06_specification import (
    SpecificationGenerator,
    SpecificationSubtype,
    SpecificationSubdomain,
    SpecificationTemplate,
)

# Goodhart generator
from generators.gen_01_goodhart import (
    GoodhartGenerator,
    GoodhartSubtype,
    ScenarioTemplate as GoodhartTemplate,
)

# Counterfactual generator
from generators.gen_02_counterfactual import (
    CounterfactualGenerator,
    CounterfactualSubtype,
    CounterfactualTemplate,
)

__all__ = [
    # Main classes
    "BaseGenerator",
    "ExampleGenerator",

    # Category-specific generators
    "GoodhartGenerator",
    "CounterfactualGenerator",
    "ConfMedGenerator",
    "InstrumentalGenerator",
    "SelectionSpuriousGenerator",
    "SpecificationGenerator",

    # Subtype definitions
    "GoodhartSubtype",
    "GoodhartTemplate",
    "CounterfactualSubtype",
    "CounterfactualTemplate",
    "CONF_MED_SUBTYPES",
    "INSTRUMENTAL_SUBTYPES",
    "SelectionSpuriousSubtype",
    "SelectionSpuriousSubdomain",
    "SelectionTemplate",
    "SpecificationSubtype",
    "SpecificationSubdomain",
    "SpecificationTemplate",

    # Convenience generation functions
    "generate_conf_med_cases",
    "generate_instrumental_cases",

    # Data classes
    "GenerationStats",
    "CRITResult",

    # Enums
    "PearlLevel",
    "Difficulty",
    "GroundTruthVerdict",

    # Type definitions
    "CaseData",
    "Variable",
    "Annotations",
    "GroundTruth",

    # Utility functions
    "load_instruction_files",
    "load_original_cases",
    "save_generated_cases",
    "validate_case_id_format",

    # Constants
    "DEFAULT_PEARL_DISTRIBUTIONS",
]

__version__ = "1.0.0"
__author__ = "AGI Benchmark Team"
