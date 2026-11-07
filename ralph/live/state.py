#!/usr/bin/env python3
"""What is loaded now: map, colonists, live ends, fallen wires. python.exe ralph/live/state.py"""
import json, os, sys
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402
B = RL.LiveBridge()
mi = B.call("jawa/map_info")
print("map", json.dumps({k: mi.get(k) for k in ("mapBiome", "season", "tile", "size", "colonists", "success")}))
m = B.probe("motion")
print("motion", json.dumps({k: m.get(k) for k in ("whipDraws", "liveFloorEnds")}), "tips", len(m.get("sparkTips") or []))
c = B.ap("census")
an = c.get("anchors") or []
print("anchors", len(an), "fallen", sum(len(a.get("fallen") or []) for a in an), "liveFallen", sum(1 for a in an if a.get("fallenLive") is True and a.get("fallen")))
print("census keys", sorted(c.keys())[:40])
