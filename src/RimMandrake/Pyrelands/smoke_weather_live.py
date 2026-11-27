"""sc_smoke_weather_chokes (bar pyre_smoke_weather_chokes): one chain of the Pyrelands suite (validation.py registers it
through register()). The owner, 2026-11-13: "the choking smoke that sometimes come as its own weather". Claim: under the
choking smoke a colonist in the open gets the smoke's sign and breathes and moves worse; one under a roof gets nothing; the
smoke carries no rain, so a grass fire lit before it still burns; the sky reads as smoke, not ash fall or rain.

  smoke_weather_chokes   A fresh load of the registered site. The weather is locked Clear and left to settle (a whole
                         transition, WeatherManager.TransitionLerpFactor's 4000 ticks), so no earlier rain is still in the
                         sky when the fire is read. The scene, on open ground: a 5 x 5 steel room, roofed, with colonist R
                         inside; colonist O on open ground east of it; a 40 x 12 strip of grown ember grass far west of
                         both, with the burn line's wind pointed west (MapComponent_BurnLine.SetWindForTest), away from
                         the pawns. Both colonists are made Baseliners (no gene resists toxins) and drafted, so they stand
                         idle on their cells. Their health is read, the strip is lit on its east column, and once the fire
                         has taken the smoke is forced and locked (jawa/weather_set RM_FE_Weather_Smoke).
    reads                every hour for READ_HOURS: the weather (current, rainRate), both colonists' rows with health, the
                         fire and the ember grass on the strip. Captures of the sky over the scene: under Clear before the
                         smoke, at the first read where the sky is wholly smoke, and at the end.
    valid opportunity    the smoke stayed the weather at every read; both colonists stayed on their cells, alive, not
                         downed, in no mental state, with no hediff but the smoke's that they did not carry at the start;
                         O's ToxicEnvironmentResistance under RES_MAX; the fire took before the smoke. Else UNMEASURED.
    success              O carries RM_FE_SmokeChoke under its label at the end, at the stage the model of the shipped rates
                         names, with Breathing and Moving each lowered by at least half that stage's offset; R never
                         carries it and keeps its Breathing and Moving; a fire burns at the first full-smoke read and the
                         grass on the strip keeps falling over the hour after it; a blind judge reads smoke on the
                         captures (owed: UNMEASURED until a judge's verdict is given in $PYRE_SWC_JUDGE).
    forbidden            a rainRate over Fire.cs's extinguish line at any read (the only way weather puts a fire out); harm
                         to R; harm to O with no readable sign; a new Player.log error line.
    end                  READ_HOURS game hours after the smoke was forced.
    harness              the suite's heat guard takes a hot site's Heatstroke off both colonists right before each health
                         read (validation._heat_guard), so no stage of it lowers a capacity read here; a hediff still new
                         at a read is an UNMEASURED opportunity, never a verdict.

Ranges (the owner's 2026-11-16 rule: the bar's whole range before any code, offline):
  The game varies: the weather's blend (curWeather, lastWeather, the 4000-tick lerp) and so the smoke's share; the pawn
  (flesh or not, immune kinds, ToxicEnvironmentResistance from genes and gear), its cell (unroofed, built roof, thin rock,
  overhead mountain), the master switch and the smoke switch, the frequency, the beat's phase (map.uniqueID) and the
  hediff's own 200-tick phase; the smoke's duration (10000~30000) against the -2.4 a day recovery. Read live here: full
  smoke after a transition from Clear, a flesh Baseliner in the open, one under a built roof, the shipped rates, a grass
  fire under the smoke. Left out live, read offline over the kernel and the settings (T_SMOKE_WEATHER_ACCEPT, the fuzz
  family smoke, T_SETTINGS_SWEEP_OFFLINE): the switches off, the frequency, resistance between 0 and 1, non-flesh and
  immune kinds, thin rock and mountain roofs (Position.Roofed is one call for all three), the smoke's natural roll.
  Worldgen: none (standing ruling).

Run (the pyrelands tier, a free game, python.exe, the bridge env of that game; about half a game day at speed):
    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains smoke_weather_chokes
Offline: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_smoke_weather_live.py
"""
import datetime
import json
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE = "RM_FE_Weather_Smoke"            # Defs/WeatherDefs/Smoke.xml
CHOKE = "RM_FE_SmokeChoke"               # Defs/HediffDefs/RM_PyrelandsHediffs.xml
GRASS = "RM_FE_Plant_EmberGrass"
BURN = "RimMandrake.Pyrelands.MapComponent_BurnLine"
HEDIFF_XML = os.path.join(HERE, "Defs", "HediffDefs", "RM_PyrelandsHediffs.xml")
WEATHER_XML = os.path.join(HERE, "Defs", "WeatherDefs", "Smoke.xml")
KERNEL_CS = os.path.join(HERE, "Source", "Kernel", "RM_FireEcoKernel.cs")

