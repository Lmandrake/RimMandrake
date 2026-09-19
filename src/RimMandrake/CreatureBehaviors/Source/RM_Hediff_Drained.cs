using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. A silent, self-clearing marker hediff — its
    // only job is to fire once (PostAdd) and hand the drained severity back
    // to whatever bit the victim, via RM_CompFluidSacs.Notify_Fed. Delivered
    // exactly like RM_Grappled: a second <li> in a bite DamageDef's own
    // <additionalHediffs> (RM_Drained_Hediffs.xml's own header has the
    // wiring example), so a race needs no C# of its own to use it — only a
    // bite tool routed through a DamageDef that lists this hediff.
    //
    // HediffCompProperties_Disappears(disappearsAfterTicks: 1) in this
    // hediff's own XML clears it out immediately — same idiom RUT_MatGrip
    // uses for a short-lived effect hediff, just shorter (this one has
    // nothing left to do after PostAdd runs).
    public class RM_Hediff_Drained : HediffWithComps
    {
        public override void PostAdd(DamageInfo? dinfo)
        {
            base.PostAdd(dinfo);

            if (!(dinfo?.Instigator is Pawn attacker))
            {
                return;
            }

            attacker.TryGetComp<RM_CompFluidSacs>()?.Notify_Fed(pawn, Severity);
        }
    }
}
