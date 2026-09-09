using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // Harmony bootstrap for the eight PLOT_MECHANISM_MODS_WAVE_1 capture-hook
    // postfixes (design/Jawa/proposals/plot_mechanisms_wave.md §1.4). Same
    // recipe as RimMandrake.Ninefold's NinefoldMod: Harmony comes from
    // brrainz.harmony at runtime, never bundled in this mod's own
    // Assemblies/ folder (see the csproj comment).
    [StaticConstructorOnStartup]
    public static class RaidRedesignerMod
    {
        public const string HarmonyId = "mandrake.rm.raidredesigner";

        // RAIDREDESIGNER_HARD_PROPERTY_REF_1: kept out of the About.xml's
        // <modDependencies> deliberately -- see Patch_CaravanRobbed's header.
        private const string PropertyPackageId = "mandrake.rm.property";

        static RaidRedesignerMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            // PatchAll only ever sees the seven Property-independent capture
            // hooks: Patch_CaravanRobbed carries no [HarmonyPatch] attribute,
            // so PatchAll's attribute scan never touches PropertyEngine.
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            if (ModsConfig.IsActive(PropertyPackageId))
            {
                Patch_CaravanRobbed.TryPatch(harmony);
            }
            else
            {
                Log.Message("[RimMandrake.RaidRedesigner] " + PropertyPackageId
                    + " not active - BetrayedTrader capture hook skipped.");
            }

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[RimMandrake.RaidRedesigner] ready: " + patches + " capture-hook patches.");
        }
    }
}
