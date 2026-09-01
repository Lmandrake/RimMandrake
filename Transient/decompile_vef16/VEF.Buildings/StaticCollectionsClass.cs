using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public static class StaticCollectionsClass
{
	public static HashSet<BuildableDef> hidden_designators;

	static StaticCollectionsClass()
	{
		hidden_designators = new HashSet<BuildableDef>();
		foreach (HiddenDesignatorsDef item in DefDatabase<HiddenDesignatorsDef>.AllDefsListForReading)
		{
			foreach (BuildableDef hiddenDesignator in item.hiddenDesignators)
			{
				hidden_designators.Add(hiddenDesignator);
			}
		}
	}
}
