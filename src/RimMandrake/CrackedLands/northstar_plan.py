"""northstar_driver plan for CrackedLands (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod CrackedLands \\
      --plan src/RimMandrake/CrackedLands/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying FlowWorks + CrackedLands + ExplosiveGrowth, current
map a plain open biome map): same without --mock / --mock-skip-site. The suite clears and arms its own site."""
MOD = "CrackedLands"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.crackedlands
NEED_GOD = False
RECT = None
