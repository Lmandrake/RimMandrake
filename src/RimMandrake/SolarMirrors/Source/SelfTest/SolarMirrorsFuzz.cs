// Approach B for SolarMirrors: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_MirrorKernel.cs):
//   math      sun vector, moving sun, normal / reflect / cosine law, ground hit, 4-connected beam walk, hysteresis, quantise, settings clamps
//   pass      random worlds (roofs, walls, closed doors, mirrors of size 1-2, targets, sun) -> the whole light pass against an
//             independent reference pass, plus invariants: conservation of light, no light behind a blocker, fire-once, depth cap, relay bounds
//   sequence  action sequences (add / remove / aim / build / sun / run) on ONE persistent pass: stale light never survives, == a fresh pass
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.SolarMirrors.SelfTest
{
    internal static partial class SolarMirrorsFuzz
    {
        public static long Relays, DeepChains, Blocked, SkyMisses, EdgeMisses, Commits, BigSpots, Cycles, Untargeted, Targeted, NightPasses, Idempotent, Glazed,
            Fields, FieldSolvable, FieldAccepted, FieldTooBig, HintWalks;

        // ═════════ the test world ═════════
        private sealed class World : IRM_BeamWorld
        {
            public int W, H;
            public bool[] roof, wall, door, aperture;
            public int[] owner;                       // mirror index standing on the cell, or -1
            public int Width { get { return W; } }
            public int Height { get { return H; } }
            public string BlockerEdge { get { return "edge"; } }
            public string BlockerSky { get { return "sky"; } }
            public string BlockerRoof { get { return "roof"; } }
            public World(int w, int h)
            {
                W = w; H = h;
                roof = new bool[w * h]; wall = new bool[w * h]; door = new bool[w * h]; aperture = new bool[w * h]; owner = new int[w * h];
                for (int i = 0; i < owner.Length; i++) owner[i] = -1;
            }
            public bool Roofed(int x, int z) { return roof[z * W + x]; }
            public bool IsAperture(int x, int z) { return aperture[z * W + x]; }
            public string CellBlocks(int x, int z, int mirrorIndex)
            {
                int i = z * W + x;
                if (owner[i] >= 0) return null;       // mirrors never block
                if (door[i]) return "door";
                if (wall[i]) return "wall";
                return null;
            }
            public int MirrorAt(int x, int z) { return owner[z * W + x]; }
        }

        private static RM_Vec Unit(Random r, bool upward)
        {
            double a = r.NextDouble() * Math.PI * 2, e = (upward ? 0.15 + r.NextDouble() * 1.3 : r.NextDouble() * 2 - 1);
            return new RM_Vec((float)(Math.Cos(a) * Math.Cos(e)), (float)Math.Sin(e), (float)(Math.Sin(a) * Math.Cos(e))).Normalized;
        }

        // ═════════ math ═════════
        private static string MathCase(int seed)
        {
            var r = new Random(seed);
            // sun vector
            {
                float sx = (float)(r.NextDouble() * 2 - 1), sz = (float)(r.NextDouble() * 2 - 1);
                float el = (float)(r.NextDouble() * 140 - 25);
                RM_Vec s = RM_MirrorKernel.SunVector(sx, sz, el);
                Check(Near(Math.Sqrt(s.SqrMagnitude), 1.0, 2e-5), "sun vector is not a unit vector");
                Check(s.Y >= -1e-6f, "sun below the horizon from SunVector (elevation is clamped to 0..90)");
                double ce = Math.Min(90, Math.Max(0, el)) * Math.PI / 180;
                Check(Near(s.Y, Math.Sin(ce), 2e-5), "sun height != sin(clamped elevation)");
                double len = Math.Sqrt((double)sx * sx + (double)sz * sz);
                if (len > 1e-3)
                {
                    double h = Math.Sqrt((double)s.X * s.X + (double)s.Z * s.Z);
                    if (h > 1e-3) Check(Near((s.X * (double)sx + s.Z * (double)sz) / (h * len), -1.0, 1e-3), "the sun does not stand opposite the shadow direction");
                }
                RM_Vec up = RM_MirrorKernel.SunVector(0f, 0f, 40f);
                Check(up.X == 0f && up.Y == 1f && up.Z == 0f, "a zero shadow direction must put the sun straight up");
            }
            // moving sun
            {
                float lat = (float)(r.NextDouble() * 180 - 90);
                float d = (float)(0.01 + r.NextDouble() * 0.24);
                RM_Vec noon = RM_Vec.Zero, am = RM_Vec.Zero, pm = RM_Vec.Zero;
                Check(RM_MirrorKernel.MovingSun(0.5f, lat, out noon), "no sun at noon");
                Check(!RM_MirrorKernel.MovingSun(0.25f - d, lat, out _), "sun before dawn");
                Check(!RM_MirrorKernel.MovingSun(0.75f + d, lat, out _), "sun after dusk");
                Check(!RM_MirrorKernel.MovingSun(0.0f, lat, out _) && !RM_MirrorKernel.MovingSun(1.0f, lat, out _), "sun at midnight");
                Check(RM_MirrorKernel.MovingSun(0.5f - d, lat, out am) && RM_MirrorKernel.MovingSun(0.5f + d, lat, out pm), "no sun in the day");
                Check(Near(Math.Sqrt(am.SqrMagnitude), 1.0, 2e-5), "moving sun not unit");
                Check(am.Y >= 0f && pm.Y >= 0f && noon.Y >= 0f, "moving sun below the horizon");
                double peak = 90 - Math.Min(89.0, Math.Abs((double)lat));
                Check(Near(noon.Y, Math.Sin(peak * Math.PI / 180), 3e-4), $"noon elevation is not 90-|lat| ({noon.Y} vs {Math.Sin(peak * Math.PI / 180)})");
                Check(am.X > 0f && pm.X < 0f, "the sun must rise in the east (+x) and set in the west");
                Check(Near(am.X, -pm.X, 2e-4) && Near(am.Y, pm.Y, 2e-4) && Near(am.Z, pm.Z, 2e-4), "morning and afternoon are not mirror images about noon");
                if (lat > 1f) Check(noon.Z <= 0f || peak > 89.5, "northern noon sun must lean toward the equator (south, -z)");
                if (lat < -1f) Check(noon.Z >= 0f || peak > 89.5, "southern noon sun must lean toward the equator (north, +z)");
                Check(am.Y <= noon.Y + 1e-4f, "the sun is higher in the morning than at noon");
            }
            // normal / reflect / cosine law
            {
                RM_Vec s = Unit(r, true), t = Unit(r, false);
                RM_Vec n = RM_MirrorKernel.Normal(s, t);
                Check(Near(Math.Sqrt(n.SqrMagnitude), 1.0, 2e-5), "normal not unit");
                if (RM_Vec.Dot(s, t) > -0.999f)
                {
                    RM_Vec o = RM_MirrorKernel.Reflect(s, n);
                    Check(Near(o.X, t.X, 3e-4) && Near(o.Y, t.Y, 3e-4) && Near(o.Z, t.Z, 3e-4), "Reflect(in, Normal(in,out)) != out");
                    Check(Near(RM_MirrorKernel.Cosine(n, s), RM_MirrorKernel.Efficiency(s, t), 3e-4), "cosine law: n.s != sqrt((1+s.t)/2)");
                }
                float e = RM_MirrorKernel.Efficiency(s, t);
                Check(e >= 0f && e <= 1.00001f, "efficiency outside [0,1]");
                Check(Near(RM_MirrorKernel.Efficiency(s, s), 1.0, 1e-6), "efficiency of a straight bounce is not 1");
                Check(Near(RM_MirrorKernel.Efficiency(s, -1f * s), 0.0, 1e-3), "efficiency of a reversal is not 0");
                Check(RM_MirrorKernel.Cosine(-1f * s, s) == 0f, "a back face passed light");
                Check(RM_MirrorKernel.Cosine(n, s) >= 0f, "negative cosine");
                RM_Vec back = RM_MirrorKernel.Normal(s, -1f * s);
                Check(back.X == s.X && back.Y == s.Y && back.Z == s.Z, "opposite in/out must fall back to the incoming direction as the normal");
            }
            // ground hit
            {
                float fx = (float)(r.NextDouble() * 50), fz = (float)(r.NextDouble() * 50), range = (float)(1 + r.NextDouble() * 40);
                RM_Vec d = Unit(r, false);
                float x, z;
                bool hit = RM_MirrorKernel.GroundHit(fx, 1.5f, fz, d, range, out x, out z);
                if (d.Y > -0.01f) Check(!hit, "a ray into the sky / skimming the ground hit the ground");
                else
                {
                    double k = 1.5 / -d.Y, dx = d.X * k, dz = d.Z * k, dist = Math.Sqrt(dx * dx + dz * dz);
                    if (dist > range * 1.0001) Check(!hit, "ground hit beyond maxRange");
                    else if (dist < range * 0.9999)
                    {
                        Check(hit, "ground hit within maxRange was missed");
                        Check(Near(x, fx + dx, 1e-3) && Near(z, fz + dz, 1e-3), "ground hit point is off the ray");
                    }
                }
            }
            // reflectivity / clamps / daylight / blind gain
            {
                float b = (float)r.NextDouble(), row = (float)r.NextDouble(), mult = (float)(r.NextDouble() * 2);
                float v = RM_MirrorKernel.Reflectivity(b, true, row, mult);
                Check(v >= 0f && v <= 1f, "reflectivity outside [0,1]");
                Check(Near(v, Math.Min(1.0, row * (double)mult), 1e-6), "a stuff row must replace the base reflectivity");
                Check(Near(RM_MirrorKernel.Reflectivity(b, false, row, mult), Math.Min(1.0, b * (double)mult), 1e-6), "no stuff row must use the base reflectivity");
                Check(RM_MirrorKernel.Reflectivity(b, true, row, 0f) == 0f, "multiplier 0 must dim the mirror to nothing");
                Check(RM_MirrorKernel.Reflectivity(9f, false, 0f, 9f) == 1f, "reflectivity is not capped at 1");
                int iv = r.Next(-500, 3000);
                int pi = RM_MirrorKernel.PassInterval(iv), dc = RM_MirrorKernel.DepthCap(iv % 12);
                Check(pi >= 125 && pi <= 1000 && (iv < 125 || iv > 1000 || pi == iv), "pass interval not clamped to 125..1000");
                Check(dc >= 1 && dc <= 6 && ((iv % 12) < 1 || (iv % 12) > 6 || dc == iv % 12), "depth cap not clamped to 1..6");
                float g1 = (float)(r.NextDouble() * 1.2), g2 = g1 + (float)r.NextDouble() * 0.3f;
                float d1 = RM_MirrorKernel.Daylight(g1), d2 = RM_MirrorKernel.Daylight(g2);
                Check(d1 >= 0f && d1 <= 1f && d2 >= d1 - 1e-6f, "daylight not monotone in [0,1]");
                Check(RM_MirrorKernel.Daylight(0.1f) == 0f && RM_MirrorKernel.Daylight(0.6f) == 1f && RM_MirrorKernel.Daylight(-1f) == 0f && RM_MirrorKernel.Daylight(5f) == 1f, "daylight end points");
                float l = (float)(r.NextDouble() * 3), perDay = (float)(r.NextDouble() * 10);
                int itv = RM_MirrorKernel.PassInterval(r.Next(125, 1001));
                float gain = RM_MirrorKernel.BlindGain(l, perDay, itv);
                if (l < 0.5f) Check(gain == 0f, "glare gain below the 0.5 light threshold");
                else Check(Near(gain, perDay * Math.Min(1.0, l) * itv / 60000.0, 1e-6), "glare gain != perDay * min(1,l) * interval / day");
                Check(RM_MirrorKernel.BlindGain(2f, perDay, itv) == RM_MirrorKernel.BlindGain(1f, perDay, itv), "glare gain keeps growing past full light");
                Check(RM_MirrorKernel.Quantise(0f) == 0, "quantise(0) != 0");
                float q1 = (float)(r.NextDouble() * 4), q2 = q1 + (float)r.NextDouble();
                Check(RM_MirrorKernel.Quantise(q2) >= RM_MirrorKernel.Quantise(q1), "quantise not monotone");
                Check(Math.Abs(RM_MirrorKernel.Quantise(q1) * 0.05 - q1) <= 0.0251, "quantise error beyond half a step");
            }
            // hysteresis as a state machine
            {
                float off = (float)(r.NextDouble() * 0.6), on = off + 0.01f + (float)(r.NextDouble() * 0.5);
                bool lit = false, refLit = false;
                for (int k = 0; k < 40; k++)
                {
                    float l = (float)(r.NextDouble() * 1.2);
                    lit = RM_MirrorKernel.Hysteresis(lit, l, on, off);
                    if (!refLit && l >= on) refLit = true; else if (refLit && l < off) refLit = false;
                    Check(lit == refLit, $"hysteresis state {lit} != reference {refLit} at light {l} (on {on}, off {off})");
                    if (l >= off && l < on) Check(true, "");
                }
                Check(!RM_MirrorKernel.Hysteresis(false, (on + off) / 2, on, off), "the dead band turned an unlit stone on");
                Check(RM_MirrorKernel.Hysteresis(true, (on + off) / 2, on, off), "the dead band turned a lit stone off");
            }
            // NormalFor
            {
                var m = new RM_MirrorSpec { faceX = 5.5f, faceZ = 5.5f, targetX = r.Next(0, 20), targetZ = r.Next(0, 20), targetValid = true, holdsTarget = true, tracking = r.Next(2) == 0, savedNormal = Unit(r, true) };
                RM_Vec s = Unit(r, true);
                bool commit;
                RM_Vec n = RM_MirrorKernel.NormalFor(m, s, out commit);
                Check(commit == m.tracking, "only a tracking mirror commits the re-aimed normal");
                RM_Vec dirTo = RM_MirrorKernel.DirTo(m, m.targetX, m.targetZ);
                Check(Near(Math.Sqrt(dirTo.SqrMagnitude), 1.0, 2e-5), "DirTo not unit");
                var exp = RM_MirrorKernel.Normal(s, dirTo);
                Check(n.X == exp.X && n.Y == exp.Y && n.Z == exp.Z, "a mirror holding its target must aim at it");
                m.holdsTarget = false;
                RM_Vec n2 = RM_MirrorKernel.NormalFor(m, s, out commit);
                Check(!commit && n2.X == m.savedNormal.X && n2.Y == m.savedNormal.Y && n2.Z == m.savedNormal.Z, "a static mirror must keep its saved normal and never commit");
            }
            // the beam walk
            {
                int x0 = r.Next(-6, 25), z0 = r.Next(-6, 25), x1 = r.Next(-6, 25), z1 = r.Next(-6, 25);
                var rec = new Rec { stopAt = -1 };
                bool clear = RM_MirrorKernel.LineClear(x0, z0, x1, z1, ref rec);
                if (rec.cells == null) rec.cells = new List<Pt>();
                Check(clear, "an all-clear visitor reported a blocked beam");
                int dx = Math.Abs(x1 - x0), dz = Math.Abs(z1 - z0);
                int want = Math.Max(0, dx + dz - 1);
                Check(rec.cells.Count == want, $"walk ({x0},{z0})->({x1},{z1}) visited {rec.cells.Count} cells, want {want} (strictly between)");
                int px = x0, pz = z0;
                for (int k = 0; k < rec.cells.Count; k++)
                {
                    var c = rec.cells[k];
                    Check(Math.Abs(c.x - px) + Math.Abs(c.z - pz) == 1, "the beam walk is not 4-connected");
                    Check(c.x >= Math.Min(x0, x1) && c.x <= Math.Max(x0, x1) && c.z >= Math.Min(z0, z1) && c.z <= Math.Max(z0, z1), "the beam walk left the bounding box");
                    Check(Dist(x0, z0, x1, z1, c.x, c.z) <= 1.0001, "a beam cell is more than a cell from the ideal line");
                    Check(!(c.x == x1 && c.z == z1) && !(c.x == x0 && c.z == z0), "the walk visited its own endpoint");
                    px = c.x; pz = c.z;
                }
                if (dx + dz >= 1) Check(Math.Abs(x1 - px) + Math.Abs(z1 - pz) == 1, "the walk does not end next to the target");
                if (rec.cells.Count > 0)
                {
                    int stop = r.Next(rec.cells.Count);
                    var blk = new Rec { stopAt = stop };
                    bool c2 = RM_MirrorKernel.LineClear(x0, z0, x1, z1, ref blk);
                    Check(!c2, "a blocked cell did not stop the beam");
                    Check(blk.cells.Count == stop + 1, "the walk kept going after a blocked cell");
                    Check(blk.cells[stop].x == rec.cells[stop].x && blk.cells[stop].z == rec.cells[stop].z, "a blocked walk took a different route");
                }
                else
                {
                    var blk = new Rec { stopAt = 0 };
                    Check(RM_MirrorKernel.LineClear(x0, z0, x1, z1, ref blk), "a beam with no cells between its ends was blocked");
                }
            }
            // dust, concentration, room heat, dazzle, heliograph reach (SOLAR_MIRRORS_BUILD_1)
            {
                float d0 = (float)(r.NextDouble() * 1.4 - 0.2), perDay = (float)(r.NextDouble() * 5), loss = (float)(r.NextDouble() * 1.2 - 0.1);
                int t = r.Next(-100, 200000);
                float d1 = RM_MirrorKernel.DustAfter(d0, true, perDay, t), dCalm = RM_MirrorKernel.DustAfter(d0, false, perDay, t);
                double c0 = Math.Min(1, Math.Max(0, d0));
                Check(d1 >= 0f && d1 <= 1f && dCalm >= 0f && dCalm <= 1f, "dust outside [0,1]");
                Check(Near(dCalm, c0, 1e-6), "dust changed with no storm");
                Check(d1 >= c0 - 1e-6, "a storm cleaned a mirror");
                if (t > 0) Check(Near(d1, Math.Min(1.0, c0 + perDay * (double)t / 60000.0), 1e-5), "dust != clamp(dust + perDay * days)");
                else Check(Near(d1, c0, 1e-6), "dust grew over no time");
                float f = RM_MirrorKernel.DustFactor(d0, loss);
                Check(f >= 0f && f <= 1f, "dust factor outside [0,1]");
                Check(Near(f, 1 - c0 * Math.Min(1, Math.Max(0, loss)), 1e-6), "dust factor != 1 - dust x maxLoss");
                Check(RM_MirrorKernel.DustFactor(0f, loss) == 1f, "a clean mirror lost light");
                Check(RM_MirrorKernel.DustFactor(1f, 0.6f) <= RM_MirrorKernel.DustFactor(0.5f, 0.6f), "more dust passed more light");

                float l = (float)(r.NextDouble() * 6), per = (float)(r.NextDouble() * 40), max = (float)(r.NextDouble() * 80), cap = (float)(r.NextDouble() * 6);
                float plain = (float)Math.Min(per, max);                       // what plain sun (exposure 1) gave
                float applied = r.Next(3) == 0 ? (float)(r.NextDouble() * 90) : plain;
                float ex = RM_MirrorKernel.ConcentrationExtraC(l, per, max, applied, cap);
                Check(ex >= 0f, "negative concentration heat");
                if (l <= 1f) Check(ex == 0f, "concentration heat from light at or below plain sun");
                Check(applied + ex <= Math.Max(max, applied) + 1e-3, "concentration pushed felt heat past the biome's cap");
                if (applied == plain && max > 0f && per > 0f)
                    Check(Near(applied + ex, Math.Max(applied, Math.Min(max, Math.Min(l, Math.Max(1f, cap)) * per)), 1e-3), "concentration total != min(cap light, light) x per-unit, capped");
                float ex2 = RM_MirrorKernel.ConcentrationExtraC(l + 0.5f, per, max, applied, cap);
                Check(ex2 >= ex - 1e-5f, "more light gave less concentration heat");
                Check(RM_MirrorKernel.ConcentrationExtraC(Math.Max(1f, cap) + 3f, per, max, applied, cap) == RM_MirrorKernel.ConcentrationExtraC(Math.Max(1f, cap) + 1f, per, max, applied, cap),
                    "light above the cap kept adding heat");

                int iv = r.Next(-10, 2000); float rate = (float)(r.NextDouble() * 12 - 1);
                float h = RM_MirrorKernel.RoomHeat(l, rate, iv);
                if (l <= 0f || rate <= 0f || iv <= 0) Check(h == 0f, "room heat with no light, rate or time");
                else Check(Near(h, l * rate * iv / 60.0, 1e-3 * Math.Max(1, h)), "room heat != light x rate x seconds");

                float pen = (float)(r.NextDouble() * 1.4 - 0.2);
                float dz = RM_MirrorKernel.DazzleFactor(l, pen);
                Check(dz >= 0f && dz <= 1f, "dazzle factor outside [0,1]");
                if (l < 0.5f) Check(dz == 1f, "dazzled below the 0.5 light threshold");
                else Check(Near(dz, Math.Max(0, 1 - Math.Min(1, Math.Max(0, pen)) * Math.Min(1.0, l)), 1e-6), "dazzle != 1 - penalty x min(1, light)");
                Check(RM_MirrorKernel.DazzleFactor(3f, pen) == RM_MirrorKernel.DazzleFactor(1f, pen), "dazzle kept growing past full light");

                float rg = (float)(r.NextDouble() * 50 - 5), day = (float)(r.NextDouble() * 1.6 - 0.3);
                float reach = RM_MirrorKernel.HeliographRange(rg, day);
                Check(reach >= 0f && reach <= Math.Max(0, rg) + 1e-5, "heliograph reach outside [0, range]");
                Check(RM_MirrorKernel.HeliographRange(rg, 0f) == 0f, "a heliograph reached anything with no daylight");
                Check(Near(RM_MirrorKernel.HeliographRange(rg, 1f), Math.Max(0, rg), 1e-6), "full daylight is not the full range");
            }
            return null;
        }

        // ═════════ the ancient field's solver (RM_MirrorFieldKernel) ═════════
        private static int Ham(int a, int b, int n, int d)
        {
            int[] x = new int[n], y = new int[n];
            for (int i = 0; i < n; i++) { x[i] = a % d; a /= d; y[i] = b % d; b /= d; }
            int h = 0; for (int i = 0; i < n; i++) if (x[i] != y[i]) h++;
            return h;
        }

        private static string FieldCase(int seed)
        {
            var r = new Random(seed);
            int n = r.Next(1, 8), d = r.Next(1, 5);
            long totalL = 1; for (int i = 0; i < n; i++) totalL *= d;
            int total = RM_MirrorFieldKernel.Configurations(n, d);
            if (totalL > RM_MirrorFieldKernel.MaxConfigurations) { Check(total == -1, "an oversized space was not refused"); FieldTooBig++; return null; }
            Check(total == totalL, $"configurations {total} != d^n {totalL}");
            double[] ps = { 0.0, 0.002, 0.05, 0.3, 0.9 };
            double p = ps[r.Next(ps.Length)];
            var truth = new bool[total]; var depth = new int[total];
            for (int c = 0; c < total; c++) { truth[c] = r.NextDouble() < p; depth[c] = r.Next(0, 6); }
            var start = new int[n]; for (int i = 0; i < n; i++) start[i] = r.Next(d);
            int startCode = 0, mul = 1; for (int i = 0; i < n; i++) { startCode += start[i] * mul; mul *= d; }
            Check(RM_MirrorFieldKernel.Encode(start, n, d) == startCode, "Encode is not base d, mirror 0 lowest");
            var back = new int[n]; RM_MirrorFieldKernel.Decode(startCode, n, d, back);
            for (int i = 0; i < n; i++) Check(back[i] == start[i], "Decode(Encode(x)) != x");
            int calls = 0;
            var rep = RM_MirrorFieldKernel.Solve(n, d, start, (int[] cfg, out int dep) =>
            {
                calls++;
                int code = 0, m2 = 1; for (int i = 0; i < n; i++) { code += cfg[i] * m2; m2 *= d; }
                dep = depth[code];
                return truth[code];
            });
            Check(calls == total, $"the solver evaluated {calls} of {total} configurations");
            int count = 0, best = -1, bestDist = -1;
            for (int c = 0; c < total; c++)
                if (truth[c]) { count++; int h = Ham(startCode, c, n, d); if (bestDist < 0 || h < bestDist) { bestDist = h; best = c; } }
            Check(rep.solutionCount == count && rep.solutions.Count == count, $"solutions {rep.solutionCount}, reference {count}");
            Check(rep.minReAims == bestDist, $"minReAims {rep.minReAims}, reference {bestDist}");
            Check(rep.startSolved == (count > 0 && truth[startCode]), "startSolved wrong");
            if (count > 0)
            {
                Check(Ham(startCode, rep.bestSolution, n, d) == bestDist && truth[rep.bestSolution], "bestSolution is not a nearest solution");
                Check(rep.bestDepth == depth[rep.bestSolution], "bestDepth is not the nearest solution's depth");
                FieldSolvable++;
            }
            int want = r.Next(0, 6), cap = r.Next(0, 6);
            string why;
            bool ok = RM_MirrorFieldKernel.Acceptable(rep, want, cap, out why);
            bool refOk = count > 0 && !truth[startCode] && bestDist >= want && rep.bestDepth <= cap;
            Check(ok == refOk, $"Acceptable {ok} ({why}), reference {refOk}");
            Check(ok == (why == null), "Acceptable's reason disagrees with its verdict");
            if (ok) FieldAccepted++;
            // PickStart: every chosen start is at least `want` from every solution; -1 only when no such start exists
            int ps0 = RM_MirrorFieldKernel.PickStart(rep, want, r.Next());
            bool anyFar = false, exhaustive = total <= 729;   // the reference below is O(total^2): keep it to the design's 6x3
            for (int c = 0; c < total && count > 0 && exhaustive; c++)
            {
                int md = int.MaxValue; for (int k = 0; k < total; k++) if (truth[k]) md = Math.Min(md, Ham(c, k, n, d));
                if (md >= Math.Max(1, want)) { anyFar = true; break; }
            }
            if (ps0 < 0) Check(!anyFar, "PickStart found nothing while a far enough start exists");
            else
            {
                Check(anyFar || !exhaustive, "PickStart returned a start although none is far enough");
                for (int k = 0; k < total; k++) if (truth[k]) Check(Ham(ps0, k, n, d) >= Math.Max(1, want), "PickStart's start is too near a solution");
                RM_MirrorFieldKernel.Rebase(rep, ps0);
                Check(rep.startCode == ps0 && !rep.startSolved && rep.minReAims >= Math.Max(1, want), "Rebase did not move the start");
            }
            // the hint walk: from any configuration, NextMove reaches a solution in exactly its distance, one mirror per step
            if (count > 0)
            {
                var cur = new int[n]; RM_MirrorFieldKernel.Decode(r.Next(total), n, d, cur);
                int code = RM_MirrorFieldKernel.Encode(cur, n, d), dist;
                RM_MirrorFieldKernel.Nearest(rep.solutions, code, n, d, out dist);
                int steps = 0;
                while (RM_MirrorFieldKernel.NextMove(rep.solutions, cur, n, d, out int mi, out int di))
                {
                    Check(mi >= 0 && mi < n && di >= 0 && di < d && cur[mi] != di, "a hint named a move that changes nothing");
                    int before; RM_MirrorFieldKernel.Nearest(rep.solutions, RM_MirrorFieldKernel.Encode(cur, n, d), n, d, out before);
                    cur[mi] = di; steps++;
                    int after; RM_MirrorFieldKernel.Nearest(rep.solutions, RM_MirrorFieldKernel.Encode(cur, n, d), n, d, out after);
                    Check(after == before - 1, "a hint did not bring the field one turn closer");
                    Check(steps <= n, "the hint walk did not end");
                }
                Check(steps == dist && truth[RM_MirrorFieldKernel.Encode(cur, n, d)], $"the hint walk took {steps} turns for a distance of {dist}");
                HintWalks++;
            }
            else Check(!RM_MirrorFieldKernel.NextMove(rep.solutions, start, n, d, out _, out _), "a hint with no solution");
            // escalating hint levels
            int mr = r.Next(-1, 6), done = r.Next(0, 20);
            int lv = RM_MirrorFieldKernel.HintLevel(done, mr), stepL = Math.Max(1, mr);
            Check(lv == (done >= 2 * stepL ? 2 : done >= stepL ? 1 : 0), "hint level is not 0 / 1 after minReAims / 2 after twice that");
            Check(RM_MirrorFieldKernel.HintLevel(done + 1, mr) >= lv, "hint level went down with more turns");
            Fields++;
            return null;
        }

        private struct Pt { public int x, z; }
        private struct Rec : IRM_LineVisitor
        {
            public List<Pt> cells;
            public int stopAt;
            public bool Blocked(int x, int z)
            {
                if (cells == null) cells = new List<Pt>();
                cells.Add(new Pt { x = x, z = z });
                return stopAt >= 0 && cells.Count - 1 == stopAt;
            }
        }

        private static double Dist(int x0, int z0, int x1, int z1, int x, int z)
        {
            double dx = x1 - x0, dz = z1 - z0, len2 = dx * dx + dz * dz;
            if (len2 == 0) return Math.Sqrt((double)(x - x0) * (x - x0) + (double)(z - z0) * (z - z0));
            double t = Math.Max(0, Math.Min(1, ((x - x0) * dx + (z - z0) * dz) / len2));
            double qx = x0 + t * dx, qz = z0 + t * dz;
            return Math.Sqrt((x - qx) * (x - qx) + (z - qz) * (z - qz));
        }

        // ═════════ worlds and the reference pass ═════════
        private sealed class Scenario
        {
            public World world;
            public RM_MirrorSpec[] specs;
            public bool anyEffect = true, sunUp = true;
            public RM_Vec sun;
            public float daylight;
            public int maxChain;
        }

        private static Scenario Gen(Random r, bool crowded)
        {
            int w = r.Next(8, 26), h = r.Next(8, 26);
            var sc = new Scenario { world = new World(w, h) };
            World wd = sc.world;
            double roofP = r.Next(3) == 0 ? 0.08 : r.Next(4) == 0 ? 0.4 : 0.0, wallP = r.NextDouble() * 0.12, doorP = r.NextDouble() * 0.05;
            double apP = r.Next(3) == 0 ? 0.06 : 0.0;
            for (int i = 0; i < w * h; i++)
            {
                wd.roof[i] = r.NextDouble() < roofP;
                double u = r.NextDouble();
                wd.wall[i] = u < wallP; wd.door[i] = !wd.wall[i] && u < wallP + doorP;
                if (r.NextDouble() < apP) { wd.aperture[i] = true; wd.wall[i] = false; wd.door[i] = false; }
            }
            int count = crowded ? r.Next(2, 9) : r.Next(0, 6);
            var list = new List<RM_MirrorSpec>();
            for (int tries = 0; tries < count * 6 && list.Count < count; tries++)
            {
                int size = r.Next(4) == 0 ? 2 : 1;
                int x = r.Next(0, w - size + 1), z = r.Next(0, h - size + 1);
                bool free = true;
                for (int dx = 0; dx < size && free; dx++) for (int dz = 0; dz < size; dz++) if (wd.owner[(z + dz) * w + x + dx] >= 0) free = false;
                if (!free) continue;
                int idx = list.Count;
                for (int dx = 0; dx < size; dx++) for (int dz = 0; dz < size; dz++)
                    {
                        int ci = (z + dz) * w + x + dx; wd.owner[ci] = idx; wd.wall[ci] = false; wd.door[ci] = false; wd.aperture[ci] = false;
                    }
                var m = new RM_MirrorSpec
                {
                    posX = x, posZ = z, minX = x, minZ = z, maxX = x + size - 1, maxZ = z + size - 1, footprintCells = size * size,
                    faceX = x + size / 2f, faceZ = z + size / 2f,
                    reflectivity = (float)(0.3 + r.NextDouble() * 0.7),
                    spotSize = r.Next(5) == 0 ? r.Next(1, 4) : size,
                    maxRange = (float)(3 + r.NextDouble() * 40),
                    spawned = r.Next(12) != 0,
                    holdsTarget = r.Next(3) != 0,
                    tracking = r.Next(2) == 0,
                    source = r.Next(8) == 0 ? (float)(r.NextDouble() * 0.03) : (float)r.NextDouble(),
                    savedNormal = r.Next(4) == 0 ? RM_Vec.Zero : Unit(r, true),
                };
                m.targetValid = r.Next(5) != 0;
                m.hasAim = m.targetValid && !m.savedNormal.IsZero;
                list.Add(m);
            }
            // targets: half of them on another mirror (relays), the rest anywhere on the map
            for (int k = 0; k < list.Count; k++)
            {
                var m = list[k];
                if (list.Count > 1 && r.Next(2) == 0)
                {
                    int o = r.Next(list.Count);
                    if (o == k) o = (o + 1) % list.Count;
                    m.targetX = list[o].minX + r.Next(list[o].maxX - list[o].minX + 1);
                    m.targetZ = list[o].minZ + r.Next(list[o].maxZ - list[o].minZ + 1);
                }
                else if (r.Next(25) == 0) { m.targetX = -1 - r.Next(3); m.targetZ = r.Next(h); }
                else { m.targetX = r.Next(w); m.targetZ = r.Next(h); }
                list[k] = m;
            }
            sc.specs = list.ToArray();
            sc.sun = Unit(r, true); if (sc.sun.Y < 0.1f) sc.sun.Y = 0.5f; sc.sun = sc.sun.Normalized;
            sc.daylight = r.Next(6) == 0 ? (float)(r.NextDouble() * 0.05) : (float)(0.2 + r.NextDouble() * 0.8);
            sc.maxChain = r.Next(-1, 9);
            sc.anyEffect = r.Next(15) != 0;
            sc.sunUp = r.Next(12) != 0;
            return sc;
        }

        private static List<Pt> PathCells(IRM_BeamWorld w, RM_MirrorSpec m, int x, int z)
        {
            var rec = new Rec { stopAt = -1 };
            RM_MirrorKernel.LineClear(m.posX, m.posZ, x, z, ref rec);
            return rec.cells ?? new List<Pt>();
        }

        private static bool InOwn(RM_MirrorSpec m, int x, int z) { return x >= m.minX && x <= m.maxX && z >= m.minZ && z <= m.maxZ; }

        // First blocker on the way to / at the cell, from the visited cells (independent of the kernel's visitor plumbing).
        // Design §2.2 + §5 E2: an aperture never blocks and, once passed, roofs stop blocking (the beam is inside).
        private static string RefBlocker(World w, RM_MirrorSpec m, int idx, int x, int z)
        {
            if (x < 0 || z < 0 || x >= w.W || z >= w.H) return w.BlockerEdge;
            var cells = PathCells(w, m, x, z);
            cells.Add(new Pt { x = x, z = z });
            bool passedGlass = false;
            foreach (var c in cells)
            {
                if (InOwn(m, c.x, c.z)) continue;
                int i = c.z * w.W + c.x;
                if (w.aperture[i]) { passedGlass = true; continue; }
                if (w.roof[i] && !passedGlass) return "roof";
                if (w.owner[i] >= 0) continue;
                if (w.door[i]) return "door";
                if (w.wall[i]) return "wall";
            }
            return null;
        }

        // Did some firing mirror's beam pass glass on its way to (x,z)? (light under a roof is legal only then)
        private static bool ReachedThroughGlass(Scenario sc, RM_MirrorResult[] got, int x, int z)
        {
            World w = sc.world;
            if (w.aperture[z * w.W + x]) return true;
            for (int k = 0; k < sc.specs.Length; k++)
            {
                if (!got[k].fired) continue;
                foreach (var c in PathCells(w, sc.specs[k], x, z)) if (!InOwn(sc.specs[k], c.x, c.z) && w.aperture[c.z * w.W + c.x]) return true;
            }
            return false;
        }

        private sealed class RefShot { public int m; public RM_Vec dir; public float input; public bool relayed; public int depth; }

        // An independent reference of the whole pass: per-depth maps, written for clarity, not speed.
        private static float[] RefPass(Scenario sc, RM_MirrorResult[] exp)
        {
            World w = sc.world; var specs = sc.specs; int n = specs.Length;
            var light = new float[w.W * w.H];
            for (int k = 0; k < n; k++) exp[k] = default(RM_MirrorResult);
            var fired = new HashSet<int>();
            var shots = new List<RefShot>();
            for (int k = 0; k < n; k++)
            {
                var m = specs[k];
                if (!sc.anyEffect || !sc.sunUp || !m.spawned || !(m.hasAim || (m.holdsTarget && m.targetValid))) continue;
                float src = m.source * sc.daylight;
                exp[k].source = src;
                if (src > 0.02f) shots.Add(new RefShot { m = k, dir = sc.sun, input = src });
            }
            int cap = Math.Max(1, Math.Min(6, sc.maxChain));
            for (int depth = 0; depth < cap && shots.Count > 0; depth++)
            {
                var feed = new Dictionary<int, float>(); var feedDir = new Dictionary<int, RM_Vec>(); var order = new List<int>();
                var firedNow = new List<int>();
                foreach (var sh in shots)
                {
                    int k = sh.m;
                    if (fired.Contains(k)) continue;
                    fired.Add(k); firedNow.Add(k);
                    var m = specs[k];
                    exp[k].ranFire = true; exp[k].inDir = sh.dir; exp[k].depth = depth; exp[k].input = sh.input;
                    bool commit;
                    RM_Vec nrm = RM_MirrorKernel.NormalFor(m, sh.dir, out commit);
                    exp[k].commitNormal = commit; exp[k].normal = nrm;
                    if (nrm.IsZero) continue;
                    float cos = RM_MirrorKernel.Cosine(nrm, sh.dir);
                    exp[k].efficiency = cos;
                    float output = sh.input * m.reflectivity * cos;
                    if (output <= 0.02f) continue;
                    int cx, cz;
                    if (m.holdsTarget && m.targetValid) { cx = m.targetX; cz = m.targetZ; }
                    else
                    {
                        float hx, hz;
                        RM_Vec outDir = RM_MirrorKernel.Reflect(sh.dir, nrm);
                        if (!RM_MirrorKernel.GroundHit(m.faceX, 1.5f, m.faceZ, outDir, m.maxRange, out hx, out hz)) { exp[k].blocker = "sky"; continue; }
                        cx = (int)Math.Floor(hx); cz = (int)Math.Floor(hz);
                    }
                    if (cx < 0 || cz < 0 || cx >= w.W || cz >= w.H) { exp[k].blocker = "edge"; continue; }
                    int size = Math.Max(1, m.spotSize), lo = -(size - 1) / 2, lit = 0;
                    for (int dx = 0; dx < size; dx++)
                        for (int dz = 0; dz < size; dz++)
                        {
                            int x = cx + lo + dx, z = cz + lo + dz;
                            if (x < 0 || z < 0 || x >= w.W || z >= w.H) continue;
                            string why = RefBlocker(w, m, k, x, z);
                            if (why != null) { if (exp[k].blocker == null) exp[k].blocker = why; continue; }
                            light[z * w.W + x] += output; lit++;
                            int o = w.owner[z * w.W + x];
                            if (o >= 0 && o != k)
                            {
                                float share = output / Math.Max(1, specs[o].footprintCells);
                                feed[o] = (feed.ContainsKey(o) ? feed[o] : 0f) + share;
                                if (!order.Contains(o)) order.Add(o);
                                feedDir[o] = (new RM_Vec(m.faceX, 1.5f, m.faceZ) - new RM_Vec(specs[o].faceX, 1.5f, specs[o].faceZ)).Normalized;
                            }
                        }
                    if (lit == 0) continue;
                    exp[k].fired = true; exp[k].relayed = sh.relayed; exp[k].delivered = output; exp[k].hasSpot = true; exp[k].spotX = cx; exp[k].spotZ = cz; exp[k].litCount = lit;
                }
                shots = new List<RefShot>();
                foreach (int o in order)
                    if (!fired.Contains(o) && feed[o] > 0.02f) shots.Add(new RefShot { m = o, dir = feedDir[o], input = feed[o], relayed = true, depth = depth + 1 });
            }
            return light;
        }

        private static string Compare(Scenario sc, RM_MirrorKernel.Pass pass, RM_MirrorResult[] got, RM_MirrorResult[] exp, float[] expLight)
        {
            int n = sc.specs.Length;
            for (int k = 0; k < n; k++)
            {
                RM_MirrorResult g = got[k], e = exp[k];
                string at = $"mirror {k}: ";
                if (g.ranFire != e.ranFire) return at + $"ranFire {g.ranFire}, reference {e.ranFire}";
                if (g.fired != e.fired) return at + $"fired {g.fired}, reference {e.fired} (blocker {g.blocker}/{e.blocker})";
                if (g.relayed != e.relayed) return at + $"relayed {g.relayed}, reference {e.relayed}";
                if (g.depth != e.depth) return at + $"depth {g.depth}, reference {e.depth}";
                if (g.blocker != e.blocker) return at + $"blocker {g.blocker ?? "null"}, reference {e.blocker ?? "null"}";
                if (g.hasSpot != e.hasSpot || g.spotX != e.spotX || g.spotZ != e.spotZ) return at + $"spot ({g.spotX},{g.spotZ}) {g.hasSpot}, reference ({e.spotX},{e.spotZ}) {e.hasSpot}";
                if (g.litCount != e.litCount) return at + $"litCount {g.litCount}, reference {e.litCount}";
                if (g.commitNormal != e.commitNormal) return at + $"commitNormal {g.commitNormal}, reference {e.commitNormal}";
                if (!Near(g.delivered, e.delivered, 1e-5) || !Near(g.efficiency, e.efficiency, 1e-5) || !Near(g.source, e.source, 1e-5) || !Near(g.input, e.input, 1e-5))
                    return at + $"delivered/eff/source/input {g.delivered}/{g.efficiency}/{g.source}/{g.input}, reference {e.delivered}/{e.efficiency}/{e.source}/{e.input}";
                if (!Near(g.inDir.X, e.inDir.X, 1e-5) || !Near(g.inDir.Y, e.inDir.Y, 1e-5) || !Near(g.inDir.Z, e.inDir.Z, 1e-5)) return at + "inDir differs from the reference";
            }
            int lit = 0;
            for (int i = 0; i < expLight.Length; i++)
            {
                if (!Near(pass.Light[i], expLight[i], 1e-4)) return $"light at cell {i % sc.world.W},{i / sc.world.W} is {pass.Light[i]}, reference {expLight[i]}";
                if (expLight[i] > 0f) lit++;
            }
            if (pass.LitCells.Count != lit) return $"{pass.LitCells.Count} lit cells, reference {lit}";
            return null;
        }

        // A mirror's own footprint is never a blocker for its own spot (a mirror aimed at its own cell lights it, roof or not).
        private static bool OwnFootprintOfFirer(Scenario sc, RM_MirrorResult[] got, int x, int z)
        {
            for (int k = 0; k < sc.specs.Length; k++) if (got[k].fired && InOwn(sc.specs[k], x, z)) return true;
            return false;
        }

        private static string Invariants(Scenario sc, RM_MirrorKernel.Pass pass, RM_MirrorResult[] got)
        {
            World w = sc.world; int n = sc.specs.Length;
            var seen = new HashSet<int>();
            foreach (int i in pass.LitCells)
            {
                if (i < 0 || i >= pass.Light.Length) return "a lit cell index is off the grid";
                if (!seen.Add(i)) return "a cell is listed lit twice";
                if (!(pass.Light[i] > 0f)) return "a listed lit cell has no light";
                if (w.roof[i] && !OwnFootprintOfFirer(sc, got, i % w.W, i / w.W) && !ReachedThroughGlass(sc, got, i % w.W, i / w.W)) return $"light under a roof at {i % w.W},{i / w.W} with no glass on any beam's way";
                if (w.wall[i] && w.owner[i] < 0) return $"light inside a wall at {i % w.W},{i / w.W}";
                if (w.door[i] && w.owner[i] < 0) return $"light on a closed door at {i % w.W},{i / w.W}";
            }
            for (int i = 0; i < pass.Light.Length; i++)
            {
                if (pass.Light[i] < 0f || float.IsNaN(pass.Light[i])) return "negative or NaN light";
                if (pass.Light[i] > 0f && !seen.Contains(i)) return "light on a cell missing from the lit list";
            }
            double total = 0, delivered = 0;
            for (int i = 0; i < pass.Light.Length; i++) total += pass.Light[i];
            int beams = 0, maxDepth = 0;
            bool any = false;
            for (int k = 0; k < n; k++)
            {
                var r = got[k];
                if (r.fired)
                {
                    delivered += (double)r.delivered * r.litCount; beams++;
                    if (!(r.delivered > 0.02f)) return "a mirror fired below the useful floor";
                    if (r.delivered > r.input * 1.00001f) return "a mirror delivered more light than arrived (reflectivity <= 1, cos <= 1)";
                    if (r.litCount < 1 || r.litCount > sc.specs[k].spotSize * sc.specs[k].spotSize && r.litCount > 1) return "lit cell count outside the spot";
                    if (r.efficiency < 0f || r.efficiency > 1.00001f) return "cosine efficiency outside [0,1]";
                }
                if (!r.ranFire && (r.fired || r.relayed)) return "a mirror that never took its shot reports firing";
                if (r.ranFire) { any = true; if (r.depth > maxDepth) maxDepth = r.depth; }
                if (r.relayed && r.depth < 1) return "a relayed shot at depth 0";
                if (r.ranFire && r.depth >= 1 && Math.Abs(r.inDir.Y) > 1e-4f) return "a relay arrived with a vertical component (faces are all at one height)";
                if (r.ranFire && r.depth == 0 && !(r.input == r.source)) return "a sun-fed mirror's input != its source";
                if (r.ranFire && r.depth == 0 && !(r.source > 0.02f)) return "a mirror took a sun shot below the useful floor";
            }
            if (Math.Abs(total - delivered) > 1e-3 * Math.Max(1, delivered)) return $"light is not conserved: grid {total}, mirrors delivered {delivered}";
            if (pass.Beams.Count != beams) return $"{pass.Beams.Count} beams for {beams} firing mirrors";
            int cap = Math.Max(1, Math.Min(6, sc.maxChain));
            if (maxDepth >= cap) return $"a shot at depth {maxDepth} with a cap of {cap}";
            if ((!sc.sunUp || !sc.anyEffect) && (any || pass.LitCells.Count > 0)) return "light or shots while the sun is down / all effects are off";
            // relay bound: relay input never exceeds what the shallower mirrors delivered in total
            for (int k = 0; k < n; k++)
                if (got[k].ranFire && got[k].depth >= 1)
                {
                    double up = 0; for (int j = 0; j < n; j++) if (got[j].fired && got[j].depth < got[k].depth) up += got[j].delivered;
                    if (got[k].input > up * 1.0001 + 1e-6) return "a relay was fed more light than the mirrors upstream delivered";
                    if (got[k].depth > 0 && sc.specs[k].source * sc.daylight > 0.02f && sc.anyEffect && sc.sunUp && sc.specs[k].spawned && (sc.specs[k].hasAim || (sc.specs[k].holdsTarget && sc.specs[k].targetValid)))
                        return "a mirror with its own sun fed at depth > 0 (it should have fired at depth 0)";
                }
            return null;
        }

        private static void Tally(Scenario sc, RM_MirrorResult[] got)
        {
            for (int k = 0; k < sc.specs.Length; k++)
            {
                var r = got[k];
                if (r.fired && r.relayed) Relays++;
                if (r.ranFire && r.depth >= 2) DeepChains++;
                if (r.blocker != null && r.blocker != "sky" && r.blocker != "edge") Blocked++;
                if (r.blocker == "sky") SkyMisses++;
                if (r.blocker == "edge") EdgeMisses++;
                if (r.commitNormal) Commits++;
                if (r.fired && sc.specs[k].spotSize >= 2) BigSpots++;
                if (r.fired && sc.specs[k].holdsTarget && sc.specs[k].targetValid) Targeted++;
                if (r.fired && !(sc.specs[k].holdsTarget && sc.specs[k].targetValid)) Untargeted++;
            }
            // a cycle: two mirrors aimed at each other that were both fed by sun
            for (int a = 0; a < sc.specs.Length; a++)
                for (int b = a + 1; b < sc.specs.Length; b++)
                {
                    var A = sc.specs[a]; var B = sc.specs[b];
                    if (A.holdsTarget && A.targetValid && B.holdsTarget && B.targetValid && InOwn(B, A.targetX, A.targetZ) && InOwn(A, B.targetX, B.targetZ) && got[a].ranFire && got[b].ranFire) Cycles++;
                }
            if (!sc.sunUp) NightPasses++;
            for (int k = 0; k < sc.specs.Length; k++)
                if (got[k].fired && got[k].hasSpot)
                {
                    int x = got[k].spotX, z = got[k].spotZ, W = sc.world.W;
                    if (x >= 0 && z >= 0 && x < W && z < sc.world.H && sc.world.roof[z * W + x] && !InOwn(sc.specs[k], x, z)) Glazed++;
                }
        }

        private static string PassCase(int seed)
        {
            var r = new Random(seed);
            var sc = Gen(r, seed % 2 == 0);
            var pass = new RM_MirrorKernel.Pass();
            var got = new RM_MirrorResult[sc.specs.Length];
            var exp = new RM_MirrorResult[sc.specs.Length];
            pass.Run(sc.world, sc.specs, sc.specs.Length, got, sc.anyEffect, sc.sunUp, sc.sun, sc.daylight, sc.maxChain);
            Steps++;
            float[] expLight = RefPass(sc, exp);
            string err = Compare(sc, pass, got, exp, expLight) ?? Invariants(sc, pass, got);
            if (err != null) return err;
            Tally(sc, got);
            // a second run on the same pass object is idempotent
            int h1 = pass.ChangeHash();
            var copy = (float[])pass.Light.Clone();
            var got2 = new RM_MirrorResult[sc.specs.Length];
            pass.Run(sc.world, sc.specs, sc.specs.Length, got2, sc.anyEffect, sc.sunUp, sc.sun, sc.daylight, sc.maxChain);
            Steps++;
            for (int i = 0; i < copy.Length; i++) if (copy[i] != pass.Light[i]) return "a second identical pass changed the light";
            if (pass.ChangeHash() != h1) return "a second identical pass changed the change hash";
            if (pass.PrevLitCells.Count != pass.LitCells.Count) return "PrevLitCells is not the previous pass's lit set";
            Idempotent++;
            // change hash reacts to a quantised change and ignores a sub-step jitter inside one quantum
            if (pass.LitCells.Count > 0)
            {
                int i0 = pass.LitCells[0];
                float v = pass.Light[i0];
                int q = RM_MirrorKernel.Quantise(v);
                float bumped = (q + 2) * 0.05f;
                pass.Light[i0] = bumped;
                int h2 = pass.ChangeHash();
                pass.Light[i0] = v;
                if (h2 == h1) return "the change hash ignored a light change of two quanta";
                float same = q * 0.05f + 0.01f;
                if (RM_MirrorKernel.Quantise(same) == q)
                {
                    pass.Light[i0] = same; int h3 = pass.ChangeHash(); pass.Light[i0] = v;
                    if (h3 != h1) return "the change hash reacted to jitter inside one quantum";
                }
            }
            return null;
        }

        // ═════════ sequences on one persistent pass ═════════
        private static readonly string[] SqNames = { "add", "remove", "aim", "build", "sun", "run", "chain", "night" };

        private static string RunSeq(int seed, List<Act> acts)
        {
            var r = new Random(seed * 7 + 1);
            var sc = Gen(new Random(seed), true);
            var keep = new List<RM_MirrorSpec>(sc.specs);
            World wd = sc.world;
            var pass = new RM_MirrorKernel.Pass();
            var prevLit = new HashSet<int>();
            bool first = true;
            foreach (var a in acts)
            {
                Steps++;
                switch (a.kind)
                {
                    case 0: // add a mirror where free
                        {
                            int x = a.a % wd.W, z = a.b % wd.H;
                            if (wd.owner[z * wd.W + x] >= 0) break;
                            int idx = keep.Count;
                            wd.owner[z * wd.W + x] = idx; wd.wall[z * wd.W + x] = false; wd.door[z * wd.W + x] = false; wd.aperture[z * wd.W + x] = false;
                            keep.Add(new RM_MirrorSpec { posX = x, posZ = z, minX = x, minZ = z, maxX = x, maxZ = z, footprintCells = 1, faceX = x + 0.5f, faceZ = z + 0.5f, reflectivity = 0.8f, spotSize = 1, maxRange = 30f, spawned = true, holdsTarget = true, targetValid = true, targetX = (a.a * 7) % wd.W, targetZ = (a.b * 3) % wd.H, tracking = a.a % 2 == 0, source = 0.9f, savedNormal = Unit(r, true), hasAim = true });
                            break;
                        }
                    case 1: // remove: despawn (it stays in the array but is not spawned, and frees its cell)
                        if (keep.Count > 0)
                        {
                            int k = a.a % keep.Count; var m = keep[k]; m.spawned = false;
                            for (int x = m.minX; x <= m.maxX; x++) for (int z = m.minZ; z <= m.maxZ; z++) if (wd.owner[z * wd.W + x] == k) wd.owner[z * wd.W + x] = -1;
                            keep[k] = m;
                        }
                        break;
                    case 2: // re-aim
                        if (keep.Count > 0)
                        {
                            int k = a.a % keep.Count; var m = keep[k];
                            m.targetX = a.b % wd.W; m.targetZ = (a.a / 3) % wd.H; m.targetValid = true; m.hasAim = !m.savedNormal.IsZero;
                            keep[k] = m;
                        }
                        break;
                    case 3: // build or remove a wall / roof / door
                        {
                            int x = a.a % wd.W, z = a.b % wd.H, i = z * wd.W + x;
                            if (wd.owner[i] >= 0) break;
                            switch ((a.a + a.b) % 5) { case 0: wd.wall[i] = !wd.wall[i]; wd.aperture[i] = false; break; case 1: wd.roof[i] = !wd.roof[i]; break; case 2: wd.door[i] = !wd.door[i]; wd.aperture[i] = false; break; case 3: wd.aperture[i] = !wd.aperture[i]; if (wd.aperture[i]) { wd.wall[i] = wd.door[i] = false; } break; default: wd.wall[i] = wd.door[i] = wd.roof[i] = wd.aperture[i] = false; break; }
                            break;
                        }
                    case 4: sc.sun = Unit(new Random(a.a * 31 + a.b), true); if (sc.sun.Y < 0.1f) sc.sun.Y = 0.6f; sc.sun = sc.sun.Normalized; sc.daylight = 0.2f + (a.b % 80) / 100f; break;
                    case 6: sc.maxChain = (a.a % 8) - 1; break;
                    case 7: sc.sunUp = a.a % 3 != 0; sc.anyEffect = a.b % 9 != 0; break;
                    default: break;
                }
                if (a.kind != 5 && a.a % 3 != 0) continue;        // run on every "run" and on a third of the other steps
                sc.specs = keep.ToArray();
                var got = new RM_MirrorResult[sc.specs.Length];
                pass.Run(sc.world, sc.specs, sc.specs.Length, got, sc.anyEffect, sc.sunUp, sc.sun, sc.daylight, sc.maxChain);
                var exp = new RM_MirrorResult[sc.specs.Length];
                float[] expLight = RefPass(sc, exp);
                string err = Compare(sc, pass, got, exp, expLight) ?? Invariants(sc, pass, got);
                if (err != null) return err;
                // the persistent pass equals a fresh one (nothing stale survives), and PrevLitCells is last pass's lit set
                var fresh = new RM_MirrorKernel.Pass();
                fresh.Run(sc.world, sc.specs, sc.specs.Length, new RM_MirrorResult[sc.specs.Length], sc.anyEffect, sc.sunUp, sc.sun, sc.daylight, sc.maxChain);
                for (int i = 0; i < pass.Light.Length; i++) if (pass.Light[i] != fresh.Light[i]) return $"stale light: persistent pass differs from a fresh pass at cell {i % wd.W},{i / wd.W} ({pass.Light[i]} vs {fresh.Light[i]})";
                if (pass.ChangeHash() != fresh.ChangeHash() && pass.LitCells.SequenceEqual(fresh.LitCells)) return "equal lit sets, different change hashes";
                if (!first && !prevLit.SetEquals(pass.PrevLitCells)) return "PrevLitCells is not the previous pass's lit set";
                prevLit = new HashSet<int>(pass.LitCells); first = false;
                Tally(sc, got);
            }
            return null;
        }

        // ═════════ runner ═════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("math", () => Family("math", N(4000), S(1), MathCase)),
                ("pass", () => Family("pass", N(4000), S(1), PassCase)),
                ("sequence", () => Family("sequence", N(1500), S(1), s => Drive(s, rr => GenActs(rr, 8, 60, new[] { 8, 5, 12, 14, 8, 30, 4, 3 }, SqNames), RunSeq))),
                ("field", () => Family("field", N(1200), S(1), FieldCase)),
                ("generate", () => Family("generate", N(600), S(1), GenerateCase)),
                ("chain", () => Family("chain", N(3000), S(1), ChainCase)),
            };
            return Finish("solarmirrors", sw, scale, oneSeed, only, fam,
                () => $"relays {Relays}, deep chains {DeepChains}, blocked {Blocked}, sky misses {SkyMisses}, edge misses {EdgeMisses}, commits {Commits}, big spots {BigSpots}, cycles {Cycles}, targeted {Targeted}, untargeted {Untargeted}, night {NightPasses}, idempotent {Idempotent}, glazed {Glazed}, fields {Fields} (solvable {FieldSolvable}, accepted {FieldAccepted}, too big {FieldTooBig}, hint walks {HintWalks}), generate {GenCases} (accepted {GenAccepted}, refused {GenRefused}, held-only configurations {GenHeldOnly}, cap<0 accepted {GenLowCap}, out-of-range settings {GenOutOfRange}, too big {GenTooBig}, early-latch walks {GenWalks}, budget stops {GenBudgetStops}, deterministic {GenDeterministic}), chain depth>=2 shots {ChainDeep}",
                () => Relays > 0 && DeepChains > 0 && Blocked > 0 && SkyMisses > 0 && EdgeMisses > 0 && Commits > 0 && BigSpots > 0 && Cycles > 0 && Targeted > 0 && Untargeted > 0 && NightPasses > 0 && Idempotent > 0
                      && (only != null || Glazed > 0 && FieldSolvable > 0 && FieldAccepted > 0 && FieldTooBig > 0 && HintWalks > 0
                          && GenAccepted > 0 && GenRefused > 0 && GenHeldOnly > 0 && GenLowCap > 0 && GenOutOfRange > 0 && GenTooBig > 0
                          && GenWalks > 0 && GenDeterministic > 0 && ChainDeep > 0 && GenBudgetStops > 0));
        }
    }
}
