using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Graphics;

[StaticConstructorOnStartup]
public static class StaticCollectionsClass
{
	public static Dictionary<ThingDef, Dictionary<ThingDef, int>> graphicOffsets;

	static StaticCollectionsClass()
	{
		graphicOffsets = new Dictionary<ThingDef, Dictionary<ThingDef, int>>();
		foreach (GraphicOffsets item in DefDatabase<GraphicOffsets>.AllDefsListForReading.ToList())
		{
			if (graphicOffsets.ContainsKey(item.thingDef))
			{
				GenCollection.AddRange<ThingDef, int>((IDictionary<ThingDef, int>)graphicOffsets[item.thingDef], (IDictionary<ThingDef, int>)item.ingredientsAndOffsetList);
			}
			else
			{
				graphicOffsets[item.thingDef] = item.ingredientsAndOffsetList;
			}
		}
	}
}
