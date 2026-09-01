using Verse;

namespace VEF.Graphics;

public class ThingWithFloorGraphic : ThingWithComps
{
	public Graphic graphicIntOverride;

	public override Graphic Graphic
	{
		get
		{
			if (((Thing)this).ParentHolder is Map)
			{
				FloorGraphicExtension modExtension = ((Def)((Thing)this).def).GetModExtension<FloorGraphicExtension>();
				if (modExtension != null)
				{
					return FloorGraphic(modExtension);
				}
			}
			return ((Thing)this).Graphic;
		}
	}

	public Graphic FloorGraphic(FloorGraphicExtension floorGraphicExtension)
	{
		if (graphicIntOverride == null)
		{
			if (floorGraphicExtension.graphicData == null)
			{
				return BaseContent.BadGraphic;
			}
			graphicIntOverride = floorGraphicExtension.graphicData.GraphicColoredFor((Thing)(object)this);
		}
		return graphicIntOverride;
	}
}
