namespace JawaBench.BridgeTools
{
    internal static class JawaBenchWaitCore
    {
        // Null pendingPawns means there is no arrival condition. A null result means keep polling.
        internal static string End(int ticksElapsed, int waitTicks, bool timedOut, bool speedChanged,
            bool paused, bool pausedAtSameTick, int? pendingPawns = null)
        {
            if (pendingPawns == 0) return "arrived";
            if (ticksElapsed >= waitTicks) return "ticks";
            if (!speedChanged && paused && pausedAtSameTick) return "paused";
            return timedOut ? "timeout" : null;
        }
    }
}
