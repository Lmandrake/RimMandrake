#!/usr/bin/env python3
"""Make the CURRENT map a river site for the FlowWorks rivers extension chains (extensions_rivers.py).

    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py            # bridge held, a Playing game
    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py --dry      # the same, on a tile with NO river

The rivers chains read "UNMEASURED: the site map has no river current" on a quicktest map without a river. This founds a
colony on a flat MILD (14-20 C mean, 15 <= |lat| <= 32: map 5 at |lat| <= 25 hit frostbite at night; |lat| <= 15 is PermanentSummer, 42 C at noon on a 22 C-mean tile, heatstroke) tile that HAS a river (first qualifying tile, in tile order), generates its map, makes it current, removes every
non-colonist, spawns colonists and runs bland_world.reset() so the watch starts bland. Mild on purpose: on a 38 C
quicktest tile (MEASURED 2026-10-06) idle colonists took Heatstroke mid-chain and five components read UNMEASURED. bland_world.setup() is the same
recipe with the opposite tile filter (riverCount == 0). Prints the tile, its rivers and the reset problems. Exit 0 when
the new map is current, reports a river current (--dry: a tile with no river, by design) and bland_world.reset() names
no problem; 2 when no tile qualified; 3 when the map is made but fewer than 3 colonists spawned and drafted, an old
colonist did not vanish, a candidate map of this run is still loaded, the map-only quiet-site profile is not clean,
or reset() reported problems (printed).
TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA (r7): a RIVER site also needs moving water on two map edges (a river that
ends in the sea has only its inflow edge, so the swept row cannot carry anyone off), the map is made current by its
uniqueID (mapId, never the Find.Maps index) and read back by tile, and every rejected candidate map is removed.
TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ (r7): no candidate map outlives the run (read back), and the site gets the
shared map-only quiet-site profile (prep_site.py's convention; the chain Watch turns the storyteller off).
"""
import csv
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bland_world as BW  # noqa: E402
import extensions_rivers as RIV  # noqa: E402


def _QS():
    """The shared quiet isolated test-site profile (Utils/modcheck/quiet_site.py)."""
    import quiet_site
    return quiet_site


def river_candidates(rows):
    out = []
    for r in rows:
        try:
            if (r.get("hilliness") in ("Flat", "SmallHills") and float(r.get("swampiness") or 0) < 0.3
                    and 0 <= float(r.get("elevation") or -1) < 600 and 14 <= float(r.get("temperature") or -99) <= 20
                    and 15 <= abs(float(r.get("lat") or 90)) <= 32
                    and r.get("biome") not in ("Ocean", "Lake", "SeaIce", "IceSheet", "Desert", "ExtremeDesert", "AridShrubland")):
                out.append(int(r.get("tile") if r.get("tile") is not None else r.get("index")))
        except (TypeError, ValueError):
            continue
    return out


def biome_has_fish(fields):
    """True/False from a BiomeDef's `maxFishPopulation` + `fishTypes` (jawa/get_defs fields), None when unreadable.
    A river WaterBody has fish only on a biome that carries both: 2026-10-12 tile 9980 (RM_TheRot) did not, and
    weir_fish_draws_stock plus 7 later rows read UNMEASURED 'no fish stock'."""
    if not isinstance(fields, dict) or "maxFishPopulation" not in fields:
        return None
    try:
        if float(fields.get("maxFishPopulation") or 0) <= 0:
            return False
    except (TypeError, ValueError):
        return None
    ft = fields.get("fishTypes")
    if ft is None:
        return None
    if isinstance(ft, dict):                      # {"freshwater_Common": {...}, ...} or a flat table
        fresh = [v for k, v in ft.items() if str(k).startswith("freshwater")]
        return any(bool(v) for v in fresh) if fresh or any(str(k).startswith("saltwater") for k in ft) else any(bool(v) for v in ft.values())
    return bool(ft)


