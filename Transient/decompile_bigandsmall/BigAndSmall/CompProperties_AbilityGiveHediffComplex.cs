using System;
using System.Collections.Generic;
using RimWorld;

namespace BigAndSmall;

public class CompProperties_AbilityGiveHediffComplex : CompProperties_AbilityGiveHediff
{
	public class OffsetSeverityByStats
	{
		public StatDef stat;

		public float multiplier;
	}

	public class OffsetSeverityByBodySize
	{
		public float multiplier;
	}

	public List<OffsetSeverityByStats> offsetSeverityByStats = new List<OffsetSeverityByStats>();

	public float offsetSeverityBodySizeFactor;

	public bool hediffStacks;

	[Obsolete]
	public StatDef offsetSeverityByStat;

	[Obsolete]
	public bool offsetSeverityBodySize;
}
