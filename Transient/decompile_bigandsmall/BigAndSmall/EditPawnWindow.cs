using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace BigAndSmall;

public class EditPawnWindow : Window
{
	public class ThingGData
	{
		public const string DEFAULT = "DEFAULT";

		public readonly Thing thing = thing;

		public Dictionary<string, SectionData> customData = new Dictionary<string, SectionData>();

		public readonly Def def = def;

		public readonly WindowTab editMode = editMode;

		public SectionData TryGetGeneric
		{
			get
			{
				if (!customData.TryGetValue("DEFAULT", out var value))
				{
					return null;
				}
				return value;
			}
		}

		public ThingGData(Thing thing, WindowTab editMode, Def def = null)
		{
		}

		public SectionData GetOrAddGeneric()
		{
			if (!customData.TryGetValue("DEFAULT", out var value))
			{
				return customData["DEFAULT"] = new SectionData(null, editMode);
			}
			return value;
		}
	}

	public class SectionData
	{
		public WindowTab tab = editMode;

		public readonly FlagString flag = flag;

		public bool colorA;

		public bool colorB;

		public bool colorC;

		public List<FlagString> customFlags = new List<FlagString>();

		public bool HasMultipleClrs => (colorA ? 1 : 0) + (colorB ? 1 : 0) + (colorC ? 1 : 0) > 1;

		public SectionData(FlagString flag, WindowTab editMode)
		{
		}
	}

	public enum WindowTab
	{
		Thing,
		Apparel,
		CustomTag
	}

	private readonly ILoadReferenceable target;

	private static readonly Vector2 ButtonSize = new Vector2(200f, 40f);

	private int selectedTab;

	private WindowTab activeTab;

	private readonly List<WindowTab> tabsWithContent = new List<WindowTab>();

	private readonly Dictionary<Thing, ThingGData> EditableThings = new Dictionary<Thing, ThingGData>();

	private readonly Dictionary<(string, FlagString), SectionData> CSectionBuilder = new Dictionary<(string, FlagString), SectionData>();

	private readonly Dictionary<string, List<SectionData>> CustomSections = new Dictionary<string, List<SectionData>>();

	private readonly Pawn pawn;

	private readonly Thing thing;

	private readonly List<Color> extraColors;

	private readonly Dictionary<Thing, List<ThingStyleDef>> apparelStyles = new Dictionary<Thing, List<ThingStyleDef>>();

	private Vector2 scrollPosition = Vector2.zero;

	private float scrollViewHeight;

	private const string NONE = "NONE";

	public static bool queuedUpdate = false;

	private string[] _tabs;

	public bool draggingSlider;

	public bool draggingWheel;

	public override Vector2 InitialSize => new Vector2(600f, 800f);

