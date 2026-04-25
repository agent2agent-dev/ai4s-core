"""
Example: Protein MD workflow generation.

This demonstrates the full pipeline from natural language query
to executable GROMACS workflow.
"""

from ai4s_core import WorkflowOrchestrator


def main():
    orch = WorkflowOrchestrator()

    # A realistic research query
    query = (
        "Simulate the protein 1UBQ (ubiquitin) in a cubic water box "
        "with 0.15 M NaCl at 300 K for 100 ns using the AMBER99SB-ILDN force field. "
        "Use GROMACS with a 2 fs timestep and save coordinates every 10 ps."
    )

    print(f"Query: {query}\n")

    # Generate plan
    plan = orch.plan(query, use_mock=True)

    print(f"Domain: {plan.domain}")
    print(f"Steps: {len(plan.steps)}")
    print(f"Estimated compute: {plan.estimated_compute or 'N/A'}")
    print(f"Required software: {', '.join(plan.required_software)}")
    print()

    # Show steps
    for i, step in enumerate(plan.steps):
        print(f"Step {i}: [{step.tool}] {step.description}")
        print(f"  Command: {step.command}")
        if step.dependencies:
            print(f"  Dependencies: {step.dependencies}")
        print()

    # Export to Python script
    script = orch.to_script(plan, format="python")
    with open("run_ubiquitin_md.py", "w") as f:
        f.write(script)
    print("Python script written to: run_ubiquitin_md.py")

    # Export to bash script
    bash_script = orch.to_script(plan, format="bash")
    with open("run_ubiquitin_md.sh", "w") as f:
        f.write(bash_script)
    print("Bash script written to: run_ubiquitin_md.sh")

    # Export to Snakemake
    smk_script = orch.to_script(plan, format="snakemake")
    with open("Snakefile", "w") as f:
        f.write(smk_script)
    print("Snakemake workflow written to: Snakefile")


if __name__ == "__main__":
    main()
