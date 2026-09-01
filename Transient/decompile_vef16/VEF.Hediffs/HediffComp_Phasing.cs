using Verse;

namespace VEF.Hediffs;

public class HediffComp_Phasing : HediffComp
{
	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		((HediffComp)this).CompPostPostAdd(dinfo);
		PhasingUtils.PhasingPawns.Add(((Hediff)base.parent).pawn);
	}

	public override void CompPostPostRemoved()
	{
		((HediffComp)this).CompPostPostRemoved();
		((Hediff)base.parent).pawn.pather.TryRecoverFromUnwalkablePosition(false);
		PhasingUtils.PhasingPawns.Remove(((Hediff)base.parent).pawn);
	}
}
