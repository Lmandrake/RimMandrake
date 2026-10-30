#!/usr/bin/env python3
"""Ask GPT (codex.exe exec) a question about some files, from any clone.

    python3 src/RimMandrake/Utils/gpt_consult.py "Review this plan for holes" -f design/x.md -f src/y.py
    python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file ask.md -f a.py --out review.md

The named files are INLINED into the prompt (codex's sandboxed file reads are flaky, and it hangs
reading \\\\wsl.localhost paths), and codex runs with its cwd in
D:\\ClaudeWork\\rimmandrake\\scratch\\codex\\consult-<ts>\\ (it fails from an ext4 cwd) — git_workflow_plan_2026-10-01.md
§2.3. The prompt goes in on stdin (no Windows command-line length limit). The answer is printed,
and written to --out when given. Default model: gpt-6.1-sol at high effort (owner,
2026-10-02; CODEX_CONSULT_MODEL overrides). Art (codex_image.py) stays on gpt-5.5 — a separate default.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONSULT_MODEL = os.environ.get("CODEX_CONSULT_MODEL", "gpt-6.1-sol")
sys.path.insert(0, str(ROOT / "skills" / "generating-images" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))          # review_identity (job receipts)
import codex_image  # noqa: E402  (find_codex_cli, wsl_to_win, DEFAULT_MODEL, CODEX_SCRATCH)


def build_prompt(question, files, inlined=None):
    """The prompt text. When `inlined` is a list, each file's (shown path, exact bytes inlined) is appended to it: the
    job receipt hashes those bytes (review_identity.write_receipt)."""
    parts = [question.strip(), ""]
    if files:
        parts.append("The files below are inlined in full; do not try to open them from disk.")
    for f in files:
        p = Path(f)
        try:
            raw = p.read_bytes()
        except OSError as e:
            sys.exit("cannot read %s: %s" % (f, e))
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p
        text = raw.decode("utf-8", errors="replace")
        if inlined is not None:
            inlined.append((Path(shown).as_posix(), raw))
        parts += ["", "===== FILE: %s =====" % shown, text.rstrip("\n"), "===== END FILE: %s =====" % shown]
    return "\n".join(parts) + "\n"


TOKENS_RE = re.compile(r"tokens used\s*[:\n]\s*([0-9][0-9,]*)", re.I)


def real_tokens(codex_log_text):
    """The real 'tokens used' figure codex prints (last one wins), or None."""
    m = TOKENS_RE.findall(codex_log_text or "")
    return int(m[-1].replace(",", "")) if m else None


# --lockdown (ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME): every tool-bearing feature of codex-cli 0.164 (`codex features
# list`, read 2026-10-30). code_mode_host is the `text(await tools.exec_command(...))` path the arena judge used.
LOCKDOWN_FEATURES = ("shell_tool", "unified_exec", "code_mode_host", "browser_use", "browser_use_external",
                     "in_app_browser", "computer_use", "apps", "plugins", "multi_agent", "image_generation",
                     "view_image", "hooks", "skill_search", "tool_suggest", "memories")
LOCKDOWN_ARGS = ["--ephemeral", "--ignore-rules", "--strict-config", "-c", 'web_search="disabled"'] + \
    [x for f in LOCKDOWN_FEATURES for x in ("--disable", f)]
REFUSED_TOOL_RE = re.compile(r"tools::router: error=")


def events_tokens(events_text):
    """Real token use from a --json event stream: the last turn.completed usage (input + output), or None."""
    tok = None
    for line in (events_text or "").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("type") == "turn.completed" and isinstance(ev.get("usage"), dict):
            u = ev["usage"]
            tok = int(u.get("input_tokens") or 0) + int(u.get("output_tokens") or 0)
    return tok


def _log_call(job, model, prompt, answer_text, rc, codex_log_text=None, tokens=None):
    """One record per call in the arm-metering log (gpt_call_log: atomic file-per-call on drvfs), tagged from
    RM_ARM (absent -> arm null = flagged UNTAGGED by spend_census). tokens_used is the REAL codex figure when the
    codex log has it; in/out_tok_est are chars/4 ESTIMATES kept as a labelled fallback. Never fails the consult."""
    try:
        import gpt_call_log
        rec = {"t": time.time(), "arm": os.environ.get("RM_ARM") or None, "job": job, "model": model, "rc": rc,
               "in_tok_est": len(prompt) // 4, "out_tok_est": len(answer_text) // 4,
               "tokens_used": tokens if tokens is not None else real_tokens(codex_log_text)}
        gpt_call_log.write_record(rec)
    except Exception as e:                                  # noqa: BLE001
        print("[consult] WARN: call not metered: %s" % e, file=sys.stderr)


def _receipt(job, model, answered, inlined, rc):
    """One mac'd receipt per job, so a code-review mark-clean can name this job as its reviewer
    (code_review_status mark-clean --gpt-job). A receipt that cannot be written never fails the consult."""
    try:
        import review_identity
        review_identity.write_receipt(job, model, answered, inlined, rc=rc)
        print("[consult] receipt job %s" % job, file=sys.stderr)
    except Exception as e:                                  # noqa: BLE001 -- the answer matters more than the receipt
        print("[consult] WARN: no receipt written for %s: %s" % (job, e), file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question", nargs="?", help="the question (or use --prompt-file)")
    ap.add_argument("--prompt-file", help="read the question from this file")
    ap.add_argument("-f", "--file", action="append", default=[], help="inline this file; repeatable")
    ap.add_argument("-i", "--image", action="append", default=[],
                    help="attach this image (PNG/JPG) for GPT to look at; repeatable. Copied into the job dir first.")
    ap.add_argument("--out", help="also write the answer here")
    ap.add_argument("-m", "--model", default=DEFAULT_CONSULT_MODEL)
    ap.add_argument("--effort", default="high", help="model_reasoning_effort (default high)")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--keep", action="store_true", help="keep the scratch job dir")
    ap.add_argument("--codex-home", help="run codex with this CODEX_HOME (must already hold a login; never seeded here)")
    ap.add_argument("--lockdown", action="store_true",
                    help="no tools: --ephemeral, every tool feature disabled, web search off, strict config")
    ap.add_argument("--events", help="run codex --json and write its event stream (the transcript) here, plus "
                                     "<EVENTS>.meta.json naming the job dir and home")
    a = ap.parse_args(argv)
    env = None
    if a.codex_home:
        home = Path(a.codex_home)
        if not (home / "auth.json").is_file():
            sys.exit("--codex-home %s has no auth.json (set it up first; gpt_consult never seeds a home)" % home)
        env = codex_image.child_env(home)
    if a.prompt_file:
        question = Path(a.prompt_file).read_text()
    elif a.question:
        question = a.question
    else:
        ap.error("give a question or --prompt-file")
    inlined = []
    prompt = build_prompt(question, a.file, inlined)

    job = codex_image.CODEX_SCRATCH / ("consult-%s-%d" % (time.strftime("%Y%m%d-%H%M%S"), os.getpid()))
    job.mkdir(parents=True, exist_ok=True)
    (job / "prompt.md").write_text(prompt)
    answer = job / "answer.md"
    cmd = [str(codex_image.find_codex_cli()), "exec", "--sandbox", "read-only",
           "--skip-git-repo-check", "-o", codex_image.wsl_to_win(answer),
           "-c", 'model_reasoning_effort="%s"' % a.effort]
    if a.model and a.model != "inherit":
        cmd += ["-m", a.model]
    if a.lockdown:
        cmd += LOCKDOWN_ARGS + ["-C", codex_image.wsl_to_win(job)]
    if a.events:
        cmd.append("--json")
    for i, img in enumerate(a.image):                       # codex reads Windows paths; stage beside the prompt
        src = Path(img)
        if not src.is_file():
            sys.exit("cannot read image %s" % img)
        dst = job / ("img%02d_%s" % (i, src.name))
        shutil.copyfile(src, dst)
        cmd += ["-i", codex_image.wsl_to_win(dst)]
    if a.image:
        cmd.append("--")                                    # -i is VARIADIC: without this it eats the "-" below
    cmd.append("-")                                         # prompt from stdin
    print("[consult] %d chars, %d file(s), %d image(s), model %s, job %s" % (
        len(prompt), len(a.file), len(a.image), a.model, codex_image.wsl_to_win(job)), file=sys.stderr)
    started = time.time()
    events = Path(a.events) if a.events else None
    if events:
        events.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(job / "prompt.md", "rb") as fin, open(job / "codex.log", "wb") as log, \
                (open(events, "wb") if events else open(os.devnull, "wb")) as evf:
            rc = subprocess.run(cmd, cwd=str(job), stdin=fin, stdout=evf if events else log,
                                stderr=log if events else subprocess.STDOUT, timeout=a.timeout, env=env).returncode
    except subprocess.TimeoutExpired:
        rc = 124
    answered = answer.is_file() and bool(answer.read_text().strip())
    _receipt(job.name, a.model, answered, inlined, rc)
    try:
        clog = (job / "codex.log").read_text(errors="replace")
    except OSError:
        clog = None
    etok = None
    if events:
        etok = events_tokens(events.read_text(encoding="utf-8", errors="replace") if events.is_file() else "")
        meta = {"job_win": codex_image.wsl_to_win(job), "job": str(job), "rc": rc, "lockdown": bool(a.lockdown),
                "codex_home_win": env["CODEX_HOME"] if env else None,
                "refused_tool_calls": len(REFUSED_TOOL_RE.findall(clog or ""))}
        Path(str(events) + ".meta.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    _log_call(job.name, a.model, prompt, answer.read_text() if answered else "", rc, clog, etok)
    if not answered:
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
