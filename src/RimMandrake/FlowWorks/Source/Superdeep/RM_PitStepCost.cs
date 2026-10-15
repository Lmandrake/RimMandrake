using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 9 (owner, 2026-10-06): <i>"people stuck inside a pit do NOT walk slowly...
	/// they walk at normal speed. Only when they are climbing in or out do they move slowly. Falling into a pit is FAST.
	/// Walking around within the pit is normal."</i>
	///
	/// A dug cell's dry terrain carries a path cost that rises with depth (30/45/80/300), and vanilla charges a
	/// terrain's cost on EVERY step into it — so walking along a pit floor was as slow as climbing in. The step cost is
	/// edge-dependent (it depends on where the pawn steps FROM), which the per-cell path grid cannot express; the
	/// actual walking speed, though, comes from Pawn_PathFollower.CostToMoveIntoCell, which calls
	/// <c>PathGrid.CalculatedCostAt(c, perceivedStatic: false, pawn.Position, override)</c> with the pawn still on its
	/// old cell. This prefix supplies the base-cost override there for a DRY dug destination: <see cref="RM_PitTrapMath.DryStepBaseCost"/> — 0 between equal
	/// depths and for a drop into a superdeep cell, the deeper cell's dry cost for a climb.
	///
	/// Unchanged on purpose: route PLANNING still sees the dry costs (a pit is still avoided as a shortcut); the pit
	/// hold, ladders and RM_PitPathing's open-pit veto are untouched; liquid cells keep their wading cost; a fall
	/// (jump, cover giving way, forced arrival) is a position change, never a walked step, so it is instant.
	/// Mod Setting pitWalkNormalEnabled (off: every dug step costs its terrain, the old behaviour).
	/// Why CalculatedCostAt and not GetPawnCellBaseCostOverride (the first version, 2026-10-06): that method is a
	/// four-line static the Mono JIT inlines into CostToMoveIntoCell, so its Harmony postfix never ran there — the
	/// depth_fill playtest still measured a D2/D3 floor crossing at ~2x the surface (fwpt_20261007T051912_s1,
	/// 763/804 vs 401 ticks). CalculatedCostAt is a large virtual method and is not inlined. Only the walked-step call
	/// is touched: perceivedStatic=false with a valid prevCell is CostToMoveIntoCell's alone (the grid rebuild passes
	/// perceivedStatic=true, the debug inspector an invalid prevCell).
	/// </summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("Normal walking along a pit floor", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitWalkNormalEnabled")]
	public static class RM_Patch_PitStepCost
	{
		// Ahead of RM_Patch_PathGrid_PitCoverCost (same method, also yields to an existing override): a climb onto a
		// cover must be priced here, cover cost + climb, not left to whichever prefix Harmony happened to order first.
		[HarmonyPrefix]
		[HarmonyPriority(Priority.High)]
		public static void Prefix(PathGrid __instance, IntVec3 c, bool perceivedStatic, IntVec3 prevCell, ref int? baseCostOverride)
		{
			if (perceivedStatic || !prevCell.IsValid || baseCostOverride.HasValue || !RimMandrakeFlowWorksSettings.pitWalkNormalEnabled)
			{
				return;
			}
			Map map = __instance.map;
			if (map == null || __instance.def == null || __instance.def.flying || !c.InBounds(map) || !prevCell.InBounds(map))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return;
			}
			// An intact pit cover is ground (PIT_COVER_FALL_REWIRE_1): stepping on or off a deck is surface walking, never a
			// climb out of the hole beneath it. RM_Patch_PathGrid_PitCoverCost prices the covered cell itself.
			int to = eng.HollowDepthAt(c);
			Pits.Building_PitCover toCover = to > 0 ? Pits.RM_PitCoverUtility.CoverAt(map, c) : null;
			if (toCover != null)
			{
				to = 0;
			}
			int from = eng.HollowDepthAt(prevCell);
			if (from > 0 && Pits.RM_PitCoverUtility.IsCovered(map, prevCell))
			{
				from = 0;
			}
			if ((to == 0 && from == 0) || (to > 0 && eng.FillAt(c) > 0))
			{
				return;   // surface walking, or a liquid cell (wading costs stay)
			}
			if (to == 0)
			{
				// climbing OUT onto undug ground (or an intact cover): the surface's own cost plus the climb. A covered
				// cell's terrain is the dug floor beneath the deck, so its surface cost is the cover's (as
				// RM_Patch_PathGrid_PitCoverCost prices it) — otherwise the result depended on which prefix ran first.
				int surface = toCover != null ? Mathf.Max(toCover.def.pathCost, 0) : (map.terrainGrid.TerrainAt(c)?.pathCost ?? 0);
				int climb = RM_ExcavationDepth.DryTerrainFor((byte)from)?.pathCost ?? 0;
				baseCostOverride = surface + (RM_CliffMask.On ? MaskedStepCost(map, eng, prevCell, c, from, 0, climb)
					: RM_PitTrapMath.DryStepBaseCost(from, 0, climb));
				return;
			}
			int deeper = to > from ? to : from;
			int cost = RM_ExcavationDepth.DryTerrainFor((byte)deeper)?.pathCost ?? 0;
			if (RM_CliffMask.On)
			{
				baseCostOverride = MaskedStepCost(map, eng, prevCell, c, from, to, cost);
				return;
			}
			baseCostOverride = RM_PitTrapMath.DryStepBaseCost(from, to, cost);
		}

		/// <summary>PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS (§8.5 step 5): with the masks on, the walked step is priced by
		/// RM_PitTrapMath.StepCost for THIS pawn's climb limit (noted by RM_Patch_PathFollower_StepPawn): a slow climb at s = K
		/// (× "Slow climb factor"), a ramp flat, a ladder per level. Down costs the same as up. Pawnless: the person band.</summary>
		private static int MaskedStepCost(Map map, RM_MapComponent_Excavation eng, IntVec3 from, IntVec3 to, int fromD, int toD, int climbCost)
		{
			Pawn p = RM_Patch_PathFollower_StepPawn.current;
			int k = p == null ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);
			bool viaLadder = false, viaRamp = false;
			if (p != null)
			{
				RM_ClimbJoins.ForPawn(map, eng, from, to, fromD, toD, p, out viaLadder, out viaRamp);
			}
			int perLevel = RM_ClimbJoins.LadderCostPerLevel(climbCost);
			return RM_PitTrapMath.StepCost(fromD, toD, k, climbCost, viaRamp, viaLadder, perLevel,
				RimMandrakeFlowWorksSettings.pitSlowClimbFactor);
		}
	}

	/// <summary>Notes which pawn CostToMoveIntoCell is pricing, so the step cost knows its climb limit (CalculatedCostAt has no
	/// pawn). Re-entrant: locomotionUrgencySameAs prices another pawn inside the call, so the previous one is restored.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "CostToMoveIntoCell", new[] { typeof(Pawn), typeof(IntVec3) })]
	[RimMandrake.Shared.PatchFeature("Normal walking along a pit floor", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitWalkNormalEnabled")]
	public static class RM_Patch_PathFollower_StepPawn
	{
		[System.ThreadStatic]
		internal static Pawn current;

		[HarmonyPrefix]
		public static void Prefix(Pawn pawn, out Pawn __state)
		{
			__state = current;
			current = pawn;
		}

		[HarmonyFinalizer]
		public static void Finalizer(Pawn __state)
		{
			current = __state;
		}
	}
}
