#!/usr/bin/env python3
"""No answer from a consult is never exit 0, and every kind of no-answer has its own code.

Owner, 2026-11-17: "Fix the codex-consult skill to make that outcome intentionally different than no
failure somehow... we must not suffer such errors."

WATCHED FAILING on the base commit 48a624d82f, where gpt_consult.py had no classify_failure,
refusal_in or verdict at all: this file exits 2 at import (ImportError) there, and every check below
is red. The incident: `gpt_consult.py` raised EnvError (no native Codex app on this Mac; Codex runs
only in the codex-consult container), printed a traceback, wrote NO --out file, and the caller's
`cmd > log 2>&1; echo "exit=$?"` chain reported 0 -- because `$?` in that chain is the exit status of
the LAST command, not of the consult. Three further runs failed the same silent way (missing
--skip-git-repo-check; a model a ChatGPT login may not use; then the real usage wall), and a fifth
returned 331 bytes of "I'm blocked by the session's tool access... I haven't read them and won't
invent findings" -- which a non-empty check reads as success.

So two defences, because the first alone could not have saved that session:
  * distinct exit codes per cause (20 auth / 21 allowance / 22 transport / 23 deadline / 1 unknown), and
  * a VERDICT= line on stderr, which survives a caller that loses the exit status.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gpt_consult as G  # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def main():
    # ---- every cause gets its own code, and none of them is 0 -------------------------------------
    cases = [
        ("ERROR: You've hit your usage limit. Visit ... or try again at Nov 18th.", 0,
         G.EXIT_ALLOWANCE, "ALLOWANCE", "the measured usage-limit wall"),
        ("ERROR: {\"status\":429,\"message\":\"rate limit\"}", 0, G.EXIT_ALLOWANCE, "ALLOWANCE", "a 429"),
        ("codex_image.EnvError: Cannot find CODEX_HOME. Looked at $CODEX_HOME, ~/.codex.", 0,
         G.EXIT_AUTH, "AUTH", "the measured missing-CODEX_HOME EnvError"),
        ("ERROR: 401 unauthorized", 0, G.EXIT_AUTH, "AUTH", "a 401"),
        ("ERROR: {\"code\":\"model_not_found\",\"message\":\"The 'gpt-5.2-codex' model is not supported "
         "when using Codex with a ChatGPT account.\"}", 0, G.EXIT_TRANSPORT, "TRANSPORT",
         "the measured model_not_found refusal"),
        ("Not inside a trusted directory and --skip-git-repo-check was not specified.", 0,
         G.EXIT_TRANSPORT, "TRANSPORT", "the measured trusted-directory refusal"),
        ("Cannot connect to the Docker daemon", 0, G.EXIT_TRANSPORT, "TRANSPORT", "the container being down"),
        ("", 124, G.EXIT_DEADLINE, "DEADLINE", "a timeout (rc 124) beats every marker"),
        ("something nobody has seen before", 0, G.EXIT_UNCLASSIFIED, "NO_ANSWER_UNCLASSIFIED",
         "an unknown failure is 1, never 0"),
    ]
    for log, rc, want_code, want_name, what in cases:
        code, name = G.classify_failure(log, rc)
        ok(code == want_code and name == want_name,
           "%s -> exit %d %s (got %d %s)" % (what, want_code, want_name, code, name))
        ok(code != 0, "%s is not exit 0" % what)

    # rc 124 must win even when the log also looks like an allowance wall: a call we killed on the
    # deadline may have been mid-429, and the actionable fact is that WE stopped it.
    code, name = G.classify_failure("usage limit reached", 124)
    ok((code, name) == (G.EXIT_DEADLINE, "DEADLINE"), "a deadline beats an allowance marker in the same log")

    # ---- a refusal is not an answer ----------------------------------------------------------------
    measured = ("I'm blocked by the session's tool access: no filesystem-reading or shell tool is "
                "available, so I cannot read the four files in `/work`.\n\nPlease attach or paste all "
                "four documents... I haven't read them and won't invent findings or citations.")
    ok(G.refusal_in(measured), "the measured 331-byte 'I cannot read /work' reply reads as a refusal")
    ok(G.refusal_in("I cannot read the attached file.") is not None, "a short 'I cannot read' is a refusal")
    ok(G.refusal_in("") is None and G.refusal_in("   ") is None, "an empty answer is not classed a refusal "
                                                                 "(the no-answer path owns that)")
    # A real review is long and may QUOTE a refusal while reviewing it. Length is the discriminator.
    long_review = ("## Finding 1\nThe spec says the agent cannot read the field, and I cannot read it "
                   "either without the code.\n" + ("Lorem ipsum dolor sit amet. " * 200))
    ok(len(long_review) > G.REFUSAL_MAX_CHARS and G.refusal_in(long_review) is None,
       "a long review that quotes 'I cannot read' is NOT a refusal")

    # ---- the verdict line reaches stderr on every path --------------------------------------------
    # This is the defence that would actually have saved the measured session, so it is checked by
    # running the real tool, not by reading the source.
    env = dict(os.environ, CODEX_HOME="/nonexistent-codex-home-for-selftest")
    r = subprocess.run([sys.executable, str(HERE / "gpt_consult.py"), "say hi"],
                       capture_output=True, text=True, timeout=180, env=env)
    lines = [x for x in r.stderr.strip().split("\n") if x.strip()]
    ok(bool(lines) and lines[-1].startswith("[consult] VERDICT="),
       "a real failing call ends stderr with a VERDICT= line (last line: %r)" % (lines[-1] if lines else None))
    ok(r.returncode != 0, "a real failing call does not exit 0 (got %d)" % r.returncode)
    ok(r.returncode in (G.EXIT_AUTH, G.EXIT_ALLOWANCE, G.EXIT_TRANSPORT, G.EXIT_DEADLINE,
                        G.EXIT_UNCLASSIFIED, 4, 5),
       "its code is one of the named ones (got %d)" % r.returncode)

    print("\n%s" % ("ALL PASS" if not FAILS else "%d failed" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
