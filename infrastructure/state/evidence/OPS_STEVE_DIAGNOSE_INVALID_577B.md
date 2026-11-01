# OPS_STEVE_DIAGNOSE_INVALID_577B: the streak of 2026-10-31 07:36Z to 08:19Z

**Verdict: diagnosed and the repeating half is fixed.** One machine-level game death became three INVALID jobs because
the worker handed a game with no map to the next job. The alarm cleared at 09:22Z, after a hand `rw_game.sh down` let c775d5
finish DONE.

| job | finished | outcome | what happened |
|---|---|---|---|
| J20261031T072710Z-1fe7ea | 07:36Z | INVALID/GAME_DIED | game pid 30872 died under the run |
| J20261031T073636Z-00238b | 07:46Z | INVALID/HARNESS | `no_game`: bridge answered, `programState` Entry, no current game |
| J20261031T081027Z-dd60e2 | 08:19Z | INVALID/HARNESS | same game reused, same `no_game` |

The job rows above come from `$TESTQ_QUEUE/done`. The rest comes from notes on other ledger items, not from a log read
for this item:

- **First job:** BENCH attributed it to a machine memory fault, under STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO (open).
  No mod verdict came out of it.
- **Next two:** pid 30296 (started 07:38Z) loaded with `AlienRace.HarmonyPatches` failed (BadImageFormat), `WorldGenStep`
  threw TypeLoadException and the game sat at Entry (note on STEVE_WORKER_UNSTICK_WOUNDED_GAME_KEPT_UP).

## The fix

`infrastructure/stevedesktop/worker.py`: a HARNESS failure whose modcheck output carries `"status": "no_game"` now stops
the game, on the same path a red canary uses (`stop_game_for_next_job`), so the next job cold-starts. Other HARNESS deaths
keep the game: 32 HARNESS results exist and only these two were `no_game`, so a blanket stop would pay cold loads for
faults that have nothing to do with the game.

With this in place the 10-31 streak should have been two jobs, not three, and recovered without a hand. That is inferred
from c775d5, which went DONE on a cold start; it was not replayed.

## Not proven

- The fix has run only against the selftest's mock modcheck, not a real wounded game on Steve. It reaches Steve when the
  runner clone next updates.
- A `no_game` line that falls outside the output tail the worker receives would not trigger the stop. Both real records
  had it inside the 300-character note.
- Why the DLL failed to load was not examined. The Steve job logs for these jobs were not found on a search of its
  ClaudeWork paths (the worker's own TESTQ_HOME was not searched). A corrupt read fits the memory fault and the disk
  bad-block events in `infrastructure/state/lessons/20261101T005033Z-BENCH-steve-nvme-badblock-events.md`, but that link
  is a hypothesis.

## Rerun

    python3 infrastructure/stevedesktop/selftest_steve_worker.py
    python3 src/RimMandrake/Utils/testq/invalid_census.py --since 2026-10-31T07:40Z --until 2026-10-31T08:20Z --require-all no_game --min 2

The second window starts after 1fe7ea on purpose: that job is GAME_DIED and carries no `no_game`.

**The item's locked contract words this check wrongly.** It reads `--since 2026-10-31T07:30Z --until
2026-10-31T08:20Z --require-all no_game...`, which exits 1 as written: the window includes 1fe7ea, and the `...` was
shorthand, not text. The contract cannot be changed from a build attempt, so the command above is a replacement, not the
contract's own. Run without `--require-all`, the contract's window lists all three jobs and exits 0.

Later INVALID jobs on 10-31 had other causes: see `infrastructure/state/evidence/OPS_STEVE_DIAGNOSE_INVALID_CE0E.md`.
