#!/usr/bin/env python3
"""Whole-map model of the Pyrelands burn: vanilla Fire (RimWorld 1.6 Fire.cs, read through RimSage 2026-11-16), the
vanilla weather decider, and this mod's burn line, fire clock, keep-alive, black-rain dousing and grass regrowth.

One beat = 150 ticks (Fire.ComplexCalcsInterval). Every number here is read from the game or the mod, not tuned:
  Fire: growth 0.00055 x flammability x 150 a beat, cap 1.75, out under 0.1; damage round-random(clamp(0.0125 + 0.0036 x size,
        0.0125, 0.05) x 150) to the plant; spreads above size 1 every max(75, 150 - (size-1) x 40) ticks: 80% one of the 8
        neighbours (GenRadial.ManualRadialPattern[1..8]), 20% a spark to [10..20]; a spread takes with chance = the target's
        flammability; rain Extinguish 10 a beat; black rain adds RM_FireEcoKernel.BlackRainDouseAmount.
  FireWatcher: danger = sum(0.5 + size), large above 90, re-read every 426 ticks.
  WeatherDecider: next weather by commonality; rain x15 and the weather's duration x0.25 while danger is large; nothing
        below Neutral favorability in the first 8 days after settling.
  Mod: PyrelandsTuning (fire clock 2-4 days, a 9-cell line at 0.35; keep-alive after 120000 quiet ticks, one 0.1 smoulder).
Regrowth is the one empirical part: fitted to the real walk saves (visit 1), see CALIBRATION in selftest.

The model is checked against the game by `validate_against_walk` (the real two-week walk's per-cell burn grid).
"""
import math
import numpy as np

BEAT = 150
DAY = 60000
ADJ = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
SPARK = [(-2, 0), (0, 2), (0, -2), (2, 1), (2, -1), (-2, 1), (-2, -1), (-1, 2), (1, 2), (-1, -2), (1, -2)]
FLAM = np.array([0.0, 1.6, 0.7])      # none, ember grass, quickgrass (Defs/ThingDefs_Plants)
HP = np.array([0.0, 28.0, 32.0])

# name: (commonality, favorability 0 VeryBad..3 Good, rainRate, duration lo, hi, lightning strike interval or 0, repeatable)
WEATHERS = {
    "AshDrift":        (40, 2, 0.0, 16000, 160000, 0, True),
    "DryThunderstorm": (20, 0, 0.0, 15000, 40000, 1200, False),
    "AshFall":         (14, 2, 0.0, 25000, 70000, 0, False),
    "Cinderfall":      (4, 0, 0.0, 12000, 30000, 640, False),
    "BlackRain":       (3, 0, 1.1, 2500, 6000, 0, False),
    "Fog":             (2, 2, 0.0, 16000, 160000, 0, False),
    "GrayPall":        (1, 1, 0.0, 16000, 160000, 0, False),
    "Windy":           (2, 2, 0.0, 16000, 160000, 0, True),
    "Overcast":        (2, 2, 0.0, 16000, 160000, 0, False),
}

DEFAULTS = dict(
    dousing=40.0,            # RM_FireEcoKernel.BlackRainDousingDefault
    settle_gate_days=8,      # vanilla: favorability < Neutral never in the first 8 days
    weather=True,            # False = sky locked clear (the visit-1 site profile)
    clock=True, keepalive=True,
    front_min_days=2.0, front_max_days=4.0, front_width=9, front_size=0.35,
    quiet_ticks=120000, retry_ticks=2500, smoulder=0.1, min_dist_colony=32.0,
    sprout_per_day=0.20, loss_per_day=0.08, ember_share=0.79,   # fitted to the walk saves
    wind=None,               # the bearing the wind blows toward, degrees (0 = +z); None = vanilla's even spread
    wind_k=11.0,             # DROPPED candidate (a weighted wind on vanilla spread): spread weight max(0, cos)^k
    wind_lin=None,           # candidate (owner, 2026-11-16): spread weight 1 + a cos: less against the wind, vanilla across, more along
    wind_side=None,          # candidate in between: weight `side` across the wind, rising to 2 straight downwind, 0 upwind
    wind_drift_deg_per_day=0.0,
    carried=False,           # the pick: the wind carries the fire (RM_BurnKernel.CarryPlan: one cell on per fire, once, and one gap cell)
    carry_ticks=1200, carry_reach=2,   # RM_BurnKernel.WindCarryTicks / WindCarryReach (the selftest reads them from the C# file)
    heal_reach=5, heal_recent=60000,   # RM_BurnKernel.HealReach / HealRecentTicks (selftest_pyrelands_burn_front_lanes.py reads them)
    carry_merge=True,        # with heal_reach=0 and this False: the rule before 2026-11-22 (lanes; the lanes test's --old)
    burn_stamps=True,        # RM_PyrelandsSettings.freshBurnBonusEnabled: the ash field stamps every burning cell; off, the heal
                             # reads live fires and MapComponent_BurnLine.CarriedAt (cells whose fire was carried on) only
    carry_heal=None,         # DROPPED candidate: lanes that heal (wind_carry_plan); None = the shipped one-cell rule
    carry_splits=1,          # MUTANT only: a fire lights this many cells (2 = a fire makes two, the flood comes back)
    cure_days=0.0,           # DROPPED candidate: grass younger than this does not carry fire
    home=None,               # (x0, z0, x1, z1) home area, or None
)


