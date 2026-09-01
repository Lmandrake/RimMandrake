using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class PresetUI : Window
{
	public readonly Preset Current;

	private Vector2 scroll;

	public static void OpenEditor(Preset pre)
	{
		if (pre != null)
		{
			Find.WindowStack.Add((Window)(object)new PresetUI(pre));
		}
	}

	public PresetUI(Preset pre)
		: base((IWindowDrawing)null)
	{
		Current = pre;
		base.draggable = true;
		base.resizeable = true;
		base.doCloseX = false;
		base.closeOnCancel = false;
		base.closeOnCancel = false;
		base.closeOnClickedOutside = false;
	}

	public override void PostOpen()
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).PostOpen();
		base.windowRect = new Rect(20f, 110f, Mathf.Max((float)UI.screenWidth * 0.5f - 550f, 450f), 1000f);
	}

	public override void PostClose()
	{
		((Window)this).PostClose();
		FactionEditUI factionEditUI = Find.WindowStack.WindowOfType<FactionEditUI>();
		if (factionEditUI != null)
		{
			((Window)factionEditUI).Close(true);
		}
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Expected O, but got Unknown
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_024d: Unknown result type (might be due to invalid IL or missing references)
		//IL_027a: Unknown result type (might be due to invalid IL or missing references)
		//IL_027f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_03fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_042f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0434: Unknown result type (might be due to invalid IL or missing references)
		//IL_0452: Unknown result type (might be due to invalid IL or missing references)
		//IL_048b: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_04cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_04d5: Expected O, but got Unknown
		//IL_04f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_030f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0320: Unknown result type (might be due to invalid IL or missing references)
		//IL_033e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0523: Unknown result type (might be due to invalid IL or missing references)
		//IL_0528: Unknown result type (might be due to invalid IL or missing references)
		//IL_052a: Unknown result type (might be due to invalid IL or missing references)
		//IL_057d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0582: Unknown result type (might be due to invalid IL or missing references)
		//IL_05a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_05b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_05d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_05eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0801: Unknown result type (might be due to invalid IL or missing references)
		//IL_0628: Unknown result type (might be due to invalid IL or missing references)
		//IL_0388: Unknown result type (might be due to invalid IL or missing references)
		//IL_0726: Unknown result type (might be due to invalid IL or missing references)
		//IL_072b: Unknown result type (might be due to invalid IL or missing references)
		//IL_072f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0744: Unknown result type (might be due to invalid IL or missing references)
		//IL_075e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0679: Unknown result type (might be due to invalid IL or missing references)
		//IL_0683: Unknown result type (might be due to invalid IL or missing references)
		//IL_068a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0798: Unknown result type (might be due to invalid IL or missing references)
		//IL_079f: Unknown result type (might be due to invalid IL or missing references)
		//IL_06af: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0701: Unknown result type (might be due to invalid IL or missing references)
		//IL_0708: Unknown result type (might be due to invalid IL or missing references)
		//IL_0712: Unknown result type (might be due to invalid IL or missing references)
		if (Current == null)
		{
			((Window)this).Close(true);
			return;
		}
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		Widgets.Label(((Listing)val).GetRect(50f, 1f), "<size=34><b>Preset: <color=#cf9af5>" + Current.Name + "</color></b></size>");
		Rect val2;
		Rect val3 = (val2 = ((Listing)val).GetRect(32f, 1f));
		((Rect)(ref val2)).x = Mathf.Lerp(((Rect)(ref val2)).x, ((Rect)(ref val2)).xMax, 0f);
		((Rect)(ref val2)).width = ((Rect)(ref val2)).width * 0.3f;
		val2 = GenUI.ExpandedBy(val2, -2f, -5f);
		GUI.color = Color.green;
		TaggedString val4;
		string text;
		if (!Current.IsPackaged)
		{
			val4 = Translator.Translate("Save");
			text = ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString().ToUpper();
		}
		else
		{
			val4 = Translator.Translate("FactionLoadout_SaveToSourceFile");
			text = ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString();
		}
		string text2 = text;
		if (Widgets.ButtonText(val2, "<color=white>" + text2 + "</color>", true, true, true, (TextAnchor?)null))
		{
			Current.Save();
		}
		val2 = val3;
		((Rect)(ref val2)).x = Mathf.Lerp(((Rect)(ref val2)).x, ((Rect)(ref val2)).xMax, 1f / 3f);
		((Rect)(ref val2)).width = ((Rect)(ref val2)).width * 0.3f;
		val2 = GenUI.ExpandedBy(val2, -2f, -5f);
		if (Widgets.ButtonText(val2, string.Format("<color=white>{0}</color>", Translator.Translate("FactionLoadout_Preset_SaveAndExit")), true, true, true, (TextAnchor?)null))
		{
			Current.Save();
			((Window)this).Close(true);
		}
		GUI.color = Color.Lerp(Color.white, Color.red, 0.65f);
		val2 = val3;
		((Rect)(ref val2)).x = Mathf.Lerp(((Rect)(ref val2)).x, ((Rect)(ref val2)).xMax, 2f / 3f);
		((Rect)(ref val2)).width = ((Rect)(ref val2)).width * 0.3f;
		val2 = GenUI.ExpandedBy(val2, -2f, -5f);
		Rect val5 = val2;
		val4 = Translator.Translate("Close");
		if (Widgets.ButtonText(val5, "<color=yellow>" + ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString().ToUpper() + "</color>", true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
		GUI.color = Color.white;
		((Listing)val).GapLine(12f);
		if (Current.IsPackaged)
		{
			Rect rect = ((Listing)val).GetRect(44f, 1f);
			Widgets.DrawBoxSolid(rect, new Color(0.45f, 0.35f, 0.05f, 0.85f));
			Rect val6 = GenUI.ContractedBy(rect, 6f);
			val4 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_PackagedPresetWarning", NamedArgument.op_Implicit(Current.PackagedModName));
			Widgets.Label(val6, ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString());
		}
		if (Current.HasMissingFactions())
		{
			val.Label(string.Format("<color=red>{0}</color>", Translator.Translate("FactionLoadout_Preset_MissingWarning")), -1f, (TipSignal?)null);
			val.Label(string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Preset_MissingHeader")), -1f, (TipSignal?)null);
			((Listing)val).GapLine(12f);
			foreach (string missingFactionAndModName in Current.GetMissingFactionAndModNames())
			{
				val.Label(" - " + missingFactionAndModName, -1f, (TipSignal?)null);
			}
		}
		Rect rect2 = ((Listing)val).GetRect(28f, 1f);
		((Rect)(ref rect2)).width = 200f;
		Widgets.Label(rect2, Translator.Translate("FactionLoadout_Preset_EditName"));
		((Rect)(ref rect2)).x = ((Rect)(ref rect2)).x + 80f;
		((Rect)(ref rect2)).height = ((Rect)(ref rect2)).height - 5f;
		Current.Name = Widgets.TextField(rect2, Current.Name);
		val.Label(string.Format("<b>{0}</b>", TranslatorFormattedStringExtensions.Translate("FactionLoadout_Preset_EditCount", NamedArgument.op_Implicit(Current.factionChanges.Count))), -1f, (TipSignal?)null);
		((Listing)val).Gap(12f);
		float num = Mathf.Max(100f, ((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 60f);
		Widgets.BeginScrollView(((Listing)val).GetRect(num, 1f), ref scroll, new Rect(0f, 0f, ((Rect)(ref inRect)).width - 20f, (float)(Current.factionChanges.Count * 66)), true);
		Listing_Standard val7 = val;
		val = new Listing_Standard();
		((Listing)val).Begin(new Rect(0f, 0f, ((Rect)(ref inRect)).width - 20f, 99999f));
		for (int i = 0; i < Current.factionChanges.Count; i++)
		{
			FactionEdit factionEdit = Current.factionChanges[i];
			Rect rect3 = ((Listing)val).GetRect(28f, 1f);
			Widgets.Label(rect3, "<b>" + factionEdit.Faction.LabelCap + "</b> <i>(" + factionEdit.Faction.DefName + ")</i>");
			rect3 = ((Listing)val).GetRect(28f, 1f);
			((Rect)(ref rect3)).width = 80f;
			((Rect)(ref rect3)).y = ((Rect)(ref rect3)).y - 5f;
			GUI.color = Color.red;
			string text3 = string.Format("[{0}]", Translator.Translate("Delete"));
			((Rect)(ref rect3)).width = Mathf.Max(80f, Text.CalcSize(text3).x + 10f);
			if (Widgets.ButtonText(rect3, text3, true, true, true, (TextAnchor?)null))
			{
				factionEdit.DeletedOrClosed = true;
				Current.factionChanges.RemoveAt(i);
				i--;
				continue;
			}
			GUI.color = Color.white;
			((Rect)(ref rect3)).x = ((Rect)(ref rect3)).x + (((Rect)(ref rect3)).width + 10f);
			if (factionEdit.Faction.IsMissing)
			{
				((Rect)(ref rect3)).width = 120f;
				GUI.color = new Color(1f, 0.75f, 0.2f);
				if (Widgets.ButtonText(rect3, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_EditAnyway")), true, true, true, (TextAnchor?)null))
				{
					FactionEditUI.OpenEditor(factionEdit);
				}
				GUI.color = Color.white;
				((Rect)(ref rect3)).x = ((Rect)(ref rect3)).x + 130f;
				((Rect)(ref rect3)).width = ((Rect)(ref inRect)).width - 20f - ((Rect)(ref rect3)).x;
				GUI.color = new Color(1f, 0.4f, 0.4f);
				Widgets.Label(rect3, Translator.Translate("FactionLoadout_FactionMissing"));
				GUI.color = Color.white;
			}
			else
			{
				val4 = Translator.Translate("FactionLoadout_Edit");
				string text4 = TaggedString.op_Implicit(((TaggedString)(ref val4)).CapitalizeFirst());
				((Rect)(ref rect3)).width = Mathf.Max(80f, Text.CalcSize(text4).x + 10f);
				if (Widgets.ButtonText(rect3, text4, true, true, true, (TextAnchor?)null))
				{
					FactionEditUI.OpenEditor(factionEdit);
				}
				((Rect)(ref rect3)).x = ((Rect)(ref rect3)).x + (((Rect)(ref rect3)).width + 10f);
				Widgets.CheckboxLabeled(rect3, TaggedString.op_Implicit(Translator.Translate("Enabled")), ref factionEdit.Active, false, (Texture2D)null, (Texture2D)null, true, false);
			}
			((Listing)val).GapLine(10f);
		}
		((Listing)val).End();
		Widgets.EndScrollView();
		val = val7;
		((Listing)val).Gap(12f);
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Preset_AddFactionEdit")), (string)null, 1f))
		{
			List<FactionDef> list = DefDatabase<FactionDef>.AllDefsListForReading.Where((FactionDef f) => !Current.HasEditFor(f)).ToList();
			if (!Current.HasEditFor(Preset.SpecialCreepjoinerFaction) && !GenCollection.Any<FactionDef>(list, (Predicate<FactionDef>)((FactionDef f) => ((Def)f).defName == ((Def)Preset.SpecialCreepjoinerFaction).defName)))
			{
				list.Add(Preset.SpecialCreepjoinerFaction);
			}
			if (!Current.HasEditFor(Preset.SpecialWildManFaction) && !GenCollection.Any<FactionDef>(list, (Predicate<FactionDef>)((FactionDef f) => ((Def)f).defName == ((Def)Preset.SpecialWildManFaction).defName)))
			{
				list.Add(Preset.SpecialWildManFaction);
			}
			if (Preset.FactionlessPawnKindsSet.Count > 0 && !Current.HasEditFor(Preset.SpecialFactionlessPawnsFaction) && !GenCollection.Any<FactionDef>(list, (Predicate<FactionDef>)((FactionDef f) => ((Def)f).defName == ((Def)Preset.SpecialFactionlessPawnsFaction).defName)))
			{
				list.Add(Preset.SpecialFactionlessPawnsFaction);
			}
			CustomFloatMenu.Open(CustomFloatMenu.MakeItems(list, (FactionDef f) => new MenuItemText(f, $"{((Def)f).LabelCap} ({((Def)f).defName})", DefUtils.TryGetIcon((Def)(object)f, out var color), color, ((Def)f).description)), delegate(MenuItemBase menuItemBase)
			{
				FactionDef payload = menuItemBase.GetPayload<FactionDef>();
				FactionEdit item = new FactionEdit
				{
					Faction = payload
				};
				Current.factionChanges.Add(item);
			});
		}
		((Listing)val).End();
	}
}
