"""host_guard.py - one driver per game, per MACHINE, for scripts as well as windows (BRIDGE_LOCK_WIDEN_ONE_PER_HOST).

Two machines each run a RimWorld: Archmagi (the interactive lane) and SteveDesktop (the batch test centre). Each
machine's game has exactly one guard: that machine's own process-keyed driver lock (driver_lock.py, the file
`rmpaths scratch/DRIVER_LOCK.json` on THAT machine's data root). `rimflow bridge take` already takes it for a window;
this module lets a SCRIPT take the same lock - the testq worker, the dispatcher's Archmagi backfill, modcheck,
deploy and rw_game.sh - so a window and a script can never both drive one game.

  * The holder of a script take is the script's OWN process (not the nearest `claude` ancestor, which is what a
    window's take uses): the guard is fenced to the process doing the driving and frees the moment it exits.
  * Children inherit the take: a holder exports RM_HOST_GUARD_GEN=<generation> (and adds it to WSLENV so a Windows
    python.exe child sees it); a nested acquire whose generation matches the live lock is a no-op pass-through. So
    `host_guard.py run -- worker` -> rw_game.sh -> modcheck all count as one driver.
  * On Archmagi a script also refuses while the cross-clone shared bridge file names a live window holder, because
    a window that took the bridge before the driver lock existed, or from the other clone, is still driving.
  * A take made from ANOTHER machine (Archmagi taking SteveDesktop's game for an interactive session) carries that
    machine's identity; driver_lock reads it as "not inspectable" and its heartbeat decides (45 min).

CLI (exit 0 ok, 75 held by someone else, 2 usage or lock unusable):
  host_guard.py status [--json]
  host_guard.py take    --seat S --for WHAT [--identity-json J] [--force WHY]
  host_guard.py release --seat S [--identity-json J] [--force WHY]
  host_guard.py run     --seat S --for WHAT [--force WHY] -- CMD [ARGS...]   hold it for CMD's lifetime
  host_guard.py remote  HOST status|take|release [same flags]                run it on HOST over ssh
"""
import argparse
import contextlib
import json
import os
import shlex
import socket
import subprocess
import sys

try:                                   # imported as rimflow.host_guard (cli.py) - one copy of model, not two
    from . import driver_lock
except ImportError:                    # run as a script on the runner or from a shell
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import driver_lock  # noqa: E402

ENV_GEN = "RM_HOST_GUARD_GEN"
EX_HELD = 75
# How a host is reached over ssh from the dispatching machine. Only SteveDesktop is remote today.
SSH_TARGETS = {"stevedesktop": os.environ.get("STEVE_WSL", "mandrake@stevedesktop-wsl")}
RUNNER_DIR = os.environ.get("RM_RUNNER_DIR", "~/rm/runner")


def _model():
    """Late import: model pulls the ledger paths, which a bare `status` on the runner does not need."""
    if __package__:
        from . import model
    else:
        import model
    return model


def local_host():
    """This machine's bridge-host key (RM_HOST overrides the hostname), or None when it is not a known game host."""
    name = (os.environ.get("RM_HOST") or socket.gethostname()).strip().lower()
    return name if name in _model().BRIDGE_HOSTS else None


def lock_path():
    return driver_lock.lock_path()


def self_identity():
    """The identity of THIS process - a script's guard is fenced to the script, not to the window that started it."""
    me = dict(driver_lock.my_identity())
    pid = os.getpid()
    me["pid"] = pid
    me["start"] = driver_lock._win_start(pid) if os.name == "nt" else driver_lock._proc_start(pid)
    return me


def _reentrant(path):
    """The generation this process may drive under without a take of its own, else None: it inherited a take
    (RM_HOST_GUARD_GEN matches the live lock), or the lock is held by its own WINDOW - a window that ran
    `rimflow bridge take` and then starts modcheck from its shell is one driver, not two."""
    if not path:
        return None
    cur, problem = driver_lock._read(path)
    if problem or not cur:
        return None
    gen = os.environ.get(ENV_GEN)
    if gen and str(cur.get("generation")) == gen:
        alive, _how = driver_lock._alive(cur)
        return cur.get("generation") if alive else None
    if driver_lock.same_process(cur.get("identity"), driver_lock.my_identity()):
        return cur.get("generation")
    return None


