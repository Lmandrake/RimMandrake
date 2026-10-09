# LASSO_CHERRYPICKER_REMOVAL_1

Owner, typed, 2026-10-01 (Sump turn 1): *"Remove lasso's from the game, but keep this"* (the capstan turret, `SUMP_CAPSTAN_TURRET_BUILD_1`). Evidence: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §5 ("The lasso removal").

1. The lassos are Melee Animation's (`co.uk.epicguru.meleeanimation`): `AM_LassoCloth`, `AM_LassoDevilstrand`, `AM_LassoHyperwave`, all apparel. Cut by Cherry Picker, never by uninstalling the mod (its animations stay).
2. `AM_LassoHyperwave` and `AM_LassoDevilstrand` are already cut (`CherryPicker.SHIP.xml` and the live config). Add `ThingDef/AM_LassoCloth` and anything that reaches it (its tailoring recipe; any research).
3. Disarm check, measured 2026-10-01: lassos are apparel, so no weapon tag is affected; `defs.sqlite` holds 0 PawnKindDefs with apparel tag `Lasso` (probe: 51 with `Neolithic`). Pawns get lassos from the mod's own C# spawn roll.
4. 🔴 So also set Melee Animation's lasso spawning off: its "No Lassos" preset or "Lasso Commonality" 0 (no saved settings file exists today; it runs on defaults). Whether its spawn roll errors with zero lasso defs is UNMEASURED; settings first, then the cut.
5. Back up the Cherry Picker config before editing (the project keeps dated backups beside it); update `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` to match.

## verify
- A full-list load: no lasso craftable or on any spawned pawn; no Melee Animation errors in `Player.log`; melee animations still play.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: No bridge needed, runs at game-down. Read `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_2944488802_*.xml` (Melee Animation, workshop id 2944488802, found by its About.xml name) for `<LassoSpawnChance>0</LassoSpawnChance>`. Measured 2026-10-08: that file does not exist in the Config folder, so the setting has never been written. PASS: the file exists and `<LassoSpawnChance>` reads 0 (or preset NoLassos applied). FAIL: file absent or the element absent or non-zero: the default spawn chance is live. Absence is a FAIL, not a pass.

## Progress (FOUNDRY belt builder, 2026-10-04)
- ✅ SHIP profile (`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`) now cuts `ThingDef/AM_LassoCloth` plus the
  three generated recipes `Make_AM_LassoCloth/Devilstrand/Hyperwave` (all three lassos inherit `AM_LassoBaseMakeable`'s
  recipeMaker; no research gates them). Same RecipeDef/Make_AM_* convention the SHIP list already uses.
- ⏳ NOT applied live: the live Cherry Picker config is UNRECOGNISED (`cherrypicker_swap.py --status`: 2133 cuts matching
  neither profile), so `--ship --apply` would discard someone's in-game edits — reconcile first, at game-down.
- ⏳ Melee Animation spawn roll: the setting field is `LassoSpawnChance` (zAnimationMod.dll; Keyed label "Lasso
  Commonality"), or preset `NoLassos`. Set to 0 at game-down, settings first, then the cut (step 4 above).
NEXT: at game-down, reconcile the live CP list vs SHIP, apply, and set LassoSpawnChance 0.
