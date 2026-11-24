// Run the production calm actions against a paused map and a controllable wall clock.
// The stand-ins below implement only the engine and SDK surface these actions use.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using AW = JawaBench.BridgeTools.JawaBenchAwareness;
using Clock = JawaBench.BridgeTools.JawaBenchTpsWatchdog;
using Tools = JawaBench.BridgeTools.JawaBenchTerrainTools;

namespace JawaBench.BridgeTools
{
    internal static class CalmLifecycleUnits
    {
        private static readonly IRimBridgeContext Context = new IRimBridgeContext();

        internal static void Run()
        {
            Program.Check("paused_expiry.restores_without_a_tick", () =>
            {
                var map = SetUp();
                Require(Act("calm", 0.05).success, "three-second calm failed to arm");
                Require(!DebugSettings.enableStoryteller && map.weatherDecider.ForcedWeather?.defName == "Clear",
                        "fixture never held the storyteller and Clear");
                int tick = Find.TickManager.TicksGame;
                Clock.Now += 5;
                new Root_Play().Update();
                bool storyteller = DebugSettings.enableStoryteller;
                var forced = map.weatherDecider.ForcedWeather;
                var read = Act("read");
                Require(read.secondsLeft == 0 && read.lastRelease == "expired", "lease did not report expiry");
                Require(Find.TickManager.TicksGame == tick, "the paused tick advanced");
                Require(storyteller && forced == null,
                        $"expired at tick {tick}, storyteller={storyteller}, forced={forced?.defName ?? "none"}");
                return true;
            });

            Program.Check("letter_restore.restores_only_letters_calm_suppressed", () =>
            {
                var map = SetUp();
                var unsent = AddLetter(map, false);
                var sent = AddLetter(map, true);
                Require(Act("calm").success && unsent.letterSent, "calm did not suppress the unsent letter");
                Require(Act("release").success, "release failed");
                Require(!unsent.letterSent && sent.letterSent,
                        $"release succeeded, originally unsent={unsent.letterSent}, originally sent={sent.letterSent}");
                return true;
            });

            Program.Check("arm_tick_follows_game.hides_previous_games_tick", () =>
            {
                SetUp();
                var calm = Act("calm");
                Require(calm.success && calm.armTick == 123, "calm did not report the armed tick");
                Current.Game = new object();
                Find.CurrentMap = new Map();   // the new game reuses the old map id
                Find.TickManager.TicksGame = 12;
                var read = Act("read");
                Require(read.armTick == -1, $"new game reported armTick={read.armTick}, expected -1");
                var rearmed = Act("reassert");
                Require(rearmed.success && rearmed.armTick == 12, "reassert did not report the new arm tick");
                return true;
            });

            Program.Check("reassert_lease.preserves_deadline_and_allows_explicit_renewal", () =>
            {
                SetUp();
                var calm = Act("calm", 60);
                Require(calm.success && calm.secondsLeft == 3600, "60-minute calm failed to arm");
                Clock.Now += 10;
                DebugSettings.enableStoryteller = true;
                var repaired = Act("reassert");
                Require(repaired.success && !DebugSettings.enableStoryteller &&
                        ((List<string>)repaired.repaired).Any(s => s.StartsWith("storyteller:", StringComparison.Ordinal)),
                        "reassert did not report the storyteller repair");
                Require(repaired.secondsLeft == 3590 && AW.Wild.UntilS - Clock.Now == 3590,
                        $"after repair calm={repaired.secondsLeft}s, wild={AW.Wild.UntilS - Clock.Now}s, expected 3590s");
                var renewed = Act("reassert", 30);
                Require(renewed.success && renewed.secondsLeft == 1800 && AW.Wild.UntilS - Clock.Now == 1800,
                        "explicit 30-minute renewal did not set both leases");
                Act("release");
                Require(Act("reassert").secondsLeft == 3600, "rearming did not use the last calm's 60 minutes");
                return true;
            });

            Program.Check("reassert_lease.preserves_an_independent_spawner_deadline", () =>
            {
                SetUp();
                Require(Act("calm", 60).success, "60-minute calm failed to arm");
                Clock.Now += 10;
                AW.Wild.Block(Current.Game, Clock.Now, 120, "jawa/wild_spawner_block");
                Clock.Now += 10;
                DebugSettings.enableStoryteller = true;
                var repaired = Act("reassert");
                Require(repaired.success && !DebugSettings.enableStoryteller, "reassert did not repair the storyteller");
                Require(repaired.secondsLeft == 3580 && AW.Wild.UntilS == 7310,
                        $"after repair calm={repaired.secondsLeft}s, wild deadline={AW.Wild.UntilS}s, expected 3580s and 7310s");
                AW.Wild.Release("released");
                var reblocked = Act("reassert");
                Require(reblocked.success && reblocked.secondsLeft == 3580 && AW.Wild.UntilS == 3700,
                        "reassert did not restore the missing spawner block for the remaining calm time");
                return true;
            });
        }

