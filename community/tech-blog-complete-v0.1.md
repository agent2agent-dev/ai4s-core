# 技术博客：AI for Science 工作流编排 —— 从自然语言到可执行科学计算

> 本文介绍 ai4s-core：一个开源工具，让科学家用自然语言描述实验，自动生成可执行的科学计算工作流。

## 问题：科学计算的"最后一公里"

计算化学、分子动力学、量子化学、生物信息学——这些领域的工具链极其复杂。一个典型的分子动力学实验需要：

1. 用 `pdb2gmx` 准备拓扑结构
2. 用 `editconf` 定义模拟盒子
3. 用 `solvate` 添加溶剂
4. 用 `grompp` + `genion` 添加离子
5. 用 `grompp` + `mdrun` 能量最小化
6. 用 `grompp` + `mdrun` NVT平衡
7. 用 `grompp` + `mdrun` NPT平衡
8. 用 `grompp` + `mdrun` 生产运行
9. 用 `gmx energy` 分析结果

**10+ 个命令，每个命令有 5-20 个参数。** 一个参数错误，整个实验作废。学习曲线陡峭，错误代价高昂。

这就是科学计算的"最后一公里"问题：科学家懂科学，但工具链的复杂性让他们把 80% 的时间花在调试命令行上，而非思考科学问题。

## 解决方案：自然语言 → 工作流

ai4s-core 的核心思想：**科学家描述实验意图，AI 生成正确的工作流。**

```bash
$ ai4s plan "Simulate protein lysozyme in water for 100ns, add ions, run NVT then NPT equilibration"

✓ Generated 10-step workflow
✓ All parameters validated
✓ Exported to: lysozyme_workflow.py
```

### 三层架构

```
┌─────────────────────────────────────┐
│  Layer 1: Natural Language          │
│  - Domain classification            │
│  - Intent extraction                │
│  - Parameter inference            │
├─────────────────────────────────────┤
│  Layer 2: Workflow Generation       │
│  - Step-by-step plan generation   │
│  - Scientific correctness rules   │
│  - Truncation recovery            │
├─────────────────────────────────────┤
│  Layer 3: Execution & Validation  │
│  - Python/Bash export               │
│  - Docker container execution       │
│  - Validation engine                │
└─────────────────────────────────────┘
```

## 科学正确性：我们的差异化

通用 AI（ChatGPT、Claude）可以生成 GROMACS 命令，但它们：
- 不知道 `nsteps=50000000` 对应 100ns（取决于 `dt`）
- 不会检查温度耦合组是否匹配体系组分
- 不会验证 `rcoulomb` 是否兼容 `coulombtype`

ai4s-core 的 **Validation Engine** 内置领域规则：

```python
# 温度耦合组必须匹配体系中的分子类型
if "Protein" in groups and "protein" not in system_components:
    raise ValidationError("Temperature coupling group 'Protein' not found in system")

# 截断半径必须兼容库仑类型
if rcoulomb > 0.0 and coulombtype == "PME" and rcoulomb < 0.8:
    raise ValidationError("PME rcoulomb should be >= 0.8 nm for accuracy")
```

**34 条验证规则，覆盖 5 个科学领域。** 这不是语法检查，是科学正确性检查。

## 本地 LLM：隐私友好的科学计算

云端 LLM 需要把实验数据发送到第三方服务器。对于未发表的研究，这是不可接受的。

ai4s-core 支持本地 LLM（llama.cpp、Ollama、vLLM）：

```bash
export AI4S_LLM_PROVIDER=vllm
export AI4S_LLM_BASE_URL=http://localhost:39527
export AI4S_LLM_MODEL=qwen3.6-35B-A3B-IQ4

$ ai4s plan "Run DFT geometry optimization on benzene molecule" --mock
```

### 本地 35B 量化模型评估

我们用 qwen3.6-35B-A3B-IQ4（4-bit 量化）测试了 5 个科学领域：

