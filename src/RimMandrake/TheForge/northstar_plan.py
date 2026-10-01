"""northstar_driver plan for The Forge. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod TheForge \\
      --plan src/RimMandrake/TheForge/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `baroque_wave0` tier, a FRESH quicktest map >= 160x160):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod TheForge \\
      --plan src/RimMandrake/TheForge/northstar_plan.py
One command from stopped game to recorded run: see live_session.py's docstring and the live-run sheet in
Transient/worker_notes_THE_FORGE_FIRST_SCRIPT_1.md.

EXPECT_MODS is `mandrake.rm.biomes`, not the dev folder's own packageId: The Forge ships COMPOSED inside the Baroque
Biomes mod (Biomes.compose.json), so `mandrake.rm.theforge` is never in ModsConfig. Same packaging as Pyrelands and
WeepingStones."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "TheForge"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite builds and clears its own pad; pre-flight checks the map, not a rect
preflight = northstar_site.preflight
