"""python.exe, bridge held (ArchSmall, small list): visit 9, staged form. KINDS=<PawnKinds>: each set down hungry 6 cells from
the patches. GROWTH=<start growth>. RING=1 puts the row's steel ring round them. See graze_read.py for the unstaged read. Stages the
row's three patches as sown (16 seedlings each at 0.05, water beside one, no ring), then reads, every 100 ticks of 4,000, each
plant's id and growth and every pawn within 8 cells with its job. A seedling that goes is named with the pawns by it. Also
reads GrowthRate (the patched getter) of each patch at the start. Nothing is fenced, spawned or held but the mod's fires."""
import json, os, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
T = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
X, Z = 160, 225
P = {"dry": (X - 9, Z - 2, 4, 4), "watered": (X - 2, Z - 2, 4, 4), "vanilla": (X + 5, Z - 2, 4, 4)}
rs = lambda r: "%d,%d,%d,%d" % tuple(r)  # noqa: E731
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    print("game", c("rimworld/get_game_info").get("ticksGame"))
    for f in ("burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled", "furnaceThermalEnabled"):
        c("jawa/mod_settings_field", typeName=T, action="set", field=f, value="False")
    try:
        c("jawa/clear_area", rect="%d,%d,24,24" % (X - 12, Z - 12), dryRun=False)
        for r in ((X - 13, Z - 6, 26, 12),):
            c("jawa/set_terrain", x=r[0], z=r[1], terrainDef="Concrete", width=r[2], height=r[3], layer="top")
        for k, r in P.items():
            c("jawa/set_terrain", x=r[0], z=r[1], terrainDef="RM_FE_Ash_Deep", width=4, height=4, layer="top")
        c("jawa/set_terrain", x=X - 3, z=Z - 2, terrainDef="WaterShallow", width=1, height=4, layer="top")
        c("jawa/safe_advance", ticks=2600)
        for k, r in P.items():
            c("jawa/set_plants", ops="%s:%s" % ("Plant_Grass" if k == "vanilla" else "RM_FE_Plant_EmberGrass", rs(r)), growth=float(os.environ.get("GROWTH") or 0.05))
        if os.environ.get("RING") == "1":
            ring = [(x, z) for x in range(X - 10, X + 10) for z in range(Z - 3, Z + 3) if x in (X - 10, X + 9) or z in (Z - 3, Z + 2)]
            c("jawa/build_batch", ops=";".join("Wall:%d,%d" % q for q in ring), stuff="Steel")
        for i, kd in enumerate([k for k in (os.environ.get("KINDS") or "").split(",") if k]):
            sp = c("jawa/spawn_pawn", kindDef=kd, x=X - 8 + i * 4, z=Z - 9, faction="none", count=1)
            for q in c("jawa/list_pawns", rect="%d,%d,42,24" % (X - 21, Z - 12), limit=200).get("pawns") or []:
                if q.get("kindDef") == kd:
                    print("grazer", kd, q["id"], str(c("jawa/pawn_need", pawn=q["id"], action="need", need="Food", level=0.08))[:160])
        def plants():
            out = {}
            for k, r in P.items():
                rows = c("jawa/thing_read", rect=rs(r), members="Growth,GrowthRate,def").get("rows") or []
                out[k] = {q["id"]: (q["x"], q["z"], (q.get("values") or {}).get("Growth"), (q.get("values") or {}).get("GrowthRate"))
                          for q in rows if "Plant" in str(q.get("defName"))}
            return out
        a = plants()
        print("START", {k: (len(v), sorted(v.values())[:2]) for k, v in a.items()})
        kinds = {}
        for i in range(int(os.environ.get('STEPS') or 25)):
            r = c("jawa/safe_advance", ticks=100)
            b = plants()
            near = [q for q in c("jawa/list_pawns", rect="%d,%d,42,24" % (X - 21, Z - 12), limit=200).get("pawns") or [] if not q.get("isPlayer")]
            jobs = {}
            if near:
                for q in near:
                    rr = (c("jawa/thing_read", thingIds=str(q["id"]), members="CurJobDef").get("rows") or [{}])[0]
                    jobs[q["id"]] = (q.get("kindDef"), q.get("x"), q.get("z"), str((rr.get("values") or {}).get("CurJobDef"))[:40])
                    kinds[q.get("kindDef")] = kinds.get(q.get("kindDef"), 0) + 1
            gone = {k: [a[k][i2] for i2 in a[k] if i2 not in b[k]] for k in P}
            came = {k: len([i2 for i2 in b[k] if i2 not in a[k]]) for k in P}
            if any(gone.values()) or any(came.values()):
                print("t+%d" % ((i + 1) * 100), "GONE", {k: v for k, v in gone.items() if v}, "CAME", came, "NEAR", list(jobs.values()))
            fell = {k: [(a[k][q][2], b[k][q][2]) for q in a[k] if q in b[k] and float(b[k][q][2]) < float(a[k][q][2]) - 0.001] for k in P}
            if any(fell.values()):
                print("t+%d" % ((i + 1) * 100), "FELL", {k: v for k, v in fell.items() if v}, "NEAR", list(jobs.values()))
            a = b
        print("END counts", {k: len(v) for k, v in a.items()}, "growth", {k: sorted(v.values())[:1] for k, v in a.items()}, "pawn-samples within the box", kinds)
    finally:
        for f in ("burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled", "furnaceThermalEnabled"):
            c("jawa/mod_settings_field", typeName=T, action="set", field=f, value="True")
