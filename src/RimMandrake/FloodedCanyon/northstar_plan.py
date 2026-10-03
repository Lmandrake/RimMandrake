"""northstar_driver plan for FloodedCanyon (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod FloodedCanyon \\
      --plan src/RimMandrake/FloodedCanyon/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying FlowWorks + FloodedCanyon + ExplosiveGrowth, current
map a plain open biome map): same without --mock / --mock-skip-site. The suite clears and arms its own site."""
MOD = "FloodedCanyon"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.floodedcanyon
NEED_GOD = False
RECT = None
