// Approach B for Huge Things: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_FootprintKernel.cs):
//   math   rounding (half up, exhaustively around every .5), growth scale bounds / monotonicity, Scaled never zero for a real dimension
//   trunk  trunk and click rects over random extensions / growth / scale: root on the south edge and inside the width, young plants block
//          nothing, the trunk grows monotonically, the click area covers the trunk, MaxRect (re-link after load) covers every rect any
//          slider position can ask for
//   pawn   hitbox: contains the footprint, empty only when vanilla is right, monotone in the scale, side >= 1
//   plan   the blocker reconcile over random worlds: never leaves a blocker outside the wanted trunk, fills every cell it may,
//          never spawns on the root / out of the map / on a refused cell, idempotent; and a growth-and-settings lifecycle where the
//          blocker set equals the wanted trunk minus the root at every step
//   units  cell-eligibility table exhaustively, pack/unpack round trip, rect helpers
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class HugeThingsFuzz
    {
        public static long Cases, Steps, Spawned, Destroyed, Refused, Grown, EmptyTrunks, BigTrunks, Unions;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string S(RM_KRect r) { return r.IsEmpty ? "empty" : $"({r.minX},{r.minZ}){r.w}x{r.h}"; }

        private static List<string> Loop(string name, int n, int seed, Action<Random> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { one(new Random(seed + i)); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ math ════════════════════════
        private static List<string> Math_(int n, int seed)
        {
            var fails = Loop("math", n, seed, r =>
            {
                Steps++;
                // round half up, with the .5 boundaries probed exactly
                for (int k = -6; k <= 12; k++)
                {
                    Check(RM_FootprintKernel.RoundHalfUp(k + 0.5f) == k + 1, $"RoundHalfUp({k}.5) = {RM_FootprintKernel.RoundHalfUp(k + 0.5f)}, want {k + 1}");
                    Check(RM_FootprintKernel.RoundHalfUp(k + 0.49f) == k, $"RoundHalfUp({k}.49)");
                }
                float v = (float)(r.NextDouble() * 40 - 10);
                Check(Math.Abs(RM_FootprintKernel.RoundHalfUp(v) - v) <= 0.5f + 1e-4f, $"RoundHalfUp({v}) is more than half a cell away");
                // growth scale
                float vmin = (float)(r.NextDouble() * 6), vmax = r.Next(8) == 0 ? 0f : vmin + (float)(r.NextDouble() * 8);
                float prev = -1f;
                for (int i = 0; i <= 20; i++)
                {
                    float gs = RM_FootprintKernel.GrowthScale(vmin, vmax, i / 20f);
                    Check(gs >= 0f && gs <= 1f, $"GrowthScale {gs} outside 0..1 (min {vmin} max {vmax})");
                    Check(gs >= prev - 1e-6f, "GrowthScale fell as growth rose");
                    prev = gs;
                }
                Check(RM_FootprintKernel.GrowthScale(vmin, vmax, -5f) == RM_FootprintKernel.GrowthScale(vmin, vmax, 0f), "negative growth not clamped to 0");
                Check(RM_FootprintKernel.GrowthScale(vmin, vmax, 7f) == RM_FootprintKernel.GrowthScale(vmin, vmax, 1f), "growth above 1 not clamped to 1");
                if (vmax > vmin && vmin >= 0f)
                {
                    Check(Math.Abs(RM_FootprintKernel.GrowthScale(vmin, vmax, 0f) - vmin / vmax) < 1e-5f, $"a seedling is drawn at {RM_FootprintKernel.GrowthScale(vmin, vmax, 0f)}, the def says {vmin / vmax} of full size");
                    Check(Math.Abs(RM_FootprintKernel.GrowthScale(vmin, vmax, 0.5f) - (vmin + vmax) / 2f / vmax) < 1e-5f, "half-grown is not halfway between the drawn sizes");
                }
                if (vmax > 0f) Check(Math.Abs(RM_FootprintKernel.GrowthScale(vmin, vmax, 1f) - Math.Min(1f, 1f)) < 1e-5f || vmin > vmax, "fully grown is not full size");
                else Check(RM_FootprintKernel.GrowthScale(vmin, vmax, 0.3f) == 1f, "a plant with no drawn range is not full size");
                // scaled
                int full = r.Next(-2, 9);
                float sc = (float)(r.NextDouble() * 3);
                int sd = RM_FootprintKernel.Scaled(full, sc);
                if (full <= 0) Check(sd == 0, "a non-positive dimension scaled to " + sd);
                else { Check(sd >= 1, $"Scaled({full},{sc}) = {sd} < 1"); Check(RM_FootprintKernel.Scaled(full, sc + 0.25f) >= sd, "Scaled not monotone in the scale"); }
            });
            return fails;
        }

        // ════════════════════════ trunk ════════════════════════
        private static List<string> Trunk(int n, int seed)
        {
            return Loop("trunk", n, seed, r =>
            {
                int rx = r.Next(-50, 250), rz = r.Next(-50, 250);
                int tw = r.Next(1, 6), td = r.Next(0, 6), sh = r.Next(0, 10);
                float minG = new[] { 0f, 0.25f, 0.25f, 0.5f, 0.9f }[r.Next(5)];
                float vmin = (float)(r.NextDouble() * 5), vmax = vmin + 1f + (float)(r.NextDouble() * 6);
                float mult = new[] { 0.5f, 0.75f, 1f, 1f, 1.25f, 1.5f }[r.Next(6)];
                RM_KRect prevT = RM_KRect.Empty; bool wasNonEmpty = false;
                int depth = RM_FootprintKernel.DepthOf(tw, td), stem = RM_FootprintKernel.StemOf(tw, td, sh);
                Check(depth == (td > 0 ? td : tw) && stem == (sh > 0 ? sh : depth), "Depth/Stem fallbacks");
                RM_KRect max = RM_FootprintKernel.MaxRect(rx, rz, tw, td);
                for (int i = 0; i <= 20; i++)
                {
                    Steps++;
                    float g = i / 20f;
                    float gs = RM_FootprintKernel.GrowthScale(vmin, vmax, g);
                    RM_KRect t = RM_FootprintKernel.TrunkRect(rx, rz, tw, td, minG, gs, g, mult);
                    RM_KRect sel = RM_FootprintKernel.SelectRect(rx, rz, tw, td, sh, gs, mult);
                    if (g < minG) Check(t.IsEmpty, $"growth {g} < {minG} still blocks {S(t)}");
                    if (t.IsEmpty) { EmptyTrunks++; Check(!wasNonEmpty || true, ""); }
                    else
                    {
                        Check(t.Area >= 2, "a one-cell trunk was returned (the plant alone is one cell)");
                        Check(t.minZ == rz, $"trunk south edge {t.minZ} is not the root row {rz}");
                        Check(t.Contains(rx, rz), $"trunk {S(t)} does not contain the root cell ({rx},{rz}), so the plant cannot be reached from the south to cut it");
                        Check(!t.Contains(rx, rz - 1), "the cell south of the root is trunk");
                        Check(max.Contains(t.minX, t.minZ) && max.Contains(t.MaxX, t.MaxZ), $"MaxRect {S(max)} does not cover trunk {S(t)} (re-link after load would orphan blockers)");
                        Check(!sel.IsEmpty, "a trunk with no click area");
                        { float sc = gs * RM_FootprintKernel.ClampScale(mult); int wantH = Math.Max(RM_FootprintKernel.Scaled(depth, sc), RM_FootprintKernel.Scaled(stem, sc)); Check(sel.h == wantH, $"click area height {sel.h}, the taller of trunk depth and stem is {wantH}"); }
                        Check(sel.minX == t.minX && sel.w == t.w && sel.minZ == t.minZ && sel.h >= t.h, $"click area {S(sel)} does not cover trunk {S(t)}");
                        if (t.w >= 3 && t.h >= 3) BigTrunks++;
                        if (wasNonEmpty) Check(t.w >= prevT.w && t.h >= prevT.h, $"the trunk shrank while growing: {S(prevT)} -> {S(t)}");
                        prevT = t; wasNonEmpty = true;
                    }
                    if (!sel.IsEmpty) { Check(sel.Contains(rx, rz), "click area misses the root cell"); Check(sel.minZ == rz, "click area not anchored on the root row"); }
                    if (wasNonEmpty) Check(!t.IsEmpty, "the trunk vanished while growing");
                    // any settings value, slider or hand-edited file (up to 4x, or negative): the trunk stays inside MaxRect
                    float mm = (float)(r.NextDouble() * 5 - 0.5);
                    RM_KRect t2 = RM_FootprintKernel.TrunkRect(rx, rz, tw, td, 0f, gs, 1f, mm);
                    if (!t2.IsEmpty) Check(max.Contains(t2.minX, t2.minZ) && max.Contains(t2.MaxX, t2.MaxZ), $"MaxRect {S(max)} misses trunk {S(t2)} at settings value {mm}");
                }
            });
        }

        // ════════════════════════ pawn ════════════════════════
        private static List<string> Pawn(int n, int seed)
        {
            return Loop("pawn", n, seed, r =>
            {
                Steps++;
                float dx = (float)(r.NextDouble() * 14), dy = (float)(r.NextDouble() * 14), frac = 0.3f + (float)(r.NextDouble() * 0.6f);
                int fw = r.Next(1, 4), fh = r.Next(1, 4);
                var foot = new RM_KRect(r.Next(0, 100), r.Next(0, 100), fw, fh);
                int cx = foot.minX + r.Next(-2, fw + 2), cz = foot.minZ + r.Next(-2, fh + 2);
                RM_KRect prev = RM_KRect.Empty;
                foreach (float mult in new[] { 0.5f, 0.75f, 1f, 1.25f, 1.5f })
                {
                    Check(RM_FootprintKernel.HitboxSide(dx, frac, mult) >= 1, "hitbox side under 1");
                    RM_KRect h = RM_FootprintKernel.PawnHitbox(dx, dy, frac, mult, foot, cx, cz);
                    int w = RM_FootprintKernel.HitboxSide(dx, frac, mult), hh = RM_FootprintKernel.HitboxSide(dy, frac, mult);
                    if (w <= fw && hh <= fh && foot.Area <= 1) Check(h.IsEmpty, $"a body no bigger than a one-cell footprint returned hitbox {S(h)} (vanilla's cell selection is right there)");
                    if (h.IsEmpty) Check(w <= fw && hh <= fh && foot.Area <= 1, $"empty hitbox but body {w}x{hh} vs footprint {fw}x{fh}");
                    else
                    {
                        Check(h.minX <= foot.minX && h.minZ <= foot.minZ && h.MaxX >= foot.MaxX && h.MaxZ >= foot.MaxZ, $"hitbox {S(h)} does not contain the footprint {S(foot)}");
                        if (!(w <= fw && hh <= fh)) { Unions++; Check(h.w >= w && h.h >= hh, $"hitbox {S(h)} is smaller than the body {w}x{hh}"); }
                        else Check(h.minX == foot.minX && h.w == foot.w, "a body inside its footprint changed the footprint");
                    }
                    if (!prev.IsEmpty && !h.IsEmpty) Check(h.Area >= prev.Area, $"hitbox shrank as the scale rose: {S(prev)} -> {S(h)}");
                    if (!h.IsEmpty) prev = h;
                }
                Check(RM_FootprintKernel.HitboxSide(dx, frac, 50f) == RM_FootprintKernel.HitboxSide(dx, frac, RM_FootprintKernel.MaxTrunkScale), "a hand-edited hitbox scale of 50 is not clamped to the slider ceiling");
                Check(RM_FootprintKernel.HitboxSide(dx, frac, -3f) == 1, "a negative hitbox scale is not clamped to side 1");
                var a = new RM_KRect(r.Next(0, 30), r.Next(0, 30), r.Next(1, 6), r.Next(1, 6));
                var b = new RM_KRect(r.Next(0, 30), r.Next(0, 30), r.Next(1, 6), r.Next(1, 6));
                RM_KRect u = RM_FootprintKernel.Union(a, b);
                Check(u.Contains(a.minX, a.minZ) && u.Contains(a.MaxX, a.MaxZ) && u.Contains(b.minX, b.minZ) && u.Contains(b.MaxX, b.MaxZ), "Union does not contain its operands");
                RM_KRect u2 = RM_FootprintKernel.Union(b, a);
                Check(u.minX == u2.minX && u.minZ == u2.minZ && u.w == u2.w && u.h == u2.h, "Union not commutative");
                Check(u.Area <= (Math.Max(a.MaxX, b.MaxX) - Math.Min(a.minX, b.minX) + 1) * (Math.Max(a.MaxZ, b.MaxZ) - Math.Min(a.minZ, b.minZ) + 1), "Union bigger than the bounding box");
            });
        }

        // ════════════════════════ plan ════════════════════════
        private static List<string> Plan(int n, int seed)
        {
            return Loop("plan", n, seed, r =>
            {
                // --- one random reconcile ---
                int rx = r.Next(0, 30), rz = r.Next(0, 30);
                RM_KRect want = r.Next(5) == 0 ? RM_KRect.Empty : RM_FootprintKernel.NorthRect(rx, rz, r.Next(1, 7), r.Next(1, 7));
                int W = 34, H = 40;
                var refused = new HashSet<long>();
                for (int i = 0; i < r.Next(0, 12); i++) refused.Add(RM_FootprintKernel.Pack(rx + r.Next(-4, 5), rz + r.Next(0, 7)));
                var live = new List<long>();
                var seen = new HashSet<long>();
                for (int i = 0; i < r.Next(0, 14); i++)
                {
                    long k = RM_FootprintKernel.Pack(rx + r.Next(-6, 8), rz + r.Next(-3, 9));
                    if (seen.Add(k)) live.Add(k);
                }
                Func<int, int, bool> inb = (x, z) => x >= 0 && z >= 0 && x < W && z < H;
                Func<int, int, bool> takes = (x, z) => !refused.Contains(RM_FootprintKernel.Pack(x, z));
                RM_TrunkPlan plan = RM_FootprintKernel.Plan(want, rx, rz, live, inb, takes);
                Steps += live.Count + want.Area;
                Check(plan.destroyIndexes.Distinct().Count() == plan.destroyIndexes.Count && plan.destroyIndexes.All(i => i >= 0 && i < live.Count), "destroy indexes invalid or repeated");
                Check(plan.spawnCells.Distinct().Count() == plan.spawnCells.Count, "a cell is planned twice");
                var finalSet = new HashSet<long>(live.Where((k, i) => !plan.destroyIndexes.Contains(i)));
                foreach (long k in plan.spawnCells)
                {
                    int x = RM_FootprintKernel.PackedX(k), z = RM_FootprintKernel.PackedZ(k);
                    Check(want.Contains(x, z), $"spawn ({x},{z}) is outside the wanted trunk {S(want)}");
                    Check(!(x == rx && z == rz), "a blocker planned on the plant's own cell");
                    Check(inb(x, z), $"spawn ({x},{z}) is out of the map");
                    Check(takes(x, z), $"spawn ({x},{z}) is on a cell that refuses a trunk");
                    Check(!finalSet.Contains(k), $"spawn ({x},{z}) already has a blocker");
                    finalSet.Add(k); Spawned++;
                }
                Destroyed += plan.destroyIndexes.Count;
                foreach (long k in finalSet) Check(want.Contains(RM_FootprintKernel.PackedX(k), RM_FootprintKernel.PackedZ(k)), "a blocker survives outside the wanted trunk");
                for (int i = 0; i < live.Count; i++)
                {
                    bool inside = want.Contains(RM_FootprintKernel.PackedX(live[i]), RM_FootprintKernel.PackedZ(live[i]));
                    Check(plan.destroyIndexes.Contains(i) == !inside, $"blocker {i} {(inside ? "inside" : "outside")} the trunk was {(inside ? "destroyed" : "kept")}");
                }
                if (want.IsEmpty) { Check(plan.spawnCells.Count == 0, "spawns planned for an empty trunk"); Check(finalSet.Count == 0, "blockers left for an empty trunk"); }
                for (int z = want.minZ; !want.IsEmpty && z <= want.MaxZ; z++)
                    for (int x = want.minX; x <= want.MaxX; x++)
                    {
                        long k = RM_FootprintKernel.Pack(x, z);
                        bool need = !(x == rx && z == rz) && inb(x, z) && takes(x, z);
                        if (need) Check(finalSet.Contains(k), $"wanted cell ({x},{z}) was not filled");
                        else if (!(x == rx && z == rz) && !live.Contains(k)) { Check(!finalSet.Contains(k), $"a blocker appeared on unwanted cell ({x},{z})"); if (inb(x, z)) Refused++; }
                    }
                // idempotent
                var again = RM_FootprintKernel.Plan(want, rx, rz, finalSet.ToList(), inb, takes);
                Check(again.destroyIndexes.Count == 0 && again.spawnCells.Count == 0, "a second reconcile still had work to do");
            });
        }

        private static List<string> Lifecycle(int n, int seed)
        {
            return Loop("plan-life", n, seed, r =>
            {
                int rx = r.Next(10, 20), rz = r.Next(10, 20), tw = r.Next(1, 5), td = r.Next(0, 5);
                float minG = 0.25f, vmin = 3f, vmax = 9f;
                var blockers = new List<long>();
                float mult = 1f;
                for (int step = 0; step < 60; step++)
                {
                    Steps++;
                    float g = Math.Min(1f, step / 40f);
                    if (r.Next(8) == 0) { mult = new[] { 0.5f, 1f, 1.5f }[r.Next(3)]; Grown++; }
                    bool enabled = r.Next(15) != 0;
                    RM_KRect want = enabled ? RM_FootprintKernel.TrunkRect(rx, rz, tw, td, minG, RM_FootprintKernel.GrowthScale(vmin, vmax, g), g, mult) : RM_KRect.Empty;
                    var plan = RM_FootprintKernel.Plan(want, rx, rz, blockers, (x, z) => true, (x, z) => true);
                    foreach (int i in plan.destroyIndexes.OrderByDescending(i => i)) blockers.RemoveAt(i);
                    blockers.AddRange(plan.spawnCells);
                    var expect = new HashSet<long>();
                    for (int z = want.minZ; !want.IsEmpty && z <= want.MaxZ; z++) for (int x = want.minX; x <= want.MaxX; x++) if (!(x == rx && z == rz)) expect.Add(RM_FootprintKernel.Pack(x, z));
                    Check(expect.SetEquals(blockers), $"step {step}: blockers {blockers.Count} differ from the wanted trunk minus the root {expect.Count} ({S(want)})");
                }
            });
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units()
        {
            var fails = new List<string>();
            Action<string, Action> t = (name, a) => { Cases++; Steps++; try { a(); } catch (Exception e) { fails.Add("units seed 0: " + name + ": " + e.Message); } };
            t("cell eligibility table", () =>
            {
                for (int m = 0; m < 64; m++)
                {
                    bool[] f = Enumerable.Range(0, 6).Select(i => (m >> i & 1) == 1).ToArray();
                    bool got = RM_FootprintKernel.CellTakesTrunk(f[0], f[1], f[2], f[3], f[4], f[5]);
                    Check(got == (f[0] && !f[1] && !f[2] && !f[3] && !f[4] && !f[5]), "CellTakesTrunk " + string.Join("", f.Select(x => x ? 1 : 0)));
                }
            });
            t("pack round trip", () =>
            {
                foreach (int x in new[] { 0, 1, -1, 12345, -12345, int.MaxValue, int.MinValue })
                    foreach (int z in new[] { 0, 1, -1, 999, -999, int.MaxValue, int.MinValue })
                    {
                        long k = RM_FootprintKernel.Pack(x, z);
                        Check(RM_FootprintKernel.PackedX(k) == x && RM_FootprintKernel.PackedZ(k) == z, $"pack({x},{z}) did not round trip");
                    }
            });
            t("even widths lean east, odd centre", () =>
            {
                Check(RM_FootprintKernel.NorthRect(10, 10, 2, 2).minX == 10, "width 2 should start on the root column");
                Check(RM_FootprintKernel.NorthRect(10, 10, 3, 3).minX == 9, "width 3 should start one west");
                Check(RM_FootprintKernel.NorthRect(10, 10, 4, 4).minX == 9, "width 4 should start one west (leans east)");
                Check(RM_FootprintKernel.CentredRect(10, 10, 4, 4).minZ == 9, "even centred rects lean north");
            });
            t("rect helpers", () =>
            {
                Check(RM_KRect.Empty.IsEmpty && !RM_KRect.Empty.Contains(0, 0), "Empty contains a cell");
                Check(new RM_KRect(0, 0, 0, 5).IsEmpty && new RM_KRect(0, 0, 5, -1).IsEmpty, "zero/negative extent is not empty");
                Check(new RM_KRect(2, 3, 4, 5).MaxX == 5 && new RM_KRect(2, 3, 4, 5).MaxZ == 7 && new RM_KRect(2, 3, 4, 5).Area == 20, "rect corners");
                var e = new RM_KRect(2, 3, 4, 5).ExpandedBy(1);
                Check(e.minX == 1 && e.minZ == 2 && e.w == 6 && e.h == 7, "ExpandedBy");
            });
            t("a young plant of the shipped table blocks nothing, a grown one does", () =>
            {
                RM_KRect young = RM_FootprintKernel.TrunkRect(50, 50, 3, 3, 0.25f, RM_FootprintKernel.GrowthScale(5.14f, 9f, 0.15f), 0.15f, 1f);
                RM_KRect half = RM_FootprintKernel.TrunkRect(50, 50, 3, 3, 0.25f, RM_FootprintKernel.GrowthScale(5.14f, 9f, 0.5f), 0.5f, 1f);
                RM_KRect full = RM_FootprintKernel.TrunkRect(50, 50, 3, 3, 0.25f, 1f, 1f, 1f);
                Check(young.IsEmpty, "a 15% grown plant blocks");
                Check(half.w == 2 && half.h == 2 && half.minX == 50, "the half-grown 3x3 trunk is not 2x2 at x=50: " + S(half));
                Check(full.w == 3 && full.h == 3 && full.minX == 49, "the full 3x3 trunk is not 3x3 at x=49: " + S(full));
            });
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int Sd(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("math", () => Math_(N(3000), Sd(1))),
                ("trunk", () => Trunk(N(4000), Sd(1))),
                ("pawn", () => Pawn(N(3000), Sd(1))),
                ("plan", () => Plan(N(6000), Sd(1)).Concat(Lifecycle(N(1500), Sd(1))).ToList()),
                ("units", () => Units()),
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
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: spawned {Spawned}, destroyed {Destroyed}, refused cells {Refused}, empty trunks {EmptyTrunks}, big trunks {BigTrunks}, hitbox unions {Unions}, scale changes {Grown}");
                if (Spawned == 0 || Destroyed == 0 || Refused == 0 || EmptyTrunks == 0 || BigTrunks == 0 || Unions == 0 || Grown == 0) { Console.WriteLine("FAIL fuzz never reached spawn / destroy / refusal / empty / big trunk / union / scale change (blind)"); ok = false; }
            }
            Console.WriteLine($"hugethings fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
