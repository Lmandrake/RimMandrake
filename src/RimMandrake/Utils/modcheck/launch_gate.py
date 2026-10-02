"""launch_gate -- refuse to start a map when Player.log shows our own C# types did not load.

MEASURED 2026-10-01 (northstar pass 3): a deploy from a stale checkout shipped old Stillsand/CreatureBehaviors DLLs; ~64
'Could not find type named RimMandrake.*' errors followed, those defs lost their class, and starting a quicktest game died in
ReadingPolicyDatabase.GenerateStartingPolicies (NRE in GenTypes.SameOrSubclassOf) -> the owner saw 'Error while generating map'.
A map must never be started on top of that, so the check runs right after 'Bridge token:' and BEFORE any world is created.

    scan(text)                -> {"ok", "problems": [...], "probe": bool}   pure function over log text
    check_player_log(path)    -> same, reading the file; no readable log is UNMEASURED (ok False), never "clean"
The sanity probe: the log must contain 'Bridge token:' (so an empty/wrong/old log can never read as clean).
CLI: python3 launch_gate.py [Player.log path]   exit 0 clean, 1 type errors found, 2 cannot tell
"""
import os
import re
import sys

PAT = re.compile(r"Could not find (?:a )?type named (RimMandrake|RimStarWars|RimUtinni)[.\w]*")
PROBE = "Bridge token:"
WIN_LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
WSL_LOG = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"


def default_log():
    return WIN_LOG if os.name == "nt" else WSL_LOG


def scan(text):
    probe = PROBE in text
    types = sorted({m.group(0).split("named ", 1)[1] for m in PAT.finditer(text)})
    problems = []
    if not probe:
        problems.append("UNMEASURED: log has no %r line (wrong, empty or old log)" % PROBE)
    if types:
        problems.append("%d missing RimMandrake type(s): %s%s" % (len(types), ", ".join(types[:12]), " ..." if len(types) > 12 else ""))
    return {"ok": probe and not types, "problems": problems, "probe": probe, "missing_types": types}


def check_player_log(path=None):
    path = path or default_log()
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return scan(f.read())
    except OSError as e:
        return {"ok": False, "problems": ["UNMEASURED: cannot read %s (%s)" % (path, e)], "probe": False, "missing_types": []}


if __name__ == "__main__":
    r = check_player_log(sys.argv[1] if len(sys.argv) > 1 else None)
    print("launch_gate: %s" % ("CLEAN" if r["ok"] else "; ".join(r["problems"])))
    sys.exit(0 if r["ok"] else (1 if r["missing_types"] else 2))
