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
(RM_Flamefang's 1.65 s cooldown), venom-fangs or head (seeded), 70 % to hit; a venom bite is a Bite wound plus 0.2
RM_FlamefangVenom (severityPerDamageDealt 0.02 x power 10), merged into the hediff. A drafted victim melees an adjacent
hostile whatever its fire-at-will (JobDriver_Wait.CheckForAutoAttack) and shoots one at range only with fire-at-will on
and a gun. `jawa/damage Cut 500` with no part destroys one seeded random part and kills only on a vital one;
`jawa/kill_hostiles` kills for certain. Health, continuous between reads: the def's numbers (severityPerDayNotImmune 0.35,
immunityPerDaySick 0.5, severityPerDayImmune -0.6, severityPerDayTended -0.4 x quality for 12 h, lethal 1), and each
untended Bite wound bleeds `bleed` BloodLoss per day, lethal at 1. A death inside the clock stops the row as the governor
does (RESTART, UNMEASURED).

The range it declares (the grid): the colonists' weapons in spawn order (none, melee, gun, and mixes), the biter's attack
phase against the poll (0, 45, 98 ticks), the seed (tool choice, hits, the Cut's part), the bleed rate (0, 0.15/day), the
biter's health (20, 60: a fast or a slow kill by the victim), and the bite's dose (flat 0.2, or armour and part caps
scaling it by 0.5, 0.8 or 1.0, seeded). Planted mod faults: the bite carries no venom; a tend does
nothing; immunity never lowers the venom. Left out: the live pathing, real armour and part coverage, real bleed rates and
blood regrowth, the doctor's walk and medicine (Stage 6 runs the scene; its command is in unrun.jsonl).

  python3 <this file> [--validation PATH] [--schemas PATH]     exit 0 = every check PASS, 1 = any FAIL
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

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "selftest_pyrelands_venom_staging"
VENOM = "RM_FlamefangVenom"
DAY, HOUR = 60000, 2500
COOLDOWN = 99                       # RM_Flamefang venom-fangs and head: cooldownTime 1.65 s
VITAL = ("Torso", "Head", "Neck")
PARTS = ("Torso", "Head", "Neck", "Tail", "Jaw", "Eye", "Tongue")
ROWS = ("venom_tended_vs_untended", "venom_wait_out")
FIRST = ("flamefang_bite_injects_venom", "venom_rises_untreated", "plain_bite_carries_no_venom")
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

    def sev(self, d):
        return sum(h["severity"] for h in self.hediffs if h["def"] == d)


class Game(object):
    def __init__(self, weapons=("melee",), phase=0, seed=1, bleed=0.0, biter_hp=20.0, doses=(1.0,), venom=True,
                 tend=True, immune_falls=True):
        self.weapons, self.phase, self.rng, self.bleed, self.biter_hp = weapons, phase, random.Random(seed), bleed, biter_hp
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

    def combat_tick(self):
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
                            self.add_venom(v, 0.2 * self.rng.choice(self.doses))
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
                d = (0.35 if not immune else (-0.6 if self.immune_falls else 0.0)) * dt
                if tended and self.tend:
                    d += -0.4 * p.tend_q * dt
                if not immune:
                    p.immunity = min(1.0, p.immunity + 0.5 * dt)
                h["severity"] += d
                self.peak = max(self.peak, h["severity"])
                if h["severity"] <= 0:
                    p.hediffs.remove(h)
                elif h["severity"] >= 1.0:
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
            if self.tick >= self.next_health:
                self.next_health += HOUR
                self.health_step()
        self.health_step()      # the partial hour: a later bite starts its venom later

    # ------------------------------------------------------------ the bridge
    def row(self, p, health):
        r = {"id": p.id, "kind": p.kind, "dead": False}
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
                                               if p.alive]}
        p = self.pawns.get(kw.get("pawnId") or kw.get("pawn") or kw.get("thingId") or kw.get("targetAId"))
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
            return {"success": True}
        return {"success": True}


