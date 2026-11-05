#!/usr/bin/env python3
"""
rimbridge_client.py - talk to a LIVE RimWorld through the RimBridgeServer GABP bridge.

*** THIS DRIVES A RUNNING GAME. THERE IS NO UNDO. ***
=====================================================
Every call goes straight into the RimWorld process that is on screen right now.
A colony that took twenty minutes to load can be wrecked by one careless call.
This module deliberately does NOT enforce read-only - it cannot, because the
bridge decides what a tool does, not us - so the discipline is yours:

  SAFE   rimbridge/ping, get_bridge_status, list_capabilities, list_logs,
         rimworld/get_game_info, list_*, get_*, search_debug_actions
  NEVER  rimworld/execute_debug_action, spawn_thing, save_game, load_game,
         set_*, rimbridge/run_lua, run_script - these mutate or destroy state

Searching for and DESCRIBING a debug action is free. EXECUTING one is not.

READ-ONLY IS NOT THE SAME AS HARMLESS
=====================================
2026-08-10: `rimworld/list_debug_action_roots` and `rimworld/search_debug_actions`
killed a live 562-mod colony. Neither tool changes game state - both build
RimWorld's debug node graph on the main thread, and on a load order this size
that build never returned. Unity stopped pumping, Windows raised AppHangB1, and
the process was terminated ~4 minutes later; 23 minutes of load time went with
it. There was no exception in Player.log, just silence.

So: on a heavily modded install, treat the four `*_debug_action*` discovery
tools as dangerous, not as reads. If you must call them, save the game first,
give them a multi-minute timeout, and expect that a timeout means the game is
already gone rather than merely slow. Everything else in the safe list above
returned in 7-15ms on that same install.

WHY THIS EXISTS
===============
The bridge is only reachable while the game is up, and the token changes on
every launch, so anything hardcoded is stale within one restart. This module
scrapes the live token out of Player.log so a session never starts with a
paste-the-token step that silently uses last launch's value and then fails with
a bare "Invalid authentication token".

WIRE FORMAT (derived from the shipped assemblies, not guessed)
==============================================================
Transport is raw TCP on 127.0.0.1 with LSP-style header framing. Everything
below was read out of the metadata/#US heaps of the DLLs RimWorld actually
loaded, at
  <Workshop>/294100/3727949765/1.6/Assemblies/{Lib.GAB.dll, Gabp.Runtime.dll}

  * Lib.GAB.dll #US heap: "Content-Length: {0}", "Content-Type: application/json",
    "\r\n\r\n"  ->  headers, blank line, then a UTF-8 JSON body of exactly
    Content-Length bytes. Reader prefix literal is "Content-Length:".
  * Gabp.Runtime.dll custom-attribute blob (JsonProperty names, in declaration
    order): v, id, type, method, params, result, error  ->  the request/response
    envelope. Events use: v, id, type, channel, seq, payload.
  * Lib.GAB.dll #US heap: "gabp/1" (envelope v), "request"/"response"/"event"
    (envelope type), and the method names "session/hello", "tools/list",
    "tools/call", "events/subscribe", "events/unsubscribe", "attention/current",
    "attention/ack".
  * Gabp.Runtime.dll blob, session/hello params: token, bridgeVersion, platform,
    launchId, clientInfo{name, version, author}. Welcome result: agentId, app,
    capabilities, schemaVersion, serverInfo{name, version}.
  * tools/call params: {name, arguments}. tools/list result: {tools:[...]}.
  * Server rejects anything before the handshake with "Session not established.
    Send session/hello first." and a bad token with "Invalid authentication
    token" (Lib.GAB.dll #US heap).

Tool names are canonical GABP form ^[a-z][a-z0-9_-]*(/[a-z][a-z0-9_-]*)+$ -
"rimworld/get_game_info", never the dotted MCP adapter spelling
"rimworld.get_game_info". Lib.GAB rejects the dotted form outright.

USAGE
=====
    python rimbridge_client.py --list-tools
    python rimbridge_client.py --call rimbridge/get_bridge_status
    python rimbridge_client.py --call rimworld/search_debug_actions \
        --json '{"query": "pawn", "limit": 50}'

    from rimbridge_client import RimBridge, discover_from_log
    host, port, token = discover_from_log()
    with RimBridge(host, port, token) as rb:
        print(rb.call("rimbridge/ping"))

Host/port/token resolve in this order: CLI flag, then environment
(RIMBRIDGE_HOST / GABP_SERVER_PORT / GABP_TOKEN - the same names Lib.GAB reads),
then the newest pair scraped from Player.log, then the built-in defaults.

Dependency-free: Python 3.8+ stdlib only. Keep it that way.
"""

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import calendar
import hashlib
import json
import os
import re
import socket
import sys
import time
import uuid

import load_policy  # noqa: E402  (Utils/ is on sys.path above: the ONE deadline policy)

__all__ = ["RimBridge", "RimBridgeError", "discover_from_log", "DEFAULT_PLAYER_LOG"]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5174
DEFAULT_TOKEN = ""

# RM_GAME_LOGDIR names this machine's Player.log folder (game_paths, GAME_PATHS_REWIRE_ONE_ENV_PER_MACHINE); when it
# is set it is the ONLY place looked, so a stale log of another Windows user never hands out a dead token
# (RIMBRIDGE_LOGDIR_FIX_ENV_VAR_IGNORED). Unset keeps the old default and the WSL fallback below.
LOGDIR_FROM_ENV = bool(os.environ.get("RM_GAME_LOGDIR", "").strip())
if LOGDIR_FROM_ENV:
    from game_paths import PLAYER_LOG as DEFAULT_PLAYER_LOG  # noqa: E402
else:
    DEFAULT_PLAYER_LOG = os.path.join(
        os.path.expanduser("~"), "AppData", "LocalLow", "Ludeon Studios",
        "RimWorld by Ludeon Studios", "Player.log")

# Under WSL, expanduser("~") is /home/<user>, so DEFAULT_PLAYER_LOG points at a
# Linux path that will never exist and discovery silently finds nothing. The
# symptom is "no bridge token in Player.log - is RimWorld up?" while the token
# is sitting in the real log and the game is running perfectly.
#
# ⚠️ Finding the log does NOT make WSL work. RimBridge binds Windows loopback
# and WSL2 is NAT-mode, so the socket is refused regardless. The fallback exists
# so the error you get is the TRUE one (connection refused, wrong interpreter)
# instead of a false one that sends you looking at the game. Reported by a retired seat,
# 2026-08-12, after it cost them the hunt twice.
WSL = sys.platform.startswith("linux") and os.path.isdir("/mnt/c")

# ADHOC_BRIDGE_CALL_LOG_1: every session (connect -> close) appends one row here so
# northstar_driver/bridge_utilization.py can count ad-hoc python.exe scripts as ACTIVE
# bridge time. Outside git (a program reads it). RIMBRIDGE_SESSION_LOG overrides; "" disables.
# The default is resolved only when the variable is unset: a .get() default runs eagerly, so a caller that set it
# (a selftest with "") still died on RmDataRootUnset with no data root configured.
SESSION_LOG = (os.environ["RIMBRIDGE_SESSION_LOG"] if "RIMBRIDGE_SESSION_LOG" in os.environ
               else rm_win("scratch", "bridge_sessions.jsonl") if os.name == "nt"
               else rm_str("scratch", "bridge_sessions.jsonl"))


