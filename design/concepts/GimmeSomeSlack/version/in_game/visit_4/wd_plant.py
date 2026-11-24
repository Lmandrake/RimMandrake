"""wd_plant.py: sc_save_reload_wire_down's repaired stage, real and planted, on the map that is up (no save): whole before the cut, mid-way after, then a planted cord lost and a planted lamp lit between the two reads must FAIL the reload rows. python.exe."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, save_wire_down as WD
B = VA.A(); out = {}
WD.stage(B, V); u = WD.read(B); out["uncut_whole"] = WD.whole(u)
out["down"] = WD.wire_down(B); before = WD.read(B); out["midway_refused"] = WD.midway(before)
out["real_same_game"] = WD.reload_rows(before, WD.read(B))
B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (WD.PLOT[0] + 10, WD.PLOT[1]), categories="Building"); B.ticks(5)
out["planted_cell_lost"] = WD.reload_rows(before, WD.read(B))
# planted: the lamps have no battery -> the uncut read must be refused as not standing
WD.stage(B, V); B.call("jawa/destroy_batch", rects="%d,%d,1,2" % WD.FLOOR_BATT, categories="Building"); B.ticks(300)
out["planted_no_battery_whole"] = WD.whole(WD.read(B))
out["planted_no_battery_row"] = WD.control_row(WD.read(B), b"", b"")[:2]
print(json.dumps(out, indent=1))
