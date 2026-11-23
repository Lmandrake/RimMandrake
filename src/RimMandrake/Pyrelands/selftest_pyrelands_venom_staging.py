#!/usr/bin/env python3
"""T_VENOM_STAGING (RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL): the sc_flamefang_venom scene lands one
flamefang bite on each patient, removes the biter for certain, and mauls nobody; so its venom rows read the mod.

Visit 2 (2026-11-21) read venom_tended_vs_untended UNMEASURED (the untended patient was never bitten) and venom_wait_out
UNMEASURED (the wait-out colonist died of BloodLoss; the flamefang kept attacking). The staging had three faults: the
biter was "killed" by an unchecked `jawa/damage Cut 500` on one random body part, which leaves it alive and manhunting
when the part is not vital; a victim that killed its biter before the bite got no second biter; and the 250-tick latch let
two or three bites stack venom. This test runs the SHIPPED scene code (flamefang_venom and _ten_flamefang_venom in
validation.py) against a scripted game and reads the scene's own verdicts.

The scripted game. Combat per tick: the manhunting biter walks to the nearest colonist and attacks every 99 ticks
(RM_Flamefang's 1.65 s cooldown), venom-fangs or head (seeded), 70 % to hit; a venom bite is a Bite wound plus the
shipped dose of RM_FlamefangVenom (severityPerDamageDealt x the venom-fangs' power after the fauna normalization patch,
read by venom_dose.py; visit 3 measured 0.45 where this model had assumed a flat 0.2), merged into the hediff. A drafted victim melees an adjacent
hostile whatever its fire-at-will (JobDriver_Wait.CheckForAutoAttack) and shoots one at range only with fire-at-will on
and a gun. `jawa/damage Cut 500` with no part destroys one seeded random part and kills only on a vital one;
`jawa/kill_hostiles` kills for certain. Health, continuous between reads: the def's numbers, read from the shipped def (severityPerDayNotImmune,
immunityPerDaySick, severityPerDayImmune, severityPerDayTended x quality for 12 h, lethalSeverity), and each
untended Bite wound bleeds `bleed` BloodLoss per day, lethal at 1. A death inside the clock stops the row as the governor
does (RESTART, UNMEASURED).

Hunger and flight (RIMMANDRAKE_FEED_PYRE_VENOM_FIXTURES_HUNGER_STOPS_WAITOUT, visit 4, 2026-11-22). No colonist eats: a
drafted pawn never does, and the site's food is not modelled (the worst case). Food falls by vanilla Need_Food (read in
RimSage): 2.6666667e-05 a tick x the pawn's hunger factor, x 0.5 below 0.24 and x 0.25 below 0.12; a colonist spawns at
0.8 (SetInitialLevel); `jawa/pawn_need` reads and sets it. A colonist at 0 stops the clock as the governor does
("starving", in BITE_STOP_ON and WAIT_OUT_STOP_ON). The scene's row start tops up as the real _comp does. An undrafted
colonist that a live manhunter is nearest to, or that stands within 12 cells of one, flees: it walks 40 cells straight
away at vanilla's 13 ticks a cell (MoveSpeed 4.6) and keeps walking after the biter dies, until it is drafted (visit 1:
an undrafted fresh colonist FleeAndCowers to the map edge). The 40 cells and the 12 are model choices, not measurements.
`jawa/list_pawns` rows carry x and z, as the bridge's do.

The range it declares (the grid): the colonists' weapons in spawn order (none, melee, gun, and mixes), the biter's attack
phase against the poll (0, 45, 98 ticks), the seed (tool choice, hits, the Cut's part), the bleed rate (0, 0.15/day), the
biter's health (20, 60: a fast or a slow kill by the victim), the hunger factor (1.0, and 2.25 = Biotech metabolism -5,
GeneTuning), and the bite's dose (the shipped dose, or armour and part
caps scaling it by 0.5, 0.8 or 1.0, seeded). The one-bite course over vanilla's damage roll and immunity factor is
selftest_pyrelands_venom_dose.py's. Planted mod faults: the bite carries no venom; a tend does
nothing; immunity never lowers the venom. Planted scene fault: PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1 (the doctor tends
the untended patient) reads FAIL, never UNMEASURED. Left out: the live pathing, real armour and part coverage, real bleed rates and
blood regrowth, the doctor's walk and medicine (Stage 6 runs the scene; its command is in unrun.jsonl).

  python3 <this file> [--validation PATH] [--schemas PATH] [--defs PATH]   exit 0 = every check PASS, 1 = any FAIL
"""
import argparse
import contextlib
import importlib.util
import itertools
import json
import os
import random
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import venom_dose as vd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "selftest_pyrelands_venom_staging"
VENOM = "RM_FlamefangVenom"
DAY, HOUR = 60000, 2500
COOLDOWN = 99                       # RM_Flamefang venom-fangs and head: cooldownTime 1.65 s
VITAL = ("Torso", "Head", "Neck")
PARTS = ("Torso", "Head", "Neck", "Tail", "Jaw", "Eye", "Tongue")
ROWS = ("venom_tended_vs_untended", "venom_wait_out")
FIRST = ("flamefang_bite_injects_venom", "venom_rises_untreated", "plain_bite_carries_no_venom")
FOOD_FALL = 2.6666667e-05          # vanilla Need_Food.BaseHungerRate for an adult human, a tick (RimSage)
FOOD_HUNGRY, FOOD_URGENT = 0.3 * 0.8, 0.3 * 0.4   # FoodLevelPercentageWantEat 0.3 (omnivore) x 0.8 and x 0.4
MAP = 250
FLEE_CELLS, FLEE_SEES, FLEE_TICKS_PER_CELL = 40, 12, 13   # model choices; 13 = 60 / MoveSpeed 4.6
VD = None        # the shipped venom numbers (venom_dose.read), set in main
RESULTS = []
SENT = {}       # tool -> every argument the scene sent it, over the whole grid


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" (%s)" % detail) if detail and not ok else ""))


