"""w9_run.py - stamp the authored planet onto a live world, in the order that works.

    python.exe src/RimMandrake/Utils/w9_run.py                 DRY RUN - the default
    python.exe src/RimMandrake/Utils/w9_run.py --apply         write for real
    python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_gen

    ⚠️ There is NO `--dry`. This block claimed one until 2026-08-21 and argparse
    refused it; the dry run is what you get by passing nothing. The real flags are
    --apply, --load, --report, --skip-links, --despite-map, --despite-abort.

🔴 WINDOWS `python.exe`. The bridge is on Windows loopback; WSL cannot reach it.

WHY A SCRIPT AND NOT A CHECKLIST. The stage ORDER is not a preference - §12 of the W9
spec has mutators clearing after the biome repaint and features last, because each stage
invalidates assumptions the previous one made. Driving it by hand means re-deciding the
order every time and getting it wrong once.

THE STAGES, and the two ordering rules that are engine facts rather than taste:
    1   tiles            biome + scalars
    2   links            rivers mouth-first, then roads
    3   mutators, clear  the marine ones the repaint stranded
    3b  landmarks, clear the 49 vanilla worldgen leftovers
    4   landmarks, add   🔴 BEFORE settlements - IsValidTile refuses a settlement tile
                            and its neighbours, and AddLandmark ignores that verdict
    4b  mutators, add    🔴 AFTER landmarks - AddLandmark also rolls the def's own
                            mutatorChances onto its tile, on top of whatever is there
    5   settlements
    6   features         the region labels — ⚠️ 71 as of 2026-08-23, not the 23 this
                         line used to claim. Verify the stage handles all of them.
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

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")
SETTS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")
MUTS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_mutators.csv")
LMKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_landmarks.csv")
EXPECT_TILES = 21872


def read_csv(path):
    """Rows as dicts, or None if the file was never authored.

    ⚠️ Returns None rather than [] on a missing file, because an empty stage and an
    unauthored stage must not report the same thing. A stage that silently does nothing
    is the failure mode this whole run exists to avoid.
    """
    if not os.path.isfile(path):
        return None
    import csv as _csv
    with io.open(path, encoding="utf-8") as fh:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write for real; default is a dry run")
    ap.add_argument("--load", default=None, help="load this save first and wait for it")
    ap.add_argument("--report", default=None)
    ap.add_argument("--skip-links", action="store_true")
    # 🔴 The help text carries the MEASURED OUTCOME, not a caution. Someone reading
    # `--help` to decide whether to pass this flag never sees the refusal message
    # below, which is where the evidence used to live exclusively.
    ap.add_argument("--despite-map", action="store_true",
                    help="proceed with a map instantiated. THIS WILL DESTROY THE CURRENT "
                         "COLONY - make a new one and carry on. That much is agreed "
                         "and expected: the paint moves the ground out from under a "
                         "map already generated from it. \u26a0 A 2026-08-21 session ALSO "
                         "reported the game then refusing to make a new colony and the "
                         "UI losing its icons - the OWNER DISPUTES THAT (2026-08-23: he "
                         "has since painted under a colony and carried on fine), it was "
                         "never reproduced, and it must not be quoted as settled. "
                         "The paint itself was faithful - seven tiles "
                         "read back exact - so this is not a painting bug: it is moving "
                         "the ground out from under a map already generated from it, "
                         "which RimWorld cannot reconcile. Only for a world nobody keeps, "
                         "and everything measured afterwards is unattributable.")
    ap.add_argument("--despite-abort", action="store_true",
                    help="proceed even though the load aborted. Records it loudly in the "
                         "report. Only justified when the WORLD layer has been shown to be "
                         "readable and the abort is downstream of it.")
    a = ap.parse_args()
    apply = bool(a.apply)

    report = a.report or os.path.join(REPO, "infrastructure", "output",
                                      "w9_run_%s.md" % time.strftime("%Y-%m-%d_%H%M"))
    out = ["# W9 run - %s (%s)" % (time.strftime("%Y-%m-%d %H:%M"), "APPLY" if apply else "DRY"), ""]

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
    with RimBridge(host, port, token) as rb:
        gi = rb.call("rimworld/get_game_info", {})
        w(out, "- status `%s`, ticks %s, maps %s" % (gi.get("status"), gi.get("ticksGame"), gi.get("mapCount")))

        # 🔴 NO MAP MAY EXIST. W9's spec says "assert and REFUSE loudly:
        # Find.CurrentMap == null", and until 2026-08-21 this file only PRINTED the
        # count — the assertion existed in prose and nowhere in code. Repainting a
        # planet underneath a live map is what killed two saves and about two cold
        # loads on 2026-08-18: the map was generated from its tile's biome, and moving
        # that biome out from under it desyncs the two permanently.
        # ⚠️ The deeper cost is ATTRIBUTION. With a map up, a defect in the picture
        # cannot be told apart from map-desync, so the run proves nothing either way.
        if (gi.get("mapCount") or 0) > 0 and not a.despite_map:
            w(out, "- 🔴 **%s map(s) are instantiated.** This run requires a world and NO map. "
                   "Generate a world and stop at the landing-site page. Regenerating costs "
                   "a minute or two, not a reload — the mod load is already paid for.\n"
                   "  🔴 `--despite-map` proceeds anyway, and IT WILL DESTROY THIS COLONY. "
                   "That is agreed and expected - the paint moves the ground out from under a "
                   "map already generated from it, and RimWorld cannot reconcile the two. Make "
                   "a new colony and carry on.\n"
                   "  ✅ A COLONY is the whole cost. Owner, 2026-08-26: \"What it can do is "
                   "destroy the player colony, it doesn't destroy the game. Just the colony.\" "
                   "The 2026-08-21 report of a game refusing to make a new colony and a UI "
                   "losing its icons is STRUCK as disproven, and the item that carried it is "
                   "dropped. Do not quote it.\n"
                   "  The paint itself was faithful - seven tiles read back exact."
                 % gi.get("mapCount"))
            return 5
        if gi.get("status") != "game_loaded":
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

        # ---- stage 2: links (rivers then roads, file order matters) --------
        if not a.skip_links:
            r = rb.call("jawa/world_links_import", {"path": LINKS, "apply": apply,
                                                    "expectTiles": EXPECT_TILES, "clearFirst": True})
            w(out, "- **stage 2 links**: success=%s %s"
                 % (r.get("success"), json.dumps({k: v for k, v in r.items()
                                                  if k in ("rows", "rivers", "roads", "unknownDefs", "message")},
                                                 ensure_ascii=False)[:220]))

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
            w(out, "- **stage 3b leftovers**: removed %s of %d" % (rr.get("removed"), len(existing)))
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

        # ---- stage 4b: the derived mutators --------------------------------
        # 🔴 AFTER landmarks, because AddLandmark also rolls the def's own mutatorChances
        # onto its tile; running ours first would let that roll land on top.
        mut = read_csv(MUTS)
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

        # ---- stage 6: named regions ----------------------------------------
        # 'Region' is NOT a real FeatureDef - that name came from the authoring
        # pipeline. WB_MapLabelFeature is Worldbuilder's arbitrary map label and
        # is what these 23 names actually are.
        r = rb.call("jawa/world_features_import", {"path": TILES, "apply": apply,
                                                   "expectTiles": EXPECT_TILES,
                                                   "featureDef": "WB_MapLabelFeature"})
        w(out, "- **stage 6 regions**: success=%s %s" % (r.get("success"), str(r.get("message") or r.get("note"))[:200]))

        # ---- commit, lint, look --------------------------------------------
        if apply:
            w(out, "- world_commit: %s" % rb.call("jawa/world_commit", {}).get("success"))
        li = rb.call("jawa/world_lint", {"limit": 4})
        w(out, "- **lint**: %s" % li.get("verdict"))
        for name, chk in (li.get("checks") or {}).items():
            n = chk.get("count") if isinstance(chk, dict) else None
            if n:
                w(out, "    - %s: %s" % (name, n))
        w(out, "- stats: %s" % rb.call("jawa/world_stats", {}).get("message"))

        if apply:
            rb.call("jawa/world_view", {"show": True, "altitude": 1100, "northUp": True})
            rb.call("jawa/clear_ui", {"all": True})
            shot = rb.call("rimworld/take_screenshot", {})
            w(out, "- 🔭 **LOOK AT THIS**: %s" % shot.get("path"))
            w(out, "  compare against `world/view/ASHKARR_WORLDMAP.biome.equirect.png` - every defect "
                   "that has mattered in this work passed its numeric check while the picture was wrong.")

    d = os.path.dirname(report)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(report, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("\nreport -> " + report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
