#!/usr/bin/env python3
"""Throwaway (Maturation advance, FlowWorks row 2): build design/concepts/FlowWorks/version/test_table.{json,md}.
Columns match the pilot's design/concepts/ExplosiveKnockback/version/test_table.json.
Inputs: tree.json, record.json, scenes.json; /tmp/fw_pilot/selftests.tsv (python selftest runs);
/tmp/fw_pilot/cs_suite.log (one full C# SelfTest run); the held-statement files."""
import json, os, re, sys, glob, datetime, subprocess

ROOT = "/home/mandrake/rm/relentless/clones/RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT.det"
os.chdir(ROOT)
C = "design/concepts/FlowWorks"
FW = "src/RimMandrake/FlowWorks"
ST = FW + "/Source/SelfTest"
tree = json.load(open(C + "/tree.json"))
rec = json.load(open(C + "/record.json"))
scn = json.load(open(C + "/scenes.json"))

# ---------------------------------------------------------------- C# cases: where each is defined, and today's result
case_file = {}
for f in sorted(glob.glob(ST + "/*.cs")) + sorted(glob.glob(FW + "/Source/SelfTestTrench/*.cs")):
    for n in re.findall(r'Case\(\s*"([^"]+)"', open(f, errors="replace").read()):
        case_file.setdefault(n.split()[0], f)
cs_res = {}
CS_LOG = "/tmp/fw_pilot/cs_suite.log"
if os.path.exists(CS_LOG):
    for line in open(CS_LOG, errors="replace"):
        m = re.match(r"(ok|FAIL)\s+(\S+)", line)
        if m:
            cs_res[m.group(2)] = m.group(1) == "ok"
CS_META = json.load(open("/tmp/fw_pilot/cs_suite.json")) if os.path.exists("/tmp/fw_pilot/cs_suite.json") else {}

