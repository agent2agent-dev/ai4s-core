#!/usr/bin/env python3
"""
ai4s CLI: command-line interface for AI4S workflow generation.

Usage:
    ai4s "simulate a protein in water for 100 ns"
    ai4s plan "calculate band structure of silicon" --domain dft --format snakemake
    ai4s list-domains
"""

import argparse
import json
import sys
from pathlib import Path

from ai4s_core.orchestrator import WorkflowOrchestrator
from ai4s_core.domain import DomainRegistry
from ai4s_core.llm_interface import LLMInterface


def cmd_plan(args: argparse.Namespace) -> int:
    """Generate a workflow plan from a natural language query."""
    orch = WorkflowOrchestrator(
        llm=LLMInterface(),
        domain_registry=DomainRegistry(),
    )

    print(f"Query: {args.query}", file=sys.stderr)
    if args.domain:
        print(f"Domain hint: {args.domain}", file=sys.stderr)

    plan = orch.plan(args.query, domain_hint=args.domain, use_mock=args.mock)

    print(f"Detected domain: {plan.domain}", file=sys.stderr)
    print(f"Steps: {len(plan.steps)}", file=sys.stderr)
    if plan.estimated_compute:
        print(f"Estimated compute: {plan.estimated_compute}", file=sys.stderr)

    if args.json:
        output = {
            "query": plan.query,
            "domain": plan.domain,
            "steps": [
                {
                    "tool": s.tool,
                    "command": s.command,
                    "inputs": s.inputs,
                    "outputs": s.outputs,
                    "dependencies": s.dependencies,
                    "description": s.description,
                }
                for s in plan.steps
            ],
            "estimated_compute": plan.estimated_compute,
            "required_software": plan.required_software,
            "validation_checks": plan.validation_checks,
        }
        print(json.dumps(output, indent=2))
    else:
        script = orch.to_script(plan, format=args.format)
        if args.output:
            Path(args.output).write_text(script)
            print(f"Script written to: {args.output}", file=sys.stderr)
        else:
            print(script)

    return 0


def cmd_list_domains(args: argparse.Namespace) -> int:
    """List all supported scientific domains."""
    reg = DomainRegistry()
    for name in reg.list_domains():
        spec = reg.get(name)
        if spec:
            print(f"{name}: {spec.description}")
            print(f"  Tools: {', '.join(spec.common_tools[:5])}...")
            print()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a workflow plan file."""
    data = json.loads(Path(args.file).read_text())
    # Basic validation
    required_keys = {"query", "domain", "steps"}
    missing = required_keys - set(data.keys())
    if missing:
        print(f"Missing keys: {missing}", file=sys.stderr)
        return 1

    for i, step in enumerate(data.get("steps", [])):
        if "tool" not in step:
            print(f"Step {i} missing 'tool'", file=sys.stderr)
            return 1
        if "command" not in step:
            print(f"Step {i} missing 'command'", file=sys.stderr)
            return 1

    print("Workflow plan is valid.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ai4s",
        description="AI for Science workflow generator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # plan command
    plan_parser = subparsers.add_parser("plan", help="Generate workflow from query")
    plan_parser.add_argument("query", help="Natural language research query")
    plan_parser.add_argument("--domain", help="Force a specific domain")
    plan_parser.add_argument(
        "--format",
        choices=["python", "bash", "snakemake"],
        default="python",
        help="Output script format",
    )
    plan_parser.add_argument("--output", "-o", help="Output file path")
    plan_parser.add_argument("--json", action="store_true", help="Output raw JSON plan")
    plan_parser.add_argument("--mock", action="store_true", help="Use mock LLM for demo (no API key needed)")
    plan_parser.set_defaults(func=cmd_plan)

    # list-domains command
    list_parser = subparsers.add_parser("list-domains", help="List supported domains")
    list_parser.set_defaults(func=cmd_list_domains)

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a workflow JSON file")
    validate_parser.add_argument("file", help="Path to workflow JSON file")
    validate_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
