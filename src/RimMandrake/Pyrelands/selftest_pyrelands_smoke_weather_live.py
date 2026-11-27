#!/usr/bin/env python3
"""Offline test of smoke_weather_live.py (sc_smoke_weather_chokes, bar pyre_smoke_weather_chokes). No game.

  1. the pure helpers: the shipped numbers read from the kernel and the defs (the smoke rains nothing; the hediff's label,
     stages and recovery), the model of the outdoor colonist's severity against a hand count of the same rates, the model
     band against a twin at random phases, the geometry (the room's ring, the gap, the strip, the firebreak, the map).
  2. each judge: its clean case passes, and each planted fault turns its own row red.
  3. the chain itself, run against a fake game (a twin of MapComponent_RM_SmokeWeather: a gain every 250 ticks at the
     weather's lerp share, the hediff's -2.4 a day every 200, removal at 0, a roof stops the gain): the clean game reads
     PASS in every component but the judge's (owed, UNMEASURED) and PASS with a judge's 'smoke'; each planted fault turns
     its own component red; the 0.1.0 build (no smoke defs) FAILs the stage: the red-first reading.
  4. the record: validation.py registers the chain.
Every row prints its worst value, its limit and its case count.
"""
import importlib.util
import os
import random
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
N = {"run": 0, "bad": 0}


def check(name, ok, detail=""):
    N["run"] += 1
    if not ok:
        N["bad"] += 1
        print("FAIL  %s -- %s" % (name, str(detail)[:400]))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "modcheck")]
import validation as V  # noqa: E402

S = load("smoke_weather_live", "smoke_weather_live.py")
NUMS = S.kernel_numbers()
SPEC = S.hediff_spec(open(S.HEDIFF_XML, encoding="utf-8").read())
RATES = S.weather_rates(open(S.WEATHER_XML, encoding="utf-8").read())

# ---- 1. the pure helpers
check("kernel numbers read (gain 0.02, interval 250, recovery 2.4)",
      NUMS == {"gain": 0.02, "interval": 250.0, "recovery": 2.4}, NUMS)
check("the hediff's recovery is the kernel's (perDay == -recovery)", SPEC and SPEC["perDay"] == -NUMS["recovery"], SPEC)
check("the hediff has its label and three stages with Breathing and Moving offsets",
      SPEC["label"] == "smoke in the lungs" and len(SPEC["stages"]) == 3
      and all(st["caps"].get("Breathing", 0) < 0 and st["caps"].get("Moving", 0) < 0 for st in SPEC["stages"]), SPEC)
print("[swc-st] smoke rates %r (limit 0 each)" % RATES)
check("the smoke rains, snows and sands nothing", RATES == {"rainRate": 0.0, "snowRate": 0.0, "sandRate": 0.0}, RATES)
check("stage_of: 0.2 coughing, 0.35 choking, 0.7 gasping, None none",
      [(S.stage_of(x, SPEC) or {}).get("label") for x in (0.2, 0.35, 0.7, None)] == ["coughing", "choking", "gasping", None])

lo, hi = S.model_band(S.READ_HOURS * S.HOUR, 0.0, NUMS, SPEC)
# a hand count of the same rates: 10 checks an hour x 0.02 = 0.2 an hour at the full share, 2.4 / 24 = 0.1 an hour
# recovered while the hediff exists. Over the 4000-tick ramp (1.6 h) the gain is 0.2 a / 1.6 an hour, under the recovery
# until a = 0.8 h (the hediff comes and goes), so the ramp keeps the integral of 0.125 a - 0.1 from 0.8 to 1.6 h = 0.04;
# then 0.1 an hour net for the rest
hand = 0.04 + 0.1 * (S.READ_HOURS - 1.6)
choke = SPEC["stages"][1]["min"]
print("[swc-st] model at %d h: lowest %.4f highest %.4f; hand count %.3f; limit lowest >= %.2f (choking %.2f + NET_HOUR) "
      "and highest < %.2f (gasping); 8 phase pairs" % (S.READ_HOURS, lo, hi, hand, choke + S.NET_HOUR, choke,
                                                       SPEC["stages"][2]["min"]))
