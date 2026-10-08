using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // HAZARD_PROTECTION_STATS_UNSEEN_BY_AI_1. RM_WetBulbProtection (this
    // mod) and RM_SheenProtection (TheRot,
    // MayRequire mandrake.rm.environmentalhazards so it can never be loaded
    // without this mod) are "Apparel"-category StatDefs summed at runtime by
    // HazardTargeting.SumApparelStat/RM_GameCondition_WetBulb's own private
    // copy — that machinery works and is untouched here.
    //
    // The gap is upstream of it: JobGiver_OptimizeApparel.ApparelScoreRaw
    // (the vanilla AI's "how good is this garment" score, confirmed by
    // reading the decompiled 1.6 method via RimSage 2026-09-27) sums
    // ArmorRating_Sharp/Blunt, Insulation_Cold, def.apparel.scoreOffset and
    // GetSpecialApparelScoreOffset() — nothing reads an arbitrary
    // Apparel-category stat, nothing reads these by name, and nothing reads
    // ArmorRating_Heat either. So a
    // pawn never gains score for picking up a boil-suit and never will,
    // no matter which XML list the stat sits in.
    //
    // ⚠️ The spec text that filed this item proposed moving the stats onto
    // <equippedStatOffsets> instead, cribbing vanilla's VacuumResistance.
    // Read against the decompiled engine, that would not have worked:
    // VacuumResistance is a PAWN-category stat auto-aggregated by the
    // generic StatWorker across equippedStatOffsets, and separately
    // JobGiver_OptimizeApparel has ONE hardcoded line
    // (`apparel.def.equippedStatOffsets.GetStatOffsetFromList(StatDefOf.
    // VacuumResistance) > 0f`) that only stops the AI stripping vacuum gear
    // it is already wearing — neither mechanism is generic, and
    // ApparelScoreRaw itself never reads equippedStatOffsets at all. Moving
    // storage there would have both done nothing for AI selection and
    // broken SumApparelStat's `worn[i].GetStatValue(stat)` read (an
    // Apparel-category GetStatValue call does not consult
    // equippedStatOffsets, which only auto-applies to Pawn-category stats).
    // So the stats stay exactly where they are; only the scorer changes.
    //
    // FIX: postfix ApparelScoreRaw and add each hazard-protection stat's
    // value straight onto the score, plus ArmorRating_Heat, which IS the
    // Scald steam clock's protection stat since SCALD_FOLD_INTO_HEAT_1 (one
    // kind of heat, decision taken by question card 2026-10-08), the same
    // weight class as
    // ArmorRating_Sharp/Blunt two lines above it in that method — a boil-suit
    // now reads as better apparel unconditionally, the same way body armor
    // does, rather than only when some detector decides the pawn "needs" it.
    [StaticConstructorOnStartup]
    public static class RM_Patch_HazardApparelScoring
    {
        // Looked up once by name rather than via a [DefOf]-bound field: TheRot
        // may not be installed, and an unresolved DefOf field would throw at
        // startup instead of quietly reading as "not present".
        private static readonly StatDef SheenProtectionStat =
            DefDatabase<StatDef>.GetNamedSilentFail("RM_SheenProtection");

        static RM_Patch_HazardApparelScoring()
        {
            var target = AccessTools.Method(typeof(JobGiver_OptimizeApparel), "ApparelScoreRaw");
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] hazard-apparel-scoring: "
                    + "JobGiver_OptimizeApparel.ApparelScoreRaw not found — hook NOT armed. "
                    + "The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_Patch_HazardApparelScoring), nameof(ApparelScoreRaw_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] hazard-apparel-scoring: patch failed, "
                    + "hook NOT armed. " + e);
            }
        }

        public static void ApparelScoreRaw_Postfix(Pawn pawn, Apparel ap, ref float __result)
        {
            if (!RM_EnvironmentalHazardsSettings.hazardApparelAIAwarenessEnabled)
            {
                return;
            }

            if (ap?.def == null)
            {
                return;
            }

            try
            {
                float bonus = ap.GetStatValue(StatDefOf.ArmorRating_Heat)
                            + ap.GetStatValue(RM_HazardApparelScoringStatDefOf.RM_WetBulbProtection);

                if (SheenProtectionStat != null)
                {
                    bonus += ap.GetStatValue(SheenProtectionStat);
                }

                __result += bonus;
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] hazard-apparel-scoring: " + e.Message, 0x485341);
            }
        }
    }

    [DefOf]
    public static class RM_HazardApparelScoringStatDefOf
    {
        public static StatDef RM_WetBulbProtection;

        static RM_HazardApparelScoringStatDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_HazardApparelScoringStatDefOf));
        }
    }
}
