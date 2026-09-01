using System;
using System.Collections.Generic;
using Verse;
using Verse.AI.Group;

namespace VEF.AnimalBehaviours;

public class DeathActionWorker_DropOnDeath : DeathActionWorker
{
	private Random rand = new Random();

	public override void PawnDied(Corpse corpse, Lord prevLord)
	{
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		CompDropOnDeath compDropOnDeath = ThingCompUtility.TryGetComp<CompDropOnDeath>((Thing)(object)corpse.InnerPawn);
		if (compDropOnDeath == null || ((Thing)corpse).Map == null || !(rand.NextDouble() <= (double)compDropOnDeath.Props.dropChance))
		{
			return;
		}
		if (compDropOnDeath.Props.isRandom)
		{
			ThingDef namedSilentFail = DefDatabase<ThingDef>.GetNamedSilentFail(GenCollection.RandomElement<string>((IEnumerable<string>)compDropOnDeath.Props.randomItems));
			if (namedSilentFail != null)
			{
				Thing obj = ThingMaker.MakeThing(namedSilentFail, (ThingDef)null);
				obj.stackCount = compDropOnDeath.Props.resourceAmount;
				GenPlace.TryPlaceThing(obj, ((Thing)corpse).Position, ((Thing)corpse).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			}
		}
		else
		{
			ThingDef namedSilentFail = DefDatabase<ThingDef>.GetNamedSilentFail(compDropOnDeath.Props.resourceDef);
			if (namedSilentFail != null)
			{
				Thing obj2 = ThingMaker.MakeThing(namedSilentFail, (ThingDef)null);
				obj2.stackCount = compDropOnDeath.Props.resourceAmount;
				GenPlace.TryPlaceThing(obj2, ((Thing)corpse).Position, ((Thing)corpse).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			}
		}
	}
}
