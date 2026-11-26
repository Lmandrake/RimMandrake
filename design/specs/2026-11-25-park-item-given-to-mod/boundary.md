# BOUNDARY: a run that gives its item to a mod leaves it parked on that mod, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/mod_park.py` (`plan`, `park`, `sweep`) and `park_to_mod` in
`src/RimMandrake/rimflow/detached_helper.py` (called by `finish`). Item
`RIMMANDRAKE_PARK_ITEM_GIVEN_TO_MOD_TWO_WAKES_OWED_A_HAND`, written 2026-11-25. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: on 2026-11-25 (8:26 PM and 8:28 PM PST) two Shape runs gave a stale-blocked item to its mod (`rimflow home --home
mod:<Mod>`) and stopped. Each left the item in state `doing`, so the run-end wake printed `OWED:` and the Conductor window
wrote the `LEFT OPEN:` note and the wait by hand. The route is any run that writes a mod home and ends with the item open,
so the program acts at the run's end, not in one brief.

## ACCEPTS (the only inputs this is built for)

- **a-run-that-ended-success.** A detached run whose item is `ready` or `doing`, with a `home mod:<Mod>` event written
  at or after the run began.

## DOES NOT SURVIVE (not promised)

- **a-ledger-that-cannot-be-read-after-the-steps.** The steps are said in the record (`parked item UNMEASURED`) and the
  `OWED:` line then stands.
- **a-mod-with-no-version-folder.** The wait names `Design Version UNMEASURED (<cause>)`; the park still happens.

## PROMISES (each one is owed a test of the same name)

- **a-run-that-gives-its-item-to-a-mod-leaves-it-parked-on-the-mod.** After such a run the item is `ready`, not `doing`;
  it waits (a dated wait ahead of now whose reason names the mod and its Design Version, and not the Conductor); its notes
  carry one note that starts `LEFT OPEN:`; the run-end wake carries no `OWED:` line. A step that is already so (a hand
  parked item) is not written again. A home older than the run, a home of another kind, no home, a closed item and a failed
  run park nothing. A failed step is named in the record and the later steps still run. Red on the base: the item stays
  `doing`, no wait, the wake prints `OWED:`.
