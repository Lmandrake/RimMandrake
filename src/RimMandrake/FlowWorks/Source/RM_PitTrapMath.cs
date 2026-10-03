using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUPERDEEP_HOLDER_RETIRE_1 — the trap rule's arithmetic, Verse-free on purpose so
	/// Source/SelfTest/ compiles THIS production file (same discipline as RM_StockMath).
	///
	/// A pit is a canal cell dug to SUPERDEEP (D = 4) and nothing else; there is no holder
	/// Thing. Owner, 2026-10-02 (Q4): <i>"The pit has to be as wide as the creature to hold
	/// it. Otherwise it gets out."</i> RimWorld pawns occupy one cell, so width is a rule on
	/// BodySize: required width W = max(1, round(sqrt(BodySize))) (bands &lt;2.25 → 1,
	/// &lt;6.25 → 2, &lt;12.25 → 3; the bands are a proposal for his word, scaled by a Mod
	/// Setting). A pawn on a D = 4 cell is held only if some W×W square made entirely of
	/// D = 4 cells contains its cell. Diagonal runs do not count.
	/// </summary>
	public static class RM_PitTrapMath
	{
		public const int Superdeep = 4;

		/// <summary>Upper bound on the width ever searched; W = 9 is BodySize ~72-90.</summary>
		public const int MaxWidth = 9;

		/// <summary>Kg of pawn mass per point of blunt fall damage (inherited from the retired
		/// Building_OpenPit.FallDamagePerMassKg = 0.08f, unchanged).</summary>
		public const float FallDamagePerMassKg = 0.08f;

		/// <summary>W = max(1, round(sqrt(bodySize × multiplier))), rounding half AWAY from
		/// zero so the band edges are exactly 2.25 → 2 and 6.25 → 3.</summary>
		public static int RequiredWidth(float bodySize, float multiplier = 1f)
		{
			float b = bodySize * (multiplier > 0f ? multiplier : 1f);
			if (!(b > 0f))
			{
				return 1;
			}
			int w = (int)Math.Round(Math.Sqrt(b), MidpointRounding.AwayFromZero);
			return Math.Max(1, Math.Min(MaxWidth, w));
		}

		/// <summary>Is there a w×w square of D = 4 cells containing (x, z)?
		/// isSuperdeep must answer false out of bounds. At most w² squares × w² reads.</summary>
		public static bool PitWidthAt(Func<int, int, bool> isSuperdeep, int x, int z, int w)
		{
			if (w < 1)
			{
				w = 1;
			}
			if (!isSuperdeep(x, z))
			{
				return false;
			}
			for (int ox = x - w + 1; ox <= x; ox++)
			{
				for (int oz = z - w + 1; oz <= z; oz++)
				{
					bool all = true;
					for (int dx = 0; dx < w && all; dx++)
					{
						for (int dz = 0; dz < w; dz++)
						{
							if (!isSuperdeep(ox + dx, oz + dz))
							{
								all = false;
								break;
							}
						}
					}
					if (all)
					{
						return true;
					}
				}
			}
			return false;
		}

		/// <summary>The widest square pit containing (x, z): 0 if the cell is not D = 4.</summary>
		public static int MeasuredPitWidth(Func<int, int, bool> isSuperdeep, int x, int z)
		{
			int best = 0;
			for (int w = 1; w <= MaxWidth; w++)
			{
				if (!PitWidthAt(isSuperdeep, x, z, w))
				{
					break;
				}
				best = w;
			}
			return best;
		}

		/// <summary>The trap predicate, given everything already read off the grid.</summary>
		public static bool Held(bool ruleOn, bool onSuperdeep, bool factionCaptured, bool flying,
			bool ladderUsableHere, bool wideEnough)
		{
			return ruleOn && onSuperdeep && factionCaptured && !flying && !ladderUsableHere && wideEnough;
		}

		/// <summary>A descent INTO a pit: the previous cell was shallower and this one is D = 4.
		/// Moving along a D = 4 floor is not a descent; climbing out is not one.</summary>
		public static bool IsPitDescent(int fromDepth, int toDepth)
		{
			return toDepth >= Superdeep && fromDepth < Superdeep;
		}

		/// <summary>A held pawn may step only to another D = 4 cell.</summary>
		public static bool StepBlocked(bool heldHere, int toDepth)
		{
			return heldHere && toDepth < Superdeep;
		}

		/// <summary>Mass-scaled blunt fall damage, at least 1.</summary>
		public static float FallDamage(float massKg, float multiplier)
		{
			return Math.Max(1f, massKg * FallDamagePerMassKg * multiplier);
		}

		/// <summary>CANAL_BOTTOM_SPIKES_1 — PROPOSED numbers, owner's word owed (the item says
		/// "propose the number with the reasoning shown"). A spiked floor is several points, not
		/// one, so the descent lands SpikeHits Sharp (Stab) hits, each through the normal armour
		/// pipeline. The total scales with body size (owner [G]): 40 per unit of BodySize. A human
		/// (1.0) takes 3 stabs of ~13: several real wounds and bleeding, not an instant kill
		/// (torso 40 HP, armour applies). A muffalo (2.4) takes ~96 across 3 hits, a thrumbo (4)
		/// ~160. Reference point: the retired building pit's spikeDamage 25 Stab, one hit, flat.</summary>
		public const int SpikeHits = 3;

		public const float SpikeDamagePerBodySize = 40f;

		/// <summary>Damage of ONE spike hit: max(1, bodySize x 40 x multiplier / 3).</summary>
		public static float SpikeDamagePerHit(float bodySize, float multiplier)
		{
			float b = bodySize > 0f ? bodySize : 0f;
			float m = multiplier > 0f ? multiplier : 0f;
			return Math.Max(1f, b * SpikeDamagePerBodySize * m / SpikeHits);
		}
	}
}
