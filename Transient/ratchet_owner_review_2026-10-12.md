# Ratchet pilot - owner review queue, 2026-10-12

Only rows that need HIS eyes, hands or ruling. Machine-checkable rows are not here. Paths are the
mirror `D:\Luke\dev\RimMandrake\...` (appears after `./mirror sync`). Ranked: the first rows gate
"full cycle done" for the pilot (and so the account reset he deferred to next week).

| # | what you look at | where | what you decide |
|---|---|---|---|
| 1 | Pyrelands creature art of 2026-10-11 (commit 68ee19c27d), provisionally accepted so selftest_art_checks is green | In game, Pyrelands review map; art files under `D:\Luke\dev\RimMandrake\src\RimMandrake\Mods\` (Pyrelands textures); contact sheet via the art ledger | Keep as final, or send back for regen. Keep = the provisional flag is lifted. |
| 2 | Canal wet front: after the 2026-10-12 fix (4de309155e) water should advance one cell per pulse from the mouth | In game: build a flat dead-end canal with a mouth source, watch ~10 pulses (a joint session; the machine live recheck runs first) | Is that the look you meant? (his own ruling, so this is a confirm) |
| 3 | Pyrelands ash redesign result: deep ash everywhere, fresh-burn bonus fading with Black Rain | In game on a Pyrelands tile after PYRE_ASH_BUILD lands | Does a burned field read as fertile and a watered one grow? Numbers are all Mod Settings; say which feel wrong. |
| 4 | GimmeSomeSlack owner-walk art sheet: 12 subjects, 4 decided so far | `D:\Luke\dev\RimMandrake\Transient\biome_ffar\gss_owner_walk_art_sheet_2026-10-11.html` | Pick a version per remaining subject (8 left). |
| 5 | embergrass regrow targets: measured 34% day 3 and 59.8% day 7 vs targets 25% / 60% | Numbers only; harness `Transient/northstar` Pyrelands regrow row | Rule the thresholds (the 50% survivor cut-off is an agent's guess). |
| 6 | Pilot verdict itself: three mods accepted together as one version | Design doc `D:\Luke\dev\RimMandrake\design\RimMandrake\ratchet_workflow_and_token_burst_design_2026-10-11.md` section H | Accept the pilot (then account reset next week) or name what is missing. |

Not owner rows (machine owns): Pyrelands north-star FAIL/UNMEASURED rows, FlowWorks river UNMEASURED
site rows, ash ladder harness retirement, IDEO_DEITY NRE, taskkill mishap (already filed as a lesson).
