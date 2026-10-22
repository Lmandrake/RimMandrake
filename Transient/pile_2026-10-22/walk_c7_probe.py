"""Scratch probe for walk stop 6 (C7 ponds): python.exe Transient/pile_2026-10-22/walk_c7_probe.py <cmd> [...]
cmds: hp:<hose probe cmd>  call:<tool>:<json kw>  ticks:<n>  water  (reads both ponds' dL and the reels' Levelling lines)"""
import sys, os, json
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation_core as V
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
B = V.Bridge()
B.probe_type = "RimMandrake.FlowWorks.Hose.HoseProbe"
OX, OZ = 12, 112
def static(t, m, a):
    r = B.call("jawa/static_call", type=t, method=m, args=a); return r.get("result") or r
for a in sys.argv[1:]:
    if a.startswith("hp:"):
        print(a, json.dumps(B.probe(a[3:]))[:900])
    elif a.startswith("call:"):
        _, tool, kw = a.split(":", 2)
        print(tool, json.dumps(B.call(tool, **json.loads(kw)))[:1500])
    elif a.startswith("shot:"):
        nm, r = a[5:].split("=")
        x, z, w, h = [int(v) for v in r.split(",")]
        B.call("jawa/clear_ui", all=True)
        B.call("rimworld/set_camera_zoom", rootSize=max(h / 2.0 + 2, w / 3.5 + 2))
        res = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1, fileName=nm, suppressMessage=True)
        import shutil
        src = res.get("path") or res.get("filePath")
        dst = os.path.join(REPO, "Transient", "pile_2026-10-22", "walk_preview", nm + ".png")
        shutil.copyfile(src, dst) if src else None
        print("shot", nm, src and dst, "" if src else json.dumps(res)[:200])
    elif a == "hugeclear":
        print("hugeclear", V.clear_huge_plants(B))
    elif a == "pawns":
        for q in B.call("jawa/list_pawns").get("pawns") or []:
            if not q.get("isPlayer") or q.get("dead") or q.get("downed"):
                print(q.get("id"), q.get("kindDef"), q.get("factionName"), q.get("x"), q.get("z"), "hostile" if q.get("hostile") else "",
                      "DEAD" if q.get("dead") else "", "DOWNED" if q.get("downed") else "")
    elif a.startswith("role:"):
        print(a, static(LPROOF, "ProofHoseRole", a[5:]))
    elif a.startswith("ticks:"):
        print(B.ticks(int(a[6:])))
    elif a == "water":
        for nm, (x, z) in (("HIGH", (1, 22)), ("LOW", (1, 14))):
            print(nm, json.dumps(static(LPROOF, "ProofPitWater", "%d,%d,4,4" % (OX + x, OZ + z)))[:300])
        for nm, (x, z) in (("reelHIGH", (11, 22)), ("reelLOW", (11, 15))):
            lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,1" % (OX + x, OZ + z), limit=1)
            rid = ((lt.get("things") or [{}])[0]).get("id")
            ins = B.call("jawa/inspect_string", thingIds=str(rid)) if rid else {}
            print(nm, rid, [ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])][:12])
