# LASSO_CHERRYPICKER_REMOVAL_1

Owner, typed, 2026-10-01 (Sump turn 1): *"Remove lasso's from the game, but keep this"* (the capstan turret, `SUMP_CAPSTAN_TURRET_BUILD_1`). Evidence: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §5 ("The lasso removal").

1. The lassos are Melee Animation's (`co.uk.epicguru.meleeanimation`): `AM_LassoCloth`, `AM_LassoDevilstrand`, `AM_LassoHyperwave`, all apparel. Cut by Cherry Picker, never by uninstalling the mod (its animations stay).
2. `AM_LassoHyperwave` and `AM_LassoDevilstrand` are already cut (`CherryPicker.SHIP.xml` and the live config). Add `ThingDef/AM_LassoCloth` and anything that reaches it (its tailoring recipe; any research).
3. Disarm check, measured 2026-10-01: lassos are apparel, so no weapon tag is affected; `defs.sqlite` holds 0 PawnKindDefs with apparel tag `Lasso` (probe: 51 with `Neolithic`). Pawns get lassos from the mod's own C# spawn roll.
4. 🔴 So also set Melee Animation's lasso spawning off: its "No Lassos" preset or "Lasso Commonality" 0 (no saved settings file exists today; it runs on defaults). Whether its spawn roll errors with zero lasso defs is UNMEASURED; settings first, then the cut.
5. Back up the Cherry Picker config before editing (the project keeps dated backups beside it); update `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` to match.

## verify
- A full-list load: no lasso craftable or on any spawned pawn; no Melee Animation errors in `Player.log`; melee animations still play.
