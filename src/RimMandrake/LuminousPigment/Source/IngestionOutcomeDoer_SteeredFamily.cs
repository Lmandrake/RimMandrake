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
        // Built live, not cached: steerMinSkill is a Mod Setting the player
        // can change mid-game, and this only runs once per meal eaten.
        private static SimpleCurve SteerChanceCurve(int minSkill)
        {
            return new SimpleCurve
            {
                new CurvePoint(minSkill, 0.5f),
                new CurvePoint(20f, 1.0f),
            };
        }

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

        private string ChooseFamily(CompSkillSteeredOutcome comp)
        {
            string intended = comp?.intendedFamily;
            if (!string.IsNullOrEmpty(intended))
            {
                int idx = DeepfireFamilies.IndexOf(intended);
                if (idx >= 0 && FamilyEnabled(idx))
                {
                    int minSkill = intended == DeepfireFamilies.VermilionKey
                        ? LuminousPigmentSettings.vermilionMinSkill
                        : LuminousPigmentSettings.steerMinSkill;
                    if (comp.cookSkill >= minSkill)
                    {
                        float chance = Mathf.Clamp01(SteerChanceCurve(minSkill).Evaluate(comp.cookSkill));
                        if (Rand.Chance(chance)) return intended;
                    }
                    // Miss: re-roll among every OTHER family, vermilion excluded.
                    return WeightedRandom(excludeKey: intended, excludeVermilion: true);
                }
            }

            // Plain dish, or a steered dish whose target is disabled/unresolvable.
            return WeightedRandom(excludeKey: null, excludeVermilion: true);
        }

        private string WeightedRandom(string excludeKey, bool excludeVermilion)
        {
            List<DeepfireFamily> candidates = new List<DeepfireFamily>();
            for (int i = 0; i < DeepfireFamilies.All.Count; i++)
            {
                DeepfireFamily f = DeepfireFamilies.All[i];
                if (!FamilyEnabled(i)) continue;
                if (f.key == excludeKey) continue;
                if (excludeVermilion && f.key == DeepfireFamilies.VermilionKey) continue;
                if (f.baseWeight <= 0f) continue;
                candidates.Add(f);
            }
            if (candidates.Count == 0) return null;

            float total = candidates.Sum(c => c.baseWeight);
            float roll = Rand.Range(0f, total);
            float cum = 0f;
            foreach (DeepfireFamily f in candidates)
            {
                cum += f.baseWeight;
                if (roll <= cum) return f.key;
            }
            return candidates[candidates.Count - 1].key;
        }

        private static void ApplyFamily(Pawn pawn, string key)
        {
            HediffDef hd = DeepfireFamilies.HediffFor(key);
            if (hd == null) return;

            Hediff existing = pawn.health.hediffSet.hediffs.FirstOrDefault(h => h.def == hd);
            if (existing != null)
            {
                existing.Severity = Mathf.Min(existing.Severity + 1f, hd.maxSeverity);
                return;
            }

            int count = pawn.health.hediffSet.hediffs.Count(h => DeepfireFamilies.IsFamilyHediff(h.def));
            if (count >= LuminousPigmentSettings.maxFamiliesPerPawn) return; // "does nothing but taste" (spec §6.2).

            Hediff made = HediffMaker.MakeHediff(hd, pawn);
            made.Severity = 0.5f;
            pawn.health.AddHediff(made);
        }
    }
}
