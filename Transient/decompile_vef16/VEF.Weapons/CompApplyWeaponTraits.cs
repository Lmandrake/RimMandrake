using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

public class CompApplyWeaponTraits : ThingComp
{
	public AbilityWithChargesDetails cachedAbilityWithChargesDetails;

	public AbilityDef abilityWithCharges;

	public int maxCharges;

	public int currentCharges;

	public int shotsFired;

	public int cachedLimitedUses = -1;

	private List<WeaponTraitDefExtension> contentDetails;

	private CompUniqueWeapon cachedComp;

	private CompEquippable cachedEquippableComp;

	public string LabelRemaining => $"{currentCharges} / {maxCharges}";

	public List<WeaponTraitDefExtension> GetDetails()
	{
		if (contentDetails == null)
		{
			contentDetails = new List<WeaponTraitDefExtension>();
			CompUniqueWeapon comp = GetComp();
			if (comp != null)
			{
				List<WeaponTraitDef> traitsListForReading = comp.TraitsListForReading;
				if (traitsListForReading != null && traitsListForReading.Count > 0)
				{
					foreach (WeaponTraitDef item in comp.TraitsListForReading)
					{
						WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
						if (modExtension != null)
						{
							contentDetails.Add(modExtension);
						}
					}
				}
			}
		}
		return contentDetails;
	}

	public CompUniqueWeapon GetComp()
	{
		if (cachedComp == null)
		{
			cachedComp = base.parent.GetComp<CompUniqueWeapon>();
		}
		return cachedComp;
	}

	public CompEquippable GetEquippableComp()
	{
		return cachedEquippableComp ?? (cachedEquippableComp = base.parent.GetComp<CompEquippable>());
	}

	public AbilityWithChargesDetails AbilityDetailsForWeapon(List<WeaponTraitDefExtension> traits)
	{
		if (cachedAbilityWithChargesDetails == null)
		{
			IEnumerable<WeaponTraitDefExtension> enumerable = traits.Where((WeaponTraitDefExtension x) => x.abilityWithCharges != null);
			cachedAbilityWithChargesDetails = ((enumerable != null) ? GenCollection.FirstOrFallback<AbilityWithChargesDetails>(enumerable.Select((WeaponTraitDefExtension x) => x.abilityWithCharges), (AbilityWithChargesDetails)null) : null);
		}
		return cachedAbilityWithChargesDetails;
	}

