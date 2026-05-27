# CLI Coding Agent Matrix

Verified from official docs and local `--help` output on 2026-05-27 where available. Prefer local `--help` when docs and installed versions disagree.

| Tool | Headless command pattern | Notes |
| --- | --- | --- |
| Codex CLI | `codex exec --skip-git-repo-check --sandbox read-only --color never -c model_reasoning_effort="xhigh" -o <final-file> "<prompt>"` | `exec` is the non-interactive path. `-o/--output-last-message` gives a cleaner final answer. Use extra-high reasoning wherever the CLI exposes it. |
| Claude Code | `claude --print --no-session-persistence --permission-mode plan --effort high "<prompt>"` | `-p/--print` exits after one response. Plan mode is the default shotgun safety stance. Use high reasoning wherever the CLI exposes it. |
| Cursor Agent | `cursor-agent --print --mode ask --model composer-2.5 --output-format json --trust --workspace <cwd> "<prompt>"` | `--print` is headless. `ask` mode is read-only. Prefer JSON and extract `result`; text mode can be lossy with multi-line prompts. The runner tries Composer first, then falls back to `--model auto` JSON if the account rejects named models. Windows installs may expose `cursor-agent.cmd` under `%LOCALAPPDATA%\cursor-agent`. |
| Antigravity CLI | `agy --log-file <log-file> --print --print-timeout 10m "<prompt>"` | The new CLI command is `agy`, not `antigravity-ide`. On Windows it may live at `%LOCALAPPDATA%\agy\bin\agy.exe`. Some local builds/auth states generate internally but return empty stdout; keep logs and mark this explicitly. |
| OpenCode | `opencode run "<prompt>"` | Current docs expose `run` for programmatic use. Older builds may use `opencode -p "<prompt>" -q`; the runner tries both. |
| Pi | `pi --tools read,grep,find,ls -p "<prompt>"` | `-p/--print` is one-shot. Read-only tool selection keeps shotgun passes from editing. |
| Gemini CLI | `gemini -p "<prompt>"` | `-p/--prompt` is headless mode. |
| Qwen Code | `qwen -p "<prompt>"` | Qwen Code is adapted from Gemini CLI and supports `-p/--prompt`; some builds also support `--output-format text`. |
| Aider | `aider --chat-mode ask --message "<prompt>" --no-auto-commits` | `--message` exits after one prompt. `ask` mode avoids edits. |
| Goose | `goose run --no-session -t "<prompt>" -q --output-format text` | `goose run` executes and exits; `-q` suppresses non-response output. |
| Amp | `amp -x "<prompt>"` | Amp docs describe `-x` for non-interactive mode. Use conservative timeouts. |
| GitHub Copilot CLI | `copilot -p "<prompt>"` | GitHub docs describe interactive and programmatic modes, with prompt passed via `-p`. |

Detection-only tools until a safe headless adapter is confirmed: Crush, Kimi CLI, Factory Droid, Auggie, ForgeCode, Continue, Cline, Roo Code, Kilo Code, Kiro, Qoder, Trae, Windsurf, Amazon Q, iFlow, Lingma, CodeBuddy, and similar IDE-first or TUI-only agents.

Runner defaults:

- Per-tool timeout: 7200 seconds. Pass `--timeout <seconds>` for shorter or even longer passes.
- When invoking the runner from another tool or shell wrapper, make the outer timeout larger than the runner timeout; otherwise the wrapper may kill the shotgun run first.
- Final synthesis should include per-tool good/bad scorecards, including failure diagnostics for tools that returned no usable answer.

Primary docs:

- Codex: https://github.com/openai/codex
- Claude Code CLI reference: https://docs.claude.com/en/docs/claude-code/cli-reference
- Cursor CLI overview/reference: https://docs.cursor.com/en/cli/overview
- Antigravity CLI getting started: https://antigravity.google/docs/cli-getting-started
- OpenCode CLI: https://open-code.ai/en/docs/cli
- Pi quickstart/usage: https://pi.dev/docs/latest/quickstart and https://pi.dev/docs/latest/usage
- Gemini CLI headless mode: https://google-gemini.github.io/gemini-cli/docs/cli/headless.html
- Qwen Code CLI: https://qwenlm.github.io/qwen-code-docs/en/cli/index
- Aider options/chat modes: https://aider.chat/docs/config/options.html and https://aider.chat/docs/usage/modes.html
- Goose CLI commands: https://block.github.io/goose/docs/guides/goose-cli-commands/
- Amp manual: https://ampcode.com/manual
- GitHub Copilot CLI: https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli
