"""northstar_driver plan for TheRot (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod TheRot \\
      --plan src/RimMandrake/TheRot/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying mandrake.rm.biomes, e.g. `desertplants`): same without
--mock / --mock-skip-site, narrowed with --chains (runbook 2026-10-22 rows 2.1, 2.2, 2.7-2.9, 2.11):
  --chains defs_resolve,settings_roundtrip   any map
  --chains living_mat_root                   a NON-Rot quicktest map (rot_root_eats_nothing needs an RM_TheRot map)
  --chains wound_link                        any map; needs RM_Durrok/RM_Mullgoth's mod (mandrake.rsw.swbestiary) for A2
  --chains dustveil                          state reads only; never flight, never a screenshot (owner ruling)
The suite stages its own sites; it never edits ModsConfig.xml (unlike `modcheck run`)."""
MOD = "TheRot"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.therot
NEED_GOD = False
RECT = None
