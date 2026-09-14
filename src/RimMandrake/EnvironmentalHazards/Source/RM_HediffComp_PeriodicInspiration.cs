using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <HediffDef>
    //     <defName>RUT_Miasma_MotherDreamed</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_PeriodicInspiration">
    //         <mtbDaysToDream>20</mtbDaysToDream>
    //         <letterLabelKey>RUT_MotherDreamedLetterLabel</letterLabelKey>
    //         <letterTextKey>RUT_MotherDreamedLetterText</letterTextKey>
    //       </li>
    //     </comps>
    //   </HediffDef>
    //
    // MIASMA_MECHANICS_1 M5 build pass, "Mother-dreamed" (miasma_kit_spec.md
    // Owner cards #1, ruled 2026-09-12: "rarely, a day-long harmless
    // fever-dream ending in a random vanilla Inspiration").
    //
    // Checked before writing any new C#, per this item's own instruction not
    // to guess an API: the real seam already exists and is already used by
    // vanilla content exactly this way —
    // RimWorld/IngestionOutcomeDoer_Psilocap.cs:19 calls
    // `pawn.mindState.inspirationHandler.TryStartInspiration(
    //   InspirationDefOf.Inspired_Creativity, "LetterInspirationBeginPsilocap".Translate())`
    // and RimWorld/CompAbilityEffect_GiveInspiration.cs:12-16 does the same
    // with a RANDOM inspiration via
    // `pawn.mindState.inspirationHandler.GetRandomAvailableInspirationDef()`.
    // `InspirationHandler.TryStartInspiration` (RimWorld/InspirationHandler.cs:68)
    // already guards everything this comp needs: `Inspired` (no
    // double-inspiring), `BlockedByHediff()`, and
    // `def.Worker.InspirationCanOccur(pawn)` — so this comp only has to roll
    // an MTB and call the same two real methods vanilla already calls
    // elsewhere; ban #1 (never a gene, never a directed pick) holds because
    // the inspiration rolled is vanilla's own random pool, not authored here.
    //
    // Generic, not Miasma-specific — any HediffDef can carry this comp to
    // grant a rare, harmless random Inspiration.
    public class CompProperties_PeriodicInspiration : HediffCompProperties
    {
        /// <summary>Mean time between dream-checks, in days. INVENTED: 20 —
        /// "rarely" (spec's own word), roughly once a season for a pawn who
        /// carries the hediff the whole time.</summary>
        public float mtbDaysToDream = 20f;

        /// <summary>Translation key for the letter label; "" falls back to
        /// the raw key rather than erroring (same pattern this mod's M4 pass
        /// already shipped for RM_MiasmaBoonLetterLabel/Text — no
        /// Languages/ entry yet, flagged there and here alike).</summary>
        public string letterLabelKey = "RUT_MotherDreamedLetterLabel";

        public string letterTextKey = "RUT_MotherDreamedLetterText";

        public CompProperties_PeriodicInspiration()
        {
            compClass = typeof(RM_HediffComp_PeriodicInspiration);
        }
    }

    public class RM_HediffComp_PeriodicInspiration : HediffComp
    {
        // 200-tick check interval, the same cadence HediffComp_Immunizable
        // and this mod's own HediffComp_EnvironmentalExposure base class use
        // for anything MTB-rolled — cheap, and (MTBEventOccurs is a
        // memoryless per-tick probability) statistically identical to
        // checking every tick, just far fewer calls. Batched via an explicit
        // countdown rather than a hash-interval check so this behaves
        // correctly under the engine's own tick coalescing for an
        // unloaded/background map, same shape as HediffComp_PeriodicAreaAttack's
        // ticksUntilBurst and this file's sibling comp's ticksUntilCycle.
        private const int CheckIntervalTicks = 200;
        private int ticksUntilCheck;

        public CompProperties_PeriodicInspiration Props => (CompProperties_PeriodicInspiration)props;

        public override void CompPostMake()
        {
            base.CompPostMake();
            ticksUntilCheck = Rand.RangeInclusive(1, CheckIntervalTicks);
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (!RM_EnvironmentalHazardsSettings.periodicInspirationEnabled)
            {
                return; // mod option: periodic inspiration disabled
            }

            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead)
            {
                return;
            }

            if (Props.mtbDaysToDream <= 0f)
            {
                return;
            }

            ticksUntilCheck -= delta;
            if (ticksUntilCheck > 0)
            {
                return;
            }
            ticksUntilCheck = CheckIntervalTicks;

            if (!Rand.MTBEventOccurs(Props.mtbDaysToDream, 60000f, CheckIntervalTicks))
            {
                return;
            }

            TryDream(pawn);
        }

        private void TryDream(Pawn pawn)
        {
            if (pawn.mindState == null || pawn.mindState.inspirationHandler == null)
            {
                return;
            }

            InspirationHandler handler = pawn.mindState.inspirationHandler;
            if (handler.Inspired)
            {
                return; // already inspired by something else — never stack
            }

            InspirationDef def = handler.GetRandomAvailableInspirationDef();
            if (def == null)
            {
                return; // vanilla's own gate found nothing eligible right now
            }

            string reason = Props.letterLabelKey.Translate();
            handler.TryStartInspiration(def, reason);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksUntilCheck, "ticksUntilCheck", 0);
        }
    }
}