        private static dynamic Act(string action, double? minutes = null) => minutes.HasValue
            ? Tools.QuietSite(Context, CancellationToken.None, action: action, minutes: minutes.Value).GetAwaiter().GetResult()
            : Tools.QuietSite(Context, CancellationToken.None, action: action).GetAwaiter().GetResult();

        private static void Require(bool ok, string why)
        {
            if (!ok) throw new InvalidOperationException(why);
        }

        private static Map SetUp()
        {
            Act("release");
            Clock.Now = 100;
            Current.Game = new object();
            Find.CurrentMap = new Map();
            Find.TickManager.TicksGame = 123;
            DebugSettings.enableStoryteller = true;
            return Find.CurrentMap;
        }

        private static CompProximityLetter AddLetter(Map map, bool sent)
        {
            var thing = new ThingWithComps { Map = map };
            thing.Letter = new CompProximityLetter { parent = thing, letterSent = sent };
            map.listerThings.AllThings.Add(thing);
            return thing.Letter;
        }
    }

    internal static class JawaBenchTpsWatchdog { internal static double Now; }

    internal static class JawaBenchCompanionSafety
    {
        internal static readonly JawaBenchSafetyCore.Policy CurrentPolicy = JawaBenchSafetyCore.TestPolicy;
    }

    internal static class JawaBenchAwareness
    {
        internal static readonly JawaBenchSafetyCore.QuietBlock Wild = new JawaBenchSafetyCore.QuietBlock();
        internal static long WildSkipped => 0;
        internal static string EnsureWildPatch() => null;
        internal static bool WildHolds(out string why) { why = "spawner lease is off"; return Wild.Active(Current.Game, Clock.Now); }
    }

    internal static class JawaBenchVitals
    {
        internal static bool IsThreatStructure(Building b, Faction player, out bool turret, out bool spawner, out bool asleep, out bool causer)
        { turret = spawner = asleep = causer = false; return false; }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        private static object Fail(string message, object suggestions = null) => new { success = false, message };
        private static object DefSuggestions<T>(string name) => null;
        private static int TicksGameSafe() => Find.TickManager.TicksGame;
        private static Map NorthstarMap(int mapId, out string err) { err = null; return Find.CurrentMap; }
    }
}

namespace RimBridgeServer.Sdk
{
    public sealed class ToolAttribute : Attribute
    {
        public ToolAttribute(string name) { }
        public string Description { get; set; }
        public string ResultDescription { get; set; }
    }

    public sealed class ToolParameterAttribute : Attribute
    {
        public string Description { get; set; }
        public object DefaultValue { get; set; }
    }

    public sealed class IRimBridgeContext
    {
        public IRimBridgeContext MainThread => this;
        public Task<T> InvokeAsync<T>(Func<T> action, CancellationToken token) => Task.FromResult(action());
    }
}

namespace HarmonyLib
{
    internal static class Priority { internal const int First = 800, Normal = 400; }

    internal sealed class HarmonyMethod
    {
        internal HarmonyMethod(MethodInfo method) { this.method = method; }
        internal readonly MethodInfo method;
        internal int priority;
        internal string owner;
    }

    internal static class AccessTools
    {
        internal static MethodInfo Method(Type type, string name, Type[] args) => type.GetMethod(name, args);
        internal static MethodInfo DeclaredMethod(Type type, string name, Type[] args) => Method(type, name, args);
    }

    internal sealed class Harmony
    {
        internal sealed class Patches
        {
            internal readonly List<HarmonyMethod> Prefixes = new List<HarmonyMethod>(), Postfixes = new List<HarmonyMethod>();
        }

        private static readonly Dictionary<MethodBase, Patches> Hooks = new Dictionary<MethodBase, Patches>();
        private readonly string _owner;