check("the model's lowest clears choking by NET_HOUR at READ_HOURS", lo >= choke + S.NET_HOUR, lo)
check("the model's highest stays under gasping", hi < SPEC["stages"][2]["min"], hi)
check("the model agrees with the hand count within 0.03", abs(lo - hand) <= 0.03 and abs(hi - hand) <= 0.03, (lo, hi, hand))
lo5, _ = S.model_band(S.READ_HOURS * S.HOUR, 0.5, NUMS, SPEC)
print("[swc-st] model at resistance 0.5 (RES_MAX): lowest %.4f (limit < 0.05: no net gain)" % lo5)
check("at RES_MAX the colonist gains no lasting smoke", lo5 < 0.05, lo5)
check("at resistance 1 the colonist never has the hediff", S.model_severity(S.READ_HOURS * S.HOUR, 1.0, NUMS, SPEC) is None)


def twin(ticks, res, gp, hp):
    """An independent per-check twin (the kernel's rule written again, not the module's code)."""
    sev = 0.0
    for a in range(1, ticks + 1):
        if (a + gp) % 250 == 0:
            sev = min(1.0, sev + 0.02 * min(1.0, a / 4000.0) * (1 - res))
        if sev > 0 and (a + hp) % 200 == 0:
            sev = max(0.0, sev - 2.4 * 200 / 60000.0)
    return sev


rng = random.Random(11)
worst = 0.0
CASES = 40
for _ in range(CASES):
    gp, hp, res = rng.randrange(250), rng.randrange(200), rng.choice((0.0, 0.1, 0.3))
    b = S.model_band(S.READ_HOURS * S.HOUR, res, NUMS, SPEC)
    v = twin(S.READ_HOURS * S.HOUR, res, gp, hp)
    worst = max(worst, b[0] - v, v - b[1])
print("[swc-st] twin at random phases outside the model band: worst %.4f (limit 0.01) over %d cases" % (worst, CASES))
check("the model band holds the twin at random phases within 0.01", worst <= 0.01, worst)

g = S.geometry(S.PAD)
rx, rz, rw, rh = g["room"]
check("the ring is the room's 24 edge cells", len(g["ring"]) == 24 and len(set(g["ring"])) == 24, len(g["ring"]))
check("R stands inside the room, O outside it", rx < g["R"][0] < rx + rw - 1 and rz < g["R"][1] < rz + rh - 1
      and not (rx <= g["O"][0] < rx + rw), g)
gap = rx - (g["strip"][0] + g["strip"][2])
print("[swc-st] strip to wall gap %d (limit > 5, HealReach); firebreak %d (limit > 5)" % (gap, S.FIREBREAK))
check("the strip ends GAP cells west of the wall, over the burn line's reach", gap == S.GAP and gap > 5, gap)
check("the spark is the strip's east column", g["spark"][0] == g["strip"][0] + g["strip"][2] - 1 and g["spark"][2] == 1)
inside = lambda r, o: r[0] >= o[0] and r[1] >= o[1] and r[0] + r[2] <= o[0] + o[2] and r[1] + r[3] <= o[1] + o[3]
check("strip, room and both colonists lie in the scene", inside(g["strip"], g["scene"]) and inside(g["room"], g["scene"])
      and inside((g["O"][0], g["O"][1], 1, 1), g["scene"]), g)
check("the scene fits a 250 map at PAD, and a pad at the corner does not", S.fits(g, (250, 250))
      and not S.fits(S.geometry((10, 10)), (250, 250)))
# the pad (SITE, ArchSmall 2026-11-27, site 1 tile 1496: a geyser stood in PAD's scene; the stage read UNMEASURED)
GEYSERS_SITE1 = [(69, 157), (57, 233), (28, 97), (143, 221)]   # MEASURED: list_things SteamGeyser, 4 of 4, that map
check("the measured site: the geyser at (143, 221) blocks PAD's scene", S.blocked(S.geometry(S.PAD), GEYSERS_SITE1)
      == [(143, 221)], S.blocked(S.geometry(S.PAD), GEYSERS_SITE1))
