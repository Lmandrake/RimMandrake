"""FlowWorks north-star trial site: the data every other script reads.

Authority: design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md section 3 (site
preparation), 3.9 (preflight), 6 (driver). Item FLOWWORKS_NORTHSTAR_SITE_PREP_1.
Dev tooling, never deployed (deploy_custom_mods.py skips *.py).

Holds: the shipped Mod Settings defaults (selftest cross-checks them against the C#),
the plot layout (bar footprint + 8-cell buffer, 12-cell gaps, limitless plots on an
edge, limited plots >= 15 cells in), the per-cell manifest model, the tool census,
the golden-save names, the run-ops parser for the bridge's run-length terrain/roof
reads, and the exact-bytes config backup/restore.
"""
import glob
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.dirname(HERE)                                   # src/RimMandrake/FlowWorks
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD_DIR)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PREP_VERSION = "1"                     # bump whenever prep_site.py's output changes
PACKAGE_ID = "mandrake.rm.flowworks"
TIER = "flowworks"
GOLDEN_NAME = "NS_FlowWorks_TrialSite_v1"
WORK_PREFIX = "NS_FlowWorks_Work_"
REPO_SIDECAR_DIR = os.path.join(ROOT, "infrastructure", "state", "northstar")
DLL_REL = os.path.join("Assemblies", "RimMandrakeFlowWorks.dll")
SEATS = ("BENCH", "FOUNDRY")

