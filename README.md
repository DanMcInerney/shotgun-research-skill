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

## Install With Codex, Claude Code, Cursor Agent, Antigravity, Whatever

This is a Codex skill, but the installer prompt is agent-neutral. Paste it into Codex, Claude Code, Cursor Agent, Antigravity, or whatever terminal-driving assistant you trust with a `git clone`.

```text
You are Codex, Claude Code, Cursor Agent, Antigravity, or another coding-agent CLI.

Task: install the /shotgun research skill from:
https://github.com/DanMcInerney/shotgun-research-skill

Install it as a Codex skill folder named "shotgun":
- Windows PowerShell target: $env:USERPROFILE\.codex\skills\shotgun
- macOS/Linux target: ~/.codex/skills/shotgun

Use a temporary clone or direct git clone into the target. The final installed folder should contain:
- SKILL.md
- scripts/shotgun.py
- references/cli-tools.md
- agents/openai.yaml
- README.md

Do not copy .git, __pycache__, or .shotgun-runs into the installed skill folder unless you used git clone directly into the target. If the target already exists, update it carefully without deleting unrelated user changes. After installing, show me the install path and run a quick syntax/validation check if the local environment supports it.
```

## Manual Install

Windows PowerShell:

```powershell
$target = "$env:USERPROFILE\.codex\skills\shotgun"
if (Test-Path $target) {
  git -C $target pull
} else {
  git clone https://github.com/DanMcInerney/shotgun-research-skill.git $target
}
```

macOS/Linux:

```bash
target="$HOME/.codex/skills/shotgun"
if [ -d "$target/.git" ]; then
  git -C "$target" pull
else
  git clone https://github.com/DanMcInerney/shotgun-research-skill.git "$target"
fi
```

Then restart Codex or start a fresh thread so the skill list reloads.

## Use It

```text
/shotgun why is clankerfights.ai the funniest AI site on the internet
```

Or:

```text
/shotgun research whether this migration plan misses any production risks
```

For long prompts, the skill uses `--prompt-file` internally so your shell does not turn your careful research request into confetti.

## Notes

Some CLIs are weird. Antigravity may authenticate and generate internally while returning empty stdout. Cursor may reject named models on some plans and fall back to Auto. Codex may write useful final output even if the wrapper gets impatient. The runner records all of that instead of pretending everything is fine.

Dumb... but effective
