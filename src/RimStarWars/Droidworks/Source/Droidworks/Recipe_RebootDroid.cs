using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// The outside-help reboot (doctor at bedside or crafter at bench):
    /// removes RSW_DW_PoweredDown and restores a sliver of power so the droid can
    /// walk to a charger. Surgery on a thing that is legally an object is the
    /// classic edge case - this stays a normal Recipe on a downed pawn, which
    /// vanilla supports.
    /// </summary>
    public class Recipe_RebootDroid : Recipe_Surgery
    {
        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            if (pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_PoweredDown))
                yield return null;
        }

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_PoweredDown);
            if (h != null) pawn.health.RemoveHediff(h);
            Need_Power need = pawn.needs?.TryGetNeed<Need_Power>();
            if (need != null && need.CurLevel < 0.15f) need.CurLevel = 0.15f;
        }
    }
}
