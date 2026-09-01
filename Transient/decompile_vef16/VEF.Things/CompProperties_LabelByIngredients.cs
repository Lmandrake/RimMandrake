using System.Collections.Generic;
using Verse;

namespace VEF.Things;

public class CompProperties_LabelByIngredients : CompProperties
{
	public bool fullReplace;

	public Dictionary<ThingDef, string> overrides = new Dictionary<ThingDef, string>();

	public List<ThingDef> exclusions = new List<ThingDef>();

	public CompProperties_LabelByIngredients()
	{
		base.compClass = typeof(CompLabelByIngredients);
	}
}
