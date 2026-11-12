namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL. Owner 2026-11-12: "a ladder hanging into water is shown entirely over
	/// the water regardless of depth. The water really should go up to some level on the ladder as though it is part
	/// submerged. Same for spikes and other pit installations."
	///
	/// Pit liquid is a TERRAIN (RM_MapComponent_Excavation.ApplyFillTerrain swaps the base terrain, AltitudeLayer.Terrain),
	/// so every fitting standing in the pit (ladders at Building, the ramp at FloorEmplacement, the spikes' realtime mesh)
	/// draws over it whole. The wall faces show liquid by being drawn SHORTER (RM_WallFaceMath.ExposedDrop), which leaves the
	/// liquid terrain showing; the fittings now do the same: the part of the sprite under the liquid is cut away, so the
	/// liquid's own terrain shows there. One rule for every liquid (water, tar, oil, acid, chemfuel...): no colour lookup.
	///
	/// The cut follows the face it hangs on, so the waterline on a ladder is the waterline on its wall:
	///  - ladder hung north: drawn over the north face; liquid covers it below z = 1 - NorthFaceHeight(exposed drop);
	///  - hung east / west: over the side face; covered on the pit side of x = 1 - SideFaceWidth / x = SideFaceWidth;
	///  - hung south: only its top shows above the near rim, which liquid never reaches: never cut;
	///  - a portable ladder lying flat on the floor: under the liquid from the first level.
	/// The ramp is covered from its downhill end by fill / rise. A stake is covered from its foot by the liquid's metres over
	/// RM_SpikeDrawMath.SubmergeMetres (still gone at 1 m). Dry: nothing is cut.
	/// The ramp and the stakes take the TRUE level in notches (one notch = 0.5 m; whole notch + the cell's part-notch), kept
	/// to quarter notches (LevelNote) so the map mesh and the realtime spikes re-draw only on a real move. A hung ladder takes
	/// the whole-notch fill its wall face is drawn with (HungLadderLevel): the two can differ by a notch, and the ladder must
	/// meet its wall.
	/// Verse-free: SelfTest SubmergeDrawChecks runs this.
	/// </summary>
	public static class RM_SubmergeMath
	{
		/// <summary>Cut steps a share is drawn at (the spikes' mesh key and the proof read both use it).</summary>
		public const int Steps = 32;

		/// <summary>Sprite sides a cut starts from: the covered part is the one nearest this side.</summary>
		public const int FromSouth = 0, FromWest = 1, FromNorth = 2, FromEast = 3;

		/// <summary>No cut (dry, or a facing liquid never reaches).</summary>
		public const float NoCut = -1f;

		public static float Clamp01(float v) => v <= 0f ? 0f : (v >= 1f ? 1f : v);

		/// <summary>A share as a step 0..Steps: 0 only when nothing is covered, Steps only when all is.</summary>
		public static int Step(float share)
		{
			if (share <= 0f) return 0;
			if (share >= 1f) return Steps;
			int s = (int)(share * Steps + 0.5f);
			return s < 1 ? 1 : (s > Steps - 1 ? Steps - 1 : s);
		}

		/// <summary>Quarter notches the drawn level is kept to: the map mesh re-prints only when the level moves a quarter
		/// notch (12.5 cm, RM_LevelSolve.LookStickyMargin), so a level swinging by a few decilitres never re-meshes.</summary>
		public const int LevelSteps = 4;

		/// <summary>A true level in notches (whole notch + part-notch) as the quarter-notch note a fitting is printed at:
		/// 0 only when dry, at least 1 when any liquid stands, at most 255.</summary>
		public static int LevelNote(double level)
		{
			if (level <= 0.0) return 0;
			int n = (int)(level * LevelSteps + 0.5);
			return n < 1 ? 1 : (n > 255 ? 255 : n);
		}

		/// <summary>The level (notches) a note draws.</summary>
		public static float NoteLevel(int note) => note <= 0 ? 0f : (float)note / LevelSteps;

		/// <summary>A face table (RM_WallFaceMath.NorthByDrop / SideByDrop) read at a fractional exposed drop: the whole-notch
		/// entries exactly, a straight line between them, the last entry past the end.</summary>
		public static float FaceAt(float[] table, float exposed)
		{
			if (exposed <= 0f) return 0f;
			int last = table.Length - 1;
			if (exposed >= last) return table[last];
			int lo = (int)exposed;
			float t = exposed - lo;
			return table[lo] + (table[lo + 1] - table[lo]) * t;
		}

		/// <summary>The cell-local waterline of a ladder hung on rotation <paramref name="rot"/> (0 N, 1 E, 2 S, 3 W) over a
		/// wall of <paramref name="drop"/> notches with <paramref name="level"/> notches of liquid standing (the TRUE level,
		/// part-notch included): z for N, x for E/W; NoCut when dry or hung south. At a whole-notch level this is exactly the
		/// wall face's own waterline (RM_WallFaceMath.ExposedDrop / NorthFaceHeight / SideFaceWidth).</summary>
		public static float LadderWaterline(int rot, int drop, float level)
		{
			if (level <= 0f || rot == 2) return NoCut;
			float exposed = drop - level;
			if (rot == 0) return 1f - FaceAt(RM_WallFaceMath.NorthByDrop, exposed);
			float w = FaceAt(RM_WallFaceMath.SideByDrop, exposed);
			return rot == 1 ? 1f - w : w;
		}

		/// <summary>The level a HUNG ladder is cut at: the whole-notch fill its wall face is drawn with
		/// (SectionLayer_RMExcavationWalls reads RM_MapComponent_Excavation.FillAt), never the true level. Owner's look
		/// 2026-11-12 (EWA_SUBMERGE_REVIEW_20261112): "2m water depth put the northern ladder behind the pit wall art for some
		/// reason, silly looking." That pit read fill 3 with a true level of 4.0 notches: the face still showed a notch of dry
		/// wall while the ladder, cut at the true level, was gone below the rim. Ramp and stakes hang on no face and keep
		/// the true level.</summary>
		public static float HungLadderLevel(int faceFill) => faceFill <= 0 ? 0f : faceFill;

		/// <summary>The redraw key a map-mesh fitting is noted with (RM_MapComponent_Excavation.submergeDrawn): a hung
		/// ladder's carries <see cref="FaceKind"/> and its face fill; the ramp's the quarter-notch note of the true level.
		/// A key that moved re-meshes the cell.</summary>
		public const int FaceKind = 1 << 16;

		public static int DrawnKey(bool face, int faceFill, double trueLevel)
		{
			return face ? FaceKind | (faceFill < 0 ? 0 : faceFill) : LevelNote(trueLevel);
		}

		/// <summary>The level (notches) a key draws.</summary>
		public static float KeyLevel(int key) => (key & FaceKind) != 0 ? key & 0xFFFF : NoteLevel(key);

		/// <summary>The side a hung ladder's cut starts from (N: its foot is south; E: west; W: east).</summary>
		public static int LadderFrom(int rot) => rot == 1 ? FromWest : (rot == 3 ? FromEast : FromSouth);

		/// <summary>The share of a ladder's in-pit span (wall foot dry to rim) under the waterline: 0 dry, 1 brim-full.
		/// The proof's state read.</summary>
		public static float LadderInPitShare(int rot, int drop, float level)
		{
			float cut = LadderWaterline(rot, drop, level);
			if (cut < 0f) return 0f;
			if (rot == 0)
			{
				float foot = 1f - FaceAt(RM_WallFaceMath.NorthByDrop, drop);
				return foot >= 1f ? 1f : Clamp01((cut - foot) / (1f - foot));
			}
			float w = FaceAt(RM_WallFaceMath.SideByDrop, drop);
			if (w <= 0f) return 1f;
			return rot == 1 ? Clamp01((cut - (1f - w)) / w) : Clamp01((w - cut) / w);
		}

		/// <summary>The share of a sprite spanning [<paramref name="lo"/>, <paramref name="hi"/>] (cell-local, along the cut
		/// axis) covered from the low end (from = South/West) or the high end (North/East) by a waterline at
		/// <paramref name="cut"/>.</summary>
		public static float SpanShare(float lo, float hi, float cut, bool fromLow)
		{
			if (cut < 0f || hi <= lo) return 0f;
			return fromLow ? Clamp01((cut - lo) / (hi - lo)) : Clamp01((hi - cut) / (hi - lo));
		}

		/// <summary>The ramp's covered share from its downhill end: the level (notches) over the notches it climbs.</summary>
		public static float RampShare(float level, int rise)
		{
			if (level <= 0f) return 0f;
			return rise <= 0 ? 1f : Clamp01(level / rise);
		}

		/// <summary>A gate's (RM_Sluice, RM_SecurityGrateDoor) covered share from its foot under <paramref name="level"/>
		/// notches in a channel <paramref name="depth"/> notches deep: the gate stands on the floor and its head clears the
		/// bank by one notch, so level / (depth + 1); a brim-full channel still shows the gate's head. Matrix review
		/// 2026-11-12 (pit_fittings_matrix.py): both gates were drawn whole at every fill, brim included.</summary>
		public static float GateShare(float level, int depth)
		{
			if (level <= 0f || depth <= 0) return 0f;
			return Clamp01(level / (depth + 1));
		}

		/// <summary>A stake's covered share from its foot under <paramref name="level"/> notches of liquid (0.5 m each).</summary>
		public static float StakeShare(float level)
		{
			if (level <= 0f) return 0f;
			return Clamp01(level * RM_Volume.MetresPerLevel / RM_SpikeDrawMath.SubmergeMetres);
		}

		/// <summary>Cuts a quad's four corners in PrintPlane order (0 = -x-z, 1 = -x+z, 2 = +x+z, 3 = +x-z), as
		/// <paramref name="uv"/> (8 floats: u,v per corner, atlas sub-rects and flips included) and the quad's rect
		/// (<paramref name="x0"/>..<paramref name="x1"/>, <paramref name="z0"/>..<paramref name="z1"/>): the
		/// <paramref name="share"/> nearest side <paramref name="from"/> is dropped, its uvs lerped along the kept edge.</summary>
		public static void Cut(int from, float share, float[] uv, ref float x0, ref float z0, ref float x1, ref float z1)
		{
			float s = Clamp01(share);
			if (s <= 0f) return;
			switch (from)
			{
				case FromSouth:
					Lerp(uv, 0, 1, s); Lerp(uv, 3, 2, s); z0 += (z1 - z0) * s; break;
				case FromNorth:
					Lerp(uv, 1, 0, s); Lerp(uv, 2, 3, s); z1 -= (z1 - z0) * s; break;
				case FromWest:
					Lerp(uv, 0, 3, s); Lerp(uv, 1, 2, s); x0 += (x1 - x0) * s; break;
				default:
					Lerp(uv, 3, 0, s); Lerp(uv, 2, 1, s); x1 -= (x1 - x0) * s; break;
			}
		}

		private static void Lerp(float[] uv, int moved, int toward, float s)
		{
			uv[moved * 2] += (uv[toward * 2] - uv[moved * 2]) * s;
			uv[moved * 2 + 1] += (uv[toward * 2 + 1] - uv[moved * 2 + 1]) * s;
		}
	}
}
