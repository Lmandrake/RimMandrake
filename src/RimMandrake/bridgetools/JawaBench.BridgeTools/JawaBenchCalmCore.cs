// JawaBenchCalmCore.cs - the PURE half of the calm map (no Verse, no Unity, no Harmony): the list of controls, the verdict
// over their readings, the incident gate's decision and the breach log. Page: design/specs/2026-11-23-calm-map/boundary.md.
// Compiled into bridgetools/LiveToolsSelfTest too: a `using Verse;` here breaks that build.
using System;
using System.Collections.Generic;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCalmCore
    {
        internal const string Held = "HELD", Calm = "CALM", Excepted = "EXCEPTED", NotCalm = "NOT_CALM", NotRead = "COULD_NOT_READ";
        internal const string VCalm = "CALM", VNotCalm = "NOT_CALM", VNotRead = "COULD_NOT_READ", VNothing = "NOTHING_CHECKED";

        internal const string Storyteller = "storyteller", MentalSwitch = "random_mental_states", Diseases = "random_diseases",
            Gate = "incident_gate", Queue = "incident_queue", Wild = "wild_spawner", Weather = "weather",
            Conditions = "game_conditions", Hostiles = "hostiles", Predators = "predators", Arrivals = "arrivals",
            Threats = "threat_structures", Letters = "proximity_letters", Fires = "fires", MentalNow = "mental_states",
            Windows = "force_pause_windows";

        internal static readonly string[] Controls =
        {
            Storyteller, MentalSwitch, Diseases, Gate, Queue, Wild, Weather, Conditions, Hostiles, Predators, Arrivals,
            Threats, Letters, Fires, MentalNow, Windows,
        };

        /// <summary>What no control reads. Printed on every reply, so CALM is never read as "everything".</summary>
        internal static readonly string[] NotCovered =
        {
            "needs, illness, pregnancy and withdrawal of any pawn", "outdoor temperature, hour and season", "inspirations and goodwill",
            "quests that run (their incidents meet the gate; their pawns are named under arrivals)",
            "an incident body that a mod runs without IncidentWorker.TryExecute", "other mods' spawners of things that are not pawns",
            "plant growth, roofs, explosives, short circuits", "autosave", "the camera and its update rate", "other maps",
        };

        internal sealed class Reading
        {
            internal string Name, Status, Detail;
            internal List<string> Things = new List<string>();
            internal Reading(string name, string status, string detail, IEnumerable<string> things = null)
            { Name = name; Status = status; Detail = detail; if (things != null) Things.AddRange(things); }
        }

        internal sealed class Report
        {
            internal string Verdict;
            internal readonly List<Reading> Readings = new List<Reading>();
            internal List<Reading> Of(string status) => Readings.Where(r => r.Status == status).ToList();
            internal bool IsCalm => Verdict == VCalm;
        }

        /// <summary>One reading; a throw is COULD_NOT_READ with its cause.</summary>
        internal static Reading Take(string name, Func<Reading> f)
        {
            try { return f() ?? new Reading(name, NotRead, "the reading returned nothing"); }
            catch (Exception e) { return new Reading(name, NotRead, e.GetType().Name + ": " + e.Message); }
        }

        /// <summary>CALM only when every control of the list that the scene did not except has exactly one reading, and that
        /// reading is HELD or CALM with no thing named. Nothing here defaults to calm.</summary>
        internal static Report Judge(IEnumerable<Reading> readings, ICollection<string> excepted, IList<string> controls = null)
        {
            var rep = new Report();
            var all = (readings ?? Enumerable.Empty<Reading>()).Where(r => r != null).ToList();
            int looked = 0;
            foreach (var name in controls ?? Controls)
            {
                if (excepted != null && excepted.Contains(name)) { rep.Readings.Add(new Reading(name, Excepted, "taken off by the scene")); continue; }
                looked++;
                var mine = all.Where(r => r.Name == name).ToList();
                if (mine.Count == 0) { rep.Readings.Add(new Reading(name, NotRead, "no reading was made")); continue; }
                var r0 = mine.FirstOrDefault(r => r.Status == NotCalm) ?? mine.FirstOrDefault(r => r.Status != Held && r.Status != Calm) ?? mine[0];
                if (r0.Status != Held && r0.Status != Calm && r0.Status != NotCalm && r0.Status != NotRead)
                    r0 = new Reading(name, NotRead, "unknown status '" + r0.Status + "'", r0.Things);
                else if (r0.Status == Calm && r0.Things.Count > 0)
                    r0 = new Reading(name, NotCalm, r0.Detail, r0.Things);      // a calm reading that names a thing is not calm
                rep.Readings.Add(r0);
            }
            rep.Verdict = rep.Of(NotCalm).Count > 0 ? VNotCalm : rep.Of(NotRead).Count > 0 ? VNotRead : looked == 0 ? VNothing : VCalm;
            return rep;
        }

        /// <summary>A comma list as a set; unknown = the first name that is not in `known` (null: any name is taken).</summary>
        internal static HashSet<string> ParseNames(string list, ICollection<string> known, out string unknown)
        {
            unknown = null;
            var o = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var raw in (list ?? "").Split(','))
            {
                var n = raw.Trim();
                if (n.Length == 0) continue;
                if (known != null)
                {
                    var k = known.FirstOrDefault(x => string.Equals(x, n, StringComparison.OrdinalIgnoreCase));
                    if (k == null) { unknown = unknown ?? n; continue; }
                    n = k;
                }
                o.Add(n);
            }
            return o;
        }

        /// <summary>The gate: hold this incident? Only while the calm is active, and never an allowed def.</summary>
        internal static bool Holds(bool active, string defName, ICollection<string> allow)
            => active && (defName == null || allow == null || !allow.Any(a => string.Equals(a, defName, StringComparison.OrdinalIgnoreCase)));

        internal sealed class Breach { internal long Seq; internal string Kind, What; internal int Tick; }

        /// <summary>Bounded rows, exact counts. Any thread.</summary>
        internal sealed class BreachLog
        {
            internal const int MaxRows = 200;
            private readonly object _gate = new object();
            private readonly LinkedList<Breach> _rows = new LinkedList<Breach>();
            private readonly Dictionary<string, long> _counts = new Dictionary<string, long>();
            private long _seq, _dropped;

            internal void Add(string kind, int tick, string what)
            {
                lock (_gate)
                {
                    long n; _counts.TryGetValue(kind, out n); _counts[kind] = n + 1;
                    _rows.AddLast(new Breach { Seq = ++_seq, Kind = kind, Tick = tick, What = what });
                    if (_rows.Count > MaxRows) { _rows.RemoveFirst(); _dropped++; }
                }
            }
            internal long Count(string kind) { lock (_gate) { long n; _counts.TryGetValue(kind, out n); return n; } }
            internal long Dropped { get { lock (_gate) return _dropped; } }
            internal long LastSeq { get { lock (_gate) return _seq; } }
            internal List<Breach> Since(long seq) { lock (_gate) return _rows.Where(b => b.Seq > seq).ToList(); }
            internal Dictionary<string, long> Counts() { lock (_gate) return new Dictionary<string, long>(_counts); }
            internal void Clear() { lock (_gate) { _rows.Clear(); _counts.Clear(); _dropped = 0; } }
        }
    }
}
