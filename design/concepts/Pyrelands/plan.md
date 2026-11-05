# Pyrelands: plan (stage 3)

Tree `design/concepts/Pyrelands/tree.json`, sheet `sheet.md`, scenes `scenes.json`, floor `floor.json`. The biome is
built; this plan is the proof work and two owed changes, nothing new.

## Owed changes (Relentless builds them from the tree)

1. **Black rain stops wiping the fresh-burn bonus** (d_blackrain_stop_wipe, OWNER:1793898829233582581). In
   `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs` drop the rain accumulator's fade of the burn bonus
   (rainBudget 12 rain-hours); the bonus keeps its own 6-day clock and stacks on the watered lift. Leaf
   `fresh_burn_compounds_with_black_rain`, measured through `ash_fertility_probe`.
2. **Firebreak excised** (d_firebreak_cut, OWNER:1793898832335289326, delegated, undoable). Delete
   `src/RimMandrake/Pyrelands/Defs/TerrainDefs/Firebreak.xml`, the `FirebreakDefName` special case in
   `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs`, its Mod Settings line and About text, and switch the
   fire-hygiene pads in `validation.py` and `human_review.py` (`_firebreak`) to a vanilla floor. Save compatibility: a
   save holding firebreak cells loads them as a missing terrain; state the outcome (`save_compat`). The firefoam sprayer
   stays (scope not opened). Leaf `paved_strip_holds_the_line`.

## Walk text owed (needs his word)

- North star bar `pyre_fresh_burn_feeds_the_field` reworded to the compound ruling and re-validated by his card
  (d_bar_reworded, commit 9232933404).
- No bar exists for ullai drifting to old burns, the sand shovel, the firefoam sprayer or the fire-rite hook
  (c_bars_vs_capabilities). Agents may add bars; until one lands, `ullai_graze_old_burns` roots at the cast bar.

## Order

1. `ash_fertility_probe` (instrument; first): per-cell base, watered lift, burn bonus and age, rain flag.
2. The two owed changes above.
3. Foils and starts on existing scenes (item `PYRELANDS_SCENES_BUILD_EVERY_FIRE_A_FOIL`): every acceptance scene in
   `scenes.json` naming that item lacks its control, start assertion, vitals/incident guard or restore snapshot (stage 0
   script audit); new entry points `paved_strip`, `firefoam_sprayer`, `rite_hook_alone`.
4. The three showcases and the walk (item `PYRELANDS_SHOWCASES_BUILD_THREE_PYRE_FACES`): `walk_season` on his full
   list with a mid-way reload, a second pass and a second order.
5. Close or re-bucket the stale items: `PYRE_OPENING_FRONT_BUILD_SMOKE_ON_ARRIVAL` (resolved by `sc_burn_line_walks`
   reading the opening front), `PYRELANDS_GREEN_MINIMAL_1`, `PYRELANDS_GREEN_FULL_1`, `PYRELANDS_NORTHSTAR_TRIAL_1`
   (FOUNDRY-era; Relentless's game_prove lane).

## Reuse

`src/RimMandrake/Pyrelands/validation.py` already holds a component per bar (`shows=`); scenes cite those functions.
`validation_core.py` gives the log tap, site prep and teardown; `_teardown` restores settings, weather and fire only,
so the snapshot restore for terrain and things is part of step 3.

## Risks

- Every bar was last green 2026-10-15 on an isolated site with compressed clocks (failure mode 1): the walk on his full
  list is the only check of ordinary play.
- Clock warps are risky (his words, OWNER:1791855166951137487): each wait carries a vitals and incident guard.
- The fire-hawk flies: its scene reads job and carried thing only; no flight is watched without him.
- `max_overlap` and `min_new_after_first` are UNMEASURED first guesses.

## Showcases

1. `burn_line` (his flagship pick, d_flagship_burn_line): the front walks, scorch-fruit comes up rapidly in the
   scar right behind it, and the scar greens over the following days. 2. `fire_cast`: hawk, ashwallow, ullai. 3. `sky_and_shelter`: three skies, the furnace-beast, a
   blackened ruin. The rest (sand shovel, firefoam sprayer, rite hook, settings, art, the excised firebreak) is in
   `coverage_rest`.
