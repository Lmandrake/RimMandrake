"""w9_run.py - stamp the authored planet onto a live world, in the order that works.

    python.exe src/RimMandrake/Utils/w9_run.py                 DRY RUN - the default
    python.exe src/RimMandrake/Utils/w9_run.py --apply         write for real
    python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_gen

    python3   src/RimMandrake/Utils/w9_run.py --inputs world/paint_inputs_2026-10-20 --check-inputs
                                                                 offline validation only, no game
    python.exe src/RimMandrake/Utils/w9_run.py --inputs world/paint_inputs_2026-10-20   dry run of a bundle

    ⚠️ There is NO `--dry`. This block claimed one until 2026-08-21 and argparse
    refused it; the dry run is what you get by passing nothing. The real flags are
    --apply, --load, --report, --skip-links, --despite-map, --despite-abort,
    --inputs DIR, --feature-def, --check-inputs.

🔴 WINDOWS `python.exe`. The bridge is on Windows loopback; WSL cannot reach it.

WHY A SCRIPT AND NOT A CHECKLIST. The stage ORDER is not a preference - §12 of the W9
spec has mutators clearing after the biome repaint and features last, because each stage
invalidates assumptions the previous one made. Driving it by hand means re-deciding the
order every time and getting it wrong once.

THE STAGES, and the two ordering rules that are engine facts rather than taste:
    1   tiles            biome + scalars
    2   links            rivers mouth-first, then roads. 🔴 The ORDER is laid HERE from
                            DIR/ASHKARR_WORLDMAP_riverdist.csv (tile,river_dist): a CSV
                            exported from a save is not mouth-first, and laying it in file
                            order flattened every river head to <= 5 (parity U4). No
                            riverdist file = file order, as before, with a warning.
    3   mutators, clear  the marine ones the repaint stranded
    3b  landmarks, clear the 49 vanilla worldgen leftovers
    4   landmarks, add   🔴 BEFORE settlements - IsValidTile refuses a settlement tile
                            and its neighbours, and AddLandmark ignores that verdict
    4a  mutators, strip  every live (tile, mutator) NOT in the mutators input, except
                            KEEP_DERIVED - the frozen-world rule: nothing the engine rolled
                            at worldgen (or AddLandmark rolled in stage 4) survives (parity
                            U2: 28,616 rolled entries survived the 2026-10-20 stamp). Runs
                            after 4 so it catches the landmark rolls, before 4b so a rolled
                            entry no longer holds a shared slot the input needs.
    4b  mutators, add    🔴 AFTER landmarks - AddLandmark also rolls the def's own
                            mutatorChances onto its tile, on top of whatever is there
    5   settlements
    6   features         the region labels — ⚠️ 71 as of 2026-08-23, not the 23 this
                         line used to claim. Verify the stage handles all of them.
                         With DIR/ASHKARR_WORLDMAP_features.csv present, its `size` and
                         `centerTile` columns set each label by name (parity U1);
                         without it the importer computes sqrt(tiles)*1.35, as before.
    commit -> lint -> screenshot

Stages 3b, 4 and 4b were added 2026-08-21 on the owner's order; before that the paint
carried no mutator and no landmark layer at all. Their input is authored by
`ashkarr_populate.py`, which writes the two CSVs they read.

🔴 IT REFUSES TO START ON A ZOMBIE. A save can abort mid-load, the engine's own bail
handler can throw, and the process will then report `game_loaded` and answer every call
while being half-disposed. Measured 2026-08-20: hours of work landed on a corpse. The
canary greps Player.log for `ErrorWhileLoadingGame`, which the engine writes only when it
has given up on a load. ⚠️ Do NOT go back to using the debug `Actions` tree for this - it
was tried, and it was wrong in both directions.

WHAT IT DOES NOT DO: decide. It writes a report and takes a picture. Whether the planet
is RIGHT is a human looking at it against world/view/ASHKARR_WORLDMAP.biome.equirect.png.
"""
import argparse
import io
import json
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import PLAYER_LOG as _PLAYER_LOG  # noqa: E402
from game_paths import SAVES as _SAVES_DIR  # noqa: E402
import save_played_tiles  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
RECORD_DIR = os.path.join(REPO, "world")
TILES = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_tiles.csv")
LINKS = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_links.csv")
SETTS = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_settlements.csv")
MUTS = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_mutators.csv")
LMKS = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_landmarks.csv")
FEATS = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_features.csv")
RIVERDIST = os.path.join(RECORD_DIR, "ASHKARR_WORLDMAP_riverdist.csv")
EXPECT_TILES = 21872
# Mutators the engine DERIVES from stamped geography, so stage 4a keeps them although no input
# names them. RM_SeaCoast: our drop-in twin of vanilla Coast beside the modded seas
# (src/RimMandrake/SeaShores/Defs/TileMutatorDefs/RM_SeaCoast.xml); all 336 dev placements border
# stamped water and none is on water (design/Jawa/worldbuilding/parity_causes_2026-10-20.md U2).
# Same set as parity_fix_plans.KEEP_DERIVED (the selftest holds them equal).
KEEP_DERIVED = frozenset({"RM_SeaCoast"})
FEATURE_DEF_DEFAULT = "WB_MapLabelFeature"
# The five stamp files, by layer. `--inputs DIR` rebinds all five at once to DIR (G7, runbook
# §0.5): a remapped bundle is stamped from its own folder instead of overwriting the frozen
# RECORD (`world/ASHKARR_WORLDMAP_tiles.csv.frozen.json` guards it). Nothing here ever writes
# a CSV - this script only reads them.
LAYERS = ("tiles", "links", "settlements", "mutators", "landmarks")