def _shared_window_holder(seat):
    """Archmagi only: a live window holder named by the cross-clone shared bridge file, else None."""
    m = _model()
    if local_host() != m.DEFAULT_BRIDGE_HOST:
        return None
    sh = m.read_shared_bridge()
    if not sh or sh.get("holder") in (None, seat):
        return None
    age = m.shared_bridge_age_seconds(sh)
    if age is None or age >= m.BRIDGE_STALE_SECONDS:
        return None
    return "%s (shared bridge file, %d min ago, for: %s)" % (sh["holder"], age // 60, sh.get("purpose"))


def acquire(seat, purpose, force=None, identity=None, path=None):
    """-> driver_lock result dict plus `reentrant` and `path`. Fails CLOSED when there is no lock file to take."""
    path = path or lock_path()
    if not path:
        return {"ok": False, "why": "no driver lock path on this machine (data root scratch/ missing, or a "
                "redirected RIMFLOW_LEDGER without RIMFLOW_DRIVER_LOCK) - refusing to drive unguarded", "path": None}
    inherited = _reentrant(path) if identity is None else None
    if inherited is not None:
        return {"ok": True, "reentrant": True, "generation": inherited, "why": "inherited take", "path": path}
    if not force:
        other = _shared_window_holder(seat)
        if other:
            return {"ok": False, "why": "a window holds this machine's bridge: %s" % other, "path": path}
    r = driver_lock.acquire(path, seat, purpose, identity or self_identity(), force=force)
    r["reentrant"] = False
    r["path"] = path
    return r


def release(seat, force=None, identity=None, path=None):
    path = path or lock_path()
    if not path:
        return {"ok": False, "why": "no driver lock path on this machine"}
    return driver_lock.release(path, seat, identity or self_identity(), force=force)


def export_take(gen):
    """Make children of this process inherit the take (WSLENV so a Windows python.exe child sees it too)."""
    os.environ[ENV_GEN] = str(gen)
    wslenv = os.environ.get("WSLENV", "")
    if ENV_GEN not in wslenv.split(":"):
        os.environ["WSLENV"] = (wslenv + ":" if wslenv else "") + ENV_GEN


class Refused(RuntimeError):
    """The guard is held by someone else (or unusable). str() is the reason."""


@contextlib.contextmanager
def held(seat, purpose, force=None):
    """Hold this machine's game guard for the block. Raises Refused when another driver holds it."""
    r = acquire(seat, purpose, force=force)
    if not r["ok"]:
        raise Refused(r["why"])
    prev = os.environ.get(ENV_GEN)
    export_take(r["generation"])
    try:
        yield r
    finally:
        if prev is None:
            os.environ.pop(ENV_GEN, None)
        else:
            os.environ[ENV_GEN] = prev
        if not r.get("reentrant"):
            release(seat)


def status(path=None):
    path = path or lock_path()
    st = driver_lock.status(path) if path else {"state": "NO_LOCK_PATH"}
    st["host"] = local_host()
    st["path"] = path
    return st


def remote_argv(host, args):
    """The ssh argv that runs `host_guard.py <args>` in the runner clone on HOST."""
    target = SSH_TARGETS.get(host)
    if not target:
        raise SystemExit("host_guard: %s is not a remote host from here (known: %s)" % (host, ", ".join(SSH_TARGETS)))
    cmd = "cd %s && python3 src/RimMandrake/rimflow/host_guard.py %s" % (
        RUNNER_DIR, " ".join(shlex.quote(a) for a in args))
    return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "LogLevel=ERROR", target, cmd]


def remote(host, args, timeout=60):
    """-> (exit code, combined output). 255 is ssh's own failure (host unreachable)."""
    try:
        p = subprocess.run(remote_argv(host, args), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 255, "ssh to %s timed out after %d s" % (host, timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def _print(r, as_json):
    if as_json:
        print(json.dumps(r, indent=1, default=str))
    else:
        gen = (" gen %s  (children: RM_HOST_GUARD_GEN=%s)" % (r["generation"], r["generation"])
               if r.get("ok") and r.get("generation") else "")
        print(("ok   " if r.get("ok", True) else "REFUSED ") + str(r.get("why") or r.get("state")) + gen)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="host_guard.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    for name in ("take", "release", "run"):
        s = sub.add_parser(name)
        s.add_argument("--seat", required=True)
        s.add_argument("--force", default=None, help="break a live holder; the reason is recorded on the lock")
        s.add_argument("--json", action="store_true")
        if name != "release":
            s.add_argument("--for", dest="purpose", required=True)
        if name != "run":
            s.add_argument("--identity-json", default=None,
                           help="hold for this identity (a window on another machine) instead of this process")
        if name == "run":
            s.add_argument("command", nargs=argparse.REMAINDER)
    s = sub.add_parser("remote")
    s.add_argument("host")
    s.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)

    if a.cmd == "remote":
        rc, out = remote(a.host.lower(), a.rest)
        print(out)
        return rc
    if a.cmd == "status":
        st = status()
        if a.json:
            print(json.dumps(st, indent=1, default=str))
        else:
            print("%s %s%s" % (st.get("host"), st.get("state"), "" if st.get("state") in ("FREE", "NO_LOCK_PATH")
                               else "  %s gen %s for: %s (%s)" % (st.get("seat"), st.get("generation"),
                                                                  st.get("purpose"), st.get("how"))))
        return 0
    ident = json.loads(a.identity_json) if getattr(a, "identity_json", None) else None
    if a.cmd == "take":
        if ident is None:
            ident = driver_lock.my_identity()      # a CLI take outlives this process: hold for the calling window
        r = acquire(a.seat, a.purpose, force=a.force, identity=ident)
        _print(r, a.json)
        return 0 if r["ok"] else (EX_HELD if r.get("path") else 2)
    if a.cmd == "release":
        r = release(a.seat, force=a.force, identity=ident or driver_lock.my_identity())
        _print(r, a.json)
        return 0 if r["ok"] else EX_HELD
    # run
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd:
        ap.error("run needs a command after --")
    try:
        with held(a.seat, a.purpose, force=a.force) as r:
            if not a.json:
                sys.stderr.write("host_guard: %s holds %s gen %s%s\n" % (
                    a.seat, local_host(), r["generation"], " (inherited)" if r.get("reentrant") else ""))
            return subprocess.call(cmd)
    except Refused as e:
        sys.stderr.write("host_guard: REFUSED %s\n" % e)
        return EX_HELD


if __name__ == "__main__":
    sys.exit(main())
