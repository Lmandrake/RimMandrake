"""sc_fire_catches_and_runs (bar fire_catches_and_runs, vision.md 0.2.0 line 11): one chain of the Pyrelands suite
(validation.py registers it through register()). Claim: "A spark in standing grass takes; on the day it is lit it is a
front the player must answer; the head walks downwind faster than 0.1.0's, and it is still the walking line of line 3,
never a flood." Owner: "The fire barely catches... I had expected faster spread."

  fire_catches_and_runs  A fresh load of the registered Pyrelands site (the suite's fresh map), weather forced clear, the
                         wind pointed east (MapComponent_BurnLine.SetWindForTest), wind carries on, Fire pace at the
                         shipped default. The spark: one cell lit by jawa/map_fire start (FireUtility.TryStartFireIn) at
                         fire size 0.1 on the row whose downwind corridor holds the most standing ember grass. When no
                         row reaches COVER_MIN the stage grows ember grass over that corridor (set_plants, plantable
                         cells only) and reads it again; the manifest names what it planted.
    valid opportunity    the spark cell holds ember grass, the corridor downwind of it to the edge is at least COVER_MIN
                         ember grass, the weather stayed clear, no pawn and no building lies in the corridor a day's front
                         can reach (DAY_REACH x 2 HALF_W). Otherwise UNMEASURED, never a verdict on the mod.
    success              the spark burns at hour 1; a front FLANK_WIDTH wide by FRONT_HOURS; the day-end head beats the
                         0.1.0 reading (READING_010, taken once on the mod/Pyrelands/v0.1.0 tag, kept beside the row);
                         a blind judge reads a walking line on the captures (the manifest lists them).
    forbidden            the burning or black share of open ground over SHARE_MAX at the day end; a fire on a cell that no
                         carry reached (the spark's own cell aside); a new Player.log error line.
    end                  one game day, or the head at the map edge. Reads every hour, captures at CAPTURE_HOURS.

Run (the pyrelands tier, a free game, python.exe, the bridge env of that game):
    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains fire_catches_and_runs
The 0.1.0 reading, once: deploy the mod/Pyrelands/v0.1.0 build, run the same chain with PYRE_FCR_TAKE_010=1; it writes
READING_010 and judges nothing.
Offline: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_fire_catches.py
"""
import datetime
import json
import math
import os

GRASS = "RM_FE_Plant_EmberGrass"
BURN = "RimMandrake.Pyrelands.MapComponent_BurnLine"
PROBE = "RimMandrake.Pyrelands.FireCatchesProbe"     # FireEcologyHook.cs: Corridor, Burn (read-only)
HOUR, DAY = 2500, 60000                 # GenDate.TicksPerHour, TicksPerDay
PACE_DEFAULT = 200                      # RM_BurnKernel.FirePacePercentDefault: the shipped pace (the selftest reads the C#)
SPARK_SIZE = 0.1                        # the contract: FireUtility.TryStartFireIn at size 0.1
BEARING = 90                            # east: SetWindForTest's bearing, the burn line's own (90 = +x)
FLANK_WIDTH = 10                        # RM_BurnKernel.FlankWidth (the selftest reads it from the C# file)
HEAL_REACH = 5                          # RM_BurnKernel.HealReach: the front's gaps passed (the selftest reads it too)
FRONT_HOURS = 24                        # bar: "on the day it is lit it is a front" (selftest_pyrelands_fire_pace.FRONT_HOURS)
SHARE_MAX = 0.5                         # bar "never a flood": the decider's "burned share of open ground at or under half"
COVER_MIN = 0.70                        # the lowest cover T_FIRE_PACE_MODEL_OFFLINE reads: the live corridor stays inside it
DAY_REACH = 150                         # MEASURED: the model's worst day-one head at the slider's high end (250) is 134
                                        # cells (blobbed maps; 113 at the default 200); the selftest re-measures it