HOUR = 2500                    # one game hour (validation.TEN_HOUR)
LERP_TICKS = 4000              # WeatherManager.TransitionLerpFactor: curWeatherAge / 4000 (decompile rw16)
HEDIFF_INTERVAL = 200          # HediffComp_SeverityModifierBase.SeverityUpdateInterval (decompile rw16)
RAIN_LINE = 0.01               # Fire.cs:312 (decompile rw16): RainRate > 0.01 puts out a fire under open sky
READ_HOURS = 7                 # the model's lowest O severity at 7 h clears "choking" by NET_HOUR (the selftest prints it)
NET_HOUR = 0.10                # the hediff's comment: +0.20 an hour gained, -0.10 recovered, +0.10 net in full smoke
RES_MAX = 0.5                  # 0.02 x (1 - res) per 250 ticks against 2.4 / 240 per 250 ticks: no net gain at res >= 0.5
CAP_EPS = 1e-3                 # our own rule: a capacity read back through JSON, a change under it is no change
BASELINER = "Baseliner"        # XenotypeDef (Data/Biotech/Defs/GeneDefs/XenotypeDefs.xml): no gene at all
PAD = (130, 215)               # our own pick, tried first: the scene (80 x 29 with its firebreak) fits a 250 map
PAD_STEP = 5                   # our own rule: when PAD's ground holds a thing no clearing removes, the next pads tried
#                                lie on a 5-cell grid, nearest PAD first (pick_pad)
STUCK_REACH = 1                # our own rule: a geyser's 2 x 2 footprint grown by one cell on each side, whatever its
#                                rotation (SteamGeyser size (2,2), destroyable false: Core Buildings_Natural.xml)
BEARING = 270                  # west: SetWindForTest's bearing (90 = +x), away from both colonists
STRIP_W, STRIP_H = 40, 12      # the fire's strip: about 4.7 cells an hour at the shipped pace (fire_catches_live's
#                                MEASURED day-one head of 113 cells), so 40 cells outlast READ_HOURS' first full-smoke hour
FIREBREAK = 6                  # cleared ground around the scene: over the burn line's HealReach (5, RM_BurnKernel)
GAP = 10                       # cells between the strip and the room's wall: over HealReach, so the fire cannot reach R
TAKE_TICKS = 250               # one SmokeCheckIntervalTicks: the spark's first spread before the smoke goes on
SHOT_PX = 1500                 # a capture's long side at most (the agents' image limit)
CAL_CELLS = 6                  # our own rule: the first capture's zoom probe, a rect this small at the sky's middle.
#                                play_zoom.shoot probes its first rect at the zoom the last call left, and refuses when
#                                that rect does not fit the screen (ArchSmall 2026-11-27: the 50 x 50 sky, 'Requested cell
#                                rectangle does not fit in the viewport'); a 6 x 6 rect fits at any zoom a scene leaves
PLANT_ENV = "PYRE_PLANT_SWC"   # the planted scene fault for the live twin: unroof (R's roof taken off as the smoke goes
#                                on; smoke_spares_roofed must FAIL)
JUDGE_ENV = "PYRE_SWC_JUDGE"   # a blind judge's verdict on the manifest's captures: "smoke" passes, anything else fails
OUT_ENV = "RM_SWC_DIR"


def kernel_numbers(path=KERNEL_CS):
    """Pure. The shipped rates from RM_FireEcoKernel.cs -> {"gain", "interval", "recovery"} (None for one not found)."""
    with open(path, encoding="utf-8") as f:
        src = f.read()

    def num(name):
        m = re.search(r"const\s+(?:float|int)\s+%s\s*=\s*([0-9.]+)f?\s*;" % name, src)
        return float(m.group(1)) if m else None
    return {"gain": num("SmokeGainPerCheck"), "interval": num("SmokeCheckIntervalTicks"),
            "recovery": num("SmokeRecoveryPerDay")}


