using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Cooking;

internal class HediffCompProperties_WhileHavingThoughts : HediffCompProperties
{
	public List<ThoughtDef> thoughtDefs = new List<ThoughtDef>();

	public List<ThoughtDef> removeThoughtDefs = new List<ThoughtDef>();

	public string hediffReduction = "";

	public float reductionAmount;

	public bool resurrectionEffect;

	public HediffCompProperties_WhileHavingThoughts()
	{
		base.compClass = typeof(HediffComp_WhileHavingThoughts);
	}
}
