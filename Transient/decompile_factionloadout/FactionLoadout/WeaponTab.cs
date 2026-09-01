using System;
using System.Collections.Generic;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class WeaponTab : EditTab
{
	public WeaponTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_Weapon")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0273: Unknown result type (might be due to invalid IL or missing references)
		base.DrawOverride<FloatRange>(ui, DefaultKind.weaponMoney, ref Current.WeaponMoney, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_ValueLabel", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_Weapon")))), (Action<Rect, bool, FloatRange>)DrawWeaponMoney, 32f, (Func<PawnKindEdit, FloatRange?>)((PawnKindEdit e) => e.WeaponMoney));
		base.DrawOverride<QualityCategory>(ui, (QualityCategory)2, ref Current.ForcedWeaponQuality, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Weapon_ForcedQuality")), (Action<Rect, bool, QualityCategory>)DrawWeaponQuality, 32f, (Func<PawnKindEdit, QualityCategory?>)((PawnKindEdit e) => e.ForcedWeaponQuality));
		DrawOverride(ui, DefaultKind.biocodeWeaponChance, ref Current.BiocodeWeaponChance, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Weapon_BiocodeChance")), DrawBiocodeChance, 32f, (PawnKindEdit e) => e.BiocodeWeaponChance);
		DrawOverride(ui, DefaultKind.weaponTags, ref Current.WeaponTags, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_AllowedTypes", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_Weapon")))), DrawWeaponTags, GetHeightFor(Current.WeaponTags), cloneDefault: true, (PawnKindEdit e) => e.WeaponTags);
		List<ThingDef> allWeapons = DefCache.AllWeapons;
		ThingDef defaultThing = ((allWeapons != null && allWeapons.Count > 0) ? DefCache.AllWeapons[0] : null);
		DrawSpecificGear(ui, ref Current.SpecificWeapons, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Weapon_RequiredAdvanced")), (ThingDef t) => t.IsWeapon, defaultThing);
		DrawOverride(ui, null, ref Current.WeaponBlacklist, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_WeaponBlacklist")), DrawWeaponBlacklist, GetHeightFor(Current.WeaponBlacklist), cloneDefault: false, (PawnKindEdit e) => e.WeaponBlacklist);
		DrawOverride(ui, null, ref Current.WeaponMaterials, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_WeaponMaterials")), DrawWeaponMaterials, GetHeightFor(Current.WeaponMaterials) + 26f, cloneDefault: false, delegate(PawnKindEdit e)
		{
			Current.WeaponMaterialsBlocklist = e.WeaponMaterialsBlocklist;
			return e.WeaponMaterials;
		});
		DrawMaterialSummary(ui, Current.WeaponMaterials, Current.WeaponMaterialsBlocklist);
	}

	private void DrawWeaponQuality(Rect rect, bool active, QualityCategory _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		DrawEnumSelector<QualityCategory>(rect, active, Current.ForcedWeaponQuality, (QualityCategory)(((_003F?)Current.Def.forceWeaponQuality) ?? 2), (Action<QualityCategory>)delegate(QualityCategory q)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			Current.ForcedWeaponQuality = q;
		}, (Func<QualityCategory, string>)null);
	}

	private void DrawBiocodeChance(Rect rect, bool active, float def)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		DrawChance(ref Current.BiocodeWeaponChance, def, rect, active);
	}

	private void DrawWeaponMoney(Rect rect, bool active, FloatRange defaultRange)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		DrawFloatRange(rect, active, ref Current.WeaponMoney, Current.Def.weaponMoney, ref buffers[bufferIndex++], ref buffers[bufferIndex++]);
	}

	private void DrawWeaponTags(Rect rect, bool active, List<string> defaultTags)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.WeaponTags, Current.Def.weaponTags, DefCache.AllWeaponsTags);
	}

	private void DrawWeaponBlacklist(Rect rect, bool active, List<DefRef<ThingDef>> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<ThingDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.WeaponBlacklist, (IList<ThingDef>)null, (IEnumerable<ThingDef>)DefCache.AllWeapons, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)null);
	}

	private void DrawWeaponMaterials(Rect rect, bool active, List<DefRef<ThingDef>> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Rect rect2 = DrawMaterialModeToggle(rect, ref Current.WeaponMaterialsBlocklist);
		DrawDefRefList<ThingDef>(rect2, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.WeaponMaterials, (IList<ThingDef>)null, (IEnumerable<ThingDef>)GenStuff.StuffDefs, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)null);
	}
}
