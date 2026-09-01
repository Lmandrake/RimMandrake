using System.Collections.Generic;
using Verse;

namespace VEF.Graphics;

[StaticConstructorOnStartup]
public class GraphicOffsets : Def
{
	public ThingDef thingDef;

	public Dictionary<ThingDef, int> ingredientsAndOffsetList;
}
