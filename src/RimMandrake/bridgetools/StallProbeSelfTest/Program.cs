// Program.cs - units for the stall probe's "top job" read (BRIDGE_STALL_DIAGNOSTIC_1). Prints "U name ok|FAIL why" and
// "U-count n"; driven by src/RimMandrake/Utils/selftest_stall_probe.py, which also builds the mutants that must go red.
// The main thread is played by ProfilerSeam.TlPre / TlFin: the profiler's own probe lines, cut from its text.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    internal sealed class StubStuckDriver : JobDriver { }

    /// <summary>A thing that moves the "main thread" on while the probe reads it: its def getter enters another list.</summary>
    internal sealed class MovingThing : Thing
    {
        internal TickList Next; internal int NextTick;
        public override ThingDef def
        {
            get { if (Next != null) { Current.Game.tickManager.TicksGame = NextTick; ProfilerSeam.TlPre(Next); } return base.def; }
            set => base.def = value;
        }
    }

    internal static class Program
    {
        static readonly List<string> Fails = new List<string>();
        static void Check(bool ok, string why) { if (!ok) Fails.Add(why); }

        static Thing T(string def) => new Thing { def = new ThingDef { defName = def } };
        static Pawn P(string id, string job, JobDriver driver, int x, int z) => new Pawn
        {
            def = new ThingDef { defName = "Human" }, ThingID = id, Position = new IntVec3(x, 0, z),
            jobs = new Pawn_JobTracker { curJob = job == null ? null : new Job { def = new JobDef { defName = job } }, curDriver = driver }
        };

        static JsonElement Read()
        {
            string s = JawaBenchStallDump.Probe();
            using (var d = JsonDocument.Parse(s)) return d.RootElement.Clone();
        }
        static string Str(JsonElement e, string k) => e.TryGetProperty(k, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;
        static int? Int(JsonElement e, string k) => e.TryGetProperty(k, out var v) && v.ValueKind == JsonValueKind.Number ? v.GetInt32() : (int?)null;
        static bool IsNull(JsonElement e, string k) => e.TryGetProperty(k, out var v) && v.ValueKind == JsonValueKind.Null;

        static void Fresh(int ticks)
        {
            Current.Game = new Game();
            Current.Game.tickManager.TicksGame = ticks;
            // reset the probe's main-thread state by reflection, so this harness also builds against an older probe
            // (the selftest's whole-commit-reverted mutant) and that probe fails a UNIT, not the build
            var t = typeof(JawaBenchStallProbe);
            const System.Reflection.BindingFlags F = System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic |
                                                     System.Reflection.BindingFlags.Public;
            t.GetField("CurTickList", F)?.SetValue(null, null);
            t.GetField("CurTick", F)?.SetValue(null, -1);
            JawaBenchTpsProfiler.Installed = true;
        }

        // Install binds the production read as the dump's probe and warms every path without error.
        static void ProbeInstall()
        {
            Fresh(0);
            JawaBenchStallDump.Probe = null;
            JawaBenchStallProbe.Install();
            Check(JawaBenchStallProbe.InstallError == null, "Install failed: " + JawaBenchStallProbe.InstallError);
            Check(JawaBenchStallDump.Probe != null, "Install did not bind JawaBenchStallDump.Probe");
            var r = Read();
            Check(IsNull(r, "tickList"), "before any tick list, tickList must be null: " + r);
        }

        // A stall OUTSIDE any tick list (a bridge call, a long event, the UI) reads tickList null, never the last list left.
        static void ProbeOutsideTickList()
        {
            Fresh(500);
            var normal = new TickList(TickerType.Normal);
            normal.thingLists[0].Add(P("PawnInside", "GotoWander", null, 1, 1));
            ProfilerSeam.TlPre(normal);
            var inside = Read();
            Check(Str(inside, "tickList") == "Normal", "inside TickList.Tick the probe must name it: " + inside);
            Check(Int(inside, "enteredTick") == 500, "inside, enteredTick must be the tick entered on (500): " + inside);
            ProfilerSeam.TlFin(default(JawaBenchHookGuard.Scope));
            Check(ProfilerSeam.Ends == 1, "TlFin must still close the profiler scope (End), ends=" + ProfilerSeam.Ends);
            Current.Game.tickManager.TicksGame = 777;
            var outside = Read();
            Check(IsNull(outside, "tickList"), "after TlFin a stall must read tickList null, not the stale list: " + outside);
            Check(!outside.TryGetProperty("bucket", out _) && !outside.TryGetProperty("pawns", out _),
                  "outside a tick list no bucket or pawns may be reported: " + outside);
            Check(Int(outside, "ticksGameNow") == 777, "ticksGameNow is the live clock (777): " + outside);
        }

        // The bucket is the one for the tick the list was ENTERED on, its pawns name their job and driver.
        static void ProbeBucketByEnteredTick()
        {
            Fresh(1234);
            var rare = new TickList(TickerType.Rare);
            var stuck = P("PawnStuck", "RM_StuckJob", new StubStuckDriver(), 3, 7);
            rare.thingLists[1234 % 250].AddRange(new[] { stuck, T("Steel"), T("Steel"), null, T("Plasteel") });
            rare.thingLists[1235 % 250].Add(P("PawnDecoy", "DecoyJob", null, 9, 9));
            ProfilerSeam.TlPre(rare);
            Current.Game.tickManager.TicksGame = 1235;     // the clock has moved past the tick the list was entered on
            var r = Read();
            Check(Str(r, "tickList") == "Rare", "tickList Rare: " + r);
            Check(Int(r, "enteredTick") == 1234, "enteredTick 1234: " + r);
            Check(Int(r, "ticksGameNow") == 1235, "ticksGameNow 1235: " + r);
            Check(Int(r, "bucket") == 234, "bucket must be enteredTick % 250 = 234, not the live clock's: " + r);
            Check(Int(r, "bucketCount") == 5, "bucketCount 5 (a null slot counts as a slot): " + r);
            var defs = r.TryGetProperty("topDefs", out var td) ? td.EnumerateArray().ToList() : new List<JsonElement>();
            Check(defs.Count == 3 && Str(defs[0], "def") == "Steel" && Int(defs[0], "n") == 2,
                  "topDefs must lead with Steel x2 among 3 defs: " + r);
            var pawns = r.TryGetProperty("pawns", out var pa) ? pa.EnumerateArray().ToList() : new List<JsonElement>();
            Check(pawns.Count == 1, "exactly the bucket's one pawn: " + r);
            if (pawns.Count == 1)
            {
                Check(Str(pawns[0], "id") == "PawnStuck" && Str(pawns[0], "job") == "RM_StuckJob", "pawn job RM_StuckJob: " + r);
                Check(Str(pawns[0], "driver") == typeof(StubStuckDriver).FullName, "pawn driver type: " + r);
                Check(Str(pawns[0], "pos") == "3,7", "pawn pos 3,7: " + r);
            }
            Check(r.TryGetProperty("changedDuringRead", out var c) && c.ValueKind == JsonValueKind.False,
                  "a still main thread reads changedDuringRead false: " + r);
            ProfilerSeam.TlFin(default(JawaBenchHookGuard.Scope));

            Fresh(4001);
            var lng = new TickList(TickerType.Long);
            lng.thingLists[1].Add(T("RM_LongThing"));
            ProfilerSeam.TlPre(lng);
            Current.Game.tickManager.TicksGame = 4100;
            var l = Read();
            Check(Int(l, "bucket") == 1 && Int(l, "bucketCount") == 1, "Long list entered at 4001: bucket 1 of 2000: " + l);
            ProfilerSeam.TlFin(default(JawaBenchHookGuard.Scope));
        }

        // The main thread moving on mid-read is flagged: the bucket may belong to another tick or list.
        static void ProbeChangedDuringRead()
        {
            Fresh(300);
            var normal = new TickList(TickerType.Normal);
            var other = new TickList(TickerType.Rare);
            var mover = new MovingThing { Next = other, NextTick = 301 };
            mover.def = new ThingDef { defName = "Mover" };
            normal.thingLists[0].Add(mover);
            ProfilerSeam.TlPre(normal);
            var r = Read();
            Check(r.TryGetProperty("changedDuringRead", out var c) && c.ValueKind == JsonValueKind.True,
                  "a main thread that entered another list mid-read must read changedDuringRead true: " + r);
            Check(Str(r, "tickList") == "Normal" && Int(r, "enteredTick") == 300, "the row still names what was read: " + r);
            // the SAME list re-entered on the next tick mid-read: the bucket read may be the wrong tick's
            var self = new MovingThing { Next = normal, NextTick = 302 };
            self.def = new ThingDef { defName = "SelfMover" };
            normal.thingLists[0].Clear();
            normal.thingLists[0].Add(self);
            Current.Game.tickManager.TicksGame = 301;
            ProfilerSeam.TlPre(normal);
            var same = Read();
            Check(same.TryGetProperty("changedDuringRead", out var c3) && c3.ValueKind == JsonValueKind.True,
                  "the same list re-entered on a new tick mid-read must read changedDuringRead true: " + same);
            self.Next = null;
            ProfilerSeam.TlPre(other);
            var again = Read();
            Check(again.TryGetProperty("changedDuringRead", out var c2) && c2.ValueKind == JsonValueKind.False,
                  "a still read reads changedDuringRead false: " + again);
            Check(Str(again, "tickList") == "Rare" && Int(again, "enteredTick") == 302, "now inside the Rare list at 302: " + again);
            ProfilerSeam.TlFin(default(JawaBenchHookGuard.Scope));
        }

        // `capture` says whether the tick list can be known at all.
        static void ProbeCaptureState()
        {
            Fresh(10);
            JawaBenchTpsProfiler.Installed = false;
            string off = Str(Read(), "capture") ?? "";
            Check(off.StartsWith("OFF"), "attribution not installed: capture must say OFF: " + off);
            JawaBenchTpsProfiler.Installed = true;
            string on = Str(Read(), "capture") ?? "";
            Check(!on.StartsWith("OFF") && on.Length > 0, "attribution installed: capture must not say OFF: " + on);
        }

        // A torn read is data, never a throw.
        static void ProbeTornReadsAreData()
        {
            Fresh(50);
            var normal = new TickList(TickerType.Normal);
            normal.thingLists[0].Add(new Pawn { def = new ThingDef { defName = "Human" }, ThingID = "PawnTorn", JobsThrow = true });
            ProfilerSeam.TlPre(normal);
            JsonElement r = default;
            try { r = Read(); } catch (Exception e) { Check(false, "the probe threw: " + e.GetType().Name); return; }
            var pawns = r.TryGetProperty("pawns", out var pa) ? pa.EnumerateArray().ToList() : new List<JsonElement>();
            Check(pawns.Count == 1 && Str(pawns[0], "id") == "PawnTorn" && IsNull(pawns[0], "job"),
                  "a pawn whose job tracker throws is listed with job null: " + r);
            normal.thingLists = null;
            var r2 = Read();
            Check(IsNull(r2, "bucketCount") || (r2.TryGetProperty("errors", out var er) && er.GetArrayLength() > 0),
                  "a list with no buckets reads bucketCount null or an error, never a throw: " + r2);
            ProfilerSeam.TlFin(default(JawaBenchHookGuard.Scope));
        }

        static int Main()
        {
            var units = new (string, Action)[]
            {
                ("ProbeInstall", ProbeInstall), ("ProbeOutsideTickList", ProbeOutsideTickList),
                ("ProbeBucketByEnteredTick", ProbeBucketByEnteredTick), ("ProbeChangedDuringRead", ProbeChangedDuringRead),
                ("ProbeCaptureState", ProbeCaptureState), ("ProbeTornReadsAreData", ProbeTornReadsAreData),
            };
            JawaBenchStallProbe.Install();
            foreach (var (name, fn) in units)
            {
                Fails.Clear();
                try { fn(); } catch (Exception e) { Fails.Add("threw " + e.GetType().Name + ": " + e.Message); }
                Console.WriteLine("U " + name + " " + (Fails.Count == 0 ? "ok" : "FAIL " + string.Join(" | ", Fails).Replace("\n", " ")));
            }
            Console.WriteLine("U-count " + units.Length);
            return 0;
        }
    }
}
