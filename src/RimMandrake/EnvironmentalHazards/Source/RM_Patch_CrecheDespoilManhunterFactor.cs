using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M6 build, §8 "everything living remembers it" —
    // "applies a standing map-wide wild-fauna aggression factor
    // (manhunter-chance x1.5 for 10 days)". Real vanilla seam, not guessed:
    // Verse/RimWorld/IncidentWorker.cs's `virtual float
    // ChanceFactorNow(IIncidentTarget target)` (default 1f) is the exact
    // multiplier the storyteller itself consults when weighing whether to
    // fire an incident — confirmed by grep across the live 1.6/Odyssey
    // decompile: RimWorld/StorytellerComp.cs calls it, and vanilla already
    // overrides it on real IncidentWorkers (e.g.
    // IncidentWorker_FarmAnimalsWanderIn) for the identical "multiply this
    // incident's chance by some map-state-derived factor" purpose this
    // patch needs. A Harmony postfix on the base method, filtered to the
    // two wild-manhunter incidents, is the same "two independent Harmony
    // ids sharing one vanilla seam" pattern this repo already uses
    // (RimMandrake.Aftermath.Patch_MentalBreakNearBattle's own header
    // comment) — never subclasses or repoints either IncidentDef's own
    // workerClass, so nothing here can break another mod's own
    // ManhunterPack/FrenziedAnimals patch.
    //
    // Registered manually (AccessTools.Method + harmony.Patch), matching
    // this assembly's own established pattern
    // (EnvironmentalHazardsMod.BuildCache/Apply in BiomeGlowPatches.cs) —
    // deliberately its own small static bootstrap rather than an edit to
    // that already code-review-clean file, since a second `new
    // Harmony("mandrake.rm.environmentalhazards")` instance patching a
    // third, unrelated method is exactly what Harmony's own multi-patch
    // model expects (same id, independent Patch() calls).
    [StaticConstructorOnStartup]
    public static class RM_CrecheDespoilManhunterFactorPatch
    {
        static RM_CrecheDespoilManhunterFactorPatch()
        {
            MethodBase target = AccessTools.Method(typeof(IncidentWorker), nameof(IncidentWorker.ChanceFactorNow));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] creche-despoil-manhunter-factor: IncidentWorker."
                    + "ChanceFactorNow not found — rule NOT armed. The engine signature this patch was "
                    + "written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_CrecheDespoilManhunterFactorPatch), nameof(ChanceFactorNow_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] creche-despoil-manhunter-factor: patch failed, "
                    + "rule NOT armed. " + e);
            }
        }

        public static void ChanceFactorNow_Postfix(IncidentWorker __instance, IIncidentTarget target, ref float __result)
        {
            if (!RM_EnvironmentalHazardsSettings.crecheDespoilMemoryEnabled)
            {
                return;
            }

            IncidentDef def = __instance?.def;
            if (def == null)
            {
                return;
            }

            // Both are Core (non-DLC-gated) IncidentDefOf fields; only
            // FrenziedAnimals carries [MayRequireAnomaly] on the def
            // itself, so it can be null with Anomaly inactive — guarded,
            // never assumed non-null.
            bool isManhunterIncident = def == IncidentDefOf.ManhunterPack
                || (IncidentDefOf.FrenziedAnimals != null && def == IncidentDefOf.FrenziedAnimals);
            if (!isManhunterIncident)
            {
                return;
            }

            if (!(target is Map map))
            {
                return;
            }

            RM_MapComponent_CrecheMemory memory = map.GetComponent<RM_MapComponent_CrecheMemory>();
            if (memory == null)
            {
                return;
            }

            __result *= memory.ManhunterChanceFactor();
        }
    }
}
