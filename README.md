# ai4s-core

> Turn "Run a protein simulation" into a complete, executable workflow in seconds.

**ai4s-core** is an open-source framework that converts natural language scientific queries into structured, validated computational workflows.

No more spending 20+ hours learning Snakemake or Nextflow syntax. Describe your experiment in plain English, get a ready-to-run workflow.

---

## Why?

If you've ever:
- Spent a day debugging a Snakemake pipeline only to realize it was a missing comma
- Copied and pasted bash scripts from Stack Overflow without understanding them
- Wanted to run a molecular dynamics simulation but got stuck on workflow setup

...this is for you.

---

## Quick Start

### CLI (fastest)

```bash
# Install
pip install ai4s-core

# Set your LLM API key — supports OpenAI, DeepSeek, Anthropic, or local via Ollama
export AI4S_LLM_PROVIDER="openai"
export AI4S_LLM_API_KEY="***"

# Or use DeepSeek (cheaper, no proxy needed in China)
export AI4S_LLM_PROVIDER="deepseek"
export AI4S_LLM_API_KEY="***"
export AI4S_LLM_MODEL="deepseek-chat"

# Or use a local model (privacy-first, zero data upload)
export AI4S_LLM_PROVIDER="vllm"
export AI4S_LLM_BASE_URL="http://localhost:8000/v1"
export AI4S_LLM_MODEL="qwen3.6-35B-A3B-IQ4"

# Generate a workflow
ai4s plan "Run a GROMACS molecular dynamics simulation for protein equilibration"

# Output: complete Python script with all steps, dependencies, validation checks,
# and auxiliary files (MDP input files, etc.) auto-generated
```

### Python API

```python
from ai4s_core import WorkflowOrchestrator

orch = WorkflowOrchestrator()

# Basic usage
plan = orch.plan("Calculate band structure of silicon using DFT")

# For limited-output models (e.g., local 35B quantized), use step-by-step strategy
plan = orch.plan(
    "Calculate band structure of silicon using DFT",
    strategy="step_by_step"  # Two-phase: outline + per-step expansion
)

# Export to your preferred format
script = orch.to_script(plan, format="python")  # or "bash", "snakemake"
print(script)
```

### No API key? Use mock mode for demo

```bash
# Demo with pre-built realistic workflows (no LLM call, no API key)
ai4s plan "Simulate ubiquitin in water" --mock

# Available mock domains: molecular_dynamics, density_functional_theory,
# quantum_chemistry, bioinformatics
ai4s plan "Run RNA-seq differential expression" --mock
```

---

## What You Get

| Feature | Description |
|---------|-------------|
| **Natural Language Input** | Describe your experiment in plain English |
| **Domain Detection** | Auto-detects MD, DFT, bioinformatics, quantum chemistry |
| **Step-by-Step Workflows** | Complete with tools, commands, inputs, outputs |
| **Dependency Graph** | Automatic step ordering and parallelization hints |
| **Validation Checks** | Built-in sanity checks (energy convergence, temperature stability, etc.) |
| **Auxiliary File Generation** | Auto-creates input files (MDP, Quantum ESPRESSO .in, ORCA input, R scripts) |
| **Error Handling** | Per-step fallback strategies and output verification |
| **Multi-Format Export** | Python, Bash, or Snakemake |
| **Mock Mode** | Demo without API keys |
| **Local LLM Support** | Works with Ollama, vLLM, llama.cpp — no data leaves your machine |

---

## Supported LLM Providers

| Provider | Setup | Best For |
|----------|-------|----------|
| **OpenAI** | `export AI4S_LLM_PROVIDER="openai"` | Best quality, highest cost |
| **DeepSeek** | `export AI4S_LLM_PROVIDER="deepseek"` | Cheapest, China-friendly, great for science |
| **Anthropic** | `export AI4S_LLM_PROVIDER="anthropic"` | Long context, careful reasoning |
| **Ollama** | `export AI4S_LLM_PROVIDER="ollama"` | Free, local, privacy-first |
| **vLLM** | `export AI4S_LLM_PROVIDER="vllm"` | Self-hosted, high throughput |

All providers use the same `AI4S_LLM_API_KEY` env var. DeepSeek and Ollama use OpenAI-compatible APIs internally.

## Supported Scientific Domains

