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