def run_scene(V, game):
    """Both venom scene functions against `game`, the harness stubbed -> {part: verdict}."""
    res = {}

    class Session(object):
        def track(self, *a, **k):
            pass

    class T(object):
        upstream_failed = False
        session = Session()

        def bridge_call(self, tool, **kw):
            return game.call(tool, **kw)

        def _record(self, *a):
            pass

    @contextlib.contextmanager
    def comp(t, name, **kw):
        try:
            yield t
            res[name] = "PASS"
        except V._Unmeasured:
            res[name] = "UNMEASURED"
        except V.ExpectationFailed:
            res[name] = "FAIL"
        t.upstream_failed = False

    def wait(t, n, fast=None, stop_on=None):
        dead = len(game.deaths)
        game.advance(n)
        if len(game.deaths) > dead and (stop_on is None or "death" in stop_on.split(",")):   # the governor's death stop
            V._unmeasured(t, "RESTART (damage to the test, not a verdict): %s died" % (game.deaths[-1],))

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
            doses=((1.0,), (0.5, 0.8, 1.0)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation", default=os.path.join(HERE, "validation.py"))
    ap.add_argument("--schemas", default=os.path.join(HERE, "..", "Utils", "northstar_driver", "tool_schemas.json"))
    a = ap.parse_args()
    V = load_validation(a.validation)
    keys = sorted(GRID)
    cases = [dict(zip(keys, vals)) for vals in itertools.product(*(GRID[k] for k in keys))]
    bad_rows, deaths, multi, gaps, peaks = [], [], [], [], []
    for kw in cases:
        g = Game(**kw)
        try:
            got = run_scene(V, g)
        except Exception as e:     # a scene that cannot run is a FAIL here, never a crash with no verdict
            got = {"raised": "%s: %s" % (type(e).__name__, e)}
        if any(got.get(r) != "PASS" for r in ROWS + FIRST):
            bad_rows.append((kw, got))
        if g.deaths:
            deaths.append((kw, g.deaths))
        gaps.extend(g.gaps)
        peaks.append(g.peak)
        stacked = dict((k, n) for k, n in g.bites.items() if n > 1)
        if stacked:
            multi.append((kw, stacked))
    n = len(cases)
    print("margin: smallest untended-minus-tended venom rise in one hour after the tend: %.4f "
          "(limit > 0; %d hours read)"
          % (min(gaps) if gaps else float("nan"), len(gaps)))
    print("margin: highest venom severity any patient reached: %.3f (lethalSeverity 1; %d cases). One bite: 0.2 + 0.35/day "
          "x 2 days to immunity = 0.9, by the def's own numbers" % (max(peaks), n))
    check("real build: every venom row PASS over the grid (%d cases read; %d not PASS)" % (n, len(bad_rows)),
          not bad_rows, "first: %r" % (bad_rows[:2],))
    check("real build: no colonist dies over the grid (%d cases; %d with a death)" % (n, len(deaths)), not deaths,
          "first: %r" % (deaths[:2],))
    check("real build: no patient takes a second venom bite (%d cases; %d with stacked bites)" % (n, len(multi)),
          not multi, "first: %r" % (multi[:2],))
    # planted mod faults: the repaired scene must read them, never PASS them
    base = dict(weapons=("melee", "gun"), phase=45, seed=2, bleed=0.15, biter_hp=20.0, doses=(0.5, 0.8, 1.0))
    for what, fault, part in (("the bite carries no venom", dict(venom=False), "flamefang_bite_injects_venom"),
                              ("a tend does nothing", dict(tend=False), "venom_tended_vs_untended"),
                              ("immunity never lowers the venom", dict(immune_falls=False), "venom_wait_out")):
        got = run_scene(V, Game(**dict(base, **fault)))
        check("planted: %s -> %s FAIL" % (what, part), got.get(part) == "FAIL", got)
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
    bad = RESULTS.count(False)
    print("%s: %d of %d checks failed" % (NAME, bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
