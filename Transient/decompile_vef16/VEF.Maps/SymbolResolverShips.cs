using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.BaseGen;
using Verse;
using Verse.AI.Group;

namespace VEF.Maps;

public class SymbolResolverShips : SymbolResolver
{
	public override void Resolve(ResolveParams rp)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Expected O, but got Unknown
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0211: Unknown result type (might be due to invalid IL or missing references)
		//IL_0212: Unknown result type (might be due to invalid IL or missing references)
		//IL_0226: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0240: Unknown result type (might be due to invalid IL or missing references)
		Map map = BaseGen.globalSettings.map;
		Faction val = rp.faction ?? Find.FactionManager.RandomEnemyFaction(false, false, true, (TechLevel)0);
		Lord singlePawnLord = rp.singlePawnLord ?? LordMaker.MakeNewLord(val, (LordJob)(object)new LordJob_DefendShip(val, ((CellRect)(ref rp.rect)).CenterCell), map, (IEnumerable<Pawn>)null);
		TraverseParms traverseParms = TraverseParms.For((TraverseMode)1, (Danger)3, false, false, false, true, false);
		ResolveParams val2 = rp;
		val2.rect = rp.rect;
		val2.faction = val;
		val2.singlePawnLord = singlePawnLord;
		val2.pawnGroupKindDef = rp.pawnGroupKindDef ?? PawnGroupKindDefOf.Settlement;
		val2.singlePawnSpawnCellExtraPredicate = rp.singlePawnSpawnCellExtraPredicate ?? ((Predicate<IntVec3>)((IntVec3 x) => map.reachability.CanReachMapEdge(x, traverseParms)));
		if (val2.pawnGroupMakerParams == null && GenCollection.Any<PawnGroupMaker>(val.def.pawnGroupMakers, (Predicate<PawnGroupMaker>)((PawnGroupMaker pgm) => pgm.kindDef == PawnGroupKindDefOf.Settlement)))
		{
			val2.pawnGroupMakerParams = new PawnGroupMakerParms();
			val2.pawnGroupMakerParams.tile = map.Tile;
			val2.pawnGroupMakerParams.faction = val;
			PawnGroupMakerParms pawnGroupMakerParams = val2.pawnGroupMakerParams;
			float? settlementPawnGroupPoints = rp.settlementPawnGroupPoints;
			float points;
			if (!settlementPawnGroupPoints.HasValue)
			{
				FloatRange defaultPawnsPoints = SymbolResolver_Settlement.DefaultPawnsPoints;
				points = ((FloatRange)(ref defaultPawnsPoints)).RandomInRange;
			}
			else
			{
				points = settlementPawnGroupPoints.GetValueOrDefault();
			}
			pawnGroupMakerParams.points = points;
			val2.pawnGroupMakerParams.inhabitants = true;
			val2.pawnGroupMakerParams.seed = rp.settlementPawnGroupSeed;
		}
		if (GenCollection.Any<PawnGroupMaker>(val.def.pawnGroupMakers, (Predicate<PawnGroupMaker>)((PawnGroupMaker pgm) => pgm.kindDef == PawnGroupKindDefOf.Settlement)))
		{
			BaseGen.symbolStack.Push("pawnGroup", val2, (string)null);
		}
		Enumerator enumerator = ((CellRect)(ref rp.rect)).GetEnumerator();
		try
		{
			while (((Enumerator)(ref enumerator)).MoveNext())
			{
				IntVec3 current = ((Enumerator)(ref enumerator)).Current;
				if (map.fogGrid.IsFogged(current))
				{
					map.fogGrid.Unfog(current);
				}
			}
		}
		finally
		{
			((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
		}
		ResolveParams val3 = rp;
		val3.faction = val;
		BaseGen.symbolStack.Push("kcsg_roomsgenfromstructure", val3, (string)null);
		enumerator = ((CellRect)(ref rp.rect)).GetEnumerator();
		try
		{
			while (((Enumerator)(ref enumerator)).MoveNext())
			{
				GridsUtility.GetThingList(((Enumerator)(ref enumerator)).Current, map).ToList().FindAll((Thing t1) => (int)t1.def.category == 6 || (int)t1.def.category == 2)
					.ForEach(delegate(Thing t)
					{
						((Entity)t).DeSpawn((DestroyMode)0);
					});
			}
		}
		finally
		{
			((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
		}
	}
}
