"""Round 5: live unforced-bends probe on the loaded map, rows printed. python.exe ralph/live/r5_bends.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import gss_stage as G  # noqa: E402
B = G.RL.LiveBridge()
b = B.probe("bends")
t = b.get("tally") or {}
print("BENDS world=%s strands=%s bends=%s UNFORCED=%s why=%s" % (b.get("world"), t.get("strands"), t.get("bends"), t.get("unforced"), json.dumps(t.get("why"))))
for r in (b.get("rows") or t.get("rows") or []):
    if r.get("why") == "unforced":
        print("ROW", json.dumps(r))
