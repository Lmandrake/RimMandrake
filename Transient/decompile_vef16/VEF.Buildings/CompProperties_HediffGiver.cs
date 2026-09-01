using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompProperties_HediffGiver : CompProperties
{
	public HediffDef hediffDef;

	public float severityIncrease;

	public float radius;

	public List<StatDef> stats;

	public int tickRate = 500;

	public CompProperties_HediffGiver()
	{
		base.compClass = typeof(CompHediffGiver);
	}
}
