#!/usr/bin/env python3
r"""game_instance.py - which RimWorld on this machine: a name, its environment, and stopping it by process id.

design/RimMandrake/two_rimworld_instances_2026-11-07.md (rung one passed on SteveDesktop, 2026-11-07). An instance is a
letter. `a` is today's game and needs nothing set, so nobody who has not asked changes behaviour. `b` and on run from the
same install with their own data folder, log, bridge port, token and driver lock; RM_GAME_INSTANCE=b says which one a
process means, and game_paths, rimbridge_client and driver_lock follow that name even over a stale RM_GAME_USERDATA
(SteveDesktop's .bashrc exports game a's folder into every shell).

    python3 src/RimMandrake/Utils/game_instance.py env b            export lines: eval "$(... env b)"; nothing for a
    python3 src/RimMandrake/Utils/game_instance.py pid [b]          the pid, or nothing when it is not running
    python3 src/RimMandrake/Utils/game_instance.py stop [PID] [--force] [--instance b] [--for "why"]   taskkill /PID, never /IM; only
                                                                    when `rimflow bridge idle` says TAKEABLE
    python3 src/RimMandrake/Utils/game_instance.py prepare b        seed the folder (safe while another game runs)
    python3 src/RimMandrake/Utils/game_instance.py launch a|b [--wait]
    python3 src/RimMandrake/Utils/game_instance.py status
    python3 src/RimMandrake/Utils/game_instance.py free [--busy a] [--for "why"]   the first game a run may take, else 3
    python3 src/RimMandrake/Utils/game_instance.py leftovers        games up with nobody holding them (may be stopped)

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

Game a starts through Steam (steam://rungameid/294100), as it always has, unless Steam will not: a direct game with
steam_appid.txt joins Steam's session for app 294100, and while Steam counts it, rungameid logs `LaunchApp changed task to
WaitingPrevProcess`, then Completed, and starts nothing (MEASURED on Archmagi 2026-11-16 21:21 and 21:23 PST, game b up,
no game a: RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B). launch reads Steam's answer in its console_log.txt
and then starts RimWorldWin64.exe itself, as Steam would: the game folder as working directory, Steam's flags, no
-savedatafolder or -logfile (Unity's own Player.log in LocalLow, which game_paths reads) and no GABP pair (a b-shell
exports one through WSLENV; game a must bind 5174 and write its `Bridge token:` line). So every tool reads it as before.
Steam silent while another game lives is the same direct start; Steam silent with no other game is waited on (its cloud
sync alone took 29 s).
A named game is always started directly, and needs steam_appid.txt (Workshop through Steam); so does a direct game a.
INHERITED_FLAGS (Archmagi's -disable-compute-shaders, a Steam launch option) come from Steam's own last "Game process
added" line, or from a running game's command line, and go on every direct start.

free answers the first game (RM_GAME_INSTANCES, else a,b) a live run may take: not --busy (a live run of the caller's
already drives it) and `rimflow bridge idle` TAKEABLE for that game. Up or down does not matter, so no run waits for a
game while one is free, and none is handed a game another run holds. leftovers lists games up whose bridge is takeable:
an idle leftover nobody holds, which stop may take down; a held game is never one.

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
INHERITED_FLAGS = ("-disable-compute-shaders",)  # Archmagi's Steam launch option for A; B is started like A on the same GPU
LAUNCH_SEEN_S = 15
STEAM_SEEN_S = 120          # Steam's launch of a: cloud sync took 29 s on 2026-11-16 before the process came
STEAM_ANSWER_S = 15         # its WaitingPrevProcess came 1 s after the URL, both times measured
STEAM_URL = "steam://rungameid/294100"
INSTANCES_ENV = "RM_GAME_INSTANCES"
A_PORT_RE = re.compile(r"\[RimBridge\][^\n]*on port\s+(\d+)")
WAIT_S = 600
EX_BLIND, EX_REFUSED = 2, 3
WIN_DIRS = ("/mnt/c/Windows/System32/WindowsPowerShell/v1.0", "/mnt/c/Windows/System32")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PREFS_TEMPLATE = os.path.join(REPO, "infrastructure", "stevedesktop", "Prefs.template.xml")
RIMFLOW_CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
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
    out = {INSTANCE_ENV: name, "RM_GAME_USERDATA": d, "RM_GAME_LOGDIR": d, "GABP_SERVER_PORT": str(port(name)),
           "GABP_TOKEN": ensure_token(name), "RIMFLOW_DRIVER_LOCK": lock_path(name), ROOT_ENV: root()}
    # game a's own log folder (SteveDesktop's testcentre_env.sh sets one), kept so `launch a` from this shell reads a's log
    a_log = os.environ.get("RM_GAME_A_LOGDIR") or os.environ.get("RM_GAME_LOGDIR", "")
    if a_log.strip() and not _under_root(a_log):
        out["RM_GAME_A_LOGDIR"] = a_log
        wslenv += [] if "RM_GAME_A_LOGDIR/p" in wslenv else ["RM_GAME_A_LOGDIR/p"]
    out["WSLENV"] = ":".join(wslenv)
    return out


def _under_root(p):
    """Is path p inside the instances root (a named game's folder, not game a's)?"""
    def norm(x):
        return _native(x).replace("\\", "/").rstrip("/").lower()
    return (norm(p) + "/").startswith(norm(root()) + "/")


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
        raise Blind("the process list did not answer (exit %s): %s" % (r.returncode, (r.stderr or r.stdout or "")))
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


def live_holder(name):
    """-> why, when a live process other than this one's own take holds game `name`'s driver lock, else None
    (host_guard.crossing). Every detached run is seat BENCH, so `rimflow bridge idle` reads another BENCH run's hold as
    ours (MEASURED 2026-11-16 23:37 PST: a live BENCH holder on b, and bridge idle said TAKEABLE); the holder's process
    is the run, whatever its seat. A process that inherited its take (RM_HOST_GUARD_GEN) or is the holder's window is
    its own holder and passes."""
    rf = os.path.join(REPO, "src", "RimMandrake", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import host_guard
    with host_guard.instance_env(None if name == DEFAULT else name):
        return host_guard.crossing()


def bridge_refusal(name, purpose=None, timeout=120):
    """None when this seat may stop game `name`, else why not and what would pass. RIMMANDRAKE_GUARD_GAME_STOP_BY_BRIDGE_HOLD
    (GPT review p2.F2: stop used to taskkill with no bridge check). The verdict is rimflow's own, not a second copy:
    `rimflow bridge idle` (the delegated gate) passes a bridge that is free, ours, or stale by the 45-min rule, and his
    OWNER hold only 45 min after his last interaction (an UNMEASURED reading of him refuses); it also refuses on the
    shared lock and the driver lock. Only its exit 0 with a TAKEABLE line passes: no answer is no permission."""
    purpose = purpose or "stop game %s (game_instance.py stop)" % name
    held = live_holder(name)
    if held:
        return ("game %s is another live driver's: %s\n  what passes: its run ends or releases it (another run's game "
                "is never stopped or handed out)" % (name, held))
    env = dict(os.environ)
    if name == DEFAULT:
        env.pop(INSTANCE_ENV, None)
    else:
        env[INSTANCE_ENV] = name            # the bridge of the game being stopped, whatever this shell drives
    try:
        r = subprocess.run([sys.executable, RIMFLOW_CLI, "bridge", "idle", "--for", purpose], env=env,
                           capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        rc, out, text = r.returncode, r.stdout or "", ((r.stdout or "") + (r.stderr or "")).strip()
    except (OSError, subprocess.SubprocessError) as e:
        rc, out, text = None, "", str(e)
    if rc == 0 and re.search(r"^TAKEABLE  ", out, re.M):
        return None
    if rc not in (0, 1):
        text = "UNMEASURED: `rimflow bridge idle` gave no verdict (exit %s): %s" % (rc, text or "no output")
    return ("the bridge does not let this seat stop game %s: %s\n  what passes: hold it yourself, then stop again  "
            "rimflow bridge take%s --for \"%s\"  (another seat's live hold needs --force; his OWNER hold is takeable "
            "only 45 min after his last interaction, --force included)"
            % (name, text, "" if name == DEFAULT else " --host <machine>.%s" % name, purpose))


def stop(pid_=None, force=False, name=None, purpose=None):
    """taskkill by process id -> (exit code, text). With no pid, every game of this instance; a pid must be this
    instance's, or Refused. Raises Blind when ownership cannot be read: nothing is signalled on a guess. Refused too
    while the bridge is not this seat's to act on (bridge_refusal): a stop is a reboot, the agent's to call only when
    the bridge is free, ours, or stale (owner, 2026-09-02; his OWNER hold by card 2026-10-30)."""
    name = check_name(name or current())
    mine = pids(name)
    if pid_ is not None and pid_ not in mine:
        raise Refused("pid %s is not game %s's (game %s: %s)" % (pid_, name, name, mine or "not running"))
    targets = [pid_] if pid_ is not None else mine
    if not targets:
        return 0, "game %s is not running" % name
    why = bridge_refusal(name, purpose)
    if why:
        raise Refused(why)
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


def _game_dir():
    import game_paths
    return game_paths.GAME_DIR


def _need_appid(what):
    if not os.path.exists(os.path.join(_game_dir(), "steam_appid.txt")):
        raise Refused("%s holds no steam_appid.txt, so %s would get no Steam and no Workshop mods; write 294100 into it "
                      "(Valve's documented file; Steam's own launch of game a is unchanged by it)" % (_game_dir(), what))


def steam_log_path():
    """Steam's console_log.txt: the install is three folders above common/RimWorld."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_game_dir()))), "logs", "console_log.txt")


