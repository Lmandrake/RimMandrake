using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class Furniture_Settings : ModSettings
{
	public static bool isRandomGraphic = true;

	public static bool hideRandomizeButton = false;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<bool>(ref isRandomGraphic, "isRandomGraphic", true, true);
		Scribe_Values.Look<bool>(ref hideRandomizeButton, "hideRandomizeButton", false, true);
	}

	public static void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VFE_RandomOrSequentially")), ref isRandomGraphic, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VFE_HideRandomizeButton")), ref hideRandomizeButton, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		((Listing)val).End();
	}
}
