"""Live art look helper (BENCH, 2026-10-22). python.exe Transient/pile_2026-10-22/live_art_look/look.py <cmd> ...
cmds: tools:<substr>  call:<tool>:<json>  hp:<hose probe cmd>  find:<defsubstr>  shot:<name>=x,z,w,h[@root]"""
import sys, os, json, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
B.probe_type = "RimMandrake.FlowWorks.Hose.HoseProbe"
OUT = os.path.join(REPO, "Transient", "pile_2026-10-22", "live_art_look")
for a in sys.argv[1:]:
    if a.startswith("tools:"):
        names = sorted(t.get("name") if isinstance(t, dict) else str(t) for t in B.S.list_tools())
        print([n for n in names if a[6:] in n])
    elif a.startswith("hp:"):
        print(a, json.dumps(B.probe(a[3:]))[:3000])
    elif a.startswith("call:"):
        _, tool, kw = a.split(":", 2)
        print(tool, json.dumps(B.call(tool, **json.loads(kw)))[:4000])
    elif a.startswith("shot:"):
        nm, r = a[5:].split("=")
        root = None
        if "@" in r:
            r, root = r.split("@"); root = float(root)
        x, z, w, h = [int(v) for v in r.split(",")]
        B.call("jawa/clear_ui", all=True)
        B.call("rimworld/set_camera_zoom", rootSize=root or max(h / 2.0 + 2, w / 3.5 + 2))
        res = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1, fileName=nm, suppressMessage=True)
        src = res.get("path") or res.get("filePath")
        dst = os.path.join(OUT, nm + ".png")
        if src:
            shutil.copyfile(src, dst)
        print("shot", nm, dst if src else json.dumps(res)[:300])
    elif a.startswith("schema:"):
        for t in B.S.list_tools():
            if isinstance(t, dict) and t.get("name") == a[7:]:
                print(t["name"], t["description"][:500]); [print("   ", k, str(v)[:220]) for k, v in t["inputSchema"]["properties"].items()]
    elif a.startswith("census:"):
        for r in a[7:].split(";"):
            d = B.call("jawa/list_things", rect=r, group="BuildingArtificial")
            p = B.call("jawa/list_things", rect=r)
            print(r, "buildings", len(d.get("things") or []), "all", len(p.get("things") or []), sorted(set(t["def"] for t in p.get("things") or []))[:12])