        internal Harmony(string owner) { _owner = owner; }
        internal static Patches GetPatchInfo(MethodBase target) => Hooks.TryGetValue(target, out var patches) ? patches : null;

        internal void Patch(MethodBase target, HarmonyMethod prefix = null, HarmonyMethod postfix = null)
        {
            var patches = GetPatchInfo(target) ?? (Hooks[target] = new Patches());
            if (prefix != null) { prefix.owner = _owner; patches.Prefixes.Add(prefix); }
            if (postfix != null) { postfix.owner = _owner; patches.Postfixes.Add(postfix); }
        }
    }
}

namespace Verse
{
    internal static class Current { internal static object Game; }
    internal static class UnityData { internal static bool IsInMainThread => true; }
    internal static class DebugSettings
    {
        internal static bool enableStoryteller = true, enableRandomMentalStates = true, enableRandomDiseases = true;
    }

    internal static class Find
    {
        internal static Map CurrentMap;
        internal static readonly TickManager TickManager = new TickManager();
        internal static readonly Storyteller Storyteller = new Storyteller();
        internal static readonly WindowStack WindowStack = new WindowStack();
        internal static List<Map> Maps => new List<Map> { CurrentMap };
    }

    internal sealed class Root_Play
    {
        public void Update()
        {
            // A paused frame only runs registered frame hooks.
            var patches = Harmony.GetPatchInfo(typeof(Root_Play).GetMethod(nameof(Update)));
            if (patches == null) return;
            foreach (var patch in patches.Prefixes.Concat(patches.Postfixes))
                patch.method.Invoke(null, Array.Empty<object>());
        }
    }

    internal sealed class TickManager { internal int TicksGame; }
    internal sealed class Window { internal bool forcePause => false; }
    internal sealed class WindowStack { internal readonly List<Window> Windows = new List<Window>(); }

    internal enum DestroyMode { Vanish }
    internal sealed class Def { internal string defName => "fixture"; internal bool destroyable => true; }
    internal sealed class Pos { internal int x => 0; internal int z => 0; }
    internal class Thing
    {
        internal string ThingID => "fixture";
        internal Def def = new Def();
        internal Pos Position = new Pos();
        internal Map Map;
        internal bool Spawned => Map != null;
        internal void Destroy(DestroyMode mode) => DeSpawn(mode);
        internal void DeSpawn(DestroyMode mode) { Map?.listerThings.AllThings.Remove(this); Map = null; }
    }

    internal class ThingWithComps : Thing
    {
        internal CompProximityLetter Letter;
        internal T GetComp<T>() where T : class => Letter as T;
    }

    internal sealed class Building : ThingWithComps { internal Faction Faction => null; }
    internal sealed class Pawn : ThingWithComps
    {
        internal bool Dead => false;
        internal Faction Faction => null;
        internal bool HostileTo(Faction f) => false;
        internal bool IsPrisonerOfColony => false;
        internal Def kindDef => def;
        internal RaceProperties RaceProps => null;
        internal int thingIDNumber => 0;
        internal bool InMentalState => false;
        internal Def MentalStateDef => null;
        public void SpawnSetup(Map map, bool respawningAfterLoad) { }
    }

    internal sealed class RaceProperties { internal bool Animal => false; internal bool predator => false; }
    internal sealed class MapPawns { internal readonly List<Pawn> AllPawnsSpawned = new List<Pawn>(); }
    internal sealed class ListerBuildings { internal readonly List<Building> allBuildingsNonColonist = new List<Building>(); }
    internal sealed class ListerThings
    {
        internal readonly List<Thing> AllThings = new List<Thing>();
        internal List<Thing> ThingsOfDef(Def def) => AllThings.Where(t => t.def == def).ToList();
    }
    internal static class ThingDefOf { internal static readonly Def Fire = new Def(); }

    internal sealed class Map
    {
        internal int uniqueID => 1;
        internal readonly MapPawns mapPawns = new MapPawns();
        internal readonly ListerBuildings listerBuildings = new ListerBuildings();
        internal readonly ListerThings listerThings = new ListerThings();
        internal readonly WeatherManager weatherManager = new WeatherManager();
        internal readonly GameConditionManager gameConditionManager;
        internal readonly WeatherDecider weatherDecider;
        internal Map() { gameConditionManager = new GameConditionManager(this); weatherDecider = new WeatherDecider(gameConditionManager); }
    }

