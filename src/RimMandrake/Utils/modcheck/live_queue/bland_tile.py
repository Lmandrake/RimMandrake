"""bland_tile NORTHSTAR_BLAND_TILE_1: a genuinely bland test map instead of the random quicktest forest.

The quicktest WORLD is regenerated every launch, so tile 4375 (bland on 2026-10-01) is only a hint: the tile is
re-chosen from a fresh world_tile_export every run and re-verified with world_tile_get.

Sequence: export tiles -> filter Flat + AridShrubland/Desert + swampiness 0 + elevation 0..400 + 15..30 C ->
world_tile_get (mutatorCount/roadCount/riverCount all 0) -> colony_found(tile) -> world_tile_map_generate(tile)
-> set_current_map(mapIndex) -> destroy_bulk factionlessAnimals (the map arrived with 47 wildlife on 10-01) ->
spawn 3 player colonists -> prove: census shows >=3 colonists on the map, no wildlife, no non-player artificial
buildings (ruins), helpers.assert_bland passes, and a 2000-tick Watch on it sees no SURPRISE/FATAL.
Leaves the bland map CURRENT, so companion_live/motion_frames run on it.
"""
import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Unmeasurable, call, main   # noqa: E402

HINT_TILE = 4375
DRY_BIOMES = ("AridShrubland", "Desert")


def candidates(rows):
    out = []
    for r in rows:
        try:
            if (r.get("hilliness") == "Flat" and r.get("biome") in DRY_BIOMES and float(r.get("swampiness") or 0) == 0
                    and 0 <= float(r.get("elevation") or -1) < 400 and 15 <= float(r.get("temperature") or -99) <= 30):
                out.append(int(r.get("tile") if r.get("tile") is not None else r.get("index")))
        except (TypeError, ValueError):
            continue
    if HINT_TILE in out:
        out.remove(HINT_TILE)
        out.insert(0, HINT_TILE)
    return out


def fake_world():
    from rimdrive.fake import FakeWorld, pawn_row
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103)])
    w.arrival_wildlife = 47
    return w


