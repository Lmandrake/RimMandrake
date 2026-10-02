"""northstar_driver plan for Graffiti. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Graffiti \\
      --plan src/RimMandrake/Graffiti/northstar_plan.py
Live (python.exe, bridge held, game up on the `graffiti_solo` tier): same without --mock."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Graffiti"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.graffiti",)
NEED_GOD = False
RECT = None                 # the suite clears its own site; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
