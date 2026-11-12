<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A1 (L1):** jawa/get_defs on the minimal list resolves the exposure hediff and RM_ExposedPrisoner thought. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_wardened_desert_pit_exposure_result_20261112T032231.json` `whittle/pit_temperature_softening_1/evidence/run18_pit_exposure_chain_reads_driver_rows.json`
- true: **A2 (L2):** At desert noon an unroofed pit's temperature moves faster than a roofed twin. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_wardened_desert_pit_exposure_result_20261112T032231.json` `whittle/pit_temperature_softening_1/evidence/run18_site_20261112T032231.jpg` `whittle/pit_temperature_softening_1/evidence/run17_wardened_desert_pit_exposure_result_20261112T030349.json` `whittle/pit_temperature_softening_1/evidence/run18_rejudged_by_fixed_verdicts.json`
- true: **A3 (L2):** An occupant's resistance falls faster in the pit than in a normal prison cell. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_wardened_desert_pit_exposure_result_20261112T032231.json` `whittle/pit_temperature_softening_1/evidence/run18_a6_panels.jpg` `whittle/pit_temperature_softening_1/evidence/run18_prisoner_tab_20261112T032231.jpg` `whittle/pit_temperature_softening_1/evidence/run17_a6_panels.jpg` `whittle/pit_temperature_softening_1/evidence/run17_wardened_desert_pit_exposure_result_20261112T030349.json` `whittle/pit_temperature_softening_1/evidence/broaden2_roof_the_pit_at_noon.json`
- true: **A4 (L2):** A compassionate colonist gets the RM_ExposedPrisoner thought and a psychopath does not. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_wardened_desert_pit_exposure_result_20261112T032231.json` `whittle/pit_temperature_softening_1/evidence/run18_a6_panels.jpg` `whittle/pit_temperature_softening_1/evidence/run17_a6_panels.jpg` `whittle/pit_temperature_softening_1/evidence/run17_wardened_desert_pit_exposure_result_20261112T030349.json`
- true: **A5 (GREEN-MIN):** The FlowWorks north-star bars for pit exposure pass on the minimal list. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_pit_exposure_chain_reads_driver_rows.json` `whittle/pit_temperature_softening_1/evidence/run18_toggle_pit_exposure_flowworks_tier.json`
- unseen: **A6 (L4):** The owner judges the provisional mood number reads as cruel at the right strength. | evidence: `whittle/pit_temperature_softening_1/evidence/run18_a6_panels.jpg` (what he would judge, as a player sees it: "Cambarseacha left exposed in a pit -3" among Hot -8, Hungry -6, Depressive -12; one per prisoner, five at most, -15, `whittle/pit_temperature_softening_1/evidence/broaden_stacking_after_fix_five_memories.json`; lasts one day after exposure ends, `whittle/pit_temperature_softening_1/evidence/broaden2_roof_the_pit_at_noon.json`). His judgement is owed: see BLOCKED.md.

## What changed this round, and why
The earlier proof never let a warden work a prisoner (vanilla's default mode for a new prisoner), so A3 compared an
unwardened pit with an unwardened cell, which no player does. Wardens might not reach a pit prisoner, or their chats
might do far less to a miserable one (vanilla scales each chat by the prisoner's mood), and then a wardened cell could
beat the pit. The proof now sets every prisoner to "Reduce resistance" (new `ProofSetInteraction`; the suite's run
passes `--interaction ReduceResistance`) and counts each prisoner's loss from placement. A3 reads UNMEASURED unless all
three were chatted and the pit prisoner no more often than the others. Selftest 40/40.

## What the runs show (run 18: flowworks tier, 12 mods, FlowWorks DLL 8286201b = HEAD 1d966226d1, a fresh Desert map, midsummer, clear)
- A2: the open pit stayed within 0.06 C of outdoors from 06:00 to 15:00 (38.5 -> 45.5 C by noon); the roofed twin trailed
  by up to 4.95 C (41.7 -> 41.8). The game reads the open pit as an outdoor room, the twin as indoor.
- A3, wardens on all three, two chats each: pit 13.0 -> 3.4 (heat hurting her from 06:00), roofed twin 12.0 -> 10.5,
  walled cell 17.0 -> 14.9. At noon her Prisoner tab reads "Reduce resistance only", resistance 4.9, "Held in a pit".
  Run 17 (another desert): pit 11.0 -> 3.4, twin 13.0 -> 12.4, cell 11.0 -> 10.4.
- Roof the pit at noon (BROADEN): the pit's own loss stops at once and stays stopped for 17 h, though the roofed hole
  holds 40-47 C and heatstroke rises. The loss is the exposure, not the heat.
- A4: at noon Manuel (a Charity ideoligion) has "Cambarseacha left exposed in a pit -3"; Montoya, the psychopath of the
  same ideoligion, does not; Thib, of an ideoligion without Charity, does not (`run18_a6_panels.jpg`, left to right,
  then the prisoner's tab).
- A5: `toggle_pit_exposure` (exposure on/off) PASS 2/2, run validity CLEAN, on a calm quicktest; the `pit_exposure` chain
  reads all four PEX rows PASS from run 18 at the current mod hash (ccef5b846b) and loaded DLL.
- Earlier runs 10, 11, 13, 14 (unwardened) and 17 (wardened) re-judge PASS under the stricter verdicts; runs 15 and 16
  (wardened, no placement read) re-judge UNMEASURED (`run18_rejudged_by_fixed_verdicts.json`).

## What I'm least sure about
- "Desert noon" is partly staged: the tile's mean temperature is set to 28 C and the clock moved to midsummer.
- The prisoners are placed in the pits, not captured and carried down.
- The pit prisoner's mood sits near 0 by mid-afternoon, and heatstroke reached 0.26 by 15:00 (0.36 by 22:00 in run 15).
  Several such days would kill her. Vanilla heatstroke is meant to do the harm (spec), but the owner may judge the pace.
- Found and filed, not this item: in run 18 a colonist ended up inside the roofed twin pit and cannot leave, yet reads
  untrapped, so nobody rescues him (`RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE`,
  `run18_colonist_stranded_in_roofed_pit.json`). How he got in is not recorded.

## What I did not test
- Mod Settings changed mid-game (narrowing, resistance rate); only the on/off toggle.
- Cold nights (hypothermia); clothed or gene-tolerant prisoners; slaves, guests, caravans.
- The full capture -> carry down -> recruit route; feeding a downed pit prisoner from the lip.
- Pit rooms over 400 cells, where the coupling multiplier is skipped by design.
- A6 itself: the owner's judgement of the mood number.
