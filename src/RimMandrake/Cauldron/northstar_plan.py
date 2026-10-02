"""northstar_driver plan for Cauldron (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Cauldron \\
      --plan src/RimMandrake/Cauldron/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a quicktest map >= 150 cells):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Cauldron \\
      --plan src/RimMandrake/Cauldron/northstar_plan.py
One command from nothing (stops the game, swaps the tier, deploys the composed mod, launches, starts a
quicktest, runs this plan):
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Cauldron --tier baroque_wave0 \\
      --plan src/RimMandrake/Cauldron/northstar_plan.py --compose

Cauldron ships COMPOSED inside mandrake.rm.biomes (Biomes.compose.json, wave 0), so that is the
packageId a run must find active; the dev folder's own mandrake.rm.cauldron is never loaded
(deploy_custom_mods.py refuses it)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Cauldron"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
