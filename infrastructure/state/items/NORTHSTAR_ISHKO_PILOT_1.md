# NORTHSTAR_ISHKO_PILOT_1 — Northstar pilot on IshkoDarkLandmarks

Owner order (relayed by the BENCH handoff of 2026-10-02 19:35): finish every bedazzle scoring sitting, then
run Northstar on IshkoDarkLandmarks. The sittings closed 2026-10-02 (Miasma last, `4d426ea50`).
Scoping and the measured chain: `design/RimMandrake/northstar_pilot_scoping_2026-10-02.md`.

## spec

Steps, in order (from the scoping doc §3):
1. Add arrows to the walk's must-be-true lines; replace the "not placed" absence bar with a real behaviour
   bar if a world landmark set tool exists, else mark it UNCOVERED with the reason.
2. Add a `modset_builder.py` tier `ishko` = Core + all DLCs + ashkarrlandmarkart + ishkolandmarks; set
   `northstar_plan.py` USE_SUITE=True.
3. `run --mock` clean; `lint_calls` clean.
4. Land `NORTHSTAR_DRIVER_RECORD_STATUS_1` (driver calls `status.record_run`), or use `modcheck run` instead.
5. Optional owner layer: draft one or two north-star lines; the owner validates with `--owner-said`.
6. Bridge take; `live_session.py --mod IshkoDarkLandmarks --tier ishko --plan …` (first live use of
   live_session).
7. Rerun until green per the debug ladder; record the run.
8. Owner review, only if step 5 happened.

## done when

- A recorded GREEN run of IshkoDarkLandmarks exists in modcheck status, produced by live_session.
- What the run taught is written back into the mod's script (`design/RimMandrake/debug_process.md`).
