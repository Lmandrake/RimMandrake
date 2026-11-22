#!/usr/bin/env python3
"""Offline selftest for the sc_firefoam_sprayer scene (RIMMANDRAKE_SEAL_PYRE_SPRAYER_RING_BOTH_COLONISTS_WAIT_IT_OUT).

Pyrelands visit 5 (2026-11-22, ArchBig): one map_fire per ring edge lit 41 to 54 of the 72 ring cells, every harvester
stood on an unlit cell beside the fruit, and the sprayer row read PASS on a fruit taken at tick 2000 with 0 fires left.
FireUtility.TryStartFireIn has no random roll (a refused cell has ChanceToStartFireIn 0), so the repair re-fuels and
relights each cold cell beside the fruit and reads the row UNMEASURED if one stays cold. The sprayer row now needs a
fruit taken while the ring still burns.

What this reads, all SHIPPED code in validation.py:
  1. the geometry (ring_cells, fruit_cells, beside_fruit): every way in to the fruit passes a cell beside it;
  2. ring_staging_verdict over every single cold cell beside the fruit, and the planted west gap;
  3. _stage_burning_fruit driven against a fake bridge that models vanilla ignition (fuel and no foam -> fire, no roll),
     over a generated range of cells: the 9x9 planting misses some cells that a one-cell replant takes ("flaky"), some
     cells take no plant at all ("dead"), firefoam left on cells, the planted gap on and off;
  4. taken_while_burning and harvested_while_burning over a generated grid of timelines (harvest tick x fire-out tick x
     at-fruit x yield seen x yield baseline), against an oracle written here from the bar's words;
  5. the recorded visit-5 timelines as challenge cases (design/concepts/Pyrelands/version/in_game/visit_5/evidence).
Not covered: fire spread, burn odds and pathing (live only; Stage 6 runs the chain), and real planting rejections (the
fake decides which cells take a plant; the live staging names the planting reply of every cell it could not light).
Run: python3 <this file>
"""
import itertools
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validation as V  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EVID = os.path.join(ROOT, "design", "concepts", "Pyrelands", "version", "in_game", "visit_5", "evidence")
X, Z = V.PAD_SPRAY


def _cells(rect):
    x, z, w, h = (int(v) for v in str(rect).split(","))
    return [(x + i, z + j) for i in range(w) for j in range(h)]


class FakeMap(object):
    """A bridge over one pad. Vanilla ignition: a cell lights iff it holds fuel, no fire and no fire-refusing filth."""

    def __init__(self, flaky=(), dead=(), foam=()):
        self.session, self.upstream_failed, self.notes = object(), False, []
        self.flaky, self.dead = set(flaky), set(dead)
        self.foam, self.fuel, self.fire, self.fruit = set(foam), set(), set(), set()

    def _record(self, label, data):
        self.notes.append((label, data))

    def bridge_call(self, tool, **p):
        if tool == "jawa/destroy_batch":
            cells = set(c for r in p["rects"].split(";") for c in _cells(r))
            if "Filth" in p.get("categories", ""):
                self.foam -= cells
            if "Plant" in p.get("categories", ""):
                self.fuel -= cells
                self.fruit -= cells
            return {"success": True}
        if tool == "jawa/set_plants":
            d, r = p["ops"].split(":")
            cells = _cells(r)
            took = [c for c in cells if c not in self.dead and not (len(cells) > 1 and c in self.flaky)]
            if d == V.FRUIT_PLANT:
                self.fruit.update(took)
                self.fuel -= set(took)
            else:
                self.fuel.update(took)
            return {"success": True, "planted": len(took), "rejected": len(cells) - len(took)}
        if tool == "jawa/map_fire" and p.get("action") == "start":
            n = 0
            for c in _cells(p["rect"]):
                if c in self.fuel and c not in self.fire and c not in self.foam:
                    self.fire.add(c)
                    n += 1
            return {"success": True, "firesStarted": n}
        if tool == "jawa/list_things":
            pool = {"Fire": self.fire, V.FRUIT_PLANT: self.fruit, V.FOAM_FILTH: self.foam}.get(p.get("defName"), set())
            hit = sorted(c for c in pool if "rect" not in p or c in set(_cells(p["rect"])))
            rows = [{"id": "%s%d" % (p.get("defName"), i), "x": c[0], "z": c[1]} for i, c in enumerate(hit)]
            return {"success": True, "things": rows[:p.get("limit", 500)], "countMatched": len(hit), "scanned": 9999}
        return {"success": True}


