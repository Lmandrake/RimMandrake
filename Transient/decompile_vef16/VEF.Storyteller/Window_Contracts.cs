using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Storyteller;

[StaticConstructorOnStartup]
public class Window_Contracts : Window
{
	private QuestGiverManager questGiverManager;

	private QuestInfo selected;

	private Vector2 scrollPosition_available;

	private Vector2 selectedQuestScrollPosition;

	private float selectedQuestLastHeight;

	private List<QuestPart> tmpQuestParts = new List<QuestPart>();

	private static readonly Color AcceptanceRequirementsColor = new Color(1f, 0.25f, 0.25f);

	private static readonly Color AcceptanceRequirementsBoxColor = new Color(0.62f, 0.18f, 0.18f);

	private static readonly Color acceptanceRequirementsBoxBgColor = new Color(0.13f, 0.13f, 0.13f);

	private static Texture2D RatingIcon = null;

	private static List<AnonymousStackElement> tmpStackElements = new List<AnonymousStackElement>();

	private static List<Rect> layoutRewardsRects = new List<Rect>();

	private static List<QuestPart> tmpRemainingQuestParts = new List<QuestPart>();

	private static List<GlobalTargetInfo> tmpLookTargets = new List<GlobalTargetInfo>();

	private static List<GlobalTargetInfo> tmpSelectTargets = new List<GlobalTargetInfo>();

	public override Vector2 InitialSize => new Vector2(1010f, 640f);

	public override void PreOpen()
	{
		((Window)this).PreOpen();
		if ((Object)(object)RatingIcon == (Object)null)
		{
			RatingIcon = ContentFinder<Texture2D>.Get("UI/Icons/ChallengeRatingIcon", true);
		}
		Select(selected);
	}

	public Window_Contracts(QuestGiverManager questGiverManager)
		: base((IWindowDrawing)null)
	{
		this.questGiverManager = questGiverManager;
		base.closeOnClickedOutside = true;
	}

