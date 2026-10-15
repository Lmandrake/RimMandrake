// JawaBenchAwarenessCore.cs - map awareness, the PURE half (no Verse, no Unity, no Harmony).
//
// Items: THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER, INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED (phase 2),
// PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN (phase 3). Design + reviews: Transient/foundry_map_awareness_*_20261010.md;
// what binds is restated in design/RimMandrake/map_awareness.md.
//
// ⛔ NO Verse/Unity/Harmony here: this file is compiled into the offline harness bridgetools/AwarenessSelfTest
// (net8.0) too, which is how every rule below is unit-tested without a game. The Verse half
// (JawaBenchAwareness.cs, JawaBenchAwarenessTools.cs) only gathers scalars and calls in here.
//
// The rules this file enforces (GPT review s3, each one a unit in AwarenessSelfTest/Units.cs):
//   * CONTEXT CHAIN, NOT TOP OF STACK. A context is an IMMUTABLE token with its parent: `bridge:jawa/fire_incident
//     > incident:RaidEnemy`, so our own injected raid stays ours and mapgen wildlife stays `mapgen > wild-spawner`.
//   * THREADS. Synchronous nesting uses a [ThreadStatic] current token; anything crossing a thread or a schedule
//     carries the token EXPLICITLY (Adopt). A thread-static stack alone never propagates causality.
//   * SKIP-SAFE SCOPES. Pop(token) restores exactly what Push saw, is idempotent, and tolerates a skipped push.
//   * EPOCHS. Every row carries the recording epoch; work from an old game never appends to a new one.
//   * BOUNDED. Tags, rings and the seen-set are capped; evictions are counted and reported, never silent.
//   * NO UPGRADES. Report text comes from Statement(), which never says "caused by"; IsForbidden() is the lint.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Threading;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchAwarenessCore
    {
        // ------------------------------------------------------------------ metric ids (game_health_record.md)
        internal const string MIncident = "aware.incident-journal";
        internal const string MContext = "aware.origin-context";
        internal const string MGeneration = "aware.origin-generation";
        internal const string MSpawn = "aware.origin-spawn";
        internal const string MDisk = "aware.disk-rows";
        internal const string MWild = "aware.wild-spawner-block";
        internal const string MExplain = "aware.thing-explain";
        internal static readonly string[] MetricIds = { MIncident, MContext, MGeneration, MSpawn, MDisk, MWild, MExplain };

        /// <summary>Install options (not metrics): install.generation-early = patch PawnGenerator.GeneratePawn at bridge
        /// registration (world generation and the first map pay for it) instead of lazily on the first arm
        /// (AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE). Default false.</summary>
        internal const string OptGenerationEarly = "install.generation-early";
        internal static readonly string[] OptionIds = { OptGenerationEarly };

        internal const int TagCapacity = 8192;          // generation tags (pawn id -> observation)
        internal const int SpawnCapacity = 2048;        // spawn observations retained
        internal const int IncidentCapacity = 512;      // incident journal rows retained
        internal const int SeenCapacity = 16384;        // pawn ids seen spawned this epoch (classification)
        internal const int MaxDepth = 12;               // context chain depth bound
        internal const int MaxLabel = 80;               // a context label is truncated to this
        internal const double DefaultTtlMinutes = 30, MaxTtlMinutes = 240;

        internal static string Clip(string s, int n = MaxLabel) => s == null ? null : (s.Length <= n ? s : s.Substring(0, n));

        // ------------------------------------------------------------------ switches (one per metric id)
        internal sealed class Switches
        {
            private readonly Dictionary<string, bool> _on = new Dictionary<string, bool>(StringComparer.Ordinal);
            private readonly Dictionary<string, bool> _opt = new Dictionary<string, bool>(StringComparer.Ordinal);
            internal string Note;
            internal Switches() { foreach (var id in MetricIds) _on[id] = true; foreach (var id in OptionIds) _opt[id] = false; }
            internal bool Option(string id) { lock (_on) return _opt.TryGetValue(id, out var v) && v; }
            internal Dictionary<string, bool> Options() { lock (_on) return new Dictionary<string, bool>(_opt); }
            internal bool On(string id) { lock (_on) return _on.TryGetValue(id, out var v) && v; }
            internal bool Set(string id, bool v)
            {
                lock (_on) { if (!_on.ContainsKey(id)) return false; _on[id] = v; return true; }
            }
            internal Dictionary<string, bool> Snapshot() { lock (_on) return new Dictionary<string, bool>(_on); }

            /// <summary>One flat JSON object {"aware.x": bool}. An unknown id, a non-bool or an invalid document is
            /// NOTED and the defaults (all on) stand for what it could not say.</summary>
            internal static Switches Parse(string json)
            {
                var s = new Switches();
                if (string.IsNullOrWhiteSpace(json)) { s.Note = "no settings file: defaults"; return s; }
                string err = JawaBenchTpsSettings.ParseFlat(json, out var kv);
                if (err != null) { s.Note = "invalid settings (" + err + "): defaults"; return s; }
                var notes = new List<string>();
                foreach (var p in kv)
                {
                    if (!(p.Value is bool b)) { notes.Add(p.Key + ": not a bool"); continue; }
                    if (s._opt.ContainsKey(p.Key)) { lock (s._on) s._opt[p.Key] = b; continue; }
                    if (!s.Set(p.Key, b)) notes.Add(p.Key + ": unknown metric id");
                }
                s.Note = notes.Count == 0 ? "ok" : string.Join("; ", notes);
                return s;
            }
        }

        // ------------------------------------------------------------------ measured cost per metric
        internal sealed class Meter
        {
            private long _calls, _ticks, _maxTicks;
            internal void Add(long ticks)
            {
                Interlocked.Increment(ref _calls);
                Interlocked.Add(ref _ticks, ticks);
                long m;
                while (ticks > (m = Interlocked.Read(ref _maxTicks)) && Interlocked.CompareExchange(ref _maxTicks, ticks, m) != m) { }
            }
            internal long Calls => Interlocked.Read(ref _calls);
            /// <summary>Mean microseconds per hook call: the body only (Harmony dispatch is NOT included).</summary>
            internal double MeanUs(double ticksPerSecond) => Calls == 0 ? 0 : Interlocked.Read(ref _ticks) * 1e6 / ticksPerSecond / Calls;
            internal double MaxUs(double ticksPerSecond) => Interlocked.Read(ref _maxTicks) * 1e6 / ticksPerSecond;
            internal double TotalMs(double ticksPerSecond) => Interlocked.Read(ref _ticks) * 1e3 / ticksPerSecond;
        }

        // ------------------------------------------------------------------ the context token
        internal sealed class Ctx
        {
            internal readonly string Kind, Label;       // kind: bridge | incident | mapgen | wild-spawner | spawner | hatch | birth | thread
            internal readonly long Id;
            internal readonly Ctx Parent;
            internal readonly int Epoch, Depth;
            internal Ctx(string kind, string label, long id, Ctx parent, int epoch)
            {
                Kind = kind; Label = Clip(label); Id = id; Parent = parent; Epoch = epoch;
                Depth = parent == null ? 1 : parent.Depth + 1;
            }
            internal Ctx Root { get { var c = this; while (c.Parent != null) c = c.Parent; return c; } }
            internal string Short => Kind + ":" + Label + "#" + Id.ToString(CultureInfo.InvariantCulture);
            /// <summary>Outermost first: "bridge:jawa/fire_incident#3 > incident:RaidEnemy#4".</summary>
            internal string Chain
            {
                get
                {
                    var parts = new List<string>();
                    for (var c = this; c != null; c = c.Parent) parts.Add(c.Short);
                    parts.Reverse();
                    return string.Join(" > ", parts);
                }
            }
            internal bool Contains(Ctx other) { for (var c = this; c != null; c = c.Parent) if (ReferenceEquals(c, other)) return true; return false; }
            internal bool HasKind(string kind) { for (var c = this; c != null; c = c.Parent) if (c.Kind == kind) return true; return false; }
        }

        internal struct Token
        {
            internal Ctx Prev, Mine;
            internal bool Valid;
        }

        private static long _ctxIds;
        internal static long NextCtxId() => Interlocked.Increment(ref _ctxIds);

        /// <summary>Per-thread current context + explicit tokens for anything that crosses a thread or a schedule.</summary>
        internal static class Scope
        {
            [ThreadStatic] private static Ctx _cur;
            internal static long Truncated;            // pushes refused by the depth bound
            internal static long Unbalanced;           // pops that found an inner scope still open (truncated to ours)

            /// <summary>The current context of THIS thread, or null. A context from another epoch is not current.</summary>
            internal static Ctx Current(int epoch) { var c = _cur; return c != null && c.Epoch == epoch ? c : null; }

            internal static Token Push(string kind, string label, int epoch)
            {
                var prev = _cur;
                var parent = prev != null && prev.Epoch == epoch ? prev : null;
                if (parent != null && parent.Depth >= MaxDepth)
                {
                    Interlocked.Increment(ref Truncated);
                    return new Token { Prev = prev, Mine = prev, Valid = false };
                }
                var mine = new Ctx(kind, label, NextCtxId(), parent, epoch);
                _cur = mine;
                return new Token { Prev = prev, Mine = mine, Valid = true };
            }

            /// <summary>Adopt a captured token on this thread (a scheduled lambda, a worker): the explicit carrier.</summary>
            internal static Token Adopt(Ctx captured, int epoch)
            {
                var prev = _cur;
                if (captured == null || captured.Epoch != epoch) return new Token { Prev = prev, Mine = prev, Valid = false };
                _cur = captured;
                return new Token { Prev = prev, Mine = captured, Valid = true };
            }

            /// <summary>Restore what the matching Push/Adopt saw. Idempotent; a token whose scope is already closed, or
            /// that never opened (a skipped prefix), changes nothing. An inner scope left open is closed with it.</summary>
            internal static void Pop(Token t)
            {
                if (!t.Valid) return;
                var cur = _cur;
                if (ReferenceEquals(cur, t.Mine)) { _cur = t.Prev; return; }
                if (cur != null && cur.Contains(t.Mine)) { Interlocked.Increment(ref Unbalanced); _cur = t.Prev; }
                // else: already popped (or another thread's token): nothing to do
            }

            internal static void ResetThreadForTest() { _cur = null; }
        }

        // ------------------------------------------------------------------ bounded FIFO map
        internal sealed class BoundedMap<TV>
        {
            private readonly Dictionary<int, TV> _d = new Dictionary<int, TV>();
            private readonly Queue<int> _order = new Queue<int>();
            internal readonly int Capacity;
            internal long Evicted;
            internal BoundedMap(int cap) { Capacity = cap; }
            internal int Count => _d.Count;
            internal bool TryGet(int k, out TV v) => _d.TryGetValue(k, out v);
            /// <summary>Insert; an existing key is NOT overwritten (returns false): history is never replaced.</summary>
            internal bool Add(int k, TV v)
            {
                if (_d.ContainsKey(k)) return false;
                while (_d.Count >= Capacity && _order.Count > 0)
                {
                    int old = _order.Dequeue();
                    if (_d.Remove(old)) Evicted++;
                }
                _d[k] = v; _order.Enqueue(k);
                return true;
            }
            internal void Set(int k, TV v) { if (!_d.ContainsKey(k)) Add(k, v); else _d[k] = v; }
            internal void Clear() { _d.Clear(); _order.Clear(); Evicted = 0; }
        }

        internal sealed class Ring<T> where T : class
        {
            private readonly T[] _buf; private long _total;
            internal Ring(int cap) { _buf = new T[cap]; }
            internal long Total => _total;
            internal long Overwritten => Math.Max(0, _total - _buf.Length);
            internal void Add(T x) { _buf[(int)(_total % _buf.Length)] = x; _total++; }
            internal List<T> Snapshot()
            {
                var l = new List<T>();
                for (long s = Math.Max(0, _total - _buf.Length); s < _total; s++) { var e = _buf[(int)(s % _buf.Length)]; if (e != null) l.Add(e); }
                return l;
            }
            internal void Clear() { Array.Clear(_buf, 0, _buf.Length); _total = 0; }
        }

        // ------------------------------------------------------------------ observations
        internal sealed class GenObs
        {
            internal long Seq; internal int Epoch, Tick, PawnId; internal string Kind, Chain, RootKind, Cause, Reuse, Thread;
            internal long CtxId; internal int Reobserved;
        }

        internal sealed class SpawnObs
        {
            internal long Seq; internal int Epoch, Tick, MapId, PawnId, X, Z; internal string Kind, Def, Faction;
            internal string Classification, SpawnChain; internal GenObs Gen; internal bool RanOriginal = true;
        }

        internal sealed class IncidentRec
        {
            internal long Seq; internal int Epoch, Tick; internal string Def, Target, Faction, Strategy, Arrival, Quest;
            internal bool Forced; internal float Points;
            internal string OuterBodyRan = "unknown";   // true | false | unknown (__runOriginal)
            internal string Returned = "pending";       // true | false | exception | pending
            internal string Exception;                  // the game's exception, observed (never swallowed)
            internal string WorkerEntered = "unknown";  // false only where a branch is established; never inferred from the return
            internal string WorkerEnteredWhy = "not instrumented";
            internal string Chain; internal long CtxId; internal int PawnsSpawnedDuring, PawnsGeneratedDuring;
        }

        internal static string Classify(BoundedMap<int> seen, int pawnId, int mapId)
        {
            if (seen.TryGet(pawnId, out var lastMap))
            {
                seen.Set(pawnId, mapId);
                return lastMap == mapId ? "observedRespawn" : "mapTransfer";
            }
            seen.Add(pawnId, mapId);
            // an evicted id could be an old pawn coming back: after any eviction "first" is no longer provable
            return seen.Evicted > 0 ? "unknown" : "firstObservedSpawn";
        }

        /// <summary>Our involvement from a chain, never from a guess: a chain rooted in a bridge tool means the pawn was
        /// generated or selected DURING our operation (not that we "made" it: GPT s3).</summary>
        internal static string Involvement(string rootKind) => rootKind == "bridge" ? "confirmedIndirectAction" : "unknown";

        // ------------------------------------------------------------------ statements (forbidden-upgrade table)
        internal static readonly string[] ForbiddenPhrases =
        {
            "caused by", "created by", "mapgen pawn", "generated before load", "newly created and intentionally",
            "no arrivals occurred", "this mod caused", "fired", "vanilla initiated", "intentionally spawned",
        };

        /// <summary>True when a report text claims more than the evidence allows (GPT s3 table). Case-insensitive.</summary>
        internal static bool IsForbidden(string text)
        {
            if (text == null) return false;
            var t = text.ToLowerInvariant();
            foreach (var p in ForbiddenPhrases) if (t.Contains(p)) return true;
            return false;
        }

        internal static string Statement(SpawnObs s)
        {
            if (s == null) return "present at baseline or before recording; origin unknown";
            string spawn = s.Classification == "firstObservedSpawn" ? "first observed spawn in this recording epoch"
                         : s.Classification == "observedRespawn" ? "seen spawned on this map before (respawn)"
                         : s.Classification == "mapTransfer" ? "seen on another map before (map transfer)"
                         : "spawn classification unknown (seen-set evicted)";
            string during = s.SpawnChain != null ? "; spawned during " + s.SpawnChain : "";
            if (s.Gen == null)
                return "origin unknown: no generation observation (generated before recording, outside a recorded " +
                       "context, or its tag was evicted); " + spawn + during;
            string what = s.Gen.Reuse == "reused" ? "an existing pawn was selected" :
                          s.Gen.Reuse == "new" ? "generated" : "generated or selected";
            return what + " during " + (s.Gen.Chain ?? "no recorded operation") + "; " + spawn + during;
        }

        internal static string IncidentStatement(IncidentRec r)
        {
            var sb = new StringBuilder();
            sb.Append("incident ").Append(r.Def).Append(" was called; outer body ran: ").Append(r.OuterBodyRan)
              .Append("; returned ").Append(r.Returned).Append("; worker entered: ").Append(r.WorkerEntered);
            if (r.Exception != null) sb.Append("; exception observed: ").Append(r.Exception);
            if (r.PawnsSpawnedDuring > 0 || r.PawnsGeneratedDuring > 0)
                sb.Append("; during the call ").Append(r.PawnsGeneratedDuring).Append(" pawn(s) generated, ")
                  .Append(r.PawnsSpawnedDuring).Append(" spawned (deferred deliveries are not counted here)");
            return sb.ToString();
        }

        // ------------------------------------------------------------------ the recorder state (one per process)
        internal sealed class Recorder
        {
            internal readonly object Gate = new object();
            internal int Epoch;
            internal object GameKey;                     // reference identity of the current Game (opaque here)
            internal long Seq;
            internal long InstallSeq = -1;               // seq when hooks went live; pawns before it are "baseline"
            internal readonly BoundedMap<GenObs> Tags = new BoundedMap<GenObs>(TagCapacity);
            internal readonly BoundedMap<int> Seen = new BoundedMap<int>(SeenCapacity);
            internal readonly Ring<SpawnObs> Spawns = new Ring<SpawnObs>(SpawnCapacity);
            internal readonly Ring<IncidentRec> Incidents = new Ring<IncidentRec>(IncidentCapacity);
            internal long UntaggedGenerations, LateRowsDropped, Faults, LoadRespawns;
            internal string LastFault;

            /// <summary>Called with the current Game object from every hook; a different object opens a new epoch and
            /// forgets the old game's state (nothing crosses games). Returns the epoch to stamp.</summary>
            internal int EpochFor(object game)
            {
                lock (Gate)
                {
                    if (game == null) return Epoch;
                    if (!ReferenceEquals(game, GameKey))
                    {
                        GameKey = game;
                        Epoch++;
                        Tags.Clear(); Seen.Clear(); Spawns.Clear(); Incidents.Clear();
                    }
                    return Epoch;
                }
            }

            internal long NextSeq() { lock (Gate) return ++Seq; }

            /// <summary>Record a generation; refuses a row from another epoch. Never overwrites an earlier creation
            /// record of the same id (a reuse is a re-observation, counted).</summary>
            internal bool AddGeneration(GenObs g)
            {
                lock (Gate)
                {
                    if (g.Epoch != Epoch) { LateRowsDropped++; return false; }
                    g.Seq = ++Seq;
                    if (Tags.TryGet(g.PawnId, out var old)) { old.Reobserved++; return false; }
                    return Tags.Add(g.PawnId, g);
                }
            }

            internal SpawnObs AddSpawn(int epoch, int tick, int mapId, int pawnId, string kind, string def, string faction,
                                       int x, int z, string spawnChain, bool ranOriginal)
            {
                lock (Gate)
                {
                    if (epoch != Epoch) { LateRowsDropped++; return null; }
                    Tags.TryGet(pawnId, out var gen);
                    var s = new SpawnObs
                    {
                        Seq = ++Seq, Epoch = epoch, Tick = tick, MapId = mapId, PawnId = pawnId, Kind = kind, Def = def,
                        Faction = faction, X = x, Z = z, Classification = Classify(Seen, pawnId, mapId),
                        SpawnChain = spawnChain, Gen = gen, RanOriginal = ranOriginal
                    };
                    Spawns.Add(s);
                    return s;
                }
            }

            /// <summary>A respawn after load is not an arrival; it only teaches the seen-set where the pawn is.</summary>
            internal void NoteLoadRespawn(int epoch, int pawnId, int mapId)
            {
                lock (Gate) { if (epoch != Epoch) return; Seen.Set(pawnId, mapId); LoadRespawns++; }
            }

            internal IncidentRec AddIncident(IncidentRec r)
            {
                lock (Gate)
                {
                    if (r.Epoch != Epoch) { LateRowsDropped++; return null; }
                    r.Seq = ++Seq;
                    Incidents.Add(r);
                    return r;
                }
            }

            internal void Fault(Exception e)
            {
                lock (Gate) { Faults++; LastFault = e.GetType().Name + ": " + e.Message; }
            }

            internal SpawnObs LatestSpawnOf(int pawnId)
            {
                lock (Gate)
                {
                    SpawnObs best = null;
                    foreach (var s in Spawns.Snapshot()) if (s.PawnId == pawnId) best = s;
                    return best;
                }
            }
        }

        // ------------------------------------------------------------------ disk arming (TTL)
        internal sealed class Arm
        {
            private DateTime _until = DateTime.MinValue;
            internal string By;
            internal void Set(DateTime nowUtc, double minutes, string by)
            {
                double m = double.IsNaN(minutes) || minutes <= 0 ? DefaultTtlMinutes : Math.Min(minutes, MaxTtlMinutes);
                _until = nowUtc.AddMinutes(m); By = by;
            }
            internal void Clear() { _until = DateTime.MinValue; By = null; }
            internal bool Armed(DateTime nowUtc) => nowUtc < _until;
            internal DateTime Until => _until;
        }

        // ------------------------------------------------------------------ thing_explain pure rules
        /// <summary>Exactly one selector. Returns null when fine, else the refusal text.</summary>
        internal static string SelectorProblem(string id, string cell, string name, bool selected)
        {
            int n = (string.IsNullOrWhiteSpace(id) ? 0 : 1) + (string.IsNullOrWhiteSpace(cell) ? 0 : 1) +
                    (string.IsNullOrWhiteSpace(name) ? 0 : 1) + (selected ? 1 : 0);
            if (n == 1) return null;
            return n == 0 ? "give exactly one selector: id, cell, name or selected=true"
                          : "give exactly ONE selector (got " + n + "): the tool never chooses between them";
        }

        /// <summary>The candidate winner is the LAST running mod holding the path: ContentFinder&lt;T&gt;.Get walks
        /// RunningModsListForReading from the end and returns the first hit (VERIFIED decompiled 1.6 via RimSage
        /// 2026-10-10). OBSERVED only when the rendered texture object was matched to a pack.</summary>
        internal static string[] ProviderVerdict(IList<string> packsInLoadOrder, string observedPack)
        {
            string candidate = packsInLoadOrder != null && packsInLoadOrder.Count > 0 ? packsInLoadOrder[packsInLoadOrder.Count - 1] : null;
            if (observedPack != null)
                return new[] { observedPack, "OBSERVED", candidate == observedPack ? "agrees with load order" : "differs from the load-order candidate " + (candidate ?? "(none)") };
            if (candidate != null)
                return new[] { candidate, "CANDIDATE", packsInLoadOrder.Count > 1 ? packsInLoadOrder.Count + " packs hold this path; last in load order wins ContentFinder" : "only pack holding this path" };
            return new[] { null, "UNKNOWN", "no loose texture at this path in any running mod (base resources or an asset bundle may supply it)" };
        }

        internal static string J(string s) => JawaBenchTpsMath.Json(s);
        internal static string I(long v) => v.ToString(CultureInfo.InvariantCulture);
    }
}
