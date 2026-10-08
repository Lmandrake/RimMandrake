// SOLAR_MIRRORS_BUILD_1 offline validation (Transient/solarmirrors_validation_20261008.md), two families added to the fuzz:
//   generate  the WHOLE ancient-field layout search mapgen runs (RM_MirrorFieldKernel.Generate) on random sites, with the real
//             light pass as its evaluator and these independent oracles: every configuration re-lit by the reference pass
//             (RefPass, not the kernel) and classified by hand; >= 1 strict solution; the start is not held lit; every held
//             configuration is >= want jobs from the start; an exhaustive walk of every job order shorter than `want`, with the
//             stones' hysteresis played out, never latches the vault; same seed -> same layout; bounded attempts/evaluations
//             for every setting, in range or not (the mapgen clamps are swept too).
//   chain     explicit relay chains (mirror k aimed at mirror k+1's footprint), the transition the random worlds almost never
//             reached ("deep chains 3" before this family), checked against the reference pass and the invariants.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.SolarMirrors.SelfTest
{
    internal static partial class SolarMirrorsFuzz
    {
        public static long GenCases, GenAccepted, GenRefused, GenHeldOnly, GenLowCap, GenOutOfRange, GenTooBig, GenWalks, GenDeterministic, ChainDeep;

        private const float StoneLitAt = 0.5f, StoneUnlitBelow = 0.35f;

        private sealed class FieldSite
        {
            public Scenario sc;
            public int[] stoneCell;          // cell index of stone k
            public int stones;
            public List<Pt> targets = new List<Pt>();
            public Dictionary<int, int> ids = new Dictionary<int, int>();
            public List<List<int>> det;
            public int Id(int x, int z)
            {
                int key = z * sc.world.W + x;
                if (!ids.TryGetValue(key, out int id)) { id = targets.Count; targets.Add(new Pt { x = x, z = z }); ids[key] = id; }
                return id;
            }
        }

        // A field site: stones in a row, ancient-style 3x3 mirrors (Position = centre, spot 3, holds its target) around them.
        private static FieldSite GenSite(Random r, int n, int stones, int maxChainSetting)
        {
            int w = r.Next(26, 40), h = r.Next(26, 40);
            var sc = new Scenario { world = new World(w, h) };
            World wd = sc.world;
            double wallP = r.Next(3) == 0 ? 0.04 : 0.0, roofP = r.Next(6) == 0 ? 0.05 : 0.0;
            for (int i = 0; i < w * h; i++) { wd.wall[i] = r.NextDouble() < wallP; wd.roof[i] = r.NextDouble() < roofP; }
            var site = new FieldSite { sc = sc, stones = stones, stoneCell = new int[stones] };
            int sz0 = h / 2, sx0 = w / 2 - stones;
            for (int k = 0; k < stones; k++)
            {
                int x = Math.Max(0, Math.Min(w - 1, sx0 + 2 * k + r.Next(0, 2))), z = Math.Max(0, Math.Min(h - 1, sz0 + r.Next(-1, 2)));
                int ci = z * w + x;
                if (Array.IndexOf(site.stoneCell, ci, 0, k) >= 0) { x = Math.Min(w - 1, x + 1); ci = z * w + x; }
                site.stoneCell[k] = ci; wd.wall[ci] = false; wd.roof[ci] = false;
                site.Id(x, z);                                   // stone k is target id k
            }
            var list = new List<RM_MirrorSpec>();
            sc.sun = Unit(r, true); if (sc.sun.Y < 0.15f) sc.sun.Y = 0.4f; sc.sun = sc.sun.Normalized;
            // as mapgen lays them (most sites): on the far side of the stones from the sun, so they throw back toward it
            double hx = -sc.sun.X, hz = -sc.sun.Z, hl = Math.Sqrt(hx * hx + hz * hz);
            if (hl < 1e-3) { hx = 0; hz = -1; hl = 1; }
            hx /= hl; hz /= hl;
            bool downsun = r.Next(4) != 0;
            for (int tries = 0; tries < 400 && list.Count < n; tries++)
            {
                int cx = r.Next(1, w - 1), cz = r.Next(1, h - 1);
                if (downsun)
                {
                    double rad = 6 + r.NextDouble() * 8, ang = (r.NextDouble() - 0.5) * 1.9;
                    double dx0 = hx * Math.Cos(ang) - hz * Math.Sin(ang), dz0 = hx * Math.Sin(ang) + hz * Math.Cos(ang);
                    cx = Math.Max(1, Math.Min(w - 2, (int)Math.Round(w / 2 + dx0 * rad)));
                    cz = Math.Max(1, Math.Min(h - 2, (int)Math.Round(h / 2 + dz0 * rad)));
                }
                bool free = true;
                for (int dx = -1; dx <= 1 && free; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        int ci = (cz + dz) * w + cx + dx;
                        if (wd.owner[ci] >= 0 || site.stoneCell.Contains(ci)) { free = false; break; }
                    }
                foreach (var o in list) if (Math.Abs(o.posX - cx) < 4 && Math.Abs(o.posZ - cz) < 4) free = false;
                if (!free) continue;
                int idx = list.Count;
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        int ci = (cz + dz) * w + cx + dx; wd.owner[ci] = idx; wd.wall[ci] = false;
                    }
                list.Add(new RM_MirrorSpec
                {
                    posX = cx, posZ = cz, minX = cx - 1, minZ = cz - 1, maxX = cx + 1, maxZ = cz + 1, footprintCells = 9,
                    faceX = cx + 0.5f, faceZ = cz + 0.5f, reflectivity = (float)(0.55 + r.NextDouble() * 0.45), spotSize = 3, maxRange = 60f,
                    spawned = true, holdsTarget = true, targetValid = true, tracking = false, hasAim = true, savedNormal = Unit(r, true),
                    source = r.Next(6) == 0 ? 0f : (float)(0.6 + r.NextDouble() * 0.4), targetX = cx, targetZ = cz,
                });
            }
            sc.specs = list.ToArray();
            sc.daylight = 1f; sc.anyEffect = true; sc.sunUp = true; sc.maxChain = maxChainSetting;
            return site;
        }

        // Mirror i's detent candidates: every stone, every other mirror, decoys >= 3 cells from any stone (a 3x3 spot cannot spill).
        private static List<int> SiteCandidates(FieldSite site, int self, Random r)
        {
            var sc = site.sc; int w = sc.world.W, h = sc.world.H;
            var l = new List<int>();
            for (int k = 0; k < site.stones; k++) l.Add(k);
            for (int m = 0; m < sc.specs.Length; m++) if (m != self) l.Add(site.Id(sc.specs[m].posX, sc.specs[m].posZ));
            for (int k = 0; k < 6; k++)
            {
                int x = r.Next(w), z = r.Next(h), ci = z * w + x;
                if (sc.world.wall[ci] || sc.world.owner[ci] >= 0) continue;
                bool near = false;
                foreach (int s in site.stoneCell) if (Math.Abs(s % w - x) <= 2 && Math.Abs(s / w - z) <= 2) near = true;
                if (!near) l.Add(site.Id(x, z));
            }
            return l;
        }

        private static void Aim(FieldSite site, int[] cfg)
        {
            for (int i = 0; i < site.sc.specs.Length; i++)
            {
                Pt t = site.targets[site.det[i][cfg[i]]];
                site.sc.specs[i].targetX = t.x; site.sc.specs[i].targetZ = t.z;
            }
        }

        // The reference level of one configuration: the reference pass, then a hand classification (not RM_MirrorFieldKernel.LevelOf).
        // ambiguous = some stone within 1e-3 of a threshold (float order differences between the two passes may tip it).
        private static int RefLevel(FieldSite site, int[] cfg, out bool ambiguous, out float[] stoneLight, out int depth)
        {
            Aim(site, cfg);
            var exp = new RM_MirrorResult[site.sc.specs.Length];
            float[] light = RefPass(site.sc, exp);
            depth = 0; for (int k = 0; k < exp.Length; k++) if (exp[k].fired && exp[k].depth > depth) depth = exp[k].depth;
            stoneLight = new float[site.stones];
            ambiguous = false;
            bool allLit = true, allHeld = true;
            for (int k = 0; k < site.stones; k++)
            {
                float l = light[site.stoneCell[k]];
                stoneLight[k] = l;
                if (Math.Abs(l - StoneLitAt) < 1e-3 || Math.Abs(l - StoneUnlitBelow) < 1e-3) ambiguous = true;
                if (l < StoneLitAt) allLit = false;
                if (l < StoneUnlitBelow) allHeld = false;
            }
            return allLit ? 2 : allHeld ? 1 : 0;
        }

        private sealed class GenRun { public RM_FieldLayout layout; public FieldSite site; public int setN, setWant, setDet, setChain, attempts, n, d, want, budget; }
        public static long GenBudgetStops;

        private static GenRun RunGenerate(int seed)
        {
            var r = new Random(seed);
            // settings, in range or not: the mapgen clamps decide what the generator sees
            int setN = r.Next(5) == 0 ? r.Next(-3, 13) : r.Next(4, 7);
            int setWant = r.Next(5) == 0 ? r.Next(-3, 10) : r.Next(2, 5);
            int setDet = r.Next(6) == 0 ? (r.Next(2) == 0 ? r.Next(-2, 2) : r.Next(4, 13)) : 3;
            int setChain = r.Next(5) == 0 ? r.Next(-2, 1) : r.Next(1, 7);
            int n = RM_MirrorFieldKernel.FieldMirrors(setN), d = RM_MirrorFieldKernel.FieldDetents(setDet), want = RM_MirrorFieldKernel.FieldMinReAims(setWant);
            int stones = r.Next(8) == 0 ? r.Next(0, 7) : r.Next(2, 5);
            var site = GenSite(r, n, stones, setChain);
            int attempts = r.Next(1, 9);
            int budget = r.Next(4) == 0 ? r.Next(0, 3000) : int.MaxValue;
            var rng = new Random(seed * 31 + 7);
            var pass = new RM_MirrorKernel.Pass();
            var res = new RM_MirrorResult[site.sc.specs.Length];
            int nm = site.sc.specs.Length;
            RM_FieldLayout lay = RM_MirrorFieldKernel.Generate(nm, d, stones, want, setChain, attempts, k => rng.Next(k),
                i => SiteCandidates(site, i, rng), k => k, det => site.det = det,
                (int[] cfg, out int depth) =>
                {
                    Aim(site, cfg);
                    pass.Run(site.sc.world, site.sc.specs, nm, res, true, true, site.sc.sun, 1f, setChain);
                    depth = 0; for (int k = 0; k < nm; k++) if (res[k].fired && res[k].depth > depth) depth = res[k].depth;
                    var sl = new float[stones];
                    for (int k = 0; k < stones; k++) sl[k] = pass.Light[site.stoneCell[k]];
                    return RM_MirrorFieldKernel.LevelOf(sl, stones, StoneLitAt, StoneUnlitBelow);
                }, budget);
            return new GenRun { layout = lay, site = site, setN = setN, setWant = setWant, setDet = setDet, setChain = setChain, attempts = attempts, n = nm, d = d, want = want, budget = budget };
        }

        private static string GenerateCase(int seed)
        {
            GenCases++;
            GenRun g = RunGenerate(seed);
            RM_FieldLayout lay = g.layout;
            int n = g.n, d = g.d, want = g.want;
            // clamps
            Check(g.want >= 2 && g.want <= 4 && RM_MirrorFieldKernel.FieldMirrors(g.setN) >= 4 && RM_MirrorFieldKernel.FieldMirrors(g.setN) <= 6 && g.d >= 2,
                $"mapgen clamps let a setting through: mirrors {g.setN}->{RM_MirrorFieldKernel.FieldMirrors(g.setN)}, re-aims {g.setWant}->{g.want}, detents {g.setDet}->{g.d}");
            if (g.setN < 4 || g.setN > 6 || g.setWant < 2 || g.setWant > 4 || g.setDet != 3 || g.setChain < 1) GenOutOfRange++;
            // termination
            int total = RM_MirrorFieldKernel.Configurations(n, d);
            Check(lay != null, "Generate returned null");
            Check(lay.attempts >= 0 && lay.attempts <= g.attempts, $"Generate ran {lay.attempts} attempts, allowed {g.attempts}");
            Check(lay.evaluations <= (long)g.attempts * Math.Max(0, total), $"Generate evaluated {lay.evaluations} configurations, bound {g.attempts} x {total}");
            Check(lay.evaluations <= g.budget, $"Generate evaluated {lay.evaluations} configurations past its budget {g.budget}");
            if (lay.why == "evaluation budget spent") GenBudgetStops++;
            if (total < 0) { GenTooBig++; Check(!lay.Ok && lay.evaluations == 0, "an oversized space was evaluated or accepted"); return null; }
            if (!lay.Ok) { GenRefused++; Check(lay.why != null, "a refused layout carries no reason"); return null; }
            Check(lay.why == null && lay.report != null && lay.start >= 0 && lay.start < total, "an accepted layout lacks its report or start");
            // determinism: the same seed lays the same field
            GenRun g2 = RunGenerate(seed);
            Check(g2.layout.Ok && g2.layout.start == lay.start && g2.layout.report.solutions.SequenceEqual(lay.report.solutions)
                  && g2.layout.detents.Count == lay.detents.Count && g2.layout.detents.Zip(lay.detents, (a, b) => a.SequenceEqual(b)).All(x => x),
                "the same seed laid a different field");
            GenDeterministic++;
            if (g.setChain < 0) GenLowCap++;
            GenAccepted++;
            // detents: d distinct per mirror; every stone is some mirror's detent when there are enough mirrors
            FieldSite site = g.site;
            site.det = lay.detents;
            Check(lay.detents.Count == n, "detent lists != mirrors");
            foreach (var l in lay.detents) Check(l.Count == d && l.Distinct().Count() == d, "a mirror's detents are not d distinct targets");
            if (g.site.stones <= n)
                for (int k = 0; k < g.site.stones; k++) Check(lay.detents.Any(l => l.Contains(k)), $"stone {k} is no mirror's detent (the intended solution is missing)");
            // every configuration, independently: the reference pass and a hand classification
            var refLevel = new int[total]; var amb = new bool[total]; var light = new float[total][]; var depthOf = new int[total];
            var cfg = new int[n];
            for (int c = 0; c < total; c++)
            {
                RM_MirrorFieldKernel.Decode(c, n, d, cfg);
                refLevel[c] = RefLevel(site, cfg, out amb[c], out light[c], out depthOf[c]);
            }
            var rep = lay.report;
            var strict = new HashSet<int>(rep.solutions); var held = new HashSet<int>(rep.holds);
            Check(strict.IsSubsetOf(held), "a strict solution is not in the held set");
            bool anyStrict = false;
            for (int c = 0; c < total; c++)
            {
                if (amb[c]) continue;
                Check(strict.Contains(c) == (refLevel[c] == 2), $"configuration {c}: kernel strict {strict.Contains(c)}, reference level {refLevel[c]}");
                Check(held.Contains(c) == (refLevel[c] >= 1), $"configuration {c}: kernel held {held.Contains(c)}, reference level {refLevel[c]}");
                if (refLevel[c] == 2) anyStrict = true;
                if (refLevel[c] == 1) GenHeldOnly++;
                if (refLevel[c] >= 1) Check(Ham(lay.start, c, n, d) >= want, $"held configuration {c} is {Ham(lay.start, c, n, d)} jobs from the start, want >= {want}");
            }
            Check(anyStrict || rep.solutions.Any(s => amb[s]), "accepted with no configuration that lights every stone (reference)");
            Check(!amb[lay.start] ? refLevel[lay.start] == 0 : true, "the start is solved or held lit (reference)");
            Check(rep.minReAims >= want && rep.minStrict >= rep.minReAims, $"minReAims {rep.minReAims} / minStrict {rep.minStrict}, want {want}");
            // minReAims is the distance to the nearest HELD configuration (the lower bound the hints and the guarantee use)
            bool anyAmb = amb.Any(x => x);
            if (!anyAmb)
            {
                int refMin = -1, refStrictMin = -1;
                for (int c = 0; c < total; c++)
                {
                    int hm = Ham(lay.start, c, n, d);
                    if (refLevel[c] >= 1 && (refMin < 0 || hm < refMin)) refMin = hm;
                    if (refLevel[c] == 2 && (refStrictMin < 0 || hm < refStrictMin)) refStrictMin = hm;
                }
                Check(rep.minReAims == refMin, $"minReAims {rep.minReAims}, reference distance to the nearest held configuration {refMin}");
                Check(rep.minStrict == refStrictMin, $"minStrict {rep.minStrict}, reference {refStrictMin}");
                // PickStart on its own: any start it returns is >= want jobs from every held configuration (reference)
                for (int t = 0; t < 4; t++)
                {
                    int ps = RM_MirrorFieldKernel.PickStart(rep, want, seed * 13 + t);
                    if (ps < 0) continue;
                    for (int c = 0; c < total; c++)
                        if (refLevel[c] >= 1) Check(Ham(ps, c, n, d) >= want, $"PickStart chose {ps}, {Ham(ps, c, n, d)} jobs from held configuration {c}, want >= {want}");
                }
            }
            int cap = RM_MirrorKernel.DepthCap(g.setChain);
            Check(rep.bestDepth < cap, $"best solution needs relay depth {rep.bestDepth}, the pass caps at {cap}");
            // a colony's every job order shorter than `want`, with the stones' hysteresis: the vault never latches early
            if (g.site.stones > 0 && Math.Pow(n * (d - 1), want - 1) <= 5000)
            {
                var cur = new int[n]; RM_MirrorFieldKernel.Decode(lay.start, n, d, cur);
                var lit = new bool[g.site.stones];
                for (int k = 0; k < lit.Length; k++) lit[k] = light[lay.start][k] >= StoneLitAt;
                string early = Walk(cur, lit, 0, want - 1, n, d, light, amb);
                if (early != null) return early;
                GenWalks++;
            }
            return null;
        }

        private static string Walk(int[] cur, bool[] lit, int jobs, int maxJobs, int n, int d, float[][] light, bool[] amb)
        {
            if (lit.All(x => x)) return $"the vault latches after {jobs} jobs, fewer than the generator promised";
            if (jobs >= maxJobs) return null;
            for (int i = 0; i < n; i++)
            {
                int was = cur[i];
                for (int j = 0; j < d; j++)
                {
                    if (j == was) continue;
                    cur[i] = j;
                    int code = RM_MirrorFieldKernel.Encode(cur, n, d);
                    var nl = (bool[])lit.Clone();
                    for (int k = 0; k < nl.Length; k++)
                    {
                        float l = light[code][k];
                        nl[k] = nl[k] ? l >= StoneUnlitBelow : l >= StoneLitAt;     // hand-written hysteresis
                    }
                    string e = amb[code] ? null : Walk(cur, nl, jobs + 1, maxJobs, n, d, light, amb);
                    if (e != null) { cur[i] = was; return e; }
                }
                cur[i] = was;
            }
            return null;
        }

        // ═════════ explicit relay chains ═════════
        private static string ChainCase(int seed)
        {
            var r = new Random(seed);
            var sc = Gen(r, true);
            int n = sc.specs.Length;
            if (n < 2) return null;
            World wd = sc.world;
            if (r.Next(2) == 0) for (int i = 0; i < wd.W * wd.H; i++) { wd.wall[i] = false; wd.door[i] = false; wd.roof[i] = false; }
            int len = Math.Min(n, r.Next(2, 8));
            for (int k = 0; k < len; k++)
            {
                var m = sc.specs[k];
                m.spawned = true; m.holdsTarget = true; m.targetValid = true; m.hasAim = true;
                m.reflectivity = (float)(0.85 + r.NextDouble() * 0.15);
                m.source = k == 0 ? (float)(0.8 + r.NextDouble() * 0.2) : (r.Next(4) == 0 ? (float)(r.NextDouble() * 0.02) : 0f);
                if (k + 1 < len) { m.targetX = sc.specs[k + 1].minX; m.targetZ = sc.specs[k + 1].minZ; m.spotSize = Math.Max(m.spotSize, 1); }
                sc.specs[k] = m;
            }
            // the chain's head throws back along the sun: a relay arrives from the previous face, so keep the daylight up
            sc.daylight = 1f; sc.sunUp = true; sc.anyEffect = true; sc.maxChain = r.Next(1, 8);
            var pass = new RM_MirrorKernel.Pass();
            var got = new RM_MirrorResult[n]; var exp = new RM_MirrorResult[n];
            pass.Run(sc.world, sc.specs, n, got, sc.anyEffect, sc.sunUp, sc.sun, sc.daylight, sc.maxChain);
            Steps++;
            float[] expLight = RefPass(sc, exp);
            string err = Compare(sc, pass, got, exp, expLight) ?? Invariants(sc, pass, got);
            if (err != null) return err;
            Tally(sc, got);
            for (int k = 0; k < n; k++) if (got[k].ranFire && got[k].depth >= 2) ChainDeep++;
            return null;
        }
    }
}
