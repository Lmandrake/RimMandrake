using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace VEF.AI;

public class JobGiver_DraftedJobs : JobGiver_AIFightEnemy
{
	public DraftedActionData actionData;

	public List<AbilityDef> blacklist = new List<AbilityDef>();

	public bool Hunt => actionData.hunt;

	protected override bool OnlyUseAbilityVerbs => !actionData.hunt;

	protected override bool OnlyUseRangedSearch => false;

	public override ThinkNode DeepCopy(bool resolve = true)
	{
		return (ThinkNode)(object)(JobGiver_DraftedJobs)(object)((JobGiver_AIFightEnemy)this).DeepCopy(resolve);
	}

	protected override bool TryFindShootingPosition(Pawn pawn, out IntVec3 dest, Verb verbToUse = null)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		dest = ((Thing)pawn).Position;
		if (Hunt)
		{
			Thing enemyTarget = pawn.mindState.enemyTarget;
			if (CanTargetWithAbillities(pawn, enemyTarget, out var pickedAbility))
			{
				CastPositionRequest val = default(CastPositionRequest);
				val.caster = pawn;
				val.target = enemyTarget;
				val.verb = pickedAbility.verb;
				val.maxRangeFromTarget = pickedAbility.verb.verbProps.range;
				val.wantCoverFromTarget = false;
				val.preferredCastPosition = ((Thing)pawn).Position;
				return CastPositionFinder.TryFindCastPosition(val, ref dest);
			}
		}
		return true;
	}

	protected override bool ExtraTargetValidator(Pawn pawn, Thing target)
	{
		if (pawn == null || !pawn.Drafted)
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
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null || !pawn.Drafted)
		{
			return null;
		}
		actionData = DraftedActionHolder.GetData(pawn);
		if (!Hunt)
		{
			if (GenCollection.Empty<AbilityDef>(actionData.autocastAbilities) || pawn.abilities?.abilities == null || GenList.NullOrEmpty<Ability>((IList<Ability>)pawn.abilities.abilities))
			{
				return null;
			}
			if (pawn.abilities.abilities.All((Ability ability) => !AcceptanceReport.op_Implicit(ability.CanCast) || blacklist.Contains(ability.def)))
			{
				return GetWaitForTimeJob(pawn, 100);
			}
		}
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
		if (((JobGiver_AIFightEnemy)this).ShouldLoseTarget(pawn))
		{
			return true;
		}
		Ability pickedAbility;
		if (!Hunt)
		{
			return !CanTargetWithAbillities(pawn, pawn.mindState.enemyTarget, out pickedAbility);
		}
		return false;
	}

	protected bool CanTargetWithAbillities(Pawn pawn, Thing target, out Ability pickedAbility)
	{
		pickedAbility = null;
		if (!pawn.Drafted || pawn.abilities?.abilities == null)
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
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
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
		if (ability.AICanTargetNow(LocalTargetInfo.op_Implicit(target)))
		{
			return ability;
		}
		return null;
	}

	protected Job GiveDraftedHuntJob(Pawn pawn)
	{
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		((JobGiver_AIFightEnemy)this).UpdateEnemyTarget(pawn);
		Thing enemyTarget = pawn.mindState.enemyTarget;
		if (enemyTarget == null)
		{
			return null;
		}
		Pawn val = (Pawn)(object)((enemyTarget is Pawn) ? enemyTarget : null);
		if (val != null && InvisibilityUtility.IsPsychologicallyInvisible(val))
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
		if (val2.verbProps.IsMeleeAttack)
		{
			Job obj = ((JobGiver_AIFightEnemy)this).MeleeAttackJob(pawn, enemyTarget);
			obj.checkOverrideOnExpire = true;
			obj.expiryInterval = 200;
			return obj;
		}
		bool num = CoverUtility.CalculateOverallBlockChance(LocalTargetInfo.op_Implicit((Thing)(object)pawn), enemyTarget.Position, ((Thing)pawn).Map) > 0.01f;
		bool flag = GenGrid.Standable(((Thing)pawn).Position, ((Thing)pawn).Map) && ((Thing)pawn).Map.pawnDestinationReservationManager.CanReserve(((Thing)pawn).Position, pawn, pawn.Drafted);
		bool flag2 = val2.CanHitTarget(LocalTargetInfo.op_Implicit(enemyTarget));
		IntVec3 val3 = ((Thing)pawn).Position - enemyTarget.Position;
		bool flag3 = ((IntVec3)(ref val3)).LengthHorizontalSquared < 25;
		IntRange expiryInterval_ShooterSucceeded;
		if ((num && flag && flag2) || (flag3 && flag2))
		{
			JobDef wait_Combat = JobDefOf.Wait_Combat;
			expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
			return JobMaker.MakeJob(wait_Combat, ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange, true);
		}
		IntVec3 val4 = default(IntVec3);
		if (!((JobGiver_AIFightEnemy)this).TryFindShootingPosition(pawn, ref val4, (Verb)null))
		{
			return null;
		}
		if (val4 == ((Thing)pawn).Position)
		{
			JobDef wait_Combat2 = JobDefOf.Wait_Combat;
			expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
			return JobMaker.MakeJob(wait_Combat2, ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange, true);
		}
		Job obj2 = JobMaker.MakeJob(JobDefOf.Goto, LocalTargetInfo.op_Implicit(val4));
		expiryInterval_ShooterSucceeded = JobGiver_AIFightEnemy.ExpiryInterval_ShooterSucceeded;
		obj2.expiryInterval = ((IntRange)(ref expiryInterval_ShooterSucceeded)).RandomInRange;
		obj2.checkOverrideOnExpire = true;
		return obj2;
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
		if ((val3 = (Pawn)(object)((val is Pawn) ? val : null)) != null && val.Faction == Faction.OfPlayer)
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
		return ((JobGiver_AIFightEnemy)this).FindAttackTarget(pawn);
	}

	public Verb TryGetAttackVerb(Pawn pawn, Thing target, bool allowManualCastWeapons = false, bool allowOnlyManualCastWeapons = false)
	{
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
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		if (pawn.abilities == null)
		{
			return null;
		}
		List<Ability> list = pawn.abilities.AICastableAbilities(LocalTargetInfo.op_Implicit(enemyTarget), true);
		if (GenList.NullOrEmpty<Ability>((IList<Ability>)list))
		{
			return null;
		}
		list = list.Where((Ability ability) => CanTargetWithAbility(enemyTarget, ability) != null && actionData.AutoCastFor(ability.def)).ToList();
		if (GenCollection.Empty<Ability>(list))
		{
			return null;
		}
		if (GenGrid.Standable(((Thing)pawn).Position, ((Thing)pawn).Map) && ((Thing)pawn).Map.pawnDestinationReservationManager.CanReserve(((Thing)pawn).Position, pawn, pawn.Drafted))
		{
			for (int i = 0; i < list.Count; i++)
			{
				if (list[i].verb.CanHitTarget(LocalTargetInfo.op_Implicit(enemyTarget)))
				{
					return list[i].GetJob(LocalTargetInfo.op_Implicit(enemyTarget), LocalTargetInfo.op_Implicit(enemyTarget));
				}
			}
			for (int j = 0; j < list.Count; j++)
			{
				LocalTargetInfo val = list[j].AIGetAOETarget();
				if (((LocalTargetInfo)(ref val)).IsValid)
				{
					return list[j].GetJob(val, val);
				}
			}
			for (int k = 0; k < list.Count; k++)
			{
				if (list[k].verb.targetParams.canTargetSelf)
				{
					return list[k].GetJob(LocalTargetInfo.op_Implicit((Thing)(object)pawn), LocalTargetInfo.op_Implicit((Thing)(object)pawn));
				}
			}
		}
		return null;
	}
}
