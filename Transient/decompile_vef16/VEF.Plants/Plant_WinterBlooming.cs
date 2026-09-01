using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Plants;

[StaticConstructorOnStartup]
public class Plant_WinterBlooming : Plant
{
	private static Graphic GraphicSowing = GraphicDatabase.Get<Graphic_Single>("Things/Plant/Plant_Sowing", ShaderDatabase.Cutout, Vector2.one, Color.white);

	private static Graphic GraphicWinter = GraphicDatabase.Get<Graphic_Random>("Things/Plant/TreeOak", ShaderDatabase.CutoutPlant, Vector2.one, Color.white);

	private bool? extensionPresent;

	private WinterBloomingExtension defExtension;

	public WinterBloomingExtension DefExtension
	{
		get
		{
			if (extensionPresent.HasValue)
			{
				if (!extensionPresent.Value)
				{
					return null;
				}
				return defExtension;
			}
			extensionPresent = (defExtension = ((Def)((Thing)this).def).GetModExtension<WinterBloomingExtension>()) != null;
			return defExtension;
		}
	}

	public override Graphic Graphic
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Invalid comparison between Unknown and I4
			if ((int)((Plant)this).LifeStage == 0)
			{
				WinterBloomingExtension winterBloomingExtension = DefExtension;
				object obj;
				if (winterBloomingExtension == null)
				{
					obj = null;
				}
				else
				{
					GraphicData graphicSowing = winterBloomingExtension.graphicSowing;
					obj = ((graphicSowing != null) ? graphicSowing.Graphic : null);
				}
				if (obj == null)
				{
					obj = GraphicSowing;
				}
				return (Graphic)obj;
			}
			Vector2 val = Find.WorldGrid.LongLatOf(((Thing)this).Map.Tile);
			if ((int)GenDate.Season((long)Find.TickManager.TicksAbs, val) == 4)
			{
				WinterBloomingExtension winterBloomingExtension2 = DefExtension;
				object obj2;
				if (winterBloomingExtension2 == null)
				{
					obj2 = null;
				}
				else
				{
					GraphicData graphicWinter = winterBloomingExtension2.graphicWinter;
					obj2 = ((graphicWinter != null) ? graphicWinter.Graphic : null);
				}
				if (obj2 == null)
				{
					obj2 = GraphicWinter;
				}
				return (Graphic)obj2;
			}
			if (((Thing)this).def.plant.leaflessGraphic != null && ((Plant)this).LeaflessNow && (!base.sown || !((Plant)this).HarvestableNow))
			{
				return ((Thing)this).def.plant.leaflessGraphic;
			}
			if (((Thing)this).def.plant.immatureGraphic != null && !((Plant)this).HarvestableNow)
			{
				return ((Thing)this).def.plant.immatureGraphic;
			}
			return ((Plant)this).Graphic;
		}
	}
}
