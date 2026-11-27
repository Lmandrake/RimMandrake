"""sc_grass_seen_under_ash (bar grass_still_seen_under_ash, vision.md 0.2.0 item 16): one chain of the Pyrelands suite
(validation.py registers it through register()). Kind A. Claim: after ash falls, standing grass is drawn under the ash, and
bare ash shows only where no grass stands. 2026-11-16: 685 grass plants in 777 cells were drawn as bare ash.

  grass_seen_under_ash   A fresh load of the registered site. Two frames side by side on the site's own grass carpet:
                         frame G replanted with grown ember grass, frame B with every plant cleared, a firebreak round both.
                         The ash fall is forced until G reads a named depth, then clear is forced (600 ticks, the contract,
                         and at least the 4,000 ticks a weather takes to fade in, so no fall overlay is read); per cell of
                         both frames the probe lists the grown grass (inspect pane) and the ash depth (SandGrid), and one
                         capture of each frame is taken at play zoom between 10h and 14h. Two regimes, one pair each:
                           light  G's median depth in [0.08, 0.40): the light dust band of RM_FireEcoKernel
                           deep   G's median depth >= 0.50: full dust and solid ash cover (the 2026-11-16 regime)
                         The verdict on each pair is a BLIND judge's (grass_under_ash_judge.py prepare / score); the
                         chain's components read the valid opportunity and the forbidden effects that code can see.

Run (the pyrelands tier, a free game, python.exe, the bridge env of that game):
    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_seen_under_ash
then  python3 src/RimMandrake/Pyrelands/grass_under_ash_judge.py prepare <manifest>   (one blind pair per regime)
Offline: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_grass_under_ash.py
"""
import datetime
import json
import os
import statistics

GRASS = "RM_FE_Plant_EmberGrass"
FRAME_W, FRAME_H = 12, 8       # one frame: 12 x 8 cells, 96 cells; at play zoom (64 px a cell) +1 cell pad, 896 x 640 px
GAP = 4                        # cells between G and B; a cleared border round B keeps G's blades out of B's capture
WINDOW_W = 2 * FRAME_W + GAP   # the pair's window, scanned over the site for the densest natural ember grass
SCAN_STEP_X, SCAN_STEP_Z = 14, 8   # scan grid; MEASURED 2026-11-26 on the site: 338 windows, best 189/224 grass
EDGE = 20                      # a window keeps 20 cells off the map edge: firebreak (4) + capture pad (1) + slack
BREAK_MARGIN = 2               # the firebreak ring lies this far outside the window
BREAK_WIDTH = 4                # validation._firebreak's default width
VISIBLE = 0.03                 # RM_FireEcoKernel.AshVisibleDepth: ash at all
LIGHT_LO, LIGHT_HI = 0.08, 0.40    # RM_FireEcoKernel.AshDustLightDepth / AshDustFullDepth: the light dust band
SOLID = 0.50                   # RM_FireEcoKernel.AshCoverOpacity is solid from 0.5 depth
LIGHT_STOP = 0.15              # stop the light fall here: inside the band with room for an hour of overshoot and dry wear
LIGHT_CEIL = 0.35              # the light fall also stops once either frame's mean reads this: LIGHT_HI less 0.05, about one
                               # hour of fall (MEASURED 2026-11-27: 0.054..0.061 a fall hour), so neither frame leaves the band
DEEP_STOP = 0.60               # stop the deep fall here: SOLID + 0.1 (dry wear, RM_FireEcoKernel 0.1 depth a day)
LIGHT_CAP_H, DEEP_CAP_H = 8, 24    # fall hours before the regime is called unreached (kernel: full dust at ~8 h of fall)
CLEAR_TICKS = 600              # the contract: clear forced 600 ticks
FADE_TICKS = 4000              # WeatherManager: a new weather is fully in after 4000 ticks (stage_review.TRANSITION_TICKS)
MOST = 0.5                     # "most open cells": more than half
MATURE = 1.0                   # plant_growth_of_lines: "Mature." reads 1.0, the plant's own word for grown
HOUR = 2500
START_LO, START_HI = 6, 9      # the light fall starts here, so it ends before the 10h-14h capture window
SHOT_LO, SHOT_HI = 10, 14      # validation._ten_noon_hour's capture window
PLANT_ENV = "PYRE_PLANT_GSUA"  # planted scene faults for the selftest's live twin: fire_in_g | grass_in_b
OUT_ENV = "RM_GSUA_DIR"


