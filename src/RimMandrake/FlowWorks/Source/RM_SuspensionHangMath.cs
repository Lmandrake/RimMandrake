using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>SUSPENSION_BRIDGE_READS_HUNG: the numbers of a surface suspension bridge's hung look (deck sag, posts, the
	/// cables between them, the suspenders and the shadow on the hole's floor). Verse-free, self-tested
	/// (SelfTest/SuspensionHangChecks.cs). Positions run ALONG the span in cells from the first anchor's centre (index 0);
	/// a hung segment runs between two supports: an anchor's deck-facing edge (0.5 or length - 1.5) or a tower's centre.
	/// Offsets are in cells on screen; a positive sag is drawn that far SOUTH.</summary>
	public static class RM_SuspensionHangMath
	{
		/// <summary>Sag per cell of segment length, by tier (rope hangs most, the heavy steel deck least).</summary>
		public static float SagPerCell(SuspensionTier tier)
		{
			switch (tier)
			{
				case SuspensionTier.Rope: return 0.06f;
				case SuspensionTier.Timber: return 0.045f;
				case SuspensionTier.Steel: return 0.03f;
				default: return 0.025f;
			}
		}

		public const float MinMidSag = 0.18f, MaxMidSag = 0.8f;

		/// <summary>Mid-segment sag (cells) of a hung segment <paramref name="segLength"/> cells long: proportional to the
		/// length, never less than <see cref="MinMidSag"/> (so a short span still reads as hung at play zoom) nor more than
		/// <see cref="MaxMidSag"/> (so the longest span does not look broken).</summary>
		public static float MidSag(float segLength, SuspensionTier tier)
		{
			if (!(segLength > 0f))
			{
				return 0f;
			}
			float s = SagPerCell(tier) * segLength;
			return s < MinMidSag ? MinMidSag : s > MaxMidSag ? MaxMidSag : s;
		}

		/// <summary>The parabola 4u(1-u): 0 at both supports, 1 at mid-segment.</summary>
		public static float Bow(float u) => u <= 0f || u >= 1f ? 0f : 4f * u * (1f - u);

		/// <summary>Sag (cells south) of the deck at position <paramref name="along"/> between supports <paramref name="a0"/>
		/// and <paramref name="a1"/>; 0 outside the segment.</summary>
		public static float SagAt(float along, float a0, float a1, SuspensionTier tier)
		{
			float len = a1 - a0;
			if (!(len > 0f))
			{
				return 0f;
			}
			return MidSag(len, tier) * Bow((along - a0) / len);
		}

		/// <summary>Sag of the deck at <paramref name="along"/> for the sorted support positions <paramref name="supports"/>
		/// (anchor edges and tower centres): the segment holding the position decides; 0 off the hung length.</summary>
		public static float SagAt(float along, float[] supports, int count, SuspensionTier tier)
		{
			for (int k = 0; k + 1 < count; k++)
			{
				if (along >= supports[k] && along <= supports[k + 1])
				{
					return SagAt(along, supports[k], supports[k + 1], tier);
				}
			}
			return 0f;
		}

		/// <summary>Post height (cells drawn north of its foot) by tier: clearly taller than the deck.</summary>
		public static float PostHeight(SuspensionTier tier)
		{
			switch (tier)
			{
				case SuspensionTier.Rope: return 0.8f;
				case SuspensionTier.Timber: return 0.95f;
				case SuspensionTier.Steel: return 1.25f;
				default: return 1.4f;
			}
		}

		/// <summary>Post width (cells) by tier.</summary>
		public static float PostWidth(SuspensionTier tier) => tier == SuspensionTier.Heavy ? 0.2f : tier == SuspensionTier.Steel ? 0.18f : 0.14f;

		/// <summary>How far (cells north of the deck line) the main cable rides at mid-segment: low over the deck, never on it.</summary>
		public const float CableMidRise = 0.4f;

		/// <summary>The main cable's height above the (sagged) deck line at fraction <paramref name="u"/> of a segment: at the
		/// post tops at both supports, lowest at mid-segment. Add the deck's own sag to place it on screen.</summary>
		public static float CableRise(float u, SuspensionTier tier)
		{
			float top = PostHeight(tier);
			return top - (top - CableMidRise) * Bow(u);
		}

		/// <summary>Screen offset (cells, positive = north) of the main cable at <paramref name="along"/> in the segment
		/// [<paramref name="a0"/>, <paramref name="a1"/>]: the cable rides <see cref="CableRise"/> above the sagged deck.</summary>
		public static float CableNorth(float along, float a0, float a1, SuspensionTier tier)
		{
			float len = a1 - a0;
			if (!(len > 0f))
			{
				return 0f;
			}
			float u = (along - a0) / len;
			return CableRise(u, tier) - SagAt(along, a0, a1, tier);
		}

		public const float MaxSplay = 0.12f;

		/// <summary>How far (cells) the cables stand outboard of the deck's edge: the full splay at the posts, none at
		/// mid-segment, so a north-south span (whose sag runs along the screen's own north-south) still shows its hang.</summary>
		public static float Splay(float u) => MaxSplay * (1f - Bow(u));

		/// <summary>The shadow's offset (cells) east of the deck on the hole's floor for a drop of <paramref name="metres"/>.</summary>
		public static float ShadowEast(float metres) => metres <= 0f ? 0f : Math.Min(0.15f * metres, 0.6f);

		/// <summary>The three looks drawn for the owner's side-by-side (RM_SuspensionHang.SetTreatment): 0 suspension (posts,
		/// a main cable, suspenders), 1 rope walk (short posts, hand ropes that sag with the deck: hangs the most), 2
		/// cable-stayed (tall pylons, straight stays fanned to the deck: hangs the least).</summary>
		public const int TreatmentSuspension = 0, TreatmentRopeWalk = 1, TreatmentCableStayed = 2;

		/// <summary>How much more (or less) a treatment's deck sags than <see cref="MidSag"/>.</summary>
		public static float SagMultiplier(int treatment) => treatment == TreatmentRopeWalk ? 1.4f : treatment == TreatmentCableStayed ? 0.35f : 1f;

		/// <summary>The slope guard: a segment's mid sag is never more than this fraction of its length, so the steepest
		/// slope of the bow (4 x mid / length, at the supports) stays at or under 0.8 and the drawn deck never folds back on
		/// itself (a 1-cell rope walk at <see cref="MinMidSag"/> x 1.4 would slope 1.008).</summary>
		public const float SlopeGuard = 0.2f;

		/// <summary>The mid sag a treatment draws on a segment <paramref name="segLength"/> cells long: <see cref="MidSag"/> times
		/// <see cref="SagMultiplier"/>, held under <see cref="SlopeGuard"/> x length.</summary>
		public static float TreatedMidSag(float segLength, SuspensionTier tier, int treatment)
		{
			if (!(segLength > 0f))
			{
				return 0f;
			}
			float s = MidSag(segLength, tier) * SagMultiplier(treatment);
			float cap = SlopeGuard * segLength;
			return s > cap ? cap : s;
		}

		/// <summary>The steepest slope (cells of sag per cell along) of a bow with mid sag <paramref name="midSag"/> over
		/// <paramref name="segLength"/>: at the supports, 4 x mid / length.</summary>
		public static float MaxSlope(float midSag, float segLength) => segLength > 0f ? 4f * midSag / segLength : 0f;

		/// <summary>Sag at <paramref name="along"/> for sorted supports and each segment's own mid sag (segment k runs from
		/// supports[k] to supports[k + 1] and sags mids[k]); 0 off the hung length.</summary>
		public static float HungSagAt(float along, float[] supports, float[] mids, int count)
		{
			for (int k = 0; k + 1 < count; k++)
			{
				float a0 = supports[k], len = supports[k + 1] - a0;
				if (along >= a0 && along <= supports[k + 1] && len > 0f)
				{
					return mids[k] * Bow((along - a0) / len);
				}
			}
			return 0f;
		}

		/// <summary>The uv vanilla's Printer_Plane gives the point (<paramref name="dx"/>, <paramref name="dz"/>) cells from the
		/// centre of a 1x1 plane turned <paramref name="rotDeg"/>: the inverse of its turn (it turns local x, z by -rot), so a
		/// warped deck tile maps its texture exactly as the flat tile did.</summary>
		public static void PlaneUv(float dx, float dz, float rotDeg, out float u, out float v)
		{
			double num = -rotDeg * Math.PI / 180.0;
			float c = (float)Math.Cos(num), s = (float)Math.Sin(num);
			u = dx * c + dz * s + 0.5f;
			v = -dx * s + dz * c + 0.5f;
		}

		/// <summary>The offset (cells) from a deck square's centre of the point <paramref name="t"/> along the span (direction
		/// <paramref name="fx"/>, <paramref name="fz"/>) and <paramref name="q"/> across it (<paramref name="sx"/>,
		/// <paramref name="sz"/>), drawn <paramref name="sag"/> south.</summary>
		public static void StripPoint(int fx, int fz, int sx, int sz, float t, float q, float sag, out float dx, out float dz)
		{
			dx = fx * t + sx * q;
			dz = fz * t + sz * q - sag;
		}

		/// <summary>True when the triangle (t0, -across), (t0, +across), (t1, +across) of a strip along (fx, fz) and across
		/// (sx, sz) with t1 > t0 is clockwise seen from above (vanilla's plane winding); false means the strip's triangles
		/// are listed the other way round. A sag under the slope guard never changes it.</summary>
		public static bool StripClockwise(int fx, int fz, int sx, int sz) => sx * fz - sz * fx < 0;

		// ---- the supports and their posts (the anchors at both ends) ----

		/// <summary>The position along the span of the support at deck index <paramref name="index"/> (RM_SuspensionMath.Supports)
		/// of a span <paramref name="length"/> squares long with both anchors: the first anchor's deck-facing edge (0.5), the
		/// last anchor's (length - 1.5), a tower's centre.</summary>
		public static float SupportAlong(int index, int length) => index <= 0 ? 0.5f : index >= length - 1 ? length - 1.5f : index;

		/// <summary>The deck square that prints the post of the support at <paramref name="along"/>: the first and last deck
		/// squares (1 and length - 2) print the anchors' posts, a tower's own square its tower's.</summary>
		public static int PostOwner(float along, int length)
		{
			int i = (int)Math.Floor(along + 0.5f);
			return i < 1 ? 1 : i > length - 2 ? length - 2 : i;
		}

		/// <summary>Where along the span the post of support <paramref name="k"/> of <paramref name="count"/> stands: an anchor's
		/// just on the deck's end (inside its owner square, against the anchor), a tower's on its own square's middle.</summary>
		public static float PostFootAlong(int k, int count, float support, float postWidth)
			=> k == 0 ? support + 0.5f * postWidth : k == count - 1 ? support - 0.5f * postWidth : support;

		// ---- draw order (PAWN_WALKS_UNDER_DECK): the redrawn deck between the pawns beneath it and the pawns on it ----

		/// <summary>Below the Pawn layer's altitude: the deck redrawn over sunk pawns (above them at RM_WallFaceMath
		/// SunkAltitudeDrop plus their seed and render layers, and above the lip cover), its posts and cables a little higher,
		/// all under every pawn on the ground (seed at most one AltInc down).</summary>
		public const float OccluderDrop = 0.07f, PartsDrop = 0.055f, RailingAboveDeck = 0.004f;

		/// <summary>A sunken deck (DeckNotches > 0) has its walkers sunk like the floor's: its redraw and parts drop this much
		/// further, and the floor band beneath it is drawn this much lower again (RM_Patch_SuspensionHangDrawPos).</summary>
		public const float SunkenExtraDrop = 0.2f;

		/// <summary>A pawn drawn more than this below the Pawn layer is sunk (on a hole's floor); more than
		/// <see cref="DeepBelow"/> is the floor band under a sunken deck.</summary>
		public const float SunkBelow = 0.1f, DeepBelow = 0.3f;

		public static float OccluderY(float pawnAlt, bool sunkenDeck) => pawnAlt - OccluderDrop - (sunkenDeck ? SunkenExtraDrop : 0f);

		public static float PartsY(float pawnAlt, bool sunkenDeck) => pawnAlt - PartsDrop - (sunkenDeck ? SunkenExtraDrop : 0f);

		/// <summary>True when the deck is redrawn over a pawn drawn <paramref name="drop"/> below the Pawn layer whose sprite
		/// overlaps it: under a surface deck any sunk pawn (the hole's floor), under a sunken deck only the floor band dropped
		/// past its sunk walkers. A pawn on the deck is never covered.</summary>
		public static bool RedrawCovers(float drop, bool sunkenDeck) => sunkenDeck ? drop > DeepBelow : drop > SunkBelow;

		/// <summary>PAWN_WALKS_UNDER_DECK, front and behind: true when a pawn on the hole's floor whose undrawn centre is at world
		/// <paramref name="pawnZ"/> is beneath or north of the deck square whose south edge is at world
		/// <paramref name="squareSouthZ"/>, so the square is nearer the viewer and is drawn over it where their sprites overlap.
		/// The view looks north from the south and the sink draws depth as distance south, so a deck point drawn over a floor
		/// pixel lies south of that pixel's own square whenever the pixel is lower than the deck: a pawn wholly south of the square
		/// can only overlap it with parts standing above the deck, and those stay in front (its head as it walks out).</summary>
		public static bool DeckSquareInFront(float pawnZ, float squareSouthZ) => pawnZ > squareSouthZ;
	}
}
