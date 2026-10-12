"""fw_theft_day2 went UNMEASURED: colonist Cait's Tantrum (letter tick 126799) destroyed OUR Fill tank (63,182) ~59,000 ticks
after the catch, so the foreign tank stopped being touched just short of a day. Rebuild our tank, set Fill, draft every
colonist, and keep their tank touched; read goodwill each 4000 ticks until goodwillCharged moves (day4: refill every 2000 ticks, cap 34 rounds; day3 refilled every 4000 so a round was only ~10 of 16 cycles touched)."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH
B = PH.PB()
T = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
g = lambda f: B.call("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value")
TANK, OURS = (77, 181), (63, 182)
tick = lambda: B.call("rimworld/get_game_info").get("ticksGame")
def gw():
    for f in B.call("jawa/list_factions").get("factions") or []:
        if f.get("defName") == "OutlanderCivil":
            return f.get("goodwill")
out = {"drafted": [p["id"] for p in (B.hp("colonists").get("pawns") or []) if B.hp("pawn:%d=draft" % p["id"]).get("success")]}
out["build"] = B.call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % OURS, faction="player", wipeExisting=False).get("success")
B.ticks(2)
B.call("rimworld/set_god_mode", enabled=True)
B.call("rimworld/clear_selection"); B.call("rimworld/click_cell", x=OURS[0], z=OURS[1])
lab = None
for _ in range(5):
    gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
    q = next((x for x in gz if str(x.get("label") or "").startswith("Job:")), None)
    lab = q and q.get("label")
    if q is None or lab == "Job: Fill":
        break
    B.call("rimworld/execute_gizmo", gizmoId=q.get("gizmoId") or q.get("id"))
B.call("rimworld/set_god_mode", enabled=False); B.call("rimworld/clear_selection")
out["job"] = lab
out.update(t0=tick(), gw0=gw(), gc0=g("goodwillCharged"), charges0=g("charges"), caught=g("caught"))
trace = []
for i in range(34):
    B.hp("filltank:%d,%d=%s,100" % (TANK + (PH.LIQUID_WATER,)))
    B.hp("filltank:%d,%d=%s,0" % (OURS + (PH.LIQUID_WATER,)))
    for _ in range(2):
        B.ticks(1000)
    trace.append({"tick": tick(), "units": [PH._tank(B, TANK).get("units"), PH._tank(B, OURS).get("units")], "gw": gw(),
                  "gc": g("goodwillCharged")})
    print(json.dumps(trace[-1]), flush=True)
    if str(trace[-1]["gc"]) != str(out["gc0"]):
        break
out["trace"] = trace
out.update(gw1=gw(), gc1=g("goodwillCharged"), charges1=g("charges"))
out["pass"] = (out["gw1"] is not None and out["gw0"] is not None and out["gw1"] < out["gw0"]
               and int(out["gc1"]) - int(out["gc0"]) <= -2)
print(json.dumps({k: v for k, v in out.items() if k != "trace"}, default=str))
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
