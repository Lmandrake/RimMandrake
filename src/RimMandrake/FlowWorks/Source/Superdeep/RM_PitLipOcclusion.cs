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
	/// Render only: it changes no sight, shot or cover (trench cover is RM_TrenchCover).
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

		/// <summary>Half the drawn sprite's width (x) and height (y), in cells. An animal's real body graphic
		/// drawSize, never less than the body-size estimate; humanlikes keep the estimate. The estimate alone
		/// (sqrt(bodySize) x 1.2) under-reads big animals — a muffalo draws 3 cells wide against an estimated
		/// 1.86, so the cover stopped short of its flanks and showed as a hard-edged dirt rectangle across its
		/// middle (PIT_LIP_OCCLUDES_OUTSIDE_1). Over plain ground a wider cover is invisible: terrain materials
		/// are world-aligned, so the cover matches the ground it lies on.</summary>
		private static Vector2 HalfExtent(Pawn p)
		{
			float est = 0.5f * Mathf.Clamp(Mathf.Sqrt(Mathf.Max(p.BodySize, 0.2f)) * 1.2f, 0.6f, 2.4f);
			Vector2 h = new Vector2(est, est);
			if (p.RaceProps != null && !p.RaceProps.Humanlike)
			{
				GraphicData g = p.ageTracker?.CurKindLifeStage?.bodyGraphicData;
				if (g != null)
				{
					h.x = Mathf.Max(h.x, 0.5f * g.drawSize.x);
					h.y = Mathf.Max(h.y, 0.5f * g.drawSize.y);
				}
			}
			// PIT_LIP_FIX_BOAR_HANGS_OUT: a lying pawn (asleep, downed, crawling) is drawn rotated by vanilla's BodyAngle,
			// so the cover spans the rotated sprite's box rather than the upright one.
			if (p.GetPosture() != PawnPosture.Standing && p.Drawer?.renderer != null)
			{
				RM_WallFaceMath.RotatedHalfExtent(h.x, h.y, p.Drawer.renderer.BodyAngle(PawnRenderFlags.None), out h.x, out h.y);
			}
			return h;
		}

		/// <summary>One frame's drawn rect and dug depth of a spawned, non-flying pawn near the view.</summary>
		private struct PawnRect
		{
			public Pawn pawn;
			public float l, r, bot, top;
			public int depth;
		}

		private readonly System.Collections.Generic.List<PawnRect> frameRects = new System.Collections.Generic.List<PawnRect>();

		/// <summary>Built at most once per MapComponentUpdate (and only when a cover piece is tested), so the patched
		/// DrawPos and HalfExtent run once per pawn per frame instead of once per pawn per cover piece.</summary>
		private void BuildFrameRects(RM_MapComponent_Excavation eng, CellRect near)
		{
			frameRects.Clear();
			foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
			{
				if (q.Flying || !near.Contains(q.Position))
				{
					continue;
				}
				Vector3 qp = q.DrawPos;
				Vector2 qh = HalfExtent(q);
				frameRects.Add(new PawnRect
				{
					pawn = q, l = qp.x - qh.x, r = qp.x + qh.x, bot = qp.z - qh.y, top = qp.z + qh.y,
					depth = Pits.RM_SuspensionUnderpass.DrawDepth(q, q.Position, eng.HollowDepthAt(q.Position))
				});
			}
		}

		private bool HitsShallowerPawn(Pawn sunk, int sunkDepth, float left, float right, float a, float b)
		{
			for (int i = 0; i < frameRects.Count; i++)
			{
				PawnRect q = frameRects[i];
				if (q.pawn == sunk)
				{
					continue;
				}
				if (RM_WallFaceMath.CoverPieceHitsShallowerPawn(left, right, a, b, q.l, q.r, q.bot, q.top, q.depth, sunkDepth))
				{
					return true;
				}
			}
			return false;
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
			bool rectsBuilt = false;
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.Flying || !view.Contains(p.Position))
				{
					continue;
				}
				// PIT_LID_FIX_VICKY_PEEKS_THROUGH: the depth the pawn is DRAWN at (a walker on a lid is at ground: no cover round
				// it); a pawn beneath a lid is not drawn, so nothing to cover
				int d = Pits.RM_SuspensionUnderpass.DrawDepth(p, p.Position, eng.HollowDepthAt(p.Position));
				if (d <= 0 || Pits.RM_PitCoverBeneath.IsBeneath(p))
				{
					continue;
				}
				// Stepping in or out (next cell at another depth): no cover. Position flips to the next cell at the START
				// of a step while the drawn pawn is still tweening across the lip, so a cover computed from either cell
				// sits on the wrong ground (owner's shots 2026-10-05: a brown block behind a pawn wading out, a darker
				// strip round one stepping into a deep filled pit). The sink itself still eases in and out.
				if (p.pather != null && p.pather.Moving && p.pather.nextCell.IsValid
					&& Pits.RM_SuspensionUnderpass.DrawDepth(p, p.pather.nextCell, eng.HollowDepthAt(p.pather.nextCell)) != d)
				{
					continue;
				}
				Vector3 dp = p.DrawPos;
				Vector2 ext = HalfExtent(p);
				float half = ext.x;
				float bottom = dp.z - ext.y;
				float top = dp.z + ext.y;
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
						if (Pits.RM_SuspensionUnderpass.SeenDepthAt(map, eng, cand) < d && !eng.IsSourceCell(cand))
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
						if (!g.InBounds(map) || Pits.RM_SuspensionUnderpass.SeenDepthAt(map, eng, g) >= d)
						{
							continue;
						}
						// a lid square is drawn in the ground the lid prints, not the pit floor under it
						Pits.Building_PitCover lid = eng.HollowDepthAt(g) > 0 ? Pits.RM_PitCoverUtility.CoverAt(map, g) : null;
						TerrainDef t = lid != null ? lid.PrintedSurface : map.terrainGrid.TerrainAt(g);
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
						if (!rectsBuilt)
						{
							// pawns a few cells beyond the view still count: a big sprite reaches into it
							BuildFrameRects(eng, view.ExpandedBy(4));
							rectsBuilt = true;
						}
						if (HitsShallowerPawn(p, d, left, right, a, b))
						{
							continue;   // never draw the cover over a pawn standing at ground level or on the lip
						}
						// FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1: a window through the cover at the occupant, but only where the lip would
						// hide more than half of it (PIT_LIP_FIX_BOAR_HANGS_OUT: with the sink clamp on, the part below the rim is hidden)
						float l1 = left, r1 = right, l2 = 0f, r2 = 0f;
						int pieces = 1;
						if (RimMandrakeFlowWorksSettings.pitLipOccupantCutEnabled && RM_WallFaceMath.OccupantCutNeeded(lipZ, bottom, top))
						{
							float cw = 0.5f * Mathf.Max(0.1f, RimMandrakeFlowWorksSettings.pitLipOccupantCutWidth);
							pieces = RM_WallFaceMath.CutCoverSpan(left, right, dp.x - cw, dp.x + cw, out l1, out r1, out l2, out r2);
						}
						for (int pc = 0; pc < pieces; pc++)
						{
							float pl = pc == 0 ? l1 : l2, pr = pc == 0 ? r1 : r2;
							Matrix4x4 m = Matrix4x4.TRS(new Vector3(pl, y, a), Quaternion.identity, new Vector3(pr - pl, 1f, b - a));
							Graphics.DrawMesh(mesh, m, mat, 0);
						}
					}
				}
			}
		}
	}
}
