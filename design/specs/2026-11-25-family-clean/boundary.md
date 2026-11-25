# Boundary for the family cleaner

Code: `src/RimMandrake/Utils/family_clean.py`.
Selftest: `python3 src/RimMandrake/Utils/selftest_family_clean.py`.

The cleaner expires the trash families that `scratch_reap.py` does not cover. Each family has one rule: the reader that
would still want a unit, checked unit by unit, and the age line past which a unit with no reader goes. The families and
their lines are in the docstring of the code. Archmagi runs it daily (`rm-family-clean.timer` from
`src/RimMandrake/Utils/systemd/`). SteveDesktop runs it every 6 h on its one family, the test lane's game Screenshots
folders (`infrastructure/stevedesktop/family_clean/`).

## Accepts

- The places of this host, from the defaults or from the `FAMILY_CLEAN_*` variables in the docstring.
- `FAMILY_CLEAN_FAMILIES`: this host's whole run. A host-only family (`screenshots`) runs only where this names it.
- A dry run (the default), one family (`--family`), or `--apply`.

## Does not survive

- A unit that changes between its judgment and its delete in a way that keeps its age and its processes: the judgment
  again before the delete reads only those two.
- A screenshot named only in a file that is neither a result under `FAMILY_CLEAN_RESULTS` nor a tracked file of the
  checkout it runs from (for example a note in a chat, or a file on another machine).
- A citation of a screenshot by a part of its name only: a reader names the whole file name.

## Promises

- **transient_old_unpinned_removed.** A Transient/ file past 14 days that no pin, track or citation holds is REMOVE,
  and `--apply` removes it.
- **transient_pinned_kept.** A pinned file, a `*.decisions.json` and a file that a live item cites are KEEP.
- **transient_young_kept.** A Transient/ file younger than 14 days is YOUNG.
- **saves_canonical_never_listed.** No row names a canonical save or a backup of one.
- **d_uncited_old_removed.** An old D: unit with no reader is REMOVE, and `--apply` removes only the REMOVE rows.
- **d_unlanded_clone_refused.** An old D: unit that holds unlanded git work is REFUSE.
- **d_canonical_only_copy_refused.** An old D: unit that holds the only copy of a canonical save is REFUSE.
- **d_protected_and_young_kept.** `scratch/save_keepers` is KEEP by the family rule; a new D: unit is YOUNG.
- **every_family_has_a_reader.** Each family of a whole run gives rows, and each row names the reader that was checked.
- **check_reads_the_last_apply.** `check` fails with no `--apply` run, holds after one, and fails when it is stale.
- **shots_old_uncited_removed.** A screenshot past 7 days that no result or tracked file names is REMOVE, and
  `--apply` removes it.
- **shots_result_named_kept.** A screenshot that a live result names (as an escaped Windows path in JSON) is KEEP at
  any age.
- **shots_young_kept.** A screenshot younger than the 27 h young line is YOUNG, whatever the budget.
- **shots_budget_newest_kept.** Past the young line, the newest screenshots stay while the folder's bytes (newest
  first) are within the budget; the older ones go.
- **shots_blind_results_unmeasured.** When a results folder cannot be read, each screenshot that would go reads
  UNMEASURED, and nothing is removed.
- **check_reads_host_families.** On a host whose family set is `screenshots`, `check` holds after one `--apply` run,
  and fails after an `--apply` run whose results folder could not be read.