HALF_W = 30                             # MEASURED: the model's worst day-one |across| at 200 and 250, 26.0 cells (re-measured
                                        # by the selftest)
SPARK_X = 12                            # cells in from the west edge: room behind the spark, the head's whole map ahead
ROW_STEP = 10                           # candidate spark rows, every 10 cells, HALF_W off the north and south edges
CAPTURE_HOURS = (1, 6, 12, 24)          # one capture of the burn per quarter day, and the hour-1 spark
SHOT_PX = 1500                          # a capture's long side at most (the agents' image limit)
PLAY_PPC = 64                           # validation.R6_PLAY_PPC, the cap
HOLD_OFF = {"burnLineEnabled": True, "fireClockEnabled": False, "fireHawkSpreadEnabled": False,   # RM_PyrelandsSettings
            "scorchFruitEnabled": False}                    # fields, in 0.1.0 and now; the stage's isolation (register())
TAKE_ENV = "PYRE_FCR_TAKE_010"
OUT_ENV = "RM_FCR_DIR"
READING_010 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fire_catches_010_reading.json")


def kv(line):
    """Pure. "a=1;b=x" -> {"a": "1", "b": "x"}; None for an error= line or a non-string."""
    if not isinstance(line, str) or line.startswith("error="):
        return None
    out = {}
    for part in line.split(";"):
        k, _, v = part.partition("=")
        if k:
            out[k] = v
    return out


def parse_burn(line):
    """Pure. FireCatchesProbe.Burn's line -> {"tick", "open", "stamps", "fires": [(x, z, carriedAt)], "burned": {(x, z)}}."""
    d = kv(line)
    if d is None or "fires" not in d or "burned" not in d:
        return None
    fires = [tuple(int(a) for a in c.split(":")) for c in d["fires"].split("|") if c]
    burned = set(tuple(int(a) for a in c.split(":")) for c in d["burned"].split("|") if c)
    return {"tick": int(d.get("tick", -1)), "open": int(d.get("open", 0)), "stamps": d.get("stamps") == "1",
            "fires": fires, "burned": burned}


def axes(bearing):
    r = math.radians(bearing)
    return math.sin(r), math.cos(r)


def along_across(cell, spark, bearing):
    wx, wz = axes(bearing)
    dx, dz = cell[0] - spark[0], cell[1] - spark[1]
    return dx * wx + dz * wz, dx * wz - dz * wx


def head(cells, spark, bearing):
    """Pure. The furthest along-wind distance of any cell from the spark (0 for none)."""
    return max([along_across(c, spark, bearing)[0] for c in cells] or [0.0])


DIRS8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # pyre_burn_sim.DIRS8, clockwise from +z


