using System.Collections.Generic;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class RaidLootTab : EditTab
{
	public RaidLootTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_RaidLoot")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Expected O, but got Unknown
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Expected O, but got Unknown
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Expected O, but got Unknown
		if (!Current.IsGlobal)
		{
			Widgets.Label(((Listing)ui).GetRect(30f, 1f), Translator.Translate("FactionLoadout_GlobalOnly"));
			return;
		}
		Widgets.Label(((Listing)ui).GetRect(120f, 1f), Translator.Translate("FactionLoadout_Desc_RaidLoot"));
		((Listing)ui).GapLine(12f);
		PawnKindEdit current = Current;
		if (current.RaidLootValueFromPointsCurve == null)
		{
			current.RaidLootValueFromPointsCurve = new SimpleCurve();
		}
		if (Widgets.ButtonText(((Listing)ui).GetRect(30f, 1f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionDefault")), true, true, true, (TextAnchor?)null))
		{
			PawnKindEdit current2 = Current;
			FactionDef obj = FactionEdit.TryGetOriginal(Current.ParentEdit?.Faction?.DefName);
			object obj2;
			if (obj == null)
			{
				obj2 = null;
			}
			else
			{
				SimpleCurve raidLootValueFromPointsCurve = obj.raidLootValueFromPointsCurve;
				obj2 = ((raidLootValueFromPointsCurve != null) ? raidLootValueFromPointsCurve.Points : null);
			}
			if (obj2 == null)
			{
				obj2 = new List<CurvePoint>();
			}
			current2.RaidLootValueFromPointsCurve = new SimpleCurve((IEnumerable<CurvePoint>)obj2);
		}
		current = Current;
		if (current.RaidLootValueFromPointsCurve == null)
		{
			current.RaidLootValueFromPointsCurve = new SimpleCurve();
		}
		((Listing)ui).GapLine(12f);
		DrawCurve(ui, ref Current.RaidLootValueFromPointsCurve, ref curvePointBuffers[curveIndex++]);
	}
}
