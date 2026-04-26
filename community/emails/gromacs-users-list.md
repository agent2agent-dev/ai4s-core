Subject: [Tool] ai4s-core — natural language interface for MD/DFT/QC workflows

Hi GROMACS community,

I'm building an open-source CLI tool that generates scientific computing workflows from plain English descriptions. It currently supports GROMACS for molecular dynamics, with domain-specific validation that catches common setup errors before you waste compute time.

Example:
  $ ai4s plan "simulate ubiquitin in water for 10ns using AMBER99SB-ILDN" --format bash
  → Generates complete GROMACS pipeline: topology prep, solvation, energy minimization, 
    equilibration (NVT+NPT), production run, with all input files

The tool validates:
- Force field compatibility (protein vs. ligand vs. membrane)
- Temperature ranges (10K-1000K sanity checks)
- Equilibration completeness (NVT before NPT before production)
- Simulation length appropriateness

It also supports Quantum ESPRESSO (DFT), ORCA (quantum chemistry), LAMMPS (materials), and bioinformatics pipelines.

I'd love feedback from people who actually use these tools daily. What workflow steps do you find most tedious to set up manually? What errors do you wish were caught before you submitted the job?

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
Docs: https://github.com/agent2agent-dev/ai4s-core/blob/main/README.md

Thanks,
Anbus
ai4s-core author
