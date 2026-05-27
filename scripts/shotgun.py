#!/usr/bin/env python3
"""Fan out a research prompt to installed CLI coding agents."""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import json
import os
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


DEFAULT_TIMEOUT_SECONDS = 7200
CURSOR_COMPOSER_MODEL = "composer-2.5"


@dataclasses.dataclass(frozen=True)
class Attempt:
    argv: list[str]
    final_file: Path | None = None
    json_result_key: str | None = None


@dataclasses.dataclass(frozen=True)
class ToolSpec:
    name: str
    commands: tuple[str, ...]
    build: Callable[[str, str, Path, Path, int], list[Attempt]] | None
    known_paths: tuple[str, ...] = ()


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value)))


def find_executable(spec: ToolSpec) -> str | None:
    for command in spec.commands:
        found = shutil.which(command)
        if found:
            return found
    for candidate in spec.known_paths:
        path = expand_path(candidate)
        if path.exists() and path.is_file():
            return str(path)
    return None


def codex_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    final_file = tool_dir / "codex-final.txt"
    return [
        Attempt(
            [
                exe,
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--color",
                "never",
                "-c",
                'model_reasoning_effort="xhigh"',
                "-o",
                str(final_file),
                prompt,
            ],
            final_file,
        )
    ]


def claude_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [
        Attempt(
            [
                exe,
                "--print",
                "--no-session-persistence",
                "--permission-mode",
                "plan",
                "--effort",
                "high",
                "--output-format",
                "text",
                prompt,
            ]
        )
    ]


def cursor_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [
        Attempt(
            [
                exe,
                "--print",
                "--mode",
                "ask",
                "--model",
                CURSOR_COMPOSER_MODEL,
                "--output-format",
                "json",
                "--trust",
                "--workspace",
                str(cwd),
                prompt,
            ],
            json_result_key="result",
        )
        ,
        Attempt(
            [
                exe,
                "--print",
                "--mode",
                "ask",
                "--model",
                CURSOR_COMPOSER_MODEL,
                "--output-format",
                "text",
                "--trust",
                "--workspace",
                str(cwd),
                prompt,
            ]
        ),
        Attempt(
            [
                exe,
                "--print",
                "--mode",
                "ask",
                "--model",
                "auto",
                "--output-format",
                "json",
                "--trust",
                "--workspace",
                str(cwd),
                prompt,
            ],
            json_result_key="result",
        ),
    ]


def agy_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [
        Attempt([exe, "--log-file", str(tool_dir / "agy.log"), "--print", "--print-timeout", f"{timeout}s", prompt]),
        Attempt([exe, "--prompt", "--print-timeout", f"{timeout}s", prompt]),
    ]


def opencode_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [Attempt([exe, "run", prompt]), Attempt([exe, "-p", prompt, "-q"])]


def pi_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [
        Attempt([exe, "--tools", "read,grep,find,ls", "-p", prompt]),
        Attempt([exe, "-p", prompt]),
    ]


def simple_p_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [Attempt([exe, "-p", prompt])]


def qwen_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [Attempt([exe, "-p", prompt, "--output-format", "text"]), Attempt([exe, "-p", prompt])]


def aider_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [Attempt([exe, "--chat-mode", "ask", "--message", prompt, "--no-auto-commits"])]


def goose_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [
        Attempt([exe, "run", "--no-session", "-t", prompt, "-q", "--output-format", "text"]),
        Attempt([exe, "run", "--no-session", "--text", prompt, "-q", "--output-format", "text"]),
    ]


def amp_attempts(exe: str, prompt: str, cwd: Path, tool_dir: Path, timeout: int) -> list[Attempt]:
    return [Attempt([exe, "-x", prompt])]


