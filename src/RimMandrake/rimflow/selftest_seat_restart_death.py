#!/usr/bin/env python3
"""selftest_seat_restart_death.py — the goodbye restart under real process death (ARENA_HANDOFF_PROVE_SURVIVES_PROCESS_DEATH).

The real-process half of the three deaths LiveHandoff.tla models (selftest_seat_restart.py runs on simulated windows).
Every window, Dispatcher and fresh window here is a real child process that dies by a real SIGKILL at a stated point of
the real code: execute(), final_fence(), kill_pid(), decide(), `seat_restart.py intile` and _wake_conductor() are not
replaced. A child only PAUSES at a point (a wrapper that calls the real function) so that the parent can kill it there.
Two things are stubbed, both for isolation: recheck_at_kill and the bridge/game/ledger/helper readers, which would read
this machine's real seats. The live session list is the session files whose pid is alive (`claude agents` needs a real
Claude; assumed: it does not list a dead pid). Nothing outside the temp dir is written and only own children are killed.

A row marked GAP pins what the code does today, which LiveHandoff.tla reports as a broken S5/L3; it flips when the
named item is fixed, and check_models.py's matching case flips with it.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.environ.get("RM_DEATH_TMP") or tempfile.mkdtemp(prefix="selftest_seat_restart_death_")
os.environ["RM_DEATH_TMP"] = TMP
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "claude")
os.environ["RM_SEAT_LOG_DIR"] = os.path.join(TMP, "seat_log")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import doorbell  # noqa: E402
import seat_restart as SR  # noqa: E402

GAP_DEAD = "SEAT_RESTART_FIX_DEAD_WINDOW_UNREAD_LOST"
GAP_WAKE = "SEAT_RESTART_FIX_WAKE_DEATH_READ_LOST"
GAP_STALE = "SEAT_RESTART_FIX_STALE_RECORD_RELAUNCH"
MSG = "owner message that must not be lost"
SCRIPT = os.path.abspath(__file__)
FAILS = []
CHILDREN = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg, flush=True)
    if not ok:
        FAILS.append(msg)


def sched(seat):
    clone = os.path.join(TMP, "clone")
    return {"seats": {seat: {"enabled": True, "session_name": "AGENT " + seat, "clone": clone, "model": "sonnet"}},
            "seat_restart": {"enabled": True, "seats": {seat: {"kind": "conductor", "goodbye_quiet_s": 600}}}}


def stamp(at):
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(at))


def append(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def user_rec(text, at):
    return {"type": "user", "timestamp": stamp(at), "origin": {"kind": "human"}, "uuid": "u-%d" % int(at * 1000),
            "message": {"role": "user", "content": text}}


def end_rec(at):
    return {"type": "assistant", "timestamp": stamp(at),
            "message": {"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "text", "text": "done"}]}}


def pause_at(mark):
    """Tell the parent this child reached the point; go on only if it says so (it may SIGKILL us here instead)."""
    with open(mark, "w") as f:
        f.write(str(os.getpid()))
    while not os.path.exists(mark + ".go"):
        time.sleep(0.02)


def wait_for(path, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(path):
            return True
        time.sleep(0.02)
    return False


def spawn(*args, stdout=None):
    p = subprocess.Popen([sys.executable, SCRIPT, "--child"] + list(args), stdout=stdout, stderr=subprocess.STDOUT)
    threading.Thread(target=p.wait, daemon=True).start()     # reaped at once: a zombie would read as alive
    CHILDREN.append(p)
    return p


def sigkill(p):
    os.kill(p.pid, signal.SIGKILL)
    p.wait()
    time.sleep(0.05)


class Scene:
    """A seat with a live window that has said goodbye: on disk exactly what a tick before the kill left."""

    def __init__(self, seat, wake=None):
        self.seat, self.sch = seat, sched(seat)
        self.cfg = SR.config(self.sch)[seat]
        self.sid, self.gen = "sid-" + seat.lower(), "gen-" + seat.lower()
        self.dir = os.path.join(TMP, seat)
        os.makedirs(self.dir)
        os.makedirs(os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "sessions"), exist_ok=True)
        self.window = spawn("window")
        self.pid = self.window.pid
        self.sess = {"pid": self.pid, "sessionId": self.sid, "cwd": self.cfg["clone"], "name": "AGENT " + seat,
                     "status": "idle", "kind": "interactive"}
        with open(os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "sessions", "%d.json" % self.pid), "w") as f:
            json.dump(self.sess, f)
        self.tx = SR.transcript_path(self.cfg["clone"], self.sid)
        os.makedirs(os.path.dirname(self.tx), exist_ok=True)
        now = time.time()
        self.goodbye_at = now - 1200
        append(self.tx, user_rec("goodbye", self.goodbye_at))
        cursor = os.path.getsize(self.tx)
        append(self.tx, end_rec(now - 1190))
        self.rs = {"source": "request", "ts": now - 1190, "req_ts": now - 1190, "session_id": self.sid, "pid": self.pid,
                   "start": SR.proc_start(self.pid), "ticket": "T", "reason": "goodbye", "busy": 0,
                   "cooldown_s": self.cfg["cooldown_s"], "state": "pending", "cancel_after": self.goodbye_at + 1,
                   "tx_offset": cursor, "tx_path": self.tx, "gen": self.gen, "quiet_since": now - 1000,
                   "seen_size": os.path.getsize(self.tx)}
        self.st_path = os.path.join(self.dir, "state.json")
        self.wake_mode = wake or "none"
        self.save({self.seat: self.rs})

    def save(self, R):
        with open(self.st_path + ".tmp", "w") as f:
            json.dump({"seat_restart": R}, f)
        os.replace(self.st_path + ".tmp", self.st_path)

    def state(self):
        with open(self.st_path) as f:
            return json.load(f)

    def owner_says(self, text=MSG):
        append(self.tx, user_rec(text, time.time()))
        self.rs["seen_size"] = os.path.getsize(self.tx)

    def dispatcher(self, pause):
        """A real Dispatcher tick that claimed the kill and paused at `pause` inside execute()."""
        act = {"do": "restart_kill", "seat": self.seat, "pid": self.pid, "session_id": self.sid,
               "session_name": self.cfg["session_name"], "session_names": [self.cfg["session_name"]], "ticket": "T",
               "gen": self.gen, "argv": [sys.executable, SCRIPT, "--child", "fresh", self.seat, self.gen, self.wake_mode]}
        with open(os.path.join(self.dir, "act.json"), "w") as f:
            json.dump({"act": act, "sch": self.sch}, f)
        p = spawn("dispatcher", self.seat, pause)
        check(wait_for(os.path.join(self.dir, pause)), "%s: the Dispatcher reached %s" % (self.seat, pause))
        return p

    def resume(self, pause, p):
        with open(os.path.join(self.dir, pause + ".go"), "w"):
            pass
        return p.wait(timeout=30)

    def live_sessions(self):
        out = []
        d = os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "sessions")
        for f in os.listdir(d):
            s = SR._read_json(os.path.join(d, f)) or {}
            if s.get("pid") and doorbell._alive(int(s["pid"])):
                out.append(s)
        return out

    def tick(self):
        """A restarted Dispatcher: state.json as it is on disk, the real decide() on real readings."""
        st = self.state()
        ro = dict(SR.default_obs(self.sch, lambda *a: []), helpers=lambda *a: [], work=lambda *a: [], game=lambda s: None,
                  bridge=lambda s: {"state": "MEASURED", "holders": []}, armed=lambda s: None)
        acts = []

        def act(**kw):
            acts.append(kw)
        SR.decide(self.sch, st, {"agents": {"state": "MEASURED", "sessions": self.live_sessions()}, "seat_restart": ro,
                                 "paused": None}, time.time(), True, act)
        self.save(st["seat_restart"])
        return st["seat_restart"][self.seat], acts

    def tile(self):
        """The real `seat_restart.py intile`: exit 3 = no relaunch, else it exec's the record's argv (the fresh window)."""
        out = os.path.join(self.dir, "tile.%d.out" % time.monotonic_ns())
        with open(out, "w") as f:
            p = subprocess.Popen([sys.executable, os.path.join(HERE, "seat_restart.py"), "intile", "--seat", self.seat],
                                 stdout=f, stderr=subprocess.STDOUT)
        threading.Thread(target=p.wait, daemon=True).start()
        CHILDREN.append(p)
        return p, out

    def fresh_by_hand(self, gen):
        """A later window with this token (or none): the fleet launcher or the owner."""
        out = os.path.join(self.dir, "by_hand.%d.out" % time.monotonic_ns())
        with open(out, "w") as f:
            spawn("fresh", self.seat, gen or "-", "none", stdout=f).wait(timeout=30)
        return read(out)

    def record(self):
        return SR._read_json(SR.killed_path(self.seat)) or {}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# -- children ----------------------------------------------------------------------------------------------------------

def child_window():
    while True:
        time.sleep(1)


def child_dispatcher(seat, pause):
    d = os.path.join(TMP, seat)
    with open(os.path.join(d, "act.json")) as f:
        j = json.load(f)
    a, sch = j["act"], j["sch"]
    st_path = os.path.join(d, "state.json")
    with open(st_path) as f:
        st = json.load(f)
    st["seat_restart"][seat].update(state="claimed", claimed_at=time.time())     # decide(), this same tick: memory only
    mark = os.path.join(d, pause)

    def final(seat_, sch_, rs, sf):
        r = SR.final_fence(seat_, sch_, rs, sf)
        if pause == "after_fence":
            pause_at(mark)
        return r

    def before_fence(seat_, sch_, rs, sf):
        if pause == "after_record":
            pause_at(mark)
        return final(seat_, sch_, rs, sf)

    def kill(pid, start=None):
        how = SR.kill_pid(pid, start=start)
        if pause == "after_kill":
            pause_at(mark)
        return how
    try:
        res = SR.execute(a, sch, st, True, time.time(), {"recheck": lambda *x: [], "final": before_fence, "kill": kill})
    finally:                                     # dispatcher.tick's finally: the only save of a restart's state
        with open(st_path + ".tmp", "w") as f:
            json.dump(st, f)
        os.replace(st_path + ".tmp", st_path)
    print(res, flush=True)


def child_fresh(seat, gen, mode):
    """A fresh window's first turn: the real wake read; then it lives until killed."""
    d = os.path.join(TMP, seat)
    print("FRESH %d" % os.getpid(), flush=True)
    real = SR.write_killed

    def write(seat_, rec, root=None):
        if mode == "die_before_mark":
            pause_at(os.path.join(d, "wake_read"))
        real(seat_, rec, root)
    SR.write_killed = write
    rec = SR._read_json(SR.killed_path(seat)) or {}
    SR._wake_conductor(seat, SR.config(sched(seat))[seat], rec, gen=None if gen == "-" else gen)
    sys.stdout.flush()
    if mode == "die_after_mark":
        pause_at(os.path.join(d, "wake_read"))
    elif mode == "live":
        pause_at(os.path.join(d, "fresh_up"))


