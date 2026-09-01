using Verse;

namespace VEF.Buildings;

public class CompProperties_RockSpawner : CompProperties
{
	public int spawnCount = 1;

	public IntRange spawnIntervalRange = new IntRange(100, 100);

	public bool spawnForbidden;

	public bool requiresPower;

	public bool requiresFuel;

	public bool writeTimeLeftToSpawn;

	public bool showMessageIfOwned;

	public string saveKeysPrefix;

	public bool inheritFaction;

	public CompProperties_RockSpawner()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompRockSpawner);
	}
}
