## spec

Found by the drain of `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` while trying to run
`CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES`'s proof, and **independently reproduced by the Conductor**
2026-11-17.

`src/RimMandrake/contracts/replay.py:40`:

```python
BASE = "c8d1d12855"   # HEAD before the contracts wiring (2026-10-27)
```

That object does not exist:

```
$ git cat-file -t c8d1d12855
fatal: Not a valid object name c8d1d12855
```

Measured in **both** the drain's scratch clone and the parent repo `/Users/mandrake/dev/RimMandrake`, so it is not
a sparse- or shallow-clone artifact. The sha was presumably rewritten, or recorded from a tree that never landed.

`BASE` is the default of `--base` (line 540), and the file's own docstring (line 19) says the replay compares
recorded calls *"against the git blobs at BASE and the files of the working tree, so 'which code ran' is proven,
not assumed."* With an unresolvable BASE there is no "which code ran" at all — and the drain reports that the
affected families **C2, C4 and C8 have never run**, while the runner still prints `RESULT: GREEN`.

🔴 **That is the defect, and it is the worst shape in the 2026-11-17 checklist.** A GREEN that covers three checks
which could not even start is a failure stored as a pass. The families are not failing and they are not passing:
they are UNMEASURED, and nothing says so. Anyone reading GREEN here has been told the opposite of the truth.

**The fix, in two parts — do not do only the first.**

1. **Make the instrument refuse rather than pass.** An unresolvable `--base` (or a BASE naming no object) must make
   the run exit non-zero with a cause-specific message naming the sha, and any family that could not run must be
   reported UNMEASURED by name — never absent, never folded into GREEN. Keep the four answers apart: a family that
   ran and matched; one that ran and differed; one whose base could not be resolved (UNMEASURED); and a family
   genuinely not selected this run.
2. **Give it a live base.** Decide what BASE should be now — most likely *"HEAD before the contracts wiring"*
   resolved to a sha that is actually an ancestor of `origin/main`, or a tag so it cannot rot again, or computed
   rather than pinned. Say in the commit message how it was chosen and verify `git merge-base --is-ancestor <new>
   origin/main` passes. A pinned literal sha in a file is exactly what rotted here, so prefer something that
   cannot.

🔑 Then re-run C2, C4 and C8 and record what they actually say. They may well pass — but that would be the first
time anyone knows it, and `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES` cannot be closed honestly until they have run.

## refs

file: src/RimMandrake/contracts/replay.py
file: infrastructure/state/items/CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES.md
file: Transient/drain_acceptance.txt

## verify

python3 src/RimMandrake/contracts/replay.py --help

## criteria

- A1: a run whose `--base` names no object in this repo exits NON-ZERO, names the sha, and says what would fix it.
- A2: a family that could not run is reported UNMEASURED by name; the run never prints GREEN while one is unrun.
- A3: `BASE`'s new value resolves and is an ancestor of `origin/main` (proved in the commit message), or is computed
  rather than pinned.
- A4: C2, C4 and C8 have actually run, with their real verdicts recorded on
  `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES`.

## acceptance

Acceptance test: a case that invokes the replay with `--base` set to a deliberately bogus sha and asserts a
non-zero exit whose message names it, plus a case asserting that an UNMEASURED family prevents a GREEN verdict.
Watched FAILING on the base commit, where today's reading is the one in this spec:
`git cat-file -t c8d1d12855` → `fatal: Not a valid object name`, while the runner's verdict line still reads GREEN.
A1 and A2 are provable offline; A4 is the re-run and is recorded with its real output, whatever it says.