p1 = S.pick_pad(GEYSERS_SITE1, (250, 250))
print("[swc-st] measured site 1: pad %r (PAD %r)" % (p1, S.PAD))
check("the measured site: the pad picked fits and no geyser touches it", p1 is not None and p1 != S.PAD
      and S.fits(S.geometry(p1), (250, 250)) and not S.blocked(S.geometry(p1), GEYSERS_SITE1), p1)
check("no geyser: the pad is PAD", S.pick_pad([], (250, 250)) == S.PAD)
check("a geyser one cell beyond the firebreak's reach does not block; one inside it does",
      not S.blocked(S.geometry(S.PAD), [(S.geometry(S.PAD)["big"][0] - 3, S.PAD[1])])
      and S.blocked(S.geometry(S.PAD), [(S.geometry(S.PAD)["big"][0] - 2, S.PAD[1])]))
dense = [(x, z) for x in range(0, 250, 8) for z in range(0, 250, 8)]
check("geysers every 8 cells: no pad, None (the stage reads UNMEASURED SITE)", S.pick_pad(dense, (250, 250)) is None)
# the sweep: what the game varies here is the geysers' number and cells (and the map's size, 250 on the fixture)
rng = random.Random(1127)
LAYOUTS, none, worst_n, bad = 3000, 0, None, []
for i in range(LAYOUTS):
    n = rng.randint(0, 16)
    size = rng.choice(((250, 250), (200, 200), (275, 275), (325, 325)))
    gs = [(rng.randrange(size[0] - 1), rng.randrange(size[1] - 1)) for _ in range(n)]
    pp = S.pick_pad(gs, size)
    if pp is None:
        none += 1
        worst_n = n if worst_n is None else min(worst_n, n)
    elif not S.fits(S.geometry(pp), size) or S.blocked(S.geometry(pp), gs):
        bad.append((size, gs, pp))
print("[swc-st] pad sweep: %d layouts (0..16 geysers, maps 200..325): %d with no pad (fewest geysers then %r), "
      "%d picks that do not fit or touch a geyser (limit 0)" % (LAYOUTS, none, worst_n, len(bad)))
check("pad sweep: every pad picked fits and touches no geyser", not bad, bad[:2])
check("pad sweep: a pad is found on every layout of up to 16 geysers", none == 0, (none, worst_n))
print("[swc-st] capture ppc %d for %r (long side %d px, limit %d)" % (S.shot_ppc(g["sky"]), g["sky"][2:],
                                                                      S.shot_ppc(g["sky"]) * 48, S.SHOT_PX))
check("a capture's long side stays at or under SHOT_PX", S.shot_ppc(g["sky"]) * max(g["sky"][2:]) <= S.SHOT_PX)


# ---- 2. the judges
def prow(pid, cell, sev=None, caps=(1.0, 1.0), extra=(), label=None, **kw):
    hs = [{"def": d, "label": d.lower(), "severity": 0.1} for d in extra]
    if sev is not None:
        st = S.stage_of(sev, SPEC)
        hs.append({"def": S.CHOKE, "label": label or "%s (%s)" % (SPEC["label"], st["label"]), "severity": sev})
    r = {"id": pid, "x": cell[0], "z": cell[1], "dead": False, "downed": False, "mentalState": None,
         "health": {"hediffs": hs, "capacities": {"Breathing": caps[0], "Moving": caps[1], "Sight": 1.0}}}
    r.update(kw)
    return r


def stage_caps(sev):
    st = S.stage_of(sev, SPEC)
    return (1.0 + st["caps"]["Breathing"], 1.0 + st["caps"]["Moving"])


def reads_of(o_sev=0.58, r_sev=None, fire=12, rain=0.0, weather=S.SMOKE, o_cell=None, extra=()):
    out = []
    for h in range(1, S.READ_HOURS + 1):
        s = o_sev * h / S.READ_HOURS
        out.append({"hour": h, "weather": weather, "rainRate": rain,
                    "O": prow("O", o_cell or g["O"], s, stage_caps(s), extra=extra if h == 3 else ()),
                    "R": prow("R", g["R"], r_sev), "fire": fire, "grass": 480 - 20 * h})
    return out


START = {"O": prow("O", g["O"]), "R": prow("R", g["R"])}
BAND = (lo, hi)
ok_all = lambda rows: all(r["ok"] for r in rows)
bad = lambda rows, part: any(not r["ok"] and part in r["check"] for r in rows)