def _steam_log_tail(start=None, size=2 << 20):
    """-> (text from byte `start`, or the last `size` bytes; the end offset). ("", None) when it cannot be read."""
    try:
        with open(steam_log_path(), "rb") as f:
            f.seek(0, 2)
            end = f.tell()
            f.seek(start if start is not None and start <= end else max(0, end - size))
            return f.read().decode("utf-8", "replace").replace("\r", ""), end
    except OSError:
        return "", None


def steam_flags():
    """The INHERITED_FLAGS on Steam's own last launch of the game (its "Game process added" line for app 294100 with no
    -savedatafolder): where Archmagi's -disable-compute-shaders comes from, read from Steam itself."""
    text, _ = _steam_log_tail()
    added = [ln for ln in text.splitlines() if "Game process added : AppID 294100" in ln and "-savedatafolder" not in ln]
    last = added[-1].split() if added else []
    return [f for f in INHERITED_FLAGS if f in last or f + '",' in last]


def inherited_flags(rows=None):
    """INHERITED_FLAGS from Steam's last launch, or any running game's command line (a b started beside a carries them)."""
    cmds = [(g["cmd"] or "").split() for g in (games() if rows is None else rows)]
    have = set(steam_flags()) | {f for f in INHERITED_FLAGS for c in cmds if f in c}
    return [f for f in INHERITED_FLAGS if f in have]


