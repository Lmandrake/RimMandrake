#!/usr/bin/env python3
"""selftest_lane_stop.py - the promises of design/specs/2026-11-23-lane-stops-name-their-end/boundary.md, one check each.
No ssh, no game: a temp queue, a fake worker. --mutants plants faults in the code and wants each one caught."""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testq as T  # noqa: E402
import lane_stop as LS  # noqa: E402

FAILS, NOTE = [], "Steve2 is running; it rewrites Prefs.xml on exit. Stop it first (pid %d)"
A, B = T.STEVE, T.STEVE2


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def job(n, mod="Mock"):
    return {"id": "J20261123T0000%02dZ-aaaa%02d" % (n, n), "mod": mod, "lane": "stevedesktop", "priority": 50,
            "profile": "targeted", "submitted": "2026-11-23T00:00:00Z", "requested_by": "BENCH", "source_sha": "abc1234",
            "selector": {"chains": ["c"]}, "purpose": "fix"}


def res(outcome="REFUSED", cause="LOAD", note=NOTE % 1234):
    return {"outcome": outcome, "cause": cause, "note": note, "attempt": "x.a1", "counts": {}}


class Rig:
    def __enter__(self):
        self.saved = {k: getattr(T, k) for k in ("QHOME", "worker_for", "companion_unready", "steve2_on")}
        T.QHOME = tempfile.mkdtemp(prefix="lane_stop_")
        T.ensure_dirs()
        self.sent = []
        T.worker_for = lambda host: (lambda args, stdin=None, timeout=180: self.reply(host, args))
        T.companion_unready = lambda j, read=None: None
        T.steve2_on = lambda: True
        return self

    def reply(self, host, args):
        if args[0] == "start":
            self.sent.append(host)
            return 0, {"attempt": "x.a1"}
        return 0, {}

    def __exit__(self, *_):
        for k, v in self.saved.items():
            setattr(T, k, v)

    def finish(self, host, j, r, cancel=False):
        T.S.dump({"job": j, "attempt": "x.a1", "host": host, "cancel": cancel}, T.q("running", j["id"] + ".json"))
        T.finish({"job": j, "attempt": "x.a1", "host": host, "cancel": cancel}, r)
        return T.read_json(T.q("done", j["id"] + ".json"))

    def admits(self, host):
        j = job(99)
        T.S.dump(j, T.q("pending", j["id"] + ".json"))
        self.sent.clear()
        T.admit({}, host=host)
        for st in ("pending", "running"):
            with contextlib.suppress(FileNotFoundError):
                os.remove(T.q(st, j["id"] + ".json"))
        return self.sent == [host]


def t_stop():
    with Rig() as r:
        r.finish(B, job(1), res())
        check(r.admits(B), "two-equal-refusals-stop-that-game: one refusal stops nothing")
        d = r.finish(B, job(2, "Other"), res(note=NOTE % 88))
        check(not r.admits(B) and r.admits(A), "two-equal-refusals-stop-that-game: Steve2 stops (another mod, another pid), Steve1 goes on")
        check(T.steve_lanes() == [A], "two-equal-refusals-stop-that-game: the filler no longer counts Steve2 as a live game")
        check(str(d.get("repeat_stop")).startswith("REFUSED/LOAD: "), "one-ticket-for-one-cause: the done record carries the cause")
        rec = LS.stopped(T, B)
        check(rec and LS.stopped(T, B, T.S.parse_ts(rec["until"]) + 1) is None, "a-stop-retries-by-itself: past its end it stands no more")
        LS.step(T, T.STEVE_HOSTS, now=T.S.parse_ts(rec["until"]) + 1)
        check(r.admits(B), "a-stop-retries-by-itself: one job is admitted after the end")
        r.finish(B, job(3), res())
        rec2 = LS.stopped(T, B)
        check(rec2 and rec2["stops"] == 2 and rec2["first"] == rec["first"], "a-stop-retries-by-itself: the same ending stops it again at once, the first stop's time kept")
        r.finish(B, job(4), res("DONE", None, ""))
        check(r.admits(B), "a-stop-retries-by-itself: a DONE clears the stop")
    with Rig() as r:
        r.finish(A, job(1), res())
        r.finish(A, job(2), res("DONE", None, ""))
        r.finish(A, job(3), res())
        r.finish(A, job(4), res(note="companion STALE x not built from"))
        check(r.admits(A), "a-done-job-or-a-different-ending-counts-from-one: neither stops the game")
        r.finish(B, job(5), res(note="companion STALE x not built from"))
        check(r.admits(A) and r.admits(B), "a-done-job-or-a-different-ending-counts-from-one: an equal ending on the other game is not the second")
    with Rig() as r:
        h = res("INVALID", "HARNESS", "modcheck exit 1 and no sheet JSON: 12 unclaimed must-shows")
        r.finish(A, job(1, "Graffiti"), h)
        r.finish(A, job(2, "Graffiti"), h)
        check(r.admits(A), "one-mods-harness-fault-does-not-stop-the-game")
        r.finish(A, job(3, "FlowWorks"), h)
        check(not r.admits(A), "one-mods-harness-fault-does-not-stop-the-game: the same fault on a second mod is the game's")
    with Rig() as r:
        for n, (x, cancel) in enumerate([(res("REFUSED", "GUARD_HELD"), False), (res("INVALID", "BLOCKED_SELECTION"), False),
                                         (res(), True), (res("INTERRUPTED", "CRASH"), False)]):
            r.finish(A, job(10 + 2 * n), x, cancel)
            r.finish(A, job(11 + 2 * n), x, cancel)
        check(r.admits(A), "a-cancelled-or-selection-refusal-never-stops")
        check(LS.signature(res("INVALID", "CANARY")) is None, "a-cancelled-or-selection-refusal-never-stops: CANARY has its own rule")
    with Rig() as r:
        for n in (1, 2):
            r.finish(A, job(n), res("REFUSED", "SCHEMA", "unknown selector key"))
        check(r.admits(A), "a-cancelled-or-selection-refusal-never-stops: repeated REFUSED/SCHEMA leaves the game open")


