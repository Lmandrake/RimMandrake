using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using FactionLoadout.Modules;
using FactionLoadout.Patches;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class FactionEditUI : Window
{
	public static string BaselinerDefName = "Baseliner";

	public readonly FactionEdit Current;

	private readonly List<PawnKindEdit> bin = new List<PawnKindEdit>();

	private FactionDef clonedFac;

	private UIState filterState = new UIState();

	private int framesSinceF;

	private readonly List<Pawn> pawns = new List<Pawn>();

	private readonly HashSet<PawnKindDef> tempKinds = new HashSet<PawnKindDef>();

	private bool _ThingIDPatch;

	private bool _previewFailed;

	private Vector2 overridesScrollPos;

	private float overridesContentHeight = 10000f;

	public FactionEditUI(FactionEdit fac)
		: base((IWindowDrawing)null)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Expected O, but got Unknown
		Current = fac;
		base.draggable = true;
		base.resizeable = true;
		base.doCloseX = true;
		base.closeOnCancel = true;
		base.closeOnClickedOutside = false;
	}

	public static void OpenEditor(FactionEdit fac)
	{
		if (fac != null)
		{
			Find.WindowStack.Add((Window)(object)new FactionEditUI(fac));
		}
	}

	public override void PostOpen()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).PostOpen();
		Rect windowRect = base.windowRect;
		((Rect)(ref windowRect)).y = 110f;
		((Rect)(ref windowRect)).x = ((Rect)(ref windowRect)).x - (((Rect)(ref windowRect)).width * 0.5f + 15f);
		((Rect)(ref windowRect)).height = 800f;
		base.windowRect = windowRect;
	}

	public override void PostClose()
	{
		((Window)this).PostClose();
		DestroyPawns();
		clonedFac = null;
		PawnKindEditUI pawnKindEditUI = Find.WindowStack.WindowOfType<PawnKindEditUI>();
		if (pawnKindEditUI != null)
		{
			((Window)pawnKindEditUI).Close(true);
		}
	}

	private void DestroyPawns()
	{
		foreach (Pawn pawn in pawns)
		{
			if (pawn == null)
			{
				continue;
			}
			WorldPawns worldPawns = Find.WorldPawns;
			if (worldPawns != null && worldPawns.Contains(pawn))
			{
				Find.WorldPawns.RemoveAndDiscardPawnViaGC(pawn);
			}
			else if (!((Thing)pawn).Discarded)
			{
				WorldPawns worldPawns2 = Find.WorldPawns;
				if (worldPawns2 != null)
				{
					worldPawns2.PassToWorld(pawn, (PawnDiscardDecideMode)2);
				}
			}
		}
		pawns.Clear();
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_16bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Expected O, but got Unknown
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a80: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a9e: Unknown result type (might be due to invalid IL or missing references)
		//IL_164b: Unknown result type (might be due to invalid IL or missing references)
		//IL_1650: Unknown result type (might be due to invalid IL or missing references)
		//IL_169a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_021a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_0230: Expected O, but got Unknown
		//IL_0232: Unknown result type (might be due to invalid IL or missing references)
		//IL_0240: Unknown result type (might be due to invalid IL or missing references)
		//IL_0af9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0afe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b05: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b18: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b2f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b4e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b7e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ba3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ba8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bac: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bbf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0beb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c45: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c75: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c7f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c84: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d15: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d37: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d50: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d72: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d7c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d81: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cc0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cf0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d04: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d09: Unknown result type (might be due to invalid IL or missing references)
		//IL_0f1e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0f23: Unknown result type (might be due to invalid IL or missing references)
		//IL_0f27: Unknown result type (might be due to invalid IL or missing references)
		//IL_0f31: Unknown result type (might be due to invalid IL or missing references)
		//IL_077d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0782: Unknown result type (might be due to invalid IL or missing references)
		//IL_07a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e42: Unknown result type (might be due to invalid IL or missing references)
		//IL_0dc3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0de5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0df4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e16: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e20: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e25: Unknown result type (might be due to invalid IL or missing references)
		//IL_114b: Unknown result type (might be due to invalid IL or missing references)
		//IL_1160: Unknown result type (might be due to invalid IL or missing references)
		//IL_119e: Unknown result type (might be due to invalid IL or missing references)
		//IL_11a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_111c: Unknown result type (might be due to invalid IL or missing references)
		//IL_113a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0fe8: Unknown result type (might be due to invalid IL or missing references)
		//IL_07d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_07de: Unknown result type (might be due to invalid IL or missing references)
		//IL_07e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_07fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e79: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e59: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e5e: Unknown result type (might be due to invalid IL or missing references)
		//IL_13b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_08b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_08b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_08c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_08d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_08d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_08e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_08f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_087e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0883: Unknown result type (might be due to invalid IL or missing references)
		//IL_1248: Unknown result type (might be due to invalid IL or missing references)
		//IL_1227: Unknown result type (might be due to invalid IL or missing references)
		//IL_1065: Unknown result type (might be due to invalid IL or missing references)
		//IL_125e: Unknown result type (might be due to invalid IL or missing references)
		//IL_1265: Unknown result type (might be due to invalid IL or missing references)
		//IL_14c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_14c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_14d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_14da: Unknown result type (might be due to invalid IL or missing references)
		//IL_14ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_14fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_152e: Unknown result type (might be due to invalid IL or missing references)
		//IL_153f: Unknown result type (might be due to invalid IL or missing references)
		//IL_128a: Unknown result type (might be due to invalid IL or missing references)
		//IL_1294: Unknown result type (might be due to invalid IL or missing references)
		//IL_09a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_09aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_09cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_09e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_09f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0705: Unknown result type (might be due to invalid IL or missing references)
		//IL_070a: Unknown result type (might be due to invalid IL or missing references)
		//IL_06e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_1578: Unknown result type (might be due to invalid IL or missing references)
		//IL_157f: Unknown result type (might be due to invalid IL or missing references)
		//IL_1588: Expected O, but got Unknown
		//IL_10bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_10b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_071d: Unknown result type (might be due to invalid IL or missing references)
		//IL_05b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_05b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_1360: Unknown result type (might be due to invalid IL or missing references)
		//IL_12c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_12c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_1312: Unknown result type (might be due to invalid IL or missing references)
		//IL_05d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0598: Unknown result type (might be due to invalid IL or missing references)
		//IL_059d: Unknown result type (might be due to invalid IL or missing references)
		//IL_046d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0464: Unknown result type (might be due to invalid IL or missing references)
		//IL_0472: Unknown result type (might be due to invalid IL or missing references)
		//IL_0477: Unknown result type (might be due to invalid IL or missing references)
		//IL_047c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0498: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0411: Unknown result type (might be due to invalid IL or missing references)
		//IL_0619: Unknown result type (might be due to invalid IL or missing references)
		//IL_061e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0439: Unknown result type (might be due to invalid IL or missing references)
		//IL_043e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0443: Unknown result type (might be due to invalid IL or missing references)
		//IL_042f: Unknown result type (might be due to invalid IL or missing references)
		framesSinceF++;
		if (Current == null || Current.DeletedOrClosed)
		{
			((Window)this).Close(true);
			return;
		}
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		Rect rect = ((Listing)val).GetRect(50f, 1f);
		FactionDef def = Current.Faction.Def;
		Widgets.Label(rect, string.Format("<size=34><b>Faction: <color=#cf9af5>{0}</color></b></size>", (def != null) ? ((Def)def).LabelCap : Translator.Translate("None")));
		if (Current.Faction.IsMissing)
		{
			val.Label(string.Format("<color=orange>{0}</color>", Translator.Translate("FactionLoadout_FactionMissingEditWarning")), -1f, (TipSignal?)null);
		}
		if (Current.Faction.DefName == Preset.SpecialCreepjoinerFactionDefName)
		{
			val.Label(string.Format("<color=yellow>{0}</color>", Translator.Translate("FactionLoadout_FactionEdit_ExperimentalCreepjoiner")), -1f, (TipSignal?)null);
		}
		if (Current.Faction.DefName == Preset.SpecialWildManFactionDefName)
		{
			val.Label(string.Format("<color=yellow>{0}</color>", Translator.Translate("FactionLoadout_FactionEdit_ExperimentalWildMan")), -1f, (TipSignal?)null);
		}
		if (Current.Faction.DefName == Preset.SpecialFactionlessPawnsFactionDefName)
		{
			val.Label(string.Format("<color=yellow>{0}</color>", Translator.Translate("FactionLoadout_Special_FactionlessWarning")), -1f, (TipSignal?)null);
		}
		if (!Current.Faction.IsMissing)
		{
			DrawFactionClipboardToolbar(val);
		}
		float num = Mathf.Max(60f, ((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 200f);
		Rect rect2 = ((Listing)val).GetRect(num, 1f);
		float num2 = Mathf.Max(overridesContentHeight + 100f, num);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref rect2)).width - 16f, num2);
		Widgets.BeginScrollView(rect2, ref overridesScrollPos, val2, true);
		Listing_Standard val3 = new Listing_Standard();
		((Listing)val3).Begin(val2);
		string text = TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Faction_Techlevel"));
		ref TechLevel? techLevel = ref Current.TechLevel;
		if (val3.ButtonTextLabeled(text, (techLevel.HasValue ? TechLevelUtility.ToStringHuman(techLevel.GetValueOrDefault()) : null) ?? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_NotOverriden_WithDefault", NamedArgument.op_Implicit(TechLevelUtility.ToStringHuman((Current.Faction?.Def?.techLevel).GetValueOrDefault())))), (TextAnchor)0, (string)null, (string)null))
		{
			FloatMenuUtility.MakeMenu<TechLevel?>(Enum.GetValues(typeof(TechLevel)).Cast<TechLevel?>().Append(null), (Func<TechLevel?, string>)((TechLevel? e) => (e.HasValue ? TechLevelUtility.ToStringHuman(e.GetValueOrDefault()) : null) ?? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_NotOverriden_WithDefault", NamedArgument.op_Implicit(TechLevelUtility.ToStringHuman((Current.Faction?.Def?.techLevel).GetValueOrDefault()))))), (Func<TechLevel?, Action>)((TechLevel? e) => delegate
			{
				Current.TechLevel = e;
			}));
		}
		DefRef<FactionDef> faction = Current.Faction;
		PawnKindDef val4;
		TaggedString val5;
		string text2;
		if (faction != null && !faction.IsMissing && Current.Faction?.Def != Preset.SpecialWildManFaction && Current.Faction?.Def != Preset.SpecialCreepjoinerFaction && Current.Faction?.Def != Preset.SpecialFactionlessPawnsFaction)
		{
			val4 = Current.Faction?.Def?.basicMemberKind;
			DefRef<PawnKindDef> basicMemberKind = Current.BasicMemberKind;
			if (basicMemberKind == null)
			{
				goto IL_0456;
			}
			if (!basicMemberKind.HasValue)
			{
				if (!basicMemberKind.IsMissing)
				{
					goto IL_0456;
				}
				val5 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_DefRef_Missing", NamedArgument.op_Implicit(Current.BasicMemberKind.DefName), NamedArgument.op_Implicit(Current.BasicMemberKind.ModName ?? TaggedString.op_Implicit(Translator.Translate("FactionLoadout_DefRef_UnknownMod"))));
				text2 = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
			}
			else
			{
				text2 = Current.BasicMemberKind.LabelCap;
			}
			goto IL_048d;
		}
		goto IL_04c4;
		IL_0456:
		val5 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_NotOverriden_WithDefault", NamedArgument.op_Implicit((val4 != null) ? ((Def)val4).LabelCap : Translator.Translate("None")));
		text2 = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
		goto IL_048d;
		IL_04c4:
		if (ModsConfig.IdeologyActive)
		{
			faction = Current.Faction;
			if (faction != null && !faction.IsMissing && Current.Faction?.Def != Preset.SpecialWildManFaction && Current.Faction?.Def != Preset.SpecialCreepjoinerFaction && Current.Faction?.Def != Preset.SpecialFactionlessPawnsFaction)
			{
				((Listing)val3).GapLine(12f);
				string text3;
				if (!ForcedIdeoRefUI.DisabledByClassicMode)
				{
					if (!string.IsNullOrEmpty(Current.ForcedPrimaryIdeoKey))
					{
						text3 = ForcedIdeoRefUI.DisplayName(Current.ForcedPrimaryIdeoSourceKind, Current.ForcedPrimaryIdeoKey);
					}
					else
					{
						val5 = Translator.Translate("FactionLoadout_Faction_PrimaryIdeoNotOverridden");
						text3 = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
					}
				}
				else
				{
					val5 = Translator.Translate("FactionLoadout_General_IdeoClassicDisabled");
					text3 = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
				}
				string text4 = text3;
				if (val3.ButtonTextLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Faction_PrimaryIdeo")), text4, (TextAnchor)0, (string)null, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Faction_PrimaryIdeoTooltip"))) && !ForcedIdeoRefUI.DisabledByClassicMode)
				{
					Action<ForcedIdeoSource, string> onPick = delegate(ForcedIdeoSource source, string key)
					{
						Current.ForcedPrimaryIdeoSourceKind = source;
						Current.ForcedPrimaryIdeoKey = key;
					};
					Action onClear = delegate
					{
						Current.ForcedPrimaryIdeoKey = null;
					};
					val5 = Translator.Translate("FactionLoadout_Faction_PrimaryIdeoNotOverridden");
					ForcedIdeoRefUI.OpenPicker(includeFactionPrimary: false, onPick, onClear, ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString());
				}
			}
		}
		if (ModsConfig.BiotechActive)
		{
			faction = Current.Faction;
			if (faction != null && !faction.IsMissing && Current.Faction?.Def != Preset.SpecialWildManFaction && Current.Faction?.Def != Preset.SpecialFactionlessPawnsFaction)
			{
				if (!Current.OverrideFactionXenotypes)
				{
					Current.xenotypeChances.Clear();
					Current.xenotypeChancesByDef.Clear();
				}
				((Listing)val3).GapLine(12f);
				string text5 = TaggedString.op_Implicit(Current.OverrideFactionXenotypes ? TranslatorFormattedStringExtensions.Translate("FactionLoadout_Xenotype_ActiveCount", NamedArgument.op_Implicit(Current.xenotypeChances.Count)) : Translator.Translate("FactionLoadout_Xenotype_Off"));
				if (val3.ButtonTextLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_EditXenoSpawnRates")), text5, (TextAnchor)0, (string)null, (string)null))
				{
					Find.WindowStack.Add((Window)(object)new Dialog_XenotypeEdit(Current));
				}
			}
		}
		faction = Current.Faction;
		if (faction == null || !faction.IsMissing)
		{
			((Listing)val3).GapLine(12f);
			Rect rect3 = ((Listing)val3).GetRect(28f, 1f);
			float num3 = 160f;
			Rect val6 = new Rect(((Rect)(ref rect3)).xMax - num3, ((Rect)(ref rect3)).y, num3, 24f);
			Text.Anchor = (TextAnchor)3;
			string text6;
			if (Current.PawnGroupMakerEdits != null)
			{
				int count = Current.PawnGroupMakerEdits.Count;
				NamedArgument val7 = NamedArgument.op_Implicit(count);
				val5 = Translator.Translate("FactionLoadout_GroupEditor_NewTag");
				text6 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_SpawnGroups_SummaryModified", val7, NamedArgument.op_Implicit(((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString().ToLower())));
			}
			else
			{
				int count = (Current?.Faction?.Def?.pawnGroupMakers?.Count).GetValueOrDefault();
				text6 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_SpawnGroups_Summary", NamedArgument.op_Implicit(count)));
			}
			Rect val8 = new Rect(((Rect)(ref rect3)).x, ((Rect)(ref rect3)).y, ((Rect)(ref rect3)).width - num3 - 4f, ((Rect)(ref rect3)).height);
			GUI.color = Color.grey;
			Widgets.Label(val8, Translator.Translate("FactionLoadout_SpawnGroups_Label") + "  " + text6);
			GUI.color = Color.white;
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonText(val6, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_SpawnGroups_EditButton")), true, true, true, (TextAnchor?)null))
			{
				GroupEditorUI.OpenEditor(Current);
			}
			HashSet<PawnKindDef> hashSet = Current?.GetOrphanedKinds() ?? new HashSet<PawnKindDef>();
			if (hashSet.Count > 0)
			{
				string text7 = GenText.ToCommaList((IEnumerable<string>)(from n in hashSet.Select(delegate(PawnKindDef k)
					{
						//IL_0001: Unknown result type (might be due to invalid IL or missing references)
						//IL_0006: Unknown result type (might be due to invalid IL or missing references)
						TaggedString labelCap = ((Def)k).LabelCap;
						return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
					})
					orderby n
					select n), false, false);
				string text8 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_SpawnGroups_OrphanWarning", NamedArgument.op_Implicit(text7)));
				float num4 = Text.CalcHeight(text8, ((Listing)val3).ColumnWidth);
				Rect rect4 = ((Listing)val3).GetRect(num4, 1f);
				GUI.color = new Color(1f, 0.6f, 0.1f);
				Widgets.Label(rect4, text8);
				GUI.color = Color.white;
			}
		}
		foreach (ITotalControlModule module in ModuleRegistry.Modules)
		{
			if (module.IsActive)
			{
				try
				{
					module.AddFactionUI(Current, val3);
				}
				catch (Exception e2)
				{
					ModCore.Error("Error drawing faction UI for module '" + module.ModuleName + "'", e2);
				}
			}
		}
		((Listing)val3).GapLine(12f);
		val3.Label(string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_FactionEdit_LoadoutOverrides")), -1f, (TipSignal?)null);
		((Listing)val3).Gap(12f);
		HashSet<PawnKindDef> hashSet2 = Current?.GetOrphanedKinds() ?? new HashSet<PawnKindDef>();
		foreach (PawnKindEdit kindEdit in Current.KindEdits)
		{
			Rect rect5 = ((Listing)val3).GetRect(30f, 1f);
			string text9 = TaggedString.op_Implicit(Translator.Translate("Delete"));
			float num5 = Mathf.Max(38f, Text.CalcSize(text9).x + 10f);
			GUI.color = Color.red;
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, num5, 24f), text9, true, true, true, (TextAnchor?)null))
			{
				bin.Add(kindEdit);
				kindEdit.DeletedOrClosed = true;
			}
			GUI.color = Color.white;
			((Rect)(ref rect5)).x = ((Rect)(ref rect5)).x + (num5 + 4f);
			val5 = Translator.Translate("FactionLoadout_Edit");
			string text10 = TaggedString.op_Implicit(((TaggedString)(ref val5)).CapitalizeFirst());
			float num6 = Mathf.Max(50f, Text.CalcSize(text10).x + 10f);
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, num6, 24f), text10, true, true, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)new PawnKindEditUI(kindEdit));
			}
			((Rect)(ref rect5)).x = ((Rect)(ref rect5)).x + (num6 + 4f);
			if (Widgets.ButtonImageFitted(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), TexButton.Copy))
			{
				PawnKindClipboard.Copy(kindEdit);
			}
			TooltipHandler.TipRegion(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_CopyTooltip")));
			((Rect)(ref rect5)).x = ((Rect)(ref rect5)).x + 28f;
			if (PawnKindClipboard.HasData)
			{
				if (Widgets.ButtonImageFitted(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), TexButton.Paste))
				{
					PawnKindClipboard.PasteAll(kindEdit);
				}
				TooltipHandler.TipRegion(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_Clipboard_PasteAllTooltip", NamedArgument.op_Implicit(PawnKindClipboard.GetDescription()))));
			}
			else
			{
				GUI.color = Color.gray;
				Widgets.DrawTextureFitted(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), (Texture)(object)TexButton.Paste, 1f, 1f);
				GUI.color = Color.white;
				TooltipHandler.TipRegion(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 24f, 24f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_Empty")));
			}
			((Rect)(ref rect5)).x = ((Rect)(ref rect5)).x + 28f;
			if (!kindEdit.IsGlobal && kindEdit.Def != null && hashSet2.Contains(kindEdit.Def))
			{
				GUI.color = Color.yellow;
				Widgets.Label(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 20f, 24f), "⚠");
				GUI.color = Color.white;
				TooltipHandler.TipRegion(new Rect(((Rect)(ref rect5)).x, ((Rect)(ref rect5)).y, 20f, 24f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_SpawnGroups_OrphanKindTooltip")));
				((Rect)(ref rect5)).x = ((Rect)(ref rect5)).x + 22f;
			}
			Rect val9 = rect5;
			string text11;
			if (!kindEdit.IsGlobal)
			{
				val5 = ((Def)kindEdit.Def).LabelCap;
				text11 = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
			}
			else
			{
				text11 = string.Format("<color=cyan>{0}</color>", Translator.Translate("FactionLoadout_GlobalLabel"));
			}
			Widgets.Label(val9, "<b>" + text11 + "</b>");
		}
		foreach (PawnKindEdit item2 in bin)
		{
			Current.KindEdits.Remove(item2);
		}
		bin.Clear();
		if (!Current.Faction.IsMissing)
		{
			val5 = Translator.Translate("Add");
			if (val3.ButtonText(TaggedString.op_Implicit(((TaggedString)(ref val5)).CapitalizeFirst() + "..."), (string)null, 1f))
			{
				List<PawnKindDef> kinds = MakeKinds().ToList();
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(kinds, delegate(PawnKindDef k)
				{
					//IL_0035: Unknown result type (might be due to invalid IL or missing references)
					//IL_0054: Unknown result type (might be due to invalid IL or missing references)
					//IL_005a: Unknown result type (might be due to invalid IL or missing references)
					//IL_000e: Unknown result type (might be due to invalid IL or missing references)
					//IL_0020: Unknown result type (might be due to invalid IL or missing references)
					//IL_0026: Unknown result type (might be due to invalid IL or missing references)
					if (k == null)
					{
						return new MenuItemText(null, string.Format("<color=cyan><b>{0}</b></color>", Translator.Translate("FactionLoadout_GlobalLabel")));
					}
					string text12 = $"{((Def)k).LabelCap} ({((Def)k).defName})";
					string description = ((Def)k).description;
					return new MenuItemText(k, text12, null, default(Color), description);
				}), delegate(MenuItemBase raw)
				{
					PawnKindDef payload = raw.GetPayload<PawnKindDef>();
					if (payload != null)
					{
						Current.KindEdits.Add(new PawnKindEdit(payload));
					}
					else
					{
						PawnKindDef val10 = GenCollection.FirstOrDefault<PawnKindDef>(kinds, (Predicate<PawnKindDef>)((PawnKindDef pawnKindDef) => pawnKindDef != null));
						ModCore.Log($"Using {val10} as global base.");
						if (val10 != null)
						{
							Current.KindEdits.Insert(0, new PawnKindEdit(val10)
							{
								IsGlobal = true
							});
						}
					}
				});
			}
		}
		overridesContentHeight = ((Listing)val3).CurHeight;
		((Listing)val3).End();
		Widgets.EndScrollView();
		((Listing)val).GapLine(26f);
		if (Prefs.DevMode && clonedFac != null && val.ButtonText(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionEdit_DebugClonedKinds")), (string)null, 1f))
		{
			foreach (PawnKindDef kindDef in clonedFac.GetKindDefs())
			{
				ModCore.Log("Kind: " + ((Def)kindDef).label + " (" + ((Def)kindDef).defName + ")");
				ModCore.Log($" - Apparel Money: {kindDef.apparelMoney}");
				if (kindDef.apparelRequired == null)
				{
					continue;
				}
				ModCore.Log(" - Apparel required:");
				foreach (ThingDef item3 in kindDef.apparelRequired)
				{
					ModCore.Log(string.Format("  * {0}", (item3 != null) ? ((Def)item3).LabelCap : TaggedString.op_Implicit("<null>")));
				}
			}
		}
		bool flag = Current.Game != null;
		if (!flag)
		{
			val.Label(string.Format("<color=yellow>{0}</color>", Translator.Translate("FactionLoadout_FactionEdit_PreviewError")), -1f, (TipSignal?)null);
		}
		else
		{
			val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionEdit_ThingIDPatch")), ref _ThingIDPatch, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionEdit_ThingIDPatchTooltip")), 0f, 1f);
			((Listing)val).Gap(20f);
			Rect rect6 = ((Listing)val).GetRect(((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 32f, 1f);
			int count2 = pawns.Count;
			if (count2 != 0)
			{
				float num7 = Mathf.Max(((Rect)(ref rect6)).height - 26f - 10f, 50f);
				float num8 = Mathf.Min(((Rect)(ref rect6)).width / (float)count2, num7);
				Rect val11 = default(Rect);
				for (int i = 0; i < count2; i++)
				{
					((Rect)(ref val11))._002Ector(((Rect)(ref rect6)).x + (float)i * num8, ((Rect)(ref rect6)).y, num8, num8);
					Pawn val12 = pawns[i];
					if (val12 != null)
					{
						Widgets.ThingIcon(val11, (Thing)(object)val12, 1f, (Rot4?)null, false, 1f, false);
					}
					else
					{
						Widgets.DrawTextureFitted(val11, (Texture)(object)Widgets.CheckboxOffTex, 1f, 1f);
					}
					Widgets.DrawHighlightIfMouseover(val11);
					Rect val13 = val11;
					object obj;
					if (val12 == null)
					{
						obj = null;
					}
					else
					{
						string kindLabel = val12.KindLabel;
						obj = ((kindLabel != null) ? GenText.CapitalizeFirst(kindLabel) : null);
					}
					if (obj == null)
					{
						obj = "<ERROR INVALID PAWN>";
					}
					TooltipHandler.TipRegion(val13, TipSignal.op_Implicit((string)obj));
					if (Mouse.IsOver(val11) && val12 != null)
					{
						Pawn p = pawns[i];
						Rect windowRect = base.windowRect;
						((Rect)(ref windowRect)).y = ((Rect)(ref windowRect)).y + 510f;
						((Rect)(ref windowRect)).x = ((Rect)(ref windowRect)).x - 425f;
						((Rect)(ref windowRect)).height = 550f;
						((Rect)(ref windowRect)).width = 410f;
						Find.WindowStack.ImmediateWindow(90812358, windowRect, (WindowLayer)3, (Action)delegate
						{
							//IL_0063: Unknown result type (might be due to invalid IL or missing references)
							//IL_0072: Expected O, but got Unknown
							List<object> obj2 = (typeof(Selector).GetField("selected", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(Find.Selector) as List<object>) ?? new List<object>();
							obj2.Clear();
							obj2.Add(p);
							typeof(ITab_Pawn_Gear).GetMethod("FillTab", BindingFlags.Instance | BindingFlags.NonPublic)?.Invoke((object)new ITab_Pawn_Gear(), Array.Empty<object>());
							obj2.Clear();
						}, true, false, 1f, (Action)null, false);
					}
					((Rect)(ref val11)).height = 200f;
					((Rect)(ref val11)).y = ((Rect)(ref val11)).y + (num8 + 10f);
					if (((Rect)(ref val11)).width >= 50f)
					{
						Rect val14 = val11;
						Pawn obj3 = pawns[i];
						Widgets.Label(val14, ((obj3 != null) ? GenText.CapitalizeFirst(obj3.KindLabel) : null) ?? "<ERROR INVALID PAWN>");
					}
				}
			}
		}
		GUI.enabled = flag;
		bool keyDown = Input.GetKeyDown((KeyCode)102);
		if ((val.ButtonText(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_FactionEdit_RegeneratePreviews")), (string)null, 1f) || (pawns.Count == 0 && !_previewFailed) || (keyDown && framesSinceF > 20)) && flag)
		{
			if (keyDown)
			{
				framesSinceF = 0;
			}
			_previewFailed = false;
			FactionDef def2 = FactionEdit.TryGetOriginal(Current.Faction.DefName) ?? Current.Faction.Def;
			clonedFac = CloningUtility.Clone(def2);
			((Def)clonedFac).defName = ((Def)Current.Faction.Def).defName;
			clonedFac.humanlikeFaction = Current.Faction.Def.humanlikeFaction;
			clonedFac.fixedName = "TEMP FACTION CLONE (" + ((Def)clonedFac).defName + ")";
			Current.Apply(clonedFac, updateDefDatabase: false);
			DestroyPawns();
			Faction val15 = new Faction
			{
				def = clonedFac,
				loadID = -1,
				colorFromSpectrum = Rand.Range(0f, 1f),
				hidden = true
			};
			FactionManager factionManager = Find.FactionManager;
			val15.ideos = ((factionManager == null) ? null : factionManager.FirstFactionOfDef(Current.Faction.Def)?.ideos);
			val15.Name = clonedFac.fixedName;
			val15.relations = Find.FactionManager.AllFactionsVisible.Select((Func<Faction, FactionRelation>)((Faction otherFaction) => new FactionRelation
			{
				other = otherFaction,
				baseGoodwill = 0,
				kind = (FactionRelationKind)1
			})).ToList();
			val15.temporary = true;
			val15.deactivated = true;
			Faction val16 = val15;
			ThingIDPatch.Active = _ThingIDPatch;
			IdeoUtilityPatch.Active = true;
			FactionUtilityPawnGenPatch.Active = true;
			foreach (PawnKindDef allPawnKind in FactionEdit.GetAllPawnKinds(clonedFac))
			{
				try
				{
					PawnGenerationRequest val17 = new PawnGenerationRequest(allPawnKind, val16, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
					((PawnGenerationRequest)(ref val17)).ForceGenerateNewPawn = true;
					((PawnGenerationRequest)(ref val17)).AllowDowned = false;
					((PawnGenerationRequest)(ref val17)).AllowDead = false;
					((PawnGenerationRequest)(ref val17)).CanGeneratePawnRelations = false;
					((PawnGenerationRequest)(ref val17)).RelationWithExtraPawnChanceFactor = 0f;
					((PawnGenerationRequest)(ref val17)).ColonistRelationChanceFactor = 0f;
					((PawnGenerationRequest)(ref val17)).ForceNoIdeo = true;
					((PawnGenerationRequest)(ref val17)).ForbidAnyTitle = true;
					Pawn item = PawnGenerator.GeneratePawn(val17);
					pawns.Add(item);
				}
				catch (Exception e3)
				{
					ModCore.Error($"Failed to generate pawn of type '{((Def)allPawnKind).LabelCap}':", e3);
					pawns.Add(null);
				}
			}
			Find.FactionManager.Remove(val16);
			ThingIDPatch.Active = false;
			FactionLeaderPatch.Active = false;
			FactionUtilityPawnGenPatch.Active = false;
			IdeoUtilityPatch.Active = false;
		}
		GUI.enabled = true;
		((Listing)val).End();
		return;
		IL_048d:
		string text13 = text2;
		if (val3.ButtonTextLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Faction_BasicMemberKind")), text13, (TextAnchor)0, (string)null, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Faction_BasicMemberKindTooltip"))))
		{
			OpenBasicMemberKindPicker(val4);
		}
		goto IL_04c4;
		IEnumerable<PawnKindDef> MakeKinds()
		{
			tempKinds.Clear();
			if (!Current.HasGlobalEditor())
			{
				tempKinds.Add(null);
			}
			foreach (PawnKindDef item4 in Current.GetAllKindDefsForUI())
			{
				if (!Current.HasEditFor(item4))
				{
					tempKinds.Add(item4);
				}
			}
			if (Current.PawnGroupMakerEdits != null && Current.Faction.Def?.fixedLeaderKinds != null)
			{
				foreach (PawnKindDef fixedLeaderKind in Current.Faction.Def.fixedLeaderKinds)
				{
					if (!Current.HasEditFor(fixedLeaderKind))
					{
						tempKinds.Add(fixedLeaderKind);
					}
				}
			}
			foreach (PawnKindDef tempKind in tempKinds)
			{
				yield return tempKind;
			}
			if (tempKinds.Count((PawnKindDef k) => k != null) == 0 && (Current.Faction.Def == FactionDefOf.Ancients || Current.Faction.Def == FactionDefOf.AncientsHostile))
			{
				yield return PawnKindDefOf.AncientSoldier;
				yield return PawnKindDefOf.Slave;
			}
			tempKinds.Clear();
		}
	}

	private void OpenBasicMemberKindPicker(PawnKindDef defaultBasic)
	{
		List<PawnKindDef> list = DefDatabase<PawnKindDef>.AllDefsListForReading.Where(delegate(PawnKindDef k)
		{
			RaceProperties raceProps = k.RaceProps;
			return raceProps != null && raceProps.Humanlike;
		}).OrderBy(delegate(PawnKindDef k)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			TaggedString labelCap = ((Def)k).LabelCap;
			return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
		}).ToList();
		list.Insert(0, null);
		CustomFloatMenu.Open(CustomFloatMenu.MakeItems(list, delegate(PawnKindDef k)
		{
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			if (k == null)
			{
				PawnKindDef obj = defaultBasic;
				return new MenuItemText(null, string.Format("<color=grey>{0}</color>", TranslatorFormattedStringExtensions.Translate("FactionLoadout_NotOverriden_WithDefault", NamedArgument.op_Implicit((obj != null) ? ((Def)obj).LabelCap : Translator.Translate("None")))));
			}
			string text = $"{((Def)k).LabelCap} ({((Def)k).defName})";
			string description = ((Def)k).description;
			return new MenuItemText(k, text, null, default(Color), description);
		}), delegate(MenuItemBase raw)
		{
			PawnKindDef payload = raw.GetPayload<PawnKindDef>();
			Current.BasicMemberKind = ((payload != null) ? new DefRef<PawnKindDef>(payload) : new DefRef<PawnKindDef>());
		});
	}

	private void DrawFactionClipboardToolbar(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		float x = ((Rect)(ref rect)).x;
		float y = ((Rect)(ref rect)).y;
		if (Widgets.ButtonImageFitted(new Rect(x, y, 24f, 24f), TexButton.Copy))
		{
			FactionEditClipboard.Copy(Current);
		}
		TooltipHandler.TipRegion(new Rect(x, y, 24f, 24f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_FactionClipboard_CopyTooltip")));
		x += 28f;
		if (FactionEditClipboard.HasData)
		{
			if (Widgets.ButtonImageFitted(new Rect(x, y, 24f, 24f), TexButton.Paste))
			{
				FactionEditClipboard.PasteAll(Current);
			}
			TooltipHandler.TipRegion(new Rect(x, y, 24f, 24f), TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_FactionClipboard_PasteTooltip", NamedArgument.op_Implicit(FactionEditClipboard.GetDescription()))));
		}
		else
		{
			GUI.color = Color.gray;
			Widgets.DrawTextureFitted(new Rect(x, y, 24f, 24f), (Texture)(object)TexButton.Paste, 1f, 1f);
			GUI.color = Color.white;
			TooltipHandler.TipRegion(new Rect(x, y, 24f, 24f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_Empty")));
		}
	}

	private void DrawMaterialFilter(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Expected O, but got Unknown
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Expected O, but got Unknown
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		((Rect)(ref rect)).width = 300f;
		if (Widgets.ButtonText(rect, string.Format("{0}{1}", Translator.Translate("FactionLoadout_FactionEdit_CustomMaterials"), (Current.ApparelStuffFilter == null) ? string.Format("<color=#ff4d4d>{0}</color>", Translator.Translate("No")) : string.Format("<color=#81f542>{0}</color>", Translator.Translate("Yes"))), true, true, true, (TextAnchor?)null))
		{
			filterState = new UIState();
			if (Current.ApparelStuffFilter != null)
			{
				Current.ApparelStuffFilter = null;
			}
			else
			{
				Current.ApparelStuffFilter = new ThingFilter();
				if (Current.Faction.Def.apparelStuffFilter != null)
				{
					Current.ApparelStuffFilter.CopyAllowancesFrom(Current.Faction.Def.apparelStuffFilter);
				}
			}
		}
		if (Current.ApparelStuffFilter != null)
		{
			ThingFilterUI.DoThingFilterConfigWindow(((Listing)ui).GetRect(240f, 1f), filterState, Current.ApparelStuffFilter, (ThingFilter)null, 1, (IEnumerable<ThingDef>)null, (IEnumerable<SpecialThingFilterDef>)new _003C_003Ez__ReadOnlyArray<SpecialThingFilterDef>((SpecialThingFilterDef[])(object)new SpecialThingFilterDef[4]
			{
				SpecialThingFilterDefOf.AllowDeadmansApparel,
				SpecialThingFilterDefOf.AllowNonDeadmansApparel,
				SpecialThingFilterDefOf.AllowFresh,
				DefDatabase<SpecialThingFilterDef>.GetNamed("AllowRotten", true)
			}), true, false, false, (List<ThingDef>)null, (Map)null);
		}
	}
}