# ---------------------------------------------------------------- python selftest runs
py_res = {}
for line in open("/tmp/fw_pilot/selftests.tsv"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 3:
        py_res[p[0]] = {"rc": int(p[1]), "seconds": float(p[2]), "tail": p[3] if len(p) > 3 else ""}

STOCK = "python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only %s"

# id: (observes, case-name regex, extra python selftests)
CS = {
 "T_DIG": ("dig jobs and labour: dig progress, deep digs to 8 m, excavation pulses, dig plans, digging time", r"^(DigProgress|DeepDig|ExcavationTick|Plan|DigCanal|Shovel|LineDigBreak|Fillin)_", [FW + "/selftest_flowworks_review1022_excavation.py"]),
 "T_WALL_FACES": ("depth legible by wall faces: cliff masks, ramps, wall faces per depth", r"^(Cliff|CliffMask|Ramp|WallFaces|PitSide|PitSun)_", [FW + "/selftest_flowworks_flat_shadow.py"]),
 "T_LEVEL": ("the levelling kernel: one surface per connected still body, exact levels, pours, settling, conserved volume, seeded fuzz", r"^(Level|LEVELLING|LEVELPREJIT|LEVELRUN|LEVELPOUR|LevelPour|Exact|Settle|Volume|Fuzz|Sequence)", [ST + "/selftest_flowworks_kernel_oracle.py", FW + "/selftest_flowworks_one_water_number.py", FW + "/selftest_flowworks_flood_hour_cadence.py"]),
 "T_STOCK": ("every source is stock: refill by season and seep, creditable levels, limitless edge bodies, pond depth and return, body mending, liquid theft", r"^(Refill|CreditableLevels|Scenario|Pond|PondDepth|Lake|Body|WaterMend|Theft|Limitless|Season|Wetness|ReviewFix_Stock|Placer|PlacerStock|ContainerMat)", [FW + "/selftest_flowworks_pond_outlet_fractional.py", FW + "/selftest_pump_draw_conserves.py"]),
 "T_SHEET": ("overspill sheets: liquid over open ground, soak-in, freeze and thaw, flood release, outflow", r"^(Sheet|FloodRelease|Outflow|Overflow|Depth)_", [FW + "/selftest_flowworks_sheet_drown_message.py"]),
 "T_ROSTER": ("liquid roster: every supported liquid, its terrains and hazards, fluid compatibility, immersion damage", r"^(FluidsCompatible|FluidDef|ImmersionDamage|NaturalTar|GateAcid|P7)_?", [FW + "/Tools/selftest_liquid_defs_hazards.py", FW + "/Tools/selftest_water_terrains_name_liquid.py", FW + "/Tools/selftest_lava_row.py", FW + "/selftest_flowworks_hot_wet_terrain.py"]),
 "T_FIRE": ("flammable liquid fire: ignition, long burn back to the source, firebreak gates", r"^(FuelFire|GateFirebreak)_", [FW + "/selftest_flowworks_fuel_moat.py"]),
 "T_SLIME": ("slime: sinking, slip and slide-back on the climb", r"^Slime_", []),
 "T_PIT_DRAW": ("a pit reads as a hole: lip occlusion, draw hold, occupant drawn below the lip, floor ground", r"^(PitLip|PitDrawHold|PitFloorGround|Relative|PitStuck)_", [FW + "/selftest_flowworks_pit_draw_census.py", FW + "/selftest_flowworks_pit_floor_ground.py", FW + "/selftest_flowworks_review1022_superdeep.py"]),
 "T_PIT_LABEL": ("the pit's label names its exact depth and liquid", r"^PitLabel_", []),
 "T_PIT_COVER": ("covered pits: cover rests on two banks, beneath-cover walkers, cover look, spikes and piercing, fall rails, deck collapse", r"^(PitCover|PitCoverLook|PitDeck|Beneath|LidWalker|Spikes|SpikePierce|FallRail|DeckCollapse|SuperdeepTrap)_", [FW + "/selftest_flowworks_cover_breaks.py", FW + "/Tools/selftest_spike_float32_parity.py"]),
 "T_PIT_ACCESS": ("ways in and out: wall ladders on rails, rescue ladders, ramps, climbing gear, wall reach, pocket grids, drafted moves into a pit", r"^(PitAccess|PitTravel|PitRamp|PitRescue|PitRoute|LadderWall|LadderRails|LadderClimb|LadderParity|LadderInspect|WallClimb|WallReach|Pocket|PocketGrid|Step|Climb|Diagonal)_", [FW + "/selftest_flowworks_drafted_move_pit.py", FW + "/selftest_flowworks_pit_travel_tags.py"]),
 "T_PRISON": ("pit-held capture: capture from the rim waits for a held pawn, pit room needs an enclosed pit, prisoners in the current", r"^(PitCapture|PitRoom|SWEEP_PRISONER|TAKEN)", []),
 "T_DOORS": ("flow doors: a shut sluice seals, a grate always passes, door facing, gate lift", r"^(FlowDoor|FlowDoorFacing|Sluice|Grate|Ruling18|FLOWWORKS_SLUICE)", [FW + "/Tools/selftest_fw_gate_lift.py"]),
 "T_BRIDGES": ("spans: drawbridges raise and lower, suspension decks hang between anchors, underpasses, span bases", r"^(Drawbridge|Suspension|SuspensionBridges|Underpass|SpanBase|Waters)_", [FW + "/selftest_flowworks_drawbridge_pose.py", FW + "/selftest_flowworks_suspension_linked.py"]),
 "T_TRENCH": ("trench cover: higher neighbouring ground covers like a sandbag; raiders never shelter in a pit; trench strides", r"^(RaiderTrench|TrenchStride|Trench)_", []),
 "T_SWIM": ("the water ladder: wading costs, swimming at 2 m and deeper, slow drowning, wet cost by height", r"^(Swim|SWIM|DugSwim|WetCost|P14|SHALLOW|WATERED)", [FW + "/selftest_swim_shore_reach.py"]),
 "T_HOSE": ("hoses: reel, lay, plump when flowing, routing, ports, bands, splices, shadows", r"^(Hose|HOSE|ReelBodyInlet|ReelFacing|HS)", [FW + "/selftest_hose_offline.py", FW + "/selftest_hose_ports.py", FW + "/selftest_hose_lay_settle.py", FW + "/selftest_hose_fittings.py"]),
 "T_NET": ("one liquid network: pipes, pumps, tanks attach (never connect two runs), adapters, transfer of real litres, tank theft", r"^(Net|LiquidJoin|PipeStub|TankFlange|Transfer|Pump|PumpPorts|PumpOutflow|TankTheft|PipeSpan|PipePole|PipeArm|Adapter|Rewire|TankDebug|TankSearch)_", [FW + "/selftest_pump_station_ports.py", FW + "/selftest_flowworks_tank_drink_recheck.py", FW + "/Tools/selftest_pipe_seat.py"]),
 "T_CONVERT": ("converters and reactions on the network", r"(Converter|converter|reaction)", []),
 "T_THIRST": ("thirst need, bottles filled, emptied and washed, containers", r"^(Thirst|BottleLoop|ContainerStyle)_", [FW + "/Tools/selftest_water_not_food.py", FW + "/selftest_natives_drink_own_water.py"]),
 "T_DRILL": ("subsurface survey and drilling", r"^(DrillSurvey|DrillWhyNot|CoverFloor)_", []),
 "T_SPRINKLER": ("sprinkler heads on a pumped universal pipe", r"^Sprinkler_", []),
 "T_RIVER": ("rivers: current, weirs, ferry and levee, silt, colours, swept pawns returned", r"^(RiverSwitchFlip|RiverWalk|RIVER|WeirPool|WeirFoam|WeirCatch|WeirBreach|Flotsam|RiverCurrent|RiverProbe|P10|Rain|Fish)", [FW + "/selftest_flowworks_rivers.py", FW + "/selftest_flowworks_river_colors.py", FW + "/Tools/selftest_weir_installed.py"]),
 "T_MAP_CONTROLS": ("map-maker controls and the debug liquid tools: source/sink taps at a set rate, level holder, current painter", r"^(MapControl|GodLiquid)_", []),
 "T_QUARRY": ("digging uncovers local materials and spoil", r"^DigFind_", []),
 "T_ICE": ("ice and packed snow cut into crushed ice; one pile melts at a time", r"^(IceDig|IceMelt)_", []),
 "T_UNDERLIQUID": ("the one under-liquid law: what is seen through which liquid at which level, one cut from the foot, shadows", r"^(Submerge|UnderLiquid|WaterLook|DeepBed)_", [FW + "/selftest_flowworks_underliquid_parity.py", FW + "/selftest_liquid_look_tune.py", FW + "/selftest_flowworks_tank_shadow.py"]),
 "T_STYLES": ("pipe, reel and tank looks: four pipe styles, tank styles, default look, build menu", r"^(PipeStyles|TankStyles|DefaultLook|BuildMenu|PipeStraightVariants|PipeTankRiser)_", [FW + "/Tools/selftest_fw_offline_art.py", FW + "/Tools/selftest_liquid_looks.py", FW + "/selftest_flowworks_pipe_pole_art.py"]),
 "T_GEYSER_TUB": ("a pit dug on a geyser keeps the geyser at the bottom; a filled geyser pit is a hot tub", r"^GeyserTub_", [FW + "/selftest_flowworks_geyser_tub.py"]),
}
SETTINGS = ("T_SETTINGS_SWEEP_OFFLINE", "every Mod Settings toggle: C# initialiser = Scribe default = the shipped table, the registry names real Scribe keys, per-section reset restores defaults, search shows its hits",
            r"^(SettingsReset|MachinerySettings|Settings)_",
            [FW + "/northstar/selftest_settings_registry.py", FW + "/selftest_settings_search.py", FW + "/northstar/selftest_flowworks_northstar.py"])

tests = {}

def py_entry(path):
    r = py_res.get(path)
    if r is None:
        return {"ran": False, "why": "not in this run's sweep" if os.path.exists(path) else "file absent"}
    return {"ran": True, "rc": r["rc"], "seconds": r["seconds"], "tail": r["tail"][:160]}

def cs_group(tid, obs, rx, extra):
    names = sorted(n for n in case_file if re.search(rx, n))
    files = sorted({case_file[n] for n in names})
    seen = [n for n in names if n in cs_res]
    ok = [n for n in seen if cs_res[n]]
    bad = [n for n in seen if not cs_res[n]]
    rt = {"ran": bool(cs_res), "cases": len(names), "seen": len(seen), "ok": len(ok), "fail": len(bad)}
    if bad:
        rt["failed"] = bad[:8]
    if cs_res:
        rt["rc"] = 0 if (seen and not bad) else 1
        if len(seen) != len(names):
            rt["not_reached"] = [n for n in names if n not in cs_res]
        rt["seconds"] = CS_META.get("seconds")
        rt["note"] = "one full C# SelfTest run, read per case; seconds is the whole suite's"
    else:
        rt["why"] = "C# suite not run yet"
    prefixes = sorted({re.match(r"([A-Za-z0-9]+)", n).group(1) for n in names})
    tests[tid] = {"id": tid, "kind": "offline", "stage": "4-5", "file": "src/RimMandrake/Utils/selftest_flowworks_stock.py",
                  "observes": obs + " (%d C# cases)" % len(names), "reads": files,
                  "command": STOCK % ",".join(p + "*" for p in prefixes), "runs_today": rt}
    py_ids = []
    for p in extra:
        pid = "PY_" + os.path.basename(p)[:-3].replace("selftest_", "").upper()
        doc = ""
        if os.path.exists(p):
            m = re.search(r'"""(.*?)(\n|""")', open(p, errors="replace").read(), re.S)
            doc = (m.group(1).strip() if m else "")[:200]
        tests[pid] = {"id": pid, "kind": "offline", "stage": "4-5", "file": p, "observes": doc or "(no docstring)",
                      "reads": [p], "command": "python3 " + p, "runs_today": py_entry(p)}
        py_ids.append(pid)
    return [tid] + py_ids

GROUP = {}
for tid, (obs, rx, extra) in CS.items():
    GROUP[tid] = cs_group(tid, obs, rx, extra)
GROUP[SETTINGS[0]] = cs_group(*SETTINGS)
tests[SETTINGS[0]]["observes"] += "; plus validation_v2.py --offline O2 (the C# toggle census against site_spec.SETTINGS)"

# validation_v2 offline tier: one python run
v2 = FW + "/northstar/validation_v2.py"
tests["PY_VALIDATION_V2_OFFLINE"] = {"id": "PY_VALIDATION_V2_OFFLINE", "kind": "offline", "stage": "4-5", "file": v2,
    "observes": "tier O: defs, settings census (O2), unbuilt register, geometry, oracle selftest, scene predictions, lint, pit width, negative controls",
    "reads": [v2], "command": "python3 %s --offline" % v2, "runs_today": json.load(open("/tmp/fw_pilot/v2_offline.json")) if os.path.exists("/tmp/fw_pilot/v2_offline.json") else {"ran": False, "why": "not run"}}
GROUP[SETTINGS[0]].append("PY_VALIDATION_V2_OFFLINE")

# ---------------------------------------------------------------- specified (Stage 3 builds them, failing first)
SPEC = {
 "T_WETTING_OFFLINE": ("cells within two squares of a filled canal read wetted, the third does not; a wetted cell holds no liquid and costs no wading; fast growth spends wetting; plants drink a flood down", ["src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs", "src/RimMandrake/FlowWorks/Source/RM_StockMath.cs"], "FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP"),
 "T_WETNESS_PROBE_OFFLINE": ("the wetness probe answers differently on a hand-wetted and a dry cell, and refuses when wetting is off", ["src/RimMandrake/FlowWorks/Source/RM_StockMath.cs"], "with T_WETTING_OFFLINE"),
 "T_TOSS_FLAME_OFFLINE": ("the toss-a-flame order: target validation (burnable liquid cell, rim reachable), first fire on the picked cell, a water cell does not light", ["src/RimMandrake/FlowWorks/Source"], "FLOWWORKS_FLAME_BUILD_TOSS_FROM_THE_RIM"),
 "T_FETCH_FALLEN_OFFLINE": ("raider rescue plan: comrade in a pit -> chop, carry, place a ladder, climb down; under fire -> retreat leaving the fallen", ["src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccessMath.cs"], "FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN"),
 "T_PRISON_CARE_OFFLINE": ("a held pawn in a drained, enclosed pit counts as a prisoner without a bed; needs are met; a bed elsewhere does not move him", ["src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPrisonCare.cs"], "FLOWWORKS_PRISON_BUILD_NO_BED_REQUIRED"),
 "T_DIG_TIME_ARITHMETIC": ("the first-cut time at default settings is within his target (held: 'Colonist DID start digging, and it's slow.'; target not yet set by him)", ["src/RimMandrake/FlowWorks/Source/RM_DigLabor.cs"], "RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION"),
}
for tid, (obs, reads, item) in SPEC.items():
    tests[tid] = {"id": tid, "kind": "offline", "stage": "4-5", "file": "(specified, Stage 3)", "observes": obs, "reads": reads,
                  "owed_under": item, "runs_today": {"ran": False, "why": "specified, not built"}}

# ---------------------------------------------------------------- live scenes and looks
leaf = {l["id"]: l for l in tree["leaves"]}
def entry_exists(ep):
    f, fn = ep.split("::")
    return os.path.exists(f) and re.search(r"^\s*def %s\b" % re.escape(fn), open(f).read(), re.M) is not None
for s in scn["scenes"]:
    f, fn = s["entry_point"].split("::")
    reqs = s.get("requirement") or []
    tiers = {leaf[r].get("tier_proposed") for r in reqs if r in leaf}
    kind = "live_full" if "live_full" in tiers else "live_minimal"
    why = "; ".join(sorted({leaf[r].get("tier_reason") or "" for r in reqs if r in leaf} - {""})) or \
          "an interaction scene of a showcase (scenes.json kind %s): a raid or a season of play runs only in a played map" % s["kind"]
    ex = entry_exists(s["entry_point"])
    tests[s["id"]] = {"id": s["id"], "kind": kind, "stage": "6", "file": f, "entry": fn,
        "observes": (s.get("expect") or "")[:300], "reads": [f, C + "/scenes.json"],
        "command": "python.exe %s  (entry %s; bridge held, %s list)" % (f.replace("/", "\\"), fn, "full" if kind == "live_full" else "minimal"),
        "why_game": why, "owed_under": s.get("entry_point_item"),
        "runs_today": {"ran": False, "entry_exists": ex, "why": "offline only: never the game in this run" + ("" if ex else "; entry function absent")}}
tests["LOOK_STAGE8"] = {"id": "LOOK_STAGE8", "kind": "look", "stage": "8", "file": "(his walk)",
    "observes": "his walk of the moat showcase save, then the garden and pit-trap faces", "reads": [], "runs_today": {"ran": False, "why": "Stage 8"}}
BR = FW + "/northstar/blind_reader.py"    # built Stage 3 2026-11-14 (RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SEVEN_BARS_LEFT)
tests["LOOK_BLIND_READER"] = {"id": "LOOK_BLIND_READER", "kind": "look", "stage": "6", "file": BR, "entry": "read",
    "observes": "a reader who did not make it names what the captures show (depth order, liquid, hole vs trap, hose vs cord, hung bridge)",
    "reads": [BR, FW + "/northstar/selftest_blind_reader.py", C + "/scenes.json"], "why_game": "captures exist only from a running map",
    "command": "python3 %s read --manifest <captures.json> --out <json>  (after the six Stage 6 scenes; manifest from `blind_reader.py template`)" % BR,
    "offline_proof": "python3 " + FW + "/northstar/selftest_blind_reader.py",
    "runs_today": {"ran": False, "entry_exists": os.path.exists(BR), "why": "UNRUN: needs the Stage 6 captures"}}
OLR = FW + "/northstar/owner_look_regressions.py"
tests["OL_OWNER_LOOK_READS"] = {"id": "OL_OWNER_LOOK_READS", "kind": "live_minimal", "stage": "6", "file": OLR,
    "observes": "in-game state reads built early for the held look rows (OL_opaque_hides, OL_goods_covered, OL_buildings_covered, OL_no_surface_shadow, OL_overlays_hidden, OL_corpses_covered, OL_pour_never_no_room ...)",
    "reads": [OLR], "command": "python.exe " + OLR.replace("/", "\\") + "  (bridge held, minimal list)",
    "why_game": "what is drawn over what is a live render-state read; the law itself is decided offline by T_UNDERLIQUID",
    "runs_today": {"ran": False, "entry_exists": os.path.exists(OLR), "why": "offline only; awaiting ingest (validation_holding/README.md)"}}

# ---------------------------------------------------------------- bars
def G(*ids):
    out = []
    for i in ids:
        out += GROUP.get(i, [i])
    return out
BARS = {
 # inventory rows: decides = the capability's offline tests + the scene that checks it directly; supports = showcase scenes
 "inv_dig_depth": (G("T_DIG", "T_WALL_FACES"), ["sc_dig_and_read"], ["sc_moat_raid", "T_DIG_TIME_ARITHMETIC"]),
 "inv_flow_level": (G("T_LEVEL"), ["sc_fill_front", "sc_one_surface"], ["sc_moat_raid"]),
 "inv_stock": (G("T_STOCK"), ["sc_source_pays"], ["sc_moat_raid"]),
 "inv_overflow_sheet": (G("T_SHEET"), [], ["sc_garden"]),
 "inv_irrigation": (["T_WETTING_OFFLINE"], ["sc_wetting"], ["sc_garden"]),
 "inv_liquid_roster": (G("T_ROSTER"), ["sc_fill_tiers"], ["sc_moat_raid"]),
 "inv_fire": (G("T_FIRE"), ["sc_canal_fire"], ["sc_moat_raid"]),
 "inv_slime": (G("T_SLIME"), ["sc_slime"], []),
 "inv_pits": (G("T_PIT_DRAW", "T_PIT_COVER"), ["sc_pit_reads", "sc_covered_pit"], ["sc_moat_raid", "sc_pit_trap_raid"]),
 "inv_pit_access": (G("T_PIT_ACCESS"), ["sc_ways_out"], ["sc_pit_trap_raid"]),
 "inv_doors": (G("T_DOORS"), ["sc_sluice"], ["sc_moat_raid"]),
 "inv_bridges": (G("T_BRIDGES"), ["sc_hung_bridge"], ["sc_moat_raid", "sc_islands"]),
 "inv_trench_cover": (G("T_TRENCH"), ["sc_trench_cover"], ["sc_pit_trap_raid"]),
 "inv_swim": (G("T_SWIM"), ["sc_pawn_height"], ["sc_moat_raid"]),
 "inv_hoses": (G("T_HOSE"), ["sc_hose_look"], ["sc_garden"]),
 "inv_liquid_net": (G("T_NET"), ["sc_one_network"], ["sc_moat_raid", "sc_garden"]),
 "inv_converters": (G("T_CONVERT"), [], ["sc_garden"]),
 "inv_bottles_thirst": (G("T_THIRST"), [], ["sc_garden"]),
 "inv_drilling": (G("T_DRILL"), [], ["sc_garden"]),
 "inv_sprinklers": (G("T_SPRINKLER"), [], ["sc_garden"]),
 "inv_rivers": (G("T_RIVER"), ["sc_river"], []),
 "inv_map_controls": (G("T_MAP_CONTROLS"), ["sc_source_pays"], []),
 "inv_quarry": (G("T_QUARRY"), ["sc_dig_finds"], []),
 "inv_settings": (G("T_SETTINGS_SWEEP_OFFLINE"), ["sc_walk"], []),
 "inv_looks": (G("T_UNDERLIQUID", "T_STYLES", "T_WALL_FACES"), ["LOOK_BLIND_READER"], ["OL_OWNER_LOOK_READS", "sc_fill_tiers", "LOOK_STAGE8"]),
 "inv_prison_no_bed": (G("T_PRISON") + ["T_PRISON_CARE_OFFLINE"], ["sc_hole_prison"], ["sc_moat_raid", "sc_pit_trap_raid"]),
 "inv_toss_flame": (["T_TOSS_FLAME_OFFLINE"], ["sc_toss_flame"], ["sc_moat_raid"]),
 "inv_raider_fetch_fallen": (["T_FETCH_FALLEN_OFFLINE"], ["sc_fetch_fallen"], ["sc_pit_trap_raid"]),
 # leaves
 "canal_reads_as_dug": (G("T_DIG", "T_WALL_FACES"), ["sc_dig_and_read", "LOOK_BLIND_READER"], ["sc_dig_finds", "T_DIG_TIME_ARITHMETIC"]),
 "fill_flows_along_canal": (G("T_LEVEL"), ["sc_fill_front"], ["LOOK_STAGE8"]),
 "fill_level_legible": (G("T_UNDERLIQUID"), ["sc_fill_tiers", "LOOK_BLIND_READER"], ["OL_OWNER_LOOK_READS", "LOOK_STAGE8"]),
 "one_still_surface": (G("T_LEVEL"), ["sc_one_surface"], []),
 "source_pays_and_refills": (G("T_STOCK"), ["sc_source_pays"], []),
 "canal_fire_burns_back": (G("T_FIRE"), ["sc_canal_fire"], []),
 "slime_holds_the_crossing": (G("T_SLIME"), ["sc_slime"], ["LOOK_BLIND_READER"]),
 "pawn_height_follows_depth": (G("T_SWIM"), ["sc_pawn_height"], []),
 "pit_reads_as_hole": (G("T_PIT_DRAW", "T_PIT_LABEL"), ["sc_pit_reads", "LOOK_BLIND_READER"], ["OL_OWNER_LOOK_READS"]),
 "covered_pit_springs": (G("T_PIT_COVER"), ["sc_covered_pit", "LOOK_BLIND_READER"], ["sc_pit_trap_raid"]),
 "ways_in_and_out": (G("T_PIT_ACCESS"), ["sc_ways_out"], []),
 "sluice_drains_on_command": (G("T_DOORS"), ["sc_sluice"], ["sc_moat_raid"]),
 "hose_reads_as_hose": (G("T_HOSE"), ["sc_hose_look", "LOOK_BLIND_READER"], []),
 "one_liquid_network": (G("T_NET"), ["sc_one_network"], ["sc_garden"]),
 "trench_gives_cover": (G("T_TRENCH"), ["sc_trench_cover"], ["sc_pit_trap_raid"]),
 "hung_bridge_spans": (G("T_BRIDGES"), ["sc_hung_bridge", "LOOK_BLIND_READER"], []),
 "ice_cuts_and_melts": (G("T_ICE"), ["sc_ice"], []),
 "river_flows_endless": (G("T_RIVER"), ["sc_river"], []),
 "moat_raid_sequence": ([], ["sc_moat_raid"], G("T_SWIM", "T_DOORS", "T_PRISON", "T_FIRE", "T_BRIDGES") + ["sc_hole_prison", "sc_toss_flame", "sc_sluice", "LOOK_STAGE8"]),
 "drained_hole_is_a_prison": (G("T_PRISON") + ["T_PRISON_CARE_OFFLINE"], ["sc_hole_prison"], ["sc_moat_raid"]),
 "toss_flame_from_rim": (["T_TOSS_FLAME_OFFLINE"], ["sc_toss_flame"], ["sc_moat_raid"]),
 "canal_wets_two_squares": (["T_WETTING_OFFLINE"], ["sc_wetting"], ["sc_garden"]),
 "raiders_fetch_their_fallen": (["T_FETCH_FALLEN_OFFLINE"], ["sc_fetch_fallen"], ["sc_pit_trap_raid"]),
 "island_bridges_trap_and_fail": (G("T_BRIDGES"), ["sc_islands"], []),
 "no_liquid_on_open_ground": (G("T_SHEET", "T_LEVEL"), ["sc_dig_and_read"], ["LOOK_BLIND_READER"]),
 "no_full_source_after_draw": (G("T_STOCK"), ["sc_source_pays"], []),
 "no_snared_standing": (G("T_PIT_DRAW"), ["sc_pit_reads"], []),
 "no_impossible_plumbing": (G("T_NET", "T_HOSE"), ["sc_one_network"], []),
 "wetting_is_not_flood": (["T_WETTING_OFFLINE"], ["sc_wetting"], []),
 "wetness_probe": (["T_WETNESS_PROBE_OFFLINE"], [], []),
 "walk_moat_season": ([], ["sc_walk"], ["LOOK_STAGE8", "T_SETTINGS_SWEEP_OFFLINE"]),
}
ORDER = {"2": 0, "4-5": 1, "6": 2, "8": 3}
def ok_today(t):
    r = t["runs_today"]
    return r.get("ran") and r.get("rc") == 0
def runnable(t):
    r = t["runs_today"]
    return bool(r.get("ran")) or bool(r.get("entry_exists"))
ids = [x["id"] for x in rec["inventory"]] + [l["id"] for l in tree["leaves"]]
src_of = {x["id"]: "record.json" for x in rec["inventory"]}
src_of.update({l["id"]: "tree.json" for l in tree["leaves"]})
kind_of = {x["id"]: "inventory" for x in rec["inventory"]}
kind_of.update({l["id"]: l.get("leaf_kind") for l in tree["leaves"]})
bars = []
for b in ids:
    off, live, sup = BARS[b]
    dec = list(dict.fromkeys(off + live))
    offd = [t for t in dec if tests[t]["kind"] == "offline"]
    bars.append({"id": b, "source": src_of[b], "kind": kind_of[b],
        "proves_at": max((tests[t]["stage"] for t in dec), key=lambda s: ORDER[s]) if dec else None,
        "decides": dec, "supports": [s for s in dict.fromkeys(sup) if s not in dec], "held": [],
        "offline_decides": offd,
        "offline_green_today": bool(offd) and all(ok_today(tests[t]) for t in offd),
        "every_decider_runnable_today": bool(dec) and all(runnable(tests[t]) for t in dec),
        "any_test_runnable_today": any(runnable(tests[t]) for t in dec + sup if t in tests)})

# ---------------------------------------------------------------- held statements, placed by hand
H = json.load(open("/tmp/fw_pilot/held_place.json"))
held = []
bar_ix = {b["id"]: b for b in bars}
for h in H:
    held.append(h)
    for b in h["bars"]:
        bar_ix[b]["held"].append("%s#%s" % (h["tag"], h["row"]))

table = {"mod": "FlowWorks", "version": "0.1.0", "made": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "made_by": "rm-builder, Maturation advance row 2 beside the pilot (throwaway /tmp/fw_pilot/make_table.py, copy in version/advance_scripts/)",
    "stages": {"2": "preflight (a program)", "4-5": "blind offline challenge and game-logic testing", "6": "in-game acceptance", "8": "his live walk"},
    "rule": "a bar passes when every test in decides passes; proves_at is the highest stage among them; supports add evidence but decide nothing",
    "settings_move": "inv_settings: the per-toggle default check is decided offline by T_SETTINGS_SWEEP_OFFLINE (C# SettingsReset/MachinerySettings/Settings cases, the settings registry selftest, the settings search selftest, the northstar selftest's registry rows, and validation_v2.py --offline O2's C# toggle census). The game keeps only sc_walk's master switch off and on mid-game, which needs a running colony. validation_v2's live L2 'settings_default' read stays a harness precondition (installed settings equal shipped), not a bar. No bar text is edited.",
    "corrections": [], "corrections_note": "FlowWorks has no coverage_verdict.json and no coverage_fixes.json: the Arbiter signed all 59 rows covered on 2026-11-05 at the locked tree and sheet; no judge correction is open (version/gaps_sorted.md)",
    "held_statements": held, "tests": tests, "bars": bars}
json.dump(table, open(C + "/version/test_table.json", "w"), indent=1)
print("bars", len(bars), "tests", len(tests), "held", len(held))

# ---------------------------------------------------------------- read view
def runs_word(b):
    return "all" if b["every_decider_runnable_today"] else ("some" if b["any_test_runnable_today"] else "none")
offl = [t for t in tests.values() if t["kind"] == "offline"]
offl_built = [t for t in offl if t["file"].startswith("src/")]
ran_ok = [t for t in offl_built if t["runs_today"].get("ran") and t["runs_today"].get("rc") == 0]
ran_red = [t for t in offl_built if t["runs_today"].get("ran") and t["runs_today"].get("rc") != 0]
live = [t for t in tests.values() if t["kind"].startswith("live")]
cnt = {
 "bars": len(bars),
 "with at least one test runnable today (an offline test that ran, or an in-game scene whose entry exists)": sum(b["any_test_runnable_today"] for b in bars),
 "with every deciding test runnable today": sum(b["every_decider_runnable_today"] for b in bars),
 "with an offline deciding test, all green today": sum(b["offline_green_today"] for b in bars),
 "with an offline deciding test that exists (built), green or red": sum(1 for b in bars if any(tests[t]["file"].startswith("src/") for t in b["offline_decides"])),
 "with no offline deciding test at all": sum(1 for b in bars if not b["offline_decides"]),
 "decided offline only (no game needed)": sum(1 for b in bars if b["decides"] and all(tests[t]["kind"] == "offline" for t in b["decides"])),
}
L = ["# FlowWorks 0.1.0: test-and-stage table", "",
     "Generated %s from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Columns match Explosive Knockback's table." % table["made"], "",
     "## Counts (measured)", ""]
L += ["- %s: %d" % kv for kv in cnt.items()]
L += ["- in-game scenes: %d, entry exists %d, absent %d" % (len(live), sum(1 for t in live if t["runs_today"].get("entry_exists")), sum(1 for t in live if not t["runs_today"].get("entry_exists"))),
      "- offline tests: %d built (ran today: %d PASS, %d red), %d specified for Stage 3" % (len(offl_built), len(ran_ok), len(ran_red), len(offl) - len(offl_built)), "",
      "## Bars", "", "| bar | from | proves at | decides | supports | runnable today | offline green |", "|---|---|---|---|---|---|---|"]
for b in bars:
    L.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (b["id"], b["source"].split(".")[0], b["proves_at"], ", ".join(b["decides"]) or "-",
             ", ".join(b["supports"]) or "-", runs_word(b), "yes" if b["offline_green_today"] else "no"))
