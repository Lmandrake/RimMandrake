using System;
using System.Collections;
using System.Collections.Generic;
using FactionLoadout.UISupport.DrawSupport;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public abstract class EditTab : Tab
{
	public readonly PawnKindEdit Current;

	public readonly PawnKindDef DefaultKind;

	protected Vector2[] scrolls = (Vector2[])(object)new Vector2[64];

	protected string[] buffers = new string[64];

	protected List<(string x, string y)>[] curvePointBuffers = new List<(string, string)>[64];

	protected int scrollIndex;

	protected int bufferIndex;

	protected int curveIndex;

	protected EditTab(string name, PawnKindEdit current, PawnKindDef defaultKind)
		: base(name, null)
	{
		Current = current;
		DefaultKind = defaultKind;
	}

	public override void Draw(Listing_Standard ui)
	{
		scrollIndex = 0;
		bufferIndex = 0;
		curveIndex = 0;
		Tab.DrawRegionTitle(ui, Name);
		DrawContents(ui);
	}

	protected abstract void DrawContents(Listing_Standard ui);

	public void ResetBuffers()
	{
		buffers = new string[64];
		scrolls = (Vector2[])(object)new Vector2[64];
		curvePointBuffers = new List<(string, string)>[64];
	}

	public void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T? field, string label, Action<Rect, bool, T> drawContent, float height = 32f, Func<PawnKindEdit, T?> pasteGet = null) where T : struct
	{
		OverrideDrawSupport.DrawOverride(ui, defaultValue, ref field, label, drawContent, height, pasteGet, ResetBuffers);
	}

	public void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T field, string label, Action<Rect, bool, T> drawContent, float height = 32f, Func<PawnKindEdit, T> pasteGet = null) where T : class
	{
		OverrideDrawSupport.DrawOverride(ui, defaultValue, ref field, label, drawContent, height, pasteGet, ResetBuffers);
	}

	public void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T field, string label, Action<Rect, bool, T> drawContent, float height = 32f, bool cloneDefault = true, Func<PawnKindEdit, T> pasteGet = null) where T : IList
	{
		OverrideDrawSupport.DrawOverride(ui, defaultValue, ref field, label, drawContent, height, cloneDefault, pasteGet, ResetBuffers);
	}

	protected CustomFloatMenu DrawDefRefList<T>(Rect rect, bool active, ref Vector2 scroll, IList<DefRef<T>> current, IList<T> defaults, IEnumerable<T> allDefs, Func<T, MenuItemBase> makeItem = null, Func<T, string> labelFunc = null, Func<T, string> warningFunc = null) where T : Def, new()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		return ListDrawSupport.DrawDefRefList(rect, active, ref scroll, current, defaults, allDefs, Current.IsGlobal, makeItem, labelFunc, warningFunc);
	}

	protected CustomFloatMenu DrawDefList<T>(Rect rect, bool active, ref Vector2 scroll, IList<T> current, IList<T> defaultThings, IEnumerable<T> allThings, bool allowDupes, Func<T, MenuItemBase> makeItems = null) where T : Def
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		return ListDrawSupport.DrawDefList(rect, active, ref scroll, current, defaultThings, allThings, allowDupes, Current.IsGlobal, makeItems);
	}

	protected void DrawColorList(Rect rect, bool active, ref Vector2 scroll, IList<Color> current, IList<Color> defaultColors)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		ListDrawSupport.DrawColorList(rect, active, ref scroll, current, defaultColors, Current.IsGlobal);
	}

	protected void DrawStringList(Rect rect, bool active, ref Vector2 scroll, IList<string> current, IList<string> defaultTags, IEnumerable<string> allTags)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		ListDrawSupport.DrawStringList(rect, active, ref scroll, current, defaultTags, allTags, Current.IsGlobal);
	}

	protected void DrawEnumSelector<T>(Rect rect, bool active, T? field, T defaultValue, Action<T> apply, Func<T, string> makeName = null) where T : struct
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		ValueDrawSupport.DrawEnumSelector(rect, active, Current.IsGlobal, field, defaultValue, apply, makeName);
	}

	protected void DrawDefSelector<T>(Rect rect, bool active, IEnumerable<T> defs, T field, T defaultValue, Action<T> apply, Func<T, string> makeName = null) where T : Def
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		ValueDrawSupport.DrawDefSelector(rect, active, Current.IsGlobal, defs, field, defaultValue, apply, makeName);
	}

	protected void DrawChance(ref float? field, float defaultValue, Rect rect, bool active)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		ValueDrawSupport.DrawChance(rect, active, Current.IsGlobal, ref field, defaultValue);
	}

	protected void DrawIntRange(Rect rect, bool active, ref IntRange? current, IntRange defaultRange, ref string buffer, ref string buffer2)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		ValueDrawSupport.DrawIntRange(rect, active, Current.IsGlobal, ref current, defaultRange, ref buffer, ref buffer2);
	}

	protected void DrawFloatRange(Rect rect, bool active, ref FloatRange? current, FloatRange defaultRange, ref string buffer, ref string buffer2)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		ValueDrawSupport.DrawFloatRange(rect, active, Current.IsGlobal, ref current, defaultRange, ref buffer, ref buffer2);
	}

	protected float GetHeightFor(IList list, float itemHeight = 26f)
	{
		return ValueDrawSupport.GetHeightFor(list, itemHeight);
	}

	protected void DrawSpecificGear(Listing_Standard ui, ref List<SpecRequirementEdit> edits, string label, Func<ThingDef, bool> thingFilter, ThingDef defaultThing)
	{
		SpecificGearDrawer.Draw(ui, ref edits, label, thingFilter, defaultThing, ref scrolls[scrollIndex++]);
	}

	protected Rect DrawMaterialModeToggle(Rect rect, ref bool isBlocklist)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		string text = TaggedString.op_Implicit(isBlocklist ? Translator.Translate("FactionLoadout_Materials_ModeBlocklist") : Translator.Translate("FactionLoadout_Materials_ModeAllowlist"));
		Rect val = rect;
		((Rect)(ref val)).height = 24f;
		((Rect)(ref val)).width = Mathf.Min(((Rect)(ref rect)).width, Mathf.Max(180f, Text.CalcSize(text).x + 24f));
		if (Widgets.ButtonText(val, text, true, true, true, (TextAnchor?)null))
		{
			isBlocklist = !isBlocklist;
		}
		Rect result = rect;
		((Rect)(ref result)).yMin = ((Rect)(ref result)).yMin + 26f;
		return result;
	}

	protected void DrawMaterialSummary(Listing_Standard ui, List<DefRef<ThingDef>> materials, bool isBlocklist)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		if (materials != null)
		{
			string text = DefCache.MaterialCategorySummary(materials, isBlocklist);
			if (!string.IsNullOrEmpty(text))
			{
				GUI.color = new Color(0.62f, 0.78f, 1f);
				ui.Label(TranslatorFormattedStringExtensions.Translate("FactionLoadout_Materials_AllowedSummary", NamedArgument.op_Implicit(text)), -1f, (string)null);
				GUI.color = Color.white;
			}
		}
	}

	public void DrawCurve(Listing_Standard listing, ref SimpleCurve curve, ref List<(string x, string y)> curvePointBuffer)
	{
		CurveDrawer.DrawCurve(listing, ref curve, ref curvePointBuffer);
	}
}
