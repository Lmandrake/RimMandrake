// Unit group for JawaBenchHealthCore.cs (the PRODUCTION file): the pure logic of the game-health metrics
// (tps.frame-hist, tps.log-counts, tps.bridge-occupancy, tps.capability-inventory, opt.profiler, spike.gc-timing).
// Prints "U name ok|FAIL why" per check and "U-count n"; exit 1 when any check fails.
// Driven by src/RimMandrake/Utils/selftest_health_core.py. Written failing-first against a stub core (2026-10-14).
using System;
using System.Collections.Generic;
using System.Threading;
using H = JawaBench.BridgeTools.JawaBenchHealthCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int _n, _bad;

        static void Check(string name, Func<bool> f, Func<string> why = null)
        {
            _n++;
            bool ok; string w = "";
            try { ok = f(); if (!ok && why != null) w = why(); }
            catch (Exception e) { ok = false; w = e.GetType().Name + ": " + e.Message; }
            if (!ok) _bad++;
            Console.WriteLine("U " + name.Replace(' ', '_') + " " + (ok ? "ok" : "FAIL " + w));
        }

        static int Main()
        {
            // ================= rule 1: unavailable is never zero
            Check("unavailable_renders_word_not_number", () => H.Reading.Unavailable("no frames").Render() == "unavailable: no frames");
            Check("unavailable_json_has_no_value_key", () => !H.Reading.Unavailable("x").Json().Contains("\"value\""));
            Check("failed_and_off_render_words", () => H.Reading.Failed("boom").Render() == "failed: boom" && H.Reading.SwitchedOff().Render().StartsWith("off"));
            Check("ok_renders_value_and_unit", () => H.Reading.Ok(12.5, "ms").Render() == "12.5 ms" && H.Reading.Ok(0, "ms").Json().Contains("\"value\":0"));
            Check("meter_without_calls_is_unavailable", () => new H.Meter().MeanUs(1e7).Word == H.WUnavailable);
            Check("meter_mean_and_max", () => { var m = new H.Meter(); m.Add(10); m.Add(30); var r = m.MeanUs(1e6); return r.IsOk && Math.Abs(r.Value - 20) < 1e-9 && m.MaxUs(1e6).Value == 30; });

            // ================= switches: one per id; merged id noted
            Check("switch_ids_are_the_six", () => H.MetricIds.Length == 6 && Array.IndexOf(H.MetricIds, "tps.frame-hist") >= 0 && Array.IndexOf(H.MetricIds, "spike.gc-timing") >= 0);
            Check("switch_defaults_all_on", () => { var s = new H.Switches(); foreach (var id in H.MetricIds) if (!s.On(id)) return false; return true; });
            Check("switch_parse_turns_one_off", () => { var s = H.Switches.Parse("{\"tps.log-counts\": false}"); return !s.On("tps.log-counts") && s.On("tps.frame-hist") && s.Note == "ok"; });
            Check("switch_parse_notes_unknown_and_merged", () =>
            {
                var s = H.Switches.Parse("{\"bogus.id\": true, \"opt.own-counters\": false, \"opt.profiler\": \"yes\"}");
                return s.Note.Contains("bogus.id: unknown metric id") && s.Note.Contains("merged into opt.profiler") && s.Note.Contains("not a bool") && s.On("opt.profiler");
            }, () => H.Switches.Parse("{\"bogus.id\": true, \"opt.own-counters\": false, \"opt.profiler\": \"yes\"}").Note);
            Check("switch_parse_invalid_keeps_defaults", () => { var s = H.Switches.Parse("not json"); return s.On("tps.frame-hist") && s.Note.StartsWith("invalid settings"); });

            // ================= tps.frame-hist: merge, never average p99
            Check("bucket_edges", () => H.FrameHist.BucketOf(0) == 0 && H.FrameHist.BucketOf(0.99) == 0 && H.FrameHist.BucketOf(1) == 1 &&
                                        H.FrameHist.BucketOf(16.6) == 5 && H.FrameHist.BucketOf(30000) == H.FrameHist.Edges.Length && H.FrameHist.BucketOf(1e9) == H.FrameHist.Edges.Length);
            Check("rejects_nan_negative_inf", () => { var h = new H.FrameHist(); h.Add(double.NaN); h.Add(-1); h.Add(double.PositiveInfinity); h.Add(5); return h.N == 1 && h.Rejected == 3; });
            Check("empty_hist_quantile_unavailable", () => { var h = new H.FrameHist(); string t; return h.Quantile(0.99, out t).Word == H.WUnavailable && t.Contains("unavailable") && !h.QuantileRange(0.5, out _, out _); });
            Check("empty_hist_json_says_unavailable", () => new H.FrameHist().Json().Contains("\"status\":\"unavailable\""));
            // merged == histogram of the concatenated data
            var a = new H.FrameHist(); var b = new H.FrameHist(); var all = new H.FrameHist();
            for (int i = 0; i < 990; i++) { a.Add(16); all.Add(16); }
            for (int i = 0; i < 10; i++) { a.Add(45); all.Add(45); }
            for (int i = 0; i < 100; i++) { b.Add(16); all.Add(16); }
            for (int i = 0; i < 900; i++) { b.Add(120); all.Add(120); }
            var m = new H.FrameHist(); string why;
            Check("merge_ok", () => m.Merge(a, out why) && m.Merge(b, out why));
            Check("merge_equals_concatenation", () =>
            {
                for (int i = 0; i < m.Counts.Length; i++) if (m.Counts[i] != all.Counts[i]) return false;
                return m.N == all.N && Math.Abs(m.TotalMs - all.TotalMs) < 1e-6 && m.MaxMs == all.MaxMs;
            });
            Check("merged_p99_is_recomputed_not_averaged", () =>
            {
                a.QuantileRange(0.99, out var alo, out var ahi); b.QuantileRange(0.99, out var blo, out var bhi);
                m.QuantileRange(0.99, out var mlo, out var mhi);
                double avgHi = (ahi + bhi) / 2;               // the forbidden average
                return mlo == 100 && mhi == 120 && !(avgHi >= mlo && avgHi <= mhi);
            }, () => { m.QuantileRange(0.99, out var lo, out var hi); return "merged p99 [" + lo + "," + hi + "]"; });
            Check("merge_refuses_other_bucket_version", () => { var x = new H.FrameHist(); var y = new H.FrameHist { BucketVersion = "fh-v0" }; y.Add(1); return !x.Merge(y, out var w) && w.Contains("fh-v0") && x.N == 0; });
            Check("quantile_is_a_bucket_range", () => { var h = new H.FrameHist(); for (int i = 0; i < 100; i++) h.Add(17); h.QuantileRange(0.5, out var lo, out var hi); return lo == 16.7 && hi == 17; });
            Check("open_bucket_upper_is_observed_max", () => { var h = new H.FrameHist(); h.Add(45000); h.QuantileRange(0.99, out var lo, out var hi); return lo == 30000 && hi == 45000; });
            Check("long_stall_above_p99_kept_in_max_and_slow_time", () =>
            {
                var h = new H.FrameHist(); for (int i = 0; i < 1000; i++) h.Add(16); h.Add(20000);
                h.QuantileRange(0.99, out _, out var hi);
                return hi <= 16.7 && h.MaxMs == 20000 && h.SlowCount[4] == 1 && h.SlowMs[4] == 20000;
            });
            Check("json_carries_bucket_version_and_edges", () => { var h = new H.FrameHist(); h.Add(3); var j = h.Json(); return j.Contains("\"bucketVersion\":\"fh-v1\"") && j.Contains("\"edgesMs\":[1,2,4") && j.Contains("\"p99RangeMs\""); });
            Check("ring_merges_windows_since", () =>
            {
                var r = new H.HistRing(3);
                for (int k = 0; k < 4; k++) { var w = new H.FrameHist(); w.Add(10 + k); r.Close(w, k * 60, k * 60 + 60); }
                var mm = r.MergedSince(121, out int n, out double from);
                return r.Count == 3 && r.Evicted == 1 && n == 2 && mm.N == 2 && from == 120;
            });

            // ================= tps.log-counts: cap 10000 and the suppression wording
            Check("cap_constant_is_10000", () => H.VerseLogCap == 10000);
            Check("cap_reached_says_suppressed", () => { var c = H.JudgeCap(10000, true, 0, false); return c.Word == "suppressed" && c.Text.Contains("emission suppressed; error activity unknown"); });
            Check("logger_disabled_alone_is_suppressed", () => { var c = H.JudgeCap(50, false, 0, false); return c.Word == "suppressed" && c.Text.Contains(H.SuppressedText); });
            Check("lockmessages_is_suppressed", () => { var c = H.JudgeCap(50, false, 2, true); return c.Word == "suppressed" && c.Text.Contains("LockMessages") && c.Text.Contains(H.SuppressedText); });
            Check("emitting_with_headroom", () => { var c = H.JudgeCap(9000, false, 0, true); return c.Word == "emitting" && c.Headroom.IsOk && c.Headroom.Value == 1000; });
            Check("unreadable_state_is_not_emitting", () => H.JudgeCap(null, null, null, null).Word == "unavailable" && H.JudgeCap(5, false, null, true).Word == "unknown");
            Check("unreadable_count_headroom_unavailable", () => H.JudgeCap(null, false, 0, true).Headroom.Word == H.WUnavailable);
            Check("log_line_leads_with_suppression", () =>
            {
                var t = new H.LogTally(); t.Note(0); t.Note(2); t.Note(2); t.Note(99);
                var line = H.LogLine(t, H.JudgeCap(10000, true, 0, false));
                return line.StartsWith("Verse.Log cap (10000) reached: emission suppressed; error activity unknown") && line.Contains("warning 2") && t.Other == 1 && t.Total == 4;
            });
            Check("log_tally_threadsafe", () =>
            {
                var t = new H.LogTally(); var ths = new Thread[4];
                for (int k = 0; k < 4; k++) { ths[k] = new Thread(() => { for (int i = 0; i < 5000; i++) t.Note(3); }); ths[k].Start(); }
                foreach (var th in ths) th.Join();
                return t.Of(3) == 20000;
            });
            Check("reset_tracker_counts_clears", () => { var r = new H.ResetTracker(); r.Observe(5); r.Observe(9000); r.Observe(1); r.Observe(4); r.Observe(0); return r.Resets == 2; });

            // ================= tps.bridge-occupancy
            Check("occupancy_union_no_double_count", () =>
            {
                var o = new H.Occupancy(2);
                o.Note(0, 100, 200, 1); o.Note(1, 150, 250, 0); o.Note(0, 300, 310, 0);
                return o.BusyTicks == 160 && o.Calls == 3 && o.CallsWithWork == 1 && o.MaxCallTicks == 100;
            });
            Check("occupancy_delay_bound_per_target", () =>
            {
                var o = new H.Occupancy(2);
                o.Note(0, 1000, 1001, 0); o.Note(1, 1002, 1003, 0); o.Note(0, 2000, 2050, 3); o.Note(1, 2100, 2101, 1);
                return o.DelayBoundSamples == 2 && o.DelayBoundMaxTicks == 1098 && o.DelayBoundSumTicks == 1000 + 1098 && o.MaxPending == 3;
            });
            Check("occupancy_first_pump_with_work_has_no_bound", () => { var o = new H.Occupancy(1); o.Note(0, 5, 6, 4); return o.DelayBoundSamples == 0 && o.CallsWithWork == 1; });
            Check("occupancy_rejects_bad_interval", () => { var o = new H.Occupancy(1); o.Note(0, 10, 5, 0); o.Note(3, 1, 2, 0); return o.Rejected == 2 && o.Calls == 0; });
            Check("occupancy_share_empty_window_unavailable", () => new H.Occupancy(1).Share(0).Word == H.WUnavailable);
            Check("occupancy_share", () => { var o = new H.Occupancy(1); o.Note(0, 0, 25, 0); var s = o.Share(100); return s.IsOk && Math.Abs(s.Value - 0.25) < 1e-12; });

            // ================= tps.capability-inventory
            Check("recorder_valid_without_samples_unavailable", () => H.ClassifyRecorder(true, null, true, 0, 0, "bytes").Word == H.WUnavailable);
            Check("recorder_invalid_unavailable", () => H.ClassifyRecorder(true, null, false, 5, 7, "bytes").Word == H.WUnavailable);
            Check("recorder_start_threw_failed", () => { var r = H.ClassifyRecorder(false, "NotSupported", false, 0, 0, null); return r.Word == H.WFailed && r.Reason.Contains("NotSupported"); });
            Check("recorder_ok_needs_valid_and_samples", () => { var r = H.ClassifyRecorder(true, null, true, 3, 4096, "bytes"); return r.IsOk && r.Value == 4096; });
            Check("inventory_summary_has_no_overall_verdict", () =>
            {
                var rows = new List<KeyValuePair<string, H.Reading>>
                {
                    new KeyValuePair<string, H.Reading>("a", H.Reading.Ok(1, "x")), new KeyValuePair<string, H.Reading>("b", H.Reading.Unavailable("y")),
                    new KeyValuePair<string, H.Reading>("c", H.Reading.SwitchedOff()), new KeyValuePair<string, H.Reading>("d", H.Reading.Failed("z")),
                };
                var s = H.InventorySummary(rows);
                return s.StartsWith("ok 1, unavailable 1, failed 1, off 1") && !s.Contains("complete") && !s.Contains("PASS");
            });

            // ================= spike.gc-timing: coincidence with its base rate
            Check("gc_no_frames_unavailable", () => new H.GapGc().Text().StartsWith("unavailable"));
            Check("gc_coincidence_counts_and_base_rate", () =>
            {
                var g = new H.GapGc();
                for (int i = 0; i < 100; i++) g.Observe(16, i % 10 == 0 ? 1 : 0, i);
                g.Observe(400, 1, 101); g.Observe(900, 0, 102);
                var t = g.Text();
                return g.Gaps == 2 && g.GapsWithGcChange == 1 && g.Frames == 102 && g.FramesWithGcChange == 11 &&
                       t.Contains("gcCountChangedDuringGap in 1 of them") && t.Contains("11 of 102 frames") && t.Contains("not a cause") && !t.Contains("pause time:");
            }, () => new H.GapGc().Text());
            Check("gc_text_never_names_pause_ms", () => { var g = new H.GapGc(); g.Observe(500, 2, 1); return !g.Text().Contains("gcPauseMs") && g.Events().Count == 1 && g.Events()[0].GcDelta == 2; });
            Check("gc_ring_bounded", () => { var g = new H.GapGc(); for (int i = 0; i < 70; i++) g.Observe(300, 0, i); return g.Events().Count == 64 && g.Evicted == 6 && g.Events()[0].AtS == 6; });

            // ================= opt.profiler (+ merged own-counters preset)
            Check("allowlist_parses_exact_names", () =>
            {
                var e = new List<string>();
                var l = H.ParseAllowlist("Verse.TickManager:DoSingleTick; RimWorld.Pawn_PathFollower:PatherTick # comment\nRimMandrake.FlowWorks.RM_LiquidSurface:MapComponentTick", 32, e);
                return e.Count == 0 && l.Count == 3 && l[1].Type == "RimWorld.Pawn_PathFollower" && l[1].Method == "PatherTick";
            });
            Check("allowlist_refuses_wildcards_whole", () => { var e = new List<string>(); var l = H.ParseAllowlist("Verse.A:B;Verse.*:Tick", 32, e); return l.Count == 0 && e.Count == 1 && e[0].Contains("wildcards"); });
            Check("allowlist_refuses_duplicates_and_bad_shape", () => { var e = new List<string>(); var l = H.ParseAllowlist("Verse.A:B;Verse.A:B;NoNs:X;Verse.C", 32, e); return l.Count == 0 && e.Count == 3; });
            Check("allowlist_cap", () =>
            {
                var parts = new List<string>(); for (int i = 0; i < 33; i++) parts.Add("Verse.T" + i + ":M");
                var e = new List<string>(); var l = H.ParseAllowlist(string.Join(";", parts), H.MaxProfileTargets, e);
                return l.Count == 0 && e.Count == 1 && e[0].Contains("maximum is 32");
            });
            Check("allowlist_empty_refused", () => { var e = new List<string>(); H.ParseAllowlist("  # nothing ", 32, e); return e.Count == 1 && e[0] == "empty allowlist"; });
            Check("own_preset_parses", () => { var e = new List<string>(); var l = H.ParseAllowlist(H.OwnPreset, 32, e); return e.Count == 0 && l.Count == 4 && l.TrueForAll(t => t.Type.StartsWith("RimMandrake.")); });
            Check("resolve_verdicts", () => H.ResolveVerdict("Verse.A:B", true, 1) == null && H.ResolveVerdict("Verse.A:B", false, 0).Contains("type not found") &&
                                            H.ResolveVerdict("Verse.A:B", true, 0).Contains("no declared method") && H.ResolveVerdict("Verse.A:B", true, 2).Contains("ambiguous"));
            Check("expiry_clamps_and_expires", () =>
            {
                var x = new H.Expiry();
                bool before = x.Live(0);
                double m = x.Set(100, 500, 10, 60);
                double d = x.Set(100, double.NaN, 10, 60);
                return !before && m == 60 && d == 10 && x.Live(699) && !x.Live(700);
            });
            Check("depth_times_outermost_only", () =>
            {
                H.Depth.ResetThreadForTest();
                bool o1 = H.Depth.Enter(3), o2 = H.Depth.Enter(3); H.Depth.Exit(3); H.Depth.Exit(3);
                bool o3 = H.Depth.Enter(3); H.Depth.Exit(3);
                H.Depth.Exit(3);              // stray exit is harmless
                bool o4 = H.Depth.Enter(3); H.Depth.Exit(3);
                return o1 && !o2 && o3 && o4 && !H.Depth.Enter(99);
            });
            Check("depth_is_per_thread", () =>
            {
                H.Depth.ResetThreadForTest(); H.Depth.Enter(1);
                bool other = false; var th = new Thread(() => { other = H.Depth.Enter(1); H.Depth.Exit(1); }); th.Start(); th.Join();
                H.Depth.Exit(1);
                return other;
            });

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
