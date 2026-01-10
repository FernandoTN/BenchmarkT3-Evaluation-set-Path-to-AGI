#!/usr/bin/env python3
"""
DAG Validator - Causal Structure Validation System

Implements validation rules for causal DAG structures:
- DAG-01: Acyclicity Check (CRITICAL)
- DAG-02: Backdoor Criterion Validation (HIGH)
- DAG-03: Collider Conditioning Warning (HIGH)
- DAG-04: Variable Role Consistency (MEDIUM)
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(Enum):
    """Validation rule severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    rule: str  # DAG-01, DAG-02, etc.
    passed: bool
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    suggestion: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "rule": self.rule,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if self.details:
            result["details"] = self.details
        return result


class DirectedGraph:
    """
    Simple directed graph implementation for causal DAG validation.

    Supports basic graph operations without external dependencies.
    """

    def __init__(self) -> None:
        """Initialize an empty directed graph."""
        self._adj: dict[str, set[str]] = defaultdict(set)  # node -> set of successors
        self._pred: dict[str, set[str]] = defaultdict(set)  # node -> set of predecessors
        self._nodes: set[str] = set()

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self._nodes.add(node)

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target."""
        self._nodes.add(source)
        self._nodes.add(target)
        self._adj[source].add(target)
        self._pred[target].add(source)

    def remove_edge(self, source: str, target: str) -> None:
        """Remove edge from source to target if it exists."""
        self._adj[source].discard(target)
        self._pred[target].discard(source)

    @property
    def nodes(self) -> set[str]:
        """Return all nodes in the graph."""
        return self._nodes.copy()

    def successors(self, node: str) -> set[str]:
        """Return nodes that this node points to."""
        return self._adj[node].copy()

    def predecessors(self, node: str) -> set[str]:
        """Return nodes that point to this node."""
        return self._pred[node].copy()

    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists from source to target."""
        return target in self._adj[source]

    def in_degree(self, node: str) -> int:
        """Return number of incoming edges."""
        return len(self._pred[node])

    def out_degree(self, node: str) -> int:
        """Return number of outgoing edges."""
        return len(self._adj[node])

    def edges(self) -> list[tuple[str, str]]:
        """Return all edges as list of (source, target) tuples."""
        result = []
        for source, targets in self._adj.items():
            for target in targets:
                result.append((source, target))
        return result

    def copy(self) -> DirectedGraph:
        """Create a deep copy of the graph."""
        new_graph = DirectedGraph()
        new_graph._nodes = self._nodes.copy()
        for node, successors in self._adj.items():
            new_graph._adj[node] = successors.copy()
        for node, predecessors in self._pred.items():
            new_graph._pred[node] = predecessors.copy()
        return new_graph

    def to_undirected(self) -> UndirectedGraph:
        """Convert to undirected graph (for path finding)."""
        undirected = UndirectedGraph()
        for node in self._nodes:
            undirected.add_node(node)
        for source, targets in self._adj.items():
            for target in targets:
                undirected.add_edge(source, target)
        return undirected


class UndirectedGraph:
    """Undirected graph for path finding in DAG analysis."""

    def __init__(self) -> None:
        """Initialize an empty undirected graph."""
        self._adj: dict[str, set[str]] = defaultdict(set)
        self._nodes: set[str] = set()

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self._nodes.add(node)

    def add_edge(self, node1: str, node2: str) -> None:
        """Add an undirected edge between two nodes."""
        self._nodes.add(node1)
        self._nodes.add(node2)
        self._adj[node1].add(node2)
        self._adj[node2].add(node1)

    @property
    def nodes(self) -> set[str]:
        """Return all nodes."""
        return self._nodes.copy()

    def neighbors(self, node: str) -> set[str]:
        """Return neighbors of a node."""
        return self._adj[node].copy()


