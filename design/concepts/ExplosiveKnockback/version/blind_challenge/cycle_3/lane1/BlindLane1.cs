// Blind lane 1, ExplosiveKnockback 0.1.0, cycle 3. Written from the bars (tree/sheet leaves, record.json inv_kernel) and the
// shipped settings alone, against RM_KnockbackMath.cs compiled as shipped. Prints one JSON row per line.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

public static class BlindLane1
{
    // ---- shipped values (RM_KnockbackMod.cs defaults; Patches/RM_Knockback_DamageDefs.xml forces) ----
    const float MortarRadius = 2.9f;       // vanilla Shell_HighExplosive; the kernel's calibration comment (owner Q7)
    const float Colonist = 70f, Muffalo = 144f, Rat = 0.5f, Thrumbo = 1000f;
    const float Wild = 1.6f;               // RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild

    static readonly List<string> Rows = new List<string>();
    static int pass, fail;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "PASS") pass++; else if (verdict == "FAIL") fail++;
        Rows.Add("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind) +
                 ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static void Check(string id, string[] bars, string kind, List<string> bad, int cases, string okDetail)
    {
        Row(id, bars, kind, bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? okDetail : ("FAIL " + bad.Count + "/" + cases + ": " + string.Join(" | ", bad.Take(4))));
    }

    sealed class Grid : IKbGrid
    {
        public readonly Dictionary<(int, int), KbCell> cells = new Dictionary<(int, int), KbCell>();
        public int W = 40, H = 40;
        public KbCell At(int x, int z)
        {
            if (x < 0 || z < 0 || x >= W || z >= H) return KbCell.OutOfBounds;
            return cells.TryGetValue((x, z), out var c) ? c : KbCell.Open;
        }
        public Grid Set(int x, int z, KbCell c) { cells[(x, z)] = c; return this; }
    }

    static KbSettings S() => new KbSettings();

    static int Cheb(int ax, int az, int bx, int bz) => Math.Max(Math.Abs(ax - bx), Math.Abs(az - bz));

    public static int Main()
    {
        FixedRows();
        RandomRows(20261115);
        SweepRows();
        foreach (var r in Rows) Console.WriteLine(r);
        Console.Error.WriteLine("lane1 C#: PASS " + pass + " FAIL " + fail + " rows " + Rows.Count);
        return 0;
    }

    // ---------------------------------------------------------------- fixed
    static void FixedRows()
    {
        var s = S();
        // people_thrown_three_cells: a mortar shell beside a colonist throws them about three cells, over sandbags
        {
            var bad = new List<string>();
            int c = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Colonist, s);
            if (c != 3) bad.Add("mortar beside 70 kg colonist throws " + c);
            int c60 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, 60f, s);
            if (c60 < 3 || c60 > 4) bad.Add("60 kg naked colonist throws " + c60);
            var g = new Grid().Set(11, 10, KbCell.Partial).Set(12, 10, KbCell.Partial);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r.cellsTravelled != 3 || r.destX != 13 || r.stop != KbStop.Distance) bad.Add("over two sandbags: travelled " + r.cellsTravelled + " dest " + r.destX + " stop " + r.stop);
            if (r.impact != 0f) bad.Add("over sandbags took impact " + r.impact);
            Check("fx_mortar_colonist_three_cells_over_sandbags", new[] { "people_thrown_three_cells", "inv_kernel" }, "fixed", bad, 4,
                "mortar r2.9 d1: 70 kg -> 3, 60 kg -> " + c60 + "; over two sandbag cells lands 3 cells on, no impact");
        }
        // no resting on a sandbag cell
        {
            var bad = new List<string>();
            var g = new Grid().Set(13, 10, KbCell.Partial);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (g.At(r.destX, r.destZ) == KbCell.Partial) bad.Add("pawn rests on sandbag");
            if (r.destX != 12) bad.Add("pawn dest " + r.destX + " want 12");
            var ri = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Item, 1f, s);
            if (g.At(ri.destX, ri.destZ) == KbCell.Partial) bad.Add("item rests on sandbag");
            Check("fx_never_rests_on_sandbag", new[] { "people_thrown_three_cells", "goods_arc_spin_rebound", "inv_kernel" }, "fixed", bad, 2,
                "a throw ending on a sandbag backs to the last free cell (pawn and item)");
        }
        // sandbags stop a throw (setting on): pawns only
        {
            var bad = new List<string>();
            var s2 = S(); s2.sandbagsStop = true;
            var g = new Grid().Set(12, 10, KbCell.Partial);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 4, KbKind.Pawn, Colonist, s2);
            if (r.stop != KbStop.PartialCover || r.destX != 11) bad.Add("pawn sandbag-stop: stop " + r.stop + " dest " + r.destX);
            if (!(r.impact > 0f)) bad.Add("sandbag stop no impact");
            var ri = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 4, KbKind.Item, 1f, s2);
            if (ri.destX != 14) bad.Add("goods stopped by sandbags with setting on: dest " + ri.destX);
            Check("fx_sandbags_stop_setting_pawns_only", new[] { "settings_scale_and_switch", "goods_arc_spin_rebound", "inv_kernel" }, "fixed", bad, 3,
                "sandbagsStop on: pawn stops before the sandbag with an impact; goods still fly over");
        }
        // heavier_flies_less + power
        {
            var bad = new List<string>();
            var info = new StringBuilder();
            foreach (float d in new[] { 0f, 0.5f, 1f, 1.5f, 2f })
            {
                int rr = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, Rat, s), cc = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, Colonist, s), mm = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, Muffalo, s);
                info.Append("d" + d + ":" + rr + "/" + cc + "/" + mm + " ");
                if (!(rr >= cc && cc >= mm)) bad.Add("d" + d + " rat " + rr + " col " + cc + " muf " + mm);
            }
            int r1 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Rat, s), c1 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Colonist, s), m1 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Muffalo, s);
            if (!(r1 > c1 && c1 > m1 && m1 >= 1)) bad.Add("strict order at d1 fails: " + r1 + "/" + c1 + "/" + m1);
            if (RM_KnockbackMath.Eligible(KbKind.Pawn, 160f, s)) bad.Add("a 160 kg creature eligible");
            if (!RM_KnockbackMath.Eligible(KbKind.Pawn, Muffalo, s)) bad.Add("muffalo 144 not eligible");
            if (RM_KnockbackMath.Eligible(KbKind.Pawn, Thrumbo, s)) bad.Add("thrumbo eligible");
            float two = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
            int r2 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, two, Rat, s), c2 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, two, Colonist, s), m2 = RM_KnockbackMath.ThrowCells(1f, MortarRadius, two, Muffalo, s);
            if (two != 2f) bad.Add("DamageRatio(100,50) = " + two);
            if (!(r2 > r1 && c2 > c1 && m2 > m1)) bad.Add("twice damage not farther: " + r2 + "/" + c2 + "/" + m2 + " vs " + r1 + "/" + c1 + "/" + m1);
            Check("fx_heavier_flies_less_and_power", new[] { "heavier_flies_less", "the_spared", "inv_kernel", "inv_creature_mass_limit", "inv_blast_power_damage" }, "fixed", bad, 12,
                "rat/colonist/muffalo by distance " + info + "; d1 x2 damage " + r2 + "/" + c2 + "/" + m2 + "; thrumbo and 160 kg spared");
        }
        // blast power: normal damage is neutral; switch off ignores damage; negative counts 0; reference percent
        {
            var bad = new List<string>();
            if (RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true) != 1f) bad.Add("normal damage not 1");
            if (RM_KnockbackMath.DamageRatio(500f, 50f, 100f, false) != 1f) bad.Add("switch off not 1");
            if (RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true) != 0f) bad.Add("negative damage not 0");
            if (RM_KnockbackMath.DamageRatio(50f, 0f, 100f, true) != 1f) bad.Add("no reference not 1");
            if (Math.Abs(RM_KnockbackMath.DamageRatio(50f, 50f, 200f, true) - 0.5f) > 1e-6) bad.Add("ref 200% not 0.5");
            if (RM_KnockbackMath.ThrowCells(1f, MortarRadius, RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true), Colonist, s) != 3) bad.Add("mortar 50 dmg with power on not 3");
            Check("fx_blast_power_ratio", new[] { "heavier_flies_less", "inv_blast_power_damage", "settings_scale_and_switch" }, "fixed", bad, 6,
                "ratio 1 at normal damage, 1 with the switch off or no reference, 0 for negative, halves at 200% reference; mortar keeps 3");
        }
        // the_spared
        {
            var bad = new List<string>();
            if (!RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s)) bad.Add("150 kg exactly is not heavier than 150, must throw");
            if (RM_KnockbackMath.Eligible(KbKind.Pawn, 150.01f, s)) bad.Add("150.01 kg thrown");
            if (!RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, s)) bad.Add("100 kg living pawn spared by the goods limit");
            if (RM_KnockbackMath.Eligible(KbKind.Item, 75.5f, s)) bad.Add("75.5 kg good thrown");
            if (RM_KnockbackMath.Eligible(KbKind.Corpse, 100f, s)) bad.Add("100 kg corpse thrown");
            if (!RM_KnockbackMath.Eligible(KbKind.Corpse, 75f, s)) bad.Add("75 kg corpse spared");
            var c216 = new KbConfig { massLimitOverride = 216f };
            var sg = KbLookup.Apply(s, c216, 6, 1f);
            if (!RM_KnockbackMath.Eligible(KbKind.Pawn, 200f, sg)) bad.Add("grav-ram 216: 200 kg spared");
            if (RM_KnockbackMath.Eligible(KbKind.Pawn, 220f, sg)) bad.Add("grav-ram 216: 220 kg thrown");
            if (RM_KnockbackMath.Eligible(KbKind.Corpse, 100f, sg)) bad.Add("grav-ram override applied to a corpse");
            if (s.creatureMassLimit != 150f) bad.Add("Apply mutated the shared settings");
            int rim = RM_KnockbackMath.ThrowCells(2.85f, MortarRadius, 1f, Colonist, s);
            if (rim != 0) bad.Add("rim throw " + rim);
            int beyond = RM_KnockbackMath.ThrowCells(5f, MortarRadius, 1f, Rat, s);
            if (beyond != 0) bad.Add("beyond radius " + beyond);
            Check("fx_the_spared_limits", new[] { "the_spared", "inv_mass_limit_skip", "inv_creature_mass_limit", "inv_big_corpse_spared", "inv_too_weak_skip", "per_weapon_tuning" }, "fixed", bad, 12,
                "150 kg creature line inclusive, goods/corpse 75 kg, a living pawn never weighed by the goods limit, grav-ram 216 for pawns only, rim and outside radius 0");
        }
        // recovery_immunity
        {
            var bad = new List<string>();
            if (KbImmunity.CanLaunch(100, 100, 190, 120)) bad.Add("during stun");
            if (KbImmunity.CanLaunch(309, 100, 190, 120)) bad.Add("stun ended, recovery not");
            if (!KbImmunity.CanLaunch(310, 100, 190, 120)) bad.Add("after stun + recovery refused");
            if (KbImmunity.CanLaunch(219, 100, 50, 120)) bad.Add("stun shorter than landing: window must count from landing");
            if (!KbImmunity.CanLaunch(100, 100, 190, 0)) bad.Add("window 0 should allow");
            Check("fx_recovery_immunity", new[] { "recovery_immunity", "inv_recovery" }, "fixed", bad, 5,
                "no launch until max(landing, stun end) + window; window 0 allows");
        }
        // wall_stops_dead
        {
            var bad = new List<string>();
            var g = new Grid().Set(12, 10, KbCell.Wall);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r.stop != KbStop.Wall || r.destX != 11 || r.cellsTravelled != 1) bad.Add("wall: stop " + r.stop + " dest " + r.destX);
            if (Math.Abs(r.impact - 8f) > 1e-4) bad.Add("impact " + r.impact + " want 4/cell x 2 cells = 8");
            var g2 = new Grid().Set(11, 10, KbCell.Wall);
            var r2 = RM_KnockbackMath.Resolve(g2, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r2.destX != 10 || r2.cellsTravelled != 0 || r2.stop != KbStop.Wall || !(r2.impact > 0)) bad.Add("adjacent wall: dest " + r2.destX + " stop " + r2.stop + " impact " + r2.impact);
            // corner cut
            var g3 = new Grid().Set(11, 10, KbCell.Wall).Set(10, 11, KbCell.Wall);
            var r3 = RM_KnockbackMath.Resolve(g3, 10, 10, 1f, 1f, 3, KbKind.Pawn, Colonist, s);
            if (r3.cellsTravelled != 0) bad.Add("cut a wall corner diagonally: travelled " + r3.cellsTravelled);
            var s0 = S(); s0.impactEnabled = false;
            if (RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s0).impact != 0f) bad.Add("impact with impact off");
            Check("fx_wall_stops_dead", new[] { "wall_stops_dead", "inv_kernel", "settings_scale_and_switch" }, "fixed", bad, 5,
                "stops on the cell before the wall, impact 4/cell for the cells not flown, no corner cutting, none with impact off");
        }
        // pawn_hits_pawn_stops
        {
            var bad = new List<string>();
            var g = new Grid().Set(12, 10, KbCell.Pawn);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r.stop != KbStop.Pawn || r.destX != 11 || !r.hitOther || r.otherX != 12) bad.Add("pawn: stop " + r.stop + " dest " + r.destX);
            if (!(r.impact > 0f) || !(r.otherImpact > 0f)) bad.Add("no impact on either");
            var ri = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Item, 1f, s);
            if (ri.destX != 13 || ri.impact != 0f) bad.Add("goods stopped by a pawn in the kernel: dest " + ri.destX);
            Check("fx_pawn_hits_pawn_stops", new[] { "pawn_hits_pawn_stops", "inv_kernel" }, "fixed", bad, 3,
                "thrown pawn stops before the other pawn; both take an impact (split " + r.impact + "/" + r.otherImpact + " of a wall's 8); goods pass a pawn's cell in the kernel");
        }
        // doors and deep water
        {
            var bad = new List<string>();
            var g = new Grid().Set(12, 10, KbCell.Door);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r.stop != KbStop.Door || !r.hitDoor || r.doorX != 12 || r.destX != 11 || !(r.impact > 0)) bad.Add("door: " + r.stop + " dest " + r.destX);
            var s0 = KbLookup.Apply(s, new KbConfig { impactFactor = 0f }, 6, 1f);
            var r0 = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s0);
            if (r0.impact != 0f || r0.destX != 11) bad.Add("impact factor 0 still hits: " + r0.impact);
            var gw = new Grid().Set(12, 10, KbCell.Water);
            var rw = RM_KnockbackMath.Resolve(gw, 10, 10, 1f, 0f, 4, KbKind.Pawn, Colonist, s);
            if (rw.stop != KbStop.Water || rw.destX != 11) bad.Add("water: " + rw.stop + " dest " + rw.destX);
            var rwi = RM_KnockbackMath.Resolve(gw, 10, 10, 1f, 0f, 4, KbKind.Item, 1f, s);
            if (gw.At(rwi.destX, rwi.destZ) == KbCell.Water || rwi.hasBlock) bad.Add("goods into deep water or rebounding off it");
            Check("fx_doors_and_deep_water_stop", new[] { "doors_and_deep_water_stop", "per_weapon_tuning", "goods_arc_spin_rebound", "inv_kernel" }, "fixed", bad, 4,
                "door stops with a door hit and impact (0 at impact factor 0); water stops on the last standable cell, goods never into it");
        }
        // shield
        {
            var bad = new List<string>();
            float e = KbShield.EnergyAfter(1f, 1f, 10f, 0.033f);
            if (!(e < 1f)) bad.Add("no extra charge paid: " + e);
            if (KbShield.EnergyAfter(1f, 0f, 10f, 0.033f) != 1f) bad.Add("force 0 costs charge");
            if (KbShield.EnergyAfter(1f, 2f, 10f, 0.033f) >= e) bad.Add("more force not dearer");
            if (KbShield.EnergyAfter(0.1f, 1f, 10f, 0.033f) >= 0f) bad.Add("a near-empty belt not broken");
            Check("fx_shield_extra_charge", new[] { "shield_belt_holds", "inv_shield" }, "fixed", bad, 4, "a belt pays force x 10 x energy loss; 1 force at 0.033 loss -> " + e);
        }
        // goods fly wild, rebound ~70%
        {
            var bad = new List<string>();
            var info = new StringBuilder();
            foreach (float m in new[] { 0.5f, 5f, 20f, 70f })
                foreach (float d in new[] { 0.5f, 1f, 1.5f })
                {
                    int p = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, m, s), w = RM_KnockbackMath.WildCells(d, MortarRadius, 1f, m, s, Wild);
                    if (w < p) bad.Add("wild shorter m" + m + " d" + d);
                    if (w > s.maxCells) bad.Add("wild over cap");
                    if (m == 70f) info.Append("d" + d + ":" + p + "->" + w + " ");
                }
            if (RM_KnockbackMath.WildCells(1f, MortarRadius, 1f, 70f, s, 1f) != RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, 70f, s)) bad.Add("wild 1 != kernel");
            int left = 6, n = 0, total = 0;
            var chain = new List<int>();
            while (left > 0 && n < 50) { left = RM_KnockbackMath.ReboundCells(left, 70f); chain.Add(left); total += left; n++; }
            if (n >= 50) bad.Add("rebound chain never ends at 70%");
            if (RM_KnockbackMath.ReboundCells(10, 70f) != 7) bad.Add("10 left at 70% != 7");
            if (RM_KnockbackMath.ReboundCells(1, 70f) != 0) bad.Add("1 left at 70% rebounds");
            if (RM_KnockbackMath.ReboundCells(5, 0f) != 0) bad.Add("keep 0 rebounds");
            if (RM_KnockbackMath.ReboundCells(5, 100f) != 5) bad.Add("keep 100 loses cells");
            if (RM_KnockbackMath.ReboundCells(5, 150f) != 5) bad.Add("keep 150 gains cells");
            Check("fx_goods_wild_and_rebound", new[] { "goods_arc_spin_rebound", "inv_goods_fly" }, "fixed", bad, 18,
                "70 kg good plain->wild " + info + "; rebound chain from 6 at 70%: " + string.Join(",", chain));
            // how close to 1.6 is "about 1.6 times as far"? INFO
            var ratios = new List<double>();
            for (float d = 0f; d < 2.9f; d += 0.1f)
                foreach (float m in new[] { 1f, 10f, 30f, 70f })
                {
                    int p = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, m, s), w = RM_KnockbackMath.WildCells(d, MortarRadius, 1f, m, s, Wild);
                    if (p > 0 && w < s.maxCells) ratios.Add(w / (double)p);
                }
            Row("info_wild_ratio_whole_cells", new[] { "goods_arc_spin_rebound" }, "info", "INFO", ratios.Count,
                "uncapped wild/plain ratios on whole cells: min " + ratios.Min().ToString("0.00") + " max " + ratios.Max().ToString("0.00") + " mean " + ratios.Average().ToString("0.00"));
        }
        // rebound reflection
        {
            var bad = new List<string>();
            var g = new Grid().Set(13, 10, KbCell.Wall);
            var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 5, KbKind.Item, 1f, s);
            if (!RM_KnockbackMath.Reflect(g, r, 1f, 0f, out float rx, out float rz) || rx != -1f || rz != 0f) bad.Add("straight wall reflect " + rx + "," + rz);
            var gd = new Grid().Set(13, 10, KbCell.Door);
            var rd = RM_KnockbackMath.Resolve(gd, 10, 10, 1f, 0f, 5, KbKind.Item, 1f, s);
            if (!RM_KnockbackMath.Reflect(gd, rd, 1f, 0f, out rx, out rz) || rx != -1f) bad.Add("closed door no rebound");
            // diagonal into a wall face along z: flip z only
            var gz = new Grid();
            for (int x = 0; x < 40; x++) gz.Set(x, 13, KbCell.Wall);
            var rz2 = RM_KnockbackMath.Resolve(gz, 10, 10, 1f, 1f, 5, KbKind.Item, 1f, s);
            if (!RM_KnockbackMath.Reflect(gz, rz2, 1f, 1f, out rx, out rz) || rx != 1f || rz != -1f) bad.Add("diag into z-wall -> " + rx + "," + rz + " stop " + rz2.stop);
            var ro = RM_KnockbackMath.Resolve(new Grid(), 10, 10, 1f, 0f, 3, KbKind.Item, 1f, s);
            if (RM_KnockbackMath.Reflect(new Grid(), ro, 1f, 0f, out rx, out rz)) bad.Add("reflect without a hit");
            Check("fx_reflect", new[] { "goods_arc_spin_rebound", "inv_goods_fly" }, "fixed", bad, 4, "wall and closed door reflect the struck axis; a diagonal into a long wall flips only z; none without a hit");
        }
        // pits
        {
            var bad = new List<string>();
            var g = new Grid().Set(12, 10, KbCell.Pit).Set(13, 10, KbCell.Pit);
            foreach (KbKind k in new[] { KbKind.Pawn, KbKind.Item, KbKind.Corpse })
            {
                var r = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 5, k, k == KbKind.Pawn ? Colonist : 5f, s);
                if (r.stop != KbStop.Pit || r.destX != 12) bad.Add(k + " pit: " + r.stop + " dest " + r.destX);
            }
            var so = S(); so.intoPits = false;
            var r2 = RM_KnockbackMath.Resolve(g, 10, 10, 1f, 0f, 5, KbKind.Pawn, Colonist, so);
            if (r2.destX != 11 || g.At(r2.destX, r2.destZ) == KbCell.Pit) bad.Add("intoPits off: entered pit");
            var gc = new Grid().Set(13, 10, KbCell.CoveredPit);
            var r3 = RM_KnockbackMath.Resolve(gc, 10, 10, 1f, 0f, 3, KbKind.Pawn, Colonist, s);
            if (r3.destX != 13) bad.Add("landing on a covered cell: dest " + r3.destX);
            Check("fx_pits_stop_inside_first_open_cell", new[] { "thrown_into_pit_falls", "inv_kernel", "inv_pits_receive", "settings_scale_and_switch" }, "fixed", bad, 5,
                "pawn, good and corpse stop in the first open pit cell (never across); intoPits off makes the pit a wall; a throw may end on a covered cell (falls through game-side)");
            var r4 = RM_KnockbackMath.Resolve(gc, 10, 10, 1f, 0f, 5, KbKind.Pawn, Colonist, s);
            Row("info_covered_pit_crossed_midflight", new[] { "thrown_into_pit_falls", "blast_breaks_pit_cover" }, "info", "INFO", 1,
                "a throw of 5 passes a covered pit cell 3 cells out and lands at x" + r4.destX + " (kernel treats a cover as ground; the cover inside the blast radius is broken game-side first)");
        }
        // closed containers
        {
            var bad = new List<string>();
            if (!RM_KnockbackMath.GoodsHeld(true, true, false)) bad.Add("closed container does not hold");
            if (RM_KnockbackMath.GoodsHeld(true, false, false)) bad.Add("open shelf holds");
            if (RM_KnockbackMath.GoodsHeld(false, true, false)) bad.Add("not on storage held");
            if (!RM_KnockbackMath.GoodsHeld(true, false, true)) bad.Add("old rule on: open shelf should hold");
            var info = new StringBuilder();
            foreach (float m in new[] { 20f, 60f, 120f, 250f, 251f, 600f })
            {
                int c = RM_KnockbackMath.ContainerThrowCells(true, m, 250f, 1f, MortarRadius, 1f, s);
                info.Append(m + "kg:" + c + " ");
                if (m <= 250f && (c < 1 || c > s.maxCells)) bad.Add("container " + m + " kg beside a mortar plans " + c + " (want a short throw >= 1)");
                if (m > 250f && c != 0) bad.Add("over-limit container plans " + c);
                if (c > RM_KnockbackMath.WildCells(1f, MortarRadius, 1f, m, s, Wild) && m <= 75f) bad.Add("container farther than the same mass loose");
            }
            if (RM_KnockbackMath.ContainerThrowCells(false, 20f, 250f, 1f, MortarRadius, 1f, s) != 0) bad.Add("2x1 container thrown");
            foreach (KbCell c in Enum.GetValues(typeof(KbCell)))
                if (RM_KnockbackMath.ShoveCellFree(c, false) != (c == KbCell.Open)) bad.Add("shove cell " + c);
            if (RM_KnockbackMath.ShoveCellFree(KbCell.Open, true)) bad.Add("shove onto a cell with things");
            Check("fx_closed_container_holds_and_short_throw", new[] { "closed_container_holds", "open_shelf_scatters", "inv_closed_guard", "inv_container_shove", "inv_shelf_skip" }, "fixed", bad, 16,
                "closed holds, open never (unless the old rule is on); beside a mortar " + info + "; only open empty ground is a shove cell");
        }
        // jolt
        {
            var bad = new List<string>();
            float max = 0f;
            for (int t = -2; t < 30; t++)
            {
                RM_KnockbackMath.JoltOffset(t, 24, 0.15f, 3f, 4f, out float ox, out float oz);
                float m = (float)Math.Sqrt(ox * ox + oz * oz);
                max = Math.Max(max, m);
                if (m > 0.15f + 1e-5f) bad.Add("t" + t + " offset " + m);
                if ((t < 0 || t >= 24) && m != 0f) bad.Add("t" + t + " moves outside the jolt");
                if (Math.Abs(ox * 4f - oz * 3f) > 1e-4f) bad.Add("t" + t + " off the blast line");
            }
            RM_KnockbackMath.JoltOffset(3, 24, 0.15f, 0f, 0f, out float zx, out float zz);
            if (float.IsNaN(zx) || float.IsNaN(zz)) bad.Add("NaN on zero direction");
            if (!(max > 0f)) bad.Add("jolt never moves");
            Check("fx_jolt_bounded", new[] { "closed_container_holds", "inv_container_shove" }, "fixed", bad, 33, "jolt along the blast line, max " + max.ToString("0.000") + " of 0.15, still outside its window, no NaN");
        }
        // heavy knock
        {
            var bad = new List<string>();
            bool h = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 10f, 10f, 2f, 5f, 0.5f, 30, out float dmg, out int st);
            if (!h || dmg < 2f || dmg > 5f || st != 30) bad.Add("10 kg stack: " + h + " " + dmg + " " + st);
            if (RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 9.9f, 10f, 2f, 5f, 0.5f, 30, out dmg, out st) || dmg != 0f) bad.Add("light goods knock");
            if (RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 60f, 10f, 2f, 5f, 0.5f, 30, out dmg, out st)) bad.Add("corpse knocks");
            if (RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 60f, 10f, 2f, 5f, 0.5f, 30, out dmg, out st)) bad.Add("rule off knocks");
            if (RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 60f, 10f, 2f, 5f, 0.5f, 30, out dmg, out st)) bad.Add("no person knocks");
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 60f, 10f, 2f, 5f, 0f, 30, out float lo, out st);
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 60f, 10f, 2f, 5f, 0.99999f, 30, out float hi, out st);
            if (lo != 2f || hi > 5f || hi < 4.99f) bad.Add("damage range " + lo + ".." + hi);
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 60f, 10f, 5f, 2f, 0.5f, -3, out float inv, out st);
            if (inv != 5f || st != 0) bad.Add("inverted range / negative stagger " + inv + " " + st);
            Check("fx_heavy_stack_knocks", new[] { "heavy_stack_knocks", "inv_heavy_knock" }, "fixed", bad, 8, "a stack of 10 kg or more hits 2..5 blunt with 30 ticks stagger; lighter, corpse, no person or rule off passes");
        }
        // which blasts throw, lookup order
        {
            var bad = new List<string>();
            var proj = new KbConfig { force = 0f }; var wpn = new KbConfig { force = 2f }; var dd = new KbConfig { force = 0.5f };
            if (KbLookup.Resolve(proj, wpn, dd, true, 1f).force != 0f) bad.Add("projectile 0 not first");
            if (KbLookup.Resolve(null, wpn, dd, true, 1f).force != 2f) bad.Add("weapon not second");
            if (KbLookup.Resolve(null, null, dd, true, 0.3f).force != 0.5f) bad.Add("unpatched percent stacked on a tuned type");
            var un = KbLookup.Resolve(null, null, null, true, 0.4f);
            if (un.force != 0.4f || un.source != "unpatched") bad.Add("unpatched harmful " + un.force);
            if (KbLookup.Resolve(null, null, null, false, 1f).force != 0f) bad.Add("harmless burst throws");
            int bomb = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 1f, Colonist, s), fire = RM_KnockbackMath.ThrowCells(1f, MortarRadius, 0.5f, Colonist, s);
            if (fire < 1 || fire >= bomb) bad.Add("fire " + fire + " vs bomb " + bomb);
            int maxdiff = 0;
            for (float d = 0; d < 2.9f; d += 0.05f) foreach (float m in new[] { 1f, 30f, 70f, 140f })
                {
                    int b = RM_KnockbackMath.ThrowCells(d, MortarRadius, 1f, m, s), f = RM_KnockbackMath.ThrowCells(d, MortarRadius, 0.5f, m, s);
                    if (b < s.maxCells) maxdiff = Math.Max(maxdiff, (int)Math.Ceiling(Math.Abs(f - b / 2.0)));
                    if (f > b) bad.Add("fire farther than bomb d" + d + " m" + m);
                }
            if (maxdiff > 1) bad.Add("fire off half by " + maxdiff);
            if (KbLookup.Resolve(null, null, new KbConfig { force = 0f }, true, 1f).force != 0f) bad.Add("EMP 0 overridden");
            Check("fx_every_harmful_blast_and_lookup", new[] { "every_harmful_blast_throws", "per_weapon_tuning", "only_explosions_throw", "inv_which_blasts", "inv_weapon_ext_fields" }, "fixed", bad, 9,
                "projectile > weapon > damage type, whole; unpatched only for an untuned harmful type; harmless 0; fire at 0.5 beside a colonist " + fire + " vs bomb " + bomb + ", within 1 cell of half when uncapped");
        }
        // caps
        {
            var bad = new List<string>();
            if (RM_KnockbackMath.CapFor(0, 6, 0.5f) != 6) bad.Add("scale shortened the global max");
            if (RM_KnockbackMath.CapFor(4, 6, 0.5f) != 2) bad.Add("own 4 x 0.5 != 2");
            if (RM_KnockbackMath.CapFor(1, 6, 0.25f) != 1) bad.Add("own cap below 1");
            if (RM_KnockbackMath.CapFor(8, 6, 1f) != 8) bad.Add("own max 8 not honoured over the global 6");
            var sg = KbLookup.Apply(s, new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 0.5f);
            if (sg.maxCells != 2) bad.Add("gas exact cap rescaled: " + sg.maxCells);
            var sw = KbLookup.Apply(s, new KbConfig { ownCap = 2 }, 6, 0.5f);
            if (sw.maxCells != 1) bad.Add("weapon cap 2 x 0.5 = " + sw.maxCells);
            int capped = RM_KnockbackMath.ThrowCells(0f, MortarRadius, 3f, Rat, KbLookup.Apply(s, new KbConfig { ownCap = 2 }, 6, 1f));
            if (capped != 2) bad.Add("own max does not cap: " + capped);
            Check("fx_caps", new[] { "per_weapon_tuning", "inv_caps", "inv_gas_chain" }, "fixed", bad, 7, "own max caps (scaled, min 1), 0 = global, scale never touches the global, gas cap exact");
        }
        // Prioritise: nothing lost, order
        {
            var bad = new List<string>();
            var all = new List<KbCandidate> {
                new KbCandidate { index = 0, kind = KbKind.Item, distance = 0.5f }, new KbCandidate { index = 1, kind = KbKind.Pawn, distance = 2f },
                new KbCandidate { index = 2, kind = KbKind.Corpse, distance = 1f }, new KbCandidate { index = 3, kind = KbKind.Pawn, distance = 1f } };
            var k = RM_KnockbackMath.Prioritise(all, -1);
            if (k.Count != 4) bad.Add("uncapped dropped " + (4 - k.Count));
            if (string.Join(",", k.Select(x => x.index)) != "3,1,2,0") bad.Add("order " + string.Join(",", k.Select(x => x.index)));
            if (RM_KnockbackMath.Prioritise(all, 2).Count != 2) bad.Add("cap 2");
            Check("fx_prioritise_order", new[] { "every_good_moves", "inv_kernel" }, "fixed", bad, 3, "pawns, corpses, items nearest first; cap -1 keeps all");
        }
        // ledger
        {
            var bad = new List<string>();
            var L = new KbExplosionLedger(600);
            if (!L.TryAdd(1, 7, 590)) bad.Add("first add refused");
            if (L.TryAdd(1, 7, 610)) bad.Add("repeat across a rotation accepted");
            L.AddLaunched(1, 620);  // ticks only move forward (a backwards clock clears the ledger by design)
            if (L.Launched(1, 1100) != 1) bad.Add("launch count lost within window");
            if (L.TryAdd(1, 7, 1150)) bad.Add("repeat at +560 accepted");
            if (!L.TryAdd(1, 7, 1800)) bad.Add("entry not dropped after 2 windows");
            Check("fx_explosion_ledger_window", new[] { "every_good_moves", "recovery_immunity", "inv_kernel", "inv_hook" }, "fixed", bad, 5, "dedupe and launch count survive a generation rotation; gone after two windows");
        }
        // frame stats
        {
            var bad = new List<string>();
            var g = KbFrameStats.Summarize(new[] { 10f, 60f, 12f, 30f }, new[] { false, true, false, false }, new[] { 1, 5, 3, 2 }, 4, 0.112f);
            if (g.worstMs != 30f) bad.Add("worst " + g.worstMs + " (paused 60 counted?)");
            if (g.maxInAir != 5) bad.Add("maxInAir " + g.maxInAir);
            if (KbFrameStats.WithinBudget(g, 50f, out _) != false) bad.Add("paused 1 of 4 rows not refused (>10%)");
            var g2 = KbFrameStats.Summarize(Enumerable.Repeat(16f, 99).Concat(new[] { 51f }).ToArray(), new bool[100], new int[100], 100, (99 * 16f + 51f) / 1000f);
            if (KbFrameStats.WithinBudget(g2, 50f, out _)) bad.Add("51 ms frame within 50 budget");
            if (!KbFrameStats.SelfCheck(g2, 40f, out string why)) bad.Add("selfcheck refused a good run: " + why);
            if (KbFrameStats.SelfCheck(g2, 60f, out _)) bad.Add("selfcheck passed without the slept frame");
            var g3 = KbFrameStats.Summarize(new float[0], new bool[0], new int[0], 0, 0f);
            if (KbFrameStats.WithinBudget(g3, 50f, out _) || KbFrameStats.SelfCheck(g3, 1f, out _)) bad.Add("no rows passes");
            Check("fx_frame_stats", new[] { "frame_time_probe", "barrage_frame_budget" }, "fixed", bad, 6, "worst = max of unpaused rows; a 51 ms frame fails 50; empty or paused runs refused; selfcheck sees the slept frame");
        }
    }

    // ---------------------------------------------------------------- random
    static KbCell RandCell(Random rng)
    {
        int r = rng.Next(100);
        if (r < 62) return KbCell.Open;
        if (r < 70) return KbCell.Wall;
        if (r < 74) return KbCell.Door;
        if (r < 82) return KbCell.Partial;
        if (r < 87) return KbCell.Pawn;
        if (r < 91) return KbCell.Pit;
        if (r < 95) return KbCell.CoveredPit;
        return KbCell.Water;
    }

    static string Shrink(Grid g, int sx, int sz, List<(int x, int z)> path)
    {
        var sb = new StringBuilder();
        foreach (var p in path) sb.Append(g.At(p.x, p.z).ToString()[0]);
        return sb.ToString();
    }

    static void RandomRows(int seed)
    {
        var rng = new Random(seed);
        var bad = new List<string>();
        int cases = 0;
        string firstShrunk = null;
        for (int t = 0; t < 20000; t++)
        {
            var g = new Grid { W = 16, H = 16 };
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) { var c = RandCell(rng); if (c != KbCell.Open) g.Set(x, z, c); }
            int sx = rng.Next(16), sz = rng.Next(16);
            g.Set(sx, sz, KbCell.Open);
            double a = rng.NextDouble() * Math.PI * 2;
            float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
            int cells = rng.Next(0, 11);
            var kind = (KbKind)rng.Next(3);
            var s = S();
            s.sandbagsStop = rng.Next(4) == 0; s.intoPits = rng.Next(4) != 0; s.impactEnabled = rng.Next(5) != 0;
            float mass = kind == KbKind.Pawn ? 20f + (float)rng.NextDouble() * 130f : 0.2f + (float)rng.NextDouble() * 70f;
            var r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
            var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
            cases++;
            var why = new List<string>();
            if (path.Count != (cells > 0 ? cells : 0)) why.Add("path " + path.Count + " != " + cells);
            for (int i = 0; i < path.Count; i++)
            {
                var prev = i == 0 ? (sx, sz) : path[i - 1];
                if (Cheb(prev.Item1, prev.Item2, path[i].x, path[i].z) != 1) why.Add("path jumps at " + i);
            }
            if (r.cellsTravelled < 0 || r.cellsTravelled > cells) why.Add("travelled " + r.cellsTravelled);
            if (Cheb(sx, sz, r.destX, r.destZ) != r.cellsTravelled) why.Add("dest cheb " + Cheb(sx, sz, r.destX, r.destZ) + " != travelled " + r.cellsTravelled);
            if (r.cellsTravelled > 0 && (path[r.cellsTravelled - 1].x != r.destX || path[r.cellsTravelled - 1].z != r.destZ)) why.Add("dest off the line");
            var dc = g.At(r.destX, r.destZ);
            if (r.cellsTravelled > 0 && (dc == KbCell.Wall || dc == KbCell.Door || dc == KbCell.Water || dc == KbCell.OutOfBounds || dc == KbCell.Partial || (dc == KbCell.Pawn && kind == KbKind.Pawn)))
                why.Add("rests on " + dc);
            if (!s.intoPits && dc == KbCell.Pit && r.cellsTravelled > 0) why.Add("into a pit with pits off");
            // nothing crosses a solid, a pit or water; a pawn crosses no pawn
            for (int i = 0; i < r.cellsTravelled - 1; i++)
            {
                var c = g.At(path[i].x, path[i].z);
                if (c == KbCell.Pit || c == KbCell.Wall || c == KbCell.Door || c == KbCell.Water || (c == KbCell.Pawn && kind == KbKind.Pawn)) why.Add("crossed " + c + " at " + i);
            }
            // first blocking cell along the path must stop the throw at or before it
            if (kind != KbKind.Pawn && (r.impact != 0f || r.otherImpact != 0f)) why.Add("goods took impact");
            if (!s.impactEnabled && r.impact != 0f) why.Add("impact with impact off");
            if (r.impact < 0f || float.IsNaN(r.impact)) why.Add("bad impact");
            if (why.Count > 0)
            {
                if (firstShrunk == null) firstShrunk = "kind " + kind + " cells " + cells + " path " + Shrink(g, sx, sz, path) + " -> " + string.Join(";", why);
                bad.Add("t" + t + ": " + string.Join(";", why));
            }
        }
        Row("rnd_resolve_invariants", new[] { "inv_kernel", "wall_stops_dead", "pawn_hits_pawn_stops", "doors_and_deep_water_stop", "thrown_into_pit_falls", "no_teleport" }, "random",
            bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed " + seed + "; 20000 random 16x16 grids, every kind, sandbag/pit/impact switches random: path = cells grid steps, dest on the line at Chebyshev = travelled, never rests on a solid/water/sandbag/pawn, never crosses a pit/solid/water" +
            (bad.Count == 0 ? "" : "; FAIL " + bad.Count + "; first shrunk: " + firstShrunk));

        // monotonic: heavier never farther, closer never shorter, more force never shorter
        var bad2 = new List<string>();
        int c2 = 0;
        for (int t = 0; t < 50000; t++)
        {
            var s = S();
            s.globalMultiplier = (float)rng.NextDouble() * 3f; s.maxCells = rng.Next(1, 11);
            float r = 0.5f + (float)rng.NextDouble() * 9f, d = (float)rng.NextDouble() * r * 1.2f, f = (float)rng.NextDouble() * 3f;
            float m1 = 0.1f + (float)rng.NextDouble() * 300f, m2 = m1 + (float)rng.NextDouble() * 200f;
            int a = RM_KnockbackMath.ThrowCells(d, r, f, m1, s), b = RM_KnockbackMath.ThrowCells(d, r, f, m2, s);
            int near = RM_KnockbackMath.ThrowCells(d * 0.5f, r, f, m1, s), more = RM_KnockbackMath.ThrowCells(d, r, f * 1.5f, m1, s);
            int w = RM_KnockbackMath.WildCells(d, r, f, m1, s, Wild);
            c2++;
            if (b > a) bad2.Add("heavier farther m" + m1 + "->" + m2 + " " + a + "<" + b);
            if (near < a) bad2.Add("closer shorter");
            if (more < a) bad2.Add("more force shorter");
            if (w < a) bad2.Add("wild shorter");
            if (a < 0 || a > s.maxCells || w > s.maxCells) bad2.Add("cap broken");
        }
        Row("rnd_monotone_mass_distance_force", new[] { "heavier_flies_less", "inv_kernel", "goods_arc_spin_rebound" }, "random", bad2.Count == 0 ? "PASS" : "FAIL", c2,
            "seed " + seed + " (continued); heavier never farther, nearer never shorter, more force never shorter, wild never shorter, within cap" + (bad2.Count == 0 ? "" : "; FAIL " + bad2.Count + ": " + string.Join(" | ", bad2.Take(3))));

        // conservation in Prioritise
        var bad3 = new List<string>();
        for (int t = 0; t < 3000; t++)
        {
            int n = rng.Next(0, 80);
            var all = new List<KbCandidate>();
            for (int i = 0; i < n; i++) all.Add(new KbCandidate { index = i, kind = (KbKind)rng.Next(3), distance = (float)Math.Round(rng.NextDouble() * 5, 1) });
            int cap = rng.Next(-1, 90);
            var k = RM_KnockbackMath.Prioritise(all, cap);
            int want = cap < 0 ? n : Math.Min(n, cap);
            if (k.Count != want) bad3.Add("count " + k.Count + " want " + want);
            if (k.Select(x => x.index).Distinct().Count() != k.Count) bad3.Add("duplicate");
            if (all.Count != n) bad3.Add("input mutated");
        }
        Row("rnd_prioritise_conserves", new[] { "every_good_moves", "inv_kernel" }, "random", bad3.Count == 0 ? "PASS" : "FAIL", 3000,
            "seed " + seed + " (continued); no duplicates, nothing created, cap -1 keeps all" + (bad3.Count == 0 ? "" : "; " + string.Join(" | ", bad3.Take(3))));

        // ledger vs a reference model
        var bad4 = new List<string>();
        int c4 = 0;
        for (int t = 0; t < 400; t++)
        {
            int w = rng.Next(1, 700);
            var L = new KbExplosionLedger(w);
            var seen = new Dictionary<(int, int), int>();
            int now = rng.Next(-2000, 2000);
            for (int i = 0; i < 200; i++)
            {
                now += rng.Next(0, w / 2 + 2);
                int e = rng.Next(5), th = rng.Next(5);
                bool added = L.TryAdd(e, th, now);
                c4++;
                if (seen.TryGetValue((e, th), out int at))
                {
                    int age = now - at;
                    if (added && age < w) bad4.Add("re-added at age " + age + " < window " + w);
                    if (!added && age >= 2 * w) bad4.Add("refused at age " + age + " >= 2 window " + w);
                }
                else if (!added) bad4.Add("first add refused");
                if (added) seen[(e, th)] = now;
            }
        }
        Row("rnd_ledger_window_model", new[] { "inv_kernel", "inv_hook", "every_good_moves" }, "random", bad4.Count == 0 ? "PASS" : "FAIL", c4,
            "seed " + seed + " (continued); an entry lives at least one window and never two" + (bad4.Count == 0 ? "" : "; " + bad4.Count + ": " + string.Join(" | ", bad4.Take(3))));
    }

    // ---------------------------------------------------------------- sweep: shipped settings through their ranges
    static void SweepRows()
    {
        var bad = new List<string>();
        int cases = 0;
        float[] strength = { 0f, 0.5f, 1f, 2f, 3f };
        int[] maxCells = { 1, 3, 6, 10 };
        float[] ownScale = { 0.25f, 1f, 2f };
        float[] creature = { 20f, 150f, 500f };
        float[] light = { 5f, 75f, 200f };
        float[] impact = { 0f, 4f, 15f };
        foreach (var st in strength) foreach (var mc in maxCells) foreach (var os in ownScale) foreach (var cl in creature) foreach (var ll in light) foreach (var ip in impact)
                            foreach (bool sb in new[] { false, true }) foreach (bool pit in new[] { false, true }) foreach (bool imp in new[] { false, true })
                                    {
                                        // RimMandrakeExplosiveKnockbackSettings.Kernel(KbConfig) mirrored: globals, then KbLookup.Apply
                                        var g = new KbSettings { globalMultiplier = st, maxCells = RM_KnockbackMath.CapFor(0, mc, os), creatureMassLimit = cl, lightMassLimit = ll, impactEnabled = imp, impactPerCell = ip, sandbagsStop = sb, intoPits = pit };
                                        foreach (var cfg in new[] { (KbConfig)null, new KbConfig { ownCap = 4 }, new KbConfig { ownCap = 2, scaleOwnCap = false, impactFactor = 0f } })
                                        {
                                            var k = KbLookup.Apply(g, cfg, mc, os);
                                            int cap = cfg == null ? mc : RM_KnockbackMath.CapFor(cfg.ownCap, mc, cfg.scaleOwnCap ? os : 1f);
                                            cases++;
                                            if (k.maxCells != cap) bad.Add("cap " + k.maxCells + " want " + cap);
                                            int c = RM_KnockbackMath.ThrowCells(0.5f, MortarRadius, 1f, 50f, k);
                                            if (st == 0f && c != 0) bad.Add("strength 0 throws " + c);
                                            if (c > k.maxCells) bad.Add("over cap");
                                            if (st > 0f && c == 0 && k.maxCells >= 1 && 4f * st * (1 - 0.5f / MortarRadius) * (float)Math.Sqrt(70f / 50f) >= 0.5f) bad.Add("lost a throw at strength " + st);
                                            var grid = new Grid().Set(11, 10, KbCell.Partial).Set(12, 10, KbCell.Pit).Set(10, 12, KbCell.Wall);
                                            var r = RM_KnockbackMath.Resolve(grid, 10, 10, 1f, 0f, 3, KbKind.Pawn, 70f, k);
                                            if (sb && r.destX != 10) bad.Add("sandbag stop on: dest " + r.destX);
                                            if (!sb && pit && r.destX != 12) bad.Add("into pit: dest " + r.destX);
                                            if (!sb && !pit && r.destX != 10) bad.Add("pits off: dest " + r.destX + " (sandbag backs to start)");
                                            var rw = RM_KnockbackMath.Resolve(grid, 10, 10, 0f, 1f, 3, KbKind.Pawn, 70f, k);
                                            float wantImp = imp ? ip * k.impactFactor * 2f / (float)Math.Sqrt(RM_KnockbackMath.MassScale(70f, k)) : 0f;
                                            if (Math.Abs(rw.impact - wantImp) > 1e-3f) bad.Add("impact " + rw.impact + " want " + wantImp);
                                            if (RM_KnockbackMath.Eligible(KbKind.Pawn, cl + 1f, k) || !RM_KnockbackMath.Eligible(KbKind.Pawn, cl, k)) bad.Add("creature limit " + cl);
                                            if (RM_KnockbackMath.Eligible(KbKind.Item, ll + 1f, k) || !RM_KnockbackMath.Eligible(KbKind.Corpse, ll, k)) bad.Add("goods limit " + ll);
                                            if (!RM_KnockbackMath.Eligible(KbKind.Pawn, Math.Min(cl, ll + 1f), k)) bad.Add("goods limit weighed a living pawn");
                                        }
                                    }
        Check("sweep_global_settings", new[] { "settings_scale_and_switch", "per_weapon_tuning", "the_spared", "inv_settings", "inv_caps", "inv_kernel" }, "sweep", bad, cases,
            "strength 0..3, max throw 1..10, own-cap scale 0.25..2, creature limit 20..500, goods limit 5..200, impact/cell 0..15, sandbags stop, into pits, impact on/off, three blast configs: strength 0 throws nothing, caps hold, each switch to its own off state, each limit weighs its own kind");

        // goods-side switches and ranges
        var bad2 = new List<string>();
        int c2 = 0;
        for (int keep = 0; keep <= 100; keep += 5)
            for (int left = 0; left <= 12; left++)
            {
                c2++;
                int rb = RM_KnockbackMath.ReboundCells(left, keep);
                if (rb < 0 || rb > left) bad2.Add("rebound " + rb + " from " + left);
                if (keep < 100 && left > 0 && rb >= left) bad2.Add("no loss at " + keep + "%");
                if (keep == 0 && rb != 0) bad2.Add("keep 0 rebounds");
            }
        for (float mn = 1f; mn <= 75f; mn += 7f) for (float lo = 0f; lo <= 20f; lo += 4f) for (float hi = 0f; hi <= 20f; hi += 4f) for (int stg = 0; stg <= 180; stg += 60)
                    {
                        c2++;
                        bool h = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, mn, mn, lo, hi, 0.7f, stg, out float d, out int st);
                        if (!h || d < lo || d > Math.Max(lo, hi) || st != stg) bad2.Add("knock mn" + mn + " " + lo + ".." + hi);
                        if (RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, mn, mn, lo, hi, 0.7f, stg, out _, out _)) bad2.Add("knock off");
                    }
        for (float lim = 20f; lim <= 1000f; lim += 70f)
            foreach (float m in new[] { 10f, 100f, 250f, 600f })
            {
                c2++;
                int cc = RM_KnockbackMath.ContainerThrowCells(true, m, lim, 0.5f, MortarRadius, 1f, S());
                if (m > lim && cc != 0) bad2.Add("container over limit " + lim + " thrown");
                if (cc > S().maxCells) bad2.Add("container over cap");
            }
        for (int gc = 1; gc <= 6; gc++)
        {
            c2++;
            var k = KbLookup.Apply(S(), new KbConfig { ownCap = gc, scaleOwnCap = false }, 6, 0.25f);
            if (k.maxCells != gc) bad2.Add("gas goods cells " + gc + " -> " + k.maxCells);
        }
        for (int pct = 25; pct <= 400; pct += 25)
        {
            c2++;
            float rr = RM_KnockbackMath.DamageRatio(50f, 50f, pct, true);
            if (Math.Abs(rr - 100f / pct) > 1e-4f) bad2.Add("ref% " + pct + " ratio " + rr);
        }
        for (int w = 0; w <= 600; w += 60)
        {
            c2++;
            if (KbImmunity.CanLaunch(100 + w - 1, 100, 100, w) && w > 0) bad2.Add("recovery " + w + " too short");
            if (!KbImmunity.CanLaunch(100 + w, 100, 100, w)) bad2.Add("recovery " + w + " too long");
        }
        Check("sweep_goods_and_other_settings", new[] { "settings_scale_and_switch", "goods_arc_spin_rebound", "heavy_stack_knocks", "closed_container_holds", "gas_goes_clump_by_clump", "recovery_immunity", "inv_settings" }, "sweep", bad2, c2,
            "rebound keep 0..100, heavy knock min 1..75 dmg 0..20 stagger 0..180 and off, container limit 20..1000, gas goods cells 1..6 exact, blast-power reference 25..400%, recovery 0..600");
    }
}
