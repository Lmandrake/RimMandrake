// SUSPENSION_BRIDGE_READS_HUNG + PAWN_WALKS_UNDER_DECK (FlowWorks pits pass 7, 2026-11-08): the hung look, drawn.
// The numbers live in RM_SuspensionHangMath.cs (Verse-free, self-tested in SelfTest/SuspensionHangChecks.cs).
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>A surface suspension bridge drawn hung between its supports, not as a flat plank: every deck square (and its
	/// railing and ledge shadow) is printed as a strip warped south by the sag (RM_SuspensionHangMath.HungSagAt), posts
	/// stand at the supports with cables or ropes between them, and the deck's shadow lies on the hole's floor. A pawn on the
	/// floor beneath is drawn UNDER the deck: each frame the deck squares a sunk pawn's sprite overlaps are drawn again just
	/// above the sunk pawns and below everyone on the ground (DrawOccluders). Walkers on the deck are drawn lowered by the
	/// sag (RM_Patch_SuspensionHangDrawPos).
	/// Three looks for the owner's side-by-side, switched live (jawa/static_call):
	/// type=RimMandrake.FlowWorks.Pits.RM_SuspensionHang method=SetTreatment args=0|1|2 - 0 suspension (posts, a main cable from
	/// post top to post top, suspenders), 1 rope walk (short posts, a hand rope that follows the sagging deck, V ties: hangs
	/// most), 2 cable-stayed (tall pylons at the supports, straight stays to the deck: hangs least).
	/// Jetties, drawbridges, raid planks and spans under 3 squares stay flat (IsHung).</summary>
	public static class RM_SuspensionHang
	{
		/// <summary>The look being drawn (RM_SuspensionHangMath.Treatment*). Not saved: the side-by-side is a viewing aid.
		/// Default 0, suspension, the one that reads most hung: tall posts on both end squares mark the anchors, the main cable
		/// dips about a square on screen from post top to mid-span (timber over 9 squares: 0.55 of cable dip on 0.4 of deck
		/// sag) and the suspenders show the deck carried by it. The rope walk sags most but its knee-high hand rope reads as a
		/// railing; cable-stayed's straight stays and least sag read rigid.</summary>
		public static int Treatment = RM_SuspensionHangMath.TreatmentSuspension;

		/// <summary>Strips per deck square along the span (the bow drawn as this many straight pieces per square).</summary>
		public const int Steps = 4;

		/// <summary>The redrawn deck sits this far below a pawn's altitude: above the sunk pawns (P - 0.22 .. P - 0.107,
		/// RM_WallFaceMath.SunkAltitudeDrop) and the lip cover (P - 0.08), below anyone on the ground (P - 0.04 and up).
		/// The draw-order numbers live in RM_SuspensionHangMath (self-tested: Hang_deck_redraw_between_floor_and_deck_walkers).</summary>
		public const float OccluderDrop = RM_SuspensionHangMath.OccluderDrop;

		/// <summary>Posts and cables: just above the redrawn deck, still below anyone on the ground.</summary>
		public const float PartsDrop = RM_SuspensionHangMath.PartsDrop;

		/// <summary>A sunken deck (DeckNotches > 0) has its walkers sunk too; its redraw and parts drop this much further and
		/// the floor band beneath it drops past them (RM_Patch_SuspensionHangDrawPos).</summary>
		public const float SunkenExtraDrop = RM_SuspensionHangMath.SunkenExtraDrop;

		/// <summary>After the pit's lip cover (RM_FaceMaterial.OccluderQueue 3050), so a sunk pawn's pixels are painted over;
		/// the pawns on the ground keep theirs by altitude.</summary>
		public const int OccluderQueue = 3051, PartsQueue = 3052;

		/// <summary>The rope walk's hand rope: this high (cells north) over the sagging deck edge.</summary>
		public const float RopeRise = 0.35f;

		/// <summary>The cable-stayed pylon: this many times the tier's post height.</summary>
		public const float PylonScale = 1.6f;

		/// <summary>Most redrawn squares per frame (a crowd under a long bridge stays bounded).</summary>
		public const int MaxOccluderMeshes = 512;

		private static readonly Color32 White = new Color32(255, 255, 255, 255);

		/// <summary>Switches every hung span on every map to look <paramref name="which"/> (0 suspension, 1 rope walk,
		/// 2 cable-stayed) and redraws them. One int parameter, no overload: jawa/static_call coerces "args=1" to it.</summary>
		public static string SetTreatment(int which)
		{
			if (which < RM_SuspensionHangMath.TreatmentSuspension || which > RM_SuspensionHangMath.TreatmentCableStayed)
			{
				return "SetTreatment: want 0 (suspension), 1 (rope walk) or 2 (cable-stayed), got " + which;
			}
			int t = which;
			Treatment = t;
			int n = 0;
			List<Map> maps = Current.Game?.Maps;
			if (maps != null)
			{
				for (int m = 0; m < maps.Count; m++)
				{
					RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(maps[m]);
					if (comp == null)
					{
						continue;
					}
					IReadOnlyList<SuspensionBridgeRecord> bs = comp.Bridges;
					for (int b = 0; b < bs.Count; b++)
					{
						if (IsHung(bs[b]))
						{
							DirtySpan(maps[m], bs[b]);
							n++;
						}
					}
				}
			}
			return "hung bridge treatment " + t + " (" + TreatmentName(t) + "): " + n + " bridge(s) redrawn";
		}

		public static string TreatmentName(int t)
		{
			return t == RM_SuspensionHangMath.TreatmentRopeWalk ? "rope walk"
				: t == RM_SuspensionHangMath.TreatmentCableStayed ? "cable-stayed" : "suspension";
		}

		/// <summary>A record drawn hung: a two-ended bridge of at least one deck square that is not a drawbridge or a raid plank.</summary>
		public static bool IsHung(SuspensionBridgeRecord r)
		{
			return r != null && !r.jetty && !r.raidPlank && !r.IsDrawbridge && r.length >= 3 && r.width >= 1;
		}

		// ---- the shape: support positions and each segment's mid sag, rebuilt when the span, tier, towers or look change ----

		private sealed class ShapeData
		{
			public int stamp;
			public float[] supports;
			public float[] mids;
			public int count;
			public float maxSag;
		}

		private sealed class Shape
		{
			// swapped whole, so a reader on another thread never sees a half-built shape
			public volatile ShapeData data;
		}

		private static readonly ConditionalWeakTable<SuspensionBridgeRecord, Shape> Shapes = new ConditionalWeakTable<SuspensionBridgeRecord, Shape>();

		private static readonly ConditionalWeakTable<SuspensionBridgeRecord, Shape>.CreateValueCallback NewShape = _ => new Shape();

		private static int StampOf(SuspensionBridgeRecord r)
		{
			unchecked
			{
				int h = r.length * 397 + (int)r.tier;
				h = h * 31 + Treatment;
				List<int> t = r.towers;
				if (t != null)
				{
					for (int i = 0; i < t.Count; i++)
					{
						h = h * 31 + t[i] + 1;
					}
				}
				return h;
			}
		}

		private static ShapeData ShapeOf(SuspensionBridgeRecord r)
		{
			Shape s = Shapes.GetValue(r, NewShape);
			int stamp = StampOf(r);
			ShapeData d = s.data;
			if (d == null || d.stamp != stamp)
			{
				d = Build(r, stamp);
				s.data = d;
			}
			return d;
		}

		private static ShapeData Build(SuspensionBridgeRecord r, int stamp)
		{
			List<int> idx = RM_SuspensionMath.Supports(r.length, r.towers);
			int n = idx.Count;
			ShapeData d = new ShapeData { stamp = stamp, supports = new float[n], mids = new float[n], count = n };
			for (int k = 0; k < n; k++)
			{
				int i = idx[k];
				d.supports[k] = RM_SuspensionHangMath.SupportAlong(i, r.length);
			}
			for (int k = 0; k + 1 < n; k++)
			{
				d.mids[k] = RM_SuspensionHangMath.TreatedMidSag(d.supports[k + 1] - d.supports[k], r.tier, Treatment);
				if (d.mids[k] > d.maxSag)
				{
					d.maxSag = d.mids[k];
				}
			}
			return d;
		}

		/// <summary>Cells along the span from the first anchor's centre (index 0) of the world point <paramref name="p"/>.</summary>
		public static float AlongOf(SuspensionBridgeRecord r, Vector3 p)
		{
			IntVec3 f = r.dir.FacingCell;
			return (p.x - r.origin.x - 0.5f) * f.x + (p.z - r.origin.z - 0.5f) * f.z;
		}

		/// <summary>How far (cells) south the deck is drawn at <paramref name="along"/>; 0 for a record not drawn hung.</summary>
		public static float SagAt(SuspensionBridgeRecord r, float along)
		{
			if (!IsHung(r))
			{
				return 0f;
			}
			ShapeData d = ShapeOf(r);
			return RM_SuspensionHangMath.HungSagAt(along, d.supports, d.mids, d.count);
		}

		private static float Sag(ShapeData d, float along)
		{
			return RM_SuspensionHangMath.HungSagAt(along, d.supports, d.mids, d.count);
		}

		/// <summary>The world point <paramref name="along"/> the span, <paramref name="across"/> it (lane centres at 0, 1, ...),
		/// on the sagged deck line raised <paramref name="north"/> cells on screen.</summary>
		private static Vector3 At(SuspensionBridgeRecord r, ShapeData d, float along, float across, float north, float y)
		{
			IntVec3 f = r.dir.FacingCell, sd = r.Side;
			return new Vector3(r.origin.x + 0.5f + f.x * along + sd.x * across, y,
				r.origin.z + 0.5f + f.z * along + sd.z * across - Sag(d, along) + north);
		}

		// ---- the warped deck square ----

		/// <summary>Adds one deck square centred on <paramref name="center"/> as <see cref="Steps"/> strips bent by the sag,
		/// with the uv, top-edge altitude bias and winding vanilla's Printer_Plane gives a flat plane turned <paramref name="rot"/>.</summary>
		private static void Warp(List<Vector3> verts, List<Vector3> uvs, List<Color32> colors, List<int> tris,
			SuspensionBridgeRecord r, ShapeData d, Vector3 center, float rot, float bias)
		{
			IntVec3 f = r.dir.FacingCell, sd = r.Side;
			float along0 = AlongOf(r, center);
			int b = verts.Count;
			for (int k = 0; k <= Steps; k++)
			{
				float t = -0.5f + (float)k / Steps;
				float sag = Sag(d, along0 + t);
				for (int e = 0; e < 2; e++)
				{
					float q = e == 0 ? -0.5f : 0.5f;
					RM_SuspensionHangMath.StripPoint(f.x, f.z, sd.x, sd.z, t, q, 0f, out float dx, out float dz);
					RM_SuspensionHangMath.PlaneUv(dx, dz, rot, out float u, out float v);
					verts.Add(new Vector3(center.x + dx, center.y + bias * v, center.z + dz - sag));
					uvs.Add(new Vector3(u, v, 0f));
					colors.Add(White);
				}
			}
			bool cw = RM_SuspensionHangMath.StripClockwise(f.x, f.z, sd.x, sd.z);
			for (int k = 0; k < Steps; k++)
			{
				int i0 = b + 2 * k, i1 = i0 + 1, i2 = i0 + 3, i3 = i0 + 2;
				if (cw)
				{
					tris.Add(i0); tris.Add(i1); tris.Add(i2);
					tris.Add(i0); tris.Add(i2); tris.Add(i3);
				}
				else
				{
					tris.Add(i0); tris.Add(i2); tris.Add(i1);
					tris.Add(i0); tris.Add(i3); tris.Add(i2);
				}
			}
		}

		/// <summary>Prints <paramref name="mat"/> as one deck square of a hung record, warped by the sag. False (nothing
		/// printed) for a record not drawn hung: the caller prints its flat plane as before.</summary>
		public static bool PrintHungPlane(SectionLayer layer, Vector3 center, Material mat, float rot, SuspensionBridgeRecord r)
		{
			if (layer == null || mat == null || !IsHung(r))
			{
				return false;
			}
			LayerSubMesh sm = layer.GetSubMesh(mat);
			Warp(sm.verts, sm.uvs, sm.colors, sm.tris, r, ShapeOf(r), center, rot, 0.01f);
			return true;
		}

		// ---- posts, cables, ropes ----

		private static Material[] postMats, cableMats;

		private static int TierIndex(SuspensionTier t)
		{
			int i = (int)t;
			return i < 0 ? 0 : i > 3 ? 3 : i;
		}

		private static void EnsureMats()
		{
			if (postMats != null)
			{
				return;
			}
			Color[] post = { new Color(0.36f, 0.25f, 0.14f), new Color(0.33f, 0.22f, 0.12f), new Color(0.40f, 0.42f, 0.45f), new Color(0.33f, 0.34f, 0.36f) };
			Color[] cable = { new Color(0.70f, 0.58f, 0.36f), new Color(0.62f, 0.50f, 0.30f), new Color(0.24f, 0.25f, 0.27f), new Color(0.20f, 0.20f, 0.22f) };
			Material[] p = new Material[4], c = new Material[4];
			for (int t = 0; t < 4; t++)
			{
				p[t] = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.SolidColor, post[t], PartsQueue);
				c[t] = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.SolidColor, cable[t], PartsQueue);
			}
			cableMats = c;
			postMats = p;
		}

		/// <summary>A straight band <paramref name="w"/> cells wide from <paramref name="a"/> to <paramref name="b"/>, clockwise
		/// seen from above like vanilla's planes.</summary>
		private static void Line(LayerSubMesh sm, Vector3 a, Vector3 b, float w)
		{
			float dx = b.x - a.x, dz = b.z - a.z, len = Mathf.Sqrt(dx * dx + dz * dz);
			if (len < 1e-4f)
			{
				return;
			}
			float k = 0.5f * w / len, nx = -dz * k, nz = dx * k;
			int c = sm.verts.Count;
			sm.verts.Add(new Vector3(a.x - nx, a.y, a.z - nz));
			sm.verts.Add(new Vector3(a.x + nx, a.y, a.z + nz));
			sm.verts.Add(new Vector3(b.x + nx, b.y, b.z + nz));
			sm.verts.Add(new Vector3(b.x - nx, b.y, b.z - nz));
			sm.uvs.Add(new Vector3(0f, 0f, 0f));
			sm.uvs.Add(new Vector3(0f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 1f, 0f));
			sm.uvs.Add(new Vector3(1f, 0f, 0f));
			for (int i = 0; i < 4; i++)
			{
				sm.colors.Add(White);
			}
			sm.tris.Add(c); sm.tris.Add(c + 1); sm.tris.Add(c + 2);
			sm.tris.Add(c); sm.tris.Add(c + 2); sm.tris.Add(c + 3);
		}

		private static int SegmentOf(ShapeData d, float along)
		{
			for (int k = 0; k + 1 < d.count; k++)
			{
				if (along >= d.supports[k] && along <= d.supports[k + 1])
				{
					return k;
				}
			}
			return -1;
		}

		/// <summary>The main cable's point at <paramref name="along"/>: post top at the supports, lowest mid-segment, splayed
		/// outboard of the deck edge most at the posts.</summary>
		private static Vector3 CablePoint(SuspensionBridgeRecord r, ShapeData d, float along, float edge, float outward, float y)
		{
			int k = SegmentOf(d, along);
			float u = 0f;
			if (k >= 0)
			{
				float len = d.supports[k + 1] - d.supports[k];
				u = len > 0f ? (along - d.supports[k]) / len : 0f;
			}
			return At(r, d, along, edge + outward * RM_SuspensionHangMath.Splay(u), RM_SuspensionHangMath.CableRise(u, r.tier), y);
		}

		/// <summary>Prints the posts, cables or ropes a deck square carries: its outer edge(s) only, its own stretch of each
		/// cable, and the post of any support it owns (RM_SuspensionHangMath.PostOwner). Printed with the square, so they come and go with it.</summary>
		public static void PrintParts(SectionLayer layer, Building_SuspensionDeck deck)
		{
			SuspensionBridgeRecord r = deck?.Record;
			if (layer == null || !IsHung(r) || !r.TryIndexOf(deck.Position, out int lane, out int i) || i < 1 || i > r.length - 2)
			{
				return;
			}
			bool lo = lane == 0, hi = lane == r.width - 1;
			if (!lo && !hi)
			{
				return;
			}
			EnsureMats();
			ShapeData d = ShapeOf(r);
			int tier = TierIndex(r.tier);
			LayerSubMesh posts = layer.GetSubMesh(postMats[tier]);
			LayerSubMesh cables = layer.GetSubMesh(cableMats[tier]);
			float y = RM_SuspensionHangMath.PartsY(AltitudeLayer.Pawn.AltitudeFor(), r.deckNotches > 0);
			if (lo)
			{
				PrintSide(posts, cables, r, d, i, -0.5f, -1f, y);
			}
			if (hi)
			{
				PrintSide(posts, cables, r, d, i, r.width - 0.5f, 1f, y);
			}
		}

		private static void PrintSide(LayerSubMesh posts, LayerSubMesh cables, SuspensionBridgeRecord r, ShapeData d, int i,
			float edge, float outward, float y)
		{
			int tr = Treatment;
			float postH = RM_SuspensionHangMath.PostHeight(r.tier), postW = RM_SuspensionHangMath.PostWidth(r.tier);
			float top = tr == RM_SuspensionHangMath.TreatmentRopeWalk ? 0.5f * postH
				: tr == RM_SuspensionHangMath.TreatmentCableStayed ? PylonScale * postH : postH;
			float topSplay = tr == RM_SuspensionHangMath.TreatmentRopeWalk ? 0f : RM_SuspensionHangMath.MaxSplay;
			for (int k = 0; k < d.count; k++)
			{
				float p = d.supports[k];
				if (RM_SuspensionHangMath.PostOwner(p, r.length) != i)
				{
					continue;
				}
				// an anchor's post stands just on the deck's end, a tower's on its own square's middle
				float a = RM_SuspensionHangMath.PostFootAlong(k, d.count, p, postW);
				float w = tr == RM_SuspensionHangMath.TreatmentCableStayed ? 1.2f * postW : postW;
				Line(posts, At(r, d, a, edge, 0f, y), At(r, d, a, edge + outward * topSplay, top, y), w);
			}
			float lo = Mathf.Max(i - 0.5f, d.supports[0]), hi = Mathf.Min(i + 0.5f, d.supports[d.count - 1]);
			if (!(hi > lo))
			{
				return;
			}
			if (tr == RM_SuspensionHangMath.TreatmentCableStayed)
			{
				// one straight stay from the square's middle up to the nearest pylon top
				int best = -1;
				float bestD = float.MaxValue;
				for (int k = 0; k < d.count; k++)
				{
					float dd = Mathf.Abs(i - d.supports[k]);
					if (dd < bestD)
					{
						bestD = dd;
						best = k;
					}
				}
				if (best >= 0 && bestD >= 0.75f)
				{
					Line(cables, At(r, d, i, edge, 0f, y), At(r, d, d.supports[best], edge + outward * topSplay, top, y), 0.03f);
				}
				return;
			}
			if (tr == RM_SuspensionHangMath.TreatmentRopeWalk)
			{
				// a hand rope riding a fixed height over the sagging deck edge, tied down to it in V's
				for (int s = 0; s < Steps; s++)
				{
					float a0 = lo + (hi - lo) * s / Steps, a1 = lo + (hi - lo) * (s + 1) / Steps;
					Line(cables, At(r, d, a0, edge, RopeRise, y), At(r, d, a1, edge, RopeRise, y), 0.04f);
				}
				for (int v = 0; v < 2; v++)
				{
					float m = i - 0.25f + 0.5f * v;
					Line(cables, At(r, d, m - 0.25f, edge, RopeRise, y), At(r, d, m, edge, 0f, y), 0.02f);
					Line(cables, At(r, d, m, edge, 0f, y), At(r, d, m + 0.25f, edge, RopeRise, y), 0.02f);
				}
				return;
			}
			// suspension: the main cable from post top to post top over this square, and one suspender down to the deck
			for (int s = 0; s < Steps; s++)
			{
				float a0 = lo + (hi - lo) * s / Steps, a1 = lo + (hi - lo) * (s + 1) / Steps;
				Line(cables, CablePoint(r, d, a0, edge, outward, y), CablePoint(r, d, a1, edge, outward, y), 0.05f);
			}
			float near = float.MaxValue;
			for (int k = 0; k < d.count; k++)
			{
				near = Mathf.Min(near, Mathf.Abs(i - d.supports[k]));
			}
			if (near >= 0.25f)
			{
				Line(cables, At(r, d, i, edge, 0f, y), CablePoint(r, d, i, edge, outward, y), 0.025f);
			}
		}

		// ---- the shadow on the hole's floor ----

		private static Material shadowMat;

		private static Map shadowMap;

		private static RM_MapComponent_Excavation shadowEng;

		private static RM_MapComponent_Excavation ExcavationOf(Map map)
		{
			if (map != shadowMap)
			{
				shadowMap = map;
				shadowEng = map?.GetComponent<RM_MapComponent_Excavation>();
			}
			return shadowEng;
		}

		private static readonly float[] PolyAX = new float[16], PolyAZ = new float[16], PolyBX = new float[16], PolyBZ = new float[16];

		/// <summary>Prints the deck square's shadow on the floor below: its sagged outline moved south by the floor's sink (where
		/// a pawn standing there is drawn) and east by the drop (RM_SuspensionHangMath.ShadowEast), clipped to dug squares, at
		/// FloorCoverings: below the deck, so the deck itself hides the part of the shadow it covers.</summary>
		public static void PrintShadow(SectionLayer layer, Building_SuspensionDeck deck)
		{
			SuspensionBridgeRecord r = deck?.Record;
			Map map = deck?.Map;
			if (layer == null || map == null || !IsHung(r))
			{
				return;
			}
			RM_MapComponent_Excavation eng = ExcavationOf(map);
			if (eng == null)
			{
				return;
			}
			int hollow = eng.HollowDepthAt(deck.Position);
			int drop = hollow - r.deckNotches;
			if (hollow <= 0 || drop <= 0)
			{
				return;
			}
			float south = RM_PitDrawMath.SinkFor(hollow, RimMandrakeFlowWorksSettings.pitSinkPerLevel);
			float east = RM_SuspensionHangMath.ShadowEast(drop * RM_SpanMath.NotchM);
			if (!(south > 0.01f || east > 0.01f))
			{
				return;   // straight under the deck: all hidden
			}
			if (shadowMat == null)
			{
				shadowMat = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0f, 0f, 0f, 0.3f));
			}
			ShapeData d = ShapeOf(r);
			IntVec3 f = r.dir.FacingCell, sd = r.Side;
			Vector3 c = deck.Position.ToVector3Shifted();
			float along0 = AlongOf(r, c);
			float y = AltitudeLayer.FloorCoverings.AltitudeFor();
			LayerSubMesh sm = layer.GetSubMesh(shadowMat);
			for (int k = 0; k < Steps; k++)
			{
				float t0 = -0.5f + (float)k / Steps, t1 = t0 + 1f / Steps;
				float s0 = Sag(d, along0 + t0) + south, s1 = Sag(d, along0 + t1) + south;
				Corner(0, f, sd, c, t0, -0.5f, s0, east);
				Corner(1, f, sd, c, t0, 0.5f, s0, east);
				Corner(2, f, sd, c, t1, 0.5f, s1, east);
				Corner(3, f, sd, c, t1, -0.5f, s1, east);
				ClipToHoles(sm, map, eng, y);
			}
		}

		private static readonly float[] QuadX = new float[4], QuadZ = new float[4];

		private static void Corner(int n, IntVec3 f, IntVec3 sd, Vector3 c, float t, float q, float sag, float east)
		{
			RM_SuspensionHangMath.StripPoint(f.x, f.z, sd.x, sd.z, t, q, sag, out float dx, out float dz);
			QuadX[n] = c.x + dx + east;
			QuadZ[n] = c.z + dz;
		}

		private static void ClipToHoles(LayerSubMesh sm, Map map, RM_MapComponent_Excavation eng, float y)
		{
			float minX = QuadX[0], maxX = QuadX[0], minZ = QuadZ[0], maxZ = QuadZ[0];
			for (int n = 1; n < 4; n++)
			{
				minX = Mathf.Min(minX, QuadX[n]); maxX = Mathf.Max(maxX, QuadX[n]);
				minZ = Mathf.Min(minZ, QuadZ[n]); maxZ = Mathf.Max(maxZ, QuadZ[n]);
			}
			int gx0 = Mathf.FloorToInt(minX), gx1 = Mathf.FloorToInt(maxX - 1e-5f);
			int gz0 = Mathf.FloorToInt(minZ), gz1 = Mathf.FloorToInt(maxZ - 1e-5f);
			for (int gx = gx0; gx <= gx1; gx++)
			{
				for (int gz = gz0; gz <= gz1; gz++)
				{
					IntVec3 cell = new IntVec3(gx, 0, gz);
					if (!cell.InBounds(map) || eng.HollowDepthAt(cell) <= 0)
					{
						continue;
					}
					for (int n = 0; n < 4; n++)
					{
						PolyAX[n] = QuadX[n];
						PolyAZ[n] = QuadZ[n];
					}
					int m = ClipAxis(PolyAX, PolyAZ, 4, PolyBX, PolyBZ, true, gx, true);
					m = ClipAxis(PolyBX, PolyBZ, m, PolyAX, PolyAZ, true, gx + 1, false);
					m = ClipAxis(PolyAX, PolyAZ, m, PolyBX, PolyBZ, false, gz, true);
					m = ClipAxis(PolyBX, PolyBZ, m, PolyAX, PolyAZ, false, gz + 1, false);
					if (m >= 3)
					{
						Fan(sm, PolyAX, PolyAZ, m, y);
					}
				}
			}
		}

		/// <summary>One Sutherland-Hodgman pass: keeps the part of the polygon on one side of x (or z) = bound.</summary>
		private static int ClipAxis(float[] ix, float[] iz, int n, float[] ox, float[] oz, bool xAxis, float bound, bool keepAbove)
		{
			int m = 0;
			for (int a = 0; a < n && m < 15; a++)
			{
				int b = a + 1 == n ? 0 : a + 1;
				float va = (xAxis ? ix[a] : iz[a]) - bound, vb = (xAxis ? ix[b] : iz[b]) - bound;
				if (!keepAbove)
				{
					va = -va;
					vb = -vb;
				}
				bool ina = va >= 0f, inb = vb >= 0f;
				if (ina)
				{
					ox[m] = ix[a];
					oz[m] = iz[a];
					m++;
				}
				if (ina != inb)
				{
					float t = va / (va - vb);
					ox[m] = ix[a] + (ix[b] - ix[a]) * t;
					oz[m] = iz[a] + (iz[b] - iz[a]) * t;
					m++;
				}
			}
			return m;
		}

		private static void Fan(LayerSubMesh sm, float[] px, float[] pz, int n, float y)
		{
			float area = 0f;
			for (int a = 0; a < n; a++)
			{
				int b = a + 1 == n ? 0 : a + 1;
				area += px[a] * pz[b] - px[b] * pz[a];
			}
			if (Mathf.Abs(area) < 1e-6f)
			{
				return;
			}
			int c = sm.verts.Count;
			for (int a = 0; a < n; a++)
			{
				sm.verts.Add(new Vector3(px[a], y, pz[a]));
				sm.uvs.Add(new Vector3(0.5f, 0.5f, 0f));
				sm.colors.Add(White);
			}
			bool cw = area < 0f;
			for (int a = 1; a + 1 < n; a++)
			{
				sm.tris.Add(c);
				sm.tris.Add(cw ? c + a : c + a + 1);
				sm.tris.Add(cw ? c + a + 1 : c + a);
			}
		}

		/// <summary>Marks every square of a record for a redraw (a look switch, a square built or lost: the cables and the
		/// shadow of one square depend on the whole span).</summary>
		public static void DirtySpan(Map map, SuspensionBridgeRecord r)
		{
			if (map == null || r == null)
			{
				return;
			}
			for (int i = 0; i < r.length; i++)
			{
				for (int lane = 0; lane < r.width; lane++)
				{
					IntVec3 c = r.Cell(lane, i);
					if (c.InBounds(map))
					{
						map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
					}
				}
			}
		}

		// ---- the deck drawn over the pawns beneath it (each frame) ----

		private struct PawnBox
		{
			public float minX, maxX, minZ, maxZ;
			public bool deep;
		}

		private static PawnBox[] boxes = new PawnBox[16];

		private static int boxCount;

		private static readonly List<SuspensionBridgeRecord> InView = new List<SuspensionBridgeRecord>();

		private static readonly List<CellRect> InViewRects = new List<CellRect>();

		private static readonly List<Mesh> Pooled = new List<Mesh>();

		private static int pooledUsed;

		private static readonly List<Vector3> BufV = new List<Vector3>(), BufUV = new List<Vector3>();

		private static readonly List<Color32> BufC = new List<Color32>();

		private static readonly List<int> BufT = new List<int>();

		private static readonly Dictionary<Material, Material> Requeued = new Dictionary<Material, Material>();

		private static Material QueuedCopy(Material src, int queue)
		{
			if (!Requeued.TryGetValue(src, out Material m))
			{
				m = new Material(src) { renderQueue = queue, name = src.name + "_RMHang" + queue };
				Requeued[src] = m;
			}
			return m;
		}

		private static CellRect SpanRect(SuspensionBridgeRecord r)
		{
			return CellRect.FromLimits(r.Cell(0, 0), r.Cell(r.width - 1, r.length - 1));
		}

		/// <summary>Called from RM_MapComponent_SuspensionBridges.MapComponentUpdate (the world view already skipped). Cheap
		/// when nothing is beneath a deck: out at once with no dug square, no hung record in view or no sunk pawn near one.</summary>
		public static void DrawOccluders(Map map, IReadOnlyList<SuspensionBridgeRecord> bridges)
		{
			if (map == null || bridges == null || bridges.Count == 0)
			{
				return;
			}
			RM_MapComponent_Excavation eng = ExcavationOf(map);
			if (eng == null || eng.ClimbCellCount == 0)
			{
				return;   // nothing dug: nobody can be beneath a surface deck
			}
			CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(2);
			InView.Clear();
			InViewRects.Clear();
			for (int b = 0; b < bridges.Count; b++)
			{
				SuspensionBridgeRecord r = bridges[b];
				if (!IsHung(r))
				{
					continue;
				}
				CellRect rr = SpanRect(r).ExpandedBy(3);
				if (rr.Overlaps(view))
				{
					InView.Add(r);
					InViewRects.Add(rr);
				}
			}
			if (InView.Count == 0)
			{
				return;
			}
			float pawnAlt = AltitudeLayer.Pawn.AltitudeFor();
			boxCount = 0;
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int n = 0; n < pawns.Count; n++)
			{
				Pawn p = pawns[n];
				if (p == null || p.Flying)
				{
					continue;
				}
				IntVec3 pos = p.Position;
				if (!view.Contains(pos) || !NearInView(pos))
				{
					continue;
				}
				Vector3 dp = p.DrawPos;
				float drop = pawnAlt - dp.y;
				if (!RM_SuspensionHangMath.RedrawCovers(drop, false) || RM_PitCoverBeneath.IsBeneath(p))
				{
					continue;   // on the ground (or on the deck), or already hidden under a pit cover
				}
				Vector2 h = HalfExtent(p);
				if (boxCount == boxes.Length)
				{
					System.Array.Resize(ref boxes, boxes.Length * 2);
				}
				boxes[boxCount++] = new PawnBox
				{
					minX = dp.x - h.x, maxX = dp.x + h.x, minZ = dp.z - h.y, maxZ = dp.z + h.y,
					deep = RM_SuspensionHangMath.RedrawCovers(drop, true),
				};
			}
			if (boxCount == 0)
			{
				return;
			}
			pooledUsed = 0;
			for (int b = 0; b < InView.Count; b++)
			{
				DrawRecordOver(map, InView[b], pawnAlt);
			}
		}

		private static bool NearInView(IntVec3 c)
		{
			for (int i = 0; i < InViewRects.Count; i++)
			{
				if (InViewRects[i].Contains(c))
				{
					return true;
				}
			}
			return false;
		}

		private static bool AnyBox(float minX, float maxX, float minZ, float maxZ, bool deepOnly)
		{
			for (int i = 0; i < boxCount; i++)
			{
				PawnBox q = boxes[i];
				if ((!deepOnly || q.deep) && q.maxX > minX && q.minX < maxX && q.maxZ > minZ && q.minZ < maxZ)
				{
					return true;
				}
			}
			return false;
		}

		private static void DrawRecordOver(Map map, SuspensionBridgeRecord r, float pawnAlt)
		{
			ShapeData d = ShapeOf(r);
			bool sunken = r.deckNotches > 0;
			float y = RM_SuspensionHangMath.OccluderY(pawnAlt, sunken);
			for (int i = 1; i <= r.length - 2; i++)
			{
				for (int lane = 0; lane < r.width; lane++)
				{
					IntVec3 c = r.Cell(lane, i);
					if (!c.InBounds(map))
					{
						continue;
					}
					float cx = c.x + 0.5f, cz = c.z + 0.5f;
					// a sunken deck's walkers are sunk like the floor's: only the floor band (dropped further) goes under it
					if (!AnyBox(cx - 0.5f, cx + 0.5f, cz - 0.5f - d.maxSag, cz + 0.5f, sunken))
					{
						continue;
					}
					Building_SuspensionDeck deck = RM_MapComponent_SuspensionBridges.DeckAt(map, c);
					if (deck == null || deck.leafRaised)
					{
						continue;
					}
					Material src = RM_SuspensionDeckLink.TileFor(deck, out float angle);
					if (src == null)
					{
						continue;
					}
					Vector3 center = c.ToVector3Shifted();
					center.y = y;
					if (!DrawWarped(r, d, center, angle, QueuedCopy(src, OccluderQueue)))
					{
						return;
					}
					DrawRailingOver(map, r, d, c, y + RM_SuspensionHangMath.RailingAboveDeck);
				}
			}
		}

		private static void DrawRailingOver(Map map, SuspensionBridgeRecord r, ShapeData d, IntVec3 c, float y)
		{
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int t = 0; t < things.Count; t++)
			{
				Building_SuspensionRailing rail = things[t] as Building_SuspensionRailing;
				Material rm = rail?.Graphic?.MatSingle;
				if (rm == null)
				{
					continue;
				}
				Material q = QueuedCopy(rm, PartsQueue);
				Vector3 center = c.ToVector3Shifted();
				center.y = y;
				for (int e = 0; e < 4; e++)
				{
					Rot4 edge = new Rot4(e);
					if (RM_MapComponent_SuspensionBridges.HoldsBridgeEnd(map, c + edge.FacingCell))
					{
						continue;
					}
					if (!DrawWarped(r, d, center, edge.AsAngle, q))
					{
						return;
					}
				}
			}
		}

		private static bool DrawWarped(SuspensionBridgeRecord r, ShapeData d, Vector3 center, float rot, Material mat)
		{
			if (pooledUsed >= MaxOccluderMeshes)
			{
				return false;
			}
			if (pooledUsed == Pooled.Count)
			{
				Mesh nm = new Mesh { name = "RM_SuspensionHangOver" };
				nm.MarkDynamic();
				Pooled.Add(nm);
			}
			// one mesh per draw: Graphics.DrawMesh reads the mesh when the frame renders, not when it is called
			Mesh m = Pooled[pooledUsed++];
			BufV.Clear();
			BufUV.Clear();
			BufC.Clear();
			BufT.Clear();
			Warp(BufV, BufUV, BufC, BufT, r, d, center, rot, 0.01f);
			m.Clear();
			m.SetVertices(BufV);
			m.SetUVs(0, BufUV);
			m.SetColors(BufC);
			m.SetTriangles(BufT, 0);
			Graphics.DrawMesh(m, Matrix4x4.identity, mat, 0);
			return true;
		}

		/// <summary>The drawn half-size (cells) of a pawn's sprite. A copy of RM_PitLipOcclusion's (private, pinned there).</summary>
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
			if (p.GetPosture() != PawnPosture.Standing && p.Drawer?.renderer != null)
			{
				RM_WallFaceMath.RotatedHalfExtent(h.x, h.y, p.Drawer.renderer.BodyAngle(PawnRenderFlags.None), out h.x, out h.y);
			}
			return h;
		}
	}

	/// <summary>PAWN on a hung deck: drawn lowered by the deck's sag where it stands (along its tweened position, so a walk
	/// onto the deck runs smoothly down the bow). Runs after the pit sink (Priority.Low): the sink reads the unsagged
	/// position. A floor-band pawn (on the floor beneath the deck) keeps its sink; under a sunken deck it drops past the
	/// deck's walkers (RM_SuspensionHang.SunkenExtraDrop) so the redrawn deck covers it.</summary>
	[HarmonyPatch(typeof(Pawn_DrawTracker), nameof(Pawn_DrawTracker.DrawPos), MethodType.Getter)]
	[RimMandrake.Shared.PatchFeature("Suspension bridges hang between their supports")]
	public static class RM_Patch_SuspensionHangDrawPos
	{
		private static readonly AccessTools.FieldRef<Pawn_DrawTracker, Pawn> PawnRef =
			AccessTools.FieldRefAccess<Pawn_DrawTracker, Pawn>("pawn");

		private static Map cachedMap;

		private static RM_MapComponent_SuspensionBridges cachedComp;

		[HarmonyPostfix]
		[HarmonyPriority(Priority.Low)]
		public static void Postfix(Pawn_DrawTracker __instance, ref Vector3 __result)
		{
			if (RM_Patch_PitDepthDrawCombatOrigin.Firing > 0)
			{
				return;   // a verb is firing: shots leave from the undrawn position
			}
			Pawn p = PawnRef(__instance);
			if (p == null || !p.Spawned || p.Flying)
			{
				return;
			}
			Map map = p.Map;
			RM_MapComponent_SuspensionBridges comp = cachedComp;
			if (map != cachedMap)
			{
				comp = RM_MapComponent_SuspensionBridges.Of(map);
				cachedComp = comp;
				cachedMap = map;
			}
			if (comp == null || comp.Bridges.Count == 0)
			{
				return;
			}
			SuspensionBridgeRecord rec = comp.RecordAt(p.Position);
			if (!RM_SuspensionHang.IsHung(rec))
			{
				return;
			}
			if (RM_MapComponent_SuspensionBridges.BandTotal > 0 && comp.InBandSet(p))
			{
				if (rec.deckNotches > 0 && RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
				{
					__result.y -= RM_SuspensionHang.SunkenExtraDrop;
				}
				return;
			}
			__result.z -= RM_SuspensionHang.SagAt(rec, RM_SuspensionHang.AlongOf(rec, __instance.tweener.TweenedPos));
		}
	}
}
