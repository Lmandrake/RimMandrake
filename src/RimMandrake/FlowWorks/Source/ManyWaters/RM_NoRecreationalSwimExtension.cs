using Verse;

namespace RimMandrake.FlowWorks.ManyWaters
{
    // ════════════════════════════════════════════════════════════════════
    // DEEP_SAND_WALKABLE_TERRAIN_1 — the marker that keeps "fishable Water-
    // tagged ground" from also reading as "swimmable water" to the ONE vanilla
    // system that does not gate on passability: JoyGiver_GoSwimming.
    //
    // Empty on purpose (a marker, not a data extension) — see
    // RM_Patch_NoRecreationalSandSwim.cs for what reads it and RM_DeepSand.xml's
    // header for the full research trail (why this exists at all).
    // ════════════════════════════════════════════════════════════════════
    public class RM_NoRecreationalSwimExtension : DefModExtension
    {
    }
}