def hediff_spec(text):
    """Pure. RM_PyrelandsHediffs.xml text -> {"label", "perDay", "max", "stages": [{"min", "label", "caps": {cap: offset}}]}
    of RM_FE_SmokeChoke; None when the def is absent."""
    root = ET.fromstring(text)
    for hd in root.iter("HediffDef"):
        if (hd.findtext("defName") or "").strip() != CHOKE:
            continue
        per_day = None
        for li in hd.iter("li"):
            if "SeverityPerDay" in (li.get("Class") or "") and li.findtext("severityPerDay") is not None:
                per_day = float(li.findtext("severityPerDay"))
        stages = []
        for st in (hd.find("stages") or []):
            caps = dict(((c.findtext("capacity") or "").strip(), float(c.findtext("offset") or 0))
                        for c in st.iter("li") if c.findtext("capacity"))
            stages.append({"min": float(st.findtext("minSeverity") or 0), "label": (st.findtext("label") or "").strip(),
                           "caps": caps})
        return {"label": (hd.findtext("label") or "").strip(), "perDay": per_day,
                "max": float(hd.findtext("maxSeverity") or 1), "stages": stages}
    return None


def weather_rates(text):
    """Pure. Smoke.xml text -> {"rainRate", "snowRate", "sandRate"} of RM_FE_Weather_Smoke; None when absent."""
    root = ET.fromstring(text)
    for wd in root.iter("WeatherDef"):
        if (wd.findtext("defName") or "").strip() == SMOKE:
            return dict((k, float(wd.findtext(k) or 0)) for k in ("rainRate", "snowRate", "sandRate"))
    return None


def stage_of(severity, spec):
    """Pure. A severity -> the stage it falls in (the last stage whose min it reaches), None for no severity."""
    if severity is None or not spec or not spec["stages"]:
        return None
    best = None
    for st in spec["stages"]:
        if severity >= st["min"]:
            best = st
    return best


def model_severity(ticks, res, nums, spec, gain_phase=0, hediff_phase=0):
    """Pure. The outdoor pawn's severity `ticks` after the smoke was forced over Clear: every `interval` ticks (at
    gain_phase) it gains gain x lerp x (1 - res), lerp = age / LERP_TICKS up to 1 (BlackRainShare with only the current
    weather smoke); every HEDIFF_INTERVAL ticks (at hediff_phase) the comp moves it by perDay / 300; Severity <= 0
    removes it (Hediff.ShouldRemove); a gain on no hediff makes one at the gain (HealthUtility.AdjustSeverity)."""
    sev = None
    step = int(nums["interval"])
    per = spec["perDay"] * (HEDIFF_INTERVAL / 60000.0)
    for a in range(1, int(ticks) + 1):
        if (a + gain_phase) % step == 0:
            g = nums["gain"] * min(1.0, a / float(LERP_TICKS)) * (1.0 - max(0.0, min(1.0, res)))
            if g > 0:
                sev = min(spec["max"], g if sev is None else sev + g)
        if sev is not None and (a + hediff_phase) % HEDIFF_INTERVAL == 0:
            sev += per
            if sev <= 0:
                sev = None
    return sev


def model_band(ticks, res, nums, spec):
    """Pure. The model over eight phase pairs -> (lowest, highest) severity (None counts as 0)."""
    vals = []
    for gp in (0, 62, 125, 187):
        for hp in (0, 100):
            v = model_severity(ticks, res, nums, spec, gp, hp)
            vals.append(0.0 if v is None else v)
    return min(vals), max(vals)


def smoke_of(row):
    """Pure. A list_pawns(includeHealth) row -> {"severity", "label"} of its RM_FE_SmokeChoke, None if it has none."""
    for h in (((row or {}).get("health") or {}).get("hediffs") or []):
        if isinstance(h, dict) and h.get("def") == CHOKE:
            return {"severity": h.get("severity"), "label": h.get("label")}
    return None


def caps_of(row):
    """Pure. A row -> {capacity: level} (only the capacities the pawn is capable of; Breathing and Moving read here)."""
    return dict((k, float(v)) for k, v in ((((row or {}).get("health") or {}).get("capacities") or {}).items())
                if isinstance(v, (int, float)))


def hediff_defs(row):
    """Pure. A row -> the set of its hediff defNames."""
    return set(h.get("def") for h in (((row or {}).get("health") or {}).get("hediffs") or []) if isinstance(h, dict))


