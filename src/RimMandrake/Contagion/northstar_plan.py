"""northstar_driver plan for The Contagion (the suite in validation.py). Item CONTAGION_FIRST_SCRIPT_1.
Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Contagion \\
      --plan src/RimMandrake/Contagion/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a quicktest map >= 150 cells):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Contagion \\
      --plan src/RimMandrake/Contagion/northstar_plan.py

The Contagion ships COMPOSED inside mandrake.rm.biomes (Biomes.compose.json, wave 0), so that is the
packageId a run must find active; the dev folder's own mandrake.rm.contagion is never loaded
(deploy_custom_mods.py refuses it)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Contagion"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
