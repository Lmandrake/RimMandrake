# Result: `RIMMANDRAKE_REWRITE_SKILL_LAYOUT_LAYERS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-layout-layers/SKILL.md`. Run 2026-11-23.

Base: `c96f01bf207b88939f11d67ba3861b14d7765dba`
Also: skills/rimworld-layout-layers/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 18,869 | 20,575 |
| words in linted prose | 2,381 | 2,733 |
| STE violations per 100 words | 4.79 | 1.21 |
| sentences over 20 words | 50 | 7 |
| flagged lines (mechanical) | 17 | 13 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 |

In each long sentence that stays, the lint joined a bold lead to the next sentence. The 13 flags are emphasis marks on the
worst traps, and the heading "This is a CHECK, not a gate". Those flags were there before.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "The four things worth carrying in your head" | five bullets follow | "Remember these five things" |
| "one **edifice** per cell" | what an edifice is | defined under the table |
| "Check the IR, not the picture" | what the IR is | `BuildPlan` in `core.py` |
| "refuse on a missing path rather than writing and hoping" | how that fits with "not a gate" | report first; write if asked |
| "same non-edifice trick" | the trick | "the same non-edifice method" |
| "`Room.doors` is declared and always left empty" | what that stops | the two questions are named |
| "Current power use: Low <- actually running" | whether the cooler cools | Off, Low and High are each defined |
| "Transmitters before connectors ... a connector binds at spawn" | what happens to one with no net | the three engine steps |
| "returns `None`, the compiler keeps its old order and writes a warning" | what to do then | "Act on that warning" |
| "A heat wave is the cheap way to make a hot tile" | when to read | read at equilibrium, from steady state |
| "soak" | what a soak is | defined |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `ConnectMaxDist = 6`, the dates, `jawa/list_things` and "~5,000 ticks", with `--also` | 1 lost, exit 1. Check 1 did not see the number, the code span or the dates that history.md also holds. |
| check 2 (`rule_doc_lint.py keep`) | the same copy, with `--also` | 5 lost, exit 1 |
| check 1, check 2 | the rewrite, with `--also` | 24 items, 0 lost; 160 spans, 0 lost (both run again after the last edit) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_retired_era_gone.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_game_names_prose.py` | the first draft | exit 0 each |
| rimplace selftest, `selftest_structureinjections_lint.py`, `selftest_inhabited_augmentation_wiring.py`, `selftest_inhabited_augmentation_paint_list.py` | the first draft, with the comment edits in rimplace | 62/62; exit 0 each |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning. The reader checked the
corrections against the decompiled source, the rimplace code and the companion source.

| finding | repair |
|---|---|
| significant: the power_net unit was inverted | 1 W reads as 1/60000; multiply by 60000. The same fault in `skills/rimbridge/references/traps/reading-results.md` is repaired |
| significant: "the engine does not read `isEdifice`" reads as RimWorld | "rimplace does not read" |
| mild: in `layer-mechanics.md` the 690 W reading stood under the wrong claim | moved under the two-nets line |
| "stays on that dead net" read as permanent | a conduit can join that net to a source |
| a connector binds on the next frame, not at spawn | said |
| a new transmitter wipes a conduit in its cells | said |
| "answers on the defaults" does not hold for `x`/`z` alone | "a tool that has defaults" |
| Dubs Bad Hygiene rows are unverified too; current map only | said |
| `room_get` skips outdoor rooms | said, in the gap column |
| no "no finding": `wall_mount` gives `room-not-sealed` in a declared room | `rimplace-gaps.md` repaired |

The same reader then read each of those repairs. All held but one: "only if a conduit later joins that net" was too strong. That
line now says to join the net to a source, or to place the connector again, as the reader proposed. No reader read that last
repair, nor one sentence of the `inspect_string` trap and one of the power rate line, each split in two after the second read began.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| a Battery is a connector / a Battery transmits | it transmits | 1: def dump, `Battery` `transmitsPower` True |
| a late transmitter never claims a connector / it claims one with no parent | the second | 1: `PowerNetManager.TryCreateNetAt` |
| `Low` is "actually running" / `Low` with a backwards cooler | powered, not moving heat | 1: `CompTempControl.CompInspectStringExtra` |
| the roof lint never under-warns / the engine fills through roofed cells | wrong both ways | 1: `RoofCollapseUtility`; a one-wall plan gave no finding |
| refuse a write on a missing path / none of this may become a block | report, then write if asked | 2: the owner's ruling of 2026-08-26, in the file itself |
| "four things" / five bullets | five | 1: the list |
| no `CONDUIT` in the palette; no terrain layer but the floor; conduit over a wall cannot be authored | false now | 1: `palette.json`, `core.py`, `place_overlay`; a test plan gave 0 findings |
| `jawa/power_net` is NOT deployed; no pipe tool; no `usesOutdoorTemperature` | false now | 1: the ArchBig DLL of 2026-11-23 and the companion source |
| `set_substructure_batch` skips silently | refuses and counts, with `success: true` | 1: `JawaBenchMapTools.cs` |
| the battery of the template is inside / the template puts it outside | outside, on the bus | 1: `nursery.lua` |
| `layer-mechanics.md`: a net resolves on tick | on the next frame, paused too | 1: `Map.MapUpdate` |
| four wrong designs / five wrong designs | both counts kept, in history.md, as two dates of one sitting | 5 |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new), `references/layer-mechanics.md`, `references/pipe-networks.md`, `references/rimplace-gaps.md`,
`skills/rimbridge/references/traps/reading-results.md` (one unit), `design/Jawa/templates/nursery.lua` (two comments),
`design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md` (a stale case count), and in `src/RimMandrake/Utils/rimplace/`: the README
(the same count), comments in `netinfo.py`, `plan.py` and `prelude.lua`, and one plan-note string in `plan.py`.

## Could not determine

- Which transmitter the dead coolers of 2026-08-26 had bound to. The battery's own net is likely. Only a live test shows it.

## What this run did not test

- No live game was driven. The live figures are the old ones. No live paint of a conduit overlay was made.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.
