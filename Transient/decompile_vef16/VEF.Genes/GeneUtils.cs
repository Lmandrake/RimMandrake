using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Genes;

public static class GeneUtils
{
	public static void ApplyGeneEffects(Gene gene)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Invalid comparison between Unknown and I4
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Invalid comparison between Unknown and I4
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Invalid comparison between Unknown and I4
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			if (gene?.pawn == null || !gene.Active || (int)Scribe.mode == 2 || (int)Scribe.mode == 3 || (int)Scribe.mode == 1)
			{
				return;
			}
			if (!GenList.NullOrEmpty<AbilityDef>((IList<AbilityDef>)gene.def.abilities))
			{
				foreach (AbilityDef ability in gene.def.abilities)
				{
					AbilityGeneExtension modExtension = ((Def)ability).GetModExtension<AbilityGeneExtension>();
					if ((modExtension == null || !modExtension.dontModifyAbilityOnGeneRemoval) && gene.pawn.abilities.GetAbility(ability, false) == null)
					{
						gene.pawn.abilities.GainAbility(ability);
					}
				}
			}
			GeneExtension modExtension2 = ((Def)gene.def).GetModExtension<GeneExtension>();
			if (modExtension2 == null)
			{
				return;
			}
			if (modExtension2.forceFemale)
			{
				gene.pawn.gender = (Gender)2;
				if (gene.pawn.story?.bodyType == BodyTypeDefOf.Male)
				{
					gene.pawn.story.bodyType = BodyTypeDefOf.Female;
				}
				StaticCollectionsClass.AddSwappedGenderGenePawnToList(gene.pawn);
			}
			if (modExtension2.forceMale)
			{
				gene.pawn.gender = (Gender)1;
				if (gene.pawn.story?.bodyType == BodyTypeDefOf.Female)
				{
					gene.pawn.story.bodyType = BodyTypeDefOf.Male;
				}
				StaticCollectionsClass.AddSwappedGenderGenePawnToList(gene.pawn);
			}
			if (modExtension2.forcedBodyType != null && DevelopmentalStageExtensions.Adult(gene.pawn.DevelopmentalStage))
			{
				gene.pawn.story.bodyType = modExtension2.forcedBodyType;
				gene.pawn.Drawer.renderer.SetAllGraphicsDirty();
			}
			if (modExtension2.customBloodThingDef != null)
			{
				StaticCollectionsClass.AddBloodtypeGenePawnToList((Thing)(object)gene.pawn, modExtension2.customBloodThingDef);
			}
			if (modExtension2.customBloodSmearThingDef != null)
			{
				StaticCollectionsClass.AddBloodSmearGenePawnToList((Thing)(object)gene.pawn, modExtension2.customBloodSmearThingDef);
			}
			if (modExtension2.customBloodIcon != "")
			{
				StaticCollectionsClass.AddBloodIconGenePawnToList((Thing)(object)gene.pawn, modExtension2.customBloodIcon);
			}
			if (modExtension2.customBloodEffect != null)
			{
				StaticCollectionsClass.AddBloodEffectGenePawnToList((Thing)(object)gene.pawn, modExtension2.customBloodEffect);
			}
			if (modExtension2.customWoundsFromFleshtype != null)
			{
				StaticCollectionsClass.AddWoundsFromFleshtypeGenePawnToList((Thing)(object)gene.pawn, modExtension2.customWoundsFromFleshtype);
			}
			if (modExtension2.diseaseProgressionFactor != 1f)
			{
				StaticCollectionsClass.AddDiseaseProgressionFactorGenePawnToList((Thing)(object)gene.pawn, modExtension2.diseaseProgressionFactor);
			}
			if (modExtension2.hediffToWholeBody != null)
			{
				gene.pawn.health.AddHediff(modExtension2?.hediffToWholeBody, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			if (modExtension2.hediffsToBodyParts != null)
			{
				foreach (HediffToBodyparts item in modExtension2?.hediffsToBodyParts)
				{
					int num = 0;
					foreach (BodyPartDef bodypart in item.bodyparts)
					{
						if (!GenCollection.EnumerableNullOrEmpty<BodyPartRecord>((IEnumerable<BodyPartRecord>)gene.pawn.RaceProps.body.GetPartsWithDef(bodypart)) && num <= gene.pawn.RaceProps.body.GetPartsWithDef(bodypart).Count)
						{
							if (!gene.pawn.health.hediffSet.PartIsMissing(gene.pawn.RaceProps.body.GetPartsWithDef(bodypart).ToArray()[num]))
							{
								gene.pawn.health.AddHediff(item.hediff, gene.pawn.RaceProps.body.GetPartsWithDef(bodypart).ToArray()[num], (DamageInfo?)null, (DamageResult)null);
							}
							num++;
						}
					}
				}
			}
			if (modExtension2.customMeatThingDef != null)
			{
				StaticCollectionsClass.AddMeatGenePawnToList((Thing)(object)gene.pawn, modExtension2.customMeatThingDef);
			}
			if (modExtension2.customLeatherThingDef != null)
			{
				StaticCollectionsClass.AddLeatherGenePawnToList((Thing)(object)gene.pawn, modExtension2.customLeatherThingDef);
			}
			if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension2.defsTreatedAsHumanMeat))
			{
				StaticCollectionsClass.AddDefsTreatedAsHumanMeatGenePawnToList((Thing)(object)gene.pawn, modExtension2.defsTreatedAsHumanMeat);
			}
			if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension2.defsTreatedAsHumanLeather))
			{
				StaticCollectionsClass.AddDefsTreatedAsHumanLeatherGenePawnToList((Thing)(object)gene.pawn, modExtension2.defsTreatedAsHumanLeather);
			}
			if (modExtension2.customVomitThingDef != null)
			{
				StaticCollectionsClass.AddVomitTypeGenePawnToList((Thing)(object)gene.pawn, modExtension2.customVomitThingDef);
			}
			if (modExtension2.customVomitEffect != null)
			{
				StaticCollectionsClass.AddVomitEffectGenePawnToList((Thing)(object)gene.pawn, modExtension2.customVomitEffect);
			}
			if (modExtension2.noSkillLoss != null)
			{
				StaticCollectionsClass.AddNoSkillLossGenePawnToList((Thing)(object)gene.pawn, modExtension2.noSkillLoss);
			}
			if (modExtension2.skillRecreation != null)
			{
				StaticCollectionsClass.AddSkillRecreationGenePawnToList((Thing)(object)gene.pawn, modExtension2.skillRecreation);
			}
			if (modExtension2.globalSkillLossMultiplier != 1f)
			{
				StaticCollectionsClass.AddSkillLossMultiplierGenePawnToList((Thing)(object)gene.pawn, modExtension2.globalSkillLossMultiplier);
			}
			if (modExtension2.skillDegradation)
			{
				StaticCollectionsClass.AddSkillDegradationGenePawnToList(gene.pawn);
			}
			if (modExtension2.pregnancySpeedFactor != 1f)
			{
				StaticCollectionsClass.AddPregnancySpeedFactorGenePawnToList((Thing)(object)gene.pawn, modExtension2.pregnancySpeedFactor);
			}
			if (!GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(modExtension2.moveSpeedFactorByTerrainTag))
			{
				StaticCollectionsClass.AddMoveSpeedFactorByTerrainTag((Thing)(object)gene.pawn, gene, modExtension2.moveSpeedFactorByTerrainTag);
			}
		}
		catch (Exception arg2)
		{
			object arg;
			if (gene == null)
			{
				arg = null;
			}
			else
			{
				GeneDef def = gene.def;
				arg = ((def != null) ? Gen.ToStringSafe<string>(((Def)def).defName) : null);
			}
			Log.Error($"[VEF] Error in GeneUtils.ApplyGeneEffects for gene {arg}: {arg2}");
		}
	}

	public static void RemoveGeneEffects(Gene gene)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Invalid comparison between Unknown and I4
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Invalid comparison between Unknown and I4
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Invalid comparison between Unknown and I4
		try
		{
			if (gene?.pawn == null || (int)Scribe.mode == 2 || (int)Scribe.mode == 3 || (int)Scribe.mode == 1)
			{
				return;
			}
			if (!GenList.NullOrEmpty<AbilityDef>((IList<AbilityDef>)gene.def.abilities))
			{
				foreach (AbilityDef ability in gene.def.abilities)
				{
					AbilityGeneExtension modExtension = ((Def)ability).GetModExtension<AbilityGeneExtension>();
					if ((modExtension == null || !modExtension.dontModifyAbilityOnGeneRemoval) && gene.pawn.abilities.GetAbility(ability, false) != null)
					{
						gene.pawn.abilities.RemoveAbility(ability);
					}
				}
			}
			GeneExtension modExtension2 = ((Def)gene.def).GetModExtension<GeneExtension>();
			if (modExtension2 == null)
			{
				return;
			}
			if (modExtension2.customBloodThingDef != null)
			{
				StaticCollectionsClass.RemoveBloodtypeGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customBloodSmearThingDef != null)
			{
				StaticCollectionsClass.RemoveBloodSmearGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension2.defsTreatedAsHumanMeat))
			{
				StaticCollectionsClass.RemoveDefsTreatedAsHumanMeatGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension2.defsTreatedAsHumanLeather))
			{
				StaticCollectionsClass.RemoveDefsTreatedAsHumanLeatherGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customBloodIcon != "")
			{
				StaticCollectionsClass.RemoveBloodIconGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customBloodEffect != null)
			{
				StaticCollectionsClass.RemoveBloodEffectGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customWoundsFromFleshtype != null)
			{
				StaticCollectionsClass.RemoveWoundsFromFleshtypeGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.diseaseProgressionFactor != 1f)
			{
				StaticCollectionsClass.RemoveDiseaseProgressionFactorGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2?.hediffToWholeBody != null)
			{
				HediffSet hediffSet = gene.pawn.health.hediffSet;
				if (hediffSet != null && hediffSet.HasHediff(modExtension2?.hediffToWholeBody, false))
				{
					Hediff firstHediffOfDef = gene.pawn.health.hediffSet.GetFirstHediffOfDef(modExtension2?.hediffToWholeBody, false);
					if (firstHediffOfDef != null)
					{
						gene.pawn.health.RemoveHediff(firstHediffOfDef);
					}
				}
			}
			if (modExtension2?.hediffsToBodyParts != null)
			{
				foreach (HediffToBodyparts item in modExtension2?.hediffsToBodyParts)
				{
					foreach (BodyPartDef bodypart in item.bodyparts)
					{
						_ = bodypart;
						HediffSet hediffSet2 = gene.pawn.health.hediffSet;
						if (hediffSet2 != null && hediffSet2.HasHediff(item.hediff, false))
						{
							Hediff firstHediffOfDef2 = gene.pawn.health.hediffSet.GetFirstHediffOfDef(item.hediff, false);
							if (firstHediffOfDef2 != null)
							{
								gene.pawn.health.RemoveHediff(firstHediffOfDef2);
							}
						}
					}
				}
			}
			if (modExtension2.customMeatThingDef != null)
			{
				StaticCollectionsClass.RemoveMeatGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customLeatherThingDef != null)
			{
				StaticCollectionsClass.RemoveLeatherGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customVomitThingDef != null)
			{
				StaticCollectionsClass.RemoveVomitTypeGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.customVomitEffect != null)
			{
				StaticCollectionsClass.RemoveVomitEffectGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.noSkillLoss != null)
			{
				StaticCollectionsClass.RemoveNoSkillLossGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.skillRecreation != null)
			{
				StaticCollectionsClass.RemoveSkillRecreationGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.globalSkillLossMultiplier != 1f)
			{
				StaticCollectionsClass.RemoveSkillLossMultiplierGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (modExtension2.skillDegradation)
			{
				StaticCollectionsClass.RemoveSkillDegradationGenePawnFromList(gene.pawn);
			}
			if (modExtension2.pregnancySpeedFactor != 1f)
			{
				StaticCollectionsClass.RemovePregnancySpeedFactorGenePawnFromList((Thing)(object)gene.pawn);
			}
			if (!GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(modExtension2.moveSpeedFactorByTerrainTag))
			{
				StaticCollectionsClass.RemoveMoveSpeedFactorByTerrainTag((Thing)(object)gene.pawn, gene);
			}
		}
		catch (Exception arg2)
		{
			object arg;
			if (gene == null)
			{
				arg = null;
			}
			else
			{
				GeneDef def = gene.def;
				arg = ((def != null) ? Gen.ToStringSafe<string>(((Def)def).defName) : null);
			}
			Log.Error($"[VEF] Error in GeneUtils.RemoveGeneEffects for gene {arg}: {arg2}");
		}
	}
}
