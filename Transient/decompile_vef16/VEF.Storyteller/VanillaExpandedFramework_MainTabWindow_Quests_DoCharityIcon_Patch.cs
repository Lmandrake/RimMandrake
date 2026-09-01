using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(MainTabWindow_Quests), "DoCharityIcon")]
public static class VanillaExpandedFramework_MainTabWindow_Quests_DoCharityIcon_Patch
{
	public static void Postfix(MainTabWindow_Quests __instance, Rect innerRect, Quest ___selected)
	{
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		if (___selected == null)
		{
			return;
		}
		QuestChainExtension modExtension = ((Def)___selected.root).GetModExtension<QuestChainExtension>();
		if (modExtension != null)
		{
			bool num = ___selected.charity && ModsConfig.IdeologyActive;
			Rect val = default(Rect);
			((Rect)(ref val))._002Ector(((Rect)(ref innerRect)).xMax - 32f - 26f - 32f - 4f, ((Rect)(ref innerRect)).y, 32f, 32f);
			if (num)
			{
				((Rect)(ref val)).x = ((Rect)(ref val)).x - 36f;
			}
			GUI.DrawTexture(val, (Texture)(object)modExtension.questChainDef.icon);
			if (Mouse.IsOver(val))
			{
				TooltipHandler.TipRegion(val, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.QuestChainTooltip", NamedArgument.op_Implicit(((Def)modExtension.questChainDef).label), NamedArgument.op_Implicit(modExtension.questChainDef.Worker.GetDescription()))));
			}
		}
	}
}
