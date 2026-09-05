using System.Linq;
using System.Reflection;
using HarmonyLib;
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

        static RaidRedesignerMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[RimMandrake.RaidRedesigner] ready: " + patches + " capture-hook patches.");
        }
    }
}
