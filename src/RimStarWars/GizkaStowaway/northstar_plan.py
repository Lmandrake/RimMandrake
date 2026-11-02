"""northstar_driver plan for GizkaStowaway (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod GizkaStowaway \\
      --plan src/RimStarWars/GizkaStowaway/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on the `gizkastowaway` modset tier -- SWBestiary carries the RSW_Gizka creature
the mod has no hard dependency on -- with a quicktest colony map and jawa/static_call enabled): same without --mock /
--mock-skip-site. The suite clears and stages its own sites (GIZKA_STOWAWAY_UNMEASURED_ROWS_1)."""
MOD = "GizkaStowaway"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rsw.gizkastowaway", "mandrake.rsw.swbestiary")
NEED_GOD = False
RECT = None