def _log_session(started, calls, client):
    """Best effort: a logging failure must never break a bridge script."""
    if not SESSION_LOG or started is None:
        return
    try:
        row = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
               "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "seconds": round(time.time() - started, 3), "calls": calls, "client": client,
               "script": os.path.basename(sys.argv[0]) if sys.argv else ""}
        with open(SESSION_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except Exception:
        pass


# BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN (2026-10-10): EVERY tools/call through this client - runners and
# ad-hoc scripts alike - appends a `start` row before sending and an `end` row after (ok / error / lost /
# INDETERMINATE) to a bounded JSONL. A MUTATING call (anything failing looks_read_only) also leaves an in-flight
# marker that is removed only when the bridge ANSWERS. If the reply is lost (timeout, closed socket, crash) the marker
# stays as INDETERMINATE and every later mutating call - the retry included - raises IndeterminateError until
# `python rimbridge_client.py --reconcile` records what actually happened (read the game with read-only calls
# first). Before refusing, call() runs reconcile_auto(), which settles as "moot" only what cannot matter (the game
# process is gone; a dead writer's repeat-safe tool). If the intent row cannot be written, the mutation is refused; a
# read only warns.
# Default on Windows only: the bridge is reachable only from python.exe (WSL2 is NAT-mode, so a WSL call dies at
# connect, before any tools/call), and a WSL selftest faking a lost reply must never leave a REAL marker behind.
EVIDENCE_LOG = (os.environ["RIMBRIDGE_EVIDENCE_LOG"] if "RIMBRIDGE_EVIDENCE_LOG" in os.environ   # lazy: SESSION_LOG
                else rm_win("scratch", "bridge_calls.jsonl") if os.name == "nt" else "")
EVIDENCE_MAX_BYTES = 20 * 1024 * 1024
_RUN_ID = uuid.uuid4().hex[:12]
_ACTIVE = set()                       # cids in flight in THIS process
# BRIDGE_CLIENT_HARDEN_FOUR_ROUGH_EDGES: cid -> marker record of a mutation whose outcome went UNKNOWN in THIS process
# but whose INDETERMINATE marker could not be written. The disk marker still reads "in-flight" under a live pid, which
# outstanding_indeterminate() skips, so without this set a live process could retry it. Fails closed until reconciled.
_UNRESOLVED = {}


def _settings_debt(tool, params, out):
    """AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED: every answered settings write goes on the wrap-up's debt register
    (wrapup_debt.settings_write: a change owes, a write back to the original pays), so no caller has to remember to.
    Never raises; a tool that is not a settings writer costs one tuple test."""
    if tool not in _SETTING_TOOLS:
        return
    try:
        import wrapup_debt
        wrapup_debt.settings_write(tool, params, out)
    except Exception:  # noqa: BLE001  the register never breaks a bridge call
        pass


_SETTING_TOOLS = ("jawa/mod_settings_field", "jawa/debug_settings", "jawa/difficulty_tune")   # = wrapup_debt.SETTING_TOOLS


LOAD_READY_TOOL = "rimworld/load_game_ready"
LOAD_READY_WAIT_ENV = "RIMBRIDGE_LOAD_READY_WAIT_S"
LOAD_READY_WAIT_S = 180.0     # live r8: the stuck state lasted >3 min; a healthy load reads Playing within seconds of the reply
LOAD_READY_POLL_S = 3.0


def _reply_dict(out):
    """-> (the reply as a dict, True when it came wrapped as MCP content[0].text JSON). Unparseable -> (out, False)."""
    if isinstance(out, dict) and out.get("content"):
        try:
            return json.loads(out["content"][0]["text"]), True
        except Exception:  # noqa: BLE001
            return out, False
    return out, False


def _rewrap(out, d, wrapped):
    if not wrapped:
        return d
    w = dict(out)
    w["content"] = [dict(out["content"][0], text=json.dumps(d))] + list(out["content"][1:])
    return w


def _program_state(gi):
    """programState from a get_game_info / get_ui_state reply: nested under `state` (get_game_info) or top-level."""
    if not isinstance(gi, dict):
        return None
    st = gi.get("state")
    if isinstance(st, dict) and st.get("programState"):
        return st.get("programState")
    return gi.get("programState")


class IndeterminateError(RuntimeError):
    """A previous mutating call's outcome is unknown; refusing further mutations until reconciled."""


def _ev_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _inflight_dir():
    return os.path.join(os.path.dirname(EVIDENCE_LOG) or ".", "bridge_inflight")


def _evidence(row, required=False):
    """Append one row; rotate past EVIDENCE_MAX_BYTES. required=True raises OSError instead of swallowing it."""
    if not EVIDENCE_LOG:
        return
    try:
        d = os.path.dirname(EVIDENCE_LOG)
        if d:
            os.makedirs(d, exist_ok=True)
        try:
            if os.path.getsize(EVIDENCE_LOG) > EVIDENCE_MAX_BYTES:
                os.replace(EVIDENCE_LOG, EVIDENCE_LOG + ".1")
        except OSError:
            pass
        with open(EVIDENCE_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError:
        if required:
            raise
        print("[rimbridge_client] evidence row NOT written to %s" % EVIDENCE_LOG, file=sys.stderr)


# BRIDGE_STALL_DIAGNOSTIC_1: a call that blocked this long names, on its `end` row, the stall dumps the companion's
# watchdog wrote meanwhile (stall_<session>_NN.json in the game's JawaBench\tps record dir: phase stack, tick bucket
# and its pawns' jobs, main-thread CPU). MUST equal JawaBenchStallDump.DumpSeconds (selftest_bridge_stall_client.py).
STALL_DUMP_SECONDS = 60.0


def _stall_dir():
    if os.environ.get("RIMBRIDGE_STALL_DIR"):
        return os.environ["RIMBRIDGE_STALL_DIR"]
    try:
        from game_paths import LOCALLOW
        return os.path.join(LOCALLOW, "JawaBench", "tps")
    except Exception:  # noqa: BLE001 - no game paths on this machine: the row says so
        return ""


def _stall_fields(t0, now=None):
    """{} for a call under STALL_DUMP_SECONDS; else the dumps written since it started (or why there are none)."""
    now = time.time() if now is None else now
    if now - t0 < STALL_DUMP_SECONDS:
        return {}
    d = _stall_dir()
    out = {"stall_dir": d, "stall_dumps": []}
    try:
        names = [n for n in os.listdir(d) if n.startswith("stall_") and n.endswith(".json")]
        # 2 s of slack for clock rounding; a dump written before the call began belongs to an earlier stall
        out["stall_dumps"] = sorted(n for n in names if os.path.getmtime(os.path.join(d, n)) >= t0 - 2)
        if not out["stall_dumps"]:
            out["stall_note"] = ("no stall dump since the call began: the main thread kept beating (the call itself was "
                                 "slow, or the watchdog is off), or the dir is not the game's")
    except OSError as ex:
        out["stall_note"] = "stall dir unreadable: %s" % ex
    return out


def _inflight_write(rec):
    if not EVIDENCE_LOG:
        return
    os.makedirs(_inflight_dir(), exist_ok=True)
    p = os.path.join(_inflight_dir(), "%s.json" % rec["cid"])
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh)
    os.replace(tmp, p)


def _inflight_clear(cid):
    # Windows refuses to delete a file another process holds open, and every concurrent client's
    # outstanding_indeterminate() opens every marker: one failed remove strands a marker that turns UNKNOWN once this
    # process exits and refuses every later mutating call (pass 8, 2026-10-13). Retry briefly.
    p = os.path.join(_inflight_dir(), "%s.json" % cid)
    for i in range(20):
        try:
            os.remove(p)
            return
        except FileNotFoundError:
            return
        except OSError:
            time.sleep(0.05 * (i + 1))


def _proc_start(pid):
    """A process's creation identity (Windows creation FILETIME; Linux /proc starttime ticks), or None when this OS
    or process cannot say. With the pid it names ONE process: a reused pid has another start."""
    try:
        pid = int(pid)
        if os.name == "nt":
            import ctypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x1000, False, pid)                           # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return None
            try:
                t = [ctypes.c_ulonglong() for _ in range(4)]               # creation, exit, kernel, user FILETIMEs
                if not k.GetProcessTimes(h, *[ctypes.byref(x) for x in t]):
                    return None
                return int(t[0].value)
            finally:
                k.CloseHandle(h)
        with open("/proc/%d/stat" % pid, encoding="ascii", errors="replace") as fh:
            stat = fh.read()
        return int(stat.rsplit(")", 1)[1].split()[19])                     # field 22, after comm's last ')'
    except (OSError, ValueError, IndexError, AttributeError):
        return None


