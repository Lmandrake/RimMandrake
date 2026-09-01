using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_SwallowWhole : CompProperties
{
	public int stomachCapacity = 5;

	public float maximumBodysize = 30f;

	public int nutritionGained = 5;

	public string soundPlayedWhenEating;

	public bool sendLetterWhenEating;

	public string letterLabel = "";

	public string letterText = "";

	public int digestionPeriod = 240;

	public bool createFilthWhenKilled;

	public ThingDef filthToMake;

	public bool playSoundWhenKilled;

	public string soundToPlay = "Hive_Spawn";

	public CompProperties_SwallowWhole()
	{
		base.compClass = typeof(CompSwallowWhole);
	}
}
