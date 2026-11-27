# BOUNDARY: the vitals proof's exit and its proof JSON

Code: `src/RimMandrake/bridgetools/prove_vitals_governor.py`, its `rec3`, `blind` and `finish` and each case that calls
them. Item: `RIMMANDRAKE_READ_FIX_D6853E5036_WITH_FRESH_EYES` (the fresh read of the fix at d6853e5036). Written
2026-11-27. This page covers how the proof ends: its exit code and the proof JSON that it writes. It does not cover
what each case stages in the game or what its row decides; those are the live rows of `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO`.
Each promise has a test of its name in `src/RimMandrake/Utils/selftest_vitals_proof_exit_contract.py`, which runs the
proof offline against a fake bridge. The two cannot-look tests were seen red on the parent (exit 1, no JSON). The proof
keeps no state between runs, so the page has no LIFE CYCLES.

## ACCEPTS (the only inputs the proof is built for)

- **a-bridge-session.** A RimBridge endpoint from `rimbridge_client.resolve_endpoint`, with the game at the main menu
  or in a game, on the minimal list plus GimmeSomeSlack.
- **case-names.** Zero or more of `clock`, `modal`, `cluster`, `raid`, `downed`, `death`, `specimen`, `hostile`,
  `colonyloss` as arguments. None means all of them. The cases run in that fixed order.

## DOES NOT SURVIVE (not promised)

- **a-bridge-call-that-raises.** A bridge call that raises (the bridge dies mid-run) ends the run with Python's
  traceback and exit 1, and no proof JSON.
- **an-unwritable-scratch-folder.** When the proof JSON cannot be written, the run ends with the write error.

## PROMISES (each one is owed a test of the same name)

- **every-row-pass-exits-0.** When every row that ran reads PASS, the proof writes them to its proof JSON and exits 0.
- **a-failed-row-exits-1.** When any row reads FAIL, the proof writes the rows to its proof JSON and exits 1.
- **a-case-that-cannot-look-exits-3.** When a case cannot look (the map's threat structures are not cleared, no map
  after start, no far standable cell, no clock read, the vitals events incomplete, or the monitor will not arm), the
  run stops. It records the row `run_stopped_could_not_look` as UNMEASURED with its cause and exits 3, never 1, unless
  a row measured before it reads FAIL.
- **a-case-that-cannot-look-keeps-the-measured-rows.** When a later case cannot look, the rows that earlier cases
  measured are still in the proof JSON.