# --------------------------------------------------------------------- Mod Settings
# Shipped defaults, MEASURED from the three settings classes' static initialisers.
# selftest re-reads the C# so this table cannot drift from what ships.
SETTINGS = {
    "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings": {
        "depthEngineEnabled": True, "pulseIntervalTicks": 250.0, "flowPerPulse": 1.0,
        "channelConfinementEnabled": True, "digToDepthEnabled": True,
        "liquidCorrosionEnabled": False, "liquidIgnitionEnabled": False,
        "fillInEnabled": True, "fillInDisplacementEnabled": True, "sourceBudgetEnabled": True,
        "stickyLimitlessEnabled": True, "recessionEnabled": True, "refillEnabled": True,
        "rainFillsExcavationsEnabled": True, "liquidLooksEnabled": True, "pitOutlineEnabled": True, "pitHidesShadowEnabled": True, "edgeSinksEnabled": True,
        "sourceBudgetMultiplier": 1.0, "minLimitlessBodyCells": 50.0, "refillRateMultiplier": 1.0,
        "rainFillPerPulse": 0.1,
        "superdeepCaptureEnabled": True, "superdeepCapturesOwnFaction": False,
        "ladderRequiredToExitEnabled": True, "ladderPrisonDoorEnabled": True,
        "superdeepShootingRuleEnabled": True,
        "pitWidthBodySizeMultiplier": 1.0,
        # PIT_LEGACY_CODE_RETIRE_1: the four survivors of the retired PitsSettings, rehoused here
        "trapTriggerEnabled": True, "trapSensitivityMultiplier": 1.0,
        "fallDamageEnabled": True, "fallDamageMultiplier": 1.0,
        "spikesEnabled": True, "spikeDamageMultiplier": 1.0,     # CANAL_BOTTOM_SPIKES_1
        "pitExposureEnabled": True, "pitTemperatureCoupling": 3.0, "pitResistanceLossMultiplier": 1.0,   # PIT_TEMPERATURE_SOFTENING_1 (PROVISIONAL)
        "pitDepthDrawOffsetEnabled": True, "pitSinkPerLevel": 0.3,   # PIT_DEPTH_DRAW_OFFSET_1 (PROVISIONAL)
        "flowDoorsSealedFromPitEnabled": True, "sluiceLetsBigThroughEnabled": True,   # FLOWWORKS_DOOR_FAMILY_1
        "canalFireEnabled": True, "canalBurnDaysPerLevel": 1.0, "sourceBurnDaysPerLevel": 5.0,   # Phase 6 (ruling 7)
        "fireFrontSpeedMultiplier": 1.0, "sourceFireReach": 3.0,                                  # Phase 6 (PROVISIONAL)
        "pitDrowningEnabled": True, "pitDrowningRateMultiplier": 1.0, "poisonFillEnabled": True,   # PIT_FILL_EFFECTS_1
        "viscosityEnabled": True,          # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (PROVISIONAL stride)
        "bottleLoopEnabled": True, "bottleDirtyStageEnabled": True,
        "tankLoopEnabled": True, "tankCapacityMultiplier": 1.0,
        "liquidDrillingEnabled": True, "drillYieldChanceMultiplier": 1.0, "drillUnitsPerCycle": 1.0,
        "typedLiquidShoresEnabled": True,
        "swaleEnabled": True, "swaleRateMultiplier": 1.0,     # CRACKEDLANDS_MECHANICS_BUILD_1 swale
        "explosionIgnitesLiquidEnabled": True, "foamSmothersLiquidFireEnabled": True,
        "rainDousesLiquidFireEnabled": True,                    # Phase 6 owed (ignition by explosion, extinguishing)
        "superdeepRoomsEnabled": True, "captureDownEnabled": True, "wardenFromLipEnabled": True,   # SUPERDEEP_PRISON_ROOM_1
        "excavationWallFacesEnabled": True,                     # EXCAVATION_WALL_ART_1 carrier
        "bottleRevertEnabled": True,                            # LIQUID_BOTTLE_LOOP_1 revert timer
        "liquidPumpEnabled": True,                              # Phase 8 slice 1 (universal pump)
        "digFindsEnabled": True, "digFindsLocalOnly": True, "digFindChanceMultiplier": 1.0,
        "digFindBudgetPercent": 5.0, "digFindLetterEnabled": True,   # FLOWWORKS_QUARRY_DIGGING_1 (FlowWorks half)
        "excavationWallMaterialEnabled": True, "pitLipOcclusionEnabled": True, "pitLipOcclusion": 0.85,
        "liquidSurfaceMotionEnabled": True, "liquidWakesEnabled": True, "pitScorchEnabled": True,
        "pitScorchFadeDays": 20.0,                              # visual principles 1-5 (belt_fwvisuals 2026-10-05)
    },
    "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings": {
        "riverSteamEnabled": True, "puffRateMultiplier": 1.0,
    },
    # River Works merged into FlowWorks 2026-10-05 (409d1f57c); its own static settings class
    "RimMandrake.FlowWorks.Rivers.RM_RiversSettings": {
        "riverWorksEnabled": True, "surfaceCurrentEnabled": True, "currentStrength": 1.0, "centreTicksPerCell": 45.0,
        "marginTicksPerCell": 90.0, "itemDriftFactor": 2.0, "scaleWithRiverSize": True, "floodSurgeEnabled": True,
        "countSeasonalFloods": True, "countTorrentialRainFloods": True, "carryAnimals": True, "carryStrangers": True,
        "carryItems": True, "washOffMapEdge": True, "washedAwayMinDays": 1.0, "washedAwayMaxDays": 3.0,
        "pathfinderAvoidsCurrents": True, "crossingHazardsEnabled": True, "bruiseChancePerStep": 0.15,
        "dropChancePerStep": 0.25, "fordsEnabled": True, "bankWorksEnabled": True, "wearRateMultiplier": 1.0,
        "breachEnabled": True, "breachHpFraction": 0.5, "stakeSnapTicksPerCell": 150.0, "stakeLineLevee": True,
        "weirPoolLength": 8.0, "weirCatchesFish": True, "weirCatchIntervalHours": 6.0, "weirHeldCatchCap": 30.0,
        "weirCatchesDrift": True, "weirDriftChance": 0.25, "breachWashesCatch": True, "breachWashCells": 4.0,
        "siltRichening": True, "siltIntervalDays": 0.5, "ferryEnabled": True, "ferryMaxSpan": 40.0,
        "ferryRopeGuidesColonists": True,
    },
    # liquid machinery pass 2026-10-05 (3e473f37c); disabledLiquidMachines is a private list (per-machine switches),
    # not a field this table can hold
    "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings": {
        "liquidHosesEnabled": True, "converterRateMultiplier": 1.0, "liquidWorksRuinsEnabled": True,
        "liquidWorksRuinStockEnabled": True, "industrialWorksBuildAnywhere": False, "pipeAdaptersEnabled": True,
    },
}
SETTINGS_SOURCES = {     # type -> C# file (relative to the mod's source folder)
    "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings": "RimMandrakeFlowWorksMod.cs",
    "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings": os.path.join("ManyWaters", "RiverSteamSettings.cs"),
    "RimMandrake.FlowWorks.Rivers.RM_RiversSettings": os.path.join("Rivers", "RM_RiversSettings.cs"),
    "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings": os.path.join("Machinery", "RM_MachinerySettings.cs"),
}
# Mod subclasses whose ModSettings files the run must restore byte-for-byte (plan 3.3).
MOD_CLASSES = ("RimMandrakeFlowWorksMod", "RiverSteamMod")   # PitsMod retired 2026-10-02


