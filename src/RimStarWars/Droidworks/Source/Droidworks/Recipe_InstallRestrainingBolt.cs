using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// The formal, consented/violating surgery route for fitting a
    /// restraining bolt. Vanilla Recipe_InstallImplant already handles
    /// targetsBodyPart=false + addsHediff on its own - droid_ruling.md
    /// section 3's own OuterRim_AttachRestraintBolt needs zero C# for exactly
    /// this reason, and RSW_DW_InstallRestrainingBolt's XML copies that shape
    /// (surgerySuccessChanceFactor 99999, isViolation true, anesthetize
    /// false). The ONLY thing this subclass adds is seeding
    /// RSW_DW_BoltResentment the moment the bolt goes on, for a sapient pawn -
    /// the resentment accumulator otherwise has nothing to tick
    /// (HediffComp_DWBoltResentment.CompPostTick only runs once the hediff
    /// exists on the pawn). The field-clamp route (JobDriver_DWClampBolt)
    /// seeds it the same way, through the same shared helper.
    /// </summary>
    public class Recipe_InstallRestrainingBolt : Recipe_InstallImplant
    {
        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            base.ApplyOnPawn(pawn, part, billDoer, ingredients, bill);
            DroidworksBoltUtility.EnsureBoltResentment(pawn);
        }
    }
}
