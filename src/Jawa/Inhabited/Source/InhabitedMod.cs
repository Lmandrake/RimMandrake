using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// Harmony bootstrap, and the one line of startup logging this mod emits.
    ///
    /// Harmony itself must come from brrainz.harmony at runtime, never from this
    /// mod's own folder -- CopyLocalLockFileAssemblies is false in the csproj for
    /// exactly that reason, and About.xml declares the dependency and the load
    /// order.
    ///
    /// 🔑 WHY THE LOG LINE EXISTS. Everything this mod does on a successful load
    /// is silent: defs load, patches bind, nothing happens until somebody visits a
    /// place. "No errors in Player.log" would then be indistinguishable from "the
    /// assembly never loaded at all", and a load round is too expensive to spend
    /// on a question the mod could answer about itself. One line, at startup, with
    /// the four counts that say it is genuinely in: patches applied, and the three
    /// def types that must exist for anything else to work.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class InhabitedMod
    {
        public const string HarmonyId = "mandrake.inhabited";

        static InhabitedMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            int patches = harmony.GetPatchedMethods().Count();
            int characters = DefDatabase<CharacterDef>.DefCount;
            int places = DefDatabase<InhabitedPlaceDef>.DefCount;
            int casts = DefDatabase<InhabitedCastDef>.DefCount;

            Log.Message("[Inhabited] ready: " + patches + " patches, "
                        + characters + " characters, "
                        + places + " places, "
                        + casts + " casts.");
        }
    }
}
