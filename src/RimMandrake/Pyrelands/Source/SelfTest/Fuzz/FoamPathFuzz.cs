using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands.Fuzz
{
    // Family `foam`: the firefoam sprayer carrier (RM_FoamPathKernel, bar firefoam_sprayer_reaches_the_fruit).
    //
    // The range of situations. Varied: the grid's fire layout (none; a ring around the fruit 1-4 cells thick, whole or with a
    // gap; a burn band across the way; scattered fire at 0-40 % of cells; fire only away from the path), walls that block the
    // sprayer's line of sight (0-4 segments), the carrier's start and the fruit's place, the path's shape (the shortest path
    // round the walls, through fire), the sprayer's range (the shipped 9.9, and 3-15), the miss scatter (within the verb's
    // forcedMissRadius 1.5), fire spread per tick (0 to 0.02 per burning neighbour), and the gate's seven inputs (all 128).
    // Left out, because the engine owns them and Stage 6 reads them live: RimWorld's own fire spread and burn-out, the
    // pathfinder's fire cost and re-paths, other pawns in the way, the job driver's own toils.
    // Checks:
    //   pick   every PickTarget answer is a burning, hittable cell in the way; when any burning hittable cell is in the way an
    //          answer is given (the bar's red: a carrier with fire in its way that never foams); the answer is the first such
    //          cell in reading order; no fire in the way gives no answer, however much burns elsewhere.
    //   gate   only the one input row foams.
    //   walk   the bar's scene: a carrier walks to fruit inside a burning ring, stopping to foam (warmup 36 ticks, cooldown 210:
    //          the shipped 0.6 s and 3.5 s), and must reach the fruit, lay foam, and never stand on a burning cell. Control: the
    //          same walk with the switch off must stand on a burning cell whenever its path crosses fire (the walk can see a no).
    internal static class FoamPathFuzz
    {
        private const float ShippedRange = 9.9f;     // FirefoamSprayer.xml <range>
        private const float FoamRadius = 2.5f;       // RM_FE_Bullet_FirefoamSplash <explosionRadius>
        private const float MissRadius = 1.5f;       // FirefoamSprayer.xml <forcedMissRadius>
        private const int WarmupTicks = 36;          // <warmupTime>0.6</warmupTime> s x 60
        private const int CooldownTicks = 210;       // RangedWeapon_Cooldown 3.5 s x 60
        private const int TicksPerCell = 13;
        // The ruled look-ahead, pinned here and NOT read from the kernel (a planted LookAheadCells = 1 stayed green while the
        // oracle read the kernel's own constant): vanilla's danger read of a new path is 20 cells (Pawn_PathFollower.PatherTick).
        private const int RuledLookAhead = 20;         // MoveSpeed 4.6 cells/s at 60 ticks/s, rounded

        public static int Picks, PickAnswers, PickNone, WalkCases, ControlCrossings, CarrierCasts;
        public static int WorstSpreadExposure;
        public static double WorstSpreadRate;

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private sealed class Grid
        {
            public int W, H;
            public bool[,] fire, wall, foam;
            public Grid(int w, int h) { W = w; H = h; fire = new bool[w, h]; wall = new bool[w, h]; foam = new bool[w, h]; }
            public bool In(int x, int z) => x >= 0 && z >= 0 && x < W && z < H;
            public bool Burning(int x, int z) => In(x, z) && fire[x, z];
            public bool Los(int x0, int z0, int x1, int z1)
            {
                int dx = Math.Abs(x1 - x0), dz = Math.Abs(z1 - z0), sx = x0 < x1 ? 1 : -1, sz = z0 < z1 ? 1 : -1, err = dx - dz;
                int x = x0, z = z0;
                while (true)
                {
                    if ((x != x0 || z != z0) && (x != x1 || z != z1) && wall[x, z]) return false;
                    if (x == x1 && z == z1) return true;
                    int e2 = 2 * err;
                    if (e2 > -dz) { err -= dz; x += sx; }
                    if (e2 < dx) { err += dx; z += sz; }
                }
            }
            public Func<int, int, bool> CanHitFrom(int px, int pz, float range) =>
                (x, z) => In(x, z) && !wall[x, z] && (x - px) * (x - px) + (z - pz) * (z - pz) <= range * range && Los(px, pz, x, z);
        }

        /// <summary>Shortest 8-way path over non-wall cells (fire allowed), start excluded, end included; null when none.</summary>
        private static List<(int x, int z)> Path(Grid g, int sx, int sz, int ex, int ez)
        {
            var prev = new (int, int)?[g.W, g.H];
            var seen = new bool[g.W, g.H];
            var q = new Queue<(int, int)>();
            q.Enqueue((sx, sz));
            seen[sx, sz] = true;
            while (q.Count > 0)
            {
                var (x, z) = q.Dequeue();
                if (x == ex && z == ez) break;
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        int nx = x + dx, nz = z + dz;
                        if ((dx == 0 && dz == 0) || !g.In(nx, nz) || seen[nx, nz] || g.wall[nx, nz]) continue;
                        if (dx != 0 && dz != 0 && (g.wall[x + dx, z] || g.wall[x, z + dz])) continue;   // no corner cutting
                        seen[nx, nz] = true;
                        prev[nx, nz] = (x, z);
                        q.Enqueue((nx, nz));
                    }
            }
            if (!seen[ex, ez]) return null;
            var path = new List<(int, int)>();
            for (var c = ((int, int)?)(ex, ez); c.HasValue && c.Value != (sx, sz); c = prev[c.Value.Item1, c.Value.Item2]) path.Add(c.Value);
            path.Reverse();
            return path;
        }

        /// <summary>Independent oracle for the reading order: -1 for the carrier's zone, i for path cell i's zone, int.Max if
        /// not in the way. Written from the rule's words, not from the kernel's loop.</summary>
        private static int ZoneIndex(int x, int z, int px, int pz, List<int> ax, List<int> az)
        {
            if (Math.Max(Math.Abs(x - px), Math.Abs(z - pz)) <= 1) return -1;
            int n = Math.Min(ax.Count, RuledLookAhead);
            for (int i = 0; i < n; i++) if (Math.Max(Math.Abs(x - ax[i]), Math.Abs(z - az[i])) <= 1) return i;
            return int.MaxValue;
        }

        private static void Layout(Grid g, Random r, int regime, int fx, int fz, int px, int pz, List<(int x, int z)> pathHint)
        {
            switch (regime)
            {
                case 0: break;   // no fire
                case 1:          // a ring round the fruit, 1-4 thick, maybe with a gap
                case 2:
                    {
                        int thick = 1 + r.Next(4), inner = 1, outer = inner + thick;
                        int gapSide = regime == 2 ? r.Next(4) : -1;
                        for (int x = fx - outer; x <= fx + outer; x++)
                            for (int z = fz - outer; z <= fz + outer; z++)
                            {
                                int d = Math.Max(Math.Abs(x - fx), Math.Abs(z - fz));
                                if (d <= inner || !g.In(x, z)) continue;
                                int side = Math.Abs(x - fx) >= Math.Abs(z - fz) ? (x < fx ? 0 : 1) : (z < fz ? 2 : 3);
                                if (side == gapSide && Math.Abs((side < 2 ? z - fz : x - fx)) <= 1) continue;
                                g.fire[x, z] = true;
                            }
                        break;
                    }
                case 3:          // a burn band across the way
                    {
                        int w = 1 + r.Next(5);
                        bool vertical = r.Next(2) == 0;
                        int at = vertical ? (px + fx) / 2 : (pz + fz) / 2;
                        for (int a = at; a < at + w; a++)
                            for (int b = 0; b < (vertical ? g.H : g.W); b++)
                                if (vertical ? g.In(a, b) : g.In(b, a)) { if (vertical) g.fire[a, b] = true; else g.fire[b, a] = true; }
                        break;
                    }
                case 4:          // scattered fire
                    {
                        double p = r.NextDouble() * 0.4;
                        for (int x = 0; x < g.W; x++) for (int z = 0; z < g.H; z++) if (r.NextDouble() < p) g.fire[x, z] = true;
                        break;
                    }
                case 5:          // fire only away from the path: a block in a corner the path does not reach
                    {
                        for (int x = 0; x < g.W; x++)
                            for (int z = 0; z < g.H; z++)
                            {
                                bool near = Math.Max(Math.Abs(x - px), Math.Abs(z - pz)) <= 2;
                                foreach (var c in pathHint) if (Math.Max(Math.Abs(x - c.x), Math.Abs(z - c.z)) <= 2) { near = true; break; }
                                if (!near && r.Next(3) == 0) g.fire[x, z] = true;
                            }
                        break;
                    }
            }
            for (int x = 0; x < g.W; x++) for (int z = 0; z < g.H; z++) if (g.wall[x, z]) g.fire[x, z] = false;
        }

        private static void Walls(Grid g, Random r, int fx, int fz, int px, int pz)
        {
            int segs = r.Next(5);
            for (int s = 0; s < segs; s++)
            {
                int x = r.Next(g.W), z = r.Next(g.H), len = 2 + r.Next(8);
                bool vertical = r.Next(2) == 0;
                for (int k = 0; k < len; k++)
                {
                    int wx = vertical ? x : x + k, wz = vertical ? z + k : z;
                    if (!g.In(wx, wz) || (wx == px && wz == pz) || (Math.Abs(wx - fx) <= 1 && Math.Abs(wz - fz) <= 1)) continue;
                    g.wall[wx, wz] = true;
                }
            }
        }

        public static List<string> Run(int n, int seed)
        {
            var fails = new List<string>();
            try
            {
                Gate();
                var r = new Random(seed);
                for (int k = 0; k < n; k++) PickCase(r, k);
                for (int k = 0; k < Math.Max(1, n / 4); k++) WalkCase(r, k);
                Check(n < 40 || (CarrierCasts > 0 && ControlCrossings > 0), $"walk is blind: {CarrierCasts} casts, {ControlCrossings} control crossings");
                Check(PickAnswers > 0 && PickNone > 0 || n < 40, $"pick is blind: {PickAnswers} answers, {PickNone} no-answers");
                Console.WriteLine($"foam: {Picks} picks ({PickAnswers} aimed, {PickNone} none), {WalkCases} walks ({CarrierCasts} casts), "
                    + $"control crossed fire in {ControlCrossings}; worst exposure with spread {WorstSpreadExposure} ticks at rate {WorstSpreadRate:F4}");
            }
            catch (Exception e) { fails.Add("foam: " + e.Message); }
            return fails;
        }

        private static void Gate()
        {
            for (int m = 0; m < 128; m++)
            {
                bool en = (m & 1) != 0, car = (m & 2) != 0, ours = (m & 4) != 0, dr = (m & 8) != 0, inc = (m & 16) != 0, busy = (m & 32) != 0, ready = (m & 64) != 0;
                var got = RM_FoamPathKernel.Gate(en, car, ours, dr, inc, busy, ready);
                bool want = en && car && ours && !dr && !inc && !busy && ready;
                PyrelandsFuzz.Cases++;
                Check((got == RM_FoamGate.Foam) == want, $"gate row {m}: {got}, ruled foam={want}");
            }
        }

        private static void PickCase(Random r, int k)
        {
            int W = 40, H = 40;
            var g = new Grid(W, H);
            int px = r.Next(W), pz = r.Next(H), fx = 2 + r.Next(W - 4), fz = 2 + r.Next(H - 4);
            if (px == fx && pz == fz) px = (px + 7) % W;
            Walls(g, r, fx, fz, px, pz);
            g.wall[px, pz] = false;
            var path = Path(g, px, pz, fx, fz) ?? new List<(int x, int z)>();
            if (r.Next(6) == 0) path.Clear();   // standing still
            Layout(g, r, r.Next(6), fx, fz, px, pz, path);
            float range = r.Next(3) == 0 ? 3f + (float)r.NextDouble() * 12f : ShippedRange;
            var ax = new List<int>(); var az = new List<int>();
            foreach (var c in path) { ax.Add(c.x); az.Add(c.z); }
            var canHit = g.CanHitFrom(px, pz, range);
            bool got = RM_FoamPathKernel.PickTarget(px, pz, ax, az, g.Burning, canHit, out int tx, out int tz);
            Picks++;
            PyrelandsFuzz.Cases++;
            int best = int.MaxValue;
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                    if (g.fire[x, z] && canHit(x, z)) best = Math.Min(best, ZoneIndex(x, z, px, pz, ax, az));
            string where = $"case {k}: carrier {px},{pz} fruit {fx},{fz} path {path.Count} range {range:F1}";
            if (!got)
            {
                PickNone++;
                Check(best == int.MaxValue, $"{where}: a hittable fire is in the way (zone {best}) and the carrier does not foam");
                return;
            }
            PickAnswers++;
            Check(g.Burning(tx, tz), $"{where}: aimed at {tx},{tz}, which is not burning");
            Check(canHit(tx, tz), $"{where}: aimed at {tx},{tz}, which the sprayer cannot hit");
            Check(RM_FoamPathKernel.InTheWay(tx, tz, px, pz, ax, az) && ZoneIndex(tx, tz, px, pz, ax, az) != int.MaxValue, $"{where}: aimed at {tx},{tz}, a fire away from the path");
            int zi = ZoneIndex(tx, tz, px, pz, ax, az);
            Check(zi == best, $"{where}: aimed at zone {zi}, the first fire in the way is in zone {best}");
        }

        /// <summary>The bar's scene. The carrier stands west of a 3x3 fruit patch inside a burning 9x9; it walks to the patch
        /// and back. Returns (reached, foam cells, ticks on a burning cell, casts).</summary>
        private static (bool reached, int foam, int exposure, int casts, bool crossed) Walk(Random r, bool sprayer, int thick, bool gap, double spread, int seed)
        {
            var rr = new Random(seed);
            int W = 40, H = 30, fx = 24, fz = 15, px = 6, pz = 15;
            var g = new Grid(W, H);
            int inner = 1, outer = inner + thick;
            for (int x = fx - outer; x <= fx + outer; x++)
                for (int z = fz - outer; z <= fz + outer; z++)
                {
                    int d = Math.Max(Math.Abs(x - fx), Math.Abs(z - fz));
                    if (d <= inner) continue;
                    if (gap && x < fx && Math.Abs(z - fz) <= 1) continue;
                    g.fire[x, z] = true;
                }
            bool[,] grass = new bool[W, H];
            for (int x = fx - outer - 2; x <= fx + outer + 2; x++) for (int z = fz - outer - 2; z <= fz + outer + 2; z++) if (g.In(x, z)) grass[x, z] = true;
            var route = Path(g, px, pz, fx - 1, fz);
            var back = Path(g, fx - 1, fz, px, pz);
            var walk = new List<(int x, int z)>(route);
            walk.AddRange(back);
            bool crossed = false;
            foreach (var c in walk) if (g.fire[c.x, c.z]) crossed = true;
            int cx = px, cz = pz, idx = 0, busy = 0, moveLeft = TicksPerCell, exposure = 0, casts = 0;
            bool reached = false;
            int landAt = -1, landX = 0, landZ = 0;
            for (int t = 0; t < 6000 && idx < walk.Count; t++)
            {
                if (spread > 0)
                {
                    var lit = new List<(int, int)>();
                    for (int x = 0; x < W; x++)
                        for (int z = 0; z < H; z++)
                        {
                            if (!g.fire[x, z]) continue;
                            for (int dx = -1; dx <= 1; dx++)
                                for (int dz = -1; dz <= 1; dz++)
                                {
                                    int nx = x + dx, nz = z + dz;
                                    if (g.In(nx, nz) && grass[nx, nz] && !g.fire[nx, nz] && !g.foam[nx, nz] && rr.NextDouble() < spread) lit.Add((nx, nz));
                                }
                        }
                    foreach (var c in lit) g.fire[c.Item1, c.Item2] = true;
                }
                if (t == landAt)
                {
                    for (int x = landX - 3; x <= landX + 3; x++)
                        for (int z = landZ - 3; z <= landZ + 3; z++)
                            if (g.In(x, z) && !g.wall[x, z] && (x - landX) * (x - landX) + (z - landZ) * (z - landZ) <= FoamRadius * FoamRadius)
                            { g.fire[x, z] = false; g.foam[x, z] = true; }
                }
                if (busy > 0) busy--;
                else if (sprayer && RM_FoamPathKernel.Gate(true, true, true, false, false, false, true) == RM_FoamGate.Foam)
                {
                    var ax = new List<int>(); var az = new List<int>();
                    for (int i = idx; i < walk.Count; i++) { ax.Add(walk[i].x); az.Add(walk[i].z); }
                    if (RM_FoamPathKernel.PickTarget(cx, cz, ax, az, g.Burning, g.CanHitFrom(cx, cz, ShippedRange), out int tx, out int tz))
                    {
                        casts++;
                        double a = rr.NextDouble() * 2 * Math.PI, d = rr.NextDouble() * MissRadius;
                        landX = tx + (int)Math.Round(Math.Cos(a) * d); landZ = tz + (int)Math.Round(Math.Sin(a) * d);
                        landAt = t + WarmupTicks;   // the foam lands when the warmup ends, not when the aim starts
                        busy = WarmupTicks + CooldownTicks;
                    }
                }
                if (busy == 0)
                {
                    if (--moveLeft <= 0)
                    {
                        cx = walk[idx].x; cz = walk[idx].z; idx++; moveLeft = TicksPerCell;
                        if (cx == fx - 1 && cz == fz) reached = true;
                    }
                }
                if (g.fire[cx, cz]) exposure++;
            }
            int foam = 0;
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) if (g.foam[x, z]) foam++;
            return (reached && idx >= walk.Count, foam, exposure, casts, crossed);
        }

        private static void WalkCase(Random r, int k)
        {
            int thick = 1 + r.Next(4);
            bool gap = r.Next(5) == 0;
            double spread = r.Next(3) == 0 ? 0 : r.NextDouble() * 0.02;
            int seed = r.Next();
            var on = Walk(r, true, thick, gap, spread, seed);
            var off = Walk(r, false, thick, gap, spread, seed);
            WalkCases++;
            CarrierCasts += on.casts;
            PyrelandsFuzz.Cases++;
            string where = $"walk {k}: ring {thick} thick, gap {gap}, spread {spread:F4}, seed {seed}";
            Check(on.reached, $"{where}: the carrier did not reach the fruit and come back");
            if (on.crossed) Check(on.foam > 0, $"{where}: the carrier's path crossed fire and it laid no foam");
            if (on.exposure > WorstSpreadExposure) { WorstSpreadExposure = on.exposure; WorstSpreadRate = spread; }
            Check(on.exposure == 0, $"{where}: the carrier stood {on.exposure} ticks on a burning cell");
            if (off.crossed)
            {
                ControlCrossings++;
                Check(off.exposure > 0, $"{where}: control without the sprayer crossed fire and stood on no burning cell (the walk is blind)");
            }
            if (!gap) Check(on.crossed, $"{where}: a closed ring did not put fire on the path (the scene is wrong)");
        }
    }
}
