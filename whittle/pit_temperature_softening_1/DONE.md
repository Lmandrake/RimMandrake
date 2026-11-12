<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A1 (L1):** jawa/get_defs on the minimal list resolves the exposure hediff and RM_ExposedPrisoner thought. | evidence: `whittle/pit_temperature_softening_1/evidence/final_run10_pit_exposure_result_20261112T005328.json`
- true: **A2 (L2):** At desert noon an unroofed pit's temperature moves faster than a roofed twin. | evidence: `whittle/pit_temperature_softening_1/evidence/final_run10_pit_exposure_result_20261112T005328.json` `whittle/pit_temperature_softening_1/evidence/final_run10_site_noon.jpg` `whittle/pit_temperature_softening_1/evidence/final_run10_player_view_from_review_save.jpg`
- true: **A3 (L2):** An occupant's resistance falls faster in the pit than in a normal prison cell. | evidence: `whittle/pit_temperature_softening_1/evidence/final_run10_pit_exposure_result_20261112T005328.json`
- true: **A4 (L2):** A compassionate colonist gets the RM_ExposedPrisoner thought and a psychopath does not. | evidence: `whittle/pit_temperature_softening_1/evidence/final_run10_pit_exposure_result_20261112T005328.json` `whittle/pit_temperature_softening_1/evidence/broaden_stacking_after_fix_five_memories.json`
- true: **A5 (GREEN-MIN):** The FlowWorks north-star bars for pit exposure pass on the minimal list. | evidence: `whittle/pit_temperature_softening_1/evidence/pit_exposure_chain_reads_driver_rows.json` `whittle/pit_temperature_softening_1/evidence/toggle_pit_exposure_flowworks_tier.json`
- unseen: **A6 (L4):** The owner judges the provisional mood number reads as cruel at the right strength. | evidence: `whittle/pit_temperature_softening_1/evidence/broaden_stacking_after_fix_five_memories.json` (the number he would judge: -3 per exposed prisoner, five at most, -15; his judgement is owed: see BLOCKED.md)

## What the runs show (final run 10, flowworks tier, 12 mods, Desert quicktest map, midsummer, clear sky)
- A2: the open pit stayed within 0.07 C of outdoors from 06:00 to 15:00 (42.0 -> 52.9 C); the roofed twin trailed by up to
  5.5 C (45.0 -> 47.4 C). The game reports the open pit as an outdoor room and the twin as an indoor one.
- A3: the open-pit prisoner's resistance fell 10.15 -> 5.65 while the heat hurt it; the walled-cell prisoner (12 -> 12)
  and the roofed-twin prisoner (12 -> 12) lost none, though both had mild heatstroke by 15:00. Both pits stayed dry and
  8 notches deep all day (recorded every hour).
- A4: at 12:00 the colonist of a Charity ideoligion had "Camiño left exposed in a pit" (-3); the Psychopath of the same
  ideoligion did not; a colonist of an ideoligion with no Charity precept did not.
- A5: validation.py's new `pit_exposure` chain reads all four PEX rows as PASS from that result at the current mod hash
  and loaded DLL; `toggle_pit_exposure` (exposure on/off) PASS 2/2 on the same tier.
- The same rows also passed on runs 4 and 5 (`evidence/run4_*`, `evidence/run5_*`), before the thought-label fix.

## Fixed this round
- RM_ExposedPrisoner collapsed every prisoner into ONE memory (vanilla groups same-label memories about different pawns,
  then `stackLimitForSameOtherPawn` 1 trims the group). The label now names the prisoner; six prisoners give five
  memories, as the def intended (`dc5b4685e4c9`).
- Filed `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT`: rain filled a 4 m open pit in one night and the prisoner swam
  out (run 8, `evidence/run8_rain_flooded_pit_A_20261111T233048.json`).

## What I'm least sure about
- "Desert noon" is staged in part. The map is a Desert quicktest tile (two rolls), but the tile's mean temperature was set to
  28 C and the clock moved to midsummer, so the heat is that of a hot desert, not the quicktest's mild spring. The map
  looks like a desert; the numbers are a hot one's. Run 1 (`evidence/run1_*`), a real spring desert at 25 C, never hurt
  anyone, and resistance did not move there. That is the design.
- The prisoners were placed in the pits (spawned as prisoners), not captured and carried down through the game's own
  route. Capture-down is another item's.
- The player-view capture shows the HUD (11 AM, clear, 122 F) and a colonist's inspect pane. No bridge tool would open the
  prisoner's own Prisoner/Health tab, so its exposure and resistance come from `jawa/inspect_string` and the proof's read
  surface, not from a screenshot.
- In the final runs the colonists were not drafted; wardens were free to work, and the default interaction mode never recruits, so
  no warden chat moved resistance. A colony actively recruiting would see the pit's loss added to warden losses.

## What I did not test
- Mod Settings changed mid-game (narrowing, resistance rate, exposure off/on); only the on/off toggle row.
- Cold nights (hypothermia), clothed or gene-tolerant prisoners, slaves, guests, caravans.
- The memory's expiry one day after exposure ends (seen still present at 6 h, not followed to 24 h).
- The full capture -> warden -> recruit route.
- A6 itself: the owner's judgement of the mood number.
