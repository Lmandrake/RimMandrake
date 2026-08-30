#!/usr/bin/env python3
"""save_played_tiles.py - which world tiles carry a GENERATED local Map in the
current campaign save (PAINT_GUARD_ASK_EACH_TIME_1).

A world-tile write (biome/terrain repaint, landmark placement, ...) that lands
on a tile with a live local Map desyncs the two - the map was generated from
that tile's biome, and moving the ground out from under it corrupts the
colony (w9_run.py's own guard, "the paint moves the ground out from under a
map already generated from it"). The tile that matters is not "the start" or
any other fixed anchor - it is whichever tiles the CURRENT save has actually
settled, which changes every session as the player expands.

MECHANISM, measured against the live campaign save (WORLDMAP_V1_original.rws,
21 MB), not guessed:
  - Game.maps is a list of Map records; each carries <mapInfo><parent>
    WorldObject_NNN</parent></mapInfo> - the save-file cross-reference string
    naming the WorldObject (usually a Settlement) the map was generated for.
  - Game.world.worldObjects.worldObjects is the flat list of every live
    WorldObject; each carries its own <ID>NNN</ID> and <tile>TTTT,L</tile>
    (a "tile,layer" pair - the layer is dropped here, only the tile id is
    the world-grid coordinate anything else on this planet cares about).
  - Joining Map.parent's NNN against WorldObject.ID gives the tile every
    generated local map actually sits on.

No save file, or no <maps> entries -> empty set: "if no campaign save exists,
nothing to protect" (the item's own words).
"""
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    from game_paths import SAVES as _SAVES_DIR
except ImportError:  # pragma: no cover - only if game_paths.py ever moves
    import sys
    sys.path.insert(0, HERE)
    from game_paths import SAVES as _SAVES_DIR

DEFAULT_SAVE_NAME = "WORLDMAP_V1_original.rws"


def default_save_path(saves_dir=None):
    """The frozen campaign save, if it exists on disk. None otherwise -
    callers treat None exactly like 'no campaign save exists'."""
    d = saves_dir or _SAVES_DIR
    if not d:
        return None
    p = os.path.join(d, DEFAULT_SAVE_NAME)
    return p if os.path.isfile(p) else None


def played_tiles(save_path):
    """-> (set of int tile ids with a generated local Map, save_path used-or-None).

    save_path=None (or a missing file) is exactly "no campaign save exists" -
    returns (set(), None), which callers must treat as nothing to protect,
    not as an error.
    """
    if not save_path or not os.path.isfile(save_path):
        return set(), None

    tree = ET.parse(save_path)
    root = tree.getroot()

    # tile id, by WorldObject loadID ("<ID>NNN</ID>" -> int(<tile>TTTT,L</tile>
    # split on the first comma))
    tile_by_id = {}
    for li in root.iter("li"):
        id_el = li.find("ID")
        tile_el = li.find("tile")
        if id_el is None or tile_el is None or not id_el.text or not tile_el.text:
            continue
        try:
            obj_id = int(id_el.text.strip())
        except ValueError:
            continue
        tile_txt = tile_el.text.strip()
        m = re.match(r"(-?\d+)", tile_txt)
        if not m:
            continue
        tile_by_id[obj_id] = int(m.group(1))

    played = set()
    for maps_el in root.iter("maps"):
        for map_li in maps_el.findall("li"):
            info = map_li.find("mapInfo")
            if info is None:
                continue
            parent = info.find("parent")
            if parent is None or not parent.text:
                continue
            m = re.match(r"WorldObject_(\d+)", parent.text.strip())
            if not m:
                continue
            obj_id = int(m.group(1))
            if obj_id in tile_by_id:
                played.add(tile_by_id[obj_id])

    return played, save_path


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else default_save_path()
    tiles, used = played_tiles(path)
    if used is None:
        print("no campaign save found - nothing to protect")
    else:
        print("%s: %d tile(s) carry a generated local map: %s"
              % (used, len(tiles), sorted(tiles)))
