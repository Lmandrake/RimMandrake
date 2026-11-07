#!/usr/bin/env python3
r"""game_instance.py - which RimWorld on this machine: a name, its environment, and stopping it by process id.

design/RimMandrake/two_rimworld_instances_2026-11-07.md (rung one passed on SteveDesktop, 2026-11-07). An instance is a
letter. `a` is today's game and needs nothing set, so nobody who has not asked changes behaviour. `b` and on run from the
same install with their own data folder, log, bridge port, token and driver lock; RM_GAME_INSTANCE=b says which one a
process means, and game_paths, rimbridge_client and driver_lock follow that name even over a stale RM_GAME_USERDATA
(SteveDesktop's .bashrc exports game a's folder into every shell).

    python3 src/RimMandrake/Utils/game_instance.py env b            export lines: eval "$(... env b)"; nothing for a
    python3 src/RimMandrake/Utils/game_instance.py pid [b]          the pid, or nothing when it is not running
    python3 src/RimMandrake/Utils/game_instance.py stop [PID] [--force] [--instance b]     taskkill /PID, never /IM
    python3 src/RimMandrake/Utils/game_instance.py prepare b        seed the folder (safe while another game runs)
    python3 src/RimMandrake/Utils/game_instance.py launch b [--wait]
    python3 src/RimMandrake/Utils/game_instance.py status

Exit 0 ok; 2 BLIND (the process list could not be read, so nothing was acted on); 3 REFUSED, with the reason.

Whose game is it? Only the process's command line can say, because both games have one image name and one window title:
`-savedatafolder=...\instances\<letter>` is that instance, and anything else is `a` (Steam's launch, a direct launch with
no folder, a private -savedatafolder). The match is on the path's last two parts rather than on this machine's root, so a
shell that resolved the root differently still cannot read B as A. A game whose command line cannot be read is nobody's:
stop refuses, and running() says True, because a guess here is what can kill someone else's game.

Launch recipe fixes from the trial: the token is written from here and read back (Set-Content wrote nothing and raised no
error); Prefs.xml carries a window size beside <fullscreen>False</fullscreen> (the -screen-* flags alone left B
fullscreen); and seeding reads no other game's state, so it works with A up. Player.log sits in the data folder, because
modset_builder builds PLAYERLOG from there. Unity does not rotate under -logfile, so launch moves the old one to .prev.

launch refuses game a, whose launch stays where it is (steam://, rw_game.sh up), and refuses a folder with no
steam_appid.txt: rung one is measured only where that file exists, and on Archmagi it is a separate decision.

Selftest: selftest_game_instance.py (two fake games, real processes, no Windows). Planted faults:
selftest_second_game_mutants.py.
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid

GAME_EXE = "RimWorldWin64.exe"
DEFAULT = "a"
BASE_PORT = 5174
INSTANCE_ENV = "RM_GAME_INSTANCE"
ROOT_ENV = "RM_INSTANCES_ROOT"
LIST_OK = "GAME-LIST-OK"            # the list's last line: without it an empty answer is a blind instrument, not "no game"
PORT_LINE = "GABP server connected to GABS on port"     # env mode's line; there is no "Bridge token:" line in that mode
WINDOW = (1280, 720)
LAUNCH_SEEN_S = 15
WAIT_S = 600
EX_BLIND, EX_REFUSED = 2, 3
WIN_DIRS = ("/mnt/c/Windows/System32/WindowsPowerShell/v1.0", "/mnt/c/Windows/System32")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PREFS_TEMPLATE = os.path.join(REPO, "infrastructure", "stevedesktop", "Prefs.template.xml")
MINIMAL_LIST = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
_WSLENV = ("RM_GAME_INSTANCE", "RM_GAME_USERDATA/p", "RM_GAME_LOGDIR/p", "GABP_SERVER_PORT", "GABP_TOKEN",
           "RIMFLOW_DRIVER_LOCK/p", "RM_INSTANCES_ROOT/p")
_SAVE_RE = re.compile(r'"-savedatafolder=([^"]*)"|-savedatafolder="([^"]*)"|-savedatafolder=([^\s"]+)', re.I)


class InstanceError(ValueError):
    """A bad instance name, or a folder that will not hold what it was given. str() is the reason."""


class Blind(RuntimeError):
    """The process list could not be read. Never means "no game"."""


class Refused(RuntimeError):
    """An act that would land on the wrong game or an unmeasured machine. str() is the reason."""


def check_name(name):
    n = (name or "").strip().lower()
    if not re.fullmatch("[a-z]", n):
        raise InstanceError("bad game instance %r: one letter, a is today's game" % (name,))
    return n


def current():
    """The instance this process means: RM_GAME_INSTANCE, else a."""
    return check_name(os.environ.get(INSTANCE_ENV, "").strip() or DEFAULT)


def port(name=None):
    return BASE_PORT + ord(check_name(name or current())) - ord("a")


def _native(p):
    """The path in this interpreter's form: WSL python gets /mnt/d/x, Windows python gets D:\\x."""
    p = str(p)
    if os.name == "nt":
        m = re.match(r"^/mnt/([a-zA-Z])(?:/(.*))?$", p)
        return "%s:\\%s" % (m.group(1).upper(), (m.group(2) or "").replace("/", "\\")) if m else p
    m = re.match(r"^([A-Za-z]):[\\/]*(.*)$", p)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else p


