"""TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE A1: a raised timber leaf with NO winch draws its upright picture, beside a raised steel
leaf WITH a winch. Trenches 8 notches deep under each span; drawbridges by RM_DrawbridgeProofs.ProofMakeDrawbridge; raised by
ProofDevSet ...;raise;instant; state by ProofLeaf; then a close capture of each, and a lowered timber control."""
import json, os, shutil, sys, time
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DP = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
res = {}
O.call("jawa/destroy_batch", rects="98,138,30,16", categories="Plant")
O.call("jawa/destroy_batch", rects="121,140,1,6;125,140,1,6", categories="Building,Item")
for x in (121, 125):
    for z in range(141, 145):
        O.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=8)
res["timber_nowinch"] = O.static(DP, "ProofMakeDrawbridge", "121,140;121,145;timber;A")
res["timber_lowered_control"] = O.static(DP, "ProofMakeDrawbridge", "125,140;125,145;timber;A")
res["raise_timber"] = O.static(DP, "ProofDevSet", "121,142;raise;instant")
O.call("jawa/map_commit")
for k, c in (("leaf_timber", "121,142"), ("leaf_steel", "110,143"), ("leaf_control", "125,142")):
    res[k] = O.static(DP, "ProofLeaf", c)
shots = []
for name, x, z, w, h in (("all_three", 107, 137, 21, 12), ("timber_nowinch_raised", 119, 139, 5, 8), ("steel_winch_raised", 108, 138, 5, 10),
                         ("timber_lowered", 123, 139, 5, 8)):
    fn = "leaf_%d_%s" % (int(time.time()), name); asked = time.time()
    r = O.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=0, fileName=fn, suppressMessage=True,
               rootSize=12.0 if name == "all_three" else 7.0)
    src, size = str(r.get("path") or ""), -1
    for _ in range(40):
        now = os.path.getsize(src) if src and os.path.isfile(src) else -1
        if now > 0 and now == size: break
        size = now; time.sleep(0.4)
    if src and os.path.isfile(src) and os.path.getmtime(src) >= asked - 2:
        dst = os.path.join(OUT, name + ".png"); shutil.copyfile(src, dst); shots.append(dst)
res["shots"] = shots
print(json.dumps(res, indent=1))
