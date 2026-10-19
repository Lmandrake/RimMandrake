using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_BUILD_PROGRAM_1 Phase 6 (fire), the Verse-free arithmetic so the selftest drives the production
	/// numbers. Ruling 7 (owner, 2026-09-16): burn is a RATE, never a timer. LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth
	/// spec §5.6, D3 defaulted, veto-able): ONE rate for every burning square, canal or pond, 0.5 m (one notch) a day,
	/// applied in decilitres so a thin sheet burns away in a fraction of it.
	/// </summary>
	public static class RM_FireMath
	{
		public const int TicksPerDay = 60000;

		/// <summary>Ticks for one burning square to lose one notch (0.5 m). Ruling 7: one day at 1. The one rate, canal or pond.</summary>
		public static int TicksPerCanalLevel(float burnDaysPerLevel)
		{
			return Math.Max(1, (int)Math.Round(TicksPerDay * Math.Max(0.01f, burnDaysPerLevel)));
		}

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: add elapsed burn ticks and return the DECILITRES due at
		/// <paramref name="ticksPerNotch"/> ticks per notch (<paramref name="unitsPerNotch"/> dL). The accumulator keeps the
		/// remainder in tick-decilitres (always below ticksPerNotch), so nothing is lost between pulses: 240 pulses of 250
		/// ticks at a day a notch burn exactly one notch.</summary>
		public static long DlDue(ref int accumulator, int addTicks, int ticksPerNotch, int unitsPerNotch)
		{
			if (ticksPerNotch <= 0 || addTicks <= 0 || unitsPerNotch <= 0)
			{
				return 0;
			}
			long total = (accumulator < 0 ? 0 : accumulator % ticksPerNotch) + (long)addTicks * unitsPerNotch;
			long dl = total / ticksPerNotch;
			accumulator = (int)(total % ticksPerNotch);
			return dl;
		}

		/// <summary><see cref="DlDue"/>, nothing unless the liquid standing there NOW burns (P8, as <see cref="CanalLevelsToBurn"/>).</summary>
		public static long CanalDlToBurn(bool burnableNow, ref int accumulator, int addTicks, int ticksPerNotch, int unitsPerNotch)
		{
			return burnableNow ? DlDue(ref accumulator, addTicks, ticksPerNotch, unitsPerNotch) : 0;
		}

		/// <summary>How often RM_LiquidFire's Maintain re-reads every burning cell (and drops one whose liquid stopped burning).</summary>
		public const int FireCheckIntervalTicks = 30;

		/// <summary>The flow pulse's floor (Mod Settings cannot set it lower). FIRE_BURN_PULSE_PROVE_REFILL_RACE (P8): it is
		/// kept above <see cref="FireCheckIntervalTicks"/> so a Maintain always runs between two pulses, and a cell drained
		/// and refilled with water by one pulse is put out before the next pulse's burn (selftested).</summary>
		public const int MinFlowPulseTicks = 60;

		/// <summary>P8 (GPT G3.7): the levels a burn pulse takes from a canal cell. Nothing unless the liquid standing there
		/// NOW burns: replacement water that refilled a cell since the last check is never consumed, and the cell's
		/// accumulator does not advance on it. Before P8 the pulse burned whatever filled the cell and relied only on the
		/// timing above.</summary>
		public static int CanalLevelsToBurn(bool burnableNow, ref int accumulator, int addTicks, int ticksPerLevel)
		{
			return burnableNow ? LevelsDue(ref accumulator, addTicks, ticksPerLevel) : 0;
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

		/// <summary>LIQUID_FIRE_MEND_COVER_AND_SAVE (C4-F7): a flyer is above the fire (never lit); a pawn standing on an intact
		/// pit cover is not trapped in the pit beneath it (the open-cell chance, not the trapped one).</summary>
		public static float AttachChance(bool inPit, bool onIntactCover, bool flying)
		{
			if (flying)
			{
				return 0f;
			}
			return AttachChance(inPit && !onIntactCover);
		}
	
		/// <summary>SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP (parent design §4.1): a grated deck passes the fire below to the people
		/// on it at this share of the open-pit (trapped) chance; a solid deck keeps the open-cell chance.</summary>
		public const float GratedOpenPitFactor = 0.75f;

		/// <summary>C4-F7 plus the grate: a flyer is never lit; a pawn on an intact GRATED deck over the fire catches at the
		/// open-pit chance × <see cref="GratedOpenPitFactor"/>; on a solid deck or cover, the open-cell chance.</summary>
		public static float AttachChance(bool inPit, bool onIntactDeck, bool flying, bool grated)
		{
			if (flying)
			{
				return 0f;
			}
			if (onIntactDeck && grated)
			{
				return AttachChance(true) * GratedOpenPitFactor;
			}
			return AttachChance(inPit, onIntactDeck, false);
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
