#!/usr/bin/env python3
"""Ask GPT (codex.exe exec) a question about some files, from any clone.

    python3 src/RimMandrake/Utils/gpt_consult.py "Review this plan for holes" -f design/x.md -f src/y.py
    python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file ask.md -f a.py --out review.md

The named files are INLINED into the prompt (codex's sandboxed file reads are flaky, and it hangs
reading \\\\wsl.localhost paths), and codex runs with its cwd in
D:\\Luke\\dev\\_rmscratch\\codex\\consult-<ts>\\ (it fails from an ext4 cwd) — git_workflow_plan_2026-10-01.md
§2.3. The prompt goes in on stdin (no Windows command-line length limit). The answer is printed,
and written to --out when given. Default model: gpt-5.5 (CODEX_MODEL overrides; the config.toml
default has been a model this ChatGPT account cannot run).
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "generating-images" / "scripts"))
import codex_image  # noqa: E402  (find_codex_cli, wsl_to_win, DEFAULT_MODEL, CODEX_SCRATCH)


def build_prompt(question, files):
    parts = [question.strip(), ""]
    if files:
        parts.append("The files below are inlined in full; do not try to open them from disk.")
    for f in files:
        p = Path(f)
        try:
            text = p.read_text(errors="replace")
        except OSError as e:
            sys.exit("cannot read %s: %s" % (f, e))
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p
        parts += ["", "===== FILE: %s =====" % shown, text.rstrip("\n"), "===== END FILE: %s =====" % shown]
    return "\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question", nargs="?", help="the question (or use --prompt-file)")
    ap.add_argument("--prompt-file", help="read the question from this file")
    ap.add_argument("-f", "--file", action="append", default=[], help="inline this file; repeatable")
    ap.add_argument("--out", help="also write the answer here")
    ap.add_argument("-m", "--model", default=codex_image.DEFAULT_MODEL)
    ap.add_argument("--effort", default="high", help="model_reasoning_effort (default high)")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--keep", action="store_true", help="keep the scratch job dir")
    a = ap.parse_args(argv)
    if a.prompt_file:
        question = Path(a.prompt_file).read_text()
    elif a.question:
        question = a.question
    else:
        ap.error("give a question or --prompt-file")
    prompt = build_prompt(question, a.file)

    job = codex_image.CODEX_SCRATCH / ("consult-%s-%d" % (time.strftime("%Y%m%d-%H%M%S"), os.getpid()))
    job.mkdir(parents=True, exist_ok=True)
    (job / "prompt.md").write_text(prompt)
    answer = job / "answer.md"
    cmd = [str(codex_image.find_codex_cli()), "exec", "--sandbox", "read-only",
           "--skip-git-repo-check", "-o", codex_image.wsl_to_win(answer),
           "-c", 'model_reasoning_effort="%s"' % a.effort]
    if a.model and a.model != "inherit":
        cmd += ["-m", a.model]
    cmd.append("-")                                         # prompt from stdin
    print("[consult] %d chars, %d file(s), model %s, job %s" % (
        len(prompt), len(a.file), a.model, codex_image.wsl_to_win(job)), file=sys.stderr)
    started = time.time()
    try:
        with open(job / "prompt.md", "rb") as fin, open(job / "codex.log", "wb") as log:
            rc = subprocess.run(cmd, cwd=str(job), stdin=fin, stdout=log, stderr=subprocess.STDOUT,
                                timeout=a.timeout).returncode
    except subprocess.TimeoutExpired:
        rc = 124
    if not answer.is_file() or not answer.read_text().strip():
        tail = (job / "codex.log").read_text(errors="replace")[-2000:]
        print("ERROR: no answer (exit %d after %.0fs). Job kept: %s\n%s" % (
            rc, time.time() - started, job, tail), file=sys.stderr)
        return 1
    text = answer.read_text()
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text)
    print(text)
    print("[consult] answered in %.0fs" % (time.time() - started), file=sys.stderr)
    if not a.keep:
        shutil.rmtree(job, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
