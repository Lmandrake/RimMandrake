using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(MainTabWindow_Quests), "DoRow")]
public static class VanillaExpandedFramework_MainTabWindow_Quests_DoRow_Patch
{
	public static void Postfix(Rect rect, Quest quest)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_0177: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		QuestChainExtension modExtension = ((Def)quest.root).GetModExtension<QuestChainExtension>();
		if (modExtension != null)
		{
			bool num = ModsConfig.IdeologyActive && quest.charity && !quest.Historical && !quest.dismissed;
			Rect val = rect;
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 95f;
			Rect val2 = rect;
			((Rect)(ref val2)).xMax = ((Rect)(ref val2)).xMax - 4f;
			((Rect)(ref val2)).xMin = ((Rect)(ref val2)).xMax - 35f;
			Rect val3 = rect;
			((Rect)(ref val3)).xMax = ((Rect)(ref val2)).xMin;
			((Rect)(ref val3)).xMin = ((Rect)(ref val3)).xMax - 60f;
			if (num)
			{
				((Rect)(ref val3)).x = ((Rect)(ref val3)).x - 15f;
			}
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(((Rect)(ref val3)).x - 15f, ((Rect)(ref val3)).y + ((Rect)(ref val3)).height / 2f - 7f, 15f, 15f);
			GUI.DrawTexture(val4, (Texture)(object)modExtension.questChainDef.icon);
			Rect val5 = default(Rect);
			((Rect)(ref val5))._002Ector(((Rect)(ref val)).x + 4f, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 4f, ((Rect)(ref val)).height);
			((Rect)(ref val4)).height = ((Rect)(ref val5)).height;
			((Rect)(ref val4)).y = ((Rect)(ref val5)).y;
			if (Mouse.IsOver(val4))
			{
				TooltipHandler.TipRegion(val4, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.QuestChainTooltip", NamedArgument.op_Implicit(((Def)modExtension.questChainDef).label), NamedArgument.op_Implicit(modExtension.questChainDef.Worker.GetDescription()))));
				Widgets.DrawHighlight(val4);
			}
		}
	}
}
