using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDER_RAILS_DRAWN_ON_THE_FACE (Artisan pass 4, bars wall_ladder_rides_on_rails, ladder_state_legible,
	/// portable_ladder_leans_on_its_wall). Under the oblique cut (pitLookMode 1) a pit ladder is printed along the wall it
	/// serves at the hole's own drawn depth, not as one fixed 0.6-cell sprite: the far face's height is the one the walls print
	/// (<see cref="SectionLayer_RMExcavationWalls.ObliqueFaceAt"/>), so the ladder's foot is the occupant's floor line.
	///
	/// One rule for every side: a LOWERED ladder is in the hole (down its wall from the rim to the floor), a RAISED one is out
	/// of it (slid up its rails and lying on the ground beyond its rim, pointing away from the hole). The rails stay fixed to
	/// the wall either way, so a raised ladder leaves bare rails in the hole.
	///   north wall (the far face, in view): rails and ladder on the face, rim to foot;
	///   east / west wall (seen edge-on): a narrow strip down the side wall, cut where the near lip hides the floor;
	///   south wall (the near face, hidden by the near ground like an occupant's legs): only what stands above the rim shows,
	///     the rail hooks and the ladder's top rungs.
	/// A portable ladder leans: its foot stands out from the wall on the floor (diagonal on the side walls). One too short for
	/// its wall keeps the def's flat art on the floor (RM_Building_Ladder.Graphic), and one leaning on a built wall keeps its own.
	/// Other looks (bevel, shadow well) keep the def's art.
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

		/// <summary>Front widths (cells): the ladder, and its rails just outside it. Side walls see both edge-on.</summary>
		public const float LadderWidth = 0.56f, RailWidth = 0.74f, SideLadderWidth = 0.24f, SideRailWidth = 0.3f;

		/// <summary>How far a lowered ladder's top and the rails' hooks stand above the rim (cells).</summary>
		public const float LadderAbove = 0.3f, RailAbove = 0.14f;

		/// <summary>The near (south) wall's ladder shows only above its rim, so it stands taller there (three rungs, the rails'
		/// hooks over them): first seen live as a sliver nobody could find (pass 4, l5_rig_lowered).</summary>
		public const float SouthAbove = 0.5f;

		/// <summary>Where a portable ladder's foot stands out from its wall (cells).</summary>
		public const float LeanOut = 0.62f;

		/// <summary>A portable on the far wall: its top and foot this far either side of the square's middle (cells), about a
		/// 15-degree slant over a 2 m face, so it reads as leaning where the fixed ladder runs straight down its rails.</summary>
		public const float FarLeanSide = 0.2f;

		/// <summary>A portable on the near wall: how far its top stands above the lip, and slants aside (cells).</summary>
		public const float NearPortableAbove = 0.72f, NearLeanSide = 0.2f;

		/// <summary>A raised ladder's length on the ground beyond its rim (cells): its drop plus the top, within these.</summary>
		public const float RaisedMin = 0.7f, RaisedMax = 2.2f;

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
			if (portable && (!RM_LadderUtility.Reaches(ladder) || RM_LadderParity.LeansOnWall(ladder)))
			{
				return false;   // lying flat on the floor, or upright on a built wall: the def's own art
			}
			bool steel = ladder.def.defName.IndexOf("Steel", StringComparison.Ordinal) >= 0;
			Material tile = steel ? SteelTile : WoodTile, cap = steel ? SteelCap : WoodCap;
			float capAspect = steel ? SteelCapAspect : WoodCapAspect;
			float tileAspect = steel ? SteelTileAspect : WoodTileAspect;
			float face = SectionLayer_RMExcavationWalls.ObliqueFaceAt(map, eng, c, out float rim, out float near);
			float drop = WallDrop(map, eng, c, rot, face, rim, near);
			float y = AltitudeLayer.Building.AltitudeFor();
			bool raised = comp.EffectivelyRaised;
			float cx = c.x + 0.5f, cz = c.z + 0.5f;
			switch (rot.AsInt)
			{
				case 0:   // north: the far face, rim at c.z + 1
				{
					float top = c.z + 1f;
					if (!portable)
					{
						Run(layer, RailTile, RailCap, RailTileAspect, RailCapAspect, new Vector2(cx, top + RailAbove), new Vector2(cx, top - drop), RailWidth, y);
					}
					if (raised)
					{
						float len = RaisedLength(drop);
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx, top + len), new Vector2(cx, top - 0.08f), LadderWidth, y + 0.02f);
					}
					else if (portable)
					{
						// leaning: the foot stands out on the floor and off to one side: a slant against the face, never the fixed ladder's
						// straight run (pass 4 read the old 0.12-cell slant as "stands straight")
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx + FarLeanSide, top + LadderAbove), new Vector2(cx - FarLeanSide, Mathf.Max(near + 0.05f, top - drop - LeanOut * 0.55f)), LadderWidth, y + 0.02f);
					}
					else
					{
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx, top + LadderAbove), new Vector2(cx, top - drop), LadderWidth, y + 0.02f);
					}
					break;
				}
				case 2:   // south: the near face is hidden; only what stands above the rim shows
				{
					float top = c.z;
					if (!portable)
					{
						Run(layer, RailTile, RailCap, RailTileAspect, RailCapAspect, new Vector2(cx, top + SouthAbove - 0.12f), new Vector2(cx, top), RailWidth, y);
					}
					if (raised)
					{
						float len = RaisedLength(drop);
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx, top - len), new Vector2(cx, top + 0.08f), LadderWidth, y + 0.02f);
					}
					else
					{
						// the top rungs over the lip; a leaning portable (a raid's rescue ladder comes in from the side the raid
						// stands on, mostly this one) stands out further and slants, so the player sees it go in
						if (portable)
						{
							Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx + NearLeanSide, top + NearPortableAbove), new Vector2(cx - NearLeanSide * 0.4f, top), LadderWidth, y + 0.02f);
						}
						else
						{
							Run(layer, tile, cap, tileAspect, capAspect, new Vector2(cx, top + SouthAbove), new Vector2(cx, top), LadderWidth, y + 0.02f);
						}
					}
					break;
				}
				default:   // east (1) / west (3): edge-on down the side wall, cut at the near lip
				{
					int s = rot.AsInt == 1 ? 1 : -1;
					float edge = rot.AsInt == 1 ? c.x + 1f : c.x;
					float foot = Mathf.Max(near, cz - drop);
					if (!portable)
					{
						Run(layer, RailTile, RailCap, RailTileAspect, RailCapAspect, new Vector2(edge - s * 0.13f, cz + RailAbove), new Vector2(edge - s * 0.13f, foot), SideRailWidth, y);
					}
					if (raised)
					{
						float len = RaisedLength(drop);
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(edge + s * len, cz), new Vector2(edge - s * 0.1f, cz), LadderWidth, y + 0.02f);
					}
					else if (portable)
					{
						// top on the rim, foot out on the floor: a diagonal; cut where it passes under the near lip
						Vector2 a = new Vector2(edge + s * 0.05f, cz + LadderAbove);
						Vector2 b = new Vector2(edge - s * LeanOut, cz - drop);
						if (b.y < near && a.y > near)
						{
							b = Vector2.Lerp(a, b, (a.y - near) / (a.y - b.y));
						}
						Run(layer, tile, cap, tileAspect, capAspect, a, b, LadderWidth * 0.92f, y + 0.02f);
					}
					else
					{
						Run(layer, tile, cap, tileAspect, capAspect, new Vector2(edge - s * 0.15f, cz + LadderAbove), new Vector2(edge - s * 0.15f, foot), SideLadderWidth, y + 0.02f);
					}
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

		public static float RaisedLength(float drop) => Mathf.Clamp(drop + LadderAbove, RaisedMin, RaisedMax);

		/// <summary>A ladder (or rail pair) from <paramref name="top"/> to <paramref name="bottom"/> (map x, z): the cap at the
		/// top, then whole tiles, the last one cut short. Each quad turns with the run, so a lean is one straight ladder.</summary>
		private static void Run(SectionLayer layer, Material tile, Material cap, float tileAspect, float capAspect, Vector2 top, Vector2 bottom,
			float width, float y)
		{
			// tile heights come from the FRONT width: an edge-on ladder is narrower, its rungs no closer
			float front = tile == RailTile ? RailWidth : LadderWidth;
			Vector2 d = bottom - top;
			float len = d.magnitude;
			if (len < 0.02f)
			{
				return;
			}
			d /= len;
			float rot = Mathf.Atan2(-d.x, -d.y) * Mathf.Rad2Deg;
			float capH = Mathf.Min(len, front * capAspect);
			float tileH = front * tileAspect;
			Quad(layer, cap, top + d * (capH * 0.5f), width, capH, rot, y + 0.001f, 1f - capH / (front * capAspect), 1f);
			float at = capH;
			while (at < len - 0.005f)
			{
				float h = Mathf.Min(tileH, len - at);
				Quad(layer, tile, top + d * (at + h * 0.5f), width, h, rot, y, 1f - h / tileH, 1f);
				at += h;
			}
		}

		private static readonly Vector2[] Uvs = new Vector2[4];

		/// <summary>One quad centred at <paramref name="c"/>, the texture's rows v0..v1 (1 = its top).</summary>
		private static void Quad(SectionLayer layer, Material mat, Vector2 c, float w, float h, float rot, float y, float v0, float v1)
		{
			Uvs[0] = new Vector2(0f, v0);
			Uvs[1] = new Vector2(0f, v1);
			Uvs[2] = new Vector2(1f, v1);
			Uvs[3] = new Vector2(1f, v0);
			Printer_Plane.PrintPlane(layer, new Vector3(c.x, y, c.y), new Vector2(w, h), mat, rot, false, Uvs, null, 0f);
		}
	}
}
