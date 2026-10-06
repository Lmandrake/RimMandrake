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
				int nd = RM_WallFaceMath.ExposedDrop(d, north, f);
				int wd = RM_WallFaceMath.ExposedDrop(d, west, f);
				int ed = RM_WallFaceMath.ExposedDrop(d, east, f);
				float h = RM_WallFaceMath.NorthFaceHeight(nd);
				if (sc > 0f && f == 0)
				{
					// principle 5: the burned floor — ash and char under the faces
					Quad(RM_FaceMaterial.ScorchMat(true, sc), c.x, c.z, 1f, 1f - h, y - 0.0005f, White, White, UvWorld);
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
				if (nd > 0)
				{
					NorthFace(map, eng, c, d, h, y, sc);
				}
				if (wd > 0)
				{
					SideFace(map, eng, c, c + IntVec3.West, d, RM_WallFaceMath.SideFaceWidth(wd), h, false, y + 0.001f, sc);
				}
				if (ed > 0)
				{
					SideFace(map, eng, c, c + IntVec3.East, d, RM_WallFaceMath.SideFaceWidth(ed), h, true, y + 0.001f, sc);
				}
			}
			FinalizeMesh(MeshParts.All);
		}

		private void NorthFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, float h, float y, float scorch)
		{
			float z0 = c.z + 1f - h;
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, c + IntVec3.North, out bool stone);
			Material face = RM_FaceMaterial.FaceMat(ground);
			if (face != null)
			{
				Quad(face, c.x, z0, 1f, h, y, White, White, UvWorld);
			}
			// vanilla convention: a camera-facing face is the LIGHT tone; occluded toward the foot
			float top = RM_WallFaceMath.FaceTopLight - 1f;                 // > 0: lighten
			float foot = 1f - RM_WallFaceMath.FaceFootLight(d);            // > 0: darken
			Color32 topC = new Color32(255, 246, 226, (byte)(255f * Mathf.Clamp01(top * 0.6f)));
			Color32 footC = new Color32(0, 0, 0, (byte)(255f * Mathf.Clamp01(foot + 0.12f * d)));
			QuadVMat(RM_FaceMaterial.ShadeMat, c.x, z0, 1f, h, y + 0.0002f, footC, topC);
			// strata (dirt) or block joints (stone), face-local v so the pattern stands upright
			Quad(stone ? RM_FaceMaterial.JointMat : RM_FaceMaterial.StrataMat, c.x, z0, 1f, h, y + 0.0004f, White, White, UvFace);
			if (scorch > 0f)
			{
				Quad(RM_FaceMaterial.ScorchMat(false, scorch), c.x, z0, 1f, h, y + 0.0006f, White, White, UvFace);
				byte a = (byte)(255f * (1f - RM_WallFaceMath.ScorchDarken(scorch)) * 0.7f);
				QuadVMat(RM_FaceMaterial.ShadeMat, c.x, z0, 1f, h, y + 0.0007f, new Color32(8, 6, 5, a), new Color32(8, 6, 5, (byte)(a / 2)));
			}
			// dark rim line along the far edge, contact shadow at the foot
			float rim = Mathf.Min(RM_WallFaceMath.RimLine, h * 0.4f);
			QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z + 1f - rim, 1f, rim, y + 0.0008f, new Color32(10, 8, 6, 200), new Color32(10, 8, 6, 200));
			float cs = RM_WallFaceMath.ContactShadow;
			QuadVMat(RM_FaceMaterial.ShadeMat, c.x, z0 - cs, 1f, cs, y + 0.0008f, new Color32(0, 0, 0, 0), new Color32(0, 0, 0, 120));
		}

		private void SideFace(Map map, RM_MapComponent_Excavation eng, IntVec3 c, IntVec3 n, int d, float w, float northH, bool lit, float y, float scorch)
		{
			float x0 = lit ? c.x + 1f - w : c.x;
			float h = 1f - northH;   // the side face runs from the foot of the north face to the near lip
			if (h <= 0f)
			{
				return;
			}
			TerrainDef ground = RM_FaceMaterial.GroundBeside(map, eng, c, n, out bool stone);
			Material face = RM_FaceMaterial.FaceMat(ground);
			if (face != null)
			{
				Quad(face, x0, c.z, w, h, y, White, White, UvWorld);
			}
			Color32 tone = lit
				? new Color32(255, 246, 226, (byte)(255f * Mathf.Clamp01((RM_WallFaceMath.FaceTopLight - 1f) * 0.45f)))
				: new Color32(0, 0, 0, (byte)(255f * Mathf.Clamp01(0.40f + 0.05f * d)));
			QuadVMat(RM_FaceMaterial.ShadeMat, x0, c.z, w, h, y + 0.0002f, tone, tone);
			if (scorch > 0f)
			{
				byte a = (byte)(255f * (1f - RM_WallFaceMath.ScorchDarken(scorch)));
				QuadVMat(RM_FaceMaterial.ShadeMat, x0, c.z, w, h, y + 0.0007f, new Color32(8, 6, 5, a), new Color32(8, 6, 5, a));
			}
		}

		/// <summary>The scorch ring on undug ground round a burned cut: a soot gradient on the side touching it.</summary>
		private void ScorchHalo(Map map, RM_PitScorch scorch, IntVec3 c, float y)
		{
			const float W = 0.35f;
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[i];
				float s = scorch.StrengthAt(n);
				if (s <= 0f)
				{
					continue;
				}
				Color32 dark = new Color32(10, 8, 6, (byte)(150f * s));
				Color32 clear = new Color32(10, 8, 6, 0);
				IntVec3 dir = GenAdj.CardinalDirections[i];
				if (dir == IntVec3.North)
				{
					QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z + 1f - W, 1f, W, y, clear, dark);
				}
				else if (dir == IntVec3.South)
				{
					QuadVMat(RM_FaceMaterial.ShadeMat, c.x, c.z, 1f, W, y, dark, clear);
				}
				else if (dir == IntVec3.East)
				{
					QuadHMat(RM_FaceMaterial.ShadeMat, c.x + 1f - W, c.z, W, 1f, y, clear, dark);
				}
				else
				{
					QuadHMat(RM_FaceMaterial.ShadeMat, c.x, c.z, W, 1f, y, dark, clear);
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
