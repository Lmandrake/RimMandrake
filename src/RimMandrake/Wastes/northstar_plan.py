"""northstar_driver plan for the Wastes (the mod was Wasteland until 33596c33a9). Offline, the suite's own mock:
  python3 src/RimMandrake/Wastes/selftest_wastes.py
(the driver's generic --mock has no jawa/set_pollution, so every pad-building chain dies there on site_ready_*).
Live (python.exe, bridge held, game up on a tier carrying mandrake.rm.biomes after a quicktest world):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Wastes \\
      --plan src/RimMandrake/Wastes/northstar_plan.py [--chains a,b]

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: the Wastes ship composed inside the
Baroque Biomes mod (Biomes.compose.json, wave 2), so `mandrake.rm.wastes` is never in ModsConfig. This is
the same packaging as Pyrelands and WeepingStones.

The storm layer, the Middenshell incident and the Rite of Tipping are biome-gated, so northstar_site.preflight
builds a Wastes map (a re-tiled land tile, a founded colony, a generated 150x150 map) when the current map
is not one. Every other chain keys on a def and runs on whatever map is current."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Wastes"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
