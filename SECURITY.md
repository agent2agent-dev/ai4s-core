# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in ai4s-core, please report it responsibly.

**Do NOT open a public issue.** Instead:

1. Email: anbus@ai4s.dev (if available)
2. Or contact the maintainer via the project's private communication channel

We will:
- Acknowledge receipt within 48 hours
- Provide a timeline for a fix within 7 days
- Credit you in the release notes (with your permission)

## Security Considerations

### Workflow Execution
- ai4s-core generates shell commands from natural language via LLM
- **Always review generated workflows before execution**
- Use `--mock` mode to preview workflows without running them
- The `dry_run()` function shows what would be executed

### Docker Execution
- Docker containers run with host directory mounted
- Generated commands execute inside the container
- Ensure Docker images are from trusted sources (quay.io/biocontainers)

### LLM Data Privacy
- Local LLM mode (vLLM/Ollama): zero data leaves your machine
- Cloud LLM mode: prompts sent to provider API
- No data retention on our side (this is a client library)

### API Keys
- Store API keys in environment variables, never commit to git
- Use `.env` files (already in `.gitignore`)
- Rotate keys regularly

## Known Limitations

- LLM-generated commands may contain errors — validation engine catches common issues but not all
- Scientific correctness is the user's responsibility
- Always verify results with domain expertise
