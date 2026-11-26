// Blind lane 1, ExplosiveKnockback 0.2.0 cycle 2 (judge-1795662842). Written from the bars (tree.json leaves, record.json
// rows, sheet) and the shipped settings alone, against the shipped kernel RM_KnockbackMath.cs. One JSON row per line on stdout.
// Exit 0 = no FAIL row; 1 = a FAIL row. Settings come in KB_* env vars, read from RM_KnockbackMod.cs by run_lane1.py.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

static class BlindLane1
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static bool anyFail;
    static float F(string k, float d) { var v = Environment.GetEnvironmentVariable(k); return v != null && float.TryParse(v, NumberStyles.Float, Inv, out var f) ? f : d; }
    static bool B(string k, bool d) { var v = Environment.GetEnvironmentVariable(k); return v == null ? d : v == "1"; }
    static string J(string s) => "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        Console.WriteLine("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind)
            + ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    sealed class Grid : IKbGrid
    {
        public readonly Dictionary<(int, int), KbCell> cells = new Dictionary<(int, int), KbCell>();
        public int w = 40, h = 40;
        public KbCell At(int x, int z)
        {
            if (x < 0 || z < 0 || x >= w || z >= h) return KbCell.OutOfBounds;
            return cells.TryGetValue((x, z), out var c) ? c : KbCell.Open;
        }
        public Grid Set(int x, int z, KbCell c) { cells[(x, z)] = c; return this; }
    }

    // the shipped defaults, as RimMandrakeExplosiveKnockbackSettings.Kernel() builds them
    static KbSettings Shipped()
    {
        return new KbSettings
        {
            globalMultiplier = F("KB_STRENGTH", 1f),
            maxCells = (int)F("KB_MAX", 6),
            creatureMassLimit = F("KB_CREATURE_LIMIT", 150f),
            lightMassLimit = F("KB_LIGHT_LIMIT", 75f),
            impactEnabled = B("KB_IMPACT_ON", true),
            impactPerCell = F("KB_IMPACT_PER_CELL", 4f),
            sandbagsStop = B("KB_SANDBAGS_STOP", false),
            intoPits = B("KB_INTO_PITS", true),
        };
    }

    // mortar shell: vanilla Shell_HighExplosive explosionRadius 2.9 (the kernel's own calibration comment); Bomb force 1.0 (patch)
    const float MortarR = 2.9f;

    static int Main()
    {
        var s = Shipped();
        float keep = F("KB_REBOUND_KEEP", 70f);
        float wild = F("KB_WILD", 1.6f);

        // ── people_thrown_three_cells: mortar, 1 cell, clothed armed colonist (70 kg ref), force 1 ──
        {
            int c = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s);
            int cNaked = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 60f, s);
            var g = new Grid(); g.Set(12, 10, KbCell.Partial); g.Set(12, 11, KbCell.Partial); g.Set(12, 9, KbCell.Partial);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, c, KbKind.Pawn, 70f, s);
            var r0 = RM_KnockbackMath.Resolve(new Grid(), 10, 10, 1f, 0f, c, KbKind.Pawn, 70f, s);
            bool ok = c == 3 && cNaked == 3 && r.destX == 13 && r.destZ == 10 && r.stop == KbStop.Distance && r.impact == 0f
                      && r0.destX == r.destX && r0.destZ == r.destZ;
            Row("L1_MORTAR_THREE_CELLS_OVER_SANDBAGS", new[] { "people_thrown_three_cells", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 4,
                $"mortar r2.9 d1 force1: 70kg->{c}, 60kg->{cNaked} (want 3 each); sandbag line at x12: dest ({r.destX},{r.destZ}) stop {r.stop} impact {r.impact}; no line: ({r0.destX},{r0.destZ}). Pass: 3 cells, past the line, same cell as without it");
            float hi = 60f; while (RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, hi + 0.1f, s) == 3) hi += 0.1f;
            float lo = 60f; while (lo > 1f && RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, lo - 0.1f, s) == 3) lo -= 0.1f;
            Row("L1_INFO_THREE_CELL_MASS_BAND", new[] { "people_thrown_three_cells" }, "info", "INFO", 1,
                $"a mortar at 1 cell throws 3 cells for a pawn of {lo:0.0}-{hi:0.0} kg (Mass incl. gear); heavier gear (e.g. 80 kg) gives 2, a light pawn 4. The bar says about three; the band is recorded, not judged");
        }

        // ── heavier_flies_less oracle numbers. The leaf gives the kernel's cells for the scene's creatures at their start
        //    mass: rat 5, colonist 3, muffalo 2 at the reference damage and 6 / 5 / 4 at twice. The colonist is the 70 kg
        //    reference. The test finds the mass band of each creature that meets the oracle and asserts each band is a
        //    real interval holding a plausible mass (rat under 10 kg, muffalo 100-160 kg); the bands are printed. ──
        {
            float ratio2 = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
            Func<float, int, int, bool> meets = (m, w1, w2) => RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, m, s) == w1 && RM_KnockbackMath.ThrowCells(1f, MortarR, ratio2, m, s) == w2;
            string Band(int w1, int w2, out float lo, out float hi) { lo = -1; hi = -1; for (float m = 0.5f; m <= 400f; m += 0.5f) if (meets(m, w1, w2)) { if (lo < 0) lo = m; hi = m; } return lo < 0 ? "none" : $"{lo}-{hi} kg"; }
            string rb = Band(5, 6, out float rlo, out float rhi), cb = Band(3, 5, out float clo, out float chi), mb = Band(2, 4, out float mlo, out float mhi);
            bool thrumboSpared = !RM_KnockbackMath.Eligible(KbKind.Pawn, 230f, s);
            var s250 = Shipped(); s250.creatureMassLimit = 250f;
            string tb = "none"; float tlo = -1, thi = -1;
            for (float m = 150.5f; m <= 250f; m += 0.5f) if (RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, m, s250) == 1 && RM_KnockbackMath.ThrowCells(1f, MortarR, 2f, m, s250) == 3) { if (tlo < 0) tlo = m; thi = m; }
            if (tlo > 0) tb = $"{tlo}-{thi} kg";
            bool ok = rlo > 0 && rlo <= 10f && clo <= 70f && chi >= 70f && mlo > 0 && mlo <= 160f && mhi >= 100f && thrumboSpared && tlo > 0;
            Row("L1_HEAVIER_FLIES_LESS_ORACLE_CELLS", new[] { "heavier_flies_less", "inv_creature_mass_limit", "inv_blast_power_damage", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 5,
                $"mass bands meeting the oracle: rat (5, x2 6) {rb}; colonist (3, x2 5) {cb}, holds 70: {clo <= 70f && chi >= 70f}; muffalo (2, x2 4) {mb}; thrumbo over 150 spared: {thrumboSpared}; thrumbo at limit 250 (1 then 3) {tb}. The scene's real masses must fall in these bands (stage 6 reads them)");
        }

        // ── monotonicity: heavier never farther, nearer never shorter, more force never shorter, cap respected (random) ──
        {
            var rnd = new Random(20261125); int n = 0; string fail = null;
            for (int i = 0; i < 200000 && fail == null; i++)
            {
                n++;
                float r = 0.5f + (float)rnd.NextDouble() * 9f, d = (float)rnd.NextDouble() * r * 1.2f, f = (float)rnd.NextDouble() * 4f, m = 0.5f + (float)rnd.NextDouble() * 600f;
                float m2 = m + (float)rnd.NextDouble() * 200f, d2 = d + (float)rnd.NextDouble() * 2f, f2 = f + (float)rnd.NextDouble() * 2f;
                int c = RM_KnockbackMath.ThrowCells(d, r, f, m, s);
                if (c < 0 || c > s.maxCells) fail = $"cells {c} out of [0,{s.maxCells}] at d{d} r{r} f{f} m{m}";
                else if (RM_KnockbackMath.ThrowCells(d, r, f, m2, s) > c) fail = $"heavier m{m2} > m{m} flies farther (d{d} r{r} f{f})";
                else if (RM_KnockbackMath.ThrowCells(d2, r, f, m, s) > c) fail = $"farther d{d2} > d{d} flies farther (r{r} f{f} m{m})";
                else if (RM_KnockbackMath.ThrowCells(d, r, f2, m, s) < c) fail = $"stronger f{f2} > f{f} flies shorter (d{d} r{r} m{m})";
                else if (d >= r && c != 0) fail = $"outside radius d{d} >= r{r} throws {c}";
            }
            Row("L1_THROW_MONOTONE_AND_CAPPED_RANDOM", new[] { "heavier_flies_less", "inv_caps", "inv_kernel" }, "random", fail == null ? "PASS" : "FAIL", n,
                "seed 20261125; " + (fail ?? "200000 cases: cells in [0,max], heavier/farther never more, stronger never less, 0 outside radius"));
        }

        // ── blast power: twice the damage throws farther (or capped), type normal damage = ratio 1, switch off = 1 ──
        {
            var cases = new List<string>(); bool ok = true;
            ok &= RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true) == 1f;
            ok &= RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true) == 2f;
            ok &= RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false) == 1f;
            ok &= RM_KnockbackMath.DamageRatio(100f, 0f, 100f, true) == 1f;     // no usable reference
            ok &= RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true) == 0f;     // negative counts as 0
            ok &= RM_KnockbackMath.DamageRatio(100f, 50f, 200f, true) == 1f;    // ref percent 200: 100 dmg is "normal"
            // "a bigger blast that throws no farther" must not happen while below the cap
            int bad = 0, n = 0;
            for (float m = 1f; m <= 150f; m += 1f) for (float d = 0f; d < MortarR; d += 0.25f)
            {
                n++;
                int a = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, m, s), b = RM_KnockbackMath.ThrowCells(d, MortarR, 2f, m, s);
                if (a >= 2 && a < s.maxCells && b <= a) { bad++; if (cases.Count < 3) cases.Add($"m{m} d{d}: {a}->{b}"); }
            }
            int same1 = 0; for (float m = 1f; m <= 150f; m += 1f) for (float d = 0f; d < MortarR; d += 0.25f) { if (RM_KnockbackMath.ThrowCells(d, MortarR, 1f, m, s) == 1 && RM_KnockbackMath.ThrowCells(d, MortarR, 2f, m, s) == 1) same1++; }
            Row("L1_INFO_RIM_ONE_CELL_DOUBLE_DAMAGE", new[] { "heavier_flies_less" }, "info", "INFO", 1, $"{same1} of 1800 (mass, distance) cases at the rim throw 1 cell at both damages (raw 0.5-0.75 doubles to under 1.5); recorded, not judged: the leaf's scene stands at 1 cell");
            Row("L1_BLAST_POWER_DOUBLE_DAMAGE_FARTHER", new[] { "heavier_flies_less", "inv_blast_power_damage", "inv_kernel" }, "sweep", ok && bad == 0 ? "PASS" : "FAIL", n + 6,
                $"DamageRatio fixed cases ok={ok}; double damage below the cap never throws a creature already thrown 2+ cells no farther: {n - bad}/{n} {string.Join("; ", cases)}");
        }

        // ── the_spared / mass limits: creature limit weighs living pawns only, goods limit weighs goods and corpses only ──
        {
            bool ok = true; var why = new List<string>();
            void Chk(bool c, string w) { if (!c) { ok = false; why.Add(w); } }
            Chk(!RM_KnockbackMath.Eligible(KbKind.Pawn, 150.01f, s), "pawn just over 150 thrown");
            Chk(RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s), "pawn at 150 spared (limit is 'heavier than')");
            Chk(RM_KnockbackMath.Eligible(KbKind.Pawn, 120f, s), "120 kg pawn spared by goods limit");
            Chk(!RM_KnockbackMath.Eligible(KbKind.Corpse, 75.5f, s), "corpse 75.5 thrown");
            Chk(!RM_KnockbackMath.Eligible(KbKind.Item, 76f, s), "item 76 thrown");
            Chk(RM_KnockbackMath.Eligible(KbKind.Corpse, 70f, s), "70 kg corpse spared");
            var s20 = Shipped(); s20.creatureMassLimit = 20f;
            Chk(RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, s20), "creature limit 20 spares a human corpse");
            var sHi = Shipped(); sHi.lightMassLimit = 200f;
            Chk(RM_KnockbackMath.Eligible(KbKind.Corpse, 190f, sHi), "thrumbo-size corpse spared with goods limit raised");
            // a weapon's own creature limit
            var own = KbLookup.Apply(s, new KbConfig { massLimitOverride = 250f }, s.maxCells, 1f);
            Chk(RM_KnockbackMath.Eligible(KbKind.Pawn, 216f, own), "weapon own limit 250 spares 216 kg");
            Chk(own.lightMassLimit == s.lightMassLimit, "own creature limit changed the goods limit");
            Chk(!RM_KnockbackMath.Eligible(KbKind.Pawn, 216f, KbLookup.Apply(s, new KbConfig(), s.maxCells, 1f)), "no override throws 216");
            Row("L1_SPARED_BY_MASS_LIMITS", new[] { "the_spared", "inv_who_is_spared", "inv_mass_limit_skip", "inv_creature_mass_limit", "inv_big_corpse_spared", "per_weapon_tuning", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 11,
                ok ? "creature limit 150 on living pawns only, goods limit 75 on goods and corpses only, weapon override applies to pawns only" : string.Join("; ", why));
        }

        // ── too weak at the rim: a throw under one cell is 0; at least one cell moves ──
        {
            bool ok = true; int n = 0; string w = "";
            for (float d = 0; d < 3f; d += 0.01f) { n++; int c = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, 70f, s); double raw = 4.0 * (1 - Math.Min(1, d / MortarR)); if ((raw < 0.5 && c != 0) || (raw >= 0.5 && c < 1)) { ok = false; w = $"d{d} raw{raw:0.00} cells{c}"; } }
            Row("L1_TOO_WEAK_RIM_ROUNDS_TO_ZERO", new[] { "the_spared", "inv_too_weak_skip", "inv_kernel" }, "sweep", ok ? "PASS" : "FAIL", n, ok ? "raw < 0.5 -> 0, raw >= 0.5 -> >= 1, over d 0..3 at r 2.9" : w);
        }

        // ── path walk: walls, doors, water, pawns, pits, sandbags. Fixed geometry on a straight +x ray from (10,10). ──
        {
            var res = new List<string>(); bool ok = true;
            void Chk(string name, bool c, KbResult r) { if (!c) { ok = false; res.Add($"{name}: dest({r.destX},{r.destZ}) trav {r.cellsTravelled} stop {r.stop} imp {r.impact} other {r.otherImpact} hit {r.hitOther}"); } }
            KbResult R(Grid g, int cells, KbKind k = KbKind.Pawn, KbSettings ss = null) => RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, cells, k, 70f, ss ?? s);
            var r1 = R(new Grid().Set(12, 10, KbCell.Wall), 3); Chk("wall", r1.destX == 11 && r1.stop == KbStop.Wall && r1.impact > 0f, r1);
            var r1b = R(new Grid(), 3); Chk("wall-removed control", r1b.destX == 13 && r1b.stop == KbStop.Distance, r1b);
            var r2 = R(new Grid().Set(12, 10, KbCell.Door), 3); Chk("door", r2.destX == 11 && r2.stop == KbStop.Door && r2.hitDoor && r2.doorX == 12 && r2.impact > 0f, r2);
            var r3 = R(new Grid().Set(12, 10, KbCell.Water), 3); Chk("water", r3.destX == 11 && r3.stop == KbStop.Water, r3);
            var r3b = R(new Grid().Set(11, 10, KbCell.Water), 3); Chk("water next", r3b.destX == 10 && r3b.cellsTravelled == 0, r3b);
            var r4 = R(new Grid().Set(12, 10, KbCell.Pawn), 3); Chk("pawn", r4.destX == 11 && r4.stop == KbStop.Pawn && r4.hitOther && r4.otherX == 12 && r4.impact > 0f && r4.otherImpact > 0f, r4);
            var r4i = R(new Grid().Set(12, 10, KbCell.Pawn), 3, KbKind.Item); Chk("item passes pawn cell (kernel)", r4i.destX == 13, r4i);
            var r5 = R(new Grid().Set(12, 10, KbCell.Pit), 3); Chk("open pit: stops inside first pit cell", r5.destX == 12 && r5.stop == KbStop.Pit, r5);
            var r5c = R(new Grid().Set(12, 10, KbCell.CoveredPit), 3); Chk("covered pit: stops in it", r5c.destX == 12 && r5c.stop == KbStop.Pit, r5c);
            var r5i = R(new Grid().Set(12, 10, KbCell.Pit), 5, KbKind.Item); Chk("item into pit", r5i.destX == 12 && r5i.stop == KbStop.Pit, r5i);
            var sNoPit = Shipped(); sNoPit.intoPits = false;
            var r6 = R(new Grid().Set(12, 10, KbCell.Pit), 3, KbKind.Pawn, sNoPit); Chk("pits off: pit is a wall", r6.destX == 11 && r6.stop == KbStop.Wall, r6);
            var r7 = R(new Grid().Set(13, 10, KbCell.Partial), 3); Chk("never rests on sandbags", r7.destX == 12 && r7.stop == KbStop.Distance, r7);
            var sSb = Shipped(); sSb.sandbagsStop = true;
            var r8 = R(new Grid().Set(12, 10, KbCell.Partial), 3, KbKind.Pawn, sSb); Chk("sandbags stop on", r8.destX == 11 && r8.stop == KbStop.PartialCover, r8);
            var r8i = R(new Grid().Set(12, 10, KbCell.Partial), 3, KbKind.Item, sSb); Chk("goods pass sandbags even with stop on", r8i.destX == 13, r8i);
            // no_impact_without_contact: lane 4 | sandbag 5 | pawn 6 — from (10,10): sandbag 11, pawn 12
            var r9 = R(new Grid().Set(11, 10, KbCell.Partial).Set(12, 10, KbCell.Pawn), 3);
            Chk("sandbag before pawn: nobody hit", !r9.hitOther && r9.otherImpact == 0f && r9.destX == 10, r9);
            var r9b = R(new Grid().Set(11, 10, KbCell.Partial).Set(12, 10, KbCell.Pawn), 3, KbKind.Pawn, sSb);
            Chk("sandbag stop on, pawn beyond: nobody hit", !r9b.hitOther && r9b.otherImpact == 0f, r9b);
            // impact factor 0 and impact off: no hurt to thrown or hit
            var s0 = KbLookup.Apply(s, new KbConfig { impactFactor = 0f }, s.maxCells, 1f);
            var r10 = R(new Grid().Set(12, 10, KbCell.Pawn), 3, KbKind.Pawn, s0); Chk("impact factor 0 at pawn", r10.impact == 0f && r10.otherImpact == 0f, r10);
            var r10w = R(new Grid().Set(12, 10, KbCell.Wall), 3, KbKind.Pawn, s0); Chk("impact factor 0 at wall", r10w.impact == 0f && r10w.destX == 11, r10w);
            var sOff = Shipped(); sOff.impactEnabled = false;
            var r11 = R(new Grid().Set(12, 10, KbCell.Door), 3, KbKind.Pawn, sOff); Chk("impact off at door", r11.impact == 0f, r11);
            // diagonal corner: never cut a wall corner
            var gd = new Grid().Set(11, 10, KbCell.Wall);
            var r12 = RM_KnockbackMath.Resolve(gd, 10, 10, 1f, 1f, 3, KbKind.Pawn, 70f, s); Chk("diagonal corner", r12.destX == 10 && r12.destZ == 10 && r12.stop == KbStop.Wall, r12);
            // map edge
            var r13 = RM_KnockbackMath.Resolve(new Grid(), 38, 10, 1f, 0f, 4, KbKind.Pawn, 70f, s); Chk("map edge", r13.destX == 39 && r13.stop == KbStop.OutOfBounds, r13);
            Row("L1_PATH_WALK_STOPS", new[] { "wall_stops_dead", "pawn_hits_pawn_stops", "doors_and_deep_water_stop", "thrown_into_pit_falls", "no_impact_without_contact", "people_thrown_three_cells", "per_weapon_tuning", "inv_kernel", "inv_pits_receive" }, "fixed", ok ? "PASS" : "FAIL", 22,
                ok ? "22 geometries: wall/door/water/pawn stop on the cell before, pits stop inside the first pit cell, pits off = wall, sandbags pass and are never a resting cell, sandbag before pawn hits nobody, impact 0 under factor 0 / impact off, no corner cutting, edge" : string.Join(" | ", res));
        }

        // ── path conservation (random): travelled <= planned, dest at grid distance travelled along the line, dest never a
        //    blocked or sandbag cell, a non-Distance stop only at a blocker, impact >= 0 (random grids, seed recorded) ──
        {
            var rnd = new Random(77031); int n = 0; string fail = null; int[] shrink = null;
            KbCell[] kinds = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
            for (int i = 0; i < 60000 && fail == null; i++)
            {
                n++;
                var g = new Grid { w = 25, h = 25 };
                for (int k = 0; k < 60; k++) g.Set(rnd.Next(25), rnd.Next(25), kinds[rnd.Next(kinds.Length)]);
                int sx = 12, sz = 12; g.cells.Remove((sx, sz));
                double a = rnd.NextDouble() * 2 * Math.PI; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
                int cells = rnd.Next(0, 11); KbKind kind = (KbKind)rnd.Next(3);
                var ss = Shipped(); ss.sandbagsStop = rnd.Next(2) == 0; ss.intoPits = rnd.Next(4) != 0;
                float mass = 1f + (float)rnd.NextDouble() * 150f;
                var r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, ss);
                var line = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
                int cheb = Math.Max(Math.Abs(r.destX - sx), Math.Abs(r.destZ - sz));
                KbCell dc = g.At(r.destX, r.destZ);
                bool onLine = r.cellsTravelled == 0 ? (r.destX == sx && r.destZ == sz) : (line[r.cellsTravelled - 1] == (r.destX, r.destZ));
                if (r.cellsTravelled > cells || r.cellsTravelled < 0) fail = "travelled > planned";
                else if (!onLine) fail = "dest not the travelled-th cell of the line";
                else if (cells > 0 && line.Count != cells) fail = $"line has {line.Count} steps, planned {cells}";
                else if (r.cellsTravelled > 0 && (dc == KbCell.Wall || dc == KbCell.Door || dc == KbCell.Water || dc == KbCell.Partial || dc == KbCell.OutOfBounds || (dc == KbCell.Pawn && kind == KbKind.Pawn)))
                    fail = "rests on a " + dc;
                else if (cheb != r.cellsTravelled) fail = $"grid distance {cheb} != travelled {r.cellsTravelled}";
                else if (r.impact < 0f || r.otherImpact < 0f || float.IsNaN(r.impact)) fail = "negative impact";
                else if (r.cellsTravelled > 0 && (dc == KbCell.Pit || dc == KbCell.CoveredPit) && r.stop != KbStop.Pit) fail = "rests in a pit with stop " + r.stop;
                else if (r.hitOther && kind != KbKind.Pawn) fail = "goods hit a pawn in the kernel";
                if (fail != null) shrink = new[] { cells, (int)kind, ss.sandbagsStop ? 1 : 0, ss.intoPits ? 1 : 0 };
                if (fail != null) fail += $" | case i{i} dir({dx:0.000},{dz:0.000}) cells {cells} kind {kind} sbStop {ss.sandbagsStop} pits {ss.intoPits} -> dest({r.destX},{r.destZ}) on {dc} trav {r.cellsTravelled} stop {r.stop}; path " + string.Join(" ", line.Select(p => p.x + "," + p.z + ":" + g.At(p.x, p.z)));
            }
            Row("L1_PATH_CONSERVATION_RANDOM", new[] { "inv_kernel", "wall_stops_dead", "thrown_into_pit_falls", "doors_and_deep_water_stop", "goods_arc_spin_rebound" }, "random", fail == null ? "PASS" : "FAIL", n,
                "seed 77031; " + (fail ?? "60000 random 25x25 grids: travelled <= planned, dest = the travelled-th line cell at that grid distance, never resting on wall/door/water/sandbag/edge/a pawn (for a pawn), pit rests only with stop Pit, impact >= 0"));
        }

        // ── nothing thrown across a pit: no path ever has a pit cell before its destination (random) ──
        {
            var rnd = new Random(4242); int n = 0; string fail = null;
            for (int i = 0; i < 40000 && fail == null; i++)
            {
                n++;
                var g = new Grid { w = 25, h = 25 };
                for (int k = 0; k < 40; k++) g.Set(rnd.Next(25), rnd.Next(25), rnd.Next(2) == 0 ? KbCell.Pit : KbCell.CoveredPit);
                g.cells.Remove((12, 12));
                double a = rnd.NextDouble() * 2 * Math.PI; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
                int cells = rnd.Next(1, 11); var kind = (KbKind)rnd.Next(3);
                var r = RM_KnockbackMath.Resolve(g, 12, 12, dx, dz, cells, kind, 50f, s);
                var line = RM_KnockbackMath.Line(12, 12, dx, dz, cells);
                for (int j = 0; j < r.cellsTravelled - 1; j++) { var c = g.At(line[j].x, line[j].z); if (c == KbCell.Pit || c == KbCell.CoveredPit) { fail = $"crossed pit at {line[j]} to ({r.destX},{r.destZ}) i{i}"; break; } }
            }
            Row("L1_NO_THROW_ACROSS_A_PIT_RANDOM", new[] { "thrown_into_pit_falls", "inv_pits_receive", "inv_kernel" }, "random", fail == null ? "PASS" : "FAIL", n, "seed 4242; " + (fail ?? "40000 random pit fields: no path passes a pit cell before its end"));
        }

        // ── Line: exactly `cells` grid steps, each step to an 8-neighbour, last at Chebyshev distance `cells`, straight away ──
        {
            var rnd = new Random(99); int n = 0; string fail = null;
            for (int i = 0; i < 100000 && fail == null; i++)
            {
                n++;
                double a = rnd.NextDouble() * 2 * Math.PI; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a); int cells = rnd.Next(0, 13);
                var L = RM_KnockbackMath.Line(0, 0, dx, dz, cells);
                if (L.Count != cells) { fail = $"count {L.Count} != {cells}"; break; }
                int px = 0, pz = 0;
                foreach (var p in L) { if (Math.Max(Math.Abs(p.x - px), Math.Abs(p.z - pz)) != 1) { fail = $"jump at {p}"; break; } px = p.x; pz = p.z; }
                if (fail == null && cells > 0) { var e = L[cells - 1]; if (Math.Max(Math.Abs(e.x), Math.Abs(e.z)) != cells) fail = "end not at distance cells"; if (e.x * dx + e.z * dz <= 0) fail = $"end {e} not away from the blast along ({dx},{dz})"; }
            }
            Row("L1_LINE_GRID_STEPS_RANDOM", new[] { "inv_kernel", "people_thrown_three_cells" }, "random", fail == null ? "PASS" : "FAIL", n, "seed 99; " + (fail ?? "100000 directions x 0-12 cells: exact step count, 8-adjacent steps, end at that grid distance, away from the blast"));
        }

        // ── rebound: part of the cells left, so bounces die away; keep sweep 0..100 ──
        {
            int n = 0; string fail = null;
            for (int kp = 0; kp <= 100 && fail == null; kp++)
            for (int left = 0; left <= 12 && fail == null; left++)
            {
                n++;
                int rc = RM_KnockbackMath.ReboundCells(left, kp);
                if (rc < 0 || rc > left) fail = $"keep {kp} left {left} -> {rc}";
                else if (kp < 100 && left > 0 && rc >= left) fail = $"keep {kp} left {left} -> {rc}: not only part of the way";
                // chain dies: repeated rebounds terminate below 100%
                if (fail == null && kp < 100) { int l = left, steps = 0; while (l > 0 && steps < 50) { l = RM_KnockbackMath.ReboundCells(l, kp); steps++; } if (l > 0) fail = $"keep {kp}: chain from {left} never ends"; }
            }
            int at70 = RM_KnockbackMath.ReboundCells(10, keep), at70b = RM_KnockbackMath.ReboundCells(3, keep), at70c = RM_KnockbackMath.ReboundCells(1, keep);
            bool near = at70 == 7 && at70b == 2 && at70c == 0;
            Row("L1_REBOUND_PART_OF_CELLS_LEFT", new[] { "rebound_goes_shorter", "goods_arc_spin_rebound", "inv_goods_fly", "inv_kernel" }, "sweep", fail == null && near ? "PASS" : "FAIL", n + 3,
                (fail ?? $"keep 0..100 x left 0..12: 0 <= rebound <= left, < left below 100, chains end") + $"; shipped keep {keep}: 10->{at70}, 3->{at70b}, 1->{at70c} (near 0.7 of the cells left, rounded down)");
        }

        // ── Reflect: a straight hit flips its axis; no block, no rebound ──
        {
            bool ok = true; var g = new Grid().Set(12, 10, KbCell.Wall);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 4, KbKind.Item, 5f, s);
            ok &= RM_KnockbackMath.Reflect(g, r, 1f, 0f, out float rx, out float rz) && rx == -1f && rz == 0f;
            var r2 = RM_KnockbackMath.Resolve(new Grid(), 10, 10, 1f, 0f, 4, KbKind.Item, 5f, s);
            ok &= !RM_KnockbackMath.Reflect(new Grid(), r2, 1f, 0f, out _, out _);
            var gz = new Grid().Set(10, 12, KbCell.Door);
            var r3 = RM_KnockbackMath.Resolve(gz, 10, 10, 0f, 1f, 4, KbKind.Item, 5f, s);
            ok &= RM_KnockbackMath.Reflect(gz, r3, 0f, 1f, out float qx, out float qz) && qz == -1f && qx == 0f;
            // the rebound points back into open ground: its first step is not the solid cell
            var back = RM_KnockbackMath.Line(r.destX, r.destZ, rx, rz, 1);
            ok &= back.Count == 1 && g.At(back[0].x, back[0].z) == KbCell.Open;
            Row("L1_REFLECT_OFF_WALL_AND_DOOR", new[] { "goods_arc_spin_rebound", "rebound_goes_shorter", "inv_goods_fly", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 4, "x wall flips x, z door flips z, no block = no rebound, rebound's first cell open");
        }

        // ── goods fly wild: about 1.6 times a person; farther than a person at the same distance (sc_storeroom_mortar shape 1.3-2.0) ──
        {
            int n = 0, bad = 0; string ex = "";
            for (float d = 0; d < MortarR; d += 0.1f) for (float m = 1; m <= 75; m += 2)
            {
                int p = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, 70f, s); int g = RM_KnockbackMath.WildCells(d, MortarR, 1f, m, s, wild); int gp = RM_KnockbackMath.WildCells(d, MortarR, 1f, 70f, s, wild);
                n++;
                if (gp < p) { bad++; ex = $"d{d} 70kg good {gp} < person {p}"; }
                if (RM_KnockbackMath.WildCells(d, MortarR, 1f, m, s, 1f) != RM_KnockbackMath.ThrowCells(d, MortarR, 1f, m, s)) { bad++; ex = "wild 1 != kernel"; }
            }
            Row("L1_GOODS_WILD_NOT_SHORTER_THAN_PERSON", new[] { "goods_arc_spin_rebound", "inv_goods_fly", "inv_kernel" }, "sweep", bad == 0 ? "PASS" : "FAIL", n, bad == 0 ? $"wild {wild}: a good never flies shorter than a person of its mass at the same distance; wild 1 = the plain kernel" : ex);
        }

        // ── per_weapon_tuning: projectile > weapon > damage type; zero wins; own cap and scale ──
        {
            bool ok = true; var w = new List<string>();
            void Chk(bool c, string m) { if (!c) { ok = false; w.Add(m); } }
            var p = new KbConfig { force = 0f }; var wp = new KbConfig { force = 2f }; var dd = new KbConfig { force = 1f };
            var c1 = KbLookup.Resolve(p, wp, dd, true, 1f); Chk(c1.source == "projectile" && c1.force == 0f, "projectile zero does not win");
            var c2 = KbLookup.Resolve(null, wp, dd, true, 1f); Chk(c2.source == "weapon" && c2.force == 2f, "weapon over damage def");
            var c3 = KbLookup.Resolve(null, null, dd, true, 1f); Chk(c3.source == "damageDef", "damage def");
            var c4 = KbLookup.Resolve(null, null, null, true, F("KB_UNPATCHED_PCT", 100f) / 100f); Chk(c4.force == 1f && c4.source == "unpatched", "unpatched harmful at 100%");
            var c5 = KbLookup.Resolve(null, null, null, false, 1f); Chk(c5.force == 0f, "harmless unpatched throws");
            Chk(RM_KnockbackMath.ThrowCells(1f, MortarR, c1.force, 70f, s) == 0, "zero force throws");
            Chk(RM_KnockbackMath.CapFor(2, 6, 1f) == 2, "own max 2");
            Chk(RM_KnockbackMath.CapFor(4, 6, 0.5f) == 2, "own max 4 x0.5");
            Chk(RM_KnockbackMath.CapFor(0, 6, 0.5f) == 6, "own max 0 keeps global under scale");
            Chk(RM_KnockbackMath.CapFor(1, 6, 0.25f) == 1, "own max never below 1");
            var a2 = KbLookup.Apply(s, new KbConfig { ownCap = 2 }, 6, 1f);
            Chk(RM_KnockbackMath.ThrowCells(0f, 5f, 3f, 5f, a2) == 2, "own max 2 throws 2");
            var gas = KbLookup.Apply(s, new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 0.25f); Chk(gas.maxCells == 2, "gas goods cap rescaled");
            Chk(s.maxCells == (int)F("KB_MAX", 6) && s.impactFactor == 1f, "Apply mutated shared settings");
            Row("L1_PER_WEAPON_LOOKUP_AND_CAPS", new[] { "per_weapon_tuning", "inv_weapon_ext_fields", "inv_caps", "every_harmful_blast_throws", "inv_which_blasts", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 13, ok ? "projectile > weapon > damage def whole; zero wins; unpatched harmful 100%, harmless 0; own max 2 -> 2, 4x0.5 -> 2, 0 keeps global, >= 1; gas cap exact; shared settings untouched" : string.Join("; ", w));
        }

        // ── fire at half: Flame 0.5 vs Bomb 1.0 -> throw length ratio near 0.5 (patched forces) ──
        {
            int nb = 0, nf = 0; double sumB = 0, sumF = 0;
            for (float d = 0; d < 6f; d += 0.05f) for (float m = 40; m <= 100; m += 5) { nb++; sumB += RM_KnockbackMath.ThrowCells(d, 6f, 1f, m, s); sumF += RM_KnockbackMath.ThrowCells(d, 6f, 0.5f, m, s); nf++; }
            double ratio = sumF / Math.Max(1, sumB);
            bool off = RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn") && RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "X", "ElectricalBurn")
                       && !RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn") && !RM_KnockbackMath.FireSwitchedOff(false, "weapon", "Flame", "Burn")
                       && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded");
            Row("L1_FIRE_AT_HALF_RATIO", new[] { "every_harmful_blast_throws", "settings_scale_and_switch", "inv_which_blasts", "inv_kernel" }, "sweep", ratio > 0.4 && ratio < 0.6 && off ? "PASS" : "FAIL", nb + 5,
                $"sum fire cells / sum bomb cells = {ratio:0.000} over {nb} (d, mass) cases at r 6 (want near 0.5); fire switch off zeroes only the damage type's own fire force: {off}");
        }

        // ── collision bruise by size ──
        {
            bool ok = true; var w = new List<string>();
            void Chk(bool c, string m) { if (!c) { ok = false; w.Add(m); } }
            float personOnDog = RM_KnockbackMath.CollisionBruise(13f, 70f, s), dogFromPerson = RM_KnockbackMath.CollisionBruise(70f, 13f, s);
            Chk(personOnDog > dogFromPerson, $"dog bruise {personOnDog} not above person bruise {dogFromPerson}");
            float ratOnMuffalo = RM_KnockbackMath.CollisionBruise(1f, 140f, s), muffaloFromRat = RM_KnockbackMath.CollisionBruise(140f, 1f, s);
            Chk(ratOnMuffalo > 10f * muffaloFromRat && muffaloFromRat < 0.1f * s.impactPerCell, $"rat {ratOnMuffalo} muffalo {muffaloFromRat}");
            float like = RM_KnockbackMath.CollisionBruise(70f, 70f, s), like2 = RM_KnockbackMath.CollisionBruise(72f, 68f, s), like3 = RM_KnockbackMath.CollisionBruise(68f, 72f, s);
            Chk(Math.Abs(like - s.impactPerCell) < 1e-4f, $"like pair {like} != one cell's wall hit {s.impactPerCell}");
            Chk(Math.Abs(like2 - like3) < 0.15f * like, "about the same size not alike");
            var sOff = Shipped(); sOff.impactEnabled = false; Chk(RM_KnockbackMath.CollisionBruise(70f, 70f, sOff) == 0f, "impact off bruises");
            Chk(RM_KnockbackMath.CollisionBruise(70f, 70f, KbLookup.Apply(s, new KbConfig { impactFactor = 0f }, 6, 1f)) == 0f, "impact factor 0 bruises");
            Chk(RM_KnockbackMath.CollisionBruise(70f, 0f, s) == 0f, "no other pawn bruises");
            Chk(RM_KnockbackMath.CollisionBruise(float.NaN, 70f, s) == 0f && RM_KnockbackMath.CollisionBruise(70f, float.PositiveInfinity, s) == 0f, "non-finite mass");
            // monotone, random
            var rnd = new Random(31337); int n = 0;
            for (int i = 0; i < 50000 && ok; i++)
            {
                n++; float a = 0.1f + (float)rnd.NextDouble() * 500, b = 0.1f + (float)rnd.NextDouble() * 500, b2 = b + (float)rnd.NextDouble() * 100, a2 = a + (float)rnd.NextDouble() * 100;
                float x = RM_KnockbackMath.CollisionBruise(a, b, s);
                if (RM_KnockbackMath.CollisionBruise(a, b2, s) < x - 1e-5f) { ok = false; w.Add($"heavier other {b2}>{b} bruises less (own {a})"); }
                if (RM_KnockbackMath.CollisionBruise(a2, b, s) > x + 1e-5f) { ok = false; w.Add($"heavier self {a2}>{a} bruised more (other {b})"); }
                if (x < 0 || x > 2f * s.impactPerCell + 1e-4f) { ok = false; w.Add("out of range " + x); }
            }
            Row("L1_COLLISION_BRUISE_BY_SIZE", new[] { "collision_bruise_by_size", "inv_kernel" }, "random", ok ? "PASS" : "FAIL", n + 9, "seed 31337; " + (ok ? "person on dog hurts the dog more; rat/muffalo; like pair = one cell's wall hit each, alike; off/factor 0/no pawn/non-finite = 0; rises with other's mass, falls with own, in [0, 2 x per cell]" : string.Join("; ", w.Take(4))));
        }

        // ── immunity window ──
        {
            int win = (int)F("KB_RECOVERY", 120);
            bool ok = !KbImmunity.CanLaunch(100, 50, 90, win) && KbImmunity.CanLaunch(90 + win, 50, 90, win) && !KbImmunity.CanLaunch(89 + win, 50, 90, win)
                      && KbImmunity.CanLaunch(51, 50, 90, 0) && !KbImmunity.CanLaunch(50 + win + 10, 50, 200, win);
            Row("L1_RECOVERY_WINDOW", new[] { "recovery_immunity", "inv_recovery", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 5, $"window {win}: no launch until stun end + window; window 0 chains; a stun longer than the landing still counts");
        }

        // ── shield: absorbing the throw costs extra charge, never gives charge back ──
        {
            float per = F("KB_SHIELD_DEBIT", 10f);
            bool ok = KbShield.EnergyAfter(1f, 1f, per, 0.033f) < 1f && KbShield.EnergyAfter(1f, 0f, per, 0.033f) == 1f && KbShield.EnergyAfter(1f, -5f, per, 0.033f) == 1f
                      && KbShield.EnergyAfter(1f, 2f, per, 0.033f) < KbShield.EnergyAfter(1f, 1f, per, 0.033f);
            Row("L1_SHIELD_EXTRA_CHARGE", new[] { "shield_belt_holds", "inv_shield", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 4, $"debit per force {per}: a throw costs extra charge, more for more force, none for 0 or negative");
        }

        // ── heavy stack knocks ──
        {
            float mn = F("KB_HEAVY_MIN", 10f), dmin = F("KB_HEAVY_DMIN", 2f), dmax = F("KB_HEAVY_DMAX", 5f); int st = (int)F("KB_HEAVY_STAGGER", 30);
            bool ok = true; float dmg; int stun;
            for (float roll = 0; roll <= 1f; roll += 0.05f) { ok &= RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 75f, mn, dmin, dmax, roll, st, out dmg, out stun) && dmg >= 2f && dmg <= 5f && stun > 0; }
            ok &= !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 3f, mn, dmin, dmax, 0.5f, st, out dmg, out stun) && dmg == 0f;   // cloth passes
            ok &= !RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 60f, mn, dmin, dmax, 0.5f, st, out _, out _);
            ok &= !RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 75f, mn, dmin, dmax, 0.5f, st, out _, out _);
            ok &= !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 75f, mn, dmin, dmax, 0.5f, st, out _, out _, -3); // gas-thrown passes
            ok &= !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 75f, mn, dmin, dmax, 0.5f, st, out _, out _);
            Row("L1_HEAVY_STACK_KNOCK", new[] { "heavy_stack_knocks", "inv_heavy_knock", "settings_scale_and_switch", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 26, $"steel stack: blunt {dmin}-{dmax} and stagger {st}; cloth, corpse, switch off, gas-thrown, nobody there: no hit");
        }

        // ── pit cover: blast-thrown landing breaks it, gas never, container never; a pawn on a cover blocks a thrown pawn ──
        {
            bool ok = RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, 5) && RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, 0)
                      && !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, -1) && !RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, true, 5)
                      && !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, false, false, 5)
                      && RM_KnockbackMath.PitCell(true, true, true) == KbCell.Pawn && RM_KnockbackMath.PitCell(true, false, true) == KbCell.CoveredPit && RM_KnockbackMath.PitCell(false, true, false) == KbCell.Pit
                      && !RM_KnockbackMath.ShoveCellFree(KbCell.Pit, false) && !RM_KnockbackMath.ShoveCellFree(KbCell.CoveredPit, false) && RM_KnockbackMath.ShoveCellFree(KbCell.Open, false) && !RM_KnockbackMath.ShoveCellFree(KbCell.Open, true);
            Row("L1_PIT_COVER_RULES", new[] { "thrown_into_pit_falls", "blast_breaks_pit_cover", "gas_shoves_pawn_on_pit_cover", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 11, "landing on a cover breaks it (blast only, not gas, not a container); a pawn on a cover blocks a thrown pawn; a shove enters only free open ground");
        }

        // ── containers: 1x1 under the container limit thrown, never past the cap, shorter than the same goods loose ──
        {
            float lim = F("KB_CONTAINER_LIMIT", 250f); int n = 0; string fail = null;
            for (float m = 5; m <= 400 && fail == null; m += 5) for (float d = 0; d < MortarR && fail == null; d += 0.2f)
            {
                n++;
                int c = RM_KnockbackMath.ContainerThrowCells(true, m, lim, d, MortarR, 1f, s);
                if (m > lim && c != 0) fail = $"over-limit {m} thrown {c}";
                if (c > s.maxCells) fail = "past cap";
                if (!RM_KnockbackMath.ContainerThrowCells(false, m, lim, d, MortarR, 1f, s).Equals(0)) fail = "2x2 thrown";
                float goods = Math.Min(m, 75f) * 0.8f; if (c > RM_KnockbackMath.WildCells(d, MortarR, 1f, goods, s, wild)) fail = $"container {m} kg flies {c} > its {goods} kg goods loose";
            }
            Row("L1_CONTAINER_THROW", new[] { "closed_container_holds", "inv_container_shove", "inv_kernel" }, "sweep", fail == null ? "PASS" : "FAIL", n, fail ?? $"limit {lim}: over limit jolts (0), 2x2 jolts, never past the cap, never farther than its goods loose");
            bool jolt = true; for (int t = -2; t < 40; t++) { RM_KnockbackMath.JoltOffset(t, 30, 0.2f, 1f, 1f, out float ox, out float oz); float a = (float)Math.Sqrt(ox * ox + oz * oz); if (a > 0.2f + 1e-5f || ((t < 0 || t >= 30) && a != 0f)) jolt = false; }
            Row("L1_JOLT_BOUNDED", new[] { "closed_container_holds", "inv_container_shove", "inv_kernel" }, "fixed", jolt ? "PASS" : "FAIL", 42, "jolt offset never above its amplitude, 0 before and after");
        }

        // ── explosion ledger: one throw request per (explosion, thing), memory lives >= window ──
        {
            var led = new KbExplosionLedger(600); bool ok = led.TryAdd(1, 7, 0) && !led.TryAdd(1, 7, 599) && !led.TryAdd(1, 7, 1199) && led.TryAdd(1, 8, 10) && led.TryAdd(2, 7, 10);
            var led2 = new KbExplosionLedger(600); var rnd = new Random(5); int n = 0;
            for (int i = 0; i < 20000 && ok; i++) { n++; int t0 = rnd.Next(0, 100000); int id = rnd.Next(); led2.TryAdd(id, 1, t0); int dt = rnd.Next(0, 600); if (led2.TryAdd(id, 1, t0 + dt)) { ok = false; } }
            Row("L1_ONE_REQUEST_PER_EXPLOSION_THING", new[] { "every_good_moves", "inv_perf_all_fly", "inv_kernel" }, "random", ok ? "PASS" : "FAIL", n + 5, "seed 5; a repeat callback inside the window never enqueues twice");
            var cand = new List<KbCandidate>(); for (int i = 0; i < 100; i++) cand.Add(new KbCandidate { index = i, kind = (KbKind)(i % 3), distance = i % 7 });
            Row("L1_NO_CAP_KEEPS_ALL", new[] { "every_good_moves", "inv_perf_all_fly", "inv_kernel" }, "fixed", RM_KnockbackMath.Prioritise(cand, -1).Count == 100 ? "PASS" : "FAIL", 1, "Prioritise with no cap keeps every candidate");
        }

        // ── frame stats ──
        {
            var ms = Enumerable.Repeat(16.6f, 600).ToArray(); ms[300] = 100f; var pz = new bool[600]; var air = new int[600];
            var g = KbFrameStats.Summarize(ms, pz, air, 600, ms.Sum() / 1000f, 0.9f, 8.25f);
            bool ok = g.worstMs == 100f && KbFrameStats.SelfCheck(g, 100f, out _) && g.windowP99Ms == 16.6f && KbFrameStats.WithinBudget(g, 50f, out _);
            var ms2 = Enumerable.Repeat(16.6f, 600).ToArray(); for (int i = 100; i < 120; i++) ms2[i] = 80f;
            var g2 = KbFrameStats.Summarize(ms2, pz, air, 600, ms2.Sum() / 1000f, 0.9f, 8.25f);
            ok &= !KbFrameStats.WithinBudget(g2, 50f, out _);
            var g3 = KbFrameStats.Summarize(ms.Take(100).ToArray(), new bool[100], new int[100], 100, 1.66f + 0.0834f, 0.9f, 8.25f);
            ok &= !KbFrameStats.WithinBudget(g3, 50f, out _);   // stopped before the window closed
            ok &= KbFrameStats.Percentile(new List<float> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }, 99f) == 10f && KbFrameStats.Percentile(new List<float>(), 99f) == 0f;
            Row("L1_FRAME_PROBE_P99", new[] { "barrage_frame_budget", "frame_time_probe", "inv_perf_all_fly", "inv_kernel" }, "fixed", ok ? "PASS" : "FAIL", 6, "one 100 ms stall is the worst row and not judged; 20 slow frames in the window fail 50 ms; a probe stopped early fails; nearest rank");
        }

        // ── shipped settings swept through their slider ranges, every switch off included ──
        {
            int n = 0; string fail = null;
            float[] strengths = { 0f, 0.5f, 1f, 2f, 3f }; int[] maxes = { 1, 3, 6, 10 }; float[] ipc = { 0f, 4f, 15f }; float[] scales = { 0.25f, 1f, 2f };
            foreach (var st in strengths) foreach (var mx in maxes) foreach (var ip in ipc) foreach (var sc in scales)
            foreach (bool impOn in new[] { true, false }) foreach (bool sb in new[] { true, false }) foreach (bool pits in new[] { true, false })
            {
                var ss = new KbSettings { globalMultiplier = st, maxCells = RM_KnockbackMath.CapFor(0, mx, sc), impactEnabled = impOn, impactPerCell = ip, sandbagsStop = sb, intoPits = pits, creatureMassLimit = 150f, lightMassLimit = 75f };
                for (float d = 0; d < 3f; d += 0.5f)
                {
                    n++;
                    int c = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, 70f, ss);
                    if (st == 0f && c != 0) fail = "strength 0 throws";
                    if (c > mx) fail = $"max {mx} exceeded: {c}";
                    var r = RM_KnockbackMath.Resolve(new Grid().Set(11, 10, KbCell.Partial).Set(12, 10, KbCell.Wall), 10, 10, 1f, 0f, c, KbKind.Pawn, 70f, ss);
                    if ((!impOn || ip == 0f) && (r.impact != 0f || r.otherImpact != 0f)) fail = "impact with impact off / 0 per cell";
                    if (r.impact < 0) fail = "negative impact";
                    if (fail != null) { fail += $" | strength {st} max {mx} ipc {ip} scale {sc} imp {impOn} sb {sb} pits {pits} d {d}"; break; }
                }
                if (fail != null) break;
            }
            // strength scales: ratio of strength 2 to 1 on a far-from-cap case
            var s2 = Shipped(); s2.globalMultiplier = 2f; s2.maxCells = 10;
            var s1 = Shipped(); s1.maxCells = 10;
            int c1 = RM_KnockbackMath.ThrowCells(1.5f, MortarR, 1f, 70f, s1), c2 = RM_KnockbackMath.ThrowCells(1.5f, MortarR, 1f, 70f, s2);
            if (fail == null && !(c2 > c1)) fail = $"strength 2 does not scale: {c1} -> {c2}";
            // every other-mod percent 0..100: unpatched harmful force = pct/100
            for (int pct = 0; pct <= 100 && fail == null; pct += 5) { n++; var c = KbLookup.Resolve(null, null, null, true, pct / 100f); if (Math.Abs(c.force - pct / 100f) > 1e-6f) fail = "unpatched pct " + pct; }
            // blast power ref percent 25..400
            for (int rp = 25; rp <= 400 && fail == null; rp += 25) { n++; if (Math.Abs(RM_KnockbackMath.DamageRatio(50f * rp / 100f, 50f, rp, true) - 1f) > 1e-5f) fail = "ref pct " + rp; }
            // creature mass limit 20..500 and goods limit 5..200: the limit is "heavier than"
            for (float lim = 20; lim <= 500 && fail == null; lim += 10) { n++; var ss = Shipped(); ss.creatureMassLimit = lim; if (!RM_KnockbackMath.Eligible(KbKind.Pawn, lim, ss) || RM_KnockbackMath.Eligible(KbKind.Pawn, lim + 0.5f, ss)) fail = "creature lim " + lim; }
            for (float lim = 5; lim <= 200 && fail == null; lim += 5) { n++; var ss = Shipped(); ss.lightMassLimit = lim; if (!RM_KnockbackMath.Eligible(KbKind.Item, lim, ss) || RM_KnockbackMath.Eligible(KbKind.Item, lim + 0.5f, ss)) fail = "goods lim " + lim; }
            Row("L1_SETTINGS_SWEEP_KERNEL_LINES", new[] { "settings_scale_and_switch", "inv_settings", "inv_caps", "inv_kernel" }, "sweep", fail == null ? "PASS" : "FAIL", n, fail ?? $"strength 0..3, max 1..10, cap scale .25..2, impact on/off and 0..15 per cell, sandbags stop on/off, pits on/off, other-mod 0..100%, ref 25..400%, creature 20..500, goods 5..200: every kernel line does what it says; strength 2 scales {c1}->{c2}");
        }

        return anyFail ? 1 : 0;
    }
}
