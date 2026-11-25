// JawaBenchSceneTickCore.cs - one scene run, stepped at the end of each tick: the PURE half (no Verse, no Unity, no Harmony).
// Item RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED. Page: design/specs/2026-11-23-bridge-v2/boundary.md (the trace
// schema, the evidence contract, the promises). It joins the condition run (JawaBenchCondCore.CondRun, built 2026-11-06 and
// never run in a tick) to a tick: sample, conditions, end test, act steps, in that order. It judges nothing.
//
// Compiled into bridgetools/SceneTickSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    /// <summary>What a run needs of the game and of the disk writer.</summary>
    internal interface ISceneHost
    {
        /// <summary>One record line of kind `scene`. Returns the line's sequence number, or -1 when the writer dropped it.</summary>
        long Enqueue(string fields);
        /// <summary>True when the writer has nothing left to write.</summary>
        bool Drained();
        /// <summary>Pause the game now. False when the speed, read back, is not Paused.</summary>
        bool Pause();
        long Tick();
        ulong RandState();
        double NowMs();
        /// <summary>Bytes allocated so far (a calibrated counter), or null when none is calibrated.</summary>
        long? AllocBytes();
    }

    internal static class JawaBenchSceneTickCore
    {
        internal const string Schema = "scene_trace_v1";
        internal const double DrainMs = 60000;      // boundary page, LIMITS

        /// <summary>The numbering of one trace. A run has its own, or it shares its session's, so that the rows of several runs
        /// are one series with no gap.</summary>
        internal sealed class Trace
        {
            public int N, Rows, Dropped;
            public string Session;                  // null: the trace of one run outside any session

            /// <summary>One row. Returns the line's sequence number, or -1 when the writer dropped it.</summary>
            public long Emit(ISceneHost h, string run, long tick, string phase, string rec, string fields)
            {
                N++;
                var sb = new StringBuilder(128);
                if (Session != null) sb.Append("\"sess\":").Append(JawaBenchCondCore.Canon(Session)).Append(',');
                sb.Append("\"run\":").Append(JawaBenchCondCore.Canon(run)).Append(",\"n\":").Append(N).Append(",\"tick\":").Append(tick)
                  .Append(",\"phase\":\"").Append(phase).Append("\",\"rec\":\"").Append(rec).Append('"');
                if (!string.IsNullOrEmpty(fields)) sb.Append(',').Append(fields);
                long seq = h.Enqueue(sb.ToString());
                if (seq < 0) Dropped++; else Rows++;
                return seq;
            }
        }

        internal sealed class Act
        {
            public readonly string Name;
            public readonly long At;                // ticks after the start, at least 1
            public readonly Func<string> Do;        // what it did; an exception is "not delivered"
            public bool Done;
            public Act(string name, long at, Func<string> act) { Name = name; At = at; Do = act; }
        }

        internal sealed class Track
        {
            public string Name;
            public JawaBenchCondCore.Probe Probe;
            public bool Has;
            public CondRead Last;
            public long Reads;                      // samples taken, the first and the last included
            public double Ms, MsMax;                // what its reads cost
            public int BadTicks;                    // samples that were not ok
            public long BadFrom;
            public string BadState, BadDetail;      // of the first of them
        }

        /// <summary>null, or why these act steps cannot be part of a run of maxTicks.</summary>
        internal static string RefuseActs(IList<Act> acts, int maxTicks)
        {
            var names = new HashSet<string>();
            foreach (var a in acts)
            {
                if (a.At < 1) return "act '" + a.Name + "' at " + a.At + ": the first tick is 1";
                if (a.At >= maxTicks) return "act '" + a.Name + "' at " + a.At + " is not before the tick limit " + maxTicks + ": its effect could not be sampled";
                if (!names.Add(a.Name)) return "two act steps are named '" + a.Name + "'";
            }
            return null;
        }

        internal sealed class SceneRun
        {
            public readonly string Id;
            readonly ISceneHost _h;
            readonly JawaBenchCondCore.CondRun _cond;
            readonly JawaBenchCondCore.Evaluator _read;
            readonly JawaBenchCondCore.Compiled _c;
            readonly List<Track> _tracks = new List<Track>();
            readonly List<Act> _acts;
            readonly string _mode, _speed;
            readonly double _budgetMs;              // the caller's own bound on one tick's reading; 0 = none
            readonly Trace _trace;
            readonly List<string> _faults = new List<string>();
            int _rows, _dropped, _randFaults, _skipped, _emitted;
            long _from, _endTick;
            bool _ended, _lastTaken, _paused, _drained;
            double _settleFrom = -1;
            long _steady, _steadyBytes, _steadyDirty, _gc;
            string _forced, _forcedWhy;

            /// <summary>running -> settling (ended, paused) -> closed.</summary>
            public string Stage = "new";
            public bool Running { get { return Stage == "running"; } }
            public string State { get { return _forced ?? _cond.State; } }
            public long EndTick { get { return _endTick; } }
            public int Rows { get { return _rows; } }
            public int Dropped { get { return _dropped; } }
            public long? HitTick { get { return _cond.HitTick; } }
            public string Why { get { return _forcedWhy; } }
            public Dictionary<string, object> Result() { return _cond.Result(); }
            public long FromTick { get { return _from; } }
            public bool Drained { get { return _drained; } }
            public IList<string> Faults { get { return _faults; } }
            public IList<Track> Tracks { get { return _tracks; } }
            /// <summary>What the run lock refused and let through while this run was live.</summary>
            public readonly JawaBenchRunLockCore.LockLog Lock = new JawaBenchRunLockCore.LockLog();

            /// <summary>The probe of the condition value that could not be read, with its state; null when there is none.</summary>
            public Dictionary<string, object> UnknownValue()
            {
                var u = _cond.Result()["unknown"] as Dictionary<string, object>;
                if (u == null) return null;
                var d = new Dictionary<string, object>(u);
                var n = Find(_c.Tree, u["id"] as string);
                d["value"] = n != null && n.Probe != null ? n.Probe.Key : null;
                return d;
            }

            static JawaBenchCondCore.Node Find(JawaBenchCondCore.Node n, string id)
            {
                if (n.Id == id) return n;
                foreach (var c in n.Children) { var f = Find(c, id); if (f != null) return f; }
                return null;
            }

            /// <summary>The compiled spec's `sample` probes are the tracks: they are read here, once a tick, and not by the
            /// condition run.</summary>
            public SceneRun(string id, JawaBenchCondCore.Compiled c, IProbeSource src, IList<Act> acts, ISceneHost h, string mode, string speed, Trace trace = null, double tickBudgetMs = 0)
            {
                _budgetMs = tickBudgetMs;
                Id = id; _trace = trace ?? new Trace(); _h = h; _c = c; _mode = mode; _speed = speed;
                _acts = new List<Act>(acts);
                if (c.Sample != null) foreach (var kv in c.Sample) _tracks.Add(new Track { Name = kv.Key, Probe = kv.Value });
                c.Sample = null;
                _read = new JawaBenchCondCore.Evaluator(src);
                _cond = new JawaBenchCondCore.CondRun(c, src, h.NowMs);
            }

            // ------------------------------------------------------------------------------------------ records
            long Emit(long tick, string phase, string rec, string fields)
            {
                _emitted++;
                long seq = _trace.Emit(_h, Id, tick, phase, rec, fields);
                if (seq < 0) _dropped++; else _rows++;
                return seq;
            }

            static string S(object o) { return JawaBenchCondCore.Canon(o); }

            void Fault(long tick, string phase, string what, string detail)
            {
                _faults.Add(what + ": " + detail);
                Emit(tick, phase, "fault", "\"what\":" + S(what) + ",\"detail\":" + S(detail));
            }

            void Sample(long tick, string phase, bool all)
            {
                for (int i = 0; i < _tracks.Count; i++)
                {
                    var t = _tracks[i];
                    double t0 = _h.NowMs();
                    var r = _read.ReadProbe(t.Probe);
                    double ms = _h.NowMs() - t0;
                    t.Ms += ms;
                    if (ms > t.MsMax) t.MsMax = ms;
                    t.Reads++;
                    if (r.Status != "ok" && phase != "last" && t.BadTicks++ == 0) { t.BadFrom = tick; t.BadState = r.Status; t.BadDetail = r.Detail; }
                    if (!all && t.Has && r.Status == t.Last.Status && JawaBenchCondCore.SameValue(r.V, t.Last.V)) continue;
                    t.Has = true; t.Last = r;
                    Emit(tick, phase, "track", "\"name\":" + S(t.Name) + ",\"st\":" + S(r.Status) + ",\"v\":" + S(r.V) +
                                               (r.Status == "ok" ? "" : ",\"detail\":" + S(r.Detail)));
                }
            }

            void RandCheck(ulong before, long tick, string phase)
            {
                ulong after = _h.RandState();
                if (after == before) return;
                _randFaults++;
                Fault(tick, phase, "rand_in_sample", "random state " + before + " -> " + after);
            }

            // ------------------------------------------------------------------------------------------ the run
            /// <summary>On the tick the run starts at, before any act.</summary>
            public void Arm(long tick, object epoch)
            {
                _from = _endTick = tick;
                Stage = "running";
                var acts = new List<object>();
                foreach (var a in _acts) acts.Add(new Dictionary<string, object> { { "name", a.Name }, { "at", (double)a.At } });
                var tracks = new List<object>();
                foreach (var t in _tracks) tracks.Add(t.Name);
                // rand: Rand.StateCompressed at arm, as a decimal string (a ulong is wider than a JSON number); reading it draws nothing
                Emit(tick, "first", "open", "\"schema\":" + S(Schema) + ",\"mode\":" + S(_mode) + ",\"speed\":" + S(_speed) + ",\"epoch\":" + S(epoch) +
                                            ",\"rand\":" + S(_h.RandState().ToString(System.Globalization.CultureInfo.InvariantCulture)) +
                                            ",\"maxTicks\":" + _c.MaxTicks + ",\"tracks\":" + S(tracks) + ",\"acts\":" + S(acts) + ",\"cond\":" + S(_c.Canonical));
                try
                {
                    ulong r0 = _h.RandState();
                    Sample(tick, "first", true);
                    _cond.Arm(tick, epoch);
                    RandCheck(r0, tick, "first");
                }
                catch (Exception e) { Force("aborted", "the arm threw " + e.GetType().Name + ": " + e.Message, tick); return; }
                if (_cond.State != "running") End(tick, "first");
            }

            /// <summary>The end of one tick: sample, conditions, end test, act steps. A run never ends on a tick that did an
            /// act step, because the end is tested before the act steps and an ended run does none. `stop` is the safety trigger that
            /// fired on this tick (a step loop has one), or null.</summary>
            public void OnTickEnd(long tick, object epoch, bool runOriginal, string stop = null)
            {
                if (Stage != "running") return;
                if (!runOriginal) { _skipped++; return; }
                int emitted = _emitted;
                long? a0 = _h.AllocBytes();
                double ms0 = _h.NowMs();
                ulong r0 = _h.RandState();
                Sample(tick, "end_of_tick", false);
                _cond.Step(tick, epoch, stop);
                double ms = _h.NowMs() - ms0;
                RandCheck(r0, tick, "end_of_tick");
                long? a1 = _h.AllocBytes();
                _endTick = tick;
                if (_cond.State != "running") { End(tick, "end_of_tick"); return; }
                if (_budgetMs > 0 && ms > _budgetMs)
                {
                    var c = Costliest();
                    Force("budget", "reading one tick took " + Ms(ms) + " ms, over the " + Ms(_budgetMs) + " ms that the caller gave; the costliest is " +
                                    (c == null ? "unknown" : c["node"] + " (" + c["value"] + "), " + Ms((double)c["msMax"]) + " ms in one tick"), tick);
                    return;
                }
                if (a0.HasValue && a1.HasValue && emitted == _emitted) Meter(a1.Value - a0.Value);
                long k = tick - _from;
                for (int i = 0; i < _acts.Count; i++)
                {
                    var a = _acts[i];
                    if (a.Done || a.At != k) continue;
                    a.Done = true;
                    bool ok = true; string d;
                    try { d = a.Do(); } catch (Exception e) { ok = false; d = e.GetType().Name + ": " + e.Message; }
                    Emit(tick, "end_of_tick", "act", "\"name\":" + S(a.Name) + ",\"ok\":" + (ok ? "true" : "false") + ",\"detail\":" + S(d ?? ""));
                }
            }

            void Meter(long d)
            {
                if (d < 0) { _gc++; return; }              // a collection landed inside: this tick says nothing
                _steady++;
                if (d > 0) { _steadyBytes += d; _steadyDirty++; }
            }

            static string Ms(double ms) { return Math.Round(ms, 3).ToString(CultureInfo.InvariantCulture); }

            /// <summary>The condition node or the track whose reads took the most time: node, value, ms, msMax. Null when there is none.</summary>
            public Dictionary<string, object> Costliest()
            {
                string id = null, key = null;
                double ms = -1, max = 0;
                Walk(_c.Tree, ref id, ref key, ref ms, ref max);
                foreach (var t in _tracks)
                    if (t.Ms > ms) { id = "track " + t.Name; key = t.Probe.Key; ms = t.Ms; max = t.MsMax; }
                if (id == null) return null;
                return new Dictionary<string, object> { { "node", id }, { "value", key }, { "ms", Math.Round(ms, 3) }, { "msMax", Math.Round(max, 3) } };
            }

            static void Walk(JawaBenchCondCore.Node n, ref string id, ref string key, ref double ms, ref double max)
            {
                if (n.Probe != null && n.Ms > ms) { id = n.Id; key = n.Probe.Key; ms = n.Ms; max = n.MsMax; }
                foreach (var c in n.Children) Walk(c, ref id, ref key, ref ms, ref max);
            }

            void End(long tick, string phase)
            {
                if (_ended) return;
                _ended = true;
                _endTick = tick;
                Stage = "settling";                  // first: whatever throws below, the evaluator is off and the run will close
                try { _paused = _h.Pause(); }
                catch (Exception e) { _paused = false; Fault(tick, phase, "threw", "the pause: " + e.GetType().Name + ": " + e.Message); }
                if (!_paused && State == "epoch") Fault(tick, phase, "game_replaced", "the game or the map of the run is gone: what is there now was not paused");
                else if (!_paused) Fault(tick, phase, "pause_refused", "the speed read back is not Paused");
                var r = _cond.Result();
                var cov = (Dictionary<string, object>)r["coverage"];
                Emit(tick, phase, "end", "\"state\":" + S(State) + ",\"why\":" + S(_forcedWhy) + ",\"hitTick\":" + S(r["hitTick"]) + ",\"executed\":" + (tick - _from) +
                                         ",\"triggers\":" + S(r["triggers"]) + ",\"unknown\":" + S(UnknownValue()) + ",\"complete\":" + S(cov["complete"]) + ",\"cost\":" + S(r["cost"]) + ",\"costliest\":" + S(Costliest()));
            }

            /// <summary>End the run from outside the condition: `cancelled`, `epoch`, `aborted`, `threw` (the game's tick threw, so the
            /// tick is not whole), `budget`.</summary>
            public void Force(string state, string why, long tick)
            {
                if (_ended || Stage == "closed" || Stage == "new") return;
                _forced = state; _forcedWhy = why;
                End(tick, "end_of_tick");
            }

            /// <summary>After the pause, once a frame until it closes: the last sample, then the closing record when the writer
            /// has drained.</summary>
            public void Settle()
            {
                if (Stage != "settling") return;
                long tick = _h.Tick();
                if (!_lastTaken)
                {
                    _lastTaken = true;
                    _settleFrom = _h.NowMs();
                    if (tick != _endTick && State != "epoch") Fault(tick, "last", "ran_past_end", "ended on " + _endTick + ", the game is on " + tick);
                    try
                    {
                        ulong r0 = _h.RandState();
                        Sample(tick, "last", true);
                        RandCheck(r0, tick, "last");
                    }
                    catch (Exception e) { Fault(tick, "last", "threw", "the last sample: " + e.GetType().Name + ": " + e.Message); }
                    return;
                }
                bool drained = _h.Drained();
                if (!drained && _h.NowMs() - _settleFrom < DrainMs) return;
                var left = new List<object>();
                foreach (var a in _acts) if (!a.Done) left.Add(a.Name);
                string alloc = _steady == 0 && _gc == 0 ? "null"
                    : "{\"steadyTicks\":" + _steady + ",\"bytes\":" + _steadyBytes + ",\"ticksThatAllocated\":" + _steadyDirty + ",\"ticksWithGc\":" + _gc + "}";
                _drained = drained;
                Emit(tick, "last", "close", "\"rows\":" + _rows + ",\"dropped\":" + _dropped + ",\"drained\":" + (drained ? "true" : "false") +
                                            ",\"paused\":" + (_paused ? "true" : "false") + ",\"tickAfter\":" + tick + ",\"skipped\":" + _skipped +
                                            ",\"randFaults\":" + _randFaults + ",\"actsNotDone\":" + S(left) + ",\"alloc\":" + alloc +
                                            ",\"lockReads\":" + Lock.Reads + ",\"breaches\":" + S(Lock.Breaches()));
                Stage = "closed";
            }
        }
    }
}
