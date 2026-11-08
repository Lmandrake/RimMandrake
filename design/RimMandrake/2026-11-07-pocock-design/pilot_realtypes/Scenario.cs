// Real-types pilot: seed pyre_fire_duty_starves (06-mined-live-bugs.md). The gate that puts "eat when urgently hungry" above
// firefighting must hold for an undrafted player colonist on a Pyrelands map, and for nobody else. Real RimWorld types only:
// each staging step is tried the natural way first, and a step that throws is reported by name with what blocked it.
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization;

namespace PilotRealTypes
{
    public static class Program
    {
        static readonly string[] Probe =
        {
            @"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed",
        };
        static int fails;

        public static int Main(string[] args)
        {
            string own = Path.GetDirectoryName(typeof(Program).Assembly.Location);
            var dirs = new List<string>(Probe);
            if (args.Length > 0) dirs.Add(args[0]);   // the mod's Assemblies dir (FireEcologyHook.dll)
            AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
            {
                string name = new AssemblyName(e.Name).Name + ".dll";
                foreach (string d in dirs)
                {
                    string p = Path.Combine(d, name);
                    if (File.Exists(p)) return Assembly.LoadFrom(p);
                }
                return null;
            };
            try { QuietUnityLog(); Run(); if (Array.IndexOf(args, "--probe-map") >= 0) ProbeRealMap(); }
            catch (Exception e) { Console.WriteLine("ABORT " + Describe(e)); return 3; }
            Console.WriteLine(fails == 0 ? "ALL SCENARIOS HOLD" : fails + " SCENARIO(S) FAILED");
            return fails == 0 ? 0 : 1;
        }

        static string Describe(Exception e)
        {
            while (e is TargetInvocationException || e is TypeInitializationException) { if (e.InnerException == null) break; e = e.InnerException; }
            string[] frames = e.StackTrace == null ? new string[0] : e.StackTrace.Split('\n');
            string top = string.Join(" < ", System.Linq.Enumerable.Take(System.Linq.Enumerable.Select(frames, f => f.Trim().Replace("at ", "")), 6));
            return e.GetType().Name + ": " + e.Message + " | " + top;
        }

        // Try the natural construction; on a throw, say what blocked it and fall back to an uninitialized object.
        static T Make<T>(string step, Func<T> natural) where T : class
        {
            try { T v = natural(); Console.WriteLine("STAGE ok      " + step); return v; }
            catch (Exception e)
            {
                Console.WriteLine("STAGE blocked " + step + " -> " + Describe(e));
                return (T)FormatterServices.GetUninitializedObject(typeof(T));
            }
        }

