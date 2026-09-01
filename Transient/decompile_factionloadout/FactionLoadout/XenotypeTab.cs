using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class XenotypeTab : EditTab
{
	public XenotypeTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_Xenotypes")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0215: Unknown result type (might be due to invalid IL or missing references)
		//IL_020e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f6: Unknown result type (might be due to invalid IL or missing references)
		ref List<ForcedGene> forcedGenes = ref Current.ForcedGenes;
		TaggedString val = Translator.Translate("FactionLoadout_Xenotype_RequiredAdvanced");
		DrawSpecificGenes(ui, ref forcedGenes, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (GeneDef _) => true, DefCache.AllGeneDefs.First());
		DrawForceSpecificXenos(ui);
		if (!Current.ForceSpecificXenos)
		{
			return;
		}
		ui.Label("<b>Xenotype spawn rates:</b>", -1f, (TipSignal?)null);
		List<string> toDelete = new List<string>();
		if (GenDictionary.NullOrEmpty<string, float>(Current.ForcedXenotypeChances))
		{
			Current.ForcedXenotypeChances = Current.Def?.xenotypeSet?.xenotypeChances?.ToDictionary((XenotypeChance x) => ((Def)x.xenotype).defName, (XenotypeChance x) => x.chance) ?? new Dictionary<string, float>();
			if (!Current.ForcedXenotypeChances.ContainsKey(FactionEditUI.BaselinerDefName))
			{
				Dictionary<string, float> forcedXenotypeChances = Current.ForcedXenotypeChances;
				string baselinerDefName = FactionEditUI.BaselinerDefName;
				PawnKindDef def2 = Current.Def;
				float? obj;
				if (def2 == null)
				{
					obj = null;
				}
				else
				{
					XenotypeSet xenotypeSet = def2.xenotypeSet;
					obj = ((xenotypeSet != null) ? new float?(xenotypeSet.BaselinerChance) : ((float?)null));
				}
				forcedXenotypeChances.Add(baselinerDefName, obj ?? 1f);
			}
		}
		foreach (string key in Current.ForcedXenotypeChances.Keys.ToList())
		{
			Dictionary<string, float> forcedXenotypeChances2 = Current.ForcedXenotypeChances;
			string key2 = key;
			XenotypeDef namedSilentFail = DefDatabase<XenotypeDef>.GetNamedSilentFail(key);
			forcedXenotypeChances2[key2] = UIHelpers.SliderLabeledWithDelete(ui, $"{((namedSilentFail != null) ? ((Def)namedSilentFail).LabelCap : TaggedString.op_Implicit(key))}: {GenText.ToStringPercent(Current.ForcedXenotypeChances[key])}", Current.ForcedXenotypeChances[key], 0f, 1f, 0.5f, null, delegate
			{
				toDelete.Add(key);
			});
		}
		foreach (string item in toDelete)
		{
			Current.ForcedXenotypeChances.Remove(item);
		}
		val = Translator.Translate("Add");
		if (ui.ButtonText(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst() + "..."), (string)null, 1f))
		{
			CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefDatabase<XenotypeDef>.AllDefs.Where((XenotypeDef def) => !Current.ForcedXenotypeChances.ContainsKey(((Def)def).defName)), (XenotypeDef def) => new MenuItemText(def, TaggedString.op_Implicit(((Def)def).LabelCap), def.Icon)), delegate(MenuItemBase item)
			{
				XenotypeDef payload = item.GetPayload<XenotypeDef>();
				Current.ForcedXenotypeChances[((Def)payload).defName] = 0.1f;
			});
		}
	}

	private void DrawForceSpecificXenos(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		Widgets.CheckboxLabeled(((Listing)ui).GetRect(32f, 1f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Xenotype_ForceSpecific")), ref Current.ForceSpecificXenos, false, (Texture2D)null, (Texture2D)null, true, false);
		((Listing)ui).Gap(12f);
	}

	private void DrawSpecificGenes(Listing_Standard ui, ref List<ForcedGene> edits, string label, Func<GeneDef, bool> geneFilter, GeneDef defaultGeneDef)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Expected O, but got Unknown
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		float num = ((edits == null) ? 32 : 340);
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = edits != null;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			edits = (flag ? null : new List<ForcedGene>());
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, ((Rect)(ref rect)).height - 30f);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		ref Vector2 reference = ref scrolls[scrollIndex++];
		if (flag)
		{
			Widgets.BeginScrollView(val, ref reference, new Rect(0f, 0f, 100f, (float)(320 * edits.Count - 10)), true);
			Listing_Standard val2 = new Listing_Standard();
			((Listing)val2).Begin(new Rect(0f, 0f, ((Rect)(ref val)).width - 20f, (float)(320 * edits.Count)));
			DrawSpecificGeneContent(val2, geneFilter, edits);
			((Listing)val2).End();
			Widgets.EndScrollView();
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			Rect val3 = val;
			TaggedString val4 = Translator.Translate("Add");
			if (Widgets.ButtonText(val3, TaggedString.op_Implicit("<b>" + ((TaggedString)(ref val4)).CapitalizeFirst() + "</b>"), true, true, true, (TextAnchor?)null))
			{
				edits.Add(new ForcedGene
				{
					GeneDef = defaultGeneDef
				});
			}
		}
		else
		{
			string text2 = "[Default] <i>None</i>";
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text2), text2);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private void DrawSpecificGeneContent(Listing_Standard tempUI, Func<GeneDef, bool> geneFilter, List<ForcedGene> edits)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_026c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Unknown result type (might be due to invalid IL or missing references)
		//IL_0296: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a5: Unknown result type (might be due to invalid IL or missing references)
		if (edits == null)
		{
			return;
		}
		for (int i = 0; i < edits.Count; i++)
		{
			ForcedGene item = edits[i];
			if (item?.GeneDef == null)
			{
				continue;
			}
			Rect rect = ((Listing)tempUI).GetRect(150f, 1f);
			Widgets.DrawBoxSolidWithOutline(rect, default(Color), Color.white * 0.75f, 1);
			Rect val = new Rect(((Rect)(ref rect)).xMax - 105f, ((Rect)(ref rect)).y + 5f, 100f, 20f);
			GUI.color = Color.red;
			TaggedString val2 = Translator.Translate("Remove");
			if (Widgets.ButtonText(val, "<b>" + ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString().ToUpper() + "</b>", true, true, true, (TextAnchor?)null))
			{
				edits.RemoveAt(i);
				i--;
				continue;
			}
			GUI.color = Color.white;
			((Listing)tempUI).Gap(2f);
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x + 5f, ((Rect)(ref rect)).y + 5f, 250f, 25f), TaggedString.op_Implicit(((Def)item.GeneDef).LabelCap), true, true, true, (TextAnchor?)null))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefDatabase<GeneDef>.AllDefsListForReading.Where(geneFilter), (GeneDef d) => new MenuItemText(d, $"{((Def)d).LabelCap} ({((Def)d).defName})", DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), delegate(MenuItemBase raw)
				{
					GeneDef payload = raw.GetPayload<GeneDef>();
					item.GeneDef = payload;
				});
			}
			Widgets.CheckboxLabeled(new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 40f, ((Rect)(ref rect)).width - 10f, 30f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Xenotype_Xenogene")), ref item.xenogene, false, (Texture2D)null, (Texture2D)null, false, false);
			Widgets.CheckboxLabeled(new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 70f, ((Rect)(ref rect)).width - 10f, 30f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_ForceActive")), ref item.forceActive, false, (Texture2D)null, (Texture2D)null, false, false);
			Rect val3 = new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 100f, ((Rect)(ref rect)).width - 10f, 30f);
			Widgets.Label(GenUI.LeftPart(val3, 0.7f), TranslatorFormattedStringExtensions.Translate("FactionLoadout_ChanceToApply", NamedArgument.op_Implicit(GenText.ToStringPercent(item.chance))));
			Widgets.TextFieldPercent(GenUI.RightPart(val3, 0.29f), ref item.chance, ref buffers[bufferIndex++], 0f, 1f);
			((Listing)tempUI).Gap(3f);
		}
	}
}
