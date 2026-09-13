# MODCHECK_RUNNER_SWAP_LIVE_PROOF_1 — first live proof of `cli.py run <mod>`'s fixed subprocess swap path

Surfaced inside `MOD_VALIDATION_RUNNER_1`'s own module docstring
(`src/RimMandrake/Utils/modcheck/runner.py:9-23`), never filed as its own
item. Which NEW mechanism has never been observed running: the WHOLE
`run()` orchestration path — capture ModsConfig, swap to MINIMAL + mods
under test via `swap_to_test_list()`, quicktest-restart, take the bridge,
run each mod's suite via `load_validation()`/`run_suite()`, release, and
`restore_full()` unconditionally from a `finally`. The 2026-09-12 Pits
pilot proved `load_validation()`/`run_suite()` alone, called directly
against an already-live `rimdrive.Session` — it never went through
`run()`'s own swap/restore machinery at all, because that path was found
dead first (subprocess targets launched via `sys.executable` instead of
plain `python3`, which breaks `modlist_swap.py`'s `atomic_copy.py` import
of POSIX-only `fcntl` when driven from `python.exe`). The fix (spawn
`python3`, not `sys.executable`) is already IN the code — just never
exercised live.

## spec

Run `python3 src/RimMandrake/Utils/modcheck/cli.py run <mod>` for a real,
already-known-good mod (Pits is the obvious first target — its own suite
already ran green via the direct route, so a red result here would
isolate the swap/restore path itself, not the suite). Read
`design/RimMandrake/mod_validation_runner_spec.md` §2 for the full
intended shape before touching this.

## verify

```
PROVE   swap_to_test_list() actually swaps ModsConfig.xml to MINIMAL + the
        target mod(s) (diff the live file before/after the swap step,
        not just a return value); the quicktest restart lands; the suite
        runs and reports the SAME result the direct-route Pits pilot got;
        restore_full() puts the owner's FULL list back, verified by a
        second diff, even if forced to fail mid-run (kill the process
        after the swap and confirm the finally still restores on next
        invocation, or reason about the finally's scope directly)
EXPECT  cli.py run pits exits clean, ModsConfig.xml ends identical (md5)
        to what it was before the run
LIES    "restore_full() ran" reported by the tool without a before/after
        md5 or file diff to back it; a swap that silently no-ops because
        modlist_swap.py itself refused (check its own exit code, not just
        that cli.py didn't crash)
```

## not chasing

Retrofitting any mod beyond Pits with a real validation.py — that is
`MOD_VALIDATION_RETROFIT_1`'s job, and it stays blocked on the owner
ratifying the modcheck sheet FORMAT regardless of this item's outcome.