def front_width(fire_cells, bearing, heal_reach=None):
    """Pure. T_FIRE_PACE_MODEL_OFFLINE's front (selftest_pyrelands_fire_pace.front_width, FlankPlan's measure): the burning
    cells projected on the perpendicular of the wind's snapped compass step (a diagonal step counts one cell per two units
    of x + z), the longest run with gaps up to HealReach passed; 0 for none."""
    heal = HEAL_REACH if heal_reach is None else heal_reach
    step = int(math.floor((bearing % 360.0) / 45.0 + 0.5)) % 8
    px, pz = DIRS8[(step + 2) % 8]
    a = sorted(set((x * px + z * pz) // (2 if px and pz else 1) for x, z in fire_cells))
    if not a:
        return 0
    best = run = 1
    for i in range(1, len(a)):
        run = run + (a[i] - a[i - 1]) if a[i] - a[i - 1] <= heal + 1 else 1
        best = max(best, run)
    return int(best)


def share(read):
    """Pure. (burning or black cells) / open cells of the map."""
    cells = set(read["burned"]) | set((f[0], f[1]) for f in read["fires"])
    return len(cells) / float(max(1, read["open"]))


def uncarried(read, spark):
    """Pure. Fire cells that no carry reached: carriedAt < 0, the spark's own cell aside."""
    return [(f[0], f[1]) for f in read["fires"] if f[2] < 0 and (f[0], f[1]) != tuple(spark)]


def cover(corr):
    """Pure. A Corridor dict -> ember grass cells / corridor cells (water and rock count against it); 0 for none."""
    cells = int((corr or {}).get("cells") or 0)
    return int(corr["ember"]) / float(cells) if cells else 0.0


def corridor_rect(spark, size):
    """Pure. The east-wind corridor as a map rect (x, z, w, h): along [0, DAY_REACH], across +-HALF_W, inside the map."""
    x0, z0 = spark[0], max(0, spark[1] - HALF_W)
    x1, z1 = min(size[0] - 1, spark[0] + DAY_REACH), min(size[1] - 1, spark[1] + HALF_W)
    return x0, z0, x1 - x0 + 1, z1 - z0 + 1


def candidate_rows(size, half_w=HALF_W, step=ROW_STEP):
    """Pure. Map size (sx, sz) -> the spark rows z, each HALF_W off the north and south edges."""
    return list(range(half_w, size[1] - half_w, step))


def pick_row(reads):
    """Pure. [(z, Corridor dict)] -> (z, dict) with the most ember grass per corridor cell, no pawn and no building; ties to
    the lowest z; None when no row is clean."""
    ok = [(z, d) for z, d in reads if d and int(d["pawns"]) == 0 and int(d["buildings"]) == 0 and int(d["cells"]) > 0]
    if not ok:
        return None
    return max(ok, key=lambda r: (cover(r[1]), -r[0]))


def opportunity(corr, weathers):
    """Pure. (the picked corridor's Corridor dict, [weather at each hourly read]) -> (ok, why, rows). ok False is no valid
    opportunity (UNMEASURED)."""
    rows = []

    def row(name, ok, worst, limit, cases):
        rows.append({"check": name, "ok": bool(ok), "worst": worst, "limit": limit, "cases": cases})

    cells = int(corr["cells"]) if corr else 0
    cov = cover(corr)
    row("spark cell holds ember grass", bool(corr) and corr.get("emberAt") == "1", corr and corr.get("emberAt"), "1", 1)
    row("corridor ember grass to the edge", cov >= COVER_MIN, round(cov, 3), ">= %.2f" % COVER_MIN, cells)
    row("pawns in a day's front", bool(corr) and int(corr["pawns"]) == 0, corr and corr.get("pawns"), "== 0", cells)
    row("buildings in a day's front", bool(corr) and int(corr["buildings"]) == 0, corr and corr.get("buildings"), "== 0", cells)
    notclear = [w for w in weathers if w != "Clear"]
    row("weather clear at every read", bool(weathers) and not notclear, notclear[:1] or "Clear", "Clear", len(weathers))
    bad = [r for r in rows if not r["ok"]]
    if bad:
        return False, "; ".join("%s %r (limit %s)" % (r["check"], r["worst"], r["limit"]) for r in bad), rows
    return True, "%d of %d opportunity checks hold" % (len(rows), len(rows)), rows


def verdict(hourly, spark, bearing, reading_010, judge=None):
    """Pure. hourly: [(hour, parse_burn read)] in hour order, the last at the end (day or edge). -> rows, each with its
    worst value, its limit and its case count; "ok" None is UNMEASURED (a reading the run could not have)."""
    rows = []

    def row(name, ok, worst, limit, cases):
        rows.append({"check": name, "ok": ok, "worst": worst, "limit": limit, "cases": cases})

    by_h = dict(hourly)
    h1 = by_h.get(1)
    row("the spark burns at hour 1", bool(h1) and len(h1["fires"]) > 0, len(h1["fires"]) if h1 else None, "> 0 fires", 1)
    front_h = None
    for h, r in hourly:
        if front_width([(f[0], f[1]) for f in r["fires"]], bearing) >= FLANK_WIDTH:
            front_h = h
            break
    row("a front FlankWidth wide by hour %d" % FRONT_HOURS, front_h is not None and front_h <= FRONT_HOURS,
        front_h, "<= %d h, width >= %d" % (FRONT_HOURS, FLANK_WIDTH), len(hourly))
    last = hourly[-1][1] if hourly else None
    hd = round(head(set(last["burned"]) | set((f[0], f[1]) for f in last["fires"]), spark, bearing), 1) if last else None
    old = (reading_010 or {}).get("head")
    row("the day-end head beats 0.1.0's", None if old is None or hd is None else hd > old, hd,
        "> %s (0.1.0, %s)" % (old, READING_010 if old is not None else "not yet taken: " + TAKE_ENV + "=1 on the tag"), 1)
    worst_share = max([share(r) for _, r in hourly] or [0.0])
    row("burning or black share of open ground", bool(hourly) and worst_share <= SHARE_MAX, round(worst_share, 4),
        "<= %.2f" % SHARE_MAX, len(hourly))
    stray = sorted(set(c for _, r in hourly for c in uncarried(r, spark)))
    row("fire on a cell no carry reached", not stray and bool(hourly), len(stray), "== 0 (first %r)" % stray[:3], len(hourly))
    row("a blind judge reads a walking line", judge, judge, "True (judge on the manifest's captures)", 1)
    return rows


def end_reached(hour, read, spark, bearing, edge):
    """Pure. The chain's end: one game day, or the head at the map edge."""
    if hour >= DAY // HOUR:
        return True
    cells = set(read["burned"]) | set((f[0], f[1]) for f in read["fires"])
    return head(cells, spark, bearing) >= edge - 1


def shot_rect(cells, size, pad=5):
    """Pure. The burn's bounding box plus `pad`, inside the map -> (x, z, w, h); None for no cells."""
    if not cells:
        return None
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    x0, z0 = max(0, min(xs) - pad), max(0, min(zs) - pad)
    x1, z1 = min(size[0] - 1, max(xs) + pad), min(size[1] - 1, max(zs) + pad)
    return x0, z0, x1 - x0 + 1, z1 - z0 + 1


def shot_ppc(rect):
    """Pure. Pixels per cell so the capture's long side stays at or under SHOT_PX, at most play zoom, at least 4."""
    return max(4, min(PLAY_PPC, SHOT_PX // max(rect[2], rect[3])))


def error_lines(lines):
    """Pure. _log_since lines -> the error and exception lines."""
    return [str(m.get("text", ""))[:240] for m in lines or []
            if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception")]


def out_dir(stamp=None):
    """$RM_FCR_DIR, else D:\\ClaudeWork\\rimmandrake\\fire_catches\\<stamp> (scratch: the judge reads it)."""
    base = os.environ.get(OUT_ENV)
    if not base:
        root = r"D:\ClaudeWork\rimmandrake\fire_catches" if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/fire_catches"
        base = os.path.join(root, stamp or datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return base


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    return path


def load_reading(path=None):
    try:
        with open(path or READING_010, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def register(suite, V):
    """Adds fire_catches_and_runs to the Pyrelands suite. V is validation.py's namespace."""
    state = {}

    def call(t, cls, method, args):
        r = t.bridge_call("jawa/static_call", type=cls, method=method, args=str(args))
        return (r or {}).get("result") if V._live(t) else None

    def weather(t):
        a = V._ash(t, "0,0,1,1")
        return a.get("weather") if a else None

    @suite.chain("fire_catches_and_runs")
    @V._teardown(fire=True, weather=True)
    def fire_catches_and_runs(t):
        state.clear()
        state["dir"] = out_dir()
        take = bool(os.environ.get(TAKE_ENV))
        with V._comp(t, "fire_catches_stage"):
            if V._live(t):
                mid, why = V._load_registered_site(t)   # the contract: a fresh map
                if mid is None:
                    V._unmeasured(t, "SITE: %s" % why)
                V._on_site(t)
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            # one spark: the biome's other fire sources held off for the run (the fire clock's fronts and scar arc, the
            # fire hawks' twigs, scorch fruit), as sc_fire_walks_with_wind does (wind_burn_live.SET); the burn line stays on,
            # it is the carry (live 2026-11-27: with them on, fires 224 cells off the spark at hour 1, 3 of them uncarried)
            V._set(t, dict(HOLD_OFF, **({"windCarriesFireEnabled": True} if take else    # the tag has no Fire pace setting
                                        {"windCarriesFireEnabled": True, "firePacePercent": PACE_DEFAULT})))
            wind = call(t, BURN, "SetWindForTest", BEARING)
            size = V._map_size(t) if V._live(t) else (250, 250)
            reads = []
            for z in candidate_rows(size):
                reads.append((z, kv(call(t, PROBE, "Corridor", "%d,%d,%d,%d,%d" % (SPARK_X, z, BEARING, DAY_REACH, HALF_W)))))
            pick = pick_row(reads) if V._live(t) else (size[1] // 2, None)
            if pick is None:
                V._unmeasured(t, "no spark row holds a corridor clear of pawns and buildings (%d rows)" % len(reads))
            z, corr = pick
            spark = (SPARK_X, z)
            planted = None
            if V._live(t) and corr and cover(corr) < COVER_MIN:
                # staging: the site's own grass is too thin on every row; grow ember grass over the corridor's plantable
                # cells (set_plants skips the rest) so the opportunity is the contract's, then read it again
                planted = corridor_rect(spark, size)
                V._plants(t, GRASS, planted, growth=1.0)
            elif V._live(t) and corr and corr.get("emberAt") != "1":   # staging: the spark cell's own blade, grown
                planted = (SPARK_X, z, 1, 1)
                V._plants(t, GRASS, planted, growth=1.0)
            if planted:
                corr = kv(call(t, PROBE, "Corridor", "%d,%d,%d,%d,%d" % (SPARK_X, z, BEARING, DAY_REACH, HALF_W)))
            state.update(spark=spark, corr=corr, wind=wind, size=size, edge=int((corr or {}).get("edge") or size[0]),
                         planted=planted)
            print("[fcr-check] stage: wind set %r (asked %d); spark %r; corridor %r; rows read %d" % (
                wind, BEARING, spark, corr, len(reads)), flush=True)
            V._note(t, "the spark row and its corridor", {"spark": spark, "corridor": corr, "rows": len(reads), "wind": wind})
            state["mark"] = V._log_mark(t)
        V._independent(t)
        with V._comp(t, "fire_catches_burn"):
            if "spark" not in state:   # _comp frees the next row after an UNMEASURED stage: no spark row, nothing to light
                V._unmeasured(t, "no spark lit: the stage set no spark row")
            spark = state["spark"]
            since = t.session._ticks() if V._live(t) else 0
            lit = t.bridge_call("jawa/map_fire", action="start", rect=V._rs((spark[0], spark[1], 1, 1)), fireSize=SPARK_SIZE)
            hourly, weathers, shots = [], [], []
            state.update(hourly=hourly, weathers=weathers, shots=shots)   # kept as read: a burn cut short still leaves its hours
            for hour in range(1, DAY // HOUR + 1):
                V._wait(t, HOUR)
                if not V._live(t):
                    break
                r = parse_burn(call(t, PROBE, "Burn", since))
                if r is None:
                    V._unmeasured(t, "FireCatchesProbe.Burn unreadable at hour %d" % hour)
                hourly.append((hour, r))
                weathers.append(weather(t))
                print("[fcr-check] hour %d: fires %d, burned %d, head %.1f, width %d, share %.4f, uncarried %d" % (
                    hour, len(r["fires"]), len(r["burned"]), head(r["burned"] | set((f[0], f[1]) for f in r["fires"]), spark,
                                                                   BEARING),
                    front_width([(f[0], f[1]) for f in r["fires"]], BEARING), share(r), len(uncarried(r, spark))),
                    flush=True)
                done = end_reached(hour, r, spark, BEARING, state["edge"])
                if hour in CAPTURE_HOURS or done:
                    rect = shot_rect(r["burned"] | set((f[0], f[1]) for f in r["fires"]), state["size"])
                    if rect:
                        shots.append({"hour": hour, "rect": rect,
                                      "path": t.screenshot(name="fcr_h%02d" % hour, rect=tuple(rect), ppc=shot_ppc(rect))})
                if done:
                    state["ended"] = hour
                    break
            state["lit"] = lit
        V._independent(t)
        with V._comp(t, "fire_catches_verdict"):
            if not V._live(t):
                return
            if "hourly" not in state:
                V._unmeasured(t, "no burn to judge: the stage set no spark row")
            spark = state["spark"]
            if not state.get("ended"):   # a burn cut short (an UNMEASURED read or capture) is no reading and no verdict
                V._unmeasured(t, "the burn stopped at hour %d, before its end (a day or the edge): no %s" % (
                    len(state["hourly"]), "0.1.0 reading" if take else "verdict"))
            ok, why, orows = opportunity(state["corr"], state["weathers"])
            last = state["hourly"][-1][1] if state["hourly"] else None
            hd = head(last["burned"] | set((f[0], f[1]) for f in last["fires"]), spark, BEARING) if last else None
            man = {"scene": "sc_fire_catches_and_runs", "spark": spark, "corridor": state["corr"], "valid": ok, "why": why,
                   "opportunity": orows, "planted": state.get("planted"), "shots": state["shots"], "head": hd,
                   "hours": len(state["hourly"]), "taken010": take}
            if take:
                if ok and hd is not None:
                    write_json(READING_010, {"head": round(hd, 1), "hours": len(state["hourly"]), "spark": spark,
                                             "tag": "mod/Pyrelands/v0.1.0", "taken": datetime.datetime.now().isoformat()})
                write_json(os.path.join(state["dir"], "manifest.json"), man)
                V._note(t, "0.1.0 reading taken (no verdict)", {"head": hd, "valid": ok, "why": why})
                if not ok:
                    V._unmeasured(t, "0.1.0 reading not taken: " + why)
            else:   # no return here: the error-line row runs in take mode too
                rows = verdict(state["hourly"], spark, BEARING, load_reading())
                man["rows"] = rows
                state["manifest"] = write_json(os.path.join(state["dir"], "manifest.json"), man)
                for r in orows + rows:
                    print("[fcr-check] %s: %s worst=%r limit=%s cases=%d" % (
                        r["check"], {True: "ok", False: "NOT", None: "UNMEASURED"}[r["ok"]], r["worst"], r["limit"], r["cases"]),
                        flush=True)
                V._note(t, "the burn's reads, the captures, the manifest", {"manifest": state["manifest"], "why": why})
                if not ok:
                    V._unmeasured(t, why)
                bad = [r for r in rows if r["ok"] is False]
                if bad:
                    V._fail("; ".join("%s %r (limit %s)" % (r["check"], r["worst"], r["limit"]) for r in bad))
                if any(r["ok"] is None for r in rows):
                    V._unmeasured(t, "owed: %s" % ", ".join(r["check"] for r in rows if r["ok"] is None))
        V._independent(t)
        with V._comp(t, "fire_catches_no_error_line"):
            lines = V._log_since(t, state.get("mark"))
            if V._live(t):
                errs = error_lines(lines)
                print("[fcr-check] error lines since the mark: %d (limit 0) of %d lines read" % (len(errs), len(lines)),
                      flush=True)
                if errs:
                    V._fail("%d new error line(s) in the log: %r" % (len(errs), errs[:2]))