SPECS: list[ToolSpec] = [
    ToolSpec("codex", ("codex",), codex_attempts),
    ToolSpec("claude", ("claude",), claude_attempts, ("%USERPROFILE%\\.local\\bin\\claude.exe",)),
    ToolSpec(
        "cursor",
        ("cursor-agent", "agent"),
        cursor_attempts,
        (
            "%LOCALAPPDATA%\\cursor-agent\\cursor-agent.cmd",
            "%LOCALAPPDATA%\\cursor-agent\\agent.cmd",
            "%LOCALAPPDATA%\\cursor-agent\\cursor-agent.ps1",
        ),
    ),
    ToolSpec("antigravity", ("agy",), agy_attempts, ("%LOCALAPPDATA%\\agy\\bin\\agy.exe",)),
    ToolSpec("opencode", ("opencode",), opencode_attempts),
    ToolSpec("pi", ("pi",), pi_attempts),
    ToolSpec("gemini", ("gemini",), simple_p_attempts),
    ToolSpec("qwen", ("qwen",), qwen_attempts),
    ToolSpec("aider", ("aider",), aider_attempts),
    ToolSpec("goose", ("goose",), goose_attempts),
    ToolSpec("amp", ("amp",), amp_attempts),
    ToolSpec("copilot", ("copilot",), simple_p_attempts),
    ToolSpec("crush", ("crush",), None),
    ToolSpec("kimi", ("kimi", "kimi-cli"), None),
    ToolSpec("factory-droid", ("droid", "factory"), None),
    ToolSpec("auggie", ("auggie",), None),
    ToolSpec("forgecode", ("forgecode", "forge"), None),
    ToolSpec("continue", ("continue", "cn"), None),
    ToolSpec("cline", ("cline",), None),
    ToolSpec("roo-code", ("roo", "roocode"), None),
    ToolSpec("kilo-code", ("kilo", "kilocode"), None),
    ToolSpec("kiro", ("kiro",), None),
    ToolSpec("qoder", ("qoder",), None),
    ToolSpec("trae", ("trae",), None),
    ToolSpec("windsurf", ("windsurf",), None),
    ToolSpec("amazon-q", ("q", "amazon-q"), None),
    ToolSpec("iflow", ("iflow",), None),
    ToolSpec("lingma", ("lingma",), None),
    ToolSpec("codebuddy", ("codebuddy",), None),
]


def one_line(text: str, limit: int = 220) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def read_text_if_present(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def extract_final_text(attempt: Attempt, stdout: str) -> str:
    file_text = read_text_if_present(attempt.final_file)
    if file_text:
        return file_text
    if attempt.json_result_key:
        try:
            payload = json.loads(stdout)
            value = payload.get(attempt.json_result_key)
            if isinstance(value, str):
                return value.strip()
        except json.JSONDecodeError:
            pass
    return stdout.strip()


def kill_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            text=True,
            capture_output=True,
            timeout=15,
        )
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)


