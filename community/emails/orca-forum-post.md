Subject: [Tool] ai4s-core — natural language interface for ORCA workflows

Hi ORCA community,

I'm building an open-source CLI tool that generates quantum chemistry workflows from plain English descriptions. It currently supports ORCA for a wide range of calculations, with domain-specific validation that catches common input errors.

Example:
  $ ai4s plan "optimize water molecule with B3LYP/6-31G* using ORCA" --format bash
  → Generates complete ORCA input: method, basis set, geometry optimization flags, 
    convergence criteria, with validation

The tool validates:
- Basis set compatibility with method (e.g., DFT vs. MP2 vs. CCSD(T))
- Method appropriateness for system size (HF for small, DFT for medium, MP2 for correlated)
- Convergence criteria matching calculation type (tighter for frequencies vs. geometry)
- Memory and parallelization settings for job size

It also supports Gaussian, PySCF, Psi4 for quantum chemistry, plus Quantum ESPRESSO (DFT), GROMACS (MD), LAMMPS (materials), and bioinformatics.

Key feature for the ORCA community: the tool handles multi-step workflows (geometry optimization → frequency → NBO → excited states) with proper checkpoint file management.

I'd love feedback from ORCA users. What calculation types do you run most frequently? What input file setup steps take the most time?

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
Docs: https://github.com/agent2agent-dev/ai4s-core/blob/main/README.md

Thanks,
Anbus
ai4s-core author
