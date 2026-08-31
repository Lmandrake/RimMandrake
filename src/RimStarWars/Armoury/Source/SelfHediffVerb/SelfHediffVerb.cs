using HarmonyLib;
using Verse;

namespace SelfHediffVerb;

[StaticConstructorOnStartup]
public class SelfHediffVerb
{
    static SelfHediffVerb()
    {
        Log.Message("[SelfHediffVerb] Now active");
        // Ported source called PatchAll(Assembly.GetExecutingAssembly()), safe
        // when this mod was its own assembly. Merged into JawaArmoury.dll
        // alongside Spinning_Projectile's own [HarmonyPatch] class, a bare
        // assembly-wide PatchAll() here would double-patch that unrelated
        // class too. Scoped to this mod's own patch class to preserve the
        // original, narrower effect.
        new Harmony("kaitorisenkou.SelfHediffVerb").CreateClassProcessor(typeof(Patch_VerbEquipmentSource)).Patch();
        Log.Message("[SelfHediffVerb] Harmony patch complete!");
    }
}
