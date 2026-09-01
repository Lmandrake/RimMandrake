using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class Dialog_ChooseGraphic : Window
{
	private static readonly Color borderColor = new Color(0.13f, 0.13f, 0.13f);

	private static readonly Color fillColor = new Color(0f, 0f, 0f, 0.1f);

	public Thing thingToChange;

	private Vector2 scrollPosition = new Vector2(0f, 0f);

	public int columnCount = 4;

	private List<string> buildingGraphics;

	private CompProperties_RandomBuildingGraphic Props;

	public override Vector2 InitialSize => new Vector2(620f, 500f);

	public Dialog_ChooseGraphic(Thing thing, CompProperties_RandomBuildingGraphic Props)
		: base((IWindowDrawing)null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		thingToChange = thing;
		base.doCloseX = true;
		base.doCloseButton = true;
		base.closeOnClickedOutside = true;
		buildingGraphics = Props.randomGraphics;
		this.Props = Props;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_03fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0406: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_0288: Unknown result type (might be due to invalid IL or missing references)
		//IL_028a: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_029a: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b0: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)1;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(inRect);
		((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 30f;
		((Rect)(ref val)).yMax = ((Rect)(ref val)).yMax - 40f;
		if (buildingGraphics.Count > 0)
		{
			Widgets.Label(new Rect(0f, 10f, 300f, 30f), Translator.Translate("VFE_ChooseGraphic"));
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(0f, 30f, ((Rect)(ref val)).width - 16f, (float)(buildingGraphics.Count / 4) * 128f + 256f);
			Color val3 = thingToChange.Graphic.Color;
			if (thingToChange.Stuff != null)
			{
				val3 = ((BuildableDef)thingToChange.def).GetColorForStuff(thingToChange.Stuff);
			}
			Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
			Rect val4 = default(Rect);
			for (int i = 0; i < buildingGraphics.Count; i++)
			{
				string text = "";
				text = ((thingToChange.StyleDef == null || i != 0) ? buildingGraphics[i] : ((thingToChange.StyleDef.graphicData == null) ? thingToChange.StyleDef.Graphic.path : thingToChange.StyleDef.graphicData.GraphicColoredFor(thingToChange).path));
				string text2 = ((!GenList.NullOrEmpty<string>((IList<string>)Props.optionalNames) && Props.optionalNames.Count >= i) ? Props.optionalNames[i] : buildingGraphics[i]);
				if (thingToChange.def.graphicData.graphicClass == typeof(Graphic_Multi))
				{
					text = ((!Props.useSouthOrientation) ? (text + "_north") : (text + "_south"));
				}
				((Rect)(ref val4))._002Ector((float)(128 * (i % columnCount) + 10 * (i % columnCount)), ((Rect)(ref val2)).y + (float)(128 * (i / columnCount) + 20 * (i / columnCount + 1)), 128f, 128f);
				Widgets.DrawBoxSolidWithOutline(val4, fillColor, borderColor, 2);
				GUI.DrawTexture(GenUI.ContractedBy(val4, 2f), (Texture)(object)ContentFinder<Texture2D>.Get(text, true), (ScaleMode)2, true, 0f, val3, 0f, 0f);
				if (Widgets.ButtonInvisible(val4, true))
				{
					foreach (object selectedObject in Find.Selector.SelectedObjects)
					{
						Thing thing = (Thing)((selectedObject is Thing) ? selectedObject : null);
						if (thing == null || thing.def != thingToChange.def)
						{
							continue;
						}
						if (thing.StyleDef != null && i == 0)
						{
							ThingCompUtility.TryGetComp<CompRandomBuildingGraphic>(thing).ResetGraphics();
						}
						else
						{
							LongEventHandler.ExecuteWhenFinished((Action)delegate
							{
								ThingCompUtility.TryGetComp<CompRandomBuildingGraphic>(thing).ChangeGraphic(random: false, i);
							});
						}
						thing.DirtyMapMesh(thing.Map);
					}
					((Window)this).Close(true);
				}
				TooltipHandler.TipRegion(val4, TipSignal.op_Implicit(text2));
			}
			Widgets.EndScrollView();
		}
		else
		{
			Widgets.Label(new Rect(0f, 10f, 300f, 30f), Translator.Translate("VFE_NoGraphics"));
		}
	}
}
