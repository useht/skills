#!/usr/bin/env python3
"""Rerun the plugin-eval-field-notes benchmark: the with/without arms and the document-control arm.

    python benchmarks/plugin-eval-field-notes/rerun.py source            # rebuild the control's source text -> rerun-out/source.md
    python benchmarks/plugin-eval-field-notes/rerun.py run all           # every arm on both sets (calls `claude plugin eval`, costs usage)
    python benchmarks/plugin-eval-field-notes/rerun.py run gate:control  # one arm: gate|confirm : with-without|control
    python benchmarks/plugin-eval-field-notes/rerun.py run all --dry-run # build the arm folders and print the commands, run nothing

Run from the repository root. Standard library only; needs `claude` (Claude Code) on PATH for `source` and `run`.

Arms, as measured on 2026-10-29 (Claude Code 2.1.312):
  with-without  the plugin in plugins/plugin-eval-field-notes, `claude plugin eval` default ablation (with and without arms)
  control       no plugin (`--ablation none` on an empty plugin folder); each prompt.md body gets the source text appended
                after a line `[참고 원문]` ("reference source"), exactly as in the measured runs
The source text is Anthropic's (docs page + CLI help), so it is not in this repository: `source` downloads the page and
captures the help output, lays them out as in the measured runs and compares the SHA-256 with the registered file.
A different hash means the docs or the CLI changed since 2026-10-28; the run still works, but it is not the same control.

Differences from the measured runs: plugin.json gained author/homepage/repository fields and the plugin folder a README and
LICENSE after the runs (the skill files are byte-identical, see prereg-sha256.txt); the measured runs also kept temp
folders to count skill invocations, which this script does not.

Results land in rerun-out/<set>-<arm>.json (raw `claude plugin eval --json`). This script does not compute intervals:
compare per-case scores with results/*.json, or pair them per case yourself (case-cluster bootstrap, see README.md).
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PLUGIN = REPO / "plugins" / "plugin-eval-field-notes"
OUT = REPO / "rerun-out"
SETS = {"gate": "gate-1-evals", "confirm": "conf-1-evals"}  # --eval-dir takes ASCII names only
ARMS = ("with-without", "control")

# As measured (README.md): answer model, judge, runs per case, concurrency. -j above 1 overcounts the judge cost share.
MODEL = "claude-sonnet-5-5"
JUDGE = "sonnet"
RUNS = "3"
JOBS = "8"

SOURCE_MARK = "[참고 원문]"
DOC_URL = "https://code.claude.com/docs/en/plugin-evals.md"
HELP_CMDS = ["plugin  --help", "plugin eval --help", "plugin eval init --help", "plugin validate --help", "plugin init --help",
             "plugin marketplace --help", "plugin marketplace add --help", "plugin tag --help", "plugin details --help"]
# The registered source file's header lines (our own notes, in Korean) — kept byte for byte so the hash can match.
HEAD1 = ("<!-- 원문 상대 팔이 요청 끝에 받는 공개 원문: Claude Code 공식 문서 'Test plugins with evals'(받은 날짜 2026-10-28, curl 원문 그대로)"
         "와 `claude plugin eval --help`·`claude plugin --help` 출력(2.1.312) — 출처.md -->")
HEAD2 = f"<!-- 주소: {DOC_URL} · 받은 날짜: 2026-10-28 · curl 원문 그대로 -->"
HEAD3 = ("<!-- 명령: claude plugin --help / claude plugin eval --help / claude plugin eval init --help / claude plugin validate --help"
         " / claude plugin init --help / claude plugin marketplace --help / claude plugin tag --help · Claude Code 2.1.312 · 받은 날짜:"
         " 2026-10-28 · 이 컨테이너 /opt/node22/bin/claude -->")
# SHA-256 of the registered source text (LF line endings) that the measured control arm received.
SOURCE_SHA256 = "0d6fa3ceb3ae24e8513d116f6b6b09128aaf029178e8b2eaf9b3e9c2317df501"


def layout(doc: str, helps: dict) -> str:
    """Lay the page and the help outputs out as in the registered file."""
    parts = [HEAD1, HEAD2, doc.replace("\r\n", "\n").rstrip("\n"), "", "", HEAD3, ""]
    for cmd in HELP_CMDS:
        parts += [f"## $ claude {cmd}", "```text", helps[cmd].replace("\r\n", "\n").rstrip("\n"), "```", ""]
    return "\n".join(parts)


def sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def claude_bin() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise SystemExit("`claude` (Claude Code) is not on PATH")
    return exe


def build_source(fetch=None, helper=None) -> Path:
    # the docs host refuses urllib's default agent (HTTP 403); the registered copy was fetched with curl
    fetch = fetch or (lambda url: urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0", "Accept": "*/*"}),
                                                         timeout=60).read().decode("utf-8"))
    helper = helper or (lambda cmd: subprocess.run([claude_bin(), *cmd.split()], capture_output=True, text=True,
                                                   encoding="utf-8", errors="replace").stdout)
    text = layout(fetch(DOC_URL), {c: helper(c) for c in HELP_CMDS})
    OUT.mkdir(exist_ok=True)
    p = OUT / "source.md"
    p.write_text(text, encoding="utf-8", newline="\n")
    got = sha(text)
    print(f"source: {p} ({len(text.encode('utf-8')):,} bytes) sha256 {got[:16]}…",
          "= registered" if got == SOURCE_SHA256 else f"!= registered {SOURCE_SHA256[:16]}… (docs or CLI changed since 2026-10-28)")
    return p


def split_front(text: str):
    m = re.match(r"^(---\n.*?\n---\n?)(.*)$", text.replace("\r\n", "\n"), re.S)
    return (m.group(1), m.group(2)) if m else ("", text.replace("\r\n", "\n"))


def arm_folder(sett: str, arm: str, source: str | None) -> tuple[Path, list[str]]:
    """Temporary plugin folder for one arm, and the extra flags. The repository is never modified."""
    base = Path(tempfile.mkdtemp(prefix="pefn-arm-")) / "plugin"
    cases = HERE / "cases" / sett
    if arm == "with-without":
        shutil.copytree(PLUGIN, base, ignore=shutil.ignore_patterns("evals"))
        shutil.copytree(cases, base / SETS[sett])
        return base, ["--eval-dir", SETS[sett]]
    base.mkdir()
    shutil.copytree(cases, base / "evals")
    for p in sorted((base / "evals").glob("*/prompt.md")):
        head, body = split_front(p.read_text(encoding="utf-8"))
        p.write_text(head + body.rstrip("\n") + f"\n\n{SOURCE_MARK}\n{source.strip()}\n", encoding="utf-8", newline="\n")
    return base, ["--ablation", "none"]


def eval_cmd(target: Path, extra: list[str], out: Path, exe: str) -> list[str]:
    return [exe, "plugin", "eval", str(target), *extra, "--runs", RUNS, "--model", MODEL, "--judge-model", JUDGE,
            "-j", JOBS, "--no-publish", "--trust-plugin", "--output-dir", str(out.with_suffix("")), "--json", str(out)]


def run(which: str, dry: bool, source_file: Path | None, runner=None) -> list[list[str]]:
    jobs = [(s, a) for s in SETS for a in ARMS] if which == "all" else [tuple(which.split(":"))]
    for s, a in jobs:
        if s not in SETS or a not in ARMS:
            raise SystemExit(f"unknown arm {s}:{a} — use all or <{'|'.join(SETS)}>:<{'|'.join(ARMS)}>")
    source = None
    if any(a == "control" for _, a in jobs):
        sf = source_file or OUT / "source.md"
        if not sf.is_file() and dry:
            source = "(source text: run `rerun.py source` before a real run)"
            print(f"note: {sf} missing — dry run uses a placeholder for the control's source text")
        elif not sf.is_file():
            raise SystemExit(f"{sf} missing — run `rerun.py source` first (or pass --source <file>)")
        else:
            source = sf.read_text(encoding="utf-8")
        if sf.is_file() and sha(source) != SOURCE_SHA256:
            print(f"note: {sf.name} differs from the registered source text — this is not the measured control")
    exe = "claude" if dry else claude_bin()
    cmds = []
    for s, a in jobs:
        target, extra = arm_folder(s, a, source)
        out = OUT / f"{s}-{a}.json"
        cmd = eval_cmd(target, extra, out, exe)
        cmds.append(cmd)
        n = len(list((target / extra[1] if extra[0] == "--eval-dir" else target / "evals").glob("*/prompt.md")))
        print(f"{s}:{a} — {n} cases\n  " + " ".join(cmd))
        try:
            if not dry:
                OUT.mkdir(exist_ok=True)
                r = (runner or subprocess.run)(cmd)
                if getattr(r, "returncode", 0) not in (0, 1):  # 1 = some case failed; the JSON is still written
                    raise SystemExit(f"claude plugin eval exited {r.returncode}")
        finally:
            shutil.rmtree(target.parent, ignore_errors=True)
    return cmds


def main(argv=None) -> int:
    for st in (sys.stdout, sys.stderr):  # Windows consoles default to a legacy code page
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("source", help="rebuild the control's source text")
    r = sub.add_parser("run", help="run arms")
    r.add_argument("which", help="all, or <gate|confirm>:<with-without|control>")
    r.add_argument("--dry-run", action="store_true", help="build the arm folders and print the commands only")
    r.add_argument("--source", type=Path, help="source text file for the control arm (default rerun-out/source.md)")
    a = ap.parse_args(argv)
    if a.cmd == "source":
        build_source()
    else:
        run(a.which, a.dry_run, a.source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
