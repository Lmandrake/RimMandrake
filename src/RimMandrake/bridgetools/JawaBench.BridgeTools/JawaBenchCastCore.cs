// JawaBenchCastCore.cs - the standard cast tracks of a scene run and the job and reservation taps: the PURE half (no Verse, no
// Unity, no Harmony). Item RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY. Page: design/specs/2026-11-23-bridge-v2/boundary.md
// §CAST TRACKS AND JOB TAPS. The Verse half is JawaBenchCast.cs; its hooks are on bridgetools/HOOKS.md.
//
// Compiled into bridgetools/CastTracksSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
//
// What it does:
//   Cast   - one member per cast alias (a pawn of the session's bindings). At each sample of the run it reads the twelve standard
//            fields of the thing the alias is on now and writes a `track` row named `<alias>.<field>` on change only. When the
//            alias's object is replaced (a dead pawn's corpse), it writes a `link` row first and moves on; it never moves silently.
//            When the job changes, the toil track re-binds to the new job (a `rebind` row, then the toil row, even when the index
//            is the same). After the last sample, Reconcile compares the death a track saw with the kill records of the run: a
//            death with no kill record is a `reconcile` row, verdict COULD NOT LOOK. Its cost per tick is in the close record.
//   Taps   - the recorder of three Harmony taps (job start, job end, reservation made or refused) and of the kill tap's cast feed.
//            Each hook pair goes through a JawaBenchHookGuard (Admit/Commit): the six rules of HOOKS.md. Each admitted call takes
//            an entry ordinal `ord` at its prefix, so a job started inside another job's start keeps its call order beside the
//            trace's own `n`. A record outside any running run is dropped and counted; a record about a pawn outside the cast
//            is not written and is counted.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    /// <summary>What the cast needs of the game. Ids are thingIDNumber.</summary>
    internal interface ICastSource
    {
        /// <summary>The thing that now carries this thing's alias, when the thing was replaced (a dead pawn: its corpse), else -1.</summary>
        int Successor(int thing, out string why);
        /// <summary>Fill the twelve fields of Cast.Fields for this thing. Null when read, else why not ("gone": no such thing).</summary>
        string Read(int thing, object[] into);
    }

    /// <summary>Where a tap writes: the live run, or nothing.</summary>
    internal interface ICastSink
    {
        /// <summary>-2: no run is running (outside any run); -1: the writer dropped it; else the sequence number.</summary>
        long EmitTap(string rec, string fields);
    }

    internal static class JawaBenchCastCore
    {
        static string S(object o) { return JawaBenchCondCore.Canon(o); }

        // ============================================================================================ the cast tracks
        internal sealed class Member
        {
            public string Alias;
            public int Bound;                       // the thing the alias was bound to
            public int Thing;                       // the thing the alias is on now
            public readonly List<int> Chain = new List<int>();  // every thing the alias was on, in order
            public object[] Last, Now;
            public string LastSt;
            public bool Has, DeadAtFirst, DeadSeen;
            public long DeadTick = -1;
        }

        /// <summary>The standard cast tracks (06_build_order.md): their order is the order of the rows of one sample.</summary>
        internal static readonly string[] Fields =
            { "pos", "facing", "job", "toil", "health", "downed", "dead", "mental", "carried", "holder", "faction", "drafted" };
        internal const int Job = 2, Toil = 3, Dead = 6;

        internal sealed class Cast : ISceneCast
        {
            readonly ICastSource _src;
            readonly Func<double> _now;
            readonly Taps _taps;
            readonly List<Member> _m = new List<Member>();
            readonly List<object> _reconciled = new List<object>();
            public long Samples, Reads, Rows, Links, Rebinds;
            public double Ms, MsMax;
            readonly string[] _names;

            public IList<Member> Members { get { return _m; } }

            /// <summary>members: alias -> thingIDNumber. taps: the recorder whose kill records the reconciliation reads (null: none).</summary>
            public Cast(IEnumerable<KeyValuePair<string, int>> members, ICastSource src, Func<double> nowMs, Taps taps)
            {
                _src = src; _now = nowMs; _taps = taps;
                foreach (var kv in members)
                {
                    var m = new Member { Alias = kv.Key, Bound = kv.Value, Thing = kv.Value, Last = new object[Fields.Length], Now = new object[Fields.Length] };
                    m.Chain.Add(kv.Value);
                    _m.Add(m);
                }
                _names = new string[_m.Count * Fields.Length];
                for (int i = 0; i < _m.Count; i++)
                    for (int f = 0; f < Fields.Length; f++) _names[i * Fields.Length + f] = _m[i].Alias + "." + Fields[f];
            }

            /// <summary>Every thing id that carries a cast alias now or did in this run: the taps record these and no others.</summary>
            public bool IsCast(int thing)
            {
                for (int i = 0; i < _m.Count; i++) if (_m[i].Chain.Contains(thing)) return true;
                return false;
            }

            /// <summary>The alias of a thing of the cast, or null.</summary>
            public string AliasOf(int thing)
            {
                for (int i = 0; i < _m.Count; i++) if (_m[i].Chain.Contains(thing)) return _m[i].Alias;
                return null;
            }

            public void Sample(SceneRow row, long tick, string phase, bool all)
            {
                double t0 = _now();
                Samples++;
                for (int i = 0; i < _m.Count; i++) SampleOne(row, tick, phase, all, i);
                double ms = _now() - t0;
                Ms += ms;
                if (ms > MsMax) MsMax = ms;
            }

            void SampleOne(SceneRow row, long tick, string phase, bool all, int i)
            {
                var m = _m[i];
                string why;
                int next = _src.Successor(m.Thing, out why);
                if (next >= 0 && next != m.Thing)
                {
                    row(tick, phase, "link", "\"alias\":" + S(m.Alias) + ",\"from\":" + m.Thing + ",\"to\":" + next + ",\"why\":" + S(why ?? ""));
                    Rows++; Links++;
                    m.Thing = next;
                    if (!m.Chain.Contains(next)) m.Chain.Add(next);
                }
                for (int f = 0; f < Fields.Length; f++) m.Now[f] = null;
                string st = _src.Read(m.Thing, m.Now) ?? "ok";
                Reads++;
                bool dead = st == "ok" && m.Now[Dead] is bool && (bool)m.Now[Dead];
                if (phase == "first") m.DeadAtFirst = dead;
                if (dead && !m.DeadSeen) { m.DeadSeen = true; m.DeadTick = tick; }
                bool jobMoved = m.Has && st == "ok" && m.LastSt == "ok" && !JawaBenchCondCore.SameValue(m.Now[Job], m.Last[Job]);
                for (int f = 0; f < Fields.Length; f++)
                {
                    bool force = all || !m.Has || st != m.LastSt;
                    if (f == Toil && jobMoved)
                    {
                        // the toil index belongs to its job: a new job is a new track, also when the index is the same
                        row(tick, phase, "rebind", "\"name\":" + S(_names[i * Fields.Length + f]) + ",\"from\":" + S(m.Last[Job]) + ",\"to\":" + S(m.Now[Job]));
                        Rows++; Rebinds++;
                        force = true;
                    }
                    if (!force && JawaBenchCondCore.SameValue(m.Now[f], m.Last[f])) continue;
                    var v = st == "ok" ? m.Now[f] : null;
                    row(tick, phase, "track", "\"name\":" + S(_names[i * Fields.Length + f]) + ",\"st\":" + S(st) + ",\"v\":" + S(v) +
                                              (st == "ok" ? "" : ",\"detail\":" + S(st)));
                    Rows++;
                }
                var swap = m.Last; m.Last = m.Now; m.Now = swap;
                m.LastSt = st; m.Has = true;
            }

            /// <summary>After the last sample: the trace against the state. A member that died in the run with no kill record of its
            /// own is a `reconcile` row, verdict COULD NOT LOOK.</summary>
            public void Reconcile(SceneRow row, long tick)
            {
                foreach (var m in _m)
                {
                    if (!m.DeadSeen || m.DeadAtFirst) continue;
                    bool killed = false;
                    if (_taps != null) foreach (var id in m.Chain) if (_taps.Killed(id)) { killed = true; break; }
                    if (killed) continue;
                    var d = new Dictionary<string, object> { { "alias", m.Alias }, { "what", "dead with no kill record" }, { "deadAt", (double)m.DeadTick }, { "verdict", "COULD NOT LOOK" } };
                    _reconciled.Add(d);
                    row(tick, "last", "reconcile", "\"alias\":" + S(m.Alias) + ",\"what\":\"dead with no kill record\",\"deadAt\":" + m.DeadTick + ",\"verdict\":\"COULD NOT LOOK\"");
                    Rows++;
                }
            }

            public IList<object> Reconciled { get { return _reconciled; } }

            static string R(double v) { return Math.Round(v, 4).ToString(CultureInfo.InvariantCulture); }

            public string Summary()
            {
                double per = Samples > 0 ? Ms / Samples : 0;
                return "{\"members\":" + _m.Count + ",\"tracks\":" + (_m.Count * Fields.Length) + ",\"samples\":" + Samples + ",\"reads\":" + Reads +
                       ",\"rows\":" + Rows + ",\"links\":" + Links + ",\"rebinds\":" + Rebinds + ",\"ms\":" + R(Ms) + ",\"msMax\":" + R(MsMax) +
                       ",\"msPerTick\":" + R(per) + ",\"reconcile\":" + S(_reconciled) + ",\"taps\":" + (_taps == null ? "null" : _taps.Summary()) + "}";
            }
        }

        // ============================================================================================ the taps
        /// <summary>A job as a tap sees it: its loadID, its def, and its toil index.</summary>
        internal struct JobSnap
        {
            public bool Has;
            public int Id;
            public string Def;
            public int Toil;
            public string Text() { return Has ? (Def ?? "?") + "#" + Id.ToString(CultureInfo.InvariantCulture) : null; }
        }

        /// <summary>The per-call state a prefix hands its own postfix (Harmony __state): never a static.</summary>
        internal struct TapState
        {
            public JawaBenchHookGuard.Scope S;
            public long Ord;
            public JobSnap Prev;
            public bool Suspend;
            // The started job as the prefix saw it. A job that ends inside its own StartJob (a pather error on the first
            // toil) is back in JobMaker's pool by the postfix, its def null and loadID -1 (measured live on ArchBig
            // 2026-11-25: an ordered Goto recorded as "?#-1"). So the postfix records these, not the pooled job.
            public JobSnap New;
            public string NewGiver;
        }

        internal sealed class Taps
        {
            public readonly JawaBenchHookGuard GStart = new JawaBenchHookGuard("cast.job_start", allowNesting: true);
            public readonly JawaBenchHookGuard GEnd = new JawaBenchHookGuard("cast.job_end", allowNesting: true);
            public readonly JawaBenchHookGuard GReserve = new JawaBenchHookGuard("cast.reserve", allowNesting: true);
            /// <summary>The live run, or null. Read at each record.</summary>
            public Func<ICastSink> Sink;
            /// <summary>The cast of the live run, or null.</summary>
            public Func<Cast> CastNow;
            long _ord;
            public long Records, Outside, NotCast, Dropped;
            readonly HashSet<int> _killed = new HashSet<int>();

            public JawaBenchHookGuard[] Guards { get { return new[] { GStart, GEnd, GReserve }; } }

            /// <summary>The prefix half, as the Verse prefix does it: thread and admission first (Admit), and only then the entry
            /// ordinal and what the prefix saw. Nothing is touched before the thread check.</summary>
            public bool Enter(JawaBenchHookGuard g, bool onMain, out TapState st, JobSnap prev = default(JobSnap), bool suspend = false)
            {
                st = default(TapState);
                if (!g.Admit(onMain, out st.S)) return false;
                Opened(ref st, prev, suspend);
                return true;
            }

            /// <summary>After Admit: the entry ordinal (the call order, also when calls nest) and the job the call found.</summary>
            public void Opened(ref TapState st, JobSnap prev, bool suspend) { st.Ord = ++_ord; st.Prev = prev; st.Suspend = suspend; }

            public void Threw(JawaBenchHookGuard g, Exception e) { try { if (e != null) g.NoteThrew(); } catch { } }

            // The postfix halves. The Verse postfix calls Commit itself (so the hook audit sees __runOriginal handed to it) and then
            // Record*; JobStart, JobEnd and Reserve are the same two steps for the harness.
            public void JobStart(TapState st, bool ranOriginal, int pawn, JobSnap job, string giver, string prevEnd, bool current)
            {
                if (!GStart.Commit(st.S, ranOriginal)) return;
                try { RecordStart(st, pawn, job, giver, prevEnd, current); } catch (Exception e) { GStart.Note("job_start", e); }
            }

            public void JobEnd(TapState st, bool ranOriginal, int pawn, string condition)
            {
                if (!GEnd.Commit(st.S, ranOriginal)) return;
                try { RecordEnd(st, pawn, condition); } catch (Exception e) { GEnd.Note("job_end", e); }
            }

            public void Reserve(TapState st, bool ranOriginal, int claimant, JobSnap job, string target, bool made, string holder)
            {
                if (!GReserve.Commit(st.S, ranOriginal)) return;
                try { RecordReserve(st, claimant, job, target, made, holder); } catch (Exception e) { GReserve.Note("reserve", e); }
            }

            /// <summary>A job started. The record names the job it replaced (the prefix's) and that job's end condition, who gave the
            /// new job, and whether the new job is the pawn's job after the call (false: queued, or ended at once).</summary>
            public void RecordStart(TapState st, int pawn, JobSnap job, string giver, string prevEnd, bool current)
            {
                Record(st, pawn, "job_start", "\"job\":" + S(job.Text()) + ",\"def\":" + S(job.Def) + ",\"giver\":" + S(giver) +
                                             ",\"current\":" + (current ? "true" : "false") + ",\"prev\":" + S(st.Prev.Text()) +
                                             ",\"prevEnd\":" + S(st.Prev.Has ? (st.Suspend ? "Suspended" : prevEnd) : null));
            }

            /// <summary>A job ended (Pawn_JobTracker.CleanupCurrentJob, where every end goes): the prefix's job, its toil, the condition.</summary>
            public void RecordEnd(TapState st, int pawn, string condition)
            {
                if (!st.Prev.Has) return;       // the original had no job to end
                Record(st, pawn, "job_end", "\"job\":" + S(st.Prev.Text()) + ",\"def\":" + S(st.Prev.Def) + ",\"toil\":" + st.Prev.Toil + ",\"cond\":" + S(condition));
            }

            /// <summary>A reservation asked: made or refused, with the pawn that holds it when refused.</summary>
            public void RecordReserve(TapState st, int claimant, JobSnap job, string target, bool made, string holder)
            {
                Record(st, claimant, "reserve", "\"job\":" + S(job.Text()) + ",\"target\":" + S(target) + ",\"made\":" + (made ? "true" : "false") +
                                                ",\"holder\":" + S(made ? null : holder));
            }

            /// <summary>True when a record about this pawn would be written now: a running run whose cast holds it.</summary>
            public bool Wanted(int pawn) { var c = CastNow == null ? null : CastNow(); return c != null && c.IsCast(pawn); }

            /// <summary>The kill tap's feed (JawaBenchSituationalTools.KillPostfix, already admitted there): a kill record of the run.</summary>
            public void Kill(int pawn, string culprit)
            {
                var c = CastNow == null ? null : CastNow();
                if (c == null) { Outside++; return; }
                if (!c.IsCast(pawn)) { NotCast++; return; }
                var sink = Sink == null ? null : Sink();
                long seq = sink == null ? -2 : sink.EmitTap("kill", "\"alias\":" + S(c.AliasOf(pawn)) + ",\"thing\":" + pawn + ",\"ord\":" + (++_ord) + ",\"culprit\":" + S(culprit));
                Count(seq);
                if (seq >= 0) _killed.Add(pawn);       // a kill the writer dropped is not in the trace: the reconciliation says so
            }

            public bool Killed(int pawn) { return _killed.Contains(pawn); }

            void Record(TapState st, int pawn, string rec, string fields)
            {
                var c = CastNow == null ? null : CastNow();
                if (c == null) { Outside++; return; }
                if (!c.IsCast(pawn)) { NotCast++; return; }
                var sink = Sink == null ? null : Sink();
                long seq = sink == null ? -2 : sink.EmitTap(rec, "\"alias\":" + S(c.AliasOf(pawn)) + ",\"thing\":" + pawn + ",\"ord\":" + st.Ord + "," + fields);
                Count(seq);
            }

            void Count(long seq)
            {
                if (seq == -2) Outside++;
                else if (seq < 0) Dropped++;
                else Records++;
            }

            /// <summary>A new run starts: the kill records of the last run are not this run's.</summary>
            public void NewRun() { _killed.Clear(); foreach (var g in Guards) g.Mark(); }

            public string Summary()
            {
                var sb = new StringBuilder("{\"records\":").Append(Records).Append(",\"outside\":").Append(Outside).Append(",\"notCast\":").Append(NotCast)
                    .Append(",\"dropped\":").Append(Dropped).Append(",\"hooks\":[");
                var gs = Guards;
                for (int i = 0; i < gs.Length; i++) { if (i > 0) sb.Append(','); sb.Append('{').Append(gs[i].CoverageFields()).Append('}'); }
                return sb.Append("]}").ToString();
            }
        }

        /// <summary>A monotonic clock for the cost of the tracks.</summary>
        internal static double ClockMs() { return Stopwatch.GetTimestamp() * 1000.0 / Stopwatch.Frequency; }
    }
}
