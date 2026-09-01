using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class TransitioningHediffProps : DefModExtension
{
	public class Trigger
	{
		public bool xenogene;

		public List<GeneDef> geneDefsToAdd = new List<GeneDef>();

		public List<GeneDef> geneDefsToRemove = new List<GeneDef>();

		public List<HediffDef> hediffsToAdd = new List<HediffDef>();

		public List<HediffDef> hediffsToRemove = new List<HediffDef>();

		public XenotypeDef xenoTypeToAdd;

		public XenotypeDef xenoTypeToReplace;

		public bool resurrect;

		public bool perfectResurrect;
	}

	public class ConditionalTrigger
	{
		public List<ConditionalStatAffecter> conditionals;

		public Trigger trigger;
	}

	public class SeverityTrigger
	{
		public float severity;

		public Trigger trigger;
	}

	public Trigger onHediffAdded;

	public Trigger onHediffRemoved;

	public List<SeverityTrigger> onSeverity;

	public ConditionalTrigger onStat;

	public ConditionalTrigger onStatRemoved;
}
