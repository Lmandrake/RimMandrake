using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDER_RAILS_DRAWN_ON_THE_FACE (Artisan pass 4, pass 8; bars wall_ladder_rides_on_rails, ladder_state_legible,
	/// portable_ladder_leans_on_its_wall). Under the oblique cut (pitLookMode 1) a pit ladder is printed along the wall it
	/// serves at the hole's own drawn depth, not as one fixed 0.6-cell sprite: the far face's height is the one the walls print
	/// (<see cref="SectionLayer_RMExcavationWalls.ObliqueFaceAt"/>), so the ladder's foot is the occupant's floor line.
	///
	/// The geometry is RM_LadderRigMath's (Verse-free, checked offline): rails fixed to the wall in both states, each rail its
	/// own column of the rail texture so its stroke reads at play zoom; a LOWERED ladder rides between them down the wall, a
	/// RAISED one is out of the hole (slid up its rails, lying on the ground beyond its rim), leaving bare rails.
	///   north wall (the far face, in view): rails and ladder on the face, rim to foot;
	///   east / west wall (seen nearly edge-on): both rails and both posts at full stroke, the rungs between shortened;
	///   south wall (the near face, hidden by the near ground like an occupant's legs): the rails' hooks over the lip and the
	///     lowered ladder's top rungs between them.
	/// A portable ladder has no rails and leans (top at the rim, foot out on the floor: a slant on every wall). One too short
	/// for its wall lies flat on the pit's drawn floor (its short art), and frees nobody (RM_LadderRules.LadderLetsOut asks
	/// RM_LadderUtility.Reaches, the rule this drawing is chosen by). One leaning on a built wall keeps the def's art, as do
	/// other looks (bevel, shadow well).
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_LadderDraw
	{
		private const string Dir = "Things/Building/FlowWorks/Canals/LadderRig/";
		private static readonly Material WoodTile = MaterialPool.MatFrom(Dir + "RM_LadderTile_Wood", ShaderDatabase.Cutout);
		private static readonly Material WoodCap = MaterialPool.MatFrom(Dir + "RM_LadderCap_Wood", ShaderDatabase.Cutout);
		private static readonly Material SteelTile = MaterialPool.MatFrom(Dir + "RM_LadderTile_Steel", ShaderDatabase.Cutout);
		private static readonly Material SteelCap = MaterialPool.MatFrom(Dir + "RM_LadderCap_Steel", ShaderDatabase.Cutout);
		private static readonly Material RailTile = MaterialPool.MatFrom(Dir + "RM_LadderRailTile", ShaderDatabase.Cutout);
		private static readonly Material RailCap = MaterialPool.MatFrom(Dir + "RM_LadderRailCap", ShaderDatabase.Cutout);

		// tile shapes (height / width of the textures, RM_LadderDraw's slice.py)
		private const float WoodTileAspect = 44f / 160f, SteelTileAspect = 43f / 160f, WoodCapAspect = 59f / 160f, SteelCapAspect = 65f / 160f;
		private const float RailTileAspect = 49f / 200f, RailCapAspect = 49f / 200f;

		/// <summary>Print <paramref name="ladder"/> along its wall; false = not this look (the caller prints the def's art).</summary>
		public static bool TryPrint(Building ladder, RM_CompLadder comp, SectionLayer layer)
		{
			if (RimMandrakeFlowWorksSettings.pitLookMode != RM_PitLookMath.Oblique || comp == null || !ladder.Spawned)
			{
				return false;
			}
			Map map = ladder.Map;
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			IntVec3 c = ladder.Position;
			Rot4 rot = ladder.Rotation;
			if (eng == null || eng.HollowDepthAt(c) <= 0 || RM_LadderUtility.WallRotAt(map, c, rot) != rot.AsInt)
			{
				return false;   // on undug ground or leading nowhere: the def's art (and its inspect line) say so
			}
			bool portable = comp.Props.portable;
			if (portable && RM_LadderParity.LeansOnWall(ladder))
			{
				return false;   // upright on a built wall: the def's own art
			}
			bool reaches = !portable || RM_LadderUtility.Reaches(ladder);
			Material flat = reaches ? null : comp.ShortGraphic?.MatSingle;
			if (!reaches && flat == null)
			{
				return false;   // no short art: the def's own
			}
			bool steel = ladder.def.defName.IndexOf("Steel", StringComparison.Ordinal) >= 0;
			Material tile = steel ? SteelTile : WoodTile, cap = steel ? SteelCap : WoodCap;
			float capAspect = steel ? SteelCapAspect : WoodCapAspect;
			float tileAspect = steel ? SteelTileAspect : WoodTileAspect;
			float face = SectionLayer_RMExcavationWalls.ObliqueFaceAt(map, eng, c, out float rim, out float near);
			float drop = WallDrop(map, eng, c, rot, face, rim, near);
			float y = AltitudeLayer.Building.AltitudeFor();
			List<RM_LadderRigMath.Stroke> strokes = RM_LadderRigMath.Strokes(rot.AsInt, c.x, c.z, face, drop, rim, near,
				comp.EffectivelyRaised, portable, reaches, steel);
			for (int i = 0; i < strokes.Count; i++)
			{
				RM_LadderRigMath.Stroke s = strokes[i];
				switch (s.Kind)
				{
					case RM_LadderRigMath.Kind.Rail:
						Run(layer, RailTile, RailCap, RailTileAspect, RailCapAspect, s, y);
						break;
					case RM_LadderRigMath.Kind.Ladder:
						Run(layer, tile, cap, tileAspect, capAspect, s, y);
						break;
					default:
						Quad(layer, flat, new Vector2(s.X0, s.Z0), s.Width, s.Width, s.Angle, y + s.Lift, 0f, 1f, 0f, 1f);
						break;
				}
			}
			return true;
		}

		/// <summary>The drawn drop down the wall the ladder serves (cells): the far face itself on the north wall, else the same
		/// column scale for the drop to that wall's ground.</summary>
		private static float WallDrop(Map map, RM_MapComponent_Excavation eng, IntVec3 c, Rot4 rot, float face, float rim, float near)
		{
			if (rot == Rot4.North)
			{
				return face;
			}
			int d = eng.HollowDepthAt(c);
			int wall = SectionLayer_RMExcavationWalls.NeighbourLevel(map, eng, c + rot.FacingCell, d);
			int drop = Math.Max(0, d - Math.Max(0, wall));
			return RM_PitLookMath.ObliqueFace(drop, Mathf.Max(1f, rim - near), RimMandrakeFlowWorksSettings.pitSinkPerLevel, 0.15f);
		}

		/// <summary>One stroke (a rail, a ladder or a slice of one) from its top to its bottom: the cap at the top, then whole
		/// tiles, the last one cut short, each showing the stroke's texture columns. Tile heights come from the whole texture's
		/// width at this scale (the stroke's Front), so a slice keeps its ladder's rung spacing and a rail its bracket spacing.
		/// Each quad turns with the run, so a lean is one straight ladder.</summary>
		private static void Run(SectionLayer layer, Material tile, Material cap, float tileAspect, float capAspect, RM_LadderRigMath.Stroke s, float y)
		{
			Vector2 top = new Vector2(s.X0, s.Z0), bottom = new Vector2(s.X1, s.Z1);
			Vector2 d = bottom - top;
			float len = d.magnitude;
			if (len < 0.02f)
			{
				return;
			}
			d /= len;
			float rot = Mathf.Atan2(-d.x, -d.y) * Mathf.Rad2Deg;
			float capFull = s.Front * capAspect, tileH = s.Front * tileAspect;
			float capH = Mathf.Min(len, capFull);
			y += s.Lift;
			Quad(layer, cap, top + d * (capH * 0.5f), s.Width, capH, rot, y + 0.001f, s.U0, s.U1, 1f - capH / capFull, 1f);
			float at = capH;
			while (at < len - 0.005f)
			{
				float h = Mathf.Min(tileH, len - at);
				Quad(layer, tile, top + d * (at + h * 0.5f), s.Width, h, rot, y, s.U0, s.U1, 1f - h / tileH, 1f);
				at += h;
			}
		}

		private static readonly Vector2[] Uvs = new Vector2[4];

		/// <summary>One quad centred at <paramref name="c"/>: the texture's columns u0..u1 and rows v0..v1 (v 1 = its top).</summary>
		private static void Quad(SectionLayer layer, Material mat, Vector2 c, float w, float h, float rot, float y, float u0, float u1, float v0, float v1)
		{
			Uvs[0] = new Vector2(u0, v0);
			Uvs[1] = new Vector2(u0, v1);
			Uvs[2] = new Vector2(u1, v1);
			Uvs[3] = new Vector2(u1, v0);
			Printer_Plane.PrintPlane(layer, new Vector3(c.x, y, c.y), new Vector2(w, h), mat, rot, false, Uvs, null, 0f);
		}
	}
}
