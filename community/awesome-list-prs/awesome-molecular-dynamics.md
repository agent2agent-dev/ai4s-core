## Add ai4s-core to Awesome Molecular Dynamics

**Name**: ai4s-core
**Link**: https://github.com/agent2agent-dev/ai4s-core
**Description**: Natural language workflow generator for molecular dynamics simulations. Generate validated GROMACS, LAMMPS, AMBER, OpenMM, and NAMD input files from plain English descriptions.

**Why it fits this list:**
ai4s-core specifically targets the MD community by automating the tedious setup phase of simulations. It generates complete MD workflows — from topology preparation to production runs — with domain-specific validation that catches common mistakes (temperature ranges, force field compatibility, equilibration completeness).

**Example:**
```bash
$ ai4s plan "simulate ubiquitin in water for 10ns using AMBER99SB-ILDN" --format bash
→ Generates: topology prep, solvation, energy minimization, equilibration, production
```

**Key MD features:**
- Supports GROMACS, LAMMPS, AMBER, OpenMM, NAMD
- Validates force field compatibility, temperature ranges (10K-1000K), equilibration completeness
- Generates step-by-step workflows with dependency DAG
- Local LLM support — no data leaves your machine
- MIT license, 44 tests passing

**License**: MIT
**Language**: Python

---

*This PR adds ai4s-core to the awesome-molecular-dynamics list. Happy to adjust placement or description based on maintainer feedback.*