def win_path(p):
    m = re.match(r"^/mnt/([a-zA-Z])(?:/(.*))?$", p)
    return "%s:\\%s" % (m.group(1).upper(), (m.group(2) or "").replace("/", "\\")) if m else p


def root():
    """RM_INSTANCES_ROOT (SteveDesktop's testcentre_env.sh sets it), else <data root>/instances (rmpaths.py)."""
    v = os.environ.get(ROOT_ENV, "").strip()
    if v:
        return _native(v)
    import rmpaths
    return rmpaths.rm_str("instances")


def data_dir(name=None):
    name = check_name(name or current())
    if name == DEFAULT:
        raise InstanceError("game a has no instance folder: it is today's game, in its usual place")
    return os.path.join(root(), name)


def log_path(name=None):
    return os.path.join(data_dir(name), "Player.log")


def token_path(name=None):
    return os.path.join(data_dir(name), "bridge_token.txt")


def lock_path(name=None):
    return os.path.join(data_dir(name), "DRIVER_LOCK.json")


def read_token(name=None):
    try:
        with open(token_path(name), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def ensure_token(name=None):
    """The instance's bridge token, made once and kept, so a loop's exported environment survives a game restart."""
    have = read_token(name)
    if have:
        return have
    path, token = token_path(name), str(uuid.uuid4())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(token)
        f.flush()
        os.fsync(f.fileno())
    if read_token(name) != token:
        raise InstanceError("the token did not read back from %s" % path)
    return token


def env(name=None):
    """The environment that means this instance. Game a is {}: nothing set is today's game."""
    name = check_name(name or current())
    if name == DEFAULT:
        return {}
    d = data_dir(name)
    have = [v for v in os.environ.get("WSLENV", "").split(":") if v]
    wslenv = have + [v for v in _WSLENV if v not in have]
    return {INSTANCE_ENV: name, "RM_GAME_USERDATA": d, "RM_GAME_LOGDIR": d, "GABP_SERVER_PORT": str(port(name)),
            "GABP_TOKEN": ensure_token(name), "RIMFLOW_DRIVER_LOCK": lock_path(name), ROOT_ENV: root(),
            "WSLENV": ":".join(wslenv)}


def owner(cmdline):
    """The instance a game's command line says it is (see the module text)."""
    m = _SAVE_RE.search(cmdline or "")
    if not m:
        return DEFAULT
    parts = next(g for g in m.groups() if g is not None).replace("\\", "/").rstrip("/").lower().split("/")
    if len(parts) >= 2 and parts[-2] == "instances" and re.fullmatch("[a-z]", parts[-1]):
        return parts[-1]
    return DEFAULT


def _exe(name):
    """A Tailscale SSH session has no Windows dirs on PATH (testcentre_env.sh), so the full path is the fallback."""
    found = shutil.which(name)
    if found:
        return found
    for d in WIN_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return name


def _run(argv, timeout=60):
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                          stdin=subprocess.DEVNULL)


