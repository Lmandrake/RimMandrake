using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, step 1: the accounting of a <c>Flood_FlowWorks</c> release, Verse-free
	/// so it is selftested (SelfTest/FloodReleaseChecks.cs). Fixes the four faults the design's §6 item 15 filed against the
	/// release (design/RimMandrake/canal_overflow_flooding_2026-10-21.md):
	/// <list type="number">
	/// <item>No silent exit: a release ends only through one path that offers what is left to the sheet (canal overflow) and
	/// DISCLOSES the rest (<see cref="Ledger.Lose"/>), whether it ends by expiry, an empty frontier or a missing def.</item>
	/// <item>Volume in whole decilitres, the depth engine's unit (one notch over one square = <see cref="U"/> dL), never a float
	/// notch: a dug square takes exactly the dL the engine pours, a surface tile exactly what it costs, and nothing is overdrawn
	/// (the old rule paid one level for a partial unit and wrote the brim over a part-notch).</item>
	/// <item>Refused squares are saved (the Verse class scribes them), so eligibility does not change on reload.</item>
	/// <item>The walk is deterministic: <see cref="Pick"/> is a hash of the release's own salt and step counter, never the
	/// global <c>Rand</c>.</item>
	/// </list></summary>
	public static class RM_FloodReleaseMath
	{
		/// <summary>Decilitres in one notch over one square (= RM_LevelSolve.U).</summary>
		public const long U = RM_Volume.UnitsPerLevel;

		/// <summary>A float notch amount (the old <c>Configure(fluid, volume)</c> contract, kept for callers in other mods) as dL.</summary>
		public static long NotchesToDl(float notches)
		{
			if (!(notches > 0f))
			{
				return 0;
			}
			return (long)Math.Round(notches * (double)U);
		}

		/// <summary>What one surface tile costs (FluidDef.volumePerTile notches), at least 1 dL.</summary>
		public static long PerTileDl(float volumePerTile) => Math.Max(1L, NotchesToDl(volumePerTile));

		/// <summary>Tiles a release can still pay for (at least 1, it sets the expand rate and expiry).</summary>
		public static int PayableTiles(long remainingDl, long perTileDl)
		{
			if (remainingDl <= 0 || perTileDl <= 0)
			{
				return 1;
			}
			long t = (remainingDl + perTileDl - 1) / perTileDl;
			return (int)Math.Max(1L, Math.Min(int.MaxValue, t));
		}

		/// <summary>The dL a release pours into a dug square with <paramref name="cellRoomDl"/> of room: as much as it holds and
		/// the square takes; whole notches only when the engine is in whole-notch mode. Never more than the release holds.</summary>
		public static long DugPourDl(long remainingDl, long cellRoomDl, bool levelExact)
		{
			if (remainingDl <= 0 || cellRoomDl <= 0)
			{
				return 0;
			}
			long want = Math.Min(remainingDl, cellRoomDl);
			if (!levelExact)
			{
				want -= want % U;
			}
			return want;
		}

		/// <summary>What a surface (temp-terrain) tile debits: its cost, or the last of the release (never an overdraw).</summary>
		public static long SurfaceDebitDl(long remainingDl, long perTileDl) =>
			remainingDl <= 0 ? 0 : Math.Min(remainingDl, Math.Max(1L, perTileDl));

		/// <summary>A deterministic draw in [0, n) from the release's salt, its step counter and a slot (SplitMix64).</summary>
		public static int Pick(int salt, long step, int slot, int n)
		{
			if (n <= 1)
			{
				return 0;
			}
			ulong z = unchecked((ulong)(uint)salt * 0x9E3779B97F4A7C15UL + (ulong)step * 0xBF58476D1CE4E5B9UL + (ulong)(uint)slot * 0x94D049BB133111EBUL);
			z = unchecked((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL);
			z = unchecked((z ^ (z >> 27)) * 0x94D049BB133111EBUL);
			z ^= z >> 31;
			return (int)(z % (ulong)n);
		}

		/// <summary>One release's books, all in dL: what it was given, what it put into the world (dug squares and surface
		/// tiles), what the sheet accepted at its end, what it disclosed as lost, and what it still holds. Every change moves dL
		/// from <see cref="Remaining"/> to exactly one exit, so <see cref="Closes"/> holds after every step.</summary>
		public sealed class Ledger
		{
			public long In, Placed, Spilled, Lost, Remaining;

			public static Ledger Start(long dl) => new Ledger { In = Math.Max(0, dl), Remaining = Math.Max(0, dl) };

			public bool Closes => Remaining >= 0 && In == Remaining + Placed + Spilled + Lost;

			/// <summary>Debit exactly <paramref name="dl"/> (clamped to what is held) as placed. Returns what was debited.</summary>
			public long Place(long dl) => Move(dl, ref Placed);

			/// <summary>The sheet took <paramref name="dl"/> of the leftover (clamped to what is held).</summary>
			public long Spill(long dl) => Move(dl, ref Spilled);

			/// <summary>Everything still held is disclosed as lost (the release could put it nowhere). Returns the amount.</summary>
			public long Lose() => Move(Remaining, ref Lost);

			private long Move(long dl, ref long into)
			{
				long d = Math.Max(0, Math.Min(dl, Remaining));
				Remaining -= d;
				into += d;
				return d;
			}
		}
	}
}
