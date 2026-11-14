# RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE

## spec

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 5, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "What is a soft sand pit? It doesn't identify "soft sand" anywhere when I hover over it. The surrounding terrain type is just soil. We shouldn't be able to dig in sand or loose snow or other very loose types: the walls would just collapse. So I don't think we'd have a soft sand pit anyway. Not sure where this idea came from."

Where "soft sand pit" came from:
- It was the staging helper's own label, not a design.
- `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\tools\stage.py` line 53 painted vanilla `SoftSand` on x150-156 z186-192 with `jawa/set_terrain_batch`. Line 55 then dug exactly that 7x7 through `jawa/flowworks_excavation_drive`.
- That bridge tool does not call `RM_DigSpoil.DigRefusal`, so the player's refusal never ran.
- The pit rect equalled the sand rect, so no sand was left to see. His mouse-over showed the Soil around it (`D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\evidence\terrmap.txt` shows no SoftSand left).
- The pit label does not name the ground it was cut from.
- The look's "requires terrain that supports: Medium" refusal was real. A dry dug floor carries the original ground's affordances, and SoftSand allows only Light. Player digging cannot reach that case while the default setting is on.

The rule already exists for the player:
- Owner 2026-10-25: "you can't dig in sand or mud (just slides back in)".
- Item `PIT_DIG_FIX_SAND_SLIDES_BACK_IN` is done, with a live pass on Designator_DigCanal.
- The setting is `sandMudSlidesBackEnabled`, default on.
- `RM_GroundClassMath.Slumps` covers sand, SoftSand, MarshyTerrain, mud, slime, quicksand and marsh.

What is still owed:
1. **Loose snow.** The def dump has no loose-snow TerrainDef. The snow-named terrains are `RM_PackedSnow` and `VEE_DenseSnow_*`, which dig as Ice. Loose snow is vanilla snow cover (the snow-depth grid), and nothing refuses a dig under it today. Decide what depth of snow cover counts as loose, and refuse it the same way.
2. **Every dig path refuses.** Route the bridge and god excavation (`jawa/flowworks_excavation_drive`, RM_GodLiquid helpers) through `DigRefusal`, or make them name an override. This stops staging from building pits the game forbids.
3. **The pit mouse-over names its original ground** (OriginalTerrainAt), so a reader can tell what a pit was cut from.

Design Version class: PROPOSED Convergent-Problem (current FlowWorks 0.1.0). This is an owner call.

Build effort: small.

Acceptance test (offline, a local model could run it): a FlowWorks selftest asserts:
- `DigRefusal` refuses sand, SoftSand, mud and snow cover above the chosen depth;
- the bridge excavation entry point returns the same refusal unless an explicit override is passed;
- the pit label for a cell cut from Soil contains "Soil".
