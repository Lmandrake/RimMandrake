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
				return Clamped(ex, pawn.Map, from, dFrom, perLevel);
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
			float sa = Clamped(ex, pawn.Map, from, dFrom, perLevel);
			float sb = to.IsValid ? Clamped(ex, pawn.Map, to, dTo, perLevel) : sa;
			return sa + (sb - sa) * t;
		}

		/// <summary>Sink on cell <paramref name="c"/> of dug depth <paramref name="d"/>, held so the drawn centre
		/// stays north of the near lip in that column (<see cref="RM_PitDrawMath.ClampSinkToLip"/>).</summary>
		private static float Clamped(RM_MapComponent_Excavation ex, Map map, IntVec3 c, int d, float perLevel)
		{
			float sink = RM_PitDrawMath.SinkFor(d, perLevel);
			if (!(sink > 0f))
			{
				return 0f;
			}
			if (!RimMandrakeFlowWorksSettings.pitSinkClampEnabled)
			{
				return sink;
			}
			float lipZ = float.NaN;
			for (int k = 1; k <= RM_PitDrawMath.MaxDepth * 2; k++)
			{
				IntVec3 cand = new IntVec3(c.x, 0, c.z - k);
				if (!cand.InBounds(map))
				{
					break;
				}
				if (ex.ExcavatedDepthAt(cand) < d)
				{
					lipZ = cand.z + 1f;
					break;
				}
			}
			return RM_PitDrawMath.ClampSinkToLip(sink, c.z + 0.5f, lipZ);
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

	/// <summary>
	/// FLOWWORKS_VISUAL_PRINCIPLES_1 — owner, 2026-10-05, looking at a sunk colonist in game: <i>"Is there a way to
	/// stop the shadow of a person showing through like this?"</i>
	///
	/// 1.6 draws a standing pawn's ground shadow in PawnRenderer.DrawShadowInternal (decompiled, read via RimSage):
	/// the race's specialShadowData blob, else the body graphic's ShadowGraphic, at the pawn's (sunk) draw position —
	/// so it lands below the near bank and shows through. Vanilla itself skips it for a swimming pawn. This skips it
	/// the same way for anything sunk in a dug cell (humans, animals, mechs; filled or dry cut). Flying pawns keep
	/// vanilla's flight shadow (that branch is not ours: a flier is above the pit). Setting off, or no sink: vanilla.
	/// </summary>
	[HarmonyPatch(typeof(PawnRenderer), "DrawShadowInternal")]
	public static class RM_Patch_PitHidesShadow
	{
		private static readonly AccessTools.FieldRef<PawnRenderer, Pawn> PawnOf =
			AccessTools.FieldRefAccess<PawnRenderer, Pawn>("pawn");

		[HarmonyPrefix]
		public static bool Prefix(PawnRenderer __instance, Vector3 drawLoc)
		{
			if (!RimMandrakeFlowWorksSettings.pitHidesShadowEnabled || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return true;
			}
			Pawn pawn = PawnOf(__instance);
			if (pawn == null || !pawn.Spawned || pawn.Flying)
			{
				return true;
			}
			return !(RM_Patch_PitDepthDrawOffset.SinkOf(pawn, drawLoc) > 0f);
		}
	}
}
