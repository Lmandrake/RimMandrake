# RIMMANDRAKE_FIX_FLOWWORKS_FUZZ_FOUR_FLAWS_SINK_STILL_FLOAT

## spec
Codex full-file review of src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs and VV/ShippedMatrixProbe.cs, 2026-11-18, on RIMMANDRAKE_SHARPEN_FLOWWORKS_VOLUME_LAW_ONE_DECILITRE_SLIPS_BY (raw: D:\ClaudeWork\rimmandrake\evidence\vv_laws_first_slice\sharpen_volume_law_one_dl_20261118.txt). Test machinery only; the mod is not touched. Static review, NOT reproduced by the filer. Line numbers are dbf76d554c's.
1. **The per-fluid and sink laws still compare float levels at 1e-3 (ten decilitres)** — FlowKernelFuzz.cs:308, :312. A 1 dL cell turned Water to Tar, or 1 dL removed from a non-sink and reported as sunk, passes. Smallest fix: per-fluid totals, external input and cell-derived sink drainage in integer dL (as the total-volume law now is).
4. **Surface failure counts are a lower bound shown as exact** — ShippedMatrixProbe.cs:205: one scene failing rest and another failing balance report failures = 1. Smallest fix: count the union of failing scenes.
5. **Per-family `planted` includes earlier families and diagnostic reruns** — ShippedMatrixProbe.cs:248 (shrinking at :236 also plants and advances the hook phase). Smallest fix: per-family counter deltas; no planting during shrink, or save and restore the plant state around it.
6. **The probe's JSON writer leaves control characters below U+0020 unescaped** — ShippedMatrixProbe.cs:326 (a --config holding a form feed writes invalid JSON). Smallest fix: escape every char below U+0020.
(Codex findings 2 (the 24-pulse settling window skips the per-pulse checks) and 3 (the shuttle plant cannot reverse its move) went to RIMMANDRAKE_PLANT_FLOWWORKS_SETTLING_LAW_SHUTTLE_TRIPS_OTHERS, whose subject they are.)

## verify
Acceptance test: none written yet; per finding the fixer writes a case red on dbf76d554c and green after (finding 1: a hook plant that moves 1 dL between fluids or into the sink count, run through `vv_laws.py prove FlowWorks --family conservation`; 4-6: probe unit cases), or rules it not-a-bug with the reason. The unplanted kernel_fuzz baseline must stay 0 failures.

## criteria
- Each finding has a case red on base and green after, or a written not-a-bug ruling; `vv_laws.py lint` clean; `selftest_vv_laws.py` green.

## refs
file: src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs
file: src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs
