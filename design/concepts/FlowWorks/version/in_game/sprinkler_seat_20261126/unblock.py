import json, os, sys
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
th = O.call("jawa/list_things", rect="96,126,50,12", limit=2000).get("things") or []
mine = {(t["x"], t["z"]) for t in th if t["def"].startswith(("RM_UniversalPipe", "RM_SprinklerHead", "RM_PipeFaucet"))}
blk = sorted({(t["x"], t["z"]) for t in th if t["def"] == "RM_HugeTrunkBlocker"})
done = []
for c in blk:
    if c in mine:
        done.append((c, "shares a cell with ours: left")); continue
    r = O.call("jawa/destroy_batch", rects="%d,%d,1,1" % c, categories="Building")
    done.append((c, (r.get("destroyed") if isinstance(r, dict) else r)))
print(json.dumps(done))
