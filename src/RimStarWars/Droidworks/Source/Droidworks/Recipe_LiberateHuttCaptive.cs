using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROID_HUTT_CAPTIVES_1 (packet C6) — the rescue half. A Hutt captive
    /// arrives already bolted (StockGenerator_DWHuttCaptives seeds
    /// RSW_DW_RestrainingBolt + RSW_DW_BoltResentment before this bill is ever
    /// offered; a future site-cast route is expected to do the same — see this
    /// item's own file for the exact plug-in point), so "rescue" is not a
    /// recruit grind: freeing a prisoner from captivity and freeing it from the
    /// BOLT are two different acts (ruling 2, verbatim: "trapped in the torture
    /// chambers of the Hutts"), and only the second one is
    /// Recipe_RemoveRestrainingBolt — left completely untouched here, so its
    /// rebellion-on-removal check (DROIDWORKS_BOLT_PAYOFF_1) still applies in
    /// full if the player chooses to also cut the bolt.
    ///
    /// Shaped after vanilla Recipe_GhoulInfusion.ApplyOnPawn: a straight
    /// SetFaction(Faction.OfPlayer) is a supported, precedented way for a
    /// surgery-style bill to convert a pawn's allegiance outright, without a
    /// resistance/will grind — the right register for "you found them chained
    /// up," as opposed to "you beat them in a fight and are holding them down."
    /// isViolation false on the RecipeDef: freeing a prisoner is not a
    /// violation the way DROIDWORKS_WIPE_AND_SPIKE_1's memory wipe is.
    ///
    /// Custom worker rather than a data-driven recipe because the gate is
    /// "prisoner AND already bolted" — no single RecipeDef field expresses
    /// that pair, the same reason Recipe_RemoveRestrainingBolt has its own
    /// GetPartsToApplyOn instead of the vanilla removesHediff-only gate.
    /// </summary>
    public class Recipe_LiberateHuttCaptive : Recipe_Surgery
    {
        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            if (pawn.IsPrisoner && pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_RestrainingBolt))
            {
                yield return null;
            }
        }

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                          List<Thing> ingredients, Bill bill)
        {
            if (pawn.Faction != Faction.OfPlayer)
            {
                pawn.SetFaction(Faction.OfPlayer);
            }
            if (billDoer != null)
            {
                TaleRecorder.RecordTale(TaleDefOf.DidSurgery, billDoer, pawn);
            }
        }
    }
}
