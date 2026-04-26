# ai4s-core

> Turn "Run a protein simulation" into a complete, executable workflow in seconds.

**ai4s-core** converts natural language scientific queries into structured, validated computational workflows. No more spending 20+ hours learning Snakemake syntax — describe your experiment in plain English, get a ready-to-run workflow.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-34%2F34-brightgreen.svg)]()

---

## 30-Second Demo

```bash
# No API key needed for demo
pip install ai4s-core
ai4s plan "Simulate ubiquitin in water" --mock
# Output: complete 14-step GROMACS workflow with validation checks
```

**With LLM** (OpenAI/DeepSeek/Anthropic/local):
```bash
export AI4S_LLM_PROVIDER="deepseek"
export AI4S_LLM_API_KEY="***"
ai4s plan "Run a GROMACS MD simulation for protein equilibration"
# Output: Python script with all steps, dependencies, validation checks
```

---

## Why ai4s-core?

| Problem | Traditional Way | With ai4s-core |
|---------|----------------|----------------|
| Run MD simulation | 20h learning GROMACS + writing scripts | 30 seconds, natural language |
| Set up DFT calculation | Manual input file editing, trial-and-error | Auto-generated Quantum ESPRESSO inputs |
| Validate workflow | Eyeballing outputs, missing errors | Built-in sanity checks (energy, temperature, pressure) |
| Reproduce colleague's work | "Ask them for their scripts" | Share the natural language query |

---

## Quick Start

### Installation

```bash
pip install ai4s-core
```

### Option 1: Mock Mode (No API Key)

```bash
# Demo with pre-built realistic workflows
ai4s plan "Simulate ubiquitin in water" --mock
ai4s plan "Calculate band structure of silicon" --mock
ai4s plan "Run RNA-seq differential expression" --mock
ai4s plan "Optimize geometry of caffeine molecule" --mock

# List available domains
ai4s plan --list-domains
```

### Option 2: With LLM (Cloud or Local)

```bash
# DeepSeek (cheapest, China-friendly)
export AI4S_LLM_PROVIDER="deepseek"
export AI4S_LLM_API_KEY="***"

# Or local LLM (privacy-first, zero data upload)
export AI4S_LLM_PROVIDER="vllm"
export AI4S_LLM_BASE_URL="http://localhost:8000/v1"
export AI4S_LLM_MODEL="qwen3.6-35B-A3B-IQ4"

# Generate workflow
ai4s plan "Run a GROMACS molecular dynamics simulation for protein equilibration"
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

---

## Features

| Feature | Description |
|---------|-------------|
| **Natural Language Input** | Describe your experiment in plain English |
| **5 Scientific Domains** | MD, DFT, Bioinformatics, Quantum Chemistry, Materials Simulation |
| **Step-by-Step Workflows** | Complete with tools, commands, inputs, outputs |
| **Dependency Graph** | Automatic step ordering and parallelization hints |
| **Validation Checks** | Built-in sanity checks (energy convergence, temperature stability, etc.) |
| **Auxiliary File Generation** | Auto-creates input files (MDP, Quantum ESPRESSO .in, ORCA input, R scripts) |
| **Error Handling** | Per-step fallback strategies and output verification |
| **Multi-Format Export** | Python, Bash, or Snakemake |
| **Mock Mode** | Demo without API keys |
| **Local LLM Support** | Works with Ollama, vLLM, llama.cpp — no data leaves your machine |

---

## Supported Scientific Domains

- **Molecular Dynamics**: GROMACS, AMBER, OpenMM, LAMMPS, NAMD
- **DFT / Electronic Structure**: VASP, Quantum ESPRESSO, GPAW, ABINIT
- **Bioinformatics**: RNA-seq, ATAC-seq, phylogenetics, genome assembly
- **Quantum Chemistry**: ORCA, Gaussian, PySCF, Psi4
- **Materials Simulation**: LAMMPS (Aluminum FCC, defect modeling, etc.)

---

## Architecture

```
User Query (natural language)
    ↓
[Domain Classifier] → Detects scientific field (MD/DFT/Bioinfo/QC/Materials)
    ↓
[LLM Interface] → Generates structured workflow plan
    ↓
[Validation Engine] → Sanity checks (parameters, dependencies, convergence)
    ↓
[Script Exporter] → Python / Bash / Snakemake
    ↓
Executable workflow + auxiliary files
```

### Code Structure

```
ai4s-core/
├── cli.py              # Command-line interface
├── orchestrator.py     # Core workflow generation engine
│   ├── plan()          # Main entry: classify domain, generate plan, validate
│   ├── _mock_plan()    # Zero-dependency demo mode (5 domains)
│   ├── to_script()     # Export to Python/Bash/Snakemake
│   └── _step_to_dict() # Clean JSON serialization
├── llm_interface.py   # Abstraction for OpenAI/Anthropic/Ollama/vLLM/DeepSeek
│   ├── generate_plan()          # Single-shot generation
│   ├── generate_plan_step_by_step()  # Two-phase for limited-output models
│   └── _extract_json()  # Robust JSON parsing with brace-depth fallback
├── domain.py           # Scientific domain registry and context
├── validation.py       # Workflow validation and sanity checks
└── tests/              # Test suite (34 tests, all passing)
```

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

---

## Local LLM Setup (Privacy-First)

For users who cannot or will not upload research data to cloud APIs:

```bash
# 1. Install llama.cpp or Ollama
# 2. Download a science-capable model (e.g., Qwen3.5-32B, DeepSeek-R1-Distill)

# 3. Configure ai4s-core to use your local endpoint
export AI4S_LLM_PROVIDER="vllm"
export AI4S_LLM_BASE_URL="http://localhost:8000/v1"
export AI4S_LLM_MODEL="your-model-name"
export AI4S_LLM_API_KEY="***"  # required but not validated by local servers

# 4. For limited-output models, use step-by-step strategy
python -c "
from ai4s_core import WorkflowOrchestrator
orch = WorkflowOrchestrator()
plan = orch.plan('Run MD simulation of lysozyme', strategy='step_by_step')
print(orch.to_script(plan, format='python'))
"
```

**Verified**: qwen3.6-35B-A3B-IQ4 (llama.cpp) successfully generates correct GROMACS and Quantum ESPRESSO workflows.

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

## Verification

New users can verify the installation in 5 seconds:

```bash
python3 scripts/mvv.py
# Output: 5 checks, all passing, total time ~0.1s
```

---

## Development

```bash
git clone https://github.com/agent2agent-dev/ai4s-core.git
cd ai4s-core
pip install -e ".[dev]"
pytest  # 34 tests, all passing
```

---

## Roadmap

- [x] Core workflow generation (MD, DFT, QC, Bioinformatics)
- [x] Materials simulation (LAMMPS)
- [x] Local LLM support (Ollama, vLLM, llama.cpp)
- [x] Auxiliary file generation (MDP, input files, scripts)
- [x] Error handling and validation
- [x] Step-by-step generation for limited-output models
- [x] Real execution engine (Docker + local subprocess)
- [ ] Web UI for non-CLI users
- [ ] Hosted execution environment (run workflows in the cloud)
- [ ] Team collaboration features
- [ ] Verified workflow templates from domain experts

---

## License

MIT — free for academic and commercial use.

---

**Made by [Anbus](https://github.com/anbus) | Independent developer, full-time AI for Science.**

Questions? Open a [GitHub Discussion](https://github.com/agent2agent-dev/ai4s-core/discussions) or check the [Contributing Guide](community/CONTRIBUTING.md).
