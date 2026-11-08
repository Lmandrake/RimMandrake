using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDER_RAILS_DRAWN_ON_THE_FACE, the ladder rig's geometry (bars wall_ladder_rides_on_rails, ladder_state_legible,
	/// portable_ladder_leans_on_its_wall). What RM_LadderDraw prints under the oblique cut, as strokes in map x/z: a rail, a
	/// ladder (or one slice of one) run from its top (cap) end to its bottom, or a flat portable lying on the floor. Verse-free,
	/// so the SelfTest checks the drawing's geometry without the game.
	///
	/// The rails are fixed to their wall and drawn in both states; the ladder rides between them when lowered and lies out on
	/// the ground beyond the rim when raised (slid up its rails):
	///   north (the far face, in view): two rails from over the rim down to the face foot, the ladder between them;
	///   east / west (seen nearly edge-on): the rig as a ladder seen at an angle: both rails and both posts at their full stroke,
	///     the rungs between the posts shortened, all down the side wall to where the near lip hides the floor;
	///   south (the near face, hidden by the near ground): the two rails' hooks over the lip, the lowered ladder's top between.
	/// Each rail is its own column cut from one side of the rail texture, so its stroke reads (one quad of the whole 0.74-cell
	/// rail texture drew each rail 0.04 cells wide: under 3 px at 64 px a cell, so pass 7 saw no rails at all).
	///
	/// A portable has no rails and is never raised; it leans (top at the rim, foot out on the floor, a slant on every wall).
	/// One too short for its wall lies flat on the floor (Flat); it frees nobody (RM_LadderRules.LadderLetsOut asks
	/// RM_LadderUtility.Reaches, the same rule this drawing is chosen by).
	/// </summary>
	public static class RM_LadderRigMath
	{
		public enum Kind { Rail, Ladder, Flat }

		public struct Stroke
		{
			public Kind Kind;

			/// <summary>Top (the cap end) and bottom of the run, map x/z. Flat: both are its middle.</summary>
			public float X0, Z0, X1, Z1;

			/// <summary>The quad's width across the run (cells). Flat: its square size.</summary>
			public float Width;

			/// <summary>The texture columns the quad shows (0..1).</summary>
			public float U0, U1;

			/// <summary>The whole texture's width at this scale (cells): sets the tile and cap heights, so the slices of one
			/// ladder keep its rung spacing.</summary>
			public float Front;

			/// <summary>Flat only: degrees the flat art turns (0 = lengthwise along x, as drawn).</summary>
			public float Angle;

			/// <summary>Altitude above the rig's base (the ladder prints over its rails).</summary>
			public float Lift;
		}

		// ---- texture layout (measured from the PNGs in Textures/Things/Building/FlowWorks/Canals/LadderRig) ----

		/// <summary>RM_LadderRailTile / RM_LadderRailCap (200 wide): each rail with its brackets and hook fits in 28 columns at
		/// its own side; the rail itself is columns 7-17 (left) and 182-192 (right).</summary>
		public const float RailSliceU = 28f / 200f, RailInSlice = 12.5f / 28f, RailStrokeInSlice = 11f / 28f;

		/// <summary>The wooden ladder's tile and cap (160 wide): left post 21-39, rungs 40-118, right post 119-137.</summary>
		public const float WoodPostL0 = 21f / 160f, WoodPostL1 = 40f / 160f, WoodPostR0 = 119f / 160f, WoodPostR1 = 138f / 160f;

		/// <summary>The steel ladder's tile and cap (160 wide): left post 37-48, rungs 49-114, right post 115-127.</summary>
		public const float SteelPostL0 = 37f / 160f, SteelPostL1 = 49f / 160f, SteelPostR0 = 115f / 160f, SteelPostR1 = 128f / 160f;

		// ---- geometry (cells) ----

		/// <summary>The ladder texture's width face-on (cells).</summary>
		public const float LadderWidth = 0.56f;

		/// <summary>One rail column's width: its rail stroke is RailSliceWidth * RailStrokeInSlice, about 0.086 cells (5.5 px at
		/// 64 px a cell, 2 px at 23).</summary>
		public const float RailSliceWidth = 0.22f;

		/// <summary>The rail texture's width at that scale (sets the rail's bracket spacing).</summary>
		public const float RailFront = RailSliceWidth / RailSliceU;

		/// <summary>Face-on rails (north, south): each this far from the ladder's middle, just outside its posts.</summary>
		public const float RailHalf = 0.29f;

		/// <summary>How far a lowered ladder's top and the rails' tops stand above the rim.</summary>
		public const float LadderAbove = 0.3f, RailAbove = 0.18f;

		/// <summary>The near (south) wall: the lowered ladder's top rungs and the rails' hooks over the lip (all that shows of a
		/// ladder down the hidden near face; pass 4 saw a shorter stub as a sliver nobody could find).</summary>
		public const float SouthAbove = 0.5f, SouthHookAbove = 0.34f;

		/// <summary>Side walls: the rig's middle this far in from the wall's edge, its rails this far either side of that, and
		/// the shortened rungs' width between the posts.</summary>
		public const float SideIn = 0.26f, SideRailHalf = 0.18f, SideRungWidth = 0.11f;

		/// <summary>A raised ladder's length on the ground beyond its rim: its drop plus its top, within these.</summary>
		public const float RaisedMin = 0.7f, RaisedMax = 2.2f;

		/// <summary>Where a portable ladder's foot stands out from its wall.</summary>
		public const float LeanOut = 0.62f;

		/// <summary>A portable on the far wall: its top and foot this far either side of the square's middle, about 18 degrees
		/// over a 2 m face (pass 4 read a 0.12-cell slant as standing straight).</summary>
		public const float FarLeanSide = 0.3f;

		/// <summary>A portable on the near wall: how far its top stands above the lip, and slants aside.</summary>
		public const float NearPortableAbove = 0.72f, NearLeanSide = 0.2f;

		/// <summary>The flat portable's art (RM_LadderPortableFlat, drawn 1 x 1): its half length and half thickness.</summary>
		public const float FlatSize = 1f, FlatHalfLength = 0.47f, FlatHalfThick = 0.22f, FlatSideIn = 0.3f;

		public static float RaisedLength(float drop) => Math.Max(RaisedMin, Math.Min(RaisedMax, drop + LadderAbove));

		/// <summary>The rig of a ladder on the pit square (cellX, cellZ) hung on wall <paramref name="rot"/> (Rot4 index).
		/// face: the oblique far face's height over the square's column; drop: the drawn drop down this wall (the face itself on
		/// the north wall); rim / near: the column's far and near rim z. reaches: a portable long enough for its wall.</summary>
		public static List<Stroke> Strokes(int rot, int cellX, int cellZ, float face, float drop, float rim, float near, bool raised,
			bool portable, bool reaches, bool steel)
		{
			List<Stroke> list = new List<Stroke>();
			raised = raised && !portable;   // a portable rides no rails (RM_CompLadder.EffectivelyRaised)
			float cx = cellX + 0.5f, cz = cellZ + 0.5f;
			if (portable && !reaches)
			{
				list.Add(FlatOnFloor(rot, cellX, cx, cz, face, rim, near));
				return list;
			}
			switch (rot)
			{
				case 0:   // north: the far face, its rim at the square's north edge
				{
					float top = cellZ + 1f;
					if (!portable)
					{
						FaceRails(list, cx, top + RailAbove, top - drop);
					}
					if (raised)
					{
						list.Add(Ladder(cx, top + RaisedLength(drop), cx, top - 0.08f));
					}
					else if (portable)
					{
						// leaning: the foot stands out on the floor and off to one side
						list.Add(Ladder(cx + FarLeanSide, top + LadderAbove, cx - FarLeanSide, Math.Max(near + 0.05f, top - drop - LeanOut * 0.55f)));
					}
					else
					{
						list.Add(Ladder(cx, top + LadderAbove, cx, top - drop));
					}
					break;
				}
				case 2:   // south: the near face is hidden; only what stands above the lip shows
				{
					float top = cellZ;
					if (!portable)
					{
						FaceRails(list, cx, top + SouthHookAbove, top);
					}
					if (raised)
					{
						list.Add(Ladder(cx, top - RaisedLength(drop), cx, top + 0.08f));
					}
					else if (portable)
					{
						// a raid's rescue ladder comes in from the side the raid stands on, mostly this one: it stands out and slants
						list.Add(Ladder(cx + NearLeanSide, top + NearPortableAbove, cx - NearLeanSide * 0.4f, top));
					}
					else
					{
						list.Add(Ladder(cx, top + SouthAbove, cx, top));
					}
					break;
				}
				default:   // east (1) / west (3): nearly edge-on down the side wall, cut at the near lip
				{
					int s = rot == 1 ? 1 : -1;
					float edge = rot == 1 ? cellX + 1f : cellX;
					float foot = Math.Max(near, cz - drop);
					float mid = edge - s * SideIn;
					if (!portable)
					{
						Rail(list, mid - SideRailHalf, true, cz + RailAbove, foot);
						Rail(list, mid + SideRailHalf, false, cz + RailAbove, foot);
					}
					if (raised)
					{
						list.Add(Ladder(edge + s * RaisedLength(drop), cz, edge - s * 0.1f, cz));
					}
					else if (portable)
					{
						// top on the rim, foot out on the floor: a diagonal, cut where it passes under the near lip
						float ax = edge + s * 0.05f, az = cz + LadderAbove, bx = edge - s * LeanOut, bz = cz - drop;
						if (bz < near && az > near)
						{
							float t = (az - near) / (az - bz);
							bx = ax + (bx - ax) * t;
							bz = near;
						}
						Stroke p = Ladder(ax, az, bx, bz);
						p.Width = LadderWidth * 0.92f;
						list.Add(p);
					}
					else
					{
						SideLadder(list, mid, cz + LadderAbove, foot, steel);
					}
					break;
				}
			}
			return list;
		}

		/// <summary>The rail's own line x (the middle of its stroke, not of its column).</summary>
		public static float RailLine(Stroke s)
		{
			float off = RailSliceWidth * (0.5f - RailInSlice);
			return s.U0 <= 0f ? s.X0 - off : s.X0 + off;
		}

		/// <summary>The rail's stroke width (cells).</summary>
		public static float RailStroke(Stroke s) => s.Width * RailStrokeInSlice / (s.U1 - s.U0) * RailSliceU;

		/// <summary>Degrees off the wall's straight-down line (screen -z) a run slants.</summary>
		public static float LeanDegrees(Stroke s)
		{
			return (float)(Math.Atan2(Math.Abs(s.X1 - s.X0), Math.Abs(s.Z1 - s.Z0)) * 180.0 / Math.PI);
		}

		private static Stroke Ladder(float x0, float z0, float x1, float z1)
		{
			return new Stroke { Kind = Kind.Ladder, X0 = x0, Z0 = z0, X1 = x1, Z1 = z1, Width = LadderWidth, U0 = 0f, U1 = 1f, Front = LadderWidth, Lift = 0.02f };
		}

		/// <summary>One rail whose line is at <paramref name="line"/>: the left (west) column of the rail texture, or the right.</summary>
		private static void Rail(List<Stroke> list, float line, bool left, float zTop, float zBottom)
		{
			float off = RailSliceWidth * (0.5f - RailInSlice);
			float x = left ? line + off : line - off;
			list.Add(new Stroke
			{
				Kind = Kind.Rail, X0 = x, Z0 = zTop, X1 = x, Z1 = zBottom, Width = RailSliceWidth,
				U0 = left ? 0f : 1f - RailSliceU, U1 = left ? RailSliceU : 1f, Front = RailFront, Lift = 0f,
			});
		}

		private static void FaceRails(List<Stroke> list, float cx, float zTop, float zBottom)
		{
			Rail(list, cx - RailHalf, true, zTop, zBottom);
			Rail(list, cx + RailHalf, false, zTop, zBottom);
		}

		/// <summary>A ladder seen at an angle down a side wall: each post at its full stroke, the rungs between them shortened.</summary>
		private static void SideLadder(List<Stroke> list, float mid, float zTop, float zBottom, bool steel)
		{
			float a0 = steel ? SteelPostL0 : WoodPostL0, a1 = steel ? SteelPostL1 : WoodPostL1;
			float b0 = steel ? SteelPostR0 : WoodPostR0, b1 = steel ? SteelPostR1 : WoodPostR1;
			float pl = (a1 - a0) * LadderWidth, pr = (b1 - b0) * LadderWidth;
			float x = mid - (pl + SideRungWidth + pr) * 0.5f;
			list.Add(Slice(x + pl * 0.5f, zTop, zBottom, pl, a0, a1));
			list.Add(Slice(x + pl + SideRungWidth * 0.5f, zTop, zBottom, SideRungWidth, a1, b0));
			list.Add(Slice(x + pl + SideRungWidth + pr * 0.5f, zTop, zBottom, pr, b0, b1));
		}

		private static Stroke Slice(float x, float zTop, float zBottom, float w, float u0, float u1)
		{
			Stroke s = Ladder(x, zTop, x, zBottom);
			s.Width = w;
			s.U0 = u0;
			s.U1 = u1;
			return s;
		}

		/// <summary>A portable too short for its wall, lying on the floor of its square's row: at the square's own drawn floor
		/// (its middle less the face), kept in view between the near lip and the face foot (the lip wins in a shallow view),
		/// lengthwise along its wall.</summary>
		private static Stroke FlatOnFloor(int rot, int cellX, float cx, float cz, float face, float rim, float near)
		{
			bool side = rot == 1 || rot == 3;
			float half = side ? FlatHalfLength : FlatHalfThick;
			float z = Math.Max(near + half, Math.Min(cz - face, rim - face - half));
			float x = cx;
			if (side)
			{
				x = rot == 1 ? cellX + 1f - FlatSideIn : cellX + FlatSideIn;
			}
			return new Stroke { Kind = Kind.Flat, X0 = x, Z0 = z, X1 = x, Z1 = z, Width = FlatSize, U0 = 0f, U1 = 1f, Front = FlatSize, Angle = side ? 90f : 0f, Lift = 0.02f };
		}
	}
}
