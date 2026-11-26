#!/usr/bin/env python3
"""steve_ends_in_conductor_log_accept.py - the outcome check of RIMMANDRAKE_LOG_STEVE_RUN_ENDS_FOR_CONDUCTOR_EIGHT_UNREAD.

LIVE: reads SteveDesktop's own run records over ssh, and the Conductor log on this machine (Archmagi). The need: every
detached run that ended on SteveDesktop has its DETACHED RUN ENDED line in the Conductor log, within one tick.
  exit 0  every SteveDesktop run that ended between WINDOW_S and GRACE_S ago has a DETACHED RUN ENDED line naming its unit
  exit 1  at least one such run has no line (each is printed)
  exit 2  could not look: the host or the log could not be read, or the host listed no record at all
Base 2026-11-25 9:55 PM PST: 35 records on SteveDesktop, none has a line (exit 1).
"""
import json
import shlex
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import detached_helper as D  # noqa: E402
import run_host as R  # noqa: E402

# budget: danger=a run that ended moments ago is judged before the 5 min rm-run-alive beat could relay it; evidence=the beat's own period
GRACE_S = 900
# budget: danger=a record folder that only grows judges runs from before the relay existed forever; matches run_host.RELAY_WINDOW_S
WINDOW_S = R.RELAY_WINDOW_S if hasattr(R, "RELAY_WINDOW_S") else 7 * 86400

PY = ("import json,sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import detached_helper as D; "
      "print(json.dumps([{k: r.get(k) for k in ('unit','status','ended')} for r in D.all_records()]))")


def main():
    now = time.time()
    try:
        r = subprocess.run(R._ssh(R.door("SteveDesktop"), "cd %s && python3 -c %s" % (R.BENCH, shlex.quote(PY))),
                           capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)  # budget: class=ssh hang guard
        recs = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
    except Exception as e:  # noqa: BLE001
        print("COULD NOT LOOK: SteveDesktop's records: %s: %s" % (type(e).__name__, e))
        return 2
    if not isinstance(recs, list) or not recs:
        print("COULD NOT LOOK: SteveDesktop listed no records (ssh exit %s: %s)" % (r.returncode, (r.stderr or "").strip()[:200]))
        return 2
    try:
        with open(D.conductor_log_path(), encoding="utf-8", errors="replace") as f:
            ended = [ln for ln in f.read().splitlines() if "DETACHED RUN ENDED" in ln]
    except OSError as e:
        print("COULD NOT LOOK: the Conductor log: %s" % e)
        return 2
    due = [x for x in recs if x.get("status") == "finished" and isinstance(x.get("ended"), (int, float))
           and now - WINDOW_S <= x["ended"] <= now - GRACE_S]
    missing = [x["unit"] for x in due if not any(x["unit"] in ln for ln in ended)]
    for u in missing:
        print("MISSING %s" % u)
    print("%d of %d SteveDesktop run ends (ended %d s to %d days ago) have a DETACHED RUN ENDED line in %s"
          % (len(due) - len(missing), len(due), GRACE_S, WINDOW_S // 86400, D.conductor_log_path()))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
