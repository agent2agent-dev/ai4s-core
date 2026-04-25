"""
Core orchestrator: translates natural language to scientific workflows.
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from .llm_interface import LLMInterface
from .domain import DomainRegistry


@dataclass
class WorkflowStep:
    """A single step in a scientific workflow."""
    tool: str
    command: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class WorkflowPlan:
    """A complete workflow plan generated from a research query."""
    query: str
    domain: str
    steps: List[WorkflowStep] = field(default_factory=list)
    estimated_compute: Optional[str] = None
    required_software: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)


class WorkflowOrchestrator:
    """
    Main orchestrator that converts natural language scientific queries
    into structured, executable workflow plans.
    """

    def __init__(
        self,
        llm: Optional[LLMInterface] = None,
        domain_registry: Optional[DomainRegistry] = None,
    ):
        self.llm = llm or LLMInterface()
        self.domains = domain_registry or DomainRegistry()

    def plan(self, query: str, domain_hint: Optional[str] = None, use_mock: bool = False) -> WorkflowPlan:
        """
        Generate a workflow plan from a natural language query.

        Args:
            query: Natural language description of the scientific problem.
            domain_hint: Optional domain override (e.g., 'molecular_dynamics').
            use_mock: If True, use a mock LLM for testing/demo without API keys.

        Returns:
            WorkflowPlan with steps, dependencies, and resource estimates.
        """
        # Step 1: Classify domain if not provided
        if use_mock:
            domain = domain_hint or "molecular_dynamics"
            plan_raw = self._mock_plan(query, domain)
        else:
            domain = domain_hint or self._classify_domain(query)
            domain_context = self.domains.get_context(domain)
            plan_raw = self.llm.generate_plan(query, domain_context)

        # Step 2: Parse and validate
        plan = self._parse_plan(query, domain, plan_raw)
        plan = self._validate_plan(plan)

        return plan

    def _mock_plan(self, query: str, domain: str) -> Dict[str, Any]:
        """Generate a realistic mock plan for demo purposes."""
        if domain == "molecular_dynamics":
            return {
                "steps": [
                    {
                        "tool": "wget",
                        "command": "wget https://files.rcsb.org/download/1UBQ.pdb",
                        "inputs": {},
                        "outputs": {"structure": "1UBQ.pdb"},
                        "dependencies": [],
                        "description": "Download ubiquitin structure from PDB",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx pdb2gmx -f 1UBQ.pdb -o processed.gro -water tip3p -ff amber99sb-ildn",
                        "inputs": {"structure": "1UBQ.pdb"},
                        "outputs": {"structure": "processed.gro", "topology": "topol.top"},
                        "dependencies": ["0"],
                        "description": "Process structure and generate topology",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt cubic",
                        "inputs": {"structure": "processed.gro"},
                        "outputs": {"structure": "boxed.gro"},
                        "dependencies": ["1"],
                        "description": "Define simulation box",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top",
                        "inputs": {"structure": "boxed.gro", "topology": "topol.top"},
                        "outputs": {"structure": "solvated.gro", "topology": "topol.top"},
                        "dependencies": ["2"],
                        "description": "Add water molecules to box",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr",
                        "inputs": {"structure": "solvated.gro", "topology": "topol.top"},
                        "outputs": {"tpr": "ions.tpr"},
                        "dependencies": ["3"],
                        "description": "Prepare input for ion addition",
                    },
                    {
                        "tool": "gmx",
                        "command": "echo 'SOL' | gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15",
                        "inputs": {"tpr": "ions.tpr", "topology": "topol.top"},
                        "outputs": {"structure": "neutralized.gro", "topology": "topol.top"},
                        "dependencies": ["4"],
                        "description": "Add ions to neutralize and reach 0.15 M NaCl",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr",
                        "inputs": {"structure": "neutralized.gro", "topology": "topol.top"},
                        "outputs": {"tpr": "em.tpr"},
                        "dependencies": ["5"],
                        "description": "Prepare energy minimization input",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx mdrun -deffnm em -v",
                        "inputs": {"tpr": "em.tpr"},
                        "outputs": {"structure": "em.gro", "log": "em.log"},
                        "dependencies": ["6"],
                        "description": "Run energy minimization",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr",
                        "inputs": {"structure": "em.gro", "topology": "topol.top"},
                        "outputs": {"tpr": "nvt.tpr"},
                        "dependencies": ["7"],
                        "description": "Prepare NVT equilibration input",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx mdrun -deffnm nvt -v",
                        "inputs": {"tpr": "nvt.tpr"},
                        "outputs": {"trajectory": "nvt.xtc", "structure": "nvt.gro"},
                        "dependencies": ["8"],
                        "description": "Run NVT equilibration (100 ps)",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr",
                        "inputs": {"structure": "nvt.gro", "topology": "topol.top", "checkpoint": "nvt.cpt"},
                        "outputs": {"tpr": "npt.tpr"},
                        "dependencies": ["9"],
                        "description": "Prepare NPT equilibration input",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx mdrun -deffnm npt -v",
                        "inputs": {"tpr": "npt.tpr"},
                        "outputs": {"trajectory": "npt.xtc", "structure": "npt.gro"},
                        "dependencies": ["10"],
                        "description": "Run NPT equilibration (100 ps)",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr",
                        "inputs": {"structure": "npt.gro", "topology": "topol.top", "checkpoint": "npt.cpt"},
                        "outputs": {"tpr": "md.tpr"},
                        "dependencies": ["11"],
                        "description": "Prepare production MD input (100 ns)",
                    },
                    {
                        "tool": "gmx",
                        "command": "gmx mdrun -deffnm md -v",
                        "inputs": {"tpr": "md.tpr"},
                        "outputs": {"trajectory": "md.xtc", "structure": "md.gro", "energy": "md.edr"},
                        "dependencies": ["12"],
                        "description": "Run production MD simulation (100 ns)",
                    },
                ],
                "estimated_compute": "~12 hours on 8 CPU cores or ~4 hours on 1 GPU (RTX 3090)",
                "required_software": ["GROMACS 2023+", "wget"],
                "validation_checks": [
                    "Energy minimized to < 1000 kJ/mol/nm",
                    "NVT temperature stable at 300 K",
                    "NPT pressure stable at 1 bar",
                    "Density converged to ~1000 kg/m^3 for water",
                    "RMSD stable during production run",
                ],
            }
        elif domain == "density_functional_theory":
            return {
                "steps": [
                    {
                        "tool": "wget",
                        "command": "wget https://materialsproject.org/static/cifs/Si.cif -O Si.cif",
                        "inputs": {},
                        "outputs": {"structure": "Si.cif"},
                        "dependencies": [],
                        "description": "Download silicon structure (diamond cubic)",
                    },
                    {
                        "tool": "cif2cell",
                        "command": "cif2cell Si.cif -p quantum-espresso -o Si.pw.in",
                        "inputs": {"structure": "Si.cif"},
                        "outputs": {"input": "Si.pw.in"},
                        "dependencies": ["0"],
                        "description": "Convert CIF to Quantum ESPRESSO input format",
                    },
                    {
                        "tool": "pw.x",
                        "command": "mpirun -np 8 pw.x -in Si.scf.in > Si.scf.out",
                        "inputs": {"input": "Si.scf.in"},
                        "outputs": {"charge_density": "Si.save/charge-density.dat", "output": "Si.scf.out"},
                        "dependencies": ["1"],
                        "description": "Self-consistent field (SCF) calculation",
                    },
                    {
                        "tool": "pw.x",
                        "command": "mpirun -np 8 pw.x -in Si.bands.in > Si.bands.out",
                        "inputs": {"charge_density": "Si.save/charge-density.dat", "input": "Si.bands.in"},
                        "outputs": {"bands": "Si.bands.dat", "output": "Si.bands.out"},
                        "dependencies": ["2"],
                        "description": "Non-SCF band structure calculation along high-symmetry path",
                    },
                    {
                        "tool": "bands.x",
                        "command": "bands.x -in Si.bands.pp.in > Si.bands.pp.out",
                        "inputs": {"bands": "Si.bands.dat", "input": "Si.bands.pp.in"},
                        "outputs": {"bands_data": "Si.bands.gnu", "output": "Si.bands.pp.out"},
                        "dependencies": ["3"],
                        "description": "Post-process band structure data",
                    },
                    {
                        "tool": "dos.x",
                        "command": "dos.x -in Si.dos.in > Si.dos.out",
                        "inputs": {"charge_density": "Si.save/charge-density.dat", "input": "Si.dos.in"},
                        "outputs": {"dos": "Si.dos", "output": "Si.dos.out"},
                        "dependencies": ["2"],
                        "description": "Calculate density of states",
                    },
                    {
                        "tool": "gnuplot",
                        "command": "gnuplot plot_bands.gnu",
                        "inputs": {"bands_data": "Si.bands.gnu"},
                        "outputs": {"plot": "Si_bands.png"},
                        "dependencies": ["4"],
                        "description": "Plot band structure",
                    },
                ],
                "estimated_compute": "~30 minutes on 8 CPU cores",
                "required_software": ["Quantum ESPRESSO 7.x", "cif2cell", "gnuplot"],
                "validation_checks": [
                    "SCF converges to < 1e-6 Ry total energy difference",
                    "Band gap matches known value (~1.1 eV for Si, with DFT underestimation)",
                    "DOS integrates to correct number of electrons (8 per Si atom)",
                    "Band path covers high-symmetry points: Gamma-X-W-L-Gamma",
                ],
            }
        return {
            "steps": [],
            "estimated_compute": "unknown",
            "required_software": [],
            "validation_checks": [],
        }

    def _classify_domain(self, query: str) -> str:
        """Classify the scientific domain of the query."""
        prompt = f"""Classify the following scientific query into one of these domains:
