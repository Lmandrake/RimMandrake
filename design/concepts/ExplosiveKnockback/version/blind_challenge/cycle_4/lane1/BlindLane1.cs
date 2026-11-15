// Blind lane 1, ExplosiveKnockback 0.1.0, cycle 4: the throw kernel (RM_KnockbackMath.cs) tested from the bars alone
// (tree.json, sheet.md, record.json inventory, the scene oracles' numbers) and the shipped settings (EK_* variables,
// read by run_lane1.py from RM_KnockbackMod.cs). Written before any test, journal or earlier finding was read.
// One JSON row per line on stdout. Exit 0 = no FAIL row; 1 = a row FAILed.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

static class BlindLane1
{
    static int fails;
    static readonly CultureInfo IC = CultureInfo.InvariantCulture;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind) +
                          ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    // a check list for one row: every failed case is kept (first 6 printed)
    sealed class Chk
    {
        public int n; public readonly List<string> bad = new List<string>();
        public void T(bool ok, string what) { n++; if (!ok) bad.Add(what); }
        public string V => bad.Count == 0 ? "PASS" : "FAIL";
        public string D(string pass) => bad.Count == 0 ? pass : bad.Count + " of " + n + " failed: " + string.Join(" | ", bad.Take(6));
    }

    static float F(string v, float d) => float.TryParse(Environment.GetEnvironmentVariable(v), NumberStyles.Float, IC, out float x) ? x : d;
    static int I(string v, int d) => int.TryParse(Environment.GetEnvironmentVariable(v), out int x) ? x : d;
    static bool B(string v, bool d) { string s = Environment.GetEnvironmentVariable(v); return s == null ? d : s == "1"; }
    static readonly List<string> unread = new List<string>();
    static string Need(string v) { if (Environment.GetEnvironmentVariable(v) == null) unread.Add(v); return v; }

    // shipped defaults (read from RM_KnockbackMod.cs by run_lane1.py)
    static float STRENGTH, OWNCAPSCALE, CREATURE, LIGHT, IMPACT_PER, REFPCT, CONTAINER, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, KEEP, WILD;
    static int MAXCELLS, STAGGER, GAS_GOODS, RECOVERY;
    static bool IMPACT_ON, SANDBAGS, PITS, POWER_ON;

    static void ReadSettings()
    {
        STRENGTH = F(Need("EK_STRENGTH"), float.NaN); MAXCELLS = I(Need("EK_MAXCELLS"), -1); OWNCAPSCALE = F(Need("EK_OWNCAPSCALE"), float.NaN);
        CREATURE = F(Need("EK_CREATURE"), float.NaN); LIGHT = F(Need("EK_LIGHT"), float.NaN); IMPACT_ON = B(Need("EK_IMPACT_ON"), true);
        IMPACT_PER = F(Need("EK_IMPACT_PER"), float.NaN); SANDBAGS = B(Need("EK_SANDBAGS"), false); PITS = B(Need("EK_PITS"), true);
        POWER_ON = B(Need("EK_POWER_ON"), true); REFPCT = F(Need("EK_REFPCT"), float.NaN); CONTAINER = F(Need("EK_CONTAINER"), float.NaN);
        HEAVY_MIN = F(Need("EK_HEAVY_MIN"), float.NaN); HEAVY_DMIN = F(Need("EK_HEAVY_DMIN"), float.NaN); HEAVY_DMAX = F(Need("EK_HEAVY_DMAX"), float.NaN);
        STAGGER = I(Need("EK_STAGGER"), -1); KEEP = F(Need("EK_KEEP"), float.NaN); GAS_GOODS = I(Need("EK_GAS_GOODS"), -1);
        RECOVERY = I(Need("EK_RECOVERY"), -1); WILD = F(Need("EK_WILD"), float.NaN);
    }

    // the global kernel settings as the shipped settings build them (the game side's Kernel(): strength, cap, limits,
    // impact, sandbags, pits; baseCells and refMass are the kernel's own)
    static KbSettings Shipped(Action<KbSettings> tweak = null)
    {
        var s = new KbSettings
        {
            globalMultiplier = STRENGTH, maxCells = MAXCELLS, creatureMassLimit = CREATURE, lightMassLimit = LIGHT,
            impactEnabled = IMPACT_ON, impactPerCell = IMPACT_PER, sandbagsStop = SANDBAGS, intoPits = PITS,
        };
        tweak?.Invoke(s);
        return s;
    }

    sealed class Grid : IKbGrid
    {
        public int w, h; public KbCell[,] c;
        public Grid(int w, int h) { this.w = w; this.h = h; c = new KbCell[w, h]; }
        public KbCell At(int x, int z) => x < 0 || z < 0 || x >= w || z >= h ? KbCell.OutOfBounds : c[x, z];
        public Grid Copy() { var g = new Grid(w, h); g.c = (KbCell[,])c.Clone(); return g; }
        public string Dump() { var sb = new StringBuilder(); for (int z = h - 1; z >= 0; z--) { for (int x = 0; x < w; x++) sb.Append((int)c[x, z]); sb.Append('/'); } return sb.ToString(); }
    }

    static Grid Lane(int len, params (int x, KbCell k)[] cells)
    {
        var g = new Grid(len, 3);
        foreach (var (x, k) in cells) g.c[x, 1] = k;
        return g;
    }

    const float MORTAR_R = 2.9f;
    static int Throw(float dist, float r, float force, float mass, KbSettings s) => RM_KnockbackMath.ThrowCells(dist, r, force, mass, s);

    static void Main()
    {
        ReadSettings();
        if (unread.Count > 0)
        {
            Row("L1_SETTINGS_READ", new[] { "settings_scale_and_switch" }, "info", "UNSETTLED", 0, "shipped settings not read: " + string.Join(",", unread));
            Environment.Exit(1);
        }
        Row("L1_SETTINGS_READ", new[] { "settings_scale_and_switch" }, "info", "INFO", 1,
            string.Format(IC, "shipped: strength {0}, max {1}, ownCapScale {2}, creature {3} kg, goods {4} kg, impact {5}/{6}, sandbagsStop {7}, pits {8}, power {9}/{10}%, container {11} kg, heavy {12} kg {13}-{14} dmg {15} ticks, keep {16}%, gas goods {17}, recovery {18}, wild {19}",
                STRENGTH, MAXCELLS, OWNCAPSCALE, CREATURE, LIGHT, IMPACT_ON, IMPACT_PER, SANDBAGS, PITS, POWER_ON, REFPCT, CONTAINER, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, STAGGER, KEEP, GAS_GOODS, RECOVERY, WILD));

        Calibration();
        MassAndPower();
        DamageRatioRows();
        EligibleRows();
        LookupRows();
        CapRows();
        FireRows();
        PathFixed();
        PathRandom(20261115);
        WildRows(20261116);
        ReboundRows();
        ContainerRows();
        HeavyKnockRows();
        ImmunityShieldRows();
        LedgerRows();
        MiscRows();
        SettingsSweep(20261117);
        Environment.Exit(fails > 0 ? 1 : 0);
    }

    // people_thrown_three_cells: a mortar (r 2.9) one cell from a colonist (64-76 kg, sc_mass_and_power's band; 70 = clothed,
    // armed) throws about 3 cells, alive; shipped settings
    static void Calibration()
    {
        var k = new Chk(); var s = Shipped();
        foreach (float m in new[] { 64f, 66f, 70f, 73f, 76f })
            k.T(Throw(1f, MORTAR_R, 1f, m, s) == 3, "mortar d1 " + m + " kg -> " + Throw(1f, MORTAR_R, 1f, m, s) + " (want 3)");
        // over the sandbag line: lane colonist at 0, sandbags at cells 2, 3 (two cells further east), throw lands on 3
        var g = Lane(10, (2, KbCell.Partial));
        var r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(r.destX == 3 && r.stop == KbStop.Distance && r.impact == 0f, "over sandbags: dest " + r.destX + " stop " + r.stop + " impact " + r.impact);
        var g2 = Lane(10);
        var r2 = RM_KnockbackMath.Resolve(g2, 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(r2.destX == r.destX, "control lane without the line lands elsewhere: " + r2.destX);
        Row("L1_CALIBRATION_MORTAR_THREE", new[] { "people_thrown_three_cells", "inv_kernel" }, "fixed", k.V, k.n,
            k.D("mortar r2.9 at 1 cell throws 3 for 64-76 kg; over a sandbag line it lands on the same cell as the no-line control, no impact"));
    }

    // heavier_flies_less / sc_mass_and_power: 12 / 70 / 144 / 240 kg at damage 50 -> 5, 3, 2, 0 (too heavy); at 100 -> 6, 5, 4, 0;
    // blast power off -> reference both runs; creature limit 250 -> thrumbo 1 then 3
    static void MassAndPower()
    {
        var k = new Chk();
        float[] mass = { 12f, 70f, 144f, 240f };
        int[] at50 = { 5, 3, 2, 0 }, at100 = { 6, 5, 4, 0 };
        foreach (var (lim, power) in new[] { (CREATURE, POWER_ON), (CREATURE, false), (250f, POWER_ON) })
        {
            var s = Shipped(x => x.creatureMassLimit = lim);
            for (int run = 0; run < 2; run++)
            {
                float dmg = run == 0 ? 50f : 100f;
                float ratio = RM_KnockbackMath.DamageRatio(dmg, 50f, REFPCT, power);
                float force = 1f * ratio;
                int prev = int.MaxValue;
                for (int i = 0; i < 4; i++)
                {
                    int cells = RM_KnockbackMath.Eligible(KbKind.Pawn, mass[i], s) ? Throw(1f, MORTAR_R, force, mass[i], s) : 0;
                    int want;
                    if (lim == 250f && i == 3) want = run == 0 ? 1 : 3;
                    else if (!power) want = at50[i];
                    else want = run == 0 ? at50[i] : at100[i];
                    k.T(cells == want, string.Format(IC, "limit {0} power {1} dmg {2}: {3} kg -> {4} (want {5})", lim, power, dmg, mass[i], cells, want));
                    k.T(cells <= prev, "heavier flew farther at " + mass[i]);
                    prev = cells;
                }
                k.T(Math.Abs(ratio - (power ? dmg / 50f : 1f)) < 1e-5f, "ratio " + ratio);
            }
        }
        Row("L1_MASS_AND_POWER_TABLE", new[] { "heavier_flies_less", "inv_creature_mass_limit", "inv_blast_power_damage", "inv_kernel" }, "fixed", k.V, k.n,
            k.D("the sc_mass_and_power table holds: 5/3/2/0 then 6/5/4/0; power off gives the reference both runs; limit 250 throws the 240 kg one 1 then 3"));

        // monotone sweep: heavier never farther, more damage never less (random seeded)
        var rnd = new Random(4242); var m2 = new Chk(); string first = null;
        for (int t = 0; t < 20000; t++)
        {
            float r = (float)(0.9 + rnd.NextDouble() * 8), d = (float)(rnd.NextDouble() * r * 1.1);
            float f = (float)(rnd.NextDouble() * 3), ma = (float)(rnd.NextDouble() * 400), mb = ma + (float)(rnd.NextDouble() * 300);
            var s = Shipped(x => x.maxCells = 1 + rnd.Next(10));
            int ca = Throw(d, r, f, ma, s), cb = Throw(d, r, f, mb, s), cc = Throw(d, r, f * 2f, ma, s), cd = Throw(Math.Min(r, d + 0.5f), r, f, ma, s);
            bool ok = cb <= ca && cc >= ca && cd <= ca && ca <= s.maxCells && ca >= 0;
            m2.T(ok, "x");
            if (!ok && first == null) first = string.Format(IC, "seed 4242 case {0}: r {1} d {2} f {3} m {4}/{5} cap {6} -> {7} {8} x2 {9} farther {10}", t, r, d, f, ma, mb, s.maxCells, ca, cb, cc, cd);
        }
        Row("L1_THROW_MONOTONE_RANDOM", new[] { "heavier_flies_less", "inv_kernel" }, "random", m2.V, m2.n,
            m2.bad.Count == 0 ? "seed 4242, 20000 cases: heavier never farther, twice the force never shorter, farther from the centre never farther, never past the cap" : first);
    }

    static void DamageRatioRows()
    {
        var k = new Chk();
        k.T(RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true) == 1f, "50/50");
        k.T(RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true) == 2f, "100/50");
        k.T(RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false) == 1f, "off");
        k.T(RM_KnockbackMath.DamageRatio(10f, 10f, 100f, true) == 1f, "Flame at its normal 10 keeps its half (ratio 1)");
        k.T(RM_KnockbackMath.DamageRatio(77f, 0f, 100f, true) == 1f, "no reference -> 1");
        k.T(RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true) == 0f, "negative damage counts 0");
        k.T(Math.Abs(RM_KnockbackMath.DamageRatio(100f, 50f, 200f, true) - 1f) < 1e-6f, "ref percent 200 halves");
        k.T(Math.Abs(RM_KnockbackMath.DamageRatio(50f, 50f, 25f, true) - 4f) < 1e-6f, "ref percent 25 x4");
        // force = type force x ratio: fire at half keeps exactly half the bomb's raw throw at the same ratio
        var s = Shipped(x => x.maxCells = 100);
        int bomb = Throw(0f, 10f, 1f, 70f, s), fire = Throw(0f, 10f, 0.5f, 70f, s);
        k.T(bomb == 4 && fire == 2, "bomb/fire at the centre r10: " + bomb + "/" + fire + " (want 4/2)");
        Row("L1_DAMAGE_RATIO", new[] { "heavier_flies_less", "inv_blast_power_damage", "every_harmful_blast_throws" }, "fixed", k.V, k.n,
            k.D("damage / (reference x percent/100), 1 when off or no reference, negative damage 0; fire 0.5 throws half the bomb"));
    }

    static void EligibleRows()
    {
        var k = new Chk(); var s = Shipped();
        k.T(RM_KnockbackMath.Eligible(KbKind.Pawn, CREATURE, s), "pawn at the limit");
        k.T(!RM_KnockbackMath.Eligible(KbKind.Pawn, CREATURE + 0.01f, s), "pawn just over");
        k.T(RM_KnockbackMath.Eligible(KbKind.Item, LIGHT, s), "item at the goods limit");
        k.T(!RM_KnockbackMath.Eligible(KbKind.Item, LIGHT + 0.01f, s), "item over");
        k.T(!RM_KnockbackMath.Eligible(KbKind.Corpse, LIGHT + 0.01f, s), "corpse over the goods limit");
        k.T(RM_KnockbackMath.Eligible(KbKind.Pawn, 140f, s), "a 140 kg living pawn flies (goods limit never weighs a pawn)");
        var s20 = Shipped(x => x.creatureMassLimit = 20f);
        k.T(RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, s20), "creature limit 20: the human corpse still thrown");
        var sBig = Shipped(x => x.lightMassLimit = 200f);
        k.T(RM_KnockbackMath.Eligible(KbKind.Corpse, 190f, sBig), "goods limit raised: the big corpse thrown (no body-size rule)");
        // grav-ram's own limit 216 throws a 200 kg pawn; without it spared
        var ram = KbLookup.Apply(s, new KbConfig { massLimitOverride = 216f }, MAXCELLS, OWNCAPSCALE);
        k.T(RM_KnockbackMath.Eligible(KbKind.Pawn, 200f, ram) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 200f, s), "grav-ram 216 override");
        k.T(ram.lightMassLimit == s.lightMassLimit, "the creature override leaves the goods limit");
        var low = KbLookup.Apply(s, new KbConfig { massLimitOverride = 100f }, MAXCELLS, OWNCAPSCALE);
        k.T(!RM_KnockbackMath.Eligible(KbKind.Pawn, 120f, low), "a weapon limit below the global spares a 120 kg pawn ('under that instead')");
        Row("L1_ELIGIBLE_MASS_LIMITS", new[] { "the_spared", "inv_mass_limit_skip", "inv_creature_mass_limit", "inv_big_corpse_spared", "per_weapon_tuning" }, "fixed", k.V, k.n,
            k.D("creature limit weighs living pawns only, goods limit goods and corpses only, inclusive at the limit; a weapon's own limit replaces the creature limit"));
    }

    static void LookupRows()
    {
        var k = new Chk();
        var proj = new KbConfig { force = 0.3f }; var weap = new KbConfig { force = 0.6f }; var dd = new KbConfig { force = 1f };
        k.T(KbLookup.Resolve(proj, weap, dd, true, 1f) == proj && proj.source == "projectile", "projectile first");
        k.T(KbLookup.Resolve(null, weap, dd, true, 1f) == weap && weap.source == "weapon", "weapon second");
        k.T(KbLookup.Resolve(null, null, dd, true, 1f) == dd && dd.source == "damageDef", "type third");
        var zero = new KbConfig { force = 0f };
        var z = KbLookup.Resolve(zero, null, new KbConfig { force = 1f }, true, 1f);
        k.T(z.force == 0f && Throw(0f, 3f, z.force, 70f, Shipped()) == 0, "projectile zero wins whole, no throw");
        var un = KbLookup.Resolve(null, null, null, true, 1f);
        k.T(un.force == 1f && un.source == "unpatched", "unpatched harmful at the default 100%: " + un.force);
        k.T(KbLookup.Resolve(null, null, null, false, 1f).force == 0f, "harmless unpatched throws nothing");
        k.T(KbLookup.Resolve(null, null, null, true, 0f).force == 0f, "unpatched percent 0");
        // a tuned modded fire type keeps its own tuning; the other-mods percent never stacks: the type's force reaches the throw as is
        var tunedFire = new KbConfig { force = 0.5f };
        var rf = KbLookup.Resolve(null, null, tunedFire, true, 0.4f);
        k.T(rf.force == 0.5f, "a tuned type ignores the other-mods percent: " + rf.force);
        // Apply never mutates the shared settings
        var g = Shipped(); int capBefore = g.maxCells; float limBefore = g.creatureMassLimit;
        KbLookup.Apply(g, new KbConfig { ownCap = 2, massLimitOverride = 300f, impactFactor = 0f }, MAXCELLS, OWNCAPSCALE);
        k.T(g.maxCells == capBefore && g.creatureMassLimit == limBefore && g.impactFactor == 1f, "Apply mutated the shared settings");
        var neg = KbLookup.Apply(g, new KbConfig { impactFactor = -2f }, MAXCELLS, OWNCAPSCALE);
        k.T(neg.impactFactor == 0f, "negative impact factor clamps to 0");
        Row("L1_LOOKUP_ORDER", new[] { "per_weapon_tuning", "every_harmful_blast_throws", "inv_weapon_ext_fields", "inv_kernel" }, "fixed", k.V, k.n,
            k.D("projectile > weapon > damage type, first wins whole (zero included); unpatched harmful at the percent, harmless 0; Apply copies"));
    }

    static void CapRows()
    {
        var k = new Chk();
        k.T(RM_KnockbackMath.CapFor(0, 6, 0.5f) == 6, "own 0 keeps the global under any scale");
        k.T(RM_KnockbackMath.CapFor(2, 6, 1f) == 2, "own 2 throws at most 2");
        k.T(RM_KnockbackMath.CapFor(4, 6, 0.5f) == 2, "own 4 x 0.5 = 2");
        k.T(RM_KnockbackMath.CapFor(1, 6, 0.25f) == 1, "never below 1");
        var s = KbLookup.Apply(Shipped(), new KbConfig { ownCap = 2 }, MAXCELLS, OWNCAPSCALE);
        k.T(Throw(0f, 5f, 3f, 10f, s) == 2, "own maximum caps a strong throw");
        // a gas burst's goods cap is exact (never rescaled by the per-weapon scale)
        foreach (float sc in new[] { 0.25f, 0.5f, 1f, 2f })
        {
            var gs = KbLookup.Apply(Shipped(), new KbConfig { ownCap = GAS_GOODS, scaleOwnCap = false }, MAXCELLS, sc);
            k.T(gs.maxCells == GAS_GOODS, "gas cap at scale " + sc + " = " + gs.maxCells);
        }
        Row("L1_CAP_FOR", new[] { "per_weapon_tuning", "gas_goes_clump_by_clump", "inv_kernel" }, "fixed", k.V, k.n,
            k.D("own maximum (0 = global) x the cap scale, never under 1; the gas goods cap is exact at every scale"));
    }

    static void FireRows()
    {
        var k = new Chk();
        k.T(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn"), "Flame, switch off, type patch");
        k.T(!RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn"), "switch on keeps fire");
        k.T(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "ElectricalBurn", "ElectricalBurn"), "ElectricalBurn is fire");
        k.T(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "SomeModFire", "Burn"), "a modded burn type is fire");
        k.T(!RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded"), "Bomb is not fire");
        k.T(!RM_KnockbackMath.FireSwitchedOff(false, "projectile", "Flame", "Burn"), "a projectile's own tuning stays");
        k.T(!RM_KnockbackMath.FireSwitchedOff(false, "weapon", "Flame", "Burn"), "a weapon's own tuning stays");
        // sheet: "fire at half off, fire throws nothing" — an UNPATCHED fire type (source unpatched) under the switch off
        bool unpatched = RM_KnockbackMath.FireSwitchedOff(false, "unpatched", "ModFireNoPatch", "Burn");
        Row("L1_FIRE_SWITCH", new[] { "every_harmful_blast_throws", "settings_scale_and_switch" }, "fixed", k.V, k.n,
            k.D("the fire switch zeroes a fire type's own patch force (Flame, Burn, ElectricalBurn), never a projectile's or weapon's own tuning"));
        Row("L1_FIRE_SWITCH_UNPATCHED_TYPE", new[] { "every_harmful_blast_throws", "settings_scale_and_switch" }, "info", "INFO", 1,
            "an unpatched modded fire-type blast (source 'unpatched', hediff Burn) under fire-at-half OFF: FireSwitchedOff = " + unpatched +
            " (it throws at the other-mods percent). The sheet says 'fire at half off, fire throws nothing'; whether a modded fire type with no patch counts is not settled by the bars (a modded Flame child inherits Flame's patch, source damageDef)");
    }

    // the path walk, fixed lanes (the leaves' scenarios)
    static void PathFixed()
    {
        var k = new Chk(); var s = Shipped();
        // wall_stops_dead: colonist two cells from a wall, a 3-cell throw: stops on the cell before, impact > 0
        var w = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Wall)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(w.destX == 1 && w.stop == KbStop.Wall && w.impact > 0f, "wall: dest " + w.destX + " stop " + w.stop + " impact " + w.impact);
        k.T(w.hasBlock && w.blockX == 2, "wall block cell recorded");
        // pawn_hits_pawn_stops
        var p = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Pawn)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(p.destX == 1 && p.stop == KbStop.Pawn && p.impact > 0f && p.otherImpact > 0f && p.hitOther && p.otherX == 2, "pawn: dest " + p.destX + " " + p.stop + " imp " + p.impact + "/" + p.otherImpact);
        // doors_and_deep_water_stop
        var d = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Door)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(d.destX == 1 && d.stop == KbStop.Door && d.hitDoor && d.doorX == 2 && d.impact > 0f, "door: dest " + d.destX + " " + d.stop + " imp " + d.impact);
        var wa = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Water)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(wa.destX == 1 && wa.stop == KbStop.Water, "water: dest " + wa.destX + " " + wa.stop);
        // impact factor 0: hits are harmless (wall, pawn, door)
        var s0 = KbLookup.Apply(s, new KbConfig { impactFactor = 0f }, MAXCELLS, OWNCAPSCALE);
        foreach (var kc in new[] { KbCell.Wall, KbCell.Pawn, KbCell.Door })
        {
            var r0 = RM_KnockbackMath.Resolve(Lane(10, (2, kc)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s0);
            k.T(r0.destX == 1 && r0.impact == 0f && r0.otherImpact == 0f, "impact factor 0 at " + kc + ": " + r0.impact + "/" + r0.otherImpact);
        }
        // impact switched off
        var soff = Shipped(x => x.impactEnabled = false);
        var ro = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Wall)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, soff);
        k.T(ro.impact == 0f, "impact off");
        // open pit: stops IN the first open pit cell; never across
        var pit = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Pit), (3, KbCell.Pit)), 0, 1, 1f, 0f, 5, KbKind.Pawn, 70f, s);
        k.T(pit.destX == 2 && pit.stop == KbStop.Pit, "pit: dest " + pit.destX + " " + pit.stop);
        var pitI = RM_KnockbackMath.Resolve(Lane(10, (1, KbCell.Pit)), 0, 1, 1f, 0f, 5, KbKind.Item, 5f, s);
        k.T(pitI.destX == 1 && pitI.stop == KbStop.Pit, "a stack falls into the pit too: " + pitI.destX);
        // throw into pits off: an open pit is a wall
        var pitOff = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Pit)), 0, 1, 1f, 0f, 5, KbKind.Pawn, 70f, Shipped(x => x.intoPits = false));
        k.T(pitOff.destX == 1 && pitOff.stop == KbStop.Wall, "pits off: dest " + pitOff.destX + " " + pitOff.stop);
        // covered pit: landing ON it puts the thing there (the game breaks the cover)
        var cov = RM_KnockbackMath.Resolve(Lane(10, (3, KbCell.CoveredPit)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(cov.destX == 3, "onto a cover: dest " + cov.destX);
        // sandbags: never come to rest on one; sandbags-stop on: stops before
        var sb = RM_KnockbackMath.Resolve(Lane(10, (3, KbCell.Partial)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, s);
        k.T(sb.destX == 2, "a throw ending on sandbags backs to the free cell: " + sb.destX);
        var sbs = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Partial)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, Shipped(x => x.sandbagsStop = true));
        k.T(sbs.destX == 1 && sbs.stop == KbStop.PartialCover, "sandbags stop on: " + sbs.destX + " " + sbs.stop);
        var sbi = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Partial)), 0, 1, 1f, 0f, 3, KbKind.Item, 5f, Shipped(x => x.sandbagsStop = true));
        k.T(sbi.destX == 3, "goods go over sandbags even with the stop on: " + sbi.destX);
        // goods: a wall gives a block to rebound off, never impact on the good itself in the kernel
        var gw = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Wall)), 0, 1, 1f, 0f, 4, KbKind.Item, 5f, s);
        k.T(gw.destX == 1 && gw.hasBlock && gw.impact == 0f, "goods wall: block for the rebound");
        var gd = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Door)), 0, 1, 1f, 0f, 4, KbKind.Item, 5f, s);
        k.T(gd.destX == 1 && gd.hasBlock, "goods rebound off a closed door too");
        var gwa = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Water)), 0, 1, 1f, 0f, 4, KbKind.Corpse, 50f, s);
        k.T(gwa.destX == 1 && gwa.stop == KbStop.Water, "a corpse never into deep water");
        // map edge
        var e = RM_KnockbackMath.Resolve(Lane(4), 2, 1, 1f, 0f, 5, KbKind.Pawn, 70f, s);
        k.T(e.destX == 3 && e.stop == KbStop.OutOfBounds, "edge: " + e.destX + " " + e.stop);
        // diagonal: never cuts a wall corner
        var gdg = new Grid(6, 6); gdg.c[1, 0] = KbCell.Wall;
        var dg = RM_KnockbackMath.Resolve(gdg, 0, 0, 1f, 1f, 3, KbKind.Pawn, 70f, s);
        k.T(dg.destX == 0 && dg.destZ == 0 && dg.stop == KbStop.Wall, "corner cut: " + dg.destX + "," + dg.destZ + " " + dg.stop);
        // throw of 0 moves nothing
        var z0 = RM_KnockbackMath.Resolve(Lane(10), 0, 1, 1f, 0f, 0, KbKind.Pawn, 70f, s);
        k.T(!z0.Moved && z0.stop == KbStop.None, "0 cells");
        Row("L1_PATH_FIXED_LANES", new[] { "inv_kernel", "wall_stops_dead", "pawn_hits_pawn_stops", "doors_and_deep_water_stop", "thrown_into_pit_falls", "per_weapon_tuning", "goods_arc_spin_rebound", "people_thrown_three_cells" }, "fixed", k.V, k.n,
            k.D("wall/pawn/door stop on the cell before with impact (none at factor 0 or impact off); water stops on the last standable cell; first open pit cell, never across; pits off = wall; sandbags passed, never rested on; corners never cut"));
    }

    // random path walk: conservation and no-teleport invariants, seeded, shrinking a failing case
    static string PathViolation(Grid g, int sx, int sz, float dx, float dz, int cells, KbKind kind, float mass, KbSettings s)
    {
        var r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
        var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
        if (cells > 0 && path.Count != cells && Math.Max(Math.Abs(dx), Math.Abs(dz)) > 1e-6f) return "path length " + path.Count + " for " + cells + " cells";
        int px = sx, pz = sz;
        foreach (var (x, z) in path) { if (Math.Max(Math.Abs(x - px), Math.Abs(z - pz)) != 1) return "path step is not adjacent (teleport)"; px = x; pz = z; }
        if (r.cellsTravelled < 0 || r.cellsTravelled > cells) return "travelled " + r.cellsTravelled + " of " + cells;
        if (Math.Max(Math.Abs(r.destX - sx), Math.Abs(r.destZ - sz)) != r.cellsTravelled) return "dest " + r.destX + "," + r.destZ + " is not travelled " + r.cellsTravelled + " grid steps out";
        if (r.cellsTravelled > 0 && (path[r.cellsTravelled - 1].x != r.destX || path[r.cellsTravelled - 1].z != r.destZ)) return "dest is off the throw's line";
        KbCell dc = g.At(r.destX, r.destZ);
        if (r.cellsTravelled > 0)
        {
            if (dc == KbCell.Wall || dc == KbCell.Door || dc == KbCell.Water || dc == KbCell.OutOfBounds || dc == KbCell.Partial) return "came to rest on " + dc;
            if (kind == KbKind.Pawn && dc == KbCell.Pawn) return "a pawn came to rest on a pawn";
            if (!s.intoPits && dc == KbCell.Pit) return "pits off but landed in a pit";
        }
        for (int i = 0; i < r.cellsTravelled - 1; i++)
        {
            KbCell c = g.At(path[i].x, path[i].z);
            if (c == KbCell.Wall || c == KbCell.Door || c == KbCell.Water || c == KbCell.OutOfBounds) return "passed through " + c + " at step " + (i + 1);
            if (c == KbCell.Pit) return "thrown across an open pit at step " + (i + 1);
            if (kind == KbKind.Pawn && c == KbCell.Pawn) return "a pawn passed through a pawn";
            if (kind == KbKind.Pawn && s.sandbagsStop && c == KbCell.Partial) return "sandbags-stop on but passed sandbags";
        }
        // corners: each diagonal step on the travelled part has both orthogonal neighbours non-solid
        px = sx; pz = sz;
        for (int i = 0; i < r.cellsTravelled; i++)
        {
            var (x, z) = path[i];
            bool Solid(KbCell c) => c == KbCell.Wall || c == KbCell.Door || c == KbCell.OutOfBounds;
            if (x != px && z != pz && (Solid(g.At(x, pz)) || Solid(g.At(px, z)))) return "cut a wall corner at step " + (i + 1);
            px = x; pz = z;
        }
        if (r.impact < 0f || r.otherImpact < 0f) return "negative impact";
        if (kind != KbKind.Pawn && (r.impact != 0f || r.otherImpact != 0f)) return "impact on a good in the kernel";
        if ((!s.impactEnabled || s.impactFactor == 0f) && (r.impact != 0f || r.otherImpact != 0f)) return "impact with impact off/factor 0";
        if (kind == KbKind.Pawn && s.impactEnabled && s.impactFactor > 0f && s.impactPerCell > 0f && (r.stop == KbStop.Wall || r.stop == KbStop.Door || r.stop == KbStop.Pawn) && r.cellsTravelled < cells && r.impact <= 0f)
            return "stopped early at " + r.stop + " with no impact";
        if (r.stop == KbStop.Pawn && (!r.hitOther || Math.Max(Math.Abs(r.otherX - r.destX), Math.Abs(r.otherZ - r.destZ)) != 1)) return "pawn stop without the hit pawn next to it";
        return null;
    }

    static void PathRandom(int seed)
    {
        var rnd = new Random(seed); int n = 0; var kinds2 = new Dictionary<string, string>(); var counts = new Dictionary<string, int>();
        KbCell[] kinds = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
        for (int t = 0; t < 30000; t++)
        {
            int W = 5 + rnd.Next(10), H = 5 + rnd.Next(10);
            var g = new Grid(W, H);
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) g.c[x, z] = kinds[rnd.Next(kinds.Length)];
            int sx = rnd.Next(W), sz = rnd.Next(H);
            double a = rnd.NextDouble() * Math.PI * 2; float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
            int cells = rnd.Next(11); KbKind kind = (KbKind)rnd.Next(3);
            float mass = (float)(1 + rnd.NextDouble() * 150);
            var s = Shipped(x => { x.intoPits = rnd.Next(4) > 0; x.sandbagsStop = rnd.Next(4) == 0; x.impactEnabled = rnd.Next(5) > 0; x.impactFactor = rnd.Next(5) == 0 ? 0f : 1f; x.impactPerCell = (float)(rnd.NextDouble() * 15); });
            n++;
            string v = PathViolation(g, sx, sz, dx, dz, cells, kind, mass, s);
            if (v == null) continue;
            string key = new string(v.TakeWhile(ch => !char.IsDigit(ch)).ToArray()).Trim();
            counts[key] = counts.TryGetValue(key, out int c0) ? c0 + 1 : 1;
            if (kinds2.ContainsKey(key)) continue;
            // shrink: fewer cells, then clear grid cells to Open while the same kind of violation persists
            bool Same(int cc) { string w = PathViolation(g, sx, sz, dx, dz, cc, kind, mass, s); return w != null && w.StartsWith(key); }
            while (cells > 1 && Same(cells - 1)) cells--;
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
            {
                if (g.c[x, z] == KbCell.Open) continue;
                var keep = g.c[x, z]; g.c[x, z] = KbCell.Open;
                if (!Same(cells)) g.c[x, z] = keep;
            }
            kinds2[key] = string.Format(IC, "first at seed {0} case {1}: {2}; shrunk: grid {3}x{4} rows top-down {5} start {6},{7} dir {8:F3},{9:F3} cells {10} kind {11} mass {12:F1} pits {13} sandbagsStop {14} impact {15}x{16}",
                seed, t, PathViolation(g, sx, sz, dx, dz, cells, kind, mass, s), W, H, g.Dump(), sx, sz, dx, dz, cells, kind, mass, s.intoPits, s.sandbagsStop, s.impactEnabled, s.impactFactor);
        }
        string detail = kinds2.Count == 0 ? ("seed " + seed + ", " + n + " random grids: a contiguous line of exactly the planned steps, never past a wall/door/water/edge/open pit/pawn, never resting on sandbags, dest = travelled steps out, corners never cut, impact only on early pawn stops")
            : string.Join(" || ", kinds2.Select(kv => "[" + kv.Key + " x" + counts[kv.Key] + "] " + kv.Value)) + " (cell codes: 0 open 1 wall 2 door 3 sandbag 4 pawn 5 pit 6 cover 7 water)";
        Row("L1_PATH_RANDOM_CONSERVATION", new[] { "inv_kernel", "no_teleport", "thrown_into_pit_falls", "wall_stops_dead", "doors_and_deep_water_stop", "pawn_hits_pawn_stops" }, "random",
            kinds2.Count == 0 ? "PASS" : "FAIL", n, detail);
    }

    // goods_arc_spin_rebound: wild = 1.6 x the unrounded kernel throw, inside sc_storeroom_mortar's whole-cell band
    static void WildRows(int seed)
    {
        var rnd = new Random(seed); var k = new Chk(); string first = null; int beyond = 0;
        for (int t = 0; t < 20000; t++)
        {
            float r = (float)(0.9 + rnd.NextDouble() * 8), d = (float)(rnd.NextDouble() * r);
            float f = (float)(rnd.NextDouble() * 2), m = (float)(0.1 + rnd.NextDouble() * 75);
            var s = Shipped(x => x.maxCells = 1 + rnd.Next(10));
            int kc = Throw(d, r, f, m, s), wc = RM_KnockbackMath.WildCells(d, r, f, m, s, WILD);
            int lo = (int)Math.Round(WILD * (kc - 0.5), MidpointRounding.AwayFromZero), hi = (int)Math.Round(WILD * (kc + 0.5), MidpointRounding.AwayFromZero);
            bool ok = kc == 0 ? wc <= 1 : (wc >= kc && wc <= s.maxCells && (wc >= Math.Min(lo, s.maxCells) && wc <= Math.Min(hi, s.maxCells)));
            if (kc > 0 && kc < s.maxCells && wc > kc) beyond++;
            k.T(ok, "x");
            if (!ok && first == null) first = string.Format(IC, "seed {0} case {1}: r {2} d {3} f {4} m {5} cap {6}: kernel {7} wild {8} band {9}..{10}", seed, t, r, d, f, m, s.maxCells, kc, wc, lo, hi);
        }
        var s6 = Shipped();
        k.T(RM_KnockbackMath.WildCells(1f, MORTAR_R, 1f, 70f, s6, WILD) > Throw(1f, MORTAR_R, 1f, 70f, s6), "a good beside the mortar flies farther than the colonist");
        Row("L1_WILD_BAND_RANDOM", new[] { "goods_arc_spin_rebound", "inv_goods_fly" }, "random", k.V, k.n,
            k.bad.Count == 0 ? "seed " + seed + ": wild cells " + WILD + " x the unrounded throw always inside the whole-cell band, never below the kernel, never past the cap (" + beyond + " cases strictly farther); a near good beside the mortar flies farther than the colonist" : first);
        // zero-kernel: a rim thing whose throw rounds to 0 but whose wild throw is 1 — inv_too_weak_skip says a 0-cell kernel throw is not thrown
        int z1 = 0;
        for (float d = 0f; d < 2.9f; d += 0.01f) if (Throw(d, MORTAR_R, 1f, 70f, s6) == 0 && RM_KnockbackMath.WildCells(d, MORTAR_R, 1f, 70f, s6, WILD) >= 1) z1++;
        Row("L1_WILD_RIM_ZERO_KERNEL", new[] { "inv_too_weak_skip", "every_good_moves" }, "info", "INFO", 290,
            z1 + " of 290 rim distances (mortar, 70 kg good) give kernel 0 but wild 1: whether the game skips them too_weak (kernel) or throws them (wild) is game-side; the bars say 'a thing reached is one whose kernel throw is at least one cell'");
    }

    static void ReboundRows()
    {
        var k = new Chk();
        for (int left = 0; left <= 12; left++)
        {
            int rc = RM_KnockbackMath.ReboundCells(left, KEEP);
            k.T(rc <= left && (left == 0 ? rc == 0 : rc < left), "keep " + KEEP + "% of " + left + " -> " + rc + " (must lose energy)");
            k.T(Math.Abs(rc - left * KEEP / 100f) < 1f, "about 70%: " + left + " -> " + rc);
        }
        // a rebound chain always runs out below 100%
        foreach (float kp in new[] { 0f, 10f, 50f, 70f, 99f })
        {
            int c = 10, steps = 0; while (c > 0 && steps < 100) { c = RM_KnockbackMath.ReboundCells(c, kp); steps++; }
            k.T(c == 0 && steps < 100, "chain at " + kp + "% ends");
        }
        k.T(RM_KnockbackMath.ReboundCells(5, 100f) == 5 && RM_KnockbackMath.ReboundCells(5, 150f) == 5, "100% keeps all (MaxBounces ends it)");
        // Reflect: a straight hit flips the axis it struck
        var g = Lane(10, (2, KbCell.Wall));
        var res = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Item, 5f, Shipped());
        k.T(RM_KnockbackMath.Reflect(g, res, 1f, 0f, out float rx, out float rz) && rx == -1f && rz == 0f, "straight reflect " + rx + "," + rz);
        var none = RM_KnockbackMath.Resolve(Lane(10), 0, 1, 1f, 0f, 3, KbKind.Item, 5f, Shipped());
        k.T(!RM_KnockbackMath.Reflect(Lane(10), none, 1f, 0f, out _, out _), "no hit, no reflect");
        // diagonal into a flat wall (wall along x = 3 column): flips x only
        var gd = new Grid(8, 8); for (int z = 0; z < 8; z++) gd.c[3, z] = KbCell.Wall;
        var rd = RM_KnockbackMath.Resolve(gd, 0, 0, 1f, 1f, 5, KbKind.Item, 5f, Shipped());
        bool ok = RM_KnockbackMath.Reflect(gd, rd, 1f, 1f, out float ax, out float az);
        k.T(ok && ax == -1f && az == 1f, "diagonal into a flat wall: " + ax + "," + az + " dest " + rd.destX + "," + rd.destZ);
        Row("L1_REBOUND", new[] { "goods_arc_spin_rebound", "inv_goods_fly" }, "fixed", k.V, k.n,
            k.D("each rebound keeps about 70% (rounded down, always losing below 100%, so a chain ends); a straight hit flips its axis, a diagonal into a flat wall flips one axis"));
    }

    static void ContainerRows()
    {
        var k = new Chk(); var s = Shipped();
        k.T(RM_KnockbackMath.ContainerThrowCells(true, CONTAINER, CONTAINER, 1f, MORTAR_R, 1f, s) >= 1, "at the container limit thrown at least a cell");
        k.T(RM_KnockbackMath.ContainerThrowCells(true, CONTAINER + 1f, CONTAINER, 1f, MORTAR_R, 1f, s) == 0, "over -> jolt");
        k.T(RM_KnockbackMath.ContainerThrowCells(false, 30f, CONTAINER, 1f, MORTAR_R, 1f, s) == 0, "2x2 -> jolt");
        // a container (75 to 250 kg, 'the 75-to-250 kg locker') is still thrown: the goods limit does not apply
        k.T(RM_KnockbackMath.ContainerThrowCells(true, 200f, CONTAINER, 1f, MORTAR_R, 1f, s) >= 1, "a 200 kg locker thrown a short way");
        // short way: never farther than the same contents loose
        var rnd = new Random(77); int bad = 0;
        for (int t = 0; t < 5000; t++)
        {
            float goods = (float)(rnd.NextDouble() * 75), own = (float)(5 + rnd.NextDouble() * 100), d = (float)(rnd.NextDouble() * 3);
            int c = RM_KnockbackMath.ContainerThrowCells(true, own + goods, CONTAINER, d, MORTAR_R, 1f, s);
            if (c > Throw(d, MORTAR_R, 1f, goods, s) || c > s.maxCells) bad++;
        }
        k.T(bad == 0, bad + " seeded (77) containers flew farther than their goods loose");
        Row("L1_CONTAINER_THROW", new[] { "closed_container_holds", "inv_container_shove" }, "fixed", k.V, k.n,
            k.D("a 1x1 container at or under 250 kg is thrown a short way (never farther than its goods loose, never past the cap), over the limit or bigger than 1x1 jolts"));
    }

    static void HeavyKnockRows()
    {
        var k = new Chk();
        bool hit = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 75f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out float dmg, out int stun);
        k.T(hit && dmg >= 2f && dmg <= 5f && stun == STAGGER && STAGGER >= 25 && STAGGER <= 35, "steel: " + hit + " " + dmg + " " + stun + " (2-5 blunt, about half a second)");
        k.T(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, HEAVY_MIN - 0.1f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out _, out _), "a light stack passes");
        k.T(RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, HEAVY_MIN, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out _, out _), "10 kg is heavy");
        k.T(!RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 50f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out _, out _), "off: stacks pass");
        k.T(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 50f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out _, out _), "no person");
        foreach (float roll in new[] { -1f, 0f, 0.999f, 2f })
        {
            RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, roll, STAGGER, out float d2, out _);
            k.T(d2 >= HEAVY_DMIN && d2 <= HEAVY_DMAX, "roll " + roll + " dmg " + d2);
        }
        RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 50f, 5f, 4f, 1f, 0.9f, -3, out float d3, out int s3);
        k.T(d3 == 4f && s3 == 0, "max under min -> min; negative stagger -> 0");
        bool corpseHit = RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 60f, HEAVY_MIN, HEAVY_DMIN, HEAVY_DMAX, 0.5f, STAGGER, out _, out _);
        Row("L1_HEAVY_KNOCK", new[] { "heavy_stack_knocks", "inv_heavy_knock" }, "fixed", k.V, k.n,
            k.D("a stack of 10 kg or more reaching a person hits 2-5 blunt with a 30-tick stagger; lighter, no person or off passes"));
        Row("L1_HEAVY_KNOCK_CORPSE", new[] { "heavy_stack_knocks" }, "info", "INFO", 1,
            "a flying 60 kg corpse reaching a person: HeavyKnock = " + corpseHit + "; the leaf speaks of a heavy thrown STACK, so a corpse passing is consistent with the words; noted only");
    }

    static void ImmunityShieldRows()
    {
        var k = new Chk();
        k.T(!KbImmunity.CanLaunch(100, 50, 150, RECOVERY), "inside stun");
        k.T(!KbImmunity.CanLaunch(150 + RECOVERY - 1, 50, 150, RECOVERY), "inside recovery");
        k.T(KbImmunity.CanLaunch(150 + RECOVERY, 50, 150, RECOVERY), "after recovery");
        k.T(!KbImmunity.CanLaunch(200, 190, 100, RECOVERY), "stun ended before landing: measured from landing");
        k.T(KbImmunity.CanLaunch(51, 50, 150, 0), "window 0 allows chains");
        k.T(KbShield.EnergyAfter(1f, 1f, 10f, 0.033f) < 1f, "the shield pays extra charge");
        k.T(KbShield.EnergyAfter(1f, -1f, 10f, 0.033f) == 1f, "negative force never pays back");
        k.T(KbShield.EnergyAfter(1f, 1f, 0f, 0.033f) == 1f, "debit 0 = no extra");
        k.T(Math.Abs(KbShield.EnergyAfter(1f, 2f, 10f, 0.03f) - 0.4f) < 1e-5f, "force 2 x 10 x 0.03 = 0.6 debit");
        Row("L1_IMMUNITY_SHIELD", new[] { "recovery_immunity", "shield_belt_holds", "inv_recovery", "inv_shield" }, "fixed", k.V, k.n,
            k.D("no relaunch until stun end AND the recovery window; window 0 chains; the shield pays force x debit x energy loss"));
    }

    static void LedgerRows()
    {
        var k = new Chk(); var L = new KbExplosionLedger(600);
        k.T(L.TryAdd(1, 7, 0), "first"); k.T(!L.TryAdd(1, 7, 10), "repeat callback enqueues nothing");
        k.T(!L.TryAdd(1, 7, 1199), "still remembered at 1199"); k.T(L.TryAdd(2, 7, 1199), "another explosion");
        var rnd = new Random(31); var L2 = new KbExplosionLedger(600); var first = new Dictionary<long, int>(); int bad = 0, now = 0;
        for (int t = 0; t < 20000; t++)
        {
            now += rnd.Next(40); int e = rnd.Next(30), th = rnd.Next(20); long key = ((long)e << 32) | (uint)th;
            bool added = L2.TryAdd(e, th, now);
            if (first.TryGetValue(key, out int at) && now - at < 600 && added) bad++;
            if (added) first[key] = now;
        }
        k.T(bad == 0, bad + " repeats inside the window enqueued twice (seed 31)");
        L.AddLaunched(5, 100); L.AddLaunched(5, 700);
        k.T(L.Launched(5, 700) == 2, "launch count spans a rotation");
        Row("L1_EXPLOSION_LEDGER", new[] { "every_good_moves", "inv_kernel" }, "random", k.V, k.n,
            k.D("each (explosion, thing) pair is queued once inside the memory window (exactly one throw request per explosion), across generation rotations"));
    }

    static void MiscRows()
    {
        var k = new Chk();
        k.T(RM_KnockbackMath.ShoveCellFree(KbCell.Open, false), "open free");
        foreach (KbCell c in Enum.GetValues(typeof(KbCell))) if (c != KbCell.Open) k.T(!RM_KnockbackMath.ShoveCellFree(c, false), "shove into " + c);
        k.T(!RM_KnockbackMath.ShoveCellFree(KbCell.Open, true), "occupied");
        k.T(!RM_KnockbackMath.GoodsHeld(true, false, false), "open shelf protects nothing");
        k.T(RM_KnockbackMath.GoodsHeld(true, true, false), "closed container keeps its goods");
        k.T(!RM_KnockbackMath.GoodsHeld(false, true, false), "not on storage");
        k.T(RM_KnockbackMath.GoodsHeld(true, false, true), "old rule back on");
        float worst = 0f;
        for (int t = -2; t < 40; t++) { RM_KnockbackMath.JoltOffset(t, 30, 0.2f, 3f, 4f, out float ox, out float oz); worst = Math.Max(worst, (float)Math.Sqrt(ox * ox + oz * oz)); if (t < 0 || t >= 30) k.T(ox == 0f && oz == 0f, "jolt outside " + t); }
        k.T(worst <= 0.2f + 1e-5f && worst > 0f, "jolt bounded " + worst);
        for (int t = 0; t < 1000; t++) { RM_KnockbackMath.EpicentreDir(t, t * 7 + 1, out float dx, out float dz); k.T(Math.Abs(dx * dx + dz * dz - 1f) < 1e-4f, "epicentre unit"); RM_KnockbackMath.EpicentreDir(t, t * 7 + 1, out float dx2, out float dz2); k.T(dx == dx2 && dz == dz2, "deterministic"); }
        var fs = KbFrameStats.Summarize(new[] { 10f, 60f, 20f }, new[] { false, true, false }, new[] { 1, 9, 2 }, 3, 0.09f);
        k.T(fs.worstMs == 20f && fs.maxInAir == 9, "worst frame is the max of unpaused rows");
        var ok = KbFrameStats.Summarize(Enumerable.Repeat(16f, 100).Concat(new[] { 49f }).ToArray(), new bool[101], new int[101], 101, 1.649f);
        k.T(KbFrameStats.WithinBudget(ok, 50f, out _) && !KbFrameStats.WithinBudget(KbFrameStats.Summarize(new[] { 51f }, new[] { false }, new[] { 0 }, 1, 0.051f), 50f, out _), "50 ms budget");
        Row("L1_MISC_SHOVE_STORAGE_JOLT_FRAME", new[] { "open_shelf_scatters", "closed_container_holds", "thrown_into_pit_falls", "frame_time_probe", "barrage_frame_budget" }, "fixed", k.V, k.n,
            k.D("a shove only onto free open ground (never a pit or cover); open storage protects nothing unless the old rule is on; jolt bounded; worst frame = max unpaused"));
    }

    // the shipped settings swept through their slider ranges (kernel-reaching ones), every switch off included
    static void SettingsSweep(int seed)
    {
        var k = new Chk(); var rnd = new Random(seed); string first = null;
        void T(bool ok, string what) { k.T(ok, what); if (!ok && first == null) first = what; }
        // strength 0..3: 0 throws nothing; monotone
        int prev = -1;
        for (float st = 0f; st <= 3.0001f; st += 0.25f)
        {
            int c = Throw(1f, MORTAR_R, 1f, 70f, Shipped(x => x.globalMultiplier = st));
            T(st == 0f ? c == 0 : c >= prev, "strength " + st + " -> " + c);
            prev = c;
        }
        // max throw 1..10 caps every throw
        for (int cap = 1; cap <= 10; cap++) T(Throw(0f, 5.9f, 3f, 5f, Shipped(x => x.maxCells = cap)) == cap, "cap " + cap);
        // own-cap scale 0.25..2 on an own maximum of 4
        foreach (float sc in new[] { 0.25f, 0.5f, 1f, 1.5f, 2f }) T(KbLookup.Apply(Shipped(), new KbConfig { ownCap = 4 }, MAXCELLS, sc).maxCells == Math.Max(1, (int)Math.Round(4 * sc, MidpointRounding.AwayFromZero)), "scale " + sc);
        // creature limit 20..500 with a 120 kg animal; goods limit 5..200 with a 65 kg good
        for (float lim = 20f; lim <= 500f; lim += 20f) T(RM_KnockbackMath.Eligible(KbKind.Pawn, 120f, Shipped(x => x.creatureMassLimit = lim)) == (120f <= lim), "creature limit " + lim);
        for (float lim = 5f; lim <= 200f; lim += 5f) T(RM_KnockbackMath.Eligible(KbKind.Item, 65f, Shipped(x => x.lightMassLimit = lim)) == (65f <= lim), "goods limit " + lim);
        // blast power reference percent 25..400 at double damage: monotone down in the percent
        prev = int.MaxValue;
        for (float pc = 25f; pc <= 400f; pc += 25f) { int c = Throw(1f, MORTAR_R, RM_KnockbackMath.DamageRatio(100f, 50f, pc, true), 70f, Shipped()); T(c <= prev, "ref percent " + pc + " -> " + c); prev = c; }
        // impact per cell 0..15, on and off
        for (float ip = 0f; ip <= 15f; ip += 1.5f)
            foreach (bool on in new[] { true, false })
            {
                var r = RM_KnockbackMath.Resolve(Lane(10, (2, KbCell.Wall)), 0, 1, 1f, 0f, 3, KbKind.Pawn, 70f, Shipped(x => { x.impactPerCell = ip; x.impactEnabled = on; }));
                T(on && ip > 0f ? r.impact > 0f : r.impact == 0f, "impact " + on + " " + ip + " -> " + r.impact);
            }
        // container limit 20..1000 on a 240 kg locker
        for (float cl = 20f; cl <= 1000f; cl += 20f) T((RM_KnockbackMath.ContainerThrowCells(true, 240f, cl, 0.5f, MORTAR_R, 1f, Shipped()) > 0) == (240f <= cl), "container limit " + cl);
        // heavy threshold 1..75
        for (float hm = 1f; hm <= 75f; hm += 2f) T(RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 20f, hm, 2f, 5f, 0.5f, 30, out _, out _) == (20f >= hm), "heavy threshold " + hm);
        // recovery 0..600
        for (int w = 0; w <= 600; w += 30) T(KbImmunity.CanLaunch(200 + w, 100, 200, w) && (w == 0 || !KbImmunity.CanLaunch(199 + w, 100, 200, w)), "recovery " + w);
        // rebound keep 0..100
        for (float kp = 0f; kp <= 100f; kp += 5f) { int rc = RM_KnockbackMath.ReboundCells(6, kp); T(rc >= 0 && rc <= 6 && (kp < 100f ? rc < 6 : rc == 6), "keep " + kp + " -> " + rc); }
        // gas goods cells 1..6, exact at any cap scale
        for (int gc = 1; gc <= 6; gc++) T(KbLookup.Apply(Shipped(), new KbConfig { ownCap = gc, scaleOwnCap = false }, MAXCELLS, 0.25f + (float)rnd.NextDouble() * 1.75f).maxCells == gc, "gas cells " + gc);
        // random combos: invariants under every kernel-reaching setting at once
        for (int t = 0; t < 5000; t++)
        {
            float st = (float)(rnd.NextDouble() * 3); int cap = 1 + rnd.Next(10);
            var s = Shipped(x => { x.globalMultiplier = st; x.maxCells = cap; x.creatureMassLimit = 20f + (float)rnd.NextDouble() * 480; x.lightMassLimit = 5f + (float)rnd.NextDouble() * 195; x.sandbagsStop = rnd.Next(2) == 0; x.intoPits = rnd.Next(2) == 0; x.impactEnabled = rnd.Next(2) == 0; x.impactPerCell = (float)rnd.NextDouble() * 15; });
            float m = (float)(1 + rnd.NextDouble() * 300), d = (float)(rnd.NextDouble() * 3);
            int c = Throw(d, MORTAR_R, (float)rnd.NextDouble() * 2, m, s);
            T(c >= 0 && c <= cap && (st > 0f || c == 0), "combo " + t + " seed " + seed + " -> " + c);
        }
        Row("L1_SETTINGS_SWEEP", new[] { "settings_scale_and_switch", "inv_settings", "inv_kernel" }, "sweep", k.V, k.n,
            k.bad.Count == 0 ? "seed " + seed + ": strength 0-3 (0 = nothing), cap 1-10, cap scale 0.25-2, creature limit 20-500, goods limit 5-200, reference 25-400%, impact 0-15 on/off, container limit 20-1000, heavy 1-75, recovery 0-600, keep 0-100, gas cells 1-6, 5000 random combos: each takes effect on its own outcome and nothing passes the cap" : first);
    }
}
