"""HAZARD_CLOCK_INSPECT_LINES_1 A1/A2 live read, FOUNDRY 2026-10-10. python.exe from repo root.
Grey Sea surface map: a lit worklight-class lamp inspects as 'Burning steadily for <period>' after ProofBurn; an unlit
lamp shows nothing; RM_Skylight and GravEngine inspect strings printed for A2 (informational unless a well ledger entry exists)."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
P = lambda m, a="1": str((S.call("jawa/static_call", type="RimMandrake.TerminalBiomes.RM_GreyLampProof", method=m, args=a) or {}))[:500]
TILE = 114502
mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
try:
    print("biome", S.call("jawa/map_info").get("mapBiome"))
    sc = S.Scene("hazclock", 40, 60, 15, 9); sc.__enter__()
    sc.room(roof=True)
    x0, z0 = sc.abs(3, 4); x1, z1 = sc.abs(10, 4)
    print("build", S.call("jawa/build_batch", ops="SunLamp:%d,%d;SunLamp:%d,%d;Battery:%d,%d" % (x0, z0, x1, z1, x0 + 1, z0), faction="player").get("survived"))
    S.call("jawa/map_commit", full=True)
    lamps = S.call("jawa/list_things", defName="SunLamp", rect=sc.rect).get("things") or []
    print("lamps", len(lamps), [(l.get("id"), l.get("faction")) for l in lamps])
    on, off = lamps[0], lamps[1]
    print("power on", json.dumps(sc.power_on(on["id"], True), default=str)[:200])
    print("power off", json.dumps(sc.power_on(off["id"], False), default=str)[:200])
    print("BEFORE burn lit:", sc.inspect(on["id"])[:500])
    print("ProofBurn:", P("ProofBurn", "1"))
    print("AFTER lit  :", sc.inspect(on["id"])[:600])
    print("AFTER unlit:", sc.inspect(off["id"])[:600])
    sc.put("RM_Skylight", 7, 2)
    sk = sc.find("RM_Skylight"); print("SKYLIGHT:", sc.inspect(sk["id"])[:500] if sk else "none spawned")
finally:
    S.drop_map(mid, TILE, back=0)
