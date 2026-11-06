#!/usr/bin/env python3
"""heap_ratchet.py - why did a session's managed heap climb? Reads a TPS record, offline.
Finding it was written for: infrastructure/state/facts/heap_reload_ratchet_2026-11-06.md

`heapMB` (the mem.managed_peak_mb alarm's field) is Mono's USED size: GC.GetTotalMemory, the same number as the context
row's monoUsedMB. It is a sawtooth, so one reading says little: a once-a-minute context row aliases it by hundreds of MB.
The honest series is the post-GC floor: the first heapMB after the `gc` counter rises, lowest per game.

Verdicts:
  reload_ratchet   the floor climbs with the game count and tracks it better than it tracks things on the map
  map_scale        the floor tracks things on the map at least as well as it tracks the game count
  high_water_only  the floor stays level while reserved (monoHeapMB) rises: Mono keeping pages, nothing retained
  flat             neither floor nor reserved moved
  mixed            the floor rose but follows neither series
  UNMEASURED       too few games with a GC in them, or no reserved reading

    python3 src/RimMandrake/Utils/heap_ratchet.py --session ee0fbaa8 [--dir D] [--control 871ad37b --same-save NAME]
                                                  [--require VERDICT] [--json]
Exit: 0 read (and --require matched), 1 --require missed, 2 UNMEASURED or no such session.
"""
import argparse
import glob
import json
import os
import sys

MIN_GAMES = 4           # three points cannot separate two explanations
RISE_MB = 200           # under this a floor change is within one GC's scatter (same-save neighbours differ by ~100)
MIN_R2 = 0.5            # a series explaining under half the floor's variance explains nothing


def default_dir():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from game_paths import LOCALLOW
    return os.path.join(LOCALLOW, "JawaBench", "tps")


def read_rows(directory, session):
    """Every parseable row of the session whose id starts with `session`, in seq order: (full id, rows)."""
    paths = {}
    for p in glob.glob(os.path.join(directory, "tps_*.jsonl")):
        parts = os.path.basename(p).split("_")
        if len(parts) >= 3 and parts[2].startswith(session):
            paths.setdefault(parts[2], []).append(p)
    if len(paths) != 1:
        return None, []
    full, files = next(iter(paths.items()))
    rows = []
    for p in sorted(files):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass                                # a torn last line is normal for a live or killed writer
    rows.sort(key=lambda r: r.get("seq", 0))
    return full, rows


def per_game(rows):
    """[{game, save, floor, firstGc, lastGc, gcs, peak, reserved, things, maps}] in game order. floor is None when no GC
    fell inside the game: a game with no collection has no floor, and its lowest reading would be a guess."""
    games, cur, last_gc = [], None, None
    for r in rows:
        kind = r.get("kind")
        if kind == "game":
            cur = {"game": r.get("game"), "save": r.get("save") or "", "floor": None, "firstGc": None, "lastGc": None,
                   "gcs": 0, "peak": None, "reserved": None, "things": None, "maps": None}
            games.append(cur)
            last_gc = None
        if cur is None:
            continue
        heap = r.get("heapMB")
        if isinstance(heap, (int, float)):
            cur["peak"] = heap if cur["peak"] is None else max(cur["peak"], heap)
            gc = r.get("gc")
            if isinstance(gc, int):
                if last_gc is not None and gc > last_gc:
                    cur["gcs"] += gc - last_gc
                    cur["floor"] = heap if cur["floor"] is None else min(cur["floor"], heap)
                    cur["lastGc"] = heap
                    if cur["firstGc"] is None:
                        cur["firstGc"] = heap
                last_gc = gc
        if kind == "context":
            if isinstance(r.get("monoHeapMB"), (int, float)):
                cur["reserved"] = r["monoHeapMB"]
            maps = r.get("maps") or []
            things = sum(m.get("things", 0) for m in maps)
            cur["things"] = things if cur["things"] is None else max(cur["things"], things)
            cur["maps"] = max(cur["maps"] or 0, len(maps))
    return games


