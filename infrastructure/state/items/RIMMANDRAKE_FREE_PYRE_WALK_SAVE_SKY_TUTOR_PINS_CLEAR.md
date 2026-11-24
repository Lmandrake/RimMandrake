# RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR

## spec

The walk save of Pyrelands 0.1.0 (`PYRELANDS_0.1.0_VISIT8_WALK_FULL.rws`, ArchBig Saves folder) needs a small restage before
the owner opens it. Staging only: no mod code, no bar. Read from the save file by the Stage 7 reader, 2026-11-24:

1. **The sky is pinned clear.** The save's storyteller is Tutor (the site fixture's quiet storyteller), and under Tutor
   vanilla always picks Clear (measured in RIMMANDRAKE_FREE_PYRE_SITE_SKY_TUTOR_PINS_CLEAR_FOREVER, which was dropped because
   test sites are disposable; his walk save was not weighed there). On this save he would never see ash fall, cinderfall or
   black rain, and the sky is a third of the vision. Set a storyteller such as Cassandra; keep threats quiet if wished.
2. **The creatures station is empty of its creatures.** All 6 ullai stand on 2 cells at the station's left edge, (68,27) and
   (68,30), and the furnace-beast stands at (21,33), left of station 1. Cause: 600 ticks ran between the spawn and the save, so
   the animals dashed to shade (RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL). Spawn them after the advance. He
   said on 2026-11-23 that he will look at the ullai at this walk.
3. Worth adding in the same restage: a station with a walked path of footprints in ash (part 3 of
   RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST, promised to him on 2026-11-08), and plain signs ("walls painted
   RM_FE_Charred" and "VISIT8" mean nothing to a player).

Script to change: a copy of `design/concepts/Pyrelands/version/in_game/visit_8/scripts/walk_save.py`. Keep the old save.

## Reading of the visit 9 save (Stage 7 reader of arrival 2, 2026-11-24 3:12 PM PST)

The walk save is now `D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT9_WALK.rws` (ArchSmall, small list, 18 mods).
The full-list save is out: full-list testing is retired. Restage this one, from
`design/concepts/Pyrelands/version/in_game/visit_9/scripts/walk_save.py`.

- Part 1 stands: storyteller Tutor, weather Clear.
- Part 2 is done as saved: 6 ullai on 6 cells, the furnace-beast and 2 ashwallows in their station. They bolt for shade soon after
  the clock runs (`screenshots/walk_small_closeups.jpg`: the herd is one heap at the station's left edge).
  A station that he can watch with the clock running needs a fence or shade. A fence also keeps the herd in view.
- Part 3 stands (the footprints station, plain signs).
- 4. **No sign is in the save.** `review_label` draws in one game session only; a plain load shows no sign, and
  `walk_twins.py check --mod Pyrelands` exits 2 (COULD NOT LOOK, no station sign). Write the signs as the in-save books
  (the `SIGNS IN THE SAVE ITSELF` part of `JawaBenchReviewLabels.cs`), which survive a plain load.

## Acceptance test

`python3 infrastructure/state/acceptance/RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR.py "<the new save>"` exits 0.
Watched red on the visit 8 save, 2026-11-24: `storyteller Tutor: FAIL; ullai 6 on 2 cells: FAIL`, exit 1.
Part 3: none, it is a look.
Also `python3 src/RimMandrake/Utils/walk_twins.py check "<the new save>"` exits 0. Watched on the visit 9 save, 2026-11-24: the first exits 1
(`storyteller Tutor: FAIL; ullai 6 on 6 cells: ok`), the second exits 2 (no station sign).
