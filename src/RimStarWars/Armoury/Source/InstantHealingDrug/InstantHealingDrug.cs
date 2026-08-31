using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace InstantHealingDrug;

[StaticConstructorOnStartup]
public class InstantHealingDrug
{
    public static Type VerbSelfHediffType;

    public static Type VerbSHPropType;

    public static FieldInfo VSH_inDangerField;

    static InstantHealingDrug()
    {
        Log.Message("[InstantHealingDrug] Now active");
        // Ported source called PatchAll(Assembly.GetExecutingAssembly()), safe
        // when this mod was its own assembly. Merged into JawaArmoury.dll
        // alongside other ported mods' own [HarmonyPatch] classes, a bare
        // assembly-wide PatchAll() here would double-patch those too. Scoped
        // to this mod's own patch class to preserve the original, narrower
        // effect (see the same fix in SelfHediffVerb.cs / HarmonyPatches.cs).
        new Harmony("kaitorisenkou.InstantHealingDrug").CreateClassProcessor(typeof(TCED_TryGiveJob_Patch)).Patch();
        Log.Message("[InstantHealingDrug] Harmony patch complete!");
        VerbSelfHediffType = AccessTools.TypeByName("SelfHediffVerb.Verb_SelfHediff");
        if (VerbSelfHediffType != null)
        {
            Log.Message("[InstantHealingDrug] SelfHediffVerb found");
            VerbSHPropType = AccessTools.TypeByName("SelfHediffVerb.VerbProperties_SelfHediff");
            VSH_inDangerField = AccessTools.Field(VerbSHPropType, "inDanger");
        }
        else
        {
            Log.Message("[InstantHealingDrug] SelfHediffVerb NOT found");
        }
    }
}
