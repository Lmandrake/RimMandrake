using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>Cuts a cell one level deeper. Reuses vanilla's own
	/// JobDriver_AffectFloor (the SmoothFloor engine) -- designation gating,
	/// reservation, work-speed ticking and the progress bar all come for
	/// free.</summary>
	public class JobDriver_DigCanal : JobDriver_AffectFloor
	{
		/// <summary>Work scales with the level being cut (ruling 19's four
		/// depths): deeper spoil is further to move and further to throw. A
		/// SHALLOW cut still costs exactly the 3200 it always did, so nothing
		/// about an existing colony's dig gets more expensive.</summary>
		protected override int BaseWorkAmount
		{
			get
			{
				Map map = base.Map;
				if (map == null || !job.targetA.IsValid)
				{
					return RM_ExcavationDepth.WorkPerLevel;
				}
				IntVec3 c = job.targetA.Cell;
				if (!c.InBounds(map))
				{
					return RM_ExcavationDepth.WorkPerLevel;
				}
				// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: priced by the GRID's depth (the terrain read every cut past 2 m as the
				// 2 m cut, and so priced a 7.5 m cut at 12,800 instead of 48,000).
				RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
				byte current = eng != null ? (byte)eng.ExcavatedDepthAt(c) : RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c));
				if (current == RM_ExcavationDepth.Surface)
				{
					// POND_BED (owner by card 2026-10-14): a dry bed's first cut is the level below the bed.
					int first = eng?.FirstCutDepthAt(c) ?? 1;
					if (first > 1)
					{
						current = (byte)(first - 1);
					}
				}
				int work = RM_ExcavationDepth.WorkToDeepen(current);
				// DIG_ROCK_TUNE_STONE_FIGHTS_BACK: digging through rock is much harder than soft ground.
				if (RimMandrakeFlowWorksSettings.digRockGroundEnabled && RM_DigDiscovery.RockGroundAt(map, c) != null)
				{
					work = RM_DigDiscoveryMath.RockWork(work, RimMandrakeFlowWorksSettings.digRockWorkMultiplier);
				}
				return work;
			}
		}

		protected override DesignationDef DesDef => RimMandrakeFlowWorks_DefOf.RM_DigCanal;

		/// <summary>Set when this job's cut landed (DoEffect): only then may the finish action re-designate a dig-to square.</summary>
		private bool cutLanded;

		/// <summary>DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: the cut was refused at this digger's cap (a setting changed mid-job)
		/// while someone else may still dig the square. Vanilla deleted the designation; the finish action puts it back.</summary>
		private bool cutRefusedButOwed;

		/// <summary>PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT, "dig to N m": vanilla's AffectFloor deletes the designation after each
		/// cut (RimWorld/JobDriver_AffectFloor.cs). One designation, one notch, as before; a square with a dig-to target gets its
		/// designation back after a landed cut while it is still above its target and the cap, so the next pawn (or this one)
		/// cuts the next notch. A cancelled job or a cancelled designation re-adds nothing.</summary>
		protected override System.Collections.Generic.IEnumerable<Verse.AI.Toil> MakeNewToils()
		{
			AddFinishAction(delegate (Verse.AI.JobCondition cond)
			{
				if (cutRefusedButOwed && Map != null && job.targetA.IsValid)
				{
					IntVec3 rc = job.targetA.Cell;
					if (Map.designationManager.DesignationAt(rc, RimMandrakeFlowWorks_DefOf.RM_DigCanal) == null
						&& Map.designationManager.DesignationAt(rc, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) == null)
					{
						Map.designationManager.AddDesignation(new Designation(rc, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
					}
					return;
				}
				if (!cutLanded || Map == null || !job.targetA.IsValid)
				{
					return;
				}
				IntVec3 c = job.targetA.Cell;
				RM_MapComponent_Excavation ex = Map.GetComponent<RM_MapComponent_Excavation>();
				if (ex == null || ex.DigTargetAt(c) <= 0)
				{
					return;
				}
				if (ex.DigToOwesWork(c) && RimMandrakeFlowWorksSettings.digToDepthEnabled)
				{
					if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) == null
						&& Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) == null)
					{
						Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
					}
				}
				else
				{
					ex.SetDigTarget(c, 0);   // reached (or the cap now stops it): the order is done
				}
			});
			return base.MakeNewToils();
		}

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			// The depth grid is the authority (ruling 18). Deepen() writes D and
			// lays the matching terrain, so pathCost and art follow the integer
			// rather than the other way round.
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (excavation != null)
			{
				int before = excavation.ExcavatedDepthAt(c);
				// DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: the cut is held to THIS digger's cap (colonist 2 m, machine deeper), so a
				// job taken before a setting change cannot overshoot.
				int after = excavation.DeepenWithin(c, RM_DigLabor.CapFor(pawn));
				cutLanded = after > before;
				cutRefusedButOwed = after == before && RM_DigDepthMath.MayDeepen(before, RM_DigLabor.DesignationCap);
				// FLOWWORKS_QUARRY_DIGGING_1: a cut that went deeper may turn up something the land holds.
				if (after > before)
				{
					excavation.DigDiscovery.OnCut(Map, c, after, pawn);
				}
			}
			else
			{
				// Defensive only: MapComponents are auto-discovered by
				// reflection, so this branch means something is badly wrong.
				Map.terrainGrid.SetTerrain(c, RimMandrakeFlowWorks_DefOf.RM_Channel_Empty);
			}
			// Ruling 24 (owner, 2026-09-16) deleted CompFluidReservoir: a source
			// is not a building, it is a SUPERDEEP cell at F = D. There is no
			// reservoir to notify any more — supply is the depth grid's own
			// business, and RM_MapComponent_Excavation's pulse is what moves it.
		}
	}
}