def stage(fake, west_gap):
    """-> (staging record, None) or (None, the UNMEASURED reason)."""
    try:
        return V._stage_burning_fruit(fake, X, Z, west_gap=west_gap)[2], None
    except V._Unmeasured as e:
        return None, str(e)


def geometry(probs):
    ring, fruit, beside = V.ring_cells(X, Z), V.fruit_cells(X, Z), V.beside_fruit(X, Z)
    box = set((X + i, Z + j) for i in range(9) for j in range(9))
    if len(ring) != 72 or ring | fruit != box or ring & fruit:
        probs.append("geometry: ring %d cells, fruit %d; ring and fruit must tile the 9x9" % (len(ring), len(fruit)))
    if len(beside) != 16 or not beside <= ring:
        probs.append("geometry: %d cells beside the fruit, inside the ring %s" % (len(beside), beside <= ring))
    # every 8-way step from outside the beside band into the fruit lands from a beside cell
    for c in box - fruit - beside:
        for dx, dz in itertools.product((-1, 0, 1), repeat=2):
            if (c[0] + dx, c[1] + dz) in fruit:
                probs.append("geometry: %r steps into the fruit without passing a cell beside it" % (c,))
    return 1


def verdicts(probs):
    beside = V.beside_fruit(X, Z)
    west = {(X + 2, Z + 3), (X + 2, Z + 4), (X + 2, Z + 5)}   # the west edge rect (x, z+3, 3, 3) beside the fruit
    n = 0
    ok, why = V.ring_staging_verdict([], X, Z)
    n += 1
    if not ok:
        probs.append("verdict: all beside cells lit read not ok: %s" % why)
    for c in sorted(beside):
        n += 1
        if V.ring_staging_verdict([c], X, Z)[0]:
            probs.append("verdict: cold cell %r beside the fruit read ok" % (c,))
        n += 1
        planted_ok = V.ring_staging_verdict(sorted(west | {c}), X, Z, west_gap=True)[0]
        if planted_ok != (c in west):
            probs.append("verdict: planted gap plus cold %r read %s" % (c, planted_ok))
        if c in west:
            n += 1
            if V.ring_staging_verdict(sorted(west - {c}), X, Z, west_gap=True)[0]:
                probs.append("verdict: planted gap with %r still burning read ok" % (c,))
    return n


def staging(probs):
    """Generated: each kind of trouble on every cell beside the fruit, then 300 random mixes over the ring."""
    beside, ring = sorted(V.beside_fruit(X, Z)), sorted(V.ring_cells(X, Z))
    west = {(X + 2, Z + 3), (X + 2, Z + 4), (X + 2, Z + 5)}   # the west edge rect (x, z+3, 3, 3) beside the fruit
    cases = []
    for c in beside:
        for gap in (False, True):
            cases += [dict(flaky=[c], gap=gap), dict(dead=[c], gap=gap), dict(foam=[c], gap=gap)]
    rnd = random.Random(20261122)
    for _ in range(300):
        pick = lambda k: rnd.sample(ring, rnd.randint(0, k))  # noqa: E731
        cases.append(dict(flaky=pick(24), dead=pick(2) if rnd.random() < 0.5 else [], foam=pick(10),
                          gap=rnd.random() < 0.3))
    n = 0
    for cs in cases:
        dead = set(cs.get("dead") or ())
        # an edge whose every cell refuses makes _fire fail; vanilla would read the same, so keep the edges lightable
        if any(not (set(_cells(V._rs(e))) - dead) for e in V.ring_edges(X, Z)):
            continue
        fake = FakeMap(cs.get("flaky", ()), dead, cs.get("foam", ()))
        rec, unm = stage(fake, cs["gap"])
        n += 1
        if unm:
            probs.append("staging %r: UNMEASURED %s" % (cs, unm))
            continue
        cold_beside = set(c for c in beside if c not in fake.fire)
        want_ok = (cold_beside == west) if cs["gap"] else not (dead & set(beside))
        if bool(rec.get("verdict")) != want_ok:
            probs.append("staging %r: verdict %r (%s), want %r; cold beside %s"
                         % (cs, rec.get("verdict"), rec.get("why"), want_ok, sorted(cold_beside)))
        if not cs["gap"] and want_ok and cold_beside:
            probs.append("staging %r: want ok, but cells beside the fruit stay cold %s" % (cs, sorted(cold_beside)))
        if cs["gap"] and (west & fake.fuel):
            probs.append("staging %r: the planted gap kept fuel at %s" % (cs, sorted(west & fake.fuel)))
        if fake.foam:
            probs.append("staging %r: foam left on the burn %s" % (cs, sorted(fake.foam)))
    return n


