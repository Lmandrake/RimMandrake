// Units for JawaBenchWorldCore.cs (the PRODUCTION file, or a planted copy) joined to the PRODUCTION JawaBenchSceneTickCore.cs.
// One unit per check of RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY (design/specs/2026-11-23-bridge-v2/boundary.md
// §WORLD EVENT TAPS AND WORLD TRACKS). Prints "U <name> ok|FAIL why" and "U-count n". The game is played as in
// CastTracksSelfTest: ticks while not paused, the end-of-tick step, Settle once a frame. The taps are called as the Verse hooks
// call them: Admit or TryEnter (through Enter/EnterMessage), then the game's work, then Commit and the record, then (message
// only) the finalizer's Exit.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using W = JawaBench.BridgeTools.JawaBenchWorldCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal sealed class World : ISceneHost, IProbeSource, IWorldSource, ICastSink
    {
        public long TickNow = 1000, Seq;
        public bool PausedNow = true;
        public ulong Rand = 7;
        public double Clock;
        public long Queue;
        public bool DropAll;                     // the writer drops every row (a full disk)
        public bool MapGone;
        // the six world fields of the fake game
        public string Weather = "Clear", Conditions = "", Camera = "0,0..40,30 zoom Middle", Windows = "";
        public double Temp = 21.5, Hour = 6;
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

        // ---- IWorldSource
        public string Read(object[] v)
        {
            if (MapGone) return "gone";
            v[0] = Weather; v[1] = Conditions; v[2] = Temp; v[3] = Hour; v[4] = Camera; v[5] = Windows;
            return null;
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
        static bool Bool(JsonElement e, string k) { return e.GetProperty(k).GetBoolean(); }

        /// <summary>A world, a run whose condition ends it at tick `endAt`, the world tracks and the taps joined to it, armed and
        /// running. Thing 7 is of the cast, alias P.</summary>
        static (World w, T.SceneRun run, W.Tracks tracks, W.Taps taps) Stage(long endAt = 1030)
        {
            var w = new World();
            var spec = C.ParseJson("{\"until\":{\"cmp\":[{\"p\":\"game.tick\"},\">=\"," + endAt + "]},\"max_ticks\":500}");
            var c = new C.Compiler(w, "run").CompileSpec(spec);
            var run = new T.SceneRun("r1", c, w, new List<T.Act>(), w, "PLAY", "Ultrafast");
            var taps = new W.Taps();
            double fake = 0;
            var tracks = new W.Tracks(w, () => fake += 0.01, taps);   // each read of the clock is 0.01 ms later
            taps.Sink = () => w;
            taps.Alias = id => id == 7 ? "P" : null;
            run.World = tracks;
            w.Run = run;
            run.Arm(w.TickNow, World.Epoch);
            w.PausedNow = false;
            return (w, run, tracks, taps);
        }

        static W.Who Pawn(int id) { return new W.Who { Has = true, Id = id, Text = "Human" + id, Pawn = true }; }
        static W.Who Thing(int id, string def) { return new W.Who { Has = true, Id = id, Text = def + id, Pawn = false }; }

        /// <summary>The six rules of HOOKS.md on one tap, and its records outside the run. `call(st, ran)` does the postfix half of
        /// the tap; it writes one `rec` row. message: the guard keeps depth (TryEnter), only the outermost call writes, and the
        /// finalizer's Exit runs after each call.</summary>
        static void SixRules(string rec, Func<W.Taps, JawaBenchHookGuard> guard, Action<W.Taps, W.TapState, bool> call, bool message = false)
        {
            var (w, run, tracks, taps) = Stage();
            var g = guard(taps);
            int Rows() { return w.Rec(rec).Count; }
            bool Enter(bool main, out W.TapState st) { return message ? taps.EnterMessage(main, out st) : taps.Enter(g, main, out st); }
            void Call(W.TapState st, bool ran) { call(taps, st, ran); if (message) taps.MessageExit(st, null); }
            // 1 reentrancy: an inner call between the outer's prefix and postfix stands on its own state
            W.TapState outer, inner;
            True(Enter(true, out outer), "the outer call was not admitted");
            True(Enter(true, out inner), "the nested call was not admitted");
            Call(inner, true);
            Call(outer, true);
            if (message)
            {
                Eq(Rows(), 1, "rows after a nested pair of message calls (the outer writes it)");
                Eq(w.Rec(rec)[0].GetProperty("ord").GetInt64(), outer.Ord, "the row is the outer call's");
                Eq(taps.Inner, 1L, "the inner call is counted");
                Eq(g.Depth, 0, "the finalizers closed both scopes");
            }
            else
            {
                Eq(Rows(), 2, "rows after a nested pair");
                var ords = w.Rec(rec).Select(r => r.GetProperty("ord").GetInt64()).ToList();
                True(ords[0] > ords[1], "the inner (later entered) call keeps the later ord");
            }
            int base0 = Rows();
            // 2 skipped prefix / late install: a default state is an orphan, counted once, records nothing
            Call(default(W.TapState), true);
            Eq(Rows(), base0, "an orphan postfix wrote a row");
            Eq(g.OrphanExits, 1L, "orphans counted");
            // 3 skipped original: records nothing, counted
            W.TapState s3; Enter(true, out s3);
            Call(s3, false);
            Eq(Rows(), base0, "a skipped original wrote a row");
            Eq(g.OriginalSkipped, 1L, "skipped originals counted");
            // 4 game exception: the void finalizer counts it and does not swallow or replace it (it returns nothing)
            if (message) { W.TapState s4; Enter(true, out s4); taps.MessageExit(s4, new InvalidOperationException("the game threw")); Eq(g.Depth, 0, "a throw closes the scope"); }
            else { taps.Threw(g, new InvalidOperationException("the game threw")); taps.Threw(g, null); }
            Eq(g.OriginalThrew, 1L, "throws counted");
            // 5 off-thread: rejected before any recorder state, silent at the postfix
            long before = taps.Records + taps.Outside + taps.Dropped + taps.Inner;
            W.TapState s5;
            True(!Enter(false, out s5), "a foreign thread was admitted");
            Eq(s5.Ord, 0L, "a rejected call took an entry ordinal");
            Call(s5, true);
            Eq(Rows(), base0, "a foreign call wrote a row");
            Eq(g.ForeignRejected, 1L, "foreign calls counted");
            Eq(g.OrphanExits, 1L, "a rejected call counted as an orphan");
            Eq(taps.Records + taps.Outside + taps.Dropped + taps.Inner, before, "a foreign call touched the counts");
            // 6 writer fault: a dropped row is counted and nothing waits or throws
            w.DropAll = true;
            W.TapState s6; Enter(true, out s6);
            Call(s6, true);
            w.DropAll = false;
            True(taps.Dropped >= 1, "a row the writer dropped is counted");
            Eq(g.Faults, 0L, "a writer fault became a recorder fault");
            Eq(g.Coverage, "degraded", "coverage after orphans, skips and rejections");
            // and a record outside any running run is dropped and counted
            w.Play(run, 30);
            Eq(run.Stage, "closed", "the run closed");
            int rows = w.Out.Count;
            long out0 = taps.Outside;
            W.TapState s7; Enter(true, out s7);
            Call(s7, true);
            Eq(w.Out.Count, rows, "a record after the run wrote a row");
            True(taps.Outside > out0, "a record after the run is counted outside");
        }

        static int Main(string[] args)
        {
            Check("mental_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("mental_attempt", t => t.GMental, (t, st, ran) => t.Mental(st, ran, 7, "Berserk", "a reason", false, false, null));
            });

            Check("quest_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("quest", t => t.GQuest, (t, st, ran) => t.Quest(st, ran, 3, "OpportunitySite_ItemStash", "Stash", true, false));
                var (w, run, tracks, taps) = Stage();
                W.TapState a, b;
                taps.Enter(taps.GQuest, true, out a); taps.Quest(a, true, 4, "Hospitality_Refugee", "Refugee", true, true);
                taps.Enter(taps.GQuest, true, out b); b.Before = true; taps.Quest(b, true, 4, "Hospitality_Refugee", "Refugee", false, true);
                var q = w.Rec("quest");
                Eq(q.Count, 2, "an added and a refused quest are two rows");
                Eq(Bool(q[0], "added"), true, "added");
                Eq(Str(q[0], "refused"), null, "an added quest names no refusal");
                Eq(Bool(q[0], "accepted"), true, "initially accepted");
                Eq(Bool(q[1], "added"), false, "a quest already there is not added");
                Eq(Str(q[1], "refused"), "already there", "the refusal is named");
                Eq(q[1].GetProperty("quest").GetInt32(), 4, "the quest id");
                Eq(Str(q[1], "root"), "Hospitality_Refugee", "its root");
            });

            Check("letter_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("letter", t => t.GLetter, (t, st, ran) => t.Letter(st, ran, "NegativeEvent", "Raid", 0, true, -1, "Human7"));
                var (w, run, tracks, taps) = Stage();
                W.TapState a, b, c;
                taps.Enter(taps.GLetter, true, out a); taps.Letter(a, true, "NeutralEvent", "Later", 120, false, 9, null);
                taps.Enter(taps.GLetter, true, out b); taps.Letter(b, true, "NeutralEvent", "Later", 0, true, 9, null);
                taps.Enter(taps.GLetter, true, out c); taps.Letter(c, true, "NeutralEvent", "Hidden", 0, false, -1, null);
                var l = w.Rec("letter");
                Eq(l.Count, 3, "letter rows");
                Eq(Bool(l[0], "queued") + "/" + Bool(l[0], "shown"), "True/False", "a delayed letter is queued, not shown");
                Eq(l[0].GetProperty("delay").GetInt32(), 120, "its delay");
                Eq(l[0].GetProperty("quest").GetInt32(), 9, "its quest");
                Eq(Bool(l[1], "queued") + "/" + Bool(l[1], "shown"), "False/True", "its arrival is shown");
                Eq(Bool(l[2], "queued") + "/" + Bool(l[2], "shown"), "False/False", "a letter that cannot show is neither");
                Eq(l[2].GetProperty("quest").ValueKind, JsonValueKind.Null, "no quest");
            });

            Check("message_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("message", t => t.GMessage, (t, st, ran) => t.Message(st, ran, "A message", "NeutralEvent", true, null), message: true);
            });

            Check("fire_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("fire", t => t.GFire, (t, st, ran) => t.Fire(st, ran, 500, "10,10", default(W.Who), Pawn(7), 0.1, false));
                var (w, run, tracks, taps) = Stage();
                W.TapState a, b, c;
                taps.Enter(taps.GFire, true, out a); taps.Fire(a, true, 501, "11,10", default(W.Who), Pawn(7), 0.5, false);          // a pawn lit it
                taps.Enter(taps.GFire, true, out b); taps.Fire(b, true, 502, "12,10", Pawn(7), Thing(80, "Shell"), 0.2, false);      // a thing set a pawn on fire
                taps.Enter(taps.GFire, true, out c); taps.Fire(c, true, 503, "13,10", default(W.Who), default(W.Who), 0.1, true);    // a load restored it
                var f = w.Rec("fire");
                Eq(f.Count, 2, "a load's fire is not a start");
                Eq(taps.Loaded, 1L, "it is counted");
                Eq(Str(f[0], "instigator") + " " + Str(f[0], "instigatorKind") + " " + Str(f[0], "instigatorAlias"), "Human7 pawn P", "a fire lit by a cast pawn");
                Eq(Str(f[0], "attached"), null, "a fire on a cell is attached to nothing");
                Eq(Str(f[1], "instigator") + " " + Str(f[1], "instigatorKind") + " " + Str(f[1], "instigatorAlias"), "Shell80 thing ", "a fire lit by a thing");
                Eq(Str(f[1], "attached") + " " + Str(f[1], "attachedAlias"), "Human7 P", "what it burns on");
                Eq(Str(f[1], "cell"), "12,10", "its cell");
            });

            Check("explosion_tap_follows_the_six_hook_rules", () =>
            {
                SixRules("explosion", t => t.GExplosion, (t, st, ran) => t.Explosion(st, ran, "20,20", 2.9, "Bomb", Pawn(7), "Weapon_GrenadeFrag", null));
                var (w, run, tracks, taps) = Stage();
                W.TapState a, b;
                taps.Enter(taps.GExplosion, true, out a); taps.Explosion(a, true, "20,20", 3.9, "Bomb", Pawn(7), "Gun_DoomsdayRocket", "Bullet_DoomsdayRocket");
                taps.Enter(taps.GExplosion, true, out b); taps.Explosion(b, true, "30,30", 1.9, "Flame", default(W.Who), null, null);
                var x = w.Rec("explosion");
                Eq(x.Count, 2, "explosion rows");
                Eq(Str(x[0], "instigator") + " " + Str(x[0], "instigatorKind") + " " + Str(x[0], "instigatorAlias"), "Human7 pawn P", "its instigator");
                Eq(Str(x[0], "weapon") + " " + Str(x[0], "projectile"), "Gun_DoomsdayRocket Bullet_DoomsdayRocket", "its weapon and projectile");
                Eq(x[0].GetProperty("radius").GetDouble(), 3.9, "its radius");
                Eq(Str(x[1], "instigatorKind"), "none", "an explosion with no instigator says so");
                Eq(Str(x[1], "damage"), "Flame", "its damage");
            });

            Check("an_attempt_and_a_start_are_two_records", () =>
            {
                var (w, run, tracks, taps) = Stage();
                w.Play(run, 1, 1);
                W.TapState a, b;
                taps.Enter(taps.GMental, true, out a); a.Prev = null;
                taps.Mental(a, true, 7, "Berserk", "insult", false, true, "Berserk");          // started
                taps.Enter(taps.GMental, true, out b); b.Prev = "Berserk";
                taps.Mental(b, true, 7, "Berserk", null, true, false, "Berserk");              // refused: the same state
                var at = w.Rec("mental_attempt"); var st = w.Rec("mental_start");
                Eq(at.Count, 2, "two attempts");
                Eq(st.Count, 1, "one start");
                Eq(Bool(at[0], "started") + "/" + Bool(at[1], "started"), "True/False", "started or not");
                Eq(Str(at[1], "prev"), "Berserk", "what the refused attempt found");
                Eq(Bool(at[1], "forced"), true, "forced");
                Eq(st[0].GetProperty("ord").GetInt64(), at[0].GetProperty("ord").GetInt64(), "the start is the first attempt's");
                True(at[0].GetProperty("n").GetInt32() < st[0].GetProperty("n").GetInt32(), "the attempt is written before its start");
                Eq(Str(st[0], "alias") + " " + Str(st[0], "state") + " " + Str(st[0], "now"), "P Berserk Berserk", "the start names the pawn and the state");
                Eq(Str(at[0], "phase"), "in_tick", "a tap record is in_tick");
            });

            Check("a_message_is_recorded_before_the_rule_that_hides_repeats", () =>
            {
                var (w, run, tracks, taps) = Stage();
                W.TapState a, b, o, i;
                taps.EnterMessage(true, out a); taps.Message(a, true, "Smoke seen", "NeutralEvent", true, "10,10"); taps.MessageExit(a, null);
                // the same text and targets again: the repeat rule hides it (no live message is added), the tap still records it
                taps.EnterMessage(true, out b); taps.Message(b, true, "Smoke seen", "NeutralEvent", false, "10,10"); taps.MessageExit(b, null);
                // a string overload whose inner Message(Message) is hidden: one record, the outer call's
                taps.EnterMessage(true, out o); taps.EnterMessage(true, out i);
                taps.Message(i, true, "Inner", "NeutralEvent", false, null); taps.MessageExit(i, null);
                taps.Message(o, true, "Inner", "NeutralEvent", false, null); taps.MessageExit(o, null);
                var m = w.Rec("message");
                Eq(m.Count, 3, "every message call is recorded, the hidden repeats too");
                Eq(Bool(m[0], "shown") + "/" + Bool(m[1], "shown"), "True/False", "the first shown, the repeat hidden");
                Eq(Str(m[1], "hidden"), "a live message with the same text and targets", "the hiding rule is named");
                Eq(Str(m[1], "text") + " " + Str(m[1], "targets"), "Smoke seen 10,10", "the hidden repeat keeps its text and targets");
                Eq(m[2].GetProperty("ord").GetInt64(), o.Ord, "the nested pair is the outer call's record");
            });

            Check("the_world_tracks_write_on_change_and_their_cost_is_in_the_result", () =>
            {
                var (w, run, tracks, taps) = Stage(1010);
                w.Play(run, 30, 6, t =>
                {
                    if (t == 1003) { w.Weather = "Rain"; w.Conditions = "Eclipse"; w.Windows = "Dialog_MessageBox"; }
                    if (t == 1005) { w.Temp = 19.0; w.Hour = 7; w.Camera = "5,5..45,35 zoom Close"; w.Windows = ""; }
                });
                Eq(run.Stage, "closed", "the run closed");
                foreach (var f in W.Fields)
                {
                    var rows = w.Track("world." + f);
                    True(rows.Count >= 2, "world." + f + ": a first and a last row");
                    True(rows.All(r => Str(r, "st") == "ok"), "world." + f + ": read ok");
                }
                Eq(w.Track("world.weather").Count(r => Str(r, "phase") == "end_of_tick"), 1, "one weather row for one change");
                var wr = w.Track("world.weather").First(r => Str(r, "phase") == "end_of_tick");
                Eq(wr.GetProperty("tick").GetInt64() + " " + Str(wr, "v"), "1003 Rain", "the weather row on the tick of its change");
                Eq(w.Track("world.windows").Count(r => Str(r, "phase") == "end_of_tick"), 2, "a window opened and closed: two rows");
                Eq(w.Track("world.hour").Count(r => Str(r, "phase") == "end_of_tick"), 1, "the hour row on its change");
                Eq(w.Track("world.camera").Count(r => Str(r, "phase") == "end_of_tick"), 1, "the camera row on its change");
                var c = w.Rec("close").Single().GetProperty("world");
                Eq(c.GetProperty("tracks").GetInt32(), W.Fields.Length, "tracks");
                Eq(c.GetProperty("samples").GetInt64(), 12L, "samples: first, ten ticks, last");
                True(c.GetProperty("msPerTick").GetDouble() > 0, "msPerTick is measured");
                True(Math.Abs(c.GetProperty("msPerTick").GetDouble() - c.GetProperty("ms").GetDouble() / 12) < 1e-3, "msPerTick is ms over samples");
                True(c.TryGetProperty("taps", out var tp) && tp.GetProperty("hooks").GetArrayLength() == 6, "the six taps' coverage is in the result");
                // a map that is gone is a row with its state, never a silent hole
                var (w2, run2, tracks2, taps2) = Stage(1004);
                w2.Play(run2, 30, 6, t => { if (t == 1002) w2.MapGone = true; });
                var g = w2.Track("world.weather").Where(r => Str(r, "st") == "gone").ToList();
                True(g.Count >= 1 && g[0].GetProperty("tick").GetInt64() == 1002, "a gone map is a `gone` row on its tick");
            });

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
