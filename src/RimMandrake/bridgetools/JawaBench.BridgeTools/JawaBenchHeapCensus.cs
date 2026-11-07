// JawaBenchHeapCensus.cs - jawa/heap_census: what does a reload of a save leave behind? (HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE,
// infrastructure/state/facts/heap_reload_ratchet_2026-11-06.md). The TPS record says the floor rises per load; it cannot say what rose.
//
//   action=floor    a forced full collection and the used/reserved sizes after it, plus how many earlier Game and Map objects
//                   are still alive. Every call also starts watching the current Game and Maps through WeakReferences, which
//                   keep nothing alive themselves, so a load that retains its predecessor reads directly.
//   action=census   the floor, then the static collections of every game and mod assembly, largest first. Called after each
//                   load, a field whose count climbs with the load count is a retainer, whichever mod owns it.
//   action=sanity   proves the instruments can see: a held block moves the floor and its release moves it back, an unheld
//                   object's WeakReference dies, the census finds its own private static (GC.GetTotalMemory on Mono has read
//                   48 B for 400 KB allocated: lessons/20261027T202852Z-BENCH-mono-gettotalmemory-blind.md).
//
// Reading a static field runs its type's static constructor if nothing ran it yet, so the first census can initialise lazy
// classes that a game would have reached later. It is a measuring tool for test sessions and nothing in play calls it.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchHeapCensus
    {
        private sealed class Watched { public WeakReference Ref; public string Kind; public int Seq; }

        private const int PeekElements = 16;      // enough to classify a collection, never a walk of a large one
        private const int CanaryBlocks = 64, CanaryBlockBytes = 1 << 20;

        private static readonly List<Watched> Watch = new List<Watched>();
        private static readonly List<object> CanaryRows = NewCanaryRows();  // the census must list this field at count 64
        private static List<byte[]> _heldCanary;    // a static: a local would linger on Boehm's conservatively scanned stack
        private static int _gameSeq, _mapSeq;

        private static List<object> NewCanaryRows()
        {
            var rows = new List<object>(64);
            for (int i = 0; i < 64; i++) rows.Add(new object());
            return rows;
        }

        private static double Mb(long bytes) => Math.Round(bytes / 1048576.0, 1);

        private static long Collect()
        {
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
            return GC.GetTotalMemory(false);
        }

        private static bool Watching(object o)
        {
            foreach (var w in Watch) if (ReferenceEquals(w.Ref.Target, o)) return true;
            return false;
        }

        private static void AddWatches()
        {
            var game = Current.Game;
            if (game == null) return;
            if (!Watching(game)) Watch.Add(new Watched { Ref = new WeakReference(game), Kind = "Game", Seq = ++_gameSeq });
            foreach (var map in game.Maps)
                if (!Watching(map)) Watch.Add(new Watched { Ref = new WeakReference(map), Kind = "Map", Seq = ++_mapSeq });
        }

        internal static object Floor()
        {
            AddWatches();
            var sw = Stopwatch.StartNew();
            long used = Collect();
            var game = Current.Game;
            int oldGames = 0, oldMaps = 0, games = 0, maps = 0;
            var aliveSeqs = new List<string>();
            foreach (var w in Watch)
            {
                bool isGame = w.Kind == "Game";
                if (isGame) games++; else maps++;
                var t = w.Ref.Target;
                if (t == null || ReferenceEquals(t, game) || (t is Map m && game != null && game.Maps.Contains(m))) continue;
                if (isGame) oldGames++; else oldMaps++;
                aliveSeqs.Add(w.Kind + w.Seq);
            }
            return new
            {
                success = true,
                usedMB = Mb(used),
                monoUsedMB = Mb(UnityEngine.Profiling.Profiler.GetMonoUsedSizeLong()),
                reservedMB = Mb(UnityEngine.Profiling.Profiler.GetMonoHeapSizeLong()),
                gc = GC.CollectionCount(0),
                collectMs = sw.ElapsedMilliseconds,
                gamesSeen = games,
                mapsSeen = maps,
                oldGamesAlive = oldGames,
                oldMapsAlive = oldMaps,
                aliveOld = aliveSeqs,
                session = JawaBenchTpsWriter.Session
            };
        }

        private static bool Skipped(Assembly a)
        {
            string n = a.GetName().Name;
            return a.IsDynamic || n == "mscorlib" || n == "netstandard" || n == "System" || n.StartsWith("System.") || n.StartsWith("Mono.")
                || n.StartsWith("Unity.") || n.StartsWith("UnityEngine");
        }

        private static IEnumerable<Type> TypesOf(Assembly a)
        {
            try { return a.GetTypes(); }
            catch (ReflectionTypeLoadException e) { return Array.FindAll(e.Types, t => t != null); }
            catch (Exception) { return new Type[0]; }
        }

        private static bool GameObject(object o) => o is Map || o is Game || o is World || o is Thing;

        /// <summary>A collection's size, or -1 when the value is not a collection. HashSet is no ICollection, so Count is looked up.</summary>
        private static int SizeOf(object v, Dictionary<Type, PropertyInfo> counts)
        {
            if (v is Array arr) return arr.Length;
            if (v is ICollection c) return c.Count;
            var t = v.GetType();
            if (!t.IsGenericType) return -1;
            if (!counts.TryGetValue(t, out var p))
            {
                p = t.GetProperty("Count", BindingFlags.Public | BindingFlags.Instance);
                if (p != null && p.PropertyType != typeof(int)) p = null;
                counts[t] = p;
            }
            return p == null ? -1 : (int)p.GetValue(v, null);
        }

        /// <summary>How many of the first few elements are game objects: a static list of Things is the leak's shape.</summary>
        private static int PeekGameObjects(object v)
        {
            int seen = 0, hits = 0;
            IEnumerable e = v is IDictionary d ? d.Keys : v as IEnumerable;
            if (e == null) return 0;
            foreach (var o in e)
            {
                if (GameObject(o)) hits++;
                if (++seen >= PeekElements) break;
            }
            if (hits == 0 && v is IDictionary d2)
            {
                seen = 0;
                foreach (var o in d2.Values)
                {
                    if (GameObject(o)) hits++;
                    if (++seen >= PeekElements) break;
                }
            }
            return hits;
        }

        internal static object Census(int top)
        {
            var sw = Stopwatch.StartNew();
            var counts = new Dictionary<Type, PropertyInfo>();
            var rows = new List<KeyValuePair<int, object>>();
            var holders = new List<object>();
            var game = Current.Game;
            int fields = 0, collections = 0, errors = 0, assemblies = 0, canarySeen = -1;
            string canaryName = typeof(JawaBenchHeapCensus).FullName + "." + nameof(CanaryRows);
            long elements = 0;
            foreach (var a in AppDomain.CurrentDomain.GetAssemblies())
            {
                if (Skipped(a)) continue;
                assemblies++;
                foreach (var t in TypesOf(a))
                {
                    if (t.IsEnum || t.IsInterface || t.ContainsGenericParameters) continue;
                    FieldInfo[] fs;
                    try { fs = t.GetFields(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly); }
                    catch (Exception) { errors++; continue; }
                    foreach (var f in fs)
                    {
                        var ft = f.FieldType;
                        if (f.IsLiteral || ft.IsPrimitive || ft.IsEnum || ft.IsPointer || ft == typeof(string)) continue;
                        if (f.IsDefined(typeof(ThreadStaticAttribute), false)) continue;
                        fields++;
                        try
                        {
                            object v = f.GetValue(null);
                            if (v == null) continue;
                            string name = t.FullName + "." + f.Name;
                            if ((v is Map vm && (game == null || !game.Maps.Contains(vm))) || (v is Game vg && !ReferenceEquals(vg, game)))
                                holders.Add(new { asm = a.GetName().Name, field = name, kind = v.GetType().Name });
                            int n = SizeOf(v, counts);
                            if (n < 0) continue;
                            collections++;
                            if (name == canaryName) canarySeen = n;
                            elements += n;
                            rows.Add(new KeyValuePair<int, object>(n, new { asm = a.GetName().Name, field = name, n, gameObj = n > 0 ? PeekGameObjects(v) : 0 }));
                        }
                        catch (Exception) { errors++; }
                    }
                }
            }
            rows.Sort((x, y) => y.Key.CompareTo(x.Key));
            var keep = new List<object>();
            for (int i = 0; i < rows.Count && i < top; i++) keep.Add(rows[i].Value);
            return new
            {
                success = true,
                floor = Floor(),
                assemblies,
                staticFields = fields,
                collections,
                elements,
                readErrors = errors,
                truncated = rows.Count > top,
                canaryField = canaryName,
                canarySeen,
                staleHolders = holders,
                rows = keep,
                censusMs = sw.ElapsedMilliseconds
            };
        }

        private static List<WeakReference> UnheldObjects(int n)
        {
            var refs = new List<WeakReference>(n);
            for (int i = 0; i < n; i++) refs.Add(new WeakReference(new byte[1024]));
            return refs;
        }

        internal static object Sanity()
        {
            long before = Collect();
            _heldCanary = new List<byte[]>(CanaryBlocks);
            for (int i = 0; i < CanaryBlocks; i++)
            {
                var block = new byte[CanaryBlockBytes];
                for (int j = 0; j < block.Length; j += 4096) block[j] = 1;
                _heldCanary.Add(block);
            }
            long whileHeld = Collect();
            int heldCount = _heldCanary.Count;
            _heldCanary = null;
            long after = Collect();
            var unheld = UnheldObjects(1000);
            Collect();
            int stillAlive = 0;
            foreach (var w in unheld) if (w.IsAlive) stillAlive++;
            return new
            {
                success = true,
                heldBlocks = heldCount,
                heldMB = Mb(whileHeld - before),
                releasedMB = Mb(whileHeld - after),
                unheldAliveOf1000 = stillAlive
            };
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/heap_census",
            Description =
                "What a reload of a save leaves behind, for the reload ratchet (heap_reload_ratchet_2026-11-06.md). action=floor: a forced " +
                "full GC, the used and reserved MB after it, and how many earlier Game and Map objects are still alive (WeakReferences, " +
                "started by the first call on each). action=census: the floor plus every static collection of the game and mod assemblies, " +
                "largest first, with stale Map or Game holders. action=sanity: proves the floor and the census can see. Freezes the main " +
                "thread for the collection, seconds on a large list; a measuring tool, never for play.",
            ResultDescription = "success; floor: usedMB, reservedMB, gc, oldGamesAlive, oldMapsAlive, session; census: floor, rows [asm, field, n, gameObj], staleHolders, truncated, canarySeen; sanity: heldMB, releasedMB, unheldAliveOf1000.")]
        public static async Task<object> HeapCensus(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "floor | census | sanity", DefaultValue = "floor")] string action = "floor",
            [ToolParameter(Description = "census: how many of the largest collections to return", DefaultValue = 800)] int top = 800)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var a = (action ?? "floor").Trim().ToLowerInvariant();
                if (a == "floor") return JawaBenchHeapCensus.Floor();
                if (a == "census") return JawaBenchHeapCensus.Census(top < 1 ? 800 : top);
                if (a == "sanity") return JawaBenchHeapCensus.Sanity();
                return Fail("action must be floor, census or sanity");
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
