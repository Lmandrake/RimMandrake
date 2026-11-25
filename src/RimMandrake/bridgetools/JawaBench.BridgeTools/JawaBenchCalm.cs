// JawaBenchCalm.cs - the calm map, the Verse half: hooks, readings, repairs, restore. Pure rules: JawaBenchCalmCore.cs.
// Page: design/specs/2026-11-23-calm-map/boundary.md. Tool: jawa/quiet_site (JawaBenchQuietSiteTools.cs).
//
// Engine facts, read from decompiled 1.6 through RimSage on 2026-11-23:
//   IncidentWorker.TryExecute(IncidentParms)  public, not virtual: every caller (storyteller, queue, quests, our tools) meets it
//   Storyteller.StorytellerTick               runs IncidentQueueTick every tick, whatever DebugSettings.enableStoryteller says
//   WeatherDecider.ForcedWeather              the LAST condition that forces a weather wins
//   WeatherManager.TransitionTo               sets lastWeather = curWeather; two calls settle the rain rate at once
//   GameCondition.End()                       removes the condition now (Duration = TicksPassed would wait one tick)
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using AW = JawaBench.BridgeTools.JawaBenchAwareness;
using C = JawaBench.BridgeTools.JawaBenchCalmCore;
using VT = JawaBench.BridgeTools.JawaBenchVitals;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCalm
    {
        internal const string HarmonyId = "mandrake.jawabench.calm";
        internal static readonly JawaBenchSafetyCore.QuietBlock Lease = new JawaBenchSafetyCore.QuietBlock();
        internal static readonly C.BreachLog Breaches = new C.BreachLog();
        internal static string PatchStatus = "not patched";
        internal static long QueueTicksHeld;

        // the last calm's arguments: what reassert sets again
        internal static bool EverArmed;
        internal static string WeatherName = "Clear";
        internal static HashSet<string> Allow = new HashSet<string>(), Except = new HashSet<string>(), KeepDefs = new HashSet<string>(), KeepIds = new HashSet<string>();
        internal static int MapId = -1;
        internal static int ArmTick
        {
            get { return _armGame?.Target is object game && ReferenceEquals(game, Current.Game) ? _armTick : -1; }
        }

        private static WeakReference _armGame;
        private static int _armTick = -1;
        private static HashSet<int> _known = new HashSet<int>();
        private static long _placed;
        private static bool _owed;                                           // a restore is owed (the calm changed something)
        private static readonly Dictionary<string, bool> Saved = new Dictionary<string, bool>();
        private static readonly HashSet<CompProximityLetter> SavedLetters = new HashSet<CompProximityLetter>();
        private static Map _letterMap;
        private static GameCondition _ours;
        private static bool _wildOurs;
        private static double _calmMinutes = JawaBenchSafetyCore.QuietBlock.DefaultMinutes;
        private static bool _probing;
        private static long _probeHeld, _probeQueueHeld;
        internal static List<string> LastRestore = new List<string>();

        private static double Now => JawaBenchTpsWatchdog.Now;
        private static int Tick() { try { return Find.TickManager != null ? Find.TickManager.TicksGame : -1; } catch { return -1; } }

        internal static bool Active() => Active(Now);

        private static bool Active(double now)
        {
            if (!Lease.On) return false;
            if (!JawaBenchCompanionSafety.CurrentPolicy.WildSpawnerBlock) { Lease.Release("campaign-profile"); return false; }
            return Lease.Active(Current.Game, now);
        }

        // ------------------------------------------------------------------ hooks
        /// <summary>Main thread only. null when the hooks are in place, read from Harmony (a hook that somebody removed
        /// is put back), else why not.</summary>
        internal static string EnsurePatched()
        {
            try
            {
                if (!UnityData.IsInMainThread) return PatchStatus = "not on the main thread";
                var h = new Harmony(HarmonyId);
                HarmonyMethod Hm(string n, int pri) => new HarmonyMethod(typeof(JawaBenchCalm).GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic)) { priority = pri };
                var exec = AccessTools.Method(typeof(IncidentWorker), "TryExecute", new[] { typeof(IncidentParms) });
                var queue = AccessTools.Method(typeof(IncidentQueue), "IncidentQueueTick", Type.EmptyTypes);
                var spawn = AccessTools.DeclaredMethod(typeof(Pawn), "SpawnSetup", new[] { typeof(Map), typeof(bool) });
                var frame = AccessTools.Method(typeof(Root_Play), "Update", Type.EmptyTypes);
                if (exec == null || queue == null || spawn == null || frame == null)
                    return PatchStatus = "not found:" + (exec == null ? " IncidentWorker.TryExecute" : "") + (queue == null ? " IncidentQueue.IncidentQueueTick" : "") + (spawn == null ? " Pawn.SpawnSetup" : "") + (frame == null ? " Root_Play.Update" : "");
                if (!Mine(exec)) h.Patch(exec, prefix: Hm(nameof(GatePre), Priority.First));
                if (!Mine(queue)) h.Patch(queue, prefix: Hm(nameof(QueuePre), Priority.First));
                if (!Mine(spawn)) h.Patch(spawn, postfix: Hm(nameof(SpawnPost), Priority.Normal));
                if (!Mine(frame)) h.Patch(frame, prefix: Hm(nameof(FramePre), Priority.First));
                PatchStatus = "patched";
                return null;
            }
            catch (Exception e) { return PatchStatus = "patch failed: " + e.GetType().Name + ": " + e.Message; }
        }

        private static bool Mine(MethodBase m)
        {
            var i = Harmony.GetPatchInfo(m);
            return i != null && (i.Prefixes.Any(p => p.owner == HarmonyId) || i.Postfixes.Any(p => p.owner == HarmonyId));
        }

        /// <summary>null while our pawn hook is on, else why arrivals are not seen.</summary>
        private static string ArrivalHookOff()
        {
            var spawn = AccessTools.DeclaredMethod(typeof(Pawn), "SpawnSetup", new[] { typeof(Map), typeof(bool) });
            return spawn != null && Mine(spawn) ? null : "the hook on Pawn.SpawnSetup is gone";
        }

        private static bool GatePre(IncidentWorker __instance, IncidentParms parms, ref bool __result)
        {
            try
            {
                if (!Lease.On || !Active()) return true;
                var def = __instance?.def?.defName;
                if (!C.Holds(true, def, Allow)) return true;
                if (__instance is ProbeWorker) _probeHeld++;
                else Breaches.Add("incident_held", Tick(), (def ?? "?") + (parms?.target is Map m ? " on map " + m.uniqueID : "") +
                                  (parms?.quest != null ? " from quest " + parms.quest.id : "") + (InTick() ? " (in a tick)" : " (from a call outside a tick)"));
                __result = false;
                return false;
            }
            catch { return true; }
        }

        private static bool QueuePre()
        {
            try
            {
                if (Lease.On && Active())
                {
                    if (_probing) _probeQueueHeld++; else QueueTicksHeld++;
                    return false;
                }
                if (_owed && !_probing) Restore("lease ended: " + (Lease.LastRelease ?? "unknown"));   // runs each tick, on the main thread
            }
            catch { }
            return true;
        }

        private static void FramePre()
        {
            try
            {
                // Root_Play.Update runs on the main thread even when the game tick is paused.
                if (_owed && !Active()) Restore("lease ended: " + (Lease.LastRelease ?? "unknown"));
                JawaBenchCalmProfile.Frame();            // the calm profile's lease, re-arm after a load and watchers (no site of its own)
            }
            catch { }
        }

        private static void SpawnPost(Pawn __instance, Map map, bool respawningAfterLoad, bool __runOriginal)
        {
            try
            {
                JawaBenchCalmProfile.Spawned(__instance, map, respawningAfterLoad, __runOriginal);   // the calm profile's arrival watch
                if (!__runOriginal || respawningAfterLoad || __instance == null || map == null || !Lease.On || !Active() || map.uniqueID != MapId) return;
                if (!_known.Add(__instance.thingIDNumber)) return;
                if (InTick()) Breaches.Add("arrival", Tick(), PawnText(__instance));
                else _placed++;
            }
            catch { }
        }

        /// <summary>Is the game inside a tick? Read from the call stack: this runs only for a held incident or a new pawn.</summary>
        private static bool InTick() => new StackTrace(2, false).ToString().IndexOf("DoSingleTick", StringComparison.Ordinal) >= 0;

        private sealed class ProbeWorker : IncidentWorker
        {
            internal bool Entered;
            protected override bool TryExecuteWorker(IncidentParms parms) { Entered = true; return false; }
        }

        // ------------------------------------------------------------------ text
        private static string PawnText(Pawn p) => p.ThingID + " " + (p.kindDef?.defName ?? p.def?.defName) + " (" + (p.Faction?.def?.defName ?? "no faction") + ") at " + p.Position.x + "," + p.Position.z;
        private static bool KeptPawn(Pawn p) => KeepIds.Contains(p.ThingID) || KeepIds.Contains(p.thingIDNumber.ToString()) ||
                                                KeepDefs.Contains(p.def?.defName ?? "") || KeepDefs.Contains(p.kindDef?.defName ?? "");

        // ------------------------------------------------------------------ things on the map
        private static List<Pawn> HostilePawns(Map map) => map.mapPawns.AllPawnsSpawned
            .Where(p => !p.Dead && Faction.OfPlayer != null && p.HostileTo(Faction.OfPlayer) && !p.IsPrisonerOfColony && !KeptPawn(p)).ToList();
        private static List<Pawn> PredatorPawns(Map map) => map.mapPawns.AllPawnsSpawned
            .Where(p => !p.Dead && p.Faction == null && p.RaceProps != null && p.RaceProps.Animal && p.RaceProps.predator && !KeptPawn(p)).ToList();
        private static List<Pawn> ArrivedPawns(Map map)
        {
            var rows = Breaches.Since(0).Where(b => b.Kind == "arrival").Select(b => b.What.Split(' ')[0]).ToList();
            var ids = new HashSet<string>(rows);
            return map.mapPawns.AllPawnsSpawned.Where(p => ids.Contains(p.ThingID) && !p.Dead && !KeptPawn(p)).ToList();
        }
        private static List<Building> ThreatBuildings(Map map)
        {
            var o = new List<Building>();
            foreach (var b in map.listerBuildings.allBuildingsNonColonist)
            {
                bool a1, a2, a3, a4;
                if (VT.IsThreatStructure(b, Faction.OfPlayer, out a1, out a2, out a3, out a4) && !KeepDefs.Contains(b.def?.defName ?? "")) o.Add(b);
            }
            return o;
        }
        private static List<CompProximityLetter> UnsentLetters(Map map) => map.listerThings.AllThings.OfType<ThingWithComps>()
            .Select(t => t.GetComp<CompProximityLetter>()).Where(c => c != null && !c.letterSent).ToList();
        private static List<Thing> Fires(Map map) => map.listerThings.ThingsOfDef(ThingDefOf.Fire).ToList();
        private static List<GameCondition> OtherConditions(Map map)
        {
            var all = new List<GameCondition>();
            map.gameConditionManager.GetAllGameConditionsAffectingMap(map, all);
            var want = DefDatabase<WeatherDef>.GetNamedSilentFail(WeatherName);
            return all.Where(c => !ReferenceEquals(c, _ours) && !(c is GameCondition_ForceWeather && want != null && c.ForcedWeather() == want)
                                  && !KeepDefs.Contains(c.def?.defName ?? "")).ToList();
        }

        // ------------------------------------------------------------------ the readings
        internal static List<C.Reading> ReadAll(Map map)
        {
            string lease = Active() ? null : "the calm is not on (" + (EverArmed ? "ended: " + (Lease.LastRelease ?? "unknown") : "never set") + ")";
            C.Reading Switch(string name, Func<bool> on) => C.Take(name, () => on()
                ? new C.Reading(name, C.NotCalm, "the engine's switch is ON", new[] { name })
                : new C.Reading(name, C.Held, "the engine's switch is off"));
            C.Reading List<T>(string name, Func<List<T>> get, Func<T, string> text) => C.Take(name, () =>
            {
                var l = get();
                return l.Count == 0 ? new C.Reading(name, C.Calm, "none") : new C.Reading(name, C.NotCalm, l.Count + " found", l.Take(40).Select(text));
            });
            var r = new List<C.Reading>
            {
                Switch(C.Storyteller, () => DebugSettings.enableStoryteller),
                Switch(C.MentalSwitch, () => DebugSettings.enableRandomMentalStates),
                Switch(C.Diseases, () => DebugSettings.enableRandomDiseases),
                C.Take(C.Gate, () => lease != null ? new C.Reading(C.Gate, C.NotCalm, lease, new[] { "any incident can run" }) : ProbeGate(map)),
                C.Take(C.Queue, () => ReadQueue(lease)),
                C.Take(C.Wild, () =>
                {
                    string why;
                    return AW.WildHolds(out why) ? new C.Reading(C.Wild, C.Held, "blocked; " + AW.WildSkipped + " spawner ticks skipped so far")
                                                 : new C.Reading(C.Wild, C.NotCalm, why, new[] { "wild animals can arrive" });
                }),
                C.Take(C.Weather, () => ReadWeather(map)),
                List(C.Conditions, () => OtherConditions(map), c => c.def?.defName),
                List(C.Hostiles, () => HostilePawns(map), PawnText),
                List(C.Predators, () => PredatorPawns(map), PawnText),
                C.Take(C.Arrivals, () =>
                {
                    if (lease != null) return new C.Reading(C.Arrivals, C.NotRead, lease + ": nobody watched for arrivals");
                    var off = ArrivalHookOff();
                    if (off != null) return new C.Reading(C.Arrivals, C.NotRead, off);
                    if (MapId != map.uniqueID) return new C.Reading(C.Arrivals, C.NotRead, "the watch is on map " + MapId + ", not " + map.uniqueID);
                    if (Breaches.Dropped > 0) return new C.Reading(C.Arrivals, C.NotRead, Breaches.Dropped + " breach rows were dropped, so an arrival may be missing from the list");
                    var l = ArrivedPawns(map);
                    string d = Breaches.Count("arrival") + " arrived in a tick since tick " + ArmTick + "; " + _placed + " placed by calls";
                    return l.Count == 0 ? new C.Reading(C.Arrivals, C.Calm, d) : new C.Reading(C.Arrivals, C.NotCalm, d, l.Take(40).Select(PawnText));
                }),
                List(C.Threats, () => ThreatBuildings(map), b => b.ThingID + " (" + (b.Faction?.Name ?? "?") + ")"),
                List(C.Letters, () => UnsentLetters(map), c => c.parent.ThingID),
                List(C.Fires, () => Fires(map), f => "fire at " + f.Position.x + "," + f.Position.z),
                List(C.MentalNow, () => map.mapPawns.AllPawnsSpawned.Where(p => p.InMentalState && !KeptPawn(p)).ToList(), p => PawnText(p) + " " + p.MentalStateDef?.defName),
                List(C.Windows, () => Find.WindowStack.Windows.Where(w => w.forcePause).ToList(), w => w.GetType().Name),
            };
            return r;
        }

        private static C.Reading ProbeGate(Map map)
        {
            long before = _probeHeld;
            var w = new ProbeWorker { def = new IncidentDef { defName = "JawaBench_CalmProbe" } };
            string threw = null;
            try { w.TryExecute(new IncidentParms { target = map }); } catch (Exception e) { threw = e.GetType().Name + ": " + e.Message; }
            if (!w.Entered && _probeHeld == before + 1)
                return new C.Reading(C.Gate, C.Held, "a probe incident was held" + (Allow.Count > 0 ? "; allowed: " + string.Join(", ", Allow.ToArray()) : "") + "; " + Breaches.Count("incident_held") + " real attempts held");
            bool hooked = Mine(AccessTools.Method(typeof(IncidentWorker), "TryExecute", new[] { typeof(IncidentParms) }));
            if (!w.Entered && !hooked) return new C.Reading(C.Gate, C.NotCalm, "our hook on IncidentWorker.TryExecute is gone", new[] { "any incident can run" });
            if (w.Entered) return new C.Reading(C.Gate, C.NotCalm, "the probe incident RAN: the gate does not hold on this mod list", new[] { "any incident can run" });
            return new C.Reading(C.Gate, C.NotRead, "the probe neither ran nor met the gate" + (threw != null ? " (" + threw + ")" : " (another mod's hook stopped it first)"));
        }

        private static C.Reading ReadQueue(string lease)
        {
            var q = Find.Storyteller?.incidentQueue;
            if (q == null) return new C.Reading(C.Queue, C.NotRead, "no storyteller or queue");
            var rows = new List<string>();
            foreach (var o in q)
                if (o is QueuedIncident qi) rows.Add((qi.FiringIncident?.def?.defName ?? "?") + " due at tick " + qi.FireTick);
            if (lease != null) return new C.Reading(C.Queue, C.NotCalm, lease + "; " + rows.Count + " queued", rows.Count > 0 ? rows : new List<string> { "the queue can fire" });
            long before = _probeQueueHeld;
            _probing = true;
            try { new IncidentQueue().IncidentQueueTick(); } finally { _probing = false; }
            if (_probeQueueHeld != before + 1) return new C.Reading(C.Queue, C.NotCalm, "a probe queue was not held", rows.Count > 0 ? rows : new List<string> { "the queue can fire" });
            return new C.Reading(C.Queue, C.Held, "frozen; " + rows.Count + " queued" + (rows.Count > 0 ? ": " + string.Join("; ", rows.Take(10).ToArray()) : ""));
        }

        private static C.Reading ReadWeather(Map map)
        {
            var want = DefDatabase<WeatherDef>.GetNamedSilentFail(WeatherName);
            if (want == null) return new C.Reading(C.Weather, C.NotRead, "no WeatherDef '" + WeatherName + "'");
            var wm = map.weatherManager;
            var forced = map.weatherDecider.ForcedWeather;
            string d = "now " + wm.curWeather?.defName + ", forced " + (forced?.defName ?? "none") + ", rain " + wm.RainRate.ToString("0.##") + ", snow " + wm.SnowRate.ToString("0.##");
            var bad = new List<string>();
            if (wm.curWeather != want) bad.Add("the weather is " + wm.curWeather?.defName);
            if (forced != want) bad.Add(forced == null ? "no weather is forced" : "the forced weather is " + forced.defName);
            if (Math.Abs(wm.RainRate - want.rainRate) > 0.001f || Math.Abs(wm.SnowRate - want.snowRate) > 0.001f) bad.Add("rain or snow has not settled");
            return bad.Count == 0 ? new C.Reading(C.Weather, C.Held, d) : new C.Reading(C.Weather, C.NotCalm, d, bad);
        }

        // ------------------------------------------------------------------ set
        /// <summary>Set every control that the scene did not except. Errors are returned by control name, never swallowed.</summary>
        internal static List<string> Apply(Map map, bool newBaseline, bool clear, double? minutes, string by)
        {
            var errors = new List<string>();
            void Do(string control, Action a)
            {
                if (Except.Contains(control)) return;
                try { a(); } catch (Exception e) { errors.Add(control + ": " + e.GetType().Name + ": " + e.Message); }
            }
            var p = EnsurePatched();
            if (p != null) errors.Add(C.Gate + ": hooks: " + p);
            double now = Now;
            bool fresh = newBaseline || !Active(now) || MapId != map.uniqueID;
            if (fresh)
            {
                if (_owed) Restore("set again");
                MapId = map.uniqueID; _armTick = Tick(); _placed = 0; Breaches.Clear(); QueueTicksHeld = 0;
                _armGame = new WeakReference(Current.Game);
                _known = new HashSet<int>(map.mapPawns.AllPawnsSpawned.Select(x => x.thingIDNumber));
            }
            EverArmed = true;
            _owed = true;
            if (newBaseline) _calmMinutes = minutes ?? JawaBenchSafetyCore.QuietBlock.DefaultMinutes;
            double? renewal = fresh ? (minutes ?? _calmMinutes) : minutes;
            if (renewal.HasValue) Lease.Block(Current.Game, now, renewal.Value, by);
            Do(C.Storyteller, () => Off("enableStoryteller", () => DebugSettings.enableStoryteller, v => DebugSettings.enableStoryteller = v));
            Do(C.MentalSwitch, () => Off("enableRandomMentalStates", () => DebugSettings.enableRandomMentalStates, v => DebugSettings.enableRandomMentalStates = v));
            Do(C.Diseases, () => Off("enableRandomDiseases", () => DebugSettings.enableRandomDiseases, v => DebugSettings.enableRandomDiseases = v));
            Do(C.Wild, () =>
            {
                var err = AW.EnsureWildPatch();
                if (err != null) throw new InvalidOperationException(err);
                bool wildActive = AW.Wild.Active(Current.Game, now);
                if (!wildActive) _wildOurs = true;
                if (!wildActive || renewal.HasValue)
                    AW.Wild.Block(Current.Game, now, renewal ?? (Lease.UntilS - now) / 60.0, by);
            });
            Do(C.Weather, () => SetWeather(map));
            Do(C.Letters, () =>
            {
                _letterMap = map;
                foreach (var letter in UnsentLetters(map))
                {
                    SavedLetters.Add(letter);
                    letter.letterSent = true;
                }
            });
            if (clear)
            {
                Do(C.Conditions, () => { foreach (var c in OtherConditions(map)) { c.suppressEndMessage = true; c.End(); } });
                Do(C.Hostiles, () => { foreach (var x in HostilePawns(map)) x.Destroy(DestroyMode.Vanish); });
                Do(C.Predators, () => { foreach (var x in PredatorPawns(map)) x.Destroy(DestroyMode.Vanish); });
                Do(C.Arrivals, () => { foreach (var x in ArrivedPawns(map)) if (x.Faction != Faction.OfPlayer) x.Destroy(DestroyMode.Vanish); });
                Do(C.Threats, () =>
                {
                    foreach (var b in ThreatBuildings(map))
                        if (b.def != null && b.def.destroyable) b.Destroy(DestroyMode.Vanish); else if (b.Spawned) b.DeSpawn(DestroyMode.Vanish);
                });
                Do(C.Fires, () => { foreach (var f in Fires(map)) f.Destroy(DestroyMode.Vanish); });
            }
            return errors;
        }

        private static void Off(string name, Func<bool> get, Action<bool> set)
        {
            if (!Saved.ContainsKey(name)) Saved[name] = get();
            set(false);
        }

        private static void SetWeather(Map map)
        {
            var want = DefDatabase<WeatherDef>.GetNamedSilentFail(WeatherName);
            if (want == null) throw new InvalidOperationException("no WeatherDef '" + WeatherName + "'");
            var fw = _ours as GameCondition_ForceWeather;
            if (fw != null && map.gameConditionManager.ActiveConditions.Contains(fw)) fw.weather = want;
            if (map.weatherDecider.ForcedWeather != want)
            {
                var def = DefDatabase<GameConditionDef>.GetNamedSilentFail("WeatherController");
                if (def == null) throw new InvalidOperationException("no GameConditionDef WeatherController");
                EndOurWeather();
                var cond = GameConditionMaker.MakeConditionPermanent(def) as GameCondition_ForceWeather;
                if (cond == null) throw new InvalidOperationException("WeatherController is not a GameCondition_ForceWeather");
                cond.weather = want;
                cond.suppressEndMessage = true;
                map.gameConditionManager.RegisterCondition(cond);
                cond.weather = want;                        // Init() fills it only when it is null
                _ours = cond;
            }
            if (map.weatherManager.curWeather != want || map.weatherManager.lastWeather != want)
            {
                map.weatherManager.TransitionTo(want);
                map.weatherManager.TransitionTo(want);      // lastWeather too: the rain rate is right now, not in 4,000 ticks
            }
        }

        private static string EndOurWeather()
        {
            var c = _ours;
            _ours = null;
            if (c == null) return null;
            var mgr = c.gameConditionManager;
            if (mgr == null || !mgr.ActiveConditions.Contains(c)) return "the forced weather was already gone";
            if (Current.Game == null || !Find.Maps.Contains(mgr.ownerMap)) return "the forced weather belongs to a game or map that is gone";
            c.suppressEndMessage = true;
            c.End();
            return mgr.ActiveConditions.Contains(c) ? "COULD NOT END the forced weather" : "forced weather ended";
        }

        /// <summary>Put back what calm changed. A value that somebody else changed since is left, and said.</summary>
        internal static List<string> Restore(string reason)
        {
            var o = new List<string> { "reason: " + reason };
            _owed = false;
            Lease.Release(reason);
            void Back(string name, Func<bool> get, Action<bool> set)
            {
                bool was;
                if (!Saved.TryGetValue(name, out was)) return;
                if (get()) o.Add(name + " was already on: left");
                else { set(was); o.Add(name + " = " + get()); }
            }
            Back("enableStoryteller", () => DebugSettings.enableStoryteller, v => DebugSettings.enableStoryteller = v);
            Back("enableRandomMentalStates", () => DebugSettings.enableRandomMentalStates, v => DebugSettings.enableRandomMentalStates = v);
            Back("enableRandomDiseases", () => DebugSettings.enableRandomDiseases, v => DebugSettings.enableRandomDiseases = v);
            Saved.Clear();
            try
            {
                int restored = 0;
                if (SavedLetters.Count > 0 && Current.Game != null && Find.Maps.Contains(_letterMap))
                    foreach (var letter in SavedLetters)
                        if (letter.parent.Map == _letterMap) { letter.letterSent = false; restored++; }
                if (restored > 0) o.Add(restored + " proximity letter(s) restored");
            }
            catch (Exception e) { o.Add("COULD NOT RESTORE proximity letters: " + e.Message); }
            SavedLetters.Clear();
            _letterMap = null;
            try { var w = EndOurWeather(); if (w != null) o.Add(w); } catch (Exception e) { o.Add("COULD NOT END the forced weather: " + e.Message); }
            try
            {
                var map = Find.Maps?.FirstOrDefault(m => m.uniqueID == MapId);
                var left = map?.weatherDecider.ForcedWeather;
                if (left != null) o.Add("the weather is still forced to " + left.defName + " by a condition that this calm did not set (another tool, or a save made while calm)");
            }
            catch (Exception e) { o.Add("the forced weather could not be read: " + e.Message); }
            if (_wildOurs) { AW.Wild.Release("calm released"); _wildOurs = false; o.Add("wild spawner released"); }
            try
            {
                var q = Find.Storyteller?.incidentQueue;
                int due = 0;
                if (q != null) foreach (var x in q) if (x is QueuedIncident qi && qi.FireTick <= Tick()) due++;
                if (due > 0) o.Add(due + " queued incident(s) became due while the queue was frozen: they fire on the next tick");
            }
            catch { }
            LastRestore = o;
            return o;
        }

        internal static bool RestoreOwed => _owed;
        internal static long Placed => _placed;
    }
}
