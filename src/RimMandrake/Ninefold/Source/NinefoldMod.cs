using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Ninefold
{
    // Harmony bootstrap for the five NINEFOLD_ENGINE_M0_1 event hooks
    // (Patch_ResearchCompleted, Patch_MentalBreakStarted, Patch_BirthOutcome,
    // Patch_BuildingDeconstructed, Patch_BuildingRepaired). Same recipe as
    // RimMandrake.Inhabited's InhabitedMod: Harmony comes from
    // brrainz.harmony at runtime, never bundled in this mod's own
    // Assemblies/ folder (see the csproj comment).
    //
    // These five are the "safe core" event-driven deltas per
    // design/Jawa/divine_satiation_engine.md §9 ("the vector, all
    // event-driven deltas... pure read/compute/text. No live mutation") --
    // each hook only ever calls GameComponent_Ninefold.ApplyDelta. No
    // letters, no first-contact chains, no player-facing prose: those remain
    // NOT built (see infrastructure/state/items/NINEFOLD_ENGINE_M0_1.md).
    [StaticConstructorOnStartup]
    public static class NinefoldMod
    {
        public const string HarmonyId = "mandrake.rm.ninefold";

        static NinefoldMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[RimMandrake.Ninefold] ready: " + patches + " event-hook patches.");
        }
    }
}