# -- the deaths --------------------------------------------------------------------------------------------------------

def test_old_window_dies_before_the_record():
    s = Scene("DEATHA")
    s.owner_says()                  # the window took it into its transcript and died before answering
    sigkill(s.window)
    rs, acts = s.tick()
    check(rs["state"] == "cancelled" and not s.record(), "death 1, no record yet: the next tick cancels (%s)" % rs["state"])
    p, _ = s.tile()
    check(p.wait(timeout=30) == 3, "GAP %s: no record, so the tile does not relaunch (exit 3)" % GAP_DEAD)
    check(MSG not in s.fresh_by_hand(None), "GAP %s: a later window never reads his message" % GAP_DEAD)


def test_old_window_dies_after_the_record_message_at_fence():
    s = Scene("DEATHB")
    d = s.dispatcher("after_record")
    s.owner_says()
    sigkill(s.window)
    check(s.resume("after_record", d) == 0, "death 1, input at the fence: the tick ends")
    check(s.record().get("aborted"), "the fence read his message and aborted the record")
    rs, _ = s.tick()
    check(rs["state"] == "cancelled", "the next tick cancels: the window is gone (%s)" % rs["state"])
    p, _ = s.tile()
    check(p.wait(timeout=30) == 3, "GAP %s: an aborted record gets no relaunch" % GAP_DEAD)
    text = s.fresh_by_hand(None)
    check("nothing to recover" in text, "GAP %s: the wake says nothing to recover, of a dead window with his message "
          "unanswered (it quotes only the reason's first words)" % GAP_DEAD)


