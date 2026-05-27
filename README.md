do you hate having unspent tokens? Boy do I have the skill for you.

# Shotgun Research Skill

`/shotgun` fans your research prompt out to every coding-agent CLI it can find, waits a generously silly amount of time, then asks Codex to collate the answers into one report. It is for those moments when one agent is good, but four agents arguing in your terminal feels better.

It currently knows how to run or detect Codex, Claude Code, Cursor Agent, Antigravity `agy`, OpenCode, Pi, Gemini CLI, Qwen Code, Aider, Goose, Amp, Copilot CLI, and a pile of other agent-shaped things. It records what worked, what failed, what timed out, and what came back empty, because silence from a CLI is still data if you squint.

## What It Does

- Discovers installed coding-agent CLIs from PATH and common Windows install paths.
- Sends each supported tool the same optimized research prompt.
- Uses read-only modes by default.
- Uses high/extra-high reasoning when a CLI exposes it.
- Gives each tool a very lax default timeout: 7200 seconds per agent.
- Captures stdout, stderr, exact commands, exit codes, and recovered final files.
- Produces a run folder under `.shotgun-runs/<timestamp>/`.
- Guides the final synthesis to include the good and bad from each model before the merged answer.

## Install With Codex, Claude, Antigravity, Cursor, Whatever

Copy this prompt into your agent of choice:

```text
Install the Codex skill from https://github.com/DanMcInerney/shotgun-research-skill.

Clone the repo into a temporary location, then install it as a Codex skill named "shotgun" under my Codex skills directory:
- Windows: %USERPROFILE%\.codex\skills\shotgun
- macOS/Linux: ~/.codex/skills/shotgun

The installed skill folder should contain SKILL.md, scripts/shotgun.py, references/cli-tools.md, agents/openai.yaml, and README.md if present. Do not copy .git or __pycache__. After installing, run a quick validation if available and show me the installed path.
```

## Manual Install

Windows PowerShell:

```powershell
git clone https://github.com/DanMcInerney/shotgun-research-skill.git "$env:USERPROFILE\.codex\skills\shotgun"
```

macOS/Linux:

```bash
git clone https://github.com/DanMcInerney/shotgun-research-skill.git ~/.codex/skills/shotgun
```

Then restart Codex or start a fresh thread so the skill list reloads.

## Use It

```text
/shotgun who is the best BJJ fighter in the world right now
```

Or:

```text
/shotgun research whether this migration plan misses any production risks
```

For long prompts, the skill uses `--prompt-file` internally so your shell does not turn your careful research request into confetti.

## Notes

Some CLIs are weird. Antigravity may authenticate and generate internally while returning empty stdout. Cursor may reject named models on some plans and fall back to Auto. Codex may write useful final output even if the wrapper gets impatient. The runner records all of that instead of pretending everything is fine.

Dumb... but effective