    internal static class DefDatabase<T> where T : class
    {
        internal static List<T> AllDefsListForReading => new List<T>();
        internal static T GetNamedSilentFail(string name) => name == "Clear" ? WeatherDef.Clear as T
            : name == "WeatherController" ? new GameConditionDef() as T : null;
    }
}

namespace RimWorld
{
    internal sealed class Faction
    {
        internal static readonly Faction OfPlayer = new Faction();
        internal Def def => null;
        internal string Name => "player";
    }
    internal sealed class CompProximityLetter
    {
        internal bool letterSent;
        internal ThingWithComps parent;
        internal LetterProps Props => null;
    }
    internal sealed class LetterProps { internal string letterLabel => null; }
    internal sealed class IncidentDef { internal string defName; }
    internal sealed class IncidentParms { internal object target; internal Quest quest => null; }
    internal sealed class Quest { internal int id => 0; }
    internal abstract class IncidentWorker
    {
        internal IncidentDef def;

        public bool TryExecute(IncidentParms parms)
        {
            var args = new object[] { this, parms, false };
            var patches = Harmony.GetPatchInfo(typeof(IncidentWorker).GetMethod(nameof(TryExecute)));
            if (patches != null && patches.Prefixes.Any(p => !(bool)p.method.Invoke(null, args))) return (bool)args[2];
            return TryExecuteWorker(parms);
        }
        protected abstract bool TryExecuteWorker(IncidentParms parms);
    }
    internal sealed class IncidentQueue : List<QueuedIncident>
    {
        public void IncidentQueueTick()
        {
            var patches = Harmony.GetPatchInfo(typeof(IncidentQueue).GetMethod(nameof(IncidentQueueTick)));
            if (patches != null) foreach (var patch in patches.Prefixes)
                if (!(bool)patch.method.Invoke(null, Array.Empty<object>())) return;
        }
    }
    internal sealed class QueuedIncident { internal FiringIncident FiringIncident => null; internal int FireTick => 0; }
    internal sealed class FiringIncident { internal IncidentDef def => null; }
    internal sealed class Storyteller { internal readonly IncidentQueue incidentQueue = new IncidentQueue(); }

    internal sealed class WeatherDef
    {
        internal static readonly WeatherDef Clear = new WeatherDef("Clear");
        internal readonly string defName;
        internal WeatherDef(string name) { defName = name; }
        internal float rainRate => 0;
        internal float snowRate => 0;
    }
    internal sealed class WeatherManager
    {
        internal WeatherDef curWeather = new WeatherDef("Rain"), lastWeather;
        internal float RainRate => curWeather.rainRate;
        internal float SnowRate => curWeather.snowRate;
        internal void TransitionTo(WeatherDef weather) { lastWeather = curWeather; curWeather = weather; }
    }
    internal sealed class WeatherDecider
    {
        private readonly GameConditionManager _manager;
        internal WeatherDecider(GameConditionManager manager) { _manager = manager; }
        internal WeatherDef ForcedWeather => _manager.ActiveConditions.Select(c => c.ForcedWeather()).LastOrDefault();
    }
    internal sealed class GameConditionDef { internal string defName => "WeatherController"; }
    internal class GameCondition
    {
        internal GameConditionDef def;
        internal GameConditionManager gameConditionManager;
        internal bool suppressEndMessage;
        internal virtual WeatherDef ForcedWeather() => null;
        internal void End() => gameConditionManager.ActiveConditions.Remove(this);
    }
    internal sealed class GameCondition_ForceWeather : GameCondition
    {
        internal WeatherDef weather;
        internal override WeatherDef ForcedWeather() => weather;
    }
    internal static class GameConditionMaker
    {
        internal static GameCondition MakeConditionPermanent(GameConditionDef def) => new GameCondition_ForceWeather { def = def };
    }
    internal sealed class GameConditionManager
    {
        internal readonly Map ownerMap;
        internal readonly List<GameCondition> ActiveConditions = new List<GameCondition>();
        internal GameConditionManager(Map map) { ownerMap = map; }
        internal void RegisterCondition(GameCondition c) { c.gameConditionManager = this; ActiveConditions.Add(c); }
        internal void GetAllGameConditionsAffectingMap(Map map, List<GameCondition> all) => all.AddRange(ActiveConditions);
    }
}
