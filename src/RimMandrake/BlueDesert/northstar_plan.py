"""northstar_driver plan for BlueDesert (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod BlueDesert \\
      --plan src/RimMandrake/BlueDesert/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a quicktest map >= 150 cells), or the
one-command session that does the tier swap, the compose deploy, the launch and the quicktest world too:
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod BlueDesert --tier baroque_wave0 \\
      --plan src/RimMandrake/BlueDesert/northstar_plan.py --compose
The live-run sheet (tier command, tick budget, site prerequisites, what each verdict means) is in
Transient/worker_notes_BLUE_DESERT_FIRST_SCRIPT_1.md and in the walk.

BlueDesert ships COMPOSED inside mandrake.rm.biomes (Biomes.compose.json, wave 2), together with the
EnvironmentalHazards kit it depends on, so that is the packageId a run must find active; the dev folder's own
mandrake.rm.bluedesert is never loaded (deploy_custom_mods.py refuses it)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "BlueDesert"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