def r2(xs, ys):
    """Squared correlation; 0.0 when either series is constant, which explains nothing."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if not sxx or not syy:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) ** 2 / (sxx * syy)


def slope(ys):
    return (ys[-1] - ys[0]) / (len(ys) - 1) if len(ys) > 1 else None


def same_save_runs(games, save=None):
    """Consecutive games on one named save with a floor: the control that holds the map fixed."""
    runs, cur = [], []
    for g in games:
        if g["floor"] is None:                          # no GC, no reading: it does not break the run of loads
            continue
        if cur and g["save"] == cur[-1]["save"]:
            cur.append(g)
        else:
            cur = [g]
            runs.append(cur)
    return [r for r in runs if len(r) >= 3 and r[0]["save"] and (save is None or r[0]["save"] == save)]


def verdict(games):
    """Returns (verdict, evidence dict)."""
    use = [g for g in games if g["floor"] is not None and g["things"] is not None]
    res = [g["reserved"] for g in games if g["reserved"] is not None]
    ev = {"games": len(games), "gamesWithFloor": len(use)}
    if len(use) < MIN_GAMES or not res:
        return "UNMEASURED", ev
    floors = [g["floor"] for g in use]
    # the first and last quarter's means, so a single GC's scatter at either end cannot decide the rise
    q = max(1, len(floors) // 4)
    rise = sum(floors[-q:]) / q - sum(floors[:q]) / q
    ev.update(floorFirst=floors[0], floorLast=floors[-1], floorRiseMB=round(rise, 1), reservedFirst=res[0],
              reservedLast=res[-1], reservedRiseMB=round(res[-1] - res[0], 1),
              r2GameIndex=round(r2(list(range(len(use))), floors), 3),
              r2Things=round(r2([g["things"] for g in use], floors), 3))
    if rise < RISE_MB:
        return ("high_water_only" if res[-1] - res[0] >= RISE_MB else "flat"), ev
    if ev["r2Things"] >= MIN_R2 and ev["r2Things"] >= ev["r2GameIndex"]:
        return "map_scale", ev
    if ev["r2GameIndex"] >= MIN_R2:
        return "reload_ratchet", ev
    return "mixed", ev


def report(directory, session, same_save=None):
    full, rows = read_rows(directory, session)
    if not full:
        return None
    games = per_game(rows)
    v, ev = verdict(games)
    mods = next((r.get("mods") for r in rows if r.get("kind") == "session"), None)
    runs = same_save_runs(games, same_save)
    return {"session": full, "mods": mods, "verdict": v, "evidence": ev, "games": games,
            "sameSave": [{"save": r[0]["save"], "floors": [g["floor"] for g in r],
                          "mbPerLoad": round(slope([g["floor"] for g in r]), 1)} for r in runs]}


def show(rep):
    print("session %s  mods %s  verdict %s" % (rep["session"][:8], rep["mods"], rep["verdict"]))
    print("  " + "  ".join("%s=%s" % kv for kv in rep["evidence"].items()))
    print("  game save                        floor  first   last  gcs   peak reserved  things maps")
    for g in rep["games"]:
        print("  %4s %-26s %6s %6s %6s %4d %6s %8s %7s %4s" % (
            g["game"], g["save"][:26] or "(new game)", fmt(g["floor"]), fmt(g["firstGc"]), fmt(g["lastGc"]), g["gcs"],
            fmt(g["peak"]), fmt(g["reserved"]), g["things"] if g["things"] is not None else "-",
            g["maps"] if g["maps"] is not None else "-"))
    for r in rep["sameSave"]:
        print("  same save %s: floors %s, %s MB/load" % (r["save"], [round(f) for f in r["floors"]], r["mbPerLoad"]))


def fmt(x):
    return "-" if x is None else "%.0f" % x


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="the TPS record folder (default: the game's own)")
    ap.add_argument("--session", required=True, help="session id or a unique prefix")
    ap.add_argument("--control", help="a second session to set beside it, same save")
    ap.add_argument("--same-save", help="report same-save runs on this save only")
    ap.add_argument("--require", help="exit 1 unless the session's verdict is this")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    directory = a.dir or default_dir()
    rep = report(directory, a.session, a.same_save)
    if rep is None:
        print("UNMEASURED: session %s has no single record in %s" % (a.session, directory))
        return 2
    ctl = report(directory, a.control, a.same_save) if a.control else None
    if a.control and ctl is None:
        print("UNMEASURED: control %s has no single record in %s" % (a.control, directory))
        return 2
    if a.json:
        print(json.dumps({"session": rep, "control": ctl}, indent=1))
    else:
        show(rep)
        if ctl:
            show(ctl)
    if rep["verdict"] == "UNMEASURED":
        print("UNMEASURED: %s" % rep["evidence"])
        return 2
    if a.same_save and not rep["sameSave"]:
        print("UNMEASURED: no run of 3 or more same-save games on %s" % a.same_save)
        return 2
    if a.require and rep["verdict"] != a.require:
        print("REQUIRED %s, READ %s" % (a.require, rep["verdict"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
