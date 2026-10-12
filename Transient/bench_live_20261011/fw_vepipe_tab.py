"""FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES A2 on the flowworks_vepipe tier (FlowWorks + Vanilla Chemfuel Expanded):
the "pipe networks" tab lists FlowWorks' pipe, tanks, hose reel and adapters beside VE's; Player.log has no duplicate-def
error for VCHE_PipeNetworks.   python.exe Transient/bench_live_20261011/fw_vepipe_tab.py <out.json>   (HEAD export root)"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
import validation_core as VC  # noqa: E402

B = VC.Bridge()
out = {}
rm = B.call("jawa/running_mods", details=False)
out["running"] = len(rm.get("packageIds") or [])
out["vchemfuel"] = any("vchemfuele" in p.lower() for p in rm.get("packageIds") or [])
cats = (B.call("rimworld/list_architect_categories") or {}).get("categories") or []
pipe = [c for c in cats if "pipe" in json.dumps(c).lower()]
out["pipeCategories"] = pipe
items = []
for c in pipe:
    lst = (B.call("rimworld/list_architect_designators", categoryId=c.get("id")) or {}).get("designators") or []
    items += [{"cat": c.get("id"), "id": d.get("id"), "label": d.get("label")} for d in lst]
out["designators"] = items
blob = json.dumps(items).lower()
want = {"pipe": "rm-universalpipe" in blob or "universal pipe" in blob,
        "tank": "rm-liquidtank" in blob or "liquid tank" in blob,
        "reel": "hosereel" in blob or "hose reel" in blob,
        "ve": "chemfuel" in blob}
out["found"] = want
log = open(r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log", encoding="utf-8", errors="replace").read()
dup = [l for l in log.splitlines() if "VCHE_PipeNetworks" in l and re.search(r"(?i)error|duplicate|same name|already", l)]
out["dupLines"] = dup[:10]
out["adapterLike"] = [i for i in items if "adapter" in json.dumps(i).lower()]
out["status"] = "PASS" if len(pipe) == 1 and all(want.values()) and not dup else ("UNMEASURED" if not out["vchemfuel"] else "FAIL")
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(out["status"], json.dumps({k: out[k] for k in ("running", "found", "dupLines")})[:600],
      "categories:", [c.get("id") for c in pipe], "n=", len(items))
