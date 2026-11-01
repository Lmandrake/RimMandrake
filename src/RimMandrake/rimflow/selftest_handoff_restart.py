#!/usr/bin/env python3
"""selftest_handoff_restart.py — HANDOFF_FIX_RESTART_TWENTY_SECONDS on the real path.

Owner 2026-11-01: "20 seconds, build it now and implement." dispatcher.tick() runs with obs=None on the production schedule,
over selftest_idle_bringback's World: real child processes, session files, transcripts, doorbell and SIGTERM. cmd_request
is the real one (only the shard reading and the wall-clock of its ts are replaced); the clock is simulated in seconds, ticks
landing where kick_handoff puts them.
  wait      the kill lands on the first tick past 20 s, never before
  rings     no ring while it is pending; a ring still in the inbox is withdrawn; a ring the window already took holds
            nothing (the live hold of 2026-11-01); a ring that lands anyway neither cancels nor fails it
  human     his own text in the window still cancels
  deferred  helpers drain, the unpublished shard holds, then it fires once; the bring-back stays out
  spin      a fresh window handing off with no work is refused and alarmed; with work, or past the cooldown, it fires
  fresh     a restart ends in work: the fresh window, armed, is verified and rung on one tick, backoff or no; the doorbell
            kicks that tick; an empty queue or an unarmed window is left alone
  hook      the words, the block, the cap, the alarm; a passing turn; the Conductor untouched
  doorbell  leaves a ring in the inbox through the hold
"""
import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_idle_bringback as IB  # noqa: E402

D, SR, doorbell, SEAT = IB.D, IB.SR, IB.doorbell, IB.SEAT
check, FAILS, REAL = IB.check, IB.FAILS, IB.REAL
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", ".claude", "hooks")))
import handoff_restart as H  # noqa: E402

CFG = SR.config(REAL)[SEAT]
WAIT = max(CFG["grace_s"], CFG["quiet_s"])
os.environ["SEAT_RESTART_NO_TICK"] = "1"


class Hw(IB.World):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.deaf = False                # True: past the doorbell's hold, a ring lands anyway; "away": none is taken

    def spawn(self, status="idle", arm=None):
        return super().spawn(status, self.arm_fresh if arm is None else arm)

    def schedule(self):
        s = super().schedule()
        s["seat_restart"]["dry"] = False
        return s

    def at(self, seconds):
        """Tick at now+seconds, as a kick does."""
        self.now += seconds
        for w in list(self.windows):
            if w["proc"].poll() is not None:
                self.windows.remove(w)
                self.gone.append(w)
                self.kills.append(self.now)
        if self.owed is not None and self.now >= self.owed:
            self.owed = None
            self.spawn()
        for w in self.windows:
            if self.deaf != "away" and (self.deaf or not SR.handoff_drain(SEAT, w["sid"], now=self.now)):
                if doorbell.take_ring(SEAT, session_id=w["sid"]):
                    self.landed(w)
                    doorbell.arm(SEAT, w["sid"], pid=w["pid"])
        acts = D.tick(self.sch, True, now=self.now, fx={"seat_restart": {"fallback": self.fallback}})
        self.acts += acts
        self.tile()
        return acts

    def landed(self, w):
        self.write(w, {"type": "user", "origin": {"kind": "task-notification"},
                       "message": {"role": "user", "content": "[RimFlow Dispatcher] ring"}})
        self.end_turn(w)

    def say_ready(self, w):
        self.write(w, {"type": "assistant", "message": {"stop_reason": "end_turn", "usage": {"input_tokens": 1000},
                                                        "content": [{"type": "text", "text": "done.\n\nHANDOFF READY"}]}})

    def hand_off(self, w, live=()):
        """The real cmd_request, as the hook calls it, then the request's ts brought onto the simulated clock."""
        os.environ["RM_SEAT_RESTART_SCHEDULE"] = os.path.join(self.dir, "sched.json")
        SR.unpublished_shard = lambda seat, repo: self.shard
        SR.helpers_of = lambda path, now, stale=None: list(self.helpers)
        SR._tick_soon = lambda *d: self.kicks.append(d)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.cmd_request(argparse.Namespace(seat=SEAT, ticket="HANDOFF", reason="handoff", note="", fresh=True,
                                                   pid=w["pid"]))
        p = SR.request_path(SEAT)
        req = json.load(open(p))
        req["ts"] = self.now
        with open(p, "w") as f:
            json.dump(req, f)
        return rc, out.getvalue()

    arm_fresh = True
    shard = None
    helpers = ()
    kicks = []

    def kill_at(self):
        return [a["at"] for a in self.acts if a.get("do") == "restart_kill"]

    def killed(self):
        return bool(self.count("restart_kill"))


