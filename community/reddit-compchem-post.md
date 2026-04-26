Title: ai4s-core — Natural language → GROMACS/QE workflows, validated and executable

I built a tool that turns plain English into validated computational chemistry workflows. It's open-source, privacy-first (works with local LLMs), and I'd love feedback from people who actually run MD and DFT.

**What it does:**
```bash
$ ai4s plan "run a DFT calculation on silicon using PBE functional with 40 Ry cutoff"
```

Generates a 7-step Quantum ESPRESSO workflow:
1. SCF calculation (pw.x with Si.scf.in)
2. Bands calculation (pw.x with Si.bands.in)
3. DOS calculation (dos.x)
4. Plotband (plotband.x)

With auxiliary input files included, error handling per step, and scientific correctness validation.

**Validation checks:**
- Energy cutoff sanity (e.g., 40 Ry for PBE is flagged as "low" — suggests 50-80 Ry)
- Temperature ranges for MD
- Timestep compatibility with force field
- Required file existence checks

**Local LLM support:**
Tested with qwen3.6-35B-A3B-IQ4 via llama.cpp. Generates correct GROMACS parameters and QE input files. Handles output truncation with automatic fallback to outline mode.

**Why local LLM matters:**
Your research data never leaves your machine. No API keys, no cloud dependency, no data leakage concerns. Especially important for unpublished research and proprietary structures.

**Current domains:**
- Molecular Dynamics (GROMACS: pdb2gmx → solvate → genion → EM → NVT → NPT → MD)
- DFT (Quantum ESPRESSO: SCF → bands → DOS → post-processing)
- Quantum Chemistry (ORCA: geometry optimization → frequency → single point)
- Bioinformatics (RNA-seq: fastqc → trim → align → count → DESeq2)

**Repo:** https://github.com/agent2agent-dev/ai4s-core (MIT license, 34 tests)

**What I'd love to know:**
1. What's your current workflow for setting up a new MD/DFT calculation? (shell scripts? Jupyter? workflow managers?)
2. What parameters do you most often get wrong or have to look up?
3. Would you trust an LLM-generated input file if it had built-in validation rules?

Any feedback appreciated — this is early stage and I want to build something actually useful, not just cool.
