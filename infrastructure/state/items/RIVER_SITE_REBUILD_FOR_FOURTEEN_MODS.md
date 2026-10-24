## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: SITE.

Repro: `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --out <json>` (it loads
RM_TestSite_river_v1). The result is "site save river: NOT CLEAN" and the proof refuses to run. Evidence: `Transient/bridge_run_1_20261023/s2_river.log`,
`Transient/bridge_run_1_20261023/Player_s2_river_load.log`.
Errors in that load: Map.FinalizeLoading NRE (ListerFilthInHomeArea.Notify_HomeAreaChanged), Pawn_ApparelTracker
sort NRE, 201 pawn register exceptions, and dead refs to AA_/VFEI2_/RUT_/AB_/RSW_ defs. The save dates from
2026-10-15, on the owner's full list. The bridge run's 14-mod list cannot load it. Same failure class as cauldron
v1 -> v2 (test_site_saves.py:64).
Fix: build RM_TestSite_river_v2 on the 14-mod fw_gss_sitting list (test_site_saves.py build river; check it does not
generate a world, per the no-worldgen ruling). Then point SITES["river"] at v2. Until then BRIDGE_RUN_1 §2 (2.1-2.5)
is UNMEASURED/SITE: WEIR_CATCH_FIX_NO_FREE_FISH A3, SUSPENSION_WATERS_BUILD_MAY_BACKTRACK A1/A3,
WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID A3, FLOWWORKS_CHECKOUT_SCOPE_1 A2, TESTENV_HIVES/TOXIC river rows.

First exception (the cause): `Could not find class VFEInsectoids.GameComponent_Insectoids ... Trying to use
Verse.GameComponent instead` → `SaveableFromNode exception: System.ArgumentException: Can't load abstract class
Verse.GameComponent`. The save carries VFE Insectoids 2 (not on the 14-mod list); everything after cascades. The game then
sat in a "Root level exception in Update()" NRE storm until closed (owner: "game died"); log kept as
`Transient/bridge_run_1_20261023/Player_s2_river_storm.log` (2.0 MB). The proof refused cleanly; the harness gap is
that it left the broken load running — extension_proof should go to main menu when the site check says NOT CLEAN.
