// Approach B for Webwork: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WebworkKernel.cs):
//   urraveth  action sequences on the seven-piece skeleton (loads, damage, deconstruction, a watcher walking about, rare ticks,
//             examines, settings flips) through the production load / creak / collapse / cascade / examine kernel calls, against an
//             independent spec that restates the rules from cell sets (not rects) and checks the conservation properties
//   relay     the nest wall's egg-clutch timer: ticks, mother dying and returning, clutches mined, multiplier changes
//   tables    gridded / exhaustive checks: emergent spawn gate, biome score, nest and site margins, outline ring, rounding,
//             intervals and windows over the Mod Settings slider ranges
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Webwork.SelfTest
{
    internal static class WebworkFuzz
    {
        public static long Cases, Steps, Collapses, Creaks, Settles, CascadeStarts, Completes, FourChapters, Unwatched, Lays, Dying, Skipped, Gaps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

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

        private struct Act
        {
            public int kind, a, b; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + (f ? ",T" : "") + ")"; }
        }

        // ════════════════════════ urraveth ════════════════════════
        // The shipped layout (RM_GenStep_UrravethRemains.Layout) with the footprints and extension numbers of RM_Urraveth_Remains.xml.
        private static readonly (string name, string chapter, bool skull, int rank, float cap, int x, int z, int w, int h)[] Layout =
        {
            ("LimbPile", "pinned", false, 0, 2f, 1, 2, 2, 2),
            ("LimbPile", "pinned", false, 0, 2f, 9, 1, 2, 2),
            ("Pelvis", "eaten", false, 1, 3f, 0, 4, 3, 3),
            ("RibSection", "bound", false, 2, 3f, 3, 3, 3, 5),
            ("RibSection", "bound", false, 2, 3f, 6, 3, 3, 5),
            ("NeckRun", "cut", false, 3, 2f, 9, 5, 3, 2),
            ("Skull", "cut", true, 4, 2f, 12, 4, 3, 3),
        };

        private sealed class P
        {
            public string name, chapter; public bool skull; public int rank; public float cap; public int x, z, w, h;
            public int maxHp = 900, hp = 900; public bool alive = true, wrapped = true; public int creak = -1, lost; public float pawns, items;
            public int MaxX { get { return x + w - 1; } }
            public int MaxZ { get { return z + h - 1; } }
            public int CX { get { return x + w / 2; } }
            public int CZ { get { return z + h / 2; } }
        }

        private static List<P> NewPieces()
        {
            return Layout.Select(l => new P { name = l.name, chapter = l.chapter, skull = l.skull, rank = l.rank, cap = l.cap, x = l.x, z = l.z, w = l.w, h = l.h }).ToList();
        }

        // ---- production-shaped world: every decision goes through the kernel ----
        private sealed class World
        {
            public List<P> ps = NewPieces();
            public bool enabled = true; public float hours = 6f; public int perPiece = 8;
            public bool watcher; public int wx, wz;
            public List<string> chapters = new List<string>(); public bool complete; public long weave;
            public int completions;

            public IEnumerable<P> Neighbours(P p)
            {
                if (!p.alive) yield break;
                foreach (P q in ps)
                    if (q != p && q.alive && RM_UrravethKernel.Adjacent(p.x, p.z, p.MaxX, p.MaxZ, q.x, q.z, q.MaxX, q.MaxZ)) yield return q;
            }
            public IEnumerable<P> Supporters(P p) { return Neighbours(p).Where(n => RM_UrravethKernel.IsSupporter(n.rank, p.rank)); }
            public IEnumerable<P> Supported(P p) { return Neighbours(p).Where(n => RM_UrravethKernel.IsSupported(n.rank, p.rank)); }
            public float Load(P p)
            {
                int heavy = 0;
                foreach (P s in Supporters(p)) if (RM_UrravethKernel.HeavilyDamaged(s.hp, s.maxHp)) heavy++;
                return RM_UrravethKernel.Load(p.pawns + p.items, p.lost, p.cap, heavy);
            }
            public bool Over(P p) { return RM_UrravethKernel.Overloaded(Load(p), p.cap); }
            public int Window { get { return RM_UrravethKernel.WindowTicks(hours); } }
            public bool Near(P p) { return watcher && RM_UrravethKernel.PawnNear(wx - p.CX, wz - p.CZ, 10f, p.w, p.h); }
            public bool CanOpenLast(P p) { return RM_UrravethKernel.CanOpenLastWrapping(p.skull, p.wrapped, true, complete, p.alive, p.alive && ps.Where(q => q.alive).All(q => !q.wrapped)); }

            public void Step(P p)
            {
                if (!p.alive || !enabled) return;
                CreakEvent ev = RM_UrravethKernel.Step(ref p.creak, Over(p), () => Near(p), RM_UrravethKernel.RareTicks, Window);
                if (ev == CreakEvent.Started) Creaks++;
                if (ev == CreakEvent.Settled) Settles++;
                if (ev == CreakEvent.Collapse) { Collapses++; Remove(p); }
            }

            public void Remove(P p)
            {
                if (!p.alive) return;
                foreach (P s in Supported(p).ToList())
                {
                    s.lost++;
                    if (RM_UrravethKernel.StartsCreakingOnLoss(enabled, s.creak >= 0, Over(s))) { s.creak = Window; Creaks++; CascadeStarts++; }
                }
                p.alive = false;
            }

            public string Examine(P p)
            {
                ExamineOutcome o = RM_UrravethKernel.Examine(true, true, p.alive, p.wrapped, CanOpenLast(p));
                if (o == ExamineOutcome.ReadChapter)
                {
                    p.wrapped = false;
                    weave += RM_UrravethKernel.WeaveDropped(perPiece, true);
                    RM_UrravethKernel.RecordChapter(chapters, p.chapter);
                    return "read";
                }
                if (o == ExamineOutcome.Complete) { if (!complete) { complete = true; completions++; } return "complete"; }
                return "nothing";
            }
        }

        // ---- the independent spec: cell sets, doubles, its own state ----
        private sealed class Spec
        {
            public int n; public bool[] alive; public int[] creak, lost; public bool[] wrapped;
            public HashSet<(int, int)>[] cells; public double[] cap; public int[] rank, hp; public double[] occ;
            private bool[,] adjM;
            public bool complete; public long weave; public HashSet<string> chapters = new HashSet<string>(); public int readCount;
            public Spec(List<P> ps)
            {
                n = ps.Count; alive = new bool[n]; creak = new int[n]; lost = new int[n]; wrapped = new bool[n]; cap = new double[n]; rank = new int[n]; hp = new int[n]; occ = new double[n];
                cells = new HashSet<(int, int)>[n];
                for (int i = 0; i < n; i++)
                {
                    alive[i] = true; creak[i] = -1; wrapped[i] = true; cap[i] = ps[i].cap; rank[i] = ps[i].rank; hp[i] = ps[i].hp;
                    cells[i] = new HashSet<(int, int)>();
                    for (int x = 0; x < ps[i].w; x++) for (int z = 0; z < ps[i].h; z++) cells[i].Add((ps[i].x + x, ps[i].z + z));
                }
            }
            public bool Adj(int a, int b)
            {
                if (adjM == null)
                {
                    adjM = new bool[n, n];
                    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) adjM[i, j] = i != j && AdjSlow(i, j);
                }
                return adjM[a, b];
            }
            private bool AdjSlow(int a, int b)
            {
                foreach (var (x, z) in cells[b])
                    for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
                            if (cells[a].Contains((x + dx, z + dz))) return true;
                return false;
            }
            public double LoadOf(int i)
            {
                double l = occ[i] + lost[i] * cap[i];
                for (int j = 0; j < n; j++)
                    if (j != i && alive[j] && rank[j] < rank[i] && Adj(i, j) && hp[j] * 100 < 900 * 35) l += cap[i];
                return l;
            }
        }

        private enum UA { Pawn, ClearPawns, Items, ClearItems, Damage, Deconstruct, Watch, Tick, Examine, Enable, Hours, Weave }

        private static Act[] GenUrraveth(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                UA kind = k < 12 ? UA.Pawn : k < 17 ? UA.ClearPawns : k < 22 ? UA.Items : k < 25 ? UA.ClearItems : k < 36 ? UA.Damage : k < 40 ? UA.Deconstruct
                    : k < 48 ? UA.Watch : k < 78 ? UA.Tick : k < 92 ? UA.Examine : k < 95 ? UA.Enable : k < 98 ? UA.Hours : UA.Weave;
                a[i] = new Act { kind = (int)kind, a = r.Next(1 << 12), b = r.Next(1 << 12), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static readonly float[] Bodies = { 0.25f, 0.5f, 1f, 1.5f, 3f };
        private static readonly int[] Hps = { 900, 500, 316, 315, 314, 100, 1 };
        private static readonly float[] Hours = { 1f, 2f, 6f, 12f, 24f, 0.1f };

        private static string RunUraveth(IList<Act> acts, int seed, bool count)
        {
            var w = new World(); var s = new Spec(w.ps);
            int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    int pi = a.a % w.ps.Count; P p = w.ps[pi];
                    switch ((UA)a.kind)
                    {
                        case UA.Pawn: if (p.alive) { float bs = Bodies[a.b % Bodies.Length]; p.pawns += bs; s.occ[pi] += bs; } break;
                        case UA.ClearPawns: s.occ[pi] -= p.pawns; p.pawns = 0; break;
                        case UA.Items:
                            if (p.alive)
                            {
                                float mass = (1 + a.b % 8) * 12.5f; int stack = 1 + a.b % 5;
                                float per = 50f;
                                float il = RM_UrravethKernel.ItemLoad(mass, stack, per);
                                Check(Math.Abs(il - mass * stack / 50.0) < 1e-4, "ItemLoad " + il);
                                p.items += il; s.occ[pi] += il;
                            }
                            break;
                        case UA.ClearItems: s.occ[pi] -= p.items; p.items = 0; break;
                        case UA.Damage: p.hp = Hps[a.b % Hps.Length]; s.hp[pi] = p.hp; break;
                        case UA.Deconstruct:
                            if (p.alive) { w.Remove(p); SpecRemove(w, s, pi); }
                            break;
                        case UA.Watch: w.watcher = a.f || (a.b & 3) != 0; w.wx = a.a % 17 - 1; w.wz = a.b % 13 - 2; break;
                        case UA.Enable: w.enabled = a.f; break;
                        case UA.Hours: w.hours = Hours[a.b % Hours.Length]; break;
                        case UA.Weave: w.perPiece = a.b % 9 == 0 ? 0 : a.b % 41; break;
                        case UA.Tick:
                            {
                                int rare = 1 + a.b % 40;
                                for (int t = 0; t < rare; t++)
                                {
                                    foreach (P q in w.ps) w.Step(q);
                                    SpecTick(w, s);
                                    if (t % 8 == 0 || t == rare - 1) Compare(w, s);
                                }
                                break;
                            }
                        case UA.Examine:
                            {
                                if (!p.alive)
                                {   // a destroyed piece is despawned: the job fails before it starts, and the kernel refuses it anyway
                                    Check(w.Examine(p) == "nothing" && !p.wrapped == !s.wrapped[pi], "examined a destroyed piece");
                                    Skipped++; break;
                                }
                                bool allowed = RM_UrravethKernel.ExamineAllowed(w.enabled, p.wrapped, w.CanOpenLast(p));
                                bool specAllowed = w.enabled && (s.wrapped[pi] || (p.skull && !s.wrapped[pi] && !s.complete && p.alive && Enumerable.Range(0, s.n).All(j => !s.alive[j] || !s.wrapped[j])));
                                Check(allowed == specAllowed, "ExamineAllowed " + allowed + " spec " + specAllowed + " on " + p.name);
                                if (!allowed) { Skipped++; break; }
                                string got = w.Examine(p);
                                SpecExamine(w, s, pi, got);
                                break;
                            }
                    }
                    Compare(w, s);
                }
                if (count)
                {
                    if (s.complete) Completes++;
                    if (s.chapters.Count == 4) FourChapters++;
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        private static void SpecRemove(World w, Spec s, int i)
        {
            s.alive[i] = false;
            for (int j = 0; j < s.n; j++)
                if (s.alive[j] && s.rank[j] > s.rank[i] && s.Adj(i, j))
                {
                    s.lost[j]++;
                    // loaded by the loss; an overloaded quiet piece starts its countdown (only while the mod is enabled)
                    if (w.enabled && s.creak[j] < 0 && s.LoadOf(j) >= s.cap[j]) s.creak[j] = w.Window;
                }
        }

        private static void SpecTick(World w, Spec s)
        {
            if (!w.enabled) return;
            for (int i = 0; i < s.n; i++)
            {
                if (!s.alive[i]) continue;
                bool over = s.LoadOf(i) >= s.cap[i];
                if (s.creak[i] < 0) { if (over) s.creak[i] = w.Window; continue; }
                if (!over) { s.creak[i] = -1; continue; }
                P p = w.ps[i];
                bool near = w.watcher && (long)(w.wx - p.CX) * (w.wx - p.CX) + (long)(w.wz - p.CZ) * (w.wz - p.CZ)
                    <= Math.Pow(10.0 + Math.Max(p.w, p.h) / 2.0, 2) + 1e-9;
                if (!near) { Unwatched++; continue; }
                s.creak[i] -= 250;
                if (s.creak[i] <= 0) SpecRemove(w, s, i);
            }
        }

        private static void SpecExamine(World w, Spec s, int i, string got)
        {
            P p = w.ps[i];
            if (!p.alive && got != "nothing") throw new Exception("examined a destroyed piece");
            if (got == "read")
            {
                Check(s.wrapped[i], "read a bare piece");
                s.wrapped[i] = false; s.weave += w.perPiece > 0 ? w.perPiece : 0; s.chapters.Add(p.chapter); s.readCount++;
            }
            else if (got == "complete")
            {
                Check(p.skull && !s.wrapped[i] && s.alive[i] && !s.complete, "completed from the wrong piece / twice");
                Check(Enumerable.Range(0, s.n).All(j => !s.alive[j] || !s.wrapped[j]), "completed with a wrapped piece standing");
                s.complete = true;
                if (s.chapters.Count < 4) Gaps++;
            }
            else
            {
                Check(false, "an allowed examine did nothing");
            }
        }

        private static void Compare(World w, Spec s)
        {
            for (int i = 0; i < s.n; i++)
            {
                P p = w.ps[i];
                Check(p.alive == s.alive[i], p.name + i + " alive " + p.alive + " spec " + s.alive[i]);
                Check(p.wrapped == s.wrapped[i], p.name + i + " wrapped");
                if (!p.alive) continue;
                Check(p.creak == s.creak[i], p.name + i + " creak " + p.creak + " spec " + s.creak[i]);
                Check(p.lost == s.lost[i], p.name + i + " lost " + p.lost + " spec " + s.lost[i]);
                double load = s.LoadOf(i);
                Check(Math.Abs(w.Load(p) - load) < 1e-4, p.name + i + " load " + w.Load(p) + " spec " + load);
                Check(p.creak == -1 || p.creak > 0, p.name + i + " creak value " + p.creak + " (a countdown at or below zero should have collapsed)");
                // conservation: a piece's lost count is exactly the removed lower-rank neighbours
                int expect = 0;
                for (int j = 0; j < s.n; j++) if (!s.alive[j] && s.rank[j] < s.rank[i] && s.Adj(i, j)) expect++;
                Check(p.lost == expect, p.name + i + " lost " + p.lost + " but " + expect + " lower-rank neighbours are gone");
            }
            Check(w.complete == s.complete, "complete " + w.complete + " spec " + s.complete);
            Check(w.weave == s.weave, "thrixweave " + w.weave + " spec " + s.weave);
            var order = RM_UrravethKernel.Ordered(w.chapters);
            Check(order.Count == w.chapters.Count && order.Count == s.chapters.Count && order.All(c => s.chapters.Contains(c)), "chapters " + string.Join(",", w.chapters) + " spec " + string.Join(",", s.chapters));
            var idx = order.Select(c => Array.IndexOf(RM_UrravethKernel.ChapterOrder, c)).ToList();
            Check(idx.All(x => x >= 0) && idx.SequenceEqual(idx.OrderBy(x => x)), "chapters out of the order the bones tell them");
            Check(w.completions <= 1, "completed twice");
            if (s.complete) Check(s.chapters.Count >= 1 && s.readCount >= 0, "complete with no chapter read");
        }

        private static List<string> Urraveth(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenUrraveth(r, 30 + r.Next(220)); Cases++;
                if (RunUraveth(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunUraveth(t, seed, false) != null);
                fails.Add($"urraveth seed {seed}: {RunUraveth(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ relay ════════════════════════
        private enum RA { Tick, BigTick, Mother, Def, Clutch, Mine, Mult, Move }

        private static string RunRelay(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x2545f491);
            int now = rr.Next(1000), next = -1; float mult = 1f; bool mother = true, def = true;
            var clutches = new List<(int dx, int dz)>();
            int radius = 4; long lays = 0; int lastLay = -1; int minDays = 20, maxDays = 30; int stepNo = 0;
            Func<float> daysRoll = () => minDays + (float)rr.NextDouble() * (maxDays - minDays);
            next = now + RM_EggRelayKernel.IntervalTicks(daysRoll(), mult);   // PostSpawnSetup
            long startedAt = now;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch ((RA)a.kind)
                    {
                        case RA.Mother: mother = a.f; break;
                        case RA.Def: def = a.b % 6 != 0; break;
                        case RA.Mult: mult = new[] { 0.1f, 0.5f, 1f, 2f, 3f, 0.01f, -1f }[a.b % 7]; break;
                        case RA.Clutch: clutches.Add((a.a % 17 - 8, a.b % 17 - 8)); break;
                        case RA.Mine: if (clutches.Count > 0) clutches.RemoveAt(a.a % clutches.Count); break;
                        case RA.Move: clutches.Clear(); break;
                        case RA.Tick:
                        case RA.BigTick:
                            {
                                int rare = a.kind == (int)RA.Tick ? 1 + a.a % 40 : 100 + a.a % 600;
                                for (int t = 0; t < rare; t++)
                                {
                                    now += 250;
                                    int nextBefore = next;
                                    bool nearby = clutches.Any(c => RM_EggRelayKernel.ClutchNearby(c.dx, c.dz, radius));
                                    // the independent restatement of "nearby": any clutch within 8 cells, Euclidean
                                    bool specNearby = clutches.Any(c => c.dx * c.dx + c.dz * c.dz <= 64);
                                    Check(nearby == specNearby, "ClutchNearby disagrees at " + string.Join(";", clutches));
                                    RelayPlan plan = now < next ? RelayPlan.NotDue : !mother ? RelayPlan.DyingNest : (!def || specNearby) ? RelayPlan.Reschedule : RelayPlan.Place;
                                    RelayPlan got = RM_EggRelayKernel.Plan(now, next, mother, def, nearby);
                                    Check(plan == got, $"Plan {got} spec {plan} (now {now} next {next} mother {mother} def {def} nearby {specNearby})");
                                    if (got == RelayPlan.NotDue || got == RelayPlan.DyingNest)
                                    {
                                        Check(next == nextBefore, "a non-firing check moved the due tick");
                                        if (got == RelayPlan.DyingNest) Dying++;
                                        continue;
                                    }
                                    if (got == RelayPlan.Place)
                                    {
                                        Check(mother && def && !specNearby && now >= nextBefore, "laid under the wrong conditions");
                                        int toPlace = 1 + (a.b + t) % 2;
                                        for (int k = 0; k < toPlace; k++) clutches.Add((rr.Next(-radius, radius + 1), rr.Next(-radius, radius + 1)));
                                        lays++; Lays++; lastLay = now;
                                    }
                                    float days = daysRoll();
                                    int iv = RM_EggRelayKernel.IntervalTicks(days, mult);
                                    Check(iv >= 1, "interval below one tick");
                                    double want = days * 60000.0 * Math.Max(0.01f, mult);
                                    Check(Math.Abs(iv - want) <= 1.0 + want * 1e-6, "interval " + iv + " vs " + want);
                                    next = now + iv;
                                    Check(next > now, "re-armed in the past");
                                }
                                break;
                            }
                    }
                    Check(lays <= (now - startedAt) / (long)(20 * 60000 * 0.01f) + 1, "more lays than the fastest allowed cadence");
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        private static Act[] GenRelay(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                RA kind = k < 40 ? RA.Tick : k < 52 ? RA.BigTick : k < 62 ? RA.Mother : k < 66 ? RA.Def : k < 78 ? RA.Clutch : k < 90 ? RA.Mine : k < 95 ? RA.Mult : RA.Move;
                a[i] = new Act { kind = (int)kind, a = r.Next(1 << 12), b = r.Next(1 << 12), f = r.Next(3) != 0 };
            }
            return a;
        }

        private static List<string> Relay(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenRelay(r, 30 + r.Next(170)); Cases++;
                if (RunRelay(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunRelay(t, seed, false) != null);
                fails.Add($"relay seed {seed}: {RunRelay(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ tables ════════════════════════
        private static List<string> Tables(int n, int seed0)
        {
            var fails = new List<string>();
            Action<string, Action> run = (name, act) =>
            {
                Cases++;
                try { act(); } catch (Exception e) { fails.Add("tables " + name + ": " + e.Message); }
            };

            // emergent spawn gate: exhaustive over the booleans, gridded over chance x multiplier x draw
            run("emergent", () =>
            {
                float[] chances = { 0f, 0.03f, 0.5f, 1f };
                float[] mults = { 0f, 0.5f, 1f, 3f };
                float[] draws = { 0f, 0.0299f, 0.03f, 0.0899f, 0.09f, 0.5f, 0.99999f, 1f };   // Random.value reaches 1.0
                foreach (bool en in new[] { false, true }) foreach (bool map in new[] { false, true }) foreach (bool van in new[] { false, true })
                            foreach (float c in chances) foreach (float m in mults) foreach (float u in draws)
                                    {
                                        Steps++;
                                        double p = c * m;
                                        bool spec = en && map && van && (p >= 1.0 ? true : p <= 0.0 ? false : u < p);
                                        // float product: compare through the same float expression the mod uses
                                        float pf = c * m;
                                        bool spec2 = en && map && van && (pf >= 1f ? true : pf <= 0f ? false : u < pf);
                                        bool got = RM_EmergentKernel.Fires(en, map, van, c, m, u);
                                        Check(got == spec2, $"Fires({en},{map},{van},{c},{m},{u}) = {got}, spec {spec2}");
                                        if (!en || !map || !van) Check(!got, "fired through a closed gate");
                                        if (c * m <= 0f) Check(!got, "fired at zero chance");
                                        if (c * m >= 1f && en && map && van) Check(got, "did not fire at certainty");
                                    }
            });

            // biome score
            run("biome", () =>
            {
                var r = new Random(seed0 + 7);
                for (int i = 0; i < n * 40; i++)
                {
                    Steps++;
                    float temp = (float)(r.NextDouble() * 90 - 10), rain = (float)(r.NextDouble() * 8000), elev = (float)(r.NextDouble() * 2000);
                    bool water = r.Next(8) == 0, mtn = r.Next(6) == 0, none = r.Next(30) == 0, en = r.Next(10) != 0;
                    float sc = RM_WebworkBiomeKernel.Score(en, none, water, temp, rain, elev, mtn);
                    if (!en) { Check(sc == 0f, "disabled worker scored " + sc); continue; }
                    if (none || water) { Check(sc == -100f, "water / no tile scored " + sc); continue; }
                    bool inBand = temp >= 30f && temp <= 60f && rain >= 1800f && elev <= 1000f && !mtn;
                    if (!inBand) { Check(sc == 0f, $"out of band scored {sc} (t {temp} r {rain} e {elev} m {mtn})"); continue; }
                    double spec = 28.0 + (temp - 30.0) * 1.2 + (rain - 1800.0) / 200.0;
                    Check(Math.Abs(sc - spec) < 1e-2, $"score {sc} spec {spec}");
                    Check(sc >= 28f, "in-band score below the base");
                    // monotone: hotter or wetter never scores lower
                    float hot = RM_WebworkBiomeKernel.Score(true, false, false, Math.Min(60f, temp + 1f), rain, elev, mtn);
                    float wet = RM_WebworkBiomeKernel.Score(true, false, false, temp, rain + 100f, elev, mtn);
                    Check(hot >= sc - 1e-3 && wet >= sc, "score not monotone in heat / rainfall");
                }
                // band edges (inclusive on both ends, wet floor inclusive, elevation ceiling inclusive)
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 30f, 1800f, 1000f, false) == 28f, "lower edge excluded");
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 60f, 1800f, 0f, false) > 28f, "upper heat edge excluded");
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 29.99f, 3000f, 0f, false) == 0f, "below band scored");
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 60.01f, 3000f, 0f, false) == 0f, "above band scored");
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 45f, 1799.9f, 0f, false) == 0f, "too dry scored");
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 45f, 3000f, 1000.1f, false) == 0f, "too high scored");
                // beaten by a vanilla biome only where it should be: the best in-band score is far above a typical vanilla 0..30 worker
                Check(RM_WebworkBiomeKernel.Score(true, false, false, 60f, 6000f, 0f, false) <= 28f + 36f + 21f + 1e-3, "score ceiling at the band corner");
            });

            // nest and site margins
            run("margins", () =>
            {
                var r = new Random(seed0 + 11);
                for (int i = 0; i < n * 40; i++)
                {
                    Steps++;
                    int mx = 100 + r.Next(250), mz = 100 + r.Next(250), x = r.Next(-3, mx + 3), z = r.Next(-3, mz + 3);
                    bool got = RM_EggRelayKernel.InBoundsWithMargin(x, z, mx, mz, 8);
                    bool spec = x >= 8 && z >= 8 && x <= mx - 9 && z <= mz - 9;
                    Check(got == spec, $"InBoundsWithMargin({x},{z}) on {mx}x{mz}");
                    int w = 15, h = 9, sx = r.Next(-3, mx + 3), sz = r.Next(-3, mz + 3);
                    bool gs = RM_UrravethKernel.SiteInMargin(sx, sz, sx + w - 1, sz + h - 1, mx, mz, 8);
                    bool ss = Enumerable.Range(sx, w).All(cx => cx >= 8 && cx < mx - 8) && Enumerable.Range(sz, h).All(cz => cz >= 8 && cz < mz - 8);
                    Check(gs == ss, $"SiteInMargin at {sx},{sz} on {mx}x{mz}");
                }
                Check(RM_EggRelayKernel.RingWantsMore(0, 2) && RM_EggRelayKernel.RingWantsMore(1, 2) && !RM_EggRelayKernel.RingWantsMore(2, 2), "ring want");
                Check(RM_EggRelayKernel.NeedsFallback(0) && !RM_EggRelayKernel.NeedsFallback(1), "fallback");
                Check(RM_EggRelayKernel.RichEnough(0.6f, 0.6f) && !RM_EggRelayKernel.RichEnough(0.59f, 0.6f), "rich soil edge");
            });

            // rounding, windows, intervals over the Mod Settings slider ranges
            run("settings-ranges", () =>
            {
                // urravethWarningHours 1..24, collapse multiplier 0..3, egg relay multiplier 0.1..3, front creep 0.25..4, thrixweave 0..40
                for (float hrs = 1f; hrs <= 24f; hrs += 0.25f)
                {
                    Steps++;
                    int wt = RM_UrravethKernel.WindowTicks(hrs);
                    Check(wt >= 250 && wt >= (int)Math.Round(hrs * 2500.0) - 1, "window " + wt + " at " + hrs + "h");
                    Check(wt >= RM_UrravethKernel.RareTicks, "window shorter than one rare tick: the countdown could collapse on its first step");
                    Check(RM_UrravethKernel.WindowTicks(hrs + 0.25f) >= wt, "window not monotone");
                }
                Check(RM_UrravethKernel.WindowTicks(0f) == 250 && RM_UrravethKernel.WindowTicks(-5f) == 250, "window floor");
                for (float m = 0.1f; m <= 3f; m += 0.1f)
                    for (float days = 20f; days <= 30f; days += 2.5f)
                    {
                        Steps++;
                        int iv = RM_EggRelayKernel.IntervalTicks(days, m);
                        Check(iv > 60000 * 20 * 0.1f * 0.99f, "relay interval too short at x" + m);
                        Check(RM_EggRelayKernel.IntervalTicks(days + 1f, m) >= iv && RM_EggRelayKernel.IntervalTicks(days, m + 0.1f) >= iv, "interval not monotone");
                    }
                Check(RM_EggRelayKernel.IntervalTicks(0f, 1f) == 1 && RM_EggRelayKernel.IntervalTicks(20f, 0f) == (int)Math.Round(20f * 60000f * 0.01f) && RM_EggRelayKernel.IntervalTicks(20f, -3f) == RM_EggRelayKernel.IntervalTicks(20f, 0f), "interval floors");
                for (float m = 0.25f; m <= 4f; m += 0.25f) { Steps++; Check(RM_EmergentKernel.ScaledInterval(60000, m) == (int)(60000 * m), "front interval x" + m); }
                foreach (int bi in new[] { 59999, 60001, 33333, 1234567 })
                    for (float m = 0.25f; m <= 4f; m += 0.25f) Check(RM_EmergentKernel.ScaledInterval(bi, m) == (int)(bi * m), $"front interval {bi} x{m}");
                Check(RM_EmergentKernel.ScaledInterval(60000, 0.25f) == 15000 && RM_EmergentKernel.ScaledInterval(60000, 4f) == 240000, "front interval ends");
                // examine ticks
                Check(RM_UrravethKernel.ExamineTicks(3000, true) == 3000 && RM_UrravethKernel.ExamineTicks(3000, false) == 6000 && RM_UrravethKernel.ExamineTicks(10, true) == 60 && RM_UrravethKernel.ExamineTicks(0, false) == 120, "examine ticks");
                Check(RM_UrravethKernel.WeaveDropped(8, true) == 8 && RM_UrravethKernel.WeaveDropped(0, true) == 0 && RM_UrravethKernel.WeaveDropped(8, false) == 0 && RM_UrravethKernel.WeaveDropped(-2, true) == 0, "weave dropped");
            });

            // RoundRandom: floor + (u < frac), mean equals the value; CollapseDamage within bounds across the slider
            run("round-random", () =>
            {
                var r = new Random(seed0 + 13);
                for (int i = 0; i < n * 40; i++)
                {
                    Steps++;
                    float f = (float)(r.NextDouble() * 120), u = (float)r.NextDouble();
                    int v = RM_UrravethKernel.RoundRandom(f, u);
                    Check(v == (int)Math.Floor(f) || v == (int)Math.Floor(f) + 1, "RoundRandom left the floor/ceil pair");
                    Check(RM_UrravethKernel.RoundRandom(f, 0.999999f) <= (int)Math.Ceiling(f), "RoundRandom above the ceiling");
                    Check(RM_UrravethKernel.RoundRandom((float)Math.Floor(f), u) == (int)Math.Floor(f), "an integer value rounds away from itself");
                    foreach (float m in new[] { 0f, 0.5f, 1f, 3f })
                    {
                        int roll = 15 + r.Next(16);
                        int d = RM_UrravethKernel.CollapseDamage(roll, m, u);
                        Check(d >= (int)Math.Floor(roll * m) && d <= (int)Math.Ceiling(roll * m), $"CollapseDamage({roll},{m}) = {d}");
                        if (m == 0f) Check(d == 0, "multiplier 0 still damages");
                    }
                }
                double sum = 0; int N = 20000; var rr = new Random(seed0 + 17);
                for (int i = 0; i < N; i++) sum += RM_UrravethKernel.RoundRandom(22.35f, (float)rr.NextDouble());
                Check(Math.Abs(sum / N - 22.35) < 0.02, "RoundRandom mean " + sum / N);
            });

            // Rand.Chance semantics
            run("chance", () =>
            {
                Check(RM_UrravethKernel.Chance(1f, 1f) && RM_UrravethKernel.Chance(1f, 0.999f) && RM_UrravethKernel.Chance(2f, 0.5f) && !RM_UrravethKernel.Chance(0f, 0f) && !RM_UrravethKernel.Chance(-1f, 0f), "chance ends");
                Check(RM_UrravethKernel.Chance(0.25f, 0.2499f) && !RM_UrravethKernel.Chance(0.25f, 0.25f), "chance edge");
                Check(RM_UrravethKernel.RollSite(true, 1f, 0.9f) && !RM_UrravethKernel.RollSite(false, 1f, 0f) && !RM_UrravethKernel.RollSite(true, 0f, 0f), "site roll");
            });

            // outline ring on the shipped 15 x 9 site (and a few others): inside the expanded rect, symmetric, non-empty, never filling the site
            run("outline", () =>
            {
                int[][] sites = { new[] { 40, 40, 15, 9 }, new[] { 10, 20, 15, 9 }, new[] { 8, 8, 9, 9 }, new[] { 0, 0, 21, 5 } };
                foreach (var st in sites)
                {
                    int minX = st[0], minZ = st[1], W = st[2], H = st[3];
                    int ring = 0, total = 0;
                    var cells = new HashSet<(int, int)>();
                    for (int x = minX - 2; x < minX + W + 2; x++)
                        for (int z = minZ - 2; z < minZ + H + 2; z++)
                        {
                            Steps++; total++;
                            bool on = RM_UrravethKernel.OutlineCell(x, z, minX, minZ, W, H);
                            if (on) { ring++; cells.Add((x, z)); }
                            // spec: normalised radius from the centre of the rect
                            double cx = minX + W / 2.0, cz = minZ + H / 2.0, a = W / 2.0 + 1, b = H / 2.0 + 1;
                            double rad = Math.Sqrt(Math.Pow((x + 0.5 - cx) / a, 2) + Math.Pow((z + 0.5 - cz) / b, 2));
                            bool band = Math.Abs(rad - 1.0) <= 0.09;
                            if (Math.Abs(Math.Abs(rad - 1.0) - 0.09) > 1e-4) Check(on == band, $"OutlineCell({x},{z}) on {W}x{H}: {on} spec radius {rad:F4}");
                        }
                    Check(ring > 0 && ring < total / 2, $"ring has {ring} of {total} cells");
                    foreach (var (x, z) in cells)
                    {
                        Check(cells.Contains((2 * minX + W - 1 - x, z)) && cells.Contains((x, 2 * minZ + H - 1 - z)), "outline not symmetric about the site centre at " + x + "," + z);
                        Check(x >= minX - 2 && x < minX + W + 2 && z >= minZ - 2 && z < minZ + H + 2, "outline cell outside the scanned rect");
                    }
                }
            });

            // neighbour / near / load tables
            run("geometry", () =>
            {
                var r = new Random(seed0 + 19);
                for (int i = 0; i < n * 40; i++)
                {
                    Steps++;
                    int ax = r.Next(0, 30), az = r.Next(0, 30), aw = 1 + r.Next(5), ah = 1 + r.Next(5), bx = r.Next(0, 30), bz = r.Next(0, 30), bw = 1 + r.Next(5), bh = 1 + r.Next(5);
                    bool got = RM_UrravethKernel.Adjacent(ax, az, ax + aw - 1, az + ah - 1, bx, bz, bx + bw - 1, bz + bh - 1);
                    bool spec = false;
                    for (int x = bx; x < bx + bw && !spec; x++) for (int z = bz; z < bz + bh && !spec; z++)
                            spec = x >= ax - 1 && x <= ax + aw && z >= az - 1 && z <= az + ah;
                    Check(got == spec, "Adjacent");
                    Check(got == RM_UrravethKernel.Adjacent(bx, bz, bx + bw - 1, bz + bh - 1, ax, az, ax + aw - 1, az + ah - 1), "Adjacent not symmetric");
                    int dx = r.Next(-20, 21), dz = r.Next(-20, 21), sx = 1 + r.Next(4), sz = 1 + r.Next(4);
                    bool near = RM_UrravethKernel.PawnNear(dx, dz, 10f, sx, sz);
                    double lim = 10.0 + Math.Max(sx, sz) / 2.0;
                    Check(near == ((double)dx * dx + (double)dz * dz <= lim * lim + 1e-9), $"PawnNear({dx},{dz}) size {sx}x{sz}");
                }
                for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++)
                    {
                        Check(RM_UrravethKernel.IsSupporter(a, b) == (a < b) && RM_UrravethKernel.IsSupported(a, b) == (a > b), "support direction");
                        Check(!(RM_UrravethKernel.IsSupporter(a, b) && RM_UrravethKernel.IsSupported(a, b)), "both supporter and supported");
                    }
                Check(RM_UrravethKernel.HeavilyDamaged(314, 900) && !RM_UrravethKernel.HeavilyDamaged(315, 900), "heavy-damage edge");
                Check(RM_UrravethKernel.StartsCreakingOnLoss(true, false, true) && !RM_UrravethKernel.StartsCreakingOnLoss(false, false, true) && !RM_UrravethKernel.StartsCreakingOnLoss(true, true, true) && !RM_UrravethKernel.StartsCreakingOnLoss(true, false, false), "start-on-loss table");
                Check(RM_UrravethKernel.Overloaded(2f, 2f) && !RM_UrravethKernel.Overloaded(1.99f, 2f), "overload edge");
                Check(RM_UrravethKernel.ExamineAllowed(true, true, false) && RM_UrravethKernel.ExamineAllowed(true, false, true) && !RM_UrravethKernel.ExamineAllowed(true, false, false) && !RM_UrravethKernel.ExamineAllowed(false, true, true), "examine allowed table");
                // CanOpenLastWrapping: every input is a necessary condition
                for (int m = 0; m < 64; m++)
                {
                    Steps++;
                    bool[] f = Enumerable.Range(0, 6).Select(bit => (m >> bit & 1) != 0).ToArray();
                    bool got = RM_UrravethKernel.CanOpenLastWrapping(f[0], !f[1], f[2], !f[3], f[4], f[5]);
                    Check(got == (f[0] && f[1] && f[2] && f[3] && f[4] && f[5]), "CanOpenLastWrapping table " + m);
                }
            });

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
                ("urraveth", () => Urraveth(N(5000), S(1))),
                ("relay", () => Relay(N(4000), S(1))),
                ("tables", () => Tables(Math.Max(1, N(100)), S(1))),
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
            if (only == null || only == "urraveth")
            {
                Console.WriteLine($"urraveth reached: creaks {Creaks} (by cascade {CascadeStarts}), settles {Settles}, collapses {Collapses}, unwatched holds {Unwatched}, completes {Completes} ({Gaps} with a chapter unread), all four chapters {FourChapters}, examines refused {Skipped}");
                if (!oneSeed.HasValue && scale >= 1 && (Creaks == 0 || CascadeStarts == 0 || Settles == 0 || Collapses == 0 || Unwatched == 0 || Completes == 0 || FourChapters == 0 || Skipped == 0)) { Console.WriteLine("FAIL urraveth fuzz never reached a path (blind)"); ok = false; }
            }
            if (only == null || only == "relay")
            {
                Console.WriteLine($"relay reached: lays {Lays}, dying-nest checks {Dying}");
                if (!oneSeed.HasValue && scale >= 1 && (Lays == 0 || Dying == 0)) { Console.WriteLine("FAIL relay fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"webwork fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
