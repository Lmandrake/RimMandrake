## spec
Child 2 of `CANAL_COVER_DESIGN_WET_FOXHOLE`. The costs of standing in water, all ruled in 2026-10-18
(`design/RimMandrake/canal_cover_design_2026-10-17.md` §5, §10 step 4). Independent of the trench-cover item.
- **Aim (Q4):** a shooter standing in water at chest depth (≥ 1.5 m, relative to its height) has its own hit chance
  × 0.85. Setting `deepWaterAimPenalty` (on).
- **Cold (Q4):** a wet pawn's comfortable minimum temperature rises (vanilla stat offset, proposal +6 °C), so ordinary
  hypothermia arrives sooner. No new hediff, no new kind of cold. Setting `wetFeelsColder` (on).
- **Swimmers cannot fire (Q6):** ranged verbs refused for a swimming pawn (in the existing `CanHitTargetFrom` prefix).
  Setting `swimmersCannotShoot` (on).
- **Downed drowning kept, with a warning (Q8):** a downed pawn in dug water over 0.2 H drowns (V2, built); a clear
  message or alert when it starts (no-vanishing rule). Check what `RM_Swim.DrownMessage` already covers first
  (`Swimming/RM_Swim.cs:562-586`, natural water); extend to dug cells, do not duplicate.
- No weapon fouling (not picked).
Dependencies: swimming `DEEP_WATER_BUILD_SWIM_OR_SINK` (done); V2 drowning in `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE`
(done); depth in metres once P4 lands. Art: none. ESTIMATE 1 to 1.5 agent-days + 0.25 day live.

## verify
- L1: selftests: aim factor 0.85 at chest depth, 1.0 below it; comfortable-min offset applied only while wet.
- L2: the same shooter, target and range, standing dry vs in 1.5 m water: `ShotReport` hit chance ratio ≈ 0.85.
- L2: a soaked pawn's `ComfyTemperatureMin` stat is 6 °C higher than when dry (stat read).
- L2: a swimming pawn with a rifle: `CanHitTargetFrom` false for every target; out of the water: true.
- L2: down a colonist in a 1 m wet canal: a warning message appears before the drowning death (message log read).
