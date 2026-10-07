using HarmonyLib;
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
	public static class RM_Patch_PitStepCost
	{
		[HarmonyPrefix]
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
			int to = eng.ExcavatedDepthAt(c);
			int from = eng.ExcavatedDepthAt(prevCell);
			if ((to == 0 && from == 0) || (to > 0 && eng.FillAt(c) > 0))
			{
				return;   // surface walking, or a liquid cell (wading costs stay)
			}
			if (to == 0)
			{
				// climbing OUT onto undug ground: the surface terrain's own cost plus the climb
				TerrainDef here = map.terrainGrid.TerrainAt(c);
				int climb = RM_ExcavationDepth.DryTerrainFor((byte)from)?.pathCost ?? 0;
				baseCostOverride = (here?.pathCost ?? 0) + RM_PitTrapMath.DryStepBaseCost(from, 0, climb);
				return;
			}
			int deeper = to > from ? to : from;
			int cost = RM_ExcavationDepth.DryTerrainFor((byte)deeper)?.pathCost ?? 0;
			baseCostOverride = RM_PitTrapMath.DryStepBaseCost(from, to, cost);
		}
	}
}
