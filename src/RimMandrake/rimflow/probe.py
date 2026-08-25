"""probe.py — the ONE place that answers "is the game actually running?"

🔴 **OWNER'S RULING, 2026-08-22 12:47.** *"I keep seeing things that say 'something says
the game is up, but the owner said it was down' and neither one is actually just checking
to see the truth. We need to simplify this game state business. Any agent is absolutely
able to check what it literally is to some degree. The point of the user saying anything
was to authorize people to react to a game state change, and there should be precisely ONE
place that variable is recorded and no more."*

⇒ **The measurement WINS, silently.** No seat writes a paragraph about a disagreement ever
again — when the record contradicts the machine, the record is corrected on the spot and
the event carries `measured: true`. The owner's word never stopped mattering; it just is
not the source of truth for *running / not running*. It is authorization to REACT to a
change, and it is the only thing that can name the finer states the machine cannot see.

## What the machine can and cannot see

| | measurable | who says it |
|---|---|---|
| process alive | ✅ `tasklist.exe` | anyone, any time |
| bridge answering | ✅ TCP connect | anyone, any time |
| `DEPLOYING` vs `DOWN` | ⛔ both are "no process" | the owner |
| `GOING_DOWN` vs `UP` | ⛔ both are "process alive" | the owner |

🔑 **So a contradiction is narrower than it looks**, and this module only corrects the two
that are real:

* recorded `UP` / `LOADING` / `GOING_DOWN` while **nothing is running** → `DOWN`
* recorded `DOWN` / `DEPLOYING` while **something IS running** → `UP` if the bridge
  answers, else `LOADING`

Everything else is left alone, because the owner knows something the probe does not.

⚠️ **A running process is not a loaded game.** A load can abort and leave the bridge
answering; `game_loaded` is not proof of a usable game. That is why `UP` here means "the
process is alive and the bridge replies", never "the save is playable".
"""

import io
import json
import os
import socket
import sys
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
CACHE = os.path.join(REPO, "infrastructure", "state", "derived", "gamestate_probe.json")

# How long a reading stays good. Short enough that a seat never acts on a stale one,
# long enough that `rimflow next` in a loop does not shell out every time.
TTL_SECONDS = 20

PROCESS = "RimWorldWin64"

# Recorded states that the two measurable facts can contradict.
_NOT_RUNNING_CONTRADICTS = ("UP", "LOADING", "GOING_DOWN")
_RUNNING_CONTRADICTS = ("DOWN", "DEPLOYING")