def biome_fish_from_xml(xml_text):
    """{biome defName: True/False} from BiomeDef XML (Odyssey / our src). A def with ParentName is skipped (unknown):
    inheritance is not resolved here, so absence of a verdict means 'ask the live game'."""
    import xml.etree.ElementTree as ET
    out = {}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for d in root.iter("BiomeDef"):
        name = (d.findtext("defName") or "").strip()
        if not name or d.get("ParentName"):
            continue
        try:
            mx = float(d.findtext("maxFishPopulation") or 0)
        except ValueError:
            continue
        ft = d.find("fishTypes")
        fresh = ft is not None and any(len(c) for c in ft if c.tag.startswith("freshwater"))
        out[name] = bool(mx > 0 and fresh)
    return out


def prefer_fish(rows, fish):
    """Order river tile rows for founding: biomes KNOWN to carry fish first, unknown next, known fishless dropped.
    Returns (ordered rows, [(biome, n) rejected]). Never names a tile: the filter is the biome's fish."""
    good, unknown, rejected = [], [], {}
    for r in rows:
        f = fish.get(r.get("biome"))
        if f is True:
            good.append(r)
        elif f is None:
            unknown.append(r)
        else:
            rejected[r.get("biome")] = rejected.get(r.get("biome"), 0) + 1
    return good + unknown, sorted(rejected.items())


def fish_by_biome(call, biomes, fallback=None):
    """{biome: True/False/None}: the live BiomeDef first (jawa/get_defs); where that is unreadable, `fallback`
    (biome_fish_from_xml over Odyssey / our BiomeDef XML); None when neither knows."""
    out = {}
    for b in sorted(set(x for x in biomes if x)):
        try:
            r = call("jawa/get_defs", defs="BiomeDef/%s" % b, fields="maxFishPopulation,fishTypes", deep=True) or {}
            f = ((r.get("defs") or [{}])[0] or {}).get("fields")
        except Exception:                      # diagnostics-grade read; unreadable means unknown, not fishless
            f = None
        out[b] = biome_has_fish(f)
        if out[b] is None and fallback:
            out[b] = fallback.get(b)
    return out


def _xml_fish():
    """Offline fallback table: the Odyssey BiomeDefs plus ours (src/**/BiomeDefs). Empty when none is readable."""
    import glob
    pats = [os.path.join(ROOT, "src", "*", "*", "Defs", "BiomeDefs", "*.xml"),
            r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\BiomeDefs\*.xml",
            "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Odyssey/Defs/BiomeDefs/*.xml"]
    out = {}
    for pat in pats:
        for f in glob.glob(pat):
            try:
                with open(f, encoding="utf-8") as fh:
                    out.update(biome_fish_from_xml(fh.read()))
            except OSError:
                continue
    return out


def scenery_blockers(call, size, dry):
    """Natural-scenery defs (BW.NATURAL_SCENERY) that sit where the chains build. DRY site: inside any site_spec plot
    buffered rect on a map of `size`. RIVER site: none -- the river chains use no plot. `call` is s.call (injectable)."""
    if not dry:
        return []
    import site_spec as S
    try:
        rects = [S.clip(p["buffered"], size) for p in S.layout(size)]
    except ValueError as e:                  # a map too small for the plots cannot be a dry site: reject it, do not crash
        return ["layout: %s" % e]
    return [d for d in BW.NATURAL_SCENERY
            if any(call("jawa/list_things", defName=d, rect=S.rect_str(r), limit=1).get("things") for r in rects if r[2] and r[3])]


