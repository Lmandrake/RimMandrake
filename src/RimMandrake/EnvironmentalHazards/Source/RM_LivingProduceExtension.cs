using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_DECAY_HARVEST_1. A ThingDef carries this to tell
    // RM_MapComponent_LivingProduce it is "living produce" — a stack of it
    // sitting in an enclosed room pushes ambient heat into that room, same
    // biological-warmth read RUT_TheRot's own flavor text gives everything
    // from that biome ("everything is warm from the inside").
    //
    //   <ThingDef>
    //     <defName>RUT_Glimmerslime</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_LivingProduceExtension" />
    //     </modExtensions>
    //   </ThingDef>
    public class RM_LivingProduceExtension : DefModExtension
    {
        // Energy RM_MapComponent_LivingProduce pushes into a thing's room per
        // unit in its stack, once per its TickInterval sweep (2000 ticks).
        // CALIBRATED (ROT_DECAY_HARVEST_1), not guessed: vanilla's Campfire is
        // the anchor. Measured via ilspycmd against the live
        // RimWorldWin64_Data/Managed/Assembly-CSharp.dll, 2026-09-18 —
        // CompHeatPusher.CompTick() calls
        // GenTemperature.PushHeat(pos, map, Props.heatPerSecond) every 60
        // ticks (Verse/CompHeatPusher.cs), and Campfire's own
        // CompProperties_HeatPusher.heatPerSecond is 21
        // (Data/Core/Defs/ThingDefs_Buildings/Buildings_Temperature.xml).
        // Solving so 200 units of a def carrying this extension, sitting in
        // one room, match one campfire's heat output over the same span:
        //   heatPerUnit = campfireHeatPerSecond * TickInterval / (60 * targetUnits)
        //               = 21 * 2000 / (60 * 200) = 3.5
        // A future def with a different intended "richness" can override this
        // per-def; the default is the calibration itself.
        public float heatPerUnit = 3.5f;

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (heatPerUnit < 0f)
            {
                yield return "RM_LivingProduceExtension.heatPerUnit is negative — it would COOL its room instead of warming it.";
            }
        }
    }
}
