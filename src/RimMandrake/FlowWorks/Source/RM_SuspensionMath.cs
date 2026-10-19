using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>The four suspension bridge types (design/RimMandrake/flowworks_bridges_design_2026-10-17.md §6.1).</summary>
	public enum SuspensionTier
	{
		Rope = 0,
		Timber = 1,
		Steel = 2,
		Heavy = 3,
	}

	/// <summary>What one square of a dragged suspension bridge stands over (the drag validator's input).</summary>
	public enum SpanGround
	{
		/// <summary>Solid surface ground an anchor can stand on: not dug, not water, no edifice.</summary>
		Ground = 0,
		/// <summary>A dug square at least 0.5 m deep with nothing in the way: a deck may cross it.</summary>
		Hole = 1,
		/// <summary>Neither: water, a wall, a building, fog, the map edge.</summary>
		Blocked = 2,
	}

	public enum SpanLoadState
	{
		Ok = 0,
		/// <summary>At 90% of the rating or more: the inspect pane warns and the bridge creaks.</summary>
		Sagging = 1,
		/// <summary>Over the rating: the whole span gives way.</summary>
		Over = 2,
	}

	/// <summary>
	/// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS (design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md §1.2-§1.3,
	/// §2, §4; parent design §6): the Verse-free rules of the surface suspension bridge. A bridge is dragged like a wall,
	/// 1 to 3 squares wide; each lane must start and end on solid ground (an anchor goes on each end) and every square between
	/// must be over a dug hole. The deck squares between two supports (the anchors, or a tower on the hole floor) form one
	/// SPAN: its length is capped per type, its load is summed together, and it gives way whole.
	///
	/// Numbers are the item's playtest starting points (length 8/6/10/14 squares between supports, load 150/600/2,000/8,000 kg
	/// per lane), never measurements. Compiled into the FlowWorks SelfTest (SuspensionBridgeChecks).
	/// </summary>
	public static class RM_SuspensionMath
	{
		public const int MaxWidth = 3;

		/// <summary>The sag warning (and creak) starts at this share of the rating.</summary>
		public const float SagFraction = 0.9f;

		/// <summary>Open-edge fall chances (construction design §2, proposals): a stagger or a blast on an edge square 25%,
		/// a slime slip on an edge square 10%. A railed square never drops anyone.</summary>
		public const float StaggerFallChance = 0.25f;
		public const float BlastFallChance = 0.25f;
		public const float SlimeFallChance = 0.10f;

		/// <summary>Railings cost this share of the deck square's own cost (design §2: +50%).</summary>
		public const float RailingCostShare = 0.5f;

		/// <summary>Ticks between two deck squares dropping when a bridge swings down from a lost anchor.</summary>
		public const int SwingTicksPerCell = 20;

		public const int AffordLight = 1;
		public const int AffordMedium = 2;
		public const int AffordHeavy = 4;

		/// <summary>Longest run of deck squares between two supports, by type (rope is longer than timber because rope bridges are).</summary>
		public static int BaseMaxLength(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return 8;
				case SuspensionTier.Timber: return 6;
				case SuspensionTier.Steel: return 10;
				default: return 14;
			}
		}

		/// <summary>Rated load of one lane of one span, kg.</summary>
		public static float BaseLoadKg(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return 150f;
				case SuspensionTier.Timber: return 600f;
				case SuspensionTier.Steel: return 2000f;
				default: return 8000f;
			}
		}

		/// <summary>The affordances a built deck lends to things built on it (timber Light; steel Light/Medium; heavy all three;
		/// rope none: walking only).</summary>
		public static int LentAffordances(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return 0;
				case SuspensionTier.Timber: return AffordLight;
				case SuspensionTier.Steel: return AffordLight | AffordMedium;
				default: return AffordLight | AffordMedium | AffordHeavy;
			}
		}

		public static string TierLabel(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return "rope";
				case SuspensionTier.Timber: return "timber";
				case SuspensionTier.Steel: return "steel";
				default: return "heavy";
			}
		}

		/// <summary>The length cap after the Mod Settings multiplier (0.5 to 3), never below one square.</summary>
		public static int MaxLength(SuspensionTier t, float lengthMultiplier)
		{
			int n = (int)(BaseMaxLength(t) * lengthMultiplier + 0.5f);
			return n < 1 ? 1 : n;
		}

		/// <summary>A span's rating: per-lane load × lanes × the Mod Settings load multiplier (0.25 to 4).</summary>
		public static float RatingKg(SuspensionTier t, int lanes, float loadMultiplier)
		{
			return BaseLoadKg(t) * (lanes < 1 ? 1 : lanes) * loadMultiplier;
		}

		public static SpanLoadState Classify(float loadKg, float ratingKg)
		{
			if (loadKg > ratingKg)
			{
				return SpanLoadState.Over;
			}
			return loadKg >= ratingKg * SagFraction ? SpanLoadState.Sagging : SpanLoadState.Ok;
		}

		/// <summary>"Load 640 / 600 kg" (the inspect pane line, verify row L2).</summary>
		public static string LoadLine(float loadKg, float ratingKg)
		{
			return "Load " + Kg(loadKg) + " / " + Kg(ratingKg) + " kg";
		}

		/// <summary>The P8 readout line: "Suspension bridge (timber) · deck at surface · load 210 / 600 kg".</summary>
		public static string ReadoutLine(SuspensionTier t, float loadKg, float ratingKg)
		{
			return "Suspension bridge (" + TierLabel(t) + ") · deck at surface · load " + Kg(loadKg) + " / " + Kg(ratingKg) + " kg";
		}

		private static string Kg(float kg)
		{
			return ((int)(kg + 0.5f)).ToString("#,0", System.Globalization.CultureInfo.InvariantCulture);
		}

		/// <summary>The chance an accident drops a pawn off a deck square: zero on a railed square or one with no open edge.</summary>
		public static float FallChance(float eventChance, bool railed, bool openEdge)
		{
			return railed || !openEdge ? 0f : eventChance;
		}

		/// <summary>The supports along one lane of length n (index 0 and n-1 are the anchors): the anchors plus every tower square.</summary>
		public static List<int> Supports(int n, ICollection<int> towers)
		{
			List<int> s = new List<int> { 0 };
			for (int i = 1; i < n - 1; i++)
			{
				if (towers != null && towers.Contains(i))
				{
					s.Add(i);
				}
			}
			if (n > 1)
			{
				s.Add(n - 1);
			}
			return s;
		}

		/// <summary>Which span (0-based, from the first anchor) the deck square at index i belongs to. A tower square belongs to
		/// the span before it.</summary>
		public static int SegmentOf(int i, List<int> supports)
		{
			for (int k = 1; k < supports.Count; k++)
			{
				if (i <= supports[k])
				{
					return k - 1;
				}
			}
			return supports.Count - 2;
		}

		/// <summary>The deck indices of span k: from just after its first support through its last square (a tower square at
		/// the far end included; the anchor excluded).</summary>
		public static List<int> SegmentCells(int k, List<int> supports, int n)
		{
			List<int> cells = new List<int>();
			int from = supports[k] + 1;
			int to = supports[k + 1] == n - 1 ? n - 2 : supports[k + 1];
			for (int i = from; i <= to; i++)
			{
				cells.Add(i);
			}
			return cells;
		}

		/// <summary>The order the squares of a span drop in when it swings down: from the lost end toward the kept one.</summary>
		public static List<int> SwingOrder(List<int> segmentCells, bool lostAtLowEnd)
		{
			List<int> order = new List<int>(segmentCells);
			order.Sort();
			if (!lostAtLowEnd)
			{
				order.Reverse();
			}
			return order;
		}

		/// <summary>One lane of a drag, from one end to the other. Null = it can be built; otherwise the refusal, in the
		/// player's words. towers: indices along the lane where a tower stands or is planned (a support in the middle).</summary>
		public static string ValidateLane(IList<SpanGround> lane, ICollection<int> towers, SuspensionTier tier, float lengthMultiplier)
		{
			int n = lane.Count;
			if (n < 3)
			{
				return "Drag a suspension bridge from solid ground, across a dug hole, to solid ground on the far side.";
			}
			if (lane[0] != SpanGround.Ground)
			{
				return "A suspension bridge must start on solid, undug ground with nothing built on it.";
			}
			if (lane[n - 1] != SpanGround.Ground)
			{
				return "A suspension bridge must end on solid, undug ground with nothing built on it.";
			}
			for (int i = 1; i < n - 1; i++)
			{
				if (lane[i] == SpanGround.Ground)
				{
					return "A suspension bridge must cross a hole without touching down: square " + i + " of the drag is undug ground (build two bridges).";
				}
				if (lane[i] != SpanGround.Hole)
				{
					return "A suspension bridge can only cross dug ground at least 0.5 m deep; square " + i + " of the drag is blocked.";
				}
			}
			int cap = MaxLength(tier, lengthMultiplier);
			List<int> supports = Supports(n, towers);
			for (int k = 0; k + 1 < supports.Count; k++)
			{
				int run = supports[k + 1] - supports[k] - 1;
				if (run > cap)
				{
					return "A " + TierLabel(tier) + " suspension bridge spans at most " + cap + " squares between supports (this span: "
						+ run + "). Build a tower on the hole floor to go further.";
				}
			}
			return null;
		}

		/// <summary>The whole drag: a rectangle lenAlong × width (width 1 to 3, every lane parallel). Null = accepted.</summary>
		public static string ValidateDrag(IList<IList<SpanGround>> lanes, IList<ICollection<int>> towersPerLane, SuspensionTier tier,
			float lengthMultiplier)
		{
			if (lanes == null || lanes.Count == 0)
			{
				return "Drag a suspension bridge from solid ground, across a dug hole, to solid ground on the far side.";
			}
			if (lanes.Count > MaxWidth)
			{
				return "A suspension bridge is 1 to 3 squares wide.";
			}
			for (int l = 0; l < lanes.Count; l++)
			{
				string r = ValidateLane(lanes[l], towersPerLane != null && l < towersPerLane.Count ? towersPerLane[l] : null, tier,
					lengthMultiplier);
				if (r != null)
				{
					return lanes.Count == 1 ? r : "Row " + (l + 1) + ": " + r;
				}
			}
			return null;
		}

		// ── SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP (parent design §4.1, Q4, Q9) ───────────────────────────────────

		/// <summary>Splash (slime slip, toxic fill) reaches a pawn on a grate at this share of the open-pit chance.</summary>
		public const float GrateSplashFactor = 0.5f;

		/// <summary>A pawn on a grate over burning liquid: chance per fire effects check (60 ticks) of one vanilla Burn injury, and
		/// its damage. Proposals (≈ 8 burns, ≈ 12 damage spread over the body in 2,500 ticks); never a new hediff (one kind of heat).</summary>
		public const float GrateBurnChancePerCheck = 0.2f;
		public const float GrateBurnDamage = 1.5f;

		/// <summary>Only the steel and heavy types come grated (a grate must not burn away in the fire it passes).</summary>
		public static bool MayBeGrated(SuspensionTier t)
		{
			return t == SuspensionTier.Steel || t == SuspensionTier.Heavy;
		}

		/// <summary>The splash chance on a grate: half the chance the same pawn would have standing in the hole.</summary>
		public static float GrateSplashChance(float openPitChance)
		{
			return openPitChance * GrateSplashFactor;
		}

		/// <summary>Decilitres of a spill on a deck square that drain into the hole below: all of it the hole has room for, on
		/// a grate over a dug square with the setting on; nothing otherwise (a solid deck keeps its spill as filth).</summary>
		public static long GrateDrainDl(bool grated, bool settingOn, bool dug, long spilledDl, long roomDl)
		{
			if (!grated || !settingOn || !dug || spilledDl <= 0 || roomDl <= 0)
			{
				return 0;
			}
			return spilledDl < roomDl ? spilledDl : roomDl;
		}

		/// <summary>The build-order rule (construction design §1.3): a deck square may be worked once the square next to it along
		/// its lane, toward either anchor, is a finished anchor or a finished deck square.</summary>
		public static bool MayBuildDeck(int i, int n, System.Func<int, bool> builtAt)
		{
			if (i <= 0 || i >= n - 1)
			{
				return true;
			}
			return builtAt(i - 1) || builtAt(i + 1);
		}
	}
}
