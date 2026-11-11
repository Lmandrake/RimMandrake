using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_DEPTH_DRAW_OFFSET_1 — the arithmetic of a pawn sinking with canal depth,
	/// Verse-free on purpose so Source/SelfTest/ compiles THIS production file (same
	/// discipline as RM_PitTrapMath).
	///
	/// Owner, 2026-10-02: <i>"The pawn should visibly rise up and lower down as they move
	/// over the depths. They should be low enough that it is visually clear how they could
	/// not possibly climb out (the walls are higher than their head by 20%)"</i>.
	///
	/// RimWorld's oblique view draws "lower" as further south on screen (vanilla's own
	/// flying lift is +0.6 z in Pawn_DrawTracker.FlyingOffset), so a pawn on a cell of
	/// depth D is drawn D × <see cref="DefaultSinkPerLevel"/> cells south of its tweened
	/// position. Between two cells the sink is interpolated by how far the tween has
	/// travelled, so the pawn rises and lowers smoothly rather than stepping.
	///
	/// PROVISIONAL (owner has not set a number beyond the 20 %): 0.3 cells per level, so a
	/// 2 m (D 4) floor sits 1.2 cells below the lip and the 4 m cap (D 8) 2.4. A humanlike reads about
	/// <see cref="HumanlikeFeetToHeadTop"/> = 1.0 cell feet-to-crown (PROVISIONAL, measure
	/// from a live frame), so at D = 4 the wall stands 1.2 × head height — his 20 %.
	/// Larger bodies poke further up; the 20 % bar is stated for a person.
	/// </summary>
	public static class RM_PitDrawMath
	{
		/// <summary>The sink stops growing at 4 m (8 levels of 0.5 m): a visual rule only, NOT the dig cap.
		/// SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR: the owner's pawn_height_ladder_legible card (2026-10-20) says a colonist keeps
		/// sinking to 4 m; the old cap of 4 levels stopped it at 2 m (validation_v2 X1 read red on it). Deeper than 4 m draws as
		/// 4 m; <see cref="ClampSinkToLip"/> still keeps the sprite inside the pit opening.</summary>
		public const int SinkCapLevels = 8;

		/// <summary>PROVISIONAL: cells of southward draw offset per level of depth.</summary>
		public const float DefaultSinkPerLevel = 0.3f;

		/// <summary>PROVISIONAL: a humanlike's on-screen height, feet to crown, in cells.</summary>
		public const float HumanlikeFeetToHeadTop = 1.0f;

		/// <summary>Sink (cells, positive = drawn lower) for a pawn standing on depth D.</summary>
		public static float SinkFor(int depth, float sinkPerLevel)
		{
			if (depth <= 0 || !(sinkPerLevel > 0f))
			{
				return 0f;
			}
			return Math.Min(depth, SinkCapLevels) * sinkPerLevel;
		}

		/// <summary>PIT_LIP_OCCLUDES_OUTSIDE_1 — the most a pawn on a cell whose centre is at
		/// <paramref name="cellCentreZ"/> may sink when the near (south) lip in its column is at
		/// <paramref name="lipZ"/>: its drawn centre never drops past the lip, so the sprite stays
		/// inside the pit opening and only its lower half goes behind the near bank. Without this a
		/// pawn on the pit's south row at D4 (sink 1.2) was drawn wholly south of the pit, over the
		/// ground outside it (owner's muffalo, 2026-10-06). NaN lipZ (no lip found) leaves the sink.</summary>
		public static float ClampSinkToLip(float sink, float cellCentreZ, float lipZ)
		{
			if (!(sink > 0f) || float.IsNaN(lipZ))
			{
				return sink > 0f ? sink : 0f;
			}
			float room = cellCentreZ - lipZ;
			if (room <= 0f)
			{
				return 0f;
			}
			return sink < room ? sink : room;
		}

		/// <summary>The near lip below a point: the north edge (z + 1) of the first square in column <paramref name="x"/>,
		/// scanning south from row <paramref name="zStart"/> - 1 for at most <paramref name="maxRows"/> rows, whose seen depth
		/// is shallower than <paramref name="d"/>. <paramref name="seenDepth"/> returns -1 off the map (the scan stops).
		/// NaN when no lip is found. Never the start row itself: the lip is SOUTH of it.</summary>
		public static float LipZBelow(int x, int zStart, int d, Func<int, int, int> seenDepth, int maxRows)
		{
			for (int k = 1; k <= maxRows; k++)
			{
				int s = seenDepth(x, zStart - k);
				if (s < 0)
				{
					break;
				}
				if (s < d)
				{
					return zStart - k + 1f;
				}
			}
			return float.NaN;
		}

		/// <summary>PIT_CLICK_FIX_SHIFTED_ONE_DOWN — the row a drafted-move click at height <paramref name="clickZ"/> (in row
		/// <paramref name="zClick"/>) means. A pawn in a pit is drawn <c>sink</c> cells south of its square, so ordering it to the
		/// clicked square left it drawn a row below the click (owner 2026-10-24: "only allow them to move 'shifted one down'").
		/// Scans the clicked row and up to <paramref name="maxRows"/> rows north while each stays sunk
		/// (<paramref name="restingSink"/> &gt; 0; NaN or 0 ends the run: off the map, or out of the pit) and returns the row
		/// whose RESTING drawn centre (z + 0.5 - sink) is nearest the click. Ties keep the clicked row; a click on unsunk ground
		/// is that ground.</summary>
		public static int PickRowForDrawnClick(int zClick, float clickZ, Func<int, float> restingSink, int maxRows)
		{
			float s0 = restingSink(zClick);
			if (float.IsNaN(s0) || !(s0 > 0f))
			{
				return zClick;
			}
			int best = zClick;
			float bestErr = Math.Abs(zClick + 0.5f - s0 - clickZ);
			for (int k = 1; k <= maxRows; k++)
			{
				int z = zClick + k;
				float s = restingSink(z);
				if (float.IsNaN(s) || !(s > 0f))
				{
					break;
				}
				float err = Math.Abs(z + 0.5f - s - clickZ);
				if (err < bestErr - 1e-4f)
				{
					best = z;
					bestErr = err;
				}
			}
			return best;
		}

		/// <summary>PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL — hold the DRAWN centre above the near lip of the column it is drawn in.
		/// The per-cell clamp measures room from the logical cell's centre, but the sink comes off the TWEENED draw position,
		/// and vanilla's PawnTweener lags the logical cell (spring 0.09 a frame: about 0.85 cell behind a walking boar at any
		/// game speed) and freezes outright while paused. A boar that stepped 38,22 -> 39,23 was sunk 1.5 (39,23's room) from
		/// a tween still on 38,22 and drawn a cell south of the pit, on the wall. <paramref name="d"/> &lt;= 0: unchanged.</summary>
		public static float HoldToDrawnLip(float sink, float drawX, float drawZ, int d, Func<int, int, int> seenDepth)
		{
			if (!(sink > 0f) || d <= 0)
			{
				return sink > 0f ? sink : 0f;
			}
			int x = (int)Math.Floor(drawX);
			int z = (int)Math.Floor(drawZ);
			return ClampSinkToLip(sink, drawZ, LipZBelow(x, z, d, seenDepth, SinkCapLevels * 2));
		}

		/// <summary>PIT_SINK_FIX_SOIL_STRIP_OVER_WALL — the lowest z the near-lip cover may reach in column <paramref name="x"/>.
		/// The cover hides the sprite band [<paramref name="bandBottom"/>, <paramref name="lipZ"/>] by re-drawing the GROUND there,
		/// cell by cell in each cell's terrain; on a cell holding a wall that terrain is the soil UNDER the wall, so a boar held on
		/// save e's C3 lip (band 20.675..22) painted a 2.65-cell soil strip over the room's south wall at z 20. Scanning south
		/// from the lip row, the first cell where <paramref name="blocksCover"/> holds (a drawn edifice) stops the cover at its
		/// north edge; what hangs lower is drawn over the wall, as vanilla draws any pawn standing north of one.
		/// No blocker in the band: <paramref name="bandBottom"/>.</summary>
		public static float CoverStopZ(int x, float lipZ, float bandBottom, Func<int, int, bool> blocksCover)
		{
			for (int z = (int)Math.Floor(lipZ) - 1; z + 1f > bandBottom; z--)
			{
				if (blocksCover(x, z))
				{
					return Math.Min(lipZ, z + 1f);
				}
			}
			return bandBottom;
		}

		/// <summary>PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM — half of vanilla's humanlike body mesh (1.5 x 1.5 cells). Measured in bridge
		/// run 1's s8_pitlip_close.png: a colonist's feet are drawn 0.75 cells below the drawn centre.</summary>
		public const float HumanlikeBodyHalf = 0.75f;

		/// <summary>The near-lip cover's body-size estimate of half a sprite's extent, in cells: sqrt(bodySize) x 1.2, held to 0.6..2.4, halved.</summary>
		public static float BodyEstimateHalf(float bodySize)
		{
			float s = (float)Math.Sqrt(Math.Max(bodySize, 0.2f)) * 1.2f;
			return 0.5f * (s < 0.6f ? 0.6f : (s > 2.4f ? 2.4f : s));
		}

		/// <summary>PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM — half the height the cover must span for a humanlike: the estimate (0.6 for a
		/// colonist) stopped 0.15 above the feet, which showed below the cover (s8). Never less than the body mesh's half.</summary>
		public static float HumanlikeHalfHeight(float bodySize)
		{
			return Math.Max(BodyEstimateHalf(bodySize), HumanlikeBodyHalf);
		}

		/// <summary>PROVISIONAL: a body's on-screen height feet to crown, in cells: a colonist's <see cref="HumanlikeFeetToHeadTop"/>
		/// scaled by sqrt(bodySize) (a muffalo, 2.4: 1.55).</summary>
		public static float BodyHeightCells(float bodySize)
		{
			return HumanlikeFeetToHeadTop * (float)Math.Sqrt(Math.Max(bodySize, 0.2f));
		}

		/// <summary>PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM — whether square (<paramref name="x"/>,<paramref name="z"/>) is a SIDE bank of the
		/// opening a pawn at depth <paramref name="d"/> is drawn in, column <paramref name="pawnX"/>: the square is shallower and the
		/// pawn's own column is at least as deep on that row. Seen from above, x is not foreshortened, so the part of a wide body
		/// (a muffalo on a corner square) that reaches over the west or east bank is below that bank's ground and hidden by it.
		/// Rows past the far (north) rim are not side banks: there the sprite stands up in front of the far wall.</summary>
		public static bool BesideOpening(int x, int z, int pawnX, int d, Func<int, int, int> seenDepth)
		{
			int s = seenDepth(x, z);
			return d > 0 && s >= 0 && s < d && seenDepth(pawnX, z) >= d;
		}

		/// <summary>PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM — the top of the band a side bank hides of a sprite spanning
		/// [<paramref name="bottom"/>, <paramref name="top"/>]: the share of the body below ground, SinkFor(d) over its height
		/// <paramref name="bodyHeight"/>, from the bottom up. A colonist at D4 or deeper, or a muffalo at D6, is wholly hidden.</summary>
		public static float SideHiddenTop(float bottom, float top, int d, float sinkPerLevel, float bodyHeight)
		{
			if (d <= 0 || !(top > bottom))
			{
				return bottom;
			}
			float f = bodyHeight > 0f ? SinkFor(d, sinkPerLevel) / bodyHeight : 1f;
			f = f < 0f ? 0f : (f > 1f ? 1f : f);
			return bottom + (top - bottom) * f;
		}

		/// <summary>PIT_COVER_FIX_DROPS_THE_SUN_SHADOW — whether ground point (<paramref name="px"/>,<paramref name="pz"/>) lies in a
		/// vanilla static sun shadow. SectionLayer_SunShadows gives each edifice cell (i,j) with staticSunShadowHeight h a flat quad
		/// plus W/E/S skirts whose far vertices carry alpha h; its shader moves a vertex by alpha x _CastVect.xz. The union drawn is
		/// therefore each cell swept by h x (vx,vz): p is shaded iff p - t·h·v lies in a caster's cell for some t in [0,1].
		/// <paramref name="heightAt"/> is the caster height of a cell (0: none); <paramref name="hMax"/> bounds it, so only cells
		/// within hMax x v of p are read. vz is always below -0.9 in GenCelestial, so a shadow never reaches north.</summary>
		public static bool SunShadowed(float px, float pz, float vx, float vz, float hMax, Func<int, int, float> heightAt)
		{
			if (hMax <= 0f) return false;
			int x0 = (int)Math.Floor(Math.Min(px, px - hMax * vx)), x1 = (int)Math.Floor(Math.Max(px, px - hMax * vx));
			int z0 = (int)Math.Floor(Math.Min(pz, pz - hMax * vz)), z1 = (int)Math.Floor(Math.Max(pz, pz - hMax * vz));
			for (int i = x0; i <= x1; i++)
			{
				for (int j = z0; j <= z1; j++)
				{
					float h = heightAt(i, j);
					if (h > 0f && SweptCellHits(px, pz, i, j, h * vx, h * vz)) return true;
				}
			}
			return false;
		}

		/// <summary>The caster cells (x, z, height) whose sweep can reach the rect [l,r]x[a,b]: every cell with height &gt; 0 within
		/// hMax x v back from it. Gathered once per cover piece, so each shade vertex tests only these (SunShadowedBy).</summary>
		public static void SunCasters(float l, float r, float a, float b, float vx, float vz, float hMax, Func<int, int, float> heightAt,
			System.Collections.Generic.List<(int x, int z, float h)> into)
		{
			into.Clear();
			if (hMax <= 0f) return;
			int x0 = (int)Math.Floor(l - Math.Max(0f, hMax * vx)), x1 = (int)Math.Floor(r - Math.Min(0f, hMax * vx));
			int z0 = (int)Math.Floor(a - Math.Max(0f, hMax * vz)), z1 = (int)Math.Floor(b - Math.Min(0f, hMax * vz));
			for (int i = x0; i <= x1; i++)
			{
				for (int j = z0; j <= z1; j++)
				{
					float h = heightAt(i, j);
					if (h > 0f) into.Add((i, j, h));
				}
			}
		}

		/// <summary>SunShadowed against a caster list from SunCasters.</summary>
		public static bool SunShadowedBy(float px, float pz, float vx, float vz, System.Collections.Generic.List<(int x, int z, float h)> casters)
		{
			for (int k = 0; k < casters.Count; k++)
			{
				var c = casters[k];
				if (SweptCellHits(px, pz, c.x, c.z, c.h * vx, c.h * vz)) return true;
			}
			return false;
		}

		/// <summary>True when p - t·(dx,dz) lies inside the unit cell (i,j) for some t in [0,1] (slab test). The cell is shrunk by
		/// 1e-4 so a point ON a caster's edge (the cover's bottom row of vertices, which stops at a wall's north edge) is not
		/// shaded by a shadow that only leaves the other way.</summary>
		public static bool SweptCellHits(float px, float pz, int i, int j, float dx, float dz)
		{
			const float e = 1e-4f;
			float lo = 0f, hi = 1f;
			bool Slab(float p, float d, float min)
			{
				// min + e <= p - t d <= min + 1 - e
				if (Math.Abs(d) < 1e-6f) return p >= min + e && p <= min + 1f - e;
				float ta = (p - min - e) / d, tb = (p - min - 1f + e) / d;
				lo = Math.Max(lo, Math.Min(ta, tb));
				hi = Math.Min(hi, Math.Max(ta, tb));
				return lo <= hi;
			}
			return Slab(px, dx, i) && Slab(pz, dz, j);
		}

		/// <summary>Tween progress from the centre of the cell a pawn is leaving
		/// (<paramref name="ax"/>,<paramref name="az"/>) toward the next cell's centre, given the
		/// drawn position (<paramref name="px"/>,<paramref name="pz"/>). Projected onto the
		/// step, clamped 0..1.</summary>
		public static float StepProgress(float ax, float az, float bx, float bz, float px, float pz)
		{
			float dx = bx - ax;
			float dz = bz - az;
			float len2 = dx * dx + dz * dz;
			if (len2 <= 1e-6f)
			{
				return 1f;
			}
			float t = ((px - ax) * dx + (pz - az) * dz) / len2;
			return t < 0f ? 0f : (t > 1f ? 1f : t);
		}

		/// <summary>The wall above an occupant's crown as a ratio of their height: the lip is
		/// D × sink above the floor. 1.2 is the owner's 20 % bar.</summary>
		public static float WallOverHeadRatio(int depth, float sinkPerLevel, float feetToHeadTop)
		{
			if (!(feetToHeadTop > 0f))
			{
				return 0f;
			}
			return SinkFor(depth, sinkPerLevel) / feetToHeadTop;
		}
	}
}
