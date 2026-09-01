using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace BigAndSmall;

public class JobGiver_AutoCombat : JobGiver_AIFightEnemy
{
	public DraftedActionData actionData;

	public bool draftedOnly = true;

	public List<AbilityDef> blacklist = new List<AbilityDef>();

	public bool Hunt => actionData.hunt;

	protected override bool OnlyUseAbilityVerbs => !actionData.hunt;

	protected override bool OnlyUseRangedSearch => false;

	public override ThinkNode DeepCopy(bool resolve = true)
	{
		return (ThinkNode)(object)(JobGiver_AutoCombat)(object)((JobGiver_AIFightEnemy)this).DeepCopy(resolve);
	}

	protected override bool TryFindShootingPosition(Pawn pawn, out IntVec3 dest, Verb verbToUse = null)
	{
		return TryFindShootinPositionInner(pawn, out dest, verbToUse);
	}

	public bool ValidUser(Pawn pawn)
	{
		if (pawn == null)
		{
			return false;
		}
		if (draftedOnly && !pawn.Drafted)
		{
			return false;
		}
		return true;
	}

	protected bool TryFindShootinPositionInner(Pawn pawn, out IntVec3 dest, Verb verbToUse, bool requestNewPos = false)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		dest = ((Thing)pawn).Position;
		if (Hunt)
		{
			Thing enemyTarget = pawn.mindState.enemyTarget;
			CastPositionRequest val = default(CastPositionRequest);
			val.caster = pawn;
			val.target = enemyTarget;
			val.wantCoverFromTarget = actionData.takeCover;
			val.preferredCastPosition = (requestNewPos ? ((IntVec3?)null) : new IntVec3?(((Thing)pawn).Position));
			if (verbToUse == null && CanTargetWithAbillities(pawn, enemyTarget, out var pickedAbility))
			{
				val.verb = pickedAbility.verb;
				val.maxRangeFromTarget = pickedAbility.verb.verbProps.range - 0.5f;
				return CastPositionFinder.TryFindCastPosition(val, ref dest);
			}
			val.verb = verbToUse;
			val.maxRangeFromTarget = verbToUse.verbProps.range - 0.5f;
			return CastPositionFinder.TryFindCastPosition(val, ref dest);
		}
		return true;
	}

	protected override bool ExtraTargetValidator(Pawn pawn, Thing target)
	{
		if (!ValidUser(pawn))
		{
			return false;
		}
		if (((JobGiver_AIFightEnemy)this).ExtraTargetValidator(pawn, target))
		{
			Ability pickedAbility;
			if (!Hunt)
			{
				return CanTargetWithAbillities(pawn, target, out pickedAbility);
			}
			return true;
		}
		return false;
	}

	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		if (!ValidUser(pawn))
		{
			return null;
		}
		actionData = DraftedActionHolder.GetData(pawn);
		if (!Hunt)
		{
			if (!GenCollection.Empty<AbilityDef>(actionData.autocastAbilities))
			{
				Pawn_AbilityTracker abilities = pawn.abilities;
				if (abilities == null || GenList.NullOrEmpty<Ability>((IList<Ability>)abilities.abilities))
				{
					if (pawn.abilities.abilities.All((Ability ability) => !AcceptanceReport.op_Implicit(ability.CanCast) || blacklist.Contains(ability.def)))
					{
						return GetWaitForTimeJob(pawn, 100);
					}
					goto IL_0076;
				}
			}
			return null;
		}
		goto IL_0076;
		IL_0076:
		HostilityResponseMode hostilityResponse = pawn.playerSettings.hostilityResponse;
		pawn.playerSettings.hostilityResponse = (HostilityResponseMode)1;
		Job val = GiveDraftedHuntJob(pawn);
		pawn.playerSettings.hostilityResponse = hostilityResponse;
		if (val != null)
		{
			val.checkOverrideOnExpire = true;
			return val;
		}
		return GetWaitForTimeJob(pawn, 100);
	}

	protected static Job GetWaitForTimeJob(Pawn pawn, int ticks)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		Job obj = JobMaker.MakeJob(JobDefOf.Wait_Combat, LocalTargetInfo.op_Implicit(((Thing)pawn).Position));
		obj.expiryInterval = ticks;
		obj.checkOverrideOnExpire = true;
		return obj;
	}

	protected override bool ShouldLoseTarget(Pawn pawn)
	{
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		Thing enemyTarget = pawn.mindState.enemyTarget;
		float num = (actionData.fullAIControl ? 999f : base.targetKeepRadius);
		if (enemyTarget.Destroyed || Find.TickManager.TicksGame - pawn.mindState.lastEngageTargetTick > ((JobGiver_AIFightEnemy)this).TicksSinceEngageToLoseTarget)
		{
			return true;
		}
		Thing obj = ((enemyTarget is IAttackTarget) ? enemyTarget : null);
		if (obj == null || !((IAttackTarget)obj).ThreatDisabled((IAttackTargetSearcher)(object)pawn))
		{
			Pawn val = (Pawn)(object)((enemyTarget is Pawn) ? enemyTarget : null);
			if (val == null || !val.DeadOrDowned)
			{
				if (actionData.fullAIControl)
				{
					if (!ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(enemyTarget), (PathEndMode)2, (Danger)3, true, false, (TraverseMode)0))
					{
						return true;
					}
					goto IL_00ce;
				}
				if (ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(enemyTarget), (PathEndMode)2, (Danger)3, false, false, (TraverseMode)0))
				{
					IntVec3 val2 = ((Thing)pawn).Position - enemyTarget.Position;
					if ((float)((IntVec3)(ref val2)).LengthHorizontalSquared > num * num)
					{
						goto IL_00ce;
					}
				}
				return true;
			}
		}
		return true;
		IL_00ce:
		if (!Hunt || !CanTargetWithAbillities(pawn, pawn.mindState.enemyTarget, out var _))
		{
			return true;
		}
		return false;
	}

	protected bool CanTargetWithAbillities(Pawn pawn, Thing target, out Ability pickedAbility)
	{
		pickedAbility = null;
		if (!ValidUser(pawn) || pawn.abilities?.abilities == null)
		{
			return false;
		}
		foreach (Ability ability in pawn.abilities.abilities)
		{
			pickedAbility = CanTargetWithAbility(target, ability);
			if (pickedAbility != null)
			{
				return true;
			}
		}
		return false;
	}

	private Ability CanTargetWithAbility(Thing target, Ability ability)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		if (!AcceptanceReport.op_Implicit(ability.CanCast))
		{
			return null;
		}
		if (blacklist.Contains(ability.def))
		{
			return null;
		}
		if (!ability.def.verbProperties.targetParams.CanTarget(TargetInfo.op_Implicit(target), (ITargetingSource)null))
		{
			return null;
		}
		if (!ability.CanApplyOn(LocalTargetInfo.op_Implicit(target)))
		{
			return null;
		}
		if (ability.def.aiCanUse && !ability.AICanTargetNow(LocalTargetInfo.op_Implicit(target)))
		{
			return null;
		}
		bool aiCanUse = ability.def.aiCanUse;
		bool flag = false;
		try
		{
			ability.def.aiCanUse = true;
			flag = ability.AICanTargetNow(LocalTargetInfo.op_Implicit(target));
		}
		finally
		{
			ability.def.aiCanUse = aiCanUse;
		}
		if (flag)
		{
			return ability;
		}
		return null;
	}

	protected Job GiveDraftedHuntJob(Pawn pawn)
	{
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_025f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0248: Unknown result type (might be due to invalid IL or missing references)
		//IL_024d: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		((JobGiver_AIFightEnemy)this).UpdateEnemyTarget(pawn);
		Thing enemyTarget = pawn.mindState.enemyTarget;
		if (enemyTarget == null)
		{
			return null;
		}
		Pawn val = (Pawn)(object)((enemyTarget is Pawn) ? enemyTarget : null);
		if (val != null && (InvisibilityUtility.IsPsychologicallyInvisible(val) || val.DeadOrDowned))
		{
			return null;
		}
		Job abilityJob = GetAbilityJob(pawn, enemyTarget);
		if (abilityJob != null)
		{
			return abilityJob;
		}
		if (!Hunt)
		{
			return null;
		}
		Verb val2 = TryGetAttackVerb(pawn, enemyTarget);
		if (val2 == null)
		{
			return null;
		}
		IntVec3 val3;
		if (val2.verbProps.IsMeleeAttack)
		{
			if (!actionData.fullAIControl && !actionData.meleeCharge)
			{
				val3 = ((Thing)pawn).Position - enemyTarget.Position;
				if (((IntVec3)(ref val3)).LengthHorizontalSquared > 9)
				{
					return JobMaker.MakeJob(JobDefOf.Wait_Combat, 100, true);
				}
			}
			Job obj = ((JobGiver_AIFightEnemy)this).MeleeAttackJob(pawn, enemyTarget);
			obj.checkOverrideOnExpire = true;
			obj.expiryInterval = 100;
			obj.canBashDoors = actionData.fullAIControl;
			return obj;
		}
		bool takeCover = actionData.takeCover;
		float num = (takeCover ? 0.24f : 0f);
		CoverUtility.CalculateOverallBlockChance(LocalTargetInfo.op_Implicit((Thing)(object)pawn), enemyTarget.Position, ((Thing)pawn).Map);
		bool flag = CoverUtility.CalculateOverallBlockChance(LocalTargetInfo.op_Implicit((Thing)(object)pawn), enemyTarget.Position, ((Thing)pawn).Map) >= num;
		bool flag2 = GenGrid.Standable(((Thing)pawn).Position, ((Thing)pawn).Map) && ((Thing)pawn).Map.pawnDestinationReservationManager.CanReserve(((Thing)pawn).Position, pawn, pawn.Drafted);
		bool flag3 = val2.CanHitTarget(LocalTargetInfo.op_Implicit(enemyTarget));
		float range = val2.verbProps.range;
		val3 = ((Thing)pawn).Position - enemyTarget.Position;
		bool flag4 = (float)((IntVec3)(ref val3)).LengthHorizontalSquared < range * range;
		IntRange expiryInterval_ShooterSucceeded;
		if (flag && flag2 && flag3 && flag4)
		{
			JobDef wait_Combat = JobDefOf.Wait_Combat;
			expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
			return JobMaker.MakeJob(wait_Combat, ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange / 3, true);
		}
		IntVec3 val4 = default(IntVec3);
		if (!((JobGiver_AIFightEnemy)this).TryFindShootingPosition(pawn, ref val4, val2))
		{
			Job val5 = TryMeleeAttackJob(pawn, enemyTarget);
			if (val5 != null)
			{
				return val5;
			}
			return JobMaker.MakeJob(JobDefOf.Wait_Combat, 100, true);
		}
		if (val4 == ((Thing)pawn).Position)
		{
			if (takeCover && !flag)
			{
				if (TryFindShootinPositionInner(pawn, out var dest, val2, requestNewPos: true) && dest != ((Thing)pawn).Position)
				{
					return MakeGotoJob(dest);
				}
				Job val6 = TryMeleeAttackJob(pawn, enemyTarget);
				if (val6 != null)
				{
					return val6;
				}
			}
			JobDef wait_Combat2 = JobDefOf.Wait_Combat;
			expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
			return JobMaker.MakeJob(wait_Combat2, ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange / 3, true);
		}
		return MakeGotoJob(val4);
	}

	protected virtual Job TryMeleeAttackJob(Pawn pawn, Thing enemyTarget)
	{
		if (actionData.fullAIControl)
		{
			Job obj = ((JobGiver_AIFightEnemy)this).MeleeAttackJob(pawn, enemyTarget);
			obj.checkOverrideOnExpire = true;
			obj.expiryInterval = 100;
			obj.canBashDoors = true;
			obj.maxNumMeleeAttacks = 1;
			return obj;
		}
		return null;
	}

	protected static Job MakeGotoJob(IntVec3 shootingPos)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		Job obj = JobMaker.MakeJob(JobDefOf.Goto, LocalTargetInfo.op_Implicit(shootingPos));
		IntRange expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
		obj.expiryInterval = ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange / 3;
		obj.checkOverrideOnExpire = true;
		return obj;
	}

	protected override void UpdateEnemyTarget(Pawn pawn)
	{
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		Thing val = pawn.mindState.enemyTarget;
		if (val != null && ((JobGiver_AIFightEnemy)this).ShouldLoseTarget(pawn))
		{
			val = null;
		}
		if (val == null)
		{
			val = FindAttackTargetIfPossible(pawn);
			if (val != null)
			{
				Notify_EngagedTarget(pawn);
				Lord lord = LordUtility.GetLord(pawn);
				if (lord != null)
				{
					lord.Notify_PawnAcquiredTarget(pawn, val);
				}
			}
		}
		else
		{
			Thing val2 = FindAttackTargetIfPossible(pawn);
			if (val2 == null && !base.chaseTarget)
			{
				val = null;
			}
			else if (val2 != null && val2 != val)
			{
				Notify_EngagedTarget(pawn);
				val = val2;
			}
		}
		pawn.mindState.enemyTarget = val;
		Pawn val3;
		if ((val3 = (Pawn)(object)((val is Pawn) ? val : null)) != null && val.Faction == Faction.OfPlayerSilentFail)
		{
			IntVec3 position = ((Thing)pawn).Position;
			if (((IntVec3)(ref position)).InHorDistOf(val.Position, 40f) && !val3.IsShambler && !InvisibilityUtility.IsPsychologicallyInvisible(pawn))
			{
				Find.TickManager.slower.SignalForceNormalSpeed();
			}
		}
	}

	protected void Notify_EngagedTarget(Pawn pawn)
	{
		pawn.mindState.lastEngageTargetTick = Find.TickManager.TicksGame;
	}

	protected Thing FindAttackTargetIfPossible(Pawn pawn)
	{
		if (pawn.TryGetAttackVerb((Thing)null, true, false) == null)
		{
			return null;
		}
		if (actionData.fullAIControl)
		{
			return FindAttackTargetAnywhere(pawn);
		}
		return ((JobGiver_AIFightEnemy)this).FindAttackTarget(pawn);
	}

	public virtual Thing FindAttackTargetAnywhere(Pawn pawn)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Expected O, but got Unknown
		TargetScanFlags val = (TargetScanFlags)292;
		return (Thing)AttackTargetFinder.BestAttackTarget((IAttackTargetSearcher)(object)pawn, val, (Predicate<Thing>)IsGoodTarget, 0f, 900f, default(IntVec3), float.MaxValue, true, true, false, false);
	}

	public virtual bool IsGoodTarget(Thing thing)
	{
		if (!PlayerCanSeeThing(thing))
		{
			return false;
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null && !val.Downed)
		{
			return !InvisibilityUtility.IsPsychologicallyInvisible(val);
		}
		return false;
	}

	public static bool PlayerCanSeeThing(Thing thing)
	{
		if (!thing.Spawned)
		{
			return false;
		}
		if (thing.MapHeld != null && !GridsUtility.Fogged(thing))
		{
			return true;
		}
		return false;
	}

	public Verb TryGetAttackVerb(Pawn pawn, Thing target, bool allowManualCastWeapons = false, bool allowOnlyManualCastWeapons = false)
	{
		Verb val = DraftedActionData.TryGetVEFAbilityVerb(pawn, target);
		if (val != null)
		{
			return val;
		}
		if (allowManualCastWeapons)
		{
			Pawn_EquipmentTracker equipment = pawn.equipment;
			if (((equipment != null) ? equipment.Primary : null) != null && pawn.equipment.PrimaryEq.PrimaryVerb.Available() && pawn.equipment.PrimaryEq.PrimaryVerb.verbProps.onlyManualCast)
			{
				return pawn.equipment.PrimaryEq.PrimaryVerb;
			}
			if (allowManualCastWeapons && pawn.apparel != null && pawn.equipment.PrimaryEq.PrimaryVerb.verbProps.onlyManualCast)
			{
				Verb firstApparelVerb = pawn.apparel.FirstApparelVerb;
				if (firstApparelVerb != null && firstApparelVerb.Available())
				{
					return firstApparelVerb;
				}
			}
		}
		if (allowOnlyManualCastWeapons)
		{
			return null;
		}
		Pawn_EquipmentTracker equipment2 = pawn.equipment;
		if (((equipment2 != null) ? equipment2.Primary : null) != null && pawn.equipment.PrimaryEq.PrimaryVerb.Available() && !pawn.equipment.PrimaryEq.PrimaryVerb.verbProps.onlyManualCast)
		{
			return pawn.equipment.PrimaryEq.PrimaryVerb;
		}
		if (pawn.kindDef.canMeleeAttack)
		{
			return pawn.meleeVerbs.TryGetMeleeVerb(target);
		}
		return null;
	}

	private Job GetAbilityJob(Pawn pawn, Thing enemyTarget)
	{
		if (pawn.abilities == null)
		{
			return null;
		}
		List<Ability> abilities = pawn.abilities.AllAbilitiesForReading.Where((Ability x) => actionData.autocastAbilities.Contains(x.def)).ToList();
		Job val = TrySelfBuff(pawn, abilities);
		if (val != null)
		{
			return val;
		}
		Job val2 = TryOffesnsiveAbility(pawn, enemyTarget, abilities);
		if (val2 != null)
		{
			return val2;
		}
		return null;
	}

	private Job TrySelfBuff(Pawn pawn, List<Ability> abilities)
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		LocalTargetInfo val = default(LocalTargetInfo);
		((LocalTargetInfo)(ref val))._002Ector((Thing)(object)pawn);
		List<Ability> list = abilities.Where((Ability ability) => ability.verb.targetParams.canTargetSelf && AcceptanceReport.op_Implicit(ability.CanCast) && (!ability.def.aiCanUse || ability.AICanTargetNow(LocalTargetInfo.op_Implicit((Thing)(object)pawn)))).ToList();
		if (GenCollection.Any<Ability>(list))
		{
			return GenCollection.RandomElement<Ability>((IEnumerable<Ability>)list).GetJob(val, val);
		}
		return null;
	}

	private Job TryOffesnsiveAbility(Pawn pawn, Thing enemyTarget, List<Ability> abilities)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		List<Ability> source = pawn.abilities.AICastableAbilities(LocalTargetInfo.op_Implicit(enemyTarget), true);
		source = source.Where(abilities.Contains).ToList();
		if (GenList.NullOrEmpty<Ability>((IList<Ability>)source))
		{
			return null;
		}
		source = source.Where((Ability ability) => CanTargetWithAbility(enemyTarget, ability) != null && actionData.AutoCastFor(ability.def)).ToList();
		if (!GenList.NullOrEmpty<Ability>((IList<Ability>)source) && GenGrid.Standable(((Thing)pawn).Position, ((Thing)pawn).Map) && ((Thing)pawn).Map.pawnDestinationReservationManager.CanReserve(((Thing)pawn).Position, pawn, pawn.Drafted))
		{
			for (int i = 0; i < source.Count; i++)
			{
				if (source[i].verb.CanHitTarget(LocalTargetInfo.op_Implicit(enemyTarget)))
				{
					return source[i].GetJob(LocalTargetInfo.op_Implicit(enemyTarget), LocalTargetInfo.op_Implicit(enemyTarget));
				}
			}
			for (int j = 0; j < source.Count; j++)
			{
				LocalTargetInfo val = source[j].AIGetAOETarget();
				if (((LocalTargetInfo)(ref val)).IsValid)
				{
					return source[j].GetJob(val, val);
				}
			}
			for (int k = 0; k < source.Count; k++)
			{
				if (source[k].verb.targetParams.canTargetSelf)
				{
					return source[k].GetJob(LocalTargetInfo.op_Implicit((Thing)(object)pawn), LocalTargetInfo.op_Implicit((Thing)(object)pawn));
				}
			}
		}
		return null;
	}
}
