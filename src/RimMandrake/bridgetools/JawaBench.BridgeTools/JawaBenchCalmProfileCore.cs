// JawaBenchCalmProfileCore.cs - the PURE half of the calm profile of BRIDGE v2.0 (no Verse, no Unity, no Harmony): named, versioned
// profiles; a control's status against its certificate line; the record of entries (PUT BACK, GIVEN BACK, NOT UNDONE) and the
// put-back in reverse order with read-back; the lease; the scene's exceptions on the gates; the breach log with its classes; one
// driver. Item RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE. Page: design/specs/2026-11-23-bridge-v2/boundary.md §CALM PROFILE.
// The Verse half is JawaBenchCalmProfile.cs. Compiled into bridgetools/CalmProfileSelfTest with JawaBenchGatesCore.cs and
// JawaBenchCastCore.cs: a `using Verse;` here breaks that build.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCalmProfileCore
    {
        // ------------------------------------------------------------------ words
        internal const string Held = "HELD", Unproven = "ARMED UNPROVEN", CouldNotArm = "COULD NOT ARM", Refused = "REFUSED",
                              Excepted = "EXCEPTED", Off = "OFF";
        internal const string PutBack = "PUT BACK", GivenBack = "GIVEN BACK", NotUndone = "NOT UNDONE";
        internal const string Attempts = "attempts", Scheduling = "scheduling", NoCount = "none";
        internal const string Environment = "ENVIRONMENT", Apparatus = "APPARATUS";

        internal const string Storyteller = "storyteller", MentalSwitch = "random_mental_states", Diseases = "random_diseases",
                              IncidentGate = "incident_gate", QuestGate = "quest_gate", MentalGate = "mental_gate", Queue = "incident_queue",
                              Wild = "wild_spawner", Weather = "weather", Letters = "proximity_letters", NeedsHold = "needs_hold",
                              ClearSite = "clear_site";

        internal sealed class ControlDef
        {
            internal string Name, Class, Counts, CertLine, Reach;
            internal bool Destructive;
            internal ControlDef(string name, string cls, string counts, string certLine = null, bool destructive = false, string reach = null)
            { Name = name; Class = cls; Counts = counts; CertLine = certLine; Destructive = destructive; Reach = reach; }
        }

        /// <summary>The named, versioned profiles. A new control or a changed class is a new version.</summary>
        internal static readonly Dictionary<string, Dictionary<int, ControlDef[]>> Catalog = new Dictionary<string, Dictionary<int, ControlDef[]>>(StringComparer.Ordinal)
        {
            ["standard"] = new Dictionary<int, ControlDef[]>
            {
                [1] = new[]
                {
                    new ControlDef(Storyteller, PutBack, Scheduling), new ControlDef(MentalSwitch, PutBack, Scheduling),
                    new ControlDef(Diseases, PutBack, Scheduling),
                    new ControlDef(IncidentGate, PutBack, Attempts, "incident.held"), new ControlDef(QuestGate, PutBack, Attempts, "gate.quest.held"),
                    new ControlDef(MentalGate, PutBack, Attempts, "gate.mental.held"),
                    new ControlDef(Queue, GivenBack, Scheduling), new ControlDef(Wild, PutBack, Attempts),
                    new ControlDef(Weather, PutBack, NoCount), new ControlDef(Letters, PutBack, NoCount),
                    new ControlDef(NeedsHold, PutBack, NoCount),
                    new ControlDef(ClearSite, NotUndone, NoCount, null, true, "save"),
                },
            },
        };

        /// <summary>Every key that a profile takes. Any other key is refused by name: a misspelt key would arm a calm the scene did
        /// not ask for.</summary>
        internal static readonly string[] Keys =
        {
            "profile", "version", "except", "allowIncidents", "allowQuests", "allowMental", "weather", "minutes", "clear", "holdNeeds",
            "keepDefs", "keepIds", "driver", "certified",
        };

        internal const double DefaultMinutes = 30, MaxMinutes = 240;

        internal sealed class Profile
        {
            internal string Name, Driver, Weather = "Clear", AllowIncidents = "", AllowQuests = "", AllowMental = "", HoldNeeds = "",
                            KeepDefs = "", KeepIds = "";
            internal int Version;
            internal ControlDef[] Controls;
            internal double Minutes = DefaultMinutes;
            internal bool Clear;
            internal HashSet<string> Except = new HashSet<string>(StringComparer.Ordinal);
            internal HashSet<string> Certified = new HashSet<string>(StringComparer.Ordinal);
            internal string Id => Name + "/" + Version;
        }

        /// <summary>Parse the keys of a profile. null with the refusal when any key, the profile, the version or an exception is unknown.</summary>
        internal static Profile Parse(IDictionary<string, string> args, out string refusal)
        {
            refusal = null;
            args = args ?? new Dictionary<string, string>();
            foreach (var k in args.Keys)
                if (!Keys.Contains(k)) { refusal = "REFUSED: unknown profile key '" + k + "'. Keys: " + string.Join(", ", Keys); return null; }
            string V(string k, string d) { string v; return args.TryGetValue(k, out v) && v != null ? v.Trim() : d; }
            var p = new Profile { Name = V("profile", "standard") };
            Dictionary<int, ControlDef[]> versions;
            if (!Catalog.TryGetValue(p.Name, out versions)) { refusal = "REFUSED: no profile '" + p.Name + "'. Profiles: " + string.Join(", ", Catalog.Keys.ToArray()); return null; }
            var vs = V("version", "");
            int ver;
            if (vs.Length == 0) ver = versions.Keys.Max();
            else if (!int.TryParse(vs, NumberStyles.Integer, CultureInfo.InvariantCulture, out ver) || !versions.ContainsKey(ver))
            { refusal = "REFUSED: profile " + p.Name + " has no version '" + vs + "'. Versions: " + string.Join(", ", versions.Keys.Select(x => x.ToString(CultureInfo.InvariantCulture)).ToArray()); return null; }
            p.Version = ver;
            p.Controls = versions[ver];
            foreach (var raw in V("except", "").Split(','))
            {
                var n = raw.Trim();
                if (n.Length == 0) continue;
                if (!p.Controls.Any(c => c.Name == n)) { refusal = "REFUSED: except: '" + n + "' is no control of " + p.Id + ". Controls: " + string.Join(", ", p.Controls.Select(c => c.Name).ToArray()); return null; }
                p.Except.Add(n);
            }
            foreach (var raw in V("certified", "").Split(',')) { var n = raw.Trim(); if (n.Length > 0) p.Certified.Add(n); }
            var ms = V("minutes", "");
            if (ms.Length > 0)
            {
                double m;
                if (!double.TryParse(ms, NumberStyles.Float, CultureInfo.InvariantCulture, out m) || double.IsNaN(m) || m <= 0)
                { refusal = "REFUSED: minutes '" + ms + "' is not a number above 0"; return null; }
                p.Minutes = Math.Min(m, MaxMinutes);
            }
            var cl = V("clear", "false").ToLowerInvariant();
            if (cl != "true" && cl != "false") { refusal = "REFUSED: clear '" + cl + "' is not true or false"; return null; }
            p.Clear = cl == "true";
            p.Weather = V("weather", "Clear");
            p.AllowIncidents = V("allowIncidents", ""); p.AllowQuests = V("allowQuests", ""); p.AllowMental = V("allowMental", "");
            p.HoldNeeds = V("holdNeeds", ""); p.KeepDefs = V("keepDefs", ""); p.KeepIds = V("keepIds", "");
            p.Driver = V("driver", "");
            if (p.Driver.Length == 0) { refusal = "REFUSED: driver is needed: the profile belongs to the driver that arms it"; return null; }
            return p;
        }

        /// <summary>HELD only with the mechanism read back AND the control's certificate line among the certified lines.</summary>
        internal static string StatusOf(ControlDef c, bool readBack, ICollection<string> certified, out string why)
        {
            if (!readBack) { why = "the mechanism was not read back in place"; return CouldNotArm; }
            if (c.CertLine == null) { why = "no certificate line exists for this kind of control yet"; return Unproven; }
            if (certified != null && certified.Contains(c.CertLine)) { why = "read back, and the certificate shows " + c.CertLine; return Held; }
            why = "read back; the certificate does not show " + c.CertLine + " on this mod list";
            return Unproven;
        }

        // ------------------------------------------------------------------ the record
        internal sealed class Entry
        {
            internal long Seq;
            internal string Control, Class, Reach, Before, Detail;
            internal Func<string> Put;          // writes the before value back: null, or the error
            internal Func<string> Read;         // the value now, compared with Before after the put-back
        }

        internal sealed class Record
        {
            private readonly List<Entry> _live = new List<Entry>();
            private long _seq;
            internal readonly List<Entry> NotUndoneDone = new List<Entry>();    // NOT UNDONE entries of earlier leaves, still listed

            internal Entry Add(string control, string cls, string before, Func<string> put, Func<string> read, string reach = null, string detail = null)
            {
                var e = new Entry { Seq = ++_seq, Control = control, Class = cls, Before = before, Put = put, Read = read, Reach = reach, Detail = detail };
                _live.Add(e);
                return e;
            }

            /// <summary>A hold on needs is two entries: the hold (PUT BACK when released) and what did not happen (NOT UNDONE, the save).</summary>
            internal void AddNeedsHold(string pawns, Func<string> release, Func<string> read)
            {
                Add(NeedsHold, PutBack, "not held", release, read, null, "needs held for " + pawns);
                Add(NeedsHold, NotUndone, null, null, null, "save", "the hunger, rest and mental breaks that did not happen while the needs of " + pawns + " were held");
            }

            internal List<Entry> Live => new List<Entry>(_live);

            internal List<string> NotUndoneLines()
            {
                return _live.Concat(NotUndoneDone).Where(e => e.Class == NotUndone)
                            .Select(e => e.Control + " (NOT UNDONE, reach " + (e.Reach ?? "?") + "): " + e.Detail).ToList();
            }

            /// <summary>Put back every PUT BACK and GIVEN BACK entry, last first, each read back. lines: what was done;
            /// notPutBack: each value that threw or reads otherwise. NOT UNDONE entries stay listed, never put back.</summary>
            internal List<string> PutBackAll(string why, List<string> notPutBack)
            {
                var lines = new List<string> { "put back: " + why };
                for (int i = _live.Count - 1; i >= 0; i--)
                {
                    var e = _live[i];
                    if (e.Class == NotUndone) { NotUndoneDone.Add(e); continue; }
                    string err = null, now = null;
                    try { err = e.Put == null ? "no put-back" : e.Put(); } catch (Exception x) { err = x.GetType().Name + ": " + x.Message; }
                    try { now = e.Read == null ? null : e.Read(); } catch (Exception x) { err = err ?? ("read-back threw: " + x.GetType().Name + ": " + x.Message); }
                    if (err == null && now != e.Before) err = "reads '" + (now ?? "nothing") + "', want '" + e.Before + "'";
                    if (err != null) { notPutBack?.Add(e.Control + " (" + e.Class + "): " + err); lines.Add(e.Control + ": NOT put back: " + err); }
                    else lines.Add(e.Control + ": " + e.Class.ToLowerInvariant() + ", reads '" + now + "'");
                }
                _live.Clear();
                return lines;
            }
        }

        // ------------------------------------------------------------------ the lease (wall time, not bound to a game: it outlives a load)
        internal sealed class Lease
        {
            private double _untilS;
            private bool _on;
            internal string LastEnd;
            internal void Arm(double nowS, double minutes) { _untilS = nowS + Math.Min(minutes > 0 ? minutes : DefaultMinutes, MaxMinutes) * 60.0; _on = true; }
            internal void End(string why) { if (_on) LastEnd = why; _on = false; }
            internal bool On => _on;
            internal bool Expired(double nowS) => _on && nowS >= _untilS;
            internal double SecondsLeft(double nowS) => _on ? Math.Max(0, _untilS - nowS) : 0;
        }

        // ------------------------------------------------------------------ the breach log
        internal sealed class Breach { internal long Seq, Tick; internal string Class, Kind, What; }

        internal sealed class Breaches
        {
            internal const int MaxRows = 200;    // the danger: a mod that tries one incident each tick fills the memory; counts stay exact
            private readonly object _gate = new object();
            private readonly LinkedList<Breach> _rows = new LinkedList<Breach>();
            private readonly Dictionary<string, long> _byClass = new Dictionary<string, long>(), _byKind = new Dictionary<string, long>();
            private long _seq, _dropped;
            internal Func<ICastSink> Sink;
            internal long SinkFaults;

            internal void Add(string cls, string kind, long tick, string what)
            {
                Breach b;
                lock (_gate)
                {
                    long n; _byClass.TryGetValue(cls, out n); _byClass[cls] = n + 1;
                    _byKind.TryGetValue(kind, out n); _byKind[kind] = n + 1;
                    b = new Breach { Seq = ++_seq, Class = cls, Kind = kind, Tick = tick, What = what };
                    _rows.AddLast(b);
                    if (_rows.Count > MaxRows) { _rows.RemoveFirst(); _dropped++; }
                }
                try
                {
                    var s = Sink == null ? null : Sink();
                    if (s != null) s.EmitTap("breach", "\"class\":" + Q(cls) + ",\"kind\":" + Q(kind) + ",\"what\":" + Q(what) + ",\"bseq\":" + b.Seq + ",\"btick\":" + tick);
                }
                catch { SinkFaults++; }
            }

            internal long OfClass(string cls) { lock (_gate) { long n; _byClass.TryGetValue(cls, out n); return n; } }
            internal long OfKind(string kind) { lock (_gate) { long n; _byKind.TryGetValue(kind, out n); return n; } }
            internal long Dropped { get { lock (_gate) return _dropped; } }
            internal long LastSeq { get { lock (_gate) return _seq; } }
            internal List<Breach> Since(long seq) { lock (_gate) return _rows.Where(x => x.Seq > seq).ToList(); }
            internal void Clear() { lock (_gate) { _rows.Clear(); _byClass.Clear(); _byKind.Clear(); _dropped = 0; } }

            private static string Q(string s)
            {
                if (s == null) return "null";
                var o = new System.Text.StringBuilder("\"");
                foreach (var ch in s)
                {
                    if (ch == '"' || ch == '\\') o.Append('\\').Append(ch);
                    else if (ch < ' ') o.Append("\\u").Append(((int)ch).ToString("x4"));
                    else o.Append(ch);
                }
                return o.Append('"').ToString();
            }
        }

        // ------------------------------------------------------------------ the session: one profile, one driver, one game
        internal sealed class ControlState { internal string Status, Why; internal Func<long> Stopped; }

        /// <summary>What the applier did for one control: the mechanism read back in place, or the error.</summary>
        internal sealed class Applied
        {
            internal bool ReadBack; internal string Error, Detail; internal Func<long> Stopped;
            internal static Applied Ok(string detail = null, Func<long> stopped = null) => new Applied { ReadBack = true, Detail = detail, Stopped = stopped };
            internal static Applied Fail(string error) => new Applied { ReadBack = false, Error = error };
            internal static Applied NotOn(string why) => new Applied { ReadBack = false, Error = null, Detail = why };
        }

        internal sealed class Exception1 { internal JawaBenchGatesCore.Gate Gate; internal string Name; }

        internal sealed class Session
        {
            internal Profile P;
            internal object Game;
            internal bool Armed;
            internal readonly Lease L = new Lease();
            internal readonly Record R = new Record();
            internal readonly Breaches B = new Breaches();
            internal readonly Dictionary<string, ControlState> State = new Dictionary<string, ControlState>(StringComparer.Ordinal);
            private readonly List<Exception1> _exceptions = new List<Exception1>();
            internal List<string> LastLeave = new List<string>(), LastNotPutBack = new List<string>();
            internal int Rearms;

            /// <summary>null when this driver may write, else the refusal; a write by a second driver is a breach of class APPARATUS.</summary>
            internal string Call(string driver, string op, long tick)
            {
                if (!Armed || P == null || string.Equals(driver ?? "", P.Driver, StringComparison.Ordinal)) return null;
                B.Add(Apparatus, "second_driver", tick, "driver '" + (driver ?? "") + "' called " + op + " while '" + P.Driver + "' holds the calm profile " + P.Id);
                return "REFUSED: the calm profile " + P.Id + " belongs to driver '" + P.Driver + "'; '" + (driver ?? "") + "' may only read. Nothing was changed.";
            }

            /// <summary>Arm the profile on this game. Each control the scene did not except is offered to `apply`, except under CAMPAIGN,
            /// where every control is refused by name and none is applied. keepLease: a re-arm after a load keeps the deadline.</summary>
            internal string Arm(Profile p, object game, bool campaign, double nowS, Func<ControlDef, Record, Applied> apply, bool keepLease = false)
            {
                if (p == null) return "REFUSED: no profile";
                if (Armed && P != null && !ReferenceEquals(P, p) && !string.Equals(P.Driver, p.Driver, StringComparison.Ordinal))
                    return Call(p.Driver, "arm", -1);
                if (game == null) return "REFUSED: the calm profile needs a game";
                if (Armed && !keepLease) Leave("armed again");
                P = p; Game = game; State.Clear();
                foreach (var c in p.Controls)
                {
                    string why;
                    if (p.Except.Contains(c.Name)) { State[c.Name] = new ControlState { Status = Excepted, Why = "taken off by the scene" }; continue; }
                    if (campaign)
                    {
                        State[c.Name] = new ControlState
                        {
                            Status = Refused,
                            Why = c.Destructive ? "DESTRUCTIVE (" + c.Class + "): refused while a canonical world save is loaded (CAMPAIGN)"
                                                : "a quiet-world control: refused while a canonical world save is loaded (CAMPAIGN)",
                        };
                        continue;
                    }
                    Applied a;
                    try { a = apply(c, R) ?? Applied.Fail("the applier returned nothing"); } catch (Exception e) { a = Applied.Fail(e.GetType().Name + ": " + e.Message); }
                    if (!a.ReadBack && a.Error == null) { State[c.Name] = new ControlState { Status = Off, Why = a.Detail ?? "not switched on by this profile" }; continue; }
                    string st;
                    if (a.Error != null) { st = CouldNotArm; why = a.Error; }
                    else st = StatusOf(c, a.ReadBack, p.Certified, out why);
                    State[c.Name] = new ControlState { Status = st, Why = why + (a.Detail != null ? "; " + a.Detail : ""), Stopped = a.Stopped };
                }
                if (!keepLease || !L.On) L.Arm(nowS, p.Minutes);
                Armed = true;
                return null;
            }

            /// <summary>A scene's exception: one named event through one gate, once. Closed at leave.</summary>
            internal string Except(JawaBenchGatesCore.Gate g, string name)
            {
                if (!Armed) return "REFUSED: no calm profile is armed";
                if (g == null || !g.On) return "REFUSED: that gate is not armed by the profile";
                if (string.IsNullOrWhiteSpace(name)) return "REFUSED: an exception names one event";
                g.AllowOne(name.Trim());
                _exceptions.Add(new Exception1 { Gate = g, Name = name.Trim() });
                return null;
            }

            internal List<string> OpenExceptions() => _exceptions.Select(x => x.Gate.Kind + ":" + x.Name).ToList();

            /// <summary>Leave: close every exception (an unused one is named), put back every entry in reverse order, end the lease.</summary>
            internal List<string> Leave(string why)
            {
                var lines = new List<string>();
                foreach (var x in _exceptions)
                {
                    int left = x.Gate.TakeBack(x.Name);
                    lines.Add("exception " + x.Gate.Kind + ":" + x.Name + (left > 0 ? " closed UNUSED" : " closed, used"));
                }
                _exceptions.Clear();
                var npb = new List<string>();
                lines.AddRange(R.PutBackAll(why, npb));
                LastNotPutBack = npb;
                L.End(why);
                Armed = false;
                LastLeave = lines;
                return lines;
            }

            /// <summary>After a load: close every exception (a used one is named closed, an unused one is carried), put back what can be
            /// put back on the old game, arm the same profile on the new game with its deadline kept, and open the carried exceptions
            /// again on their gates (the re-arm cleared the allow lists). null when armed, else the refusal (the profile is then left).</summary>
            internal string Rearm(object game, bool campaign, double nowS, Func<ControlDef, Record, Applied> apply, List<string> lines)
            {
                var carry = new List<Exception1>();
                foreach (var x in _exceptions)
                {
                    if (x.Gate.TakeBack(x.Name) > 0) carry.Add(x);
                    else lines?.Add("exception " + x.Gate.Kind + ":" + x.Name + " closed, used");
                }
                _exceptions.Clear();
                var npb = new List<string>();
                lines?.AddRange(R.PutBackAll("the game changed (a load)", npb));
                LastNotPutBack = npb;
                Rearms++;
                var why = Arm(P, game, campaign, nowS, apply, keepLease: true);
                if (why != null) { Leave("re-arm refused: " + why); return why; }
                foreach (var x in carry)
                {
                    if (x.Gate.On) { x.Gate.AllowOne(x.Name); _exceptions.Add(x); lines?.Add("exception " + x.Gate.Kind + ":" + x.Name + " carried over the load"); }
                    else lines?.Add("exception " + x.Gate.Kind + ":" + x.Name + " closed UNUSED: its gate did not arm again");
                }
                return null;
            }

            /// <summary>Each frame: a lease that ran out puts back now; a game that changed under the profile asks for a re-arm.</summary>
            internal List<string> Tick(double nowS, object game, out bool rearm)
            {
                rearm = false;
                if (!Armed) return null;
                if (L.Expired(nowS)) return Leave("lease ended");
                if (!ReferenceEquals(game, Game)) rearm = true;
                return null;
            }

            /// <summary>Attempts that the controls stopped, and schedulers that they switched off: two numbers, never one sum.</summary>
            internal long AttemptsStopped()
            {
                long n = 0;
                if (P == null) return 0;
                foreach (var c in P.Controls)
                {
                    ControlState s;
                    if (c.Counts != Attempts || !State.TryGetValue(c.Name, out s) || s.Stopped == null) continue;
                    try { n += s.Stopped(); } catch { }
                }
                return n;
            }

            internal int SchedulingSwitchedOff()
            {
                if (P == null) return 0;
                return P.Controls.Count(c => c.Counts == Scheduling && State.TryGetValue(c.Name, out var s) && (s.Status == Held || s.Status == Unproven));
            }
        }
    }
}
