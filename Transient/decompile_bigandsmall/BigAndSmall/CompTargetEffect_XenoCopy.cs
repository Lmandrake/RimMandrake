using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompTargetEffect_XenoCopy : CompTargetEffect
{
	public override void DoEffectOn(Pawn user, Thing target)
	{
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val != null)
		{
			Discombobulator.XenoCopy(val);
		}
	}
}