def wind_weights(bearing_deg, k, offsets):
    """Spread weights of each offset under a wind blowing TOWARD bearing_deg (0 = +z, clockwise): max(0, cos)^k.
    The same formula ships in RM_BurnKernel.WindSpreadWeight; the selftest compares the two tables."""
    r = math.radians(bearing_deg)
    wx, wz = math.sin(r), math.cos(r)
    out = []
    for dx, dz in offsets:
        c = (dx * wx + dz * wz) / math.hypot(dx, dz)
        out.append(max(0.0, c) ** k)
    return np.array(out)


DIRS8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # clockwise from +z (north)
FUEL = 1


def wind_probes(bearing_deg, roll01, roll2, reach):
    """RM_BurnKernel.WindProbes: the cells a fire tries, in order, when the wind carries it on. The compass step nearest the
    bearing and its neighbour on the bearing's side are tried first (the neighbour with chance = how far the bearing leans to
    it, so the mean heading is the wind), then the neighbour on the other side; then each of the three further out to `reach`.
    Never sideways, never back."""
    b = bearing_deg % 360.0
    n = int(math.floor(b / 45.0 + 0.5)) % 8
    delta = b - 45.0 * math.floor(b / 45.0 + 0.5)          # -22.5 .. 22.5
    if delta > 0: side = 1
    elif delta < 0: side = -1
    else: side = 1 if roll2 < 0.5 else -1
    near, lean, far = DIRS8[n], DIRS8[(n + side) % 8], DIRS8[(n - side) % 8]
    first, second = (lean, near) if roll01 < abs(delta) / 45.0 else (near, lean)
    out = []
    for d in range(1, reach + 1):
        for v in (first, second, far):
            out.append((v[0] * d, v[1] * d))
    return out


BARE, FUEL, BURNING = 0, 1, 2


def heal_dirs(bearing_deg, roll_side):
    """RM_BurnKernel.HealDirs: the four steps a carried fire looks along, beside it, for a gap in its own line, from the
    compass step nearest the bearing: the two at 90 degrees (beside), then the two at 135 degrees (beside and behind: they
    close the checkerboard a line lit across a diagonal wind leaves). roll_side picks which side comes first."""
    b = bearing_deg % 360.0
    n = int(math.floor(b / 45.0 + 0.5)) % 8
    s1, s2 = (1, -1) if roll_side < 0.5 else (-1, 1)
    return [DIRS8[(n + 2 * s1) % 8], DIRS8[(n + 2 * s2) % 8], DIRS8[(n + 3 * s1) % 8], DIRS8[(n + 3 * s2) % 8]]


