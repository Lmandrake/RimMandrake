// Pure flight policy of jawa/pawn_flight, with no RimWorld or Unity reference, so that
// src/RimMandrake/bridgetools/selftest_order_wait.py compiles it into a plain .NET 8 harness.
// Boundary page: design/specs/2026-11-24-bridge-order-waits/boundary.md (flight-maintain-holds-started).

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchFlightCore
    {
        // Pawn_FlightTracker.FlightState is a private nested enum. Its values, read from source:
        internal const int Grounded = 0;
        internal const int Flying = 1;
        internal const int TakingOff = 2;
        internal const int Landing = 3;

        /// <summary>Whether the maintain window holds this pawn aloft after the action.
        /// Only a pawn that this call left airborne without a refusal is held. StartFlying()
        /// leaves the pawn in TakingOff, and FlightTick moves it to Flying 50 ticks later.
        /// A refused pawn, a grounded pawn and a pawn that is landing are never held.</summary>
        internal static bool HoldInWindow(bool hasTracker, bool refused, int stateAfter)
        {
            return hasTracker && !refused && (stateAfter == Flying || stateAfter == TakingOff);
        }
    }
}