def _ps(script, timeout=60):
    return _run([_exe("powershell.exe"), "-NoProfile", "-NonInteractive", "-Command", script], timeout)


def _list_script(exe=GAME_EXE):
    # no double quotes: they do not survive the WSL interop command line
    return ("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; "
            "Get-CimInstance Win32_Process -Filter 'Name=''%s''' | ForEach-Object { '{0}|{1}|{2}' -f $_.ProcessId, "
            "([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds(), $_.CommandLine }; '%s'" % (exe, LIST_OK))


def games(exe=GAME_EXE):
    """-> [{pid, start (epoch s), cmd, instance}]; instance is None when the command line could not be read. Raises
    Blind when the list did not answer: an empty list here is a measured "no game"."""
    try:
        r = _ps(_list_script(exe))
    except (OSError, subprocess.SubprocessError) as e:
        raise Blind("the process list did not answer: %s: %s" % (type(e).__name__, e))
    lines = (r.stdout or "").replace("\r", "").splitlines()
    if r.returncode != 0 or LIST_OK not in lines:
        raise Blind("the process list did not answer (exit %s): %s" % (r.returncode, (r.stderr or r.stdout or "")[:200]))
    rows = []
    for line in lines:
        m = re.match(r"(\d+)\|(\d*)\|(.*)$", line)
        if m:
            cmd = m.group(3).strip()
            rows.append({"pid": int(m.group(1)), "start": int(m.group(2)) / 1000.0 if m.group(2) else None, "cmd": cmd,
                         "instance": owner(cmd) if cmd else None})
    return rows


def procs(name=None):
    """This instance's games as [{pid, start}], oldest pid first. Raises Blind if any game's owner cannot be read."""
    name = check_name(name or current())
    rows = games()
    unread = [g["pid"] for g in rows if g["instance"] is None]
    if unread:
        raise Blind("cannot read the command line of game pid %s, so it cannot be told apart" % unread)
    return [{"pid": g["pid"], "start": g["start"]} for g in sorted(rows, key=lambda g: g["pid"]) if g["instance"] == name]


def pids(name=None):
    return [p["pid"] for p in procs(name)]


def pid(name=None):
    """The instance's pid, or None. Two games on one instance share a save folder: say so, and answer the lower."""
    mine = pids(name)
    if len(mine) > 1:
        sys.stderr.write("game_instance: %d games on one instance: pids %s\n" % (len(mine), mine))
    return mine[0] if mine else None


def running(name=None):
    """Is this instance's game up? A game nobody can attribute counts as up. Raises Blind when the list did not answer."""
    name = check_name(name or current())
    return any(g["instance"] in (name, None) for g in games())


def ps_process(name=None):
    """PowerShell for this instance's game process, for a script that reads `$p = <this>`. No game is @(), which `if ($p)`
    reads as false and a pipeline as nothing ($null would run a pipeline once). The list is read in Python, so there is
    one rule for whose game it is."""
    mine = pid(name)
    return "Get-Process -Id %d -ErrorAction SilentlyContinue" % mine if mine else "@()"


def ps_processes(name=None):
    mine = pids(name)
    return "Get-Process -Id %s -ErrorAction SilentlyContinue" % ",".join(map(str, mine)) if mine else "@()"


