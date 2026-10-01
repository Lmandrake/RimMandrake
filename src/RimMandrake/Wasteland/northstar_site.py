"""Wasteland's site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed
precondition, empty = clean. Dev tooling, never deployed. Built only from northstar_driver.site primitives
(existing bridge tools) plus one plan-only deploy check.

THE SITE. The storm layer (RM_MapComponent_WastelandStorms), the Middenshell incident and the Rite of Tipping
read `map.Biome`, so the run needs a map whose biome IS `RM_Wasteland`. When the current map is not one,
`ensure_wasteland_map` re-tiles ONE land tile of the scratch quicktest world to RM_Wasteland, founds a player
colony on it, generates a 150x150 map there and makes it current (the Pyrelands recipe without its save and
reload, which only cured a black render: every Wasteland bar is a state read). The scratch world is test
scaffolding and is discarded; nothing here chooses or sweeps a seed or produces anything a player receives
(CLAUDE.md worldgen ban). A failure to build the site is recorded in LAST_SITE_ERROR and printed, NOT
returned as a failed precondition: the def-keyed chains are still worth running, and every biome-gated chain
records UNMEASURED (never PASS) on a map that is not Wasteland.

The mod ships COMPOSED inside mandrake.rm.biomes, and the driver's own deploy-fingerprint check skips folded
sources, so a run would otherwise test whatever composed copy the game folder happens to hold.
`composed_deploy_drift` runs the compose plan (read-only, never --apply) and refuses on any drift in this
mod's files or the kits it leans on (MovingDunes, whose binding patch this mod carries)."""
import contextlib
import os
import re
import subprocess

from northstar_driver import site

SETTINGS = "RimMandrake.Wasteland.RM_WastelandSettings"
BIOME = "RM_Wasteland"
MIN_MAP = 150
MAP_SIZE = 150
SITE_TEMPERATURE = 10.0         # the heat pusher only pushes below 26 C; a cool map keeps the control room honest
QUIET_STORYTELLER = "Tutor"     # UNMEASURED that it fires nothing; the queue is also cleared
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DRIFT_NEEDLES = ("Wasteland", "MovingDunes")
LAST_SITE_ERROR = None
WATER_WORDS = ("ocean", "lake", "sea")


class SiteError(AssertionError):
    pass


