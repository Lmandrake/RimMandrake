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

		/// <summary>Ticks to climb over one wall square at speed 1 and a normal walking speed: 5 s, about the time a person
		/// walks 23 squares. Slow, per the ruling, and a raider halfway over is a target.</summary>
		public const int BaseTicksPerSquare = 300;

		/// <summary>A person's MoveSpeed in vanilla (cells/s). A slower walker climbs slower, a faster one faster (capped).</summary>
		public const float NormalMoveSpeed = 4.6f;

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

		/// <summary>Ticks the climb takes: per wall square, BaseTicksPerSquare over the speed setting, scaled by how fast the
		/// pawn walks against a person (between half and double), never under 60.</summary>
		public static int ClimbTicks(int wallSquares, float speedSetting, float moveSpeed)
		{
			float speed = Math.Max(0.1f, speedSetting);
			float walk = moveSpeed <= 0f ? 1f : Math.Max(0.5f, Math.Min(2f, moveSpeed / NormalMoveSpeed));
			int ticks = (int)Math.Round(Math.Max(1, wallSquares) * BaseTicksPerSquare / (speed * walk));
			return Math.Max(60, ticks);
		}
	}
}
