# BOUNDARY: what a run spent and in which unit, and which model an alias means, Design Version 0.1.0

Code: one home, `src/RimMandrake/rimflow/role_launch.py`, for two facts.

- **The unit and weight of a stored spend figure:** `stored_unit`, `tokens_v2` and `run_spend`. `MODEL_PRICES` stays
  the one price table.
- **The model an alias or tier means:** `MODEL_VARS`, `resolve_model`, `TIERS`, `tier`, `launch_model` and `model_id`.

Callers that read the home and hold no copy of their own: `maturation.py` (`row_unit`, `_spend_row`),
`Utils/maturation_now.py` (the run view), `detached_helper.py` (the H4 model gate and the claude argv), `mod_model.py`
(`pinnable`, `pin_id`), `run_store.py` (`pilot_tier`, `pilot_model`), `maturation_autonomy.py` (`pilot_run_model`) and
`Utils/install_wt_seat_profiles.py` (the BENCH profile's `--model`).

Item: `RIMMANDRAKE_MERGE_RUN_SPEND_UNIT_AND_MODEL_ALIAS_THREE_RULES_TWO_TABLES`. The report is
`design/specs/2026-11-22-pipeline-single-source-sweep/report.md`, candidates 3 and 4. Written 2026-11-22. Each promise
has a test of the same name in `src/RimMandrake/rimflow/selftest_run_spend_and_model_alias.py`. The test reads
fixtures only, never the machine's environment or `~/.claude/settings.json`. The equivalence run is in
`equivalence.md`, beside this page.

## ACCEPTS (the only inputs the home is built for)

- **a-stored-figure-is-stamped-or-old.** A stored spend figure is one of these: a detached run record, a role run in
  the dispatcher state, a RUN_SPEND line or a stage record's `spend` row. Each one carries `token_unit`, or else it
  was written before the weighted_v2 switch (2026-11-16 23:05 PST), so its figure is weighted_v1. Measured
  2026-11-22: 0 of the 405 unstamped detached records with tokens ended after the switch. Every committed spend row
  carries a stamp, because the 145 unstamped rows were stamped that day from their own run records (`equivalence.md`).
- **an-alias-is-a-ladder-tier.** A model is given as a tier (`fable`, `opus`, `sonnet`), as a full id, a
  provider-prefixed id or a dated id, or in any letter case.
- **the-environment-names-the-ids.** `ANTHROPIC_DEFAULT_<TIER>_MODEL` in the environment, else in
  `~/.claude/settings.json` `env` (GenAiSwitch writes both), names the id that a tier launches as.

## DOES NOT SURVIVE (not promised)

- **a-route-id-for-a-pin.** `pin_id` returns the `MODEL_PRICES` key (`claude-fable-5-2`), not a provider-prefixed
  route id. A pinned Designer launch passes that key to claude.
- **an-unstamped-figure-written-after-the-switch.** No writer makes one (every writer stamps). If a writer did, the
  figure would read as weighted_v1 and be held apart from the stage total. It would never be mixed in.
- **old-dollar-readers.** `detached_helper.result_cost`, `run_void.void_spend` and `spend_watchdog` keep list dollars
  for the tools that need them (`--cap-usd`, a record's `cost_usd`). They measure a run's result. They do not read the
  unit of a stored figure, so they are not rivals of this home.

## PROMISES (each one is owed a test of the same name)

- **one-unit-reader.** `stored_unit(rec)` gives the record's `token_unit` when it is a non-empty string, else
  weighted_v1. `maturation.row_unit` is this function. No reader decides a unit by the time of a record.
- **one-weigher.** `tokens_v2` gives a weighted_v2 figure as it is. It converts a weighted_v1 figure from its per-model
  usage, else to an upper bound by its model's input weight. Any other unit reads `(None, "unit <name>")`.
  `run_spend(r)` is the `tokens_v2` figure of `r`. For an unstamped Fable record of 1,000 tokens, both read 2,000.
- **unmeasured-counts-its-budget-never-zero.** In `run_spend`, a record with no figure, a unit that it cannot convert,
  or a figure whose model `MODEL_PRICES` cannot price counts its budget. `run_spend` reads role runs, and every role
  run carries a budget (81 of 81, measured 2026-11-22). `tokens_v2` raises `UnknownModel` for such a model and names it. It
  never reads 0.
- **a-run-row-takes-its-run-unit.** The maturation_now run view carries its record's `token_unit`. So `_spend_row`
  (the seed and `record_run_spend`) stamps the run's own unit, and stamps weighted_v1 for a run record with none.
- **every-committed-row-is-stamped.** Every row of each committed `version/run_spend.jsonl` and each
  `version/stage_record.json` `spend` list carries a `token_unit`.
- **one-alias-table.** `MODEL_VARS` names the variable of `fable`, `opus`, `sonnet` and `haiku`. `resolve_model('fable')`
  reads `ANTHROPIC_DEFAULT_FABLE_MODEL`, and `mod_model.pin_id('fable')` equals it.
- **an-unset-variable-raises-by-name.** With `ANTHROPIC_DEFAULT_FABLE_MODEL` set in neither the environment nor the
  settings file, `resolve_model('fable')`, `launch_model('fable')` and `pin_id('fable')` each raise `UnknownModel` and
  name that variable.
- **the-cli-resolves-opus-and-sonnet.** `launch_model('opus')` with no variable set gives `opus`, because the CLI
  resolves that alias itself. With the variable set, it gives the variable's id. `launch_model('fable')` never gives
  the bare alias `fable`: the CLI resolved it to claude-fable-5-1 (measured 2026-11-12 and 2026-11-16).
- **a-full-id-is-repaired-to-its-tier.** `tier` maps a full id, a prefixed id or any case to its tier. A name that
  holds no tier, or holds two, comes back as given. So the H4 gate (`model in TIERS`) still refuses `haiku` and a typo.
- **haiku-is-never-a-tier.** `haiku` is not in `TIERS` and cannot pin a mod. `resolve_model` still prices a Haiku id
  for a record, so a spend is never UNMEASURED only because its model is banned.
- **the-pilot-reads-its-tier-once.** `run_store.pilot_tier` reads the agent file's `model:` line.
  `pilot_model` launches that tier through `launch_model`. `maturation_autonomy.pilot_run_model` hands the helper the
  tier itself, which the H4 gate takes.
- **the-profile-installer-reads-the-environment.** The BENCH profile's `--model` is `launch_model('fable')`. It is
  read at install time and is never a typed id.

## LIMITS

None. The home has no cap, timeout or retry.

Later lists beside this page: `polish.md`. There is no `next_version.md`.
