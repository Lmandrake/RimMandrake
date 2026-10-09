"""Named scenarios built on scenelib. Run: python.exe src/RimMandrake/Utils/scenes/scenarios.py <name>
Each prints one JSON line {scenario, criterion, result: pass|fail|UNMEASURED, evidence}."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S

def out(scn, crit, result, evidence):
    print(json.dumps(dict(scenario=scn, criterion=crit, result=result, evidence=evidence), default=str)); sys.stdout.flush()

LP = "RimMandrake.LuminousPigment.LuminousPigmentSettings"

def glow_tank_fed(*liquids):
    """GLOW_TANK_LIQUID_FEED_1 A2 (salt tank drawn down, crop seeded; setting off removes the line) and A3 (fresh, brine do not)."""
    for liquid in (liquids or ("SaltWater", "FreshWater", "Brine")):
        with S.Scene("glow_tank_" + liquid, 100, 100, 14, 8) as sc:
            pid = sc.colonist(1, 1)
            sc.put("RM_GlowTank", 4, 3); sc.put("RM_LiquidTank", 6, 3)
            sc.put("RM_CrowncarpetFresh", 1, 2); sc.put("RM_Bottle_%s" % liquid, 2, 2)
            gt, lt = sc.find("RM_GlowTank"), sc.find("RM_LiquidTank")
            sc.power_on(gt["id"], True)
            mat, bot = sc.find("RM_CrowncarpetFresh"), sc.find("RM_Bottle_%s" % liquid)
            sc.order(pid, "Refuel", a=gt["id"], b=mat["id"], count=1); S.run(1500)
            sc.power_on(gt["id"], True)
            sc.order(pid, "RM_EmptyIntoTankJob", a=bot["id"], b=lt["id"]); S.run(1200)
            before = (sc.inspect(gt["id"]), sc.inspect(lt["id"]))
            S.run(600)
            after = (sc.inspect(gt["id"]), sc.inspect(lt["id"]))
            with S.setting(LP, tankNeedsWater="False"):
                S.run(120); off = sc.inspect(gt["id"])
            out("glow_tank_fed", {"SaltWater": "A2", "FreshWater": "A3", "Brine": "A3b"}[liquid], "?",
                dict(liquid=liquid, gt_before=before[0][-420:], lt_before=before[1][-200:], gt_after=after[0][-420:], lt_after=after[1][-200:], gt_setting_off=off[-300:]))

if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
