"""northstar_driver plan for Warcasket. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Warcasket \\
      --plan src/RimMandrake/Warcasket/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `warcasket` tier, any 150x150+ map): same without --mock."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Warcasket"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.warcasket",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
