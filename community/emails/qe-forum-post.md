Subject: [Tool] ai4s-core — natural language interface for DFT calculations

Hi Quantum ESPRESSO community,

I'm building an open-source CLI tool that generates DFT and quantum chemistry workflows from plain English descriptions. It currently supports Quantum ESPRESSO for electronic structure calculations, with domain-specific validation that catches common input errors.

Example:
  $ ai4s plan "DFT calculation for silicon band structure using PBE functional with 8x8x8 k-grid" --format bash
  → Generates complete QE input: &CONTROL, &SYSTEM, &ELECTRONS, &CELL with validated parameters

The tool validates:
- K-grid density appropriateness for system size
- Energy cutoff convergence (checks ecutwfc vs. ecutrho ratio)
- Pseudopotential compatibility with element list
- Functional appropriateness for property (band structure vs. DOS vs. relaxation)
- Spin polarization settings for magnetic systems

It also supports VASP, GPAW, ABINIT for DFT, plus GROMACS (MD), ORCA (quantum chemistry), LAMMPS (materials), and bioinformatics.

Key feature for the QE community: the tool generates step-by-step workflows for multi-step calculations (relaxation → SCF → bands → DOS) with proper dependency ordering.

I'd love feedback from QE users. What input file parameters do you find most error-prone? What would help you set up complex multi-step calculations faster?

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
Docs: https://github.com/agent2agent-dev/ai4s-core/blob/main/README.md

Thanks,
Anbus
ai4s-core author
