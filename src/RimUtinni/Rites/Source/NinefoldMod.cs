using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    // Harmony bootstrap for every Ninefold [HarmonyPatch] class in Salvation
    // Rites' assembly (the event hooks, favour tilts and offerings; the first
    // five were NINEFOLD_ENGINE_M0_1's). Same recipe as
    // RimMandrake.Inhabited's InhabitedMod: Harmony comes from
    // brrainz.harmony at runtime, never bundled in this mod's own
    // Assemblies/ folder (see the csproj comment).
    //
    // The event hooks are the "safe core" event-driven deltas per
    // design/Jawa/divine_satiation_engine.md §9 ("the vector, all
    // event-driven deltas... pure read/compute/text. No live mutation") --
    // each one calls GameComponent_Ninefold.ApplyDelta and, for a god's
    // trigger, TryFirstContact (the first-contact letters, FirstContactCorpus.cs).
    [StaticConstructorOnStartup]
    public static class NinefoldMod
    {
        public const string HarmonyId = "mandrake.rut.rites";

        static NinefoldMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            RimMandrake.Shared.PatchApplier.Apply(harmony, Assembly.GetExecutingAssembly(), "Ninefold");

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[Ninefold] ready: " + patches + " event-hook patches.");
        }
    }
}
