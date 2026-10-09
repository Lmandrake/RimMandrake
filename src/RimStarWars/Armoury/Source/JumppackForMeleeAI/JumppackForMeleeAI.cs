using HarmonyLib;
using Verse;

namespace JumppackForMeleeAI;

[StaticConstructorOnStartup]
public class JumppackForMeleeAI
{
    static JumppackForMeleeAI()
    {
        Log.Message("[JumppackForMeleeAI]Now Active");
        // See InstantHealingDrug.cs / SelfHediffVerb.cs for why this is scoped
        // to the one patch class rather than a bare assembly-wide PatchAll().
        RimMandrake.Shared.PatchApplier.Apply(new Harmony("kaitorisenkou.JumppackForMeleeAI"), typeof(JumppackForMeleeAI).Assembly, "JumppackForMeleeAI", "JumppackForMeleeAI");
        Log.Message("[JumppackForMeleeAI]Harmony patch complete!");
    }
}
