#!/usr/bin/env python3
"""taozin_nest_live.py - live clauses L2/L3 of TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO on a generated RM_Abyss map.

    python3 src/RimStarWars/SWBestiary/taozin_nest_live.py L2     # WSL: stages an Abyss map, re-runs under python.exe
    python3 src/RimStarWars/SWBestiary/taozin_nest_live.py L3     # same staging (reuses a current RM_Abyss map)
    python.exe ...\\taozin_nest_live.py --inner L2 --out <json>   # the bridge half (Windows side)

L2 (owner card 2026-10-17, "A map feature with a guarding adult"; Crags = RM_Abyss): map generation on RM_Abyss runs
RSW_GenStep_TaozinNest (patched onto RM_Abyss.extraGenSteps), so the fresh map holds GRUB_MIN..GRUB_MAX living
RSW_TaozinGrub (the grub is never wild, so every one is the nest's), SILK_MIN..SILK_MAX stacks of RSW_WoolTaozin, every
grub and stack within NEST_RADIUS of the grubs' centre, and a living unowned RSW_Taozin within GUARD_RADIUS of it.
A patch that matches nothing, a GenStep that never runs or a gate that skips the map reads 0 grubs: FAIL.
L3 (the art reads in game): every nest grub and the guarding adult has thing_explain appearance rows whose body texPath
is the shipped one (EXPECTED_BODY, pinned to the defs by selftest_taozin_nest_live.py) and is held by >= 1 running
pack. Held by none = the renderer draws BadTex: FAIL.

Staging: a FRESH scratch vanilla quicktest world, a 2-ring land patch re-tiled to RM_Abyss with the Abyss's measured tile
values (design/Jawa/worldbuilding/biomes/abyss.md section 0: temp median -10.5 C, elevation median 490 m, the hilliest
def, LargeHills), centre mutators stripped, colony_found + world_tile_map_generate, map made current. Recipe:
Utils/modcheck/biome_site.py, as GelatinousSlime/live_kit_art.py uses it. Never Ash'karr, never a world a player
receives (CLAUDE.md worldgen ban); nothing is saved. If the CURRENT map is already RM_Abyss it is read instead (one
staging serves both lines in a sitting).
Exit 0 holds, 1 the clause is false, 2 UNMEASURED (no bridge, wrong load, wrong map, unreadable read). Callers hold the
bridge lock; this never takes it.
"""
import json
import math
import os
import subprocess
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
MODCHECK = os.path.join(UTILS, "modcheck")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch/taozin_nest"
TIMEOUT = 530
BIOME = "RM_Abyss"
ADULT, GRUB, SILK = "RSW_Taozin", "RSW_TaozinGrub", "RSW_WoolTaozin"
GRUB_MIN, GRUB_MAX = 2, 4          # RSW_TaozinNest.xml RM_CaveElement_Pawns count 2~4
SILK_MIN, SILK_MAX = 2, 3          # RM_CaveElement_Things stacks 2~3
NEST_RADIUS = 10.0                 # cave elements fall back to cells within ~4 of the site; 10 leaves slack
GUARD_RADIUS = 14.0                # the anchored adult spawns at the site; a 10-cell body may stand off it
EXPECTED_BODY = {ADULT: "Things/Pawn/Animal/RSW_Taozin/RSW_Taozin",
                 GRUB: "Things/Pawn/Animal/RSW_TaozinGrub/RSW_TaozinGrub"}
SPEC = types.SimpleNamespace(       # the fields biome_site.choose_tile / retile read
    BIOME=BIOME, LAT_MAX=45.0, MAP_SIZE=200,
    TILE={"temperature": -10.5, "rainfall": 0.0, "elevation": 490.0, "hilliness": "LargeHills", "swampiness": 0.0})


def pos(t):
    p = t.get("position") or {}
    return float(p.get("x")), float(p.get("z"))


def alive(t):
    return not t.get("dead")


def unowned(t):
    return t.get("faction") in (None, "", "None") and t.get("factionName") in (None, "")


