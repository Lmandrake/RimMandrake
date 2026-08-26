"""first_light.py - everything worth knowing about a fresh load, in one command.

    python.exe src/RimMandrake/Utils/first_light.py
    python.exe src/RimMandrake/Utils/first_light.py --report out.md

🔴 RUN IT WITH WINDOWS `python.exe`, NEVER WSL `python3`. RimBridge binds Windows
loopback and WSL2 is a separate network namespace, so python3 gets an empty token
and ConnectionRefusedError - no route, not a timeout.

WHY THIS EXISTS. A cold load on the full mod list costs ~25 minutes, and the
questions worth asking of a fresh process are always the same ones. Asking them by
hand costs twenty minutes of the window and the answers land in a chat log rather
than a file. This asks all of them in about a minute and writes the answers down.

WHAT IT IS NOT. It does not change anything. Every call here is a read. The one
thing it will not do is decide - a red line is a finding to look at, not a verdict.
"""
import argparse
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import PLAYER_LOG as _PLAYER_LOG  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES_CSV = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
PLAYER_LOG = _PLAYER_LOG

# The count the deployed assembly carries. Read it off the DLL rather than
# trusting a literal here -- but a literal is still useful as a "did the deploy
# take" tripwire, because a LOW count means the bundle did not load, not that a
# tool is missing.
EXPECT_JAWA_AT_LEAST = 112


def section(out, title):
    out.append("")
    out.append("## " + title)


