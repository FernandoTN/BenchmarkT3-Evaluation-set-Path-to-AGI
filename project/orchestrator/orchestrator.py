#!/usr/bin/env python3
"""
T3 Benchmark Orchestrator - Main Pipeline Coordinator.

This module coordinates the complete T3 Benchmark generation pipeline:
1. Generation Phase: Distribute work to 8 generators, produce 405 new cases
2. Validation Phase: Run DAG, Content, and Cross validators
3. Revision Phase: Process revision queue with up to 3 cycles per case
4. Finalization: Merge validated cases with original 45, produce final dataset

The orchestrator implements:
- Pearl's Ladder distribution (L1: 10-12%, L2: 66-70%, L3: 18-21%)
- CRIT (Causal Reasoning Integrity Test) quality scoring
- SocraSynth methodology for case generation
- Progress tracking and crash recovery via checkpoints
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type

# Ensure project directory is in path for generator imports
_project_dir = Path(__file__).parent.parent
if str(_project_dir) not in sys.path:
    sys.path.insert(0, str(_project_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("orchestrator.log"),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# Generator Imports and Mapping
# =============================================================================

# Lazy import function to avoid circular imports and missing dependencies
def _get_generator_class(generator_id: str) -> Optional[Type]:
    """
    Lazily import and return the generator class for a given generator ID.

    Args:
        generator_id: The generator identifier (e.g., "gen_01_goodhart").

    Returns:
        The generator class if available, None otherwise.
    """
    try:
        if generator_id == "gen_01_goodhart":
            from generators.gen_01_goodhart import GoodhartGenerator
            return GoodhartGenerator
        elif generator_id == "gen_02_counterfactual":
            from generators.gen_02_counterfactual import CounterfactualGenerator
            return CounterfactualGenerator
        elif generator_id == "gen_03_conf_med":
            from generators.gen_03_conf_med import ConfMedGenerator
            return ConfMedGenerator
        elif generator_id == "gen_04_instrumental":
            from generators.gen_04_instrumental import InstrumentalGenerator
            return InstrumentalGenerator
        elif generator_id == "gen_05_selection_spurious":
            from generators.gen_05_selection_spurious import SelectionSpuriousGenerator
            return SelectionSpuriousGenerator
        elif generator_id == "gen_06_specification":
            from generators.gen_06_specification import SpecificationGenerator
            return SpecificationGenerator
        elif generator_id == "gen_07_feedback_loops":
            from generators.gen_07_feedback_loops import FeedbackLoopsGenerator
            return FeedbackLoopsGenerator
        elif generator_id == "gen_08_other_traps":
            from generators.gen_08_other_traps import OtherTrapsGenerator
            return OtherTrapsGenerator
        else:
            return None
    except ImportError as e:
        logger.warning("Failed to import generator for %s: %s", generator_id, e)
        return None


# =============================================================================
# Atomic ID Counter for Thread-Safe Case ID Generation
# =============================================================================

from threading import Lock
from itertools import count


class AtomicIDCounter:
    """
    Thread-safe atomic counter for generating unique case IDs.

    This prevents duplicate case IDs when multiple generators or threads
    are creating cases concurrently.
    """

    def __init__(self, start: int = 100) -> None:
        """
        Initialize the counter.

        Args:
            start: Starting value for the counter (default 100 to avoid
                   collision with original cases 8.1 - 8.49).
        """
        self._counter = count(start)
        self._lock = Lock()

    def next_id(self) -> int:
        """
        Get the next unique ID in a thread-safe manner.

        Returns:
            The next sequential integer ID.
        """
        with self._lock:
            return next(self._counter)


# Mapping from generator IDs to their expected class names (for logging)
GENERATOR_CLASS_NAMES = {
    "gen_01_goodhart": "GoodhartGenerator",
    "gen_02_counterfactual": "CounterfactualGenerator",
    "gen_03_conf_med": "ConfMedGenerator",
    "gen_04_instrumental": "InstrumentalGenerator",
    "gen_05_selection_spurious": "SelectionSpuriousGenerator",
    "gen_06_specification": "SpecificationGenerator",
    "gen_07_feedback_loops": "FeedbackLoopsGenerator",
    "gen_08_other_traps": "OtherTrapsGenerator",
}


# =============================================================================
# Enums and Constants
# =============================================================================


class PipelinePhase(str, Enum):
    """Pipeline execution phases."""

    SETUP = "setup"
    GENERATION = "generation"
    VALIDATION = "validation"
    REVISION = "revision"
    FINALIZATION = "finalization"
    COMPLETE = "complete"


class PhaseStatus(str, Enum):
    """Status of a pipeline phase."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueSeverity(str, Enum):
    """Validation issue severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ValidationIssue:
    """Represents a validation issue for a case."""

    case_id: str
    rule: str
    severity: IssueSeverity
    message: str
    suggestion: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "rule": self.rule,
            "severity": self.severity.value,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class RevisionQueueItem:
    """An item in the revision queue."""

    case_id: str
    case_data: dict[str, Any]
    issues: list[ValidationIssue]
    revision_cycle: int = 0
    generator_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "revision_cycle": self.revision_cycle,
            "generator_id": self.generator_id,
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class PipelineStats:
    """Statistics for the pipeline run."""

    total_generated: int = 0
    total_validated: int = 0
    total_accepted: int = 0
    total_rejected: int = 0
    total_revised: int = 0
    revision_cycles: dict[str, int] = field(
        default_factory=lambda: {"cycle_1": 0, "cycle_2": 0, "cycle_3": 0}
    )
    severity_counts: dict[str, int] = field(
        default_factory=lambda: {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    )
    crit_scores: list[float] = field(default_factory=list)
    validation_pass_rate: float = 0.0
    dag_validity_rate: float = 0.0

    @property
    def avg_crit_score(self) -> float:
        """Calculate average CRIT score."""
        if not self.crit_scores:
            return 0.0
        return sum(self.crit_scores) / len(self.crit_scores)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_generated": self.total_generated,
            "total_validated": self.total_validated,
            "total_accepted": self.total_accepted,
            "total_rejected": self.total_rejected,
            "total_revised": self.total_revised,
            "revision_cycles": self.revision_cycles,
            "severity_counts": self.severity_counts,
            "avg_crit_score": round(self.avg_crit_score, 2),
            "validation_pass_rate": round(self.validation_pass_rate, 4),
            "dag_validity_rate": round(self.dag_validity_rate, 4),
        }


# =============================================================================
# Orchestrator Class
# =============================================================================


class Orchestrator:
    """
    Main coordinator for the T3 Benchmark generation pipeline.

    Orchestrates generation, validation, revision, and finalization
    of 450 benchmark cases for AI safety evaluation.

    Attributes:
        config: Loaded configuration dictionary
        config_path: Path to configuration file
        stats: Pipeline statistics tracker
        original_cases: Original 45 benchmark cases
        generated_cases: Cases produced during generation phase
        validated_cases: Cases that passed validation
        revision_queue: Queue of cases needing revision
        failed_cases: Cases that failed after max revision cycles
    """

    MAX_REVISION_CYCLES = 3
    TARGET_TOTAL_CASES = 450
    ORIGINAL_CASES_COUNT = 45
    NEW_CASES_TARGET = 405

    def __init__(self, config_path: str = "config.json") -> None:
        """
        Initialize the orchestrator with configuration.

        Args:
            config_path: Path to orchestrator/config.json

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config JSON is malformed
        """
        self.config_path = Path(config_path).resolve()
        self.config = self._load_config()
        self.stats = PipelineStats()

        # Resolve paths relative to config file
        self._base_path = self.config_path.parent
        self._paths = self._resolve_paths()

        # Data containers
        self.original_cases: list[dict[str, Any]] = []
        self.generated_cases: list[dict[str, Any]] = []
        self.validated_cases: list[dict[str, Any]] = []
        self.revision_queue: list[RevisionQueueItem] = []
        self.failed_cases: list[dict[str, Any]] = []

        # Validators (lazy loaded)
        self._dag_validator: Any = None
        self._content_validator: Any = None
        self._cross_validator: Any = None

        # Atomic ID counter for thread-safe case ID generation
        self._id_counter = AtomicIDCounter(100)

        # Generator configurations
        self.generator_configs = self.config.get(
            "generator_batch_allocations", {}
        ).get("generators", {})

        # Progress tracker
        self._progress_tracker_path = self._base_path / "progress_tracker.json"

        # Initialize resources
        self._initialize()

        logger.info(
            "Orchestrator initialized with config from %s", self.config_path
        )

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, encoding="utf-8") as f:
            return json.load(f)

    def _resolve_paths(self) -> dict[str, Path]:
        """Resolve all paths relative to config file location."""
        paths_config = self.config.get("paths", {})

        resolved = {}
        for key, relative_path in paths_config.items():
            resolved[key] = (self._base_path / relative_path).resolve()

        # Ensure output directories exist
        output_dir = resolved.get("output_dir", self._base_path.parent / "output")
        (output_dir / "generated").mkdir(parents=True, exist_ok=True)
        (output_dir / "validated").mkdir(parents=True, exist_ok=True)
        (output_dir / "revision").mkdir(parents=True, exist_ok=True)
        (output_dir / "final").mkdir(parents=True, exist_ok=True)

        resolved["output_dir"] = output_dir

        return resolved

    def _initialize(self) -> None:
        """Initialize resources and load original cases."""
        # Load original cases
        original_cases_path = self._paths.get(
            "categories_dir", self._base_path.parent / "categories"
        ) / "original_cases.json"

        if original_cases_path.exists():
            with open(original_cases_path, encoding="utf-8") as f:
                self.original_cases = json.load(f)
                logger.info(
                    "Loaded %d original cases from %s",
                    len(self.original_cases),
                    original_cases_path,
                )
        else:
            logger.warning(
                "Original cases file not found at %s", original_cases_path
            )

        # Load instruction files for context
        self._load_instructions()

    def _load_instructions(self) -> None:
        """Load instruction markdown files for generator context."""
        instructions_dir = self._paths.get(
            "instructions_dir", self._base_path.parent / "instructions"
        )

        self.instructions: dict[str, str] = {}

        if instructions_dir.exists():
            for md_file in instructions_dir.glob("*.md"):
                key = md_file.stem.lower()
                with open(md_file, encoding="utf-8") as f:
                    self.instructions[key] = f.read()
            logger.info(
                "Loaded %d instruction files", len(self.instructions)
            )

    # =========================================================================
    # Validator Access (Lazy Loading)
    # =========================================================================

    @property
    def dag_validator(self) -> Any:
        """Get or create DAG validator instance."""
        if self._dag_validator is None:
            try:
                # Import from validators directory
                validators_dir = self._paths.get(
                    "validators_dir", self._base_path.parent / "validators"
                )
                sys.path.insert(0, str(validators_dir.parent))
                from validators.dag_validator import DAGValidator

                self._dag_validator = DAGValidator()
            except ImportError as e:
                logger.error("Failed to import DAGValidator: %s", e)
                raise
        return self._dag_validator

    @property
    def content_validator(self) -> Any:
        """Get or create Content validator instance."""
        if self._content_validator is None:
            try:
                validators_dir = self._paths.get(
                    "validators_dir", self._base_path.parent / "validators"
                )
                sys.path.insert(0, str(validators_dir.parent))
                from validators.content_validator import ContentValidator

                self._content_validator = ContentValidator()
            except ImportError as e:
                logger.error("Failed to import ContentValidator: %s", e)
                raise
        return self._content_validator

    @property
    def cross_validator(self) -> Any:
        """Get or create Cross validator instance."""
        if self._cross_validator is None:
            try:
                validators_dir = self._paths.get(
                    "validators_dir", self._base_path.parent / "validators"
                )
                sys.path.insert(0, str(validators_dir.parent))
                from validators.cross_validator import CrossValidator

                self._cross_validator = CrossValidator(str(self.config_path))
            except ImportError as e:
                logger.error("Failed to import CrossValidator: %s", e)
                raise
        return self._cross_validator

    # =========================================================================
    # Main Orchestration Methods
    # =========================================================================

    def run_full_pipeline(self) -> dict[str, Any]:
        """
        Run complete generation, validation, revision, finalization pipeline.

        Returns:
            Dictionary containing pipeline results and report path.

        Raises:
            RuntimeError: If any critical pipeline phase fails.
        """
        logger.info("=" * 60)
        logger.info("Starting T3 Benchmark Generation Pipeline")
        logger.info("=" * 60)

        start_time = datetime.now()

        # Reset global ID counter to ensure unique IDs
        from generators.base_generator import reset_global_id_counter
        reset_global_id_counter(100)
        logger.info("Reset global ID counter to 100")

        try:
            # Phase 1: Generation
            self._update_progress(PipelinePhase.GENERATION, {"status": "starting"})
            self.run_generation_phase()
            self._save_checkpoint()

            # Phase 2: Validation
            self._update_progress(PipelinePhase.VALIDATION, {"status": "starting"})
            self.run_validation_phase()
            self._save_checkpoint()

            # Phase 3: Revision
            self._update_progress(PipelinePhase.REVISION, {"status": "starting"})
            self.run_revision_phase()
            self._save_checkpoint()

            # Phase 4: Finalization
            self._update_progress(PipelinePhase.FINALIZATION, {"status": "starting"})
            self.finalize_dataset()

            # Generate report
            report_path = self.generate_report()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self._update_progress(
                PipelinePhase.COMPLETE,
                {
                    "status": "completed",
                    "duration_seconds": duration,
                    "report_path": str(report_path),
                },
            )

            logger.info("=" * 60)
            logger.info(
                "Pipeline completed in %.2f seconds", duration
            )
            logger.info("Report generated at: %s", report_path)
            logger.info("=" * 60)

            return {
                "status": "success",
                "duration_seconds": duration,
                "stats": self.stats.to_dict(),
                "report_path": str(report_path),
                "total_cases": len(self.validated_cases) + len(self.original_cases),
            }

        except Exception as e:
            logger.exception("Pipeline failed with error: %s", e)
            self._update_progress(
                PipelinePhase.GENERATION,
                {"status": "failed", "error": str(e)},
            )
            raise RuntimeError(f"Pipeline failed: {e}") from e

    def run_generation_phase(self) -> None:
        """
        Distribute work to 8 generators, produce 405 new cases.

        For each generator configuration:
        1. Load generator (or use placeholder for this implementation)
        2. Generate batch of cases according to allocation
        3. Save to output/generated/{category}/
        4. Update progress_tracker.json
        """
        logger.info("-" * 60)
        logger.info("PHASE 1: Generation")
        logger.info("-" * 60)

        self._update_phase_status(PipelinePhase.GENERATION, PhaseStatus.IN_PROGRESS)

        total_allocated = 0
        for gen_id, gen_config in self.generator_configs.items():
            allocation = gen_config.get("allocation", 0)
            trap_type = gen_config.get("primary_trap", "OTHER")
            subdomains = gen_config.get("subdomains", [])

            logger.info(
                "Generator %s: allocation=%d, trap=%s, subdomains=%s",
                gen_id,
                allocation,
                trap_type,
                subdomains,
            )

            try:
                # Generate cases for this batch
                batch_cases = self._generate_batch(
                    gen_id, allocation, trap_type, subdomains
                )

                # Save generated batch
                self._save_generated_batch(gen_id, batch_cases)

                self.generated_cases.extend(batch_cases)
                total_allocated += len(batch_cases)

                # Update progress
                self._update_generator_progress(
                    gen_id, {"generated": len(batch_cases)}
                )

                logger.info(
                    "  Generated %d cases for %s", len(batch_cases), gen_id
                )

            except Exception as e:
                logger.error(
                    "Generator %s failed: %s", gen_id, e
                )
                # Continue with other generators
                continue

        self.stats.total_generated = total_allocated

        logger.info(
            "Generation phase complete: %d cases generated", total_allocated
        )
        self._update_phase_status(PipelinePhase.GENERATION, PhaseStatus.COMPLETED)

    def _generate_batch(
        self,
        generator_id: str,
        allocation: int,
        trap_type: str,
        subdomains: list[str],
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of cases using the category-specific generator.

        This method looks up the appropriate generator class from the
        GENERATOR_MAP and instantiates it to generate cases. Falls back
        to ExampleGenerator only if the specific generator is unavailable
        or fails to implement generate_batch correctly.

        Args:
            generator_id: Identifier for the generator (e.g., "gen_01_goodhart")
            allocation: Number of cases to generate
            trap_type: Primary trap type for cases
            subdomains: List of subdomains to distribute cases across

        Returns:
            List of generated case dictionaries
        """
        cases: list[dict[str, Any]] = []

        # Ensure generators directory is in path
        generators_dir = self._paths.get(
            "generators_dir", self._base_path.parent / "generators"
        )
        if str(generators_dir.parent) not in sys.path:
            sys.path.insert(0, str(generators_dir.parent))

        # Try to use the category-specific generator
        generator_class = _get_generator_class(generator_id)

        if generator_class is not None:
            try:
                generator = generator_class(str(self.config_path))
                cases = generator.generate_batch(allocation, trap_type, subdomains)

                # Add generator_id to each case for tracking
                for case in cases:
                    case["_generator_id"] = generator_id

                logger.info(
                    "Used %s for %s: generated %d cases",
                    GENERATOR_CLASS_NAMES.get(generator_id, generator_id),
                    generator_id,
                    len(cases),
                )
                return cases

            except AttributeError as e:
                logger.warning(
                    "Generator %s does not implement generate_batch correctly: %s",
                    generator_id,
                    e,
                )
            except TypeError as e:
                logger.warning(
                    "Generator %s has incompatible generate_batch signature: %s",
                    generator_id,
                    e,
                )
            except Exception as e:
                logger.warning(
                    "Generator %s failed during generation: %s",
                    generator_id,
                    e,
                )

        # Fallback to ExampleGenerator if specific generator is unavailable
        logger.info(
            "Falling back to ExampleGenerator for %s", generator_id
        )
        try:
            from generators.base_generator import ExampleGenerator

            generator = ExampleGenerator(str(self.config_path))
            cases = generator.generate_batch(allocation, trap_type, subdomains)

            # Add generator_id to each case for tracking
            for case in cases:
                case["_generator_id"] = generator_id

            logger.info(
                "Used ExampleGenerator (fallback) for %s: generated %d cases",
                generator_id,
                len(cases),
            )
            return cases

        except ImportError:
            logger.warning(
                "ExampleGenerator not available, using placeholder for %s",
                generator_id,
            )

        # Last resort: placeholder generation
        cases = self._generate_placeholder_batch(
            generator_id, allocation, trap_type, subdomains
        )
        return cases

    def _generate_placeholder_batch(
        self,
        generator_id: str,
        allocation: int,
        trap_type: str,
        subdomains: list[str],
    ) -> list[dict[str, Any]]:
        """
        Generate placeholder cases when no generator is available.

        This is a fallback for testing and development purposes.

        Args:
            generator_id: Identifier for the generator
            allocation: Number of cases to generate
            trap_type: Primary trap type for cases
            subdomains: List of subdomains to distribute cases across

        Returns:
            List of placeholder case dictionaries
        """
        cases: list[dict[str, Any]] = []
        base_case_id = self._get_next_case_id_start()

        for i in range(allocation):
            subdomain = subdomains[i % len(subdomains)] if subdomains else "General"
            pearl_level = self._assign_pearl_level(trap_type)

            case: dict[str, Any] = {
                "case_id": f"8.{base_case_id + i}",
                "scenario": f"[PLACEHOLDER] {trap_type} scenario in {subdomain} domain.",
                "variables": {
                    "X": {"name": "Variable X", "role": "treatment"},
                    "Y": {"name": "Variable Y", "role": "outcome"},
                    "Z": {"name": "Variable Z", "role": "confounder"},
                },
                "annotations": {
                    "pearl_level": pearl_level,
                    "domain": "D8",
                    "trap_type": trap_type,
                    "trap_subtype": f"{trap_type} Variant",
                    "difficulty": self._assign_difficulty(),
                    "subdomain": subdomain,
                    "causal_structure": "X -> Y <- Z",
                    "key_insight": f"Key insight for {trap_type}",
                },
                "correct_reasoning": [
                    f"Step 1: Identify {trap_type} pattern",
                    "Step 2: Analyze causal structure",
                    "Step 3: Apply correct reasoning",
                ],
                "wise_refusal": (
                    f"This is a {trap_type} trap. The correct analysis requires "
                    f"understanding the hidden causal structure between X, Y, and Z. "
                    f"Simply observing correlation is insufficient for causal claims."
                ),
                "is_original": False,
                "original_case_ref": None,
                "_generator_id": generator_id,
            }

            # Add level-specific fields
            if pearl_level == "L2":
                case["hidden_structure"] = (
                    f"The hidden causal mechanism involves {trap_type}."
                )
            elif pearl_level == "L3":
                case["ground_truth"] = {
                    "verdict": self._assign_ground_truth_verdict(),
                    "justification": (
                        f"The counterfactual claim depends on the {trap_type} "
                        "structural assumptions."
                    ),
                }

            cases.append(case)

        logger.warning(
            "Generated %d placeholder cases for %s (no generator available)",
            len(cases),
            generator_id,
        )
        return cases

    def _get_next_case_id_start(self) -> int:
        """
        Get a unique case ID in a thread-safe manner.

        This method uses an atomic counter to prevent duplicate case IDs
        when multiple generators or threads are creating cases concurrently.

        Returns:
            A unique integer for use in case_id (e.g., 8.{return_value}).
        """
        return self._id_counter.next_id()

    def _assign_pearl_level(self, trap_type: str) -> str:
        """Assign Pearl level based on trap type distribution."""
        import random

        # Default distributions by trap type
        distributions = {
            "GOODHART": {"L1": 0.05, "L2": 0.80, "L3": 0.15},
            "COUNTERFACTUAL": {"L1": 0.00, "L2": 0.10, "L3": 0.90},
            "CONF_MED": {"L1": 0.15, "L2": 0.70, "L3": 0.15},
            "INSTRUMENTAL": {"L1": 0.05, "L2": 0.75, "L3": 0.20},
            "SELECTION_SPURIOUS": {"L1": 0.20, "L2": 0.65, "L3": 0.15},
            "SPECIFICATION": {"L1": 0.10, "L2": 0.75, "L3": 0.15},
            "FEEDBACK": {"L1": 0.10, "L2": 0.70, "L3": 0.20},
            "OTHER": {"L1": 0.15, "L2": 0.65, "L3": 0.20},
        }

        dist = distributions.get(trap_type, {"L1": 0.12, "L2": 0.68, "L3": 0.20})

        r = random.random()
        cumulative = 0.0
        for level, prob in dist.items():
            cumulative += prob
            if r <= cumulative:
                return level
        return "L2"

    def _assign_difficulty(self) -> str:
        """Assign difficulty level with balanced distribution."""
        import random

        return random.choice(["Easy", "Medium", "Hard"])

    def _assign_ground_truth_verdict(self) -> str:
        """Assign ground truth verdict for L3 cases."""
        import random

        # Target distribution: VALID 30%, INVALID 20%, CONDITIONAL 50%
        r = random.random()
        if r < 0.30:
            return "VALID"
        elif r < 0.50:
            return "INVALID"
        else:
            return "CONDITIONAL"

    def _save_generated_batch(
        self, generator_id: str, cases: list[dict[str, Any]]
    ) -> None:
        """Save generated batch to output directory."""
        output_dir = self._paths["output_dir"] / "generated"
        output_file = output_dir / f"batch_{generator_id}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)

        logger.info("Saved %d cases to %s", len(cases), output_file)

    def run_validation_phase(self) -> None:
        """
        Run validation on all generated cases.

        For each batch:
        1. Load generated cases
        2. Run DAG validator
        3. Run Content validator
        4. Run Cross validator (duplicates, distribution)
        5. Categorize issues by severity
        6. Queue cases for revision or accept them
        """
        logger.info("-" * 60)
        logger.info("PHASE 2: Validation")
        logger.info("-" * 60)

        self._update_phase_status(PipelinePhase.VALIDATION, PhaseStatus.IN_PROGRESS)

        cases_to_validate = self.generated_cases.copy()
        total_validated = 0
        total_passed = 0
        dag_passed = 0

        for case in cases_to_validate:
            case_id = case.get("case_id", "unknown")
            issues: list[ValidationIssue] = []

            # Run DAG validation
            try:
                dag_results = self.dag_validator.validate(case)
                for result in dag_results:
                    if not result.passed:
                        issues.append(
                            ValidationIssue(
                                case_id=case_id,
                                rule=result.rule,
                                severity=IssueSeverity(result.severity),
                                message=result.message,
                                suggestion=result.suggestion,
                            )
                        )
                        self.stats.severity_counts[result.severity] += 1
                    else:
                        dag_passed += 1
            except Exception as e:
                logger.warning("DAG validation failed for %s: %s", case_id, e)
                issues.append(
                    ValidationIssue(
                        case_id=case_id,
                        rule="DAG-ERROR",
                        severity=IssueSeverity.HIGH,
                        message=f"DAG validation error: {e}",
                    )
                )

            # Run Content validation
            try:
                content_result = self.content_validator.validate(case)
                if not content_result.passes_threshold:
                    for issue_msg in content_result.issues:
                        # Parse severity from message
                        severity = IssueSeverity.MEDIUM
                        if issue_msg.startswith("CRITICAL:"):
                            severity = IssueSeverity.CRITICAL
                        elif issue_msg.startswith("HIGH:"):
                            severity = IssueSeverity.HIGH
                        elif issue_msg.startswith("LOW:"):
                            severity = IssueSeverity.LOW

                        issues.append(
                            ValidationIssue(
                                case_id=case_id,
                                rule="CONTENT",
                                severity=severity,
                                message=issue_msg,
                            )
                        )
                        self.stats.severity_counts[severity.value] += 1

                self.stats.crit_scores.append(content_result.total_score)

            except Exception as e:
                logger.warning("Content validation failed for %s: %s", case_id, e)
                issues.append(
                    ValidationIssue(
                        case_id=case_id,
                        rule="CONTENT-ERROR",
                        severity=IssueSeverity.HIGH,
                        message=f"Content validation error: {e}",
                    )
                )

            total_validated += 1

            # Categorize by severity and queue or accept
            critical_issues = [
                i for i in issues if i.severity == IssueSeverity.CRITICAL
            ]
            high_issues = [i for i in issues if i.severity == IssueSeverity.HIGH]

            if critical_issues or high_issues:
                # Queue for revision
                self.revision_queue.append(
                    RevisionQueueItem(
                        case_id=case_id,
                        case_data=case,
                        issues=issues,
                        revision_cycle=0,
                        generator_id=case.get("_generator_id", "unknown"),
                    )
                )
                logger.debug("Case %s queued for revision", case_id)
            else:
                # Accept case
                self.validated_cases.append(case)
                total_passed += 1

        # Run cross-validation on all cases
        try:
            all_cases = self.validated_cases + [
                item.case_data for item in self.revision_queue
            ]
            cross_result = self.cross_validator.validate(all_cases)

            if cross_result.duplicates:
                logger.warning(
                    "Found %d duplicate cases", cross_result.duplicate_count
                )
                # Mark duplicates for revision
                for dup_pair in cross_result.duplicates:
                    dup_id = dup_pair[1]  # Second case in pair
                    # Find and move to revision queue
                    for case in self.validated_cases[:]:
                        if case.get("case_id") == dup_id:
                            self.validated_cases.remove(case)
                            self.revision_queue.append(
                                RevisionQueueItem(
                                    case_id=dup_id,
                                    case_data=case,
                                    issues=[
                                        ValidationIssue(
                                            case_id=dup_id,
                                            rule="CROSS-DUP",
                                            severity=IssueSeverity.HIGH,
                                            message=f"Duplicate of {dup_pair[0]}",
                                        )
                                    ],
                                    revision_cycle=0,
                                )
                            )
                            break

        except Exception as e:
            logger.warning("Cross validation failed: %s", e)

        # Update stats
        self.stats.total_validated = total_validated
        self.stats.total_accepted = len(self.validated_cases)
        if total_validated > 0:
            self.stats.validation_pass_rate = total_passed / total_validated
            self.stats.dag_validity_rate = dag_passed / (total_validated * 4)  # 4 DAG rules

        logger.info(
            "Validation phase complete: %d validated, %d accepted, %d queued for revision",
            total_validated,
            len(self.validated_cases),
            len(self.revision_queue),
        )

        self._update_phase_status(PipelinePhase.VALIDATION, PhaseStatus.COMPLETED)

    def _validate_id_uniqueness(self) -> bool:
        """
        Validate that all case IDs are unique across generated cases.

        This method checks for duplicate case IDs which can occur if
        the ID generation was not atomic or if cases were merged incorrectly.

        Returns:
            True if all case IDs are unique, False if duplicates found.
        """
        case_ids = [c.get("case_id") for c in self.generated_cases]
        duplicates = [id for id in set(case_ids) if case_ids.count(id) > 1]

        if duplicates:
            logger.critical(
                "Duplicate case IDs detected: %s (count: %d)",
                duplicates,
                len(duplicates),
            )
            return False

        logger.info("ID uniqueness validation passed: %d unique case IDs", len(case_ids))
        return True

    def run_revision_phase(self) -> None:
        """
        Process revision queue with maximum 3 cycles per case.

        For each case needing revision:
        1. Classify failure severity
        2. Apply targeted fixes
        3. Re-validate
        4. If still failing after 3 cycles, mark as failed and regenerate
        """
        logger.info("-" * 60)
        logger.info("PHASE 3: Revision")
        logger.info("-" * 60)

        self._update_phase_status(PipelinePhase.REVISION, PhaseStatus.IN_PROGRESS)

        max_cycles = self.config.get("revision_settings", {}).get(
            "max_revision_cycles", self.MAX_REVISION_CYCLES
        )

        total_revised = 0

        while self.revision_queue:
            item = self.revision_queue.pop(0)
            item.revision_cycle += 1

            cycle_key = f"cycle_{min(item.revision_cycle, 3)}"
            self.stats.revision_cycles[cycle_key] = (
                self.stats.revision_cycles.get(cycle_key, 0) + 1
            )

            logger.info(
                "Revising case %s (cycle %d/%d)",
                item.case_id,
                item.revision_cycle,
                max_cycles,
            )

            if item.revision_cycle > max_cycles:
                # Max cycles exceeded - mark as failed
                logger.warning(
                    "Case %s failed after %d revision cycles",
                    item.case_id,
                    max_cycles,
                )
                self.failed_cases.append(item.case_data)
                self.stats.total_rejected += 1
                continue

            # Apply targeted fixes based on issues
            revised_case = self._apply_revision_fixes(item)
            total_revised += 1

            # Re-validate
            new_issues: list[ValidationIssue] = []

            # DAG validation
            try:
                dag_results = self.dag_validator.validate(revised_case)
                for result in dag_results:
                    if not result.passed:
                        new_issues.append(
                            ValidationIssue(
                                case_id=item.case_id,
                                rule=result.rule,
                                severity=IssueSeverity(result.severity),
                                message=result.message,
                                suggestion=result.suggestion,
                            )
                        )
            except Exception as e:
                new_issues.append(
                    ValidationIssue(
                        case_id=item.case_id,
                        rule="DAG-ERROR",
                        severity=IssueSeverity.HIGH,
                        message=str(e),
                    )
                )

            # Content validation
            try:
                content_result = self.content_validator.validate(revised_case)
                if not content_result.passes_threshold:
                    for issue_msg in content_result.issues:
                        severity = IssueSeverity.MEDIUM
                        if issue_msg.startswith("CRITICAL:"):
                            severity = IssueSeverity.CRITICAL
                        elif issue_msg.startswith("HIGH:"):
                            severity = IssueSeverity.HIGH

                        new_issues.append(
                            ValidationIssue(
                                case_id=item.case_id,
                                rule="CONTENT",
                                severity=severity,
                                message=issue_msg,
                            )
                        )
            except Exception as e:
                new_issues.append(
                    ValidationIssue(
                        case_id=item.case_id,
                        rule="CONTENT-ERROR",
                        severity=IssueSeverity.HIGH,
                        message=str(e),
                    )
                )

            # Check if critical/high issues remain
            critical_or_high = [
                i
                for i in new_issues
                if i.severity in (IssueSeverity.CRITICAL, IssueSeverity.HIGH)
            ]

            if critical_or_high:
                # Re-queue for another revision cycle
                self.revision_queue.append(
                    RevisionQueueItem(
                        case_id=item.case_id,
                        case_data=revised_case,
                        issues=new_issues,
                        revision_cycle=item.revision_cycle,
                        generator_id=item.generator_id,
                    )
                )
            else:
                # Accept revised case
                self.validated_cases.append(revised_case)
                logger.info("Case %s accepted after revision", item.case_id)

        self.stats.total_revised = total_revised

        # Save revision results
        revision_output = self._paths["output_dir"] / "revision"
        if self.failed_cases:
            failed_path = revision_output / "failed_cases.json"
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(self.failed_cases, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d failed cases to %s", len(self.failed_cases), failed_path)

        logger.info(
            "Revision phase complete: %d revisions, %d accepted, %d failed",
            total_revised,
            len(self.validated_cases),
            len(self.failed_cases),
        )

        self._update_phase_status(PipelinePhase.REVISION, PhaseStatus.COMPLETED)

    def _apply_revision_fixes(self, item: RevisionQueueItem) -> dict[str, Any]:
        """
        Apply targeted fixes based on validation issues.

        Args:
            item: RevisionQueueItem containing case and issues

        Returns:
            Revised case dictionary
        """
        revised_case = copy.deepcopy(item.case_data)

        for issue in item.issues:
            if issue.rule.startswith("DAG"):
                # DAG-related fixes
                if "cycle" in issue.message.lower():
                    # Fix cyclic structure
                    structure = revised_case.get("annotations", {}).get(
                        "causal_structure", ""
                    )
                    # Simple fix: remove one edge
                    if "->" in structure:
                        parts = structure.split(",")
                        if len(parts) > 1:
                            revised_case["annotations"]["causal_structure"] = (
                                ", ".join(parts[:-1])
                            )

            elif issue.rule == "CONTENT":
                # Content-related fixes
                if "scenario" in issue.message.lower():
                    # Expand scenario
                    scenario = revised_case.get("scenario", "")
                    if len(scenario) < 100:
                        revised_case["scenario"] = (
                            f"{scenario} This scenario demonstrates a key "
                            f"principle in AI safety evaluation."
                        )

                if "reasoning" in issue.message.lower():
                    # Add reasoning steps
                    reasoning = revised_case.get("correct_reasoning", [])
                    if len(reasoning) < 3:
                        reasoning.append(
                            "Additional step: Consider edge cases and exceptions."
                        )
                        revised_case["correct_reasoning"] = reasoning

                if "refusal" in issue.message.lower():
                    # Expand wise refusal
                    refusal = revised_case.get("wise_refusal", "")
                    if len(refusal) < 100:
                        trap_type = revised_case.get("annotations", {}).get(
                            "trap_type", "causal"
                        )
                        revised_case["wise_refusal"] = (
                            f"{refusal} The key insight is recognizing the "
                            f"{trap_type} trap and avoiding common reasoning errors."
                        )

            elif issue.rule == "CROSS-DUP":
                # Duplicate - modify scenario to be unique
                scenario = revised_case.get("scenario", "")
                revised_case["scenario"] = f"[REVISED] {scenario}"
                # Regenerate case ID
                revised_case["case_id"] = f"8.{self._get_next_case_id_start() + 1}"

        return revised_case

    def finalize_dataset(self) -> None:
        """
        Merge validated cases with original 45 and generate final output.

        Steps:
        1. Deduplicate validated cases by case_id
        2. Collect all validated cases
        3. Add original 45 cases (marked is_original=true)
        4. Verify total = 450
        5. Save to output/final/GroupI1_dataset.json
        """
        logger.info("-" * 60)
        logger.info("PHASE 4: Finalization")
        logger.info("-" * 60)

        self._update_phase_status(PipelinePhase.FINALIZATION, PhaseStatus.IN_PROGRESS)

        # Deduplicate validated_cases by case_id before merge
        seen_ids: set[str] = set()
        unique_validated: list[dict[str, Any]] = []
        duplicate_count = 0
        for case in self.validated_cases:
            case_id = case.get("case_id")
            if case_id not in seen_ids:
                seen_ids.add(case_id)
                unique_validated.append(case)
            else:
                duplicate_count += 1
        if duplicate_count > 0:
            logger.info(
                "Removed %d duplicate case IDs during finalization",
                duplicate_count,
            )
        self.validated_cases = unique_validated

        # Validate ID uniqueness before finalizing
        if not self._validate_id_uniqueness():
            logger.error(
                "Cannot finalize dataset: duplicate case IDs detected. "
                "This indicates a bug in case ID generation."
            )
            raise RuntimeError("Duplicate case IDs detected - cannot finalize dataset")

        # Mark original cases
        for case in self.original_cases:
            case["is_original"] = True

        # Mark generated cases
        for case in self.validated_cases:
            case["is_original"] = False
            # Remove internal generator ID
            case.pop("_generator_id", None)

        # Combine all cases
        final_dataset = self.original_cases + self.validated_cases

        # Verify totals
        total_cases = len(final_dataset)
        original_count = sum(1 for c in final_dataset if c.get("is_original", False))
        new_count = total_cases - original_count

        logger.info(
            "Final dataset: %d total cases (%d original, %d new)",
            total_cases,
            original_count,
            new_count,
        )

        if total_cases < self.TARGET_TOTAL_CASES:
            logger.warning(
                "Target of %d cases not met. Got %d cases. "
                "Consider generating additional cases.",
                self.TARGET_TOTAL_CASES,
                total_cases,
            )

        # Sort by case_id
        final_dataset.sort(key=lambda x: float(x.get("case_id", "8.0").split(".")[1]))

        # Save final dataset
        final_output = self._paths["output_dir"] / "final"
        final_output.mkdir(parents=True, exist_ok=True)

        final_path = final_output / "GroupI1_dataset.json"
        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(final_dataset, f, indent=2, ensure_ascii=False)

        logger.info("Final dataset saved to %s", final_path)

        # Also save validated cases separately
        validated_path = self._paths["output_dir"] / "validated" / "validated_cases.json"
        with open(validated_path, "w", encoding="utf-8") as f:
            json.dump(self.validated_cases, f, indent=2, ensure_ascii=False)

        self._update_phase_status(PipelinePhase.FINALIZATION, PhaseStatus.COMPLETED)

    # =========================================================================
    # Progress Tracking
    # =========================================================================

    def _update_progress(self, phase: PipelinePhase, metrics: dict[str, Any]) -> None:
        """
        Update progress_tracker.json with current metrics.

        Args:
            phase: Current pipeline phase
            metrics: Dictionary of metrics to update
        """
        try:
            if self._progress_tracker_path.exists():
                with open(self._progress_tracker_path, encoding="utf-8") as f:
                    progress = json.load(f)
            else:
                progress = {}

            progress["status"] = phase.value
            progress["last_updated"] = datetime.now().isoformat()

            # Update case counts
            if "case_counts" not in progress:
                progress["case_counts"] = {}

            progress["case_counts"]["cases_generated"] = len(self.generated_cases)
            progress["case_counts"]["cases_validated"] = self.stats.total_validated
            progress["case_counts"]["cases_revised"] = self.stats.total_revised
            progress["case_counts"]["cases_final"] = (
                len(self.validated_cases) + len(self.original_cases)
            )

            # Update quality metrics
            if "quality_metrics" not in progress:
                progress["quality_metrics"] = {}

            progress["quality_metrics"]["average_crit_score"] = self.stats.avg_crit_score
            progress["quality_metrics"]["structure_pass_rate"] = self.stats.validation_pass_rate
            progress["quality_metrics"]["dag_validity_rate"] = self.stats.dag_validity_rate

            # Update revision stats
            progress["revision_stats"] = {
                "total_revisions": self.stats.total_revised,
                "by_cycle": self.stats.revision_cycles,
                "by_severity": self.stats.severity_counts,
            }

            # Add any additional metrics
            for key, value in metrics.items():
                progress[key] = value

            with open(self._progress_tracker_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2)

        except Exception as e:
            logger.warning("Failed to update progress tracker: %s", e)

    def _update_phase_status(
        self, phase: PipelinePhase, status: PhaseStatus
    ) -> None:
        """Update the status of a specific phase."""
        try:
            if self._progress_tracker_path.exists():
                with open(self._progress_tracker_path, encoding="utf-8") as f:
                    progress = json.load(f)
            else:
                progress = {"phases": {}}

            if "phases" not in progress:
                progress["phases"] = {}

            if phase.value not in progress["phases"]:
                progress["phases"][phase.value] = {}

            progress["phases"][phase.value]["status"] = status.value
            timestamp = datetime.now().isoformat()

            if status == PhaseStatus.IN_PROGRESS:
                progress["phases"][phase.value]["started"] = timestamp
            elif status in (PhaseStatus.COMPLETED, PhaseStatus.FAILED):
                progress["phases"][phase.value]["completed"] = timestamp

            with open(self._progress_tracker_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2)

        except Exception as e:
            logger.warning("Failed to update phase status: %s", e)

    def _update_generator_progress(
        self, generator_id: str, metrics: dict[str, Any]
    ) -> None:
        """Update progress for a specific generator."""
        try:
            if self._progress_tracker_path.exists():
                with open(self._progress_tracker_path, encoding="utf-8") as f:
                    progress = json.load(f)
            else:
                progress = {}

            if "generator_progress" not in progress:
                progress["generator_progress"] = {}

            if generator_id not in progress["generator_progress"]:
                progress["generator_progress"][generator_id] = {}

            progress["generator_progress"][generator_id].update(metrics)

            with open(self._progress_tracker_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2)

        except Exception as e:
            logger.warning(
                "Failed to update generator progress for %s: %s",
                generator_id,
                e,
            )

    def _get_current_state(self) -> dict[str, Any]:
        """
        Get current pipeline state for resumption.

        Returns:
            Dictionary containing current pipeline state
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats.to_dict(),
            "generated_count": len(self.generated_cases),
            "validated_count": len(self.validated_cases),
            "revision_queue_count": len(self.revision_queue),
            "failed_count": len(self.failed_cases),
            "original_count": len(self.original_cases),
        }

    def _save_checkpoint(self) -> None:
        """Save state for crash recovery."""
        checkpoint_path = self._paths["output_dir"] / "checkpoint.json"

        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "state": self._get_current_state(),
            "generated_case_ids": [c.get("case_id") for c in self.generated_cases],
            "validated_case_ids": [c.get("case_id") for c in self.validated_cases],
            "revision_queue_ids": [item.case_id for item in self.revision_queue],
            "failed_case_ids": [c.get("case_id") for c in self.failed_cases],
        }

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)

        logger.debug("Checkpoint saved to %s", checkpoint_path)

    # =========================================================================
    # Report Generation
    # =========================================================================

    def generate_report(self) -> Path:
        """
        Generate analysis_report.md with methodology and statistics.

        Returns:
            Path to the generated report file

        The report includes:
        - Executive summary
        - Methodology (Pearl's Ladder, SocraSynth/CRIT)
        - Coverage analysis (Pearl levels, trap types, subdomains)
        - Quality metrics (CRIT scores, validation rates)
        - Revision statistics
        - Original case mapping
        """
        report_lines = []

        # Header
        report_lines.extend([
            "# T3 Benchmark Generation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ])

        # Executive Summary
        total_cases = len(self.validated_cases) + len(self.original_cases)
        report_lines.extend([
            "## Executive Summary",
            "",
            f"- **Total Cases Generated:** {total_cases}",
            f"- **Original Cases:** {len(self.original_cases)}",
            f"- **New Cases:** {len(self.validated_cases)}",
            f"- **Failed Cases:** {len(self.failed_cases)}",
            f"- **Average CRIT Score:** {self.stats.avg_crit_score:.2f}/10",
            f"- **Validation Pass Rate:** {self.stats.validation_pass_rate:.1%}",
            f"- **DAG Validity Rate:** {self.stats.dag_validity_rate:.1%}",
            "",
        ])

        # Methodology
        report_lines.extend([
            "## Methodology",
            "",
            "### Pearl's Ladder of Causation",
            "",
            "This benchmark uses Pearl's three-level causal hierarchy:",
            "",
            "1. **L1 (Association):** Observational correlations (10-12% of cases)",
            "2. **L2 (Intervention):** Causal effects via do-calculus (66-70% of cases)",
            "3. **L3 (Counterfactual):** What-if reasoning with structural models (18-21% of cases)",
            "",
            "### CRIT Scoring Framework",
            "",
            "Cases are evaluated on five dimensions (1-10 scale):",
            "",
            "- **Scenario Clarity:** Publication-ready descriptions",
            "- **Variable Definition:** Precise formal notation",
            "- **Trap Mechanism:** Novel, deeply instructive traps",
            "- **Reasoning Chain:** Formally valid causal analysis",
            "- **Wise Refusal:** Deep understanding demonstrated",
            "",
            "Acceptance thresholds:",
            "- Mean CRIT score >= 7.0: PASS",
            "- Min CRIT score >= 5.0: Revise if below",
            "- Structure pass rate >= 95%",
            "",
        ])

        # Coverage Analysis
        report_lines.extend([
            "## Coverage Analysis",
            "",
            "### Pearl Level Distribution",
            "",
        ])

        # Count Pearl levels
        all_cases = self.original_cases + self.validated_cases
        pearl_counts = {"L1": 0, "L2": 0, "L3": 0}
        for case in all_cases:
            level = case.get("annotations", {}).get("pearl_level", "unknown")
            if level in pearl_counts:
                pearl_counts[level] += 1

        total = len(all_cases) if all_cases else 1
        report_lines.extend([
            "| Level | Count | Percentage | Target |",
            "|-------|-------|------------|--------|",
            f"| L1 | {pearl_counts['L1']} | {pearl_counts['L1']/total*100:.1f}% | 10-12% |",
            f"| L2 | {pearl_counts['L2']} | {pearl_counts['L2']/total*100:.1f}% | 66-70% |",
            f"| L3 | {pearl_counts['L3']} | {pearl_counts['L3']/total*100:.1f}% | 18-21% |",
            "",
        ])

        # Trap Type Distribution
        report_lines.extend([
            "### Trap Type Distribution",
            "",
        ])

        trap_counts: dict[str, int] = {}
        for case in all_cases:
            trap = case.get("annotations", {}).get("trap_type", "OTHER")
            trap_counts[trap] = trap_counts.get(trap, 0) + 1

        report_lines.append("| Trap Type | Count |")
        report_lines.append("|-----------|-------|")
        for trap, count in sorted(trap_counts.items(), key=lambda x: -x[1]):
            report_lines.append(f"| {trap} | {count} |")
        report_lines.append("")

        # Quality Metrics
        report_lines.extend([
            "## Quality Metrics",
            "",
            f"- **Average CRIT Score:** {self.stats.avg_crit_score:.2f}/10",
            f"- **Cases Above Threshold (7.0):** {sum(1 for s in self.stats.crit_scores if s >= 7.0)}",
            f"- **Cases Below Minimum (5.0):** {sum(1 for s in self.stats.crit_scores if s < 5.0)}",
            "",
        ])

        # Revision Statistics
        report_lines.extend([
            "## Revision Statistics",
            "",
            f"- **Total Revisions:** {self.stats.total_revised}",
            f"- **Cycle 1 Revisions:** {self.stats.revision_cycles.get('cycle_1', 0)}",
            f"- **Cycle 2 Revisions:** {self.stats.revision_cycles.get('cycle_2', 0)}",
            f"- **Cycle 3 Revisions:** {self.stats.revision_cycles.get('cycle_3', 0)}",
            "",
            "### Issues by Severity",
            "",
            f"- **Critical:** {self.stats.severity_counts.get('CRITICAL', 0)}",
            f"- **High:** {self.stats.severity_counts.get('HIGH', 0)}",
            f"- **Medium:** {self.stats.severity_counts.get('MEDIUM', 0)}",
            f"- **Low:** {self.stats.severity_counts.get('LOW', 0)}",
            "",
        ])

        # Original Case Mapping
        report_lines.extend([
            "## Original Cases",
            "",
            f"The benchmark includes {len(self.original_cases)} original cases "
            "marked with `is_original: true`.",
            "",
            "Original case IDs:",
            "",
        ])

        original_ids = [c.get("case_id", "unknown") for c in self.original_cases[:20]]
        report_lines.append(", ".join(original_ids))
        if len(self.original_cases) > 20:
            report_lines.append(f" ... and {len(self.original_cases) - 20} more")
        report_lines.append("")

        # Footer
        report_lines.extend([
            "---",
            "",
            "*Report generated by T3 Benchmark Orchestrator*",
            "",
        ])

        # Write report
        report_dir = self._paths.get("output_dir", self._base_path.parent / "output")
        report_path = report_dir / "analysis_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        logger.info("Report generated at %s", report_path)

        return report_path


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(
        description="T3 Benchmark Generation Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run full pipeline:
    python orchestrator.py --phase all

  Run generation only:
    python orchestrator.py --phase generate

  Run validation on existing generated cases:
    python orchestrator.py --phase validate

  Run revision phase:
    python orchestrator.py --phase revise

  Finalize and generate report:
    python orchestrator.py --phase finalize

  Use custom config:
    python orchestrator.py --config /path/to/config.json --phase all
        """,
    )

    parser.add_argument(
        "--phase",
        choices=["all", "generate", "validate", "revise", "finalize", "report"],
        default="all",
        help="Pipeline phase to execute (default: all)",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve config path
    config_path = Path(args.config)
    if not config_path.is_absolute():
        # Check if running from orchestrator directory
        if (Path.cwd() / "config.json").exists():
            config_path = Path.cwd() / args.config
        else:
            # Try relative to script location
            script_dir = Path(__file__).parent
            config_path = script_dir / args.config

    if args.dry_run:
        print(f"[DRY RUN] Would execute phase: {args.phase}")
        print(f"[DRY RUN] Config path: {config_path}")
        return

    try:
        orchestrator = Orchestrator(str(config_path))

        if args.phase == "all":
            result = orchestrator.run_full_pipeline()
            print(f"\nPipeline completed successfully!")
            print(f"Total cases: {result['total_cases']}")
            print(f"Report: {result['report_path']}")

        elif args.phase == "generate":
            orchestrator.run_generation_phase()
            print(f"\nGeneration phase completed.")
            print(f"Generated {len(orchestrator.generated_cases)} cases.")

        elif args.phase == "validate":
            # Load previously generated cases
            generated_dir = orchestrator._paths["output_dir"] / "generated"
            for batch_file in generated_dir.glob("batch_*.json"):
                with open(batch_file, encoding="utf-8") as f:
                    cases = json.load(f)
                    orchestrator.generated_cases.extend(cases)

            orchestrator.run_validation_phase()
            print(f"\nValidation phase completed.")
            print(f"Accepted: {len(orchestrator.validated_cases)}")
            print(f"Queued for revision: {len(orchestrator.revision_queue)}")

        elif args.phase == "revise":
            # Load revision queue from checkpoint if available
            checkpoint_path = orchestrator._paths["output_dir"] / "checkpoint.json"
            if checkpoint_path.exists():
                logger.info("Loading state from checkpoint")
            orchestrator.run_revision_phase()
            print(f"\nRevision phase completed.")
            print(f"Revised: {orchestrator.stats.total_revised}")

        elif args.phase == "finalize":
            # Load validated cases
            validated_path = (
                orchestrator._paths["output_dir"] / "validated" / "validated_cases.json"
            )
            if validated_path.exists():
                with open(validated_path, encoding="utf-8") as f:
                    orchestrator.validated_cases = json.load(f)

            orchestrator.finalize_dataset()
            print(f"\nFinalization completed.")

        elif args.phase == "report":
            report_path = orchestrator.generate_report()
            print(f"\nReport generated: {report_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "Make sure you are running from the orchestrator directory "
            "or provide the full path to config.json",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        logger.exception("Pipeline failed")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