def test_old_window_dies_after_the_fence():
    s = Scene("DEATHC", wake="live")
    d = s.dispatcher("after_fence")
    s.owner_says()                  # the milliseconds between the fence and the signal
    sigkill(s.window)
    check(s.resume("after_fence", d) == 0, "death 1, after the fence: the tick ends")
    rs = s.state()["seat_restart"][s.seat]
    check(rs["state"] == "killed" and rs.get("kill") == "already gone", "kill_pid: already gone, not a failure (%s %s)"
          % (rs["state"], rs.get("kill")))
    p, out = s.tile()
    check(wait_for(os.path.join(s.dir, "fresh_up")), "the tile relaunched on the record")
    check(MSG in read(out), "SURVIVES: the fresh window's wake read his message")
    sigkill(p)


def test_dispatcher_dies_after_the_record():
    s = Scene("DEATHD", wake="live")
    d = s.dispatcher("after_record")
    sigkill(d)
    check(s.state()["seat_restart"][s.seat]["state"] == "pending", "death 2: SIGKILL lost the tick; state.json says pending")
    check(s.window.poll() is None and s.record().get("gen") == s.gen, "the window lives and the record is on disk")
    rs, acts = s.tick()
    check(rs["state"] == "claimed" and any(a["do"] == "restart_kill" for a in acts),
          "SURVIVES: the restarted Dispatcher judges again and claims (%s %s)" % (rs["state"], [a["do"] for a in acts]))
    d2 = s.dispatcher("after_kill")
    s.owner_says()                  # accepted in the instant before the signal
    check(s.resume("after_kill", d2) == 0, "the second tick's kill lands")
    p, out = s.tile()
    check(wait_for(os.path.join(s.dir, "fresh_up")) and MSG in read(out), "SURVIVES: relaunched, and the wake read him")
    sigkill(p)