# PAWNKIND_AUDIT_TAGLESS_BLIND_1. `jawa/pawnkind_audit` (the companion tool)
# already splits tagless kinds into a deliberate-civilian bucket and a
# `taglessButLooksLikeAFighter` bucket -- a combat role (isFighter or
# combatPower >= 40) that carries no weaponTags field at all, which is
# indistinguishable from a civilian by tag count alone and is how three of
# our own authored kinds (Jawa_Droid_Leader, Jawa_Droid_Specialist,
# Jawa_TradeMoot_Specialist) hid in the civilian exclusion while broken.
# 🔑 first_light.py used to just echo `pk["message"]` and list example rows
# for cannotAfford/emptyTagPool only -- the tagless-fighter suspects were in
# the payload (`counts.taglessButLooksLikeAFighter`, and the row list itself)
# but never surfaced as their own line or their own named rows. This pulls
# the section-building logic into a standalone function precisely so a
# scratch test can feed it a fabricated pk payload without a live bridge.
def format_pawnkind_section(pk):
    """Given a jawa/pawnkind_audit response dict, return (lines, headline_bits)."""
    lines = []
    headline_bits = []
    c = pk.get("counts") or {}
    lines.append("- %s" % pk.get("message"))
    lines.append("- weapon pairs in game: %s, distinct weapon tags: %s" %
                 (pk.get("weaponPairsInGame"), pk.get("distinctWeaponTags")))

    broken = c.get("emptyTagPool", 0) + c.get("cannotAfford", 0)
    if broken:
        headline_bits.append("%d kinds cannot arm" % broken)
    for row in (pk.get("cannotAfford") or [])[:40]:
        lines.append("  - `%s` money max %s, cheapest `%s` at %s -> raise max to %s" %
                     (row.get("kind"), row.get("weaponMoneyMax"),
                      row.get("cheapestEligible"), row.get("cheapestPrice"),
                      row.get("raiseMaxTo")))
    for row in (pk.get("emptyTagPool") or [])[:20]:
        lines.append("  - `%s` tags %s match NO loaded weapon" % (row.get("kind"), row.get("tags")))

    # ⛔ NOT folded into `broken` and NOT into the civilian exclusion either --
    # it is its own reported line, per PAWNKIND_AUDIT_TAGLESS_BLIND_1's verify
    # condition. A kind here is a SUSPECT, not a proven defect (a pure melee
    # brawler can legitimately carry no ranged tags), so a human reads the
    # named rows rather than the count alone driving a headline verdict.
    tagless_fighters = c.get("taglessButLooksLikeAFighter", 0)
    if tagless_fighters:
        headline_bits.append("%d kinds intend to fight and carry no weaponTags at all" % tagless_fighters)
        lines.append("- ⚠️ %d kinds intend to fight (isFighter or combatPower >= 40) and carry NO "
                     "weaponTags at all -- a combat role that lost its tags, not a deliberate "
                     "civilian:" % tagless_fighters)
        for row in (pk.get("taglessButLooksLikeAFighter") or [])[:40]:
            lines.append("  - `%s` isFighter=%s combatPower=%s" %
                         (row.get("kind"), row.get("isFighter"), row.get("combatPower")))

    return lines, headline_bits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=os.path.join(REPO, "infrastructure", "output",
                                                     "first_light_%s.md" % time.strftime("%Y-%m-%d_%H%M")))
    ap.add_argument("--skip-texture", action="store_true",
                    help="skip the texture sweep, which is the slow one")
    a = ap.parse_args()

    host, port, token = resolve_endpoint()
    if not token:
        print("No bridge token in Player.log. Is the game running?")
        return 2

    out = ["# First light - %s" % time.strftime("%Y-%m-%d %H:%M"), ""]
    headline = []

    # A token in Player.log proves a PAST launch, not a live one -- the log
    # outlives the process. So a connection refusal here is the normal "game is
    # down" case and deserves one line, not a traceback.
    try:
        rb_ctx = RimBridge(host, port, token)
        rb_ctx.__enter__()
    except Exception as ex:
        print("bridge not answering on %s:%s - the game is down, or RimBridgeServer is off."
              % (host, port))
        print("  (%s)" % str(ex).split(" - ")[0])
        return 2

    with rb_ctx as rb:
        # ---- 1. is anything home -------------------------------------------
        gi = rb.call("rimworld/get_game_info", {})
        tools = [t.get("name") for t in (rb._request("tools/list", {}).get("tools") or [])]
        jawa = sorted(n for n in tools if n and n.startswith("jawa/"))
        section(out, "Process")
        out.append("- status `%s`, ticksGame %s, maps %s" %
                   (gi.get("status"), gi.get("ticksGame"), gi.get("mapCount")))
        out.append("- %d tools, %d `jawa/`" % (len(tools), len(jawa)))
        if len(jawa) < EXPECT_JAWA_AT_LEAST:
            out.append("- 🔴 **only %d `jawa/` tools, expected at least %d.** A LOW count means the "
                       "companion bundle did not load, not that one tool is missing. 0 means it did "
                       "not load at all." % (len(jawa), EXPECT_JAWA_AT_LEAST))
            headline.append("companion short by %d tools" % (EXPECT_JAWA_AT_LEAST - len(jawa)))
        if gi.get("status") != "game_loaded":
            out.append("- ⚠️ no game loaded; the world and map checks below will be skipped.")

        # 🔴 THE ZOMBIE CANARY — and it reads the LOG, not the debug tree.
        # A save can abort mid-load, the engine's own bail handler can throw, and
        # the process then reports `game_loaded` and answers every call for hours
        # while half-disposed. Measured 2026-08-20.
        # ⚠️ An earlier version of this check asked whether the debug `Actions`
        # tree enumerated. That was WRONG IN BOTH DIRECTIONS: the tree reports few
        # or no VISIBLE children when no map is loaded, and it enumerated fine on
        # a game that had definitely aborted. `ErrorWhileLoadingGame` is written
        # by the engine only when it has given up on a load.
        try:
            with io.open(PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
                _log = fh.read()
            _n = _log.count("ErrorWhileLoadingGame")
            if _n:
                out.append("- 🔴 **THE LOAD ABORTED** — Player.log carries %d "
                           "`ErrorWhileLoadingGame`. The process may still say `game_loaded` "
                           "and answer every call while being half-disposed. Nothing measured "
                           "on it counts. Find the exception above that line." % _n)
                headline.append("LOAD ABORTED — game is a zombie")
            else:
                out.append("- load finished cleanly (no `ErrorWhileLoadingGame`)")
        except Exception as _e:
            out.append("- ⚠️ could not read Player.log for the abort check: %s" % _e)

        # ---- 2. can every pawn kind arm itself ------------------------------
        section(out, "Pawn kinds that cannot arm themselves")
        try:
            pk = rb.call("jawa/pawnkind_audit", {"limit": 200})
            lines, headline_bits = format_pawnkind_section(pk)
            out.extend(lines)
            headline.extend(headline_bits)
        except Exception as e:
            out.append("- audit failed: %s" % e)

        # ---- 3. dead texture paths ------------------------------------------
        if not a.skip_texture:
            section(out, "Dead texture paths")
            try:
                tx = rb.call("jawa/texture_audit", {"limit": 200})
                out.append("- %s (%s ms)" % (tx.get("message"), tx.get("elapsedMs")))
                if tx.get("missingCount"):
                    headline.append("%d dead texPaths" % tx.get("missingCount"))
                for row in (tx.get("missing") or [])[:60]:
                    out.append("  - `%s` (%s) %s -> `%s`" %
                               (row.get("def"), row.get("mod"), row.get("graphic"), row.get("texPath")))
            except Exception as e:
                out.append("- sweep failed: %s" % e)

        # ---- 4. the world ----------------------------------------------------
        if gi.get("status") == "game_loaded":
            section(out, "World")
            try:
                wi = (rb.call("jawa/world_info_get", {}) or {}).get("info") or {}
                out.append("- `%s`, seed `%s`, coverage %s, %s tiles" %
                           (wi.get("name"), wi.get("seedString"),
                            wi.get("planetCoverage"), rb.call("jawa/world_info_get", {}).get("tilesCount")))
                st = rb.call("jawa/world_stats", {})
                out.append("- %s" % st.get("message"))
            except Exception as e:
                out.append("- world info failed: %s" % e)

            if os.path.exists(TILES_CSV):
                try:
                    v = rb.call("jawa/world_tile_validate", {"path": TILES_CSV})
                    out.append("- authored tiles: matched %s / %s (%s%%)" %
                               (v.get("matched"), v.get("rows"), v.get("matchPct")))
                    if (v.get("matchPct") or 0) < 100:
                        headline.append("tiles %.1f%% match" % (v.get("matchPct") or 0))
                except Exception as e:
                    out.append("- tile validate failed: %s" % e)

            section(out, "World lint")
            try:
                li = rb.call("jawa/world_lint", {"limit": 6})
                out.append("- %s" % li.get("verdict"))
                for name, chk in (li.get("checks") or {}).items():
                    n = chk.get("count") if isinstance(chk, dict) else None
                    if n:
                        out.append("  - **%s: %s** - %s" % (name, n, str(chk.get("note"))[:150]))
                if li.get("totalFindings"):
                    headline.append("lint %s" % li.get("totalFindings"))
            except Exception as e:
                out.append("- lint failed: %s" % e)

    out.append("")
    out.append("---")
    out.append("_Every call above is a read. Nothing here changed the game._")

    d = os.path.dirname(a.report)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(a.report, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))

    print("first light: " + ("; ".join(headline) if headline else "nothing flagged"))
    print("report -> " + a.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
