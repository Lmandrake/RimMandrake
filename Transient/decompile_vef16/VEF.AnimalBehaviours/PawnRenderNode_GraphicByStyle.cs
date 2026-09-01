using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class PawnRenderNode_GraphicByStyle : PawnRenderNode_AnimalPart
{
	public PawnRenderNode_GraphicByStyle(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		CompGraphicByStyle compGraphicByStyle = default(CompGraphicByStyle);
		if (ThingCompUtility.TryGetComp<CompGraphicByStyle>((ThingWithComps)(object)pawn, ref compGraphicByStyle))
		{
			Graphic graphic = pawn.ageTracker.CurKindLifeStage.bodyGraphicData.Graphic;
			StyleCategoryDef style = null;
			List<ThingStyleCategoryWithPriority> thingStyleCategories = Current.Game.World.factionManager.OfPlayer.ideos.PrimaryIdeo.thingStyleCategories;
			List<StyleCategoryDef> list = new List<StyleCategoryDef>();
			List<StyleCategoryDef> list2 = new List<StyleCategoryDef>();
			if (thingStyleCategories.Count > 0)
			{
				foreach (ThingStyleCategoryWithPriority item in thingStyleCategories)
				{
					list.Add(item.category);
				}
				foreach (StyleGraphics styleGraphic in compGraphicByStyle.Props.styleGraphics)
				{
					list2.Add(styleGraphic.style);
				}
				foreach (StyleCategoryDef item2 in list)
				{
					foreach (StyleCategoryDef item3 in list2)
					{
						if (item2 == item3)
						{
							style = item3;
							break;
						}
					}
				}
				if (style != null)
				{
					StyleGraphics styleGraphics = compGraphicByStyle.Props.styleGraphics.Where((StyleGraphics x) => x.style == style).FirstOrDefault();
					return GraphicDatabase.Get<Graphic_Multi>(graphic.path + styleGraphics.styleImageSuffix, ShaderDatabase.Cutout, graphic.drawSize, Color.white);
				}
			}
		}
		return ((PawnRenderNode_AnimalPart)this).GraphicFor(pawn);
	}
}
