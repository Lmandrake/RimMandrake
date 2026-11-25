// Units for JawaBenchCastCore.cs (the PRODUCTION file, or a planted copy) joined to the PRODUCTION JawaBenchSceneTickCore.cs.
// One unit per check of RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY (design/specs/2026-11-23-bridge-v2/boundary.md
// §CAST TRACKS AND JOB TAPS). Prints "U <name> ok|FAIL why" and "U-count n". The game is played by World.Play, as in
// SceneTickSelfTest: ticks while not paused, the end-of-tick step, Settle once a frame. The taps are called as the Verse hooks
// call them: Admit (through Enter), then the game's work, then Commit and the record (through JobStart/JobEnd/Reserve).
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using K = JawaBench.BridgeTools.JawaBenchCastCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    /// <summary>One pawn of the fake game.</summary>
    internal sealed class FakePawn
    {
        public int Id, Corpse = -1;
        public int X = 10, Z = 10, Toil = 0, JobId = 1;
        public string JobDef = "Goto";
        public bool Dead, Downed, Drafted;
        public double Health = 100;
        public object[] Fill(object[] v, bool corpse)
        {
            v[0] = X + "," + Z; v[1] = "south"; v[2] = JobDef == null ? null : JobDef + "#" + JobId; v[3] = JobDef == null ? null : (object)(double)Toil;
            v[4] = Health; v[5] = Downed; v[6] = Dead; v[7] = null; v[8] = null; v[9] = corpse ? "map" : "map"; v[10] = "PlayerColony#1"; v[11] = Drafted;
            return v;
        }
    }

    internal sealed class World : ISceneHost, IProbeSource, ICastSource, ICastSink
    {
        public long TickNow = 1000, Seq;
        public bool PausedNow = true;
        public ulong Rand = 7;
        public double Clock;
        public long Queue;
        public bool DropAll;                     // the writer drops every row (a full disk)
        public readonly Dictionary<int, FakePawn> Pawns = new Dictionary<int, FakePawn>();
        public readonly Dictionary<int, FakePawn> Corpses = new Dictionary<int, FakePawn>();
        public readonly List<(long seq, JsonElement r)> Out = new List<(long, JsonElement)>();
        public T.SceneRun Run;

        // ---- ISceneHost
        public long Enqueue(string fields)
        {
            var e = JsonDocument.Parse("{" + fields + "}").RootElement;
            if (DropAll) return -1;
            Seq++;
            Queue++;
            Out.Add((Seq, e));
            return Seq;
        }
        public bool Drained() { return Queue == 0; }
        public bool Pause() { PausedNow = true; return true; }
        public long Tick() { return TickNow; }
        public ulong RandState() { return Rand; }
        public double NowMs() { return Clock; }
        public long? AllocBytes() { return null; }

        // ---- IProbeSource
        public int CurrentMap() { return 0; }
        public bool MapSize(int m, out int x, out int z) { x = z = 250; return m == 0; }
        public string Refuse(string key, C.Probe p) { return null; }
        public CondRead Read(string key, C.Probe p, int x, int z)
        {
            if (p.Name == "game.tick") return new CondRead((double)TickNow, "ok", "");
            return new CondRead(null, "error", "no value for " + key);
        }

        // ---- ICastSource
        public int Successor(int thing, out string why)
        {
            why = null;
            FakePawn p;
            if (!Pawns.TryGetValue(thing, out p) || !p.Dead || p.Corpse < 0) return -1;
            why = "dead: its corpse";
            return p.Corpse;
        }
        public string Read(int thing, object[] into)
        {
            FakePawn p;
            if (Pawns.TryGetValue(thing, out p)) { p.Fill(into, false); return null; }
            if (Corpses.TryGetValue(thing, out p)) { p.Fill(into, true); return null; }
            return "gone";
        }

        // ---- ICastSink (the Verse half's Sink: the live run, or outside)
        public long EmitTap(string rec, string fields) { return Run == null ? -2 : Run.EmitTap(rec, fields); }

        public void Play(T.SceneRun run, int frames, int perFrame = 6, Action<long> during = null)
        {
            for (int f = 0; f < frames && run.Stage != "closed"; f++)
            {
                Clock += 16;
                run.Settle();
                for (int i = 0; i < perFrame && !PausedNow; i++)
                {
                    TickNow++;
                    if (during != null) during(TickNow);
                    run.OnTickEnd(TickNow, Epoch, true);
                }
                Queue = 0;
            }
        }
        public static readonly object Epoch = 1.0;
        public List<JsonElement> Rec(string rec) { return Out.Where(o => o.r.GetProperty("rec").GetString() == rec).Select(o => o.r).ToList(); }
        public List<JsonElement> Track(string name) { return Rec("track").Where(r => r.GetProperty("name").GetString() == name).ToList(); }
    }

    internal static class Program
    {
        static int _n, _bad;

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w));
        }

        static void Eq(object a, object b, string what) { if (!Equals(a, b)) throw new Exception(what + ": got " + a + ", want " + b); }
        static void True(bool b, string what) { if (!b) throw new Exception(what); }
        static string Str(JsonElement e, string k) { var v = e.GetProperty(k); return v.ValueKind == JsonValueKind.Null ? null : v.ToString(); }

        /// <summary>A world with pawn 7 as alias P (and more pawns as Q, R...), a run whose condition ends it at tick `end`, the cast
        /// and the taps joined to it, armed and running.</summary>
        static (World w, T.SceneRun run, K.Cast cast, K.Taps taps) Stage(long endAt = 1030, params int[] more)
        {
            var w = new World();
            w.Clock = 0;
            var ids = new List<int> { 7 };
            ids.AddRange(more);
            var names = "PQRSTU";
            var members = new List<KeyValuePair<string, int>>();
            for (int i = 0; i < ids.Count; i++) { w.Pawns[ids[i]] = new FakePawn { Id = ids[i] }; members.Add(new KeyValuePair<string, int>(names[i].ToString(), ids[i])); }
            var spec = C.ParseJson("{\"until\":{\"cmp\":[{\"p\":\"game.tick\"},\">=\"," + endAt + "]},\"max_ticks\":500}");
            var c = new C.Compiler(w, "run").CompileSpec(spec);
            var run = new T.SceneRun("r1", c, w, new List<T.Act>(), w, "PLAY", "Ultrafast");
            var taps = new K.Taps();
            double fake = 0;
            var cast = new K.Cast(members, w, () => fake += 0.01, taps);   // each read of the clock is 0.01 ms later
            taps.Sink = () => w;
            taps.CastNow = () => run.Running ? cast : null;
            run.Cast = cast;
            w.Run = run;
            run.Arm(w.TickNow, World.Epoch);
            w.PausedNow = false;
            return (w, run, cast, taps);
        }

        static K.JobSnap Job(string def, int id, int toil = 0) { return new K.JobSnap { Has = true, Def = def, Id = id, Toil = toil }; }

        /// <summary>The six rules of HOOKS.md on one tap. `call(st, ran)` does the postfix half of the tap for pawn 7; `g` is its guard.</summary>
        static void SixRules(string rec, Func<K.Taps, JawaBenchHookGuard> guard, Action<K.Taps, K.TapState, bool> call)
        {
            var (w, run, cast, taps) = Stage();
            var g = guard(taps);
            int Rows() { return w.Rec(rec).Count; }
            // 1 reentrancy: an inner call between the outer's prefix and postfix stands on its own state
            K.TapState outer, inner;
            True(taps.Enter(g, true, out outer, Job("Outer", 11)), "the outer call was not admitted");
            True(taps.Enter(g, true, out inner, Job("Inner", 12)), "the nested call was not admitted");
            call(taps, inner, true);
            call(taps, outer, true);
            Eq(Rows(), 2, "rows after a nested pair");
            var ords = w.Rec(rec).Select(r => r.GetProperty("ord").GetInt64()).ToList();
            Eq(ords[0] > ords[1], true, "the inner (later entered) call keeps the later ord");
            // 2 skipped prefix / late install: a default state is an orphan, counted, records nothing
            call(taps, default(K.TapState), true);
            Eq(Rows(), 2, "an orphan postfix wrote a row");
            Eq(g.OrphanExits, 1L, "orphans counted");
            // 3 skipped original: records nothing, counted
            K.TapState s3; taps.Enter(g, true, out s3, Job("Skipped", 13));
            call(taps, s3, false);
            Eq(Rows(), 2, "a skipped original wrote a row");
            Eq(g.OriginalSkipped, 1L, "skipped originals counted");
            // 4 game exception: the void finalizer counts it and does not swallow or replace it (it returns nothing)
            taps.Threw(g, new InvalidOperationException("the game threw"));
            taps.Threw(g, null);
            Eq(g.OriginalThrew, 1L, "throws counted");
            // 5 off-thread: rejected before any recorder state, silent at the postfix
            long before = taps.Records + taps.Outside + taps.NotCast + taps.Dropped;
            K.TapState s5;
            True(!taps.Enter(g, false, out s5, Job("Foreign", 14)), "a foreign thread was admitted");
            Eq(s5.Ord, 0L, "a rejected call took an entry ordinal");
            Eq(s5.Prev.Has, false, "a rejected call stored what it saw");
            call(taps, s5, true);
            Eq(Rows(), 2, "a foreign call wrote a row");
            Eq(g.ForeignRejected, 1L, "foreign calls counted");
            Eq(g.OrphanExits, 1L, "a rejected call counted as an orphan");
            Eq(taps.Records + taps.Outside + taps.NotCast + taps.Dropped, before, "a foreign call touched the counts");
            // 6 writer fault: a dropped row is counted and nothing waits or throws
            w.DropAll = true;
            K.TapState s6; taps.Enter(g, true, out s6, Job("Dropped", 15));
            call(taps, s6, true);
            w.DropAll = false;
            Eq(taps.Dropped, 1L, "a row the writer dropped is counted");
            Eq(g.Faults, 0L, "a writer fault became a recorder fault");
            Eq(g.Coverage, "degraded", "coverage after orphans, skips and rejections");
        }

        static int Main(string[] args)
        {
            Check("job_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("job_start", t => t.GStart, (t, st, ran) => t.JobStart(st, ran, 7, Job("Haul", 20 + (int)st.Ord), "JobGiver_Work", "InterruptForced", true));
                SixRules("job_end", t => t.GEnd, (t, st, ran) => t.JobEnd(st, ran, 7, "Succeeded"));
            });

            Check("reserve_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("reserve", t => t.GReserve, (t, st, ran) => t.Reserve(st, ran, 7, Job("Haul", 30), "Steel123", false, "Pawn_Other"));
                var (w, run, cast, taps) = Stage();
                K.TapState a, b;
                taps.Enter(taps.GReserve, true, out a); taps.Reserve(a, true, 7, Job("Haul", 31), "Steel1", true, null);
                taps.Enter(taps.GReserve, true, out b); taps.Reserve(b, true, 7, Job("Haul", 31), "Steel2", false, "Human99");
                var r = w.Rec("reserve");
                Eq(r.Count, 2, "a made and a refused reservation are two rows");
                Eq(r[0].GetProperty("made").GetBoolean(), true, "made");
                Eq(Str(r[0], "holder"), null, "a made reservation names no holder");
                Eq(r[1].GetProperty("made").GetBoolean(), false, "refused");
                Eq(Str(r[1], "holder"), "Human99", "a refusal names who holds it");
                Eq(Str(r[1], "alias"), "P", "the row names the alias");
            });

            Check("a_job_start_names_the_job_it_replaced", () =>
            {
                var (w, run, cast, taps) = Stage();
                K.TapState st, en;
                taps.Enter(taps.GStart, true, out st, Job("Goto", 1, 2));
                taps.Enter(taps.GEnd, true, out en, Job("Goto", 1, 2));        // StartJob ends the old job inside itself
                taps.JobEnd(en, true, 7, "InterruptForced");
                taps.JobStart(st, true, 7, Job("Haul", 2), "JobGiver_Work", "InterruptForced", true);
                var s = w.Rec("job_start"); var e = w.Rec("job_end");
                Eq(s.Count, 1, "job_start rows"); Eq(e.Count, 1, "job_end rows");
                Eq(Str(s[0], "job"), "Haul#2", "the new job");
                Eq(Str(s[0], "giver"), "JobGiver_Work", "who gave it");
                Eq(Str(s[0], "prev"), "Goto#1", "the job it replaced");
                Eq(Str(s[0], "prevEnd"), "InterruptForced", "the end condition of the job it replaced");
                Eq(Str(e[0], "job"), "Goto#1", "the job that ended");
                Eq(Str(e[0], "cond"), "InterruptForced", "its end condition");
                Eq(e[0].GetProperty("toil").GetInt32(), 2, "the toil it ended on");
                True(e[0].GetProperty("n").GetInt32() < s[0].GetProperty("n").GetInt32(), "the end is written before the start");
                K.TapState first;                                               // a first job: no job replaced
                taps.Enter(taps.GStart, true, out first);
                taps.JobStart(first, true, 7, Job("Wait", 3), "direct", "InterruptForced", true);
                Eq(Str(w.Rec("job_start")[1], "prev"), null, "a first job names no previous job");
                Eq(Str(w.Rec("job_start")[1], "prevEnd"), null, "and no end condition");
            });

            Check("two_job_starts_in_one_tick_keep_their_order", () =>
            {
                var (w, run, cast, taps) = Stage(1030, 8);
                w.Play(run, 1, 1);                                              // one tick in
                long tick = w.TickNow;
                K.TapState a, b;
                taps.Enter(taps.GStart, true, out a); taps.JobStart(a, true, 7, Job("Haul", 40), "g", "None", true);
                taps.Enter(taps.GStart, true, out b); taps.JobStart(b, true, 8, Job("Haul", 41), "g", "None", true);
                // a start inside a start (an opportunistic job): the inner postfix writes first, the entry ordinal keeps the call order
                K.TapState o, i;
                taps.Enter(taps.GStart, true, out o); taps.Enter(taps.GStart, true, out i);
                taps.JobStart(i, true, 7, Job("Clean", 43), "opportunistic", "None", true);
                taps.JobStart(o, true, 7, Job("Haul", 42), "g", "None", false);
                var s = w.Rec("job_start");
                Eq(s.Count, 4, "rows");
                True(s.All(r => r.GetProperty("tick").GetInt64() == tick), "all on one tick");
                True(s.All(r => Str(r, "phase") == "in_tick"), "phase in_tick");
                var n = s.Select(r => r.GetProperty("n").GetInt32()).ToList();
                True(n[0] < n[1] && n[1] < n[2] && n[2] < n[3], "n follows the record order");
                Eq(Str(s[0], "job") + " " + Str(s[1], "job"), "Haul#40 Haul#41", "two starts in one tick in their order");
                var ord = s.Select(r => r.GetProperty("ord").GetInt64()).ToList();
                True(ord[0] < ord[1], "sequential starts: ord in call order");
                True(ord[3] < ord[2], "nested starts: the outer call has the lower ord although its row is later");
            });

            Check("a_record_outside_any_run_is_dropped_and_counted", () =>
            {
                var (w, run, cast, taps) = Stage(1003);
                K.TapState a;
                taps.Enter(taps.GStart, true, out a); taps.JobStart(a, true, 99, Job("Haul", 50), "g", "None", true);
                Eq(taps.NotCast, 1L, "a pawn outside the cast is counted, not written");
                w.Play(run, 30);                                                 // the run ends at 1003 and closes
                Eq(run.Stage, "closed", "the run closed");
                int rows = w.Out.Count;
                K.TapState b;
                taps.Enter(taps.GStart, true, out b); taps.JobStart(b, true, 7, Job("Haul", 51), "g", "None", true);
                taps.Kill(7, "damage Cut");
                Eq(w.Out.Count, rows, "a record after the run wrote a row");
                Eq(taps.Outside, 2L, "the job start and the kill outside the run are counted");
                Eq(taps.Records, 0L, "nothing was recorded");
                // inside the run but after its end (settling): the sink itself says outside
                var (w2, run2, cast2, taps2) = Stage(1003);
                w2.Play(run2, 1);
                Eq(run2.Stage, "settling", "the run is settling");
                taps2.CastNow = () => cast2;                                    // a cast still named, the run no longer running
                K.TapState c;
                taps2.Enter(taps2.GReserve, true, out c); taps2.Reserve(c, true, 7, Job("Haul", 52), "X", true, null);
                Eq(taps2.Outside, 1L, "a record while the run settles is outside it");
                Eq(w2.Rec("reserve").Count, 0, "and is not written");
            });

            Check("an_alias_whose_object_is_replaced_writes_a_link", () =>
            {
                var (w, run, cast, taps) = Stage(1020);
                w.Play(run, 20, 6, t => { if (t == 1005) { var p = w.Pawns[7]; p.Dead = true; p.Corpse = 70; w.Corpses[70] = p; p.X = 12; } });
                var links = w.Rec("link");
                Eq(links.Count, 1, "link rows");
                Eq(Str(links[0], "alias"), "P", "the alias");
                Eq(links[0].GetProperty("from").GetInt32(), 7, "from the pawn");
                Eq(links[0].GetProperty("to").GetInt32(), 70, "to its corpse");
                Eq(links[0].GetProperty("tick").GetInt64(), 1005L, "on the tick of the change");
                var pos = w.Track("P.pos").Where(r => r.GetProperty("tick").GetInt64() == 1005).ToList();
                True(pos.Count == 1 && links[0].GetProperty("n").GetInt32() < pos[0].GetProperty("n").GetInt32(), "the link comes before the rows it explains");
                True(cast.Members[0].Thing == 70 && cast.IsCast(7) && cast.IsCast(70), "the alias is on the corpse, and both ids are of the cast");
                Eq(w.Rec("link").Count, 1, "one link, not one a tick");
            });

            Check("a_track_on_a_replaced_job_rebinds", () =>
            {
                var (w, run, cast, taps) = Stage(1020);
                w.Play(run, 20, 6, t => { if (t == 1004) { var p = w.Pawns[7]; p.JobDef = "Haul"; p.JobId = 2; p.Toil = 0; } });   // the same index
                var rb = w.Rec("rebind");
                Eq(rb.Count, 1, "rebind rows");
                Eq(Str(rb[0], "name"), "P.toil", "the toil track");
                Eq(Str(rb[0], "from") + " -> " + Str(rb[0], "to"), "Goto#1 -> Haul#2", "from the old job to the new");
                var toil = w.Track("P.toil").Where(r => r.GetProperty("tick").GetInt64() == 1004).ToList();
                Eq(toil.Count, 1, "the toil row on the new job, although its index is the same");
                True(rb[0].GetProperty("n").GetInt32() < toil[0].GetProperty("n").GetInt32(), "the rebind comes before the toil row");
                Eq(w.Track("P.toil").Count(r => Str(r, "phase") == "end_of_tick"), 1, "no toil row without a change");
            });

            Check("settle_catches_a_death_with_no_kill_record", () =>
            {
                foreach (bool killed in new[] { false, true })
                {
                    var (w, run, cast, taps) = Stage(1012);
                    w.Play(run, 30, 6, t => { if (t == 1006) { w.Pawns[7].Dead = true; if (killed) taps.Kill(7, "damage Bullet"); } });
                    Eq(run.Stage, "closed", "the run closed");
                    var rc = w.Rec("reconcile");
                    var close = w.Rec("close").Single();
                    var listed = close.GetProperty("cast").GetProperty("reconcile").GetArrayLength();
                    if (killed)
                    {
                        Eq(w.Rec("kill").Count, 1, "the kill record");
                        Eq(rc.Count, 0, "a death with its kill record is reconciled clean");
                        Eq(listed, 0, "close lists nothing");
                    }
                    else
                    {
                        Eq(rc.Count, 1, "reconcile rows");
                        Eq(Str(rc[0], "alias"), "P", "the alias");
                        Eq(Str(rc[0], "verdict"), "COULD NOT LOOK", "the verdict");
                        Eq(rc[0].GetProperty("deadAt").GetInt64(), 1006L, "the tick the death was seen");
                        Eq(listed, 1, "close lists it");
                        var cl = w.Out.Last().r;
                        Eq(Str(cl, "rec"), "close", "close is still the last record");
                    }
                }
            });

            Check("the_per_tick_cost_of_the_tracks_is_in_the_result", () =>
            {
                var (w, run, cast, taps) = Stage(1010, 8);
                w.Play(run, 30);
                var c = w.Rec("close").Single().GetProperty("cast");
                Eq(c.GetProperty("members").GetInt32(), 2, "members");
                Eq(c.GetProperty("tracks").GetInt32(), 2 * K.Fields.Length, "tracks");
                Eq(c.GetProperty("samples").GetInt64(), 12L, "samples: first, ten ticks, last");
                True(c.GetProperty("msPerTick").GetDouble() > 0, "msPerTick is measured");
                True(Math.Abs(c.GetProperty("msPerTick").GetDouble() - c.GetProperty("ms").GetDouble() / 12) < 1e-3, "msPerTick is ms over samples");
                True(c.GetProperty("msMax").GetDouble() > 0, "msMax");
                True(c.TryGetProperty("taps", out var tp) && tp.GetProperty("hooks").GetArrayLength() == 3, "the three taps' coverage is in the result");
                Eq(w.Track("P.pos").Count, 2, "one first and one last row for an unchanged field");
            });

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