def toggles():
    """Every boolean Mod Settings field -- the toggle floor (plan 2.5: 27)."""
    return sorted(f for fields in SETTINGS.values() for f, v in fields.items() if isinstance(v, bool))


def settings_equal(got, want):
    """Bridge values come back as strings; compare by the default's type."""
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(got) - float(want)) < 1e-4
    except (TypeError, ValueError):
        return False


# --------------------------------------------------------------------- tools
EXISTING_TOOLS = (            # MEASURED: [Tool] names in JawaBench.BridgeTools / bench_tools_dump
    "rimworld/get_game_info", "rimworld/pause_game", "rimworld/step_game_ticks",
    "rimworld/screenshot_cell_rect", "rimworld/save_game", "rimworld/list_windows",
    "jawa/map_info", "jawa/list_things", "jawa/list_pawns", "jawa/destroy_batch",
    "jawa/set_terrain_batch", "jawa/get_terrain_batch", "jawa/get_terrain_layers",
    "jawa/set_roof_batch", "jawa/get_roof_batch", "jawa/set_fog", "jawa/paint_area",
    "jawa/weather_set", "jawa/weather_get", "jawa/game_condition", "jawa/incident_queue_clear",
    "jawa/cell_temperature", "jawa/time_clock", "jawa/time_set_ticks", "jawa/time_perf",
    "jawa/mod_settings_field", "jawa/type_probe", "jawa/research_bulk", "jawa/clear_ui",
    "jawa/flowworks_excavation_drive", "jawa/flowworks_excavation_report", "jawa/canal_cell_report",
)
P_B3_TOOLS = ("jawa/flowworks_excavation_drive", "jawa/flowworks_excavation_report",
              "jawa/canal_cell_report", "jawa/mod_settings_field")
# Built 2026-10-01 (JawaBenchFlowWorksNorthstarTools.cs + type_probe identity), not yet deployed
# or live-proven; callers still gate on the LIVE tool list. The response shape given here is the
# CONTRACT the tool meets; FakeFlowWorksGame implements exactly this shape and nothing else.
NEEDED_TOOLS = {
    "jawa/flowworks_body_report":
        "{x,z} -> success, classified (bool; the call itself classifies via RM_LiquidStock.BodyAt, "
        "which is the plan 3.4 'force classification once'), body{id, limitless, stock, capacity, "
        "cellCount, recededCount, truncated}, activeFluid, ticksGame",
    "jawa/flowworks_engine_state":
        "{} -> success, nextPulseTick, pulseIntervalTicks, activeFluid, rainAccumulator, "
        "excavatedCellCount, ticksGame (plan 6.11)",
    "jawa/type_probe+identity":
        "type_probe extended with assemblyLocation, assemblyMvid, assemblyFileSha256 for the "
        "loaded RimMandrake.FlowWorks assembly (plan 3.2 / 6.12, P-E6)",
}

# --------------------------------------------------------------------- layout
BUFFER = 8          # plan 3.4: bar footprint + 8-cell buffer
GAP = 12            # >= 12-cell gaps between buffered plots
EDGE_LIMITED = 15   # limited plots sit >= 15 cells from every edge
HALO = 15           # no natural water within 15 cells of a plot except its own reservoir
MIN_MAP = 200       # plan 3.4: size >= 200x200
SOIL = "Soil"
WET_OR_ROUGH = ("Water", "Marsh", "Mud", "Ice", "Lava")   # substrings refused near a plot

