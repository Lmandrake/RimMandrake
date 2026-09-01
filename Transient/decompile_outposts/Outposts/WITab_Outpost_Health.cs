using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace Outposts;

[StaticConstructorOnStartup]
public class WITab_Outpost_Health : WITab
{
	private static readonly List<PawnCapacityDef> capacitiesToDisplay = new List<PawnCapacityDef>();

	private bool compactMode;

	private Vector2 scrollPosition;

	private float scrollViewHeight;

	private Pawn specificHealthTabForPawn;

	public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

	private List<Pawn> Pawns => SelOutpost.AllPawns.Where((Pawn p) => p.apparel != null && p.equipment != null && p.health != null && p.guest != null).ToList();

	private float SpecificHealthTabWidth
	{
		get
		{
			EnsureSpecificHealthTabForPawnValid();
			if (ThingUtility.DestroyedOrNull((Thing)(object)specificHealthTabForPawn))
			{
				return 0f;
			}
			return 630f;
		}
	}

	private static List<PawnCapacityDef> CapacitiesToDisplay
	{
		get
		{
			capacitiesToDisplay.Clear();
			List<PawnCapacityDef> allDefsListForReading = DefDatabase<PawnCapacityDef>.AllDefsListForReading;
			for (int i = 0; i < allDefsListForReading.Count; i++)
			{
				if (allDefsListForReading[i].showOnCaravanHealthTab)
				{
					capacitiesToDisplay.Add(allDefsListForReading[i]);
				}
			}
			GenCollection.SortBy<PawnCapacityDef, int>(capacitiesToDisplay, (Func<PawnCapacityDef, int>)((PawnCapacityDef x) => x.listOrder));
			return capacitiesToDisplay;
		}
	}

	public WITab_Outpost_Health()
	{
		((InspectTabBase)this).labelKey = "TabCaravanHealth";
	}

	public override void FillTab()
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Invalid comparison between Unknown and I4
		EnsureSpecificHealthTabForPawnValid();
		Text.Font = (GameFont)1;
		Rect val = GenUI.ContractedBy(new Rect(0f, 0f, ((InspectTabBase)this).size.x, ((InspectTabBase)this).size.y), 10f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
		float curY = 0f;
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		DoColumnHeaders(ref curY);
		DoRows(ref curY, val2, val);
		if ((int)Event.current.type == 8)
		{
			scrollViewHeight = curY + 30f;
		}
		Widgets.EndScrollView();
	}

