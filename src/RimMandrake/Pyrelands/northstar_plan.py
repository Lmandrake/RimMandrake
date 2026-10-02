"""northstar_driver plan for Pyrelands (the suite in validation.py). Live, python.exe, bridge held, game up on the
`pyrelands` tier, current map = the gate-B-clean site fixture (northstar_site.py + preflight_pyrelands.py gates A, B):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands \\
      --plan src/RimMandrake/Pyrelands/northstar_plan.py
The deploy of the composed mod and the site are gated by preflight_pyrelands.py (rows 3.2.x, 3.8.x), not here."""
MOD = "Pyrelands"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)
NEED_GOD = False
RECT = None