def _process_alive():
    """True/False, or None when the question could not be asked at all.

    ⛔ None is NOT False. On a host with no `tasklist.exe` — a Linux CI box, a container —
    "I could not look" must never be reported as "nothing is running", because that would
    silently rewrite a correct `UP` to `DOWN`. Ignorance answers None and the caller
    leaves the record alone.
    """
    try:
        out = subprocess.run(["tasklist.exe"], capture_output=True, text=True,
                             timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return PROCESS.lower() in (out.stdout or "").lower()


def _under_wsl():
    """WSL2 is NAT-mode: 127.0.0.1 in this namespace is NOT Windows' loopback."""
    try:
        return "microsoft" in io.open("/proc/sys/kernel/osrelease").read().lower()
    except OSError:
        return False


def _bridge_port():
    """The port, from the env if set, else scraped out of Player.log like the client."""
    env = os.environ.get("GABP_SERVER_PORT")
    if env:
        try:
            return int(env)
        except ValueError:
            pass
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
        from rimbridge_client import discover_from_log
        _host, port, _tok = discover_from_log()
        return int(port) if port else None
    except Exception:
        return None


def _bridge_answers():
    """True/False/None — does something accept a connection on the bridge port?

    Only ever used to separate `UP` from `LOADING`. ⚠️ A None is conservative for the
    VERDICT and was NOT harmless for the MESSAGE: `measure` used to render None and
    False identically as "bridge silent", so "I never looked" and "I looked and got
    nothing" were indistinguishable to every reader. They are now worded apart.

    🔴 **Corrected 2026-08-25 (CHECK).** This used to `socket.create_connection` to
    `127.0.0.1` unconditionally. RimBridge binds **Windows** loopback and WSL2 is
    NAT-mode, so from any agent seat that socket is refused *while the bridge is
    answering fine* — the probe returned a clean `False` and `./game` reported
    `LOADING` for a fully-up game, which parks BUILD's deploys. Under WSL the reading
    is now taken with `netstat.exe`, which sees the real Windows listener.
    """
    port = _bridge_port()
    if not port:
        return None
    if _under_wsl():
        try:
            out = subprocess.run(["netstat.exe", "-ano", "-p", "TCP"],
                                 capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.SubprocessError):
            return None          # could not look — NOT a negative
        for line in (out.stdout or "").splitlines():
            if "LISTENING" in line and (":%d " % port) in line + " ":
                return True
        return False
    try:
        with socket.create_connection(("127.0.0.1", int(port)), timeout=2):
            return True
    except (OSError, ValueError):
        return False


def measure(use_cache=True):
    """The reading. Returns a dict and never raises.

        {"running": True/False/None, "bridge": True/False/None,
         "implies": "UP"|"LOADING"|"DOWN"|None, "evidence": "...", "at": <epoch>}

    `implies` is None when the probe could not look — the one case where a caller must
    leave the recorded value exactly as it found it.
    """
    if use_cache:
        try:
            with open(CACHE, "r", encoding="utf-8") as fh:
                cached = json.load(fh)
            if time.time() - cached.get("at", 0) < TTL_SECONDS:
                return cached
        except (OSError, ValueError):
            pass

    running = _process_alive()
    bridge = None
    if running:
        bridge = _bridge_answers()

    if running is None:
        implies, evidence = None, "could not run tasklist.exe — no reading taken"
    elif not running:
        implies, evidence = "DOWN", "tasklist.exe lists no %s" % PROCESS
    elif bridge:
        implies, evidence = "UP", "%s running, bridge answers" % PROCESS
    elif bridge is False:
        implies, evidence = "LOADING", "%s running, bridge did not answer" % PROCESS
    else:
        # 🔴 bridge is None: THE PROBE NEVER LOOKED. This used to print "bridge
        # silent" — identical wording to a real negative — so every seat read
        # ignorance as a measurement. Measured 2026-08-23: it said "bridge silent"
        # all session while the bridge was up the whole time, because
        # GABP_SERVER_PORT is simply not set in a plain shell.
        # 🔑 An instrument must never spell ignorance the same way as a finding.
        implies, evidence = ("LOADING",
                             "%s running; BRIDGE NOT PROBED — no port found in the "
                             "environment or in Player.log, so LOADING here is a "
                             "DEFAULT, not a reading." % PROCESS)

    reading = {"running": running, "bridge": bridge, "implies": implies,
               "evidence": evidence, "at": time.time()}
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump(reading, fh)
    except OSError:
        pass
    return reading


def contradicts(recorded, reading):
    """The corrected state, or None when the record and the machine agree.

    🔑 This is the whole rule, and it is deliberately small. If it ever grows a third
    case, that case is probably something only the owner can see.
    """
    implied = reading.get("implies")
    if implied is None:
        return None
    if reading.get("running") is False and recorded in _NOT_RUNNING_CONTRADICTS:
        return "DOWN"
    if reading.get("running") is True and recorded in _RUNNING_CONTRADICTS:
        return implied
    # 🔴 The third case, added 2026-08-25 (CHECK). The docstring above warns that a
    # third case is "probably something only the owner can see" — this one is the
    # opposite, and it is the case the machine sees BEST. `LOADING` means exactly
    # "process alive, bridge not yet answering"; the moment the bridge answers, that
    # is measured false. This module's own table already promises this correction
    # ("→ `UP` if the bridge answers, else `LOADING`") and only reached it from DOWN
    # and DEPLOYING, so a game that came up left the board reading LOADING forever.
    # ⚠️ It is only ever taken on a POSITIVE bridge reading — never on None, and never
    # to move UP back to LOADING, which is the owner's GOING_DOWN territory.
    if (recorded == "LOADING" and reading.get("running") is True
            and reading.get("bridge") is True):
        return "UP"
    return None
