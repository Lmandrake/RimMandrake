// ExplosiveKnockback blind lane 1, cycle 6 (run judge-1795437145). Written from the bars alone (tree leaves via sheet.md,
// record.json inv_kernel, plan.md), the shipped settings (RM_KnockbackMod.cs) and the def patch, against the shipped kernels
// RM_KnockbackMath.cs and RM_KnockbackPlan.cs (both Verse-free). One JSON row per line on stdout.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using RimMandrake.ExplosiveKnockback;

public static class BlindLane1
{
    static readonly List<string> Rows = new List<string>();
    static bool anyFail;

    static string Esc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ");

    static void Row(string id, string bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        var b = new StringBuilder();
        b.Append("{\"id\":\"").Append(id).Append("\",\"bars\":[");
        string[] bs = bars.Split(',');
        for (int i = 0; i < bs.Length; i++) b.Append(i > 0 ? "," : "").Append('"').Append(bs[i].Trim()).Append('"');
        b.Append("],\"kind\":\"").Append(kind).Append("\",\"verdict\":\"").Append(verdict).Append("\",\"cases\":").Append(cases)
         .Append(",\"detail\":\"").Append(Esc(detail)).Append("\"}");
        Rows.Add(b.ToString());
    }

    // ── a grid for the path walk ──
    sealed class Grid : IKbGrid
    {
        public readonly int W, H;
        public readonly KbCell[,] c;
        public Grid(int w, int h) { W = w; H = h; c = new KbCell[w, h]; }
        public KbCell At(int x, int z) => x < 0 || z < 0 || x >= W || z >= H ? KbCell.OutOfBounds : c[x, z];
        public Grid Copy() { var g = new Grid(W, H); Array.Copy(c, g.c, c.Length); return g; }
    }

    sealed class World : IKbWorld
    {
        public Grid pawnGrid, goodsGrid;
        public bool[,] pawn, occ, deep;
        public World(Grid g)
        {
            pawnGrid = g; goodsGrid = g.Copy();
            pawn = new bool[g.W, g.H]; occ = new bool[g.W, g.H]; deep = new bool[g.W, g.H];
        }
        public void SetPawn(int x, int z) { pawn[x, z] = true; occ[x, z] = true; pawnGrid.c[x, z] = KbCell.Pawn; }
        public IKbGrid Grid(bool forPawn) => forPawn ? pawnGrid : goodsGrid;
        public bool PawnAt(int x, int z) => In(x, z) && pawn[x, z];
        public bool Occupied(int x, int z) => In(x, z) && occ[x, z];
        public bool Superdeep(int x, int z) => In(x, z) && deep[x, z];
        bool In(int x, int z) => x >= 0 && z >= 0 && x < pawnGrid.W && z < pawnGrid.H;
    }

    static KbSettings Def() => new KbSettings();
    static KbRules Rules() => new KbRules();
    static string F(float v) => v.ToString("0.###", CultureInfo.InvariantCulture);

    public static int Main()
    {
        Calibration();
        HeavierFliesLess();
        DamageRatioRows();
        MonotoneRandom(20261123);
        EligibleRows();
        ResolveFixed();
        PitRows();
        GasShoveRows();
        ShieldRows();
        RecoveryRows();
        SpareRows();
        WildRows();
        ReboundRows();
        EveryGoodMoves(7741);
        ShelfStoreroom(2611);
        ShelfRows();
        ContainerRandom(9917);
        HeavyKnockRows();
        LookupRows();
        LineRandom(31337);
        ResolveRandom(4242);
        FrameRows();
        LedgerRows();
        JoltRows();
        SettingsSweep(555);
        Conservation(8080);
        foreach (string r in Rows) Console.WriteLine(r);
        return anyFail ? 1 : 0;
    }

