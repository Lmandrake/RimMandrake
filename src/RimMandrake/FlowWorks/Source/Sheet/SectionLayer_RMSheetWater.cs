using RimWorld;
using UnityEngine;
using Verse;
using static RimMandrake.FlowWorks.RM_SheetMath;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 1: the overlay picture of spilled water (design §6 item 2:
	/// overlay-first; no temp terrain is written, so no vanilla side effect fires from a picture). One translucent quad per
	/// wet square, its strength by tier (film, sheet, pool) and a pale ice tint for a frozen sheet (D10). PROVISIONAL look:
	/// plain tints, no art yet (a cosmetic pass needs the owner's permission and comes after Stage 4).
	/// Redrawn only on a tier change (the kernel's hysteresis bounds mesh churn) or a spill.</summary>
	public class SectionLayer_RMSheetWater : SectionLayer
	{
		private static Material film, sheet, pool, ice;

		public SectionLayer_RMSheetWater(Section section) : base(section)
		{
			relevantChangeTypes = MapMeshFlagDefOf.Terrain;
		}

		public override bool Visible => DebugViewSettings.drawTerrain;

		private static Material Mat(Tier t)
		{
			if (film == null)
			{
				film = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0.32f, 0.42f, 0.50f, 0.22f));
				sheet = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0.24f, 0.38f, 0.52f, 0.45f));
				pool = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0.17f, 0.31f, 0.47f, 0.62f));
				ice = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0.82f, 0.90f, 0.96f, 0.55f));
			}
			switch (t)
			{
				case Tier.Film: return film;
				case Tier.Sheet: return sheet;
				case Tier.Pool: return pool;
				case Tier.Ice: return ice;
				default: return null;
			}
		}

		public override void Regenerate()
		{
			ClearSubMeshes(MeshParts.All);
			RM_MapComponent_Sheet s = RM_MapComponent_Sheet.Of(Map);
			if (s == null || s.WetCells == 0)
			{
				FinalizeMesh(MeshParts.All);
				return;
			}
			float y = AltitudeLayer.TerrainScatter.AltitudeFor() + 0.002f;
			foreach (IntVec3 c in section.CellRect)
			{
				Material m = Mat(s.TierAt(c));
				if (m == null)
				{
					continue;
				}
				LayerSubMesh sm = GetSubMesh(m);
				int n = sm.verts.Count;
				sm.verts.Add(new Vector3(c.x, y, c.z));
				sm.verts.Add(new Vector3(c.x, y, c.z + 1));
				sm.verts.Add(new Vector3(c.x + 1, y, c.z + 1));
				sm.verts.Add(new Vector3(c.x + 1, y, c.z));
				sm.uvs.Add(new Vector3(0f, 0f, 0f));
				sm.uvs.Add(new Vector3(0f, 1f, 0f));
				sm.uvs.Add(new Vector3(1f, 1f, 0f));
				sm.uvs.Add(new Vector3(1f, 0f, 0f));
				for (int k = 0; k < 4; k++)
				{
					sm.colors.Add(new Color32(255, 255, 255, 255));
				}
				sm.tris.Add(n);
				sm.tris.Add(n + 1);
				sm.tris.Add(n + 2);
				sm.tris.Add(n);
				sm.tris.Add(n + 2);
				sm.tris.Add(n + 3);
			}
			FinalizeMesh(MeshParts.All);
		}
	}
}
