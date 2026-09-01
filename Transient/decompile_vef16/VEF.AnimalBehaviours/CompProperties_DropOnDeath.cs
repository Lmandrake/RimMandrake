using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DropOnDeath : CompProperties
{
	public int resourceAmount = 1;

	public string resourceDef;

	public float dropChance = 1f;

	public bool isRandom;

	public List<string> randomItems;

	public CompProperties_DropOnDeath()
	{
		base.compClass = typeof(CompDropOnDeath);
	}
}
