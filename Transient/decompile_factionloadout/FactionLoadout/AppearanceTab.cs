using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class AppearanceTab : EditTab
{
	public AppearanceTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_Appearance")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_023e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0243: Unknown result type (might be due to invalid IL or missing references)
		ref List<DefRef<BeardDef>> customBeards = ref Current.CustomBeards;
		TaggedString val = Translator.Translate("FactionLoadout_Appearance_Beards");
		DrawOverride(ui, null, ref customBeards, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawBeardStyles, GetHeightFor(Current.CustomBeards), cloneDefault: false, (PawnKindEdit e) => e.CustomBeards);
		ref List<DefRef<HairDef>> customHair = ref Current.CustomHair;
		val = Translator.Translate("FactionLoadout_Appearance_Hair");
		DrawOverride(ui, null, ref customHair, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawHairStyles, GetHeightFor(Current.CustomHair), cloneDefault: false, (PawnKindEdit e) => e.CustomHair);
		ref List<Color> customHairColors = ref Current.CustomHairColors;
		val = Translator.Translate("FactionLoadout_Appearance_HairColors");
		DrawOverride(ui, null, ref customHairColors, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawHairColors, GetHeightFor(Current.CustomHairColors, 36f), cloneDefault: false, (PawnKindEdit e) => e.CustomHairColors);
		ref List<DefRef<BodyTypeDef>> bodyTypes = ref Current.BodyTypes;
		val = Translator.Translate("FactionLoadout_Appearance_BodyTypes");
		DrawOverride(ui, null, ref bodyTypes, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawBodyTypes, GetHeightFor(Current.BodyTypes), cloneDefault: false, (PawnKindEdit e) => e.BodyTypes);
		if (ModsConfig.IdeologyActive)
		{
			ref List<DefRef<TattooDef>> customFaceTattoos = ref Current.CustomFaceTattoos;
			val = Translator.Translate("FactionLoadout_Appearance_FaceTattoos");
			DrawOverride(ui, null, ref customFaceTattoos, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawFaceTattoos, GetHeightFor(Current.CustomFaceTattoos), cloneDefault: false, (PawnKindEdit e) => e.CustomFaceTattoos);
			ref List<DefRef<TattooDef>> customBodyTattoos = ref Current.CustomBodyTattoos;
			val = Translator.Translate("FactionLoadout_Appearance_BodyTattoos");
			DrawOverride(ui, null, ref customBodyTattoos, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawBodyTattoos, GetHeightFor(Current.CustomBodyTattoos), cloneDefault: false, (PawnKindEdit e) => e.CustomBodyTattoos);
		}
	}

	private void DrawFaceTattoos(Rect rect, bool active, List<DefRef<TattooDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawTattoos(rect, active, Current.CustomFaceTattoos, (TattooType)0);
	}

	private void DrawBodyTattoos(Rect rect, bool active, List<DefRef<TattooDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawTattoos(rect, active, Current.CustomBodyTattoos, (TattooType)1);
	}

	private void DrawTattoos(Rect rect, bool active, List<DefRef<TattooDef>> current, TattooType type)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		List<TattooDef> allDefs = DefDatabase<TattooDef>.AllDefsListForReading.Where((TattooDef t) => t.tattooType == type).ToList();
		CustomFloatMenu customFloatMenu = DrawDefRefList<TattooDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<TattooDef>>)current, (IList<TattooDef>)null, (IEnumerable<TattooDef>)allDefs, (Func<TattooDef, MenuItemBase>)MakeItem, (Func<TattooDef, string>)null, (Func<TattooDef, string>)null);
		if (customFloatMenu != null)
		{
			customFloatMenu.Columns = 4;
		}
		static MenuItemBase MakeItem(TattooDef def)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			object arg = ((Def)def).LabelCap;
			ModContentPack modContentPack = ((Def)def).modContentPack;
			return new MenuItemIcon(def, string.Format("{0} ({1})", arg, ((modContentPack != null) ? modContentPack.Name : null) ?? "<no-mod>"), ((StyleItemDef)def).Icon)
			{
				Size = new Vector2(100f, 100f),
				BGColor = Color.white
			};
		}
	}

	private void DrawHairStyles(Rect rect, bool active, List<DefRef<HairDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		CustomFloatMenu customFloatMenu = DrawDefRefList<HairDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<HairDef>>)Current.CustomHair, (IList<HairDef>)null, (IEnumerable<HairDef>)DefDatabase<HairDef>.AllDefsListForReading, (Func<HairDef, MenuItemBase>)MakeItem, (Func<HairDef, string>)null, (Func<HairDef, string>)null);
		if (customFloatMenu != null)
		{
			customFloatMenu.AllowChangeTint = true;
			customFloatMenu.Tint = Color32.op_Implicit(new Color32((byte)245, (byte)212, (byte)78, byte.MaxValue));
			customFloatMenu.Columns = 4;
		}
		static MenuItemBase MakeItem(HairDef def)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			object arg = ((Def)def).LabelCap;
			ModContentPack modContentPack = ((Def)def).modContentPack;
			return new MenuItemIcon(def, string.Format("{0} ({1})", arg, ((modContentPack != null) ? modContentPack.Name : null) ?? "<no-mod>"), ((StyleItemDef)def).Icon)
			{
				Size = new Vector2(100f, 100f),
				BGColor = Color.white
			};
		}
	}

	private void DrawBeardStyles(Rect rect, bool active, List<DefRef<BeardDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		CustomFloatMenu customFloatMenu = DrawDefRefList<BeardDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<BeardDef>>)Current.CustomBeards, (IList<BeardDef>)null, (IEnumerable<BeardDef>)DefDatabase<BeardDef>.AllDefsListForReading, (Func<BeardDef, MenuItemBase>)MakeItem, (Func<BeardDef, string>)null, (Func<BeardDef, string>)null);
		if (customFloatMenu != null)
		{
			customFloatMenu.AllowChangeTint = true;
			customFloatMenu.Tint = Color32.op_Implicit(new Color32((byte)245, (byte)212, (byte)78, byte.MaxValue));
			customFloatMenu.Columns = 4;
		}
		static MenuItemBase MakeItem(BeardDef def)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			object arg = ((Def)def).LabelCap;
			ModContentPack modContentPack = ((Def)def).modContentPack;
			return new MenuItemIcon(def, string.Format("{0} ({1})", arg, ((modContentPack != null) ? modContentPack.Name : null) ?? "<no-mod>"), ((StyleItemDef)def).Icon)
			{
				Size = new Vector2(100f, 100f),
				BGColor = Color.white
			};
		}
	}

	private void DrawHairColors(Rect rect, bool active, List<Color> nullList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawColorList(rect, active, ref scrolls[scrollIndex++], Current.CustomHairColors, nullList);
	}

	private void DrawBodyTypes(Rect rect, bool active, List<DefRef<BodyTypeDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<BodyTypeDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<BodyTypeDef>>)Current.BodyTypes, (IList<BodyTypeDef>)null, (IEnumerable<BodyTypeDef>)DefCache.AllBodyTypes, (Func<BodyTypeDef, MenuItemBase>)((BodyTypeDef d) => new MenuItemText(d, TaggedString.op_Implicit(((Def)d).LabelCap) ?? ((Def)d).defName, DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), (Func<BodyTypeDef, string>)null, (Func<BodyTypeDef, string>)null);
	}
}
