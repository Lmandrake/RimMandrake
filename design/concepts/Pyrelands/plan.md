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
   stays: his root ending (OWNER:1793950669508519029) names it as the way to the scorch-fruit. Leaf
   `paved_strip_holds_the_line`; a fire-hawk ember carried six cells past the strip is expected and is the sprayer's
   job (`firefoam_sprayer_reaches_the_fruit`).
3. **Biome text** (item `PYRELANDS_TEXT_FIX_ENGINEERED_NEVER_SAID`): the RM_Pyrelands description says the savanna was
   genetically engineered (leaf `biome_text_says_engineered`); About.xml and the furnace-beast description stop
   promising the world migration his card cut on 2026-10-23 (commit 84cc81013d).

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
   script audit); new entry points `paved_strip`, `firefoam_sprayer`, `rite_hook_alone`. Item
   `PYRELANDS_SCENES_BUILD_EIGHT_JUDGE_GAPS` (coverage judge rm-coverage-judge-1793932124): new `furnace_thermal_bed`
   (charge, heat immunity against an ullai in the same fire, bed smoulder; control furnace thermal off); `cinderfall`
   gains lightning counts, the black-rain ash wash and clear-sky and vanilla-rain fire pads; `firefoam_sprayer`,
   `sand_shovel` and `rite_hook_alone` become acceptance scenes with controls. Each scene's `restore` now says what it
   puts back; `sc_no_rain` runs on a disposable map, `sc_walk` keeps a pre-walk save.
   Item `PYRELANDS_SCENES_BUILD_VENOM_GIANT_DUST_DOME` (coverage judge rm-coverage-judge-1793981105): new
   `flamefang_venom` (bite applies RM_FlamefangVenom, severity rises; control a non-venomous bite of like size);
   `ullai_and_giant` gains a live body-size read of RM_FurnaceBeast (6) and a classic-restore control (3.2) instead of
   echoing the XML; `fire_tick_effects` asserts a clean, clear-weather pad and runs the ash-dusting-off control against
   an unburned twin pad; `heat_dome` asserts no fire on its pad and stands as its own scene (`sc_heat_dome`), with
   the dome switch off as its control.
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
   scar right behind it, and the scar greens over the following days. 2. `fire_cast`: hawk, ashwallow (dive and dome), ullai, the giant furnace-beast's size. 3. `sky_and_shelter`: three skies, the furnace-beast (warmth, heat cycle, bed), a
   blackened ruin. The rest (sand shovel, firefoam sprayer, rite hook, settings, art, the excised firebreak) is in
   `coverage_rest`. The vanilla new-world placement switch is outside the promise (d_worldgen_outside_promise): no
   scene, no check; its default is `PYRE_WORLDSWITCH_DECIDE_ON_BY_DEFAULT`.
