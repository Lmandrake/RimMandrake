// JawaBenchVitals.cs - the test-state monitor's Verse half (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO).
// Pure rules: JawaBenchVitalsCore.cs. Tools: JawaBenchVitalsTools.cs. Design: design/RimMandrake/test_control/monitor_governor_build.md.
//
// ENGINE MEMBERS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-10-13), NOT GUESSED:
//   Verse/TickManager.cs     public void DoSingleTick() (ticksGameInt++ or += 2000 under DebugSettings.fastEcology;
//                            GameEnder.GameEndTick and LetterStack tick run inside it); DebugSetTicksGame(int); Paused; CurTimeSpeed
//   RimWorld/GameEnder.cs    public bool gameEnding; GameEndTick sends LetterDefOf.GameEnded 400 ticks after the countdown starts
//   Verse/Letter.cs          public int ID; LetterDef def; int arrivalTick; TaggedString Label
//   Verse/Window.cs          public int ID; bool forcePause; bool absorbInputAroundWindow; virtual bool IsDebug
//   Verse/WindowStack.cs     int Count; Window this[int] (Windows allocates AsReadOnly: not used)
//   Verse/ListerBuildings.cs public readonly List<Building> allBuildingsNonColonist
//   RimWorld/CompCanBeDormant.cs  virtual bool Awake
//   RimWorld/GenHostility.cs HostileTo(this Thing, Faction)
//   Verse/AI/MentalBreaker.cs BreakThresholdMinor (a stat read: colonists only)
//
// LAWS
//   * Armed per test (TTL, max 240 min); disarmed = every hook returns at its first volatile read.
//   * DoSingleTick prefix/postfix installed at the FIRST arm only (a session that never arms has no patch).
//   * T60 = every 60 PROCESSED ticks (a reassignment cannot skip a deadline); W250 = wall-time pass from a hidden
//     MonoBehaviour (the playtest driver pattern), so a paused game is still watched.
//   * Rows go through the TPS record's ordered bounded writer as kind "vitals"; a dropped row is counted.
//   * Each channel has a switch (JawaBench/vitals_settings.json {"pawns": false, ...}; default all on) and a meter.
//     A channel that is off or has never run reports UNMEASURED, never 0.
//   * Observer faults are counted and contained; the game's own exceptions are never swallowed.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using A = JawaBench.BridgeTools.JawaBenchAwarenessCore;
using V = JawaBench.BridgeTools.JawaBenchVitalsCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    /// <summary>Per-frame pump for the monitor's wall pass and the safe-advance stepper.</summary>
    internal sealed class JawaBenchVitalsDriver : MonoBehaviour
    {
        private void Update() { JawaBenchVitals.Frame(); }
    }

    internal static class JawaBenchVitals
    {
        internal const string HarmonyId = "mandrake.jawabench.vitals";

        internal static readonly V.Latch Latch = new V.Latch();
        internal static readonly V.ClockLedger Clock = new V.ClockLedger();
        internal static readonly V.ModalAges Modals = new V.ModalAges();
        internal static readonly Dictionary<string, A.Meter> Meters = new Dictionary<string, A.Meter>();
        internal static readonly Dictionary<string, bool> Switch = new Dictionary<string, bool>();
        internal static readonly List<string> Tombs = new List<string>();     // death tombstone rows (json), bounded

        internal static volatile bool Armed;
        private static double _until;
        internal static string By, Why, Row, ArmedUtc, LastDisarm, HookStatus = "not-installed", HookDetail, DriverStatus = "none";
        internal static bool TimeException;
        internal static long Budget;
        internal static readonly HashSet<int> Critical = new HashSet<int>();
        internal static readonly Dictionary<int, Thing> Specimens = new Dictionary<int, Thing>();
        private static readonly HashSet<int> _specimenLost = new HashSet<int>();
        internal static readonly List<int> SpecimensUnresolved = new List<int>();

        internal static Dictionary<int, V.PawnObs> Prev;
        internal static V.Rollup LastRollup;
        private static string _lastRollupKey;
        private static double _lastRollupMono = -1, _lastWall = -1, _lastHeartbeat = -1, _lastPausedSample = -1;
        private static readonly Dictionary<int, string> _threats = new Dictionary<int, string>();
        internal static int ThreatTotal = -1, ThreatTurrets, ThreatSpawners, ThreatDormant;
        private static int _maxLetterId = -1, _ticksSinceSample, _ticksSinceThreat, _prevColonists = -1;
        private static bool _lastEnding, _lastPaused;
        private static string _lastSpeed;
        private static object _gameKey;
        internal static int Epoch;
        internal static long Samples, RowsWritten, RowsDropped, Faults, TickHookCalls;
        internal static string LastFault;
        internal static int LastSampleTick = -1;
        private static GameObject _driverGo;
        private static bool _hooksTried;

        internal static double Mono => W.Clock.Elapsed.TotalSeconds;

        static JawaBenchVitals()
        {
            foreach (var ch in V.Channels) { Meters[ch] = new A.Meter(); Switch[ch] = true; }
        }

        internal static bool On(string ch) => Switch.TryGetValue(ch, out var v) && v;

        // ------------------------------------------------------------------ arm / disarm (main thread)
        internal static object Arm(double ttlMin, string by, string why, string row, List<int> critical, List<int> specimens,
                                   bool timeException, long budget)
        {
            LoadSwitches();
            InstallHooks();
            EnsureDriver();
            double ttl = double.IsNaN(ttlMin) || ttlMin <= 0 ? 30 : Math.Min(ttlMin, 240);
            _until = Mono + ttl * 60.0;
            bool renew = Armed && Row == row;          // a different row starts a fresh latch and history
            By = by; Why = why; Row = row; TimeException = timeException; Budget = budget;
            Critical.Clear(); foreach (var i in critical) Critical.Add(i);
            ResolveSpecimens(specimens);
            if (!renew)
            {
                Latch.Clear(); Clock.Reset(); Modals.Clear(); Prev = null; _threats.Clear(); ThreatTotal = -1;
                Clock.LastAfter = GameReady() ? Find.TickManager.TicksGame : int.MinValue;   // the base is the arm tick: a reassignment before the first wall pass still counts (live 2026-10-13)
                _lastRollupKey = null; _maxLetterId = MaxLetterId(); _lastEnding = Find.GameEnder != null && Find.GameEnder.gameEnding;
                _prevColonists = -1; _gameKey = Current.Game; Tombs.Clear(); _specimenLost.Clear();
                ArmedUtc = W.Utc();
            }
            Armed = true;
            Emit(V.ChHeartbeat, "arm", "\"renew\":" + V.B(renew) + ",\"ttlMin\":" + V.F(ttl, 1) + ",\"by\":" + V.J(by) + ",\"why\":" + V.J(why) +
                 ",\"row\":" + V.J(row) + ",\"critical\":[" + string.Join(",", Critical) + "],\"specimens\":[" + string.Join(",", Specimens.Keys) +
                 "],\"timeException\":" + V.B(timeException) + ",\"budget\":" + budget + ",\"hooks\":" + V.J(HookStatus));
            Sample("arm");
            return null;
        }

        internal static void Disarm(string reason)
        {
            if (!Armed) return;
            Emit(V.ChHeartbeat, "disarm", "\"reason\":" + V.J(reason) + ",\"triggers\":" + Latch.Seq + ",\"first\":" + (Latch.First?.Json() ?? "null"));
            Armed = false;
            LastDisarm = reason;
        }

        internal static bool Populated()
        {
            var maps = Find.Maps;
            if (maps == null) return false;
            for (int i = 0; i < maps.Count; i++) if (maps[i].mapPawns.FreeColonistsSpawnedCount > 0) return true;
            return false;
        }

        private static void ResolveSpecimens(List<int> ids)
        {
            Specimens.Clear(); SpecimensUnresolved.Clear();
            if (ids.Count == 0) return;
            var want = new HashSet<int>(ids);
            foreach (var map in Find.Maps)
                foreach (var t in map.listerThings.AllThings)
                    if (want.Contains(t.thingIDNumber)) { Specimens[t.thingIDNumber] = t; want.Remove(t.thingIDNumber); }
            SpecimensUnresolved.AddRange(want);
        }

        private static int MaxLetterId()
        {
            int m = -1;
            var ls = Find.LetterStack?.LettersListForReading;
            if (ls != null) for (int i = 0; i < ls.Count; i++) if (ls[i].ID > m) m = ls[i].ID;
            return m;
        }

        private static void LoadSwitches()
        {
            try
            {
                string p = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"), "vitals_settings.json");
                if (!File.Exists(p)) return;
                string s = File.ReadAllText(p).Replace(" ", "");
                foreach (var ch in V.Channels) Switch[ch] = !s.Contains("\"" + ch + "\":false");
            }
            catch (Exception e) { Fault("settings", e); }
        }

        // ------------------------------------------------------------------ hooks + driver
        private static void InstallHooks()
        {
            if (_hooksTried) return;
            _hooksTried = true;
            try
            {
                var h = new Harmony(HarmonyId);
                var t = typeof(JawaBenchVitals);
                var targets = new List<JawaBenchTpsInstall.Target>
                {
                    new JawaBenchTpsInstall.Target("TickManager.DoSingleTick", true, () => AccessTools.Method(typeof(TickManager), nameof(TickManager.DoSingleTick))),
                };
                HookStatus = JawaBenchTpsInstall.Run(targets, (name, m) =>
                    h.Patch((MethodInfo)m, prefix: new HarmonyMethod(t.GetMethod(nameof(TickPre), BindingFlags.Static | BindingFlags.NonPublic)),
                                           postfix: new HarmonyMethod(t.GetMethod(nameof(TickPost), BindingFlags.Static | BindingFlags.NonPublic))),
                    () => h.UnpatchAll(HarmonyId), out HookDetail);
            }
            catch (Exception e) { HookStatus = "failed"; HookDetail = e.GetType().Name + ": " + e.Message; }
        }

        private static void EnsureDriver()
        {
            if (_driverGo != null && _driverGo.GetComponent<JawaBenchVitalsDriver>() != null) return;
            try
            {
                _driverGo = new GameObject("JawaBench.VitalsDriver");
                UnityEngine.Object.DontDestroyOnLoad(_driverGo);
                DriverStatus = _driverGo.AddComponent<JawaBenchVitalsDriver>() != null ? "monobehaviour" : "AddComponent returned null";
            }
            catch (Exception e) { DriverStatus = "failed: " + e.GetType().Name + ": " + e.Message; }
        }

        /// <summary>A game that is safe to read: Playing AND its TickManager has a start tick. While a save loads from inside a
        /// game, ProgramState is still Playing and Current.Game is already the NEW, unloaded Game (gameStartAbsTick 0,
        /// TicksGame 0): reading TicksAbs then logs vanilla's ErrorOnce (TESTENV_VITALS_REPAIR_TICKSABS_SECOND_SOURCE), and
        /// a clock baseline taken then reads the load as a jump 0 -> N (TESTENV_VITALS_HARDEN_LOADS_ARE_NOT_JUMPS).</summary>
        internal static bool GameReady()
        {
            return Current.ProgramState == ProgramState.Playing && Current.Game != null && Find.TickManager != null
                   && Find.TickManager.gameStartAbsTick != 0;
        }

        /// <summary>A replaced Game (load or new game) is a new EPOCH, never a clock jump: histories restart and the clock
        /// baseline is UNSET, so the first tick observed in the new game becomes the base. Called from the tick hook too,
        /// because the new game's first DoSingleTick runs before the frame finalizer notices the swap.</summary>
        private static void EnsureEpoch(double now)
        {
            if (ReferenceEquals(_gameKey, Current.Game)) return;
            _gameKey = Current.Game; Epoch++;
            Clock.Reset(); Prev = null; _threats.Clear(); ThreatTotal = -1; Modals.Clear(); _maxLetterId = MaxLetterId(); _prevColonists = -1;
            var t = new V.Trigger { Kind = V.KCoverage, Severity = V.SCoverage, Tick = Find.TickManager.TicksGame, Mono = now,
                                    Detail = "game replaced (load or new game): epoch " + Epoch + "; histories restart, clock re-based" };
            Latch1(t);
        }

        private static void TickPre(TickManager __instance, out int __state)
        {
            __state = int.MinValue;
            if (!Armed) return;
            try
            {
                if (!GameReady()) return;                 // __state stays MinValue: a tick of an unloaded game is not counted
                EnsureEpoch(Mono);
                __state = __instance.TicksGame;
                if (On(V.ChClock)) Latch1(Clock.BeforeTick(__state, Mono));
            }
            catch (Exception e) { Fault("tick-pre", e); }
        }

        private static void TickPost(TickManager __instance, int __state)
        {
            if (!Armed || __state == int.MinValue) return;
            try
            {
                TickHookCalls++;
                long t0 = Stopwatch.GetTimestamp();
                if (On(V.ChClock)) Latch1(Clock.AfterTick(__state, __instance.TicksGame, Mono));
                else Clock.Processed++;
                Meters[V.ChClock].Add(Stopwatch.GetTimestamp() - t0);
                if (++_ticksSinceSample >= V.SampleEveryTicks) Sample("t60");
            }
            catch (Exception e) { Fault("tick-post", e); }
        }

        /// <summary>From JawaBenchEventRecorder.KillPostfix (only real deaths reach it). The tombstone outlives the corpse.</summary>
        internal static void OnKill(Pawn p, DamageInfo? dinfo, Hediff culprit)
        {
            if (!Armed || p == null) return;
            try
            {
                var o = Observe(p);
                bool anyCrit = Critical.Count > 0;
                string sev = V.Matters(o, anyCrit) ? V.SDamage : (o.Colonist ? V.SThreat : V.SInfo);
                string cause = dinfo.HasValue && dinfo.Value.Def != null ? dinfo.Value.Def.defName : (culprit != null ? culprit.def?.defName : null);
                string inst = dinfo.HasValue && dinfo.Value.Instigator != null ? dinfo.Value.Instigator.ThingID : null;
                var t = V.T(V.KDeath, sev, Find.TickManager.TicksGame, o, "died: " + (cause ?? "unknown cause") + (inst != null ? " by " + inst : ""));
                t.Mono = Mono;
                Latch.Add(t);
                string tomb = "{\"tick\":" + t.Tick + ",\"pawn\":" + o.Json() + ",\"cause\":" + V.J(cause) + ",\"instigator\":" + V.J(inst) + "}";
                if (Tombs.Count >= V.TombCapacity) Tombs.RemoveAt(0);
                Tombs.Add(tomb);
                Emit(V.ChPawns, "tomb", "\"tomb\":" + tomb);
                Emit(V.ChPawns, "trigger", "\"trigger\":" + t.Json());
                if (Prev != null) Prev.Remove(p.thingIDNumber);
            }
            catch (Exception e) { Fault("kill", e); }
        }

        // ------------------------------------------------------------------ per-frame (main thread)
        internal static void Frame()
        {
            if (!Armed) return;
            try
            {
                double now = Mono;
                if (now >= _until) { Disarm("ttl"); return; }
                if (!GameReady()) return;
                EnsureEpoch(now);
                JawaBenchSafeAdvance.Frame();
                if (now - _lastWall < V.WallPassSeconds) return;
                _lastWall = now;
                WallPass(now);
            }
            catch (Exception e) { Fault("frame", e); }
        }

        private static void WallPass(double now)
        {
            var tm = Find.TickManager;
            int tick = tm.TicksGame;
            long t0 = Stopwatch.GetTimestamp();
            if (On(V.ChClock))
            {
                Latch1(Clock.Frame(tick, now));
                string spd = tm.CurTimeSpeed.ToString();
                if (tm.Paused != _lastPaused || spd != _lastSpeed)
                {
                    Emit(V.ChClock, "speed", "\"paused\":" + V.B(tm.Paused) + ",\"speed\":" + V.J(spd) + ",\"processed\":" + Clock.Processed);
                    _lastPaused = tm.Paused; _lastSpeed = spd;
                }
            }
            Meters[V.ChClock].Add(Stopwatch.GetTimestamp() - t0);
            if (On(V.ChUi)) UiPass(now, tick);
            // a paused game still changes (dev spawns, kills): a sample at most once per wall second while ticks stand still
            if (LastSampleTick == tick && now - _lastPausedSample >= 1.0) { _lastPausedSample = now; Sample("paused"); }
            if (On(V.ChHeartbeat) && now - _lastHeartbeat >= V.HeartbeatSeconds) { _lastHeartbeat = now; Heartbeat(now); }
        }

        private static void UiPass(double now, int tick)
        {
            long t0 = Stopwatch.GetTimestamp();
            var ws = Find.WindowStack;
            var blocking = new List<int>();
            var byId = new Dictionary<int, Window>();
            if (ws != null)
                for (int i = 0; i < ws.Count; i++)
                {
                    var w = ws[i];
                    if (w == null || w.IsDebug) continue;
                    if (w.forcePause || w.absorbInputAroundWindow) { blocking.Add(w.ID); byId[w.ID] = w; }
                }
            var fresh = new List<int>(); var crossed = new List<int>();
            Modals.Observe(blocking, now, V.ModalStuckSeconds, fresh, crossed);
            foreach (int id in fresh)
            {
                var w = byId[id];
                Emit(V.ChUi, "window", "\"windowId\":" + id + ",\"type\":" + V.J(w.GetType().FullName) + ",\"forcePause\":" + V.B(w.forcePause) +
                                      ",\"absorbInput\":" + V.B(w.absorbInputAroundWindow) + ",\"paused\":" + V.B(Find.TickManager.Paused));
            }
            foreach (int id in crossed)
            {
                var w = byId[id];
                Latch1(new V.Trigger { Kind = V.KModalStuck, Severity = V.SBlock, Tick = tick, Mono = now, SubjectId = id, Subject = w.GetType().Name,
                                       Detail = "blocking window " + w.GetType().FullName + " open " + V.F(Modals.Age(id, now), 1) + " s (paused=" + Find.TickManager.Paused + ")" });
            }
            LettersAndEnder(tick, now);
            Meters[V.ChUi].Add(Stopwatch.GetTimestamp() - t0);
        }

        /// <summary>Letters (insertion observed by id; GameEnded = colony loss) and the GameEnder countdown. Runs on the wall
        /// pass AND every T60 sample: a fast advance can start and cancel a game-over countdown (Man in Black, live
        /// 2026-10-13) between two wall passes.</summary>
        private static void LettersAndEnder(int tick, double now)
        {
            var ls = Find.LetterStack?.LettersListForReading;
            if (ls != null)
                for (int i = 0; i < ls.Count; i++)
                {
                    var l = ls[i];
                    if (l == null || l.ID <= _maxLetterId) continue;
                    _maxLetterId = Math.Max(_maxLetterId, l.ID);
                    string def = l.def?.defName;
                    string label = null;
                    try { label = l.Label.RawText; } catch { }
                    Emit(V.ChUi, "letter", "\"letterId\":" + l.ID + ",\"def\":" + V.J(def) + ",\"label\":" + V.J(A.Clip(label, 120)) + ",\"arrivalTick\":" + l.arrivalTick);
                    if (l.def == LetterDefOf.GameEnded)
                        Latch1(new V.Trigger { Kind = V.KColonyLoss, Severity = V.SDamage, Tick = tick, Mono = now, Subject = label, Detail = "GameEnded letter: " + label });
                    else if (def == "ThreatBig" || def == "ThreatSmall")
                        Latch1(new V.Trigger { Kind = V.KLetter, Severity = V.SThreat, Tick = tick, Mono = now, Subject = label, Detail = def + " letter: " + label });
                }
            bool ending = Find.GameEnder != null && Find.GameEnder.gameEnding;
            if (ending && !_lastEnding)
                Latch1(new V.Trigger { Kind = V.KColonyLoss, Severity = V.SDamage, Tick = tick, Mono = now, Detail = "GameEnder countdown started (no free colonist anywhere)" });
            _lastEnding = ending;
        }

        // ------------------------------------------------------------------ sampling
        internal static V.PawnObs Observe(Pawn p)
        {
            var o = new V.PawnObs
            {
                Id = p.thingIDNumber, Map = p.MapHeld != null ? p.MapHeld.uniqueID : -1, Label = p.LabelShort, Def = p.def?.defName,
                Kind = p.kindDef?.defName, Colonist = p.IsColonist, Downed = !p.Dead && p.Downed, Critical = Critical.Contains(p.thingIDNumber),
                Mental = p.MentalStateDef?.defName,
            };
            try { o.Hostile = Faction.OfPlayer != null && p.HostileTo(Faction.OfPlayer); } catch { }
            var rp = p.RaceProps;
            o.Cls = rp == null ? "other" : rp.Humanlike ? "humanlike" : rp.IsMechanoid ? "mech" : rp.Animal ? "animal" : "other";
            o.Rel = p.Faction == Faction.OfPlayer ? "player" : o.Hostile ? "hostile" : "neutral";
            if (!p.Dead && p.health != null)
            {
                o.Health = p.health.summaryHealth.SummaryHealthPercent;
                o.Bleed = p.health.hediffSet.BleedRateTotal;
            }
            var needs = p.needs;
            if (needs != null)
            {
                if (needs.mood != null) o.Mood = needs.mood.CurLevel;
                if (needs.food != null) o.Food = needs.food.CurCategory.ToString();
            }
            if (o.Colonist && !float.IsNaN(o.Mood) && p.mindState?.mentalBreaker != null)
                try { o.MoodBreak = p.mindState.mentalBreaker.BreakThresholdMinor; } catch { }
            if (p.Spawned) { o.X = p.Position.x; o.Z = p.Position.z; }
            o.Job = p.CurJobDef?.defName;
            return o;
        }

        internal static List<V.PawnObs> Census()
        {
            var list = new List<V.PawnObs>();
            foreach (var map in Find.Maps)
            {
                var ps = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < ps.Count; i++) if (ps[i] != null && !ps[i].Dead) list.Add(Observe(ps[i]));
            }
            return list;
        }

        internal static void Sample(string why)
        {
            if (!Armed || Find.TickManager == null || Find.Maps == null) return;
            _ticksSinceSample = 0;
            int tick = Find.TickManager.TicksGame;
            LastSampleTick = tick;
            Samples++;
            try
            {
                if (On(V.ChPawns) || On(V.ChSubjects))
                {
                    long t0 = Stopwatch.GetTimestamp();
                    var cur = Census();
                    var trig = V.Diff(Prev, cur, Critical.Count > 0, tick);
                    double now = Mono;
                    foreach (var t in trig) { t.Mono = now; Latch1(t); }
                    var next = new Dictionary<int, V.PawnObs>(cur.Count);
                    foreach (var c in cur)
                    {
                        PawnObs0(c, out var old);
                        if (On(V.ChPawns) && c.Changed(old)) Emit(V.ChPawns, "pawn", "\"pawn\":" + c.Json());
                        next[c.Id] = c;
                    }
                    Prev = next;
                    var r = V.Rollup.Of(cur);
                    LastRollup = r;
                    if (_prevColonists > 0 && r.ColonistsAlive == 0)
                        Latch1(new V.Trigger { Kind = V.KColonyLoss, Severity = V.SDamage, Tick = tick, Mono = now, Detail = "alive colonists 0 on every map (map scope)" });
                    _prevColonists = r.ColonistsAlive;
                    string key = r.Key();
                    if (On(V.ChPawns) && (key != _lastRollupKey || now - _lastRollupMono >= V.RollupMinWallSeconds))
                    {
                        Emit(V.ChPawns, "rollup", "\"why\":" + V.J(why) + "," + r.Fields());
                        _lastRollupKey = key; _lastRollupMono = now;
                    }
                    Meters[V.ChPawns].Add(Stopwatch.GetTimestamp() - t0);
                }
                if (On(V.ChSubjects) && Specimens.Count > 0)
                {
                    long t0 = Stopwatch.GetTimestamp();
                    foreach (var kv in Specimens)
                    {
                        var th = kv.Value;
                        if (_specimenLost.Contains(kv.Key)) continue;
                        if (th.Destroyed || th.MapHeld == null)
                        {
                            _specimenLost.Add(kv.Key);
                            Latch1(new V.Trigger { Kind = V.KSpecimenLost, Severity = V.SDamage, Tick = tick, Mono = Mono, SubjectId = kv.Key, Subject = th.def?.defName,
                                                   Critical = true, Detail = (th.Destroyed ? "destroyed" : "no longer on any map") });
                        }
                    }
                    Meters[V.ChSubjects].Add(Stopwatch.GetTimestamp() - t0);
                }
                if (On(V.ChUi) && why == "t60") { long t1 = Stopwatch.GetTimestamp(); LettersAndEnder(tick, Mono); Meters[V.ChUi].Add(Stopwatch.GetTimestamp() - t1); }
                _ticksSinceThreat += V.SampleEveryTicks;
                if (On(V.ChThreats) && (why != "t60" || _ticksSinceThreat >= V.ThreatEveryTicks)) { _ticksSinceThreat = 0; ThreatPass(tick); }
            }
            catch (Exception e) { Fault("sample", e); }
        }

        private static void PawnObs0(V.PawnObs c, out V.PawnObs old)
        {
            old = null;
            if (Prev != null) Prev.TryGetValue(c.Id, out old);
        }

        private static void ThreatPass(int tick)
        {
            long t0 = Stopwatch.GetTimestamp();
            var player = Faction.OfPlayer;
            var seen = new HashSet<int>();
            int total = 0, turrets = 0, spawners = 0, dormant = 0, baseline = 0, newThisPass = 0, suppressed = 0;
            string baselineFirst = null;
            foreach (var map in Find.Maps)
            {
                var bs = map.listerBuildings.allBuildingsNonColonist;
                for (int i = 0; i < bs.Count; i++)
                {
                    var b = bs[i];
                    if (b == null || b.Faction == null || player == null || !b.Faction.HostileTo(player)) continue;
                    bool turret = b is Building_Turret;
                    bool spawner = b.GetComp<CompSpawnerPawn>() != null;
                    var dc = b.GetComp<CompCanBeDormant>();
                    bool asleep = dc != null && !dc.Awake;
                    // A hostile WALL is not a threat (live 2026-10-13: an ancient ruin's walls latched thousands of rows).
                    // Threat = can shoot, can make pawns, can wake up, causes a condition, or belongs to a non-humanlike
                    // faction (mechanoids, insects: every part of a mech cluster or hive counts).
                    bool causer = b.GetComp<CompCauseGameCondition>() != null;
                    bool nonHuman = b.Faction.def != null && !b.Faction.def.humanlikeFaction;
                    if (!(turret || spawner || dc != null || causer || nonHuman)) continue;
                    total++;
                    if (turret) turrets++;
                    if (spawner) spawners++;
                    if (asleep) dormant++;
                    seen.Add(b.thingIDNumber);
                    if (!_threats.ContainsKey(b.thingIDNumber))
                    {
                        string desc = b.def?.defName + " (" + b.Faction.Name + (turret ? ", turret" : "") + (spawner ? ", spawner" : "") + (asleep ? ", dormant" : "") + (causer ? ", condition causer" : "") + ")";
                        _threats[b.thingIDNumber] = desc;
                        if (ThreatTotal < 0) { baseline++; if (baselineFirst == null) baselineFirst = desc; continue; }   // present at arm: one summary row
                        if (++newThisPass > 8) { suppressed++; continue; }                                                  // a landing cluster: 8 rows, then a count
                        Latch1(new V.Trigger { Kind = V.KThreatStructure, Severity = V.SThreat, Tick = tick, Mono = Mono, SubjectId = b.thingIDNumber,
                                               Subject = b.def?.defName, Map = map.uniqueID,
                                               Detail = (ThreatTotal < 0 ? "present at arm: " : "new hostile structure: ") + desc });
                    }
                }
            }
            if (baseline > 0)
                Latch1(new V.Trigger { Kind = V.KThreatStructure, Severity = V.SThreat, Tick = tick, Mono = Mono, Subject = baselineFirst,
                                       Detail = "present at arm: " + baseline + " hostile threat structure(s), e.g. " + baselineFirst });
            if (suppressed > 0)
                Latch1(new V.Trigger { Kind = V.KThreatStructure, Severity = V.SThreat, Tick = tick, Mono = Mono,
                                       Detail = "and " + suppressed + " more new hostile structure(s) this pass (rows capped at 8)" });
            var gone = new List<int>();
            foreach (var k in _threats.Keys) if (!seen.Contains(k)) gone.Add(k);
            foreach (var k in gone) _threats.Remove(k);
            bool changed = total != ThreatTotal || turrets != ThreatTurrets || spawners != ThreatSpawners || dormant != ThreatDormant;
            ThreatTotal = total; ThreatTurrets = turrets; ThreatSpawners = spawners; ThreatDormant = dormant;
            if (changed) Emit(V.ChThreats, "threats", "\"structures\":" + total + ",\"turrets\":" + turrets + ",\"spawners\":" + spawners + ",\"dormant\":" + dormant);
            Meters[V.ChThreats].Add(Stopwatch.GetTimestamp() - t0);
        }

        private static void Heartbeat(double now)
        {
            long t0 = Stopwatch.GetTimestamp();
            var sb = new StringBuilder(400);
            sb.Append("\"samples\":").Append(Samples).Append(",\"processed\":").Append(Clock.Processed).Append(",\"disc\":").Append(Clock.Discontinuities)
              .Append(",\"discDeclared\":").Append(Clock.Declared).Append(",\"triggers\":").Append(Latch.Seq).Append(",\"latched\":").Append(V.B(Latch.First != null))
              .Append(",\"modalMaxAgeS\":").Append(V.F(Modals.MaxAge(now), 1)).Append(",\"lastSampleTick\":").Append(LastSampleTick)
              .Append(",\"rowsDropped\":").Append(RowsDropped).Append(",\"faults\":").Append(Faults).Append(",\"ttlLeftS\":").Append(V.F(Math.Max(0, _until - now), 0))
              .Append(",\"hooks\":").Append(V.J(HookStatus)).Append(",\"meters\":{");
            bool first = true;
            foreach (var ch in V.Channels)
            {
                if (!first) sb.Append(',');
                first = false;
                var m = Meters[ch];
                sb.Append(V.J(ch)).Append(":{\"on\":").Append(V.B(On(ch))).Append(",\"calls\":").Append(m.Calls)
                  .Append(",\"meanUs\":").Append(m.Calls == 0 ? "null" : V.F(m.MeanUs(Stopwatch.Frequency), 1))
                  .Append(",\"totalMs\":").Append(m.Calls == 0 ? "null" : V.F(m.TotalMs(Stopwatch.Frequency), 2)).Append('}');
            }
            sb.Append('}');
            Emit(V.ChHeartbeat, "heartbeat", sb.ToString());
            Meters[V.ChHeartbeat].Add(Stopwatch.GetTimestamp() - t0);
        }

        // ------------------------------------------------------------------ helpers
        internal static void DeclareClock(int target, string why) { if (Armed) Clock.Declare(target, why); }

        internal static void Latch1(V.Trigger t)
        {
            if (t == null) return;
            Latch.Add(t);
            Emit(ChOf(t.Kind), "trigger", "\"trigger\":" + t.Json());
        }

        private static string ChOf(string kind)
        {
            switch (kind)
            {
                case V.KClock: return V.ChClock;
                case V.KModalStuck: case V.KLetter: case V.KColonyLoss: return V.ChUi;
                case V.KThreatStructure: return V.ChThreats;
                case V.KSpecimenLost: return V.ChSubjects;
                case V.KCoverage: case V.KCancel: return V.ChHeartbeat;
                default: return V.ChPawns;
            }
        }

        internal static void Emit(string ch, string what, string fields)
        {
            if (!W.Running) { RowsDropped++; return; }
            int tick = -1; long abs = -1; int map = -1;
            // TicksAbs logs a Verse ErrorOnce while a game is being loaded (gameStartAbsTick unset), which turned GSS
            // proof_all's Z_log_budget red in pass 8. "Playing" alone was not enough: a load from inside a game keeps
            // ProgramState Playing while Current.Game is the new, unloaded Game -- GameReady() also needs the start tick.
            try { tick = Find.TickManager.TicksGame; abs = GameReady() ? Find.TickManager.TicksAbs : -1; map = Find.CurrentMap != null ? Find.CurrentMap.uniqueID : -1; } catch { }
            long seq = W.Enqueue("vitals", "\"ch\":" + V.J(ch) + ",\"what\":" + V.J(what) + ",\"epoch\":" + Epoch + ",\"tick\":" + tick + ",\"tickAbs\":" + abs +
                                           ",\"curMap\":" + map + ",\"row\":" + V.J(Row) + "," + fields);
            if (seq < 0) RowsDropped++; else RowsWritten++;
        }

        private static void Fault(string where, Exception e)
        {
            Faults++;
            LastFault = where + ": " + e.GetType().Name + ": " + e.Message;
        }

        internal static object ChannelStatus()
        {
            var d = new Dictionary<string, object>();
            foreach (var ch in V.Channels)
            {
                var m = Meters[ch];
                d[ch] = new
                {
                    on = On(ch),
                    calls = m.Calls,
                    cost = m.Calls == 0 ? "UNMEASURED" : "measured",
                    meanUs = m.Calls == 0 ? (double?)null : Math.Round(m.MeanUs(Stopwatch.Frequency), 2),
                    maxUs = m.Calls == 0 ? (double?)null : Math.Round(m.MaxUs(Stopwatch.Frequency), 1),
                    totalMs = m.Calls == 0 ? (double?)null : Math.Round(m.TotalMs(Stopwatch.Frequency), 3),
                };
            }
            return d;
        }

        internal static double TtlLeft => Armed ? Math.Max(0, _until - Mono) : 0;
    }

    // ====================================================================== safe advance (main thread, per frame)
    internal static class JawaBenchSafeAdvance
    {
        internal sealed class Run
        {
            internal long Requested, Executed, StartSeq;
            internal int Chunk, StartTick, EndTick;
            internal double FrameBudgetMs, StartMono, EndMono, MaxWallS;
            internal HashSet<string> Stop;
            internal volatile string State = "running";       // running | done | stopped | cancelled | aborted
            internal V.Trigger StopBy;
            internal string AbortWhy;
            internal bool TimeException;
            internal TimeSpeed PrevSpeed;
            internal int SettledFrames;
            internal long Frames;
        }

        internal static Run Cur;
        internal static volatile bool CancelRequested;

        internal static void Frame()
        {
            var r = Cur;
            if (r == null || r.State != "running") return;
            try
            {
                var tm = Find.TickManager;
                if (Current.Game == null || tm == null || LongEventHandler.AnyEventNowOrWaiting) { r.SettledFrames = 0; return; }
                if (r.SettledFrames < 3) { r.SettledFrames++; return; }
                r.Frames++;
                if (CancelRequested) { Finish(r, "cancelled", new V.Trigger { Kind = V.KCancel, Severity = V.SBlock, Detail = "cancel requested" }); return; }
                if (JawaBenchVitals.Mono - r.StartMono > r.MaxWallS) { Finish(r, "aborted", null, "exceeded " + r.MaxWallS + " s wall"); return; }
                if (!JawaBenchVitals.Armed) { Finish(r, "aborted", null, "monitor disarmed mid-advance (coverage lost)"); return; }
                if (tm.CurTimeSpeed != TimeSpeed.Paused) tm.CurTimeSpeed = TimeSpeed.Paused;
                var sw = Stopwatch.StartNew();
                while (r.Executed < r.Requested)
                {
                    var st = V.FirstStop(JawaBenchVitals.Latch.Since(r.StartSeq), r.Stop);
                    if (st != null) { Finish(r, "stopped", st); return; }
                    if (sw.Elapsed.TotalMilliseconds >= r.FrameBudgetMs) return;
                    int n = (int)Math.Min(r.Chunk, r.Requested - r.Executed);
                    for (int i = 0; i < n; i++) tm.DoSingleTick();
                    r.Executed += n;
                }
                var last = V.FirstStop(JawaBenchVitals.Latch.Since(r.StartSeq), r.Stop);
                Finish(r, last != null ? "stopped" : "done", last);
            }
            catch (Exception e) { Finish(r, "aborted", null, "stepper exception: " + e.GetType().Name + ": " + e.Message); }
        }

        internal static void Finish(Run r, string state, V.Trigger by, string why = null)
        {
            r.StopBy = by; r.AbortWhy = why; r.EndMono = JawaBenchVitals.Mono;
            try { r.EndTick = Find.TickManager.TicksGame; Find.TickManager.CurTimeSpeed = TimeSpeed.Paused; } catch { }
            r.State = state;
            JawaBenchVitals.Emit(V.ChClock, "advance", "\"state\":" + V.J(state) + ",\"requested\":" + r.Requested + ",\"executed\":" + r.Executed +
                                                     ",\"tickFrom\":" + r.StartTick + ",\"tickTo\":" + r.EndTick + ",\"stopBy\":" + (by?.Json() ?? "null") +
                                                     ",\"why\":" + V.J(why) + ",\"timeException\":" + V.B(r.TimeException));
        }
    }
}
