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
	///   • Liquid standing in the cut covers the foot of the faces (RM_WallFaceMath.ExposedDrop).
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
			relevantChangeTypes = MapMeshFlagDefOf.Terrain;
		}

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
				int d = eng.ExcavatedDepthAt(c);
				float sc = scorch != null ? scorch.StrengthAt(c) : 0f;
				if (d == 0)
				{
					if (material && BordersCut(map, eng, c))
					{
						Collar(map, c, y - 0.001f);
					}
					if (scorch != null)
					{
						ScorchHalo(map, scorch, c, y);
					}
					continue;
				}
				int f = eng.FillAt(c);
				int north = NeighbourLevel(map, eng, c + IntVec3.North, d);
				int west = NeighbourLevel(map, eng, c + IntVec3.West, d);
				int east = NeighbourLevel(map, eng, c + IntVec3.East, d);
				int south = NeighbourLevel(map, eng, c + IntVec3.South, d);
				if (RimMandrakeFlowWorksSettings.pitOutlineEnabled)
				{
					Outline(c, d, north, south, west, east, y + 0.0009f);
				}
				int nd = RM_WallFaceMath.ExposedDrop(d, north, f);
				int wd = RM_WallFaceMath.ExposedDrop(d, west, f);
				int ed = RM_WallFaceMath.ExposedDrop(d, east, f);
				float h = RM_WallFaceMath.NorthFaceHeight(nd);
				if (sc > 0f && f == 0)
				{
					// principle 5: the SAME empty pit, charred — vertex-colour char over the normal floor
					CharFloor(c, d, north, south, west, east, 1f - h, sc, y - 0.0005f);
					// 2026-10-06 review: "it needs blast marks and blackened bits"
					if (RM_WallFaceMath.HasFloorBlast(c.x, c.z))
					{
						BlastMark(c.x + 0.5f, c.z + (1f - h) * 0.5f, 0.42f, Gen.HashCombineInt(c.x * 31, c.z), sc, y - 0.0002f);
					}
				}
				if (f > 0 && material && RimMandrakeFlowWorksSettings.liquidSeeThroughEnabled)
				{
					SeeThrough(map, eng, c, d, f, north, y - 0.0008f);
				}
				if (!material)
				{
					if (nd > 0)
					{
						QuadV(c.x, c.z + 1f - h, 1f, h, y, Dark(d), Rim);
					}
					if (wd > 0)
					{
						Color32 shade = Dark(d + 1);
						QuadV(c.x, c.z, RM_WallFaceMath.SideFaceWidth(wd), 1f, y + 0.001f, shade, shade);
					}
					if (ed > 0)
					{
						float w = RM_WallFaceMath.SideFaceWidth(ed);
						QuadV(c.x + 1f - w, c.z, w, 1f, y + 0.001f, Earth, Earth);
					}
					continue;
				}
				float ww = RM_WallFaceMath.SideFaceWidth(wd);
				float ew = RM_WallFaceMath.SideFaceWidth(ed);
				if (nd > 0)
				{
					NorthFace(map, eng, c, d, h, ww, ew, y, sc);
				}
				if (wd > 0)
				{
					SideFace(map, eng, c, c + IntVec3.West, d, ww, h, false, y + 0.001f, sc);
				}
				if (ed > 0)
				{
					SideFace(map, eng, c, c + IntVec3.East, d, ew, h, true, y + 0.001f, sc);
				}
			}
			FinalizeMesh(MeshParts.All);
		}

		/// <summary>The far (north) bank's face, drawn as vanilla draws a wall's south bevel (MEASURED from the owner's
		/// steel-wall shot): a flat band the ground's own material, lit x1.85 against the ground, hanging directly from
		/// the rim, with 45-degree mitred lower corners where a side bevel meets it.</summary>
		private void NorthFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, float h, float ww, float ew, float y, float scorch)
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
				byte s = (byte)(255f * RM_WallFaceMath.FaceSootAlpha(scorch, 0.3f));
				Poly(RM_FaceMaterial.ShadeMat, Lift(q, 0.0007f), new Color32(22, 15, 10, s), new Color32(22, 15, 10, (byte)(s * 0.75f)), false, 1f);
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
			Material m = RM_FaceMaterial.ShadeMat;
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

		/// <summary>True when an undug cell touches (8-way) a dug cell.</summary>
		private static bool BordersCut(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (n.InBounds(map) && eng.ExcavatedDepthAt(n) > 0)
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

		// ── scorch (principle 5, redone): vertex-colour char over the normal pit, no texture tiles ──

		private static readonly Color32 Char = new Color32(30, 21, 14, 0);
		private static readonly Color32 Ash = new Color32(132, 124, 114, 0);

		private static float Blotch(float x, float z)
		{
			// two octaves of world-space Perlin: patches a couple of cells across, never a repeat inside a pit
			return Mathf.Clamp01(0.65f * Mathf.PerlinNoise(x * 0.55f + 31.7f, z * 0.55f + 11.3f)
				+ 0.35f * Mathf.PerlinNoise(x * 1.7f + 5.1f, z * 1.7f + 77.9f));
		}

		/// <summary>The burned floor: a 6x6 vertex grid per cell, char alpha from world noise and wall distance, warm
		/// ash drifts where the noise is high, and a few pale ash flecks seeded per cell.</summary>
		private void CharFloor(IntVec3 c, int d, int north, int south, int west, int east, float hTop, float s, float y)
		{
			const int N = 6;
			bool wn = north < d, ws = south < d, ww = west < d, we = east < d;
			Color32[,] charC = new Color32[N + 1, N + 1];
			Color32[,] ashC = new Color32[N + 1, N + 1];
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
					float b = Blotch(x, z);
					Color32 k = Char;
					k.a = (byte)(255f * RM_WallFaceMath.FloorCharAlpha(s, b, dist));
					charC[i, j] = k;
					Color32 a = Ash;
					a.a = (byte)(255f * RM_WallFaceMath.AshDriftAlpha(s, b, dist));
					ashC[i, j] = a;
				}
			}
			Grid(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, hTop, N, charC, y);
			Grid(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, hTop, N, ashC, y + 0.0001f);
			// blackened patches (2026-10-06): near-black where the noise runs high — bits, never the whole floor
			Color32[,] blackC = new Color32[N + 1, N + 1];
			for (int i = 0; i <= N; i++)
			{
				for (int j = 0; j <= N; j++)
				{
					float b = Blotch(c.x + i / (float)N + 13.7f, c.z + j / (float)N * hTop + 4.1f);
					blackC[i, j] = new Color32(8, 7, 6, (byte)(255f * RM_WallFaceMath.BlackPatchAlpha(s, b)));
				}
			}
			Grid(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, hTop, N, blackC, y + 0.00005f);
			// a few pale ash flecks, seeded per cell (not a pattern)
			System.Random r = new System.Random(Gen.HashCombineInt(c.x * 7349, c.z * 2971));
			int flecks = r.Next(2);   // sparse and soft: dense pale dots read as rain/specks (owner, 2026-10-05)
			for (int k = 0; k < flecks; k++)
			{
				float fx = c.x + 0.12f + 0.76f * (float)r.NextDouble();
				float fz = c.z + 0.12f + (hTop - 0.24f) * (float)r.NextDouble();
				float sz = 0.025f + 0.03f * (float)r.NextDouble();
				Color32 fc = new Color32(150, 142, 132, (byte)(90f * s));
				QuadVMat(RM_FaceMaterial.ShadeMat, fx, fz, sz * 1.6f, sz, y + 0.0002f, fc, fc);
			}
		}

		/// <summary>Soot on a north face: darkest at the foot, a band at the rim, plus a few short irregular streaks
		/// climbing from the foot, seeded per cell.</summary>
		private void SootFace(IntVec3 c, float xl, float xr, float bot, float top, float s, float y)
		{
			const int R = 4;
			float h = top - bot;
			Color32[,] g = new Color32[2, R + 1];
			for (int j = 0; j <= R; j++)
			{
				Color32 k = new Color32(22, 15, 10, (byte)(255f * RM_WallFaceMath.FaceSootAlpha(s, j / (float)R)));
				g[0, j] = k;
				g[1, j] = k;
			}
			Grid(RM_FaceMaterial.ShadeMat, xl, bot, xr - xl, h, 1, g, y, R);
			System.Random r = new System.Random(Gen.HashCombineInt(c.x * 4271, c.z * 9157));
			int streaks = 1 + r.Next(3);
			for (int k = 0; k < streaks; k++)
			{
				float w = 0.02f + 0.04f * (float)r.NextDouble();
				float x = xl + (xr - xl - w) * (float)r.NextDouble();
				float len = h * (0.35f + 0.5f * (float)r.NextDouble());
				QuadVMat(RM_FaceMaterial.ShadeMat, x, bot, w, len, y + 0.0001f,
					new Color32(14, 10, 7, (byte)(170f * s)), new Color32(14, 10, 7, 0));
			}
		}

		/// <summary>The scorch ring on undug ground round a burned cut: soot fading out within 0.4 cell of the edge,
		/// broken up by the same world noise so it is irregular, never a hard rectangle.</summary>
		private void ScorchHalo(Map map, RM_PitScorch scorch, IntVec3 c, float y)
		{
			float sN = scorch.StrengthAt(c + IntVec3.North), sS = scorch.StrengthAt(c + IntVec3.South);
			float sW = scorch.StrengthAt(c + IntVec3.West), sE = scorch.StrengthAt(c + IntVec3.East);
			if (sN <= 0f && sS <= 0f && sW <= 0f && sE <= 0f)
			{
				return;
			}
			const int N = 6;
			const float W = 0.75f;   // 2026-10-06: was 0.4 — the ring read as nothing at play zoom
			Color32[,] g = new Color32[N + 1, N + 1];
			for (int i = 0; i <= N; i++)
			{
				for (int j = 0; j <= N; j++)
				{
					float lx = i / (float)N, lz = j / (float)N;
					float a = 0f;
					if (sN > 0f) a = Mathf.Max(a, sN * Mathf.Clamp01(1f - (1f - lz) / W));
					if (sS > 0f) a = Mathf.Max(a, sS * Mathf.Clamp01(1f - lz / W));
					if (sW > 0f) a = Mathf.Max(a, sW * Mathf.Clamp01(1f - lx / W));
					if (sE > 0f) a = Mathf.Max(a, sE * Mathf.Clamp01(1f - (1f - lx) / W));
					float b = Blotch(c.x + lx, c.z + lz);
					a *= 0.40f + 0.55f * b;
					Color32 k = Char;
					k.a = (byte)(255f * Mathf.Clamp01(a));
					g[i, j] = k;
				}
			}
			Grid(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, 1f, N, g, y);
			// a scorch splash thrown out of the burned cut onto the ground beside it, centred toward the cut
			if (RM_WallFaceMath.HasRimBlast(c.x, c.z))
			{
				float s = Mathf.Max(Mathf.Max(sN, sS), Mathf.Max(sW, sE));
				float cx = c.x + 0.5f + (sE > 0f ? 0.3f : sW > 0f ? -0.3f : 0f);
				float cz = c.z + 0.5f + (sN > 0f ? 0.3f : sS > 0f ? -0.3f : 0f);
				BlastMark(cx, cz, 0.5f, Gen.HashCombineInt(c.x * 17, c.z * 5), s, y + 0.0001f);
			}
		}

		/// <summary>A blast mark: a near-black core fading out along long and short spikes (a starburst), seeded so no
		/// two look alike. Owner, 2026-10-06: <i>"it needs blast marks and blackened bits."</i></summary>
		private void BlastMark(float cx, float cz, float radius, int seed, float s, float y)
		{
			float core = RM_WallFaceMath.BlastCoreAlpha(s);
			if (core <= 0f)
			{
				return;
			}
			int rays = 10 + (int)(RM_WallFaceMath.Hash01(seed, 1, 2) * 5f);
			float spin = RM_WallFaceMath.Hash01(seed, 3, 4) * Mathf.PI * 2f;
			LayerSubMesh sm = GetSubMesh(RM_FaceMaterial.ShadeMat);
			int b = sm.verts.Count;
			Color32 k = new Color32(10, 8, 7, (byte)(255f * core));
			sm.verts.Add(new Vector3(cx, y, cz));
			sm.uvs.Add(Vector3.zero);
			sm.colors.Add(k);
			// ring 1: the dark core (0.35 r), ring 2: the spike tips (alpha 0)
			int n = rays * 2;
			for (int i = 0; i < n; i++)
			{
				float ang = spin + i * Mathf.PI * 2f / n;   // x = sin, z = cos: rising angle runs clockwise, the winding Quad uses
				float len = RM_WallFaceMath.BlastRayLength(i, n, seed) * radius;
				float rc = Mathf.Min(len, radius * 0.35f);
				sm.verts.Add(new Vector3(cx + Mathf.Sin(ang) * rc, y, cz + Mathf.Cos(ang) * rc));
				sm.uvs.Add(Vector3.zero);
				sm.colors.Add(new Color32(10, 8, 7, (byte)(255f * core * 0.85f)));
				sm.verts.Add(new Vector3(cx + Mathf.Sin(ang) * len, y, cz + Mathf.Cos(ang) * len));
				sm.uvs.Add(Vector3.zero);
				sm.colors.Add(new Color32(10, 8, 7, 0));
			}
			for (int i = 0; i < n; i++)
			{
				int inner = b + 1 + i * 2, outer = inner + 1;
				int inner2 = b + 1 + ((i + 1) % n) * 2, outer2 = inner2 + 1;
				sm.tris.Add(b); sm.tris.Add(inner); sm.tris.Add(inner2);
				sm.tris.Add(inner); sm.tris.Add(outer); sm.tris.Add(outer2);
				sm.tris.Add(inner); sm.tris.Add(outer2); sm.tris.Add(inner2);
			}
		}

		/// <summary>FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 10 (owner, 2026-10-06: <i>"Is it possible to still show the pit
		/// walls/floor beneath the translucent water?"</i>). The liquid's terrain has replaced the cut's floor; for a
		/// liquid whose look is see-through, the cut's GEOMETRY is redrawn faintly over it — the floor (the ground it was
		/// dug through), the drowned band of the far wall and the drowned side walls, each lit like the dry pit's — then
		/// a thin wash of the liquid's colour over all of it, so they read as lying under the liquid and the water's own
		/// shimmer still shows through. Opaque liquids (seeThrough 0: tar, oil, slime, blood) draw nothing here.
		/// Live 2026-10-06, first cut: a flat floor quad plus a black depth quad at 0.55 alpha turned every water pit into
		/// a dark grey slab with no walls — so no darkening quad any more, lower alphas, walls drawn, a colour wash.</summary>
		private void SeeThrough(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, int f, int north, float y)
		{
			RM_LiquidSurfaceLook look = RM_LiquidSurface.LookFor(map.terrainGrid.TerrainAt(c));
			if (look == null || look.seeThrough <= 0f)
			{
				return;
			}
			float a = RM_LiquidLookMath.FloorSeeThroughAlpha(look.seeThrough, f);
			if (a <= 0f)
			{
				return;
			}
			TerrainDef ground = eng.OriginalTerrainAt(c);
			if (ground == null || ground.IsWater)
			{
				ground = TerrainDefOf.Soil;
			}
			int fullDrop = RM_WallFaceMath.ExposedDrop(d, north, 0);
			int dryDrop = RM_WallFaceMath.ExposedDrop(d, north, f);
			float hFull = RM_WallFaceMath.NorthFaceHeight(fullDrop);
			float hDry = RM_WallFaceMath.NorthFaceHeight(dryDrop);
			float floorTop = 1f - hFull;
			byte fa = (byte)(255f * a);
			Quad(RM_FaceMaterial.FaceMat(ground), c.x, c.z, 1f, floorTop, y, new Color32(255, 255, 255, fa), new Color32(255, 255, 255, fa), UvWorld);
			float drowned = hFull - hDry;
			if (drowned > 0.01f)
			{
				// the drowned band of the far wall: the wall's own ground, lit toward the water line like the dry face
				TerrainDef faceGround = RM_FaceMaterial.GroundBeside(map, eng, c, c + IntVec3.North, out bool _);
				byte b0 = (byte)(255f * RM_LiquidLookMath.DrownedFaceAlpha(look.seeThrough, f, 0f));
				byte b1 = (byte)(255f * RM_LiquidLookMath.DrownedFaceAlpha(look.seeThrough, f, 1f));
				Quad(RM_FaceMaterial.FaceMat(faceGround), c.x, c.z + floorTop, 1f, drowned, y + 0.0002f,
					new Color32(255, 255, 255, b0), new Color32(255, 255, 255, b1), UvFace);
				byte lit = (byte)(255f * LightAlpha(RM_WallFaceMath.WallFaceLight) * b1 / 255f);
				QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z + floorTop, 1f, drowned, y + 0.0003f,
					new Color32(255, 248, 232, 0), new Color32(255, 248, 232, lit));
				// the foot of the wall: a soft dark line where it meets the floor, so the corner reads
				byte foot = (byte)(120f * a);
				QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z + floorTop - 0.04f, 1f, 0.08f, y + 0.0003f,
					new Color32(0, 0, 0, 0), new Color32(0, 0, 0, foot));
			}
			// drowned side walls: a strip each side where the neighbour is shallower
			int west = NeighbourLevel(map, eng, c + IntVec3.West, d), east = NeighbourLevel(map, eng, c + IntVec3.East, d);
			float ww = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, west, 0));
			float ew = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, east, 0));
			byte sa = (byte)(255f * a * 0.8f);
			if (ww > 0f)
			{
				QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z, ww, floorTop, y + 0.0003f, new Color32(0, 0, 0, sa), new Color32(0, 0, 0, sa));
			}
			if (ew > 0f)
			{
				QuadVMat(RM_FaceMaterial.ShadeMat, c.x + 1f - ew, c.z, ew, floorTop, y + 0.0003f,
					new Color32(255, 248, 232, (byte)(sa / 2)), new Color32(255, 248, 232, (byte)(sa / 2)));
			}
			// the liquid's own colour washed thinly over everything drawn above, deeper = stronger
			Color wash = look.seeThroughTint.r >= 0.999f && look.seeThroughTint.g >= 0.999f && look.seeThroughTint.b >= 0.999f
				? new Color(0.30f, 0.46f, 0.58f) : look.seeThroughTint;
			byte wa = (byte)(255f * Mathf.Clamp01(0.16f + 0.07f * f));
			Color32 w = new Color32((byte)(255f * wash.r), (byte)(255f * wash.g), (byte)(255f * wash.b), wa);
			QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, 1f - hDry, y + 0.0005f, w, w);
		}

		/// <summary>An (nx x nz)-cell vertex grid over (x0,z0,w,h) with a colour per vertex; nz defaults to nx.</summary>
		private void Grid(Material mat, float x0, float z0, float w, float h, int nx, Color32[,] col, float y, int nz = -1)
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
					sm.verts.Add(new Vector3(x0 + w * i / nx, y, z0 + h * j / nz));
					sm.uvs.Add(Vector3.zero);
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

		/// <summary>A neighbour's floor level: dug depth; off-map or a natural liquid cell counts as level with
		/// this cell (no wall into a lake or the map edge).</summary>
		private static int NeighbourLevel(Map map, RM_MapComponent_Excavation eng, IntVec3 n, int myDepth)
		{
			if (!n.InBounds(map) || eng.IsSourceCell(n))
			{
				return myDepth;
			}
			return eng.ExcavatedDepthAt(n);
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