def start(name, **kw):
    w = Hw(name, **kw)
    IB.patch(w)
    w.spawn()
    return w


def ring_of(w):
    return (D.load_state(w.state).get("seats") or {}).get(SEAT, {}).get("ring") or {}


def seat_state(w):
    return (D.load_state(w.state).get("seat_restart") or {}).get(SEAT) or {}


def first_ring(w):
    """Ticks until the Dispatcher rings this idle window."""
    for _ in range(60):
        if w.count("ring"):
            return
        w.at(IB.TICK)


def ready(w):
    """One window that has just said it, handed off, the request on disk. -> (window, start time)."""
    win = w.windows[0]
    w.say_ready(win)
    rc, out = w.hand_off(win)
    return win, w.now, rc, out


def test_schedule():
    bench = SR.config(REAL)["BENCH"]
    check(CFG["grace_s"] == 20 and CFG["quiet_s"] == 20, "FOUNDRY grace_s and quiet_s are 20")
    check(bench["grace_s"] == 0 and bench["goodbye_quiet_s"] == 0, "the Conductor's goodbye stays instant")
    check(SR.says_handoff_ready("x\n\n**HANDOFF READY**") and SR.says_handoff_ready("HANDOFF READY.")
          and SR.says_handoff_ready("HANDOFF READY: all closed") and SR.says_handoff_ready("HANDOFF READY\n\nbye"),
          "the words, bold, stopped, opening a last line, or a line of their own")
    check(not SR.says_handoff_ready("> HANDOFF READY") and not SR.says_handoff_ready("`HANDOFF READY`")
          and not SR.says_handoff_ready("e.g.\n```\nHANDOFF READY\n```\nok"), "NEGATIVE: a quote, code span or fence is not the signal")
    check(not SR.says_handoff_ready("I will say HANDOFF READY soon\nok") and not SR.says_handoff_ready("")
          and not SR.says_handoff_ready("say `HANDOFF READY` once `--check` passes"), "the words inside a sentence are not")


def test_wait():
    w = start("wait")
    w.at(120)
    win, t0, rc, out = ready(w)
    check(rc == 0 and "RESTART REQUESTED" in out, "the request lands: %s" % out[:80])
    check(json.load(open(SR.request_path(SEAT))).get("handoff") is True, "marked a handoff")
    check(w.kicks and w.kicks[-1][0] == WAIT + 1, "ticks kicked just past the wait: %s" % (w.kicks[-1:],))
    w.at(WAIT - 1)
    check(not w.killed() and SR.drain_of(SEAT, win["sid"], now=w.now), "19 s: still waiting, draining")
    w.at(2)
    check(w.killed(), "21 s: killed on the first tick past 20 (%s)" % [a.get("why") for a in w.acts if a.get("do") == "restart_hold"][-1:])
    print("      wait measured on the simulated clock: %d s" % (w.now - t0))
    w.close()


def test_rings():
    w = start("idle_queue")                  # idle, stalled, work waiting: the ring would fire today
    w.at(300)
    w.queue = {"id": "READY_TICKET_WAITING"}
    win, t0, *_ = ready(w)
    n = w.count("ring")
    for dt in (5, 5, 5):
        w.at(dt)
    check(w.count("ring") == n, "no ring through the wait (%d)" % (w.count("ring") - n))
    w.at(WAIT - 14)
    check(w.killed(), "and the kill still lands at 21 s")
    w.close()

    w = start("inbox")                       # a ring rung just before the handoff, not yet taken
    w.deaf = "away"
    first_ring(w)
    check(os.path.exists(doorbell.inbox_path(SEAT)), "a ring sits in the inbox, unconsumed")
    w.deaf = False
    ready(w)
    w.at(WAIT + 1)
    check(w.count("withdraw") == 1 and not os.path.exists(doorbell.inbox_path(SEAT)), "it is withdrawn, never delivered")
    w.at(10)
    check(w.killed(), "the kill lands on the next kick (31 s)")
    w.close()

    w = start("consumed")                    # the live hold: rung, taken, restart requested after; held to handoff_s before this
    win = w.windows[0]
    first_ring(w)
    check(w.count("ring") >= 1, "rung")
    w.at(7)                                  # the doorbell takes it; the Dispatcher's record stays until handoff_s
    check(ring_of(w).get("consumed_at"), "consumed, still in ss.ring: %s" % str(ring_of(w))[:80])
    t0 = w.now
    w.say_ready(win)
    w.hand_off(win)
    w.at(WAIT + 1)
    check(w.killed(), "a ring the window already took holds nothing: killed at %d s" % (w.now - t0))
    check(not ring_of(w), "and the ring ends with the window")
    w.close()

    w = start("landed")                      # the worst case: one lands anyway, mid-wait
    win, t0, *_ = ready(w)
    w.at(5)
    w.landed(win)
    w.at(WAIT - 5 + 1)
    check(not w.killed() and not w.count("restart_cancel"), "a ring at 5 s does not cancel; its record starts the quiet again")
    check(os.path.exists(SR.request_path(SEAT)) or seat_state(w).get("state") == "pending", "still pending")
    for _ in range(6):
        w.at(1 if w.killed() else 5)
    check(w.killed() and not w.count("restart_fail"), "no busy failure: it fires once the window is quiet again")
    w.close()