def run_attempt(attempt: Attempt, cwd: Path, timeout: int) -> tuple[int | None, str, str, bool]:
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    start_new_session = os.name != "nt"
    process = subprocess.Popen(
        attempt.argv,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
        start_new_session=start_new_session,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_process_tree(process)
        stdout, stderr = process.communicate(timeout=30)
    return process.returncode, stdout or "", stderr or "", timed_out


def run_tool(spec: ToolSpec, exe: str, prompt: str, cwd: Path, out_dir: Path, timeout: int) -> dict:
    tool_dir = out_dir / "work" / spec.name
    tool_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / "outputs" / f"{spec.name}.txt"
    started = time.monotonic()
    attempts = spec.build(exe, prompt, cwd, tool_dir, timeout) if spec.build else []

    if not attempts:
        result = {
            "tool": spec.name,
            "executable": exe,
            "status": "detected-no-headless-adapter",
            "duration_seconds": 0.0,
            "output_file": None,
            "error": "Installed, but no documented safe headless adapter is configured.",
            "attempts": [],
        }
        return result

    attempt_records = []
    final_text = ""
    last_error = ""
    status = "failed"

    for attempt in attempts:
        attempt_no = len(attempt_records) + 1
        attempt_started = time.monotonic()
        command_record = {"argv": attempt.argv, "exit_code": None, "duration_seconds": None}
        try:
            returncode, stdout, stderr, timed_out = run_attempt(attempt, cwd, timeout)
            command_record["exit_code"] = returncode
            command_record["duration_seconds"] = round(time.monotonic() - attempt_started, 3)
            stdout_path = tool_dir / f"attempt-{attempt_no}-stdout.txt"
            stderr_path = tool_dir / f"attempt-{attempt_no}-stderr.txt"
            stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
            stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
            final_text = extract_final_text(attempt, stdout)
            last_error = stderr.strip()
            command_record["stdout_preview"] = one_line(stdout)
            command_record["stderr_preview"] = one_line(stderr)
            command_record["stdout_file"] = str(stdout_path)
            command_record["stderr_file"] = str(stderr_path)
            attempt_records.append(command_record)
            if timed_out and final_text:
                status = "timeout-with-output"
                last_error = f"timed out after {timeout}s, but a final/partial output was recovered"
                break
            if timed_out:
                status = "timeout"
                last_error = f"timed out after {timeout}s"
                break
            if returncode == 0 and final_text:
                prior_attempts = len(attempt_records) - 1
                status = "ok-after-fallback" if prior_attempts else "ok"
                last_error = (
                    f"succeeded after {prior_attempts} prior failed/empty attempt(s)"
                    if prior_attempts
                    else ""
                )
                break
            if returncode == 0 and not final_text:
                status = "empty"
                last_error = "exited 0 but produced no stdout/final output; likely auth, adapter, or CLI print-mode issue"
            if returncode not in (0, None) and not final_text:
                status = "failed"
                last_error = stderr.strip() or f"exited with code {returncode}"
        except Exception as exc:  # noqa: BLE001 - keep runner resilient across unknown CLIs.
            command_record["duration_seconds"] = round(time.monotonic() - attempt_started, 3)
            command_record["error"] = repr(exc)
            attempt_records.append(command_record)
            last_error = repr(exc)

    if final_text:
        output_file.write_text(final_text + "\n", encoding="utf-8")

    return {
        "tool": spec.name,
        "executable": exe,
        "status": status,
        "duration_seconds": round(time.monotonic() - started, 3),
        "output_file": str(output_file) if final_text else None,
        "error": last_error,
        "attempts": attempt_records,
    }


def detect_tools(include: set[str] | None, exclude: set[str]) -> list[tuple[ToolSpec, str | None]]:
    detected = []
    for spec in SPECS:
        if include and spec.name not in include:
            continue
        if spec.name in exclude:
            continue
        detected.append((spec, find_executable(spec)))
    return detected


def write_summary(out_dir: Path, prompt: str, records: list[dict], missing: list[str]) -> None:
    lines = [
        "# Shotgun Run",
        "",
        f"Created: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Prompt",
        "",
        "```text",
        prompt.strip(),
        "```",
        "",
        "## Results",
        "",
        "| Tool | Status | Duration | Output | Note |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for record in records:
        output = record.get("output_file") or ""
        note = one_line(record.get("error") or "")
        lines.append(
            f"| {record['tool']} | {record['status']} | {record.get('duration_seconds', 0)}s | {output} | {note} |"
        )
    if missing:
        lines.extend(["", "## Not Detected", "", ", ".join(missing)])
    lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fan out a prompt to installed CLI coding agents.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="Prompt to send to every supported installed agent.")
    source.add_argument("--prompt-file", type=Path, help="UTF-8 file containing the prompt.")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Working directory for agent runs.")
    parser.add_argument("--out-dir", type=Path, help="Output directory. Defaults to .shotgun-runs/<timestamp>.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per-tool timeout in seconds. Defaults to 7200 seconds for long research runs.",
    )
    parser.add_argument("--include", help="Comma-separated tool names to include.")
    parser.add_argument("--exclude", help="Comma-separated tool names to exclude.")
    parser.add_argument("--dry-run", action="store_true", help="Detect tools and print planned commands without running.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt
    cwd = args.cwd.resolve()
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out_dir = (args.out_dir or (cwd / ".shotgun-runs" / timestamp)).resolve()
    (out_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (out_dir / "work").mkdir(parents=True, exist_ok=True)
    (out_dir / "prompt.txt").write_text(prompt.strip() + "\n", encoding="utf-8")

    include = {x.strip() for x in args.include.split(",")} if args.include else None
    exclude = {x.strip() for x in args.exclude.split(",")} if args.exclude else set()
    detected = detect_tools(include, exclude)
    runnable = [(spec, exe) for spec, exe in detected if exe]
    missing = [spec.name for spec, exe in detected if not exe]

    if args.dry_run:
        records = []
        for spec, exe in runnable:
            attempts = spec.build(exe, prompt, cwd, out_dir / "work" / spec.name, args.timeout) if spec.build else []
            records.append(
                {
                    "tool": spec.name,
                    "executable": exe,
                    "status": "planned" if attempts else "detected-no-headless-adapter",
                    "attempts": [attempt.argv for attempt in attempts],
                }
            )
        print(json.dumps({"out_dir": str(out_dir), "detected": records, "missing": missing}, indent=2))
        return 0

    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(8, len(runnable)))) as pool:
        futures = {
            pool.submit(run_tool, spec, exe, prompt, cwd, out_dir, args.timeout): spec.name
            for spec, exe in runnable
        }
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())

    records.sort(key=lambda item: item["tool"])
    metadata = {
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "cwd": str(cwd),
        "timeout_seconds": args.timeout,
        "records": records,
        "missing": missing,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_summary(out_dir, prompt, records, missing)
    print(str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
