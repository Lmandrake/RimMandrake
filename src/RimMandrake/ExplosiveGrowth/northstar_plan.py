"""northstar_driver plan for ExplosiveGrowth. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod ExplosiveGrowth \\
      --plan src/RimMandrake/ExplosiveGrowth/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `explosivegrowth_solo` tier = Baroque Biomes + the bridge): same without
--mock / --mock-skip-site."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "ExplosiveGrowth"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)   # the engine is composed in Baroque Biomes (EXPLOSIVE_GROWTH_MERGE_COMES_HOME)
NEED_GOD = False
RECT = None                 # the suite clears its own site; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