def nest(things):
    """(rc, lines, ids) for L2 from list_things rows (includePawns) of ADULT, GRUB and SILK. Pure, for the selftest."""
    grubs = [t for t in things if t.get("def") == GRUB and alive(t)]
    silk = [t for t in things if t.get("def") == SILK]
    adults = [t for t in things if t.get("def") == ADULT and alive(t) and unowned(t)]
    lines = ["grubs %d, silk stacks %d, unowned adults %d" % (len(grubs), len(silk), len(adults))]
    fails = []
    if not (GRUB_MIN <= len(grubs) <= GRUB_MAX):
        fails.append("grubs %d, want %d..%d (0 = the nest never generated; more = a grub came from elsewhere)" % (
            len(grubs), GRUB_MIN, GRUB_MAX))
    if not (SILK_MIN <= len(silk) <= SILK_MAX):
        fails.append("silk stacks %d, want %d..%d" % (len(silk), SILK_MIN, SILK_MAX))
    guard = None
    if grubs:
        cx = sum(pos(t)[0] for t in grubs) / len(grubs)
        cz = sum(pos(t)[1] for t in grubs) / len(grubs)
        lines.append("nest centre %.1f,%.1f" % (cx, cz))
        for t in grubs + silk:
            d = math.hypot(pos(t)[0] - cx, pos(t)[1] - cz)
            if d > NEST_RADIUS:
                fails.append("%s %s %.1f cells from the nest (> %s)" % (t.get("def"), t.get("id"), d, NEST_RADIUS))
        near = sorted((math.hypot(pos(a)[0] - cx, pos(a)[1] - cz), a.get("id")) for a in adults)
        if near and near[0][0] <= GUARD_RADIUS:
            guard = near[0][1]
            lines.append("guard %s at %.1f cells" % (guard, near[0][0]))
        else:
            fails.append("no unowned living %s within %s of the nest (nearest %s)" % (
                ADULT, GUARD_RADIUS, "%.1f" % near[0][0] if near else "none"))
    lines += ["FAIL " + f for f in fails]
    ids = [t.get("id") for t in grubs] + ([guard] if guard else [])
    return (1 if fails else 0), lines + ([] if fails else ["HOLDS"]), ids


def art(ids, defs_by_id, explain):
    """(rc, lines) for L3: each nest pawn's appearance body row is EXPECTED_BODY[def] and held by a running pack."""
    if not ids or not any(defs_by_id.get(i) == ADULT for i in ids) or not any(defs_by_id.get(i) == GRUB for i in ids):
        return 2, ["UNMEASURED: no nest adult and grub to read (L2 must hold first): %s" % ids]
    fails, blind = [], []
    for pid in ids:
        name = defs_by_id.get(pid)
        ex = explain(pid) or {}
        app = ex.get("appearance") or {}
        rows = app.get("paths") if isinstance(app, dict) else None
        if ex.get("success") is False or not rows:
            blind.append("%s %s appearance unread: %s" % (name, pid, str(ex)[:150]))
            continue
        body = [r for r in rows if r.get("role") == "body"]
        if not body:
            fails.append("%s %s has no body row: %s" % (name, pid, rows))
            continue
        for r in body:
            if r.get("texPath") != EXPECTED_BODY[name]:
                fails.append("%s %s body texPath %s, want %s" % (name, pid, r.get("texPath"), EXPECTED_BODY[name]))
            elif not r.get("packsHoldingPath"):
                fails.append("%s %s body %s is held by no running pack: draws BadTex" % (name, pid, r.get("texPath")))
    lines = ["pawns explained %d" % len(ids)] + ["FAIL " + f for f in fails]
    if fails:
        return 1, lines
    if blind:
        return 2, lines + ["UNMEASURED: " + b for b in blind]
    return 0, lines + ["HOLDS"]


