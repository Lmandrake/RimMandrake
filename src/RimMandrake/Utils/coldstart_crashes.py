#!/usr/bin/env python3
"""Did RimWorld crash since T? Reads BOTH crash witnesses a cold-start proof needs.

A Unity crash writes a Crash_* folder under %LOCALAPPDATA%\\Temp\\<company>\\<product>\\Crashes - but not
every crash does. SteveDesktop 2026-10-26 15:37Z: RimWorld died ~44 s into startup with Windows APPCRASH
ntdll c0000005 (+ a FaultTolerantHeap report) and wrote NO Crash_* folder
(COLDSTART_PROVE_NTDLL_CRASH_NO_FOLDER). So "no new Crash_* folder" alone is blind to a native-heap
death; this module also reads the Windows Application log, Event 1000 (Application Error) and 1001
(Windows Error Reporting) for RimWorldWin64.exe.

    python3 src/RimMandrake/Utils/coldstart_crashes.py --since-process   # since the running game started
    python3 src/RimMandrake/Utils/coldstart_crashes.py --since 2026-10-26T15:36:00Z
    python3 src/RimMandrake/Utils/coldstart_crashes.py --hours 2

Exit 0 = both witnesses readable and neither saw a crash; 1 = a crash, or a witness was blind (UNMEASURED
is a failure: a reader that cannot see must not pass). With --since-process and no RimWorld running, the
look-back is --hours (default 1) and the run fails: a cold start that left no process did not survive.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from game_paths import LOCALLOW  # noqa: E402

EXE = "RimWorldWin64.exe"
SLACK_S = 5.0
# Unity writes crash folders to %LOCALAPPDATA%\Temp\<company>\<product>\Crashes; LOCALLOW is
# %USERPROFILE%\AppData\LocalLow\<company>\<product>
_APPDATA = os.path.dirname(os.path.dirname(os.path.dirname(LOCALLOW)))
CRASHES = os.path.join(_APPDATA, "Local", "Temp", *LOCALLOW.replace("\\", "/").rstrip("/").split("/")[-2:], "Crashes")
# Event 1001 is a WER report of any kind; only these event names mean the process died or faulted.
# RADAR_PRE_LEAK_64 and friends are diagnostics, not deaths. FaultTolerantHeap is the heap-corruption
# report that rode with the 2026-10-26 ntdll death: count it.
CRASH_1001 = re.compile(r"^(APPCRASH|BEX(64)?|MoAppCrash|AppHang\w*|FaultTolerantHeap|CLR20r3)$", re.I)
SENTINEL = "WER_READ_OK"


def epoch(utc):
    """ISO-8601 (Z, offset or 7-digit fraction from .NET 'o') -> epoch seconds."""
    t = dt.datetime.fromisoformat(utc.strip())   # 3.11+: 'Z' and >6 fraction digits are accepted
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.timestamp()


def event_name(msg, props=()):
    m = re.search(r"Event Name:\s*(\S+)", msg or "")
    if m:
        return m.group(1)
    return props[2] if len(props) > 2 else ""      # 1001 with no rendered Message: Properties[2] is the event name


def is_rimworld_crash(ev, exe=EXE):
    """One Application-log event (dict utc/id/provider/msg) -> True if it records RimWorld dying."""
    msg = ev.get("msg") or ""
    props = ev.get("props") or []
    # Message can be null when Windows cannot render the event text; Properties still name the app
    if exe.lower() not in (msg + "|" + "|".join(props)).lower():
        return False
    if ev.get("id") == 1000:
        return True
    if ev.get("id") == 1001:
        return bool(CRASH_1001.match(event_name(msg, props)))
    return False


def parse_wer(text):
    """powershell output of WER_SCRIPT -> (log record count, events). Raises ValueError when blind."""
    lines = (text or "").replace("\r", "").strip().splitlines()
    if not lines or lines[0].strip() != SENTINEL:
        raise ValueError("no %s sentinel: the Application log was not read (%r)" % (SENTINEL, (text or "")[:200]))
    try:
        head = json.loads(lines[1])
        body = json.loads("\n".join(lines[2:]) or "[]")
    except (IndexError, ValueError) as e:
        raise ValueError("Application log output after the sentinel is unreadable: %s" % e)
    if isinstance(body, dict):
        body = [body]
    return int(head.get("records") or 0), body


def wer_crashes(events, since, exe=EXE):
    return [e for e in events if is_rimworld_crash(e, exe) and epoch(e["utc"]) >= since - SLACK_S]


WER_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$since = [DateTime]::Parse('%s').ToUniversalTime().ToLocalTime()
$records = (Get-WinEvent -ListLog Application).RecordCount
try { $ev = @(Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000,1001; StartTime=$since}) }
catch { if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { $ev = @() } else { throw } }
'%s'
(@{records=$records} | ConvertTo-Json -Compress)
ConvertTo-Json -Compress -InputObject @($ev | ForEach-Object { [pscustomobject]@{
  utc=$_.TimeCreated.ToUniversalTime().ToString('o'); id=$_.Id; provider=$_.ProviderName; msg=$_.Message;
  props=@($_.Properties | ForEach-Object { [string]$_.Value }) } })
"""


