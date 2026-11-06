#!/usr/bin/env python3
"""selftest_relentless_finish_proof_gate.py: LIVEPROOF_DOLLAR_FIX_REFUSED_AT_FILING.

9 of the 17 live runs that measured nothing in one window were a live_proofs line the live gate refuses (a `$` or
backtick expansion), caught only at game_implemented (after a blind check was paid) or on the lane. And 4 more were a
prover whose `modcheck run` re-deployed into the running game (a locked DLL: 'modcheck wrote NO RESULTS').
1. proof_refusals(): names a `$`, a backtick and a mutation line; passes a literal line, a single-quoted `$`, the one
   `$(wslpath -w <path>)` idiom the gate reads, and a flyer line (the lane's to put down, not the worker's).
2. finish(): a sha whose live_proofs/<ID>.txt holds a refused line is refused, naming the line, and the item is not
   taken as a candidate; after the line is rewritten literally the later sha finishes. A sha with no file, or one the
   tree cannot read, is not refused here.
3. run_proof(): every live proof runs with MODCHECK_SKIP_DEPLOY=1 and MODCHECK_KEEP_MODLIST=1 in its environment.
4. Sanity: the gate the lane uses still refuses the same `$` line (so 1 measures the lane's own rule).

Runs on selftest_relentless's FakeWorld plus a throwaway git repo under TMPDIR; no ledger, clone or game is touched.

    python3 src/RimMandrake/rimflow/selftest_relentless_finish_proof_gate.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import selftest_relentless as SR    # noqa: E402
import relentless_live as L         # noqa: E402

R = SR.R
FAILS = []
PATH = "infrastructure/state/live_proofs/I0.txt"
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def refused(f):
    try:
        f()
    except ValueError as e:
        return str(e)
    return None


def commit(d, files):
    """Write {path: text} into repo `d`, commit -> sha."""
    for p, text in files.items():
        os.makedirs(os.path.join(d, os.path.dirname(p)), exist_ok=True)
        with open(os.path.join(d, p), "w") as f:
            f.write(text)
    for argv in (["add", "--", *files], ["commit", "-q", "-m", "I0: test", "--no-verify"]):
        subprocess.run(["git", *argv], cwd=d, env=ENV, check=True, capture_output=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()


def new_repo():
    d = tempfile.mkdtemp(prefix="finish_proof_gate_")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=d, check=True, capture_output=True)
    return d


def rig():
    x = SR.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    R.contract(x.s, "I0", g, "proof")
    return x, g


DOLLAR = "live-proof A1: python3 src/RimMandrake/X/prove.py --since $(date +%s)\n"
TICK = "live-proof A2: python3 src/RimMandrake/X/prove.py --map `cat m.txt`\n"
MUT = "live-proof A3: python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod X --apply\n"
GOOD = "live-proof A1: python3 src/RimMandrake/X/prove.py --clause A1 < /dev/null\n"


def t_refusals():
    rr = SR.R.rules()
    got = R.proof_refusals(DOLLAR + TICK + MUT + GOOD.replace("A1", "A4"), rr)
    ok([g.split(":")[0] for g in got] == ["A1", "A2", "A3"], "the $, backtick and --apply lines are named: %r" % got)
    ok(R.proof_refusals(GOOD, rr) == [], "a literal line passes")
    ok(R.proof_refusals("live-proof A1: python3 x.py --tag '$HOME'\n", rr) == [], "a single-quoted $ passes")
    ok(R.proof_refusals("live-proof A1: python3 x.py --out $(wslpath -w /tmp/x.json)\n", rr) == [],
       "the wslpath idiom the gate reads passes")
    fly = "live-proof A1: python3 x.py --check flight of the mynock\n"
    lr = L.live_rules(rr)
    ok(L.refused_proof(lr, "", "", fly) is None or R.proof_refusals(fly, rr) == [],
       "a flyer line is not the worker's to rewrite")
    own = "live-proof L4: python3 x.py --read infrastructure/state/ledger/events/OWNER.jsonl\n"
    ok(L.refused_proof(lr, "", "", own.split(": ", 1)[1]) and R.proof_refusals(own, rr) == [],
       "an owner-look line (OWNER.jsonl) is the game lane's to skip, not refused at finish")
    # sanity: the lane's own gate refuses the same text, so this measures the lane's rule and not a copy of it
    ok(bool(L.refused_proof(lr, "", "", DOLLAR.split(": ", 1)[1])), "the lane's refused_proof refuses the $ line")


def t_finish():
    x, g = rig()
    d = new_repo()
    sha = commit(d, {PATH: "live-mods: X\n" + DOLLAR})
    why = refused(lambda: R.finish(x.s, "I0", g, sha, "e", root=d))
    ok(why is not None and PATH in why and "A1" in why and "'$'" in why, "finish refuses a $ line, naming it: %r" % why)
    ok(x.st("I0")["status"] != "candidate", "the refused sha is not taken as a candidate")
    sha2 = commit(d, {PATH: "live-mods: X\n" + GOOD})
    why = refused(lambda: R.finish(x.s, "I0", g, sha2, "e", root=d))
    ok(why is None and x.st("I0")["status"] == "candidate", "the rewritten line finishes: %r" % why)

    x, g = rig()
    d = new_repo()
    sha = commit(d, {"src/RimMandrake/rimflow/plain.py": "x\n"})
    why = refused(lambda: R.finish(x.s, "I0", g, sha, "e", root=d))
    ok(why is None, "a sha with no live_proofs file finishes: %r" % why)
    x, g = rig()
    why = refused(lambda: R.finish(x.s, "I0", g, "f" * 40, "e", root=d))
    ok(why is None, "a sha the tree cannot read is left to the check: %r" % why)


def t_proof_env():
    seen = {}

    class P(object):
        pid = 2 ** 30      # no such process: run_proof killpg()s it (pid 0 would be our own group)

        def __init__(self, *a, **k):
            seen.update(k.get("env") or {})

        def wait(self, timeout=None):
            return 0

    real = L.subprocess.Popen
    L.subprocess.Popen = P
    try:
        fx = L.Fx.__new__(L.Fx)
        fx.books = tempfile.mkdtemp(prefix="finish_proof_env_")
        fx.run_proof("true", os.path.join(fx.books, "log.txt"), 5)
    finally:
        L.subprocess.Popen = real
    ok(seen.get("MODCHECK_SKIP_DEPLOY") == "1" and seen.get("MODCHECK_KEEP_MODLIST") == "1",
       "run_proof sets MODCHECK_SKIP_DEPLOY and MODCHECK_KEEP_MODLIST: %r"
       % {k: v for k, v in seen.items() if k.startswith("MODCHECK")})


if __name__ == "__main__":
    try:
        t_refusals()
        t_finish()
        t_proof_env()
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