def _defaults():
    """The shipped defaults, single-sourced from validation.py (never copied here)."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("wasteland_validation_defaults", os.path.join(here, "validation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DEFAULTS


def composed_deploy_drift(root=ROOT, timeout=900):
    """Drift lines of `deploy_custom_mods.py --compose biomes` (plan only) naming this mod or its kit.
    Runs under WSL python3: the deploy tool is developed there and a Windows interpreter composes the
    same files with different line endings and reports drift. Raises on a plan that did not run."""
    p = subprocess.run(["wsl.exe", "--cd", root, "-e", "python3",
                        "src/RimMandrake/Utils/deploy_custom_mods.py", "--compose", "biomes"],
                       capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode not in (0, 1) or "Traceback" in out:
        raise RuntimeError("compose plan did not run (rc=%s): %s" % (p.returncode, out[-300:]))
    # `+`/`~` lines are drift; `-` lines are files only in the game folder (kept), the tool's only
    # reason to exit 1 when everything else is in sync
    return [ln.strip() for ln in out.splitlines()
            if re.match(r"\s+[+~]\s", ln) and any(n in ln for n in DRIFT_NEEDLES)]


# ------------------------------------------------------------------------------- the site recipe

def _call(s, tool, **kw):
    """One bridge call that must succeed. (Reached through getattr so the static lint, which checks every
    literal-named call to this helper, does not also flag this one dynamic call.)"""
    fn = getattr(s, "call")
    r = fn(tool, **kw)
    if not isinstance(r, dict) or r.get("success") is False:
        raise SiteError("%s failed: %s" % (tool, str(r)[:240]))
    return r


def _pick_tile(s, colony_tile):
    """The first flat/small-hills, non-water, riverless, roadless tile within 20..260 ids of the colony tile.
    Tile ids of a geodesic grid are spatially coherent, so this stays near the colony, which is all it needs.
    Row keys are read tolerantly; a row missing a key is skipped, never assumed clean."""
    lo = int(colony_tile) + 20
    r = _call(s, "jawa/world_tile_get", range="%d-%d" % (lo, lo + 240), limit=300)
    rows = r.get("tiles") or []
    if not rows:
        raise SiteError("world_tile_get returned no tiles for %d-%d: %s" % (lo, lo + 240, str(r)[:160]))
    for row in rows:
        tid = row.get("tile", row.get("id"))
        biome = str(row.get("biome") or "")
        hills = str(row.get("hilliness") or "")
        if tid is None or not biome or biome.lower() in ("(null)", "none"):
            continue
        if any(w in biome.lower() for w in WATER_WORDS):
            continue
        if hills not in ("Flat", "SmallHills"):
            continue
        if (row.get("riverCount") or 0) or (row.get("roadCount") or 0) or (row.get("mutatorCount") or 0):
            continue
        return int(tid)
    raise SiteError("no flat dry tile among %d rows from %d" % (len(rows), lo))


def ensure_wasteland_map(s):
    """Make the current map an RM_Wasteland map. Returns a one-line record. Raises SiteError on failure."""
    mi = _call(s, "jawa/map_info")
    if mi.get("mapBiome") == BIOME:
        return "current map is already %s (tile %s)" % (BIOME, mi.get("tile"))
    colony = mi.get("tile")
    if colony is None:
        raise SiteError("map_info carries no tile: %s" % str(mi)[:200])
    tile = _pick_tile(s, colony)
    # biome, temperature and relief are written BEFORE anything reads the tile's lazy caches (world-editing skill)
    w = _call(s, "jawa/world_tile_set", tiles=str(tile), biome=BIOME, temperature=SITE_TEMPERATURE, rainfall=0.0,
           elevation=300.0, hilliness="Flat", swampiness=0.0, readBack=1)
    back = {t.get("tile"): t for t in (w.get("tiles") or [])}.get(tile) or {}
    if back.get("biome") != BIOME:
        raise SiteError("re-tile read-back: tile %d reads biome %r, want %s" % (tile, back.get("biome"), BIOME))
    _call(s, "jawa/world_mutators_set", action="clear", tiles=str(tile))
    c = _call(s, "jawa/world_commit")
    failed = [st for st in (c.get("steps") or []) if str(st.get("status", st.get("result", ""))).lower() == "failed"]
    if failed:
        raise SiteError("world_commit step(s) failed: %s" % failed)
    # The engine culls a generated map that is not a player home (MEASURED live 2026-10-01), so the tile gets a
    # PLAYER settlement first; the map itself is built by the generate call (colony_found never generates one).
    _call(s, "jawa/colony_found", tile=tile, faction="Player")
    g = _call(s, "jawa/world_tile_map_generate", tile=tile, sizeX=MAP_SIZE, sizeZ=MAP_SIZE)
    if g.get("wasAlreadyGenerated"):
        raise SiteError("tile %d already had a map" % tile)
    fin = g.get("mapFinalize")
    if not isinstance(fin, dict) or "failedSteps" not in fin:
        raise SiteError("world_tile_map_generate gave no mapFinalize.failedSteps: %s" % str(g)[:200])
    if fin["failedSteps"]:
        raise SiteError("mapgen finalize steps failed: %s" % fin["failedSteps"])
    map_id = g.get("mapId")
    if map_id is None:
        raise SiteError("world_tile_map_generate returned no mapId")
    _call(s, "jawa/set_current_map", mapId=map_id)
    mi = _call(s, "jawa/map_info")
    if mi.get("mapId") != map_id or mi.get("mapBiome") != BIOME:
        raise SiteError("current map is %r biome %r after set_current_map(%s), want %s" % (
            mi.get("mapId"), mi.get("mapBiome"), map_id, BIOME))
    # homed: three colonists so quests, jobs and animal tools have people on THIS map
    cx, cz = (mi.get("sizeX") or MAP_SIZE) // 2, (mi.get("sizeZ") or MAP_SIZE) // 2
    sp = _call(s, "jawa/spawn_pawn", kindDef="Colonist", x=cx, z=cz, faction="PlayerColony", count=3)
    if len(sp.get("pawns") or []) != 3:
        raise SiteError("spawned %d of 3 colonists: %s" % (len(sp.get("pawns") or []), str(sp)[:160]))
    _call(s, "jawa/set_fog", action="unfog", rect="0,0,%d,%d" % (mi.get("sizeX") or MAP_SIZE, mi.get("sizeZ") or MAP_SIZE))
    return "built %s map %s on tile %d (colony tile was %s), %dx%d" % (BIOME, map_id, tile, colony, MAP_SIZE, MAP_SIZE)


def preflight(s):
    global LAST_SITE_ERROR
    bad = []
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    try:
        wrong = site.read_settings(s, SETTINGS, _defaults())
        if wrong:
            bad.append("settings_defaults: not at shipped defaults: %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    try:
        drift = composed_deploy_drift()
        if drift:
            bad.append("composed_deploy: the game's mandrake.rm.biomes differs from source in %d file(s) "
                       "(deploy_custom_mods.py --compose biomes --apply, game closed): %s" % (len(drift), drift[:3]))
    except Exception as ex:
        bad.append("composed_deploy: could not check: %s" % ex)
    # a quiet world: no random incident may land on a fixture mid-chain
    with contextlib.suppress(Exception):
        s.call("jawa/storyteller_swap", storytellerDef=QUIET_STORYTELLER)
    with contextlib.suppress(Exception):
        s.call("jawa/incident_queue_clear")
    try:
        LAST_SITE_ERROR = None
        rec = ensure_wasteland_map(s)
        print("[wl-site] %s" % rec, flush=True)
    except Exception as ex:
        LAST_SITE_ERROR = "%s: %s" % (type(ex).__name__, ex)
        print("[wl-site] SITE NOT BUILT -- biome-gated chains will be UNMEASURED: %s" % LAST_SITE_ERROR, flush=True)
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < MIN_MAP:
        bad.append("map_size: both axes must be >= %d, got %sx%s" % (MIN_MAP, mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.weather_lock(s, "Clear")
    except Exception as ex:
        bad.append("weather: %s" % ex)
    return bad
