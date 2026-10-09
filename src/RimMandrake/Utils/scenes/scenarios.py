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


AB = "RimMandrake.Abyss.RM_AbyssSettings"

def abyss_dark():
    """DEEPFIRE_WORLD_LIGHT_1 A2: in the Abyss Dark a glow tank keeps its radius while a vanilla lamp beside it shrinks;
    darkSparesDeepfire off makes the tank shrink too."""
    mid = S.biome_map(114470, "RM_Abyss")
    try:
        with S.Scene("abyss_dark", 150, 40, 12, 10) as sc:
            sc.weather("RM_AbyssDark")
            sc.room(); sc.grid()
            sc.put("StandingLamp", 5, 2); sc.put("RM_GlowTank", 5, 5)
            pid = sc.colonist(8, 8); sc.fuel(pid, n=75, ticks=1500)
            sc.put("RM_CrowncarpetFresh", 2, 8); tk = sc.find("RM_GlowTank"); sc.order(pid, "Refuel", a=tk["id"], b=sc.find("RM_CrowncarpetFresh")["id"], count=1); S.run(1200)
            sc.heat(8, 8, 0)
            def rd(tag):
                return dict(tag=tag, lamp=sc.comp("StandingLamp", "Glower", "GlowRadius,Glows"), tank=sc.comp("RM_GlowTank", "Glower", "GlowRadius,Glows"),
                            temp=sc.temp(8, 8), net=sc.netsize('StandingLamp'))
            rows = [rd("t0")]
            S.run(700); sc.heat(8, 8, 0); S.run(700); rows.append(rd("dark_on"))
            with S.setting(AB, darkSparesDeepfire="False"):
                S.run(700); rows.append(rd("spare_off"))
            S.run(700); rows.append(rd("spare_on_again"))
            out("abyss_dark", "DEEPFIRE_A2", "?", rows)
    finally:
        S.drop_map(mid, 114470)

def tank_control():
    """Control for abyss_dark: the same powered, seeded GlowTank with NO Dark (the Rot map); does its radius move by itself?"""
    with S.Scene("tank_control", 100, 100, 12, 10) as sc:
        sc.room(); sc.grid(); sc.put("RM_GlowTank", 5, 5)
        pid = sc.colonist(8, 8); sc.fuel(pid, n=75, ticks=1500)
        sc.put("RM_CrowncarpetFresh", 2, 8); tk = sc.find("RM_GlowTank"); sc.order(pid, "Refuel", a=tk["id"], b=sc.find("RM_CrowncarpetFresh")["id"], count=1); S.run(1200)
        rows = []
        for i in range(4):
            rows.append(sc.comp("RM_GlowTank", "Glower", "GlowRadius,Glows")); S.run(500)
        rows.append(sc.inspect(tk["id"])[-300:]); rows.append(sc.inspect(sc.find("WoodFiredGenerator")["id"])[-200:]); rows.append(sc.netsize("RM_GlowTank"))
        out("tank_control", "DEEPFIRE_A2_control", "?", rows)

def abyss_dark2():
    """Isolate the tank: seeded+powered tank in the Abyss, read radius with Clear weather (no Dark), then the Dark with
    darkSparesDeepfire on, then the Dark with darkEnabled off."""
    mid = S.biome_map(114470, "RM_Abyss")
    try:
        with S.Scene("abyss_dark2", 150, 40, 12, 10) as sc:
            sc.room(); sc.grid(); sc.put("StandingLamp", 5, 2); sc.put("RM_GlowTank", 5, 5)
            pid = sc.colonist(8, 8); sc.weather("Clear"); sc.fuel(pid, n=75, ticks=1500)
            sc.put("RM_CrowncarpetFresh", 2, 8); tk = sc.find("RM_GlowTank")
            sc.order(pid, "Refuel", a=tk["id"], b=sc.find("RM_CrowncarpetFresh")["id"], count=1); S.run(1200)
            def rd(tag): return dict(tag=tag, lamp=sc.comp("StandingLamp", "Glower", "GlowRadius,Glows"), tank=sc.comp("RM_GlowTank", "Glower", "GlowRadius,Glows"), temp=sc.temp(8, 8), weather=S.call("jawa/weather_get").get("weather", {}).get("current"))
            rows = [rd("clear")]
            S.run(600); rows.append(rd("clear+600"))
            sc.weather("RM_AbyssDark"); sc.heat(8, 8, 0); S.run(800); sc.heat(8, 8, 0); S.run(800); rows.append(rd("dark_spare_on"))
            with S.setting(AB, darkEnabled="False"):
                S.run(800); rows.append(rd("darkEnabled_off"))
            S.run(800); rows.append(rd("darkEnabled_restored"))
            out("abyss_dark2", "DEEPFIRE_A2", "?", rows)
    finally:
        S.drop_map(mid, 114470)

if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
