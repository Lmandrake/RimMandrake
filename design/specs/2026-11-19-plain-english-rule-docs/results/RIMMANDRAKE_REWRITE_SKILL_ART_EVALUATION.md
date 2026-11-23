# Result: `RIMMANDRAKE_REWRITE_SKILL_ART_EVALUATION`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-art-evaluation/SKILL.md`. Run 2026-11-23.

Base: `e5751732345606d7971b8db6a5a60ac7a54eb1f5`

No evidence left the skill file. So `references/history.md` did not change, and no `Also:` line is needed.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 11,861 | 14,381 |
| words in linted prose | 941 | 1,331 |
| STE violations per 100 words | 3.51 | 1.65 |
| sentences over 20 words | 17 | 4 |
| flagged lines (mechanical) | 0 | 0 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 |

The 4 long sentences that stay: lines 22, 72 and 180 are two short sentences that the lint joined at a bold lead. Line 102
is the spec field list, one code span.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "files it as polish" | what polish is | a fault that does not stop an accept (`severity_policy.md`) |
| `--pilot RM_HulduCatch:C:D` | what the letters are | explained from `cards.pilot_spec` |
| "re-running it skips subjects already decided" | that a `HOLD_ERROR` record also counts as decided | stated, with the trap named |
| "NONE/PLACEHOLDER/DONOR" | the meaning | no art, a stand-in, borrowed art (`fill_queue.py`) |
| the 130-word "Fresh rounds" bullet | the order of the acts | one bullet for each act |
| "used VERBATIM" | which command uses the text | only `fauna_drive.py rows` |
| "FLAGs any row whose judged picture is not on the sheet" | what the sheet shows now | names `--references` also |
| "a wing baked into the plate" | what the plate is | the body layer without the wings (`flyer_cutout.py`) |
| "tuning to one key" | what a key is | the answers of one sitting |
| the subagent rules, one bold sentence of 9 rules | each rule apart | 9 bullets |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without ~25–45 s, ≤12, `regen_rounds.json`, `references/criteria_ledger.md`, 2026-10-24 | 3 lost. Check 1 did not see ≤12, `regen_rounds.json` and the date. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 8 lost, exit 1 |
| check 1, check 2 | the final rewrite | 31 items, 0 lost; 85 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| the 11 selftests in `src/RimMandrake/Utils` and `rimflow` that name the skill or `art_eval`, except the next row, and 6 skill and prose selftests (`validate_skills`, `skills_by_work`, `skills_registered_or_listed`, `guiding_prose`, `game_names_prose`, `retired_era_gone`) | final text | exit 0 |
| `selftest_art_judge_no_keyline.py` | before and after the code correction | 5 FAIL, then PASS |
| `selftest_conductor_authority.py` | final text, then the base text | 6 failures both times. Each one names a file that this run did not touch. |

Names: Opus and GPT appear 9 times in old and new. Neither text names a person. The front matter and every heading are byte
for byte the same. The command fence is the same. One line of the diagram fence changed (below).

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found no lost line and 5 items.

| finding | repair |
|---|---|
| "no judged picture is on the sheet" passes a row with one of two judged records shown | the row fails when one judged record has no picture |
| "the body layer under the wing layers" is false: the plate draws over the wings by default | "the body layer without the wings" |
| the template version is "only" in `prompt_versions`: `summary.md` prints it too | "in `prompt_versions`, not in `versions_key`" |
| the routing table lacks `owner_kept_unmeasured` | a row in `references/pipeline.md` |
| the PASS line of the selftest claims all art-eval prompts | "the two prompts that code composes" |
| fact: the ban check and the facing check run before HOLD_KEPT | a row in `references/pipeline.md` |
| fact: the auto-judge timer files without the owner's prompt | stated in the skill and in `references/traps.md` |

The same reader then read each repair and found no wrong line. It said that the kept-art row was narrower than the code
(the two checks also skip `replaces_kept` when a revert record exists). The writer widened that row of `pipeline.md`.

After the first landing (7cceccf2d2), the prose check of `./publish` named 4 lines. The writer repaired all 4. The same reader
read those repairs and the widened row, and found each one the same or true. `subagent_budget.md` rule 11 does not define
"order"; the gloss (one instruction to compare prompts) is the natural reading of that rule.
The reader then called line 112 overlong. The writer split that line. No reader read that split.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| GOOD needs every checklist item answered ok / an allowed n/a also passes | the second, also in the diagram | 1: `policy.opus_band` |
| art_sheet shows only installed art and renders by name or `--jobs` / judged pictures also go in by `--references` | the second | 1: `shadow.py` `build`, `reference_map` |
| `versions_key` names every prompt version / it names the creature template only | the second | 1: `runner.py` `run`, `prompt_versions` |
| `references/pipeline.md` holds open questions / he answered them | "his answers to the open questions" | 1: that file, §His answers |
| the prompts that code composes ask for a "clean dark outline" / no outlines | no outlines; `round_series.py` and `policy.py` corrected, test first | 2: owner card 2026-10-04, `art_judge_brief.md` B1a |
| `settings.json`: the shadow threshold is provisional / 30 in a row | 30 by owner card | 2: card 2026-10-23 |
| `runner.py` docstring: owner-kept art held / redrawn with a revert record | the second | 1: `policy.after_opus` |
| `traps.md`: never `--file-regens` on fauna candidates (bad job id, raw prompt, no canvas) / all three are corrected | the old reasons deleted; the reason that is true now is stated | 1: `runner.regen_job_id`, `regen_jobs`; the timer passes `--file-regens` |
| `subagent_budget.md`: a budget launcher is owed / its item was dropped 2026-11-18 | the second | 4: `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY` |
| each brief carries `max_turns` and `max_judge_calls` / no agent is told its spend | both: the two numbers count work; a token or spend figure never goes in a brief | 3: root `CLAUDE.md` §No launched agent is told its spend |
| `pipeline.md` routing table lacked six outcomes of the code | six rows added | 1: `runner.evaluate`, `policy.pre_route` |

## Left to another item

`references/prompts/preamble.md` ("a clean dark outline that reads at standard zoom") and
`references/prompts/regen_prompt_edit.md` ("clean dark outline") also disagree with B1a. A change of these files needs
`runner.py regress` first. The item `RIMMANDRAKE_REWRITE_ART_EVAL_PROMPT_FILES_THEN_CALIBRATE` rewrites both files. A note
on that item names the two lines.

## Could not determine

None.

## What this run did not test

- No model judged art with the new text. `runner.py regress` was not run, because no judge prompt changed.
- No image was generated with the two corrected prompts.
- One case exists where the timer filed a round without his prompt: RM_Surrik, judged REGEN in `fauna_auto_20261028_1131`,
  round 3. The text now says what the code does. The code did not change.
- No measurement shows that an agent judges better with the new text. The trigger evals were not run, because the
  description did not change.
