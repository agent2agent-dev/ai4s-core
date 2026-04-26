"""
Test mock mode for all 5 scientific domains.
Ensures mock plans are complete, realistic, and produce valid scripts.
"""

import pytest
from ai4s_core.orchestrator import WorkflowOrchestrator, WorkflowPlan


class TestMockModeDomains:
    """Test that all 5 scientific domains have complete mock plans."""

    def test_molecular_dynamics_mock(self):
        """MD mock plan should have 14 steps with GROMACS commands."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "molecular_dynamics"
        assert len(plan.steps) == 14
        # Should have auxiliary files (MDP files)
        steps_with_aux = [s for s in plan.steps if s.auxiliary_files]
        assert len(steps_with_aux) >= 5
        # Should have validation checks
        assert len(plan.validation_checks) >= 4
        # Should estimate compute time
        assert plan.estimated_compute is not None

    def test_dft_mock(self):
        """DFT mock plan should have 7 steps with Quantum ESPRESSO commands."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Calculate band structure of silicon",
            domain_hint="density_functional_theory",
            use_mock=True,
        )
        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "density_functional_theory"
        assert len(plan.steps) == 7
        # Should have auxiliary files (input files)
        steps_with_aux = [s for s in plan.steps if s.auxiliary_files]
        assert len(steps_with_aux) >= 4
        # Should have validation checks
        assert len(plan.validation_checks) >= 4

    def test_quantum_chemistry_mock(self):
        """QC mock plan should have 4 steps with ORCA commands."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Optimize geometry of caffeine molecule",
            domain_hint="quantum_chemistry",
            use_mock=True,
        )
        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "quantum_chemistry"
        assert len(plan.steps) == 4
        # Should have auxiliary files (ORCA input files)
        steps_with_aux = [s for s in plan.steps if s.auxiliary_files]
        assert len(steps_with_aux) >= 3

    def test_bioinformatics_mock(self):
        """Bioinformatics mock plan should have 7 steps with QC/alignment/counting."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Run RNA-seq differential expression",
            domain_hint="bioinformatics",
            use_mock=True,
        )
        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "bioinformatics"
        assert len(plan.steps) == 7
        # Should have auxiliary files (R script)
        steps_with_aux = [s for s in plan.steps if s.auxiliary_files]
        assert len(steps_with_aux) >= 1

    def test_materials_simulation_mock(self):
        """Materials mock plan should have 8 steps with LAMMPS commands."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate aluminum FCC crystal with LAMMPS",
            domain_hint="materials_simulation",
            use_mock=True,
        )
        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "materials_simulation"
        assert len(plan.steps) == 8
        # Should have auxiliary files (LAMMPS input files)
        steps_with_aux = [s for s in plan.steps if s.auxiliary_files]
        assert len(steps_with_aux) >= 5

    def test_mock_to_python_script(self):
        """Mock plan should generate valid Python script."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        script = orch.to_script(plan, format="python")
        assert "#!/usr/bin/env python3" in script
        assert "subprocess" in script
        assert "WORKFLOW" in script
        # Should have all 14 steps (15 because function def also contains "run_step(")
        assert script.count("run_step(") == 15  # 14 calls + 1 function def

    def test_mock_to_bash_script(self):
        """Mock plan should generate valid Bash script."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        script = orch.to_script(plan, format="bash")
        assert "#!/usr/bin/env bash" in script
        assert "set -euo pipefail" in script
        # Should have auxiliary file writes
        assert "cat >" in script

    def test_mock_to_snakemake_script(self):
        """Mock plan should generate valid Snakemake workflow."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        script = orch.to_script(plan, format="snakemake")
        assert "rule" in script
        # Should have rules for each step
        assert script.count("rule step_") == 14

    def test_mock_plan_dependency_graph(self):
        """Mock plan dependencies should form a valid DAG."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        # Check no circular dependencies (already validated by plan())
        # Check all dependencies reference earlier steps
        for i, step in enumerate(plan.steps):
            for dep in step.dependencies:
                dep_idx = int(dep)
                assert dep_idx < i, f"Step {i} depends on step {dep_idx} which comes after it"

    def test_mock_plan_error_handling(self):
        """Mock plan should have error handling for critical steps."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Simulate ubiquitin in water",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )
        steps_with_eh = [s for s in plan.steps if s.error_handling]
        assert len(steps_with_eh) >= 3  # EM, NVT, NPT should have error handling