def _steam_answer(start, sleep, clock):
    """-> 'refused' (WaitingPrevProcess), 'working' (any other LaunchApp task after start), or None (nothing said in
    STEAM_ANSWER_S, or the log unreadable)."""
    t0 = clock()
    while True:
        text, _ = _steam_log_tail(start)
        tasks = re.findall(r"GameAction \[AppID 294100, ActionID \d+\] : LaunchApp changed task to (\w+)", text)
        if "WaitingPrevProcess" in tasks:
            return "refused"
        if [t for t in tasks if t not in ("CheckShaderDepotManifest", "Completed")] or "Game process added" in text:
            return "working"
        if clock() - t0 >= STEAM_ANSWER_S or start is None:
            return None
        sleep(1)


def _steam_url():
    subprocess.run([_exe("cmd.exe"), "/c", "start", "", STEAM_URL], cwd="/mnt/c" if os.path.isdir("/mnt/c") else None,
                   capture_output=True, timeout=60, stdin=subprocess.DEVNULL)


def _start_direct_a(flags):
    """RimWorldWin64.exe as Steam starts it: the game folder, Steam's flags, no GABP pair (port 5174, the token line)."""
    gd = win_path(_game_dir())
    script = ("Remove-Item Env:GABP_SERVER_PORT,Env:GABP_TOKEN -ErrorAction SilentlyContinue; "
              "Start-Process -FilePath '%s\\%s' -WorkingDirectory '%s'%s"
              % (gd, GAME_EXE, gd, (" -ArgumentList " + ",".join("'%s'" % f for f in flags)) if flags else ""))
    r = _ps(script)
    if r.returncode != 0:
        raise Refused("Start-Process failed (exit %d): %s" % (r.returncode, (r.stderr or "").strip()))


