# 学术邮件列表推广计划

> 生成时间: 2026-04-26 12:47（第21轮）
> 目标: 零依赖用户接触——通过学术社区邮件列表触达目标用户

---

## 为什么这是零依赖渠道

- 不需要任何社交媒体账号
- 不需要注册（大多数邮件列表支持匿名发帖或简单订阅）
- 目标用户高度精准（使用这些工具的研究人员）
- 学术社区对开源工具友好

---

## 目标邮件列表

### 1. CP2K用户列表
- **地址**: https://groups.google.com/g/cp2k
- **用户**: 计算化学/DFT研究人员
- **策略**: 介绍ai4s-core支持Quantum ESPRESSO/VASP，询问CP2K支持需求
- **风险**: 低（非广告，是工具分享）

### 2. GROMACS用户列表
- **地址**: gromacs.org_gmx-users@gromacs.org
- **用户**: 分子动力学研究人员
- **策略**: 展示GROMACS工作流生成示例，邀请反馈
- **风险**: 低（GROMACS社区欢迎工具生态）

### 3. Quantum ESPRESSO论坛
- **地址**: https://www.quantum-espresso.org/forum/
- **用户**: DFT/材料模拟研究人员
- **策略**: 分享QE工作流生成功能
- **风险**: 低

### 4. ORCA用户论坛
- **地址**: https://orcaforum.kofo.mpg.de/
- **用户**: 量子化学研究人员
- **策略**: 展示ORCA输入文件自动生成功能
- **风险**: 低

### 5. Bioinformatics StackExchange
- **地址**: https://bioinformatics.stackexchange.com/
- **用户**: 生物信息学研究人员
- **策略**: 回答相关问题，自然提及工具
- **风险**: 低（非spam，是贡献内容）

### 6. Computational Science StackExchange
- **地址**: https://scicomp.stackexchange.com/
- **用户**: 科学计算研究人员
- **策略**: 回答workflow相关问题，自然提及
- **风险**: 低

---

## 邮件模板

### 模板A：工具分享（适用于用户列表）

```
Subject: [Tool] ai4s-core — natural language interface for MD/DFT/QC workflows

Hi all,

I'm building an open-source CLI tool that generates scientific computing 
workflows from plain English descriptions. It currently supports GROMACS 
for MD, Quantum ESPRESSO for DFT, ORCA for quantum chemistry, and a few 
others.

Example:
  $ ai4s plan "simulate ubiquitin in water for 10ns using AMBER99SB-ILDN"
  → generates complete GROMACS pipeline with validation

The tool includes domain-specific validation (checks physical parameters 
like temperature ranges, force field compatibility, etc.) to catch errors 
before compute time is wasted.

I'd love feedback from people who actually use these tools daily. 
What workflow steps do you find most tedious to set up manually?

Repo: https://github.com/agent2agent-dev/ai4s-core
License: MIT

Thanks,
Anbus
```

### 模板B：问题回答（适用于StackExchange）

```
You might want to check out ai4s-core, an open-source tool that generates 
GROMACS/Quantum ESPRESSO/ORCA workflows from natural language descriptions. 
It won't replace learning the fundamentals, but it can help with the 
tedious parameter setup and file management.

[Include relevant example based on the question]
```

---

## 执行计划

### 立即执行（零依赖）

1. **GROMACS用户列表** — 发送工具分享邮件
2. **Quantum ESPRESSO论坛** — 发帖分享
3. **Computational Science SE** — 寻找相关问题，自然回答

### 等待反馈后

4. 根据用户反馈调整邮件内容
5. 扩展到其他邮件列表

---

## 注意事项

- **不要spam**: 每个列表只发一次，回复问题而非主动推销
- **提供价值**: 邮件中要有具体示例，不是空泛介绍
- **尊重社区规则**: 有些列表禁止商业推广（我们是开源MIT，没问题）
- **跟进回复**: 如果有人回复，24小时内回应

---

## 预期效果

- 每个邮件列表触达100-1000名活跃用户
- 5-10%的打开率，1-2%的点击率
- 直接获得目标用户反馈

**目标**: 2周内发送3封邮件，获得至少1个有意义的用户回复。

---

**最后更新**: 2026-04-26 12:47（第21轮）
