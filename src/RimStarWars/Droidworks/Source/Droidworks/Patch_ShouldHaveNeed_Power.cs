using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Written 2026-09-02 (opus code review, re-review pass), fixing a defect
    /// the SAME session's earlier fix introduced: `RSW_DW_Power`'s needClass
    /// was corrected from a broken bare namespace to the real
    /// RimMandrake.StarWars.Droidworks.Need_Power (NeedDefs_Droidworks.xml),
    /// which unmasked that the NeedDef carries NO gating field at all -
    /// no minIntelligence, hediffRequiredAny, colonistsOnly, requiredComps.
    ///
    /// Verified against Pawn_NeedsTracker.ShouldHaveNeed (RimSage): with
    /// every gate left at its default, the method falls through to
    /// `return true;` for every pawn in the game - human, animal,
    /// mechanoid, alike. That means every pawn gets RSW_DW_Power, it
    /// drains to 0 in about 1.5 in-game days (Need_Power's fallback rate
    /// for a pawn with no DroidworksExtension), and RSW_DW_PoweredDown
    /// never decays - the pawn is permanently, irrecoverably downed,
    /// since Recipe_RebootDroid is wired only onto Droidworks race
    /// ThingDefs' own `<recipes>` list. Left unfixed, enabling this mod
    /// ends any game inside two days.
    ///
    /// Rather than retrofit every existing/future Droidworks race def with
    /// a new gating hediff or NeedDef field, this postfixes the one method
    /// that decides need eligibility and narrows RSW_DW_Power specifically
    /// to FleshType == RSW_DW_FleshType_Droid - the same "is this pawn a
    /// droid" signal HediffComp_IonOverloadsDroid already uses.
    ///
    /// Same bootstrap shape as BoltCorePatches.cs (a static Apply(Harmony)
    /// called from a [StaticConstructorOnStartup] wrapper, try/catch'd) -
    /// a separate Harmony instance rather than reusing BoltCore's, since
    /// that lives in a different sub-project (net48, Source/BoltCore/) and
    /// this fix belongs with Need_Power.cs in the main net472 assembly.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DroidworksNeedGateMod
    {
        static DroidworksNeedGateMod()
        {
            try
            {
                Patch_ShouldHaveNeed_Power.Apply(new Harmony("mandrake.rsw.droidworks.needgate"));
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply RSW_DW_Power need gate - "
                    + "EVERY PAWN may get this need with no way to clear it. " + ex);
            }
        }
    }

    public static class Patch_ShouldHaveNeed_Power
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(Pawn_NeedsTracker), "ShouldHaveNeed");
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Pawn_NeedsTracker.ShouldHaveNeed not found "
                    + "by reflection - vanilla API has moved. RSW_DW_Power need gate NOT applied.");
                return;
            }
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(Patch_ShouldHaveNeed_Power), nameof(Postfix)));
        }

        public static void Postfix(NeedDef nd, Pawn ___pawn, ref bool __result)
        {
            if (!__result) return;
            if (nd != DroidworksDefOf.RSW_DW_Power) return;
            if (___pawn?.RaceProps?.FleshType != DroidworksDefOf.RSW_DW_FleshType_Droid)
            {
                __result = false;
            }
        }
    }
}
