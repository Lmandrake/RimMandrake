// Blind challenge, cycle 2, lane 1: Explosive Knockback's kernel judged from the bars alone (tree.json, sheet.md, plan.md,
// the inventory bar text) against Source/RM_KnockbackMath.cs as shipped and the settings ranges in RM_KnockbackMod.cs.
// Written by a judge that did not build the mod or judge cycle 1. One JSON row per line on stdout.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

public static class BlindLane1
{
    const float Wild = 1.6f;          // RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild (a const; the settings class needs Verse)
    const float MortarR = 2.9f;
    static readonly List<string> Rows = new List<string>();

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string bars, string kind, string verdict, int cases, string detail)
    {
        Rows.Add("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Split(',').Select(b => J(b.Trim()))) + "],\"kind\":" + J(kind)
            + ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    // a fixed-case row: every check must hold
    sealed class Checks
    {
        public int n; public List<string> bad = new List<string>();
        public void Eq<T>(string what, T got, T want) { n++; if (!EqualityComparer<T>.Default.Equals(got, want)) bad.Add(what + ": got " + got + " want " + want); }
        public void True(string what, bool ok) { n++; if (!ok) bad.Add(what); }
        public void Emit(string id, string bars, string kind = "fixed", string extra = "")
        {
            Row(id, bars, kind, bad.Count == 0 ? "PASS" : "FAIL", n, (bad.Count == 0 ? "all " + n + " hold" : string.Join("; ", bad.Take(6))) + (extra.Length > 0 ? "; " + extra : ""));
        }
    }

    static KbSettings Def() => new KbSettings();   // the kernel defaults = the shipped settings (strength 1, max 6, 70 kg, 150, 75)

    sealed class Grid : IKbGrid
    {
        public readonly int W, H; public readonly KbCell[,] c;
        public Grid(int w, int h) { W = w; H = h; c = new KbCell[w, h]; }
        public KbCell At(int x, int z) => x < 0 || z < 0 || x >= W || z >= H ? KbCell.OutOfBounds : c[x, z];
        public Grid Clone() { var g = new Grid(W, H); Array.Copy(c, g.c, c.Length); return g; }
        public string Dump() { var sb = new StringBuilder(); for (int z = H - 1; z >= 0; z--) { for (int x = 0; x < W; x++) sb.Append((int)c[x, z]); sb.Append('/'); } return sb.ToString(); }
    }

    static Grid Lane(params KbCell[] cells)   // a 1-high corridor: the thrown thing starts at x 0, the throw runs +x
    {
        var g = new Grid(cells.Length + 1, 1);
        for (int i = 0; i < cells.Length; i++) g.c[i + 1, 0] = cells[i];
        return g;
    }

    public static int Main()
    {
        Calibration();
        HeavierFliesLess();
        DamageRatio();
        GoodsWild();
        RimAndTooWeak();
        CapsAndPerWeapon();
        LookupOrder();
        Spared();
        Rebound();
        PathWalk();
        Impact();
        ContainerAndHeavy();
        Ledger();
        NoCap();
        RandomKernel(20261115);
        RandomPaths(20261116);
        Sweeps();
        NotKernel();
        foreach (string r in Rows) Console.WriteLine(r);
        return 0;
    }

    static void Calibration()
    {
        var k = new Checks(); var s = Def();
        k.Eq("mortar r2.9 d1 clothed colonist 70 kg", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s), 3);
        k.Eq("mortar r2.9 d1 naked 60 kg", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 60f, s), 3);
        k.Eq("mortar r2.9 d1 76 kg (64-76 band top)", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 76f, s), 3);
        k.Eq("mortar r2.9 d1 64 kg (band bottom)", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 64f, s), 3);
        k.Eq("at the radius: 0", RM_KnockbackMath.ThrowCells(2.9f, MortarR, 1f, 70f, s), 0);
        k.Eq("beyond the radius: 0", RM_KnockbackMath.ThrowCells(4f, MortarR, 1f, 70f, s), 0);
        k.Eq("radius 0: 0", RM_KnockbackMath.ThrowCells(0f, 0f, 1f, 70f, s), 0);
        k.Eq("fire at half (force 0.5) d1: about half", RM_KnockbackMath.ThrowCells(1f, MortarR, 0.5f, 70f, s), 1);
        k.Eq("force 0 (EMP, smoke, extinguish, tox gas)", RM_KnockbackMath.ThrowCells(0f, MortarR, 0f, 70f, s), 0);
        k.Emit("L1_mortar_throws_colonist_three", "people_thrown_three_cells,inv_kernel,every_harmful_blast_throws");
    }

    static void HeavierFliesLess()
    {
        var s = Def(); var k = new Checks();
        // rat 0.4 kg (mass scale capped at 2), colonist 70, muffalo 144, thrumbo 240 (tree.json oracle numbers)
        k.Eq("ref: rat", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 0.4f, s), 5);
        k.Eq("ref: colonist", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s), 3);
        k.Eq("ref: muffalo", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 144f, s), 2);
        k.True("ref: thrumbo 240 not eligible", !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, s));
        float f2 = 1f * RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
        k.Eq("x2: rat (cap 6)", RM_KnockbackMath.ThrowCells(1f, MortarR, f2, 0.4f, s), 6);
        k.Eq("x2: colonist", RM_KnockbackMath.ThrowCells(1f, MortarR, f2, 70f, s), 5);
        k.Eq("x2: muffalo", RM_KnockbackMath.ThrowCells(1f, MortarR, f2, 144f, s), 4);
        var s250 = Def(); s250.creatureMassLimit = 250f;
        k.True("limit 250: thrumbo eligible", RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, s250));
        k.Eq("limit 250 ref: thrumbo 1", RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 240f, s250), 1);
        k.Eq("limit 250 x2: thrumbo 3", RM_KnockbackMath.ThrowCells(1f, MortarR, f2, 240f, s250), 3);
        float off = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false);
        k.Eq("power off x2: colonist at ref", RM_KnockbackMath.ThrowCells(1f, MortarR, off, 70f, s), 3);
        k.Emit("L1_heavier_flies_less_oracle_numbers", "heavier_flies_less,inv_creature_mass_limit,inv_blast_power_damage,inv_kernel");
    }

    static void DamageRatio()
    {
        var k = new Checks();
        k.Eq("at normal damage", RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true), 1f);
        k.Eq("twice", RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true), 2f);
        k.Eq("off", RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false), 1f);
        k.Eq("no reference", RM_KnockbackMath.DamageRatio(100f, 0f, 100f, true), 1f);
        k.Eq("negative damage counts 0", RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true), 0f);
        k.Eq("ref percent 200 halves", RM_KnockbackMath.DamageRatio(50f, 50f, 200f, true), 0.5f);
        k.Eq("Flame at its own normal 10", RM_KnockbackMath.DamageRatio(10f, 10f, 100f, true), 1f);
        k.Emit("L1_blast_power_is_type_times_damage", "heavier_flies_less,inv_blast_power_damage");
    }

    static void GoodsWild()
    {
        var s = Def();
        // (a) a good flies at least as far as the kernel and never past the cap, over a dense lattice
        int n = 0; var bad = new List<string>();
        int[] hist = new int[12]; double sumRatio = 0; int ratioN = 0; double minR = 99, maxR = 0; string minCase = "";
        for (float d = 0f; d <= 6f; d += 0.05f)
            for (float m = 0.1f; m <= 80f; m *= 1.15f)
                foreach (float r in new[] { 1.9f, 2.9f, 3.5f, 5.9f })
                    foreach (float f in new[] { 0.5f, 1f, 2f })
                    {
                        n++;
                        int kc = RM_KnockbackMath.ThrowCells(d, r, f, m, s), wc = RM_KnockbackMath.WildCells(d, r, f, m, s, Wild);
                        if (wc < kc) bad.Add($"wild<kernel d{d:0.00} r{r} f{f} m{m:0.0}: {wc}<{kc}");
                        if (wc > s.maxCells) bad.Add($"wild over cap d{d:0.00} m{m:0.0}: {wc}");
                        if (kc >= 1 && kc < s.maxCells && wc < s.maxCells)
                        {
                            double ratio = (double)wc / kc; sumRatio += ratio; ratioN++;
                            if (ratio < minR) { minR = ratio; minCase = $"d{d:0.00} r{r} f{f} m{m:0.0}: kernel {kc} wild {wc}"; }
                            if (ratio > maxR) maxR = ratio;
                        }
                    }
        Row("L1_goods_fly_wild_at_least_kernel_under_cap", "goods_arc_spin_rebound,inv_goods_fly,inv_kernel", "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "wild >= kernel and wild <= cap on all " + n + " lattice cases (d 0-6 by 0.05, m 0.1-80 x1.15, r 1.9/2.9/3.5/5.9, force 0.5/1/2)" : string.Join("; ", bad.Take(5)));
        // (b) "about 1.6 times as far as a person": the per-case ratio of whole cells, away from the cap
        Row("L1_goods_wild_ratio_whole_cells", "goods_arc_spin_rebound", "info", "INFO", ratioN,
            $"wild/kernel over uncapped throws: mean {sumRatio / Math.Max(1, ratioN):0.000}, min {minR:0.00} ({minCase}), max {maxR:0.00}. Whole cells: a kernel 2 from raw 1.5 gives wild round(2.4)=2, ratio 1.0; the bar's 'about 1.6' holds on average, not per stack at short throws");
        // (c) the plain fixed points
        var k = new Checks();
        k.Eq("wild 1 = kernel (colonist)", RM_KnockbackMath.WildCells(1f, MortarR, 1f, 70f, s, 1f), RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s));
        k.Eq("mortar d1 70 kg good: round(2.62*1.6)=4", RM_KnockbackMath.WildCells(1f, MortarR, 1f, 70f, s, Wild), 4);
        k.Eq("wild 0", RM_KnockbackMath.WildCells(1f, MortarR, 1f, 70f, s, 0f), 0);
        k.Eq("wild negative clamps to 0", RM_KnockbackMath.WildCells(1f, MortarR, 1f, 70f, s, -1f), 0);
        k.Eq("force 0 stays 0 under wild", RM_KnockbackMath.WildCells(1f, MortarR, 0f, 1f, s, Wild), 0);
        var s0 = Def(); s0.globalMultiplier = 0f;
        k.Eq("strength 0 stays 0 under wild", RM_KnockbackMath.WildCells(1f, MortarR, 1f, 1f, s0, Wild), 0);
        k.Eq("a light good at the cap stays at the cap", RM_KnockbackMath.WildCells(0f, MortarR, 1f, 1f, s, Wild), 6);
        k.Emit("L1_goods_wild_fixed_points", "goods_arc_spin_rebound,inv_goods_fly");
    }

    static void RimAndTooWeak()
    {
        var s = Def();
        // the band where the kernel rounds to 0 but the wild throw is a cell: raw in [0.3125, 0.5)
        int band = 0, n = 0; string ex = "";
        for (float d = 0f; d < MortarR; d += 0.01f)
        {
            n++;
            int kc = RM_KnockbackMath.ThrowCells(d, MortarR, 1f, 70f, s), wc = RM_KnockbackMath.WildCells(d, MortarR, 1f, 70f, s, Wild);
            if (kc == 0 && wc >= 1) { band++; if (ex.Length == 0) ex = $"70 kg at d {d:0.00} of r 2.9: kernel 0, wild {wc}"; }
        }
        Row("L1_rim_band_kernel_zero_wild_one", "the_spared,inv_too_weak_skip,every_good_moves", "info", "INFO", n,
            $"{band} of {n} distances (step 0.01) have kernel 0 and wild 1, first {ex}. The game throws goods by the wild count, so a rim good the kernel rounds to 0 still flies one cell; inv_too_weak_skip and every_good_moves' oracle define 'reached' by the KERNEL throw. Either the oracle counts reached by the throw the good gets, or such goods should skip: a criterion question for the steward, not a kernel defect");
        var k = new Checks();
        k.Eq("raw 0.49 -> 0", RM_KnockbackMath.ThrowCells(MortarR * (1f - 0.49f / 4f), MortarR, 1f, 70f, s), 0);
        k.Eq("raw 0.5 -> 1 (away from zero)", RM_KnockbackMath.ThrowCells(MortarR * (1f - 0.5f / 4f), MortarR, 1f, 70f, s), 1);
        k.Emit("L1_rim_under_one_cell_is_no_throw", "the_spared,inv_too_weak_skip,inv_kernel");
    }

    static void CapsAndPerWeapon()
    {
        var k = new Checks(); var g = Def();
        k.Eq("own max 2", RM_KnockbackMath.CapFor(2, 6, 1f), 2);
        k.Eq("own max 4 under scale 0.5", RM_KnockbackMath.CapFor(4, 6, 0.5f), 2);
        k.Eq("own max 0 under scale 0.5 keeps global", RM_KnockbackMath.CapFor(0, 6, 0.5f), 6);
        k.Eq("own max 1 under scale 0.25 never below 1", RM_KnockbackMath.CapFor(1, 6, 0.25f), 1);
        k.Eq("own max 9 under scale 2", RM_KnockbackMath.CapFor(9, 6, 2f), 18);
        var two = KbLookup.Apply(g, new KbConfig { ownCap = 2 }, 6, 1f);
        k.Eq("own max 2 throws 2 at most", RM_KnockbackMath.ThrowCells(0f, MortarR, 1f, 1f, two), 2);
        var four = KbLookup.Apply(g, new KbConfig { ownCap = 4 }, 6, 0.5f);
        k.Eq("own max 4 x 0.5 throws 2", RM_KnockbackMath.ThrowCells(0f, MortarR, 1f, 1f, four), 2);
        var zero = KbLookup.Apply(g, new KbConfig { ownCap = 0 }, 6, 0.5f);
        k.Eq("own max 0 x 0.5 throws the global 6", RM_KnockbackMath.ThrowCells(0f, MortarR, 1f, 1f, zero), 6);
        // gas burst: goods at most gasBurstGoodsCells whatever the weapons' scale
        foreach (float sc in new[] { 0.25f, 0.5f, 1f, 1.5f, 2f })
            for (int gc = 1; gc <= 6; gc++)
            {
                var gas = KbLookup.Apply(g, new KbConfig { force = 1f, ownCap = gc, impactFactor = 0f, scaleOwnCap = false }, 10, sc);
                k.Eq($"gas cap {gc} under scale {sc}", gas.maxCells, gc);
                k.True($"gas goods at most {gc} (scale {sc})", RM_KnockbackMath.WildCells(0f, 1.9f, 1f, 0.1f, gas, Wild) <= gc);
            }
        var nul = KbLookup.Apply(g, null, 6, 0.5f);
        k.Eq("no config: global cap", nul.maxCells, 6);
        k.Eq("no config: impact factor 1", nul.impactFactor, 1f);
        var ov = KbLookup.Apply(g, new KbConfig { massLimitOverride = 216f, impactFactor = -3f }, 6, 1f);
        k.Eq("override 216", ov.creatureMassLimit, 216f);
        k.True("216 throws 180 kg", RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, ov));
        k.True("216 spares 240 kg", !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, ov));
        k.True("no override spares 151 kg", !RM_KnockbackMath.Eligible(KbKind.Pawn, 151f, g));
        k.Eq("negative impact factor clamps 0", ov.impactFactor, 0f);
        k.Eq("Apply never mutates the global", g.maxCells, 6);
        k.Emit("L1_per_weapon_caps_and_gas_cap", "per_weapon_tuning,gas_goes_clump_by_clump,inv_weapon_ext_fields,inv_kernel");
    }

    static void LookupOrder()
    {
        var k = new Checks();
        KbConfig p = new KbConfig { force = 3f }, w = new KbConfig { force = 2f }, d = new KbConfig { force = 0.5f };
        var a = KbLookup.Resolve(p, w, d, true, 1f); k.Eq("projectile first", a.force, 3f); k.Eq("source projectile", a.source, "projectile");
        var b = KbLookup.Resolve(null, new KbConfig { force = 2f }, new KbConfig { force = 0.5f }, true, 1f); k.Eq("then weapon", b.force, 2f); k.Eq("source weapon", b.source, "weapon");
        var c = KbLookup.Resolve(null, null, new KbConfig { force = 0.5f }, true, 1f); k.Eq("then damage type", c.force, 0.5f);
        var z = KbLookup.Resolve(new KbConfig { force = 0f }, null, new KbConfig { force = 1f }, true, 1f); k.Eq("zero on projectile wins", z.force, 0f);
        k.Eq("zero throws nothing", RM_KnockbackMath.ThrowCells(0f, MortarR, z.force, 1f, Def()), 0);
        var u = KbLookup.Resolve(null, null, null, true, 1f); k.Eq("unpatched harmful at 100%", u.force, 1f); k.Eq("source unpatched", u.source, "unpatched");
        var h = KbLookup.Resolve(null, null, null, false, 1f); k.Eq("harmless bursts nothing", h.force, 0f);
        var u0 = KbLookup.Resolve(null, null, null, true, 0f); k.Eq("other-mods percent 0", u0.force, 0f);
        k.Emit("L1_lookup_projectile_weapon_type", "per_weapon_tuning,every_harmful_blast_throws");
    }

    static void Spared()
    {
        var k = new Checks(); var s = Def();
        k.True("pawn 150 kg thrown (limit is 'heavier than')", RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s));
        k.True("pawn 150.1 spared", !RM_KnockbackMath.Eligible(KbKind.Pawn, 150.1f, s));
        k.True("muffalo 144 flies", RM_KnockbackMath.Eligible(KbKind.Pawn, 144f, s));
        k.True("rhino 180 stays", !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, s));
        k.True("item 75 thrown", RM_KnockbackMath.Eligible(KbKind.Item, 75f, s));
        k.True("item 75.1 spared", !RM_KnockbackMath.Eligible(KbKind.Item, 75.1f, s));
        k.True("corpse 76 spared", !RM_KnockbackMath.Eligible(KbKind.Corpse, 76f, s));
        var s20 = Def(); s20.creatureMassLimit = 20f;
        k.True("creature limit 20: human corpse 60 kg still thrown", RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, s20));
        var sHi = Def(); sHi.lightMassLimit = 200f;
        k.True("goods limit 200: thrumbo corpse 180 thrown (no body-size rule)", RM_KnockbackMath.Eligible(KbKind.Corpse, 180f, sHi));
        k.True("goods limit never weighs a living pawn (pawn 100 with goods limit 5)", RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, new KbSettings { lightMassLimit = 5f }));
        k.Emit("L1_spared_by_mass", "the_spared,inv_mass_limit_skip,inv_creature_mass_limit,inv_big_corpse_spared");
    }

    static void Rebound()
    {
        var k = new Checks();
        int c = 6; var chain = new List<int> { c };
        while (c > 0 && chain.Count < 20) { c = RM_KnockbackMath.ReboundCells(c, 70f); chain.Add(c); }
        k.Eq("70% chain from 6", string.Join(",", chain), "6,4,2,1,0");
        k.Eq("1 cell left at 70% = 0", RM_KnockbackMath.ReboundCells(1, 70f), 0);
        k.Eq("keep 0", RM_KnockbackMath.ReboundCells(5, 0f), 0);
        k.Eq("keep 100 loses nothing", RM_KnockbackMath.ReboundCells(5, 100f), 5);
        k.Eq("keep 150 clamps to 100", RM_KnockbackMath.ReboundCells(5, 150f), 5);
        k.Eq("nothing left", RM_KnockbackMath.ReboundCells(0, 70f), 0);
        k.Emit("L1_rebound_keeps_seventy_percent", "goods_arc_spin_rebound,inv_goods_fly");
        // the slider sweep 0..100: below 100 every chain ends within cellsLeft rebounds; at 100 the kernel never ends it
        int n = 0; var bad = new List<string>();
        for (int keep = 0; keep <= 100; keep++)
            for (int left = 1; left <= 12; left++)
            {
                n++;
                int x = left, steps = 0;
                while (x > 0 && steps < 50) { int y = RM_KnockbackMath.ReboundCells(x, keep); if (y > x) bad.Add($"grows keep{keep} {x}->{y}"); if (keep < 100 && y >= x) { bad.Add($"no loss keep{keep} at {x}"); break; } x = y; steps++; }
                if (keep < 100 && x > 0) bad.Add($"chain does not end keep{keep} left{left}");
            }
        Row("L1_sweep_rebound_keep_slider", "goods_arc_spin_rebound,settings_scale_and_switch", "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "keep 0..99: every chain loses a cell or more per rebound and ends within cellsLeft rebounds; keep 100: the kernel keeps every cell, so the chain is ended by the carrier's bounce limit (game-side, not decided here)" : string.Join("; ", bad.Take(5)));
    }

    static void PathWalk()
    {
        var s = Def(); var k = new Checks();
        KbCell O = KbCell.Open;
        var r = RM_KnockbackMath.Resolve(Lane(O, O, KbCell.Wall, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("wall: stops dead before it", r.destX, 2); k.Eq("wall stop", r.stop, KbStop.Wall); k.True("wall: a pawn takes an impact", r.impact > 0f); k.True("wall: block recorded", r.hasBlock && r.blockX == 3);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Door, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("door: stops before", r.destX, 1); k.True("door hit", r.hitDoor && r.doorX == 2); k.Eq("door stop", r.stop, KbStop.Door);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Water, O), 0, 0, 1, 0, 3, KbKind.Item, 1f, s);
        k.Eq("deep water: last standable cell", r.destX, 1); k.Eq("water stop", r.stop, KbStop.Water);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Partial, O, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("over sandbags", r.destX, 3); k.Eq("over sandbags travelled", r.cellsTravelled, 3);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Partial, O), 0, 0, 1, 0, 2, KbKind.Pawn, 70f, s);
        k.Eq("never rests on a sandbag", r.destX, 1);
        var sb = Def(); sb.sandbagsStop = true;
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Partial, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, sb);
        k.Eq("sandbags stop on: pawn stops", r.stop, KbStop.PartialCover); k.Eq("sandbags stop on: dest", r.destX, 1);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Pit, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("open pit: stops IN the pit", r.destX, 2); k.Eq("pit stop", r.stop, KbStop.Pit);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Pit, O), 0, 0, 1, 0, 3, KbKind.Item, 1f, s);
        k.Eq("goods fall in too", r.stop, KbStop.Pit);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.CoveredPit, O, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("covered pit is ground for the path", r.destX, 3);
        var np = Def(); np.intoPits = false;
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Pit, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, np);
        k.Eq("into pits off: pit is a wall", r.stop, KbStop.Wall); k.Eq("into pits off: dest", r.destX, 1);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Pawn, O), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("pawn hits pawn: stops", r.destX, 1); k.True("pawn hits pawn: both hurt", r.hitOther && r.impact > 0 && r.otherImpact > 0);
        r = RM_KnockbackMath.Resolve(Lane(O, KbCell.Pawn, O), 0, 0, 1, 0, 3, KbKind.Item, 1f, s);
        k.Eq("goods pass a pawn's cell in the kernel", r.destX, 3);
        r = RM_KnockbackMath.Resolve(Lane(O), 0, 0, 1, 0, 4, KbKind.Item, 1f, s);
        k.Eq("map edge", r.stop, KbStop.OutOfBounds); k.Eq("map edge dest", r.destX, 1);
        var cg = new Grid(3, 3); cg.c[1, 0] = KbCell.Wall;  // corner at (1,0): a diagonal from (0,0) to (1,1) cuts it
        r = RM_KnockbackMath.Resolve(cg, 0, 0, 1, 1, 2, KbKind.Pawn, 70f, s);
        k.Eq("never cuts a wall corner", r.cellsTravelled, 0);
        r = RM_KnockbackMath.Resolve(Lane(O, O), 0, 0, 1, 0, 0, KbKind.Pawn, 70f, s);
        k.Eq("0 cells: no move", r.stop, KbStop.None);
        k.Emit("L1_path_walk_fixed", "inv_kernel,wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop,thrown_into_pit_falls,people_thrown_three_cells");
    }

    static void Impact()
    {
        var s = Def(); var k = new Checks();
        var r = RM_KnockbackMath.Resolve(Lane(KbCell.Wall), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s);
        k.Eq("impact at a wall: 4 x 3 left / sqrt(1)", r.impact, 12f);
        var f0 = KbLookup.Apply(s, new KbConfig { impactFactor = 0f }, 6, 1f);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Wall), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, f0);
        k.Eq("impact factor 0: harmless at the wall", r.impact, 0f);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Pawn), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, f0);
        k.Eq("impact factor 0: harmless to the pawn hit", r.otherImpact, 0f);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Door), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, f0);
        k.Eq("impact factor 0 at a door: no impact", r.impact, 0f); k.True("the door still stops it", r.hitDoor);
        var off = Def(); off.impactEnabled = false;
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Wall), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, off);
        k.Eq("impact off", r.impact, 0f);
        r = RM_KnockbackMath.Resolve(Lane(KbCell.Wall), 0, 0, 1, 0, 3, KbKind.Item, 1f, s);
        k.Eq("goods take no kernel impact (the goods wall hit is game-side)", r.impact, 0f);
        k.Emit("L1_impact_and_factor_zero", "wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop,per_weapon_tuning");
    }

    static void ContainerAndHeavy()
    {
        var k = new Checks();
        // (edited after lane 1 was recorded, blind cycle 2: the dead slide kernel ContainerShove was deleted by the steward's
        // decision 7, owner card 2026-11-14 "thrown as built"; the row now tests the container throw the game calls)
        var cs = Def();
        k.Eq("30 kg 1x1 at mortar d1: the item kernel's cells", RM_KnockbackMath.ContainerThrowCells(true, 30f, 250f, 1f, MortarR, 1f, cs), RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 30f, cs));
        k.True("250 kg at the limit is still thrown", RM_KnockbackMath.ContainerThrowCells(true, 250f, 250f, 0f, MortarR, 2f, cs) >= 1);
        k.Eq("251 kg: jolt (0 cells)", RM_KnockbackMath.ContainerThrowCells(true, 251f, 250f, 0f, MortarR, 2f, cs), 0);
        k.Eq("not 1x1: jolt", RM_KnockbackMath.ContainerThrowCells(false, 10f, 250f, 0f, MortarR, 1f, cs), 0);
        k.True("100 kg (over the 75 kg goods limit) still thrown: the container limit is its own", RM_KnockbackMath.ContainerThrowCells(true, 100f, 250f, 0f, MortarR, 1f, cs) >= 1);
        foreach (KbCell c in Enum.GetValues(typeof(KbCell)))
            k.Eq("shove cell " + c, RM_KnockbackMath.ShoveCellFree(c, false), c == KbCell.Open);
        k.True("shove cell with things on it", !RM_KnockbackMath.ShoveCellFree(KbCell.Open, true));
        k.Emit("L1_container_throw_kernel", "closed_container_holds,inv_container_shove", "fixed",
            "ContainerThrowCells (called by ThrowContainer) against the 250 kg container limit; sc_closed_containers' wording (slide vs thrown) is the steward's re-pin, no verdict built on it");
        var h = new Checks();
        h.True("10 kg stack knocks", RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 10f, 10f, 2f, 5f, 0.5f, 30, out float d1, out int st1) && d1 >= 2f && d1 <= 5f && st1 == 30);
        h.True("9.9 kg passes", !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 9.9f, 10f, 2f, 5f, 0.5f, 30, out _, out _));
        h.True("a corpse passes", !RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 50f, 10f, 2f, 5f, 0.5f, 30, out _, out _));
        h.True("off passes", !RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 50f, 10f, 2f, 5f, 0.5f, 30, out _, out _));
        h.True("no person: passes", !RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 50f, 10f, 2f, 5f, 0.5f, 30, out _, out _));
        h.True("roll 1: 5", RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 2f, 5f, 1f, 30, out float d2, out _) && d2 == 5f);
        h.True("max under min uses min", RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 4f, 1f, 1f, 30, out float d3, out _) && d3 == 4f);
        h.True("negative stagger is 0", RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 2f, 5f, 0f, -5, out _, out int st2) && st2 == 0);
        h.Emit("L1_heavy_stack_knock", "heavy_stack_knocks,inv_heavy_knock");
    }

    static void Ledger()
    {
        var k = new Checks(); var L = new KbExplosionLedger(600);
        k.True("first request", L.TryAdd(7, 100, 0));
        k.True("repeat in the same tick refused", !L.TryAdd(7, 100, 0));
        k.True("repeat 599 ticks on refused", !L.TryAdd(7, 100, 599));
        k.True("another explosion may throw it", L.TryAdd(8, 100, 10));
        // a wave that straddles a generation boundary keeps its pairs
        var L2 = new KbExplosionLedger(600);
        k.True("t 599", L2.TryAdd(1, 1, 599)); k.True("t 601 same pair refused", !L2.TryAdd(1, 1, 601));
        k.Emit("L1_one_request_per_thing_per_explosion", "every_good_moves,inv_kernel");
    }

    static void NoCap()
    {
        var k = new Checks(); var all = new List<KbCandidate>();
        for (int i = 0; i < 150; i++) all.Add(new KbCandidate { index = i, kind = i % 3 == 0 ? KbKind.Pawn : KbKind.Item, distance = i * 0.01f });
        k.Eq("cap -1 keeps all 150", RM_KnockbackMath.Prioritise(all, -1).Count, 150);
        k.Eq("the old cap 40 (control) keeps 40", RM_KnockbackMath.Prioritise(all, 40).Count, 40);
        k.True("pawns first", RM_KnockbackMath.Prioritise(all, 40).Take(40).All(c => c.kind == KbKind.Pawn));
        k.Emit("L1_no_cap_kernel_and_control", "every_good_moves,inv_caps", "fixed", "whether the game passes no cap is game-side");
    }

    // ── random kernel properties, seed recorded, failures shrunk ─────────────
    static void RandomKernel(int seed)
    {
        var rng = new Random(seed); int n = 0; string fail = null;
        for (int i = 0; i < 40000 && fail == null; i++)
        {
            n++;
            var s = Def(); s.globalMultiplier = (float)(rng.NextDouble() * 3); s.maxCells = 1 + rng.Next(10);
            float r = 0.5f + (float)rng.NextDouble() * 8f, d = (float)rng.NextDouble() * 9f, f = (float)rng.NextDouble() * 3f, m = 0.05f + (float)rng.NextDouble() * 300f;
            float d2 = d + (float)rng.NextDouble() * 2f, m2 = m + (float)rng.NextDouble() * 50f, f2 = f + (float)rng.NextDouble();
            int a = RM_KnockbackMath.ThrowCells(d, r, f, m, s);
            string c = $"seed {seed} i{i}: d{d:0.###} r{r:0.###} f{f:0.###} m{m:0.###} mult{s.globalMultiplier:0.###} cap{s.maxCells}";
            if (a < 0 || a > s.maxCells) fail = c + $" out of 0..cap: {a}";
            else if (RM_KnockbackMath.ThrowCells(d2, r, f, m, s) > a) fail = c + $" farther from the blast flies farther (d2 {d2:0.###})";
            else if (RM_KnockbackMath.ThrowCells(d, r, f, m2, s) > a) fail = c + $" heavier flies farther (m2 {m2:0.###})";
            else if (RM_KnockbackMath.ThrowCells(d, r, f2, m, s) < a) fail = c + $" stronger flies less (f2 {f2:0.###})";
            else if (RM_KnockbackMath.WildCells(d, r, f, m, s, Wild) < a) fail = c + " wild < kernel";
            else if (RM_KnockbackMath.WildCells(d, r, f, m2, s, Wild) > RM_KnockbackMath.WildCells(d, r, f, m, s, Wild)) fail = c + " heavier good flies farther";
        }
        Row("L1_random_throw_monotone", "inv_kernel,heavier_flies_less,goods_arc_spin_rebound", "random", fail == null ? "PASS" : "FAIL", n,
            fail ?? $"seed {seed}: {n} random blasts; throw in 0..cap, non-increasing in distance and mass, non-decreasing in force; wild >= kernel and non-increasing in mass");
    }

    static string PathProblem(Grid g, int sx, int sz, float dx, float dz, int cells, KbKind kind, KbSettings s)
    {
        var r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, 70f, s);
        var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
        if (r.cellsTravelled < 0 || r.cellsTravelled > cells) return $"travelled {r.cellsTravelled} of {cells}";
        if (path.Count != cells && cells > 0) return $"line has {path.Count} steps for {cells} cells";
        if (r.cellsTravelled > 0 && (r.destX, r.destZ) != path[r.cellsTravelled - 1]) return "dest is not the travelled-th path cell";
        if (r.cellsTravelled == 0 && (r.destX != sx || r.destZ != sz)) return "no travel but moved";
        KbCell at = g.At(r.destX, r.destZ);
        if (r.cellsTravelled > 0 && (at == KbCell.Wall || at == KbCell.Door || at == KbCell.Water || at == KbCell.OutOfBounds || at == KbCell.Partial)) return "rests on " + at;
        if (kind == KbKind.Pawn && r.cellsTravelled > 0 && at == KbCell.Pawn) return "a pawn rests on a pawn";
        for (int i = 0; i < r.cellsTravelled; i++)
        {
            KbCell c = g.At(path[i].x, path[i].z);
            if (c == KbCell.Wall || c == KbCell.Door || c == KbCell.Water || c == KbCell.OutOfBounds) return $"passed through {c} at step {i + 1}";
            if (c == KbCell.Pit && i < r.cellsTravelled - 1) return "thrown across a pit";
            if (kind == KbKind.Pawn && c == KbCell.Pawn) return "a pawn passed a pawn";
        }
        if (r.stop == KbStop.Distance && r.cellsTravelled != cells && g.At(path[cells - 1].x, path[cells - 1].z) != KbCell.Partial) return "Distance stop short of its cells";
        if (kind != KbKind.Pawn && (r.impact != 0f || r.otherImpact != 0f)) return "goods impact in kernel";
        if (r.stop == KbStop.Pit && at != KbCell.Pit) return "Pit stop off a pit";
        if (r.stop == KbStop.Pit && !s.intoPits) return "into pits off but fell in";
        return null;
    }

    static void RandomPaths(int seed)
    {
        var rng = new Random(seed); int n = 0; string fail = null;
        KbCell[] pool = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
        for (int i = 0; i < 20000 && fail == null; i++)
        {
            n++;
            int w = 5 + rng.Next(10), h = 5 + rng.Next(10); var g = new Grid(w, h);
            for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) g.c[x, z] = pool[rng.Next(pool.Length)];
            int sx = rng.Next(w), sz = rng.Next(h); g.c[sx, sz] = KbCell.Open;
            double a = rng.NextDouble() * Math.PI * 2; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
            int cells = rng.Next(9); KbKind kind = (KbKind)rng.Next(3);
            var s = Def(); s.sandbagsStop = rng.Next(4) == 0; s.intoPits = rng.Next(4) != 0;
            string p = PathProblem(g, sx, sz, dx, dz, cells, kind, s);
            if (p != null)
            {
                // shrink: open every cell that is not needed, then cut the throw short
                bool changed = true;
                while (changed)
                {
                    changed = false;
                    for (int x = 0; x < w; x++) for (int z = 0; z < h; z++)
                        {
                            if (g.c[x, z] == KbCell.Open) continue;
                            var keep = g.c[x, z]; g.c[x, z] = KbCell.Open;
                            if (PathProblem(g, sx, sz, dx, dz, cells, kind, s) != null) changed = true; else g.c[x, z] = keep;
                        }
                    if (cells > 1 && PathProblem(g, sx, sz, dx, dz, cells - 1, kind, s) != null) { cells--; changed = true; }
                }
                fail = $"seed {seed} i{i}: {PathProblem(g, sx, sz, dx, dz, cells, kind, s)}; shrunk grid {w}x{h} {g.Dump()} start ({sx},{sz}) dir ({dx:0.###},{dz:0.###}) cells {cells} kind {kind} sandbagsStop {s.sandbagsStop} intoPits {s.intoPits}";
            }
        }
        Row("L1_random_path_walk_conservation", "inv_kernel,no_teleport,thrown_into_pit_falls,wall_stops_dead,doors_and_deep_water_stop", "random", fail == null ? "PASS" : "FAIL", n,
            fail ?? $"seed {seed}: {n} random grids; a throw never passes a wall, door, water or the edge, never crosses a pit, never rests on sandbags, a wall or a pawn, travels at most its cells along its own line, goods take no kernel impact");
    }

    static void Sweeps()
    {
        // every shipped kernel-facing slider through its range (RM_KnockbackMod.cs DoSettingsWindowContents)
        int n = 0; var bad = new List<string>();
        for (float st = 0f; st <= 3.0001f; st += 0.05f)
            for (int max = 1; max <= 10; max++)
                foreach (float scale in new[] { 0.25f, 0.5f, 1f, 1.5f, 2f })
                    foreach (int own in new[] { 0, 2, 4 })
                    {
                        n++;
                        var g = Def(); g.globalMultiplier = st;
                        var s = KbLookup.Apply(g, new KbConfig { ownCap = own }, max, scale);
                        int cap = RM_KnockbackMath.CapFor(own, max, scale);
                        int kc = RM_KnockbackMath.ThrowCells(1f, MortarR, 1f, 70f, s), wc = RM_KnockbackMath.WildCells(0.5f, MortarR, 1f, 2f, s, Wild);
                        if (kc > cap || wc > cap) bad.Add($"over cap st{st} max{max} scale{scale} own{own}");
                        if (st < 1e-6f && (kc != 0 || wc != 0)) bad.Add("strength 0 throws");
                        if (st > 0.999f && st < 1.001f && max >= 3 && own == 0 && kc != 3) bad.Add($"calibration lost at max {max}: {kc}");
                    }
        foreach (float cm in Range(20f, 500f, 1f)) { n++; var s = Def(); s.creatureMassLimit = cm; if (RM_KnockbackMath.Eligible(KbKind.Pawn, cm + 0.5f, s) || !RM_KnockbackMath.Eligible(KbKind.Pawn, cm, s) || !RM_KnockbackMath.Eligible(KbKind.Corpse, Math.Min(75f, cm + 10f), s)) bad.Add("creature limit " + cm); }
        foreach (float lm in Range(5f, 200f, 0.5f)) { n++; var s = Def(); s.lightMassLimit = lm; if (RM_KnockbackMath.Eligible(KbKind.Item, lm + 0.25f, s) || !RM_KnockbackMath.Eligible(KbKind.Item, lm, s) || !RM_KnockbackMath.Eligible(KbKind.Pawn, 149f, s)) bad.Add("goods limit " + lm); }
        foreach (float rp in Range(25f, 400f, 1f)) { n++; float ratio = RM_KnockbackMath.DamageRatio(50f, 50f, rp, true); if (Math.Abs(ratio - 100f / rp) > 1e-4f) bad.Add("ref percent " + rp); }
        foreach (float ip in Range(0f, 15f, 0.5f)) { n++; var s = Def(); s.impactPerCell = ip; var r = RM_KnockbackMath.Resolve(Lane(KbCell.Wall), 0, 0, 1, 0, 3, KbKind.Pawn, 70f, s); if (Math.Abs(r.impact - ip * 3f) > 1e-3f) bad.Add("impact per cell " + ip); }
        foreach (float up in Range(0f, 100f, 1f)) { n++; var c = KbLookup.Resolve(null, null, null, true, up / 100f); if (Math.Abs(c.force - up / 100f) > 1e-6f) bad.Add("other-mods " + up); }
        Row("L1_sweep_kernel_settings_ranges", "settings_scale_and_switch,inv_settings,inv_kernel,per_weapon_tuning", "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? $"{n} settings points: strength 0-3 x max 1-10 x own-max scale 0.25-2 x own max 0/2/4; creature limit 20-500; goods limit 5-200; ref percent 25-400; impact 0-15; other-mods 0-100: every cap holds, strength 0 throws nothing, the 3-cell calibration holds at strength 1 for every max >= 3" : string.Join("; ", bad.Take(5)));
    }

    static IEnumerable<float> Range(float a, float b, float step) { for (float x = a; x <= b + 1e-4f; x += step) yield return x; }

    static void NotKernel()
    {
        Row("L1_not_kernel_goods_carrier", "goods_arc_spin_rebound,no_teleport,inv_goods_fly", "not_kernel", "UNSETTLED", 0, "arc height, spin, drawn position and the bounce limit at keep 100 live in RM_ThingFlyer_Knockback.cs (game-side); lane 2 and the live Stage 6 trace decide them");
        Row("L1_not_kernel_every_good_counted", "every_good_moves", "not_kernel", "UNSETTLED", 0, "stacks reached vs moved, the absent cap lines and the 40-cap control hook are game-side (RM_MapComponent_Knockback.cs, proof scenes)");
        Row("L1_not_kernel_gas_chain", "gas_goes_clump_by_clump,our_gases_burn,inv_gas_chain", "not_kernel", "UNSETTLED", 0, "clump ordering, the 2 s cooldown, belts ignored and fire-touch ignition are game-side; the kernel half (goods cap exact at gasBurstGoodsCells) is in L1_per_weapon_caps_and_gas_cap");
        Row("L1_not_kernel_switches", "settings_scale_and_switch", "not_kernel", "UNSETTLED", 0, "each switch's off state (goods in the air off, closed guard off, container shove off, sealed crates off, heavy knock off, gas chain off, fire at half off, blast power off) is read game-side");
        Row("L1_not_kernel_proof_scenes", "inv_proof_scenes", "not_kernel", "UNSETTLED", 0, "the live scenes (RM_KnockbackProof*.cs) are decided by T_SCRIPT, T_PROOFGATE and T_RESTORE in lane 2");
    }
}
