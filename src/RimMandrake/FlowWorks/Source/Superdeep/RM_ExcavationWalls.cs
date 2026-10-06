using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// EXCAVATION_WALL_ART_1 — the CARRIER for the wall-face art: a map section layer that draws the inner
	/// faces of every dug cut, Quarry-style (ruling 33: "walls with depth, not a flat tile with a lip shadow").
	/// Form chosen 2026-10-05 (FOUNDRY): a SectionLayer over the depth grid rather than per-depth terrain
	/// variants or a Thing overlay — faces depend on the NEIGHBOUR's depth too, which terrain cannot express,
	/// and a Thing per cell is what the collapse ruling deleted.
	///
	///   • NORTH face (the one the camera sees): a band across the top of the deeper cell, taller the bigger
	///     the drop, lit earth at the rim shading to dark earth at the foot (darker the deeper the cut).
	///   • EAST / WEST faces: narrow strips (west in shadow, east lit).
	///   • Liquid standing in the cut covers the foot of the faces (RM_WallFaceMath.ExposedDrop).
	///
	/// Art: until the commissioned textures exist this draws procedural vertex-colour gradients (placeholder,
	/// legible at every depth). When <c>Things/Building/FlowWorks/Excavation/RM_WallFace_North</c> /
	/// <c>_Side</c> exist they are used instead, UV-stretched over the same quads.
	/// Mod Setting: excavationWallFacesEnabled (off: dug cells show only their terrain).
	/// </summary>
	public class SectionLayer_RMExcavationWalls : SectionLayer
	{
		private static Material vertexMat;
		private static Material northTexMat;
		private static Material sideTexMat;
		private static bool texLooked;

		private static readonly Color32 Rim = new Color32(196, 164, 118, 235);
		private static readonly Color32 Earth = new Color32(122, 92, 62, 240);

		public const string NorthTexPath = "Things/Building/FlowWorks/Excavation/RM_WallFace_North";
		public const string SideTexPath = "Things/Building/FlowWorks/Excavation/RM_WallFace_Side";

		public SectionLayer_RMExcavationWalls(Section section) : base(section)
		{
			relevantChangeTypes = MapMeshFlagDefOf.Terrain;
		}

		public override bool Visible => DebugViewSettings.drawTerrain && RimMandrakeFlowWorksSettings.excavationWallFacesEnabled;

		private static void EnsureMaterials()
		{
			if (vertexMat == null)
			{
				vertexMat = MaterialPool.MatFrom(new MaterialRequest(BaseContent.WhiteTex, ShaderDatabase.VertexColor));
			}
			if (!texLooked)
			{
				texLooked = true;
				Texture2D n = ContentFinder<Texture2D>.Get(NorthTexPath, false);
				Texture2D s = ContentFinder<Texture2D>.Get(SideTexPath, false);
				if (n != null)
				{
					northTexMat = MaterialPool.MatFrom(new MaterialRequest(n, ShaderDatabase.Transparent));
				}
				if (s != null)
				{
					sideTexMat = MaterialPool.MatFrom(new MaterialRequest(s, ShaderDatabase.Transparent));
				}
			}
		}

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
			EnsureMaterials();
			float y = AltitudeLayer.TerrainScatter.AltitudeFor() + 0.003f;
			foreach (IntVec3 c in section.CellRect)
			{
				int d = eng.ExcavatedDepthAt(c);
				if (d == 0)
				{
					continue;
				}
				int f = eng.FillAt(c);
				int north = NeighbourLevel(map, eng, c + IntVec3.North, d);
				int west = NeighbourLevel(map, eng, c + IntVec3.West, d);
				int east = NeighbourLevel(map, eng, c + IntVec3.East, d);
				int nd = RM_WallFaceMath.ExposedDrop(d, north, f);
				if (nd > 0)
				{
					float h = RM_WallFaceMath.NorthFaceHeight(nd);
					Quad(c.x, c.z + 1f - h, 1f, h, y, Dark(d), Rim, northTexMat, true);
				}
				int wd = RM_WallFaceMath.ExposedDrop(d, west, f);
				if (wd > 0)
				{
					float w = RM_WallFaceMath.SideFaceWidth(wd);
					Color32 shade = Dark(d + 1);
					Quad(c.x, c.z, w, 1f, y + 0.001f, shade, shade, sideTexMat, false);
				}
				int ed = RM_WallFaceMath.ExposedDrop(d, east, f);
				if (ed > 0)
				{
					float w = RM_WallFaceMath.SideFaceWidth(ed);
					Quad(c.x + 1f - w, c.z, w, 1f, y + 0.001f, Earth, Earth, sideTexMat, false);
				}
			}
			FinalizeMesh(MeshParts.All);
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

		/// <summary>An axis-aligned quad from (x0,z0) of size (w,h); vertical gradient bottom→top, or the
		/// texture when one exists (stretched).</summary>
		private void Quad(float x0, float z0, float w, float h, float y, Color32 bottom, Color32 top, Material tex, bool vertical)
		{
			Material mat = tex ?? vertexMat;
			LayerSubMesh sm = GetSubMesh(mat);
			int n = sm.verts.Count;
			sm.verts.Add(new Vector3(x0, y, z0));
			sm.verts.Add(new Vector3(x0, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0));
			sm.uvs.Add(new Vector3(0f, 0f, 0f));
			sm.uvs.Add(new Vector3(0f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 0f, 0f));
			Color32 white = new Color32(255, 255, 255, 255);
			sm.colors.Add(tex != null ? white : bottom);
			sm.colors.Add(tex != null ? white : top);
			sm.colors.Add(tex != null ? white : top);
			sm.colors.Add(tex != null ? white : bottom);
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
