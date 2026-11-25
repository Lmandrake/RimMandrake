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
    python3 src/RimMandrake/Utils/game_instance.py stop --broken --instance b  confirm broken disk health, then stop by PID
    python3 src/RimMandrake/Utils/game_instance.py prepare b        seed the folder and its own install (safe while another
                                                                    game runs)
    python3 src/RimMandrake/Utils/game_instance.py install b [--refresh]   copy the install into <root>/b/game (game a's
                                                                    is only read)
    python3 src/RimMandrake/Utils/game_instance.py launch a|b [--wait]
    python3 src/RimMandrake/Utils/game_instance.py status
    python3 src/RimMandrake/Utils/game_instance.py free [--busy a] [--for "why"]   the first game a run may take, else 3
    python3 src/RimMandrake/Utils/game_instance.py leftovers        games up with nobody holding them (may be stopped)

Exit 0 ok; 1 confirmed stop failed; 2 BLIND (could not look); 3 REFUSED, with the reason.

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
an idle leftover nobody holds, which stop may take down; a held game is never one, and a hold by the asker's own window
is a hold (leftovers asks for every holder, the asker included).

Each named game has its own install (RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST, rung three of the design
note): <root>/<letter>/game holds a copy of the game's files, its own Mods and its own BridgeTools, so a deploy or a
companion build for b (RM_GAME_INSTANCE=b: game_paths.GAME_DIR and LOCAL_MODS follow it) never writes a folder game a has
loaded. Steam's Workshop folder stays shared: nothing of ours writes there. `install` copies game a's install once (about
2.5 GB, MEASURED 2026-11-20) and only reads game a's folder.

The per-game hold (`pipe off game:a`, control.game_held): while it stands, stop and launch of that game refuse unless the
caller passes despite (the Conductor, on purpose, with its reason), and free and leftovers never offer it.

