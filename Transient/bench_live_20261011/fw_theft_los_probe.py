"""Discriminate L6 (liquid theft never caught): is the witness's line of sight blocked by the 2x2 tank's OWN cells?
RM_LiquidTheft.Witness uses GenSight.LineOfSight(p.Position, tank.Position, map) -- the 3-arg overload ends at the
single Position cell, and RM_LiquidTank is 2x2 with fillPercent 1.0. Witness A stands NE (line crosses another tank
cell first); witness B stands on the side whose first tank cell is Position. Same site as fw_live_checks L6."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH
B = PH.PB()
T = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
g = lambda f: B.call("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value")
out = {}
tank = (77, 181)
lt = B.call("jawa/list_things", defName="RM_LiquidTank", rect="75,179,5,5", limit=5).get("things") or []
out["tank"] = lt
cells = B.call("rimworld/get_cell_info", x=76, z=180)
out["cell_76_180"] = [t.get("defName") for t in cells.get("things") or []]
cells2 = B.call("rimworld/get_cell_info", x=78, z=182)
out["cell_78_182"] = [t.get("defName") for t in cells2.get("things") or []]
def run(label, x, z):
    B.hp("filltank:%d,%d=%s,100" % (tank + (PH.LIQUID_WATER,)))
    w = B.call("jawa/spawn_pawn", kindDef="Villager", x=x, z=z, faction="OutlanderCivil", count=1)
    pid = (w.get("pawns") or [{}])[0]
    c0 = g("caught")
    B.ticks(260); B.ticks(260); B.ticks(260)
    c1 = g("caught")
    p = B.call("jawa/list_pawns", faction="OutlanderCivil", limit=10).get("pawns") or []
    out[label] = {"spawnAt": [x, z], "spawned": {k: pid.get(k) for k in ("id", "x", "z")}, "caught": [c0, c1],
                  "now": [{k: q.get(k) for k in ("id", "x", "z")} for q in p]}
    for q in p:
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (q.get("x"), q.get("z")), categories="Pawn")
    print(label, json.dumps(out[label])[:400], flush=True)
run("A_northeast_4", 81, 185)
run("B_southwest_4", 73, 177)
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("tank", "cell_76_180", "cell_78_182")}, default=str)[:600])
