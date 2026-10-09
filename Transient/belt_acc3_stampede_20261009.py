import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
try:
    old = int(open("Transient/belt_acc3_ls_map_id.txt").read()); S.drop_map(old, 114480)
except Exception as e: print("drop", e)
S.call("jawa/world_tile_set", tiles="114480", biome="RM_LongShade", temperature=45); S.call("jawa/world_commit")
try:
    mid = S.biome_map(114480, "RM_LongShade", size=100, keeper=(30, 30))
    open("Transient/belt_acc3_ls_map_id.txt", "w").write(str(mid))
    S.quiet()
    clk = S.call("jawa/time_clock"); hr = S.call("jawa/glow_at", cells="50,50").get("hour") or 0
    S.call("jawa/time_set_ticks", ticks=int(clk["ticksGame"] + ((13 - hr) % 24) * 2500))
    print("outdoor", S.call("jawa/map_info").get("outdoorTempNow"), flush=True)
    with S.Scene("stampede", 20, 20, 9, 9) as sc:
        sc.room(roof=True)
        sc.colonist(4, 4)
        print("home", {k:v for k,v in S.call("jawa/paint_area", area="home", ops="18,18,13,13").items() if k in ("setCount","failedVerify","requested","success","message","trueCount","areaTrueCount")}, flush=True)
        r = S.call("jawa/spawn_pawn", kindDef="Caribou", x=60, z=60, faction="none", count=8); print("spawn", r.get("success"), r.get("spawnedCount"), str(r.get("message"))[:100], flush=True)
        print("hw", S.call("jawa/game_condition", action="start", condition="HeatWave", durationTicks=30000).get("success"), flush=True)
        S.call("rimworld/step_game_ticks", ticks=180)
        print("outdoor", S.call("jawa/map_info").get("outdoorTempNow"), flush=True)
        print("caribou", json.dumps(S.call("jawa/animal_stats", defs="Caribou", extraStats="ComfyTemperatureMax").get("animals"),default=str)[:300])
        ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
        rn = [p for p in ps if p["kind"] == "Caribou"]; print("runyip", len(rn))
        if rn: print("ambient", S.call("jawa/thing_ambient_temp", thing=rn[0]["id"]))
        fi = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", dryRun=True); print("dry on", fi.get("canFireNow"), str(fi.get("message"))[:200], flush=True)
        with S.setting("RimMandrake.LongShade.RM_LongShadeSettings", stampedeEnabled=False):
            fo = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", dryRun=True); print("dry off", fo.get("canFireNow"), flush=True)
        if fi.get("canFireNow"):
            f = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", forced=True); print("fire", f.get("success"), f.get("fired"), str(f.get("message"))[:200], flush=True)
            S.run(60)
            L = S.call("rimworld/list_letters", limit=5); print("letters", str(L)[:500])
            ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
            for p in [p for p in ps if p["kind"] == "Caribou"][:3]:
                pg = (S.call("jawa/pawn_get", pawn=p["id"]).get("pawns") or [{}])[0]; print(p["id"], pg.get("curJob") or pg.get("job"), p["x"], p["z"])
finally:
    S.call("jawa/world_tile_set", tiles="114480", temperature=-0.95); S.call("jawa/world_commit")
