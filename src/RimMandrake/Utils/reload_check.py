"""reload_check.py - load the painted world and read every decision string in one pass.

    python.exe src/RimMandrake/Utils/reload_check.py               # read only
    python.exe src/RimMandrake/Utils/reload_check.py --repush      # also re-push rain + rivers
    python.exe src/RimMandrake/Utils/reload_check.py --no-load     # a world is already loaded

🔴 WINDOWS `python.exe`. The bridge is on Windows loopback; WSL cannot reach it.

The strings and their expected values are `infrastructure/state/RELOAD_CHECK.md`, written
BEFORE the launch. This file only reads them back; it does not decide anything.

🔴 THE CANARY IS TWO STRINGS, NOT ONE. Measured 2026-08-21: `WORLDMAP_gen` aborted on
FactionControl's cross-ref postfix and bailed to the main menu while `ErrorWhileLoadingGame`
read ZERO — that handler fires on MAP init, and a save with no map dies in `FinalizeLoading`
with nothing to write the usual line. A canary that checks only the old string calls a dead
game healthy. This one checks both, and then reads `programState` back as a third instrument.
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

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")
WIN_TILES = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"
WIN_LINKS = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv"
PLAYER_LOG = (r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
              r"\RimWorld by Ludeon Studios\Player.log")
SAVE = "WORLDMAP_gen"
PROBE = [2476, 11350, 15087, 8147, 19495, 10, 12411]

out = []


def w(line):
    out.append(line)
    print(line)


def log_counts():
    try:
        with io.open(PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            s = fh.read()
    except Exception as e:
        return None, None, None, str(e)
    return (s.count("ErrorWhileLoadingGame"),
            s.count("Exception in FinalizeLoading"),
            s.count("WorldMaterials/BiomesKit"), None)


def rb():
    h, p, t = resolve_endpoint()
    return RimBridge(h, p, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repush", action="store_true", help="re-push rainfall + river grades")
    ap.add_argument("--no-load", action="store_true", help="a world is already loaded")
    ap.add_argument("--save", action="store_true",
                    help="save over WORLDMAP_gen after a successful re-push. Requires --repush.")
    a = ap.parse_args()

    w("# reload check - %s" % time.strftime("%Y-%m-%d %H:%M"))

    if not a.no_load:
        # ⏳ THE BRIDGE ANSWERING IS NOT THE GAME BEING DRIVABLE. Measured by the owner
        # 2026-08-14 and re-learned the hard way 2026-08-21: the game becomes reactive
        # about forty seconds after the bridge first responds, and a mutation issued
        # inside that window is accepted and never happens. A load_game issued seconds
        # after the bridge came up left the game at the main menu with a Player.log that
        # never grew by a single byte - no error, no abort, nothing to find.
        # Read-only calls are fine in that window; this is not one.
        w("- settling 45s before issuing a mutation")
        time.sleep(45)
        with rb() as s:
            st = s.call("rimworld/get_ui_state", {}).get("programState")
            w("- pre-load programState: %s" % st)
            w("- loading `%s`" % SAVE)
            s.call("rimworld/load_game", {"saveName": SAVE})
        loaded = False
        for _ in range(150):
            time.sleep(6)
            try:
                with rb() as s:
                    if s.call("rimworld/get_game_info", {}).get("status") == "game_loaded":
                        loaded = True
                        break
            except Exception:
                pass
        if not loaded:
            # ⛔ Distinguish "aborted" from "never started". A load that never dispatched
            # leaves the log UNCHANGED and no exception anywhere - it looks identical to a
            # healthy idle game, which is how it cost an hour.
            w("- 🔴 **NEVER REACHED `game_loaded`.** If Player.log did not grow, the call was "
              "accepted and never dispatched - not an abort. Re-issue after the game has "
              "settled; do not read this as the save being broken.")

    # ⏳ The abort is written AFTER status flips, so a read at t+0 passes a broken load.
    time.sleep(20)
    n_err, n_fin, n_bk, err = log_counts()
    w("- **1 canary**: ErrorWhileLoadingGame=%s  ExceptionInFinalizeLoading=%s%s"
      % (n_err, n_fin, ("  (log unreadable: %s)" % err) if err else ""))

    with rb() as s:
        gi = s.call("rimworld/get_game_info", {})
        ui = s.call("rimworld/get_ui_state", {})
        w("- **2 state**: status=%s maps=%s programState=%s hasCurrentGame=%s"
          % (gi.get("status"), gi.get("mapCount"), ui.get("programState"), ui.get("hasCurrentGame")))
        if gi.get("status") != "game_loaded" or (n_fin or 0) > 0 or (n_err or 0) > 0:
            w("- 🔴 **THE LOAD DID NOT SURVIVE.** Nothing below would be attributable. Stopping.")
            return 3

        wi = s.call("jawa/world_info_get", {})
        w("- **3 world**: `%s` seed `%s` coverage %s tiles **%s**"
          % ((wi.get("info") or {}).get("name"), (wi.get("info") or {}).get("seedString"),
             (wi.get("info") or {}).get("planetCoverage"), wi.get("tilesCount")))

        import csv as _csv
        rows = {int(r["tile"]): r for r in _csv.DictReader(io.open(TILES, encoding="utf-8"))}
        g = s.call("jawa/world_tile_get", {"tiles": ",".join(map(str, PROBE))})
        bad = 0
        for row in (g.get("tiles") or []):
            c = rows.get(row.get("tile")) or {}
            same = (c.get("biome") == row.get("biome")
                    and abs(float(c.get("temp_c") or 0) - float(row.get("temperature") or 0)) < 0.05)
            if not same:
                bad += 1
        w("- **4 spot-check**: %d of %d tiles match the CSV on biome and temperature"
          % (len(g.get("tiles") or []) - bad, len(g.get("tiles") or [])))

        w("- **5 landmarks**: %d" % len(s.call("jawa/world_landmarks_get", {"limit": 60}).get("landmarks") or []))
        feats = s.call("jawa/world_features_get", {"limit": 60}).get("features") or []
        biggest = max([f.get("maxDrawSizeInTiles") or 0 for f in feats] or [0])
        w("- **6 features**: %d, largest label %.1f tiles" % (len(feats), biggest))
        w("- **10 BiomesKit misses in this run's log**: %s" % n_bk)

        # ---- the four tools built 2026-08-21 -------------------------------
        r = s.call("jawa/tile_settleable", {})
        w("- **11 tile_settleable**: %s of %s settleable, %s refused"
          % (r.get("settleable"), r.get("tilesTested"), r.get("refused")))
        for br in (r.get("byReason") or [])[:6]:
            w("    - %5d  %s" % (br.get("count"), str(br.get("reason"))[:88]))

        r = s.call("jawa/tile_cache_audit", {})
        w("- **12 tile_cache_audit**: populated=%s disagreements=%s byMutator=%s **UNEXPLAINED STALE=%s**"
          % (r.get("hillinessCachePopulated"), r.get("disagreements"),
             r.get("explainedByMutator"), r.get("unexplainedStale")))

        r = s.call("jawa/biome_art_audit", {})
        w("- **13 biome_art_audit**: %s biomes, missing=%s %s"
          % (r.get("biomesReported"), r.get("missingCount"), r.get("missing")))

        r = s.call("jawa/faction_leader_get", {})
        w("- **14 faction_leader_get**: %s factions, ideo overrode def on %s"
          % (r.get("factions"), r.get("ideoOverrodeDefCount")))
        for row in (r.get("rows") or []):
            if row.get("defName") in ("Empire", "OutlanderCivil", "TribeCivil", "Pirate",
                                      "Jawa_IndigenousTribes"):
                w("    - %-22s %-26s effective=%-16s def=%s"
                  % (row.get("defName"), str(row.get("name"))[:26],
                     str(row.get("effectiveTitle"))[:16], row.get("defTitle")))

        if a.repush:
            r = s.call("jawa/world_tile_import", {"path": WIN_TILES, "apply": True, "expectTiles": 21872})
            w("- **8 rainfall re-push**: success=%s applied=%s unknownBiomes=%s"
              % (r.get("success"), r.get("applied"), r.get("unknownBiomes")))
            r = s.call("jawa/world_links_import", {"path": WIN_LINKS, "apply": True,
                                                   "expectTiles": 21872, "clearFirst": True})
            w("- **9 river re-push**: success=%s rivers=%s roads=%s unknownDefs=%s"
              % (r.get("success"), r.get("rivers"), r.get("roads"), r.get("unknownDefs")))
            w("- commit: %s" % s.call("jawa/world_commit", {}).get("success"))
            g = s.call("jawa/world_tile_get", {"tiles": "11965,19495,2540"})
            ok40 = 0
            for row in (g.get("tiles") or []):
                w("    - %s %s rainfall %s" % (row.get("tile"), row.get("biome"), row.get("rainfall")))
                try:
                    if abs(float(row.get("rainfall") or 0) - 40.0) < 0.5:
                        ok40 += 1
                except (TypeError, ValueError):
                    pass

            # ⛔ Saving is gated on the read-back, not on the import's success flag. An
            # import that reported success and moved nothing would otherwise be written
            # over the only copy of the painted world.
            if a.save:
                if ok40 == 3:
                    r = s.call("rimworld/save_game", {"saveName": SAVE})
                    w("- **save** over `%s`: %s" % (SAVE, r.get("success")))
                else:
                    w("- ⛔ **NOT SAVING**: the volcanic read-back is %d of 3 at 40mm, so the "
                      "re-push did not land. Saving now would overwrite the only painted "
                      "world with one that is no better." % ok40)

    path = os.path.join(REPO, "infrastructure", "output",
                        "reload_check_%s.md" % time.strftime("%Y-%m-%d_%H%M"))
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("\nreport -> " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
