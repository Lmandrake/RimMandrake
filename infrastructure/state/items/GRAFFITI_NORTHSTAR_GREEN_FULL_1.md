# GRAFFITI_NORTHSTAR_GREEN_FULL_1

Parent: `GRAFFITI_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`, §3.1 (full rung), §3.14 and §6.8.

## spec
Run the same suite on the owner's FULL list:
1. a **fresh launch** on that list;
2. verify `RunningModsListForReading` against FULL.LATEST;
3. a fresh quicktest map and site.

Foreign mark defs from SacredGraffiti and GraffitiImperial go into separately reported compatibility
components, never into Graffiti's bars. This needs the driver's full-list mode, which `modcheck run`
cannot do: it records only `min+<mod>`.

## acceptance
- Every Graffiti bar passes on the full list, and the state predicates pass.
- Recorded with config `full`.
- Every full-list-only difference is listed in the sheet: pool members, cleaning mods, camera mods.
