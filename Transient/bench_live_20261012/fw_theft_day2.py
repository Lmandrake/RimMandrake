"""After fw_theft_los_probe2 caught the theft: the letter, then one in-game day with the foreign tank touched every 4000 ticks;
goodwill must fall by >= liquidTheftGoodwillPerDay (fw_live_checks L6_goodwill_after_a_day's bar)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH
B = PH.PB()
T = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
g = lambda f: B.call("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value")
TANK, OURS = (77, 181), (63, 182)
def gw():
    for f in B.call("jawa/list_factions").get("factions") or []:
        if f.get("defName") == "OutlanderCivil":
            return f.get("goodwill", f.get("playerGoodwill"))
let = B.call("jawa/letter_list")
out = {"letters": [l for l in (let.get("letters") or []) if "Liquid theft" in json.dumps(l, default=str)][-3:],
       "caught": g("caught"), "gw0": gw(), "gc0": g("goodwillCharged")}
raw = B.ticks
for i in range(16):
    B.hp("filltank:%d,%d=%s,100" % (TANK + (PH.LIQUID_WATER,)))
    B.hp("filltank:%d,%d=%s,0" % (OURS + (PH.LIQUID_WATER,)))
    for _ in range(4):
        raw(1000)
out.update(gw1=gw(), gc1=g("goodwillCharged"), charges=g("charges"))
out["pass"] = out["gw0"] is not None and out["gw1"] is not None and out["gw1"] < out["gw0"] and int(out["gc1"]) - int(out["gc0"]) <= -2
print(json.dumps(out, default=str)[:1500])
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
