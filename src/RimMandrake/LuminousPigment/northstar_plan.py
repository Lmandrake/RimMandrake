"""northstar_driver plan for LuminousPigment (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod LuminousPigment \\
      --plan src/RimMandrake/LuminousPigment/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `luminouspigment_ns` tier, a fresh quicktest map):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod LuminousPigment \\
      --plan src/RimMandrake/LuminousPigment/northstar_plan.py
The live-run sheet (tier command, tick budget, site prerequisites, what each verdict means) is in
Transient/worker_notes_LUMINOUS_PIGMENT_FIRST_SCRIPT_1.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "LuminousPigment"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.luminouspigment", "mandrake.rm.ninefold")
NEED_GOD = False
RECT = None                 # every chain builds and clears its own pad; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
