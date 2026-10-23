using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LADDER_PARITY_BUILD_NO_KEYS_REQUIRED — owner by card 2026-10-23, option (4) "Full parity both ways", his words: <i>"It's
	/// (4). We need a way to repair damage caused by people digging their way into a pit. Digging should be slow. Building
	/// ladders available to both sides on demand. Both sides should be able to use each other's ladders: makes NO sense
	/// otherwise (what are they locked with a key?). Can pick up each other's ladders too and move them. Raiders should show up
	/// with ladders sometimes but not always, and certainly not on every raider. Ladders should work to climb one-way over single
	/// walls without roofs as well."</i> Design: design/RimMandrake/ladder_parity_2026-10-23.md.
	///
	/// The pure half (no Verse; selftested in SelfTest/LadderParityChecks.cs). The Verse half is RM_LadderParity.cs.
	/// </summary>
	public static class RM_LadderParityMath
	{
		/// <summary>"Digging should be slow": the shipped breach-fill speed (PROVISIONAL; it was x1).</summary>
		public const float DefaultRaiderFillSpeed = 0.5f;

		/// <summary>A ladder over a wall: this many of the pawn's own steps (climbing gear is 20). PROVISIONAL.</summary>
		public const float DefaultWallLadderSlowFactor = 4f;

		/// <summary>May this pawn climb a LOWERED ladder (any standing portable ladder, or a lowered wall ladder)? First the
		/// creature must be able to climb one at all (<paramref name="climbEligible"/>: ClimbEligible, owner Q1). No keys: a
		/// lowered ladder is a HELD-OPEN door (owner Q4: "A prison ladder left down is equivalent to a prison door left open...
		/// same game rules apply"): vanilla Building_Door.FreePassage makes CanPhysicallyPass true for every pawn, prisoners and
		/// wild animals included, so every climber climbs it. With <paramref name="noKeys"/> off, the 2026-10-02 prison-door
		/// rule: hostiles and wild things barred, prisoners only in a prison break. (A RAISED wall ladder is nobody's:
		/// RM_PitTrapMath.LadderUsable, unchanged.)</summary>
		public static bool MayClimbLowered(bool noKeys, bool hasFaction, bool isPlayer, bool hostile, bool prisoner,
			bool prisonBreaking, bool climbEligible)
		{
			if (!climbEligible)
			{
				return false;
			}
			if (noKeys)
			{
				return true;
			}
			if (prisoner)
			{
				return prisonBreaking;
			}
			if (!hasFaction)
			{
				return false;
			}
			if (isPlayer)
			{
				return true;
			}
			return !hostile;
		}

		private static uint Hash(int x, uint salt)
		{
			unchecked
			{
				uint h = (uint)x * 2654435761u ^ salt;
				h ^= h >> 16;
				h *= 0x7feb352du;
				h ^= h >> 15;
				h *= 0x846ca68bu;
				h ^= h >> 16;
				return h;
			}
		}

		/// <summary>Owner Q1 2026-10-23: the biggest body that fits a 1x1 ladder (a person is 1.0). PROVISIONAL.</summary>
		public const float DefaultMaxClimberBodySize = 1.2f;

		/// <summary>Owner Q1 2026-10-23, verbatim: <i>"Needs a per-creature evaluation, unfortunately. Many mechs, droids, humans,
		/// animals should be able to climb, jump up alone, or slither along a ladder as long as they fit in a 1x1 cell area.
		/// Bigger things no, wheeled things no, and many creatures without arms no."</i> A per-def override (RM_LadderClimber:
		/// 1 yes, 0 no; -1 none) beats the rule; else: fits (body size at most <paramref name="maxSize"/>), not wheeled, and a
		/// way up: arms (a manipulation limb), a jump, or a body that slithers (no legs).</summary>
		public static bool ClimbEligible(float bodySize, float maxSize, bool wheeled, bool hasArms, bool jumps, bool slithers,
			int overrideClimbs)
		{
			if (overrideClimbs >= 0)
			{
				return overrideClimbs > 0;
			}
			return bodySize <= maxSize && !wheeled && (hasArms || jumps || slithers);
		}

		public enum LadderSource
		{
			None,
			SetCarried,
			Take,
			Build,
			Chop,
		}

		/// <summary>Owner Q2 2026-10-23: <i>"They don't carry wood, they look for something to chop down, get the wood, then
		/// build it. Destructive."</i> A raider's ladder: the one it carries, else one standing to take, else build one from the
		/// wood it has, else go and chop a tree for wood; None: no ladder (breach by fill, or jump).</summary>
		public static LadderSource ChooseLadderSource(bool carries, bool takeable, bool hasWood, bool treeInReach)
		{
			if (carries)
			{
				return LadderSource.SetCarried;
			}
			if (takeable)
			{
				return LadderSource.Take;
			}
			if (hasWood)
			{
				return LadderSource.Build;
			}
			return treeInReach ? LadderSource.Chop : LadderSource.None;
		}

		/// <summary>Ticks to fell a tree as vanilla's JobDriver_PlantWork does: harvestWork spent at PlantWorkSpeed a tick.</summary>
		public static int ChopTicks(float harvestWork, float plantWorkSpeed)
		{
			return (int)Math.Ceiling(Math.Max(1f, harvestWork) / Math.Max(0.1f, plantWorkSpeed));
		}

		/// <summary>"Sometimes but not always": does this raid bring ladders? A stable roll on the raid's seed.</summary>
		public static bool RaidBringsLadders(int raidSeed, float chance)
		{
			if (chance <= 0f)
			{
				return false;
			}
			if (chance >= 1f)
			{
				return true;
			}
			return Hash(raidSeed, 0x1add3du) % 10000u < (uint)(chance * 10000f);
		}

		/// <summary>"Certainly not on every raider": how many of <paramref name="people"/> carry one: the share, rounded, at
		/// least one, never all (a lone raider carries none).</summary>
		public static int CarrierCount(int people, float share)
		{
			if (people < 2 || share <= 0f)
			{
				return 0;
			}
			int n = (int)Math.Round(people * Math.Min(1f, share), MidpointRounding.AwayFromZero);
			return Math.Max(1, Math.Min(n, people - 1));
		}

		/// <summary>The carriers among a raid's pawn ids: the CarrierCount lowest by a stable hash, so list order and a reload
		/// never change who carries.</summary>
		public static List<int> PickCarriers(IList<int> ids, float share)
		{
			int n = CarrierCount(ids?.Count ?? 0, share);
			if (n == 0)
			{
				return new List<int>();
			}
			return ids.OrderBy(i => Hash(i, 0xca771e5u)).ThenBy(i => i).Take(n).ToList();
		}

		/// <summary>Ticks for a raider to put up a ladder: a carried one is SET (4 s + 0.5 s a metre), else one is BUILT on the
		/// spot (RM_RaiderTrenchMath.LadderTicks, the 2026-10-18 time); both divided by the speed setting.</summary>
		public static int RaiderLadderTicks(double metres, float speed, bool carried)
		{
			if (!carried)
			{
				return RM_RaiderTrenchMath.LadderTicks(metres, speed);
			}
			double s = Math.Max(0.1, speed);
			return (int)Math.Ceiling((240.0 + 30.0 * Math.Max(0.0, metres)) / s);
		}

		/// <summary>"Can pick up each other's ladders": may a raider take this standing portable ladder? Only one who carries
		/// none, within <paramref name="radius"/> squares, never a ladder its own crossing stands on, never from under a pawn.</summary>
		public static bool MayTakeLadder(bool settingOn, bool carriesOne, int distSq, int radius, bool ownCrossingUsesIt,
			bool pawnOnIt)
		{
			return settingOn && !carriesOne && distSq <= radius * radius && !ownCrossingUsesIt && !pawnOnIt;
		}

		/// <summary>The breach scar after one more level of fill: the depth before the FIRST fill is kept.</summary>
		public static int ScarAfterFill(int existingScar, int depthBefore)
		{
			return Math.Max(existingScar, depthBefore);
		}

		/// <summary>The dig-to target that repairs a scarred square (its scar depth), or 0 when there is nothing to repair.</summary>
		public static int RepairTarget(int scar, int current)
		{
			return scar > current ? scar : 0;
		}

		/// <summary>A scar is healed once the square is that deep again.</summary>
		public static bool ScarHealed(int scar, int current)
		{
			return current >= scar;
		}

		/// <summary>"One-way over single walls without roofs": a pawn standing on a portable ladder's square, the ladder facing
		/// the wall, climbs over ONE wall square, when the wall and both sides are open (RM_WallClimbMath.CrossingOpen) and the
		/// ladder rule lets this pawn climb it. Back needs a ladder on the other side.</summary>
		public static bool LadderOverWallOpen(bool settingOn, bool ladderAtFoot, bool facesWall, bool ladderUsable, int wallSquares,
			bool anyWallRoofed, bool fromRoofed, bool toRoofed, bool fromStandable, bool toStandable)
		{
			return settingOn && ladderAtFoot && facesWall && ladderUsable && wallSquares == 1
				&& RM_WallClimbMath.CrossingOpen(wallSquares, anyWallRoofed, fromRoofed, toRoofed, fromStandable, toStandable);
		}

		/// <summary>A portable ladder may stand on undug ground only against a single climbable wall it faces.</summary>
		public static bool PlaceOnWall(bool settingOn, bool cellDug, bool facesClimbableWall, int wallSquares)
		{
			return settingOn && !cellDug && facesClimbableWall && wallSquares == 1;
		}

		/// <summary>Ticks to go up and over a wall on a ladder: slowFactor of the pawn's own steps (never under 30).</summary>
		public static int WallClimbTicks(float slowFactor, float ticksPerCell)
		{
			return Math.Max(30, RM_WallClimbMath.StepCost(slowFactor, ticksPerCell));
		}
	}
}
