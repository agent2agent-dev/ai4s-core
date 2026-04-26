# Cold Outreach Templates for ai4s-core

> Zero-dependency user contact strategy. No social media accounts needed.

---

## Strategy Overview

**Goal**: Generate at least 1 real user conversation per week.

**Channels** (ranked by effort/expected response rate):
1. **GitHub Issues/PRs on related projects** — Highest response rate, direct relevance
2. **Cold email to paper authors** — Medium response rate, highly targeted
3. **arXiv/paper comment sections** — Low response rate, but public visibility
4. **Academic forum posts** — Medium response rate, community building

**Principle**: Every outreach must offer value first, ask for feedback second.

---

## Template 1: GitHub Issue on Related Project

**Target**: Projects like GROMACS tutorials, Snakemake workflows, Nextflow pipelines, Bioinformatics tool collections

**Subject**: "Feature idea: Natural language interface for [project name] workflows"

```markdown
Hi [maintainer name],

I've been working on a tool called [ai4s-core](https://github.com/agent2agent-dev/ai4s-core) that converts natural language descriptions into executable scientific workflows.

For example, a user can type:
> "Run a GROMACS MD simulation for protein equilibration"

And get a complete Python script with all steps, validation checks, and auxiliary files.

I noticed your project [project name] has excellent [workflows/tutorials/pipelines]. I was wondering:

1. Have you seen users struggle with the learning curve for setting up workflows?
2. Would a natural language interface be valuable for your community?
3. Would you be open to a collaboration where ai4s-core could generate workflows compatible with your project?

I'm not trying to sell anything — this is an open-source project (MIT license), and I'm looking for feedback from real users to understand what actually matters.

If you have 10 minutes for a quick chat or async feedback, I'd really appreciate it.

Best,
Anbus
Independent developer, AI for Science
```

**Follow-up**: If no response in 7 days, send a brief follow-up with a concrete example relevant to their project.

---

## Template 2: Cold Email to Paper Author

**Target**: Authors of recent papers (2024-2026) in computational chemistry, molecular dynamics, or bioinformatics workflow automation

**How to find**: Google Scholar search for "workflow automation molecular dynamics" or "Snakemake bioinformatics pipeline"

**Subject**: "Quick question about workflow setup in your [journal] paper"

```
Dear Dr. [Last Name],

I read your recent paper "[Paper Title]" in [Journal] with great interest. 

Specifically, I noticed that [specific detail about their workflow setup — e.g., "you mentioned spending significant time configuring the Snakemake pipeline for the RNA-seq analysis"].

I'm building an open-source tool (ai4s-core) that converts natural language descriptions into executable scientific workflows. The idea is that a researcher could type:

"Run RNA-seq differential expression analysis on paired-end reads"

and get a complete, validated workflow script instead of manually writing configuration files.

I have two quick questions:

1. In your experience, how much time do researchers typically spend on workflow setup vs. actual science?
2. Would a natural language interface have been useful for your project, or are the manual steps actually valuable for understanding?

I'm not selling anything — this is an MIT-licensed open-source project, and I'm seeking honest feedback from researchers who actually do this work.

If you have 5 minutes to reply, I'd be grateful. If you're open to a 15-minute video call, even better.

Best regards,
Anbus
[GitHub profile link]
[Project link]
```

**Follow-up**: If no response in 10 days, send one brief follow-up. If still no response, move on.

---

## Template 3: Academic Forum Post

**Target**: Computational chemistry/bioinformatics forums (e.g., Matter Modeling Stack Exchange, Bioinformatics Stack Exchange)

**Title**: "Would a natural language interface for computational chemistry workflows be useful?"

```markdown
I'm an independent developer building an open-source tool that converts natural language descriptions into executable scientific workflows.

Example:
- Input: "Run a GROMACS MD simulation for protein equilibration"
- Output: Complete Python script with all steps, validation checks, and auxiliary files

The tool supports GROMACS, Quantum ESPRESSO, ORCA, and bioinformatics pipelines. It can use cloud LLMs (OpenAI, DeepSeek) or local models (Ollama, llama.cpp) for privacy.

**My question for this community**: 

For those of you who regularly set up MD/DFT calculations, would this actually save you time, or is the manual setup part of understanding what you're doing?

I'm genuinely trying to understand if this solves a real problem or if it's a solution looking for one. Any honest feedback appreciated.

Project: https://github.com/agent2agent-dev/ai4s-core
License: MIT
```

---

## Template 4: Hacker News "Ask HN"

**Title**: "Ask HN: Would scientists use a natural language interface for computational workflows?"

```markdown
I'm building an open-source tool that converts plain English descriptions into executable scientific workflows (molecular dynamics, DFT, bioinformatics).

Example: "Run a GROMACS MD simulation for protein equilibration" → complete Python script with validation checks.

The target users are computational chemistry and bioinformatics researchers who currently spend hours writing Snakemake/Nextflow configs or bash scripts.

Before I invest more time, I want to validate: **Is this a real pain point, or do scientists prefer manual control?**

If you work in computational science, I'd love your honest take. What would make you try this? What would make you distrust it?

Project: https://github.com/agent2agent-dev/ai4s-core
```

**When to post**: Tuesday-Thursday, 8-10 AM US Eastern Time for maximum visibility.

---

## Tracking Sheet

| Date | Channel | Target | Template | Sent | Response | Notes |
|------|---------|--------|----------|------|----------|-------|
| | | | | | | |

**Goal**: 5 outreaches per week. Track everything.

---

## Response Handling

### Positive Response
- Thank them immediately
- Offer 15-minute video call
- Ask: "What would make this indispensable for you?"
- Ask: "What's the biggest reason you WOULDN'T use this?"

### Critical Response
- Thank them for honesty
- Ask for specific examples of what would need to change
- Document the feedback
- Follow up in 2-4 weeks with improvements

### No Response
- One follow-up after 7-10 days
- If still no response, mark as "no response" and move on
- Don't take it personally — researchers are busy

---

## Success Metrics

- **Week 1-2**: 10 outreaches sent, 2 responses
- **Month 1**: 20 outreaches, 5 responses, 1 video call
- **Month 2**: 40 outreaches, 10 responses, 3 video calls, 1 beta tester

**The goal is not mass outreach — it's genuine conversations that shape the product.**
