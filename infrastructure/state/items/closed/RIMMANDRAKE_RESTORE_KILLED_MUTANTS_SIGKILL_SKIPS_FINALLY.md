## spec
`mutate_explosivegrowth_fuzz.run_mutations` (the engine 38 `mutate_*_fuzz.py` scripts import) writes each mutant into the
PRODUCTION kernel and restores it in a `finally`. run_selftests' timeout kills with SIGKILL (`os.killpg(..., SIGKILL)`), so the
`finally` never runs and the mutant stays in the working tree. Measured 2026-11-16 in the clone of
RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS: `mutate_graffiti_fuzz.py` timed out and left
`if (makerIdeoDiffersFromViewer) return RM_ReactionSlot.OtherIdeo;` in RM_GraffitiKernel.cs (fuzz `react` went red); a parallel
selftest_graffiti_fuzz.py run in the same batch also read a mutant (`misc`: Stencil in the spree forms). On the base the next run
even re-captures the mutant as its "original" and prints "kernel restored".

Fix: a journal (`~/.cache/rm_mutation_journal/<sha1 of path>.json`: path, pid, original bytes, mutant sha) written before each
mutation and removed after the restore; every run_mutations call first restores any dead run's entry, only when the file still
holds exactly that mutant (an edit made after the kill is never clobbered).

Not fixed here (separate): mutators edit the shared source while other selftests in the same run_selftests batch read it.

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_mutation_journal.py` -> `RESULT: PASS (0 failure(s))`, 4 checks.
Watched it fail on the base engine (checks 2 and 4 FAIL: the killed run's mutant stays, no journal exists).

## criteria
- A mutation run SIGKILLed mid-mutation leaves no mutant behind once any mutation run starts next: restored byte-identical.
- A kernel edited after the kill is never overwritten by the journal.
- A clean run leaves no journal entry.

## refs
file: src/RimMandrake/Utils/mutate_explosivegrowth_fuzz.py
file: src/RimMandrake/Utils/selftest_mutation_journal.py
