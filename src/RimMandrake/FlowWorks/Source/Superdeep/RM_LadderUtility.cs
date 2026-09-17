using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDERS — <i>"a building that makes a dug cell exitable — one boolean
	/// effect; removing the ladder strands whatever is down there."</i>
	///
	/// That is the whole mechanic and it is deliberately the whole mechanic. A
	/// ladder does NOT change pathing cost, passability, line of sight or the
	/// escape odds — it flips one gate, the same gate Building_PitCell's closed
	/// door flips, and the jailer mechanic falls out of it for free.
	/// </summary>
	public static class RM_LadderUtility
	{
		/// <summary>Is there a ladder standing in this cell? O(things-in-cell),
		/// which on an excavated cell is one or two.</summary>
		public static bool HasLadder(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			ThingDef ladder = RimMandrakeFlowWorks_DefOf.RM_Ladder;
			if (ladder == null)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == ladder)
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>A ladder belongs in a hole. Refusing it on open ground is not
	/// pedantry — a ladder that can be built anywhere and does nothing anywhere
	/// else is a button that lies.</summary>
	public class PlaceWorker_LadderOnExcavation : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return false;
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			if (engine == null || !engine.IsExcavated(loc))
			{
				return "RMFlow_LadderNeedsExcavation".Translate();
			}
			return true;
		}
	}
}
