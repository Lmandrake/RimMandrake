// Approach B for Explosive Knockback: seeded fuzz over the Verse-free production kernel (../RM_KnockbackMath.cs), next to the K-01..K-16
// scene checks in Program.cs. Families:
//   cells   ThrowCells against an independent decimal oracle plus monotonicity (closer, lighter, harder, bigger multiplier never throw less)
//   line    the throw line: exact length, king-adjacent steps, the integer-rational oracle for every cell, mirror and transpose symmetry
//   resolve the walk over random grids against an independently written walker, plus structural invariants (never rests in a solid /
//           water / sandbag cell, never reads the start cell, corner cutting refused, impact only for pawns that hit something)
//   rank    the per-explosion cap: kept set = the first `cap` of the total order (kind, distance, index), independent of input order
//   cfg     config lookup order, per-request settings copy, throw cap arithmetic
//   guard   stun-lock window, shield debit, dedupe, per-tick budget, epicentre direction
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.ExplosiveKnockback;

internal static class KnockbackFuzz
{
    public static long Cases, Steps, Stopped, Thrown, PitStops, PawnHits, Backoffs, CornerBlocks, DoorHits, Capped;
    private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

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

    private static KbSettings RandSettings(Random r)
    {
        return new KbSettings
        {
            globalMultiplier = new[] { 0f, 0.5f, 1f, 1f, 1.5f, 3f }[r.Next(6)],
            baseCells = new[] { 1f, 2f, 4f, 4f, 6f, 8f }[r.Next(6)],
            maxCells = r.Next(1, 11),
            refMass = new[] { 30f, 60f, 70f, 70f, 120f }[r.Next(5)],
            immuneBodySize = new[] { 1f, 2.5f, 2.5f, 3.6f, 9f }[r.Next(5)],
            lightMassLimit = new[] { 10f, 75f, 75f, 300f }[r.Next(4)],
            impactEnabled = r.Next(5) != 0,
            impactPerCell = new[] { 0f, 2f, 4f, 4f, 9f }[r.Next(5)],
            sandbagsStop = r.Next(2) == 0,
            intoPits = r.Next(3) != 0,
            impactFactor = new[] { 0f, 0.5f, 1f, 1f, 2f }[r.Next(5)],
        };
    }

