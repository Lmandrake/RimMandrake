#!/usr/bin/env python3
"""Rule 6 of design/RimMandrake/relentless_verdict_identity_design_2026-11-02.md (RELENTLESS_REDESIGN_VERDICT_FAIL_CLOSED):
relentless.py binds evidence to build identity, caps close retries, and enforces deadlines on result arrival.

  F  `finish` names one commit by its full id: canonical_commit turns a short id or a ref into 40 hex, refuses the rest
  B  a check binds {sha, gen, contract hash} at launch; a verdict consumed after any moved is dropped (check_rebound):
     no verdict acted on, no strike, no new gen, and the candidate is checked afresh
  D  run, check and consult persist an absolute deadline at launch; finish / verdict / help_answer arriving past it are
     Fenced and change nothing
  C  closing attempts are counted before each try and capped by close_retry_max; past it, close_stuck, never for ever

Each family has a mutant (a monkeypatch of the one design point) that must turn its rows red; a surviving mutant fails
this selftest. Rows run the real tick on selftest_relentless's rig."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []


class Rows:
    """Collects one family's rows, so the same family runs plain (must be green) and under a mutant (must go red)."""

    def __init__(self, quiet=False):
        self.bad, self.quiet = [], quiet

    def ok(self, cond, name):
        if not self.quiet:
            print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            self.bad.append(name)


def to_check(x, rows):
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "proof", live="once: test")
    R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    rows.ok(st["status"] == "checking", "the rig reaches the checker")
    return st


def fam_finish_sha(rows):
    d = tempfile.mkdtemp(prefix="rl-r6-git-")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    for cmd in (["git", "init", "-q", "-b", "main"], ["git", "commit", "-q", "--allow-empty", "-m", "one"]):
        subprocess.run(cmd, cwd=d, env=env, check=True, capture_output=True)
    full = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    old = os.getcwd()
    os.chdir(d)
    try:
        rows.ok(R.canonical_commit(full[:9]) == full, "F a short id is resolved to the full 40-hex id")
        rows.ok(R.canonical_commit("main") == full, "F a ref is resolved to the commit it names now")
        for bad in ("nope", "0" * 40):
            try:
                R.canonical_commit(bad)
                rows.ok(False, "F %r refused" % bad)
            except ValueError:
                rows.ok(True, "F %r refused: not a commit in this clone" % bad)
    finally:
        os.chdir(old)
        subprocess.run(["rm", "-rf", d])


def fam_bind(rows):
    for what in ("contract", "sha", "gen", None):
        x = T.Rig(n=1, share=1.0)
        st = to_check(x, rows)
        b = st["check"].get("bind") or {}
        rows.ok(b.get("sha") == "sha1" and b.get("gen") == st["gen"] and b.get("hash") == R.contract_hash(st["contract"]),
                "B the check is bound at launch to sha, gen and contract hash: %s" % b)
        was = st
        if what:
            with x.s.lock():
                cur = x.s.load("I0")
                if what == "contract":
                    cur["contract"] = dict(cur["contract"], proof="an easier proof")
                elif what == "sha":
                    cur["candidate"] = dict(cur["candidate"], sha="f" * 40)
                else:
                    cur["gen"] += 1
                x.s.save(cur)
        R.verdict(x.s, "I0", st["check"]["nonce"], "FAIL", "it broke", defects=["it broke"])
        x.w.up[st["check"]["run"]["unit"]] = False
        acts = x.tick()
        st = x.st("I0")
        if what:
            rows.ok(st["status"] in ("candidate", "checking") and st["gen"] == was["gen"] + (what == "gen") and not st["failures"]
                    and st["total_failures"] == was["total_failures"] and st["returns"] == was["returns"]
                    and (st.get("check") or {}).get("nonce") != was["check"]["nonce"],
                    "B %s moved under the checker: its FAIL is not acted on, no strike, no gen, a fresh check (%s)"
                    % (what, st["status"]))
            rows.ok(any(a.get("do") == "check_rebound" for a in acts or [])
                    and any(a.get("end") == "check_rebound" and {"contract": "hash"}.get(what, what) in a.get("detail", "") for a in x.s.attempts("I0")),
                    "B the drop is told and recorded, naming what moved")
        else:
            w = st.get("wait") or {}
            rows.ok(st["status"] == "held" and w.get("kind") == "attribution" and w.get("sha") == "sha1"
                    and not any(a.get("do") == "check_rebound" for a in acts or []),
                    "B control: nothing moved, the FAIL is consumed and waits for its attribution (%s %s)" % (st["status"], w))
        x.done()