def stop(pid_=None, force=False, name=None):
    """taskkill by process id -> (exit code, text). With no pid, every game of this instance; a pid must be this
    instance's, or Refused. Raises Blind when ownership cannot be read: nothing is signalled on a guess."""
    name = check_name(name or current())
    mine = pids(name)
    if pid_ is not None and pid_ not in mine:
        raise Refused("pid %s is not game %s's (game %s: %s)" % (pid_, name, name, mine or "not running"))
    targets = [pid_] if pid_ is not None else mine
    if not targets:
        return 0, "game %s is not running" % name
    rc, out = 0, []
    for p in targets:
        r = _run([_exe("taskkill.exe")] + (["/F"] if force else []) + ["/PID", str(p)])
        rc = rc or r.returncode
        out.append(((r.stdout or "") + (r.stderr or "")).strip() or "taskkill /PID %d" % p)
    return rc, "\n".join(out)


# ---------------------------------------------------------------- seeding and launching a named instance

def _set_pref(text, tag, value, keep=False):
    m = re.search(r"<%s>[^<]*</%s>" % (tag, tag), text)
    if m:
        return text if keep else text[:m.start()] + "<%s>%s</%s>" % (tag, value, tag) + text[m.end():]
    at = re.search(r"<fullscreen>[^<]*</fullscreen>|<PrefsData>", text)
    if not at:
        raise InstanceError("Prefs has no place for <%s>" % tag)
    return text[:at.end()] + "\n  <%s>%s</%s>" % (tag, value, tag) + text[at.end():]


def seed_prefs(path):
    """Prefs.xml with no fullscreen, runInBackground on, and a window size unless it already has one. Without the size B
    runs fullscreen whatever the flags say (MEASURED); without runInBackground it stops advancing unfocused."""
    src = path if os.path.exists(path) else PREFS_TEMPLATE
    with open(src, encoding="utf-8", newline="") as f:
        was = f.read()
    text = _set_pref(_set_pref(was, "fullscreen", "False"), "runInBackground", "True")
    text = _set_pref(_set_pref(text, "screenWidth", WINDOW[0], keep=True), "screenHeight", WINDOW[1], keep=True)
    if src != path or text != was:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def prepare(name=None):
    """Seed the folder a named instance needs. It reads no other game's state, so it works while A runs; it refuses while
    its own game runs, which rewrites Prefs from memory on exit. Keeps whatever list and Prefs are already there."""
    name = check_name(name or current())
    d = data_dir(name)
    if re.search(r"\s", d):
        raise Refused("instance folder %r has whitespace: the launch's -savedatafolder is unquoted, as measured" % d)
    if running(name):
        raise Refused("game %s is running; it rewrites Prefs.xml on exit. Stop it first" % name)
    for sub in ("Config", "JawaBench"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    ensure_token(name)
    seed_prefs(os.path.join(d, "Config", "Prefs.xml"))
    mods = os.path.join(d, "Config", "ModsConfig.xml")
    if not os.path.exists(mods):
        shutil.copyfile(MINIMAL_LIST, mods)
    expires = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 30 * 86400))
    with open(os.path.join(d, "JawaBench", "companion_profile.json"), "w", encoding="utf-8") as f:
        json.dump({"profile": "test", "expiresUtc": expires, "campaignSaves": "",
                   "why": "second game %s: the game and every save in %s are the runner's (game_instance prepare)"
                   % (name, win_path(d))}, f, indent=2)
    return d


def _steam_running():
    r = _ps("(Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1).Id")
    return r.returncode == 0 and (r.stdout or "").strip().isdigit()