def test_human():
    w = start("human")
    win, *_ = ready(w)
    w.at(5)
    w.human(win)
    w.at(WAIT)
    w.at(30)
    check(not w.killed() and w.count("restart_cancel") == 1, "his text in the window cancels it")
    w.close()


def test_deferred():
    w = start("deferred")
    win = w.windows[0]
    w.helpers = [{"id": "h1", "desc": "a helper", "alive": True, "last_at": w.now}]
    w.say_ready(win)
    t0 = w.now
    rc, out = w.hand_off(win)
    check(rc == 0 and "DEFERRED" in out, "helpers alive: DEFERRED (%s)" % out[:60])
    w.at(30)
    w.at(400)
    check(not w.killed(), "held while the helper lives")
    w.helpers[0]["last_at"] = w.now
    w.at(IB.LIMIT - 300)
    check(w.count("idle_bringback:" + SEAT) == 0 and not w.count("ring"), "no bring-back and no ring through a long drain")
    w.helpers = [dict(w.helpers[0], alive=False, last_at=w.now)]
    w.shard = "shard dirty"
    w.end_turn(win)                          # the last notice woke it
    w.at(21)
    check(not w.killed() and w.acts and any("unpublished" in str(a.get("why")) for a in w.acts if a.get("do") == "restart_hold"),
          "the helper is done, the shard is not published: held, no gap")
    w.shard = None
    w.at(10)
    check(w.count("restart_kill") == 1, "published: it fires, once")
    w.close()


def test_spin():
    w = start("spin")
    ready(w)
    w.at(WAIT + 1)
    w.at(10)
    w.at(120)
    w.at(120)
    w.at(120)
    check(len(w.windows) == 1 and w.count("restart_verified") == 1, "a fresh window, verified (%d)" % len(w.windows))
    fresh = w.windows[0]
    w.say_ready(fresh)
    w.hand_off(fresh)
    w.at(WAIT + 1)
    w.at(60)
    check(w.count("restart_kill") == 1, "the fresh window handing off at once is not killed")
    check(sum(1 for a in w.acts if a.get("kind") == "restart:%s:handoff_spin" % SEAT) >= 1, "and the Conductor is alarmed")
    w.hand_off(fresh)
    w.at(WAIT + 1)
    check(w.count("restart_kill") == 1, "nor on a second try")
    w.take()
    w.at(30)
    w.say_ready(fresh)
    w.hand_off(fresh)
    w.at(1)
    w.at(WAIT + 1)
    check(w.count("restart_kill") == 2, "real work since the restart: the handoff stands")
    w.close()

    w = start("spin_cool")
    ready(w)
    for dt in (WAIT + 1, 10, 120, 120, 120):
        w.at(dt)
    fresh = w.windows[0]
    w.at(CFG["cooldown_s"] + 60)
    w.say_ready(fresh)
    w.hand_off(fresh)
    w.at(1)
    w.at(WAIT + 1)
    check(w.count("restart_kill") == 2, "past the cooldown it fires: at most one per cooldown_s")
    w.close()


