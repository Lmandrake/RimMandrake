"""BACTA_TANK_CORE_1 A1 (brain + missing organ half), FOUNDRY 2026-10-10. python.exe from repo root, ~3 min.
Same pawn, same tank, brain-only injuries (all other hediffs removed so natural healing has nothing else to target - vanilla heals injuries
one at a time, which confounded l2_bacta_20261010.py): Crack on Brain + MissingBodyPart Kidney. Phase OFF = tank healingEnabled false, phase ON =
healing true (autoEject off so the tank keeps the pawn with nothing to heal). Per-1500-tick brain change must match; kidney must stay missing.
Prints 'RESULT BACTA_TANK_CORE_1/A1b <PASS|FAIL|UNMEASURED> detail'."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
TILE = 114502; ST = "RimMandrake.StarWars.Bacta.BactaSettings"
def hed(sc, pid):
    pg = ((sc.pawn_state(pid) or {}).get("pawns") or [{}])[0]
    return {(h.get("def"), h.get("part")): h.get("severity") for h in pg.get("hediffs", [])}
def calm(): S.call("jawa/kill_hostiles"); S.call("jawa/set_game_speed", speed=0)
S.call("jawa/set_game_speed", speed=0)
mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
try:
    sc = S.Scene("bactab", 40, 60, 8, 9); sc.__enter__(); sc.room(roof=True)
    sc.put("RSW_BactaTank", 3, 3, rot=2); sc.put("Battery", 6, 7); S.call("jawa/map_commit", full=True)
    t = sc.find("RSW_BactaTank")["id"]; sc.power_on(t, True); S.call("jawa/thing_refuel", thingId=t, amount=30)
    p = sc.colonist(1, 6); S.call("jawa/pawn_need", pawn=p, action="need", need="Mood", level=1.0)
    for (d, part), sev in list(hed(sc, p).items()):
        S.call("jawa/pawn_health", pawn=p, action="remove", hediff=d, bodyPart=part or "")
    S.call("jawa/pawn_health", pawn=p, action="add", hediff="MissingBodyPart", bodyPart="Kidney", severity=1)
    S.call("jawa/pawn_health", pawn=p, action="add", hediff="Crack", bodyPart="Brain", severity=3)
    calm(); h0 = hed(sc, p); print("START", h0, flush=True)
    with S.setting(ST, autoEjectEnabled="False", healingEnabled="False"):
        sc.order(p, "EnterBuilding", a=t, wait=300); S.run(900); calm(); h1 = hed(sc, p); print("inside:", sc.inspect(t)[-120:], flush=True)
        S.run(1500); calm(); h2 = hed(sc, p); print("OFF  900->2400", h1, h2, flush=True)
    with S.setting(ST, autoEjectEnabled="False", healingEnabled="True"):
        S.run(1500); calm(); h3 = hed(sc, p); print("ON  2400->3900", h3, "|", sc.inspect(t)[-120:], flush=True)
    g = lambda d: d.get(("Crack", "Brain"))
    off, on = g(h1) - g(h2), g(h2) - g(h3)
    kid = ("MissingBodyPart", "Kidney") in h3 and h3[("MissingBodyPart", "Kidney")] == 1.0
    ok = kid and abs(on - off) <= max(0.05, 0.5 * off)
    clean = all(k[0] != "Gunshot" for k in h3)
    print("RESULT BACTA_TANK_CORE_1/A1b %s kidney_still_missing=%s brain per-1500t: off=%.3f on=%.3f" % ((("PASS" if ok else "FAIL") if clean and off > 0 else "UNMEASURED"), kid, off, on), flush=True)
finally:
    calm()
    try: sc.teardown()
    except Exception as e: print("teardown", e)
    S.drop_map(mid, TILE, back=0)
