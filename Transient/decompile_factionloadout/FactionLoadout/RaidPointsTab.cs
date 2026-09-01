using System.Collections.Generic;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class RaidPointsTab : EditTab
{
	public RaidPointsTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_RaidPoints")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Expected O, but got Unknown
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		//IL_020b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Unknown result type (might be due to invalid IL or missing references)
		//IL_024f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0230: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Expected O, but got Unknown
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Expected O, but got Unknown
		//IL_02bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c5: Expected O, but got Unknown
		float combatPower = DefaultKind.combatPower;
		ref float? combatPower2 = ref Current.CombatPower;
		TaggedString val = Translator.Translate("FactionLoadout_CombatPower");
		DrawOverride(ui, combatPower, ref combatPower2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawCombatPower, 32f, (PawnKindEdit e) => e.CombatPower);
		bool appearsRandomlyInCombatGroups = DefaultKind.appearsRandomlyInCombatGroups;
		ref bool? appearsRandomlyInCombatGroups2 = ref Current.AppearsRandomlyInCombatGroups;
		val = Translator.Translate("FactionLoadout_AppearsRandomlyInCombatGroups");
		DrawOverride(ui, appearsRandomlyInCombatGroups, ref appearsRandomlyInCombatGroups2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawAppearsRandomlyInCombatGroups, 32f, (PawnKindEdit e) => e.AppearsRandomlyInCombatGroups);
		if (!Current.IsGlobal)
		{
			return;
		}
		((Listing)ui).GapLine(12f);
		Widgets.Label(((Listing)ui).GetRect(120f, 1f), Translator.Translate("FactionLoadout_Desc_RaidPoints"));
		((Listing)ui).GapLine(12f);
		PawnKindEdit current = Current;
		if (current.RaidCommonalityFromPointsCurve == null)
		{
			current.RaidCommonalityFromPointsCurve = new SimpleCurve();
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
				SimpleCurve raidCommonalityFromPointsCurve = obj.raidCommonalityFromPointsCurve;
				obj2 = ((raidCommonalityFromPointsCurve != null) ? raidCommonalityFromPointsCurve.Points : null);
			}
			if (obj2 == null)
			{
				obj2 = new List<CurvePoint>();
			}
			current2.RaidCommonalityFromPointsCurve = new SimpleCurve((IEnumerable<CurvePoint>)obj2);
		}
		((Listing)ui).GapLine(12f);
		DrawCurve(ui, ref Current.RaidCommonalityFromPointsCurve, ref curvePointBuffers[curveIndex++]);
		((Listing)ui).GapLine(12f);
		Widgets.Label(((Listing)ui).GetRect(60f, 1f), Translator.Translate("FactionLoadout_Desc_MaxPawnCost"));
		((Listing)ui).GapLine(12f);
		current = Current;
		if (current.MaxPawnCostPerTotalPointsCurve == null)
		{
			current.MaxPawnCostPerTotalPointsCurve = new SimpleCurve();
		}
		if (Widgets.ButtonText(((Listing)ui).GetRect(30f, 1f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionDefault")), true, true, true, (TextAnchor?)null))
		{
			PawnKindEdit current3 = Current;
			FactionDef obj3 = FactionEdit.TryGetOriginal(Current.ParentEdit?.Faction?.DefName);
			object obj4;
			if (obj3 == null)
			{
				obj4 = null;
			}
			else
			{
				SimpleCurve maxPawnCostPerTotalPointsCurve = obj3.maxPawnCostPerTotalPointsCurve;
				obj4 = ((maxPawnCostPerTotalPointsCurve != null) ? maxPawnCostPerTotalPointsCurve.Points : null);
			}
			if (obj4 == null)
			{
				obj4 = new List<CurvePoint>();
			}
			current3.MaxPawnCostPerTotalPointsCurve = new SimpleCurve((IEnumerable<CurvePoint>)obj4);
		}
		((Listing)ui).GapLine(12f);
		DrawCurve(ui, ref Current.MaxPawnCostPerTotalPointsCurve, ref curvePointBuffers[curveIndex++]);
	}

	private void DrawCombatPower(Rect rect, bool active, float def)
	{
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			ref string reference = ref buffers[bufferIndex++];
			float valueOrDefault = Current.CombatPower.GetValueOrDefault(Current.Def.combatPower);
			if (reference == null)
			{
				reference = valueOrDefault.ToString("F0");
			}
			Widgets.TextFieldNumeric<float>(rect, ref valueOrDefault, ref reference, 0f, 1E+09f);
			Current.CombatPower = valueOrDefault;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {Current.Def.combatPower:F0}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawAppearsRandomlyInCombatGroups(Rect rect, bool active, bool def)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			bool valueOrDefault = Current.AppearsRandomlyInCombatGroups.GetValueOrDefault(Current.Def.appearsRandomlyInCombatGroups);
			Widgets.CheckboxLabeled(rect, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AppearsRandomly_Label")), ref valueOrDefault, false, (Texture2D)null, (Texture2D)null, true, false);
			Current.AppearsRandomlyInCombatGroups = valueOrDefault;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {Current.Def.appearsRandomlyInCombatGroups}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}
}
