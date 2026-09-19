using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// The arithmetic of the source stock model (flowworks_mod_definition.md §5),
	/// with every Verse and UnityEngine dependency removed.
	///
	/// WHY THIS FILE IS SEPARATE FROM <see cref="RM_LiquidStock"/>. The Pits
	/// selftest (Source/Pits/SelfTest/) names its own weakness in its header: the
	/// escape-chance formula there is a HAND TRANSCRIPTION of the real method,
	/// so it keeps passing against the old formula if the real one changes. That
	/// trap is avoidable here. These are the numbers §5 actually specifies — the
	/// 5:1 budget, the refill accrual, the supported-cell count, the recession
	/// order and the credit/debit primitives — and none of them needs a Map, a
	/// Thing or an IntVec3 to be stated. Pulling them into a plain-C# static
	/// class lets Source/SelfTest/ compile the PRODUCTION file in directly, so a
	/// change to any constant or clause below fails the selftest immediately
	/// instead of silently drifting away from a copy.
	///
	/// ⛔ NOTHING WITH A VERSE OR UNITY TYPE MAY BE ADDED TO THIS FILE. It is
	/// compiled into a net8.0 console project that has no RimWorld assemblies at
	/// all; `using Verse;` or `Mathf` here breaks the selftest build, which is
	/// the guard rail working, not a problem to route around. Grid walking,
	/// terrain writes and scribing stay in RM_LiquidStock where they belong.
	/// </summary>
	public static class RM_StockMath
	{
		/// <summary>A body's per-footprint-cell budget may never reach zero. A
		/// capacity of zero makes PerCellVolume zero, which makes the supported
		/// cell count a division by zero — and a settings slider at its lowest
		/// notch is a player choice, not a licence to divide by zero.</summary>
		public const float MinPerCellVolume = 0.01f;

		/// <summary>Which way a season pushes refill on a desert world. The
		/// mapping from RimWorld's <c>Season</c> enum onto these four bands lives
		/// in <see cref="RM_LiquidStock"/>, because <c>Season</c> is a Verse type;
		/// the NUMBERS live here, where they can be tested.</summary>
		public enum SeasonBand
		{
			/// <summary>Spring — the wet season carries the refill.</summary>
			Wet,
			/// <summary>Summer, permanent summer — high summer barely moves it.</summary>
			Dry,
			/// <summary>Fall, and anything unclassified.</summary>
			Neutral,
			/// <summary>Winter, permanent winter.</summary>
			Cool,
		}

		// ── the 5:1 budget (§5, "Budget") ─────────────────────────────────

		/// <summary>Fill-units one cell of footprint is worth:
		/// <c>canalCellsPerSourceCell * volumePerTile</c>, scaled by the player's
		/// budget slider and floored so it can never reach zero.</summary>
		public static float PerCellBudget(float canalCellsPerSourceCell, float volumePerTile, float budgetMultiplier)
		{
			float perCell = canalCellsPerSourceCell * volumePerTile * budgetMultiplier;
			return perCell < MinPerCellVolume ? MinPerCellVolume : perCell;
		}

		/// <summary>§5's formula verbatim:
		/// <c>bodyCapacity = sourceCellCount * canalCellsPerSourceCell * volumePerTile</c>.</summary>
		public static float BodyCapacity(int sourceCellCount, float canalCellsPerSourceCell, float volumePerTile, float budgetMultiplier)
		{
			if (sourceCellCount <= 0)
			{
				return 0f;
			}
			return sourceCellCount * PerCellBudget(canalCellsPerSourceCell, volumePerTile, budgetMultiplier);
		}

		/// <summary>The 5:1 budget read backwards — what one cell of footprint is
		/// worth, and the number recession compares its stock against.</summary>
		public static float PerCellVolume(float capacity, int cellCount)
		{
			return cellCount > 0 ? capacity / cellCount : 0f;
		}

		// ── classification (ruling 16) ────────────────────────────────────

		/// <summary>LIMITLESS is a SENTINEL, never a magic number (§5). A body
		/// earns it by being too large to flood-fill (an ocean) or by touching
		/// the map edge AND being big enough that the off-map continuation is a
		/// believable reservoir. Classified ONCE and never re-argued, which is
		/// ruling 16 — this function is called from exactly one place, at
		/// formation, and never again.</summary>
		public static bool IsLimitless(bool stickyEnabled, bool truncated, bool touchesEdge, int cellCount, int minLimitlessCells)
		{
			if (!stickyEnabled)
			{
				return false;
			}
			return truncated || (touchesEdge && cellCount >= minLimitlessCells);
		}

		// ── refill (ruling 2, §5 "Refill") ────────────────────────────────

		public static float SeasonFactor(SeasonBand band)
		{
			switch (band)
			{
				case SeasonBand.Wet: return 1.25f;
				case SeasonBand.Dry: return 0.5f;
				case SeasonBand.Cool: return 0.75f;
				default: return 1f;
			}
		}

		/// <summary>Fill-units a LIMITED body regains per in-game day:
		/// <c>groundOoze * sourceCellCount</c> as the always-on baseline, times a
		/// rain term read from the map's current rain rate, times the season
		/// term. Proportional to footprint on purpose — a one-cell seep regains
		/// slowest in absolute terms, which is what a player watching a small
		/// pond actually sees.</summary>
		public static float RefillPerDay(float oozePerSourceCellPerDay, int cellCount, float rainFactor, float rainRate, SeasonBand band, float rateMultiplier)
		{
			if (cellCount <= 0)
			{
				return 0f;
			}
			float baseline = oozePerSourceCellPerDay * cellCount;
			return baseline * (1f + rainFactor * rainRate) * SeasonFactor(band) * rateMultiplier;
		}

		/// <summary>The accrual for ONE pulse, and the reason pillar 2 holds: the
		/// per-day rate is scaled by how much of a day the pulse covered, so the
		/// result is identical whether the pulse interval is 600 ticks or 6000.
		/// Refill is a rate sampled rarely, never a per-tick drip.</summary>
		public static float RefillForPulse(float perDay, int pulseTicks, int ticksPerDay)
		{
			if (pulseTicks <= 0 || ticksPerDay <= 0)
			{
				return 0f;
			}
			return perDay * (pulseTicks / (float)ticksPerDay);
		}

		/// <summary>Stock after an accrual, clamped to capacity (§5: "clamped to
		/// bodyCapacity"). A body never holds more than the footprint justifies.</summary>
		public static float ClampToCapacity(float stock, float gained, float capacity)
		{
			float raised = stock + gained;
			return raised > capacity ? capacity : raised;
		}

		// ── recession and restoration (§5, "Recession, cell by cell") ─────

		/// <summary>How many cells of footprint the current stock still pays for.
		/// Floor, not round: a body pays for a cell in full or gives it up.</summary>
		public static int SupportedCells(float stock, float perCellVolume)
		{
			if (perCellVolume <= 0f)
			{
				return 0;
			}
			int supported = (int)Math.Floor(stock / perCellVolume);
			return supported < 0 ? 0 : supported;
		}

		/// <summary>§5's recession order, as a strict "is A a better candidate
		/// than the incumbent" predicate: fewest same-liquid neighbours first,
		/// tie-broken by greatest distance from the centroid, then by the cell
		/// index — a deterministic per-cell number, so the order survives a save
		/// and is identical on every machine.
		///
		/// 🔑 That last tie-break is what makes recession reproducible. Without
		/// it two cells equally far from the centroid with equally few neighbours
		/// would be separated by iteration order, and a reload could dry a
		/// different cell than the one the player watched dry.</summary>
		public static bool PrefersCandidate(
			int neighbours, int distSquared, int cellIndex,
			int bestNeighbours, int bestDistSquared, int bestCellIndex)
		{
			if (neighbours != bestNeighbours)
			{
				return neighbours < bestNeighbours;
			}
			if (distSquared != bestDistSquared)
			{
				return distSquared > bestDistSquared;
			}
			return cellIndex < bestCellIndex;
		}

		// ── the debit / credit primitives (§5, "Debits") ──────────────────

		/// <summary>May a body still hand out one unit? Compared against the SAME
		/// unit a debit spends — a flat 1 would let a viscous liquid with
		/// volumePerTile above 1 pass the check and then fail the debit, which
		/// reads as a source that stutters rather than one that is empty.</summary>
		public static bool CanSupply(bool limitless, float stock, float unit)
		{
			return limitless || stock >= unit;
		}

		/// <summary>Whether a debit of <paramref name="units"/> is affordable. The
		/// caller MUST NOT move liquid when this is false: a transfer that happens
		/// after its debit failed is exactly the silent leak the conservation
		/// ledger exists to catch.</summary>
		public static bool CanDebit(bool limitless, float stock, float units)
		{
			return limitless || stock >= units;
		}

		/// <summary>How much of an offered credit a body accepts — the receiving
		/// half of fill-in displacement (§5, "Filling a canal back in"). A limited
		/// body accepts up to its capacity and no more; a limitless body accepts
		/// everything, because the reservoir it stands for is off-map and cannot
		/// be overfilled.
		///
		/// Kept deliberately generic: CANAL_FILL_IN_DISPLACEMENT_1's displacement
		/// walk is one caller, a pump (§8) is another, and neither needs its own
		/// arithmetic.</summary>
		public static float CreditAccepted(bool limitless, float stock, float capacity, float units)
		{
			if (units <= 0f)
			{
				return 0f;
			}
			if (limitless)
			{
				return units;
			}
			float room = capacity - stock;
			if (room <= 0f)
			{
				return 0f;
			}
			return room < units ? room : units;
		}

		// ── fill-in displacement (§5, "Filling a canal back in") ──────────
		//
		// 🔑 TWO UNITS LIVE HERE AND THEY ARE NOT THE SAME. The depth/fill grids
		// count LEVELS (0..4, one byte per cell); a body's stock counts
		// FILL-UNITS of volume. One level of a given liquid is
		// `fluid.volumePerTile` fill-units — which is exactly what the pulse
		// already spends, debiting volumePerTile per ONE level moved out of a
		// source. Displacement is the same transfer read backwards, so it must
		// convert the same way. Handing a level count straight to a fill-unit
		// credit under-pays every liquid whose volumePerTile is not 1.

		/// <summary>How much a fill-in displaces out of a cell: whatever the new,
		/// shallower cell can no longer hold, <c>F - (D-1)</c>, clamped at zero.
		///
		/// A trench holding one level out of four loses nothing when it is raised
		/// to three — the liquid simply sits higher, which is what actually
		/// happens when you shovel earth in under it.</summary>
		public static int DisplacedLevels(int depth, int fill)
		{
			if (depth <= 0)
			{
				return 0;
			}
			if (fill > depth)
			{
				fill = depth;
			}
			int displaced = fill - (depth - 1);
			return displaced > 0 ? displaced : 0;
		}

		/// <summary>Room below a channel cell's brim, in levels. Negative fill or
		/// a fill above the brim (only reachable from a corrupt grid) reads as no
		/// room rather than as negative room, so a caller can add this to a
		/// running total without guarding.</summary>
		public static int CellRoom(int depth, int fill)
		{
			int room = depth - fill;
			return room > 0 ? room : 0;
		}

		/// <summary>How many WHOLE fill levels a body will take back.
		///
		/// Whole levels, not a float, and that is the point: the grid can only
		/// record an integer fill, so crediting a body a fractional level's worth
		/// of volume would put stock into the world that no cell ever gave up.
		/// Flooring here and crediting exactly <c>result * unitPerLevel</c> keeps
		/// the two ledgers equal to the unit.
		///
		/// A limitless body takes everything — the off-map continuation it stands
		/// for cannot be overfilled (§5).</summary>
		public static int CreditableLevels(bool limitless, float stock, float capacity, int offeredLevels, float unitPerLevel)
		{
			if (offeredLevels <= 0)
			{
				return 0;
			}
			if (limitless)
			{
				return offeredLevels;
			}
			if (unitPerLevel <= 0f)
			{
				// A malformed FluidDef (volumePerTile <= 0 is rejected by
				// FluidDef's own ConfigErrors) would otherwise divide by zero.
				// Accept nothing rather than accept everything: an unbounded
				// credit is a silent mass gain, and a refused credit shows up as
				// disclosed overflow, which is the failure the player can see.
				return 0;
			}
			float room = capacity - stock;
			if (room <= 0f)
			{
				return 0;
			}
			int levels = (int)Math.Floor(room / unitPerLevel);
			if (levels <= 0)
			{
				return 0;
			}
			return levels < offeredLevels ? levels : offeredLevels;
		}
	}
}
