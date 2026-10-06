using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_BUILD_PROGRAM_1 Phase 6 (fire), the Verse-free arithmetic so the selftest drives the production
	/// numbers. Ruling 7 (owner, 2026-09-16): burn is a RATE on the tier ladder, never a timer —
	/// one canal fill level per day while alight, one source level per five days (the 5:1 density relation).
	/// </summary>
	public static class RM_FireMath
	{
		public const int TicksPerDay = 60000;

		/// <summary>Ticks for one burning canal cell to lose one fill level. Ruling 7: one day at 1.</summary>
		public static int TicksPerCanalLevel(float burnDaysPerLevel)
		{
			return Math.Max(1, (int)Math.Round(TicksPerDay * Math.Max(0.01f, burnDaysPerLevel)));
		}

		/// <summary>Ticks for a burning source cell to cost its body one level's worth of stock. Ruling 7: five
		/// days, the same 5:1 the supply budget uses. Kept a separate dial so the settings screen can say so.</summary>
		public static int TicksPerSourceLevel(float sourceBurnDaysPerLevel)
		{
			return TicksPerCanalLevel(sourceBurnDaysPerLevel);
		}

		/// <summary>Add elapsed burn ticks to a cell's accumulator and return how many whole levels are due,
		/// leaving the remainder. A rate, not a countdown: a cell that is refilled while alight keeps burning.</summary>
		public static int LevelsDue(ref int accumulator, int addTicks, int ticksPerLevel)
		{
			if (ticksPerLevel <= 0 || addTicks <= 0)
			{
				return 0;
			}
			long total = (long)accumulator + addTicks;
			int levels = (int)(total / ticksPerLevel);
			accumulator = (int)(total % ticksPerLevel);
			return levels;
		}

		/// <summary>When the travelling front reaches the next cell. One front for every burnable liquid;
		/// speed is the only difference between a creeping fuse and a detonation (Phase 6).</summary>
		public static int FrontDue(int parentDue, int ticksPerCell, float speedMultiplier)
		{
			float m = speedMultiplier <= 0.01f ? 0.01f : speedMultiplier;
			return parentDue + Math.Max(1, (int)Math.Round(ticksPerCell / m));
		}

		/// <summary>How many source cells deep the front may walk into a natural body from where it entered.
		/// Fire reaches the source (his words: "they will also light their source"); this bound only stops one
		/// lit pond edge walking an ocean cell by cell. 0 = a source never lights.</summary>
		public static int SourceHopsFor(bool parentIsSource, int parentHops, bool childIsSource)
		{
			if (!childIsSource)
			{
				return 0;
			}
			return parentIsSource ? parentHops + 1 : 1;
		}

		public static bool SourceHopAllowed(int hops, int reach)
		{
			return hops <= reach;
		}

		/// <summary>Ruling 22: liquid acting on a TRAPPED occupant is very effective. A pawn standing in burning
		/// liquid on an ordinary cell may step out; one held at D=4 cannot, so it always catches.
		/// PROVISIONAL: 0.35 attach chance per check outside a pit.</summary>
		public static float AttachChance(bool heldInPit)
		{
			return heldInPit ? 1f : 0.35f;
		}
	
		/// <summary>Rain douse chance per 60-tick check on an open burning cell. PROVISIONAL: 0.03 at full rain.</summary>
		public static float RainDouseChance(float rainRate)
		{
			if (rainRate <= 0f) return 0f;
			return 0.03f * (rainRate > 1f ? 1f : rainRate);
		}

		/// <summary>Which blasts light liquid: flame and bomb (vanilla), and any damage named incendiary or
		/// thermobaric (mods). EMP, smoke, firefoam, stun and the rest never do.</summary>
		public static bool ExplosionIgnites(string damageDefName)
		{
			if (string.IsNullOrEmpty(damageDefName)) return false;
			if (damageDefName == "Flame" || damageDefName == "Bomb") return true;
			string d = damageDefName.ToLowerInvariant();
			return d.Contains("incendiary") || d.Contains("thermobaric") || d.Contains("napalm");
		}
	}
}
