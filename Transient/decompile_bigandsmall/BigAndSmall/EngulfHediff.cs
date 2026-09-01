using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using BigAndSmall.DeathActionInner;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class EngulfHediff : HediffWithComps, IThingHolder
{
	public bool canEject = true;

	public float internalBaseDamage = 10f;

	public float selfDamageMultiplier = 0.2f;

	public Hediff enchumberanceHediff;

	public float baseCapacity = 1f;

	public DamageDef damageDef;

	public const float globalDamageMultiplier = 0.7f;

	public float bodyPartsRegeneratedPerDay;

	public bool alliesAttackBack = true;

	public bool dealsDamage = true;

	public float healPerDay = -1f;

	public float regularHealingMultiplier = -1f;

	public bool healsScars;

	public bool canHealBrain;

	public const int tickRate = 530;

	[CompilerGenerated]
	private float? _003CFoodFallRate_003Ek__BackingField;

	public ThingOwner innerContainer;

	private int countDownToRegenerate;

	private float? FoodFallRate
	{
		get
		{
			float valueOrDefault = _003CFoodFallRate_003Ek__BackingField.GetValueOrDefault();
			float value;
			if (!_003CFoodFallRate_003Ek__BackingField.HasValue)
			{
				valueOrDefault = GetFoodFallRate();
				_003CFoodFallRate_003Ek__BackingField = valueOrDefault;
				value = valueOrDefault;
			}
			else
			{
				value = valueOrDefault;
			}
			return value;
		}
		[CompilerGenerated]
		set
		{
			_003CFoodFallRate_003Ek__BackingField = value;
		}
	}

	public float MaxCapacity => baseCapacity * PowScale(((Hediff)this).pawn.BodySize);

	public float Fullness => TotalMass / MaxCapacity;

	public bool HealsInner
	{
		get
		{
			if (!((double)healPerDay > -0.5))
			{
				return regularHealingMultiplier > -0.5f;
			}
			return true;
		}
	}

	public float TotalMass => ((IEnumerable<Thing>)innerContainer).Where((Thing x) => x is Pawn).Sum((Thing x) => PowScale(((Pawn)x).BodySize)) + ((IEnumerable<Thing>)innerContainer).Where((Thing x) => x is Corpse).Sum((Thing x) => PowScale(((Corpse)x).InnerPawn.BodySize * 0.5f));

	public Hediff EnchumberanceHediff
	{
		get
		{
			if (enchumberanceHediff == null)
			{
				enchumberanceHediff = GetEnchumberedHediff();
				return enchumberanceHediff;
			}
			return enchumberanceHediff;
		}
		set
		{
			enchumberanceHediff = value;
		}
	}

	public IThingHolder ParentHolder => (IThingHolder)(object)((Hediff)this).pawn;

	public bool HasAnyContents => innerContainer.Count > 0;

	public override string LabelInBrackets
	{
		get
		{
			try
			{
				return GenText.ToStringPercent(Fullness);
			}
			catch
			{
				return "FULLNESS CALCULATION FAILED";
			}
		}
	}

	private float GetFoodFallRate()
	{
		return ((Hediff)this).pawn.needs.food.FoodFallPerTickAssumingCategory((HungerCategory)1, true);
	}

	public static float PowScale(float bodySize)
	{
		return Mathf.Pow(bodySize, 1.4f);
	}

	public void GetChildHolders(List<IThingHolder> outChildren)
	{
		ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, (IList<Thing>)GetDirectlyHeldThings());
	}

	public override void PostAdd(DamageInfo? dinfo)
	{
		((HediffWithComps)this).PostAdd(dinfo);
		innerContainer = (ThingOwner)(object)new ThingOwner<Thing>((IThingHolder)(object)this, false, (LookMode)2, true);
	}

	public ThingOwner GetDirectlyHeldThings()
	{
		return innerContainer;
	}

	public bool Engulf(Thing thing)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		if (!thing.Spawned)
		{
			return false;
		}
		thing.DeSpawnOrDeselect((DestroyMode)0);
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null && val.IsColonist)
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_EngulfedColonist", NamedArgument.op_Implicit(((Entity)((Hediff)this).pawn).LabelShort), NamedArgument.op_Implicit(((Entity)val).LabelShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.NegativeHealthEvent, true);
		}
		bool result;
		if (thing.holdingOwner != null)
		{
			thing.holdingOwner.TryTransferToContainer(thing, innerContainer, thing.stackCount, true);
			result = true;
		}
		else
		{
			result = innerContainer.TryAdd(thing, true);
		}
		EnchumberanceHediff.Severity = Fullness;
		FoodFallRate = GetFoodFallRate();
		return result;
	}

	public Hediff GetEnchumberedHediff()
	{
		HediffDef namedSilentFail = DefDatabase<HediffDef>.GetNamedSilentFail("BS_EngulfedEnchumberance");
		if (namedSilentFail == null)
		{
			Log.Error("Could not find hediff with name BS_EngulfedEnchumberance");
			return null;
		}
		if (((Hediff)this).pawn.health.hediffSet.HasHediff(namedSilentFail, false))
		{
			enchumberanceHediff = ((Hediff)this).pawn.health.hediffSet.GetFirstHediffOfDef(namedSilentFail, false);
		}
		else
		{
			((Hediff)this).pawn.health.AddHediff(namedSilentFail, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			enchumberanceHediff = ((Hediff)this).pawn.health.hediffSet.GetFirstHediffOfDef(namedSilentFail, false);
		}
		return enchumberanceHediff;
	}

	public override string GetTooltip(Pawn pawn, bool showHediffsDebugInfo)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		string tooltip = ((Hediff)this).GetTooltip(pawn, showHediffsDebugInfo);
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(tooltip);
		stringBuilder.AppendLine();
		stringBuilder.AppendLine();
		stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("BS_EngulfedContents")));
		foreach (Thing item in (IEnumerable<Thing>)innerContainer)
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val != null)
			{
				float summaryHealthPercent = val.health.summaryHealth.SummaryHealthPercent;
				stringBuilder.AppendLine(string.Format("{0} {1:f0}% {2}", ((Entity)item).LabelCap, summaryHealthPercent * 100f, val.Downed ? string.Format(", {0}", Translator.Translate("DownedLower")) : ""));
			}
			else
			{
				stringBuilder.AppendLine($"{((Entity)item).LabelCap} {(float)item.HitPoints / (float)item.MaxHitPoints * 100f:f0}%");
			}
		}
		return GenText.TrimEndNewlines(stringBuilder.ToString());
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		((HediffWithComps)this).Notify_PawnDied(dinfo, culprit);
		IList<Thing> list = (IList<Thing>)innerContainer;
		for (int num = list.Count - 1; num >= 0; num--)
		{
			Piloted.TryEjectFromPawn(list[num], ((Hediff)this).pawn);
		}
	}

	public override void PostRemoved()
	{
		((HediffWithComps)this).PostRemoved();
		IList<Thing> list = (IList<Thing>)innerContainer;
		for (int num = list.Count - 1; num >= 0; num--)
		{
			Piloted.TryEjectFromPawn(list[num], ((Hediff)this).pawn);
		}
		try
		{
			((Hediff)this).pawn.health.RemoveHediff(EnchumberanceHediff);
		}
		catch
		{
		}
	}

	public override void Tick()
	{
		//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_04bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0487: Unknown result type (might be due to invalid IL or missing references)
		((Hediff)this).Tick();
		if (Find.TickManager.TicksGame % 530 == 0)
		{
			if (((IEnumerable<Thing>)innerContainer).Count() == 0)
			{
				return;
			}
			if (damageDef == null)
			{
				damageDef = DefDatabase<DamageDef>.GetNamed("BS_AcidDmgDirectQuiet", true);
				if (damageDef == null)
				{
					damageDef = DefDatabase<DamageDef>.GetNamed("AcidBurn", true);
				}
			}
			float num = 1f;
			if (((Hediff)this).pawn.health.capacities.CapableOf(BSDefs.Metabolism))
			{
				num = ((Hediff)this).pawn.health.capacities.GetLevel(BSDefs.Metabolism);
				if (num > 1f)
				{
					num += (num - 1f) * 3f;
				}
			}
			bool num2 = ((Hediff)this).pawn.health.Downed && ((Hediff)this).pawn.IsPrisonerOfColony;
			Pawn pawn = ((Hediff)this).pawn;
			int num3;
			if (pawn == null)
			{
				num3 = 0;
			}
			else
			{
				Pawn_HealthTracker health = pawn.health;
				float? obj;
				if (health == null)
				{
					obj = null;
				}
				else
				{
					HediffSet hediffSet = health.hediffSet;
					obj = ((hediffSet != null) ? new float?(hediffSet.PainTotal) : ((float?)null));
				}
				num3 = ((obj > 0.5f) ? 1 : 0);
			}
			bool flag = (byte)num3 != 0;
			bool flag2 = true;
			bool flag3 = true;
			BodyPartRecord val = GenCollection.FirstOrDefault<BodyPartRecord>(((Hediff)this).pawn.RaceProps.body.AllParts, (Predicate<BodyPartRecord>)((BodyPartRecord x) => ((Def)x.def).defName.Contains("stomach", StringComparison.OrdinalIgnoreCase)));
			if (val == null)
			{
				val = GenCollection.FirstOrDefault<BodyPartRecord>(((Hediff)this).pawn.RaceProps.body.AllParts, (Predicate<BodyPartRecord>)((BodyPartRecord x) => x.def.tags?.Contains(BodyPartTagDefOf.MetabolismSource) ?? false));
			}
			BodyPartRecord corePart = ((Hediff)this).pawn.RaceProps.body.corePart;
			if (val == null)
			{
				val = corePart;
			}
			else
			{
				if (((Hediff)this).pawn.health.hediffSet.GetPartHealth(val) < val.def.GetMaxHealth(((Hediff)this).pawn) * 0.3f)
				{
					val = corePart;
					flag2 = false;
				}
				if (corePart != null && ((Hediff)this).pawn.health.hediffSet.GetPartHealth(corePart) < corePart.def.GetMaxHealth(((Hediff)this).pawn) * 0.3f)
				{
					flag3 = false;
				}
			}
			if (num2 || ((flag || num < 0.51f || !flag2) && canEject) || !flag3 || Fullness > 1.4f)
			{
				((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
				((Hediff)this).pawn.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Vomit), (JobCondition)16, (ThinkNode)null, true, true, (ThinkTreeDef)null, (JobTag?)null, false, false, (bool?)null, false, true, false);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_EngulfedVomit", NamedArgument.op_Implicit(((Entity)((Hediff)this).pawn).LabelShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.NegativeHealthEvent, true);
				return;
			}
			bool flag4 = ((IEnumerable<Thing>)innerContainer).Any((Thing x) => x is Corpse);
			bool flag5 = ((IEnumerable<Thing>)innerContainer).Any((Thing x) => x is Pawn);
			if ((flag5 || flag4) && !HealsInner)
			{
				Need_Food food = ((Hediff)this).pawn.needs.food;
				((Need)food).CurLevel = ((Need)food).CurLevel + FoodFallRate.Value * 530f * 1.2f;
			}
			else if (flag5 && HealsInner)
			{
				Need_Food food2 = ((Hediff)this).pawn.needs.food;
				((Need)food2).CurLevel = ((Need)food2).CurLevel + (0f - FoodFallRate.Value) * 530f * -0.5f;
			}
			List<Thing> list = new List<Thing>();
			IList<Thing> list2 = (IList<Thing>)innerContainer;
			for (int num4 = list2.Count - 1; num4 >= 0; num4--)
			{
				Thing val2 = list2[num4];
				Pawn val3 = (Pawn)(object)((val2 is Pawn) ? val2 : null);
				if (val3 != null)
				{
					if (TryKill(num, val, val2, val3))
					{
						continue;
					}
					HandleEffectToInner(num, flag2, val2, val3);
					HandleEffectFromInner(val, val3);
				}
				else if (!val2.def.destroyable || !val2.def.useHitPoints)
				{
					list.Add(val2);
				}
				else if (val2 is Corpse)
				{
					val2.TakeDamage(new DamageInfo(damageDef, 5f * num, 100f, -1f, (Thing)(object)((Hediff)this).pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, val2, true, false, (QualityCategory)2, true, false));
				}
				else
				{
					val2.TakeDamage(new DamageInfo(damageDef, 1f * num, 100f, -1f, (Thing)(object)((Hediff)this).pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, val2, true, false, (QualityCategory)2, true, false));
				}
				if (val2.HitPoints < 20)
				{
					Corpse val4 = (Corpse)(object)((val2 is Corpse) ? val2 : null);
					if (val4 != null)
					{
						DestroyCorpse(val4);
					}
				}
			}
			for (int num5 = list.Count - 1; num5 >= 0; num5--)
			{
				innerContainer.Remove(list[num5]);
				if (((Thing)((Hediff)this).pawn).Spawned)
				{
					Piloted.TryEjectFromPawn(list[num5], ((Hediff)this).pawn);
				}
			}
		}
		EnchumberanceHediff.Severity = Fullness;
	}

	private void HandleEffectFromInner(BodyPartRecord stomach, Pawn innerPawn)
	{
		if (innerPawn.DeadOrDowned || innerPawn.health.ShouldBeDead() || innerPawn.health.ShouldBeDowned())
		{
			return;
		}
		try
		{
			bool flag = ((Thing)innerPawn).Faction == null || ((Thing)((Hediff)this).pawn).Faction == null || (((Thing)((Hediff)this).pawn).Faction != null && FactionUtility.HostileTo(((Thing)((Hediff)this).pawn).Faction, ((Thing)innerPawn).Faction) && !innerPawn.IsSlaveOfColony && !innerPawn.IsPrisonerOfColony);
			if (alliesAttackBack || flag)
			{
				AttackPossessor(stomach, innerPawn);
			}
			if (innerPawn.Dead)
			{
				((Hediff)this).Severity = ((Hediff)this).Severity + 0.2f;
			}
		}
		catch (Exception ex)
		{
			Log.ErrorOnce("Error in BS_HediffComp_Engulfed.CompPostTick():\n" + ex.Message + "\n" + ex.StackTrace, 983452345);
		}
	}

	private void HandleEffectToInner(float digestionEffiency, bool stomachIntact, Thing thing, Pawn innerPawn)
	{
		if (dealsDamage)
		{
			AttackInnerThing(digestionEffiency, stomachIntact, thing);
		}
		else if (HealsInner)
		{
			HealInner(innerPawn);
		}
	}

	private bool TryKill(float digestionEffiency, BodyPartRecord stomach, Thing thing, Pawn innerPawn)
	{
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		if (SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead(innerPawn) || (!innerPawn.IsColonist && innerPawn.health.summaryHealth.SummaryHealthPercent < 0.1f))
		{
			((Thing)innerPawn).Kill((DamageInfo?)new DamageInfo(damageDef, 999f * digestionEffiency, 100f, -1f, (Thing)(object)((Hediff)this).pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, thing, true, false, (QualityCategory)2, true, false), (Hediff)null);
			DeathActionWorker deathActionWorker = innerPawn.RaceProps.DeathActionWorker;
			if (deathActionWorker != null && !innerPawn.IsShambler)
			{
				if (deathActionWorker is DeathActionWorker_BigExplosion)
				{
					InnerDeathWorkerHelper.BigExplosion(innerPawn.Corpse, ((Hediff)this).pawn, stomach);
				}
				else if (((object)deathActionWorker).ToString().ToLower().Contains("explosion"))
				{
					InnerDeathWorkerHelper.SmallExplosion(innerPawn.Corpse, ((Hediff)this).pawn, stomach);
				}
			}
			return true;
		}
		return false;
	}

	private void HealInner(Pawn innerPawn)
	{
		float num = healPerDay * 530f / 60000f;
		num = ((innerPawn.BodySize > 1f) ? innerPawn.HealthScale : 1f) * ((Hediff)this).pawn.BodySize;
		float num2 = StatExtension.GetStatValue((Thing)(object)innerPawn, StatDefOf.InjuryHealingFactor, true, -1);
		if (regularHealingMultiplier > 1f)
		{
			num2 *= regularHealingMultiplier;
		}
		num += innerPawn.HealthScale * 0.01f * num2 * regularHealingMultiplier;
		HediffSet hediffSet = innerPawn.health.hediffSet;
		foreach (Hediff item in hediffSet.hediffs.Where((Hediff x) => (x is Hediff_Injury || x is Hediff_MissingPart) && x.TendableNow(true)))
		{
			item.Tended(0.15f, 1f, 1);
		}
		List<Hediff> list = hediffSet.hediffs.Where((Hediff x) => x is Hediff_Injury && (!HediffUtility.IsPermanent(x) || healsScars)).ToList();
		if (!canHealBrain)
		{
			BodyPartRecord brain = hediffSet.GetBrain();
			list = list.Where((Hediff x) => !(((x == null) ? null : ((Def)x.Part?.def).defName) == ((Def)brain?.def).defName) || !HediffUtility.IsPermanent(x)).ToList();
		}
		if (list.Count > 0)
		{
			GenCollection.RandomElement<Hediff>((IEnumerable<Hediff>)list).Heal(num);
		}
		List<Hediff> list2 = hediffSet.hediffs.Where((Hediff x) => x is Hediff_MissingPart).ToList();
		if (list2.Count > 0)
		{
			countDownToRegenerate++;
			if ((double)bodyPartsRegeneratedPerDay > 0.001 && (float)countDownToRegenerate > 113f / bodyPartsRegeneratedPerDay)
			{
				Hediff val = GenCollection.RandomElement<Hediff>((IEnumerable<Hediff>)list2);
				innerPawn.health.RestorePart(val.Part, (Hediff)null, true);
				countDownToRegenerate = 0;
			}
		}
	}

	public void DestroyCorpse(Corpse corpse)
	{
		ProcessCorpseDestruction(((Hediff)this).pawn, corpse.InnerPawn);
		if (((corpse == null) ? null : corpse.InnerPawn?.inventory?.innerContainer) != null)
		{
			List<Thing> list = ((IEnumerable<Thing>)corpse.InnerPawn.inventory.innerContainer).ToList();
			for (int num = list.Count - 1; num >= 0; num--)
			{
				Thing thing = list[num];
				Engulf(thing);
			}
			((ThingOwner)corpse.InnerPawn.inventory.innerContainer).Clear();
		}
		object obj;
		if (corpse == null)
		{
			obj = null;
		}
		else
		{
			Pawn innerPawn = corpse.InnerPawn;
			if (innerPawn == null)
			{
				obj = null;
			}
			else
			{
				Pawn_ApparelTracker apparel = innerPawn.apparel;
				obj = ((apparel != null) ? apparel.WornApparel : null);
			}
		}
		if (obj != null)
		{
			List<Apparel> wornApparel = corpse.InnerPawn.apparel.WornApparel;
			for (int num2 = wornApparel.Count - 1; num2 >= 0; num2--)
			{
				Apparel thing2 = wornApparel[num2];
				Engulf((Thing)(object)thing2);
			}
		}
		object obj2;
		if (corpse == null)
		{
			obj2 = null;
		}
		else
		{
			Pawn innerPawn2 = corpse.InnerPawn;
			if (innerPawn2 == null)
			{
				obj2 = null;
			}
			else
			{
				Pawn_EquipmentTracker equipment = innerPawn2.equipment;
				obj2 = ((equipment != null) ? equipment.AllEquipmentListForReading : null);
			}
		}
		if (obj2 != null)
		{
			List<ThingWithComps> list2 = corpse.InnerPawn.equipment.AllEquipmentListForReading.ToList();
			for (int num3 = list2.Count - 1; num3 >= 0; num3--)
			{
				ThingWithComps thing3 = list2[num3];
				Engulf((Thing)(object)thing3);
			}
		}
		((Thing)corpse).Destroy((DestroyMode)0);
	}

	private void AttackInnerThing(float digestionEffiency, bool stomachIntact, Thing thing)
	{
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		DamageDef crush = damageDef;
		if (Rand.Chance(0.2f))
		{
			crush = DamageDefOf.Crush;
		}
		bool flag = true;
		float num = internalBaseDamage * digestionEffiency * 0.7f;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			if (val.ageTracker.CurLifeStageIndex == 0)
			{
				flag = false;
			}
			float num2 = ((Hediff)this).pawn.BodySize / val.BodySize;
			if (num2 > 2f)
			{
				float num3 = (num2 - 1f) / 2f + 1f;
				num *= num3;
			}
		}
		if (!stomachIntact)
		{
			DamageDef obj = crush;
			float num4 = num * 0.66f;
			bool flag2 = flag;
			thing.TakeDamage(new DamageInfo(obj, num4, 100f, -1f, (Thing)(object)((Hediff)this).pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, thing, flag2, false, (QualityCategory)2, true, false));
		}
		else
		{
			DamageDef obj2 = crush;
			float num5 = num;
			bool flag2 = flag;
			thing.TakeDamage(new DamageInfo(obj2, num5, 100f, -1f, (Thing)(object)((Hediff)this).pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, thing, flag2, false, (QualityCategory)2, true, false));
		}
	}

	private void AttackPossessor(BodyPartRecord targetPart, Pawn innerPawn)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		VerbEntry val = GenCollection.MaxBy<VerbEntry, float>((IEnumerable<VerbEntry>)innerPawn.meleeVerbs.GetUpdatedAvailableVerbsList(false), (Func<VerbEntry, float>)((VerbEntry x) => x.verb.verbProps.AdjustedMeleeDamageAmount(x.verb, innerPawn)));
		VerbEntry val2 = GenCollection.RandomElement<VerbEntry>((IEnumerable<VerbEntry>)innerPawn.meleeVerbs.GetUpdatedAvailableVerbsList(false));
		float num = 1f;
		Pawn obj = innerPawn;
		if (obj != null)
		{
			Pawn_SkillTracker skills = obj.skills;
			int? obj2;
			if (skills == null)
			{
				obj2 = null;
			}
			else
			{
				SkillRecord skill = skills.GetSkill(SkillDefOf.Melee);
				obj2 = ((skill != null) ? new int?(skill.Level) : ((int?)null));
			}
			if (obj2 >= 0)
			{
				int level = innerPawn.skills.GetSkill(SkillDefOf.Melee).Level;
				if (level <= 4)
				{
					num = 0.75f;
				}
				else if (level <= 7)
				{
					num = 0.85f;
				}
				else if (level <= 10)
				{
					num = 1f;
				}
				else if (level <= 14)
				{
					num = 1.15f;
				}
				else if (level <= 17)
				{
					num = 1.3f;
				}
				else if (level <= 20)
				{
					num = 1.5f;
				}
			}
		}
		if (Rand.Chance(0.6f))
		{
			val = val2;
		}
		float num2 = val.verb.verbProps.AdjustedMeleeDamageAmount(val.verb, innerPawn);
		DamageDef meleeDamageDef = val.verb.verbProps.meleeDamageDef;
		bool canInterruptJobs = meleeDamageDef.canInterruptJobs;
		bool makesBlood = meleeDamageDef.makesBlood;
		float num3 = targetPart.def.GetMaxHealth(((Hediff)this).pawn) / StatExtension.GetStatValue((Thing)(object)((Hediff)this).pawn, StatDefOf.IncomingDamageFactor, true, -1) / 16f;
		if (num2 < num3)
		{
			if (!Rand.Chance(num2 / num3))
			{
				return;
			}
			num2 = num3;
		}
		float num4 = HumanoidPawnScaler.GetCacheUltraSpeed(((Hediff)this).pawn)?.internalDamageDivisor ?? 1f;
		meleeDamageDef.canInterruptJobs = false;
		meleeDamageDef.makesBlood = false;
		Pawn pawn = ((Hediff)this).pawn;
		float num5 = num2 * selfDamageMultiplier * num * 0.7f / num4;
		Thing pawn2 = (Thing)(object)((Hediff)this).pawn;
		((Thing)pawn).TakeDamage(new DamageInfo(meleeDamageDef, num5, 500f, -1f, (Thing)(object)innerPawn, targetPart, (ThingDef)null, (SourceCategory)0, pawn2, false, false, (QualityCategory)2, true, false));
		meleeDamageDef.canInterruptJobs = canInterruptJobs;
		meleeDamageDef.makesBlood = makesBlood;
	}

	protected virtual void ProcessCorpseDestruction(Pawn attacker, Pawn innerPawn)
	{
		if (attacker.needs?.food != null && innerPawn != null)
		{
			_ = innerPawn.BodySize;
			Need_Food food = attacker.needs.food;
			((Need)food).CurLevel = ((Need)food).CurLevel + 6f * innerPawn.BodySize;
		}
		try
		{
			GetEatenCorpseMeatThoughts(attacker, innerPawn);
		}
		catch (Exception ex)
		{
			Log.Warning("Error adding thought after destroying corpse: " + ex.Message + "\n" + ex.StackTrace);
		}
		Pawn_NeedsTracker needs = attacker.needs;
		Need_KillThirst val = ((needs != null) ? needs.TryGetNeed<Need_KillThirst>() : null);
		if (val != null)
		{
			((Need)val).CurLevelPercentage = 1f;
		}
	}

	public static void GetEatenCorpseMeatThoughts(Pawn attacker, Pawn target)
	{
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Expected O, but got Unknown
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Expected O, but got Unknown
		if (target.RaceProps.Humanlike)
		{
			bool? obj;
			if (attacker == null)
			{
				obj = null;
			}
			else
			{
				Pawn_StoryTracker story = attacker.story;
				if (story == null)
				{
					obj = null;
				}
				else
				{
					TraitSet traits = story.traits;
					obj = ((traits != null) ? new bool?(traits.HasTrait(BSDefs.Cannibal)) : ((bool?)null));
				}
			}
			bool? flag = obj;
			if (flag == true)
			{
				Thought_Memory val = (Thought_Memory)ThoughtMaker.MakeThought(BSDefs.AteHumanlikeMeatDirectCannibal);
				attacker.mindState.lastHumanMeatIngestedTick = Find.TickManager.TicksGame;
				if (attacker != null)
				{
					Pawn_NeedsTracker needs = attacker.needs;
					if (needs != null)
					{
						Need_Mood mood = needs.mood;
						if (mood != null)
						{
							ThoughtHandler thoughts = mood.thoughts;
							if (thoughts != null)
							{
								MemoryThoughtHandler memories = thoughts.memories;
								if (memories != null)
								{
									memories.TryGainMemory(val, (Pawn)null);
								}
							}
						}
					}
				}
			}
			else
			{
				object obj2;
				if (attacker == null)
				{
					obj2 = null;
				}
				else
				{
					Pawn_IdeoTracker ideo = attacker.ideo;
					obj2 = ((ideo != null) ? ideo.Ideo : null);
				}
				Ideo val2 = (Ideo)obj2;
				if (val2 != null)
				{
					if (val2.HasPrecept(PreceptDefOf.Cannibalism_Preferred) || val2.HasPrecept(PreceptDefOf.Cannibalism_RequiredRavenous) || val2.HasPrecept(PreceptDefOf.Cannibalism_RequiredStrong) || val2.HasPrecept(BSDefs.Cannibalism_Acceptable))
					{
						attacker.mindState.lastHumanMeatIngestedTick = Find.TickManager.TicksGame;
					}
				}
				else
				{
					Thought_Memory val = (Thought_Memory)ThoughtMaker.MakeThought(BSDefs.AteHumanlikeMeatDirect);
					if (attacker != null)
					{
						Pawn_NeedsTracker needs2 = attacker.needs;
						if (needs2 != null)
						{
							Need_Mood mood2 = needs2.mood;
							if (mood2 != null)
							{
								ThoughtHandler thoughts2 = mood2.thoughts;
								if (thoughts2 != null)
								{
									MemoryThoughtHandler memories2 = thoughts2.memories;
									if (memories2 != null)
									{
										memories2.TryGainMemory(val, (Pawn)null);
									}
								}
							}
						}
					}
				}
			}
		}
		foreach (Gene allActiveGene in attacker.GetAllActiveGenes())
		{
			allActiveGene.Notify_IngestedThing((Thing)(object)target, 1);
		}
	}

	public override void ExposeData()
	{
		((HediffWithComps)this).ExposeData();
		Scribe_Deep.Look<ThingOwner>(ref innerContainer, "innerContainer", new object[1] { this });
		Scribe_Values.Look<float>(ref selfDamageMultiplier, "selfDamageMultiplier", 1f, false);
		Scribe_Values.Look<float>(ref internalBaseDamage, "internalBaseDamage", 1f, false);
		Scribe_Values.Look<bool>(ref canEject, "canEject", true, false);
		Scribe_Values.Look<float>(ref baseCapacity, "maxCapacity", 1f, false);
		Scribe_Values.Look<bool>(ref alliesAttackBack, "alliesAttackBack", true, false);
		Scribe_Values.Look<bool>(ref dealsDamage, "dealsDamage", true, false);
		Scribe_Values.Look<float>(ref healPerDay, "healPerDay", -1f, false);
		Scribe_Values.Look<float>(ref regularHealingMultiplier, "regularHealingMultiplier", -1f, false);
		Scribe_Values.Look<bool>(ref healsScars, "healsScars", false, false);
		Scribe_Values.Look<bool>(ref canHealBrain, "canHealBrain", false, false);
		Scribe_Values.Look<float>(ref bodyPartsRegeneratedPerDay, "bodyPartsRegeneratedPerDay", 0f, false);
		Scribe_Defs.Look<DamageDef>(ref damageDef, "damageDef");
	}
}