def load_validation(path):
    mc = types.ModuleType("modcheck")

    class Suite(object):
        def __init__(self, name):
            self.chains = {}

        def chain(self, name):
            def deco(fn):
                self.chains[name] = fn
                return fn
            return deco

    class ExpectationFailed(Exception):
        pass

    mc.Suite, mc.Component, mc.ExpectationFailed = Suite, object, ExpectationFailed
    sys.modules.setdefault("modcheck", mc)
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location("pyre_validation_venom_staging", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Pawn(object):
    def __init__(self, pid, kind, faction, x, z, tick):
        self.id, self.kind, self.faction, self.x, self.z = pid, kind, faction, x, z
        self.alive, self.manhunter, self.drafted, self.fire_at_will = True, False, False, True
        self.weapon, self.hp, self.born = "none", 0.0, tick
        self.hediffs = []            # [{def, severity, part, tended}]
        self.immunity, self.tended_until, self.tend_q = 0.0, -1, 0.0
        self.next_attack = None
        self.next_melee = None
        self.food, self.flee = 0.8, None    # vanilla SetInitialLevel; flee = (dx, dz) cell to walk to, or None

    def sev(self, d):
        return sum(h["severity"] for h in self.hediffs if h["def"] == d)


class Game(object):
    def __init__(self, weapons=("melee",), phase=0, seed=1, bleed=0.0, biter_hp=20.0, doses=(1.0,), venom=True,
                 tend=True, immune_falls=True, hunger=1.0):
        self.weapons, self.phase, self.rng, self.bleed, self.biter_hp = weapons, phase, random.Random(seed), bleed, biter_hp
        self.hunger, self.starved, self.last_food, self.low = hunger, [], 0, 1.0
        self.venom, self.tend, self.immune_falls, self.doses = venom, tend, immune_falls, doses
        self.tick, self.pawns, self.n, self.ncol, self.deaths, self.bites = 0, {}, 0, 0, [], {}
        self.next_health, self.last_health = HOUR, 0
        self.gaps, self.peak, self.read = [], 0.0, []   # the scene's own reads, for the margins

    # ------------------------------------------------------------ the world
    def spawn(self, kind, faction, x, z):
        self.n += 1
        p = Pawn("%s%d" % ("Human" if kind == "Colonist" else kind, 90000 + self.n), kind, faction, x, z, self.tick)
        if kind == "Colonist":
            p.weapon = self.weapons[self.ncol % len(self.weapons)]
            self.ncol += 1
        else:
            p.hp = self.biter_hp if kind == "RM_Flamefang" else 15.0
            p.next_attack = self.tick + self.phase
        self.pawns[p.id] = p
        return p

    def colonists(self):
        return [p for p in self.pawns.values() if p.alive and p.faction == "player"]

    def biters(self):
        return [p for p in self.pawns.values() if p.alive and p.manhunter]

    def die(self, p, cause):
        p.alive = False
        if p.faction == "player":
            self.deaths.append((p.id, cause, self.tick))

    def hit_biter(self, b, dmg):
        b.hp -= dmg
        if b.hp <= 0:
            self.die(b, "killed")

    def food_step(self):
        dt = self.tick - self.last_food
        self.last_food = self.tick
        for p in self.colonists():
            left = float(dt)
            while left > 0 and p.food > 0:
                mult, floor = (1.0, FOOD_HUNGRY) if p.food > FOOD_HUNGRY else \
                    ((0.5, FOOD_URGENT) if p.food > FOOD_URGENT else (0.25, 0.0))
                r = FOOD_FALL * self.hunger * mult
                need = (p.food - floor) / r
                if need > left:
                    p.food -= r * left
                    left = 0
                else:
                    p.food, left = floor, left - need
            self.low = min(self.low, p.food)
            if p.food <= 0 and p.id not in [s_[0] for s_ in self.starved]:
                self.starved.append((p.id, self.tick))

    def flee_tick(self):
        bs = self.biters()
        for c in self.colonists():
            if c.drafted:
                c.flee = None
                continue
            if c.flee is None and bs:
                b = min(bs, key=lambda q: max(abs(q.x - c.x), abs(q.z - c.z)))
                near = max(abs(b.x - c.x), abs(b.z - c.z)) <= FLEE_SEES
                aimed = min(self.colonists(), key=lambda q: max(abs(q.x - b.x), abs(q.z - b.z))) is c
                if near or aimed:
                    dx = (c.x > b.x) - (c.x < b.x) or 0
                    dz = (c.z > b.z) - (c.z < b.z) or (-1 if dx == 0 else 0)
                    c.flee = (min(MAP - 1, max(0, c.x + FLEE_CELLS * dx)), min(MAP - 1, max(0, c.z + FLEE_CELLS * dz)))
            if c.flee and (self.tick - c.born) % FLEE_TICKS_PER_CELL == 0:
                c.x += (c.flee[0] > c.x) - (c.flee[0] < c.x)
                c.z += (c.flee[1] > c.z) - (c.flee[1] < c.z)

    def combat_tick(self):
        self.flee_tick()
        for b in self.biters():
            cols = self.colonists()
            if not cols:
                return
            v = min(cols, key=lambda c: max(abs(c.x - b.x), abs(c.z - b.z)))
            dist = max(abs(v.x - b.x), abs(v.z - b.z))
            if dist > 1:
                if (self.tick - b.born) % 15 == 0:
                    b.x += (v.x > b.x) - (v.x < b.x)
                    b.z += (v.z > b.z) - (v.z < b.z)
                if v.drafted and v.fire_at_will and v.weapon == "gun" and dist <= 20 and self.tick % 60 == 0:
                    self.hit_biter(b, 9.0)
                continue
            if self.tick >= b.next_attack:
                b.next_attack = self.tick + COOLDOWN
                fangs = self.rng.random() < 0.8
                if self.rng.random() < 0.7:
                    if fangs:
                        v.hediffs.append({"def": "Bite", "severity": 10.0, "part": "Torso", "tended": False})
                        if self.venom and b.kind == "RM_Flamefang":
                            self.add_venom(v, vd.dose(VD) * self.rng.choice(self.doses))
                        self.bites[v.id] = self.bites.get(v.id, 0) + 1
                    else:
                        v.hediffs.append({"def": "Bruise", "severity": 1.0, "part": "Head", "tended": False})
            if v.drafted:   # melee back, any weapon, fire-at-will or not
                if v.next_melee is None or v.next_melee < b.born:
                    v.next_melee = self.tick + 20
                if self.tick >= v.next_melee:
                    v.next_melee = self.tick + 120
                    if self.rng.random() < 0.8:
                        self.hit_biter(b, {"none": 4.0, "melee": 13.0, "gun": 7.0}[v.weapon])
            if not b.alive:
                continue

    def add_venom(self, v, s):
        for h in v.hediffs:
            if h["def"] == VENOM:
                h["severity"] += s
                return
        v.hediffs.append({"def": VENOM, "severity": s, "part": None, "tended": False})

    def health_step(self):
        dt = (self.tick - self.last_health) / float(DAY)
        self.last_health = self.tick
        if dt <= 0:
            return
        for p in self.colonists():
            tended = p.tended_until > self.tick
            for h in list(p.hediffs):
                if h["def"] != VENOM:
                    continue
                immune = p.immunity >= 1.0
                d = (VD["rise"] if not immune else (VD["fall"] if self.immune_falls else 0.0)) * dt
                if tended and self.tend:
                    d += VD["tended"] * p.tend_q * dt
                if not immune:
                    p.immunity = min(1.0, p.immunity + VD["immunity"] * dt)
                h["severity"] += d
                self.peak = max(self.peak, h["severity"])
                if h["severity"] <= 0:
                    p.hediffs.remove(h)
                elif h["severity"] >= VD["lethal"]:
                    self.die(p, VENOM)
            open_bites = len([h for h in p.hediffs if h["def"] == "Bite" and not h["tended"]])
            if open_bites and self.bleed:
                bl = [h for h in p.hediffs if h["def"] == "BloodLoss"]
                if not bl:
                    bl = [{"def": "BloodLoss", "severity": 0.0, "part": None, "tended": False}]
                    p.hediffs.append(bl[0])
                bl[0]["severity"] += self.bleed * open_bites * dt
                if bl[0]["severity"] >= 1.0 and p.alive:
                    self.die(p, "BloodLoss")

    def advance(self, n):
        end = self.tick + n
        while self.tick < end:
            if self.biters():
                self.tick += 1
                self.combat_tick()
            else:
                self.tick = min(end, self.next_health)
                for c in self.colonists():        # a flight in progress ends at its cell (no biter left to flee)
                    if c.flee and not c.drafted:
                        c.x, c.z = c.flee
            self.food_step()
            if self.tick >= self.next_health:
                self.next_health += HOUR
                self.health_step()
        self.health_step()      # the partial hour: a later bite starts its venom later

    # ------------------------------------------------------------ the bridge
    def row(self, p, health):
        r = {"id": p.id, "kind": p.kind, "dead": False, "downed": False, "x": p.x, "z": p.z,
             "isPlayer": p.faction == "player"}
        if health:
            r["health"] = {"hediffs": [{"def": h["def"], "severity": h["severity"], "part": h["part"]}
                                       for h in p.hediffs]}
        return r

    def call(self, tool, **kw):
        SENT.setdefault(tool, set()).update(kw)
        if tool == "jawa/spawn_pawn":
            p = self.spawn(kw["kindDef"], "player" if kw.get("faction") == "player" else None, kw["x"], kw["z"])
            return {"success": True, "pawns": [{"id": p.id}]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [self.row(p, kw.get("includeHealth")) for p in self.pawns.values()
                                               if p.alive and (kw.get("faction") != "player" or p.faction == "player")]}
        p = self.pawns.get(kw.get("pawnId") or kw.get("pawn") or kw.get("thingId") or kw.get("targetAId"))
        if tool == "jawa/pawn_need":
            if kw.get("action") == "list":
                return {"success": True, "needs": [{"need": "Food", "level": p.food}]}
            if kw.get("action") == "need" and kw.get("need") == "Food":
                p.food = float(kw["level"])
                return {"success": True}
            return {"success": False}
        if tool == "jawa/set_draft":
            p.drafted = bool(kw.get("drafted"))
            if kw.get("fireAtWill") is not None:
                p.fire_at_will = bool(kw["fireAtWill"])
            return {"success": True, "drafted": p.drafted, "fireAtWill": p.fire_at_will}
        if tool == "jawa/pawn_mental":
            p.manhunter = True
            return {"success": True}
        if tool == "jawa/damage":
            if p is None or not p.alive:
                return {"success": False}
            if self.rng.choice(PARTS) in VITAL:
                self.die(p, "killed")
            return {"success": True}
        if tool == "jawa/kill_hostiles":
            killed = [b for b in self.biters() if b.kind == kw.get("pawnDef")]
            for b in killed:
                self.die(b, "killed")
            return {"success": True, "killed": len(killed), "killedPawns": [{"id": b.id} for b in killed]}
        if tool == "jawa/pawn_health" and kw.get("action") == "remove":
            for h in p.hediffs:
                if h["def"] == kw.get("hediff"):
                    p.hediffs.remove(h)
                    return {"success": True}
            return {"success": False}
        if tool == "jawa/ordered_job":
            target = self.pawns[kw["targetAId"]]
            target.tended_until, target.tend_q = self.tick + 12 * HOUR, 0.7
            for h in target.hediffs:
                h["tended"] = True
            # the doctor's TendPatient job runs a few hundred ticks (walk and tend), as the live game reads it through
            # jawa/site_state (Pyrelands visit 4: the row starts its hourly series once that job has ended)
            self.tend_job = (kw.get("pawnId"), self.tick + 400)
            return {"success": True}
        if tool == "jawa/site_state":
            doc, end = getattr(self, "tend_job", (None, -1))
            return {"success": True, "pawns": [{"id": q.id, "job": "TendPatient" if (q.id == doc and self.tick < end)
                                                else None} for q in self.pawns.values() if q.alive]}
        return {"success": True}


def run_scene(V, game):
    """Both venom scene functions against `game`, the harness stubbed -> {part: verdict}."""
    res = {}

    class Session(object):
        def track(self, *a, **k):
            pass

        def call(self, tool, **kw):
            return game.call(tool, **kw)

    class T(object):
        upstream_failed = False
        session = Session()

        def _declare_fixture(self, pid, name=None):   # the suite's: the safe_advance stop rule's own-pawn list
            if hasattr(game, "declared"):
                game.declared.add(pid)

        def bridge_call(self, tool, **kw):
            return game.call(tool, **kw)

        def _record(self, *a):
            pass

    @contextlib.contextmanager
    def comp(t, name, **kw):
        pre = V._vitals(t)                       # the real _comp's row-start top-up
        if pre is not None and name not in V.NEEDS_ROWS:
            V._top_up(t, pre)
        try:
            yield t
            res[name] = "PASS"
        except V._Unmeasured:
            res[name] = "UNMEASURED"
        except V.ExpectationFailed:
            res[name] = "FAIL"
        t.upstream_failed = False

    def wait(t, n, fast=None, stop_on=None):
        dead, starved = len(game.deaths), len(game.starved)
        game.advance(n)
        stops = (stop_on or V.BITE_STOP_ON).split(",")
        if len(game.deaths) > dead and "death" in stops:   # the governor's death stop
            V._unmeasured(t, "RESTART (damage to the test, not a verdict): %s died" % (game.deaths[-1],))
        if len(game.starved) > starved and "starving" in stops:   # the governor's starving stop
            V._unmeasured(t, "governor stop: starving: %s" % (game.starved[-1],))

    def note(t, label, data):
        ser = (data or {}).get("series") if isinstance(data, dict) else None
        if isinstance(ser, dict) and "tended" in ser:
            te, un = ser["tended"], ser["untended"]
            if te and un and None not in te + un:
                game.gaps.extend((un[i] - un[i - 1]) - (te[i] - te[i - 1]) for i in range(1, len(te)))

    stubs = {"_comp": comp, "_independent": lambda t: None, "_on_site": lambda t: None, "_pad": lambda t, xz: None,
             "_wait": wait, "_bite_wait": wait, "_note": note}
    saved = dict((k, getattr(V, k)) for k in stubs if hasattr(V, k))
    try:
        for k, v in stubs.items():
            setattr(V, k, v)
        V.flamefang_venom(T())
    finally:
        for k, v in saved.items():
            setattr(V, k, v)
    return res


GRID = dict(weapons=(("none",), ("melee",), ("gun",), ("melee", "gun"), ("gun", "melee", "none")),
            phase=(0, 45, 98), seed=(1, 2, 3, 4), bleed=(0.0, 0.15), biter_hp=(20.0, 60.0),
            doses=((1.0,), (0.5, 0.8, 1.0)), hunger=(1.0, 2.25))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation", default=os.path.join(HERE, "validation.py"))
    ap.add_argument("--schemas", default=os.path.join(HERE, "..", "Utils", "northstar_driver", "tool_schemas.json"))
    ap.add_argument("--defs", default=vd.DEFS, help="the Defs folder the venom numbers come from")
    a = ap.parse_args()
    global VD
    VD = vd.read(a.defs)
    V = load_validation(a.validation)
    keys = sorted(GRID)
    cases = [dict(zip(keys, vals)) for vals in itertools.product(*(GRID[k] for k in keys))]
    bad_rows, deaths, multi, gaps, peaks, starved, lows = [], [], [], [], [], [], []
    undeclared = []
    for kw in cases:
        g = Game(**kw)
        g.declared, g.spawned_biters = set(), []
        _call = g.call

        def spy(tool, _call=_call, g=g, **k):
            r = _call(tool, **k)
            if tool == "jawa/spawn_pawn" and k.get("kindDef") in ("RM_Flamefang", "Fox_Fennec"):
                g.spawned_biters.extend(p.get("id") for p in (r or {}).get("pawns") or [])
            return r
        g.call = spy
        try:
            got = run_scene(V, g)
        except Exception as e:     # a scene that cannot run is a FAIL here, never a crash with no verdict
            got = {"raised": "%s: %s" % (type(e).__name__, e)}
        if any(got.get(r) != "PASS" for r in ROWS + FIRST):
            bad_rows.append((kw, got))
        if [b for b in g.spawned_biters if b not in g.declared]:
            undeclared.append((kw, [b for b in g.spawned_biters if b not in g.declared]))
        if g.deaths:
            deaths.append((kw, g.deaths))
        if g.starved:
            starved.append((kw, g.starved))
        lows.append(g.low)
        gaps.extend(g.gaps)
        peaks.append(g.peak)
        stacked = dict((k, n) for k, n in g.bites.items() if n > 1)
        if stacked:
            multi.append((kw, stacked))
    n = len(cases)
    print("margin: smallest untended-minus-tended venom rise in one hour after the tend: %.4f "
          "(limit > 0; %d hours read)"
          % (min(gaps) if gaps else float("nan"), len(gaps)))
    print("margin: highest venom severity any patient reached: %.3f (lethalSeverity %.3g; %d cases). One bite: %.3f + "
          "%.3g/day x %.2f days to immunity = %.3f, by the shipped defs (power %.4g from %s)"
          % (max(peaks), VD["lethal"], n, vd.dose(VD), VD["rise"], vd.days_to_immune(VD), vd.peak(VD, vd.dose(VD)),
             VD["power"], VD["sources"]["power"]))
    # HARNESS (visit 6, 2026-11-22, ArchSmall): the wait-out's own biter, spawned wild and undeclared, stopped the advance as
    # a 'hostile_arrival' (declared False) 60 ticks in; every biter the scene spawns is the test's own fixture
    check("real build: every biter the scene spawns is declared a fixture (%d cases; %d with an undeclared biter)"
          % (n, len(undeclared)), not undeclared, undeclared[:2])
    check("real build: every venom row PASS over the grid (%d cases read; %d not PASS)" % (n, len(bad_rows)),
          not bad_rows, "first: %r" % (bad_rows[:2],))
    check("real build: no colonist dies over the grid (%d cases; %d with a death)" % (n, len(deaths)), not deaths,
          "first: %r" % (deaths[:2],))
    check("real build: no patient takes a second venom bite (%d cases; %d with stacked bites)" % (n, len(multi)),
          not multi, "first: %r" % (multi[:2],))
    print("margin: lowest Food any colonist reached: %.3f (limit > 0, Starving; %d cases)" % (min(lows), n))
    check("real build: no colonist reaches Starving over the grid (%d cases; %d with a starving colonist)"
          % (n, len(starved)), not starved, "first: %r" % (starved[:2],))
    # planted mod faults: the repaired scene must read them, never PASS them
    base = dict(weapons=("melee", "gun"), phase=45, seed=2, bleed=0.15, biter_hp=20.0, doses=(0.5, 0.8, 1.0))
    for what, fault, part in (("the bite carries no venom", dict(venom=False), "flamefang_bite_injects_venom"),
                              ("a tend does nothing", dict(tend=False), "venom_tended_vs_untended"),
                              ("immunity never lowers the venom", dict(immune_falls=False), "venom_wait_out")):
        got = run_scene(V, Game(**dict(base, **fault)))
        check("planted: %s -> %s FAIL" % (what, part), got.get(part) == "FAIL", got)
    env = getattr(V, "PLANT_VENOM_TEND_WRONG_ENV", "PYRE_PLANT_VENOM_TEND_WRONG_PATIENT")
    for case in (base, dict(base, weapons=("none",), phase=0, seed=1), dict(base, hunger=2.25, biter_hp=60.0, seed=3)):
        os.environ[env] = "1"
        try:
            got = run_scene(V, Game(**case))
        finally:
            os.environ.pop(env, None)
        check("planted: %s=1 (the doctor tends the wrong patient) -> venom_tended_vs_untended FAIL, never UNMEASURED "
              "(weapons %r, seed %d, hunger %.2f)" % (env, case["weapons"], case["seed"], case.get("hunger", 1.0)),
              got.get("venom_tended_vs_untended") == "FAIL", got)
    # the feeding cadence against vanilla's hunger (pure)
    tts = getattr(V, "ticks_to_starving", None)
    check("ticks_to_starving exists", tts is not None)
    if tts is not None:
        full = (1.0 - FOOD_HUNGRY) / FOOD_FALL + (FOOD_HUNGRY - FOOD_URGENT) / (FOOD_FALL * 0.5) + FOOD_URGENT / (FOOD_FALL * 0.25)
        check("ticks_to_starving(1.0) = %.0f by vanilla's three rates (read %.0f)" % (full, tts(1.0)), abs(tts(1.0) - full) < 1)
        check("ticks_to_starving(1.0) < one day: a once-a-day top-up cannot carry a drafted pawn (%.0f < %d)"
              % (tts(1.0), DAY), tts(1.0) < DAY)
        g = Game(hunger=2.25)
        q = g.spawn("Colonist", "player", 0, 0)
        q.food = 0.8
        g.advance(int(tts(0.8, 2.25)) - 2)
        alive_fed = q.food > 0
        g.advance(4)
        check("the scripted game's hunger agrees with ticks_to_starving (0.8 at x2.25: %.0f ticks)" % tts(0.8, 2.25),
              alive_fed and q.food <= 0, "food %.4f" % q.food)
        fe = getattr(V, "FEED_EVERY", None)
        check("FEED_EVERY %r < ticks_to_starving(0.8, 3.0) = %.0f (a spawned pawn fed late, factor 3)"
              % (fe, tts(0.8, 3.0)), isinstance(fe, int) and 0 < fe < tts(0.8, 3.0))
    bes = getattr(V, "_beside", None)
    check("_beside exists", bes is not None)
    if bes is not None:
        for what, row, want in (("a live position", {"x": 30, "z": 40}, (31, 40)), ("no position", {}, (11, 20)),
                                ("an unplaced pawn (-1)", {"x": -1, "z": -1}, (11, 20)), ("no row", None, (11, 20))):
            check("_beside: %s -> %r" % (what, want), bes(row, 10, 20) == want, bes(row, 10, 20))
    tools = json.load(open(a.schemas))["tools"]
    for tool, args in sorted(SENT.items()):
        have = set((tools.get(tool) or {}).get("parameters") or [])
        check("tools: %s declared with %s" % (tool, ", ".join(sorted(args))), tool in tools and args <= have,
              "absent" if tool not in tools else "undeclared %s" % sorted(args - have))
    f = getattr(V, "tended_rises_less", None)
    check("tended_rises_less exists", f is not None)
    if f is not None:
        for what, te, un, want in (
                ("a working tend on equal doses", [0.2, 0.203, 0.206], [0.2, 0.215, 0.229], True),
                ("a working tend, the tended dose larger", [0.24, 0.243, 0.246], [0.12, 0.135, 0.149], True),
                ("a tend that does nothing, the tended dose smaller", [0.1, 0.115, 0.129], [0.2, 0.215, 0.229], False),
                ("a tend that works an hour then stops", [0.2, 0.203, 0.218], [0.2, 0.215, 0.229], False),
                ("the tended rising faster at the last read", [0.2, 0.203, 0.235], [0.2, 0.215, 0.229], False),
                ("one read only", [0.2], [0.2], False)):
            ok, why = f(te, un)
            check("tended_rises_less: %s -> %s" % (what, want), ok is want, why)
    # HARNESS (visit 6, 2026-11-22): a bite row with no bite left venom_rises_untreated reading [None] * 7, and it FAILed the
    # mod; with no venom read at all the rises row is UNMEASURED (venom_never_read), a bite with no venom is the bite row's FAIL
    nr = getattr(V, "venom_never_read", None)
    check("venom_never_read exists", nr is not None)
    if nr is not None:
        for what, series, want in (("seven unreadable hours (no bite)", [None] * 7, True), ("no reading", [], True),
                                   ("venom read once", [None, 0.17, None], False), ("venom rising", [0.17, 0.19, 0.21], False),
                                   ("venom read as 0.0", [0.0, None], False)):
            check("venom_never_read: %s -> %s" % (what, want), nr(series) is want, repr(series))
    bad = RESULTS.count(False)
    print("%s: %d of %d checks failed" % (NAME, bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
