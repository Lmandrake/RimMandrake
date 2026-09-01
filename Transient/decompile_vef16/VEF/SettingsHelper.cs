using UnityEngine;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class SettingsHelper
{
	public static bool Settings_Button(this Listing_Standard ls, string label, Rect rect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		bool result = Widgets.ButtonText(rect, label, true, true, true, (TextAnchor?)null);
		((Listing)ls).Gap(2f);
		return result;
	}

	public static Rect LabelPlusButton(this Listing_Standard ls, string label, string tooltip = null)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		float num = Text.CalcHeight(label, ((Listing)ls).ColumnWidth);
		Rect rect = ((Listing)ls).GetRect(num, 1f);
		Widgets.Label(rect, label);
		if (tooltip != null)
		{
			TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(tooltip));
		}
		((Listing)ls).Gap(50f);
		return rect;
	}
}
