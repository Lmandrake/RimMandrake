using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_VISUAL_PRINCIPLES_1, principle 1 — the NEAR lip hides what stands below it.
	///
	/// PIT_DEPTH_DRAW_OFFSET_1 draws a pawn on a dug cell D × sink cells further south (lower on screen). Seen from
	/// the south, the near (south) bank is in FRONT of anyone standing deep in the cut, so whatever part of the
	/// sprite hangs below that bank's edge must be hidden behind it — before this, nothing hid it and a sunk pawn
	/// simply overlapped the ground south of the pit.
	///
	/// Each frame, for every visible sunk pawn, this draws the near-lip ground (the lip cell's OWN terrain material,
	/// so it matches the ground exactly) over the band of the sprite below the lip, at a render queue after pawns.
	/// The lip is the north edge of the first cell south of the pawn, in each column the sprite spans, that is
	/// shallower than the pawn's floor. Opacity is a Mod Setting (default 0.85: a faint ghost stays so a pawn at
	/// D4 can still be found — assumption A2); where a terrain shader ignores vertex alpha the lip is simply opaque.
	/// Render only: LAW 2 (depth never touches sight, shooting or cover) is untouched.
	/// Known trade (recorded): an item or pawn standing on the lip cell inside that band is drawn under the lip too.
	/// </summary>
	public class RM_PitLipOcclusion : MapComponent
	{
		private static Mesh quad;
		private static float quadAlpha = -1f;

		public RM_PitLipOcclusion(Map map) : base(map)
		{
		}

		private static Mesh Quad(float alpha)
		{
			if (quad == null)
			{
				quad = new Mesh { name = "RM_PitLipQuad" };
				quad.vertices = new[] { new Vector3(0f, 0f, 0f), new Vector3(0f, 0f, 1f), new Vector3(1f, 0f, 1f), new Vector3(1f, 0f, 0f) };
				quad.uv = new[] { new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(1f, 0f) };
				quad.triangles = new[] { 0, 1, 2, 0, 2, 3 };
			}
			if (alpha != quadAlpha)
			{
				Color c = new Color(1f, 1f, 1f, alpha);
				quad.colors = new[] { c, c, c, c };
				quadAlpha = alpha;
			}
			return quad;
		}

		public override void MapComponentUpdate()
		{
			if (!RimMandrakeFlowWorksSettings.pitLipOcclusionEnabled || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled
				|| Find.CurrentMap != map || RimWorld.Planet.WorldRendererUtility.WorldRendered)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return;
			}
			CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(2);
			Mesh mesh = Quad(Mathf.Clamp01(RimMandrakeFlowWorksSettings.pitLipOcclusion));
			float y = AltitudeLayer.Pawn.AltitudeFor() + Altitudes.AltInc * 0.9f;
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.Flying || !view.Contains(p.Position))
				{
					continue;
				}
				int d = eng.ExcavatedDepthAt(p.Position);
				if (d <= 0)
				{
					continue;
				}
				// Stepping in or out (next cell at another depth): no cover. Position flips to the next cell at the START
				// of a step while the drawn pawn is still tweening across the lip, so a cover computed from either cell
				// sits on the wrong ground (owner's shots 2026-10-05: a brown block behind a pawn wading out, a darker
				// strip round one stepping into a deep filled pit). The sink itself still eases in and out.
				if (p.pather != null && p.pather.Moving && p.pather.nextCell.IsValid
					&& eng.ExcavatedDepthAt(p.pather.nextCell) != d)
				{
					continue;
				}
				Vector3 dp = p.DrawPos;
				float half = 0.5f * Mathf.Clamp(Mathf.Sqrt(Mathf.Max(p.BodySize, 0.2f)) * 1.2f, 0.6f, 2.4f);
				float bottom = dp.z - half;
				float top = dp.z + half;
				if (bottom >= p.Position.z)
				{
					continue;   // nothing hangs below the pawn's own cell
				}
				int x0 = Mathf.FloorToInt(dp.x - half);
				int x1 = Mathf.FloorToInt(dp.x + half);
				for (int cx = x0; cx <= x1; cx++)
				{
					IntVec3 lipCell = IntVec3.Invalid;
					for (int k = 1; k <= 3; k++)   // never the pawn's own row: the lip is SOUTH of it
					{
						IntVec3 cand = new IntVec3(cx, 0, p.Position.z - k);
						if (!cand.InBounds(map))
						{
							break;
						}
						if (eng.ExcavatedDepthAt(cand) < d && !eng.IsSourceCell(cand))
						{
							lipCell = cand;
							break;
						}
					}
					if (!lipCell.IsValid)
					{
						continue;
					}
					float lipZ = lipCell.z + 1f;
					if (!RM_WallFaceMath.OccludedBand(lipZ, bottom, top, out float z0, out float z1))
					{
						continue;
					}
					float left = Mathf.Max(cx, dp.x - half);
					float right = Mathf.Min(cx + 1f, dp.x + half);
					if (right <= left)
					{
						continue;
					}
					// cover cell by cell so each piece is drawn in the ground it stands for
					for (int cz = Mathf.FloorToInt(z0); cz < Mathf.CeilToInt(z1); cz++)
					{
						IntVec3 g = new IntVec3(cx, 0, cz);
						if (!g.InBounds(map) || eng.ExcavatedDepthAt(g) >= d)
						{
							continue;
						}
						TerrainDef t = map.terrainGrid.TerrainAt(g);
						if (t == null || t.IsWater)
						{
							continue;
						}
						Material mat = RM_FaceMaterial.OccluderMat(t);
						if (mat == null)
						{
							continue;
						}
						float a = Mathf.Max(z0, cz);
						float b = Mathf.Min(z1, cz + 1f);
						if (b <= a)
						{
							continue;
						}
						Matrix4x4 m = Matrix4x4.TRS(new Vector3(left, y, a), Quaternion.identity, new Vector3(right - left, 1f, b - a));
						Graphics.DrawMesh(mesh, m, mat, 0);
					}
				}
			}
		}
	}
}