def fire_a(sleep=time.sleep, clock=time.time):
    """Send game a's launch -> (route, text): 'steam' when Steam took it (or is still working on it), 'direct' when
    Steam refused it, or said nothing while another game lives, and this started the exe itself. Waits for nothing
    else; the caller waits for the process (launch, launch_ready)."""
    rows = games()
    others = sorted({g["instance"] or "?" for g in rows if g["instance"] != DEFAULT})
    _, start = _steam_log_tail()
    _steam_url()
    said = _steam_answer(start, sleep, clock)
    if said == "working" or (said is None and not others):
        return "steam", "through Steam (%s)" % ("Steam is launching it" if said else "Steam has not said yet; no other game up")
    _need_appid("game a started directly")
    flags = inherited_flags(rows)
    _start_direct_a(flags)
    return "direct", ("directly (Steam %s while game %s runs), flags %s" % (
        "answered WaitingPrevProcess" if said else "said nothing", ",".join(others) or "?", " ".join(flags) or "none"))


def a_player_log():
    """Game a's Player.log from any shell: a b-shell's RM_GAME_LOGDIR is b's folder (env), so RM_GAME_A_LOGDIR, which
    env() keeps when it replaces one, then game_paths' own reading in a shell on game a, then its default LocalLow."""
    import game_paths
    keep = os.environ.get("RM_GAME_A_LOGDIR", "").strip()
    if keep:
        return os.path.join(_native(keep), "Player.log")
    if current() == DEFAULT:
        return game_paths.PLAYER_LOG
    have = os.environ.get("RM_GAME_LOGDIR", "").strip()
    if have and not _under_root(have):
        return os.path.join(_native(have), "Player.log")
    return os.path.join(game_paths.resolve(game_paths._DEF_LOW_WIN, game_paths._DEF_LOW_WSL), "Player.log")


def _launch_a(wait, wait_s, sleep, clock):
    log = a_player_log()
    t0 = clock()
    t_file = time.time()
    route, how = fire_a(sleep, clock)
    t_fired = clock()           # Steam's answer may have taken STEAM_ANSWER_S; the process window starts now
    up, seen_s = None, STEAM_SEEN_S if route == "steam" else LAUNCH_SEEN_S
    while up is None and clock() - t_fired < seen_s:
        up = pid(DEFAULT)
        if up is None:
            sleep(1)
    if up is None:
        return 1, "no game a process %d s after the launch, %s" % (seen_s, how)
    if not wait:
        return 0, "started game a %s, pid %d" % (how, up)
    while clock() - t0 < wait_s:
        text = ""
        try:
            if os.path.getmtime(log) >= t_file - 5:
                text = _read(log)
        except OSError:
            pass
        m = A_PORT_RE.search(text)
        if m and int(m.group(1)) == port(DEFAULT):
            return 0, "started game a %s, pid %d, bridge on port %d after %d s" % (how, up, port(DEFAULT), clock() - t0)
        if m or "[RimBridge] Failed to start server" in text:
            return 1, "game a pid %d, %s: its bridge is not on port %d (%s): a GABP pair reached it, or the port is taken" % (
                up, how, port(DEFAULT), m.group(0) if m else "Failed to start server")
        if up not in pids(DEFAULT):
            return 1, "game a exited during the load (%s); last of %s:\n%s" % (how, log, text[-1500:])  # cut-ok: the tail of a game log the message names; the log is the full text
        sleep(5)
    return 1, "no port line in %s after %d s; game a pid %d (%s) is left running" % (log, wait_s, up, how)


def launch(name=None, wait=False, wait_s=WAIT_S, sleep=time.sleep, clock=time.time):
    """Start a game -> (exit code, text). Game a through Steam, or directly when Steam will not (fire_a); a named game
    directly. Raises Refused for no Steam, or a direct start with no steam_appid.txt; a game already up is ok, with its
    pid. wait: until this run's log has the port line."""
    name = check_name(name or current())
    up = pid(name)
    if up:
        return 0, "game %s already running, pid %d" % (name, up)
    if not _steam_running():
        raise Refused("Steam is not running, and a game started now would have no Workshop mods (rw_game.sh up starts it)")
    if name == DEFAULT:
        return _launch_a(wait, wait_s, sleep, clock)
    _need_appid("game %s" % name)
    d = prepare(name)
    log = log_path(name)
    if os.path.exists(log):
        os.replace(log, log + ".prev")
    wd = win_path(d)
    game_dir = win_path(_game_dir())
    args = ["-savedatafolder=%s" % wd, "-logfile", "%s\\Player.log" % wd, "-screen-fullscreen", "0",
            "-screen-width", str(WINDOW[0]), "-screen-height", str(WINDOW[1])]
    args += inherited_flags()
    script = ("$env:GABP_SERVER_PORT='%d'; $env:GABP_TOKEN='%s'; Start-Process -FilePath '%s\\%s' -WorkingDirectory '%s' "
              "-ArgumentList %s" % (port(name), ensure_token(name), game_dir, GAME_EXE, game_dir,
                                    ",".join("'%s'" % a for a in args)))
    r = _ps(script)
    if r.returncode != 0:
        return 1, "Start-Process failed (exit %d): %s" % (r.returncode, (r.stderr or ""))
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
            return 1, "game %s exited during the load; last of %s:\n%s" % (name, log, text[-1500:])  # cut-ok: the tail of a game log the message names; the log is the full text
        sleep(5)
    return 1, "no port line in %s after %d s; game %s pid %d is left running" % (log, wait_s, name, up)


