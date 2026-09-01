using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class DamageWorker_PushBackAttackMelee : DamageWorker_Blunt
{
	public override DamageResult Apply(DamageInfo dinfo, Thing thing)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		if (((DamageInfo)(ref dinfo)).Instigator != null && thing is Pawn)
		{
			DamageExtension modExtension = ((Def)((DamageWorker)this).def).GetModExtension<DamageExtension>();
			TryToKnockBack(((DamageInfo)(ref dinfo)).Instigator, thing, ((FloatRange)(ref modExtension.pushBackDistance)).RandomInRange, modExtension);
		}
		return ((DamageWorker_AddInjury)this).Apply(dinfo, thing);
	}

	private void TryToKnockBack(Thing attacker, Thing thing, float knockBackDistance, DamageExtension extension)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		float distanceDiff = ((IntVec3Utility.DistanceTo(attacker.Position, thing.Position) < knockBackDistance) ? IntVec3Utility.DistanceTo(attacker.Position, thing.Position) : knockBackDistance);
		Predicate<IntVec3> validator = delegate(IntVec3 x)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
			if (IntVec3Utility.DistanceTo(x, thing.Position) < knockBackDistance)
			{
				return false;
			}
			if (!GenGrid.Walkable(x, thing.Map) || !GenSight.LineOfSight(thing.Position, x, thing.Map))
			{
				return false;
			}
			float num = IntVec3Utility.DistanceTo(attacker.Position, thing.Position);
			float num2 = IntVec3Utility.DistanceTo(attacker.Position, x);
			float num3 = IntVec3Utility.DistanceTo(thing.Position, x);
			if (num > num2)
			{
				return false;
			}
			if (num2 > num3 + (distanceDiff - 1f))
			{
				return true;
			}
			return (attacker.Position == thing.Position) ? true : false;
		};
		IEnumerable<IntVec3> enumerable = from x in GenRadial.RadialCellsAround(thing.Position, knockBackDistance + 1f, true)
			where validator(x)
			select x;
		if (enumerable.Any())
		{
			IntVec3 position = GenCollection.RandomElement<IntVec3>(enumerable);
			thing.Position = position;
			Thing obj = thing;
			Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
			if (val != null)
			{
				val.pather.StopDead();
				val.jobs.StopAll(false, true);
			}
			if (extension.fleckOnDamage != null)
			{
				Thing val2 = (extension.fleckOnInstigator ? attacker : thing);
				FleckMaker.Static(val2.Position, val2.Map, extension.fleckOnDamage, extension.fleckRadius);
			}
		}
	}
}
