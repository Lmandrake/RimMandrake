# Pyrelands 0.1.0: open judge gaps, sorted

Source: the latest coverage verdict, `rm-coverage-judge-1794594804` (2026-11-13 10:33 PST), copied to `evidence/` because its only copy is untracked in `/home/mandrake/rm/bench`. It met 20 of 41 rows and left 14 gaps, all "criterion sound". It judged a slightly earlier tree: the one Designer run since (rm-role-designer-1794596464) changed only the worldgen wording and treated the verdict as advisory, so every gap below still stands on the locked files (g5 and g12's sheet lines are still there, checked by reading `sheet.md`).

Sort rule (same in every mod): **PROBLEM** = without the fix a defect a player would reject (or find strange or disappointing) can ship unnoticed; stays in 0.1.0. **POLISH** = improves play, not part of passing, needs his confirmation. **NEXT VERSION** = shifts or extends the vision. **CORRECTION** = the bar's or test's own text is wrong, contradictory or reads something that does not exist.

| gap | bars it touches | sort | reason |
|---|---|---|---|
| g1 | ash field, burn line, ruins, weather, ash_ground_and_blowing_ash, ruins_stand_blackened, three_skies | CORRECTION | Four scenes count a loose-ash def the build deleted, so they read zero whether ash works or not; the fix swaps in the ash-depth reading. |
| g2 | ash field, plant and animal rosters, fire-hawk, populations_are_the_biomes_own | PROBLEM (unsure: CORRECTION) | The inventory predates the code: the foreign-arrivals guard that keeps other kinds out is untested, and an outside animal wandering in breaks "whole on its own". Re-auditing the inventory is procedure (Correction); anything it turns up beyond the vision would be next version. |
| g3 | ash field, ash_fertile_when_watered, fresh_burn_compounds_with_black_rain | CORRECTION | Four oracle numbers disagree with the ruled and built values, so a correct build would fail. |
| g4 | plant roster, ember-grass regrowth, grass_carpets_and_regreens | PROBLEM | His 2026-11-13 ruling (grass grows swiftly on dry ash, bursts only where watered) has no reading; grass crawling on dry ash would disappoint. |
| g5 | biome self-contained, settings gate | CORRECTION | Two sheet lines disagree on whether the ships-off world switch is checked; one offline check settles it. |
| g6 | furnace-beast | PROBLEM | Its immunity to its own heat ships untested; a furnace-beast burning in its own fire would look broken. |
| g7 | animal roster, flamefang_bite_carries_venom | PROBLEM (unsure: CORRECTION) | The leaf promises venom stops worsening when treated, and nothing tests it; a venom that tending does not help would disappoint. Cutting the clause instead would be a Correction. |
| g8 | weather, three_skies | POLISH (unsure: PROBLEM) | The black-rain test has no clear-sky ash control, so ordinary dry wear could pass for black rain washing ash away. A player would hardly notice the difference. |
| g9 | plant roster, populations_are_the_biomes_own | PROBLEM | The switch that evicts other mods' plants is never shown working; foreign flora in the Pyrelands breaks the vision. |
| g10 | settings gate | PROBLEM (unsure: POLISH) | The roster toggle is said to stop every mechanic and no scene turns it off; a switch that does nothing breaks the Mod Settings rule, though few players will flip it. |
| g11 | art and text | CORRECTION | The coverage line cites a census scene that takes no picture; reword it or add the captures. |
| g12 | ullai herd giant | CORRECTION | Two sheet and record lines are now false (the description no longer promises migration); delete them and add one absence check. |
| g13 | (sheet only) | CORRECTION | The sheet's showcase-3 description does not match what the scenes stage. |
| g14 | (exam) | CORRECTION | The exam was taken on an older tree and sheet; rerun it (stage 4, where the concept stands). |

Counts: PROBLEM 6 · POLISH 1 · NEXT VERSION 0 · CORRECTION 7.

## Other open lines (not judge gaps)

| line | where | suggested sort | reason |
|---|---|---|---|
| The walk has no bar for ullai drifting, the furnace-beast's sleep-ignition, the sand shovel, the firefoam sprayer or the fire-rite hook | `sheet.md` ## open | CORRECTION | The leaves are locked; only the walk's bar list lags (agents may add bars, owner 2026-10-26). |
| A week-old scar is about 60% green; nearly-all-green is playtest tuning | `sheet.md` advisory | POLISH | Already advisory; listed in `polish.md` as a tuning candidate. |
| The pending note still names the 2026-11-06 verdict's five gaps and the worldgen question | `stage.json` pending_decision | not a gap | Stale: the worldgen question was answered by card 2026-11-13. |

## Round 6: rm-coverage-judge-1794750987 (2026-11-15 13:56Z, not covered, 18 gaps)

Sorted 2026-11-15 under the Evidence-for-Ask rule (`RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`).
This is a Conductor sort, not his. Same sort rule as above. Every gap reads "criterion sound", and the judge's smallest fix
is a `scenes.json` or `tree.json` edit (a re-pin; Stage 3 owes it). Judging is STOPPED (REFUSAL_NOTHING_COULD_EVER_PASS,
`evidence/coverage_judge_refusal_2026-11-15_round6.json`). This sort releases nothing.

| gap | bars | sort | reason |
|---|---|---|---|
| g1 | inv_furnacebeast | PROBLEM | The furnace hide and the hide heat bank ship with no scene or check, so a broken heat bank, the biome's gift to the ship, could ship unnoticed. |
| g2 | inv_biome_self_contained | PROBLEM (unsure: CORRECTION) | The acoustic payload and the generic text ship unchecked. The mutator ports are inert under the no-worldgen ruling, so their row is an inert or absence check. |
| g3 | inv_firehawk_ember | POLISH | `sc_firehawk` already fails a drop that is not on fuel. "Largest" fuel against any fuel is a difference a player would hardly notice. `polish.md`. |
| g4 | inv_settings_gate, inv_furnacebeast, walk | PROBLEM | "Switch the other mechanics off and on" names no switch. A switch that does nothing breaks his Mod Settings rule. Map each switch to a scene control or to `T_SETTINGS_SWEEP_OFFLINE` (built, 41 settings). The cross-biome default stays OFF, as he carded. |
| g5 | inv_plant_roster, inv_animal_roster | PROBLEM | Grass withering under a roof and the herds' slow thirst are read only in `sc_walk`, with no control. Grass killed by fire, or a herd that was never thirsty, would pass a broken mechanic. |
| g6 | inv_ash_field, ash_ground_and_blowing_ash | PROBLEM | The scene accepts "most cells" deep ash against the sheet's "almost all" and the 0.85 bar (visit 1 measured 83%). The water ring passes on a map with no water. This tightens the scene to the bar and does not loosen it. |
| g7 | inv_ash_field | PROBLEM | Ash drawn as ground cover and as dust on plants is the biome's core look, and no scene expects it. |
| g8 | inv_weather, no_ordinary_rain | PROBLEM | Forced weather can choose ordinary rain (question 4). The code fix was shown live, and `sc_no_rain` still owes the case. |
| g9 | inv_burrowers_heat_dome, ashwallow_dives_unharmed | PROBLEM | The leaf promises a dome stance, but the dome sprite is the standing body, so the scene can neither see the stance nor fail it. The scene must refuse the standing body, and the dome art is owed. |
| g10 | furnacebeast_warms | CORRECTION | The claim already holds by defs: body size 6 against at most 2.5 for every other roster animal. Only the scene's expect is narrower than the leaf. |
| g11 | inv_firehawk_hunt_rewards | PROBLEM | His card 2026-11-14 promises a letter naming the hawk and the ember, and a valuable crestfeather of beauty. `T_FH_LETTER` checks only the keys and the toggle, and the scene reads neither the wording nor the value. |
| g12 | inv_art_and_text | PROBLEM | Art shipped after his 2026-10-16 approval rests on no judge. The crestfeather uses placeholder art. Art judging is owed before anything reaches him. |
| g13 | burn_line_walks | PROBLEM | The flagship lead scene takes no capture, though `owner_part` names the face he picked, so he is never shown it. |
| g14 | fresh_burn_compounds_with_black_rain | CORRECTION | A seven-day scene runs without the vitals and incident guard the script audit asks for. This is test text, not player-facing. |
| g15 | inv_plant_roster, grass_carpets_and_regreens | PROBLEM | "Dense grass" has no number and no control against the density enforcer's own fill. Without them, thin grass, which his words say would disappoint, could pass. |
| g16 | inv_ullai_herd_giant, ullai_cross_the_map_as_vanilla_herds | PROBLEM | The mod's own herd filter is never checked against the vanilla migration he kept ("Yes, let them cross", 2026-11-14), so the filter could silently block the ullai. The cut world-map leg needs `T_CUT_STAYS_CUT` named in coverage_rest. |
| g17 | (sheet and tree) | CORRECTION | The sheet and tree do not state behaviours the scenes already test. All of them are in `record.json`'s inventory, so this is not Divergent. It is a text sync, so the exam can probe them. |
| g18 | (showcases) | PROBLEM (unsure: CORRECTION) | The contract says to add showcases while a candidate exercises 3 or more new parts. The "solace" one would, and `record.json` failure mode 2 names that solace as what the biome must read as. |

Counts: PROBLEM 14 · CORRECTION 3 · POLISH 1 · NEXT VERSION 0.

What would let judging resume: repair and calibrate the coverage brief's criteria (the alarm reads "criteria repair due";
contract calibration is UNTESTED), so that one round can pass when the gaps are fixed. Then fix the 14 PROBLEM and
3 CORRECTION gaps in Stage 3 under one re-pin, then make one recorded release.