check("opportunity: the clean scene is valid", ok_all(S.judge_opportunity(reads_of(), START, g, 0.0, 12)),
      S.judge_opportunity(reads_of(), START, g, 0.0, 12))
for name, kw, args, part in (
        ("weather drifts off smoke", {"weather": "Clear"}, (0.0, 12), "smoke is the weather"),
        ("O moved", {"o_cell": (g["O"][0] + 1, g["O"][1])}, (0.0, 12), "O stays"),
        ("O gains Heatstroke", {"extra": ("Heatstroke",)}, (0.0, 12), "O gains no hediff"),
        ("O wears a gas mask (res 0.6)", {}, (0.6, 12), "Resistance"),
        ("resistance unread", {}, (None, 12), "Resistance"),
        ("the fire never took", {}, (0.0, 0), "fire took")):
    check("opportunity: planted %s is caught" % name, bad(S.judge_opportunity(reads_of(**kw), START, g, *args), part))
downed = reads_of()
downed[4]["R"]["downed"] = True
check("opportunity: planted R downed is caught", bad(S.judge_opportunity(downed, START, g, 0.0, 12), "R alive"))

end_ok = prow("O", g["O"], 0.58, stage_caps(0.58))
check("outdoor: the clean end passes", ok_all(S.judge_outdoor(START["O"], end_ok, SPEC, BAND)),
      S.judge_outdoor(START["O"], end_ok, SPEC, BAND))
for name, end, part in (
        ("no hediff", prow("O", g["O"]), "carries"),
        ("wrong label", prow("O", g["O"], 0.58, stage_caps(0.58), label="toxic buildup (minor)"), "label"),
        ("stage too low (0.2)", prow("O", g["O"], 0.2, stage_caps(0.2)), "stage"),
        ("no Breathing drop", prow("O", g["O"], 0.58, (1.0, stage_caps(0.58)[1])), "Breathing"),
        ("no Moving drop", prow("O", g["O"], 0.58, (stage_caps(0.58)[0], 1.0)), "Moving")):
    check("outdoor: planted %s is caught" % name, bad(S.judge_outdoor(START["O"], end, SPEC, BAND), part))

check("roofed: the clean reads pass", ok_all(S.judge_roofed(START["R"], reads_of())), S.judge_roofed(START["R"], reads_of()))
check("roofed: planted hediff on R is caught", bad(S.judge_roofed(START["R"], reads_of(r_sev=0.05)), "never carries"))
low = reads_of()
low[2]["R"]["health"]["capacities"]["Moving"] = 0.95
check("roofed: planted Moving loss on R is caught", bad(S.judge_roofed(START["R"], low), "Moving kept"))
check("roofed: no reads is red", bad(S.judge_roofed(START["R"], []), "never carries"))

check("fire: the clean reads pass", ok_all(S.judge_fire(reads_of())), S.judge_fire(reads_of()))
check("fire: full smoke is the first read at or after 4000 ticks (hour 2)", S.full_smoke_hour(reads_of()) == 2)
check("fire: planted rainRate 0.02 is caught", bad(S.judge_fire(reads_of(rain=0.02)), "rainRate"))
check("fire: planted rainRate unread is caught", bad(S.judge_fire(reads_of(rain=None)), "rainRate"))
check("fire: rainRate at the line (0.01) passes", ok_all(S.judge_fire(reads_of(rain=0.01))))
out = reads_of()
out[1]["fire"] = 0
check("fire: planted fire out at hour 2 is caught", bad(S.judge_fire(out), "a fire burns"))
stall = reads_of()
stall[2]["grass"] = stall[1]["grass"]
check("fire: planted grass that stops falling is caught", bad(S.judge_fire(stall), "keeps falling"))

shots = [{"label": "a", "path": "/x/a.png"}, {"label": "b", "path": "/x/b.png"}]
o_, v_ = S.judge_captures(shots, None)
check("sky: no judge yet is owed (None), never a pass", v_[0]["ok"] is None and o_[0]["ok"])
check("sky: a judge's 'smoke' passes, 'ash fall' fails", S.judge_captures(shots, "Smoke")[1][0]["ok"] is True
      and S.judge_captures(shots, "ash fall")[1][0]["ok"] is False)
