## Add ai4s-core to Awesome Chemistry

**Name**: ai4s-core
**Link**: https://github.com/agent2agent-dev/ai4s-core
**Description**: Natural language interface for computational chemistry workflows. Generate validated input files for ORCA, Gaussian, PySCF, Psi4, Quantum ESPRESSO, and VASP from plain English descriptions.

**Why it fits this list:**
ai4s-core automates the setup of quantum chemistry and DFT calculations by translating natural language into validated input files. It includes domain-specific validation rules for basis set compatibility, DFT cutoff convergence, and functional selection — catching errors before expensive compute jobs are submitted.

**Example:**
```bash
$ ai4s plan "optimize water molecule with B3LYP/6-31G* using ORCA" --format bash
→ Generates: geometry optimization workflow with basis set validation
```

**Key chemistry features:**
- Quantum Chemistry: ORCA, Gaussian, PySCF, Psi4
- DFT / Electronic Structure: VASP, Quantum ESPRESSO, GPAW, ABINIT
- Validates basis set compatibility, DFT cutoff convergence, functional appropriateness
- Step-by-step generation for limited-output LLMs
- Local LLM support — sensitive research data never leaves your machine
- MIT license, 44 tests passing

**License**: MIT
**Language**: Python

---

*This PR adds ai4s-core to the awesome-chemistry list. Happy to adjust placement or description based on maintainer feedback.*
