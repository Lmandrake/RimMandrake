// JawaBenchGatesCore.cs - the scene gates of BRIDGE v2.0: the PURE half (no Verse, no Unity, no Harmony). Item
// RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE. Page: design/specs/2026-11-23-bridge-v2/boundary.md §SCENE GATES.
// The Verse half is JawaBenchGates.cs (and the incident gate's call in JawaBenchAwareness.IncPre); hooks: bridgetools/HOOKS.md.
//
// Compiled into bridgetools/GatesSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
//
// What it does:
//   Gate      - one gate (incident, quest or mental): off, or armed for one game with an allow list. While armed, every attempt
//               that reaches it is counted; an attempt whose name is on the allow list goes through and uses up that entry (a
//               name listed once goes through once); every other attempt is held, counted, and recorded with its caller and
//               tick. An off gate decides nothing, counts nothing and records nothing. A gate armed for another game, or one
//               whose game is now under a canonical save (CAMPAIGN), lets the attempt through and releases itself, with the
//               reason kept.
//   Decide    - the prefix half, in the order of the hook rules: an off gate first (nothing touched), then the thread (a call
//               from another thread runs, counted), then an original that another prefix already skipped (not ours: nothing
//               held, counted), then the decision, contained (a fault of ours lets the game run, counted).
//   QueueHold - the incident queue held aside and given back. At the hold every entry is copied aside with its absolute ticks
//               (the fire tick and the end of its retry window). At the give-back both are moved by the ticks held, so the entry
//               keeps its distance to its fire tick and the length of its retry window. An entry already past its retry window
//               when held (the engine drops it on its next tick) is reported at the hold and at the give-back, never dropped in
//               silence. A give-back into another game returns nothing and names every entry it could not return.
//   CAMPAIGN  - arming any gate, and a queue hold, is refused while a canonical world save is loaded.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchGatesCore
    {
        static string S(object o) { return JawaBenchCondCore.Canon(o); }

        internal const string Incident = "incident", Quest = "quest", Mental = "mental";
        internal static readonly string[] Kinds = { Incident, Quest, Mental };

        /// <summary>One attempt that a gate held or let through, as the log keeps it.</summary>
        internal sealed class Attempt
        {
            public long Seq, Tick;
            public string Name, Caller, Detail, Outcome;     // Outcome: "held" | "allowed"
        }

        internal sealed class Gate
        {
            internal const int MaxRows = 200;                // bounded log: a gate left armed on a busy map must not grow without end
            public readonly string Kind;
            readonly object _lock = new object();
            volatile bool _on;
            object _game;
            readonly Dictionary<string, int> _allow = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            readonly LinkedList<Attempt> _rows = new LinkedList<Attempt>();
            long _seq;
            public long Attempts, Held, Allowed, ForeignPassed, AlreadySkipped, Faults, RowsDropped, Outside, SinkDropped;
            public string LastRelease, LastFault;
            /// <summary>The live run, or nothing (a held attempt is also a `gate` row of the run's trace).</summary>
            public Func<ICastSink> Sink;

            public Gate(string kind) { Kind = kind; }

            public bool On { get { return _on; } }

            /// <summary>Arm for this game. campaign: a canonical world save is loaded. allow: names, comma separated; a name listed
            /// N times goes through N times. null when armed, else the refusal (nothing changed).</summary>
            public string Arm(object game, bool campaign, string allow)
            {
                if (campaign) return "REFUSED: the " + Kind + " gate does not arm while a canonical world save is loaded (CAMPAIGN)";
                if (game == null) return "REFUSED: the " + Kind + " gate needs a game";
                lock (_lock)
                {
                    _allow.Clear();
                    foreach (var raw in (allow ?? "").Split(','))
                    {
                        var n = raw.Trim();
                        if (n.Length == 0) continue;
                        int c; _allow.TryGetValue(n, out c); _allow[n] = c + 1;
                    }
                    _game = game;
                    _on = true;
                }
                return null;
            }

            public void Release(string why)
            {
                lock (_lock) { if (_on) LastRelease = why; _on = false; _game = null; _allow.Clear(); }
            }

            /// <summary>One more pass for this name (a scene's exception, JawaBenchCalmProfileCore.Session.Except).</summary>
            public void AllowOne(string name)
            {
                lock (_lock) { int c; _allow.TryGetValue(name, out c); _allow[name] = c + 1; }
            }

            /// <summary>Take back one pass for this name if it is still unused. Returns 1 when one was taken back (the pass was not
            /// used), else 0.</summary>
            public int TakeBack(string name)
            {
                lock (_lock)
                {
                    int c;
                    if (!_allow.TryGetValue(name, out c) || c <= 0) return 0;
                    _allow[name] = c - 1;
                    return 1;
                }
            }

            /// <summary>The allow entries not used yet, "name xN".</summary>
            public string AllowLeft()
            {
                lock (_lock)
                {
                    var l = new List<string>();
                    foreach (var kv in _allow) if (kv.Value > 0) l.Add(kv.Key + (kv.Value > 1 ? " x" + kv.Value : ""));
                    l.Sort(string.CompareOrdinal);
                    return string.Join(",", l.ToArray());
                }
            }

            /// <summary>The prefix half. true: the original runs; false: the attempt is held (the hook skips the original and
            /// returns the method's refusal). The order is the contract: off, thread, an original already skipped, the decision.
            /// caller is read only when the gate decides (it walks the stack).</summary>
            public bool Decide(bool onMain, bool runOriginal, object game, bool campaign, string name, Func<string> caller, Func<string> detail, long tick)
            {
                if (!_on) return true;                                         // off: nothing counted, nothing recorded
                if (!onMain) { System.Threading.Interlocked.Increment(ref ForeignPassed); return true; }
                if (!runOriginal) { AlreadySkipped++; return true; }           // another prefix skipped it: not ours to hold
                try
                {
                    if (campaign) { Release("a canonical world save is loaded (CAMPAIGN)"); return true; }
                    if (!ReferenceEquals(game, _game)) { Release("the game changed (a load or a new game)"); return true; }
                    bool allowed;
                    lock (_lock)
                    {
                        int left;
                        allowed = name != null && _allow.TryGetValue(name, out left) && left > 0;
                        if (allowed) _allow[name] = _allow[name] - 1;
                    }
                    Attempts++;
                    if (allowed) Allowed++; else Held++;
                    var a = new Attempt { Tick = tick, Name = name, Outcome = allowed ? "allowed" : "held" };
                    try { a.Caller = caller == null ? null : caller(); } catch (Exception e) { a.Caller = "unknown: " + e.GetType().Name; }
                    try { a.Detail = detail == null ? null : detail(); } catch { }
                    try { Log(a); }
                    catch (Exception e) { Faults++; try { LastFault = "log: " + e.GetType().Name + ": " + e.Message; } catch { } }   // the decision stands
                    return allowed;
                }
                catch (Exception e)
                {
                    Faults++;
                    try { LastFault = e.GetType().Name + ": " + e.Message; } catch { }
                    return true;                                               // a fault of ours never holds the game
                }
            }

            void Log(Attempt a)
            {
                lock (_lock)
                {
                    a.Seq = ++_seq;
                    _rows.AddLast(a);
                    if (_rows.Count > MaxRows) { _rows.RemoveFirst(); RowsDropped++; }
                }
                var sink = Sink == null ? null : Sink();
                long seq = sink == null ? -2 : sink.EmitTap("gate", Fields(a));
                if (seq == -2) Outside++;
                else if (seq < 0) SinkDropped++;
            }

            public string Fields(Attempt a)
            {
                return "\"gate\":" + S(Kind) + ",\"outcome\":" + S(a.Outcome) + ",\"name\":" + S(a.Name) + ",\"caller\":" + S(a.Caller) +
                       ",\"detail\":" + S(a.Detail) + ",\"gseq\":" + a.Seq + ",\"gtick\":" + a.Tick;
            }

            public List<Attempt> Rows() { lock (_lock) return new List<Attempt>(_rows); }

            public string Summary()
            {
                string I(long v) { return v.ToString(CultureInfo.InvariantCulture); }
                return "{\"gate\":" + S(Kind) + ",\"on\":" + (_on ? "true" : "false") + ",\"allowLeft\":" + S(AllowLeft()) + ",\"attempts\":" + I(Attempts) +
                       ",\"held\":" + I(Held) + ",\"allowed\":" + I(Allowed) + ",\"foreignPassed\":" + I(ForeignPassed) + ",\"alreadySkipped\":" + I(AlreadySkipped) +
                       ",\"faults\":" + I(Faults) + ",\"lastFault\":" + S(LastFault) + ",\"rowsDropped\":" + I(RowsDropped) + ",\"outside\":" + I(Outside) +
                       ",\"sinkDropped\":" + I(SinkDropped) + ",\"lastRelease\":" + S(LastRelease) + "}";
            }
        }

        /// <summary>The three gates. Arm refuses every one of them under CAMPAIGN.</summary>
        internal sealed class Gates
        {
            public readonly Gate GIncident = new Gate(Incident), GQuest = new Gate(Quest), GMental = new Gate(Mental);
            public readonly QueueHold Queue = new QueueHold();
            public Gate[] All { get { return new[] { GIncident, GQuest, GMental }; } }

            public Gate Of(string kind)
            {
                foreach (var g in All) if (string.Equals(g.Kind, kind, StringComparison.OrdinalIgnoreCase)) return g;
                return null;
            }

            public string Summary()
            {
                var sb = new StringBuilder("{\"gates\":[");
                var a = All;
                for (int i = 0; i < a.Length; i++) { if (i > 0) sb.Append(','); sb.Append(a[i].Summary()); }
                return sb.Append("],\"queue\":").Append(Queue.Summary()).Append('}').ToString();
            }
        }

        // ============================================================================================ the incident queue
        /// <summary>One queued incident, with its ticks absolute: RetryEnd = fire tick + retry duration (IncidentQueueTick drops a
        /// tried entry at RetryEnd). Ref is the engine's object; the core never reads it.</summary>
        internal struct QEntry
        {
            public string Def;
            public long FireTick, RetryEnd;
            public bool Tried;
            public object Ref;
            public long RetryDuration { get { return RetryEnd - FireTick; } }
            public string Text() { return (Def ?? "?") + " fire " + FireTick + " retry to " + RetryEnd + (Tried ? " (tried)" : ""); }
        }

        internal sealed class QueueHold
        {
            List<QEntry> _aside;
            object _game;
            long _at;
            public long Held, Returned, Expired, Lost;
            public string Last;

            public bool Holding { get { return _aside != null; } }
            public int Count { get { return _aside == null ? 0 : _aside.Count; } }

            /// <summary>An entry the engine drops on its next tick: tried once, and its retry window has ended.</summary>
            public static bool PastWindow(QEntry e, long now) { return e.Tried && e.RetryEnd <= now; }

            /// <summary>Take the entries aside (the Verse half then empties the queue). null when held, else the refusal (the queue
            /// is not touched). report: one line per entry past its retry window, which the give-back will not return.</summary>
            public string Hold(object game, bool campaign, long now, IList<QEntry> entries, List<string> report)
            {
                if (campaign) return "REFUSED: the incident queue is not held while a canonical world save is loaded (CAMPAIGN)";
                if (_aside != null) return "REFUSED: the queue is held already (" + _aside.Count + " entries aside since tick " + _at + ")";
                if (game == null) return "REFUSED: no game";
                _aside = new List<QEntry>(entries ?? new QEntry[0]);
                _game = game;
                _at = now;
                Held += _aside.Count;
                foreach (var e in _aside)
                    if (PastWindow(e, now) && report != null)
                        report.Add("past its retry window when held: " + e.Text() + " (the engine drops it on its next tick; it is not given back)");
                Last = "held " + _aside.Count + " at tick " + now;
                return null;
            }

            /// <summary>The entries to put back, each with its fire tick AND the end of its retry window moved by the ticks held.
            /// report: what is not returned, each named. null game or another game: nothing is returned.</summary>
            public List<QEntry> GiveBack(object game, long now, List<string> report)
            {
                var back = new List<QEntry>();
                if (_aside == null) { if (report != null) report.Add("nothing is held"); return back; }
                long held = Math.Max(0, now - _at);
                bool same = game != null && ReferenceEquals(game, _game);
                foreach (var e in _aside)
                {
                    if (!same)
                    {
                        Lost++;
                        if (report != null) report.Add("not given back, the game changed while it was held: " + e.Text());
                        continue;
                    }
                    if (PastWindow(e, _at))
                    {
                        Expired++;
                        if (report != null) report.Add("not given back, past its retry window when held: " + e.Text());
                        continue;
                    }
                    var m = e;
                    m.FireTick = e.FireTick + held;
                    m.RetryEnd = e.RetryEnd + held;
                    back.Add(m);
                    Returned++;
                }
                Last = "given back " + back.Count + " of " + _aside.Count + " after " + held + " ticks held";
                _aside = null;
                _game = null;
                return back;
            }

            public string Summary()
            {
                return "{\"holding\":" + (Holding ? "true" : "false") + ",\"aside\":" + Count + ",\"since\":" + (Holding ? _at.ToString(CultureInfo.InvariantCulture) : "null") +
                       ",\"held\":" + Held + ",\"returned\":" + Returned + ",\"expired\":" + Expired + ",\"lost\":" + Lost + ",\"last\":" + S(Last) + "}";
            }
        }
    }
}