- **Molecular Dynamics**: GROMACS, AMBER, OpenMM, LAMMPS, NAMD
- **DFT / Electronic Structure**: VASP, Quantum ESPRESSO, GPAW, ABINIT
- **Bioinformatics**: RNA-seq, ATAC-seq, phylogenetics, genome assembly
- **Quantum Chemistry**: ORCA, Gaussian, PySCF, Psi4

---

## Example Output

Input:
```bash
ai4s plan "Run a GROMACS MD simulation for protein equilibration"
```

Output (auto-generated Python script):
```python
#!/usr/bin/env python3
"""Auto-generated workflow: Run a GROMACS MD simulation for protein equilibration"""

# Steps:
# 1. Download protein structure from PDB
# 2. Process structure and generate topology
# 3. Define simulation box
# 4. Add water molecules
# 5. Add ions to neutralize
# 6. Energy minimization
# 7. NVT equilibration
# 8. NPT equilibration
# 9. Production MD run
# 10. Validation: check energy, temperature, pressure convergence

def run_step(cmd, desc):
    print(f"[Running] {desc}")
    print(f"  Command: {cmd}")
    # subprocess.run(cmd, shell=True, check=True)

# ... (full script generated)
```

---

## Architecture

```
ai4s-core/
├── cli.py              # Command-line interface
├── orchestrator.py     # Core workflow generation engine
├── llm_interface.py    # Abstraction for OpenAI/Anthropic/Ollama/vLLM
├── domain.py           # Scientific domain registry and context
├── validation.py       # Workflow validation and sanity checks
└── tests/              # Test suite
```

---

## Development

```bash
git clone https://github.com/anbus/ai4s-core.git
cd ai4s-core
pip install -e ".[dev]"
pytest
```

---

## Architecture

```
ai4s-core/
├── cli.py              # Command-line interface
├── orchestrator.py     # Core workflow generation engine
│   ├── plan()          # Main entry: classify domain, generate plan, validate
│   ├── _mock_plan()    # Zero-dependency demo mode (4 domains)
│   ├── to_script()     # Export to Python/Bash/Snakemake
│   └── _step_to_dict() # Clean JSON serialization (no repr() artifacts)
├── llm_interface.py   # Abstraction for OpenAI/Anthropic/Ollama/vLLM/DeepSeek
│   ├── generate_plan()          # Single-shot generation (fast, may truncate)
│   ├── generate_plan_step_by_step()  # Two-phase: outline + per-step expansion
│   └── _extract_json()  # Robust JSON parsing with brace-depth fallback
├── domain.py           # Scientific domain registry and context
├── validation.py       # Workflow validation and sanity checks
└── tests/              # Test suite (13 tests, all passing)
```

## Local LLM Setup (Privacy-First)

For users who cannot or will not upload research data to cloud APIs:

```bash
# 1. Install llama.cpp or Ollama
# 2. Download a science-capable model (e.g., Qwen3.5-32B, DeepSeek-R1-Distill)

# 3. Configure ai4s-core to use your local endpoint
export AI4S_LLM_PROVIDER="vllm"
export AI4S_LLM_BASE_URL="http://localhost:8000/v1"
export AI4S_LLM_MODEL="your-model-name"
export AI4S_LLM_API_KEY="dummy"  # required but not validated by local servers

# 4. For limited-output models, use step-by-step strategy
python -c "
from ai4s_core import WorkflowOrchestrator
orch = WorkflowOrchestrator()
plan = orch.plan('Run MD simulation of lysozyme', strategy='step_by_step')
print(orch.to_script(plan, format='python'))
"
```

**Verified**: qwen3.6-35B-A3B-IQ4 (llama.cpp) successfully generates correct GROMACS and Quantum ESPRESSO workflows.

## Roadmap

- [x] Core workflow generation (MD, DFT, QC, Bioinformatics)
- [x] Local LLM support (Ollama, vLLM, llama.cpp)
- [x] Auxiliary file generation (MDP, input files, scripts)
- [x] Error handling and validation
- [x] Step-by-step generation for limited-output models
- [ ] Real execution engine (run generated scripts, not just generate)
- [ ] Web UI for non-CLI users
- [ ] Hosted execution environment (run workflows in the cloud)
- [ ] Team collaboration features
- [ ] Verified workflow templates from domain experts

---

## License

MIT — free for academic and commercial use.

---

**Made by [Anbus](https://github.com/anbus) | Independent developer, full-time AI for Science.**
