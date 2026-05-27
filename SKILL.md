---
name: shotgun
description: Fan out a user's research or codebase-investigation prompt across installed CLI coding agents, then synthesize the best findings. Use when the user says /shotgun, asks for shotgun research, wants multiple agent opinions, wants to compare Codex/Claude/Cursor/Antigravity/Pi/OpenCode/Gemini/Qwen/Aider/Goose/Amp/Copilot or similar CLI agents, or asks Codex to use all available coding CLIs for research before producing a report.
---

# Shotgun

Run read-only, parallel "ask the other coding agents" research. The goal is breadth first: collect independent answers from installed CLI coding tools, summarize each briefly, then merge their strongest evidence and disagreements into one report.

## Workflow

1. Restate the user's request as an optimized agentic research prompt.
   - Preserve the user's intent and constraints.
   - Ask each tool to stay read-only unless the user explicitly requested edits.
   - Ask for concise, structured output with: answer, evidence, uncertainty, recommended next checks, and sources or file references when available.
   - Tell tools that support delegation/subagents to fan out internally when useful, but to return only a concise final.

2. Run the bundled fan-out runner:

```powershell
python C:\Users\danhm\.codex\skills\shotgun\scripts\shotgun.py --prompt "..." --cwd "<workspace>"
```

If `python` is unavailable, use any available Python runtime. The runner has no third-party dependencies. Prefer `--prompt-file` for long prompts. The default per-tool timeout is intentionally lax: 7200 seconds. For unusually deep research, pass a larger `--timeout` and ensure the invoking shell/tool timeout is larger than the runner timeout.

3. Inspect the generated run directory.
   - `summary.md` lists detected tools, command status, and output files.
   - `outputs/*.txt` contains each tool's captured answer.
   - `metadata.json` records exact adapters, exit codes, and durations.

4. Produce the final answer in three layers:
   - **Per-tool scorecards:** for every detected tool, summarize the good and bad. For successful tools, name the strongest useful contribution and the main weakness, blind spot, or questionable claim. For failed, empty, or timed-out tools, state the status and useful diagnostic from `summary.md`/`metadata.json`.
   - **Consensus and disagreements:** what multiple tools agreed on, what only one tool noticed, and which claims are uncertain.
   - **Comprehensive report:** the best merged answer, with local file references or web citations if the tools supplied them and they are credible.

## Safety

- Default to research-only execution. Do not let downstream tools modify files unless the user explicitly asks for implementation.
- Do not pass secrets or private credentials into the prompt. Redact tokens, API keys, customer data, and unrelated personal data.
- If a tool is installed but only exposes an interactive TUI, record it as unavailable for headless shotgun rather than launching a hanging session.
- If the runner reports an installed unsupported tool, inspect `<tool> --help` and the latest docs before adding a manual invocation.
- Keep timeouts finite but generous. A slow or silent tool should be reported as timed out, not allowed to block the whole shotgun pass indefinitely.

## Prompt Template

Use this shape when creating the prompt sent to each CLI:

```text
You are one agent in a shotgun research pass. Work independently.

Research request:
<user request>

Context:
- Current working directory: <cwd>
- Treat this as read-only research unless explicitly told otherwise.
- If your CLI supports subagents, delegation, or parallel internal research, use it when it improves coverage.

Output:
1. Direct answer or conclusion.
2. Key evidence, with file paths, commands, URLs, or sources when available.
3. Important caveats or uncertainty.
4. Best next checks.

Keep the final concise and information-dense. Do not edit files.
```

## Tool Matrix

The runner's first-pass adapters are documented in [references/cli-tools.md](references/cli-tools.md). Update that reference and `scripts/shotgun.py` together when adding or correcting a CLI adapter.
