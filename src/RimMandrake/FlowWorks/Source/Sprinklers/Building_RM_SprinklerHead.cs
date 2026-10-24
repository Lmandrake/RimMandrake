using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE: the things set ON a universal pipe print on the pipe's drawn centreline in their
	/// cell (RM_PipeSeatMath), not at the cell centre, so a head or faucet on a bend stands on the bend. Position only: the
	/// fitting art is a 3/4-view saddle, and turning it with the bend would tip its dome over.
	/// </summary>
	public static class RM_PipeSeat
	{
		/// <summary>The pipe in <paramref name="onPipe"/>'s cell, or null.</summary>
		public static Thing PipeUnder(Thing onPipe)
		{
			if (onPipe?.Map == null) return null;
			foreach (Thing t in onPipe.Position.GetThingList(onPipe.Map))
			{
				if (t != onPipe && RM_LiquidNet.IsPipe(t)) return t;
			}
			return null;
		}

		/// <summary>The link mask the pipe is DRAWN with (Graphic_Linked's own test, our Harmony postfix included), its look
		/// from the atlas it is drawn from, and so the seat offset (world x/z). Zero when there is no linked pipe here.</summary>
		public static Vector3 Offset(Thing onPipe)
		{
			Thing pipe = PipeUnder(onPipe);
			if (pipe == null || !(pipe.Graphic is Graphic_Linked gl)) return Vector3.zero;
			int mask = 0;
			for (int i = 0; i < 4; i++)
			{
				IntVec3 c = pipe.Position + GenAdj.CardinalDirections[i];
				if (gl.ShouldLinkWith(c, pipe)) mask |= 1 << i;
			}
			// the atlas actually drawn names the look; the style record only when the graphic carries no path
			string look = RM_PipeSeatMath.LookOfTexPath(gl.SubGraphic?.path ?? gl.path) ?? PipeLook.LookOfThing(pipe);
			RM_PipeSeatMath.Seat(mask, look, out float x, out float z);
			return new Vector3(x, 0f, z);
		}

		/// <summary>ThingWithComps.Print for an unrotatable single-graphic fitting, its plane moved by the seat offset (the
		/// same plane, atlas, shadow and comp overlays vanilla prints; only the centre differs). Call it from Print.</summary>
		public static void Print(SectionLayer layer, ThingWithComps onPipe)
		{
			Graphic g = onPipe.Graphic;
			bool hidden = onPipe.def.dontPrint || g == null;
			foreach (ThingComp comp in onPipe.AllComps) hidden |= comp.DontDrawParent();
			if (!hidden)
			{
				Vector3 center = onPipe.TrueCenter() + g.DrawOffset(onPipe.Rotation) + Offset(onPipe);
				Material mat = g.MatAt(onPipe.Rotation, onPipe);
				Graphic.TryGetTextureAtlasReplacementInfo(mat, onPipe.def.category.ToAtlasGroup(), false, true, out mat, out Vector2[] uvs, out Color32 vc);
				Printer_Plane.PrintPlane(layer, center, g.drawSize, mat, 0f, false, uvs, new Color32[4] { vc, vc, vc, vc });
				g.ShadowGraphic?.Print(layer, onPipe, 0f);
			}
			foreach (ThingComp comp in onPipe.AllComps) comp.PostPrintOnto(layer);
		}
	}

	/// <summary>RM_SprinklerHead's thing class: a plain building that prints on the pipe's centreline (RM_PipeSeat).</summary>
	public class Building_RM_SprinklerHead : Building
	{
		public override void Print(SectionLayer layer)
		{
			RM_PipeSeat.Print(layer, this);
		}
	}
}
