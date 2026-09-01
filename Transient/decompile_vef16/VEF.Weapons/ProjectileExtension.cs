using Verse;

namespace VEF.Weapons;

public class ProjectileExtension : DefModExtension
{
	public int beamLifetimeTicks = 30;

	public int beamSkyFadeInTicks;

	public int beakSkyHoldTikcs = 25;

	public int beakSkyFadeOutTicks = 5;

	public float flashIntensity = -1f;

	public FleckDef hitFleck;

	public bool excludeFromStaticCollection;

	public EffecterDef attachedEffecter;

	public FleckDef attachedFleck;

	public float fleckScale = 1f;

	public int fleckRefreshInterval = 10;

	public ThingDef filthOnMiss;

	public float filthOnMissChance;

	public IntRange filthOnMissCount;
}