check("sky: a capture with no path is an invalid opportunity", not S.judge_captures(shots + [{"path": None}], "smoke")[0][0]["ok"])
check("error_lines keeps Error and Exception lines only", S.error_lines(
    [{"type": "Error", "text": "a"}, {"level": "exception", "text": "b"}, {"type": "Warning", "text": "c"}]) == ["a", "b"])


# ---- 3. the chain against a fake game
class Stop(Exception):
    pass


PROBE_FITS = 30   # the twin's screen at the zoom a scene leaves: cells, a 50 x 50 sky over it (MEASURED refusal)


class Game(object):
    """A twin of MapComponent_RM_SmokeWeather over a 250 map, two colonists and a burning strip."""

    def __init__(self, fault=None, geysers=()):
        self.fault, self.clock, self.notes, self.geysers = fault, 0, [], list(geysers)
        self.weather, self.age, self.last = "Clear", 0, "Clear"
        self.pawns, self.roof, self.fire_on, self.burned, self.shots = {}, set(), False, 0, 0
        self.gp, self.hp = 37, 113
        self.calibrated, self.shot_rects = False, []

    def roofed(self, cell):
        return cell in self.roof

    def advance(self, n):
        for _ in range(int(n)):
            self.clock += 1
            self.age += 1
            lerp = min(1.0, self.age / 4000.0)
            share = (lerp if self.weather == S.SMOKE else 0) + ((1 - lerp) if self.last == S.SMOKE else 0)
            for p in self.pawns.values():
                if (self.clock + self.gp) % 250 == 0 and share > 0 and not self.roofed(p["cell"]):
                    if not (self.fault == "no_hediff" and p["id"] == "O"):
                        p["sev"] = min(1.0, p["sev"] + 0.02 * min(1.0, share))
                if self.fault == "roofed_hediff" and p["id"] == "R" and self.clock % 250 == 0 and share > 0:
                    p["sev"] = min(1.0, p["sev"] + 0.02)
                if p["sev"] > 0 and (self.clock + self.hp) % 200 == 0:
                    p["sev"] = max(0.0, p["sev"] - 0.008)
            for p in self.pawns.values():   # AutoUndrafter: drafted and waiting UNDRAFT_TICKS, the pawn goes to work
                if p.get("drafted") and self.clock - p["draftTick"] >= 10000:
                    p["drafted"], p["loose"] = False, True
            if self.fire_on and self.clock % 530 == 0 and self.burned < 40:
                self.burned += 1
            if self.fault == "fire_out" and self.weather == S.SMOKE:
                self.fire_on = False

    def row(self, p):
        hs, caps = [], {"Breathing": 1.0, "Moving": 1.0, "Sight": 1.0}
        if p["sev"] > 0:
            st = S.stage_of(p["sev"], SPEC)
            hs.append({"def": S.CHOKE, "label": "%s (%s)" % (SPEC["label"], st["label"]), "severity": p["sev"]})
            if self.fault != "no_cap_drop":
                for k, v in st["caps"].items():
                    caps[k] += v
        if self.fault == "heatstroke" and p["id"] == "O" and self.clock > 6000:
            hs.append({"def": "Heatstroke", "label": "heatstroke (minor)", "severity": 0.05})
        x, z = p["cell"]
        if p.get("loose"):
            x += 3
        if self.fault == "moved" and p["id"] == "O" and self.clock > 8000:
            x += 2
        return {"id": p["id"], "x": x, "z": z, "dead": False, "downed": False, "mentalState": None,
                "health": {"hediffs": hs, "capacities": caps}}

    def call(self, tool, **kw):
        if tool == "jawa/set_draft":
            p = self.pawns.get(kw["pawnId"])
            if p is not None and bool(kw["drafted"]) != bool(p.get("drafted")):   # Drafted's setter: a no-op unchanged
                p["drafted"] = bool(kw["drafted"])
                if p["drafted"]:
                    p["draftTick"] = self.clock
            return {"success": True}
        if tool == "jawa/weather_set":
            if self.fault != "not_smoke" or kw["weather"] != S.SMOKE:
                self.last, self.weather, self.age = self.weather, kw["weather"], 0
            return {"success": True}
        if tool == "jawa/weather_get":
            rain = 0.02 if self.fault == "rain" and self.weather == S.SMOKE else 0.0
            return {"weather": {"current": self.weather, "last": self.last, "curWeatherAge": self.age, "rainRate": rain}}
        if tool == "jawa/list_pawns":
            return {"pawns": [self.row(p) for p in self.pawns.values()]}
        if tool == "jawa/pawn_stats":
            return {"stats": [{"defName": "ToxicEnvironmentResistance", "value": 0.0}], "refused": []}
        if tool == "jawa/list_things":
            if self.fault == "things_unreadable":
                return {"success": False, "error": "timeout"}
            th = [{"def": "SteamGeyser", "x": x, "z": z} for x, z in self.geysers] if kw["defName"] == "SteamGeyser" \
                else []
            return {"success": True, "things": th, "countMatched": len(th), "scanned": 54669}
        if tool == "jawa/set_roof_batch":
            kind, rect = kw["ops"].split(":")
            x, z, w, h = [int(v) for v in rect.split(",")]
            cells = set((a, b) for a in range(x, x + w) for b in range(z, z + h))
            self.roof = self.roof | cells if kind != "None" else self.roof - cells
            return {"success": True}
        return {"success": True}


