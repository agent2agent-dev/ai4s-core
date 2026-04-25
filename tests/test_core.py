"""
Test suite for ai4s-core.
"""

import pytest
from ai4s_core.orchestrator import WorkflowOrchestrator, WorkflowPlan, WorkflowStep
from ai4s_core.domain import DomainRegistry, DomainSpec
from ai4s_core.llm_interface import LLMInterface


class TestDomainRegistry:
    def test_default_domains_registered(self):
        reg = DomainRegistry()
        domains = reg.list_domains()
        assert "molecular_dynamics" in domains
        assert "density_functional_theory" in domains
        assert "bioinformatics" in domains
        assert "quantum_chemistry" in domains

    def test_get_domain_context(self):
        reg = DomainRegistry()
        ctx = reg.get_context("molecular_dynamics")
        assert "GROMACS" in ctx
        assert "temperature" in ctx
        assert "NVT" in ctx

    def test_tool_exists(self):
        reg = DomainRegistry()
        assert reg.tool_exists("molecular_dynamics", "GROMACS")
        assert not reg.tool_exists("molecular_dynamics", "VASP")

    def test_register_new_domain(self):
        reg = DomainRegistry()
        reg.register(
            DomainSpec(
                name="fluid_dynamics",
                description="CFD simulations",
                common_tools=["OpenFOAM", "ANSYS Fluent"],
            )
        )
        assert "fluid_dynamics" in reg.list_domains()


class TestWorkflowOrchestrator:
    def test_plan_basic(self):
        """Test that plan() returns a WorkflowPlan with correct structure."""
        # Mock LLM that returns a fixed plan
        class MockLLM:
            def complete(self, prompt, **kwargs):
                return "molecular_dynamics"

            def generate_plan(self, query, context):
                return {
                    "steps": [
                        {
                            "tool": "packmol",
                            "command": "packmol < packmol.inp",
                            "inputs": {"input_file": "molecules.pdb"},
                            "outputs": {"output_file": "system.pdb"},
                            "dependencies": [],
                            "description": "Build initial system",
                        },
                        {
                            "tool": "gmx",
                            "command": "gmx mdrun -deffnm em",
                            "inputs": {"structure": "system.pdb"},
                            "outputs": {"structure": "em.gro"},
                            "dependencies": ["0"],
                            "description": "Energy minimization",
                        },
                    ],
                    "estimated_compute": "1 hour",
                    "required_software": ["packmol", "gromacs"],
                    "validation_checks": ["check energy converged"],
                }

        orch = WorkflowOrchestrator(llm=MockLLM())
        plan = orch.plan("Simulate a protein in water for 100 ns")

        assert isinstance(plan, WorkflowPlan)
        assert plan.domain == "molecular_dynamics"
        assert len(plan.steps) == 2
        assert plan.steps[0].tool == "packmol"
        assert plan.steps[1].dependencies == ["0"]

    def test_validate_plan_circular_deps(self):
        """Test that circular dependencies are detected."""
        orch = WorkflowOrchestrator()
        plan = WorkflowPlan(
            query="test",
            domain="md",
            steps=[
                WorkflowStep(tool="a", command="a", dependencies=["1"]),
                WorkflowStep(tool="b", command="b", dependencies=["0"]),
            ],
        )
        with pytest.raises(ValueError, match="circular"):
            orch._validate_plan(plan)

    def test_validate_plan_invalid_dep_index(self):
        """Test that out-of-range dependencies are detected."""
        orch = WorkflowOrchestrator()
        plan = WorkflowPlan(
            query="test",
            domain="md",
            steps=[
                WorkflowStep(tool="a", command="a", dependencies=["5"]),
            ],
        )
        with pytest.raises(ValueError, match="invalid dependency"):
            orch._validate_plan(plan)

    def test_to_python(self):
        orch = WorkflowOrchestrator()
        plan = WorkflowPlan(
            query="test simulation",
            domain="md",
            steps=[
                WorkflowStep(
                    tool="gmx",
                    command="gmx mdrun -deffnm run",
                    description="Run MD",
                ),
            ],
        )
        script = orch.to_script(plan, format="python")
        assert "#!/usr/bin/env python3" in script
        assert "Auto-generated workflow" in script
        assert "gmx mdrun" in script

    def test_to_bash(self):
        orch = WorkflowOrchestrator()
        plan = WorkflowPlan(
            query="test",
            domain="md",
            steps=[
                WorkflowStep(tool="echo", command="echo hello", description="Say hello"),
            ],
        )
        script = orch.to_script(plan, format="bash")
        assert "#!/usr/bin/env bash" in script
        assert "set -euo pipefail" in script
        assert "echo hello" in script

    def test_to_snakemake(self):
        orch = WorkflowOrchestrator()
        plan = WorkflowPlan(
            query="test",
            domain="md",
            steps=[
                WorkflowStep(
                    tool="gmx",
                    command="gmx mdrun",
                    inputs={"structure": "input.gro"},
                    outputs={"trajectory": "output.xtc"},
                    description="Run MD",
                ),
            ],
        )
        script = orch.to_script(plan, format="snakemake")
        assert "rule step_0_gmx" in script
        assert "input.gro" in script
        assert "output.xtc" in script


class TestLLMInterface:
    def test_init_defaults(self):
        llm = LLMInterface()
        assert llm.provider == "openai"
        assert llm.model == "gpt-4o"

    def test_init_override(self):
        llm = LLMInterface(provider="anthropic", model="claude-3-opus")
        assert llm.provider == "anthropic"
        assert llm.model == "claude-3-opus"

    def test_generate_plan_json_parsing(self):
        import json
        class FakeMessage:
            content = json.dumps({
                "steps": [],
                "estimated_compute": "none",
                "required_software": [],
                "validation_checks": [],
            })

        class FakeChoice:
            message = FakeMessage()

        class FakeResponse:
            choices = [FakeChoice()]

        class FakeCompletions:
            def create(self, **kwargs):
                return FakeResponse()

        class FakeChat:
            completions = FakeCompletions()

        class FakeClient:
            chat = FakeChat()

        llm = LLMInterface()
        llm._client = FakeClient()
        llm.provider = "openai"

        plan = llm.generate_plan("test", "context")
        assert "steps" in plan
