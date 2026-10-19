using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS — owner 2026-10-18, verbatim: <i>"Two ladders: one permanent that you install on
	/// a wall that raises and lowers to open and close access (prisoner logic). Also a personally carriable ladder placed into
	/// the pit (if not too deep) to allow entrance/exit, easily retrieved or moved. Climbing gear a pawn has that allows them to
	/// scale. ... Then jump packs and other leaping abilities allow entrance/exit immediately, and teleportation, etc."</i>
	/// Pit rescue (owner by card, 2026-10-18): <i>"any colonist who can climb back out goes; if nobody can, a ladder job is
	/// queued first."</i>
	///
	/// The pure half (no Verse; selftested in SelfTest/PitAccessChecks.cs). The Verse half: RM_LadderUtility (both ladder defs,
	/// the portable ladder's reach), RM_PocketGrid.ClimbLimitOf (climbing gear), RM_PitPathing / RM_PitAccess (jumps and skips
	/// land without a fall), RM_PitRescueLadder (the queued ladder job).
	/// </summary>
	public static class RM_PitAccessMath
	{
		/// <summary>A climb limit no band answers for: RM_PocketGridMath.BandFor returns 0 for it, which every trap, mask, step
		/// floor and reachability read already treats as "climbs every step there is". Climbing gear's climb limit.</summary>
		public const int ScalesAnyWall = RM_PitTrapMath.ClimbBands;

		/// <summary>Does a ladder that reaches <paramref name="maxLevels"/> levels (0 = any depth: the fixed wall ladder) span
		/// the drop from its own square (depth <paramref name="cellD"/>) to the wall square it hangs on (<paramref name="wallD"/>)?
		/// A ladder whose wall is no shallower reaches nothing.</summary>
		public static bool LadderReaches(int cellD, int wallD, int maxLevels)
		{
			int drop = cellD - wallD;
			if (drop <= 0)
			{
				return false;
			}
			return maxLevels <= 0 || drop <= maxLevels;
		}

		/// <summary>The climb limit with climbing gear: worn and the setting on, any wall; else the creature's own.</summary>
		public static int ClimbLimitWithGear(int naturalK, bool wearsGear, bool gearEnabled)
		{
			return wearsGear && gearEnabled ? ScalesAnyWall : naturalK;
		}

		/// <summary>A walked step a gear-wearer takes ON THE GEAR (slowly, per level, like a ladder): one taller than it climbs
		/// unaided. Steps it would climb anyway cost what they always did.</summary>
		public static bool StepOnGear(int fromD, int toD, int naturalK, bool wearsGear)
		{
			return wearsGear && Math.Abs(fromD - toD) > Math.Max(1, naturalK);
		}

		/// <summary>A landing that never falls: a deliberate jump (a flyer with no stun: jump packs, longjump, leaping abilities)
		/// or a teleport (skip), each under its own setting. A throw (a stun flyer: blast knockback) still falls.</summary>
		public static bool LandsSafely(bool deliberateJump, bool jumpSafeOn, bool teleport, bool teleportSafeOn)
		{
			return (deliberateJump && jumpSafeOn) || (teleport && teleportSafeOn);
		}

		public enum RescueLadder
		{
			None,
			/// <summary>Carry a portable ladder that is lying about to the wall and set it there (an install job).</summary>
			InstallPortable,
			/// <summary>Build a new portable ladder there.</summary>
			BuildPortable,
			/// <summary>The drop is past a portable ladder's reach: build the fixed wall ladder.</summary>
			BuildFixed,
		}

		/// <summary>The owner's rescue order: someone who can climb back out goes (vanilla's rescue, which our reachability
		/// already limits to those who can); only when NOBODY can, and no ladder job is already pending in that pit, is a ladder
		/// job queued, the cheapest that reaches: a spare portable ladder, a new portable one, else the fixed ladder.</summary>
		public static RescueLadder ChooseRescueLadder(bool needsHelp, bool anyoneCanReach, bool ladderPending, int drop,
			int portableReach, bool spareMinified, bool portableEnabled)
		{
			if (!needsHelp || anyoneCanReach || ladderPending || drop <= 0)
			{
				return RescueLadder.None;
			}
			if (portableEnabled && LadderReaches(drop, 0, portableReach))
			{
				return spareMinified ? RescueLadder.InstallPortable : RescueLadder.BuildPortable;
			}
			return RescueLadder.BuildFixed;
		}
	}
}
