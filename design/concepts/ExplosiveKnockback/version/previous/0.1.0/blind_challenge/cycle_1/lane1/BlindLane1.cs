// Blind lane 1 (game logic) for Explosive Knockback 0.1.0, cycle 1 of the Stages 4 and 5 challenge.
// Written from the locked bars (sheet.md, tree.json, plan.md), the shipped kernel RM_KnockbackMath.cs and the shipped
// settings (RM_KnockbackMod.cs defaults and slider ranges, Patches/RM_Knockback_DamageDefs.xml forces) ONLY: the
// builder's selftests were not read before this file was written and run. Each row names the bar it decides.
// Output: one JSON line per row on stdout (id, bar, kind, verdict, cases, detail); exit 1 if any row FAILs.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

static class BlindLane1
{
    // ---- shipped settings, copied from RM_KnockbackMod.cs (defaults, slider ranges) and the def patch -----------------
    const float Strength = 1f; const int MaxCells = 6; const float OwnCapScale = 1f; const float UnpatchedPct = 100f;
    const float CreatureLimit = 150f; const float RefPct = 100f; const float GoodsLimit = 75f;
    const float ReboundKeep = 70f; const float ContainerLimit = 250f; const float HeavyMin = 10f;
    const float HeavyDmgMin = 2f, HeavyDmgMax = 5f; const int StaggerTicks = 30; const int RecoveryTicks = 120;
    const int StunMax = 120; const float ShieldDebit = 10f; const float ImpactPerCell = 4f;
    const float BombForce = 1f, FlameForce = 0.5f; // Patches/RM_Knockback_DamageDefs.xml
    const float BombDefault = 50f, FlameDefault = 10f; // sheet.md delegated: "Bomb 50, Flame 10"
    const float MortarRadius = 2.9f; // tree.json / kernel calibration comment
    // masses (kg). Colonist 70 = the kernel's refMass (a clothed, armed human); muffalo 144 and thrumbo over 150 from
    // sheet.md delegated ("a muffalo at 144 flies and a rhino at 180 does not"); rat 12 = 60 kg x body size 0.2 (an
    // assumption, not measured: any rat under 17.5 kg gives the same cells).
    const float Rat = 12f, Colonist = 70f, Muffalo = 144f, Rhino = 180f, Thrumbo = 240f;

    static readonly List<string> Out = new List<string>();
    static int fails;

