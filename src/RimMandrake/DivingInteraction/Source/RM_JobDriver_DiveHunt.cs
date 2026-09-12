using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // Reaches down for whatever the deep holds. Same burn cost as commune
    // (the standing-there toil in the base class); hunting adds only a
    // material outcome roll and a chance the deep resists — resolved with
    // the SAME DamageDef the standing terrain already uses
    // (DamageDefOf.Burn, per HediffGiver_Terrain), never a new damage type.
    public class RM_JobDriver_DiveHunt : RM_JobDriver_DiveBase
    {
        protected override string ReportKey => "diving to hunt the deep";

        protected override void ResolveOutcome()
        {
            IntVec3 cell = TargetLocA;
            Map map = Map;
            if (map == null)
            {
                return;
            }

            if (Rand.Chance(RM_DivingSettings.huntSuccessChance))
            {
                int count = Rand.RangeInclusive(RM_DivingSettings.huntYieldMin, RM_DivingSettings.huntYieldMax);
                Thing chitin = ThingMaker.MakeThing(RM_DivingDefOf.RM_ScaldWalkerChitin);
                chitin.stackCount = count;
                GenPlace.TryPlaceThing(chitin, cell, map, ThingPlaceMode.Near);
                Messages.Message(
                    "RM_DiveHuntSuccess".Translate(pawn.LabelShort, count).Resolve(),
                    new LookTargets(pawn), MessageTypeDefOf.PositiveEvent);
            }
            else
            {
                if (Rand.Chance(RM_DivingSettings.huntLashbackChance))
                {
                    pawn.TakeDamage(new DamageInfo(DamageDefOf.Burn, Rand.Range(2f, 5f)));
                    Messages.Message(
                        "RM_DiveHuntLashback".Translate(pawn.LabelShort).Resolve(),
                        new LookTargets(pawn), MessageTypeDefOf.NegativeEvent);
                }
                else
                {
                    Messages.Message(
                        "RM_DiveHuntNothing".Translate(pawn.LabelShort).Resolve(),
                        new LookTargets(pawn), MessageTypeDefOf.NeutralEvent);
                }
            }
        }
    }
}
