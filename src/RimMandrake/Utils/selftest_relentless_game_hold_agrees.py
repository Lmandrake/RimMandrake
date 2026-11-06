#!/usr/bin/env python3
"""selftest_relentless_game_hold_agrees: OPS_RELENTLESS_GAME_HOLD_UNSTICK_DRDP's class guard.

The class: relentless.game_hold_idle_min (ops_watch.rl_game_hold_idle, the reader) and the supervisor that frees a hold
(relentless_game.stale_holds and relentless_broker.over, the actor) are two statements of one rule, and they drifted.
The instance, 2026-11-06: broker batch b1793994255808 proved for 65 minutes with prove_pid=None by design; the actor
reads the broker job's lock, the reader saw "proving, pid gone" and alarmed at 30.4 min on
LIVE_SESSION_FIX_OUTRUNS_FOREGROUND_WINDOW, which was working. The table below runs both on one real store: each row
states what the actor does and what the reader must read, so neither can move alone.
"""
import fcntl
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_relentless_game_hold_agrees_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RELENTLESS_ROOT"] = str(TMP / "belt")
import ops_watch as OW  # noqa: E402
import relentless_broker as RB  # noqa: E402
import relentless_game as G  # noqa: E402

T0 = 1_800_000_000.0
LINE = 30.0                     # the shipped rule's alarm line, read back below
DEAD_PID = 2 ** 22 + 7
ACTOR = {"live_idle_s": 1200}
FAILS = []


class Store:
    def __init__(self, root):
        self.root = str(root)

    def p(self, *a):
        return os.path.join(self.root, *a)


def alive(pid):
    return os.path.exists("/proc/%d" % int(pid))


def proving(**g):
    return {"status": "game", "game": dict({"phase": "proving", "prove_pid": None, "proved_at": T0 - 66 * 60}, **g)}


BROKER = {"broker": {"batch": "b1"}}
ROWS = [
    # name, state, queue entry, job (lock held, jobs table), actor frees it, reader's minutes
    ("the instance: a broker batch proving, its job holds the lock", proving(**BROKER),
     {"state": "running", "batch": "b1"}, (True, {"state": "running"}), False, 0.0),
    ("a broker job launched and inside its grace, lock not yet taken", proving(**BROKER),
     {"state": "running", "batch": "b1"}, (False, {"state": "queued", "launched": T0 - 30}), False, 0.0),
    ("a broker job killed mid-batch: the entry says running, nothing holds the lock", proving(**BROKER),
     {"state": "running", "batch": "b1"}, (False, {"state": "running"}), True, 66.0),
    ("a batch that ended 2 min ago: the hold is 2 min old, not 66", proving(**BROKER),
     {"state": "ran", "batch": "b1"}, (False, {"state": "done", "ended": T0 - 120}), True, 2.0),
    ("a batch that ended 45 min ago and was never stepped: that hold is real", proving(**BROKER),
     {"state": "ran", "batch": "b1"}, (False, {"state": "done", "ended": T0 - 45 * 60}), True, 45.0),
    ("the broker's job runs another batch: this one is not in it", proving(**BROKER),
     {"state": "running", "batch": "b0"}, (True, {"state": "running"}), True, 66.0),
    ("a plain round, its prove pid alive", proving(prove_pid=os.getpid()), None, None, False, 0.0),
    ("a plain round, its prove pid dead", proving(prove_pid=DEAD_PID), None, None, True, 66.0),
    ("a plain round with no pid", proving(), None, None, True, 66.0),
    ("a live-iterating worker that used the bridge 5 min ago",
     {"status": "running", "live_iter": {"at": T0 - 50 * 60, "bridge_seen": T0 - 5 * 60}}, None, None, False, 5.0),
    ("a live-iterating worker idle 47 min", {"status": "running", "live_iter": {"at": T0 - 47 * 60}}, None, None, True, 47.0),
]


def check(ok, what, got):
    print("%s %s -> %s" % ("ok  " if ok else "FAIL", what, got))
    if not ok:
        FAILS.append(what)


def row(n, name, state, entry, job, frees, want):
    root = TMP / ("row%d" % n)
    (root / "items" / "H").mkdir(parents=True)
    (root / "jobs").mkdir()
    (root / "broker").mkdir()
    (root / "items" / "H" / "state.json").write_text(json.dumps(dict(state, item="H")), encoding="utf-8")
    if entry:
        (root / "broker" / "queue.json").write_text(json.dumps({"items": {"H": entry}}), encoding="utf-8")
    fd = None
    if job:
        (root / "jobs" / "broker.json").write_text(json.dumps(job[1]), encoding="utf-8")
        fd = os.open(root / "jobs" / "broker.lock", os.O_CREAT | os.O_RDWR, 0o644)
        if job[0]:
            fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        st, g = dict(state, item="H"), state.get("game") or {}
        if g.get("broker"):             # the actor's own step (_broker_holds) reads the turn; stale_holds skips it
            actor = RB.over(Store(root), "H", g, T0)
        else:
            actor = any(k != "seen" for _, k, _w in G.stale_holds([st], T0, ACTOR, alive, lambda: {}, lambda: {}))
        got, who = OW.rl_game_hold_idle(root / "items", T0)
    finally:
        if fd is not None:
            os.close(fd)
    check(actor == frees, "actor, %s: frees=%s" % (name, frees), actor)
    check(got == want, "reader, %s: reads %s" % (name, want), (got, who))
    if got is not None:
        check(not (got > LINE and not actor), "no alarm on a holder the actor would keep, %s" % name, got)


rule = [r for r in json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))["targets"]
        if r.get("key") == "relentless.game_hold_idle_min"]
check(len(rule) == 1 and rule[0]["value"] == LINE, "the table is written against the shipped alarm line", rule[:1])
for i, r in enumerate(ROWS):
    row(i, *r)
shutil.rmtree(TMP, ignore_errors=True)
print("FAIL: %d checks disagree" % len(FAILS) if FAILS else "PASS: reader and actor agree on every holder")
sys.exit(1 if FAILS else 0)