def pause(**kw):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = T.cmd_pause(argparse.Namespace(**dict({"reason": "r", "hours": None, "until_unit": None}, **kw)))
    return rc, out.getvalue()


def t_pause():
    with Rig() as r:
        now = time.time()
        rc, out = pause()
        pz = T.paused()
        check(rc == 0 and "NOTE" in out and abs(T.S.parse_ts(pz["until"]) - now - LS.DEFAULT_PAUSE_H * 3600) < 5,
              "every-pause-has-an-end: a hand pause with none gets the default and says so")
        check(LS.step(T, T.STEVE_HOSTS, now=now + 60) == [] and not r.admits(A), "every-pause-has-an-end: it stands until then")
        rc, _ = pause(hours=5)
        check(rc == 0 and T.S.parse_ts(T.paused()["until"]) - now > 4 * 3600, "a-hand-pause-is-extended-not-refused")
        check(LS.step(T, T.STEVE_HOSTS, now=now + 5 * 3600 + 5) == ["pause " + A] and not T.paused() and r.admits(A),
              "every-pause-has-an-end: the tick lifts it at its end")
        check("the pause's own end" in open(T.q("tick.log")).read(), "every-pause-has-an-end: the log says why")
        T.S.dump({"since": T.S.utcnow(), "reason": "old record with no end"}, T.pause_path())
        check(LS.step(T, T.STEVE_HOSTS, now=now + 49 * 3600) == ["pause " + A], "every-pause-has-an-end: a record from before this rule ends too")
        r.finish(A, job(1), res("REFUSED", "SYNC", "runner pull failed"))
        pz = T.paused()
        check(pz and pz["outcome"] == "REFUSED" and LS.step(T, T.STEVE_HOSTS, now=time.time() + LS.RETRY_S + 5) == ["pause " + A],
              "every-pause-has-an-end: an auto pause ends for a retry")
        r.finish(B, job(2), res("REFUSED", "SYNC", "runner pull failed"))
        check(T.paused(B) and LS.step(T, T.STEVE_HOSTS, now=time.time() + LS.RETRY_S + 5) == ["pause " + B],
              "every-pause-has-an-end: Steve2's own pause ends too")
    with Rig():
        pause(until_unit="soak.service")
        check(LS.step(T, T.STEVE_HOSTS, now=time.time() + 9e5, active=lambda u: True) == [], "a-unit-pause-waits-for-its-unit: it stands while the unit runs")
        check(LS.step(T, T.STEVE_HOSTS, active=lambda u: None) == [] and "could not look" in open(T.q("tick.log")).read(),
              "a-unit-pause-waits-for-its-unit: systemd unreadable, the pause stays and says so")
        check(LS.step(T, T.STEVE_HOSTS, active=lambda u: False) == ["pause " + A], "a-unit-pause-waits-for-its-unit: over, the pause ends")


def t_steward():
    import steward as W
    saved = W.tick_timer_state
    W.tick_timer_state = lambda: "active"
    try:
        with Rig() as r:
            for h in (A, B):
                r.finish(h, job(1), res())
                r.finish(h, job(2, "Other"), res())
            st = W.lane_state(time.time(), mods=[])
            rec = LS.stopped(T, A)
            check(st["state"] == "PAUSED" and "equal endings" in st["reason"]
                  and st["fault_at"] == T.S.parse_ts(rec["first"]) + LS.ESCALATE_S,
                  "the-steward-reads-a-stop-as-a-pause: PAUSED, a fault only after ESCALATE_S (%s)" % st["state"])
    finally:
        W.tick_timer_state = saved


