// JawaBenchHealthTools.cs - jawa/health (status / arm / disarm / switch) and jawa/health_profile
// (status / start / stop). The game-health metrics of design/RimMandrake/game_health_record.md; hooks in
// JawaBenchHealth.cs, profiler in JawaBenchHealthProfiler.cs, pure rules in
// JawaBenchHealthCore.cs (unit-tested offline: src/RimMandrake/Utils/selftest_health_core.py).
//
// Every reading is a status word first (ok | unavailable | failed | off); a value appears only beside "ok".
// Readings are observations side by side; none of them names a cause.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using H = JawaBench.BridgeTools.JawaBenchHealthCore;
using HL = JawaBench.BridgeTools.JawaBenchHealth;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/health",
            Description =
                "Game-health metrics beyond TPS (game_health_record.md): tps.frame-hist (frame-interval histogram, merged per " +
                "window, never averaged p99) and tps.log-counts (messages per type + Verse.Log cap/logger state). NOTHING " +
                "records until action=arm minutes=N (default 30, max 240); disarm makes the hooks inert. action=switch " +
                "metric=<id> on=bool. Each arm starts fresh frame histograms. sinceMinutes merges the retained minute " +
                "windows of that span.",
            ResultDescription = "success, armed, install, switches, frameHist, log, cost.")]
        public static async Task<object> Health(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | arm | disarm | switch", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "arm: minutes (default 30, max 240)", DefaultValue = 30)] double minutes = 30,
            [ToolParameter(Description = "switch: metric id", DefaultValue = null)] string metric = null,
            [ToolParameter(Description = "switch: true = on", DefaultValue = true)] bool on = true,
            [ToolParameter(Description = "status: merge the minute windows that ended in the last N minutes (default 10)", DefaultValue = 10)] double sinceMinutes = 10)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var a = (action ?? "status").Trim().ToLowerInvariant();
                string note = null;
                if (a == "arm") note = HL.ArmNow(minutes, "jawa/health arm");
                else if (a == "disarm") HL.Disarm();
                else if (a == "switch")
                {
                    string id = (metric ?? "").Trim();
                    if (H.MergedIds.TryGetValue(id, out var where)) return Fail(id + " is " + where);
                    if (!HL.Sw.Set(id, on)) return Fail("unknown metric id '" + metric + "'", new { metricIds = H.MetricIds });
                    HL.RefreshFlags();
                }
                else if (a != "status") return Fail("action must be status, arm, disarm or switch");
                if (note != null && !note.StartsWith("armed")) return Fail(note, HealthStatus(sinceMinutes));
                return HealthStatus(sinceMinutes);
            }, cancellationToken).ConfigureAwait(false);
        }

        private static object HealthStatus(double sinceMinutes)
        {
            double f = Stopwatch.Frequency, nowS = HL.NowS;
            double since = double.IsNaN(sinceMinutes) || sinceMinutes <= 0 ? 10 : sinceMinutes;
            var merged = HL.Ring.MergedSince(nowS - since * 60, out int windows, out double fromS);
            merged.Merge(HL.Window, out _);                       // the open window too: a merge, never an average
            string p99Text, p50Text;
            merged.Quantile(0.99, out p99Text); merged.Quantile(0.5, out p50Text);
            var cap = HL.ReadCap();
            var cost = new Dictionary<string, object>();
            foreach (var id in H.MetricIds)
            {
                if (!HL.Meters.TryGetValue(id, out var m)) continue;
                cost[id] = new { calls = m.Calls, meanUsPerCall = m.MeanUs(f).Render(), maxUs = m.MaxUs(f).Render(), totalMs = Math.Round(m.TotalMs(f), 3),
                                 measures = "hook body only; Harmony dispatch excluded" };
            }
            return new
            {
                success = true,
                armed = HL.Live, armedBy = HL.ArmedBy, armedAtUtc = HL.ArmedAtUtc,
                install = new { status = HL.InstallStatus, detail = HL.InstallDetail, settings = HL.SettingsPath, switchNote = HL.Sw.Note },
                switches = HL.Sw.Snapshot(),
                guards = new[] { "{" + HL.GRoot.CoverageFields() + "}" },
                frameHist = new
                {
                    reading = HL.SourceReading(H.MFrameHist).Render(),
                    merged = "{" + "\"windows\":" + windows + ",\"plusOpenWindow\":true,\"hist\":" + merged.Json() + "}",
                    p50 = p50Text, p99 = p99Text,
                    session = HL.Session.Json(),
                    measures = "interval between successive Root.Update prefixes in the same playing game, outside long events (update cadence, NOT displayed FPS)",
                    ringEvicted = HL.Ring.Evicted,
                },
                log = new
                {
                    reading = HL.SourceReading(H.MLogCounts).Render(), state = cap.Word, text = cap.Text, line = H.LogLine(HL.Logs, cap),
                    headroom = cap.Headroom.Render(), capResets = HL.CapResets.Resets, countingSinceUtc = HL.LogCountingSinceUtc,
                    measures = "messages that REACHED Application.logMessageReceivedThreaded; process-scoped, never reset at a game change",
                },
                cost,
                merged = H.MergedIds,
                verdict = "observations only; no cause is established",
            };
        }

        [Tool(
            "jawa/health_profile",
            Description =
                "opt.profiler (game_health_record.md; opt.own-counters is merged into it as preset=own): time an EXACT allowlist " +
                "of methods ('Namespace.Type:Method', separated by ';', max 32, no wildcards, overloads refused) for N minutes " +
                "(default 10, max 60), then it expires. TEST profile only. action=status | start | stop.",
            ResultDescription = "success, status, methods (calls, meanUs, maxUs, totalMs), refused, foreignThreadCalls.")]
        public static async Task<object> HealthProfile(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | start | stop", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "start: 'Ns.Type:Method;Ns.Type:Method'", DefaultValue = null)] string methods = null,
            [ToolParameter(Description = "start: preset (own = our mods' map-component ticks)", DefaultValue = null)] string preset = null,
            [ToolParameter(Description = "start: minutes (default 10, max 60)", DefaultValue = 10)] double minutes = 10)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var a = (action ?? "status").Trim().ToLowerInvariant();
                if (a == "start")
                {
                    var why = JawaBenchHealthProfiler.Start(methods, preset, minutes, "jawa/health_profile");
                    if (why != null) return Fail(why, JawaBenchHealthProfiler.Report());
                }
                else if (a == "stop") JawaBenchHealthProfiler.Stop();
                else if (a != "status") return Fail("action must be status, start or stop");
                return new { success = true, profile = JawaBenchHealthProfiler.Report() };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
