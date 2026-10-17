## spec
Plan P13 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
The vanilla water-body traps of `design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md` §2.3 (read from
`Verse/WaterBody.cs`, `RimWorld/WaterBodyTracker.cs`; not yet seen live). They bite today's design too (trap 2 is a
bug in the ruled pond design), and become core under R10 (one water: dug water is fishable).

1. **Born small, never fished:** fish are rolled once at body creation; a body born at 1 square never rolls. Re-roll
   when a body with no fish crosses 75, 100 or 200 squares with no roll at that size (postfix on the tracker's
   add/flood path).
2. **Drained and refilled, fish lost:** a pond that dries out completely is removed; the refill is a new 1-square body.
   Default (veto-able, engine Q5a): the same fish come back on refill, by footprint; fishing-zone squares removed on
   drying (`WaterBodyTracker.cs:229-234`) are restored on refill.
3. **Never split:** when the P3 solver reports a body split, rebuild the vanilla body membership.
4. **Plant churn (hysteresis):** a square changes band only after its depth stays past the threshold for a while, or
   the chest-deep band keeps the shallow plant tags, so a pump cycle does not kill reeds (default, veto-able, engine Q6a).

Fish in dug water by the game's own size rule (engine Q2a) is a default under R10, veto-able. ESTIMATE 1 to 1.5
agent-days. Needs P14 (base-layer water) to matter for dug water; trap 2 fixes natural ponds whatever P14 does.

## verify
- L1: a body grown square by square from 1 to 120 squares has rolled fish at 75/100 (selftest on the adapter math).
- L1: drain a pond with fish to 0 squares, refill: same fish types, fishing-zone squares restored.
- L1: a split reported by the solver yields two vanilla bodies.
- L2 (live, minimal list): a fishing zone on a 100+ square dug reservoir catches fish; a natural pond drained and
  refilled is fishable again; reeds on a pumped canal survive a pump cycle.
