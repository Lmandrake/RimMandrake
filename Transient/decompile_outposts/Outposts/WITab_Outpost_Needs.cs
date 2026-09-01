using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace Outposts;

public class WITab_Outpost_Needs : WITab
{
	private static readonly List<Need> needsToDisplay = new List<Need>();

	private static readonly List<Thought> thoughtGroupsPresent = new List<Thought>();

	private static readonly List<Thought> thoughtGroup = new List<Thought>();

	private bool doNeeds;

	private Vector2 scrollPosition;

	private float scrollViewHeight;

	private Pawn specificNeedsTabForPawn;

	private Vector2 thoughtScrollPosition;

	public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

	private float SpecificNeedsTabWidth
	{
		get
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			if (!ThingUtility.DestroyedOrNull((Thing)(object)specificNeedsTabForPawn))
			{
				return NeedsCardUtility.GetSize(specificNeedsTabForPawn).x;
			}
			return 0f;
		}
	}

	private List<Pawn> Pawns => SelOutpost.AllPawns.ToList();

	public WITab_Outpost_Needs()
	{
		((InspectTabBase)this).labelKey = "TabCaravanNeeds";
	}

	public override void Notify_ClearingAllMapsMemory()
	{
		((InspectTabBase)this).Notify_ClearingAllMapsMemory();
		specificNeedsTabForPawn = null;
	}

	public override void UpdateSize()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		EnsureSpecificNeedsTabForPawnValid();
		((InspectTabBase)this).UpdateSize();
		((InspectTabBase)this).size = CaravanNeedsTabUtility.GetSize(Pawns, ((InspectTabBase)this).PaneTopY, true);
		if (((InspectTabBase)this).size.x + SpecificNeedsTabWidth > (float)UI.screenWidth)
		{
			doNeeds = false;
			((InspectTabBase)this).size = CaravanNeedsTabUtility.GetSize(Pawns, ((InspectTabBase)this).PaneTopY, false);
		}
		else
		{
			doNeeds = true;
		}
		((InspectTabBase)this).size.y = Mathf.Max(((InspectTabBase)this).size.y, NeedsCardUtility.FullSize.y);
	}

	public override void ExtraOnGUI()
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		EnsureSpecificNeedsTabForPawnValid();
		((InspectTabBase)this).ExtraOnGUI();
		Pawn localSpecificNeedsTabForPawn = specificNeedsTabForPawn;
		if (localSpecificNeedsTabForPawn == null)
		{
			return;
		}
		Rect tabRect = ((InspectTabBase)this).TabRect;
		float specificNeedsTabWidth = SpecificNeedsTabWidth;
		Rect rect = new Rect(((Rect)(ref tabRect)).xMax - 1f, ((Rect)(ref tabRect)).yMin, specificNeedsTabWidth, ((Rect)(ref tabRect)).height);
		Find.WindowStack.ImmediateWindow(1439870015, rect, (WindowLayer)0, (Action)delegate
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			if (!ThingUtility.DestroyedOrNull((Thing)(object)localSpecificNeedsTabForPawn))
			{
				NeedsCardUtility.DoNeedsMoodAndThoughts(GenUI.AtZero(rect), localSpecificNeedsTabForPawn, ref thoughtScrollPosition);
				if (Widgets.CloseButtonFor(GenUI.AtZero(rect)))
				{
					specificNeedsTabForPawn = null;
					SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabClose, (Map)null);
				}
			}
		}, true, false, 1f, (Action)null, false);
	}

	private void EnsureSpecificNeedsTabForPawnValid()
	{
		if (specificNeedsTabForPawn != null && (((Thing)specificNeedsTabForPawn).Destroyed || !SelOutpost.Has(specificNeedsTabForPawn)))
		{
			specificNeedsTabForPawn = null;
		}
	}

	public override void FillTab()
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		EnsureSpecificNeedsTabForPawnValid();
		DoRows(((InspectTabBase)this).size, Pawns);
	}

	private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn pawn)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		float num = scrollPosition.y - 40f;
		float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
		if (curY > num && curY < num2)
		{
			DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), pawn);
		}
		curY += 40f;
	}

	private void DoRows(Vector2 size, List<Pawn> pawns)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Invalid comparison between Unknown and I4
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		if (specificNeedsTabForPawn != null && (!pawns.Contains(specificNeedsTabForPawn) || specificNeedsTabForPawn.Dead))
		{
			specificNeedsTabForPawn = null;
		}
		Text.Font = (GameFont)1;
		Rect val = GenUI.ContractedBy(new Rect(0f, 0f, size.x, size.y), 10f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		float curY = 0f;
		bool flag = false;
		for (int i = 0; i < pawns.Count; i++)
		{
			Pawn val3 = pawns[i];
			if (val3.IsColonist)
			{
				if (!flag)
				{
					Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
					flag = true;
				}
				DoRow(ref curY, val2, val, val3);
			}
		}
		bool flag2 = false;
		for (int j = 0; j < pawns.Count; j++)
		{
			Pawn val4 = pawns[j];
			if (!val4.IsColonist)
			{
				if (!flag2)
				{
					Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisonersAndAnimals")));
					flag2 = true;
				}
				DoRow(ref curY, val2, val, val4);
			}
		}
		if ((int)Event.current.type == 8)
		{
			scrollViewHeight = curY + 30f;
		}
		Widgets.EndScrollView();
	}

	private static void GetNeedsToDisplay(Pawn p)
	{
		needsToDisplay.Clear();
		List<Need> allNeeds = p.needs.AllNeeds;
		for (int i = 0; i < allNeeds.Count; i++)
		{
			Need val = allNeeds[i];
			if (val.def.showForCaravanMembers)
			{
				needsToDisplay.Add(val);
			}
		}
		PawnNeedsUIUtility.SortInDisplayOrder(needsToDisplay);
	}

	private void DoRow(Rect rect, Pawn pawn)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_0249: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(rect);
		Rect val = GenUI.AtZero(rect);
		Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)pawn);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		if (!pawn.Dead)
		{
			CaravanThingsTabUtility.DoOpenSpecificTabButton(val, pawn, ref specificNeedsTabForPawn);
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
			CaravanThingsTabUtility.DoOpenSpecificTabButtonInvisible(val, pawn, ref specificNeedsTabForPawn);
		}
		Widgets.DrawHighlightIfMouseover(val);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
		Widgets.ThingIcon(val2, (Thing)(object)pawn, 1f, (Rot4?)null, false, 1f, false);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
		GenMapUI.DrawPawnLabel(pawn, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
		if (doNeeds)
		{
			GetNeedsToDisplay(pawn);
			float xMax = ((Rect)(ref val3)).xMax;
			Rect val5 = default(Rect);
			for (int i = 0; i < needsToDisplay.Count; i++)
			{
				Need val4 = needsToDisplay[i];
				int num = 0;
				bool flag = true;
				((Rect)(ref val5))._002Ector(xMax, 0f, 100f, 40f);
				Need_Mood mood = (Need_Mood)(object)((val4 is Need_Mood) ? val4 : null);
				if (mood != null)
				{
					num = 1;
					flag = false;
					if (Mouse.IsOver(val5))
					{
						TooltipHandler.TipRegion(val5, new TipSignal((Func<string>)(() => CustomMoodNeedTooltip(mood)), ((object)(Rect)(ref val5)/*cast due to .constrained prefix*/).GetHashCode()));
					}
				}
				Rect val6 = val5;
				((Rect)(ref val6)).yMin = ((Rect)(ref val6)).yMin - 5f;
				((Rect)(ref val6)).yMax = ((Rect)(ref val6)).yMax + 5f;
				val4.DrawOnGUI(val6, num, 10f, false, flag, (Rect?)val5, true);
				xMax = ((Rect)(ref val5)).xMax;
			}
		}
		if (pawn.Downed)
		{
			GUI.color = new Color(1f, 0f, 0f, 0.5f);
			Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
			GUI.color = Color.white;
		}
		GUI.EndGroup();
	}

	private static string CustomMoodNeedTooltip(Need_Mood mood)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(((Need)mood).GetTipString());
		PawnNeedsUIUtility.GetThoughtGroupsInDisplayOrder(mood, thoughtGroupsPresent);
		bool flag = false;
		for (int i = 0; i < thoughtGroupsPresent.Count; i++)
		{
			Thought val = thoughtGroupsPresent[i];
			mood.thoughts.GetMoodThoughts(val, thoughtGroup);
			Thought leadingThoughtInGroup = PawnNeedsUIUtility.GetLeadingThoughtInGroup(thoughtGroup);
			if (leadingThoughtInGroup.VisibleInNeedsTab)
			{
				if (!flag)
				{
					flag = true;
					stringBuilder.AppendLine();
				}
				stringBuilder.Append(leadingThoughtInGroup.LabelCap);
				if (thoughtGroup.Count > 1)
				{
					stringBuilder.Append(" x");
					stringBuilder.Append(thoughtGroup.Count);
				}
				stringBuilder.Append(": ");
				stringBuilder.AppendLine(mood.thoughts.MoodOffsetOfGroup(val).ToString("##0"));
			}
		}
		return stringBuilder.ToString();
	}
}
