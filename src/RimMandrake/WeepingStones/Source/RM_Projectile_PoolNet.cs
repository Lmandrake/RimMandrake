using RimWorld;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// WEEPINGSTONES_NET_TARGET_FLEES_1. The thrown net. Flight, arc, shields and the landing cell are vanilla
	/// <see cref="Projectile"/>, unchanged: the handler aims at a CELL (usedTarget), the destination is fixed at launch,
	/// and the flight takes |origin - destination| / SpeedTilesPerTick ticks. Launched with
	/// <see cref="ProjectileHitFlags.None"/>, so vanilla's en-route intercept skips every pawn and wall (the net is
	/// lobbed; the driver only throws with line of sight).
	///
	/// The one override is the landing: vanilla's ImpactSomething rolls 0.5 x bodySize for whatever stands in the
	/// destination cell; a net instead takes the intended target if it is still within the net's spread
	/// (<see cref="RM_NetKernel.NetCovers"/>) when it lands - so a target fast enough to leave in the flight time is
	/// missed, which is the owner's ruling (2026-10-07: "It's supposed to depend on how fast they are. Whether the net
	/// can hit the right place."). A covered target is entangled: stunned (vanilla StunHandler) for
	/// <see cref="NetHoldTicks"/> and marked netted for the handler to bag. No damage, so no vanilla revenge roll.
	/// </summary>
	public class RM_Projectile_PoolNet : Projectile
	{
		/// <summary>How long a netted animal stays entangled. INVENTED: enough for a handler at full throw range to
		/// walk over and bag it.</summary>
		public const int NetHoldTicks = 600;

		protected override void ImpactSomething()
		{
			Pawn target = intendedTarget.Thing as Pawn;
			IntVec3 land = Position;
			bool covered = target != null && target.Spawned && !target.Dead && target.Map == Map
				&& RM_NetKernel.NetCovers(target.Position.x, target.Position.z, land.x, land.z, RM_NetKernel.DefaultNetRadius);
			if (covered)
			{
				target.stances?.stunner?.StunFor(NetHoldTicks, launcher, false, true);
				RM_PoolBreederUtility.MarkNetted(target, NetHoldTicks);
				Impact(target);
				return;
			}
			Impact(null);
		}
	}
}
