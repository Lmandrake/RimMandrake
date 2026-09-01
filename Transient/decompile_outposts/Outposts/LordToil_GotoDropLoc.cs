using System;
using System.Linq;
using Verse;
using Verse.AI.Group;

namespace Outposts;

public class LordToil_GotoDropLoc : LordToil_Travel
{
	public LordToil_GotoDropLoc()
		: base(IntVec3.Zero)
	{
	}//IL_0001: Unknown result type (might be due to invalid IL or missing references)


	public override void UpdateAllDuties()
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		((LordToil_Travel)this).SetDestination(FindDropSpot(((LordToil)this).lord.ownedPawns.First()));
		((LordToil_Travel)this).UpdateAllDuties();
	}

	private IntVec3 FindDropSpot(Pawn pawn)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 result = default(IntVec3);
		if (CellFinder.TryFindRandomReachableCellNearPosition(((Thing)pawn).Position, ((Thing)pawn).Position, ((Thing)pawn).Map, 25.8f, TraverseParms.For(pawn, (Danger)3, (TraverseMode)0, false, false, false, true), (Predicate<IntVec3>)((IntVec3 x) => GenGrid.Walkable(x, ((Thing)pawn).Map) && GenRadial.RadialCellsAround(x, 12.9f, true).Count((IntVec3 c) => GenGrid.Walkable(c, ((Thing)pawn).Map) && !GenCollection.Any<Thing>(GridsUtility.GetThingList(c, ((Thing)pawn).Map), (Predicate<Thing>)((Thing t) => t.def.saveCompressible || (int)t.def.category == 2))) >= GenRadial.NumCellsInRadius(12.9f) / 2), (Predicate<Region>)((Region _) => true), ref result, 999999))
		{
			return result;
		}
		return CellFinder.RandomCell(((Thing)pawn).Map);
	}
}
