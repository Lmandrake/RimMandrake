using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompProperties_CustomizableGraphic : CompProperties
{
	public class CustomizableGraphicOptionData
	{
		public string name;

		public int sortingPriority;

		public int clockwiseRotationIndex = -1;
	}

	public string iconPath = "UI/VEF_ChooseGraphic";

	private Texture2D icon;

	public string gizmoLabel;

	public string gizmoDescription;

	public int defaultIndex = -1;

	public Dictionary<ThingStyleDef, int> defaultStyleIndex;

	public List<CustomizableGraphicOptionData> defaultGraphicData;

	public Dictionary<ThingStyleDef, List<CustomizableGraphicOptionData>> styledGraphicData;

	public Texture2D Icon
	{
		get
		{
			Texture2D obj = icon;
			if (obj == null)
			{
				Texture2D obj2 = ContentFinder<Texture2D>.Get(iconPath, true) ?? BaseContent.BadTex;
				Texture2D val = obj2;
				icon = obj2;
				obj = val;
			}
			return obj;
		}
	}

	public CompProperties_CustomizableGraphic()
	{
		base.compClass = typeof(CompCustomizableGraphic);
	}
}
