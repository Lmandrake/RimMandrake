"""selftest_launch_ready.py - launch_ready.run() never reports READY from evidence that predates the launch.

Written failing-first (LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE). Each case is a scripted fake world: a clock, a
process table, a Player.log, a listener table, a ping. The cases are the ways the old launch_and_wait.sh lied or
could lie: an old token line with no process, Steam never starting the game, a zombie load, a duplicate game, a
listener owned by someone else, a Core-only reset.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))

import launch_ready as L  # noqa: E402

POL = {"launch_to_process_s": 60, "process_to_bridge_warn_s": 100, "process_to_bridge_deadline_s": 300,
       "bridge_to_dispatcher_s": 30, "kill_existing_grace_s": 30, "name": "test"}
TOKEN_LOG = ("Mono path[0]\n[RimBridge] GABP server running standalone on port 5174\n"
             "[RimBridge] Bridge token: abc123\n")
OLD_LOG = "old run\n[RimBridge] GABP server running standalone on port 5174\n[RimBridge] Bridge token: OLD999\n"
FULL = ["ludeon.rimworld", "ludeon.rimworld.royalty", "brrainz.harmony", "mandrake.rm.flowworks"]


class Fake:
    """t advances only through sleep(). spawn_at: when the new game process appears (None = never)."""

    def __init__(self, old_procs=(), spawn_at=5.0, token_at=20.0, log_text=TOKEN_LOG, old_log=OLD_LOG,
                 exit_at=None, listener="game", ping_ok=True, active=FULL, dup_at=None, kill_works=True):
        self.t = 1000.0
        self.old = [{"pid": 11, "start": 10.0}] if old_procs else []
        self.kill_works = kill_works
        self.spawn_at, self.token_at, self.exit_at, self.dup_at = spawn_at, token_at, exit_at, dup_at
        self.log_text, self.listener, self.ping_ok, self.active = log_text, listener, ping_ok, active
        self.log = old_log            # what is on disk before launch
        self.log_mtime = 500.0
        self.launched = None
        self.archived = []
        self.killed = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s
        if self.launched is not None and self.token_at is not None and self.t - self.launched >= self.token_at:
            if self.log != self.log_text:
                self.log, self.log_mtime = self.log_text, self.t

    def list_game_procs(self):
        out = list(self.old)
        if self.launched is not None and self.spawn_at is not None:
            el = self.t - self.launched
            if el >= self.spawn_at and (self.exit_at is None or el < self.exit_at):
                out.append({"pid": 4242, "start": self.launched + self.spawn_at})
            if self.dup_at is not None and el >= self.dup_at:
                out.append({"pid": 4343, "start": self.launched + self.dup_at})
        return out

    def kill_pid(self, pid):
        self.killed.append(pid)
        if self.kill_works:
            self.old = [p for p in self.old if p["pid"] != pid]

    def archive_log(self):
        if self.log is None:
            return None
        self.archived.append(self.log)
        self.log = None
        return "/archive/Player.%d.log" % len(self.archived)

    def launch(self):
        self.launched = self.t
        if self.spawn_at is not None:
            self.log, self.log_mtime = "Mono path[0]\n", self.t + 1

    def read_log(self):
        return self.log, self.log_mtime

    def listener_pid(self, port):
        return {"game": 4242, "other": 999, None: None}[self.listener]

    def ping(self, port, token):
        return (self.ping_ok, "pong" if self.ping_ok else "timed out")

    def active_mods(self):
        return self.active


def run(**kw):
    f = Fake(**kw)
    r = L.run(f, POL, log=lambda *a: None)
    return f, r


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    good = []
    f, r = run()
    good.append(case("happy path is READY with this run's pid and token",
                     r["verdict"] == "READY" and r["pid"] == 4242 and r["token_seen"] == "abc123", r))
    good.append(case("old log was archived before launch", f.archived == [OLD_LOG]))

    f, r = run(spawn_at=None, token_at=None)
    good.append(case("Steam never starts the game -> LAUNCH_NO_PROCESS, nonzero",
                     r["verdict"] == "LAUNCH_NO_PROCESS" and L.exit_code(r) != 0, r["verdict"]))

    # the old bug: an old token line in the log and no process at all
    f, r = run(spawn_at=None, token_at=None, old_log=OLD_LOG)
    good.append(case("old token line with no process is never READY", r["verdict"] != "READY", r["verdict"]))

    f, r = run(token_at=None)
    good.append(case("zombie load (process alive, no token) -> DEADLINE_ALIVE, not killed",
                     r["verdict"] == "DEADLINE_ALIVE" and 4242 not in f.killed and L.exit_code(r) != 0, r["verdict"]))
    good.append(case("zombie load warned at the warn threshold first", r.get("warned") is True))

    f, r = run(exit_at=10.0)
    good.append(case("process exits mid-load -> PROCESS_EXITED", r["verdict"] == "PROCESS_EXITED", r["verdict"]))

    f, r = run(dup_at=8.0)
    good.append(case("second game process -> DUPLICATE_PROCESS", r["verdict"] == "DUPLICATE_PROCESS", r["verdict"]))

    f, r = run(listener="other")
    good.append(case("listener owned by another pid -> LISTENER_NOT_OURS", r["verdict"] == "LISTENER_NOT_OURS",
                     r["verdict"]))

    f, r = run(ping_ok=False)
    good.append(case("dispatcher silent -> DISPATCHER_SILENT", r["verdict"] == "DISPATCHER_SILENT", r["verdict"]))

    f, r = run(active=["ludeon.rimworld", "ludeon.rimworld.royalty"])
    good.append(case("Core-only active list after load -> CORE_ONLY", r["verdict"] == "CORE_ONLY", r["verdict"]))

    f, r = run(log_text=TOKEN_LOG + "Resetting mods config\n")
    good.append(case("'Resetting mods config' in this run's log -> MODS_RESET",
                     r["verdict"] == "MODS_RESET", r["verdict"]))

    f, r = run(log_text="Mono\nNullReferenceException: boom\n  at X\n" + TOKEN_LOG)
    good.append(case("first exception recorded but not fatal",
                     r["verdict"] == "READY" and "NullReferenceException" in (r.get("first_exception") or ""), r))

    f, r = run(old_procs=True)
    good.append(case("pre-existing game killed by PID before launch", f.killed == [11] and r["verdict"] == "READY",
                     (f.killed, r["verdict"])))

    f, r = run(old_procs=True, kill_works=False)
    good.append(case("unkillable old game -> KILL_FAILED, no launch", r["verdict"] == "KILL_FAILED" and
                     f.launched is None, r["verdict"]))

    # token line present but the log on disk predates the launch (stale drvfs read / rotation failed)
    class Stale(Fake):
        def archive_log(self):
            self.archived.append(self.log)
            return "/archive/x"          # claims success but leaves the old log in place

        def launch(self):
            self.launched = self.t
    f = Stale(token_at=None)
    r = L.run(f, POL, log=lambda *a: None)
    good.append(case("old log left in place is never read as this run's token", r["verdict"] != "READY",
                     r["verdict"]))

    # the policy file: one source, kill_on_deadline refused, profiles chosen by list size
    import json
    import tempfile
    import load_policy
    pol = load_policy.load()
    good.append(case("shipped policy loads, kill_on_deadline false", pol["kill_on_deadline"] is False))
    good.append(case("15-mod list -> minimal, 551 -> full, unknown -> full",
                     load_policy.profile_name(15, pol) == "minimal" and load_policy.profile_name(551, pol) == "full"
                     and load_policy.profile_name(None, pol) == "full"))
    bad = dict(pol, kill_on_deadline=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(bad, fh)
    try:
        load_policy.load(fh.name)
        refused = False
    except load_policy.PolicyError:
        refused = True
    os.unlink(fh.name)
    good.append(case("a policy that kills on deadline is refused", refused))
    import belt_watchdog
    good.append(case("belt_watchdog's load threshold comes from the policy",
                     belt_watchdog.LOAD_BUDGET_S == belt_watchdog._PROFILE["process_to_bridge_warn_s"]))

    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


if __name__ == "__main__":
    sys.exit(main())
