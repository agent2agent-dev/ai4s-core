"""
Workflow validation engine: domain-specific rule checking for LLM-generated plans.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .orchestrator import WorkflowPlan, WorkflowStep
from .domain import DomainSpec


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    severity: Severity
    step_index: Optional[int]
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.passed = False

    def merge(self, other: "ValidationReport") -> None:
        self.issues.extend(other.issues)
        if not other.passed:
            self.passed = False

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]


class Rule:
    """A single validation rule."""

    def __init__(
        self,
        name: str,
        check: Callable[[WorkflowPlan, Optional[DomainSpec]], List[ValidationIssue]],
        description: str = "",
    ):
        self.name = name
        self.check = check
        self.description = description


class RuleRegistry:
    """Registry of validation rules per domain."""

    def __init__(self):
        self._global_rules: List[Rule] = []
        self._domain_rules: Dict[str, List[Rule]] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in validation rules."""
        # Global rules
        self._global_rules.append(
            Rule(
                "non_empty_steps",
                self._check_non_empty_steps,
                "Workflow must have at least one step",
            )
        )
        self._global_rules.append(
            Rule(
                "valid_dependencies",
                self._check_valid_dependencies,
                "All step dependencies must reference valid step indices",
            )
        )
        self._global_rules.append(
            Rule(
                "no_circular_deps",
                self._check_no_circular_deps,
                "Workflow must not contain circular dependencies",
            )
        )

        # Molecular dynamics rules
        self._domain_rules["molecular_dynamics"] = [
            Rule(
                "md_has_minimization",
                self._check_md_minimization,
                "MD workflow should include energy minimization",
            ),
            Rule(
                "md_has_equilibration",
                self._check_md_equilibration,
                "MD workflow should include equilibration before production",
            ),
            Rule(
                "md_temperature_reasonable",
                self._check_md_temperature,
                "MD temperature should be in physically reasonable range",
            ),
            Rule(
                "md_timestep_reasonable",
                self._check_md_timestep,
                "MD timestep should be appropriate for the force field",
            ),
        ]

        # DFT rules
        self._domain_rules["density_functional_theory"] = [
            Rule(
                "dft_has_scf",
                self._check_dft_scf,
                "DFT workflow should include SCF calculation",
            ),
            Rule(
                "dft_ecutwfc_positive",
                self._check_dft_ecutwfc,
                "Plane-wave cutoff must be positive and reasonable",
            ),
            Rule(
                "dft_kpoint_density",
                self._check_dft_kpoints,
                "K-point sampling should be sufficient for the system size",
            ),
            Rule(
                "dft_smearing_metal",
                self._check_dft_smearing,
                "Metallic systems need smearing for SCF convergence",
            ),
        ]

        # Quantum chemistry rules
        self._domain_rules["quantum_chemistry"] = [
            Rule(
                "qc_has_optimization",
                self._check_qc_optimization,
                "QC workflow should include geometry optimization",
            ),
            Rule(
                "qc_basis_set_reasonable",
                self._check_qc_basis_set,
                "Basis set should be appropriate for the system",
            ),
            Rule(
                "qc_charge_multiplicity",
                self._check_qc_charge_multiplicity,
                "Charge and multiplicity should be consistent",
            ),
        ]

        # Bioinformatics rules
        self._domain_rules["bioinformatics"] = [
            Rule(
                "bio_has_quality_control",
                self._check_bio_quality_control,
                "Bioinformatics workflow should include QC step",
            ),
            Rule(
                "bio_has_alignment",
                self._check_bio_alignment,
                "Sequence workflow should include alignment step",
            ),
            Rule(
                "bio_replicates_sufficient",
                self._check_bio_replicates,
                "Differential expression needs biological replicates",
            ),
        ]

    def _check_non_empty_steps(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        if not plan.steps:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    step_index=None,
                    field="steps",
                    message="Workflow has no steps",
                    suggestion="Add at least one computational step",
                )
            )
        return issues

    def _check_valid_dependencies(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        n = len(plan.steps)
        for i, step in enumerate(plan.steps):
            for dep in step.dependencies:
                try:
                    dep_idx = int(dep)
                    if dep_idx < 0 or dep_idx >= n:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                step_index=i,
                                field="dependencies",
                                message=f"Step {i} references invalid dependency: {dep}",
                                suggestion=f"Dependency must be between 0 and {n - 1}",
                            )
                        )
                except ValueError:
                    pass  # Named dependencies
        return issues

    def _check_no_circular_deps(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        dep_graph = {i: set() for i in range(len(plan.steps))}
        for i, step in enumerate(plan.steps):
            for dep in step.dependencies:
                try:
                    dep_graph[i].add(int(dep))
                except ValueError:
                    pass

        visited = set()
        rec_stack = set()

        def has_cycle(node: int) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for dep in dep_graph.get(node, set()):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for i in range(len(plan.steps)):
            if i not in visited:
                if has_cycle(i):
                    issues.append(
                        ValidationIssue(
                            severity=Severity.ERROR,
                            step_index=None,
                            field="dependencies",
                            message="Workflow contains circular dependencies",
                            suggestion="Review step dependencies to remove cycles",
                        )
                    )
                    break
        return issues

    def _check_md_minimization(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_min = any(
            "minim" in step.description.lower()
            or "em" in step.tool.lower()
            or "minim" in step.command.lower()
            for step in plan.steps
        )
        if not has_min and len(plan.steps) > 2:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="MD workflow may be missing energy minimization",
                    suggestion="Add an energy minimization step before equilibration",
                )
            )
        return issues

    def _check_md_equilibration(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_equi = any(
            "equilibrat" in step.description.lower()
            or "nvt" in step.command.lower()
            or "npt" in step.command.lower()
            for step in plan.steps
        )
        if not has_equi and len(plan.steps) > 3:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="MD workflow may be missing equilibration phase",
                    suggestion="Add NVT and/or NPT equilibration before production run",
                )
            )
        return issues

    def _check_md_temperature(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            # Look for temperature references in command
            if "ref_t" in cmd or "gen_temp" in cmd:
                # Extract temperature value (simplified)
                import re
                temps = re.findall(r"ref_t\s*=\s*(\d+)", cmd)
                temps += re.findall(r"gen_temp\s*=\s*(\d+)", cmd)
                for t in temps:
                    temp = int(t)
                    if temp < 10 or temp > 1000:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"Temperature {temp} K seems unusual",
                                suggestion="Typical MD temperatures are 100-500 K",
                            )
                        )
        return issues

    def _check_md_timestep(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if "dt" in cmd:
                import re
                dts = re.findall(r"dt\s*=\s*(\d+\.?\d*)", cmd)
                for dt_str in dts:
                    dt = float(dt_str)
                    if dt > 0.005:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                step_index=i,
                                field="command",
                                message=f"Timestep {dt} ps is too large for all-atom MD",
                                suggestion="Use dt <= 0.002 ps (2 fs) for all-atom simulations",
                            )
                        )
        return issues

    def _check_dft_scf(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_scf = any(
            "scf" in step.description.lower()
            or "pw.x" in step.tool.lower()
            for step in plan.steps
        )
        if not has_scf and len(plan.steps) > 1:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="DFT workflow may be missing SCF calculation",
                    suggestion="Add a self-consistent field calculation step",
                )
            )
        return issues

    def _check_dft_ecutwfc(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if "ecutwfc" in cmd:
                import re
                cuts = re.findall(r"ecutwfc\s*=\s*(\d+\.?\d*)", cmd)
                for cut_str in cuts:
                    cut = float(cut_str)
                    if cut < 10:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                step_index=i,
                                field="command",
                                message=f"ecutwfc = {cut} Ry is too low",
                                suggestion="Minimum recommended ecutwfc is 20-30 Ry",
                            )
                        )
                    elif cut > 200:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"ecutwfc = {cut} Ry is very high",
                                suggestion="Verify this cutoff is necessary for your pseudopotential",
                            )
                        )
        return issues

    def _check_dft_kpoints(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if "kpoints" in cmd or "k_points" in cmd:
                import re
                meshes = re.findall(r"(\d+)\s+(\d+)\s+(\d+)", cmd)
                for mesh in meshes:
                    kx, ky, kz = int(mesh[0]), int(mesh[1]), int(mesh[2])
                    total = kx * ky * kz
                    if total < 1:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                step_index=i,
                                field="command",
                                message=f"K-point mesh {kx}x{ky}x{kz} is invalid",
                                suggestion="Use at least 1x1x1 k-point mesh",
                            )
                        )
                    elif total < 8:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"K-point mesh {kx}x{ky}x{kz} may be too coarse",
                                suggestion="For accurate results, use at least 4x4x4 or Monkhorst-Pack sampling",
                            )
                        )
        return issues

    def _check_dft_smearing(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_smearing = False
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if any(x in cmd for x in ["smearing", "degauss", "occupations", "metal"]):
                has_smearing = True
            if "occupations='smearing'" in cmd or "degauss" in cmd:
                import re
                degs = re.findall(r"degauss\s*=\s*(\d+\.?\d*)", cmd)
                for d in degs:
                    deg = float(d)
                    if deg > 0.05:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"Smearing width {deg} Ry is large",
                                suggestion="Typical degauss is 0.01-0.02 Ry for metals",
                            )
                        )
        if not has_smearing and len(plan.steps) > 2:
            issues.append(
                ValidationIssue(
                    severity=Severity.INFO,
                    step_index=None,
                    field="steps",
                    message="No smearing detected. If system is metallic, add smearing for SCF convergence",
                    suggestion="Add occupations='smearing' and degauss for metallic systems",
                )
            )
        return issues

    def _check_qc_optimization(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_opt = any(
            "opt" in step.command.lower() or "optimize" in step.description.lower()
            for step in plan.steps
        )
        if not has_opt and len(plan.steps) > 1:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="QC workflow may be missing geometry optimization",
                    suggestion="Add geometry optimization before frequency or property calculations",
                )
            )
        return issues

    def _check_qc_basis_set(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if "basis" in cmd:
                import re
                basis_match = re.search(r"basis\s*[=\s]+\s*['\"]([^'\"]+)['\"]", cmd)
                if basis_match:
                    basis = basis_match.group(1).lower()
                    minimal_sets = ["sto-3g", "3-21g", "6-31g"]
                    if any(b in basis for b in minimal_sets):
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"Basis set '{basis}' is minimal",
                                suggestion="Consider def2-TZVP or 6-311++G(d,p) for publication-quality results",
                            )
                        )
        return issues

    def _check_qc_charge_multiplicity(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        for i, step in enumerate(plan.steps):
            cmd = step.command.lower()
            if "charge" in cmd or "mult" in cmd:
                import re
                charges = re.findall(r"charge\s*[=\s]+\s*(-?\d+)", cmd)
                mults = re.findall(r"mult\s*[=\s]+\s*(\d+)", cmd)
                for charge in charges:
                    ch = int(charge)
                    if abs(ch) > 5:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.WARNING,
                                step_index=i,
                                field="command",
                                message=f"Charge = {ch} is unusual",
                                suggestion="Verify this charge is correct for your molecule",
                            )
                        )
                for mult in mults:
                    m = int(mult)
                    if m < 1:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                step_index=i,
                                field="command",
                                message=f"Multiplicity = {m} is invalid (must be >= 1)",
                                suggestion="Multiplicity = 2S+1 where S is total spin",
                            )
                        )
        return issues

    def _check_bio_quality_control(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_qc = any(
            "fastqc" in step.tool.lower() or "qc" in step.description.lower()
            or "quality" in step.description.lower() or "trim" in step.tool.lower()
            for step in plan.steps
        )
        if not has_qc and len(plan.steps) > 1:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="Bioinformatics workflow may be missing quality control",
                    suggestion="Add FastQC and/or trimming step before alignment",
                )
            )
        return issues

    def _check_bio_alignment(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_align = any(
            "align" in step.description.lower() or "bwa" in step.tool.lower()
            or "hisat" in step.tool.lower() or "bowtie" in step.tool.lower()
            or "star" in step.tool.lower() or "minimap" in step.tool.lower()
            for step in plan.steps
        )
        if not has_align and len(plan.steps) > 2:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    step_index=None,
                    field="steps",
                    message="Sequence workflow may be missing alignment step",
                    suggestion="Add alignment step (BWA, HISAT2, STAR, etc.)",
                )
            )
        return issues

    def _check_bio_replicates(
        self, plan: WorkflowPlan, spec: Optional[DomainSpec]
    ) -> List[ValidationIssue]:
        issues = []
        has_de = any(
            "deseq" in step.tool.lower() or "edge" in step.tool.lower()
            or "diff" in step.description.lower() or "expression" in step.description.lower()
            for step in plan.steps
        )
        if has_de:
            replicate_count = 0
            for step in plan.steps:
                if "sample" in step.description.lower() or "replicate" in step.description.lower():
                    import re
                    reps = re.findall(r"(\d+)\s*replicate", step.description.lower())
                    replicate_count = max(replicate_count, max((int(r) for r in reps), default=0))
            if replicate_count < 3:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        step_index=None,
                        field="steps",
                        message="Differential expression with < 3 replicates per condition",
                        suggestion="Use at least 3 biological replicates for reliable DE analysis",
                    )
                )
        return issues

    def get_rules(self, domain: str) -> List[Rule]:
        """Get all applicable rules for a domain."""
        rules = list(self._global_rules)
        rules.extend(self._domain_rules.get(domain, []))
        return rules

    def validate(self, plan: WorkflowPlan, spec: Optional[DomainSpec] = None) -> ValidationReport:
        """Run all applicable rules against a workflow plan."""
        report = ValidationReport()
        rules = self.get_rules(plan.domain)
        for rule in rules:
            issues = rule.check(plan, spec)
            for issue in issues:
                report.add(issue)
        return report

    def validate_batch(self, plans: List[WorkflowPlan]) -> Dict[str, ValidationReport]:
        """Validate multiple workflow plans and return reports keyed by plan query."""
        reports = {}
        for plan in plans:
            reports[plan.query] = self.validate(plan)
        return reports