def fam_deadline(rows):
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "proof", live="once: test")
    rows.ok(st["run"].get("deadline") == st["started_at"] + x.r["run_max_s"], "D a run persists its deadline at launch")
    x.now = st["run"]["deadline"] + 1
    try:
        R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
        rows.ok(False, "D a finish past the run deadline is Fenced")
    except R.Fenced:
        rows.ok(not x.s.load("I0").get("candidate") and x.s.load("I0")["status"] == "running",
                "D a finish past the run deadline is Fenced and leaves no candidate")
    x.done()

    x = T.Rig(n=1, share=1.0)
    st = to_check(x, rows)
    rows.ok(st["check"].get("deadline") == st["check"]["at"] + x.r["check_max_s"] + x.r["launch_grace_s"],
            "D a check persists its deadline at launch")
    x.now = st["check"]["deadline"] + 1
    try:
        R.verdict(x.s, "I0", st["check"]["nonce"], "PASS", "ran it")
        rows.ok(False, "D a verdict past the check deadline is Fenced")
    except R.Fenced:
        rows.ok(x.s.load("I0")["check"].get("verdict") is None, "D a verdict past the check deadline is Fenced, unrecorded")
    x.done()

    for late in (True, False):      # a real consult: launched by the tick, its deadline persisted by help_start
        x = T.Rig(1, circling=T.HELP)
        T.circle(x, detail="first round")
        T.circle(x, detail="second round")
        for _ in range(4):
            x.tick()
        h = x.st("I0").get("help") or {}
        rows.ok(h.get("status") == "running" and h.get("deadline") == h.get("started_at", 0) + T.HELP["help_max_s"]
                + x.r["launch_grace_s"], "D a consult persists its deadline at launch: %s" % h.get("deadline"))
        if late:
            x.now = (h.get("deadline") or 0) + 1
        try:
            R.help_answer(x.s, "I0", h.get("nonce"), ["idea | what kills it"], x.r)
            got = "taken"
        except R.Fenced:
            got = "fenced"
        h = x.st("I0")["help"]
        if late:
            rows.ok(got == "fenced" and not h.get("answered_at"), "D a consult answer past its deadline is Fenced")
        else:
            rows.ok(got == "taken" and h.get("answered_at"), "D control: an answer inside the deadline is taken")
        x.done()


def fam_close(rows, cap=3):
    x = T.Rig(n=1, share=1.0, close_retry_max=cap)
    calls = []

    def stuck(item, sha, reason, live=None):
        calls.append(sha)
        return "git hiccup"
    x.w.ledger_close = stuck
    T.full_pass(x, "I0")
    for _ in range(cap + 6):
        x.tick()
    st = x.st("I0")
    text = json.dumps(st) + json.dumps(x.s.attempts("I0"))
    rows.ok(len(calls) == cap, "C exactly close_retry_max=%d attempts, then no more: %d" % (cap, len(calls)))
    rows.ok(st["status"] != "closing" and "close_stuck" in text and x.w.closes == [],
            "C past the cap the item leaves closing as close_stuck (%s)" % st["status"])
    x.done()


MUTANTS = {
    "M_bind_never_moves": ("bind_moved", lambda st: None, fam_bind),
    "M_no_deadline": ("past_deadline", lambda rec, now: None, fam_deadline),
    "M_no_close_cap": ("CLOSE_RETRY_MAX", 10 ** 9, None),
}


def main():
    families = [fam_finish_sha, fam_bind, fam_deadline, fam_close, fam_close_uncapped]
    for fam in families:
        rows = Rows()
        fam(rows)
        FAILS.extend(rows.bad)
    for name, (attr, fake, fam) in MUTANTS.items():
        real = getattr(R, attr)
        setattr(R, attr, fake)
        rows = Rows(quiet=True)
        try:
            if fam is None:     # the cap mutant: no rules entry, the module default made unlimited
                fam_close_uncapped(rows)
            else:
                fam(rows)
        except Exception as e:      # a mutant that crashes a row is killed too
            rows.bad.append("raised %s" % type(e).__name__)
        finally:
            setattr(R, attr, real)
        killed = bool(rows.bad)
        print(("ok   " if killed else "FAIL ") + "mutant %s is killed (%d red rows)" % (name, len(rows.bad)))
        if not killed:
            FAILS.append("mutant %s survived" % name)
    print("FAIL: %d failed" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


def fam_close_uncapped(rows):
    """fam_close with the rules entry left out, so the cap comes from R.CLOSE_RETRY_MAX (the mutant's target)."""
    x = T.Rig(n=1, share=1.0)
    x.r.pop("close_retry_max", None)
    calls = []

    def stuck(item, sha, reason, live=None):
        calls.append(sha)
        return "git hiccup"
    x.w.ledger_close = stuck
    T.full_pass(x, "I0")
    for _ in range(R.CLOSE_RETRY_MAX + 6 if R.CLOSE_RETRY_MAX < 100 else 30):
        x.tick()
    rows.ok(x.st("I0")["status"] != "closing", "C the module default caps closing too (%d attempts)" % len(calls))
    x.done()


if __name__ == "__main__":
    sys.exit(main())