def generated_map_id(g):
    """Map.uniqueID of a jawa/world_tile_map_generate reply, or None. TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA (r7): this
    used to pass g["mapIndex"] (a Find.Maps POSITION) to set_current_map, which wants the uniqueID; on the fixture world
    (uids 1..10 at indexes 0..9) every candidate was read on the PREVIOUS map and the site settled on tile 60145 while
    printing 60146. Never fall back to the index: a missing id is a refusal."""
    v = (g or {}).get("mapId")
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def river_reject(kv, edges, dry, tile=None, map_tile=None):
    """Why this candidate map is not a river site, or None to accept it. kv: the mod's ProofGrid key=values; edges:
    extensions_rivers.moving_edges of the map's ring; map_tile: jawa/map_info's tile (the current map's read-back).
    RIVER needs a current, a FAST lane (ProofShove's 4-cell run) and moving water on MIN_RIVER_EDGES edges (a river that
    ends in the sea has only its inflow edge: r7 swept read UNMEASURED twice, nobody could be carried off)."""
    if tile is not None and map_tile != tile:
        return "the current map is tile %s, not %s (set_current_map read-back)" % (map_tile, tile)
    if dry:
        return None
    if not (int(kv.get("current", 0) or 0) > 0 and (int(kv.get("fast", 0) or 0) > 0 or ALLOW_NO_FAST)):
        return "no current with a fast lane (grid current=%s fast=%s)" % (kv.get("current"), kv.get("fast"))
    if edges is None:
        return "map-edge terrain unreadable (get_terrain_batch refused)"
    if len(edges or {}) < RIV.MIN_RIVER_EDGES:
        return "no downstream edge: moving water reaches only %s (the river ends in the sea or a lake)" % (edges,)
    return None


def loaded_maps(call):
    """[{mapId, tile, biome}] of every loaded map, or None when unreadable. jawa/set_current_map refuses an unknown
    mapId WITHOUT changing the current map and lists loadedMaps in the refusal (its documented read)."""
    r = call("jawa/set_current_map", mapId=-1) or {}
    det = r.get("details") if isinstance(r.get("details"), dict) else {}
    lm = det.get("loadedMaps", r.get("loadedMaps"))   # the live tool nests it under details (r8)
    return lm if isinstance(lm, list) and not r.get("success") else None


def leftover_maps(loaded, site_map_id, generated_tiles):
    """Maps THIS run generated that are not the site: they must go. TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ (r7): the
    hostile Bumbledrone swarm (a queen + drones, fresh ids, one tick) that stopped swept run 1 arrived on map uid 3, a
    rejected candidate river_site had left loaded, not on the test map (uid 9). Nothing swept or quieted those maps,
    and the vitals governor watches every map. Maps loaded before the run (the session's home) are not touched."""
    gen = set(int(t) for t in generated_tiles)
    return [m for m in loaded or [] if m.get("mapId") != site_map_id and m.get("tile") in gen]


ALLOW_NO_FAST = "--allow-no-fast" in sys.argv   # R3 (wash-off-map) needs edge current only; a quicktest world can hold no size-1.89
# river (2026-10-18: 20 of 20 river tiles fast=0) -- opt in to accept current without a fast lane (R1/ProofShove "fast" then UNMEASURED)
DRY = "--dry" in sys.argv     # the opposite site: NO river, for the plot/toggle chains. Their 40x30 Soil repaints cut a
# river and a river cut their plots (MEASURED 2026-10-06: confinement read river cells (122,87..89) as D=4 F=4 "liquid on
# un-dug ground"; the weir pooled over painted Soil). Rivers chains run on a river site, the rest on a dry one.


