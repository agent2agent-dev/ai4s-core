👋 Welcome to ai4s-core discussions!

**What is ai4s-core?**
An open-source CLI that turns plain English into validated, executable scientific computing workflows. No more memorizing GROMACS flags or Quantum ESPRESSO input syntax.

**Quick start:**
```bash
pip install ai4s-core
ai4s plan "simulate ubiquitin in water for 10ns" --format bash
```

**Current domains:**
- Molecular Dynamics (GROMACS, AMBER, OpenMM, LAMMPS, NAMD)
- DFT (Quantum ESPRESSO, VASP, GPAW, ABINIT)
- Quantum Chemistry (ORCA, Gaussian, PySCF, Psi4)
- Bioinformatics (RNA-seq, ATAC-seq, phylogenetics, genome assembly)
- Materials Science (LAMMPS, EAM potentials)

**We need help with:**
- 🧪 **Domain experts**: If you use MD/DFT/QC/bioinformatics tools daily, your feedback is gold
- 💻 **Contributors**: New domains, validation rules, bug fixes — see CONTRIBUTING.md
- 📝 **Documentation**: Tutorials, examples, blog posts
- 🔬 **Testing**: Try it with your real research problems, report what breaks

**Roadmap:**
- ✅ Core workflow generation
- ✅ Validation engine (L1-L3: structural, domain-rule, execution-simulation)
- ✅ Execution engine (Docker + local + dry-run)
- ✅ Local LLM support (llama.cpp/Ollama/vLLM)
- ✅ 44 unit tests, all passing
- 🔄 HPC integration (Slurm/PBS) — design ready, implementation pending
- 🔄 More domains (CFD, climate modeling, astrophysics)
- 🔄 Verified templates validated by domain experts
- 🔄 SaaS hosted version with team collaboration

Drop a comment if you're working in computational chemistry / molecular simulation — I'd love to hear what workflow tools you currently use and what frustrates you about them.

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
