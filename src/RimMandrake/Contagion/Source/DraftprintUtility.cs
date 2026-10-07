using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GPT_ENRICHMENT_1, part 1: Draftprints. Who can be sampled, and
    // what a sample records. The Unfinished is recognised by carrying
    // CompRandomizeUnfinished (the comp that rolled its limbs), never by
    // defName, and each one yields a single print (CompRandomizeUnfinished.
    // draftprintTaken). Only the living can be sampled: the corpse dissolves
    // to goo the moment it dies (race.deathAction Vanish).
    public static class DraftprintUtility
    {
        public static CompRandomizeUnfinished UnfinishedComp(Pawn p)
        {
            return p?.TryGetComp<CompRandomizeUnfinished>();
        }

        public static bool CanBeSampled(Pawn p)
        {
            CompRandomizeUnfinished comp = UnfinishedComp(p);
            return RM_DraftprintKernel.CanBeSampled(comp != null, comp != null && comp.draftprintTaken, p.Spawned, p.Dead);
        }

        // Fills a fresh print from the living Unfinished and marks the
        // Unfinished as sampled.
        public static void Record(Pawn source, Thing print)
        {
            CompDraftprint dp = print.TryGetComp<CompDraftprint>();
            CompRandomizeUnfinished uc = UnfinishedComp(source);
            if (dp == null || uc == null)
            {
                return;
            }
            CompProperties_RandomizeUnfinished up = (CompProperties_RandomizeUnfinished)uc.props;
            List<Hediff> hediffs = source.health.hediffSet.hediffs;

            dp.limbs = hediffs
                .Where(h => up.limbPool != null && up.limbPool.Contains(h.def))
                .Select(h => h.def)
                .Distinct()
                .ToList();
            dp.monstrous = up.monstrousHediff != null && hediffs.Any(h => h.def == up.monstrousHediff);
            dp.extremeStat = ExtremeStat(source, dp.Props.extremeStats);
            dp.failure = Failure(source, up);
            dp.sourceLabel = source.LabelShort;
            dp.sampledTick = Find.TickManager.TicksGame;
            uc.draftprintTaken = true;
        }

        // The stat furthest from its own kind's base, as a ratio. A stat whose
        // base is zero (armor) is compared by absolute difference instead.
        private static string ExtremeStat(Pawn p, List<StatDef> stats)
        {
            if (stats.NullOrEmpty())
            {
                return "";
            }
            List<float> baseValues = stats.Select(st => p.def.GetStatValueAbstract(st)).ToList();
            List<float> values = stats.Select(st => p.GetStatValue(st)).ToList();
            int pick = RM_DraftprintKernel.ExtremeStat(baseValues, values);
            if (pick < 0)
            {
                return "nothing; it is average for its kind";
            }
            StatDef best = stats[pick];
            float bestValue = values[pick];
            float bestBase = baseValues[pick];
            string s = best.label + " " + best.ValueToString(bestValue);
            if (bestBase > 0.001f)
            {
                s += " (" + (bestValue / bestBase).ToString("0.0#") + "x its kind)";
            }
            return s;
        }

        // What failed: the worst-working rolled limb (an abandoned attempt), or
        // failing that, how far along its unravelling is.
        private static string Failure(Pawn p, CompProperties_RandomizeUnfinished up)
        {
            List<Hediff> all = p.health.hediffSet.hediffs;
            int w = RM_DraftprintKernel.WorstLimb(
                all.Select(h => h is Hediff_AddedPart && up.limbPool != null && up.limbPool.Contains(h.def)).ToList(),
                all.Select(h => h.def.addedPartProps?.partEfficiency ?? 1f).ToList());
            Hediff_AddedPart worst = w >= 0 ? (Hediff_AddedPart)all[w] : null;
            if (worst != null && RM_DraftprintKernel.IsAbandonedAttempt(worst.def.addedPartProps?.partEfficiency ?? 1f))
            {
                return worst.def.label + (worst.Part != null ? " on its " + worst.Part.Label : "");
            }
            Hediff unravel = up.unravelingHediff == null ? null : p.health.hediffSet.GetFirstHediffOfDef(up.unravelingHediff);
            if (unravel != null)
            {
                return "the whole body: " + unravel.LabelBase + " (" + unravel.Severity.ToStringPercent() + ")";
            }
            return "none recorded";
        }

        // "You assume the risks": a conscious Unfinished that is sampled may
        // turn on the sampler. Downed ones cannot.
        public static void MaybeProvoke(Pawn source, Pawn sampler)
        {
            if (!RM_DraftprintKernel.MaybeProvokes(source.Downed, source.InMentalState, RM_ContagionSettings.draftprintProvokeChance, () => Rand.Value))
            {
                return;
            }
            if (source.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "sampled", otherPawn: sampler))
            {
                Messages.Message(
                    source.LabelShort.CapitalizeFirst() + " did not like being sampled.",
                    source, MessageTypeDefOf.ThreatSmall, historical: false);
            }
        }
    }
}
