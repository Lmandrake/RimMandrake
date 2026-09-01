using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using JetBrains.Annotations;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Utils;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Abilities;

public abstract class Ability : IExposable, ILoadReferenceable, ITargetingSource
{
	public Pawn pawn;

	public Thing holder;

	public AbilityDef def;

	public int cooldown;

	public Verb_CastAbility verb;

	public Hediff_Abilities hediff;

	public List<AbilityExtension_AbilityMod> abilityModExtensions;

	public Mote warmupMote;

	private Sustainer soundCast;

	private CompAbilities comp;

	public int currentTargetingIndex = -1;

	public GlobalTargetInfo[] currentTargets = Array.Empty<GlobalTargetInfo>();

	private static readonly HashSet<ToStringStyle> percentageBasedStyles = new HashSet<ToStringStyle>
	{
		(ToStringStyle)8,
		(ToStringStyle)9,
		(ToStringStyle)10
	};

	private List<Pair<Effecter, TargetInfo>> maintainedEffecters = new List<Pair<Effecter, TargetInfo>>();

	public bool autoCast;

	protected bool currentAoETargeting;

	public LocalTargetInfo firstTarget;

	public Hediff_Abilities Hediff
	{
		get
		{
			if (hediff != null || def.requiredHediff == null)
			{
				return hediff;
			}
			Pawn obj = pawn;
			return hediff = (Hediff_Abilities)(object)((obj != null) ? obj.health.hediffSet.GetFirstHediffOfDef(def.requiredHediff.hediffDef, false) : null);
		}
	}

	public List<AbilityExtension_AbilityMod> AbilityModExtensions => abilityModExtensions ?? (abilityModExtensions = ((Def)def).modExtensions.Where((DefModExtension dme) => dme is AbilityExtension_AbilityMod).Cast<AbilityExtension_AbilityMod>().ToList());

	public CompAbilities Comp => comp ?? (comp = ((ThingWithComps)pawn).GetComp<CompAbilities>());

	public virtual bool AutoCast
	{
		get
		{
			if (!pawn.IsColonistPlayerControlled)
			{
				if (((Thing)pawn).Spawned)
				{
					return CanAutoCast;
				}
				return false;
			}
			return autoCast;
		}
	}

	public virtual bool CanAutoCast
	{
		get
		{
			if (def.targetCount == 1)
			{
				return Chance > 0f;
			}
			return false;
		}
	}

	public virtual float Chance => def.Chance;

