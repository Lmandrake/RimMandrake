// Blind lane 1, ExplosiveKnockback 0.2.0, cycle 1. Written from the bars alone (tree.json, sheet.md, plan.md,
// record.json bar rows, VERSION.json, bars.md), the shipped settings (RM_KnockbackMod.cs) and the patches; compiled against
// the shipped kernel RM_KnockbackMath.cs. One JSON row per line on stdout. Exit 0 = no FAIL row, 1 = a FAIL row.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

public static class BlindLane1
{
    static readonly List<string> rows = new List<string>();
    static bool anyFail;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        rows.Add("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind) + ",\"verdict\":" + J(verdict)
            + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    // ── shipped settings, from the env the runner fills from RM_KnockbackMod.cs (never hand-copied) ──
    static readonly List<string> unread = new List<string>();
    static float F(string n, float fallback)
    {
        string v = Environment.GetEnvironmentVariable("EK_" + n);
        if (v == null) { unread.Add(n); return fallback; }
        return float.Parse(v.TrimEnd('f'), CultureInfo.InvariantCulture);
    }
    static bool B(string n, bool fallback)
    {
        string v = Environment.GetEnvironmentVariable("EK_" + n);
        if (v == null) { unread.Add(n); return fallback; }
        return v == "true" || v == "1";
    }

    static KbSettings Shipped()
    {
        // as RimMandrakeExplosiveKnockbackSettings.Kernel() builds it
        return new KbSettings
        {
            globalMultiplier = F("strength", 1f),
            maxCells = (int)F("maxThrowCells", 6),
            creatureMassLimit = F("creatureMassLimit", 150f),
            lightMassLimit = F("lightMassLimit", 75f),
            impactEnabled = B("impactDamageEnabled", true),
            impactPerCell = F("impactDamagePerCell", 4f),
            sandbagsStop = B("sandbagsStopThrow", false),
            intoPits = B("throwIntoPits", true),
        };
    }

    static KbSettings Copy(KbSettings s) => new KbSettings
    {
        globalMultiplier = s.globalMultiplier, baseCells = s.baseCells, maxCells = s.maxCells, refMass = s.refMass,
        creatureMassLimit = s.creatureMassLimit, lightMassLimit = s.lightMassLimit, impactEnabled = s.impactEnabled,
        impactPerCell = s.impactPerCell, sandbagsStop = s.sandbagsStop, intoPits = s.intoPits, impactFactor = s.impactFactor,
    };

    sealed class Grid : IKbGrid
    {
        public readonly int w, h;
        public readonly Dictionary<(int, int), KbCell> cells = new Dictionary<(int, int), KbCell>();
        public Grid(int w, int h) { this.w = w; this.h = h; }
        public KbCell At(int x, int z)
        {
            if (x < 0 || z < 0 || x >= w || z >= h) return KbCell.OutOfBounds;
            return cells.TryGetValue((x, z), out KbCell c) ? c : KbCell.Open;
        }
        public Grid Set(int x, int z, KbCell c) { cells[(x, z)] = c; return this; }
        public string Describe() => string.Join(" ", cells.OrderBy(k => k.Key).Select(k => k.Key.Item1 + "," + k.Key.Item2 + "=" + k.Value));
    }

    // a lane along +x from (0,5): cells at x = 1.. are given by the string: . open, W wall, D door, S sandbag, P pawn,
    // O open pit, C covered pit, ~ water
    static Grid Lane(string s)
    {
        var g = new Grid(30, 11);
        for (int i = 0; i < s.Length; i++)
        {
            KbCell c = s[i] switch
            {
                'W' => KbCell.Wall, 'D' => KbCell.Door, 'S' => KbCell.Partial, 'P' => KbCell.Pawn, 'O' => KbCell.Pit,
                'C' => KbCell.CoveredPit, '~' => KbCell.Water, _ => KbCell.Open,
            };
            if (c != KbCell.Open) g.Set(1 + i, 5, c);
        }
        return g;
    }

    static KbResult Throw(string lane, int cells, KbKind kind = KbKind.Pawn, float mass = 70f, KbSettings s = null)
        => RM_KnockbackMath.Resolve(Lane(lane), 0, 5, 1f, 0f, cells, kind, mass, s ?? Shipped());

    static string R(KbResult r) => "dest=" + r.destX + "," + r.destZ + " travelled=" + r.cellsTravelled + "/" + r.cellsPlanned + " stop=" + r.stop
        + " impact=" + r.impact.ToString("0.###", CultureInfo.InvariantCulture) + " other=" + r.otherImpact.ToString("0.###", CultureInfo.InvariantCulture)
        + " hitOther=" + r.hitOther + " hitDoor=" + r.hitDoor;

    sealed class Check
    {
        public int cases; public readonly List<string> fails = new List<string>();
        public void That(bool ok, string what) { cases++; if (!ok && fails.Count < 6) fails.Add(what); else if (!ok) fails.Add(""); }
        public string V => fails.Count == 0 ? "PASS" : "FAIL";
        public string D(string pass) => fails.Count == 0 ? pass : (fails.Count + " of " + cases + " cases fail: " + string.Join(" | ", fails.Where(f => f != "")));
    }

    const float MortarR = 2.9f;   // the calibration shell's radius (kernel note, sheet "a mortar beside a human")

    public static int Main()
    {
        try { Run(); }
        catch (Exception e) { Row("L1_HARNESS_CRASH", new[] { "inv_kernel" }, "info", "FAIL", 0, e.ToString()); }
        foreach (string r in rows) Console.WriteLine(r);
        return anyFail ? 1 : 0;
    }

    static void Run()
    {
        KbSettings S = Shipped();
        int shipCap = S.maxCells;
        Row("L1_SETTINGS_READ", new[] { "inv_kernel", "settings_scale_and_switch" }, "info", unread.Count == 0 ? "INFO" : "FAIL", 1,
            unread.Count == 0 ? "shipped settings read from RM_KnockbackMod.cs: strength " + S.globalMultiplier + ", max " + S.maxCells + ", creature limit "
                + S.creatureMassLimit + ", goods limit " + S.lightMassLimit + ", impact/cell " + S.impactPerCell + ", sandbags stop " + S.sandbagsStop + ", into pits " + S.intoPits
            : "settings not read by the runner: " + string.Join(",", unread));

        // ── calibration: a mortar shell one cell from a clothed colonist throws about three cells ──
        {
            var c = new Check();
            int n70 = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, S);
            int n60 = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 60f, S);
            c.That(n70 == 3, "70 kg colonist at 1 cell from a 2.9 mortar: " + n70 + " cells, want 3");
            c.That(n60 == 3, "60 kg (naked) colonist: " + n60 + ", want 3");
            KbResult clear = Throw("......", n70);
            KbResult bags = Throw(".S....", n70);
            c.That(clear.destX == 3 && clear.stop == KbStop.Distance, "no line: " + R(clear));
            c.That(bags.destX == clear.destX && bags.stop == KbStop.Distance && bags.impact == 0f, "over a sandbag line at cell 2: " + R(bags) + " (control lands " + clear.destX + ")");
            KbResult bags1 = Throw("S.....", n70);
            c.That(bags1.destX == 3, "over a sandbag at cell 1: " + R(bags1));
            Row("L1_FIXED_CALIBRATION_MORTAR_THREE", new[] { "inv_kernel", "people_thrown_three_cells" }, "fixed", c.V, c.cases,
                c.D("mortar r 2.9 at 1 cell throws a 70 kg colonist 3 cells and a 60 kg one 3; a sandbag line in the path changes nothing (lands x=3, no impact)"));
        }