def run(game, env=None, judge=None):
    verdicts, calls = {}, []

    class Comp(object):
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, et, ev, tb):
            if et is None:
                verdicts[self.name] = "PASS"
            elif et is Stop:
                verdicts[self.name] = ev.args[0]
            else:
                verdicts[self.name] = "CRASH %s: %s" % (et.__name__, ev)
            return True

    class T(object):
        session, upstream_failed, anchor = object(), False, None

        def bridge_call(self, tool, **kw):
            calls.append(tool)
            return game.call(tool, **kw)

        def screenshot(self, name=None, rect=None, ppc=None):
            # play_zoom.shoot's refusal: its first rect is probed at the zoom the last call left, and a rect over
            # PROBE_FITS cells does not fit there (ArchSmall 2026-11-27: the 50 x 50 sky refused)
            if not game.calibrated and max(rect[2], rect[3]) > PROBE_FITS:
                stop("UNMEASURED")("play-zoom calibration: rect %r does not fit the viewport" % (rect,))
            game.calibrated = True
            game.shot_rects.append(tuple(rect))
            game.shots += 1
            return "/fake/%s.png" % name

    def stop(v):
        def f(*a):
            raise Stop(v, a[-1])
        return f

    def spawn(t, x, z):
        pid = "R" if (x, z) == tuple(S.geometry(t.anchor)["R"]) else "O"   # the pad the chain picked
        game.pawns[pid] = {"id": pid, "cell": (x, z), "sev": 0.0}
        return pid

    def get_defs(t, defs, fields, deep=True):
        if game.fault == "v010":
            stop("FAIL")("get_defs could not resolve %r" % defs)
        return {}

    def fire(t, rect, size=1.2):
        game.fire_on = True

    def count(t, d, rect=None):
        if d == "Fire":
            return 12 if game.fire_on else 0
        return 480 - 12 * game.burned

    def pad(t, xz):
        t.anchor = xz

    def open_ground(t, rect, margin=0, soil=None):
        """The real one's refusal: a geyser (destroyable false) left standing in the cleared rect is UNMEASURED SITE."""
        x, z, w, h = rect
        big = (x - margin, z - margin, w + 2 * margin, h + 2 * margin)
        left = [c for c in game.geysers if any(big[0] <= c[0] + i < big[0] + big[2] and big[1] <= c[1] + j < big[1] + big[3]
                                               for i in (0, 1) for j in (0, 1))]
        if left:
            stop("UNMEASURED")("SITE: %s could not be made open ground: %d SteamGeyser" % (V._rs(big), len(left)))

    ns = types.SimpleNamespace(
        _teardown=lambda **k: (lambda fn: fn), _comp=lambda t, n, **k: Comp(n), _live=lambda t: True,
        _independent=lambda t: None, _unmeasured=stop("UNMEASURED"), _fail=stop("FAIL"),
        _wait=lambda t, n, fast=None: game.advance(n), _note=lambda t, k, v: game.notes.append((k, v)),
        _load_registered_site=lambda t: (1, ""), _pad=pad, _rs=V._rs, _get_defs=get_defs, _map_size=lambda t: (250, 250),
        _ten_gate_on=lambda t: True, _set=lambda t, v: None, _extinguish=lambda t: None,
        _open_ground=open_ground, _spawn_colonist=spawn, RUIN_NOT_A_RUIN=V.RUIN_NOT_A_RUIN,
        _plants=lambda t, p, rect, growth=1.0: None, _fire=fire, _count=count, _log_mark=lambda t: 0,
        _log_since=lambda t, m, limit=1000: ([{"type": "Error", "text": "planted"}] if game.fault == "error_line"
                                             else [{"type": "Message", "text": "ok"}]),
        weather_name=V.weather_name, padded_inside=V.padded_inside, _heat_guarded=lambda t: False,
        _heat_guard=lambda t, why: None)
    chains = {}
    S.register(types.SimpleNamespace(chain=lambda n: (lambda fn: chains.setdefault(n, fn))), ns)
    saved = dict((k, os.environ.get(k)) for k in (S.PLANT_ENV, S.OUT_ENV, S.JUDGE_ENV))
    os.environ[S.OUT_ENV] = os.path.join(os.environ.get("TMPDIR", "/tmp"), "swc_selftest")
    for k, v in ((S.PLANT_ENV, env), (S.JUDGE_ENV, judge)):
        if v:
            os.environ[k] = v
        else:
            os.environ.pop(k, None)
    try:
        chains["smoke_weather_chokes"](T())
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return verdicts, calls


