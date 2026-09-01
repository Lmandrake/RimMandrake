using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace FactionLoadout.Util;

public static class StyleHelper
{
	public static IEnumerable<(ThingStyleDef style, string name, Texture2D exampleIcon)> GetValidStyles(ThingDef def)
	{
		foreach (StyleCategoryDef item in DefDatabase<StyleCategoryDef>.AllDefsListForReading)
		{
			if (item.thingDefStyles == null)
			{
				continue;
			}
			foreach (ThingDefStyle thingDefStyle in item.thingDefStyles)
			{
				if (thingDefStyle.ThingDef == def)
				{
					yield return (style: thingDefStyle.StyleDef, name: TaggedString.op_Implicit(((Def)item).LabelCap), exampleIcon: Widgets.GetIconFor(thingDefStyle.ThingDef, (ThingDef)null, thingDefStyle.StyleDef, (int?)null));
				}
			}
		}
	}
}