    // ── people_thrown_three_cells: mortar r 2.9 (Bomb 50 at its own 50: ratio 1), distance 1, a clothed colonist 64-76 kg -> 3 ──
    static void Calibration()
    {
        var s = Def();
        var bad = new List<string>();
        int n = 0;
        for (float m = 64f; m <= 76.01f; m += 0.5f)
        {
            n++;
            float ratio = RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true);
            int c = RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f * ratio, m, s);
            if (c != 3) bad.Add("m=" + F(m) + "->" + c);
        }
        // also diagonal neighbour (distance 1.414): "beside" may be diagonal
        int diag = RM_KnockbackMath.ThrowCells(1.4142f, 2.9f, 1f, 70f, s);
        Row("L1_CALIBRATION_MORTAR_BESIDE_COLONIST", "people_thrown_three_cells,inv_kernel", "fixed", bad.Count == 0 ? "PASS" : "FAIL", n + 1,
            bad.Count == 0 ? "dist 1, r 2.9, force 1, masses 64..76 kg every 0.5: all 3 cells; diagonal neighbour (1.414) at 70 kg: " + diag + " cells (INFO)"
                           : "violations: " + string.Join("; ", bad));
    }

    // ── heavier_flies_less: one blast throws a rat farther than a colonist, a colonist farther than a muffalo, a thrumbo over 150 kg
    //    not at all; at twice the damage each goes farther ──
    static void HeavierFliesLess()
    {
        var s = Def();
        float rat = 0.6f, col = 70f, muf = 144f, thr = 3500f;
        float r1 = RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true), r2 = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
        int a = RM_KnockbackMath.ThrowCells(1f, 2.9f, r1, rat, s), b = RM_KnockbackMath.ThrowCells(1f, 2.9f, r1, col, s),
            c = RM_KnockbackMath.ThrowCells(1f, 2.9f, r1, muf, s);
        int a2 = RM_KnockbackMath.ThrowCells(1f, 2.9f, r2, rat, s), b2 = RM_KnockbackMath.ThrowCells(1f, 2.9f, r2, col, s),
            c2 = RM_KnockbackMath.ThrowCells(1f, 2.9f, r2, muf, s);
        bool thrumboStays = !RM_KnockbackMath.Eligible(KbKind.Pawn, thr, s);
        bool muffaloFlies = RM_KnockbackMath.Eligible(KbKind.Pawn, muf, s);
        bool ok = a > b && b > c && c >= 1 && a2 > a && b2 > b && c2 > c && thrumboStays && muffaloFlies;
        Row("L1_HEAVIER_FLIES_LESS_MORTAR_SCENE", "heavier_flies_less,inv_kernel,inv_creature_mass_limit,inv_blast_power_damage", "fixed", ok ? "PASS" : "FAIL", 8,
            "dist 1 r 2.9 dmg 50: rat " + a + " > colonist " + b + " > muffalo " + c + "; dmg 100: " + a2 + "/" + b2 + "/" + c2 +
            "; thrumbo 3500 kg eligible=" + !thrumboStays + "; muffalo 144 kg eligible=" + muffaloFlies);
        // where the strict order cannot hold: rim (both round to the same) and the cap (both capped) - INFO, the bar names one blast at the scene
        int eq = 0, tot = 0;
        for (float d = 0f; d <= 2.9f; d += 0.1f)
        {
            tot++;
            int x = RM_KnockbackMath.ThrowCells(d, 2.9f, 1f, rat, s), y = RM_KnockbackMath.ThrowCells(d, 2.9f, 1f, col, s), z = RM_KnockbackMath.ThrowCells(d, 2.9f, 1f, muf, s);
            if (!(x >= y && y >= z)) { Row("L1_HEAVIER_NEVER_FARTHER", "heavier_flies_less", "fixed", "FAIL", 1, "d=" + F(d) + " rat " + x + " col " + y + " muf " + z); return; }
            if (x == y || y == z) eq++;
        }
        Row("L1_HEAVIER_NEVER_FARTHER", "heavier_flies_less,inv_kernel", "fixed", "PASS", tot,
            "d 0..2.9 step 0.1 at r 2.9: never a heavier thing farther; strict order fails only by rounding/cap at " + eq + " of " + tot + " distances (INFO: the rim and the cap)");
    }

    static void DamageRatioRows()
    {
        var bad = new List<string>();
        void E(float got, float want, string what) { if (Math.Abs(got - want) > 1e-5f) bad.Add(what + "=" + F(got) + " want " + F(want)); }
        E(RM_KnockbackMath.DamageRatio(50, 50, 100, true), 1f, "at ref");
        E(RM_KnockbackMath.DamageRatio(100, 50, 100, true), 2f, "twice");
        E(RM_KnockbackMath.DamageRatio(100, 50, 100, false), 1f, "switch off");
        E(RM_KnockbackMath.DamageRatio(100, 50, 200, true), 1f, "ref 200%");
        E(RM_KnockbackMath.DamageRatio(-5, 50, 100, true), 0f, "negative");
        E(RM_KnockbackMath.DamageRatio(30, 0, 100, true), 1f, "no ref");
        E(RM_KnockbackMath.DamageRatio(10, 10, 100, true), 1f, "Flame 10 at its own");
        Row("L1_BLAST_POWER_TYPE_X_DAMAGE", "heavier_flies_less,inv_blast_power_damage,settings_scale_and_switch", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 7,
            bad.Count == 0 ? "ratio = damage/(ref x pct/100); off or no ref = 1; negative = 0" : string.Join("; ", bad));
    }

    // ── monotone in mass, distance, force, strength; capped; 0 at force 0 / strength 0 ──
    static void MonotoneRandom(int seed)
    {
        var rng = new Random(seed);
        int n = 0;
        string first = null;
        for (int i = 0; i < 200000 && first == null; i++)
        {
            n++;
            var s = Def();
            s.globalMultiplier = (float)(rng.NextDouble() * 3);
            s.maxCells = 1 + rng.Next(10);
            float r = 0.5f + (float)rng.NextDouble() * 8f, d1 = (float)rng.NextDouble() * r, d2 = d1 + (float)rng.NextDouble() * r;
            float f1 = (float)rng.NextDouble() * 3f, f2 = f1 + (float)rng.NextDouble();
            float m1 = 0.1f + (float)rng.NextDouble() * 300f, m2 = m1 + (float)rng.NextDouble() * 300f;
            int a = RM_KnockbackMath.ThrowCells(d1, r, f1, m1, s);
            if (a > s.maxCells || a < 0) first = "cap: " + a + " > " + s.maxCells;
            else if (RM_KnockbackMath.ThrowCells(d1, r, f1, m2, s) > a) first = "mass m1=" + F(m1) + " m2=" + F(m2);
            else if (RM_KnockbackMath.ThrowCells(d2, r, f1, m1, s) > a) first = "dist d1=" + F(d1) + " d2=" + F(d2) + " r=" + F(r);
            else if (RM_KnockbackMath.ThrowCells(d1, r, f2, m1, s) < a) first = "force";
            else if (RM_KnockbackMath.ThrowCells(d1, r, 0f, m1, s) != 0) first = "force 0 throws";
            else { var z = Def(); z.globalMultiplier = 0f; if (RM_KnockbackMath.ThrowCells(d1, r, f1, m1, z) != 0) first = "strength 0 throws"; }
            if (first == null && RM_KnockbackMath.WildCells(d1, r, f1, m1, s, 1.6f) < a) first = "wild shorter than kernel";
        }
        Row("L1_THROW_MONOTONE_RANDOM", "heavier_flies_less,inv_kernel,settings_scale_and_switch", "random", first == null ? "PASS" : "FAIL", n,
            "seed " + seed + "; heavier/farther-out never throws farther, more force never less, never above maxCells, 0 at force 0 or strength 0, wild >= kernel" + (first == null ? "" : "; first: " + first));
    }

    // ── the_spared (mass parts): creature limit weighs pawns only, goods limit goods and corpses only; overrides ──
    static void EligibleRows()
    {
        var s = Def();
        var bad = new List<string>();
        void E(bool got, bool want, string w) { if (got != want) bad.Add(w + "=" + got); }
        E(RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s), true, "pawn 150");
        E(RM_KnockbackMath.Eligible(KbKind.Pawn, 150.5f, s), false, "pawn 150.5");
        E(RM_KnockbackMath.Eligible(KbKind.Pawn, 120f, s), true, "pawn 120 (over the 75 goods limit)");
        E(RM_KnockbackMath.Eligible(KbKind.Item, 75f, s), true, "item 75");
        E(RM_KnockbackMath.Eligible(KbKind.Item, 75.5f, s), false, "item 75.5");
        E(RM_KnockbackMath.Eligible(KbKind.Corpse, 90f, s), false, "corpse 90 (a corpse weighed by the goods limit)");
        E(RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, s), true, "corpse 60");
        var gr = KbLookup.Apply(s, new KbConfig { massLimitOverride = 216f }, 6, 1f);
        E(RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, gr), true, "grav-ram 180");
        E(RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, gr), false, "grav-ram 240");
        E(RM_KnockbackMath.Eligible(KbKind.Corpse, 100f, gr), false, "grav-ram corpse 100 (goods limit stays)");
        Row("L1_SPARED_BY_MASS_LIMITS", "the_spared,inv_creature_mass_limit,inv_mass_limit_skip,inv_big_corpse_spared,per_weapon_tuning", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 10,
            bad.Count == 0 ? "150 kg creature limit on pawns only, 75 kg goods limit on goods and corpses only, grav-ram 216 override" : string.Join("; ", bad));
    }

    static Grid Strip(string cells)
    {
        // a 1-high strip: index 0 is the start (Open); 'o' open, 'W' wall, 'D' door, 'S' sandbags, 'P' pawn, 'O' open pit, 'C' covered pit, '~' water
        var g = new Grid(cells.Length + 1, 1);
        for (int i = 0; i < cells.Length; i++)
        {
            KbCell k = KbCell.Open;
            switch (cells[i])
            {
                case 'W': k = KbCell.Wall; break;
                case 'D': k = KbCell.Door; break;
                case 'S': k = KbCell.Partial; break;
                case 'P': k = KbCell.Pawn; break;
                case 'O': k = KbCell.Pit; break;
                case 'C': k = KbCell.CoveredPit; break;
                case '~': k = KbCell.Water; break;
            }
            g.c[i, 0] = k;
        }
        return g;
    }

    // ── wall_stops_dead, pawn_hits_pawn_stops, doors_and_deep_water_stop, over sandbags ──
    static void ResolveFixed()
    {
        var s = Def();
        var bad = new List<string>();
        KbResult R(string strip, int cells, KbKind k, KbSettings st = null) => RM_KnockbackMath.Resolve(Strip(strip), 0, 0, 1f, 0f, cells, k, 70f, st ?? s);
        var r = R("ooWoo", 3, KbKind.Pawn);
        if (!(r.destX == 1 && r.stop == KbStop.Wall && r.impact > 0f)) bad.Add("wall: dest " + r.destX + " stop " + r.stop + " impact " + F(r.impact));
        r = R("oPooo", 3, KbKind.Pawn);
        if (!(r.destX == 0 && r.stop == KbStop.Pawn && r.hitOther && r.impact > 0f && r.otherImpact > 0f)) bad.Add("pawn: dest " + r.destX + " stop " + r.stop);
        r = R("oPooo", 3, KbKind.Item);
        if (r.destX != 3) bad.Add("item passes a pawn: dest " + r.destX);
        r = R("ooDoo", 3, KbKind.Pawn);
        if (!(r.destX == 1 && r.stop == KbStop.Door && r.hitDoor && r.doorX == 2 && r.impact > 0f)) bad.Add("door: dest " + r.destX + " stop " + r.stop);
        var z = Def(); z.impactFactor = 0f;
        r = R("ooDoo", 3, KbKind.Pawn, z);
        if (!(r.stop == KbStop.Door && r.impact == 0f)) bad.Add("door at impact factor 0: impact " + F(r.impact));
        r = R("ooWoo", 3, KbKind.Pawn, z);
        if (r.impact != 0f) bad.Add("wall at impact factor 0: impact " + F(r.impact));
        r = R("o~ooo", 3, KbKind.Pawn);
        if (!(r.destX == 0 && r.stop == KbStop.Water)) bad.Add("water pawn: dest " + r.destX + " stop " + r.stop);
        r = R("o~ooo", 3, KbKind.Item);
        if (!(r.destX == 0 && r.stop == KbStop.Water)) bad.Add("water goods: dest " + r.destX);
        r = R("oSoo", 3, KbKind.Pawn);
        if (r.destX != 3) bad.Add("over sandbags: dest " + r.destX);
        r = R("ooSo", 3, KbKind.Pawn);
        if (r.destX == 3 && Strip("ooSo").At(3, 0) == KbCell.Partial) bad.Add("rests on sandbags");
        if (Strip("ooSo").At(r.destX, 0) == KbCell.Partial) bad.Add("ends on a sandbag cell " + r.destX);
        var sb = Def(); sb.sandbagsStop = true;
        r = R("oSoo", 3, KbKind.Pawn, sb);
        if (!(r.destX == 0 && r.stop == KbStop.PartialCover)) bad.Add("sandbags stop on: dest " + r.destX + " stop " + r.stop);
        r = R("oSoo", 3, KbKind.Item, sb);
        if (r.destX != 3) bad.Add("sandbags stop on, goods still pass: dest " + r.destX);
        var im = Def(); im.impactEnabled = false;
        r = R("ooWoo", 3, KbKind.Pawn, im);
        if (r.impact != 0f) bad.Add("impact off: " + F(r.impact));
        // people never rebound: the plan launches a pawn on its single walk (no legs)
        var w = new World(Strip("ooWoo"));
        var f = new KbFacts { kind = KbKind.Pawn, x = 0, z = 0, mass = 70f, thingId = 1 };
        var p = KbPlanner.Decide(f, new KbBlast { id = 1, cx = -1, cz = 0, radius = 2.9f, force = 2f }, Rules(), Def(), w);
        if (!(p.act == KbAct.LaunchPawn && p.res.destX == 1 && p.res.stop == KbStop.Wall)) bad.Add("plan pawn at wall: " + p.act + " dest " + p.res.destX);
        Row("L1_PATH_STOPS_FIXED", "wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop,people_thrown_three_cells,per_weapon_tuning,inv_kernel", "fixed",
            bad.Count == 0 ? "PASS" : "FAIL", 16, bad.Count == 0 ? "wall, pawn, door, water, sandbags (both settings), impact factor 0, impact off, pawn never rebounds" : string.Join("; ", bad));
    }

    // ── thrown_into_pit_falls, blast_breaks_pit_cover (landing part) ──
    static void PitRows()
    {
        var s = Def();
        var bad = new List<string>();
        foreach (KbKind k in new[] { KbKind.Pawn, KbKind.Item, KbKind.Corpse })
        {
            var r = RM_KnockbackMath.Resolve(Strip("oOooo"), 0, 0, 1f, 0f, 5, k, 50f, s);
            if (!(r.destX == 1 && r.stop == KbStop.Pit)) bad.Add(k + " open pit: dest " + r.destX + " " + r.stop);
            r = RM_KnockbackMath.Resolve(Strip("oCooo"), 0, 0, 1f, 0f, 5, k, 50f, s);
            if (!(r.destX == 1 && r.stop == KbStop.Pit)) bad.Add(k + " covered pit: dest " + r.destX + " " + r.stop);
            if (!RM_KnockbackMath.LandingBreaksCover(k, true, false, 7)) bad.Add(k + " landing does not break a cover");
            if (RM_KnockbackMath.LandingBreaksCover(k, true, false, -7)) bad.Add(k + " gas landing breaks a cover");
        }
        if (RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, true, 7)) bad.Add("container breaks a cover");
        var off = Def(); off.intoPits = false;
        var q = RM_KnockbackMath.Resolve(Strip("oOooo"), 0, 0, 1f, 0f, 5, KbKind.Pawn, 70f, off);
        if (q.destX != 0) bad.Add("intoPits off: entered the pit, dest " + q.destX);
        Row("L1_PIT_FALLS_NEVER_ACROSS", "thrown_into_pit_falls,blast_breaks_pit_cover,inv_pits_receive,inv_kernel", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 17,
            bad.Count == 0 ? "pawn/stack/corpse stop IN the first open or covered pit cell, never across; a landing breaks the cover, a gas landing never; intoPits off keeps it out" : string.Join("; ", bad));
    }

    // ── gas_goes_clump_by_clump, thrown_into_pit_falls: a gas clump shoves a person one cell; onto an open pit falls in, onto a cover stands ──
    static void GasShoveRows()
    {
        var bad = new List<string>();
        var g = new KbBlast { id = -5, cx = 0, cz = 0, radius = 1.9f, force = 1f, gas = true };
        KbPlan P(string strip, KbFacts f, KbRules q = null) => KbPlanner.Decide(f, g, q ?? Rules(), Def(), new World(Strip(strip)));
        KbFacts Pawn(int ago = int.MaxValue) => new KbFacts { kind = KbKind.Pawn, x = 1, z = 0, mass = 70f, thingId = 3, gasShovedAgo = ago };
        var p = P("oooooo", Pawn());
        if (!(p.act == KbAct.LaunchPawn && p.res.destX == 2)) bad.Add("open ground: " + p.act + " dest " + p.res.destX);
        p = P("ooOooo", Pawn());
        if (!(p.act == KbAct.LaunchPawn && p.res.destX == 2 && p.res.stop == KbStop.Pit)) bad.Add("open pit: " + p.act + " dest " + p.res.destX);
        p = P("ooCooo", Pawn());
        if (!(p.act == KbAct.LaunchPawn && p.res.destX == 2 && !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, g.id))) bad.Add("cover: " + p.act);
        p = P("oooooo", Pawn(60));
        if (!(p.act == KbAct.Skip && p.reason == "gas_cooldown")) bad.Add("cooldown 60 ticks: " + p.act);
        p = P("oooooo", Pawn(120));
        if (p.act != KbAct.LaunchPawn) bad.Add("after 120 ticks: " + p.act);
        // goods: at most gasBurstGoodsCells (2), the caller's exact own cap
        var s = KbLookup.Apply(Def(), new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 0.25f);
        var it = KbPlanner.Decide(new KbFacts { kind = KbKind.Item, x = 1, z = 0, mass = 0.5f, thingId = 4 }, g, Rules(), s, new World(Strip("oooooooo")));
        if (!(it.act == KbAct.ThrowGoods && it.cells <= 2 && it.cells >= 1)) bad.Add("goods cap 2: " + it.act + " cells " + it.cells);
        Row("L1_GAS_SHOVE_ONE_CELL", "gas_goes_clump_by_clump,thrown_into_pit_falls,inv_gas_chain", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 7,
            bad.Count == 0 ? "a person shoved exactly 1 cell, into an open pit falls, onto a cover stands (cover whole), once per 120 ticks; goods at most 2 cells at any cap scale" : string.Join("; ", bad));
        // a person standing on an intact pit cover beside a burning clump (not in a pit: the spared list names 'a pawn already in a pit')
        var onCover = Pawn(); onCover.onSuperdeep = true;
        var w = new World(Strip("oCoooo"));
        var pc = KbPlanner.Decide(onCover, g, Rules(), Def(), w);
        Row("L1_GAS_SHOVE_PAWN_ON_INTACT_COVER", "gas_goes_clump_by_clump,the_spared", "fixed", pc.act == KbAct.LaunchPawn ? "PASS" : "UNSETTLED", 1,
            "KbFacts.onSuperdeep is 'dug to superdeep, covered or not', and PawnSkipReason skips it as in_pit: a person on an intact cover beside a burning clump got " +
            pc.act + (pc.reason != null ? " (" + pc.reason + ")" : "") + ". The bar spares 'a pawn already in a pit'; whether a pawn on an intact cover counts as in a pit is not in the bars. " +
            "Settles: the caller's onSuperdeep for a pawn on a cover, and a ruling whether standing on a cover is 'in a pit'.");
    }

    static void ShieldRows()
    {
        var bad = new List<string>();
        var f = new KbFacts { kind = KbKind.Pawn, x = 1, z = 0, mass = 70f, thingId = 3, shieldAbsorbed = true };
        var p = KbPlanner.Decide(f, new KbBlast { id = 2, cx = 0, cz = 0, radius = 2.9f, force = 1f }, Rules(), Def(), new World(Strip("oooooo")));
        if (p.act != KbAct.Absorb) bad.Add("mortar on a belt: " + p.act);
        var q = Rules(); q.shieldsAbsorbThrow = false;
        p = KbPlanner.Decide(f, new KbBlast { id = 2, cx = 0, cz = 0, radius = 2.9f, force = 1f }, q, Def(), new World(Strip("oooooo")));
        if (p.act != KbAct.LaunchPawn) bad.Add("belt switch off: " + p.act);
        float e = KbShield.EnergyAfter(1f, 1f, 10f, 0.033f);
        if (!(e < 1f)) bad.Add("no extra charge: " + F(e));
        if (KbShield.EnergyAfter(1f, -1f, 10f, 0.033f) != 1f) bad.Add("negative force pays");
        Row("L1_SHIELD_BELT_HOLDS", "shield_belt_holds,inv_shield", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 4,
            bad.Count == 0 ? "absorbed blast: wearer stays (Absorb), pays force x perForce x loss; switch off throws" : string.Join("; ", bad));
        var pg = KbPlanner.Decide(f, new KbBlast { id = -2, cx = 0, cz = 0, radius = 1.9f, force = 1f, gas = true }, Rules(), Def(), new World(Strip("oooooo")));
        Row("L1_SHIELD_DOES_NOT_STOP_GAS_SHOVE", "shield_belt_holds,gas_goes_clump_by_clump", "fixed", pg.act == KbAct.LaunchPawn ? "PASS" : "UNSETTLED", 1,
            "Decide with shieldAbsorbed=true on a gas burst gives " + pg.act + "; the bar says a belt does not stop a burning clump's shove. The plan has no gas exception, so it holds only if the caller " +
            "never sets shieldAbsorbed for a gas burst. Settles: the caller's shieldAbsorbed for gas bursts (lane 2).");
    }

    static void RecoveryRows()
    {
        var bad = new List<string>();
        if (KbImmunity.CanLaunch(150, 100, 160, 120)) bad.Add("inside stun");
        if (KbImmunity.CanLaunch(279, 100, 160, 120)) bad.Add("inside recovery");
        if (!KbImmunity.CanLaunch(280, 100, 160, 120)) bad.Add("after recovery");
        if (!KbImmunity.CanLaunch(101, 100, 160, 0)) bad.Add("window 0");
        if (KbImmunity.CanLaunch(200, 100, 50, 120)) bad.Add("stun before landing");
        var f = new KbFacts { kind = KbKind.Pawn, x = 1, z = 0, mass = 70f, recovering = true };
        var p = KbPlanner.Decide(f, new KbBlast { id = 2, cx = 0, cz = 0, radius = 2.9f, force = 1f }, Rules(), Def(), new World(Strip("oooo")));
        if (!(p.act == KbAct.Skip && p.reason == "immune")) bad.Add("plan: " + p.act);
        Row("L1_RECOVERY_IMMUNITY", "recovery_immunity,inv_recovery", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 6,
            bad.Count == 0 ? "no launch until max(landing, stun end) + window; window 0 chains; a recovering pawn is skipped immune" : string.Join("; ", bad));
    }

    static void SpareRows()
    {
        var bad = new List<string>();
        var b = new KbBlast { id = 9, cx = 0, cz = 0, radius = 2.9f, force = 1f };
        void T(KbFacts f, string want)
        {
            var p = KbPlanner.Decide(f, b, Rules(), Def(), new World(Strip("oooooo")));
            string got = p.act == KbAct.Skip ? p.reason : p.act.ToString();
            if (got != want) bad.Add(want + " got " + got);
        }
        KbFacts P() => new KbFacts { kind = KbKind.Pawn, x = 1, z = 0, mass = 70f, thingId = 5 };
        var a = P(); a.flying = true; T(a, "flying");
        a = P(); a.inBed = true; T(a, "in_bed");
        a = P(); a.carryingPawn = true; T(a, "carrying_pawn");
        a = P(); a.onSuperdeep = true; T(a, "in_pit");
        a = P(); a.mass = 151f; T(a, "too_heavy_creature");
        a = P(); a.downed = true; T(a, "LaunchPawn");
        var g = new KbFacts { kind = KbKind.Item, x = 1, z = 0, mass = 80f }; T(g, "too_heavy");
        g = new KbFacts { kind = KbKind.Corpse, x = 1, z = 0, mass = 60f, onSuperdeep = true }; T(g, "in_pit");
        g = new KbFacts { kind = KbKind.Item, x = 2, z = 0, mass = 70f }; // at 2 of r 2.9: raw 4 x 0.31 x 1 = 1.24 -> 1
        T(g, "ThrowGoods");
        g = new KbFacts { kind = KbKind.Item, x = 1, z = 0, mass = 70f };
        var rim = KbPlanner.Decide(g, new KbBlast { id = 9, cx = -2, cz = 0, radius = 2.9f, force = 0.6f }, Rules(), Def(), new World(Strip("oooooo")));
        // raw = 4 x 0.6 x (1 - 3/2.9 -> 0) = 0 -> too_weak
        if (!(rim.act == KbAct.Skip && rim.reason == "too_weak")) bad.Add("rim: " + rim.act);
        g = new KbFacts { kind = KbKind.Item, x = 1, z = 0, mass = 70f, spawned = false }; T(g, "not_spawned");
        Row("L1_THE_SPARED_STATES", "the_spared,inv_who_is_spared,inv_too_weak_skip,inv_mass_limit_skip,inv_pit_floor_goods_stay", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 11,
            bad.Count == 0 ? "airborne, in bed, carrying, in pit, >150 kg creature, >75 kg goods, goods on pit floor, rim under one cell: all stay; downed thrown (setting on)" : string.Join("; ", bad));
    }

    static void WildRows()
    {
        var s = Def();
        s.maxCells = 100;
        int n = 0;
        string first = null;
        double worstRatio = 0;
        for (float d = 0f; d < 5.9f; d += 0.05f)
            for (float m = 0.2f; m <= 75f; m *= 1.3f)
            {
                n++;
                // the bar's raw throw, written from the bar (force x falloff x sqrt(70/mass) clamped 0.25..2 x 4 base cells)
                double ms = Math.Min(2.0, Math.Max(0.25, Math.Sqrt(70.0 / Math.Max(m, 1f))));
                double raw = 4.0 * (1.0 - Math.Min(1.0, d / 5.9)) * ms;
                int k = RM_KnockbackMath.ThrowCells(d, 5.9f, 1f, m, s), w = RM_KnockbackMath.WildCells(d, 5.9f, 1f, m, s, 1.6f);
                if (Math.Abs(w - 1.6 * raw) > 0.5 + 1e-3) first = first ?? ("d " + F(d) + " m " + F(m) + " raw " + raw.ToString("0.00", CultureInfo.InvariantCulture) + " wild " + w);
                if (k >= 3) worstRatio = Math.Max(worstRatio, Math.Abs(w / (double)k - 1.6));
            }
        Row("L1_GOODS_FLY_ABOUT_1_6X", "goods_arc_spin_rebound,inv_goods_fly", "sweep", first == null ? "PASS" : "FAIL", n,
            "uncapped: every good's wild throw is the whole cell nearest 1.6 x the person throw (|wild - 1.6 raw| <= 0.5); against the ROUNDED person throw the ratio strays up to " +
            worstRatio.ToString("0.00", CultureInfo.InvariantCulture) + " from 1.6 at kernel >= 3 (INFO: whole cells)" + (first == null ? "" : "; first: " + first));
    }

    static void ReboundRows()
    {
        var bad = new List<string>();
        int[] want = { 0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 7 };
        for (int c = 0; c <= 10; c++) if (RM_KnockbackMath.ReboundCells(c, 70f) != want[c]) bad.Add(c + "->" + RM_KnockbackMath.ReboundCells(c, 70f));
        for (int k = 0; k < 100; k++)
            for (int c = 1; c <= 20; c++)
            {
                int c2 = RM_KnockbackMath.ReboundCells(c, k);
                if (c2 >= c) { bad.Add("keep " + k + "% does not shrink " + c); break; }
            }
        if (RM_KnockbackMath.ReboundCells(5, 100f) != 5) bad.Add("100% loses");
        // a chain in a closed box ends (maxBounces at 100%)
        var g = new Grid(5, 5);
        for (int i = 0; i < 5; i++) { g.c[i, 0] = KbCell.Wall; g.c[i, 4] = KbCell.Wall; g.c[0, i] = KbCell.Wall; g.c[4, i] = KbCell.Wall; }
        var q = Rules(); q.goodsReboundKeepPercent = 100f;
        var s = Def(); s.maxCells = 50;
        var res = RM_KnockbackMath.Resolve(g, 2, 2, 1f, 0.3f, 40, KbKind.Item, 1f, s);
        int bounces = 0, x = res.destX, z = res.destZ; float dx = 1f, dz = 0.3f; int left = 40 - res.cellsTravelled;
        while (KbPlanner.Rebound(g, res.stop, left, bounces, res, x, z, dx, dz, KbKind.Item, 1f, s, q, out KbLeg next))
        {
            bounces++; res = next.res; x = res.destX; z = res.destZ; dx = next.dx; dz = next.dz; left = res.cellsPlanned - res.cellsTravelled;
            if (bounces > 100) break;
        }
        if (bounces > q.maxBounces) bad.Add("100% chain ran " + bounces + " bounces");
        Row("L1_REBOUND_KEEPS_70_UNTIL_SPENT", "goods_arc_spin_rebound,inv_goods_fly", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 11 + 2000 + 2,
            bad.Count == 0 ? "floor(0.7 x left): 10->7,3->2,2->1,1->0; every keep under 100 shrinks; at 100 the chain stops at maxBounces (" + bounces + ")" : string.Join("; ", bad));
    }

    // ── every_good_moves: random walled storerooms; every reached light good (kernel >= 1 cell) moves, bar deep water right behind ──
    static void EveryGoodMoves(int seed)
    {
        var rng = new Random(seed);
        int reached = 0, still = 0;
        var cause = new SortedDictionary<string, int>();
        string firstStill = null; int firstCells = int.MaxValue;
        for (int t = 0; t < 400; t++)
        {
            int W = 8 + rng.Next(8), H = 8 + rng.Next(8);
            var g = new Grid(W, H);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    bool edge = x == 0 || z == 0 || x == W - 1 || z == H - 1;
                    double u = rng.NextDouble();
                    g.c[x, z] = edge ? (u < 0.1 ? KbCell.Door : KbCell.Wall) : (u < 0.04 ? KbCell.Partial : u < 0.06 ? KbCell.Wall : KbCell.Open);
                }
            var w = new World(g);
            var b = new KbBlast { id = t + 1, cx = 1 + rng.Next(W - 2), cz = 1 + rng.Next(H - 2), radius = 2.9f + (float)rng.NextDouble() * 3f, force = 1f };
            for (int x = 1; x < W - 1; x++) for (int z = 1; z < H - 1; z++)
                {
                    if (g.c[x, z] != KbCell.Open) continue;
                    var f = new KbFacts { kind = KbKind.Item, x = x, z = z, mass = 0.3f + (float)rng.NextDouble() * 70f, thingId = x * 100 + z };
                    var p = KbPlanner.Decide(f, b, Rules(), Def(), w);
                    if (p.kernelCells < 1) continue;
                    if (p.act == KbAct.Skip) continue;
                    reached++;
                    if (p.act != KbAct.ThrowGoods)
                    {
                        still++;
                        string why = p.cells == 1 && p.res.stop != KbStop.None ? "one_cell_against_" + p.res.stop : p.res.stop == KbStop.None ? "sandbags_no_hop" : "rebound_walk_blocked_" + p.res.stop;
                        cause.TryGetValue(why, out int cc); cause[why] = cc + 1;
                        if (p.cells < firstCells)
                        {
                            firstCells = p.cells;
                            firstStill = "seed " + seed + " room " + t + " (" + W + "x" + H + ") blast (" + b.cx + "," + b.cz + ") r " + F(b.radius) + " good (" + x + "," + z + ") " + F(f.mass) +
                                " kg: act " + p.act + " kernel " + p.kernelCells + " wild " + p.cells + " stop " + p.res.stop;
                        }
                    }
                }
        }
        // shrunk: a good one cell from a wall, the blast behind it, throw 1 cell
        var sg = Strip("ooooooW");
        var sp = KbPlanner.Decide(new KbFacts { kind = KbKind.Item, x = 5, z = 0, mass = 60f, thingId = 1 }, new KbBlast { id = 1, cx = 3, cz = 0, radius = 2.4f, force = 1f }, Rules(), Def(), new World(sg));
        string shrunk = "shrunk: a 60 kg good at (5,0) with a wall at (6,0), open floor behind it, a blast of radius 2.4 at force 1 at (3,0): kernel " + sp.kernelCells + " wild " + sp.cells + " act " + sp.act +
            " (the wall-first bounce keeps floor(0.7 x 1) = 0 cells); would pass: the good moves at least one cell off the wall";
        var causes = new List<string>(); foreach (var kv in cause) causes.Add(kv.Key + " " + kv.Value);
        Row("L1_EVERY_REACHED_GOOD_MOVES", "every_good_moves,goods_arc_spin_rebound,inv_goods_fly", "random", still == 0 ? "PASS" : "FAIL", reached,
            "seed " + seed + ", 400 walled rooms (walls, doors, sandbags), no water: " + still + " of " + reached + " reached goods (kernel >= 1 cell) did not move" +
            (still == 0 ? "" : "; causes: " + string.Join(", ", causes) + "; smallest-throw case: " + firstStill + "; " + shrunk));
    }

    // ── open_shelf_scatters + every_good_moves: a storeroom of open shelf rows (shelves are partial cover for the path), goods on the
    //    shelves and the aisles, one bomb inside: every reached good moves ──
    static void ShelfStoreroom(int seed)
    {
        var rng = new Random(seed);
        int reached = 0, still = 0;
        var cause = new SortedDictionary<string, int>();
        string firstStill = null;
        for (int t = 0; t < 300; t++)
        {
            int W = 10 + rng.Next(6), H = 10 + rng.Next(6);
            var g = new Grid(W, H);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    bool edge = x == 0 || z == 0 || x == W - 1 || z == H - 1;
                    g.c[x, z] = edge ? KbCell.Wall : (z % 3 == 1 && x > 1 && x < W - 2 ? KbCell.Partial : KbCell.Open);
                }
            g.c[W / 2, 0] = KbCell.Door;
            var w = new World(g);
            var b = new KbBlast { id = t + 1, cx = 1 + rng.Next(W - 2), cz = 1 + rng.Next(H - 2), radius = 2.9f + (float)rng.NextDouble() * 3f, force = 1f };
            for (int x = 1; x < W - 1; x++) for (int z = 1; z < H - 1; z++)
                {
                    var f = new KbFacts { kind = KbKind.Item, x = x, z = z, mass = 0.3f + (float)rng.NextDouble() * 70f, thingId = x * 100 + z, onStorage = g.c[x, z] == KbCell.Partial };
                    var p = KbPlanner.Decide(f, b, Rules(), Def(), w);
                    if (p.kernelCells < 1 || p.act == KbAct.Skip) continue;
                    reached++;
                    if (p.act != KbAct.ThrowGoods)
                    {
                        still++;
                        string why = p.cells == 1 && p.res.stop != KbStop.None ? "one_cell_against_" + p.res.stop : p.res.stop == KbStop.None ? "sandbags_no_hop" : "rebound_walk_blocked_" + p.res.stop;
                        cause.TryGetValue(why, out int cc); cause[why] = cc + 1;
                        firstStill = firstStill ?? ("room " + t + " (" + W + "x" + H + ") blast (" + b.cx + "," + b.cz + ") r " + F(b.radius) + " good (" + x + "," + z + ") " + F(f.mass) + " kg: " + p.act + " kernel " + p.kernelCells + " wild " + p.cells + " stop " + p.res.stop);
                    }
                }
        }
        var causes = new List<string>(); foreach (var kv in cause) causes.Add(kv.Key + " " + kv.Value);
        Row("L1_SHELF_STOREROOM_EVERY_GOOD_MOVES", "every_good_moves,open_shelf_scatters,goods_arc_spin_rebound", "random", still == 0 ? "PASS" : "FAIL", reached,
            "seed " + seed + ", 300 walled storerooms with open shelf rows every third row, one bomb inside: " + still + " of " + reached + " reached goods did not move" +
            (still == 0 ? "" : "; causes: " + string.Join(", ", causes) + "; first: " + firstStill));
    }

    static void ShelfRows()
    {
        var bad = new List<string>();
        var q = Rules();
        string H(bool st, bool cl, KbRules r) => KbPlanner.HeldReason(new KbFacts { kind = KbKind.Item, onStorage = st, onClosed = cl }, r) ?? "loose";
        if (H(true, false, q) != "loose") bad.Add("open shelf protects");
        if (H(true, true, q) != "closed_container") bad.Add("closed does not hold");
        if (H(false, true, q) != "closed_container") bad.Add("closed (not flagged storage) does not hold");
        var g = Rules(); g.closedContainerGuard = false;
        if (H(true, true, g) != "loose") bad.Add("guard off still holds");
        var o = Rules(); o.openStorageProtects = true;
        if (H(true, false, o) != "in_storage") bad.Add("old rule on, shelf loose");
        Row("L1_OPEN_SHELF_SCATTERS_CLOSED_HOLDS", "open_shelf_scatters,closed_container_holds,inv_shelf_skip,inv_closed_guard,settings_scale_and_switch", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 5,
            bad.Count == 0 ? "open storage protects nothing; closed holds; guard off = goods loose; the old rule switch restores shelf protection" : string.Join("; ", bad));
    }

    // ── closed_container_holds: thrown a short way at or under 250 kg, else a jolt; never into a pit, a wall or onto a pawn ──
    static void ContainerRandom(int seed)
    {
        var rng = new Random(seed);
        int n = 0, thrown = 0, jolts = 0;
        string first = null;
        for (int t = 0; t < 3000 && first == null; t++)
        {
            int W = 9, H = 9;
            var g = new Grid(W, H);
            var w0 = new bool[W, H];
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    double u = rng.NextDouble();
                    g.c[x, z] = u < 0.08 ? KbCell.Wall : u < 0.12 ? KbCell.Partial : u < 0.17 ? KbCell.Pit : u < 0.21 ? KbCell.CoveredPit : u < 0.24 ? KbCell.Water : u < 0.26 ? KbCell.Door : KbCell.Open;
                }
            g.c[4, 4] = KbCell.Open;
            var w = new World(g);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    if (g.c[x, z] == KbCell.Pit || g.c[x, z] == KbCell.CoveredPit) w.deep[x, z] = true;
                    if (g.c[x, z] == KbCell.Open && (x != 4 || z != 4))
                    {
                        double u = rng.NextDouble();
                        if (u < 0.08) w.SetPawn(x, z); else if (u < 0.16) w.occ[x, z] = true;
                    }
                }
            float mass = 5f + (float)rng.NextDouble() * 400f;
            var b = new KbBlast { id = t + 1, cx = 4 + rng.Next(-2, 3), cz = 4 + rng.Next(-2, 3), radius = 2.9f + (float)rng.NextDouble() * 3f, force = 0.5f + (float)rng.NextDouble() * 2f };
            var s = Def(); s.maxCells = 1 + rng.Next(10);
            var f = new KbFacts { container = true, kind = KbKind.Item, x = 4, z = 4, mass = mass, oneByOne = rng.NextDouble() < 0.85, thingId = 77 };
            var p = KbPlanner.Decide(f, b, Rules(), s, w);
            n++;
            if (p.act == KbAct.ContainerThrown)
            {
                thrown++;
                KbCell c = g.At(p.toX, p.toZ);
                if (mass > 250f || !f.oneByOne) first = "over limit or not 1x1 thrown: " + F(mass);
                else if (c != KbCell.Open) first = "rests on " + c;
                else if (w.pawn[p.toX, p.toZ]) first = "rests on a pawn";
                else if (w.deep[p.toX, p.toZ]) first = "rests on a pit";
                else if (w.occ[p.toX, p.toZ]) first = "rests on an occupied cell";
                else
                {
                    // never through a person, a wall or a pit: every cell from start to rest along the line is passable for it
                    var path = RM_KnockbackMath.Line(4, 4, p.dx, p.dz, p.planned);
                    for (int i = 0; i < p.travelled; i++)
                    {
                        KbCell pc = g.At(path[i].x, path[i].z);
                        if (pc == KbCell.Wall || pc == KbCell.Door || pc == KbCell.Pit || pc == KbCell.CoveredPit || pc == KbCell.Water || w.pawn[path[i].x, path[i].z])
                        { first = "flew through " + pc + (w.pawn[path[i].x, path[i].z] ? " (pawn)" : "") + " at step " + (i + 1) + " room " + t; break; }
                    }
                }
            }
            else if (p.act == KbAct.ContainerJolt) jolts++;
            else first = "act " + p.act;
            if (first != null) first = "seed " + seed + " room " + t + " mass " + F(mass) + ": " + first;
        }
        var q = Rules(); q.shoveClosedContainers = false;
        var off = KbPlanner.Decide(new KbFacts { container = true, x = 1, z = 0, mass = 20f, oneByOne = true }, new KbBlast { id = 1, cx = 0, cz = 0, radius = 2.9f, force = 1f }, q, Def(), new World(Strip("oooo")));
        if (off.act != KbAct.None && first == null) first = "shove off: " + off.act;
        int heavy = RM_KnockbackMath.ContainerThrowCells(true, 250f, 250f, 1f, 2.9f, 1f, Def()), loose = RM_KnockbackMath.WildCells(1f, 2.9f, 1f, 30f, Def(), 1.6f);
        Row("L1_CONTAINER_THROWN_SHORT_OR_JOLTS", "closed_container_holds,inv_container_shove,settings_scale_and_switch", "random", first == null ? "PASS" : "FAIL", n,
            "seed " + seed + ": " + thrown + " thrown, " + jolts + " jolts; rest cell always open, free, no pawn, no pit; never through a wall, pit or person; >250 kg or not 1x1 jolts; shove off = None; " +
            "a 250 kg crate beside a mortar plans " + heavy + " cell(s) vs a 30 kg loose good " + loose + (first == null ? "" : "; first: " + first));
    }

    static void HeavyKnockRows()
    {
        var bad = new List<string>();
        float d; int st;
        if (!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 10f, 10f, 2f, 5f, 0.5f, 30, out d, out st) || d < 2f || d > 5f || st != 30) bad.Add("10 kg: " + F(d) + "/" + st);
        if (RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 9.9f, 10f, 2f, 5f, 0.5f, 30, out d, out st)) bad.Add("9.9 kg hits");
        if (RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 50f, 10f, 2f, 5f, 0.5f, 30, out d, out st)) bad.Add("off hits");
        if (RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 50f, 10f, 2f, 5f, 0.5f, 30, out d, out st)) bad.Add("no person hits");
        for (float r = -1f; r <= 2f; r += 0.05f)
        {
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 2f, 5f, r, 30, out d, out st);
            if (d < 2f || d > 5f) { bad.Add("roll " + F(r) + " dmg " + F(d)); break; }
        }
        RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 10f, 6f, 3f, 0.9f, -5, out d, out st);
        if (d != 6f || st != 0) bad.Add("max<min/neg stagger: " + F(d) + "/" + st);
        Row("L1_HEAVY_STACK_KNOCKS", "heavy_stack_knocks,inv_heavy_knock,settings_scale_and_switch", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 66,
            bad.Count == 0 ? "a stack >= 10 kg reaching a person: 2..5 blunt, 30-tick stagger; lighter, no person or switch off: passes" : string.Join("; ", bad));
    }

    // ── per_weapon_tuning, every_harmful_blast_throws ──
    static void LookupRows()
    {
        var bad = new List<string>();
        var pz = new KbConfig { force = 0f }; var dd = new KbConfig { force = 1f };
        var r = KbLookup.Resolve(pz, null, dd, true, 1f);
        if (!(r.force == 0f && r.source == "projectile")) bad.Add("projectile 0 does not win");
        r = KbLookup.Resolve(null, new KbConfig { force = 0.3f }, dd, true, 1f);
        if (!(r.force == 0.3f && r.source == "weapon")) bad.Add("weapon before damageDef");
        r = KbLookup.Resolve(null, null, null, true, 1f);
        if (!(r.force == 1f && r.source == "unpatched")) bad.Add("unpatched harmful at 100%: " + F(r.force));
        r = KbLookup.Resolve(null, null, null, true, 0.4f);
        if (r.force != 0.4f) bad.Add("unpatched percent");
        r = KbLookup.Resolve(null, null, null, false, 1f);
        if (r.force != 0f) bad.Add("harmless throws");
        r = KbLookup.Resolve(null, null, new KbConfig { force = 0.5f }, true, 0.4f);
        if (r.force != 0.5f) bad.Add("other-mods percent stacked on a tuned type: " + F(r.force));
        var g = Def();
        if (KbLookup.Apply(g, new KbConfig { ownCap = 0 }, 6, 0.5f).maxCells != 6) bad.Add("ownCap 0 != global");
        if (KbLookup.Apply(g, new KbConfig { ownCap = 4 }, 6, 0.5f).maxCells != 2) bad.Add("own cap scale does not shorten");
        if (KbLookup.Apply(g, new KbConfig { ownCap = 4, scaleOwnCap = false }, 6, 0.5f).maxCells != 4) bad.Add("exact cap rescaled");
        if (KbLookup.Apply(g, new KbConfig { impactFactor = -2f }, 6, 1f).impactFactor != 0f) bad.Add("negative impact factor");
        if (g.maxCells != 6 || g.impactFactor != 1f) bad.Add("Apply mutated the shared settings");
        if (!RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn")) bad.Add("fire off keeps Flame");
        if (RM_KnockbackMath.FireSwitchedOff(false, "projectile", "Flame", "Burn")) bad.Add("fire off zeroes a weapon's own");
        if (RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn")) bad.Add("fire on zeroed");
        if (!RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "ElectricalBurn", "ElectricalBurn")) bad.Add("ElectricalBurn");
        if (RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded")) bad.Add("bomb zeroed");
        // fire at half: Flame force 0.5 from the patch gives about half the colonist's 3
        int fire = RM_KnockbackMath.ThrowCells(1f, 2.9f, 0.5f, 70f, Def()), bomb = RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, Def());
        if (!(fire >= 1 && fire <= 2 && bomb == 3)) bad.Add("fire " + fire + " bomb " + bomb);
        Row("L1_LOOKUP_AND_WHICH_BLASTS", "per_weapon_tuning,every_harmful_blast_throws,only_explosions_throw,inv_which_blasts,inv_weapon_ext_fields,inv_kernel", "fixed",
            bad.Count == 0 ? "PASS" : "FAIL", 18, bad.Count == 0 ? "projectile > weapon > damageDef whole, zero wins; unpatched harmful at the percent, harmless 0, never stacked; own cap/scale/exact; fire half " + fire + " vs bomb " + bomb + "; fire-off zeroes only the type patch" : string.Join("; ", bad));
        // a fire type of another mod with no patch of ours and not parented on Flame: the switch does not reach it
        bool modFireOff = RM_KnockbackMath.FireSwitchedOff(false, "unpatched", "VFE_Burn", "Burn");
        Row("L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE", "every_harmful_blast_throws,settings_scale_and_switch", "fixed", "UNSETTLED", 1,
            "FireSwitchedOff(false, 'unpatched', a Burn-hediff type) = " + modFireOff + ": an other-mod fire damage type with no extension throws at the other-mods percent (full, not half) and keeps throwing with 'fire at half' off. " +
            "The bars say 'fire at half ... other mods too (the other-mods percent only for a damage type our patch does not tune)' and 'fire at half off, fire throws nothing'. Settles: whether the caller halves an unpatched fire type, and a ruling which clause wins for another mod's fire.");
    }

    // ── no_teleport: the throw line is contiguous, exactly `cells` grid steps ──
    static void LineRandom(int seed)
    {
        var rng = new Random(seed);
        string first = null; int n = 0;
        for (int i = 0; i < 100000 && first == null; i++)
        {
            n++;
            float a = (float)(rng.NextDouble() * Math.PI * 2);
            int cells = rng.Next(0, 12);
            var l = RM_KnockbackMath.Line(0, 0, (float)Math.Cos(a), (float)Math.Sin(a), cells);
            if (l.Count != cells) first = "count " + l.Count + " != " + cells + " at angle " + F(a);
            int px = 0, pz = 0;
            foreach (var c in l)
            {
                if (Math.Max(Math.Abs(c.x - px), Math.Abs(c.z - pz)) != 1) { first = "jump at angle " + F(a) + " cells " + cells; break; }
                px = c.x; pz = c.z;
            }
        }
        Row("L1_LINE_CONTIGUOUS_NO_TELEPORT", "no_teleport,people_thrown_three_cells,inv_kernel", "random", first == null ? "PASS" : "FAIL", n,
            "seed " + seed + ": every step one king move, exactly `cells` steps" + (first == null ? "" : "; first: " + first));
    }

    // ── random walk invariants ──
    static void ResolveRandom(int seed)
    {
        var rng = new Random(seed);
        string first = null; int n = 0;
        KbCell[] pal = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
        for (int t = 0; t < 60000 && first == null; t++)
        {
            int W = 7, H = 7;
            var g = new Grid(W, H);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) g.c[x, z] = pal[rng.Next(pal.Length)];
            g.c[3, 3] = KbCell.Open;
            float a = (float)(rng.NextDouble() * Math.PI * 2);
            float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
            int cells = 1 + rng.Next(8);
            KbKind k = (KbKind)rng.Next(3);
            var s = Def(); s.sandbagsStop = rng.NextDouble() < 0.3; s.intoPits = rng.NextDouble() < 0.8;
            var r = RM_KnockbackMath.Resolve(g, 3, 3, dx, dz, cells, k, 1f + (float)rng.NextDouble() * 140f, s);
            n++;
            var path = RM_KnockbackMath.Line(3, 3, dx, dz, cells);
            string bad = null;
            if (r.cellsTravelled < 0 || r.cellsTravelled > cells) bad = "travelled " + r.cellsTravelled;
            else
            {
                (int x, int z) dest = r.cellsTravelled == 0 ? (3, 3) : path[r.cellsTravelled - 1];
                if (dest.x != r.destX || dest.z != r.destZ) bad = "dest off the line prefix";
                KbCell dc = g.At(r.destX, r.destZ);
                if (r.cellsTravelled > 0 && (dc == KbCell.Wall || dc == KbCell.Door || dc == KbCell.Water || dc == KbCell.OutOfBounds || dc == KbCell.Partial)) bad = bad ?? "rests on " + dc;
                if (r.cellsTravelled > 0 && k == KbKind.Pawn && dc == KbCell.Pawn) bad = bad ?? "pawn rests on a pawn";
                int px = 3, pz = 3;
                for (int i = 0; i < r.cellsTravelled && bad == null; i++)
                {
                    KbCell c = g.At(path[i].x, path[i].z);
                    if (c == KbCell.Wall || c == KbCell.Door || c == KbCell.Water || c == KbCell.OutOfBounds) bad = "passed through " + c;
                    if ((c == KbCell.Pit || c == KbCell.CoveredPit) && i < r.cellsTravelled - 1) bad = "thrown across a pit";
                    if ((c == KbCell.Pit || c == KbCell.CoveredPit) && !s.intoPits) bad = "entered a pit with intoPits off";
                    if (k == KbKind.Pawn && c == KbCell.Pawn) bad = "pawn passed through a pawn";
                    if (k == KbKind.Pawn && s.sandbagsStop && c == KbCell.Partial) bad = "pawn passed sandbags with sandbagsStop";
                    if (path[i].x != px && path[i].z != pz)
                    {
                        KbCell c1 = g.At(path[i].x, pz), c2 = g.At(px, path[i].z);
                        if (c1 == KbCell.Wall || c1 == KbCell.Door || c2 == KbCell.Wall || c2 == KbCell.Door) bad = "cut a wall corner";
                    }
                    px = path[i].x; pz = path[i].z;
                }
            }
            if (bad != null) first = "seed " + seed + " grid " + t + " kind " + k + " cells " + cells + " angle " + F(a) + ": " + bad;
        }
        Row("L1_RESOLVE_RANDOM_INVARIANTS", "no_teleport,wall_stops_dead,pawn_hits_pawn_stops,doors_and_deep_water_stop,thrown_into_pit_falls,goods_arc_spin_rebound,inv_kernel", "random",
            first == null ? "PASS" : "FAIL", n, "seed " + seed + ": dest on the line prefix; never rests on wall/door/water/edge/sandbags; never through them, never across a pit, never a corner cut; pawn never through or onto a pawn" + (first == null ? "" : "; first: " + first));
    }

    static void FrameRows()
    {
        var bad = new List<string>();
        var l = new List<float>(); for (int i = 1; i <= 100; i++) l.Add(i);
        if (KbFrameStats.Percentile(l, 99f) != 99f) bad.Add("p99 of 1..100 = " + F(KbFrameStats.Percentile(l, 99f)));
        if (KbFrameStats.Percentile(new List<float>(), 99f) != 0f) bad.Add("empty");
        // 9 s of 16 ms frames, one 400 ms stall at 3 s: passes (a single stall is reported, not judged)
        List<float> ms = new List<float>(); for (int i = 0; i < 560; i++) ms.Add(i == 180 ? 400f : 16f);
        KbFrameSummary G(List<float> m, int pausedEvery = 0)
        {
            var p = new bool[m.Count]; var a = new int[m.Count];
            if (pausedEvery > 0) for (int i = 0; i < m.Count; i += pausedEvery) p[i] = true;
            float sum = 0; foreach (float v in m) sum += v;
            return KbFrameStats.Summarize(m.ToArray(), p, a, m.Count, sum / 1000f, 0.9f, 8.25f);
        }
        string why;
        if (!KbFrameStats.WithinBudget(G(ms), 50f, out why)) bad.Add("single stall failed: " + why);
        var slow = new List<float>(ms); for (int i = 200; i < 215; i++) slow[i] = 80f;
        if (KbFrameStats.WithinBudget(G(slow), 50f, out why)) bad.Add("a 15-frame 80 ms stretch passed");
        var shortRun = ms.GetRange(0, 300);
        if (KbFrameStats.WithinBudget(G(shortRun), 50f, out why)) bad.Add("probe stopped before the window end passed");
        if (KbFrameStats.WithinBudget(G(ms, 5), 50f, out why)) bad.Add("20% paused passed");
        var g = G(ms);
        if (g.worstMs != 400f) bad.Add("worst " + F(g.worstMs));
        Row("L1_FRAME_P99_IN_WINDOW", "barrage_frame_budget,frame_time_probe,inv_perf_all_fly", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 7,
            bad.Count == 0 ? "nearest-rank p99; one stall passes, a stretch fails, short or paused runs fail, worst frame reported" : string.Join("; ", bad));
    }

    static void LedgerRows()
    {
        var bad = new List<string>();
        var L = new KbExplosionLedger(600);
        if (!L.TryAdd(1, 10, 599)) bad.Add("first add");
        if (L.TryAdd(1, 10, 600)) bad.Add("repeat across rotation");
        if (L.TryAdd(1, 10, 1198)) bad.Add("repeat at +599");
        if (!L.TryAdd(-3, 10, 1199)) bad.Add("gas id distinct");
        if (!L.TryAdd(2, 10, 1199)) bad.Add("other explosion");
        Row("L1_EXPLOSION_LEDGER_DEDUPE", "every_good_moves,inv_kernel", "fixed", bad.Count == 0 ? "PASS" : "FAIL", 5,
            bad.Count == 0 ? "a repeat callback for the same (explosion, thing) is refused for at least the window, across a rotation" : string.Join("; ", bad));
    }

    static void JoltRows()
    {
        float worst = 0; int n = 0;
        for (int t = -2; t < 40; t++) { n++; RM_KnockbackMath.JoltOffset(t, 30, 0.15f, 1f, 2f, out float ox, out float oz); worst = Math.Max(worst, (float)Math.Sqrt(ox * ox + oz * oz)); if ((t < 0 || t >= 30) && (ox != 0 || oz != 0)) worst = 99; }
        Row("L1_CONTAINER_JOLT_BOUNDED", "closed_container_holds,inv_container_shove", "fixed", worst <= 0.15f + 1e-5f ? "PASS" : "FAIL", n, "jolt never beyond its amplitude, 0 outside its ticks (worst " + F(worst) + ")");
    }

    // ── every shipped setting swept through its range, every switch off ──
    static void SettingsSweep(int seed)
    {
        var rng = new Random(seed);
        string first = null; int n = 0;
        float[] strengths = { 0f, 0.5f, 1f, 2f, 3f };
        for (int t = 0; t < 30000 && first == null; t++)
        {
            n++;
            var s = Def();
            s.globalMultiplier = strengths[rng.Next(strengths.Length)];
            s.maxCells = 1 + rng.Next(10);
            s.creatureMassLimit = 20 + rng.Next(481);
            s.lightMassLimit = 5 + rng.Next(196);
            s.impactPerCell = (float)rng.NextDouble() * 15f;
            s.impactEnabled = rng.NextDouble() < 0.7;
            s.sandbagsStop = rng.NextDouble() < 0.3;
            s.intoPits = rng.NextDouble() < 0.7;
            var q = Rules();
            q.throwDowned = rng.NextDouble() < 0.7; q.throwAnimals = rng.NextDouble() < 0.7; q.throwMechanoids = rng.NextDouble() < 0.7;
            q.throwItems = rng.NextDouble() < 0.7; q.throwCorpses = rng.NextDouble() < 0.7; q.flyingGoods = rng.NextDouble() < 0.7;
            q.closedContainerGuard = rng.NextDouble() < 0.7; q.openStorageProtects = rng.NextDouble() < 0.3; q.shoveClosedContainers = rng.NextDouble() < 0.7;
            q.shieldsAbsorbThrow = rng.NextDouble() < 0.7; q.goodsRebound = rng.NextDouble() < 0.7; q.goodsReboundKeepPercent = rng.Next(101);
            q.containerMassLimit = 20 + rng.Next(981); q.gasPawnCooldownTicks = rng.Next(601);
            float refPct = 25 + rng.Next(376);
            bool power = rng.NextDouble() < 0.7;
            float ratio = RM_KnockbackMath.DamageRatio(50f + rng.Next(100), 50f, refPct, power);
            if (!power && ratio != 1f) first = "blast power off ratio " + F(ratio);
            var g = Strip("ooooooooooo");
            var w = new World(g);
            KbKind k = (KbKind)rng.Next(3);
            var f = new KbFacts { kind = k, x = 1, z = 0, mass = 0.5f + (float)rng.NextDouble() * 200f, thingId = t, downed = rng.NextDouble() < 0.2, animal = rng.NextDouble() < 0.2, mechanoid = rng.NextDouble() < 0.1,
                onStorage = rng.NextDouble() < 0.3, onClosed = rng.NextDouble() < 0.2 };
            var b = new KbBlast { id = t + 1, cx = 0, cz = 0, radius = 2.9f, force = ratio };
            var p = KbPlanner.Decide(f, b, q, s, w);
            string got = p.act == KbAct.Skip ? p.reason : p.act.ToString();
            if (first != null) break;
            if (p.Throws && s.globalMultiplier == 0f) first = "strength 0 throws";
            else if (k == KbKind.Item && !q.throwItems && p.Throws) first = "items off throws";
            else if (k == KbKind.Corpse && !q.throwCorpses && p.Throws) first = "corpses off throws";
            else if (k != KbKind.Pawn && !q.flyingGoods && p.Throws) first = "goods in the air off, still thrown (the old hop?)";
            else if (k == KbKind.Pawn && f.downed && !q.throwDowned && p.Throws) first = "downed off throws";
            else if (k == KbKind.Pawn && f.animal && !q.throwAnimals && p.Throws) first = "animals off throws";
            else if (k == KbKind.Pawn && f.mechanoid && !q.throwMechanoids && p.Throws) first = "mechs off throws";
            else if (k == KbKind.Pawn && f.mass > s.creatureMassLimit && p.Throws) first = "creature over limit thrown";
            else if (k != KbKind.Pawn && f.mass > s.lightMassLimit && p.Throws) first = "goods over limit thrown";
            else if (k == KbKind.Item && q.closedContainerGuard && f.onClosed && p.Throws) first = "closed guard on, good thrown";
            else if (p.Throws && p.res.cellsTravelled > s.maxCells) first = "beyond the cap";
            if (first != null) first = "seed " + seed + " case " + t + " kind " + k + " mass " + F(f.mass) + " got " + got + ": " + first;
        }
        Row("L1_SETTINGS_SWEEP_SWITCHES_OFF", "settings_scale_and_switch,inv_settings,inv_kernel", "sweep", first == null ? "PASS" : "FAIL", n,
            "seed " + seed + ": strength 0..3, max 1..10, creature 20..500, goods 5..200, impact, sandbags, pits, every plan switch, rebound keep 0..100, container 20..1000, blast power ref 25..400 and off: each switch off gives its off state, nothing beyond the cap" + (first == null ? "" : "; first: " + first));
    }

    // ── conservation: one plan per request, a thrown good's whole flight ends on a cell where it can lie, in the map ──
    static void Conservation(int seed)
    {
        var rng = new Random(seed);
        string first = null; int n = 0, legsTotal = 0;
        for (int t = 0; t < 300 && first == null; t++)
        {
            int W = 12, H = 12;
            var g = new Grid(W, H);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    double u = rng.NextDouble();
                    g.c[x, z] = u < 0.07 ? KbCell.Wall : u < 0.09 ? KbCell.Door : u < 0.13 ? KbCell.Partial : u < 0.16 ? KbCell.Pit : u < 0.18 ? KbCell.CoveredPit : u < 0.2 ? KbCell.Water : KbCell.Open;
                }
            var w = new World(g);
            var b = new KbBlast { id = t + 1, cx = rng.Next(W), cz = rng.Next(H), radius = 5.9f, force = 1f + (float)rng.NextDouble() };
            var s0 = Def(); s0.maxCells = 10;
            for (int x = 0; x < W && first == null; x++) for (int z = 0; z < H && first == null; z++)
                {
                    if (g.c[x, z] != KbCell.Open) continue;
                    n++;
                    var s = KbLookup.Apply(s0, new KbConfig(), 10, 1f);
                    var f = new KbFacts { kind = rng.NextDouble() < 0.2 ? KbKind.Corpse : KbKind.Item, x = x, z = z, mass = 0.2f + (float)rng.NextDouble() * 70f, thingId = x * 31 + z };
                    var p = KbPlanner.Decide(f, b, Rules(), s, w);
                    if (p.act != KbAct.ThrowGoods) continue;
                    KbLeg leg = p.first;
                    int bounces = p.wallFirst ? 1 : 0;
                    var q = Rules();
                    while (true)
                    {
                        legsTotal++;
                        int left = leg.res.cellsPlanned - leg.res.cellsTravelled;
                        if (!KbPlanner.Rebound(g, leg.res.stop, left, bounces, leg.res, leg.res.destX, leg.res.destZ, leg.dx, leg.dz, f.kind, f.mass, s, q, out KbLeg next)) break;
                        bounces++; leg = next;
                        if (bounces > 50) { first = "chain does not end"; break; }
                    }
                    KbCell end = g.At(leg.res.destX, leg.res.destZ);
                    if (end == KbCell.OutOfBounds || end == KbCell.Wall || end == KbCell.Door || end == KbCell.Water || end == KbCell.Partial)
                        first = "seed " + seed + " room " + t + " good (" + x + "," + z + ") ends on " + end + " at (" + leg.res.destX + "," + leg.res.destZ + ")";
                }
        }
        Row("L1_CONSERVATION_FLIGHT_ENDS_ON_GROUND", "no_teleport,goods_arc_spin_rebound,every_good_moves,inv_goods_fly", "random", first == null ? "PASS" : "FAIL", n,
            "seed " + seed + ", 300 rooms with walls, doors, sandbags, pits, covers, water: every thrown good's whole leg chain (" + legsTotal + " legs) ends, in bounds, on a cell it can lie on" + (first == null ? "" : "; first: " + first));
    }
}