class DAGValidator:
    """
    Validates causal DAG structures according to defined rules.

    Implements four validation rules:
    - DAG-01: Acyclicity Check (CRITICAL)
    - DAG-02: Backdoor Criterion Validation (HIGH)
    - DAG-03: Collider Conditioning Warning (HIGH)
    - DAG-04: Variable Role Consistency (MEDIUM)
    """

    # Patterns for parsing causal structure notation
    ARROW_PATTERNS = {
        "directed": r"([A-Za-z0-9_]+)\s*(?:->|-->|->)\s*([A-Za-z0-9_]+)",
        "reverse": r"([A-Za-z0-9_]+)\s*(?:<-|<--|<-)\s*([A-Za-z0-9_]+)",
        "bidirectional": r"([A-Za-z0-9_]+)\s*(?:<->|<-->)\s*([A-Za-z0-9_]+)",
        "no_effect": r"([A-Za-z0-9_]+)\s*(?:-/->|-/-->)\s*([A-Za-z0-9_]+)",
        "unicode_right": r"([A-Za-z0-9_]+)\s*\u2192\s*([A-Za-z0-9_]+)",  # ->
        "unicode_left": r"([A-Za-z0-9_]+)\s*\u2190\s*([A-Za-z0-9_]+)",   # <-
        "unicode_bi": r"([A-Za-z0-9_]+)\s*\u2194\s*([A-Za-z0-9_]+)",     # <->
    }

    def __init__(self) -> None:
        """Initialize the DAG validator."""
        self._validation_rules = [
            ("DAG-01", Severity.CRITICAL, self.check_acyclicity),
            ("DAG-02", Severity.HIGH, self.check_backdoor_criterion),
            ("DAG-03", Severity.HIGH, self.check_collider_conditioning),
            ("DAG-04", Severity.MEDIUM, self.check_variable_roles),
        ]

    def parse_structure(self, structure: str) -> tuple[DirectedGraph, list[tuple[str, str]]]:
        """
        Parse causal structure notation into a directed graph.

        Args:
            structure: Causal structure string (e.g., "X -> Y, Z -> X, Z -> Y")

        Returns:
            Tuple of (DirectedGraph, list of no-effect pairs)

        Supports notations:
            - "X -> Y" or "X --> Y" or "X->" (directed edge)
            - "X <- Y" or "X <-- Y" (reverse directed edge)
            - "X <-> Y" (bidirectional, implies latent confounder)
            - "X -/-> Y" (explicitly no causal effect)
            - Unicode arrows: -> <- <->
        """
        graph = DirectedGraph()
        no_effect_pairs: list[tuple[str, str]] = []

        if not structure or structure.strip() == "":
            return graph, no_effect_pairs

        # Normalize unicode arrows to ASCII equivalents
        normalized = structure
        normalized = normalized.replace("\u2192", "->")  # ->
        normalized = normalized.replace("\u2190", "<-")  # <-
        normalized = normalized.replace("\u2194", "<->") # <->

        # Split by common delimiters
        segments = re.split(r"[,;]|\band\b", normalized, flags=re.IGNORECASE)

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            # Handle chained arrows like "X <- Z -> Y"
            parsed = self._parse_segment(segment)

            for edge_type, source, target in parsed:
                if edge_type == "directed":
                    graph.add_edge(source, target)
                elif edge_type == "bidirectional":
                    # Bidirectional implies latent confounder
                    # Add edges in both directions for simplicity
                    graph.add_edge(source, target)
                    graph.add_edge(target, source)
                elif edge_type == "no_effect":
                    no_effect_pairs.append((source, target))
                    # Still add nodes but no edge
                    graph.add_node(source)
                    graph.add_node(target)

        return graph, no_effect_pairs

    def _parse_segment(self, segment: str) -> list[tuple[str, str, str]]:
        """
        Parse a single segment which may contain chained arrows.

        Returns list of (edge_type, source, target) tuples.
        """
        results: list[tuple[str, str, str]] = []

        # Handle no-effect notation first
        no_effect_match = re.search(r"([A-Za-z0-9_]+)\s*-/->+\s*([A-Za-z0-9_]+)", segment)
        if no_effect_match:
            results.append(("no_effect", no_effect_match.group(1), no_effect_match.group(2)))
            return results

        # Handle chained arrows: "X <- Z -> Y" means Z->X and Z->Y
        # Split by variable names, preserving arrows
        tokens = re.split(r"(<->|<--|<-|-->|->)", segment)
        tokens = [t.strip() for t in tokens if t.strip()]

        if len(tokens) < 3:
            # Try simple patterns
            for pattern_name, pattern in [
                ("directed", r"([A-Za-z0-9_]+)\s*(?:-->?)\s*([A-Za-z0-9_]+)"),
                ("reverse", r"([A-Za-z0-9_]+)\s*(?:<--?)\s*([A-Za-z0-9_]+)"),
                ("bidirectional", r"([A-Za-z0-9_]+)\s*<->\s*([A-Za-z0-9_]+)"),
            ]:
                match = re.search(pattern, segment)
                if match:
                    source, target = match.group(1), match.group(2)
                    if pattern_name == "reverse":
                        results.append(("directed", target, source))
                    else:
                        results.append((pattern_name, source, target))
                    return results

            # Just variable names, add as nodes
            var_names = re.findall(r"[A-Za-z0-9_]+", segment)
            return results

        # Process chained tokens
        i = 0
        while i < len(tokens) - 2:
            left = tokens[i]
            arrow = tokens[i + 1]
            right = tokens[i + 2]

            # Skip if not valid variable names
            if not re.match(r"^[A-Za-z0-9_]+$", left) or not re.match(r"^[A-Za-z0-9_]+$", right):
                i += 1
                continue

            if arrow in ("->", "-->"):
                results.append(("directed", left, right))
            elif arrow in ("<-", "<--"):
                results.append(("directed", right, left))
            elif arrow == "<->":
                results.append(("bidirectional", left, right))

            i += 2

        return results

    def check_acyclicity(
        self,
        structure: str,
        variables: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """
        DAG-01: Check if the causal structure is acyclic.

        A valid DAG must not contain cycles. Cycles make causal inference
        impossible and indicate specification errors.

        Args:
            structure: Causal structure string
            variables: Optional variable definitions (unused for this check)

        Returns:
            ValidationResult with cycle information if found
        """
        graph, _ = self.parse_structure(structure)

        if not graph.nodes:
            return ValidationResult(
                rule="DAG-01",
                passed=True,
                severity=Severity.CRITICAL.value,
                message="Empty graph - no cycles possible",
                suggestion="Add causal relationships to the structure"
            )

        # Find cycles using DFS
        cycles = self._find_cycles(graph)

        if cycles:
            cycle_str = " -> ".join(cycles[0] + [cycles[0][0]])
            return ValidationResult(
                rule="DAG-01",
                passed=False,
                severity=Severity.CRITICAL.value,
                message=f"Cycle detected: {cycle_str}",
                suggestion="Remove one edge to break the cycle. Consider temporal ordering of variables.",
                details={"cycles": cycles, "nodes": list(graph.nodes)}
            )

        return ValidationResult(
            rule="DAG-01",
            passed=True,
            severity=Severity.CRITICAL.value,
            message="Graph is acyclic (valid DAG)",
            details={"nodes": list(graph.nodes), "edges": graph.edges()}
        )

    def _find_cycles(self, graph: DirectedGraph) -> list[list[str]]:
        """
        Find all cycles in the graph using DFS.

        Returns list of cycles, where each cycle is a list of nodes.
        """
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.successors(node):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:].copy())
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph.nodes:
            if node not in visited:
                dfs(node)

        return cycles

    def check_backdoor_criterion(
        self,
        structure: str,
        variables: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """
        DAG-02: Validate backdoor criterion for causal identification.

        For estimating causal effect X -> Y, we need to block all backdoor
        paths (paths from X to Y that start with an arrow into X).

        Args:
            structure: Causal structure string
            variables: Variable definitions with roles (treatment X, outcome Y, adjustment Z)

        Returns:
            ValidationResult with backdoor path analysis
        """
        graph, no_effect_pairs = self.parse_structure(structure)

        if not variables:
            return ValidationResult(
                rule="DAG-02",
                passed=True,
                severity=Severity.HIGH.value,
                message="No variables defined - skipping backdoor criterion check",
                suggestion="Define variables with roles (X=treatment, Y=outcome, Z=adjustment)"
            )

        # Identify treatment (X), outcome (Y), and adjustment set (Z)
        treatment = None
        outcome = None
        adjustment_set: set[str] = set()

        for var_name, var_info in variables.items():
            role = var_info.get("role", "").lower() if isinstance(var_info, dict) else ""

            if var_name == "X" or "treatment" in role or "action" in role or "intervention" in role:
                treatment = var_name
            elif var_name == "Y" or "outcome" in role or "reward" in role or "output" in role:
                outcome = var_name
            elif var_name == "Z" or "confounder" in role or "adjustment" in role:
                adjustment_set.add(var_name)

        if not treatment or not outcome:
            return ValidationResult(
                rule="DAG-02",
                passed=True,
                severity=Severity.HIGH.value,
                message="Cannot identify treatment/outcome variables",
                suggestion="Ensure X (treatment) and Y (outcome) are defined in variables"
            )

        # Find backdoor paths
        backdoor_paths = self.find_backdoor_paths(graph, treatment, outcome)

        if not backdoor_paths:
            return ValidationResult(
                rule="DAG-02",
                passed=True,
                severity=Severity.HIGH.value,
                message=f"No backdoor paths from {treatment} to {outcome}",
                details={"treatment": treatment, "outcome": outcome}
            )

        # Check if adjustment set blocks all backdoor paths
        unblocked_paths = []
        blocked_paths = []

        for path in backdoor_paths:
            if self.is_blocked_by(path, adjustment_set, graph):
                blocked_paths.append(path)
            else:
                unblocked_paths.append(path)

        if unblocked_paths:
            path_strs = [" <- ".join(p) for p in unblocked_paths[:3]]
            return ValidationResult(
                rule="DAG-02",
                passed=False,
                severity=Severity.HIGH.value,
                message=f"Unblocked backdoor path(s): {'; '.join(path_strs)}",
                suggestion=f"Add confounders to adjustment set or modify structure. "
                          f"Current adjustment: {adjustment_set or 'none'}",
                details={
                    "unblocked_paths": unblocked_paths,
                    "blocked_paths": blocked_paths,
                    "adjustment_set": list(adjustment_set)
                }
            )

        return ValidationResult(
            rule="DAG-02",
            passed=True,
            severity=Severity.HIGH.value,
            message=f"All backdoor paths blocked by adjustment set: {adjustment_set}",
            details={
                "backdoor_paths": backdoor_paths,
                "adjustment_set": list(adjustment_set)
            }
        )

    def find_backdoor_paths(
        self,
        graph: DirectedGraph,
        source: str,
        target: str
    ) -> list[list[str]]:
        """
        Find all backdoor paths from source to target.

        A backdoor path starts with an arrow INTO the source node
        (i.e., source <- ... -> target).

        Args:
            graph: Directed graph
            source: Treatment variable
            target: Outcome variable

        Returns:
            List of backdoor paths (each path is list of nodes)
        """
        backdoor_paths: list[list[str]] = []

        # Get parents of source (nodes that point to source)
        source_parents = graph.predecessors(source)

        if not source_parents:
            return backdoor_paths

        # For each parent, find paths to target that don't go through source directly
        for parent in source_parents:
            paths = self._find_all_paths_undirected(graph, parent, target, exclude={source})
            for path in paths:
                backdoor_paths.append([source] + path)

        return backdoor_paths

    def _find_all_paths_undirected(
        self,
        graph: DirectedGraph,
        start: str,
        end: str,
        exclude: Optional[set[str]] = None
    ) -> list[list[str]]:
        """
        Find all undirected paths between start and end.

        Used for backdoor path finding where direction doesn't matter
        for path existence (though it matters for blocking).
        """
        if exclude is None:
            exclude = set()

        paths: list[list[str]] = []

        def dfs(current: str, target: str, visited: set[str], path: list[str]) -> None:
            if current == target:
                paths.append(path.copy())
                return

            visited.add(current)

            # Check both successors and predecessors (undirected traversal)
            neighbors = graph.successors(current) | graph.predecessors(current)

            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in exclude:
                    path.append(neighbor)
                    dfs(neighbor, target, visited, path)
                    path.pop()

            visited.remove(current)

        dfs(start, end, set(), [start])
        return paths

    def is_blocked_by(
        self,
        path: list[str],
        adjustment_set: set[str],
        graph: DirectedGraph
    ) -> bool:
        """
        Check if a path is blocked by the adjustment set.

        A path is blocked if:
        1. It contains a non-collider that is in the adjustment set, OR
        2. It contains a collider that is NOT in the adjustment set
           (and neither are its descendants)

        Args:
            path: List of nodes forming the path
            adjustment_set: Set of nodes being conditioned on
            graph: The directed graph

        Returns:
            True if path is blocked, False otherwise
        """
        if len(path) < 3:
            # Path too short to have intermediate nodes
            return bool(adjustment_set & set(path[1:-1])) if len(path) > 1 else False

        # Check each triple in the path
        for i in range(len(path) - 2):
            node_a = path[i]
            node_b = path[i + 1]  # Middle node
            node_c = path[i + 2]

            is_collider = self._is_collider(graph, node_a, node_b, node_c)

            if is_collider:
                # Collider: path is blocked UNLESS we condition on collider or descendant
                descendants = self._get_descendants(graph, node_b)
                if node_b not in adjustment_set and not (adjustment_set & descendants):
                    return True  # Blocked at this collider
            else:
                # Non-collider (chain or fork): path is blocked IF we condition on it
                if node_b in adjustment_set:
                    return True  # Blocked at this non-collider

        return False

    def _is_collider(
        self,
        graph: DirectedGraph,
        node_a: str,
        node_b: str,
        node_c: str
    ) -> bool:
        """
        Check if node_b is a collider on the path A - B - C.

        A collider has arrows pointing INTO it from both neighbors:
        A -> B <- C
        """
        # Check if both A and C point to B
        a_to_b = graph.has_edge(node_a, node_b)
        c_to_b = graph.has_edge(node_c, node_b)

        return a_to_b and c_to_b

    def _get_descendants(self, graph: DirectedGraph, node: str) -> set[str]:
        """Get all descendants of a node (nodes reachable via directed paths)."""
        descendants: set[str] = set()
        queue = list(graph.successors(node))

        while queue:
            current = queue.pop(0)
            if current not in descendants:
                descendants.add(current)
                queue.extend(graph.successors(current))

        return descendants

    def check_collider_conditioning(
        self,
        structure: str,
        variables: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """
        DAG-03: Warn about conditioning on colliders.

        Conditioning on a collider (node with multiple incoming edges)
        opens spurious paths and can introduce bias.

        Args:
            structure: Causal structure string
            variables: Variable definitions (to check if any are colliders)

        Returns:
            ValidationResult with collider warnings
        """
        graph, _ = self.parse_structure(structure)

        # Find all colliders in the graph
        colliders = self.find_colliders(graph)

        if not colliders:
            return ValidationResult(
                rule="DAG-03",
                passed=True,
                severity=Severity.HIGH.value,
                message="No colliders detected in the structure",
                details={"nodes": list(graph.nodes)}
            )

        # Check if any variable in the case is a collider being conditioned on
        conditioned_colliders: list[str] = []
        warnings: list[str] = []

        if variables:
            for var_name, var_info in variables.items():
                role = var_info.get("role", "").lower() if isinstance(var_info, dict) else ""

                # Check if this variable is a collider
                if var_name in colliders:
                    # Check if it's being used as an adjustment/conditioning variable
                    if var_name == "Z" or "adjustment" in role or "confounder" in role:
                        conditioned_colliders.append(var_name)
                        warnings.append(
                            f"{var_name} is a collider (has {colliders[var_name]} parents) "
                            f"and may open spurious paths if conditioned on"
                        )

        if conditioned_colliders:
            return ValidationResult(
                rule="DAG-03",
                passed=False,
                severity=Severity.HIGH.value,
                message=f"Potential collider bias: {', '.join(warnings)}",
                suggestion="Avoid conditioning on colliders unless necessary. "
                          "Consider the common pattern: X -> C <- Y (where conditioning on C induces X-Y correlation)",
                details={
                    "colliders": colliders,
                    "conditioned_colliders": conditioned_colliders
                }
            )

        # Just informational - colliders exist but may not be problematic
        collider_info = [f"{node} (parents: {count})" for node, count in colliders.items()]
        return ValidationResult(
            rule="DAG-03",
            passed=True,
            severity=Severity.HIGH.value,
            message=f"Colliders found but not problematically conditioned: {', '.join(collider_info)}",
            suggestion="Be cautious if you decide to condition on these variables",
            details={"colliders": colliders}
        )

    def find_colliders(self, graph: DirectedGraph) -> dict[str, int]:
        """
        Find all collider nodes in the graph.

        A collider is a node with 2 or more incoming edges.

        Args:
            graph: Directed graph

        Returns:
            Dictionary mapping collider nodes to their in-degree
        """
        colliders: dict[str, int] = {}

        for node in graph.nodes:
            in_deg = graph.in_degree(node)
            if in_deg >= 2:
                colliders[node] = in_deg

        return colliders

    def check_variable_roles(
        self,
        structure: str,
        variables: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """
        DAG-04: Verify variable roles are consistent with structure.

        Checks:
        - X (treatment) should have outgoing edges
        - Y (outcome) should have incoming edges
        - Z role should match its structural position (confounder/mediator/collider)

        Args:
            structure: Causal structure string
            variables: Variable definitions with roles

        Returns:
            ValidationResult with role consistency analysis
        """
        graph, no_effect_pairs = self.parse_structure(structure)

        if not variables:
            return ValidationResult(
                rule="DAG-04",
                passed=True,
                severity=Severity.MEDIUM.value,
                message="No variables defined - skipping role consistency check",
                suggestion="Define variables with roles for validation"
            )

        issues: list[str] = []
        warnings: list[str] = []

        for var_name, var_info in variables.items():
            role = var_info.get("role", "") if isinstance(var_info, dict) else ""
            role_lower = role.lower()

            # Skip if variable not in graph
            if var_name not in graph.nodes:
                warnings.append(f"{var_name} defined but not found in causal structure")
                continue

            out_deg = graph.out_degree(var_name)
            in_deg = graph.in_degree(var_name)

            # Check treatment (X) - should have outgoing edges
            if var_name == "X" or "treatment" in role_lower or "action" in role_lower:
                if out_deg == 0 and not any(var_name == pair[0] for pair in no_effect_pairs):
                    issues.append(
                        f"{var_name} is treatment but has no outgoing edges "
                        f"(in-degree: {in_deg}, out-degree: {out_deg})"
                    )

            # Check outcome (Y) - should have incoming edges
            if var_name == "Y" or "outcome" in role_lower or "reward" in role_lower:
                if in_deg == 0:
                    issues.append(
                        f"{var_name} is outcome but has no incoming edges "
                        f"(in-degree: {in_deg}, out-degree: {out_deg})"
                    )

            # Check Z role consistency
            if var_name == "Z" or "confounder" in role_lower or "mediator" in role_lower:
                if "confounder" in role_lower:
                    # Confounder should have edges to both X and Y
                    has_path_to_x = var_name in graph.predecessors("X") if "X" in graph.nodes else False
                    has_path_to_y = var_name in graph.predecessors("Y") if "Y" in graph.nodes else False

                    if not (has_path_to_x or has_path_to_y):
                        warnings.append(
                            f"{var_name} is labeled as confounder but doesn't directly "
                            f"connect to both X and Y"
                        )

                elif "mediator" in role_lower:
                    # Mediator should be on path from X to Y
                    x_to_var = "X" in graph.predecessors(var_name) if "X" in graph.nodes else False
                    var_to_y = "Y" in graph.successors(var_name) if "Y" in graph.nodes else False

                    if not (x_to_var and var_to_y):
                        warnings.append(
                            f"{var_name} is labeled as mediator but doesn't form "
                            f"X -> {var_name} -> Y path"
                        )

        if issues:
            return ValidationResult(
                rule="DAG-04",
                passed=False,
                severity=Severity.MEDIUM.value,
                message=f"Role inconsistencies: {'; '.join(issues)}",
                suggestion="Verify variable roles match their position in the causal graph",
                details={"issues": issues, "warnings": warnings}
            )

        if warnings:
            return ValidationResult(
                rule="DAG-04",
                passed=True,
                severity=Severity.MEDIUM.value,
                message=f"Minor role warnings: {'; '.join(warnings)}",
                suggestion="Review variable roles for accuracy",
                details={"warnings": warnings}
            )

        return ValidationResult(
            rule="DAG-04",
            passed=True,
            severity=Severity.MEDIUM.value,
            message="Variable roles consistent with causal structure",
            details={"variables": list(variables.keys())}
        )

    def validate(self, case: dict[str, Any]) -> list[ValidationResult]:
        """
        Run all validation checks on a case.

        Args:
            case: Case dictionary with at least:
                - annotations.causal_structure (or hidden_structure for L2)
                - variables (optional)

        Returns:
            List of ValidationResult objects
        """
        results: list[ValidationResult] = []

        # Extract structure from case
        annotations = case.get("annotations", {})
        structure = annotations.get("causal_structure", "")

        # For L2 cases, also check hidden_structure
        hidden_structure = case.get("hidden_structure", "")
        if hidden_structure and not structure:
            structure = hidden_structure

        # Extract variables
        variables = case.get("variables", {})

        # Run all validation rules
        for rule_id, severity, check_func in self._validation_rules:
            try:
                result = check_func(structure, variables)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    rule=rule_id,
                    passed=False,
                    severity=severity.value,
                    message=f"Validation error: {str(e)}",
                    suggestion="Check structure syntax and variable definitions"
                ))

        return results

    def validate_batch(
        self,
        cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Validate multiple cases and compute statistics.

        Args:
            cases: List of case dictionaries

        Returns:
            Dictionary with:
                - results: List of (case_id, ValidationResult list) tuples
                - statistics: Aggregated statistics
                - summary: Human-readable summary
        """
        all_results: list[tuple[str, list[ValidationResult]]] = []

        # Per-rule statistics
        rule_stats: dict[str, dict[str, int]] = {
            "DAG-01": {"passed": 0, "failed": 0, "total": 0},
            "DAG-02": {"passed": 0, "failed": 0, "total": 0},
            "DAG-03": {"passed": 0, "failed": 0, "total": 0},
            "DAG-04": {"passed": 0, "failed": 0, "total": 0},
        }

        # Severity statistics
        severity_stats: dict[str, int] = {
            "CRITICAL_failures": 0,
            "HIGH_failures": 0,
            "MEDIUM_failures": 0,
            "LOW_failures": 0,
        }

        for case in cases:
            case_id = case.get("case_id", "unknown")
            results = self.validate(case)
            all_results.append((case_id, results))

            for result in results:
                rule_stats[result.rule]["total"] += 1
                if result.passed:
                    rule_stats[result.rule]["passed"] += 1
                else:
                    rule_stats[result.rule]["failed"] += 1
                    severity_stats[f"{result.severity}_failures"] += 1

        # Compute pass rates
        for rule in rule_stats:
            total = rule_stats[rule]["total"]
            if total > 0:
                rule_stats[rule]["pass_rate"] = rule_stats[rule]["passed"] / total
            else:
                rule_stats[rule]["pass_rate"] = 1.0

        # Generate summary
        total_cases = len(cases)
        critical_failures = severity_stats["CRITICAL_failures"]
        high_failures = severity_stats["HIGH_failures"]

        summary_lines = [
            f"Validated {total_cases} cases",
            f"Critical failures (cycles): {critical_failures}",
            f"High severity failures: {high_failures}",
        ]

        for rule, stats in rule_stats.items():
            pass_rate = stats.get("pass_rate", 1.0) * 100
            summary_lines.append(f"  {rule}: {pass_rate:.1f}% pass rate")

        return {
            "results": all_results,
            "statistics": {
                "rule_stats": rule_stats,
                "severity_stats": severity_stats,
                "total_cases": total_cases,
            },
            "summary": "\n".join(summary_lines)
        }


def main() -> None:
    """Test the DAG validator with example cases."""
    validator = DAGValidator()

    # Test case 1: Simple confounding
    test_case_1 = {
        "case_id": "test_1",
        "annotations": {
            "causal_structure": "Z -> X, Z -> Y, X -> Y"
        },
        "variables": {
            "X": {"name": "Treatment", "role": "Treatment"},
            "Y": {"name": "Outcome", "role": "Outcome"},
            "Z": {"name": "Confounder", "role": "Confounder"}
        }
    }

    # Test case 2: Cycle detection
    test_case_2 = {
        "case_id": "test_2",
        "annotations": {
            "causal_structure": "X -> Y, Y -> Z, Z -> X"
        },
        "variables": {
            "X": {"name": "Var1", "role": "Treatment"},
            "Y": {"name": "Var2", "role": "Outcome"},
            "Z": {"name": "Var3", "role": "Mediator"}
        }
    }

    # Test case 3: Collider
    test_case_3 = {
        "case_id": "test_3",
        "annotations": {
            "causal_structure": "X -> C, Y -> C"
        },
        "variables": {
            "X": {"name": "Cause1", "role": "Treatment"},
            "Y": {"name": "Cause2", "role": "Outcome"},
            "C": {"name": "Collider", "role": "Adjustment"}
        }
    }

    print("=" * 60)
    print("DAG Validator Test Results")
    print("=" * 60)

    for test_case in [test_case_1, test_case_2, test_case_3]:
        print(f"\nCase: {test_case['case_id']}")
        print(f"Structure: {test_case['annotations']['causal_structure']}")
        print("-" * 40)

        results = validator.validate(test_case)
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"  [{status}] {result.rule} ({result.severity}): {result.message}")
            if result.suggestion:
                print(f"         Suggestion: {result.suggestion}")

    # Batch validation test
    print("\n" + "=" * 60)
    print("Batch Validation Summary")
    print("=" * 60)

    batch_result = validator.validate_batch([test_case_1, test_case_2, test_case_3])
    print(batch_result["summary"])


if __name__ == "__main__":
    main()
