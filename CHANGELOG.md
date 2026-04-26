# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Mock mode: generate realistic workflows without API keys (5 domains)
- Validation engine: domain-specific sanity checks for LLM-generated plans
  - MD: minimization, equilibration, temperature, timestep checks
  - DFT: SCF, cutoff, k-point, smearing checks
  - QC: optimization, basis set, charge/multiplicity checks
  - Bioinformatics: QC, alignment, replicate checks
- Execution engine: Docker container + local subprocess fallback
- Step-by-step generation strategy for limited-output models
- LLM truncation recovery: outline mode fallback
- CLI: `plan`, `list-domains`, `validate` commands
- 5 scientific domains: MD, DFT, QC, Bioinformatics, Materials
- 5 LLM providers: OpenAI, Anthropic, DeepSeek, Ollama, vLLM
- Local LLM support verified (qwen3.6-35B-A3B-IQ4 via vLLM)
- GitHub community templates (Issue, PR, Contributing)
- 44 tests covering core + mock domains + validation

### Changed
- Improved pyproject.toml metadata and SEO keywords
- Refactored executor: extracted `_build_docker_cmd` helper
- Added `__repr__` to `ExecutionResult`

## [0.1.0] - 2026-04-26

### Added
- Initial MVP release
- Core orchestrator: natural language -> workflow plan
- Domain registry with 5 scientific domains
- LLM interface with multiple provider support
- Plan parser and script exporter (Python, Bash, Snakemake)
- Basic CLI with argparse
- 34 core tests

[Unreleased]: https://github.com/anbus/ai4s-core/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/anbus/ai4s-core/releases/tag/v0.1.0