def scan_windows(size, step_x=SCAN_STEP_X, step_z=SCAN_STEP_Z, edge=EDGE, w=WINDOW_W, h=FRAME_H):
    """Pure. Map size (sx, sz) -> [(x, z)] corners of the pair's window, every window `edge` cells off the map edge."""
    sx, sz = size
    return [(x, z) for x in range(edge, sx - edge - w + 1, step_x) for z in range(edge, sz - edge - h + 1, step_z)]


def pick_window(counts):
    """Pure. [(grass count, x, z)] -> (x, z) of the densest window, ties to the lowest (x, z); None for none counted."""
    rows = [r for r in counts if isinstance(r[0], int)]
    if not rows:
        return None
    best = max(r[0] for r in rows)
    return min((r[1], r[2]) for r in rows if r[0] == best)


def frames_of(x, z):
    """Pure. Window corner -> (G, B, B's cleared border, the firebreak's inner rect), each (x, z, w, h)."""
    g = (x, z, FRAME_W, FRAME_H)
    b = (x + FRAME_W + GAP, z, FRAME_W, FRAME_H)
    border = (b[0] - GAP // 2, z - GAP // 2, FRAME_W + GAP, FRAME_H + GAP)
    ring = (x - BREAK_MARGIN, z - BREAK_MARGIN, WINDOW_W + 2 * BREAK_MARGIN, FRAME_H + 2 * BREAK_MARGIN)
    return g, b, border, ring


def cells_of(rect):
    x, z, w, h = rect
    return [(x + i, z + j) for j in range(h) for i in range(w)]


def grown_cells(rows, growth_of):
    """Pure. jawa/inspect_string things[] -> set of cells holding ember grass that reads grown (MATURE)."""
    out = set()
    for r in rows or []:
        if not isinstance(r, dict) or r.get("defName") != GRASS:
            continue
        g = growth_of(r.get("lines") or r.get("inspect") or [])
        if g is not None and g >= MATURE and r.get("x") is not None and r.get("z") is not None:
            out.add((int(r["x"]), int(r["z"])))
    return out


def regime_ok(regime, median):
    """Pure. Does a median depth sit in the regime the pair names?"""
    if median is None:
        return False
    if regime == "light":
        return LIGHT_LO <= median < LIGHT_HI
    if regime == "deep":
        return median >= SOLID
    raise ValueError("unknown regime %r" % regime)


def fall_done(g_mean, b_mean, stop, ceiling=None):
    """Whether the forced fall has done its work: BOTH frames' mean depth at `stop` (the regime asks it of G and of B), or
    either frame at `ceiling` (the light band's top, so neither leaves the band). MEASURED 2026-11-27 on ArchSmall (0.2.0
    build): G's ash ran ahead of B's (light G 0.2445 / B 0.167, deep G 0.6135 / B 0.404), so a stop read on G alone left B
    short of the deep regime and the pair unmeasured; on 0.1.0 (2026-11-26) B ran ahead. A missing read is not done."""
    if g_mean is None or b_mean is None:
        return False
    if ceiling is not None and max(g_mean, b_mean) >= ceiling:
        return True
    return min(g_mean, b_mean) >= stop


def frame_read(rect, depth, grown, plants, fires):
    """Pure. One frame's read -> dict. depth {cell: depth}; grown the set of grown-grass cells; plants the count of any
    plant in the frame; fires the fire cells inside the frame (or its pad)."""
    cells = cells_of(rect)
    ds = [depth.get(c) for c in cells]
    have = [d for d in ds if d is not None]
    return {"rect": list(rect), "cells": len(cells), "depthRead": len(have),
            "median": round(statistics.median(have), 4) if have else None, "min": round(min(have), 4) if have else None,
            "max": round(max(have), 4) if have else None,
            "ashedShare": (sum(1 for d in have if d >= VISIBLE) / float(len(cells))) if cells else 0.0,
            "grown": len(set(grown) & set(cells)), "grownShare": len(set(grown) & set(cells)) / float(len(cells)),
            "grownUnderAsh": sum(1 for c in cells if c in grown and (depth.get(c) or 0) >= VISIBLE),
            "plants": plants, "fires": len(fires or [])}


def opportunity(regime, g, b, weather, clear_age):
    """Pure. (regime, G's frame_read, B's frame_read, the weather at the captures, ticks of clear) -> (ok, why, rows).
    rows: one check line each, printing the worst value, the limit and the cases read. ok False is no valid opportunity
    (UNMEASURED), never a verdict on the mod."""
    rows = []

    def row(name, ok, worst, limit, cases):
        rows.append({"check": name, "ok": bool(ok), "worst": worst, "limit": limit, "cases": cases})

    row("G grown ember grass share", g["grownShare"] > MOST, round(g["grownShare"], 3), "> %.2f" % MOST, g["cells"])
    row("G cells with ash", g["ashedShare"] > MOST, round(g["ashedShare"], 3), "> %.2f at >= %.2f" % (MOST, VISIBLE),
        g["depthRead"])
    row("G median depth in the %s regime" % regime, regime_ok(regime, g["median"]), g["median"],
        "[%.2f, %.2f)" % (LIGHT_LO, LIGHT_HI) if regime == "light" else ">= %.2f" % SOLID, g["depthRead"])
    row("B plants", b["plants"] == 0, b["plants"], "== 0", b["cells"])
    row("B cells with ash", b["ashedShare"] > MOST, round(b["ashedShare"], 3), "> %.2f at >= %.2f" % (MOST, VISIBLE),
        b["depthRead"])
    row("B median depth in the %s regime" % regime, regime_ok(regime, b["median"]), b["median"],
        "[%.2f, %.2f)" % (LIGHT_LO, LIGHT_HI) if regime == "light" else ">= %.2f" % SOLID, b["depthRead"])
    row("fires in either frame", g["fires"] + b["fires"] == 0, g["fires"] + b["fires"], "== 0", 2)
    row("weather at the captures", weather == "Clear", weather, "Clear", 1)
    row("ticks of clear before the captures", (clear_age or 0) >= max(CLEAR_TICKS, FADE_TICKS), clear_age,
        ">= %d" % max(CLEAR_TICKS, FADE_TICKS), 1)
    bad = [r for r in rows if not r["ok"]]
    if bad:
        return False, "; ".join("%s %r (limit %s)" % (r["check"], r["worst"], r["limit"]) for r in bad), rows
    return True, "%d of %d opportunity checks hold" % (len(rows), len(rows)), rows


def error_lines(lines):
    """Pure. _log_since lines -> the error and exception lines (the contract: a new error line in Player.log)."""
    return [str(m.get("text", ""))[:240] for m in lines or []
            if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception")]


def out_dir(stamp=None):
    """Where the manifest goes: $RM_GSUA_DIR, else D:\\ClaudeWork\\rimmandrake\\grass_under_ash\\<stamp> (scratch: a
    program, the judge script, reads it)."""
    base = os.environ.get(OUT_ENV)
    if not base:
        root = r"D:\ClaudeWork\rimmandrake\grass_under_ash" if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/grass_under_ash"
        base = os.path.join(root, stamp or datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return base


def write_manifest(path_dir, data):
    os.makedirs(path_dir, exist_ok=True)
    p = os.path.join(path_dir, "manifest.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    return p


def register(suite, V):
    """Adds grass_seen_under_ash to the Pyrelands suite. V is validation.py's namespace (its helpers and constants)."""
    state = {}

    def depth_map(t, rect):
        out = {}
        for c in cells_of(rect):
            a = V._ash(t, "%d,%d,1,1" % c)
            if a:
                out[c] = float(a.get("depthSum") or 0.0)
        return out

    def grown_in(t, rect):
        r = t.bridge_call("jawa/inspect_string", rect=V._rs(rect), limit=4 * rect[2] * rect[3])
        if not V._live(t):
            return set()
        rows = (r or {}).get("things")
        if not isinstance(rows, list):
            V._unmeasured(t, "inspect_string over %s unreadable: %r" % (V._rs(rect), str(r)[:200]))
        return grown_cells(rows, V.plant_growth_of_lines)

    def plants_in(t, rect):
        r = t.bridge_call("jawa/list_things", group="Plant", rect=V._rs(rect), limit=1)
        if not V._live(t):
            return 0
        if not isinstance(r, dict) or "countMatched" not in r:
            V._unmeasured(t, "list_things group=Plant over %s unreadable: %r" % (V._rs(rect), str(r)[:200]))
        return int(r["countMatched"])

    def fires_in(t, rect):
        cells, _unplaced = V.fire_cells(V._things(t, "Fire", V._rs(rect), limit=2000))
        return cells

    def weather_now(t):
        a = V._ash(t, V._rs(state["g"]))
        return a.get("weather") if a else None

    def mean_depth(t, rect):
        a = V._ash(t, V._rs(rect))
        return float(a.get("depthSum") or 0.0) / max(1, int(a.get("cells") or 0)) if a else None

    def fall_until(t, stop, cap_h, ceiling=None):
        """Lock the ash fall and play it an hour at a time (fires put out each hour) until both frames' mean depth reads
        `stop` (fall_done). -> [G mean by hour] (B's means under state["fallMeansB"])."""
        t.bridge_call("jawa/weather_set", weather=V.ASHFALL, lockWeather=True)
        means, means_b = [], []
        for _hour in range(cap_h):
            V._wait(t, HOUR)
            V._extinguish(t)
            m, mb = mean_depth(t, state["g"]), mean_depth(t, state["b"])
            means.append(round(m, 4) if m is not None else None)
            means_b.append(round(mb, 4) if mb is not None else None)
            if not V._live(t) or fall_done(m, mb, stop, ceiling):
                break
        state.setdefault("fallMeansB", []).append(means_b)
        return means

    def clear_then_noon(t):
        """Clear forced: the contract's 600 ticks, and no fewer than the 4,000 a weather takes to fade in, then the clock
        into the capture window. -> (hour, ticks of clear at the capture)."""
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        start = t.session._ticks() if V._live(t) else None
        V._wait(t, max(CLEAR_TICKS, FADE_TICKS))
        h = V._ten_noon_hour(t, SHOT_LO, SHOT_HI)
        return h, (t.session._ticks() - start) if V._live(t) and start is not None else None

    def read_pair(t, regime, means):
        g, b, border = state["g"], state["b"], state["border"]
        if plants_in(t, border):   # a seed that took in B's border since it was cleared: B stays "grass cleared"
            t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % V._rs(border))
            state.setdefault("reclears", []).append(regime)
        plant = os.environ.get(PLANT_ENV) or ""
        if plant == "grass_in_b" and V._live(t):
            V._plants(t, GRASS, b)
        if plant == "fire_in_g" and V._live(t):
            t.bridge_call("jawa/map_fire", action="start", rect=V._rs((g[0] + 5, g[1] + 3, 2, 2)), fireSize=1.0)
        if plant != "fire_in_g":
            V._extinguish(t)
        pad = lambda r: (r[0] - 1, r[1] - 1, r[2] + 2, r[3] + 2)  # noqa: E731 - the capture's 1-cell padding
        gr = frame_read(g, depth_map(t, g), grown_in(t, g), plants_in(t, g), fires_in(t, pad(g)))
        br = frame_read(b, depth_map(t, b), set(), plants_in(t, b), fires_in(t, pad(b)))
        weather = weather_now(t)
        shot_g = V._r6_shot(t, g, "gsua_%s_G" % regime)
        shot_b = V._r6_shot(t, b, "gsua_%s_B" % regime)
        return gr, br, weather, shot_g, shot_b

    def judge_pair(t, regime, means, hour, age):
        gr, br, weather, shot_g, shot_b = read_pair(t, regime, means)
        if not V._live(t):
            return
        ok, why, rows = opportunity(regime, gr, br, weather, age)
        pair = {"regime": regime, "fallMeans": means, "fallMeansB": (state.get("fallMeansB") or [None])[-1], "hour": hour, "clearAge": age, "weather": weather,
                "G": gr, "B": br, "shotG": shot_g, "shotB": shot_b, "checks": rows, "valid": ok, "why": why,
                "plantedFault": os.environ.get(PLANT_ENV) or None, "reclears": state.get("reclears", [])}
        state.setdefault("pairs", []).append(pair)
        state["manifest"] = write_manifest(state["dir"], {"scene": "sc_grass_seen_under_ash", "frames":
                                                          {"G": list(state["g"]), "B": list(state["b"])},
                                                          "pairs": state["pairs"], "stage": state.get("stage")})
        for r in rows:
            print("[gsua-check] %s: %s: %s worst=%r limit=%s cases=%d" % (regime, r["check"], "ok" if r["ok"] else "NOT",
                                                                            r["worst"], r["limit"], r["cases"]), flush=True)
        V._note(t, "%s pair: the frames' reads, the captures, the manifest" % regime,
                {"manifest": state["manifest"], "G": dict((k, gr[k]) for k in ("median", "grownShare", "plants", "fires")),
                 "B": dict((k, br[k]) for k in ("median", "plants", "fires")), "shots": [shot_g, shot_b], "why": why})
        if not shot_g or not shot_b:
            V._fail("the %s capture pair is incomplete: %r / %r" % (regime, shot_g, shot_b))
        if not ok:
            V._unmeasured(t, "%s pair: %s" % (regime, why))

    @suite.chain("grass_seen_under_ash")
    @V._teardown(fire=True, weather=True)
    def grass_seen_under_ash(t):
        state.clear()
        state["dir"] = out_dir()
        with V._comp(t, "grass_under_ash_stage"):
            if V._live(t):
                mid, why = V._load_registered_site(t)   # the contract: a fresh map
                if mid is None:
                    V._unmeasured(t, "SITE: %s" % why)
                V._on_site(t)
            plant = os.environ.get(PLANT_ENV) or ""
            if plant:
                V._note(t, "PLANTED FAULT", "%s=%s" % (PLANT_ENV, plant))
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            t.bridge_call("jawa/static_call", type=V.ASH_SAND, method="ClearAsh")   # housekeeping: no earlier ash
            counts = []
            if V._live(t):
                for x, z in scan_windows(V._map_size(t)):
                    counts.append((V._count(t, GRASS, "%d,%d,%d,%d" % (x, z, WINDOW_W, FRAME_H)), x, z))
            corner = pick_window(counts) if V._live(t) else (EDGE, EDGE)
            if corner is None:
                V._unmeasured(t, "no window of the site was counted")
            g, b, border, ring = frames_of(*corner)
            state.update(g=g, b=b, border=border, ring=ring)
            V._firebreak(t, ring, width=BREAK_WIDTH)
            planted = V._plants(t, GRASS, g, growth=1.0)
            t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % V._rs(border))
            if V._live(t):
                gg, bp = grown_in(t, g), plants_in(t, border)
                state["stage"] = {"window": list(corner), "windowGrass": max(counts)[0], "windows": len(counts),
                                  "plantReply": V._GEN.get("last_plants"), "grownG": len(gg), "plantsBborder": bp}
                print("[gsua-check] stage: G grown %d of %d (limit > %d); B border plants %d (limit 0); windows %d, "
                      "best %d of %d" % (len(gg), FRAME_W * FRAME_H, int(MOST * FRAME_W * FRAME_H), bp, len(counts),
                                         max(counts)[0], WINDOW_W * FRAME_H), flush=True)
                V._note(t, "the pair's frames on the site's densest carpet", state["stage"])
                if len(gg) <= MOST * FRAME_W * FRAME_H:
                    V._unmeasured(t, "G holds %d grown ember grass of %d cells after the replant: %r" % (
                        len(gg), FRAME_W * FRAME_H, planted))
                if bp:
                    V._unmeasured(t, "B's border holds %d plant(s) after the clear" % bp)
            state["mark"] = V._log_mark(t)
        V._independent(t)
        with V._comp(t, "grass_under_ash_light_pair"):
            V._ten_noon_hour(t, START_LO, START_HI)
            means = fall_until(t, LIGHT_STOP, LIGHT_CAP_H, ceiling=LIGHT_CEIL)
            hour, age = clear_then_noon(t)
            judge_pair(t, "light", means, hour, age)
        V._independent(t)
        with V._comp(t, "grass_under_ash_deep_pair"):
            means = fall_until(t, DEEP_STOP, DEEP_CAP_H)
            hour, age = clear_then_noon(t)
            judge_pair(t, "deep", means, hour, age)
        V._independent(t)
        with V._comp(t, "grass_under_ash_no_error_line"):
            lines = V._log_since(t, state.get("mark"))
            if V._live(t):
                errs = error_lines(lines)
                print("[gsua-check] error lines since the mark: %d (limit 0) of %d lines read" % (len(errs), len(lines)),
                      flush=True)
                V._note(t, "error lines since the scene's mark", {"errors": errs[:5], "lines": len(lines),
                                                                   "manifest": state.get("manifest")})
                if errs:
                    V._fail("%d new error line(s) in the log: %r" % (len(errs), errs[:2]))
