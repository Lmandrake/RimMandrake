using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI.Group;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class DeathActionWorker_SpawnItemsAndFilth : DeathActionWorker
{
	public DeathActionProperties_SpawnItemsAndFilth Props => (DeathActionProperties_SpawnItemsAndFilth)(object)base.props;

	public override void PawnDied(Corpse corpse, Lord prevLord)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)corpse).Map == null || !Rand.Chance(Props.dropChance))
		{
			return;
		}
		if (Props.isRandom)
		{
			ThingDefCount val = ThingDefCount.op_Implicit(GenCollection.RandomElement<ThingDefCountClass>((IEnumerable<ThingDefCountClass>)Props.items));
			if (val != ThingDefCount.op_Implicit((ThingDefCountClass)null))
			{
				Thing obj = ThingMaker.MakeThing(((ThingDefCount)(ref val)).ThingDef, (ThingDef)null);
				obj.stackCount = ((ThingDefCount)(ref val)).Count;
				GenPlace.TryPlaceThing(obj, ((Thing)corpse).Position, ((Thing)corpse).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			}
		}
		else
		{
			foreach (ThingDefCountClass item in Props.items)
			{
				ThingDefCount val2 = ThingDefCount.op_Implicit(item);
				Thing obj2 = ThingMaker.MakeThing(((ThingDefCount)(ref val2)).ThingDef, (ThingDef)null);
				obj2.stackCount = ((ThingDefCount)(ref val2)).Count;
				GenPlace.TryPlaceThing(obj2, ((Thing)corpse).Position, ((Thing)corpse).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			}
		}
		IntVec3 val3 = default(IntVec3);
		for (int i = 0; i < ((IntRange)(ref Props.filthCountRange)).RandomInRange; i++)
		{
			CellFinder.TryFindRandomReachableNearbyCell(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val3, 999999);
			FilthMaker.TryMakeFilth(val3, ((Thing)corpse).MapHeld, Props.filthCreated, 1, (FilthSourceFlags)0, true);
		}
		if (Props.sound != null)
		{
			SoundStarter.PlayOneShot(Props.sound, SoundInfo.op_Implicit(new TargetInfo(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, false)));
		}
	}
}
