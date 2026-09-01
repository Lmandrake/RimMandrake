using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Modules;
using FactionLoadout.UISupport;
using FactionLoadout.UISupport.DrawSupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class PawnKindEditUI : Window
{
	public readonly PawnKindEdit Current;

	private readonly Dictionary<Tab, float> tabHeights = new Dictionary<Tab, float>();

	private Vector2 globalScroll;

	private int selectedTab;

	private List<Tab> tabs;

	public PawnKindDef DefaultKind
	{
		get
		{
			if (Current.DeletedOrClosed)
			{
				return Current.Def;
			}
			FactionDef val = FactionEdit.TryGetOriginal(Current.ParentEdit?.Faction?.DefName);
			if (val == null)
			{
				return Current.Def;
			}
			return val.GetKindDefs().FirstOrDefault((PawnKindDef k) => ((Def)k).defName == ((Def)Current.Def).defName) ?? Current.Def;
		}
	}

	public PawnKindEditUI(PawnKindEdit toEdit)
		: base((IWindowDrawing)null)
	{
		base.draggable = true;
		base.resizeable = true;
		base.doCloseX = true;
		Current = toEdit;
		DefCache.ScanDefs();
	}

	public override void PostOpen()
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).PostOpen();
		base.windowRect = new Rect((float)UI.screenWidth * 0.5f, 30f, (float)UI.screenWidth * 0.5f - 20f, (float)(UI.screenHeight - 50));
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0153: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_0264: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Unknown result type (might be due to invalid IL or missing references)
		//IL_0281: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0300: Unknown result type (might be due to invalid IL or missing references)
		//IL_0305: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Expected O, but got Unknown
		//IL_0338: Unknown result type (might be due to invalid IL or missing references)
		if (Current == null || Current.DeletedOrClosed)
		{
			((Window)this).Close(true);
			return;
		}
		Text.Font = (GameFont)1;
		if (tabs == null)
		{
			BuildTabs();
		}
		List<Tab> list = tabs;
		if (list == null || list.Count == 0)
		{
			Widgets.Label(inRect, Translator.Translate("FactionLoadout_NoEditableProperties"));
			return;
		}
		Rect val = inRect;
		((Rect)(ref val)).height = 40f;
		TaggedString val2;
		string text;
		if (!Current.IsGlobal)
		{
			val2 = ((Def)Current.Def).LabelCap;
			text = ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString();
		}
		else
		{
			val2 = Translator.Translate("FactionLoadout_GlobalLabel");
			text = ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString();
		}
		string text2 = "<size=32><b>Pawn Type: <color=#cf9af5>" + text + "</color></b></size>";
		Widgets.Label(val, text2);
		Rect val3 = inRect;
		float num = (float)Math.Ceiling((float)tabs.Count / 5f);
		((Rect)(ref val3)).height = num * 50f + 50f;
		((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 50f;
		for (int i = 0; i < tabs.Count; i++)
		{
			float num2 = (float)Math.Floor((float)i / 5f);
			if (num2 > 0f && i % 5 == 0)
			{
				GenUI.ExpandedBy(val3, 0f, 50f);
				((Rect)(ref val3)).yMin = ((Rect)(ref val3)).yMin + 50f;
			}
			Rect val4 = val3;
			((Rect)(ref val4)).height = 40f;
			((Rect)(ref val4)).width = 140f;
			((Rect)(ref val4)).x = ((Rect)(ref val4)).x + 150f * ((float)i - 5f * num2);
			Tab tab = tabs[i];
			Color val5 = (Color)((selectedTab == i) ? Color32.op_Implicit(new Color32((byte)49, (byte)82, (byte)133, byte.MaxValue)) : new Color(0.2f, 0.2f, 0.2f, 1f));
			if (Widgets.CustomButtonText(ref val4, "<b>" + tab.Name + "</b>", val5, Color.white, Color.white, default(Color), false, 1f, true, true, 1f))
			{
				selectedTab = i;
			}
			if (selectedTab != i)
			{
				continue;
			}
			float num3 = ((Rect)(ref inRect)).y + 100f + 50f * (num - 1f);
			ClipboardToolbar.Draw(new Rect(((Rect)(ref inRect)).x, num3, ((Rect)(ref inRect)).width, 28f), Current, delegate
			{
				if (selectedTab >= 0 && selectedTab < tabs.Count && tabs[selectedTab] is EditTab editTab)
				{
					editTab.ResetBuffers();
				}
			});
			Rect val6 = inRect;
			((Rect)(ref val6)).yMin = ((Rect)(ref val6)).yMin + (100f + 50f * (num - 1f) + 32f);
			float value;
			float num4 = (tabHeights.TryGetValue(tab, out value) ? Mathf.Max(value, ((Rect)(ref val6)).height) : ((Rect)(ref val6)).height);
			Widgets.BeginScrollView(val6, ref globalScroll, new Rect(0f, 0f, ((Rect)(ref inRect)).width - 24f, num4), true);
			Listing_Standard val7 = new Listing_Standard
			{
				ColumnWidth = ((Rect)(ref inRect)).width - 24f
			};
			((Listing)val7).Begin(new Rect(0f, 0f, ((Rect)(ref inRect)).width - 24f, 1000000f));
			tab.Draw(val7);
			tabHeights[tab] = ((Listing)val7).CurHeight;
			((Listing)val7).End();
			Widgets.EndScrollView();
		}
	}

	private void BuildTabs()
	{
		PawnKindDef defaultKind = DefaultKind;
		tabs = new List<Tab>(1)
		{
			new GeneralTab(Current, defaultKind)
		};
		if (defaultKind.RaceProps.Animal)
		{
			return;
		}
		tabs.AddRange(new _003C_003Ez__ReadOnlyArray<Tab>(new Tab[8]
		{
			new BackstoryTab(Current, defaultKind),
			new AppearanceTab(Current, defaultKind),
			new ApparelTab(Current, defaultKind),
			new WeaponTab(Current, defaultKind),
			new ImplantsTab(Current, defaultKind),
			new InventoryTab(Current, defaultKind),
			new RaidPointsTab(Current, defaultKind),
			new RaidLootTab(Current, defaultKind)
		}));
		if (VFEAncientsReflectionModule.ModLoaded.Value)
		{
			tabs.Add(new AncientsTab(Current, defaultKind));
		}
		if (VEPsycastsReflectionModule.ModLoaded.Value)
		{
			tabs.Add(new PsycastsTab(Current, defaultKind));
		}
		if (ModsConfig.BiotechActive)
		{
			tabs.Add(new XenotypeTab(Current, defaultKind));
		}
		foreach (ITotalControlModule module in ModuleRegistry.Modules)
		{
			if (module.IsActive)
			{
				module.AddTabs(Current, defaultKind, tabs);
			}
		}
	}
}