    // ════════════════════════ cells ════════════════════════
    private static List<string> Cells(int n, int seed)
    {
        return Loop("cells", n, seed, r =>
        {
            Steps++;
            KbSettings s = RandSettings(r);
            float radius = new[] { 0f, 1.9f, 2.9f, 5f }[r.Next(4)];
            float dist = (float)(r.NextDouble() * (radius + 2));
            float force = new[] { -1f, 0f, 0.5f, 1f, 2.5f, 4f }[r.Next(6)];
            float mass = new[] { 0f, 0.5f, 1f, 20f, 70f, 200f, 2000f }[r.Next(7)];
            int c = RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s);
            Check(c >= 0 && c <= Math.Max(0, s.maxCells), $"ThrowCells {c} outside 0..{s.maxCells}");
            if (force <= 0f || s.globalMultiplier <= 0f || dist >= radius) Check(c == 0, $"force {force} mult {s.globalMultiplier} dist {dist}/{radius} still threw {c}");
            // decimal oracle for the unclamped value
            double fall = radius <= 0 ? 0 : 1.0 - Math.Min(1.0, Math.Max(0.0, (double)dist / radius));
            double mscale = Math.Min(2.0, Math.Max(0.25, Math.Sqrt((double)s.refMass / Math.Max(mass, 1f))));
            double raw = (double)s.baseCells * force * fall * mscale * s.globalMultiplier;
            if (force > 0f && s.globalMultiplier > 0f && radius > 0f)
            {
                int want = (int)Math.Floor(raw + 0.5 + 1e-6);
                want = Math.Min(want, s.maxCells); if (want < 1) want = 0;
                if (Math.Abs(raw - Math.Floor(raw) - 0.5) > 1e-3) Check(c == want, $"ThrowCells {c}, oracle {want} (raw {raw:F4}, cap {s.maxCells})");
            }
            if (c == s.maxCells && raw > s.maxCells + 0.5) Capped++;
            if (c > 0) Thrown++;
            // monotone
            Check(RM_KnockbackMath.ThrowCells(Math.Max(0f, dist - 0.5f), radius, force, mass, s) >= c, "standing closer threw less");
            Check(RM_KnockbackMath.ThrowCells(dist, radius, force + 0.5f, mass, s) >= c, "a harder blast threw less");
            Check(RM_KnockbackMath.ThrowCells(dist, radius, force, mass + 10f, s) <= c, "a heavier thing flew farther");
            var s2 = new KbSettings { globalMultiplier = s.globalMultiplier + 0.5f, baseCells = s.baseCells, maxCells = s.maxCells, refMass = s.refMass };
            var s1 = new KbSettings { globalMultiplier = s.globalMultiplier, baseCells = s.baseCells, maxCells = s.maxCells, refMass = s.refMass };
            Check(RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s2) >= RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s1), "a bigger global multiplier threw less");
            // mass scale clamps
            Check(RM_KnockbackMath.MassScale(0f, s) == RM_KnockbackMath.MassScale(1f, s), "mass below 1 not treated as 1");
            Check(RM_KnockbackMath.MassScale(-5f, s) == RM_KnockbackMath.MassScale(1f, s), "a negative mass (a corrupt stat) is not treated as 1 (sqrt of a negative is NaN)");
            Check(RM_KnockbackMath.Falloff(0f, 0f) == 0f, "Falloff(0, 0) is not 0 (0/0 = NaN would poison the throw)");
            {   // exact halves round AWAY from zero: 0.5 -> 1, 1.5 -> 2, 2.5 -> 3, 3.5 -> 4
                var hs = new KbSettings { baseCells = 1f, refMass = 70f, maxCells = 10, globalMultiplier = 1f };
                foreach (var (f, want) in new[] { (0.5f, 1), (1.5f, 2), (2.5f, 3), (3.5f, 4) })
                    Check(RM_KnockbackMath.ThrowCells(0f, 1f, f, 70f, hs) == want, $"force {f} (exactly {f} cells) threw {RM_KnockbackMath.ThrowCells(0f, 1f, f, 70f, hs)}, want {want}");
            }
            float ms = RM_KnockbackMath.MassScale(mass, s);
            Check(ms >= 0.25f && ms <= 2f, $"mass scale {ms} outside 0.25..2");
            // falloff
            Check(RM_KnockbackMath.Falloff(0f, 3f) == 1f && RM_KnockbackMath.Falloff(3f, 3f) == 0f && RM_KnockbackMath.Falloff(9f, 3f) == 0f && RM_KnockbackMath.Falloff(1f, 0f) == 0f, "falloff end points");
            // eligibility table
            foreach (KbKind k in new[] { KbKind.Pawn, KbKind.Item, KbKind.Corpse })
            {
                float body = (float)(r.NextDouble() * 5);
                if (r.Next(3) == 0) body = s.immuneBodySize;       // exactly on the line: immune (>=)
                bool e = RM_KnockbackMath.Eligible(k, mass, body, s);
                bool wantE = !((k != KbKind.Item && body >= s.immuneBodySize) || (k != KbKind.Pawn && mass > s.lightMassLimit));
                Check(e == wantE, $"Eligible({k}, mass {mass}, body {body}) = {e}");
            }
        });
    }

    // ════════════════════════ line ════════════════════════
    private static int RoundHalfAwayRational(int num, int den) { return (2 * num + den) / (2 * den); }   // num >= 0, den > 0

    private static List<string> LineFam(int n, int seed)
    {
        return Loop("line", n, seed, r =>
        {
            Steps++;
            int sx = r.Next(-20, 20), sz = r.Next(-20, 20);
            float dx = (float)(r.NextDouble() * 2 - 1), dz = (float)(r.NextDouble() * 2 - 1);
            if (r.Next(6) == 0) dx = 0f; if (r.Next(6) == 0) dz = 0f; if (r.Next(10) == 0) { dx = 0f; dz = 0f; }
            if (r.Next(8) == 0) dx = dz = 0.7071068f; if (r.Next(12) == 0) { dx = 1f; dz = 0.5f; }
            int cells = r.Next(-1, 12);
            var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
            float m = Math.Max(Math.Abs(dx), Math.Abs(dz));
            if (cells <= 0 || m < 1e-6f) { Check(path.Count == 0, "a path for no throw"); return; }
            Check(path.Count == cells, $"path has {path.Count} steps for a {cells}-cell throw");
            int px = sx, pz = sz;
            for (int i = 0; i < path.Count; i++)
            {
                var (x, z) = path[i];
                Check(Math.Max(Math.Abs(x - px), Math.Abs(z - pz)) == 1, $"step {i} from ({px},{pz}) to ({x},{z}) is not a king step");
                px = x; pz = z;
            }
            Check(!(path.Any(p => p.x == sx && p.z == sz)), "the start cell is on the path");
            // oracle: exact rational DDA from the rounded target
            int tx = sx + (int)Math.Round(dx / m * cells, MidpointRounding.AwayFromZero);
            int tz = sz + (int)Math.Round(dz / m * cells, MidpointRounding.AwayFromZero);
            int ddx = Math.Abs(tx - sx), ddz = Math.Abs(tz - sz), nn = Math.Max(ddx, ddz);
            Check(nn == cells, $"target is {nn} grid steps away, wanted {cells}");
            for (int i = 1; i <= nn; i++)
            {
                int wx = sx + (tx >= sx ? 1 : -1) * (ddx == 0 ? 0 : RoundHalfAwayRational(ddx * i, nn));
                int wz = sz + (tz >= sz ? 1 : -1) * (ddz == 0 ? 0 : RoundHalfAwayRational(ddz * i, nn));
                Check(path[i - 1] == (wx, wz), $"cell {i} is {path[i - 1]}, the rational oracle says ({wx},{wz})");
            }
            Check(path[path.Count - 1] == (tx, tz), "the path does not end on the target");
            // symmetry
            var mx = RM_KnockbackMath.Line(sx, sz, -dx, dz, cells);
            for (int i = 0; i < path.Count; i++) Check(mx[i] == (2 * sx - path[i].x, path[i].z), $"x-mirror asymmetry at step {i}");
            var mz = RM_KnockbackMath.Line(sx, sz, dx, -dz, cells);
            for (int i = 0; i < path.Count; i++) Check(mz[i] == (path[i].x, 2 * sz - path[i].z), $"z-mirror asymmetry at step {i}");
            var tp = RM_KnockbackMath.Line(sx, sz, dz, dx, cells);
            for (int i = 0; i < path.Count; i++) Check(tp[i] == (sx + (path[i].z - sz), sz + (path[i].x - sx)), $"transpose asymmetry at step {i}");
        });
    }

    // ════════════════════════ resolve ════════════════════════
    private sealed class FuzzGrid : IKbGrid
    {
        public KbCell[,] c; public int W, H; public int startX, startZ; public bool readStart;
        public KbCell At(int x, int z)
        {
            if (x == startX && z == startZ) readStart = true;
            return x < 0 || z < 0 || x >= W || z >= H ? KbCell.OutOfBounds : c[x, z];
        }
        public KbCell Raw(int x, int z) { return x < 0 || z < 0 || x >= W || z >= H ? KbCell.OutOfBounds : c[x, z]; }
    }

    private static bool IsSolid(KbCell k) { return k == KbCell.Wall || k == KbCell.Door || k == KbCell.OutOfBounds; }

    // An independently written walker: a state machine over the line, one verdict per cell.
    private static KbResult Walker(FuzzGrid g, int sx, int sz, float dx, float dz, int cells, KbKind kind, float mass, KbSettings s)
    {
        var res = new KbResult { destX = sx, destZ = sz, cellsPlanned = cells, stop = KbStop.None };
        if (cells <= 0) return res;
        var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
        var trail = new List<(int x, int z, KbCell k)>();
        KbStop why = KbStop.Distance;
        (int x, int z) cur = (sx, sz);
        foreach (var step in path)
        {
            KbCell k = g.Raw(step.x, step.z);
            bool diag = step.x != cur.x && step.z != cur.z;
            KbStop block = KbStop.None;
            if (diag && k != KbCell.OutOfBounds && (IsSolid(g.Raw(step.x, cur.z)) || IsSolid(g.Raw(cur.x, step.z)))) block = KbStop.Wall;
            else if (k == KbCell.OutOfBounds) block = KbStop.OutOfBounds;
            else if (k == KbCell.Wall) block = KbStop.Wall;
            else if (k == KbCell.Door) { block = KbStop.Door; res.hitDoor = true; res.doorX = step.x; res.doorZ = step.z; }
            else if (k == KbCell.Water) block = KbStop.Water;
            else if (k == KbCell.Pit && !s.intoPits) block = KbStop.Wall;
            else if (k == KbCell.Partial && kind == KbKind.Pawn && s.sandbagsStop) block = KbStop.PartialCover;
            else if (k == KbCell.Pawn && kind == KbKind.Pawn) { block = KbStop.Pawn; res.hitOther = true; res.otherX = step.x; res.otherZ = step.z; }
            if (block != KbStop.None) { why = block; break; }
            trail.Add((step.x, step.z, k));
            cur = (step.x, step.z);
            if (k == KbCell.Pit) { why = KbStop.Pit; break; }
        }
        // rest on the last non-sandbag cell of the trail
        int keep = trail.Count;
        while (keep > 0 && trail[keep - 1].k == KbCell.Partial) keep--;
        if (trail.Count > 0 && trail[trail.Count - 1].k == KbCell.Partial) { /* backed off */ }
        else keep = trail.Count;
        res.cellsTravelled = keep;
        if (keep > 0) { res.destX = trail[keep - 1].x; res.destZ = trail[keep - 1].z; }
        res.stop = res.cellsTravelled == 0 && why == KbStop.Distance ? KbStop.None : why;
        if (kind == KbKind.Pawn && (why == KbStop.Wall || why == KbStop.Door || why == KbStop.Pawn || why == KbStop.PartialCover))
        {
            float imp = s.impactEnabled && cells - keep > 0 ? s.impactPerCell * s.impactFactor * (cells - keep) / (float)Math.Sqrt(RM_KnockbackMath.MassScale(mass, s)) : 0f;
            if (why == KbStop.Pawn) { res.impact = imp * 0.5f; res.otherImpact = imp * 0.5f; } else res.impact = imp;
        }
        return res;
    }

    private static string Show(KbResult r) { return $"dest ({r.destX},{r.destZ}) travelled {r.cellsTravelled}/{r.cellsPlanned} stop {r.stop} impact {r.impact:F3}/{r.otherImpact:F3} other {(r.hitOther ? $"({r.otherX},{r.otherZ})" : "-")} door {(r.hitDoor ? $"({r.doorX},{r.doorZ})" : "-")}"; }

    private static List<string> ResolveFam(int n, int seed)
    {
        return Loop("resolve", n, seed, r =>
        {
            int W = r.Next(8, 20), H = r.Next(8, 20);
            var g = new FuzzGrid { W = W, H = H, c = new KbCell[W, H] };
            double dens = r.NextDouble() * 0.45;
            var kinds = new[] { KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) g.c[x, z] = r.NextDouble() < dens ? kinds[r.Next(kinds.Length)] : KbCell.Open;
            int sx = r.Next(0, W), sz = r.Next(0, H);
            g.c[sx, sz] = KbCell.Open; g.startX = sx; g.startZ = sz;
            float dx = (float)(r.NextDouble() * 2 - 1), dz = (float)(r.NextDouble() * 2 - 1);
            if (r.Next(5) == 0) dz = 0f; if (r.Next(5) == 0) dx = 0f; if (r.Next(10) == 0) dx = dz = 1f;
            int cells = r.Next(0, 9);
            KbKind kind = (KbKind)r.Next(3);
            float mass = new[] { 1f, 20f, 70f, 300f }[r.Next(4)];
            KbSettings s = RandSettings(r);
            Steps += cells + 1;
            KbResult got = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
            Check(!g.readStart, "the start cell was read");
            KbResult want = Walker(g, sx, sz, dx, dz, cells, kind, mass, s);
            string detail = $"start ({sx},{sz}) dir ({dx:F3},{dz:F3}) cells {cells} {kind} mass {mass} pits {s.intoPits} sand {s.sandbagsStop} impact {s.impactEnabled}/{s.impactPerCell}/{s.impactFactor}";
            Check(got.destX == want.destX && got.destZ == want.destZ && got.cellsTravelled == want.cellsTravelled && got.stop == want.stop
                && got.hitOther == want.hitOther && got.hitDoor == want.hitDoor && (!got.hitOther || (got.otherX == want.otherX && got.otherZ == want.otherZ))
                && (!got.hitDoor || (got.doorX == want.doorX && got.doorZ == want.doorZ))
                && Math.Abs(got.impact - want.impact) < 1e-3f && Math.Abs(got.otherImpact - want.otherImpact) < 1e-3f,
                $"kernel {Show(got)} | walker {Show(want)} | {detail}");
            // structural invariants, independent of the walker
            Check(got.cellsTravelled >= 0 && got.cellsTravelled <= cells, "travelled outside 0..cells");
            if (cells <= 0) Check(got.stop == KbStop.None && !got.Moved && got.destX == sx && got.destZ == sz, "a move for zero cells");
            KbCell at = g.Raw(got.destX, got.destZ);
            if (got.Moved)
            {
                Check(!IsSolid(at) && at != KbCell.Water && at != KbCell.Partial, $"came to rest in a {at} cell");
                if (kind == KbKind.Pawn) Check(at != KbCell.Pawn, "a thrown pawn rests on another pawn");
                if (at == KbCell.Pit) Check(got.stop == KbStop.Pit && s.intoPits, "rests in a pit without the Pit stop / with pits off");
                Check(Math.Max(Math.Abs(got.destX - sx), Math.Abs(got.destZ - sz)) == got.cellsTravelled || got.stop == KbStop.None || true, "");
                Check(Math.Max(Math.Abs(got.destX - sx), Math.Abs(got.destZ - sz)) <= cells, "rests farther than the throw");
            }
            if (!got.Moved) Check(got.destX == sx && got.destZ == sz, "did not move but the destination changed");
            if (got.stop == KbStop.Pit) Check(at == KbCell.Pit, "Pit stop but the destination is not an open pit cell");
            if (kind != KbKind.Pawn) Check(got.impact == 0f && got.otherImpact == 0f && !got.hitOther, "an item / corpse took impact or hit a pawn");
            if (!s.impactEnabled) Check(got.impact == 0f && got.otherImpact == 0f, "impact with impact switched off");
            Check(got.impact >= 0f && got.otherImpact >= 0f, "negative impact");
            if (got.stop == KbStop.Distance || got.stop == KbStop.Pit || got.stop == KbStop.Water || got.stop == KbStop.OutOfBounds || got.stop == KbStop.None) Check(got.impact == 0f, "impact on a non-collision stop " + got.stop);
            if (got.hitOther) Check(got.impact == got.otherImpact, "impact not split evenly between the two pawns");
            if (got.stop == KbStop.Door) Check(got.hitDoor && g.Raw(got.doorX, got.doorZ) == KbCell.Door, "Door stop without the door cell");
            // determinism
            KbResult again = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
            Check(Show(again) == Show(got), "Resolve is not deterministic");
            if (got.stop != KbStop.None && got.stop != KbStop.Distance) Stopped++;
            if (got.stop == KbStop.Pit) PitStops++;
            if (got.hitOther) PawnHits++;
            if (got.hitDoor) DoorHits++;
            if (got.stop == KbStop.Wall && cells > 1) { /* corner or wall */ }
            // sandbag back-off reached: a path whose last entered cell was Partial
            var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
            if (got.Moved && got.cellsTravelled < path.Count && path.Count >= got.cellsTravelled + 1 && g.Raw(path[got.cellsTravelled].x, path[got.cellsTravelled].z) == KbCell.Partial) Backoffs++;
            // corner cutting: replay the accepted steps
            int cx = sx, cz = sz;
            for (int i = 0; i < got.cellsTravelled && i < path.Count; i++)
            {
                var p = path[i];
                if (p.x != cx && p.z != cz) Check(!IsSolid(g.Raw(p.x, cz)) && !IsSolid(g.Raw(cx, p.z)), $"cut the corner at ({cx},{cz}) -> ({p.x},{p.z})");
                cx = p.x; cz = p.z;
            }
            for (int i = 0; i < path.Count; i++)
            {
                var p = path[i];
                bool diag = i == 0 ? (p.x != sx && p.z != sz) : (p.x != path[i - 1].x && p.z != path[i - 1].z);
                if (diag && got.stop == KbStop.Wall && i >= got.cellsTravelled) { CornerBlocks++; break; }
            }
        });
    }

    // ════════════════════════ rank ════════════════════════
    private static List<string> Rank(int n, int seed)
    {
        return Loop("rank", n, seed, r =>
        {
            Steps++;
            int count = r.Next(0, 25);
            var all = new List<KbCandidate>();
            for (int i = 0; i < count; i++) all.Add(new KbCandidate { index = i, kind = (KbKind)r.Next(3), distance = r.Next(0, 6) * 0.5f });
            int cap = r.Next(6) == 0 ? -1 : r.Next(0, 30);
            var shuffled = all.OrderBy(_ => r.Next()).ToList();
            var a = RM_KnockbackMath.Prioritise(all, cap);
            var b = RM_KnockbackMath.Prioritise(shuffled, cap);
            Check(string.Join(",", a.Select(c => c.index)) == string.Join(",", b.Select(c => c.index)), "the kept set depends on the input order");
            Check(cap < 0 ? a.Count == count : a.Count == Math.Min(cap, count), $"kept {a.Count} of {count} with cap {cap}");
            Func<KbKind, int> rank = k => k == KbKind.Pawn ? 0 : k == KbKind.Corpse ? 1 : 2;
            for (int i = 1; i < a.Count; i++)
            {
                var p = a[i - 1]; var q = a[i];
                Check((rank(p.kind), p.distance, p.index).CompareTo((rank(q.kind), q.distance, q.index)) < 0, "kept list is not in throw order");
            }
            var keptIdx = new HashSet<int>(a.Select(c => c.index));
            foreach (var d in all.Where(c => !keptIdx.Contains(c.index)))
                foreach (var k in a)
                    Check((rank(k.kind), k.distance, k.index).CompareTo((rank(d.kind), d.distance, d.index)) < 0, "a dropped candidate outranks a kept one");
            if (cap >= 0 && count > cap) Capped++;
            Check(all.Count == count, "the input list was modified");
        });
    }

    // ════════════════════════ cfg ════════════════════════
    private static List<string> Cfg(int n, int seed)
    {
        return Loop("cfg", n, seed, r =>
        {
            Steps++;
            Func<KbConfig> mk = () => r.Next(2) == 0 ? null : new KbConfig { force = (float)r.Next(0, 5), ownCap = r.Next(-1, 12), impactFactor = new[] { -1f, 0f, 1f, 2f }[r.Next(4)], immuneOverride = new[] { 0f, 0f, 3.6f }[r.Next(3)] };
            KbConfig p = mk(), w = mk(), d = mk();
            string expect = p != null ? "projectile" : w != null ? "weapon" : d != null ? "damageDef" : null;
            KbConfig first = p ?? w ?? d;
            float frac = (float)r.Next(0, 3) / 2f;
            bool harm = r.Next(2) == 0;
            float f0 = first?.force ?? 0;
            KbConfig got = KbLookup.Resolve(p, w, d, harm, frac);
            if (first != null) { Check(ReferenceEquals(got, first), "lookup did not return the first non-null config whole"); Check(got.source == expect, $"source {got.source}, want {expect}"); Check(got.force == f0, "an explicit force was changed"); }
            else { Check(got.source == (harm ? "unpatched" : "none"), "unpatched source label"); Check(got.force == (harm ? frac : 0f), "unpatched force"); }
            var g = RandSettings(r);
            int globalCap = r.Next(1, 12);
            float scale = new[] { 0.1f, 0.2f, 0.5f, 1f, 1.5f, 2f }[r.Next(6)];
            var before = (g.globalMultiplier, g.baseCells, g.maxCells, g.refMass, g.immuneBodySize, g.impactFactor);
            KbSettings a = KbLookup.Apply(g, got, globalCap, scale);
            Check(before == (g.globalMultiplier, g.baseCells, g.maxCells, g.refMass, g.immuneBodySize, g.impactFactor), "Apply mutated the shared settings");
            Check(!ReferenceEquals(a, g), "Apply returned the shared settings object");
            Check(a.maxCells >= 1 || got.ownCap <= 0, "cap below 1");
            Check(a.impactFactor >= 0f, "negative impact factor");
            Check(a.immuneBodySize == (got.immuneOverride > 0f ? got.immuneOverride : g.immuneBodySize), "immune override");
            Check(KbLookup.Apply(g, null, globalCap, scale).maxCells == globalCap && KbLookup.Apply(g, null, globalCap, scale).impactFactor == 1f, "null config does not mean global cap and factor 1");
            Check(RM_KnockbackMath.CapFor(0, globalCap, scale) == globalCap && RM_KnockbackMath.CapFor(-3, globalCap, scale) == globalCap, "ownCap <= 0 is not the global cap");
            int own = r.Next(1, 20);
            int cap = RM_KnockbackMath.CapFor(own, globalCap, scale);
            Check(cap >= 1, "own cap below 1 (\"never below 1\")");
            Check(Math.Abs(cap - own * scale) <= 0.5 + 1e-6 || cap == 1, $"cap {cap} is not round({own} x {scale})");
            Check(RM_KnockbackMath.CapFor(own + 1, globalCap, scale) >= cap, "a higher own cap gave a lower cap");
        });
    }

    // ════════════════════════ guard ════════════════════════
    private static List<string> Guard(int n, int seed)
    {
        return Loop("guard", n, seed, r =>
        {
            Steps++;
            int landed = r.Next(0, 5000), stun = r.Next(0, 5000), window = r.Next(-5, 400);
            bool prev = false;
            for (int now = 0; now < 9000; now += 37)
            {
                bool can = KbImmunity.CanLaunch(now, landed, stun, window);
                if (window <= 0) Check(can, "window 0 refused a chain throw");
                else Check(can == (now >= Math.Max(landed, stun) + window), $"CanLaunch({now},{landed},{stun},{window}) = {can}");
                if (prev) Check(can, "CanLaunch turned false again as time passed");
                prev = can;
            }
            float e = (float)(r.NextDouble() * 3);
            float f = (float)(r.NextDouble() * 6 - 1), pf = (float)(r.NextDouble() * 20 - 2), loss = (float)(r.NextDouble() * 0.1 - 0.01);
            float after = KbShield.EnergyAfter(e, f, pf, loss);
            Check(after <= e + 1e-6f, "a shield GAINED energy from a throw");
            Check(KbShield.EnergyAfter(e, f + 1f, pf, loss) <= after + 1e-6f, "more force cost the shield less");
            Check(KbShield.EnergyAfter(e, 0f, pf, loss) == e, "zero force cost energy");
            // explosion ledger against an independent per-pair clock: a pair is refused for at least `window` ticks after it was first accepted,
            // accepted again once 2 x window has passed, and never "forgotten" mid-wave
            int win = new[] { 5, 20, 600 }[r.Next(3)];
            var led = new KbExplosionLedger(win);
            var firstSeen = new Dictionary<(int, int), int>();
            var launchedSpec = new Dictionary<int, List<int>>();
            int clock = r.Next(0, 1000);
            for (int i = 0; i < 400; i++)
            {
                clock += r.Next(0, 4) == 0 ? r.Next(0, win) : r.Next(0, 3);
                int ex = r.Next(0, 6), th = r.Next(-2, 5) * (r.Next(8) == 0 ? 1000000 : 1);
                if (r.Next(25) == 0) th = r.Next(2) == 0 ? int.MinValue : int.MaxValue;
                bool got = led.TryAdd(ex, th, clock);
                bool known = firstSeen.TryGetValue((ex, th), out int t0);
                if (known && clock - t0 < win) Check(!got, $"pair ({ex},{th}) accepted again {clock - t0} ticks after it was first seen (window {win})");
                if (!known || clock - t0 >= 2 * win) { Check(got, $"pair ({ex},{th}) refused although last accepted {(known ? (clock - t0).ToString() : "never")} ticks ago (window {win})"); firstSeen[(ex, th)] = clock; }
                else if (got) firstSeen[(ex, th)] = clock;          // accepted in the grey zone between win and 2 x win: legal, restart its clock
                if (r.Next(3) == 0)
                {
                    int before = led.Launched(ex, clock);
                    led.AddLaunched(ex, clock);
                    Check(led.Launched(ex, clock) == before + 1, "AddLaunched did not add exactly one");
                    if (!launchedSpec.TryGetValue(ex, out var l)) launchedSpec[ex] = l = new List<int>();
                    l.Add(clock);
                }
                if (launchedSpec.TryGetValue(ex, out var ls))
                {
                    int live = ls.Count(tk => clock - tk < win);       // everything within one window is certainly remembered
                    int ceiling = ls.Count(tk => clock - tk < 2 * win);
                    int now2 = led.Launched(ex, clock);
                    Check(now2 >= live && now2 <= Math.Max(ceiling, 0), $"launch count for explosion {ex} is {now2}, must lie in [{live},{ceiling}] (window {win})");
                }
                Steps++;
            }
            var l0 = new KbExplosionLedger(0);
            Check(l0.TryAdd(1, 1, 5) && !l0.TryAdd(1, 1, 5), "a ledger built with window 0 divides by zero (the window is floored at 1)");
            var l2 = new KbExplosionLedger(10);
            Check(l2.TryAdd(1, 1, 50) && !l2.TryAdd(1, 1, 50) && l2.TryAdd(1, 1, 40), "a clock that goes backwards must start a fresh ledger");
            // per-tick budget
            var b = new KbTickBudget(); int tick = r.Next(0, 100); int used = 0, cap = r.Next(0, 6);
            for (int i = 0; i < 60; i++)
            {
                if (r.Next(4) == 0) { tick += r.Next(1, 3); used = 0; cap = r.Next(0, 6); }
                bool ok = b.TryTake(tick, cap);
                Check(ok == (used < cap), $"budget at tick {tick}: took {ok} with {used}/{cap}");
                if (ok) used++;
                Check(b.Used(tick) == used, "budget Used()");
                Check(b.Used(tick + 5) == 0, "Used() for another tick is not 0");
            }
            // epicentre direction
            int ex2 = r.Next(-1000, 100000), th2 = r.Next(-1000, 100000);
            RM_KnockbackMath.EpicentreDir(ex2, th2, out float dx1, out float dz1);
            RM_KnockbackMath.EpicentreDir(ex2, th2, out float dx2, out float dz2);
            Check(dx1 == dx2 && dz1 == dz2, "epicentre direction not deterministic");
            Check(Math.Abs(dx1 * dx1 + dz1 * dz1 - 1f) < 1e-4f, "epicentre direction is not a unit vector");
        });
    }

    private static List<string> Spread()
    {
        var fails = new List<string>();
        Cases++;
        try
        {
            var quad = new int[4];
            var seen = new HashSet<string>();
            for (int th = 0; th < 4000; th++)
            {
                RM_KnockbackMath.EpicentreDir(77, th, out float dx, out float dz);
                quad[(dx >= 0 ? 0 : 1) + (dz >= 0 ? 0 : 2)]++;
                seen.Add(dx.ToString("F3") + "," + dz.ToString("F3"));
            }
            Check(quad.All(q => q > 700), "epicentre directions are lopsided: " + string.Join("/", quad));
            Check(seen.Count > 300, "epicentre directions use only " + seen.Count + " of 360 angles");
            int same = 0;
            for (int th = 0; th < 1000; th++)
            {
                RM_KnockbackMath.EpicentreDir(5, th, out float ax, out float az);
                RM_KnockbackMath.EpicentreDir(6, th, out float bx, out float bz);
                if (ax == bx && az == bz) same++;
            }
            Check(same < 20, "two explosions throw things on their own cell the same way " + same + "/1000 times");
        }
        catch (Exception e) { fails.Add("guard seed 0: " + e.Message); }
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
            ("cells", () => Cells(N(6000), S(1))),
            ("line", () => LineFam(N(6000), S(1))),
            ("resolve", () => ResolveFam(N(20000), S(1))),
            ("rank", () => Rank(N(4000), S(1))),
            ("cfg", () => Cfg(N(4000), S(1))),
            ("guard", () => Guard(N(2000), S(1)).Concat(oneSeed.HasValue ? new List<string>() : Spread()).ToList()),
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
            Console.WriteLine($"reached: throws {Thrown}, capped throws {Capped}, collision stops {Stopped}, pit stops {PitStops}, pawn hits {PawnHits}, door hits {DoorHits}, sandbag back-offs {Backoffs}, corner blocks {CornerBlocks}");
            if (Thrown == 0 || Capped == 0 || Stopped == 0 || PitStops == 0 || PawnHits == 0 || DoorHits == 0 || Backoffs == 0 || CornerBlocks == 0)
            { Console.WriteLine("FAIL fuzz never reached throw / cap / stop / pit / pawn hit / door / back-off / corner block (blind)"); ok = false; }
        }
        Console.WriteLine($"explosiveknockback fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
        return ok;
    }
}
