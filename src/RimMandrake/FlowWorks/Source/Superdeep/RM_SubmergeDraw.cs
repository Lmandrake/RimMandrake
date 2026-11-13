using System.Collections.Generic;
using System.Globalization;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: what stands in a dug square drawn under the liquid in it by ONE rule,
	/// <see cref="RM_UnderLiquid"/> (owner's live look 2026-11-12: "It's as though each case is independently set in these
	/// variables, badly (major fix)"). Map-mesh things (ladders hung or lying flat, the pit ramp, items, minified things,
	/// the swale) are split where they are printed: SectionLayer_ThingsGeneral.TakePrintFrom opens a context for the thing
	/// (<see cref="Begin"/>), and every Printer_Plane.PrintPlane it makes (Graphic.Print, MinifiedThing's crate and its
	/// content, atlas tiles and flips included) is drawn as the part above the line, as it is, plus the drowned part in up to
	/// RM_UnderLiquid.Bands bands at alpha RM_UnderLiquid.Seen over the liquid terrain (clear liquids: tinted by depth;
	/// opaque: hidden). The realtime gates (RM_FlowDoors) and stakes (RM_Spikes) draw the same split from <see cref="Wet"/>
	/// and <see cref="DrawUnder"/>; the pit's walls and floor (SectionLayer_RMExcavationWalls) use the same level, cut and
	/// law. Setting pitSubmergeCutEnabled (on): off draws them whole over the liquid.
	///
	/// Cost: nothing while dry beyond one note per dug cell a thing was printed on. The note (RM_MapComponent_Excavation.
	/// submergeDrawn, cell index -> RM_UnderLiquid.LevelNote of the true level) is what the cell was printed at; the engine's
	/// picture-writer (ApplyFillTerrain, which every write of a dug square's liquid calls) re-meshes a noted cell whose note
	/// moved (<see cref="FillPictured"/>), and the re-print notes it again. Prints run only on a section rebuild; the split
	/// uses static buffers and cached faded materials.
	/// </summary>
	public static class RM_SubmergeDraw
	{
		public static bool On => RimMandrakeFlowWorksSettings.pitSubmergeCutEnabled;

		/// <summary>The quarter-notch note of the true level (whole notch + part-notch) standing on <paramref name="c"/>.</summary>
		public static int NoteAt(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return RM_UnderLiquid.LevelNote(eng.WaterDlAt(c) / (double)RM_LevelSolve.U);
		}

		/// <summary>Called by RM_MapComponent_Excavation.ApplyFillTerrain for a dug square while any cell is noted: a cell
		/// printed at another level re-meshes (its things, and the walls layer through RM_WaterLookDraw.LookFlag).</summary>
		public static void FillPictured(RM_MapComponent_Excavation eng, Map map, IntVec3 c, int index)
		{
			if (eng.submergeDrawn.TryGetValue(index, out int drawn) && drawn != NoteAt(eng, c))
			{
				eng.submergeDrawn.Remove(index);
				map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things | RM_WaterLookDraw.LookFlag);
			}
		}

		/// <summary>How clear the liquid on <paramref name="c"/> is (RM_LiquidSurfaceLook.seeThrough: the share of the view
		/// left after 1 m; 0 = opaque): the cell's fluid's look, else its terrain's, else fresh water's.</summary>
		public static float ClarityAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			RM_LiquidSurfaceLook look = LookAt(map, eng, c);
			return look != null ? look.seeThrough : 0f;
		}

		public static RM_LiquidSurfaceLook LookAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			FluidDef f = eng?.FluidAt(c);
			RM_LiquidSurfaceLook look = f != null ? RM_LiquidLooks.LookOfFluid(f) : null;
			if (look == null)
			{
				look = RM_LiquidSurface.LookFor(map.terrainGrid.TerrainAt(c));
			}
			if (look == null)
			{
				look = RM_LiquidSurface.LookFor(RM_WaterLadderDefs.Freshwater(RM_WaterLadder.Rung.VeryShallow));
			}
			return look;
		}

		/// <summary>The dug depth (notches), the true level (m, never above the floor's depth: no level above the bank) and
		/// the clarity under a thing; false when it stands on no dug square, the setting is off or it is dry. Notes the
		/// level printed at when <paramref name="noteIt"/> (a map-mesh print; a dry print too: the first liquid must re-mesh
		/// it). The realtime drawers pass false.</summary>
		public static bool Wet(Thing t, out int depth, out float levelMetres, out float clarity, bool noteIt = true)
		{
			depth = 0;
			levelMetres = 0f;
			clarity = 0f;
			if (!On || t == null || !t.Spawned)
			{
				return false;
			}
			Map map = t.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return false;
			}
			IntVec3 c = t.Position;
			depth = eng.HollowDepthAt(c);
			if (depth <= 0)
			{
				return false;
			}
			int note = NoteAt(eng, c);
			if (noteIt)
			{
				eng.submergeDrawn[map.cellIndices.CellToIndex(c)] = note;
			}
			if (note <= 0)
			{
				return false;
			}
			float lv = RM_UnderLiquid.NoteLevel(note);
			levelMetres = (lv > depth ? depth : lv) * RM_UnderLiquid.Notch;
			clarity = ClarityAt(map, eng, c);
			return true;
		}

		/// <summary>The levels a ladder's wall drops (its own depth when it hangs on none).</summary>
		private static int LadderDrop(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			int drop = d - SectionLayer_RMExcavationWalls.NeighbourLevel(t.Map, eng, t.Position + t.Rotation.FacingCell, d);
			return drop > 0 ? drop : d;
		}

		private static bool LiesFlat(Thing t, Graphic g)
		{
			RM_CompLadder comp = t.TryGetComp<RM_CompLadder>();
			return comp != null && g == comp.ShortGraphic;
		}

		/// <summary>The ramp points uphill: its downhill end is the opposite side.</summary>
		private static int RampFrom(int rot) => rot == 0 ? RM_UnderLiquid.FromSouth : rot == 1 ? RM_UnderLiquid.FromWest
			: rot == 2 ? RM_UnderLiquid.FromNorth : RM_UnderLiquid.FromEast;

		private static int RampRise(Thing t, RM_MapComponent_Excavation eng, int d)
		{
			IntVec3 up = t.Position + t.Rotation.FacingCell;
			return up.InBounds(t.Map) ? d - eng.HollowDepthAt(up) : d;
		}

		private static ThingDef swaleDef;
		private static bool swaleResolved;

		private static bool IsSwale(ThingDef d)
		{
			if (!swaleResolved)
			{
				swaleDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Swale");
				swaleResolved = true;
			}
			return d == swaleDef && d != null;
		}

		/// <summary>The drawn height (m) of a thing standing on the floor, or 0 when it is not one this draws.</summary>
		private static float StandingMetres(Thing t)
		{
			if (t is MinifiedThing)
			{
				return RM_UnderLiquid.MinifiedMetres;
			}
			if (t.def.category == ThingCategory.Item)
			{
				return RM_UnderLiquid.ItemMetres;
			}
			return IsSwale(t.def) ? RM_UnderLiquid.SwaleMetres : 0f;
		}

		// ── the print context (main thread only: section rebuilds) ──────────────

		private static bool ctxOn, inSplit, ctxWorld;
		private static int ctxFrom;
		private static float ctxShare, ctxLevel, ctxHeight, ctxClarity, ctxCut, ctxFoot;
		private static IntVec3 ctxCell;

		/// <summary>SectionLayer_ThingsGeneral.TakePrintFrom prefix: opens the split for a thing standing wet in a dug
		/// square (nothing for anything else).</summary>
		public static void Begin(Thing t)
		{
			ctxOn = false;
			if (!On || t == null)
			{
				return;
			}
			bool ladder = t is RM_Building_Ladder, ramp = t is RM_Building_PitRamp;
			float standing = ladder || ramp ? 0f : StandingMetres(t);
			if (!ladder && !ramp && standing <= 0f)
			{
				return;
			}
			if (!Wet(t, out int d, out float levelM, out float clarity))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(t.Map);
			ctxWorld = false;
			ctxFrom = RM_UnderLiquid.FromSouth;
			ctxLevel = levelM;
			ctxClarity = clarity;
			ctxCell = t.Position;
			int rot = t.Rotation.AsInt;
			if (ladder && !LiesFlat(t, t.Graphic))
			{
				if (rot == 2)
				{
					return;   // hung on the near wall: only its top above the near rim shows, never under
				}
				int drop = LadderDrop(t, eng, d);
				float cut = RM_UnderLiquid.Waterline(rot, drop, levelM / RM_UnderLiquid.Notch);
				if (cut < 0f)
				{
					return;
				}
				ctxWorld = true;
				ctxFrom = RM_UnderLiquid.HungFrom(rot);
				ctxCut = cut;
				ctxFoot = rot == 0 ? 1f - RM_UnderLiquid.NorthFace(drop)
					: rot == 1 ? 1f - RM_UnderLiquid.SideFace(drop) : RM_UnderLiquid.SideFace(drop);
			}
			else if (ladder)
			{
				ctxHeight = RM_UnderLiquid.LyingLadderMetres;
			}
			else if (ramp)
			{
				ctxFrom = RampFrom(rot);
				ctxHeight = RampRise(t, eng, d) * RM_UnderLiquid.Notch;
			}
			else
			{
				ctxHeight = standing;
			}
			ctxShare = RM_UnderLiquid.Share(levelM, 0f, ctxHeight);
			ctxOn = true;
		}

		public static void End()
		{
			ctxOn = false;
		}

		private static readonly float[] Uv0 = new float[8];
		private static readonly float[] Uv = new float[8];
		private static readonly Vector2[] UvBuf = new Vector2[4];

		/// <summary>Printer_Plane.PrintPlane prefix while a context is open: true when this drew the plane (split, faded or
		/// hidden), false = vanilla prints it as asked.</summary>
		internal static bool Split(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot, bool flipUv,
			Vector2[] uvs, Color32[] colors, float bias, float payload)
		{
			if (!ctxOn || inSplit || mat == null)
			{
				return false;
			}
			float x0 = center.x - size.x * 0.5f, x1 = center.x + size.x * 0.5f;
			float z0 = center.z - size.y * 0.5f, z1 = center.z + size.y * 0.5f;
			bool alongZ = ctxFrom == RM_UnderLiquid.FromSouth || ctxFrom == RM_UnderLiquid.FromNorth;
			bool fromLow = ctxFrom == RM_UnderLiquid.FromSouth || ctxFrom == RM_UnderLiquid.FromWest;
			float lo = alongZ ? z0 - ctxCell.z : x0 - ctxCell.x, hi = alongZ ? z1 - ctxCell.z : x1 - ctxCell.x;
			float s = ctxWorld ? RM_UnderLiquid.SpanShare(lo, hi, ctxCut, fromLow) : ctxShare;
			if (s <= 0f)
			{
				return false;
			}
			inSplit = true;
			try
			{
				if (rot != 0f)
				{
					// a turned sprite (an item's random lie): whole above the line until half of it is under, then whole at
					// the law's alpha for its middle
					if (s >= 0.5f)
					{
						int q = RM_UnderLiquid.BandAlphaStep(ctxClarity, MetresOf(0.5f, lo, hi, fromLow));
						Material m = q > 0 ? Faded(mat, q) : null;
						if (m != null)
						{
							Printer_Plane.PrintPlane(layer, center, size, m, rot, flipUv, uvs, colors, bias, payload);
						}
						return true;
					}
					return false;
				}
				if (uvs != null)
				{
					for (int j = 0; j < 4; j++)
					{
						Uv0[j * 2] = uvs[j].x;
						Uv0[j * 2 + 1] = uvs[j].y;
					}
				}
				else
				{
					// Printer_Plane.DefaultUvs / DefaultUvsFlipped, corner order (-x-z, -x+z, +x+z, +x-z)
					float ul = flipUv ? 1f : 0f, ur = flipUv ? 0f : 1f;
					Uv0[0] = ul; Uv0[1] = 0f; Uv0[2] = ul; Uv0[3] = 1f; Uv0[4] = ur; Uv0[5] = 1f; Uv0[6] = ur; Uv0[7] = 0f;
				}
				if (s < 1f)
				{
					Piece(layer, center.y, mat, colors, bias, payload, s, 1f, x0, z0, x1, z1);
				}
				int n = RM_UnderLiquid.BandsFor(ctxClarity, MetresOf(s, lo, hi, fromLow), MetresOf(0f, lo, hi, fromLow));
				for (int b = 0; b < n; b++)
				{
					float a = s * b / n, e = s * (b + 1) / n;
					int q = RM_UnderLiquid.BandAlphaStep(ctxClarity, MetresOf((a + e) * 0.5f, lo, hi, fromLow));
					Material m = q > 0 ? Faded(mat, q) : null;
					if (m != null)
					{
						Piece(layer, center.y, m, colors, bias, payload, a, e, x0, z0, x1, z1);
					}
				}
				return true;
			}
			finally
			{
				inSplit = false;
			}
		}

		/// <summary>Metres of liquid over the point a share <paramref name="share"/> in from the drowned side of a sprite
		/// spanning [lo, hi] (cell-local): standing things by their drawn height, hung ones between the waterline and their
		/// wall's foot.</summary>
		private static float MetresOf(float share, float lo, float hi, bool fromLow)
		{
			if (!ctxWorld)
			{
				float m = ctxLevel - share * ctxHeight;
				return m < 0f ? 0f : m;
			}
			float pos = fromLow ? lo + share * (hi - lo) : hi - share * (hi - lo);
			return RM_UnderLiquid.MetresAt(pos, ctxCut, ctxFoot, 0f, ctxLevel);
		}

		private static void Piece(MapDrawLayer layer, float y, Material mat, Color32[] colors, float bias, float payload,
			float a, float b, float x0, float z0, float x1, float z1)
		{
			System.Array.Copy(Uv0, Uv, 8);
			RM_UnderLiquid.Slice(ctxFrom, a, b, Uv, ref x0, ref z0, ref x1, ref z1);
			if (x1 - x0 <= 0f || z1 - z0 <= 0f)
			{
				return;
			}
			for (int j = 0; j < 4; j++)
			{
				UvBuf[j] = new Vector2(Uv[j * 2], Uv[j * 2 + 1]);
			}
			Printer_Plane.PrintPlane(layer, new Vector3((x0 + x1) * 0.5f, y, (z0 + z1) * 0.5f), new Vector2(x1 - x0, z1 - z0),
				mat, 0f, false, UvBuf, colors, bias, payload);
		}

		private static readonly Dictionary<long, Material> faded = new Dictionary<long, Material>();

		/// <summary><paramref name="mat"/> at alpha <paramref name="q"/>/Steps on the transparent shader (its texture and
		/// colour kept): how a drowned part is seen over the liquid. Null when the material has no texture.</summary>
		public static Material Faded(Material mat, int q)
		{
			if (q >= RM_UnderLiquid.Steps)
			{
				return mat;
			}
			long key = ((long)mat.GetInstanceID() << 8) | (long)q;
			if (faded.TryGetValue(key, out Material m) && m != null)
			{
				return m;
			}
			Texture2D tex = mat.mainTexture as Texture2D;
			if (tex == null)
			{
				return null;
			}
			Color c = mat.color;
			m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent,
				new Color(c.r, c.g, c.b, c.a * q / RM_UnderLiquid.Steps)));
			faded[key] = m;
			return m;
		}

		// ── realtime drawers (gates, stakes) ───────────────────────────────

		private static readonly Dictionary<long, Mesh> sliceMeshes = new Dictionary<long, Mesh>();

		/// <summary>A realtime plane of <paramref name="size"/> keeping only the slice [a, b] measured from its foot (uvs
		/// lerped; unflipped art). Cached per size and slice (1/128 steps), so a frame allocates nothing.</summary>
		public static Mesh SliceMesh(Vector2 size, float a, float b)
		{
			int ia = Mathf.RoundToInt(RM_UnderLiquid.Clamp01(a) * 128f), ib = Mathf.RoundToInt(RM_UnderLiquid.Clamp01(b) * 128f);
			if (ib <= ia)
			{
				return null;
			}
			long key = ((long)Mathf.RoundToInt(size.x * 1000f) << 40) | ((long)Mathf.RoundToInt(size.y * 1000f) << 16) | ((long)ia << 8) | (long)ib;
			if (sliceMeshes.TryGetValue(key, out Mesh m) && m != null)
			{
				return m;
			}
			float sa = ia / 128f, sb = ib / 128f, hw = size.x * 0.5f, hh = size.y * 0.5f;
			float za = -hh + size.y * sa, zb = -hh + size.y * sb;
			m = new Mesh { name = "RM_SubmergeSlice" };
			m.vertices = new[] { new Vector3(-hw, 0f, za), new Vector3(-hw, 0f, zb), new Vector3(hw, 0f, zb), new Vector3(hw, 0f, za) };
			m.uv = new[] { new Vector2(0f, sa), new Vector2(0f, sb), new Vector2(1f, sb), new Vector2(1f, sa) };
			m.triangles = new[] { 0, 1, 2, 0, 2, 3 };
			m.RecalculateNormals();
			m.RecalculateBounds();
			sliceMeshes[key] = m;
			return m;
		}

		/// <summary>A realtime upright sprite (<paramref name="whole"/>, <paramref name="size"/>) whose foot lies
		/// <paramref name="footMetres"/> under the liquid and which spans <paramref name="heightMetres"/> up from there:
		/// the part above the line as it is, the drowned part in bands at the law's alpha. Returns the share drawn under.</summary>
		public static float DrawUnder(Mesh whole, Vector2 size, Matrix4x4 at, Material mat, float footMetres, float heightMetres, float clarity)
		{
			float s = RM_UnderLiquid.Share(footMetres, 0f, heightMetres);
			if (s <= 0f)
			{
				UnityEngine.Graphics.DrawMesh(whole, at, mat, 0);
				return 0f;
			}
			if (s < 1f)
			{
				Mesh kept = SliceMesh(size, s, 1f);
				if (kept != null)
				{
					UnityEngine.Graphics.DrawMesh(kept, at, mat, 0);
				}
			}
			float line = footMetres - s * heightMetres;
			int n = RM_UnderLiquid.BandsFor(clarity, line < 0f ? 0f : line, footMetres);
			for (int b = 0; b < n; b++)
			{
				float a = s * b / n, e = s * (b + 1) / n, mid = footMetres - (a + e) * 0.5f * heightMetres;
				int q = RM_UnderLiquid.BandAlphaStep(clarity, mid);
				Material m = q > 0 ? Faded(mat, q) : null;
				Mesh band = m != null ? SliceMesh(size, a, e) : null;
				if (band != null)
				{
					UnityEngine.Graphics.DrawMesh(band, at, m, 0);
				}
			}
			return s;
		}

		/// <summary>Scene helper for pit_fittings_matrix.py: "x,z,w,h,fill[,FluidDefName]" writes that whole-notch fill on every
		/// dug square of the rect through the engine's own driver write (TrySetDriverFillOutcome; default fluid = the map's).
		/// -> "FILL applied=N refused=N notOwned=N fluid=..." or "REFUSED: ...".</summary>
		public static string ProofFillRect(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null || p.Length < 5 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z)
				|| !int.TryParse(p[2].Trim(), out int w) || !int.TryParse(p[3].Trim(), out int h) || !int.TryParse(p[4].Trim(), out int fill)
				|| w < 1 || h < 1 || w * h > 400)
			{
				return "REFUSED: need a current map with FlowWorks and \"x,z,w,h,fill[,FluidDefName]\" (w*h <= 400)";
			}
			FluidDef fluid = null;
			if (p.Length > 5 && p[5].Trim().Length > 0)
			{
				fluid = DefDatabase<FluidDef>.GetNamedSilentFail(p[5].Trim());
				if (fluid == null)
				{
					return "REFUSED: no FluidDef " + p[5].Trim();
				}
			}
			int applied = 0, refused = 0, notOwned = 0;
			foreach (IntVec3 c in new CellRect(x, z, w, h))
			{
				switch (eng.TrySetDriverFillOutcome(c, fill, fluid))
				{
					case RM_MapComponent_Excavation.DriverFillOutcome.Applied: applied++; break;
					case RM_MapComponent_Excavation.DriverFillOutcome.Refused: refused++; break;
					default: notOwned++; break;
				}
			}
			return "FILL applied=" + applied + " refused=" + refused + " notOwned=" + notOwned + " fluid=" + (fluid?.defName ?? "default");
		}

		private static string F(float v, string fmt = "F3") => v < 0f ? "-" : v.ToString(fmt, CultureInfo.InvariantCulture);

		/// <summary>The waterline the wall layer draws on the face a ladder hangs on, computed the way
		/// SectionLayer_RMExcavationWalls does (Exposed at the true level; N: 1 - NorthFace, E: 1 - SideFace, W: SideFace):
		/// the proof's independent reference for the ladder's cut. -1 when no face shows liquid.</summary>
		private static float FaceWaterline(Thing t, RM_MapComponent_Excavation eng, int d, float lv)
		{
			int rot = t.Rotation.AsInt;
			if (rot == 2 || lv <= 0f)
			{
				return RM_UnderLiquid.NoCut;
			}
			int nb = SectionLayer_RMExcavationWalls.NeighbourLevel(t.Map, eng, t.Position + t.Rotation.FacingCell, d);
			if (d - nb <= 0)
			{
				return RM_UnderLiquid.NoCut;   // hangs on no wall: no face to meet
			}
			float e = RM_UnderLiquid.Exposed(d, nb, lv);
			if (rot == 0)
			{
				return 1f - RM_UnderLiquid.NorthFace(e);
			}
			float w = RM_UnderLiquid.SideFace(e);
			return rot == 1 ? 1f - w : w;
		}

		/// <summary>
		/// Proof read for wall_art_scene.py's "submerge" and pit_fittings_matrix.py's rows: the first thing at "x,z" this
		/// draws, and what the one rule decides for it.
		/// "def=RM_Ladder class=RM_Building_Ladder kind=hung rot=0 depth=4 fill=3 level=3.25 flat=no cutZ=0.880 faceZ=0.880
		/// share=0.760 clarity=0.450 seenLine=0.756 seenFoot=0.120 printedLevel=3.25 setting=on liquid=WaterDeep tint=0.24,0.24,0.24"
		/// (fill = whole notches; level = the true level, quarter notches, what everything is drawn at; cutZ = the cell-local
		/// waterline the ladder is cut at, faceZ = the one the wall layer draws on its face, "-" for none: they must agree;
		/// share = of the sprite under the line, from its foot (a hung ladder: of its in-pit span, wall foot to rim); clarity
		/// = the liquid's; seenLine / seenFoot = how much of the drowned part is seen just under the line and at its foot (0
		/// opaque); printedLevel = the level the cell was last printed at, "-" for the realtime gates and stakes or when not
		/// printed since the last change; tint = the liquid look's tint).
		/// Else "REFUSED: ...".
		/// </summary>
		public static string ProofSubmerge(string arg)
		{
			Map map = Find.CurrentMap;
			string[] p = (arg ?? "").Split(',');
			if (map == null || p.Length < 2 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z))
			{
				return "REFUSED: need a current map and \"x,z\"";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (!c.InBounds(map) || eng == null)
			{
				return "REFUSED: cell off the map or no excavation engine";
			}
			int d = eng.HollowDepthAt(c), f = eng.FillAt(c);
			float lv = RM_UnderLiquid.NoteLevel(NoteAt(eng, c));
			if (lv > d)
			{
				lv = d;
			}
			float levelM = lv * RM_UnderLiquid.Notch;
			RM_LiquidSurfaceLook look = lv > 0f ? LookAt(map, eng, c) : null;
			float clarity = look != null ? look.seeThrough : 0f;
			List<Thing> list = c.GetThingList(map);
			for (int i = 0; i < list.Count; i++)
			{
				Thing t = list[i];
				float share, lineM, footM, heightM;
				string kind, faces = "";
				if (t is RM_Building_Ladder && !LiesFlat(t, t.Graphic))
				{
					kind = "hung";
					int drop = d > 0 ? LadderDrop(t, eng, d) : 0;
					float cut = d <= 0 ? RM_UnderLiquid.NoCut : RM_UnderLiquid.Waterline(t.Rotation.AsInt, drop, lv);
					int r = t.Rotation.AsInt;
					// of its in-pit span, wall foot to rim, along its face (N: z up to 1; E: x up to 1; W: x down to 0)
					float side = RM_UnderLiquid.SideFace(drop);
					share = cut < 0f ? 0f : r == 0 ? RM_UnderLiquid.SpanShare(1f - RM_UnderLiquid.NorthFace(drop), 1f, cut, true)
						: r == 1 ? RM_UnderLiquid.SpanShare(1f - side, 1f, cut, true) : RM_UnderLiquid.SpanShare(0f, side, cut, false);
					lineM = 0f;
					footM = share > 0f ? levelM : 0f;
					heightM = drop * RM_UnderLiquid.Notch;
					faces = " flat=no cutZ=" + F(cut) + " faceZ=" + F(d <= 0 ? RM_UnderLiquid.NoCut : FaceWaterline(t, eng, d, lv));
				}
				else if (t is RM_Building_Ladder)
				{
					kind = "flat";
					heightM = RM_UnderLiquid.LyingLadderMetres;
					faces = " flat=yes cutZ=- faceZ=-";
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is RM_Building_PitRamp)
				{
					kind = "ramp";
					heightM = d <= 0 ? 0f : RampRise(t, eng, d) * RM_UnderLiquid.Notch;
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is Building_RM_Spikes)
				{
					kind = "stakes";
					heightM = RM_UnderLiquid.StakeMetres;
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if (t is Building_RM_FlowDoor)
				{
					kind = "gate";
					heightM = RM_UnderLiquid.GateMetres(d);
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else if ((heightM = StandingMetres(t)) > 0f)
				{
					kind = t is MinifiedThing ? "minified" : t.def.category == ThingCategory.Item ? "item" : "swale";
					share = d <= 0 ? 0f : RM_UnderLiquid.Share(levelM, 0f, heightM);
					lineM = levelM - share * heightM; footM = levelM;
				}
				else
				{
					continue;
				}
				if (lineM < 0f)
				{
					lineM = 0f;
				}
				bool wet = share > 0f;
				float seenLine = wet ? RM_UnderLiquid.Seen(clarity, lineM <= 0f ? 0.0001f : lineM) : 1f;
				float seenFoot = wet ? RM_UnderLiquid.Seen(clarity, footM) : 1f;
				bool realtime = t is Building_RM_Spikes || t is Building_RM_FlowDoor;
				string printed = realtime || !eng.submergeDrawn.TryGetValue(map.cellIndices.CellToIndex(c), out int pn)
					? "-" : RM_UnderLiquid.NoteLevel(pn).ToString("F2", CultureInfo.InvariantCulture);
				Color tint = look != null ? look.tint : Color.white;
				return "def=" + t.def.defName + " class=" + t.GetType().Name + " kind=" + kind + " rot=" + t.Rotation.AsInt
					+ " depth=" + d + " fill=" + f + " level=" + lv.ToString("F2", CultureInfo.InvariantCulture) + faces
					+ " share=" + F(share) + " clarity=" + F(clarity) + " seenLine=" + F(seenLine) + " seenFoot=" + F(seenFoot)
					+ " printedLevel=" + printed + " setting=" + (On ? "on" : "off")
					+ " liquid=" + (map.terrainGrid.TerrainAt(c)?.defName ?? "-")
					+ " tint=" + F(tint.r, "F2") + "," + F(tint.g, "F2") + "," + F(tint.b, "F2");
			}
			return "REFUSED: nothing drawn under liquid at " + x + "," + z + " (depth=" + d + " fill=" + f + ")";
		}
	}

	/// <summary>Opens the under-liquid split for each thing the general things layer prints (RM_SubmergeDraw.Begin).</summary>
	[HarmonyPatch(typeof(SectionLayer_ThingsGeneral), "TakePrintFrom")]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergeTakePrint
	{
		[HarmonyPrefix]
		private static void Prefix(Thing t)
		{
			RM_SubmergeDraw.Begin(t);
		}

		[HarmonyFinalizer]
		private static void Finalizer()
		{
			RM_SubmergeDraw.End();
		}
	}

	/// <summary>Draws each plane of a thing in an open split as its part above the line plus its drowned bands.</summary>
	[HarmonyPatch(typeof(Printer_Plane), nameof(Printer_Plane.PrintPlane))]
	[RimMandrake.Shared.PatchFeature("Pit contents under liquid (planes)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled")]
	internal static class Patch_RM_SubmergePrintPlane
	{
		[HarmonyPrefix]
		private static bool Prefix(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot, bool flipUv,
			Vector2[] uvs, Color32[] colors, float topVerticesAltitudeBias, float uvzPayload)
		{
			return !RM_SubmergeDraw.Split(layer, center, size, mat, rot, flipUv, uvs, colors, topVerticesAltitudeBias, uvzPayload);
		}
	}
}