	public override void DoWindowContents(Rect rect)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)2;
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y, 400f, 30f), TranslatorFormattedStringExtensions.Translate(questGiverManager.def.windowTitleKey ?? "VEF.AvailableContracts", NamedArgument.op_Implicit(questGiverManager.AvailableQuests.Count)));
		Rect rect2 = rect;
		((Rect)(ref rect2)).yMin = ((Rect)(ref rect2)).yMin + 4f;
		((Rect)(ref rect2)).xMax = ((Rect)(ref rect2)).width * 0.5f;
		((Rect)(ref rect2)).yMin = ((Rect)(ref rect2)).yMin + 32f;
		((Rect)(ref rect2)).yMax = ((Rect)(ref rect2)).yMax - 45f;
		DoQuestsList(rect2);
		Rect rect3 = rect;
		((Rect)(ref rect3)).yMin = ((Rect)(ref rect3)).yMin + 4f;
		((Rect)(ref rect3)).xMin = ((Rect)(ref rect2)).xMax + 17f;
		((Rect)(ref rect3)).yMin = ((Rect)(ref rect3)).yMin + 32f;
		((Rect)(ref rect3)).yMax = ((Rect)(ref rect3)).yMax - 45f;
		DoSelectedQuestInfo(rect3);
	}

	public void Select(QuestInfo questInfo)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		if (questInfo != selected)
		{
			selected = questInfo;
			selectedQuestScrollPosition = default(Vector2);
			selectedQuestLastHeight = 300f;
		}
	}

	private void DoQuestsList(Rect rect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		Rect val = rect;
		Widgets.DrawMenuSection(val);
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)0;
		if (questGiverManager.AvailableQuests.Count != 0)
		{
			Rect val2 = val;
			val2 = GenUI.ContractedBy(val2, 10f);
			((Rect)(ref val2)).xMax = ((Rect)(ref val2)).xMax + 6f;
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(0f, 0f, ((Rect)(ref val2)).width - 16f, (float)questGiverManager.AvailableQuests.Count * 32f);
			Vector2 val4 = default(Vector2);
			Widgets.BeginScrollView(val2, ref scrollPosition_available, val3, true);
			val4 = scrollPosition_available;
			float num = 0f;
			for (int i = 0; i < questGiverManager.AvailableQuests.Count; i++)
			{
				float num2 = val4.y - 32f;
				float num3 = val4.y + ((Rect)(ref val2)).height;
				if (num > num2 && num < num3)
				{
					DoRow(new Rect(0f, num, ((Rect)(ref val3)).width - 4f, 32f), questGiverManager.AvailableQuests[i]);
				}
				num += 32f;
			}
			Widgets.EndScrollView();
			Rect val5 = default(Rect);
			((Rect)(ref val5))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).yMax + 7f, ((Rect)(ref rect)).xMax, 40f);
			if (selected != null)
			{
				if (!AcceptanceReport.op_Implicit(QuestUtility.CanAcceptQuest(selected.Quest)))
				{
					GUI.color = Color.grey;
				}
				if (Widgets.ButtonText(val5, TaggedString.op_Implicit(Translator.Translate("AcceptQuest")), true, true, true, (TextAnchor?)null))
				{
					if (selected.choice != null)
					{
						tmpRemainingQuestParts.Clear();
						tmpRemainingQuestParts.AddRange(selected.Quest.PartsListForReading);
						for (int j = 0; j < selected.quest_Part_choice.choices.Count; j++)
						{
							for (int k = 0; k < selected.choice.questParts.Count; k++)
							{
								QuestPart item = selected.choice.questParts[k];
								if (!selected.choice.questParts.Contains(item))
								{
									tmpRemainingQuestParts.Remove(item);
								}
							}
						}
						bool requiresAccepter = false;
						for (int l = 0; l < tmpRemainingQuestParts.Count; l++)
						{
							if (tmpRemainingQuestParts[l].RequiresAccepter)
							{
								requiresAccepter = true;
								break;
							}
						}
						tmpRemainingQuestParts.Clear();
						AcceptQuestByInterface(delegate
						{
							selected.quest_Part_choice.Choose(selected.choice);
						}, requiresAccepter);
					}
					else
					{
						AcceptQuestByInterface(null, selected.Quest.RequiresAccepter);
					}
				}
			}
			TooltipHandler.TipRegionByKey(val5, "AcceptQuestForTip");
			GUI.color = Color.white;
		}
		else
		{
			Widgets.NoneLabel(((Rect)(ref val)).y + 17f, ((Rect)(ref val)).width, (string)null);
		}
	}

	private void DoRow(Rect rect, QuestInfo questInfo)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0198: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		Rect val = rect;
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 200f;
		Rect val2 = rect;
		((Rect)(ref val2)).x = ((Rect)(ref val)).xMax - 4f;
		((Rect)(ref val2)).xMax = ((Rect)(ref rect)).xMax;
		Rect val3 = rect;
		((Rect)(ref val3)).width = ((Rect)(ref val3)).width + 14f;
		if (selected == questInfo)
		{
			Widgets.DrawHighlightSelected(val3);
		}
		Rect val4 = val2;
		((Rect)(ref val4)).width = 60f;
		Text.Anchor = (TextAnchor)3;
		Rect val5 = default(Rect);
		((Rect)(ref val5))._002Ector(((Rect)(ref val)).x + 4f, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 4f, ((Rect)(ref val)).height);
		Widgets.Label(val5, GenText.Truncate(questInfo.Quest.name, ((Rect)(ref val5)).width, (Dictionary<string, string>)null));
		for (int i = 0; i < questInfo.Quest.challengeRating; i++)
		{
			GUI.DrawTexture(new Rect(((Rect)(ref val2)).x + (float)(15 * (i + 1)), ((Rect)(ref val2)).y + ((Rect)(ref val2)).height / 2f - 7f, 15f, 15f), (Texture)(object)RatingIcon);
		}
		if (Mouse.IsOver(val4))
		{
			TooltipHandler.TipRegion(val4, TipSignal.op_Implicit(Translator.Translate("QuestChallengeRatingTip")));
			Widgets.DrawHighlight(val4);
		}
		float num = ((Rect)(ref val2)).x + 7f + 60f;
		if (questInfo.currencyInfo == null)
		{
			num += 120f;
		}
		Rect r = default(Rect);
		((Rect)(ref r))._002Ector(num, ((Rect)(ref rect)).y + 2f, ((Rect)(ref rect)).height - 4f, ((Rect)(ref rect)).height - 4f);
		DrawFactionIconWithTooltip(r, questInfo.askerFaction);
		if (questInfo.currencyInfo != null)
		{
			Rect val6 = new Rect(((Rect)(ref r)).xMax + 10f, ((Rect)(ref rect)).y, 200f, ((Rect)(ref rect)).height);
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val6, questInfo.currencyInfo.GetCurrencyInfo());
		}
		GenUI.ResetLabelAlign();
		if (Widgets.ButtonInvisible(rect, true))
		{
			Select(questInfo);
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
		}
	}

	public void DrawFactionIconWithTooltip(Rect r, Faction faction)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		GUI.color = faction.Color;
		GUI.DrawTexture(r, (Texture)(object)faction.def.FactionIcon);
		GUI.color = Color.white;
		if (Mouse.IsOver(r))
		{
			TipSignal val = default(TipSignal);
			((TipSignal)(ref val))._002Ector((Func<string>)(() => faction.Name + "\n\n" + ((Def)faction.def).description), faction.loadID ^ 0x738AC053);
			TooltipHandler.TipRegion(r, val);
			Widgets.DrawHighlight(r);
		}
	}

	private void DoSelectedQuestInfo(Rect rect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		Widgets.DrawMenuSection(rect);
		if (selected == null)
		{
			Widgets.NoneLabelCenteredVertically(rect, TaggedString.op_Implicit("(" + Translator.Translate("NoQuestSelected") + ")"));
			return;
		}
		Rect val = GenUI.ContractedBy(rect, 17f);
		Rect val2 = val;
		Rect innerRect = default(Rect);
		((Rect)(ref innerRect))._002Ector(0f, 0f, ((Rect)(ref val2)).width, selectedQuestLastHeight);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(0f, 0f, ((Rect)(ref val2)).width - 16f, selectedQuestLastHeight);
		Rect rect2 = val3;
		bool flag = ((Rect)(ref val3)).height > ((Rect)(ref val)).height;
		if (flag)
		{
			((Rect)(ref val3)).width = ((Rect)(ref val3)).width - 4f;
			((Rect)(ref rect2)).width = ((Rect)(ref rect2)).width - 16f;
		}
		Widgets.BeginScrollView(val2, ref selectedQuestScrollPosition, val3, true);
		float curY = 0f;
		DoTitle(val3, ref curY);
		if (selected != null)
		{
			DoDescription(val3, ref curY);
			DoAcceptanceRequirementInfo(innerRect, flag, ref curY);
			DoRewards(val3, ref curY);
			DoLookTargets(val3, ref curY);
			DoSelectTargets(val3, ref curY);
			float num = curY;
			DoDefHyperlinks(val3, ref curY);
			float num2 = curY;
			curY = num;
			if (!selected.Quest.root.hideInvolvedFactionsInfo)
			{
				DoFactionInfo(rect2, ref curY);
			}
			if (num2 > curY)
			{
				curY = num2;
			}
			selectedQuestLastHeight = curY;
		}
		Widgets.EndScrollView();
	}

	private void DoTitle(Rect innerRect, ref float curY)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)2;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 100f);
		Widgets.Label(val, GenText.Truncate(selected.Quest.name, ((Rect)(ref val)).width, (Dictionary<string, string>)null));
		Text.Font = (GameFont)1;
		curY += Text.LineHeight;
		curY += 17f;
	}

	private void DoAcceptanceRequirementInfo(Rect innerRect, bool scrollBarVisible, ref float curY)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Expected O, but got Unknown
		if (selected.Quest.EverAccepted)
		{
			return;
		}
		IEnumerable<string> enumerable = ListUnmetAcceptRequirements();
		int num = enumerable.Count();
		if (num != 0)
		{
			bool flag = num > 1;
			string text = TaggedString.op_Implicit(Translator.Translate("QuestAcceptanceRequirementsDescription") + (flag ? ": " : " ") + (flag ? ("\n" + GenText.ToLineList(enumerable, "  - ", true)) : (enumerable.First() + ".")));
			curY += 17f;
			float num2 = 0f;
			float num3 = ((Rect)(ref innerRect)).x + 8f;
			float num4 = ((Rect)(ref innerRect)).width - 16f;
			if (scrollBarVisible)
			{
				num4 -= 31f;
			}
			Rect val = default(Rect);
			((Rect)(ref val))._002Ector(num3, curY, num4, 10000f);
			num2 += Text.CalcHeight(text, ((Rect)(ref val)).width);
			Rect val2 = GenUI.ExpandedBy(new Rect(num3, curY, num4, num2), 8f);
			Widgets.DrawBoxSolid(val2, acceptanceRequirementsBoxBgColor);
			GUI.color = AcceptanceRequirementsColor;
			Widgets.Label(val, text);
			GUI.color = AcceptanceRequirementsBoxColor;
			Widgets.DrawBox(val2, 2, (Texture2D)null);
			curY += num2;
			GUI.color = Color.white;
			LookTargetsUtility.TryHighlight(new LookTargets(ListUnmetAcceptRequirementCulprits()), true, true, true);
		}
	}

	private IEnumerable<string> ListUnmetAcceptRequirements()
	{
		for (int i = 0; i < selected.Quest.PartsListForReading.Count; i++)
		{
			QuestPart obj = selected.Quest.PartsListForReading[i];
			QuestPart_RequirementsToAccept val = (QuestPart_RequirementsToAccept)(object)((obj is QuestPart_RequirementsToAccept) ? obj : null);
			if (val != null)
			{
				AcceptanceReport val2 = val.CanAccept();
				if (!((AcceptanceReport)(ref val2)).Accepted)
				{
					yield return ((AcceptanceReport)(ref val2)).Reason;
				}
			}
		}
	}

	private IEnumerable<GlobalTargetInfo> ListUnmetAcceptRequirementCulprits()
	{
		for (int i = 0; i < selected.Quest.PartsListForReading.Count; i++)
		{
			QuestPart obj = selected.Quest.PartsListForReading[i];
			QuestPart_RequirementsToAccept val = (QuestPart_RequirementsToAccept)(object)((obj is QuestPart_RequirementsToAccept) ? obj : null);
			if (val == null)
			{
				continue;
			}
			foreach (GlobalTargetInfo culprit in val.Culprits)
			{
				yield return culprit;
			}
		}
	}

	private void DoDescription(Rect innerRect, ref float curY)
	{
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Invalid comparison between Unknown and I4
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		if (!GenText.NullOrEmpty(((TaggedString)(ref selected.Quest.description)).RawText))
		{
			string value = ((TaggedString)(ref selected.Quest.description)).Resolve();
			stringBuilder.Append(value);
		}
		tmpQuestParts.Clear();
		tmpQuestParts.AddRange(selected.Quest.PartsListForReading);
		GenCollection.SortBy<QuestPart, int>(tmpQuestParts, (Func<QuestPart, int>)((QuestPart x) => (x is QuestPartActivable) ? ((QuestPartActivable)x).EnableTick : 0));
		for (int i = 0; i < tmpQuestParts.Count; i++)
		{
			QuestPart obj = tmpQuestParts[i];
			QuestPartActivable val = (QuestPartActivable)(object)((obj is QuestPartActivable) ? obj : null);
			if (val != null && (int)val.State != 1)
			{
				continue;
			}
			string descriptionPart = tmpQuestParts[i].DescriptionPart;
			if (!GenText.NullOrEmpty(descriptionPart))
			{
				if (stringBuilder.Length != 0)
				{
					stringBuilder.AppendLine();
					stringBuilder.AppendLine();
				}
				stringBuilder.Append(descriptionPart);
			}
		}
		tmpQuestParts.Clear();
		if (stringBuilder.Length != 0)
		{
			curY += 17f;
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 10000f);
			Widgets.Label(val2, stringBuilder.ToString());
			curY += Text.CalcHeight(stringBuilder.ToString(), ((Rect)(ref val2)).width);
		}
	}

	private void DoRewards(Rect innerRect, ref float curY)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Invalid comparison between Unknown and I4
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Invalid comparison between Unknown and I4
		//IL_070a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0710: Invalid comparison between Unknown and I4
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Expected O, but got Unknown
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Invalid comparison between Unknown and I4
		//IL_033f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0344: Unknown result type (might be due to invalid IL or missing references)
		//IL_0349: Unknown result type (might be due to invalid IL or missing references)
		//IL_0353: Unknown result type (might be due to invalid IL or missing references)
		//IL_0358: Unknown result type (might be due to invalid IL or missing references)
		//IL_036b: Unknown result type (might be due to invalid IL or missing references)
		//IL_036e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0378: Unknown result type (might be due to invalid IL or missing references)
		//IL_0392: Expected O, but got Unknown
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_045b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0402: Unknown result type (might be due to invalid IL or missing references)
		//IL_0416: Unknown result type (might be due to invalid IL or missing references)
		//IL_0434: Unknown result type (might be due to invalid IL or missing references)
		//IL_0445: Unknown result type (might be due to invalid IL or missing references)
		//IL_044f: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_04d4: Invalid comparison between Unknown and I4
		//IL_04db: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_052a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0531: Unknown result type (might be due to invalid IL or missing references)
		//IL_053b: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_06c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_06cf: Unknown result type (might be due to invalid IL or missing references)
		bool flag = (int)selected.Quest.State == 0;
		bool flag2 = true;
		if ((int)Event.current.type == 8)
		{
			layoutRewardsRects.Clear();
		}
		Rect val3;
		if (selected.choice != null)
		{
			tmpStackElements.Clear();
			float num = 0f;
			for (int i = 0; i < selected.choice.rewards.Count; i++)
			{
				tmpStackElements.AddRange(selected.choice.rewards[i].StackElements);
				num += selected.choice.rewards[i].TotalMarketValue;
			}
			if (GenCollection.Any<AnonymousStackElement>(tmpStackElements))
			{
				if (num > 0f)
				{
					TaggedString totalValueStr = TranslatorFormattedStringExtensions.Translate("TotalValue", NamedArgument.op_Implicit(GenText.ToStringMoney(num, "F0")));
					tmpStackElements.Add(new AnonymousStackElement
					{
						drawer = delegate(Rect r)
						{
							//IL_000f: Unknown result type (might be due to invalid IL or missing references)
							//IL_0041: Unknown result type (might be due to invalid IL or missing references)
							//IL_0047: Unknown result type (might be due to invalid IL or missing references)
							//IL_0051: Unknown result type (might be due to invalid IL or missing references)
							GUI.color = new Color(0.7f, 0.7f, 0.7f);
							Widgets.Label(new Rect(((Rect)(ref r)).x + 5f, ((Rect)(ref r)).y, ((Rect)(ref r)).width - 10f, ((Rect)(ref r)).height), totalValueStr);
							GUI.color = Color.white;
						},
						width = Text.CalcSize(TaggedString.op_Implicit(totalValueStr)).x + 10f
					});
				}
				if (flag2)
				{
					curY += 17f;
					flag2 = false;
				}
				else
				{
					curY += 10f;
				}
				Rect val = default(Rect);
				((Rect)(ref val))._002Ector(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 10000f);
				Rect val2 = GenUI.ContractedBy(val, 10f);
				val3 = GenUI.DrawElementStack<AnonymousStackElement>(val2, 24f, tmpStackElements, (StackElementDrawer<AnonymousStackElement>)delegate(Rect r, AnonymousStackElement obj)
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					obj.drawer(r);
				}, (StackElementWidthGetter<AnonymousStackElement>)((AnonymousStackElement obj) => obj.width), 4f, 5f, false);
				((Rect)(ref val)).height = ((Rect)(ref val3)).height + 20f;
				if ((int)Event.current.type == 8)
				{
					layoutRewardsRects.Add(val);
				}
				curY += ((Rect)(ref val)).height;
			}
		}
		else
		{
			QuestPart_Choice choice = null;
			List<QuestPart> partsListForReading = selected.Quest.PartsListForReading;
			for (int j = 0; j < partsListForReading.Count; j++)
			{
				ref QuestPart_Choice reference = ref choice;
				QuestPart obj2 = partsListForReading[j];
				reference = (QuestPart_Choice)(object)((obj2 is QuestPart_Choice) ? obj2 : null);
				if (choice != null)
				{
					break;
				}
			}
			if (choice == null)
			{
				return;
			}
			Rect val4 = default(Rect);
			Rect val6 = default(Rect);
			for (int k = 0; k < choice.choices.Count; k++)
			{
				tmpStackElements.Clear();
				float num2 = 0f;
				for (int l = 0; l < choice.choices[k].rewards.Count; l++)
				{
					tmpStackElements.AddRange(choice.choices[k].rewards[l].StackElements);
					num2 += choice.choices[k].rewards[l].TotalMarketValue;
				}
				if (!GenCollection.Any<AnonymousStackElement>(tmpStackElements))
				{
					continue;
				}
				if (num2 > 0f)
				{
					TaggedString totalValueStr2 = TranslatorFormattedStringExtensions.Translate("TotalValue", NamedArgument.op_Implicit(GenText.ToStringMoney(num2, "F0")));
					tmpStackElements.Add(new AnonymousStackElement
					{
						drawer = delegate(Rect r)
						{
							//IL_000f: Unknown result type (might be due to invalid IL or missing references)
							//IL_0041: Unknown result type (might be due to invalid IL or missing references)
							//IL_0047: Unknown result type (might be due to invalid IL or missing references)
							//IL_0051: Unknown result type (might be due to invalid IL or missing references)
							GUI.color = new Color(0.7f, 0.7f, 0.7f);
							Widgets.Label(new Rect(((Rect)(ref r)).x + 5f, ((Rect)(ref r)).y, ((Rect)(ref r)).width - 10f, ((Rect)(ref r)).height), totalValueStr2);
							GUI.color = Color.white;
						},
						width = Text.CalcSize(TaggedString.op_Implicit(totalValueStr2)).x + 10f
					});
				}
				if (flag2)
				{
					curY += 17f;
					flag2 = false;
				}
				else
				{
					curY += 10f;
				}
				((Rect)(ref val4))._002Ector(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 10000f);
				Rect val5 = GenUI.ContractedBy(val4, 10f);
				if (flag)
				{
					((Rect)(ref val5)).xMin = ((Rect)(ref val5)).xMin + 100f;
				}
				if (k < layoutRewardsRects.Count)
				{
					Widgets.DrawBoxSolid(layoutRewardsRects[k], new Color(0.13f, 0.13f, 0.13f));
					GUI.color = new Color(1f, 1f, 1f, 0.3f);
					Widgets.DrawHighlightIfMouseover(layoutRewardsRects[k]);
					GUI.color = Color.white;
				}
				val3 = GenUI.DrawElementStack<AnonymousStackElement>(val5, 24f, tmpStackElements, (StackElementDrawer<AnonymousStackElement>)delegate(Rect r, AnonymousStackElement obj)
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					obj.drawer(r);
				}, (StackElementWidthGetter<AnonymousStackElement>)((AnonymousStackElement obj) => obj.width), 4f, 5f, false);
				((Rect)(ref val4)).height = ((Rect)(ref val3)).height + 20f;
				if ((int)Event.current.type == 8)
				{
					layoutRewardsRects.Add(val4);
				}
				if (flag)
				{
					if (!AcceptanceReport.op_Implicit(QuestUtility.CanAcceptQuest(selected.Quest)))
					{
						GUI.color = Color.grey;
					}
					((Rect)(ref val6))._002Ector(((Rect)(ref val4)).x, ((Rect)(ref val4)).y, 100f, ((Rect)(ref val4)).height);
					if (Widgets.ButtonText(val6, TaggedString.op_Implicit(Translator.Translate("AcceptQuestFor") + ":"), true, true, true, (TextAnchor?)null))
					{
						tmpRemainingQuestParts.Clear();
						tmpRemainingQuestParts.AddRange(selected.Quest.PartsListForReading);
						for (int m = 0; m < choice.choices.Count; m++)
						{
							if (k == m)
							{
								continue;
							}
							for (int n = 0; n < choice.choices[m].questParts.Count; n++)
							{
								QuestPart item = choice.choices[m].questParts[n];
								if (!choice.choices[k].questParts.Contains(item))
								{
									tmpRemainingQuestParts.Remove(item);
								}
							}
						}
						bool requiresAccepter = false;
						for (int num3 = 0; num3 < tmpRemainingQuestParts.Count; num3++)
						{
							if (tmpRemainingQuestParts[num3].RequiresAccepter)
							{
								requiresAccepter = true;
								break;
							}
						}
						tmpRemainingQuestParts.Clear();
						Choice localChoice = choice.choices[k];
						AcceptQuestByInterface(delegate
						{
							choice.Choose(localChoice);
						}, requiresAccepter);
					}
					TooltipHandler.TipRegionByKey(val6, "AcceptQuestForTip");
					GUI.color = Color.white;
				}
				curY += ((Rect)(ref val4)).height;
				break;
			}
		}
		if ((int)Event.current.type == 7)
		{
			layoutRewardsRects.Clear();
		}
		tmpStackElements.Clear();
	}

	private void DoLookTargets(Rect innerRect, ref float curY)
	{
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Unknown result type (might be due to invalid IL or missing references)
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		List<Map> maps = Find.Maps;
		int num = 0;
		for (int i = 0; i < maps.Count; i++)
		{
			if (maps[i].IsPlayerHome)
			{
				num++;
			}
		}
		tmpLookTargets.Clear();
		tmpLookTargets.AddRange(selected.Quest.QuestLookTargets);
		GenCollection.SortBy<GlobalTargetInfo, int, string>(tmpLookTargets, (Func<GlobalTargetInfo, int>)delegate(GlobalTargetInfo x)
		{
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			if (((GlobalTargetInfo)(ref x)).Thing is Pawn)
			{
				return 0;
			}
			if (((GlobalTargetInfo)(ref x)).HasThing)
			{
				return 1;
			}
			if (!((GlobalTargetInfo)(ref x)).IsWorldTarget)
			{
				return 2;
			}
			return (((GlobalTargetInfo)(ref x)).WorldObject is Settlement && ((WorldObject)(Settlement)((GlobalTargetInfo)(ref x)).WorldObject).Faction == Faction.OfPlayer) ? 4 : 3;
		}, (Func<GlobalTargetInfo, string>)((GlobalTargetInfo x) => ((GlobalTargetInfo)(ref x)).Label));
		bool flag = false;
		for (int j = 0; j < tmpLookTargets.Count; j++)
		{
			GlobalTargetInfo val = tmpLookTargets[j];
			if (((GlobalTargetInfo)(ref val)).HasWorldObject)
			{
				WorldObject worldObject = ((GlobalTargetInfo)(ref val)).WorldObject;
				MapParent val2 = (MapParent)(object)((worldObject is MapParent) ? worldObject : null);
				if (val2 != null && (!val2.HasMap || !val2.Map.IsPlayerHome))
				{
					flag = true;
					break;
				}
			}
		}
		bool flag2 = false;
		for (int k = 0; k < tmpLookTargets.Count; k++)
		{
			GlobalTargetInfo val3 = tmpLookTargets[k];
			if (CameraJumper.CanJump(val3) && (num != 1 || !(val3 == GlobalTargetInfo.op_Implicit((WorldObject)(object)Find.AnyPlayerHomeMap.Parent)) || flag))
			{
				if (!flag2)
				{
					flag2 = true;
					curY += 17f;
				}
				if (Widgets.ButtonText(new Rect(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 25f), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("JumpToTargetCustom", NamedArgument.op_Implicit(((GlobalTargetInfo)(ref val3)).Label))), false, true, true, (TextAnchor?)null))
				{
					CameraJumper.TryJumpAndSelect(val3, (MovementMode)0);
					Find.MainTabsRoot.EscapeCurrentTab(true);
				}
				curY += 25f;
			}
		}
	}

	private void DoSelectTargets(Rect innerRect, ref float curY)
	{
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		bool flag = false;
		for (int i = 0; i < selected.Quest.PartsListForReading.Count; i++)
		{
			QuestPart val = selected.Quest.PartsListForReading[i];
			tmpSelectTargets.Clear();
			tmpSelectTargets.AddRange(val.QuestSelectTargets);
			if (tmpSelectTargets.Count == 0)
			{
				continue;
			}
			if (!flag)
			{
				flag = true;
				curY += 4f;
			}
			if (Widgets.ButtonText(new Rect(((Rect)(ref innerRect)).x, curY, ((Rect)(ref innerRect)).width, 25f), val.QuestSelectTargetsLabel, false, true, true, (TextAnchor?)null))
			{
				Map val2 = null;
				int num = 0;
				Vector3 val3 = Vector3.zero;
				Find.Selector.ClearSelection();
				for (int j = 0; j < tmpSelectTargets.Count; j++)
				{
					GlobalTargetInfo val4 = tmpSelectTargets[j];
					if (CameraJumper.CanJump(val4) && ((GlobalTargetInfo)(ref val4)).HasThing)
					{
						Find.Selector.Select((object)((GlobalTargetInfo)(ref val4)).Thing, true, true);
						if (val2 == null)
						{
							val2 = ((GlobalTargetInfo)(ref val4)).Map;
						}
						else if (((GlobalTargetInfo)(ref val4)).Map != val2)
						{
							num = 0;
							break;
						}
						Vector3 val5 = val3;
						IntVec3 cell = ((GlobalTargetInfo)(ref val4)).Cell;
						val3 = val5 + ((IntVec3)(ref cell)).ToVector3();
						num++;
					}
				}
				if (num > 0)
				{
					CameraJumper.TryJump(new IntVec3(val3 / (float)num), val2, (MovementMode)0);
				}
				Find.MainTabsRoot.EscapeCurrentTab(true);
			}
			curY += 25f;
		}
	}

	private void DoFactionInfo(Rect rect, ref float curY)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		curY += 15f;
		foreach (Faction involvedFaction in selected.Quest.InvolvedFactions)
		{
			if (involvedFaction != null && !involvedFaction.Hidden && !involvedFaction.IsPlayer)
			{
				FactionUIUtility.DrawRelatedFactionInfo(rect, involvedFaction, ref curY);
			}
		}
	}

	private void DoDefHyperlinks(Rect rect, ref float curY)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		curY += 25f;
		foreach (Hyperlink hyperlink in selected.Quest.Hyperlinks)
		{
			Hyperlink current = hyperlink;
			float num = Text.CalcHeight(((Hyperlink)(ref current)).Label, ((Rect)(ref rect)).width);
			Widgets.HyperlinkWithIcon(new Rect(((Rect)(ref rect)).x, curY, ((Rect)(ref rect)).width / 2f, num), current, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ViewHyperlink", NamedArgument.op_Implicit(((Hyperlink)(ref current)).Label))), 2f, 6f, (Color?)null, false, (string)null);
			curY += num;
		}
	}

	private void AcceptQuestByInterface(Action preAcceptAction = null, bool requiresAccepter = false)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Expected O, but got Unknown
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Expected O, but got Unknown
		if (AcceptanceReport.op_Implicit(QuestUtility.CanAcceptQuest(selected.Quest)))
		{
			if (requiresAccepter)
			{
				List<FloatMenuOption> list = new List<FloatMenuOption>();
				foreach (Pawn p in PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_FreeColonists_NoCryptosleep)
				{
					if (!QuestUtility.CanPawnAcceptQuest(p, selected.Quest))
					{
						continue;
					}
					Pawn pLocal = p;
					string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("AcceptWith", NamedArgument.op_Implicit((Thing)(object)p)));
					if (p.royalty != null && GenCollection.Any<RoyalTitle>(p.royalty.AllTitlesInEffectForReading))
					{
						text = text + " (" + p.royalty.MostSeniorTitle.def.GetLabelFor(pLocal) + ")";
					}
					list.Add(new FloatMenuOption(text, (Action)delegate
					{
						//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
						//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
						//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
						//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
						//IL_00df: Unknown result type (might be due to invalid IL or missing references)
						//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
						//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
						//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
						//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
						//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
						//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
						//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
						//IL_0147: Unknown result type (might be due to invalid IL or missing references)
						//IL_014c: Unknown result type (might be due to invalid IL or missing references)
						//IL_010a: Unknown result type (might be due to invalid IL or missing references)
						//IL_010c: Unknown result type (might be due to invalid IL or missing references)
						//IL_0198: Unknown result type (might be due to invalid IL or missing references)
						//IL_019a: Unknown result type (might be due to invalid IL or missing references)
						//IL_019c: Unknown result type (might be due to invalid IL or missing references)
						//IL_01a1: Unknown result type (might be due to invalid IL or missing references)
						//IL_0157: Unknown result type (might be due to invalid IL or missing references)
						//IL_0159: Unknown result type (might be due to invalid IL or missing references)
						//IL_013a: Unknown result type (might be due to invalid IL or missing references)
						//IL_013f: Unknown result type (might be due to invalid IL or missing references)
						//IL_0144: Unknown result type (might be due to invalid IL or missing references)
						//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
						//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
						//IL_01af: Unknown result type (might be due to invalid IL or missing references)
						//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
						//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
						//IL_0187: Unknown result type (might be due to invalid IL or missing references)
						//IL_018c: Unknown result type (might be due to invalid IL or missing references)
						//IL_0191: Unknown result type (might be due to invalid IL or missing references)
						//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
						//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
						//IL_01c8: Unknown result type (might be due to invalid IL or missing references)
						//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
						//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
						//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
						//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
						//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
						//IL_0203: Unknown result type (might be due to invalid IL or missing references)
						//IL_0208: Unknown result type (might be due to invalid IL or missing references)
						//IL_020f: Unknown result type (might be due to invalid IL or missing references)
						//IL_0216: Unknown result type (might be due to invalid IL or missing references)
						//IL_0231: Unknown result type (might be due to invalid IL or missing references)
						//IL_0241: Unknown result type (might be due to invalid IL or missing references)
						//IL_024b: Expected O, but got Unknown
						//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
						//IL_01df: Unknown result type (might be due to invalid IL or missing references)
						//IL_01e1: Unknown result type (might be due to invalid IL or missing references)
						//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
						//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
						if (QuestUtility.CanPawnAcceptQuest(pLocal, selected.Quest))
						{
							QuestPart_GiveRoyalFavor val = selected.Quest.PartsListForReading.OfType<QuestPart_GiveRoyalFavor>().FirstOrDefault();
							if (val != null && val.giveToAccepter)
							{
								IEnumerable<Trait> conceitedTraits = RoyalTitleUtility.GetConceitedTraits(p);
								IEnumerable<Trait> traitsAffectingPsylinkNegatively = RoyalTitleUtility.GetTraitsAffectingPsylinkNegatively(p);
								bool totallyDisabled = p.skills.GetSkill(SkillDefOf.Social).TotallyDisabled;
								bool flag = conceitedTraits.Any();
								bool flag2 = !p.HasPsylink && traitsAffectingPsylinkNegatively.Any();
								if (totallyDisabled || flag || flag2)
								{
									NamedArgument val2 = NamedArgumentUtility.Named((object)p, "PAWN");
									NamedArgument val3 = NamedArgumentUtility.Named((object)val.faction, "FACTION");
									TaggedString val4 = TaggedString.op_Implicit((string)null);
									if (totallyDisabled)
									{
										val4 = TranslatorFormattedStringExtensions.Translate("RoyalIncapableOfSocial", val2, val3);
									}
									TaggedString val5 = TaggedString.op_Implicit((string)null);
									if (flag)
									{
										val5 = TranslatorFormattedStringExtensions.Translate("RoyalWithConceitedTrait", val2, val3, NamedArgument.op_Implicit(GenText.ToCommaList(conceitedTraits.Select((Trait t) => t.Label), true, false)));
									}
									TaggedString val6 = TaggedString.op_Implicit((string)null);
									if (flag2)
									{
										val6 = TranslatorFormattedStringExtensions.Translate("RoyalWithTraitAffectingPsylinkNegatively", val2, val3, NamedArgument.op_Implicit(GenText.ToCommaList(traitsAffectingPsylinkNegatively.Select((Trait t) => t.Label), true, false)));
									}
									TaggedString val7 = TranslatorFormattedStringExtensions.Translate("QuestGivesRoyalFavor", val2, val3);
									if (totallyDisabled)
									{
										val7 += "\n\n" + val4;
									}
									if (flag)
									{
										val7 += "\n\n" + val5;
									}
									if (flag2)
									{
										val7 += "\n\n" + val6;
									}
									val7 += "\n\n" + Translator.Translate("WantToContinue");
									Find.WindowStack.Add((Window)new Dialog_MessageBox(val7, TaggedString.op_Implicit(Translator.Translate("Confirm")), (Action)AcceptAction, TaggedString.op_Implicit(Translator.Translate("GoBack")), (Action)null, (string)null, false, (Action)null, (Action)null, (WindowLayer)1));
								}
								else
								{
									AcceptAction();
								}
							}
							else
							{
								AcceptAction();
							}
						}
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					void AcceptAction()
					{
						//IL_0033: Unknown result type (might be due to invalid IL or missing references)
						//IL_0052: Unknown result type (might be due to invalid IL or missing references)
						//IL_0057: Unknown result type (might be due to invalid IL or missing references)
						SoundStarter.PlayOneShotOnCamera(SoundDefOf.Quest_Accepted, (Map)null);
						if (preAcceptAction != null)
						{
							preAcceptAction();
						}
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageQuestAccepted", NamedArgument.op_Implicit((Thing)(object)pLocal), NamedArgument.op_Implicit(selected.Quest.name))), LookTargets.op_Implicit((Thing)(object)pLocal), MessageTypeDefOf.TaskCompletion, false);
						questGiverManager.ActivateQuest(pLocal, selected);
						selected = null;
					}
				}
				if (list.Count > 0)
				{
					Find.WindowStack.Add((Window)new FloatMenu(list));
				}
				else
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageNoColonistCanAcceptQuest", NamedArgument.op_Implicit(Faction.OfPlayer.def.pawnsPlural))), MessageTypeDefOf.RejectInput, false);
				}
			}
			else
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Quest_Accepted, (Map)null);
				if (preAcceptAction != null)
				{
					preAcceptAction();
				}
				questGiverManager.ActivateQuest(null, selected);
				selected = null;
			}
		}
		else
		{
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCannotAcceptQuest")), MessageTypeDefOf.RejectInput, false);
		}
	}
}
