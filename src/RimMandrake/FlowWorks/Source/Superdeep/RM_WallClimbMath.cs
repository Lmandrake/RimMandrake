using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS — owner 2026-10-18: climbing gear <i>"should allow pawns to scale walls (unroofed on
	/// both sides) just as easily as canal sides, albeit slowly"</i>; by card the same day: built walls too, for everyone
	/// wearing the gear (colonists AND raiders), both directions, slowly; and the gear is <i>"a "belt/backpack" type item of
	/// ropes, little grappling hooks, climbing claws, etc. all together in "climbing gear" item."</i>
	///
	/// The pure half (no Verse; selftested in SelfTest/WallClimbChecks.cs). The Verse half is RM_WallClimb.cs: which things
	/// are walls (read from the def's flags, never a name list), the climb job, and the seams where a gear-wearer climbs
	/// instead of bashing (sappers, breachers, a blocked path, a raider with no way in) or is ordered over (the float menu).
	/// A climb never changes pathing or regions: the pawn walks to the foot of the wall by an ordinary path, spends the climb
	/// there, and is set down on the far side, so reachability and the pathfinder never disagree.
	/// </summary>
	public static class RM_WallClimbMath
	{
		/// <summary>The thickest run of wall squares one climb crosses (a double wall is two).</summary>
		public const int MaxWallSquares = 2;

		/// <summary>Owner 2026-10-18 by card: <i>"They can route when shorter, but climbing should be SLOOOWW. Like x20 slow, so
		/// it's not something you do routinely."</i> One wall square takes this many of the pawn's own walking steps (the
		/// setting's default).</summary>
		public const float DefaultSlowFactor = 20f;

		/// <summary>A person's ticks per cardinal step in vanilla (MoveSpeed 4.6 cells/s): 60 / 4.6.</summary>
		public const float PersonTicksPerCell = 13f;

		/// <summary>The route planner's price of one wall square must stay under the pathfinder's 10000 "impassable".</summary>
		public const int MaxStepCost = 9000;

		/// <summary>A built thing that blocks movement and may be climbed: an impassable wall or fence. Never a door (it
		/// opens), never mineable or natural rock (that is a cliff, not a built wall), never anything not flagged as a wall or
		/// fence (a machine is not scaled).</summary>
		public static bool IsClimbableWallKind(bool impassable, bool isDoor, bool mineable, bool naturalRock, bool isWall,
			bool isFence)
		{
			return impassable && !isDoor && !mineable && !naturalRock && (isWall || isFence);
		}

		/// <summary>May this pawn climb walls at all: gear worn, both the gear and the wall setting on, and, for anyone not
		/// the player's, "raiders may climb" on.</summary>
		public static bool MayClimb(bool wearsGear, bool gearEnabled, bool wallClimbEnabled, bool playerSide,
			bool raidersMayClimb)
		{
			return wearsGear && gearEnabled && wallClimbEnabled && (playerSide || raidersMayClimb);
		}

		/// <summary>The crossing is open: 1..MaxWallSquares wall squares, none roofed, and the squares on both sides (where the
		/// climb starts and where it lands) standable and unroofed.</summary>
		public static bool CrossingOpen(int wallSquares, bool anyWallRoofed, bool fromRoofed, bool toRoofed,
			bool fromStandable, bool toStandable)
		{
			return wallSquares >= 1 && wallSquares <= MaxWallSquares && !anyWallRoofed && !fromRoofed && !toRoofed
				&& fromStandable && toStandable;
		}

		/// <summary>Ticks the climb takes: per wall square, <paramref name="slowFactor"/> of the pawn's own steps
		/// (<paramref name="ticksPerCell"/>, its TicksPerMoveCardinal; a person's when unknown), never under 60. The same number
		/// is what the route planner charges for the square, so "shorter" means "sooner".</summary>
		public static int ClimbTicks(int wallSquares, float slowFactor, float ticksPerCell)
		{
			return Math.Max(60, Math.Max(1, wallSquares) * StepCost(slowFactor, ticksPerCell));
		}

		/// <summary>The planner's (and the climb's) price of one wall square, in ticks: slowFactor steps of this pawn,
		/// between 1 and MaxStepCost.</summary>
		public static int StepCost(float slowFactor, float ticksPerCell)
		{
			float step = ticksPerCell > 0f ? ticksPerCell : PersonTicksPerCell;
			int cost = (int)Math.Round(Math.Max(1f, slowFactor) * step);
			return Math.Max(1, Math.Min(MaxStepCost, cost));
		}

		/// <summary>Climb instead of walking round: the through-the-wall route (its whole cost, climb included) is cheaper
		/// than the ordinary route, or there is no ordinary route.</summary>
		public static bool ClimbIsShorter(bool normalFound, float normalCost, bool climbFound, float climbCost)
		{
			return climbFound && climbCost >= 0f && (!normalFound || climbCost < normalCost);
		}

		/// <summary>Chance a generated pawn carries climbing gear (owner 2026-10-18 by card: <i>"Wildsteam should have this.
		/// Junkers and Blackstar should. Jawa should. Deep Desert tribes yes. Then breachers and sappers from anyone."</i>): the
		/// highest of its kind's and its faction's own chance, and the breacher/sapper chance when the kind is one, times the
		/// scale setting, clamped to 0..1. Nothing for the player's own, or when the setting is off.</summary>
		public static float GearChance(float kindChance, float factionChance, bool breacherOrSapper, float breacherSapperChance,
			float scale, bool enabled, bool playerFaction)
		{
			if (!enabled || playerFaction)
			{
				return 0f;
			}
			float c = Math.Max(Math.Max(kindChance, factionChance), breacherOrSapper ? breacherSapperChance : 0f);
			return Math.Max(0f, Math.Min(1f, c * Math.Max(0f, scale)));
		}
	}
}