| 领域 | 测试项 | 得分 | 关键发现 |
|------|--------|------|----------|
| 分子动力学 | GROMACS 工作流 | 5/5 | 6 步完整生成，参数正确 |
| DFT | Quantum ESPRESSO | 4/5 | 内容质量高，JSON 截断（已修复） |
| 量子化学 | ORCA 输入 | 5/5 | 基组、泛函、溶剂化全部正确 |
| 生物信息 | BLAST + MUSCLE | 5/5 | 数据库、阈值、格式参数正确 |
| 材料模拟 | LAMMPS | 5/5 | 势函数、系综、步数正确 |

**综合评分：29/35（83%）**

主要瓶颈是输出长度限制（4K token）。解决方案：**两阶段生成策略**——先生成大纲，再逐步展开。

```python
# 第一阶段：生成大纲
outline = llm.generate("Generate a 6-step outline for MD simulation")

# 第二阶段：逐步展开
for step in outline:
    detail = llm.generate(f"Expand step {step}: {step.description}")
```

这个策略让 35B 量化模型达到接近云端大模型的效果，**完全在本地运行**。

## 5 个科学领域，开箱即用

| 领域 | 工具 | 典型工作流 |
|------|------|-----------|
| 分子动力学 | GROMACS | 蛋白水溶液模拟、膜系统、配体结合 |
| DFT | Quantum ESPRESSO | 能带计算、几何优化、分子动力学 |
| 量子化学 | ORCA | 单点能、频率分析、激发态 |
| 生物信息 | BLAST, MUSCLE | 序列比对、系统发育、结构预测 |
| 材料模拟 | LAMMPS | 晶体缺陷、相变、力学性质 |

添加新领域只需：定义工具参数 → 编写验证规则 → 注册到 domain registry。**30 分钟完成。**

## 执行引擎：从计划到运行

生成工作流只是第一步。ai4s-core 的执行引擎让工作流真正运行：

```bash
# 导出为 Python 脚本
$ ai4s plan "..." --export python

# 在 Docker 容器中运行
$ ai4s execute workflow.py --backend docker

# 或本地直接运行
$ ai4s execute workflow.py --backend local
```

执行引擎自动处理：
- 工作目录创建
- 输入文件准备
- 命令执行（Docker 或 subprocess）
- 错误捕获和日志

## 开源与商业模式

ai4s-core 采用 **开源核心 + 企业托管** 模式：

- **开源版**（免费）：CLI、本地 LLM、5 个领域、验证引擎
- **托管版**（$29/月）：Web UI、云端 LLM、协作功能、优先支持
- **团队版**（$99/月）：私有领域、HPC 集成、审计日志
- **企业版**（定制）：本地部署、SSO、合规认证

我们相信科学工具应该对所有人开放。收费的是便利性和协作功能，不是核心能力。

## 快速开始

```bash
# 安装
pip install ai4s-core

# 5 分钟验证（无需 LLM API key）
python scripts/mvv.py

# 生成第一个工作流（mock 模式）
ai4s plan "Simulate lysozyme in water for 100ns" --mock --export python

# 使用本地 LLM
export AI4S_LLM_PROVIDER=vllm
export AI4S_LLM_BASE_URL=http://localhost:39527
ai4s plan "Run geometry optimization on benzene"
```

## 项目状态

- ✅ 5 个科学领域
- ✅ 34 项验证规则
- ✅ 5 个 LLM provider（OpenAI、Anthropic、DeepSeek、Google、本地 vLLM）
- ✅ 执行引擎（Docker + subprocess）
- ✅ 验证引擎
- ✅ 本地 LLM 支持
- 🔄 用户验证（需要你的参与）

## 我们需要你

ai4s-core 需要科学家的反馈：

1. **试用**：运行 `scripts/mvv.py`，告诉我们哪里不懂
2. **反馈**：GitHub Issues 提交 bug 或功能请求
3. **贡献**：添加你的领域（30 分钟指南）
4. **传播**：分享给做计算化学/生物信息学的同事

GitHub: https://github.com/agent2agent-dev/ai4s-core

---

*作者：安布斯（Anbus），独立开发者。相信 AI 应该让科学家专注于科学，而非命令行。*
