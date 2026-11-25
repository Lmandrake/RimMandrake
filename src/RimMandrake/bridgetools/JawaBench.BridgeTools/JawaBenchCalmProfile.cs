// JawaBenchCalmProfile.cs - the calm profile of BRIDGE v2.0, the Verse half: each control's mechanism and its entries, the breach
// watchers, the lease and the re-arm after a load, and the tool jawa/calm_profile. The rules are JawaBenchCalmProfileCore.cs; page
// design/specs/2026-11-23-bridge-v2/boundary.md §CALM PROFILE. Item RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE.
//
// NO NEW PATCH SITE. The profile is driven from two hooks that the calm map already owns (JawaBenchCalm.cs, on HOOKS.md):
//   FramePre on Root_Play.Update   -> Frame(): the lease, the re-arm after a load, the gate breach poll, the needs hold, the weather watch
//   SpawnPost on Pawn.SpawnSetup   -> Spawned(): the arrival watch
// and the gates of JawaBenchGates.cs (the incident gate on the awareness prefix, the quest and mental prefixes).
// Built on the sibling's calm map (RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY): the same switches, the same forced
// weather route (WeatherController, TransitionTo twice), the same wild spawner block; the calm map's own incident gate and queue
// freeze are not used: the profile's are the scene gates, which the tap certificate proves.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using AW = JawaBench.BridgeTools.JawaBenchAwareness;
using K = JawaBench.BridgeTools.JawaBenchGatesCore;
using P = JawaBench.BridgeTools.JawaBenchCalmProfileCore;
using VT = JawaBench.BridgeTools.JawaBenchVitals;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCalmProfile
    {
        internal static readonly P.Session S = new P.Session();
        internal static int MapId = -1;
        internal static long Placed, Faults;
        internal static string LastFault;

        private static HashSet<int> _known = new HashSet<int>();
        private static HashSet<string> _keepDefs = new HashSet<string>(), _keepIds = new HashSet<string>();
        private static readonly Dictionary<string, long> _gateSeen = new Dictionary<string, long>();
        private static readonly List<KeyValuePair<Need, float>> _needs = new List<KeyValuePair<Need, float>>();
        private static string _weatherWant;
        private static double _saveKnownAt = -1;
        internal static string RearmPolicy;
        private static bool _weatherOff;

        static JawaBenchCalmProfile()
        {
            S.B.Sink = () => JawaBenchWorld.LiveSink;
        }

        private static double Now => JawaBenchTpsWatchdog.Now;
        private static long Tick() { try { return Find.TickManager != null ? Find.TickManager.TicksGame : -1; } catch { return -1; } }
        private static string B(bool v) => v ? "on" : "off";
        private static bool Campaign() => JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies;

        // ------------------------------------------------------------------ arm (main thread)
        internal static string Arm(P.Profile p, Map map)
        {
            var hook = JawaBenchCalm.EnsurePatched();
            if (hook != null) return "REFUSED: the frame hook that ends the lease is not on (" + hook + "): nothing was armed";
            double minutes = p.Minutes;
            var why = S.Arm(p, Current.Game, Campaign(), Now, (c, r) => Apply(c, r, map, p, minutes));
            if (why == null) Watch(map, p);
            return why;
        }

        /// <summary>After a load: put back what can be put back on the old game, then arm the same profile on the new one, with its
        /// certified lines and its deadline. Under CAMPAIGN every control is refused and nothing is applied.</summary>
        private static void Rearm()
        {
            var map = Find.CurrentMap;
            if (map == null || Current.ProgramState != ProgramState.Playing) return;      // still loading: the next frame
            // Right after a load the companion does not know the loaded save yet, and its policy reads CAMPAIGN until it does (and
            // keeps a reading for 2 s): measured on ArchBig 2026-11-25, a re-arm on the first frame read every control REFUSED.
            // So the re-arm waits until the save is known and the policy has been read again after that.
            string unknownWhy;
            if (JawaBenchCompanionSafety.LoadedSave(out unknownWhy) == null) { _saveKnownAt = -1; return; }
            if (_saveKnownAt < 0) { _saveKnownAt = Now; return; }
            if (Now - _saveKnownAt < 2.5) return;
            _saveKnownAt = -1;
            string pw, pd;
            RearmPolicy = JawaBenchCompanionSafety.Effective(out pw, out pd) + ": " + pw;
            var p = S.P;
            double minutes = S.L.SecondsLeft(Now) / 60.0;
            var lines = new List<string>();
            var why = S.Rearm(Current.Game, Campaign(), Now, (c, r) => Apply(c, r, map, p, minutes), lines);
            S.LastLeave = lines;
            if (why == null) Watch(map, p);
            else LastFault = "re-arm after a load refused: " + why;
        }

        private static void Watch(Map map, P.Profile p)
        {
            MapId = map.uniqueID;
            _known = new HashSet<int>(map.mapPawns.AllPawnsSpawned.Select(x => x.thingIDNumber));
            Placed = 0;
            _weatherOff = false;
            string unknown;
            _keepDefs = JawaBenchCalmCore.ParseNames(p.KeepDefs, null, out unknown);
            _keepIds = JawaBenchCalmCore.ParseNames(p.KeepIds, null, out unknown);
            _gateSeen.Clear();
            foreach (var g in JawaBenchGates.G.All) _gateSeen[g.Kind] = g.Rows().Select(a => a.Seq).DefaultIfEmpty(0).Max();
        }

        // ------------------------------------------------------------------ the controls
        private static P.Applied Apply(P.ControlDef c, P.Record r, Map map, P.Profile p, double minutes)
        {
            switch (c.Name)
            {
                case P.Storyteller: return Switch(r, c.Name, () => DebugSettings.enableStoryteller, v => DebugSettings.enableStoryteller = v);
                case P.MentalSwitch: return Switch(r, c.Name, () => DebugSettings.enableRandomMentalStates, v => DebugSettings.enableRandomMentalStates = v);
                case P.Diseases: return Switch(r, c.Name, () => DebugSettings.enableRandomDiseases, v => DebugSettings.enableRandomDiseases = v);
                case P.IncidentGate: return Gate(r, c.Name, K.Incident, p.AllowIncidents);
                case P.QuestGate: return Gate(r, c.Name, K.Quest, p.AllowQuests);
                case P.MentalGate: return Gate(r, c.Name, K.Mental, p.AllowMental);
                case P.Queue: return Queue(r);
                case P.Wild: return Wild(r, minutes);
                case P.Weather: return Weather(r, map, p.Weather);
                case P.Letters: return Letters(r, map);
                case P.NeedsHold: return Needs(r, map, p.HoldNeeds);
                case P.ClearSite: return p.Clear ? ClearSite(r, map) : P.Applied.NotOn("clear=false: nothing is removed");
            }
            return P.Applied.Fail("no mechanism for control '" + c.Name + "' in this companion");
        }

        /// <summary>An engine switch off. Put back writes the old value, unless another hand turned it on meanwhile (then it is left,
        /// and named by its read-back).</summary>
        private static P.Applied Switch(P.Record r, string control, Func<bool> get, Action<bool> set)
        {
            bool before = get();
            set(false);
            r.Add(control, P.PutBack, B(before), () => { if (get()) return "turned on by another hand while held: left on"; set(before); return null; },
                  () => B(get()));
            return get() ? P.Applied.Fail("the switch reads on after it was set off") : P.Applied.Ok("the engine's switch is off (was " + B(before) + ")");
        }

        private static P.Applied Gate(P.Record r, string control, string kind, string allow)
        {
            var refused = JawaBenchGates.Arm(kind, allow ?? "");
            if (refused != null) return P.Applied.Fail(refused);
            var g = JawaBenchGates.G.Of(kind);
            long held0 = g.Held;
            r.Add(control, P.PutBack, "off", () => { JawaBenchGates.Release(kind, "calm profile put back"); return null; }, () => B(g.On));
            string off = kind == K.Incident ? JawaBenchGates.IncidentHookOff() : JawaBenchGates.EnsurePatched();
            if (off != null) return P.Applied.Fail("armed, but its hook is not on: " + off);
            return g.On ? P.Applied.Ok("armed" + (string.IsNullOrEmpty(allow) ? "" : "; allowed: " + allow), () => g.Held - held0)
                        : P.Applied.Fail("the gate reads off after it was armed (" + g.LastRelease + ")");
        }

        private static P.Applied Queue(P.Record r)
        {
            var rep = new List<string>();
            var why = JawaBenchGates.HoldQueue(rep);
            if (why != null) return P.Applied.Fail(why);
            r.Add(P.Queue, P.GivenBack, "not held", () =>
            {
                var back = new List<string>();
                JawaBenchGates.GiveBackQueue(back);
                return back.Count > 0 ? string.Join("; ", back.ToArray()) : null;
            }, () => JawaBenchGates.G.Queue.Holding ? "held" : "not held");
            return JawaBenchGates.G.Queue.Holding ? P.Applied.Ok(JawaBenchGates.G.Queue.Count + " entries held aside" + (rep.Count > 0 ? "; " + string.Join("; ", rep.ToArray()) : ""))
                                                  : P.Applied.Fail("the queue reads not held after the hold");
        }

        private static P.Applied Wild(P.Record r, double minutes)
        {
            var err = AW.EnsureWildPatch();
            if (err != null) return P.Applied.Fail(err);
            double now = Now;
            long skipped0 = AW.WildSkipped;
            if (AW.Wild.Active(Current.Game, now)) return P.Applied.Ok("already blocked by another hold (" + AW.Wild.By + "): left to it", () => AW.WildSkipped - skipped0);
            AW.Wild.Block(Current.Game, now, minutes, "jawa/calm_profile");
            r.Add(P.Wild, P.PutBack, "off", () => { AW.Wild.Release("calm profile put back"); return null; }, () => B(AW.Wild.Active(Current.Game, Now)));
            string why;
            return AW.WildHolds(out why) ? P.Applied.Ok("blocked", () => AW.WildSkipped - skipped0) : P.Applied.Fail(why);
        }

        private static P.Applied Weather(P.Record r, Map map, string weather)
        {
            var want = DefDatabase<WeatherDef>.GetNamedSilentFail(weather ?? "Clear");
            if (want == null) return P.Applied.Fail("no WeatherDef '" + weather + "'");
            var def = DefDatabase<GameConditionDef>.GetNamedSilentFail("WeatherController");
            if (def == null) return P.Applied.Fail("no GameConditionDef WeatherController");
            var cond = GameConditionMaker.MakeConditionPermanent(def) as GameCondition_ForceWeather;
            if (cond == null) return P.Applied.Fail("WeatherController is not a GameCondition_ForceWeather");
            cond.weather = want;
            cond.suppressEndMessage = true;
            map.gameConditionManager.RegisterCondition(cond);
            cond.weather = want;                                   // Init() fills it only when it is null
            map.weatherManager.TransitionTo(want);
            map.weatherManager.TransitionTo(want);                 // lastWeather too: the rain rate is right now
            _weatherWant = want.defName;
            bool Live() => cond.gameConditionManager != null && Current.Game != null && Find.Maps.Contains(cond.gameConditionManager.ownerMap) &&
                           cond.gameConditionManager.ActiveConditions.Contains(cond);
            r.Add(P.Weather, P.PutBack, "no forced weather of ours", () => { if (Live()) { cond.suppressEndMessage = true; cond.End(); } return null; },
                  () => Live() ? "forced to " + want.defName + " by ours" : "no forced weather of ours");
            bool ok = map.weatherDecider.ForcedWeather == want && map.weatherManager.curWeather == want;
            return ok ? P.Applied.Ok("forced to " + want.defName)
                      : P.Applied.Fail("forced " + (map.weatherDecider.ForcedWeather?.defName ?? "none") + ", now " + map.weatherManager.curWeather?.defName + ": another condition forces the weather");
        }

        private static List<CompProximityLetter> Unsent(Map map) => map.listerThings.AllThings.OfType<ThingWithComps>()
            .Select(t => t.GetComp<CompProximityLetter>()).Where(c => c != null && !c.letterSent).ToList();

        private static P.Applied Letters(P.Record r, Map map)
        {
            var saved = Unsent(map);
            foreach (var l in saved) l.letterSent = true;
            bool Here() => Current.Game != null && Find.Maps.Contains(map);
            r.Add(P.Letters, P.PutBack, saved.Count + " unsent", () =>
            {
                if (!Here()) return null;                           // gone with its game: nothing to put back
                foreach (var l in saved) if (l.parent != null && l.parent.Map == map) l.letterSent = false;
                return null;
            }, () => (Here() ? saved.Count(l => !l.letterSent) : saved.Count) + " unsent");
            int left = Unsent(map).Count;
            return left == 0 ? P.Applied.Ok(saved.Count + " marked sent") : P.Applied.Fail(left + " proximity letters still unsent");
        }

        private static P.Applied Needs(P.Record r, Map map, string pawns)
        {
            string unknown;
            var ids = JawaBenchCalmCore.ParseNames(pawns, null, out unknown);
            if (ids.Count == 0) return P.Applied.NotOn("holdNeeds names no pawn");
            var found = new List<Pawn>();
            foreach (var id in ids)
            {
                var pawn = map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.ThingID == id || x.thingIDNumber.ToString(CultureInfo.InvariantCulture) == id);
                if (pawn == null) return P.Applied.Fail("holdNeeds: no pawn '" + id + "' on map " + map.uniqueID);
                if (pawn.needs == null) return P.Applied.Fail("holdNeeds: pawn " + id + " has no needs");
                found.Add(pawn);
            }
            _needs.Clear();
            foreach (var pawn in found) foreach (var n in pawn.needs.AllNeeds) _needs.Add(new KeyValuePair<Need, float>(n, n.CurLevel));
            r.AddNeedsHold(string.Join(", ", ids.ToArray()), () => { _needs.Clear(); return null; }, () => _needs.Count == 0 ? "not held" : "held");
            return P.Applied.Ok(_needs.Count + " needs of " + found.Count + " pawns held at their levels");
        }

        private static bool Kept(Pawn x) => _keepIds.Contains(x.ThingID) || _keepIds.Contains(x.thingIDNumber.ToString(CultureInfo.InvariantCulture)) ||
                                            _keepDefs.Contains(x.def?.defName ?? "") || _keepDefs.Contains(x.kindDef?.defName ?? "");

        private static P.Applied ClearSite(P.Record r, Map map)
        {
            var player = Faction.OfPlayer;
            var hostiles = map.mapPawns.AllPawnsSpawned.Where(x => !x.Dead && player != null && x.HostileTo(player) && !x.IsPrisonerOfColony && !Kept(x)).ToList();
            var predators = map.mapPawns.AllPawnsSpawned.Where(x => !x.Dead && x.Faction == null && x.RaceProps != null && x.RaceProps.Animal && x.RaceProps.predator && !Kept(x)).ToList();
            var fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire).ToList();
            var threats = new List<Building>();
            foreach (var b in map.listerBuildings.allBuildingsNonColonist)
            {
                bool a1, a2, a3, a4;
                if (VT.IsThreatStructure(b, player, out a1, out a2, out a3, out a4) && !_keepDefs.Contains(b.def?.defName ?? "")) threats.Add(b);
            }
            var all = new List<GameCondition>();
            map.gameConditionManager.GetAllGameConditionsAffectingMap(map, all);
            var conds = all.Where(x => !(x is GameCondition_ForceWeather && x.ForcedWeather()?.defName == _weatherWant) && !_keepDefs.Contains(x.def?.defName ?? "")).ToList();
            foreach (var x in hostiles.Concat(predators)) x.Destroy(DestroyMode.Vanish);
            foreach (var f in fires) f.Destroy(DestroyMode.Vanish);
            foreach (var b in threats) { if (b.def != null && b.def.destroyable) b.Destroy(DestroyMode.Vanish); else if (b.Spawned) b.DeSpawn(DestroyMode.Vanish); }
            foreach (var x in conds) { x.suppressEndMessage = true; x.End(); }
            r.Add(P.ClearSite, P.NotUndone, null, null, null, "save", "vanished " + hostiles.Count + " hostiles, " + predators.Count + " wild predators, " +
                  fires.Count + " fires, " + threats.Count + " threat structures; ended " + conds.Count + " conditions (" +
                  string.Join(", ", conds.Select(x => x.def?.defName).ToArray()) + ")");
            int left = hostiles.Count(x => x.Spawned) + predators.Count(x => x.Spawned) + fires.Count(x => x.Spawned) + threats.Count(x => x.Spawned);
            return left == 0 ? P.Applied.Ok() : P.Applied.Fail(left + " things are still on the map after the clear");
        }

        // ------------------------------------------------------------------ each frame (JawaBenchCalm.FramePre, main thread)
        internal static void Frame()
        {
            if (!S.Armed) return;
            try
            {
                bool rearm;
                var left = S.Tick(Now, Current.Game, out rearm);
                if (left != null) { _needs.Clear(); return; }
                if (rearm) { Rearm(); return; }
                if (Current.Game == null) return;
                PollGates();
                foreach (var kv in _needs) if (kv.Key.CurLevel != kv.Value) kv.Key.CurLevel = kv.Value;
                WatchWeather();
            }
            catch (Exception e) { Faults++; LastFault = "frame: " + e.GetType().Name + ": " + e.Message; }
        }

        /// <summary>Every attempt a gate held since the last frame is a breach of class ENVIRONMENT.</summary>
        private static void PollGates()
        {
            foreach (var g in JawaBenchGates.G.All)
            {
                long seen;
                _gateSeen.TryGetValue(g.Kind, out seen);
                foreach (var a in g.Rows())
                {
                    if (a.Seq <= seen) continue;
                    seen = a.Seq;
                    if (a.Outcome == "held") S.B.Add(P.Environment, g.Kind + "_held", a.Tick, (a.Name ?? "?") + " held by the " + g.Kind + " gate; caller " + a.Caller + (a.Detail != null ? "; " + a.Detail : ""));
                }
                _gateSeen[g.Kind] = seen;
            }
        }

        private static void WatchWeather()
        {
            if (_weatherWant == null || !S.State.TryGetValue(P.Weather, out var st) || (st.Status != P.Held && st.Status != P.Unproven)) return;
            var map = Find.Maps.FirstOrDefault(m => m.uniqueID == MapId);
            if (map == null) return;
            var now = map.weatherManager.curWeather?.defName;
            bool off = now != _weatherWant;
            if (off && !_weatherOff) S.B.Add(P.Environment, "weather", Tick(), "the weather is " + now + " (forced " + (map.weatherDecider.ForcedWeather?.defName ?? "none") + "), not " + _weatherWant);
            _weatherOff = off;
        }

        /// <summary>The arrival watch (JawaBenchCalm.SpawnPost): a pawn that appears on the profile's map in a game tick is a breach; one
        /// that a call places outside a tick is counted as placed.</summary>
        internal static void Spawned(Pawn pawn, Map map, bool respawningAfterLoad, bool runOriginal)
        {
            try
            {
                if (!S.Armed || !runOriginal || respawningAfterLoad || pawn == null || map == null || map.uniqueID != MapId) return;
                if (!_known.Add(pawn.thingIDNumber) || Kept(pawn)) return;
                if (new StackTrace(2, false).ToString().IndexOf("DoSingleTick", StringComparison.Ordinal) >= 0)
                    S.B.Add(P.Environment, "arrival", Tick(), pawn.ThingID + " " + (pawn.kindDef?.defName ?? pawn.def?.defName) + " (" + (pawn.Faction?.def?.defName ?? "no faction") + ") at " + pawn.Position.x + "," + pawn.Position.z);
                else Placed++;
            }
            catch (Exception e) { Faults++; LastFault = "spawn: " + e.GetType().Name + ": " + e.Message; }
        }

        // ------------------------------------------------------------------ the reply
        internal static Dictionary<string, object> Reply(string action, long sinceSeq)
        {
            var d = new Dictionary<string, object>
            {
                ["action"] = action, ["armed"] = S.Armed, ["profile"] = S.P?.Id, ["driver"] = S.P?.Driver, ["mapId"] = MapId,
                ["controls"] = S.P == null ? new List<object>() : S.P.Controls.Select(c =>
                {
                    P.ControlState st;
                    S.State.TryGetValue(c.Name, out st);
                    return (object)new Dictionary<string, object>
                    {
                        ["name"] = c.Name, ["status"] = st?.Status, ["why"] = st?.Why, ["class"] = c.Class, ["destructive"] = c.Destructive,
                        ["counts"] = c.Counts, ["certificateLine"] = c.CertLine,
                    };
                }).ToList(),
                ["certified"] = S.P == null ? new List<string>() : S.P.Certified.ToList(),
                ["exceptions"] = S.OpenExceptions(),
                ["attemptsStopped"] = S.AttemptsStopped(), ["schedulingSwitchedOff"] = S.SchedulingSwitchedOff(),
                ["entries"] = S.R.Live.Select(e => (object)new Dictionary<string, object>
                {
                    ["seq"] = e.Seq, ["control"] = e.Control, ["class"] = e.Class, ["before"] = e.Before, ["reach"] = e.Reach, ["detail"] = e.Detail,
                }).ToList(),
                ["notUndone"] = S.R.NotUndoneLines(), ["lastLeave"] = S.LastLeave, ["notPutBack"] = S.LastNotPutBack,
                ["breaches"] = new Dictionary<string, object>
                {
                    ["environment"] = S.B.OfClass(P.Environment), ["apparatus"] = S.B.OfClass(P.Apparatus), ["lastSeq"] = S.B.LastSeq, ["dropped"] = S.B.Dropped,
                    ["rows"] = S.B.Since(sinceSeq).Select(b => (object)new Dictionary<string, object> { ["seq"] = b.Seq, ["class"] = b.Class, ["kind"] = b.Kind, ["tick"] = b.Tick, ["what"] = b.What }).ToList(),
                },
                ["placed"] = Placed, ["rearms"] = S.Rearms, ["rearmPolicy"] = RearmPolicy, ["secondsLeft"] = Math.Round(S.L.SecondsLeft(Now), 0), ["leaseEnd"] = S.L.LastEnd,
                ["gates"] = JawaBenchGates.Summary(), ["faults"] = Faults, ["lastFault"] = LastFault, ["ticksGame"] = Tick(),
            };
            return d;
        }

        /// <summary>The profile keys of a JSON object; a number, a bool or a list becomes the text the core parses.</summary>
        internal static Dictionary<string, string> Keys(string spec, out string bad)
        {
            bad = null;
            var o = new Dictionary<string, string>(StringComparer.Ordinal);
            if (string.IsNullOrWhiteSpace(spec)) return o;
            Dictionary<string, object> d;
            try { d = JawaBenchCondCore.ParseJson(spec) as Dictionary<string, object>; } catch (Exception e) { bad = "spec is not JSON: " + e.Message; return null; }
            if (d == null) { bad = "spec is not a JSON object"; return null; }
            foreach (var kv in d)
            {
                var v = kv.Value;
                o[kv.Key] = v == null ? null : v is bool b ? (b ? "true" : "false") : v is double x ? x.ToString("R", CultureInfo.InvariantCulture)
                          : v is List<object> l ? string.Join(",", l.Select(i => Convert.ToString(i, CultureInfo.InvariantCulture)).ToArray())
                          : Convert.ToString(v, CultureInfo.InvariantCulture);
            }
            return o;
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/calm_profile",
            Description =
                "The calm profile of BRIDGE v2.0: a named, versioned list of controls armed in one call (profile standard/1: the engine's " +
                "storyteller, random mental state and disease switches; the incident, quest and mental gates with the scene's allow lists; the " +
                "incident queue held aside; the wild spawner; a forced weather; proximity letters; a needs hold for named pawns; with clear=true " +
                "the DESTRUCTIVE clear of hostiles, predators, fires, threat structures and conditions). A control reads HELD only with its " +
                "certificate line in `certified` (calm_profile.py fills it from a valid tap certificate), else ARMED UNPROVEN. Every held " +
                "attempt, arrival in a tick, weather change and second driver's write is a breach (class ENVIRONMENT or APPARATUS), also a " +
                "`breach` row of a running run's trace. The profile holds for `minutes` (default 30, max 240) of wall time, re-arms itself " +
                "after a load, and puts every entry back in reverse order with read-back at leave or at the end of its lease. " +
                "action=arm (spec: a JSON object of profile keys; driver) | read | renew (minutes) | except (gate incident|quest|mental, name: one " +
                "event through once) | leave.",
            ResultDescription =
                "success, action, armed, profile, driver, controls[] (name, status, why, class, destructive, counts, certificateLine), certified[], " +
                "exceptions[], attemptsStopped, schedulingSwitchedOff, entries[], notUndone[], lastLeave[], notPutBack[], breaches{environment, " +
                "apparatus, lastSeq, dropped, rows[]}, placed, rearms, secondsLeft, leaseEnd, gates, ticksGame; a refusal: success false, message.")]
        public static async Task<object> CalmProfile(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "arm | read | renew | except | leave", DefaultValue = "read")] string action = "read",
            [ToolParameter(Description = "who drives: the profile belongs to the driver that arms it; another driver may only read", DefaultValue = null)] string driver = null,
            [ToolParameter(Description = "arm: a JSON object of profile keys: profile, version, except, allowIncidents, allowQuests, allowMental, weather, minutes, clear, holdNeeds, keepDefs, keepIds, certified. An unknown key is refused.", DefaultValue = null)] string spec = null,
            [ToolParameter(Description = "renew: lease minutes from now (max 240)", DefaultValue = 0.0)] double minutes = 0.0,
            [ToolParameter(Description = "except: incident | quest | mental", DefaultValue = null)] string gate = null,
            [ToolParameter(Description = "except: the one event (incident def, quest root def, mental state def) let through once", DefaultValue = null)] string name = null,
            [ToolParameter(Description = "arm: map uniqueID, -1 = current map", DefaultValue = -1)] int mapId = -1,
            [ToolParameter(Description = "read: breach rows with seq above this", DefaultValue = 0L)] long sinceSeq = 0)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var S = JawaBenchCalmProfile.S;
                var a = (action ?? "read").Trim().ToLowerInvariant();
                long t = Find.TickManager != null ? Find.TickManager.TicksGame : -1;
                Dictionary<string, object> Done(string refusal)
                {
                    var d = JawaBenchCalmProfile.Reply(a, sinceSeq);
                    d["success"] = refusal == null;
                    d["message"] = refusal;
                    return d;
                }
                if (a == "read") return Done(null);
                if (a != "arm" && a != "renew" && a != "except" && a != "leave") return Fail("action must be arm, read, renew, except or leave");
                var no = S.Call(driver, a, t);
                if (no != null) return Done(no);
                if (a == "arm")
                {
                    string bad;
                    var keys = JawaBenchCalmProfile.Keys(spec, out bad);
                    if (keys == null) return Done("REFUSED: " + bad);
                    if (!string.IsNullOrEmpty(driver)) keys["driver"] = driver;
                    var p = JawaBenchCalmProfileCore.Parse(keys, out bad);
                    if (p == null) return Done(bad);
                    string err;
                    var map = NorthstarMap(mapId, out err);
                    if (map == null) return Done("REFUSED: " + err);
                    return Done(JawaBenchCalmProfile.Arm(p, map));
                }
                if (!S.Armed) return Done("REFUSED: no calm profile is armed");
                if (a == "renew")
                {
                    double m = minutes > 0 ? minutes : S.P.Minutes;
                    S.L.Arm(JawaBenchTpsWatchdog.Now, m);
                    if (AW.Wild.By == "jawa/calm_profile" && AW.Wild.Active(Current.Game, JawaBenchTpsWatchdog.Now)) AW.Wild.Block(Current.Game, JawaBenchTpsWatchdog.Now, m, "jawa/calm_profile");
                    return Done(null);
                }
                if (a == "except")
                {
                    var g = JawaBenchGates.G.Of(gate ?? "");
                    if (g == null) return Done("REFUSED: gate must be incident, quest or mental");
                    return Done(S.Except(g, name));
                }
                S.Leave("left by " + driver);
                return Done(S.LastNotPutBack.Count == 0 ? null : "left; NOT put back: " + string.Join(" | ", S.LastNotPutBack.ToArray()));
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
