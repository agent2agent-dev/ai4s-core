# GitHub Discussions 手动发布操作指南

> 生成时间: 2026-04-26 11:23（第18轮）
> 状态: 内容已就绪，需手动操作发布

---

## 为什么需要手动发布

GitHub Discussions 已启用 ✅，但当前 PAT 缺少 `write:discussion` scope，无法通过 API 自动发布。

**解决方案**: 复制粘贴发布（5分钟完成）。

---

## 操作步骤

### Step 1: 打开 Discussions 页面

访问: https://github.com/agent2agent-dev/ai4s-core/discussions

点击右上角 **"New discussion"** 绿色按钮。

---

### Step 2: 发布 Intro 帖子

**Category**: General

**Title**:
```
Welcome to ai4s-core — natural language for scientific computing
```

**Body** (复制以下内容):

```markdown
👋 Welcome to ai4s-core discussions!

**What is ai4s-core?**
An open-source CLI that turns plain English into validated, executable scientific computing workflows. No more memorizing GROMACS flags or Quantum ESPRESSO input syntax.

**Quick start:**
```bash
pip install ai4s-core
ai4s plan "simulate ubiquitin in water for 10ns" --format bash
```

**Current domains (5):**
- Molecular Dynamics (GROMACS, AMBER, OpenMM, LAMMPS, NAMD)
- DFT / Electronic Structure (VASP, Quantum ESPRESSO, GPAW, ABINIT)
- Quantum Chemistry (ORCA, Gaussian, PySCF, Psi4)
- Bioinformatics (RNA-seq, ATAC-seq, phylogenetics, genome assembly)
- Materials Simulation (LAMMPS — aluminum FCC, defect modeling)

**We need help with:**
- 🧪 **Domain experts**: If you use MD/DFT/QC/bioinformatics tools daily, your feedback is gold
- 💻 **Contributors**: New domains, validation rules, bug fixes — see CONTRIBUTING.md
- 📝 **Documentation**: Tutorials, examples, blog posts
- 🔬 **Testing**: Try it with your real research problems, report what breaks

**Roadmap:**
- ✅ Core workflow generation (5 domains, 44 tests passing)
- ✅ Validation engine (domain-specific rules: MD minimization, DFT cutoff, QC basis set, Bio QC)
- ✅ Execution engine (Docker + local subprocess, dry-run mode)
- ✅ Local LLM support (llama.cpp, Ollama, vLLM — verified with qwen3.6-35B)
- ✅ Step-by-step generation for limited-output models
- 🔄 HPC integration (Slurm/PBS) — design ready, implementation pending
- 🔄 Web UI for non-CLI users
- 🔄 SaaS hosted version
- 🔄 Verified workflow templates from domain experts

Drop a comment if you're working in computational chemistry / molecular simulation — I'd love to hear what workflow tools you currently use and what frustrates you about them.

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT
```

点击 **"Start discussion"**。

---

### Step 3: 发布技术博客帖子

**Category**: Show and tell

**Title**:
```
How we built a natural language interface for scientific computing (and why it matters)
```

**Body**: 复制 `community/tech-blog-complete-v0.1.md` 的全部内容。

文件路径: `/workspace/d3168165-c968-48da-9265-167643ec51f9/repos/Hermes_Workspace/community/tech-blog-complete-v0.1.md`

点击 **"Start discussion"**。

---

## 发布后行动

### 立即做
- [ ] 在 Intro 帖子中 pinned（置顶）
- [ ] 将 Discussion 链接添加到 README
- [ ] 在 README 的 badge 区域添加 Discussions 计数 badge

### 后续监控（我来做）
- 每天检查新回复
- 回复所有技术问题（24小时内）
- 收集用户反馈到 `feedback/` 目录
- 根据反馈调整产品优先级

---

## 替代方案（如果你不想手动操作）

**方案A**: 提供含 `write:discussion` scope 的 GitHub PAT
- 生成路径: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- 勾选权限: `repo` + `write:discussion`
- 提供给我，后续所有 Discussion 自动发布

**方案B**: 给我临时的 GitHub 账号访问
- 风险较低（仅操作 Discussion，不碰代码）
- 完成后可撤销权限

---

## 预期效果

- Intro 帖子: 建立社区第一印象，降低贡献门槛
- 技术博客: 展示技术深度，吸引技术用户
- 两个帖子互相链接，形成内容闭环

**目标**: 2周内获得 2+ 有意义的用户回复。

---

**最后更新**: 2026-04-26 11:23（第18轮）
