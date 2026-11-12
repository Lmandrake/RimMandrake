# PIT_TEMPERATURE_SOFTENING_1: fresh-eyes judge (2026-11-12)

I read STATEMENT.md, NOTES.md, the evidence folder and `src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py` (to see what each row checks; I did not run the live proof). I did not read DONE.md or BROADEN.md. I re-ran the script's pure `verdicts()` function offline on the four recorded results (run10, run11, run13 desert; run14 AridShrubland). Every one gives A2/A3/A4 PASS/MOD under the current code, which refuses unread or off-clock samples.

All four runs used the same 12-mod list: Harmony, Core and the 5 DLCs, RimBridgeServer, SimpleCameraSetting, GimmeSomeSlack, FlowWorks, Patches. That is the `flowworks` tier, which is what GREEN-MINIMAL means (flowworks_finish_board F6). All four ran on DLL `ea772b7c`.

## Lines

- **A1 true.** `PEX_A1_defs_resolve` PASS in all four runs: `found: [RM_ExposedPrisoner, RM_PitExposure]`, `notFound: []`, on the 12-mod tier list.
- **A2 true.** Three desert runs (lat 47.8, 23.1, 25.0), 06:00 to 12:00. The open pit A stays within 0.07 C of outdoors at every hourly sample. It rises 7.8 / 7.55 / 8.4 C. The roofed twin B rises only 0.47 / 0.61 / 2.26 C and trails outdoors by 4.7 to 5.5 C. Both pits read dry and full depth (8 notches) at every sample. `outdoorRoomA=True`, `outdoorRoomB=False`.
- **A3 true.** In the desert runs, prisoner PA in the open pit loses 4.5 / 4.5 / 2.7 resistance. PB (roofed twin) and PC (normal walled cell) lose 0.0. PA was "hurting" over the hours when ambient was above its safe max. PA's safe max is 38 C against 46 C for PB and PC. That is the mod's 8 C comfort narrowing in an open pit (RM_PitExposureMath.DefaultNarrowing, owner Q1), not a gear difference. The loss happens only while the heat hurts (owner Q2). None of the three prisoners was lost or recruited.
- **A4 true.** All four runs agree. At 12:00 the non-psychopath colonist in a Charity ideoligion has `RM_ExposedPrisoner -3 "<prisoner> left exposed in a pit"`. The psychopath in the SAME ideoligion lacks it, and so does a colonist of an ideoligion with no Charity precept. The run13 Needs panels show the same in-game: Kiri has "Oleirmea left exposed in a pit -3"; Lex and Snap do not.
- **A5 true.** The `toggle_pit_exposure` chain ran live on the flowworks tier with run_validity CLEAN, acceptance GREEN, PASS 2 / FAIL 0 / UNMEASURED 0. On: a spawned colonist carries RM_PitExposure. Off: the hediff is absent. The chain reads the driver's four PEX rows as PASS (run13 and run14 chain files, mod hash `512ff10a`, DLL `ea772b7c`).
- **A6 cannot tell.** Only the owner can judge whether the mood number reads as cruel at the right strength. `run13_a6_run13_panels.jpg` is a fair thing to show him: three Needs panels, the prisoner's health showing "Pit exposure (exposed)", and the prisoner tab. He also needs two facts the panels do not show. First, the -3 lasts 1 day. Second, it stacks once per prisoner up to 5, so five pit prisoners give -15 (`broaden_stacking_after_fix_five_memories.json`).

## Notes: staging and freshness

- **Staged conditions (declared in the proof).** The tile's mean temperature was set to 28 C, the clock jumped to midsummer, the storyteller was off and colonist needs were topped up. Every tick after the jump is simulated, so these are declared exceptions, not hidden ones.
- **PC's zero loss.** PC loses nothing partly because no warden was set to reduce resistance; vanilla never lowers resistance without a warden. So A3 isolates the pit effect: equal (zero) wardening, and only the pit hurts. It does not compare a pit against a wardened cell.
- **Why the open pit tracks outdoors.** Pit A reads the outdoor temperature almost exactly. That looks like vanilla's outdoor-room rule for a fully unroofed room more than a mod coupling dial. A2 is still true as stated. Whether the "coupling multiplier" Mod Setting changes anything in an open pit is not shown.
- **Run14 is not a desert.** It was AridShrubland with PermanentSummer at lat 10, and PA hurt only from 14:00 (drop 0.85). A2 rests on runs 10, 11 and 13, which were deserts.
- **The DLL has moved on since the runs.** The evidence DLL `ea772b7c` is the parent of 60bbc5b684. HEAD's committed DLL is `f393bbe6`. 60bbc5b684 touched only hose source (CompHoseReel.cs, HoseEnds.cs, two SelfTest files), so the pit code is unchanged. Under the suite's own stamp rule, though, these rows will not count for HEAD's DLL until it is deployed and re-run.
- **Flooded-pit escape (outside these lines).** Run8 (rain-flooded pit A) lost its prisoner: the pit brimmed overnight and PA swam out and left the map. This is already filed as RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT.
- **Still frames.** The site stills cannot show the roof over pit B; that comes from the room data (`outdoorRoomB=False`), not the picture.

The machine-checkable lines A1 to A5 hold on the evidence. A6 is the owner's look, and the panels are ready for it.

would show: yes
