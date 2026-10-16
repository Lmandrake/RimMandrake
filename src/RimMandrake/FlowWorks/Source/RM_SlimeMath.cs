namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SLIME_CROSSING_BUILD_SLIPPERY_SLOPE, Verse-free so the selftest drives the production numbers. Owner (feature
	/// description, quoted in design/validation_walks/RimMandrake/FlowWorks.md): <i>"Slime has the particular property of
	/// being so slippery that it is nearly impossible to cross, and escape from the pit takes a great deal of time."</i>
	///
	/// The mechanic: a pawn WALKING through a liquid whose <c>FluidDef.slipperiness</c> &gt; 0 rolls once per
	/// <see cref="IntervalTicks"/>; a slip stuns it briefly, with a text mote saying so. A step toward shallower
	/// ground (climbing out) slips more, and a slip there also slides the pawn back to the start of the step. All numbers PROVISIONAL and tunable.
	/// </summary>
	public static class RM_SlimeMath
	{
		/// <summary>One roll per second of walking in slime.</summary>
		public const int IntervalTicks = 60;

		/// <summary>PROVISIONAL: chance per roll for a pawn wading in a brim-full cell of slipperiness 1.</summary>
		public const float BaseSlipChance = 0.35f;

		/// <summary>No roll is ever a certainty: "nearly" impossible, never impossible.</summary>
		public const float MaxSlipChance = 0.9f;

		/// <summary>Defaults of the Mod Settings (RimMandrakeFlowWorksSettings restates them as literals).</summary>
		public const float DefaultClimbOutFactor = 2f;
		public const float DefaultStunSeconds = 2f;

		/// <summary>Is the step this pawn is making a climb toward shallower ground (out of the slime)?
		/// fromD/toD = the hollow depths of the cell it stands on and the cell it is stepping into.</summary>
		public static bool IsClimbingOut(int fromD, int toD)
		{
			return toD < fromD;
		}

		/// <summary>Chance of a slip on one roll. 0 for a flier, a dry cell or a non-slippery liquid; otherwise the base chance
		/// times slipperiness, times how full the cell is (a trace of slime is less treacherous than a brimming canal, but
		/// any slime counts for at least half), times the climb-out factor when climbing out, times the setting multiplier,
		/// capped at <see cref="MaxSlipChance"/>.</summary>
		public static float SlipChance(float slipperiness, int fill, int depth, bool climbingOut, bool flying,
			float chanceMultiplier, float climbOutFactor)
		{
			if (flying || fill <= 0 || slipperiness <= 0f || chanceMultiplier <= 0f)
			{
				return 0f;
			}
			float frac = RM_FillEffectMath.FillFraction(fill, depth);
			float c = BaseSlipChance * slipperiness * (0.5f + 0.5f * frac) * chanceMultiplier;
			if (climbingOut)
			{
				c *= climbOutFactor < 1f ? 1f : climbOutFactor;
			}
			return c > MaxSlipChance ? MaxSlipChance : c;
		}

		/// <summary>Stun length in ticks for a slip (never below one tick).</summary>
		public static int StunTicks(float stunSeconds)
		{
			int t = (int)(stunSeconds * 60f + 0.5f);
			return t < 1 ? 1 : t;
		}

		/// <summary>Expected stun seconds per slime cell walked ACROSS (no lost progress: only a climb out slides back), at
		/// one roll per <see cref="IntervalTicks"/> of walking. The selftest uses it to state "nearly uncrossable" in time.</summary>
		public static float ExpectedStunSecondsPerCell(float chance, int ticksPerCell, float stunSeconds)
		{
			if (chance <= 0f || ticksPerCell <= 0)
			{
				return 0f;
			}
			return (float)ticksPerCell / IntervalTicks * chance * stunSeconds;
		}

		/// <summary>Expected seconds to make one climb-out step that takes <paramref name="ticksPerStep"/> to walk: every slip
		/// stuns and slides the pawn back to the start of the step, so the tries are geometric.</summary>
		public static float ExpectedClimbOutSeconds(float chance, int ticksPerStep, float stunSeconds)
		{
			float walk = ticksPerStep / 60f;
			if (chance <= 0f || ticksPerStep <= 0)
			{
				return walk;
			}
			float rolls = (float)ticksPerStep / IntervalTicks;
			float pClean = (float)System.Math.Pow(1f - chance, rolls);
			if (pClean < 0.001f)
			{
				pClean = 0.001f;
			}
			// failed tries: on average half the step walked, then the stun
			float failed = (1f - pClean) / pClean;
			return walk + failed * (stunSeconds + 0.5f * walk);
		}
	}
}
