"""modcheck.bland_world -- a featureless test world, set up once and kept that way. Reusable by any suite.

    import bland_world
    info = bland_world.setup(session)                 # once per game: found + generate + clean a bland tile map
    rep  = bland_world.reset(session)                 # between suites/chains: re-establish and PROVE blandness
    probs = bland_world.assert_world(session)         # verification only; [] == bland

The recipe is the measured bland_tile one (NORTHSTAR_BLAND_TILE_1, 2026-10-01): export tiles -> Flat dry 15-30 C tiles with
no mutators/roads/rivers -> colony_found (skipping tiles an earlier call in this game already settled) ->
world_tile_map_generate -> set_current_map -> destroy_bulk factionlessAnimals -> destroy the map-gen ruins
(destroy_batch) -> spawn colonists -> close the naming dialog. `reset` is what a suite runner calls between suites
instead of relaunching the game: it removes everything a hazard job or a previous suite left behind (hostiles,
wildlife, strangers, corpses, fires, queued incidents, injuries, hunger) and then READS the world back, so the
caller gets a list of residual problems rather than a promise.

Nothing here returns success it did not read back (rimbridge skill: a bridge call that reports success can change
nothing). Every step reports what it found before and after.
"""
import csv
import os
import tempfile

import helpers as H

DRY_BIOMES = ("AridShrubland", "Desert")
NAMING_DIALOG = "Dialog_NamePlayer"       # colony-naming prompts: re-raised every ~600 ticks until named, harmless
NATURAL_SCENERY = ("SteamGeyser",)         # in the BuildingArtificial group but indestructible and not a ruin
HINT_TILE = 4375


class BlandWorldError(RuntimeError):
    """The bland world could not be built or restored; the caller must treat its chains as UNMEASURED."""


def candidates(rows, hint=HINT_TILE):
    out = []
    for r in rows:
        try:
            if (r.get("hilliness") == "Flat" and r.get("biome") in DRY_BIOMES and float(r.get("swampiness") or 0) == 0
                    and 0 <= float(r.get("elevation") or -1) < 400 and 15 <= float(r.get("temperature") or -99) <= 30):
                out.append(int(r.get("tile") if r.get("tile") is not None else r.get("index")))
        except (TypeError, ValueError):
            continue
    if hint in out:
        out.remove(hint)
        out.insert(0, hint)
    return out


def close_naming_dialogs(session):
    """Housekeeping only: never a verdict. (detectors.modal_open already ignores these prompts.)"""
    try:
        r = session.call("jawa/window_list_close", action="close", typeName=NAMING_DIALOG, closeAll=True)
        return int(r.get("closedCount") or 0)
    except Exception:                                            # noqa: BLE001
        return 0


def ruins(session):
    """Non-player artificial buildings on the current map (map-gen ruins), natural scenery excluded.
    Returns (rows, complete)."""
    lt = session.call("jawa/list_things", group="BuildingArtificial", limit=2000)
    if not lt.get("success"):
        raise BlandWorldError("ruin census failed: %s" % lt.get("message"))
    rows = [t for t in lt.get("things") or []
            if (t.get("factionName") or t.get("faction")) in (None, "", "None") and t.get("def") not in NATURAL_SCENERY]
    return rows, lt.get("isCompleteList", True)


def destroy_ruins(session, passes=5):
    """Cell-by-cell destroy_batch until the census is empty or `passes` run out. Returns (left, destroyed_total)."""
    total = 0
    left, complete = ruins(session)
    for _ in range(passes):
        if not left:
            break
        rects = ";".join("%d,%d,1,1" % (t["x"], t["z"]) for t in left)
        r = session.call("jawa/destroy_batch", rects=rects, categories="Building,Item")
        if r.get("success"):
            total += len(left)
        left, complete = ruins(session)
    return left, total


def corpses(session):
    r = session.call("jawa/list_things", group="Corpse", limit=2000)
    if not r.get("success"):
        raise BlandWorldError("corpse census failed: %s" % r.get("message"))
    return r.get("things") or []


