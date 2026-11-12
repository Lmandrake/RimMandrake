<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A1 (L1):** jawa/get_defs on the minimal list resolves the exposure hediff and RM_ExposedPrisoner thought. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_desert_pit_exposure_result_20261112T014420.json`
- true: **A2 (L2):** At desert noon an unroofed pit's temperature moves faster than a roofed twin. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_desert_pit_exposure_result_20261112T014420.json` `whittle/pit_temperature_softening_1/evidence/run13_site_20261112T014420.jpg` `whittle/pit_temperature_softening_1/evidence/run11_desert_pit_exposure_result_20261112T011827.json` `whittle/pit_temperature_softening_1/evidence/run14_aridshrubland_pit_exposure_result_20261112T020521.json` `whittle/pit_temperature_softening_1/evidence/run13_rejudged_by_fixed_verdicts.json`
- true: **A3 (L2):** An occupant's resistance falls faster in the pit than in a normal prison cell. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_desert_pit_exposure_result_20261112T014420.json` `whittle/pit_temperature_softening_1/evidence/run13_prisoner_tab_20261112T014420.jpg` `whittle/pit_temperature_softening_1/evidence/run13_selected_20261112T014420.jpg`
- true: **A4 (L2):** A compassionate colonist gets the RM_ExposedPrisoner thought and a psychopath does not. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_desert_pit_exposure_result_20261112T014420.json` `whittle/pit_temperature_softening_1/evidence/run13_a6_run13_panels.jpg` `whittle/pit_temperature_softening_1/evidence/run13_needs_Human626_20261112T014420.jpg` `whittle/pit_temperature_softening_1/evidence/run13_needs_Human629_20261112T014420.jpg` `whittle/pit_temperature_softening_1/evidence/run14_a6_panels.jpg`
- true: **A5 (GREEN-MIN):** The FlowWorks north-star bars for pit exposure pass on the minimal list. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_pit_exposure_chain_reads_driver_rows.json` `whittle/pit_temperature_softening_1/evidence/run13_toggle_pit_exposure_flowworks_tier.json` `whittle/pit_temperature_softening_1/evidence/run14_pit_exposure_chain_reads_driver_rows.json`
- unseen: **A6 (L4):** The owner judges the provisional mood number reads as cruel at the right strength. | evidence: `whittle/pit_temperature_softening_1/evidence/run13_a6_run13_panels.jpg` (what he would judge, as a player sees it: -3 per exposed prisoner beside Hot -8 and Hungry -6; five at most, -15, `whittle/pit_temperature_softening_1/evidence/broaden_stacking_after_fix_five_memories.json`; his judgement is owed: see BLOCKED.md)

## What the runs show (run 13, flowworks tier, 12 mods, a fresh Desert quicktest map at latitude 25, third roll; midsummer, clear sky)
- A2: the open pit stayed within 0.07 C of outdoors from 06:00 to 15:00 (33.7 -> 46.1 C, a rise of 8.4 by noon); the roofed
  twin trailed outdoors by up to 4.7 C (37.7 -> 39.9 C by noon, a rise of 2.3). The game reports the open pit as an outdoor
  room and the twin as an indoor one.
- A3: the open-pit prisoner's resistance fell 11.0 -> 8.3 once the heat hurt her (from 10:00); the roofed-twin prisoner
  (15 -> 15) and the walled-cell prisoner (14 -> 14) lost none. Her Prisoner tab at noon reads resistance 9.8; her Health
  tab lists "Pit exposure (exposed)".
- A4: at noon Kiri (a Charity ideoligion) has "Oleirmea left exposed in a pit" -3 in her Needs tab; Lex, the Psychopath
  of the same ideoligion, does not; Snap, of an ideoligion with no Charity precept, does not. All three tabs are in
  `run13_a6_run13_panels.jpg`, as the player sees them.
- A5: validation.py's `pit_exposure` chain reads all four PEX rows as PASS from run 13 at the current mod hash
  (512ff10a52) and loaded DLL; `toggle_pit_exposure` (exposure on/off) PASS 2/2, runValidity CLEAN, on a calm quicktest.
- Run 11 (another fresh desert, latitude 47.8) passed the same four rows; so did run 10 (last round). Run 14, on the
  code-review-fixed harness, rolled an AridShrubland at latitude 10 (a mild one: 39.8 C at 15:00): all four rows pass,
  the prisoner hurting only from 14:00 (resistance 12.0 -> 11.15), and its Needs tabs show the same thought pattern
  (`run14_a6_panels.jpg`). The chain now reads run 14. Runs 10, 11 and 13 re-judge PASS under the fixed verdict code, and
  two damaged copies of run 13 read UNMEASURED (`run13_rejudged_by_fixed_verdicts.json`).

## Fixed this round
- The 12:00 "prisoner selected" capture never selected the prisoner: `rimworld/select_pawn` refuses a non-colonist, so
  the shot showed whichever colonist was selected before (run 10's "player view" was Bucky, not the prisoner). It now
  selects by id (`jawa/select_things`) and opens the prisoner's Health and Prisoner tabs and every colonist's Needs tab.
- A fresh map that never rolled a desert was judged anyway: run 12 ran on a TemperateForest and passed every row silently.
  The proof now ends with one UNMEASURED SITE row instead, and the suite's driver entry re-rolls up to 8 times (was 2).
  Run 12's result is not used as evidence.
- A code review of the proof found: a blank outdoor read mid-day dropped out of the A2 lag test (or crashed it); sample
  labels were never checked against the game clock; a southern tile would run in midwinter; a finished run could be
  resumed and write its rows twice. All four now refuse or correct (selftest 31/31, two new cases).

## What I'm least sure about
- "Desert noon" is staged in part: the tile's mean temperature is set to 28 C and the clock moved to midsummer, so the
  heat is a hot desert's, not the quicktest's mild spring (run 1, a real spring desert, never hurt anyone: by design).
- The prisoners were placed in the pits, not captured and carried down. In every noon capture they stand on the pit's
  south row (in the pit, "Held in a pit"), where the shade falls at noon; it reads at a glance as standing on the lip.
- Resistance falls only while the heat is hurting the prisoner (0.5 an hour, flat): a prisoner with a wide comfort range
  loses nothing until the day is hot enough (run 13: from 10:00).
- Rain is out: run 8 showed rain filling an open pit overnight (filed RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT).

- Every run here was on FlowWorks DLL ea772b7c (mod hash 512ff10a52). Another seat's later commit 60bbc5b684 changed
  only hose code and rebuilt the DLL (f393bbe6), so the chain will read these rows as stale until a redeploy and a rerun.

## What I did not test
- Mod Settings changed mid-game (narrowing, resistance rate); only the on/off toggle row.
- Cold nights (hypothermia), clothed or gene-tolerant prisoners, slaves, guests, caravans.
- The memory's expiry one day after exposure ends; the full capture -> warden -> recruit route.
- A6 itself: the owner's judgement of the mood number.