def instances():
    """The games a run may be given on this machine: RM_GAME_INSTANCES (letters, comma separated), else a and b."""
    have = [check_name(x) for x in os.environ.get(INSTANCES_ENV, "").replace(" ", "").split(",") if x]
    return have or [DEFAULT, "b"]


def free(busy=(), purpose=None, refusal=None):
    """-> (the first game a live run may take, or None; {game: why not}). A game in `busy` (a live run already drives
    it) is not free; any other is free when its bridge is takeable (bridge_refusal: free, ours, or stale), up or down."""
    refusal = refusal or bridge_refusal
    why = {}
    for n in instances():
        if n in busy:
            why[n] = "a live run drives it"
            continue
        no = refusal(n, purpose or "take game %s for a live run (game_instance.py free)" % n)
        if no:
            why[n] = no.splitlines()[0]
            continue
        return n, why
    return None, why


def leftovers(busy=(), refusal=None):
    """-> [{instance, pid}]: games up that nobody holds (not busy, bridge takeable): an idle leftover may be stopped."""
    refusal = refusal or bridge_refusal
    rows = games()
    if any(g["instance"] is None for g in rows):
        raise Blind("cannot read a game's command line, so no game can be called nobody's")
    return [{"instance": g["instance"], "pid": g["pid"]} for g in sorted(rows, key=lambda g: (g["instance"], g["pid"]))
            if g["instance"] not in busy and not refusal(g["instance"], "is game %s an idle leftover" % g["instance"])]


def brief(name):
    """A run brief's section naming the game it drives (maturation.game_brief, the Dispatch step's in-game runs)."""
    name = check_name(name)
    return "\n".join([
        "## Your game: %s" % name, "",
        "This machine runs two RimWorld games, a and b. This run drives game **%s**: `RM_GAME_INSTANCE=%s` is set in "
        "your environment, so game_paths, the bridge client (port %d), `rimflow bridge take` and the driver lock all "
        "follow it. The other game is another run's: never stop, restart or deploy over it, and never take its bridge."
        % (name, name, port(name)),
        "- Start yours, if it is down: `python3 src/RimMandrake/Utils/game_instance.py launch %s --wait` (game a goes "
        "through Steam, or directly with Steam's flags when Steam refuses beside the other game; b always directly)."
        % name,
        "- Stop only yours, by pid: `python3 src/RimMandrake/Utils/game_instance.py stop --instance %s`. "
        "`game_instance.py status` shows both." % name,
        "- Both games read one Mods folder: deploy only your own mod's files; a DLL the other game has loaded "
        "cannot be replaced while it runs.", ""])


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
    s.add_argument("--for", dest="purpose", default=None, help="what the stop is for (the bridge check records it)")
    sub.add_parser("status")
    s = sub.add_parser("free")
    s.add_argument("--busy", action="append", default=[], help="a game a live run already drives (repeatable)")
    s.add_argument("--for", dest="purpose", default=None)
    sub.add_parser("leftovers")
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
        elif a.cmd == "free":
            got, why = free([check_name(x) for x in a.busy], a.purpose)
            if not got:
                raise Refused("no game is free: %s" % "; ".join("game %s: %s" % kv for kv in sorted(why.items())))
            print(got)
        elif a.cmd == "leftovers":
            for g in leftovers():
                print("%s  pid %d  up, nobody holds it: may be stopped (game_instance.py stop --instance %s)" % (
                    g["instance"], g["pid"], g["instance"]))
        else:
            rc, text = (stop(a.pid, a.force, a.instance, a.purpose) if a.cmd == "stop" else launch(a.name, a.wait))
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
