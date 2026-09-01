using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Dialog_InfoCard), "FillCard")]
public static class VanillaExpandedFramework_Dialog_InfoCard_FillCard_Patch
{
	public static AnimalStatExtension extension;

	public static Rect rect;

	public static bool Prefix(Rect cardRect, Dialog_InfoCard __instance, Thing ___thing, InfoCardTab ___tab)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		rect = cardRect;
		if (___thing == null)
		{
			return true;
		}
		if (((Def)___thing.def).GetModExtension<AnimalStatExtension>() != null)
		{
			extension = ((Def)___thing.def).GetModExtension<AnimalStatExtension>();
			if (extension.showImageInInfoCard && (int)___tab == 0)
			{
				Texture2D val = ContentFinder<Texture2D>.Get(extension.ImageToShowInInfoCard, false);
				Rect val2 = GenUI.AtZero(rect);
				((Rect)(ref val2)).width = 384f;
				((Rect)(ref val2)).height = 576f;
				((Rect)(ref val2)).x = ((Rect)(ref rect)).width * 0.75f - ((Rect)(ref val2)).width / 2f + 18f;
				((Rect)(ref val2)).y = ((Rect)(ref rect)).center.y - ((Rect)(ref val2)).height / 2f + 120f;
				GUI.DrawTexture(val2, (Texture)(object)val, (ScaleMode)2, true);
			}
		}
		return true;
	}
}
