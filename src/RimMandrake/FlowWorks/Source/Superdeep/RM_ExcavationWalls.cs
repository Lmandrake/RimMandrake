using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// EXCAVATION_WALL_ART_1 + FLOWWORKS_VISUAL_PRINCIPLES_1 — a map section layer that draws the inner faces of
	/// every dug cut the way vanilla draws its own walls seen from above (ruling 33: "walls with depth, not a flat
	/// tile with a lip shadow"; owner principles 1, 2 and 5, 2026-10-05).
	///
	///   • NORTH face (the one the camera sees): a band hanging from the far rim, height by exposed drop from
	///     <see cref="RM_WallFaceMath.NorthByDrop"/> — D3 a wall's height, D4 taller. Drawn in the ground's OWN
	///     terrain material (<see cref="RM_FaceMaterial"/>: dirt or stone per the ground beside it), lit at the top
	///     like vanilla's camera-facing faces, ambient-occluded at the foot, a dark rim line along the top edge, a
	///     contact shadow at the foot, and earth strata or stone block joints over it.
	///   • EAST / WEST faces: narrow strips of the same ground, west in shadow, east lit.
	///   • Liquid standing in the cut covers the foot of the faces at its TRUE level (RM_UnderLiquid.Exposed); the drowned
	///     part is seen through by the one law (SeeThrough).
	///   • SCORCH (<see cref="RM_PitScorch"/>): a cut that burned dry gets an ash/char floor, soot climbing its
	///     faces and a scorch ring on the ground round its rim, fading by the scorch rule.
	///
	/// Form chosen 2026-10-05: a SectionLayer over the depth grid rather than per-depth terrain variants or a Thing
	/// overlay — faces depend on the NEIGHBOUR's depth and ground, which terrain cannot express.
	/// Mod Settings: excavationWallFacesEnabled (off: dug cells show only their terrain), excavationWallMaterialEnabled
	/// (off: the old flat earth-colour band — the fallback look), pitScorchEnabled.
	/// </summary>
	public class SectionLayer_RMExcavationWalls : SectionLayer
	{
		private static readonly Color32 Rim = new Color32(196, 164, 118, 235);
		private static readonly Color32 Earth = new Color32(122, 92, 62, 240);

		public SectionLayer_RMExcavationWalls(Section section) : base(section)
		{
			// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: the faces follow the TRUE level, which moves between terrain rungs;
			// RM_SubmergeDraw.FillPictured dirties LookFlag on a cell whose drawn level note went stale.
			relevantChangeTypes = (ulong)MapMeshFlagDefOf.Terrain | RM_WaterLookDraw.LookFlag;
			// RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM: the relief is lit by the game's own sun (RM_PitSunDraw
			// raises PitSunFlag when the snapped sun or sky moves), and a lamp or a roof changes what reaches a square.
			relevantChangeTypes |= RM_PitSunDraw.PitSunFlag | (ulong)MapMeshFlagDefOf.GroundGlow | (ulong)MapMeshFlagDefOf.Roofs;
		}

		/// <summary>The sun as it reaches the square being drawn (set by ReliefCell; read by its faces and cast shadow).</summary>
		private RM_PitReliefMath.PitSun sunHere = RM_PitReliefMath.FixedSun;

		public override bool Visible => DebugViewSettings.drawTerrain && RimMandrakeFlowWorksSettings.excavationWallFacesEnabled;

		private static Color32 Dark(int depth)
		{
			float k = 1f - RM_WallFaceMath.FootDarkness(depth);
			return new Color32((byte)(Earth.r * k), (byte)(Earth.g * k), (byte)(Earth.b * k), 245);
		}

		public override void Regenerate()
		{
			ClearSubMeshes(MeshParts.All);
			Map map = Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || !RimMandrakeFlowWorksSettings.excavationWallFacesEnabled)
			{
				FinalizeMesh(MeshParts.All);
				return;
			}
			RM_PitScorch scorch = RimMandrakeFlowWorksSettings.pitScorchEnabled ? map.GetComponent<RM_PitScorch>() : null;
			bool material = RimMandrakeFlowWorksSettings.excavationWallMaterialEnabled;
			float y = AltitudeLayer.TerrainScatter.AltitudeFor() + 0.003f;
			foreach (IntVec3 c in section.CellRect)
			{
				int d = eng.HollowDepthAt(c);
				float sc = scorch != null ? scorch.StrengthAt(c) : 0f;
				if (d == 0)
				{
					if (material && BordersOpenCut(map, eng, c))
					{
						Collar(map, c, y - 0.001f);
					}
					if (scorch != null)
					{
						ScorchHalo(map, scorch, c, y);
					}
					continue;
				}
				// RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER: a lid printing the ground hides its square; the faces draw
				// at render queues after that print, so a concealed square draws no pit art at all
				if (!DrawsPitArt(map, eng, c, d))
				{
					continue;
				}
				// the TRUE level (quarter-notch note, RM_UnderLiquid.LevelNote), noted so a stale one re-meshes the cell
				int note = RM_SubmergeDraw.NoteAt(eng, c);
				eng.submergeDrawn[map.cellIndices.CellToIndex(c)] = note;
				float lvTrue = RM_UnderLiquid.NoteLevel(note);
				// RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE: under a clear liquid every face is the DRY pit's (level 0)
				// and WaterSurface lays one sheet over it; an opaque liquid keeps the faces above its line (its terrain is the surface)
				RM_LiquidSurfaceLook look = note > 0 && material && RimMandrakeFlowWorksSettings.liquidSeeThroughEnabled
					? RM_SubmergeDraw.LookAt(map, eng, c) : null;
				bool sheet = look != null && look.seeThrough > 0f;
				float lv = sheet ? 0f : lvTrue;
				if (note == 0 && material && RM_PitReliefMath.ReprintsFloor(true, false, BesideLiquidTerrain(map, c)))
				{
					FloorReprint(map, c, y - 0.0008f);
				}
				int north = NeighbourLevel(map, eng, c + IntVec3.North, d);
				int west = NeighbourLevel(map, eng, c + IntVec3.West, d);
				int east = NeighbourLevel(map, eng, c + IntVec3.East, d);
				int south = NeighbourLevel(map, eng, c + IntVec3.South, d);
				// RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN: the diagonals, for the corners of a shallower block inside a
				// deeper area (RM_PitReliefMath.ClosesCorner / CornerPiece)
				int nw = NeighbourLevel(map, eng, c + IntVec3.North + IntVec3.West, d);
				int ne = NeighbourLevel(map, eng, c + IntVec3.North + IntVec3.East, d);
				int sw = NeighbourLevel(map, eng, c + IntVec3.South + IntVec3.West, d);
				int se = NeighbourLevel(map, eng, c + IntVec3.South + IntVec3.East, d);
				// RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM: the stepped rule (RM_PitReliefMath.PlanStep): a wall
				// shows only the part between the two floors, so a riser's top meets the side walls part way down
				bool relief = RM_UnderLiquid.Relief && material;
				RM_PitReliefMath.StepPlan sp = RM_PitReliefMath.PlanStep(d, north, south, west, east, nw, ne, lv);
				if (RimMandrakeFlowWorksSettings.pitOutlineEnabled)
				{
					if (relief)
					{
						OutlineStep(c, sp, y + 0.0009f);
					}
					else
					{
						Outline(c, d, north, south, west, east, y + 0.0009f);
					}
					CornerLines(c, d, north, south, west, east, nw, ne, sw, se, y + 0.0009f);
				}
				float nd = RM_UnderLiquid.Exposed(d, north, lv);
				float wd = RM_UnderLiquid.Exposed(d, west, lv);
				float ed = RM_UnderLiquid.Exposed(d, east, lv);
				float h = relief ? sp.T : RM_UnderLiquid.NorthFace(nd);
				RM_PitReliefMath.CornerPiece(d, north, west, nw, lv, out float wnw, out float hnw);
				RM_PitReliefMath.CornerPiece(d, north, east, ne, lv, out float wne, out float hne);
				if (sc > 0f && note == 0)
				{
					// principle 5: the SAME empty pit, burned — grey ash over the floor, char at the walls and in patches
					bool dirt = !RM_FaceMaterial.IsStone(eng.OriginalTerrainAt(c));
					ScorchFloor(c, d, north, south, west, east, 1f - h, sc, y - 0.0005f, dirt);
				}
				if (sheet)
				{
					WaterSurface(map, eng, c, d, lvTrue, look, north, south, west, east, nw, ne, relief, y - 0.0008f);
				}
				if (!material)
				{
					if (nd > 0f)
					{
						QuadV(c.x, c.z + 1f - h, 1f, h, y, Dark(d), Rim);
					}
					if (wd > 0f)
					{
						Color32 shade = Dark(d + 1);
						QuadV(c.x, c.z, RM_UnderLiquid.SideFace(wd), 1f, y + 0.001f, shade, shade);
					}
					if (ed > 0f)
					{
						float w = RM_UnderLiquid.SideFace(ed);
						QuadV(c.x + 1f - w, c.z, w, 1f, y + 0.001f, Earth, Earth);
					}
					continue;
				}
				float ww = RM_UnderLiquid.SideFace(wd);
				float ew = RM_UnderLiquid.SideFace(ed);
				if (relief)
				{
					ReliefCell(map, eng, c, d, sp, note == 0 || sheet, sc, y);
					continue;
				}
				if (nd > 0f)
				{
					NorthFace(map, eng, c, d, h, ww, ew, y, sc, RM_PitReliefMath.FaceFootShade(nd));
				}
				if (wd > 0f)
				{
					SideFace(map, eng, c, c + IntVec3.West, d, ww, h, false, y + 0.001f, sc);
				}
				if (ed > 0f)
				{
					SideFace(map, eng, c, c + IntVec3.East, d, ew, h, true, y + 0.001f, sc);
				}
				if (wnw > 0f)
				{
					CornerFace(map, eng, c, c + IntVec3.North + IntVec3.West, false, wnw, hnw, y + 0.001f);
				}
				if (wne > 0f)
				{
					CornerFace(map, eng, c, c + IntVec3.North + IntVec3.East, true, wne, hne, y + 0.001f);
				}
				if (note == 0 || sheet)
				{
					// every floor shaded by its own depth, the dry pit's under a clear liquid's sheet too
					FloorShade(c, d, ww, ew, h, wnw, hnw, wne, hne, y + 0.0012f);
				}
			}
			FinalizeMesh(MeshParts.All);
		}

		/// <summary>RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN: a square's height (or the deck on it) changed; it and its 8
		/// neighbours re-mesh at once (their faces read its height; whether a lid conceals reads its neighbours). The layer re-meshed
		/// only on a floor TERRAIN change, and every floor past 2 m is one terrain, so a pit cut deeper past 2 m kept its old
		/// faces until something else re-meshed the section.</summary>
		public static void RedrawStep(Map map, IntVec3 c)
		{
			if (map?.mapDrawer == null || !c.InBounds(map))
			{
				return;
			}
			ulong flag = RM_WaterLookDraw.LookFlag;
			// the 4-argument form: the 2-argument MapMeshDirty dirties the 8 neighbours' sections only for FogOfWar, Buildings or
			// Roofs (Verse.MapDrawer, 1.6, read in RimSage 2026-11-21), so a neighbour across a section edge kept its old faces.
			// RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM: a square's cast shadow reads the plans of the squares
			// toward the sun, up to 2 away under a low sun, which read their own neighbours: the 7x7 re-meshes (each of the 5x5 with
			// its adjacent cells).
			for (int dz = -2; dz <= 2; dz++)
			{
				for (int dx = -2; dx <= 2; dx++)
				{
					IntVec3 q = c + new IntVec3(dx, 0, dz);
					if (q.InBounds(map))
					{
						map.mapDrawer.MapMeshDirty(q, flag != 0 ? flag : (ulong)MapMeshFlagDefOf.Terrain, regenAdjacentCells: true, regenAdjacentSections: false);
					}
				}
			}
		}

		/// <summary>Does this dug square draw pit art? Not under a cover that prints the ground (RM_PitReliefMath.DrawsPitArt).</summary>
		internal static bool DrawsPitArt(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int hollow)
		{
			if (hollow <= 0)
			{
				return false;
			}
			bool covered = Pits.RM_PitCoverUtility.CoverAt(map, c) != null;
			return RM_PitReliefMath.DrawsPitArt(hollow, covered, covered && Pits.RM_PitCoverUtility.LidShowsArt(map, c));
		}

		private readonly float[] floorRects = new float[8];
		private readonly float[] cornerXz = new float[8];
		private static readonly Color32 ShadeBlack = new Color32(10, 8, 7, 0);

		/// <summary>The floor depth shade's colour (RM_PitReliefMath.FloorTint: pure black, so the floor draws at FloorBrightness).</summary>
		private static readonly Color32 FloorTintColour = new Color32(RM_PitReliefMath.FloorTint, RM_PitReliefMath.FloorTint, RM_PitReliefMath.FloorTint, 0);

		/// <summary>The floor's depth shade: black at RM_PitReliefMath.FloorShade(d) over the floor between the faces
		/// (RM_PitReliefMath.FloorRects, never over a face), so every depth draws apart, past 2 m too.</summary>
		private void FloorShade(IntVec3 c, int d, float ww, float ew, float h, float wnw, float hnw, float wne, float hne, float y)
		{
			FloorShade(c, RM_PitReliefMath.FloorShade(d), ww, ew, h, wnw, hnw, wne, hne, y);
		}

		private void FloorShade(IntVec3 c, float a, float ww, float ew, float h, float wnw, float hnw, float wne, float hne, float y)
		{
			if (!(a > 0f))
			{
				return;
			}
			Color32 k = FloorTintColour;
			k.a = Alpha(a);
			int n = RM_PitReliefMath.FloorRects(ww, ew, h, wnw, hnw, wne, hne, floorRects);
			for (int i = 0; i < n; i++)
			{
				float x0 = floorRects[4 * i], z0 = floorRects[4 * i + 1], x1 = floorRects[4 * i + 2], z1 = floorRects[4 * i + 3];
				QuadVMat(RM_FaceMaterial.TintMat, c.x + x0, c.z + z0, x1 - x0, z1 - z0, y, k, k);
			}
		}

		// ── the stepped rule's draw (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM; RM_PitReliefMath.PlanStep) ──
		// Every face is the bank's own ground, darkened to StepK of its TOP's depth and lit by its facing (a black tint, a white
		// lift only where the sun brightens it past the ground), fading by FaceFade toward its foot; floors darken by StepK; the
		// upper floor at a lip gets a pale band; a fixed north-west sun casts each face's shadow onto the floor past its foot.

		private readonly int[] win = new int[49];

		private void ReliefCell(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, RM_PitReliefMath.StepPlan sp, bool dry, float sc, float y)
		{
			sunHere = RM_PitSunDraw.SunAt(map, eng, c);
			if (sp.T > 0f)
			{
				NorthFaceStep(map, eng, c, sp, y, sc);
			}
			if (sp.L > 0f)
			{
				SideFaceStep(map, eng, c, sp, false, y + 0.001f, sc);
			}
			if (sp.R > 0f)
			{
				SideFaceStep(map, eng, c, sp, true, y + 0.001f, sc);
			}
			if (sp.CnwW > 0f)
			{
				CornerFaceStep(map, eng, c, c + IntVec3.North + IntVec3.West, false, sp.CnwW, sp.CnwH, sp.Znw, y + 0.001f);
			}
			if (sp.CneW > 0f)
			{
				CornerFaceStep(map, eng, c, c + IntVec3.North + IntVec3.East, true, sp.CneW, sp.CneH, sp.Zne, y + 0.001f);
			}
			if (!dry)
			{
				return;
			}
			LipBands(c, d, sp, y + 0.0005f);
			FloorShade(c, RM_PitReliefMath.StepFloorShade(d), sp.L, sp.R, sp.T, sp.CnwW, sp.CnwH, sp.CneW, sp.CneH, y + 0.0012f);
			CastShadow(map, eng, c, d, sp, y + 0.0013f);
		}

		/// <summary>A point of the square in its plan's coordinates (x east, y DOWN from the north edge) on the map.</summary>
		private static Vector3 At(IntVec3 c, float x, float yDown, float y) => new Vector3(c.x + x, y, c.z + 1f - yDown);

		private void NorthFaceStep(Map map, RM_MapComponent_Excavation eng, IntVec3 c, RM_PitReliefMath.StepPlan sp, float y, float scorch)
		{
			float t = sp.T, foot = c.z + 1f - t;
			// the face's ends: straight down by hv beside a side wall that runs on above it, then the mitre to the floor strip
			Vector3[] q =
			{
				At(c, sp.Lt, 0f, y), At(c, 1f - sp.Rt, 0f, y), At(c, 1f - sp.Rt, sp.HvR, y), At(c, 1f - sp.R, t, y),
				At(c, sp.L, t, y), At(c, sp.Lt, sp.HvL, y),
			};
			float[] frac = { 0f, 0f, sp.HvR / t, 1f, 1f, sp.HvL / t };
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, c + IntVec3.North, out bool stone);
			Fan(RM_FaceMaterial.FaceMat(ground), q, null, true, foot);
			FaceShadeStep(q, frac, RM_PitReliefMath.StepK(sp.Zn), RM_PitReliefMath.FaceLight(0, sunHere), foot);
			Fan(stone ? RM_FaceMaterial.JointMat : RM_FaceMaterial.StrataMat, Lift(q, 0.0004f), null, true, foot);
			if (scorch > 0f)
			{
				SootFace(c, c.x + sp.L, c.x + 1f - sp.R, foot, c.z + 1f, scorch, y + 0.0007f);
			}
		}

		private void SideFaceStep(Map map, RM_MapComponent_Excavation eng, IntVec3 c, RM_PitReliefMath.StepPlan sp, bool east, float y, float scorch)
		{
			float full = east ? sp.R : sp.L, top = east ? sp.Rt : sp.Lt, hv = east ? sp.HvR : sp.HvL, t = sp.T;
			Vector3[] q;
			float[] off;
			if (t <= 0f)
			{
				off = new[] { 0f, 0f, full, full };
				q = new[] { At(c, 0f, 1f, y), At(c, 0f, 0f, y), At(c, full, 0f, y), At(c, full, 1f, y) };
			}
			else
			{
				// x in from the wall's edge: the upper part beside the north face (top wide, straight down by hv), the mitre, the strip
				off = new[] { 0f, 0f, top, top, full, full };
				q = new[] { At(c, 0f, 1f, y), At(c, 0f, 0f, y), At(c, top, 0f, y), At(c, top, hv, y), At(c, full, t, y), At(c, full, 1f, y) };
			}
			float[] frac = new float[q.Length];
			for (int i = 0; i < q.Length; i++)
			{
				frac[i] = full > 0f ? off[i] / full : 0f;
				if (east)
				{
					q[i].x = c.x + 1f - (q[i].x - c.x);
				}
			}
			if (east)
			{
				System.Array.Reverse(q);
				System.Array.Reverse(frac);
			}
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, east ? c + IntVec3.East : c + IntVec3.West, out bool _);
			Fan(RM_FaceMaterial.FaceMat(ground), q, null, false, c.z);
			FaceShadeStep(q, frac, RM_PitReliefMath.StepK(east ? sp.Ze : sp.Zw), RM_PitReliefMath.FaceLight(east ? 2 : 1, sunHere), c.z);
			if (scorch > 0f)
			{
				byte st = (byte)(255f * RM_WallFaceMath.FaceSoot(scorch, 0.3f, 0.5f));
				Fan(RM_FaceMaterial.SootMat, Lift(q, 0.0007f), Uniform(q.Length, new Color32(255, 255, 255, st)), false, c.z);
			}
		}

		private void CornerFaceStep(Map map, RM_MapComponent_Excavation eng, IntVec3 c, IntVec3 diag, bool east, float w, float h, int zTop, float y)
		{
			RM_PitReliefMath.CornerPoly(east, w, h, cornerXz);
			Vector3[] q = new Vector3[4];
			float[] frac = new float[4];
			for (int i = 0; i < 4; i++)
			{
				float x = cornerXz[2 * i];
				q[i] = new Vector3(c.x + x, y, c.z + cornerXz[2 * i + 1]);
				frac[i] = east ? (1f - x) / w : x / w;
			}
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, diag, out bool _);
			Fan(RM_FaceMaterial.FaceMat(ground), q, null, false, c.z);
			FaceShadeStep(q, frac, RM_PitReliefMath.StepK(zTop), RM_PitReliefMath.FaceLight(east ? 2 : 1, sunHere), c.z);
		}

		/// <summary>A face's tone: StepK of its top x its light x (1 - FaceFade x frac), frac 0 at the top line, 1 at the foot. Under 1
		/// a black tint; over 1 (a sunlit face beside the ground) a white lift.</summary>
		private void FaceShadeStep(Vector3[] q, float[] frac, float kTop, float light, float zFoot)
		{
			Color32[] dark = new Color32[q.Length], lift = new Color32[q.Length];
			bool anyDark = false, anyLift = false;
			for (int i = 0; i < q.Length; i++)
			{
				float m = kTop * light * (1f - RM_PitReliefMath.FaceFade * RM_UnderLiquid.Clamp01(frac[i]));
				dark[i] = ShadeBlack;
				dark[i].a = Alpha(m < 1f ? 1f - m : 0f);
				lift[i] = new Color32(255, 248, 232, Alpha(m > 1f ? LightAlpha(m) : 0f));
				anyDark |= dark[i].a > 0;
				anyLift |= lift[i].a > 0;
			}
			if (anyDark)
			{
				Fan(RM_FaceMaterial.TintMat, Lift(q, 0.0002f), dark, false, zFoot);
			}
			if (anyLift)
			{
				Fan(RM_FaceMaterial.ShadeMat, Lift(q, 0.0003f), lift, false, zFoot);
			}
		}

		/// <summary>The outline under the stepped rule: the near lining as today; the north lip line only between the side walls
		/// (from Lt to 1 - Rt, where the riser's top meets them); a side lip line from its hv down.</summary>
		private void OutlineStep(IntVec3 c, RM_PitReliefMath.StepPlan sp, float y)
		{
			Material m = RM_FaceMaterial.OutlineMat;
			Color32 k = new Color32(0, 0, 0, 255);
			if (sp.Sl > 0f)
			{
				QuadVMat(m, c.x, c.z, 1f, sp.Sl, y, k, k);
			}
			float r = RM_WallFaceMath.RimLine, sl = RM_WallFaceMath.SideLine;
			if (sp.LipN && sp.LipN1 > sp.LipN0)
			{
				QuadVMat(m, c.x + sp.LipN0, c.z + 1f - r, sp.LipN1 - sp.LipN0, r, y, k, k);
			}
			if (sp.LipW && sp.LipW0 < 1f)
			{
				QuadHMat(m, c.x, c.z, sl, 1f - sp.LipW0, y, k, k);
			}
			if (sp.LipE && sp.LipE0 < 1f)
			{
				QuadHMat(m, c.x + 1f - sl, c.z, sl, 1f - sp.LipE0, y, k, k);
			}
		}

		/// <summary>The pale band of this floor along an edge where its neighbour is deeper (his "differently colored edge").</summary>
		private void LipBands(IntVec3 c, int d, RM_PitReliefMath.StepPlan sp, float y)
		{
			float b = RM_PitReliefMath.LipBand;
			Color32 w = new Color32(255, 248, 232, Alpha(RM_PitReliefMath.StepLipAlpha(d)));
			Material m = RM_FaceMaterial.ShadeMat;
			if (sp.EdgeS)
			{
				QuadVMat(m, c.x + sp.L, c.z, 1f - sp.L - sp.R, b, y, w, w);
			}
			if (sp.EdgeN)
			{
				float x0 = Mathf.Max(sp.L, sp.CnwW), x1 = 1f - Mathf.Max(sp.R, sp.CneW);
				QuadVMat(m, c.x + x0, c.z + 1f - b, x1 - x0, b, y, w, w);
			}
			if (sp.EdgeW)
			{
				QuadVMat(m, c.x, c.z, b, 1f - Mathf.Max(sp.T, sp.CnwH), y, w, w);
			}
			if (sp.EdgeE)
			{
				QuadVMat(m, c.x + 1f - b, c.z, b, 1f - Mathf.Max(sp.T, sp.CneH), y, w, w);
			}
		}

		/// <summary>The cast shadow over the dry floor: a vertex grid (8 a cell) whose black alpha is ShadowDarkFor(sun) x (1 - Lit), read
		/// from the 5x5 depths round the square (RM_PitReliefMath.Lit) under the game's sun as it reaches the square. Skipped when the sun
		/// gives no shadow there or nothing in reach is shallower.</summary>
		private void CastShadow(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, RM_PitReliefMath.StepPlan sp, float y)
		{
			// 7x7: a low sun's shadow reaches 2 squares (slope 2), and the plan of a square it reaches reads that square's neighbours
			for (int r = -3; r <= 3; r++)
			{
				for (int k = -3; k <= 3; k++)
				{
					win[(r + 3) * 7 + (k + 3)] = r == 0 && k == 0 ? d : NeighbourLevel(map, eng, c + new IntVec3(k, 0, -r), d);
				}
			}
			if (!RM_PitReliefMath.MayBeShaded(win, sunHere))
			{
				return;
			}
			float dark = RM_PitReliefMath.ShadowDarkFor(sunHere);
			int n = RM_PitReliefMath.FloorRects(sp.L, sp.R, sp.T, sp.CnwW, sp.CnwH, sp.CneW, sp.CneH, floorRects);
			for (int i = 0; i < n; i++)
			{
				float x0 = floorRects[4 * i], z0 = floorRects[4 * i + 1], x1 = floorRects[4 * i + 2], z1 = floorRects[4 * i + 3];
				int nx = Mathf.Max(1, Mathf.CeilToInt((x1 - x0) * 8f)), nz = Mathf.Max(1, Mathf.CeilToInt((z1 - z0) * 8f));
				Color32[,] col = new Color32[nx + 1, nz + 1];
				bool any = false;
				for (int a = 0; a <= nx; a++)
				{
					for (int b = 0; b <= nz; b++)
					{
						float fx = x0 + (x1 - x0) * a / nx, fz = z0 + (z1 - z0) * b / nz;
						Color32 k = ShadeBlack;
						k.a = Alpha(dark * (1f - RM_PitReliefMath.Lit(win, fx, 1f - fz, sunHere)));
						any |= k.a > 0;
						col[a, b] = k;
					}
				}
				if (any)
				{
					Grid(RM_FaceMaterial.TintMat, c.x + x0, c.z + z0, x1 - x0, z1 - z0, nx, col, y, nz);
				}
			}
		}

		private static Color32[] Uniform(int n, Color32 c)
		{
			Color32[] r = new Color32[n];
			for (int i = 0; i < n; i++)
			{
				r[i] = c;
			}
			return r;
		}

		/// <summary>A convex (or star-shaped from v[0]) polygon as a fan from v[0]; colours per vertex (null: white); faceUv: u
		/// along x, v from <paramref name="zFoot"/> (as Poly), else world uv.</summary>
		private void Fan(Material mat, Vector3[] v, Color32[] col, bool faceUv, float zFoot)
		{
			if (mat == null || v.Length < 3)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int b = sm.verts.Count;
			for (int i = 0; i < v.Length; i++)
			{
				sm.verts.Add(v[i]);
				sm.uvs.Add(faceUv ? new Vector3(v[i].x, (v[i].z - zFoot) * 2f, 0f) : new Vector3(v[i].x, v[i].z, 0f));
				sm.colors.Add(col != null ? col[i] : White);
			}
			for (int i = 1; i + 1 < v.Length; i++)
			{
				sm.tris.Add(b);
				sm.tris.Add(b + i);
				sm.tris.Add(b + i + 1);
			}
		}

		/// <summary>The side face of a shallower block continued down beside it into a north corner of this square (the convex
		/// corner the camera sees), in the block's ground, lit as a side bevel, its foot mitred (RM_PitReliefMath.CornerPoly).</summary>
		private void CornerFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, IntVec3 diag, bool east, float w, float h, float y)
		{
			RM_PitReliefMath.CornerPoly(east, w, h, cornerXz);
			Vector3[] q = new Vector3[4];
			for (int i = 0; i < 4; i++)
			{
				q[i] = new Vector3(c.x + cornerXz[2 * i], y, c.z + cornerXz[2 * i + 1]);
			}
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, diag, out bool _);
			Material face = RM_FaceMaterial.FaceMat(ground);
			if (face != null)
			{
				Poly(face, q, White, White, false, h);
			}
			byte a = (byte)(255f * LightAlpha(RM_WallFaceMath.WallSideLight));
			Poly(RM_FaceMaterial.ShadeMat, Lift(q, 0.0002f), new Color32(255, 248, 232, a), new Color32(255, 248, 232, a), false, h);
		}

		/// <summary>The outline's corner quadrants: where a diagonal neighbour is shallower and neither square beside it is, no line
		/// of this square's reaches that corner, so the block's outline would break there (RM_PitReliefMath.ClosesCorner).</summary>
		private void CornerLines(IntVec3 c, int d, int north, int south, int west, int east, int nw, int ne, int sw, int se, float y)
		{
			Material m = RM_FaceMaterial.OutlineMat;
			Color32 k = new Color32(0, 0, 0, 255);
			float sl = RM_WallFaceMath.SideLine, r = RM_WallFaceMath.RimLine;
			if (RM_PitReliefMath.ClosesCorner(d, north, west, nw))
			{
				QuadVMat(m, c.x, c.z + 1f - r, sl, r, y, k, k);
			}
			if (RM_PitReliefMath.ClosesCorner(d, north, east, ne))
			{
				QuadVMat(m, c.x + 1f - sl, c.z + 1f - r, sl, r, y, k, k);
			}
			if (RM_PitReliefMath.ClosesCorner(d, south, west, sw))
			{
				QuadVMat(m, c.x, c.z, sl, RM_WallFaceMath.SouthLining(d - sw), y, k, k);
			}
			if (RM_PitReliefMath.ClosesCorner(d, south, east, se))
			{
				QuadVMat(m, c.x + 1f - sl, c.z, sl, RM_WallFaceMath.SouthLining(d - se), y, k, k);
			}
		}

		/// <summary>The far (north) bank's face, drawn as vanilla draws a wall's south bevel (MEASURED from the owner's
		/// steel-wall shot): a flat band the ground's own material, lit x1.85 against the ground, hanging directly from
		/// the rim, with 45-degree mitred lower corners where a side bevel meets it.</summary>
		private void NorthFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, float h, float ww, float ew, float y, float scorch,
			float foot)
		{
			float top = c.z + 1f;
			float bot = top - h;
			float xl = c.x, xr = c.x + 1f;
			float il = RM_WallFaceMath.MitreInset(ww, h), ir = RM_WallFaceMath.MitreInset(ew, h);
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, c + IntVec3.North, out bool stone);
			Material face = RM_FaceMaterial.FaceMat(ground);
			// trapezoid: bottom-left, top-left, top-right, bottom-right
			Vector3[] q = { new Vector3(xl + il, y, bot), new Vector3(xl, y, top), new Vector3(xr, y, top), new Vector3(xr - ir, y, bot) };
			if (face != null)
			{
				Poly(face, q, White, White, false, h);
			}
			// lit like the wall bevel; only a touch darker at the foot the deeper the cut (depth still reads)
			byte aTop = (byte)(255f * LightAlpha(RM_WallFaceMath.WallFaceLight));
			byte aFoot = (byte)(Mathf.Max(0f, aTop - 12f * d));
			Poly(RM_FaceMaterial.ShadeMat, Lift(q, 0.0002f), new Color32(255, 248, 232, aFoot), new Color32(255, 248, 232, aTop), false, h);
			Poly(stone ? RM_FaceMaterial.JointMat : RM_FaceMaterial.StrataMat, Lift(q, 0.0004f), White, White, true, h);
			// RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN: past the tallest face (2.5 m) a dark foot keeps telling drops apart
			if (foot > 0f)
			{
				Color32 kf = ShadeBlack, kt = ShadeBlack;
				kf.a = Alpha(foot);
				Poly(RM_FaceMaterial.TintMat, Lift(q, 0.0006f), kf, kt, false, h);
			}
			if (scorch > 0f)
			{
				SootFace(c, xl + il, xr - ir, bot, top, scorch, y + 0.0007f);
			}
		}

		/// <summary>A side bank as vanilla's side bevel: a strip lit x1.29, its top end mitred where the north face meets
		/// it, running down to the near edge.</summary>
		private void SideFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, IntVec3 n, int d, float w, float northH, bool east, float y, float scorch)
		{
			float top = c.z + 1f;
			float x0 = east ? c.x + 1f - w : c.x;
			float x1 = x0 + w;
			// mitre: the edge touching the bank is full height; the inner edge stops where the north face's foot is
			float innerTop = northH > 0f ? top - northH : top;
			Vector3[] q = east
				? new[] { new Vector3(x0, y, c.z), new Vector3(x0, y, innerTop), new Vector3(x1, y, top), new Vector3(x1, y, c.z) }
				: new[] { new Vector3(x0, y, c.z), new Vector3(x0, y, top), new Vector3(x1, y, innerTop), new Vector3(x1, y, c.z) };
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, n, out bool _);
			Material face = RM_FaceMaterial.FaceMat(ground);
			if (face != null)
			{
				Poly(face, q, White, White, false, 1f);
			}
			byte a = (byte)(255f * LightAlpha(RM_WallFaceMath.WallSideLight));
			Poly(RM_FaceMaterial.ShadeMat, Lift(q, 0.0002f), new Color32(255, 248, 232, a), new Color32(255, 248, 232, a), false, 1f);
			if (scorch > 0f)
			{
				byte sf = (byte)(255f * RM_WallFaceMath.FaceSoot(scorch, 0f, 0.5f));
				byte st = (byte)(255f * RM_WallFaceMath.FaceSoot(scorch, 0.6f, 0.5f));
				Poly(RM_FaceMaterial.SootMat, Lift(q, 0.0007f), new Color32(255, 255, 255, sf), new Color32(255, 255, 255, st), false, 1f);
			}
		}

		/// <summary>White-blend alpha that brightens a mid-dark ground by <paramref name="mult"/> (alpha blend toward
		/// white: g' = g(1-a) + a; solved at a typical ground value of 0.30).</summary>
		private static float LightAlpha(float mult)
		{
			const float g = 0.30f;
			return Mathf.Clamp01((g * mult - g) / (1f - g));
		}

		private static Vector3[] Lift(Vector3[] q, float dy)
		{
			Vector3[] r = new Vector3[q.Length];
			for (int i = 0; i < q.Length; i++)
			{
				r[i] = new Vector3(q[i].x, q[i].y + dy, q[i].z);
			}
			return r;
		}

		/// <summary>The pit's footprint as a closed BLACK outline — vanilla outlines every wall edge — drawn whether or
		/// not liquid stands in it (it marks the edge, not the face). The near (south) edge is heavier and grows with
		/// the drop: the owner's "black-lining on the southern edge".</summary>
		private void Outline(IntVec3 c, int d, int north, int south, int west, int east, float y)
		{
			Material m = RM_FaceMaterial.OutlineMat;
			Color32 k = new Color32(0, 0, 0, 255);
			int sd = d - south;
			if (sd > 0)
			{
				QuadVMat(m, c.x, c.z, 1f, RM_WallFaceMath.SouthLining(sd), y, k, k);
			}
			if (d - north > 0)
			{
				float r = RM_WallFaceMath.RimLine;
				QuadVMat(m, c.x, c.z + 1f - r, 1f, r, y, k, k);
			}
			float sl = RM_WallFaceMath.SideLine;
			if (d - west > 0)
			{
				QuadHMat(m, c.x, c.z, sl, 1f, y, k, k);
			}
			if (d - east > 0)
			{
				QuadHMat(m, c.x + 1f - sl, c.z, sl, 1f, y, k, k);
			}
		}

		/// <summary>True when an undug cell touches (8-way) a dug cell that draws as a hole (not one under a concealing lid).</summary>
		private static bool BordersOpenCut(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (n.InBounds(map) && DrawsPitArt(map, eng, n, eng.HollowDepthAt(n)))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The bank's own ground redrawn over a cell bordering a cut, so the cut's terrain (gravel, water)
		/// no longer smears soft-edged over the bank: the edge stays crisp under the black outline, and the near-lip
		/// occluder (same material) matches it with no seam.</summary>
		private void Collar(Map map, IntVec3 c, float y)
		{
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null || t.IsWater)
			{
				return;
			}
			Material m = RM_FaceMaterial.FaceMat(t);
			if (m != null)
			{
				Quad(m, c.x, c.z, 1f, 1f, y, White, White, UvWorld);
			}
		}

		// ── scorch (principle 5), round 3: textured ash and soot from GPT concept art (Transient/scorch_concept_2026-10-06)
		//    — owner, 2026-10-06, of the starburst round: "those look ridiculous". Coverage per vertex, grain from the
		//    textures, edges broken by the terrain-fade shader's rough alpha: no stamps, no repeating shapes. ──

		private const float ScorchUv = 1f / 3f;   // one texture repeat per three cells
		private static readonly Color32 Tint = new Color32(150, 72, 30, 0);

		private static float Blotch(float x, float z)
		{
			// two octaves of world-space Perlin: patches a couple of cells across, never a repeat inside a pit
			return Mathf.Clamp01(0.65f * Mathf.PerlinNoise(x * 0.55f + 31.7f, z * 0.55f + 11.3f)
				+ 0.35f * Mathf.PerlinNoise(x * 1.7f + 5.1f, z * 1.7f + 77.9f));
		}

		/// <summary>Low-frequency, domain-warped noise for the halo's reach: big lumpy lobes, different on each side.</summary>
		private static float Lobes(float x, float z)
		{
			float wx = x + 1.6f * (Mathf.PerlinNoise(x * 0.31f + 3.3f, z * 0.31f + 9.1f) - 0.5f);
			float wz = z + 1.6f * (Mathf.PerlinNoise(x * 0.31f + 41.2f, z * 0.31f + 2.7f) - 0.5f);
			return Mathf.Clamp01(0.7f * Mathf.PerlinNoise(wx * 0.62f + 17.1f, wz * 0.62f + 5.9f)
				+ 0.3f * Mathf.PerlinNoise(wx * 2.1f + 8.8f, wz * 2.1f + 61.3f));
		}

		/// <summary>The burned floor: the ash texture over (nearly) all of it, the soot texture at the walls and in soft
		/// patches, and a faint rust heat tint in a band just off the walls. 6x6 vertex grid per cell.</summary>
		private void ScorchFloor(IntVec3 c, int d, int north, int south, int west, int east, float hTop, float s, float y, bool dirt)
		{
			const int N = 6;
			bool wn = north < d, ws = south < d, ww = west < d, we = east < d;
			Color32[,] ash = new Color32[N + 1, N + 1];
			Color32[,] soot = new Color32[N + 1, N + 1];
			Color32[,] tint = new Color32[N + 1, N + 1];
			for (int i = 0; i <= N; i++)
			{
				for (int j = 0; j <= N; j++)
				{
					float lx = i / (float)N, lz = j / (float)N * hTop;
					float x = c.x + lx, z = c.z + lz;
					float dist = 9f;
					if (wn) dist = Mathf.Min(dist, hTop - lz);
					if (ws) dist = Mathf.Min(dist, lz);
					if (ww) dist = Mathf.Min(dist, lx);
					if (we) dist = Mathf.Min(dist, 1f - lx);
					float n = Blotch(x, z);
					ash[i, j] = new Color32(255, 255, 255, (byte)(255f * RM_WallFaceMath.AshCover(s, n, dirt)));
					soot[i, j] = new Color32(255, 255, 255, (byte)(255f * RM_WallFaceMath.CharCover(s, Blotch(x + 13.7f, z + 4.1f), dist, dirt)));
					Color32 t = Tint;
					t.a = (byte)(255f * RM_WallFaceMath.HeatTint(s, Blotch(x + 7.3f, z + 21.9f), dist, dirt));
					tint[i, j] = t;
				}
			}
			Grid(dirt ? RM_FaceMaterial.DirtAshMat : RM_FaceMaterial.AshMat, c.x, c.z, 1f, hTop, N, ash, y, -1, ScorchUv);
			Grid(RM_FaceMaterial.SootMat, c.x, c.z, 1f, hTop, N, soot, y + 0.0001f, -1, ScorchUv);
			Grid(RM_FaceMaterial.TintMat, c.x, c.z, 1f, hTop, N, tint, y + 0.0002f);
			// the ash is lighter than the bare floor it covers, so the depth must be put back: a flat shade by depth
			Color32 deep = new Color32(10, 8, 7, (byte)(255f * RM_WallFaceMath.AshDepthShade(d) * Mathf.Min(1f, s * 2f)));
			QuadVMat(RM_FaceMaterial.TintMat, c.x, c.z, 1f, hTop, y + 0.0003f, deep, deep);
			// debris (round 4): char lumps and ash flakes, seeded per cell — stable across save/load, no grid
			int pieces = RM_WallFaceMath.DebrisCount(s, c.x, c.z);
			for (int k = 0; k < pieces; k++)
			{
				RM_WallFaceMath.DebrisPiece(c.x, c.z, k, hTop, RM_FaceMaterial.DebrisVariants, out float lx, out float lz,
					out float size, out float rot, out bool isChar, out int v);
				Material m = RM_FaceMaterial.DebrisMat(isChar, v);
				if (m != null)
				{
					Sprite(m, c.x + lx, c.z + lz, size, rot, y + 0.0004f);
				}
			}
		}

		/// <summary>A square sprite centred on (cx,cz), <paramref name="size"/> cells across, rotated by
		/// <paramref name="rotDeg"/>.</summary>
		private void Sprite(Material mat, float cx, float cz, float size, float rotDeg, float y)
		{
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			float a = rotDeg * Mathf.Deg2Rad, h = size * 0.5f;
			float ca = Mathf.Cos(a) * h, sa = Mathf.Sin(a) * h;
			// corners: bottom-left, top-left, top-right, bottom-right (same winding as Quad)
			sm.verts.Add(new Vector3(cx - ca + sa, y, cz - sa - ca));
			sm.verts.Add(new Vector3(cx - ca - sa, y, cz - sa + ca));
			sm.verts.Add(new Vector3(cx + ca - sa, y, cz + sa + ca));
			sm.verts.Add(new Vector3(cx + ca + sa, y, cz + sa - ca));
			sm.uvs.Add(new Vector3(0f, 0f, 0f));
			sm.uvs.Add(new Vector3(0f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 0f, 0f));
			for (int i = 0; i < 4; i++)
			{
				sm.colors.Add(White);
			}
			Tris(sm, n);
		}

		/// <summary>Soot on a north face: the soot texture, heaviest at the foot, a band under the rim, and vertical
		/// plumes (noise stretched up the face) so it reads as smoke-stained, not painted.</summary>
		private void SootFace(IntVec3 c, float xl, float xr, float bot, float top, float s, float y)
		{
			const int NX = 8, R = 5;
			float h = top - bot;
			Color32[,] g = new Color32[NX + 1, R + 1];
			for (int i = 0; i <= NX; i++)
			{
				float x = xl + (xr - xl) * i / NX;
				for (int j = 0; j <= R; j++)
				{
					float v = j / (float)R;
					float p = Mathf.PerlinNoise(x * 4.3f + 12.9f, v * 0.8f + c.z * 0.37f);
					g[i, j] = new Color32(255, 255, 255, (byte)(255f * RM_WallFaceMath.FaceSoot(s, v, p)));
				}
			}
			Grid(RM_FaceMaterial.SootMat, xl, bot, xr - xl, h, NX, g, y, R, ScorchUv);
			// drip streaks (round 4, as concept_dirt_v3): narrow dark runs hanging from the rim, tapering as they go down
			int drips = RM_WallFaceMath.DripCount(c.x, c.z);
			for (int k = 0; k < drips; k++)
			{
				RM_WallFaceMath.Drip(c.x, c.z, k, out float u, out float w, out float len);
				float x = xl + (xr - xl) * u;
				float zb = top - h * len;
				float ds = RM_WallFaceMath.DripStrength(c.x, c.z, k);
				Color32 head = new Color32(14, 10, 8, (byte)(255f * ds * s));
				Color32 tail = new Color32(14, 10, 8, 0);
				// a soft, wider stain behind each run so it reads as soot washed down, not a painted tooth
				Vector3[] halo = { new Vector3(x - w * 0.6f, y + 0.00025f, zb), new Vector3(x - w * 1.4f, y + 0.00025f, top),
					new Vector3(x + w * 1.4f, y + 0.00025f, top), new Vector3(x + w * 0.6f, y + 0.00025f, zb) };
				Poly(RM_FaceMaterial.TintMat, halo, tail, new Color32(14, 10, 8, (byte)(90f * ds * s)), false, h);
				Vector3[] q = { new Vector3(x - w * 0.15f, y + 0.0003f, zb), new Vector3(x - w * 0.5f, y + 0.0003f, top),
					new Vector3(x + w * 0.5f, y + 0.0003f, top), new Vector3(x + w * 0.15f, y + 0.0003f, zb) };
				Poly(RM_FaceMaterial.TintMat, q, tail, head, false, h);
			}
		}

		/// <summary>The smoke halo on undug ground round a burned cut: per vertex, the distance to the nearest burned
		/// cell within two cells, turned into soot coverage whose reach the lobe noise sets — lumpy, uneven, darkest
		/// at the lip.</summary>
		// scratch for ScorchHalo, reused for every cell of this section's regeneration (every entry is rewritten before use)
		private readonly IntVec3[] haloCells = new IntVec3[25];
		private readonly float[] haloStr = new float[25];
		private readonly Color32[,] haloGrid = new Color32[7, 7];

		private void ScorchHalo(Map map, RM_PitScorch scorch, IntVec3 c, float y)
		{
			// burned cells within reach, with their strength
			float best = 0f;
			int nb = 0;
			IntVec3[] cells = haloCells;
			float[] str = haloStr;
			for (int dx = -2; dx <= 2; dx++)
			{
				for (int dz = -2; dz <= 2; dz++)
				{
					IntVec3 n = new IntVec3(c.x + dx, 0, c.z + dz);
					float sn = scorch.StrengthAt(n);
					if (sn > 0f)
					{
						cells[nb] = n;
						str[nb] = sn;
						nb++;
						if (sn > best) best = sn;
					}
				}
			}
			if (nb == 0)
			{
				return;
			}
			const int N = 6;
			Color32[,] g = haloGrid;
			for (int i = 0; i <= N; i++)
			{
				for (int j = 0; j <= N; j++)
				{
					float x = c.x + i / (float)N, z = c.z + j / (float)N;
					float a = 0f;
					float lobe = Lobes(x, z);
					for (int k = 0; k < nb; k++)
					{
						float ddx = Mathf.Max(0f, Mathf.Max(cells[k].x - x, x - (cells[k].x + 1f)));
						float ddz = Mathf.Max(0f, Mathf.Max(cells[k].z - z, z - (cells[k].z + 1f)));
						a = Mathf.Max(a, RM_WallFaceMath.HaloCover(str[k], Mathf.Sqrt(ddx * ddx + ddz * ddz), lobe));
					}
					g[i, j] = new Color32(255, 255, 255, (byte)(255f * a));
				}
			}
			Grid(RM_FaceMaterial.SootMat, c.x, c.z, 1f, 1f, N, g, y, -1, ScorchUv);
		}

		// ── one water surface (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE; RM_PitReliefMath.SheetPieces; twin
		//    model/water_surface.py) ──
		// Owner, walk 2026-11-25: "Station 6 still shows odd pit walls under water ... Look at the corners", and of station 22: "I
		// suspect you're applying multiple layers over each other instead of calculating a single one". The census
		// (jawa/cell_draw_census) counted nine sheet pieces at alpha 0..229 on one square, and the drowned walls drawn as plain
		// rectangles in a paler light than the dry pit's. Now a square under a clear liquid is drawn as the DRY pit (Regenerate passes
		// level 0 to every face), and over it lies ONE sheet: one colour and one alpha (its level's Seen with the wet-ground darkening
		// composed in), over the dry pit cut by the waterline on each face. A shut sluice with one dry side carries it on its wet
		// half. Opaque liquids (clarity 0: tar, oil, blood) draw nothing here: their own terrain is the surface.

		private readonly System.Collections.Generic.List<float[]> sheetPieces = new System.Collections.Generic.List<float[]>();
		private readonly System.Collections.Generic.List<float[]> facePolys = new System.Collections.Generic.List<float[]>();
		private readonly System.Collections.Generic.List<int> faceKinds = new System.Collections.Generic.List<int>();
		private readonly System.Collections.Generic.List<float> faceCuts = new System.Collections.Generic.List<float>();

		/// <summary>The liquid's one surface over a dug square holding <paramref name="lv"/> notches of a clear liquid: the dry floor
		/// printed opaque (the liquid's terrain has replaced it), then ONE sheet, then the damp band on the dry wall just above the
		/// line.</summary>
		private void WaterSurface(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, float lv, RM_LiquidSurfaceLook look,
			int north, int south, int west, int east, int nw, int ne, bool relief, float y)
		{
			Window(map, eng, c, out float wx0, out float wx1, out float wz0, out float wz1);
			// the dry pit's faces at level 0 with each face's waterline (the dry part's reach from its edge at the true level)
			facePolys.Clear();
			faceKinds.Clear();
			faceCuts.Clear();
			float ww, ew, h, wnw, hnw, wne, hne;
			if (relief)
			{
				RM_PitReliefMath.StepPlan full = RM_PitReliefMath.PlanStep(d, north, south, west, east, nw, ne, 0f);
				RM_PitReliefMath.StepPlan wet = RM_PitReliefMath.PlanStep(d, north, south, west, east, nw, ne, lv);
				RM_PitReliefMath.ReliefFaces(full, facePolys, faceKinds);
				int cw = full.CnwW > 0f ? facePolys.Count - (full.CneW > 0f ? 2 : 1) : -1;
				int ce = full.CneW > 0f ? facePolys.Count - 1 : -1;
				for (int i = 0; i < facePolys.Count; i++)
				{
					faceCuts.Add(RM_PitReliefMath.CutOf(wet, faceKinds[i], i, cw, ce));
				}
				ww = full.L; ew = full.R; h = full.T; wnw = full.CnwW; hnw = full.CnwH; wne = full.CneW; hne = full.CneH;
			}
			else
			{
				h = RM_UnderLiquid.NorthFace(RM_UnderLiquid.Exposed(d, north, 0f));
				ww = RM_UnderLiquid.SideFace(RM_UnderLiquid.Exposed(d, west, 0f));
				ew = RM_UnderLiquid.SideFace(RM_UnderLiquid.Exposed(d, east, 0f));
				RM_PitReliefMath.CornerPiece(d, north, west, nw, 0f, out wnw, out hnw);
				RM_PitReliefMath.CornerPiece(d, north, east, ne, 0f, out wne, out hne);
				RM_PitReliefMath.CornerPiece(d, north, west, nw, lv, out float wnwDry, out float _);
				RM_PitReliefMath.CornerPiece(d, north, east, ne, lv, out float wneDry, out float _);
				if (h > 0f)
				{
					float il = RM_WallFaceMath.MitreInset(ww, h), ir = RM_WallFaceMath.MitreInset(ew, h);
					AddFace(new[] { il, 1f - h, 0f, 1f, 1f, 1f, 1f - ir, 1f - h }, RM_PitReliefMath.CutNorth,
						RM_UnderLiquid.NorthFace(RM_UnderLiquid.Exposed(d, north, lv)));
				}
				float innerTop = h > 0f ? 1f - h : 1f;
				if (ww > 0f)
				{
					AddFace(new[] { 0f, 0f, 0f, 1f, ww, innerTop, ww, 0f }, RM_PitReliefMath.CutWest,
						RM_UnderLiquid.SideFace(RM_UnderLiquid.Exposed(d, west, lv)));
				}
				if (ew > 0f)
				{
					AddFace(new[] { 1f - ew, 0f, 1f - ew, innerTop, 1f, 1f, 1f, 0f }, RM_PitReliefMath.CutEast,
						RM_UnderLiquid.SideFace(RM_UnderLiquid.Exposed(d, east, lv)));
				}
				float[] xz = new float[8];
				if (wnw > 0f)
				{
					RM_PitReliefMath.CornerPoly(false, wnw, hnw, xz);
					AddFace((float[])xz.Clone(), RM_PitReliefMath.CutWest, wnwDry);
				}
				if (wne > 0f)
				{
					RM_PitReliefMath.CornerPoly(true, wne, hne, xz);
					AddFace((float[])xz.Clone(), RM_PitReliefMath.CutEast, wneDry);
				}
			}
			// the floor between the faces, opaque in the dry pit's own ground (the liquid's terrain replaced it)
			TerrainDef floor = RM_ExcavationDepth.DryTerrainFor((byte)Mathf.Clamp(d, RM_ExcavationDepth.Shallow, 255)) ?? TerrainDefOf.Soil;
			int nr = RM_PitReliefMath.FloorRects(ww, ew, h, wnw, hnw, wne, hne, floorRects);
			sheetPieces.Clear();
			for (int i = 0; i < nr; i++)
			{
				float x0 = floorRects[4 * i], z0 = floorRects[4 * i + 1], x1 = floorRects[4 * i + 2], z1 = floorRects[4 * i + 3];
				Quad(RM_FaceMaterial.FaceMat(floor), c.x + x0, c.z + z0, x1 - x0, z1 - z0, y, Opaque, Opaque, UvWorld);
				RM_PitReliefMath.AddUnderLine(new[] { x0, z0, x0, z1, x1, z1, x1, z0 }, -1, 0f, wx0, wx1, wz0, wz1, sheetPieces);
			}
			for (int i = 0; i < facePolys.Count; i++)
			{
				RM_PitReliefMath.AddUnderLine(facePolys[i], faceKinds[i], faceCuts[i], wx0, wx1, wz0, wz1, sheetPieces);
			}
			// ONE sheet: one colour, one alpha, over every piece
			float levelM = lv * RM_UnderLiquid.Notch;
			float seen = RM_UnderLiquid.Seen(look.seeThrough, levelM);
			float wa = RM_UnderLiquid.WetAlpha;
			float share = RM_PitReliefMath.SheetBodyShare(seen, wa);
			Color body = RM_SubmergeDraw.BodyColour(look);
			Color32 sheet = new Color32((byte)(255f * body.r * share + 0.5f), (byte)(255f * body.g * share + 0.5f),
				(byte)(255f * body.b * share + 0.5f), Alpha(RM_PitReliefMath.SheetAlpha(seen, wa)));
			for (int i = 0; i < sheetPieces.Count; i++)
			{
				Fan(RM_FaceMaterial.SheetMat, Verts(c, sheetPieces[i], y + 0.0005f), Uniform(sheetPieces[i].Length / 2, sheet), false, c.z);
			}
			WetEdges(map, eng, c, d, lv, north, south, west, east, wx0, wx1, wz0, wz1, y);
		}

		private void AddFace(float[] xz, int kind, float cut)
		{
			facePolys.Add(xz);
			faceKinds.Add(kind);
			faceCuts.Add(cut);
		}

		private static Vector3[] Verts(IntVec3 c, float[] xz, float y)
		{
			Vector3[] v = new Vector3[xz.Length / 2];
			for (int i = 0; i < v.Length; i++)
			{
				v[i] = new Vector3(c.x + xz[2 * i], y, c.z + xz[2 * i + 1]);
			}
			return v;
		}

		/// <summary>The part of the square the sheet may cover: the whole square, or a shut sluice's wet half when the square across
		/// its other side is a dug square holding no liquid (RM_PitReliefMath.SluiceHalf).</summary>
		private static void Window(Map map, RM_MapComponent_Excavation eng, IntVec3 c, out float wx0, out float wx1, out float wz0, out float wz1)
		{
			wx0 = wz0 = 0f;
			wx1 = wz1 = 1f;
			if (!(c.GetEdifice(map) is Building_RM_FlowDoor door) || !RM_FlowDoorRules.SealsLiquid(door))
			{
				return;
			}
			int rot = door.Rotation.AsInt;
			bool sideView = rot == 1 || rot == 3;
			IntVec3 lo = c + (sideView ? IntVec3.West : IntVec3.South), hi = c + (sideView ? IntVec3.East : IntVec3.North);
			RM_PitReliefMath.SluiceHalf(rot, !DrainedDug(map, eng, lo), !DrainedDug(map, eng, hi), out wx0, out wx1, out wz0, out wz1);
		}

		/// <summary>A dug square holding no liquid (a drained side; the bank or a natural liquid is not one).</summary>
		internal static bool DrainedDug(Map map, RM_MapComponent_Excavation eng, IntVec3 n)
		{
			return n.InBounds(map) && eng.IsExcavated(n) && !eng.IsSourceCell(n) && RM_SubmergeDraw.NoteAt(eng, n) == 0;
		}

		/// <summary>Does any square round <paramref name="c"/> (8-way) carry a liquid terrain, whose vanilla edge fade would lie over
		/// this dry dug square?</summary>
		private static bool BesideLiquidTerrain(Map map, IntVec3 c)
		{
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (!n.InBounds(map))
				{
					continue;
				}
				TerrainDef t = map.terrainGrid.TerrainAt(n);
				if (t != null && (t.IsWater || RM_FluidIdentity.FluidOfTerrain(t) != null))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>A dry dug square's own floor printed whole over vanilla's edge fade of a liquid beside it (RM_PitReliefMath
		/// .ReprintsFloor): the drained side of a shut sluice drew the gate square's water fading over it.</summary>
		private void FloorReprint(Map map, IntVec3 c, float y)
		{
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null || t.IsWater)
			{
				return;
			}
			Material m = RM_FaceMaterial.FaceMat(t);
			if (m != null)
			{
				Quad(m, c.x, c.z, 1f, 1f, y, Opaque, Opaque, UvWorld);
			}
		}

		/// <summary>RIMMANDRAKE_RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED (owner card 2026-11-20 evening: "Maybe dry and
		/// wet have different colors too"; a naive judge picked BLEND): a dark damp band on the dry wall just above the line, inside
		/// each dry face (the face's own polygon, clipped to the band), so two bands never lie over each other at a corner; round a
		/// brim-full pit it lies on the bank beyond the edge. Nothing when the setting is off. No pale waterline
		/// (RIMMANDRAKE_REMOVE_WHITE_FRAMES_AT_EVERY_WATER_EDGE_HE_SAW_THEM_EVERYWHERE).</summary>
		private void WetEdges(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, float lv, int north, int south, int west, int east,
			float wx0, float wx1, float wz0, float wz1, float y)
		{
			float wetA = RM_UnderLiquid.WetBandDarken;
			if (!(RM_UnderLiquid.WetAlpha > 0f) || !(wetA > 0f))
			{
				return;
			}
			float band = RM_UnderLiquid.WetBandCells;
			Material bandMat = RM_FaceMaterial.WetBandMat;
			float yb = y + 0.0003f;
			Color32 none = new Color32(0, 0, 0, 0);
			for (int i = 0; i < facePolys.Count; i++)
			{
				float cut = faceCuts[i];
				int kind = faceKinds[i];
				if (!(cut > 0f))
				{
					continue;   // drowned whole: its band is on the bank (below)
				}
				// the strip of this face between its line and band above it (away from the water)
				float[] q = facePolys[i];
				band0.Clear();
				if (kind == RM_PitReliefMath.CutNorth)
				{
					RM_PitReliefMath.AddUnderLine(q, RM_PitReliefMath.CutWest, 0f, wx0, wx1, 1f - cut, Mathf.Min(1f, 1f - cut + band), band0);
				}
				else if (kind == RM_PitReliefMath.CutWest)
				{
					RM_PitReliefMath.AddUnderLine(q, RM_PitReliefMath.CutWest, 0f, Mathf.Max(wx0, cut - band), Mathf.Min(wx1, cut), wz0, wz1, band0);
				}
				else
				{
					RM_PitReliefMath.AddUnderLine(q, RM_PitReliefMath.CutWest, 0f, Mathf.Max(wx0, 1f - cut), Mathf.Min(wx1, 1f - cut + band), wz0, wz1, band0);
				}
				foreach (float[] s in band0)
				{
					Color32[] col = new Color32[s.Length / 2];
					for (int k = 0; k < col.Length; k++)
					{
						float x = s[2 * k], z = s[2 * k + 1];
						float dist = kind == RM_PitReliefMath.CutNorth ? z - (1f - cut) : kind == RM_PitReliefMath.CutWest ? cut - x : x - (1f - cut);
						col[k] = new Color32(0, 0, 0, Alpha(wetA * (1f - Mathf.Clamp01(dist / band))));
					}
					Fan(bandMat, Verts(c, s, yb), col, false, c.z);
				}
			}
			// a brim-full pit: the band lies on the bank beyond each drowned edge
			Color32 wet = new Color32(0, 0, 0, Alpha(wetA));
			if (RM_UnderLiquid.Exposed(d, north, 0f) > 0f && !(RM_UnderLiquid.NorthFaceAt(d, north, lv) > 0f) && wz1 >= 1f)
			{
				Quad(bandMat, c.x + wx0, c.z + 1f, wx1 - wx0, band, yb, wet, none, UvWorld);
			}
			if (d - south > 0 && !(RM_UnderLiquid.Exposed(d, south, lv) > 0f) && wz0 <= 0f)
			{
				Quad(bandMat, c.x + wx0, c.z - band, wx1 - wx0, band, yb, none, wet, UvWorld);
			}
			if (RM_UnderLiquid.Exposed(d, west, 0f) > 0f && !(RM_UnderLiquid.SideFaceAt(d, west, lv) > 0f) && wx0 <= 0f)
			{
				QuadHWorld(bandMat, c.x - band, c.z + wz0, band, wz1 - wz0, yb, none, wet);
			}
			if (RM_UnderLiquid.Exposed(d, east, 0f) > 0f && !(RM_UnderLiquid.SideFaceAt(d, east, lv) > 0f) && wx1 >= 1f)
			{
				QuadHWorld(bandMat, c.x + 1f, c.z + wz0, band, wz1 - wz0, yb, wet, none);
			}
		}

		private readonly System.Collections.Generic.List<float[]> band0 = new System.Collections.Generic.List<float[]>();

		private static readonly Color32 Opaque = new Color32(255, 255, 255, 255);

		private static byte Alpha(float a) => (byte)(255f * RM_UnderLiquid.Clamp01(a) + 0.5f);

		/// <summary>An (nx x nz)-cell vertex grid over (x0,z0,w,h) with a colour per vertex; nz defaults to nx.</summary>
		private void Grid(Material mat, float x0, float z0, float w, float h, int nx, Color32[,] col, float y, int nz = -1, float uvScale = 0f)
		{
			if (nz < 0) nz = nx;
			if (w <= 0f || h <= 0f)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int b = sm.verts.Count;
			for (int i = 0; i <= nx; i++)
			{
				for (int j = 0; j <= nz; j++)
				{
					float vx = x0 + w * i / nx, vz = z0 + h * j / nz;
					sm.verts.Add(new Vector3(vx, y, vz));
					sm.uvs.Add(uvScale > 0f ? new Vector3(vx * uvScale, vz * uvScale, 0f) : Vector3.zero);
					sm.colors.Add(col[i, j]);
				}
			}
			for (int i = 0; i < nx; i++)
			{
				for (int j = 0; j < nz; j++)
				{
					int v00 = b + i * (nz + 1) + j, v01 = v00 + 1, v10 = v00 + nz + 1, v11 = v10 + 1;
					sm.tris.Add(v00); sm.tris.Add(v01); sm.tris.Add(v11);
					sm.tris.Add(v00); sm.tris.Add(v11); sm.tris.Add(v10);
				}
			}
		}

		/// <summary>A neighbour's floor level: hollow depth (dug, or a dry pond bed's); off-map or a natural liquid cell counts as level with
		/// this cell (no wall into a lake or the map edge).</summary>
		internal static int NeighbourLevel(Map map, RM_MapComponent_Excavation eng, IntVec3 n, int myDepth)
		{
			if (!n.InBounds(map) || eng.IsSourceCell(n))
			{
				return myDepth;
			}
			return eng.HollowDepthAt(n);
		}

		// ── mesh helpers ─────────────────────────────────────────────────────

		private static readonly Color32 White = new Color32(255, 255, 255, 255);

		private const int UvWorld = 0;
		private const int UvFace = 1;

		private void Quad(Material mat, float x0, float z0, float w, float h, float y, Color32 bottom, Color32 top, int uvMode)
		{
			if (mat == null || w <= 0f || h <= 0f)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			sm.verts.Add(new Vector3(x0, y, z0));
			sm.verts.Add(new Vector3(x0, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0));
			if (uvMode == UvWorld)
			{
				sm.uvs.Add(new Vector3(x0, z0, 0f));
				sm.uvs.Add(new Vector3(x0, z0 + h, 0f));
				sm.uvs.Add(new Vector3(x0 + w, z0 + h, 0f));
				sm.uvs.Add(new Vector3(x0 + w, z0, 0f));
			}
			else
			{
				// u along the face in cells; v = 0 at the foot, scaled so a full-cell face shows two pattern repeats
				float v = h * 2f;
				sm.uvs.Add(new Vector3(x0, 0f, 0f));
				sm.uvs.Add(new Vector3(x0, v, 0f));
				sm.uvs.Add(new Vector3(x0 + w, v, 0f));
				sm.uvs.Add(new Vector3(x0 + w, 0f, 0f));
			}
			sm.colors.Add(bottom);
			sm.colors.Add(top);
			sm.colors.Add(top);
			sm.colors.Add(bottom);
			Tris(sm, n);
		}

		/// <summary>An arbitrary convex quad q[0..3] = bottom-left, top-left, top-right, bottom-right; bottom/top colours;
		/// faceUv: u along x, v from the foot (scaled by height), else world uv.</summary>
		private void Poly(Material mat, Vector3[] q, Color32 bottom, Color32 top, bool faceUv, float h)
		{
			if (mat == null)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			float zb = Mathf.Min(q[0].z, q[3].z);
			for (int i = 0; i < 4; i++)
			{
				sm.verts.Add(q[i]);
				sm.uvs.Add(faceUv ? new Vector3(q[i].x, (q[i].z - zb) * 2f, 0f) : new Vector3(q[i].x, q[i].z, 0f));
				sm.colors.Add(i == 0 || i == 3 ? bottom : top);
			}
			Tris(sm, n);
		}

		/// <summary>Vertical gradient (bottom→top) in the plain vertex-colour material — the fallback look.</summary>
		private void QuadV(float x0, float z0, float w, float h, float y, Color32 bottom, Color32 top)
		{
			QuadVMat(MaterialPool.MatFrom(new MaterialRequest(BaseContent.WhiteTex, ShaderDatabase.VertexColor)), x0, z0, w, h, y, bottom, top);
		}

		private void QuadVMat(Material mat, float x0, float z0, float w, float h, float y, Color32 bottom, Color32 top)
		{
			Quad(mat, x0, z0, w, h, y, bottom, top, UvFace);
		}

		/// <summary>Horizontal gradient (left→right).</summary>
		private void QuadHMat(Material mat, float x0, float z0, float w, float h, float y, Color32 left, Color32 right)
		{
			if (w <= 0f || h <= 0f)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			sm.verts.Add(new Vector3(x0, y, z0));
			sm.verts.Add(new Vector3(x0, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0));
			for (int i = 0; i < 4; i++)
			{
				sm.uvs.Add(Vector3.zero);
			}
			sm.colors.Add(left);
			sm.colors.Add(left);
			sm.colors.Add(right);
			sm.colors.Add(right);
			Tris(sm, n);
		}

		/// <summary>Horizontal gradient (left→right) with world uvs (a rough-fade material breaks its edge up by them).</summary>
		private void QuadHWorld(Material mat, float x0, float z0, float w, float h, float y, Color32 left, Color32 right)
		{
			if (mat == null || w <= 0f || h <= 0f)
			{
				return;
			}
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			sm.verts.Add(new Vector3(x0, y, z0));
			sm.verts.Add(new Vector3(x0, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0));
			sm.uvs.Add(new Vector3(x0, z0, 0f));
			sm.uvs.Add(new Vector3(x0, z0 + h, 0f));
			sm.uvs.Add(new Vector3(x0 + w, z0 + h, 0f));
			sm.uvs.Add(new Vector3(x0 + w, z0, 0f));
			sm.colors.Add(left);
			sm.colors.Add(left);
			sm.colors.Add(right);
			sm.colors.Add(right);
			Tris(sm, n);
		}

		private static void Tris(LayerSubMesh sm, int n)
		{
			sm.tris.Add(n);
			sm.tris.Add(n + 1);
			sm.tris.Add(n + 2);
			sm.tris.Add(n);
			sm.tris.Add(n + 2);
			sm.tris.Add(n + 3);
		}

		/// <summary>The setting was flipped: redraw every map.</summary>
		public static void RedrawAll()
		{
			if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
			{
				return;
			}
			foreach (Map m in Find.Maps)
			{
				m.mapDrawer?.RegenerateEverythingNow();
			}
		}
	}
}
