👋 Welcome to ai4s-core discussions!

**What is ai4s-core?**
An open-source CLI that turns plain English into validated, executable scientific computing workflows. No more memorizing GROMACS flags or Quantum ESPRESSO input syntax.

**Quick start:**
```bash
pip install ai4s-core
ai4s plan "simulate ubiquitin in water for 10ns" --format bash
```

**Current domains:**
- Molecular Dynamics (GROMACS)
- DFT (Quantum ESPRESSO)
- Quantum Chemistry (ORCA)
- Bioinformatics (RNA-seq)

**We need help with:**
- 🧪 **Domain experts**: If you use MD/DFT/QC/bioinformatics tools daily, your feedback is gold
- 💻 **Contributors**: New domains, validation rules, bug fixes — see CONTRIBUTING.md
- 📝 **Documentation**: Tutorials, examples, blog posts
- 🔬 **Testing**: Try it with your real research problems, report what breaks

**Roadmap:**
- ✅ Core workflow generation
- ✅ Validation engine (L2 domain rules)
- ✅ Execution engine (Docker + local)
- 🔄 HPC integration (Slurm/PBS) — design ready, implementation pending
- 🔄 More domains (LAMMPS, WRF, FEniCS)
- 🔄 SaaS hosted version

Drop a comment if you're working in computational chemistry / molecular simulation — I'd love to hear what workflow tools you currently use and what frustrates you about them.

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