def _pid_alive(pid, start=None):
    """Is the process that wrote a marker still running? `start` is its recorded _proc_start: a live pid whose start
    differs is a REUSED pid, and the writer is gone (BRIDGE_CLIENT_HARDEN_FOUR_ROUGH_EDGES). An unreadable start on a
    live pid keeps the pid-only answer (alive): a sibling's genuine in-flight call must not read as orphaned."""
    if os.name == "nt":
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))   # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        if code.value != 259:                                             # STILL_ACTIVE
            return False
    else:
        try:
            os.kill(int(pid), 0)
        except (OSError, ValueError):
            return False
    if start is None:
        return True
    now = _proc_start(pid)
    return now is None or now == start


def outstanding_indeterminate():
    """In-flight markers whose outcome is unknown: marked INDETERMINATE, or left by a process that is gone."""
    out = []
    if not EVIDENCE_LOG:
        return out
    seen = set()
    try:
        names = sorted(os.listdir(_inflight_dir()))
    except OSError:
        names = []
    for n in names:
        if not n.endswith(".json"):
            continue
        try:
            with open(os.path.join(_inflight_dir(), n), encoding="utf-8") as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            rec = {"cid": n[:-5], "status": "UNREADABLE marker"}
        if rec.get("cid") in _ACTIVE:
            continue
        if rec.get("cid") in _UNRESOLVED or rec.get("status") == "INDETERMINATE" \
                or rec.get("status") == "UNREADABLE marker" \
                or (rec.get("os") in (None, os.name)
                    and not _pid_alive(rec.get("pid") or 0, rec.get("pid_start"))):
            out.append(rec)
            seen.add(rec.get("cid"))
    # a marker this process failed to mark INDETERMINATE counts even if its file is gone or unreadable
    out.extend(r for c, r in sorted(_UNRESOLVED.items()) if c not in seen)
    return out


def _mark_indeterminate(start, error):
    """Mark a mutation's outcome UNKNOWN on disk; when that write fails, remember it in this process (_UNRESOLVED) so
    a retry here is still refused (the disk marker reads "in-flight" under our live pid, which nothing else blocks)."""
    rec = dict(start, status="INDETERMINATE", error=error)
    try:
        _inflight_write(rec)
    except OSError as ex:
        _UNRESOLVED[start["cid"]] = dict(rec, marker_write_failed=str(ex)[:200])
        print("[rimbridge_client] INDETERMINATE marker for %s NOT written (%s): refusing mutations in this process "
              "until reconciled" % (start["cid"], ex), file=sys.stderr)


def reconcile_resolve(cid, verdict, note):
    """Record what a reconcile found (applied / not-applied / partial) and clear the marker. Touches no game."""
    _evidence({"ev": "reconciled", "cid": cid, "as": verdict, "note": note, "t": _ev_now(), "pid": os.getpid()},
              required=True)
    _inflight_clear(cid)
    _UNRESOLVED.pop(cid, None)


# BRIDGE_PENDINGCALL_RECONCILE_INDETERMINATE: nothing ran the reconcile, so one lost reply (b7164851922b4797
# jawa/safe_advance from prove_sandswim.py, 2026-11-04T02:14Z) refused every later live proof (PIT_LIP A1-A3, 02:22)
# until a human resolved it an hour later. reconcile_auto() settles, as "moot", only the markers whose answer cannot
# matter, reading nothing but the OS process table and the marker itself (no bridge call, no game write):
#   1 the game process the call went to is gone: no RimWorld runs, or the one running started after the call;
#   2 its writer process is gone AND the tool is REPEAT_SAFE: applying it again changes nothing a caller relied on.
# Everything else (a live writer, an unreadable marker, a non-repeat-safe tool in the same game, a marker this
# process failed to write) still refuses, and --reconcile lists it for a human-read verdict.
REPEAT_SAFE_TOOLS = {
    "rimworld/pause_game": "sets the pause flag to a value: a second set is the same state",
    "rimworld/set_time_speed": "sets the speed to a value: a second set is the same state",
    "jawa/weather_set": "sets the weather to a value: a second set is the same state",
    "jawa/safe_advance": "advances the clock: a later caller reads the clock it finds, it never relied on this one",
}
GAME_PROCESS = "RimWorldWin64.exe"
_FILETIME_EPOCH = 116444736000000000           # 1601-01-01 to 1970-01-01, in 100 ns ticks
GAME_START_SLACK_S = 2.0                       # marker `t` is whole seconds; the game's start is exact


def _iso_epoch(t):
    try:
        return calendar.timegm(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None


def game_starts():
    """Start times (epoch s) of every running RimWorld, [] when none runs, None when this OS cannot say. Windows only:
    the markers and the game both live there; from WSL the answer is None (never [] - that would read as 'gone')."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class PE(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]
        k = ctypes.windll.kernel32
        k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        snap = k.CreateToolhelp32Snapshot(0x2, 0)                      # TH32CS_SNAPPROCESS
        if not snap or snap == wintypes.HANDLE(-1).value:
            return None
        out = []
        try:
            e = PE()
            e.dwSize = ctypes.sizeof(PE)
            ok = k.Process32FirstW(snap, ctypes.byref(e))
            while ok:
                if e.szExeFile.lower() == GAME_PROCESS.lower():
                    ft = _proc_start(e.th32ProcessID)
                    if ft is None:
                        return None                                    # a game we cannot date: say nothing
                    out.append((ft - _FILETIME_EPOCH) / 1e7)
                ok = k.Process32NextW(snap, ctypes.byref(e))
        finally:
            k.CloseHandle(snap)
        return out
    except (OSError, AttributeError, ValueError):
        return None


def _moot_why(rec, starts):
    """Why this marker's outcome cannot matter any more, or None when it still might."""
    cid = rec.get("cid")
    if cid in _ACTIVE or cid in _UNRESOLVED or rec.get("status") == "UNREADABLE marker":
        return None
    t = _iso_epoch(rec.get("t"))
    if starts is not None and t is not None:
        if not starts:
            return "the game process it went to is gone: no %s runs" % GAME_PROCESS
        if all(s > t + GAME_START_SLACK_S for s in starts):
            return ("the game process it went to is gone: the running %s started %s, after the call"
                    % (GAME_PROCESS, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(max(starts)))))
    tool = rec.get("tool")
    if tool in REPEAT_SAFE_TOOLS and rec.get("os") in (None, os.name) \
            and not _pid_alive(rec.get("pid") or 0, rec.get("pid_start")):
        return "its writer (pid %s, %s) is gone and %s is repeat-safe: %s" % (
            rec.get("pid"), rec.get("script"), tool, REPEAT_SAFE_TOOLS[tool])
    return None


def reconcile_auto(starts=None):
    """Settle every outstanding marker whose outcome cannot matter (see REPEAT_SAFE_TOOLS); return (settled, left).
    Read-only towards the game. `starts` overrides game_starts() (tests)."""
    pend = outstanding_indeterminate()
    if not pend:
        return [], []
    if starts is None:
        starts = game_starts()
    settled, left = [], []
    for rec in pend:
        why = _moot_why(rec, starts)
        if why is None:
            left.append(rec)
            continue
        try:
            reconcile_resolve(rec["cid"], "moot", "auto-reconcile (%s %s): %s" % (rec.get("tool"), rec.get("t"), why))
        except OSError as ex:
            print("[rimbridge_client] auto-reconcile of %s NOT recorded (%s)" % (rec.get("cid"), ex), file=sys.stderr)
            left.append(rec)
            continue
        print("[rimbridge_client] auto-reconciled %s %s as moot: %s" % (rec.get("cid"), rec.get("tool"), why),
              file=sys.stderr)
        settled.append(dict(rec, moot=why))
    return settled, left


def _args_sha(params):
    return hashlib.sha256(json.dumps(params or {}, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def _player_log_candidates():
    """Every place Player.log might be, best first."""
    yield DEFAULT_PLAYER_LOG
    if WSL and not LOGDIR_FROM_ENV:
        import glob
        for base in sorted(glob.glob("/mnt/c/Users/*/AppData/LocalLow/"
                                     "Ludeon Studios/RimWorld by Ludeon Studios")):
            yield os.path.join(base, "Player.log")

GABP_VERSION = "gabp/1"
BRIDGE_VERSION = "1.0"

# Anything not on this list is assumed to mutate the game until proven otherwise.
READ_ONLY_PREFIXES = ("list_", "get_", "search_", "find_", "compile_", "ping")
# Reads the prefixes cannot see. companion_handshake only reports the companion's profile; treated as mutating it was
# refused whenever any earlier call had an UNKNOWN outcome (testq: 4 jobs INVALID/HARNESS 10-27..10-29), so the
# harness could not even read the state it needed to reconcile.
# running_mods only lists LoadedModManager's running mods (and hashes an assembly file when asked); without this entry
# live_def_check's owner lookup was refused on every call (exit 3) and every unresolved def read UNMEASURED (2026-11-02).
# map_info, thing_graphic and thing_explain are READ ONLY by their C# [Tool] descriptions (JawaBenchMapInfoTools,
# JawaBenchNorthstarTools, JawaBenchAwarenessTools); refused here, GELATINOUSSLIME_KIT_ART_1's live proof read
# UNMEASURED (exit 3, 2026-11-03) and no live proof could read the map without --yes-i-know-this-is-live.
READ_ONLY_TOOLS = ("jawa/companion_handshake", "jawa/running_mods", "jawa/map_info", "jawa/thing_graphic",
                   "jawa/thing_explain")
# jawa/static_call runs ANY static method, so it is mutating by default. These (type, method) pairs are reviewed getters:
# a caller that declares its call read-only (CLI --read-only-static, live_def_check._bridge(read_only_static=True)) passes
# the guard for these and only these. TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING's readback was refused as not read-only on
# every relentless live run (RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED). Add a pair only after reading its source.
READ_ONLY_STATIC_CALLS = frozenset((
    ("AlienWorlds.PlanetTypeManager", "get_Current"),             # a property getter
    ("HarmonyLib.Harmony", "HasAnyPatches"),                      # Harmony's own query: a dictionary read
    ("Worldbuilder.World_ExposeData_Patch", "get_WorldPresetName"),   # a static property getter
    ("RimMandrake.Biomes.RM_WorldDecals", "Info"),                # builds a string from statics
    ("RimMandrake.Biomes.RM_WorldDecals", "Probe"),               # ContentFinder lookup, no cache, no build
    ("RimMandrake.Biomes.RM_BiomesSettings", "Enabled"),          # a dictionary TryGetValue
    ("RimMandrake.Pyrelands.PyrelandsMechanicsGate", "get_ShellPresent"),   # a null test on a cached delegate
    ("RimMandrake.Pyrelands.PyrelandsMechanicsGate", "get_ShellOn"),        # the delegate above, i.e. Enabled
    ("RimMandrake.Pyrelands.PyrelandsMechanicsGate", "get_On"),             # pure RM_FireEcoKernel.MechanicsOn
))


def read_only_static(params):
    """-> None when this jawa/static_call is a reviewed read (READ_ONLY_STATIC_CALLS), else why it is not."""
    p = params if isinstance(params, dict) else {}
    pair = (p.get("type"), p.get("method"))
    return None if pair in READ_ONLY_STATIC_CALLS else "%s.%s is not a reviewed read-only static call" % pair

# Tools the owner has RETIRED. The bridge still registers them; we refuse to be the
# thing that calls one. A doc saying "don't" is read by whoever already looked it up;
# this is read by whoever didn't.
RETIRED_TOOLS = {
    "jawa/hot_reload_defs": (
        "RETIRED by the owner on 2026-09-03 as unstable.\n"
        "  Measured on the 589-mod list: it hung the bridge ~5 minutes, then left the\n"
        "  game unable to generate ANY pawn - jawa/spawn_pawn NRE'd on Muffalo, Hare,\n"
        "  Colonist, Tribesperson and Villager alike, and vanilla's own debug spawn\n"
        "  named it: \"The given key 'RimWorld.HairDef' was not present in the\n"
        "  dictionary\". Every health flag read green throughout.\n"
        "  DO INSTEAD: deploy the XML and restart on the 19-mod minimal list - 22\n"
        "  seconds - then read the field back with jawa/get_defs.\n"
        "  Ruling: skills/rimworld-modding/SKILL.md #2.\n"
        "  Evidence: infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md\n"
        "  To run the sanctioned re-test (MINIMAL LIST ONLY, where a broken game costs\n"
        "  22 s): set RIMBRIDGE_ALLOW_RETIRED=jawa/hot_reload_defs in the environment."
    ),
}


def _retired(tool):
    """The refusal text for a retired tool, or None. Honours the explicit override."""
    why = RETIRED_TOOLS.get(tool)
    if why is None:
        return None
    allowed = os.environ.get("RIMBRIDGE_ALLOW_RETIRED", "")
    if tool in [t.strip() for t in allowed.split(",") if t.strip()]:
        return None
    return why


class RimBridgeError(RuntimeError):
    """A GABP-level failure: bad handshake, transport break, or tool error."""


class RetiredToolError(RimBridgeError):
    """The tool exists on the bridge and the owner has retired it. See RETIRED_TOOLS."""


# MODCHECK_DRIVERS_HARDEN_OWN_TIMEOUT_MIDCALL: a process that will be hard-killed at a known time (modcheck drivers.py
# sets this to the epoch second of its subprocess timeout) gets no NEW mutating call that could still be in flight
# then: a kill mid call strands an UNKNOWN-outcome marker that refuses every later mutation of the run.
DEADLINE_ENV = "RIMBRIDGE_CALL_DEADLINE"
DEADLINE_MARGIN_S = 10.0       # kept clear between a clamped call's own timeout and the kill
DEADLINE_MIN_CALL_S = 30.0     # less room than this refuses the mutation (DeadlineError) instead of clamping it


class DeadlineError(RimBridgeError):
    """A mutating call refused before it started: it might not finish before RIMBRIDGE_CALL_DEADLINE."""


def _deadline_left():
    """Seconds until RIMBRIDGE_CALL_DEADLINE: None only when UNSET. A set value that is unparseable or NaN reads as
    already expired (-inf): the process may still be killed at a time it cannot read, so a mutation fails closed
    (RIMBRIDGE_DEADLINE_FIX_NAN_FAILS_OPEN -- 'nan' compared False and let every mutation run). 'inf' is no limit."""
    raw = os.environ.get(DEADLINE_ENV)
    if raw is None:
        return None
    try:
        at = float(raw)
    except ValueError:
        return float("-inf")
    if at != at:   # NaN
        return float("-inf")
    return at - time.time()


class DriverHeldError(RimBridgeError):
    """A mutating call on this machine's game while another live process holds the driver lock."""


CROSS_ENV = "RM_BRIDGE_CROSS_WHY"       # a deliberate crossing: the reason, recorded on the call's evidence row
_LOOPBACK = ("127.0.0.1", "localhost", "::1")


def _driver_crossing(host):
    """The holder's refusal text if a mutation here would cross him, else None. Only this machine's game: the lock
    file is this machine's. The guard lives next door in rimflow; a client copied without it says so and goes on."""
    if host not in _LOOPBACK:
        return None
    try:
        rimflow_dir = str(_rm_pl.Path(__file__).resolve().parents[1] / "rimflow")
        if rimflow_dir not in sys.path:
            sys.path.append(rimflow_dir)
        import host_guard
        return host_guard.crossing()
    except Exception as ex:
        print("[rimbridge_client] driver lock not checked: %s" % ex, file=sys.stderr)
        return None


class UnknownParameterError(RimBridgeError):
    """A tool was called with an argument key its schema does not declare.

    BRIDGE_DROPS_UNKNOWN_PARAMS_1, proven live 2026-08-26: the bridge DISCARDS a
    key it does not know, silently, and runs the tool on its defaults.

        jawa/new_allowed_area {label: "CHECK_correct"}           -> label "CHECK_correct"
        jawa/new_allowed_area {name:  "CHECK_wrong", banana: 42} -> label "Area 3"   success:true
        jawa/time_clock       {zzz: "nonsense"}                  -> full correct payload

    ⛔ The server is not ours and cannot be changed. This is the CLIENT-side guard,
    and it turns each of those into a loud local failure before a byte is sent.
    """


# --------------------------------------------------------------------------
# token discovery
# --------------------------------------------------------------------------

_PORT_RE = re.compile(r"\[RimBridge\].*?on port\s+(\d+)")
_TOKEN_RE = re.compile(r"\[RimBridge\]\s*Bridge token:\s*([0-9A-Za-z._\-]+)")


def discover_from_log(path=None):
    """Scrape the NEWEST '[RimBridge] ... on port N' / 'Bridge token: X' pair.

    Returns (host, port, token); port/token are None if the log has no bridge
    lines. Last match wins on purpose - Player.log is append-only across
    restarts, so the first match is usually a dead session from hours ago.
    """
    paths = [path] if path else list(_player_log_candidates())
    port = token = None
    for candidate in paths:
        port = token = None
        try:
            with open(candidate, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "[RimBridge]" not in line:
                        continue
                    m = _PORT_RE.search(line)
                    if m:
                        port = int(m.group(1))
                    m = _TOKEN_RE.search(line)
                    if m:
                        token = m.group(1)
        except OSError:
            continue
        if token:
            break
    if token is None and port is None:
        return DEFAULT_HOST, None, None
    return DEFAULT_HOST, port, token


def resolve_endpoint(host=None, port=None, token=None, log_path=None):
    """CLI arg > env > Player.log > module default, per field independently."""
    log_host = log_port = log_token = None
    if host is None or port is None or token is None:
        log_host, log_port, log_token = discover_from_log(log_path)

    host = host or os.environ.get("RIMBRIDGE_HOST") or log_host or DEFAULT_HOST
    if port is None:
        env_port = os.environ.get("GABP_SERVER_PORT")
        port = int(env_port) if env_port else (log_port or DEFAULT_PORT)
    token = token or os.environ.get("GABP_TOKEN") or log_token or DEFAULT_TOKEN
    return host, int(port), token


# --------------------------------------------------------------------------
# the bridge
# --------------------------------------------------------------------------

class RimBridge:
    """One GABP session over one TCP socket.

    Not thread-safe and not meant to be: the bridge serialises onto RimWorld's
    main thread anyway, so a second concurrent caller buys nothing but
    interleaved frames.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, token="",
                 timeout=30.0, connect_timeout=5.0, client_name="rimbridge_client.py"):
        self.host = host
        self.port = int(port)
        self.token = token or ""
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.client_name = client_name
        self.sock = None
        self.buf = b""
        # tool name -> set of declared argument keys. Populated lazily on the first
        # guarded call; None until then, and a tool absent from it is UNCHECKED,
        # never "has no parameters". See _declared_params.
        self._param_index = None
        self.welcome = None
        self.events = []          # unsolicited event envelopes seen while reading
        self._session_started = None
        self._session_calls = 0

    # -- lifecycle ---------------------------------------------------------

    def connect(self):
        """Open the socket and complete session/hello. Raises on refusal."""
        try:
            self.sock = socket.create_connection((self.host, self.port),
                                                 timeout=self.connect_timeout)
        except OSError as ex:
            # Under WSL this is never "the game is down" -- RimBridge binds
            # Windows loopback and WSL2 is NAT-mode, so there is no route at
            # all. Saying "is RimWorld running?" here sends the reader to check
            # a game that is running fine. Name the real cause instead.
            if WSL:
                raise RimBridgeError(
                    "cannot reach the bridge from WSL, and no amount of "
                    "retrying will fix it.\n"
                    "  RimBridge binds Windows loopback; WSL2 is NAT-mode, so "
                    "%s:%s has no route from here.\n"
                    "  This says NOTHING about whether RimWorld is running.\n"
                    "  Re-run under Windows Python:  python.exe %s"
                    % (self.host, self.port,
                       " ".join(sys.argv) or "<your script>")) from ex
            raise RimBridgeError(
                "cannot reach the bridge at %s:%s (%s) - is RimWorld running "
                "with RimBridgeServer enabled?" % (self.host, self.port, ex)) from ex
        self.sock.settimeout(self.timeout)
        self.welcome = self._hello()
        self._session_started = time.time()
        self._session_calls = 0
        return self

    def close(self):
        if self._session_started is not None:
            _log_session(self._session_started, self._session_calls, self.client_name)
            self._session_started = None
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def __enter__(self):
        if self.sock is None:
            self.connect()
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    # -- framing -----------------------------------------------------------

    # BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY: a request's limit is ONE absolute monotonic instant
    # (load_policy.Deadline, set in _request); every blocking read gets only the time left, so an event flood or a
    # byte trickle can no longer reset a per-read timeout and stretch a call forever (GPT N04). A timeout mid-frame
    # KEEPS self.buf (parser state preserved, never re-parsed from mid-frame; the late reply is dropped as
    # abandoned). A frame that cannot be parsed (bad/negative/oversize Content-Length, runaway header, bad JSON)
    # CLOSES the connection: the stream position is unknowable, so the operation is indeterminate, never guessed.
    MAX_HEADER_BYTES = 8192
    MAX_FRAME_BYTES = 256 * 1024 * 1024

    def _send(self, envelope):
        if self.sock is None:
            raise RimBridgeError("bridge connection is closed (an earlier malformed frame or EOF); reconnect")
        body = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
        head = ("Content-Length: %d\r\nContent-Type: application/json\r\n\r\n"
                % len(body)).encode("ascii")
        self.sock.sendall(head + body)

    def _malformed(self, why):
        snippet = self.buf[:120]
        self.close()
        self.buf = b""
        raise RimBridgeError("malformed bridge frame (%s): %r; connection closed, any call in flight is INDETERMINATE"
                             % (why, snippet))

    def _recv_raw(self):
        """Read exactly one framed JSON message. Tolerates LF-only headers."""
        while True:
            i_crlf, i_lf = self.buf.find(b"\r\n\r\n"), self.buf.find(b"\n\n")
            if i_crlf >= 0 or i_lf >= 0:
                break
            if len(self.buf) > self.MAX_HEADER_BYTES:
                self._malformed("no header end within %d bytes" % self.MAX_HEADER_BYTES)
            self._fill()
        # the EARLIER separator ends this header: a later CRLF pair belongs to the body or the next frame
        sep = b"\n\n" if i_crlf < 0 or (0 <= i_lf < i_crlf) else b"\r\n\r\n"
        head = self.buf.partition(sep)[0]
        length = None
        for line in head.decode("ascii", "replace").splitlines():
            if line.lower().startswith("content-length:"):
                raw = line.split(":", 1)[1].strip()
                if not raw.isdigit():
                    self._malformed("Content-Length %r" % raw)
                length = int(raw)
        if length is None:
            self._malformed("no Content-Length header")
        if length > self.MAX_FRAME_BYTES:
            self._malformed("Content-Length %d over the %d cap" % (length, self.MAX_FRAME_BYTES))
        start = len(head) + len(sep)          # self.buf is consumed only once the whole frame is here
        while len(self.buf) < start + length:
            self._fill()
        body, self.buf = self.buf[start:start + length], self.buf[start + length:]
        try:
            return json.loads(body.decode("utf-8"))
        except ValueError as ex:
            self._malformed("body is not UTF-8 JSON: %s" % ex)

    def _fill(self):
        dl = getattr(self, "_deadline", None)
        if dl is not None:
            left = dl.remaining()
            if left <= 0:
                self._timed_out(dl)
            self.sock.settimeout(left)
        else:
            self.sock.settimeout(self.timeout)
        try:
            chunk = self.sock.recv(65536)
        except socket.timeout as ex:
            if dl is not None:
                self._timed_out(dl, ex)
            raise RimBridgeError(
                "timed out after %ss waiting for the bridge; RimWorld may be in a "
                "long event or the call may be frame-bound" % self.timeout) from ex
        if not chunk:
            self.close()
            raise RimBridgeError("bridge closed the connection")
        self.buf += chunk

    def _timed_out(self, dl, cause=None):
        """The absolute call deadline passed. The message starts 'timed out' (call() and _request key on it) and
        states whether the game process is alive; nothing is killed."""
        n_ev = len(self.events) - getattr(self, "_events_at_send", len(self.events))
        msg = ("timed out: %s (%d event(s) arrived meanwhile; RimWorld may be in a long event or the call may be "
               "frame-bound)" % (load_policy.deadline_exceeded("bridge request", dl.elapsed(), dl.limit_s,
                                                                 alive=self._alive_probe()), n_ev))
        raise RimBridgeError(msg) from cause

    def _alive_probe(self):
        """Game liveness for a deadline message. RIMBRIDGE_ALIVE_PROBE=off reads UNKNOWN without asking (tests)."""
        if os.environ.get("RIMBRIDGE_ALIVE_PROBE") == "off":
            return None
        return load_policy.game_alive()

    def _recv_response(self, want_id):
        """Read until the response with our id arrives; park events aside."""
        while True:
            msg = self._recv_raw()
            if msg.get("type") == "event":
                self.events.append(msg)
                continue
            if msg.get("id") == want_id or want_id is None:
                return msg
            if msg.get("id") in getattr(self, "abandoned", ()):
                # The late answer to a request this client already gave up on (timed out). MEASURED live 2026-10-01:
                # FlowWorks' heavy flood ticks outran the call timeout, and the late reply then made every LATER call
                # in the run die with "unexpected response id". It belongs to nobody; drop it.
                self.abandoned.discard(msg.get("id"))
                continue
            # A response for some other id means the stream desynced.
            raise RimBridgeError("unexpected response id %r (wanted %r)"
                                 % (msg.get("id"), want_id))

    def _request(self, method, params=None):
        rid = str(uuid.uuid4())
        # fixed now; nothing arriving later moves it (timeout None = block, as socket.settimeout(None) always did)
        self._deadline = load_policy.Deadline(self.timeout) if self.timeout is not None else None
        self._events_at_send = len(self.events)
        self._send({
            "v": GABP_VERSION,
            "id": rid,
            "type": "request",
            "method": method,
            "params": params or {},
        })
        try:
            msg = self._recv_response(rid)
        except RimBridgeError as ex:
            if str(ex).startswith("timed out"):
                if not hasattr(self, "abandoned"):
                    self.abandoned = set()
                self.abandoned.add(rid)
            raise
        finally:
            self._deadline = None
        err = msg.get("error")
        if err:
            raise RimBridgeError("%s failed: %s" % (
                method, err.get("message") if isinstance(err, dict) else err))
        return msg.get("result")

    # -- handshake ---------------------------------------------------------

    def _hello(self):
        params = {
            "token": self.token,
            "bridgeVersion": BRIDGE_VERSION,
            "platform": sys.platform,
            "clientInfo": {
                "name": self.client_name,
                "version": "1.0.0",
                "author": "rimworld-project",
            },
        }
        try:
            return self._request("session/hello", params)
        except RimBridgeError as ex:
            if "Invalid session/hello parameters" not in str(ex):
                raise
            # Fall back to the minimum the server documents as required.
            return self._request("session/hello", {"token": self.token})

    # -- public API --------------------------------------------------------

    def list_tools(self):
        """tools/list -> the live tool descriptors. Never mutates."""
        result = self._request("tools/list") or {}
        return result.get("tools", [])

    # --- the unknown-parameter guard --------------------------------------
    #
    # The descriptor key holding a tool's schema is not something this client can
    # know offline, and guessing one and finding nothing would make the guard pass
    # everything - the exact failure it exists to prevent. So it tries the
    # candidates in order and, when none of them yields keys, says UNCHECKED out
    # loud rather than returning a clean answer.
    _SCHEMA_KEYS = ("inputSchema", "input_schema", "parameters", "schema", "arguments")

    @staticmethod
    def _declared_params(descriptor):
        """The argument keys a tool descriptor declares, or None if UNMEASURABLE.

        ⛔ Returns None - NOT an empty set - when no schema can be found. An empty
        set would read as "this tool takes no arguments" and reject every correct
        call; None means "this client could not look", and the caller warns.
        """
        if not isinstance(descriptor, dict):
            return None
        for key in RimBridge._SCHEMA_KEYS:
            node = descriptor.get(key)
            if isinstance(node, dict):
                props = node.get("properties")
                if isinstance(props, dict):
                    # An EMPTY dict is a real, common shape (51/432 live tools,
                    # rimworld/get_game_info among them) meaning "declares zero
                    # params" - not "no schema found". The old `and props` here
                    # made every such tool read UNCHECKED, silently disabling the
                    # unknown-parameter guard on exactly the tools where a typo'd
                    # key is most likely: one that takes no real arguments at all.
                    return set(props.keys())
                if node and "properties" not in node and all(isinstance(k, str) for k in node):
                    # a bare {name: spec} map rather than a JSON-Schema object
                    return set(node.keys())
        return None

    def _param_map(self):
        if self._param_index is None:
            index = {}
            for d in self.list_tools():
                name = d.get("name") if isinstance(d, dict) else None
                if name:
                    index[name] = self._declared_params(d)
            self._param_index = index
        return self._param_index

    def check_params(self, tool, params):
        """Raise UnknownParameterError for any key the tool does not declare.

        Returns a one-line reason string when the check could NOT be made, and None
        when it passed. A caller that ignores the return value still gets the raise.
        """
        if not params:
            return None
        try:
            declared = self._param_map().get(tool, "missing")
        except Exception as exc:                      # a tools/list failure must not
            return "UNCHECKED: tools/list failed (%s)" % exc   # break the call itself
        if declared == "missing":
            return "UNCHECKED: %s is not in tools/list" % tool
        if declared is None:
            return "UNCHECKED: no readable schema on %s" % tool
        unknown = sorted(k for k in params if k not in declared)
        if unknown:
            raise UnknownParameterError(
                "%s does not declare %s. The bridge would DISCARD %s silently and run "
                "on its defaults, returning success. Declared: %s"
                % (tool, ", ".join(unknown),
                   "them" if len(unknown) > 1 else "it",
                   ", ".join(sorted(declared)) or "(none)"))
        return None

    def call(self, tool, params=None, check=True):
        """tools/call. NOTHING here stops you calling a destructive tool.

        🔑 It DOES stop you calling one with a misspelled argument: `check` runs the
        unknown-parameter guard first (BRIDGE_DROPS_UNKNOWN_PARAMS_1). Pass
        check=False only when you mean to send a key the schema does not declare.
        """
        why = _retired(tool)
        if why is not None:
            raise RetiredToolError("%s is RETIRED - refusing to call it.\n  %s" % (tool, why))
        if check:
            unchecked = self.check_params(tool, params)
            if unchecked:
                print("[rimbridge_client] %s -> %s" % (tool, unchecked), file=sys.stderr)
        mutating = not self.looks_read_only(tool, params)
        crossed = None
        clamp = None
        if mutating:
            crossed = _driver_crossing(self.host)
            if crossed and not os.environ.get(CROSS_ENV):
                raise DriverHeldError("refusing %s: %s. Wait for `rimflow bridge who` to read free, or take the bridge; "
                                      "to cross him on purpose set %s=<why>" % (tool, crossed, CROSS_ENV))
            left = _deadline_left()
            if left is not None and left < self.timeout + self.connect_timeout + DEADLINE_MARGIN_S:
                # TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD: the call's timeout is CLAMPED to the room left, and only a
                # room under DEADLINE_MIN_CALL_S refuses. Refusing whenever the room was under the full timeout made
                # a driver whose kill time is within one call timeout of its start (sprinkler_live: 600 s driver,
                # 600 s calls) refuse its FIRST mutation on every testq run, and cost every driver its last ten
                # minutes (thirst_live: the settings restore refused at 1195 s of 1800). A clamped call that does
                # time out leaves the same INDETERMINATE marker the kill would have; one that answers, as most do in
                # seconds, leaves none.
                room = left - self.connect_timeout - DEADLINE_MARGIN_S
                if room < DEADLINE_MIN_CALL_S:
                    raise DeadlineError("refusing %s: %.0f s to %s (=%r), under the %.0f s minimum call room after "
                                        "%.0f s connect + %.0f s margin: a kill mid call would strand an "
                                        "UNKNOWN-outcome marker"
                                        % (tool, max(left, 0), DEADLINE_ENV, os.environ.get(DEADLINE_ENV),
                                           DEADLINE_MIN_CALL_S, self.connect_timeout, DEADLINE_MARGIN_S))
                clamp = room
            pending = outstanding_indeterminate()
            if pending:
                pending = reconcile_auto()[1]
            if pending:
                raise IndeterminateError(
                    "refusing %s: %d earlier mutating call(s) have an UNKNOWN outcome (%s). A retry could apply it "
                    "twice. Read the game with read-only calls, then record the answer:\n  python "
                    "rimbridge_client.py --reconcile [--resolve CID --as applied|not-applied|partial --note \"...\"]"
                    % (tool, len(pending), ", ".join("%s %s" % (p.get("cid"), p.get("tool")) for p in pending[:3])))
        cid = uuid.uuid4().hex[:16]
        start = {"ev": "start", "cid": cid, "run": _RUN_ID, "t": _ev_now(), "tool": tool,
                 "args_sha256": _args_sha(params), "mutating": mutating, "pid": os.getpid(), "os": os.name,
                 "pid_start": _proc_start(os.getpid()),
                 "seat": os.environ.get("RIMFLOW_SEAT") or os.environ.get("AGENT_SEAT"),
                 "script": os.path.basename(sys.argv[0]) if sys.argv else "", "client": self.client_name,
                 "endpoint": "%s:%s" % (self.host, self.port)}
        if crossed:
            start["crossed_holder"] = "%s: %s" % (os.environ[CROSS_ENV], crossed)
        try:
            _evidence(start, required=mutating)
            if mutating:
                _inflight_write(dict(start, status="in-flight"))
        except OSError as ex:
            raise RimBridgeError("refusing mutating call %s: its evidence (intent) could not be recorded at %s "
                                 "(%s)" % (tool, EVIDENCE_LOG, ex))
        _ACTIVE.add(cid)
        t0 = time.time()
        self._session_calls += 1
        full = self.timeout
        try:
            if clamp is not None:
                self._set_call_timeout(clamp)
            out = self._request("tools/call", {"name": tool, "arguments": params or {}})
        except RimBridgeError as ex:
            answered = " failed: " in str(ex)          # the server replied with an error: outcome known
            status = "error" if answered else ("INDETERMINATE" if mutating else "lost")
            timed_out = "timed out" in str(ex).lower()
            # outcome/transport/timeout folded in from the retired rimdrive.obs_events (design 08 P5)
            outcome = "error" if answered else ("timeout" if timed_out else "lost")
            _evidence(dict({"ev": "end", "cid": cid, "status": status, "ms": int((time.time() - t0) * 1000),
                            "error": str(ex)[:300], "t": _ev_now(), "outcome": outcome, "timeout": timed_out,
                            "transport": "ok" if answered else outcome}, **_stall_fields(t0)))
            if mutating and status == "INDETERMINATE":
                _mark_indeterminate(start, str(ex)[:300])
            else:
                _inflight_clear(cid)
            _ACTIVE.discard(cid)
            raise
        except BaseException as ex:
            _ACTIVE.discard(cid)                      # KeyboardInterrupt etc: marker stays, read as orphaned
            # Name the exception: a bare "client interrupted" left testq J20261026T182927Z-c2508c's set_fog death
            # (an OSError/ValueError escaping the socket read <1 s after the send, game alive) undiagnosable.
            why = "client interrupted: %s: %s" % (type(ex).__name__, str(ex)[:240])
            try:
                _evidence(dict({"ev": "end", "cid": cid, "status": "INDETERMINATE" if mutating else "lost",
                                "ms": int((time.time() - t0) * 1000), "error": why, "t": _ev_now(),
                                "outcome": "lost", "timeout": False, "transport": type(ex).__name__}, **_stall_fields(t0)))
            except Exception:  # noqa: BLE001 - evidence is best effort here; the original exception must propagate
                pass
            if mutating:
                _mark_indeterminate(start, why)
            raise
        finally:
            if clamp is not None:
                self._set_call_timeout(full)
        ok_success = out.get("success") if isinstance(out, dict) else None
        _evidence(dict({"ev": "end", "cid": cid, "status": "ok", "ms": int((time.time() - t0) * 1000), "t": _ev_now(),
                        "success": ok_success, "outcome": "reply_fail" if ok_success is False else "ok",
                        "timeout": False, "transport": "ok"}, **_stall_fields(t0)))
        _inflight_clear(cid)
        _ACTIVE.discard(cid)
        _settings_debt(tool, params, out)
        if tool == LOAD_READY_TOOL:
            out = self._settle_load_ready(params, out)
        return out

    def _settle_load_ready(self, params, out, sleep=time.sleep, clock=time.time):
        """BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING (live r8, 2026-10-26): the first load_game_ready after a cold launch
        answered success / game_loaded while programState stayed MapInitializing for minutes (a SmashTools
        DetachedMapComponentCache duplicate key thrown in Map.FinalizeLoading), so every later tick was refused. A success
        reply is therefore held until get_game_info reads programState Playing; one that never gets there within
        LOAD_READY_WAIT_S (env RIMBRIDGE_LOAD_READY_WAIT_S, capped by the call deadline) comes back success False with
        `stuckProgramState`. An explicit readiness other than "playable" (e.g. "mapData", asked for mid-load on purpose) is
        passed through untouched, as is a failure reply."""
        readiness = (params or {}).get("readiness")
        if readiness not in (None, "", "playable"):
            return out
        d, wrapped = _reply_dict(out)
        if not isinstance(d, dict) or d.get("success") is not True:
            return out
        try:
            budget = float(os.environ.get(LOAD_READY_WAIT_ENV) or LOAD_READY_WAIT_S)
        except ValueError:
            budget = LOAD_READY_WAIT_S
        left = _deadline_left()
        if left is not None:
            budget = max(0.0, min(budget, left - self.connect_timeout - DEADLINE_MARGIN_S))
        t0 = clock()
        st, err = None, None
        while True:
            try:
                gi, _ = _reply_dict(self.call("rimworld/get_game_info", check=False))
                st = _program_state(gi)
                err = None
            except RimBridgeError as ex:          # a main thread busy finishing the load may not answer: keep waiting
                st, err = None, str(ex)[:200]
            if st == "Playing":
                d["programStateAfter"] = "Playing"
                d["settledSeconds"] = round(clock() - t0, 1)
                return _rewrap(out, d, wrapped)
            if clock() - t0 >= budget:
                break
            sleep(LOAD_READY_POLL_S)
        d["loadReplySuccess"] = True
        d["success"] = False
        d["stuckProgramState"] = st
        d["error"] = ("load_game_ready answered success but programState stayed %s for %.0f s (not Playing; %s). Read the "
                      "FIRST exception in Player.log; go_to_main_menu and load again cleared it in live r8 "
                      "(BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING)" % (st, clock() - t0, err or "get_game_info answered"))
        return _rewrap(out, d, wrapped)

    def _set_call_timeout(self, seconds):
        """This connection's per-read timeout: `self.timeout` and the open socket's (a deadline-clamped call sets it,
        then puts the full timeout back)."""
        self.timeout = seconds
        if self.sock is not None:
            self.sock.settimeout(seconds)

    def looks_read_only(self, tool, params=None):
        """Cheap heuristic only - a False here is a warning, a True is not a promise. A jawa/static_call is a read only
        when this client was told so (static_reads, the --read-only-static declaration) AND it is a reviewed pair."""
        leaf = tool.split("/", 1)[-1]
        if tool == "jawa/static_call" and getattr(self, "static_reads", False):
            return read_only_static(params) is None
        return leaf.startswith(READ_ONLY_PREFIXES) or tool in READ_ONLY_TOOLS


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="Query a live RimWorld through the RimBridgeServer GABP bridge.")
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--token")
    ap.add_argument("--log", dest="log_path", help="Player.log to scrape for port/token")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--list-tools", action="store_true")
    ap.add_argument("--call", metavar="TOOL")
    ap.add_argument("--json", dest="params", default="{}",
                    help="JSON object of tool arguments")
    ap.add_argument("--raw", action="store_true", help="dump the full envelope result")
    ap.add_argument("--yes-i-know-this-is-live", action="store_true",
                    help="required to call a tool that fails the read-only heuristic")
    ap.add_argument("--read-only-static", action="store_true",
                    help="declare a jawa/static_call a read; accepted only for READ_ONLY_STATIC_CALLS")
    ap.add_argument("--reconcile", action="store_true",
                    help="list mutating calls with an UNKNOWN outcome (touches no game); with --resolve, record one")
    ap.add_argument("--auto", action="store_true",
                    help="with --reconcile: first settle as moot what cannot matter (game gone; dead writer of a "
                         "repeat-safe tool), reading only the process table")
    ap.add_argument("--resolve", metavar="CID")
    ap.add_argument("--as", dest="verdict", choices=("applied", "not-applied", "partial", "moot"))
    ap.add_argument("--note", default="")
    args = ap.parse_args(argv)

    if args.reconcile:
        if args.resolve:
            if not args.verdict or not args.note:
                print("--resolve needs --as and a --note saying what you read to decide", file=sys.stderr)
                return 2
            reconcile_resolve(args.resolve, args.verdict, args.note)
            print("reconciled %s as %s" % (args.resolve, args.verdict))
            return 0
        if args.auto:
            for p in reconcile_auto()[0]:
                print("  settled %s  %s  moot: %s" % (p.get("cid"), p.get("tool"), p.get("moot")))
        pend = outstanding_indeterminate()
        print("evidence log %s; %d mutating call(s) with UNKNOWN outcome" % (EVIDENCE_LOG, len(pend)))
        for p in pend:
            print("  %s  %s  %s  args %s  pid %s %s  %s" % (p.get("cid"), p.get("t"), p.get("tool"),
                                                         p.get("args_sha256"), p.get("pid"), p.get("script"),
                                                         p.get("error", p.get("status"))))
        return 1 if pend else 0

    host, port, token = resolve_endpoint(args.host, args.port, args.token, args.log_path)
    if not token:
        print("no bridge token found (CLI, env GABP_TOKEN, or Player.log)", file=sys.stderr)
        return 2

    if args.call:          # --list-tools beside --call is no way round the acknowledgment (BRIDGE_CLIENT_HARDEN_FOUR_ROUGH_EDGES)
        probe = RimBridge(host, port, token, timeout=args.timeout)
        try:
            params = json.loads(args.params)
        except ValueError:
            params = None
        if args.read_only_static:
            why = "--read-only-static is for jawa/static_call" if args.call != "jawa/static_call" else read_only_static(params)
            if why:
                print("REFUSING '%s': %s" % (args.call, why), file=sys.stderr)
                return 3
            probe.static_reads = True
        if not probe.looks_read_only(args.call, params) and not args.yes_i_know_this_is_live:
            print("REFUSING '%s': it does not look read-only. This drives a LIVE game.\n"
                  "Pass --yes-i-know-this-is-live if you really mean it." % args.call,
                  file=sys.stderr)
            return 3

    try:
        with RimBridge(host, port, token, timeout=args.timeout) as rb:
            if args.list_tools:
                tools = rb.list_tools()
                print(json.dumps({"count": len(tools), "tools": tools}, indent=2))
            if args.call:
                rb.static_reads = bool(args.read_only_static)
                out = rb.call(args.call, json.loads(args.params))
                print(json.dumps(out, indent=2))
            if not args.list_tools and not args.call:
                print(json.dumps({"welcome": rb.welcome}, indent=2))
    except RimBridgeError as ex:
        print("bridge error: %s" % ex, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