def t_fill_stop():
    import steward as W
    saved = W.tick_timer_state
    W.tick_timer_state = lambda: "active"
    try:
        with Rig():
            stop, now = T.q("fill.stop"), time.time()
            end = now + 5 * 3600
            open(stop, "w").write("owner order: no filler today\nuntil: %s\n" % W.iso(end))
            st = W.lane_state(now, mods=[])
            check(st["state"] == "PAUSED" and st["fault_at"] == int(end) and "until" in st["reason"],
                  "a-fill-stop-names-its-end: an until line is its end, not a fault at 60 min (%r, %r)" % (st["fault_at"], int(end)))
            for text in ("owner order: no filler today\n", "until: not a time\n"):
                open(stop, "w").write(text)
                st = W.lane_state(now, mods=[])
                check(st["state"] == "PAUSED" and st["fault_at"] == os.path.getmtime(stop) + W.MANUAL_PAUSE_S,
                      "a-fill-stop-names-its-end: no readable until, a fault 60 min after its mtime (%r)" % text)
    finally:
        W.tick_timer_state = saved


def t_ticket():
    import ingest as I
    with Rig() as r:
        r.finish(B, job(1), res())
        d = r.finish(B, job(2, "Other"), res())
        got, saved = [], (I.repair, I.note_once)
        I.repair, I.note_once = lambda j, x, cause, rec=None: got.append(cause), lambda *a: True
        try:
            I.ingest_one(d)
            I.ingest_one({k: v for k, v in d.items() if k != "repeat_stop"})
        finally:
            I.repair, I.note_once = saved
        check(len(got) == 1 and got[0].startswith("repeat: REFUSED/LOAD: "), "one-ticket-for-one-cause: ingest files the stop's cause, and only a stop's (%r)" % got)


# One scene proves several promises; each promise's name is the test that proves it (boundary_check.py).
t_two_equal_refusals_stop_that_game = t_stop
t_a_done_job_or_a_different_ending_counts_from_one = t_stop
t_one_mods_harness_fault_does_not_stop_the_game = t_stop
t_a_cancelled_or_selection_refusal_never_stops = t_stop
t_a_stop_retries_by_itself = t_stop
t_one_ticket_for_one_cause = t_ticket
t_every_pause_has_an_end = t_pause
t_a_unit_pause_waits_for_its_unit = t_pause
t_a_hand_pause_is_extended_not_refused = t_pause
t_the_steward_reads_a_stop_as_a_pause = t_steward
t_a_fill_stop_names_its_end = t_fill_stop


MUTANTS = [("sig is None:\n        if os", "sig is not None and False:\n        if os"), ('rec["stops"] if False else ', ""),
           ("if same and not one_mod else 0", "if same else 0"), ("if same and not one_mod else 0", "if not one_mod else 0"),
           ('a is None:\n            return None', 'a is None:\n            return True'), ("return now >= until", "return False"),
           ("if cancelled or ", "if "), ("> (time.time() if now is None else now) else None", "> 0 else None"),
           ("            T.cmd_resume(", "            (lambda **k: 0)(a=1) or (lambda *a: 0)(")]


def mutants():
    src = open(os.path.join(HERE, "lane_stop.py")).read()
    caught = n = 0
    for old, new in MUTANTS:
        if old not in src:
            continue
        n += 1
        with tempfile.TemporaryDirectory() as d:
            for f in os.listdir(HERE):
                if f.endswith((".py", ".json")):
                    open(os.path.join(d, f), "w").write(open(os.path.join(HERE, f)).read() if f != "lane_stop.py" else src.replace(old, new))
            env = dict(os.environ, PYTHONPATH=os.pathsep.join([os.path.dirname(os.path.dirname(HERE)), os.path.join(os.path.dirname(os.path.dirname(HERE)), "rimflow"), os.path.dirname(HERE)]))
            p = subprocess.run([sys.executable, os.path.join(d, "selftest_lane_stop.py"), "--core"], capture_output=True, text=True, env=env, timeout=120)
            ok = p.returncode == 1 and "FAIL" in p.stdout
            caught += ok
            print("mutant %s: %s" % (re.sub(r"\s+", " ", old)[:50], "caught" if ok else "NOT CAUGHT %s" % (p.stdout + p.stderr)[-300:]))
    print("mutants caught %d of %d" % (caught, n))
    return 0 if caught == n else 1


def main():
    if "--mutants" in sys.argv:
        return mutants()
    scenes = dict.fromkeys((t_two_equal_refusals_stop_that_game,
                           t_a_done_job_or_a_different_ending_counts_from_one,
                           t_one_mods_harness_fault_does_not_stop_the_game,
                           t_a_cancelled_or_selection_refusal_never_stops,
                           t_a_stop_retries_by_itself,
                           t_one_ticket_for_one_cause,
                           t_every_pause_has_an_end,
                           t_a_unit_pause_waits_for_its_unit,
                           t_a_hand_pause_is_extended_not_refused,
                           t_the_steward_reads_a_stop_as_a_pause,
                           t_a_fill_stop_names_its_end))
    for t in scenes:
        if "--core" not in sys.argv or t in (t_stop, t_pause):
            t()
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
