# AtmosphericBase — Phase 2 notes, 2026-10-11 (FOUNDRY, offline)

Item: `ATMOSPHERIC_BASE_BUILD_PROGRAM_1`. Phase 1 landed at `570079355`.

## Is Phase 2 blocked?

No. The item says Phases 1-2 proceed without `ATMOSPHERIC_BASE_CANVAS_1` and `NINEFOLD_LOUDNESS_FRONT_1`. Phase 2
is ONE mood, so nothing is ranked (rank orders two or more claims; territory is Phase 3). The god signatures are an
owner sitting, so Phase 2 ships only the framework's own schemes: catalog III-2 Lamplight (which the catalog names
as the shipped default) and III-1 Fireflies, as a second pattern kind.

## What was built

- **Schemes as data** (§2.3): `RM_AtmosphericSchemeDef` (palette of ColorInt, pattern kind, mass period, spark
  params, mayGoDark, flasher count and period), validated at load by the pure `RM_SchemeKernel.Errors`: at most 8
  entries (L4), no bright white (L11, every channel >= 200), no full black without mayGoDark and never in a Steady
  scheme (L8), flashers need a period (L7). Shipped in `Defs/RM_AtmosphericSchemes.xml`. Every entry keeps its
  max channel >= 200 so the default never dims work light.
- **Brightness is carried by the palette**, not radius: `GlowGrid.GroundGlowAt` reads the max channel of the
  accumulated glow. No radius write and no LightLedger modifier.
- **The pattern** is a pure function (emitter, group, time) -> palette INDEX: RoomBreath (per-room phase,
  up-and-back), Sparks (independent rise-and-fall), Steady; flashers picked by the framework by stable hash (L7).
- **Groups** (§2.2): registered groups through the API (not saved; the registrant re-registers), plus framework
  defaults ship/rooms/halls/exterior. Vanilla has no hallway role, so a hall is an indoor room with role `Room`/`None`.
- **Compositor** (§2.6 steps 1, 5, 6): one mood per map (a push replaces), saved. With no mood and the default on,
  Lamplight runs on the chosen default group. Each evaluation (every 6 frames, real time, so it runs while paused):
  unlit fixtures skipped (L9), group members get `palette[index]` and everything else its own glow, and only
  changed values are written (`RM_ChangeTracker`). `Drive` refuses any colour not in a loaded palette (L4 at the
  write) and counts violations. Counters (evaluations, writes, skipped) feed the live cost re-measure.
- **Phase-1 gap closed:** `MapComponent.MapRemoved` (RimSage: `Game.DeinitAndRemoveMap`) restores every held
  fixture's override field-only, because a gravship takeoff abandons the map and the fixtures would carry the driven
  colour away. A never-seen fixture is always written once, substrate included, so a reload can't leave one stuck
  on a driven colour.
- **Settings:** `compositor` (animate), `defaultMood`, `defaultMoodGroup` (ship/rooms/halls/outdoors), plus Phase 1's two.
- **API:** PushMood / ReleaseMood / CurrentMood / RegisterGroup / UnregisterGroup / Showing.

## Proof

- `selftest_atmosphericbase_kernel.py` (now through `selftest_winstage`): 59 checks PASS. The Phase 2 checks cover
  every validation law by a planted bad scheme. 60,000 pattern samples are all valid indices. RoomBreath steps one
  level at a time. Changed-only writes exactly the index changes (under 0.5% of 1.2M evaluations). The SHIPPED
  scheme XML validates.
- `selftest_atmosphericbase.py`: 103 checks PASS, including mock `one_mood_proof` with 14 planted breaks and 12 new
  planted source breaks.
- `selftest_lightledger.py` PASS. winbuild clean, no Harmony.
- New live chain `one_mood_proof` (`RM_AtmosphericBaseProof.ProofCompositor`), **never run**.

## Remains

- Live runs of `take_over_proof` and `one_mood_proof`, plus the end-of-Phase-2 cost re-measure on the owner's real
  list (the proof prints sweep counts).
- Unlit-fixture bar is a stub (cutting power on his map leaves a trace). Save/reload and leave-the-map release still
  have no live component.
- A ScenPart for the scenario-decides path is still only the API.
- Phases 3+ blocked on ATMOSPHERIC_BASE_CANVAS_1 and NINEFOLD_LOUDNESS_FRONT_1.
- The player's colour picker can still change a held fixture's colour; the compositor overwrites it on the next
  change, and release restores the pre-hand-over colour. This is unruled.
