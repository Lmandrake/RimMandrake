#!/usr/bin/env python3
"""SCRUB_WILDLIFE_PROVE_NOBODY_CAME live A1: does a FRESH RM_LeaningScrub map get its wildlife at map generation?

    python3 src/RimMandrake/LeaningScrub/northstar/wildlife_mapgen_live.py         # WSL: re-runs itself under python.exe
    python.exe ...\\wildlife_mapgen_live.py --inner [--out <json>]                  # the bridge half (Windows side)

Exit 0 = the generated map holds >= 1 unowned animal and >= site_spec.MIN_NATIVES living natives. Exit 1 = it does
not, or a read could not complete (UNMEASURED is never a pass). On a zero it prints the inputs of the engine's
DesiredAnimalDensity that a live map alone holds (tile pollution: on the Biotech pollution path every kind's weight is
CommonalityOfPollutionAnimal, which RM_LeaningScrub never sets; the tile's mutators; the outdoor temperature against
the season gate), so a zero names its route. The static routes are selftest_scrub_wildlife_zero_paths.py's.

Recipe: the Scrub saved-site recipe's first half (biome_site.py: fresh scratch quicktest world, 2-ring land patch
re-tiled to RM_LeaningScrub at site_spec.TILE, centre mutators stripped, colony_found + world_tile_map_generate) and
nothing after it: no clean, no save, no registry write. A scratch vanilla quicktest world, never Ash'karr and never a
world a player receives (CLAUDE.md worldgen ban). Needs: game up on biomes_sprint (all five DLC), bridge held.

Census: list_pawns with NO faction filter, unowned rows kept here (the deployed faction=none filter returned 0 on a
20-animal map, 2026-10-21), cross-checked by biome_site.census (list_things per native defName).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRUB = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(SCRUB, "..", "..", ".."))
MODCHECK = os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck")
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch/scrub_wildlife"
TIMEOUT = 520


def wild_rows(pawns):
    """Unowned, living animals from an UNFILTERED list_pawns reply. Row shape (JawaBenchTerrainTools ListPawns):
    faction = the faction's defName or null; no humanlike field, so intelligence == 'Humanlike' is the person test
    (lesson 20261102T170737Z); isMechanoid; dead.
    A row counts only when it AFFIRMS every field: faction present and null, isPlayer False, dead False, isMechanoid
    False and intelligence 'Animal'; a row missing any of them is not wildlife (never counted on absence)."""
    out = []
    for p in pawns or []:
        if not isinstance(p, dict) or "faction" not in p or p["faction"] is not None:
            continue
        if p.get("isPlayer") is not False or p.get("dead") is not False or p.get("isMechanoid") is not False:
            continue
        if p.get("intelligence") != "Animal" or not (p.get("kind") or p.get("def")):
            continue
        out.append(p.get("kind") or p.get("def"))
    return out


def verdict(wild, natives, min_natives, diag):
    """(ok, line) from the counts; pure, so the selftest can sweep it."""
    n_nat = sum(natives.values())
    if wild >= 1 and n_nat >= min_natives:
        return True, "A1 PASS: %d wild animal(s), %d native(s) at map generation" % (wild, n_nat)
    return False, "A1 FAIL: %d wild animal(s), %d native(s) (want >= 1 and >= %d); inputs %s" % (
        wild, n_nat, min_natives, json.dumps(diag, sort_keys=True))


def inner(out_path):
    for p in (MODCHECK, UTILS, SCRUB):
        if p not in sys.path:
            sys.path.insert(0, p)
    import biome_site as B
    from northstar_driver.session import FastSession
    S = B.load_spec(os.path.join(SCRUB, "site_spec.py"), "scrub_wildlife_site_spec")
    NS = B.pyre()
    rec = {"item": "SCRUB_WILDLIFE_PROVE_NOBODY_CAME", "clause": "A1", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                                            time.gmtime())}
    s = FastSession(strict=False)
    ok, line = False, "A1 FAIL: UNMEASURED (did not reach the census)"
    try:
        with s:
            mods, retired = B.running_retired(s.call)
            lack = B.missing_dlc(mods)
            rec["mods"] = mods
            if retired or lack:
                line = "A1 FAIL: UNMEASURED: wrong load (retired %s, DLC missing %s); load biomes_sprint" % (retired,
                                                                                                         lack)
                raise B.SiteError(line)
            rec["world"] = NS.fresh_quicktest_world(s)
            rec["colonyTile"] = s.call("jawa/map_info").get("tile")
            work = os.path.join(os.path.dirname(out_path), "scrub_wildlife_site")
            rec["pick"] = B.choose_tile(s, S, work, rec["colonyTile"])
            centre = rec["pick"]["centre"]
            rec["retiled"] = B.retile(s, S, rec["pick"]["patch"])
            NS.strip_mutators(s, centre)
            g = NS.generate(s, centre, S.MAP_SIZE)
            rec["mapId"] = g["mapId"]
            s.call("jawa/set_current_map", mapId=g["mapId"])
            mi = s.call("jawa/map_info")
            if mi.get("mapId") != g["mapId"] or mi.get("mapBiome") != S.BIOME:
                line = "A1 FAIL: UNMEASURED: current map %s biome %s, want %s %s" % (
                    mi.get("mapId"), mi.get("mapBiome"), g["mapId"], S.BIOME)
                raise B.SiteError(line)
            lp = s.call("jawa/list_pawns", limit=5000)
            if lp.get("success") is False or not isinstance(lp.get("pawns"), list):
                line = "A1 FAIL: UNMEASURED: list_pawns unreadable %s" % str(lp)[:200]
                raise B.SiteError(line)
            wild = wild_rows(lp["pawns"])
            natives = B.census(s.call, S)
            mu = s.call("jawa/world_mutators_get", tiles=str(centre))
            diag = {"tile": mi.get("tile"), "tileInfo": mi.get("tileInfo"), "outdoorTempNow": mi.get("outdoorTempNow"),
                    "season": mi.get("season"), "latitude": mi.get("latitude"),
                    "mutators": ((mu.get("tiles") or [{}])[0]).get("mutators"), "pawnsListed": len(lp["pawns"])}
            rec.update({"wild": len(wild), "wildKinds": sorted(set(wild)), "natives": natives, "diag": diag})
            ok, line = verdict(len(wild), natives, S.MIN_NATIVES, diag)
    except Exception as ex:   # every failure is a FAIL with its reason on disk, never a silent pass
        ok = False                                    # an error after the verdict (session exit) still fails
        rec["error"] = "%s: %s" % (type(ex).__name__, str(ex)[:400])
        if "UNMEASURED" not in line:
            line = "A1 FAIL: UNMEASURED: %s" % rec["error"]
    rec["ok"], rec["line"] = ok, line
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    print(line)
    return 0 if ok else 1


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def outer():
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, "a1_%d_%d.json" % (os.getpid(), time.time_ns()))   # this run's own file
    argv = ["python.exe", win(os.path.abspath(__file__)), "--inner", "--out", win(out)]
    print("$ " + " ".join(argv), flush=True)
    rc = subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode
    if not os.path.exists(out):
        print("A1 FAIL: the bridge half wrote no %s (exit %d)" % (out, rc))
        return 1
    with open(out, encoding="utf-8") as fh:
        rec = json.load(fh)
    print("evidence: %s" % out)
    return 0 if rc == 0 and rec.get("ok") is True else 1


def main(argv):
    if "--inner" in argv:
        out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(os.getcwd(), "scrub_wildlife_a1.json")
        return inner(out)
    return outer()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