def geometry(anchor):
    """Pure. The scene's cells from the pad -> dict of rects (x, z, w, h) and cells (x, z)."""
    ax, az = anchor
    room = (ax + 3, az - 3, 7, 7)                       # the steel ring and its 5 x 5 inside
    inner = (room[0] + 1, room[1] + 1, 5, 5)
    ring = [(x, z) for x in range(room[0], room[0] + 7) for z in range(room[1], room[1] + 7)
            if x in (room[0], room[0] + 6) or z in (room[1], room[1] + 6)]
    strip = (room[0] - GAP - STRIP_W, az - STRIP_H // 2, STRIP_W, STRIP_H)
    scene = (strip[0], az - 8, (ax + 20) - strip[0] + 1, 17)
    return {"room": room, "inner": inner, "ring": ring, "R": (ax + 6, az), "O": (ax + 16, az), "strip": strip,
            "spark": (strip[0] + STRIP_W - 1, strip[1], 1, STRIP_H), "scene": scene,
            "big": (scene[0] - FIREBREAK, scene[1] - FIREBREAK, scene[2] + 2 * FIREBREAK, scene[3] + 2 * FIREBREAK),
            "sky": (ax - 24, az - 24, 48, 48)}


def fits(geo, size):
    """Pure. The scene with its firebreak lies inside the map."""
    x, z, w, h = geo["big"]
    return x >= 0 and z >= 0 and x + w <= size[0] and z + h <= size[1]


def blocked(geo, stuck):
    """Pure. The things no clearing removes (cells (x, z), each a 2 x 2 footprint from its cell) that touch the scene
    with its firebreak, which _open_ground must leave bare. SITE (ArchSmall, 2026-11-27, site 1 tile 1496): a steam
    geyser at (143, 221) stood in PAD's scene and the stage read UNMEASURED, 'could not be made open ground'."""
    x, z, w, h = geo["big"]
    r = STUCK_REACH
    return [c for c in stuck or [] if c[0] + 1 + r >= x and c[0] - r < x + w and c[1] + 1 + r >= z and c[1] - r < z + h]


def pick_pad(stuck, size, first=PAD, step=PAD_STEP):
    """Pure. The pad for this map: `first` when its scene fits and no stuck thing touches it, else the nearest pad on a
    `step` grid that does; None when no pad on the map does (the stage reads UNMEASURED SITE, never a verdict)."""
    grid = sorted(((ax, az) for ax in range(0, size[0], step) for az in range(0, size[1], step)),
                  key=lambda a: ((a[0] - first[0]) ** 2 + (a[1] - first[1]) ** 2, a))
    for a in [tuple(first)] + grid:
        g = geometry(a)
        if fits(g, size) and not blocked(g, stuck):
            return a
    return None


def _row(rows, name, ok, worst, limit, cases):
    rows.append({"check": name, "ok": ok, "worst": worst, "limit": limit, "cases": cases})


def _cell(row):
    return (row.get("x"), row.get("z")) if isinstance(row, dict) else None


def judge_opportunity(reads, start, geo, res_o, fires_at_force):
    """Pure. reads [{"hour", "weather", "rainRate", "O", "R", "fire", "grass"}] in hour order; start {"O", "R"} rows read
    before the smoke; res_o O's ToxicEnvironmentResistance; fires_at_force the fire count on the strip as the smoke went
    on -> opportunity rows (a failed one is UNMEASURED: the scene, not the mod)."""
    opp = []
    n = len(reads)
    off = [r["weather"] for r in reads if r["weather"] != SMOKE]
    _row(opp, "the smoke is the weather at every read", n > 0 and not off, off[:1] or SMOKE, "== %s" % SMOKE, n)
    for who in ("O", "R"):
        want = tuple(geo[who])
        moved = [(r["hour"], _cell(r[who])) for r in reads if _cell(r[who]) != want]
        _row(opp, "%s stays on its cell" % who, n > 0 and not moved, moved[:1] or list(want), "== %r" % (want,), n)
        bad = [(r["hour"], "dead" if r[who].get("dead") else "downed" if r[who].get("downed") else r[who].get("mentalState"))
               for r in reads if r[who] and (r[who].get("dead") or r[who].get("downed") or r[who].get("mentalState"))]
        gone = [r["hour"] for r in reads if not r[who]]
        _row(opp, "%s alive, up and calm" % who, n > 0 and not bad and not gone, (bad or gone)[:1] or "ok",
             "no death, downing, mental state or missing row", n)
        base = hediff_defs(start.get(who))
        new = sorted(set(d for r in reads for d in hediff_defs(r[who]) - base - {CHOKE}))
        _row(opp, "%s gains no hediff but the smoke's" % who, n > 0 and not new, new[:3] or [], "== [] (start %d)" % len(base), n)
    _row(opp, "O's ToxicEnvironmentResistance", res_o is not None and res_o < RES_MAX, res_o, "< %.2f" % RES_MAX, 1)
    _row(opp, "the fire took before the smoke", bool(fires_at_force), fires_at_force, ">= 1 fire on the strip", 1)
    return opp


def judge_outdoor(start, end, spec, band):
    """Pure. O's start and end rows, the hediff spec, the model's (lowest, highest) severity at the end -> verdict rows."""
    ver = []
    s = smoke_of(end)
    sev = s["severity"] if s else None
    _row(ver, "O carries %s" % CHOKE, s is not None and isinstance(sev, (int, float)) and sev > 0, sev, "> 0", 1)
    want = spec["label"] if spec else None
    got = (s or {}).get("label") or ""
    _row(ver, "O's sign reads its label", bool(want) and got.startswith(want), got or None, "starts %r" % want, 1)
    model_stage = stage_of(band[0], spec)
    stage = stage_of(sev, spec)
    _row(ver, "O's stage at the end is the model's", stage is not None and model_stage is not None
         and stage["min"] >= model_stage["min"], stage["label"] if stage else None,
         ">= %r (model lowest %.3f, highest %.3f)" % (model_stage["label"] if model_stage else None, band[0], band[1]), 1)
    c0, c1 = caps_of(start), caps_of(end)
    for cap in ("Breathing", "Moving"):
        off = abs((stage or {}).get("caps", {}).get(cap, 0.0))
        drop = (c0[cap] - c1[cap]) if cap in c0 and cap in c1 else None
        _row(ver, "O's %s lowered" % cap, drop is not None and off > 0 and drop >= off / 2 - 1e-9,
             None if drop is None else round(drop, 4), ">= %.3f (half the %s stage's offset)"
             % (off / 2, (stage or {}).get("label")), 1)
    return ver


def judge_roofed(start, reads):
    """Pure. R's start row and every read -> verdict rows: never the smoke's sign, Breathing and Moving kept."""
    ver = []
    had = [(r["hour"], (smoke_of(r["R"]) or {}).get("severity")) for r in reads if smoke_of(r["R"])]
    _row(ver, "R never carries %s" % CHOKE, bool(reads) and not had, had[:1] or 0, "== 0 reads with it", len(reads))
    c0 = caps_of(start)
    for cap in ("Breathing", "Moving"):
        drops = [c0[cap] - caps_of(r["R"]).get(cap, -1.0) for r in reads] if cap in c0 else []
        worst = max(drops) if drops else None
        _row(ver, "R's %s kept" % cap, worst is not None and worst <= CAP_EPS, None if worst is None else round(worst, 4),
             "<= %g below the start" % CAP_EPS, len(drops))
    return ver


def full_smoke_hour(reads):
    """Pure. The first read hour whose sky is wholly smoke: forced at hour 0, the lerp is whole at LERP_TICKS."""
    for r in reads:
        if r["hour"] * HOUR >= LERP_TICKS:
            return r["hour"]
    return None


def judge_fire(reads):
    """Pure. reads -> verdict rows: no rain at any read, a fire at the first full-smoke read, the grass falling after it."""
    ver = []
    rains = [r.get("rainRate") for r in reads]
    worst = max([x for x in rains if isinstance(x, (int, float))] or [None]) if rains else None
    _row(ver, "rainRate under the smoke", bool(reads) and all(isinstance(x, (int, float)) for x in rains)
         and worst <= RAIN_LINE, worst, "<= %g (Fire.cs:312)" % RAIN_LINE, len(reads))
    h = full_smoke_hour(reads)
    by = dict((r["hour"], r) for r in reads)
    at, nxt = by.get(h), by.get(h + 1) if h is not None else None
    _row(ver, "a fire burns at the first full-smoke read", bool(at) and (at.get("fire") or 0) > 0,
         (at or {}).get("fire"), ">= 1 at hour %r" % h, 1)
    fell = None if not at or not nxt else (at.get("grass") or 0) - (nxt.get("grass") or 0)
    _row(ver, "the strip's grass keeps falling under full smoke", fell is not None and fell > 0, fell,
         "> 0 plants from hour %r to %r" % (h, None if h is None else h + 1), 2)
    return ver


def judge_captures(shots, judge):
    """Pure. shots [{"label", "path"}], judge the blind judge's word (None: not yet read) -> (opp, ver)."""
    opp, ver = [], []
    _row(opp, "captures taken", bool(shots) and all(s.get("path") for s in shots),
         sum(1 for s in shots if s.get("path")), "== %d" % len(shots), len(shots))
    ok = None if judge is None else str(judge).strip().lower() == "smoke"
    _row(ver, "a blind judge reads smoke, not ash fall or rain", ok, judge, "'smoke' (judge on the manifest's captures)", 1)
    return opp, ver


def shot_ppc(rect):
    """Pure. Pixels per cell so the capture's long side stays at or under SHOT_PX, at least 4."""
    return max(4, SHOT_PX // max(rect[2], rect[3]))


def calibration_rect(rect, cells=None):
    """Pure. The zoom probe's rect: `cells` (CAL_CELLS) square at the middle of `rect`."""
    c = cells or CAL_CELLS
    return (rect[0] + (rect[2] - c) // 2, rect[1] + (rect[3] - c) // 2, c, c)


def error_lines(lines):
    """Pure. _log_since lines -> the error and exception lines (the contract: a new error line in Player.log)."""
    return [str(m.get("text", ""))[:240] for m in lines or []
            if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception")]


def out_dir(stamp=None):
    """Where the manifest goes: $RM_SWC_DIR, else D:\\ClaudeWork\\rimmandrake\\smoke_weather\\<stamp>."""
    base = os.environ.get(OUT_ENV)
    if not base:
        root = r"D:\ClaudeWork\rimmandrake\smoke_weather" if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/smoke_weather"
        base = os.path.join(root, stamp or datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return base


def write_manifest(path_dir, data):
    os.makedirs(path_dir, exist_ok=True)
    p = os.path.join(path_dir, "manifest.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    return p


def print_rows(tag, rows):
    for r in rows:
        print("[swc-check] %s: %s: %s worst=%r limit=%s cases=%d" % (
            tag, r["check"], "ok" if r["ok"] else ("OWED" if r["ok"] is None else "NOT"), r["worst"], r["limit"],
            r["cases"]), flush=True)


def register(suite, V):
    """Adds smoke_weather_chokes to the Pyrelands suite. V is validation.py's namespace (its helpers and constants)."""
    state = {}

    def rows_of(t):
        r = t.bridge_call("jawa/list_pawns", includeHealth=True, includeCorpses=True, limit=500)
        if not V._live(t):
            return {}, {}
        by = dict((p.get("id"), p) for p in ((r or {}).get("pawns") or []))
        return by.get(state.get("O")), by.get(state.get("R"))

    def read(t, hour):
        g = state["geo"]
        if V._heat_guarded(t):   # the suite's heat guard (a hot site's Heatstroke off the colonists) right before the read,
            V._heat_guard(t, "smoke read")   # so a stage of it never lowers a capacity that is read here
        w = t.bridge_call("jawa/weather_get") or {}
        wd = w.get("weather") if isinstance(w, dict) else None
        o, r = rows_of(t)
        return {"hour": hour, "weather": V.weather_name(wd), "rainRate": (wd or {}).get("rainRate"),
                "age": (wd or {}).get("curWeatherAge"), "O": o, "R": r,
                "fire": V._count(t, "Fire", V._rs(g["big"])), "grass": V._count(t, GRASS, V._rs(g["strip"]))}

    def shot(t, label):
        rect = V.padded_inside(state["geo"]["sky"], V._map_size(t)) if V._live(t) else state["geo"]["sky"]
        if CAL_CELLS and not state.get("zoomProbe"):   # learns the zoom on a rect that fits; never judged, never listed
            state["zoomProbe"] = t.screenshot(name="swc_zoomprobe", rect=calibration_rect(rect), ppc=shot_ppc(rect))
        path = t.screenshot(name="swc_%s" % label, rect=tuple(rect), ppc=shot_ppc(rect))
        state["shots"].append({"label": label, "path": path, "rect": list(rect)})

    def stuck_things(t):
        """The cells of every thing on the map that no clearing removes (validation's RUIN_NOT_A_RUIN: the geysers);
        UNMEASURED when a count cannot be read, never an empty list read as none."""
        out = []
        for d in V.RUIN_NOT_A_RUIN:
            r = t.bridge_call("jawa/list_things", defName=d, limit=500)
            if not V._live(t):
                return []
            if not isinstance(r, dict) or "countMatched" not in r or not r.get("scanned") \
                    or len(r.get("things") or []) != r.get("countMatched"):
                V._unmeasured(t, "SITE: list_things(%s) unreadable: %r" % (d, str(r)[:200]))
            out += [(th.get("x"), th.get("z")) for th in r.get("things") or []]
        return out

    def save():
        state["manifest"] = write_manifest(state["dir"], dict(
            (k, state.get(k)) for k in ("scene", "pad", "stuck", "geo", "numbers", "spec", "band", "res", "start",
                                        "reads", "shots", "firesAtForce", "plantedFault", "judge")))

    def judged(t, tag, opp, ver):
        print_rows(tag, opp + ver)
        save()
        bad_o = [r for r in opp if not r["ok"]]
        bad_v = [r for r in ver if r["ok"] is False]
        owed = [r for r in ver if r["ok"] is None]
        V._note(t, "%s: the checks" % tag, {"manifest": state.get("manifest"), "not": [r["check"] for r in bad_o + bad_v],
                                            "owed": [r["check"] for r in owed]})
        if bad_o:
            V._unmeasured(t, "%s: %s" % (tag, "; ".join("%s %r (limit %s)" % (r["check"], r["worst"], r["limit"])
                                                        for r in bad_o)))
        if bad_v:
            V._fail("%s: %s" % (tag, "; ".join("%s %r (limit %s, %d cases)" % (r["check"], r["worst"], r["limit"],
                                                                               r["cases"]) for r in bad_v)))
        if owed:
            V._unmeasured(t, "%s: owed: %s (manifest %s)" % (tag, ", ".join(r["check"] for r in owed), state.get("manifest")))

    def opportunity():
        return judge_opportunity(state["reads"], state["start"], state["geo"], state.get("res"), state.get("firesAtForce"))

    @suite.chain("smoke_weather_chokes")
    @V._teardown(fire=True, weather=True)
    def smoke_weather_chokes(t):
        state.clear()
        state.update(dir=out_dir(), scene="sc_smoke_weather_chokes", shots=[], reads=[],
                     plantedFault=os.environ.get(PLANT_ENV) or None, judge=os.environ.get(JUDGE_ENV) or None)
        with open(HEDIFF_XML, encoding="utf-8") as f:
            spec = hediff_spec(f.read())
        nums = kernel_numbers()
        state.update(spec=spec, numbers=nums)
        with V._comp(t, "smoke_weather_stage"):
            if V._live(t):
                mid, why = V._load_registered_site(t)   # the contract: a fresh map
                if mid is None:
                    V._unmeasured(t, "SITE: %s" % why)
            # red-first (contract): the 0.1.0 build has no smoke weather to force, and that is the mod's FAIL
            V._get_defs(t, "WeatherDef/%s;HediffDef/%s" % (SMOKE, CHOKE), "label")
            V._pad(t, PAD)
            if V._live(t):
                state["stuck"] = stuck_things(t)
                state["pad"] = pick_pad(state["stuck"], V._map_size(t))
                print("[swc-check] pad %r (PAD %r): %d stuck thing(s) on the map, %d in PAD's scene" % (
                    state["pad"], PAD, len(state["stuck"]), len(blocked(geometry(PAD), state["stuck"]))), flush=True)
                if state["pad"] is None:
                    V._unmeasured(t, "SITE: no pad on the map clears the geysers %r" % state["stuck"])
                V._pad(t, state["pad"])
            g = geometry(t.anchor)
            state["geo"] = g
            if V._live(t) and not fits(g, V._map_size(t)):
                V._unmeasured(t, "SITE: the scene %r does not fit the map %r" % (g["big"], V._map_size(t)))
            if state["plantedFault"]:
                V._note(t, "PLANTED FAULT", "%s=%s" % (PLANT_ENV, state["plantedFault"]))
            if V._live(t) and V._ten_gate_on(t) is not True:
                V._unmeasured(t, "PyrelandsMechanicsGate.On is not true: the mod's mechanics are off on this game")
            V._set(t, {"smokeWeatherEnabled": True})
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            V._open_ground(t, g["scene"], margin=FIREBREAK)
            t.bridge_call("jawa/build_batch", ops=";".join("Wall:%d,%d" % c for c in g["ring"]), stuff="Steel",
                          faction="player")
            t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % V._rs(g["room"]))
            state["O"] = V._spawn_colonist(t, *g["O"])
            state["R"] = V._spawn_colonist(t, *g["R"])
            res = {}
            for who in ("O", "R"):
                pid = state[who]
                if pid:
                    t.bridge_call("jawa/pawn_genes", pawn=pid, action="xenotype", xenotype=BASELINER)
                    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
                    st = t.bridge_call("jawa/pawn_stats", pawn=pid, stats="ToxicEnvironmentResistance")
                    vals = dict((s.get("defName"), s.get("value")) for s in ((st or {}).get("stats") or []))
                    res[who] = vals.get("ToxicEnvironmentResistance")
            state["res"] = res.get("O")
            V._plants(t, GRASS, g["strip"], growth=1.0)
            t.bridge_call("jawa/static_call", type=BURN, method="SetWindForTest", args=str(BEARING))
            V._wait(t, LERP_TICKS)     # Clear wholly in: no earlier weather's rain is left in the sky
            if V._heat_guarded(t):
                V._heat_guard(t, "smoke start read")
            o, r = rows_of(t)
            state["start"] = {"O": o, "R": r, "res": res}
            state["band"] = model_band(READ_HOURS * HOUR, state["res"] or 0.0, nums, spec)
            print("[swc-check] model: O at %d h lowest %.3f highest %.3f (choking from %.2f; limit lowest >= %.2f) at res "
                  "%r" % (READ_HOURS, state["band"][0], state["band"][1], spec["stages"][1]["min"],
                          spec["stages"][1]["min"] + NET_HOUR, state["res"]), flush=True)
            shot(t, "clear_before")
            V._fire(t, g["spark"])
            V._wait(t, TAKE_TICKS)
            state["firesAtForce"] = V._count(t, "Fire", V._rs(g["big"]))
            state["mark"] = V._log_mark(t)
            forced = SMOKE
            t.bridge_call("jawa/weather_set", weather=forced, lockWeather=True)   # unlocked by the chain's teardown
            now = V.weather_name(((t.bridge_call("jawa/weather_get") or {}).get("weather"))) if V._live(t) else SMOKE
            if state["plantedFault"] == "unroof":
                t.bridge_call("jawa/set_roof_batch", ops="None:%s" % V._rs(g["room"]))
            if V._live(t):
                save()
                if not state["O"] or not state["R"]:
                    V._unmeasured(t, "a colonist could not be spawned: O %r, R %r" % (state["O"], state["R"]))
                if now != forced:
                    V._fail("the smoke could not be forced: weather_set %s left %r" % (forced, now))
        V._independent(t)
        with V._comp(t, "smoke_weather_reads"):
            if not state.get("start"):
                V._unmeasured(t, "the stage did not finish")
            full = None
            for h in range(1, READ_HOURS + 1):
                V._wait(t, HOUR)
                if not V._live(t):
                    break
                state["reads"].append(read(t, h))
                if full is None and h * HOUR >= LERP_TICKS:
                    full = h
                    shot(t, "smoke_full")
            shot(t, "smoke_end")
            if V._live(t):
                save()
                print("[swc-check] reads: %d (limit %d)" % (len(state["reads"]), READ_HOURS), flush=True)
                if len(state["reads"]) != READ_HOURS:
                    V._unmeasured(t, "%d reads of %d" % (len(state["reads"]), READ_HOURS))
        V._independent(t)
        with V._comp(t, "smoke_chokes_outdoors"):
            if V._live(t):
                if not state.get("reads"):
                    V._unmeasured(t, "no reads")
                judged(t, "outdoor", opportunity(),
                       judge_outdoor(state["start"]["O"], state["reads"][-1]["O"], state["spec"], state["band"]))
        V._independent(t)
        with V._comp(t, "smoke_spares_roofed"):
            if V._live(t):
                if not state.get("reads"):
                    V._unmeasured(t, "no reads")
                judged(t, "roofed", opportunity(), judge_roofed(state["start"]["R"], state["reads"]))
        V._independent(t)
        with V._comp(t, "smoke_puts_out_no_fire"):
            if V._live(t):
                if not state.get("reads"):
                    V._unmeasured(t, "no reads")
                judged(t, "fire", opportunity(), judge_fire(state["reads"]))
        V._independent(t)
        with V._comp(t, "smoke_sky_reads_as_smoke"):
            if V._live(t):
                opp, ver = judge_captures(state["shots"], state.get("judge"))
                judged(t, "sky", opp, ver)
        V._independent(t)
        with V._comp(t, "smoke_weather_no_error_line"):
            lines = V._log_since(t, state.get("mark"))
            if V._live(t):
                errs = error_lines(lines)
                print("[swc-check] error lines since the mark: %d (limit 0) of %d lines read" % (len(errs), len(lines)),
                      flush=True)
                V._note(t, "error lines since the scene's mark", {"errors": errs[:5], "lines": len(lines)})
                if errs:
                    V._fail("%d new error line(s) in the log: %r" % (len(errs), errs[:2]))
        # housekeeping (owner 2026-11-17): the room's roof off; the next chain loads a fresh site anyway
        if state.get("geo"):
            t.bridge_call("jawa/set_roof_batch", ops="None:%s" % V._rs(state["geo"]["room"]))