        static void Set(object o, string field, object v)
        {
            for (Type t = o.GetType(); t != null; t = t.BaseType)
            {
                FieldInfo f = t.GetField(field, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
                if (f != null) { f.SetValue(o, v); return; }
            }
            throw new MissingFieldException(o.GetType().Name, field);
        }

        static object Get(object o, string field)
        {
            for (Type t = o.GetType(); t != null; t = t.BaseType)
            {
                FieldInfo f = t.GetField(field, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
                if (f != null) return f.GetValue(o);
            }
            throw new MissingFieldException(o.GetType().Name, field);
        }

        static void Expect(string scenario, bool want, Func<bool> got)
        {
            try
            {
                bool g = got();
                if (g == want) Console.WriteLine("PASS  " + scenario);
                else { fails++; Console.WriteLine("FAIL  " + scenario + " (got " + g + ")"); }
            }
            catch (Exception e) { fails++; Console.WriteLine("ERROR " + scenario + " -> " + Describe(e)); }
        }

        // Verse.Log ends in UnityEngine.Debug, whose DebugLogHandler is an engine ECall: outside the player it throws
        // SecurityException. The logger's handler is plain managed state, so swap it for one that prints.
        sealed class ConsoleLogHandler : UnityEngine.ILogHandler
        {
            public void LogFormat(UnityEngine.LogType t, UnityEngine.Object c, string format, params object[] args) =>
                Console.WriteLine("LOG   " + t + ": " + (args == null || args.Length == 0 ? format : string.Format(format, args)));
            public void LogException(Exception e, UnityEngine.Object c) => Console.WriteLine("LOG   exception: " + e.Message);
        }

        [MethodImpl(MethodImplOptions.NoInlining)]
        static void QuietUnityLog()
        {
            try { UnityEngine.Debug.unityLogger.logHandler = new ConsoleLogHandler(); Console.WriteLine("STAGE ok      Unity log handler -> console"); }
            catch (Exception e) { Console.WriteLine("STAGE blocked Unity log handler -> " + Describe(e)); }
        }

        // Not a scenario: how far a REAL map gets outside the game. Most seeds (a JobGiver choosing a cell, a pawn stepping off fire)
        // need a spawned pawn on a map with grids; each step reports ok or the first thing that blocks it.
        [MethodImpl(MethodImplOptions.NoInlining)]
        static void ProbeRealMap()
        {
            void Step(string step, Action a)
            {
                try { a(); Console.WriteLine("PROBE ok      " + step); }
                catch (Exception e) { Console.WriteLine("PROBE blocked " + step + " -> " + Describe(e)); }
            }
            var map = new Verse.Map();
            map.info.Size = new Verse.IntVec3(20, 1, 20);
            Step("Map.ConstructComponents() with an empty DefDatabase", () => map.ConstructComponents());
            Step("DefOfHelper.RebindAllDefOfs (empty DefDatabase)", () => RimWorld.DefOfHelper.RebindAllDefOfs(true));
            Step("new TerrainGrid(map)", () => map.terrainGrid = new Verse.TerrainGrid(map));
            Step("new ThingGrid(map)", () => map.thingGrid = new Verse.ThingGrid(map));
            Step("new RegionGrid(map)", () => map.regionGrid = new Verse.RegionGrid(map));
            Step("new PathFinder(map) (Unity NativeArray inside)", () => Activator.CreateInstance(typeof(Verse.Map).Assembly.GetType("Verse.PathFinder"), map));
        }

        [MethodImpl(MethodImplOptions.NoInlining)]
        static void Run()
        {
            // The world the gate reads: Current.Game -> Find.Maps -> Map.Biome (via the tile), Pawn.Faction, RaceProps, drafter.
            Verse.Game game = Make("new Game()", () => new Verse.Game());
            Verse.Current.Game = game;
            if (Get(game, "maps") == null) Set(game, "maps", new List<Verse.Map>());
            var maps = (List<Verse.Map>)Get(game, "maps");

            Verse.Map Map(string biomeDefName)
            {
                RimWorld.BiomeDef biome = Make("new BiomeDef()", () => new RimWorld.BiomeDef());
                biome.defName = biomeDefName;
                RimWorld.Planet.Tile tile = Make("new Tile()", () => new RimWorld.Planet.Tile());
                Set(tile, "biome", biome);
                Verse.Map map = Make("new Map()", () => new Verse.Map());
                if (map.info == null) map.info = Make("new MapInfo()", () => new Verse.MapInfo());
                map.info.isPocketMap = true;          // Map.Biome reads pocketTileInfo, not Find.WorldGrid
                map.pocketTileInfo = tile;
                maps.Add(map);
                return map;
            }

            Verse.ThingDef human = Make("new ThingDef()", () => new Verse.ThingDef());
            human.defName = "Human";
            human.race = Make("new RaceProperties()", () => new Verse.RaceProperties());
            human.race.intelligence = Verse.Intelligence.Humanlike;

            RimWorld.FactionDef playerDef = Make("new FactionDef()", () => new RimWorld.FactionDef());
            playerDef.isPlayer = true;
            RimWorld.Faction player = Make("new Faction()", () => new RimWorld.Faction());
            player.def = playerDef;
            RimWorld.FactionDef pirateDef = Make("new FactionDef()", () => new RimWorld.FactionDef());
            RimWorld.Faction pirates = Make("new Faction()", () => new RimWorld.Faction());
            pirates.def = pirateDef;

            Verse.Pawn Pawn(Verse.Map on, RimWorld.Faction faction, bool drafted)
            {
                Verse.Pawn p = Make("new Pawn()", () => new Verse.Pawn());
                p.def = human;
                Set(p, "factionInt", faction);
                Set(p, "mapIndexOrState", (sbyte)maps.IndexOf(on));
                if (drafted)
                {
                    p.drafter = Make("new Pawn_DraftController(pawn)", () => new RimWorld.Pawn_DraftController(p));
                    Set(p.drafter, "draftedInt", true);
                }
                return p;
            }

            var gate = new RimMandrake.Pyrelands.ThinkNode_ConditionalPyrelandsColonist();
            MethodInfo satisfied = typeof(RimMandrake.Pyrelands.ThinkNode_ConditionalPyrelandsColonist)
                .GetMethod("Satisfied", BindingFlags.Instance | BindingFlags.NonPublic);
            bool Gate(Verse.Pawn p) => (bool)satisfied.Invoke(gate, new object[] { p });

            Verse.Map pyre = Map("RM_Pyrelands");
            Verse.Map desert = Map("AridShrubland");

            // Staging read-backs through the real getters: a scenario that passes on a pawn the game would not see is no scenario.
            Expect("staging: a pawn on the Pyrelands map reads that biome", true, () => Pawn(pyre, player, false).Map?.Biome?.defName == "RM_Pyrelands");
            Expect("staging: a pawn on the other map reads AridShrubland", true, () => Pawn(desert, player, false).Map?.Biome?.defName == "AridShrubland");
            Expect("staging: a player pawn is a colonist", true, () => Pawn(pyre, player, false).IsColonist);
            Expect("staging: a drafted pawn reads Drafted", true, () => Pawn(pyre, player, true).Drafted);
            Expect("staging: the mechanics gate is on by default", true, () => RimMandrake.Pyrelands.PyrelandsMechanicsGate.On);

            Expect("an undrafted colonist on a Pyrelands map eats before fire duty", true, () => Gate(Pawn(pyre, player, false)));
            Expect("a drafted colonist on a Pyrelands map is left to his orders", false, () => Gate(Pawn(pyre, player, true)));
            Expect("an undrafted colonist on another biome keeps vanilla's order", false, () => Gate(Pawn(desert, player, false)));
            Expect("a raider on a Pyrelands map is not a colonist", false, () => Gate(Pawn(pyre, pirates, false)));
            Expect("with Pyrelands switched off in its settings, nobody is gated", false, () =>
            {
                RimMandrake.Pyrelands.RM_PyrelandsSettings.pyrelandsEnabled = false;
                try { return Gate(Pawn(pyre, player, false)); }
                finally { RimMandrake.Pyrelands.RM_PyrelandsSettings.pyrelandsEnabled = true; }
            });
        }
    }
}
