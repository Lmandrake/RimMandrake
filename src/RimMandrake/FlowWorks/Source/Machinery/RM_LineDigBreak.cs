using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 2 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
	/// digging breaks the lines on a square when the cut COMMITS. The one commit point is RM_MapComponent_Excavation.Deepen
	/// (LAW 1: the only writer of D; the dig job's DoEffect and the dev "deepen" action both go through it), which calls
	/// <see cref="OnDigCommitted"/> after the grid write. A designation or a cancelled job never calls Deepen, so it breaks
	/// nothing.
	///
	/// What breaks: built rigid pipe, rigid conduit and cords (RM_LineDigBreakMath.BreaksOnDig), destroyed in Deconstruct
	/// mode (salvage drops, no auto-rebuild blueprint, no "destroyed" alert). The liquid net splits through the normal despawn
	/// path (RM_Patch_NetTopologyDespawn bumps the revision); the power net through vanilla's. Blueprints and frames of lines
	/// are left to vanilla: TerrainGrid.DoTerrainChangedEffects cancels them through the phase-1 CanBuildOnTerrain gate.
	/// A pipe pole (phase 4) is killed instead (RM_LineDigBreakMath.KilledOnDig), so Gimme Some Slack drops its spans
	/// (a fallen half lies at each surviving pole) and the pipe edge goes with them.
	/// A hose is not touched here: its re-plan-or-cut belongs to the hose router's depth rule (P5, the item's phase 6).
	/// Setting RM_MachinerySettings.lineCrossingRulesEnabled; off, a dig leaves lines standing (the pre-ruling behaviour).
	/// </summary>
	public static class RM_LineDigBreak
	{
		/// <summary>State reads for the functional script: lines broken by digging, and the commits that broke at least one.</summary>
		public static int LinesBroken, CommitsThatBroke;

		/// <summary>Called by Deepen after D was written. Idempotent: a second call for the same square finds nothing standing.</summary>
		public static int OnDigCommitted(Map map, IntVec3 c, int depthBefore, int depthAfter)
		{
			if (map == null || !c.InBounds(map))
			{
				return 0;
			}
			List<Thing> hit = RM_LineDigBreakMath.ToBreak(RM_MachinerySettings.lineCrossingRulesEnabled, depthBefore, depthAfter,
				new List<Thing>(c.GetThingList(map)), KindOfBuilt, t => t.Destroyed || !t.Spawned);
			int broken = 0;
			foreach (Thing t in hit)
			{
				if (!t.Destroyed)
				{
					LineKind? k = KindOfBuilt(t);
					if (k != null && RM_LineDigBreakMath.KilledOnDig(k.Value))
					{
						t.Destroy(DestroyMode.KillFinalize);   // phase 4: a pipe pole that loses its ground drops its spans
					}
					else
					{
						t.Destroy(DestroyMode.Deconstruct);
					}
					broken++;
				}
			}
			if (broken > 0)
			{
				LinesBroken += broken;
				CommitsThatBroke++;
				Messages.Message(RM_LineDigBreakMath.Message(broken), new TargetInfo(c, map), MessageTypeDefOf.NegativeEvent, false);
			}
			return broken;
		}

		/// <summary>A BUILT line's kind (blueprints and frames answer null: vanilla cancels those on the terrain change).</summary>
		private static LineKind? KindOfBuilt(Thing t)
		{
			if (t is Blueprint || t is Frame || t.def.category != ThingCategory.Building)
			{
				return null;
			}
			return RM_LineCrossing.KindOf(t.def);
		}
	}
}
