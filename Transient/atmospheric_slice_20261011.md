# AtmosphericBase — slice picked 2026-10-11 (FOUNDRY, offline)

Item: `ATMOSPHERIC_BASE_BUILD_PROGRAM_1`. Phase 0 answered 2026-09-19 (L10 GO), so Phase 1 is the next unbuilt phase.

## The slice: Phase 1 — skeleton and take-over

- Mod scaffold `src/RimMandrake/AtmosphericBase` (`mandrake.rm.atmosphericbase`, `RimMandrake.AtmosphericBase`, `RM_`), loadAfter Ludeon.RimWorld only, **no Harmony**.
- Capability discovery (§2.1): an emitter is a player-owned Building with a CompGlower; never a def whitelist.
- Hard exclusion list: pawns (glowing animals), plants, apparel/equipment, holograms (marker modExtension + name).
- Per-thing opt-in button and a release button; hidden when the scenario decides for that map.
- Release restores the fixture's prior colour exactly (the CompGlower override field, not the effective value). Radius is never written: it belongs to `_Shared/LightLedger` (LIGHT_LEDGER_ONE_1), which `selftest_lightledger.py` enforced against the first draft.
- Mod Settings: light channel on/off, player take-over button on/off.
- Script: validation.py + selftest (offline, --mock) + a C# kernel selftest against the real CompGlower.

## Status — landed 2026-10-11, never run live

- Built, compiles clean via winbuild, no Harmony. Buttons ride `Find.ReverseDesignatorDatabase` (RimSage: `GizmoGridDrawer.DrawGizmoGridFor`).
- `validation.py` chain `take_over_proof`: static gates + 8 proof components through `RM_AtmosphericBaseProof.ProofTakeover`.
- `selftest_atmosphericbase.py` (mock + planted breaks) PASS; `selftest_atmosphericbase_kernel.py` (C# vs real CompGlower) PASS; `selftest_lightledger.py` PASS.
- Walk `## must be true` carries coverage arrows; north star section untouched.

## Remains
- Live run of `take_over_proof` (bridge; never run). Save/reload release and leave-the-map release have no live component yet.
- A ScenPart for the scenario-decides path (only the API `SetScenarioDecides` exists).
- Phases 2-10. Phase 3+ is still blocked on ATMOSPHERIC_BASE_CANVAS_1 and NINEFOLD_LOUDNESS_FRONT_1.
