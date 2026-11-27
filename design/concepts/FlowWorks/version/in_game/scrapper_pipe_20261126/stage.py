"""Scrapper pipe close-zoom look (SCRAPPER_PIPE_REDRAW_BLURRY_AT_ZOOM A1): the review map's pipe_long_run station on the current
map: 26 straight RM_UniversalPipe cells styled Scrapper at z=123 over 26 styled Industrial at z=120 (x 100..125), built
beforehand. Sets the styles, commits, reads Patch_Pipe_StraightVariants.printed, captures close crops. python.exe, RM_REPO set."""
import json, os, shutil, sys, time
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
res = {"styled": {}, "failed": []}
def printed():
    r = O.call("jawa/read_paths", reads=json.dumps([{"of": "static:RimMandrake.FlowWorks.Machinery.Patch_Pipe_StraightVariants", "path": "printed"}]))
    v = (r.get("values") or [{}])[0]
    return v.get("v") if v.get("state") == "ok" else "UNREAD:" + str(r)[:200]
res["printed_before"] = printed()
things = O.call("jawa/list_things", rect="100,120,26,4", limit=400).get("things") or []
for t in things:
    if t.get("def") != "RM_UniversalPipe":
        continue
    lk = {123: "Scrapper", 120: "Industrial"}.get(t.get("z"))
    if not lk:
        continue
    r = O.call("jawa/set_thing_props", thing=str(t.get("id")), style="RM_UniversalPipe_" + lk)
    if r.get("success") is False:
        res["failed"].append((t.get("x"), t.get("z"), str(r)[:160]))
    else:
        res["styled"][lk] = res["styled"].get(lk, 0) + 1
res["commit"] = str(O.call("jawa/map_commit"))[:200]
time.sleep(1.0)
res["printed_after_commit"] = printed()
shots = []
for name, x, z, w, h in (("run_both_whole", 100, 120, 26, 4), ("scrapper_close_west", 102, 122, 6, 3), ("scrapper_close_mid", 110, 122, 6, 3),
                         ("industrial_close_mid", 110, 119, 6, 3)):
    fn = "scrapperpipe_%d_%s" % (int(time.time()), name)
    asked = time.time()
    r = O.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=0, fileName=fn, suppressMessage=True)
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
res["printed_end"] = printed()
print(json.dumps(res, indent=1))
