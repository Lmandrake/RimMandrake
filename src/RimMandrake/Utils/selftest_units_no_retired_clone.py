#!/usr/bin/env python3
"""selftest (FOUNDRY_UNITS_MIGRATE_GHOST_STILL_ON_SHIFT): no shipped systemd unit runs code from a retired seat clone.

FOUNDRY was retired 2026-11-02 and its clone emptied 2026-11-05; rm-codebase-health and rm-mirror kept running
its frozen HEAD until 0c6807acae repointed them at the bench clone. This reads the repo's unit files only
(src/RimMandrake/Utils/systemd/), so it runs on any exported tree; it touches no installed unit.

    python3 src/RimMandrake/Utils/selftest_units_no_retired_clone.py
"""
import re
import sys
from pathlib import Path

UNITS = Path(__file__).resolve().parent / "systemd"
RETIRED = ("foundry",)  # seat clones under /home/mandrake/rm/ that no unit may run from
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def retired_refs(text):
    """Return the retired clone roots a unit's text names (path form /rm/<seat> followed by / or end)."""
    out = []
    for seat in RETIRED:
        if re.search(r"/rm/%s(?:/|\s|'|\"|$)" % re.escape(seat), text, re.M):
            out.append(seat)
    return out


def directives(text, key):
    return [ln.split("=", 1)[1].strip() for ln in text.splitlines() if ln.strip().startswith(key + "=")]


# --- the detector can see (sanity probe on fixtures)
check(retired_refs("WorkingDirectory=/home/mandrake/rm/foundry\n") == ["foundry"], "a bare retired workdir is caught")
check(retired_refs("ExecStart=/usr/bin/python3 /home/mandrake/rm/foundry/src/x.py\n") == ["foundry"],
      "a retired script path is caught")
check(retired_refs("ExecStart=/usr/bin/python3 /home/mandrake/rm/bench/src/x.py\n") == [], "a bench path is clean")
check(retired_refs("Description=FOUNDRY retired 2026-11-02\n") == [], "prose naming the seat is not a path")

# --- the shipped units
files = sorted(p for p in UNITS.glob("*") if p.suffix in (".service", ".timer"))
check(len(files) >= 10, "the unit directory is seen (%d unit files)" % len(files))
for p in files:
    bad = retired_refs(p.read_text())
    check(not bad, "%s names no retired clone%s" % (p.name, (" (names %s)" % bad) if bad else ""))

health = (UNITS / "rm-codebase-health.service").read_text()
check(directives(health, "WorkingDirectory") == ["/home/mandrake/rm/bench"],
      "rm-codebase-health.service runs in the bench clone")
mirror = (UNITS / "rm-mirror.service").read_text()
ex = directives(mirror, "ExecStart")
check(len(ex) == 1 and "/home/mandrake/rm/bench/src/RimMandrake/Utils/mirror.py" in ex[0],
      "rm-mirror.service runs mirror.py from the bench clone")

print("FAIL %d" % len(FAILS) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)
