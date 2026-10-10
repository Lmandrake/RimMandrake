"""BACTA_TANK_CORE_1 A1/A3/A4 L2 live read, FOUNDRY 2026-10-10. python.exe from repo root, ~3 min.
A1: tank heals a fresh cut while a missing kidney stays missing and a brain Crack changes no more than the same Crack on an identical pawn
    INSIDE a tank with healingEnabled=false (a pawn in a bed/tank heals faster than one standing, so an outside control is not a control).
A3: a permanent Cut (sev 1.0, action=permanent) is erased in the time its rate predicts (scarHealPerDay raised 10x to 24 for speed; shipped 2.4).
A4: fluid falls while used; at zero the pawn is ejected and a new pawn is refused.
Prints 'RESULT <crit> <PASS|FAIL|UNMEASURED> detail'."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
TILE = 114502
ST = "RimMandrake.StarWars.Bacta.BactaSettings"
def R(c, v, d=""): print("RESULT %s %s %s" % (c, v, d), flush=True)
def hed(sc, pid):
    pg = ((sc.pawn_state(pid) or {}).get("pawns") or [{}])[0]
    return {(h.get("def"), h.get("part")): h.get("severity") for h in pg.get("hediffs", [])}
def fuel(tid): return S.call("jawa/thing_refuel", thingId=tid, amount=0).get("fuelAfter")
def hd(pid, d, part, sev): return S.call("jawa/pawn_health", pawn=pid, action="add", hediff=d, bodyPart=part, severity=sev)
def contained(tid):
    v = (S.call("jawa/comp_read", thing=tid, comp="Immersion", members="workedLastPass").get("values") or {})
    return v
def enter(sc, pid, tid):
    return sc.order(pid, "EnterBuilding", a=tid, wait=300)
def hostile_count(): 
    return sum(1 for p in (S.call("jawa/list_pawns").get("pawns") or []) if p.get("hostile"))
def calm(): S.call("jawa/kill_hostiles"); S.call("jawa/set_game_speed", speed=0)
S.call("jawa/set_game_speed", speed=0)
def hostile_count():
    return sum(1 for p in (S.call("jawa/list_pawns").get("pawns") or []) if p.get("hostile"))
def calm(): S.call("jawa/kill_hostiles"); S.call("jawa/set_game_speed", speed=0)
S.call("jawa/set_game_speed", speed=0)
mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
try:
    sc = S.Scene("bacta", 40, 60, 16, 9); sc.__enter__(); sc.room(roof=True)
    for dx in (3, 6, 9, 12): sc.put("RSW_BactaTank", dx, 3, rot=2)
    sc.put("Battery", 14, 7); S.call("jawa/map_commit", full=True)
    tanks = sorted((S.call("jawa/list_things", defName="RSW_BactaTank", rect=sc.rect).get("things") or []), key=lambda t: t["x"])
    assert len(tanks) == 4, tanks
    for t in tanks:
        sc.power_on(t["id"], True); S.call("jawa/thing_refuel", thingId=t["id"], amount=30)
    t1, t2, t3, t4 = [t["id"] for t in tanks]
    def injured(dx, dz):
        p = sc.colonist(dx, dz); S.call("jawa/pawn_need", pawn=p, action="need", need="Mood", level=1.0)
        hd(p, "MissingBodyPart", "Kidney", 1); hd(p, "Cut", "Arm", 4); hd(p, "Crack", "Brain", 2); return p
    p1 = injured(1, 6)
    p2 = sc.colonist(2, 7); S.call("jawa/pawn_need", pawn=p2, action="need", need="Mood", level=1.0)
    hd(p2, "Cut", "Arm", 1.0); S.call("jawa/pawn_health", pawn=p2, action="permanent", hediff="Cut")
    calm(); b1, b2 = hed(sc, p1), hed(sc, p2); print("BEFORE p1", b1, "p2", b2, flush=True)
    # phase 1: SAME pawn, tank healing OFF (natural-rate baseline inside the tank)
    with S.setting(ST, healingEnabled="False"):
        enter(sc, p1, t1); S.run(900); print("p1 inside:", sc.inspect(t1)[-90:], flush=True)
        m1 = hed(sc, p1); S.run(1500); calm()
    off = hed(sc, p1); print("p1 healing-off 900->2400", m1, off, flush=True)
    # phase 2: healing ON, same pawn same tank, same duration; plus the A3 scar pawn
    enter(sc, p2, t3); S.run(300)
    with S.setting(ST, scarHealPerDay=24):
        S.run(1200); calm(); m2 = hed(sc, p2); a1 = hed(sc, p1); print("p2@1500", m2, "p1 healing-on", a1, flush=True)
        S.run(1800); calm(); e2 = hed(sc, p2); print("p2@3300", e2, flush=True)
    kid = ("MissingBodyPart", "Kidney") in a1
    g = lambda d, k: d.get(k, 0)
    cut_on = g(off, ("Cut", "Arm")) - g(a1, ("Cut", "Arm")); cut_off = g(m1, ("Cut", "Arm")) - g(off, ("Cut", "Arm"))
    br_on = g(off, ("Crack", "Brain")) - g(a1, ("Crack", "Brain")); br_off = g(m1, ("Crack", "Brain")) - g(off, ("Crack", "Brain"))
    clean = all(d[0] != "Gunshot" or d[1] == "Leg" for d in list(a1) + list(off))
    ok = kid and cut_on > 3 * max(cut_off, 0.01) and br_on <= br_off * 1.5 + 0.05
    R("BACTA_TANK_CORE_1/A1", ("PASS" if ok else "FAIL") if clean else "UNMEASURED", "clean=%s kidney_still_missing=%s same-pawn per-1500t: cut_heal on=%.2f off=%.2f ; brain_drop on=%.2f off=%.2f" % (clean, kid, cut_on, cut_off, br_on, br_off))
    sev0 = b2.get(("Cut", "Arm")); sevm = m2.get(("Cut", "Arm")); sevn = e2.get(("Cut", "Arm"))
    R("BACTA_TANK_CORE_1/A3", "PASS" if (sev0 and sevm is not None and sevm < sev0 and sevn is None) else "FAIL", "permanent cut %s -> %s(@1500) -> %s(@3300); rate 24/day predicts ~%d ticks" % (sev0, sevm, sevn, int(sev0 / 24 * 60000) if sev0 else -1))
    f3a = fuel(t4)
    p4 = sc.colonist(10, 6); S.call("jawa/pawn_need", pawn=p4, action="need", need="Mood", level=1.0); hd(p4, "Cut", "Arm", 5); hd(p4, "Cut", "Leg", 5)
    with S.setting(ST, fluidCostPerDay=3000):
        enter(sc, p4, t4); S.run(300); fa = fuel(t4); S.run(1500); calm(); fb = fuel(t4)
        ins = sc.inspect(t4); print("t4 inspect", ins[-200:], flush=True)
        p5 = sc.colonist(11, 6); hd(p5, "Cut", "Arm", 3); enter(sc, p5, t4); S.run(300)
        ins5 = sc.inspect(t4); print("t4 after 2nd pawn", ins5[-200:], flush=True)
    R("BACTA_TANK_CORE_1/A4", "PASS" if (f3a > fb and fb <= 0.01 and "Immers" not in ins5) else "FAIL",
      "fuel %s -> %s(@300) -> %s(@1800); second pawn refused at zero: %s" % (f3a, fa, fb, "Immers" not in ins5))
finally:
    calm()
    try: sc.teardown()
    except Exception as e: print("teardown", e)
    S.drop_map(mid, TILE, back=0)
