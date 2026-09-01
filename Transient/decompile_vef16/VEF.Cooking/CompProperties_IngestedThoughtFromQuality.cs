using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Cooking;

public class CompProperties_IngestedThoughtFromQuality : CompProperties
{
	public ThoughtDef ingestedThought;

	public CompProperties_IngestedThoughtFromQuality()
	{
		base.compClass = typeof(CompIngestedThoughtFromQuality);
	}

	public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
	{
		if (!parentDef.HasComp(typeof(CompQuality)))
		{
			yield return $"{parentDef} does not have CompQuality but is using CompProperties_IngestedThoughtFromQuality.";
		}
		if (!ingestedThought.IsMemory)
		{
			yield return $"{parentDef} CompProperties_IngestedThoughtFromQuality {ingestedThought}'s thoughtClass is not a Thought_Memory.";
		}
	}
}
