using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_PassiveRegenerator : HediffCompProperties
{
	public int radius = 1;

	public int tickInterval = 1000;

	public float healAmount = 0.1f;

	public bool healAll = true;

	public bool showEffect;

	public bool needsToBeTamed;

	public HediffCompProperties_PassiveRegenerator()
	{
		base.compClass = typeof(HediffComp_PassiveRegenerator);
	}
}