def destroy_corpses(session, passes=3):
    """Corpses are Things, not pawns, so destroy_batch can remove them. Returns (left, destroyed_total)."""
    total = 0
    left = corpses(session)
    for _ in range(passes):
        if not left:
            break
        rects = ";".join("%d,%d,1,1" % (t["x"], t["z"]) for t in left)
        r = session.call("jawa/destroy_batch", rects=rects, categories="Item")
        if r.get("success"):
            total += len(left)
        left = corpses(session)
    return left, total


def queued_incidents(session):
    r = session.call("jawa/incident_queue_peek")
    if not r.get("success"):
        raise BlandWorldError("incident_queue_peek failed: %s" % r.get("message"))
    return r.get("incidents") or r.get("entries") or r.get("queue") or []


def feed_colonists(session, floor=0.25):
    """Top up Food for colonists below `floor` (starvation is the one slow hazard a food-less bland map really has:
    MEASURED 2026-10-01, Malnutrition aborted five long chains). Only a colonist that is LOW is touched, so a suite
    that measures needs still sees its own effects. Returns the ids fed."""
    fed = []
    for row in H.read_pawns(session, health=False):
        if not H.is_colonist(row) or row.get("dead") or not row.get("spawned", True):
            continue
        try:
            needs = dict((x["need"], x["level"]) for x in session.call("jawa/pawn_need", pawn=row["id"],
                                                                         action="list").get("needs") or [])
        except Exception:                                        # noqa: BLE001
            continue
        if needs.get("Food", 1.0) < floor:
            session.call("jawa/pawn_need", pawn=row["id"], action="need", need="Food", level=1.0)
            fed.append(row["id"])
    return fed


def assert_world(session, expected_ids=(), ruins_too=False):
    """Verification only. helpers.assert_bland PLUS what a hazard job leaves: corpses, ruins, queued incidents,
    injured or hungry colonists. Returns a list of problems; [] == provably bland."""
    problems = list(H.assert_bland(session, expected_ids))
    exp = set(expected_ids)
    try:
        c = [t for t in corpses(session) if t.get("id") not in exp]
        if c:
            problems.append("corpses present: %d" % len(c))
        if ruins_too:         # only meaningful on a map built by setup(): map-gen scenery is not hazard residue
            r, complete = ruins(session)
            if r:
                problems.append("ruins present: %d" % len(r))
        q = queued_incidents(session)
        if q:
            problems.append("incidents queued: %d" % len(q))
    except BlandWorldError as e:
        problems.append("UNMEASURED: %s" % e)
    for row in H.read_pawns(session, health=True):
        if H.is_colonist(row) and not row.get("dead") and row["id"] not in exp:
            hs = [h["def"] for h in row["health"]["hediffs"] if h["def"] in H.INJURY_DEFS]
            if hs:
                problems.append("colonist %s carries %s" % (row["id"], hs[:4]))
    return problems


def reset(session, expected_ids=(), resurrect=True):
    """Re-establish the bland world between suites, then prove it. Returns
    {"bland": bool, "problems": [...], "steps": {...}}. Does not touch settings (the Watch's
    SettingsTransaction owns storyteller/difficulty); it removes the CONSEQUENCES of the previous run."""
    steps = {}
    steps["dialogs_closed"] = close_naming_dialogs(session)
    for h in (H.kill_hostiles, H.kill_wildlife, H.clear_strangers):
        r = h(session, expected_ids)
        steps[r.name] = {"acted": r.acted, "verified": r.verified, "residue": r.residue}
    try:
        steps["incident_queue_cleared"] = session.call("jawa/incident_queue_clear").get("clearedCount")
    except Exception as e:                                       # noqa: BLE001
        steps["incident_queue_cleared"] = "ERR %r" % (e,)
    left, n = destroy_corpses(session)
    steps["corpses_destroyed"] = n
    steps["corpses_left"] = len(left)
    r = H.extinguish(session)
    steps[r.name] = {"acted": r.acted, "verified": r.verified}
    start = dict((x["id"], set()) for x in H.read_pawns(session, health=False)
                 if H.is_colonist(x) and (resurrect or not x["dead"]) and x["id"] not in set(expected_ids))
    r = H.restore_colonists(session, start, resurrect=resurrect)
    steps[r.name] = {"acted": r.acted, "verified": r.verified, "residue": r.residue}
    r = H.restore_needs(session, [i for i in start])
    steps[r.name] = {"acted": r.acted, "verified": r.verified}
    problems = assert_world(session, expected_ids)
    return {"bland": not problems, "problems": problems, "steps": steps}


