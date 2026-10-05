using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_DEPTH_DRAW_OFFSET_1 — a pawn is drawn lower the deeper the dug cell it stands
	/// in, and rises again as it walks out. Render only: LAW 2 (depth never touches sight,
	/// shooting or cover) is untouched, because this postfix moves only the drawn position.
	///
	/// Reads the DUG depth (<see cref="RM_MapComponent_Excavation.ExcavatedDepthAt"/>), not
	/// <c>DepthAt</c>: natural water reads through as SUPERDEEP there, and a pawn wading a
	/// vanilla river must not vanish 1.2 cells into it — vanilla draws its own swimming.
	/// Fluid in a canal does not lift the pawn: the occupant stays down on the floor
	/// (<c>slime_occupant_below_surface</c>).
	///
	/// Flying pawns are skipped (vanilla lifts them; a flier over a pit is above it).
	/// Numbers are PROVISIONAL — see <see cref="RM_PitDrawMath"/>; live check owed.
	/// Harmony bootstrap: RM_FlowWorksHarmony's PatchAll() in RM_Patch_SuperdeepShooting.cs.
	/// </summary>
	[HarmonyPatch(typeof(Pawn_DrawTracker), nameof(Pawn_DrawTracker.DrawPos), MethodType.Getter)]
	public static class RM_Patch_PitDepthDrawOffset
	{
		private static readonly AccessTools.FieldRef<Pawn_DrawTracker, Pawn> PawnRef =
			AccessTools.FieldRefAccess<Pawn_DrawTracker, Pawn>("pawn");

		private static Map cachedMap;

		private static RM_MapComponent_Excavation cachedComp;

		[HarmonyPostfix]
		public static void Postfix(Pawn_DrawTracker __instance, ref Vector3 __result)
		{
			if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return;
			}
			Pawn pawn = PawnRef(__instance);
			if (pawn == null || !pawn.Spawned || pawn.Flying)
			{
				return;
			}
			float sink = SinkOf(pawn, __result);
			if (sink > 0f)
			{
				__result.z -= sink;
			}
		}

		/// <summary>The current sink of a spawned pawn, in cells. Public so a companion
		/// [Tool] can state-read it for the northstar bars without a frame.</summary>
		public static float SinkOf(Pawn pawn, Vector3 drawPos)
		{
			RM_MapComponent_Excavation ex = ExcavationOf(pawn.Map);
			if (ex == null)
			{
				return 0f;
			}
			float perLevel = RimMandrakeFlowWorksSettings.pitSinkPerLevel;
			IntVec3 from = pawn.Position;
			int dFrom = ex.ExcavatedDepthAt(from);
			if (pawn.pather == null || !pawn.pather.Moving)
			{
				return RM_PitDrawMath.SinkFor(dFrom, perLevel);
			}
			IntVec3 to = pawn.pather.nextCell;
			int dTo = to.IsValid ? ex.ExcavatedDepthAt(to) : dFrom;
			if (dFrom == 0 && dTo == 0)
			{
				return 0f;
			}
			Vector3 a = from.ToVector3Shifted();
			Vector3 b = to.ToVector3Shifted();
			float t = RM_PitDrawMath.StepProgress(a.x, a.z, b.x, b.z, drawPos.x, drawPos.z);
			return RM_PitDrawMath.SinkBetween(dFrom, dTo, t, perLevel);
		}

		private static RM_MapComponent_Excavation ExcavationOf(Map map)
		{
			if (map == null)
			{
				return null;
			}
			if (map != cachedMap)
			{
				cachedMap = map;
				cachedComp = map.GetComponent<RM_MapComponent_Excavation>();
			}
			return cachedComp;
		}
	}
}