COMPS = ("smoke_weather_stage", "smoke_weather_reads", "smoke_chokes_outdoors", "smoke_spares_roofed",
         "smoke_puts_out_no_fire", "smoke_sky_reads_as_smoke", "smoke_weather_no_error_line")
clean, calls = run(Game(), judge="smoke")
print("[swc-st] clean run, judge 'smoke': %r" % clean)
check("clean game with the judge's 'smoke': all seven components PASS",
      len(clean) == 7 and all(clean.get(c) == "PASS" for c in COMPS), clean)
check("clean game: the chain forced the weather, read health and the resistance, set the wind and drafted",
      all(x in calls for x in ("jawa/weather_set", "jawa/list_pawns", "jawa/pawn_stats", "jawa/static_call",
                               "jawa/set_draft", "jawa/pawn_genes", "jawa/build_batch")), sorted(set(calls)))
owed, _ = run(Game())
print("[swc-st] clean run, no judge: %r" % owed)
check("clean game with no judge: the sky is UNMEASURED (owed), every other component PASS",
      owed.get("smoke_sky_reads_as_smoke") == "UNMEASURED"
      and all(owed.get(c) == "PASS" for c in COMPS if c != "smoke_sky_reads_as_smoke"), owed)
FAULTS = {"no_hediff": ("smoke_chokes_outdoors", "FAIL"), "no_cap_drop": ("smoke_chokes_outdoors", "FAIL"),
          "roofed_hediff": ("smoke_spares_roofed", "FAIL"), "fire_out": ("smoke_puts_out_no_fire", "FAIL"),
          "rain": ("smoke_puts_out_no_fire", "FAIL"), "not_smoke": ("smoke_weather_stage", "FAIL"),
          "moved": ("smoke_chokes_outdoors", "UNMEASURED"), "heatstroke": ("smoke_chokes_outdoors", "UNMEASURED"),
          "error_line": ("smoke_weather_no_error_line", "FAIL"), "v010": ("smoke_weather_stage", "FAIL")}
for fault, (comp, want) in sorted(FAULTS.items()):
    v, _ = run(Game(fault), judge="smoke")
    others = dict((k, x) for k, x in v.items() if k != comp and x != "PASS")
    print("[swc-st] planted %s: %s=%s (want %s), other reds %r" % (fault, comp, v.get(comp), want, others))
    check("planted %s turns %s %s" % (fault, comp, want), v.get(comp) == want, v)
    check("planted %s: no component crashes" % fault, not any(str(x).startswith("CRASH") for x in v.values()), v)