def killed_world(name, queue=True, arm=True):
    """Handed off and killed, the dead window's backoff on record; the next tick finds a fresh idle window. -> world."""
    w = start(name)
    w.arm_fresh = arm
    ready(w)
    w.at(WAIT + 1)
    check(w.killed(), "killed")
    w.queue = {"id": "READY_TICKET_WAITING"} if queue else None
    p = os.path.join(w.state, "state.json")
    st = json.load(open(p))
    st["seats"][SEAT].update(cooldown_until=w.now + 1500, nh_until=w.now + 1500, nh_tickets=["READY_TICKET_WAITING"],
                             nh_streak=2)                  # the dead window declined this very ticket
    with open(p, "w") as f:
        json.dump(st, f)
    return w


def test_fresh():
    w = killed_world("fresh")
    n = w.count("ring")
    w.at(40)                                 # the doorbell armed: the kick's tick
    check(w.count("restart_relaunched") == 1 and w.count("restart_verified") == 1, "seen and verified on one tick")
    check(w.count("ring") == n + 1 and ring_of(w).get("ticket") == "READY_TICKET_WAITING",
          "and rung on that tick, past the dead window's backoff and stall clock")
    check(not any(k in (D.load_state(w.state)["seats"][SEAT]) for k in ("cooldown_until", "nh_tickets", "nh_streak")),
          "the backoff died with its window")
    w.close()

    w = killed_world("fresh_empty", queue=False)
    w.at(40)
    check(w.count("restart_verified") == 1 and not w.count("ring"), "an empty queue: no ring")
    w.close()

    w = killed_world("fresh_unarmed", arm=False)
    w.at(40)
    check(w.count("restart_relaunched") == 1 and not w.count("restart_verified") and not w.count("ring"),
          "still in its first turn, no doorbell: not verified, not rung")
    doorbell.arm(SEAT, w.windows[0]["sid"], pid=w.windows[0]["pid"])
    w.at(5)
    check(w.count("restart_verified") == 1 and w.count("ring") == 1, "its first stop arms; the next tick rings")
    w.close()

    w = start("kick")
    kicks = []
    SR._tick_soon = lambda *d: kicks.append(d)
    p = os.path.join(w.state, "state.json")
    for state, sid, want in (("killed", "new", True), ("relaunched", "new", True), ("verified", "new", False),
                             ("killed", "old", False), ("pending", "new", False)):
        with open(p, "w") as f:
            json.dump({"seat_restart": {SEAT: {"state": state, "session_id": "old"}}}, f)
        kicks.clear()
        check(SR.kick_fresh(SEAT, sid) is want and bool(kicks) is want, "doorbell arming: %s, session %s -> kick %s" % (state, sid, want))
    w.close()


class Fake:
    """seat_restart for the hook: the real words, paths and files; drain and helpers set by the case."""
    def __init__(self, drain=False, live=False, unpub=None, cfg=None):
        self.drain, self.live, self.unpub = drain, live, unpub
        self.cfg, self.kicked = cfg or dict(CFG), 0
        self.dir = tempfile.mkdtemp(prefix="hook_", dir=IB.TMP)
    says_handoff_ready = staticmethod(SR.says_handoff_ready)
    last_assistant_text = staticmethod(SR.last_assistant_text)
    _read_json = staticmethod(SR._read_json)
    _write_json = staticmethod(SR._write_json)

    def config(self, _):
        return {SEAT: self.cfg}

    def _schedule(self):
        return {}

    def refused_path(self, seat):
        return os.path.join(self.dir, "refused.json")

    def handoff_drain(self, seat, sid):
        return self.drain

    def helpers_of(self, path, now, stale=None):
        return [{"alive": self.live}]

    def unpublished_shard(self, seat, repo):
        return self.unpub

    def kick_handoff(self, cfg):
        self.kicked += 1


def hook_case(fake, text="x\nHANDOFF READY", chk=(0, "ok"), req=(0, "RESTART REQUESTED"), lands=True):
    calls = []

    def _check(seat):
        calls.append("check")
        return chk

    def _request(seat):
        calls.append("request")
        fake.drain = lands and req[0] == 0
        return req
    H.check, H.request = _check, _request
    out = io.StringIO()
    did = H.on_stop({"session_id": "s1", "transcript_path": None, "last_assistant_message": text}, SEAT, fake, out)
    return did, calls, json.loads(out.getvalue()) if out.getvalue() else None


