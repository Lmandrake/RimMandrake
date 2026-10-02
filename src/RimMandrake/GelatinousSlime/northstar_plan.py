"""northstar_driver plan for GelatinousSlime (the suite in validation.py). Item GELATINOUS_SLIME_FIRST_SCRIPT_1.
Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod GelatinousSlime \\
      --plan src/RimMandrake/GelatinousSlime/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier = mandrake.rm.biomes composed):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod GelatinousSlime \\
      --plan src/RimMandrake/GelatinousSlime/northstar_plan.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_mock                                    # noqa: E402  (patches MockGame only; inert live)
import northstar_site                                    # noqa: E402

northstar_mock.install()
MOD = "GelatinousSlime"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # GelatinousSlime ships composed in it (Biomes.compose.json, wave 2)
NEED_GOD = False
RECT = None
preflight = northstar_site.preflight
