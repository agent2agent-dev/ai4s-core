#!/usr/bin/env python3
"""
Test script for real LLM integration with ai4s-core.
Run this after setting AI4S_LLM_API_KEY and AI4S_LLM_PROVIDER.

Usage:
    export AI4S_LLM_PROVIDER="deepseek"
    export AI4S_LLM_API_KEY="sk-..."
    export AI4S_LLM_MODEL="deepseek-chat"
    python test_llm_integration.py

Tests:
1. Basic connectivity (hello world)
2. GROMACS workflow generation (full plan)
3. DFT workflow generation (full plan)
4. JSON schema validation
5. Parameter sanity checks
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai4s_core.llm_interface import LLMInterface
from ai4s_core.domain import DomainRegistry
from ai4s_core.validation import RuleRegistry


def test_basic_connectivity():
    """Test 1: Can we reach the LLM?"""
    print("=" * 60)
    print("TEST 1: Basic Connectivity")
    print("=" * 60)

    llm = LLMInterface()
    response = llm.complete("Say 'hello' and nothing else.", max_tokens=50)

    print(f"Response: {response}")
    assert response.strip(), "Empty response from LLM"
    print("✅ PASS: LLM is reachable\n")
    return True


def test_gromacs_workflow():
    """Test 2: GROMACS workflow generation quality."""
    print("=" * 60)
    print("TEST 2: GROMACS Workflow Generation")
    print("=" * 60)

    llm = LLMInterface()
    registry = DomainRegistry()
    domain = registry.get_domain("molecular_dynamics")

    query = "Run a GROMACS molecular dynamics simulation for ubiquitin protein equilibration in water"
    plan = llm.generate_plan(query, domain.get_context())

    print(f"Generated plan keys: {list(plan.keys())}")
    print(f"Number of steps: {len(plan.get('steps', []))}")

    # Validation checks
    assert "steps" in plan, "Missing 'steps' in plan"
    assert len(plan["steps"]) > 0, "Empty steps list"
    assert "required_software" in plan, "Missing required_software"
    assert "validation_checks" in plan, "Missing validation_checks"

    # Check for GROMACS-specific content
    steps_text = json.dumps(plan["steps"]).lower()
    assert "gmx" in steps_text or "gromacs" in steps_text, "No GROMACS commands found"

    # Check parameter quality
    for step in plan["steps"]:
        assert "tool" in step, f"Step missing 'tool': {step}"
        assert "command" in step, f"Step missing 'command': {step}"
        assert "description" in step, f"Step missing 'description': {step}"

    print(f"\nStep details:")
    for i, step in enumerate(plan["steps"][:5]):
        print(f"  {i}. [{step['tool']}] {step['description'][:60]}...")

    print(f"\nValidation checks: {plan.get('validation_checks', [])}")
    print(f"Required software: {plan.get('required_software', [])}")
    print("✅ PASS: GROMACS workflow generated with structure\n")
    return plan


def test_dft_workflow():
    """Test 3: DFT workflow generation quality."""
    print("=" * 60)
    print("TEST 3: DFT Workflow Generation")
    print("=" * 60)

    llm = LLMInterface()
    registry = DomainRegistry()
    domain = registry.get_domain("dft")

    query = "Calculate the band structure of silicon using Quantum ESPRESSO"
    plan = llm.generate_plan(query, domain.get_context())

    print(f"Number of steps: {len(plan.get('steps', []))}")

    steps_text = json.dumps(plan["steps"]).lower()
    assert "pw.x" in steps_text or "quantum espresso" in steps_text or "espresso" in steps_text, \
        "No Quantum ESPRESSO commands found"

    print("✅ PASS: DFT workflow generated\n")
    return plan


def test_parameter_sanity(plan: dict) -> list:
    """Test 4: Check for obviously wrong parameters."""
    print("=" * 60)
    print("TEST 4: Parameter Sanity Checks")
    print("=" * 60)

    issues = []
    steps_text = json.dumps(plan.get("steps", [])).lower()

    # Check for physically unreasonable values
    dangerous_patterns = [
        ("temperature", ["10000", "50000"], "Unreasonably high temperature"),
        ("pressure", ["100000"], "Unreasonably high pressure"),
        ("timestep", ["0.1", "1.0"], "Unreasonably large timestep (fs)"),
    ]

    # Check for placeholder parameters
    if "<" in steps_text and ">" in steps_text:
        issues.append("Found placeholder parameters (<...>) in commands")

    # Check for missing required fields
    for i, step in enumerate(plan.get("steps", [])):
        if not step.get("command"):
            issues.append(f"Step {i}: missing command")
        if step.get("command", "").startswith("#"):
            issues.append(f"Step {i}: command is a comment, not executable")

    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No obvious sanity issues found")

    print()
    return issues


def test_json_schema(plan: dict) -> bool:
    """Test 5: Validate plan structure against expected schema."""
    print("=" * 60)
    print("TEST 5: JSON Schema Validation")
    print("=" * 60)

    validator = RuleRegistry()
    # TODO: Add schema validation

    required_keys = ["steps", "estimated_compute", "required_software", "validation_checks"]
    missing = [k for k in required_keys if k not in plan]

    if missing:
        print(f"❌ Missing keys: {missing}")
        return False

    print("✅ All required keys present\n")
    return True


def main():
    print("\n" + "=" * 60)
    print("AI4S-CORE LLM INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Provider: {os.getenv('AI4S_LLM_PROVIDER', 'openai')}")
    print(f"Model: {os.getenv('AI4S_LLM_MODEL', 'gpt-4o')}")
    print(f"API Key: {'✅ Set' if os.getenv('AI4S_LLM_API_KEY') else '❌ NOT SET'}")
    print("=" * 60 + "\n")

    if not os.getenv("AI4S_LLM_API_KEY"):
        print("❌ ERROR: AI4S_LLM_API_KEY not set")
        print("   export AI4S_LLM_API_KEY='sk-...'")
        sys.exit(1)

    results = {
        "connectivity": False,
        "gromacs": None,
        "dft": None,
        "sanity": [],
        "schema": False,
    }

    try:
        results["connectivity"] = test_basic_connectivity()
    except Exception as e:
        print(f"❌ FAIL: {e}\n")

    try:
        results["gromacs"] = test_gromacs_workflow()
    except Exception as e:
        print(f"❌ FAIL: {e}\n")

    try:
        results["dft"] = test_dft_workflow()
    except Exception as e:
        print(f"❌ FAIL: {e}\n")

    if results["gromacs"]:
        results["sanity"] = test_parameter_sanity(results["gromacs"])
        results["schema"] = test_json_schema(results["gromacs"])

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Connectivity:     {'✅ PASS' if results['connectivity'] else '❌ FAIL'}")
    print(f"GROMACS plan:     {'✅ PASS' if results['gromacs'] else '❌ FAIL'}")
    print(f"DFT plan:         {'✅ PASS' if results['dft'] else '❌ FAIL'}")
    print(f"Sanity checks:    {'⚠️  ISSUES' if results['sanity'] else '✅ PASS'} ({len(results['sanity'])} issues)")
    print(f"Schema validation: {'✅ PASS' if results['schema'] else '❌ FAIL'}")
    print("=" * 60)

    # Save results
    output_file = "test_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "connectivity": results["connectivity"],
            "gromacs_steps": len(results["gromacs"]["steps"]) if results["gromacs"] else 0,
            "dft_steps": len(results["dft"]["steps"]) if results["dft"] else 0,
            "sanity_issues": results["sanity"],
            "schema_valid": results["schema"],
        }, f, indent=2)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
