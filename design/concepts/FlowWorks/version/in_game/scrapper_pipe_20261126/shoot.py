"""Clear plants round the two pipe runs (huge Rot plants draw over them), then capture close crops at a fixed zoom."""
import json, os, shutil, sys, time
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
OUT, ROOT = sys.argv[1], float(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
res = {"failed": []}
res["destroy"] = str(O.call("jawa/destroy_batch", rects="88,108,50,28", categories="Plant"))[:200]
lt = O.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000).get("things") or []
near = [(t["x"], t["z"]) for t in lt if 80 <= t.get("x", -99) <= 145 and 100 <= t.get("z", -99) <= 140]
res["huge_blockers_near"] = near[:10]
O.call("jawa/map_commit")
r = O.call("jawa/read_paths", reads=json.dumps([{"of": "static:RimMandrake.FlowWorks.Machinery.Patch_Pipe_StraightVariants", "path": "printed"}]))
res["printed"] = (r.get("values") or [{}])[0].get("v")
shots = []
for name, x, z, w, h in (("both_runs", 100, 119, 26, 6), ("scrapper_west", 100, 122, 9, 3), ("scrapper_mid", 109, 122, 9, 3),
                         ("scrapper_east", 117, 122, 9, 3), ("industrial_mid", 109, 119, 9, 3)):
    fn = "scrapperpipe_%d_%s" % (int(time.time()), name)
    asked = time.time()
    r = O.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=0, fileName=fn, suppressMessage=True,
               rootSize=ROOT if name != "both_runs" else ROOT * 2.5)
    src, size = str(r.get("path") or ""), -1
    for _ in range(40):
        now = os.path.getsize(src) if src and os.path.isfile(src) else -1
        if now > 0 and now == size:
            break
        size = now
        time.sleep(0.4)
    if src and os.path.isfile(src) and os.path.getmtime(src) >= asked - 2:
        dst = os.path.join(OUT, name + ".png"); shutil.copyfile(src, dst); shots.append(dst)
    else:
        res["failed"].append((name, "no capture", str(r)[:200]))
res["shots"] = shots
print(json.dumps(res, indent=1))