def oracle(tl, need_take):
    """The bar's words: the first sample at which a harvest is first seen while the ring holds fire."""
    prev_n, prev_y = 0, tl[0]["yield"]
    for s in tl:
        n, y = len(s["taken"]), s["yield"]
        seen = (n > prev_n and s["atFruit"]) or y > prev_y
        if not need_take:
            seen = s["atFruit"] or y > tl[0]["yield"]
        if s["fires"] > 0 and seen:
            return s["tick"]
        prev_n, prev_y = max(prev_n, n), max(prev_y, y)
    return None


def timelines(probs):
    ticks = list(range(0, 3001, 250))
    n = 0
    for h, out, at, ysee, y0 in itertools.product(ticks[1:] + [None], ticks[1:] + [None], (True, False), (True, False),
                                                  (0, 3)):
        tl = []
        for k in ticks:
            took = h is not None and k >= h
            tl.append({"tick": k, "fires": 0 if (out is not None and k >= out) else 40,
                       "taken": ["F0"] if took else [], "atFruit": at and k > 0,
                       "yield": y0 + (5 if took and ysee else 0)})
        n += 1
        got = (V.taken_while_burning(tl) or {}).get("tick")
        if got != oracle(tl, True):
            probs.append("taken_while_burning h=%s out=%s at=%s yield=%s y0=%s: %r, want %r"
                         % (h, out, at, ysee, y0, got, oracle(tl, True)))
        got = (V.harvested_while_burning(tl) or {}).get("tick")
        if got != oracle(tl, False):
            probs.append("harvested_while_burning h=%s out=%s at=%s: %r, want %r" % (h, out, at, got, oracle(tl, False)))
    return n


def recorded(name, row):
    """A recorded timeline from a visit-5 run log (the note is cut at 1500 chars: whole samples only)."""
    with open(os.path.join(EVID, name), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("[pyre-note] %s run timeline" % row):
                return [json.loads(m) for m in re.findall(r'\{"tick"[^{}]*\}', line)]
    return None


def challenges(probs):
    n = 0
    # visit 5 repaired2: the sprayer colonist's first fruit went at tick 2000 with 0 fires: not a harvest through fire
    for name, row, want in (("run_firefoam_repaired2.log", "sprayer", None),
                            ("run_firefoam_sprayer.log", "sprayer", 2000),
                            ("run_firefoam_repaired.log", "sprayer", 1250)):
        tl = recorded(name, row)
        n += 1
        if not tl:
            probs.append("challenge %s %s: no timeline read" % (name, row))
            continue
        got = (V.taken_while_burning(tl) or {}).get("tick")
        if got != want:
            probs.append("challenge %s %s: taken_while_burning %r, want %r" % (name, row, got, want))
    return n


def main():
    probs, counts = [], {}
    V._wait = lambda t, n, fast=None: None   # the fake map has no clock: the 250-tick settle is a no-op
    for name, fn in (("geometry", geometry), ("verdicts", verdicts), ("staging", staging), ("timelines", timelines),
                     ("challenges", challenges)):
        try:
            counts[name] = fn(probs)
        except Exception as e:  # the parent build has none of these functions: that is the red
            probs.append("%s: %s: %s" % (name, type(e).__name__, e))
    print("selftest_pyrelands_firefoam_scene: %s  cases %s" % ("FAIL" if probs else "PASS", counts))
    for p in probs[:25]:
        print("  - " + p)
    if len(probs) > 25:
        print("  ... %d more" % (len(probs) - 25))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
