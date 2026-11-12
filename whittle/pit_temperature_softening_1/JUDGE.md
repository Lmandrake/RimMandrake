# PIT_TEMPERATURE_SOFTENING_1: blind judge verdict

Judge: claude-opus-5-5, a fresh-eyes subagent. I did not build this work. I read STATEMENT.md, NOTES.md and the files under `evidence/`. I also read the grading code in `src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py` (lines 100-180), the `toggle_pit_exposure` chain in `northstar/extensions.py` and the `RM_ExposedPrisoner` ThoughtDef, so I could see what each PASS actually checks. I did not read DONE.md or BROADEN.md, and I drove no game. The main record is `final_run10_pit_exposure_result_20261112T005328.json` (mod_hash 512ff10a52..., assembly ea772b7c2d...). `toggle_pit_exposure_flowworks_tier.json` has the same hashes.

## Lines

**A1 (L1): true.** Row PEX_A1 is PASS. `jawa/get_defs` was called with `HediffDef/RM_PitExposure;ThoughtDef/RM_ExposedPrisoner` and returned `found: [RM_ExposedPrisoner, RM_PitExposure]` with `notFound: []`. The running list has 12 mods: Harmony, Core, the 6 DLCs, the bridge, the camera mod, GimmeSomeSlack, FlowWorks and Patches. That is the minimal list plus the FlowWorks tier.

**A2 (L2): true.** The map is Desert. The sample labelled 12:00 was taken at game hour 11.77.
- Open pit A, depth [8,8], dry, outdoorRoom=True: 41.98 to 49.80 C, a rise of 7.82. It never strays more than 0.07 C from outdoors (41.99 to 49.83).
- Roofed twin B, same depth, openRoof 0, outdoorRoom=False: 45.00 to 45.47 C, a rise of 0.47. It trails outdoors by up to 5.5 C.

Both measures agree: by rise and by lag, A moves with the noon swing and B does not. Two qualifications:
- The PASS test only checks lag: A within 1 C of outdoors, and B lagging at least 2 C more than A. The script's own header (line 32) still says "rises more", which is stale. Run 5 PASSed with the roofed twin rising faster (12.17 against 9.57), because it was catching up from a cold night. Run 3 FAILed over a 9:00 to 12:00 window for the same reason. In run 10 both readings point the same way, so the line holds here.
- Nothing here separates the mod's coupling from vanilla's rule that an unroofed room uses the outdoor temperature. The line does not ask for that split.

**A3 (L2): true.** Over 6:00 to 15:00, resistance fell by:
- PA, in the open pit: 10.15 to 5.65, a drop of 4.5.
- PB, in the roofed pit: 0.
- PC, in the walled prison cell (prison=True, openRoof 0): 0.

PB and PC were also hurting from heat by the end (PC ambient 51.95 against safeMax 46, heatstroke 0.088 and 0.089). They lost nothing, so the drop is tied to pit exposure and not to heat alone. All three had the same conditions, with no wardens.
- The drop is a flat 0.5 per hour from 42 C to 53 C. It does not grow with how far past the comfort range the prisoner is.
- PA's comfort range narrows by 8 C at both ends (4 to 38, against -4 to 46 for the others). That is presumably the exposure hediff working. I am noting it, not counting it against the line.
- In inspect_PA at the end, PA is still in the pit: "Held in a pit: it cannot climb out without a ladder".

**A4 (L2): true.** At noon:
- Human416, whose ideoligion Nova-Archotechnics holds Charity_Important, has `RM_ExposedPrisoner -3 "Camiño left exposed in a pit"`.
- Human413 is in the same ideoligion with the Psychopath trait and has no such thought. This is a fair control, because only the trait differs.
- Human419 (Free Temple, no Charity precept) has no such thought either.
- The only thought is about the exposed prisoner PA. None fired for PB or PC.

Staged parts: the harness added the Charity precept and the Psychopath trait. "Compassionate" here means "belongs to a Charity ideoligion", not a trait.

**A5 (GREEN-MIN): true.**
- All four PEX rows (A1 to A4) are PASS on the minimal list, and `pit_exposure_chain_reads_driver_rows.json` records the same four.
- In the toggle chain, `pit_exposure_on` gave a pawn RM_PitExposure at severity 0.5 after 1000 ticks on an open pit floor. `pit_exposure_off` (pitExposureEnabled=False) gave none. Acceptance is GREEN 2/2 and runValidity is CLEAN.
- Both files have the same mod and assembly hashes.

**A6 (L4): cannot tell.** This line is the owner's own judgment, and nothing in the evidence records it. To settle it, the owner looks at the review save `RM_PitExposure_Review_20261112T005328` (saved at noon) and rules on -3 per exposed prisoner, which stacks to a limit of 5 for -15 (`broaden_stacking_after_fix_five_memories.json`, stackLimit 5 in Pit_Thoughts.xml). The player-view still `final_run10_player_view_from_review_save.jpg` shows the pits and a selected colonist marked "Stressed", but not the thought or its number. The owner must open the Needs tab in the save, or be shown a crop of it.

## Staged or flattering evidence
- The tile's real mean temperature is 0.94 C (a cold, mountainous desert at latitude 47.8). The driver forced it to 28 C and jumped to midsummer day 22. The weather was forced clear, the storyteller was off and wild animals were removed. This is a hand-made hot noon, not a natural one.
- Rain is excluded on purpose. In run 8 rain flooded pit A, prisoner PA climbed out and left the map by 14:00. Run 2 also lost PA. Both read UNMEASURED. The fill is filed separately as RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT. The green result covers a dry pit only.
- One green run follows nine earlier runs, three of which went FAIL or UNMEASURED: run 3 (A2 and A4 FAIL), run 2 and run 8. Those failures are harness or site problems that were later fixed, but only one complete green run exists on this build.
- The site still `final_run10_site_noon.jpg` cannot show which pit is roofed, and a still cannot show temperature or resistance moving. Every claim rests on the JSON samples.
- The map's metadata says "Spring" because it was read before the clock jump. The HUD in the player view says "Summer, 9th of Jugust, 11 AM, Outdoors 122F". This is cosmetic.

## Owed
- A6 needs the owner's look. A crop of the Needs tab showing the thought would make that look quick.
- Small finding, not filed by me (my brief allows only this file): `pit_exposure_live.py` line 32 says PEX_A2 checks the rise, but the code checks lag.

would show: yes
