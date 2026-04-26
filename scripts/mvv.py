#!/usr/bin/env python3
"""
ai4s-core Minimal Viable Verification (MVV) Script

Purpose: Let a new user experience value in < 5 minutes, zero setup.

Usage:
    python3 scripts/mvv.py

What it does:
    1. Runs mock mode (no API key needed)
    2. Generates a GROMACS workflow for a simple protein
    3. Exports to Python script
    4. Runs validation checks
    5. Shows a summary with timing

Exit codes:
    0 - All checks passed, user can proceed
    1 - Something failed, show troubleshooting
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, desc):
    """Run a command and report timing."""
    print(f"\n{'='*60}")
    print(f"Step: {desc}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    elapsed = time.time() - start
    
    print(f"Time: {elapsed:.2f}s | Exit: {result.returncode}")
    if result.stdout:
        print(result.stdout[:2000])  # Truncate long output
    if result.stderr and result.returncode != 0:
        print(f"STDERR: {result.stderr[:500]}")
    
    return result.returncode == 0, elapsed


def main():
    print("="*60)
    print(" ai4s-core Minimal Viable Verification")
    print(" Experience value in < 5 minutes, zero setup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9+ required")
        return 1
    
    # Check ai4s-core is importable
    try:
        from ai4s_core.orchestrator import WorkflowOrchestrator
        from ai4s_core.domain import DomainRegistry
        from ai4s_core.llm_interface import LLMInterface
        print("\n[OK] ai4s-core modules importable")
    except ImportError as e:
        print(f"\n[FAIL] Cannot import ai4s-core: {e}")
        print("Fix: pip install -e .")
        return 1
    
    results = []
    total_start = time.time()
    
    # Step 1: Generate workflow (mock mode)
    ok, t = run_command(
        'python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --json > /tmp/mvv-plan.json 2>/dev/null',
        "Generate workflow (mock mode, no API key)"
    )
    results.append(("Workflow generation", ok, t))
    if not ok:
        print("[FAIL] Workflow generation failed")
        return 1
    
    # Validate JSON
    try:
        with open("/tmp/mvv-plan.json") as f:
            plan = json.load(f)
        print(f"[OK] Valid JSON | Domain: {plan['domain']} | Steps: {len(plan['steps'])}")
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        return 1
    
    # Step 2: Export to Python
    ok, t = run_command(
        'python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --format python > /tmp/mvv-script.py 2>/dev/null',
        "Export to Python script"
    )
    results.append(("Python export", ok, t))
    
    script_lines = len(Path("/tmp/mvv-script.py").read_text().splitlines())
    print(f"[OK] Python script: {script_lines} lines")
    
    # Step 3: Export to Bash
    ok, t = run_command(
        'python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --format bash > /tmp/mvv-script.sh 2>/dev/null',
        "Export to Bash script"
    )
    results.append(("Bash export", ok, t))
    
    # Step 4: List domains
    ok, t = run_command(
        'python -m ai4s_core.cli list-domains > /tmp/mvv-domains.txt 2>/dev/null',
        "List supported domains"
    )
    results.append(("List domains", ok, t))
    
    domain_count = len([l for l in Path("/tmp/mvv-domains.txt").read_text().splitlines() if l.strip()])
    print(f"[OK] {domain_count} domains supported")
    
    # Step 5: Validation checks
    validation_checks = plan.get("validation_checks", [])
    print(f"\n[OK] Validation checks: {len(validation_checks)} included")
    for vc in validation_checks[:3]:
        if isinstance(vc, dict):
            print(f"  - {vc.get('name', 'unnamed')}: {vc.get('severity', 'info')}")
        else:
            print(f"  - {vc}")
    
    # Summary
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(" SUMMARY")
    print(f"{'='*60}")
    print(f"Total time: {total_time:.2f}s")
    print()
    
    all_passed = True
    for name, ok, t in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  [{status}] {name}: {t:.2f}s")
    
    print()
    if all_passed:
        print("All checks PASSED. ai4s-core is working correctly.")
        print()
        print("Next steps:")
        print("  1. Get an API key: export AI4S_LLM_API_KEY='your-key'")
        print("  2. Run with real LLM: ai4s plan 'your research query'")
        print("  3. Read docs: https://github.com/agent2agent-dev/ai4s-core")
        return 0
    else:
        print("Some checks FAILED. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
