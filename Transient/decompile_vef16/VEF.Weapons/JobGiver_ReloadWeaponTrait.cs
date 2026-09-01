using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

public class JobGiver_ReloadWeaponTrait : ThinkNode_JobGiver
{
	private const bool ForceReloadWhenLookingForWork = false;

	public override float GetPriority(Pawn pawn)
	{
		return 5.9f;
	}

	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		if (!pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
		{
			return null;
		}
		CompApplyWeaponTraits compApplyWeaponTraits = FloatMenuOptionProvider_ReloadWeaponTrait.FindSomeReloadableComponent(pawn);
		if (compApplyWeaponTraits == null)
		{
			return null;
		}
		if (pawn.carryTracker.AvailableStackSpace(compApplyWeaponTraits.AbilityDetailsForWeapon(compApplyWeaponTraits.GetDetails()).ammoDef) < compApplyWeaponTraits.MinAmmoNeeded())
		{
			return null;
		}
		List<Thing> list = FloatMenuOptionProvider_ReloadWeaponTrait.FindEnoughAmmo(pawn, ((Thing)pawn).Position, compApplyWeaponTraits);
		if (GenList.NullOrEmpty<Thing>((IList<Thing>)list))
		{
			return null;
		}
		return MakeReloadJob(compApplyWeaponTraits, list);
	}

	public static Job MakeReloadJob(CompApplyWeaponTraits comp, List<Thing> chosenAmmo)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		Job obj = JobMaker.MakeJob(InternalDefOf.VEF_ReloadWeaponTrait, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)comp).parent));
		obj.targetQueueB = ((IEnumerable<Thing>)chosenAmmo).Select((Func<Thing, LocalTargetInfo>)((Thing t) => new LocalTargetInfo(t))).ToList();
		obj.count = chosenAmmo.Sum((Thing t) => t.stackCount);
		obj.count = Math.Min(obj.count, comp.MaxAmmoNeeded());
		return obj;
	}
}
