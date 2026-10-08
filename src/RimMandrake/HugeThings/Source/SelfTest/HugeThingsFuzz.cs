// Approach B for HugeThings: seeded fuzz over the Verse-free footprint kernel (../Kernel/RM_HugeFootprintKernel.cs).
// Families (each case is one random plant: root cell, drawSize, visualSizeRange, growth, jitter, flip, Mod Settings
// multiplier, and a random mask shaped the way measure_huge_plant_masks.py shapes real ones):
//   any          on every case: the selection rect holds every blocked cell and the whole drawn picture; every blocked
//                cell's centre is inside the drawn picture; the root cell is never blocked; nothing south of the root
//                when the quad is bottom-anchored on it (drawSize <= 1)
//   full         at full growth, settings 1, drawSize 1, any jitter: the blocked cells ARE the measured cells, mirrored
//                exactly when flipped
//   any (also)   the kernel's blocked cells equal an INDEPENDENT double-precision forward oracle written from Plant.Print's
//                formulas (drawSize != 1 included), ignoring only cells within Eps of an edge; no duplicates
//   boundary     growths that put an edge within 1e-4 of a cell centre, nudged both ways, against the oracle
//   symmetry     integer translation moves the footprint with the root; a mirrored mask with the opposite flip is identical
//   ledger       overlap: realized = union of claims in any order; idempotent re-set; removing one owner keeps the rest
//   planner      never closes pawn/item/protected cells, never cuts a cell off from open ground or a root from access;
//                order-independent; idempotent (checked against an independent whole-board flood)
//   cache        signature cache == fresh computation as each field changes alone
//   damage       one forwarded hit per (tick, source, owner)
// Growth -> cells nesting is NOT an invariant (GPT review #10; a ring of roots scaled up truly moves outward).
//   determinism  the same seed gives byte-identical results
// A failing case prints as `FAIL family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Linq;
using K = RimMandrake.HugeThings.RM_HugeFootprintKernel;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class HugeThingsFuzz
    {
        public static long Cases, Checks;
        private const float JitterMargin = 0.06f;   // measure_huge_plant_masks.py JITTER_MARGIN

        private static void Check(bool ok, string msg)
        {
            Checks++;
            if (!ok) throw new Exception(msg);
        }

        internal sealed class Plant
        {
            public int RootX, RootZ;
            public float DrawX, VMin, VMax, Growth, Jx, Jz, Scale;
            public bool Flip;
            public HugeMask Mask;

            public float Visual(float g) => VMin + (VMax - VMin) * g;
        }

        private static float R(Random r, float a, float b) => a + (float)r.NextDouble() * (b - a);

        /// <summary>A random mask in the tool's measurement frame (drawSize 1 at full growth, bottom on the root's south
        /// edge): a visible box, and contact cells inside it (centre within the box, less the jitter margin in x), never
        /// the root. star: a solid base box containing the bottom-centre, so the region is star-shaped about it.</summary>
        internal static HugeMask MakeMask(Random r, float size, bool star)
        {
            var m = new HugeMask { MeasuredSize = size };
            if (star)
            {
                m.U0 = R(r, 0f, 0.45f);
                m.U1 = R(r, 0.55f, 1f);
                m.V0 = 0f;
                m.V1 = R(r, 0.3f, 1f);
            }
            else
            {
                m.U0 = R(r, 0f, 0.45f);
                m.U1 = R(r, Math.Max(m.U0 + 0.05f, 0.5f), 1f);
                m.V0 = R(r, 0f, 0.3f);
                m.V1 = R(r, Math.Max(m.V0 + 0.1f, 0.4f), 1f);
            }
            float left = 0.5f - size / 2f;
            int n = (int)Math.Ceiling(size);
            // star: a solid band of rows from the bottom, columns spanning the root; else a random blob
            int rows = star ? 1 + r.Next(Math.Max(1, n / 2)) : n;
            int halfW = 1 + r.Next(Math.Max(1, n / 2));
            for (int dz = 0; dz < rows; dz++)
            {
                for (int dx = (int)Math.Floor(left) - 1; dx <= (int)Math.Ceiling(left + size); dx++)
                {
                    if (dx == 0 && dz == 0) continue;
                    float cu = (dx + 0.5f - left) / size, cv = (dz + 0.5f) / size;
                    if (!(m.U0 + JitterMargin / size <= cu && cu <= m.U1 - JitterMargin / size && m.V0 <= cv && cv <= m.V1)) continue;
                    if (star)
                    {
                        if (Math.Abs(dx) <= halfW) m.Contact.Add(K.Key(dx, dz));
                    }
                    else if (r.NextDouble() < 0.35)
                    {
                        m.Contact.Add(K.Key(dx, dz));
                    }
                }
            }
            return m;
        }

        internal static Plant MakePlant(int seed, bool star)
        {
            var r = new Random(seed);
            var p = new Plant
            {
                RootX = r.Next(-50, 300),
                RootZ = r.Next(-50, 300),
                DrawX = r.NextDouble() < 0.5 ? 1f : R(r, 0.5f, 2f),
                VMin = R(r, 1f, 8f),
                Growth = (float)r.NextDouble(),
                Jx = R(r, -0.05f, 0.05f),
                Jz = R(r, -0.05f, 0.05f),
                Flip = r.Next(2) == 0,
                Scale = r.NextDouble() < 0.4 ? 1f : R(r, 0.5f, 1.5f),
            };
            p.VMax = p.VMin + R(r, 0f, 18f);
            p.Mask = MakeMask(r, p.DrawX * p.VMax, star);
            return p;
        }

        private static string Fmt(List<long> cells) => string.Join(" ", cells.Select(k => K.KeyX(k) + "," + K.KeyZ(k)));

        // ---- the independent oracle: double precision, FORWARD mapping straight from Plant.Print's formulas --------------
        // Each measured contact cell is pushed forward into the world as a rectangle; a world cell is blocked when its centre
        // lies in one of those rectangles, inside the drawn picture, inside the blocking quad, and is not the root. Cells whose
        // centre sits within Eps of any edge are AMBIGUOUS (float vs double may round either way) and excluded from the
        // comparison, never from the run.
        private const double Eps = 2e-3;

        internal static HashSet<long> Oracle(Plant p, float visual, out HashSet<long> ambiguous)
        {
            ambiguous = new HashSet<long>();
            var outCells = new HashSet<long>();
            double cx = p.RootX + 0.5 + p.Jx, cz = p.RootZ + 0.5 + p.Jz;
            if (cz - visual / 2.0 < p.RootZ) cz = p.RootZ + visual / 2.0;     // Plant.Print: compares with visual, not side
            double side = (double)p.DrawX * visual;
            double qx = cx - side / 2.0, qz = cz - side / 2.0;
            double pu0 = p.Flip ? 1 - p.Mask.U1 : p.Mask.U0, pu1 = p.Flip ? 1 - p.Mask.U0 : p.Mask.U1;
            double px0 = qx + pu0 * side, px1 = qx + pu1 * side, pz0 = qz + p.Mask.V0 * side, pz1 = qz + p.Mask.V1 * side;
            double bs = side * p.Scale, bx0 = cx - bs / 2.0, bz0 = qz;
            double S = p.Mask.MeasuredSize, left = 0.5 - S / 2.0;
            if (S <= 0 || bs <= 0 || p.Mask.Contact.Count == 0) return outCells;
            var rects = new List<double[]>();
            foreach (long k in p.Mask.Contact)
            {
                int dx = K.KeyX(k), dz = K.KeyZ(k);
                double u0 = (dx - left) / S, u1 = (dx + 1 - left) / S, v0 = dz / S, v1 = (dz + 1) / S;
                if (p.Flip) { double t = 1 - u1; u1 = 1 - u0; u0 = t; }
                rects.Add(new[] { bx0 + u0 * bs, bz0 + v0 * bs, bx0 + u1 * bs, bz0 + v1 * bs });
            }
            int xa = (int)Math.Floor(Math.Min(bx0, px0)) - 1, xb = (int)Math.Ceiling(Math.Max(bx0 + bs, px1)) + 1;
            int za = (int)Math.Floor(Math.Min(bz0, pz0)) - 1, zb = (int)Math.Ceiling(Math.Max(bz0 + bs, pz1)) + 1;
            for (int z = za; z <= zb; z++)
            {
                for (int x = xa; x <= xb; x++)
                {
                    double ux = x + 0.5, uz = z + 0.5;
                    bool near = Math.Abs(ux - px0) < Eps || Math.Abs(ux - px1) < Eps || Math.Abs(uz - pz0) < Eps || Math.Abs(uz - pz1) < Eps
                             || Math.Abs(ux - bx0) < Eps || Math.Abs(ux - bx0 - bs) < Eps || Math.Abs(uz - bz0) < Eps || Math.Abs(uz - bz0 - bs) < Eps;
                    bool hit = false;
                    foreach (double[] r in rects)
                    {
                        if (Math.Abs(ux - r[0]) < Eps || Math.Abs(ux - r[2]) < Eps || Math.Abs(uz - r[1]) < Eps || Math.Abs(uz - r[3]) < Eps)
                        {
                            if (ux > r[0] - Eps && ux < r[2] + Eps && uz > r[1] - Eps && uz < r[3] + Eps) near = true;
                        }
                        if (ux > r[0] && ux < r[2] && uz > r[1] && uz < r[3]) hit = true;
                    }
                    long key = K.Key(x, z);
                    if (near) { ambiguous.Add(key); continue; }
                    bool inPic = ux > px0 && ux < px1 && uz > pz0 && uz < pz1;
                    bool inQuad = ux > bx0 && ux < bx0 + bs && uz > bz0 && uz < bz0 + bs;
                    if (hit && inPic && inQuad && !(x == p.RootX && z == p.RootZ)) outCells.Add(key);
                }
            }
            return outCells;
        }

        internal static void CheckOracle(Plant p, float visual, List<long> got, string where)
        {
            HashSet<long> want = Oracle(p, visual, out HashSet<long> amb);
            var g = new HashSet<long>(got);
            Check(g.Count == got.Count, where + ": duplicate cells in the kernel's output");
            g.ExceptWith(amb);
            want.ExceptWith(amb);
            if (!g.SetEquals(want))
            {
                var extra = g.Except(want).ToList();
                var miss = want.Except(g).ToList();
                Check(false, where + ": kernel != oracle; extra [" + Fmt(extra) + "] missing [" + Fmt(miss) + "]");
            }
        }

        internal static string CaseAny(int seed)
        {
            Plant p = MakePlant(seed, false);
            HugeQuad q = K.Quad(p.RootX, p.RootZ, p.DrawX, p.Visual(p.Growth), p.Jx, p.Jz);
            List<long> blocked = K.ContactCells(p.RootX, p.RootZ, q, p.Scale, p.Flip, p.Mask);
            CheckOracle(p, p.Visual(p.Growth), blocked, "any");
            CellBox pic = K.PictureBox(q, p.Mask, p.Flip);
            CellBox sel = K.SelectBox(p.RootX, p.RootZ, pic, blocked);
            K.PictureBounds(q, p.Mask, p.Flip, out float x0, out float z0, out float x1, out float z1);
            foreach (long c in blocked)
            {
                int x = K.KeyX(c), z = K.KeyZ(c);
                Check(sel.Contains(x, z), "selection misses blocked cell " + x + "," + z);
                Check(x + 0.5f >= x0 && x + 0.5f <= x1 && z + 0.5f >= z0 && z + 0.5f <= z1,
                      "blocked cell " + x + "," + z + " is outside the drawn picture");
                Check(!(x == p.RootX && z == p.RootZ), "the root cell is blocked");
                if (p.DrawX <= 1f) Check(z >= p.RootZ, "blocked cell " + x + "," + z + " is south of the root");
            }
            Check(sel.MinX <= Math.Floor(x0) && sel.MinZ <= Math.Floor(z0), "selection starts inside the picture");
            Check(sel.MaxX + 1 >= x1 && sel.MaxZ + 1 >= z1, "selection ends inside the picture");
            Check(sel.Contains(p.RootX, p.RootZ), "selection misses the root cell");
            return Fmt(blocked) + "|" + sel.MinX + "," + sel.MinZ + "," + sel.MaxX + "," + sel.MaxZ;
        }

        internal static string CaseFull(int seed)
        {
            Plant p = MakePlant(seed, (seed & 1) == 0);
            p.DrawX = 1f;                      // the tool's frame: drawSize 1
            var r = new Random(seed ^ 0x5eed);
            var m = MakeMask(r, p.VMax, (seed & 1) == 0);
            p.Mask = m;
            HugeQuad q = K.Quad(p.RootX, p.RootZ, 1f, p.VMax, p.Jx, p.Jz);
            List<long> got = K.ContactCells(p.RootX, p.RootZ, q, 1f, p.Flip, m);
            var want = new HashSet<long>(m.Contact.Select(k => K.Key(p.RootX + (p.Flip ? -K.KeyX(k) : K.KeyX(k)), p.RootZ + K.KeyZ(k))));
            Check(want.SetEquals(got), "full growth blocked != measured" + (p.Flip ? " (flipped)" : "") + ": got [" + Fmt(got) +
                  "] want [" + Fmt(want.ToList()) + "]");
            return Fmt(got);
        }

        /// <summary>Cell-boundary crossings: the growth is chosen so a picture or quad edge lands within 1e-4 of a cell
        /// centre or edge, then nudged both ways; the kernel must agree with the oracle on every unambiguous cell.</summary>
        internal static string CaseBoundary(int seed)
        {
            Plant p = MakePlant(seed, false);
            var r = new Random(seed ^ 0xb0b);
            // side = drawX * visual; aim the quad's top edge (qz + side) at a half-integer
            float target = (float)Math.Floor(p.RootZ + p.VMin * p.DrawX) + 0.5f + r.Next(0, 6);
            float visual = Math.Max(p.VMin, Math.Min(p.VMax, (target - p.RootZ) / Math.Max(0.01f, (p.DrawX + 1f) / 2f)));
            var sb = new List<string>();
            foreach (float d in new[] { -1e-4f, 0f, 1e-4f })
            {
                float v = visual + d;
                HugeQuad q = K.Quad(p.RootX, p.RootZ, p.DrawX, v, p.Jx, p.Jz);
                List<long> got = K.ContactCells(p.RootX, p.RootZ, q, p.Scale, p.Flip, p.Mask);
                CheckOracle(p, v, got, "boundary");
                sb.Add(got.Count.ToString());
            }
            return string.Join(",", sb);
        }

        /// <summary>Translation and double mirroring at the geometry level: moving the root by an integer moves every
        /// blocked cell by it; mirroring the mask AND flipping gives the same cells.</summary>
        internal static string CaseSymmetry(int seed)
        {
            Plant p = MakePlant(seed, false);
            p.DrawX = 1f;
            p.Jx = 0f;
            HugeQuad q = K.Quad(p.RootX, p.RootZ, 1f, p.Visual(p.Growth), 0f, p.Jz);
            List<long> a = K.ContactCells(p.RootX, p.RootZ, q, p.Scale, p.Flip, p.Mask);
            int tx = 37, tz = -11;
            HugeQuad q2 = K.Quad(p.RootX + tx, p.RootZ + tz, 1f, p.Visual(p.Growth), 0f, p.Jz);
            var b = new HashSet<long>(K.ContactCells(p.RootX + tx, p.RootZ + tz, q2, p.Scale, p.Flip, p.Mask));
            var moved = new HashSet<long>(a.Select(k => K.Key(K.KeyX(k) + tx, K.KeyZ(k) + tz)));
            // translation is exact only away from float rounding at large coordinates: compare through the oracle's ambiguity
            Oracle(p, p.Visual(p.Growth), out HashSet<long> amb);
            var ambMoved = new HashSet<long>(amb.Select(k => K.Key(K.KeyX(k) + tx, K.KeyZ(k) + tz)));
            moved.ExceptWith(ambMoved);
            b.ExceptWith(ambMoved);
            Check(moved.SetEquals(b), "translation by " + tx + "," + tz + " changed the footprint");
            var mirror = new HugeMask { U0 = 1 - p.Mask.U1, U1 = 1 - p.Mask.U0, V0 = p.Mask.V0, V1 = p.Mask.V1, MeasuredSize = p.Mask.MeasuredSize };
            foreach (long k in p.Mask.Contact) mirror.Contact.Add(K.Key(-K.KeyX(k), K.KeyZ(k)));
            var c = new HashSet<long>(K.ContactCells(p.RootX, p.RootZ, q, p.Scale, !p.Flip, mirror));
            var a2 = new HashSet<long>(a);
            a2.ExceptWith(amb);
            c.ExceptWith(amb);
            Check(a2.SetEquals(c), "mirrored mask + opposite flip != original");
            return a.Count.ToString();
        }

        // ---- claims, planning, cache, damage ------------------------------------------------------------------------------
        private static List<long> Blob(Random r, int cx, int cz, int n)
        {
            var s = new HashSet<long>();
            int x = cx, z = cz;
            for (int i = 0; i < n; i++)
            {
                s.Add(K.Key(x, z));
                int d = r.Next(4);
                x += d == 0 ? 1 : d == 1 ? -1 : 0;
                z += d == 2 ? 1 : d == 3 ? -1 : 0;
            }
            return s.ToList();
        }

        /// <summary>Overlap: the realized set is the union of current claims whatever order owners set/refresh/remove in;
        /// setting the same claims twice changes nothing; removing one owner leaves exactly the others' union.</summary>
        internal static string CaseLedger(int seed)
        {
            var r = new Random(seed);
            int owners = 2 + r.Next(5);
            var claims = new Dictionary<int, List<long>>();
            for (int o = 0; o < owners; o++) claims[o + 100] = Blob(r, r.Next(6), r.Next(6), 1 + r.Next(25));
            string Realize(IEnumerable<int> order, out ClaimLedger led, out HashSet<long> realized)
            {
                led = new ClaimLedger();
                realized = new HashSet<long>();
                foreach (int o in order)
                {
                    var on = new List<long>();
                    var off = new List<long>();
                    led.Set(o, Blob(new Random(o * 31 + seed), 0, 0, 5), on, off);   // a stale earlier footprint
                    foreach (long c in on) Check(realized.Add(c), "a cell became claimed twice");
                    foreach (long c in off) Check(realized.Remove(c), "freed a cell that was not realized");
                    on.Clear(); off.Clear();
                    led.Set(o, claims[o], on, off);
                    foreach (long c in on) Check(realized.Add(c), "a cell became claimed twice");
                    foreach (long c in off) Check(realized.Remove(c), "freed a cell that was not realized");
                }
                var want = new HashSet<long>(claims.Values.SelectMany(v => v));
                Check(realized.SetEquals(want), "realized != union of claims");
                Check(new HashSet<long>(led.Claimed).SetEquals(want), "ledger != union of claims");
                ClaimLedger l = led;
                return string.Join(" ", want.OrderBy(k => k).Select(k => l.PrimaryOwner(k)));
            }
            var ids = claims.Keys.ToList();
            string a = Realize(ids, out ClaimLedger l1, out HashSet<long> real1);
            var shuffled = ids.OrderBy(_ => r.Next()).ToList();
            string b = Realize(shuffled, out _, out _);
            Check(a == b, "primary owners depend on registration order");
            var on2 = new List<long>();
            var off2 = new List<long>();
            int victim = ids[r.Next(ids.Count)];
            l1.Set(victim, claims[victim], on2, off2);
            Check(on2.Count == 0 && off2.Count == 0, "re-setting identical claims changed cells (not idempotent)");
            l1.Remove(victim, off2);
            foreach (long c in off2) real1.Remove(c);
            var rest = new HashSet<long>(claims.Where(kv => kv.Key != victim).SelectMany(kv => kv.Value));
            Check(real1.SetEquals(rest), "removing one owner lost another owner's claims");
            Check(new HashSet<long>(l1.Claimed).SetEquals(rest), "ledger after removal != others' union");
            return a;
        }

        internal sealed class Grid
        {
            public int W, H;
            public CellFlags[] F;
            public CellFlags At(long k)
            {
                int x = K.KeyX(k), z = K.KeyZ(k);
                if (x < 0 || z < 0 || x >= W || z >= H) return CellFlags.Passable;   // beyond the board: open map
                return F[z * W + x];
            }
        }

        internal static Grid MakeGrid(Random r, int w, int h)
        {
            var g = new Grid { W = w, H = h, F = new CellFlags[w * h] };
            for (int i = 0; i < g.F.Length; i++)
            {
                double u = r.NextDouble();
                g.F[i] = u < 0.12 ? CellFlags.None                                   // wall / existing trunk
                       : u < 0.17 ? CellFlags.Passable | CellFlags.Pawn
                       : u < 0.22 ? CellFlags.Passable | CellFlags.Item
                       : u < 0.27 ? CellFlags.Passable | CellFlags.Protected
                       : CellFlags.Passable;
            }
            return g;
        }

        /// <summary>The planner never closes a pawn/item/protected/impassable cell, never cuts a passable cell off from the
        /// border it reached, keeps every served root served, is order-independent and idempotent.</summary>
        internal static string CasePlanner(int seed)
        {
            var r = new Random(seed);
            int w = 8 + r.Next(16), h = 8 + r.Next(16);
            Grid g = MakeGrid(r, w, h);
            List<long> wanted = Blob(r, w / 2, h / 2, 5 + r.Next(60)).Where(k => K.KeyX(k) >= 0 && K.KeyZ(k) >= 0 && K.KeyX(k) < w && K.KeyZ(k) < h).ToList();
            var roots = new List<long> { K.Key(w / 2, h / 2 - 1) };
            wanted.Remove(roots[0]);
            CellBox win = Planner.Window(wanted, roots[0]);
            List<long> acc = Planner.Plan(wanted, roots, g.At, win);
            var accSet = new HashSet<long>(acc);
            Check(accSet.Count == acc.Count, "duplicate planned cells");
            Check(accSet.IsSubsetOf(wanted), "planned a cell nobody wanted");
            foreach (long k in acc)
            {
                CellFlags f = g.At(k);
                Check((f & CellFlags.Passable) != 0, "closed an already impassable cell");
                Check((f & CellFlags.Pawn) == 0, "closed a cell with a pawn in it");
                Check((f & CellFlags.Item) == 0, "closed a cell with an item in it (it would be moved or destroyed)");
                Check((f & CellFlags.Protected) == 0, "closed a protected cell");
                Check(!roots.Contains(k), "closed a root");
            }
            // independent reachability over the planner's window, flooded by separate code (the window border = open map)
            bool[] Board(HashSet<long> closed, out int bw, out int bh)
            {
                bw = win.MaxX - win.MinX + 1; bh = win.MaxZ - win.MinZ + 1;
                var pass = new bool[bw * bh];
                for (int z = 0; z < bh; z++)
                    for (int x = 0; x < bw; x++)
                    {
                        long k = K.Key(x + win.MinX, z + win.MinZ);
                        pass[z * bw + x] = (g.At(k) & CellFlags.Passable) != 0 && !closed.Contains(k);
                    }
                return pass;
            }
            bool[] p0 = Board(new HashSet<long>(), out int W2, out int H2);
            bool[] p1 = Board(accSet, out _, out _);
            bool[] r0 = Flood(p0, W2, H2), r1 = Flood(p1, W2, H2);
            for (int i = 0; i < p1.Length; i++)
            {
                if (p1[i] && r0[i]) Check(r1[i], "a cell that reached open ground is now cut off (trapped pawn / new pocket) at " + (i % W2 + win.MinX) + "," + (i / W2 + win.MinZ));
            }
            foreach (long root in roots)
            {
                int ri = (K.KeyZ(root) - win.MinZ) * W2 + K.KeyX(root) - win.MinX;
                bool Served(bool[] pass, bool[] reach) => new[] { 1, -1, W2, -W2 }.Any(d => pass[ri + d] && reach[ri + d]);
                if (Served(p0, r0)) Check(Served(p1, r1), "the root lost every reachable open neighbour (cannot be cut)");
            }
            // order independence
            var shuffled = wanted.OrderBy(_ => r.Next()).ToList();
            List<long> acc2 = Planner.Plan(shuffled, roots, g.At, win);
            Check(acc2.SequenceEqual(acc), "planning depends on the order cells were wanted in");
            // idempotence: with the accepted cells closed, the rest stays deferred
            Grid g2 = new Grid { W = w, H = h, F = (CellFlags[])g.F.Clone() };
            foreach (long k in acc) g2.F[K.KeyZ(k) * w + K.KeyX(k)] = CellFlags.None;
            List<long> again = Planner.Plan(wanted.Where(k => !accSet.Contains(k)).ToList(), roots, g2.At, win);
            Check(again.Count == 0, "a second plan on the same map closed " + again.Count + " more cells (not idempotent)");
            return string.Join(" ", acc);
        }

        /// <summary>Independent 4-connected flood from the border (BFS over a queue; the planner uses a stack).</summary>
        private static bool[] Flood(bool[] pass, int w, int h)
        {
            var seen = new bool[pass.Length];
            var q = new Queue<int>();
            for (int i = 0; i < pass.Length; i++)
            {
                int x = i % w, z = i / w;
                if (pass[i] && (x == 0 || z == 0 || x == w - 1 || z == h - 1)) { seen[i] = true; q.Enqueue(i); }
            }
            while (q.Count > 0)
            {
                int i = q.Dequeue(), x = i % w, z = i / w;
                foreach (int j in new[] { x > 0 ? i - 1 : -1, x < w - 1 ? i + 1 : -1, z > 0 ? i - w : -1, z < h - 1 ? i + w : -1 })
                {
                    if (j >= 0 && pass[j] && !seen[j]) { seen[j] = true; q.Enqueue(j); }
                }
            }
            return seen;
        }

        /// <summary>The cache returns exactly what a fresh computation would, as each signature field changes alone.</summary>
        internal static string CaseCache(int seed)
        {
            var r = new Random(seed);
            var cache = new SignatureCache<string>();
            Plant p = MakePlant(seed, false);
            var sig = new FootprintSignature { RootX = p.RootX, RootZ = p.RootZ, MaskId = 1, DrawX = p.DrawX, Visual = p.Visual(p.Growth),
                                               JitterX = p.Jx, JitterZ = p.Jz, BlockScale = p.Scale, Flip = p.Flip, Measured = true,
                                               Blocking = true, Selecting = true, OldEnough = true };
            var masks = new Dictionary<int, HugeMask> { { 1, p.Mask }, { 2, MakeMask(r, p.Mask.MeasuredSize, true) } };
            string Fresh(FootprintSignature s)
            {
                if (!s.Blocking || !s.OldEnough) return "-";
                HugeQuad q = K.Quad(s.RootX, s.RootZ, s.DrawX, s.Visual, s.JitterX, s.JitterZ);
                HugeMask m = masks[s.MaskId];
                List<long> b = K.ContactCells(s.RootX, s.RootZ, q, s.BlockScale, s.Flip, m);
                CellBox sel = K.SelectBox(s.RootX, s.RootZ, K.PictureBox(q, m, s.Flip), b);
                return Fmt(b) + "|" + sel.MinX + "," + sel.MinZ + "," + sel.MaxX + "," + sel.MaxZ + (s.Selecting ? "S" : "") + (s.Measured ? "M" : "");
            }
            for (int step = 0; step < 40; step++)
            {
                switch (r.Next(13))
                {
                    case 0: sig.RootX += 1; break;
                    case 1: sig.RootZ -= 1; break;
                    case 2: sig.MaskId = sig.MaskId == 1 ? 2 : 1; break;
                    case 3: sig.DrawX = r.NextDouble() < 0.5 ? 1f : R(r, 0.5f, 2f); break;
                    case 4: sig.Visual = R(r, p.VMin, p.VMax); break;
                    case 5: sig.JitterX = R(r, -0.05f, 0.05f); break;
                    case 6: sig.JitterZ = R(r, -0.05f, 0.05f); break;
                    case 7: sig.BlockScale = R(r, 0.5f, 1.5f); break;
                    case 8: sig.Flip = !sig.Flip; break;
                    case 9: sig.Measured = !sig.Measured; break;
                    case 10: sig.Blocking = !sig.Blocking; break;
                    case 11: sig.Selecting = !sig.Selecting; break;
                    default: sig.OldEnough = !sig.OldEnough; break;
                }
                Check(cache.Get(sig, Fresh) == Fresh(sig), "cache disagrees with a fresh computation after step " + step);
            }
            return "";
        }

        /// <summary>A blast or beam crossing many cells of one giant forwards one hit per (tick, source, owner).</summary>
        internal static string CaseDamage(int seed)
        {
            var r = new Random(seed);
            var d = new DamageDedup();
            int tick = r.Next(1000);
            var forwarded = new Dictionary<(int, long, int), int>();
            for (int i = 0; i < 200; i++)
            {
                if (r.Next(10) == 0) tick += 1 + r.Next(3);
                long src = r.Next(4);
                int owner = r.Next(3);
                bool f = d.ShouldForward(tick, src, owner);
                var key = (tick, src, owner);
                forwarded.TryGetValue(key, out int n);
                Check(f == (n == 0), f ? "forwarded twice for one source in one tick" : "dropped the first hit of a source");
                if (f) forwarded[key] = n + 1;
            }
            return forwarded.Count.ToString();
        }

        private static bool Family(string name, int n, int? one, Func<int, string> run)
        {
            int fails = 0;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? (i * 7919 + name.Length * 104729);
                Cases++;
                try
                {
                    run(seed);
                }
                catch (Exception e)
                {
                    if (fails++ < 5) Console.WriteLine("FAIL " + name + " seed " + seed + ": " + e.Message);
                }
                if (one.HasValue) break;
            }
            Console.WriteLine((fails == 0 ? "PASS " : "FAIL ") + name + ": " + (one.HasValue ? 1 : n) + " cases, " + fails + " failed");
            return fails == 0;
        }

        public static bool Run(double scale, int? one, string only)
        {
            int N(int baseN) => Math.Max(scale > 0 ? 1 : 0, (int)(baseN * scale));
            bool ok = true;
            if (only == null || only == "any") ok &= Family("any", N(20000), one, CaseAny);
            if (only == null || only == "full") ok &= Family("full", N(5000), one, CaseFull);
            if (only == null || only == "boundary") ok &= Family("boundary", N(5000), one, CaseBoundary);
            if (only == null || only == "symmetry") ok &= Family("symmetry", N(3000), one, CaseSymmetry);
            if (only == null || only == "ledger") ok &= Family("ledger", N(4000), one, CaseLedger);
            if (only == null || only == "planner") ok &= Family("planner", N(3000), one, CasePlanner);
            if (only == null || only == "cache") ok &= Family("cache", N(2000), one, CaseCache);
            if (only == null || only == "damage") ok &= Family("damage", N(2000), one, CaseDamage);
            if (only == null || only == "determinism")
            {
                ok &= Family("determinism", N(500), one, s =>
                {
                    Check(CaseAny(s) == CaseAny(s) && CaseBoundary(s) == CaseBoundary(s) && CaseFull(s) == CaseFull(s)
                          && CaseLedger(s) == CaseLedger(s) && CasePlanner(s) == CasePlanner(s), "a seed replayed differently");
                    return "";
                });
            }
            Console.WriteLine("hugethings fuzz: " + Cases + " cases, " + Checks + " checks");
            Console.WriteLine(ok ? "ALL PASS" : "FAILURES");
            return ok;
        }
    }
}
