using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ExplodeOnDowned : HediffComp
{
	public int checkEveryTicks = 60;

	public HediffCompProperties_ExplodeOnDowned Props => (HediffCompProperties_ExplodeOnDowned)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, checkEveryTicks, delta) && ((Hediff)base.parent).pawn.Downed && !((Hediff)base.parent).pawn.health.hediffSet.HasHediff(HediffDefOf.Anesthetic, false))
		{
			((Thing)((Hediff)base.parent).pawn).Kill((DamageInfo?)null, (Hediff)null);
		}
	}
}
