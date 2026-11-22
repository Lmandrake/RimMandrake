# Equivalence run: old readers against the one home (2026-11-22)

Item `RIMMANDRAKE_MERGE_RUN_SPEND_UNIT_AND_MODEL_ALIAS_THREE_RULES_TWO_TABLES`. Base `7580e09e4f`. The script is
`equivalence.py`, beside this file. Run it with `--recorded` to read this machine's stores. It holds frozen copies of
the old paths, because the old paths are deleted. Each figure below is `[measured]` on Archmagi, 2026-11-22.

## The frozen old paths equal the base code

The base tree was exported with `git archive 7580e09e4f`. Each frozen function was compared with the base module's own
function on the same inputs: 912 detached records, 81 role runs, 250 committed rows and 4 pin aliases. That is 1,247
comparisons, and 0 differed.

## Inputs

- 912 detached run records in `D:\ClaudeWork\rimmandrake\dispatcher\detached`. The folder holds 1,811 `.json` files:
  262 do not parse, and the others are not run records (no `unit` and `item`).
- 81 role runs in the dispatcher state (`state.json`). All 81 carry `token_unit` weighted_v2 and a budget.
- 250 committed spend rows in 24 files (11 `version/run_spend.jsonl`, 13 `version/stage_record.json`).
- Fixture cases: an unstamped Fable record of 1,000 tokens, a model that is not in `MODEL_PRICES`, and 8 model names
  for `tier`.

## The committed rows were stamped first

145 committed rows had no `token_unit`: 131 in `run_spend.jsonl` and 14 in `stage_record.json`. `stamp_rows.py` stamped
each one from its own run record's unit. It used the old time rule only for a row with no run record.

| stamped | from | old time rule | rows |
|---|---|---|---|
| weighted_v1 | its run record | agrees | 124 |
| weighted_v1 | the time rule (no run record: designer seed rows) | agrees | 5 |
| weighted_v2 | its run record | agrees | 16 |

The 16 weighted_v2 rows are the rows where the old time rule and "no stamp means weighted_v1" disagree. Each of the 16
names a run record stamped weighted_v2, so the time rule was right on all 16. The stamp now carries that answer, and the
time rule is deleted. The diff adds only the `token_unit` key.

## Verdicts after the switch

| comparison | same | differ | class of each difference |
|---|---|---|---|
| committed row: unit (old `row_unit` against new) | 250 | 0 | |
| committed row: unit against its run record's unit | 235 | 0 | (15 rows name no run record) |
| detached record: run row unit (old `_spend_row` against new) | 903 | 0 | (9 records not finished) |
| detached record: `tokens_v2` | 912 | 0 | |
| detached record: `tier` | 912 | 0 | |
| detached record: `--model` argument | 912 | 0 | |
| role run: `run_spend` | 81 | 0 | |
| detached record: `run_spend` | 507 | 405 | old was wrong, all 405 |
| pin_id: fable, opus, sonnet, haiku | 4 | 0 | (opus and sonnet: both refuse here, because their variables are unset) |
| fixture: unstamped Fable `run_spend` | 0 | 1 | old was wrong: old 1,000, new 2,000 (the `tokens_v2` figure) |
| fixture: unknown model `run_spend` | 0 | 1 | old was wrong: old took a figure it could not weigh as it stood; new counts the budget |
| fixture: `tier` | 8 | 0 | |

The 405 differences in `run_spend` are unstamped (weighted_v1) detached records that the old `run_spend` took as
weighted_v2. 4 are Fable, which the new code converts. 354 are Opus and 47 are Sonnet. Their alias names no variable on
this machine, so the new code counts them UNMEASURED (their budget). In production, `run_spend` reads only role runs
(`spent_today`), and those are all stamped, so the daily cap does not change. The final line of the run:
`EQUIVALENCE OK: 0 unclassed difference(s)`.

## Planted faults

The selftest (`selftest_run_spend_and_model_alias.py`) went red on each of these 10 planted faults:

1. An unstamped record reads weighted_v2.
2. An unknown model gives the bare figure.
3. `run_spend` skips the conversion.
4. `fable` is dropped from `MODEL_VARS`.
5. Fable falls back to the bare alias.
6. `tier` does not repair a full id.
7. `haiku` is added to `TIERS`.
8. The run view drops its unit.
9. The installer types the id.
10. `pin_id` hard-codes the id.

The acceptance line SPEND went red on fault 3 and MODEL went red on fault 4. Both lines stay green on faults 1 and 5 to
10, because both of their readers now share the one home. The selftest catches those faults.

## What the report proposed and this run did not do

The report said to delete the `run_spend.jsonl` writer and its lander, and to build RUN_SPEND as a view of the run
records. This run kept both. RUN_SPEND is committed and reaches every clone and SteveDesktop. The detached run records
are agent storage on one machine (`D:\ClaudeWork`). A view built from them would lose the other machine's runs and the
history in git `[guess ~80%]`. The fault that the report found was the unit, and the unit now has one reader.
