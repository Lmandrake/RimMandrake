using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_GraphicByStyle : CompProperties
{
	public List<StyleGraphics> styleGraphics;

	public int changeGraphicsInterval = 2000;

	public CompProperties_GraphicByStyle()
	{
		base.compClass = typeof(CompGraphicByStyle);
	}
}
