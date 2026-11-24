using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static async Task<(int ticks, bool pausedDuringWait, string waitEnded, int polls, int elapsedMs)>
            WaitForGameTicks(IRimBridgeContext ctx, CancellationToken cancellationToken, int startTicks,
                int waitTicks, int timeoutSeconds, bool speedChanged = false, Func<int> pendingPawns = null,
                Action onPoll = null, int pollMs = 100, Stopwatch clock = null)
        {
            (int ticks, bool paused, int? pending) Read()
            {
                var tm = Current.Game != null ? Find.TickManager : null;
                return (tm?.TicksGame ?? -1, tm?.Paused ?? false, pendingPawns?.Invoke());
            }

            var sample = await ctx.MainThread.InvokeAsync(() => Read(), cancellationToken).ConfigureAwait(false);
            var previous = sample;
            var pausedDuringWait = sample.paused;
            var polls = 0;
            var elapsedMs = 0;
            while (true)
            {
                cancellationToken.ThrowIfCancellationRequested();
                // The first sample can detect arrival or seed pause detection. The existing
                // tick wait counts only delayed polls, and waitTicks=0 reports the setup tick.
                var ticks = polls == 0 ? startTicks : sample.ticks;
                var pausedAtSameTick = polls > 0 && previous.paused && previous.ticks == sample.ticks;
                var timedOut = polls > 0 && (clock?.ElapsedMilliseconds ?? elapsedMs) >= timeoutSeconds * 1000;
                var end = JawaBenchWaitCore.End(ticks - startTicks, waitTicks, timedOut,
                    speedChanged, sample.paused, pausedAtSameTick, sample.pending);
                if (end != null) return (ticks, pausedDuringWait, end, polls, elapsedMs);

                await Task.Delay(pollMs, cancellationToken).ConfigureAwait(false);
                elapsedMs += pollMs;
                polls++;
                previous = sample;
                sample = await ctx.MainThread.InvokeAsync(() =>
                {
                    onPoll?.Invoke();
                    return Read();
                }, cancellationToken).ConfigureAwait(false);
                pausedDuringWait |= sample.paused;
            }
        }
    }
}
