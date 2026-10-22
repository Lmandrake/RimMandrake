"""northstar_driver plan for Webwork (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Webwork \\
      --plan src/RimMandrake/Webwork/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying mandrake.rm.biomes, e.g. `desertplants`): same without
--mock / --mock-skip-site, narrowed with --chains (runbook 2026-10-22 rows 2.3-2.6, 2.10):
  --chains defs_resolve,settings_roundtrip,thrixweave_and_front   any map
  --chains urraveth_remains | traction_lance | siege                 a plain quicktest map; siege's
      spider_spins_a_web_on_an_unexposed_cell reads UNMEASURED until it runs on a shaded RM_Webwork map.
The suite stages its own sites; it never edits ModsConfig.xml (unlike `modcheck run`)."""
MOD = "Webwork"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.webwork
NEED_GOD = False
RECT = None
