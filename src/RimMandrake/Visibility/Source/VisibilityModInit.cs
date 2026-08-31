using System;
using HarmonyLib;
using Verse;

namespace RimMandrake.Visibility
{
    /// <summary>
    /// Harmony bootstrap, same pattern as
    /// RimMandrake.Utinni.Doctrine.JawaDoctrineCoreMod (which formerly hosted
    /// this mod's patches before it was rehomed to its own dedicated mod).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class VisibilityModInit
    {
        static VisibilityModInit()
        {
            var harmony = new Harmony("mandrake.rm.visibility");
            try
            {
                ColonyVisibilityRaidPatch.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.Visibility] Failed to apply patches: " + ex);
            }
        }
    }
}
