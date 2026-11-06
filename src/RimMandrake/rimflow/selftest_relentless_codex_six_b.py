#!/usr/bin/env python3
"""RELENTLESS_REVIEW_FIX_ROUND_SIX_STILL_DIGS, the rows that run the real tick (selftest_relentless's rig) or game_pass.
Run from selftest_relentless_codex_six.py; the findings' list is its docstring.

  #16 checking: bind_moved is asked again under the lock that consumes a PASS (a contract moved while origin was read).
  #17 checking: a blind FAIL is owed in the state before the item moves; a failed ledger write is retried until it lands.
  #18 closing: a retry tick spent waiting on origin (published() unknown) is no counted closing attempt.
  #22 game_pass: a busy game skips a waiting item, never breaks before the staging holder's own step.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402
import selftest_relentless as T  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def to_check(x):
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "proof", live="once: test")
    R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "checking", "the rig reaches the checker: %s" % st["status"])
    return st


def t16_rebind_under_final_lock():
    x = T.Rig(n=1, share=1.0)
    try:
        st = to_check(x)
        R.verdict(x.s, "I0", st["check"]["nonce"], "PASS", "ran it")
        x.w.up[st["check"]["run"]["unit"]] = False
        moved = []

        def published(sha):        # the contract moves while origin is read, outside the store's lock
            if not moved:
                with x.s.lock():
                    cur = x.s.load("I0")
                    cur["contract"] = dict(cur["contract"], proof="an easier proof")
                    x.s.save(cur)
                moved.append(sha)
            return True
        x.w.published = published
        x.tick()
        st = x.st("I0")
        ok(moved and st["status"] not in ("closing", "done"),
           "#16 a PASS whose contract moved during the unlocked reads is not consumed: %s" % st["status"])
    finally:
        x.done()


def t17_marker_fail_owed():
    x = T.Rig(n=1, share=1.0)
    try:
        st = to_check(x)
        calls, seen = [], []

        def marker(item, sha, reasons):
            calls.append(sha)
            if len(calls) == 1:     # the item has moved already: what the state owes at the failed write
                seen.append((x.st("I0")["status"], x.st("I0").get("marker_fail_owed")))
                return "ledger down"
            return None
        x.w.ledger_marker_fail = marker
        R.verdict(x.s, "I0", st["check"]["nonce"], "FAIL", "it broke")      # old-format prose: no defects
        x.w.up[st["check"]["run"]["unit"]] = False
        x.tick()
        ok(seen and seen[0][1] and seen[0][1][0] == "sha1" and seen[0][0] != "checking",
           "#17 the FAIL is owed in the state before its ledger write is tried: %s" % seen)
        x.tick()
        ok(calls[:2] == ["sha1", "sha1"] and not x.st("I0").get("marker_fail_owed"),
           "#17 a failed write is retried and the debt cleared once it lands: calls %s" % calls)
    finally:
        x.done()


def t18_publish_wait_uncounted():
    x = T.Rig(n=1, share=1.0, close_retry_max=3)
    try:
        x.w.ledger_close = lambda item, sha, reason, live=None: "git hiccup"
        T.full_pass(x, "I0")
        for _ in range(3):
            if x.st("I0")["status"] == "closing" and x.st("I0").get("close_retry"):
                break
            x.tick()
        ok(x.st("I0")["status"] == "closing" and x.st("I0").get("close_retry"), "the rig reaches a close retry: %s"
           % x.st("I0")["status"])
        tries = x.st("I0").get("close_tries")
        x.w.is_pub = None
        for _ in range(8):
            x.tick()
        st = x.st("I0")
        stuck = [a for a in x.s.attempts("I0") if a.get("end") == "close_stuck"]
        ok(st["status"] == "closing" and not stuck and st.get("close_tries") == tries,
           "#18 eight ticks waiting on origin count no closing attempt: %s tries %s -> %s, stuck %d"
           % (st["status"], tries, st.get("close_tries"), len(stuck)))
    finally:
        x.done()


def t22_staging_steps_past_waiting_expedite():
    d = tempfile.mkdtemp(prefix="cx6b_")
    real = R.step, R.broker_drain, G.busy
    try:
        s = R.Store(d)
        for item, phase, exp, at in (("E1", "waiting", True, 1), ("S1", "staging", False, 2)):
            st = R.new_state(item, 1000.0, "t")
            st.update(status=G.GAME, expedite=exp, game={"phase": phase, "entered_at": at})
            with s.lock():
                s.save(st)
        stepped = []
        R.step = lambda store, fx, r, item, now, acts: stepped.append(item)
        R.broker_drain = lambda *a, **k: None
        G.busy = lambda *a, **k: True
        R.game_pass(s, object(), dict(R.rules()), 2000.0, [])
        ok("S1" in stepped and "E1" not in stepped,
           "#22 a busy game still steps the staging holder behind a waiting expedited item: %s" % stepped)
    finally:
        R.step, R.broker_drain, G.busy = real
        shutil.rmtree(d, ignore_errors=True)


def main():
    for t in (t16_rebind_under_final_lock, t17_marker_fail_owed, t18_publish_wait_uncounted,
              t22_staging_steps_past_waiting_expedite):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a row that raises is a FAIL, never a stopped file
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