def set_inputs(dirpath):
    """Rebind TILES/LINKS/SETTS/MUTS/LMKS to `dirpath`/ASHKARR_WORLDMAP_<layer>.csv.

    Returns {layer: path}. A missing file is NOT an error here; check_inputs() decides.
    """
    global TILES, LINKS, SETTS, MUTS, LMKS, FEATS, RIVERDIST
    d = os.path.abspath(dirpath)
    p = {k: os.path.join(d, "ASHKARR_WORLDMAP_%s.csv" % k) for k in LAYERS}
    TILES, LINKS, SETTS, MUTS, LMKS = (p["tiles"], p["links"], p["settlements"],
                                       p["mutators"], p["landmarks"])
    # Optional companions (absent = the old behaviour): label size/centre, river target.
    FEATS = os.path.join(d, "ASHKARR_WORLDMAP_features.csv")
    RIVERDIST = os.path.join(d, "ASHKARR_WORLDMAP_riverdist.csv")
    return p


def mouth_first_links(out, tmpdir=None):
    """Stage 2's input path. -> (path, ok).

    With RIVERDIST present: re-order and re-orient the river rows of LINKS so OverlayRiver
    reproduces it exactly (river_lay.order_links_mouth_first), write that to a temp CSV and
    return its path; ok=False if the order cannot reproduce the target (stage 2 then stops).
    Without it: LINKS itself, in file order, as before - with a warning."""
    import csv as _csv
    import tempfile
    from river_lay import order_links_mouth_first, read_river_dist
    target = read_river_dist(RIVERDIST)
    if target is None:
        w(out, "- ⚠️ stage 2: no %s - rivers laid in FILE order; riverDist is whatever that "
               "order gives (parity U4)" % os.path.basename(RIVERDIST))
        return LINKS, True
    rows = read_csv(LINKS) or []
    try:
        laid, mism = order_links_mouth_first(rows, target)
    except ValueError as e:
        w(out, "- 🔴 stage 2 river order: %s" % e)
        return LINKS, False
    riv = {int(x) for r in rows if (r.get("kind") or "").strip() == "river" for x in (r["a"], r["b"])}
    if set(target) != riv:
        w(out, "- 🔴 stage 2 river order: river_dist covers %d tile(s), the river links touch %d "
               "(%d differ) - the table does not describe these links"
             % (len(target), len(riv), len(set(target) ^ riv)))
        return LINKS, False
    if mism:
        w(out, "- 🔴 stage 2 river order cannot reproduce river_dist on %d tile(s): %s"
             % (len(mism), mism[:5]))
        return LINKS, False
    fd, path = tempfile.mkstemp(prefix="w9_links_mouthfirst_", suffix=".csv", dir=tmpdir)
    with io.open(fd, "w", encoding="utf-8", newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(laid)
    nriv = sum(1 for r in laid if r.get("kind") == "river")
    w(out, "- stage 2 river order: %d river link(s) laid mouth-first from %s (reproduces "
           "river_dist on all %d river tiles) -> %s" % (nriv, os.path.basename(RIVERDIST), len(target), path))
    return path, True


def stamp_mutator_entries(rows):
    """{(tile, def)} the mutators input names. rows: ASHKARR_WORLDMAP_mutators.csv dicts."""
    out = set()
    for r in rows:
        for name in (r.get("mutators") or "").split(";"):
            name = name.strip()
            if name:
                out.add((int(r["tile"]), name))
    return out


def rolled_mutators(live, stamp, keep=KEEP_DERIVED):
    """Stage 4a's removal list: {def: sorted tiles} for every live (tile, def) the stamp input
    does not hold and whose def is not in `keep`. live/stamp: iterables of (tile, def)."""
    by = {}
    stamp = set(stamp)
    for t, d in set(live):
        if (t, d) in stamp or d in keep:
            continue
        by.setdefault(d, []).append(t)
    return {d: sorted(ts) for d, ts in by.items()}


def read_live_mutators(rb, tiles_count, step=2000):
    """[(tile, def)] for every mutator on the live surface, read in ranges. Refuses (raises) a
    truncated read: a strip computed from a partial read would keep what it never saw."""
    live = []
    for lo in range(0, tiles_count, step):
        hi = min(tiles_count, lo + step) - 1
        r = rb.call("jawa/world_mutators_get", {"range": "%d-%d" % (lo, hi),
                                                "onlyWithMutators": True, "limit": step + 1})
        if not r.get("success") or r.get("limitHit") or r.get("errors"):
            raise RuntimeError("world_mutators_get %d-%d: success=%s limitHit=%s errors=%s"
                               % (lo, hi, r.get("success"), r.get("limitHit"), str(r.get("errors"))[:120]))
        for t in r.get("tiles") or []:
            for m in t.get("mutators") or []:
                d = (m or {}).get("def")
                if d:
                    live.append((int(t["tile"]), d))
    return live


def inputs_feature_def(dirpath):
    """The single FeatureDef named by DIR/ASHKARR_WORLDMAP_features.csv, or None.

    A bundle built for a mod list without Worldbuilder cannot use `WB_MapLabelFeature`; its
    features CSV says which def its labels carry. Two or more defs -> None (ambiguous;
    stage 6 imports every label under ONE def, so the caller must pass --feature-def).
    """
    rows = read_csv(os.path.join(os.path.abspath(dirpath), "ASHKARR_WORLDMAP_features.csv"))
    if not rows:
        return None
    defs = {r.get("def") for r in rows if r.get("def")}
    return defs.pop() if len(defs) == 1 else None


def check_inputs(out):
    """Offline validation of the five stamp files now bound. -> list of problems ([] = ok).

    No bridge. Catches what would otherwise surface mid-stamp on a live world: a missing
    layer, a tiles file of the wrong subdivision, a duplicated tile, a header the bridge
    importer will not read.
    """
    need = {"tiles": {"tile", "biome", "region"}, "links": {"kind", "a", "b", "def"},
            "settlements": {"faction_def", "name", "tile"}, "mutators": {"tile", "mutators"},
            "landmarks": {"tile", "landmark"}}
    paths = dict(zip(LAYERS, (TILES, LINKS, SETTS, MUTS, LMKS)))
    probs = []
    for k in LAYERS:
        rows = read_csv(paths[k])
        if rows is None:
            probs.append("%s: missing (%s)" % (k, paths[k]))
            continue
        cols = set(rows[0].keys()) if rows else set()
        miss = need[k] - cols
        if miss:
            probs.append("%s: missing column(s) %s" % (k, sorted(miss)))
            continue
        if k == "tiles":
            try:
                ids = [int(r["tile"]) for r in rows]
            except (TypeError, ValueError):
                probs.append("tiles: a row has a non-integer tile id")
                continue
            if len(ids) != EXPECT_TILES or len(set(ids)) != EXPECT_TILES:
                probs.append("tiles: %d rows / %d distinct, expected %d"
                             % (len(ids), len(set(ids)), EXPECT_TILES))
            if any(not r["biome"] for r in rows):
                probs.append("tiles: %d row(s) with an empty biome" % sum(1 for r in rows if not r["biome"]))
        w(out, "- input %-11s %6d rows  %s" % (k, len(rows), paths[k]))
    probs += check_companions(out)
    return probs


def check_companions(out):
    """Offline check of the optional riverdist and features files. -> problems."""
    from river_lay import order_links_mouth_first, read_river_dist
    probs = []
    target = read_river_dist(RIVERDIST) if os.path.isfile(RIVERDIST) else None
    links = read_csv(LINKS)
    if target is not None and links:
        try:
            laid, mism = order_links_mouth_first(links, target)
        except ValueError as e:
            laid, mism = [], [str(e)]
        riv = {int(x) for r in links if r.get("kind") == "river" for x in (r["a"], r["b"])}
        if mism:
            probs.append("riverdist: the lay order misses river_dist on %d tile(s): %s" % (len(mism), mism[:3]))
        elif riv != set(target):
            probs.append("riverdist: covers %d tiles, river links touch %d" % (len(target), len(riv)))
        else:
            w(out, "- input %-11s %6d rows  reproduced exactly by the mouth-first lay" % ("riverdist", len(target)))
    feats = read_csv(FEATS)
    tiles = read_csv(TILES)
    if feats and tiles and "centerTile" in feats[0]:
        region = {int(r["tile"]): (r.get("region") or "").strip() for r in tiles}
        off = [r["name"] for r in feats if (r.get("centerTile") or "").strip()
               and region.get(int(r["centerTile"])) != r["name"]]
        if off:
            probs.append("features: %d centerTile(s) not on their own region: %s" % (len(off), off[:5]))
        else:
            w(out, "- input %-11s %6d rows  every centerTile on its own region" % ("features", len(feats)))
    return probs


def read_csv(path):
    """Rows as dicts, or None if the file was never authored.

    ⚠️ Returns None rather than [] on a missing file, because an empty stage and an
    unauthored stage must not report the same thing. A stage that silently does nothing
    is the failure mode this whole run exists to avoid.
    """
    if not os.path.isfile(path):
        return None
    import csv as _csv
    # utf-8-sig: a BOM must not rename the first header; newline="": csv owns embedded newlines.
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        return list(_csv.DictReader(fh))


def w(out, line):
    out.append(line)
    print(line)


PLAYER_LOG = _PLAYER_LOG


def canary(rb, out):
    """Did this load actually finish?

    🔴 THE AUTHORITATIVE SIGNAL IS THE LOG, not the debug tree. An earlier version
    of this check used `list_debug_action_children("Actions")` and it was WRONG in
    both directions: the tree legitimately reports few or no VISIBLE children when
    no map is loaded, and it enumerated fine on a game that had definitely aborted.
    A canary that fires on healthy games and stays silent on broken ones is worse
    than none. `ErrorWhileLoadingGame` in Player.log is unambiguous - the engine
    only writes it when it has given up on a load and is bailing to the main menu.
    """
    try:
        with io.open(PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            log = fh.read()
    except Exception as e:
        w(out, "- ⚠️ canary could not read Player.log (%s); proceeding UNVERIFIED" % e)
        return True
    # 🔴 TWO STRINGS, NOT ONE. Measured 2026-08-21: `WORLDMAP_gen` aborted on
    # FactionControl's cross-ref postfix and bailed to the main menu while
    # `ErrorWhileLoadingGame` read ZERO. That handler is
    # `GameAndMapInitExceptionHandlers.ErrorWhileLoadingGame` and it fires on MAP init -
    # a save with `<maps />` empty dies in FinalizeLoading with no map-init handler to
    # write the string. So the old canary called a dead load healthy, which is the exact
    # failure this function exists to prevent.
    n = log.count("ErrorWhileLoadingGame")
    m = log.count("Exception in FinalizeLoading")
    if n == 0 and m == 0:
        w(out, "- canary: no `ErrorWhileLoadingGame` and no `Exception in FinalizeLoading` "
               "-> the load finished")
        return True
    if n == 0 and m > 0:
        w(out, "- 🔴 CANARY FAILED: %d `Exception in FinalizeLoading` and ZERO "
               "`ErrorWhileLoadingGame`. That combination is a NO-MAP abort - the scribe "
               "threw and there was no map-init handler to write the usual string. The game "
               "has bailed. Stopping." % m)
        return False
    w(out, "- 🔴 CANARY FAILED: Player.log carries %d `ErrorWhileLoadingGame`. The load "
           "ABORTED and the engine bailed; the process may still answer and report "
           "`game_loaded` while being half-disposed. NOTHING measured here would count. "
           "Stopping." % n)
    return False


def _played_tile_conflict(load_name, out):
    """PAINT_GUARD_ASK_EACH_TIME_1. -> sorted list of tile ids this run's own
    TILES.csv is about to overwrite that ALSO carry a generated local Map in
    the campaign save - or [] if there is nothing to protect (no save, no
    overlap). Reads the save named by --load if one was given (the file this
    run just loaded), else the default frozen campaign save; neither read
    touches the bridge.
    """
    save_path = (os.path.join(_SAVES_DIR, load_name + ".rws") if load_name
                 else save_played_tiles.default_save_path(_SAVES_DIR))
    played, used = save_played_tiles.played_tiles(save_path)
    if not played:
        w(out, "- paint guard: %s"
             % ("no campaign save found - nothing to protect" if used is None
                else "%s carries no generated local maps - nothing to protect" % used))
        return []

    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    rows = read_csv(TILES)
    if rows is None:
        w(out, "- ⚠️ paint guard: %s missing — cannot check for a conflict, and this run "
               "would write the whole planet blind. Run ashkarr_paint.py first." % TILES)
        return sorted(played)  # fail closed: treat every played tile as a conflict

    writing = {int(r["tile"]) for r in rows}
    conflict = sorted(played & writing)
    if conflict:
        w(out, "- paint guard: %s has %d generated map(s); %d of them are in this run's "
               "own write set (%s)" % (used, len(played), len(conflict), TILES))
    else:
        w(out, "- paint guard: %s has %d generated map(s), none in this run's write set - "
               "clean pass" % (used, len(played)))
    return conflict


def _ask_or_refuse(conflict, out, despite):
    """The actual "question it has to ask right before it writes over a savegame
    tilemap location, each time" (owner, PAINT_GUARD_ASK_EACH_TIME_1). Every
    conflicting tile is named. Non-interactive (no tty on stdin) NEVER prompts -
    it refuses outright with the tile list, exactly per the item's own rule,
    because a hung prompt in a non-interactive run is worse than a refusal.
    """
    if not conflict:
        return True
    w(out, "- 🔴 **%d tile(s) with a live colony are in this run's write set: %s.**"
         % (len(conflict), ", ".join(str(t) for t in conflict)))
    w(out, "  Painting over a tile with a generated map moves the ground out from under "
           "it - RimWorld cannot reconcile the two, and the colony on it does not survive "
           "the mismatch. (Owner, 2026-08-26: \"it doesn't destroy the game. Just the "
           "colony.\") `--despite-map` skips this check entirely, every run.")
    if despite:
        w(out, "  !! `--despite-map` given — proceeding over %d tile(s) anyway." % len(conflict))
        return True
    if not sys.stdin.isatty():
        w(out, "  Non-interactive: REFUSING rather than prompting. Pass `--despite-map` to "
               "proceed, or run interactively to be asked.")
        return False
    try:
        ans = input("  Proceed and overwrite %d tile(s) with a live colony? [y/N] "
                     % len(conflict)).strip().lower()
    except EOFError:
        ans = ""
    if ans == "y":
        w(out, "  confirmed interactively — proceeding over %d tile(s)." % len(conflict))
        return True
    w(out, "  declined — stopping.")
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write for real; default is a dry run")
    ap.add_argument("--load", default=None, help="load this save first and wait for it")
    ap.add_argument("--report", default=None)
    ap.add_argument("--skip-links", action="store_true")
    # PAINT_GUARD_ASK_EACH_TIME_1 (2026-08-30): this used to be a BLANKET refuse -
    # any map anywhere on the planet, whether or not this run's own write set ever
    # touched it. It is now a per-tile question, asked every run
    # (_played_tile_conflict/_ask_or_refuse below): only a played tile actually in
    # TILES.csv's write set triggers it. `--despite-map` still skips the question
    # entirely, same as before.
    ap.add_argument("--despite-map", action="store_true",
                    help="skip the played-tile guard entirely and write over any colony "
                         "tile in this run's write set without asking. THIS WILL DESTROY "
                         "THAT COLONY - the paint moves the ground out from under a map "
                         "already generated from it, and RimWorld cannot reconcile the two "
                         "(owner, 2026-08-26: \"it doesn't destroy the game, just the "
                         "colony\"). Only for a colony nobody keeps.")
    ap.add_argument("--despite-abort", action="store_true",
                    help="proceed even though the load aborted. Records it loudly in the "
                         "report. Only justified when the WORLD layer has been shown to be "
                         "readable and the abort is downstream of it.")
    ap.add_argument("--inputs", default=None, metavar="DIR",
                    help="stamp from DIR/ASHKARR_WORLDMAP_{tiles,links,settlements,mutators,landmarks}.csv "
                         "instead of the frozen record in world/ (G7). All five must exist. The record "
                         "is never written either way.")
    ap.add_argument("--feature-def", default=None,
                    help="FeatureDef stage 6 imports the region labels under. Default: the one def "
                         "named by DIR/ASHKARR_WORLDMAP_features.csv under --inputs, else %s."
                         % FEATURE_DEF_DEFAULT)
    ap.add_argument("--check-inputs", action="store_true",
                    help="validate the stamp files offline and exit; no bridge, no game")
    a = ap.parse_args(argv)
    apply = bool(a.apply)

    report = a.report or os.path.join(REPO, "infrastructure", "output",
                                      "w9_run_%s.md" % time.strftime("%Y-%m-%d_%H%M"))
    out = ["# W9 run - %s (%s)" % (time.strftime("%Y-%m-%d %H:%M"), "APPLY" if apply else "DRY"), ""]

    feature_def = a.feature_def
    if a.inputs:
        if not os.path.isdir(a.inputs):
            print("--inputs %s: not a directory" % a.inputs)
            return 12
        set_inputs(a.inputs)
        feature_def = feature_def or inputs_feature_def(a.inputs)
        w(out, "- inputs: `%s` (not the record in world/)" % os.path.abspath(a.inputs))
    feature_def = feature_def or FEATURE_DEF_DEFAULT
    w(out, "- stage 6 featureDef: `%s`" % feature_def)
    probs = check_inputs(out)
    for p in probs:
        w(out, "- 🔴 input: %s" % p)
    if a.check_inputs:
        w(out, "- check-inputs: %s" % ("FAIL" if probs else "ok (offline only - the stamp itself needs a world)"))
        return 13 if probs else 0
    if probs and a.inputs:
        # The record path keeps its old tolerance (stages 4/4b report a missing file and
        # carry on); a bundle passed by hand must be whole.
        w(out, "- 🔴 --inputs bundle is incomplete. Stopping before the bridge.")
        return 13

    host, port, token = resolve_endpoint()
    if not token:
        print("No bridge token in Player.log - is the game running?")
        return 2

    with RimBridge(host, port, token) as rb:
        if a.load:
            w(out, "- loading save `%s`" % a.load)
            rb.call("rimworld/load_game", {"saveName": a.load})

    # A load tears the connection down; poll the POSTcondition on fresh sockets.
    if a.load:
        for _ in range(120):
            try:
                host, port, token = resolve_endpoint()
                with RimBridge(host, port, token) as rb:
                    if rb.call("rimworld/get_game_info", {}).get("status") == "game_loaded":
                        break
            except Exception:
                pass
            time.sleep(5)

    host, port, token = resolve_endpoint()
    # 🔴 The report/screenshot write used to sit AFTER this whole `with` block, so
    # every early `return` below (paint-guard refusal, no game loaded, canary
    # failure, tile-count mismatch) skipped it entirely -- precisely the cases
    # most worth a persisted record (which tiles were at risk, what the canary
    # actually said) left only stdout and no file. `finally` guarantees the
    # report is written on every exit path, early return included.
    try:
      with RimBridge(host, port, token) as rb:
        gi = rb.call("rimworld/get_game_info", {})
        w(out, "- status `%s`, ticks %s, maps %s" % (gi.get("status"), gi.get("ticksGame"), gi.get("mapCount")))

        # PAINT_GUARD_ASK_EACH_TIME_1 (2026-08-30, owner: "This should be a question
        # it has to ask right before it writes over a savegame tilemap location, each
        # time"). Repainting a planet underneath a live map is what killed two saves
        # and about two cold loads on 2026-08-18: the map was generated from its
        # tile's biome, and moving that biome out from under it desyncs the two
        # permanently. Owner, 2026-08-26: "What it can do is destroy the player
        # colony, it doesn't destroy the game. Just the colony." Superseded from a
        # blanket "any map anywhere -> refuse" into a per-tile question: only a
        # played tile actually in THIS run's own write set (TILES.csv) triggers it.
        conflict = _played_tile_conflict(a.load, out)
        if not _ask_or_refuse(conflict, out, a.despite_map):
            return 5
        world_screen = False
        if gi.get("status") != "game_loaded":
            # 2026-10-20 remake S8: the runbook stamps at Page_SelectStartingSite (no map yet),
            # where get_game_info THROWS ("Specified cast is not valid", Find.MapUI null —
            # rimworld-world-editing §0). The world_* tools reach Find.WorldGrid there, so a
            # fresh world at the landing-site page counts as loaded: hasCurrentGame + that page.
            us = rb.call("rimworld/get_ui_state", {})
            st = us.get("state") or {}
            wins = " ".join(str(x.get("type")) for x in (us.get("windows") or []) if isinstance(x, dict))
            if st.get("hasCurrentGame") and "Page_SelectStartingSite" in wins:
                w(out, "- world screen: hasCurrentGame, Page_SelectStartingSite open (no map) -> stamping a fresh world")
                world_screen = True
            else:
                w(out, "- 🔴 no game loaded. Stopping.")
                return 2
        # ⏳ The abort is written AFTER `status` flips to game_loaded, so checking
        # immediately reads a clean log and passes a broken load. Measured twice
        # on 2026-08-20: canary passed at t+0 and failed at t+60 on the same load.
        time.sleep(20)
        if not canary(rb, out):
            if not a.despite_abort:
                w(out, "  (pass --despite-abort to proceed anyway, if the world layer has been "
                       "shown to read back correctly and the abort is downstream of it)")
                return 3
            w(out, "- ⚠️ **PROCEEDING ANYWAY (--despite-abort).** Everything below is PROVISIONAL "
                   "and must be re-proven by a save→reload before it is believed. The abort is "
                   "in a Harmony POSTFIX on ResolveAllCrossReferences, i.e. downstream of the "
                   "engine's own cross-reference resolution, which is why the world layer still "
                   "reads back correctly.")

        wi = rb.call("jawa/world_info_get", {})
        info = wi.get("info") or {}
        w(out, "- world `%s`, seed `%s`, coverage %s, **%s tiles**"
             % (info.get("name"), info.get("seedString"), info.get("planetCoverage"), wi.get("tilesCount")))
        if wi.get("tilesCount") != EXPECT_TILES:
            w(out, "- 🔴 tile count is %s, expected %s. A tile id means a different PLACE on a "
                   "different subdivision - importing here paints the wrong planet. Stopping."
                 % (wi.get("tilesCount"), EXPECT_TILES))
            return 4

        # ---- stage 1: tiles ------------------------------------------------
        r = rb.call("jawa/world_tile_import", {"path": TILES, "apply": apply, "expectTiles": EXPECT_TILES})
        w(out, "- **stage 1 tiles**: success=%s rows=%s applied=%s skipped=%s unknownBiomes=%s"
             % (r.get("success"), r.get("rows"), r.get("applied"), r.get("skipped"), r.get("unknownBiomes")))
        if not r.get("success"):
            w(out, "- 🔴 stage 1 tiles FAILED — every later stage assumes this one landed. Stopping.")
            return 6

        # ---- stage 2: links (rivers then roads, file order matters) --------
        if not a.skip_links:
            links_path, ok_order = mouth_first_links(out)
            if not ok_order:
                w(out, "- 🔴 stage 2 links: river order refused. Stopping.")
                return 7
            r = rb.call("jawa/world_links_import", {"path": links_path, "apply": apply,
                                                    "expectTiles": EXPECT_TILES, "clearFirst": True})
            w(out, "- **stage 2 links**: success=%s %s"
                 % (r.get("success"), json.dumps({k: v for k, v in r.items()
                                                  if k in ("rows", "rivers", "roads", "unknownDefs", "message")},
                                                 ensure_ascii=False)[:220]))
            if not r.get("success"):
                w(out, "- 🔴 stage 2 links FAILED. Stopping.")
                return 7

        # ---- stage 3: clear the marine mutators the repaint stranded -------
        au = rb.call("jawa/world_mutators_audit", {"limit": 5000})
        offs = [o["tile"] for o in (au.get("offenders") or [])]
        if len(offs) != (au.get("offenderCount") or 0):
            w(out, "- ⚠️ stage 3: audit returned %d of %s offenders - TRUNCATED, refusing a partial fix"
                 % (len(offs), au.get("offenderCount")))
        elif not offs:
            w(out, "- **stage 3 mutators**: nothing stale (0 offenders)")
        elif apply:
            done = 0
            for i in range(0, len(offs), 1000):
                chunk = offs[i:i + 1000]
                rr = rb.call("jawa/world_mutators_set", {"action": "remove", "mutators": "Coast",
                                                        "tiles": ",".join(map(str, chunk)), "readBack": 2})
                if not rr.get("success"):
                    w(out, "- 🔴 stage 3 chunk failed: %s" % str(rr.get("message"))[:120])
                    break
                done += len(chunk)
            after = rb.call("jawa/world_mutators_audit", {"limit": 1}).get("offenderCount")
            w(out, "- **stage 3 mutators**: removed stale `Coast` from %d tile(s); offenders now %s" % (done, after))
        else:
            w(out, "- stage 3 mutators (dry): would clear stale `Coast` from %d tile(s)" % len(offs))

        # ---- stage 3b: the 49 vanilla landmark leftovers -------------------
        # Bay, Cove, VEE_CoralReef, VEE_DriftwoodShore on a world that is 8.1% water
        # with no forest upstream. They are worldgen fossils that no longer match the
        # repainted biomes, and they must go BEFORE ours are placed: AddLandmark refuses
        # a tile that already holds one, silently.
        lg = rb.call("jawa/world_landmarks_get", {"limit": 5000})
        existing = [l.get("tile") for l in (lg.get("landmarks") or []) if l.get("tile") is not None]
        if not existing:
            w(out, "- **stage 3b leftovers**: none present")
        elif apply:
            rr = rb.call("jawa/world_landmarks_set",
                         {"action": "remove", "tiles": ",".join(map(str, existing)), "checkValid": False})
            w(out, "- **stage 3b leftovers**: success=%s removed %s of %d"
                 % (rr.get("success"), rr.get("removed"), len(existing)))
            if not rr.get("success"):
                w(out, "- 🔴 stage 3b leftover removal FAILED — stage 4 refuses a tile that "
                       "already holds a landmark. Stopping.")
                return 8
        else:
            w(out, "- stage 3b leftovers (dry): would remove %d" % len(existing))

        # ---- stage 4: landmarks --------------------------------------------
        # 🔴 BEFORE settlements. LandmarkDef.IsValidTile refuses a settlement tile and
        # every tile adjacent to one — but AddLandmark never calls it, so nothing stops
        # us and nothing reports it. ashkarr_populate.py already refused those tiles;
        # checkValid=True here is the second instrument, and its verdict is recorded.
        lmk = read_csv(LMKS)
        if lmk is None:
            w(out, "- ⚠️ **stage 4 landmarks**: %s is missing — run ashkarr_populate.py" % LMKS)
        else:
            by_def = {}
            for r in lmk:
                by_def.setdefault(r["landmark"], []).append(r["tile"])
            added, invalid = 0, []
            for ldef, tl in sorted(by_def.items()):
                if not apply:
                    continue
                rr = rb.call("jawa/world_landmarks_set",
                             {"action": "add", "def": ldef, "tiles": ",".join(tl), "checkValid": True})
                if not rr.get("success"):
                    w(out, "- 🔴 stage 4 `%s` failed: %s" % (ldef, str(rr.get("message"))[:140]))
                    continue
                added += rr.get("added") or 0
                for v in (rr.get("validity") or []):
                    if not v.get("isValidTile"):
                        invalid.append("%s@%s%s" % (ldef, v.get("tile"),
                                                    " (settlement)" if v.get("settlementAtOrAdjacent") else ""))
            if apply:
                w(out, "- **stage 4 landmarks**: added %d of %d across %d defs"
                     % (added, len(lmk), len(by_def)))
                if invalid:
                    w(out, "  - ⚠️ engine called %d tile(s) invalid and placed them anyway: %s"
                         % (len(invalid), ", ".join(invalid[:8])))
            else:
                w(out, "- stage 4 landmarks (dry): would add %d across %d defs — %s"
                     % (len(lmk), len(by_def), ", ".join("%s×%d" % (k, len(v)) for k, v in sorted(by_def.items()))))

        # ---- stage 4a: strip every mutator the input does not hold --------
        # Frozen-world rule (parity U2): the engine rolled ~28,600 mutators at worldgen and
        # AddLandmark rolls more in stage 4; stage 3 clears only stale Coast, 4b only adds.
        # KEEP_DERIVED (RM_SeaCoast) is geography-derived and stays.
        mut = read_csv(MUTS)
        if mut is None:
            w(out, "- ⚠️ **stage 4a strip**: no mutators input - nothing to compare against, "
                   "nothing stripped")
        else:
            try:
                live = read_live_mutators(rb, wi.get("tilesCount") or EXPECT_TILES)
            except RuntimeError as e:
                w(out, "- 🔴 stage 4a: live mutator read failed (%s). Stopping." % e)
                return 14
            strip = rolled_mutators(live, stamp_mutator_entries(mut))
            nstrip = sum(len(v) for v in strip.values())
            kept = sum(1 for _, d in live if d in KEEP_DERIVED)
            if not apply:
                w(out, "- stage 4a strip (dry): would remove %d rolled entr(ies) over %d def(s) of %d live; "
                       "keep %d KEEP_DERIVED" % (nstrip, len(strip), len(live), kept))
            else:
                gone = 0
                for name, tl in sorted(strip.items()):
                    for i in range(0, len(tl), 1000):
                        chunk = tl[i:i + 1000]
                        rr = rb.call("jawa/world_mutators_set",
                                     {"action": "remove", "mutators": name,
                                      "tiles": ",".join(map(str, chunk)), "readBack": 2})
                        if not rr.get("success"):
                            w(out, "- 🔴 stage 4a `%s` chunk failed: %s" % (name, str(rr.get("message"))[:140]))
                            return 14
                        gone += len(chunk)
                left = rolled_mutators(read_live_mutators(rb, wi.get("tilesCount") or EXPECT_TILES),
                                       stamp_mutator_entries(mut))
                w(out, "- **stage 4a strip**: removed %d rolled entr(ies) over %d def(s); kept %d "
                       "KEEP_DERIVED; rolled entries left on read-back: %d"
                     % (gone, len(strip), kept, sum(len(v) for v in left.values())))

        # ---- stage 4b: the derived mutators --------------------------------
        # 🔴 AFTER landmarks, because AddLandmark also rolls the def's own mutatorChances
        # onto its tile; running ours first would let that roll land on top.
        if mut is None:
            w(out, "- ⚠️ **stage 4b mutators**: %s is missing — run ashkarr_populate.py" % MUTS)
        else:
            by_mut = {}
            for r in mut:
                for name in (r["mutators"] or "").split(";"):
                    if name:
                        by_mut.setdefault(name, []).append(r["tile"])
            if not apply:
                w(out, "- stage 4b mutators (dry): would add %s"
                     % ", ".join("%s×%d" % (k, len(v)) for k, v in sorted(by_mut.items())))
            else:
                tot = 0
                for name, tl in sorted(by_mut.items()):
                    done = 0
                    for i in range(0, len(tl), 1000):
                        chunk = tl[i:i + 1000]
                        rr = rb.call("jawa/world_mutators_set",
                                     {"action": "add", "mutators": name,
                                      "tiles": ",".join(chunk), "readBack": 2})
                        if not rr.get("success"):
                            w(out, "- 🔴 stage 4b `%s` chunk failed: %s" % (name, str(rr.get("message"))[:140]))
                            break
                        done += len(chunk)
                    tot += done
                    w(out, "    - %-12s %d tile(s)" % (name, done))
                w(out, "- **stage 4b mutators**: %d placements over %d tiles" % (tot, len(mut)))
                # ⭐ The Oasis mutator whitelists Desert/ExtremeDesert only, and our oasis
                # tiles are ZBiome_DesertOasis. Reading the count back is what proves
                # AddMutator ignores biomeWhitelist — do not take the success flag for it.
                if "Oasis" in by_mut:
                    sample = by_mut["Oasis"][:200]
                    chk = rb.call("jawa/world_mutators_get",
                                  {"tiles": ",".join(sample), "limit": len(sample)})
                    # ⚠️ `mutators` is a list of OBJECTS ({def,label,genOrder}), not names.
                    hits = sum(1 for t in (chk.get("tiles") or [])
                               if any((m or {}).get("def") == "Oasis" for m in (t.get("mutators") or [])))
                    w(out, "  - ⭐ Oasis read-back: %d of %d sampled tiles carry it "
                           "(0 ⇒ AddMutator DOES honour biomeWhitelist and the patch is needed)"
                         % (hits, len(sample)))

        # ---- stage 5: settlements ------------------------------------------
        r = rb.call("jawa/world_settlements_import", {"path": SETTS, "apply": apply,
                                                     "expectTiles": EXPECT_TILES, "clearExisting": True})
        w(out, "- **stage 5 settlements**: success=%s %s"
             % (r.get("success"), str(r.get("message") or r.get("note"))[:200]))
        for ref in (r.get("refused") or [])[:5]:
            w(out, "    - refused: %s" % json.dumps(ref, ensure_ascii=False)[:170])
        if not r.get("success"):
            w(out, "- 🔴 stage 5 settlements FAILED. Stopping before regions/commit.")
            return 9

        # ---- stage 6: named regions ----------------------------------------
        # 'Region' is NOT a real FeatureDef - that name came from the authoring
        # pipeline. WB_MapLabelFeature is Worldbuilder's arbitrary map label and
        # is what these names actually are (71 as of 2026-08-23, not the 23 this
        # line used to claim — see the module docstring).
        fargs = {"path": TILES, "apply": apply, "expectTiles": EXPECT_TILES,
                 "featureDef": feature_def}
        if os.path.isfile(FEATS):
            # Canonical label size and centre by name (parity U1). Needs the companion built
            # 2026-10-20 or later; what an older DLL does with the extra argument is UNMEASURED,
            # so the read-back below says when the result carries no size counts.
            fargs["featuresPath"] = FEATS
        r = rb.call("jawa/world_features_import", fargs)
        if fargs.get("featuresPath"):
            w(out, "  - labels by name from %s: sizes %s, centres %s, off-region %s, unmatched rows %s"
                 % (os.path.basename(FEATS), r.get("sizesApplied", r.get("sizesByName")),
                    r.get("centresApplied", r.get("centresByName")), r.get("centresOffRegion"),
                    r.get("featureRowsWithNoRegion")))
            if r.get("success") and "sizesApplied" not in r and "sizesByName" not in r:
                w(out, "  - 🔴 the result has no size counts: the deployed companion predates "
                       "featuresPath, so label sizes/centres were COMPUTED, not canonical")
        w(out, "- **stage 6 regions**: success=%s %s" % (r.get("success"), str(r.get("message") or r.get("note"))[:200]))
        if not r.get("success"):
            w(out, "- 🔴 stage 6 regions FAILED. Stopping before commit.")
            return 10

        # ---- commit, lint, look --------------------------------------------
        if apply:
            commit_ok = rb.call("jawa/world_commit", {}).get("success")
            w(out, "- world_commit: %s" % commit_ok)
            if not commit_ok:
                w(out, "- 🔴 world_commit FAILED — nothing above this line is guaranteed to be "
                       "on the live world. The lint/screenshot below may be reading stale state.")
                return 11
        li = rb.call("jawa/world_lint", {"limit": 4})
        w(out, "- **lint**: %s" % li.get("verdict"))
        for name, chk in (li.get("checks") or {}).items():
            n = chk.get("count") if isinstance(chk, dict) else None
            if n:
                w(out, "    - %s: %s" % (name, n))
        w(out, "- stats: %s" % rb.call("jawa/world_stats", {}).get("message"))

        if apply and world_screen:
            # 🔴 2026-10-20: `jawa/clear_ui {all:true}` CLOSES Page_SelectStartingSite, which drops
            # the fresh world (it lives only in Current.CreatingWorld until landing; it cannot be
            # saved there). It cost remake generation #1. At the world screen: no UI calls at all.
            w(out, "- world screen: skipped world_view/clear_ui/screenshot (clear_ui would close the "
                   "landing page and discard the unsaved world). Render from the first save instead.")
        elif apply:
            rb.call("jawa/world_view", {"show": True, "altitude": 1100, "northUp": True})
            rb.call("jawa/clear_ui", {"all": True})
            shot = rb.call("rimworld/take_screenshot", {})
            w(out, "- 🔭 **LOOK AT THIS**: %s" % shot.get("path"))
            w(out, "  compare against `world/view/ASHKARR_WORLDMAP.biome.equirect.png` - every defect "
                   "that has mattered in this work passed its numeric check while the picture was wrong.")

    finally:
        d = os.path.dirname(report)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with io.open(report, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out))
        print("\nreport -> " + report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
