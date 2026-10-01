"""northstar_driver plan for LeaningScrub (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod LeaningScrub \\
      --plan src/RimMandrake/LeaningScrub/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a quicktest map >= 150 cells):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod LeaningScrub \\
      --plan src/RimMandrake/LeaningScrub/northstar_plan.py

LeaningScrub ships COMPOSED inside mandrake.rm.biomes (Biomes.compose.json), together with the
EnvironmentalHazards kit it depends on, so that is the packageId a run must find active; the
dev folder's own mandrake.rm.leaningscrub is never loaded (deploy_custom_mods.py refuses it)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "LeaningScrub"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