    static KbSettings Shipped()
    {
        return new KbSettings
        {
            globalMultiplier = Strength, maxCells = MaxCells, creatureMassLimit = CreatureLimit, lightMassLimit = GoodsLimit,
            impactEnabled = true, impactPerCell = ImpactPerCell, sandbagsStop = false, intoPits = true,
        };
    }

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string bar, string kind, bool pass, int cases, string detail)
    {
        if (!pass) fails++;
        Out.Add("{\"id\":" + J(id) + ",\"bar\":" + J(bar) + ",\"kind\":" + J(kind) + ",\"verdict\":" + J(pass ? "PASS" : "FAIL")
            + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static void Info(string id, string bar, int cases, string detail)
    {
        Out.Add("{\"id\":" + J(id) + ",\"bar\":" + J(bar) + ",\"kind\":\"info\",\"verdict\":\"INFO\",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static void Unsettled(string id, string bar, string why)
    {
        Out.Add("{\"id\":" + J(id) + ",\"bar\":" + J(bar) + ",\"kind\":\"not_kernel\",\"verdict\":\"UNSETTLED\",\"cases\":0,\"detail\":" + J(why) + "}");
    }

    // ---- a test grid --------------------------------------------------------------------------------------------------
    sealed class Grid : IKbGrid
    {
        public readonly int W, H; public readonly KbCell[,] c;
        public Grid(int w, int h) { W = w; H = h; c = new KbCell[w, h]; }
        public KbCell At(int x, int z) => x < 0 || z < 0 || x >= W || z >= H ? KbCell.OutOfBounds : c[x, z];
        public Grid Clone() { var g = new Grid(W, H); Array.Copy(c, g.c, c.Length); return g; }
        public string Dump() { var sb = new StringBuilder(); for (int z = H - 1; z >= 0; z--) { for (int x = 0; x < W; x++) sb.Append((int)c[x, z]); sb.Append('/'); } return sb.ToString(); }
    }

    static int ThrowWith(float dist, float radius, float typeForce, float damage, float refDamage, float mass, KbSettings s, bool power = true, float refPct = RefPct)
    {
        float ratio = RM_KnockbackMath.DamageRatio(damage, refDamage, refPct, power);
        return RM_KnockbackMath.ThrowCells(dist, radius, typeForce * ratio, mass, s);
    }

    // ---- the random-case engine with shrinking -------------------------------------------------------------------------
    sealed class Case
    {
        public Grid g; public int sx, sz; public float dx, dz; public int cells; public KbKind kind; public float mass; public KbSettings s;
        public Case Copy() => new Case { g = g.Clone(), sx = sx, sz = sz, dx = dx, dz = dz, cells = cells, kind = kind, mass = mass, s = s };
        public override string ToString() => $"grid {g.W}x{g.H} {g.Dump()} start ({sx},{sz}) dir ({dx:0.###},{dz:0.###}) cells {cells} kind {kind} mass {mass} sandbagsStop {s.sandbagsStop} intoPits {s.intoPits} impact {s.impactEnabled}/{s.impactPerCell}/{s.impactFactor}";
    }

    static Case RandomCase(Random r)
    {
        int w = r.Next(3, 16), h = r.Next(3, 16);
        var g = new Grid(w, h);
        double pFill = r.NextDouble() * 0.5;
        for (int x = 0; x < w; x++) for (int z = 0; z < h; z++)
                g.c[x, z] = r.NextDouble() < pFill ? (KbCell)r.Next(0, 8) : KbCell.Open;
        int sx = r.Next(w), sz = r.Next(h);
        g.c[sx, sz] = KbCell.Open;
        double a = r.NextDouble() * 2 * Math.PI;
        var s = Shipped();
        s.sandbagsStop = r.Next(4) == 0; s.intoPits = r.Next(4) != 0; s.impactEnabled = r.Next(5) != 0;
        s.impactPerCell = (float)(r.NextDouble() * 15); s.impactFactor = r.Next(5) == 0 ? 0f : (float)(r.NextDouble() * 2);
        return new Case { g = g, sx = sx, sz = sz, dx = (float)Math.Cos(a), dz = (float)Math.Sin(a), cells = r.Next(0, 11), kind = (KbKind)r.Next(0, 3), mass = (float)(1 + r.NextDouble() * 150), s = s };
    }

    // shrink: fewer cells, open cells, smaller grid edge reached by trimming, axis-aligned direction, round mass
    static Case Shrink(Case c, Func<Case, string> fails)
    {
        bool progress = true;
        while (progress)
        {
            progress = false;
            var tries = new List<Case>();
            if (c.cells > 1) { var t = c.Copy(); t.cells--; tries.Add(t); }
            for (int x = 0; x < c.g.W; x++) for (int z = 0; z < c.g.H; z++)
                    if (c.g.c[x, z] != KbCell.Open) { var t = c.Copy(); t.g.c[x, z] = KbCell.Open; tries.Add(t); }
            if (Math.Abs(c.mass - 70f) > 0.5f) { var t = c.Copy(); t.mass = 70f; tries.Add(t); }
            foreach (var t in tries)
            {
                if (fails(t) != null) { c = t; progress = true; break; }
            }
        }
        return c;
    }

    static void Property(string id, string bar, int n, int seed, Func<Case, string> check)
    {
        var r = new Random(seed);
        for (int i = 0; i < n; i++)
        {
            var c = RandomCase(r);
            string why = check(c);
            if (why != null)
            {
                var small = Shrink(c, check);
                Row(id, bar, "random", false, i + 1, $"seed {seed} case {i}: {why}; shrunk to: {small} -> {check(small)}");
                return;
            }
        }
        Row(id, bar, "random", true, n, $"seed {seed}, {n} random grids");
    }

    static bool Solid(KbCell k) => k == KbCell.Wall || k == KbCell.Door || k == KbCell.OutOfBounds;

    static string PathInvariants(Case c)
    {
        var path = RM_KnockbackMath.Line(c.sx, c.sz, c.dx, c.dz, c.cells);
        if (c.cells > 0 && path.Count != c.cells) return $"path has {path.Count} steps, asked {c.cells}";
        int px = c.sx, pz = c.sz;
        foreach (var (x, z) in path)
        {
            if (Math.Max(Math.Abs(x - px), Math.Abs(z - pz)) != 1) return $"step ({px},{pz})->({x},{z}) is not one grid step";
            if ((x - c.sx) * c.dx + (z - c.sz) * c.dz <= 0) return $"cell ({x},{z}) is not away from the blast";
            px = x; pz = z;
        }
        return null;
    }

    static string ResolveInvariants(Case c)
    {
        var r = RM_KnockbackMath.Resolve(c.g, c.sx, c.sz, c.dx, c.dz, c.cells, c.kind, c.mass, c.s);
        var path = RM_KnockbackMath.Line(c.sx, c.sz, c.dx, c.dz, c.cells);
        if (r.cellsTravelled < 0 || r.cellsTravelled > c.cells) return $"travelled {r.cellsTravelled} of {c.cells}";
        // conservation: the thing is at exactly one cell, the start or a cell of its own path
        if (r.cellsTravelled == 0 && (r.destX != c.sx || r.destZ != c.sz)) return "moved 0 cells but dest != start";
        if (r.cellsTravelled > 0 && (path[r.cellsTravelled - 1].x != r.destX || path[r.cellsTravelled - 1].z != r.destZ)) return $"dest ({r.destX},{r.destZ}) is not path step {r.cellsTravelled}";
        if (r.cellsTravelled > 0)
        {
            var k = c.g.At(r.destX, r.destZ);
            if (k == KbCell.Wall || k == KbCell.Door || k == KbCell.Water || k == KbCell.OutOfBounds || k == KbCell.Partial) return $"rests on a {k} cell";
            if (k == KbCell.Pawn && c.kind == KbKind.Pawn) return "a thrown pawn rests on another pawn's cell";
            if (k == KbCell.Pit && !c.s.intoPits) return "rests in an open pit with throw-into-pits off";
        }
        // nothing is thrown across an open pit (thrown_into_pit_falls)
        for (int i = 0; i < r.cellsTravelled - 1; i++)
            if (c.g.At(path[i].x, path[i].z) == KbCell.Pit) return $"crossed the open pit at step {i + 1}";
        if (r.cellsTravelled > 0 && c.g.At(r.destX, r.destZ) == KbCell.Pit && r.stop != KbStop.Pit) return "in a pit but stop != Pit";
        // no wall corner is cut, on the cells actually travelled
        int px = c.sx, pz = c.sz;
        for (int i = 0; i < r.cellsTravelled; i++)
        {
            var (x, z) = path[i];
            if (x != px && z != pz && (Solid(c.g.At(x, pz)) || Solid(c.g.At(px, z)))) return $"cut the corner into ({x},{z})";
            px = x; pz = z;
        }
        // sandbags never stop a throw with the shipped setting (people_thrown_three_cells)
        if (!c.s.sandbagsStop && r.stop == KbStop.PartialCover) return "stopped by sandbags with sandbagsStop off";
        // wall_stops_dead / pawn_hits_pawn_stops / doors: a pawn that stopped short on a solid or a pawn takes impact
        bool shortStop = r.stop == KbStop.Wall || r.stop == KbStop.Door || r.stop == KbStop.Pawn || r.stop == KbStop.PartialCover || r.stop == KbStop.OutOfBounds;
        if (c.kind == KbKind.Pawn && (r.stop == KbStop.Wall || r.stop == KbStop.Door || r.stop == KbStop.Pawn) && c.s.impactEnabled && c.s.impactPerCell > 0.01f && c.s.impactFactor > 0.01f && r.cellsTravelled < c.cells && !(r.impact > 0f)) return $"stopped by {r.stop} with {c.cells - r.cellsTravelled} cells left and no impact";
        if (c.kind != KbKind.Pawn && (r.impact != 0f || r.otherImpact != 0f)) return "goods carry pawn impact";
        if (c.s.impactFactor == 0f && (r.impact != 0f || r.otherImpact != 0f)) return "impact factor 0 but impact > 0";
        if (r.stop == KbStop.Pawn && Math.Abs(r.impact - r.otherImpact) > 1e-5f) return "pawn-on-pawn impact not split evenly";
        if (r.stop == KbStop.Pawn && c.kind != KbKind.Pawn) return "goods stopped by a pawn in Resolve";
        // deep water: stops on the last standable cell, the next path cell is the water
        if (r.stop == KbStop.Water && c.g.At(path[r.cellsTravelled].x, path[r.cellsTravelled].z) != KbCell.Water)
        {
            // the sandbag pull-back may have moved it further back; the water must still be the first blocked step after it
            bool waterAhead = false; for (int i = r.cellsTravelled; i < path.Count; i++) { var k = c.g.At(path[i].x, path[i].z); if (k == KbCell.Water) { waterAhead = true; break; } if (k != KbCell.Partial) break; }
            if (!waterAhead) return "stop Water but no water ahead";
        }
        // determinism
        var r2 = RM_KnockbackMath.Resolve(c.g, c.sx, c.sz, c.dx, c.dz, c.cells, c.kind, c.mass, c.s);
        if (r2.destX != r.destX || r2.destZ != r.destZ || r2.stop != r.stop) return "not deterministic";
        _ = shortStop;
        return null;
    }

    static string ReflectInvariant(Case c)
    {
        var r = RM_KnockbackMath.Resolve(c.g, c.sx, c.sz, c.dx, c.dz, c.cells, KbKind.Item, c.mass, c.s);
        if (!r.hasBlock) return null;
        if (!RM_KnockbackMath.Reflect(c.g, r, c.dx, c.dz, out float rx, out float rz)) return "hasBlock but Reflect false";
        if (Math.Abs(rx * rx + rz * rz - (c.dx * c.dx + c.dz * c.dz)) > 1e-4f) return "reflection changed the speed";
        // the rebound's first step from the hit cell never re-enters the cell it broke on
        var p = RM_KnockbackMath.Line(r.blockFromX, r.blockFromZ, rx, rz, 1);
        if (p.Count == 1 && p[0].x == r.blockX && p[0].z == r.blockZ) return $"rebound re-enters the block ({r.blockX},{r.blockZ})";
        return null;
    }

    static void Main()
    {
        var S = Shipped();

        // ===================== people_thrown_three_cells =====================
        {
            int c70 = ThrowWith(1f, MortarRadius, BombForce, BombDefault, BombDefault, Colonist, S);
            bool ok = c70 == 3; string det = $"mortar r 2.9, distance 1, 70 kg -> {c70} cells";
            foreach (float m in new[] { 60f, 65f, 75f }) { int k = ThrowWith(1f, MortarRadius, BombForce, BombDefault, BombDefault, m, S); det += $"; {m} kg -> {k}"; ok &= k == 3; }
            Row("L1_calibration_mortar_three_cells", "people_thrown_three_cells", "fixed", ok, 4, det);
        }
        {
            // a colonist one cell east of the shell, sandbags two cells further east (and a barricade lane: both Partial)
            var g = new Grid(12, 3); g.c[3, 1] = KbCell.Partial;
            var r = RM_KnockbackMath.Resolve(g, 1, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var g2 = new Grid(12, 3); var r2 = RM_KnockbackMath.Resolve(g2, 1, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var s3 = Shipped(); s3.sandbagsStop = true; var r3 = RM_KnockbackMath.Resolve(g, 1, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, s3);
            bool ok = r.destX == 4 && r.stop == KbStop.Distance && r.impact == 0f && r2.destX == r.destX && r3.destX < 3;
            Row("L1_over_sandbags_same_cell_as_no_line", "people_thrown_three_cells", "fixed", ok, 3, $"line lands x={r.destX} stop {r.stop}; no line x={r2.destX}; sandbagsStop on x={r3.destX} stop {r3.stop}");
        }
        {
            // landing exactly on a sandbag cell: pulled back to the last free cell, never left on the bag
            var g = new Grid(12, 3); g.c[4, 1] = KbCell.Partial;
            var r = RM_KnockbackMath.Resolve(g, 1, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            Row("L1_never_rests_on_sandbags", "people_thrown_three_cells", "fixed", r.destX == 3 && g.At(r.destX, 1) == KbCell.Open, 1, $"bag at the landing cell x=4 -> lands x={r.destX}");
        }

        // ===================== heavier_flies_less =====================
        {
            int rat = ThrowWith(1f, MortarRadius, BombForce, 50, 50, Rat, S), col = ThrowWith(1f, MortarRadius, BombForce, 50, 50, Colonist, S),
                muf = ThrowWith(1f, MortarRadius, BombForce, 50, 50, Muffalo, S);
            bool thrEl = RM_KnockbackMath.Eligible(KbKind.Pawn, Thrumbo, S);
            int rat2 = ThrowWith(1f, MortarRadius, BombForce, 100, 50, Rat, S), col2 = ThrowWith(1f, MortarRadius, BombForce, 100, 50, Colonist, S),
                muf2 = ThrowWith(1f, MortarRadius, BombForce, 100, 50, Muffalo, S);
            bool ok = rat == 5 && col == 3 && muf == 2 && !thrEl && rat2 == 6 && col2 == 5 && muf2 == 4;
            Row("L1_mass_and_power_cells_match_oracle", "heavier_flies_less", "fixed", ok, 8, $"ref damage rat {rat} colonist {col} muffalo {muf} thrumbo eligible {thrEl}; 2x rat {rat2} colonist {col2} muffalo {muf2} (oracle 5/3/2/0 then 6/5/4/0)");
            int off1 = ThrowWith(1f, MortarRadius, BombForce, 100, 50, Colonist, S, power: false);
            var s250 = Shipped(); s250.creatureMassLimit = 250f;
            int th1 = RM_KnockbackMath.Eligible(KbKind.Pawn, Thrumbo, s250) ? ThrowWith(1f, MortarRadius, BombForce, 50, 50, Thrumbo, s250) : -1;
            int th2 = RM_KnockbackMath.Eligible(KbKind.Pawn, Thrumbo, s250) ? ThrowWith(1f, MortarRadius, BombForce, 100, 50, Thrumbo, s250) : -1;
            Row("L1_mass_and_power_controls", "heavier_flies_less", "fixed", off1 == 3 && th1 == 1 && th2 == 3, 3, $"power off at 2x colonist {off1} (want 3); limit 250 thrumbo {th1} then {th2} (want 1 then 3)");
        }
        {
            // random: heavier never flies farther; more damage never flies less; farther from the blast never flies farther
            var r = new Random(41); string bad = null; int n = 20000;
            for (int i = 0; i < n && bad == null; i++)
            {
                float rad = (float)(0.5 + r.NextDouble() * 8), d = (float)(r.NextDouble() * rad), m1 = (float)(1 + r.NextDouble() * 200), m2 = m1 + (float)(r.NextDouble() * 100);
                float dmg = (float)(r.NextDouble() * 200), f = (float)(r.NextDouble() * 2); float d2 = d + (float)(r.NextDouble() * 2);
                int a = ThrowWith(d, rad, f, dmg, 50, m1, S), b = ThrowWith(d, rad, f, dmg, 50, m2, S), c2 = ThrowWith(d, rad, f, dmg * 2, 50, m1, S), e = ThrowWith(d2, rad, f, dmg, 50, m1, S);
                if (b > a) bad = $"mass {m1}->{a} but heavier {m2}->{b} (r {rad} d {d} f {f} dmg {dmg})";
                else if (c2 < a) bad = $"damage {dmg}->{a} but 2x->{c2}";
                else if (e > a) bad = $"distance {d}->{a} but farther {d2}->{e}";
                else if (a < 0 || a > MaxCells) bad = $"throw {a} outside 0..{MaxCells}";
            }
            Row("L1_monotone_mass_damage_distance", "heavier_flies_less", "random", bad == null, n, bad ?? "seed 41: heavier <= lighter, 2x damage >= 1x, farther <= nearer, 0 <= cells <= max");
        }
        {
            // "at twice the damage each goes farther": strictly farther unless capped. Cycle-1 note: the first version of
            // this row demanded it for every throw and failed on rim throws (1x raw 0.5..0.75 and 2x both round to 1 cell),
            // which integer cells make unavoidable; the bar's own examples are all 2+ cells. Strict from 2 cells; the rim
            // case is recorded as INFO.
            var r = new Random(43); string bad = null; int n = 20000, capped = 0, rimSame = 0; string rimEx = null;
            for (int i = 0; i < n && bad == null; i++)
            {
                float rad = (float)(1 + r.NextDouble() * 6), d = (float)(r.NextDouble() * rad * 0.9), m = (float)(1 + r.NextDouble() * 149);
                int a = ThrowWith(d, rad, 1f, 50, 50, m, S), b = ThrowWith(d, rad, 1f, 100, 50, m, S);
                if (a == 0) continue; if (a == MaxCells) { capped++; continue; }
                if (a == 1) { if (b == 1) { rimSame++; rimEx ??= $"mass {m:0.#} d {d:0.##} r {rad:0.##}"; } continue; }
                if (b <= a) bad = $"mass {m} d {d} r {rad}: 1x {a} cells, 2x {b} cells";
            }
            Row("L1_twice_damage_strictly_farther_below_cap", "heavier_flies_less", "random", bad == null, n, bad ?? $"seed 43: every uncapped throw of 2+ cells goes strictly farther at 2x; {capped} capped cases skipped");
            Info("L1_twice_damage_rim_one_cell", "heavier_flies_less", rimSame, $"{rimSame} one-cell rim throws stay one cell at 2x damage (e.g. {rimEx}); integer cells, not a defect");
        }

        // ===================== the_spared (kernel part) =====================
        {
            bool ok = RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, S) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 150.01f, S)
                && RM_KnockbackMath.Eligible(KbKind.Pawn, Muffalo, S) && !RM_KnockbackMath.Eligible(KbKind.Pawn, Rhino, S)
                && RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, S) // a living pawn is never weighed by the 75 kg goods limit
                && RM_KnockbackMath.Eligible(KbKind.Item, 75f, S) && !RM_KnockbackMath.Eligible(KbKind.Item, 75.01f, S)
                && !RM_KnockbackMath.Eligible(KbKind.Corpse, 80f, S);
            var s20 = Shipped(); s20.creatureMassLimit = 20f; ok &= RM_KnockbackMath.Eligible(KbKind.Corpse, 65f, s20); // the creature limit never weighs a corpse
            var sG = Shipped(); sG.lightMassLimit = 300f; ok &= RM_KnockbackMath.Eligible(KbKind.Corpse, Thrumbo, sG); // no body-size rule spares a thrumbo corpse
            var grav = KbLookup.Apply(S, new KbConfig { massLimitOverride = 216f }, MaxCells, OwnCapScale);
            ok &= RM_KnockbackMath.Eligible(KbKind.Pawn, Rhino, grav) && !RM_KnockbackMath.Eligible(KbKind.Pawn, Thrumbo, grav) && S.creatureMassLimit == 150f;
            Row("L1_mass_limits_who_is_spared", "the_spared", "fixed", ok, 12, "150 kg flies, over 150 spared; muffalo flies, rhino spared; 100 kg pawn flies; goods 75 flies, 75.01 spared; 80 kg corpse spared; 65 kg corpse thrown under a 20 kg creature limit; thrumbo corpse thrown with goods limit 300; grav-ram 216 throws a rhino, spares a thrumbo, global untouched");
        }
        {
            var r = new Random(47); string bad = null; int n = 20000;
            for (int i = 0; i < n && bad == null; i++)
            {
                float rad = (float)(0.5 + r.NextDouble() * 8), d = (float)(r.NextDouble() * rad * 1.2), m = (float)(r.NextDouble() * 200), f = (float)(r.NextDouble() * 3);
                int a = RM_KnockbackMath.ThrowCells(d, rad, f, m, S);
                if (a != 0 && a < 1) bad = "a throw under one cell that is not 0";
                if (d >= rad && a != 0) bad = $"thrown {a} from at or beyond the radius (d {d} r {rad})";
            }
            Row("L1_rim_under_one_cell_is_no_move", "the_spared", "random", bad == null, n, bad ?? "seed 47: every throw is 0 or >= 1 cell; nothing at or beyond the radius moves");
        }

        // ===================== recovery_immunity =====================
        {
            var r = new Random(53); string bad = null; int n = 20000;
            for (int i = 0; i < n && bad == null; i++)
            {
                int landed = r.Next(0, 100000), stun = landed + r.Next(0, StunMax + 1), now = landed + r.Next(-10, 1000), w = r.Next(0, 601);
                bool can = KbImmunity.CanLaunch(now, landed, stun, w);
                bool want = w <= 0 || now >= Math.Max(landed, stun) + w;
                if (can != want) bad = $"now {now} landed {landed} stun {stun} window {w}: {can}";
                if (w > 0 && now < stun && can) bad = "launched while still stunned";
                if (can && !KbImmunity.CanLaunch(now + 1, landed, stun, w)) bad = "immunity came back later";
            }
            bool fix = !KbImmunity.CanLaunch(1000 + StunMax + RecoveryTicks - 1, 1000, 1000 + StunMax, RecoveryTicks) && KbImmunity.CanLaunch(1000 + StunMax + RecoveryTicks, 1000, 1000 + StunMax, RecoveryTicks);
            Row("L1_recovery_window", "recovery_immunity", "random", bad == null && fix, n + 2, bad ?? "seed 53: no second launch before stun end + window, always after; shipped 120-tick window boundary exact");
        }

        // ===================== wall_stops_dead / pawn_hits_pawn_stops / doors_and_deep_water_stop =====================
        {
            var g = new Grid(10, 3); g.c[3, 1] = KbCell.Wall;
            var r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var r0 = RM_KnockbackMath.Resolve(new Grid(10, 3), 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var gp = new Grid(10, 3); gp.c[3, 1] = KbCell.Pawn; var rp = RM_KnockbackMath.Resolve(gp, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var gd = new Grid(10, 3); gd.c[2, 1] = KbCell.Door; var rd = RM_KnockbackMath.Resolve(gd, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var gw = new Grid(10, 3); gw.c[3, 1] = KbCell.Water; var rw = RM_KnockbackMath.Resolve(gw, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var s0 = KbLookup.Apply(S, new KbConfig { impactFactor = 0f }, MaxCells, OwnCapScale); var rd0 = RM_KnockbackMath.Resolve(gd, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, s0);
            bool ok = r.destX == 2 && r.stop == KbStop.Wall && r.impact > 0 && r0.destX == 3
                && rp.destX == 2 && rp.stop == KbStop.Pawn && rp.hitOther && rp.impact > 0 && rp.otherImpact > 0
                && rd.destX == 1 && rd.stop == KbStop.Door && rd.hitDoor && rd.impact > 0
                && rw.destX == 2 && rw.stop == KbStop.Water && rd0.impact == 0f && rd0.hitDoor;
            Row("L1_wall_pawn_door_water_stops", "wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop", "fixed", ok, 6,
                $"wall x={r.destX} {r.stop} impact {r.impact:0.##}; no wall x={r0.destX}; pawn x={rp.destX} {rp.stop} {rp.impact:0.##}/{rp.otherImpact:0.##}; door x={rd.destX} {rd.stop} {rd.impact:0.##}; water x={rw.destX} {rw.stop}; impact factor 0 at the door {rd0.impact}");
        }
        Property("L1_resolve_invariants_random_grids", "wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop,thrown_into_pit_falls,people_thrown_three_cells", 50000, 59, c => PathInvariants(c) ?? ResolveInvariants(c));

        // ===================== thrown_into_pit_falls (kernel part) =====================
        {
            var g = new Grid(10, 3); g.c[2, 1] = KbCell.Pit; g.c[3, 1] = KbCell.Pit;
            var rp = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var ri = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Item, 5f, S);
            var gc = new Grid(10, 3); gc.c[3, 1] = KbCell.CoveredPit; var rc = RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, S);
            var sOff = Shipped(); sOff.intoPits = false; var ro = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, Colonist, sOff);
            bool ok = rp.destX == 2 && rp.stop == KbStop.Pit && ri.destX == 2 && ri.stop == KbStop.Pit && rc.destX == 3 && gc.At(rc.destX, 1) == KbCell.CoveredPit && ro.destX == 1;
            Row("L1_pit_first_cell_and_cover_landing", "thrown_into_pit_falls", "fixed", ok, 4, $"pawn into the first pit cell x={rp.destX} {rp.stop}; stack x={ri.destX} {ri.stop}; lands ON the covered cell x={rc.destX} (the fall and the broken cover are game side); pits off: stops before x={ro.destX}");
        }

        // ===================== shield_belt_holds =====================
        {
            var r = new Random(61); string bad = null; int n = 20000;
            for (int i = 0; i < n && bad == null; i++)
            {
                float e = (float)(r.NextDouble() * 2), f = (float)(r.NextDouble() * 3), per = (float)(r.NextDouble() * 50), loss = (float)(r.NextDouble() * 0.1);
                float after = KbShield.EnergyAfter(e, f, per, loss);
                if (after > e + 1e-6f) bad = "a throw gave the shield energy";
                if (f > 0.01f && per > 0.01f && loss > 0.0001f && !(after < e)) bad = "a positive force cost no extra charge";
            }
            float plain = 1f, extra = plain - KbShield.EnergyAfter(plain, 1f, ShieldDebit, 0.033f);
            Row("L1_shield_extra_charge", "shield_belt_holds", "random", bad == null && extra > 0f, n + 1, bad ?? $"seed 61: charge never grows, always drops on a real throw; mortar at shipped debit 10 costs {extra:0.###} extra at 0.033 loss/damage (an assumed loss rate)");
        }

        // ===================== goods_arc_spin_rebound =====================
        {
            bool ok = true; string det = "";
            for (int n0 = 1; n0 <= 10; n0++)
            {
                int n = n0, total = 0, hops = 0; var chain = new List<int>();
                while (n > 0 && hops < 100) { chain.Add(n); total += n; n = RM_KnockbackMath.ReboundCells(n, ReboundKeep); hops++; }
                if (hops >= 100) ok = false;
                if (total > n0 / (1 - ReboundKeep / 100f) + 1e-3) ok = false;
                if (n0 == 10) det = "10 cells at 70%: " + string.Join("->", chain) + "->0";
            }
            ok &= RM_KnockbackMath.ReboundCells(10, 70f) == 7 && RM_KnockbackMath.ReboundCells(1, 70f) == 0;
            Row("L1_rebound_keeps_70_and_runs_out", "goods_arc_spin_rebound", "fixed", ok, 10, det + "; every chain ends, total within n/(1-0.7)");
        }
        {
            // the shipped slider runs goodsReboundKeepPercent 0..100. Cycle-1 rescope (after lane 2 read the carrier): below 100
            // the kernel's rounding ends the chain; at exactly 100 the kernel keeps every cell and the carrier's MaxBounces
            // (RM_ThingFlyer_Knockback, read as text by the runner and passed in) ends it. The first version demanded the kernel
            // alone end it at 100 and failed; that FAIL is lane 1's record, kept in the cycle summary.
            string bad = null; int maxBounces = int.Parse(Environment.GetEnvironmentVariable("EK_MAX_BOUNCES") ?? "-1");
            for (float k = 0f; k <= 100f; k += 1f)
            {
                int n = 6, hops = 0, limit = k < 100f ? 1000 : maxBounces;
                while (n > 0 && hops < 1000 && (limit < 0 || hops < limit)) { n = RM_KnockbackMath.ReboundCells(n, k); hops++; }
                if (k < 100f && n > 0) { bad = $"keep {k}%: the kernel never ends a 6-cell chain"; break; }
                if (k >= 100f && !(maxBounces > 0 && maxBounces <= 20)) { bad = $"keep 100%: the kernel keeps every cell and the carrier bound is {maxBounces}"; break; }
            }
            Row("L1_sweep_rebound_keep_slider_chain_ends", "goods_arc_spin_rebound,settings_scale_and_switch", "sweep", bad == null, 101, bad ?? $"keep 0..99%: the kernel's rounding ends every chain; 100%: the carrier's MaxBounces {maxBounces} ends it");
        }
        Property("L1_reflect_never_reenters_block", "goods_arc_spin_rebound", 50000, 67, ReflectInvariant);
        {
            // goods fly about 1.6x as far as a person (sheet), the shape check 1.3..2.0x and farther than a person (tree advisory)
            var r = new Random(71); int n = 0, inBand = 0, notFarther = 0; string example = null;
            for (int i = 0; i < 20000; i++)
            {
                float rad = (float)(2 + r.NextDouble() * 5), d = (float)(r.NextDouble() * rad * 0.8), m = (float)(0.1 + r.NextDouble() * 74.9);
                int person = RM_KnockbackMath.ThrowCells(d, rad, 1f, Colonist, S); if (person < 1 || person >= MaxCells) continue;
                int good = RM_KnockbackMath.ThrowCells(d, rad, 1f, m, S); n++;
                double ratio = good / (double)person; if (ratio >= 1.3 && ratio <= 2.0) inBand++;
                if (good <= person) { notFarther++; if (example == null) example = $"a {m:0.#} kg good at d {d:0.##} r {rad:0.##} throws {good}, a colonist {person}"; }
            }
            int corpse = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, 60f, S), person3 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Colonist, S);
            Info("L1_kernel_alone_goods_vs_person_distance", "goods_arc_spin_rebound", n,
                $"not a verdict (the 1.6x may be applied game side; lane 2 checks) kernel alone: {inBand} of {n} goods/person ratios in 1.3..2.0, {notFarther} goods not farther than the person (e.g. {example}); a 60 kg corpse beside a mortar {corpse} vs a colonist {person3}");
        }

        // ===================== every_good_moves (kernel part) =====================
        {
            var r = new Random(73); string bad = null; int n = 2000;
            for (int i = 0; i < n && bad == null; i++)
            {
                var all = new List<KbCandidate>(); int k = r.Next(0, 300);
                for (int j = 0; j < k; j++) all.Add(new KbCandidate { index = j, kind = (KbKind)r.Next(0, 3), distance = (float)(r.NextDouble() * 6) });
                var kept = RM_KnockbackMath.Prioritise(all, -1);
                if (kept.Count != all.Count || kept.Select(x => x.index).Distinct().Count() != all.Count) bad = $"no cap: kept {kept.Count} of {all.Count}";
            }
            Row("L1_no_cap_keeps_every_candidate", "every_good_moves", "random", bad == null, n, bad ?? "seed 73: Prioritise with no cap returns every candidate exactly once (the game side must not pass a cap)");
        }
        {
            // each (explosion, thing) pair is queued exactly once while its explosion is live
            var r = new Random(79); string bad = null; int n = 3000;
            for (int i = 0; i < n && bad == null; i++)
            {
                var L = new KbExplosionLedger(); int t0 = r.Next(-5000, 100000), now = t0; var first = new Dictionary<(int, int), int>();
                for (int j = 0; j < 200 && bad == null; j++)
                {
                    now += r.Next(0, 40); int e = r.Next(0, 5), th = r.Next(0, 20);
                    bool added = L.TryAdd(e, th, now);
                    if (first.TryGetValue((e, th), out int at))
                    {
                        if (added && now - at < KbExplosionLedger.DefaultWindow) bad = $"pair ({e},{th}) queued twice {now - at} ticks apart";
                        if (added) first[(e, th)] = now;
                    }
                    else if (!added) bad = $"first sight of ({e},{th}) refused";
                    else first[(e, th)] = now;
                }
            }
            Row("L1_one_request_per_thing_per_explosion", "every_good_moves", "random", bad == null, n, bad ?? "seed 79: within 600 ticks of the first sight no pair is queued twice; a first sight is never refused");
        }

        // ===================== open_shelf_scatters / closed_container_holds =====================
        {
            bool ok = !RM_KnockbackMath.GoodsHeld(true, false, false) && RM_KnockbackMath.GoodsHeld(true, true, false) && !RM_KnockbackMath.GoodsHeld(false, false, false) && !RM_KnockbackMath.GoodsHeld(false, true, false);
            Row("L1_open_storage_protects_nothing", "open_shelf_scatters,closed_container_holds", "fixed", ok, 4, "open shelf: thrown; closed container: held; loose: thrown (shipped openStorageProtectsGoods false)");
        }
        {
            // (cycle 2: the dead slide kernel ContainerShove was deleted, steward's decision 7; the container throw the game calls)
            var cks = new KbSettings();
            bool ok = RM_KnockbackMath.ContainerThrowCells(true, ContainerLimit, ContainerLimit, 0f, 2.9f, 2f, cks) >= 1
                && RM_KnockbackMath.ContainerThrowCells(true, 251f, ContainerLimit, 0f, 2.9f, 2f, cks) == 0
                && RM_KnockbackMath.ContainerThrowCells(true, 100f, ContainerLimit, 0f, 2.9f, 1f, cks) >= 1
                && RM_KnockbackMath.ContainerThrowCells(false, 50f, ContainerLimit, 0f, 2.9f, 1f, cks) == 0;
            foreach (KbCell k in Enum.GetValues(typeof(KbCell))) ok &= RM_KnockbackMath.ShoveCellFree(k, false) == (k == KbCell.Open);
            ok &= !RM_KnockbackMath.ShoveCellFree(KbCell.Open, true);
            Row("L1_container_slide_or_jolt_at_250", "closed_container_holds", "fixed", ok, 14, "with the 250 kg container limit passed in (cycle 2: ContainerThrowCells): 250 and 100 kg thrown, 251 jolts, 2x2 jolts; only empty open ground is free (never pit, cover, wall, door, bags, water, edge, pawn). Which limit the game passes is lane 2's question");
        }

        // ===================== heavy_stack_knocks =====================
        {
            var r = new Random(83); string bad = null; int n = 20000;
            for (int i = 0; i < n && bad == null; i++)
            {
                float m = (float)(r.NextDouble() * 80), roll = (float)r.NextDouble();
                bool hit = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, m, HeavyMin, HeavyDmgMin, HeavyDmgMax, roll, StaggerTicks, out float dmg, out int stun);
                if (hit != (m >= HeavyMin)) bad = $"{m} kg: hit {hit}";
                if (hit && (dmg < HeavyDmgMin || dmg > HeavyDmgMax || stun != StaggerTicks)) bad = $"{m} kg: {dmg} blunt, {stun} ticks";
                if (!hit && (dmg != 0 || stun != 0)) bad = "a pass did damage";
            }
            bool corpse = RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 60f, HeavyMin, 2, 5, 0.5f, 30, out _, out _);
            bool off = RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 60f, HeavyMin, 2, 5, 0.5f, 30, out _, out _);
            bool inv = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 60f, HeavyMin, 8, 3, 0.9f, 30, out float d2, out _) && d2 == 8f;
            Row("L1_heavy_stack_knock", "heavy_stack_knocks", "random", bad == null && !corpse && !off && inv, n + 3, bad ?? $"seed 83: >= 10 kg hits 2..5 blunt, 30 ticks (~0.5 s); lighter passes; corpse passes; off passes; max<min gives min");
        }

        // ===================== every_harmful_blast_throws / only_explosions_throw / per_weapon_tuning =====================
        {
            var none = KbLookup.Resolve(null, null, null, true, UnpatchedPct / 100f);
            var harmless = KbLookup.Resolve(null, null, null, false, UnpatchedPct / 100f);
            var tuned = KbLookup.Resolve(null, null, new KbConfig { force = FlameForce }, true, 0.4f);
            bool ok = none.force == 1f && none.source == "unpatched" && harmless.force == 0f && tuned.force == FlameForce && tuned.source == "damageDef";
            Row("L1_unpatched_harmful_full_harmless_none_never_stacked", "every_harmful_blast_throws", "fixed", ok, 3, $"unpatched harmful {none.force} ({none.source}); harmless {harmless.force}; a tuned type ignores the other-mods percent: {tuned.force}");
        }
        {
            var r = new Random(89); int n = 0, sumF = 0, sumB = 0; string worst = null; double worstGap = 0;
            for (int i = 0; i < 20000; i++)
            {
                float rad = (float)(1 + r.NextDouble() * 8), d = (float)(r.NextDouble() * rad * 0.7), m = (float)(1 + r.NextDouble() * 149);
                int b = ThrowWith(d, rad, BombForce, BombDefault, BombDefault, m, S), f = ThrowWith(d, rad, FlameForce, FlameDefault, FlameDefault, m, S);
                if (b < 2 || b >= MaxCells) continue; n++; sumF += f; sumB += b;
                double gap = Math.Abs(f - b * 0.5); if (gap > worstGap) { worstGap = gap; worst = $"bomb {b} fire {f}"; }
            }
            double ratio = sumF / (double)sumB;
            Row("L1_fire_throws_half", "every_harmful_blast_throws", "random", ratio > 0.4 && ratio < 0.6 && worstGap <= 1.0, n, $"seed 89: fire/bomb total ratio {ratio:0.###} over {n} uncapped cases; worst single gap {worstGap} ({worst})");
        }
        {
            var p = new KbConfig { force = 0f }; var w = new KbConfig { force = 2f }; var dd = new KbConfig { force = 1f, ownCap = 2 };
            var a = KbLookup.Resolve(p, w, dd, true, 1f); var b = KbLookup.Resolve(null, w, dd, true, 1f); var c = KbLookup.Resolve(null, null, dd, true, 1f);
            bool ok = a.source == "projectile" && a.force == 0f && a.ownCap == 0 && b.source == "weapon" && b.force == 2f && b.ownCap == 0 && c.source == "damageDef";
            int zero = RM_KnockbackMath.ThrowCells(0f, 3f, a.force, Colonist, KbLookup.Apply(S, a, MaxCells, OwnCapScale));
            var own2 = KbLookup.Apply(S, new KbConfig { ownCap = 2 }, MaxCells, OwnCapScale); var own4 = KbLookup.Apply(S, new KbConfig { ownCap = 4 }, MaxCells, 0.5f); var own0 = KbLookup.Apply(S, new KbConfig { ownCap = 0 }, MaxCells, 0.5f);
            int t2 = RM_KnockbackMath.ThrowCells(0f, 5f, 3f, Colonist, own2), t4 = RM_KnockbackMath.ThrowCells(0f, 5f, 3f, Colonist, own4), t0 = RM_KnockbackMath.ThrowCells(0f, 5f, 3f, Colonist, own0);
            ok &= zero == 0 && t2 == 2 && t4 == 2 && t0 == MaxCells;
            Row("L1_lookup_order_whole_zero_wins_own_max", "per_weapon_tuning", "fixed", ok, 7, $"projectile 0 wins whole -> {zero} cells; weapon wins over type, no merge (ownCap {b.ownCap}); own max 2 -> {t2}; own 4 x 0.5 -> {t4}; own 0 under scale 0.5 -> {t0} (global {MaxCells})");
        }

        // ===================== blast power from damage =====================
        {
            bool ok = RM_KnockbackMath.DamageRatio(50, 50, 100, true) == 1f && RM_KnockbackMath.DamageRatio(100, 50, 100, true) == 2f
                && RM_KnockbackMath.DamageRatio(100, 50, 100, false) == 1f && RM_KnockbackMath.DamageRatio(50, 50, 200, true) == 0.5f
                && RM_KnockbackMath.DamageRatio(-5, 50, 100, true) == 0f && RM_KnockbackMath.DamageRatio(10, 0, 100, true) == 1f
                && RM_KnockbackMath.DamageRatio(10, 10, 100, true) == 1f;
            Row("L1_damage_ratio", "heavier_flies_less,settings_scale_and_switch", "fixed", ok, 7, "normal damage 1; twice 2; off 1; ref 200% halves; negative damage 0; no reference 1; Flame 10/10 = 1 so fire keeps its half");
        }

        // ===================== settings_scale_and_switch: shipped settings swept through their ranges =====================
        {
            string bad = null; int cases = 0; var r = new Random(97);
            for (float strength = 0f; strength <= 3.0001f && bad == null; strength += 0.25f)
                for (int max = 1; max <= 10 && bad == null; max++)
                    for (float scale = 0.25f; scale <= 2.0001f && bad == null; scale += 0.25f)
                        for (int t = 0; t < 30 && bad == null; t++)
                        {
                            var s = Shipped(); s.globalMultiplier = strength;
                            int own = r.Next(0, 8);
                            var k = KbLookup.Apply(s, new KbConfig { ownCap = own }, max, scale);
                            float rad = (float)(1 + r.NextDouble() * 8), d = (float)(r.NextDouble() * rad), m = (float)(1 + r.NextDouble() * 149), f = (float)(r.NextDouble() * 4);
                            int c = RM_KnockbackMath.ThrowCells(d, rad, f, m, k); cases++;
                            int cap = own > 0 ? Math.Max(1, (int)Math.Round(own * scale, MidpointRounding.AwayFromZero)) : max;
                            if (c > cap) bad = $"strength {strength} max {max} scale {scale} own {own}: {c} cells over cap {cap}";
                            if (strength == 0f && c != 0) bad = "strength 0 still throws";
                            var s2 = Shipped(); s2.globalMultiplier = strength + 0.25f; int c2 = RM_KnockbackMath.ThrowCells(d, rad, f, m, KbLookup.Apply(s2, new KbConfig { ownCap = own }, max, scale));
                            if (c2 < c) bad = $"more strength threw less ({c} -> {c2})";
                            if (own == 0 && k.maxCells != max) bad = "own 0 does not keep the global maximum";
                        }
            Row("L1_sweep_strength_max_capscale", "settings_scale_and_switch", "sweep", bad == null, cases, bad ?? "strength 0..3, maximum 1..10, cap scale 0.25..2 (shipped slider ranges) x 30 random blasts: never over its cap, strength 0 throws nothing, monotone in strength");
        }
        {
            string bad = null; int cases = 0;
            for (float lim = 20f; lim <= 500f && bad == null; lim += 10f)
            {
                var s = Shipped(); s.creatureMassLimit = lim;
                foreach (float m in new[] { 5f, 65f, 100f, 149f, 151f, 300f, 499f })
                {
                    cases++;
                    if (RM_KnockbackMath.Eligible(KbKind.Pawn, m, s) != (m <= lim)) bad = $"creature limit {lim}: pawn {m}";
                    if (RM_KnockbackMath.Eligible(KbKind.Corpse, m, s) != (m <= GoodsLimit)) bad = $"creature limit {lim} changed a corpse {m}";
                    if (RM_KnockbackMath.Eligible(KbKind.Item, m, s) != (m <= GoodsLimit)) bad = $"creature limit {lim} changed an item {m}";
                }
            }
            for (float lim = 5f; lim <= 200f && bad == null; lim += 5f)
            {
                var s = Shipped(); s.lightMassLimit = lim;
                foreach (float m in new[] { 5f, 65f, 100f, 149f, 151f })
                {
                    cases++;
                    if (RM_KnockbackMath.Eligible(KbKind.Item, m, s) != (m <= lim)) bad = $"goods limit {lim}: item {m}";
                    if (RM_KnockbackMath.Eligible(KbKind.Pawn, m, s) != (m <= CreatureLimit)) bad = $"goods limit {lim} changed a pawn {m}";
                }
            }
            Row("L1_sweep_mass_limits_change_only_their_own", "settings_scale_and_switch,the_spared", "sweep", bad == null, cases, bad ?? "creature limit 20..500 moves only living pawns; goods limit 5..200 moves only goods and corpses");
        }
        {
            string bad = null; int cases = 0;
            for (float pct = 25f; pct <= 400f && bad == null; pct += 5f)
            {
                cases++;
                float ratio = RM_KnockbackMath.DamageRatio(50, 50, pct, true);
                if (Math.Abs(ratio - 100f / pct) > 1e-4f) bad = $"ref {pct}%: ratio {ratio}";
                int a = ThrowWith(1f, MortarRadius, 1f, 50, 50, Colonist, S, true, pct), b = ThrowWith(1f, MortarRadius, 1f, 50, 50, Colonist, S, true, pct + 5f);
                if (b > a) bad = $"a higher reference threw farther ({pct}% {a} -> {b})";
            }
            for (float pct = 0f; pct <= 100f && bad == null; pct += 1f)
            {
                cases++;
                var c = KbLookup.Resolve(null, null, null, true, pct / 100f);
                if (Math.Abs(c.force - pct / 100f) > 1e-5f) bad = $"other-mods {pct}% gives force {c.force}";
                if (KbLookup.Resolve(null, null, null, false, pct / 100f).force != 0f) bad = "harmless throws under the other-mods percent";
            }
            Row("L1_sweep_refpercent_and_othermods", "settings_scale_and_switch,every_harmful_blast_throws", "sweep", bad == null, cases, bad ?? "reference 25..400% scales the ratio as 100/pct and never throws farther as it rises; other-mods 0..100% is the force, harmless always 0");
        }
        {
            string bad = null; int cases = 0;
            for (float imp = 0f; imp <= 15f && bad == null; imp += 0.5f)
                for (float fac = 0f; fac <= 2f && bad == null; fac += 0.5f)
                {
                    cases++;
                    var s = Shipped(); s.impactPerCell = imp; var k = KbLookup.Apply(s, new KbConfig { impactFactor = fac }, MaxCells, OwnCapScale);
                    var g = new Grid(10, 3); g.c[2, 1] = KbCell.Wall;
                    var r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, Colonist, k);
                    if ((imp * fac > 0f) != (r.impact > 0f)) bad = $"per cell {imp} factor {fac}: impact {r.impact}";
                    var s2 = Shipped(); s2.impactEnabled = false; s2.impactPerCell = imp;
                    if (RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, Colonist, KbLookup.Apply(s2, new KbConfig { impactFactor = fac }, MaxCells, OwnCapScale)).impact != 0f) bad = "impact off still hurts";
                }
            Row("L1_sweep_impact_per_cell_and_factor", "settings_scale_and_switch,wall_stops_dead,per_weapon_tuning", "sweep", bad == null, cases, bad ?? "impact per cell 0..15 x factor 0..2: impact > 0 exactly when both > 0; impact off never hurts");
        }
        {
            string bad = null; int cases = 0;
            for (float lim = 20f; lim <= 1000f && bad == null; lim += 10f)
            {
                cases++;
                if (RM_KnockbackMath.ContainerThrowCells(true, lim, lim, 0f, 2.9f, 3f, new KbSettings()) < 1 || RM_KnockbackMath.ContainerThrowCells(true, lim + 1f, lim, 0f, 2.9f, 3f, new KbSettings()) != 0) bad = $"container limit {lim}";
            }
            for (float mn = 1f; mn <= 75f && bad == null; mn += 1f)
                for (float dmin = 0f; dmin <= 20f && bad == null; dmin += 2f)
                    for (float dmax = 0f; dmax <= 20f && bad == null; dmax += 2f)
                    {
                        cases++;
                        bool hit = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, mn, mn, dmin, dmax, 0.99f, 30, out float dmg, out _);
                        if (!hit || dmg < dmin || dmg > Math.Max(dmin, dmax)) bad = $"heavy min {mn} dmg {dmin}..{dmax}: hit {hit} {dmg}";
                        if (RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, mn - 0.01f, mn, dmin, dmax, 0.5f, 30, out _, out _)) bad = $"under heavy min {mn} hit";
                    }
            for (int st = 0; st <= 180 && bad == null; st += 10) { cases++; RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 20, 10, 2, 5, 0.5f, st, out _, out int stun); if (stun != st) bad = $"stagger {st} -> {stun}"; }
            for (int w = 0; w <= 600 && bad == null; w += 10) { cases++; if (KbImmunity.CanLaunch(1000 + w - 1, 1000, 1000, w) && w > 0) bad = $"recovery {w} allowed early"; if (!KbImmunity.CanLaunch(1000 + w, 1000, 1000, w)) bad = $"recovery {w} refused late"; }
            for (float deb = 0f; deb <= 50f && bad == null; deb += 1f) { cases++; float e = KbShield.EnergyAfter(1f, 1f, deb, 0.033f); if ((deb > 0f) != (e < 1f)) bad = $"shield debit {deb}: {e}"; }
            Row("L1_sweep_container_heavy_recovery_shield", "settings_scale_and_switch,closed_container_holds,heavy_stack_knocks,recovery_immunity,shield_belt_holds", "sweep", bad == null, cases, bad ?? "container limit 20..1000, heavy min 1..75, damage 0..20 both ends, stagger 0..180, recovery 0..600, shield debit 0..50: each does exactly its own thing at every step");
        }

        // ===================== frame_time_probe / barrage_frame_budget (the pure reading) =====================
        {
            var ms = new float[1000]; var paused = new bool[1000]; var air = new int[1000];
            for (int i = 0; i < 1000; i++) { ms[i] = 16.6f; air[i] = i % 70; }
            ms[500] = 100f; paused[10] = true; ms[10] = 500f;
            float sum = ms.Sum();
            var g = KbFrameStats.Summarize(ms, paused, air, 1000, sum / 1000f);
            bool self = KbFrameStats.SelfCheck(g, 100f, out string w1), within = KbFrameStats.WithinBudget(g, 50f, out string w2);
            // the bar is the p99 frame (owner, 9c8c37aced "1 agree."; RIMMANDRAKE_ALIGN_LANE_FRAME_ROW_TO_P99_STILL_WORST): one 100 ms
            // frame is the worst frame yet within the 50 ms budget; a sustained stall (15 rows at 75 ms) is refused
            var stall = (float[])ms.Clone(); for (int i = 600; i < 615; i++) stall[i] = 75f;
            var gs = KbFrameStats.Summarize(stall, paused, air, 1000, stall.Sum() / 1000f);
            bool stallRefused = !KbFrameStats.WithinBudget(gs, 50f, out string w3);
            bool ok = g.worstMs == 100f && g.pausedRows == 1 && g.maxInAir == 69 && self && within && stallRefused;
            var gNo = KbFrameStats.Summarize(new float[0], new bool[0], new int[0], 0, 0f); ok &= !KbFrameStats.WithinBudget(gNo, 50f, out _);
            Row("L1_frame_probe_reading", "frame_time_probe,barrage_frame_budget", "fixed", ok, 4, $"worst {g.worstMs} (paused 500 ms row ignored), slept 100 ms seen {self} ({w1}), one 100 ms frame within the p99 50 ms budget {within} ({w2}), 15 rows at 75 ms refused {stallRefused} ({w3}); an empty run is not within budget");
        }

        // ===================== cycle-1 fixes, red first (lane2/faults.json) =====================
        {
            // RIMMANDRAKE_FLING_GOODS_WILD_FACTOR_NEVER_SHIPPED: goods fly about 1.6x a person (sheet), wild/kernel 1.3..2.0 (advisory)
            var wildM = typeof(RM_KnockbackMath).GetMethod("WildCells");
            float wild = float.Parse(Environment.GetEnvironmentVariable("EK_GOODS_WILD") ?? "0", System.Globalization.CultureInfo.InvariantCulture);
            if (wildM == null || !(wild > 0f)) Row("L1_goods_fly_wild", "goods_arc_spin_rebound", "random", false, 0, $"no wild factor ships: RM_KnockbackMath.WildCells {(wildM == null ? "missing" : "present")}, setting goodsThrowWild {(wild > 0f ? wild.ToString() : "missing")}");
            else
            {
                Func<float, float, float, float, KbSettings, float, int> W = (d, rad, f, m, s, w) => (int)wildM.Invoke(null, new object[] { d, rad, f, m, s, w });
                var r = new Random(101); string bad = null; int n = 20000; double sumW = 0, sumK = 0;
                for (int i = 0; i < n && bad == null; i++)
                {
                    float rad = (float)(1 + r.NextDouble() * 7), d = (float)(r.NextDouble() * rad), m = (float)(0.1 + r.NextDouble() * 74.9), f = (float)(r.NextDouble() * 2);
                    int k = RM_KnockbackMath.ThrowCells(d, rad, f, m, S), w = W(d, rad, f, m, S, wild), w1 = W(d, rad, f, m, S, 1f);
                    double raw = 4.0 * f * RM_KnockbackMath.Falloff(d, rad) * RM_KnockbackMath.MassScale(m, S);
                    if (w1 != k) bad = $"wild 1 is not the kernel: {w1} vs {k}";
                    else if (w < k) bad = $"a good flies less wild than its kernel: {w} < {k}";
                    else if (w > MaxCells) bad = $"wild {w} over the maximum";
                    else if (w < MaxCells && Math.Abs(w - raw * wild) > 0.5 + 1e-6 && raw * wild >= 0.5) bad = $"wild {w} is not round({raw * wild:0.###})";
                    if (k >= 2 && w < MaxCells) { sumW += w; sumK += k; }
                }
                int corpse = W(1f, MortarRadius, 1f, 60f, S, wild), person = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Colonist, S);
                double ratio = sumK > 0 ? sumW / sumK : 0;
                bool ok = bad == null && corpse > person && ratio >= 1.3 && ratio <= 2.0;
                Row("L1_goods_fly_wild", "goods_arc_spin_rebound", "random", ok, n, bad ?? $"seed 101, wild {wild}: wild 1 = kernel; wild never below the kernel or over the maximum; wild = round(raw x {wild}) below the cap; uncapped wild/kernel ratio {ratio:0.###}; a 60 kg corpse beside a mortar {corpse} cells vs a colonist {person}");
            }
        }
        {
            // RIMMANDRAKE_UNCOUPLE_GAS_GOODS_CAP_FROM_WEAPON_SCALE: the gas burst's goods cap is exact at every weapon cap scale
            var fld = typeof(KbConfig).GetField("scaleOwnCap");
            if (fld == null) Row("L1_gas_goods_cap_ignores_weapon_scale", "gas_goes_clump_by_clump,settings_scale_and_switch", "sweep", false, 0, $"KbConfig has no scaleOwnCap: a gas burst's own cap 2 becomes {KbLookup.Apply(S, new KbConfig { ownCap = 2 }, MaxCells, 2f).maxCells} at cap scale 2 and {KbLookup.Apply(S, new KbConfig { ownCap = 2 }, MaxCells, 0.25f).maxCells} at 0.25");
            else
            {
                string bad = null; int cases = 0;
                for (float scale = 0.25f; scale <= 2.0001f && bad == null; scale += 0.25f)
                    for (int gc = 1; gc <= 6 && bad == null; gc++)
                    {
                        cases++;
                        var gasCfg = new KbConfig { ownCap = gc }; fld.SetValue(gasCfg, false);
                        int got = KbLookup.Apply(S, gasCfg, MaxCells, scale).maxCells;
                        int weapon = KbLookup.Apply(S, new KbConfig { ownCap = gc }, MaxCells, scale).maxCells;
                        if (got != gc) bad = $"gas goods cells {gc} at cap scale {scale}: cap {got}";
                        if (weapon != Math.Max(1, (int)Math.Round(gc * scale, MidpointRounding.AwayFromZero))) bad = $"a weapon's own cap {gc} no longer scales at {scale}: {weapon}";
                    }
                Row("L1_gas_goods_cap_ignores_weapon_scale", "gas_goes_clump_by_clump,settings_scale_and_switch", "sweep", bad == null, cases, bad ?? "gas goods cells 1..6 x cap scale 0.25..2: the gas cap is exact; a weapon's own cap still scales");
            }
        }

        // ===================== bars the kernel cannot decide =====================
        Unsettled("L1_pawn_flight_arc", "pawn_flight_arc", "the carrier, re-targeting and job resumption are PawnFlyer runtime; the kernel only fixes the landing cell at launch (deterministic, row L1_resolve_invariants_random_grids)");
        Unsettled("L1_hose_drops_at_takeoff", "hose_drops_at_takeoff", "FlowWorks hose state, runtime only");
        Unsettled("L1_gas_clump_rules", "gas_goes_clump_by_clump,our_gases_burn", "no gas kernel ships: clump order, 1.9 radius, 2-cell goods cap, 1-cell shove, 120-tick cooldown live in the map component (lane 2 reads it)");
        Unsettled("L1_cover_breaks", "blast_breaks_pit_cover", "the cover's damage and the descent are runtime; the kernel only lands a thing on a CoveredPit cell (row L1_pit_first_cell_and_cover_landing)");
        Unsettled("L1_pit_goods_fetched", "pit_goods_fetched", "hauling off a pit floor is FlowWorks pathing, runtime");
        Unsettled("L1_only_explosions_throw", "only_explosions_throw", "which damage path calls the kernel is a Harmony patch (lane 2)");
        Unsettled("L1_no_teleport_no_careless_fall", "no_teleport,no_careless_fall", "spawn/despawn trace and pathing, runtime");
        Unsettled("L1_walk_and_frame_budget", "walk_storeroom_raid,barrage_frame_budget", "live_full by the tree; only the probe's pure reading is decided here");

        foreach (var line in Out) Console.WriteLine(line);
        Environment.Exit(fails > 0 ? 1 : 0);
    }
}
