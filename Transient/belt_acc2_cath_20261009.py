import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def mech(x, z):
    r = S.call("jawa/spawn_pawn", kindDef="Mech_Lancer", x=x, z=z, faction="Pirate", count=1)
    return (r.get("pawns") or [{}])[0].get("id"), str(r.get("message"))[:80]
def hostile(pid):
    ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
    for p in ps:
        if p["id"] == pid: return p.get("hostile")
S.call("jawa/site_state", storyteller="off", clearIncidentQueue=True)
res = {}
# A: off-cathedral (current quicktest map)
mi = S.call("jawa/map_info"); res["offmap_biome"] = mi.get("mapBiome")
pid, m = mech(30, 30); res["off_spawn"] = (pid, m)
res["off_before"] = hostile(pid)
h = S.call("jawa/pawn_health", pawn=pid, action="add", hediff="RUT_CathedralPass", severity=1.0); res["off_hediff"] = (h.get("success"), str(h.get("message"))[:80])
res["off_after"] = hostile(pid)
S.call("jawa/damage", damageDef="Bomb", amount=2000, thingId=pid, allowColonists=True)
print(json.dumps(res, default=str), flush=True)
# B: cathedral map
mid = S.biome_map(114480, "RM_RustCathedral", size=80, keeper=(5, 5))
try:
    S.call("jawa/site_state", storyteller="off", clearIncidentQueue=True)
    mi = S.call("jawa/map_info"); res["cath_biome"] = mi.get("mapBiome")
    pid, m = mech(40, 40); res["cath_spawn"] = (pid, m)
    res["cath_before"] = hostile(pid)
    h = S.call("jawa/pawn_health", pawn=pid, action="add", hediff="RUT_CathedralPass", severity=1.0); res["cath_hediff"] = (h.get("success"), str(h.get("message"))[:80])
    res["cath_after"] = hostile(pid)
    S.call("jawa/pawn_health", pawn=pid, action="remove", hediff="RUT_CathedralPass")
    res["cath_removed"] = hostile(pid)
finally:
    S.drop_map(mid, 114480)
print(json.dumps(res, default=str))
