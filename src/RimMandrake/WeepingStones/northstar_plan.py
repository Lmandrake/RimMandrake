"""northstar_driver plan for WeepingStones. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod WeepingStones \\
      --plan src/RimMandrake/WeepingStones/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `weepingstones_solo` tier, a quicktest map >= 150x150):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod WeepingStones \\
      --plan src/RimMandrake/WeepingStones/northstar_plan.py

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: WeepingStones ships composed
inside the Baroque Biomes mod (Biomes.compose.json), so `mandrake.rm.weepingstones` is never in
ModsConfig. This is the same packaging as Pyrelands."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "WeepingStones"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pad; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