def launch(name=None, wait=False, wait_s=WAIT_S, sleep=time.sleep, clock=time.time):
    """Start a named instance directly -> (exit code, text). Raises Refused for game a, a folder with no steam_appid.txt
    or no Steam; a game already up is ok, with its pid. wait: until this run's log has the port line."""
    name = check_name(name or current())
    if name == DEFAULT:
        raise Refused("game a keeps its own launch (Steam, or rw_game.sh up)")
    import game_paths
    if not os.path.exists(os.path.join(game_paths.GAME_DIR, "steam_appid.txt")):
        raise Refused("%s holds no steam_appid.txt: rung one is measured only where it exists, and this machine's trial "
                      "is a separate decision" % game_paths.GAME_DIR)
    up = pid(name)
    if up:
        return 0, "game %s already running, pid %d" % (name, up)
    if not _steam_running():
        raise Refused("Steam is not running, and a game started now would have no Workshop mods (rw_game.sh up starts it)")
    d = prepare(name)
    log = log_path(name)
    if os.path.exists(log):
        os.replace(log, log + ".prev")
    wd = win_path(d)
    game_dir = win_path(game_paths.GAME_DIR)
    args = ["-savedatafolder=%s" % wd, "-logfile", "%s\\Player.log" % wd, "-screen-fullscreen", "0",
            "-screen-width", str(WINDOW[0]), "-screen-height", str(WINDOW[1])]
    script = ("$env:GABP_SERVER_PORT='%d'; $env:GABP_TOKEN='%s'; Start-Process -FilePath '%s\\%s' -WorkingDirectory '%s' "
              "-ArgumentList %s" % (port(name), ensure_token(name), game_dir, GAME_EXE, game_dir,
                                    ",".join("'%s'" % a for a in args)))
    r = _ps(script)
    if r.returncode != 0:
        return 1, "Start-Process failed (exit %d): %s" % (r.returncode, (r.stderr or "")[:300])
    t0 = clock()
    up = None
    while up is None and clock() - t0 < LAUNCH_SEEN_S:
        up = pid(name)
        if up is None:
            sleep(1)
    if up is None:
        return 1, "no game %s process %d s after Start-Process" % (name, LAUNCH_SEEN_S)
    if not wait:
        return 0, "started game %s, pid %d, port %d" % (name, up, port(name))
    while clock() - t0 < wait_s:
        text = _read(log)
        if "%s %d" % (PORT_LINE, port(name)) in text:
            return 0, "started game %s, pid %d, bridge on port %d after %d s" % (name, up, port(name), clock() - t0)
        if "[RimBridge] Failed to start server" in text:
            return 1, "game %s pid %d: [RimBridge] Failed to start server (the port is taken, or the pair did not carry)" % (
                name, up)
        if up not in pids(name):
            return 1, "game %s exited during the load; last of %s:\n%s" % (name, log, text[-1500:])
        sleep(5)
    return 1, "no port line in %s after %d s; game %s pid %d is left running" % (log, wait_s, name, up)


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def status_lines():
    rows = games()
    names = sorted({DEFAULT, current()} | {g["instance"] or "?" for g in rows})
    out = []
    for n in names:
        mine = [g["pid"] for g in rows if (g["instance"] or "?") == n]
        out.append("%s  %-22s  port %s" % (n, "running pid %s" % ",".join(map(str, mine)) if mine else "stopped",
                                           "?" if n == "?" else port(n)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="game_instance.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for verb in ("env", "pid", "prepare"):
        sub.add_parser(verb).add_argument("name", nargs="?")
    s = sub.add_parser("launch")
    s.add_argument("name", nargs="?")
    s.add_argument("--wait", action="store_true")
    s = sub.add_parser("stop")
    s.add_argument("pid", nargs="?", type=int)
    s.add_argument("--force", action="store_true")
    s.add_argument("--instance", default=None)
    sub.add_parser("status")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "env":
            for k, v in env(a.name).items():
                print("export %s=%s" % (k, shlex.quote(v)))
        elif a.cmd == "pid":
            mine = pid(a.name)
            if mine:
                print(mine)
        elif a.cmd == "prepare":
            print("prepared %s" % prepare(a.name))
        elif a.cmd == "status":
            print("\n".join(status_lines()))
        else:
            rc, text = (stop(a.pid, a.force, a.instance) if a.cmd == "stop" else launch(a.name, a.wait))
            print(text)
            return rc
    except Blind as e:
        print("BLIND: %s" % e, file=sys.stderr)
        return EX_BLIND
    except (Refused, InstanceError) as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return EX_REFUSED
    return 0


if __name__ == "__main__":
    sys.exit(main())
