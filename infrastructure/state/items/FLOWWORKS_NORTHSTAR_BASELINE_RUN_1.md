# FLOWWORKS_NORTHSTAR_BASELINE_RUN_1

Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §4. Needs: WIRE + SITE_PREP + the shared driver.

The first live execution is a BASELINE, not GREEN: most visual bars are expected NO today (Gravel channel
art, no pit art, no depth draw offset — plan §1). Its value is (a) the first live proof the visual floor
catches a mod whose state passes, and (b) real timings.

## acceptance
- Preflight clean; full run on the `flowworks` tier; every phase's wall-clock recorded in the sheet.
- Sheet produced (`Transient/modcheck/`), every bar with its nominated frame + verdict + state predicates.
- `rimflow verify FLOWWORKS_NORTHSTAR_BASELINE_RUN_1 --result <real> --config flowworks-minimal --evidence <sheet>`.
- Findings filed per failed component; ModsConfig/ModSettings restored and hash-verified; bridge released.
