using System;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>Pure arithmetic of the liquid kits — no Verse types, so the C# selftest compiles it directly.
	/// Every constant here is PROVISIONAL (owner ruling 2026-10-03: ship first-guess numbers, tune live).</summary>
	public static class RM_KitMath
	{
		/// <summary>Whole reaction batches runnable now: bounded by accrued batches, both reactants on hand
		/// (each batch eats unitsA of A and unitsB of B) and output room (outputRoom &lt; 0 = unbounded).</summary>
		public static int ReactionBatches(float accruedBatches, int unitsA, int unitsB, int haveA, int haveB,
			int productUnits, int outputRoom)
		{
			if (unitsA < 1 || unitsB < 1)
			{
				return 0;
			}
			int n = (int)Math.Floor(accruedBatches + 1e-4f);
			n = Math.Min(n, haveA / unitsA);
			n = Math.Min(n, haveB / unitsB);
			if (outputRoom >= 0)
			{
				n = productUnits < 1 ? 0 : Math.Min(n, outputRoom / productUnits);
			}
			return Math.Max(0, n);
		}

		/// <summary>Accrued batch budget per rare tick (240 a day).</summary>
		public static float BatchesPerRareTick(float batchesPerDay, float settingsMultiplier)
		{
			if (batchesPerDay <= 0f || settingsMultiplier <= 0f)
			{
				return 0f;
			}
			return batchesPerDay * settingsMultiplier / 240f;
		}

		/// <summary>Heat left in a hot release: 1 at release, linear to 0 at cooled. PROVISIONAL shape.</summary>
		public static float HeatFraction(int ticksSinceRelease, int coolTicks)
		{
			if (coolTicks <= 0 || ticksSinceRelease >= coolTicks)
			{
				return 0f;
			}
			if (ticksSinceRelease <= 0)
			{
				return 1f;
			}
			return 1f - (float)ticksSinceRelease / coolTicks;
		}

		/// <summary>Burn damage dealt to a pawn standing in a hot release on one check: the full scald at
		/// release heat, scaled by heat left and the setting; below a quarter heat the water is merely hot
		/// and deals nothing. Rounded to whole damage (0 = no hit this check).</summary>
		public static int ScaldDamage(float fullScald, float heatFraction, float multiplier)
		{
			if (fullScald <= 0f || multiplier <= 0f || heatFraction < 0.25f)
			{
				return 0;
			}
			return (int)Math.Round(fullScald * heatFraction * multiplier, MidpointRounding.AwayFromZero);
		}

		/// <summary>Whether a drained cell keeps the liquid's residue: a roll against the def's chance.</summary>
		public static bool LeavesResidue(float chance, float roll)
		{
			return chance > 0f && roll < chance;
		}
	}
}
