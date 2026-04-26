Title: ai4s-core — Natural language workflows for MD, DFT, and bioinformatics

I built a CLI tool that turns plain English descriptions into validated, executable scientific computing pipelines. It's open-source, works with local LLMs, and currently supports GROMACS, Quantum ESPRESSO, ORCA, and RNA-seq.

**The problem I was trying to solve:**
I spend too much time writing shell scripts for molecular dynamics and DFT calculations. Memorizing GROMACS MDP parameters, checking if my energy cutoff is reasonable, making sure I didn't typo the temperature — it's tedious and error-prone. One wrong parameter and you waste days of compute time.

**What it does:**
```bash
$ ai4s plan "simulate ubiquitin in water for 10ns with AMBER99SB-ILDN"
```
Generates a 14-step GROMACS workflow with proper MDP files, error handling, and validation checks. Outputs as Bash, Python, or Snakemake.

**Key features:**
- Natural language → structured workflow (with auxiliary input files)
- Built-in validation: checks temperature ranges, energy cutoffs, timestep sanity
- Execution engine: Docker containers or local execution
- Local LLM support (llama.cpp, vLLM, Ollama) — data never leaves your machine
- Handles model output truncation with fallback strategies

**Validation example:**
```bash
$ ai4s validate workflow.json
✓ Step 1: temperature 300K within valid range [0.1, 1000]
✓ Step 2: energy cutoff 400 Ry within valid range [10, 1000]
```

**Current status:** 34 tests passing, MIT license, looking for early users and contributors. The core is solid; next steps are HPC integration (Slurm/PBS) and more domains (LAMMPS, WRF).

**Repo:** https://github.com/agent2agent-dev/ai4s-core

If you work in computational chemistry or molecular simulation — what workflow tools do you use now, and what frustrates you about them? I'd genuinely love to hear.