def test_dispatcher_dies_after_the_kill():
    s = Scene("DEATHE", wake="live")
    d = s.dispatcher("after_kill")
    sigkill(d)
    check(s.window.poll() is not None, "death 2: the window was killed by the real kill_pid before the Dispatcher died")
    s.owner_says()                  # accepted in the instant before the signal: past the cursor
    p, out = s.tile()               # the Dispatcher is still dead
    check(wait_for(os.path.join(s.dir, "fresh_up")), "SURVIVES: the tile relaunched with no Dispatcher alive")
    check(MSG in read(out), "SURVIVES: the wake read his message with no Dispatcher alive")
    rs, acts = s.tick()
    check(rs["state"] == "cancelled", "the restarted Dispatcher, on a stale state.json, cancels what already happened "
          "(%s: its first-turn verification is lost, %s)" % (rs["state"], GAP_STALE))
    sigkill(p)


def test_dispatcher_dies_then_input_cancels_and_the_window_quits():
    s = Scene("DEATHF", wake="live")
    d = s.dispatcher("after_record")
    sigkill(d)
    s.owner_says()                  # the old window is alive: it answers him, and the restart must be off
    append(s.tx, end_rec(time.time()))
    rs, _ = s.tick()
    check(rs["state"] == "cancelled", "the input cancels the restart (%s)" % rs["state"])
    check(not s.record().get("aborted"), "GAP %s: the cancelled restart's record stays armed" % GAP_STALE)
    sigkill(s.window)               # he quits the window, inside the tile's window
    p, out = s.tile()
    check(wait_for(os.path.join(s.dir, "fresh_up")), "GAP %s: a cancelled restart still relaunches" % GAP_STALE)
    check(MSG in read(out), "GAP %s: and replays what the old window already answered" % GAP_STALE)
    sigkill(p)


def _to_fresh(seat, mode):
    s = Scene(seat, wake=mode)
    d = s.dispatcher("after_kill")
    s.owner_says()
    s.resume("after_kill", d)
    p, out = s.tile()
    check(wait_for(os.path.join(s.dir, "wake_read")), "%s: the fresh window reached its wake point" % seat)
    return s, p, out


def test_fresh_window_dies_before_the_wake_marks():
    s, p, out = _to_fresh("DEATHG", "die_before_mark")
    sigkill(p)
    check(not s.record().get("woken_at"), "death 3, before woken_at: the record is not consumed")
    q, _ = s.tile()
    check(q.wait(timeout=30) == 3, "GAP %s: the tile's O_EXCL marker refuses a second relaunch" % GAP_WAKE)
    check(MSG not in s.fresh_by_hand(None), "GAP %s: a window with no token gets a pointer, not the message" % GAP_WAKE)
    check(MSG in s.fresh_by_hand(s.gen), "the record survives for a window that holds the token")


def test_fresh_window_dies_after_the_wake_marks():
    s, p, out = _to_fresh("DEATHH", "die_after_mark")
    check(MSG in read(out), "death 3: the wake printed his message")
    sigkill(p)
    check(s.record().get("woken_at"), "the wake marked the record before anything answered him")
    q, _ = s.tile()
    check(q.wait(timeout=30) == 3, "GAP %s: no second relaunch" % GAP_WAKE)
    text = s.fresh_by_hand(s.gen)
    check("not replayed" in text and MSG not in text, "GAP %s: even the same token is refused: read, unanswered, gone"
          % GAP_WAKE)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return {"window": child_window, "dispatcher": child_dispatcher, "fresh": child_fresh}[sys.argv[2]](*sys.argv[3:])
    if not (doorbell.state_dir().startswith(TMP) and SR.claude_home().startswith(TMP)):
        print("FAIL  refusing to run: state or claude home outside the temp dir")
        return 1
    try:
        for name, fn in sorted(globals().items()):
            if name.startswith("test_"):
                print("-- " + name, flush=True)
                fn()
    finally:
        for c in CHILDREN:
            if c.poll() is None:
                c.kill()
        shutil.rmtree(TMP, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