molecular_dynamics, density_functional_theory, bioinformatics, fluid_dynamics, quantum_chemistry, other.

Query: {query}

Respond with only the domain name."""
        return self.llm.complete(prompt).strip().lower()

    def _parse_plan(self, query: str, domain: str, raw: Dict[str, Any]) -> WorkflowPlan:
        """Parse LLM output into a structured WorkflowPlan."""
        steps = [
            WorkflowStep(
                tool=s["tool"],
                command=s["command"],
                inputs=s.get("inputs", {}),
                outputs=s.get("outputs", {}),
                dependencies=s.get("dependencies", []),
                description=s.get("description", ""),
            )
            for s in raw.get("steps", [])
        ]

        return WorkflowPlan(
            query=query,
            domain=domain,
            steps=steps,
            estimated_compute=raw.get("estimated_compute"),
            required_software=raw.get("required_software", []),
            validation_checks=raw.get("validation_checks", []),
        )

    def _validate_plan(self, plan: WorkflowPlan) -> WorkflowPlan:
        """Validate workflow plan for consistency and completeness."""
        # Check for circular dependencies
        dep_graph = {i: set(step.dependencies) for i, step in enumerate(plan.steps)}
        visited = set()
        rec_stack = set()

        def has_cycle(node: int) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for dep in dep_graph.get(node, set()):
                try:
                    dep_idx = int(dep)
                except ValueError:
                    continue
                if dep_idx not in visited:
                    if has_cycle(dep_idx):
                        return True
                elif dep_idx in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for i in range(len(plan.steps)):
            if i not in visited:
                if has_cycle(i):
                    raise ValueError("Workflow plan contains circular dependencies")

        # Check all dependencies reference valid steps
        for i, step in enumerate(plan.steps):
            for dep in step.dependencies:
                try:
                    dep_idx = int(dep)
                except ValueError:
                    continue  # Named dependencies handled at runtime
                if dep_idx < 0 or dep_idx >= len(plan.steps):
                    raise ValueError(
                        f"Step {i} references invalid dependency: {dep}"
                    )

        return plan

    def to_script(self, plan: WorkflowPlan, format: str = "python") -> str:
        """
        Convert a workflow plan to an executable script.

        Args:
            plan: The workflow plan to convert.
            format: Output format - 'python', 'bash', 'snakemake', 'cwl'.

        Returns:
            Executable script as a string.
        """
        if format == "python":
            return self._to_python(plan)
        elif format == "bash":
            return self._to_bash(plan)
        elif format == "snakemake":
            return self._to_snakemake(plan)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_python(self, plan: WorkflowPlan) -> str:
        """Generate a Python script from the workflow plan."""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            f"Auto-generated workflow for: {plan.query}",
            f"Domain: {plan.domain}",
            '"""',
            "",
            "import subprocess",
            "import json",
            "from pathlib import Path",
            "",
            f"WORKFLOW = {json.dumps(plan.__dict__, default=str, indent=4)}",
            "",
            "def run_step(step, step_idx):",
            '    print(f"[Step {step_idx}] {step[\'tool\']}: {step[\'description\']}")',
            "    # TODO: Implement tool-specific execution",
            '    cmd = step["command"]',
            "    # subprocess.run(cmd, shell=True, check=True)",
            "    print(f'  Command: {cmd}')",
            "",
            "def main():",
        ]

        for i, step in enumerate(plan.steps):
            lines.append(f"    # Step {i}: {step.description}")
            lines.append(f"    run_step(WORKFLOW['steps'][{i}], {i})")
            lines.append("")

        lines.extend([
            'if __name__ == "__main__":',
            "    main()",
            "",
        ])

        return "\n".join(lines)

    def _to_bash(self, plan: WorkflowPlan) -> str:
        """Generate a bash script from the workflow plan."""
        lines = [
            "#!/usr/bin/env bash",
            f"# Auto-generated workflow for: {plan.query}",
            f"# Domain: {plan.domain}",
            "set -euo pipefail",
            "",
        ]

        for i, step in enumerate(plan.steps):
            lines.append(f"# Step {i}: {step.description}")
            lines.append(f'echo "[Step {i}] {step.tool}: {step.description}"')
            lines.append(step.command)
            lines.append("")

        return "\n".join(lines)

    def _to_snakemake(self, plan: WorkflowPlan) -> str:
        """Generate a Snakemake workflow from the plan."""
        lines = [
            f"# Auto-generated Snakemake workflow for: {plan.query}",
            f"# Domain: {plan.domain}",
            "",
        ]

        for i, step in enumerate(plan.steps):
            rule_name = f"step_{i}_{step.tool.replace('-', '_')}"
            lines.append(f"rule {rule_name}:")
            if step.inputs:
                lines.append("    input:")
                for k, v in step.inputs.items():
                    lines.append(f'        {k}="{v}"')
            if step.outputs:
                lines.append("    output:")
                for k, v in step.outputs.items():
                    lines.append(f'        {k}="{v}"')
            lines.append("    shell:")
            lines.append(f'        """{step.command}"""')
            lines.append("")

        return "\n".join(lines)
