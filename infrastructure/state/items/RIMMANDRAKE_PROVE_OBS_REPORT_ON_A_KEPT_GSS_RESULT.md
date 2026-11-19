# RIMMANDRAKE_PROVE_OBS_REPORT_ON_A_KEPT_GSS_RESULT

## spec
Child of `RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST` (first slice: `src/RimMandrake/Utils/modcheck/obs_report.py`).
The slice's "done when" asks a real proof run whose report's first line is required checks proven. The tool reads the
real call log (run `4d0e9a2ae543`: wall 394 s, in-call 240.8 s against an independent tally of 240.7 s, ticks 46.0 s
against 44.6 s of `safe_advance` plus the step calls: within 3%), but no live GSS result of any logged run (2026-11-12..17)
survives: each was written beside `proof_all.py` in a clone since reaped, so line 1 reads UNMEASURED for this run.
1. DONE in the parent's landing: `proof_all.py` writes its bridge client's run id (`rimbridge_client._RUN_ID`) into its
   result as `bridge_run`, and `obs_report.py` counts a result as a run's only through it (a time-window start is
   context, never proof: Codex repair check 2026-11-18). Offline cases R3 and R9 of `selftest_obs_report.py` cover it.
2. What is left: the next live `proof_all.py` run keeps its result (commit or pin it), and `obs_report.py <run>` on it leads with
   `required checks proven: N of M`.

## criteria
- Offline part: done (R3, R9 of `selftest_obs_report.py`, green).
- Live (part 2, UNRUN): `python.exe src\RimMandrake\GimmeSomeSlack\northstar\proof_all.py`, then
  `python3 src/RimMandrake/Utils/modcheck/obs_report.py <its run id> --out <evidence>`; its first line is `required checks proven: N of M`.

## verify
- The report file of that run, cited on the close.

## refs
file: src/RimMandrake/Utils/modcheck/obs_report.py
file: src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py
