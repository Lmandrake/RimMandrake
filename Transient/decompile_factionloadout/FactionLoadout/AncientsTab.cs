using System.Collections.Generic;
using FactionLoadout.Modules;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class AncientsTab : EditTab
{
	private string numVFEAncientsPowersBuffer;

	private string numVFEAncientsWeaknessesBuffer;

	public AncientsTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_VFEAncients")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		if (VFEAncientsReflectionModule.ModLoaded.Value)
		{
			ref int? numVFEAncientsSuperPowers = ref Current.NumVFEAncientsSuperPowers;
			TaggedString val = Translator.Translate("FactionLoadout_Ancients_SuperPowers");
			DrawOverride(ui, 0, ref numVFEAncientsSuperPowers, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawNumVFEAncientsSuperPowers, 32f, (PawnKindEdit e) => e.NumVFEAncientsSuperPowers);
			ref int? numVFEAncientsSuperWeaknesses = ref Current.NumVFEAncientsSuperWeaknesses;
			val = Translator.Translate("FactionLoadout_Ancients_SuperWeaknesses");
			DrawOverride(ui, 0, ref numVFEAncientsSuperWeaknesses, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawNumVFEAncientsSuperWeaknesses, 32f, (PawnKindEdit e) => e.NumVFEAncientsSuperWeaknesses);
			List<string> defaultValue = new List<string>();
			ref List<string> forcedVFEAncientsItems = ref Current.ForcedVFEAncientsItems;
			val = Translator.Translate("FactionLoadout_Ancients_ForcedPowers");
			DrawOverride(ui, defaultValue, ref forcedVFEAncientsItems, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawVFEAncientsPowers, GetHeightFor(Current.ForcedVFEAncientsItems), cloneDefault: true, (PawnKindEdit e) => e.ForcedVFEAncientsItems);
		}
	}

	private void DrawNumVFEAncientsSuperPowers(Rect rect, bool active, int _)
	{
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		if (numVFEAncientsPowersBuffer == null && active)
		{
			numVFEAncientsPowersBuffer = Current.NumVFEAncientsSuperPowers?.ToString() ?? "";
		}
		if (active)
		{
			int value = Current.NumVFEAncientsSuperPowers ?? 0;
			Widgets.IntEntry(rect, ref value, ref numVFEAncientsPowersBuffer, 1);
			Current.NumVFEAncientsSuperPowers = value;
			return;
		}
		DefModExtension val = VFEAncientsReflectionModule.FindVEAncientsExtension(Current.Def);
		string text = "NA";
		if (val != null)
		{
			text = VFEAncientsReflectionModule.NumRandomSuperpowersField.Value?.GetValue(val)?.ToString();
		}
		string text2 = (Current.IsGlobal ? "---" : ("[Default] " + text));
		Widgets.Label(rect.GetCentered(text2), text2);
	}

	private void DrawNumVFEAncientsSuperWeaknesses(Rect rect, bool active, int _)
	{
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		if (numVFEAncientsWeaknessesBuffer == null && active)
		{
			numVFEAncientsWeaknessesBuffer = Current.NumVFEAncientsSuperWeaknesses?.ToString() ?? "";
		}
		if (active)
		{
			int value = Current.NumVFEAncientsSuperWeaknesses ?? 0;
			Widgets.IntEntry(rect, ref value, ref numVFEAncientsWeaknessesBuffer, 1);
			Current.NumVFEAncientsSuperWeaknesses = value;
			return;
		}
		DefModExtension val = VFEAncientsReflectionModule.FindVEAncientsExtension(Current.Def);
		string text = "NA";
		if (val != null)
		{
			text = VFEAncientsReflectionModule.VfeAncientsExtensionType.Value?.GetField("numRandomWeaknesses")?.GetValue(val)?.ToString();
		}
		string text2 = (Current.IsGlobal ? "---" : ("[Default] " + text));
		Widgets.Label(rect.GetCentered(text2), text2);
	}

	private void DrawVFEAncientsPowers(Rect rect, bool active, List<string> defaultPowers)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.ForcedVFEAncientsItems, new List<string>(), DefCache.AllPowerDefs);
	}
}
