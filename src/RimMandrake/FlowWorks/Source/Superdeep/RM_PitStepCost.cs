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
	/// actual walking speed, though, comes from Pawn_PathFollower.CostToMoveIntoCell, which asks
	/// <c>GetPawnCellBaseCostOverride(pawn, c)</c> for the cell's base cost with the pawn still on its old cell. This
	/// postfix answers it for a DRY dug destination: <see cref="RM_PitTrapMath.DryStepBaseCost"/> — 0 between equal
	/// depths and for a drop into a superdeep cell, the deeper cell's dry cost for a climb.
	///
	/// Unchanged on purpose: route PLANNING still sees the dry costs (a pit is still avoided as a shortcut); the pit
	/// hold, ladders and RM_PitPathing's open-pit veto are untouched; liquid cells keep their wading cost; a fall
	/// (jump, cover giving way, forced arrival) is a position change, never a walked step, so it is instant.
	/// Mod Setting pitWalkNormalEnabled (off: every dug step costs its terrain, the old behaviour).
	/// </summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.GetPawnCellBaseCostOverride))]
	public static class RM_Patch_PitStepCost
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, IntVec3 c, ref int? __result)
		{
			if (__result.HasValue || !RimMandrakeFlowWorksSettings.pitWalkNormalEnabled || pawn?.Map == null)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(pawn.Map);
			if (eng == null || !c.InBounds(pawn.Map))
			{
				return;
			}
			int to = eng.ExcavatedDepthAt(c);
			int from = pawn.Position.InBounds(pawn.Map) ? eng.ExcavatedDepthAt(pawn.Position) : 0;
			if ((to == 0 && from == 0) || (to > 0 && eng.FillAt(c) > 0))
			{
				return;   // surface walking, or a liquid cell (wading costs stay)
			}
			if (to == 0)
			{
				// climbing OUT onto undug ground: the surface terrain's own cost plus the climb
				TerrainDef here = pawn.Map.terrainGrid.TerrainAt(c);
				int climb = RM_ExcavationDepth.DryTerrainFor((byte)from)?.pathCost ?? 0;
				__result = (here?.pathCost ?? 0) + RM_PitTrapMath.DryStepBaseCost(from, 0, climb);
				return;
			}
			int deeper = to > from ? to : from;
			int cost = RM_ExcavationDepth.DryTerrainFor((byte)deeper)?.pathCost ?? 0;
			__result = RM_PitTrapMath.DryStepBaseCost(from, to, cost);
		}
	}
}
