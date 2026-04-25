"""
ai4s-core: AI for Science orchestration framework.

Enables researchers to describe scientific problems in natural language
and automatically generates executable computational workflows.

Supported domains (planned):
- Molecular Dynamics (MD) - GROMACS, OpenMM, LAMMPS
- Density Functional Theory (DFT) - VASP, Quantum ESPRESSO, GPAW
- Bioinformatics - AlphaFold, BLAST, phylogenetics
- Fluid Dynamics - OpenFOAM
- Quantum Chemistry - PySCF, ORCA
"""

__version__ = "0.1.0"
__author__ = "Anbus <anbus@ai4s.dev>"

from .orchestrator import WorkflowOrchestrator
from .domain import DomainRegistry
from .llm_interface import LLMInterface

__all__ = ["WorkflowOrchestrator", "DomainRegistry", "LLMInterface"]