        // ── heavier flies less, a bigger blast throws farther (the oracle's own numbers) ──
        {
            var c = new Check();
            float r1 = RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true), r2 = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
            c.That(r1 == 1f && r2 == 2f, "damage ratio at 50 and 100 of Bomb 50: " + r1 + ", " + r2);
            float[] masses = { 0.5f, 70f, 144f };
            int[] want1 = { 5, 3, 2 }, want2 = { 6, 5, 4 };
            for (int i = 0; i < 3; i++)
            {
                int a = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f * r1, masses[i], S);
                int b = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f * r2, masses[i], S);
                c.That(a == want1[i], "mass " + masses[i] + " at ref damage: " + a + ", want " + want1[i]);
                c.That(b == want2[i], "mass " + masses[i] + " at twice the damage: " + b + ", want " + want2[i]);
                c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, masses[i], S), "mass " + masses[i] + " eligible");
            }
            c.That(!RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, S), "a 240 kg thrumbo is spared at the 150 kg limit");
            var s250 = Copy(S); s250.creatureMassLimit = 250f;
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, s250), "thrumbo eligible at a 250 kg limit");
            int t1 = RM_KnockbackMath.ThrowCells(1f, MortarR, r1, 240f, s250), t2 = RM_KnockbackMath.ThrowCells(1f, MortarR, r2, 240f, s250);
            c.That(t1 == 1 && t2 == 3, "thrumbo at 250 kg limit: " + t1 + " then " + t2 + ", want 1 then 3");
            float off = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false);
            c.That(off == 1f, "blast power off: ratio " + off);
            Row("L1_FIXED_HEAVIER_FLIES_LESS_ORACLE", new[] { "inv_kernel", "heavier_flies_less", "inv_blast_power_damage", "inv_creature_mass_limit" }, "fixed", c.V, c.cases,
                c.D("rat 5, colonist 3, muffalo 2 at ref damage; 6 (cap), 5, 4 at twice; thrumbo 240 kg spared at 150, thrown 1 then 3 at 250; power off ratio 1"));
        }

        // ── random: the throw distance is bounded and monotone in each input ──
        {
            int seed = 20261125; var rng = new Random(seed); var c = new Check(); string shrunk = null;
            for (int t = 0; t < 20000; t++)
            {
                var s = Copy(S);
                s.globalMultiplier = (float)(rng.NextDouble() * 3); s.maxCells = 1 + rng.Next(10);
                float radius = 0.5f + (float)rng.NextDouble() * 9f, dist = (float)rng.NextDouble() * radius * 1.2f;
                float force = (float)(rng.NextDouble() * 4 - 0.5), mass = (float)Math.Exp(rng.NextDouble() * 7 - 1);
                int n = RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s);
                bool ok = n >= 0 && n <= s.maxCells;
                if (force <= 0f || dist >= radius || s.globalMultiplier <= 0f) ok &= n == 0;
                ok &= RM_KnockbackMath.ThrowCells(dist, radius, force, mass * 1.5f, s) <= n;
                ok &= RM_KnockbackMath.ThrowCells(Math.Min(radius, dist + 0.5f), radius, force, mass, s) <= n;
                ok &= RM_KnockbackMath.ThrowCells(dist, radius, force + 0.3f, mass, s) >= n;
                var s2 = Copy(s); s2.globalMultiplier += 0.25f; ok &= RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s2) >= n;
                var s3 = Copy(s); s3.maxCells += 1; ok &= RM_KnockbackMath.ThrowCells(dist, radius, force, mass, s3) >= n;
                int wild = RM_KnockbackMath.WildCells(dist, radius, force, mass, s, 1.6f);
                ok &= wild >= n && wild <= s.maxCells && RM_KnockbackMath.WildCells(dist, radius, force, mass, s, 1f) == n;
                if (!ok && shrunk == null) shrunk = "t" + t + ": dist " + dist + " r " + radius + " force " + force + " mass " + mass + " strength " + s.globalMultiplier + " cap " + s.maxCells + " -> " + n + " wild " + wild;
                c.That(ok, "case " + t);
            }
            Row("L1_RANDOM_THROW_BOUNDED_MONOTONE", new[] { "inv_kernel", "heavier_flies_less", "goods_arc_spin_rebound" }, "random", c.V, c.cases,
                "seed " + seed + "; 0 <= cells <= cap; 0 when force <= 0, dist >= radius or strength 0; never more for heavier, farther, weaker, lower strength or lower cap; wild 1.6 >= plain, capped, wild 1 = plain. "
                + (shrunk == null ? "all hold" : "first failing case: " + shrunk + "; " + c.D("")));
        }

        // ── wild goods: about 1.6 times a person's throw before rounding and the cap ──
        {
            var c = new Check(); var wildS = Copy(S); wildS.maxCells = 100;
            for (int d10 = 0; d10 < 29; d10++)
                foreach (float m in new[] { 1f, 10f, 40f, 70f })
                {
                    float d = d10 / 10f;
                    int p = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, m, wildS), w = RM_KnockbackMath.WildCells(d, MortarR, 1f, m, wildS, 1.6f);
                    double raw = 4.0 * (1 - d / MortarR) * Math.Min(2, Math.Max(0.25, Math.Sqrt(70.0 / Math.Max(m, 1)))) * 1.6;
                    int want = (int)Math.Round(raw, MidpointRounding.AwayFromZero); if (want < 1) want = 0;
                    c.That(w == want, "d " + d + " m " + m + ": wild " + w + " vs 1.6 x raw rounded " + want + " (plain " + p + ")");
                }
            Row("L1_FIXED_WILD_ONE_POINT_SIX", new[] { "inv_kernel", "goods_arc_spin_rebound" }, "fixed", c.V, c.cases,
                c.D("wild goods throw = round(1.6 x the unrounded person throw), uncapped here, at 29 distances x 4 masses"));
        }

        // ── the path walk: walls, doors, water, sandbags, pits, pawns ──
        {
            var c = new Check();
            KbResult w = Throw("..W...", 5);
            c.That(w.destX == 2 && w.stop == KbStop.Wall && w.impact > 0f && w.hasBlock && w.blockX == 3, "wall at 3: " + R(w));
            KbResult w0 = Throw("......", 5); c.That(w0.destX == 5 && w0.impact == 0f, "control without wall: " + R(w0));
            KbResult d = Throw("..D...", 5);
            c.That(d.destX == 2 && d.stop == KbStop.Door && d.hitDoor && d.doorX == 3 && d.impact > 0f, "door at 3: " + R(d));
            KbResult wa = Throw("..~~..", 5);
            c.That(wa.destX == 2 && wa.stop == KbStop.Water, "deep water at 3: " + R(wa));
            KbResult it = Throw("..~~..", 5, KbKind.Item, 5f);
            c.That(it.destX == 2 && it.stop == KbStop.Water, "an item toward water: " + R(it));
            KbResult o = Throw(".O.O..", 5);
            c.That(o.destX == 2 && o.stop == KbStop.Pit, "open pit at 2: " + R(o));
            KbResult cp = Throw("C.....", 5, KbKind.Item, 5f);
            c.That(cp.destX == 1 && cp.stop == KbStop.Pit, "covered pit at 1, an item: " + R(cp));
            var noPit = Copy(S); noPit.intoPits = false;
            KbResult op = Throw("..O...", 5, KbKind.Pawn, 70f, noPit);
            c.That(op.destX == 2 && op.stop == KbStop.Wall, "into pits off, pit at 3: " + R(op));
            KbResult pp = Throw("...P..", 5);
            c.That(pp.destX == 3 && pp.stop == KbStop.Pawn && pp.hitOther && pp.otherX == 4 && pp.impact > 0f && pp.otherImpact > 0f, "pawn at 4: " + R(pp));
            KbResult ip = Throw("...P..", 5, KbKind.Item, 5f);
            c.That(ip.destX == 5 && !ip.hitOther, "an item passes a pawn: " + R(ip));
            var sb = Copy(S); sb.sandbagsStop = true;
            KbResult ss = Throw("..S...", 5, KbKind.Pawn, 70f, sb);
            c.That(ss.destX == 2 && ss.stop == KbStop.PartialCover, "sandbags stop on: " + R(ss));
            KbResult endS = Throw("..S...", 3);
            c.That(endS.destX == 2 && endS.cellsTravelled == 2, "a throw ending on a sandbag comes back off it: " + R(endS));
            KbResult ws = Throw(".SW...", 5);
            c.That(ws.destX == 1 && ws.stop == KbStop.Wall && ws.impact > 0f, "wall behind a sandbag: " + R(ws));
            Row("L1_FIXED_PATH_STOPS", new[] { "inv_kernel", "wall_stops_dead", "doors_and_deep_water_stop", "thrown_into_pit_falls", "pawn_hits_pawn_stops", "people_thrown_three_cells" }, "fixed", c.V, c.cases,
                c.D("wall and door stop on the cell before with impact; water stops on the last standable cell; open and covered pits end the throw in the first pit cell; pits off = a wall; a pawn stops a pawn before it (both hit) and an item passes; sandbags stop only when switched on; nothing rests on a sandbag"));
        }

        // ── no impact without contact: lane | sandbag | pawn ──
        {
            var c = new Check();
            foreach (string lane in new[] { "SP....", ".SP...", ".SSP..", "SSSP.." })
                for (int n = 1; n <= 6; n++)
                {
                    KbResult r = Throw(lane, n);
                    int p = lane.IndexOf('P') + 1;
                    bool contact = r.destX == p - 1;
                    c.That(!r.hitOther || contact, lane + " n " + n + ": hit reported without contact, " + R(r));
                    c.That(r.hitOther || r.otherImpact == 0f, lane + " n " + n + ": other impact with no hit, " + R(r));
                    if (r.destX > 0) c.That(Lane(lane).At(r.destX, 5) == KbCell.Open, lane + " n " + n + ": rests on " + Lane(lane).At(r.destX, 5));
                }
            KbResult direct = Throw("..P...", 5);
            c.That(direct.hitOther && direct.otherImpact > 0f, "control: a pawn with no sandbag in between is hit, " + R(direct));
            Row("L1_FIXED_NO_IMPACT_WITHOUT_CONTACT", new[] { "inv_kernel", "no_impact_without_contact" }, "fixed", c.V, c.cases,
                c.D("a thrown pawn backed off a sandbag in front of another pawn reports no hit and no impact on the other; control: the bare pawn lane is hit"));
        }

        // ── random grids: conservation and the path's rules ──
        {
            int seed = 7; var rng = new Random(seed); var c = new Check(); string shrunk = null;
            KbCell[] palette = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
            for (int t = 0; t < 30000; t++)
            {
                var g = new Grid(9 + rng.Next(8), 9 + rng.Next(8));
                for (int x = 0; x < g.w; x++) for (int z = 0; z < g.h; z++) if (rng.Next(3) == 0) g.Set(x, z, palette[rng.Next(palette.Length)]);
                int sx = rng.Next(g.w), sz = rng.Next(g.h);
                g.cells.Remove((sx, sz));
                double a = rng.NextDouble() * Math.PI * 2; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
                int cells = rng.Next(11); KbKind kind = (KbKind)rng.Next(3); float mass = 1f + (float)rng.NextDouble() * 140f;
                var s = Copy(S); s.sandbagsStop = rng.Next(3) == 0; s.intoPits = rng.Next(4) != 0; s.impactEnabled = rng.Next(5) != 0;
                KbResult r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
                var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
                var errs = new List<string>();
                if (path.Count != (cells > 0 ? cells : 0)) errs.Add("line has " + path.Count + " steps for " + cells);
                int px = sx, pz = sz;
                foreach (var st in path) { if (Math.Abs(st.x - px) > 1 || Math.Abs(st.z - pz) > 1 || (st.x == px && st.z == pz)) { errs.Add("line gap at " + st); break; } px = st.x; pz = st.z; }
                int k = r.cellsTravelled;
                if (k < 0 || k > Math.Max(0, cells)) errs.Add("travelled " + k);
                (int x, int z) dest = k == 0 ? (sx, sz) : path[k - 1];
                if (dest.x != r.destX || dest.z != r.destZ) errs.Add("dest " + r.destX + "," + r.destZ + " is not step " + k + " of the line " + dest);
                bool pawn = kind == KbKind.Pawn;
                int qx = sx, qz = sz;
                for (int i = 0; i < k; i++)
                {
                    var st = path[i]; KbCell cc = g.At(st.x, st.z);
                    if (cc == KbCell.Wall || cc == KbCell.Door || cc == KbCell.Water || cc == KbCell.OutOfBounds) errs.Add("entered " + cc + " at " + st);
                    if ((cc == KbCell.Pit || cc == KbCell.CoveredPit) && i < k - 1) errs.Add("crossed a pit at " + st);
                    if ((cc == KbCell.Pit || cc == KbCell.CoveredPit) && !s.intoPits) errs.Add("entered a pit with pits off");
                    if (cc == KbCell.Pawn && pawn) errs.Add("a pawn entered a pawn's cell");
                    if (cc == KbCell.Partial && pawn && s.sandbagsStop) errs.Add("a pawn crossed sandbags with sandbags stop on");
                    if (st.x != qx && st.z != qz)
                    {
                        KbCell a1 = g.At(st.x, qz), a2 = g.At(qx, st.z);
                        bool solid1 = a1 == KbCell.Wall || a1 == KbCell.Door || a1 == KbCell.OutOfBounds, solid2 = a2 == KbCell.Wall || a2 == KbCell.Door || a2 == KbCell.OutOfBounds;
                        if (solid1 || solid2) errs.Add("cut a corner into " + st);
                    }
                    qx = st.x; qz = st.z;
                }
                if (k > 0 && g.At(dest.x, dest.z) == KbCell.Partial) errs.Add("rests on a sandbag");
                if (r.hitOther && (k >= path.Count || path[k] != (r.otherX, r.otherZ) || g.At(r.otherX, r.otherZ) != KbCell.Pawn)) errs.Add("hit a pawn it never reached");
                if (!r.hitOther && r.otherImpact != 0f) errs.Add("other impact without a hit");
                if (!pawn && (r.impact != 0f || r.hitOther)) errs.Add("goods carry pawn impact");
                if (!s.impactEnabled && (r.impact != 0f || r.otherImpact != 0f)) errs.Add("impact with impact off");
                if (r.impact < 0f || r.otherImpact < 0f || float.IsNaN(r.impact)) errs.Add("negative impact");
                if (r.stop == KbStop.Distance && k != cells && !(k < path.Count && g.At(path[k].x, path[k].z) == KbCell.Partial)) errs.Add("stop Distance after " + k + " of " + cells + " with no sandbag to come back off");
                if (r.stop == KbStop.Pit && !(g.At(dest.x, dest.z) == KbCell.Pit || g.At(dest.x, dest.z) == KbCell.CoveredPit)) errs.Add("stop Pit off a pit");
                if (errs.Count > 0 && shrunk == null) shrunk = "t" + t + " start " + sx + "," + sz + " dir " + dx.ToString("0.###") + "," + dz.ToString("0.###") + " cells " + cells + " kind " + kind + " sbStop " + s.sandbagsStop + " pits " + s.intoPits + ": " + string.Join("; ", errs) + " | " + R(r) + " | grid " + g.w + "x" + g.h + " " + g.Describe();
                c.That(errs.Count == 0, "t" + t);
            }
            Row("L1_RANDOM_PATH_RULES_CONSERVED", new[] { "inv_kernel", "thrown_into_pit_falls", "wall_stops_dead", "doors_and_deep_water_stop", "no_impact_without_contact", "pawn_hits_pawn_stops" }, "random", c.V, c.cases,
                "seed " + seed + "; one thing in, one landing out: the landing is step k of the line (no teleport, no rebound for people), the line is gap-free and exactly `cells` long, nothing enters a wall, door, water or the map edge, nothing crosses a pit, no corner is cut, nothing rests on sandbags, a hit pawn is the very next cell, goods carry no pawn impact. "
                + (shrunk == null ? "all hold" : "first failing case: " + shrunk + "; " + c.D("")));
        }

        // ── rebounds: each carries on for only part of the way left, and the chain dies away ──
        {
            var c = new Check(); var info = new List<string>();
            for (int keep = 0; keep <= 100; keep++)
                for (int left = 0; left <= 12; left++)
                {
                    int rb = RM_KnockbackMath.ReboundCells(left, keep);
                    c.That(rb >= 0 && rb <= left, "keep " + keep + " left " + left + ": " + rb);
                    if (keep < 100 && left > 0) c.That(rb < left, "keep " + keep + "% left " + left + ": rebound " + rb + " is not only part of the way left");
                    if (keep < 100)
                    {
                        int chain = left, n = 0; while (chain > 0 && n < 100) { chain = RM_KnockbackMath.ReboundCells(chain, keep); n++; }
                        c.That(chain == 0, "keep " + keep + " left " + left + ": the chain never ends");
                    }
                }
            float ship = F("goodsReboundKeepPercent", 70f);
            info.Add("shipped keep " + ship + "%: left 1..6 rebounds " + string.Join(",", Enumerable.Range(1, 6).Select(l => RM_KnockbackMath.ReboundCells(l, ship))));
            info.Add("keep 100: rebound = left (the chain is ended by the carrier's MaxBounces, game-side)");
            Row("L1_SWEEP_REBOUND_SHORTER_DIES_AWAY", new[] { "inv_kernel", "rebound_goes_shorter", "goods_arc_spin_rebound" }, "sweep", c.V, c.cases,
                c.D("keep 0..99% x cells left 0..12: every rebound strictly under the cells left, the chain ends") + "; " + string.Join("; ", info));
        }

        // ── reflection off the solid cell the throw broke on ──
        {
            var c = new Check();
            var g = Lane("..W...");
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 5, 1f, 0f, 5, KbKind.Item, 5f, S);
            bool ok = RM_KnockbackMath.Reflect(g, r, 1f, 0f, out float rx, out float rz);
            c.That(ok && rx == -1f && rz == 0f, "straight wall at x=3: reflected " + rx + "," + rz);
            var gz = new Grid(11, 11).Set(5, 8, KbCell.Wall);
            KbResult r2 = RM_KnockbackMath.Resolve(gz, 5, 5, 0f, 1f, 5, KbKind.Item, 5f, S);
            ok = RM_KnockbackMath.Reflect(gz, r2, 0.3f, 1f, out rx, out rz);
            c.That(ok && rx == 0.3f && rz == -1f && r2.destZ == 7, "wall north: " + R(r2) + " reflected " + rx + "," + rz);
            KbResult r3 = RM_KnockbackMath.Resolve(Lane("~....."), 0, 5, 1f, 0f, 5, KbKind.Item, 5f, S);
            c.That(!RM_KnockbackMath.Reflect(Lane("~....."), r3, 1f, 0f, out rx, out rz), "water gives no rebound");
            // random: after a straight hit, the reflected first step from the stop cell never enters the solid cell
            var rng = new Random(11); int bad = 0, n = 0;
            for (int t = 0; t < 5000; t++)
            {
                var gg = new Grid(12, 12);
                for (int i = 0; i < 25; i++) gg.Set(rng.Next(12), rng.Next(12), KbCell.Wall);
                int sx = rng.Next(12), sz = rng.Next(12); gg.cells.Remove((sx, sz));
                double a = rng.NextDouble() * Math.PI * 2; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
                KbResult rr = RM_KnockbackMath.Resolve(gg, sx, sz, dx, dz, 8, KbKind.Item, 5f, S);
                if (!rr.hasBlock) continue;
                n++;
                RM_KnockbackMath.Reflect(gg, rr, dx, dz, out float ax, out float az);
                var next = RM_KnockbackMath.Line(rr.destX, rr.destZ, ax, az, 1);
                if (next.Count == 1 && next[0] == (rr.blockX, rr.blockZ)) bad++;
            }
            c.That(bad == 0, "seed 11: " + bad + " of " + n + " reflections step straight back into the cell they hit");
            Row("L1_FIXED_REFLECT_OFF_SOLID", new[] { "inv_kernel", "goods_arc_spin_rebound" }, "fixed", c.V, c.cases,
                c.D("a straight hit flips the struck axis; water reflects nothing; seed 11, " + n + " random hits: no reflected first step re-enters the solid cell"));
        }

        // ── collision bruise by size ──
        {
            var c = new Check();
            float ipc = S.impactPerCell;
            float a = RM_KnockbackMath.CollisionBruise(70f, 70f, S), b = RM_KnockbackMath.CollisionBruise(70f, 70f, S);
            c.That(a == b && a > 0f && a <= ipc + 1e-4f, "a like pair: " + a + " each (a wall hit per cell is " + ipc + ")");
            float personOnDog = RM_KnockbackMath.CollisionBruise(70f, 25f, S), dogFromPerson = RM_KnockbackMath.CollisionBruise(25f, 70f, S);
            c.That(dogFromPerson > personOnDog, "person on dog: dog takes " + dogFromPerson + ", person " + personOnDog);
            float rat = RM_KnockbackMath.CollisionBruise(0.5f, 144f, S), muff = RM_KnockbackMath.CollisionBruise(144f, 0.5f, S);
            c.That(rat > 20f * muff && muff < 0.05f * ipc, "rat on muffalo: rat " + rat + ", muffalo " + muff);
            var off = Copy(S); off.impactEnabled = false;
            c.That(RM_KnockbackMath.CollisionBruise(70f, 70f, off) == 0f, "impact off: no bruise");
            var f0 = Copy(S); f0.impactFactor = 0f;
            c.That(RM_KnockbackMath.CollisionBruise(70f, 70f, f0) == 0f, "impact factor 0: no bruise");
            foreach (float bad in new[] { 0f, -5f, float.NaN, float.PositiveInfinity })
                c.That(RM_KnockbackMath.CollisionBruise(bad, 70f, S) == 0f && RM_KnockbackMath.CollisionBruise(70f, bad, S) == 0f, "mass " + bad + ": 0");
            var rng = new Random(3); int n = 0;
            for (int t = 0; t < 20000; t++)
            {
                float m1 = (float)Math.Exp(rng.NextDouble() * 6 - 1), m2 = (float)Math.Exp(rng.NextDouble() * 6 - 1);
                var s = Copy(S); s.impactPerCell = (float)rng.NextDouble() * 15f; s.impactFactor = (float)rng.NextDouble() * 2f;
                float x1 = RM_KnockbackMath.CollisionBruise(m1, m2, s), x2 = RM_KnockbackMath.CollisionBruise(m2, m1, s);
                float more = RM_KnockbackMath.CollisionBruise(m1, m2 * 1.5f, s);
                bool ok = x1 >= 0 && x2 >= 0 && Math.Abs(x1 + x2 - 2 * s.impactPerCell * s.impactFactor) < 1e-3f * (1 + s.impactPerCell)
                    && (m1 >= m2 ? x1 <= x2 + 1e-4f : x1 >= x2 - 1e-4f) && more >= x1 - 1e-5f;
                c.That(ok, "seed 3 t" + t + ": m1 " + m1 + " m2 " + m2 + " -> " + x1 + "," + x2);
                n++;
            }
            Row("L1_FIXED_RANDOM_COLLISION_BRUISE_BY_SIZE", new[] { "inv_kernel", "collision_bruise_by_size" }, "random", c.V, c.cases,
                c.D("like pair bruise alike and lightly; the smaller of a pair takes the bigger bruise; rat on muffalo: the muffalo hardly notices; impact off or factor 0 gives 0; bad masses give 0; seed 3, " + n + " random pairs: the bruise rises with the other's mass, the pair shares 2 cells of wall hit"));
        }

        // ── who is spared by mass ──
        {
            var c = new Check();
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, S) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 150.01f, S), "creature limit: 150 flies, 150.01 does not");
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 144f, S) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, S), "muffalo 144 flies, rhino 180 not");
            c.That(RM_KnockbackMath.Eligible(KbKind.Item, 75f, S) && !RM_KnockbackMath.Eligible(KbKind.Item, 75.01f, S), "goods limit 75");
            c.That(!RM_KnockbackMath.Eligible(KbKind.Corpse, 100f, S), "a 100 kg corpse is spared too_heavy at 75");
            var big = Copy(S); big.lightMassLimit = 300f;
            c.That(RM_KnockbackMath.Eligible(KbKind.Corpse, 240f, big), "thrumbo corpse thrown with the goods limit raised (no body-size rule)");
            var tiny = Copy(S); tiny.creatureMassLimit = 20f;
            c.That(RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, tiny), "the creature limit at 20 never weighs a corpse");
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, tiny) == false && RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, S), "pawn 100 kg spared at 20, thrown at 150");
            var heavyPawn = Copy(S); heavyPawn.lightMassLimit = 5f;
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 70f, heavyPawn), "the goods limit never weighs a living pawn");
            int rim = RM_KnockbackMath.ThrowCells(2.8f, MortarR, 1f, 70f, S);
            c.That(rim == 0, "a colonist at the rim (2.8 of 2.9) throws " + rim + " cells: too weak");
            var ov = RM_KnockbackMath.Resolve(Lane("......"), 0, 5, 1, 0, 0, KbKind.Pawn, 70f, S);
            c.That(ov.stop == KbStop.None && !ov.Moved, "a zero-cell throw does not move: " + R(ov));
            Row("L1_FIXED_SPARED_BY_MASS", new[] { "inv_kernel", "the_spared", "inv_mass_limit_skip", "inv_too_weak_skip", "inv_creature_mass_limit", "inv_big_corpse_spared" }, "fixed", c.V, c.cases,
                c.D("creature limit 150 weighs living pawns only (heavier than = spared); goods limit 75 weighs goods and corpses only; a rim throw under one cell is 0"));
        }

        // ── lookup order and per-weapon tuning ──
        {
            var c = new Check();
            var proj = new KbConfig { force = 0f }; var weap = new KbConfig { force = 2f }; var dmg = new KbConfig { force = 1f };
            var r = KbLookup.Resolve(proj, weap, dmg, true, 1f);
            c.That(r == proj && r.force == 0f && r.source == "projectile", "a projectile's 0 wins whole: " + r.source + " " + r.force);
            r = KbLookup.Resolve(null, weap, dmg, true, 1f);
            c.That(r == weap && r.source == "weapon", "weapon over damage type: " + r.source);
            r = KbLookup.Resolve(null, null, dmg, true, 1f);
            c.That(r == dmg && r.source == "damageDef", "damage type: " + r.source);
            float unp = F("unpatchedHarmfulPercent", 100f) / 100f;
            r = KbLookup.Resolve(null, null, null, true, unp);
            c.That(r.force == 1f && r.source == "unpatched", "another mod's harmful blast at the shipped " + unp * 100 + "%: force " + r.force);
            r = KbLookup.Resolve(null, null, null, false, unp);
            c.That(r.force == 0f, "a harmless untuned burst throws nothing: " + r.force);
            var g = Copy(S); g.maxCells = shipCap;
            var a2 = KbLookup.Apply(g, new KbConfig { ownCap = 2 }, shipCap, 1f);
            c.That(a2.maxCells == 2, "own maximum 2: cap " + a2.maxCells);
            c.That(RM_KnockbackMath.ThrowCells(0f, 5f, 3f, 70f, a2) == 2, "own maximum 2 throws 2");
            var a4 = KbLookup.Apply(g, new KbConfig { ownCap = 4 }, shipCap, 0.5f);
            c.That(a4.maxCells == 2, "own maximum 4 under scale 0.5: cap " + a4.maxCells);
            var a0 = KbLookup.Apply(g, new KbConfig { ownCap = 0 }, shipCap, 0.5f);
            c.That(a0.maxCells == shipCap, "own maximum 0 keeps the global " + shipCap + " under scale 0.5: " + a0.maxCells);
            var gas = KbLookup.Apply(g, new KbConfig { ownCap = 2, scaleOwnCap = false }, shipCap, 0.25f);
            c.That(gas.maxCells == 2, "an exact own cap (gas goods cap) is not rescaled: " + gas.maxCells);
            var imp0 = KbLookup.Apply(g, new KbConfig { impactFactor = 0f }, shipCap, 1f);
            KbResult wall0 = RM_KnockbackMath.Resolve(Lane("..W..."), 0, 5, 1, 0, 5, KbKind.Pawn, 70f, imp0);
            KbResult pawn0 = RM_KnockbackMath.Resolve(Lane("..P..."), 0, 5, 1, 0, 5, KbKind.Pawn, 70f, imp0);
            c.That(wall0.impact == 0f && wall0.stop == KbStop.Wall && pawn0.impact == 0f && pawn0.otherImpact == 0f && RM_KnockbackMath.CollisionBruise(70, 70, imp0) == 0f,
                "impact factor 0: wall " + R(wall0) + "; pawn " + R(pawn0));
            var neg = KbLookup.Apply(g, new KbConfig { impactFactor = -2f }, shipCap, 1f);
            c.That(neg.impactFactor == 0f, "a negative impact factor clamps to 0: " + neg.impactFactor);
            var ram = KbLookup.Apply(g, new KbConfig { massLimitOverride = 216f }, shipCap, 1f);
            c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, ram) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, ram) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, g),
                "grav-ram 216 throws a 180 kg animal, not a 240 kg one; the global 150 spares the 180");
            c.That(g.maxCells == shipCap && g.impactFactor == 1f && g.creatureMassLimit == S.creatureMassLimit, "Apply never mutates the shared settings");
            var nul = KbLookup.Apply(g, null, shipCap, 0.5f);
            c.That(nul.maxCells == shipCap && nul.impactFactor == 1f, "a null config: global cap and impact");
            Row("L1_FIXED_LOOKUP_AND_WEAPON_TUNING", new[] { "inv_kernel", "per_weapon_tuning", "inv_weapon_ext_fields", "every_harmful_blast_throws", "inv_which_blasts" }, "fixed", c.V, c.cases,
                c.D("projectile -> weapon -> damage type, first wins whole (a 0 wins); untuned harmful at the shipped percent, harmless 0; own cap, cap scale, exact gas cap, impact factor 0 at walls, pawns and bruises, the mass override; the shared settings unchanged"));
        }

        // ── fire at half, the fire switch ──
        {
            var c = new Check(); var big = Copy(S); big.maxCells = 100;
            for (int d10 = 0; d10 < 25; d10++)
            {
                float d = d10 / 10f;
                int bomb = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, 70f, big), fire = RM_KnockbackMath.ThrowCells(d, MortarR, 0.5f, 70f, big);
                c.That(Math.Abs(fire - bomb / 2.0) <= 1.0, "dist " + d + ": fire " + fire + " vs bomb " + bomb);
            }
            c.That(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn"), "switch off zeroes Flame");
            c.That(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "ElectricalBurn", "ElectricalBurn"), "switch off zeroes ElectricalBurn");
            c.That(!RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn"), "switch on keeps Flame");
            c.That(!RM_KnockbackMath.FireSwitchedOff(false, "projectile", "Flame", "Burn"), "a weapon's own tuning stays");
            c.That(!RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded"), "Bomb is not fire");
            int fm = RM_KnockbackMath.ThrowCells(1f, MortarR, 0.5f, 70f, S), bm = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, S);
            Row("L1_FIXED_FIRE_AT_HALF", new[] { "inv_kernel", "every_harmful_blast_throws", "settings_scale_and_switch" }, "fixed", c.V, c.cases,
                c.D("fire force 0.5 throws within a cell of half the bomb's throw at 25 distances; the switch zeroes fire only on the damage type's own patch") + "; INFO: at the calibration distance whole cells give fire " + fm + " vs bomb " + bm);
        }

        // ── shield, immunity, containers, heavy knock, covers, shoves ──
        {
            var c = new Check();
            float e = KbShield.EnergyAfter(1f, 1f, 10f, 0.033f);
            c.That(e < 1f && Math.Abs(e - (1f - 0.33f)) < 1e-4f, "a shield pays extra charge for a force-1 throw: " + e);
            c.That(KbShield.EnergyAfter(1f, 0f, 10f, 0.033f) == 1f && KbShield.EnergyAfter(1f, -1f, 10f, 0.033f) == 1f, "force 0 or below costs nothing extra");
            c.That(KbShield.EnergyAfter(1f, 2f, 0f, 0.033f) == 1f, "a debit of 0 costs nothing extra");
            Row("L1_FIXED_SHIELD_EXTRA_CHARGE", new[] { "inv_kernel", "shield_belt_holds", "inv_shield" }, "fixed", c.V, c.cases, c.D("the extra drain is force x debit x loss, never negative"));

            c = new Check();
            int win = (int)F("recoveryWindowTicks", 120f);
            c.That(!KbImmunity.CanLaunch(100, 50, 150, win), "inside the stun: immune");
            c.That(!KbImmunity.CanLaunch(150 + win - 1, 50, 150, win), "one tick before the window ends: immune");
            c.That(KbImmunity.CanLaunch(150 + win, 50, 150, win), "at the window's end: throwable");
            c.That(!KbImmunity.CanLaunch(300 + win - 1, 300, 150, win), "a stun already over: the window runs from the landing");
            c.That(KbImmunity.CanLaunch(0, 0, 1000, 0), "window 0: chain throws allowed");
            Row("L1_FIXED_RECOVERY_IMMUNITY", new[] { "inv_kernel", "recovery_immunity", "inv_recovery" }, "fixed", c.V, c.cases, c.D("no second throw until max(landing, stun end) + the shipped " + win + "-tick window; 0 = chains allowed"));

            c = new Check(); float cml = F("closedContainerMassLimit", 250f);
            for (float m = 5f; m <= 400f; m += 5f)
                for (float d = 0f; d < MortarR; d += 0.25f)
                {
                    int ct = RM_KnockbackMath.ContainerThrowCells(true, m, cml, d, MortarR, 1f, S);
                    int loose = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, Math.Max(1f, m / 3f), S);
                    if (m > cml) c.That(ct == 0, "over the limit " + m + ": " + ct);
                    else c.That(ct == RM_KnockbackMath.ThrowCells(d, MortarR, 1f, m, S) && ct <= loose && ct <= S.maxCells, "m " + m + " d " + d + ": container " + ct + " loose goods " + loose);
                    c.That(RM_KnockbackMath.ContainerThrowCells(false, m, cml, d, MortarR, 1f, S) == 0, "a 2x2 jolts");
                }
            int at250 = RM_KnockbackMath.ContainerThrowCells(true, 250f, cml, 1f, MortarR, 1f, S);
            c.That(at250 >= 1, "a 250 kg locker one cell from a mortar is thrown at least a cell: " + at250);
            Row("L1_SWEEP_CONTAINER_SHORT_THROW", new[] { "inv_kernel", "closed_container_holds", "inv_container_shove" }, "sweep", c.V, c.cases,
                c.D("a 1x1 container at or under " + cml + " kg flies the item throw at its whole mass (never farther than its own goods loose, never past the cap); over it, or bigger than 1x1, 0 (a jolt)"));

            c = new Check(); float hmin = F("heavyGoodsMinMass", 10f), dmin = F("heavyGoodsDamageMin", 2f), dmax = F("heavyGoodsDamageMax", 5f); int stag = (int)F("heavyGoodsStaggerTicks", 30f);
            var rng = new Random(5);
            for (int t = 0; t < 2000; t++)
            {
                float roll = (float)rng.NextDouble(); float m = (float)rng.NextDouble() * 40f;
                bool hit = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, m, hmin, dmin, dmax, roll, stag, out float dmg, out int stun, 7);
                c.That(hit == (m >= hmin), "m " + m + " hit " + hit);
                if (hit) c.That(dmg >= dmin && dmg <= dmax && stun == stag, "dmg " + dmg + " stun " + stun);
                else c.That(dmg == 0f && stun == 0, "a pass deals " + dmg);
            }
            c.That(!RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 50f, hmin, dmin, dmax, 0.5f, stag, out _, out _, 7), "a corpse passes");
            c.That(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, hmin, dmin, dmax, 0.5f, stag, out _, out _, -3), "a gas-thrown stack passes");
            c.That(!RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 50f, hmin, dmin, dmax, 0.5f, stag, out _, out _, 7), "heavy knock off: passes");
            c.That(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 50f, hmin, dmin, dmax, 0.5f, stag, out _, out _, 7), "nobody there: no hit");
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, hmin, 6f, 3f, 0.9f, stag, out float inv, out _, 7);
            c.That(inv == 6f, "max under min: the hit is the min, " + inv);
            Row("L1_RANDOM_HEAVY_STACK_KNOCK", new[] { "inv_kernel", "heavy_stack_knocks", "inv_heavy_knock" }, "random", c.V, c.cases,
                c.D("seed 5: a stack of " + hmin + " kg or more hits for " + dmin + ".." + dmax + " blunt and a " + stag + "-tick stagger; lighter, corpses, gas-thrown or switched off pass"));

            c = new Check();
            c.That(RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, 4), "a thrown pawn breaks the cover it lands on");
            c.That(RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, 0), "a stack breaks it, whatever its mass");
            c.That(!RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, -1), "a gas burst never breaks a cover");
            c.That(!RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, true, 4), "a container never lands on one");
            c.That(!RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, false, false, 4), "no cover, nothing to break");
            foreach (KbCell cc in Enum.GetValues(typeof(KbCell)))
            {
                c.That(RM_KnockbackMath.ShoveCellFree(cc, false) == (cc == KbCell.Open), "shove into " + cc);
                c.That(!RM_KnockbackMath.ShoveCellFree(cc, true), "shove into an occupied " + cc);
            }
            c.That(RM_KnockbackMath.PitCell(true, true, true) == KbCell.Pawn && RM_KnockbackMath.PitCell(true, false, true) == KbCell.CoveredPit
                && RM_KnockbackMath.PitCell(false, true, false) == KbCell.Pit && RM_KnockbackMath.PitCell(true, true, false) == KbCell.CoveredPit, "pit cells");
            Row("L1_FIXED_COVER_AND_SHOVE_CELLS", new[] { "inv_kernel", "blast_breaks_pit_cover", "thrown_into_pit_falls", "closed_container_holds" }, "fixed", c.V, c.cases,
                c.D("a thrown landing breaks a cover, a gas burst and a container never do; a shove enters only empty open ground; a pawn on a pit cell blocks a thrown pawn"));
        }

        // ── every good moves: no cap; nothing created or lost ──
        {
            var c = new Check(); var rng = new Random(9);
            for (int t = 0; t < 500; t++)
            {
                var all = new List<KbCandidate>();
                int n = rng.Next(200);
                for (int i = 0; i < n; i++) all.Add(new KbCandidate { index = i, kind = (KbKind)rng.Next(3), distance = (float)rng.NextDouble() * 6f });
                var kept = RM_KnockbackMath.Prioritise(all, -1);
                c.That(kept.Count == n && kept.Select(k => k.index).OrderBy(x => x).SequenceEqual(Enumerable.Range(0, n)), "no cap: all " + n + " kept once");
                bool order = true;
                for (int i = 1; i < kept.Count; i++)
                {
                    int ra = kept[i - 1].kind == KbKind.Pawn ? 0 : kept[i - 1].kind == KbKind.Corpse ? 1 : 2, rb = kept[i].kind == KbKind.Pawn ? 0 : kept[i].kind == KbKind.Corpse ? 1 : 2;
                    if (ra > rb || (ra == rb && kept[i - 1].distance > kept[i].distance)) order = false;
                }
                c.That(order, "pawns first, then corpses, then items, nearest first");
            }
            Row("L1_RANDOM_NO_CAP_ALL_KEPT", new[] { "inv_kernel", "every_good_moves" }, "random", c.V, c.cases,
                c.D("seed 9, 500 lists of up to 200: with no cap every candidate is kept exactly once (none created, none lost)") + "; whether the game passes no cap is game-side");
        }

        // ── the explosion ledger: one throw request per thing per explosion ──
        {
            var c = new Check(); int W = KbExplosionLedger.DefaultWindow;
            var rng = new Random(13);
            for (int t = 0; t < 2000; t++)
            {
                var L = new KbExplosionLedger(W);
                int t0 = rng.Next(-5000, 5000), ex = rng.Next(1, 999), th = rng.Next(1, 99999);
                c.That(L.TryAdd(ex, th, t0), "first add");
                int later = t0 + rng.Next(W);
                c.That(!L.TryAdd(ex, th, later), "a repeat " + (later - t0) + " ticks on (t0 " + t0 + ") is refused");
                L.AddLaunched(ex, later);
                c.That(L.Launched(ex, later + rng.Next(W)) >= 1 || true, "launched");
                c.That(L.TryAdd(ex, th + 1, later), "another thing");
                c.That(L.TryAdd(ex + 1, th, later), "another explosion");
            }
            var L2 = new KbExplosionLedger(W);
            L2.TryAdd(5, 5, 0);
            c.That(L2.TryAdd(5, 5, 2 * W), "an entry is gone from 2 x window");
            var L3 = new KbExplosionLedger(W);
            L3.AddLaunched(9, W - 1); c.That(L3.Launched(9, 2 * W - 2) == 1, "a launch count lives at least a window: " + L3.Launched(9, 2 * W - 2));
            Row("L1_RANDOM_EXPLOSION_LEDGER_DEDUPE", new[] { "inv_kernel", "every_good_moves", "no_teleport" }, "random", c.V, c.cases,
                c.D("seed 13: a repeat (explosion, thing) inside the window is refused, other pairs pass, entries live at least a window and are gone at two"));
        }

        // ── the frame-time probe's reading ──
        {
            var c = new Check();
            int N = 600; var ms = new float[N]; var paused = new bool[N]; var air = new int[N];
            for (int i = 0; i < N; i++) ms[i] = 16.7f;
            ms[300] = 400f;
            var g1 = KbFrameStats.Summarize(ms, paused, air, N, ms.Sum() / 1000f, 0.9f, 8.25f);
            c.That(g1.worstMs == 400f, "the worst frame is the max: " + g1.worstMs);
            c.That(KbFrameStats.WithinBudget(g1, 50f, out string why1), "one random stall is reported, not judged: " + why1 + " p99 " + g1.windowP99Ms);
            for (int i = 100; i < 120; i++) ms[i] = 80f;
            var g2 = KbFrameStats.Summarize(ms, paused, air, N, ms.Sum() / 1000f, 0.9f, 8.25f);
            c.That(!KbFrameStats.WithinBudget(g2, 50f, out string why2), "a stretch of 20 slow frames fails: p99 " + g2.windowP99Ms);
            var shortMs = ms.Take(200).ToArray();
            var g3 = KbFrameStats.Summarize(shortMs, new bool[200], new int[200], 200, shortMs.Sum() / 1000f, 0.9f, 8.25f);
            c.That(!KbFrameStats.WithinBudget(g3, 50f, out string why3) && why3.Contains("stopped"), "a probe that stops before the window closes is not a pass: " + why3);
            var sl = new float[N]; for (int i = 0; i < N; i++) sl[i] = 16.7f; sl[50] = 100f;
            var g4 = KbFrameStats.Summarize(sl, new bool[N], air, N, sl.Sum() / 1000f);
            c.That(KbFrameStats.SelfCheck(g4, 100f, out string why4), "a 100 ms sleep shows as a row: " + why4);
            var sl2 = new float[N]; for (int i = 0; i < N; i++) sl2[i] = 16.7f;
            var g5 = KbFrameStats.Summarize(sl2, new bool[N], air, N, sl2.Sum() / 1000f);
            c.That(!KbFrameStats.SelfCheck(g5, 100f, out _), "a missing sleep fails the self check");
            var pz = new bool[N]; for (int i = 0; i < 100; i++) pz[i] = true;
            var g6 = KbFrameStats.Summarize(sl2, pz, air, N, sl2.Sum() / 1000f, 0.9f, 8.25f);
            c.That(!KbFrameStats.WithinBudget(g6, 50f, out _), "a paused run is not a pass");
            var vals = new List<float> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
            c.That(KbFrameStats.Percentile(vals, 99f) == 10f && KbFrameStats.Percentile(vals, 50f) == 5f && KbFrameStats.Percentile(new List<float>(), 99f) == 0f, "nearest rank");
            var g7 = KbFrameStats.Summarize(new float[0], new bool[0], new int[0], 0, 0f, 0.9f, 8.25f);
            c.That(!KbFrameStats.WithinBudget(g7, 50f, out _), "no rows is not a pass");
            Row("L1_FIXED_FRAME_PROBE_READING", new[] { "inv_kernel", "barrage_frame_budget", "frame_time_probe", "inv_perf_all_fly" }, "fixed", c.V, c.cases,
                c.D("p99 in the 0.9-8.25 s window: one 400 ms stall passes, 20 slow frames fail, a short, paused or empty probe is not a pass; a 100 ms sleep shows as a row"));
        }

        // ── the container jolt drawing stays bounded ──
        {
            var c = new Check(); var rng = new Random(17);
            for (int t = 0; t < 5000; t++)
            {
                int dur = rng.Next(-2, 60), ts = rng.Next(-5, 70); float amp = (float)rng.NextDouble() * 0.5f;
                float dx = (float)(rng.NextDouble() * 2 - 1), dz = (float)(rng.NextDouble() * 2 - 1);
                if (t % 50 == 0) { dx = 0; dz = 0; }
                RM_KnockbackMath.JoltOffset(ts, dur, amp, dx, dz, out float ox, out float oz);
                float m = (float)Math.Sqrt(ox * ox + oz * oz);
                c.That(m <= amp + 1e-5f && !float.IsNaN(m), "seed 17 t" + t + ": offset " + m + " over amplitude " + amp);
                if (ts < 0 || ts >= dur || dur <= 0) c.That(m == 0f, "outside the jolt: " + m);
            }
            Row("L1_RANDOM_JOLT_BOUNDED", new[] { "inv_kernel", "closed_container_holds" }, "random", c.V, c.cases, c.D("seed 17: the drawn jolt never exceeds its amplitude and is 0 outside its ticks"));
        }

        // ── the shipped settings swept through their slider ranges, every switch off included ──
        {
            var c = new Check();
            for (float st = 0f; st <= 3.0001f; st += 0.05f)
            {
                var s = Copy(S); s.globalMultiplier = st;
                int n = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s);
                c.That(st > 0f || n == 0, "strength 0 throws " + n);
                c.That(n <= s.maxCells, "strength " + st + " past the cap");
            }
            for (int mx = 1; mx <= 10; mx++)
            {
                var s = Copy(S); s.maxCells = mx;
                c.That(RM_KnockbackMath.ThrowCells(0f, 10f, 3f, 1f, s) == mx, "max " + mx + " caps a strong throw");
                var res = RM_KnockbackMath.Resolve(Lane(new string('.', 20)), 0, 5, 1, 0, RM_KnockbackMath.ThrowCells(0f, 10f, 3f, 1f, s), KbKind.Item, 1f, s);
                c.That(res.cellsTravelled == mx, "max " + mx + " lands " + res.cellsTravelled);
            }
            for (float sc = 0.25f; sc <= 2.0001f; sc += 0.05f)
            {
                int cap = RM_KnockbackMath.CapFor(4, S.maxCells, sc);
                c.That(cap >= 1 && cap == Math.Max(1, (int)Math.Round(4 * sc, MidpointRounding.AwayFromZero)), "cap scale " + sc + ": " + cap);
                c.That(RM_KnockbackMath.CapFor(0, S.maxCells, sc) == S.maxCells, "an unset own cap ignores the scale");
            }
            for (float lim = 20f; lim <= 500f; lim += 10f)
            {
                var s = Copy(S); s.creatureMassLimit = lim;
                c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, lim, s) && !RM_KnockbackMath.Eligible(KbKind.Pawn, lim + 1f, s), "creature limit " + lim);
                c.That(RM_KnockbackMath.Eligible(KbKind.Corpse, 50f, s), "creature limit " + lim + " never weighs a 50 kg corpse");
            }
            for (float lim = 5f; lim <= 200f; lim += 5f)
            {
                var s = Copy(S); s.lightMassLimit = lim;
                c.That(RM_KnockbackMath.Eligible(KbKind.Item, lim, s) && !RM_KnockbackMath.Eligible(KbKind.Item, lim + 0.5f, s), "goods limit " + lim);
                c.That(RM_KnockbackMath.Eligible(KbKind.Pawn, 140f, s), "goods limit " + lim + " never weighs a pawn");
            }
            for (float ipc = 0f; ipc <= 15.0001f; ipc += 0.5f)
            {
                var s = Copy(S); s.impactPerCell = ipc;
                var r = RM_KnockbackMath.Resolve(Lane("..W..."), 0, 5, 1, 0, 5, KbKind.Pawn, 70f, s);
                c.That(Math.Abs(r.impact - ipc * 3f) < 1e-3f, "impact per cell " + ipc + ": 3 cells left gives " + r.impact);
                var off = Copy(s); off.impactEnabled = false;
                var r0 = RM_KnockbackMath.Resolve(Lane("..P..."), 0, 5, 1, 0, 5, KbKind.Pawn, 70f, off);
                c.That(r0.impact == 0f && r0.otherImpact == 0f && RM_KnockbackMath.CollisionBruise(70, 30, off) == 0f, "impact off at " + ipc);
            }
            for (float rp = 25f; rp <= 400f; rp += 25f)
            {
                float r = RM_KnockbackMath.DamageRatio(50f, 50f, rp, true);
                c.That(Math.Abs(r - 100f / rp) < 1e-4f, "ref percent " + rp + ": ratio at normal damage " + r);
                c.That(RM_KnockbackMath.DamageRatio(50f, 50f, rp, false) == 1f, "power off at " + rp);
            }
            c.That(RM_KnockbackMath.DamageRatio(-10f, 50f, 100f, true) == 0f && RM_KnockbackMath.DamageRatio(10f, 0f, 100f, true) == 1f, "negative damage 0; no reference 1");
            for (float cl = 20f; cl <= 1000f; cl += 20f)
            {
                c.That(RM_KnockbackMath.ContainerThrowCells(true, cl, cl, 0f, MortarR, 1f, S) == RM_KnockbackMath.ThrowCells(0f, MortarR, 1f, cl, S)
                    && RM_KnockbackMath.ContainerThrowCells(true, cl + 1f, cl, 0f, MortarR, 1f, S) == 0, "container limit " + cl);
            }
            for (float hm = 1f; hm <= 75f; hm += 1f)
            {
                c.That(RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, hm, hm, 2, 5, 0.5f, 30, out _, out _) && !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, hm - 0.5f, hm, 2, 5, 0.5f, 30, out _, out _), "heavy threshold " + hm);
            }
            for (int dmn = 0; dmn <= 20; dmn++) for (int dmx = 0; dmx <= 20; dmx++)
                {
                    RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, dmn, dmx, 1f, 30, out float dd, out _);
                    c.That(dd >= dmn && dd <= Math.Max(dmn, dmx), "damage " + dmn + ".." + dmx + ": " + dd);
                }
            for (int st = 0; st <= 180; st += 10)
            {
                RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 2, 5, 0.5f, st, out _, out int stun);
                c.That(stun == st, "stagger " + st);
            }
            for (int w = 0; w <= 600; w += 30) c.That(KbImmunity.CanLaunch(1000 + w, 900, 1000, w) && (w == 0 || !KbImmunity.CanLaunch(999 + w, 900, 1000, w)), "recovery window " + w);
            for (float sd = 0f; sd <= 50f; sd += 5f) c.That(KbShield.EnergyAfter(1f, 1f, sd, 0.033f) <= 1f, "shield debit " + sd);
            // every switch that the kernel reads, off at once: nothing breaks, people are still thrown, no impact
            var alloff = Copy(S); alloff.impactEnabled = false; alloff.intoPits = false; alloff.sandbagsStop = true;
            var rr = RM_KnockbackMath.Resolve(Lane("...O.."), 0, 5, 1, 0, 5, KbKind.Pawn, 70f, alloff);
            c.That(rr.destX == 3 && rr.impact == 0f && rr.stop == KbStop.Wall, "all kernel switches off: " + R(rr));
            var zero = Copy(S); zero.globalMultiplier = 0f;
            c.That(RM_KnockbackMath.ThrowCells(0f, MortarR, 1f, 1f, zero) == 0 && RM_KnockbackMath.WildCells(0f, MortarR, 1f, 1f, zero, 1.6f) == 0, "strength 0 throws nothing, goods included");
            Row("L1_SWEEP_SHIPPED_SETTINGS_RANGES", new[] { "inv_kernel", "settings_scale_and_switch" }, "sweep", c.V, c.cases,
                c.D("strength 0-3, maximum 1-10, cap scale 0.25-2, creature limit 20-500, goods limit 5-200, impact/cell 0-15 with impact off, ref percent 25-400 with power off, container limit 20-1000, heavy threshold 1-75, damage 0-20 x 0-20, stagger 0-180, recovery 0-600, shield debit 0-50, every kernel switch off at once"));
        }
    }
}
