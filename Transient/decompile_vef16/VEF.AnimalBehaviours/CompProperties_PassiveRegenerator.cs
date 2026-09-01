using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_PassiveRegenerator : CompProperties
{
	public int radius = 1;

	public int tickInterval = 1000;

	public float healAmount = 0.1f;

	public bool healAll = true;

	public bool showEffect;

	public bool needsToBeTamed;

	public CompProperties_PassiveRegenerator()
	{
		base.compClass = typeof(CompPassiveRegenerator);
	}
}
