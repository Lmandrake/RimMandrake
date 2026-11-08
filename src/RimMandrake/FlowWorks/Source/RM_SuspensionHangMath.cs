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
	}
}
