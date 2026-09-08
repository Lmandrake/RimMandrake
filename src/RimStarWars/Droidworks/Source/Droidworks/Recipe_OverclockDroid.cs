using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_SHOP_BENCHES_1 (packet B4b): "overclock as a bench job".
    /// Whole-pawn Recipe_Surgery, same "near a RSW_DW_RepairBench" gate as
    /// Recipe_InstallDroidPartAtBench (shares its static check rather than
    /// re-deriving it). Grants RSW_DW_Overclocked at severity 1 - a
    /// temporary stat boost that decays on its own
    /// (HediffCompProperties_SeverityPerDay, XML-only, no custom decay code
    /// needed) - nothing in the design doc specifies overclock's mechanical
    /// shape beyond naming it, so this is FOUNDRY's own scope call.
    /// </summary>
    public class Recipe_OverclockDroid : Recipe_Surgery
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null) =>
            base.AvailableOnNow(thing, part) && thing is Pawn p
            && Recipe_InstallDroidPartAtBench.NearRepairBench(p);

        public override bool CompletableEver(Pawn surgeryTarget) =>
            Recipe_InstallDroidPartAtBench.NearRepairBench(surgeryTarget);

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_Overclocked);
            if (existing != null)
                existing.Severity = 1f;
            else
                pawn.health.AddHediff(DroidworksDefOf.RSW_DW_Overclocked);
        }
    }
}