def carry_plan(bearing_deg, roll01, roll2, roll_side, reach, heal_reach, cell, anchor, splits=1, merge=True):
    """RM_BurnKernel.CarryPlan: the cells one carried fire lights, as offsets from it, and how many of them are the heal
    (0 or 1). cell(dx, dz) is BARE, FUEL or BURNING; anchor(dx, dz) is true where a fire burns or the ground burned lately.
    RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES: with the carry alone a line lit with gaps (the scar's
    arc lights every 3rd or 4th cell) walked as separate one-cell lanes for good, grass standing between them.
    1. Carry: the first probe (wind_probes) that holds FUEL. A probe that holds a fire already ends the carry with nothing
       lit (merge): the lane runs on in that fire. Without it a gap cell lit beside a lane shoves every lane beside it one
       cell out and the flank creeps at 45 degrees, a flood (measured 2026-11-22: 10,600 cells burned against 1,440).
    2. Heal (heal_reach > 0): from that cell T, the first heal_dirs step s whose cell T+s holds FUEL and whose ray T+k*s,
       k = 2 .. heal_reach + 1, meets an anchor (the ray passes bare cells, as the carry's reach does: stopped at the first
       bare cell, a 70%-cover burn left 0.38 of its cells in one-cell strands, vanilla's own fire 0.23; passing, 0.27).
       That one gap cell is lit too. The fire's
       own trail never lies on those rays (a lane moves at most one cell aside a row), so the outermost lane of a line
       never heals outward: the burn is never wider than what was lit, or what it ran into.
    splits (MUTANT only): the carry lights that many probes."""
    out = []
    for dx, dz in wind_probes(bearing_deg, roll01, roll2, reach):
        st = cell(dx, dz)
        if st == BURNING and merge:
            break
        if st == FUEL:
            out.append((dx, dz))
            if len(out) >= splits:
                break
    if not out or heal_reach <= 0:
        return out, 0
    tx, tz = out[0]
    for sx, sz in heal_dirs(bearing_deg, roll_side):
        if cell(tx + sx, tz + sz) != FUEL:
            continue
        for k in range(2, heal_reach + 2):
            ax, az = tx + k * sx, tz + k * sz
            if anchor(ax, az):
                return out + [(tx + sx, tz + sz)], 1
    return out, 0
CARDINAL = [(0, 1), (1, 0), (0, -1), (-1, 0)]       # the wind blows toward north, east, south, west


def wind_carry_plan(state, roll01, reach, heal):
    """DROPPED candidate (measured 2026-11-16: with siblings sought in the fire's own row the lanes drift out of step and the
    line thins to one or two fires on 70% grass; sought in the new row it floods, 774 fires). Kept so the map can be re-run.
    In the wind's own frame: `along` cells downwind, `across` cells to the side.
    state(along, across) is BARE (nothing to burn), FUEL or BURNING. Returns the cells this fire lights, as (along, across).

    Carry (at most one cell): the lane straight downwind, out to `reach` (a spark over bare ground); a cell already burning
    there means the lane is carried and this fire adds nothing; with nothing to burn straight on, one diagonal step
    (roll01 picks which side first). Never sideways, never back.
    Heal (heal > 0): where a sibling burns in this fire's own row, 2 .. heal + 1 lanes across, the cells between the two lanes
    in the next row catch too. A hole in the line closes; nothing is ever lit beyond the outermost lane."""
    out = []
    carried = False
    for d in range(1, reach + 1):
        st = state(d, 0)
        if st == BURNING:
            carried = True
            break
        if st == FUEL:
            out.append((d, 0)); carried = True
            break
    if not carried:
        for side in ((1, -1) if roll01 < 0.5 else (-1, 1)):
            if state(1, side) == FUEL:
                out.append((1, side))
                break
    for side in (1, -1):
        for k in range(2, heal + 2):
            if state(0, side * k) == BURNING:
                for g in range(1, k):
                    if state(1, side * g) == FUEL and (1, side * g) not in out:
                        out.append((1, side * g))
                break
    return out


def carry_plan_checksum(cases=1200, reach=2, heal_reach=5):
    """The CarryPlan table both sides compute (PyrelandsFuzz.CarryPlanTable asserts CarryPlanChecksum): per case a 17 x 17
    neighbourhood drawn by a 31-bit LCG (20% bare, 50% fuel, 10% burning, 20% burned lately: bare but an anchor), a bearing
    on a 7.5-degree step and exact-binary rolls, so float and double agree. Hashes every planned cell, the count and the heal."""
    h = 0
    for c in range(cases):
        x = 12345 + c
        grid = {}
        for dz in range(-8, 9):
            for dx in range(-8, 9):
                x = (x * 1103515245 + 12345) & 0x7fffffff
                grid[(dx, dz)] = (x >> 8) % 100
        bearing = (c * 75 % 3600) / 10.0
        r1, r2, rs = (c * 3 % 8) / 8.0, (2 * (c * 5 % 8) + 1) / 16.0, (2 * (c * 7 % 4) + 1) / 8.0

        def cell(dx, dz):
            v = grid.get((dx, dz))
            if v is None or v < 20 or v >= 80: return BARE
            return FUEL if v < 70 else BURNING

        def anchor(dx, dz):
            v = grid.get((dx, dz))
            return v is not None and v >= 70
        plan, healed = carry_plan(bearing, r1, r2, rs, reach, heal_reach, cell, anchor)
        for dx, dz in plan:
            h = (h * 31 + (dx + 20) * 41 + (dz + 20)) % 1000000007
        h = (h * 31 + len(plan) * 7 + healed) % 1000000007
    return h


