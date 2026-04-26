Turn your scientific ideas into executable workflows with natural language.

ai4s-core is an open-source CLI that translates plain English into validated, ready-to-run scientific computing pipelines. No more memorizing GROMACS flags or Quantum ESPRESSO input syntax.

Key features:
- Natural language → structured workflow (JSON/Python/Bash/Snakemake)
- Built-in validation engine checks scientific correctness (temperature ranges, energy cutoff sanity, etc.)
- Execution engine runs workflows in Docker containers or locally
- Works with local LLMs — your data never leaves your machine
- 4 domains ready: Molecular Dynamics (GROMACS), DFT (Quantum ESPRESSO), Quantum Chemistry (ORCA), Bioinformatics (RNA-seq)

Example:
  $ ai4s plan "simulate ubiquitin in water for 10ns with AMBER force field" --format bash
  → Generates a 14-step GROMACS pipeline with MDP files, error handling, and validation checks

Local LLM setup (privacy-friendly):
  $ export AI4S_LLM_PROVIDER=vllm
  $ export AI4S_LLM_BASE_URL=http://localhost:39527
  $ export AI4S_LLM_MODEL=qwen3.6-35B-A3B-IQ4
  $ ai4s plan "..." --format python

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT

Looking for early users in computational chemistry / molecular simulation. If you or your lab spends too much time writing shell scripts for MD/DFT, I'd love to hear from you.
