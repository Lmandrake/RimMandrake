"""load_policy.py - the ONE declared cold-load deadline policy (load_policy.json beside this file).

Before 2026-10-10 the tree carried five disagreeing budgets (launch_and_wait ~5-7 min, live_session 15 min,
belt_watchdog 25 min, docs 25/33 min) and one of them was read as a kill trigger. Every caller now asks here:

    import load_policy
    p = load_policy.profile_for(active_count)      # 'full' or 'minimal' numbers
    p["process_to_bridge_warn_s"]                  # past this: investigate, capture evidence
    p["process_to_bridge_deadline_s"]              # past this: the ATTEMPT ends; the process is NOT killed

kill_on_deadline is asserted False on load: a policy file that turns a clock into a kill is refused.

Version 2 (BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY) adds the per-call rule: call_deadline is "absolute_monotonic",
so a bridge call's limit is ONE instant fixed when it is sent (Deadline below) and no event flood or trickle of bytes
extends it (GPT N04); and every deadline-exceeded message says whether the game process is ALIVE, DEAD or UNKNOWN
(deadline_exceeded), because "it timed out" alone sent readers to kill a game that was loading fine.
"""
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "load_policy.json")
KEYS = ("launch_to_process_s", "process_to_bridge_warn_s", "process_to_bridge_deadline_s",
        "bridge_to_dispatcher_s", "kill_existing_grace_s", "late_arrival_watch_s")


VERSION = 2
# Every file that must take its deadlines from here (selftest_bridge_deadlines.py proves each one does).
READERS = ("src/RimMandrake/bridgetools/launch_ready.py", "src/RimMandrake/Utils/belt_watchdog.py",
           "src/RimMandrake/Utils/northstar_driver/live_session.py",
           "src/RimMandrake/FlowWorks/northstar/playtest_runner.py", "src/RimMandrake/Utils/rimbridge_client.py")
GAME_IMAGE = "RimWorldWin64.exe"


class PolicyError(ValueError):
    pass


def load(path=PATH):
    with open(path, encoding="utf-8") as fh:
        pol = json.load(fh)
    if pol.get("version") != VERSION:
        raise PolicyError("%s: version %r, this reader knows %d" % (path, pol.get("version"), VERSION))
    if pol.get("call_deadline") != "absolute_monotonic":
        raise PolicyError("%s: call_deadline must be 'absolute_monotonic' - traffic must never extend a call" % path)
    if not isinstance(pol.get("playtest_run_wall_s"), int) or pol["playtest_run_wall_s"] <= 0:
        raise PolicyError("%s: playtest_run_wall_s must be a positive int" % path)
    if pol.get("kill_on_deadline") is not False:
        raise PolicyError("%s: kill_on_deadline must be false - a deadline never kills by itself" % path)
    for name, prof in pol.get("profiles", {}).items():
        missing = [k for k in KEYS if not isinstance(prof.get(k), int) or prof[k] <= 0]
        if missing:
            raise PolicyError("%s: profile %s lacks positive int %s" % (path, name, missing))
        if prof["process_to_bridge_warn_s"] >= prof["process_to_bridge_deadline_s"]:
            raise PolicyError("%s: profile %s warn must be < deadline" % (path, name))
    for need in ("full", "minimal"):
        if need not in pol.get("profiles", {}):
            raise PolicyError("%s: profile %r missing" % (path, need))
    return pol


def profile_name(active_count, pol=None):
    """'minimal' for a small list, else 'full'. None (count unknown) is 'full' - the generous one."""
    pol = pol or load()
    if active_count is not None and active_count <= pol["minimal_max_active_mods"]:
        return "minimal"
    return "full"


def profile_for(active_count=None, pol=None):
    pol = pol or load()
    prof = dict(pol["profiles"][profile_name(active_count, pol)])
    prof["name"] = profile_name(active_count, pol)
    return prof


class Deadline:
    """One absolute instant on the monotonic clock, fixed at creation. Nothing that happens later (an event, a byte,
    a retry) moves it; callers ask remaining() before every blocking read and stop at <= 0."""

    def __init__(self, seconds, clock=time.monotonic):
        self.clock = clock
        self.limit_s = float(seconds)
        self.start = clock()
        self.at = self.start + self.limit_s

    def remaining(self):
        return self.at - self.clock()

    def expired(self):
        return self.remaining() <= 0

    def elapsed(self):
        return self.clock() - self.start


def game_alive(image=GAME_IMAGE, timeout=15):
    """True/False when tasklist answered about the game image, None (UNKNOWN) when it could not be asked. Read-only:
    this never signals, kills or focuses anything."""
    exe = "tasklist" if os.name == "nt" else "tasklist.exe"
    try:
        out = subprocess.run([exe, "/FI", "IMAGENAME eq %s" % image, "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    if image.lower() in out.lower():
        return True
    return False if out.strip() else None


def alive_word(alive):
    return {True: "ALIVE", False: "DEAD"}.get(alive, "UNKNOWN")


def deadline_exceeded(what, elapsed_s, limit_s, alive="probe"):
    """THE deadline-exceeded sentence: names the limit, the elapsed time and the game process state; says nothing
    was killed (kill_on_deadline is false). alive='probe' asks game_alive(); pass True/False/None to skip the probe."""
    if alive == "probe":
        alive = game_alive()
    return ("deadline exceeded: %s after %.1f s (absolute limit %.1f s); game process %s; nothing was killed"
            % (what, elapsed_s, limit_s, alive_word(alive)))


def active_count_from_modsconfig(path=None):
    """Parsed activeMods count of the ModsConfig the NEXT load reads, or None if unreadable."""
    import xml.etree.ElementTree as ET
    if path is None:
        try:
            from game_paths import MODS_CONFIG as path
        except ImportError:
            return None
    try:
        am = ET.parse(path).getroot().find("activeMods")
        return None if am is None else len(am.findall("li"))
    except (OSError, ET.ParseError):
        return None


if __name__ == "__main__":
    n = active_count_from_modsconfig()
    print("active mods %s -> profile %s: %s" % (n, profile_name(n), json.dumps(profile_for(n))))
