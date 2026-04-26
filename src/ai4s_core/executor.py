"""
Execution engine: runs scientific workflows using containerized tools.

Supports:
- Docker containers for reproducible execution
- Local subprocess fallback for installed tools
- Step-by-step execution with checkpointing
- Error handling and retry logic
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .orchestrator import WorkflowPlan, WorkflowStep


# Docker image registry for scientific tools
DOCKER_IMAGES = {
    "gmx": "quay.io/biocontainers/gromacs:2023.4",
    "gromacs": "quay.io/biocontainers/gromacs:2023.4",
    "pw.x": "quay.io/biocontainers/quantum-espresso:7.2",
    "quantum_espresso": "quay.io/biocontainers/quantum-espresso:7.2",
    "orca": "valentinsulzer/orca:5.0.4",  # Community image
    "fastqc": "quay.io/biocontainers/fastqc:0.12.1",
    "hisat2": "quay.io/biocontainers/hisat2:2.2.1",
    "samtools": "quay.io/biocontainers/samtools:1.18",
    "featurecounts": "quay.io/biocontainers/subread:2.0.6",
    "wget": "alpine:latest",
    "python": "python:3.11-slim",
    "R": "rocker/r-ver:4.3.0",
}


class ExecutionResult:
    """Result of executing a workflow step."""
    def __init__(
        self,
        step_idx: int,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        outputs_created: List[str] = None,
        error_message: str = "",
    ):
        self.step_idx = step_idx
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.outputs_created = outputs_created or []
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_idx": self.step_idx,
            "success": self.success,
            "stdout": self.stdout[:2000],  # Truncate for logs
            "stderr": self.stderr[:2000],
            "exit_code": self.exit_code,
            "outputs_created": self.outputs_created,
            "error_message": self.error_message,
        }


class WorkflowExecutor:
    """
    Execute workflow plans using Docker containers or local tools.
    
    Design philosophy:
    - Default to Docker for reproducibility
    - Fall back to local tools if Docker unavailable
    - Write auxiliary files before each step
    - Check outputs after each step
    - Support checkpoint/resume
    """

    def __init__(
        self,
        use_docker: bool = True,
        work_dir: Optional[str] = None,
        docker_runtime: str = "docker",
    ):
        self.use_docker = use_docker
        self.work_dir = work_dir or os.getcwd()
        self.docker_runtime = docker_runtime
        self.results: List[ExecutionResult] = []
        self._docker_available: Optional[bool] = None

    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        if self._docker_available is not None:
            return self._docker_available
        try:
            result = subprocess.run(
                [self.docker_runtime, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._docker_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._docker_available = False
        return self._docker_available

    def _get_docker_image(self, tool: str) -> Optional[str]:
        """Get Docker image for a tool."""
        # Direct match
        if tool in DOCKER_IMAGES:
            return DOCKER_IMAGES[tool]
        # Try prefix match (e.g., "gmx_mdrun" -> "gmx")
        for prefix, image in DOCKER_IMAGES.items():
            if tool.startswith(prefix) or prefix in tool:
                return image
        return None

    def _write_auxiliary_files(self, step: WorkflowStep) -> None:
        """Write auxiliary files for a step."""
        for filename, content in step.auxiliary_files.items():
            filepath = Path(self.work_dir) / filename
            filepath.write_text(content)
            print(f"  [Written] {filepath}")

    def _check_outputs(self, step: WorkflowStep) -> List[str]:
        """Check which expected outputs were created."""
        created = []
        for output_name, output_path in step.outputs.items():
            full_path = Path(self.work_dir) / output_path
            if full_path.exists():
                created.append(str(full_path))
        return created

    def _run_docker(
        self,
        image: str,
        command: str,
        step: WorkflowStep,
    ) -> ExecutionResult:
        """Run a command inside a Docker container."""
        work_path = Path(self.work_dir).resolve()
        
        # Build docker run command
        cmd_parts = [
            self.docker_runtime,
            "run",
            "--rm",  # Remove container after run
            "-v", f"{work_path}:/work",
            "-w", "/work",
            image,
            "sh", "-c", command,
        ]
        
        print(f"  [Docker] {image}: {command[:80]}...")
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout for scientific jobs
                cwd=self.work_dir,
            )
            
            outputs = self._check_outputs(step)
            
            if result.returncode == 0:
                return ExecutionResult(
                    step_idx=-1,  # Set by caller
                    success=True,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=0,
                    outputs_created=outputs,
                )
            else:
                return ExecutionResult(
                    step_idx=-1,
                    success=False,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    outputs_created=outputs,
                    error_message=f"Docker command failed with exit code {result.returncode}",
                )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                step_idx=-1,
                success=False,
                error_message="Docker command timed out (>1 hour)",
            )
        except Exception as e:
            return ExecutionResult(
                step_idx=-1,
                success=False,
                error_message=f"Docker execution error: {str(e)}",
            )

    def _run_local(
        self,
        command: str,
        step: WorkflowStep,
    ) -> ExecutionResult:
        """Run a command locally using subprocess."""
        print(f"  [Local] {command[:80]}...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600,
                cwd=self.work_dir,
            )
            
            outputs = self._check_outputs(step)
            
            if result.returncode == 0:
                return ExecutionResult(
                    step_idx=-1,
                    success=True,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=0,
                    outputs_created=outputs,
                )
            else:
                return ExecutionResult(
                    step_idx=-1,
                    success=False,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    outputs_created=outputs,
                    error_message=f"Command failed with exit code {result.returncode}",
                )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                step_idx=-1,
                success=False,
                error_message="Command timed out (>1 hour)",
            )
        except Exception as e:
            return ExecutionResult(
                step_idx=-1,
                success=False,
                error_message=f"Execution error: {str(e)}",
            )

    def execute_step(self, step: WorkflowStep, step_idx: int) -> ExecutionResult:
        """Execute a single workflow step."""
        print(f"\n[Step {step_idx}] {step.tool}: {step.description}")
        
        # Write auxiliary files first
        self._write_auxiliary_files(step)
        
        # Determine execution method
        image = self._get_docker_image(step.tool)
        
        if self.use_docker and self._check_docker() and image:
            result = self._run_docker(image, step.command, step)
        else:
            if self.use_docker and not self._check_docker():
                print("  [Warning] Docker not available, falling back to local execution")
            elif self.use_docker and not image:
                print(f"  [Warning] No Docker image for '{step.tool}', using local execution")
            result = self._run_local(step.command, step)
        
        result.step_idx = step_idx
        
        # Check error handling
        if not result.success and step.error_handling:
            check_file = step.error_handling.get("check_file")
            fallback = step.error_handling.get("fallback")
            if check_file:
                check_path = Path(self.work_dir) / check_file
                if not check_path.exists():
                    print(f"  [Error] Expected output {check_file} not found")
                    if fallback:
                        print(f"  [Fallback] {fallback}")
        
        # Print result summary
        if result.success:
            print(f"  [OK] Created {len(result.outputs_created)} output(s)")
        else:
            print(f"  [FAILED] {result.error_message}")
            if result.stderr:
                print(f"  [stderr] {result.stderr[:500]}")
        
        return result

    def execute_plan(
        self,
        plan: WorkflowPlan,
        resume_from: Optional[int] = None,
        stop_on_error: bool = True,
    ) -> List[ExecutionResult]:
        """
        Execute a complete workflow plan.
        
        Args:
            plan: The workflow plan to execute.
            resume_from: Step index to resume from (for checkpointing).
            stop_on_error: If True, stop execution on first failure.
        
        Returns:
            List of ExecutionResult for each step.
        """
        print(f"\n{'='*60}")
        print(f"Executing workflow: {plan.query}")
        print(f"Domain: {plan.domain}")
        print(f"Steps: {len(plan.steps)}")
        print(f"Work directory: {self.work_dir}")
        print(f"Docker: {'enabled' if self.use_docker else 'disabled'}")
        print(f"{'='*60}")
        
        start_idx = resume_from or 0
        self.results = []
        
        for i in range(start_idx, len(plan.steps)):
            result = self.execute_step(plan.steps[i], i)
            self.results.append(result)
            
            if not result.success and stop_on_error:
                print(f"\n[STOP] Step {i} failed. Stopping workflow.")
                break
        
        # Summary
        success_count = sum(1 for r in self.results if r.success)
        print(f"\n{'='*60}")
        print(f"Workflow complete: {success_count}/{len(self.results)} steps succeeded")
        print(f"{'='*60}")
        
        return self.results

    def save_results(self, path: str) -> None:
        """Save execution results to a JSON file."""
        data = {
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
            },
        }
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"[Saved] Results to {path}")


def dry_run(plan: WorkflowPlan, work_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Perform a dry run: show what would be executed without running anything.
    
    Returns:
        List of step summaries with tool, command, and auxiliary files.
    """
    work_path = Path(work_dir or os.getcwd())
    summary = []
    
    print(f"\n{'='*60}")
    print(f"DRY RUN: {plan.query}")
    print(f"{'='*60}")
    
    for i, step in enumerate(plan.steps):
        print(f"\n[Step {i}] {step.tool}: {step.description}")
        print(f"  Command: {step.command}")
        
        if step.auxiliary_files:
            print(f"  Auxiliary files:")
            for fname, content in step.auxiliary_files.items():
                fpath = work_path / fname
                print(f"    - {fname} ({len(content)} chars) -> {fpath}")
        
        if step.error_handling:
            print(f"  Error handling: {step.error_handling}")
        
        summary.append({
            "step_idx": i,
            "tool": step.tool,
            "command": step.command,
            "auxiliary_files": list(step.auxiliary_files.keys()),
            "error_handling": step.error_handling,
        })
    
    print(f"\n{'='*60}")
    print(f"Total: {len(plan.steps)} steps")
    print(f"{'='*60}")
    
    return summary
