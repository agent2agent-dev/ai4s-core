"""
Example: DFT band structure calculation for silicon.

Demonstrates the full pipeline for density functional theory workflows
using Quantum ESPRESSO.
"""

from ai4s_core import WorkflowOrchestrator


def main():
    orch = WorkflowOrchestrator()

    query = (
        "Calculate the electronic band structure of silicon (diamond cubic) "
        "using DFT with the PBE exchange-correlation functional. "
        "Use a plane-wave cutoff of 40 Ry and a 8x8x8 k-point grid for SCF. "
        "Plot the band structure along the Gamma-X-W-L-Gamma high-symmetry path."
    )

    print(f"Query: {query}\n")

    plan = orch.plan(query, domain_hint="density_functional_theory", use_mock=True)

    print(f"Domain: {plan.domain}")
    print(f"Steps: {len(plan.steps)}")
    print(f"Estimated compute: {plan.estimated_compute or 'N/A'}")
    print(f"Required software: {', '.join(plan.required_software)}")
    print()

    for i, step in enumerate(plan.steps):
        print(f"Step {i}: [{step.tool}] {step.description}")
        print(f"  Command: {step.command}")
        if step.dependencies:
            print(f"  Dependencies: {step.dependencies}")
        print()

    script = orch.to_script(plan, format="python")
    with open("run_si_dft.py", "w") as f:
        f.write(script)
    print("Python script written to: run_si_dft.py")

    bash_script = orch.to_script(plan, format="bash")
    with open("run_si_dft.sh", "w") as f:
        f.write(bash_script)
    print("Bash script written to: run_si_dft.sh")

    smk_script = orch.to_script(plan, format="snakemake")
    with open("Snakefile_dft", "w") as f:
        f.write(smk_script)
    print("Snakemake workflow written to: Snakefile_dft")


if __name__ == "__main__":
    main()
