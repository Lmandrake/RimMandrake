using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §6.2/§6.4/§6.5. Family-agnostic outcome doer: reads the eaten
    // meal's CompSkillSteeredOutcome (written at cook time by
    // Patch_GenRecipe_WriteCookSkill); a steered dish rolls against
    // LuminousPigmentSettings.steerCurve (linear steerMinSkill->50% .. 20->
    // 100%) for its intended family and otherwise re-rolls among the
    // others (never the vermilion); a plain dish always rolls the plain
    // weighted table (never the vermilion). Eating the same family again
    // bumps its hediff's severity by one whole tier instead of stacking a
    // second hediff; a different family is a second hediff, capped at
    // maxFamiliesPerPawn (spec: "the body has no more to give" past that --
    // the dish still gives the taste thought, nothing else).
    public class IngestionOutcomeDoer_SteeredFamily : IngestionOutcomeDoer
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (!LuminousPigmentSettings.cuisineEnabled) return;
            if (pawn?.RaceProps?.Humanlike != true) return; // animals: no effect (spec §6.2).

            CompSkillSteeredOutcome comp = (ingested as ThingWithComps)?.TryGetComp<CompSkillSteeredOutcome>();
            string family = ChooseFamily(comp);
            if (family != null)
            {
                ApplyFamily(pawn, family);
            }

            ThoughtDef ate = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_AteDeepfire");
            if (ate != null) pawn.needs?.mood?.thoughts?.memories?.TryGainMemory(ate);

            // spec §5.2: "a Deepfire dish eaten" -- Zizzik +Small (the
            // spark), Ozzik +Small (pride). The only §5.2 row wireable
            // without CompDeepfire (piece 1, deferred).
            NinefoldDeltaBridge.ApplyDelta("Zizzik", LuminousPigmentSettings.godDeltaLike, "deepfire.eaten");
            NinefoldDeltaBridge.ApplyDelta("Ozzik", LuminousPigmentSettings.godDeltaLike, "deepfire.eaten");
        }

        private static bool FamilyEnabled(int index)
        {
            bool[] en = LuminousPigmentSettings.familyEnabled;
            return en == null || index < 0 || index >= en.Length || en[index];
        }

        private static float[] weightsCache;

        private static float[] FamilyWeights()
        {
            if (weightsCache == null)
            {
                weightsCache = new float[DeepfireFamilies.All.Count];
                for (int i = 0; i < weightsCache.Length; i++) weightsCache[i] = DeepfireFamilies.All[i].baseWeight;
            }
            return weightsCache;
        }

        private string ChooseFamily(CompSkillSteeredOutcome comp)
        {
            string intended = comp?.intendedFamily;
            int idx = string.IsNullOrEmpty(intended) ? -1 : DeepfireFamilies.IndexOf(intended);
            int picked = RM_DeepfireCuisine.Choose(idx, comp?.cookSkill ?? 0, LuminousPigmentSettings.steerMinSkill,
                LuminousPigmentSettings.vermilionMinSkill, DeepfireFamilies.IndexOf(DeepfireFamilies.VermilionKey), FamilyWeights(),
                LuminousPigmentSettings.familyEnabled, chance => Rand.Chance(chance), total => Rand.Range(0f, total));
            return picked < 0 ? null : DeepfireFamilies.All[picked].key;
        }

        private static void ApplyFamily(Pawn pawn, string key)
        {
            HediffDef hd = DeepfireFamilies.HediffFor(key);
            if (hd == null) return;

            Hediff existing = pawn.health.hediffSet.hediffs.FirstOrDefault(h => h.def == hd);
            int count = pawn.health.hediffSet.hediffs.Count(h => DeepfireFamilies.IsFamilyHediff(h.def));
            FamilyOutcome outcome = RM_DeepfireCuisine.Apply(existing != null, count, LuminousPigmentSettings.maxFamiliesPerPawn);
            if (outcome == FamilyOutcome.Bumped)
            {
                existing.Severity = RM_DeepfireCuisine.Bump(existing.Severity, hd.maxSeverity);
                return;
            }
            if (outcome == FamilyOutcome.CapBlocked) return; // "does nothing but taste" (spec §6.2).

            Hediff made = HediffMaker.MakeHediff(hd, pawn);
            made.Severity = 0.5f;
            pawn.health.AddHediff(made);
        }
    }
}