# Plot footprints are bar-derived (plan 2.3/2.4/2.5); bodies are rects RELATIVE to the plot.
# edge: None (interior, limited) | "west" | "east" (touches that edge; limitless/sink plots).
PLOTS = [
    {"id": "A", "w": 8, "h": 3, "bars": ["canal_reads_as_dug_channel", "canal_dry_reads_as_obstacle",
                                         "never_gravel_path"], "bodies": []},
    {"id": "B", "w": 6, "h": 7, "bars": ["canal_partial_fill_distinct", "fill_tier_legible"], "bodies": []},
    {"id": "D", "w": 18, "h": 5, "bars": ["reservoir_fill_visibly_drops", "never_full_reservoir_after_heavy_draw"],
     "bodies": [{"name": "D_pond", "terrain": "WaterShallow", "rect": (0, 0, 5, 5), "limitless": False}]},
    # E: tar pond is painted by the bar on its own working copy AFTER ActiveFluid=Tar (plan 2.3),
    # so the golden plot is bare Soil; the buffer is the 8-cell fire moat.
    {"id": "E", "w": 14, "h": 6, "bars": ["canal_burning_reads_as_burning_liquid", "canal_fire_reaches_reservoir",
                                          "canal_spent_after_burn"], "bodies": [],
     "deferred": [{"name": "E_tarpond", "fluid": "RM_Fluid_Tar", "rect": (0, 1, 4, 4)}]},
    {"id": "F", "w": 6, "h": 3, "bars": ["slime_reads_as_viscous_not_water", "slime_occupant_below_surface"],
     "bodies": []},
    {"id": "G", "w": 13, "h": 9, "bars": ["pit_reads_as_hole", "pit_occupant_below_floor", "pit_trapped_reads_as_trapped",
                                          "pit_occupied_distinguishable", "ladder_state_legible"], "bodies": []},
    {"id": "H", "w": 10, "h": 5, "bars": ["pit_depth_ladder_legible"], "bodies": []},
    {"id": "R", "w": 3, "h": 1, "bars": ["toggle:rainFillsExcavationsEnabled"], "bodies": [],
     # The rain twin is NOT roofed in the golden: MEASURED 2026-10-05 a lone roofed cell collapses within ~250
     # ticks (RoofConstructed AND RoofRockThick, even with a steel wall adjacent), leaving rubble in the plot.
     # The rain bar roofs its own cell on its working copy, right before the pulse it judges.
     "roofed": []},
    {"id": "K", "w": 32, "h": 2, "bars": ["toggle:sourceBudgetEnabled"],
     "bodies": [{"name": "K_pond", "terrain": "WaterShallow", "rect": (0, 0, 2, 2), "limitless": False}]},
    {"id": "C", "w": 20, "h": 12, "edge": "west",
     "bars": ["canal_fill_spreads_along_itself", "canal_fill_front_watchable", "canal_holds_only_the_channel",
              "canal_reads_as_same_liquid_as_reservoir", "never_liquid_on_open_ground"],
     "bodies": [{"name": "C_sea", "terrain": "WaterDeep", "rect": (0, 0, 8, 12), "limitless": True}]},
    {"id": "S", "w": 22, "h": 4, "edge": "east", "bars": ["toggle:edgeSinksEnabled"],
     "bodies": [{"name": "S_pond", "terrain": "WaterShallow", "rect": (0, 0, 4, 4), "limitless": False}]},
]


def _buffered(r, b=BUFFER):
    x, z, w, h = r
    return (x - b, z - b, w + 2 * b, h + 2 * b)


def _overlap_gap(a, b):
    """Smallest axis gap between two rects (negative = overlap)."""
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    gx = max(bx - (ax + aw), ax - (bx + bw))
    gz = max(bz - (az + ah), az - (bz + bh))
    return max(gx, gz)


def clip(r, size):
    x, z, w, h = r
    x0, z0 = max(0, x), max(0, z)
    x1, z1 = min(size[0], x + w), min(size[1], z + h)
    return (x0, z0, max(0, x1 - x0), max(0, z1 - z0))