	protected PlanetTile Tile
	{
		get
		{
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_006b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)pawn);
			if (caravan == null)
			{
				Map map = ((Thing)pawn).Map;
				if (map == null)
				{
					Map obj = GenCollection.FirstOrDefault<Map>(Find.Maps, (Predicate<Map>)((Map m) => m.IsPlayerHome));
					if (obj == null)
					{
						Map obj2 = Find.Maps.FirstOrDefault();
						if (obj2 == null)
						{
							return TileFinder.RandomStartingTile();
						}
						return obj2.Tile;
					}
					return obj.Tile;
				}
				return map.Tile;
			}
			return ((WorldObject)caravan).Tile;
		}
	}

	public bool CasterIsPawn => CasterPawn != null;

	public bool IsMeleeAttack => GetRangeForPawn() < 6f;

	public bool Targetable => def.targetModes[(currentTargetingIndex >= 0) ? currentTargetingIndex : 0] != AbilityTargetingMode.Self;

	public bool MultiSelect { get; }

	public virtual bool HidePawnTooltips
	{
		get
		{
			foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
			{
				if (abilityModExtension.HidePawnTooltips)
				{
					return true;
				}
			}
			return false;
		}
	}

	public Thing Caster => (Thing)(((object)pawn) ?? ((object)holder));

	public Pawn CasterPawn => pawn;

	public Verb GetVerb => (Verb)(object)verb;

	public Texture2D UIIcon => def.icon;

	public virtual TargetingParameters targetParams
	{
		get
		{
			TargetingParameters val = def.targetingParametersList[(currentTargetingIndex >= 0) ? currentTargetingIndex : 0];
			if (def.targetModes[(currentTargetingIndex >= 0) ? currentTargetingIndex : 0] == AbilityTargetingMode.Self)
			{
				val.targetSpecificThing = (Thing)(object)pawn;
			}
			return val;
		}
	}

	public ITargetingSource DestinationSelector { get; }

	public virtual void Init()
	{
		if (verb == null)
		{
			verb = (Verb_CastAbility)Activator.CreateInstance(def.verbProperties.verbClass);
		}
		((Verb)verb).loadID = GetUniqueLoadID() + "_Verb";
		((Verb)verb).verbProps = def.verbProperties;
		((Verb)verb).verbTracker = pawn?.verbTracker;
		((Verb)verb).caster = (Thing)(object)pawn;
		verb.ability = this;
		autoCast = CanAutoCast && def.autocastPlayerDefault;
		currentTargetingIndex = -1;
		currentTargets = (GlobalTargetInfo[])(object)new GlobalTargetInfo[def.targetCount];
	}

	public virtual bool ShowGizmoOnPawn()
	{
		if (pawn != null && ((pawn.IsColonistPlayerControlled && (def.showUndrafted || pawn.Drafted)) || (CaravanUtility.IsCaravanMember(pawn) && pawn.IsColonist && !pawn.IsPrisoner && !pawn.Downed)))
		{
			return AbilityModExtensions.All((AbilityExtension_AbilityMod x) => x.ShowGizmoOnPawn(pawn));
		}
		return false;
	}

	public virtual bool IsEnabledForPawn(out string reason)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		if (cooldown > Find.TickManager.TicksGame)
		{
			reason = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VFEA.AbilityDisableReasonCooldown", NamedArgument.op_Implicit(((Def)def).LabelCap), NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(cooldown - Find.TickManager.TicksGame, true, false, true, true, false))));
			return false;
		}
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			if (!abilityModExtension.IsEnabledForPawn(this, out var reason2))
			{
				reason = reason2;
				return false;
			}
		}
		Pawn obj = pawn;
		reason = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VFEA.AbilityDisableReasonGeneral", NamedArgument.op_Implicit((obj != null) ? obj.NameShortColored : TaggedString.op_Implicit(((Entity)holder).LabelCap))));
		return def.Satisfied(Hediff);
	}

	public virtual float CalculateStatFactorForPawn(float current, StatModifier statFactor)
	{
		if (!(statFactor.value >= 0f))
		{
			return current / (StatExtension.GetStatValue((Thing)(object)pawn, statFactor.stat, true, -1) * Math.Abs(statFactor.value));
		}
		return current * (StatExtension.GetStatValue((Thing)(object)pawn, statFactor.stat, true, -1) * statFactor.value);
	}

	public virtual float CalculateStatOffsetForPawn(float current, StatModifier statOffset)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (!percentageBasedStyles.Contains(statOffset.stat.toStringStyle))
		{
			return current + StatExtension.GetStatValue((Thing)(object)pawn, statOffset.stat, true, -1) * statOffset.value;
		}
		return current + (StatExtension.GetStatValue((Thing)(object)pawn, statOffset.stat, true, -1) - statOffset.stat.defaultBaseValue) * statOffset.value;
	}

	public virtual float CalculateModifiedStatForPawn(float current, IEnumerable<StatModifier> statFactors, IEnumerable<StatModifier> statOffsets)
	{
		return statOffsets.Aggregate(0f, CalculateStatOffsetForPawn) + statFactors.Aggregate(current, CalculateStatFactorForPawn);
	}

	public virtual float GetRangeForPawn()
	{
		if (def.targetModes[(currentTargetingIndex >= 0) ? currentTargetingIndex : 0] != AbilityTargetingMode.Self)
		{
			return Mathf.Min(CalculateModifiedStatForPawn(def.range, def.rangeStatFactors, def.rangeStatOffsets), def.maxRange);
		}
		return 0f;
	}

	public virtual float GetRadiusForPawn()
	{
		return Mathf.Min(CalculateModifiedStatForPawn(def.radius, def.radiusStatFactors, def.radiusStatOffsets), def.maxRadius);
	}

	public float GetAdditionalRadius()
	{
		return ((Def)def).GetModExtension<AbilityExtension_AdditionalRadius>().GetRadiusFor(pawn);
	}

	public virtual float GetPowerForPawn()
	{
		float num = CalculateModifiedStatForPawn(def.power, def.powerStatFactors, def.powerStatOffsets);
		AbilityExtension_RandomPowerMultiplier modExtension = ((Def)def).GetModExtension<AbilityExtension_RandomPowerMultiplier>();
		if (modExtension == null)
		{
			return num;
		}
		return num * ((FloatRange)(ref modExtension.range)).RandomInRange;
	}

	public virtual int GetCastTimeForPawn()
	{
		return Mathf.RoundToInt(CalculateModifiedStatForPawn(def.castTime, def.castTimeStatFactors, def.castTimeStatOffsets));
	}

	public virtual int GetCooldownForPawn()
	{
		return Mathf.RoundToInt(CalculateModifiedStatForPawn(def.cooldownTime, def.cooldownTimeStatFactors, def.cooldownTimeStatOffsets));
	}

	public virtual int GetDurationForPawn()
	{
		return Mathf.RoundToInt(CalculateModifiedStatForPawn(def.durationTime, def.durationTimeStatFactors, def.durationTimeStatOffsets));
	}

	public virtual string GetPowerForPawnDescription()
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		float num = CalculateModifiedStatForPawn(def.power, def.powerStatFactors, def.powerStatOffsets);
		if (num == 0f)
		{
			return "";
		}
		AbilityExtension_RandomPowerMultiplier modExtension = ((Def)def).GetModExtension<AbilityExtension_RandomPowerMultiplier>();
		if (modExtension == null)
		{
			return ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("VFEA.AbilityStatsPower"), num), Color.cyan);
		}
		FloatRange range = modExtension.range;
		return ColoredText.Colorize(string.Format("{0}: {1}-{2}", Translator.Translate("VFEA.AbilityStatsPower"), num * range.min, num * range.max), Color.cyan);
	}

	public virtual string GetDescriptionForPawn()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_029b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0312: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder(ColoredText.Colorize(((Def)def).LabelCap, ColoredText.TipSectionTitleColor) + "\n\n" + ((Def)def).description + "\n\n");
		float rangeForPawn = GetRangeForPawn();
		if (rangeForPawn > 0f && rangeForPawn < 500f)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("Range"), rangeForPawn), Color.cyan));
		}
		if (def.minRange > 0f)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("MinimumRange"), def.minRange), Color.cyan));
		}
		float radiusForPawn = GetRadiusForPawn();
		if (radiusForPawn > 0f && radiusForPawn < 500f)
		{
			TaggedString val = Translator.Translate("radius");
			stringBuilder.AppendLine(ColoredText.Colorize($"{((TaggedString)(ref val)).CapitalizeFirst()}: {radiusForPawn}", Color.cyan));
		}
		if (def.minRadius > 0f)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("VFEA.MinRadius"), def.minRadius), Color.cyan));
		}
		string powerForPawnDescription = GetPowerForPawnDescription();
		if (!GenText.NullOrEmpty(powerForPawnDescription))
		{
			stringBuilder.AppendLine(powerForPawnDescription);
		}
		int castTimeForPawn = GetCastTimeForPawn();
		if (castTimeForPawn > 0)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("AbilityCastingTime"), castTimeForPawn.ToStringTicksToPeriodSpecific()), Color.cyan));
		}
		int cooldownForPawn = GetCooldownForPawn();
		if (cooldownForPawn > 0)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("CooldownTime"), cooldownForPawn.ToStringTicksToPeriodSpecific()), Color.cyan));
		}
		int durationForPawn = GetDurationForPawn();
		if (durationForPawn > 0)
		{
			stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1}", Translator.Translate("VFEA.AbilityStatsDuration"), durationForPawn.ToStringTicksToPeriodSpecific()), Color.cyan));
		}
		else if (((Def)def).HasModExtension<AbilityExtension_Hediff>())
		{
			HediffCompProperties_Disappears val2 = ((Def)def).GetModExtension<AbilityExtension_Hediff>().hediff.CompProps<HediffCompProperties_Disappears>();
			if (val2 != null)
			{
				stringBuilder.AppendLine(ColoredText.Colorize(string.Format("{0}: {1} ~ {2}", Translator.Translate("VFEA.AbilityStatsDuration"), val2.disappearsAfterTicks.min.ToStringTicksToPeriodSpecific(), val2.disappearsAfterTicks.max.ToStringTicksToPeriodSpecific()), Color.cyan));
			}
		}
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			string description = abilityModExtension.GetDescription(this);
			if (description.Length > 1)
			{
				stringBuilder.AppendLine(description);
			}
		}
		if (CanAutoCast)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate(AutoCast ? "VFEA.RClickToNoAuto" : "VFEA.RClickToAuto")));
		}
		return GenText.TrimEndNewlines(stringBuilder.ToString());
	}

	public virtual void Tick()
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		for (int num = maintainedEffecters.Count - 1; num >= 0; num--)
		{
			Effecter first = maintainedEffecters[num].First;
			if (first.ticksLeft > 0)
			{
				TargetInfo second = maintainedEffecters[num].Second;
				first.EffectTick(second, second);
				first.ticksLeft--;
			}
			else
			{
				first.Cleanup();
				maintainedEffecters.RemoveAt(num);
			}
		}
	}

	public virtual void TickInterval(int delta)
	{
	}

	public virtual Gizmo GetGizmo()
	{
		return (Gizmo)(object)(Command_Ability)Activator.CreateInstance(def.gizmoClass, pawn, this);
	}

	public virtual void GizmoUpdateOnMouseover()
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		float num = ((def.targetModes[0] != AbilityTargetingMode.Self) ? GetRangeForPawn() : GetRadiusForPawn());
		if (GenRadial.MaxRadialPatternRadius > num && num >= 1f)
		{
			GenDraw.DrawRadiusRing(((Thing)pawn).Position, num, def.rangeRingColor, (Func<IntVec3, bool>)null);
		}
		if (GenRadial.MaxRadialPatternRadius > def.minRange && def.minRange >= 1f)
		{
			GenDraw.DrawRadiusRing(((Thing)pawn).Position, def.minRange, def.rangeRingColor, (Func<IntVec3, bool>)null);
		}
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.GizmoUpdateOnMouseover(this);
		}
	}

	public virtual void WarmupToil(Toil toil)
	{
		toil.AddPreInitAction((Action)delegate
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			SoundDef warmupStartSound = def.warmupStartSound;
			if (warmupStartSound != null)
			{
				SoundStarter.PlayOneShot(warmupStartSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)toil.actor).Position, ((Thing)toil.actor).Map, false)));
			}
		});
		toil.AddPreTickAction((Action)delegate
		{
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_0099: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
			//IL_013c: Unknown result type (might be due to invalid IL or missing references)
			//IL_013d: Unknown result type (might be due to invalid IL or missing references)
			if (def.warmupPreEndSound != null && ((Verb)verb).WarmupTicksLeft == def.warmupPreEndSoundTicks)
			{
				SoundStarter.PlayOneShot(def.warmupPreEndSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)toil.actor).Position, ((Thing)toil.actor).Map, false)));
			}
			if (def.warmupMote != null)
			{
				Vector3 drawPos = ((Thing)pawn).DrawPos;
				Vector3 val = drawPos;
				LocalTargetInfo currentTarget = ((Verb)verb).CurrentTarget;
				drawPos = val + (((LocalTargetInfo)(ref currentTarget)).CenterVector3 - drawPos) * def.moteOffsetAmountTowardsTarget;
				if (warmupMote == null || ((Thing)warmupMote).Destroyed)
				{
					warmupMote = MoteMaker.MakeStaticMote(drawPos, ((Thing)pawn).Map, def.warmupMote, 1f, false, 0f);
				}
				else
				{
					warmupMote.exactPosition = drawPos;
					warmupMote.Maintain();
				}
			}
			if (def.warmupSound != null)
			{
				if (soundCast == null || soundCast.Ended)
				{
					soundCast = SoundStarter.TrySpawnSustainer(def.warmupSound, SoundInfo.InMap(new TargetInfo(((Thing)pawn).Position, ((Thing)pawn).Map, false), (MaintenanceType)1));
				}
				else
				{
					soundCast.Maintain();
				}
			}
		});
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.WarmupToil(toil);
		}
	}

	public virtual void DoAction()
	{
		SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Tiny, (Map)null);
		if (Event.current.button == 1)
		{
			if (CanAutoCast)
			{
				autoCast = !autoCast;
			}
			else
			{
				autoCast = false;
			}
		}
		else
		{
			currentTargetingIndex = -1;
			currentTargets = (GlobalTargetInfo[])(object)new GlobalTargetInfo[def.targetCount];
			DoTargeting();
		}
	}

	public virtual void DoTargeting()
	{
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_01da: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		currentTargetingIndex++;
		if (currentTargetingIndex >= def.targetCount)
		{
			if (currentTargets.Length <= 1)
			{
				if (currentTargets.Any())
				{
					GlobalTargetInfo val = currentTargets.First();
					if (((GlobalTargetInfo)(ref val)).Map != Caster.Map)
					{
						goto IL_00a2;
					}
				}
				if (!CaravanUtility.IsCaravanMember(pawn) && !currentTargets.Any((GlobalTargetInfo gti) => ((GlobalTargetInfo)(ref gti)).HasWorldObject))
				{
					this.CreateCastJob((!currentTargets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref currentTargets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref currentTargets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref currentTargets[0])).Cell)));
					return;
				}
			}
			goto IL_00a2;
		}
		AbilityTargetingMode targetMode = def.targetModes[currentTargetingIndex];
		if (targetMode == AbilityTargetingMode.Self)
		{
			currentTargets[currentTargetingIndex] = GlobalTargetInfo.op_Implicit((Thing)(object)pawn);
			DoTargeting();
		}
		else if (targetMode == AbilityTargetingMode.Random)
		{
			IntVec3 cell = ((currentTargets.Length > currentTargetingIndex) ? ((GlobalTargetInfo)(ref currentTargets[currentTargetingIndex - 1])).Cell : ((Thing)pawn).Position);
			GlobalTargetInfo val2 = default(GlobalTargetInfo);
			if (GenCollection.TryRandomElement<GlobalTargetInfo>(GetTargetsAround(cell, targetParams, isRandom: true), ref val2))
			{
				currentTargets[currentTargetingIndex] = val2;
			}
			DoTargeting();
		}
		else if (def.worldTargeting)
		{
			GlobalTargetInfo worldTarget = CameraJumper.GetWorldTarget(GlobalTargetInfo.op_Implicit((Thing)(object)pawn));
			CameraJumper.TryJump(worldTarget, (MovementMode)0);
			Find.WorldTargeter.BeginTargeting((Func<GlobalTargetInfo, bool>)delegate(GlobalTargetInfo gti)
			{
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				//IL_0018: Unknown result type (might be due to invalid IL or missing references)
				//IL_0051: Unknown result type (might be due to invalid IL or missing references)
				//IL_0052: Unknown result type (might be due to invalid IL or missing references)
				//IL_0080: Unknown result type (might be due to invalid IL or missing references)
				//IL_0087: Unknown result type (might be due to invalid IL or missing references)
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0092: Unknown result type (might be due to invalid IL or missing references)
				//IL_010f: Unknown result type (might be due to invalid IL or missing references)
				if (!ValidateTargetTile(gti, showMessages: true))
				{
					return false;
				}
				MapParent obj = Find.WorldObjects.MapParentAt(((GlobalTargetInfo)(ref gti)).Tile);
				Map val3 = ((obj != null) ? obj.Map : null);
				if (targetMode == AbilityTargetingMode.Tile || val3 == null)
				{
					currentTargets[currentTargetingIndex] = gti;
					DoTargeting();
					return true;
				}
				currentTargets[currentTargetingIndex] = new GlobalTargetInfo(val3.AllCells.First(), val3, false);
				CameraJumper.TryJump(val3.Center, val3, (MovementMode)0);
				Find.Targeter.BeginTargeting(targetParams, (Action<LocalTargetInfo>)OrderForceTarget, (Action<LocalTargetInfo>)DrawHighlight, (Func<LocalTargetInfo, bool>)((LocalTargetInfo lti) => ValidateTarget(lti)), (Pawn)null, (Action)null, MouseAttachment(currentTargets[currentTargetingIndex]), true, (Action<LocalTargetInfo>)null, (Action<LocalTargetInfo>)null);
				return true;
			}, targetMode == AbilityTargetingMode.Tile, MouseAttachment(worldTarget), targetMode == AbilityTargetingMode.Tile, (Action)OnUpdateWorld, (Func<GlobalTargetInfo, TaggedString>)WorldTargetingLabel, (Func<GlobalTargetInfo, bool>)CanHitTargetTile, (PlanetTile?)null, false);
		}
		else
		{
			Find.Targeter.BeginTargeting((ITargetingSource)(object)this, (ITargetingSource)null, false, (Func<LocalTargetInfo, ITargetingSource>)null, (Action)null, true);
		}
		return;
		IL_00a2:
		CreateCastJob(currentTargets);
	}

	public virtual bool AICanUseOn(Thing target)
	{
		if (def.isPositive.HasValue)
		{
			if (GenHostility.HostileTo(target, (Thing)(object)pawn))
			{
				if (def.isPositive.Value)
				{
					return false;
				}
			}
			else if (!def.isPositive.Value)
			{
				return false;
			}
		}
		return true;
	}

	protected virtual TaggedString WorldTargetingLabel(GlobalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit((string)null);
	}

	public virtual void CreateCastJob(LocalTargetInfo target)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		CreateCastJob(((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(Caster.Map));
	}

	public virtual void CreateCastJob(params GlobalTargetInfo[] targets)
	{
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			if (!abilityModExtension.Valid(targets, this, throwMessages: true))
			{
				currentTargetingIndex--;
				return;
			}
		}
		currentTargetingIndex = -1;
		bool startAbilityJobImmediately = true;
		PreCast(targets, ref startAbilityJobImmediately, delegate
		{
			StartAbilityJob(targets);
		});
		if (startAbilityJobImmediately)
		{
			StartAbilityJob(targets);
		}
		currentTargets = (GlobalTargetInfo[])(object)new GlobalTargetInfo[def.targetCount];
	}

	[Obsolete("Use new method with GlobalTargetInfo instead")]
	public void StartAbilityJob(LocalTargetInfo target)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		StartAbilityJob(((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(Caster.Map));
	}

	public void StartAbilityJob(params GlobalTargetInfo[] targets)
	{
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		Pawn_JobTracker jobs = pawn.jobs;
		if (jobs != null)
		{
			jobs.EndCurrentJob((JobCondition)16, false, true);
		}
		Job val = JobMaker.MakeJob(def.jobDef ?? VFE_DefOf_Abilities.VFEA_UseAbility, (LocalTargetInfo)((targets.Any() && ((GlobalTargetInfo)(ref targets[0])).IsMapTarget) ? ((LocalTargetInfo)targets[0]) : default(LocalTargetInfo)));
		CompAbilities compAbilities = ((ThingWithComps)pawn).GetComp<CompAbilities>();
		compAbilities.currentlyCasting = this;
		ModifyTargets(ref targets);
		compAbilities.currentlyCastingTargets = targets;
		if (CaravanUtility.IsCaravanMember(pawn))
		{
			Cast(targets);
			return;
		}
		Pawn_JobTracker jobs2 = pawn.jobs;
		bool? keepCarryingThing = def.keepCarryingThing;
		jobs2.StartJob(val, (JobCondition)16, (ThinkNode)null, false, true, (ThinkTreeDef)null, (JobTag?)null, false, false, keepCarryingThing, false, true, false);
	}

	public virtual void ModifyTargets(ref GlobalTargetInfo[] targets)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (!def.hasAoE)
		{
			return;
		}
		currentAoETargeting = true;
		IEnumerable<GlobalTargetInfo> source = GetTargetsAround(((GlobalTargetInfo)(ref targets[0])).Cell, (TargetingParameters)(object)def.targetingParametersForAoE);
		if (def.targetCount == 2 && def.targetModes[1] == AbilityTargetingMode.Random)
		{
			source = source.SelectMany((GlobalTargetInfo target) => (IEnumerable<GlobalTargetInfo>)(object)new GlobalTargetInfo[2]
			{
				target,
				GenCollection.RandomElement<GlobalTargetInfo>(GetTargetsAround(((GlobalTargetInfo)(ref target)).Cell, def.targetingParametersList[1], isRandom: true))
			});
		}
		targets = source.ToArray();
		currentAoETargeting = false;
	}

	protected IEnumerable<GlobalTargetInfo> GetTargetsAround(IntVec3 cell, TargetingParameters parms, bool isRandom = false)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		float minRadius = def.minRadius;
		float num = GetRadiusForPawn();
		if (isRandom)
		{
			AbilityExtension_RandomRadius modExtension = ((Def)def).GetModExtension<AbilityExtension_RandomRadius>();
			if (modExtension != null)
			{
				minRadius = modExtension.minRadius;
				num = modExtension.maxRadius;
			}
		}
		if (parms.canTargetLocations)
		{
			foreach (IntVec3 item in GenRadial.RadialCellsAround(cell, minRadius, num))
			{
				if (GenGrid.InBounds(item, ((Thing)pawn).Map) && (!(parms is TargetingParametersForAoE targetingParametersForAoE) || targetingParametersForAoE.CanTarget(new TargetInfo(item, ((Thing)pawn).Map, false), this)))
				{
					yield return new GlobalTargetInfo(item, ((Thing)pawn).Map, false);
				}
			}
			yield break;
		}
		foreach (Thing item2 in GenRadial.RadialDistinctThingsAround(cell, ((Thing)pawn).Map, num, true))
		{
			TargetingParametersForAoE targetingParametersForAoE2 = parms as TargetingParametersForAoE;
			if (!(targetingParametersForAoE2?.CanTarget(TargetInfo.op_Implicit(item2), this) ?? parms.CanTarget(TargetInfo.op_Implicit(item2), (ITargetingSource)null)))
			{
				continue;
			}
			if (targetingParametersForAoE2 == null || !targetingParametersForAoE2.ignoreRangeAndSight)
			{
				if (!ValidateTarget(LocalTargetInfo.op_Implicit(item2), showMessages: false))
				{
					continue;
				}
				CellRect val = GenAdj.OccupiedRect(item2);
				if (!(((CellRect)(ref val)).ClosestDistSquaredTo(cell) > minRadius))
				{
					continue;
				}
			}
			if (parms.canTargetSelf || item2 != pawn)
			{
				yield return GlobalTargetInfo.op_Implicit(item2);
			}
		}
	}

	public virtual void PreCast(GlobalTargetInfo[] target, ref bool startAbilityJobImmediately, Action startJobAction)
	{
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.PreCast(target, this, ref startAbilityJobImmediately, startJobAction);
		}
	}

	[Obsolete("Refer to casting targets in comp instead")]
	public virtual void PreWarmupAction(LocalTargetInfo target)
	{
		PreWarmupAction();
	}

	public virtual void PreWarmupAction()
	{
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.PreWarmupAction(((ThingWithComps)pawn).GetComp<CompAbilities>().currentlyCastingTargets, this);
		}
	}

	[Obsolete("Use the new Cast method using GlobalTargets instead")]
	public virtual void Cast(LocalTargetInfo target)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		Cast(((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(Caster.Map));
	}

	public virtual void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_026c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0272: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Unknown result type (might be due to invalid IL or missing references)
		//IL_020e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_028b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0290: Unknown result type (might be due to invalid IL or missing references)
		//IL_0325: Unknown result type (might be due to invalid IL or missing references)
		//IL_030d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0312: Unknown result type (might be due to invalid IL or missing references)
		cooldown = Find.TickManager.TicksGame + GetCooldownForPawn();
		if (def.goodwillImpact != 0 && targets.Any())
		{
			for (int i = 0; i < targets.Length; i++)
			{
				GlobalTargetInfo val = targets[i];
				Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
				Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
				if (val2 != null)
				{
					ApplyGoodwillImpact(val2);
				}
			}
		}
		GlobalTargetInfo val3;
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			if (targets.Length <= 1)
			{
				if (targets.Any())
				{
					val3 = targets.First();
					if (((GlobalTargetInfo)(ref val3)).Map != Caster.Map)
					{
						goto IL_00a9;
					}
				}
				abilityModExtension.Cast((!targets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref targets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Cell)), this);
				continue;
			}
			goto IL_00a9;
			IL_00a9:
			abilityModExtension.Cast(targets, this);
		}
		if (targets.Length > 1)
		{
			goto IL_0148;
		}
		if (targets.Any())
		{
			val3 = targets.First();
			if (((GlobalTargetInfo)(ref val3)).Map != Caster.Map)
			{
				goto IL_0148;
			}
		}
		CheckCastEffects((!targets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref targets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Cell)), out var cast, out var target, out var hediffApply);
		goto IL_01a9;
		IL_0148:
		CheckCastEffects(targets, out cast, out target, out hediffApply);
		goto IL_01a9;
		IL_01a9:
		if (hediffApply)
		{
			if (targets.Length > 1)
			{
				goto IL_01d6;
			}
			if (targets.Any())
			{
				val3 = targets.First();
				if (((GlobalTargetInfo)(ref val3)).Map != Caster.Map)
				{
					goto IL_01d6;
				}
			}
			this.ApplyHediffs((!targets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref targets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Cell)));
		}
		goto IL_022b;
		IL_0258:
		CastEffects(targets);
		goto IL_02ad;
		IL_032f:
		PostCast(targets);
		return;
		IL_02da:
		TargetEffects(targets);
		goto IL_032f;
		IL_02ad:
		if (target)
		{
			if (targets.Length > 1)
			{
				goto IL_02da;
			}
			if (targets.Any())
			{
				val3 = targets.First();
				if (((GlobalTargetInfo)(ref val3)).Map != Caster.Map)
				{
					goto IL_02da;
				}
			}
			this.TargetEffects((!targets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref targets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Cell)));
		}
		goto IL_032f;
		IL_01d6:
		ApplyHediffs(targets);
		goto IL_022b;
		IL_022b:
		if (cast)
		{
			if (targets.Length > 1)
			{
				goto IL_0258;
			}
			if (targets.Any())
			{
				val3 = targets.First();
				if (((GlobalTargetInfo)(ref val3)).Map != Caster.Map)
				{
					goto IL_0258;
				}
			}
			this.CastEffects((!targets.Any()) ? default(LocalTargetInfo) : ((((GlobalTargetInfo)(ref targets[0])).Thing != null) ? new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Thing) : new LocalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Cell)));
		}
		goto IL_02ad;
	}

	public virtual void PostCast(params GlobalTargetInfo[] targets)
	{
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.PostCast(targets, this);
		}
	}

	public void ApplyGoodwillImpact(Pawn pawnTarget)
	{
		if (!pawnTarget.IsSlaveOfColony)
		{
			Faction homeFaction = pawnTarget.HomeFaction;
			if (((Thing)pawn).Faction == Faction.OfPlayer && homeFaction != null && !FactionUtility.HostileTo(homeFaction, ((Thing)pawn).Faction) && (def.applyGoodwillImpactToLodgers || !QuestUtility.IsQuestLodger(pawnTarget)) && !QuestUtility.IsQuestHelper(pawnTarget))
			{
				Faction.OfPlayer.TryAffectGoodwillWith(homeFaction, def.goodwillImpact, true, true, HistoryEventDefOf.UsedHarmfulAbility, (GlobalTargetInfo?)null);
			}
		}
	}

	public virtual void EndCastJob()
	{
	}

	[Obsolete("Use the new method that uses GlobalTargetInfo instead")]
	public virtual void CastEffects(LocalTargetInfo targetInfo)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		CastEffects(((LocalTargetInfo)(ref targetInfo)).ToGlobalTargetInfo(Caster.MapHeld));
	}

	public virtual void CastEffects(params GlobalTargetInfo[] targetInfos)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		if (def.castFleck != null)
		{
			MakeStaticFleck(((Thing)pawn).DrawPos, ((Thing)pawn).MapHeld, def.castFleck, def.castFleckScaleWithRadius ? GetRadiusForPawn() : def.castFleckScale, def.castFleckSpeed);
		}
		if (def.fleckOnTarget != null && targetInfos.Any())
		{
			Vector3 loc;
			if (!def.hasAoE)
			{
				if (((GlobalTargetInfo)(ref targetInfos[0])).Thing == null)
				{
					IntVec3 cell = ((GlobalTargetInfo)(ref targetInfos[0])).Cell;
					loc = ((IntVec3)(ref cell)).ToVector3();
				}
				else
				{
					loc = ((GlobalTargetInfo)(ref targetInfos[0])).Thing.DrawPos;
				}
			}
			else
			{
				loc = ((LocalTargetInfo)(ref firstTarget)).CenterVector3;
			}
			Map map = ((((GlobalTargetInfo)(ref targetInfos[0])).Thing != null) ? ((GlobalTargetInfo)(ref targetInfos[0])).Map : ((Thing)pawn).MapHeld);
			MakeStaticFleck(loc, map, def.fleckOnTarget, def.fleckOnTargetScaleWithRadius ? GetRadiusForPawn() : def.fleckOnTargetScale, def.fleckOnTargetSpeed);
		}
		if (def.casterHediff != null)
		{
			pawn.health.AddHediff(def.casterHediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		SoundDef castSound = def.castSound;
		if (castSound != null)
		{
			SoundStarter.PlayOneShot(castSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)pawn).Position, ((Thing)pawn).MapHeld, false)));
		}
	}

	public static void MakeStaticFleck(IntVec3 cell, Map map, FleckDef fleckDef, float scale, float speed)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		MakeStaticFleck(((IntVec3)(ref cell)).ToVector3Shifted(), map, fleckDef, scale, speed);
	}

	public static void MakeStaticFleck(Vector3 loc, Map map, FleckDef fleckDef, float scale, float speed)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, fleckDef, scale);
		dataStatic.velocitySpeed = speed;
		map.flecks.CreateFleck(dataStatic);
	}

	public void AddEffecterToMaintain(Effecter eff, IntVec3 pos, int ticks, Map map = null)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		eff.ticksLeft = ticks;
		maintainedEffecters.Add(new Pair<Effecter, TargetInfo>(eff, new TargetInfo(pos, map ?? ((Thing)pawn).Map, false)));
	}

	public void AddEffecterToMaintain(Effecter eff, TargetInfo target, int ticks)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		eff.ticksLeft = ticks;
		maintainedEffecters.Add(new Pair<Effecter, TargetInfo>(eff, target));
	}

	[Obsolete("Use new Method using GlobalTargetInfo instead")]
	public virtual void TargetEffects(LocalTargetInfo targetInfo)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		TargetEffects(((LocalTargetInfo)(ref targetInfo)).ToGlobalTargetInfo(Caster.Map));
	}

	public virtual void TargetEffects(params GlobalTargetInfo[] targetInfo)
	{
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		if (!targetInfo.Any())
		{
			return;
		}
		if (!GenList.NullOrEmpty<FleckDef>((IList<FleckDef>)def.targetFlecks))
		{
			foreach (FleckDef targetFleck in def.targetFlecks)
			{
				FleckMaker.Static(((GlobalTargetInfo)(ref targetInfo[0])).Cell, ((Thing)pawn).Map, targetFleck, 1f);
			}
		}
		Thing thing = ((GlobalTargetInfo)(ref targetInfo[0])).Thing;
		if (((Pawn)(((thing is Pawn) ? thing : null)?)).health.hediffSet.hediffs == null)
		{
			return;
		}
		foreach (Hediff hediff in ((Pawn)((GlobalTargetInfo)(ref targetInfo[0])).Thing).health.hediffSet.hediffs)
		{
			HediffWithComps val = (HediffWithComps)(object)((hediff is HediffWithComps) ? hediff : null);
			if (val == null)
			{
				continue;
			}
			foreach (HediffComp comp in val.comps)
			{
				if (comp is HediffComp_AbilityTargetReact hediffComp_AbilityTargetReact)
				{
					hediffComp_AbilityTargetReact.ReactTo(this);
				}
			}
		}
	}

	[Obsolete("Use new method that uses GlobalTargetInfo instead")]
	public virtual void ApplyHediffs(LocalTargetInfo targetInfo)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		ApplyHediffs(((LocalTargetInfo)(ref targetInfo)).ToGlobalTargetInfo(Caster.Map));
	}

	public virtual void ApplyHediffs(params GlobalTargetInfo[] targetInfo)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		AbilityExtension_Hediff modExtension = ((Def)def).GetModExtension<AbilityExtension_Hediff>();
		if (modExtension == null || !modExtension.applyAuto)
		{
			return;
		}
		if (modExtension.applyToCaster)
		{
			ApplyHediff(pawn, modExtension);
			return;
		}
		for (int i = 0; i < targetInfo.Length; i++)
		{
			GlobalTargetInfo val = targetInfo[i];
			Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
			Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val2 != null)
			{
				ApplyHediff(val2, modExtension);
			}
		}
	}

	public Hediff ApplyHediff(Pawn targetPawn)
	{
		AbilityExtension_Hediff modExtension = ((Def)def).GetModExtension<AbilityExtension_Hediff>();
		return ApplyHediff(targetPawn, modExtension);
	}

	public Hediff ApplyHediff(Pawn targetPawn, AbilityExtension_Hediff hediffExtension)
	{
		BodyPartRecord bodyPart = ((hediffExtension.bodyPartToApply != null) ? targetPawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null).FirstOrDefault((BodyPartRecord x) => x.def == hediffExtension.bodyPartToApply) : null);
		int num = GetDurationForPawn();
		if (hediffExtension.durationMultiplier != null)
		{
			num = (int)((float)num * (hediffExtension.durationMultiplierFromCaster ? StatExtension.GetStatValue((Thing)(object)pawn, hediffExtension.durationMultiplier, true, -1) : StatExtension.GetStatValue((Thing)(object)targetPawn, hediffExtension.durationMultiplier, true, -1)));
		}
		return ApplyHediff(targetPawn, hediffExtension.hediff, bodyPart, num, hediffExtension.severity);
	}

	public virtual Hediff ApplyHediff(Pawn targetPawn, HediffDef hediffDef, BodyPartRecord bodyPart, int duration, float severity)
	{
		Hediff val = HediffMaker.MakeHediff(hediffDef, targetPawn, bodyPart);
		if (val is Hediff_Ability hediff_Ability)
		{
			hediff_Ability.ability = this;
		}
		if (severity > float.Epsilon)
		{
			val.Severity = severity;
		}
		HediffWithComps val2 = (HediffWithComps)(object)((val is HediffWithComps) ? val : null);
		if (val2 != null)
		{
			foreach (HediffComp comp in val2.comps)
			{
				if (comp is HediffComp_Ability hediffComp_Ability)
				{
					hediffComp_Ability.ability = this;
				}
				if (duration > 0)
				{
					HediffComp_Disappears val3 = (HediffComp_Disappears)(object)((comp is HediffComp_Disappears) ? comp : null);
					if (val3 != null)
					{
						val3.ticksToDisappear = duration;
					}
				}
			}
		}
		targetPawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		return targetPawn.health.hediffSet.GetFirstHediffOfDef(hediffDef, false);
	}

	[Obsolete("Use new method that uses GlobalTargetInfos")]
	public virtual void CheckCastEffects(LocalTargetInfo targetInfo, out bool cast, out bool target, out bool hediffApply)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		CheckCastEffects((GlobalTargetInfo[])(object)new GlobalTargetInfo[1] { ((LocalTargetInfo)(ref targetInfo)).ToGlobalTargetInfo(Caster.Map) }, out cast, out target, out hediffApply);
	}

	public virtual void CheckCastEffects(GlobalTargetInfo[] targetsInfos, out bool cast, out bool target, out bool hediffApply)
	{
		cast = (target = (hediffApply = true));
	}

	public virtual void ExposeData()
	{
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Invalid comparison between Unknown and I4
		Scribe_References.Look<Pawn>(ref pawn, "pawn", true);
		Scribe_Values.Look<int>(ref cooldown, "cooldown", 0, false);
		Scribe_Defs.Look<AbilityDef>(ref def, "def");
		Scribe_Deep.Look<Verb_CastAbility>(ref verb, "verb", Array.Empty<object>());
		Scribe_Values.Look<bool>(ref autoCast, "autoCast", false, false);
		Scribe_TargetInfo.Look(ref firstTarget, "firstTarget");
		if ((int)Scribe.mode == 4)
		{
			if (verb == null)
			{
				verb = (Verb_CastAbility)Activator.CreateInstance(def.verbProperties.verbClass);
			}
			((Verb)verb).loadID = GetUniqueLoadID() + "_Verb";
			((Verb)verb).verbProps = def.verbProperties;
			((Verb)verb).verbTracker = pawn?.verbTracker;
			((Verb)verb).caster = (Thing)(object)pawn;
			verb.ability = this;
			currentTargetingIndex = -1;
			currentTargets = (GlobalTargetInfo[])(object)new GlobalTargetInfo[def.targetCount];
		}
	}

	public string GetUniqueLoadID()
	{
		return "Ability_" + ((Def)def).defName + "_" + holder.GetUniqueLoadID();
	}

	public virtual bool CanHitTarget(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return CanHitTarget(target, def.requireLineOfSight);
	}

	public virtual bool CanHitTarget(LocalTargetInfo target, bool sightCheck)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			if (!abilityModExtension.CanApplyOn(target, this))
			{
				return false;
			}
		}
		if (currentAoETargeting)
		{
			return true;
		}
		if (def.worldTargeting)
		{
			return true;
		}
		float num = IntVec3Utility.DistanceTo(((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Position);
		if (((LocalTargetInfo)(ref target)).IsValid && num < GetRangeForPawn() && num > def.minRange && ((targetParams.canTargetLocations && targetParams.CanTarget(new TargetInfo(((LocalTargetInfo)(ref target)).Cell, Caster.Map, false), (ITargetingSource)null)) || targetParams.CanTarget(((LocalTargetInfo)(ref target)).ToTargetInfo(Caster.Map), (ITargetingSource)null)))
		{
			if (!sightCheck)
			{
				return true;
			}
			if (GenSight.LineOfSight(((Thing)pawn).Position, ((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map))
			{
				return true;
			}
			List<IntVec3> list = new List<IntVec3>();
			ShootLeanUtility.LeanShootingSourcesFromTo(((Thing)pawn).Position, ((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map, list);
			if (GenCollection.Any<IntVec3>(list, (Predicate<IntVec3>)((IntVec3 ivc) => GenSight.LineOfSight(ivc, ((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map))))
			{
				return true;
			}
		}
		return false;
	}

	public virtual bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (CanHitTarget(target))
		{
			return AbilityModExtensions.All((AbilityExtension_AbilityMod x) => x.ValidateTarget(target, this, showMessages));
		}
		return false;
	}

	public virtual void DrawHighlight(LocalTargetInfo target)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		float rangeForPawn = GetRangeForPawn();
		if (!def.worldTargeting && GenRadial.MaxRadialPatternRadius > rangeForPawn && rangeForPawn >= 1f)
		{
			GenDraw.DrawRadiusRing(((Thing)pawn).Position, rangeForPawn, def.rangeRingColor, (Func<IntVec3, bool>)null);
		}
		if (((LocalTargetInfo)(ref target)).IsValid)
		{
			GenDraw.DrawTargetHighlight(target);
			float radiusForPawn = GetRadiusForPawn();
			if (GenRadial.MaxRadialPatternRadius > radiusForPawn && radiusForPawn >= 1f)
			{
				GenDraw.DrawRadiusRing(((LocalTargetInfo)(ref target)).Cell, radiusForPawn, def.radiusRingColor, (Func<IntVec3, bool>)null);
			}
			if (GenRadial.MaxRadialPatternRadius > def.minRadius && def.minRadius >= 1f)
			{
				GenDraw.DrawRadiusRing(((LocalTargetInfo)(ref target)).Cell, def.minRadius, def.radiusRingColor, (Func<IntVec3, bool>)null);
			}
		}
	}

	public virtual void OrderForceTarget(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		firstTarget = target;
		if (((LocalTargetInfo)(ref target)).Thing != null)
		{
			currentTargets[currentTargetingIndex] = GlobalTargetInfo.op_Implicit(((LocalTargetInfo)(ref target)).Thing);
		}
		else if (((GlobalTargetInfo)(ref currentTargets[currentTargetingIndex])).Map != null)
		{
			currentTargets[currentTargetingIndex] = new GlobalTargetInfo(((LocalTargetInfo)(ref target)).Cell, ((GlobalTargetInfo)(ref currentTargets[currentTargetingIndex])).Map, false);
		}
		else
		{
			currentTargets[currentTargetingIndex] = new GlobalTargetInfo(((LocalTargetInfo)(ref target)).Cell, Caster.Map, false);
		}
		DoTargeting();
	}

	public virtual void OnGUI(LocalTargetInfo target)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		GenUI.DrawMouseAttachment(MouseAttachment(((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(((Thing)pawn).Map)));
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			abilityModExtension.TargetingOnGUI(target, this);
		}
		DrawAttachmentExtraLabel(target);
	}

	public virtual string ExtraLabelMouseAttachment(LocalTargetInfo target)
	{
		return null;
	}

	protected void DrawAttachmentExtraLabel(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		string text = ExtraLabelMouseAttachment(target);
		if (!GenText.NullOrEmpty(text))
		{
			Widgets.MouseAttachedLabel(text, 0f, 0f, (Color?)null);
			return;
		}
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			text = abilityModExtension.ExtraLabelMouseAttachment(target, this);
			if (!GenText.NullOrEmpty(text))
			{
				Widgets.MouseAttachedLabel(text, 0f, 0f, (Color?)null);
				break;
			}
		}
	}

	protected virtual Texture2D MouseAttachment(GlobalTargetInfo target)
	{
		if (((GlobalTargetInfo)(ref target)).IsValid)
		{
			if ((Object)(object)UIIcon != (Object)(object)BaseContent.BadTex)
			{
				return UIIcon;
			}
			return TexCommand.Attack;
		}
		return TexCommand.CannotShoot;
	}

	public virtual bool ValidateTargetTile(GlobalTargetInfo target, bool showMessages = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return CanHitTargetTile(target);
	}

	public virtual bool CanHitTargetTile(GlobalTargetInfo target)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		foreach (AbilityExtension_AbilityMod abilityModExtension in AbilityModExtensions)
		{
			if (!abilityModExtension.ValidTile(target, this))
			{
				return false;
			}
		}
		float num = Find.World.grid.ApproxDistanceInTiles(((GlobalTargetInfo)(ref target)).Tile, Tile);
		if (((GlobalTargetInfo)(ref target)).IsValid && num < GetRangeForPawn())
		{
			return num > def.minRange;
		}
		return false;
	}

	public virtual void OnUpdateWorld()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		float rangeForPawn = GetRangeForPawn();
		if (rangeForPawn >= 1f)
		{
			GenDraw.DrawWorldRadiusRing(Tile, Mathf.RoundToInt(rangeForPawn), (Material)null);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	[UsedImplicitly]
	private static void GiveAbility()
	{
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Expected O, but got Unknown
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		List<DebugMenuOption> list = new List<DebugMenuOption>();
		foreach (AbilityDef allDef in DefDatabase<AbilityDef>.AllDefs)
		{
			AbilityDef abilityDef = allDef;
			list.Add(new DebugMenuOption($"{((abilityDef.requiredHediff != null) ? $"{((Def)abilityDef.requiredHediff.hediffDef).LabelCap} ({abilityDef.requiredHediff.minimumLevel}): " : string.Empty)}{((Def)abilityDef).LabelCap}", (DebugMenuOptionMode)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item in (from t in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell())
					where t is Pawn
					select t).Cast<Pawn>())
				{
					CompAbilities compAbilities = ThingCompUtility.TryGetComp<CompAbilities>((Thing)(object)item);
					if (compAbilities != null)
					{
						compAbilities.GiveAbility(abilityDef);
						DebugActionsUtility.DustPuffFrom((Thing)(object)item);
					}
				}
			}));
		}
		Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list, (string)null));
	}
}
