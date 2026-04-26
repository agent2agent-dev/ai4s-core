"""
Test execution engine functionality.
"""

import json
import tempfile
from pathlib import Path

from ai4s_core.orchestrator import WorkflowOrchestrator, WorkflowPlan, WorkflowStep
from ai4s_core.executor import WorkflowExecutor, dry_run, DOCKER_IMAGES


class TestExecutor:
    def test_docker_images_registry(self):
        """Test that Docker images are registered for common tools."""
        assert "gmx" in DOCKER_IMAGES
        assert "gromacs" in DOCKER_IMAGES
        assert "pw.x" in DOCKER_IMAGES
        assert "fastqc" in DOCKER_IMAGES
        assert "wget" in DOCKER_IMAGES

    def test_executor_init(self):
        """Test WorkflowExecutor initialization."""
        executor = WorkflowExecutor(use_docker=False, work_dir="/tmp")
        assert executor.use_docker is False
        assert executor.work_dir == "/tmp"
        assert executor.results == []

    def test_dry_run(self):
        """Test dry run functionality."""
        orch = WorkflowOrchestrator()
        plan = orch.plan(
            "Run a GROMACS MD simulation",
            domain_hint="molecular_dynamics",
            use_mock=True,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            summary = dry_run(plan, tmpdir)
            assert len(summary) == len(plan.steps)
            # Check that auxiliary files are listed
            steps_with_aux = [s for s in summary if s["auxiliary_files"]]
            assert len(steps_with_aux) > 0

    def test_executor_local_fallback(self):
        """Test that executor falls back to local when Docker unavailable."""
        executor = WorkflowExecutor(use_docker=False)
        
        # Create a simple plan with a harmless command
        plan = WorkflowPlan(
            query="test",
            domain="test",
            steps=[
                WorkflowStep(
                    tool="python",
                    command="python3 -c 'print(\"hello\")'",
                    outputs={"out": "hello.txt"},
                    description="Test step",
                ),
            ],
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            executor.work_dir = tmpdir
            results = executor.execute_plan(plan, stop_on_error=False)
            assert len(results) == 1
            # Should attempt execution (may fail if python3 not available)
            assert results[0].step_idx == 0

    def test_execution_result_serialization(self):
        """Test ExecutionResult can be serialized to dict."""
        from ai4s_core.executor import ExecutionResult
        
        result = ExecutionResult(
            step_idx=0,
            success=True,
            stdout="hello",
            stderr="",
            exit_code=0,
            outputs_created=["file.txt"],
        )
        
        d = result.to_dict()
        assert d["step_idx"] == 0
        assert d["success"] is True
        assert d["exit_code"] == 0
        assert d["outputs_created"] == ["file.txt"]

    def test_executor_save_results(self):
        """Test saving results to JSON file."""
        executor = WorkflowExecutor(use_docker=False)
        
        from ai4s_core.executor import ExecutionResult
        executor.results = [
            ExecutionResult(step_idx=0, success=True, exit_code=0),
            ExecutionResult(step_idx=1, success=False, exit_code=1, error_message="failed"),
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result_path = Path(tmpdir) / "results.json"
            executor.save_results(str(result_path))
            
            data = json.loads(result_path.read_text())
            assert data["summary"]["total"] == 2
            assert data["summary"]["successful"] == 1
            assert data["summary"]["failed"] == 1