	public int LimitedUses(List<WeaponTraitDefExtension> traits)
	{
		if (cachedLimitedUses == -1)
		{
			foreach (WeaponTraitDefExtension trait in traits)
			{
				if (trait.limitedUses != 0)
				{
					cachedLimitedUses = trait.limitedUses;
					break;
				}
				cachedLimitedUses = 0;
			}
		}
		return cachedLimitedUses;
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic();
			});
			CalculateAbilities();
			LimitedUses(GetDetails());
		}
	}

	public void CalculateAbilities()
	{
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()) && abilityWithCharges == null)
		{
			abilityWithCharges = AbilityDetailsForWeapon(GetDetails())?.abilityDef;
			if (abilityWithCharges != null)
			{
				maxCharges = AbilityDetailsForWeapon(GetDetails()).maxCharges;
				currentCharges = maxCharges;
			}
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		string text = "";
		if (LimitedUses(GetDetails()) > 0)
		{
			text = TaggedString.op_Implicit(text + (Translator.Translate("VWE_WeaponDeteriorationInfo") + "\n" + ShotRemainingInfo()));
		}
		if (AbilityDetailsForWeapon(GetDetails()) != null)
		{
			text = TaggedString.op_Implicit(text + (TranslatorFormattedStringExtensions.Translate("ChargesRemaining", NamedArgument.op_Implicit(AbilityDetailsForWeapon(GetDetails()).chargeNoun)) + ": " + LabelRemaining));
		}
		return text + ((ThingComp)this).CompInspectStringExtra();
	}

	public override void Notify_DefsHotReloaded()
	{
		((ThingComp)this).Notify_DefsHotReloaded();
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic();
			});
			CalculateAbilities();
			LimitedUses(GetDetails());
		}
	}

	public void Notify_ForceRefresh()
	{
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic();
			});
			CalculateAbilities();
			LimitedUses(GetDetails());
		}
	}

	public void DeleteCaches()
	{
		contentDetails = null;
		cachedComp = null;
		cachedEquippableComp = null;
		cachedAbilityWithChargesDetails = null;
		abilityWithCharges = null;
		cachedLimitedUses = -1;
		ReinitializeVerbsIfNeeded();
	}

	public void ReinitializeVerbsIfNeeded()
	{
		if (AreVerbsDirty())
		{
			GetEquippableComp().VerbTracker.VerbsNeedReinitOnLoad();
		}
	}

	public bool AreVerbsDirty()
	{
		CompEquippable equippableComp = GetEquippableComp();
		if (((equippableComp != null) ? equippableComp.VerbTracker : null) == null)
		{
			return false;
		}
		foreach (VerbProperties verbProps in equippableComp.VerbProperties)
		{
			if (!GenCollection.Any<Verb>(equippableComp.VerbTracker.AllVerbs, (Predicate<Verb>)((Verb v) => v.verbProps == verbProps)))
			{
				return true;
			}
		}
		return false;
	}

	public override void PostExposeData()
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Invalid comparison between Unknown and I4
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref maxCharges, "maxCharges", 0, false);
		Scribe_Values.Look<int>(ref currentCharges, "currentCharges", 0, false);
		Scribe_Defs.Look<AbilityDef>(ref abilityWithCharges, "abilityWithCharges");
		Scribe_Values.Look<int>(ref shotsFired, "shotsFired", 0, false);
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic();
			});
			CalculateAbilities();
		}
		if ((int)Scribe.mode == 4)
		{
			ReinitializeVerbsIfNeeded();
		}
	}

	public void ChangeGraphic()
	{
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Expected O, but got Unknown
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Expected O, but got Unknown
		//IL_0230: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Expected O, but got Unknown
		if (!((Thing)base.parent).def.IsApparel)
		{
			IEnumerable<WeaponTraitDefExtension> enumerable = from x in GetDetails()
				where x.graphicOverrides != null && x.graphicOverrides.ContainsKey(((Thing)base.parent).def)
				select x;
			GraphicData val = ((enumerable != null) ? GenCollection.FirstOrFallback<WeaponTraitDefExtension>((IEnumerable<WeaponTraitDefExtension>)enumerable.OrderByDescending((WeaponTraitDefExtension x) => x.graphicOverridePriority), (WeaponTraitDefExtension)null) : null)?.graphicOverrides[((Thing)base.parent).def] ?? ((Thing)base.parent).def.graphicData;
			float num = (from x in GetDetails()
				where x.sizeMultiplier != 1f
				select x)?.Select((WeaponTraitDefExtension x) => x.sizeMultiplier)?.Aggregate(1f, (float acc, float current) => acc * current) ?? 1f;
			ShaderTypeDef shaderType = val.shaderType;
			Shader val2 = ((shaderType != null) ? shaderType.Shader : null) ?? ShaderTypeDefOf.Cutout.Shader;
			Color val3 = (Color)(((_003F?)((ThingComp)GetComp()).ForceColor()) ?? Color.white);
			if (val.graphicClass == typeof(Graphic_Single))
			{
				Graphic_Single val4 = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(val.texPath, val2, new Vector2(num, num), val3);
				ReflectionCache.weaponGraphic.Invoke((Thing)(object)base.parent) = (Graphic)(object)val4;
			}
			else if (val.graphicClass == typeof(Graphic_Random))
			{
				Graphic_Random val5 = (Graphic_Random)GraphicDatabase.Get<Graphic_Random>(val.texPath, val2, new Vector2(num, num), val3);
				ReflectionCache.weaponGraphic.Invoke((Thing)(object)base.parent) = (Graphic)(object)val5;
				ReflectionCache.weaponGraphic.Invoke((Thing)(object)base.parent) = (Graphic)new Graphic_RandomRotated(ReflectionCache.weaponGraphic.Invoke((Thing)(object)base.parent), 35f);
			}
		}
	}

	public override void Notify_Equipped(Pawn pawn)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		if (!GenList.NullOrEmpty<WeaponTraitDefExtension>((IList<WeaponTraitDefExtension>)GetDetails()))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic();
			});
		}
		foreach (WeaponTraitDefExtension detail in GetDetails())
		{
			if (detail?.abilityToAdd != null)
			{
				Pawn_AbilityTracker abilities = pawn.abilities;
				if (abilities != null)
				{
					abilities.GainAbility(detail.abilityToAdd);
				}
				_ = detail.abilityToAdd.cooldownTicksRange;
				Ability ability = pawn.abilities.GetAbility(detail.abilityToAdd, false);
				ability.StartCooldown(((IntRange)(ref ability.def.cooldownTicksRange)).RandomInRange);
				Pawn_AbilityTracker abilities2 = pawn.abilities;
				if (abilities2 != null)
				{
					abilities2.Notify_TemporaryAbilitiesChanged();
				}
			}
		}
		if (pawn.abilities != null && abilityWithCharges != null)
		{
			pawn.abilities.GainAbility(abilityWithCharges);
			pawn.abilities.Notify_TemporaryAbilitiesChanged();
			Ability ability2 = pawn.abilities.GetAbility(abilityWithCharges, false);
			ability2.maxCharges = maxCharges;
			ability2.RemainingCharges = currentCharges;
		}
		((ThingComp)this).Notify_Equipped(pawn);
	}

	public override void Notify_Unequipped(Pawn pawn)
	{
		foreach (WeaponTraitDefExtension detail in GetDetails())
		{
			if (detail?.abilityToAdd != null)
			{
				Pawn_AbilityTracker abilities = pawn.abilities;
				if (abilities != null)
				{
					abilities.RemoveAbility(detail.abilityToAdd);
				}
				Pawn_AbilityTracker abilities2 = pawn.abilities;
				if (abilities2 != null)
				{
					abilities2.Notify_TemporaryAbilitiesChanged();
				}
			}
		}
		if (pawn.abilities != null && abilityWithCharges != null)
		{
			Ability ability = pawn.abilities.GetAbility(abilityWithCharges, false);
			maxCharges = ability.maxCharges;
			currentCharges = ability.RemainingCharges;
			Pawn_AbilityTracker abilities3 = pawn.abilities;
			if (abilities3 != null)
			{
				abilities3.RemoveAbility(abilityWithCharges);
			}
			Pawn_AbilityTracker abilities4 = pawn.abilities;
			if (abilities4 != null)
			{
				abilities4.Notify_TemporaryAbilitiesChanged();
			}
		}
		((ThingComp)this).Notify_Unequipped(pawn);
	}

	public override void Notify_KilledPawn(Pawn pawn)
	{
		((ThingComp)this).Notify_KilledPawn(pawn);
		foreach (WeaponTraitDefExtension detail in GetDetails())
		{
			if (detail?.killHediff != null)
			{
				float num = detail.killHediffSeverity;
				if (detail.killHediff == HediffDefOf.ToxicBuildup)
				{
					num *= Mathf.Max(1f - StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.ToxicResistance, true, -1), 0f);
					num *= Mathf.Max(1f - StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.ToxicEnvironmentResistance, true, -1), 0f);
				}
				if (num != 0f)
				{
					HealthUtility.AdjustSeverity(pawn, detail.killHediff, num);
				}
			}
		}
	}

	public override float GetStatFactor(StatDef stat)
	{
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		float num = 1f;
		List<WeaponTraitDefExtension> details = GetDetails();
		if (details != null && details.Count > 0)
		{
			foreach (WeaponTraitDefExtension detail in GetDetails())
			{
				if (GenList.NullOrEmpty<ConditionalStatAffecter>((IList<ConditionalStatAffecter>)detail.conditionalStatAffecters))
				{
					continue;
				}
				for (int i = 0; i < detail.conditionalStatAffecters.Count; i++)
				{
					ConditionalStatAffecter val = detail.conditionalStatAffecters[i];
					if (val.statFactors != null && val.Applies(StatRequest.For((Thing)(object)base.parent)))
					{
						num *= StatUtility.GetStatFactorFromList(val.statFactors, stat);
					}
				}
			}
		}
		return num;
	}

	public override float GetStatOffset(StatDef stat)
	{
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		float num = 0f;
		List<WeaponTraitDefExtension> details = GetDetails();
		if (details != null && details.Count > 0)
		{
			foreach (WeaponTraitDefExtension detail in GetDetails())
			{
				if (GenList.NullOrEmpty<ConditionalStatAffecter>((IList<ConditionalStatAffecter>)detail.conditionalStatAffecters))
				{
					continue;
				}
				for (int i = 0; i < detail.conditionalStatAffecters.Count; i++)
				{
					ConditionalStatAffecter val = detail.conditionalStatAffecters[i];
					if (val.statOffsets != null && val.Applies(StatRequest.For((Thing)(object)base.parent)))
					{
						num += StatUtility.GetStatOffsetFromList(val.statOffsets, stat);
					}
				}
			}
		}
		return num;
	}

	public override void GetStatsExplanation(StatDef stat, StringBuilder sb, string whitespace = "")
	{
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		CompUniqueWeapon comp = GetComp();
		if (((comp != null) ? comp.TraitsListForReading : null) != null)
		{
			foreach (WeaponTraitDef item in GetComp().TraitsListForReading)
			{
				WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
				if (modExtension == null || GenList.NullOrEmpty<ConditionalStatAffecter>((IList<ConditionalStatAffecter>)modExtension.conditionalStatAffecters))
				{
					continue;
				}
				for (int i = 0; i < modExtension.conditionalStatAffecters.Count; i++)
				{
					ConditionalStatAffecter val = modExtension.conditionalStatAffecters[i];
					if (val.statOffsets != null)
					{
						float statOffsetFromList = StatUtility.GetStatOffsetFromList(val.statOffsets, stat);
						if (statOffsetFromList != 0f && val.Applies(StatRequest.For((Thing)(object)base.parent)))
						{
							sb.AppendLine(TaggedString.op_Implicit(whitespace + "    " + ((Def)item).LabelCap + " (" + val.Label + "): " + stat.ValueToString(statOffsetFromList, (ToStringNumberSense)3, false)));
						}
					}
					if (val.statFactors != null)
					{
						float statFactorFromList = StatUtility.GetStatFactorFromList(val.statFactors, stat);
						if (statFactorFromList != 1f && val.Applies(StatRequest.For((Thing)(object)base.parent)))
						{
							sb.AppendLine(TaggedString.op_Implicit(whitespace + "    " + ((Def)item).LabelCap + " (" + val.Label + "): " + stat.ValueToString(statFactorFromList, (ToStringNumberSense)2, false)));
						}
					}
				}
			}
		}
		if (stringBuilder.Length != 0)
		{
			sb.AppendLine(TaggedString.op_Implicit(whitespace + Translator.Translate("StatsReport_WeaponTraits") + ":"));
			sb.Append(stringBuilder.ToString());
		}
	}

	public bool NeedsReload()
	{
		if (AbilityDetailsForWeapon(GetDetails()) == null)
		{
			return false;
		}
		return currentCharges != maxCharges;
	}

	public int MinAmmoNeeded()
	{
		if (!NeedsReload())
		{
			return 0;
		}
		return AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge;
	}

	public int MaxAmmoNeeded()
	{
		if (!NeedsReload())
		{
			return 0;
		}
		return AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge * (maxCharges - currentCharges);
	}

	public void ReloadFrom(Pawn pawn, Thing ammo)
	{
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		if (NeedsReload() && ammo.stackCount >= AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge)
		{
			int num = Mathf.Clamp(ammo.stackCount / AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge, 0, maxCharges - currentCharges);
			ammo.SplitOff(num * AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge).Destroy((DestroyMode)0);
			currentCharges += num;
			Ability ability = pawn.abilities.GetAbility(abilityWithCharges, false);
			ability.RemainingCharges += num;
			if (AbilityDetailsForWeapon(GetDetails()).soundReload != null)
			{
				SoundStarter.PlayOneShot(AbilityDetailsForWeapon(GetDetails()).soundReload, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).PositionHeld, ((Thing)base.parent).MapHeld, false)));
			}
		}
	}

	public void Notify_UsedAbility()
	{
		currentCharges--;
	}

	public string ShotRemainingInfo()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VWE_ShotRemaining", NamedArgument.op_Implicit(LimitedUses(GetDetails()) - shotsFired)));
	}

	public override void Notify_UsedWeapon(Pawn pawn)
	{
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		if (LimitedUses(GetDetails()) > 0)
		{
			shotsFired++;
			if (shotsFired >= LimitedUses(GetDetails()))
			{
				string labelNoParenthesisCap = ((Thing)base.parent).LabelNoParenthesisCap;
				string text = ((pawn != null) ? ((Entity)pawn).LabelShort : null);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VWE_WeaponDeterioratedMessage", NamedArgument.op_Implicit(labelNoParenthesisCap), NamedArgument.op_Implicit(text))), MessageTypeDefOf.NegativeEvent, false);
				((Thing)base.parent).Destroy((DestroyMode)0);
			}
		}
	}

	public override IEnumerable<StatDrawEntry> SpecialDisplayStats()
	{
		IEnumerable<StatDrawEntry> enumerable = _003C_003En__0();
		if (enumerable != null)
		{
			foreach (StatDrawEntry item in enumerable)
			{
				yield return item;
			}
		}
		if (AbilityDetailsForWeapon(GetDetails())?.abilityDef != null)
		{
			yield return new StatDrawEntry(StatCategoryDefOf.Weapon, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Stat_Thing_ReloadChargesRemaining_Name", AbilityDetailsForWeapon(GetDetails()).ChargeNounArgument)), LabelRemaining, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Stat_Thing_ReloadChargesRemaining_Desc", AbilityDetailsForWeapon(GetDetails()).ChargeNounArgument)), 5440, (string)null, (IEnumerable<Hyperlink>)null, false, false);
			yield return new StatDrawEntry(StatCategoryDefOf.Weapon, TaggedString.op_Implicit(Translator.Translate("VEF.Weapons.Stat_Thing_MaterialPerCharge")), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Weapons.Stat_Thing_MaterialPerCharge_Value", NamedArgument.op_Implicit(AbilityDetailsForWeapon(GetDetails()).ammoCountPerCharge), NamedArgument.op_Implicit(((Def)AbilityDetailsForWeapon(GetDetails()).ammoDef).LabelCap), NamedArgument.op_Implicit(AbilityDetailsForWeapon(GetDetails()).maxCharges))), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Weapons.Stat_Thing_MaterialPerCharge_Desc", NamedArgument.op_Implicit(((Def)AbilityDetailsForWeapon(GetDetails()).ammoDef).label))), 5440, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<StatDrawEntry> _003C_003En__0()
	{
		return ((ThingComp)this).SpecialDisplayStats();
	}
}
