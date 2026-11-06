#!/usr/bin/env python3
"""Detached jobs: slow, read-only work the supervisor tick used to wait on, run in their own unit instead.

RELENTLESS_SHRINK_TICK_SLOW_PHASES_DETACHED (owner 2026-11-05: "Please stop building arbitrary pauses into the system").
The tick is the wait: 118 ticks on 2026-11-06 ran p50 327 s / p95 499 s. Its biggest self-contained cost was the showing
stage fingerprinting the game's deployed Mods over the Windows mount (relentless_showing.mods_fp, 2565 s of 2685 s
in that stage). That walk now runs here; the tick reads its last answer and asks for a fresh one.

One job table per kind, store/jobs/<kind>.json:
  gen      bumped by every request; the job finishes only when the gen it computed is still the newest (gen fence),
           so a request made while it runs is never lost: the running job goes round again (coalescing).
  want     what the newest request asked for (replaced, not merged: a set nobody asks for drops off).
  state    queued | running | done | lost;  pid, started, ended, runs, lost (counts), run_gen.
Liveness is the kernel's, not a clock: a running job holds store/jobs/<kind>.lock (flock) for its whole run; a killed
job's lock is released by the kernel. So
  duplicate start  -> the second process cannot take the lock and exits "duplicate", touching nothing;
  kill mid-job     -> the table still says running but nobody holds the lock: reconcile() (every tick's prelude) marks
                      it lost and launches again; the result file is written by atomic replace, so the last good answer
                      survives the kill.
The job releases its lock only at its gen check, holding the table lock, and the unit's process exits there before
letting go of the table lock; a request checks liveness under the same table lock: a request either lands before the
job's last gen check (the job loops) or finds no job and no live process (it launches, and systemd starts the unit).
No wakeup is lost between them. done_gen fences the other side: a gen already finished is never computed again.

Launch: `systemctl --user start --no-block rm-relentless-job@<kind>.service` (systemd also refuses a second instance of
an active unit). Only the live store launches, only when the unit is installed and relentless_jobs.json says "live";
anything else returns no launcher and callers compute inline as before (tests, a fresh host, the off switch).
"""
import argparse
import contextlib
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "relentless_jobs.json")
UNIT = "rm-relentless-job@%s.service"
UNIT_FILE = os.path.expanduser("~/.config/systemd/user/rm-relentless-job@.service")
DEFAULT_ROOT = "/home/mandrake/rm/relentless"
DUP_TRIES = 20  # x 50 ms: outlasts a probe, not a job
KINDS = {}      # kind -> fn(want) -> result dict; filled below


def _dir(store):
    d = store.p("jobs")
    os.makedirs(d, exist_ok=True)
    return d


def _path(store, kind, suffix):
    return os.path.join(_dir(store), kind + suffix)


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else None
    except (OSError, ValueError):
        return None


def _write(path, obj):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


