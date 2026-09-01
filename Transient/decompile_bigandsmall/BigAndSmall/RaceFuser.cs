using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using BigAndSmall.ModPatches;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class RaceFuser
{
	internal static class ShortHashWrapper
	{
		private static Action<Def, Type, HashSet<ushort>> giveHashDelegate;

		private static FieldRef<Dictionary<Type, HashSet<ushort>>> takenHashesFieldRef;

		static ShortHashWrapper()
		{
			giveHashDelegate = AccessTools.MethodDelegate<Action<Def, Type, HashSet<ushort>>>(AccessTools.Method(typeof(ShortHashGiver), "GiveShortHash", new Type[3]
			{
				typeof(Def),
				typeof(Type),
				typeof(HashSet<ushort>)
			}, (Type[])null), (object)null, true, (Type[])null);
			takenHashesFieldRef = AccessTools.StaticFieldRefAccess<Dictionary<Type, HashSet<ushort>>>(AccessTools.Field(typeof(ShortHashGiver), "takenHashesPerDeftype"));
		}

		internal static void GiveShortHash<T>(T def) where T : Def
		{
			Dictionary<Type, HashSet<ushort>> dictionary = takenHashesFieldRef.Invoke();
			if (!dictionary.ContainsKey(typeof(T)))
			{
				dictionary[typeof(T)] = new HashSet<ushort>();
			}
			HashSet<ushort> arg = dictionary[typeof(T)];
			giveHashDelegate((Def)(object)def, null, arg);
		}
	}

	public const string MESH_DEF = "Mech";

	public const string MESH_LABEL = "BS_Mech";

	public static bool doDebug = false;

	public static HashSet<BodyDef> bodyDefsAdded = new HashSet<BodyDef>();

	public static HashSet<ThingDef> thingDefsAdded = new HashSet<ThingDef>();

	private static Dictionary<BodyPartDef, List<BodyPartDef>> _mechanicalVersionOf = null;

	public static void PreHotreload()
	{
		FusedBody.FusedBodies.Clear();
		FusedBody.FusedBodyByThing.Clear();
		bodyDefsAdded.ToList().ForEach(delegate(BodyDef bodyDef)
		{
			bodyDef.AllParts.Clear();
		});
	}

	/// <summary>
	/// Merge body parts.
	/// </summary>
	public static void CreateMergedBodyTypes(bool hotReload)
	{
		//IL_0239: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cf: Unknown result type (might be due to invalid IL or missing references)
		BodyDefFusionsHelper.SetupSubstitutableTrackers();
		if (doDebug)
		{
			Log.Message("Found Mergable Bodies: " + GenText.ToCommaList(BodyDefFusionsHelper.MergableBodies.Select((MergableBody x) => ((Def)x.bodyDef).defName), false, false));
		}
		List<MergableBody> list = (from x in DefDatabase<BodyDef>.AllDefsListForReading
			where GenCollection.Any<MergableBody>(BodyDefFusionsHelper.MergableBodies, (Predicate<MergableBody>)((MergableBody y) => y.bodyDef == x))
			select BodyDefFusionsHelper.MergableBodies.First((MergableBody y) => y.bodyDef == x)).ToList();
		if (doDebug)
		{
			Log.Message($"Merging {list.Count} body types.");
			Log.Message("Merging " + GenText.ToCommaList(list.Select((MergableBody x) => ((Def)x.bodyDef).defName), false, false));
		}
		if (list.Count < 2)
		{
			return;
		}
		list = list.OrderByDescending((MergableBody x) => x.priority).ToList();
		List<MergableBody> list2 = BodyDefFusionsHelper.MergableBodies.Where((MergableBody x) => x.fuseAll).ToList();
		List<List<MergableBody>> list3 = new List<List<MergableBody>>();
		int count = list2.Count;
		for (int i = 0; i < 1 << count; i++)
		{
			List<MergableBody> list4 = new List<MergableBody>();
			for (int j = 0; j < count; j++)
			{
				if ((i & (1 << j)) != 0)
				{
					list4.Add(list2[j]);
				}
			}
			list3.Add(list4);
		}
		List<MergableBody> fuseSets = BodyDefFusionsHelper.MergableBodies.Where((MergableBody x) => x.fuseSet).ToList();
		RunStandardFusions(list, list3);
		RunFuseSetsOnFused(fuseSets);
		RunFuseSetsOnSources(list, fuseSets);
		GenerateAndRegisterRaceDefs(hotReload);
		if (!doDebug)
		{
			return;
		}
		Log.Message("------------------------------------------------------\nSources:\n------------------------------------------------------");
		foreach (MergableBody item in list)
		{
			Log.Message($"* {((Def)item.bodyDef).LabelCap}");
		}
		Log.Message("------------------------------------------------------\nResults:\n------------------------------------------------------");
		foreach (FusedBody value in FusedBody.FusedBodies.Values)
		{
			string arg = string.Join(", ", value.mergableBodies.Select((MergableBody x) => ((Def)x.bodyDef).LabelCap));
			Log.Message($"{((Def)value.generatedBody).LabelCap,-45} (bp: {value.generatedBody.AllParts.Count}, src: {arg})");
		}
	}

	private static void RunFuseSetsOnFused(List<MergableBody> fuseSets)
	{
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		List<FusedBody> list = FusedBody.FusedBodies.Values.ToList();
		if (doDebug)
		{
			Log.Message($"Running FuseSets on Fused. There are {fuseSets.Count} sets to fuse and {list.Count} targets to fuse them with");
		}
		foreach (MergableBody item in fuseSets.Where((MergableBody x) => x.fuseSet))
		{
			foreach (FusedBody item2 in list.Where((FusedBody x) => !x.fake))
			{
				string defName = item.overrideDefNamer ?? ((Def)item.bodyDef).defName;
				BodyDef val = MakeBodyDef(item, defName, mechanicalAlt: true, item2.mergableBodies);
				ClonePartsRecursive(null, item2.generatedBody.corePart, val, item2.mergableBodies[0], new List<BodyPartRecord>(), item.isMechanical);
				bool isMechanical = item.isMechanical;
				MergableBody mergableBody = item;
				MergableBody[] mergableBodies = item2.mergableBodies;
				int num = 0;
				MergableBody[] array = new MergableBody[1 + mergableBodies.Length];
				array[num] = mergableBody;
				num++;
				ReadOnlySpan<MergableBody> val2 = new ReadOnlySpan<MergableBody>(mergableBodies);
				val2.CopyTo(new Span<MergableBody>(array).Slice(num, val2.Length));
				num += val2.Length;
				new FusedBody(val, item, isMechanical, array);
				if (doDebug)
				{
					Log.Message("FuseSets->Fused: " + ((Def)val).defName + " from " + ((Def)item2.generatedBody).defName + " and " + ((Def)item.bodyDef).defName);
				}
			}
		}
	}

	private static void RunFuseSetsOnSources(List<MergableBody> bodyDefsToMerge, List<MergableBody> fuseSets)
	{
		if (doDebug)
		{
			Log.Message($"Running FuseSets on Sources. There are {fuseSets.Count} sets to fuse, and {bodyDefsToMerge.Count} sources to fuse them with.");
		}
		foreach (MergableBody fusedSetBody in fuseSets.Where((MergableBody x) => x.fuseSet))
		{
			foreach (MergableBody item in bodyDefsToMerge.Where((MergableBody x) => x != fusedSetBody && (!fusedSetBody.isMechanical || x.canMakeRobotVersion)))
			{
				string defName = fusedSetBody.overrideDefNamer ?? ((Def)fusedSetBody.bodyDef).defName;
				BodyDef val = MakeBodyDef(fusedSetBody, defName, fusedSetBody.isMechanical, item);
				ClonePartsRecursive(null, item.bodyDef.corePart, val, item, new List<BodyPartRecord>(), fusedSetBody.isMechanical);
				new FusedBody(val, fusedSetBody, fusedSetBody.isMechanical, fusedSetBody, item);
				if (doDebug)
				{
					Log.Message("FuseSets->Source: " + ((Def)val).defName + " from " + ((Def)item.bodyDef).defName + " and " + ((Def)fusedSetBody.bodyDef).defName);
				}
			}
		}
	}

	private static void RunStandardFusions(List<MergableBody> bodyDefsToMerge, List<List<MergableBody>> allFusionCombinations)
	{
		foreach (MergableBody bodyOne in bodyDefsToMerge.Where((MergableBody x) => x.canBeFusionOne))
		{
			foreach (MergableBody bodyTwo in bodyDefsToMerge.Where((MergableBody x) => x != bodyOne && !FusedBody.HasKey(bodyOne.isMechanical, bodyOne.bodyDef, x.bodyDef) && bodyOne.Fuse && x.Fuse))
			{
				new List<BodyDef>();
				foreach (List<MergableBody> fusionCombo in allFusionCombinations)
				{
					if (fusionCombo.Contains(bodyOne) || fusionCombo.Contains(bodyTwo) || bodyOne.exclusionTags.Intersect(bodyTwo.exclusionTags).Any() || GenCollection.Any<MergableBody>(fusionCombo, (Predicate<MergableBody>)((MergableBody x) => bodyOne.exclusionTags.Intersect(x.exclusionTags).Any() || bodyTwo.exclusionTags.Intersect(x.exclusionTags).Any() || GenCollection.Any<MergableBody>(fusionCombo, (Predicate<MergableBody>)((MergableBody y) => y != x && x.exclusionTags.Intersect(y.exclusionTags).Any())))))
					{
						continue;
					}
					BodyDef[] bodyDefs = fusionCombo.Select((MergableBody x) => x.bodyDef).Concat(new _003C_003Ez__ReadOnlyArray<BodyDef>((BodyDef[])(object)new BodyDef[2] { bodyOne.bodyDef, bodyTwo.bodyDef })).ToArray();
					if (FusedBody.HasKey(mechanical: false, bodyDefs))
					{
						continue;
					}
					bodyOne.bodyDef.AllParts.ToList();
					List<MergableBody> list = fusionCombo.ToList();
					list.Insert(0, bodyTwo);
					string newDefName = bodyOne.overrideDefNamer ?? ((Def)bodyOne.bodyDef).defName;
					BodyDef val = DefDatabase<BodyDef>.AllDefs.FirstOrDefault((BodyDef x) => ((Def)x).defName == newDefName);
					BodyDef val2;
					if (val != null)
					{
						val2 = val;
					}
					else
					{
						val2 = MakeBodyDef(bodyOne, newDefName, mechanicalAlt: false, list.ToArray());
						ClonePartsRecursive(null, bodyOne.bodyDef.corePart, val2, bodyOne, new List<BodyPartRecord>(), makeMechanical: false);
						foreach (MergableBody item in list)
						{
							BodyPartRecord corePart = item.bodyDef.corePart;
							List<BodyPartRecord> unTransfereredParts = (from x in item.bodyDef.corePart.GetAllBodyPartsRecursive()
								where !bodyOne.ShouldRemovePart(x.def)
								select x).ToList();
							_ = val2.corePart;
							MergeRecursively(val2.corePart, corePart, unTransfereredParts, bodyOne);
						}
					}
					BodyDef generatedBody = val2;
					bool mechanical = bodyOne.isMechanical || GenCollection.Any<MergableBody>(list, (Predicate<MergableBody>)((MergableBody x) => x.isMechanical));
					MergableBody mergableBody = bodyOne;
					List<MergableBody> list2 = list;
					int num = 0;
					MergableBody[] array = new MergableBody[1 + list2.Count];
					array[num] = mergableBody;
					num++;
					foreach (MergableBody item2 in list2)
					{
						array[num] = item2;
						num++;
					}
					new FusedBody(generatedBody, null, mechanical, array);
				}
			}
		}
	}

	private static BodyDef MakeBodyDef(MergableBody bodyOne, string defName, bool mechanicalAlt, params MergableBody[] bodyTwoArray)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Expected O, but got Unknown
		if (bodyOne.prefixLabel == null)
		{
			TaggedString.op_Implicit(((Def)bodyOne.bodyDef).LabelCap);
		}
		string text = "";
		string obj = (mechanicalAlt ? "M" : "G");
		if (bodyOne.prefixLabel == null)
		{
			TaggedString.op_Implicit(((Def)bodyOne.bodyDef).LabelCap);
		}
		text = string.Concat(str2: TaggedString.op_Implicit(Translator.Translate("BS_With") + " " + string.Join(string.Format(" {0} ", Translator.Translate("BS_And")), bodyTwoArray.Select((MergableBody x) => x.suffixLabel ?? ((Def)x.bodyDef).label))), str0: bodyOne.prefixLabel, str1: " ");
		List<string> values = bodyTwoArray.Select((MergableBody x) => x.overrideDefNamer ?? ((Def)x.bodyDef).defName).ToList();
		string text2 = (obj + "_" + defName + string.Join("", values)).Trim();
		BodyDef val = text2.TryGetExistingDef<BodyDef>();
		if (val == null)
		{
			val = new BodyDef();
		}
		((Def)val).defName = text2;
		((Def)val).description = ((Def)bodyOne.bodyDef).description;
		((Def)val).label = text;
		if (doDebug)
		{
			Log.Message("Creating " + ((Def)val).defName + " from " + text2);
		}
		return val;
	}

	private static string GetPartsStringRecursive(BodyPartRecord source, string indent = "")
	{
		string text = $"{indent}{source.LabelCap} ({source.coverage * 100f:f0}%)\n";
		foreach (BodyPartRecord part in source.parts)
		{
			text += GetPartsStringRecursive(part, indent + "  ");
		}
		return text;
	}

	public static List<BodyPartRecord> GetAllBodyPartsRecursive(this BodyPartRecord source)
	{
		List<BodyPartRecord> list = new List<BodyPartRecord>(1) { source };
		foreach (BodyPartRecord part in source.parts)
		{
			list.AddRange(part.GetAllBodyPartsRecursive());
		}
		return list;
	}

	private static void GenerateAndRegisterRaceDefs(bool hotReload)
	{
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Expected O, but got Unknown
		//IL_0438: Unknown result type (might be due to invalid IL or missing references)
		foreach (FusedBody value in FusedBody.FusedBodies.Values)
		{
			BodyDef generatedBody = value.generatedBody;
			MergableBody sourceBody = value.SourceBody;
			if (doDebug)
			{
				Log.Message(GetPartsStringRecursive(generatedBody.corePart));
			}
			ThingDef thingDef = sourceBody.thingDef;
			RaceProperties race = thingDef.race;
			string defName = ((Def)generatedBody).defName ?? "";
			string defName2 = ((Def)generatedBody).defName;
			ThingDef val = defName.TryGetExistingDef<ThingDef>();
			defName2.TryGetExistingDef<BodyDef>();
			RaceProperties val2 = new RaceProperties();
			if (val == null)
			{
				object obj = ((object)thingDef).GetType().GetConstructor(Array.Empty<Type>()).Invoke(Array.Empty<object>());
				val = (ThingDef)((obj is ThingDef) ? obj : null);
			}
			CopyThingDefFields(thingDef, val);
			List<ThingDef> source = value.mergableBodies.Select((MergableBody x) => x.thingDef).ToList();
			val.recipes = (from x in source.Where((ThingDef x) => x.recipes != null).SelectMany((ThingDef x) => x?.recipes)
				where x != null
				select x).ToList().Distinct().ToList();
			val.thingCategories = (from x in source.Where((ThingDef x) => x.thingCategories != null).SelectMany((ThingDef x) => x?.thingCategories)
				where x != null
				select x).ToList().Distinct().ToList();
			((Def)val).modExtensions = ((((Def)thingDef).modExtensions != null) ? ((Def)thingDef).modExtensions.ToList() : new List<DefModExtension>());
			val.comps = ((thingDef.comps != null) ? thingDef.comps.ToList() : null);
			val.thingCategories = ((thingDef.thingCategories != null) ? thingDef.thingCategories.ToList() : new List<ThingCategoryDef>());
			val.recipes = ((thingDef.recipes != null) ? thingDef.recipes.ToList() : null);
			val.tools = ((thingDef.tools != null) ? thingDef.tools.ToList() : null);
			val.inspectorTabs = ((thingDef.inspectorTabs != null) ? thingDef.inspectorTabs.ToList() : null);
			val.inspectorTabsResolved = ((thingDef.inspectorTabsResolved != null) ? thingDef.inspectorTabsResolved.ToList() : null);
			val.tradeTags = ((thingDef.tradeTags != null) ? thingDef.tradeTags.ToList() : null);
			val.verbs = ((thingDef.verbs != null) ? thingDef.verbs.ToList() : null);
			((BuildableDef)val).stuffCategories = ((((BuildableDef)thingDef).stuffCategories != null) ? ((BuildableDef)thingDef).stuffCategories.ToList() : null);
			val.thingSetMakerTags = ((thingDef.thingSetMakerTags != null) ? thingDef.thingSetMakerTags.ToList() : null);
			val.butcherProducts = ((thingDef.butcherProducts != null) ? thingDef.butcherProducts.ToList() : null);
			val.smeltProducts = ((thingDef.smeltProducts != null) ? thingDef.smeltProducts.ToList() : null);
			val.virtualDefs = ((thingDef.virtualDefs != null) ? thingDef.virtualDefs.ToList() : null);
			if (val.inspectorTabs != null)
			{
				val.inspectorTabs = val.inspectorTabs.Distinct().ToList();
			}
			if (val.inspectorTabsResolved != null)
			{
				val.inspectorTabsResolved = val.inspectorTabsResolved.Distinct().ToList();
			}
			CopyRaceProperties(race, val2);
			if (race.hasMeat)
			{
				if (race.useMeatFrom != null)
				{
					val2.useMeatFrom = race.useMeatFrom;
				}
				else
				{
					val2.useMeatFrom = thingDef;
				}
			}
			else
			{
				val2.specificMeatDef = BSDefs.BS_MeatGeneric;
			}
			val2.body = race.body;
			val2.renderTree = race.renderTree;
			((Def)val).generated = true;
			((Def)val).defName = defName;
			((Def)val).label = TaggedString.op_Implicit(((Def)generatedBody).LabelCap);
			val.race = val2;
			val2.body = generatedBody;
			((Def)generatedBody).generated = true;
			RaceExtension item = new RaceExtension(source.SelectMany((ThingDef x) => x.ExtensionsOnDef<RaceExtension, ThingDef>((List<Type>)null, (List<Type>)null, doSort: true)).ToList())
			{
				isFusionOf = value.mergableBodies.Select((MergableBody x) => x.thingDef).ToList()
			};
			ThingDef val3 = val;
			if (((Def)val3).modExtensions == null)
			{
				((Def)val3).modExtensions = new List<DefModExtension>();
			}
			((Def)val).modExtensions.RemoveAll((DefModExtension x) => x is RaceExtension);
			((Def)val).modExtensions.Add((DefModExtension)(object)item);
			MergableBody fuseSetBody = value.fuseSetBody;
			if (fuseSetBody != null)
			{
				ThingDef thingDef2 = fuseSetBody.thingDef;
				_ = thingDef2.race;
				val.butcherProducts = thingDef2.butcherProducts.ToList();
				val.ingredient = thingDef2.ingredient;
				MergeStatDefValues(thingDef2, thingDef, val);
			}
			val2.corpseDef = null;
			val2.linkedCorpseKind = null;
			val2.hasCorpse = false;
			((object)val2).GetType().GetField("hasUnnaturalCorpse")?.SetValue(val2, false);
			value.SetThing(val);
			val2.body.cachedPartsByTag.Clear();
			val2.body.cachedPartsByDef.Clear();
			bodyDefsAdded.Add(val2.body);
			thingDefsAdded.Add(val);
			DefGenerator.AddImpliedDef<ThingDef>(val, true);
			DefGenerator.AddImpliedDef<BodyDef>(val2.body, true);
			((Editable)val).ResolveReferences();
		}
	}

	public static void MergeStatDefValues(ThingDef priorityThing, ThingDef secondaryThing, ThingDef newThing)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Expected O, but got Unknown
		((BuildableDef)newThing).statBases = new List<StatModifier>();
		foreach (StatModifier statBasis in ((BuildableDef)priorityThing).statBases)
		{
			((BuildableDef)newThing).statBases.Add(new StatModifier
			{
				stat = statBasis.stat,
				value = statBasis.value
			});
		}
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PsychicSensitivity, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.PsychicSensitivity, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.PsychicSensitivity, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.DeepDrillingSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.DeepDrillingSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.DeepDrillingSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MiningSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.MiningSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.MiningSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MiningYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.MiningYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.MiningYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ConstructionSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.ConstructionSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.ConstructionSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.SmoothingSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.SmoothingSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.SmoothingSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantHarvestYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.PlantHarvestYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.PlantHarvestYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantWorkSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.PlantWorkSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.PlantWorkSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PlantHarvestYield, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.PlantHarvestYield, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.PlantHarvestYield, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MoveSpeed, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.MoveSpeed, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.MoveSpeed, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.IncomingDamageFactor, (StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.IncomingDamageFactor, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.IncomingDamageFactor, (ThingDef)null)) / 2f);
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.PawnBeauty, Mathf.Ceil((StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.PawnBeauty, (ThingDef)null) + StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.PawnBeauty, (ThingDef)null)) / 2f));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MarketValue, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.MarketValue, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.MarketValue, (ThingDef)null)));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.Nutrition, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.Nutrition, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.Nutrition, (ThingDef)null)));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.Mass, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.Mass, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.Mass, (ThingDef)null)));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ToxicResistance, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.ToxicResistance, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.ToxicResistance, (ThingDef)null)));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.ToxicEnvironmentResistance, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.ToxicEnvironmentResistance, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.ToxicEnvironmentResistance, (ThingDef)null)));
		StatExtension.SetStatBaseValue((BuildableDef)(object)newThing, StatDefOf.MeleeDodgeChance, Mathf.Max(StatExtension.GetStatValueAbstract((BuildableDef)(object)secondaryThing, StatDefOf.MeleeDodgeChance, (ThingDef)null), StatExtension.GetStatValueAbstract((BuildableDef)(object)priorityThing, StatDefOf.MeleeDodgeChance, (ThingDef)null)));
	}

	public static void CopyRaceProperties(RaceProperties sRace, RaceProperties newRace)
	{
		foreach (FieldInfo item in from x in AccessTools.GetDeclaredFields(((object)sRace).GetType())
			where !x.IsStatic
			select x)
		{
			try
			{
				object value = item.GetValue(sRace);
				if (item.FieldType.IsGenericType && item.FieldType.GetGenericTypeDefinition() == typeof(Nullable<>))
				{
					item.SetValue(newRace, value);
				}
				else
				{
					item.SetValue(newRace, value);
				}
			}
			catch (Exception ex)
			{
				Log.Error("Failed to copy field " + item.Name + " from race.\n" + ex.Message + "\n" + ex.StackTrace);
			}
		}
	}

	public static void CopyThingDefFields(ThingDef sThing, ThingDef newThing)
	{
		foreach (FieldInfo item in from x in ((object)sThing).GetType().GetFields()
			where !x.IsLiteral && !x.IsStatic
			select x)
		{
			try
			{
				if (item.FieldType.IsClass && item.GetValue(sThing) != null && item.GetType().Name.Contains("ThingDef_AlienRace.AlienSettings"))
				{
					item.SetValue(newThing, item.GetType().GetConstructor(Array.Empty<Type>()).Invoke(Array.Empty<object>()));
					foreach (FieldInfo item2 in from x in item.GetType().GetFields()
						where !x.IsLiteral && !x.IsStatic
						select x)
					{
						try
						{
							item2.SetValue(item.GetValue(newThing), item2.GetValue(item.GetValue(sThing)));
						}
						catch (Exception ex)
						{
							Log.Error("Failed to access field " + item.Name + ".\n" + ex.Message + "\n" + ex.StackTrace);
						}
					}
				}
				else
				{
					object value = item.GetValue(sThing);
					if (item.FieldType.IsGenericType && item.FieldType.GetGenericTypeDefinition() == typeof(Nullable<>))
					{
						item.SetValue(newThing, value);
					}
					else
					{
						item.SetValue(newThing, value);
					}
				}
			}
			catch (Exception ex2)
			{
				Log.Error("Failed to copy field " + item.Name + " from thingDef.\n" + ex2.Message + "\n" + ex2.StackTrace);
			}
		}
	}

	public static void PostSaveLoadedSetup()
	{
		bool flag = false;
		foreach (ThingDef item in thingDefsAdded)
		{
			if (GenList.NullOrEmpty<BodyPartRecord>((IList<BodyPartRecord>)item.race.body.cachedAllParts))
			{
				item.race.body.CacheDataRecursive(item.race.body.corePart);
				flag = true;
			}
		}
		if (flag)
		{
			FacialAnim_PatchDynamicRaces.PatchFaceAdjustmentDict(thingDefsAdded.ToList());
		}
	}

	public static void GenerateCorpses(bool hotReload)
	{
		foreach (var (newThing, fusedBody) in FusedBody.FusedBodyByThing.Select((KeyValuePair<ThingDef, FusedBody> x) => (Key: x.Key, Value: x.Value)))
		{
			GenerateCorpse(fusedBody.SourceBody.thingDef, newThing, fusedBody.isMechanical, hotReload);
		}
	}

	private static void GenerateCorpse(ThingDef sThing, ThingDef newThing, bool isMechanical, bool hotReload)
	{
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Expected O, but got Unknown
		//IL_01da: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0200: Unknown result type (might be due to invalid IL or missing references)
		RaceProperties race = newThing.race;
		BodyDef body = newThing.race.body;
		RaceProperties race2 = sThing.race;
		ThingDef val = sThing.race.corpseDef;
		if (val == null)
		{
			val = sThing?.race?.linkedCorpseKind;
		}
		string defName = ((Def)body).defName + "_Corpse";
		ThingDef val2 = defName.TryGetExistingDef<ThingDef>();
		if (val2 == null)
		{
			val2 = new ThingDef();
		}
		bool hasCorpse = race2.hasCorpse;
		if (hasCorpse && val == null)
		{
			Log.Warning($"{sThing}.hasCorpse is True, but no ThingDef for corpse was found. Aborting corpse generation for fused race things.");
		}
		else
		{
			if (!hasCorpse)
			{
				return;
			}
			foreach (FieldInfo item in from x in ((object)val).GetType().GetFields()
				where !x.IsLiteral && !x.IsStatic
				select x)
			{
				try
				{
					if (item.FieldType.IsGenericType && item.GetValue(val) != null)
					{
						object value = item.GetValue(val);
						IList list = (IList)Activator.CreateInstance(item.FieldType);
						foreach (object item2 in (IEnumerable)value)
						{
							list.Add(item2);
						}
						item.SetValue(val2, list);
					}
					else
					{
						item.SetValue(val2, item.GetValue(val));
					}
				}
				catch (Exception ex)
				{
					Log.Error("Failed to copy field " + item.Name + " from race.\n" + ex.Message + "\n" + ex.StackTrace);
				}
			}
			((Def)val2).defName = defName;
			((Def)val2).label = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CorpseLabel", NamedArgument.op_Implicit(((Def)body).label)));
			((Def)val2).description = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CorpseDesc", NamedArgument.op_Implicit(((Def)newThing).label)));
			val2.race = race;
			val2.recipes = val.recipes.ToList();
			val2.inspectorTabs = val.inspectorTabs.ToList();
			newThing.race.corpseDef = val2;
			newThing.race.hasCorpse = true;
			DirectXmlCrossRefLoader.RegisterListWantsCrossRef<ThingCategoryDef>(val2.thingCategories, (!isMechanical) ? ((Def)ThingCategoryDefOf.CorpsesHumanlike).defName : ((Def)BSDefs.BS_RobotCorpses).defName, (object)val2, (string)null, (string)null);
			DefGenerator.AddImpliedDef<ThingDef>(val2, hotReload);
		}
	}

	private static void GenerateShortHashes(bool hotReload, ThingDef newThing, RaceProperties newRace)
	{
		if (!hotReload)
		{
			((Def)newThing).shortHash = 0;
			((Def)newRace.body).shortHash = 0;
		}
	}

	private static string OutputFullClassAsString(object obj)
	{
		if (obj == null)
		{
			return "null";
		}
		Type type = obj.GetType();
		FieldInfo[] fields = type.GetFields();
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendLine($"Class: {type?.Name} ({obj})");
		stringBuilder.AppendLine("{");
		FieldInfo[] array = fields;
		foreach (FieldInfo fieldInfo in array)
		{
			object value = fieldInfo.GetValue(obj);
			if (value != null)
			{
				stringBuilder.AppendLine($"  {fieldInfo?.Name}: {value}");
			}
		}
		stringBuilder.AppendLine("}");
		return stringBuilder.ToString();
	}

	private static Dictionary<BodyPartDef, List<BodyPartDef>> GetMechanicalVersionsOf()
	{
		if (_mechanicalVersionOf != null)
		{
			return _mechanicalVersionOf;
		}
		_mechanicalVersionOf = new Dictionary<BodyPartDef, List<BodyPartDef>>();
		List<(BodyPartDef, BodyPartExtension)> list = new List<(BodyPartDef, BodyPartExtension)>();
		foreach (BodyPartDef item in DefDatabase<BodyPartDef>.AllDefsListForReading)
		{
			foreach (BodyPartExtension item2 in item.ExtensionsOnDef<BodyPartExtension, BodyPartDef>((List<Type>)null, (List<Type>)null, doSort: true))
			{
				if (item2.mechanicalVersionOf != null && GenCollection.Any<BodyPartDef>(item2.mechanicalVersionOf))
				{
					list.Add((item, item2));
				}
			}
		}
		foreach (var item3 in list)
		{
			foreach (BodyPartDef item4 in item3.Item2.mechanicalVersionOf)
			{
				if (!_mechanicalVersionOf.ContainsKey(item4))
				{
					_mechanicalVersionOf[item4] = new List<BodyPartDef>();
				}
				_mechanicalVersionOf[item4].Add(item3.Item1);
			}
		}
		return _mechanicalVersionOf;
	}

	private static BodyPartRecord ClonePartsRecursive(BodyPartRecord genPartParent, BodyPartRecord source, BodyDef genBody, MergableBody bodyOne, List<BodyPartRecord> unTransfereredParts, bool makeMechanical)
	{
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0118: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Expected O, but got Unknown
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		if (bodyOne.ShouldRemovePart(source.def))
		{
			return null;
		}
		BodyPartDef val = source.def;
		string text = source.customLabel;
		if (makeMechanical)
		{
			Dictionary<BodyPartDef, List<BodyPartDef>> mechanicalVersionsOf = GetMechanicalVersionsOf();
			if (mechanicalVersionsOf != null && mechanicalVersionsOf.TryGetValue(source.def, out var value) && !GenList.NullOrEmpty<BodyPartDef>((IList<BodyPartDef>)value))
			{
				val = value.First();
				if (text != null)
				{
					TaggedString val2 = Translator.Translate("BS_Artificial");
					text = TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst() + " " + text.ToLower());
				}
				if (text == null)
				{
					text = (source.def.IsMirroredPart ? TaggedString.op_Implicit(source.flipGraphic ? Translator.Translate("BS_Left") : (Translator.Translate("BS_Right") + " " + ((Def)val).label)) : ((Def)val).label);
				}
			}
		}
		BodyPartRecord val3 = new BodyPartRecord
		{
			body = genBody,
			parent = genPartParent,
			def = val,
			customLabel = text,
			untranslatedCustomLabel = source.untranslatedCustomLabel,
			coverage = source.coverage,
			depth = source.depth,
			height = source.height,
			woundAnchorTag = source.woundAnchorTag,
			flipGraphic = source.flipGraphic,
			groups = ((source.groups == null) ? null : source.groups.ToList()),
			visibleHediffRots = ((source.visibleHediffRots == null) ? null : source.visibleHediffRots.ToList())
		};
		if (unTransfereredParts.Contains(source))
		{
			unTransfereredParts.Remove(source);
		}
		if (genPartParent == null)
		{
			genBody.corePart = val3;
		}
		else
		{
			genPartParent.parts.Add(val3);
		}
		foreach (BodyPartRecord part in source.parts)
		{
			ClonePartsRecursive(val3, part, genBody, bodyOne, unTransfereredParts, makeMechanical);
		}
		return val3;
	}

	private static float? Similarity(BodyPartRecord partOne, BodyPartRecord partTwo)
	{
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		float num = 0f;
		if (partOne.def == partTwo.def)
		{
			num += 1000000f;
		}
		else
		{
			float? num2 = BodyDefFusionsHelper.Equavalence(partOne.def, partTwo.def);
			if (!num2.HasValue)
			{
				return null;
			}
			float valueOrDefault = num2.GetValueOrDefault();
			num += 1000000f * valueOrDefault;
		}
		if (partOne.groups == partTwo.groups)
		{
			num += 10000f;
		}
		if (partOne.flipGraphic == partTwo.flipGraphic)
		{
			num += 1000f;
		}
		if (partOne.height == partTwo.height)
		{
			num += 100f;
		}
		if (partOne.customLabel == partTwo.customLabel)
		{
			num += 10f;
		}
		if (partOne.coverage == partTwo.coverage)
		{
			num += 1f;
		}
		string customLabel = partOne.customLabel;
		if (customLabel != null && customLabel.Split(' ', StringSplitOptions.None).Intersect(partTwo.customLabel?.Split(' ', StringSplitOptions.None)).Any())
		{
			num += 0.5f;
		}
		if (partOne.depth == partTwo.depth)
		{
			num += 0.1f;
		}
		if (partOne.woundAnchorTag == partTwo.woundAnchorTag)
		{
			num += 0.05f;
		}
		if (partOne.visibleHediffRots == partTwo.visibleHediffRots)
		{
			num += 0.01f;
		}
		return num;
	}

	private static void MergeRecursively(BodyPartRecord genPart, BodyPartRecord partTwo, List<BodyPartRecord> unTransfereredParts, MergableBody mergeOne)
	{
		List<BodyPartRecord> list = partTwo.parts.Where((BodyPartRecord x) => !mergeOne.ShouldRemovePart(x.def)).ToList();
		genPart.parts = genPart.parts.Where((BodyPartRecord x) => !mergeOne.ShouldRemovePart(x.def)).ToList();
		foreach (BodyPartRecord child in genPart.parts)
		{
			(BodyPartRecord, float?)? tuple = list.Where((BodyPartRecord x) => Similarity(x, child).HasValue)?.Select((BodyPartRecord x) => (x: x, Similarity(x, child)))?.OrderByDescending(((BodyPartRecord x, float?) x) => x.Item2).FirstOrDefault();
			if (tuple.HasValue && tuple.Value.Item1 != null)
			{
				BodyPartRecord item = tuple.Value.Item1;
				MergeRecursively(child, item, unTransfereredParts, mergeOne);
				unTransfereredParts.Remove(item);
				list.Remove(item);
			}
		}
		float num = (GenCollection.Any<BodyPartRecord>(genPart.parts) ? genPart.parts.Sum((BodyPartRecord x) => x.coverage) : 0f);
		float num2 = (GenCollection.Any<BodyPartRecord>(list) ? list.Sum((BodyPartRecord x) => x.coverage) : 0f);
		float num3 = 1f;
		if (num != 0f)
		{
			num3 = num / (num + num2);
			foreach (BodyPartRecord part in genPart.parts)
			{
				part.coverage *= num3;
			}
		}
		foreach (BodyPartRecord item2 in list)
		{
			if (unTransfereredParts.Contains(item2))
			{
				unTransfereredParts.Remove(item2);
				if (!BodyDefFusionsHelper.PartsToSkip.Contains(item2.def))
				{
					BodyPartRecord obj = ClonePartsRecursive(genPart, item2, genPart.body, mergeOne, unTransfereredParts, makeMechanical: false);
					obj.coverage *= num3;
					obj.parent = genPart;
				}
			}
		}
	}
}
