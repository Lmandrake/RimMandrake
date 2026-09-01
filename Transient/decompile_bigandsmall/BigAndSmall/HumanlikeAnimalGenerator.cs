using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class HumanlikeAnimalGenerator
{
	public static Dictionary<ThingDef, HumanlikeAnimal> humanlikeAnimals = new Dictionary<ThingDef, HumanlikeAnimal>();

	public static Dictionary<ThingDef, HumanlikeAnimal> reverseLookupHumanlikeAnimals = new Dictionary<ThingDef, HumanlikeAnimal>();

	public static HashSet<BodyDef> modifiedBodies = new HashSet<BodyDef>();

	public static bool HasHumanlikeAnimals { get; private set; }

	public static void GenerateHumanlikeAnimals(bool hotReload)
	{
		if (!BigSmall.BSSapientAnimalsActive && !BigSmall.BSSapientMechanoidsActive)
		{
			return;
		}
		HasHumanlikeAnimals = true;
		modifiedBodies.Clear();
		HashSet<ThingDef> hashSet = new HashSet<ThingDef>();
		List<PawnKindDef> list = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Invalid comparison between Unknown and I4
			ThingDef race = x.race;
			if (race != null)
			{
				RaceProperties val = race?.race;
				if (val != null && val.Animal)
				{
					return (int)val.intelligence == 0;
				}
			}
			return false;
		}).ToList();
		if (BigSmall.BSSapientMechanoidsActive)
		{
			IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
			{
				//IL_0023: Unknown result type (might be due to invalid IL or missing references)
				//IL_0029: Invalid comparison between Unknown and I4
				//IL_002c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0032: Invalid comparison between Unknown and I4
				ThingDef race2 = x.race;
				if (race2 != null)
				{
					RaceProperties val2 = race2?.race;
					if (val2 != null && val2.IsMechanoid && (int)val2.intelligence >= 0)
					{
						return (int)val2.intelligence != 2;
					}
				}
				return false;
			});
			Log.Message($"Found {enumerable.Count()} mechanoid pawn kinds to generate humanlike animals from.");
			list.AddRange(enumerable);
			SapienatorCanTargetMechsHack();
		}
		foreach (PawnKindDef item in list)
		{
			if (!hashSet.Contains(item.race))
			{
				GenerateAndRegisterHumanlikeAnimal(item, ThingDefOf.Human, hotReload);
				hashSet.Add(item.race);
			}
		}
		foreach (PawnKindDef item2 in DefDatabase<PawnKindDef>.AllDefs.Where((PawnKindDef x) => GenCollection.Any<PawnKindExtension>(x.ExtensionsOnDef<PawnKindExtension, PawnKindDef>((List<Type>)null, (List<Type>)null, doSort: true), (Predicate<PawnKindExtension>)((PawnKindExtension y) => y.generateHumanlikeAnimalFromThis))).ToList())
		{
			if (!hashSet.Contains(item2.race))
			{
				MakeDummySetupsForAlreadySapientAnimals(item2);
				hashSet.Add(item2.race);
			}
		}
		ThingDef val3 = default(ThingDef);
		HumanlikeAnimal humanlikeAnimal = default(HumanlikeAnimal);
		foreach (KeyValuePair<ThingDef, HumanlikeAnimal> humanlikeAnimal3 in humanlikeAnimals)
		{
			humanlikeAnimal3.Deconstruct(ref val3, ref humanlikeAnimal);
			HumanlikeAnimal humanlikeAnimal2 = humanlikeAnimal;
			reverseLookupHumanlikeAnimals[humanlikeAnimal2.animal] = humanlikeAnimal2;
		}
		modifiedBodies.Clear();
	}

	private static void SapienatorCanTargetMechsHack()
	{
		DefDatabase<ThingDef>.GetNamedSilentFail("BS_Sapienator")?.comps.Where((CompProperties x) => x is CompProperties_TargetableExtended).ToList().ForEach(delegate(CompProperties x)
		{
			((CompProperties_TargetableExtended)(object)x).targetInfo.canTargetMechs = true;
		});
	}

	private static void MakeDummySetupsForAlreadySapientAnimals(PawnKindDef animalLikePK)
	{
		animalLikePK.ExtensionsOnDef<PawnKindExtension, PawnKindDef>((List<Type>)null, (List<Type>)null, doSort: true).First((PawnKindExtension x) => x.generateHumanlikeAnimalFromThis);
		HumanlikeAnimal value = new HumanlikeAnimal
		{
			animalKind = animalLikePK,
			humanlikeAnimal = animalLikePK.race,
			humanlike = animalLikePK.race,
			animal = animalLikePK.race
		};
		humanlikeAnimals[animalLikePK.race] = value;
	}

	/// <summary>
	/// Generate a humanlike animal from an AnimalThing and HumanThing.
	///
	/// Generally we want to grab most stuff from the human, and transfer mostly the body and some traits from the animal.
	/// </summary>
	/// <param name="aniPawnKind">ThingKindDef of an Animal.</param>
	/// <param name="humThing">ThingDef of a Humanlike (likely always the defautl "Human")</param>
	/// <param name="hotReload">Whether or not this is in context of a hotreload.</param>
	public static void GenerateAndRegisterHumanlikeAnimal(PawnKindDef aniPawnKind, ThingDef humThing, bool hotReload)
	{
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Expected O, but got Unknown
		//IL_0585: Unknown result type (might be due to invalid IL or missing references)
		//IL_058a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0593: Unknown result type (might be due to invalid IL or missing references)
		//IL_0598: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_05ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_06fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_08e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_08e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_08ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_08fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0905: Unknown result type (might be due to invalid IL or missing references)
		//IL_090c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0917: Unknown result type (might be due to invalid IL or missing references)
		//IL_0928: Unknown result type (might be due to invalid IL or missing references)
		//IL_0939: Unknown result type (might be due to invalid IL or missing references)
		//IL_0949: Unknown result type (might be due to invalid IL or missing references)
		//IL_094e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0953: Unknown result type (might be due to invalid IL or missing references)
		//IL_095c: Expected O, but got Unknown
		//IL_0a8f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a94: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a9a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aa4: Expected O, but got Unknown
		ThingDef aniThing = aniPawnKind.race;
		bool allAnimalsHaveHands = BigSmallMod.settings.allAnimalsHaveHands;
		string defName = "HL_" + ((Def)aniThing).defName;
		RaceProperties race = aniThing.race;
		RaceProperties race2 = humThing.race;
		ThingDef val = defName.TryGetExistingDef<ThingDef>();
		RaceProperties val2 = new RaceProperties();
		if (val == null)
		{
			object obj = ((object)humThing).GetType().GetConstructor(Array.Empty<Type>()).Invoke(Array.Empty<object>());
			val = (ThingDef)((obj is ThingDef) ? obj : null);
		}
		RaceFuser.CopyThingDefFields(humThing, val);
		((Def)val).defName = defName;
		HashSet<string> compWhitelist = new HashSet<string>();
		HashSet<string> tabWhiteList = new HashSet<string>();
		HashSet<string> extWhiteList = new HashSet<string>();
		HashSet<RomanceTags> hashSet = new HashSet<RomanceTags>();
		RomanceTags romanceTags = null;
		foreach (HumanlikeAnimalSettings allHASetting in HumanlikeAnimalSettings.AllHASettings)
		{
			GenCollection.AddRange<string>(compWhitelist, allHASetting.compWhitelist);
			GenCollection.AddRange<string>(tabWhiteList, allHASetting.tabWhitelist);
			GenCollection.AddRange<string>(extWhiteList, allHASetting.modExtensionWhitelist);
			GenCollection.AddRange<RomanceTags>(hashSet, from x in allHASetting.animalFamilySettings
				where GenCollection.Any<string>(x.members, (Predicate<string>)((string x) => ((Def)aniThing).defName.Contains(x, StringComparison.OrdinalIgnoreCase))) || GenCollection.Any<string>(x.membersExact, (Predicate<string>)((string x) => ((Def)aniThing).defName.Equals(x, StringComparison.OrdinalIgnoreCase)))
				select x.romanceTags);
		}
		if (GenCollection.Any<RomanceTags>(hashSet))
		{
			romanceTags = hashSet.GetMerged();
		}
		List<CompProperties> list = new List<CompProperties>();
		if (aniThing.comps != null)
		{
			list.AddRange(aniThing.comps);
		}
		foreach (CompProperties comp in humThing.comps)
		{
			if (!GenCollection.Any<CompProperties>(list, (Predicate<CompProperties>)((CompProperties x) => ((object)x).GetType() == ((object)comp).GetType() && x.compClass == comp.compClass)))
			{
				list.Add(comp);
			}
		}
		List<CompProperties> comps = list.Where((CompProperties x) => compWhitelist.Contains(((object)x).GetType().ToString(), StringComparer.OrdinalIgnoreCase) || compWhitelist.Contains(x.compClass.ToString(), StringComparer.OrdinalIgnoreCase)).Distinct().ToList();
		val.comps = comps;
		val.thingClass = aniThing.thingClass;
		val.thingCategories = ((humThing.thingCategories != null) ? humThing.thingCategories.ToList() : new List<ThingCategoryDef>());
		((BuildableDef)val).stuffCategories = ((((BuildableDef)humThing).stuffCategories != null) ? ((BuildableDef)humThing).stuffCategories.ToList() : null);
		val.thingSetMakerTags = ((humThing.thingSetMakerTags != null) ? humThing.thingSetMakerTags.ToList() : null);
		val.virtualDefs = ((humThing.virtualDefs != null) ? humThing.virtualDefs.ToList() : null);
		((Def)val).modExtensions = new List<DefModExtension>();
		List<DefModExtension> modExtensions = ((Def)aniThing).modExtensions;
		if (modExtensions != null && modExtensions.Count > 0)
		{
			((Def)val).modExtensions.AddRange(((Def)aniThing).modExtensions.Where((DefModExtension x) => extWhiteList.Contains(((object)x).GetType().ToString(), StringComparer.OrdinalIgnoreCase)));
		}
		val.tools = ((aniThing.tools != null) ? aniThing.tools.ToList() : null);
		val.verbs = ((aniThing.verbs != null) ? aniThing.verbs.ToList() : null);
		ThingDef obj2 = val;
		List<ThingDefCountClass> list2 = humThing.butcherProducts ?? new List<ThingDefCountClass>();
		List<ThingDefCountClass> list3 = aniThing.butcherProducts ?? new List<ThingDefCountClass>();
		List<ThingDefCountClass> list4 = new List<ThingDefCountClass>(list2.Count + list3.Count);
		list4.AddRange(list2);
		list4.AddRange(list3);
		obj2.butcherProducts = list4;
		if (GenCollection.Empty<ThingDefCountClass>(val.butcherProducts))
		{
			val.butcherProducts = null;
		}
		ThingDef obj3 = val;
		list3 = humThing.smeltProducts ?? new List<ThingDefCountClass>();
		list2 = aniThing.smeltProducts ?? new List<ThingDefCountClass>();
		List<ThingDefCountClass> list5 = new List<ThingDefCountClass>(list3.Count + list2.Count);
		list5.AddRange(list3);
		list5.AddRange(list2);
		obj3.smeltProducts = list5;
		if (GenCollection.Empty<ThingDefCountClass>(val.smeltProducts))
		{
			val.smeltProducts = null;
		}
		List<RecipeDef> list6 = new List<RecipeDef>();
		if (humThing.recipes != null)
		{
			list6.AddRange(humThing.recipes);
		}
		if (aniThing.recipes != null)
		{
			list6.AddRange(aniThing.recipes);
		}
		val.recipes = list6.Distinct().ToList();
		ThingDef obj4 = val;
		List<string> list7 = humThing.tradeTags ?? new List<string>();
		List<string> list8 = aniThing.tradeTags ?? new List<string>();
		List<string> list9 = new List<string>(list7.Count + list8.Count);
		list9.AddRange(list7);
		list9.AddRange(list8);
		obj4.tradeTags = list9;
		List<Type> list10 = new List<Type>();
		if (humThing.inspectorTabs != null)
		{
			list10.AddRange(humThing.inspectorTabs);
		}
		if (aniThing.inspectorTabs != null)
		{
			list10.AddRange(aniThing.inspectorTabs);
		}
		val.inspectorTabs = list10.Where((Type x) => tabWhiteList.Contains(x.ToString(), StringComparer.OrdinalIgnoreCase)).Distinct().ToList();
		RaceFuser.CopyRaceProperties(race, val2);
		if (race.lifeExpectancy < race2.lifeExpectancy)
		{
			val2.lifeExpectancy = race2.lifeExpectancy;
			val2.ageGenerationCurve = race2.ageGenerationCurve;
		}
		val2.thinkTreeConstant = race2.thinkTreeConstant;
		val2.thinkTreeMain = race2.thinkTreeMain;
		val2.intelligence = race2.intelligence;
		val2.foodType = race2.foodType;
		val2.lifeStageAges = race2.lifeStageAges;
		val2.lifeStageWorkSettings = race2.lifeStageWorkSettings;
		val2.trainability = race2.trainability;
		val2.petness = race2.petness;
		val2.predator = race2.predator;
		val2.animalType = race2.animalType;
		val2.fleshType = ((val2.fleshType == FleshTypeDefOf.Mechanoid) ? race2.FleshType : val2.FleshType);
		val2.meatDef = race2.meatDef;
		if (race.hasMeat)
		{
			if (race.specificMeatDef != null)
			{
				val2.specificMeatDef = race.specificMeatDef;
			}
			else if (race.useMeatFrom != null)
			{
				val2.useMeatFrom = race.useMeatFrom;
			}
			else
			{
				val2.useMeatFrom = aniThing;
			}
		}
		else
		{
			val2.specificMeatDef = BSDefs.BS_MeatGeneric;
		}
		val2.hideTrainingTab = race2.hideTrainingTab;
		val2.canReleaseToWild = race2.canReleaseToWild;
		val2.disableAreaControl = race2.disableAreaControl;
		val2.canBePredatorPrey = race2.canBePredatorPrey;
		val2.allowedOnCaravan = race2.allowedOnCaravan;
		val2.herdAnimal = race2.herdAnimal;
		val2.herdMigrationAllowed = race2.herdMigrationAllowed;
		val2.packAnimal = race2.packAnimal;
		val2.willNeverEat = race2.willNeverEat;
		val2.nameCategory = race2.nameCategory;
		val2.nameGenerator = race2.nameGenerator;
		val2.nameGeneratorFemale = race2.nameGeneratorFemale;
		val2.nameOnTameChance = race2.nameOnTameChance;
		val2.roamMtbDays = null;
		((object)val2).GetType().GetField("hasUnnaturalCorpse")?.SetValue(val2, false);
		SetRenderTree(aniPawnKind, aniThing, race, race2, val2);
		SetupBodyTags(val, val2);
		string defName2 = "HL_" + ((Def)aniThing).defName + "_RaceHediff";
		HediffDef val3 = defName2.TryGetExistingDef<HediffDef>();
		PawnExtension pawnExtension = val3?.GetAllPawnExtensionsOnHediff().FirstOrDefault();
		float num = (pawnExtension?.animalFineManipulation).GetValueOrDefault();
		if (val3 == null)
		{
			bool flag = false;
			List<string> blackListKeyword = new List<string>(4) { "Mouth", "Jaw", "Beak", "Leg" };
			List<BodyPartRecord> allBodyPartsRecursive = val2.body.corePart.GetAllBodyPartsRecursive();
			if (GenCollection.Any<HumanlikeAnimalSettings>(HumanlikeAnimalSettings.AllHASettings, (Predicate<HumanlikeAnimalSettings>)((HumanlikeAnimalSettings x) => GenCollection.Any<string>(x.hasHandsWildcards, (Predicate<string>)((string wc) => ((Def)aniThing).defName.Contains(wc, StringComparison.OrdinalIgnoreCase))))))
			{
				flag = true;
				num = 1f;
			}
			else if (aniThing.race.IsMechanoid)
			{
				flag = true;
				num = 0.65f;
			}
			else if (GenCollection.Any<HumanlikeAnimalSettings>(HumanlikeAnimalSettings.AllHASettings, (Predicate<HumanlikeAnimalSettings>)((HumanlikeAnimalSettings x) => GenCollection.Any<string>(x.hasPoorHandsWildcards, (Predicate<string>)((string wc) => ((Def)aniThing).defName.Contains(wc, StringComparison.OrdinalIgnoreCase))))))
			{
				flag = true;
				num = 0.5f;
			}
			else
			{
				flag = HasPartWithTag(allBodyPartsRecursive, BodyPartTagDefOf.ManipulationLimbCore, blackListKeyword) || HasPartWithTag(allBodyPartsRecursive, BodyPartTagDefOf.ManipulationLimbDigit, blackListKeyword) || HasPartWithTag(allBodyPartsRecursive, BodyPartTagDefOf.ManipulationLimbSegment, blackListKeyword);
				num = (flag ? 1f : 0f);
			}
			if (allAnimalsHaveHands)
			{
				num = 1f;
				flag = true;
			}
			val3 = new HediffDef
			{
				defName = defName2,
				hediffClass = typeof(RaceTracker),
				isBad = false,
				everCurableByItem = false,
				initialSeverity = 1f,
				label = ((Def)aniThing).label,
				description = ((Def)aniThing).description,
				defaultLabelColor = new Color(0.5f, 1f, 1f),
				generated = true
			};
			HediffDef val4;
			if (VanillaExpanded.VEActive)
			{
				foreach (AbilityDef item in VEF_InitialAbility_Helper.TryGetAbilities(aniThing.comps ?? new List<CompProperties>()))
				{
					val4 = val3;
					if (val4.abilities == null)
					{
						val4.abilities = new List<AbilityDef>();
					}
					val3.abilities.Add(item);
				}
			}
			val4 = val3;
			if (val4.comps == null)
			{
				val4.comps = new List<HediffCompProperties>();
			}
			val3.comps.Add((HediffCompProperties)(object)new CompProperties_Race
			{
				canSwapAwayFrom = false
			});
			PawnExtension pawnExtension2 = new PawnExtension();
			PawnExtensionDef pawnExtensionDef = ((num > 0.75f) ? BSDefs.BS_DefaultAnimal : ((num > 0.35f) ? BSDefs.BS_DefaultAnimal_PoorHands : BSDefs.BS_DefaultAnimal_NoHands));
			if (pawnExtensionDef.pawnExtension.animalFineManipulation.HasValue)
			{
				num = pawnExtensionDef.pawnExtension.animalFineManipulation.Value;
				if (num > 0.45f)
				{
					flag = true;
				}
			}
			if (!flag && !BigSmallMod.settings.animalsLowSkillPenalty)
			{
				val4 = val3;
				if (val4.stages == null)
				{
					val4.stages = new List<HediffStage>();
				}
				val3.stages.Add(new HediffStage
				{
					disabledWorkTags = (WorkTags)525568
				});
			}
			if (aniPawnKind.RaceProps.IsMechanoid)
			{
				pawnExtensionDef = BSDefs.BS_DefaultMechanoid;
			}
			foreach (FieldInfo item2 in from f in typeof(PawnExtension).GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
				where !f.IsStatic && !f.IsInitOnly
				select f)
			{
				object value = item2.GetValue(pawnExtensionDef.pawnExtension);
				if (value != null)
				{
					item2.SetValue(pawnExtension2, value);
				}
			}
			if (BigSmallMod.settings.animalsLowSkillPenalty && pawnExtension2.aptitudes != null)
			{
				foreach (Aptitude aptitude in pawnExtension2.aptitudes)
				{
					if (aptitude.level < -8)
					{
						aptitude.level = -4;
					}
					else if (aptitude.level < -4)
					{
						aptitude.level = -2;
					}
					else if (aptitude.level < 0)
					{
						aptitude.level = 0;
					}
				}
			}
			if (pawnExtension2.traitIcon == null)
			{
				List<PawnKindLifeStage> lifeStages = aniPawnKind.lifeStages;
				if (lifeStages != null && GenCollection.Any<PawnKindLifeStage>(lifeStages))
				{
					pawnExtension2.traitIcon = GetTraitIcon(aniPawnKind);
				}
			}
			pawnExtension2.animalFineManipulation = num;
			pawnExtension2.romanceTags = romanceTags;
			((Def)val3).modExtensions = new List<DefModExtension>(1) { (DefModExtension)(object)pawnExtension2 };
			pawnExtension = pawnExtension2;
		}
		GenerateProductionCompsFromAnimal(aniThing, val3);
		num = pawnExtension.animalFineManipulation ?? num;
		if (pawnExtension.traitIcon == null || pawnExtension.traitIcon == "BS_Traits/robot")
		{
			List<PawnKindLifeStage> lifeStages2 = aniPawnKind.lifeStages;
			if (lifeStages2 != null && GenCollection.Any<PawnKindLifeStage>(lifeStages2))
			{
				pawnExtension.traitIcon = GetTraitIcon(aniPawnKind);
			}
		}
		if ((double?)pawnExtension.animalFineManipulation < 0.45)
		{
			pawnExtension.canWieldThings = false;
		}
		pawnExtension.bodyTypes.Add(new GenderBodyType
		{
			bodyType = BSDefs.BS_AnimalBodyType,
			isDefault = true
		});
		PawnExtension pawnExtension3 = pawnExtension;
		if (pawnExtension3.nullsThoughts == null)
		{
			pawnExtension3.nullsThoughts = new List<ThoughtDef>();
		}
		IEnumerable<ThoughtDef> items = DefDatabase<ThoughtDef>.AllDefs.Where((ThoughtDef x) => ((Def)x).defName.Contains("uncovered", StringComparison.OrdinalIgnoreCase));
		IEnumerable<ThoughtDef> items2 = DefDatabase<ThoughtDef>.AllDefs.Where((ThoughtDef x) => ((Def)x).defName.Contains("sweat", StringComparison.OrdinalIgnoreCase));
		IEnumerable<ThoughtDef> items3 = DefDatabase<ThoughtDef>.AllDefs.Where((ThoughtDef x) => ((Def)x).defName.Contains("table", StringComparison.OrdinalIgnoreCase));
		pawnExtension.nullsThoughts.AddDistinctRange(items);
		pawnExtension.nullsThoughts.AddDistinctRange(items2);
		pawnExtension.nullsThoughts.AddDistinctRange(items3);
		if (aniPawnKind.abilities != null)
		{
			HediffDef val4 = val3;
			if (val4.abilities == null)
			{
				val4.abilities = new List<AbilityDef>();
			}
			val3.abilities.AddRange(aniPawnKind.abilities);
		}
		RaceExtension raceExtension = new RaceExtension();
		raceExtension.SetHediff(val3);
		((Def)val).generated = true;
		((Def)val).label = ((Def)aniThing).label;
		((Def)val).description = ((Def)aniThing).description;
		val.race = val2;
		((Def)val).modExtensions.Add((DefModExtension)(object)raceExtension);
		SetAnimalStatDefValues(humThing, aniThing, val, num, pawnExtension);
		if (val2.gestationPeriodDays == -1f)
		{
			val2.gestationPeriodDays = race2.gestationPeriodDays;
			if (ModsConfig.BiotechActive)
			{
				StatExtension.SetStatBaseValue((BuildableDef)(object)val, StatDefOf.Fertility, 0f);
			}
		}
		DefGenerator.AddImpliedDef<ThingDef>(val, true);
		DefGenerator.AddImpliedDef<BodyDef>(val2.body, true);
		DefGenerator.AddImpliedDef<HediffDef>(val3, true);
		((Editable)val).ResolveReferences();
		((Editable)val3).ResolveReferences();
		humanlikeAnimals[val] = new HumanlikeAnimal
		{
			humanlikeAnimal = val,
			animalKind = aniPawnKind,
			humanlike = humThing,
			animal = aniThing
		};
		static string GetTraitIcon(PawnKindDef aniPawnKind)
		{
			return aniPawnKind.lifeStages.Last().bodyGraphicData.texPath + "_east";
		}
	}

	private static void GenerateProductionCompsFromAnimal(ThingDef aniThing, HediffDef raceHediff)
	{
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
		List<HediffCompProperties> comps = raceHediff.comps;
		if (comps != null && GenCollection.Any<HediffCompProperties>(comps, (Predicate<HediffCompProperties>)((HediffCompProperties x) => x is ProductionHediffSettings)))
		{
			return;
		}
		foreach (CompProperties_Milkable item in aniThing.comps?.Where((CompProperties x) => x is CompProperties_Milkable) ?? Array.Empty<CompProperties>())
		{
			ThingDef milkDef = item.milkDef;
			int milkAmount = item.milkAmount;
			int milkIntervalDays = item.milkIntervalDays;
			bool milkFemaleOnly = item.milkFemaleOnly;
			GenerateProductionComp(raceHediff, milkDef, milkAmount, milkIntervalDays, milkFemaleOnly);
		}
		foreach (CompProperties_Shearable item2 in aniThing.comps?.Where((CompProperties x) => x is CompProperties_Shearable) ?? Array.Empty<CompProperties>())
		{
			ThingDef woolDef = item2.woolDef;
			int woolAmount = item2.woolAmount;
			int shearIntervalDays = item2.shearIntervalDays;
			GenerateProductionComp(raceHediff, woolDef, woolAmount, shearIntervalDays);
		}
		foreach (CompProperties_EggLayer item3 in aniThing.comps?.Where((CompProperties x) => x is CompProperties_EggLayer) ?? Array.Empty<CompProperties>())
		{
			ThingDef eggUnfertilizedDef = item3.eggUnfertilizedDef;
			int quantity = Mathf.CeilToInt(((IntRange)(ref item3.eggCountRange)).Average);
			int frequency = Mathf.CeilToInt(item3.eggLayIntervalDays);
			bool eggLayFemaleOnly = item3.eggLayFemaleOnly;
			GenerateProductionComp(raceHediff, eggUnfertilizedDef, quantity, frequency, eggLayFemaleOnly);
		}
		foreach (CompProperties item4 in aniThing.comps.Where((CompProperties x) => ((object)x).GetType().Name == "CompProperties_AnimalProduct"))
		{
			FieldInfo field = ((object)item4).GetType().GetField("resourceDef");
			FieldInfo field2 = ((object)item4).GetType().GetField("resourceAmount");
			FieldInfo field3 = ((object)item4).GetType().GetField("gatheringIntervalDays");
			if (!(field != null) || !(field2 != null) || !(field3 != null))
			{
				continue;
			}
			int quantity2 = (int)field2.GetValue(item4);
			int frequency2 = (int)field3.GetValue(item4);
			object value = field.GetValue(item4);
			ThingDef val4 = (ThingDef)((value is ThingDef) ? value : null);
			if (val4 != null)
			{
				GenerateProductionComp(raceHediff, val4, quantity2, frequency2);
			}
			if (((object)item4).GetType().GetField("randomItems")?.GetValue(item4) is List<string> list)
			{
				_ = list.Count;
				List<ThingDef> list2 = (from def in ((IEnumerable<string>)list).Select((Func<string, ThingDef>)DefDatabase<ThingDef>.GetNamedSilentFail)
					where def != null
					select def).ToList();
				if (list2.Count != 0)
				{
					GenerateProductionComp(raceHediff, null, quantity2, frequency2, femaleOnly: false, list2);
				}
			}
		}
	}

	private static void GenerateProductionComp(HediffDef raceHediff, ThingDef product, int quantity, int frequency, bool femaleOnly = false, List<ThingDef> rngOptions = null, float chance = 1f)
	{
		if (rngOptions == null)
		{
			rngOptions = new List<ThingDef>();
		}
		string text = ((product != null) ? ((Def)product).defName : "RandomProduct");
		ProductionHediffSettings pSettings = new ProductionHediffSettings
		{
			frequencyInDays = frequency,
			progressName = "ResourceGrowth",
			saveKey = ((Def)raceHediff).defName + "_ResourceGrowth_" + text,
			activationAge = 13,
			chance = chance,
			femaleOnly = femaleOnly,
			products = new List<ProductionHediffSettings.ProductionSettings>(1)
			{
				new ProductionHediffSettings.ProductionSettings
				{
					product = product,
					randomProduct = rngOptions,
					baseAmount = quantity
				}
			}
		};
		while (GenCollection.Any<HediffCompProperties>(raceHediff.comps, (Predicate<HediffCompProperties>)((HediffCompProperties x) => x.compClass == ((HediffCompProperties)pSettings).compClass)))
		{
			Type compClass = pSettings.NextFromThis();
			((HediffCompProperties)pSettings).compClass = compClass;
			if (pSettings == null)
			{
				Log.Warning("Could not add production hediff for " + ((Def)(product?)).defName + " to " + ((Def)(raceHediff?)).defName + " due to too many comp class name collisions.");
				return;
			}
		}
		raceHediff.comps.Add((HediffCompProperties)(object)pSettings);
	}

	private static void SetRenderTree(PawnKindDef aniPawnKind, ThingDef aniThing, RaceProperties aniRace, RaceProperties humRace, RaceProperties newRace)
	{
		bool flag = false;
		List<RenderTreeOverride> list = new List<RenderTreeOverride>();
		foreach (HumanlikeAnimalSettings allHASetting in HumanlikeAnimalSettings.AllHASettings)
		{
			list.AddRange(allHASetting.renderTreeWhitelist);
		}
		foreach (RenderTreeOverride item in list)
		{
			if (item.thingDefNames.Contains(((Def)aniThing).defName, StringComparer.OrdinalIgnoreCase))
			{
				newRace.renderTree = DefDatabase<PawnRenderTreeDef>.GetNamed(item.renderTreeDefName, true);
				flag = true;
				break;
			}
		}
		if (flag)
		{
			return;
		}
		if (((Def)newRace.renderTree).defName == "Animal" || ((Def)newRace.renderTree).defName == "Misc")
		{
			newRace.renderTree = DefDatabase<PawnRenderTreeDef>.GetNamed("BS_HumanlikeAnimal", true);
		}
		else if (!(((Def)newRace.renderTree).defName == "Human"))
		{
			if (aniRace.Humanlike)
			{
				Log.WarningOnce("Unhandled Render-Tree: " + ((Def)aniPawnKind).defName + " has an unhandled render tree: " + ((Def)newRace.renderTree).defName + ". It will likely not render as expected if made sapient. Keeping previous.\nNo warning of this type will be sent to avoid spamming the log.", 6661337);
				newRace.renderTree = humRace.renderTree;
			}
			else
			{
				Log.WarningOnce("Unhandled Render-Tree: " + ((Def)aniPawnKind).defName + " has an unhandled render tree: " + ((Def)newRace.renderTree).defName + ". It will likely not render as expected if made sapient. Defaulting to BS_HumanlikeAnimal.\nNo warning of this type will be sent to avoid spamming the log.", 6661338);
				newRace.renderTree = DefDatabase<PawnRenderTreeDef>.GetNamed("BS_HumanlikeAnimal", true);
			}
		}
	}

	private static void GetPartsRecursive(BodyPartRecord part, List<BodyPartRecord> parts)
	{
		parts.Add(part);
		foreach (BodyPartRecord part2 in part.parts)
		{
			GetPartsRecursive(part2, parts);
		}
	}

	private static void SetupBodyTags(ThingDef newThing, RaceProperties newRace)
	{
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Expected O, but got Unknown
		if (!modifiedBodies.Add(newRace.body))
		{
			return;
		}
		bool foundUtilitySlot = false;
		BodyPartDef def = DefDatabase<BodyPartDef>.AllDefs.FirstOrDefault((BodyPartDef x) => ((Def)x).defName == "BS_InorganicWaist");
		BodyPartGroupDef armGrp = DefDatabase<BodyPartGroupDef>.AllDefs.FirstOrDefault((BodyPartGroupDef x) => ((Def)x).defName == "Arms");
		DefDatabase<BodyPartGroupDef>.AllDefs.FirstOrDefault((BodyPartGroupDef x) => ((Def)x).defName == "Shoulders");
		BodyPartGroupDef item = DefDatabase<BodyPartGroupDef>.AllDefs.FirstOrDefault((BodyPartGroupDef x) => ((Def)x).defName == "Waist");
		List<string> multiUseTorso = new List<string>(1) { "snakebody" };
		List<string> legAndArmParts = new List<string>(1) { "tentacle" };
		List<string> legParts = new List<string>(2) { "leg", "snakeBody" };
		List<string> armParts = new List<string>(2) { "arm", "wing" };
		List<BodyPartRecord> list = new List<BodyPartRecord>();
		GetPartsRecursive(newRace.body.corePart, list);
		list.ForEach(delegate(BodyPartRecord part)
		{
			if (((Def)part.def).defName == "Waist")
			{
				foundUtilitySlot = true;
			}
			if (part == newRace.body.corePart)
			{
				TryAddTags(newThing, part, multiUseTorso, new List<BodyPartGroupDef>(2)
				{
					BodyPartGroupDefOf.Torso,
					BodyPartGroupDefOf.Legs
				});
				AddGroupIfNoneDefined(part, new List<BodyPartGroupDef>(1) { BodyPartGroupDefOf.Torso }, newThing);
			}
			else if (!TryAddTags(newThing, part, legAndArmParts, new List<BodyPartGroupDef>(2)
			{
				BodyPartGroupDefOf.Legs,
				armGrp
			}) && !TryAddTags(newThing, part, legParts, new List<BodyPartGroupDef>(1) { BodyPartGroupDefOf.Legs }))
			{
				TryAddTags(newThing, part, armParts, new List<BodyPartGroupDef>(1) { armGrp });
			}
		});
		if (!foundUtilitySlot)
		{
			BodyPartRecord corePart = newRace.body.corePart;
			BodyPartRecord item2 = new BodyPartRecord
			{
				def = def,
				coverage = 0f,
				parent = corePart,
				groups = new List<BodyPartGroupDef>(1) { item }
			};
			corePart.parts.Add(item2);
		}
	}

	private static bool TryAddTags(ThingDef newThing, BodyPartRecord part, List<string> tags, List<BodyPartGroupDef> grp)
	{
		bool num = GenCollection.Any<string>(tags, (Predicate<string>)((string tag) => ((Def)part.def).defName.ToLower().Contains(tag)));
		bool flag = part.parent != null && GenCollection.Any<string>(tags, (Predicate<string>)((string tag) => ((Def)part.parent.def).defName.ToLower().Contains(tag)));
		if (num || flag)
		{
			AddGroupIfNoneDefined(part, grp, newThing);
			return true;
		}
		return false;
	}

	private static void AddGroupIfNoneDefined(BodyPartRecord part, List<BodyPartGroupDef> groupToAdd, ThingDef thingDef)
	{
		if (GenList.NullOrEmpty<BodyPartGroupDef>((IList<BodyPartGroupDef>)part.groups))
		{
			part.groups = groupToAdd;
		}
	}

	public static void SetAnimalStatDefValues(ThingDef humanThing, ThingDef animalThing, ThingDef newThing, float fineManipulation, PawnExtension pExt)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Expected O, but got Unknown
		//IL_0501: Unknown result type (might be due to invalid IL or missing references)
		//IL_0601: Unknown result type (might be due to invalid IL or missing references)
		//IL_055a: Unknown result type (might be due to invalid IL or missing references)
		((BuildableDef)newThing).statBases = new List<StatModifier>();
		foreach (StatModifier statBasis in ((BuildableDef)humanThing).statBases)
		{
			((BuildableDef)newThing).statBases.Add(new StatModifier
			{
				stat = statBasis.stat,
				value = statBasis.value
			});
		}
		float baseBodySize = animalThing.race.baseBodySize;
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PsychicSensitivity, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.PsychicSensitivity, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PawnBeauty, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.PawnBeauty, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MoveSpeed, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MoveSpeed, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.IncomingDamageFactor, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.IncomingDamageFactor, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MarketValue, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MarketValue, (ThingDef)null) * 1.5f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.Mass, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.Mass, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ToxicResistance, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ToxicResistance, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ToxicEnvironmentResistance, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ToxicEnvironmentResistance, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.CarryingCapacity, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.CarryingCapacity, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ComfyTemperatureMax, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ComfyTemperatureMax, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ComfyTemperatureMin, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ComfyTemperatureMin, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.LeatherAmount, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.LeatherAmount, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MeatAmount, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MeatAmount, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.FlightCooldown, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.FlightCooldown, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MaxFlightTime, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MaxFlightTime, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ArmorRating_Sharp, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ArmorRating_Sharp, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ArmorRating_Blunt, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ArmorRating_Blunt, (ThingDef)null));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ArmorRating_Heat, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ArmorRating_Heat, (ThingDef)null));
		float val = StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.Nutrition, (ThingDef)null) * baseBodySize;
		float statValueAbstract = StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.Nutrition, (ThingDef)null);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.Nutrition, Math.Max(statValueAbstract, val));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.DeepDrillingSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.DeepDrillingSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.DeepDrillingSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MiningSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MiningSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.MiningSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MiningYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MiningYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.MiningYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ConstructionSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.ConstructionSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.ConstructionSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.SmoothingSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.SmoothingSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.SmoothingSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantHarvestYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.PlantHarvestYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.PlantHarvestYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantWorkSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.PlantWorkSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.PlantWorkSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantHarvestYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.PlantHarvestYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.PlantHarvestYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MeleeDodgeChance, (StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.MeleeDodgeChance, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.MeleeDodgeChance, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.FilthRate, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.FilthRate, (ThingDef)null) / 3f + StatExtension.GetStatValueAbstract((BuildableDef)(object)humanThing, StatDefOf.FilthRate, (ThingDef)null) / 3f * 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.FlightCooldown, StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, StatDefOf.FlightCooldown, (ThingDef)null) / 2f);
		if ((double)fineManipulation < 0.99)
		{
			float num = Mathf.Lerp(1f, 0.65f, fineManipulation);
			StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.WorkSpeedGlobal, StatExtension.GetStatValueAbstract((BuildableDef)(object)newThing, StatDefOf.WorkSpeedGlobal, (ThingDef)null) * num);
			float num2 = Mathf.Lerp(1f, 0.5f, fineManipulation);
			StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.SurgerySuccessChanceFactor, StatExtension.GetStatValueAbstract((BuildableDef)(object)newThing, StatDefOf.SurgerySuccessChanceFactor, (ThingDef)null) * num2);
		}
		if (pExt.isMechanical || animalThing.race.IsMechanoid)
		{
			if (ModsConfig.BiotechActive)
			{
				StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.Fertility, 0f);
			}
			StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, BSDefs.BS_BatteryCharging, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)animalThing, BSDefs.BS_BatteryCharging, (ThingDef)null), 1.6f));
		}
		if (animalThing.race.Animal && animalThing.race.Insect && pExt.romanceTags == null)
		{
			pExt.romanceTags = new RomanceTags
			{
				compatibilities = new Dictionary<string, RomanceTags.Compatibility> { [TaggedString.op_Implicit(Translator.Translate("BS_Insect"))] = new RomanceTags.Compatibility
				{
					chance = 1f,
					factor = 1f
				} }
			};
			if (BigSmallMod.settings.animalOnAnimal)
			{
				pExt.romanceTags.compatibilities[TaggedString.op_Implicit(Translator.Translate("BS_SapientAnimal"))] = new RomanceTags.Compatibility
				{
					chance = 0.75f,
					factor = 1f
				};
			}
		}
		else if (animalThing.race.Animal)
		{
			if (pExt.romanceTags == null)
			{
				pExt.romanceTags = new RomanceTags
				{
					compatibilities = new Dictionary<string, RomanceTags.Compatibility> { [((Def)animalThing).label] = new RomanceTags.Compatibility
					{
						chance = 1f,
						factor = 1f
					} }
				};
			}
			if (BigSmallMod.settings.animalOnAnimal)
			{
				pExt.romanceTags.compatibilities[TaggedString.op_Implicit(Translator.Translate("BS_SapientAnimal"))] = new RomanceTags.Compatibility
				{
					chance = 0.75f,
					factor = 1f
				};
			}
		}
	}

	private static bool HasPartWithTag(List<BodyPartRecord> parts, BodyPartTagDef tag, List<string> blackListKeyword)
	{
		for (int i = 0; i < parts.Count; i++)
		{
			BodyPartRecord val = parts[i];
			if (val.def.tags.Contains(tag) && !GenCollection.Any<string>(blackListKeyword, (Predicate<string>)((Def)val.def).defName.Contains))
			{
				return true;
			}
		}
		return false;
	}
}