L += ["", "## Tests", "", "| test | kind | stage | file | runs today |", "|---|---|---|---|---|"]
for k, t in tests.items():
    r = t["runs_today"]
    if r.get("ran"):
        rw = ("PASS" if r.get("rc") == 0 else "RED rc %s" % r.get("rc")) + (" (%s/%s cases ok)" % (r["ok"], r["cases"]) if "cases" in r else "") + (", %ss" % r["seconds"] if r.get("seconds") is not None else "")
    elif "entry_exists" in r:
        rw = "not run (offline only); entry %s" % ("exists" if r["entry_exists"] else "ABSENT")
    else:
        rw = "not run: " + r.get("why", "")
    L.append("| `%s` | %s | %s | `%s` | %s |" % (k, t["kind"], t["stage"], t["file"], rw))
L += ["", "## Held look statements placed (%d rows)" % len(held), "", "| row | bars | test | stage | kind |", "|---|---|---|---|---|"]
for h in held:
    L.append("| %s#%s | %s | %s | %s | %s |" % (h["tag"], h["row"], ", ".join(h["bars"]) or "-", h["test"].replace("|", "/"), h["stage"], h["kind"]))
L += ["", "## Judge corrections", "", table["corrections_note"] + ".", "", "## The settings sweep, moved offline", "", table["settings_move"], ""]
open(C + "/version/test_table.md", "w").write("\n".join(L))
print("\n".join(L[4:16]))
