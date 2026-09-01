using System.Collections.Generic;
using Verse;

namespace VEF.Graphics;

public class CompProperties_GraphicCustomization : CompProperties
{
	public List<GraphicPart> graphics;

	public bool customizable;

	public string customizationTitle;

	public CompProperties_GraphicCustomization()
	{
		base.compClass = typeof(CompGraphicCustomization);
	}
}
