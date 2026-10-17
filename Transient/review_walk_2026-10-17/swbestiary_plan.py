"""Thin northstar_driver plan for SWBestiary's modcheck suite (walk 2026-10-17). Kept OUT of the mod folder so it does not
move the mod hash. Live (python.exe, bridge held, game up on the walk list):
  python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod SWBestiary --plan Transient/review_walk_2026-10-17/swbestiary_plan.py \
      --chains defs_resolve,dragonsnake_pair,taozin_brine_tank_infuses_and_whitens --no-record"""
MOD = "SWBestiary"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rsw.swbestiary",)
NEED_GOD = False
RECT = None
preflight = None
