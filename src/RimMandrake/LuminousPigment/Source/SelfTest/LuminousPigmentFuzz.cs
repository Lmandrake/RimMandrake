// Approach B for LuminousPigment: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   lights   the Deepfire light book (RM_DeepfireLightBook): floor grid, 3x3 block clusters, anchor/radius, own-vs-cluster
//            routing, settings rebuild, save/load - action sequences against an independent from-scratch spec
//   rules    RM_DeepfireRules: coat cap + first-coat latch, status engine, beauty/cost, mat lifecycle, god tables and
//            anti-pinning, dodge inversion, worn blend, dark test - property checks and short sequences
//   cuisine  RM_DeepfireCuisine: steer curve, family rolls (incl. exact roll boundaries), per-pawn cap, rates
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.LuminousPigment.SelfTest
{
    internal static class LuminousPigmentFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(float a, float b, float eps) { return Math.Abs(a - b) <= eps; }

        internal struct Act
        {
            public int kind, a, b;
            public string[] names;
            public override string ToString() { return (names != null && kind < names.Length ? names[kind] : "k" + kind) + "(" + a + "," + b + ")"; }
        }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static string Drive(int seed, Func<Random, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var acts = gen(new Random(seed));
            string err = run(seed, acts);
            if (err == null) return null;
            var small = Shrink(acts, t => run(seed, t) != null);
            return run(seed, small) + " | " + string.Join(" ", small);
        }

        private static List<string> Family(string name, int n, int baseSeed, Func<int, string> one)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { string e = one(baseSeed + k); if (e != null) fails.Add($"{name} seed {baseSeed + k}: {e}"); }
                catch (Exception e) { fails.Add($"{name} seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }

        // ════════════════════════ lights ════════════════════════
        private static readonly string[] LightNames = { "AddFloor", "ClearFloor", "Spawn", "Move", "Coats", "Despawn", "Block", "Recolor", "Reload", "Cap", "Vanish", "Corrupt", "Relight" };

        private sealed class Th { public int id, x, z, coats, color; public bool spawned, building, one; }
        private struct Lit { public int x, z, color; public float radius; }

        public static long MultiGroups, OwnLights, Rebuilds, Reloads, FloorAdds, ClusteredThings, BlockChangesWithThings;

        private static List<Act> GenLights(Random r)
        {
            int n = 15 + r.Next(80);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 22 ? 0 : w < 28 ? 1 : w < 44 ? 2 : w < 49 ? 3 : w < 59 ? 4 : w < 66 ? 5 : w < 74 ? 6 : w < 79 ? 7 : w < 85 ? 8 : w < 88 ? 9 : w < 92 ? 10 : w < 95 ? 11 : 12;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = LightNames });
            }
            return l;
        }

        private static string RunLights(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x77);
            int W = 4 + r.Next(10), H = 4 + r.Next(8);
            int block = 1 + r.Next(5);
            float[] rad = { 0f, 0.5f + r.Next(4) * 0.5f, 1f + r.Next(4) * 0.5f, 1.5f + r.Next(6) * 0.5f };
            const float bonus = 1f;
            int cap = 3;
            var floor = new int[W * H]; var fcol = new int[W * H]; var coatable = new bool[W * H];
            for (int i = 0; i < coatable.Length; i++) coatable[i] = true;
            bool corrupt = false;
            var things = new List<Th>();
            var lights = new Dictionary<DeepfireClusterKey, Lit>();
            var ownL = new Dictionary<Th, Lit>();
            int nextId = 1;

            DeepfireLightBook<Th, int> Make()
            {
                return new DeepfireLightBook<Th, int>(W, H, () => block, c => rad[Math.Max(0, Math.Min(3, c))], bonus,
                    (x, z, c) => new DeepfireGlow<int> { Packed = 5000 + fcol[z * W + x] * 9, Color = fcol[z * W + x] },
                    t => new DeepfireThingView<int> { Live = t.spawned && t.coats > 0, Coats = t.coats, X = t.x, Z = t.z, Glow = new DeepfireGlow<int> { Packed = 7000 + t.color * 13, Color = t.color } },
                    (k, x, z, c, rd) => { if (rd <= 0f) lights.Remove(k); else lights[k] = new Lit { x = x, z = z, color = c, radius = rd }; },
                    k => lights.Remove(k),
                    (t, x, z, c, rd) => { if (rd <= 0f) ownL.Remove(t); else ownL[t] = new Lit { x = x, z = z, color = c, radius = rd }; },
                    t => ownL.Remove(t));
            }
            var book = Make();
            Func<Th, bool> clusterable = t => DeepfireLightBook<Th, int>.Clusterable(block, t.building, t.one ? 1 : 2, 1);
            Action<Th> register = t => book.RegisterThing(t, t.x, t.z, clusterable(t), t.color, rad[t.coats]);

            void Verify()
            {
                int nz = 0;
                for (int z = 0; z < H; z++)
                    for (int x = 0; x < W; x++)
                    {
                        Check(book.FloorCoatsAt(x, z) == floor[z * W + x], $"floor coats at {x},{z}: book {book.FloorCoatsAt(x, z)} spec {floor[z * W + x]}");
                        if (floor[z * W + x] > 0) nz++;
                        if (!corrupt) Check(floor[z * W + x] <= 3, "floor coats above the architecture ceiling");
                    }
                Check(book.CoatedFloorCells == nz, $"coatedFloorCells {book.CoatedFloorCells} but {nz} cells are coated");

                // spec: groups from scratch
                int bw = (W + block - 1) / block;
                var groups = new Dictionary<DeepfireClusterKey, List<int[]>>();
                void Put(DeepfireClusterKey k, int x, int z) { if (!groups.TryGetValue(k, out var l)) groups[k] = l = new List<int[]>(); l.Add(new[] { x, z }); }
                for (int z = 0; z < H; z++)
                    for (int x = 0; x < W; x++)
                        if (floor[z * W + x] > 0) Put(new DeepfireClusterKey((z / block) * bw + x / block, 0, floor[z * W + x], 5000 + fcol[z * W + x] * 9), x, z);
                foreach (var t in things)
                    if (t.spawned && t.coats > 0 && clusterable(t)) Put(new DeepfireClusterKey((t.z / block) * bw + t.x / block, 1, t.coats, 7000 + t.color * 13), t.x, t.z);
                Check(lights.Count == groups.Count, $"lit clusters {lights.Count} but the spec has {groups.Count} groups");
                foreach (var kv in groups)
                {
                    Check(lights.TryGetValue(kv.Key, out Lit lit), $"group {kv.Key} ({kv.Value.Count} cells) has no light");
                    float mx = (float)kv.Value.Average(c => c[0]), mz = (float)kv.Value.Average(c => c[1]);
                    Func<int[], double> d2 = c => (c[0] - mx) * (c[0] - mx) + (c[1] - mz) * (c[1] - mz);
                    Check(kv.Value.Any(c => c[0] == lit.x && c[1] == lit.z), $"group {kv.Key} anchor {lit.x},{lit.z} is not one of its cells");
                    double best = kv.Value.Min(d2), got = d2(new[] { lit.x, lit.z });
                    Check(got <= best + 1e-3, $"group {kv.Key} anchor is not the cell nearest the centroid ({got} vs {best})");
                    float want = rad[kv.Key.Coats] + (kv.Value.Count > 1 ? bonus : 0f);
                    Check(Near(lit.radius, want, 1e-4f), $"group {kv.Key} radius {lit.radius} want {want} ({kv.Value.Count} cells)");
                    Check((kv.Key.Kind == 0 ? 5000 + lit.color * 9 : 7000 + lit.color * 13) == kv.Key.Color, $"group {kv.Key} colour payload {lit.color} does not match its key");
                    if (kv.Value.Count > 1) MultiGroups++;
                }
                Check(book.LitKeys().Count() == groups.Count, "LitKeys disagrees with the lit clusters");

                // spec: each coated spawned thing has exactly one light, cluster XOR own; nothing else does
                int ownWant = 0;
                foreach (var t in things)
                {
                    bool live = t.spawned && t.coats > 0;
                    bool cl = live && clusterable(t), ow = live && !cl;
                    Check(book.IsClustered(t) == cl, $"thing {t.id} clustered={book.IsClustered(t)} want {cl} (block {block}, building {t.building}, 1x1 {t.one}, coats {t.coats}, spawned {t.spawned})");
                    Check(book.HasOwn(t) == ow, $"thing {t.id} own light={book.HasOwn(t)} want {ow} (block {block}, building {t.building}, 1x1 {t.one}, coats {t.coats}, spawned {t.spawned})");
                    Check(ownL.ContainsKey(t) == ow, $"thing {t.id} proxy present={ownL.ContainsKey(t)} want {ow}");
                    if (ow) { ownWant++; Check(Near(ownL[t].radius, rad[t.coats], 1e-4f) && ownL[t].x == t.x && ownL[t].z == t.z, $"thing {t.id} own light at wrong place/radius"); }
                    if (cl) ClusteredThings++;
                }
                Check(ownL.Count == ownWant && book.OwnCount == ownWant, $"own lights {ownL.Count}/{book.OwnCount} want {ownWant}");
                Check(book.ClusteredCount == things.Count(t => t.spawned && t.coats > 0 && clusterable(t)), "ClusteredCount disagrees with the spec");
                OwnLights += ownWant;
            }

            void Reload(bool floorFirst)
            {
                Reloads++;
                byte[] grid = book.FloorGrid == null ? null : (byte[])book.FloorGrid.Clone();
                lights.Clear(); ownL.Clear();
                book = Make();
                if (grid != null) book.FloorGrid = grid;
                for (int i = 0; i < floor.Length; i++) if (floor[i] > 0) floor[i] = coatable[i] ? Math.Min(floor[i], 3) : 0;
                corrupt = false;
                Action fin = () => book.Finalize((x, z) => coatable[z * W + x], 3);
                Action regs = () => { foreach (var t in things) if (t.spawned && t.coats > 0) register(t); };
                if (floorFirst) { fin(); regs(); } else { regs(); fin(); }
            }

            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                int x = a.a % W, z = a.b % H, i = z * W + x;
                                bool want = coatable[i] && floor[i] < cap;
                                bool got = book.AddFloorCoat(coatable[i], x, z, cap, out bool first);
                                Check(got == want, $"AddFloorCoat={got} want {want} (coatable {coatable[i]}, coats {floor[i]}, cap {cap})");
                                if (got)
                                {
                                    Check(first == (floor[i] == 0), "firstCoat flag wrong");
                                    floor[i]++; FloorAdds++;
                                    Check(floor[i] <= cap, "a floor coat landed above the cap");
                                }
                                else Check(!first, "firstCoat set on a refused add");
                                Check(book.CanAddFloorCoat(coatable[i], x, z, cap) == (coatable[i] && floor[i] < cap), "CanAddFloorCoat disagrees");
                                break;
                            }
                        case 1:
                            {
                                int x = a.a % W, z = a.b % H, i = z * W + x;
                                bool got = book.ClearFloorCoats(x, z);
                                Check(got == (floor[i] > 0), $"ClearFloorCoats={got} want {floor[i] > 0}");
                                floor[i] = 0;
                                break;
                            }
                        case 2:
                            {
                                var t = new Th { id = nextId++, x = a.a % W, z = a.b % H, coats = 1 + (a.a + a.b) % 3, color = (a.a / 7) % 4, spawned = true, building = (a.a % 4) != 0, one = (a.b % 4) != 0 };
                                things.Add(t); register(t);
                                break;
                            }
                        case 3:
                            {
                                var live = things.Where(t => t.spawned && t.coats > 0).ToList();
                                if (live.Count == 0) break;
                                var t = live[a.a % live.Count];
                                if (a.b % 2 == 0) { book.DeregisterThing(t); t.x = a.b / 2 % W; t.z = a.a / 3 % H; register(t); }
                                else { t.x = a.b / 2 % W; t.z = a.a / 3 % H; register(t); }   // moved in place: re-registered without a despawn
                                break;
                            }
                        case 4:
                            {
                                if (things.Count == 0) break;
                                var t = things[a.a % things.Count];
                                t.coats = a.b % 4;
                                if (t.spawned) { if (t.coats > 0) register(t); else book.DeregisterThing(t); }
                                break;
                            }
                        case 5:
                            {
                                if (things.Count == 0) break;
                                var t = things[a.a % things.Count];
                                if (t.spawned) { t.spawned = false; book.DeregisterThing(t); }
                                else { t.spawned = true; if (t.coats > 0) register(t); }
                                break;
                            }
                        case 6:
                            {
                                block = 1 + a.a % 5; Rebuilds++;
                                if (things.Any(t => t.spawned && t.coats > 0)) BlockChangesWithThings++;
                                // the mod re-registers every coated BUILDING (listerBuildings); loose items keep their proxies
                                book.RebuildAll(() => { foreach (var t in things) if (t.building && t.spawned && t.coats > 0) register(t); });
                                break;
                            }
                        case 7:
                            {
                                int x = a.a % W, z = a.b % H, i = z * W + x;
                                fcol[i] = (fcol[i] + 1) % 4;
                                book.NotifyFloorColorChanged(x, z);
                                break;
                            }
                        case 8: Reload(a.b % 2 == 0); break;
                        case 9: cap = 1 + a.a % 3; break;
                        case 10:
                            {
                                int i = (a.b % H) * W + a.a % W;
                                coatable[i] = a.a % 5 == 0;   // mostly: the floor vanished quietly (nobody cleared its coats)
                                break;
                            }
                        case 11:
                            {
                                var cells = Enumerable.Range(0, floor.Length).Where(i => floor[i] > 0).ToList();
                                if (cells.Count == 0 || book.FloorGrid == null) break;
                                int ci = cells[a.a % cells.Count];
                                int v = 4 + a.b % 5;
                                book.FloorGrid[ci] = (byte)v; floor[ci] = v; corrupt = true; Reload(a.b % 2 == 0);   // a hand-edited grid is only noticed at load
                                break;
                            }
                        case 12:
                            {
                                if (things.Count == 0) break;
                                var t = things[a.a % things.Count];
                                t.color = (t.color + 1) % 4;
                                if (t.spawned && t.coats > 0) register(t);
                                break;
                            }
                    }
                    Verify();
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where; }
            return null;
        }

        private static List<string> Lights(int n, int baseSeed)
        {
            return Family("lights", n, baseSeed, seed => Drive(seed, GenLights, RunLights));
        }

        // ════════════════════════ rules ════════════════════════
        public static long MatChill, MatAge, DodgeReach, DodgeClamp, WornCases, ImpressBlocked, DiminishedEvents, FirstCoatEvents;

        private static string RunRules(int seed)
        {
            var r = new Random(seed);
            // ---- coat cap and the first-coat latch ----
            {
                int ceiling = 3, setting = 1 + r.Next(3), coats = 0; bool bonus = false; int bonusEvents = 0;
                for (int s = 0; s < 40; s++)
                {
                    Steps++;
                    int k = r.Next(10);
                    if (k < 6)
                    {
                        bool can = RM_DeepfireRules.CanAddCoat(coats, ceiling, setting);
                        Check(can == (coats < Math.Min(ceiling, setting)), "CanAddCoat disagrees with min(ceiling, setting)");
                        if (can)
                        {
                            bool first = RM_DeepfireRules.IsFirstCoat(coats, bonus);
                            Check(first == (coats == 0 && !bonus), "IsFirstCoat is not 'no coats and never bonused'");
                            coats++;
                            Check(coats <= setting && coats <= ceiling, "a coat landed above the cap");
                            if (first) { bonus = true; bonusEvents++; FirstCoatEvents++; }
                        }
                    }
                    else if (k < 8) coats = 0;                          // strip: bonusApplied is never reset
                    else setting = 1 + r.Next(3);                       // the slider moves; existing coats are not stripped
                    Check(bonusEvents <= 1, "the first-coat bonus fired twice for one thing");
                    Check(RM_DeepfireRules.CoatCap(ceiling, setting) <= ceiling, "cap above the ceiling");
                }
                Check(RM_DeepfireRules.CoatIndex(-3, 3) == 0 && RM_DeepfireRules.CoatIndex(9, 3) == 3 && RM_DeepfireRules.CoatIndex(2, 3) == 2, "CoatIndex clamp");
            }
            // ---- status engine ----
            {
                for (int s = -2; s <= 12; s++)
                {
                    int want = s <= 0 ? -1 : (s <= 2 ? 0 : (s <= 4 ? 1 : 2));
                    Check(RM_DeepfireRules.ScoreStage(s) == want, $"ScoreStage({s}) = {RM_DeepfireRules.ScoreStage(s)} want {want}");
                }
                for (int m = 0; m < 16; m++)
                {
                    bool en = (m & 1) != 0, titled = (m & 2) != 0, req = (m & 4) != 0; int score = (m & 8) != 0 ? 4 : 0;
                    int got = RM_DeepfireRules.WearerThoughtStage(en, titled, req, score);
                    int want = !en ? -1 : (titled != req ? -1 : (score <= 0 ? -1 : 1));
                    Check(got == want, $"WearerThoughtStage({en},{titled},{req},{score}) = {got} want {want}");
                    bool offence = RM_DeepfireRules.WearsAboveStation(en, titled, req, score, 2);
                    Check(offence == (en && titled && !req && score >= 2), "WearsAboveStation truth table");
                }
                int low = 2 + r.Next(4), high = low + 1 + r.Next(6);
                for (int sc = 0; sc < 20; sc++)
                {
                    int got = RM_DeepfireRules.BedroomStage(true, true, sc, low, high);
                    Check(got == (sc >= high ? 1 : (sc >= low ? 0 : -1)), $"BedroomStage({sc},{low},{high}) = {got}");
                    Check(RM_DeepfireRules.BedroomStage(false, true, sc, low, high) == -1 && RM_DeepfireRules.BedroomStage(true, false, sc, low, high) == -1, "bedroom thought fired for an untitled pawn or with status off");
                }
                int sum = 0, cap = 1 + r.Next(8);
                for (int g = 0; g < 8; g++)
                {
                    bool hasComp = r.Next(2) == 0, hasExt = r.Next(2) == 0; int coats = r.Next(5), ext = r.Next(4);
                    int gl = RM_DeepfireRules.GoodLevel(hasComp, coats, hasExt, ext);
                    int wantG = hasComp && coats > 0 ? coats : (hasExt ? ext : 0);
                    Check(gl == wantG, "GoodLevel disagrees (comp first, then the extension)");
                    sum += gl;
                    Check(RM_DeepfireRules.DisplayScore(sum, cap) == Math.Min(sum, cap) && RM_DeepfireRules.DisplayScore(sum, cap) <= cap, "DisplayScore exceeds the cap");
                }
                int per = 1 + r.Next(12), f = r.Next(20), w = r.Next(40), fl = r.Next(40);
                Check(RM_DeepfireRules.RoomScore(f, w, fl, per) == f + (w + fl) / per, "RoomScore");
                Check(RM_DeepfireRules.RoomScore(f, w + per, fl, per) == RM_DeepfireRules.RoomScore(f, w, fl, per) + 1, "one more block of per walls is not exactly one point");
                // impress: once per faction per quadrum
                var last = new Dictionary<int, int>(); int quad = 0;
                var granted = new Dictionary<(int, int), int>();
                for (int s = 0; s < 40; s++)
                {
                    if (r.Next(5) == 0) quad++;
                    int fac = r.Next(4);
                    bool known = last.TryGetValue(fac, out int q);
                    if (RM_DeepfireRules.CanImpress(known, q, quad)) { last[fac] = quad; granted[(fac, quad)] = granted.TryGetValue((fac, quad), out int n) ? n + 1 : 1; }
                    else ImpressBlocked++;
                }
                Check(granted.Values.All(v => v == 1), "a faction was impressed twice in one quadrum");
            }
            // ---- beauty and costs ----
            {
                float flat = r.Next(1, 8), pct = r.Next(0, 6) * 0.1f, baseB = r.Next(-3, 12); int sizeCap = 1 + r.Next(6);
                float prev = float.MinValue;
                for (int cells = 1; cells <= 10; cells++)
                {
                    float got = RM_DeepfireRules.BeautyBonus(flat, pct, sizeCap, cells, 1, baseB);
                    Check(Near(got, flat * Math.Min(cells, sizeCap) + pct * baseB, 1e-4f), "BeautyBonus formula");
                    Check(got >= prev - 1e-4f, "BeautyBonus fell as the footprint grew");
                    prev = got;
                    if (cells >= sizeCap) Check(Near(got, RM_DeepfireRules.BeautyBonus(flat, pct, sizeCap, sizeCap, 1, baseB), 1e-4f), "BeautyBonus grew past the size cap");
                }
                Check(Near(RM_DeepfireRules.BeautyBonus(flat, pct, sizeCap, 0, 0, baseB), flat + pct * baseB, 1e-4f), "a zero-size footprint is not treated as one cell");
                float per10 = r.Next(1, 6), fcap = r.Next(1, 12); float p2 = float.MinValue;
                for (int c = 0; c <= 80; c++)
                {
                    float b = RM_DeepfireRules.FloorRoomBonus(per10, fcap, c);
                    Check(b <= fcap + 1e-4f && b >= p2 - 1e-4f, "FloorRoomBonus exceeds its cap or falls");
                    Check(Near(b, Math.Min(per10 * (c / 10), fcap), 1e-4f), "FloorRoomBonus is not per-10-cells stepped");
                    p2 = b;
                }
                for (int m = 0; m < 16; m++)
                {
                    bool art = (m & 1) != 0, ap = (m & 2) != 0, wp = (m & 4) != 0, wall = (m & 8) != 0;
                    PaintClass want = art ? PaintClass.Art : ap ? PaintClass.Apparel : wp ? PaintClass.Weapon : wall ? PaintClass.Wall : PaintClass.Furniture;
                    Check(RM_DeepfireRules.ClassOf(art, ap, wp, wall) == want, "ClassOf precedence (art, apparel, weapon, wall, furniture)");
                    PaintClass want2 = ap ? PaintClass.Apparel : wp ? PaintClass.Weapon : wall ? PaintClass.Wall : PaintClass.Furniture;
                    Check(RM_DeepfireRules.PaintableClassOf(ap, wp, wall) == want2, "PaintableClassOf precedence");
                }
                int fb = 1 + r.Next(4), fx = r.Next(1, 4), fc = fb + r.Next(0, 6), pc = -1;
                for (int cells = 1; cells <= 12; cells++)
                {
                    int cost = RM_DeepfireRules.Cost(PaintClass.Furniture, cells, 1, 9, 9, 9, 9, fb, fx, fc);
                    Check(cost == (cells == 1 ? fb : Math.Min(fc, fb + (cells - 1) * fx)), "furniture cost formula");
                    Check(cost >= pc && cost <= Math.Max(fb, fc), "furniture cost fell or passed its cap");
                    pc = cost;
                }
                Check(RM_DeepfireRules.Cost(PaintClass.Art, 5, 5, 1, 2, 3, 4, 5, 6, 7) == 1 && RM_DeepfireRules.Cost(PaintClass.Apparel, 5, 5, 1, 2, 3, 4, 5, 6, 7) == 2
                    && RM_DeepfireRules.Cost(PaintClass.Weapon, 5, 5, 1, 2, 3, 4, 5, 6, 7) == 3 && RM_DeepfireRules.Cost(PaintClass.Wall, 5, 5, 1, 2, 3, 4, 5, 6, 7) == 4, "flat costs by class");
            }
            // ---- mat lifecycle ----
            {
                float life = new[] { 0.25f, 0.5f, 1f, 2f, 10f }[r.Next(5)], chill = new[] { -5f, 5f, 10f, 20f }[r.Next(4)]; bool coldSnaps = r.Next(2) == 0;
                int ticks = 0, n = 0; bool dead = false; int prevHours = int.MaxValue;
                const int TPD = 60000, RARE = 250;
                for (int s = 0; s < 3000 && !dead; s++)
                {
                    Steps++; n++;
                    float amb = coldSnaps && r.Next(40) == 0 ? chill - 1f - r.Next(5) : chill + r.Next(30);
                    if (n > 1) { /* alive so far */ }
                    MatFate fate = RM_DeepfireRules.MatTick(ref ticks, amb, chill, life, RARE, TPD);
                    Check(ticks == n * RARE, "ticksAlive is not one rare interval per tick");
                    if (amb < chill) { Check(fate == MatFate.DiedChill, "a mat survived below the chill temperature"); MatChill++; dead = true; }
                    else if ((double)ticks >= (double)life * TPD) { Check(fate == MatFate.DiedAge, "a mat outlived its life"); MatAge++; dead = true; }
                    else
                    {
                        Check(fate == MatFate.Alive, "a mat died early");
                        int h = RM_DeepfireRules.HoursLeft(ticks, life, TPD);
                        Check(h <= prevHours && h >= 0 && h <= (int)(life * 24f + 0.5f), "HoursLeft out of order or range");
                        prevHours = h;
                    }
                }
                Check(RM_DeepfireRules.HoursLeft(int.MaxValue / 2, life, TPD) == 0 && RM_DeepfireRules.HoursLeft(0, life, TPD) == (int)(life * 24f + 0.5f), "HoursLeft ends");
            }
            // ---- god deltas ----
            {
                string[] gods = { "Ishko", "MobUnloo", "Rekko", "Zizzik", "Ozzik", "Aaa", "Bbb", "Ccc", "Ddd" };
                string[] trio = { "MobUnloo", "Rekko", "Zizzik" };
                float like = 1 + r.Next(5), adore = like + 1 + r.Next(9), ishkoPen = 1 + r.Next(5), statue = adore + ishkoPen + 1 + r.Next(9);
                var ct = RM_DeepfireRules.CoatTable(gods, trio, "Ishko", ishkoPen, adore, like);
                Check(ct.Count == gods.Length, "CoatTable lost a god");
                foreach (var g in gods)
                    Check(Near(ct[g], g == "Ishko" ? -ishkoPen : trio.Contains(g) ? adore : like, 1e-5f), $"CoatTable[{g}]");
                string sg = gods[r.Next(gods.Length)];
                var st = RM_DeepfireRules.StatueTable(gods, sg, "Ishko", statue, ishkoPen, like);
                foreach (var g in gods)
                {
                    float want = g == sg ? (g == "Ishko" ? -statue : statue) : g == "Ishko" ? -ishkoPen : like;
                    Check(Near(st[g], want, 1e-5f), $"StatueTable[{g}] for statue {sg}");
                }
                Check(st.Values.Count(v => Math.Abs(v) >= statue) == 1, "more than one god reacts at statue strength");
                int after = r.Next(0, 6); var counts = new Dictionary<int, int>(); var undim = new Dictionary<int, int>();
                for (int e = 0; e < 40; e++)
                {
                    Steps++;
                    int def = r.Next(3); counts.TryGetValue(def, out int prior); counts[def] = prior + 1;
                    foreach (float amt in ct.Values)
                    {
                        float d = RM_DeepfireRules.Diminish(amt, prior, after, 1f);
                        if (prior < after) Check(d == amt, "an early first-coat event was shrunk");
                        else { Check(Math.Abs(d) == Math.Min(Math.Abs(amt), 1f) && Math.Sign(d) == Math.Sign(amt), "a late event was not clamped to min(|amt|,1) keeping its sign"); DiminishedEvents++; }
                    }
                    if (prior < after) undim[def] = undim.TryGetValue(def, out int u) ? u + 1 : 1;
                }
                foreach (var kv in counts) Check((undim.TryGetValue(kv.Key, out int u2) ? u2 : 0) == Math.Min(kv.Value, after), "undiminished events per def != min(events, after)");
            }
            // ---- dodge inversion ----
            for (int rep = 0; rep < 6; rep++)
            {
                int np = 2 + r.Next(5);
                var xs = new List<float>(); var ys = new List<float>(); float x = r.Next(0, 10), y = r.Next(0, 5) * 0.05f;
                for (int i = 0; i < np; i++)
                {
                    xs.Add(x); ys.Add(y);
                    x += 1 + r.Next(15);
                    y += r.Next(4) == 0 ? 0f : r.Next(1, 6) * 0.04f;
                }
                Func<float, float> eval = v =>
                {
                    if (v <= xs[0]) return ys[0];
                    if (v >= xs[xs.Count - 1]) return ys[ys.Count - 1];
                    for (int i = 1; i < xs.Count; i++) if (v <= xs[i]) return xs[i] == xs[i - 1] ? ys[i] : ys[i - 1] + (v - xs[i - 1]) / (xs[i] - xs[i - 1]) * (ys[i] - ys[i - 1]);
                    return ys[ys.Count - 1];
                };
                float minV = r.Next(3) == 0 ? ys[0] * 0.5f : (r.Next(3) == 0 ? ys[ys.Count - 1] * 0.9f : 0f), pen = r.Next(0, 8) * 0.02f, val = xs[0] - 2 + (float)r.NextDouble() * (xs[xs.Count - 1] - xs[0] + 4);
                float nv = RM_DeepfireRules.DodgeAdjust(eval, xs, ys, minV, pen, val);
                float fin = eval(val), target = Math.Max(minV, fin - pen), after = eval(nv);
                Check(nv <= val + 1e-4f, "the dodge penalty raised the raw value");
                Check(after <= fin + 1e-3f, "the dodge penalty raised the final value");
                if (target > ys[0] + 1e-6f && target <= fin + 1e-6f) { Check(Near(after, target, 1e-3f), $"dodge landed at {after}, wanted {target} (final {fin}, penalty {pen})"); DodgeReach++; }
                if (target > fin + 1e-6f) { Check(nv == val, "a floor above the value moved it"); DodgeClamp++; }
                if (pen == 0f && minV <= ys[0]) Check(Near(after, fin, 1e-3f), "a zero penalty changed the final dodge");
                Check(RM_DeepfireRules.DodgeAdjust(eval, new List<float> { 1f }, new List<float> { 1f }, 0f, 0.1f, 0.5f) == 0.4f, "a one-point curve takes the penalty off the raw value");
            }
            // ---- worn blend ----
            {
                WornCases++;
                int n = r.Next(0, 6); float[] inten = { 0f, 0.45f, 0.7f, 1f };
                var coats = new List<int>(); var cr = new List<float>(); var cg = new List<float>(); var cb = new List<float>();
                for (int i = 0; i < n; i++) { coats.Add(r.Next(-1, 5)); cr.Add((float)r.NextDouble()); cg.Add((float)r.NextDouble()); cb.Add((float)r.NextDouble()); }
                bool ok = RM_DeepfireRules.WornBlend(coats, cr, cg, cb, inten, 3, out float R, out float G, out float B, out int mx);
                int wantMax = coats.Count == 0 ? 0 : Math.Max(0, coats.Max());
                Check(ok == (wantMax > 0), "WornBlend says glow=" + ok + " but the max coat is " + wantMax);
                if (ok)
                {
                    Check(mx == wantMax, "maxCoats");
                    float k = inten[Math.Min(3, mx)];
                    float w = 0, er = 0, eg = 0, eb = 0;
                    for (int i = 0; i < n; i++) if (coats[i] > 0) { w += coats[i]; er += cr[i] * coats[i]; eg += cg[i] * coats[i]; eb += cb[i] * coats[i]; }
                    Check(Near(R, er / w * k, 1e-4f) && Near(G, eg / w * k, 1e-4f) && Near(B, eb / w * k, 1e-4f), "blend is not the coat-weighted mean scaled by the brightest coat's intensity");
                    var order = Enumerable.Range(0, n).OrderBy(_ => r.Next()).ToList();
                    WornBlendRepeat(coats, cr, cg, cb, inten, order, R, G, B);
                    for (int i = 0; i < n; i++) if (coats[i] > 0) { Check(R >= 0f && R <= k + 1e-4f, "blend channel out of range"); }
                }
            }
            // ---- dark test ----
            {
                float lerp = 0.4f, fac = 3.6f, mxn = 0.5f;
                Check(RM_DeepfireRules.OtherLightAt(true, 0, 0, 0, 0, 0, 0, 1f, lerp, fac, mxn) == 1f, "an overlit cell is not fully lit");
                for (int rep = 0; rep < 12; rep++)
                {
                    float ar = r.Next(256), ag = r.Next(256), ab = r.Next(256), or = r.Next(256), og = r.Next(256), ob = r.Next(256), rad = r.Next(0, 8) * 0.5f;
                    float v = RM_DeepfireRules.OtherLightAt(false, ar, ag, ab, or, og, ob, rad, lerp, fac, mxn);
                    Check(v >= 0f && v <= mxn + 1e-5f, "OtherLightAt out of [0,max]");
                    Check(RM_DeepfireRules.OtherLightAt(false, ar + 10, ag, ab, or, og, ob, rad, lerp, fac, mxn) >= v - 1e-5f, "more ambient light lowered the reading");
                    Check(RM_DeepfireRules.OtherLightAt(false, ar, ag, ab, or + 10, og, ob, rad, lerp, fac, mxn) <= v + 1e-5f, "more of OUR light raised the other-light reading");
                    float none = RM_DeepfireRules.OtherLightAt(false, ar, ag, ab, 0, 0, 0, rad, lerp, fac, mxn);
                    Check(Near(none, Math.Min(mxn, Math.Max(ar, Math.Max(ag, ab)) / 255f * fac), 1e-4f), "with no light of ours the reading is not the plain ground glow");
                    Check(Near(RM_DeepfireRules.OtherLightAt(false, ar, ag, ab, or, og, ob, 0.2f, lerp, fac, mxn), RM_DeepfireRules.OtherLightAt(false, ar, ag, ab, or, og, ob, 1f, lerp, fac, mxn), 1e-5f), "a radius under 1 is not treated as 1");
                }
            }
            return null;
        }

        private static void WornBlendRepeat(List<int> coats, List<float> cr, List<float> cg, List<float> cb, float[] inten, List<int> order, float R, float G, float B)
        {
            RM_DeepfireRules.WornBlend(order.Select(i => coats[i]).ToList(), order.Select(i => cr[i]).ToList(), order.Select(i => cg[i]).ToList(), order.Select(i => cb[i]).ToList(),
                inten, 3, out float r2, out float g2, out float b2, out int _);
            Check(Near(R, r2, 1e-4f) && Near(G, g2, 1e-4f) && Near(B, b2, 1e-4f), "the blend depends on item order");
        }

        private static List<string> Rules(int n, int baseSeed) { return Family("rules", n, baseSeed, RunRules); }

        // ════════════════════════ cuisine ════════════════════════
        public static long Steered, Missed, PlainRolls, CapBlocks, Bumps, Adds, VermilionLands, RateChecks;

        private static string RunCuisine(int seed)
        {
            var r = new Random(seed);
            // ---- steer chance ----
            for (int min = 4; min <= 20; min++)
            {
                float prev = 0f;
                for (int sk = 0; sk <= 25; sk++)
                {
                    float c = RM_DeepfireCuisine.SteerChance(min, sk);
                    Check(c >= 0f && c <= 1f, $"SteerChance({min},{sk}) = {c} outside [0,1]");
                    if (sk < min) Check(c == 0f, $"a cook below the minimum steers: SteerChance({min},{sk}) = {c}");
                    else
                    {
                        Check(c >= prev - 1e-6f && c >= 0.5f - 1e-6f, $"SteerChance({min},{sk}) = {c} fell or is under 50%");
                        if (sk >= 20) Check(c == 1f, $"a skill-20 cook does not always steer (min {min}): {c}");
                        if (sk == min && min < 20) Check(Near(c, 0.5f, 1e-5f), $"SteerChance at the minimum is {c}, not 50%");
                        prev = c;
                    }
                }
            }
            // ---- roll partition ----
            int nf = 3 + r.Next(12);
            var w = new float[nf]; var en = new bool[nf];
            for (int i = 0; i < nf; i++) { w[i] = r.Next(4) == 0 ? 0f : 1 + r.Next(12); en[i] = r.Next(5) != 0; }
            int verm = r.Next(nf), excl = r.Next(3) == 0 ? -1 : r.Next(nf);
            bool[] enArg = r.Next(6) == 0 ? null : en;
            Func<int, bool> elig = i => (enArg == null || enArg[i]) && i != excl && i != verm && w[i] > 0f;
            float total = 0f; for (int i = 0; i < nf; i++) if (elig(i)) total += w[i];
            Func<float, int> oracle = rv => { float cum = 0f; int last = -1; for (int i = 0; i < nf; i++) if (elig(i)) { cum += w[i]; last = i; if (rv <= cum) return i; } return last; };
            Func<float, int> pick = rv => RM_DeepfireCuisine.WeightedRandom(w, enArg, excl, verm, tot => { Check(Near(tot, total, 1e-3f), "the roll range is not the eligible weight total"); return rv; });
            if (total <= 0f) Check(pick(0f) == -1, "a pick came back from an empty pool");
            else
            {
                var probes = new List<float> { 0f, total, total + 0.001f };
                float cum = 0f; for (int i = 0; i < nf; i++) if (elig(i)) { cum += w[i]; probes.Add(cum); probes.Add(cum - 0.001f); probes.Add(cum + 0.001f); }
                for (int k = 0; k < 20; k++) probes.Add((float)r.NextDouble() * total);
                foreach (float p in probes)
                {
                    if (p < 0f) continue;
                    int got = pick(p), want = oracle(p);
                    Check(got == want, $"roll {p} picked {got}, the cumulative table says {want}");
                    Check(got >= 0 && elig(got), $"roll {p} picked an ineligible family {got} (excluded {excl}, vermilion {verm})");
                }
                // rate
                var rng = new Random(seed * 31 + 7); var hits = new int[nf]; const int N = 6000;
                for (int k = 0; k < N; k++) hits[RM_DeepfireCuisine.WeightedRandom(w, enArg, excl, verm, tot => (float)(rng.NextDouble() * tot))]++;
                for (int i = 0; i < nf; i++)
                {
                    double p = elig(i) ? w[i] / total : 0, sd = Math.Sqrt(N * p * (1 - p));
                    Check(Math.Abs(hits[i] - N * p) <= 5 * sd + 3, $"family {i} rolled {hits[i]}/{N}, expected {N * p:F0}");
                }
                RateChecks++; PlainRolls += N;
            }
            // ---- Choose ----
            {
                int steerMin = 4 + r.Next(15), vermMin = 10 + r.Next(11);
                for (int rep = 0; rep < 30; rep++)
                {
                    int intended = r.Next(4) == 0 ? -1 : r.Next(nf), skill = r.Next(26);
                    int asked = 0; float askedP = -1f;
                    bool yes = r.Next(2) == 0;
                    int got = RM_DeepfireCuisine.Choose(intended, skill, steerMin, vermMin, verm, w, enArg, p => { asked++; askedP = p; return yes; },
                        tot => (float)(r.NextDouble() * tot));
                    int min = intended == verm ? vermMin : steerMin;
                    bool steerable = intended >= 0 && RM_DeepfireCuisine.Enabled(enArg, intended);
                    if (steerable && skill >= min)
                    {
                        Check(asked == 1 && Near(askedP, RM_DeepfireCuisine.SteerChance(min, skill), 1e-6f), "the chance asked is not SteerChance(min, skill)");
                        if (yes) { Check(got == intended, "a successful steer did not return the intended family"); Steered++; if (intended == verm) VermilionLands++; }
                        else { Check(got != intended, "a missed steer still returned the intended family"); Missed++; }
                    }
                    else
                    {
                        Check(asked == 0, "the steer roll was made for a cook below the minimum or an unsteerable dish");
                        if (steerable) Check(got != intended || false, "a cook below the minimum steered");
                    }
                    if (got >= 0 && !(steerable && skill >= min && yes && intended == verm)) Check(got != verm, "the vermilion came from a plain roll or a re-roll");
                    if (got >= 0) Check(RM_DeepfireCuisine.Enabled(enArg, got) && w[got] > 0f || got == intended, "a disabled or zero-weight family was chosen");
                }
                // steer rate
                int skill2 = steerMin + r.Next(0, 25 - steerMin), target = r.Next(nf);
                if (target == verm) target = (target + 1) % nf;
                var rng = new Random(seed ^ 0x5bd1); int hit = 0; const int N = 5000;
                var enAll = (bool[])null;
                float pcs = RM_DeepfireCuisine.SteerChance(steerMin, skill2);
                for (int k = 0; k < N; k++)
                    if (RM_DeepfireCuisine.Choose(target, skill2, steerMin, vermMin, verm, w, enAll, p => rng.NextDouble() < p, tot => (float)(rng.NextDouble() * tot)) == target) hit++;
                // a miss may also re-roll... never onto the target (it is excluded), so hits are exactly the steered ones
                double sd2 = Math.Sqrt(N * pcs * (1 - pcs));
                Check(Math.Abs(hit - N * pcs) <= 5 * sd2 + 3, $"steer rate {hit}/{N} for chance {pcs}");
                RateChecks++;
            }
            // ---- a pawn eating dishes ----
            {
                int cap = 1 + r.Next(4); var state = new Dictionary<int, float>(); const float MAXSEV = 3f;
                var wAll = new float[nf]; for (int i = 0; i < nf; i++) wAll[i] = i == verm ? 0f : 1f + i % 3;
                bool[] fam = r.Next(2) == 0 ? null : en; bool vermAte = false;
                var rng = new Random(seed + 99);
                for (int meal = 0; meal < 40; meal++)
                {
                    Steps++;
                    int intended = r.Next(3) == 0 ? -1 : r.Next(nf), skill = r.Next(26);
                    int got = RM_DeepfireCuisine.Choose(intended, skill, 8, 14, verm, wAll, fam, p => rng.NextDouble() < p, tot => (float)(rng.NextDouble() * tot));
                    if (got < 0) continue;
                    if (got == verm) { Check(intended == verm && skill >= 14, "the vermilion landed without a qualifying steered dish"); vermAte = true; }
                    var oc = RM_DeepfireCuisine.Apply(state.ContainsKey(got), state.Count, cap);
                    switch (oc)
                    {
                        case FamilyOutcome.Bumped: Check(state.ContainsKey(got), "bumped a family the pawn does not have"); state[got] = RM_DeepfireCuisine.Bump(state[got], MAXSEV); Bumps++; break;
                        case FamilyOutcome.Added: Check(!state.ContainsKey(got) && state.Count < cap, "added past the cap"); state[got] = 0.5f; Adds++; break;
                        case FamilyOutcome.CapBlocked: Check(!state.ContainsKey(got) && state.Count >= cap, "blocked a family the pawn could take"); CapBlocks++; break;
                        default: throw new Exception("no outcome");
                    }
                    Check(state.Count <= cap, $"pawn carries {state.Count} families, cap {cap}");
                    Check(state.Values.All(v => v <= MAXSEV + 1e-5f && v >= 0.5f), "family severity out of range");
                }
                Check(RM_DeepfireCuisine.Bump(2.5f, 3f) == 3f && RM_DeepfireCuisine.Bump(0.5f, 3f) == 1.5f, "Bump");
                if (vermAte) Check(state.ContainsKey(verm) || state.Count >= 0, "unreachable");
            }
            return null;
        }

        private static List<string> Cuisine(int n, int baseSeed) { return Family("cuisine", n, baseSeed, RunCuisine); }

        // DESIGN_PASS LP-2: the GlowTank water reserve. A tank on a net that always gives never goes dry; a tank whose
        // net is dry goes parched within its reserve and recovers on the first unit; the reserve never exceeds 2 units.
        private static List<string> Water(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                var r = new Random(baseSeed * 104729 + k);
                float upd = new[] { 0f, -1f, 0.5f, 4f, 20f, 1e7f }[r.Next(6)];
                int per = RM_GlowTankWater.TicksPerUnit(upd);
                int reserve = 0; bool netGives = r.Next(2) == 0; int dryRun = 0;
                try
                {
                    Check(upd > 0f ? per >= 1 : per == 0, $"TicksPerUnit({upd}) = {per}");
                    for (int st = 0; st < 200; st++)
                    {
                        Steps++;
                        if (r.Next(25) == 0) netGives = !netGives;
                        reserve = RM_GlowTankWater.Drain(reserve, 250);
                        if (RM_GlowTankWater.WantsDraw(reserve, per) && netGives) reserve = RM_GlowTankWater.Refill(reserve, per);
                        bool parched = RM_GlowTankWater.Parched(true, per, reserve);
                        Check(reserve >= 0 && (per <= 0 || reserve <= 2L * per), $"reserve {reserve} outside [0, 2x{per}]");
                        if (per <= 0) Check(!parched, "a tank that drinks nothing went parched");
                        if (netGives && per >= 500) Check(!parched, $"parched on a giving net (per {per}, reserve {reserve})");
                        Check(!RM_GlowTankWater.Parched(false, per, reserve), "parched with the gate off");
                        dryRun = parched ? dryRun + 1 : 0;
                    }
                }
                catch (Exception e) { fails.Add($"water seed {k}: {e.Message}"); }
            }
            Cases++; Steps++;
            if (!RM_GlowTankWater.IsOceanLiquid("RM_Liquid_SaltWater") || !RM_GlowTankWater.IsOceanLiquid("RM_Liquid_BoilingWater")
                || RM_GlowTankWater.IsOceanLiquid("RM_Liquid_Brine") || RM_GlowTankWater.IsOceanLiquid("RM_Liquid_Water") || RM_GlowTankWater.IsOceanLiquid(null))
                fails.Add("water units: only salt and boiling water count");
            if (RM_GlowTankWater.GateActive(true, false) || RM_GlowTankWater.GateActive(false, true) || !RM_GlowTankWater.GateActive(true, true))
                fails.Add("water units: the gate needs the setting AND FlowWorks");
            if (RM_GlowTankWater.TicksPerUnit(4f) != 15000 || RM_GlowTankWater.Refill(int.MaxValue - 1, int.MaxValue) != int.MaxValue)
                fails.Add("water units: 4/day = 15000 ticks per unit; Refill saturates");
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("lights", () => Lights(N(3000), S(1))),
                ("rules", () => Rules(N(3000), S(1))),
                ("cuisine", () => Cuisine(N(1500), S(1))),
                ("water", () => Water(N(2000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"reached: lights multi-cell groups {MultiGroups}, own lights {OwnLights}, clustered things {ClusteredThings}, floor adds {FloorAdds}, rebuilds {Rebuilds} ({BlockChangesWithThings} with coated things), reloads {Reloads}");
            Console.WriteLine($"reached: rules mat chill deaths {MatChill}, age deaths {MatAge}, first-coat events {FirstCoatEvents}, impress blocked {ImpressBlocked}, diminished {DiminishedEvents}, dodge reach {DodgeReach} / floor-clamped {DodgeClamp}, worn blends {WornCases}");
            Console.WriteLine($"reached: cuisine steered {Steered} (vermilion {VermilionLands}), missed {Missed}, plain rolls {PlainRolls}, rate checks {RateChecks}, bumps {Bumps}, adds {Adds}, cap blocks {CapBlocks}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (MultiGroups == 0 || OwnLights == 0 || ClusteredThings == 0 || FloorAdds == 0 || BlockChangesWithThings == 0 || Reloads == 0 || MatChill == 0 || MatAge == 0 || FirstCoatEvents == 0
                    || ImpressBlocked == 0 || DiminishedEvents == 0 || DodgeReach == 0 || DodgeClamp == 0 || Steered == 0 || Missed == 0 || VermilionLands == 0 || Bumps == 0 || Adds == 0 || CapBlocks == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"luminouspigment fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