class Sim:
    def __init__(self, plant, plantable, seed=0, **kw):
        self.P = dict(DEFAULTS); self.P.update(kw)
        self.rng = np.random.default_rng(seed)
        self.H, self.W = plant.shape
        self.plant = plant.astype(np.int8).copy()
        self.plantable = plantable.copy()
        self.hp = HP[self.plant].copy()
        self.sprout_tick = np.full(plant.shape, -10 * DAY, np.int64)
        self.size = np.zeros(plant.shape)
        self.acc = np.zeros(plant.shape)
        self.burn = np.full(plant.shape, -1, np.int64)
        self.born = np.zeros(plant.shape, np.int64); self.carried = np.zeros(plant.shape, bool)
        self.carried_at = np.full(plant.shape, -1, np.int64)
        self.tick = 0
        self.weather, self.last_weather = "AshDrift", "AshDrift"
        self.w_age, self.w_dur = 0, 10000
        self.large = False
        self.quiet = 0; self.last_reseed = -99999
        self.next_front = -1
        self.wind = self.P["wind"]
        self.log = []           # (tick, event, detail)
        self.series = []        # per sample: tick, fires, weather, cover, burned_today
        self._burned_since = 0
        self.home_mask = np.zeros(plant.shape, bool)
        if self.P["home"]:
            x0, z0, x1, z1 = self.P["home"]; self.home_mask[z0:z1, x0:x1] = True
        self.home_fire_ticks = 0; self.first_home_fire = -1
        self.hist = []          # burn-centre samples (tick, x, z), one per 2500 ticks while burning
        self.fire_beats = 0; self.beats = 0; self.gap = 0; self.longest_gap = 0
        self.rains = []         # dicts: start, fires_at_start, out_tick
        self.lit_by_day = {}    # game day -> cells that caught fire that day
        self.heal_lit = 0
        self.carries = 0; self.carry_lit = 0      # fires carried on, cells they lit (never more than one each)

    # ---------------------------------------------------------------- ignition
    def chance(self, z, x):
        f = FLAM[self.plant[z, x]]
        if self.P["cure_days"] > 0:
            f = np.where(self.tick - self.sprout_tick[z, x] >= self.P["cure_days"] * DAY, f, 0.0)
        return np.where(self.size[z, x] > 0, 0.0, f)

    def start(self, z, x, size):
        self.born[z, x] = self.tick; self.carried[z, x] = False
        self.lit_by_day[self.tick // DAY] = self.lit_by_day.get(self.tick // DAY, 0) + (np.size(z) if np.ndim(z) else 1)
        self.size[z, x] = size; self.acc[z, x] = self.rng.random(np.shape(z)) * 150 if np.ndim(z) else self.rng.random() * 150
        self.burn[z, x] = self.tick

    def spread_weights(self, offsets):
        P = self.P
        if P["wind_lin"] is None and P["wind_side"] is None:
            return wind_weights(self.wind, P["wind_k"], offsets)
        r = math.radians(self.wind); wx, wz = math.sin(r), math.cos(r)
        out = []
        for dx, dz in offsets:
            c = (dx * wx + dz * wz) / math.hypot(dx, dz)
            if P["wind_lin"] is not None: out.append(max(0.0, 1.0 + P["wind_lin"] * c))
            else: out.append(P["wind_side"] + (2.0 - P["wind_side"]) * c if c >= 0 else 0.0)
        return np.array(out)

    def lawful(self, z, x):
        if not (0 <= x < self.W and 0 <= z < self.H): return False
        if self.chance(z, x) <= 0 or self.home_mask[z, x]: return False
        if self.P["home"]:
            x0, z0, x1, z1 = self.P["home"]
            dx = max(x0 - x, 0, x - x1); dz = max(z0 - z, 0, z - z1)
            if dx * dx + dz * dz < self.P["min_dist_colony"] ** 2: return False
        return True

    def light_line(self, cx, cz, width, size, angle=None):
        if angle is None:
            angle = self.rng.random() * 360 if self.wind is None else self.wind + 90   # across the wind
        rad = math.radians(angle); sx, sz = math.sin(rad), math.cos(rad); m = max(abs(sx), abs(sz))
        lit = 0
        for i in range(-(width // 2), width - width // 2):
            x = cx + int(round(sx / m * i)); z = cz + int(round(sz / m * i))
            if self.lawful(z, x):
                self.start(z, x, size); lit += 1
        return lit

    def find_origin(self, kind=1):
        zs, xs = np.nonzero(self.plant == kind)
        for _ in range(30):
            if len(zs) == 0: break
            i = self.rng.integers(len(zs))
            if self.lawful(zs[i], xs[i]): return xs[i], zs[i]
        for _ in range(40):
            x, z = self.rng.integers(self.W), self.rng.integers(self.H)
            if self.lawful(z, x): return x, z
        return None

    # ---------------------------------------------------------------- weather
    def rain_rate(self):
        lerp = min(1.0, self.w_age / 4000.0)
        return WEATHERS[self.weather][2] * lerp + WEATHERS[self.last_weather][2] * (1 - lerp)

    def black_share(self):
        lerp = min(1.0, self.w_age / 4000.0)
        return (lerp if self.weather == "BlackRain" else 0.0) + ((1 - lerp) if self.last_weather == "BlackRain" else 0.0)

    def choose_weather(self):
        names, ws = [], []
        days = self.tick // DAY
        for n, (com, fav, rain, lo, hi, strike, rep) in WEATHERS.items():
            if n == self.weather and not rep: continue
            if fav < 2 and days < self.P["settle_gate_days"]: continue
            w = com * (15.0 if (self.large and rain > 0.1) else 1.0)
            names.append(n); ws.append(w)
        ws = np.array(ws, float)
        return names[self.rng.choice(len(names), p=ws / ws.sum())]

    def weather_beat(self):
        self.w_age += BEAT
        dur = self.w_dur * (0.25 if self.large else 1.0)
        if self.w_age > dur:
            nxt = self.choose_weather()
            self.last_weather, self.weather, self.w_age = self.weather, nxt, 0
            lo, hi = WEATHERS[nxt][3], WEATHERS[nxt][4]
            self.w_dur = self.rng.integers(lo, hi + 1)
            if nxt == "BlackRain":
                self.rains.append(dict(start=self.tick, fires=int((self.size > 0).sum()), out=-1, dur=int(self.w_dur)))
            self.log.append((self.tick, "weather", nxt))
        strike = WEATHERS[self.weather][5]
        if strike and self.rng.random() < BEAT / strike:
            x, z = self.rng.integers(self.W), self.rng.integers(self.H)
            for dz in range(-2, 3):
                for dx in range(-2, 3):
                    if dx * dx + dz * dz <= 1.9 * 1.9 and 0 <= x + dx < self.W and 0 <= z + dz < self.H:
                        if self.rng.random() < self.chance(z + dz, x + dx):
                            self.start(z + dz, x + dx, 0.2 + 0.4 * self.rng.random())

    # ---------------------------------------------------------------- one beat
    def beat(self):
        P = self.P; rng = self.rng
        self.tick += BEAT; self.beats += 1
        F = self.size > 0
        nf = int(F.sum())
        if nf:
            flam = FLAM[self.plant] * F
            dead = F & (flam < 0.01)
            self.size[dead] = 0.0
            F &= ~dead
            zs, xs = np.nonzero(F)
            s = self.size[zs, xs]
            d = np.clip(0.0125 + 0.0036 * s, 0.0125, 0.05) * 150
            d = np.floor(d) + (rng.random(len(d)) < (d - np.floor(d)))
            self.hp[zs, xs] -= np.maximum(1, d)
            gone = self.hp[zs, xs] <= 0
            self.plant[zs[gone], xs[gone]] = 0
            s = np.minimum(1.75, s + 0.00055 * flam[zs, xs] * 150)
            if P["weather"]:
                if self.rain_rate() > 0.01: s = s - 0.10
                sh = self.black_share()
                if sh > 0 and P["dousing"] > 0: s = s - P["dousing"] * min(1.0, sh) * 0.01
            out = s < 0.1
            s[out] = 0.0
            self.size[zs, xs] = s
            self.burn[zs[~out], xs[~out]] = self.tick
            # spread
            if P["carried"]:
                due = (~out) & (~self.carried[zs, xs]) & (self.tick - self.born[zs, xs] >= P["carry_ticks"])
                dz_, dx_ = zs[due], xs[due]
                for i in rng.permutation(len(dz_)):      # the game ticks its fires in no row order
                    z0, x0 = int(dz_[i]), int(dx_[i])
                    self.carried[z0, x0] = True; self.carries += 1; self.carried_at[z0, x0] = self.tick
                    if P["carry_heal"] is None:
                        # THE SHIPPED RULE (RM_BurnKernel.CarryPlan): the first cell downwind that can take fire, unless the lane
                        # runs on in a fire already there; and one gap cell of its own line beside it.
                        def cell(dx, dz, x0=x0, z0=z0):
                            tx, tz = x0 + dx, z0 + dz
                            if not (0 <= tx < self.W and 0 <= tz < self.H): return BARE
                            if self.size[tz, tx] > 0: return BURNING
                            return FUEL if self.chance(tz, tx) > 0 else BARE

                        def anchor(dx, dz, x0=x0, z0=z0):
                            tx, tz = x0 + dx, z0 + dz
                            if not (0 <= tx < self.W and 0 <= tz < self.H): return False
                            stamp = max(int(self.burn[tz, tx]) if P["burn_stamps"] else -1, int(self.carried_at[tz, tx]))
                            return bool(self.size[tz, tx] > 0 or (stamp >= 0 and self.tick - stamp <= P["heal_recent"]))
                        plan, healed = carry_plan(self.wind, rng.random(), rng.random(), rng.random(), P["carry_reach"],
                                                  P["heal_reach"], cell, anchor, P["carry_splits"], P["carry_merge"])
                        for dx, dz in plan:
                            self.start(z0 + dz, x0 + dx, 0.1)
                        self.carry_lit += len(plan) - healed; self.heal_lit += healed
                        continue
                    # DROPPED candidate (lanes that heal): see wind_carry_plan.
                    ux, uz = CARDINAL[int(round(self.wind / 90.0)) % 4]; px, pz = uz, -ux

                    def state(al, ac, x0=x0, z0=z0):
                        tx, tz = x0 + al * ux + ac * px, z0 + al * uz + ac * pz
                        if not (0 <= tx < self.W and 0 <= tz < self.H): return BARE
                        if self.size[tz, tx] > 0: return BURNING
                        return FUEL if self.chance(tz, tx) > 0 else BARE
                    for al, ac in wind_carry_plan(state, rng.random(), P["carry_reach"], P["carry_heal"]):
                        tx, tz = x0 + al * ux + ac * px, z0 + al * uz + ac * pz
                        if self.size[tz, tx] == 0:
                            self.start(tz, tx, 0.1); self.carry_lit += 1
            big = (s > 1.0) & (not P["carried"])
            if big.any():
                bz, bx, bs = zs[big], xs[big], s[big]
                a = self.acc[bz, bx] + BEAT
                interval = np.maximum(75.0, 150.0 - (bs - 1.0) * 40.0)
                n = np.minimum(2, np.floor(a / interval)).astype(int)
                self.acc[bz, bx] = a - n * interval
                for rep in (1, 2):
                    m = n >= rep
                    if not m.any(): continue
                    z0, x0 = bz[m], bx[m]; k = len(z0)
                    near = rng.random(k) < 0.8
                    if self.wind is None:
                        ai = rng.integers(0, 8, k); si = rng.integers(0, len(SPARK), k)
                    else:
                        wa = self.spread_weights(ADJ); wsp = self.spread_weights(SPARK)
                        ai = rng.choice(8, k, p=wa / wa.sum()); si = rng.choice(len(SPARK), k, p=wsp / wsp.sum())
                    adj = np.array(ADJ); sp = np.array(SPARK)
                    dx = np.where(near, adj[ai, 0], sp[si, 0]); dz = np.where(near, adj[ai, 1], sp[si, 1])
                    tx, tz = x0 + dx, z0 + dz
                    ok = (tx >= 0) & (tx < self.W) & (tz >= 0) & (tz < self.H)
                    tx, tz = tx[ok], tz[ok]
                    ch = self.chance(tz, tx)
                    take = rng.random(len(ch)) < ch
                    tx, tz = tx[take], tz[take]
                    if len(tx):
                        self.size[tz, tx] = 0.1; self.acc[tz, tx] = rng.random(len(tx)) * 150; self.burn[tz, tx] = self.tick
                        self.lit_by_day[self.tick // DAY] = self.lit_by_day.get(self.tick // DAY, 0) + len(np.unique(tz * self.W + tx))
        # bookkeeping on the 426-tick watch (every 3 beats)
        F = self.size > 0; nf = int(F.sum())
        if self.beats % 3 == 0:
            self.large = float((0.5 + self.size[F]).sum()) > 90.0
        if nf:
            self.fire_beats += 1; self.gap = 0
            if self.home_mask.any():
                hf = int((F & self.home_mask).sum())
                if hf:
                    self.home_fire_ticks += BEAT
                    if self.first_home_fire < 0: self.first_home_fire = self.tick
            if not self.hist or self.tick - self.hist[-1][0] >= 2500:
                zs, xs = np.nonzero(F); self.hist.append((self.tick, int(xs.mean()), int(zs.mean())))
        else:
            self.gap += BEAT; self.longest_gap = max(self.longest_gap, self.gap)
        for r in self.rains:
            if r["out"] < 0 and nf == 0 and self.tick >= r["start"]:
                r["out"] = self.tick
        if P["weather"]: self.weather_beat()
        # keep-alive and the fire clock (MapComponent_BurnLine, PyrelandsFireFront)
        if P["keepalive"]:
            if nf: self.quiet = 0
            else:
                self.quiet += BEAT
                if self.quiet >= P["quiet_ticks"] and self.tick - self.last_reseed >= P["retry_ticks"]:
                    self.last_reseed = self.tick
                    for _ in range(40):
                        x, z = rng.integers(self.W), rng.integers(self.H)
                        if self.lawful(z, x):
                            if P["carried"]: self.light_line(x, z, P["front_width"], P["front_size"])
                            else: self.start(z, x, P["smoulder"])
                            self.quiet = 0
                            self.log.append((self.tick, "reseed", (int(x), int(z)))); break
        if P["clock"]:
            if self.next_front < 0:
                self.next_front = self.tick + int((P["front_min_days"] + rng.random() * (P["front_max_days"] - P["front_min_days"])) * DAY)
            elif self.tick >= self.next_front:
                self.next_front = self.tick + int((P["front_min_days"] + rng.random() * (P["front_max_days"] - P["front_min_days"])) * DAY)
                o = self.find_origin()
                if o:
                    lit = self.light_line(o[0], o[1], P["front_width"], P["front_size"])
                    self.log.append((self.tick, "front", (int(o[0]), int(o[1]), lit)))
        # regrowth and loss, once a game hour
        if self.tick % 2500 < BEAT:
            dt = 2500 / DAY
            bare = self.plantable & (self.plant == 0) & (self.size == 0)
            sprout = bare & (rng.random(bare.shape) < P["sprout_per_day"] * dt)
            kind = np.where(rng.random(bare.shape) < P["ember_share"], 1, 2).astype(np.int8)
            self.plant[sprout] = kind[sprout]; self.hp[sprout] = HP[kind[sprout]]; self.sprout_tick[sprout] = self.tick
            lose = (self.plant > 0) & (self.size == 0) & (rng.random(bare.shape) < P["loss_per_day"] * dt)
            self.plant[lose] = 0
            if self.wind is not None and P["wind_drift_deg_per_day"]:
                self.wind += rng.normal(0, P["wind_drift_deg_per_day"] * math.sqrt(dt))

    def cover(self):
        return float((self.plant > 0)[self.plantable].mean())

    def run(self, days, sample_ticks=2500, snap_days=()):
        snaps = {}
        end = self.tick + int(days * DAY)
        last_burned = (self.burn >= 0).sum()
        while self.tick < end:
            self.beat()
            if self.tick % sample_ticks < BEAT:
                self.series.append((self.tick, int((self.size > 0).sum()), self.weather, self.cover()))
            for d in snap_days:
                if abs(self.tick - d * DAY) < BEAT / 2 + 1 and d not in snaps:
                    snaps[d] = (self.burn.copy(), self.plant.copy(), self.size.copy())
        return snaps

    def summary(self):
        t = self.tick
        ser = np.array([(a, b, c) for a, b, _, c in self.series], float)
        fresh2 = 0
        # herd anchor: is there a burn-centre sample at least two days old (and under ten)?
        anchor_ok = sum(1 for (tk, f, w, c) in self.series if any(tk - 600000 <= h[0] <= tk - 120000 for h in self.hist))
        day_burn = np.bincount((self.burn[self.burn >= 0] // DAY).astype(int), minlength=int(t // DAY) + 1)
        return dict(
            days=t / DAY,
            fire_time_share=self.fire_beats / max(1, self.beats),
            longest_fireless_days=self.longest_gap / DAY,
            mean_fires=float(ser[:, 1].mean()) if len(ser) else 0.0,
            max_fires=float(ser[:, 1].max()) if len(ser) else 0.0,
            cover_mean=float(ser[:, 2].mean()) if len(ser) else 0.0,
            cover_min=float(ser[:, 2].min()) if len(ser) else 0.0,
            burned_share=float((self.burn >= 0)[self.plantable].mean()),
            black_rains=len(self.rains),
            rain_fires_at_start=[r["fires"] for r in self.rains],
            rain_ticks_to_out=[(r["out"] - r["start"]) if r["out"] >= 0 else None for r in self.rains],
            anchor_share=anchor_ok / max(1, len(self.series)),
            first_home_fire_day=self.first_home_fire / DAY if self.first_home_fire >= 0 else None,
            home_fire_days=self.home_fire_ticks / DAY,
            fronts=sum(1 for e in self.log if e[1] == "front"), reseeds=sum(1 for e in self.log if e[1] == "reseed"),
        )


def synthetic_map(size=250, seed=0, ember_share=0.79, cover=0.97, blobs=14):
    """A fresh map: grass on nearly every plantable cell, with rock and water blobs (about 17% of the map, as the real site)."""
    rng = np.random.default_rng(seed + 1000)
    yy, xx = np.mgrid[0:size, 0:size]
    solid = np.zeros((size, size), bool)
    for _ in range(blobs):
        cx, cz, r = rng.integers(size), rng.integers(size), rng.uniform(0.04, 0.10) * size
        solid |= ((xx - cx) ** 2 + (yy - cz) ** 2) < (r * (0.8 + 0.4 * rng.random((size, size)) ** 4)) ** 2
    plantable = ~solid
    plant = np.where(plantable & (rng.random((size, size)) < cover), np.where(rng.random((size, size)) < ember_share, 1, 2), 0)
    return plant.astype(np.int8), plantable


def pad_test(seed=0, rain=False, dousing=0.0, n=8):
    """The visit-1 rain_fire.py pad: n x n ember grass ringed by concrete, every cell lit. Returns fires each 250 ticks."""
    plant = np.zeros((n + 4, n + 4), np.int8); plant[2:n + 2, 2:n + 2] = 1
    s = Sim(plant, plant > 0, seed, weather=rain, clock=False, keepalive=False, sprout_per_day=0, loss_per_day=0, dousing=dousing)
    if rain:
        s.weather = s.last_weather = "BlackRain"; s.w_age = 4500; s.w_dur = 10 ** 9
        s.weather_beat = lambda: None
    zs, xs = np.nonzero(plant); s.size[zs, xs] = 0.5; s.acc[zs, xs] = 0
    # each fire's first complex calc falls anywhere in its first 150 ticks: model by a random head start in hp terms
    out = []
    phase = s.rng.integers(0, 150, plant.shape)
    for t in range(250, 3001, 250):
        while s.tick < t: s.beat()
        alive = (s.size > 0) | ((s.plant == 0) & (plant > 0) & (s.burn >= 0) & (s.tick - s.burn < phase))
        out.append(int(((s.size > 0)).sum()))
    return out
