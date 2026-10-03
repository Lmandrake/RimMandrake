"""northstar_driver plan for Greentide (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Greentide \\
      --plan src/RimMandrake/Greentide/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying Greentide + Creature Behaviors + Environmental Hazards):
same without --mock / --mock-skip-site. The suite builds and clears its own site."""
MOD = "Greentide"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.greentide
NEED_GOD = False
RECT = None