def layout(size):
    """Place every plot on a map of `size` (W, Z). Deterministic; raises ValueError if it
    cannot honour plan 3.4. Returns [{id, rect, buffered, edge, bodies[abs], roofed[abs], ...}]."""
    W, Z = size
    if W < MIN_MAP or Z < MIN_MAP:
        raise ValueError("map %dx%d is below the plan 3.4 minimum %dx%d" % (W, Z, MIN_MAP, MIN_MAP))
    out = []
    # interior plots: row packer over buffered rects, footprints >= EDGE_LIMITED from edges
    lo = EDGE_LIMITED - BUFFER
    x, z, row_h = lo, lo, 0
    interior = [p for p in PLOTS if not p.get("edge")]
    for p in interior:
        bw, bh = p["w"] + 2 * BUFFER, p["h"] + 2 * BUFFER
        if x + bw > W - lo:
            x, z, row_h = lo, z + row_h + GAP, 0
        if z + bh > Z - lo:
            raise ValueError("interior plots do not fit on %dx%d" % (W, Z))
        out.append(_place(p, (x + BUFFER, z + BUFFER, p["w"], p["h"])))
        x += bw + GAP
        row_h = max(row_h, bh)
    # edge plots: top band, west and east edges
    top = z + row_h + GAP + BUFFER
    for p in (q for q in PLOTS if q.get("edge")):
        fz = top
        fx = 0 if p["edge"] == "west" else W - p["w"]
        if fz + p["h"] + BUFFER > Z:
            raise ValueError("edge plot %s does not fit on %dx%d" % (p["id"], W, Z))
        # C: the sea sits on the west edge. S: the pond sits at the plot's INNER (west) end and
        # the channel the bar digs runs east to the map edge -- both fall out of rect (0,0,..).
        out.append(_place(p, (fx, fz, p["w"], p["h"])))
    errs = validate_layout(out, size)
    if errs:
        raise ValueError("; ".join(errs))
    return out


def _place(p, rect):
    x, z = rect[0], rect[1]
    return {
        "id": p["id"], "rect": rect, "buffered": _buffered(rect), "edge": p.get("edge"),
        "bars": list(p["bars"]),
        "bodies": [dict(b, rect=(x + b["rect"][0], z + b["rect"][1], b["rect"][2], b["rect"][3]))
                   for b in p["bodies"]],
        "deferred": [dict(d, rect=(x + d["rect"][0], z + d["rect"][1], d["rect"][2], d["rect"][3]))
                     for d in p.get("deferred", ())],
        "roofed": [(x + dx, z + dz) for dx, dz in p.get("roofed", ())],
        # a roofed cell with no roof holder within range COLLAPSES on the first ticks, thick rock included
        # (MEASURED 2026-10-05: CollapsedRocks + Filth_RubbleRock): one steel wall in the buffer, north of it, holds it
        "supports": [(x + dx, z + dz - 1) for dx, dz in p.get("roofed", ())],
    }


def validate_layout(plots, size):
    W, Z = size
    errs = []
    for i, a in enumerate(plots):
        x, z, w, h = a["rect"]
        if x < 0 or z < 0 or x + w > W or z + h > Z:
            errs.append("%s off map" % a["id"])
        edge_d = min(x, z, W - (x + w), Z - (z + h))
        if a["edge"] is None and edge_d < EDGE_LIMITED:
            errs.append("limited plot %s is %d < %d from an edge" % (a["id"], edge_d, EDGE_LIMITED))
        if a["edge"] == "west" and x != 0:
            errs.append("%s must touch the west edge" % a["id"])
        if a["edge"] == "east" and x + w != W:
            errs.append("%s must touch the east edge" % a["id"])
        for b in a["bodies"]:
            bx, bz, bw, bh = b["rect"]
            if b["limitless"]:
                if bw * bh < 80:
                    errs.append("limitless body %s has %d < 80 cells" % (b["name"], bw * bh))
                if not (bx == 0 or bz == 0 or bx + bw == W or bz + bh == Z):
                    errs.append("limitless body %s does not touch the map edge" % b["name"])
            elif min(bx, bz, W - (bx + bw), Z - (bz + bh)) < EDGE_LIMITED:
                errs.append("limited body %s within %d of an edge" % (b["name"], EDGE_LIMITED))
        for b in plots[i + 1:]:
            g = _overlap_gap(clip(a["buffered"], size), clip(b["buffered"], size))
            if g < GAP:
                errs.append("plots %s/%s buffered gap %d < %d" % (a["id"], b["id"], g, GAP))
    return errs


