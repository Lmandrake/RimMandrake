// Verse-free kernel of the stocked pools (RM_MapComponent_PoolStock / RM_PoolBody): the READ gauge, the feed clock and
// the per-pulse mismanagement dice (starvation decay, vhorrin emergence, vizhik escape). The mod calls these with the
// same expressions and the engine's Rand; SelfTest/WeepingStonesFuzz.cs compiles this file alone, so it must stay free
// of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.WeepingStones
{
	public enum RM_PoolStockState
	{
		/// <summary>Murrin rings are up, no vhorrin, population healthy relative to footprint.</summary>
		Healthy,
		/// <summary>Population present but thin relative to the pen's footprint - hungry or predated.</summary>
		Thin,
		/// <summary>No rings at all - the dead-oasis image as farm telemetry.</summary>
		Silent,
		/// <summary>One wide slow ring doing all the surfacing - a live RM_Vhorrin occupies the pen.</summary>
		Vhorrin,
	}

	public struct PoolPulse
	{
		public RM_PoolStockState state;
		public int starveIdx;   // index into the non-vhorrin candidates, or -1
		public int emergeIdx;   // index into the candidates of the one that turns vhorrin, or -1
		public int escapeIdx;   // index into the vizhik list, or -1
	}

	public static class RM_PoolKernel
	{
		public const float ThinPopulationFraction = 0.5f;
		public const int UnfedThinDays = 2;
		public const int UnfedDecayDays = 3;
		public const float UnfedDeathChancePerPulse = 0.03f;
		public const float VhorrinEmergenceChanceCrowded = 0.02f;
		public const float VhorrinEmergenceChanceCrashed = 0.01f;

		// ---- the feed clock ----------------------------------------------------------------------
		public static int UnfedDays(int lastFedTick, int currentTick, int ticksPerDay)
		{
			if (lastFedTick < 0)
			{
				return 0;
			}
			return Math.Max(0, currentTick - lastFedTick) / ticksPerDay;
		}

		public static bool NeedsFeed(int lastFedTick, int currentTick, int ticksPerDay)
		{
			return lastFedTick < 0 || currentTick - lastFedTick >= ticksPerDay;
		}

		// ---- the READ gauge ----------------------------------------------------------------------
		public static RM_PoolStockState ClassifyState(int population, int vhorrinCount, int cellCount, int unfedDays)
		{
			if (vhorrinCount > 0)
			{
				return RM_PoolStockState.Vhorrin;
			}
			if (population <= 0)
			{
				return RM_PoolStockState.Silent;
			}
			if (unfedDays >= UnfedThinDays)
			{
				return RM_PoolStockState.Thin;
			}
			if (cellCount > 0 && population < cellCount * ThinPopulationFraction)
			{
				return RM_PoolStockState.Thin;
			}
			return RM_PoolStockState.Healthy;
		}

		// ---- the dice ---------------------------------------------------------------------------
		// Rand.Chance(c): no roll at <= 0 or >= 1, else value < c.
		public static bool Chance(float c, Func<float> value)
		{
			if (c <= 0f) return false;
			if (c >= 1f) return true;
			return value() < c;
		}

		public static bool Crowded(int cellCount, int population) { return cellCount > 0 && population >= cellCount; }
		public static bool Crashed(int unfedDays) { return unfedDays >= UnfedDecayDays; }

		public static float EmergenceChance(bool crowded, bool crashed, float oddsMultiplier)
		{
			return (crowded ? VhorrinEmergenceChanceCrowded : crashed ? VhorrinEmergenceChanceCrashed : 0f) * oddsMultiplier;
		}

		// One pulse's decisions for one pen. value() is Rand.Value, range(n) is Rand.Range(0, n); the draws happen in the
		// order and under the conditions the original loop used: starve, emerge, escape.
		public static PoolPulse Decide(int population, int vhorrinCount, int cellCount, int unfedDays,
									   int candidateCount, int vizhikCount, float oddsMultiplier, float vizhikEscapeChance,
									   Func<float> value, Func<int, int> range)
		{
			var p = new PoolPulse { starveIdx = -1, emergeIdx = -1, escapeIdx = -1 };
			p.state = ClassifyState(population, vhorrinCount, cellCount, unfedDays);
			if (unfedDays >= UnfedDecayDays && candidateCount > 0 && Chance(UnfedDeathChancePerPulse, value))
			{
				p.starveIdx = range(candidateCount);
			}
			if (vhorrinCount <= 0 && candidateCount > 0)
			{
				float emergenceChance = EmergenceChance(Crowded(cellCount, population), Crashed(unfedDays), oddsMultiplier);
				if (emergenceChance > 0f && Chance(emergenceChance, value))
				{
					p.emergeIdx = range(candidateCount);
				}
			}
			if (vizhikCount > 0 && Chance(vizhikEscapeChance, value))
			{
				p.escapeIdx = range(vizhikCount);
			}
			return p;
		}
	}
}
