using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnWeaponGenerator), "TryGenerateWeaponFor")]
public static class WeaponGenPatch
{
	public class AccumulatedWeaponEdits
	{
		public List<SpecRequirementEdit> always = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> chance = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool1 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool2 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool3 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool4 = new List<SpecRequirementEdit>();

		public int editCount;
	}

	private static void Postfix(Pawn pawn)
	{
		if (pawn == null || (MySettings.VanillaRestrictions && !pawn.RaceProps.ToolUser) || !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || (MySettings.VanillaRestrictions && pawn.WorkTagIsDisabled((WorkTags)8)))
		{
			return;
		}
		AccumulatedWeaponEdits accumulatedWeaponEdits = new AccumulatedWeaponEdits();
		foreach (PawnKindEdit item in PawnKindEdit.GetEditsFor(pawn.kindDef, ((Thing)pawn).Faction?.def))
		{
			Accumulate(accumulatedWeaponEdits, item);
			accumulatedWeaponEdits.editCount++;
		}
		if (accumulatedWeaponEdits.editCount > 0 && pawn.RaceProps.ToolUser)
		{
			ForceGiveWeapons(pawn, accumulatedWeaponEdits);
		}
		if (accumulatedWeaponEdits.editCount > 0)
		{
			HandleWeaponPriceLimit(pawn);
		}
	}

