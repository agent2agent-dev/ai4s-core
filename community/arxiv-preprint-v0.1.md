# arXiv Preprint: ai4s-core

## Metadata
- **Title**: ai4s-core: Natural Language Interface for Scientific Computing Workflows
- **Authors**: Anbus (agent2agent-dev)
- **Categories**: cs.SE (Software Engineering), cs.AI (Artificial Intelligence)
- **Keywords**: scientific computing, natural language processing, workflow automation, molecular dynamics, density functional theory, quantum chemistry, bioinformatics, large language models
- **Length**: 4-6 pages
- **Repository**: https://github.com/agent2agent-dev/ai4s-core
- **License**: MIT

---

## Abstract

Scientific computing workflows require expertise in domain-specific software with complex input syntax, creating a steep learning curve for researchers and frequent wasted compute from parameter errors. We present ai4s-core, an open-source command-line interface that translates natural language descriptions into validated, executable scientific computing pipelines. The system combines LLM-based workflow generation with a multi-layer validation engine that checks scientific correctness at structural, domain-rule, and execution-simulation levels. It supports local LLM deployment via llama.cpp, Ollama, or vLLM for privacy-sensitive research data. We demonstrate the system on five scientific domains: molecular dynamics (GROMACS, AMBER, OpenMM, LAMMPS, NAMD), density functional theory (Quantum ESPRESSO, VASP, GPAW, ABINIT), quantum chemistry (ORCA, Gaussian, PySCF, Psi4), bioinformatics (RNA-seq, ATAC-seq, phylogenetics, genome assembly), and materials simulation (LAMMPS). The tool includes 44 unit tests covering workflow generation, validation, and execution. ai4s-core is available under MIT license at https://github.com/agent2agent-dev/ai4s-core.

---

## 1. Introduction

### 1.1 Problem Statement

Scientific computing software—such as GROMACS for molecular dynamics, Quantum ESPRESSO for density functional theory, and ORCA for quantum chemistry—requires researchers to master arcane input syntax, understand implicit file dependencies, and navigate parameter spaces with physical constraints. A single incorrect parameter (e.g., temperature below 0.1 K, energy cutoff below 10 Ry) can produce meaningless results or waste hours of cluster compute time.

The learning curve is particularly steep for:
- Graduate students entering computational research
- Experimentalists seeking to validate hypotheses with simulations
- Interdisciplinary researchers crossing domain boundaries

### 1.2 Existing Solutions and Their Limitations

**Workflow managers** (Snakemake, Nextflow, Galaxy) provide powerful pipeline orchestration but require programming expertise. They do not generate domain-specific input files from high-level intent.

**GUI tools** (VMD, Avogadro, Maestro) lower the barrier for specific tasks but lack flexibility for custom workflows and do not scale to batch processing or HPC environments.

**AI coding assistants** (GitHub Copilot, Claude Code) can suggest code snippets but lack domain-specific scientific correctness validation and do not understand implicit physical constraints.

### 1.3 Contribution

ai4s-core bridges the gap between natural language research intent and executable domain-specific workflows through three contributions:

1. **Natural language workflow generation**: A provider-agnostic LLM interface that converts plain English descriptions into structured workflow plans with per-step commands, file dependencies, and parameters.

2. **Scientific correctness validation engine**: A three-layer validation system (structural, domain-rule, execution-simulation) that catches errors before compute resources are consumed.

3. **Local LLM support**: Full compatibility with locally deployed models (llama.cpp, Ollama, vLLM) for privacy-sensitive research data, with automatic fallback strategies for limited-output models.

---

## 2. System Architecture

### 2.1 Overview

The system follows a four-stage pipeline:

```
Natural Language Query
        ↓
[LLM Interface] → Workflow Plan (JSON)
        ↓
[Validation Engine] → Validated Plan / Error Report
        ↓
[Export Engine] → Bash / Python / Snakemake / JSON
        ↓
[Execution Engine] → Docker / Local Subprocess / Dry-Run
```

### 2.2 LLM Interface