	protected override void SetInitialSizeAndPosition()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).SetInitialSizeAndPosition();
		((Rect)(ref base.windowRect)).x = ((Rect)(ref base.windowRect)).x - ((Window)this).InitialSize.x;
	}

	private static WindowTab EditModeFrom(HasCustomizableGraphics cg, WindowTab @default)
	{
		return FlagStringData.DataFor(cg?.Flag).displayTab ?? @default;
	}

	public EditPawnWindow(ILoadReferenceable target)
		: base((IWindowDrawing)null)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		thing = (Thing)(object)((target is Thing) ? target : null);
		if (thing == null)
		{
			return;
		}
		pawn = (Pawn)(object)((target is Pawn) ? target : null);
		_tabs = null;
		tabsWithContent = new List<WindowTab>(1) { WindowTab.Thing };
		EditableThings = new Dictionary<Thing, ThingGData>();
		apparelStyles.Clear();
		this.target = target;
		base.forcePause = false;
		base.absorbInputAroundWindow = false;
		base.closeOnClickedOutside = false;
		base.closeOnAccept = false;
		base.closeOnCancel = true;
		base.doCloseX = true;
		base.preventCameraMotion = false;
		base.resizeable = true;
		base.draggable = true;
		if (ModsConfig.IdeologyActive)
		{
			extraColors = new List<Color>();
			Ideo ideo = pawn.Ideo;
			if (ideo != null)
			{
				extraColors.Add(ideo.Color);
			}
			ColorDef val = pawn.story?.favoriteColor;
			if (val != null)
			{
				extraColors.Add(val.color);
			}
		}
		AddEditable(null, WindowTab.Thing);
		if (pawn != null)
		{
			foreach (Thing equippedWornOrInventoryThing in pawn.EquippedWornOrInventoryThings)
			{
				Apparel val2 = (Apparel)(object)((equippedWornOrInventoryThing is Apparel) ? equippedWornOrInventoryThing : null);
				if (val2 != null)
				{
					AddWornItem((Thing)(object)val2);
				}
				else
				{
					AddWornItem(equippedWornOrInventoryThing);
				}
			}
			if (ModsConfig.BiotechActive && pawn.genes != null)
			{
				foreach (Gene allActiveGene in pawn.GetAllActiveGenes())
				{
					List<HasCustomizableGraphics> list = allActiveGene.def.ExtensionsOnDef<HasCustomizableGraphics, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true);
					if (list.Count != 0)
					{
						AddEditable(list, WindowTab.CustomTag);
					}
				}
			}
			foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
			{
				List<HasCustomizableGraphics> list2 = hediff.def.ExtensionsOnDef<HasCustomizableGraphics, HediffDef>((List<Type>)null, (List<Type>)null, doSort: true);
				if (list2.Count != 0)
				{
					AddEditable(list2, WindowTab.CustomTag);
				}
			}
		}
		tabsWithContent = tabsWithContent.Distinct().ToList();
		CustomSections = (from x in CSectionBuilder.Values
			group x by x.flag.CustomCategory ?? "NONE").ToDictionary((IGrouping<string, SectionData> g) => g.Key, (IGrouping<string, SectionData> g) => g.ToList());
	}

	private void AddWornItem(Thing item)
	{
		List<HasCustomizableGraphics> list = item.def.ExtensionsOnDef<HasCustomizableGraphics, ThingDef>((List<Type>)null, (List<Type>)null, doSort: true);
		if (ThingStyleHelper.CanBeStyled(item.def))
		{
			List<ThingStyleDef> list2 = new List<ThingStyleDef>();
			foreach (StyleCategoryDef allDef in DefDatabase<StyleCategoryDef>.AllDefs)
			{
				foreach (ThingDefStyle thingDefStyle in allDef.thingDefStyles)
				{
					if (thingDefStyle.ThingDef == item.def)
					{
						list2.Add(thingDefStyle.StyleDef);
					}
				}
			}
			if (list2.Count != 0)
			{
				apparelStyles[item] = list2;
			}
		}
		if (list.Count != 0)
		{
			_ = list[0];
			AddEditable(list, WindowTab.Apparel, item);
			return;
		}
		Apparel val = (Apparel)(object)((item is Apparel) ? item : null);
		if (val != null && val.WornGraphicPath != null)
		{
			AddEditable(null, WindowTab.Apparel, item);
			tabsWithContent.Add(WindowTab.Apparel);
			return;
		}
		ThingWithComps val2 = (ThingWithComps)(object)((item is ThingWithComps) ? item : null);
		if (val2 != null && GenCollection.Any<ThingComp>(val2.AllComps, (Predicate<ThingComp>)((ThingComp x) => x is CompStyleable)))
		{
			AddEditable(null, WindowTab.Apparel, item);
			tabsWithContent.Add(WindowTab.Apparel);
		}
		else
		{
			Log.Message($"[BigAndSmall] Tried to edit apparel {item} but it has no graphics extension or worn graphic path.");
		}
	}

	private void AddEditable(List<HasCustomizableGraphics> cgList, WindowTab defaultMode, Thing overrideThing = null)
	{
		Thing val = overrideThing ?? thing;
		ThingGData data2 = GetMakeMainSection(defaultMode, val);
		if (GenList.NullOrEmpty<HasCustomizableGraphics>((IList<HasCustomizableGraphics>)cgList))
		{
			return;
		}
		cgList = cgList.OrderByDescending((HasCustomizableGraphics cg) => (cg?.Flag == null) ? 1 : 0).ToList();
		foreach (HasCustomizableGraphics cg in cgList)
		{
			FlagString flagString = cg?.Flag;
			if ((object)flagString != null)
			{
				string item = flagString.CustomCategory ?? "NONE";
				if (!CSectionBuilder.TryGetValue((item, flagString), out var value))
				{
					WindowTab windowTab = cg.Flag.DisplayTab ?? defaultMode;
					tabsWithContent.Add(windowTab);
					value = (CSectionBuilder[(item, flagString)] = new SectionData(flagString, windowTab));
				}
				value.colorA |= cg.colorA;
				value.colorB |= cg.colorB;
				value.colorC |= cg.colorC;
				value.customFlags.AddRange(cg.customFlags);
				value.customFlags.Distinct();
			}
			else
			{
				PopulateShared(cg, data2);
			}
		}
		ThingGData GetMakeMainSection(WindowTab defaultMode, Thing target)
		{
			tabsWithContent.Add(defaultMode);
			if (!EditableThings.TryGetValue(target, out var value2))
			{
				value2 = (EditableThings[target] = new ThingGData(target, defaultMode));
				SectionData orAddGeneric = value2.GetOrAddGeneric();
				if (target is Pawn && defaultMode == WindowTab.Thing)
				{
					orAddGeneric.colorA = true;
					orAddGeneric.colorB = true;
					orAddGeneric.colorC = true;
				}
			}
			return value2;
		}
		static void PopulateShared(HasCustomizableGraphics cg, ThingGData data)
		{
			SectionData orAddGeneric2 = data.GetOrAddGeneric();
			orAddGeneric2.colorA |= cg.colorA;
			orAddGeneric2.colorB |= cg.colorB;
			orAddGeneric2.colorC |= cg.colorC;
			orAddGeneric2.customFlags.AddRange(cg.customFlags);
			orAddGeneric2.customFlags.Distinct();
		}
	}

	private string[] GetTabKeys()
	{
		return _tabs ?? (_tabs = tabsWithContent.Select((WindowTab x) => $"BS_Tab_{x}").ToArray().ToArray());
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_022f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0234: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_0276: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_031d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Expected O, but got Unknown
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Expected O, but got Unknown
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		if (((Rect)(ref inRect)).width < 400f)
		{
			((Rect)(ref inRect)).width = 400f;
		}
		UIRoot uIRoot = Find.UIRoot;
		UIRoot_Play val = (UIRoot_Play)(object)((uIRoot is UIRoot_Play) ? uIRoot : null);
		if (val != null && val.mapUI != null && Find.Selector.NumSelected == 1)
		{
			Thing singleSelectedThing = Find.Selector.SingleSelectedThing;
			Pawn val2 = (Pawn)(object)((singleSelectedThing is Pawn) ? singleSelectedThing : null);
			if (val2 != null && val2 != pawn)
			{
				EditPawnWindow editPawnWindow = new EditPawnWindow((ILoadReferenceable)(object)val2)
				{
					selectedTab = selectedTab
				};
				Find.WindowStack.Add((Window)(object)editPawnWindow);
				((Window)editPawnWindow).windowRect = base.windowRect;
				((Window)this).Close(true);
				return;
			}
		}
		if (queuedUpdate && pawn != null)
		{
			queuedUpdate = false;
			pawn.Drawer.renderer.SetAllGraphicsDirty();
		}
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y + 35f - 4f, ((Rect)(ref inRect)).width, 35f);
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y + 30f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 30f - 40f);
		Widgets.DrawMenuSection(val4);
		string[] tabKeys = GetTabKeys();
		int num = tabKeys.Length;
		List<TabRecord> list = new List<TabRecord>();
		for (int i = 0; i < num; i++)
		{
			int tabIndex = i;
			if (tabKeys[i] == "BS_Tab_Thing")
			{
				list.Add(new TabRecord(((object)target).ToString(), (Action)delegate
				{
					selectedTab = tabIndex;
				}, selectedTab == tabIndex));
			}
			else
			{
				list.Add(new TabRecord(TaggedString.op_Implicit(Translator.Translate(tabKeys[i])), (Action)delegate
				{
					selectedTab = tabIndex;
				}, selectedTab == tabIndex));
			}
		}
		TabDrawer.DrawTabs<TabRecord>(val3, list, 200f);
		try
		{
			activeTab = tabsWithContent[selectedTab];
		}
		catch (ArgumentOutOfRangeException)
		{
			selectedTab = 0;
			activeTab = tabsWithContent[selectedTab];
		}
		Rect rect = GenUI.ContractedBy(val4, 12f);
		DrawMainUI(rect, activeTab);
		List<(string, Action)> list2 = new List<(string, Action)>(2)
		{
			(TaggedString.op_Implicit(Translator.Translate("BS_Reset_Custom")), delegate
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
				ClearAll();
			}),
			(TaggedString.op_Implicit(Translator.Translate("Close")), delegate
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
				((Window)this).Close(true);
			})
		};
		if (!BigSmallMod.settings.makeDefsRecolorable)
		{
			list2.Insert(0, (TaggedString.op_Implicit(Translator.Translate("BS_RecolourAnything")), delegate
			{
				BigSmallMod.settings.makeDefsRecolorable = true;
				((ModSettings)BigSmallMod.settings).Write();
				RenderNodePatcher.TryPatchPawnRenderNodeDefs();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
			}));
		}
		else
		{
			list2.Insert(0, (TaggedString.op_Implicit(Translator.Translate("BS_RecolourAnythingDisable")), delegate
			{
				//IL_002a: Unknown result type (might be due to invalid IL or missing references)
				//IL_0034: Unknown result type (might be due to invalid IL or missing references)
				//IL_0046: Unknown result type (might be due to invalid IL or missing references)
				//IL_0050: Expected O, but got Unknown
				BigSmallMod.settings.makeDefsRecolorable = false;
				((ModSettings)BigSmallMod.settings).Write();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
				Find.WindowStack.Add((Window)new Dialog_MessageBox(Translator.Translate("BS_RestartRequired"), TaggedString.op_Implicit(Translator.Translate("OK")), (Action)null, (string)null, (Action)null, (string)null, false, (Action)null, (Action)null, (WindowLayer)1));
			}));
		}
		MakeBottomButtons(inRect, list2);
	}

	private void MakeBottomButtons(Rect inRect, List<(string, Action)> buttons)
	{
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		if (buttons == null || buttons.Count == 0)
		{
			return;
		}
		float num = 10f;
		float num2 = num * (float)(buttons.Count - 1);
		float num3 = ((Rect)(ref inRect)).width - 2f * ((Rect)(ref inRect)).x;
		float num4 = ButtonSize.x * 1.3f;
		if ((float)buttons.Count * num4 + num2 > num3)
		{
			num4 = (num3 - num2) / (float)buttons.Count;
		}
		float num5 = ((Rect)(ref inRect)).x + (((Rect)(ref inRect)).width - ((float)buttons.Count * num4 + num2)) / 2f;
		float num6 = ((Rect)(ref inRect)).yMax - ButtonSize.y + 4f;
		for (int i = 0; i < buttons.Count; i++)
		{
			(string, Action) tuple = buttons[i];
			if (Widgets.ButtonText(new Rect(num5 + (float)i * (num4 + num), num6, num4, ButtonSize.y), tuple.Item1, true, true, true, (TextAnchor?)null))
			{
				tuple.Item2?.Invoke();
			}
		}
	}

	private void ClearAll()
	{
		Thing obj = thing;
		Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
		if (val != null)
		{
			if (val.apparel != null)
			{
				foreach (Apparel item in val.apparel.WornApparel)
				{
					CustomizableGraphic.Replace((Thing)(object)item, null);
				}
			}
			CustomizableGraphic.Replace(thing, null);
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
		else
		{
			CustomizableGraphic.Replace(thing, null);
		}
	}

	public List<SectionData> TryFetchAllByCustomCat(string cat)
	{
		if (!CustomSections.Any() || !CustomSections.TryGetValue(cat, out var value))
		{
			return new List<SectionData>();
		}
		return value;
	}

	public bool IsSpecialCategory(string cat)
	{
		if (!cat.Equals("Hair"))
		{
			return cat.Equals("Skin");
		}
		return true;
	}

	private void DrawMainUI(Rect rect, WindowTab tab)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0232: Invalid comparison between Unknown and I4
		//IL_01e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(rect);
		((Rect)(ref val)).height = scrollViewHeight;
		((Rect)(ref val)).width = ((Rect)(ref rect)).width - 50f;
		Rect val2 = val;
		rect = GenUI.ContractedBy(rect, 2f);
		Widgets.BeginScrollView(rect, ref scrollPosition, val2, true);
		((Rect)(ref rect)).width = ((Rect)(ref rect)).width - 48f;
		float curY = ((Rect)(ref rect)).y;
		Thing val3 = default(Thing);
		ThingGData thingGData = default(ThingGData);
		foreach (KeyValuePair<Thing, ThingGData> editableThing in EditableThings)
		{
			editableThing.Deconstruct(ref val3, ref thingGData);
			Thing val4 = val3;
			ThingGData thingGData2 = thingGData;
			WindowTab editMode = thingGData2.editMode;
			if (editMode != tab)
			{
				continue;
			}
			curY = MakeStandardSection(rect, curY, val4, thingGData2, editMode);
			foreach (SectionData value in thingGData2.customData.Values)
			{
				if (value != thingGData2.TryGetGeneric)
				{
					curY = DrawCustom(rect, curY, val4, value);
				}
			}
		}
		foreach (string key in CustomSections.Keys)
		{
			if (IsSpecialCategory(key))
			{
				continue;
			}
			List<SectionData> list = CustomSections[key];
			if (list.Count == 0 || list.All((SectionData x) => x.editMode != tab))
			{
				continue;
			}
			foreach (SectionData item in list)
			{
				if (item.editMode == tab)
				{
					if (key != "NONE")
					{
						DrawTitle(item.flag.CustomCategory, rect, ref curY);
					}
					curY = DrawCustom(rect, curY, thing, item);
				}
			}
		}
		if ((int)Event.current.type == 8)
		{
			scrollViewHeight = curY - ((Rect)(ref rect)).y;
		}
		Widgets.EndScrollView();
	}

	private float MakeStandardSection(Rect rect, float curY, Thing thing, ThingGData data, WindowTab tab)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Expected O, but got Unknown
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e2: Expected O, but got Unknown
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_020c: Expected O, but got Unknown
		Pawn pawn = default(Pawn);
		ref Pawn reference = ref pawn;
		Thing obj = thing;
		reference = (Pawn)(object)((obj is Pawn) ? obj : null);
		SectionData tryGetGeneric = data.TryGetGeneric;
		DrawTitle(((Entity)thing).LabelCap, rect, ref curY);
		if (thing is Pawn && tab == WindowTab.Thing)
		{
			curY = PawnDefaulSection(rect, curY, thing);
		}
		else if (tab == WindowTab.Apparel)
		{
			DrawApparelIcon(thing, rect, ref curY, thing.DrawColor);
			if (apparelStyles.TryGetValue(thing, out var value))
			{
				ThingStyleDef styleDef = thing.StyleDef;
				string text = TaggedString.op_Implicit((styleDef != null) ? ((Def)styleDef).LabelCap : Translator.Translate("BS_Default"));
				if (MemoryExtensions.IsWhiteSpace(MemoryExtensions.AsSpan(text)) && thing.StyleDef != null)
				{
					int nameLessStyleIdx2 = -1;
					text = GetStyleName(thing, ref nameLessStyleIdx2, thing.StyleDef);
				}
				Rect val = default(Rect);
				((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, curY, ButtonSize.x + 20f, 32f);
				int nameLessStyleIdx3 = 2;
				if (Widgets.ButtonText(val, text, true, true, true, (TextAnchor?)null))
				{
					List<FloatMenuOption> list = new List<FloatMenuOption>();
					list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_Reset")), (Action)delegate
					{
						ThingStyleHelper.SetStyleDef(thing, (ThingStyleDef)null);
						queuedUpdate = true;
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					foreach (ThingStyleDef style2 in value)
					{
						string text2 = GetStyleName(thing, ref nameLessStyleIdx3, style2);
						list.Add(new FloatMenuOption(text2, (Action)delegate
						{
							ThingStyleHelper.SetStyleDef(thing, style2);
							queuedUpdate = true;
						}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					}
					Find.WindowStack.Add((Window)new FloatMenu(list));
				}
				curY = ((Rect)(ref val)).yMax + 12f;
			}
		}
		curY = MakeSharedCustomColorSection(rect, curY, thing, tryGetGeneric);
		return curY;
		static string GetStyleName(Thing thing, ref int nameLessStyleIdx, ThingStyleDef style)
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			string text3 = style.overrideLabel;
			if (text3 == null)
			{
				StyleCategoryDef category = style.Category;
				TaggedString? val2 = ((category != null) ? new TaggedString?(((Def)category).LabelCap) : ((TaggedString?)null));
				if (val2.HasValue)
				{
					TaggedString valueOrDefault = val2.GetValueOrDefault();
					text3 = ((object)(TaggedString)(ref valueOrDefault)/*cast due to .constrained prefix*/).ToString();
				}
				else if (nameLessStyleIdx > -1)
				{
					text3 = $"{((Entity)thing).LabelCap}, Style {nameLessStyleIdx}";
					nameLessStyleIdx++;
				}
				else
				{
					text3 = ((Entity)thing).LabelCap ?? "";
				}
			}
			return text3;
		}
		float MakeSharedCustomColorSection(Rect rect, float curY, Thing inThing, SectionData data)
		{
			//IL_0139: Unknown result type (might be due to invalid IL or missing references)
			//IL_0143: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
			//IL_0105: Unknown result type (might be due to invalid IL or missing references)
			//IL_0114: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_017d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0196: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01de: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0206: Unknown result type (might be due to invalid IL or missing references)
			//IL_0262: Unknown result type (might be due to invalid IL or missing references)
			//IL_0267: Unknown result type (might be due to invalid IL or missing references)
			//IL_026c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0270: Unknown result type (might be due to invalid IL or missing references)
			//IL_02a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_02c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_02eb: Unknown result type (might be due to invalid IL or missing references)
			//IL_02f5: Expected O, but got Unknown
			//IL_0351: Unknown result type (might be due to invalid IL or missing references)
			//IL_035b: Expected O, but got Unknown
			//IL_037b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0385: Expected O, but got Unknown
			bool flag = ThingCompUtility.HasComp<CompColorable>(inThing);
			SectionData sectionData = data;
			if (sectionData != null && sectionData.colorC)
			{
				if (flag)
				{
					if (!inThing.GetCustomColorA().HasValue)
					{
						DrawColorPicker(inThing.DrawColor, rect, ref curY, delegate(Color col)
						{
							//IL_0006: Unknown result type (might be due to invalid IL or missing references)
							inThing.DrawColor = col;
						}, TaggedString.op_Implicit(Translator.Translate("BS_BaseColor")));
					}
					DrawColorPicker(inThing.GetCustomColorA(), rect, ref curY, delegate(Color col)
					{
						//IL_000c: Unknown result type (might be due to invalid IL or missing references)
						//IL_000d: Unknown result type (might be due to invalid IL or missing references)
						//IL_000e: Unknown result type (might be due to invalid IL or missing references)
						//IL_0014: Unknown result type (might be due to invalid IL or missing references)
						//IL_0015: Unknown result type (might be due to invalid IL or missing references)
						Thing t = inThing;
						Color color = (inThing.DrawColor = col);
						t.SetCustomColorA(color);
					}, string.Format("{0} {1}", Translator.Translate("BS_Color"), Translator.Translate("BS_Primary")));
				}
				else
				{
					DrawColorPicker(inThing.GetCustomColorA(), rect, ref curY, delegate(Color col)
					{
						//IL_0006: Unknown result type (might be due to invalid IL or missing references)
						//IL_0007: Unknown result type (might be due to invalid IL or missing references)
						inThing.SetCustomColorA(col);
					}, string.Format("{0} {1}", Translator.Translate("BS_Color"), Translator.Translate("BS_Primary")));
				}
			}
			else if (flag)
			{
				DrawColorPicker(inThing.DrawColor, rect, ref curY, delegate(Color col)
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					inThing.DrawColor = col;
				});
			}
			SectionData sectionData2 = data;
			if (sectionData2 != null && sectionData2.colorB)
			{
				DrawColorPicker(inThing.GetCustomColorB(), rect, ref curY, delegate(Color col)
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					//IL_0007: Unknown result type (might be due to invalid IL or missing references)
					inThing.SetCustomColorB(col);
				}, string.Format("{0} {1}", Translator.Translate("BS_Color"), Translator.Translate("BS_Secondary")));
			}
			SectionData sectionData3 = data;
			if (sectionData3 != null && sectionData3.colorC)
			{
				DrawColorPicker(inThing.GetCustomColorC(), rect, ref curY, delegate(Color col)
				{
					//IL_0006: Unknown result type (might be due to invalid IL or missing references)
					//IL_0007: Unknown result type (might be due to invalid IL or missing references)
					inThing.SetCustomColorC(col);
				}, string.Format("{0} {1}", Translator.Translate("BS_Color"), Translator.Translate("BS_Tertiary")));
			}
			SectionData sectionData4 = data;
			if (sectionData4 != null)
			{
				List<FlagString> customFlags = sectionData4.customFlags;
				if (((customFlags != null) ? new bool?(GenCollection.Any<FlagString>(customFlags)) : ((bool?)null)) == true)
				{
					TaggedString val4 = TranslatorFormattedStringExtensions.Translate("BS_VariantsOf", NamedArgument.op_Implicit(((Entity)inThing).LabelCap));
					string text4 = TaggedString.op_Implicit(((TaggedString)(ref val4)).CapitalizeFirst());
					Rect val5 = default(Rect);
					((Rect)(ref val5))._002Ector(((Rect)(ref rect)).x, curY, ButtonSize.x + 20f, 32f);
					if (Widgets.ButtonText(val5, text4, true, true, true, (TextAnchor?)null))
					{
						List<FloatMenuOption> list2 = new List<FloatMenuOption>
						{
							new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_Reset")), (Action)delegate
							{
								foreach (FlagString customFlag in data.customFlags)
								{
									inThing.RemoveCustomTag(customFlag.mainTag);
								}
								queuedUpdate = true;
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)
						};
						foreach (FlagString subFlag in data.customFlags)
						{
							string label = subFlag.Label;
							list2.Add(new FloatMenuOption(label, (Action)delegate
							{
								foreach (FlagString customFlag2 in data.customFlags)
								{
									inThing.RemoveCustomTag(customFlag2.mainTag);
								}
								inThing.SetCustomTag(subFlag.mainTag, subFlag.subTag);
								queuedUpdate = true;
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
						}
						Find.WindowStack.Add((Window)new FloatMenu(list2));
					}
					curY = ((Rect)(ref val5)).yMax + 12f;
				}
			}
			return curY;
		}
		float PawnDefaulSection(Rect rect, float curY, Thing thing)
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			Pawn_StoryTracker story = pawn.story;
			Color value2 = ((story != null) ? story.SkinColor : Color.white);
			DrawColorPicker(value2, rect, ref curY, delegate(Color col)
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				pawn.story.skinColorOverride = col;
			}, TaggedString.op_Implicit(Translator.Translate("BS_Skin")));
			foreach (SectionData item in TryFetchAllByCustomCat("Skin"))
			{
				curY = DrawCustom(rect, curY, thing, item);
			}
			Pawn_StoryTracker story2 = pawn.story;
			Color value3 = ((story2 != null) ? story2.HairColor : Color.white);
			DrawColorPicker(value3, rect, ref curY, delegate(Color col)
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				pawn.story.HairColor = col;
			}, TaggedString.op_Implicit(Translator.Translate("BS_Hair")));
			foreach (SectionData item2 in TryFetchAllByCustomCat("Hair"))
			{
				curY = DrawCustom(rect, curY, thing, item2);
			}
			return curY;
		}
	}

	public string ColorIdxLabel(int idx)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit((TaggedString)(idx switch
		{
			0 => Translator.Translate("BS_PrimaryColor"), 
			1 => Translator.Translate("BS_SecondaryColor"), 
			2 => Translator.Translate("BS_TertiaryColor"), 
			_ => Translator.Translate("BS_Color") + " " + $"{idx} ", 
		}));
	}

	private float DrawCustom(Rect rect, float curY, Thing thing, SectionData data)
	{
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0326: Unknown result type (might be due to invalid IL or missing references)
		//IL_034f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0371: Unknown result type (might be due to invalid IL or missing references)
		//IL_037b: Expected O, but got Unknown
		//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e1: Expected O, but got Unknown
		//IL_0401: Unknown result type (might be due to invalid IL or missing references)
		//IL_040b: Expected O, but got Unknown
		bool hasMultipleClrs = data.HasMultipleClrs;
		if (data.colorA)
		{
			int idx = 0;
			FlagString flag = data.flag;
			if ((object)flag != null)
			{
				DrawColorPicker(thing.GetFlagColor(flag, idx), rect, ref curY, delegate(Color col)
				{
					//IL_0017: Unknown result type (might be due to invalid IL or missing references)
					//IL_0018: Unknown result type (might be due to invalid IL or missing references)
					thing.SetFlagColor(flag, idx, col);
				}, hasMultipleClrs ? (flag.Label + " " + ColorIdxLabel(idx)) : (flag.Label ?? ""));
			}
			else
			{
				Log.WarningOnce($"[BigAndSmall] Tried to draw custom color for {thing} with null flag.", 7123745);
			}
		}
		if (data.colorB)
		{
			int idx2 = 1;
			FlagString flag2 = data.flag;
			if ((object)flag2 != null)
			{
				DrawColorPicker(thing.GetFlagColor(flag2, idx2), rect, ref curY, delegate(Color col)
				{
					//IL_0017: Unknown result type (might be due to invalid IL or missing references)
					//IL_0018: Unknown result type (might be due to invalid IL or missing references)
					thing.SetFlagColor(flag2, idx2, col);
				}, hasMultipleClrs ? (flag2.Label + " " + ColorIdxLabel(idx2)) : (flag2.Label ?? ""));
			}
			else
			{
				Log.WarningOnce($"[BigAndSmall] Tried to draw custom color for {thing} with null flag.", 7123745);
			}
		}
		if (data.colorC)
		{
			int idx3 = 2;
			FlagString flag3 = data.flag;
			if ((object)flag3 != null)
			{
				DrawColorPicker(thing.GetFlagColor(flag3, idx3), rect, ref curY, delegate(Color col)
				{
					//IL_0017: Unknown result type (might be due to invalid IL or missing references)
					//IL_0018: Unknown result type (might be due to invalid IL or missing references)
					thing.SetFlagColor(flag3, idx3, col);
				}, hasMultipleClrs ? (flag3.Label + " " + ColorIdxLabel(idx3)) : (flag3.Label ?? ""));
			}
			else
			{
				Log.WarningOnce($"[BigAndSmall] Tried to draw custom color for {thing} with null flag.", 7123745);
			}
		}
		SectionData sectionData = data;
		if (sectionData != null)
		{
			List<FlagString> customFlags = sectionData.customFlags;
			if (((customFlags != null) ? new bool?(GenCollection.Any<FlagString>(customFlags)) : ((bool?)null)) == true)
			{
				TaggedString val = TranslatorFormattedStringExtensions.Translate("BS_VariantsOf", NamedArgument.op_Implicit(data.flag.Label));
				string text = TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
				Rect val2 = default(Rect);
				((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x, curY, ButtonSize.x + 20f, 32f);
				if (Widgets.ButtonText(val2, text, true, true, true, (TextAnchor?)null))
				{
					List<FloatMenuOption> list = new List<FloatMenuOption>();
					list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_Default")), (Action)delegate
					{
						foreach (FlagString customFlag in data.customFlags)
						{
							thing.RemoveFlagTag(data.flag, customFlag.mainTag);
						}
						queuedUpdate = true;
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					foreach (FlagString subFlag in data.customFlags)
					{
						string label = subFlag.Label;
						list.Add(new FloatMenuOption(label, (Action)delegate
						{
							foreach (FlagString customFlag2 in data.customFlags)
							{
								thing.RemoveFlagTag(data.flag, customFlag2.mainTag);
							}
							thing.SetFlagTag(data.flag, subFlag.mainTag, subFlag.subTag);
							queuedUpdate = true;
						}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
					}
					Find.WindowStack.Add((Window)new FloatMenu(list));
				}
				curY = ((Rect)(ref val2)).yMax + 12f;
			}
		}
		return curY;
	}

	private void DrawTitle(string titleText, Rect rect, ref float curY)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)2;
		curY += 4f;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(rect);
		((Rect)(ref val)).y = curY;
		((Rect)(ref val)).height = Text.LineHeight * 1.2f;
		Rect val2 = val;
		Widgets.Label(val2, GenText.CapitalizeFirst(titleText));
		Text.Font = (GameFont)1;
		curY += ((Rect)(ref val2)).height;
	}

	private void DrawApparelIcon(Thing item, Rect rect, ref float curY, Color color)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		GUI.color = color;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, curY, 64f, 64f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(val);
		Graphic graphic = item.Graphic;
		if (graphic != null)
		{
			_ = graphic.drawSize;
			if (true)
			{
				val2 = GenUI.ExpandedBy(val2, 32f * (item.Graphic.drawSize.x - 1f));
			}
		}
		Widgets.DrawTextureFitted(val2, item.Graphic.MatSouth.mainTexture, 1f, 1f);
		GUI.color = Color.white;
		curY += ((Rect)(ref val)).height + 12f;
	}

	private void DrawGeneTitleArea(GeneDef geneDef, Rect rect, ref float curY, Color color)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		DrawTitle(TaggedString.op_Implicit(((Def)geneDef).LabelCap), rect, ref curY);
		DrawGeneIcon(geneDef, rect, ref curY, color);
	}

	private void DrawGeneIcon(GeneDef geneDef, Rect rect, ref float curY, Color color)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		if ((Object)(object)geneDef.Icon != (Object)null)
		{
			GUI.color = color;
			Widgets.DrawTextureFitted(GenUI.ExpandedBy(new Rect(((Rect)(ref rect)).x, curY, 64f, 64f), 6f), (Texture)(object)geneDef.Icon, 1f, 1f);
			curY += ((Rect)(ref rect)).height + 24f;
			GUI.color = Color.white;
		}
	}

	private void DrawColorPicker(Color? currClrNullable, Rect rect, ref float curY, Action<Color> setColor, string title = null)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		if (!currClrNullable.HasValue)
		{
			TaggedString val = Translator.Translate("BS_Enable") + " " + title;
			string text = TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x, curY, ButtonSize.x + 20f, ButtonSize.y);
			if (Widgets.ButtonText(val2, text, true, true, true, (TextAnchor?)null))
			{
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
				setColor(Color.cyan);
				Pawn obj = pawn;
				if (obj != null)
				{
					obj.Drawer.renderer.SetAllGraphicsDirty();
				}
			}
			curY = ((Rect)(ref val2)).yMax + 14f;
			return;
		}
		if (title != null)
		{
			DrawTitle(title, rect, ref curY);
		}
		Color value = currClrNullable.Value;
		Color? val3 = SmartColorWidgets.MakeColorPicker(new Rect(((Rect)(ref rect)).x, curY, ((Rect)(ref rect)).width, 180f), value, ref draggingSlider, ref draggingWheel, extraColors);
		if (val3.HasValue)
		{
			Color valueOrDefault = val3.GetValueOrDefault();
			setColor(valueOrDefault);
			Pawn obj2 = pawn;
			if (obj2 != null)
			{
				obj2.Drawer.renderer.SetAllGraphicsDirty();
			}
		}
		curY += 192f;
	}
}