@contextlib.contextmanager
def _table(store, kind):
    """The table lock: short, never held across the work itself."""
    fd = os.open(_path(store, kind, ".table.lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def table(store, kind):
    return _read(_path(store, kind, ".json")) or {"kind": kind, "gen": 0, "want": None, "state": None, "runs": 0, "lost": 0}


def result(store, kind):
    """The last finished answer ({"gen", "at", "want", "out"}) or None. Survives a kill mid-job (atomic replace)."""
    return _read(_path(store, kind, ".result.json"))


def running(store, kind):
    """True while some process holds the kind's lock: the kernel's word, not a pid or a clock."""
    fd = os.open(_path(store, kind, ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    finally:
        os.close(fd)        # closing drops a lock this probe took
    return False


def _launch(store, kind, launch, t):
    try:
        why = launch(kind)
    except Exception as e:  # noqa: BLE001  a launch that cannot start leaves the row queued; reconcile retries
        why = "%s: %s" % (type(e).__name__, e)
    t["launched"] = time.time()
    t["launch_why"] = (str(why)[:200] if why else None)
    return why


def request(store, kind, want, launch):
    """Ask for a fresh answer to `want`. Coalesces: a running job sees the bumped gen and goes round again."""
    if not launch:
        return None
    with _table(store, kind):
        t = table(store, kind)
        t["gen"] = int(t.get("gen") or 0) + 1
        t["want"] = want
        why = None
        if not running(store, kind):
            t["state"] = "queued"
            why = _launch(store, kind, launch, t)
        _write(_path(store, kind, ".json"), t)
    return why


def reconcile(store, acts, launch, kinds=None):
    """Every tick's prelude: a job the table calls running that holds no lock was killed; it is marked lost and launched
    again. A queued job nobody is running (a launch that never started) is launched again. Idempotent."""
    if not launch:
        return
    for kind in kinds or sorted(KINDS):
        if not os.path.isfile(_path(store, kind, ".json")):
            continue
        with _table(store, kind):
            t = table(store, kind)
            if t.get("state") not in ("running", "queued") or running(store, kind):
                continue
            if t["state"] == "running":
                t["lost"] = int(t.get("lost") or 0) + 1
                acts.append({"do": "job_lost", "kind": kind, "gen": t.get("run_gen"), "pid": t.get("pid")})
            t["state"] = "queued"
            why = _launch(store, kind, launch, t)
            acts.append({"do": "job_relaunch", "kind": kind, "gen": t.get("gen"), "why": why})
            _write(_path(store, kind, ".json"), t)


def run(store, kind, fn=None, on_release=None):
    """The job itself (the unit's ExecStart). -> "duplicate" | "idle" | "done".

    The kind lock is let go at ONE place only, the top-of-loop gen check, under the table lock: everything after a
    finished gen (the result, the done row, the poke) happens with the lock still held, so a request in that time sees
    a job running, bumps gen and is picked up by the same job's next check (RELENTLESS_JOBS_HARDEN_EXIT_WINDOW_RERUN:
    released early, a request between release and the unit's exit got a no-op `systemctl start` and waited a tick).
    `on_release` runs right there, table lock still held; the unit passes one that exits the process, so a request is
    blocked until the process is gone and its `systemctl start` finds the unit inactive. A gen already finished
    (done_gen) is not computed again: a duplicate that wins the lock after the first job ended returns idle."""
    fn = fn or KINDS[kind]
    fd = os.open(_path(store, kind, ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    for i in range(DUP_TRIES):      # a running() probe holds the lock for microseconds; a running job holds it throughout
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if i == DUP_TRIES - 1:
                os.close(fd)
                return "duplicate"
            time.sleep(0.05)
    held, verdict = True, "idle"
    try:
        while True:
            with _table(store, kind):
                t = table(store, kind)
                gen, want = int(t.get("gen") or 0), t.get("want")
                if want is None or t.get("done_gen") == gen:
                    if t.get("state") != "done":
                        t["state"] = "done"
                        _write(_path(store, kind, ".json"), t)
                    os.close(fd)    # released under the table lock: a request now sees it free and launches
                    held = False
                    if on_release:
                        on_release(verdict)
                    return verdict
                t.update(state="running", pid=os.getpid(), started=time.time(), run_gen=gen)
                _write(_path(store, kind, ".json"), t)
            out = fn(want)
            prev = (result(store, kind) or {}).get("out")
            _write(_path(store, kind, ".result.json"), {"gen": gen, "at": time.time(), "want": want, "out": out})
            with _table(store, kind):
                t = table(store, kind)
                if int(t.get("gen") or 0) != gen:
                    continue        # asked again while it ran: once more, on the newest want
                t.update(state="done", ended=time.time(), runs=int(t.get("runs") or 0) + 1, done_gen=gen)
                _write(_path(store, kind, ".json"), t)
            verdict = "done"
            if prev is not None and prev == out:
                continue            # same answer as before: nobody waits on it, and a poke would sustain tick -> job -> tick
            try:            # the tick that wants this answer reads it now, not at its next heartbeat
                import relentless_wake
                relentless_wake.poke("job_" + kind, "gen %d" % gen, root=os.path.dirname(os.path.normpath(store.p(""))))
            except Exception:  # noqa: BLE001  a wake is a courtesy
                pass
    finally:
        if held:
            os.close(fd)


def _exit_now(verdict):
    """The unit's on_release: print and leave while the table lock is held, so no request falls between the lock's
    release and the process's end (the kernel drops both flocks at exit)."""
    print(verdict)
    sys.stdout.flush()
    os._exit(0)


# ---------------------------------------------------------------- launching

def mode(kind):
    return (_read(CONFIG) or {}).get(kind, "off")


def systemd_launch(kind):
    r = subprocess.run(["systemctl", "--user", "start", "--no-block", UNIT % kind], capture_output=True, text=True,
                       timeout=30)
    return None if r.returncode == 0 else ("systemctl exit %d: %s" % (r.returncode, r.stderr.strip()))[:200]


def launcher(store, kind):
    """The live launcher, or None (callers then compute inline, as before): only the live store, only when the unit is
    installed, only when relentless_jobs.json says "live" for the kind."""
    root = getattr(store, "root", None)
    if not root or os.path.realpath(root) != os.path.realpath(DEFAULT_ROOT) or mode(kind) != "live":
        return None
    if not os.path.isfile(UNIT_FILE):
        return None
    return systemd_launch


# ---------------------------------------------------------------- kind: mods_fp (the showing stage's Mods walk)

def _mods_fp_job(want):
    import relentless_showing
    root = want.get("root")
    return {"root": root, "fps": {k: relentless_showing.mods_fp(v, root) for k, v in sorted((want.get("sets") or {}).items())}}


KINDS["mods_fp"] = _mods_fp_job


def mods_key(mods):
    return "\n".join(sorted({x for x in mods or [] if isinstance(x, str)}))


class ModsFp:
    """The showing stage's fingerprint of deployed mods. With a launcher: the job's answer for this mod set, used only
    when it answered the newest request (the previous pass's close()); a job still running, dead or failing, or a set it
    has not answered, is walked inline as before. So an answer is at most one pass old: a deploy landing between the
    job's walk and this pass is seen on the next pass. Without a launcher: walked inline every time, as before."""

    def __init__(self, store, root, launch=None):
        self.store, self.root, self.launch = store, root, launch
        self.sets, self.hits, self.inline = {}, 0, 0
        got = result(store, "mods_fp") if launch else None
        out = (got or {}).get("out") or {}
        fresh = got is not None and got.get("gen") == table(store, "mods_fp").get("gen")
        self.cached = (out.get("fps") or {}) if fresh and out.get("root") == root else {}

    def __call__(self, mods):
        import relentless_showing
        key = mods_key(mods)
        self.sets[key] = sorted(set(key.split("\n"))) if key else []
        if self.launch and key in self.cached:
            self.hits += 1
            return self.cached[key]
        self.inline += 1
        return relentless_showing.mods_fp(mods, self.root)

    def close(self):
        if self.launch and self.sets:
            return request(self.store, "mods_fp", {"root": self.root, "sets": self.sets}, self.launch)
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("kind", choices=sorted(KINDS))
    p = sub.add_parser("show")
    p.add_argument("kind", choices=sorted(KINDS))
    a = ap.parse_args(argv)
    sys.path.insert(0, HERE)
    import relentless
    store = relentless.Store()
    if a.cmd == "run":
        print(run(store, a.kind, on_release=_exit_now))   # _exit_now leaves; a "duplicate" returns here
        return 0
    t = table(store, a.kind)
    t["running"] = running(store, a.kind)
    print(json.dumps(t, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
