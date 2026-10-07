using System;
using System.Collections.Generic;

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

		// ── FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner, 2026-10-06): who falls ─────────
		// "You can't fall in by careless colonist pathing. Only if they get blown/forced in do they
		// fall. Enemies can fall if the pit is concealed or they are forced/blown in."

		/// <summary>Does this descent into an (uncovered) D = 4 cell count as a FALL (fall damage,
		/// spikes)? <paramref name="walkedStep"/> = the pawn's own path follower stepped it there;
		/// anything else (skip/teleport, a flyer landing, the jump gizmo, a mod's push) is forced.
		/// Covered cells never reach here: a cover is ground until it gives way, and giving way is
		/// its own fall route (Building_PitCover).</summary>
		public static bool DescentFalls(bool walkedStep, bool ontoUsableLadder, bool playerFaction, bool captured)
		{
			if (!walkedStep)
			{
				return true;
			}
			if (ontoUsableLadder)
			{
				return false; // climbing down a lowered ladder
			}
			// A walked step into an open pit is pathing; pathing avoids open pits (RM_PitPathing),
			// so this is a stale route. Never a colonist's fall; for anyone the hole captures it
			// keeps the old ruling-26 rule.
			return !playerFaction && captured;
		}

		/// <summary>The legs RM_PitPathing can ask the path follower for.</summary>
		public enum PitLeg
		{
			/// <summary>Vanilla request, no customizer.</summary>
			Vanilla,
			/// <summary>To the real destination, open pit cells impassable.</summary>
			AvoidPits,
			/// <summary>To the real destination, everything but this pit impassable.</summary>
			StayInPit,
			/// <summary>One step to (x, z), no customizer (onto a ladder, or up onto the lip).</summary>
			StepTo,
			/// <summary>To (x, z), open pit cells impassable (the lip beside a ladder).</summary>
			WalkToAvoidPits,
			/// <summary>To (x, z) inside the pit, everything but the pit impassable (to the way out).</summary>
			WalkToInPit,
		}

		public struct PitRoute
		{
			public PitLeg leg;
			public int x;
			public int z;

			public PitRoute(PitLeg leg, int x = 0, int z = 0)
			{
				this.leg = leg;
				this.x = x;
				this.z = z;
			}
		}

		private static readonly int[] Dx8 = { 0, 1, 0, -1, 1, 1, -1, -1 };
		private static readonly int[] Dz8 = { 1, 0, -1, 0, 1, -1, -1, 1 };

		/// <summary>The 8-connected open-pit component containing (x, z), in BFS order from it.
		/// Empty if (x, z) is not an open pit cell. Capped at maxCells.</summary>
		public static List<(int, int)> PitComponent(Func<int, int, bool> isPit, int x, int z, int maxCells)
		{
			var order = new List<(int, int)>();
			if (!isPit(x, z))
			{
				return order;
			}
			var seen = new HashSet<(int, int)> { (x, z) };
			order.Add((x, z));
			for (int i = 0; i < order.Count && order.Count < maxCells; i++)
			{
				(int cx, int cz) = order[i];
				for (int k = 0; k < 8; k++)
				{
					var n = (cx + Dx8[k], cz + Dz8[k]);
					if (!seen.Contains(n) && isPit(n.Item1, n.Item2))
					{
						seen.Add(n);
						order.Add(n);
					}
				}
			}
			return order;
		}

		private static bool BestLip(Func<int, int, bool> isPit, Func<int, int, bool> lipStandable, int x, int z,
			int towardX, int towardZ, out int lx, out int lz)
		{
			lx = lz = 0;
			long best = long.MaxValue;
			for (int k = 0; k < 8; k++)
			{
				int nx = x + Dx8[k], nz = z + Dz8[k];
				if (isPit(nx, nz) || !lipStandable(nx, nz))
				{
					continue;
				}
				long d = (long)(nx - towardX) * (nx - towardX) + (long)(nz - towardZ) * (nz - towardZ);
				if (d < best)
				{
					best = d;
					lx = nx;
					lz = nz;
				}
			}
			return best != long.MaxValue;
		}

		/// <summary>
		/// LADDER FIX (pit_escape live FAIL 2026-10-06) + FLOWWORKS_PIT_FALL_ONLY_FORCED_1. Which leg the
		/// path follower should request from start s toward destination d.
		///
		/// The vanilla pathfinder knows nothing of the trap: a D = 4 cell costs 300, so its shortest
		/// route out of a pit leaves over the NEAREST lip, never via the ladder, and from a held cell
		/// that step is vetoed by the per-move floor (StepBlocked) — the pawn never leaves. And from
		/// outside, a 300-cost hole is still crossable "by careless pathing". So:
		///   • outside → open pits are impassable (AvoidPits); a destination that needs the pit floor is
		///     reached only down a ladder this pawn may climb (lip beside it, then one step onto it);
		///   • inside, held → walk INSIDE the pit to the nearest cell that lets it out and touches the lip
		///     (WalkToInPit), then step up onto the lip (StepTo);
		///   • inside, on such an exit cell, where this pit holds the pawn elsewhere → StepTo the lip;
		///   • inside, destination in the same pit → StayInPit (never out over the lip and back in).
		/// isPit = uncovered D = 4; heldAt = the full trap predicate for this pawn; ladderFor = a ladder
		/// this pawn may climb stands there; lipStandable = walkable ground.
		/// </summary>
		public static PitRoute PlanRoute(Func<int, int, bool> isPit, Func<int, int, bool> heldAt,
			Func<int, int, bool> ladderFor, Func<int, int, bool> lipStandable,
			int sx, int sz, int dx, int dz, bool destNeedsPit, int maxCells)
		{
			if (!isPit(sx, sz))
			{
				if (!destNeedsPit)
				{
					return new PitRoute(PitLeg.AvoidPits);
				}
				// Down a ladder or not at all.
				List<(int, int)> destComp = PitComponent(isPit, dx, dz, maxCells);
				long best = long.MaxValue;
				(int, int) ladder = (0, 0);
				foreach ((int x, int z) c in destComp)
				{
					if (!ladderFor(c.x, c.z))
					{
						continue;
					}
					long d = (long)(c.x - sx) * (c.x - sx) + (long)(c.z - sz) * (c.z - sz);
					if (d < best)
					{
						best = d;
						ladder = c;
					}
				}
				if (best == long.MaxValue)
				{
					return new PitRoute(PitLeg.AvoidPits); // no way down: the pathfinder refuses
				}
				if (Math.Abs(ladder.Item1 - sx) <= 1 && Math.Abs(ladder.Item2 - sz) <= 1)
				{
					return new PitRoute(PitLeg.StepTo, ladder.Item1, ladder.Item2);
				}
				if (BestLip(isPit, lipStandable, ladder.Item1, ladder.Item2, sx, sz, out int lx, out int lz))
				{
					return new PitRoute(PitLeg.WalkToAvoidPits, lx, lz);
				}
				return new PitRoute(PitLeg.AvoidPits);
			}

			List<(int, int)> comp = PitComponent(isPit, sx, sz, maxCells);
			if (destNeedsPit && comp.Contains((dx, dz)))
			{
				return new PitRoute(PitLeg.StayInPit);
			}
			bool anyHeld = false;
			foreach ((int x, int z) c in comp)
			{
				if (heldAt(c.x, c.z))
				{
					anyHeld = true;
					break;
				}
			}
			if (!anyHeld)
			{
				return new PitRoute(PitLeg.Vanilla); // this pit does not hold this pawn anywhere
			}
			// Nearest (BFS order) cell that is not held and touches the lip: the way out.
			foreach ((int x, int z) c in comp)
			{
				if (heldAt(c.x, c.z))
				{
					continue;
				}
				if (!BestLip(isPit, lipStandable, c.x, c.z, dx, dz, out int lx, out int lz))
				{
					continue;
				}
				if (c.x == sx && c.z == sz)
				{
					return new PitRoute(PitLeg.StepTo, lx, lz);
				}
				return new PitRoute(PitLeg.WalkToInPit, c.x, c.z);
			}
			return new PitRoute(PitLeg.Vanilla); // trapped: reachability already vetoes
		}

		/// <summary>FLOWWORKS_LADDER_RAISE_LOWER_1 + LADDER_PRISON_DOOR_1: may this pawn climb this ladder (either
		/// way)? A RAISED ladder is climbed by nobody while the raise/lower setting is on; a lowered one follows the
		/// prison-door rule (<paramref name="mayClimb"/>) while that setting is on, else anyone climbs it.</summary>
		public static bool LadderUsable(bool raiseLowerOn, bool raised, bool prisonDoorOn, bool mayClimb)
		{
			if (raiseLowerOn && raised)
			{
				return false;
			}
			return !prisonDoorOn || mayClimb;
		}

		/// <summary>FLOWWORKS_LADDER_RAISE_LOWER_1: from OUTSIDE the pit, can a pawn get down onto the floor cell
		/// (dx, dz) at all? Only down a ladder it may climb that stands in that cell's open-pit component with
		/// walkable ground beside it — the same test PlanRoute's "down a ladder or not at all" leg makes, so the
		/// reachability veto and the pather never disagree (a hauler is not offered an item it cannot path to).</summary>
		public static bool PitFloorEnterable(Func<int, int, bool> isPit, Func<int, int, bool> ladderFor,
			Func<int, int, bool> lipStandable, int dx, int dz, int maxCells)
		{
			foreach ((int x, int z) c in PitComponent(isPit, dx, dz, maxCells))
			{
				if (ladderFor(c.x, c.z) && BestLip(isPit, lipStandable, c.x, c.z, c.x, c.z, out _, out _))
				{
					return true;
				}
			}
			return false;
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

		/// <summary>FLOWWORKS_DOOR_FAMILY_1 — does a sluice / security grate open for this pawn?
		/// A pawn held in a superdeep pit never opens one (the pit spec's door rule) while that
		/// setting is on; otherwise vanilla decides, except that a SLUICE (holds small creatures only)
		/// also gives way to any non-player humanlike or anything wider than a one-wide pit holds
		/// (requiredWidth &gt; 1, the owner's Q4 "small").</summary>
		public static bool FlowDoorOpens(bool vanillaOpens, bool heldInPit, bool sealedFromPitRule,
			bool isSluice, bool sluiceRule, bool playerFaction, bool humanlike, int requiredWidth)
		{
			if (sealedFromPitRule && heldInPit)
			{
				return false;
			}
			if (vanillaOpens)
			{
				return true;
			}
			return isSluice && sluiceRule && !playerFaction && (humanlike || requiredWidth > 1);
		}

		/// <summary>FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 9 (owner, 2026-10-06: <i>"people stuck inside a pit do NOT walk
		/// slowly... they walk at normal speed. Only when they are climbing in or out do they move slowly. Falling into a
		/// pit is FAST. Walking around within the pit is normal."</i>). The terrain base cost of one step between two
		/// DRY cells: 0 (normal walking) between equal depths, 0 for a drop INTO a superdeep cell (a fall), otherwise
		/// <paramref name="climbCost"/> (the deeper cell's dry path cost: climbing in or out, ladder included).</summary>
		public static int DryStepBaseCost(int fromDepth, int toDepth, int climbCost)
		{
			if (fromDepth == toDepth)
			{
				return 0;
			}
			if (toDepth >= Superdeep && toDepth > fromDepth)
			{
				return 0;
			}
			return climbCost < 0 ? 0 : climbCost;
		}
	}
}
