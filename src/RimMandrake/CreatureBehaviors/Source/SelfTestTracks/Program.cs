// Selftest for FOOTPRINT_TRACK_GRID_1 (the footprint grid, mandrake.rm.creaturebehaviors).
//
// REAL, compiled straight from production source: RM_TrackPool — the cap, the
// eviction order (small animals, then the rest, then the oldest protected),
// overwrite on re-step, ClearCell/ClearRect, resize, the downwind sweep order,
// the classification every pawn step goes through, and the packed save format.
//
// Item criteria this proves offline:
//   1. 6,000+ steps on a surface leave exactly the cap in records; humanlike
//      and bs >= 1.5 records survive a flood of small-animal records.
//   3. save/load round-trips byte-identical (ToBytes -> FromBytes -> ToBytes).
//   2 (in part). Classify has no visibility input, so an invisible pawn is
//      recorded exactly like a seen one — asserted on the signature, below.
// NOT covered (needs a live map): the Harmony postfix firing, the section
// layer drawing, "no Thing count change" (the pool holds no Things by type —
// asserted structurally below), and the biomes' XML + eraser wiring.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace RimMandrake.CreatureBehaviors.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new List<string>();
        private static readonly List<string> Fail = new List<string>();

        private static readonly byte SmallAnimal = RM_TrackPool.Classify(false, false, true, 0.3f, false, 0f);
        private static readonly byte MediumAnimal = RM_TrackPool.Classify(false, false, true, 1.0f, false, 90f);
        private static readonly byte Human = RM_TrackPool.Classify(true, false, false, 1.0f, false, 180f);
        private static readonly byte LargeAnimal = RM_TrackPool.Classify(false, false, true, 1.5f, false, 270f);

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
            }
            catch (Exception e)
            {
                Fail.Add(name + ": " + e.Message);
            }
        }

        private static void Check(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static int Main()
        {
            Case("classification: tiers", () =>
            {
                Check(RM_TrackPool.TierOf(SmallAnimal) == 0, "small animal not tier 0");
                Check(RM_TrackPool.TierOf(MediumAnimal) == 1, "medium animal not tier 1");
                Check(RM_TrackPool.TierOf(Human) == 2, "humanlike not protected");
                Check(RM_TrackPool.TierOf(LargeAnimal) == 2, "bs 1.5 animal not protected");
                Check(RM_TrackPool.TierOf(RM_TrackPool.Classify(false, false, true, 1.49f, false, 0f)) == 1, "bs 1.49 protected");
                Check(RM_TrackPool.TierOf(RM_TrackPool.Classify(true, false, false, 0.2f, false, 0f)) == 2, "small humanlike (a child) not protected");
                Check(RM_TrackPool.TierOf(RM_TrackPool.Classify(false, true, false, 0.3f, false, 0f)) == 1, "small mech should be tier 1, not small-animal tier");
            });

            Case("classification: direction, drag, unpack", () =>
            {
                Check(RM_TrackPool.QuantizeDirection(0f) == 0, "0deg");
                Check(RM_TrackPool.QuantizeDirection(90f) == 2, "90deg");
                Check(RM_TrackPool.QuantizeDirection(225f) == 5, "225deg");
                Check(RM_TrackPool.QuantizeDirection(359f) == 0, "359deg");
                Check(RM_TrackPool.QuantizeDirection(-45f) == 7, "-45deg");
                var r = new RM_TrackRecord { bits = RM_TrackPool.Classify(true, false, false, 1f, true, 135f) };
                Check(r.Drag, "crawler not drag");
                Check(r.Direction == 3 && Math.Abs(r.Angle - 135f) < 0.01f, "angle round-trip");
                Check(r.Source == RM_TrackSource.Humanlike && r.Size == RM_TrackSize.Medium, "unpack source/size");
            });

            Case("criterion 2: no visibility input exists to filter on", () =>
            {
                MethodInfo m = typeof(RM_TrackPool).GetMethod("Classify");
                string[] names = m.GetParameters().Select(p => p.Name.ToLowerInvariant()).ToArray();
                Check(!names.Any(n => n.Contains("visib") || n.Contains("invis") || n.Contains("seen")),
                    "Classify grew a visibility parameter: " + string.Join(",", names));
            });

            Case("criterion 1: 7,000 steps on distinct cells leave exactly the cap (6,000)", () =>
            {
                var pool = new RM_TrackPool(200, 200, RM_TrackPool.DefaultCapacity);
                for (int i = 0; i < 7000; i++) pool.Write(i, i, MediumAnimal, 0);
                Check(pool.Count == 6000, "count " + pool.Count);
                // The oldest 1,000 are the ones that went.
                Check(!pool.Has(0) && !pool.Has(999) && pool.Has(1000) && pool.Has(6999), "evicted wrong records (age)");
            });

            Case("criterion 1: humanlike + bs>=1.5 survive a 30,000-step small-animal flood", () =>
            {
                var pool = new RM_TrackPool(250, 250, RM_TrackPool.DefaultCapacity);
                int cell = 0, tick = 0;
                var protectedCells = new List<int>();
                for (int i = 0; i < 400; i++) { pool.Write(cell, tick++, Human, 1); protectedCells.Add(cell++); }
                for (int i = 0; i < 400; i++) { pool.Write(cell, tick++, LargeAnimal, 2); protectedCells.Add(cell++); }
                for (int i = 0; i < 30000; i++) pool.Write(cell++, tick++, SmallAnimal, 3);
                Check(pool.Count == 6000, "count " + pool.Count);
                Check(protectedCells.All(pool.Has), "a protected print was evicted");
                Check(pool.CountTier(2) == 800, "protected count " + pool.CountTier(2));
            });

            Case("eviction order: small animals, then other, then oldest protected", () =>
            {
                var pool = new RM_TrackPool(50, 50, 6);
                pool.Write(0, 0, Human, 0);        // protected, oldest
                pool.Write(1, 1, MediumAnimal, 0); // tier 1
                pool.Write(2, 2, SmallAnimal, 0);  // tier 0
                pool.Write(3, 3, Human, 0);
                pool.Write(4, 4, MediumAnimal, 0);
                pool.Write(5, 5, SmallAnimal, 0);
                int e1 = pool.Write(10, 10, Human, 0);
                int e2 = pool.Write(11, 11, Human, 0);
                int e3 = pool.Write(12, 12, Human, 0);
                int e4 = pool.Write(13, 13, Human, 0);
                int e5 = pool.Write(14, 14, Human, 0);
                Check(e1 == 2 && e2 == 5, "small animals not first: " + e1 + "," + e2);
                Check(e3 == 1 && e4 == 4, "tier-1 not next, oldest first: " + e3 + "," + e4);
                Check(e5 == 0, "oldest protected not last resort: " + e5);
                Check(pool.Has(3) && pool.Count == 6, "recent humanlike lost");
            });

            Case("re-step overwrites in place and becomes newest; stale queue stays bounded", () =>
            {
                var pool = new RM_TrackPool(50, 50, 100);
                pool.Write(7, 1, SmallAnimal, 0);
                pool.Write(7, 2, Human, 4);
                Check(pool.Count == 1, "overwrite added a record");
                Check(pool.TryGet(7, out RM_TrackRecord r) && r.tick == 2 && r.style == 4 && r.Source == RM_TrackSource.Humanlike, "overwrite lost");
                for (int i = 0; i < 100000; i++) pool.Write(i % 20, i, i % 2 == 0 ? SmallAnimal : Human, 0);
                Check(pool.Count == 20, "count " + pool.Count);
                Check(pool.QueuedEntries <= 2 * pool.Capacity + 64 + 1, "queue grew unbounded: " + pool.QueuedEntries);
                // Re-stepping refreshes age: cell 0 written last as tier-0 must not go before an older tier-0.
                var p2 = new RM_TrackPool(10, 10, 2);
                p2.Write(0, 0, SmallAnimal, 0);
                p2.Write(1, 1, SmallAnimal, 0);
                p2.Write(0, 2, SmallAnimal, 0);
                int ev = p2.Write(2, 3, SmallAnimal, 0);
                Check(ev == 1, "re-stepped cell aged wrong, evicted " + ev);
            });

            Case("ClearCell / ClearRect / ClearAll", () =>
            {
                var pool = new RM_TrackPool(20, 20, 400);
                for (int i = 0; i < 400; i++) pool.Write(i, i, MediumAnimal, 0);
                Check(pool.Clear(pool.CellIndex(3, 3)) && !pool.Has(pool.CellIndex(3, 3)), "ClearCell");
                Check(!pool.Clear(pool.CellIndex(3, 3)), "double clear reported true");
                var seen = new List<int>();
                int n = pool.ClearRect(-5, -5, 4, 4, seen.Add);
                Check(n == 24 && seen.Count == 24, "ClearRect cleared " + n);
                Check(pool.Count == 400 - 25, "count " + pool.Count);
                // Freed slots are reusable without evicting.
                for (int i = 0; i < 25; i++) Check(pool.Write(pool.CellIndex(i % 5, i / 5), 1000 + i, Human, 0) == -1, "evicted while slots were free");
                pool.ClearAll();
                Check(pool.Count == 0 && pool.QueuedEntries == 0, "ClearAll");
            });

            Case("resize down evicts by the rule; up keeps everything", () =>
            {
                var pool = new RM_TrackPool(100, 100, 3000);
                for (int i = 0; i < 100; i++) pool.Write(i, i, Human, 0);
                for (int i = 100; i < 3000; i++) pool.Write(i, i, SmallAnimal, 0);
                pool.Resize(1000);
                Check(pool.Count == 1000 && pool.Capacity == 1000, "count " + pool.Count);
                Check(Enumerable.Range(0, 100).All(pool.Has), "resize evicted a humanlike");
                Check(pool.Has(2999) && !pool.Has(100), "resize kept old small prints over new");
                pool.Resize(5000);
                Check(pool.Count == 1000, "resize up lost records");
            });

            Case("downwind sweep order: upwind edge first, every cell once, deterministic", () =>
            {
                int[] east = RM_TrackPool.SweepOrder(30, 20, 90f);
                Check(east.Length == 600 && east.Distinct().Count() == 600, "not every cell once");
                Check(Enumerable.Range(0, 20).All(k => east[k] % 30 == 0), "wind toward east must start at x=0");
                Check(Enumerable.Range(580, 20).All(k => east[k] % 30 == 29), "wind toward east must end at x=29");
                int[] south = RM_TrackPool.SweepOrder(30, 20, 180f);
                Check(Enumerable.Range(0, 30).All(k => south[k] / 30 == 19), "wind toward south must start at the north edge");
                int[] diag = RM_TrackPool.SweepOrder(30, 20, 45f);
                Check(diag[0] == 0 && diag[599] == 599, "wind toward NE must run SW corner -> NE corner");
                Check(RM_TrackPool.SweepOrder(30, 20, 45f).SequenceEqual(diag), "sweep order not deterministic");
                // Monotone projection along the order.
                double rad = 45 * Math.PI / 180;
                double prev = double.MinValue;
                foreach (int c in diag)
                {
                    double p = Math.Round((c % 30) * Math.Sin(rad) + (c / 30) * Math.Cos(rad), 6);
                    Check(p >= prev, "projection went backwards");
                    prev = p;
                }
            });

            Case("criterion 3: save -> load -> save is byte-identical (after evictions, clears, overwrites)", () =>
            {
                var pool = new RM_TrackPool(120, 90, 2000);
                var rng = new Random(12345);
                byte[] kinds = { SmallAnimal, MediumAnimal, Human, LargeAnimal };
                for (int i = 0; i < 9000; i++)
                {
                    pool.Write(rng.Next(120 * 90), i, kinds[rng.Next(4)], (ushort)rng.Next(5));
                    if (i % 97 == 0) pool.Clear(rng.Next(120 * 90));
                }
                byte[] a = pool.ToBytes();
                RM_TrackPool loaded = RM_TrackPool.FromBytes(a, 120, 90, 0, out string err);
                Check(loaded != null, "load failed: " + err);
                byte[] b = loaded.ToBytes();
                Check(a.SequenceEqual(b), "bytes differ: " + a.Length + " vs " + b.Length);
                Check(loaded.Count == pool.Count && loaded.Capacity == pool.Capacity, "count/capacity differ");
                // Byte equality alone would pass a format that drops a field on BOTH saves.
                List<RM_TrackRecord> ra = pool.RecordsOldestFirst(), rb = loaded.RecordsOldestFirst();
                for (int i = 0; i < ra.Count; i++)
                {
                    Check(ra[i].cell == rb[i].cell && ra[i].tick == rb[i].tick && ra[i].bits == rb[i].bits && ra[i].style == rb[i].style,
                        "record " + i + " changed in the round trip");
                }
                Check(ra.Any(r => r.style != 0), "test data has no non-zero style (probe would be blind)");
                // And the loaded pool evicts the same cell next.
                int e1 = pool.Write(120 * 90 - 1, 99999, Human, 0);
                int e2 = loaded.Write(120 * 90 - 1, 99999, Human, 0);
                Check(e1 == e2, "eviction order not restored: " + e1 + " vs " + e2);
                Check(pool.ToBytes().SequenceEqual(loaded.ToBytes()), "diverged after one more write");
            });

            Case("load refuses a wrong-size map and junk without throwing", () =>
            {
                var pool = new RM_TrackPool(10, 10, 50);
                pool.Write(5, 5, Human, 0);
                byte[] a = pool.ToBytes();
                Check(RM_TrackPool.FromBytes(a, 11, 10, 0, out string e1) == null && e1 != null, "accepted wrong size");
                Check(RM_TrackPool.FromBytes(new byte[3], 10, 10, 0, out string e2) == null && e2 != null, "accepted junk");
                Check(RM_TrackPool.FromBytes(a.Take(a.Length - 4).ToArray(), 10, 10, 0, out string e3) == null && e3 != null, "accepted truncated");
                RM_TrackPool capped = RM_TrackPool.FromBytes(a, 10, 10, 1, out string e4);
                Check(capped != null && capped.Capacity == 1 && capped.Count == 1, "capacity override");
            });

            Case("no Thing is ever held: the pool's fields are value arrays only", () =>
            {
                foreach (FieldInfo f in typeof(RM_TrackPool).GetFields(BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public))
                {
                    Type t = f.FieldType;
                    bool ok = t.IsPrimitive || (t.IsArray && t.GetElementType().IsPrimitive) || t == typeof(Queue<long>[]);
                    Check(ok, "field " + f.Name + " is " + t.Name);
                }
            });

            Case("performance: 200,000 steps on a full 250x250 pool", () =>
            {
                var pool = new RM_TrackPool(250, 250, RM_TrackPool.DefaultCapacity);
                var rng = new Random(7);
                byte[] kinds = { SmallAnimal, MediumAnimal, Human, LargeAnimal };
                var sw = System.Diagnostics.Stopwatch.StartNew();
                for (int i = 0; i < 200000; i++) pool.Write(rng.Next(62500), i, kinds[rng.Next(4)], 0);
                sw.Stop();
                Check(pool.Count == 6000, "count " + pool.Count);
                Check(sw.ElapsedMilliseconds < 3000, "too slow: " + sw.ElapsedMilliseconds + " ms");
            });

            foreach (string p in Pass) Console.WriteLine("PASS  " + p);
            foreach (string f in Fail) Console.WriteLine("FAIL  " + f);
            Console.WriteLine((Fail.Count == 0 ? "OK" : "FAILED") + " " + Pass.Count + "/" + (Pass.Count + Fail.Count));
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
