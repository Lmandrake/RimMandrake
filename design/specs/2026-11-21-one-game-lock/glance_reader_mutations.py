#!/usr/bin/env python3
"""Plant each fault in the two moved readers (handoff.bridge_lines, preflight_flowworks.p_b1), run
selftest_game_driver_readers.py, restore. Every row must read CAUGHT. Measured 2026-11-22: 9 of 9 caught.
Item RIMMANDRAKE_MOVE_TWO_MORE_GLANCE_READERS_CENSUS_MISSED. Run from anywhere: python3 glance_reader_mutations.py"""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
import subprocess
import sys
H="src/RimMandrake/Utils/handoff.py"; P="src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py"
M=[("handoff_only_archbig",H,'return [r["line"] for r in rows] or','return [r["line"] for r in rows][:1] or'),
   ("handoff_drops_could_not_look",H,'return [r["line"] for r in rows] or','return [r["line"] for r in rows if r["state"] != "UNKNOWN"] or'),
   ("handoff_blind_reads_free",H,'return ["COULD NOT LOOK at the game locks: %s: %s" % (type(e).__name__, e)]','return ["ArchBig: FREE"]\n    rows = [dict(r, line="ArchBig: FREE") if r["state"] == "UNKNOWN" else r for r in rows]'),
   ("p_b1_ignores_alive",P,'held = (r.get("seat") or "") if (r.get("alive") or r.get("owner_hold")) else ""','held = r.get("seat") or ""'),
   ("p_b1_unknown_is_fail",P,'        return row("P-B1", UNMEASURED, r["line"])','        return row("P-B1", FAIL, r["line"])'),
   ("p_b1_always_archbig",P,'game_lock.query(game_lock.current_game(), pipe=False','game_lock.query("a", pipe=False'),
   ("p_b1_free_passes",P,'if not (r.get("mine") or (held and held == mine)):','if held and not (r.get("mine") or held == mine):'),
   ("p_b1_reads_pipe_hold",P,'current_game(), pipe=False,','current_game(), pipe=True,'),
   ("p_b1_prefix_match",P,'(held and held == mine)','(held and mine.startswith(held[:1]))'),
]
for name,f,old,new in M:
    src=open(f).read(); assert src.count(old)==1,(name)
    open(f,"w").write(src.replace(old,new))
    try:
        r=subprocess.run([sys.executable,"src/RimMandrake/rimflow/selftest_game_driver_readers.py"],capture_output=True,text=True,timeout=900)
        fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        print("%-30s %s  %s"%(name,"CAUGHT" if r.returncode else "NOT CAUGHT",(fails[0][:110] if fails else r.stderr[-150:])))
    finally:
        open(f,"w").write(src)
