using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class BSCache : IExposable, ICacheable
{
	public enum BleedRateState
	{
		Unchanged,
		SlowBleeding,
		VerySlowBleeding,
		NoBleeding
	}

	/// <summary>
	/// Used to get more realistic results from size changes.
	/// F.ex. most things scale quadratically, but weight/health scales by cube.
	///
	/// Technically a Rimworld Scale isn't really linear, but this type of change gives fairly good values when going upwards.
	/// Downwards is another story though, and we don't want small pawns to get utterly obliterated if something looks at the wrong.
	/// </summary>
	public enum SizeChangeType
	{
		Linear = 1,
		Quadratic,
		Cubic
	}

	public class PercentChange : IExposable
	{
		public float linear = 1f;

		public float quadratic = 1f;

		public float cubic = 1f;

		public float KelibersLaw => Mathf.Pow(cubic, 0.75f);

		public float DoubleMaxLinear
		{
			get
			{
				if (!(linear < 1f))
				{
					return 1f + (linear - 1f) * 2f;
				}
				return linear;
			}
		}

		public float TripleMaxLinear
		{
			get
			{
				if (!(linear < 1f))
				{
					return 1f + (linear - 1f) * 3f;
				}
				return linear;
			}
		}

		public PercentChange()
		{
		}

		public PercentChange(float linear, float quadratic, float cubic)
		{
			this.linear = linear;
			this.quadratic = quadratic;
			this.cubic = cubic;
		}

		public void ExposeData()
		{
			Scribe_Values.Look<float>(ref linear, "linear", 1f, false);
			Scribe_Values.Look<float>(ref quadratic, "quadratic", 1f, false);
			Scribe_Values.Look<float>(ref cubic, "cubic", 1f, false);
		}
	}

	private readonly List<Gene> genesActivated = new List<Gene>();

	private readonly List<Gene> genesDeactivated = new List<Gene>();

	public static BSCache defaultCache = new BSCache
	{
		isDefaultCache = true
	};

	public bool isDefaultCache;

	[DefaultValue(false)]
	public bool isJunkCache = true;

	public Pawn pawn;

	public uint changeIndex;

	public bool refreshQueued;

	public int? lastUpdateTick;

	public int? creationTick;

	public bool isHumanlike;

	public ThingDef originalThing;

	public HashSet<HediffDef> raceTrackerHistory = new HashSet<HediffDef>();

	public bool approximatelyNoChange = true;

	public bool hideHead;

	public bool hideBody;

	public bool hideHumanlikeRenderNodes;

	public BodyTypesPerGender bodyTypeOverride;

	private Gender? apparentGender;

	public string bodyGraphicPath;

	public string bodyDessicatedGraphicPath;

	public string headGraphicPath;

	public string headDessicatedGraphicPath;

	public CustomMaterial bodyMaterial;

	public CustomMaterial headMaterial;

	public RotDrawMode? forcedRotDrawMode;

	public float bodyRenderSize = 1f;

	public float headRenderSize = 1f;

	public float totalSize = 1f;

	public float totalCosmeticSize = 1f;

	public float totalSizeOffset;

	public PercentChange scaleMultiplier = new PercentChange(1f, 1f, 1f);

	public PercentChange previousScaleMultiplier;

	public PercentChange cosmeticScaleMultiplier = new PercentChange(1f, 1f, 1f);

	public float healthMultiplier = 1f;

	public float healthMultiplier_previous = 1f;

	public float internalDamageDivisor = 1f;

	public Dictionary<ThingDef, bool> willEatDef = new Dictionary<ThingDef, bool>();

	public float minimumLearning;

	public float growthPointGain = 1f;

	public bool preventHeadScaling;

	public bool bodyConstantHeadScale;

	public bool bodyConstantHeadScaleBigOnly;

	public float preventHeadScalingFactor = 1f;

	public float preventHeadOffsetFactor = 1f;

	public float headSizeMultiplier = 1f;

	public float headPositionMultiplier = 1f;

	public float worldspaceOffset;

	/// <summary>
	/// If populated should always have 4 items, one for each rotation.
	/// </summary>
	public List<Vector3> complexHeadOffsets;

	public List<Vector3> complexBodyOffsets;

	public bool hasComplexHeadOffsets;

	/// <summary>
	/// This one returns true on stuff like bloodless pawns just so they can't have blood drained from them.
	/// </summary>
	public bool isBloodFeeder;

	public bool hasSizeAffliction;

	public float attackSpeedMultiplier = 1f;

	public float attackSpeedUnarmedMultiplier = 1f;

	public float alcoholAmount;

	public RomanceTags romanceTags;

	public ApparelRestrictions apparelRestrictions;

	public bool canWield = true;

	public float? fineManipulation;

	public bool injuriesRescaled;

	public bool isUnliving;

	public BleedRateState bleedRate;

	public float bleedRateFactor = 1f;

	public bool slowBleeding;

	public bool deathlike;

	public bool isMechanical;

	public bool empVulnerable;

	public HashSet<RacialFeature> racialFeatures = new HashSet<RacialFeature>();

	public HashSet<RacialFeatureDef> racialFeaturesAuto = new HashSet<RacialFeatureDef>();

	/// <summary>
	/// Bans addictions that are not whitelisted or better.
	/// </summary>
	public bool banAddictions;

	public bool partsCanBeHarvested = true;

	public bool willBeUndead;

	public bool unarmedOnly;

	public bool succubusUnbonded;

	public float pregnancySpeed = 1f;

	public bool everFertile;

	public bool animalFriend;

	public float apparentAge = 30f;

	public DevelopmentalStage developmentalStage;

	public float raidWealthOffset;

	public float raidWealthMultiplier = 1f;

	public float bodyPosOffset;

	public bool preventDisfigurement;

	public bool renderCacheOff;

	public List<NewFoodCategory> newFoodCatAllow;

	public List<NewFoodCategory> newFoodCatDeny;

	public List<PawnDiet> pawnDiet = new List<PawnDiet>();

	public bool canUseChargers;

	public bool poorUserOfChargers;

	public List<ApparelCache> apparelCaches = new List<ApparelCache>();

	public Color? savedSkinColor;

	public Color? savedHairColor;

	public string savedFurSkin;

	public string savedBodyDef;

	public string savedHeadDef;

	public string savedBeardDef;

	public string savedHairDef;

	public Color? overridenSkinColor;

	public Color? overridenHairColor;

	public FurDef overridenFurSkin;

	public BodyTypeDef overridenBodyDef;

	public HeadTypeDef overridenHeadDef;

	public BeardDef overridenBeardDef;

	public HairDef overridenHairDef;

	public int? randomPickSkinColor;

	public int? randomPickHairColor;

	public bool facialAnimationDisabled;

	public bool facialAnimationDisabled_Transform;

	public FacialAnimDisabler facialAnimDisabler;

	public bool disableLookChangeDesired;

	public bool isDrone;

	public bool noFamilyRelations;

	public bool isAmorphous;

	public List<Aptitude> aptitudes = new List<Aptitude>();

	public List<WorkTypeDef> disabledWorkTypes = new List<WorkTypeDef>();

	public List<WorkTypeDef> explicitlyDisabled = new List<WorkTypeDef>();

	public List<SkillDef> skillsDisabledByExtensions = new List<SkillDef>();

	public List<GeneDef> endogenesRemovedByRace = new List<GeneDef>();

	public List<GeneDef> xenoenesRemovedByRace = new List<GeneDef>();

	public List<HediffToBody> hediffsToBody = new List<HediffToBody>();

	public List<HediffToBodyparts> hediffsToParts = new List<HediffToBodyparts>();

	public string id = "BS_DefaultID";

	public static bool regenerationInProgress = false;

	[Unsaved(false)]
	public HashSet<Gene> recordedActiveGenes = new HashSet<Gene>();

	private static readonly float hulkSize = 0.88f;

	private static readonly float fatSize = 0.93f;

	private static readonly float thinSize = 1f;

	public bool IsTempCache
	{
		get
		{
			if (!isDefaultCache)
			{
				return isJunkCache;
			}
			return true;
		}
	}

	public bool SameTick => lastUpdateTick == Find.TickManager.TicksGame;

	private string GeneShouldBeActive(Gene gene, List<PawnExtension> genePawnExts, List<PawnExtension> hediffPawnExts, List<PawnExtension> allPawnExts)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val;
		if (genePawnExts.Count != 0 && !ConditionalManager.TestConditionals(gene, genePawnExts))
		{
			val = Translator.Translate("BS_ConditionForActivationNotMet");
			return TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
		}
		if (hediffPawnExts.Count != 0)
		{
			for (int num = hediffPawnExts.Count - 1; num >= 0; num--)
			{
				if (hediffPawnExts[num].IsGeneLegal(gene.def, removalCheck: false).Denied())
				{
					val = Translator.Translate("BS_DisabledByHediff");
					return TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
				}
			}
		}
		string text = PrerequisiteValidator.Validate(gene.def, pawn);
		if (text != null && text != "")
		{
			return text;
		}
		if (allPawnExts.Count != 0)
		{
			for (int num2 = allPawnExts.Count - 1; num2 >= 0; num2--)
			{
				if (allPawnExts[num2].IsGeneLegal(gene.def, removalCheck: false).Denied())
				{
					val = Translator.Translate("BS_DisabledByFilter");
					return TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
				}
			}
		}
		return "";
	}

	private bool UpdateGeneOverrideStates(List<PawnExtension> allPawnExts)
	{
		if (pawn.genes == null)
		{
			return false;
		}
		List<Gene> genesListForReading = pawn.genes.GenesListForReading;
		if (GenList.NullOrEmpty<Gene>((IList<Gene>)genesListForReading) || allPawnExts.Count == 0)
		{
			return false;
		}
		bool flag = false;
		IOrderedEnumerable<(Gene gene, List<PawnExtension> extensions)> orderedEnumerable = from gene in genesListForReading
			select (gene: gene, extensions: gene.def.GetAllPawnExtensionsOnGene()) into gene
			orderby (gene.extensions.Count <= 0) ? (-1f) : gene.extensions.Max((PawnExtension x) => (float)x.priority + (x.HasGeneFilters ? 0.5f : 0f)) descending
			select gene;
		List<PawnExtension> hediffExtensions = pawn.GetHediffExtensions<PawnExtension>();
		foreach (var item in orderedEnumerable)
		{
			var (val, _) = item;
			if (!GeneCache.globalCache.TryGetValue(val, out var value))
			{
				value = (GeneCache.globalCache[val] = new GeneCache(val));
			}
			bool flag2 = val.overriddenByGene == GeneCache.DummyGene;
			if (!(!val.Overridden || flag2))
			{
				continue;
			}
			string text = GeneShouldBeActive(val, item.extensions, hediffExtensions, allPawnExts);
			bool active = val.Active;
			if (text != "")
			{
				if (!value.isOverriden)
				{
					genesDeactivated.Add(val);
				}
				value.isOverriden = true;
				if (active)
				{
					val.OverrideBy(GeneCache.DummyGene);
					flag = true;
				}
			}
			else if (value.isOverriden || flag2)
			{
				if (value.isOverriden)
				{
					value.isOverriden = false;
					genesActivated.Add(val);
				}
				if (!active)
				{
					val.OverrideBy((Gene)null);
					flag |= val.Active;
				}
			}
		}
		return flag;
	}

	/// <summary>
	/// For use by the Prepatcher.
	/// </summary>
	public static BSCache GetDefaultCache()
	{
		return defaultCache;
	}

	public Gender GetApparentGender()
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		return (Gender)(((_003F?)apparentGender) ?? pawn.gender);
	}

	public void ExposeData()
	{
		Scribe_Values.Look<bool>(ref isJunkCache, "BS_IsJunkCache", false, false);
		Scribe_Values.Look<string>(ref id, "BS_CachePawnID", "BS_DefaultCahced", false);
		Scribe_Defs.Look<ThingDef>(ref originalThing, "BS_OriginalThing");
		Scribe_Values.Look<float>(ref healthMultiplier, "BS_HealthMultiplier", 1f, false);
		Scribe_Values.Look<float>(ref healthMultiplier_previous, "BS_HealthMultiplier_Previous", 1f, false);
		Scribe_Values.Look<float>(ref bodyRenderSize, "BS_BodyRenderSize", 1f, false);
		Scribe_Values.Look<float>(ref headRenderSize, "BS_HeadRenderSize", 1f, false);
		Scribe_Values.Look<float>(ref totalSize, "BS_TotalSize", 1f, false);
		Scribe_Values.Look<float>(ref totalCosmeticSize, "BS_TotalCosmeticSize", 1f, false);
		Scribe_Deep.Look<PercentChange>(ref scaleMultiplier, "BS_ScaleMultiplier", Array.Empty<object>());
		Scribe_Deep.Look<PercentChange>(ref previousScaleMultiplier, "BS_PreviousScaleMultiplier", Array.Empty<object>());
		Scribe_Deep.Look<PercentChange>(ref cosmeticScaleMultiplier, "BS_CosmeticScaleMultiplier", Array.Empty<object>());
		Scribe_Values.Look<float>(ref totalSizeOffset, "BS_SizeOffset", 0f, false);
		Scribe_Values.Look<bool>(ref isHumanlike, "BS_IsHumanlike", false, false);
		Scribe_Values.Look<float>(ref headPositionMultiplier, "BS_HeadPositionMultiplier", 1f, false);
		Scribe_Values.Look<bool>(ref hideHead, "BS_HideHead", false, false);
		Scribe_Values.Look<bool>(ref hideBody, "BS_HideBody", false, false);
		Scribe_Values.Look<bool>(ref hideHumanlikeRenderNodes, "BS_HideHumanlikeRenderNodes", false, false);
		Scribe_Values.Look<float>(ref minimumLearning, "BS_MinimumLearning", 0.35f, false);
		Scribe_Values.Look<float>(ref headSizeMultiplier, "BS_HeadSizeMultiplier", 1f, false);
		Scribe_Values.Look<bool>(ref isBloodFeeder, "BS_IsBloodFeeder", false, false);
		Scribe_Values.Look<bool>(ref hasSizeAffliction, "BS_HasSizeAffliction", false, false);
		Scribe_Values.Look<float>(ref attackSpeedMultiplier, "BS_AttackSpeedMultiplier", 1f, false);
		Scribe_Values.Look<float>(ref alcoholAmount, "BS_AlcoholAmount", 0f, false);
		Scribe_Values.Look<bool>(ref isUnliving, "BS_IsUnliving", false, false);
		Scribe_Values.Look<BleedRateState>(ref bleedRate, "BS_BleedRate", BleedRateState.Unchanged, false);
		Scribe_Values.Look<bool>(ref slowBleeding, "BS_SlowBleeding", false, false);
		Scribe_Values.Look<bool>(ref deathlike, "BS_Deathlike", false, false);
		Scribe_Values.Look<bool>(ref isMechanical, "BS_IsMechanical", false, false);
		Scribe_Values.Look<bool>(ref willBeUndead, "BS_WillBeUndead", false, false);
		Scribe_Values.Look<bool>(ref unarmedOnly, "BS_UnarmedOnly", false, false);
		Scribe_Values.Look<bool>(ref succubusUnbonded, "BS_SuccubusUnbonded", false, false);
		Scribe_Values.Look<float>(ref pregnancySpeed, "BS_FastPregnancy", 1f, false);
		Scribe_Values.Look<bool>(ref everFertile, "BS_EverFertile", false, false);
		Scribe_Values.Look<float>(ref apparentAge, "BS_ApparentAge", 30f, false);
		Scribe_Values.Look<bool>(ref injuriesRescaled, "BS_InjuriesRescaled", false, false);
		Scribe_Collections.Look<ApparelCache>(ref apparelCaches, "BS_ApparelCaches", (LookMode)2, Array.Empty<object>());
		Scribe_Values.Look<bool>(ref preventDisfigurement, "BS_PreventDisfigurement", false, false);
		Scribe_Values.Look<bool>(ref renderCacheOff, "BS_RenderCacheOff", false, false);
		Scribe_Values.Look<string>(ref savedBodyDef, "BS_SavedBodyDefName", (string)null, false);
		Scribe_Values.Look<string>(ref savedHeadDef, "BS_SavedHeadDefName", (string)null, false);
		Scribe_Values.Look<Color?>(ref savedSkinColor, "BS_SavedSkinColor", (Color?)null, false);
		Scribe_Values.Look<Color?>(ref savedHairColor, "BS_SavedHairColor", (Color?)null, false);
		Scribe_Values.Look<string>(ref savedBeardDef, "BS_SavedBeardDef", (string)null, false);
		Scribe_Values.Look<string>(ref savedFurSkin, "BS_SavedFurskinName", (string)null, false);
		Scribe_Defs.Look<FurDef>(ref overridenFurSkin, "BS_OverridenFurSkin");
		Scribe_Defs.Look<BodyTypeDef>(ref overridenBodyDef, "BS_OverridenBodyDef");
		Scribe_Defs.Look<HeadTypeDef>(ref overridenHeadDef, "BS_OverridenHeadDef");
		Scribe_Defs.Look<BeardDef>(ref overridenBeardDef, "BS_OverridenBeardDef");
		Scribe_Defs.Look<HairDef>(ref overridenHairDef, "BS_OverridenHairDef");
		Scribe_Values.Look<Color?>(ref overridenSkinColor, "BS_OverridenSkinColor", (Color?)null, false);
		Scribe_Values.Look<Color?>(ref overridenHairColor, "BS_OverridenHairColor", (Color?)null, false);
		Scribe_Values.Look<int?>(ref randomPickSkinColor, "BS_RandomPickSkinColor", (int?)null, false);
		Scribe_Values.Look<int?>(ref randomPickHairColor, "BS_RandomPickHairColor", (int?)null, false);
		Scribe_Values.Look<bool>(ref facialAnimationDisabled, "BS_FacialAnimationDisabled", false, false);
		Scribe_Collections.Look<GeneDef>(ref endogenesRemovedByRace, "BS_EndogenesRemovedByRace", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<GeneDef>(ref xenoenesRemovedByRace, "BS_XenoenesRemovedByRace", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<NewFoodCategory>(ref newFoodCatAllow, "BS_NewFoodCatAllow", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<NewFoodCategory>(ref newFoodCatDeny, "BS_NewFoodCatDeny", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<PawnDiet>(ref pawnDiet, "BS_PawnDiet", (LookMode)4, Array.Empty<object>());
		Scribe_Values.Look<bool>(ref animalFriend, "BS_AnimalFriend", false, false);
		Scribe_Values.Look<float>(ref raidWealthOffset, "BS_RaidWealthOffset", 0f, false);
		Scribe_Values.Look<float>(ref raidWealthMultiplier, "BS_RaidWealthMultiplier", 1f, false);
		Scribe_Values.Look<bool>(ref isDrone, "BS_IsDrone", false, false);
	}

	public static bool Compare(BSCache a, BSCache b)
	{
		return a.id == b.id;
	}

	public BSCache()
	{
	}

	public BSCache(Pawn pawn)
	{
		this.pawn = pawn;
		id = ((Thing)pawn).ThingID;
	}

	public bool RefreshOwnerId(Pawn pawn)
	{
		if (pawn == null)
		{
			return false;
		}
		if (pawn != this.pawn)
		{
			Log.ErrorOnce($"Tried to refresh BSCache owner ID, but the pawn provided ({pawn})" + $"does not match the cache's pawn ({this.pawn}).", 94561234);
		}
		if (id != ((Thing)pawn).ThingID)
		{
			id = ((Thing)pawn).ThingID;
			return true;
		}
		return false;
	}

	public bool RegenerateCache()
	{
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_033a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ddf: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			throw new Exception("Big & Small: Cannot regenerate Pawn Cache because the Pawn is null.");
		}
		if (regenerationInProgress)
		{
			HumanoidPawnScaler.GetCache(pawn, forceRefresh: false, canRegenerate: false, 10);
			return false;
		}
		regenerationInProgress = true;
		try
		{
			_ = BS.Tick;
			int valueOrDefault = creationTick.GetValueOrDefault();
			if (!creationTick.HasValue)
			{
				valueOrDefault = BS.Tick;
				creationTick = valueOrDefault;
			}
			DevelopmentalStage dStage;
			try
			{
				dStage = (developmentalStage = pawn.DevelopmentalStage);
			}
			catch (Exception ex)
			{
				Log.Warning($"[BigAndSmall] caught an exception when fetching Developmental Stage for {pawn.Name} Aborting generation of pawn cache.\n" + "This likely means the pawn lacks \"lifeStageAges\" or another requirement for fetching the age is missing.\n" + ex.Message + "\n" + ex.StackTrace);
				return false;
			}
			isJunkCache = false;
			RaceProperties raceProps = pawn.RaceProps;
			isHumanlike = raceProps != null && raceProps.Humanlike;
			if (originalThing == null)
			{
				originalThing = ((Thing)pawn).def;
			}
			if (changeIndex < uint.MaxValue)
			{
				changeIndex++;
			}
			else
			{
				changeIndex = 1u;
			}
			List<RaceTracker> raceTrackers = pawn.GetRaceTrackers();
			GenCollection.AddRange<HediffDef>(raceTrackerHistory, raceTrackers.Select((RaceTracker x) => ((Hediff)x).def));
			HashSet<Gene> allActiveGenes = pawn.GetAllActiveGenes();
			List<PawnExtension> allPawnExtensions = pawn.GetAllPawnExtensions();
			List<PawnExtension> racePawnExtensions = pawn.GetRacePawnExtensions();
			List<PawnExtension> allPawnExtensions2 = pawn.GetAllPawnExtensions(null, new List<Type>(1) { typeof(RaceTracker) });
			preventHeadScaling = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.preventHeadScaling));
			bodyConstantHeadScale = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.bodyConstantHeadScale));
			bodyConstantHeadScaleBigOnly = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.bodyConstantHeadScaleBigOnly));
			preventHeadScalingFactor = allPawnExtensions.Where((PawnExtension x) => x.preventHeadScalingFactor.HasValue).DefaultIfEmpty(new PawnExtension
			{
				preventHeadScalingFactor = 1f
			}).Average((PawnExtension x) => x.preventHeadScalingFactor.Value);
			preventHeadOffsetFactor = allPawnExtensions.Where((PawnExtension x) => x.preventHeadOffsetFactor.HasValue).DefaultIfEmpty(new PawnExtension
			{
				preventHeadOffsetFactor = preventHeadScalingFactor
			}).Average((PawnExtension x) => x.preventHeadOffsetFactor.Value);
			CalculateGenderAndApparentGender(allPawnExtensions);
			bool overrideLimits = ScalingMethods.CheckForSizeAffliction(pawn);
			CalculateSize(dStage, allPawnExtensions, overrideLimits);
			if (isHumanlike)
			{
				willEatDef.Clear();
				pawnDiet = (from x in allPawnExtensions2
					where x.pawnDiet != null
					select x.pawnDiet).ToList();
				if (GenCollection.Any<PawnExtension>(racePawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.pawnDiet != null)) && !GenCollection.Any<PawnExtension>(allPawnExtensions2, (Predicate<PawnExtension>)((PawnExtension x) => x.pawnDietRacialOverride)))
				{
					pawnDiet.AddRange(from x in racePawnExtensions
						where x.pawnDiet != null
						select x.pawnDiet);
				}
				List<GeneDef> activeGenedefs = allActiveGenes.Select((Gene x) => x.def).ToList();
				newFoodCatAllow = BSDefLibrary.FoodCategoryDefs.Where((NewFoodCategory x) => x.DefaultAcceptPawn(pawn, activeGenedefs, pawnDiet).Fuse(pawnDiet.Select((PawnDiet y) => y.AcceptFoodCategory(x))).ExplicitlyAllowed()).ToList();
				newFoodCatDeny = BSDefLibrary.FoodCategoryDefs.Where((NewFoodCategory x) => x.DefaultAcceptPawn(pawn, activeGenedefs, pawnDiet).Fuse(pawnDiet.Select((PawnDiet y) => y.AcceptFoodCategory(x))).NotExplicitlyAllowed()).ToList();
				ApparelRestrictions seed = new ApparelRestrictions();
				bool num = GenCollection.Any<Trait>(pawn.story.traits.allTraits, (Predicate<Trait>)((Trait x) => x.def == BSDefs.BS_Giant || ((Def)x.def).defName.ToLower().Contains("AG_ToughSinews") || ((Def)x.def).defName.ToLower().Contains("warcasket"))) || totalSize > 1.99f;
				List<ApparelRestrictions> list = (from x in allPawnExtensions
					where x.apparelRestrictions != null
					select x.apparelRestrictions).ToList();
				if (num)
				{
					list.Add(new ApparelRestrictions
					{
						tags = new FilterListSet<string>
						{
							acceptlist = new AcceptList<string> { "BS_GiantWeapon" }
						}
					});
				}
				if (list.Count > 0)
				{
					seed = list.Aggregate(seed, (ApparelRestrictions acc, ApparelRestrictions x) => acc.MakeFusionWith(x));
					apparelRestrictions = seed;
				}
				else
				{
					apparelRestrictions = null;
				}
				if (GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.animalFineManipulation.HasValue)))
				{
					fineManipulation = allPawnExtensions.Where((PawnExtension x) => x.animalFineManipulation.HasValue).Max((PawnExtension x) => x.animalFineManipulation.Value);
					fineManipulation += allPawnExtensions.Sum((PawnExtension x) => x.animalFineManipulationOffset);
				}
				canWield = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.canWieldThings == true)) || !GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.canWieldThings == false));
			}
			canUseChargers = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.canUseChargers));
			if (canUseChargers)
			{
				float statValue = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.BS_BatteryCharging, true, -1);
				if (statValue <= 0f)
				{
					canUseChargers = false;
					Log.WarningOnce($"[BigAndSmall] {pawn} has canUseChargers enabled but has 0 or negative BatteryChargingEfficiency. Disabling canUseChargers.", 14237890);
				}
				else
				{
					poorUserOfChargers = statValue < 0.71f;
				}
			}
			HandleSkillsAndAptitudes(allPawnExtensions);
			float statValue2 = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_Minimum_Learning_Speed, true, -1);
			_ = pawn.story?.traits?.allTraits;
			bool flag = GenCollection.Any<Hediff>(pawn.health?.hediffSet.hediffs, (Predicate<Hediff>)((Hediff x) => ((Def)x.def).defName == "VU_DraculVampirism" || ((Def)x.def).defName == "BS_ReturnedReanimation"));
			List<Gene> activeGenesByNames = GeneHelpers.GetActiveGenesByNames(pawn, new List<string>(6) { "VU_Unliving", "VU_Lesser_Unliving_Resilience", "VU_Unliving_Resilience", "BS_RoboticResilienceLesser", "BS_RoboticResilience", "BS_IsUnliving" });
			bool flag2 = pawn.health.hediffSet.HasHediff(BSDefs.VU_AnimalReturned, false);
			bool flag3 = pawn.health.hediffSet.HasHediff(BSDefs.VU_DraculAnimalVampirism, false);
			bool flag4 = flag2 || flag3;
			bool flag5 = allActiveGenes.Any((Gene x) => x.def == BSDefs.Ageless);
			bool flag6 = allActiveGenes.Any((Gene x) => x.def == BSDefs.DiseaseFree);
			float ageBiologicalYearsFloat = pawn.ageTracker.AgeBiologicalYearsFloat;
			if (ageBiologicalYearsFloat > 18f && flag5)
			{
				apparentAge = Mathf.Clamp(ageBiologicalYearsFloat, 30f, 60f);
			}
			else if (flag6)
			{
				apparentAge = Mathf.Min(ageBiologicalYearsFloat, 60f);
			}
			else
			{
				apparentAge = Mathf.Min(ageBiologicalYearsFloat, 80f);
			}
			bool num2 = allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "VU_NoBlood") || flag2;
			bool flag7 = flag3;
			bool flag8 = allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "BS_SlowBleeding");
			BleedRateState bleedRateState = (num2 ? BleedRateState.NoBleeding : (flag7 ? BleedRateState.VerySlowBleeding : (flag8 ? BleedRateState.SlowBleeding : BleedRateState.Unchanged)));
			if (GenCollection.Any<RaceTracker>(raceTrackers, (Predicate<RaceTracker>)delegate(RaceTracker x)
			{
				HediffStage curStage = ((Hediff)x).CurStage;
				return curStage != null && curStage.totalBleedFactor == 0f;
			}))
			{
				bleedRateState = BleedRateState.NoBleeding;
			}
			bool flag9 = false;
			if (allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "VU_LethalLover") && pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBond, false) == null)
			{
				flag9 = true;
			}
			isMechanical = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isMechanical)) || pawn.RaceProps.IsMechanoid;
			empVulnerable = !GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.empVulnerable == false)) && (GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.empVulnerable == true)) || isMechanical);
			SetupRacialFeatures(allPawnExtensions);
			bool flag10 = allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "BS_EverFertile");
			Pawn_StoryTracker story = pawn.story;
			int num3;
			if (story != null)
			{
				TraitSet traits = story.traits;
				if (((traits != null) ? new bool?(GenCollection.Any<Trait>(traits.allTraits, (Predicate<Trait>)((Trait x) => !x.Suppressed && ((Def)x.def).defName == "BS_AnimalFriend"))) : ((bool?)null)) == true)
				{
					num3 = 1;
					goto IL_0b74;
				}
			}
			num3 = (isMechanical ? 1 : 0);
			goto IL_0b74;
			IL_0fae:
			int num4;
			bool flag11 = (byte)num4 != 0;
			isUnliving = activeGenesByNames.Count > 0 || flag4 || flag11 || GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isUnliving));
			willBeUndead = flag;
			bleedRateFactor = (GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.bleedRate.HasValue)) ? allPawnExtensions.Where((PawnExtension x) => x.bleedRate.HasValue).Aggregate(1f, (float acc, PawnExtension x) => acc * x.bleedRate.Value) : 1f);
			if (bleedRateFactor == 0f)
			{
				bleedRateState = BleedRateState.NoBleeding;
			}
			bleedRate = bleedRateState;
			deathlike = flag4 || GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isDeathlike));
			unarmedOnly = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.unarmedOnly || x.forceUnarmed)) || allActiveGenes.Any((Gene x) => new List<string> { "BS_UnarmedOnly", "BS_NoEquip", "BS_UnarmedOnly_Android" }.Contains(((Def)x.def).defName));
			succubusUnbonded = flag9;
			romanceTags = (from x in allPawnExtensions
				select x.romanceTags into x
				where x != null
				select x)?.GetMerged();
			if ((romanceTags == null && HumanLikes.Humanlikes.Contains(((Thing)(pawn?)).def)) || (GenCollection.Any<PawnExtension>(racePawnExtensions) && racePawnExtensions.All((PawnExtension x) => x.romanceTags == null)) || ((Thing)(pawn?)).def == ThingDefOf.Human || ((Thing)(pawn?)).def == ThingDefOf.CreepJoiner)
			{
				romanceTags = RomanceTags.simpleRaceDefault;
			}
			pregnancySpeed = allPawnExtensions.Aggregate(1f, (float acc, PawnExtension x) => acc * x.pregnancySpeedMultiplier);
			everFertile = flag10;
			renderCacheOff = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.renderCacheOff));
			partsCanBeHarvested = allPawnExtensions.All((PawnExtension x) => x.partsCanBeHarvested);
			float f;
			bodyPosOffset = f;
			raidWealthMultiplier = StatExtension.GetStatValue((Thing)(object)pawn, StatDef.Named("SM_RaidWealthMultiplier"), true, -1);
			raidWealthOffset = StatExtension.GetStatValue((Thing)(object)pawn, StatDef.Named("SM_RaidWealthOffset"), true, -1);
			bodyRenderSize = GetBodyRenderSize();
			headRenderSize = GetHeadRenderSize();
			float num5;
			headPositionMultiplier = CalculateHeadOffset(num5);
			SetWorldOffset();
			complexHeadOffsets = (from x in allPawnExtensions
				select x.headDrawData into x
				where x != null
				select x).ToList().GetCombinedOffsetsByRot(headPositionMultiplier);
			complexBodyOffsets = (from x in allPawnExtensions
				select x.bodyDrawData into x
				where x != null
				select x).ToList().GetCombinedOffsetsByRot();
			IEnumerable<RotDrawMode?> enumerable = from x in allPawnExtensions
				select x.forcedRotDrawMode into x
				where x.HasValue
				select x;
			forcedRotDrawMode = (GenCollection.EnumerableNullOrEmpty<RotDrawMode?>(enumerable) ? ((RotDrawMode?)null) : enumerable.First());
			if (forcedRotDrawMode.HasValue)
			{
				Pawn obj = pawn;
				object obj2;
				if (obj == null)
				{
					obj2 = null;
				}
				else
				{
					ThingDef corpseDef = obj.RaceProps.corpseDef;
					obj2 = ((corpseDef != null) ? corpseDef.GetCompProperties<CompProperties_Rottable>() : null);
				}
				if (obj2 == null)
				{
					forcedRotDrawMode = null;
				}
			}
			approximatelyNoChange = bodyRenderSize.Approx(1f) && headRenderSize.Approx(1f) && f.Approx(0f) && num5.Approx(1f) && headPositionMultiplier.Approx(1f) && worldspaceOffset.Approx(0f) && complexHeadOffsets == null && complexBodyOffsets == null && pawn.RaceProps.baseBodySize < 2f;
			if ((double)pawn.RaceProps.baseBodySize > 1.49)
			{
				renderCacheOff = true;
			}
			hasComplexHeadOffsets = complexHeadOffsets != null;
			if (isHumanlike)
			{
				ReevaluateGraphics(allPawnExtensions2, racePawnExtensions);
			}
			ScheduleUpdate(1);
			goto end_IL_0040;
			IL_0b74:
			animalFriend = (byte)num3 != 0;
			hideHumanlikeRenderNodes = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.hideHumanlikeRenderNodes));
			facialAnimationDisabled = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.disableFacialAnimations)) || facialAnimationDisabled_Transform;
			IEnumerable<FacialAnimDisabler> enumerable2 = from x in allPawnExtensions
				where x.facialDisabler != null
				select x.facialDisabler;
			facialAnimDisabler = GenCollection.FirstOrFallback<FacialAnimDisabler>(enumerable2, (FacialAnimDisabler)null);
			f = allPawnExtensions.Sum((PawnExtension x) => x.bodyPosOffset);
			num5 = 1f + allPawnExtensions.Sum((PawnExtension x) => x.headPosMultiplier);
			GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.preventDisfigurement));
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.AlcoholHigh, false);
			float num6 = ((firstHediffOfDef != null) ? firstHediffOfDef.Severity : 0f);
			alcoholAmount = num6;
			minimumLearning = statValue2;
			growthPointGain = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_GrowthPointAccumulation, true, -1);
			internalDamageDivisor = (GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.internalDamageDivisor.HasValue)) ? allPawnExtensions.Where((PawnExtension x) => x.internalDamageDivisor.HasValue).Aggregate(1f, (float acc, PawnExtension x) => acc * x.internalDamageDivisor.Value) : 1f);
			if (allPawnExtensions.Count > 0 && GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => !x.canHavePassions)))
			{
				foreach (SkillRecord skill in pawn.skills.skills)
				{
					skill.passion = (Passion)0;
				}
			}
			isBloodFeeder = IsBloodfeederPatch.IsBloodfeeder(pawn) || GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isBloodfeeder));
			hasSizeAffliction = overrideLimits;
			attackSpeedMultiplier = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_AttackSpeed, true, -1);
			attackSpeedUnarmedMultiplier = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_UnarmedAttackSpeed, true, -1);
			isDrone = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isDrone));
			noFamilyRelations = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.noFamilyRelations));
			isAmorphous = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.isAmorphous));
			disableLookChangeDesired = GenCollection.Any<PawnExtension>(allPawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.disableLookChangeDesired));
			Pawn obj3 = pawn;
			if (obj3 != null)
			{
				Pawn_MutantTracker mutant = obj3.mutant;
				if (((mutant == null) ? ((bool?)null) : ((Def)(mutant.Def?)).defName?.ToLower().Contains("shambler")) == true)
				{
					num4 = 1;
					goto IL_0fae;
				}
			}
			num4 = (pawn.health.hediffSet.HasHediff(HediffDefOf.ShamblerCorpse, false) ? 1 : 0);
			goto IL_0fae;
			end_IL_0040:;
		}
		catch (Exception ex2)
		{
			if (!BigAndSmallCache.regenerationAttempted)
			{
				Log.Warning($"Issue reloading cache of {pawn} ({id}). Removing entire cache so it can be regenerated.\n{ex2.Message}\n{ex2.StackTrace}");
				DictCache<Pawn, BSCache>.Cache = new ConcurrentDictionary<Pawn, BSCache>();
				BigAndSmallCache.ScribedCache = new HashSet<BSCache>();
				BigAndSmallCache.regenerationAttempted = true;
			}
			throw;
		}
		finally
		{
			regenerationInProgress = false;
		}
		return true;
	}

	private void SetupRacialFeatures(List<PawnExtension> allPawnExt)
	{
		racialFeatures = new HashSet<RacialFeature>();
		foreach (IGrouping<string, PawnExtension> item3 in from x in allPawnExt
			where x.fuseTag != null || x.featureInfo != null
			group x by x.fuseTag)
		{
			if (item3.Key == null)
			{
				foreach (PawnExtension item4 in item3)
				{
					RacialFeature item = item4.featureInfo.SetupFromThis(new List<PawnExtension>(1) { item4 });
					racialFeatures.Add(item);
				}
				continue;
			}
			List<PawnExtension> list = item3.ToList();
			RacialFeature racialFeature = GenCollection.FirstOrDefault<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension items) => items.featureInfo != null))?.featureInfo;
			if (racialFeature != null)
			{
				RacialFeature item2 = racialFeature.SetupFromThis(list);
				racialFeatures.Add(item2);
			}
		}
		HashSet<RacialFeatureDef> hashSet = new HashSet<RacialFeatureDef>();
		foreach (RacialFeatureDef item5 in allPawnExt.Where((PawnExtension x) => x.RacialFeaturesWithAuto != null).SelectMany((PawnExtension x) => x.RacialFeaturesWithAuto ?? new List<RacialFeatureDef>()))
		{
			hashSet.Add(item5);
		}
		racialFeaturesAuto = hashSet;
	}

	public void HandleSkillsAndAptitudes(List<PawnExtension> allPawnExt)
	{
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		aptitudes = allPawnExt.Where((PawnExtension x) => x.aptitudes != null).SelectMany((PawnExtension x) => x.aptitudes).ToList();
		if (GenCollection.Any<PawnExtension>(allPawnExt, (Predicate<PawnExtension>)((PawnExtension x) => x.clampedSkills != null)))
		{
			Dictionary<SkillDef, IntRange> dictionary = (from x in allPawnExt.Where((PawnExtension x) => x.clampedSkills != null).SelectMany((PawnExtension x) => x.clampedSkills)
				group x by x.Skill).ToDictionary((Func<IGrouping<SkillDef, SkillRange>, SkillDef>)((IGrouping<SkillDef, SkillRange> g) => g.Key), (Func<IGrouping<SkillDef, SkillRange>, IntRange>)((IGrouping<SkillDef, SkillRange> g) => new IntRange(g.Min((SkillRange x) => x.Range.min), g.Max((SkillRange x) => x.Range.max))));
			foreach (SkillRecord skill3 in pawn.skills.skills)
			{
				if (dictionary.TryGetValue(skill3.def, out var value))
				{
					int level = skill3.GetLevel(false);
					if (level < value.min)
					{
						skill3.Level = value.min;
					}
					else if (level > value.max)
					{
						skill3.Level = value.max;
					}
				}
			}
		}
		IEnumerable<WorkTypeDef> enumerable = allPawnExt.SelectMany((PawnExtension x) => x.disabledWorkTypes ?? new List<WorkTypeDef>()).Distinct();
		if (pawn.skills?.skills == null || (!GenCollection.Any<Aptitude>(aptitudes) && !enumerable.Any() && !GenCollection.Any<WorkTypeDef>(disabledWorkTypes) && !GenCollection.Any<PawnExtension>(allPawnExt, (Predicate<PawnExtension>)((PawnExtension x) => x.disableSkillsWithMinus20Aptitude || x.disableSkillBelowAptitude != null)) && GenCollection.Any<SkillDef>(skillsDisabledByExtensions)))
		{
			return;
		}
		if (pawn.cachedDisabledWorkTypes == null)
		{
			pawn.GetDisabledWorkTypes(false);
			pawn.GetDisabledWorkTypes(true);
		}
		bool flag = false;
		if (explicitlyDisabled.Count() != enumerable.Count() || explicitlyDisabled.Intersect(enumerable).Count() != enumerable.Count())
		{
			explicitlyDisabled = enumerable.ToList();
			flag = true;
		}
		HashSet<SkillDef> skillsDisabled = new HashSet<SkillDef>();
		if (flag)
		{
			foreach (SkillRecord skill in pawn.skills.skills)
			{
				IEnumerable<WorkTypeDef> enumerable2 = DefDatabase<WorkTypeDef>.AllDefs.Where((WorkTypeDef wt) => wt.relevantSkills.Contains(skill.def));
				if (enumerable2.Count() > 0 && enumerable.Intersect(enumerable2).Count() == enumerable2.Count())
				{
					skillsDisabled.Add(skill.def);
				}
			}
		}
		HashSet<Aptitude> hashSet = new HashSet<Aptitude>();
		foreach (Aptitude item in allPawnExt.SelectMany((PawnExtension x) => x.disableSkillBelowAptitude ?? new List<Aptitude>()).Distinct())
		{
			hashSet.Add(item);
		}
		HashSet<Aptitude> source = hashSet;
		foreach (SkillRecord skill2 in pawn.skills.skills)
		{
			skill2.aptitudeCached = null;
			int num = (from x in source
				where x.skill == skill2.def
				select x.level).DefaultIfEmpty(-19).Min();
			if (skill2.Aptitude < num)
			{
				skillsDisabled.Add(skill2.def);
				if (!skillsDisabledByExtensions.Contains(skill2.def))
				{
					flag = true;
				}
			}
		}
		if (!GenList.NullOrEmpty<SkillDef>((IList<SkillDef>)skillsDisabledByExtensions) && GenCollection.Any<SkillDef>(skillsDisabledByExtensions, (Predicate<SkillDef>)((SkillDef x) => !skillsDisabled.Contains(x))))
		{
			flag = true;
		}
		skillsDisabledByExtensions = skillsDisabled.ToList();
		if (!flag)
		{
			return;
		}
		List<WorkTypeDef> list = enumerable.ToList();
		foreach (SkillDef skillDef in skillsDisabled)
		{
			list.AddRange(DefDatabase<WorkTypeDef>.AllDefs.Where((WorkTypeDef wt) => wt.relevantSkills.Contains(skillDef)));
		}
		disabledWorkTypes = list.ToList();
		pawn.Notify_DisabledWorkTypesChanged();
	}

	private void CalculateGenderAndApparentGender(List<PawnExtension> allPawnExt)
	{
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		Gender? val = (GenCollection.Any<PawnExtension>(allPawnExt, (Predicate<PawnExtension>)((PawnExtension x) => x.forceGender.HasValue)) ? allPawnExt.First((PawnExtension x) => x.forceGender.HasValue).forceGender : ((Gender?)null));
		val = (GenCollection.Any<PawnExtension>(allPawnExt, (Predicate<PawnExtension>)((PawnExtension x) => x.ignoreForceGender)) ? ((Gender?)null) : val);
		if (val.HasValue && val != (Gender?)pawn.gender)
		{
			pawn.gender = val.Value;
		}
		apparentGender = GetApparentGender(allPawnExt);
	}

	private Gender? GetApparentGender(List<PawnExtension> allExts = null)
	{
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Invalid comparison between Unknown and I4
		Gender? val = GenCollection.FirstOrFallback<PawnExtension>((IEnumerable<PawnExtension>)allExts, (Func<PawnExtension, bool>)((PawnExtension x) => x.ApparentGender.HasValue), (PawnExtension)null)?.ApparentGender;
		bool flag = GenCollection.Any<PawnExtension>(allExts, (Predicate<PawnExtension>)((PawnExtension x) => x.invertApparentGender));
		if (val.HasValue && flag)
		{
			val = (Gender)((val != (Gender?)1) ? 1 : 2);
		}
		if (!val.HasValue && flag)
		{
			val = (Gender)(((int)pawn.gender != 1) ? 1 : 2);
		}
		return val;
	}

	public void ReevaluateGraphics(List<PawnExtension> otherExts = null, List<PawnExtension> raceExts = null)
	{
		if (otherExts == null || raceExts == null)
		{
			otherExts = pawn.GetAllExtensions<PawnExtension>();
			raceExts = pawn.GetRacePawnExtensions();
		}
		headMaterial = null;
		bodyMaterial = null;
		headGraphicPath = null;
		bodyGraphicPath = null;
		List<PawnExtension> list = otherExts;
		List<PawnExtension> list2 = raceExts;
		List<PawnExtension> list3 = new List<PawnExtension>(list.Count + list2.Count);
		list3.AddRange(list);
		list3.AddRange(list2);
		CalculateGenderAndApparentGender(list3);
		int pawnRNGSeed = pawn.GetPawnRNGSeed();
		SetPawnHeadAndBodyTextures(otherExts.ToHashSet(), raceExts.ToHashSet(), pawnRNGSeed);
		BodyTypesPerGender bodyTypesPerGender = new BodyTypesPerGender();
		bodyTypesPerGender.AddRange(otherExts.SelectMany((PawnExtension x) => x.bodyTypes));
		if (bodyTypesPerGender.Count == 0)
		{
			bodyTypesPerGender.AddRange(raceExts.SelectMany((PawnExtension x) => x.bodyTypes));
		}
		bool flag = bodyTypeOverride == null;
		bodyTypeOverride = ((bodyTypesPerGender.Count == 0) ? null : bodyTypesPerGender);
		if (bodyTypeOverride == null && !flag)
		{
			PawnGenerator.GetBodyTypeFor(pawn);
		}
		if (this != defaultCache && pawn?.story?.bodyType != null && pawn?.story?.headType != null)
		{
			GenderMethods.UpdateBodyHeadAndBeardPostGenderChange(this);
		}
	}

	private void SetPawnHeadAndBodyTextures(HashSet<PawnExtension> otherPawnExt, HashSet<PawnExtension> fromRace, int pawnRNGSeed)
	{
		List<(AdaptivePathList, PawnExtension)> list = GetValidPaths(otherPawnExt, (PawnExtension x) => x.headPaths, this);
		List<(AdaptivePathList, PawnExtension)> list2 = GetValidPaths(otherPawnExt, (PawnExtension x) => x.headDessicatedPaths, this);
		List<(AdaptivePathList, PawnExtension)> list3 = GetValidPaths(otherPawnExt, (PawnExtension x) => x.bodyPaths, this);
		List<(AdaptivePathList, PawnExtension)> list4 = GetValidPaths(otherPawnExt, (PawnExtension x) => x.bodyDessicatedPaths, this);
		list = ((list.Count == 0) ? GetValidPaths(fromRace, (PawnExtension x) => x.headPaths, this) : list);
		list2 = ((list2.Count == 0) ? GetValidPaths(fromRace, (PawnExtension x) => x.headDessicatedPaths, this) : list2);
		list3 = ((list3.Count == 0) ? GetValidPaths(fromRace, (PawnExtension x) => x.bodyPaths, this) : list3);
		list4 = ((list4.Count == 0) ? GetValidPaths(fromRace, (PawnExtension x) => x.bodyDessicatedPaths, this) : list4);
		headGraphicPath = null;
		bodyGraphicPath = null;
		headDessicatedGraphicPath = null;
		bodyDessicatedGraphicPath = null;
		headMaterial = GenCollection.FirstOrFallback<PawnExtension>((IEnumerable<PawnExtension>)otherPawnExt, (Func<PawnExtension, bool>)((PawnExtension x) => x.headMaterial != null), (PawnExtension)null)?.headMaterial;
		bodyMaterial = GenCollection.FirstOrFallback<PawnExtension>((IEnumerable<PawnExtension>)otherPawnExt, (Func<PawnExtension, bool>)((PawnExtension x) => x.bodyMaterial != null), (PawnExtension)null)?.bodyMaterial;
		if (headMaterial == null)
		{
			headMaterial = GenCollection.FirstOrFallback<PawnExtension>((IEnumerable<PawnExtension>)fromRace, (Func<PawnExtension, bool>)((PawnExtension x) => x.headMaterial != null), (PawnExtension)null)?.headMaterial;
		}
		if (bodyMaterial == null)
		{
			bodyMaterial = GenCollection.FirstOrFallback<PawnExtension>((IEnumerable<PawnExtension>)fromRace, (Func<PawnExtension, bool>)((PawnExtension x) => x.bodyMaterial != null), (PawnExtension)null)?.bodyMaterial;
		}
		PawnExtension pawnExtension = null;
		RandBlock val = default(RandBlock);
		if (list.Count != 0)
		{
			((RandBlock)(ref val))._002Ector(pawnRNGSeed);
			try
			{
				(AdaptivePathList, PawnExtension) tuple = GenCollection.RandomElement<(AdaptivePathList, PawnExtension)>((IEnumerable<(AdaptivePathList, PawnExtension)>)list);
				string text = GenCollection.RandomElement<string>((IEnumerable<string>)tuple.Item1.GetPaths(this, apparentGender));
				PawnExtension item = tuple.Item2;
				headGraphicPath = text;
				pawnExtension = item;
				if (tuple.Item2.headMaterial != null)
				{
					headMaterial = tuple.Item2.headMaterial;
				}
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		if (list2.Count != 0)
		{
			if (pawnExtension != null && pawnExtension.headDessicatedPaths.ValidFor(this, apparentGender))
			{
				((RandBlock)(ref val))._002Ector(pawnRNGSeed);
				try
				{
					headDessicatedGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)pawnExtension.headDessicatedPaths.GetPaths(this, apparentGender));
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
			else
			{
				(AdaptivePathList, PawnExtension) tuple2 = GenCollection.RandomElement<(AdaptivePathList, PawnExtension)>((IEnumerable<(AdaptivePathList, PawnExtension)>)list2);
				((RandBlock)(ref val))._002Ector(pawnRNGSeed);
				try
				{
					headDessicatedGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)tuple2.Item1.GetPaths(this, apparentGender));
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
		}
		PawnExtension pawnExtension2 = pawnExtension;
		if (list3.Count != 0)
		{
			if (pawnExtension != null && pawnExtension.bodyPaths.ValidFor(this, apparentGender))
			{
				((RandBlock)(ref val))._002Ector(pawnRNGSeed);
				try
				{
					bodyGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)pawnExtension.bodyPaths.GetPaths(this, apparentGender));
					if (pawnExtension.bodyMaterial != null)
					{
						bodyMaterial = pawnExtension.bodyMaterial;
					}
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
			else
			{
				(AdaptivePathList, PawnExtension) tuple3 = GenCollection.RandomElement<(AdaptivePathList, PawnExtension)>((IEnumerable<(AdaptivePathList, PawnExtension)>)list3);
				((RandBlock)(ref val))._002Ector(pawnRNGSeed);
				try
				{
					string text = GenCollection.RandomElement<string>((IEnumerable<string>)tuple3.Item1.GetPaths(this, apparentGender));
					PawnExtension item2 = tuple3.Item2;
					bodyGraphicPath = text;
					pawnExtension2 = item2;
					if (tuple3.Item2.bodyMaterial != null)
					{
						bodyMaterial = tuple3.Item2.bodyMaterial;
					}
				}
				finally
				{
					((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
				}
			}
		}
		if (list4.Count == 0)
		{
			return;
		}
		if (pawnExtension2 != null && pawnExtension2.bodyDessicatedPaths.ValidFor(this, apparentGender))
		{
			((RandBlock)(ref val))._002Ector(pawnRNGSeed);
			try
			{
				bodyDessicatedGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)pawnExtension2.bodyDessicatedPaths.GetPaths(this, apparentGender));
				return;
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		(AdaptivePathList, PawnExtension) tuple4 = GenCollection.RandomElement<(AdaptivePathList, PawnExtension)>((IEnumerable<(AdaptivePathList, PawnExtension)>)list4);
		((RandBlock)(ref val))._002Ector(pawnRNGSeed);
		try
		{
			bodyDessicatedGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)tuple4.Item1.GetPaths(this, apparentGender));
		}
		finally
		{
			((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
		}
		List<(AdaptivePathList, PawnExtension)> GetValidPaths(HashSet<PawnExtension> allPawnExt, Func<PawnExtension, AdaptivePathList> pathSelector, BSCache cache)
		{
			List<(AdaptivePathList, PawnExtension)> list5 = (from p in allPawnExt
				select (pathSelector(p), p: p) into x
				where x.Item1 != null && x.Item1.ValidFor(cache, apparentGender)
				select x).ToList();
			if (list5.Count == 0)
			{
				return new List<(AdaptivePathList, PawnExtension)>();
			}
			int bestScore = list5.Max<(AdaptivePathList, PawnExtension)>(((AdaptivePathList, PawnExtension p) x) => x.p.priority);
			return list5.Where<(AdaptivePathList, PawnExtension)>(((AdaptivePathList, PawnExtension p) x) => x.p.priority == bestScore).ToList();
		}
	}

	public void ScheduleUpdate(int delayTicks)
	{
		int key = BS.Tick + delayTicks;
		if (!BigAndSmallCache.schedulePostUpdate.ContainsKey(key))
		{
			BigAndSmallCache.schedulePostUpdate[key] = new HashSet<BSCache>();
		}
		BigAndSmallCache.schedulePostUpdate[key].Add(this);
	}

	/// <summary>
	/// Stuff that should be run a bit later. Typically 1 tick. This also has the benefit that it will never run more than once per tick.
	///
	/// Anything that we don't need to figure out RIGHT NOW. Can go here.
	///
	/// More stuff should probably be moved here. Delaying stuff helps dealing with issues like genes being appended on-by-one.
	/// </summary>
	public void DelayedUpdate()
	{
		//IL_0653: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null || pawn.Dead)
		{
			return;
		}
		((Def)((Thing)pawn).def).modExtensions?.OfType<RaceExtension>()?.FirstOrDefault()?.ApplyTrackerIfMissing(pawn, this);
		List<PawnExtension> racePawnExtensions = pawn.GetRacePawnExtensions();
		HashSet<Gene> allActiveGenes = pawn.GetAllActiveGenes();
		List<PawnExtension> allExtensions = pawn.GetAllExtensions<PawnExtension>(null, new List<Type>(1) { typeof(RaceTracker) });
		List<PawnExtension> list = racePawnExtensions;
		List<PawnExtension> list2 = allExtensions;
		List<PawnExtension> list3 = new List<PawnExtension>(list.Count + list2.Count);
		list3.AddRange(list);
		list3.AddRange(list2);
		List<PawnExtension> list4 = list3;
		list4.ForEach(delegate(PawnExtension x)
		{
			x.transformGene?.TryTransform(pawn);
		});
		if (noFamilyRelations)
		{
			for (int num = pawn.relations.DirectRelations.Count - 1; num >= 0; num--)
			{
				if (pawn.relations.DirectRelations.Count > num)
				{
					DirectPawnRelation val = pawn.relations.DirectRelations[num];
					bool num2 = val.def == PawnRelationDefOf.Parent || val.def == PawnRelationDefOf.Parent;
					if (val.def.implied || val.def.inbredChanceOnChild > 0f)
					{
						pawn.relations.TryRemoveDirectRelation(val.def, val.otherPawn);
					}
					if (num2)
					{
						PawnRelationDef bS_Creator = BSDefs.BS_Creator;
						if (bS_Creator != null)
						{
							pawn.relations.AddDirectRelation(bS_Creator, val.otherPawn);
						}
					}
				}
			}
		}
		List<Trait> list5 = pawn.story?.traits?.allTraits;
		List<Hediff> list6 = pawn.health?.hediffSet.hediffs;
		if (list5 != null)
		{
			try
			{
				if (pawn.needs != null && GenCollection.Any<Trait>(list5, (Predicate<Trait>)((Trait x) => !x.Suppressed && ((Def)x.def).defName == "BS_AlcoholAddict")) && !GenCollection.Any<Hediff>(list6, (Predicate<Hediff>)((Hediff x) => ((Def)x.def).defName == "AlcoholAddiction")))
				{
					pawn.health.AddHediff(HediffDef.Named("AlcoholAddiction"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
			catch
			{
			}
		}
		if (BSDefs.BS_SoulPower != null && (double)StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.BS_SoulPower, true, -1) > 0.1 && !pawn.Dead && !GenCollection.Any<Hediff>(list6, (Predicate<Hediff>)((Hediff x) => x.def == BSDefs.BS_SoulPowerHediff)))
		{
			pawn.health.AddHediff(BSDefs.BS_SoulPowerHediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		UpdateFineManipulationHediffs(list6);
		bool flag = allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "BS_SelfRepairingApparel");
		bool flag2 = allActiveGenes.Any((Gene x) => ((Def)x.def).defName == "BS_IndestructibleApparel");
		flag2 |= pawn.health.hediffSet.HasHediff(BSDefs.BS_IndestructibelApparel, false);
		int ticksGame = Find.TickManager.TicksGame;
		Pawn_ApparelTracker apparel = pawn.apparel;
		if (((apparel != null) ? apparel.WornApparel : null) != null && pawn.apparel.WornApparel.Count > 0)
		{
			if (flag || flag2)
			{
				List<Apparel> wornApparel = pawn.apparel.WornApparel;
				foreach (Apparel apparel2 in wornApparel)
				{
					bool flag3 = false;
					foreach (ApparelCache item in apparelCaches.Where((ApparelCache x) => x.apparelID == ((Thing)apparel2).ThingID))
					{
						flag3 = true;
						if (flag2)
						{
							item.RepairAllDurability(apparel2);
						}
						else if (flag)
						{
							item.RepairDurability(apparel2, ticksGame, 0.24f);
						}
					}
					if (!flag3)
					{
						apparelCaches.Add(new ApparelCache(apparel2));
					}
				}
				for (int num3 = apparelCaches.Count - 1; num3 >= 0; num3--)
				{
					ApparelCache apparelCache = apparelCaches[num3];
					if (!GenCollection.Any<Apparel>(wornApparel, (Predicate<Apparel>)((Apparel x) => ((Thing)x).ThingID == apparelCache.apparelID)))
					{
						apparelCaches.RemoveAt(num3);
					}
				}
			}
			if (apparelRestrictions != null)
			{
				List<Apparel> list7 = new List<Apparel>();
				list7.AddRange(pawn.apparel.WornApparel.Where((Apparel app) => ((Thing)(app?)).def != null && apparelRestrictions.CanWear(((Thing)app).def) != null));
				if (list7.Count > 0)
				{
					for (int num4 = list7.Count - 1; num4 >= 0; num4--)
					{
						Apparel val2 = list7[num4];
						try
						{
							if (((Thing)pawn).Faction == Faction.OfPlayerSilentFail || pawn.IsPrisonerOfColony)
							{
								pawn.apparel.TryDrop(val2);
							}
							else
							{
								pawn.apparel.Remove(val2);
							}
						}
						catch (Exception ex)
						{
							Log.Warning($"[BigAndSmall] Failed to remove apparel {val2} from {pawn.Name}.\n{ex.Message}\n{ex.StackTrace}");
						}
					}
				}
			}
		}
		if (!canWield)
		{
			if (((Thing)pawn).Spawned && (pawn.IsColonist || pawn.IsPrisonerOfColony))
			{
				pawn.equipment.DropAllEquipment(((Thing)pawn).Position, false, false);
			}
			else
			{
				Pawn_EquipmentTracker equipment = pawn.equipment;
				if (equipment != null)
				{
					equipment.DestroyAllEquipment((DestroyMode)0);
				}
			}
		}
		banAddictions = GenCollection.Any<PawnExtension>(list4, (Predicate<PawnExtension>)((PawnExtension x) => x.banAddictionsByDefault));
		try
		{
			SimpleRaceUpdate(racePawnExtensions, allExtensions, pawn.GetRaceCompProps());
		}
		catch (Exception ex2)
		{
			if (!BigAndSmallCache.regenerationAttempted)
			{
				Log.Warning($"Issue updating RaceCache of {pawn} ({id}). Cleaing and regenerating cache.\n{ex2.Message}\n{ex2.StackTrace}");
				DictCache<Pawn, BSCache>.Cache = new ConcurrentDictionary<Pawn, BSCache>();
				BigAndSmallCache.ScribedCache = new HashSet<BSCache>();
				BigAndSmallCache.regenerationAttempted = true;
			}
			throw;
		}
		if (GenCollection.Any<Gene>(genesActivated) || GenCollection.Any<Gene>(genesDeactivated))
		{
			GeneHelpers.RefreshAllGenes(pawn, genesActivated, genesDeactivated);
			genesDeactivated.Clear();
			genesActivated.Clear();
		}
		Pawn_SkillTracker skills = pawn.skills;
		if (skills != null)
		{
			skills.DirtyAptitudes();
		}
		if (GenCollection.Any<PawnExtension>(list4, (Predicate<PawnExtension>)((PawnExtension x) => x.removeTattoos)))
		{
			pawn.style.BodyTattoo = null;
			pawn.style.FaceTattoo = null;
		}
	}

	private void UpdateFineManipulationHediffs(List<Hediff> hediffs)
	{
		HediffDef targetManipulationHediff = null;
		List<HediffDef> manipulationHediffs = new List<HediffDef>(2)
		{
			BSDefs.BS_NoHands,
			BSDefs.BS_PoorHands
		};
		if (fineManipulation.HasValue)
		{
			if ((double?)fineManipulation < 0.45)
			{
				targetManipulationHediff = BSDefs.BS_NoHands;
			}
			else if ((double?)fineManipulation < 0.75)
			{
				targetManipulationHediff = BSDefs.BS_PoorHands;
			}
		}
		List<Hediff> list = new List<Hediff>();
		foreach (Hediff item in hediffs.Where((Hediff x) => manipulationHediffs.Contains(x.def)))
		{
			if (item.def != targetManipulationHediff)
			{
				list.Add(item);
			}
		}
		list.ForEach((Action<Hediff>)pawn.health.RemoveHediff);
		if (targetManipulationHediff != null && !GenCollection.Any<Hediff>(hediffs, (Predicate<Hediff>)((Hediff x) => x.def == targetManipulationHediff)))
		{
			pawn.health.AddHediff(targetManipulationHediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}

	private void SimpleRaceUpdate(List<PawnExtension> raceExts, List<PawnExtension> otherPawnExts, List<CompProperties_Race> raceCompProps)
	{
		List<PawnExtension> list = otherPawnExts;
		List<PawnExtension> list2 = new List<PawnExtension>(raceExts.Count + list.Count);
		list2.AddRange(raceExts);
		list2.AddRange(list);
		List<PawnExtension> allExt2 = list2;
		if (UpdateGeneOverrideStates(allExt2))
		{
			UpdatePawnExts(raceExts, out otherPawnExts, out allExt2);
		}
		UpdateFrequentUpdateGeneList();
		Metamorphosis.HandleMetamorph(pawn, allExt2);
		ProcessRaceGeneRequirements(raceExts);
		HandleTraitRequirements(raceExts);
		ProcessForcedHediffs(allExt2);
		ProcessRaceHediffRequirements(raceExts);
		ProcessHediffsToRemove(allExt2);
		UpdateGeneOverrideStates(allExt2);
		raceCompProps.EnsureValidBodyType(this);
		raceCompProps.EnsureValidHeadType(this);
		void UpdatePawnExts(List<PawnExtension> raceExts, out List<PawnExtension> otherPawnExts, out List<PawnExtension> allExt)
		{
			otherPawnExts = pawn.GetAllExtensions<PawnExtension>(null, new List<Type>(1) { typeof(RaceTracker) });
			List<PawnExtension> list3 = otherPawnExts;
			List<PawnExtension> list4 = new List<PawnExtension>(raceExts.Count + list3.Count);
			list4.AddRange(raceExts);
			list4.AddRange(list3);
			allExt = list4;
		}
	}

	private void UpdateFrequentUpdateGeneList()
	{
		if (pawn.genes == null)
		{
			return;
		}
		foreach (Gene item in pawn.genes.GenesListForReading)
		{
			if (GenCollection.Any<PawnExtension>(item.def.GetAllPawnExtensionsOnGene(), (Predicate<PawnExtension>)((PawnExtension x) => !GenList.NullOrEmpty<ConditionalStatAffecter>((IList<ConditionalStatAffecter>)x.conditionals))))
			{
				BigAndSmallCache.frequentUpdateGenes[item] = item.Active;
			}
		}
	}

	private void ProcessRaceGeneRequirements(List<PawnExtension> raceExts)
	{
		if (pawn.genes == null)
		{
			return;
		}
		if (endogenesRemovedByRace == null)
		{
			endogenesRemovedByRace = new List<GeneDef>();
		}
		if (xenoenesRemovedByRace == null)
		{
			xenoenesRemovedByRace = new List<GeneDef>();
		}
		raceExts.ForEach(delegate(PawnExtension ext)
		{
			ext.ForcedEndogenes.Where((GeneDef g) => !pawn.HasGene(g)).ToList().ForEach(delegate(GeneDef g)
			{
				pawn.genes.AddGene(g, false);
			});
		});
		raceExts.ForEach(delegate(PawnExtension ext)
		{
			ext.forcedXenogenes?.Where((GeneDef g) => !pawn.HasGene(g)).ToList().ForEach(delegate(GeneDef g)
			{
				pawn.genes.AddGene(g, true);
			});
		});
		List<Gene> list = pawn.genes.Xenogenes.Where((Gene g) => raceExts.Select((PawnExtension ext) => ext.IsGeneLegal(g.def, removalCheck: true)).Aggregate((FilterResult a, FilterResult b) => a.Fuse(b)).Denied()).ToList();
		if (list.Count > 0)
		{
			for (int num = list.Count - 1; num >= 0; num--)
			{
				Gene val = list[num];
				xenoenesRemovedByRace.Add(val.def);
				pawn.genes.RemoveGene(val);
			}
		}
		List<Gene> list2 = pawn.genes.Endogenes.Where((Gene g) => raceExts.Select((PawnExtension ext) => ext.IsGeneLegal(g.def, removalCheck: true)).Aggregate((FilterResult a, FilterResult b) => a.Fuse(b)).Denied()).ToList();
		if (list2.Count > 0)
		{
			for (int num2 = list2.Count - 1; num2 >= 0; num2--)
			{
				Gene val2 = list2[num2];
				endogenesRemovedByRace.Add(val2.def);
				pawn.genes.RemoveGene(val2);
			}
		}
	}

	private void HandleTraitRequirements(List<PawnExtension> raceExts)
	{
		TraitSet traits = pawn.story?.traits;
		if (traits == null)
		{
			return;
		}
		List<PawnExtension.TraitDegreeData> allForcedTraits = raceExts.SelectMany((PawnExtension ext) => ext.GetForcedTraits()).ToList();
		List<PawnExtension.TraitDegreeData> list = allForcedTraits.Where(delegate(PawnExtension.TraitDegreeData ft)
		{
			Trait trait = traits.GetTrait(ft.Def);
			return trait == null || trait.Degree != ft.Degree;
		}).Distinct().ToList();
		FilterListSet<TraitDef> traitFilter = (from x in raceExts
			where x.traitFilters != null
			select x.traitFilters).MergeFilters();
		List<Trait> list2 = traits.allTraits.Where((Trait t) => traitFilter != null && !GenCollection.Any<PawnExtension.TraitDegreeData>(allForcedTraits, (Predicate<PawnExtension.TraitDegreeData>)((PawnExtension.TraitDegreeData ft) => ft.Def == t.def && ft.Degree == t.Degree)) && traitFilter.GetFilterResult(t.def).Denied()).ToList();
		if (list2.Count > 0)
		{
			for (int num = list2.Count - 1; num >= 0; num--)
			{
				Trait val = list2[num];
				traits.allTraits.Remove(val);
				traits.RemoveTrait(val, false);
			}
		}
		if (list.Count <= 0)
		{
			return;
		}
		foreach (PawnExtension.TraitDegreeData item in list)
		{
			traits.GetTrait(item.Def, item.Degree);
		}
	}

	private void ProcessForcedHediffs(List<PawnExtension> pawnExts)
	{
		List<HediffToBody> prevToBody = this.hediffsToBody;
		List<HediffToBodyparts> prevToParts = this.hediffsToParts;
		List<HediffToBodyparts> hediffsToParts = pawnExts.SelectMany((PawnExtension x) => x.applyPartHediff ?? new List<HediffToBodyparts>()).ToList();
		List<HediffToBody> hediffsToBody = pawnExts.SelectMany((PawnExtension x) => x.applyBodyHediff ?? new List<HediffToBody>()).ToList();
		if (hediffsToParts.Count == 0 && hediffsToBody.Count == 0 && prevToBody.Count == 0 && prevToParts.Count == 0)
		{
			return;
		}
		hediffsToParts = hediffsToParts.Where((HediffToBodyparts h) => pawnExts.All((PawnExtension x) => ConditionalManager.TestConditionals(pawn, h.conditionals) && PrerequisiteValidator.SetIsValid(pawn, h.prerequisiteSets) && x.IsHediffLegal(h.hediff).Accepted())).ToList();
		hediffsToBody = hediffsToBody.Where((HediffToBody h) => pawnExts.All((PawnExtension x) => ConditionalManager.TestConditionals(pawn, h.conditionals) && PrerequisiteValidator.SetIsValid(pawn, h.prerequisiteSets) && x.IsHediffLegal(h.hediff).Accepted())).ToList();
		List<HediffToBody> list = prevToBody.Where((HediffToBody h) => !hediffsToBody.Contains(h)).ToList();
		List<HediffToBodyparts> list2 = prevToParts.Where((HediffToBodyparts h) => !hediffsToParts.Contains(h)).ToList();
		List<HediffToBody> list3 = hediffsToBody.Where((HediffToBody h) => !prevToBody.Contains(h)).ToList();
		List<HediffToBodyparts> list4 = hediffsToParts.Where((HediffToBodyparts h) => !prevToParts.Contains(h)).ToList();
		if (hediffsToParts.Count > 0)
		{
			HashSet<BodyPartRecord> hashSet = new HashSet<BodyPartRecord>();
			foreach (BodyPartRecord notMissingPart in pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null))
			{
				hashSet.Add(notMissingPart);
			}
			HashSet<BodyPartRecord> partsToConsider = hashSet;
			foreach (HediffToBodyparts item in list4)
			{
				item.hediff.TryAddToAllMatchingParts(pawn, item.bodyparts, partsToConsider);
			}
		}
		if (hediffsToBody.Count > 0)
		{
			foreach (HediffToBody item2 in list3)
			{
				if (item2.hediff != null)
				{
					try
					{
						pawn.health.GetOrAddHediff(item2.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
					catch (Exception ex)
					{
						Log.Message(string.Format("Encountered exception when running {0} for {1}:\n{2}\n{3}", "GetOrAddHediff", item2?.hediff, ex.Message, ex.StackTrace));
					}
				}
			}
		}
		if (list.Count > 0)
		{
			for (int num = list.Count - 1; num >= 0; num--)
			{
				list[num].hediff.TryRemoveAllOfType(pawn);
			}
		}
		if (list2.Count > 0)
		{
			for (int num2 = list2.Count - 1; num2 >= 0; num2--)
			{
				list2[num2].hediff.TryRemoveAllOfType(pawn);
			}
		}
		this.hediffsToBody = hediffsToBody;
		this.hediffsToParts = hediffsToParts;
	}

	private void ProcessRaceHediffRequirements(List<PawnExtension> raceExts)
	{
		if (pawn.health?.hediffSet != null)
		{
			FilterListSet<HediffDef> hediffFilter = (from x in raceExts
				where x.hediffFilters != null
				select x.hediffFilters).MergeFilters();
			(from h in raceExts.SelectMany((PawnExtension x) => x.forcedHediffs ?? new List<HediffDef>()).ToHashSet()
				where (!pawn.health.hediffSet.HasHediff(h, false) && hediffFilter == null) || hediffFilter.GetFilterResult(h).Accepted()
				select h).ToList().ForEach(delegate(HediffDef h)
			{
				pawn.health.AddHediff(h, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			});
		}
	}

	private void ProcessHediffsToRemove(List<PawnExtension> pawnExts)
	{
		FilterListSet<HediffDef> hediffFilter = (from x in pawnExts
			where x.hediffFilters != null
			select x.hediffFilters).MergeFilters();
		List<Hediff> list = new List<Hediff>();
		if (hediffFilter == null || hediffFilter.IsEmpty())
		{
			if (banAddictions)
			{
				list = pawn.health.hediffSet.hediffs.Where((Hediff h) => h is Hediff_Addiction).ToList();
			}
		}
		else
		{
			list = pawn.health.hediffSet.hediffs.Where((Hediff h) => hediffFilter.GetFilterResult(h.def).Denied() || (h is Hediff_Addiction && banAddictions && hediffFilter.GetFilterResult(h.def).NotExplicitlyAllowed())).ToList();
		}
		if (list.Count > 0)
		{
			for (int num = list.Count - 1; num >= 0; num--)
			{
				Hediff val = list[num];
				pawn.health.RemoveHediff(val);
			}
		}
	}

	private void ProcessHairFilters(PawnExtension props)
	{
		PawnStyleItemChooser.RandomHairFor(pawn);
	}

	public void CalculateSize(DevelopmentalStage dStage, List<PawnExtension> geneExts, bool overrideLimits)
	{
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_0206: Invalid comparison between Unknown and I4
		//IL_027e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Invalid comparison between Unknown and I4
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a5: Invalid comparison between Unknown and I4
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d9: Invalid comparison between Unknown and I4
		//IL_02f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fb: Invalid comparison between Unknown and I4
		int ticksGame = Find.TickManager.TicksGame;
		if (!lastUpdateTick.HasValue || lastUpdateTick != ticksGame)
		{
			lastUpdateTick = ticksGame;
			previousScaleMultiplier = scaleMultiplier;
			healthMultiplier_previous = CalculateHealthMultiplier(scaleMultiplier, pawn);
		}
		float num = geneExts.Sum(delegate(PawnExtension x)
		{
			Pawn obj = pawn;
			float? age;
			if (obj == null)
			{
				age = null;
			}
			else
			{
				Pawn_AgeTracker ageTracker = obj.ageTracker;
				age = ((ageTracker != null) ? new float?(ageTracker.AgeBiologicalYearsFloat) : ((float?)null));
			}
			return x.GetSizeFromSizeByAge(age);
		});
		float num2 = geneExts.Where((PawnExtension x) => x.sizeByAgeMult != null).Aggregate(1f, delegate(float acc, PawnExtension x)
		{
			Pawn obj2 = pawn;
			float? age2;
			if (obj2 == null)
			{
				age2 = null;
			}
			else
			{
				Pawn_AgeTracker ageTracker2 = obj2.ageTracker;
				age2 = ((ageTracker2 != null) ? new float?(ageTracker2.AgeBiologicalYearsFloat) : ((float?)null));
			}
			return acc * x.GetSizeMultiplierFromSizeByAge(age2);
		});
		Pawn obj3 = pawn;
		float? obj4;
		if (obj3 == null)
		{
			obj4 = null;
		}
		else
		{
			Pawn_AgeTracker ageTracker3 = obj3.ageTracker;
			obj4 = ((ageTracker3 == null) ? ((float?)null) : ageTracker3.CurLifeStage?.bodySizeFactor);
		}
		float num3 = obj4 ?? 1f;
		Pawn obj5 = pawn;
		float num4 = ((obj5 == null) ? ((float?)null) : obj5.RaceProps?.baseBodySize) ?? 1f;
		float num5 = num3 * num4;
		float num6 = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_BodySizeOffset, true, -1) + num;
		float statValue = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_Cosmetic_BodySizeOffset, true, -1);
		float num7 = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_BodySizeMultiplier, true, -1) * num2;
		float statValue2 = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_Cosmetic_BodySizeMultiplier, true, -1);
		statValue += num6;
		float num8 = num7 + statValue2 - 1f;
		totalSizeOffset = (num4 + num6) * num7 * num3 - num5;
		float num9 = (num4 + statValue) * num8 * num3 - num5;
		totalSize = totalSizeOffset + num5;
		totalCosmeticSize = num9 + num5;
		if (!overrideLimits)
		{
			if ((int)dStage < 4)
			{
				totalSize = Mathf.Clamp(totalSize, 0.05f, 0.4f);
				totalSizeOffset = Mathf.Clamp(totalSizeOffset, 0.05f - num5, 0.4f - num5);
			}
			else if ((double)totalSize < 0.1)
			{
				totalSize = 0.1f;
				totalSizeOffset = 0.1f - num5;
			}
			if (totalSize < 0.05f && (int)dStage < 4)
			{
				totalSizeOffset = 0f - (num5 - 0.05f);
			}
			else if (totalSize > 0.4f && (int)dStage < 4 && pawn.RaceProps.Humanlike)
			{
				totalSizeOffset = 0f - (num5 - 0.4f);
			}
			else if (totalSize < 0.1f && (int)dStage == 4)
			{
				totalSizeOffset = 0f - (num5 - 0.1f);
			}
			else if (totalSize < 0.1f && (int)dStage > 4 && pawn.RaceProps.Humanlike)
			{
				totalSizeOffset = 0f - (num5 - 0.1f);
			}
		}
		else
		{
			totalSize = Mathf.Max(totalSize, 0.02f);
		}
		headSizeMultiplier = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.SM_HeadSize_Cosmetic, true, -1);
		scaleMultiplier = GetPercentChange(totalSizeOffset, pawn);
		cosmeticScaleMultiplier = GetPercentChange(num9, pawn);
		if (!pawn.RaceProps.Humanlike)
		{
			cosmeticScaleMultiplier.linear = Mathf.Sqrt(cosmeticScaleMultiplier.linear);
		}
		healthMultiplier = CalculateHealthMultiplier(scaleMultiplier, pawn);
		if (!healthMultiplier_previous.ApproximatelyEquals(healthMultiplier))
		{
			injuriesRescaled = false;
		}
		if (BSDefs.BS_MaxNutritionFromSize.Worker is StatWorker_MaxNutritionFromSize statWorker_MaxNutritionFromSize)
		{
			statWorker_MaxNutritionFromSize.SetTemporaryStatCache(pawn, scaleMultiplier.linear);
		}
	}

	private float CalculateHeadOffset(float headPosMultiplier)
	{
		float num = Mathf.Max(bodyRenderSize, headRenderSize);
		if (num < 1f)
		{
			num = Mathf.Pow(num, 0.96f);
		}
		float statValueAbstract = StatExtension.GetStatValueAbstract((BuildableDef)(object)((Thing)pawn).def, BSDefs.SM_Cosmetic_BodySizeMultiplier, (ThingDef)null);
		float num2 = StatExtension.GetStatValueAbstract((BuildableDef)(object)((Thing)pawn).def, BSDefs.SM_BodySizeMultiplier, (ThingDef)null) + statValueAbstract - 1f;
		if (preventHeadScaling || bodyConstantHeadScale || (bodyConstantHeadScaleBigOnly && bodyRenderSize + 0.001f > num2))
		{
			float num3 = bodyRenderSize;
			num3 *= headPosMultiplier;
			return Mathf.Lerp(num, num3, preventHeadOffsetFactor);
		}
		return num;
	}

	private void SetWorldOffset()
	{
		float num = bodyRenderSize;
		float num2 = num;
		if (num < 1f)
		{
			num = 1f;
		}
		float num3 = bodyPosOffset;
		float num4 = 1f;
		if (pawn.story?.bodyType != null)
		{
			BodyTypeDef bodyType = pawn.story.bodyType;
			num4 = bodyType.bodyGraphicScale.y;
			if (bodyType == BodyTypeDefOf.Hulk)
			{
				num3 += 0.25f;
			}
		}
		worldspaceOffset = (num - 1f) / 2f * (num3 + 1f) + num3 * 0.3f * ((num2 < 1f) ? num2 : 1f) * num4;
	}

	private static PercentChange GetPercentChange(float bodySizeOffset, Pawn pawn)
	{
		if (pawn != null && bodySizeOffset != 0f && (pawn.needs != null || pawn.Dead))
		{
			float bodySizeFactor = pawn.ageTracker.CurLifeStage.bodySizeFactor;
			float num = ((pawn == null) ? ((float?)null) : pawn.RaceProps?.baseBodySize) ?? 1f;
			float num2 = bodySizeFactor * num;
			float num3 = num2 + bodySizeOffset;
			float num4 = num3 / num2;
			float num5 = Mathf.Pow(num3, 2f) / Mathf.Pow(num2, 2f);
			float num6 = Mathf.Pow(num3, 3f) / Mathf.Pow(num2, 3f);
			num4 = Mathf.Max(num4, 0.04f);
			num5 = Mathf.Max(num5, 0.04f);
			num6 = Mathf.Max(num6, 0.04f);
			if (num4 < 0.2f)
			{
				num4 = 0.2f;
			}
			return new PercentChange(num4, num5, num6);
		}
		return new PercentChange(1f, 1f, 1f);
	}

	public float GetHeadRenderSize()
	{
		float num = GetBodyRenderSize();
		float num2 = 1f;
		if (pawn.story != null && BigSmallMod.settings.scaleBodyTypes)
		{
			if (pawn.story.bodyType == BodyTypeDefOf.Hulk)
			{
				num2 = hulkSize;
			}
			else if (pawn.story.bodyType == BodyTypeDefOf.Fat)
			{
				num2 = fatSize;
			}
			else if (pawn.story.bodyType == BodyTypeDefOf.Thin)
			{
				num2 = thinSize;
			}
			num *= 1f / num2;
		}
		float num3 = num;
		if (num3 > 1f)
		{
			num3 = Mathf.Pow(num, BigSmallMod.settings.headPowLarge);
			num3 = Math.Max(num - 0.5f, num3);
		}
		else
		{
			num3 = Mathf.Pow(num, BigSmallMod.settings.headPowSmall);
		}
		num3 *= headSizeMultiplier;
		if (preventHeadScaling || bodyConstantHeadScale || (bodyConstantHeadScaleBigOnly && num > 1f))
		{
			float num4 = (preventHeadScaling ? num : (num * headSizeMultiplier));
			return Mathf.Lerp(num3, num4, preventHeadScalingFactor);
		}
		return num3;
	}

	public float GetBodyRenderSize()
	{
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Invalid comparison between Unknown and I4
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Invalid comparison between Unknown and I4
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Invalid comparison between Unknown and I4
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Invalid comparison between Unknown and I4
		float num = cosmeticScaleMultiplier.linear;
		if (num != 1f)
		{
			if (num < 1f)
			{
				if (!hasSizeAffliction)
				{
					num = (((int)pawn.DevelopmentalStage < 4) ? Mathf.Pow(num, 0.95f) : (((int)pawn.DevelopmentalStage >= 8) ? Mathf.Pow(num, 0.75f) : Mathf.Pow(num, 0.9f)));
				}
				num *= BigSmallMod.settings.visualSmallerMult;
			}
			else
			{
				num = (((int)pawn.DevelopmentalStage < 4) ? Mathf.Pow(num, 0.4f) : (((int)pawn.DevelopmentalStage >= 8) ? Mathf.Pow(num, 0.7f) : Mathf.Pow(num, 0.5f)));
				num = (num - 1f) * BigSmallMod.settings.visualLargerMult + 1f;
			}
		}
		if (pawn.story != null && BigSmallMod.settings.scaleBodyTypes)
		{
			if (pawn.story.bodyType == BodyTypeDefOf.Hulk)
			{
				num *= hulkSize;
			}
			else if (pawn.story.bodyType == BodyTypeDefOf.Fat)
			{
				num *= fatSize;
			}
			else if (pawn.story.bodyType == BodyTypeDefOf.Thin)
			{
				num *= thinSize;
			}
		}
		return num;
	}

	private static float CalculateHealthMultiplier(PercentChange scalMult, Pawn pawn)
	{
		if (scalMult.linear <= 1f)
		{
			return scalMult.linear;
		}
		float linear = scalMult.linear;
		float num = 4f;
		float num2 = pawn.RaceProps?.baseHealthScale ?? 1f;
		float num3 = pawn.RaceProps?.baseBodySize ?? 1f;
		float num4 = num2 / num3;
		float num5 = Mathf.Max(4f, num4);
		float num6 = num3;
		float? obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_AgeTracker ageTracker = pawn.ageTracker;
			obj = ((ageTracker == null) ? ((float?)null) : ageTracker.CurLifeStage?.bodySizeFactor);
		}
		float num7 = (num6 * obj) ?? 1f;
		float num8 = Mathf.Clamp01((linear * num7 - num7) / num);
		float num9 = Mathf.SmoothStep(num4, num5, num8);
		float num10 = Mathf.Lerp(num4, num5, num8);
		float num11 = Mathf.Lerp(num9, num10, 0.5f) / num4;
		return linear * num11;
	}
}
