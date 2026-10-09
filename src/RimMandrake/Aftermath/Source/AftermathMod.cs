using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Aftermath
{
    // Harmony bootstrap for the battle recorder's four postfixes. Same
    // recipe as RimMandrake.Ninefold's NinefoldMod / RimMandrake.RaidRedesigner's
    // RaidRedesignerMod.
    [StaticConstructorOnStartup]
    public static class AftermathMod
    {
        public const string HarmonyId = "mandrake.rm.aftermath";

        static AftermathMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            RimMandrake.Shared.PatchApplier.Apply(harmony, Assembly.GetExecutingAssembly(), "RimMandrake.Aftermath");

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[RimMandrake.Aftermath] ready: " + patches + " battle-recorder patches.");
        }
    }
}
