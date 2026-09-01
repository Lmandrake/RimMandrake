using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class PawnExtension : SmartExtension
{
	public record struct TraitDegreeData(TraitDef Def, int Degree);

	[CompilerGenerated]
	private sealed class _003CGetForcedTraits_003Ed__171 : IEnumerable<TraitDegreeData>, IEnumerable, IEnumerator<TraitDegreeData>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private TraitDegreeData _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public PawnExtension _003C_003E4__this;

		private List<TraitDef>.Enumerator _003C_003E7__wrap1;

		private List<GeneticTraitData>.Enumerator _003C_003E7__wrap2;

		TraitDegreeData IEnumerator<TraitDegreeData>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CGetForcedTraits_003Ed__171(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			switch (_003C_003E1__state)
			{
			case -3:
			case 1:
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
				break;
			case -4:
			case 2:
				try
				{
				}
				finally
				{
					_003C_003Em__Finally2();
				}
				break;
			}
			_003C_003E7__wrap1 = default(List<TraitDef>.Enumerator);
			_003C_003E7__wrap2 = default(List<GeneticTraitData>.Enumerator);
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			try
			{
				int num = _003C_003E1__state;
				PawnExtension pawnExtension = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E7__wrap1 = pawnExtension.forcedTraits.GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_0078;
				case 1:
					_003C_003E1__state = -3;
					goto IL_0078;
				case 2:
					{
						_003C_003E1__state = -4;
						break;
					}
					IL_0078:
					if (_003C_003E7__wrap1.MoveNext())
					{
						TraitDef current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = new TraitDegreeData(current, 0);
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = default(List<TraitDef>.Enumerator);
					_003C_003E7__wrap2 = pawnExtension.forcedTraitDegrees.GetEnumerator();
					_003C_003E1__state = -4;
					break;
				}
				if (_003C_003E7__wrap2.MoveNext())
				{
					GeneticTraitData current2 = _003C_003E7__wrap2.Current;
					_003C_003E2__current = new TraitDegreeData(current2.def, current2.degree);
					_003C_003E1__state = 2;
					return true;
				}
				_003C_003Em__Finally2();
				_003C_003E7__wrap2 = default(List<GeneticTraitData>.Enumerator);
				return false;
			}
			catch
			{
				//try-fault
				((IDisposable)this).Dispose();
				throw;
			}
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		private void _003C_003Em__Finally1()
		{
			_003C_003E1__state = -1;
			((IDisposable)_003C_003E7__wrap1/*cast due to .constrained prefix*/).Dispose();
		}

		private void _003C_003Em__Finally2()
		{
			_003C_003E1__state = -1;
			((IDisposable)_003C_003E7__wrap2/*cast due to .constrained prefix*/).Dispose();
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<TraitDegreeData> IEnumerable<TraitDegreeData>.GetEnumerator()
		{
			_003CGetForcedTraits_003Ed__171 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CGetForcedTraits_003Ed__171(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<TraitDegreeData>)this).GetEnumerator();
		}
	}

	public static PawnExtension defaultPawnExtension = new PawnExtension();

	public RacialFeature featureInfo;

	public string traitIcon;

	/// <summary>
	/// The order in which this extension is applied.
	/// Higher numbers are applied later, which means they can in some cases overwrite earlier extensions.
	/// </summary>
	public int priority = int.MinValue;

	/// <summary>
	/// Exclusion tags makes this PawnExtension disable all PawnExtensions of a lower priority and sharing any tag.
	/// </summary>
	public List<string> exclusionTags;

	/// <summary>
	/// Tags which can be used for checks, filtering, etc.
	/// </summary>
	public List<string> tags;

	/// <summary>
	/// If used it will display them in UI as one entry when used with racialFeatureData.
	/// </summary>
	public string fuseTag;

	public bool frequentUpdate;

	public bool hideInGenePicker;

	public bool hideInXenotypeUI;

	/// <summary>
	/// Used by Genes. If it evaluates to False the gene will disable itself.
	/// Useful for werewolf-like beaviour, or genes that deactivate if not drunk or something.
	/// </summary>
	public List<ConditionalStatAffecter> conditionals;

	/// <summary>
	/// Used by the above. Inverts the conditional
	/// </summary>
	public bool? invert;

	/// <summary>
	/// Turns off the zoomed-out render cache for the pawn. Useful if your pawn graphics might otherwise get cut off.
	/// </summary>
	public bool renderCacheOff;

	public List<RacialFeatureDef> racialFeatures;

	private bool checkedRacialFeatures;

	[CompilerGenerated]
	private List<RacialFeatureDef> _003CRacialFeaturesWithAuto_003Ek__BackingField;

	/// <summary>
	/// Used by Genes. When the gene is added/activated it will apply these hediffs to the pawn.
	/// </summary>
	public List<HediffToBody> applyBodyHediff;

	/// <summary>
	/// Same as above but applies to specific bodyparts.
	/// </summary>
	public List<HediffToBodyparts> applyPartHediff;

	/// <summary>
	/// This is the magic thing that makes the pawn swap to a different ThingDef. E.g. "Race".
	/// </summary>
	public ThingDef thingDefSwap;

	/// <summary>
	/// Forces the swap to the ThingDef. If false, it will be cautious to avoid accidentally turning robots into
	/// biological snake-people, etc. If in doubt, leave this as false.
	/// </summary>
	public bool forceThingDefSwap;

	/// <summary>
	/// Used by Genes. A bit of a miseleading name.
	/// The listed genes will be added to the pawn when this gene is added.
	/// When removed the genes will be removed as well.
	///
	/// It was originally used to make genes with multiple sets of graphics, but it can be used nowadays to "bundle" genes.
	/// </summary>
	[Obsolete("Will be renamed in 1.7")]
	public List<GeneDef> hiddenGenes = new List<GeneDef>();

	/// <summary>
	/// All the listed thoughts will be nulled.
	///
	/// It is suggested to not add too many of these to a gene since they WILL show in the tooltip. Hediffs don't have this issue.
	/// </summary>
	public List<ThoughtDef> nullsThoughts;

	/// <summary>
	/// Sets what apparel the pawn can wear. Check in the class for more details.
	/// </summary>
	public ApparelRestrictions apparelRestrictions;

	public bool? canWieldThings;

	/// <summary>
	/// If found on an animal's raceTracker it will be considered to have fine-manipulation ability.
	/// E.g. able to use guns. Highest value will be used. E.g. a bionic with 1.0 will make the pawn always avoid penalties.
	/// </summary>
	public float? animalFineManipulation;

	public float animalFineManipulationOffset;

	/// <summary>
	/// Transforms the pawn into a specific xenotype under some conditions.
	/// Currently used by the hidden Grigori gene to trigger potential Nephilim transformation in hybrid kids.
	/// </summary>
	public TransformationGene transformGene;

	/// <summary>
	/// Applies a size curve to the age of the pawn. Can be used to change how big they are at different ages.
	/// </summary>
	public SimpleCurve sizeByAge;

	/// <summary>
	/// Same as above, but multiplies the size by the curve.
	/// </summary>
	public SimpleCurve sizeByAgeMult;

	/// <summary>
	/// Works about the same as Rimworld's aptitudes. Let's you add skill-offsets to genes/hediffs/races.
	/// </summary>
	public List<Aptitude> aptitudes;

	public bool disableSkillsWithMinus20Aptitude;

	public List<Aptitude> disableSkillBelowAptitude;

	public List<SkillRange> clampedSkills;

	public bool canHavePassions = true;

	public List<WorkTypeDef> disabledWorkTypes = new List<WorkTypeDef>();

	/// <summary>
	/// Makes the pawn consider the pawn female for rendering purposes.
	/// Useful for compatibility. Despite the name, it also affects the head.
	/// </summary>
	public Gender? forceGender;

	protected bool forceFemaleBody;

	public bool ignoreForceGender;

	/// <summary>
	/// Set what the pawn can eat. By default assumes human diet.
	/// </summary>
	public PawnDiet pawnDiet;

	/// <summary>
	/// If true this will let the pawn use electric chargers.
	/// </summary>
	public bool canUseChargers;

	/// <summary>
	/// If true this will make the race's "PawnDiet" be ignored in favor of other diets.
	///
	/// </summary>
	public bool pawnDietRacialOverride;

	public float? internalDamageDivisor = 1f;

	/// Stats
	public float soulFalloffStart;

	public float siphonFactorOffset;

	public float siphonSkillFactorOffset;

	/// <summary>
	/// Trigger the soul-consume effect on hit.
	/// </summary>
	public SiphonSoul siphonSoul;

	public RomanceTags romanceTags;

	public bool disableLookChangeDesired;

	public bool partsCanBeHarvested = true;

	public float? bleedRate;

	public bool preventDisfigurement;

	/// <summary>
	/// Lets the pawn walk on VFE's creep. Only works on genes.
	/// </summary>
	public bool canWalkOnCreep;

	/// <summary>
	/// Can hold melee weapons, but will only use natural/bionic attacks.
	/// </summary>
	public bool forceUnarmed;

	[Obsolete("Use forceUnarmed instead.")]
	public bool unarmedOnly;

	/// <summary>
	/// If set the pawn will be butchered for this meat instead of the default.
	/// </summary>
	public ThingDef meatOverride;

	/// <summary>
	/// If set the following extra products will be created when the pawn is butchered.
	/// </summary>
	public List<CustomButcherProduct> butcherProducts;

	/// <summary>
	/// If set to true the pawn will default to blocking additctions unless white/allowlisted.
	/// </summary>
	public bool banAddictionsByDefault;

	/// <summary>
	/// Pawn will be considered...
	/// </summary>
	public bool isUnliving;

	public bool isDeathlike;

	public bool isMechanical;

	public bool isBloodfeeder;

	public bool isAmorphous;

	/// <summary>
	/// Makes colonists care less about the pawn's death, and the pawn care less about death in general.
	/// </summary>
	public bool isDrone;

	public bool noFamilyRelations;

	public bool? empVulnerable;

	/// <summary>
	/// Lock a Needbar at a certain level. Often more compatible than just removing them.
	/// </summary>
	public List<LockedNeedClass> lockedNeeds;

	/// <summary>
	/// Filters (removes) based on filtering settings
	/// </summary>
	public FilterListSet<GeneDef> geneFilters;

	public FilterListSet<GeneCategoryDef> geneCategoryFilters;

	public FilterListSet<string> geneTagFilters;

	/// <summary>
	/// These filters don't remove the gene, but simply block it from being activated.
	/// </summary>
	public FilterListSet<GeneDef> activeGeneFilters;

	public FilterListSet<GeneCategoryDef> activeGeneCategoryFilters;

	public FilterListSet<string> activeGeneTagFilters;

	public FilterListSet<TraitDef> traitFilters;

	public FilterListSet<HediffDef> hediffFilters;

	public FilterListSet<HairDef> hairFilters;

	public FilterListSet<RecipeDef> surgeryRecipes;

	/// <summary>
	/// How many babies the pawn will give birth to. If null, it will use normal counts.
	/// Note that this is better than the vanilla options since it will re-randomize the gene list for each additional
	/// baby instead of making them clones.
	/// </summary>
	public List<int> babyBirthCount;

	/// <summary>
	/// What "practical" age the baby born at. Creatures that give birth to less helpless offspring may want to start at 3.
	/// Insects that are born fully formed could start at 10, 13, or even 20.
	/// Consider combining with sizeByAgeMult to make the babies a plausible size.
	/// </summary>
	public int? babyStartAge;

	/// <summary>
	/// How fast pregnancy progresses. 1 is normal, 0.5 is half speed, 2 is double speed.
	/// </summary>
	public float pregnancySpeedMultiplier = 1f;

	/// <summary>
	/// Added to pregnancy quality. If sum is above 0.5 (from all sources) then pregnancy outcome index will be set to a minimum of 0.
	/// </summary>
	public float pregnancyQuality;

	/// <summary>
	/// Modifies the pawn if the <see cref="F:BigAndSmall.PawnExtension.morphSettings" /> requirements are met
	/// </summary>
	public List<MorphTarget> morphTargets = new List<MorphTarget>();

	/// <summary>
	/// Requirements to attempt to morph to the <see cref="F:BigAndSmall.PawnExtension.morphTargets" />
	/// </summary>
	public MorphSettings morphSettings;

	/// <summary>
	/// Trigger Metamorph at this age.
	/// </summary>
	[Obsolete("Use morphSettings instead.")]
	public int? metamorphAtAge;

	/// <summary>
	/// Trigger Retromorph if less than this age.
	/// </summary>
	[Obsolete("Use morphSettings instead.")]
	public int? retromorphUnderAge;

	[Obsolete("Use morphSettings instead.")]
	public bool metamorphIfPregnant;

	[Obsolete("Use morphSettings instead.")]
	public bool metamorphIfNight;

	[Obsolete("Use morphSettings instead.")]
	public bool metamorphIfDay;

	/// <summary>
	/// Sets a custom material for the body. Highly versatile.
	/// </summary>
	public CustomMaterial bodyMaterial;

	/// <summary>
	/// Sets a custom material for the head. Highly versatile.
	/// </summary>
	public CustomMaterial headMaterial;

	/// <summary>
	/// Sets the path(s) of the body. Can be per body type, gender, etc.
	/// You can for example set a list of paths to be used by male hulks only.
	/// </summary>
	public AdaptivePathList bodyPaths = new AdaptivePathList();

	public AdaptivePathList bodyDessicatedPaths = new AdaptivePathList();

	public BodyTypesPerGender bodyTypes = new BodyTypesPerGender();

	public bool removeTattoos;

	public RotDrawMode? forcedRotDrawMode;

	/// <summary>
	/// Same as above.
	/// </summary>
	public AdaptivePathList headPaths = new AdaptivePathList();

	public AdaptivePathList headDessicatedPaths = new AdaptivePathList();

	/// <summary>
	/// Offsets the entire pawn's body up or down.
	/// </summary>
	public float bodyPosOffset;

	/// <summary>
	/// Offsets the head up or down relative to the body.
	/// </summary>
	public float headPosMultiplier;

	public bool hideBody;

	public bool hideHead;

	/// <summary>
	/// Prevents head-scaling/offsets from sources other than the pawn's general size.
	/// </summary>
	public bool preventHeadScaling;

	/// <summary>
	/// Prevents auto-scaling the pawn's head from changing body-size sources other than explicit headscale.
	/// This means large pawns won't get slightly smaller heads, and small ones won't get a chibi-head.
	///
	/// Basically just a more specific version of the above.
	/// </summary>
	public bool bodyConstantHeadScale;

	/// <summary>
	/// Exactly the same as the above, but permits big head if the body is small.
	/// </summary>
	public bool bodyConstantHeadScaleBigOnly;

	/// <summary>
	/// If specified, instead of blocking scale it will be reduced by this factor.
	/// </summary>
	public float? preventHeadScalingFactor;

	public float? preventHeadOffsetFactor;

	/// <summary>
	/// If set this lets you disabe a renderNode type on the pawn.
	/// </summary>
	public bool hideHumanlikeRenderNodes;

	protected Gender? apparentGender;

	public bool invertApparentGender;

	/// <summary>
	/// Only the basic offsets will be respected at the moment. Supporting all is a performance hit.
	/// </summary>
	public BSDrawData bodyDrawData;

	public BSDrawData headDrawData;

	/// <summary>
	/// Disable Nal's facial animations on the pawn and restore their original head.
	/// </summary>
	public bool disableFacialAnimations;

	/// <summary>
	/// More granular version of the above. Currently not working after a Nal's update.
	/// </summary>
	public FacialAnimDisabler facialDisabler;

	/// <summary>
	/// Force-adds these hediffs. Removes when race is removed.
	/// </summary>
	public List<HediffDef> forcedHediffs = new List<HediffDef>();

	/// <summary>
	/// Force-adds these traits.
	/// </summary>
	public List<TraitDef> forcedTraits = new List<TraitDef>();

	public List<GeneticTraitData> forcedTraitDegrees = new List<GeneticTraitData>();

	public List<TraitDef> traitsDependentOnRace = new List<TraitDef>();

	/// <summary>
	/// Adds endogenes to the pawn. Ensures they are always present.
	/// </summary>
	public List<GeneDef> forcedEndogenes;

	/// <summary>
	/// Same as above, but also removes anything that would overwrite them
	/// </summary>
	public List<GeneDef> immutableEndogenes;

	/// <summary>
	/// Adds xenogenes to the pawn. Ensures they are always present.
	/// </summary>
	public List<GeneDef> forcedXenogenes;

	public List<GeneDef> genesDependentOnRace = new List<GeneDef>();

	/// <summary>
	/// These are just for generating pawns. They are most useful on custom races, not on genes/hediffs.
	/// Don't forget that the RaceHediff also inherits the props from "CompProperties_ColorAndFur" which could be used instead.
	///
	/// Should work even without biotech
	/// </summary>;
	public List<GeneDef> randomSkinGenes;

	public List<GeneDef> randomHairGenes;

	private Dictionary<GeneDef, FilterResult> _blocked = new Dictionary<GeneDef, FilterResult>();

	public string ConditionalDescription
	{
		get
		{
			List<ConditionalStatAffecter> list = conditionals;
			if (list == null)
			{
				return null;
			}
			return GenText.ToLineList(list.Select(delegate(ConditionalStatAffecter x)
			{
				string label = x.Label;
				List<StatModifier> statFactors = x.statFactors;
				string obj = ((statFactors != null) ? GenText.ToLineList(statFactors.Select((StatModifier y) => ((object)y).ToString()), "  - ", true) : null);
				List<StatModifier> statOffsets = x.statOffsets;
				return label + ":\n" + obj + ((statOffsets != null) ? GenText.ToLineList(statOffsets.Select((StatModifier y) => ((object)y).ToString()), "  - ", true) : null);
			}), (string)null, false);
		}
	}

	public List<RacialFeatureDef> RacialFeaturesWithAuto
	{
		get
		{
			if (checkedRacialFeatures)
			{
				return _003CRacialFeaturesWithAuto_003Ek__BackingField;
			}
			List<RacialFeatureDef> list = new List<RacialFeatureDef>();
			if (isMechanical)
			{
				list.Add(BSDefs.BS_Mechanical);
			}
			if (isDrone)
			{
				list.Add(DefDatabase<RacialFeatureDef>.GetNamedSilentFail("BS_Drone"));
			}
			if (isUnliving)
			{
				list.Add(DefDatabase<RacialFeatureDef>.GetNamedSilentFail("BS_Unliving"));
			}
			if (noFamilyRelations)
			{
				list.Add(DefDatabase<RacialFeatureDef>.GetNamedSilentFail("BS_NoFamilyRelations"));
			}
			if (isAmorphous)
			{
				list.Add(DefDatabase<RacialFeatureDef>.GetNamedSilentFail("BS_Amorphous"));
			}
			if (racialFeatures != null)
			{
				list.AddRange(racialFeatures);
			}
			list = list.Where((RacialFeatureDef x) => x != null).ToList();
			if (list.Count == 0)
			{
				list = null;
			}
			checkedRacialFeatures = true;
			return _003CRacialFeaturesWithAuto_003Ek__BackingField = list;
		}
	}

	public List<TaggedString> RacialFeaturesDescription => RacialFeaturesWithAuto?.Select((RacialFeatureDef x) => ((Def)x).LabelCap).ToList();

	public List<string> ApplyBodyHediffDescription => applyBodyHediff?.Where((HediffToBody x) => x.conditionals == null && x.prerequisiteSets == null)?.Select((HediffToBody x) => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ApplyBodyHediff", NamedArgument.op_Implicit(((Def)x.hediff).LabelCap)))).ToList();

	public List<string> ApplyPartHediffDescription => applyPartHediff?.Where((HediffToBodyparts x) => x.conditionals == null && x.prerequisiteSets == null)?.Select((HediffToBodyparts x) => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ApplyPartHediff", NamedArgument.op_Implicit(((Def)x.hediff).LabelCap), NamedArgument.op_Implicit(string.Join(", ", x.bodyparts))))).ToList();

	public string ThingDefSwapDescription
	{
		get
		{
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val2;
			if (thingDefSwap != null)
			{
				TaggedString val = TranslatorFormattedStringExtensions.Translate("BS_ThingDefSwapDesc", NamedArgument.op_Implicit(((Def)thingDefSwap).LabelCap));
				val2 = ((TaggedString)(ref val)).CapitalizeFirst();
			}
			else
			{
				val2 = TaggedString.op_Implicit((string)null);
			}
			return TaggedString.op_Implicit(val2);
		}
	}

	public string SizeByAgeDescription
	{
		get
		{
			SimpleCurve obj = sizeByAge;
			if (obj == null)
			{
				return null;
			}
			return GenText.ToLineList(((IEnumerable<CurvePoint>)obj).Select(delegate(CurvePoint pt)
			{
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				TaggedString val = TranslatorFormattedStringExtensions.Translate("PeriodYears", NamedArgument.op_Implicit(((CurvePoint)(ref pt)).x));
				return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString() + ": +" + ((CurvePoint)(ref pt)).y;
			}), "  - ", true);
		}
	}

	public string SizeByAgeMultDescription
	{
		get
		{
			SimpleCurve obj = sizeByAgeMult;
			if (obj == null)
			{
				return null;
			}
			return GenText.ToLineList(((IEnumerable<CurvePoint>)obj).Select(delegate(CurvePoint pt)
			{
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				//IL_0016: Unknown result type (might be due to invalid IL or missing references)
				TaggedString val = TranslatorFormattedStringExtensions.Translate("PeriodYears", NamedArgument.op_Implicit(((CurvePoint)(ref pt)).x));
				return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString() + ": x" + ((CurvePoint)(ref pt)).y;
			}), "  - ", true);
		}
	}

	public List<string> AptitudeDescription => aptitudes?.Select(delegate(Aptitude x)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		TaggedString labelCap = ((Def)x.skill).LabelCap;
		return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString() + " " + GenText.ToStringWithSign(x.level);
	}).ToList();

	public List<string> DisableSkillBelowAptitudeDescription => disableSkillBelowAptitude?.Select(delegate(Aptitude x)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		TaggedString labelCap = ((Def)x.skill).LabelCap;
		return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString() + " " + GenText.ToStringWithSign(x.level);
	}).ToList();

	public List<string> LearnedSkillRangesDescription => clampedSkills?.Select((SkillRange x) => $"{((Def)x.Skill).LabelCap} {x.Range}").ToList();

	public List<string> DisabledWorkTypeDescription => disabledWorkTypes?.Select((WorkTypeDef x) => GenText.CapitalizeFirst(x.gerundLabel)).ToList();

	public string PawnDietDescription
	{
		get
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			PawnDiet obj = pawnDiet;
			TaggedString? val = ((obj != null) ? new TaggedString?(((Def)obj).LabelCap) : ((TaggedString?)null));
			if (!val.HasValue)
			{
				return null;
			}
			return TaggedString.op_Implicit(val.GetValueOrDefault());
		}
	}

	public string SoulPowerFalloffStartDescription => TaggedString.op_Implicit((soulFalloffStart == 0f) ? TaggedString.op_Implicit((string)null) : TranslatorFormattedStringExtensions.Translate("BS_SoulPowerFalloffDesc", NamedArgument.op_Implicit(GenText.ToStringPercentSigned(soulFalloffStart))));

	public string SiphonSoulOffsetStartDescription => TaggedString.op_Implicit((siphonFactorOffset == 0f) ? TaggedString.op_Implicit((string)null) : TranslatorFormattedStringExtensions.Translate("BS_SiphonSoulOffsetDesc", NamedArgument.op_Implicit(GenText.ToStringPercentSigned(siphonFactorOffset))));

	public string SiphonSkillOffsetStartDescription => TaggedString.op_Implicit((siphonSkillFactorOffset == 0f) ? TaggedString.op_Implicit((string)null) : TranslatorFormattedStringExtensions.Translate("BS_SiphonSkillOffsetDesc", NamedArgument.op_Implicit(GenText.ToStringPercentSigned(siphonSkillFactorOffset))));

	public string SoulSiphonDescription
	{
		get
		{
			if (!(siphonSoul == null))
			{
				return siphonSoul.SiphonSoulDescription;
			}
			return null;
		}
	}

	public List<string> StatChangeDescriptions => new List<string> { SoulPowerFalloffStartDescription, SiphonSoulOffsetStartDescription, SiphonSkillOffsetStartDescription }.Where((string x) => x != null).ToList();

	public List<string> RomanceTagsDescription => romanceTags?.GetDescriptions();

	public string BleedRateDescription => TaggedString.op_Implicit((!bleedRate.HasValue) ? TaggedString.op_Implicit((string)null) : TranslatorFormattedStringExtensions.Translate("BS_BleedRateDesc", NamedArgument.op_Implicit(GenText.ToStringPercent(bleedRate.Value))));

	public string PreventDisfigurementDescription => TaggedString.op_Implicit(preventDisfigurement ? Translator.Translate("BS_PreventDisfigurementDesc") : TaggedString.op_Implicit((string)null));

	public string CanWalkOnCreepDescription => TaggedString.op_Implicit(canWalkOnCreep ? Translator.Translate("BS_CanWalkOnCreepDesc") : TaggedString.op_Implicit((string)null));

	public string ForceUnarmedDescription => TaggedString.op_Implicit(forceUnarmed ? Translator.Translate("BS_ForceUnarmedDesc") : TaggedString.op_Implicit((string)null));

	public string LockedNeedsDescription
	{
		get
		{
			List<LockedNeedClass> list = lockedNeeds;
			if (list == null)
			{
				return null;
			}
			IEnumerable<string> enumerable = from x in list
				where x != null && x.GetLabel() != ""
				select x.GetLabel();
			if (enumerable == null)
			{
				return null;
			}
			return GenText.ToLineList(enumerable, "  - ", true);
		}
	}

	public Gender? ApparentGender
	{
		get
		{
			if (!forceFemaleBody)
			{
				return apparentGender;
			}
			return (Gender)2;
		}
	}

	public List<string> RaceForcedHediffsDesc
	{
		get
		{
			if (!GenList.NullOrEmpty<HediffDef>((IList<HediffDef>)forcedHediffs))
			{
				return forcedHediffs?.Select((HediffDef x) => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ApplyBodyHediff", NamedArgument.op_Implicit(((Def)x).LabelCap)))).ToList();
			}
			return null;
		}
	}

	public string NoFamilyRelationsDescription => TaggedString.op_Implicit(noFamilyRelations ? Translator.Translate("BS_NoFamilyRelationsDesc") : TaggedString.op_Implicit((string)null));

	public string DroneDescription => TaggedString.op_Implicit(isDrone ? Translator.Translate("BS_DroneDesc") : TaggedString.op_Implicit((string)null));

	private string UnlivingDescription => TaggedString.op_Implicit(isUnliving ? Translator.Translate("BS_UnlivingDesc") : TaggedString.op_Implicit((string)null));

	private string DeathlikeDescription => TaggedString.op_Implicit(isDeathlike ? Translator.Translate("BS_DeathlikeDesc") : TaggedString.op_Implicit((string)null));

	private string MechanicalDescription => TaggedString.op_Implicit(isMechanical ? Translator.Translate("BS_MechanicalDesc") : TaggedString.op_Implicit((string)null));

	private string BloodfeederDescription => TaggedString.op_Implicit(isBloodfeeder ? Translator.Translate("BS_BloodfeederDesc") : TaggedString.op_Implicit((string)null));

	private string AmorphousDescription => TaggedString.op_Implicit(isAmorphous ? Translator.Translate("BS_AmorphousDesc") : TaggedString.op_Implicit((string)null));

	public List<string> TagDescriptions => new List<string> { UnlivingDescription, DeathlikeDescription, MechanicalDescription, BloodfeederDescription, AmorphousDescription, DroneDescription }.Where((string x) => x != null).ToList();

	/// <summary>
	/// Returns true if frequent update is true in xml, time-based morphing, locked needs, conditional genes or active gene filters.
	/// </summary>
	public bool FrequentUpdate
	{
		get
		{
			if (!frequentUpdate)
			{
				MorphSettings obj = morphSettings;
				if ((obj == null || !obj.RequiresFrequentChecks) && !HasActiveGeneFilters && GenList.NullOrEmpty<LockedNeedClass>((IList<LockedNeedClass>)lockedNeeds))
				{
					return !GenList.NullOrEmpty<ConditionalStatAffecter>((IList<ConditionalStatAffecter>)conditionals);
				}
			}
			return true;
		}
	}

	public bool HasActiveGeneFilters
	{
		get
		{
			if (activeGeneFilters == null && activeGeneCategoryFilters == null)
			{
				return activeGeneTagFilters != null;
			}
			return true;
		}
	}

	public bool HasGeneRemovalFilters
	{
		get
		{
			if (geneFilters == null && geneCategoryFilters == null)
			{
				return geneTagFilters != null;
			}
			return true;
		}
	}

	public bool HasGeneFilters
	{
		get
		{
			if (!HasGeneRemovalFilters)
			{
				return HasActiveGeneFilters;
			}
			return true;
		}
	}

	public List<GeneDef> ForcedEndogenes
	{
		get
		{
			List<GeneDef> list = forcedEndogenes ?? new List<GeneDef>();
			List<GeneDef> list2 = immutableEndogenes ?? new List<GeneDef>();
			List<GeneDef> list3 = new List<GeneDef>(list.Count + list2.Count);
			list3.AddRange(list);
			list3.AddRange(list2);
			return list3;
		}
	}

	public List<GeneDef> ForcedXenogenes => forcedXenogenes ?? new List<GeneDef>();

	public List<GeneDef> AllForcedGenes
	{
		get
		{
			List<GeneDef> list = ForcedEndogenes;
			List<GeneDef> list2 = ForcedXenogenes;
			List<GeneDef> list3 = new List<GeneDef>(list.Count + list2.Count);
			list3.AddRange(list);
			list3.AddRange(list2);
			return list3;
		}
	}

	public void UpdateLegacy()
	{
		UpdateLegacyMorph();
	}

	private bool AnyLegacyMetamorphConditions()
	{
		if (!metamorphAtAge.HasValue && !metamorphIfPregnant && !metamorphIfNight)
		{
			return metamorphIfDay;
		}
		return true;
	}

	public void UpdateLegacyMorph()
	{
		if (AnyLegacyMetamorphConditions() && morphSettings == null)
		{
			morphSettings = new MorphSettings
			{
				morphOverAge = metamorphAtAge,
				morphUnderAge = retromorphUnderAge,
				morphIfPregnant = metamorphIfPregnant,
				morphIfNight = metamorphIfNight,
				morphIfDay = metamorphIfDay
			};
		}
		if (retromorphUnderAge.HasValue && morphSettings == null)
		{
			morphSettings = new MorphSettings
			{
				isRetromorph = true,
				morphUnderAge = retromorphUnderAge
			};
		}
	}

	[IteratorStateMachine(typeof(_003CGetForcedTraits_003Ed__171))]
	public IEnumerable<TraitDegreeData> GetForcedTraits()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetForcedTraits_003Ed__171(-2)
		{
			_003C_003E4__this = this
		};
	}

	public float GetSizeFromSizeByAge(float? age)
	{
		if (sizeByAge == null || !age.HasValue)
		{
			return 0f;
		}
		return sizeByAge.Evaluate(age.Value);
	}

	public float GetSizeMultiplierFromSizeByAge(float? age)
	{
		if (sizeByAgeMult == null || !age.HasValue)
		{
			return 1f;
		}
		if (!age.HasValue)
		{
			return 1f;
		}
		return sizeByAgeMult.Evaluate(age.Value);
	}

	public bool RequiresCacheRefresh()
	{
		return aptitudes != null;
	}

	public StringBuilder GetAllEffectorDescriptions()
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		if (applyBodyHediff != null)
		{
			foreach (HediffToBody item in applyBodyHediff)
			{
				if (item.conditionals == null || item.hediff == null)
				{
					continue;
				}
				string text = ((Def)item.hediff).label ?? ((Def)item.hediff).defName;
				stringBuilder.AppendLine();
				stringBuilder.AppendLine(ColoredText.Colorize(string.Format("\"{0}\" {1}:", GenText.CapitalizeFirst(text), Translator.Translate("BS_ActiveIf")), ColoredText.TipSectionTitleColor));
				foreach (ConditionalStatAffecter conditional in item.conditionals)
				{
					stringBuilder.AppendLine("  - " + conditional.Label);
				}
			}
		}
		if (applyPartHediff != null)
		{
			foreach (HediffToBodyparts item2 in applyPartHediff)
			{
				if (item2.conditionals == null || item2.hediff == null)
				{
					continue;
				}
				string text2 = ((Def)item2.hediff).label ?? ((Def)item2.hediff).defName;
				stringBuilder.AppendLine();
				stringBuilder.AppendLine(ColoredText.Colorize(string.Format("\"{0}\" {1}:", GenText.CapitalizeFirst(text2), Translator.Translate("BS_ActiveIf")), ColoredText.TipSectionTitleColor));
				foreach (ConditionalStatAffecter conditional2 in item2.conditionals)
				{
					stringBuilder.AppendLine("  - " + conditional2.Label);
				}
			}
		}
		return stringBuilder;
	}

	public List<string> GetImmutableEndoGeneExclusionTags()
	{
		return immutableEndogenes.Where((GeneDef x) => x.exclusionTags != null).SelectMany((GeneDef x) => x.exclusionTags).ToList();
	}

	public FilterResult IsHediffLegal(HediffDef hediffDef)
	{
		if (hediffFilters == null)
		{
			return FilterResult.Neutral;
		}
		return hediffFilters.GetFilterResult(hediffDef);
	}

	/// <summary>
	/// Checks if a gene is legal for the pawn.
	/// </summary>
	/// <param name="gene"></param>
	/// <param name="removalCheck">If true the gene will be removed when failing legality check. Otherwise it will just be disabled.</param>
	/// <returns></returns>
	public FilterResult IsGeneLegal(GeneDef gene, bool removalCheck)
	{
		if (gene == null)
		{
			return FilterResult.ForceAllow;
		}
		if (_blocked.TryGetValue(gene, out var value))
		{
			return value;
		}
		if (AllForcedGenes.Contains(gene))
		{
			return FilterResult.ForceAllow;
		}
		if (immutableEndogenes != null && !AllForcedGenes.Contains(gene))
		{
			List<string> immutableEndoGeneExclusionTags = GetImmutableEndoGeneExclusionTags();
			if (!GenList.NullOrEmpty<string>((IList<string>)immutableEndoGeneExclusionTags) && !GenList.NullOrEmpty<string>((IList<string>)gene.exclusionTags) && GenCollection.Any<string>(gene.exclusionTags, (Predicate<string>)immutableEndoGeneExclusionTags.Contains))
			{
				return FilterResult.Banned;
			}
		}
		List<FilterResult> list = new List<FilterResult>(1) { FilterResult.Neutral };
		list.Add(geneFilters?.GetFilterResult(gene) ?? FilterResult.Neutral);
		if (gene.displayCategory != null)
		{
			list.Add(geneCategoryFilters?.GetFilterResult(gene.displayCategory) ?? FilterResult.Neutral);
		}
		if (gene.exclusionTags != null)
		{
			list.Add(geneTagFilters?.GetFilterResultFromItemList(gene.exclusionTags) ?? FilterResult.Neutral);
		}
		if (((Def)gene).descriptionHyperlinks != null)
		{
			list.Add(geneTagFilters?.GetFilterResultFromItemList((from x in ((Def)gene).descriptionHyperlinks
				where x.def is DefTag
				select x.def.defName).ToList()) ?? FilterResult.Neutral);
		}
		if (!removalCheck)
		{
			list.Add(activeGeneFilters?.GetFilterResult(gene) ?? FilterResult.Neutral);
			if (gene.displayCategory != null)
			{
				list.Add(activeGeneCategoryFilters?.GetFilterResult(gene.displayCategory) ?? FilterResult.Neutral);
			}
			if (gene.exclusionTags != null)
			{
				list.Add(activeGeneTagFilters?.GetFilterResultFromItemList(gene.exclusionTags) ?? FilterResult.Neutral);
			}
			if (((Def)gene).descriptionHyperlinks != null)
			{
				list.Add(activeGeneTagFilters?.GetFilterResultFromItemList((from x in ((Def)gene).descriptionHyperlinks
					where x.def is DefTag
					select x.def.defName).ToList()) ?? FilterResult.Neutral);
			}
		}
		FilterResult filterResult = list.Max();
		_blocked[gene] = filterResult;
		return filterResult;
	}
}
