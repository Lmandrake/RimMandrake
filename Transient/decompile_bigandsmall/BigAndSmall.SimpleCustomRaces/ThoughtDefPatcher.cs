using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall.SimpleCustomRaces;

public static class ThoughtDefPatcher
{
	public static void PatchDefs()
	{
		foreach (HediffDef allDef in DefDatabase<HediffDef>.AllDefs)
		{
			foreach (PawnExtension item in from x in allDef.ExtensionsOnDef<PawnExtension, HediffDef>((List<Type>)null, (List<Type>)null, doSort: true)
				where x.nullsThoughts != null
				select x)
			{
				foreach (ThoughtDef nullsThought in item.nullsThoughts)
				{
					ThoughtDef current2;
					ThoughtDef obj = (current2 = nullsThought);
					if (current2.nullifyingHediffs == null)
					{
						current2.nullifyingHediffs = new List<HediffDef>();
					}
					GenCollection.AddDistinct<HediffDef>(obj.nullifyingHediffs, allDef);
				}
			}
		}
		if (!ModsConfig.BiotechActive)
		{
			return;
		}
		foreach (GeneDef allDef2 in DefDatabase<GeneDef>.AllDefs)
		{
			foreach (PawnExtension item2 in from x in allDef2.ExtensionsOnDef<PawnExtension, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true)
				where x.nullsThoughts != null
				select x)
			{
				foreach (ThoughtDef nullsThought2 in item2.nullsThoughts)
				{
					ThoughtDef current2;
					ThoughtDef obj2 = (current2 = nullsThought2);
					if (current2.nullifyingGenes == null)
					{
						current2.nullifyingGenes = new List<GeneDef>();
					}
					GenCollection.AddDistinct<GeneDef>(obj2.nullifyingGenes, allDef2);
				}
			}
		}
	}
}
