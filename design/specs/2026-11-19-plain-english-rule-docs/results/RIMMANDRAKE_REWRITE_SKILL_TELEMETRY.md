# Result: `RIMMANDRAKE_REWRITE_SKILL_TELEMETRY`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/telemetry/SKILL.md`. Run 2026-11-23.

Base: `c8588d7e606cba178c204a2a3fa73d34d9985a73`

## Scores

| measure | before | after |
|---|---|---|
| bytes | 5,734 | 8,272 |
| words in linted prose | 477 | 887 |
| STE violations per 100 words | 5.03 | 1.80 |
| sentences over 20 words | 10 | 4 |
| flagged lines (mechanical) | 0 | 0 |
| lines that a cold reader cannot act on (hand count, by the writer) | 8 | 0 |

Four long sentences stay. One is the owner's quote. The lint joined the other three at a bold lead.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "owner picks: hybrid …, 1 s test tier + flight recorder" | what the test tier and the flight recorder are | both defined in §Arming the test tier |
| "compare versions … (`telemetry around`)" | that `around` does not match the mod list | says so, and names `telemetry query` |
| "grade it with `telemetry label <id> tp\|fp`" | which id, and what `tp` and `fp` mean | both given |
| "the friction census `events.jsonl`" | what the friction census is | one sentence |
| "v2 ran 267, 279, 773 done a week" | what v2 is, and what was done | the rimflow version of 2026-10; items done |
| "`<data root>`" | where it is | the command that prints it |
| "needs the P2 companion" | what P2 is | the JawaBench build that has `jawa/telemetry_tier` |
| "(see traps)" | which trap | `references/traps.md`, "Visible windows" |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without "300 chars", `rm-telemetry-health.timer`, "2026-10-11" and "267" | 2 lost, exit 1. Check 1 did not see the timer name or "267". |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1, check 2 | the rewrite | 20 items, 0 lost; 55 spans, 0 lost (run again after the last edit) |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | none | pass; 19 of 19 |
| `selftest_telemetry.py` | the changed files | OK: 153/153 |
| `selftest_skills_by_work.py`, `selftest_retired_era_gone.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py` | the changed files | exit 0 each |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning, and checked each
new statement against the code. No rule was lost.

| finding | repair |
|---|---|
| significant: the draft said that `rebuild` reads the raw files again; it rewinds the cursors on the producers' files | says that telemetryd reads the producers' files again, and does not read `E:\telemetry\raw` |
| significant: "the game records come from ArchBig only" is false for `rm_proc_*`, `rm_game_process_up` and `blind:tps` | only the TPS record comes from ArchBig; the others count any RimWorld process |
| `cli.py` docstring: "only when" is false | "only" is gone |
| "`analysis.RULES` holds every threshold" is too strong | "the alarm thresholds" |
| `traps.md`: `jawa/vitals` alone arms nothing | `jawa/vitals` with `action=arm` |
| "every process runs on the Windows side": the exporter does not | names the daemon, the stores, Grafana and the CLI |
| "it reads each tick" needs TPS attribution | condition added |
| `around` does not filter by `mods` | says so |

The same reader then read each repair: all correct. No reader read two later edits: the words "`telemetry query` prints the
labels", and "telemetryd" in place of "It" in law 1.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `alerts.json` is "read by ops_watch" / no such reader | `telemetry health` shows it; nothing carries an alarm out | 1: `git grep alerts.json`; `analysis.py` docstring |
| WSL "never reads `\\wsl.localhost` from Windows" / the Windows side must not | the Windows side | 1: `wsl_export.py` docstring |
| the extractor is under the agent storage root / under its RimMandrake folder | the RimMandrake folder | 1: the file is at `D:\ClaudeWork\rimmandrake\orch_record\delegation\extract_cards.py` |
| CAMPAIGN is only a canonical save / more cases | the other cases are in `JawaBenchSafetyCore.cs` `Effective` | 1 |
| the diagram omits `ops_watch` / it is a source | added | 1: `make_sources()` |
| `traps.md`: no pawn vitals series yet / `telemetry series --grep pawn` lists them | the series exist; points only while the vitals monitor is armed | 1 |
| `cli.py` docstring: `tier` refuses without the bridge hold / no such check | corrected; no code changed | 1: `cmd_tier` |
| the description says "a TELEMETRY row fires in RimPulse" / RimPulse is retired | the description stays | the special rule of this item: a description changes only with the trigger evals. The body says that RimPulse is retired. |

None goes to the owner.

## Changed outside the skill file

One bullet of `references/traps.md` and one docstring of `src/RimMandrake/Utils/telemetry/cli.py`.

## Could not determine

- The source of "`done_wk` 1.25 on the log scale" and "5..398". The old text is kept. The `v3_vs_v2` program that made them is
  purged (commit 1492763e7a).

## What this run did not test

- No live game was driven. `telemetry health`, `events`, `series` and `query` ran. `tier`, `rebuild`, `label` and `around` did not.
- A bridge hold that a clone other than the bench clone took, then `telemetry tier`, was not tried. The client's refusal names
  `game_lock.py run`.
- The trigger evals were not run, because the description did not change.
