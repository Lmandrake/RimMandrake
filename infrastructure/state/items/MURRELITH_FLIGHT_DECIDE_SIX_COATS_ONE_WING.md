## spec
Split out of `FLYER_TIER_ONE_REBUILD_REDO_ROWS_FIRST`. `RM_Murrelith`
(`src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_FeverWoodBirds.xml`) has no flip-book and 6
`alternateGraphics` (`RM_MurrelithV_C`..`V_H`, chance 0.857). In 1.6 `AlternateGraphic` has no flying
field (decompile `D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse\AlternateGraphic.cs`); the prefix is
per PawnKindDef only. Decide (judge agent, delegation_policy): (a) one shared flip-book cut from the base
static (every coat looks like the base in flight), or (b) a small Harmony swap choosing a per-coat prefix.
Then build it with the cut-out recipe (`design/RimMandrake/flyer_stable_body_study.md` 3.1/3.2).

## criteria
`flyer_gate.py flipbook Murrelith` exits 0 (per coat if (b)); `flyer_gate.py audit --strict` stays 0;
the RM_Murrelith row in `design/RimMandrake/flyer_regen_plan.json` leaves tier 1. Never test flight live.
