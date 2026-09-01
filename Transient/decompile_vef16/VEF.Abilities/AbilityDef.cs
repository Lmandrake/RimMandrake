using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class AbilityDef : Def
{
	public Type abilityClass;

	public bool needsTicking;

	public bool needsTickingInterval;

	public bool showUndrafted;

	public bool? isPositive;

	public bool? keepCarryingThing;

	public HediffWithLevelCombination requiredHediff;

	public TraitDef requiredTrait;

	public int targetCount = 1;

	private AbilityTargetingMode targetMode;

	public List<AbilityTargetingMode> targetModes = new List<AbilityTargetingMode>();

	private TargetingParameters targetingParameters;

	public TargetingParametersForAoE targetingParametersForAoE;

	public List<TargetingParameters> targetingParametersList = new List<TargetingParameters>();

	public float range;

	public float maxRange = float.MaxValue;

	public float minRange = -1f;

	public List<StatModifier> rangeStatFactors = new List<StatModifier>();

	public List<StatModifier> rangeStatOffsets = new List<StatModifier>();

	public float radius;

	public float maxRadius = float.MaxValue;

	public float minRadius = -1f;

	public List<StatModifier> radiusStatFactors = new List<StatModifier>();

	public List<StatModifier> radiusStatOffsets = new List<StatModifier>();

	public float power;

	public List<StatModifier> powerStatFactors = new List<StatModifier>();

	public List<StatModifier> powerStatOffsets = new List<StatModifier>();

	public int castTime;

	public List<StatModifier> castTimeStatFactors = new List<StatModifier>();

	public List<StatModifier> castTimeStatOffsets = new List<StatModifier>();

	public int cooldownTime;

	public List<StatModifier> cooldownTimeStatFactors = new List<StatModifier>();

	public List<StatModifier> cooldownTimeStatOffsets = new List<StatModifier>();

	public int durationTime;

	public List<StatModifier> durationTimeStatFactors = new List<StatModifier>();

	public List<StatModifier> durationTimeStatOffsets = new List<StatModifier>();

	public int goodwillImpact;

	public bool applyGoodwillImpactToLodgers = true;

	public bool worldTargeting;

	public bool hasAoE;

	public bool requireLineOfSight = true;

	public JobDef jobDef;

	public float distanceToTarget = 1.5f;

	public bool showGizmoOnWorldView;

	public bool reserveTargets;

	public ThingDef warmupMote;

	public SoundDef warmupSound;

	public SoundDef warmupStartSound;

	public SoundDef warmupPreEndSound;

	public int warmupPreEndSoundTicks;

	public float moteOffsetAmountTowardsTarget;

	public bool drawAimPie = true;

	[Unsaved(false)]
	public Texture2D icon = BaseContent.BadTex;

	public string iconPath;

	public SoundDef castSound;

	public FleckDef castFleck;

	public float castFleckScale = 1f;

	public bool castFleckScaleWithRadius;

	public float castFleckSpeed;

	public FleckDef fleckOnTarget;

	public bool fleckOnTargetScaleWithRadius;

	public float fleckOnTargetScale = 1f;

	public float fleckOnTargetSpeed;

	public HediffDef casterHediff;

	public List<FleckDef> targetFlecks;

	public VerbProperties verbProperties;

	public float chance = 1f;

	public bool autocastPlayerDefault;

	public Type gizmoClass = typeof(Command_Ability);

	public Color rangeRingColor = Color.cyan;

	public Color radiusRingColor = Color.red;

	public string jobReportString = "Using ability: {0}";

	public string JobReportString => TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted(jobReportString, NamedArgument.op_Implicit(((Def)this).LabelCap)));

	public float Chance => chance;

	public bool Satisfied(Hediff_Abilities hediff)
	{
		if ((hediff != null && hediff.SatisfiesConditionForAbility(this)) || requiredHediff == null)
		{
			if (requiredTrait != null)
			{
				bool? obj;
				if (hediff == null)
				{
					obj = null;
				}
				else
				{
					Pawn pawn = ((Hediff)hediff).pawn;
					if (pawn == null)
					{
						obj = null;
					}
					else
					{
						Pawn_StoryTracker story = pawn.story;
						obj = ((story != null) ? new bool?(story.traits.HasTrait(requiredTrait)) : ((bool?)null));
					}
				}
				bool? flag = obj;
				return flag == true;
			}
			return true;
		}
		return false;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
		if (!typeof(Ability).IsAssignableFrom(abilityClass))
		{
			yield return $"{abilityClass} is not a valid ability type";
		}
		else
		{
			if (!needsTicking && AccessTools.DeclaredMethod(abilityClass, "Tick", Type.EmptyTypes, (Type[])null) != null)
			{
				yield return base.defName + " has a Tick method but doesn't have the needsTicking field. It will not work.";
			}
			if (!needsTickingInterval && AccessTools.DeclaredMethod(abilityClass, "TickInterval", new Type[1] { typeof(int) }, (Type[])null) != null)
			{
				yield return base.defName + " has a TickInterval method but doesn't have the needsTickingInterval field. It will not work.";
			}
		}
		if (targetModes != null && targetModes.Count != targetCount)
		{
			yield return $"{base.defName} has {targetCount} targets but {targetModes.Count} modes. This will lead to unexpected behavior";
		}
		if (targetingParametersList != null && targetingParametersList.Count != targetCount)
		{
			yield return $"{base.defName} has {targetCount} targets but {targetingParametersList.Count} targeting parameters. This will lead to unexpected behavior";
		}
		if (hasAoE && targetCount != 1 && (targetCount != 2 || targetModes == null || targetModes.Count != 2 || targetModes[1] != AbilityTargetingMode.Random))
		{
			yield return base.defName + " is AoE but has more than one target. This will lead to unexpected behavior";
		}
		if (!typeof(Command_Ability).IsAssignableFrom(gizmoClass))
		{
			yield return base.defName + " uses gizmo class " + Gen.ToStringSafe<Type>(gizmoClass) + " not subclassing from Command_Ability";
		}
	}

	public override void PostLoad()
	{
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Expected O, but got Unknown
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Expected O, but got Unknown
		if (!GenText.NullOrEmpty(iconPath))
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				icon = ContentFinder<Texture2D>.Get(iconPath, true);
			});
		}
		if (targetingParameters != null)
		{
			if (GenCollection.Any<TargetingParameters>(targetingParametersList))
			{
				targetingParametersList.Insert(0, targetingParameters);
			}
			else
			{
				targetingParametersList.Add(targetingParameters);
			}
		}
		if (targetMode != 0)
		{
			if (GenCollection.Any<AbilityTargetingMode>(targetModes))
			{
				targetModes.Insert(0, targetMode);
			}
			else
			{
				targetModes.Add(targetMode);
			}
		}
		for (int i = 0; i < targetCount; i++)
		{
			TargetingParameters val = ((targetingParametersList.Count > i) ? targetingParametersList[i] : null);
			AbilityTargetingMode abilityTargetingMode = ((targetModes.Count > i) ? targetModes[i] : ((val == null) ? AbilityTargetingMode.Self : AbilityTargetingMode.None));
			if (val == null)
			{
				val = new TargetingParameters
				{
					canTargetPawns = false,
					canTargetBuildings = false,
					canTargetAnimals = false,
					canTargetHumans = false,
					canTargetMechs = false
				};
				if (abilityTargetingMode == AbilityTargetingMode.None)
				{
					abilityTargetingMode = AbilityTargetingMode.Self;
				}
				switch (abilityTargetingMode)
				{
				case AbilityTargetingMode.Self:
					val = new TargetingParameters
					{
						targetSpecificThing = null,
						canTargetPawns = false,
						canTargetBuildings = false,
						mapObjectTargetsMustBeAutoAttackable = false
					};
					break;
				case AbilityTargetingMode.Location:
					val.canTargetLocations = true;
					break;
				case AbilityTargetingMode.Thing:
					val.canTargetItems = true;
					val.canTargetBuildings = true;
					break;
				case AbilityTargetingMode.Pawn:
					val.canTargetPawns = (val.canTargetHumans = (val.canTargetMechs = (val.canTargetAnimals = true)));
					break;
				case AbilityTargetingMode.Humanlike:
					val.canTargetPawns = (val.canTargetHumans = true);
					break;
				default:
					throw new ArgumentOutOfRangeException();
				case AbilityTargetingMode.Tile:
					break;
				}
			}
			if (i < targetModes.Count)
			{
				targetModes[i] = abilityTargetingMode;
			}
			else
			{
				targetModes.Add(abilityTargetingMode);
			}
			if (i < targetingParametersList.Count)
			{
				targetingParametersList[i] = val;
			}
			else
			{
				targetingParametersList.Add(val);
			}
		}
	}

	public override void ResolveReferences()
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Expected O, but got Unknown
		((Def)this).ResolveReferences();
		if (base.modExtensions == null)
		{
			base.modExtensions = new List<DefModExtension>();
		}
		if (verbProperties == null)
		{
			verbProperties = new VerbProperties
			{
				verbClass = typeof(Verb_CastAbility),
				label = base.label,
				category = (VerbCategory)3,
				range = range,
				minRange = minRange,
				noiseRadius = 3f,
				targetParams = targetingParameters,
				warmupTime = (float)castTime / 60f,
				defaultCooldownTime = cooldownTime,
				meleeDamageBaseAmount = Mathf.RoundToInt(power),
				meleeDamageDef = DamageDefOf.Blunt
			};
		}
		if (base.modExtensions == null)
		{
			return;
		}
		foreach (DefModExtension modExtension in base.modExtensions)
		{
			if (modExtension is AbilityExtension_AbilityMod abilityExtension_AbilityMod)
			{
				abilityExtension_AbilityMod.abilityDef = this;
			}
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((Def)this).ConfigErrors();
	}
}
