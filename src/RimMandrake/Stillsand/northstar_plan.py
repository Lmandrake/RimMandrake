"""northstar_driver plan for Stillsand (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Stillsand \\
      --plan src/RimMandrake/Stillsand/northstar_plan.py --mock-skip-site
Live, one command (bridge held by FOUNDRY; stops the game, swaps the tier, deploys the composed biomes,
launches, starts a quicktest world, runs the driver):
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Stillsand --tier baroque_wave0 \\
      --plan src/RimMandrake/Stillsand/northstar_plan.py --compose
or, with the game already up on `baroque_wave0` and a quicktest world:
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Stillsand \\
      --plan src/RimMandrake/Stillsand/northstar_plan.py

Stillsand ships COMPOSED inside mandrake.rm.biomes (Biomes.compose.json, wave 2), so that is the packageId
a run must find active; the dev folder's own mandrake.rm.stillsand is never loaded (deploy_custom_mods.py
refuses it). The suite builds its own Stillsand map (its `site` chain): the quicktest world only has to
exist."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import northstar_site                                    # noqa: E402

MOD = "Stillsand"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None                 # the suite clears its own pads; pre-flight checks the world, not a rect
preflight = northstar_site.preflight
