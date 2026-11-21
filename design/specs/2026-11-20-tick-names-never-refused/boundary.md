# BOUNDARY: every name the tick builds is valid, and no filing is refused for its name, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`fit_name`, `item_id`, `cert_item_id`, `ingame_item_id`,
`blind_item_id`, `free_name`), `src/RimMandrake/rimflow/maturation_autonomy.py` (`item_name`, `name_refusal`,
`_execute_one`), `src/RimMandrake/rimflow/cli.py` (`_mint_or_die`, the `file` A1 gate and `spawn`) and
`src/RimMandrake/rimflow/model.py` (`refusing_name_problems`). Item `RIMMANDRAKE_FIX_TICK_NAMER_RUN_THREE_NAME_TOO_LONG`,
written 2026-11-20. Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_tick_names.py`.

Why: on 2026-11-20 at about 11 PM PST the Dispatch tick named GimmeSomeSlack's third road-back steward run
`RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK_RUN_THREE` (66 characters). `maturation_autonomy.item_name`
cut the base to 56 characters and then added `_RUN_<N>` with no second check. `rimflow spawn` refused the name, the tick
tried the same name three times, and `OPS_MATURATION_SYSTEM_FAULT_LOOP` paused the mod. The owner ruled by card the
same evening (item `RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION`, picked "Keep grammar, never
refuse"): "no filing is ever blocked; a bad name is fixed by the tool or filed with a warning."

## ACCEPTS (the only inputs this is built for)

- **a-name-spec.** A list of words in order. A word that starts with `?` may be dropped. The word that starts with `@`
  is the mod name (CamelCase or with underscores). Every other word is kept as it is.
- **a-known-set.** The item ids already in the ledger, as `helper_checkpoint.known_items` returns them.
- **a-filing.** `rimflow file <ID>` or `rimflow spawn --name <NAME>`, from any seat.

## DOES NOT SURVIVE (not promised)

- **a-run-past-ninety-nine.** `fit_name` tries `_RUN_TWO` to `_RUN_NINETYNINE`. Past that it returns None, and the
  tick reads "no free item name".
- **a-hash-collision.** A mod name that is too long for the room is cut to a prefix plus 4 hex characters of its SHA-1.
  Two mod names with the same prefix and the same 4 hex characters would get the same name. The tick's known-set check
  still gives the second one a `_RUN_<N>`.

## PROMISES (each one is owed a check of the same name)

- **every-tick-name-is-valid.** For every concept folder in `design/concepts/`, a 40-character mod name, every steward
  kind, every stage, visit and cycle numbers 0 to 25 and run numbers 1 to 20, each name that a namer returns passes
  `model.mint_problems` (4 to 9 words, at most 64 characters), starts with `RIMMANDRAKE`, and is not in the known set.
  An in-game visit name also passes `model.RUNNER_INGAME_NAME`.
- **distinct-work-gets-distinct-names.** With an empty known set, two different inputs (namer, mod, kind, stage,
  number) never get the same name, and the visit or cycle number stays in every name that has one.
- **the-run-three-name-fits.** GimmeSomeSlack's road-back steward at visit 1, with the base and `_RUN_TWO` taken, gets
  a valid name that still names GimmeSomeSlack, visit one and run three.
- **a-bad-name-files-with-a-warning.** `rimflow file` and `rimflow spawn` of a name that breaks the grammar (too long,
  too many or too few words) file the item, exit 0, and print a `NAME NOTE:` line that names each problem. The event
  carries the problems in its `name_note` field.
- **only-identity-refuses.** `rimflow file` and `rimflow spawn` still refuse an id that already exists, and an id that
  is not UPPER_SNAKE ASCII. These are not grammar: the ledger cannot hold two items with one id, and other code splits
  ids on `_`.
- **namecheck-stays-advisory.** `rimflow namecheck` of a bad name still prints `REFUSED:` and exits 1.
- **a-name-refusal-is-no-fault.** A launch that never started because rimflow refused the tick's own item name counts
  no system fault, spends no try, and reads `launch_wait`, so the next tick names the item again.

## LIMITS

- `RUN_MAX` = 99 runs per name. Danger: an endless name search if `known` is wrong. Evidence: the old namers stopped at
  19 and GimmeSomeSlack reached run three in one evening; 99 is far past any measured count.

Later lists beside this page: `polish.md`.
