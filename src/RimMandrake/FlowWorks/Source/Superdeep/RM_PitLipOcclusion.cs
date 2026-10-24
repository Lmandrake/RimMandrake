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
	/// shallower than the pawn's floor. PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM: the SIDE banks hide too: in a column whose square
	/// beside the opening's row is shallower (a muffalo on a corner square reaching over the west rim), the part of the
	/// sprite below that bank's ground (RM_PitDrawMath.SideHiddenTop) is covered the same way; never past the far rim. Opacity is a Mod Setting (default 0.85: a faint ghost stays so a pawn at
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

		// PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE (owner walk 2026-10-23, the boar pit: "a strange square of bright terrain around it
		// as it moves"). The cover re-draws the bare ground above the pawn, so everything vanilla lays ON the ground under it is
		// lost; against a wall that is SectionLayer_EdgeShadows' darkening, and the cover read as a lit box sliding with the boar.
		// Each cover piece next to a shadow-casting edifice now carries the same shade (RM_WallFaceMath.EdgeShadeAt), drawn with
		// vanilla's own EdgeShadow material just after the cover. Meshes are pooled per frame (Graphics.DrawMesh renders later).
		private static Material edgeShadeMat;
		private readonly System.Collections.Generic.List<Mesh> shadeMeshes = new System.Collections.Generic.List<Mesh>();
		private int shadeUsed;
		private const float ShadeStep = 0.1f;

		/// <summary>PIT_SINK_FIX_SOIL_STRIP_OVER_WALL: a cell the near-lip cover must not paint ground over: it holds a drawn
		/// edifice (wall, door, fence...). A pit lid is excluded: the cover draws a lid square in the ground it prints.
		/// Cached once per component, no allocation per frame.</summary>
		private System.Func<int, int, bool> blocksCover;

		private System.Func<int, int, bool> BlocksCover => blocksCover ?? (blocksCover = (x, z) =>
		{
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map)) return false;
			Building ed = c.GetEdifice(map);
			return ed != null && !(ed is Pits.Building_PitCover);
		});

		private int EdgeCasters(IntVec3 g) => RM_WallFaceMath.ShadeCasters(o =>
		{
			IntVec3 c = new IntVec3(g.x + o.Item1, 0, g.z + o.Item2);
			if (!c.InBounds(map)) return false;
			Building ed = c.GetEdifice(map);
			return ed != null && ed.def.castEdgeShadows;
		});

		// PIT_COVER_FIX_DROPS_THE_SUN_SHADOW (save e C3: a lighter box under the boar between the lip and the wall). The cover also
		// hid SectionLayer_SunShadows: each edifice with staticSunShadowHeight h is swept by h x _CastVect.xz and tinted by
		// MatBases.SunShadow.color (SkyManager: lerp(white, sky shadow colour, shadow strength); a multiply, like EdgeShadow).
		// Each shade vertex in that sweep (RM_PitDrawMath.SunShadowedBy) takes the tint on top of its edge shade, so one
		// EdgeShadow-material mesh carries both shadows the cover hides. Read once per frame in MapComponentUpdate.
		private bool sunOn;
		private float sunVx, sunVz;
		private Color sunCol = Color.white;
		private static float sunHMax = -1f;

		private System.Func<int, int, float> sunHeightAt;

		private System.Func<int, int, float> SunHeightAt => sunHeightAt ?? (sunHeightAt = (x, z) =>
		{
			if (x < 0 || z < 0 || x >= map.Size.x || z >= map.Size.z) return 0f;
			Building ed = map.edificeGrid[new IntVec3(x, 0, z)];
			return ed != null ? ed.def.staticSunShadowHeight : 0f;
		});

		/// <summary>The tallest staticSunShadowHeight any def carries, so a shade vertex reads only the cells whose sweep can reach it.</summary>
		private static float SunHMax
		{
			get
			{
				if (sunHMax < 0f)
				{
					sunHMax = 0f;
					foreach (ThingDef td in DefDatabase<ThingDef>.AllDefs)
					{
						sunHMax = Mathf.Max(sunHMax, td.staticSunShadowHeight);
					}
				}
				return sunHMax;
			}
		}

		private void ReadSunShadow(bool shadowsDrawn)
		{
			sunOn = false;
			if (!shadowsDrawn || MatBases.SunShadow == null || MatBases.SunShadow.shader == null || !MatBases.SunShadow.shader.isSupported)
			{
				return;
			}
			Vector4 cv = Shader.GetGlobalVector(ShaderPropertyIDs.MapSunLightDirection);
			sunVx = cv.x;
			sunVz = cv.z;
			sunCol = MatBases.SunShadow.color;
			sunOn = SunHMax > 0f && (sunCol.r < 0.995f || sunCol.g < 0.995f || sunCol.b < 0.995f) && (sunVx != 0f || sunVz != 0f);
		}

		private readonly System.Collections.Generic.List<(int x, int z, float h)> sunCasters = new System.Collections.Generic.List<(int x, int z, float h)>();

		/// <summary>Gathers the casters whose sun shadow can reach a cover piece over [l,r]x[a,b] (RM_PitDrawMath.SunCasters);
		/// false when none can, so the piece needs no sun shade.</summary>
		private bool SunMayShade(float l, float r, float a, float b)
		{
			if (!sunOn) return false;
			RM_PitDrawMath.SunCasters(l, r, a, b, sunVx, sunVz, SunHMax, SunHeightAt, sunCasters);
			return sunCasters.Count > 0;
		}

		private void DrawEdgeShade(IntVec3 g, float l, float r, float a, float b, int casters, bool sun, float y)
		{
			if (edgeShadeMat == null)
			{
				if (MatBases.EdgeShadow == null) return;
				edgeShadeMat = new Material(MatBases.EdgeShadow) { renderQueue = RM_FaceMaterial.OccluderQueue + 1 };
			}
			int nx = Mathf.Max(1, Mathf.CeilToInt((r - l) / ShadeStep)), nz = Mathf.Max(1, Mathf.CeilToInt((b - a) / ShadeStep));
			int nv = (nx + 1) * (nz + 1);
			var verts = new Vector3[nv];
			var cols = new Color32[nv];
			bool any = false;
			for (int iz = 0; iz <= nz; iz++)
				for (int ix = 0; ix <= nx; ix++)
				{
					float x = l + (r - l) * ix / nx, z = a + (b - a) * iz / nz;
					float v = casters != 0 ? Mathf.Clamp01(RM_WallFaceMath.EdgeShadeAt(x - g.x, z - g.z, casters)) : 1f;
					Color col = new Color(v, v, v, 1f);
					if (sun && RM_PitDrawMath.SunShadowedBy(x, z, sunVx, sunVz, sunCasters))
					{
						col = new Color(v * sunCol.r, v * sunCol.g, v * sunCol.b, 1f);   // both multiply the ground: their product
					}
					if (col.r < 0.999f || col.g < 0.999f || col.b < 0.999f) any = true;
					int k = iz * (nx + 1) + ix;
					verts[k] = new Vector3(x, 0f, z);
					cols[k] = col;
				}
			if (!any) return;
			var tris = new int[nx * nz * 6];
			int t = 0;
			for (int iz = 0; iz < nz; iz++)
				for (int ix = 0; ix < nx; ix++)
				{
					int v0 = iz * (nx + 1) + ix, v1 = v0 + nx + 1;
					tris[t++] = v0; tris[t++] = v1; tris[t++] = v1 + 1;
					tris[t++] = v0; tris[t++] = v1 + 1; tris[t++] = v0 + 1;
				}
			if (shadeUsed >= shadeMeshes.Count) shadeMeshes.Add(new Mesh { name = "RM_PitLipEdgeShade" });
			Mesh m = shadeMeshes[shadeUsed++];
			m.Clear();
			m.vertices = verts;
			m.colors32 = cols;
			m.triangles = tris;
			Graphics.DrawMesh(m, Matrix4x4.TRS(new Vector3(0f, y, 0f), Quaternion.identity, Vector3.one), edgeShadeMat, 0);
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
		/// drawSize, never less than the body-size estimate; humanlikes keep the estimate's width. The estimate alone
		/// (sqrt(bodySize) x 1.2) under-reads big animals — a muffalo draws 3 cells wide against an estimated
		/// 1.86, so the cover stopped short of its flanks and showed as a hard-edged dirt rectangle across its
		/// middle (PIT_LIP_OCCLUDES_OUTSIDE_1). Over plain ground a wider cover is invisible: terrain materials
		/// are world-aligned, so the cover matches the ground it lies on. PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM: a humanlike's
		/// height is at least its body mesh's (the estimate left a colonist's feet showing below the cover).</summary>
		private static Vector2 HalfExtent(Pawn p)
		{
			float est = RM_PitDrawMath.BodyEstimateHalf(p.BodySize);
			Vector2 h = new Vector2(est, est);
			if (p.RaceProps != null && p.RaceProps.Humanlike)
			{
				h.y = RM_PitDrawMath.HumanlikeHalfHeight(p.BodySize);
			}
			else if (p.RaceProps != null)
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
			frameEng = eng;
			frameView = view;
			frameMesh = Quad(Mathf.Clamp01(RimMandrakeFlowWorksSettings.pitLipOcclusion));
			shadeUsed = 0;
			bool edgeShadows = DebugViewSettings.drawShadows && map.Biome?.disableShadows != true;
			frameEdgeShadows = edgeShadows;
			ReadSunShadow(edgeShadows);   // SectionLayer_SunShadows.Visible's test; its Regenerate also needs SunShadow.shader.isSupported
			frameY = AltitudeLayer.Pawn.AltitudeFor() + Altitudes.AltInc * 0.9f;
			rectsBuilt = false;
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
				bool hangs = bottom < p.Position.z;   // something hangs below the pawn's own cell: the near lip may hide it
				// PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM: what reaches over a west/east bank is below that bank's ground up to here
				float sideTop = RM_PitDrawMath.SideHiddenTop(bottom, top, d, RimMandrakeFlowWorksSettings.pitSinkPerLevel,
					RM_PitDrawMath.BodyHeightCells(p.BodySize));
				int pawnCol = Mathf.FloorToInt(dp.x);
				int x0 = Mathf.FloorToInt(dp.x - half);
				int x1 = Mathf.FloorToInt(dp.x + half);
				for (int cx = x0; cx <= x1; cx++)
				{
					float left = Mathf.Max(cx, dp.x - half);
					float right = Mathf.Min(cx + 1f, dp.x + half);
					if (right <= left)
					{
						continue;
					}
					float southTop = bottom;   // the side band starts above what the near lip already covers in this column
					IntVec3 lipCell = IntVec3.Invalid;
					for (int k = 1; hangs && k <= 3; k++)   // never the pawn's own row: the lip is SOUTH of it
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
					if (lipCell.IsValid)
					{
						float lipZ = lipCell.z + 1f;
						if (RM_WallFaceMath.OccludedBand(lipZ, bottom, top, out float z0, out float z1))
						{
							southTop = z1;
							// PIT_SINK_FIX_SOIL_STRIP_OVER_WALL: never re-draw the ground under a wall (or any drawn edifice) over it
							z0 = Mathf.Max(z0, RM_PitDrawMath.CoverStopZ(cx, lipZ, z0, BlocksCover));
							if (z1 > z0 + 0.001f)
							{
								DrawBand(p, d, cx, left, right, z0, z1, dp.x, -1, RimMandrakeFlowWorksSettings.pitLipOccupantCutEnabled
									&& RM_WallFaceMath.OccupantCutNeeded(lipZ, bottom, top));
							}
						}
					}
					// the side bank: only on ground beside the opening's rows (DrawBand tests each square), never under an edifice
					float sideLo = Mathf.Max(bottom, southTop);
					float sideHi = Mathf.Min(top, sideTop);
					if (sideHi > sideLo + 0.001f)
					{
						DrawBand(p, d, cx, left, right, sideLo, sideHi, dp.x, pawnCol, false);
					}
				}
			}
		}

		// one frame's drawing state, set at the top of MapComponentUpdate
		private RM_MapComponent_Excavation frameEng;
		private CellRect frameView;
		private Mesh frameMesh;
		private float frameY;
		private bool frameEdgeShadows;
		private bool rectsBuilt;

		private System.Func<int, int, int> seenDepth;

		/// <summary>The depth a square SHOWS on this map (frameEng), -1 off the map: RM_PitDrawMath.BesideOpening's lookup.</summary>
		private System.Func<int, int, int> SeenDepth => seenDepth ?? (seenDepth = (x, z) =>
		{
			IntVec3 c = new IntVec3(x, 0, z);
			return c.InBounds(map) && frameEng != null ? Pits.RM_SuspensionUnderpass.SeenDepthAt(map, frameEng, c) : -1;
		});

		/// <summary>Covers [left,right] x [z0,z1] of column <paramref name="cx"/> square by square, each piece in the ground it
		/// stands for, over the pawn at depth <paramref name="d"/>. <paramref name="sideOf"/> &gt;= 0: a side-bank band, drawn
		/// only on squares beside the opening in column sideOf (RM_PitDrawMath.BesideOpening) that hold no edifice.
		/// <paramref name="cut"/>: open the occupant window (near-lip band only).</summary>
		private void DrawBand(Pawn p, int d, int cx, float left, float right, float z0, float z1, float drawX, int sideOf, bool cut)
		{
			RM_MapComponent_Excavation eng = frameEng;
			for (int cz = Mathf.FloorToInt(z0); cz < Mathf.CeilToInt(z1); cz++)
			{
				IntVec3 g = new IntVec3(cx, 0, cz);
				if (!g.InBounds(map) || Pits.RM_SuspensionUnderpass.SeenDepthAt(map, eng, g) >= d)
				{
					continue;
				}
				if (sideOf >= 0 && (!RM_PitDrawMath.BesideOpening(cx, cz, sideOf, d, SeenDepth) || BlocksCover(cx, cz)))
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
					BuildFrameRects(eng, frameView.ExpandedBy(4));
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
				if (cut)
				{
					float cw = 0.5f * Mathf.Max(0.1f, RimMandrakeFlowWorksSettings.pitLipOccupantCutWidth);
					pieces = RM_WallFaceMath.CutCoverSpan(left, right, drawX - cw, drawX + cw, out l1, out r1, out l2, out r2);
				}
				// PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE: the ground's own edge shadow, which the cover (drawn above it) hid
				int casters = frameEdgeShadows ? EdgeCasters(g) : 0;
				for (int pc = 0; pc < pieces; pc++)
				{
					float pl = pc == 0 ? l1 : l2, pr = pc == 0 ? r1 : r2;
					Matrix4x4 m = Matrix4x4.TRS(new Vector3(pl, frameY, a), Quaternion.identity, new Vector3(pr - pl, 1f, b - a));
					Graphics.DrawMesh(frameMesh, m, mat, 0);
					bool sun = SunMayShade(pl, pr, a, b);
					if (casters != 0 || sun)
					{
						DrawEdgeShade(g, pl, pr, a, b, casters, sun, frameY + Altitudes.AltInc * 0.05f);
					}
				}
			}
		}
	}
}