The LLM interface is provider-agnostic, supporting:
- Cloud APIs: OpenAI GPT-4, Anthropic Claude, DeepSeek
- Local deployment: llama.cpp, Ollama, vLLM

For models with limited output length (common with locally quantized models), the system employs a two-phase generation strategy:
1. **Outline phase**: Generate workflow metadata (domain, software, number of steps)
2. **Expansion phase**: Generate each step individually, using the outline as context

This approach successfully generates complex workflows (e.g., 14-step GROMACS protein simulation with 4 MDP parameter files) on models with 4K-8K output limits.

### 2.3 Validation Engine

The validation engine operates at three levels:

**L1 — Structural Validation**: Schema checking for required fields (step IDs, commands, file paths), type validation (numeric parameters), and dependency graph completeness (no orphaned inputs).

**L2 — Domain Rule Validation**: Domain-specific physical constraints enforced via a rule registry:
- Molecular Dynamics: temperature ∈ [0.1, 1000] K, timestep-force field compatibility (e.g., AMBER99SB-ILDN requires fs-scale timestep), energy minimization must precede production run
- DFT: energy cutoff ∈ [10, 1000] Ry, k-point grid density ≥ 0.02 Å⁻¹, pseudopotential consistency
- Quantum Chemistry: basis set availability, method-basis set compatibility (e.g., CCSD requires at least triple-zeta), charge-multiplicity consistency
- Bioinformatics: quality score encoding detection, adapter sequence validity, reference genome availability

**L3 — Execution Simulation**: Pre-flight checks that simulate execution without consuming compute:
- File dependency graph validation (all inputs producible by upstream steps or existing files)
- Command existence check (is `gmx`, `pw.x`, `orca` available in PATH or container?)
- Resource estimation (memory, walltime, GPU requirements)

### 2.4 Export and Execution

The export engine generates executable artifacts in multiple formats:
- **Bash**: Sequential shell script with error handling
- **Python**: Python script with subprocess management and logging
- **Snakemake**: Workflow definition for HPC cluster execution
- **JSON**: Machine-readable plan for integration with external tools

The execution engine supports three modes:
- **Dry-run**: Validate without executing (default)
- **Local**: Execute via subprocess with environment isolation
- **Docker**: Execute in containerized environment with pre-installed scientific software

---

## 3. Validation Methodology

### 3.1 Test Suite

The system includes 44 unit tests covering:
- Core workflow generation (12 tests): Plan parsing, step extraction, dependency resolution
- Domain validation (16 tests): Rule registry, parameter bounds, compatibility checks
- Export engine (8 tests): Bash, Python, Snakemake, JSON serialization
- Execution engine (8 tests): Docker command building, result capture, error handling

### 3.2 Example: GROMACS Workflow Validation

Consider the natural language query: *"Simulate ubiquitin in water for 10 ns using AMBER99SB-ILDN force field at 300K with GPU acceleration."*

The generated workflow includes:
1. Topology preparation (`pdb2gmx`)
2. Solvation (`editconf`, `genbox`)
3. Energy minimization (`grompp` + `mdrun` with steep integrator)
4. NVT equilibration (`grompp` + `mdrun` with position restraints)
5. NPT equilibration (`grompp` + `mdrun` with position restraints)
6. Production run (`grompp` + `mdrun` with GPU acceleration)

Validation results:
- L1: ✅ All 6 steps have valid commands, file dependencies resolved
- L2: ✅ Temperature 300K ∈ [0.1, 1000]K; AMBER99SB-ILDN + TIP3P compatible; minimization precedes production
- L3: ✅ File dependency graph: topology → structure → box → solvated → minimized → equilibrated → production

---

## 4. Local LLM Evaluation

### 4.1 Experimental Setup

We evaluated local LLM workflow generation using:
- **Model**: Qwen3-235B-A22B (IQ4 quantization) via llama.cpp
- **Hardware**: Consumer GPU with 24GB VRAM
- **Test cases**: 5 domain-specific workflow queries (MD, DFT, QC, Bioinformatics, Materials)

### 4.2 Results