def test_hook():
    f = Fake()
    did, calls, blk = hook_case(f)
    check(did == "requested" and calls == ["check", "request"] and blk is None, "the words + a passing check: requested")
    did, calls, _ = hook_case(Fake(), text="more to do")
    check(did == "no" and not calls, "no words: nothing runs")
    did, calls, _ = hook_case(Fake(cfg=dict(CFG, kind="conductor")))
    check(did == "skip" and not calls, "the Conductor is out of scope")
    f = Fake()
    did, calls, blk = hook_case(f, chk=(1, "NOT READY - unpushed"))
    check(did == "refused" and calls == ["check"] and blk["decision"] == "block" and "unpushed" in blk["reason"],
          "a failed check blocks, naming it, and requests nothing")
    did, calls, blk = hook_case(f, req=(3, "REFUSED: ledger shard unpublished"))
    check(did == "refused" and blk and "unpublished" in blk["reason"] and "2/3" in blk["reason"], "a refused request blocks too")
    hook_case(f, chk=(1, "x"))
    did, calls, blk = hook_case(f, chk=(1, "x"))
    check(did == "refused" and blk is None and f._read_json(f.refused_path(SEAT))["n"] == 4,
          "past the cap the turn ends: never a stuck window, and the file stands")
    did, calls, blk = hook_case(f)
    check(did == "requested" and not os.path.exists(f.refused_path(SEAT)), "a landed request clears the refusal")
    did, _, blk = hook_case(Fake(), req=(0, "seat_restart is not enabled"), lands=False)
    check(did == "refused" and blk, "rc 0 with no request recorded is a refusal")
    f = Fake(live=True)
    did, calls, _ = hook_case(f, chk=(1, "doing items open"))
    check(did == "requested" and calls == ["request"], "helpers alive: the check waits, the request defers")
    did, calls, _ = hook_case(f, text="helper notice read")
    check(did == "draining" and not f.kicked, "draining with a helper left: nothing kicked")
    f.live, f.unpub = False, "BENCH shard dirty"
    did, calls, blk = hook_case(f, text="helper notice read")
    check(did == "refused" and blk and "dirty" in blk["reason"], "the last helper done and the shard unpublished: told, blocked")
    f.unpub = None
    did, calls, blk = hook_case(f, text="helper notice read")
    check(did == "kicked" and f.kicked == 1 and calls == ["check"], "published: ticks kicked at this turn's end")

    w = start("refused_alarm")               # the Dispatcher's side: the same file, the real tick
    win = w.windows[0]
    SR._write_json(SR.refused_path(SEAT), {"session_id": win["sid"], "ts": w.now, "why": "shard unpublished", "n": 4})
    w.at(60)
    k = "restart:%s:handoff_refused" % SEAT
    check(w.count("alarm", k) == 0, "inside the window's chance to fix it: quiet")
    w.at(120)
    check(w.count("alarm", k) == 1, "a refusal left standing alarms")
    w.at(300)
    check(w.count("alarm", k) == 1, "once")
    w.close()


def test_doorbell():
    with tempfile.TemporaryDirectory(dir=IB.TMP) as root:
        os.makedirs(os.path.join(root, "inbox"))
        doorbell.arm("X", "s", root, pid=os.getpid())
        with open(doorbell.inbox_path("X", root), "w") as f:
            json.dump({"ring_id": "r", "message": "ring"}, f)
        ticks = {"n": 0}
        t = {"now": 0}

        def sleep(_):
            t["now"] += 1
            ticks["n"] += 1
        code, _ = doorbell.wait("X", "s", root, max_wait=5, clock=lambda: t["now"], sleep=sleep, hold=lambda: True)
        check(code == 0 and os.path.exists(doorbell.inbox_path("X", root)), "a hold leaves the ring in the inbox")
        t["now"] = 0
        code, _ = doorbell.wait("X", "s", root, max_wait=5, clock=lambda: t["now"], sleep=sleep, hold=lambda: t["now"] < 2)
        check(code == 2, "the hold ending lets it through: a window that stayed open is not deaf")
    real = time.time()
    hold = doorbell.handoff_hold("NOSEAT", {"session_id": "s", "last_assistant_message": "HANDOFF READY"}, clock=lambda: real)
    check(hold(), "this turn said it: held while the hook runs")
    hold = doorbell.handoff_hold("NOSEAT", {"session_id": "s", "last_assistant_message": "ok"}, clock=lambda: real)
    check(not hold(), "any other turn: no hold")


if __name__ == "__main__":
    try:
        for t in (test_schedule, test_wait, test_rings, test_human, test_deferred, test_spin, test_fresh, test_hook, test_doorbell):
            print("== " + t.__name__)
            t()
    finally:
        IB.shutil.rmtree(IB.TMP, ignore_errors=True)
    print("FAILED %d: %s" % (len(FAILS), FAILS) if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)
