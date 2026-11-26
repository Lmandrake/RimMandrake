using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN (design/specs/2026-11-22-jetty-bridge-art/design.md §2,
	/// §3, §5): the owner's picked jetty and bridge art, on the ThingStyleDef of the deck (or jetty) in the look it was picked for.
	/// The deck draws one continuous strip cut into ROOT / MID / TIP / SOLO pieces (no seam between squares); the anchor at each
	/// end draws upright posts and taut cables (a jetty: post heads to its tip; a bridge: a sagging main cable with hangers).
	/// The numbers are the generated option's own geometry (art_source/JettyBridgeRedesign/gen_render.py spec_for), copied into
	/// RM_SuspensionStyles.xml; selftest_flowworks_deck_strips.py keeps the two equal. A style without this extension draws as before.
	/// </summary>
	public class RM_DeckArtExtension : DefModExtension
	{
		/// <summary>texPath base of the four pieces: base + "_root" / "_mid" / "_tip" / "_solo", drawn running east.</summary>
		public string strip;
		/// <summary>The upright post sprite (foot at the bottom), drawn rising north from its foot.</summary>
		public string post;
		/// <summary>The cable texture (runs left to right), tiled along each cable.</summary>
		public string cable;
		/// <summary>Deck width across, in cells (the painted deck inside its 1-cell piece).</summary>
		public float deckWidth = 0.8f;
		public float postHeight = 1.2f;
		public float postWidth = 0.09f;
		/// <summary>How far the posts stand outside the deck edge, and how far in from the anchor's deck-side edge.</summary>
		public float postOut = 0.09f;
		public float postInset = 0.16f;
		/// <summary>The main cable's drawn thickness (cells), the texture's own thickness included.</summary>
		public float cableThick = 0.06f;
		/// <summary>A jetty: 1 cable a side to the tip, or 2 (one to mid, one to the tip).</summary>
		public int fan = 1;
		/// <summary>A jetty: each cable doubled.</summary>
		public bool doubled;
		/// <summary>A bridge: the main cable's height at mid span (cells), hanger pitch (cells) and hanger thickness factor.</summary>
		public float sagLow = 0.22f;
		public float hangerPitch = 0.5f;
		public float hangerFactor = 0.45f;
		/// <summary>Where a backstay lands behind its post, as a share of the post's distance out from the centre line.</summary>
		public float backstayOut = 0.9f;
		/// <summary>Where a backstay lands behind the anchor square's centre (cells), and how high (a bollard's head).</summary>
		public float backstayBack = 0.42f;
		public float backstayFootH = 0.04f;
		/// <summary>RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: a railed square draws rope netting (diagonals this
		/// far apart, cells along the run) between the side rope and the hand rope, in place of the railing picture. 0: none.</summary>
		public float netPitch = 0f;
		/// <summary>A netting rope's thickness, as a share of cableThick.</summary>
		public float netFactor = 0.4f;
		/// <summary>RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: a beam bridge. Each anchor square draws this picture
		/// (drawn with the deck to its east, turned to face the deck; plus the lane suffix) in place of its bollards and ropes,
		/// and the ends draw no posts, cables or backstays. Null: an anchor draws as before.</summary>
		public string abutment;
		/// <summary>A bridge 2+ squares wide draws lane pieces (strip/abutment + LaneEdge's suffix) that carry only their own
		/// outer edge, so no curb or stringer runs down the middle of a wide deck.</summary>
		public bool laneEdges;
		/// <summary>A railed square draws timber posts this far apart along the run (cells), standing on the side line (deckWidth
		/// / 2), with a top rail at railHeight and knee braces landing braceOut outside it; the rail picture is cable. 0: none.</summary>
		public float railPitch = 0f;
		public float railHeight = 0.45f;
		public float railThick = 0.07f;
		public float braceOut = 0.1f;
	}

	/// <summary>The pure geometry of the picked art (no game state): which piece a deck square draws, how it is turned, and where
	/// the cables run. Mirrored in selftest_flowworks_deck_strips.py.</summary>
	public static class RM_DeckArtMath
	{
		public const string Root = "root", Mid = "mid", Tip = "tip", Solo = "solo";

		/// <summary>The piece of deck square k (0-based from the root) in a deck n squares long.</summary>
		public static string PieceAt(int k, int n)
		{
			if (n <= 1)
			{
				return Solo;
			}
			return k <= 0 ? Root : k >= n - 1 ? Tip : Mid;
		}

		/// <summary>The turn of a piece (drawn running east) for a deck running toward <paramref name="dir"/> (Rot4 int:
		/// 0 N, 1 E, 2 S, 3 W): east 0, south 90, west 180, north 270.</summary>
		public static float StripAngle(int dir)
		{
			return ((dir + 3) % 4) * 90f;
		}

		/// <summary>A bridge main cable's height at t (0 = one tower head, 1 = the other): a parabola from the head height down
		/// to <paramref name="low"/> at mid span.</summary>
		public static double CableHeight(double t, double head, double low)
		{
			return head - (head - low) * 4 * t * (1 - t);
		}

		/// <summary>Where the hangers hang, as t along the foot-to-foot span (n deck squares, posts inset by <paramref
		/// name="inset"/> into each anchor).</summary>
		public static List<double> HangerTs(int n, double pitch, double inset)
		{
			var ts = new List<double>();
			if (pitch <= 0)
			{
				return ts;
			}
			int m = (int)(n / pitch + 1e-6);
			for (int k = 1; k <= m; k++)
			{
				double t = (k * pitch + inset) / (n + 2 * inset);
				ts.Add(System.Math.Min(0.97, System.Math.Max(0.03, t)));
			}
			return ts;
		}

		/// <summary>The netting bays of deck square k (0-based from the root): pieces [s0, s1] of the run, in cells from the near
		/// anchor's deck-facing edge, <paramref name="pitch"/> long, covering the square exactly (the last one shorter).</summary>
		public static List<(double, double)> NetBays(int k, double pitch)
		{
			var bays = new List<(double, double)>();
			if (pitch <= 0)
			{
				return bays;
			}
			double s = k;
			while (s < k + 1 - 1e-6)
			{
				double e = System.Math.Min(k + 1, s + pitch);
				bays.Add((s, e));
				s = e;
			}
			return bays;
		}

		/// <summary>The picture suffix of a lane piece: "" on a 1-wide bridge; on a wider one "_top" for the lane on the left of
		/// the picture's run (it keeps the picture's top edge), "_bottom" for the right-most, "_open" between. A deck piece runs
		/// with the bridge (<paramref name="withRun"/> true): its left is lane 0 (Side is the clockwise turn of dir). An
		/// abutment faces its deck, so at the far end it runs against the bridge and the lanes swap.</summary>
		public static string LaneEdge(int lane, int width, bool withRun)
		{
			if (width <= 1)
			{
				return "";
			}
			int fromLeft = withRun ? lane : width - 1 - lane;
			return fromLeft <= 0 ? "_top" : fromLeft >= width - 1 ? "_bottom" : "_open";
		}

		/// <summary>Where the railing posts of deck square k (0-based from the root) stand, in cells from the near anchor's
		/// deck-facing edge: from k, <paramref name="pitch"/> apart, short of k + 1, plus k + 1 on the last square, so a post
		/// stands on every shared edge once and at both ends.</summary>
		public static List<double> RailPosts(int k, double pitch, bool last)
		{
			var ss = new List<double>();
			if (pitch <= 0)
			{
				return ss;
			}
			for (double s = k; s < k + 1 - 1e-6; s += pitch)
			{
				ss.Add(s);
			}
			if (last)
			{
				ss.Add(k + 1);
			}
			return ss;
		}

		/// <summary>A jetty's cable landing points, in cells out from the root anchor's edge, for a jetty n squares long.</summary>
		public static List<double> JettyTargets(int n, int fan)
		{
			if (fan <= 1 || n <= 1)
			{
				return new List<double> { n - 0.1 };
			}
			return new List<double> { n * 0.5, n - 0.1 };
		}
	}

	[StaticConstructorOnStartup]
	public static class RM_DeckArt
	{
		private static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();
		private static readonly Material Shade = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(0.04f, 0.03f, 0.02f, 0.32f));
		/// <summary>The sun offset of a height (cells east and south per cell of height), the generated scenes' SUN.</summary>
		private const float SunX = 0.42f, SunZ = -0.30f;
		/// <summary>Where a cable lands on the deck (cells above it), and a hanger's foot.</summary>
		private const float LandH = 0.02f, HangerFootH = 0.06f;

		private static Material Mat(string path)
		{
			if (path.NullOrEmpty())
			{
				return null;
			}
			if (!mats.TryGetValue(path, out Material m))
			{
				m = ContentFinder<Texture2D>.Get(path, false) != null ? MaterialPool.MatFrom(path, ShaderDatabase.Cutout) : null;
				mats[path] = m;
			}
			return m;
		}

		public static ThingDef DeckDefOf(SuspensionBridgeRecord r)
		{
			if (r == null)
			{
				return null;
			}
			if (r.jetty)
			{
				return DefDatabase<ThingDef>.GetNamedSilentFail(r.tier == SuspensionTier.Heavy ? "RM_SuspensionJetty_Heavy" : "RM_SuspensionJetty_Steel");
			}
			return RM_SuspensionDefOf.DeckOf(r.tier, r.grated);
		}

		/// <summary>The picked art of a bridge or jetty in its look, or null (no pick for this kind and look: draws as before).</summary>
		public static RM_DeckArtExtension For(SuspensionBridgeRecord r, ThingStyleDef own = null)
		{
			if (r == null || r.raidPlank || r.IsDrawbridge)
			{
				return null;
			}
			ThingDef def = DeckDefOf(r);
			ThingStyleDef s = own ?? RM_SuspensionLooks.StyleFor(def, RM_DrawbridgeArt.LookOf(r));
			// a deck def with no looks (the rope bridge) carries its art on the def itself
			return s?.GetModExtension<RM_DeckArtExtension>() ?? def?.GetModExtension<RM_DeckArtExtension>();
		}

		/// <summary>The deck indices of a record (a jetty: 1..length-1; a bridge: 1..length-2).</summary>
		public static int FirstDeck(SuspensionBridgeRecord r) => 1;

		public static int DeckCount(SuspensionBridgeRecord r) => r.LastDeck;

		/// <summary>Print a deck square as its strip piece. False when its bridge has no picked art (it draws as before).</summary>
		public static bool PrintDeck(SectionLayer layer, Building_SuspensionDeck deck, SuspensionBridgeRecord r)
		{
			Material m = DeckMat(deck, r, out float angle);
			if (m == null)
			{
				return false;
			}
			Printer_Plane.PrintPlane(layer, deck.TrueCenter(), Vector2.one, m, angle);
			return true;
		}

		/// <summary>The strip piece a deck square of a bridge with picked art prints, and its turn: the one chooser PrintDeck and
		/// the fade over a pawn beneath (Building_SuspensionDeck.FadeMaterial) share. Null when its bridge has no picked art.</summary>
		public static Material DeckMat(Building_SuspensionDeck deck, SuspensionBridgeRecord r, out float angle)
		{
			angle = 0f;
			if (r == null)
			{
				return null;
			}
			RM_DeckArtExtension x = For(r, deck.StyleDef);
			if (x == null || x.strip == null || !r.TryIndexOf(deck.Position, out int lane, out int i))
			{
				return null;
			}
			angle = RM_DeckArtMath.StripAngle(r.dir.AsInt);
			string path = x.strip + "_" + RM_DeckArtMath.PieceAt(i - FirstDeck(r), DeckCount(r));
			if (x.laneEdges)
			{
				string suffix = RM_DeckArtMath.LaneEdge(lane, r.width, true);
				Material lm = suffix.Length > 0 ? Mat(path + suffix) : null;
				if (lm != null)
				{
					return lm;
				}
			}
			return Mat(path);
		}

		/// <summary>Every deck square of the record is built and down (lane 0): the cables have something to hold.</summary>
		public static bool DeckComplete(Map map, SuspensionBridgeRecord r)
		{
			for (int i = FirstDeck(r); i <= r.LastDeck; i++)
			{
				IntVec3 c = r.Cell(0, i);
				if (!c.InBounds(map) || !(c.GetFirstThing<Building_SuspensionDeck>(map) is Building_SuspensionDeck d) || d.leafRaised)
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>A deck square came or went: its bridge's two ends re-print their cables, and its railed squares their
		/// netting (both wait for the whole deck: DeckComplete).</summary>
		public static void DirtyEnds(Map map, SuspensionBridgeRecord r)
		{
			if (map == null || r == null)
			{
				return;
			}
			var cells = new List<IntVec3> { r.Cell(0, 0), r.Cell(0, r.length - 1) };
			if (r.railings)
			{
				for (int lane = 0; lane < r.width; lane++)
				{
					for (int i = FirstDeck(r); i <= r.LastDeck; i++)
					{
						cells.Add(r.Cell(lane, i));
					}
				}
			}
			foreach (IntVec3 c in cells)
			{
				if (c.InBounds(map))
				{
					map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
				}
			}
		}

		/// <summary>The anchor at one end of a picked bridge or jetty (lane 0 prints for the whole width) prints its posts and
		/// cables. A jetty's root carries both; each bridge end prints its own half of the main cables and hangers.</summary>
		public static void PrintEnd(SectionLayer layer, Building_SuspensionAnchor anchor)
		{
			Map map = anchor.Map;
			SuspensionBridgeRecord r = map?.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(anchor.Position);
			if (r == null || !r.TryIndexOf(anchor.Position, out int lane, out int i) || lane != 0)
			{
				return;
			}
			bool near = i == 0, far = !r.jetty && i == r.length - 1;
			if (!near && !far)
			{
				return;
			}
			Building_SuspensionDeck first = r.Cell(0, 1).InBounds(map) ? r.Cell(0, 1).GetFirstThing<Building_SuspensionDeck>(map) : null;
			RM_DeckArtExtension x = For(r, first?.StyleDef);
			if (x == null || x.abutment != null)
			{
				return;   // a beam bridge's ends are its abutments (PrintAbutment): no posts, cables or backstays
			}
			Vector3 a = r.dir.FacingCell.ToVector3();          // along the deck, from the near end to the far end
			Vector3 f = near ? a : -a;                          // from this end toward the deck
			Vector3 side = r.Side.ToVector3();
			float across = (r.width - 1) * 0.5f;
			Vector3 c = r.Cell(0, i).ToVector3Shifted() + side * across;
			c.y = 0f;
			float sw = across + x.deckWidth * 0.5f;
			float off = sw + x.postOut;
			Vector3 foot = c + f * (0.5f - x.postInset);
			Vector3[] feet = { foot - side * off, foot + side * off };
			Material post = Mat(x.post);
			Material cable = Mat(x.cable);
			bool cables = cable != null && DeckComplete(map, r);
			float H = x.postHeight;
			// shadows first (on the ground and the deck, under every pawn)
			float shadowY = AltitudeLayer.Building.AltitudeFor() - Altitudes.AltInc;
			foreach (Vector3 p in feet)
			{
				Run(layer, Shade, p, 0f, p, H, x.postWidth, shadowY, true);
			}
			var runs = new List<(Vector3 p, float h, Vector3 q, float g, float w)>();
			Vector3 back = c - f * x.backstayBack;
			for (int s = 0; s < 2; s++)
			{
				float sg = s == 0 ? -1f : 1f;
				runs.Add((feet[s], H, back + side * (off * x.backstayOut * sg), x.backstayFootH, x.cableThick * 0.8f));   // backstay
			}
			if (cables)
			{
				if (r.jetty)
				{
					int n = DeckCount(r);
					Vector3 root = c + f * 0.5f;
					foreach (double L in RM_DeckArtMath.JettyTargets(n, x.fan))
					{
						for (int s = 0; s < 2; s++)
						{
							float sg = s == 0 ? -1f : 1f;
							Vector3 q = root + a * (float)L + side * (sw * 0.92f * sg);
							if (x.doubled)
							{
								foreach (float o in new[] { -0.35f, 0.35f })
								{
									Vector3 d = a * (o * x.cableThick);
									runs.Add((feet[s] - d, H, q - d, LandH, x.cableThick * 0.75f));
								}
							}
							else
							{
								runs.Add((feet[s], H, q, LandH, x.cableThick));
							}
						}
					}
				}
				else
				{
					int n = DeckCount(r);
					float span = n + 2 * x.postInset;
					Vector3 nearFoot = (near ? foot : foot - a * span);     // the near end's foot centre, whichever end prints
					const int K = 24;
					for (int s = 0; s < 2; s++)
					{
						float sg = s == 0 ? -1f : 1f;
						Vector3 pa = nearFoot + side * (off * sg);
						for (int k = 0; k < K; k++)
						{
							double t0 = (double)k / K, t1 = (double)(k + 1) / K;
							if ((t1 <= 0.5) != near)
							{
								continue;   // each end prints its own half
							}
							runs.Add((pa + a * (float)(span * t0), (float)RM_DeckArtMath.CableHeight(t0, H, x.sagLow),
								pa + a * (float)(span * t1), (float)RM_DeckArtMath.CableHeight(t1, H, x.sagLow), x.cableThick));
						}
						foreach (double t in RM_DeckArtMath.HangerTs(n, x.hangerPitch, x.postInset))
						{
							if ((t < 0.5) != near)
							{
								continue;
							}
							Vector3 p = pa + a * (float)(span * t);
							runs.Add((p, (float)RM_DeckArtMath.CableHeight(t, H, x.sagLow), p - side * (x.postOut * sg), HangerFootH,
								x.cableThick * x.hangerFactor));
						}
					}
				}
			}
			foreach (var run in runs)
			{
				Run(layer, Shade, run.p, run.h, run.q, run.g, run.w, shadowY, true);
			}
			// posts: upright, rising north from the foot, the northern one first so the southern one covers it
			if (post != null)
			{
				float pw = PostDrawWidth(post, H, x.postWidth);
				float postY = AltitudeLayer.BuildingOnTop.AltitudeFor();
				foreach (Vector3 p in feet[0].z >= feet[1].z ? feet : new[] { feet[1], feet[0] })
				{
					Vector3 at = p;
					at.z += H * 1.06f * 0.5f - 0.02f;
					at.y = postY;
					postY += Altitudes.AltInc * 0.1f;
					Printer_Plane.PrintPlane(layer, at, new Vector2(pw, H * 1.06f), post);
				}
			}
			// cables over pawns (design.md §3: PawnUnused, directly above Pawn)
			if (cable != null)
			{
				float cableY = AltitudeLayer.PawnUnused.AltitudeFor();
				foreach (var run in runs)
				{
					Run(layer, cable, run.p, run.h, run.q, run.g, run.w, cableY, false);
				}
			}
		}

		/// <summary>RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: an anchor square of a beam bridge (its art names an
		/// abutment) prints the abutment, the deck's end resting on a sill, turned to face its deck, in place of its own picture
		/// (bollards and ropes: "No ropes tied to the ground for the wood bridge"). False when its bridge has no abutment.</summary>
		public static bool PrintAbutment(SectionLayer layer, Thing anchor)
		{
			Material m = AbutmentMat(anchor, out float angle);
			if (m == null)
			{
				return false;
			}
			Vector3 c = anchor.Position.ToVector3Shifted();
			c.y = anchor.def.Altitude;
			Printer_Plane.PrintPlane(layer, c, Vector2.one, m, angle);
			return true;
		}

		/// <summary>The abutment picture an anchor square prints and its turn (facing its deck), or null (not a beam bridge's
		/// end): the one chooser PrintAbutment and the proof read share.</summary>
		public static Material AbutmentMat(Thing anchor, out float angle)
		{
			angle = 0f;
			Map map = anchor.Map;
			SuspensionBridgeRecord r = map?.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(anchor.Position);
			if (r == null || r.jetty || !r.TryIndexOf(anchor.Position, out int lane, out int i))
			{
				return null;
			}
			bool near = i == 0;
			if (!near && i != r.length - 1)
			{
				return null;
			}
			Building_SuspensionDeck first = r.Cell(0, 1).InBounds(map) ? r.Cell(0, 1).GetFirstThing<Building_SuspensionDeck>(map) : null;
			RM_DeckArtExtension x = For(r, first?.StyleDef);
			if (x?.abutment == null)
			{
				return null;
			}
			string suffix = x.laneEdges ? RM_DeckArtMath.LaneEdge(lane, r.width, near) : "";
			Material m = (suffix.Length > 0 ? Mat(x.abutment + suffix) : null) ?? Mat(x.abutment);
			Rot4 facing = near ? r.dir : r.dir.Opposite;
			angle = RM_DeckArtMath.StripAngle(facing.AsInt);
			return m;
		}

		/// <summary>RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS (his photo 14): a railed square of a beam bridge draws
		/// timber posts on its outer side line, a top rail and knee braces, each with its sun shadow; the railing picture is
		/// not drawn.</summary>
		private static void PrintTimberRail(SectionLayer layer, SuspensionBridgeRecord r, RM_DeckArtExtension x, Material beam, int lane, int i)
		{
			Vector3 a = r.dir.FacingCell.ToVector3();
			Vector3 side = r.Side.ToVector3();
			float across = (r.width - 1) * 0.5f;
			float sw = across + x.deckWidth * 0.5f;
			Vector3 edge = r.Cell(0, 0).ToVector3Shifted() + side * across + a * 0.5f;
			edge.y = 0f;
			int k = i - FirstDeck(r);
			bool last = i == r.LastDeck;
			float H = x.railHeight;
			var runs = new List<(Vector3 p, float h, Vector3 q, float g, float w)>();
			for (int sd = 0; sd < 2; sd++)
			{
				float sg = sd == 0 ? -1f : 1f;
				if ((sd == 0 && lane != 0) || (sd == 1 && lane != r.width - 1))
				{
					continue;   // an inner lane edge has no rail
				}
				Vector3 line = edge + side * (sw * sg);
				runs.Add((line + a * k, H, line + a * (k + 1), H, x.railThick));           // the top rail
				foreach (double s in RM_DeckArtMath.RailPosts(k, x.railPitch, last))
				{
					Vector3 p = line + a * (float)s;
					runs.Add((p, 0f, p, H + x.railThick * 0.5f, x.railThick));            // a post
					if (x.braceOut > 0f)
					{
						runs.Add((p + side * (x.braceOut * sg), 0f, p, H * 0.5f, x.railThick * 0.7f));   // a knee brace
					}
				}
			}
			float shadowY = AltitudeLayer.Building.AltitudeFor() - Altitudes.AltInc;
			float beamY = AltitudeLayer.PawnUnused.AltitudeFor();
			foreach (var run in runs)
			{
				Run(layer, Shade, run.p, run.h, run.q, run.g, run.w, shadowY, true);
			}
			foreach (var run in runs)
			{
				Run(layer, beam, run.p, run.h, run.q, run.g, run.w, beamY, false);
			}
		}

		/// <summary>RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: a railed square of a bridge whose art has netting
		/// draws rope netting on its two sides, diagonals between the side rope (on the deck) and the hand rope above it, with
		/// their shadows; the railing picture is not drawn. False when the bridge's art has no netting (draw the railing).</summary>
		public static bool PrintNetting(SectionLayer layer, Thing railing)
		{
			Map map = railing.Map;
			SuspensionBridgeRecord r = map?.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(railing.Position);
			if (r == null || r.jetty || !r.TryIndexOf(railing.Position, out int lane, out int i))
			{
				return false;
			}
			Building_SuspensionDeck deck = railing.Position.GetFirstThing<Building_SuspensionDeck>(map);
			RM_DeckArtExtension x = For(r, deck?.StyleDef);
			if (x != null && x.railPitch > 0f && Mat(x.cable) is Material beam)
			{
				PrintTimberRail(layer, r, x, beam, lane, i);
				return true;
			}
			if (x == null || x.netPitch <= 0f)
			{
				return false;
			}
			Material cable = Mat(x.cable);
			if (cable == null)
			{
				return false;   // no rope picture: the railing draws as before
			}
			if (!DeckComplete(map, r))
			{
				return true;    // the netting hangs from the hand rope, strung (PrintEnd) only once the whole deck is down
			}
			Vector3 a = r.dir.FacingCell.ToVector3();
			Vector3 side = r.Side.ToVector3();
			float across = (r.width - 1) * 0.5f;
			float sw = across + x.deckWidth * 0.5f;
			float off = sw + x.postOut;
			int n = DeckCount(r);
			float span = n + 2 * x.postInset;
			// the near anchor's deck-facing edge on the bridge's centre line; square i spans s in [i-1, i] from it
			Vector3 edge = r.Cell(0, 0).ToVector3Shifted() + side * across + a * 0.5f;
			edge.y = 0f;
			float w = x.cableThick * x.netFactor;
			float shadowY = AltitudeLayer.Building.AltitudeFor() - Altitudes.AltInc;
			float cableY = AltitudeLayer.PawnUnused.AltitudeFor();
			var runs = new List<(Vector3 p, float h, Vector3 q, float g)>();
			for (int sd = 0; sd < 2; sd++)
			{
				float sg = sd == 0 ? -1f : 1f;
				if ((sd == 0 && lane != 0) || (sd == 1 && lane != r.width - 1))
				{
					continue;   // an inner lane edge has no side rope
				}
				foreach ((double s0, double s1) in RM_DeckArtMath.NetBays(i - FirstDeck(r), x.netPitch))
				{
					float h0 = (float)RM_DeckArtMath.CableHeight((s0 + x.postInset) / span, x.postHeight, x.sagLow);
					float h1 = (float)RM_DeckArtMath.CableHeight((s1 + x.postInset) / span, x.postHeight, x.sagLow);
					Vector3 p0 = edge + a * (float)s0 + side * (sw * sg);
					Vector3 p1 = edge + a * (float)s1 + side * (sw * sg);
					Vector3 t0 = edge + a * (float)s0 + side * (off * sg);
					Vector3 t1 = edge + a * (float)s1 + side * (off * sg);
					runs.Add((p0, HangerFootH, t1, h1));   // rising diagonal
					runs.Add((t0, h0, p1, HangerFootH));   // falling diagonal
				}
			}
			foreach (var run in runs)
			{
				Run(layer, Shade, run.p, run.h, run.q, run.g, w, shadowY, true);
			}
			foreach (var run in runs)
			{
				Run(layer, cable, run.p, run.h, run.q, run.g, w, cableY, false);
			}
			return true;
		}

		/// <summary>The post sprite's drawn width: its own aspect at the drawn height, held between 1.1 and 1.9 post widths.</summary>
		private static float PostDrawWidth(Material m, float h, float w)
		{
			Texture t = m.mainTexture;
			float own = t == null || t.height == 0 ? w : h * 1.06f * t.width / t.height;
			return Mathf.Clamp(own, w * 1.1f, w * 1.9f);
		}

		private static readonly (float, float)[] Corners = { (-0.5f, -0.5f), (-0.5f, 0.5f), (0.5f, 0.5f), (0.5f, -0.5f) };

		/// <summary>One straight cable from ground point p at height h to q at height g, thickness w, printed at altitude y: on
		/// screen a point at height h is h cells north of its ground point; its shadow is the ground point moved by the sun.
		/// The texture (cable along u) is tiled in pieces of its own aspect length.</summary>
		private static void Run(SectionLayer layer, Material m, Vector3 p, float h, Vector3 q, float g, float w, float y, bool shadow)
		{
			Vector3 s = shadow ? new Vector3(p.x + SunX * h, y, p.z + SunZ * h) : new Vector3(p.x, y, p.z + h);
			Vector3 e = shadow ? new Vector3(q.x + SunX * g, y, q.z + SunZ * g) : new Vector3(q.x, y, q.z + g);
			Vector3 d = e - s;
			float len = new Vector2(d.x, d.z).magnitude;
			if (len < 1e-4f || w <= 0f)
			{
				return;
			}
			float rot = (float)RM_DrawbridgeCableMath.AngleOf(d.x, d.z);
			Texture t = m.mainTexture;
			float tile = shadow || t == null || t.height == 0 ? len : w * t.width / t.height;
			float done = 0f;
			while (done < len - 1e-4f)
			{
				float piece = Mathf.Min(tile, len - done);
				float u1 = piece / tile;
				Vector3 mid = s + d * ((done + piece * 0.5f) / len);
				var uvs = new Vector2[4];
				int k = 0;
				foreach ((float sx, float sz) in Corners)
				{
					uvs[k++] = new Vector2((sz + 0.5f) * u1, sx + 0.5f);
				}
				Printer_Plane.PrintPlane(layer, mid, new Vector2(w, piece), m, rot, false, uvs, null, 0f);
				done += piece;
			}
		}
	}
}