def plots_from_json(plots):
    """A sidecar's plots after a JSON round trip (lists) -> the tuple form layout() returns."""
    out = []
    for p in plots:
        q = dict(p, rect=tuple(p["rect"]), buffered=tuple(p["buffered"]),
                 roofed=[tuple(c) for c in p.get("roofed", ())],
                 supports=[tuple(c) for c in p.get("supports", ())])
        q["bodies"] = [dict(b, rect=tuple(b["rect"])) for b in p.get("bodies", ())]
        q["deferred"] = [dict(d, rect=tuple(d["rect"])) for d in p.get("deferred", ())]
        out.append(q)
    return out


def plot_by_id(plots, pid):
    for p in plots:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def cells(rect):
    x, z, w, h = rect
    return [(cx, cz) for cx in range(x, x + w) for cz in range(z, z + h)]


def rect_str(r):
    return "%d,%d,%d,%d" % tuple(r)


# The rain twin's roof. MEASURED 2026-10-05: a lone RoofConstructed cell has no support and COLLAPSES on the first
# ticks (roof=none, Filth_RubbleBuilding left behind); a thick rock roof never collapses.
TWIN_ROOF = "RoofConstructed"
SUPPORT_THING = "Wall"


def expected_cells(plot, size):
    """The manifest model for one plot: {(x,z): {base, temp, roof, D, F, things}} over
    footprint + buffer (clipped to the map). Bodies are their terrain, the rain twin is
    roofed, everything else is bare Soil, unroofed, undug, empty."""
    want = {}
    for c in cells(clip(plot["buffered"], size)):
        want[c] = {"base": SOIL, "temp": "none", "roof": "none", "D": 0, "F": 0, "things": []}
    for b in plot["bodies"]:
        for c in cells(b["rect"]):
            want[c]["base"] = b["terrain"]
    for c in plot["roofed"]:
        want[c]["roof"] = TWIN_ROOF
    for c in plot.get("supports", ()):
        if c in want:
            want[c]["things"] = [SUPPORT_THING]
    return want


