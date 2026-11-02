#!/usr/bin/env python3
"""The big repaint, live half: stamp world/repaint_2026-10-21/tiles_biome.csv (and the Scald temperature CSV) onto
the loaded dev world, read back what it must not disturb, and save under a NEW name. Plan section 3 steps 6-8:
design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md (item BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL).

    python3 src/RimMandrake/Utils/remake/repaint_stamp.py --plan          offline: the steps and the bars, no bridge
    python3 src/RimMandrake/Utils/remake/repaint_stamp.py                 DRY RUN on the bridge: load R3, import apply:false
    python3 src/RimMandrake/Utils/remake/repaint_stamp.py --apply         stamp, validate, commit, read back, save

Only a seat holding the bridge runs the last two (`rimflow bridge take --for "big repaint stamp"`), with the game up on
a list that loads RM_SleepingIce and RM_Wastes. Every bar is checked before the next write; the first failed bar stops
the run with nothing saved. R3 is never overwritten; an existing REPAINT save is never overwritten.

Then the offline proof (step 9), read-only:
    python3 src/RimMandrake/Utils/remake/repaint_biomes.py verify-save "<Saves>/ASHKARR_DEV_START_2026-10-21_REPAINT.rws" \
        --against world/repaint_2026-10-21/tiles_biome.csv

The CSVs are copied under the agent storage root (AGENT_STORAGE_ROOT, else ~/dev/Lodestar/bin/lib/agent_storage.py,
which fails by name when unset: no fallback) so the game reads a plain Windows drive path, never a \\\\wsl UNC one.
"""
import argparse, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
sys.path.insert(0, UTILS)

EXPECT_TILES = 21872
SOURCE_SAVE = "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3"
TARGET_SAVE = "ASHKARR_DEV_START_2026-10-21_REPAINT"
STAMP = os.path.join(REPO, "world", "repaint_2026-10-21", "tiles_biome.csv")
SCALD = os.path.join(REPO, "world", "repaint_2026-10-21", "scald_temperature.csv")
EXPECT_LABELS = 71          # plan section 3 step 7: jawa/world_features_get must still show 71 labels


def storage_root():
    root = os.environ.get("AGENT_STORAGE_ROOT")
    if not root:
        root = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                              capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    return root


def windows_path(p):
    if os.name == "nt":
        return p
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, check=True, timeout=30).stdout.strip()


def stage_csvs():
    d = os.path.join(storage_root(), "rimmandrake", "repaint_2026-10-21")
    os.makedirs(d, exist_ok=True)
    out = {}
    for k, src in (("stamp", STAMP), ("scald", SCALD)):
        dst = os.path.join(d, os.path.basename(src))
        shutil.copyfile(src, dst)
        out[k] = windows_path(dst)
    return out


STEPS = [
    ("load", "rimworld/load_game_ready {saveName: %s}; the renamed-def tiles load as the default biome (expected)" % SOURCE_SAVE),
    ("dry", "jawa/world_tile_import stamp apply:false expectTiles:%d -> unknownBiomes [] and biomeSkipped 0 and success" % EXPECT_TILES),
    ("apply", "jawa/world_tile_import stamp apply:true -> applied %d, success" % EXPECT_TILES),
    ("validate", "jawa/world_tile_validate stamp -> mismatched 0, checkedRows %d" % EXPECT_TILES),
    ("scald", "jawa/world_tile_import scald_temperature.csv dry then apply; world_tile_validate -> mismatched 0"),
    ("commit", "jawa/world_commit -> success"),
    ("readback", "jawa/world_mutators_audit offenderCount 0; jawa/world_features_get %d labels" % EXPECT_LABELS),
    ("save", "rimworld/save_game {saveName: %s} (refused if that save exists)" % TARGET_SAVE),
]


class Stop(Exception):
    pass


def bar(ok, what, r):
    if not ok:
        raise Stop("%s: %s" % (what, json.dumps(r, default=str)[:600]))


def run(rb, apply, paths, log):
    def call(tool, params):
        r = rb.call(tool, params)
        log.append({"tool": tool, "params": params, "result": r})
        return r

    import game_paths
    if apply and os.path.exists(os.path.join(game_paths.SAVES, TARGET_SAVE + ".rws")):
        raise Stop("%s.rws already exists: never overwritten" % TARGET_SAVE)
    r = call("rimworld/load_game_ready", {"saveName": SOURCE_SAVE})
    bar(r.get("success", True) is not False, "load", r)
    wi = call("jawa/world_info_get", {})
    bar(wi.get("tilesCount") == EXPECT_TILES, "grid size", {"tilesCount": wi.get("tilesCount")})
    r = call("jawa/world_tile_import", {"path": paths["stamp"], "apply": False, "expectTiles": EXPECT_TILES})
    bar(r.get("success") and not r.get("unknownBiomes") and r.get("biomeSkipped") == 0, "dry import", r)
    if not apply:
        return "DRY RUN PASS: the stamp would write %s rows; nothing written" % r.get("wouldApply")
    r = call("jawa/world_tile_import", {"path": paths["stamp"], "apply": True, "expectTiles": EXPECT_TILES})
    bar(r.get("success") and r.get("applied") == EXPECT_TILES, "apply import", r)
    r = call("jawa/world_tile_validate", {"path": paths["stamp"]})
    bar(r.get("mismatched") == 0 and r.get("checkedRows") == EXPECT_TILES, "validate stamp", r)
    r = call("jawa/world_tile_import", {"path": paths["scald"], "apply": False, "expectTiles": EXPECT_TILES})
    bar(r.get("success") and r.get("biomeSkipped") == 0, "dry scald", r)
    r = call("jawa/world_tile_import", {"path": paths["scald"], "apply": True, "expectTiles": EXPECT_TILES})
    bar(r.get("success"), "apply scald", r)
    r = call("jawa/world_tile_validate", {"path": paths["scald"]})
    bar(r.get("mismatched") == 0 and (r.get("checkedRows") or 0) > 0, "validate scald", r)
    r = call("jawa/world_commit", {})
    bar(r.get("success"), "commit", r)
    r = call("jawa/world_mutators_audit", {"limit": 50})
    bar(r.get("offenderCount") == 0, "mutators audit", r)
    r = call("jawa/world_features_get", {"limit": 100})
    bar(r.get("count") == EXPECT_LABELS, "labels", {"count": r.get("count")})
    r = call("rimworld/save_game", {"saveName": TARGET_SAVE})
    bar(r.get("success", True) is not False, "save", r)
    return "STAMPED and saved as %s; next: repaint_biomes.py verify-save" % TARGET_SAVE


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--plan", action="store_true", help="print the steps and bars; no bridge")
    ap.add_argument("--log", help="JSON log of every call (default: under the agent storage root)")
    a = ap.parse_args(argv)
    for p in (STAMP, SCALD):
        if not os.path.exists(p):
            print("REFUSED: %s missing" % p)
            return 2
    if a.plan:
        for k, s in STEPS:
            print("%-9s %s" % (k, s))
        return 0
    from rimbridge_client import RimBridge, resolve_endpoint
    paths = stage_csvs()
    log, code = [], 0
    host, port, token = resolve_endpoint()
    try:
        with RimBridge(host, port, token, timeout=600.0) as rb:
            print(run(rb, a.apply, paths, log))
    except Stop as e:
        print("STOPPED, nothing saved: %s" % e)
        code = 1
    out = a.log or os.path.join(storage_root(), "rimmandrake", "repaint_2026-10-21",
                                "stamp_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    json.dump(log, open(out, "w"), indent=1, default=str)
    print("log:", out)
    return code


if __name__ == "__main__":
    sys.exit(main())
