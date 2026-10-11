// JawaBenchTpsTierTools.cs - the bridge tools of the TPS record's test tier (telemetry design P2). Mechanism and row
// shapes: JawaBenchTpsTier.cs and JawaBenchTpsTierCore.cs. Same instance-[Tool] type as the TPS report, so the tools
// register with the sampler at game load.

using System;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using C = JawaBench.BridgeTools.JawaBenchTpsTierCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTpsTools
    {
        [Tool(
            "jawa/telemetry_tier",
            Description =
                "Arm or disarm the TPS record's TEST TIER for one test. tier=test: 1 s sample windows (5 s otherwise) carrying " +
                "a tick-duration histogram (hist, histV), log error/warning counts ahead of the 10,000-message cap (exc) and " +
                "bridge main-thread occupancy (br); a per-tick flight ring dumped to tps/flight/*.jsonl.gz on an incident, a " +
                "tick over 250 ms, more than 50 log calls in a window, a telemetry mark with dump=true, or disarm (one dump per " +
                "30 s). Auto-disarms after ttl_min (default 60, cap 240) and whenever the companion profile is campaign. " +
                "Calling tier=test again renews the TTL. tier=campaign disarms now. Writes a marker row at arm and disarm. " +
                "Per-tick data needs TPS attribution on. Test profile only: overhead is UNMEASURED until the MUST 17 A/B runs.",
            ResultDescription =
                "success, tier, armedUtc, minutesLeft, windowSeconds, t0 {on, histogram, flight, ticksRecorded, ringTicks}, " +
                "flight {dumps, suppressed, last, lastStatus}, exc {on, total, firstSights, hooks}, bridge {on, hooks}, error.")]
        public Task<object> TelemetryTier(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "test = arm (or renew), campaign = disarm.", DefaultValue = "test")] string tier = "test",
            [ToolParameter(Description = "Minutes until the tier disarms itself (default 60, max 240).", DefaultValue = 60)] double ttl_min = 60,
            [ToolParameter(Description = "Why: the test this tier is armed for (written to the marker row).")] string why = null)
        {
            string t = (tier ?? "").Trim().ToLowerInvariant();
            if (t != C.TierTest && t != C.TierCampaign)
                return Task.FromResult<object>(new { success = false, error = "tier must be 'test' or 'campaign', got '" + tier + "'" });
            return ctx.MainThread.InvokeAsync<object>(() =>
                t == C.TierTest ? JawaBenchTpsTier.Arm(ttl_min, "bridge", why) : JawaBenchTpsTier.Disarm("tool"), cancellationToken);
        }

        [Tool(
            "jawa/telemetry_mark",
            Description =
                "Write a marker row (kind marker, mark=true, with the current tier) into the TPS record, so a test step can be " +
                "found on the timeline. dump=true also asks for a flight-recorder dump of the last 8,192 ticks; that only " +
                "happens while the test tier is armed and at most once per 30 s (the reply says fired, rate-limited, " +
                "not-armed, flight-off or empty).",
            ResultDescription = "success, seq (-1 = the writer dropped the row), tier, dump (status or null).")]
        public Task<object> TelemetryMark(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "What is happening at this moment of the test.")] string why = null,
            [ToolParameter(Description = "Also dump the flight ring (test tier only).", DefaultValue = false)] bool dump = false)
        {
            return ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (!JawaBenchTpsSampler.Installed || !W.Running)
                    return new { success = false, seq = -1L, tier = JawaBenchTpsTier.TierName, dump = (string)null, error = "TPS sampler not running" };
                long seq = W.Enqueue("marker", "\"why\":" + W.Json(why ?? "mark") + ",\"mark\":true,\"tier\":" + W.Json(JawaBenchTpsTier.TierName));
                string d = dump ? JawaBenchTpsTier.Dump(C.TrigMark) : null;
                return (object)new { success = seq >= 0, seq, tier = JawaBenchTpsTier.TierName, dump = d, error = seq < 0 ? "writer dropped the marker row" : null };
            }, cancellationToken);
        }
    }
}
