#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_repair.py - the mechanical defects four independent reviews found, 2026-08-22.

Each block below cites the finding it closes. Run with --apply; every block reports the
number it changed, and a block that finds nothing to do says so rather than staying silent.

  1 ROAD DUPLICATES      8 tile pairs declared as BOTH StoneRoad and DirtRoad, plus 13
                         exact repeat rows. One corridor was re-laid at a different grade
                         and the old rows were never removed. StoneRoad wins: a graded
                         road is an upgrade, and the dirt row is the stale one.
  2 THE SETDOWN          The `AbandonedColonyOutlander` landmark sits ON tile 2476, the
                         campaign start tile. ASHKARR_WORLD_DEFINITION.md is explicit that
                         it goes ADJACENT, never on 2476, because the gravship needs 4,057
                         clear cells there. Moved to a neighbour.
  3 HUTT WELLS           "Every Hutt settlement is on an oasis" - FACTION_SPEC. Eight of
                         the nineteen sat on bare ExtremeDesert. A toll-well faction with
                         no well is nothing, so each gets one dug beside it.
  4 ORPHAN FLOW          Tiles carrying river_flow with no river link. Where a river tile
                         is adjacent the link is drawn; where the tile is isolated the
                         flow is zeroed, because accumulation with no channel is a number
                         that contradicts its own map.
  5 GREY SEA             Every design doc and Tidewatch's own why-line say "Grey Sea";
                         the map region said "The Gray Sea". The docs are the older and
                         more numerous usage, so the map moves.

⛔ NOT REPAIRED HERE, DELIBERATELY: the review flagged the Scald sitting at -30 m as
contradicting the doctrine's perched-crater image. The MAP is right and the DOC is stale -
the owner ratified dropping it (SCALD_WATER_RULING_1, applied in bd5dad0, verified: 312
tiles at -30 m, water 8.14% matching canon). That correction belongs in the doc, and is
made there, not by re-lifting a sea the owner sank.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")
START_TILE = 2476


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    trows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {int(r["tile"]): r for r in trows}
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    header, body = links[0], links[1:]
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in re.split(r"[;|,]", r["mutators"]) if x.strip()]
          for r in mrows}

    # ── 1. road duplicates ────────────────────────────────────────────────────
    keep, seen_pair, dropped_dup, dropped_grade = [], {}, 0, 0
    for row in body:
        kind, p, q, d = row
        key = (kind, frozenset((int(p), int(q))))
        if key not in seen_pair:
            seen_pair[key] = len(keep)
            keep.append(row)
            continue
        prev = keep[seen_pair[key]]
        if prev[3] == d:
            dropped_dup += 1                      # exact repeat
        elif kind == "road":
            # StoneRoad beats DirtRoad; the dirt row is the one left behind
            if d == "StoneRoad" and prev[3] == "DirtRoad":
                keep[seen_pair[key]] = row
            dropped_grade += 1
        else:
            dropped_dup += 1
    body = keep
    print("1 ROAD DUPLICATES  dropped %d exact repeats and %d contradictory grades"
          % (dropped_dup, dropped_grade))

    # ── 2. the Setdown off the start tile ─────────────────────────────────────
    moved = 0
    lm_tiles = {int(r["tile"]) for r in lrows}
    s_tiles = {int(r["tile"]) for r in srows}
    for r in lrows:
        if int(r["tile"]) == START_TILE and r["landmark"] == "AbandonedColonyOutlander":
            dest = next((n for n in nb[START_TILE]
                         if n not in lm_tiles and n not in s_tiles
                         and T[n]["water"] == "0" and int(T[n]["hilliness"]) < 5), None)
            if dest is None:
                sys.exit("REFUSED: no free neighbour of the start tile for the Setdown")
            MU[dest] = MU.get(dest, []) + [m for m in MU.get(START_TILE, [])
                                           if m == "AbandonedColonyOutlander"]
            MU[START_TILE] = [m for m in MU.get(START_TILE, [])
                              if m != "AbandonedColonyOutlander"]
            if "AbandonedColonyOutlander" not in MU[dest]:
                MU[dest].append("AbandonedColonyOutlander")
            r["tile"] = str(dest)
            r["why"] = ("The Setdown - where the dead gravship was found. ADJACENT to the "
                        "start tile, never on it: the ship needs 4,057 clear cells there")
            lm_tiles.discard(START_TILE)
            lm_tiles.add(dest)
            moved += 1
    print("2 THE SETDOWN      moved off the start tile: %d" % moved)

    # ── 3. Hutt wells ─────────────────────────────────────────────────────────
    oasis = {int(r["tile"]) for r in lrows if r["landmark"] == "Oasis"}
    dug = 0
    for s in srows:
        if s["faction"] != "Hutt Cartel":
            continue
        t = int(s["tile"])
        if t in oasis or any(n in oasis for n in nb[t]):
            continue
        dest = next((n for n in nb[t]
                     if n not in lm_tiles and n not in s_tiles
                     and T[n]["water"] == "0" and int(T[n]["hilliness"]) <= 3), None)
        if dest is None:
            print("   ! %s has no free neighbour for a well" % s["name"])
            continue
        lrows.append({"tile": str(dest), "landmark": "Oasis",
                      "why": "a Hutt well - the holding beside it exists because of this water"})
        MU.setdefault(dest, [])
        if "Oasis" not in MU[dest]:
            MU[dest].append("Oasis")
        lm_tiles.add(dest)
        oasis.add(dest)
        dug += 1
    print("3 HUTT WELLS       dug for holdings that had none: %d" % dug)

    # ── 4. orphan river flow ──────────────────────────────────────────────────
    river_tiles = {int(x) for k, p, q, d in body if k == "river" for x in (p, q)}
    linked = zeroed = 0
    for r in trows:
        t = int(r["tile"])
        if float(r["river_flow"]) <= 0 or t in river_tiles:
            continue
        touch = [n for n in nb[t] if n in river_tiles]
        if touch:
            # join it to the lowest river neighbour, mouth-first (a = downstream)
            down = min(touch, key=lambda n: float(T[n]["elev_m"]))
            lo, hi = (down, t) if float(T[down]["elev_m"]) <= float(r["elev_m"]) else (t, down)
            body.append(["river", str(lo), str(hi), "Creek"])
            river_tiles.add(t)
            linked += 1
        else:
            r["river_flow"] = "0.0"
            zeroed += 1
    print("4 ORPHAN FLOW      %d joined to an adjacent river, %d isolated flows zeroed"
          % (linked, zeroed))

    # ── 5. Grey Sea ───────────────────────────────────────────────────────────
    renamed = 0
    for r in trows:
        if r["region"] == "The Gray Sea":
            r["region"] = "Grey Sea"
            renamed += 1
    print("5 GREY SEA         tiles respelled to match every doc: %d" % renamed)

    if not a.apply:
        print("\nplan only - re-run with --apply")
        return

    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader()
        w.writerows(trows)
    with open(STEM + "_landmarks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tile", "landmark", "why"])
        w.writeheader()
        w.writerows(lrows)
    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    print("\nwritten: tiles, links, landmarks, mutators")


if __name__ == "__main__":
    main()
