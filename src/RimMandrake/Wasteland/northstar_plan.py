"""northstar_driver plan for Wasteland. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Wasteland \\
      --plan src/RimMandrake/Wasteland/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier after a quicktest world):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Wasteland \\
      --plan src/RimMandrake/Wasteland/northstar_plan.py
or the one-command session (stops the game, applies the tier, composes + deploys the biome mod, launches,
starts a quicktest world and runs this plan): see the live-run sheet in
Transient/worker_notes_WASTELAND_FIRST_SCRIPT_1.md.

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: Wasteland ships composed inside the
Baroque Biomes mod (Biomes.compose.json, wave 2), so `mandrake.rm.wasteland` is never in ModsConfig. This is
the same packaging as Pyrelands and WeepingStones.

The storm layer, the Middenshell incident and the Rite of Tipping are biome-gated, so northstar_site.preflight
builds a Wasteland map (a re-tiled land tile, a founded colony, a generated 150x150 map) when the current map
is not one. Every other chain keys on a def and runs on whatever map is current."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Wasteland"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