| Domain | Query | Steps Generated | Validation | Notes |
|--------|-------|----------------|------------|-------|
| MD | "Simulate lysozyme in water for 50ns" | 6 | ✅ Pass | Correct force field (AMBER99SB-ILDN), solvent (TIP3P), temperature (300K) |
| DFT | "Calculate band structure of silicon" | 4 | ✅ Pass | Correct functional (PBE), k-path (L-Γ-X), cutoff (50 Ry) |
| QC | "Optimize geometry of benzene at B3LYP/6-31G*" | 3 | ✅ Pass | Method-basis set compatible, charge=0, multiplicity=1 |
| Bioinfo | "RNA-seq differential expression analysis" | 5 | ✅ Pass | QC → alignment → quantification → DE → visualization |
| Materials | "Aluminum FCC crystal with EAM potential" | 4 | ✅ Pass | Lattice parameter 4.05Å, potential type consistent |

### 4.3 Truncation Handling

Local models with limited output length occasionally truncate JSON responses. The system implements automatic recovery via brace-depth matching to extract valid JSON objects from incomplete output. In our tests, 3 of 20 generation attempts produced truncated output; all were successfully recovered without user intervention.

---

## 5. Related Work

**Workflow Managers**: Snakemake, Nextflow, and Galaxy provide powerful pipeline orchestration but require users to write domain-specific code. ai4s-core complements these tools by generating the domain-specific inputs they execute.

**AI for Science Interfaces**: Recent tools like ChemCrow and BoilingPoint use LLMs for scientific reasoning but focus on property prediction rather than workflow generation. ai4s-core is unique in combining natural language workflow generation with multi-layer scientific validation.

**LLM Code Generation**: Tools like GitHub Copilot and Claude Code assist with general programming but lack domain-specific validation. ai4s-core's validation engine ensures scientific correctness, not just syntactic validity.

---

## 6. Conclusion and Future Work

ai4s-core demonstrates that natural language interfaces for scientific computing are feasible with appropriate validation safeguards. The combination of LLM generation and multi-layer scientific correctness checking addresses the key barrier—trust—that prevents adoption of AI-generated workflows in research.

### Current Status
- 5 scientific domains supported
- 44 unit tests, all passing
- Execution engine with Docker and local modes
- Local LLM support verified

### Future Work
- **HPC Integration**: Slurm/PBS backend for cluster execution (design complete, implementation pending)
- **Additional Domains**: Computational fluid dynamics, climate modeling, astrophysics
- **Web UI**: Browser interface for non-CLI users
- **Verified Templates**: Curated workflow templates validated by domain experts
- **SaaS Version**: Hosted service with team collaboration features

### Call for Contributors

We seek domain experts in computational chemistry, molecular simulation, and bioinformatics to validate workflow templates and contribute domain-specific validation rules. The project is open-source under MIT license at https://github.com/agent2agent-dev/ai4s-core.

---

## References

1. Mölder, F., et al. (2021). Sustainable data analysis with Snakemake. *F1000Research*, 10, 33.
2. Di Tommaso, P., et al. (2017). Nextflow enables reproducible computational workflows. *Nature Biotechnology*, 35(4), 316-319.
3. Abraham, M. J., et al. (2015). GROMACS: High performance molecular simulations through multi-level parallelism. *SoftwareX*, 1, 19-25.
4. Giannozzi, P., et al. (2009). QUANTUM ESPRESSO: a modular and open-source software project for quantum simulations of materials. *Journal of Physics: Condensed Matter*, 21(39), 395502.
5. Neese, F. (2012). The ORCA program system. *Wiley Interdisciplinary Reviews: Computational Molecular Science*, 2(1), 73-78.
6. Bran, A. M., et al. (2023). ChemCrow: Augmenting large-language models with chemistry tools. *arXiv preprint*, arXiv:2304.05376.

---

## Code Availability

- **Repository**: https://github.com/agent2agent-dev/ai4s-core
- **License**: MIT
- **Installation**: `pip install ai4s-core`
- **Documentation**: README.md in repository root
- **Issue Tracker**: https://github.com/agent2agent-dev/ai4s-core/issues

---

*Prepared for arXiv submission. Last updated: 2026-04-26.*