def main():
    from rimdrive import Session
    with Session(lock=None) as s:
        # the colonists left on the map we are leaving: vanished once the new site stands. Left alone they starve or
        # cook there, and their deaths are game-wide letters the watch reads as colonist_died in whatever chain is
        # running (MEASURED 2026-10-06: three chains UNMEASURED on deaths of map-0 quicktest colonists)
        old_cols = [p["id"] for p in (s.call("jawa/list_pawns", limit=500).get("pawns") or [])
                    if p.get("isPlayer") and not p.get("dead")]
        path = os.path.join(os.environ.get("TEMP") or tempfile.gettempdir(), "river_site_tiles.csv")
        r = s.call("jawa/world_tile_export", path=path)
        if not r.get("success") or not os.path.isfile(path):
            print("world_tile_export failed: %s" % r)
            return 2
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cands = river_candidates(rows)
        print("tiles", len(rows), "flat temperate candidates", len(cands))
        tile, info, river = None, None, []
        for i in range(0, len(cands), 100):           # world_tile_get caps a read at 100 rows
            got = s.call("jawa/world_tile_get", tiles=",".join(str(t) for t in cands[i:i + 100])).get("tiles") or []
            # no mutator/road filter: on 1.6 a river tile commonly carries a river mutator (0 of 7901 passed with it)
            river += [g for g in got if (int(g.get("riverCount") or 0) > 0) != DRY]
        print("river tiles among them", len(river))
        if not DRY:
            fish = fish_by_biome(s.call, [g.get("biome") for g in river], _xml_fish())
            river, rej = prefer_fish(river, fish)
            print("fish by biome:", fish, "| rejected fishless river tiles:", rej)
        g, tries, generated = None, 0, []
        for row in river:
            if tries >= 40:                     # BENCH 2026-10-11: 10 was spent on steam geysers alone
                break
            t = int(row["tile"])
            cf = s.call("jawa/colony_found", tile=t, faction="Player", name=("NorthstarDry" if DRY else "NorthstarRiver"))
            if not cf.get("success"):
                continue
            tries += 1
            BW.close_naming_dialogs(s)
            g = s.call("jawa/world_tile_map_generate", tile=t, suggestedMapParent="Settlement")
            mid = generated_map_id(g)
            fresh = bool(g.get("success")) and not g.get("wasAlreadyGenerated")
            if fresh:
                generated.append(t)
            if not g.get("success") or mid is None:
                print("tile", t, "map generate refused or gave no mapId: %s" % (g.get("message") or str(g)[:200]))
                if fresh:                       # a map made with no id to address it by is still a leftover
                    s.call("jawa/settlement_remove", mode="map", tile=t, force=True)
                continue
            BW.close_naming_dialogs(s)

            def drop(why, t=t, fresh=fresh):
                # every rejected map THIS run made goes (BENCH 2026-10-11: ten rejected tries left ten live maps behind;
                # r7: only the scenery reject dropped its map, and a hostile swarm then arrived on a leftover one)
                print("tile", t, "rejected:", why)
                if fresh:
                    s.call("jawa/settlement_remove", mode="map", tile=t, force=True)
            cm = s.call("jawa/set_current_map", mapId=mid)
            if not (cm or {}).get("success"):
                drop("set_current_map refused: %s" % (cm or {}).get("message"))
                continue
            # a tile's riverCount is not a promise of a CURRENT on its map (MEASURED 2026-10-06: tile 24, riverCount 2,
            # ProofGrid current=0): ask the mod's own grid and move on when it is empty
            grid = str((s.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid",
                               args="-") or {}).get("result", ""))
            kv = dict(p.split("=", 1) for p in grid.split() if "=" in p)
            print("tile", t, "mapId", mid, row.get("biome"), "riverCount", row.get("riverCount"), "grid:", grid[:120])
            # indestructible scenery (steam geyser) only matters where the chains build: the DRY site's plot chains use the
            # site_spec plot footprints + buffers (a geyser in plot D took the pump's cell: MEASURED 2026-10-06, tile 45);
            # the RIVER chains are C# proofs that find the river themselves and use no plot, so a geyser anywhere else is
            # harmless there. The old test (any geyser in the 130x130 centre rect) rejected every river tile (MEASURED
            # 2026-10-11, 40 of 40) -- RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE.
            mi0 = s.call("jawa/map_info") or {}
            size = (int(mi0.get("sizeX", 250)), int(mi0.get("sizeZ", mi0.get("sizeY", 250))))
            scenery = scenery_blockers(s.call, size, DRY)
            if scenery:
                drop("%s inside a plot footprint+buffer" % (scenery,))
                continue
            edges = {}
            if not DRY:
                import site_spec as S
                tb = s.call("jawa/get_terrain_batch", rects=RIV.edge_rects(size)) or {}
                edges = RIV.moving_edges(S.parse_ops(tb.get("ops")), size) if tb.get("success") else None
                print("tile", t, "moving water on edges", edges)
            why = river_reject(kv, edges, DRY, tile=t, map_tile=mi0.get("tile"))
            if why:
                drop(why)
                continue
            tile, info = t, row
            break
        if tile is None:
            print("no river tile with a current among %d tried" % tries)
            return 2
        site_id = generated_map_id(g)
        # TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ: no candidate map of this run may outlive it (read back)
        bad = []
        for m in leftover_maps(loaded_maps(s.call), site_id, generated):
            print("dropping leftover candidate map", m)
            s.call("jawa/settlement_remove", mode="map", tile=m.get("tile"), force=True)
        lm = loaded_maps(s.call)
        if lm is None:
            bad.append("loaded maps unreadable after the site was chosen")
        else:
            left = leftover_maps(lm, site_id, generated)
            if left:
                bad.append("candidate maps still loaded: %s" % left)
            print("loaded maps:", lm)
        # the site is made current (read back) BEFORE the map-only profile, which acts on whatever map is current
        cm = s.call("jawa/set_current_map", mapId=site_id) or {}
        if not cm.get("success") or cm.get("tile") != tile:
            bad.append("the site map %s is not current after the cleanup: %s" % (site_id, str(cm)[:160]))
        # the shared quiet-site profile, map controls (as prep_site.py): threat structures, hostiles, proximity letters,
        # read back. The storyteller/wild-spawner half is the chain Watch's own SettingsTransaction (quiet_world), applied
        # at every chain start, so it is not duplicated here.
        qs = _QS().site_profile_receipt(s, "flowworks_river_site_%s" % tile, controls=_QS().MAP_ONLY)
        print("quiet site (map):", [(c.get("name"), c.get("readBack")) for c in qs.get("controls") or []],
              "problems", qs.get("problems"), "error", qs.get("error"))
        if qs.get("error"):                     # prep_site.py's bar: an UNCLEAN map-only profile is a site problem
            bad.append("quiet site (map) not clean: %s" % (qs.get("error"),))
        d = s.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        mi = s.call("jawa/map_info")
        # OFF the extension plot grid (centred on the map, +-~56 cells) and DRAFTED: colonists spawned at the centre
        # wandered into the plots' pits and read as colonist_damaged "Blunt by nobody" (the mod's fall damage) in five
        # components (MEASURED 2026-10-06, map 5).
        cx, cz = int(mi.get("sizeX", 250)) // 2, 30
        new_ids = []
        for i in range(3):
            sp = s.call("jawa/spawn_pawn", kindDef="Colonist", x=cx + 2 * i, z=cz, faction="player", count=1) or {}
            for p in sp.get("pawns") or []:
                if not p.get("id"):
                    continue
                new_ids.append(p["id"])
                if not (s.call("jawa/set_draft", pawnId=p["id"], drafted=True) or {}).get("success"):
                    bad.append("set_draft %s refused" % p["id"])
        BW.close_naming_dialogs(s)
        for pid in old_cols:
            if not (s.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish") or {}).get("success"):
                bad.append("old colonist %s did not vanish" % pid)
        if len(new_ids) < 3:
            bad.append("only %d of 3 colonists spawned" % len(new_ids))
        rep = BW.reset(s, expected_ids=new_ids)
        print("tile", tile, "mapId", generated_map_id(g), "map_info tile", mi.get("tile"), "size", mi.get("sizeX"), "biome", mi.get("mapBiome"), "destroyed", d.get("matchedCount"),
              "colonists", new_ids, "site problems", bad, "reset problems", rep.get("problems"))
        if bad or rep.get("problems"):
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
