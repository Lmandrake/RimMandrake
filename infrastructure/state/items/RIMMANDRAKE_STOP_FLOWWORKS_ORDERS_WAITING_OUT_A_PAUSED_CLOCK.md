## spec
FlowWorks (Design Version 0.1.0). Rank 5 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` section 5; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves.

**Measured (visit 9, bridge log 2026-11-23, calls over 3 s whose 5 s tick windows show 0 ticks):** 40 orders waited on a paused game until their time limit, 757 s together.
| caller | calls | seconds |
|---|---|---|
| `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`, `ordered_job` (default waitTicks 60, game paused) | 30 | 479 |
| `src/RimMandrake/FlowWorks/northstar/extension_proof.py`, `ordered_job` | 2 | 33 |
| `src/RimMandrake/FlowWorks/northstar/live_session.py`, `order_pawn` (waitTicks 1, unpause=False) | 8 | 245 |
Time limits: 15 s `ordered_job`, 30 s `order_pawn`. The tool reports `pausedDuringWait`; no script reads it (JawaBenchJobTools.cs line ~890). Four hand calls showed 0 to 60 ticks in 15 s. Saving the whole 757 s: [guess ~85%].
Fix shape (analysis section 8, "Waits"): order with `waitTicks=0`, then advance fast and end on the state (`s.run(until, limit, speed)` is built; `s.act` for the order itself is NOT_BUILT, so use `s.raw` or the existing driver call until then).
Fixer notes: a grep found no literal order call in `extension_proof.py` (the study's 2 calls go through a helper; the fixer finds it). The 9 call sites in concept_scenes.py/live_session.py that the offline proxy flags are in the acceptance output.

**Recommendation: current Design Version** (harness only; about 12 min per FlowWorks visit). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK.acceptance.sh`
- Part 1, offline PROXY: every order call in the callers passes `waitTicks=0`. WATCHED FAIL today (2026-11-24): `order call sites read 15 in 2 files; sites that can wait on a paused clock 9 (limit 0, our own rule)`, exit 1. `--selftest` prints SELFTEST OK (4 cases: default wait -> red; waitTicks=1 -> red; waitTicks=0 -> green; a file with no order -> could not look). Watched green.
- The proxy is NOT the bar: a call with waitTicks=0 can still sit in a later fixed wait. A passing proxy does not close the item alone.
- Part 2, UNRUN and not built: `clock_still_waits.py --day <visit day> --limit 0`, a reader of the bridge log plus tps windows (the study's method, analysis section 1) that counts order calls over 3 s with 0 ticks in their windows. It must read 40 / 757 s on 2026-11-23 (red) and 0 on the next visit. Input kinds: empty day (could not look), a visit with no order (0), a record that cannot be read (could not look).

## criteria
- The proxy exits 0 AND the clock-still reader reads 0 order calls in the next FlowWorks visit.
