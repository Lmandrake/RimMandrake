using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_SummonOnSpawn : CompProperties
{
	public string pawnDef = "Pig";

	public List<int> groupMinMax;

	public bool summonsAreManhunters = true;

	public CompProperties_SummonOnSpawn()
	{
		base.compClass = typeof(CompSummonOnSpawn);
	}
}