def setup(session, colonists=3, tmpdir=None, max_tiles=40, log=None):
    """Build the bland world. Leaves it as the CURRENT map. Returns
    {"tile","mapIndex","colonists":[ids],"ruins_destroyed","wildlife_destroyed","problems":[...]}.
    Raises BlandWorldError when no tile can be founded/generated (UNMEASURED, never a verdict on a mod)."""
    say = log or (lambda *_a: None)
    tmpdir = tmpdir or os.environ.get("TEMP") or tempfile.gettempdir()
    path = os.path.join(tmpdir, "bland_world_tiles.csv")
    r = session.call("jawa/world_tile_export", path=path)
    if not r.get("success") or not os.path.isfile(path):
        raise BlandWorldError("world_tile_export failed or wrote nothing: %s" % (r.get("message") or r))
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cands = candidates(rows)
    say("tiles exported", len(rows), "candidates", len(cands))
    if not cands:
        raise BlandWorldError("no Flat dry 15-30C tile in this world (%d tiles exported)" % len(rows))
    tile = None
    for t in cands[:max_tiles]:
        g = session.call("jawa/world_tile_get", tiles=str(t))
        row = (g.get("tiles") or [{}])[0]
        if not all(int(row.get(k) or 0) == 0 for k in ("mutatorCount", "roadCount", "riverCount")):
            continue
        cf = session.call("jawa/colony_found", tile=t, faction="Player", name="NorthstarBland")
        if not cf.get("success") and "already has" in str(cf.get("message")):
            continue                      # settled by an earlier setup() in this same game: pick another tile
        if not cf.get("success"):
            raise BlandWorldError("colony_found refused: %s" % cf.get("message"))
        tile = t
        break
    if tile is None:
        raise BlandWorldError("no unsettled bland tile among the first %d candidates" % max_tiles)
    close_naming_dialogs(session)
    g = session.call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement")
    if not g.get("success") or g.get("mapIndex") is None:
        raise BlandWorldError("world_tile_map_generate refused: %s" % (g.get("message") or g))
    failed = (g.get("mapFinalize") or {}).get("failedSteps") or []
    if failed:
        raise BlandWorldError("map finalize failed steps: %s" % failed)
    close_naming_dialogs(session)
    sc = session.call("jawa/set_current_map", mapId=g["mapIndex"])
    if not sc.get("success"):
        raise BlandWorldError("set_current_map refused: %s" % sc.get("message"))
    # nonColonists, not factionlessAnimals: MEASURED 2026-10-01 (tile 254) a fresh map also arrives with hostile-faction
    # insects (Locust, Spelopede, Megaspider). The colony's own pawns live on another map until spawned below.
    d = session.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    left, n_ruins = destroy_ruins(session)
    info = session.call("jawa/map_info")
    cx, cz = int(info.get("sizeX", 250)) // 2, int(info.get("sizeZ", 250)) // 2
    spawned = []
    for i in range(colonists):
        sp = session.call("jawa/spawn_pawn", kindDef="Colonist", x=cx + 2 * i, z=cz, faction="player", count=1)
        rows_ = sp.get("pawns") or []
        if sp.get("success") and rows_:
            spawned.append(rows_[0].get("id"))
    close_naming_dialogs(session)
    problems = assert_world(session, ruins_too=True)
    if len(spawned) < colonists:
        problems.append("only %d of %d colonists spawned" % (len(spawned), colonists))
    return {"tile": tile, "mapIndex": g["mapIndex"], "colonists": spawned, "ruins_destroyed": n_ruins,
            "wildlife_destroyed": d.get("matchedCount"), "ruins_left": len(left), "problems": problems}