	public override void UpdateSize()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		EnsureSpecificHealthTabForPawnValid();
		((InspectTabBase)this).UpdateSize();
		((InspectTabBase)this).size = GetRawSize(compactMode: false);
		if (((InspectTabBase)this).size.x + SpecificHealthTabWidth > (float)UI.screenWidth)
		{
			compactMode = true;
			((InspectTabBase)this).size = GetRawSize(compactMode: true);
		}
		else
		{
			compactMode = false;
		}
	}

	public override void ExtraOnGUI()
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		EnsureSpecificHealthTabForPawnValid();
		((InspectTabBase)this).ExtraOnGUI();
		Pawn localSpecificHealthTabForPawn = specificHealthTabForPawn;
		if (localSpecificHealthTabForPawn == null)
		{
			return;
		}
		Rect tabRect = ((InspectTabBase)this).TabRect;
		float specificHealthTabWidth = SpecificHealthTabWidth;
		Rect rect = new Rect(((Rect)(ref tabRect)).xMax - 1f, ((Rect)(ref tabRect)).yMin, specificHealthTabWidth, ((Rect)(ref tabRect)).height);
		Find.WindowStack.ImmediateWindow(1439870015, rect, (WindowLayer)0, (Action)delegate
		{
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			if (!ThingUtility.DestroyedOrNull((Thing)(object)localSpecificHealthTabForPawn))
			{
				HealthCardUtility.DrawPawnHealthCard(new Rect(0f, 20f, ((Rect)(ref rect)).width, ((Rect)(ref rect)).height - 20f), localSpecificHealthTabForPawn, false, true, (Thing)(object)localSpecificHealthTabForPawn);
				if (Widgets.CloseButtonFor(GenUI.AtZero(rect)))
				{
					specificHealthTabForPawn = null;
					SoundStarter.PlayOneShotOnCamera(SoundDefOf.TabClose, (Map)null);
				}
			}
		}, true, false, 1f, (Action)null, false);
	}

	private void DoColumnHeaders(ref float curY)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		if (!compactMode)
		{
			float num = 135f;
			Text.Anchor = (TextAnchor)1;
			GUI.color = Widgets.SeparatorLabelColor;
			Widgets.Label(new Rect(num, 3f, 100f, 100f), Translator.Translate("Pain"));
			num += 100f;
			List<PawnCapacityDef> list = CapacitiesToDisplay;
			for (int i = 0; i < list.Count; i++)
			{
				Widgets.Label(new Rect(num, 3f, 100f, 100f), GenText.Truncate(((Def)list[i]).LabelCap, 100f, (Dictionary<string, TaggedString>)null));
				num += 100f;
			}
			Text.Anchor = (TextAnchor)0;
			GUI.color = Color.white;
		}
	}

	private void DoRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		List<Pawn> pawns = Pawns;
		if (specificHealthTabForPawn != null && !pawns.Contains(specificHealthTabForPawn))
		{
			specificHealthTabForPawn = null;
		}
		bool flag = false;
		for (int i = 0; i < pawns.Count; i++)
		{
			Pawn val = pawns[i];
			if (val.IsColonist)
			{
				if (!flag)
				{
					Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
					flag = true;
				}
				DoRow(ref curY, scrollViewRect, scrollOutRect, val);
			}
		}
		bool flag2 = false;
		for (int j = 0; j < pawns.Count; j++)
		{
			Pawn val2 = pawns[j];
			if (!val2.IsColonist)
			{
				if (!flag2)
				{
					Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisonersAndAnimals")));
					flag2 = true;
				}
				DoRow(ref curY, scrollViewRect, scrollOutRect, val2);
			}
		}
	}

	private Vector2 GetRawSize(bool compactMode)
	{
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		float num = 100f;
		if (!compactMode)
		{
			num += 100f;
			num += (float)CapacitiesToDisplay.Count * 100f;
			num += 40f;
		}
		Vector2 result = default(Vector2);
		result.x = 127f + num + 16f;
		result.y = Mathf.Min(550f, ((InspectTabBase)this).PaneTopY - 30f);
		return result;
	}

	private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn p)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		float num = scrollPosition.y - 40f;
		float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
		if (curY > num && curY < num2)
		{
			DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), p);
		}
		curY += 40f;
	}

	private void DoRow(Rect rect, Pawn p)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_022e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0256: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(rect);
		Rect val = GenUI.AtZero(rect);
		Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)p);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		CaravanThingsTabUtility.DoOpenSpecificTabButton(val, p, ref specificHealthTabForPawn);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		CaravanThingsTabUtility.DoOpenSpecificTabButtonInvisible(val, p, ref specificHealthTabForPawn);
		if (Mouse.IsOver(val))
		{
			Widgets.DrawHighlight(val);
		}
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
		Widgets.ThingIcon(val2, (Thing)(object)p, 1f, (Rot4?)null, false, 1f, false);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
		GenMapUI.DrawPawnLabel(p, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
		float xMax = ((Rect)(ref val3)).xMax;
		if (!compactMode)
		{
			if (p.RaceProps.IsFlesh)
			{
				DoPain(new Rect(xMax, 0f, 100f, 40f), p);
			}
			xMax += 100f;
			List<PawnCapacityDef> list = CapacitiesToDisplay;
			Rect rect2 = default(Rect);
			for (int i = 0; i < list.Count; i++)
			{
				((Rect)(ref rect2))._002Ector(xMax, 0f, 100f, 40f);
				if ((p.RaceProps.Humanlike && !list[i].showOnHumanlikes) || (p.RaceProps.Animal && !list[i].showOnAnimals) || (p.RaceProps.IsMechanoid && !list[i].showOnMechanoids) || !PawnCapacityUtility.BodyCanEverDoCapacity(p.RaceProps.body, list[i]))
				{
					xMax += 100f;
					continue;
				}
				DoCapacity(rect2, p, list[i]);
				xMax += 100f;
			}
		}
		if (p.Downed)
		{
			GUI.color = new Color(1f, 0f, 0f, 0.5f);
			Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
			GUI.color = Color.white;
		}
		GUI.EndGroup();
	}

	private static void DoPain(Rect rect, Pawn pawn)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		Pair<string, Color> painLabel = HealthCardUtility.GetPainLabel(pawn);
		if (Mouse.IsOver(rect))
		{
			Widgets.DrawHighlight(rect);
		}
		GUI.color = painLabel.Second;
		Text.Anchor = (TextAnchor)4;
		Widgets.Label(rect, painLabel.First);
		GUI.color = Color.white;
		Text.Anchor = (TextAnchor)0;
		if (Mouse.IsOver(rect))
		{
			string painTip = HealthCardUtility.GetPainTip(pawn);
			TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(painTip));
		}
	}

	private static void DoCapacity(Rect rect, Pawn pawn, PawnCapacityDef capacity)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		Pair<string, Color> efficiencyLabel = HealthCardUtility.GetEfficiencyLabel(pawn, capacity);
		if (Mouse.IsOver(rect))
		{
			Widgets.DrawHighlight(rect);
		}
		GUI.color = efficiencyLabel.Second;
		Text.Anchor = (TextAnchor)4;
		Widgets.Label(rect, efficiencyLabel.First);
		GUI.color = Color.white;
		Text.Anchor = (TextAnchor)0;
		if (Mouse.IsOver(rect))
		{
			string pawnCapacityTip = HealthCardUtility.GetPawnCapacityTip(pawn, capacity);
			TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(pawnCapacityTip));
		}
	}

	public override void Notify_ClearingAllMapsMemory()
	{
		((InspectTabBase)this).Notify_ClearingAllMapsMemory();
		specificHealthTabForPawn = null;
	}

	private void EnsureSpecificHealthTabForPawnValid()
	{
		if (specificHealthTabForPawn != null && (((Thing)specificHealthTabForPawn).Destroyed || !SelOutpost.Has(specificHealthTabForPawn)))
		{
			specificHealthTabForPawn = null;
		}
	}
}
