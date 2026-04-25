"""
Domain registry: manages scientific domain-specific knowledge and tools.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DomainSpec:
    """Specification for a scientific domain."""
    name: str
    description: str
    common_tools: List[str] = field(default_factory=list)
    file_formats: List[str] = field(default_factory=list)
    typical_workflows: List[str] = field(default_factory=list)
    key_parameters: Dict[str, str] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)


class DomainRegistry:
    """Registry of supported scientific domains."""

    def __init__(self):
        self._domains: Dict[str, DomainSpec] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in scientific domains."""
        self.register(
            DomainSpec(
                name="molecular_dynamics",
                description="Classical molecular dynamics simulations",
                common_tools=[
                    "GROMACS", "OpenMM", "LAMMPS", "NAMD", "Amber",
                    "MDAnalysis", "VMD", "packmol"
                ],
                file_formats=[
                    "PDB", "GRO", "XTC", "TRR", "DCD", "TOP", "ITP", "PRM"
                ],
                typical_workflows=[
                    "system_preparation",
                    "energy_minimization",
                    "equilibration_nvt",
                    "equilibration_npt",
                    "production_run",
                    "trajectory_analysis",
                ],
                key_parameters={
                    "temperature": "Simulation temperature in K",
                    "pressure": "Simulation pressure in bar",
                    "timestep": "Integration timestep in fs",
                    "duration": "Total simulation time",
                    "force_field": "Force field model (e.g., CHARMM36, AMBER99SB-ILDN)",
                    "ensemble": "Statistical ensemble (NVT, NPT, NVE)",
                },
                validation_rules=[
                    "temperature must be > 0 K",
                    "timestep must be <= 2 fs for all-atom",
                    "box must be large enough for periodic boundaries",
                    "force field must be compatible with molecule types",
                ],
            )
        )

        self.register(
            DomainSpec(
                name="density_functional_theory",
                description="Electronic structure calculations via DFT",
                common_tools=[
                    "VASP", "Quantum ESPRESSO", "GPAW", "ABINIT",
                    "PySCF", "JDFTx", "SIESTA"
                ],
                file_formats=[
                    "POSCAR", "POTCAR", "KPOINTS", "INCAR",
                    "pw.in", "CIF", "XYZ", "CHGCAR", "WAVECAR"
                ],
                typical_workflows=[
                    "structure_relaxation",
                    "scf_calculation",
                    "band_structure",
                    "dos_calculation",
                    "phonon_calculation",
                    "molecular_dynamics_ab_initio",
                ],
                key_parameters={
                    "xc_functional": "Exchange-correlation functional",
                    "ecutwfc": "Plane-wave cutoff energy in Ry or eV",
                    "kpoints": "K-point sampling mesh",
                    "smearing": "Occupation smearing method and width",
                    "pseudopotential": "Pseudopotential family",
                    "spin_polarized": "Whether to include spin polarization",
                },
                validation_rules=[
                    "ecutwfc must be converged for the pseudopotential",
                    "k-point density must be sufficient for the system",
                    "cell size must accommodate vacuum for surfaces/molecules",
                ],
            )
        )

        self.register(
            DomainSpec(
                name="bioinformatics",
                description="Computational biology and sequence analysis",
                common_tools=[
                    "AlphaFold", "BLAST", "HMMER", "ClustalOmega",
                    "MAFFT", "RAxML", "IQ-TREE", "Biopython",
                    "SAMtools", "BWA", "GATK"
                ],
                file_formats=[
                    "FASTA", "FASTQ", "BAM", "SAM", "VCF",
                    "PDB", "MMIF", "GenBank", "GFF", "Newick"
                ],
                typical_workflows=[
                    "sequence_alignment",
                    "phylogenetic_tree_construction",
                    "protein_structure_prediction",
                    "genome_assembly",
                    "variant_calling",
                    "differential_expression",
                ],
                key_parameters={
                    "e_value": "BLAST E-value threshold",
                    "identity_threshold": "Sequence identity cutoff",
                    "bootstrap_replicates": "Number of bootstrap replicates",
                    "model": "Evolutionary substitution model",
                },
                validation_rules=[
                    "input sequences must be valid FASTA",
                    "bootstrap replicates >= 100 for publication",
                ],
            )
        )

        self.register(
            DomainSpec(
                name="quantum_chemistry",
                description="Quantum chemical calculations",
                common_tools=[
                    "ORCA", "Gaussian", "PySCF", "Psi4",
                    "Q-Chem", "Molpro", "NWChem"
                ],
                file_formats=[
                    "XYZ", "MOL", "SDF", "FCHK", "CUBE",
                    "log", "out", "hess"
                ],
                typical_workflows=[
                    "geometry_optimization",
                    "frequency_calculation",
                    "transition_state_search",
                    "reaction_pathway",
                    "excited_state_calculation",
                    "nmr_prediction",
                ],
                key_parameters={
                    "basis_set": "Gaussian basis set",
                    "method": "Electronic structure method (e.g., B3LYP, CCSD(T))",
                    "charge": "Molecular charge",
                    "multiplicity": "Spin multiplicity",
                    "solvent": "Solvent model if applicable",
                },
                validation_rules=[
                    "basis set must be available for all elements",
                    "method must be appropriate for system size",
                    "geometry optimization must converge",
                ],
            )
        )

    def register(self, spec: DomainSpec) -> None:
        """Register a new domain."""
        self._domains[spec.name] = spec

    def get(self, name: str) -> Optional[DomainSpec]:
        """Get a domain specification by name."""
        return self._domains.get(name)

    def get_context(self, name: str) -> str:
        """Get a formatted context string for LLM prompting."""
        spec = self._domains.get(name)
        if not spec:
            return f"Domain '{name}' not found. Available: {', '.join(self.list_domains())}"

        lines = [
            f"Domain: {spec.name}",
            f"Description: {spec.description}",
            "",
            "Common tools:",
        ]
        for tool in spec.common_tools:
            lines.append(f"  - {tool}")

        lines.extend(["", "Typical workflows:"])
        for wf in spec.typical_workflows:
            lines.append(f"  - {wf}")

        lines.extend(["", "Key parameters:"])
        for param, desc in spec.key_parameters.items():
            lines.append(f"  - {param}: {desc}")

        lines.extend(["", "Validation rules:"])
        for rule in spec.validation_rules:
            lines.append(f"  - {rule}")

        return "\n".join(lines)

    def list_domains(self) -> List[str]:
        """List all registered domain names."""
        return list(self._domains.keys())

    def tool_exists(self, domain: str, tool: str) -> bool:
        """Check if a tool is known for a given domain."""
        spec = self._domains.get(domain)
        if not spec:
            return False
        return tool in spec.common_tools