def body(s, job):
    import helpers as H
    from watch import Watch
    if not job.dry_run:        # a freshly launched game sits at the main menu: world_tile_export needs a world (bland_base, 2026-10-01)
        import runner
        job.note("map", runner.ensure_playing_map())
    tmpdir = os.environ.get("TEMP") or tempfile.gettempdir()     # python.exe: the Windows %TEMP% the game can write
    path = os.path.join(tmpdir, "lq_tiles.csv")
    r = call(s, "jawa/world_tile_export", path=path)
    if not r.get("success") or not os.path.isfile(path):
        raise Unmeasurable("world_tile_export failed or wrote nothing: %s" % (r.get("message") or r))
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cands = candidates(rows)
    job.note("tiles_exported", len(rows))
    job.note("candidates", len(cands))
    if not cands:
        raise Unmeasurable("no Flat dry 15-30C tile in this world (%d tiles exported)" % len(rows))
    tile, info, cf = None, None, {}
    for t in cands[:40]:
        g = call(s, "jawa/world_tile_get", tiles=str(t))
        row = (g.get("tiles") or [{}])[0]
        if not all(int(row.get(k) or 0) == 0 for k in ("mutatorCount", "roadCount", "riverCount")):
            continue
        cf = call(s, "jawa/colony_found", tile=t, faction="Player", name="NorthstarBland")
        if not cf.get("success") and "already has" in str(cf.get("message")):
            continue            # settled by an earlier run in this same game session: pick another tile
        tile, info = t, row
        break
    job.check("a candidate tile has no mutators, roads or rivers", tile is not None, cands[:12])
    if tile is None:
        return
    job.note("tile", info)
    job.check("colony_found settled the tile for the player", cf.get("success"), cf.get("message"))
    # colony_found opens Dialog_NamePlayerFactionAndSettlement (force-pause). MEASURED 2026-10-01: left open it makes
    # modal_open SURPRISE abort every later job's controls. Close it now, and again after map generation.
    def _close_name_dialog():
        return call(s, "jawa/window_list_close", action="close", typeName="Dialog_NamePlayerFactionAndSettlement",
                    closeAll=True)
    job.note("name_dialog_closed", _close_name_dialog().get("closedCount"))
    g = call(s, "jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement")
    job.note("map_generate", {k: g.get(k) for k in ("mapIndex", "mapParentDef", "wasAlreadyGenerated", "pawnCount",
                                                    "thingCount", "mapFinalize", "message")})
    if not g.get("success") or g.get("mapIndex") is None:
        raise Unmeasurable("world_tile_map_generate refused after colony_found: %s" % (g.get("message") or g))
    failed_steps = (g.get("mapFinalize") or {}).get("failedSteps") or []
    job.check("map generated with no failed finalize steps", not failed_steps, failed_steps)
    _close_name_dialog()
    sc = call(s, "jawa/set_current_map", mapId=g["mapIndex"])
    job.check("the new map is current and on the chosen tile",
              sc.get("success") and int(sc.get("tile", tile)) == tile, sc.get("message") or sc)
    d = call(s, "jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
    job.note("wildlife_destroyed", d.get("matchedCount"))
    job.check("destroy_bulk factionlessAnimals succeeded", d.get("success"), d.get("message"))
    info_ = call(s, "jawa/map_info")
    cx, cz = int(info_.get("sizeX", 250)) // 2, int(info_.get("sizeZ", 250)) // 2
    spawned = []
    for i in range(3):
        sp = call(s, "jawa/spawn_pawn", kindDef="Colonist", x=cx + 2 * i, z=cz, faction="player", count=1)
        rows_ = sp.get("pawns") or []
        if sp.get("success") and rows_:
            spawned.append(rows_[0].get("id"))
    job.note("colonists_spawned", spawned)
    cen = call(s, "jawa/pawn_census", faction="player")
    cols = [p for p in cen.get("pawns") or [] if p.get("isColonist")]
    job.check(">=3 colonists stand on the bland map (census isColonist)", len(cols) >= 3,
              [(p.get("id"), p.get("isColonist")) for p in (cen.get("pawns") or [])][:8])
    pawns = H.read_pawns(s, health=False)
    wild = [p["id"] for p in pawns if H.is_wildlife(p)]
    job.check("no wildlife left on the map", not wild, wild[:10])
    lt = call(s, "jawa/list_things", group="BuildingArtificial", limit=2000)
    # Ancient ruins are map-gen scenery (MEASURED 2026-10-01 live: 161 Wall/Urn/Table things on a fresh tile map).
    # A bland map removes them: destroy_batch the non-player artificial things cell by cell, then re-census.
    for _ in range(5):
        pre = [t for t in lt.get("things") or [] if (t.get("factionName") or t.get("faction")) in (None, "", "None")
               and t.get("def") != "SteamGeyser"]    # natural, indestructible scenery (MEASURED: 'non-destroyable'), not a ruin
        if not pre:
            break
        rects = ";".join("%d,%d,1,1" % (t["x"], t["z"]) for t in pre)
        db = call(s, "jawa/destroy_batch", rects=rects, categories="Building,Item")
        job.note("ruins_destroyed_pass", {"targeted": len(pre), "success": db.get("success"), "msg": str(db.get("message"))[:200]})
        lt = call(s, "jawa/list_things", group="BuildingArtificial", limit=2000)
    if not lt.get("success"):
        job.check("ruin census answered (list_things group=BuildingArtificial)", False, lt.get("message"))
    else:
        ruins = [t for t in lt.get("things") or [] if (t.get("factionName") or t.get("faction")) in (None, "", "None")
               and t.get("def") != "SteamGeyser"]    # natural, indestructible scenery (MEASURED: 'non-destroyable'), not a ruin
        job.note("ruins_sample", [(t.get("def"), t.get("x"), t.get("z")) for t in ruins[:15]])
        job.check("no non-player artificial buildings (ruins) on the map", not ruins and lt.get("isCompleteList", True),
                  "%d ruin things, complete=%s" % (len(ruins), lt.get("isCompleteList")))
    problems = H.assert_bland(s)
    job.check("helpers.assert_bland passes on the new map", not problems, problems)
    w = Watch(s, (cx, cz), os.path.join(job.outdir, "bland_watch"), mod="LiveQueue", chain="bland_idle",
              policy="record", chunk=500)
    with w:
        w.wait(None, 2000)
    serious = [h for h in w.seen_hits if h["severity"] in ("SURPRISE", "FATAL")]
    job.check("2000 idle ticks on the bland map raise no SURPRISE/FATAL", not serious, serious[:5])


if __name__ == "__main__":
    sys.exit(main("bland_tile", body, fake_builder=fake_world))
