#!/usr/bin/env python3
"""live_site.py -- make the running game show the scene a live proof reads: a map of one biome, or a named save.

    python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand [--temperature 30]
    python.exe src/RimMandrake/Utils/live_site.py --not-biome RM_LeaningScrub --biome RM_BlueDesert
    python.exe src/RimMandrake/Utils/live_site.py --save rm_proof_atmosphere

RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: the live stage ran HORIZON_CARAVAN_VANILLA_REFUSES_1's Stillsand probe on a
Leaning Scrub map eight times and LEANINGSCRUB_STALL_SHARED_MOVE_1's proof on the very biome its criteria exclude, while
nothing ever set the map up. A live_proofs/<ID>.txt line `live-site A1: <this command>` makes relentless_live run it,
bridge held, before the proof; a non-zero exit here is UNMEASURED ("site not prepared"), and the proof does not run.

--biome: the recipe proven live 2026-10-01 (Stillsand/validation.py site chain): jawa/world_tile_set on the current
tile, jawa/world_commit, the vanilla debug action `Actions\\Regenerate Current Map` (it honours the tile's CURRENT
biome), poll until a map is ready, read jawa/map_info back. A map already of that biome is left alone (no regen).
Regenerating wipes the map's colonists, so three are spawned at the centre and hostiles destroyed, as the site chain does.
The quicktest world is scaffolding (CLAUDE.md worldgen ban: nothing here makes a planet a player receives), and a game
past --max-ticks (default two in-game days) is refused: that is someone's colony, not a test map.

--save: rimworld/load_game, then wait for Playing with a map (validation_core._wait_playing's rule). Canonical saves
(infrastructure/state/canon.yml) load read-only by definition: this tool never saves.

Exit 0 the scene is up (read back), 2 it could not be made (UNMEASURED; never 1: a site is not a verdict).
Runs under Windows Python: RimBridge binds Windows loopback.
"""
import argparse
import os
import sys
import time

READY, NOT_READY = 0, 2
REGEN = "Actions\\Regenerate Current Map"


def need_regen(info, biome, not_biome):
    """map_info -> (verdict, why): "ok" the map already serves, "regen" make `biome`, "no" cannot. Pure."""
    have = info.get("mapBiome")
    if biome and have == biome:
        return "ok", "the current map is already %s" % biome
    if not biome and have and have not in not_biome:
        return "ok", "the current map is %s, not %s" % (have, "/".join(not_biome))
    if not biome:
        return "no", "the map is %s and no --biome names what to make instead" % have
    return "regen", "the current map is %s, %s wanted" % (have, biome)


def wait_ready(rb, budget_s=300, step_s=5):
    """Poll the bridge until a map is up: no `currentMapReady` key exists (measured 2026-10-07)."""
    t0 = time.time()
    while time.time() - t0 < budget_s:
        time.sleep(step_s)
        try:
            st = (rb.call("rimbridge/get_bridge_status", {}) or {}).get("state") or {}
        except Exception:      # noqa: BLE001  the call can drop while the map rebuilds: poll, never trust
            continue
        if st.get("automationReady") and st.get("currentMapId") and not st.get("longEventPending") \
                and st.get("programState") == "Playing":
            return True
    return False


def connect(timeout):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rimbridge_client as rc
    host, port, token = rc.resolve_endpoint(None, None, None, None)
    if not token:
        raise RuntimeError("no bridge token")
    return rc.RimBridge(host, port, token, timeout=timeout)


def biome_site(a):
    # 300 s: a timed-out mutation leaves an UNKNOWN-outcome marker that refuses every later write (the client's
    # guard), and Regenerate Current Map is the one call here slow enough to hit a short timeout.
    with connect(300) as rb:
        info = rb.call("jawa/map_info", {})
        if not isinstance(info, dict) or info.get("success") is False or info.get("tile") is None:
            print("NOT READY: no current map to make a site on (%s)" % str(info)[:200])
            return NOT_READY
        verdict, why = need_regen(info, a.biome, a.not_biome)
        if verdict != "regen":
            print(("READY: " if verdict == "ok" else "NOT READY: ") + why)
            return READY if verdict == "ok" else NOT_READY
        target = a.biome
        ticks = int((rb.call("jawa/time_clock", {}) or {}).get("ticksGame") or 0)
        if ticks > a.max_ticks:
            print("NOT READY: the game is at tick %d (> %d): a colony, not a test map; no regen" % (ticks, a.max_ticks))
            return NOT_READY
        print("site: %s; tile %s" % (why, info["tile"]))
        args = {"tiles": str(info["tile"]), "biome": target}
        if a.temperature is not None:
            args["temperature"] = a.temperature
        r = rb.call("jawa/world_tile_set", args)
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: world_tile_set refused: %s" % str(r)[:300])
            return NOT_READY
        r = rb.call("jawa/world_commit", {})
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: world_commit refused: %s" % str(r)[:300])
            return NOT_READY
        try:
            rb.call("rimworld/execute_debug_action", {"path": REGEN})
        except Exception as e:      # noqa: BLE001  the connection may drop while the map rebuilds
            print("regen call ended: %s" % str(e)[:200])
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: no map %ds after %s" % (a.budget, REGEN))
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        if info.get("mapBiome") != target:
            print("NOT READY: the regenerated map is %r, not %s" % (info.get("mapBiome"), target))
            return NOT_READY
        cx, cz = (info.get("sizeX") or 0) // 2, (info.get("sizeZ") or 0) // 2
        try:     # the regenerated map has no colonists; a proof that wants them says so, the site is up either way
            rb.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": cx, "z": cz, "faction": "player", "count": 3})
            rb.call("rimworld/execute_debug_action", {"path": "Actions\\Destroy hostile pawns"})
        except Exception as e:      # noqa: BLE001
            print("colonists not spawned: %s" % str(e)[:200])
        print("READY: map %s on tile %s, %sx%s, 3 colonists at %d,%d" % (target, info.get("tile"), info.get("sizeX"),
                                                                        info.get("sizeZ"), cx, cz))
        return READY


def save_site(a):
    with connect(120) as rb:
        r = rb.call("rimworld/load_game", {"saveName": a.save})
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: load_game %s refused: %s" % (a.save, str(r)[:300]))
            return NOT_READY
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: %s did not reach Playing with a map in %ds" % (a.save, a.budget))
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        print("READY: %s loaded, map %s tick %s" % (a.save, info.get("mapBiome"), info.get("ticksGame")))
        return READY


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", help="BiomeDef the current map must be")
    ap.add_argument("--not-biome", action="append", default=[], help="a BiomeDef the map must not be (repeatable)")
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--save", help="a save name to load (no .rws)")
    ap.add_argument("--max-ticks", type=int, default=120000)
    ap.add_argument("--budget", type=int, default=300)
    a = ap.parse_args(argv)
    if bool(a.save) == bool(a.biome or a.not_biome):
        ap.error("give --save, or --biome / --not-biome")
    try:
        return save_site(a) if a.save else biome_site(a)
    except Exception as e:      # noqa: BLE001  any bridge failure is a site not made, never a verdict
        print("NOT READY: %s: %s" % (type(e).__name__, str(e)[:300]))
        return NOT_READY


if __name__ == "__main__":
    sys.exit(main())
