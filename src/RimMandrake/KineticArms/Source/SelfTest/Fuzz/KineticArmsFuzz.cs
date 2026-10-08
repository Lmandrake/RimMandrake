// Approach B for KineticArms: seeded fuzz over the Verse-free kernel the mod calls (../../RM_KineticMath.cs):
//   geometry  direction / back-step / cone membership against an angle oracle, cone cells against a disc oracle, rotation symmetry
//   bolt      a whole shot (origin, destination, impact): the explosion centre sits behind the impact, everything thrown is ahead of it
//   charge    the pulse cannon's charge through random power / tick / fire sequences against a double-precision ledger
//   ruins     ruins loot picks against an independent weighted-pick oracle, edge rolls, toggles, roll-for round trip, stacks
//   looted    looted raider weapons: the rare gate, grenadier split, money fit, uniform pick; the money ceiling and floor
//   units     facings, force scaling, the charge threshold, shipped weight table
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.KineticArms.SelfTest
{
    internal static class KineticArmsFuzz
    {
        public static long Cases, Steps, ConesChecked, EdgeHits, ZeroWeightFit, ShotsFired, EmptyFits;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("0.#####", System.Globalization.CultureInfo.InvariantCulture); }

        private static readonly float[] Radii = { 0.5f, 1f, 1.5f, 1.9f, 2f, 2.5f, 3f, 4.5f, 6f };
        private static readonly float[] Cones = { 0f, 30f, 60f, 90f, 120f, 180f, 270f, 359f, 360f, 360.5f, 400f, 540f };

        // ════════════════════════ geometry ════════════════════════
        private static List<string> Geometry(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 7919 + 1);
                try
                {
                    // --- Dir
                    float ox = r.Next(-30, 30), oz = r.Next(-30, 30), tx = r.Next(-30, 30), tz = r.Next(-30, 30);
                    bool ok = RM_KineticMath.Dir(ox, oz, tx, tz, out float dx, out float dz);
                    bool zero = ox == tx && oz == tz;
                    Check(ok == !zero, "Dir ok=" + ok + " for a " + (zero ? "zero" : "non-zero") + " vector");
                    if (!ok) Check(dx == 0f && dz == 0f, "a refused Dir must return (0,0)");
                    else
                    {
                        Check(Math.Abs(Math.Sqrt(dx * dx + dz * dz) - 1.0) < 1e-4, "Dir not unit: " + F(dx) + "," + F(dz));
                        double vx = tx - ox, vz = tz - oz;
                        Check(Math.Abs(dx * vz - dz * vx) < 1e-3 * Math.Sqrt(vx * vx + vz * vz) && dx * vx + dz * vz > 0, "Dir not parallel to the vector");
                        // --- BackStep
                        int ix = r.Next(-50, 50), iz = r.Next(-50, 50);
                        RM_KineticMath.BackStep(ix, iz, dx, dz, out int bx, out int bz);
                        Check(Math.Abs(bx - ix) <= 1 && Math.Abs(bz - iz) <= 1, "back-step more than one cell");
                        Check(bx != ix || bz != iz, "back-step of a unit direction stayed on the impact cell");
                        Check((ix - bx) * dx + (iz - bz) * dz > 0, "back-step is not behind the impact (against the shot)");
                        RM_KineticMath.BackStep(ix, iz, -dx, -dz, out int cx2, out int cz2);
                        Check(cx2 + bx == 2 * ix && cz2 + bz == 2 * iz, "back-step is not odd-symmetric under reversing the shot");
                    }
                    RM_KineticMath.BackStep(7, 9, 0f, 0f, out int zx, out int zz);
                    Check(zx == 7 && zz == 9, "a zero direction must return the impact cell");

                    // --- InCone against an angle oracle (skip the boundary band, where the 1e-4 tolerance is the documented fuzz)
                    double ang = r.NextDouble() * 2 * Math.PI;
                    float ux = (float)Math.Cos(ang), uz = (float)Math.Sin(ang);
                    float cone = Cones[r.Next(Cones.Length)];
                    int pcx = r.Next(-10, 10), pcz = r.Next(-10, 10);
                    for (int k = 0; k < 12; k++)
                    {
                        int x = pcx + r.Next(-8, 9), z = pcz + r.Next(-8, 9);
                        bool got = RM_KineticMath.InCone(pcx, pcz, x, z, ux, uz, cone);
                        int vx2 = x - pcx, vz2 = z - pcz;
                        if (vx2 == 0 && vz2 == 0) { Check(!got, "the centre cell is in its own cone"); continue; }
                        if (cone >= 360f) { Check(got, "a 360+ cone must accept every other cell"); continue; }
                        double len = Math.Sqrt(vx2 * vx2 + vz2 * vz2);
                        double diff = Math.Acos(Math.Max(-1, Math.Min(1, (vx2 * ux + vz2 * uz) / len)));
                        double half = cone * 0.5 * Math.PI / 180.0;
                        // the kernel accepts cos >= cos(half) - 1e-4 (documented slack): skip the band where that tolerance, not the angle, decides
                        if (Math.Abs(Math.Cos(diff) - Math.Cos(half)) < 3e-4 || Math.Abs(diff - half) < 2e-3) continue;
                        Check(got == (diff < half), "InCone=" + got + " but the angle is " + F(diff * 180 / Math.PI) + " deg against half-cone " + F(cone / 2) + " for v=(" + vx2 + "," + vz2 + ") d=(" + F(ux) + "," + F(uz) + ")");
                    }
                    ConesChecked++;

                    // --- ConeCells against a disc oracle, kept impact, no centre, monotone in radius and cone
                    float rad = Radii[r.Next(Radii.Length)];
                    int ccx = r.Next(-6, 6), ccz = r.Next(-6, 6);
                    int iix = ccx + r.Next(-2, 3), iiz = ccz + r.Next(-2, 3);
                    var cells = RM_KineticMath.ConeCells(ccx, ccz, iix, iiz, ux, uz, rad, cone);
                    var set = new HashSet<(int, int)>(cells);
                    Check(set.Count == cells.Count, "ConeCells returned a duplicate cell");
                    Check(set.Contains((iix, iiz)), "the impact cell was dropped");
                    float r2 = rad * rad;
                    foreach (var c in cells)
                    {
                        if (c == (iix, iiz)) continue;
                        int ddx = c.Item1 - ccx, ddz = c.Item2 - ccz;
                        Check(ddx * ddx + ddz * ddz <= r2, "cell " + c + " is farther than the radius " + F(rad));
                        Check(!(ddx == 0 && ddz == 0), "the centre cell is in the cone cells");
                        Check(RM_KineticMath.InCone(ccx, ccz, c.Item1, c.Item2, ux, uz, cone), "a cone cell fails InCone");
                    }
                    int rr = (int)Math.Ceiling(rad);
                    for (int a = -rr; a <= rr; a++)
                        for (int b = -rr; b <= rr; b++)
                        {
                            int xx = ccx + a, zz2 = ccz + b;
                            bool want = a * a + b * b <= r2 && RM_KineticMath.InCone(ccx, ccz, xx, zz2, ux, uz, cone);
                            if (want) Check(set.Contains((xx, zz2)), "cell " + xx + "," + zz2 + " is in the disc and the cone but missing");
                        }
                    var bigger = RM_KineticMath.ConeCells(ccx, ccz, iix, iiz, ux, uz, rad + 1f, Math.Min(360f, cone + 40f));
                    Check(set.IsSubsetOf(bigger), "a larger radius/cone lost a cell");
                    Check(cells.Count <= (2 * rr + 1) * (2 * rr + 1) + 1, "more cells than the bounding square");
                    if (cone >= 360f) Check(cells.Count >= set.Count && set.Count >= (a0(rad, ccx, ccz, iix, iiz)), "a full cone missed part of the disc");

                    // --- exact rotation symmetry for the four facings
                    RM_KineticMath.Facing(0, out float nx, out float nz);
                    var north = RM_KineticMath.ConeCells(0, 0, nx > 0 ? 1 : 0, 1, nx, nz, rad, cone);
                    for (int rot = 1; rot < 4; rot++)
                    {
                        RM_KineticMath.Facing(rot, out float fx, out float fz);
                        Check(Math.Abs(fx * fx + fz * fz - 1f) < 1e-6f, "facing " + rot + " not unit");
                        // clockwise quarter turn: (x,z) -> (z,-x)
                        Func<(int, int), (int, int)> turn = p => (p.Item2, -p.Item1);
                        var expect = new HashSet<(int, int)>(north);
                        for (int t = 0; t < rot; t++) expect = new HashSet<(int, int)>(expect.Select(turn));
                        var itsImpact = (0, 1);
                        for (int t = 0; t < rot; t++) itsImpact = turn(itsImpact);
                        var got = RM_KineticMath.ConeCells(0, 0, itsImpact.Item1, itsImpact.Item2, fx, fz, rad, cone);
                        Check(expect.SetEquals(got), "facing " + rot + " cone cells are not the rotation of facing 0 (cone " + F(cone) + ", radius " + F(rad) + ")");
                    }
                    int big = r.Next(-1000, 1000);
                    RM_KineticMath.Facing(big, out float ax, out float az);
                    RM_KineticMath.Facing(((big % 4) + 4) % 4, out float bx2, out float bz2);
                    Check(ax == bx2 && az == bz2, "Facing(" + big + ") does not wrap mod 4");
                }
                catch (Exception e) { fails.Add("geometry seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // the disc area floor used only as a sanity lower bound for a full cone (every integer cell with d2 <= r2, minus the centre, plus the impact)
        private static int a0(float rad, int cx, int cz, int ix, int iz)
        {
            int rr = (int)Math.Ceiling(rad), n = 0; float r2 = rad * rad;
            for (int a = -rr; a <= rr; a++) for (int b = -rr; b <= rr; b++) if (a * a + b * b <= r2 && !(a == 0 && b == 0)) n++;
            bool inDisc = (ix - cx) * (ix - cx) + (iz - cz) * (iz - cz) <= r2 && !(ix == cx && iz == cz);
            return inDisc ? n : n + 1;
        }

        // ════════════════════════ bolt ════════════════════════
        private static List<string> Bolt(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 131 + 17);
                try
                {
                    float ox = r.Next(-20, 20), oz = r.Next(-20, 20);
                    float tx = ox + r.Next(-18, 19), tz = oz + r.Next(-18, 19);
                    if (!RM_KineticMath.Dir(ox, oz, tx, tz, out float dx, out float dz)) continue;
                    int ix = (int)tx, iz = (int)tz;
                    RM_KineticMath.BackStep(ix, iz, dx, dz, out int bx, out int bz);
                    float rad = Radii[r.Next(Radii.Length)];
                    float cone = new[] { 60f, 90f, 120f, 180f }[r.Next(4)];
                    var cells = RM_KineticMath.ConeCells(bx, bz, ix, iz, dx, dz, rad, cone);
                    ShotsFired++;
                    Check(cells.Contains((ix, iz)), "the impact cell is not hit");
                    Check(!cells.Contains((bx, bz)), "the explosion centre itself is hit (it lies behind the target)");
                    foreach (var c in cells)
                    {
                        if (c == (ix, iz)) continue;
                        // the radial throw from the centre must carry along the shot: positive component on the shot direction for cones up to 180
                        double along = (c.Item1 - bx) * dx + (c.Item2 - bz) * dz;
                        Check(along >= -1e-3, "cell " + c + " is behind the centre of a " + F(cone) + " deg shot (along " + F(along) + ")");
                        if (cone < 180f) Check(along > 0, "cell " + c + " is not ahead of the centre of a " + F(cone) + " deg shot");
                    }
                    // a cell dead ahead of the impact within the radius is always hit
                    int ahead = 1;
                    int axx = bx + (int)Math.Round(dx * (ahead + 1), MidpointRounding.AwayFromZero), azz = bz + (int)Math.Round(dz * (ahead + 1), MidpointRounding.AwayFromZero);
                    if (rad >= 2f && (axx - bx) * (axx - bx) + (azz - bz) * (azz - bz) <= rad * rad && !(axx == bx && azz == bz))
                        Check(cells.Contains((axx, azz)), "a cell " + (ahead + 1) + " steps straight ahead of the centre is missed");
                    // force scaling used by the bolt's DamageDef
                    float strength = (float)(r.NextDouble() * 3), baseForce = (float)(r.NextDouble() * 6 - 1);
                    float scaled = RM_KineticMath.ScaledForce(baseForce, strength);
                    Check(scaled >= 0f && (baseForce <= 0f ? scaled == 0f : Math.Abs(scaled - baseForce * strength) < 1e-4), "scaled force " + F(scaled) + " for base " + F(baseForce) + " x " + F(strength));
                }
                catch (Exception e) { fails.Add("bolt seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ charge ════════════════════════
        private enum CA { Tick, Power, Fire, Reload }
        private struct CAct { public CA kind; public int a; public override string ToString() { return kind + "(" + a + ")"; } }

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

        private static string RunCharge(IList<CAct> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x5bd1e995);
            int capacity = rr.Next(1, 13), recharge = new[] { 1, 2, 7, 60, 600, 1200, 2400, 7200 }[rr.Next(8)];
            float charge = rr.Next(2) == 0 ? capacity : 0f;
            double model = charge; bool powered = true; int shots = 0; long poweredTicks = 0;
            int step = 0;
            try
            {
                foreach (var a in acts)
                {
                    step++;
                    if (count) Steps++;
                    switch (a.kind)
                    {
                        case CA.Power: powered = a.a % 3 != 0; break;
                        case CA.Tick:
                        {
                            int ticks = 1 + a.a % 3000;
                            float before = charge;
                            for (int t = 0; t < ticks; t++) charge = RM_KineticMath.Recharge(charge, capacity, recharge, 1, powered);
                            if (powered) { model = Math.Min(capacity, model + (double)ticks / recharge); poweredTicks += ticks; }
                            Check(powered ? charge >= before - 1e-6f : charge == before, (powered ? "powered" : "unpowered") + " ticks moved the charge " + F(before) + " -> " + F(charge));
                            // the same span in one call lands on the same charge (the building ticks one at a time)
                            float oneShot = RM_KineticMath.Recharge(before, capacity, recharge, ticks, powered);
                            Check(Math.Abs(oneShot - charge) <= 1e-3f + ticks * 1e-6f, "one call of " + ticks + " ticks gives " + F(oneShot) + " but " + ticks + " single ticks give " + F(charge));
                            break;
                        }
                        case CA.Fire:
                            if (RM_KineticMath.CanFire(charge)) { float c0 = charge; charge = RM_KineticMath.Spend(charge); model = Math.Max(0, model - 1); shots++; Check(Math.Abs((c0 - charge) - 1f) < 1e-4f, "a shot spent " + F(c0 - charge) + " charges"); }
                            else Check(charge < 1f, "CanFire refused a charge of " + F(charge));
                            break;
                        case CA.Reload: charge = Math.Min(charge, capacity); break;
                    }
                    Check(charge >= 0f && charge <= capacity + 1e-4f, "charge " + F(charge) + " outside 0.." + capacity);
                    Check(Math.Abs(charge - model) < 2e-3 + poweredTicks * 6e-7, "charge " + F(charge) + " drifted from the ledger " + F(model) + " after " + poweredTicks + " powered ticks");
                }
                // full cycle: from empty, powered, exactly one recharge interval buys a shot (within one tick of float slack)
                float c = 0f; int need = 0;
                while (!RM_KineticMath.CanFire(c) && need < recharge + 5) { c = RM_KineticMath.Recharge(c, Math.Max(1, capacity), recharge, 1, true); need++; }
                Check(need >= recharge - 1 && need <= recharge + 1, "the first shot took " + need + " ticks at " + recharge + " ticks per charge");
            }
            catch (Exception e) { return "step " + step + ": " + e.Message; }
            return null;
        }

        private static List<string> Charge(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 3; s++)
            {
                Cases++;
                var r = new Random(s * 101 + 13);
                int len = 5 + r.Next(60);
                var acts = new List<CAct>();
                for (int i = 0; i < len; i++) { int k = r.Next(10); acts.Add(new CAct { kind = k < 5 ? CA.Tick : k < 7 ? CA.Power : k < 9 ? CA.Fire : CA.Reload, a = r.Next(1 << 14) }); }
                string msg = RunCharge(acts, s, true);
                if (msg != null)
                {
                    var small = Shrink(acts, t => RunCharge(t, s, false) != null);
                    fails.Add("charge seed " + s + ": " + RunCharge(small, s, false) + " | " + string.Join(" ", small));
                }
            }
            return fails;
        }

        // ════════════════════════ ruins ════════════════════════
        private static readonly float[] EdgeRolls = { 0f, 1e-7f, 0.5f, 0.25f, 0.75f, 0.9999f, 0.99999994f /* BitDecrement(1f) */ };

        private static float W(IList<float> w, int i) { if (w == null) return 1f; float v = i < w.Count ? w[i] : 0f; return v > 0f ? v : 0f; }

        private static List<string> Ruins(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 977 + 5);
                try
                {
                    int count = r.Next(1, 10);
                    var enabled = Enumerable.Range(0, count).Select(i => r.Next(5) != 0).ToList();
                    List<float> weights = null;
                    int wk = r.Next(6);
                    if (wk == 5) weights = Enumerable.Range(0, count).Select(i => r.Next(2) == 0 ? 0f : -1f).ToList();      // nothing has weight: uniform fallback
                    else if (wk > 0)
                    {
                        int wl = wk == 1 ? Math.Max(0, count - r.Next(1, 3)) : count;      // shorter than the toggles: missing weights are 0
                        weights = Enumerable.Range(0, wl).Select(i => r.Next(4) == 0 ? 0f : (r.Next(12) == 0 ? -(float)r.Next(1, 5) : r.Next(1, 40))).ToList();
                    }
                    float chance = r.Next(6) == 0 ? 0f : (float)r.NextDouble();
                    var fit = Enumerable.Range(0, count).Where(i => enabled[i]).ToList();
                    double total = fit.Sum(i => (double)W(weights, i));
                    // --- gating
                    Check(RM_KineticMath.PickRuins(null, weights, 1f, 0f, 0f) == -1, "null toggles must pick nothing");
                    Check(RM_KineticMath.PickRuins(enabled, weights, 0f, 0f, 0f) == -1, "chance 0 must pick nothing");
                    if (chance > 0f) Check(RM_KineticMath.PickRuins(enabled, weights, chance, chance, 0.5f) == -1, "roll1 == chance must pick nothing");
                    // --- sweep roll2 over a grid plus the edges
                    int N = 400; int prev = -1; var counts = new Dictionary<int, int>();
                    var rolls = Enumerable.Range(0, N).Select(i => (i + 0.5f) / N).Concat(EdgeRolls).ToList();
                    for (int ri = 0; ri < rolls.Count; ri++)
                    {
                        float roll2 = rolls[ri];
                        bool isEdge = ri >= N;
                        if (isEdge) EdgeHits++;
                        int got = RM_KineticMath.PickRuins(enabled, weights, 1f, 0f, roll2);
                        if (fit.Count == 0) { Check(got == -1, "nothing enabled but picked " + got); EmptyFits++; continue; }
                        Check(fit.Contains(got), "picked " + got + " which is disabled or out of range");
                        if (total > 0) Check(W(weights, got) > 0f, "picked " + got + " whose weight is 0 although a total of " + F(total) + " is available (roll " + F(roll2) + ")");
                        else ZeroWeightFit++;
                        if (!isEdge)
                        {
                            Check(got >= prev, "pick fell from " + prev + " to " + got + " as the roll rose to " + F(roll2));
                            prev = got;
                            counts[got] = counts.TryGetValue(got, out int cc) ? cc + 1 : 1;
                        }
                        // oracle away from cumulative boundaries
                        if (total > 0)
                        {
                            double target = (double)roll2 * total, acc = 0; int want = -1; double nearest = double.MaxValue;
                            foreach (int i in fit) { acc += W(weights, i); nearest = Math.Min(nearest, Math.Abs(target - acc)); if (want < 0 && target < acc) want = i; }
                            if (nearest > 1e-3 * total && want >= 0) Check(got == want, "roll " + F(roll2) + " picked " + got + ", the oracle says " + want);
                        }
                    }
                    // --- frequencies track the weights
                    if (fit.Count > 0)
                        foreach (int i in fit)
                        {
                            double share = total > 0 ? W(weights, i) / total : 1.0 / fit.Count;
                            double seen = (counts.TryGetValue(i, out int c) ? c : 0) / (double)N;
                            Check(Math.Abs(seen - share) <= 2.0 / N + 1e-9, "weapon " + i + " picked " + F(seen) + " of the time, weight share is " + F(share));
                        }
                    // --- roll-for round trip: the roll it hands out lands on the weapon asked for
                    for (int i = 0; i < count; i++)
                    {
                        float rf = RM_KineticMath.RuinsRollFor(enabled, weights, i);
                        bool pickable = enabled[i] && (total <= 0 || W(weights, i) > 0f);
                        if (!pickable) { Check(rf == -1f, "RuinsRollFor(" + i + ") = " + F(rf) + " for a weapon that can never be picked"); continue; }
                        Check(rf >= 0f && rf < 1f, "RuinsRollFor(" + i + ") = " + F(rf) + " outside [0,1)");
                        int back = RM_KineticMath.PickRuins(enabled, weights, 1f, 0f, rf);
                        Check(back == i, "RuinsRollFor(" + i + ") = " + F(rf) + " but that roll picks " + back);
                    }
                    Check(RM_KineticMath.RuinsRollFor(enabled, weights, count + 3) == -1f && RM_KineticMath.RuinsRollFor(enabled, weights, -1) == -1f, "RuinsRollFor of an index outside the table must be -1");
                    // --- stacks
                    float sr = (float)r.NextDouble();
                    int st = RM_KineticMath.RuinsStack(true, sr);
                    Check(st >= 5 && st <= 12, "stack " + st + " outside 5..12");
                    Check(st == Math.Min(12, 5 + (int)(sr * 8f)), "stack " + st + " for roll " + F(sr) + ", the table says 5 + floor(roll * 8)");
                    Check(RM_KineticMath.RuinsStack(true, Math.Min(0.9999f, sr + 0.1f)) >= st, "stack fell as the roll rose");
                    Check(RM_KineticMath.RuinsStack(true, -3f) == 5 && RM_KineticMath.RuinsStack(true, 7f) == 12 && RM_KineticMath.RuinsStack(false, sr) == 1, "stack clamps / single weapons");
                }
                catch (Exception e) { fails.Add("ruins seed " + s + ": " + e.Message); }
            }
            return fails;
        }

                // ════════════════════════ looted ════════════════════════
        private static List<string> Looted(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 331 + 9);
                try
                {
                    int count = r.Next(1, 9);
                    var opts = new RM_KineticMath.LootOption[count];
                    for (int i = 0; i < count; i++) opts[i] = new RM_KineticMath.LootOption { grenade = r.Next(4) == 0, price = r.Next(0, 3000), enabled = r.Next(5) != 0 };
                    bool grenadier = r.Next(3) == 0;
                    float money = r.Next(0, 2000);
                    float chance = r.Next(5) == 0 ? 0f : (float)(r.NextDouble() * 0.2);
                    Check(RM_KineticMath.PickLooted(null, grenadier, money, 0.5f, 0f, 0f) == -1, "null options must pick nothing");
                    var fit = Enumerable.Range(0, count).Where(i => opts[i].enabled && opts[i].grenade == grenadier && opts[i].price <= money).ToList();
                    if (fit.Count == 0) EmptyFits++;
                    // gate: exactly the rolls below the chance pass
                    int N = 1000, pass = 0;
                    for (int i = 0; i < N; i++)
                    {
                        float roll1 = (i + 0.5f) / N;
                        int got = RM_KineticMath.PickLooted(opts, grenadier, money, chance, roll1, 0.5f);
                        bool gate = chance > 0f && roll1 < chance;
                        if (!gate || fit.Count == 0) Check(got == -1, "gate " + gate + " fit " + fit.Count + " but picked " + got);
                        else { Check(fit.Contains(got), "picked " + got + " which is not an enabled, same-kind, affordable option"); pass++; }
                    }
                    if (fit.Count > 0)
                    {
                        int expected = (int)Enumerable.Range(0, N).Count(i => (i + 0.5f) / N < chance);
                        Check(pass == expected, "the gate passed " + pass + " of " + N + " pawns, " + expected + " rolled below the chance " + F(chance));
                        if (chance > 0f) Check(RM_KineticMath.PickLooted(opts, grenadier, money, chance, chance, 0.5f) == -1, "roll1 == chance must keep the raider's own gun");
                        // uniform over the fit set; edge rolls stay inside it
                        var seen = new int[count]; int M = fit.Count * 50;
                        for (int i = 0; i < M; i++) seen[RM_KineticMath.PickLooted(opts, grenadier, money, 1f, 0f, (i + 0.5f) / M)]++;
                        foreach (int i in fit) Check(seen[i] == 50, "option " + i + " picked " + seen[i] + " of " + M + ", uniform would be 50");
                        foreach (float e in EdgeRolls) { EdgeHits++; Check(fit.Contains(RM_KineticMath.PickLooted(opts, grenadier, money, 1f, 0f, e)), "edge roll " + F(e) + " left the fit set"); }
                        // a grenadier never gets a gun and nobody else a grenade
                        foreach (int i in fit) Check(opts[i].grenade == grenadier, "grenadier split broken");
                    }
                    // money: ceiling, floor, monotone
                    float kind = r.Next(0, 30000), floor = r.Next(0, 1500);
                    float m = RM_KineticMath.LootMoney(kind, floor);
                    Check(m <= RM_KineticMath.RaiderPriceCeiling, "money " + F(m) + " above the ceiling");
                    Check(m >= Math.Min(Math.Max(kind, floor), RM_KineticMath.RaiderPriceCeiling) - 1e-3f && m <= Math.Max(kind, floor) + 1e-3f, "money " + F(m) + " is not min(max(kind,floor),ceiling)");
                    Check(RM_KineticMath.LootMoney(kind + 100f, floor) >= m && RM_KineticMath.LootMoney(kind, floor + 100f) >= m, "money fell as an input rose");
                }
                catch (Exception e) { fails.Add("looted seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Steps += 20;
                Check(RM_KineticMath.CanFire(1f) && RM_KineticMath.CanFire(1f - 1e-5f) && !RM_KineticMath.CanFire(1f - 2e-4f) && !RM_KineticMath.CanFire(0f), "charge threshold");
                Check(RM_KineticMath.Spend(1f) == 0f && RM_KineticMath.Spend(0.2f) == 0f && RM_KineticMath.Spend(3.5f) == 2.5f, "spend");
                Check(RM_KineticMath.Recharge(5f, 4, 100, 10, true) == 4f && RM_KineticMath.Recharge(5f, 4, 100, 10, false) == 4f, "a charge above a lowered capacity is clamped");
                Check(RM_KineticMath.Recharge(1f, 4, 0, 10, true) == 1f && RM_KineticMath.Recharge(1f, 4, -5, 10, true) == 1f, "a zero recharge time must not divide by zero or add charge");
                // BackStep rounds half away from zero (a diagonal 0.5 component still steps back)
                RM_KineticMath.BackStep(10, 10, 0.5f, 0.5f, out int hx, out int hz);
                Check(hx == 9 && hz == 9, "back-step of (0.5,0.5) must step to (9,9), got " + hx + "," + hz);
                RM_KineticMath.BackStep(10, 10, -0.5f, 0.5f, out hx, out hz);
                Check(hx == 11 && hz == 9, "back-step of (-0.5,0.5) must step to (11,9), got " + hx + "," + hz);
                // cone boundaries on the grid, facing north (0,1): the cells that sit exactly on a cone's edge belong to it
                bool In(int x, int z, float cone) { return RM_KineticMath.InCone(0, 0, x, z, 0f, 1f, cone); }
                Check(In(1, 1, 90f) && In(-1, 1, 90f) && !In(1, -1, 90f) && !In(1, 0, 90f) && !In(0, -1, 90f), "90 degree cone edges (forward diagonals in, sides and rear out)");
                Check(In(1, 0, 180f) && In(-1, 0, 180f) && In(0, 1, 180f) && !In(0, -1, 180f) && !In(1, -1, 180f), "180 degree cone edges (perpendicular cells in, rear out)");
                Check(In(1, -1, 270f) && In(-1, -1, 270f) && !In(0, -1, 270f), "270 degree cone edges (rear diagonals in, dead astern out)");
                Check(In(1, 2, 60f) && !In(1, 1, 60f) && In(0, 5, 60f), "60 degree cone: 26.6 deg in, 45 deg out");
                Check(In(0, -1, 360f) && In(0, -1, 360.5f) && In(0, -1, 540f), "a cone of 360 or more accepts the cell dead astern");
                Check(RM_KineticMath.ScaledForce(2.5f, 0f) == 0f && RM_KineticMath.ScaledForce(0f, 3f) == 0f && RM_KineticMath.ScaledForce(2f, -1f) == 0f, "force scaling zeros");
                var rw = RM_KineticMath.RuinsWeights;
                Check(rw.Length == 8 && rw.All(x => x > 0f), "eight positive ruins weights (PROVISIONAL tuning, index-aligned with the weapon table)");
                Check(rw.Take(7).All(x => x > rw[7]), "the grav-ram must be the rarest ruins find");
                Check(Math.Abs(rw.Sum() - 110f) < 1e-3f, "shipped ruins weights sum to 110 (PROVISIONAL)");
                Check(RM_KineticMath.RaiderPriceCeiling == 1000f, "raider price ceiling is the documented 1000 (a grav-ram is never carried by a raider)");
            }
            catch (Exception e) { fails.Add("units: " + e.Message); }
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
                ("geometry", () => Geometry(N(5000), S(1))),
                ("bolt", () => Bolt(N(8000), S(1))),
                ("charge", () => Charge(N(3000), S(1))),
                ("ruins", () => Ruins(N(4000), S(1))),
                ("looted", () => Looted(N(3000), S(1))),
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
            if (only == null)
            {
                Console.WriteLine($"reached: cones {ConesChecked}, shots {ShotsFired}, edge rolls {EdgeHits}, all-zero-weight fits {ZeroWeightFit}, empty fits {EmptyFits}");
                if (!oneSeed.HasValue && scale >= 1 && (ConesChecked == 0 || ShotsFired == 0 || EdgeHits == 0 || ZeroWeightFit == 0 || EmptyFits == 0)) { Console.WriteLine("FAIL the fuzz never reached cones, shots, edge rolls, zero-weight fits and empty fits (blind)"); ok = false; }
            }
            Console.WriteLine($"kineticarms fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
