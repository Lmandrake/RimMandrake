using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_LOOK_TREATMENTS (Artisan pass 3, 2026-11-07): the pit's depth look as one of three treatments, so they can be
	/// shown side by side on one view before one is built out (Mod Setting <c>pitLookMode</c>, live-switchable).
	///
	///   0 BEVEL (the look until now): a wall-bevel band on the far rim clamped at 0.62 of a cell whatever the depth,
	///     a closed black outline, pawns sunk 0.3 of a cell a notch. The band and the sink disagree past 1 m.
	///   1 OBLIQUE CUT: the camera's own convention (it looks down from the south, so the far wall's face shows and the
	///     near wall hides what stands below it), at ONE scale: the far face hangs <c>pitSinkPerLevel</c> a notch, the same
	///     number the pawn sinks by, so its foot is the floor line the occupant stands on. Lit at the rim, darkening to the
	///     foot by depth, a strata line every metre (count them for the depth), soft shade along the side walls and just
	///     inside the near lip, a lit lip edge. No black box.
	///   2 SHADOW WELL: the top-down reading. Short rim band, the whole floor in view, darkness growing inward from all four
	///     walls and over the floor with depth; occupants barely shift but are drawn smaller and darker the deeper they stand.
	///
	/// Both new treatments darken an occupant with the floor's light (the patch below), so a pawn deep in the hole reads as
	/// in its shadow. Drawing only: nothing here changes sight, cover, pathing or a shot (LAW 2).
	/// </summary>
	/// <summary>The look setting, read in one place.</summary>
	public static class RM_PitLook
	{
		public static int Mode
		{
			get
			{
				int m = RimMandrakeFlowWorksSettings.pitLookMode;
				return m < 0 || m > 2 ? 0 : m;
			}
		}

		/// <summary>The depth (notches) of the dry floor a pawn's body is drawn on, or 0: off the map, flying, standing in
		/// liquid, or on ground. Corpses read where they lie.</summary>
		public static int DryFloorDepth(Pawn pawn)
		{
			if (pawn == null || pawn.Flying)
			{
				return 0;
			}
			Map map = pawn.MapHeld;
			if (map == null)
			{
				return 0;
			}
			IntVec3 c = pawn.PositionHeld;
			if (!c.InBounds(map))
			{
				return 0;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return 0;
			}
			int h = ex.HollowDepthAt(c);
			if (h <= 0 || ex.FillAt(c) > 0)
			{
				return 0;
			}
			if (pawn.Spawned)
			{
				h = Pits.RM_SuspensionUnderpass.DrawDepth(pawn, c, h);
			}
			return h;
		}
	}

	/// <summary>PIT_LOOK_TREATMENTS: an occupant of a dry hole is drawn in the hole's light (darker with depth) and, in the
	/// SHADOW WELL, smaller with depth. Postfix on the draw parameters every pawn render reads (tint multiplies each node's
	/// colour, the matrix places every node). Portraits and the render cache are left alone.</summary>
	[HarmonyPatch(typeof(PawnRenderer), "GetDrawParms")]
	[RimMandrake.Shared.PatchFeature("Pawns sink into dug channels", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitDepthDrawOffsetEnabled")]
	public static class RM_Patch_PitOccupantLight
	{
		[HarmonyPostfix]
		public static void Postfix(PawnRenderFlags flags, ref PawnDrawParms __result)
		{
			int mode = RM_PitLook.Mode;
			if (mode == RM_PitLookMath.Bevel || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled
				|| (flags & (PawnRenderFlags.Portrait | PawnRenderFlags.Cache)) != 0)
			{
				return;
			}
			int d = RM_PitLook.DryFloorDepth(__result.pawn);
			if (d <= 0)
			{
				return;
			}
			float k = 1f - RM_PitLookMath.OccupantShade(d, mode);
			Color t = __result.tint;
			__result.tint = new Color(t.r * k, t.g * k, t.b * k, t.a);
			float s = RM_PitLookMath.OccupantScale(d, mode);
			if (s < 0.999f)
			{
				__result.matrix = __result.matrix * Matrix4x4.Scale(new Vector3(s, 1f, s));
			}
		}
	}
}
