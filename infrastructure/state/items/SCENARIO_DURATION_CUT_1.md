# SCENARIO_DURATION_CUT_1 — cut "ten thousand years" from the opening narration

Owner ruled 2026-09-11 (card sitting): CUT the number. The scenario file's
own header vows no invented duration; the shipped text says "in a language
nobody on this world has heard in ten thousand years"
(`src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml:185`).

## spec
- Reword that one phrase to a non-numeric span in the scenario's register
  (e.g. "in a language nobody on this world has ever heard" / "heard in
  living memory" — the builder's ear picks; no number, no invented era).
- Blast radius: the scenario narration ONLY. Design docs' "ten thousand
  years" prose (depths_concept.md, forsaken_crags.md, the_propane_lakes.md,
  wreck_fields.md) and `RUT_Lightfall.xml`'s landmark text are NOT bound by
  the scenario header's vow and are NOT touched by this ruling.
- Redeploy the UtinniPatches mod after the edit (repo write ≠ deploy).

## verify
Deployed Scenario_Utinni.xml carries no numeric duration; the narration
reads clean in a quicktest new-game screen.

## criteria
The file honors its own header rule.