def read_wer(since, timeout=90):
    iso = dt.datetime.fromtimestamp(since - SLACK_S, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", WER_SCRIPT % (iso, SENTINEL)],
                         capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise ValueError("powershell exit %d: %s" % (out.returncode, (out.stderr or out.stdout)[-300:]))
    return parse_wer(out.stdout)


def crash_folders(since, root=CRASHES):
    """-> list of Crash_* folder names newer than since. Raises ValueError when the root is absent (blind)."""
    if not os.path.isdir(root):
        raise ValueError("crash root %s not found: cannot see crashes" % root)
    return sorted(d for d in os.listdir(root)
                  if d.startswith("Crash_") and os.path.getmtime(os.path.join(root, d)) >= since - SLACK_S)


def process_start():
    """Start time (epoch) of this process's RimWorldWin64 (game_instance.py), or None when it is not running."""
    import game_instance
    try:
        ps = ("$p = %s; if ($p) { $p.StartTime.ToUniversalTime().ToString('o') }" % game_instance.ps_process())
        out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
                             capture_output=True, text=True, timeout=60)
        s = (out.stdout or "").replace("\r", "").strip()
        return epoch(s) if s else None
    except (OSError, ValueError, subprocess.TimeoutExpired, game_instance.Blind) as e:
        print("FAIL process: start time unreadable: %s (UNMEASURED)" % e)
        return None


def check(since, say, wer=read_wer, folders=crash_folders):
    """Both witnesses since `since`; say(ok, msg) per line. Returns True when both see and neither saw a crash."""
    good = True
    try:
        new = folders(since)
        say(not new, "crash folders: Crash_* since %s: %s" % (_iso(since), new or "none"))
        good &= not new
    except ValueError as e:
        say(False, "crash folders: %s (UNMEASURED)" % e)
        good = False
    try:
        records, events = wer(since)
        if records <= 0:
            say(False, "WER: Application log reports %d records: instrument blind (UNMEASURED)" % records)
            return False
        hits = wer_crashes(events, since)
        say(not hits, "WER: Event 1000/1001 for %s since %s (%d events read, log holds %d): %s" % (
            EXE, _iso(since), len(events), records,
            ["%s %d %s" % (h["utc"][:19], h["id"], _summary(h)) for h in hits] or "none"))
        good &= not hits
    except (ValueError, OSError, subprocess.TimeoutExpired) as e:
        say(False, "WER: %s (UNMEASURED)" % e)
        good = False
    return good


def _summary(ev):
    msg = ev.get("msg") or ""
    if ev.get("id") == 1001:
        p4 = re.search(r"P4:\s*(\S+)", msg)
        return "%s %s" % (event_name(msg), p4.group(1) if p4 else "")
    m = re.search(r"Faulting module name:\s*([^,\s]+)", msg)
    c = re.search(r"Exception code:\s*(\S+)", msg)
    return "%s %s" % (m.group(1) if m else "?", c.group(1) if c else "?")


def _iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--since", help="ISO UTC start of the window")
    g.add_argument("--since-process", action="store_true", help="since the running RimWorldWin64 started")
    ap.add_argument("--hours", type=float, default=1.0, help="look-back when no --since (default 1)")
    a = ap.parse_args(argv)
    fails = []

    def say(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    now = dt.datetime.now(dt.timezone.utc).timestamp()
    if a.since:
        since = epoch(a.since)
    elif a.since_process:
        since = process_start()
        say(since is not None, "process: RimWorldWin64 %s" % (
            "started %s" % _iso(since) if since else "NOT running: looking back %.1f h" % a.hours))
        if since is None:
            since = now - a.hours * 3600
    else:
        since = now - a.hours * 3600
    check(since, say)
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
