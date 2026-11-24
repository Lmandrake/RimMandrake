"""Acceptance of RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL: on a save of a hot, sunny map, no cell holds three
or more wild animals. usage: <this> <save.rws>. Exit 0 holds, 1 fails, 2 could not look (no wild animal on the map)."""
import collections
import sys
import xml.etree.ElementTree as ET
try:
    things = ET.parse(sys.argv[1]).getroot().findall("game/maps/li/things/thing")
except Exception as e:  # noqa: BLE001
    print("COULD NOT LOOK: %s" % e); sys.exit(2)
cells = collections.defaultdict(list)
for t in things:
    if t.find("kindDef") is not None and t.findtext("faction") is None:
        cells[t.findtext("pos")].append(t.findtext("kindDef"))
if not cells:
    print("COULD NOT LOOK: no wild animal"); sys.exit(2)
bad = {p: v for p, v in cells.items() if len(v) >= 3}
print("%d wild animals; cells with three or more: %s" % (sum(map(len, cells.values())), bad or "none"))
sys.exit(1 if bad else 0)
