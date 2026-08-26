# -*- coding: utf-8 -*-
r"""import_trial.py - carry Ash'karr onto a NEW world and measure what survives.

WHY
===
Owner, 2026-08-26, choosing between re-creating Ash'karr in full Ideology mode and
shipping classic mode: "Prove the import first." The import half has NEVER been run.
Everything said about it so far is a plan.

WHAT IT REFUSES TO DO
=====================
Four guards, each of which has a real incident behind it. None is advisory.

  1. NO MAP.  ASHKARR_WORLD_DEFINITION 12.4 rule 3: painting a planet under an
     instantiated map is what destroyed the save twice. Checked with
     rimworld/get_game_info -> mapCount, not with get_ui_state, which has no
     currentMap key at all and whose hasCurrentGame is true for a mapless game.

  2. NOT ASH'KARR.  This writes 21,872 tiles. Running it against the real planet
     would overwrite the thing it is trying to copy. Refuses if the world's name
     is Ash'karr unless --i-know-this-is-the-target is passed.

  3. TILE COUNT MUST MATCH.  A different planet coverage or MLP subcount gives a
     different tile count and every row would land on the wrong hex. Every
     importer takes expectTiles and this passes it.

  4. NOT CLASSIC MODE.  The entire point of the trial is a world with real
     ideoligions. jawa/ideo_of -> ideosTotal == 1 means classic, and importing
     onto it proves nothing about the question being asked.

USAGE
=====
    python.exe D:\Luke\dev\Rimworld\world\_rebuild\import_trial.py --bundle <stem>
    ... --dry-run          guards + dry run only, writes nothing   <- DO THIS FIRST
    ... --apply            actually import

A bundle stem is a path prefix: <stem>_tiles.csv, _links.csv, _settlements.csv.
Named regions come from the region column of the TILES csv, not a separate file.
"""
import sys, os, json, io, csv, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc

EXPECT_TILES = 21872


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, help="stem, e.g. D:\\...\\world\\ASHKARR_PREREBUILD_2026-08-26")
    ap.add_argument("--apply", action="store_true", help="actually write; otherwise dry run")
    ap.add_argument("--i-know-this-is-the-target", action="store_true",
                    help="override guard 2 - only when you deliberately mean to write onto Ash'karr")
    a = ap.parse_args(argv)

    tiles = a.bundle + "_tiles.csv"
    links = a.bundle + "_links.csv"
    setts = a.bundle + "_settlements.csv"
    for f in (tiles, links, setts):
        if not os.path.exists(f):
            print("MISSING: " + f)
            return 2

    # the region column is what world_features_import reads; say so before anything runs
    with io.open(tiles, encoding="utf-8") as fh:
        hdr = next(csv.reader(fh))
    if "region" not in hdr:
        print("REFUSED: %s has no 'region' column, so named regions cannot be imported." % tiles)
        print("  Export the bundle with vivify_world.py, whose first fourteen columns are the contract.")
        print("  header seen: %s" % ",".join(hdr[:16]))
        return 2

    h, p, t = rc.resolve_endpoint()
    b = rc.RimBridge(host=h, port=p, token=t, timeout=180)
    b.connect()

    def call(m, args=None):
        try:
            r = b.call(m, args or {})
            r.pop("operation", None)
            return r
        except Exception as ex:
            return {"success": False, "EXC": str(ex)}

    print("\nGUARDS")
    gi = call("rimworld/get_game_info")
    maps = gi.get("mapCount")
    print("  mapCount              : %s" % maps)
    if (maps or 0) > 0:
        print("  REFUSED - a map is instantiated. 12.4 rule 3. Discard it or start from the world screen.")
        return 3

    info = (call("jawa/world_info_get").get("info") or {})
    name, tilesCount = info.get("name"), call("jawa/world_info_get").get("tilesCount")
    print("  world                 : %r,  %s tiles" % (name, tilesCount))
    if name == "Ash'karr" and not a.i_know_this_is_the_target:
        print("  REFUSED - this world is called Ash'karr. Importing would overwrite the source.")
        print("  Pass --i-know-this-is-the-target only if that is genuinely what you mean.")
        return 3
    if tilesCount != EXPECT_TILES:
        print("  REFUSED - %s tiles, bundle is %d. Regenerate with Scale 7 / Coverage 100%%."
              % (tilesCount, EXPECT_TILES))
        return 3

    ideo = call("jawa/ideo_of", {"precepts": False})
    n_ideo = ideo.get("ideosTotal")
    print("  ideosTotal            : %s" % n_ideo)
    if n_ideo is not None and n_ideo <= 1:
        print("  REFUSED - one ideoligion means CLASSIC mode, which is the thing being tested away.")
        print("  Re-create the world with Ideology NOT in classic mode.")
        return 3
    print("  all four guards passed.")

    # ---- the imports, dry run first no matter what -------------------------
    steps = [
        ("jawa/world_tile_import",        {"path": tiles, "expectTiles": EXPECT_TILES, "maxRows": 30000}),
        ("jawa/world_links_import",       {"path": links, "expectTiles": EXPECT_TILES, "clearFirst": True}),
        ("jawa/world_settlements_import", {"path": setts, "expectTiles": EXPECT_TILES, "clearExisting": True}),
        ("jawa/world_features_import",    {"path": tiles, "expectTiles": EXPECT_TILES, "clearExisting": True}),
    ]
    print("\nDRY RUN")
    for tool, args in steps:
        r = call(tool, dict(args, apply=False))
        print("  %-32s %s" % (tool.split("/")[-1], (r.get("message") or json.dumps(r))[:120]))
        if r.get("success") is False:
            print("    ^ a dry run that fails is the answer. Stopping.")
            return 4
    if not a.apply:
        print("\nDry run only. Re-run with --apply to write.")
        return 0

    print("\nAPPLY")
    for tool, args in steps:
        r = call(tool, dict(args, apply=True))
        print("  %-32s %s" % (tool.split("/")[-1], (r.get("message") or json.dumps(r))[:120]))
    print("  commit: %s" % call("jawa/world_commit", {}).get("success"))

    # ---- read it back, through DIFFERENT tools than wrote it ---------------
    print("\nREAD BACK  (a writer's own echo is not evidence)")
    v = call("jawa/world_tile_validate", {"path": tiles, "maxRows": 30000, "limit": 40})
    print("  tiles      rows %s matched %s mismatched %s (%.2f%%) raw=%s"
          % (v.get("rows"), v.get("matched"), v.get("mismatched"),
             v.get("matchPct") or 0.0, v.get("readRawFields")))
    if v.get("byField"):
        print("             byField %s" % json.dumps(v["byField"])[:200])
    lv = call("jawa/world_links_validate", {"limit": 20})
    print("  links      river %s road %s | asymmetric %s nonAdjacent %s"
          % (lv.get("riverEntries"), lv.get("roadEntries"),
             lv.get("asymmetricCount"), lv.get("nonAdjacentCount")))
    ov = call("jawa/world_objects_validate", {"limit": 20})
    print("  objects    settlements %s | nullFaction %s badTile %s onWater %s stacked %s"
          % (ov.get("settlements"), ov.get("nullFactionSettlements"), ov.get("badTileCount"),
             ov.get("settlementsOnWater"), ov.get("stackedTiles")))
    ma = call("jawa/world_mutators_audit", {"limit": 5})
    print("  mutators   tilesWithMutators %s   <- EXPECT ~0: there is no mutators importer"
          % ma.get("tilesWithMutators"))
    lm = call("jawa/world_landmarks_get", {"limit": 30000})
    got = len(lm.get("landmarks") or [])
    print("  landmarks  %s                     <- EXPECT 0: there is no landmarks importer" % got)

    print("""
WHAT THIS RUN ANSWERS
  The four file imports either carried the planet or they did not, and the read-back
  above says which - through validators that read RAW fields, not the importers' echo.
  Mutators and landmarks were NEVER going to cross: no importer exists for either
  (WORLD_MUTATOR_LANDMARK_IMPORTERS_1). Their counts above are the size of the replay
  that a real rebuild would still owe - 13,569 mutator tiles and 579 landmarks on the
  source planet.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
