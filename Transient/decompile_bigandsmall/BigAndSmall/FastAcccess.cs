using Verse;

namespace BigAndSmall;

public static class FastAcccess
{
	public static BSCache GetCache(Pawn pawn, bool force = false, int scheduleForce = -1)
	{
		return HumanoidPawnScaler.GetCache(pawn, force);
	}

	public static bool IsUndead(this Pawn pawn)
	{
		BSCache cache = GetCache(pawn);
		if (cache != null && cache.isUnliving)
		{
			return true;
		}
		return false;
	}
}
