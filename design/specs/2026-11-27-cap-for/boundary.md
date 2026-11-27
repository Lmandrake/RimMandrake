# Boundary: the spend cap of a launch, read from its verb's measured cost (`src/RimMandrake/rimflow/cap_for.py`)

Item RIMMANDRAKE_BUILD_CAP_FOR_VERB_FOURTEEN_CAPS_UNDER_P90, the below-the-line candidate `cap_for <verb>` of
`design/specs/2026-11-26-script-candidates/one_page.md`. Why: of 934 runs with a cost (7.2 days to 2026-11-26), 16
ended at their cap and 14 of those 16 caps sat below that verb's p90 cost; 2 items hit the cap twice (`evidence.md`
G11). A cap is a runaway guard (CLAUDE.md §No limit without the danger it guards), never a stop for an ordinary run.

Code: `src/RimMandrake/rimflow/cap_for.py` (all of it).

## ACCEPTS

- **a-verb.** The item's verb as `measure/rows.py` G11 reads it (`verb_of`): the word after `RIMMANDRAKE_`/`RIMMASTER_`,
  else the first word. Upper-cased.
- **a-model.** `--model M`: only runs whose record's `model` field is `M` as written (an alias such as `opus`).
- **the-run-records.** `--records DIR`, else `detached_helper.runs_dir()`: each `<unit>.json` that names its unit
  (`detached_helper.record_unit`, `is_record`). A run's cost is its `tokens` (weighted_v2: a resumed session's own part,
  `detached_helper.own_part`), else its legacy `cost_usd` through `role_launch.list_usd_to_weighted`; a run with neither
  is not read. `<unit>.out.json` tells a run that ended at its cap (`detached_helper.cap_stopped`).

## DOES NOT SURVIVE

- **a-censored-need.** A run that ended at its cap counts at its cost, a lower bound of its need. The line counts those
  runs; the multiple (3x p90) is the margin over them.
- **records-of-one-machine.** The cap reads the run records of the machine where it runs. On 2026-11-27 SteveDesktop held
  160 records over 2.8 days and Archmagi held 1801. Fewer records give more UNMEASURED verbs, never a wrong figure.
- **a-model-alias.** `--model claude-opus-5-5` does not match records that say `opus`: no alias is resolved.

## PROMISES

- **the-cap-is-not-below-the-verbs-p90.** With at least `FLOOR_RUNS` (9) runs of the verb, `cap_for` returns MEASURED and
  a cap of `P90_MULTIPLE` (3) times the verb's nearest-rank p90 in weighted_v2 tokens, never below that p90, and the
  same figure in list dollars (`role_launch.weighted_to_list_usd`) for `spend_watchdog`.
- **a-verb-with-no-record-reads-unmeasured-and-names-its-fallback.** Fewer than 9 runs: UNMEASURED with the cause, and a
  fallback cap of 3x the larger of every verb's p90 and the verb's own thin p90, with where it comes from. Fewer than
  9 runs of every verb: no number, exit 3, the launch must state its cap. A folder that cannot be listed: COULD NOT LOOK,
  exit 2, no number, the folder never made. Each unreadable record file is counted on the line.
- **the-cap-line-names-danger-and-measured-need.** The one line names the cap (list dollars and weighted_v2), the
  multiple, the verb's p90 and max, the run count, how many ended at their cap, the window the records span, and the
  danger (a runaway run spends an account). `FLOOR_RUNS` and `P90_MULTIPLE` each carry a `# budget: danger=` line.
- **the-cap-never-reaches-the-brief.** `capped_argv` hands the cap to `spend_watchdog.wrap` (`--cap-usd`) only; the
  claude argv is untouched; the brief `detached_helper.brief_message` builds holds no form of the figure; the result
  carries no brief text.

## LIMITS

- `FLOOR_RUNS = 9`. danger: a cap sized from too few runs sits below the verb's real p90 (14 of 16 caps hit in G11).
  measured: the next run outspends all n seen with chance 1/(n+1), which is at or under the 10% that the p90 bar allows
  only from n = 9.
- `P90_MULTIPLE = 3`. danger: a runaway run spends an account. measured (2026-11-27 records): the dearest run of each
  verb with at least 9 runs cost 2.19x (READ, n=41) and 1.76x (OPS, n=11) that verb's p90.

## LIFE CYCLES

- **a launch by hand:** `cap_for.py <verb>` prints the line; the Conductor passes its dollars as `--budget-usd`.
- **a launcher:** `cap_for.capped_argv(verb, argv)` → `spend_watchdog.wrap(argv, cap_usd)`. Not wired into
  `detached_helper.launch` in this run (the parent decides).

Later lists beside this page: `polish.md` (none yet).
