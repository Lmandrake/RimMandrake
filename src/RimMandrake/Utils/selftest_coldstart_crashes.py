#!/usr/bin/env python3
"""Offline proof of coldstart_crashes.py (COLDSTART_PROVE_NTDLL_CRASH_NO_FOLDER).

Replays SteveDesktop 2026-10-26 15:37Z: RimWorld died with APPCRASH ntdll c0000005 + FaultTolerantHeap
and wrote NO Crash_* folder. The old criterion (Crash_* folders only) passes that start; the new check
must fail it on the WER witness alone. Also: a blind witness (no sentinel, zero records, absent crash
root) fails as UNMEASURED; another program's crash and a RADAR leak report do not count; events before
the window do not count; prove_tps_startup_no_bg_jit.py clause 3 calls the shared check.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coldstart_crashes as cc  # noqa: E402

SINCE = cc.epoch("2026-10-26T15:36:16Z")          # session start, ~44 s before the death
E1000 = {"utc": "2026-10-26T15:37:00.4123456Z", "id": 1000, "provider": "Application Error",
         "msg": "Faulting application name: RimWorldWin64.exe, version: 2021.3.30.33648, time stamp: 0x6527a0b1\n"
                "Faulting module name: ntdll.dll, version: 10.0.19041.6456, time stamp: 0x7ec9c15d\n"
                "Exception code: 0xc0000005\nFaulting process id: 0x6554"}
E1001 = {"utc": "2026-10-26T15:37:01.0000000Z", "id": 1001, "provider": "Windows Error Reporting",
         "msg": "Fault bucket , type 0\nEvent Name: APPCRASH\nResponse: Not available\nP1: RimWorldWin64.exe\n"
                "P4: ntdll.dll\nP7: c0000005\nP8: 00000000000a17c7"}
FTH = {"utc": "2026-10-26T15:37:01.1000000Z", "id": 1001, "provider": "Windows Error Reporting",
       "msg": "Event Name: FaultTolerantHeap\nP1: RimWorldWin64.exe\nP4: ffffbaad"}
RADAR = {"utc": "2026-10-26T15:37:05Z", "id": 1001, "provider": "Windows Error Reporting",
         "msg": "Event Name: RADAR_PRE_LEAK_64\nP1: RimWorldWin64.exe"}
OTHER = {"utc": "2026-10-26T15:37:02Z", "id": 1000, "provider": "Application Error",
         "msg": "Faulting application name: chrome.exe\nFaulting module name: ntdll.dll"}
OLD = dict(E1000, utc="2026-10-25T19:48:04Z")

fails = []


def expect(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def run(events, records=40758, folders=()):
    lines = []
    good = cc.check(SINCE, lambda ok, m: lines.append((ok, m)),
                    wer=lambda s: (records, events), folders=lambda s: list(folders))
    return good, lines


# the instance: no folder, WER says it died
old_criterion_passes = True   # the folder-only criterion: no Crash_ folder was written
good, lines = run([E1000, E1001, FTH, RADAR, OTHER])
expect(old_criterion_passes and not good, "2026-10-26 ntdll death with no Crash_ folder: folder-only passes, new check FAILS")
expect([ok for ok, _ in lines] == [True, False], "folder line ok, WER line fails: %s" % lines)
hits = cc.wer_crashes([E1000, E1001, FTH, RADAR, OTHER, OLD], SINCE)
expect(hits == [E1000, E1001, FTH], "hits are exactly 1000 + APPCRASH + FaultTolerantHeap (not RADAR, chrome, pre-window)")
expect("ntdll.dll 0xc0000005" in lines[1][1] and "APPCRASH ntdll.dll" in lines[1][1], "summary names module and code")

# clean start
good, _ = run([RADAR, OTHER, OLD])
expect(good, "a start with only a RADAR report, another app's crash and a pre-window event passes")
good, lines = run([], folders=["Crash_2026-10-26_153700"])
expect(not good and not lines[0][0], "a new Crash_ folder alone still fails")

# blind witnesses fail
good, lines = run([], records=0)
expect(not good and "UNMEASURED" in lines[-1][1], "Application log with 0 records = UNMEASURED fail")
for text in ("", "Get-WinEvent : Access is denied", None):
    try:
        cc.parse_wer(text)
        expect(False, "parse_wer(%r) must raise" % (text,))
    except ValueError:
        expect(True, "parse_wer(%r) raises (no sentinel)" % (text,))
lines = []
good = cc.check(SINCE, lambda ok, m: lines.append((ok, m)), wer=lambda s: cc.parse_wer("boom"),
                folders=lambda s: [])
expect(not good and "UNMEASURED" in lines[-1][1], "unreadable WER output fails UNMEASURED")
with tempfile.TemporaryDirectory() as d:
    try:
        cc.crash_folders(SINCE, root=os.path.join(d, "absent"))
        expect(False, "absent crash root must raise")
    except ValueError:
        expect(True, "absent crash root raises (blind)")
    os.makedirs(os.path.join(d, "Crash_new"))
    os.makedirs(os.path.join(d, "Crash_old"))
    os.utime(os.path.join(d, "Crash_old"), (SINCE - 3600, SINCE - 3600))
    os.utime(os.path.join(d, "Crash_new"), (SINCE + 44, SINCE + 44))
    expect(cc.crash_folders(SINCE, root=d) == ["Crash_new"], "crash_folders keeps only folders in the window")

# parse_wer: real powershell output shapes (single object, array, empty)
one = cc.SENTINEL + "\r\n{\"records\":5}\r\n" + '{"utc":"2026-10-26T15:37:00Z","id":1000,"provider":"x","msg":"RimWorldWin64.exe"}'
expect(cc.parse_wer(one) == (5, [{"utc": "2026-10-26T15:37:00Z", "id": 1000, "provider": "x", "msg": "RimWorldWin64.exe"}]),
       "parse_wer wraps a lone object, strips CRLF")
expect(cc.parse_wer(cc.SENTINEL + "\n{\"records\":5}\n[]") == (5, []), "parse_wer reads an empty array")
expect(cc.parse_wer(cc.SENTINEL + "\n{\"records\":5}") == (5, []), "parse_wer reads a missing body as none")

# Message null (unrenderable): Properties carry the app and event name
NOMSG = {"utc": "2026-10-26T15:37:00Z", "id": 1000, "msg": None, "props": ["RimWorldWin64.exe", "2021.3.30", "0x6527a0b1", "ntdll.dll"]}
NOMSG1001 = {"utc": "2026-10-26T15:37:01Z", "id": 1001, "msg": None, "props": ["0", "0", "APPCRASH", "Not available", "0", "RimWorldWin64.exe"]}
expect(cc.wer_crashes([NOMSG, NOMSG1001], SINCE) == [NOMSG, NOMSG1001], "events with a null Message still count via Properties")
try:
    cc.parse_wer(cc.SENTINEL)
    expect(False, "sentinel alone must raise")
except ValueError:
    expect(True, "sentinel with no header raises ValueError (UNMEASURED, not a traceback)")

# the cold-start proof uses the shared check
src = open(os.path.join(HERE, "..", "bridgetools", "prove_tps_startup_no_bg_jit.py")).read()
expect("coldstart_crashes.check(start" in src and "os.listdir(CRASHES)" not in src,
       "prove_tps_startup_no_bg_jit.py clause 3 reads both witnesses via coldstart_crashes.check")

print("PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
