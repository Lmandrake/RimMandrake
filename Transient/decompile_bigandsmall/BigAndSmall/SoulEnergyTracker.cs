using Verse;

namespace BigAndSmall;

public class SoulEnergyTracker
{
	private const int cacheTimeout = 1000;

	private int cacheTime;

	protected SoulResourceHediff soulResourceHediff;

	public SoulResourceHediff Resource(Pawn pawn)
	{
		int ticksGame = Find.TickManager.TicksGame;
		if (soulResourceHediff == null || cacheTime + 1000 < ticksGame)
		{
			soulResourceHediff = pawn.health.GetOrAddHediff(BSDefs.BS_SoulPowerHediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null) as SoulResourceHediff;
			cacheTime = ticksGame;
		}
		return soulResourceHediff;
	}
}
