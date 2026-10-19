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
			// SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: the climb depth (a dug swim square at its water surface), not the bare hole
			// SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT: a decked cell reads its deck's walking height (a cover's is 0, the surface).
			int to = eng.ClimbDepthAt(c);
			Pits.Building_SpanDeck toCover = to > 0 ? Pits.RM_SpanUtility.DeckAt(map, c) : null;
			if (toCover != null)
			{
				to = RM_SpanMath.WalkingDepth(to, toCover.Read);
			}
			int from = eng.ClimbDepthAt(prevCell);
			if (from > 0 && Pits.RM_SpanUtility.DeckedAt(map, prevCell, out float fromDeckM))
			{
				from = System.Math.Min(from, RM_SpanMath.Notches(fromDeckM));
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

	/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §4.1): a wet pit now shows the look of the water standing in
	/// it (4 cm is a thin sheet, 1 m is shallow water), and those looks cost less to cross than a pit (90/120 against 300).
	/// The pit's own fill terrain used to carry its 300 for every depth of water; this prefix keeps that: a wet pit cell is
	/// priced at least as the dry pit, so route planning still treats a pit as a place nobody crosses by choice and the walked
	/// step costs what it did. Runs after the pit cover's prefix (a covered pit costs the cover) and yields to any override
	/// already set. Capture, hold and climb read the depth grid, never the terrain (ruling 26).</summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("A wet pit costs a pit to cross")]
	public static class RM_Patch_WetPitPlanningCost
	{
		[HarmonyPrefix]
		[HarmonyPriority(Priority.Low)]
		public static void Prefix(PathGrid __instance, IntVec3 c, ref int? baseCostOverride)
		{
			if (baseCostOverride.HasValue)
			{
				return;
			}
			Map map = __instance.map;
			if (map == null || !c.InBounds(map))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || eng.ExcavatedCellCount == 0)
			{
				return;
			}
			// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: a wet dug square is priced at least as its own DRY hole (by its depth band),
			// not "a 2 m pit or nothing". Shipped looks make this a no-op under 2 m (wet 90/120/300 against dry 30/45/80).
			int depth = eng.ExcavatedDepthRaw(c);
			if (depth <= 0)
			{
				return;
			}
			// SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: dug water 2 m or deeper is swum (owner R12), priced like natural deep
			// water (the swim offset grids close it to non-swimmers), never as a pit nobody crosses
			if (eng.IsDugSwimCell(c))
			{
				baseCostOverride = Swimming.RM_SwimSettings.swimPathCost;
				return;
			}
			// P14: a wet dug square's water is its BASE terrain now (the one ladder, whose 0.5-1.5 m rungs cost less than a
			// dug floor); TerrainAt also covers ice or a flood lying over it.
			TerrainDef temp = map.terrainGrid.TerrainAt(c);
			int dry = RM_ExcavationDepth.DryTerrainFor((byte)System.Math.Min(255, depth))?.pathCost ?? 0;
			if (temp != null && temp.pathCost < dry)
			{
				baseCostOverride = dry;
			}
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
