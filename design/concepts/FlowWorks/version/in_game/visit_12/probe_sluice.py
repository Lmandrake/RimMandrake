"""probe_sluice.py x z: the gizmos, door state and inspect string of the gate at (x, z) on the live map, then run
water_scenes_walk.gate_open there and print its whole reply (the walk-save stager cuts it at 60 chars) (visit 12 probe)."""
import sys, os, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
sys.path.insert(0, os.path.join(R, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(R, "src", "RimMandrake", "FlowWorks", "northstar"))
import validation_core as V
B = V.Bridge()
x, z = int(sys.argv[1]), int(sys.argv[2])
B.call("rimworld/set_god_mode", enabled=True); B.call("rimworld/clear_selection"); B.call("rimworld/click_cell", x=x, z=z)
gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
print("gizmos:", [g.get("label") for g in gz])
B.call("rimworld/clear_selection")
ci = B.call("rimworld/get_cell_info", x=x, z=z) or {}
print("cell:", [(t.get("defName"), t.get("className")) for t in (ci.get("cell") or {}).get("things") or []], "walkable", (ci.get("cell") or {}).get("walkable"))
if "--open" in sys.argv:
    import water_scenes_walk as m
    W = m.Walk() if hasattr(m, "Walk") else None
    print("gate_open:", m.gate_open(W, (x, z)))
