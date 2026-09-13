# D2 DROID_RETIRE_KOTORDROIDS_1 — decision strings, written before launch

Baseline: infrastructure/state/facts/config_error_baseline_2026-09-06.json
Checker: python3 src/RimMandrake/Utils/check_config_errors.py

1. `check_config_errors.py` exit code 0 (nothing outside baseline, no regression)
   => CLEAN. Exit 1 => read the new/regressed lines named in its output.
2. Mod count in the fresh Player.log's mod list should be 599 (600 - guy762.kotordroids).
3. grep the fresh log for `guy762` and `KotOR` (case-insensitive) in any
   `Config error in` / `Could not resolve cross-reference` / `Could not load reference to`
   line naming a DONOR defName (`guy762_KotORFaction_RogueDroids`, `KotORDroidColonist_*`,
   `KotORDroid*` without the `RSW_DW_` prefix). Zero such hits => the "all gated" claim
   holds. Any hit => something was NOT actually gated; revert ModsConfig.xml from backup
   (infrastructure/state/modlists/ModsConfig.PRESWAP.20260908_before_D2_kotordroids_retire.xml),
   leave item `doing`+blocked with the exact line.
4. Spot check: `jawa/list_pawns` or a debug spawn of a FDE (`Jawa_FreeDroidEnclaves`)
   pawn kind (`Jawa_Droid_Grunt`/`Jawa_Droid_Heavy`/`Jawa_Droid_Specialist`/`Jawa_Droid_Leader`)
   generates successfully on the `RSW_DW_Race_OuterRim_*` race — confirms C2's repoint still
   functions with kotordroids gone.