v, _ = run(Game(), env="unroof", judge="smoke")
print("[swc-st] planted scene %s=unroof: %r" % (S.PLANT_ENV, v))
check("the live twin's planted unroof fails smoke_spares_roofed", v.get("smoke_spares_roofed") == "FAIL", v)
v, _ = run(Game(), judge="ash fall")
check("a judge's 'ash fall' fails the sky", v.get("smoke_sky_reads_as_smoke") == "FAIL", v)

v, _ = run(Game(geysers=GEYSERS_SITE1), judge="smoke")
print("[swc-st] measured site 1 geysers, judge 'smoke': %r" % v)
check("the measured site's geysers: all seven components PASS (the pad moves off the geyser)",
      all(v.get(c) == "PASS" for c in COMPS), v)
real_pick = S.pick_pad
S.pick_pad = lambda stuck, size, **k: S.PAD   # the planted fault: the pre-repair scene, PAD whatever stands on it
try:
    v, _ = run(Game(geysers=GEYSERS_SITE1), judge="smoke")
finally:
    S.pick_pad = real_pick
print("[swc-st] planted pad=PAD on the measured site: %r" % v.get("smoke_weather_stage"))
check("planted pad=PAD on the measured site: the stage reads UNMEASURED (the live run's reading)",
      str(v.get("smoke_weather_stage")) == "UNMEASURED", v)
gm = Game()
v, _ = run(gm, judge="smoke")
print("[swc-st] zoom probe: first capture rect %r (limit <= %d cells), %d captures" % (
    gm.shot_rects[0] if gm.shot_rects else None, PROBE_FITS, len(gm.shot_rects)))
check("the first capture is the small zoom probe at the sky's middle, and the sky shots follow it",
      gm.shot_rects and gm.shot_rects[0][2:] == (S.CAL_CELLS, S.CAL_CELLS) and len(gm.shot_rects) == 4
      and all(r[2] > PROBE_FITS for r in gm.shot_rects[1:]), gm.shot_rects)
real_cal = S.CAL_CELLS
S.CAL_CELLS = 0   # the planted fault: the pre-repair scene, no probe before the 50 x 50 sky
try:
    v, _ = run(Game(), judge="smoke")
finally:
    S.CAL_CELLS = real_cal
print("[swc-st] planted no zoom probe: stage %r" % v.get("smoke_weather_stage"))
check("planted no zoom probe: the stage reads UNMEASURED (the live run's reading)",
      str(v.get("smoke_weather_stage")) == "UNMEASURED", v)
real_redraft = S.REDRAFT
S.REDRAFT = False   # the planted fault: the pre-repair scene, drafted once at the stage and left
try:
    v, _ = run(Game(), judge="smoke")
finally:
    S.REDRAFT = real_redraft
print("[swc-st] planted no redraft: %r" % v)
check("planted no redraft: the auto-undrafted colonists walk and every pawn check reads UNMEASURED (the live reading)",
      all(v.get(c) == "UNMEASURED" for c in ("smoke_chokes_outdoors", "smoke_spares_roofed", "smoke_puts_out_no_fire")), v)
check("the reads' waits each stay under AutoUndrafter's delay", S.HOUR < S.UNDRAFT_TICKS, (S.HOUR, S.UNDRAFT_TICKS))
check("the probe rect lies at the middle of the sky", S.calibration_rect((10, 20, 50, 50)) == (32, 42, 6, 6))
v, _ = run(Game(fault="things_unreadable"), judge="smoke")
check("an unreadable geyser count: the stage reads UNMEASURED, never 'no geyser'",
      str(v.get("smoke_weather_stage")) == "UNMEASURED", v)

# ---- 4. the record
check("validation.py registers smoke_weather_chokes", any(
    k == "smoke_weather_chokes" or (isinstance(k, tuple) and k[0] == "smoke_weather_chokes") for k in V.suite.chains))

print("%s: %d checks, %d failed" % (os.path.basename(__file__), N["run"], N["bad"]))
sys.exit(1 if N["bad"] else 0)
