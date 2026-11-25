#!/usr/bin/env python3
"""Ask GPT (codex exec) a question about some files, from any clone.

    python3 src/RimMandrake/Utils/gpt_consult.py "Review this plan for holes" -f design/x.md -f src/y.py
    python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file ask.md -f a.py --out review.md

This is a thin shim over Dispatch's GPT door (`~/dev/Dispatch/providers/chatgpt/bin/gpt_door.py`, loaded by
dispatch_door.py): the door finds Codex, uses the one sign-in folder, inlines nothing on its own, runs the call, keeps
the outcomes apart, retries once on a rotated sign-in, and logs every consult. This file keeps RimMandrake's
own rules: the Codex advice gate, receipts, rounds and the call log. Sign-in status and renewal:
`python3 ~/dev/Dispatch/providers/chatgpt/bin/gpt_door.py status --probe` / `renew` (the chatgpt-consult skill).

The named files are inlined into the prompt. --codex-home uses another folder that has its own sign-in.
Default model and effort: the door's PURPOSES table (CODEX_CONSULT_MODEL overrides the model).

Every call is metered in gpt_call_log (job, model, rc, real tokens, seconds, files inlined, and its review ROUND:
`--round NAME` or $RM_CONSULT_ROUND). One round = one review pass over one subject; give every call of that pass the
same name, record what it found with `gpt_consult_rounds.py yield`, and `gpt_consult_rounds.py report` prints cost and
yield per round (GPT_CONSULT_MEASURE_COST_UNLOGGED).

Every call first passes codex_advice.gate, which asks the account plan (`./acct can-use codex`): with Codex at or
under its leave line every call is refused with that line, exit 4, a call marked `--required` too; a plan or a meter
that cannot be read says COULD NOT LOOK and the job is sent. The line and its reset-day rule are in the plan
(`./acct plan`), not here. No Claude fallback (owner routing ruling 2026-10-28).

🔴 NO ANSWER IS NEVER EXIT 0, AND EVERY KIND OF NO-ANSWER HAS ITS OWN CODE (owner, 2026-11-17: "make that
outcome intentionally different than no failure somehow... we must not suffer such errors"). The codes are
the GPT door's (Dispatch providers/chatgpt/bin/gpt_door.py EXIT):

    0   an answer arrived and is non-empty
    4   Codex is at or under its leave line in the account plan (./acct can-use codex): no job was sent
    20  AUTH: no usable login (no CODEX_HOME, 401/invalid_grant)  -> the agent renews it: gpt_door.py renew
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
import subprocess  # noqa: F401  (selftests patch gpt_consult.subprocess.run; the door runs codex through it)
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))          # review_identity (job receipts)
import codex_advice  # noqa: E402  (the Codex HOLD/EXHAUSTED gate)
import dispatch_door  # noqa: E402

EXIT_AUTH, EXIT_ALLOWANCE, EXIT_TRANSPORT, EXIT_DEADLINE, EXIT_UNCLASSIFIED = 20, 21, 22, 23, 1
try:
    door = dispatch_door.load()
except dispatch_door.DoorMissing as _e:          # cli() turns this into a TRANSPORT verdict
    door, DOOR_MISSING = None, str(_e)
else:
    DOOR_MISSING = None
    assert (door.EXIT_AUTH, door.EXIT_ALLOWANCE, door.EXIT_TRANSPORT, door.EXIT_DEADLINE, door.EXIT_UNCLASSIFIED) \
        == (EXIT_AUTH, EXIT_ALLOWANCE, EXIT_TRANSPORT, EXIT_DEADLINE, EXIT_UNCLASSIFIED)
    # One copy of each rule, in the door; re-exported for callers and selftests that read them here.
    from gpt_door import (AUTH_MARKERS, ALLOWANCE_MARKERS, TRANSPORT_MARKERS, REFUSAL_MARKERS,  # noqa: E402,F401
                          REFUSAL_MAX_CHARS, classify_failure, refusal_in, LOCKDOWN_FEATURES, LOCKDOWN_ARGS,
                          REFUSED_TOOL_RE, TOKENS_RE, real_tokens, events_tokens)

DEFAULT_CONSULT_MODEL, DEFAULT_EFFORT = door.defaults("consult") if door else ("gpt-6.1-sol", "high")


def verdict(name, code):
    """The last line of stderr on every path, so a caller that captured only the output can still tell an
    answer from a wall (owner, 2026-11-17)."""
    print("[consult] VERDICT=%s exit=%d" % (name, code), file=sys.stderr, flush=True)


def scratch_root():
    """Job folders, where they have always been (ext4 state). CODEX_SCRATCH overrides."""
    if os.environ.get("CODEX_SCRATCH"):
        return Path(os.environ["CODEX_SCRATCH"]).expanduser()
    return Path.home() / ".local/state/rimmandrake/scratch/codex"


def build_prompt(question, files, inlined=None):
    """The prompt text (door.build_prompt, names relative to this repo). When `inlined` is a list, each file's
    (shown path, exact bytes inlined) is appended to it: the job receipt hashes those bytes."""
    try:
        return door.build_prompt(question, files, root=ROOT, inlined=inlined)
    except door.PromptError as e:
        sys.exit(str(e))


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
    ap.add_argument("--effort", default=DEFAULT_EFFORT, help="model_reasoning_effort (default %s)" % DEFAULT_EFFORT)
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--keep", action="store_true", help="keep the scratch job dir")
    ap.add_argument("--codex", help=argparse.SUPPRESS)      # retired: "win" is refused by name and logged by the door
    ap.add_argument("--codex-home", help="run codex with this CODEX_HOME (must already hold a login; never seeded here)")
    ap.add_argument("--lockdown", action="store_true",
                    help="no tools: --ephemeral, every tool feature disabled, web search off, strict config")
    ap.add_argument("--events", help="run codex --json and write its event stream (the transcript) here, plus "
                                     "<EVENTS>.meta.json naming the job dir and home")
    ap.add_argument("--required", help="the rule that requires this review round: recorded with a refusal. It does "
                                       "not pass Codex's leave line; ./acct line codex changes that line")
    a = ap.parse_args(argv)
    side = door.resolve_side(a.codex or os.environ.get("RM_CODEX_SIDE") or None)
    if a.round is not None and not ROUND_RE.match(a.round):
        ap.error("--round %r: 1-80 chars of A-Z a-z 0-9 _ . : - (starting alphanumeric)" % a.round)
    refused = codex_advice.gate("gpt_consult", a.required)
    if refused:
        return refused
    home = None
    if a.codex_home:
        home = Path(a.codex_home).expanduser().resolve()
        if not (home / "auth.json").is_file():
            sys.exit("--codex-home %s has no auth.json (set it up first; gpt_consult never seeds a home)" % home)
    if a.prompt_file:
        question = Path(a.prompt_file).read_text(encoding="utf-8")
    elif a.question:
        question = a.question
    else:
        ap.error("give a question or --prompt-file")
    for img in a.image:
        if not Path(img).is_file():
            sys.exit("cannot read image %s" % img)
    inlined = []
    prompt = build_prompt(question, a.file, inlined)
    print("[consult] %d chars, %d file(s), %d image(s), model %s, round %s, side %s" % (
        len(prompt), len(a.file), len(a.image), a.model, a.round or "-", side), file=sys.stderr)
    events = Path(a.events) if a.events else None
    ans = door.ask(prompt, images=a.image, side=side, home=home, model=a.model, effort=a.effort,
                   lockdown=a.lockdown, timeout=a.timeout, events_path=events, scratch=scratch_root(),
                   keep=a.keep, caller="rimmandrake/gpt_consult" + ("/" + a.round if a.round else ""))
    job = Path(ans.job) if ans.job else None
    job_name = job.name if job else "consult-none"
    answered = ans.outcome in ("ANSWERED", "MODEL_REFUSED")     # an answer file with text arrived
    _receipt(job_name, a.model, answered, inlined, ans.rc)
    if events:
        meta = {"job": str(job) if job else None, "rc": ans.rc, "lockdown": bool(a.lockdown),
                "codex_home": ans.home or None, "refused_tool_calls": ans.refused_tool_calls}
        Path(str(events) + ".meta.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    _log_call(job_name, a.model, prompt, ans.text if answered else "", ans.rc, None, ans.tokens,
              round_name=a.round, secs=ans.seconds, files=[p for p, _ in inlined])
    if ans.outcome == "ANSWERED":
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(ans.text, encoding="utf-8")
        print(ans.text)
        print("[consult] answered in %.0fs" % ans.seconds, file=sys.stderr)
        verdict("ANSWERED", 0)
        return 0
    if ans.outcome == "MODEL_REFUSED":
        # A refusal is not an answer. Written out anyway (--out and stdout) so the caller can read what was
        # said, but the exit code and the verdict say it did not happen.
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(ans.text, encoding="utf-8")
        print(ans.text)
        print("ERROR: the model refused rather than answered (%d chars, %s). Job kept: %s"
              % (len(ans.text.strip()), ans.detail, job), file=sys.stderr)
        verdict("MODEL_REFUSED", ans.exit_code)
        return ans.exit_code
    print("ERROR: no answer (%s, codex rc %s, %.0fs%s). Job kept: %s\n%s" % (
        ans.outcome, ans.rc, ans.seconds, ", retried once" if ans.retried else "", job, ans.detail), file=sys.stderr)
    verdict(ans.outcome, ans.exit_code)
    return ans.exit_code


def cli(argv=None):
    """main() with no path out that lacks a verdict. An EnvError (no CODEX_HOME, no CLI)
    used to escape as a bare traceback: exit 1, no --out file, no verdict -- indistinguishable from "the
    model had nothing to say" to a caller that lost the status (measured 2026-11-17)."""
    if door is None:
        print(DOOR_MISSING, file=sys.stderr)
        verdict("TRANSPORT", EXIT_TRANSPORT)
        return EXIT_TRANSPORT
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
