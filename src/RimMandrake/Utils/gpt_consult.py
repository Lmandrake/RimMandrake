#!/usr/bin/env python3
"""Ask GPT (codex exec) a question about some files, from any clone.

    python3 src/RimMandrake/Utils/gpt_consult.py "Review this plan for holes" -f design/x.md -f src/y.py
    python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file ask.md -f a.py --out review.md

The named files are inlined into the prompt. On Archmagi/WSL the Linux CLI is the default;
--codex win (or RM_CODEX_SIDE=win) selects Windows with drive-local staging and Windows paths.
The prompt goes on stdin. CODEX_HOME defaults to the selected runtime's login; --codex-home
uses an existing isolated login. Default model: gpt-6.1-sol, high effort (CODEX_CONSULT_MODEL overrides).

Every call is metered in gpt_call_log (job, model, rc, real tokens, seconds, files inlined, and its review ROUND:
`--round NAME` or $RM_CONSULT_ROUND). One round = one review pass over one subject; give every call of that pass the
same name, record what it found with `gpt_consult_rounds.py yield`, and `gpt_consult_rounds.py report` prints cost and
yield per round (GPT_CONSULT_MEASURE_COST_UNLOGGED).

Every call first passes codex_advice.gate (slot_allocator's Codex advice): on HOLD only a call given
`--required "<rule that requires this review>"` (or env RM_CODEX_REQUIRED) runs, exit 4 otherwise; on EXHAUSTED
every call is refused, exit 5. No Claude fallback (owner routing ruling 2026-10-28).

🔴 NO ANSWER IS NEVER EXIT 0, AND EVERY KIND OF NO-ANSWER HAS ITS OWN CODE (owner, 2026-11-17: "make that
outcome intentionally different than no failure somehow... we must not suffer such errors"). The codes are
Dispatch's, so one taxonomy covers both consult routes (providers/chatgpt/bin/codex_worker.py EXIT_CODES):

    0   an answer arrived and is non-empty
    4   Codex advice says HOLD and this call was not --required
    5   Codex advice says EXHAUSTED
    20  AUTH: no usable login (no CODEX_HOME, no CLI, 401/invalid_grant)   -> a human logs in
    21  ALLOWANCE: usage limit, 429, quota                                 -> wait for the reset
    22  TRANSPORT: the route is broken (no interpreter, bad flag, 400 model_not_found, container down)
    23  DEADLINE: the call timed out
    1   no answer, cause unclassified (the catch-all; it means READ THE LOG, not "nothing to say")

The last line of stderr is always `[consult] VERDICT=<name> exit=<n>`, so a caller that captured only
stderr can still tell an answer from a wall. Measured 2026-11-17: an EnvError here printed a traceback,
wrote no --out file, and the CALLER's `cmd > log 2>&1; echo` chain reported 0 — the exit status of the
last command in the chain, not of the consult. A verdict line in the output survives that mistake;
an exit code alone does not.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONSULT_MODEL = os.environ.get("CODEX_CONSULT_MODEL", "gpt-6.1-sol")

# One taxonomy with Dispatch (providers/chatgpt/bin/codex_worker.py EXIT_CODES), so a caller that knows one
# route knows both. The markers are matched against the codex log, lower-cased.
EXIT_AUTH, EXIT_ALLOWANCE, EXIT_TRANSPORT, EXIT_DEADLINE, EXIT_UNCLASSIFIED = 20, 21, 22, 23, 1
AUTH_MARKERS = ("401", "unauthorized", "not logged in", "refresh token", "token expired", "please log in",
                "login again", "re-authenticate", "invalid_grant", "403 forbidden", "auth_required",
                "cannot find codex_home", "cannot find codex.exe")
ALLOWANCE_MARKERS = ("429", "usage limit", "rate limit", "quota", "limit reached", "too many requests",
                     "usage_limit", "insufficient_quota", "purchase more credits")
TRANSPORT_MARKERS = ("model_not_found", "not supported when using codex", "invalid_request_error",
                     "not inside a trusted directory", "no such file or directory", "connection refused",
                     "cannot connect to the docker daemon", "enverror", "traceback (most recent call last)")
# An answer that is only the model saying it could not read or could not comply is NOT an answer. Measured
# 2026-11-17: a mounted-packet run returned 331 bytes of "I'm blocked by the session's tool access... I
# haven't read them and won't invent findings", and a non-empty check called that a success.
REFUSAL_MARKERS = ("i cannot read", "i can't read", "unable to read", "i haven't read",
                   "i have not read", "no filesystem-reading", "please attach or paste",
                   "i'm blocked by", "i am blocked by", "cannot access the files")
REFUSAL_MAX_CHARS = 2000        # a real review is long; a refusal is short. Only applied with a marker.


def classify_failure(log_text, rc):
    """-> (exit code, VERDICT name) for a call that produced no usable answer. Never 0."""
    t = (log_text or "").lower()
    if rc == 124:
        return EXIT_DEADLINE, "DEADLINE"
    for markers, code, name in ((ALLOWANCE_MARKERS, EXIT_ALLOWANCE, "ALLOWANCE"),
                                (AUTH_MARKERS, EXIT_AUTH, "AUTH"),
                                (TRANSPORT_MARKERS, EXIT_TRANSPORT, "TRANSPORT")):
        if any(m in t for m in markers):
            return code, name
    return EXIT_UNCLASSIFIED, "NO_ANSWER_UNCLASSIFIED"


def refusal_in(text):
    """-> the marker a short answer refused with, or None. A long answer is never read as a refusal: a real
    review may quote the words 'I cannot read' while reviewing something."""
    t = (text or "").strip()
    if len(t) > REFUSAL_MAX_CHARS:
        return None
    low = t.lower()
    return next((m for m in REFUSAL_MARKERS if m in low), None)


def verdict(name, code):
    """The last line of stderr on every path, so a caller that captured only the output can still tell an
    answer from a wall (owner, 2026-11-17)."""
    print("[consult] VERDICT=%s exit=%d" % (name, code), file=sys.stderr, flush=True)
sys.path.insert(0, str(ROOT / "skills" / "generating-images" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))          # review_identity (job receipts)
import codex_image  # noqa: E402  (find_codex_cli, wsl_to_win, DEFAULT_MODEL, CODEX_SCRATCH)
import codex_advice  # noqa: E402  (the Codex HOLD/EXHAUSTED gate)


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


ROUND_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}\Z")


def _log_call(job, model, prompt, answer_text, rc, codex_log_text=None, tokens=None, round_name=None, secs=None,
              files=None):
    """One record per call in the arm-metering log (gpt_call_log: atomic file-per-call on drvfs), tagged from
    RM_ARM (absent -> arm null = flagged UNTAGGED by spend_census). tokens_used is the REAL codex figure when the
    codex log has it; in/out_tok_est are chars/4 ESTIMATES kept as a labelled fallback. Never fails the consult."""
    try:
        import gpt_call_log
        rec = {"t": time.time(), "arm": os.environ.get("RM_ARM") or None, "job": job, "model": model, "rc": rc,
               "in_tok_est": len(prompt) // 4, "out_tok_est": len(answer_text) // 4,
               "tokens_used": tokens if tokens is not None else real_tokens(codex_log_text),
               "round": round_name or None, "secs": None if secs is None else round(secs, 1),
               "answered": bool(answer_text.strip()), "files": list(files or [])}
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
    ap.add_argument("--round", default=os.environ.get("RM_CONSULT_ROUND") or None,
                    help="review round this call belongs to (default $RM_CONSULT_ROUND); metered per round, see "
                         "gpt_consult_rounds.py")
    ap.add_argument("-m", "--model", default=DEFAULT_CONSULT_MODEL)
    ap.add_argument("--effort", default="high", help="model_reasoning_effort (default high)")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--keep", action="store_true", help="keep the scratch job dir")
    ap.add_argument("--codex", choices=("wsl", "win"), help="override RM_CODEX_SIDE (Archmagi/WSL default: wsl)")
    ap.add_argument("--codex-home", help="run codex with this CODEX_HOME (must already hold a login; never seeded here)")
    ap.add_argument("--lockdown", action="store_true",
                    help="no tools: --ephemeral, every tool feature disabled, web search off, strict config")
    ap.add_argument("--events", help="run codex --json and write its event stream (the transcript) here, plus "
                                     "<EVENTS>.meta.json naming the job dir and home")
    ap.add_argument("--required", help="the rule that requires this review round: lets it run while the Codex "
                                       "advice is HOLD (never while EXHAUSTED)")
    a = ap.parse_args(argv)
    codex_image.select_codex(a.codex)
    if a.round is not None and not ROUND_RE.match(a.round):
        ap.error("--round %r: 1-80 chars of A-Z a-z 0-9 _ . : - (starting alphanumeric)" % a.round)
    refused = codex_advice.gate("gpt_consult", a.required)
    if refused:
        return refused
    env = codex_image.child_env(codex_image.base_codex_home())
    if a.codex_home:
        home = Path(a.codex_home).expanduser().resolve()
        if not (home / "auth.json").is_file():
            sys.exit("--codex-home %s has no auth.json (set it up first; gpt_consult never seeds a home)" % home)
        env = codex_image.child_env(home)
    if a.prompt_file:
        question = Path(a.prompt_file).read_text(encoding="utf-8")
    elif a.question:
        question = a.question
    else:
        ap.error("give a question or --prompt-file")
    inlined = []
    prompt = build_prompt(question, a.file, inlined)

    job = codex_image.CODEX_SCRATCH / ("consult-%s-%d-%s" % (time.strftime("%Y%m%d-%H%M%S"), os.getpid(),
                                                              uuid.uuid4().hex[:6]))   # unique per call, not per pid+s
    job.mkdir(parents=True, exist_ok=False)
    (job / "prompt.md").write_text(prompt, encoding="utf-8")
    answer = job / "answer.md"
    cmd = [str(codex_image.find_codex_cli()), "exec", "--sandbox", "read-only",
           "--skip-git-repo-check", "-o", codex_image.codex_path(answer),
           "-c", 'model_reasoning_effort="%s"' % a.effort]
    if a.model and a.model != "inherit":
        cmd += ["-m", a.model]
    if a.lockdown:
        cmd += LOCKDOWN_ARGS + ["-C", codex_image.codex_path(job)]
    if a.events:
        cmd.append("--json")
    for i, img in enumerate(a.image):                       # codex reads Windows paths; stage beside the prompt
        src = Path(img)
        if not src.is_file():
            sys.exit("cannot read image %s" % img)
        dst = job / ("img%02d_%s" % (i, src.name))
        shutil.copyfile(src, dst)
        cmd += ["-i", codex_image.codex_path(dst)]
    if a.image:
        cmd.append("--")                                    # -i is VARIADIC: without this it eats the "-" below
    cmd.append("-")                                         # prompt from stdin
    print("[consult] %d chars, %d file(s), %d image(s), model %s, round %s, job %s" % (
        len(prompt), len(a.file), len(a.image), a.model, a.round or "-", codex_image.codex_path(job)), file=sys.stderr)
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
    answered = answer.is_file() and bool(answer.read_text(encoding="utf-8", errors="replace").strip())
    _receipt(job.name, a.model, answered, inlined, rc)
    try:
        clog = (job / "codex.log").read_text(errors="replace")
    except OSError:
        clog = None
    etok = None
    if events:
        etok = events_tokens(events.read_text(encoding="utf-8", errors="replace") if events.is_file() else "")
        meta = {"job_win": codex_image.codex_path(job), "job": str(job), "rc": rc, "lockdown": bool(a.lockdown),
                "codex_home_win": env["CODEX_HOME"] if codex_image.codex_side() == "win" else None,
                "codex_home": env["CODEX_HOME"], "codex_side": codex_image.codex_side(),
                "refused_tool_calls": len(REFUSED_TOOL_RE.findall(clog or ""))}
        Path(str(events) + ".meta.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    _log_call(job.name, a.model, prompt, answer.read_text(encoding="utf-8", errors="replace") if answered else "", rc, clog, etok,
              round_name=a.round, secs=time.time() - started, files=[p for p, _ in inlined])
    if not answered:
        tail = (job / "codex.log").read_text(errors="replace")
        code, name = classify_failure(tail, rc)
        print("ERROR: no answer (%s, codex rc %d, %.0fs). Job kept: %s\n%s" % (
            name, rc, time.time() - started, job, tail), file=sys.stderr)
        verdict(name, code)
        return code
    text = answer.read_text(encoding="utf-8", errors="replace")
    # A refusal is not an answer. Written out anyway (--out and stdout) so the caller can read what was
    # said, but the exit code and the verdict say it did not happen.
    refused = refusal_in(text)
    if refused:
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(text, encoding="utf-8")
        print(text)
        print("ERROR: the model refused rather than answered (%d chars, matched %r). Job kept: %s"
              % (len(text.strip()), refused, job), file=sys.stderr)
        verdict("MODEL_REFUSED", EXIT_TRANSPORT)
        return EXIT_TRANSPORT
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    print("[consult] answered in %.0fs" % (time.time() - started), file=sys.stderr)
    if not a.keep:
        shutil.rmtree(job, ignore_errors=True)
    verdict("ANSWERED", 0)
    return 0


def cli(argv=None):
    """main() with no path out that lacks a verdict. An EnvError from codex_image (no CODEX_HOME, no CLI)
    used to escape as a bare traceback: exit 1, no --out file, no verdict -- indistinguishable from "the
    model had nothing to say" to a caller that lost the status (measured 2026-11-17)."""
    try:
        return main(argv)
    except KeyboardInterrupt:
        verdict("INTERRUPTED", EXIT_TRANSPORT)
        return EXIT_TRANSPORT
    except SystemExit as e:                     # argparse and the tool's own sys.exit("message")
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 2)
        if code:
            if not isinstance(e.code, int):
                print(e.code, file=sys.stderr)
            verdict("REFUSED_BEFORE_SENDING" if code == 2 else "EXIT_%s" % code, code)
        return code
    except Exception as e:                      # noqa: BLE001  the whole point: no silent traceback
        import traceback
        traceback.print_exc()
        code, name = classify_failure("%s: %s" % (type(e).__name__, e), 0)
        verdict(name, code)
        return code


if __name__ == "__main__":
    sys.exit(cli())
