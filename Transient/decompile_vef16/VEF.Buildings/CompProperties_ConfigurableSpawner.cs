using Verse;

namespace VEF.Buildings;

public class CompProperties_ConfigurableSpawner : CompProperties
{
	public int spawnCount = 1;

	public bool spawnForbidden;

	public bool requiresPower;

	public bool requiresFuel;

	public bool writeTimeLeftToSpawn;

	public bool showMessageIfOwned;

	public string saveKeysPrefix;

	public bool inheritFaction;

	public CompProperties_ConfigurableSpawner()
	{
		base.compClass = typeof(CompConfigurableSpawner);
	}
}
