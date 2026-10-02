"""northstar_driver plan for FeverWood (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod FeverWood \\
      --plan src/RimMandrake/FeverWood/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a quicktest map >= 150x150):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod FeverWood \\
      --plan src/RimMandrake/FeverWood/northstar_plan.py
One command from a cold start (stops the game, writes the tier, composes, launches, runs): live_session.py.

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: FeverWood ships composed inside the
Baroque Biomes mod (Biomes.compose.json, wave 2), so `mandrake.rm.feverwood` is never in ModsConfig."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "FeverWood"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pad; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
