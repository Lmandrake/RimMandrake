"""northstar_driver plan for Bacta (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Bacta \\
      --plan src/RimStarWars/Bacta/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `bacta` tier, a colony map with >= 80x80 free):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Bacta \\
      --plan src/RimStarWars/Bacta/northstar_plan.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_mock                                    # noqa: E402
import northstar_site                                    # noqa: E402

MOD = "Bacta"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rsw.bacta",)
NEED_GOD = False
RECT = None                 # the suite clears its own 40x40 site at the map centre
preflight = northstar_site.preflight
mock_extension = northstar_mock.mock_extension
