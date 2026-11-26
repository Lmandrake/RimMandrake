"""python.exe: load the visit-6 walk save (PYRELANDS_0.1.0_VISIT6_WALK, tile 38) through northstar_site.reload_fixture, so its
stations can be shot close up (walk_closeups.py). Nothing is saved after."""
import os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
import northstar_site as NS  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402
s = FastSession(strict=False)
with s:
    mi = NS.reload_fixture(s, "PYRELANDS_0.1.0_VISIT6_WALK", 38, map_id=1)
print("loaded walk save: map %s tile %s %s" % (mi.get("mapId"), mi.get("tile"), mi.get("mapBiome")))