Selftest: selftest_game_instance.py (two fake games, real processes, no Windows). Planted faults:
selftest_second_game_mutants.py.
"""
import argparse
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
import uuid

_RF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow")
if _RF not in sys.path:
    sys.path.insert(0, _RF)
import game_names  # noqa: E402  (the one map from a game's letter to its name: ArchBig, ArchSmall, Steve1, Steve2)


def _n(name):
    """-> the name people read for game letter `name` on this machine ('b' -> 'ArchSmall' on Archmagi)."""
    return game_names.show(name)


def _named(fn):
    """launch and stop build their answers from many format strings: each answer, and each refusal, reads the games
    by name (game_names.name_text), whoever calls them (the CLI, maturation's deploy restart)."""
    import functools

    @functools.wraps(fn)
    def wrap(*a, **k):
        try:
            rc, text = fn(*a, **k)
        except Refused as e:
            raise Refused(game_names.name_text(str(e)))
        return rc, game_names.name_text(text)
    return wrap

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
# --wait's bound. Danger: a game that stays alive but never starts its bridge (a hung load) would hold a --wait caller
# forever; process exit and a failed bridge already end the wait sooner. Evidence of a hung load: none measured yet, so
# the bound sits past the slowest measured cold load (his full list: ~14.5 min on 2026-11-21, ~25 min in the
# rimworld-load-round skill) instead of under it. At 600 s it reported a healthy full-list load as failed (2026-11-21).
WAIT_S = 3600
EX_BLIND, EX_REFUSED = 2, 3
WIN_DIRS = ("/mnt/c/Windows/System32/WindowsPowerShell/v1.0", "/mnt/c/Windows/System32")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PREFS_TEMPLATE = os.path.join(REPO, "infrastructure", "stevedesktop", "Prefs.template.xml")
RIMFLOW_CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
MINIMAL_LIST = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
SITE_REGISTRY = os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck", "test_site_saves.json")
INSTALL_SUB = "game"                # <root>/<letter>/game: a named game's own install
# What a named game's install copies from game a's (MEASURED 2026-11-20 on Archmagi: about 2.5 GB with Mods). Anything
# else in game a's folder (ModsRetired, _ModsAside, Source, Transient, crash dumps) is not the game's to load.
INSTALL_DIRS = ("Data", "MonoBleedingEdge", "RimWorldWin64_Data", "BridgeTools", "Mods")
INSTALL_FILES = (GAME_EXE, "UnityPlayer.dll", "UnityCrashHandler64.exe", "Version.txt", "steam_appid.txt", "EULA.txt",
                 "Licenses.txt", "SteamInputDefaultConfiguration.vdf")
COPY_TIMEOUT_S = 1800   # danger: a copy that never ends holds the run (robocopy's retry defaults held BENCH 3.6 h on
                        # 2026-11-02, tool_traps.md); the copy of 2.5 GB takes minutes, so 30 min is far past a real one
# What crosses from WSL to python.exe. .claude/settings.json sets the same list for every agent shell, so a game that is
# only named (RM_GAME_INSTANCE=b) still reaches the tool (selftest_game_instance.py name_crosses checks the copy).
_WSLENV = ("RM_GAME_INSTANCE", "RM_GAME_USERDATA/p", "RM_GAME_LOGDIR/p", "GABP_SERVER_PORT", "GABP_TOKEN",
           "RIMFLOW_DRIVER_LOCK/p", "RM_INSTANCES_ROOT/p", "RM_GAME_A_LOGDIR/p")
_SAVE_RE = re.compile(r'"-savedatafolder=([^"]*)"|-savedatafolder="([^"]*)"|-savedatafolder=([^\s"]+)', re.I)


class InstanceError(ValueError):
    """A bad instance name, or a folder that will not hold what it was given. str() is the reason."""


class Blind(RuntimeError):
    """The process list could not be read. Never means "no game"."""


class Refused(RuntimeError):
    """An act that would land on the wrong game or an unmeasured machine. str() is the reason."""


def check_name(name):
    """A game as typed (ArchSmall, archbig, b, game:b, archmagi.b) -> its letter on this machine. Raises InstanceError
    naming an unknown name or another machine's game (game_names.letter)."""
    if name is None or not str(name).strip():
        raise InstanceError("bad game instance %r: name a game (%s)" % (name, game_names.known()))
    try:
        return game_names.letter(name)
    except game_names.GameNameError as e:
        raise InstanceError("bad game instance: %s" % e)


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
        raise InstanceError("%s has no instance folder: it is Steam's install, in its usual place" % _n(DEFAULT))
    return os.path.join(root(), name)


def log_path(name=None):
    return os.path.join(data_dir(name), "Player.log")


def token_path(name=None):
    return os.path.join(data_dir(name), "bridge_token.txt")


def lock_path(name=None):
    return os.path.join(data_dir(name), "DRIVER_LOCK.json")


def a_game_dir():
    """Game a's install, Steam's (RM_STEAMAPPS, else C:\\Program Files (x86)\\Steam\\steamapps), whatever this shell
    names."""
    import game_paths
    return game_paths.A_GAME_DIR


def game_dir(name=None):
    """The install a game runs from: a's is Steam's; a named game's is <root>/<letter>/game, its own."""
    name = check_name(name or current())
    if name == DEFAULT:
        return a_game_dir()
    return os.path.join(data_dir(name), INSTALL_SUB)


def _same_or_inside(p, top):
    def norm(x):
        return os.path.realpath(_native(x)).replace("\\", "/").rstrip("/").lower()
    return (norm(p) + "/").startswith(norm(top) + "/")


def _copy_tree(src, dst, files=None):
    """robocopy src -> dst (files: only those names, else the whole tree), bounded: /R:2 /W:5 and a timeout. Its exit
    0-7 is success; 8 and up is a failure, raised."""
    argv = ["timeout", "-k", "10", str(COPY_TIMEOUT_S), _exe("robocopy.exe"), win_path(src), win_path(dst)]
    argv += list(files) if files else ["/E"]
    argv += ["/R:2", "/W:5", "/NFL", "/NDL", "/NP", "/NJH"]
    r = _run(argv, timeout=COPY_TIMEOUT_S + 30)
    if r.returncode >= 8:
        raise InstanceError("robocopy %s -> %s failed (exit %d): %s" % (
            src, dst, r.returncode, ((r.stdout or "") + (r.stderr or ""))[-600:]))  # cut-ok: the tail of a copy log
    return r.returncode


def install(name=None, refresh=False, copier=None, source=None):
    """Copy game a's install into game `name`'s own folder (game_dir) -> (folder, [what was copied]). Reads game a's
    folder only; refuses a target inside it (or the reverse), so no route writes under game a. Without refresh an
    install that already has its exe is left as it is, so a deploy into it is not undone; refresh copies again over
    it (Mods included: /E adds and updates, never deletes)."""
    name = check_name(name or current())
    if name == DEFAULT:
        raise InstanceError("%s is Steam's own install; only a named game gets a copy" % _n(DEFAULT))
    src, dst = _native(source or a_game_dir()), game_dir(name)
    if _same_or_inside(dst, src) or _same_or_inside(src, dst):
        raise Refused("%s's install %s and %s's %s overlap: a write for one would land in the other" % (
            _n(name), dst, _n(DEFAULT), src))
    if not os.path.exists(os.path.join(src, GAME_EXE)):
        raise InstanceError("%s's install %s holds no %s" % (_n(DEFAULT), src, GAME_EXE))
    copier = copier or _copy_tree
    if os.path.exists(os.path.join(dst, GAME_EXE)) and not refresh:
        # kept as it is (a deploy into it stays), but a top-level file game a has gained since is copied: a
        # steam_appid.txt written after the copy must reach b too, or b starts with no Steam and no Workshop
        gained = [f for f in INSTALL_FILES if os.path.exists(os.path.join(src, f))
                  and not os.path.exists(os.path.join(dst, f))]
        if gained:
            copier(src, dst, gained)
        return dst, gained
    os.makedirs(dst, exist_ok=True)
    done = []
    files = [f for f in INSTALL_FILES if os.path.exists(os.path.join(src, f))]
    copier(src, dst, files)
    done += files
    for d in INSTALL_DIRS:
        if os.path.isdir(os.path.join(src, d)):
            copier(os.path.join(src, d), os.path.join(dst, d), None)
            done.append(d + "/")
    if not os.path.exists(os.path.join(dst, GAME_EXE)):
        raise InstanceError("the copy into %s left no %s" % (dst, GAME_EXE))
    return dst, done


def hold_refusal(name, despite=None):
    """-> why game `name` may not be started, stopped or written now, or None. The per-game hold is a live `pipe off
    game:<g>` switch (control.game_held). despite: the caller's reason to act on a held game anyway (the Conductor, on
    purpose); it is said on stderr. A store that cannot be read refuses (could not look is never "not held"), except a
    store that does not exist on this machine: a hold is only ever written into it, so none can stand there."""
    name = check_name(name)
    rf = os.path.join(REPO, "src", "RimMandrake", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import control
    try:
        if not os.path.exists(control.db_path()):
            return None
        why = control.game_held(name)
    except control.Unreadable as e:
        why = "the control store could not be read, so a hold on %s cannot be ruled out: %s" % (_n(name), e)
    if why and despite:
        sys.stderr.write("game_instance: %s is held (%s); acting anyway: %s\n" % (_n(name), why, despite))
        return None
    if why:
        return ("%s is held: %s\n  what passes: `./pipe on game:%s --why \"...\"`, or the act on purpose with "
                "--despite-hold \"<why>\"" % (_n(name), why, _n(name)))
    return None


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
    out["WSLENV"] = ":".join(wslenv)
    return out


def _under_root(p):
    """Is path p inside the instances root (a named game's folder, not game a's)?"""
    def norm(x):
        return _native(x).replace("\\", "/").rstrip("/").lower()
    return (norm(p) + "/").startswith(norm(root()) + "/")


def owner(cmdline):
    """The instance a game's command line says it is (see the module text); a game started from a named game's own
    install (<root>/<letter>/game/RimWorldWin64.exe) with no -savedatafolder is that game too."""
    m = _SAVE_RE.search(cmdline or "")
    if not m:
        e = re.search(r"[\\/]instances[\\/]([a-z])[\\/]%s[\\/]%s" % (INSTALL_SUB, re.escape(GAME_EXE.lower())),
                      (cmdline or "").lower())
        return e.group(1) if e else DEFAULT
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


def alive(pids_):
    """-> those of `pids_` still in the game process list, read by pid alone. For the wait after a stop of pids already
    attributed: a closing RimWorld reads an empty command line before it leaves the list, so pids() raised Blind on our
    own stopped game (Pyrelands visit 5, pid 15352, 2026-11-22 03:45 PST). Raises Blind when the list did not answer."""
    want = set(pids_)
    return sorted(g["pid"] for g in games() if g["pid"] in want)


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


def live_holder(name, new_run=False):
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
        return host_guard.crossing(new_run=new_run)


def child_env(name, base=None):
    """-> a copy of the environment aimed at game `name`: RM_GAME_INSTANCE, and RIMFLOW_DRIVER_LOCK with it when this
    shell pins one (that variable names the lock of the game RM_GAME_INSTANCE names: `env b` exports both). Changing
    one without the other made a child read game a's lock as game b's (RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_
    RECORDS_DISAGREE, found by selftest_game_instance 2026-11-21)."""
    env = dict(os.environ if base is None else base)
    have = (env.get(INSTANCE_ENV) or DEFAULT).strip().lower() or DEFAULT
    if name == DEFAULT:
        env.pop(INSTANCE_ENV, None)
    else:
        env[INSTANCE_ENV] = name
    if "RIMFLOW_DRIVER_LOCK" in env and have != name:
        if name == DEFAULT:
            env.pop("RIMFLOW_DRIVER_LOCK")      # game a's own lock: driver_lock's default (none under a test ledger)
        else:
            env["RIMFLOW_DRIVER_LOCK"] = lock_path(name)
    return env


def bridge_host_args(name):
    """["--host", <machine>] when game `name` is this machine's today's game and the machine is not the default bridge
    host, else []. `rimflow bridge idle` with no --host reads ARCHMAGI's lock on every machine (ambient_bridge_host
    answers None for game a), so SteveDesktop's own game a was gated on whoever held Archmagi's bridge, e.g. the
    Conductor's walk (MEASURED 2026-11-20 12:40 PST on Steve's clone: `bridge idle` NOT TAKEABLE, BENCH holds, while
    `--host stevedesktop` said TAKEABLE). A named instance already carries its machine (<host>.<letter>)."""
    if name != DEFAULT:
        return []
    rf = os.path.join(REPO, "src", "RimMandrake", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import model
    machine = (os.environ.get("RM_HOST") or socket.gethostname()).strip().lower()
    return ["--host", machine] if machine in model.BRIDGE_HOSTS and machine != model.DEFAULT_BRIDGE_HOST else []


def bridge_refusal(name, purpose=None, timeout=120, new_run=False, seat=None, despite=None):
    """None when this seat may stop game `name`, else why not and what would pass. RIMMANDRAKE_GUARD_GAME_STOP_BY_BRIDGE_HOLD
    (GPT review p2.F2: stop used to taskkill with no bridge check). The verdict is rimflow's own, not a second copy:
    `rimflow bridge idle` (the delegated gate) passes a bridge that is free, ours, or stale by the 45-min rule, and his
    OWNER hold only 45 min after his last interaction (an UNMEASURED reading of him refuses); it reads the game's
    driver lock, the one record (game_lock.py). Only its exit 0 with a TAKEABLE line passes: no answer is no permission. seat: the
    caller's seat, passed as `--seat` (the systemd tick names none in its env, and a seatless `rimflow` refuses: "I
    cannot tell which seat I am", RIMMANDRAKE_REPAIR_GIMMESOMESLACK_FORM_REFUSAL_AT_THE_RUN_FIVE); an env seat still
    wins, as in rimflow's own order."""
    purpose = purpose or "stop %s (game_instance.py stop)" % _n(name)
    held = live_holder(name, new_run)
    if held:
        return ("%s is another live driver's: %s\n  what passes: its run ends or releases it (another run's game "
                "is never stopped or handed out)" % (_n(name), held))
    env = child_env(name)                   # the bridge of the game being stopped, whatever this shell drives
    host = bridge_host_args(name)
    try:
        r = subprocess.run([sys.executable, RIMFLOW_CLI, "bridge", "idle"] + host + ["--for", purpose]
                           + (["--seat", seat] if seat else [])
                           + (["--despite-hold", despite] if despite else []), env=env,
                           capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        rc, out, text = r.returncode, r.stdout or "", ((r.stdout or "") + (r.stderr or "")).strip()
    except (OSError, subprocess.SubprocessError) as e:
        rc, out, text = None, "", str(e)
    if rc == 0 and re.search(r"^TAKEABLE  ", out, re.M):
        return None
    if rc not in (0, 1):
        text = "UNMEASURED: `rimflow bridge idle` gave no verdict (exit %s): %s" % (rc, text or "no output")
    return ("the bridge does not let this seat stop %s: %s\n  what passes: hold it yourself, then stop again  "
            "rimflow bridge take%s --for \"%s\"  (another seat's live hold needs --force; his OWNER hold is takeable "
            "only 45 min after his last interaction, --force included)"
            % (_n(name), text, " --host " + _n(host[1]) if host else "" if name == DEFAULT else " --host %s" % _n(name),
               purpose))


@_named
def stop(pid_=None, force=False, name=None, purpose=None, despite=None, seat=None, broken=False):
    """taskkill by process id -> (exit code, text). With no pid, every game of this instance; a pid must be this
    instance's, or Refused. Raises Blind when ownership cannot be read: nothing is signalled on a guess. Refused too
    while the bridge is not this seat's to act on (bridge_refusal): a stop is a reboot, the agent's to call only when
    the bridge is free, ours, or stale (owner, 2026-09-02; his OWNER hold by card 2026-10-30). A confirmed broken game
    uses the emergency stop rule (CLAUDE.md §Facts you cannot guess), including held games."""
    name = check_name(name or current())
    if broken:
        import game_watcher
        reading, confirmed = game_watcher.confirm(name)
        if reading.state == "could_not_look":
            raise Blind("%s: %s" % (_n(name), reading.detail))
        if not confirmed or (pid_ is not None and pid_ != reading.pid):
            raise Refused("%s: this stop needs a confirmed broken process (%s: %s)" %
                          (_n(name), reading.state, reading.detail))
        if procs(name) != [{"pid": reading.pid, "start": reading.start}]:
            raise Refused("%s: the confirmed process changed before stop" % _n(name))
        pid_, force = reading.pid, True
        mine = [pid_]
    else:
        mine = pids(name)
    if pid_ is not None and pid_ not in mine:
        raise Refused("pid %s is not %s's (%s: %s)" % (pid_, _n(name), _n(name), mine or "not running"))
    targets = [pid_] if pid_ is not None else mine
    if not targets:
        return 0, "%s is not running" % _n(name)
    if not broken:
        held = hold_refusal(name, despite)
        if held:
            raise Refused(held)
        why = bridge_refusal(name, purpose, seat=seat, despite=despite)   # his pipe hold, passed on purpose there too
        if why:
            raise Refused(why)
    rc, out = 0, []
    for p in targets:
        try:
            r = _run([_exe("taskkill.exe")] + (["/F"] if force else []) + ["/PID", str(p)])
        except (OSError, subprocess.SubprocessError) as e:
            if not broken:
                raise
            rc, out = 1, [str(e)]
            break
        rc = rc or r.returncode
        out.append(((r.stdout or "") + (r.stderr or "")).strip() or "taskkill /PID %d" % p)
    if broken:
        out.insert(0, "%s %s pid %d: %s (%s)" %
                   ("STOP FAILED" if rc else "STOPPED", _n(name), pid_, reading.state, reading.detail))
        rc = int(rc != 0)
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
    text = _seeded_prefs(path)
    if text is not None:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def _seeded_prefs(path):
    """-> the Prefs.xml text seed_prefs would write at PATH, or None when the file already reads so."""
    src = path if os.path.exists(path) else PREFS_TEMPLATE
    with open(src, encoding="utf-8", newline="") as f:
        was = f.read()
    text = _set_pref(_set_pref(was, "fullscreen", "False"), "runInBackground", "True")
    text = _set_pref(_set_pref(text, "screenWidth", WINDOW[0], keep=True), "screenHeight", WINDOW[1], keep=True)
    return text if src != path or text != was else None


def _unseeded(name, d):
    """-> what prepare would still have to write into game NAME's folder D besides its companion profile, [] when it is
    seeded already. A running game rewrites Prefs.xml from memory on exit, so a seed written under it is lost."""
    gaps = [] if os.path.exists(os.path.join(game_dir(name), GAME_EXE)) else ["its install"]
    gaps += [] if read_token(name) else ["its bridge token"]
    gaps += [] if os.path.exists(os.path.join(d, "Config", "ModsConfig.xml")) else ["Config/ModsConfig.xml"]
    return gaps + ([] if _seeded_prefs(os.path.join(d, "Config", "Prefs.xml")) is None else ["Config/Prefs.xml"])


def a_saves_dir():
    """ArchBig's own Saves folder (LocalLow), whatever game this shell names: the registered site saves live there."""
    import game_paths
    return game_paths.resolve(os.path.join(game_paths._DEF_LOW_WIN, "Saves"), os.path.join(game_paths._DEF_LOW_WSL, "Saves"))


def _registered_saves(registry):
    """Every save name the site registry (modcheck/test_site_saves.json) records, at any depth under a `save` key."""
    with open(registry, encoding="utf-8") as f:
        doc = json.load(f)
    names, todo = set(), [doc]
    while todo:
        x = todo.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "save" and isinstance(v, str) and v:
                    names.add(v)
                else:
                    todo.append(v)
        elif isinstance(x, list):
            todo.extend(x)
    return names


def seed_site_saves(name=None, source=None, registry=SITE_REGISTRY):
    """-> the names copied. A named game has its own Saves folder, and the registered site saves were made on ArchBig, so a
    Pyrelands check on ArchSmall read "SiteError: programState 'Entry'" for a save it never had (2026-11-25 06:18 PST,
    RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME). Copies each registered save the named game lacks from
    ArchBig's folder; never overwrites one it has, never copies one ArchBig lacks, never writes ArchBig's folder."""
    name = check_name(name or current())
    if name == DEFAULT:
        return []
    src, dst = source or a_saves_dir(), os.path.join(data_dir(name), "Saves")
    os.makedirs(dst, exist_ok=True)
    done = []
    for n in sorted(_registered_saves(registry)):
        s, d = os.path.join(src, n + ".rws"), os.path.join(dst, n + ".rws")
        if os.path.exists(d) or not os.path.isfile(s):
            continue
        shutil.copyfile(s, d + ".part")
        os.replace(d + ".part", d)
        done.append(n)
    return done


def prepare(name=None):
    """Seed the folder a named instance needs. It reads no other game's state, so it works while A runs; it refuses while
    its own game runs and the folder is not seeded yet: that game rewrites Prefs from memory on exit. A running game whose
    folder is seeded already (live 2026-11-23: Steve2's worker keeps its game up between jobs, and 46 of 53 Steve2 jobs
    were refused at this step) only gets its companion profile renewed, as game a's `rw_game.sh init` does. Keeps
    whatever list and Prefs are already there."""
    name = check_name(name or current())
    d = data_dir(name)
    if re.search(r"\s", d):
        raise Refused("instance folder %r has whitespace: the launch's -savedatafolder is unquoted, as measured" % d)
    up = running(name)
    if up and _unseeded(name, d):
        raise Refused("%s is running; it rewrites Prefs.xml on exit, so %s cannot be seeded now. Stop it first" % (
            _n(name), ", ".join(_unseeded(name, d))))
    for sub in ("Config", "JawaBench"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    try:
        seed_site_saves(name)
    except (OSError, ValueError) as e:      # a check on a save b lacks still says so by name (SiteError), so go on
        sys.stderr.write("game_instance: could not seed %s's site saves from ArchBig's: %s\n" % (_n(name), e))
    if not up:
        install(name)
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


def _need_appid(what, name=DEFAULT):
    gd = game_dir(name)
    if not os.path.exists(os.path.join(gd, "steam_appid.txt")):
        raise Refused("%s holds no steam_appid.txt, so %s would get no Steam and no Workshop mods; write 294100 into it "
                      "(Valve's documented file; Steam's own launch of game a is unchanged by it)" % (gd, what))


def steam_log_path():
    """Steam's console_log.txt: Steam's install is three folders above game a's common/RimWorld (never a named game's
    own install, which is not under Steam)."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(a_game_dir()))), "logs", "console_log.txt")


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
    gd = win_path(a_game_dir())
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
    _need_appid("%s started directly" % _n(DEFAULT))
    flags = inherited_flags(rows)
    _start_direct_a(flags)
    return "direct", ("directly (Steam %s while %s runs), flags %s" % (
        "answered WaitingPrevProcess" if said else "said nothing", ",".join(_n(o) for o in others) or "?", " ".join(flags) or "none"))


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


@_named
def launch(name=None, wait=False, wait_s=WAIT_S, sleep=time.sleep, clock=time.time, despite=None):
    """Start a game -> (exit code, text). Game a through Steam, or directly when Steam will not (fire_a); a named game
    directly. Raises Refused for no Steam, or a direct start with no steam_appid.txt; a game already up is ok, with its
    pid. wait: until this run's log has the port line."""
    name = check_name(name or current())
    up = pid(name)
    if up:
        return 0, "game %s already running, pid %d" % (name, up)
    held = hold_refusal(name, despite)
    if held:
        raise Refused(held)
    if not _steam_running():
        raise Refused("Steam is not running, and a game started now would have no Workshop mods (rw_game.sh up starts it)")
    if name == DEFAULT:
        return _launch_a(wait, wait_s, sleep, clock)
    d = prepare(name)
    _need_appid("game %s" % name, name)
    log = log_path(name)
    if os.path.exists(log):
        os.replace(log, log + ".prev")
    wd = win_path(d)
    gdir = win_path(game_dir(name))
    args = ["-savedatafolder=%s" % wd, "-logfile", "%s\\Player.log" % wd, "-screen-fullscreen", "0",
            "-screen-width", str(WINDOW[0]), "-screen-height", str(WINDOW[1])]
    args += inherited_flags()
    script = ("$env:GABP_SERVER_PORT='%d'; $env:GABP_TOKEN='%s'; Start-Process -FilePath '%s\\%s' -WorkingDirectory '%s' "
              "-ArgumentList %s" % (port(name), ensure_token(name), gdir, GAME_EXE, gdir,
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
    refusal = refusal or (lambda n, p: bridge_refusal(n, p, new_run=True))
    why = {}
    for n in instances():
        if n in busy:
            why[n] = "a live run drives it"
            continue
        no = hold_refusal(n) or refusal(n, purpose or "take %s for a live run (game_instance.py free)" % _n(n))
        if no:
            why[n] = no.splitlines()[0]
            continue
        return n, why
    return None, why


def held_by_anyone(name):
    """-> why game `name` has a holder, the asker's own window included, else None: its per-game hold, or a live
    holder of its driver lock. leftovers asks this first: inside the Conductor's own process tree `rimflow bridge idle`
    reads the Conductor's walk hold on game a as ours, and leftovers said to stop ArchBig (MEASURED 2026-11-20)."""
    return hold_refusal(name) or live_holder(name, new_run=True)


def leftovers(busy=(), refusal=None, holder=None):
    """-> [{instance, pid}]: games up that nobody holds (not busy, no holder at all, bridge takeable): an idle leftover
    may be stopped."""
    refusal = refusal or bridge_refusal
    holder = holder or held_by_anyone
    rows = games()
    if any(g["instance"] is None for g in rows):
        raise Blind("cannot read a game's command line, so no game can be called nobody's")
    return [{"instance": g["instance"], "pid": g["pid"]} for g in sorted(rows, key=lambda g: (g["instance"], g["pid"]))
            if g["instance"] not in busy and not holder(g["instance"])
            and not refusal(g["instance"], "is %s an idle leftover" % _n(g["instance"]))]


def brief(name, full_list=None):
    """A run brief's section naming the game it drives (maturation.game_brief, the Dispatch step's in-game runs).
    full_list: the visit's full-list checks; on a named game they cannot run (his full list on the second game beside
    the first does not fit in memory), so the brief says to record each UNMEASURED with that cause."""
    name = check_name(name)
    me, first, second = _n(name), _n(DEFAULT), _n("b")
    extra = []
    if name != DEFAULT and full_list:
        # RIMMANDRAKE_ALIGN_SECOND_GAME_FULL_LIST_ROW_WITH_EXIT_READER (Pyrelands visit 6, 2026-11-23): the row this
        # names must carry the class, unrepaired cause and owner maturation.line_class counts as not_counted; a bare
        # UNMEASURED row read 'unclassed' and refused the exit on form (selftest_full_list_row_on_second_game.py)
        extra = ["- These checks need his full list, which %s cannot hold beside %s (memory): %s. Run every "
                 "other check on a tier list here; give each of these one row with result UNMEASURED, detail "
                 "`%s: tier list only beside %s`, class `SITE`, unrepaired `%s cannot hold his full list beside %s "
                 "in memory, so this check did not run here` and owner `%s: its full-list run of this check` (an "
                 "UNMEASURED row spends nothing, and its bar stays undecided); %s runs them later."
                 % (me, first, ", ".join(full_list), me, first, me, first, first, first)]
    return "\n".join([
        "## Your game: %s" % me, "",
        "This machine runs two RimWorld games, %s and %s. This run drives **%s**: `RM_GAME_INSTANCE=%s` is set in "
        "your environment, so game_paths, the bridge client (port %d), `rimflow bridge take` and the driver lock all "
        "follow it. The other game is another run's: never stop, restart or deploy over it, and never take its bridge."
        % (first, second, me, name, port(name)),
        "- Start yours, if it is down: `python3 src/RimMandrake/Utils/game_instance.py launch %s --wait` (%s goes "
        "through Steam, or directly with Steam's flags when Steam refuses beside the other game; %s always directly)."
        % (me, first, second),
        "- Stop only yours, by pid: `python3 src/RimMandrake/Utils/game_instance.py stop --instance %s`. "
        "`game_instance.py status` shows both." % me,
        ("- %s has its own install, Mods and BridgeTools (`%s`): with `RM_GAME_INSTANCE=%s` set, "
         "`deploy_custom_mods.py` and `bridgetools/build.py` write only there. Never deploy with another game named."
         % (me, win_path(game_dir(name)), name)) if name != DEFAULT else
        "- %s is Steam's install; %s has its own. Deploy only your own mod's files." % (first, second)] + extra + [""])


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def status_lines():
    """One line per game: up or stopped, its port, and who drives it, read from its lock (game_lock.py, the one record
    of who drives a game)."""
    rows = games()
    names = sorted({DEFAULT, current()} | {g["instance"] or "?" for g in rows})
    out = []
    for n in names:
        mine = [g["pid"] for g in rows if (g["instance"] or "?") == n]
        out.append("%-9s  %-22s  port %s%s" % (_n(n), "running pid %s" % ",".join(map(str, mine)) if mine else "stopped",
                                             "?" if n == "?" else port(n), "" if n == "?" else "  | " + _driver(n)))
    return out


def _driver(name):
    rf = os.path.join(REPO, "src", "RimMandrake", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import game_lock
    try:
        return game_lock.query(name, pipe=False)["line"]
    except Exception as e:  # noqa: BLE001  (could not look is said, never read as free)
        return "%s: COULD NOT LOOK (%s: %s)" % (_n(name), type(e).__name__, e)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="game_instance.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for verb in ("env", "pid", "prepare"):
        sub.add_parser(verb).add_argument("name", nargs="?")
    s = sub.add_parser("install")
    s.add_argument("name")
    s.add_argument("--refresh", action="store_true", help="copy again over an existing install (adds and updates)")
    s = sub.add_parser("launch")
    s.add_argument("name", nargs="?")
    s.add_argument("--wait", action="store_true")
    s.add_argument("--despite-hold", dest="despite", default=None, help="act on a held game on purpose: why")
    s = sub.add_parser("stop")
    s.add_argument("pid", nargs="?", type=int)
    s.add_argument("--force", action="store_true")
    s.add_argument("--instance", default=None)
    s.add_argument("--for", dest="purpose", default=None, help="what the stop is for (the bridge check records it)")
    s.add_argument("--despite-hold", dest="despite", default=None, help="act on a held game on purpose: why")
    # Emergency stop requires the full flag. Keep ordinary help and parse errors as before.
    options = argv[:argv.index("--")] if "--" in argv else argv
    if "--broken" in options:
        s.add_argument("--broken", action="store_true", help="confirm broken disk health before a forced stop, including held games")
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
        elif a.cmd == "install":
            where, done = install(a.name, a.refresh)
            print("%s install %s: %s" % (_n(check_name(a.name)), win_path(where),
                                              "copied " + ", ".join(done) if done else "already there, left as it is"))
        elif a.cmd == "status":
            print("\n".join(status_lines()))
        elif a.cmd == "free":
            got, why = free([check_name(x) for x in a.busy], a.purpose)
            if not got:
                raise Refused("no game is free: %s" % "; ".join("%s: %s" % (_n(k), v) for k, v in sorted(why.items())))
            print(_n(got))
        elif a.cmd == "leftovers":
            for g in leftovers():
                print("%s  pid %d  up, nobody holds it: may be stopped (game_instance.py stop --instance %s)" % (
                    _n(g["instance"]), g["pid"], _n(g["instance"])))
        else:
            if a.cmd == "stop":
                emergency = {"broken": True} if getattr(a, "broken", False) else {}
                rc, text = stop(a.pid, a.force, a.instance, a.purpose, a.despite, **emergency)
            else:
                rc, text = launch(a.name, a.wait, despite=a.despite)
            print(text)
            return rc
    except Blind as e:
        print("BLIND: %s" % game_names.name_text(str(e)), file=sys.stderr)
        return EX_BLIND
    except (Refused, InstanceError) as e:
        print("REFUSED: %s" % game_names.name_text(str(e)), file=sys.stderr)
        return EX_REFUSED
    return 0


if __name__ == "__main__":
    sys.exit(main())