	private static void ForceGiveWeapons(Pawn pawn, AccumulatedWeaponEdits edits)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Invalid comparison between Unknown and I4
		if (pawn.apparel == null)
		{
			return;
		}
		bool flag = false;
		foreach (SpecRequirementEdit item in GetWhatToGive(edits))
		{
			if (item.Thing == null)
			{
				continue;
			}
			ThingWithComps val;
			try
			{
				val = GenerateNewWeapon(pawn, item);
				if (val == null)
				{
					continue;
				}
			}
			catch (Exception e)
			{
				ModCore.Error($"Exception generating required weapon '{((Def)item.Thing).LabelCap}'", e);
				continue;
			}
			if ((int)((Thing)val).def.equipmentType == 1)
			{
				if (!flag)
				{
					if (pawn.equipment.Primary != null)
					{
						pawn.equipment.Remove(pawn.equipment.Primary);
					}
					pawn.equipment.AddEquipment(val);
					flag = true;
				}
				else
				{
					((ThingOwner)pawn.inventory.innerContainer).TryAdd((Thing)(object)val, true);
				}
			}
			else
			{
				pawn.equipment.AddEquipment(val);
			}
		}
	}

	private static void Accumulate(AccumulatedWeaponEdits edits, PawnKindEdit edit)
	{
		if (edit?.SpecificWeapons == null)
		{
			return;
		}
		foreach (SpecRequirementEdit specificWeapon in edit.SpecificWeapons)
		{
			switch (specificWeapon.SelectionMode)
			{
			case ApparelSelectionMode.AlwaysTake:
				edits.always.Add(specificWeapon);
				break;
			case ApparelSelectionMode.RandomChance:
				edits.chance.Add(specificWeapon);
				break;
			case ApparelSelectionMode.FromPool1:
				edits.pool1.Add(specificWeapon);
				break;
			case ApparelSelectionMode.FromPool2:
				edits.pool2.Add(specificWeapon);
				break;
			case ApparelSelectionMode.FromPool3:
				edits.pool3.Add(specificWeapon);
				break;
			case ApparelSelectionMode.FromPool4:
				edits.pool4.Add(specificWeapon);
				break;
			}
		}
	}

	private static IEnumerable<SpecRequirementEdit> GetWhatToGive(AccumulatedWeaponEdits edits)
	{
		foreach (SpecRequirementEdit alway in edits.always)
		{
			yield return alway;
		}
		foreach (SpecRequirementEdit item in edits.chance)
		{
			if (Rand.Chance(item.SelectionChance))
			{
				yield return item;
			}
		}
		SpecRequirementEdit specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>((IEnumerable<SpecRequirementEdit>)edits.pool1, (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>((IEnumerable<SpecRequirementEdit>)edits.pool2, (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>((IEnumerable<SpecRequirementEdit>)edits.pool3, (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>((IEnumerable<SpecRequirementEdit>)edits.pool4, (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
	}

	private static ThingWithComps GenerateNewWeapon(Pawn pawn, SpecRequirementEdit spec)
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Expected I4, but got Unknown
		//IL_00e7: Expected I4, but got Unknown
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		Thing obj = ThingMaker.MakeThing(spec.Thing, spec.Material);
		ThingWithComps val = (ThingWithComps)(object)((obj is ThingWithComps) ? obj : null);
		if (val == null)
		{
			object arg = ((Def)spec.Thing).LabelCap;
			ThingDef material = spec.Material;
			ModCore.Error(string.Format("Failed to generate a '{0}' made out of '{1}'.", arg, (material != null) ? ((Def)material).LabelCap : TaggedString.op_Implicit("<nothing>")));
			return null;
		}
		if (spec.Style != null)
		{
			ThingStyleHelper.SetStyleDef((Thing)(object)val, spec.Style);
		}
		CompQuality val2 = ThingCompUtility.TryGetComp<CompQuality>((Thing)(object)val);
		if (val2 != null)
		{
			if (spec.Quality.HasValue)
			{
				val2.SetQuality(spec.Quality.Value, (ArtGenerationContext?)(ArtGenerationContext)0);
			}
			else
			{
				QualityCategory val3 = QualityUtility.GenerateQualityGeneratingPawn(pawn.kindDef, ((Thing)val).def);
				if (pawn.royalty != null && ((Thing)pawn).Faction != null)
				{
					RoyalTitleDef currentTitle = pawn.royalty.GetCurrentTitle(((Thing)pawn).Faction);
					if (currentTitle != null)
					{
						val3 = (QualityCategory)(byte)Mathf.Clamp((int)val3, (int)currentTitle.requiredMinimumApparelQuality, 6);
					}
				}
				val2.SetQuality(val3, (ArtGenerationContext?)(ArtGenerationContext)0);
			}
		}
		if (((Thing)val).def.useHitPoints)
		{
			float randomInRange = ((FloatRange)(ref pawn.kindDef.gearHealthRange)).RandomInRange;
			if (randomInRange < 1f)
			{
				int hitPoints = Mathf.Max(1, Mathf.RoundToInt(randomInRange * (float)((Thing)val).MaxHitPoints));
				((Thing)val).HitPoints = hitPoints;
			}
		}
		if (spec.Color != default(Color))
		{
			CompColorableUtility.SetColor((Thing)(object)val, spec.Color, false);
		}
		CompBiocodable val4 = ThingCompUtility.TryGetComp<CompBiocodable>((Thing)(object)val);
		if (val4 != null && val4.Biocodable)
		{
			if (val4.Biocoded)
			{
				val4.UnCode();
			}
			if (spec.Biocode)
			{
				val4.CodeFor(pawn);
			}
		}
		return val;
	}

	private static void HandleWeaponPriceLimit(Pawn pawn)
	{
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		if ((!MySettings.VerboseLogging && !MySettings.IgnorePriceLimits) || pawn.equipment == null || pawn.equipment.Primary != null)
		{
			return;
		}
		PawnKindDef kindDef = pawn.kindDef;
		if (kindDef.weaponTags == null || kindDef.weaponTags.Count == 0 || (MySettings.VanillaRestrictions && !pawn.RaceProps.ToolUser) || !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || (MySettings.VanillaRestrictions && pawn.WorkTagIsDisabled((WorkTags)8)))
		{
			return;
		}
		ThingStuffPair? val = null;
		List<ThingStuffPair> allWeaponPairs = PawnWeaponGenerator.allWeaponPairs;
		for (int i = 0; i < allWeaponPairs.Count; i++)
		{
			ThingStuffPair val2 = allWeaponPairs[i];
			if (!WeaponMatchesKind(val2, pawn, kindDef) || PawnWeaponGenerator.GetCommonality(pawn, val2) <= 0f)
			{
				continue;
			}
			if (val.HasValue)
			{
				float price = ((ThingStuffPair)(ref val2)).Price;
				ThingStuffPair value = val.Value;
				if (!(price < ((ThingStuffPair)(ref value)).Price))
				{
					continue;
				}
			}
			val = val2;
		}
		if (!val.HasValue)
		{
			return;
		}
		ThingStuffPair value2 = val.Value;
		if (!(((ThingStuffPair)(ref value2)).Price <= kindDef.weaponMoney.max))
		{
			if (MySettings.VerboseLogging)
			{
				string arg = ((value2.stuff != null) ? $" ({((Def)value2.stuff).LabelCap})" : "");
				ModCore.Warn($"Weapon slot left empty by price for '{((Def)pawn.kindDef).LabelCap}': nothing affordable within weaponMoney {kindDef.weaponMoney}. " + $"Cheapest matching option is {((Def)value2.thing).LabelCap}{arg} at ${((ThingStuffPair)(ref value2)).Price:F0} - raise weaponMoney or relax the weapon/material filters.");
			}
			if (MySettings.IgnorePriceLimits)
			{
				EquipFallbackWeapon(pawn, value2);
			}
		}
	}

	private static bool WeaponMatchesKind(ThingStuffPair w, Pawn pawn, PawnKindDef kind)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		bool flag = false;
		for (int i = 0; i < kind.weaponTags.Count; i++)
		{
			if (w.thing.weaponTags != null && w.thing.weaponTags.Contains(kind.weaponTags[i]))
			{
				flag = true;
				break;
			}
		}
		if (!flag)
		{
			return false;
		}
		if (kind.weaponStuffOverride != null && w.stuff != kind.weaponStuffOverride)
		{
			return false;
		}
		if (w.thing.IsRangedWeapon && pawn.WorkTagIsDisabled((WorkTags)524288))
		{
			return false;
		}
		if (w.stuff != null && !w.stuff.stuffProps.allowedInStuffGeneration)
		{
			return false;
		}
		return true;
	}

	private static void EquipFallbackWeapon(Pawn pawn, ThingStuffPair pair)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			Thing obj = ThingMaker.MakeThing(pair.thing, pair.stuff);
			ThingWithComps val = (ThingWithComps)(object)((obj is ThingWithComps) ? obj : null);
			if (val != null)
			{
				PawnGenerator.PostProcessGeneratedGear((Thing)(object)val, pawn);
				if (pawn.equipment.Primary != null)
				{
					pawn.equipment.Remove(pawn.equipment.Primary);
				}
				pawn.equipment.AddEquipment(val);
				ModCore.Debug($"Ignore-price fallback armed '{((Def)pawn.kindDef).LabelCap}' with {((Entity)val).LabelCap}.");
			}
		}
		catch (Exception e)
		{
			ModCore.Error($"Ignore-price weapon fallback failed for '{((Def)pawn.kindDef).LabelCap}'", e);
		}
	}
}
