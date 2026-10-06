using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_VISUAL_PRINCIPLES_1, principle 2 (owner, 2026-10-05): <i>"the walls should look like either dirt or
	/// stone, depending on the terrain beside them."</i>
	///
	/// DATA-DRIVEN, no per-biome table: a terrain is STONE when any natural-rock ThingDef names it (its
	/// <c>building.naturalTerrain</c>, that terrain's <c>smoothedTerrain</c>, or its <c>leaveTerrain</c>) — so every
	/// modded rock type that follows vanilla's shape is recognised automatically. A natural rock building standing
	/// beside the cut is stone too, drawn in that rock's own rough-floor terrain. Everything else (soil, sand, gravel,
	/// mud, ice …) is DIRT. The face is drawn with the ground's OWN terrain material, so it is that ground's exact
	/// texture and colour; this class only decides which terrain and which detail (strata vs block joints) to add.
	///
	/// Also owns the procedural strata/joint textures (generated, not art: nothing to install, nothing to queue)
	/// and the render-queue clones of terrain materials the faces and the near-lip occluder draw with.
	/// </summary>
	public static class RM_FaceMaterial
	{
		private static HashSet<TerrainDef> stoneTerrains;
		private static readonly Dictionary<Material, Material> faceClones = new Dictionary<Material, Material>();
		private static readonly Dictionary<Material, Material> occluderClones = new Dictionary<Material, Material>();

		/// <summary>Faces draw after every terrain (terrain queues are 2000 + renderPrecedence) and before
		/// cutout things (2450).</summary>
		public const int FaceQueue = 2440;
		public const int ShadeQueue = 2441;
		public const int DetailQueue = 2442;

		/// <summary>The occluder must draw AFTER pawns so it can cover the part of one hanging below the lip.</summary>
		public const int OccluderQueue = 3050;

		private static Texture2D strataTex, jointTex;
		private static Material strataMat, jointMat, shadeMat;

		public static bool IsStone(TerrainDef t)
		{
			if (t == null)
			{
				return false;
			}
			if (stoneTerrains == null)
			{
				stoneTerrains = new HashSet<TerrainDef>();
				foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
				{
					BuildingProperties b = d.building;
					if (b == null || !b.isNaturalRock)
					{
						continue;
					}
					if (b.naturalTerrain != null)
					{
						stoneTerrains.Add(b.naturalTerrain);
						if (b.naturalTerrain.smoothedTerrain != null)
						{
							stoneTerrains.Add(b.naturalTerrain.smoothedTerrain);
						}
					}
					if (b.leaveTerrain != null)
					{
						stoneTerrains.Add(b.leaveTerrain);
					}
				}
			}
			return stoneTerrains.Contains(t);
		}

		/// <summary>The ground a face beside cell <paramref name="self"/> is cut through, read from neighbour
		/// <paramref name="n"/>: a natural rock wall there (stone), the neighbour's own ground, or — when the
		/// neighbour is itself dug, built over, liquid or off the map — what the cell itself was dug through.</summary>
		public static TerrainDef GroundBeside(Map map, RM_MapComponent_Excavation eng, IntVec3 self, IntVec3 n, out bool stone)
		{
			TerrainDef t = null;
			if (n.InBounds(map))
			{
				Building ed = n.GetEdifice(map);
				if (ed != null && ed.def.building != null && ed.def.building.isNaturalRock && ed.def.building.naturalTerrain != null)
				{
					stone = true;
					return ed.def.building.naturalTerrain;
				}
				t = eng.ExcavatedDepthAt(n) > 0 ? eng.OriginalTerrainAt(n) : map.terrainGrid.BaseTerrainAt(n);
				if (t != null && (!t.natural || t.IsWater))
				{
					t = map.terrainGrid.UnderTerrainAt(n);
				}
			}
			if (t == null || !t.natural || t.IsWater)
			{
				t = eng.OriginalTerrainAt(self);
			}
			if (t == null || t.IsWater || t.DrawMatSingle == null)
			{
				t = TerrainDefOf.Soil;
			}
			stone = IsStone(t);
			return t;
		}

		/// <summary>The terrain's own material, cloned into the face queue so it draws over the cut's floor.</summary>
		public static Material FaceMat(TerrainDef t) => Clone(t, faceClones, FaceQueue);

		/// <summary>The terrain's own material, cloned into the occluder queue (after pawns).</summary>
		public static Material OccluderMat(TerrainDef t) => Clone(t, occluderClones, OccluderQueue);

		private static Material Clone(TerrainDef t, Dictionary<Material, Material> cache, int queue)
		{
			Material src = t?.DrawMatSingle;
			if (src == null)
			{
				return null;
			}
			if (!cache.TryGetValue(src, out Material m) || m == null)
			{
				m = new Material(src) { renderQueue = queue };
				cache[src] = m;
			}
			return m;
		}

		/// <summary>Alpha-blended vertex-colour material for the light/shadow gradients.</summary>
		public static Material ShadeMat
		{
			get
			{
				if (shadeMat == null)
				{
					shadeMat = new Material(MaterialPool.MatFrom(new MaterialRequest(BaseContent.WhiteTex, ShaderDatabase.VertexColor)))
					{
						renderQueue = ShadeQueue
					};
				}
				return shadeMat;
			}
		}

		public static Material StrataMat => strataMat ?? (strataMat = DetailMat(strataTex = MakeStrata()));
		public static Material JointMat => jointMat ?? (jointMat = DetailMat(jointTex = MakeJoints()));

		private static Material DetailMat(Texture2D tex)
		{
			Material m = new Material(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent)))
			{
				renderQueue = DetailQueue
			};
			m.mainTexture = tex;
			return m;
		}

		// ── procedural textures (deterministic seeds; dark marks on a transparent ground) ──

		private static Texture2D NewTex(int w, int h)
		{
			return new Texture2D(w, h, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Bilinear };
		}

		/// <summary>Earth strata: soft horizontal bands and pick marks, tiling.</summary>
		private static Texture2D MakeStrata()
		{
			Texture2D t = NewTex(64, 64);
			for (int y = 0; y < 64; y++)
			{
				float band = Mathf.Pow(Mathf.Sin(y / 64f * Mathf.PI * 6f), 2f);
				for (int x = 0; x < 64; x++)
				{
					float grain = Mathf.PerlinNoise(x * 0.31f + 3.1f, y * 0.9f + 7.7f);
					float a = 0.10f + 0.20f * band * grain;
					t.SetPixel(x, y, new Color(0.18f, 0.12f, 0.07f, a));
				}
			}
			t.Apply(false, true);
			return t;
		}

		/// <summary>Stone: block joints (horizontal courses, staggered vertical breaks) plus faint fracture grain.</summary>
		private static Texture2D MakeJoints()
		{
			Texture2D t = NewTex(64, 64);
			for (int y = 0; y < 64; y++)
			{
				int course = y / 16;
				for (int x = 0; x < 64; x++)
				{
					bool joint = (y % 16) < 2 || ((x + course * 21) % 40) < 2;
					float grain = Mathf.PerlinNoise(x * 0.2f + 1.3f, y * 0.2f + 5.1f);
					float a = joint ? 0.55f : 0.06f + 0.10f * grain;
					t.SetPixel(x, y, new Color(0.05f, 0.05f, 0.06f, a));
				}
			}
			t.Apply(false, true);
			return t;
		}
	}
}
