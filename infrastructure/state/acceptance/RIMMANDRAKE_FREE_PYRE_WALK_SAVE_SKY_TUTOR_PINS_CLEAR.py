"""Acceptance of RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR: the Pyrelands walk savegame has a free sky and its
creatures station holds its creatures. usage: <this> <save.rws>. Exit 0 both hold, 1 one fails, 2 could not look."""
import sys
import xml.etree.ElementTree as ET
try:
    g = ET.parse(sys.argv[1]).getroot().find("game")
    story = g.findtext("storyteller/def")
    pawns = [(t.findtext("kindDef"), t.findtext("pos")) for t in g.findall("maps/li/things/thing") if t.find("kindDef") is not None]
except Exception as e:  # noqa: BLE001
    print("COULD NOT LOOK: %s" % e); sys.exit(2)
if not story or not pawns:
    print("COULD NOT LOOK: storyteller %r, %d pawns" % (story, len(pawns))); sys.exit(2)
ullai = [p for k, p in pawns if k == "RM_Ullai"]
sky, herd = story != "Tutor", len(ullai) >= 2 and len(set(ullai)) == len(ullai)
print("storyteller %s: %s; ullai %d on %d cells: %s" % (story, "ok" if sky else "FAIL", len(ullai), len(set(ullai)), "ok" if herd else "FAIL"))
sys.exit(0 if sky and herd else 1)
