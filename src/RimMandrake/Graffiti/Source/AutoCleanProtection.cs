using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 7 / fork F6 (recommendation
    // stands): "Scrub semantics: own-faction and Devotional marks protected
    // from home-area auto-clean, a scrub designator overrides." Same
    // Harmony shape as BreachBiasHook.cs (a postfix there; this is a
    // prefix, since we want to SKIP the vanilla check entirely rather than
    // veto its result).
    //
    // Hook point: RimWorld.WorkGiver_CleanFilth.HasJobOnThing(Pawn pawn,
    // Thing t, bool forced) - the ambient ammbient-cleaning-work scan calls
    // this with forced=false; a player's explicit right-click "Clean now"
    // calls it with forced=true. That existing `forced` flag IS this
    // engine's "scrub designator override" - no new designator needed,
    // vanilla already gives the player an explicit bypass.
    [StaticConstructorOnStartup]
    public static class AutoCleanProtectionMod
    {
        static AutoCleanProtectionMod()
        {
            var harmony = new Harmony("mandrake.rm.graffiti.autocleanprotection");
            harmony.Patch(
                AccessTools.Method(typeof(WorkGiver_CleanFilth), nameof(WorkGiver_CleanFilth.HasJobOnThing)),
                prefix: new HarmonyMethod(typeof(AutoCleanProtectionMod), nameof(Prefix)));
        }

        public static bool Prefix(Pawn pawn, Thing t, bool forced, ref bool __result)
        {
            if (forced || !RM_GraffitiSettings.autoCleanProtectionEnabled)
            {
                return true; // the player's own explicit override - always allowed
            }
            if (!(t is Filth_Mark mark))
            {
                return true;
            }
            ModExtension_Graffiti ext = mark.def.GetModExtension<ModExtension_Graffiti>();
            if (ext == null)
            {
                return true;
            }
            // design §2.3/§4 fork F6, verbatim: "own-faction AND Devotional
            // marks protected" - two independent conditions, either one is
            // enough. Own-faction: this mark's maker was one of ours.
            // Devotional: the mark's own category, regardless of maker
            // (a god's mark deserves the protection even if a visitor
            // placed it via a future RUT placer).
            bool ownFaction = mark.makerFaction != null && mark.makerFaction == Faction.OfPlayer;
            bool devotional = ext.category == GraffitiCategory.Devotional;
            if (ext.protectedFromAutoClean || ownFaction || devotional)
            {
                __result = false;
                return false;
            }
            return true;
        }
    }
}
