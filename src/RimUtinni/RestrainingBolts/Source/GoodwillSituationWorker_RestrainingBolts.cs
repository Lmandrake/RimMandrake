using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RestrainingBolts
{
    /// <summary>
    /// DROID_FDE_GOODWILL_CAP_1 (design/Jawa/worldbuilding/restraining_bolt_technical.md).
    /// Caps the player's goodwill ceiling with the Free Droid Enclaves by how many
    /// currently-owned pawns carry Droid Depot's OuterRim_RestraintBolt hediff RIGHT
    /// NOW. No stored state, no Harmony, no removal hook -- the count is read live
    /// every GoodwillSituationManager recache (~1000 ticks), so freeing a droid lifts
    /// the ceiling on the engine's own schedule.
    ///
    /// maxGoodwill = 100 - 2.5*N, floored at -70 (not -100: Hostile fires at <= -75,
    /// and other negative situations stack via Min, so -70 leaves margin rather than
    /// declaring war outright at 30 bolted droids).
    /// </summary>
    public class GoodwillSituationWorker_RestrainingBolts : GoodwillSituationWorker
    {
        // Resolved lazily, not via [DefOf]: HediffDef lives in Droid Depot
        // (Neronix17.OuterRim.DroidDepot), which may not be active at all.
        // GetNamedSilentFail never throws, so a missing donor degrades to
        // "always null -> always early-out to vanilla 100" rather than a
        // startup error.
        private static HediffDef boltHediffDef;
        private static bool boltHediffResolved;

        private static HediffDef BoltHediff
        {
            get
            {
                if (!boltHediffResolved)
                {
                    boltHediffDef = DefDatabase<HediffDef>.GetNamedSilentFail("OuterRim_RestraintBolt");
                    boltHediffResolved = true;
                }
                return boltHediffDef;
            }
        }

        public override int GetMaxGoodwill(Faction other)
        {
            // Load-bearing, not tidiness: Recalculate runs every situation worker
            // for every goodwill-capable faction on every recache. Returning the
            // vanilla default before touching PawnsFinder means the real walk
            // over every owned pawn happens only for the one faction it can ever
            // matter for.
            if (other?.def != FactionDefOf_RestrainingBolts.RUT_Jawa_FreeDroidEnclaves)
                return 100;

            var hediff = BoltHediff;
            if (hediff == null)
                return 100; // Droid Depot not active -- nothing to count, degrade quietly.

            int boltedCount = PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction
                .Count(p => p.health?.hediffSet?.HasHediff(hediff) ?? false);

            return Mathf.Max(-70, 100 - Mathf.RoundToInt(2.5f * boltedCount));
        }
    }
}
