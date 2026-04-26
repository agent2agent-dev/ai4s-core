ai4s-core: Natural Language → Scientific Computing Workflows

ai4s-core is an open-source Python CLI that turns plain English descriptions into validated, executable scientific computing pipelines. Think of it as a compiler for scientific ideas.

The problem: Researchers spend hours writing and debugging shell scripts for molecular dynamics, DFT calculations, and bioinformatics pipelines. The syntax is arcane, parameters are easy to get wrong, and a single typo in an input file wastes days of compute time.

What it does:
- Takes a natural language description like "simulate ubiquitin in water for 10ns with AMBER force field"
- Generates a structured workflow with proper commands, auxiliary files (MDP configs, input files), and error handling
- Validates scientific correctness: checks temperature ranges, energy cutoffs, timestep sanity, etc.
- Outputs as Python script, Bash script, or Snakemake workflow
- Executes in Docker containers with automatic fallback to local execution

Local LLM support (privacy-first):
- Works with llama.cpp, Ollama, vLLM — your research data never leaves your machine
- Validated with qwen3.6-35B-A3B-IQ4: generates correct GROMACS parameters and Quantum ESPRESSO input files
- Handles model output truncation with automatic fallback strategies

Example session:
  $ pip install ai4s-core
  $ ai4s plan "run a 10ns MD simulation of protein 1UBQ in TIP3P water"
  $ ai4s plan "..." --format bash --work-dir ./run1
  $ ai4s validate workflow.json

Current domains: Molecular Dynamics (GROMACS), DFT (Quantum ESPRESSO), Quantum Chemistry (ORCA), Bioinformatics (RNA-seq). Adding a new domain is ~50 lines of Python.

34 tests, MIT license, looking for contributors and early users in computational chemistry.

https://github.com/agent2agent-dev/ai4s-core
