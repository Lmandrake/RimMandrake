"""L6 rerun discriminator (BENCH 2026-10-12): the L6 row and the 2026-10-11 probe both spawn a neutral villager and then tick
250-780 ticks; villagers with no lord WALK OFF (2026-10-11 probe: the NE witness spawned at (81,185) was at (73,200) when read),
so 'caught 0' cannot tell 'LOS blocked' from 'witness already gone'. Here the witness is spawned 2-3 ticks BEFORE the theft
check (RM_LiquidTheft.TheftTick runs at TicksGame % 250 == 7, right after SettleTick moves the Fill job's level), and its
position at the check is read back. Order: NE witness (the side the old Position-only aim could not see) first; SW only if
NE is not caught (a caught tank is never re-caught). Site: fw_live_checks L6 (foreign tank (77,181), our Fill tank north of
the reel at (63,182))."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH
B = PH.PB()
T = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
g = lambda f: B.call("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value")
tick = lambda: B.call("rimworld/get_game_info").get("ticksGame")
TANK, OURS = (77, 181), (63, 182)
out = {"tank": B.call("jawa/list_things", defName="RM_LiquidTank", rect="60,170,30,20", limit=5).get("things"),
       "sightRange": B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.Machinery.RM_MachinerySettings",
                            action="get", field="liquidTheftSightRange").get("value")}
fac = sys.argv[2] if len(sys.argv) > 2 else "OutlanderCivil"


def step_to(mod):
    t = tick()
    n = (mod - t % 250) % 250
    if n:
        B.ticks(n)
    return tick()


def run(label, x, z):
    B.hp("filltank:%d,%d=%s,100" % (TANK + (PH.LIQUID_WATER,)))
    B.hp("filltank:%d,%d=%s,0" % (OURS + (PH.LIQUID_WATER,)))
    step_to(8)                      # one check with the refill as baseline change (no witness yet)
    t_sp = step_to(4)
    w = B.call("jawa/spawn_pawn", kindDef="Villager", x=x, z=z, faction=fac, count=1)
    pid = (w.get("pawns") or [{}])[0].get("id")
    c0 = g("caught")
    t_chk = step_to(9)              # passes tick % 250 == 7
    c1 = g("caught")
    p = [q for q in (B.call("jawa/list_pawns", faction=fac, limit=20).get("pawns") or []) if q.get("id") == pid]
    units = [PH._tank(B, TANK).get("units"), PH._tank(B, OURS).get("units")]
    out[label] = {"spawnAt": [x, z], "spawnTick": t_sp, "checkTick": t_chk, "pid": pid, "caught": [c0, c1],
                  "witnessAtCheck": [{k: q.get(k) for k in ("x", "z", "downed", "dead")} for q in p], "units": units,
                  "spawn": w.get("success")}
    print(label, json.dumps(out[label]), flush=True)
    return str(c1) != str(c0)


hit = run("A_northeast", 81, 185)
if not hit:
    run("B_southwest", 73, 177)
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
