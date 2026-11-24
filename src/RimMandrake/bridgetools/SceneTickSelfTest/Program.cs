// Units for JawaBenchSceneTickCore.cs (the PRODUCTION file). One unit per promise of
// design/specs/2026-11-23-bridge-v2/boundary.md. Prints "U <name> ok|FAIL why" and "U-count n".
// The game is played by World.Play: ticks run while the game is not paused, several to a frame, exactly as
// TickManager.TickManagerUpdate does (a pause made in the postfix ends the frame's loop), and Settle runs once a frame.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal sealed class World : ISceneHost, IProbeSource
    {
        public long TickNow = 1000, Seq;
        public bool PausedNow = true, RefusePause, DrawInSample;
        public ulong Rand = 7;
        public double Clock;
        public long Queue;                       // rows the writer has not written yet
        public int DropAtRow = -1;               // the n-th row of the run that the writer drops
        int _rows;
        public readonly Dictionary<string, CondRead> Values = new Dictionary<string, CondRead>();
        public readonly List<(long seq, JsonElement r)> Out = new List<(long, JsonElement)>();
        public int WrittenWhenClosed = -1, FramesPlayed;

        public void Set(string key, object v, string st = "ok", string d = "") { Values[key] = new CondRead(v, st, d); }

        // ---- ISceneHost
        public long Enqueue(string fields)
        {
            _rows++;
            Seq++;
            var e = JsonDocument.Parse("{" + fields + "}").RootElement;
            if (_rows == DropAtRow) return -1;
            if (e.GetProperty("rec").GetString() == "close") WrittenWhenClosed = (int)Queue;
            Queue++;
            Out.Add((Seq, e));
            return Seq;
        }
        public bool Drained() { return Queue == 0; }
        public bool Pause() { if (RefusePause) return false; PausedNow = true; return true; }
        public long Tick() { return TickNow; }
        public ulong RandState() { return Rand; }
        public double NowMs() { return Clock; }
        public long? AllocBytes() { return GC.GetAllocatedBytesForCurrentThread(); }

        // ---- IProbeSource
        public int CurrentMap() { return 0; }
        public bool MapSize(int m, out int x, out int z) { x = z = 250; return m == 0; }
        public string Refuse(string key, C.Probe p) { return null; }
        static readonly object[] Boxes = Enumerable.Range(0, 4000).Select(i => (object)(double)i).ToArray();   // made before the metered ticks
        public CondRead Read(string key, C.Probe p, int x, int z)
        {
            if (DrawInSample) Rand++;
            if (p.Name == "game.tick")
                return new CondRead(Boxes[TickNow], "ok", "");
            CondRead r;
            return Values.TryGetValue(key, out r) ? r : new CondRead(null, "error", "no value for " + key);
        }

        // ---- the game's loop
        public void Play(T.SceneRun run, int frames, int perFrame = 6, Action<long> during = null, Func<long, bool> skip = null)
        {
            for (int f = 0; f < frames && run.Stage != "closed"; f++)
            {
                FramesPlayed++;
                Clock += 16;
                run.Settle();                                              // the driver's Update, before the game's own
                for (int i = 0; i < perFrame && !PausedNow; i++)
                {
                    bool skipped = skip != null && skip(TickNow + 1);
                    TickNow++;
                    Rand += 3;                                             // ordinary play draws
                    if (during != null) during(TickNow);
                    run.OnTickEnd(TickNow, Epoch, !skipped);
                }
                if (f % 4 == 3) Queue = 0;                                 // the writer thread catches up now and then
            }
        }
        public static readonly object Epoch = 1.0;
        public List<(long seq, JsonElement r)> Rec(string rec) { return Out.Where(o => o.r.GetProperty("rec").GetString() == rec).ToList(); }
        public List<(long seq, JsonElement r)> Track(string name, string phase = null)
        {
            return Rec("track").Where(o => o.r.GetProperty("name").GetString() == name && (phase == null || o.r.GetProperty("phase").GetString() == phase)).ToList();
        }
        public JsonElement One(string rec) { var l = Rec(rec); if (l.Count != 1) throw new Exception(l.Count + " records " + rec); return l[0].r; }
    }

    internal static class Program
    {
        static int _n, _bad;
        static bool _session;            // `session`: each run is part of a session, as jawa/run_until makes it

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w));
        }

        static void Eq(object a, object b, string what)
        {
            if (!Equals(a, b)) throw new Exception(what + ": got " + a + ", want " + b);
        }

        const string HealthKey = "thing.field path=hp thing=P";
        const string Health = "{\"p\":\"thing.field\",\"thing\":\"P\",\"path\":\"hp\"}";
        const string Tracks = ",\"sample\":{\"every\":1,\"probes\":{\"hp\":" + Health + "}}";

        static T.SceneRun Run(World w, string until, int max = 500, string extra = Tracks, params T.Act[] acts)
        {
            var spec = C.ParseJson("{\"until\":" + until + ",\"max_ticks\":" + max + extra + "}");
            var c = new C.Compiler(w, "run").CompileSpec(spec);
            string why = T.RefuseActs(acts, max);
            if (why != null) throw new Exception("refused: " + why);
            return new T.SceneRun("r1", c, w, acts, w, "PLAY", "Ultrafast", _session ? new T.Trace { Session = "S1" } : null);
        }

        static string AtTick(long t) { return "{\"cmp\":[{\"p\":\"game.tick\"},\">=\"," + t + "]}"; }
        static string Hp(string op, double v) { return "{\"cmp\":[" + Health + ",\"" + op + "\"," + v + "]}"; }

        static World New(double hp = 100) { var w = new World(); w.Set(HealthKey, hp); return w; }

        static void Start(World w, T.SceneRun r)
        {
            r.Arm(w.TickNow, World.Epoch);
            if (r.Running) w.PausedNow = false;
        }

        static int Main(string[] args)
        {
            _session = args.Length > 0 && args[0] == "session";
            Check("a_hit_on_tick_t_executes_t", () =>
            {
                foreach (int per in new[] { 1, 6, 30 })
                {
                    var w = New();
                    var r = Run(w, AtTick(1137));
                    Start(w, r);
                    w.Play(r, 400, per);
                    Eq(w.TickNow, 1137L, "the game's tick after the run, " + per + " ticks a frame");
                    Eq(w.One("end").GetProperty("executed").GetInt64(), 137L, "executed");
                    Eq(w.One("end").GetProperty("hitTick").GetDouble(), 1137.0, "hitTick");
                    Eq(w.One("end").GetProperty("state").GetString(), "hit", "state");
                    Eq(w.One("close").GetProperty("tickAfter").GetInt64(), 1137L, "tickAfter");
                    Eq(w.One("close").GetProperty("paused").GetBoolean(), true, "paused");
                }
                var p = New();
                p.RefusePause = true;
                var q = Run(p, AtTick(1010));
                Start(p, q);
                p.Play(q, 50);
                if (!p.Rec("fault").Any(f => f.r.GetProperty("what").GetString() == "pause_refused")) throw new Exception("a refused pause left no fault");
                if (!p.Rec("fault").Any(f => f.r.GetProperty("what").GetString() == "ran_past_end")) throw new Exception("a game that ran past the end left no fault");
            });
            Check("true_at_arm_executes_nothing", () =>
            {
                var w = New();
                var r = Run(w, AtTick(1000));
                Start(w, r);
                Eq(r.Running, false, "running");
                w.Play(r, 50);
                Eq(w.TickNow, 1000L, "tick");
                Eq(w.One("end").GetProperty("executed").GetInt64(), 0L, "executed");
                Eq(w.One("close").GetProperty("tickAfter").GetInt64(), 1000L, "tickAfter");
            });
            Check("a_track_writes_on_change_only", () =>
            {
                var w = New();
                var r = Run(w, AtTick(1200));
                Start(w, r);
                w.Play(r, 200, 6, t => { if (t == 1050) w.Set(HealthKey, 90.0); if (t == 1100) w.Set(HealthKey, 80.0); if (t == 1101) w.Set(HealthKey, 80.0); });
                var rows = w.Track("hp", "end_of_tick");
                Eq(rows.Count, 2, "rows between the first and the last sample");
                Eq(rows[0].r.GetProperty("tick").GetInt64(), 1050L, "first change");
                Eq(rows[1].r.GetProperty("v").GetDouble(), 80.0, "second value");
                // the steady state allocates nothing: 200 ticks, no row, exact .NET thread counter
                var a = w.One("close").GetProperty("alloc");
                if (a.GetProperty("steadyTicks").GetInt64() < 190) throw new Exception("steady ticks " + a);
                if (a.GetProperty("ticksThatAllocated").GetInt64() > 6) throw new Exception("the steady state allocates: " + a);
            });
            Check("gone_is_gone_never_zero", () =>
            {
                var w = New();
                var r = Run(w, AtTick(1100));
                Start(w, r);
                w.Play(r, 200, 6, t => { if (t == 1040) w.Set(HealthKey, null, "gone", "destroyed"); });
                var rows = w.Track("hp", "end_of_tick");
                Eq(rows.Count, 1, "rows");
                Eq(rows[0].r.GetProperty("st").GetString(), "gone", "status");
                Eq(rows[0].r.GetProperty("v").ValueKind, JsonValueKind.Null, "value");
                Eq(rows[0].r.GetProperty("detail").GetString(), "destroyed", "detail");
                Eq(w.Track("hp", "last")[0].r.GetProperty("st").GetString(), "gone", "last sample");
            });
            Check("an_unknown_ends_the_run_as_unknown", () =>
            {
                var w = New();
                var r = Run(w, Hp("<=", 10));
                Start(w, r);
                w.Play(r, 200, 6, t => { if (t == 1033) w.Set(HealthKey, null, "gone", "destroyed"); });
                var e = w.One("end");
                Eq(e.GetProperty("state").GetString(), "unknown", "state");
                Eq(e.GetProperty("hitTick").ValueKind, JsonValueKind.Null, "hitTick");
                Eq(e.GetProperty("executed").GetInt64(), 33L, "executed");
                Eq(e.GetProperty("unknown").GetProperty("status").GetString(), "gone", "unknown status");
                Eq(w.TickNow, 1033L, "tick");
            });
            Check("a_skipped_original_records_nothing", () =>
            {
                var w = New();
                var r = Run(w, AtTick(1100), 500, Tracks, new T.Act("hurt", 60, () => "x"));
                Start(w, r);
                // a skipped tick changes nothing in the game, the clock included
                for (int i = 0; i < 3; i++) { w.Set(HealthKey, 50.0 + i); r.OnTickEnd(w.TickNow, World.Epoch, false); }
                Eq(w.Track("hp", "end_of_tick").Count, 0, "rows on skipped ticks");
                Eq(w.Rec("end").Count, 0, "end records");
                w.Set(HealthKey, 100.0);
                w.Play(r, 200);
                Eq(w.One("end").GetProperty("state").GetString(), "hit", "state");
                Eq(w.One("close").GetProperty("skipped").GetInt32(), 3, "skipped");
                Eq(w.Rec("act").Count, 1, "the act still happens on a real tick");
            });
            Check("the_close_counts_the_dropped_and_waits_for_the_drain", () =>
            {
                var w = New();
                w.DropAtRow = 4;                     // open, first hp, then the second change
                var r = Run(w, AtTick(1060));
                Start(w, r);
                w.Play(r, 200, 6, t => { if (t == 1010 || t == 1020 || t == 1030) w.Set(HealthKey, (double)t); });
                var c = w.One("close");
                Eq(c.GetProperty("dropped").GetInt32(), 1, "dropped");
                Eq(c.GetProperty("rows").GetInt32(), w.Out.Count - 1, "rows");
                Eq(c.GetProperty("drained").GetBoolean(), true, "drained");
                Eq(w.WrittenWhenClosed, 0, "rows still queued when the close was written");
                var ns = w.Out.Select(o => o.r.GetProperty("n").GetInt32()).ToList();
                Eq(string.Join(",", Enumerable.Range(1, ns.Max()).Except(ns)), "4", "the gap in n");
                // a writer that never drains: the close says so, after the bound
                var s = New();
                var q = Run(s, AtTick(1005));
                Start(s, q);
                for (int i = 0; i < 10; i++) { s.Play(q, 1); s.Queue = 5; }
                Eq(s.Rec("close").Count, 0, "close while the writer is behind");
                s.Clock += T.DrainMs + 1;
                s.Queue = 5;
                s.Play(q, 1);
                Eq(s.One("close").GetProperty("drained").GetBoolean(), false, "drained");
            });
            Check("sample_before_act_inside_a_tick", () =>
            {
                var w = New();
                var r = Run(w, Hp("<", 60), 500, Tracks, new T.Act("hurt", 40, () => { w.Set(HealthKey, 50.0); return "-50"; }));
                Start(w, r);
                w.Play(r, 200, 6, t => { if (t == 1040) w.Set(HealthKey, 95.0); });
                var act = w.Rec("act").Single();
                var same = w.Track("hp", "end_of_tick").Where(x => x.r.GetProperty("tick").GetInt64() == 1040).ToList();
                Eq(same.Count, 1, "samples on the act's tick");
                Eq(same[0].r.GetProperty("v").GetDouble(), 95.0, "the sample on the act's tick is the value before the act");
                if (same[0].seq >= act.seq) throw new Exception("sample seq " + same[0].seq + " is not before act seq " + act.seq);
                var after = w.Track("hp", "end_of_tick").Single(x => x.r.GetProperty("tick").GetInt64() == 1041);
                Eq(after.r.GetProperty("v").GetDouble(), 50.0, "the act's effect is sampled on the next tick");
                Eq(w.One("end").GetProperty("executed").GetInt64(), 41L, "the run ends on the tick after the act");
                if (after.seq >= w.Rec("end").Single().seq) throw new Exception("the new value is not in the trace before the end");
            });
            Check("an_act_and_the_end_never_share_a_tick", () =>
            {
                var w = New();
                bool did = false;
                var r = Run(w, AtTick(1040), 500, Tracks, new T.Act("hurt", 40, () => { did = true; return "x"; }));
                Start(w, r);
                w.Play(r, 200);
                Eq(did, false, "the act on the end's tick was done");
                Eq(w.One("close").GetProperty("actsNotDone")[0].GetString(), "hurt", "actsNotDone");
                Eq(T.RefuseActs(new[] { new T.Act("late", 500, () => "") }, 500) != null, true, "an act on the tick limit is refused");
                Eq(T.RefuseActs(new[] { new T.Act("zero", 0, () => "") }, 500) != null, true, "an act at the start is refused");
                // an act that throws is a record, and the run goes on
                var t = New();
                var q = Run(t, AtTick(1060), 500, Tracks, new T.Act("bad", 10, () => throw new Exception("no target")));
                Start(t, q);
                t.Play(q, 200);
                Eq(t.Rec("act").Single().r.GetProperty("ok").GetBoolean(), false, "act ok");
                Eq(t.One("end").GetProperty("executed").GetInt64(), 60L, "executed");
            });
            Check("first_and_last_sample_of_every_track", () =>
            {
                const string two = ",\"sample\":{\"every\":1,\"probes\":{\"hp\":" + Health + ",\"job\":{\"p\":\"pawn.job\",\"pawn\":\"P\",\"f\":\"def\"}}}";
                foreach (long end in new[] { 1000L, 1050L })
                {
                    var w = New();
                    w.Set("pawn.job f=def pawn=P", "Wait");
                    var r = Run(w, AtTick(end), 500, two);
                    Start(w, r);
                    w.Play(r, 200);
                    foreach (var name in new[] { "hp", "job" })
                    {
                        Eq(w.Track(name, "first").Count, 1, name + " first, end " + end);
                        Eq(w.Track(name, "last").Count, 1, name + " last, end " + end);
                    }
                    if (w.Track("hp", "last")[0].seq < w.Rec("end")[0].seq) throw new Exception("the last sample is before the end");
                    if (w.Rec("close")[0].seq != w.Out.Max(o => o.seq)) throw new Exception("the close is not the last record");
                }
            });
            Check("a_draw_in_the_sample_phase_is_reported", () =>
            {
                var w = New();
                var r = Run(w, AtTick(1100));
                Start(w, r);
                w.Play(r, 200, 6, t => { w.DrawInSample = t == 1050; });
                var f = w.Rec("fault").Where(x => x.r.GetProperty("what").GetString() == "rand_in_sample").ToList();
                Eq(f.Count, 1, "fault records");
                Eq(f[0].r.GetProperty("tick").GetInt64(), 1050L, "fault tick");
                Eq(w.One("close").GetProperty("randFaults").GetInt32(), 1, "randFaults");
            });
            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
