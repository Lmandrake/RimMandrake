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

def greentide_heat(hours=6):
    """WETBULB_FOLD_INTO_HEAT_1 A3: an unprotected colonist outdoors on a Greentide map gains vanilla Heatstroke, one in an enclosed room does not."""
    mid = S.biome_map(114480, "RM_Greentide")
    try:
        with S.Scene("greentide_heat", 10, 20, 24, 12) as sc:
            sc.weather("Clear")
            S.call("jawa/game_condition", action="start", condition="HeatWave", durationTicks=40000)
            sc.time_of_day(12.0)
            out_p = sc.colonist(2, 2)
            room = S.Scene("room", 40, 20, 8, 8); room.clear(); room.room()
            in_p = S.call("jawa/spawn_pawn", kindDef="Colonist", x=44, z=24, faction="player", count=1)["pawns"][0]["id"]
            for pid in (in_p, out_p):
                S.call("jawa/set_draft", pawnId=pid, drafted=True)
            rows = []
            def rd(tag):
                d = {}
                for nm, pid in (("outdoor", out_p), ("enclosed", in_p)):
                    pg = (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
                    d[nm] = dict(hediffs=[(h["def"], h.get("severity")) for h in pg.get("hediffs", []) if h["def"] != "Scarification"], pos=pg.get("position"),
                                 felt=S.call("jawa/thing_ambient_temp", thing=pid).get("ambient"))
                return dict(tag=tag, temp_out=sc.temp(10, 6), temp_in=room.temp(4, 4), **d)
            rows.append(rd("t0"))
            for h in range(int(hours)):
                S.run(1) if False else None
                for pid in (out_p, in_p): S.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
                for _ in range(5):
                    S.run(500); S.call("jawa/kill_hostiles")
                rows.append(rd("h%d" % (h + 1)))
            room.clear()
            out("greentide_heat", "WETBULB_A3", "?", rows)
    finally:
        S.drop_map(mid, 114480)

def sealed_suit(stuff="Cloth"):
    """WETBULB_FOLD_INTO_HEAT_1 A4: the sealed suit raises ComfyTemperatureMax by about 1.4x the stuff's heat insulation."""
    with S.Scene("sealed_suit", 100, 100, 10, 10) as sc:
        pid = sc.colonist(3, 3)
        def comfy(): return [s for s in S.call("jawa/pawn_stats", pawn=pid, stats="ComfyTemperatureMax,Insulation_Heat").get("stats", [])]
        before = comfy()
        sc.put("RUT_SealedSuit", 5, 5, stuff=stuff); suit = sc.find("RUT_SealedSuit")
        r = sc.order(pid, "Wear", a=suit["id"]); S.run(900)
        after = comfy()
        ts = S.call("jawa/thing_stats", thing=suit["id"], stats="Insulation_Heat,StuffEffectMultiplierInsulation_Heat")
        st = S.call("jawa/get_defs", defs="ThingDef/%s" % stuff, fields="stuffProps")
        out("sealed_suit", "WETBULB_A4", "?", dict(before=before, after=after, suit_stats=ts, order=str(r)[:150], stuff=str(st)[:500]))

def chill_pump():
    """CHILL_AIR_PUMP_1 A2/A3/A4 on a Chill seabed map (RM_SeabedLayer under a RM_TheChill surface tile): a fuelled stove lights only
    while a live pump serves its sealed roofed room. MEASURED: spawn_batch'd OxygenPumps never join a power net (Not connected to power),
    so 'switched on/off' is jawa/power_net forcePowerOn, which the comp reads as power.PowerOn (Live)."""
    mid = S.biome_map(114490, "RM_TheChill", layer="RM_SeabedLayer", surface_biome="RM_TheChill")
    rows = []
    def rd(sc, stove, tag, pumps):
        d = dict(tag=tag, stove_pushes_heat=S.call("jawa/comp_read", thing=stove["id"], comp="HeatPusher", members="ShouldPushHeatNow").get("values"),
                 pumps=[(t["x"], t["z"], S.call("jawa/comp_read", thing=t["id"], comp="ChillAirSupply", members="Live").get("values", {}).get("Live")) for t in pumps])
        if pumps: d["pump_inspect"] = sc.inspect(pumps[0]["id"])[-230:]
        rows.append(d)
    try:
        with S.Scene("chill_pump", 20, 20, 8, 8) as sc:
            sc.room()
            sc.put("OxygenPump", 2, 2); sc.put("OxygenPump", 2, 4); sc.put("FueledStove", 5, 4)
            pid = sc.colonist(4, 6); sc.put("WoodLog", 5, 2, n=50)
            stove = sc.find("FueledStove"); logs = S.call("jawa/list_things", defName="WoodLog", rect=sc.rect)["things"]
            sc.order(pid, "Refuel", a=stove["id"], b=logs[0]["id"], count=50); S.run(900)
            pumps = S.call("jawa/list_things", defName="OxygenPump", rect=sc.rect)["things"]
            a, b = pumps[0], pumps[1]
            def setp(t, on):
                r = sc.power_on(t["id"], on); return r.get("powerOnAfter")
            rd(sc, stove, "no_pump_on", pumps)
            rows.append(dict(note="pump1_on", after=setp(a, True))); S.run(600); rd(sc, stove, "A2_pump1_on", pumps)
            rows.append(dict(note="pump1_off", after=setp(a, False))); S.run(600); rd(sc, stove, "A2_pump1_off", pumps)
            rows.append(dict(note="both_on", after=(setp(a, True), setp(b, True)))); S.run(600); rd(sc, stove, "A3_two_on", pumps)
            rows.append(dict(note="one_off", after=setp(a, False))); S.run(600); rd(sc, stove, "A3_one_off", pumps)
            rows.append(dict(note="both_off", after=setp(b, False))); S.run(600); rd(sc, stove, "A3_both_off", pumps)
            # A4: an unroofed room: strip the roof over the interior and switch one pump on
            rows.append(dict(note="unroof_and_on", after=setp(a, True), roof=str(S.call("jawa/set_roof_batch", ops="%d,%d,6,6" % (sc.x + 1, sc.z + 1), roofDef="none"))[:120])); S.run(600)
            rd(sc, stove, "A4_unroofed_pump_on", pumps)
            out("chill_pump", "CHILL_A2_A3_A4", "?", rows)
    finally:
        S.drop_map(mid, 114490)

if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