def check_points(plot):
    """Cells sampled for temperature / D-F spot reads: footprint corners + centre +
    every body's centre and every roofed cell (plan 3.5: source, excavated, shot cells)."""
    x, z, w, h = plot["rect"]
    pts = {(x, z), (x + w - 1, z), (x, z + h - 1), (x + w - 1, z + h - 1), (x + w // 2, z + h // 2)}
    for b in plot["bodies"]:
        bx, bz, bw, bh = b["rect"]
        pts.add((bx + bw // 2, bz + bh // 2))
    pts.update(plot["roofed"])
    return sorted(pts)


# --------------------------------------------------------------------- run-length reads
def parse_ops(ops, default=None):
    """'Def:x,z,w,h;Def:x,z,...' (the get_terrain_batch / get_roof_batch grammar) ->
    {(x,z): Def}. Bare 'x,z,w,h' entries take `default`. Raises on a malformed op."""
    out = {}
    for op in str(ops or "").replace("\n", ";").split(";"):
        op = op.strip()
        if not op:
            continue
        name, _, coords = op.rpartition(":")
        name = name or default
        parts = [int(v) for v in coords.split(",")]
        x, z = parts[0], parts[1]
        w = parts[2] if len(parts) > 2 else 1
        h = parts[3] if len(parts) > 3 else 1
        for c in cells((x, z, w, h)):
            out[c] = name
    return out


# --------------------------------------------------------------------- hashing
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root, exts=(".xml",)):
    """sha256 over (relpath, file sha256) of every file with `exts` under root, sorted."""
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            if f.lower().endswith(exts):
                p = os.path.join(dp, f)
                h.update(os.path.relpath(p, root).replace("\\", "/").encode())
                h.update(sha256_file(p).encode())
    return h.hexdigest()


def defs_hash(mod_dir=MOD_DIR):
    return tree_hash(os.path.join(mod_dir, "Defs"))


def read_prefs(prefs_path):
    """Render profile + autosave from Prefs.xml (read-only). Missing keys are absent, never 0."""
    import xml.etree.ElementTree as ET
    r = ET.parse(prefs_path).getroot()
    keys = ("screenWidth", "screenHeight", "fullscreen", "uiScale", "langFolderName",
            "textureCompression", "resetModsConfigOnCrash", "autosaveIntervalDays")
    return {k: r.findtext(k).strip() for k in keys if r.findtext(k) is not None}


RENDER_KEYS = ("screenWidth", "screenHeight", "fullscreen", "uiScale", "langFolderName", "textureCompression")


# --------------------------------------------------------------------- config backup / restore
def settings_files(config_dir):
    out = []
    for cls in MOD_CLASSES:
        out += glob.glob(os.path.join(config_dir, "Mod_*_%s.xml" % cls))
    return sorted(set(out))


def backup_configs(config_dir, out_dir, stamp=None):
    """Copy ModsConfig.xml + every FlowWorks ModSettings file byte-for-byte into out_dir and
    write a manifest with each sha256 (plan 3.1 / 3.3, GPT #6/#13). Returns the manifest path.
    A ModSettings file that does not exist is recorded as absent: restore then deletes any
    file the run created under that name pattern."""
    stamp = stamp or time.strftime("%Y%m%dT%H%M%S")
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    src = os.path.join(config_dir, "ModsConfig.xml")
    for path, label in [(src, "ModsConfig.pre-ns-flowworks.%s.xml" % stamp)] + \
            [(p, "%s.pre-ns-flowworks.%s.xml" % (os.path.splitext(os.path.basename(p))[0], stamp))
             for p in settings_files(config_dir)]:
        dst = os.path.join(out_dir, label)
        shutil.copyfile(path, dst)
        sha = sha256_file(path)
        if sha256_file(dst) != sha:
            raise IOError("backup of %s does not hash-match its source" % path)
        entries.append({"src": os.path.basename(path), "backup": label, "sha256": sha})
    man = {"stamp": stamp, "config_dir": config_dir, "entries": entries,
           "settings_patterns": ["Mod_*_%s.xml" % c for c in MOD_CLASSES]}
    mpath = os.path.join(out_dir, "ns_flowworks_backup.%s.json" % stamp)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    return mpath


def verify_backup(manifest_path):
    """[] when every backup file still hashes to its recorded sha; else the problems."""
    man = json.load(open(manifest_path, encoding="utf-8"))
    d = os.path.dirname(manifest_path)
    bad = []
    for e in man["entries"]:
        p = os.path.join(d, e["backup"])
        if not os.path.isfile(p):
            bad.append("missing backup %s" % e["backup"])
        elif sha256_file(p) != e["sha256"]:
            bad.append("backup %s no longer matches its recorded sha" % e["backup"])
    if not any(e["src"] == "ModsConfig.xml" for e in man["entries"]):
        bad.append("no ModsConfig.xml in the backup")
    return bad


def restore_configs(manifest_path, config_dir=None):
    """Put every backed-up file back by exact bytes, delete ModSettings files the run
    created, and prove each restored file hashes to the recorded sha. Re-runnable by hand:
      python3 src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py restore <manifest>"""
    man = json.load(open(manifest_path, encoding="utf-8"))
    config_dir = config_dir or man["config_dir"]
    d = os.path.dirname(manifest_path)
    kept = set()
    for e in man["entries"]:
        dst = os.path.join(config_dir, e["src"])
        shutil.copyfile(os.path.join(d, e["backup"]), dst)
        kept.add(e["src"])
    removed = []
    for p in settings_files(config_dir):
        if os.path.basename(p) not in kept:
            os.remove(p)
            removed.append(os.path.basename(p))
    bad = [e["src"] for e in man["entries"]
           if sha256_file(os.path.join(config_dir, e["src"])) != e["sha256"]]
    if bad:
        raise IOError("restore did not reproduce the recorded bytes for %s" % bad)
    return {"restored": sorted(kept), "removed": removed}
