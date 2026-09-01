using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnKindExtension : DefModExtension
{
	public class SkillPassion
	{
		public SkillDef skill;

		public Passion? passion;

		public int incrementBy;
	}

	public class FeatureAppendData
	{
		public float chance = 1f;

		public HashSet<string> exclusionTags = new HashSet<string>();

		public string modID;

		public List<GeneDef> appendGenes;

		public bool appendAsXenogenes = true;

		public XenotypeIconDef xenotypeIconDef;

		public string customXenotypeName;

		public string customXenotypeNameFemale;

		public bool removeOverlappingGenes = true;
	}

	public class ApparelAndEquipmentGraphics
	{
		public CustomizableGraphic graphic;

		public bool colorAToApparelClr = true;

		public bool applyToEquippment;

		public bool? applyToApparel;

		public List<ApparelLayerDef> apparelLayer;

		public List<BodyPartGroupDef> bodyPartGroup;

		public List<ThingCategoryDef> thingCategories;

		public List<string> tradeTags;

		public string requiredTag;
	}

	public HashSet<string> exclusionTags = new HashSet<string>();

	public float chance = 1f;

	public SimpleCurve ageCurve;

	public SimpleCurve ageCurveChronological;

	public SimpleCurve psylinkLevels;

	public List<SkillRange> clampedSkills;

	public List<SkillRange> skillRange;

	public bool skillRangeApplyToBabies;

	public bool? canHavePassions;

	public List<SkillPassion> forcedPassions;

	public List<GeneDef> appendGenes = new List<GeneDef>();

	[Obsolete("Use subExtensions instead")]
	public List<FeatureAppendData> ifModAppendGenes = new List<FeatureAppendData>();

	public List<PawnKindExtension> subExtensions = new List<PawnKindExtension>();

	public bool appendAsXenogenes;

	public bool removeOverlappingGenes = true;

	public float animalSapienceChance;

	public XenotypeIconDef xenotypeIconDef;

	public string customXenotypeName;

	public string customXenotypeNameFemale;

	public List<ApparelAndEquipmentGraphics> itemGraphics;

	public CustomizableGraphic pawnGraphic;

	public bool preventPantless;

	public bool preventShirtless;

	public bool blockAllApparel;

	public bool blockAllNonNudityApparel;

	/// <summary>
	/// Generate a "humanlike animal" dummy based on this PawnKindDef.
	/// Used to treat the pawn as if it had been generated from an animal.
	/// </summary>
	public bool generateHumanlikeAnimalFromThis;

	public Pawn Execute(Pawn pawn, bool singlePawn = false)
	{
		TryChangeApparel(pawn);
		SetModdableGraphics(pawn);
		if (singlePawn && Rand.Chance(animalSapienceChance))
		{
			pawn = pawn.SwapAnimalToSapientVersion();
		}
		if (ModsConfig.BiotechActive)
		{
			DoBiotechStuff(pawn);
		}
		ApplyPsylink(pawn);
		ApplyAgeCurve(pawn);
		ModifySkills(pawn);
		DoFeatureSets(pawn);
		return pawn;
	}

	private void DoBiotechStuff(Pawn pawn)
	{
		SetFakeXenotype(pawn, xenotypeIconDef, customXenotypeName, customXenotypeNameFemale);
		AppendGenes(pawn, appendGenes, appendAsXenogenes, removeOverlappingGenes);
		HashSet<string> hashSet = new HashSet<string>();
		foreach (FeatureAppendData ifModAppendGene in ifModAppendGenes)
		{
			if ((ifModAppendGene.modID == null || ModLister.GetActiveModWithIdentifier(ifModAppendGene.modID, false) != null) && Rand.Chance(ifModAppendGene.chance) && !ifModAppendGene.exclusionTags.Intersect(hashSet).Any())
			{
				SetFakeXenotype(pawn, ifModAppendGene.xenotypeIconDef, ifModAppendGene.customXenotypeName, ifModAppendGene.customXenotypeNameFemale);
				AppendGenes(pawn, ifModAppendGene.appendGenes, ifModAppendGene.appendAsXenogenes, ifModAppendGene.removeOverlappingGenes);
				GenCollection.AddRange<string>(hashSet, ifModAppendGene.exclusionTags);
			}
		}
	}

	private void DoFeatureSets(Pawn pawn)
	{
		HashSet<string> second = new HashSet<string>();
		foreach (PawnKindExtension subExtension in subExtensions)
		{
			if (Rand.Chance(subExtension.chance) && !subExtension.exclusionTags.Intersect(second).Any())
			{
				subExtension.Execute(pawn);
			}
		}
	}

	public void SetModdableGraphics(Pawn pawn)
	{
		if (pawnGraphic != null)
		{
			CustomizableGraphic.Replace((Thing)(object)pawn, pawnGraphic);
		}
		if (itemGraphics != null)
		{
			SetModdableApparelEtc(pawn);
		}
	}

	private void SetModdableApparelEtc(Pawn pawn)
	{
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		Pawn_EquipmentTracker equipment = pawn.equipment;
		List<ThingWithComps> list = ((equipment != null) ? equipment.AllEquipmentListForReading : null);
		Pawn_ApparelTracker apparel = pawn.apparel;
		List<Apparel> list2 = ((apparel != null) ? apparel.WornApparel : null);
		foreach (ApparelAndEquipmentGraphics itemGraphic in itemGraphics)
		{
			if (itemGraphic.applyToEquippment && list != null)
			{
				foreach (ThingWithComps item in list)
				{
					CustomizableGraphic.Replace((Thing)(object)item, itemGraphic.graphic);
				}
			}
			bool flag = itemGraphic.applyToApparel ?? (!itemGraphic.applyToEquippment);
			if (!(list2 != null && flag))
			{
				continue;
			}
			foreach (Apparel item2 in list2)
			{
				ThingDef def = ((Thing)item2).def;
				ApparelProperties apparel2 = ((Thing)item2).def.apparel;
				if ((itemGraphic.apparelLayer != null && (apparel2.layers == null || !apparel2.layers.Intersect(itemGraphic.apparelLayer).Any())) || (itemGraphic.bodyPartGroup != null && !apparel2.bodyPartGroups.Intersect(itemGraphic.bodyPartGroup).Any()) || (itemGraphic.requiredTag != null && (!apparel2.tags.Contains(itemGraphic.requiredTag) || (itemGraphic.thingCategories != null && !def.thingCategories.Intersect(itemGraphic.thingCategories).Any()) || (itemGraphic.tradeTags != null && !def.tradeTags.Intersect(itemGraphic.tradeTags).Any()))))
				{
					continue;
				}
				CustomizableGraphic.Replace((Thing)(object)item2, itemGraphic.graphic);
				if (itemGraphic.colorAToApparelClr)
				{
					Color? colorA = itemGraphic.graphic.colorA;
					if (colorA.HasValue)
					{
						Color valueOrDefault = colorA.GetValueOrDefault();
						((Thing)item2).DrawColor = valueOrDefault;
					}
				}
			}
		}
	}

	public static void AppendGenes(Pawn pawn, List<GeneDef> appendGenes, bool appendAsXenogenes, bool removeOverlappingGenes)
	{
		if (pawn.genes == null)
		{
			return;
		}
		List<Gene> source = pawn.genes.GenesListForReading.ToList();
		if (removeOverlappingGenes)
		{
			List<string> appendGeneExlusions = new List<string>();
			foreach (GeneDef item in appendGenes.Where((GeneDef x) => !GenList.NullOrEmpty<string>((IList<string>)x.exclusionTags)))
			{
				appendGeneExlusions.AddRange(item.exclusionTags);
			}
			if (GenCollection.Any<string>(appendGeneExlusions))
			{
				foreach (Gene item2 in source.Where((Gene x) => !GenList.NullOrEmpty<string>((IList<string>)x.def.exclusionTags) && x.def.exclusionTags.Intersect(appendGeneExlusions).Any()))
				{
					pawn.genes.RemoveGene(item2);
				}
			}
		}
		if (appendAsXenogenes)
		{
			foreach (GeneDef appendGene in appendGenes)
			{
				pawn.genes.AddGene(appendGene, true);
			}
			return;
		}
		foreach (GeneDef appendGene2 in appendGenes)
		{
			pawn.genes.AddGene(appendGene2, false);
		}
	}

	public static void SetFakeXenotype(Pawn pawn, XenotypeIconDef icon, string customName, string customNameFemale)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Invalid comparison between Unknown and I4
		if (icon != null || customName != null)
		{
			XenotypeIconDef val = icon ?? XenoTypeDefExtensions.TryFindIconDef(pawn);
			if (val != null)
			{
				pawn.genes.iconDef = val;
			}
			if (!string.IsNullOrEmpty(customName))
			{
				pawn.genes.xenotypeName = (((int)pawn.gender == 2 && customNameFemale != null) ? customNameFemale : customName);
			}
		}
	}

	public void ApplyAgeCurve(Pawn pawn)
	{
		if (ageCurve != null)
		{
			pawn.ageTracker.AgeBiologicalTicks = (long)ageCurve.Evaluate(Rand.Value) * 3600000;
		}
		if (ageCurveChronological != null)
		{
			long num = (long)ageCurveChronological.Evaluate(Rand.Value) * 3600000;
			if (num > pawn.ageTracker.AgeBiologicalTicks)
			{
				pawn.ageTracker.AgeChronologicalTicks = num;
			}
		}
	}

	public void ApplyPsylink(Pawn pawn)
	{
		if (!pawn.RaceProps.Humanlike)
		{
			return;
		}
		SimpleCurve val = psylinkLevels;
		if (val == null || !ModsConfig.RoyaltyActive)
		{
			return;
		}
		int num = (int)val.Evaluate(Rand.Value);
		if (num > 0)
		{
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicAmplifier, false);
			Hediff_Level val2 = (Hediff_Level)(object)((firstHediffOfDef is Hediff_Level) ? firstHediffOfDef : null);
			if (val2 != null)
			{
				int level = val2.level;
				val2.SetLevelTo(num + level);
				return;
			}
			Hediff obj = HediffMaker.MakeHediff(HediffDefOf.PsychicAmplifier, pawn, pawn.health.hediffSet.GetBrain());
			val2 = (Hediff_Level)(object)((obj is Hediff_Level) ? obj : null);
			pawn.health.AddHediff((Hediff)(object)val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			val2.SetLevelTo(num);
		}
	}

	public void TryChangeApparel(Pawn pawn)
	{
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0182: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_029d: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_03cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_03cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d2: Invalid comparison between Unknown and I4
		//IL_02a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Invalid comparison between Unknown and I4
		//IL_0439: Unknown result type (might be due to invalid IL or missing references)
		//IL_043c: Invalid comparison between Unknown and I4
		//IL_030e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0311: Invalid comparison between Unknown and I4
		//IL_0418: Unknown result type (might be due to invalid IL or missing references)
		//IL_041f: Expected O, but got Unknown
		//IL_02ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Expected O, but got Unknown
		//IL_0482: Unknown result type (might be due to invalid IL or missing references)
		//IL_0489: Expected O, but got Unknown
		//IL_0357: Unknown result type (might be due to invalid IL or missing references)
		//IL_035e: Expected O, but got Unknown
		if (blockAllApparel)
		{
			Pawn_ApparelTracker apparel = pawn.apparel;
			if (((apparel != null) ? apparel.WornApparel : null) != null && GenCollection.Any<Apparel>(pawn.apparel.WornApparel))
			{
				pawn.apparel.DestroyAll((DestroyMode)0);
			}
			return;
		}
		if (blockAllNonNudityApparel)
		{
			Pawn_ApparelTracker apparel2 = pawn.apparel;
			if (((apparel2 != null) ? apparel2.WornApparel : null) == null || !GenCollection.Any<Apparel>(pawn.apparel.WornApparel))
			{
				return;
			}
			List<Apparel> list = new List<Apparel>();
			foreach (Apparel item in pawn.apparel.WornApparel)
			{
				if (!((Thing)item).def.apparel.countsAsClothingForNudity || ((Thing)item).def.apparel.bodyPartGroups.Contains(BodyPartGroupDefOf.FullHead))
				{
					list.Add(item);
				}
			}
			{
				foreach (Apparel item2 in list)
				{
					pawn.apparel.Remove(item2);
					((Thing)item2).Destroy((DestroyMode)0);
				}
				return;
			}
		}
		if (!preventPantless && !preventShirtless)
		{
			return;
		}
		Pawn_StoryTracker story = pawn.story;
		if (story != null)
		{
			TraitSet traits = story.traits;
			if (((traits != null) ? new bool?(traits.HasTrait(TraitDefOf.Nudist)) : ((bool?)null)) == true)
			{
				return;
			}
		}
		Color? val = ((pawn.kindDef.apparelColor == Color.white) ? ((Color?)null) : new Color?(pawn.kindDef.apparelColor));
		Pawn_ApparelTracker apparel3 = pawn.apparel;
		if (((apparel3 != null) ? apparel3.WornApparel : null) == null)
		{
			return;
		}
		bool flag = false;
		bool flag2 = false;
		List<Apparel> list2 = new List<Apparel>();
		foreach (Apparel item3 in pawn.apparel.WornApparel)
		{
			if (((Thing)item3).def.apparel.bodyPartGroups.Contains(BodyPartGroupDefOf.Legs))
			{
				flag = true;
			}
			if (((Thing)item3).def.apparel.bodyPartGroups.Contains(BodyPartGroupDefOf.Torso))
			{
				flag2 = true;
			}
		}
		if (!flag && preventPantless && GenCollection.Any<BodyPartRecord>(pawn.RaceProps.body.AllParts, (Predicate<BodyPartRecord>)((BodyPartRecord x) => x.groups.Contains(BodyPartGroupDefOf.Legs))))
		{
			Faction faction = ((Thing)pawn).Faction;
			TechLevel val2 = (TechLevel)((faction == null) ? 2 : ((int)faction.def.techLevel));
			if ((int)val2 == 2)
			{
				ThingDef namedSilentFail = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_TribalA");
				if (namedSilentFail != null && namedSilentFail.apparel.PawnCanWear(pawn, false))
				{
					Pawn_ApparelTracker apparel4 = pawn.apparel;
					if (apparel4 != null && apparel4.CanWearWithoutDroppingAnything(namedSilentFail))
					{
						Apparel val3 = (Apparel)ThingMaker.MakeThing(namedSilentFail, GenStuff.RandomStuffFor(namedSilentFail));
						list2.Add(val3);
						pawn.apparel.Wear(val3, true, false);
						goto IL_0376;
					}
				}
			}
			if ((int)val2 > 2)
			{
				ThingDef namedSilentFail2 = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_Pants");
				if (namedSilentFail2 != null && namedSilentFail2.apparel.PawnCanWear(pawn, false))
				{
					Pawn_ApparelTracker apparel5 = pawn.apparel;
					if (apparel5 != null && apparel5.CanWearWithoutDroppingAnything(namedSilentFail2))
					{
						Apparel val4 = (Apparel)ThingMaker.MakeThing(namedSilentFail2, GenStuff.RandomStuffFor(namedSilentFail2));
						list2.Add(val4);
						pawn.apparel.Wear(val4, false, false);
					}
				}
			}
		}
		goto IL_0376;
		IL_0376:
		if (!flag2 && GenCollection.Any<BodyPartRecord>(pawn.RaceProps.body.AllParts, (Predicate<BodyPartRecord>)((BodyPartRecord x) => x.groups.Contains(BodyPartGroupDefOf.Torso))))
		{
			Faction faction2 = ((Thing)pawn).Faction;
			TechLevel val5 = (TechLevel)((faction2 == null) ? 2 : ((int)faction2.def.techLevel));
			if ((int)val5 == 2)
			{
				ThingDef namedSilentFail3 = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_TribalA");
				if (namedSilentFail3 != null && namedSilentFail3.apparel.PawnCanWear(pawn, false))
				{
					Pawn_ApparelTracker apparel6 = pawn.apparel;
					if (apparel6 != null && apparel6.CanWearWithoutDroppingAnything(namedSilentFail3))
					{
						Apparel val6 = (Apparel)ThingMaker.MakeThing(namedSilentFail3, GenStuff.RandomStuffFor(namedSilentFail3));
						list2.Add(val6);
						pawn.apparel.Wear(val6, true, false);
						goto IL_04a1;
					}
				}
			}
			if ((int)val5 > 2)
			{
				ThingDef namedSilentFail4 = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_BasicShirt");
				if (namedSilentFail4 != null && namedSilentFail4.apparel.PawnCanWear(pawn, false))
				{
					Pawn_ApparelTracker apparel7 = pawn.apparel;
					if (apparel7 != null && apparel7.CanWearWithoutDroppingAnything(namedSilentFail4))
					{
						Apparel val7 = (Apparel)ThingMaker.MakeThing(namedSilentFail4, GenStuff.RandomStuffFor(namedSilentFail4));
						list2.Add(val7);
						pawn.apparel.Wear(val7, false, false);
					}
				}
			}
		}
		goto IL_04a1;
		IL_04a1:
		if (!val.HasValue)
		{
			return;
		}
		Color valueOrDefault = val.GetValueOrDefault();
		foreach (Apparel item4 in list2)
		{
			((Thing)item4).DrawColor = valueOrDefault;
		}
	}

	public void ModifySkills(Pawn pawn)
	{
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0405: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f8: Expected I4, but got Unknown
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0410: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		if (pawn.skills?.skills == null && (skillRange != null || clampedSkills != null || forcedPassions != null || canHavePassions.HasValue))
		{
			Log.Warning($"PawnKindExtension for {pawn} tried to modify skills but they have no skills.");
		}
		if (canHavePassions == false)
		{
			foreach (SkillRecord skill in pawn.skills.skills)
			{
				skill.passion = (Passion)0;
			}
		}
		if (forcedPassions != null)
		{
			foreach (SkillPassion fPassion in forcedPassions)
			{
				foreach (SkillRecord item in pawn.skills.skills.Where((SkillRecord x) => x.def == fPassion.skill))
				{
					Passion? passion = fPassion.passion;
					if (passion.HasValue)
					{
						Passion value = (item.passion = passion.GetValueOrDefault());
						if (ModsConfig.BiotechActive)
						{
							foreach (Gene allActiveGene in pawn.GetAllActiveGenes())
							{
								PassionMod passionMod = allActiveGene.def.passionMod;
								if (passionMod != null && passionMod.skill == fPassion.skill)
								{
									allActiveGene.passionPreAdd = value;
								}
							}
						}
					}
					for (int i = 0; i < Math.Abs(fPassion.incrementBy); i++)
					{
						if (fPassion.incrementBy > 0)
						{
							item.passion = PassionExtension.IncrementPassion(item.passion);
						}
						else if (fPassion.incrementBy < 0)
						{
							item.passion = (Passion)(byte)Math.Max(0, item.passion - 1);
						}
					}
				}
			}
		}
		if (skillRange != null)
		{
			if (!skillRangeApplyToBabies)
			{
				Pawn_AgeTracker ageTracker = pawn.ageTracker;
				if (((ageTracker != null) ? ageTracker.CurLifeStage : null) == LifeStageDefOf.HumanlikeBaby)
				{
					goto IL_033c;
				}
			}
			foreach (var (val, val2) in skillRange.Select((SkillRange x) => (Skill: x.Skill, Range: x.Range)))
			{
				foreach (SkillRecord skill2 in pawn.skills.skills)
				{
					if (skill2.def == val)
					{
						int level = Rand.RangeInclusive(val2.min, val2.max);
						skill2.Level = level;
					}
				}
			}
		}
		goto IL_033c;
		IL_033c:
		if (clampedSkills == null)
		{
			return;
		}
		if (!skillRangeApplyToBabies)
		{
			Pawn_AgeTracker ageTracker2 = pawn.ageTracker;
			if (((ageTracker2 != null) ? ageTracker2.CurLifeStage : null) == LifeStageDefOf.HumanlikeBaby)
			{
				return;
			}
		}
		foreach (var (val3, val4) in clampedSkills.Select((SkillRange x) => (Skill: x.Skill, Range: x.Range)))
		{
			foreach (SkillRecord skill3 in pawn.skills.skills)
			{
				if (skill3.def == val3)
				{
					int level2 = skill3.GetLevel(false);
					if (level2 < val4.min)
					{
						skill3.Level = val4.min;
					}
					else if (level2 > val4.max)
					{
						skill3.Level = val4.max;
					}
				}
			}
		}
	}
}
