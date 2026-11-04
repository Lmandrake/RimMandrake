#!/usr/bin/env python3
"""Live proof A1 of JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT - read-only, run after one cold start.

The fix moved every startup background job off the patching window: the session manifest is parked and
written by the idle pump (>= ArchiveIdleSeconds = 10 s of no long event), the writer thread starts only
after a synchronous first pass, the watchdog is warmed on the installing thread. A cold start of a DLL
built from these sources must therefore show, for the NEWEST TPS session (newest hb_<session>.json):

  1. the deployed companion DLL is FRESH against --rev (companion_identity: embedded source hash);
  2. the session row was written (the record opened) and session_<id>.json exists, last written at
     least 10 s after the session row: the manifest waited for idle;
  3. no Crash_* folder under the Unity crash root is newer than the session start;
  4. the session's record holds no error row from "install", "manifest" or "idle-pump";
  5. if Player-prev.log predates the session and archivePlayerLog is on, its content is kept in
     JawaBench/tps/logs as *_<sha12>.log (the archive dedupes by content, so an existing copy counts).

    python3 src/RimMandrake/bridgetools/prove_tps_startup_no_bg_jit.py [--rev HEAD]
Exit 0 = every clause holds, 1 = one does not (each line says which).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
from game_paths import LOCALLOW, GAME_DIR  # noqa: E402

IDLE_S = 10.0
TPS = os.path.join(LOCALLOW, "JawaBench", "tps")
# Unity writes crash folders to %LOCALAPPDATA%\Temp\<company>\<product>\Crashes; LOCALLOW is %USERPROFILE%\AppData\LocalLow\<company>\<product>
_APPDATA = os.path.dirname(os.path.dirname(os.path.dirname(LOCALLOW)))
CRASHES = os.path.join(_APPDATA, "Local", "Temp", *LOCALLOW.replace("\\", "/").rstrip("/").split("/")[-2:], "Crashes")
DLL = os.path.join(GAME_DIR, "BridgeTools", "JawaBench", "JawaBench.BridgeTools.dll")


def epoch(utc):
    return dt.datetime.strptime(utc.rstrip("Z")[:23], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=dt.timezone.utc).timestamp()


def rows_of(session):
    out = []
    for f in sorted(glob.glob(os.path.join(TPS, "tps_*_%s_*.jsonl" % session))):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict) and r.get("session") == session:
                    out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="HEAD", help="the sources the deployed DLL must match (default HEAD)")
    a = ap.parse_args()
    fails = []

    def say(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    r = subprocess.run([sys.executable, os.path.join(HERE, "companion_identity.py"), DLL, "--repo", REPO, "--rev", a.rev],
                       capture_output=True, text=True)
    say(r.returncode == 0, "1 deployed DLL vs %s: %s" % (a.rev, (r.stdout or r.stderr).strip().splitlines()[-1:] or "no output"))

    hbs = sorted(glob.glob(os.path.join(TPS, "hb_*.json")), key=os.path.getmtime)
    if not hbs:
        say(False, "2 no hb_*.json under %s (instrument blind or sampler off)" % TPS)
        return 1
    session = os.path.basename(hbs[-1])[3:-5]
    rows = rows_of(session)
    srow = next((x for x in rows if x.get("kind") == "session"), None)
    say(srow is not None, "2 session %s: session row present (%d rows read)" % (session, len(rows)))
    if srow is None:
        return 1
    start = epoch(srow["utc"])
    man = os.path.join(TPS, "session_%s.json" % session)
    if os.path.exists(man):
        lag = os.path.getmtime(man) - start
        say(lag >= IDLE_S, "2 manifest written %.1f s after the session row (needs >= %.0f s: deferred to idle)" % (lag, IDLE_S))
    else:
        say(False, "2 manifest %s missing (startup never went idle, or the pump lost it)" % man)

    if not os.path.isdir(CRASHES):
        say(False, "3 crash root %s not found: cannot see crashes (UNMEASURED)" % CRASHES)
    else:
        new = [d for d in os.listdir(CRASHES) if d.startswith("Crash_") and os.path.getmtime(os.path.join(CRASHES, d)) >= start - 5]
        say(not new, "3 Crash_ folders since session start: %s" % (new or "none"))

    bad = [x for x in rows if x.get("kind") == "error" and x.get("where") in ("install", "manifest", "idle-pump")]
    say(not bad, "4 startup error rows: %s" % ([(x.get("where"), x.get("error")) for x in bad] or "none"))

    prev = os.path.join(LOCALLOW, "Player-prev.log")
    archive_on = (srow.get("settings") or {}).get("archivePlayerLog", True)
    if archive_on and os.path.exists(prev) and os.path.getmtime(prev) < start:
        with open(prev, "rb") as fh:
            tag = hashlib.sha256(fh.read()).hexdigest()[:12]
        kept = glob.glob(os.path.join(TPS, "logs", "*_%s.log" % tag))
        say(bool(kept), "5 Player-prev.log (sha12 %s) kept in logs/: %s" % (tag, [os.path.basename(k) for k in kept] or "NO"))
    else:
        print("ok   5 Player-prev archive not owed (archivePlayerLog=%s, Player-prev present=%s)" % (archive_on, os.path.exists(prev)))

    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
