# GSS GPT-consult fixes — BENCH, 2026-10-15

Source: `Transient/release_push_2026-10-15/gpt_GSS/TRIAGE.md`. Scope: fix bugs, add no features.
`GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE`: owner ruled by card mid-session ("Make it a colonist job"); taken after the high items.

| item | findings | status | sha |
|---|---|---|---|
| GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR | C3, C2, C6 | closed | f70ee930b8 |
| GSS_LAMP_STYLE_FIX_OFF_STILL_STYLED | D3 | closed | 4173e9556f |
| GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH | C5, C1, C7, C8 | closed (C5: letter fixed, no new switch) | b6241f9758 |
| GSS_STATICS_FIX_OUTLIVE_THE_SAVE | C14, B16, D11 | closed | e42ac437f0 |
| GSS_LAMP_RUN_FIX_NEIGHBOUR_PAINTS_IT | D2, D9 | closed | e4030582ac |
| GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON | B14, B15, B24, A10, C16 | closed (ripple 0 B/frame, stays ON) | 047fa73b09 |
| GSS_FALLEN_LINE_REDRAW_FLOATS_OVER_PAWNS | C4, C9 | closed | ef8f5e72a5 |
| GSS_AERIAL_HINTS_FIX_SMALL_FIBS | C10, C11, D13 | closed | 946156859f |
| GSS_PROBES_FIX_BLIND_SPOTS | B22, B23, B25, B26, C15, C17, D12, D14 | closed | fb76ad5fc9 |
| GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED | D1, D4, D5, D7, D8 | OPEN: D8 fixed; live rows S12a/b written (needs bridge) | 9b208fdf70 |
| GSS_CORD_LAY_FIX_HEAPS_IN_DOORWAYS | A2-A9 | closed (A2/A3/A7 confirmed offline + fixed, A6 refuted, A8 UNMEASURED row) | 146e2a6be2 |
| GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT | B12, B13 | OPEN: live row B13 written; remedy is cosmetic (owner) | d10301a60f |
| GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE | C12, C13 | closed (colonist job + falloff; by card) | 0b491a254c, 37f46f130e |

## Log
- Offline: new suite `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/GptPreReleaseChecks.cs`; Verse-bound fixes are shape rows
  `GPT_PRERELEASE_FIX_SHAPES` read by `validation.py` O7 (+ C5 letter-vs-def check with a planted probe); live row S11 in
  `validation_style.py` (lamp art with the master off). No live rows were run (no bridge this session).
- C5 choice: the letter was fixed ("Remove the clamp to stop it."), no CompFlickable added. The design never gave the clamp a
  switch; adding one is a new player-facing control (new scope).
- _Shared/SlackGeometry (CordLayer A9, CordPlanner A5) changed: FlowWorks selftests (355 + hose 342) pass on a clean export;
  the FlowWorks DLL at HEAD (8160877246) was rebuilt from source including the change. FlowWorks WIP in the shared tree untouched.
- Offline suite: 682/682 (`selftest_gimmesomeslack.py`); validation.py O7 49 shapes PASS. No live row was run (no bridge).
- Review: 13 changed files CLEAN after full-file review (small/new ones); 18 large changed files still DIRTY (not reviewed in
  full this session): AerialMath, RM_MapComponent_Aerial, RM_MapComponent_CordGraph, CordBuilder, CordGraph, CordAudit,
  CordLayer, GimmeSomeSlackMod, GimmeSomeSlackProbe, AerialProbe, CompAerialAnchor, ConduitStyles, ConduitStylePicker,
  RM_MapComponent_ConduitRuns, ConduitStyleProbe, StyleProbeAerial, SectionLayer_RM_MessyCords, GptPreReleaseChecks.
