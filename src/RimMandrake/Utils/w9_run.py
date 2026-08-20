"""w9_run.py - stamp the authored planet onto a live world, in the order that works.

    python.exe src/RimMandrake/Utils/w9_run.py --dry
    python.exe src/RimMandrake/Utils/w9_run.py --apply
    python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_gen_sub7b

🔴 WINDOWS `python.exe`. The bridge is on Windows loopback; WSL cannot reach it.

WHY A SCRIPT AND NOT A CHECKLIST. The stage ORDER is not a preference - §12 of the W9
spec has mutators clearing after the biome repaint and features last, because each stage
invalidates assumptions the previous one made. Driving it by hand means re-deciding the
order every time and getting it wrong once.

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

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")
SETTS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")
EXPECT_TILES = 21872


def w(out, line):
    out.append(line)
    print(line)


PLAYER_LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"


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
    n = log.count("ErrorWhileLoadingGame")
    if n == 0:
        w(out, "- canary: no `ErrorWhileLoadingGame` in Player.log -> the load finished")
        return True
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
        if gi.get("status") != "game_loaded":
            w(out, "- 🔴 no game loaded. Stopping.")
            return 2
        if not canary(rb, out):
            return 3

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
