# RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE: an experiment with drawn crown shadows on one tree type

Owner, by card 2026-10-19 (`TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT`, Q3): *"(2) + an experiment with (3) to see how
painful it is for a single large tree type"*. Option 2, the ground tint under canopy, is built
(`TREE_SHADE_BUILD_CROWNS_ON_STILTS`, `src/RimMandrake/CreatureBehaviors/Source/RM_ShadeOverlay.cs`). Option 3 is a
rendered crown shadow that follows the sun vector (design `design/RimMandrake/tree_shade_model_2026-10-19.md` §4.5 item
4: art and shader work, more risk). **Needs:** a free game; the verdict is his look.

## spec

1. Pick one large day-side tree type (the greatbole or the veluthar: their crown factors are measured, in
   `src/RimMandrake/CreatureBehaviors/Patches/RM_TreeCrowns_Giants.xml`).
2. Draw its crown's shadow on the ground at the disc the shade grid casts (`RM_SunHeatMath.CrownFootprint`), in the
   sun's direction, with no new art if that is possible (the tree's own texture, darkened and flattened, or a soft disc).
3. Report the effort and what broke (draw order, altitude, performance on a full forest), with a save that shows it.

## criteria

- The owner looks at the save and rules keep, change or drop (act 3, his walk).

## verify

Acceptance test: none, a look by the owner.
