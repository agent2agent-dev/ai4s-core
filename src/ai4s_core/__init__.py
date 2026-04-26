"""
ai4s-core: AI for Science orchestration framework.

Enables researchers to describe scientific problems in natural language
and automatically generates validated, executable computational workflows.

Supported domains:
- Molecular Dynamics (MD) - GROMACS, AMBER, OpenMM, LAMMPS, NAMD
- Density Functional Theory (DFT) - Quantum ESPRESSO, VASP, GPAW, ABINIT
- Quantum Chemistry - ORCA, Gaussian, PySCF, Psi4
- Bioinformatics - RNA-seq, ATAC-seq, phylogenetics, genome assembly
- Materials Science - LAMMPS, EAM potentials

Features:
- Natural language to executable workflow (Bash/Python/Docker)
- Multi-level validation (structural, domain-rule, execution-simulation)
- Local LLM support (llama.cpp/Ollama/vLLM) - privacy-friendly
- Mock mode for zero-dependency demos
- 44 unit tests, all passing
"""

__version__ = "0.1.0"
__author__ = "Anbus <anbus@ai4s.dev>"

from .orchestrator import WorkflowOrchestrator
from .domain import DomainRegistry
from .llm_interface import LLMInterface

__all__ = ["WorkflowOrchestrator", "DomainRegistry", "LLMInterface"]
