"""bridge4 acceptance checks, full list. Run under python.exe from the repo root: python.exe Transient/belt_bridge4_checks_20261009i.py <phase>
phases: start | defs | maps | shokk | creep"""
import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S

def show(tag, r, n=900):
    print(tag, "|", (r if isinstance(r, str) else json.dumps(r, default=str))[:n]); sys.stdout.flush()

PORTS = ["RM_Radyak", "RM_Thermadon", "RM_Agaripawn", "RM_Agaripod", "RM_MycoidColossus", "RM_DecayDrake", "RM_RipperHound"]
CAST = {"RM_Cauldron": ["RM_Radyak", "RM_DecayDrake"], "RM_Miasma": ["RM_Thermadon", "RM_DecayDrake"],
        "RM_TheRot": ["RM_Agaripawn", "RM_Agaripod", "RM_MycoidColossus"]}
ph = sys.argv[1]

if ph == "start":
    r = S.rbc().call("rimworld/start_debug_game_ready", {"timeoutMs": 300000}, check=False); show("start", r, 400)
    for i in range(60):
        g = json.dumps(S.call("rimworld/get_game_info"), default=str)
        if '"Playing"' in g: break
        time.sleep(5)
    show("state", g, 300)

if ph == "defs":
    for kind in ("ThingDef", "PawnKindDef"):
        r = S.call("jawa/get_defs", defs=";".join(kind + "/" + p for p in PORTS), fields="defName;label")
        show("DEFS " + kind, {k: r.get(k) for k in ("success", "foundCount", "notFound")})
    r = S.call("jawa/get_defs", defs="ThingDef/RM_OssrithCrystal;ThingDef/RM_FermentedMound;AbilityDef/RM_DuskfireSpit;RecipeDef/RM_RefineOssrithCrystal", fields="defName")
    show("DEFS extras", {k: r.get(k) for k in ("success", "foundCount", "notFound")})
    for p in PORTS:
        r = S.call("jawa/get_defs", defs="PawnKindDef/" + p, fields="lifeStages", deep=True)
        txt = json.dumps(r, default=str)
        import re
        show("TEX " + p, sorted(set(re.findall(r'"texPath": "([^"]+)"', txt))), 400)
    for b, cast in CAST.items():
        r = S.call("jawa/get_defs", defs="BiomeDef/" + b, fields="wildAnimals", deep=True)
        txt = json.dumps(r, default=str)
        show("ROSTER " + b, {c: (c in txt) for c in cast} | {"success": r.get("success"), "len": len(txt)})

if ph == "maps":
    S.quiet()
    for b, cast in CAST.items():
        t0 = time.time()
        try:
            mid = S.biome_map(114480, b, size=100, keeper=(5, 5))
        except Exception as e:
            show("MAP " + b, "FAILED " + str(e)); continue
        def kinds():
            ps = S.call("jawa/list_pawns", limit=500).get("pawns") or []
            return [(p.get("kindDef") or p.get("def")) for p in ps], ps
        ks, _ = kinds()
        nat = {c: ks.count(c) for c in cast}
        nat["_total"] = len(ks)
        show("MAP %s mid=%s %.0fs natural" % (b, mid, time.time() - t0), nat)
        sp = {}
        for i, c in enumerate(cast):
            r = S.call("jawa/spawn_pawn", kindDef=c, x=20 + 6 * i, z=20, faction="none", count=1)
            sp[c] = r.get("success")
        S.run(300)
        ks, ps = kinds()
        alive = {c: ks.count(c) for c in cast}
        sample = [p for p in ps if (p.get("kindDef") or p.get("def")) in cast][:2]
        show("SPAWN " + b, {"spawn_ok": sp, "count_after300": alive, "sample": sample}, 1500)
        S.drop_map(mid, 114480)

if ph == "shokk":
    S.quiet()
    W = "RimMandrake.Webwork.RM_WebworkProof"
    for a in ("true;RM_Webwork_Anchor;34", "false;RM_Webwork_Anchor;0"):
        show("WEB " + a, S.call("jawa/static_call", type=W, method="ProofHarvest", args=a))

if ph == "creep":
    S.quiet()
    pawns = S.call("jawa/list_pawns", faction="player").get("pawns") or []
    pos = pawns[0].get("position") if pawns else None
    show("colonist", pos)
    x, z = (int(pos["x"]) + 6, int(pos["z"]) + 6) if isinstance(pos, dict) else (60, 60)
    show("spawn", S.call("jawa/spawn_batch", ops="RUT_DyingCreep:%d,%d" % (x, z)))
    t = S.ticks()
    for i in range(10):
        dc = len(S.call("jawa/list_things", defName="RUT_DyingCreep").get("things") or [])
        dd = len(S.call("jawa/list_things", defName="RUT_DeadCreep").get("things") or [])
        show("CREEP t+%d" % (S.ticks() - t), {"dying": dc, "dead": dd})
        if i < 9: S.run(2500)