def stage(s, rec, work):
    import biome_site as B
    NS = B.pyre()
    mods, retired = B.running_retired(s.call)
    lack = B.missing_dlc(mods)
    if retired or lack:
        raise B.SiteError("UNMEASURED: wrong load (retired %s, DLC missing %s)" % (retired, lack))
    rec["world"] = NS.fresh_quicktest_world(s)
    rec["colonyTile"] = s.call("jawa/map_info").get("tile")
    rec["pick"] = B.choose_tile(s, SPEC, work, rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = B.retile(s, SPEC, rec["pick"]["patch"])
    NS.strip_mutators(s, centre)
    g = NS.generate(s, centre, SPEC.MAP_SIZE)   # raises on any failed mapgen finalize step
    rec["mapId"] = g["mapId"]
    s.call("jawa/set_current_map", mapId=g["mapId"])


def inner(clause, out_path):
    for p in (MODCHECK, UTILS):
        if p not in sys.path:
            sys.path.insert(0, p)
    from northstar_driver.session import FastSession
    rec = {"item": "TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO", "clause": clause,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rc, lines = 2, ["UNMEASURED: did not reach the read"]
    try:
        with FastSession(strict=False, focus=False) as s:   # never focus the game (live-tier rule)
            mi = s.call("jawa/map_info")
            rec["staged"] = mi.get("mapBiome") != BIOME
            if rec["staged"]:
                stage(s, rec, os.path.join(os.path.dirname(out_path), "taozin_nest_site"))
                mi = s.call("jawa/map_info")
            rec["map"] = {k: mi.get(k) for k in ("mapId", "mapBiome", "tile", "sizeX", "sizeZ")}
            if mi.get("mapBiome") != BIOME or (rec.get("mapId") is not None and mi.get("mapId") != rec["mapId"]):
                raise RuntimeError("UNMEASURED: current map %s biome %s is not the %s map %s" % (
                    mi.get("mapId"), mi.get("mapBiome"), BIOME, rec.get("mapId")))
            r = s.call("jawa/list_things", defName=",".join((ADULT, GRUB, SILK)), includePawns=True, limit=5000) or {}
            if r.get("success") is False or not isinstance(r.get("things"), list) or r.get("isCompleteList") is False:
                raise RuntimeError("UNMEASURED: list_things unreadable or truncated: %s" % str(r)[:200])
            if not r.get("scanned"):
                raise RuntimeError("UNMEASURED: list_things scanned %r things: the read cannot see" % r.get("scanned"))
            things = r["things"]
            rec["things"] = things
            rc, lines, ids = nest(things)
            if clause == "L3":
                by_id = {t.get("id"): t.get("def") for t in things}
                rc, more = art(ids, by_id, lambda pid: s.call("jawa/thing_explain", id=pid))
                lines = lines + more
            rec["ids"] = ids
    except Exception as ex:   # every failure is UNMEASURED with its reason on disk, never a silent pass
        msg = str(ex)[:400]
        if rc != 1:
            rc, lines = 2, [msg if msg.startswith("UNMEASURED") else "UNMEASURED: %s: %s" % (type(ex).__name__, msg)]
    rec["rc"], rec["lines"] = rc, lines
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    print("%s: %s" % (clause, "\n".join(lines)))
    return rc


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def outer(clause):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, "%s_%d_%d.json" % (clause.lower(), os.getpid(), time.time_ns()))
    argv = ["python.exe", win(os.path.abspath(__file__)), "--inner", clause, "--out", win(out)]
    print("$ " + " ".join(argv), flush=True)
    try:
        rc = subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode
    except (OSError, subprocess.TimeoutExpired) as ex:
        print("UNMEASURED: bridge half did not finish: %s" % ex)
        return 2
    if not os.path.exists(out):
        print("UNMEASURED: the bridge half wrote no %s (exit %d)" % (out, rc))
        return 2
    with open(out, encoding="utf-8") as fh:
        rec = json.load(fh)
    print("evidence: %s" % out)
    return rec.get("rc", 2) if rc in (0, 1, 2) and rc == rec.get("rc") else 2


def main(argv):
    clause = next((a for a in argv if a in ("L2", "L3")), None)
    if clause is None:
        print("usage: taozin_nest_live.py L2|L3")
        return 2
    if "--inner" in argv:
        out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(os.getcwd(), "taozin_%s.json" % clause)
        return inner(clause, out)
    return outer(clause)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
