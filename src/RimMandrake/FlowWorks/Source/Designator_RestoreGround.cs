using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY (owner 2026-10-25, "Suspension: 2 or 3 (towers should be VERY
	/// expensive to build, so using islands is important for resource savings)"): one order that fills a dug square all the
	/// way back to solid ground, for a ground island a suspension bridge rests on. It is the fill-in order repeated: each job
	/// still raises the square half a metre (displacing liquid the same way), and RM_MapComponent_GroundRestore puts the
	/// fill order back after each job until the square is ground again. Cancelling the fill order stops it.</summary>
	public class Designator_RestoreGround : Designator_FillInCanal
	{
		public Designator_RestoreGround()
		{
			defaultLabel = "Restore ground";
			defaultDesc = "Fill dug squares all the way back to solid ground, half a metre per job until done (the fill-in order, "
				+ "repeated). Use it for a ground island in a hole: a suspension bridge dragged across an island at least 2 squares "
				+ "long and as wide as the bridge becomes one bridge per hole, far cheaper than a tower. Cancel the fill-in order to "
				+ "stop. Colonists assigned to Mining do the work.";
			hotKey = null;
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!c.InBounds(Map) || c.Fogged(Map))
			{
				return false;
			}
			RM_MapComponent_GroundRestore restore = Map.GetComponent<RM_MapComponent_GroundRestore>();
			if (restore != null && restore.Tracks(c))
			{
				return "Already being restored.";
			}
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) != null)
			{
				return RimMandrakeFlowWorksSettings.fillInEnabled ? AcceptanceReport.WasAccepted
					: (AcceptanceReport)"Filling in is switched off in this mod's settings.";
			}
			return base.CanDesignateCell(c);
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) == null)
			{
				base.DesignateSingleCell(c);
			}
			Map.GetComponent<RM_MapComponent_GroundRestore>()?.Track(c);
		}
	}

	/// <summary>The squares a Restore ground order is bringing back to the surface, with the dug depth each had when its
	/// current fill order was (re)placed. Every 250 ticks: a square back at the surface is done; one whose fill order is still
	/// there is waiting for its job; one whose order is gone and that got shallower had its job done, so the order goes back
	/// (a square built on, or one that can no longer take a fill order, ends the restore: there would be no order for the
	/// player to Cancel); one whose order is gone at the same depth was cancelled by the player and is forgotten.</summary>
	public class RM_MapComponent_GroundRestore : MapComponent
	{
		private Dictionary<IntVec3, int> tracked = new Dictionary<IntVec3, int>();
		private List<IntVec3> keysWork;
		private List<int> valuesWork;

		public RM_MapComponent_GroundRestore(Map map) : base(map)
		{
		}

		public bool Tracks(IntVec3 c) => tracked.ContainsKey(c);

		public int Count => tracked.Count;

		public void Track(IntVec3 c)
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex != null && ex.ExcavatedDepthAt(c) > 0)
			{
				tracked[c] = ex.ExcavatedDepthAt(c);
			}
		}

		public override void MapComponentTick()
		{
			if (tracked.Count == 0 || Find.TickManager.TicksGame % 250 != 0)
			{
				return;
			}
			Step();
		}

		/// <summary>One pass over the tracked squares (public for the proof).</summary>
		public void Step()
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				tracked.Clear();
				return;
			}
			List<IntVec3> forget = new List<IntVec3>();
			List<KeyValuePair<IntVec3, int>> renew = new List<KeyValuePair<IntVec3, int>>();
			foreach (KeyValuePair<IntVec3, int> kv in tracked)
			{
				IntVec3 c = kv.Key;
				int d = ex.ExcavatedDepthAt(c);
				if (d <= 0 || !c.InBounds(map))
				{
					forget.Add(c);
					continue;
				}
				if (map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) != null)
				{
					continue;
				}
				if (d >= kv.Value)
				{
					forget.Add(c);   // the order went without a job done: cancelled
					continue;
				}
				if (c.GetEdifice(map) != null)
				{
					forget.Add(c);   // something was built on it: the island is not wanted any more
					continue;
				}
				if (!RimMandrakeFlowWorksSettings.fillInEnabled || !ex.CanFillIn(c))
				{
					forget.Add(c);   // no fill order can stand here now: holding an invisible intent would leave the player
					continue;        // nothing to Cancel (review r1), so the restore ends and the player orders it again
				}
				// a pawn standing on the square does not pause it: the order is re-added (so Cancel can always see it) and the
				// fill job waits for the square like any other order
				map.designationManager.TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal);
				map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal));
				renew.Add(new KeyValuePair<IntVec3, int>(c, d));
			}
			foreach (IntVec3 c in forget)
			{
				tracked.Remove(c);
			}
			foreach (KeyValuePair<IntVec3, int> kv in renew)
			{
				tracked[kv.Key] = kv.Value;
			}
		}

		public override void ExposeData()
		{
			Scribe_Collections.Look(ref tracked, "restoreGround", LookMode.Value, LookMode.Value, ref keysWork, ref valuesWork);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && tracked == null)
			{
				tracked = new Dictionary<IntVec3, int>();
			}
		}
	}
}
