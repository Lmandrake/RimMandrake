using BigAndSmall;
using Verse;

public class ZombielandSupport
{
	public static bool? CanBecomeZombie(Pawn pawn)
	{
		if ((pawn.Dead && pawn.RaceProps.Humanlike) || pawn.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && (cache.isUnliving || cache.isBloodFeeder || cache.willBeUndead))
			{
				return false;
			}
		}
		return true;
	}

	public static bool? AttractsZombies(Pawn pawn)
	{
		if (pawn.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && cache.deathlike)
			{
				return false;
			}
		}
		return true;
	}
}
