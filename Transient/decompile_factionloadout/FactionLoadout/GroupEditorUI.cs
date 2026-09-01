using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport.DrawSupport;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class GroupEditorUI : Window
{
	private readonly FactionEdit _edit;

	private readonly HashSet<int> _expanded = new HashSet<int>();

	private Vector2 _scrollPos;

	private static List<RaidStrategyDef> _allRaidStrategies;

	private static List<PawnGroupKindDef> _allGroupKinds;

	private List<PawnGroupMakerEdit> _cachedVanillaGroups;

	private readonly Dictionary<(int, string), string> _numBuffers = new Dictionary<(int, string), string>();

	private int _pendingDeleteIndex = -1;

	public override Vector2 InitialSize => new Vector2(720f, 640f);

	public static void OpenEditor(FactionEdit edit)
	{
		if (edit != null)
		{
			Find.WindowStack.Add((Window)(object)new GroupEditorUI(edit));
		}
	}

	public GroupEditorUI(FactionEdit edit)
		: base((IWindowDrawing)null)
	{
		_edit = edit;
		base.draggable = true;
		base.resizeable = true;
		base.doCloseX = true;
		base.closeOnCancel = true;
		base.closeOnClickedOutside = false;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Expected O, but got Unknown
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Unknown result type (might be due to invalid IL or missing references)
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_022b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0253: Unknown result type (might be due to invalid IL or missing references)
		//IL_025d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0303: Unknown result type (might be due to invalid IL or missing references)
		//IL_030a: Expected O, but got Unknown
		//IL_030c: Unknown result type (might be due to invalid IL or missing references)
		//IL_031e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0357: Unknown result type (might be due to invalid IL or missing references)
		//IL_035c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0366: Unknown result type (might be due to invalid IL or missing references)
		//IL_0337: Unknown result type (might be due to invalid IL or missing references)
		//IL_033c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0346: Unknown result type (might be due to invalid IL or missing references)
		//IL_0371: Unknown result type (might be due to invalid IL or missing references)
		//IL_0377: Unknown result type (might be due to invalid IL or missing references)
		//IL_0386: Unknown result type (might be due to invalid IL or missing references)
		//IL_039c: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03bc: Unknown result type (might be due to invalid IL or missing references)
		if (_edit == null || _edit.DeletedOrClosed)
		{
			((Window)this).Close(true);
			return;
		}
		List<PawnGroupMakerEdit> pawnGroupMakerEdits = _edit.PawnGroupMakerEdits;
		bool flag = pawnGroupMakerEdits == null;
		List<PawnGroupMakerEdit> list;
		if (flag)
		{
			if (_cachedVanillaGroups == null)
			{
				_cachedVanillaGroups = (FactionEdit.TryGetOriginal(_edit.Faction.DefName) ?? _edit.Faction.Def)?.pawnGroupMakers?.Select(PawnGroupMakerEdit.FromPawnGroupMaker).ToList();
			}
			list = _cachedVanillaGroups;
		}
		else
		{
			_cachedVanillaGroups = null;
			list = pawnGroupMakerEdits;
		}
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		Rect rect = ((Listing)val).GetRect(36f, 1f);
		Text.Font = (GameFont)2;
		FactionDef def = _edit.Faction.Def;
		Widgets.Label(rect, TranslatorFormattedStringExtensions.Translate("FactionLoadout_GroupEditor_Title", NamedArgument.op_Implicit((def != null) ? ((Def)def).LabelCap : TaggedString.op_Implicit(_edit.Faction.DefName))));
		Text.Font = (GameFont)1;
		GUI.color = Color.grey;
		val.Label("<i>" + Translator.Translate("FactionLoadout_GroupEditor_HelpText") + "</i>", -1f, (string)null);
		GUI.color = Color.white;
		((Listing)val).GapLine(12f);
		Rect rect2 = ((Listing)val).GetRect(28f, 1f);
		float num = 160f;
		GUI.color = Color.green;
		if (flag)
		{
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y, num, 24f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_CustomizeGroups")), true, true, true, (TextAnchor?)null))
			{
				_edit.GetOrInitPawnGroupMakerEdits();
			}
		}
		else if (Widgets.ButtonText(new Rect(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y, num, 24f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_AddGroup")), true, true, true, (TextAnchor?)null))
		{
			OpenAddGroupMenu();
		}
		GUI.color = (flag ? Color.grey : Color.white);
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect2)).xMax - 200f, ((Rect)(ref rect2)).y, 200f, 24f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_ResetButton")), true, true, true, (TextAnchor?)null) && !flag)
		{
			OpenResetConfirm();
		}
		GUI.color = Color.white;
		float num2 = Mathf.Max(60f, ((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 8f);
		Rect rect3 = ((Listing)val).GetRect(num2, 1f);
		float num3 = CalcTotalContentHeight(list) + 20f;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref rect3)).width - 16f, Mathf.Max(num3, num2));
		Widgets.BeginScrollView(rect3, ref _scrollPos, val2, true);
		Listing_Standard val3 = new Listing_Standard();
		((Listing)val3).Begin(val2);
		if (list == null || list.Count == 0)
		{
			GUI.color = Color.grey;
			val3.Label(flag ? ("<i>" + Translator.Translate("FactionLoadout_GroupEditor_VanillaGroups") + "</i>") : ("<i>(" + Translator.Translate("FactionLoadout_GroupEditor_NoPawns") + ")</i>"), -1f, (string)null);
			GUI.color = Color.white;
		}
		else
		{
			if (flag)
			{
				GUI.color = Color.grey;
				val3.Label("<i>" + Translator.Translate("FactionLoadout_GroupEditor_VanillaGroups") + "</i>", -1f, (string)null);
				GUI.color = Color.white;
				((Listing)val3).Gap(4f);
			}
			DrawGroupList(val3, list, flag);
		}
		((Listing)val3).End();
		Widgets.EndScrollView();
		((Listing)val).End();
	}

	private float CalcTotalContentHeight(List<PawnGroupMakerEdit> groups)
	{
		if (groups == null || groups.Count == 0)
		{
			return 30f;
		}
		float num = 0f;
		for (int i = 0; i < groups.Count; i++)
		{
			num += 28f;
			if (_expanded.Contains(i))
			{
				num += CalcExpandedGroupHeight(groups[i]);
				num += 12f;
			}
		}
		return num;
	}

	private static float CalcExpandedGroupHeight(PawnGroupMakerEdit group)
	{
		return 0f + 28f + 28f + 28f + 28f + 12f + PawnListDrawer.CalcHeight(group.Options) + PawnListDrawer.CalcHeight(group.Guards) + PawnListDrawer.CalcHeight(group.Traders) + PawnListDrawer.CalcHeight(group.Carriers) + 4f;
	}

	private void DrawGroupList(Listing_Standard ui, List<PawnGroupMakerEdit> groups, bool readOnly)
	{
		if (_pendingDeleteIndex >= 0 && _pendingDeleteIndex < groups.Count)
		{
			int idx = _pendingDeleteIndex;
			groups.RemoveAt(idx);
			_expanded.Remove(idx);
			foreach (int item in _expanded.Where((int x) => x > idx).ToList())
			{
				_expanded.Remove(item);
				_expanded.Add(item - 1);
			}
			_numBuffers.Clear();
		}
		_pendingDeleteIndex = -1;
		for (int i = 0; i < groups.Count; i++)
		{
			PawnGroupMakerEdit group = groups[i];
			bool flag = _expanded.Contains(i);
			DrawGroupHeader(ui, group, i, flag, readOnly);
			if (flag)
			{
				DrawGroupBody(ui, group, i, readOnly);
			}
		}
	}

	private void DrawGroupHeader(Listing_Standard ui, PawnGroupMakerEdit group, int index, bool expanded, bool readOnly)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0288: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Widgets.DrawHighlightIfMouseover(rect);
		string text = (expanded ? "▼" : "▶");
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y + 2f, 20f, 24f), text, false, true, true, (TextAnchor?)null))
		{
			if (expanded)
			{
				_expanded.Remove(index);
			}
			else
			{
				_expanded.Add(index);
			}
		}
		if (!readOnly)
		{
			int capturedIndex = index;
			Rect val = new Rect(((Rect)(ref rect)).xMax - 28f, ((Rect)(ref rect)).y + 2f, 24f, 24f);
			GUI.color = Color.red;
			if (Widgets.ButtonText(val, "×", true, true, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)Dialog_MessageBox.CreateConfirmation(Translator.Translate("FactionLoadout_GroupEditor_DeleteConfirmBody"), (Action)delegate
				{
					_pendingDeleteIndex = capturedIndex;
				}, true, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_DeleteConfirmTitle")), (WindowLayer)1));
			}
			GUI.color = Color.white;
		}
		float num = (readOnly ? 4f : 32f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + 24f, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - 24f - num, ((Rect)(ref rect)).height);
		string text2 = ((Def)(group.KindDef?)).label ?? group.KindDefName;
		if (string.IsNullOrEmpty(text2))
		{
			text2 = "?";
		}
		string text3 = (group.IsNew ? string.Format(" <color=#ffd700>{0}</color>", Translator.Translate("FactionLoadout_GroupEditor_NewTag")) : "");
		string text4 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_GroupEditor_PawnCount", NamedArgument.op_Implicit(group.TotalKindCount)));
		string text5 = ((group.TotalKindCount == 0) ? string.Format("  <color=#ff9900>{0}</color>", Translator.Translate("FactionLoadout_GroupEditor_EmptyWarning")) : "");
		string text6 = ((group.MaxTotalPoints >= 9999999f) ? "" : $"  max {group.MaxTotalPoints:0}");
		string text7 = $"<b>{text2}</b>{text3}  <color=grey>commonality {group.Commonality:0}{text6}  {text4}</color>{text5}";
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val2, text7);
		Text.Anchor = (TextAnchor)0;
		if (group.TotalKindCount == 0)
		{
			TooltipHandler.TipRegion(val2, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_EmptyGroupTooltip")));
		}
		if (Widgets.ButtonInvisible(new Rect(((Rect)(ref rect)).x + 24f, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - 24f - num, ((Rect)(ref rect)).height), true))
		{
			if (expanded)
			{
				_expanded.Remove(index);
			}
			else
			{
				_expanded.Add(index);
			}
		}
	}

	private void DrawGroupBody(Listing_Standard ui, PawnGroupMakerEdit group, int groupIndex, bool readOnly)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Expected O, but got Unknown
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0273: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0308: Unknown result type (might be due to invalid IL or missing references)
		//IL_0317: Unknown result type (might be due to invalid IL or missing references)
		//IL_0345: Unknown result type (might be due to invalid IL or missing references)
		//IL_0354: Unknown result type (might be due to invalid IL or missing references)
		//IL_0363: Unknown result type (might be due to invalid IL or missing references)
		//IL_0391: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03af: Unknown result type (might be due to invalid IL or missing references)
		//IL_03dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_03fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0451: Unknown result type (might be due to invalid IL or missing references)
		//IL_046a: Unknown result type (might be due to invalid IL or missing references)
		//IL_047c: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(0f, 1f);
		float y = ((Rect)(ref rect)).y;
		Listing_Standard val = new Listing_Standard();
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Listing)ui).curX + 16f, y, ((Listing)ui).ColumnWidth - 16f, 9999f);
		((Listing)val).Begin(val2);
		if (readOnly)
		{
			LabeledRowDrawer.DrawLabeledText(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_GroupType")), ((Def)(group.KindDef?)).label ?? group.KindDefName);
		}
		else
		{
			LabeledRowDrawer.DrawLabeledButton(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_GroupType")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_GroupTypeTooltip")), ((Def)(group.KindDef?)).label ?? group.KindDefName, delegate
			{
				EnsureGroupKinds();
				FloatMenuUtility.MakeMenu<PawnGroupKindDef>((IEnumerable<PawnGroupKindDef>)_allGroupKinds, (Func<PawnGroupKindDef, string>)((PawnGroupKindDef gk) => ((Def)gk).label + " (" + ((Def)gk).defName + ")"), (Func<PawnGroupKindDef, Action>)((PawnGroupKindDef gk) => delegate
				{
					group.KindDefName = ((Def)gk).defName;
				}));
			});
		}
		if (readOnly)
		{
			LabeledRowDrawer.DrawLabeledText(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_Commonality")), group.Commonality.ToString("0.##"));
		}
		else
		{
			group.Commonality = DrawLabeledFloat(val, groupIndex, "commonality", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_Commonality")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_CommonalityTooltip")), group.Commonality, 0f);
		}
		if (readOnly)
		{
			string value = ((group.MaxTotalPoints >= 9999999f) ? "∞" : group.MaxTotalPoints.ToString("0"));
			LabeledRowDrawer.DrawLabeledText(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_MaxPoints")), value);
		}
		else
		{
			group.MaxTotalPoints = DrawLabeledFloat(val, groupIndex, "maxPoints", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_MaxPoints")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_MaxPointsTooltip")), group.MaxTotalPoints, 0f);
		}
		string text;
		if (group.DisallowedStrategyDefNames != null && group.DisallowedStrategyDefNames.Count != 0)
		{
			text = string.Join(", ", group.DisallowedStrategyDefNames.Select((string n) => ((Def)(DefDatabase<RaidStrategyDef>.GetNamedSilentFail(n)?)).label ?? n));
		}
		else
		{
			TaggedString val3 = Translator.Translate("FactionLoadout_GroupEditor_BlockStrategiesNone");
			text = ((object)(TaggedString)(ref val3)/*cast due to .constrained prefix*/).ToString();
		}
		string value2 = text;
		if (readOnly)
		{
			LabeledRowDrawer.DrawLabeledText(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_BlockStrategies")), value2);
		}
		else
		{
			LabeledRowDrawer.DrawLabeledButton(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_BlockStrategies")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_BlockStrategiesTooltip")), value2, delegate
			{
				OpenStrategyMenu(group);
			});
		}
		((Listing)val).GapLine(12f);
		PawnListDrawer.Draw(val, groupIndex, "options", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_CombatPawns")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_CombatPawnsTooltip")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_AddCombatPawn")), group.Options, readOnly, _numBuffers);
		PawnListDrawer.Draw(val, groupIndex, "guards", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_Guards")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_GuardsTooltip")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_AddGuard")), group.Guards, readOnly, _numBuffers);
		PawnListDrawer.Draw(val, groupIndex, "traders", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_Traders")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_TradersTooltip")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_AddTrader")), group.Traders, readOnly, _numBuffers);
		PawnListDrawer.Draw(val, groupIndex, "carriers", TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_Carriers")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_CarriersTooltip")), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_AddCarrier")), group.Carriers, readOnly, _numBuffers);
		((Listing)val).Gap(4f);
		float curHeight = ((Listing)val).CurHeight;
		((Listing)val).End();
		Widgets.DrawBoxSolid(new Rect(((Listing)ui).curX + 16f, y, ((Listing)ui).ColumnWidth - 16f, curHeight), new Color(1f, 1f, 1f, 0.04f));
		((Listing)ui).GetRect(curHeight, 1f);
		((Listing)ui).GapLine(12f);
	}

	private float DrawLabeledFloat(Listing_Standard ui, int groupIndex, string fieldId, string label, string tooltip, float value, float min)
	{
		if (!_numBuffers.TryGetValue((groupIndex, fieldId), out var value2))
		{
			value2 = value.ToString("0.##");
		}
		float result = LabeledRowDrawer.DrawLabeledFloat(ui, label, tooltip, ref value2, value, min);
		_numBuffers[(groupIndex, fieldId)] = value2;
		return result;
	}

	private void OpenAddGroupMenu()
	{
		EnsureGroupKinds();
		FloatMenuUtility.MakeMenu<PawnGroupKindDef>((IEnumerable<PawnGroupKindDef>)_allGroupKinds, (Func<PawnGroupKindDef, string>)((PawnGroupKindDef gk) => ((Def)gk).label + " (" + ((Def)gk).defName + ")"), (Func<PawnGroupKindDef, Action>)((PawnGroupKindDef gk) => delegate
		{
			List<PawnGroupMakerEdit> orInitPawnGroupMakerEdits = _edit.GetOrInitPawnGroupMakerEdits();
			PawnGroupMakerEdit item = new PawnGroupMakerEdit
			{
				IsUserAdded = true,
				KindDefName = ((Def)gk).defName
			};
			orInitPawnGroupMakerEdits.Add(item);
			_expanded.Add(orInitPawnGroupMakerEdits.Count - 1);
		}));
	}

	private void OpenStrategyMenu(PawnGroupMakerEdit group)
	{
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Expected O, but got Unknown
		EnsureRaidStrategies();
		PawnGroupMakerEdit pawnGroupMakerEdit = group;
		if (pawnGroupMakerEdit.DisallowedStrategyDefNames == null)
		{
			pawnGroupMakerEdit.DisallowedStrategyDefNames = new List<string>();
		}
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		list.AddRange(from strat in _allRaidStrategies
			let current = @group.DisallowedStrategyDefNames.Contains(((Def)strat).defName)
			let mark = current ? "✓ " : "   "
			let stratDef = ((Def)strat).defName
			select new FloatMenuOption(mark + (((Def)strat).label ?? ((Def)strat).defName), (Action)delegate
			{
				if (@group.DisallowedStrategyDefNames.Contains(stratDef))
				{
					@group.DisallowedStrategyDefNames.Remove(stratDef);
				}
				else
				{
					@group.DisallowedStrategyDefNames.Add(stratDef);
				}
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}

	private void OpenResetConfirm()
	{
		Find.WindowStack.Add((Window)(object)new Dialog_ResetGroupsConfirm(_edit));
	}

	private static void EnsureGroupKinds()
	{
		if (_allGroupKinds == null)
		{
			_allGroupKinds = DefDatabase<PawnGroupKindDef>.AllDefsListForReading.OrderBy((PawnGroupKindDef gk) => ((Def)gk).label ?? ((Def)gk).defName).ToList();
		}
	}

	private static void EnsureRaidStrategies()
	{
		if (_allRaidStrategies == null)
		{
			_allRaidStrategies = DefDatabase<RaidStrategyDef>.AllDefsListForReading.OrderBy((RaidStrategyDef rs) => ((Def)rs).label ?? ((Def)rs).defName).ToList();
		}
	}
}
