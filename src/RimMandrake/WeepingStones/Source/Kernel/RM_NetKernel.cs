// Verse-free kernel of the NET throw (RM_JobDriver_NetPoolBreeder / RM_Projectile_PoolNet).
// WEEPINGSTONES_NET_TARGET_FLEES_1, owner 2026-10-07: "It's supposed to depend on how fast they are. Whether the net can
// hit the right place." Capture is a thrown projectile, not a channel: the net flies on vanilla Projectile flight
// (Verse/Projectile.cs: ticksToImpact = |origin - destination| / SpeedTilesPerTick, destination fixed at launch) to the
// cell the handler aimed at, and it takes the target only if the target is still under it when it lands. Speed matters
// because a fast animal is somewhere else by then; aim matters through vanilla's ShotReport.HitFactorFromShooter.
// SelfTest/WeepingStonesFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.WeepingStones
{
	public static class RM_NetKernel
	{
		/// <summary>The net's spread around its landing cell, in cells. 1.0 = the landing cell and its four cardinal
		/// neighbours (a ~2 m net). INVENTED; the projectile def can override it through its own field.</summary>
		public const float DefaultNetRadius = 1.0f;

		/// <summary>A missed aim lands at least this far from the target's cell - beyond the net's spread, so a bad
		/// throw is a real miss rather than a near-hit the spread forgives.</summary>
		public const int MissOffsetMin = 2;

		public const int MissOffsetMax = 3;

		/// <summary>Did a net landing at (lx,lz) cover a target standing at (tx,tz)? Horizontal distance, inclusive.</summary>
		public static bool NetCovers(int tx, int tz, int lx, int lz, float radius)
		{
			int dx = tx - lx, dz = tz - lz;
			return dx * dx + dz * dz <= radius * radius;
		}

		/// <summary>Vanilla Projectile flight time: ceil(distance / SpeedTilesPerTick), at least 1 tick.
		/// SpeedTilesPerTick is ProjectileProperties.speed / 100.</summary>
		public static int FlightTicks(float distance, float speed)
		{
			float perTick = speed / 100f;
			if (perTick <= 0f) return int.MaxValue;
			int t = (int)Math.Ceiling(distance / perTick);
			return t < 1 ? 1 : t;
		}

		/// <summary>Can a target moving straight away at <paramref name="cellsPerTick"/> still be under the net when it
		/// lands? The analytic form of what the projectile decides cell by cell; used by the selftest as the oracle.</summary>
		public static bool OutrunsNet(float cellsPerTick, int flightTicks, float radius)
		{
			return cellsPerTick * flightTicks > radius;
		}

		public static bool InThrowRange(float distance, float range)
		{
			return distance <= range;
		}
	}
}
