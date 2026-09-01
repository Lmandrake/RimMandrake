using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class GenderMethods
{
	public static HashSet<string> failedPaths = new HashSet<string>();

	public static HashSet<string> successPaths = new HashSet<string>();

	private static HashSet<BodyTypeDef> standardBodyTypes = null;

	private static HashSet<BodyTypeDef> vanillaBodyTypesPlus = null;

	public static HashSet<BodyTypeDef> StandardBodyTypes
	{
		get
		{
			object obj = standardBodyTypes;
			if (obj == null)
			{
				obj = new HashSet<BodyTypeDef>
				{
					BodyTypeDefOf.Male,
					BodyTypeDefOf.Female
				};
				standardBodyTypes = (HashSet<BodyTypeDef>)obj;
			}
			return (HashSet<BodyTypeDef>)obj;
		}
	}

	public static HashSet<BodyTypeDef> VanillaBodyTypesPlus
	{
		get
		{
			HashSet<BodyTypeDef> hashSet = vanillaBodyTypesPlus;
			if (hashSet == null)
			{
				HashSet<BodyTypeDef> hashSet2 = new HashSet<BodyTypeDef>();
				foreach (BodyTypeDef standardBodyType in StandardBodyTypes)
				{
					hashSet2.Add(standardBodyType);
				}
				hashSet2.Add(BodyTypeDefOf.Thin);
				hashSet2.Add(BodyTypeDefOf.Fat);
				hashSet2.Add(BodyTypeDefOf.Hulk);
				hashSet2.Add(BodyTypeDefOf.Baby);
				hashSet2.Add(BodyTypeDefOf.Child);
				hashSet = (vanillaBodyTypesPlus = hashSet2);
			}
			return hashSet;
		}
	}

	public static void TrySetGenderBody(PawnRenderNode_Body __instance, Pawn pawn, ref Graphic __result)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Invalid comparison between Unknown and I4
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		string bodyNakedGraphicPath = pawn.story.bodyType.bodyNakedGraphicPath;
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache == null || cache.bodyGraphicPath != null)
		{
			return;
		}
		bool flag = (int)cache.GetApparentGender() == 2;
		if (cache.overridenBodyDef != null)
		{
			pawn.story.bodyType = cache.overridenBodyDef;
		}
		else
		{
			if (HARCompat.IsHarRaceWithExtendedBodyGraphics(((Thing)(pawn?)).def) || !flag || bodyNakedGraphicPath == null || bodyNakedGraphicPath.Contains("_Female") || (!bodyNakedGraphicPath.Contains("_Thin") && !bodyNakedGraphicPath.Contains("_Fat") && !bodyNakedGraphicPath.Contains("_Hulk")))
			{
				return;
			}
			bodyNakedGraphicPath += "_Female";
			if (!failedPaths.Contains(bodyNakedGraphicPath))
			{
				if (successPaths.Contains(bodyNakedGraphicPath) || (Object)(object)ContentFinder<Texture2D>.Get(bodyNakedGraphicPath + "_south", false) != (Object)null)
				{
					Shader val = ((PawnRenderNode)__instance).ShaderFor(pawn);
					__result = GraphicDatabase.Get<Graphic_Multi>(bodyNakedGraphicPath, val, Vector2.one, ((PawnRenderNode)__instance).ColorFor(pawn));
					successPaths.Add(bodyNakedGraphicPath);
				}
				else
				{
					failedPaths.Add(bodyNakedGraphicPath);
				}
			}
		}
	}

	public static bool IsBodyStandard(this BodyTypeDef bodyType)
	{
		return StandardBodyTypes.Contains(bodyType);
	}

	public static bool TryBodyGenderBodyUpdate(BodyTypeDef bodyType, Gender apparentGender, BSCache cache, out BodyTypeDef newBody)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Invalid comparison between Unknown and I4
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Invalid comparison between Unknown and I4
		List<BodyTypeDef> list = HARCompat.TryGetHarBodiesForThingdef(((Thing)(cache?.pawn?)).def);
		newBody = null;
		if (TryGetBodyTypeOverride(cache, cache.pawn, apparentGender, out var bodyType2))
		{
			if (list != null && !list.Contains(newBody))
			{
				return false;
			}
			newBody = bodyType2;
			if (newBody == null)
			{
				return false;
			}
			return true;
		}
		if (cache.pawn.IsAdult() && bodyType.IsBodyStandard())
		{
			BodyTypeDef val = (((int)apparentGender == 1) ? BodyTypeDefOf.Male : (((int)apparentGender != 2) ? null : BodyTypeDefOf.Female));
			newBody = val;
			if (list != null && !list.Contains(newBody))
			{
				return false;
			}
			if (newBody == null)
			{
				return false;
			}
			return true;
		}
		return false;
	}

	public static void UpdateBodyHeadAndBeardPostGenderChange(Pawn pawn, bool banNarrow = false, bool force = false)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		if (pawn != null)
		{
			Pawn_StoryTracker story = pawn.story;
			if (story != null)
			{
				HeadTypeDef headType = story.headType;
				if (headType != null)
				{
					_ = headType.gender;
					if (0 == 0)
					{
						goto IL_00ea;
					}
				}
			}
		}
		Log.Warning($"Tried to update body, head and beard for {pawn} but pawn?.story?.headType?.gender was null.\n" + $"{pawn},{pawn?.story},{pawn?.story?.headType}, {pawn?.story?.headType?.gender}\n" + "Traceback " + Environment.StackTrace);
		if (pawn?.story == null)
		{
			Log.Warning("Also pawn?.story was null. This may mean it is broken. Aborting attempts to fix.");
			return;
		}
		goto IL_00ea;
		IL_00ea:
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			UpdateBodyHeadAndBeardPostGenderChange(cache, banNarrow, force);
		}
	}

	public static bool IsAdult(this Pawn pawn)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Invalid comparison between Unknown and I4
		if (pawn != null)
		{
			_ = pawn.DevelopmentalStage;
			if (0 == 0)
			{
				return (int)pawn.DevelopmentalStage > 4;
			}
		}
		return true;
	}

	public static void UpdateBodyHeadAndBeardPostGenderChange(BSCache cache, bool banNarrow = false, bool force = false)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0424: Unknown result type (might be due to invalid IL or missing references)
		//IL_0425: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b7: Invalid comparison between Unknown and I4
		//IL_02e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e5: Invalid comparison between Unknown and I4
		//IL_027d: Unknown result type (might be due to invalid IL or missing references)
		//IL_029f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0334: Unknown result type (might be due to invalid IL or missing references)
		//IL_036b: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = cache.pawn;
		Gender apparentGender = cache.GetApparentGender();
		if ((int)apparentGender == 0 || pawn?.story == null)
		{
			return;
		}
		Pawn_StoryTracker story = pawn.story;
		int num;
		if (story == null || story.headType?.gender != (Gender?)0)
		{
			Pawn_StoryTracker story2 = pawn.story;
			num = ((story2 == null || story2.headType?.gender != (Gender?)apparentGender) ? 1 : 0);
		}
		else
		{
			num = 0;
		}
		bool flag = (byte)num != 0;
		HashSet<Gene> allActiveGenes = pawn.GetAllActiveGenes();
		List<GeneDef> activeGeneDefs = allActiveGenes.Select((Gene x) => x.def).ToList();
		bool flag2 = pawn.story.bodyType == null || pawn.story.bodyType.IsBodyStandard() || cache.bodyTypeOverride != null || (Gender?)apparentGender != pawn?.gender || banNarrow || force;
		List<BodyTypeDef> list = HARCompat.TryGetHarBodiesForThingdef(((Thing)(cache?.pawn?)).def);
		if (cache.overridenBodyDef != null)
		{
			pawn.story.bodyType = cache.overridenBodyDef;
			flag2 = false;
		}
		if (cache.overridenHeadDef != null)
		{
			pawn.story.headType = cache.overridenHeadDef;
			flag = false;
		}
		if (flag2)
		{
			bool flag3 = pawn.IsAdult();
			BodyTypeDef val = pawn.story?.bodyType;
			if (TryGetBodyTypeOverride(cache, pawn, apparentGender, out var bodyType) && (list == null || list.Contains(bodyType)))
			{
				pawn.story.bodyType = bodyType;
				goto IL_0391;
			}
			if (val == null || VanillaBodyTypesPlus.Contains(val))
			{
				if (allActiveGenes.Any((Gene x) => x.def.bodyType.HasValue))
				{
					GeneticBodyType? bodyType2 = allActiveGenes.First((Gene x) => x.def.bodyType.HasValue).def.bodyType;
					if (bodyType2.HasValue && flag3)
					{
						pawn.story.bodyType = GeneUtility.ToBodyType(bodyType2.Value, pawn);
					}
					else if (!bodyType2.HasValue)
					{
						TrySetMissingBodytype(pawn, apparentGender, list);
					}
				}
				else if (val.IsBodyStandard())
				{
					if ((int)apparentGender == 2 && (list == null || list.Contains(BodyTypeDefOf.Female)))
					{
						pawn.story.bodyType = BodyTypeDefOf.Female;
					}
					else if ((int)apparentGender == 1 && (list == null || list.Contains(BodyTypeDefOf.Female)))
					{
						pawn.story.bodyType = BodyTypeDefOf.Male;
					}
				}
				else if (val == null)
				{
					Pawn_StoryTracker story3 = pawn.story;
					if (((story3 != null) ? story3.Adulthood : null) != null)
					{
						BodyTypeDef val2 = pawn.story.Adulthood.BodyTypeFor(apparentGender);
						if (list == null || list.Contains(val2))
						{
							pawn.story.bodyType = val2;
						}
					}
					else if (pawn.story.bodyType == null)
					{
						TrySetMissingBodytype(pawn, apparentGender, list);
					}
				}
			}
		}
		Pawn_StoryTracker story4 = pawn.story;
		if (story4.bodyType == null)
		{
			story4.bodyType = PawnGenerator.GetBodyTypeFor(pawn);
		}
		goto IL_0391;
		IL_0391:
		if (flag)
		{
			IEnumerable<Gene> headGenes = allActiveGenes.Where((Gene x) => !GenList.NullOrEmpty<HeadTypeDef>((IList<HeadTypeDef>)x.def.forcedHeadTypes));
			List<HeadTypeDef> list2 = headGenes.SelectMany((Gene x) => x.def.forcedHeadTypes).ToList();
			if (list2.Count > 0)
			{
				Gender targetGender = apparentGender;
				List<HeadTypeDef> list3 = (from x in list2
					where headGenes.All((Gene ag) => ag.def.forcedHeadTypes.Contains(x))
					where x.gender == targetGender && (GenList.NullOrEmpty<GeneDef>((IList<GeneDef>)x.requiredGenes) || x.requiredGenes.All((GeneDef x) => activeGeneDefs.Contains(x)))
					select x).ToList();
				if (list3.Count == 0)
				{
					list3 = (from x in list2
						where headGenes.All((Gene ag) => ag.def.forcedHeadTypes.Contains(x))
						where x.gender == targetGender
						select x).ToList();
					if (list3.Count == 0)
					{
						list3 = (from x in list2
							where headGenes.All((Gene ag) => ag.def.forcedHeadTypes.Contains(x))
							where (int)x.gender == 0 || x.gender == targetGender
							select x).ToList();
					}
				}
				if (list3.Count == 0)
				{
					list3 = list2.Where((HeadTypeDef x) => headGenes.All((Gene ag) => ag.def.forcedHeadTypes.Contains(x))).ToList();
					if (GenCollection.Any<HeadTypeDef>(list3))
					{
						Log.WarningOnce($"Couldn't find an appropriate head fitting {pawn}'s genes. One was picked which ignored gender-limits." + "\nThis is usually caused by a pawn of a gender the race-modder did not support.", ((Thing)pawn).thingIDNumber ^ 0x3F2A1A);
					}
				}
				if (banNarrow)
				{
					List<HeadTypeDef> list4 = list3.Where((HeadTypeDef x) => !x.narrow).ToList();
					if (list4.Count > 0)
					{
						list3 = list4;
					}
				}
				if (list3.Count > 0)
				{
					Rand.PushState(((Thing)pawn).thingIDNumber);
					pawn.story.headType = GenCollection.RandomElement<HeadTypeDef>((IEnumerable<HeadTypeDef>)list3);
					Rand.PopState();
					flag = false;
				}
			}
		}
		if (flag && !pawn.story.TryGetRandomHeadFromSet(DefDatabase<HeadTypeDef>.AllDefs.Where((HeadTypeDef x) => x.randomChosen)) && !pawn.story.TryGetRandomHeadFromSet(DefDatabase<HeadTypeDef>.AllDefs.Where((HeadTypeDef x) => x.randomChosen)))
		{
			Log.Warning($"Couldn't find an appropriate head for {pawn}.");
		}
		if (!pawn.style.CanWantBeard && pawn.style.beardDef != BeardDefOf.NoBeard)
		{
			pawn.style.beardDef = BeardDefOf.NoBeard;
		}
	}

	private static void TrySetMissingBodytype(Pawn pawn, Gender gender, List<BodyTypeDef> harWhitelist)
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Invalid comparison between Unknown and I4
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null && cache.overridenBodyDef != null)
		{
			pawn.story.bodyType = cache.overridenBodyDef;
		}
		else
		{
			if (pawn?.story == null)
			{
				return;
			}
			if (pawn.story.Adulthood != null)
			{
				BodyTypeDef val = pawn.story.Adulthood.BodyTypeFor(gender);
				if (val != null && (harWhitelist == null || harWhitelist.Contains(val)))
				{
					pawn.story.bodyType = pawn.story.Adulthood.BodyTypeFor(gender);
				}
				else
				{
					BodyTypeDef val2 = pawn.story.Adulthood.BodyTypeFor(pawn.gender);
					if (val2 != null && (harWhitelist == null || harWhitelist.Contains(val2)))
					{
						Pawn_StoryTracker story = pawn.story;
						if (story.bodyType == null)
						{
							story.bodyType = pawn.story.Adulthood.BodyTypeFor(pawn.gender);
						}
					}
				}
			}
			if (pawn.story.bodyType == null && ModsConfig.BiotechActive && DevelopmentalStageExtensions.Juvenile(pawn.DevelopmentalStage))
			{
				if ((int)pawn.DevelopmentalStage == 2 && (harWhitelist == null || harWhitelist.Contains(BodyTypeDefOf.Baby)))
				{
					pawn.story.bodyType = BodyTypeDefOf.Baby;
				}
				else if (harWhitelist == null || harWhitelist.Contains(BodyTypeDefOf.Child))
				{
					pawn.story.bodyType = BodyTypeDefOf.Child;
				}
			}
			if (pawn.story.bodyType == null && harWhitelist != null && harWhitelist.Count == 0)
			{
				PawnGenerator.GetBodyTypeFor(pawn);
			}
		}
	}

	private static bool TryGetBodyTypeOverride(BSCache cache, Pawn pawn, Gender apparentGender, out BodyTypeDef bodyType)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		bodyType = null;
		if (cache.overridenBodyDef != null)
		{
			bodyType = cache.overridenBodyDef;
		}
		if (cache.bodyTypeOverride != null)
		{
			List<GenderBodyType> list = cache.bodyTypeOverride.BodytypesForGender(pawn, apparentGender);
			if (GenCollection.Any<GenderBodyType>(list))
			{
				RandBlock val = default(RandBlock);
				((RandBlock)(ref val))._002Ector(pawn.GetPawnRNGSeed());
				try
				{
					bodyType = GenCollection.RandomElement<GenderBodyType>((IEnumerable<GenderBodyType>)list).bodyType;
					return true;
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
		}
		return false;
	}

	/// <summary>
	/// This is some old questionable method to clean up broken pawns.
	///
	/// Probably best to leave it alone for now... It doesn't seem to break anything and might still fix something important.
	/// </summary>
	public static void UpdatePawnHairAndHeads(Pawn pawn)
	{
		try
		{
			BSCache cachePrepatched = pawn.GetCachePrepatched();
			if (cachePrepatched != null)
			{
				bool flag = false;
				bool flag2 = false;
				if (cachePrepatched.overridenHeadDef != null)
				{
					pawn.story.headType = cachePrepatched.overridenHeadDef;
					flag2 = true;
				}
				if (cachePrepatched.overridenHairDef != null)
				{
					pawn.story.hairDef = cachePrepatched.overridenHairDef;
					flag = true;
				}
				if (cachePrepatched.overridenBodyDef != null)
				{
					pawn.story.bodyType = cachePrepatched.overridenBodyDef;
				}
				if (flag && flag2)
				{
					return;
				}
			}
			HashSet<Gene> genes = pawn.GetAllActiveGenes();
			if (genes.Count == 0)
			{
				return;
			}
			List<string> hairStyleWhitelist = (from x in genes
				where x.def.hairTagFilter != null && x.def.hairTagFilter.whitelist
				select x.def.hairTagFilter.tags).SelectMany((List<string> x) => x).ToList();
			if (hairStyleWhitelist.Count <= 0)
			{
				return;
			}
			Pawn obj = pawn;
			if (obj == null)
			{
				return;
			}
			Pawn_StoryTracker story = obj.story;
			bool? obj2;
			if (story == null)
			{
				obj2 = null;
			}
			else
			{
				HairDef hairDef = story.hairDef;
				obj2 = ((hairDef != null) ? new bool?(GenCollection.Any<string>(((StyleItemDef)hairDef).styleTags, (Predicate<string>)((string x) => hairStyleWhitelist.Contains(x)))) : ((bool?)null));
			}
			if (obj2 != false)
			{
				return;
			}
			List<HairDef> source = DefDatabase<HairDef>.AllDefs.Where((HairDef x) => GenCollection.Any<string>(((StyleItemDef)x).styleTags, (Predicate<string>)((string st) => hairStyleWhitelist.Contains(st)))).ToList();
			source = source.Where((HairDef x) => ((StyleItemDef)x).requiredGene == null || genes.Any((Gene g) => g.def == ((StyleItemDef)x).requiredGene)).ToList();
			source = source.Where(delegate(HairDef x)
			{
				if (((StyleItemDef)x).requiredMutant != null)
				{
					Pawn obj3 = pawn;
					object obj4;
					if (obj3 == null)
					{
						obj4 = null;
					}
					else
					{
						Pawn_MutantTracker mutant = obj3.mutant;
						obj4 = ((mutant != null) ? mutant.Def : null);
					}
					return obj4 == ((StyleItemDef)x).requiredMutant;
				}
				return true;
			}).ToList();
			if (source.Count > 0)
			{
				HairDef hairDef2 = GenCollection.RandomElement<HairDef>((IEnumerable<HairDef>)source);
				pawn.story.hairDef = hairDef2;
			}
		}
		catch (Exception ex)
		{
			Log.Warning($"Warning: Failed to update hair for {pawn}.\n{ex.Message}\n{ex.StackTrace}");
		}
	}
}
