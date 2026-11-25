// Blind lane 1, cycle 5 (judge-1794890427): ExplosiveKnockback's Verse-free kernel RM_KnockbackMath.cs tested from the bars
// alone (tree.json, sheet.md, plan.md, record.json inventory rows, the shipped settings). Written before any builder test was
// opened. One JSON row per line on stdout. Random rows print their seed and, on a failure, the shrunk case.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

public static class BlindLane1
{
    sealed class G : IKbGrid
    {
        public int W, H;
        public Dictionary<(int, int), KbCell> c = new Dictionary<(int, int), KbCell>();
        public G(int w, int h) { W = w; H = h; }
        public KbCell At(int x, int z)
        {
            if (x < 0 || z < 0 || x >= W || z >= H) return KbCell.OutOfBounds;
            return c.TryGetValue((x, z), out var v) ? v : KbCell.Open;
        }
        public G Set(int x, int z, KbCell v) { c[(x, z)] = v; return this; }
        public G Clone() { var g = new G(W, H); foreach (var kv in c) g.c[kv.Key] = kv.Value; return g; }
        public string Dump() => string.Join(" ", c.Where(kv => kv.Value != KbCell.Open).Select(kv => kv.Key.Item1 + "," + kv.Key.Item2 + "=" + kv.Value));
    }

    static readonly List<string> rows = new List<string>();
    static string J(string s) => "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static void Row(string id, string[] bars, string kind, bool? ok, int cases, string detail)
    {
        string v = ok == null ? "INFO" : (ok.Value ? "PASS" : "FAIL");
        Console.WriteLine("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind)
            + ",\"verdict\":" + J(v) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static string F(float f) => f.ToString("0.###", CultureInfo.InvariantCulture);
    static KbSettings Def() => new KbSettings();   // the kernel's defaults; checked against RM_KnockbackMod.cs below
    // shipped defaults from RM_KnockbackMod.cs (BlindLane1.py checks the three default lists there agree)
    const float MORTAR_R = 2.9f, COLONIST = 70f, RAT = 2f, MUFFALO = 144f, THRUMBO = 240f;

    sealed class Check
    {
        public int cases; public List<string> bad = new List<string>();
        public void T(bool ok, string what) { cases++; if (!ok && bad.Count < 6) bad.Add(what); else if (!ok) bad.Add("..."); }
        public bool Ok => bad.Count == 0;
        public string D(string pass) => Ok ? pass : "FAILED: " + string.Join(" | ", bad.Take(6));
    }

    static KbResult East(G g, int cells, KbKind k = KbKind.Pawn, float mass = COLONIST, KbSettings s = null)
        => RM_KnockbackMath.Resolve(g, 2, 5, 1f, 0f, cells, k, mass, s ?? Def());

    public static void Main()
    {
        // ---------------- kernel defaults equal the shipped settings ----------------
        {
            var c = new Check(); var s = Def();
            c.T(s.maxCells == 6, "maxCells " + s.maxCells); c.T(s.creatureMassLimit == 150f, "creatureMassLimit"); c.T(s.lightMassLimit == 75f, "lightMassLimit");
            c.T(s.impactPerCell == 4f, "impactPerCell"); c.T(!s.sandbagsStop, "sandbagsStop"); c.T(s.intoPits, "intoPits"); c.T(s.impactEnabled, "impactEnabled");
            c.T(s.globalMultiplier == 1f, "strength");
            Row("K_KERNEL_DEFAULTS_MATCH_SHIPPED", new[] { "inv_kernel", "inv_settings" }, "fixed", c.Ok, c.cases, c.D("KbSettings defaults = RM_KnockbackMod.cs shipped values (max 6, creature 150, goods 75, impact 4/cell, sandbags pass, into pits)"));
        }
        // ---------------- people thrown three cells (mortar r 2.9, one cell, clothed colonist 64-76 kg) ----------------
        {
            var c = new Check();
            for (int m = 64; m <= 76; m++) c.T(RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f, m, Def()) == 3, "mass " + m + " -> " + RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f, m, Def()));
            var r = East(new G(20, 11), RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f, COLONIST, Def()));
            c.T(r.destX == 5 && r.destZ == 5 && r.stop == KbStop.Distance && r.impact == 0f, "open ground dest " + r.destX + "," + r.destZ + " " + r.stop);
            Row("K_MORTAR_THROWS_COLONIST_THREE", new[] { "inv_kernel", "people_thrown_three_cells" }, "fixed", c.Ok, c.cases, c.D("mortar r2.9 at 1 cell throws a 64-76 kg colonist 3 cells straight away, no impact on open ground"));
        }
        // ---------------- over sandbags and barricades ----------------
        {
            var c = new Check();
            foreach (int at in new[] { 3, 4 })
            {
                var r = East(new G(20, 11).Set(at, 5, KbCell.Partial), 3);
                c.T(r.destX == 5 && r.stop == KbStop.Distance && r.impact == 0f, "partial at " + at + " -> dest " + r.destX + " " + r.stop);
            }
            var land = East(new G(20, 11).Set(5, 5, KbCell.Partial), 3);
            c.T(land.destX == 4 && land.cellsTravelled == 2, "throw ending on a sandbag rests " + land.destX + " (want the cell before)");
            var on = new KbSettings { sandbagsStop = true };
            var st = East(new G(20, 11).Set(4, 5, KbCell.Partial), 3, KbKind.Pawn, COLONIST, on);
            c.T(st.destX == 3 && st.stop == KbStop.PartialCover, "sandbagsStop on: " + st.destX + " " + st.stop);
            var item = East(new G(20, 11).Set(4, 5, KbCell.Partial), 3, KbKind.Item, 1f, on);
            c.T(item.destX == 5, "goods go over sandbags even with sandbagsStop on: " + item.destX);
            Row("K_OVER_SANDBAGS_AND_BARRICADES", new[] { "inv_kernel", "people_thrown_three_cells", "goods_arc_spin_rebound" }, "fixed", c.Ok, c.cases,
                c.D("a sandbag/barricade (Partial) line does not shorten a 3-cell throw; nothing rests on one; the opt-in setting stops pawns only"));
        }
        // ---------------- heavier flies less, bigger blast farther (the leaf's own numbers) ----------------
        {
            var c = new Check(); var s = Def();
            float r1 = RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true), r2 = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
            c.T(r1 == 1f && r2 == 2f, "ratio " + F(r1) + " " + F(r2));
            int[] want1 = { 5, 3, 2 }, want2 = { 6, 5, 4 }; float[] mass = { RAT, COLONIST, MUFFALO };
            for (int i = 0; i < 3; i++)
            {
                int a = RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f * r1, mass[i], s), b = RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f * r2, mass[i], s);
                c.T(a == want1[i], "mass " + mass[i] + " at ref " + a + " want " + want1[i]);
                c.T(b == want2[i], "mass " + mass[i] + " at x2 " + b + " want " + want2[i]);
                c.T(RM_KnockbackMath.Eligible(KbKind.Pawn, mass[i], s), "mass " + mass[i] + " eligible");
            }
            c.T(!RM_KnockbackMath.Eligible(KbKind.Pawn, THRUMBO, s), "thrumbo 240 kg not thrown at 150");
            var s250 = new KbSettings { creatureMassLimit = 250f };
            c.T(RM_KnockbackMath.Eligible(KbKind.Pawn, THRUMBO, s250), "thrumbo eligible at 250");
            int t1 = RM_KnockbackMath.ThrowCells(1f, MORTAR_R, r1, THRUMBO, s250), t2 = RM_KnockbackMath.ThrowCells(1f, MORTAR_R, r2, THRUMBO, s250);
            c.T(t1 == 1 && t2 == 3, "thrumbo at 250 kg limit " + t1 + " then " + t2 + " want 1 then 3");
            float off = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false);
            c.T(off == 1f, "blastPowerFromDamage off ratio " + F(off));
            Row("K_HEAVIER_FLIES_LESS_LEAF_NUMBERS", new[] { "inv_kernel", "heavier_flies_less", "inv_creature_mass_limit", "inv_blast_power_damage" }, "fixed", c.Ok, c.cases,
                c.D("rat/colonist/muffalo 5/3/2 at damage 50, 6/5/4 at 100, thrumbo spared at 150 and 1/3 at 250; switch off = ratio 1"));
        }
        // ---------------- monotonicity, random ----------------
        {
            int seed = 50501; var rng = new Random(seed); var c = new Check(); string shrunk = "";
            for (int i = 0; i < 20000; i++)
            {
                float radius = 0.5f + (float)rng.NextDouble() * 8f, d = (float)rng.NextDouble() * radius * 1.2f, force = (float)rng.NextDouble() * 3f;
                float m1 = 0.1f + (float)rng.NextDouble() * 300f, m2 = m1 + (float)rng.NextDouble() * 100f;
                var s = new KbSettings { globalMultiplier = (float)rng.NextDouble() * 3f, maxCells = 1 + rng.Next(10) };
                int a = RM_KnockbackMath.ThrowCells(d, radius, force, m1, s), b = RM_KnockbackMath.ThrowCells(d, radius, force, m2, s);
                int nearer = RM_KnockbackMath.ThrowCells(d * 0.5f, radius, force, m1, s), stronger = RM_KnockbackMath.ThrowCells(d, radius, force * 1.5f, m1, s);
                bool ok = b <= a && nearer >= a && stronger >= a && a >= 0 && a <= s.maxCells && (d < radius || a == 0);
                c.T(ok, "i" + i);
                if (!ok && shrunk == "") shrunk = "r=" + F(radius) + " d=" + F(d) + " f=" + F(force) + " m1=" + F(m1) + " m2=" + F(m2) + " -> " + a + "/" + b + "/" + nearer + "/" + stronger;
            }
            Row("K_THROW_MONOTONE_RANDOM", new[] { "inv_kernel", "heavier_flies_less", "settings_scale_and_switch" }, "random", c.Ok, c.cases,
                c.D("seed " + seed + ": heavier never farther, nearer/stronger never shorter, 0..max cells, 0 at or past the radius") + (shrunk == "" ? "" : " shrunk " + shrunk));
        }
        // ---------------- the spared: mass limits and the rim ----------------
        {
            var c = new Check(); var s = Def();
            c.T(RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 150.01f, s), "pawn limit 150 inclusive");
            c.T(RM_KnockbackMath.Eligible(KbKind.Item, 75f, s) && !RM_KnockbackMath.Eligible(KbKind.Item, 75.01f, s), "goods limit 75 inclusive");
            c.T(RM_KnockbackMath.Eligible(KbKind.Corpse, 75f, s) && !RM_KnockbackMath.Eligible(KbKind.Corpse, 75.01f, s), "corpse limit 75");
            c.T(RM_KnockbackMath.Eligible(KbKind.Pawn, 120f, s), "a living 120 kg pawn is not weighed by the 75 kg goods limit");
            var low = new KbSettings { creatureMassLimit = 20f };
            c.T(RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, low), "a 60 kg corpse is not weighed by a 20 kg creature limit");
            var g = new KbSettings { lightMassLimit = 300f };
            c.T(RM_KnockbackMath.Eligible(KbKind.Corpse, THRUMBO, g), "thrumbo corpse thrown with the goods limit raised (no body-size rule)");
            var ram = KbLookup.Apply(Def(), new KbConfig { massLimitOverride = 216f }, 6, 1f);
            c.T(RM_KnockbackMath.Eligible(KbKind.Pawn, 200f, ram) && !RM_KnockbackMath.Eligible(KbKind.Pawn, 220f, ram), "grav-ram 216 override");
            var none = KbLookup.Apply(Def(), new KbConfig { massLimitOverride = 0f }, 6, 1f);
            c.T(none.creatureMassLimit == 150f, "override 0 keeps the global");
            // the rim: a throw under one cell is no move
            int rim = RM_KnockbackMath.ThrowCells(2.75f, MORTAR_R, 1f, COLONIST, s);
            c.T(rim == 0, "rim throw " + rim);
            var rr = East(new G(20, 11), rim);
            c.T(!rr.Moved && rr.stop == KbStop.None, "rim result " + rr.stop);
            c.T(RM_KnockbackMath.ThrowCells(MORTAR_R, MORTAR_R, 1f, 1f, s) == 0 && RM_KnockbackMath.ThrowCells(5f, MORTAR_R, 1f, 1f, s) == 0, "at/past the radius 0");
            Row("K_SPARED_BY_MASS_AND_RIM", new[] { "inv_kernel", "the_spared", "inv_creature_mass_limit", "inv_mass_limit_skip", "inv_too_weak_skip", "inv_big_corpse_spared" }, "fixed", c.Ok, c.cases,
                c.D("creature limit weighs living pawns only (150, override 216), goods limit goods and corpses only (75), no body-size rule, a rim throw under 1 cell is no move"));
        }
        // ---------------- recovery immunity ----------------
        {
            var c = new Check();
            c.T(!KbImmunity.CanLaunch(100, 100, 160, 120), "inside stun");
            c.T(!KbImmunity.CanLaunch(279, 100, 160, 120), "inside recovery");
            c.T(KbImmunity.CanLaunch(280, 100, 160, 120), "after stun+recovery");
            c.T(!KbImmunity.CanLaunch(219, 200, 100, 20) && KbImmunity.CanLaunch(220, 200, 100, 20), "stun already over: from landing");
            c.T(KbImmunity.CanLaunch(100, 100, 160, 0), "window 0 = chain throws allowed");
            int seed = 50502; var rng = new Random(seed); bool mono = true; int n = 0;
            for (int i = 0; i < 5000; i++)
            {
                int land = rng.Next(100000), stun = land + rng.Next(300), w = rng.Next(601); bool prev = false;
                for (int t = land; t < stun + w + 5; t += 1 + rng.Next(7)) { bool now = KbImmunity.CanLaunch(t, land, stun, w); if (prev && !now) mono = false; prev = now; n++; }
            }
            c.T(mono, "seed " + seed + " CanLaunch non-monotone in time");
            Row("K_RECOVERY_IMMUNITY", new[] { "inv_kernel", "recovery_immunity", "inv_recovery" }, "fixed", c.Ok, c.cases + n,
                c.D("no relaunch before max(landing, stun end) + window; window 0 allows chains; once allowed always allowed (seed " + seed + ")"));
        }
        // ---------------- wall stops dead, pawn hits pawn, doors, deep water ----------------
        {
            var c = new Check(); var s = Def();
            var w = East(new G(20, 11).Set(5, 5, KbCell.Wall), 3);
            float want = 4f * (3 - w.cellsTravelled) / (float)Math.Sqrt(RM_KnockbackMath.MassScale(COLONIST, s));
            c.T(w.destX == 4 && w.cellsTravelled == 2 && w.stop == KbStop.Wall && w.impact > 0f && Math.Abs(w.impact - want) < 1e-4, "wall: dest " + w.destX + " " + w.stop + " impact " + F(w.impact));
            var ctrl = East(new G(20, 11), 3);
            c.T(ctrl.destX == 5, "control no wall " + ctrl.destX);
            var p = East(new G(20, 11).Set(5, 5, KbCell.Pawn), 3);
            c.T(p.destX == 4 && p.stop == KbStop.Pawn && p.hitOther && p.otherX == 5 && p.impact > 0f && p.impact == p.otherImpact, "pawn: " + p.destX + " " + p.stop + " " + F(p.impact) + "/" + F(p.otherImpact));
            var pi = East(new G(20, 11).Set(4, 5, KbCell.Pawn), 3, KbKind.Item, 1f);
            c.T(pi.destX == 5 && !pi.hitOther, "goods pass a pawn in the kernel (heavy knock is the carrier's): " + pi.destX);
            var d = East(new G(20, 11).Set(5, 5, KbCell.Door), 3);
            c.T(d.destX == 4 && d.stop == KbStop.Door && d.hitDoor && d.doorX == 5 && d.impact > 0f, "door: " + d.destX + " " + d.stop);
            var zero = KbLookup.Apply(Def(), new KbConfig { impactFactor = 0f }, 6, 1f);
            var w0 = East(new G(20, 11).Set(5, 5, KbCell.Wall), 3, KbKind.Pawn, COLONIST, zero);
            var p0 = East(new G(20, 11).Set(5, 5, KbCell.Pawn), 3, KbKind.Pawn, COLONIST, zero);
            var d0 = East(new G(20, 11).Set(5, 5, KbCell.Door), 3, KbKind.Pawn, COLONIST, zero);
            c.T(w0.impact == 0f && p0.impact == 0f && p0.otherImpact == 0f && d0.impact == 0f && w0.destX == 4 && d0.hitDoor, "impact factor 0: " + F(w0.impact) + "/" + F(p0.impact) + "/" + F(d0.impact));
            var off = East(new G(20, 11).Set(5, 5, KbCell.Wall), 3, KbKind.Pawn, COLONIST, new KbSettings { impactEnabled = false });
            c.T(off.impact == 0f && off.destX == 4, "impact off");
            var wat = East(new G(20, 11).Set(4, 5, KbCell.Water).Set(5, 5, KbCell.Water), 3);
            c.T(wat.destX == 3 && wat.stop == KbStop.Water, "water: " + wat.destX + " " + wat.stop);
            var watItem = East(new G(20, 11).Set(5, 5, KbCell.Water), 3, KbKind.Item, 1f);
            c.T(watItem.destX == 4 && watItem.stop == KbStop.Water, "goods never into deep water: " + watItem.destX);
            var edge = RM_KnockbackMath.Resolve(new G(6, 11), 4, 5, 1f, 0f, 3, KbKind.Pawn, COLONIST, s);
            c.T(edge.destX == 5 && edge.stop == KbStop.OutOfBounds, "map edge: " + edge.destX + " " + edge.stop);
            Row("K_WALL_PAWN_DOOR_WATER_STOP", new[] { "inv_kernel", "wall_stops_dead", "pawn_hits_pawn_stops", "doors_and_deep_water_stop", "per_weapon_tuning" }, "fixed", c.Ok, c.cases,
                c.D("wall/door/pawn: stop on the cell before with impact (pawn: split equally); impact factor 0 or impact off: none; water: last standable cell; map edge stops"));
        }
        // ---------------- pits ----------------
        {
            var c = new Check();
            var a = East(new G(20, 11).Set(4, 5, KbCell.Pit), 3);
            c.T(a.destX == 4 && a.stop == KbStop.Pit, "falls into the first pit cell: " + a.destX + " " + a.stop);
            var across = East(new G(20, 11).Set(3, 5, KbCell.Pit).Set(4, 5, KbCell.Pit), 5, KbKind.Item, 1f);
            c.T(across.destX == 3 && across.stop == KbStop.Pit, "nothing thrown across: " + across.destX);
            var offp = East(new G(20, 11).Set(4, 5, KbCell.Pit), 3, KbKind.Pawn, COLONIST, new KbSettings { intoPits = false });
            c.T(offp.destX == 3 && offp.stop == KbStop.Wall, "into pits off: a wall " + offp.destX + " " + offp.stop);
            var cov = East(new G(20, 11).Set(4, 5, KbCell.CoveredPit), 3);
            c.T(cov.destX == 5, "a covered pit is ground for the path: " + cov.destX);
            var covLand = East(new G(20, 11).Set(5, 5, KbCell.CoveredPit), 3, KbKind.Item, 1f);
            c.T(covLand.destX == 5 && RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, 7), "a stack landing on a cover breaks it");
            c.T(RM_KnockbackMath.LandingBreaksCover(KbKind.Corpse, true, false, 7), "a corpse breaks it");
            c.T(!RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, -3), "a gas burst's throw never breaks a cover");
            c.T(!RM_KnockbackMath.LandingBreaksCover(KbKind.Item, false, false, 7), "no cover, nothing to break");
            Row("K_PITS_FALL_NOT_ACROSS", new[] { "inv_kernel", "thrown_into_pit_falls", "inv_pits_receive", "blast_breaks_pit_cover" }, "fixed", c.Ok, c.cases,
                c.D("stops IN the first open pit cell, never across; into-pits off = wall; covered = ground; a stack/corpse landing on a cover breaks it, a gas throw never"));
            Row("I_PAWN_LANDING_ON_COVER_IS_GAME_SIDE", new[] { "thrown_into_pit_falls" }, "info", null, 1,
                "LandingBreaksCover(Pawn, covered) is false by design (the kernel says FlowWorks' trap handles a pawn): whether a thrown pawn landing on a cover falls through is game-side; lane 2 must read the caller");
        }
        // ---------------- shove cell (containers and gas) ----------------
        {
            var c = new Check();
            foreach (KbCell k in Enum.GetValues(typeof(KbCell)))
                c.T(RM_KnockbackMath.ShoveCellFree(k, false) == (k == KbCell.Open), "cell " + k);
            c.T(!RM_KnockbackMath.ShoveCellFree(KbCell.Open, true), "occupied");
            Row("K_SHOVE_CELL_FREE_TABLE", new[] { "inv_kernel", "closed_container_holds", "inv_container_shove" }, "fixed", c.Ok, c.cases,
                c.D("a shove enters only open, empty ground: never a pit, cover, wall, door, sandbag, water, edge or pawn"));
            Row("I_GAS_SHOVE_ONTO_PIT_NOT_THE_SHOVE_CELL_RULE", new[] { "thrown_into_pit_falls", "blast_breaks_pit_cover" }, "info", null, 1,
                "the bars say a gas shove onto an open pit drops the pawn in and onto a cover it stands; ShoveCellFree refuses both pit kinds, so the gas shove must NOT use it; lane 2 must read RM_MapComponent's gas shove");
        }
        // ---------------- shield ----------------
        {
            var c = new Check();
            c.T(Math.Abs(KbShield.EnergyAfter(1f, 1f, 10f, 0.033f) - (1f - 0.33f)) < 1e-5, "debit force x perForce x loss");
            c.T(KbShield.EnergyAfter(1f, -2f, 10f, 0.033f) == 1f && KbShield.EnergyAfter(1f, 1f, 0f, 0.033f) == 1f, "no debit for negative force or 0 per force");
            c.T(KbShield.EnergyAfter(0.1f, 1f, 10f, 0.033f) < 0f, "can break");
            Row("K_SHIELD_PAYS_EXTRA", new[] { "inv_kernel", "shield_belt_holds", "inv_shield" }, "fixed", c.Ok, c.cases, c.D("the belt pays force x debit x its energy loss per damage on top; never gains"));
        }
        // ---------------- goods fly wild, rebound ----------------
        {
            var c = new Check(); var s = new KbSettings { maxCells = 1000 };
            int seed = 50503; var rng = new Random(seed);
            for (int i = 0; i < 5000; i++)
            {
                float radius = 1f + (float)rng.NextDouble() * 6f, d = (float)rng.NextDouble() * radius, m = 0.1f + (float)rng.NextDouble() * 75f, f = (float)rng.NextDouble() * 2f;
                double raw = 4.0 * f * (1 - Math.Min(1, d / radius)) * Math.Min(2, Math.Max(0.25, Math.Sqrt(70.0 / Math.Max(m, 1f))));
                int w = RM_KnockbackMath.WildCells(d, radius, f, m, s, 1.6f);
                int want = (int)Math.Round(raw * 1.6, MidpointRounding.AwayFromZero); if (want < 1) want = 0;
                c.T(Math.Abs(w - want) <= 1, "i" + i + " wild " + w + " want ~" + want);
                c.T(RM_KnockbackMath.WildCells(d, radius, f, m, s, 1f) == RM_KnockbackMath.ThrowCells(d, radius, f, m, s), "wild 1 = kernel");
            }
            var capS = Def();
            int capped = RM_KnockbackMath.WildCells(1f, MORTAR_R, 1f, 1f, capS, 1.6f);
            c.T(capped <= capS.maxCells, "wild throw respects the max " + capped);
            Row("K_GOODS_WILD_ABOUT_1_6", new[] { "inv_kernel", "goods_arc_spin_rebound", "inv_goods_fly" }, "random", c.Ok, c.cases,
                c.D("seed " + seed + ": goods' cells = round(1.6 x the person kernel's unrounded throw) within 1, wild 1 = plain kernel, capped at the max"));
            Row("I_WILD_GOODS_CLIPPED_BY_MAX", new[] { "goods_arc_spin_rebound" }, "info", null, 1,
                "at the defaults a 1 kg good one cell from a mortar plans " + capped + " cells (1.6x would be " + F((float)(5.24 * 1.6)) + "): the global max 6 clips the 1.6x near a blast; the bar says 'about 1.6 times as far as a person' and the max is a setting that caps throws, so INFO not FAIL");
        }
        {
            var c = new Check();
            for (int n = 0; n <= 20; n++)
            {
                int k = RM_KnockbackMath.ReboundCells(n, 70f);
                c.T(k == (int)Math.Floor(n * 0.7 + 1e-4), "rebound " + n + " -> " + k);
                c.T(k < n || n == 0, "loses energy " + n);
                int chain = n, steps = 0; while (chain > 0 && steps < 100) { chain = RM_KnockbackMath.ReboundCells(chain, 70f); steps++; }
                c.T(chain == 0, "chain from " + n + " ends");
            }
            for (float keep = 0f; keep < 100f; keep += 0.5f)
            {
                int chain = 10, steps = 0; while (chain > 0 && steps < 1000) { chain = RM_KnockbackMath.ReboundCells(chain, keep); steps++; }
                c.T(chain == 0, "keep " + F(keep) + " ends");
            }
            c.T(RM_KnockbackMath.ReboundCells(10, 100f) == 10 && RM_KnockbackMath.ReboundCells(10, 150f) == 10, "100% loses nothing, clamps");
            c.T(RM_KnockbackMath.ReboundCells(10, 0f) == 0 && RM_KnockbackMath.ReboundCells(0, 70f) == 0, "0% none");
            // reflection: a straight hit flips the struck axis, a diagonal into a corner flips both
            var g = new G(20, 11).Set(6, 5, KbCell.Wall);
            var r = RM_KnockbackMath.Resolve(g, 2, 5, 1f, 0f, 6, KbKind.Item, 1f, Def());
            c.T(RM_KnockbackMath.Reflect(g, r, 1f, 0f, out float rx, out float rz) && rx == -1f && rz == 0f, "straight wall reflect " + F(rx) + "," + F(rz));
            var g2 = new G(20, 11); for (int z = 0; z < 11; z++) g2.Set(6, z, KbCell.Wall);
            var r2 = RM_KnockbackMath.Resolve(g2, 2, 2, 1f, 1f, 6, KbKind.Item, 1f, Def());
            bool okr = RM_KnockbackMath.Reflect(g2, r2, 1f, 1f, out rx, out rz);
            c.T(okr && rx == -1f && rz == 1f, "diagonal into an x-wall flips x only: " + F(rx) + "," + F(rz) + " block " + r2.blockX + "," + r2.blockZ);
            var open = RM_KnockbackMath.Resolve(new G(20, 11), 2, 5, 1f, 0f, 3, KbKind.Item, 1f, Def());
            c.T(!RM_KnockbackMath.Reflect(new G(20, 11), open, 1f, 0f, out rx, out rz), "no hit, no rebound");
            var door = RM_KnockbackMath.Resolve(new G(20, 11).Set(5, 5, KbCell.Door), 2, 5, 1f, 0f, 6, KbKind.Item, 1f, Def());
            c.T(door.hasBlock && RM_KnockbackMath.Reflect(new G(20, 11).Set(5, 5, KbCell.Door), door, 1f, 0f, out rx, out rz) && rx == -1f, "goods rebound off a closed door");
            Row("K_REBOUND_KEEPS_70_AND_ENDS", new[] { "inv_kernel", "goods_arc_spin_rebound", "inv_goods_fly" }, "fixed", c.Ok, c.cases,
                c.D("rebound keeps floor(70%) of the cells left, every keep under 100 ends, walls and closed doors reflect the struck axis"));
        }
        // ---------------- every good moves: no cap, conservation ----------------
        {
            int seed = 50504; var rng = new Random(seed); var c = new Check();
            for (int t = 0; t < 500; t++)
            {
                int n = rng.Next(200); var all = new List<KbCandidate>();
                for (int i = 0; i < n; i++) all.Add(new KbCandidate { index = i, kind = (KbKind)rng.Next(3), distance = (float)rng.NextDouble() * 6f });
                var kept = RM_KnockbackMath.Prioritise(all, -1);
                c.T(kept.Count == n && kept.Select(k => k.index).Distinct().Count() == n, "trial " + t + " no cap keeps all, once each");
                for (int i = 1; i < kept.Count; i++)
                {
                    int ra = kept[i - 1].kind == KbKind.Pawn ? 0 : (kept[i - 1].kind == KbKind.Corpse ? 1 : 2), rb = kept[i].kind == KbKind.Pawn ? 0 : (kept[i].kind == KbKind.Corpse ? 1 : 2);
                    c.T(ra < rb || (ra == rb && kept[i - 1].distance <= kept[i].distance), "order " + t);
                }
            }
            Row("K_NO_CAP_CONSERVES_CANDIDATES", new[] { "inv_kernel", "every_good_moves", "inv_perf_all_fly" }, "random", c.Ok, c.cases,
                c.D("seed " + seed + ": Prioritise with no cap returns every candidate exactly once (nothing created or lost), pawns then corpses then items, nearest first"));
        }
        // ---------------- storage: open shelves scatter, closed containers hold ----------------
        {
            var c = new Check();
            c.T(!RM_KnockbackMath.GoodsHeld(true, false, false), "open shelf holds nothing (shipped)");
            c.T(RM_KnockbackMath.GoodsHeld(true, true, false), "closed container holds");
            c.T(!RM_KnockbackMath.GoodsHeld(false, true, false) && !RM_KnockbackMath.GoodsHeld(false, false, true), "loose on the floor");
            c.T(RM_KnockbackMath.GoodsHeld(true, false, true), "old open-storage rule only when turned on");
            var s = Def();
            int box = RM_KnockbackMath.ContainerThrowCells(true, 120f, 250f, 1f, MORTAR_R, 1f, s);
            c.T(box == RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 1f, 120f, s) && box >= 1 && box <= s.maxCells, "1x1 120 kg thrown a short way " + box);
            c.T(RM_KnockbackMath.ContainerThrowCells(true, 250f, 250f, 1f, MORTAR_R, 1f, s) >= 1, "at the limit thrown");
            c.T(RM_KnockbackMath.ContainerThrowCells(true, 250.5f, 250f, 1f, MORTAR_R, 1f, s) == 0, "over the limit jolts");
            c.T(RM_KnockbackMath.ContainerThrowCells(false, 30f, 250f, 1f, MORTAR_R, 1f, s) == 0, "2x2 jolts");
            int seed = 50505; var rng = new Random(seed);
            for (int i = 0; i < 3000; i++)
            {
                float contents = (float)rng.NextDouble() * 75f, own = (float)rng.NextDouble() * 175f, d = (float)rng.NextDouble() * 3f;
                int ct = RM_KnockbackMath.ContainerThrowCells(true, own + contents, 250f, d, MORTAR_R, 1f, s);
                int loose = RM_KnockbackMath.WildCells(d, MORTAR_R, 1f, Math.Max(contents, 0.1f), s, 1.6f);
                c.T(ct <= loose, "container " + ct + " farther than its goods loose " + loose);
            }
            for (int t = -5; t < 40; t++)
            {
                RM_KnockbackMath.JoltOffset(t, 30, 0.15f, 3f, 4f, out float ox, out float oz);
                float mag = (float)Math.Sqrt(ox * ox + oz * oz);
                c.T(mag <= 0.15f + 1e-6f && ((t >= 0 && t < 30) || mag == 0f), "jolt t" + t + " " + F(mag));
            }
            Row("K_STORAGE_OPEN_SCATTERS_CLOSED_HOLDS", new[] { "inv_kernel", "open_shelf_scatters", "closed_container_holds", "inv_closed_guard", "inv_container_shove", "inv_shelf_skip" }, "fixed", c.Ok, c.cases,
                c.D("only a closed container holds; a 1x1 at or under 250 kg is thrown a short way (never farther than its goods loose, seed " + seed + "), else jolts within its amplitude"));
        }
        // ---------------- heavy stack knock ----------------
        {
            var c = new Check();
            c.T(RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 10f, 10f, 2f, 5f, 0.5f, 30, out float dmg, out int stun) && dmg == 3.5f && stun == 30, "10 kg hits " + F(dmg));
            for (float roll = 0f; roll < 1f; roll += 0.05f) { RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 30f, 10f, 2f, 5f, roll, 30, out dmg, out stun); c.T(dmg >= 2f && dmg <= 5f, "dmg " + F(dmg)); }
            c.T(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 9.99f, 10f, 2f, 5f, 0.5f, 30, out dmg, out stun) && dmg == 0f, "light passes");
            c.T(!RM_KnockbackMath.HeavyKnock(false, KbKind.Item, true, 30f, 10f, 2f, 5f, 0.5f, 30, out dmg, out stun), "off");
            c.T(!RM_KnockbackMath.HeavyKnock(true, KbKind.Corpse, true, 30f, 10f, 2f, 5f, 0.5f, 30, out dmg, out stun), "corpse not a stack");
            c.T(!RM_KnockbackMath.HeavyKnock(true, KbKind.Item, false, 30f, 10f, 2f, 5f, 0.5f, 30, out dmg, out stun), "nobody there");
            c.T(RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, 30f, 10f, 6f, 2f, 0.9f, -4, out dmg, out stun) && dmg == 6f && stun == 0, "max under min, negative stagger");
            Row("K_HEAVY_STACK_KNOCK", new[] { "inv_kernel", "heavy_stack_knocks", "inv_heavy_knock" }, "fixed", c.Ok, c.cases, c.D("a stack of 10 kg+ hits a standing pawn for 2-5 blunt and a 30-tick stagger; lighter, corpses, or off pass"));
        }
        // ---------------- which blasts, lookup order, fire half ----------------
        {
            var c = new Check();
            var u = KbLookup.Resolve(null, null, null, true, 1f); c.T(u.force == 1f && u.source == "unpatched", "unpatched harmful full");
            var h = KbLookup.Resolve(null, null, null, false, 1f); c.T(h.force == 0f, "harmless none");
            var u50 = KbLookup.Resolve(null, null, null, true, 0.5f); c.T(u50.force == 0.5f, "percent applies to an untuned type");
            var tuned = KbLookup.Resolve(null, null, new KbConfig { force = 0.5f }, true, 0.3f); c.T(tuned.force == 0.5f && tuned.source == "damageDef", "a tuned type keeps its tuning, the percent never stacked");
            var pr = KbLookup.Resolve(new KbConfig { force = 0f }, new KbConfig { force = 2f }, new KbConfig { force = 1f }, true, 1f);
            c.T(pr.force == 0f && pr.source == "projectile", "projectile zero wins");
            var we = KbLookup.Resolve(null, new KbConfig { force = 0.7f }, new KbConfig { force = 1f }, true, 1f); c.T(we.force == 0.7f && we.source == "weapon", "weapon over type");
            var s = Def();
            double bomb = 4.0 * 1.0 * (1 - 1 / 2.9) * Math.Sqrt(70 / 70.0), fire = bomb * 0.5;
            c.T(RM_KnockbackMath.ThrowCells(1f, MORTAR_R, 0.5f, COLONIST, s) == (int)Math.Round(fire, MidpointRounding.AwayFromZero), "fire half");
            c.T(RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn") && RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Whatever", "ElectricalBurn"), "fire off zeroes the type's own patch");
            c.T(!RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn"), "fire on");
            c.T(!RM_KnockbackMath.FireSwitchedOff(false, "projectile", "Flame", "Burn") && !RM_KnockbackMath.FireSwitchedOff(false, "weapon", "Flame", "Burn"), "a weapon's own tuning stays");
            c.T(!RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded"), "bomb unaffected");
            Row("K_WHICH_BLASTS_AND_LOOKUP", new[] { "inv_kernel", "every_harmful_blast_throws", "per_weapon_tuning", "inv_which_blasts", "inv_weapon_ext_fields" }, "fixed", c.Ok, c.cases,
                c.D("projectile > weapon > type > unpatched percent (harmful only, never stacked on a tuned type); zero wins; fire at half; fire switch off zeroes only the type's own fire patch"));
            Row("I_FIRE_HALF_ROUNDS_TO_ONE_THIRD", new[] { "every_harmful_blast_throws" }, "info", null, 1,
                "at the calibration point the bomb throws 3 cells and fire 1 (raw " + F((float)bomb) + " vs " + F((float)fire) + "): the force ratio is exactly 0.5 but whole cells round it to 1/3; the leaf's oracle reads 'ratio near 0.5', which a scene staged at that point cannot show");
        }
        // ---------------- caps and per-weapon maximum, gas goods cap ----------------
        {
            var c = new Check();
            c.T(RM_KnockbackMath.CapFor(0, 6, 0.5f) == 6, "0 = global"); c.T(RM_KnockbackMath.CapFor(2, 6, 1f) == 2, "own 2");
            c.T(RM_KnockbackMath.CapFor(4, 6, 0.5f) == 2, "own 4 x 0.5"); c.T(RM_KnockbackMath.CapFor(1, 6, 0.25f) == 1, "never below 1");
            var g = Def(); var snap = (g.maxCells, g.creatureMassLimit, g.impactFactor);
            var a = KbLookup.Apply(g, new KbConfig { ownCap = 2, impactFactor = 0.3f }, 6, 1f);
            c.T(a.maxCells == 2 && RM_KnockbackMath.ThrowCells(0f, MORTAR_R, 3f, 1f, a) == 2, "own max 2 throws 2");
            c.T((g.maxCells, g.creatureMassLimit, g.impactFactor) == snap, "Apply never mutates the global");
            var gas = KbLookup.Apply(g, new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 2f);
            c.T(gas.maxCells == 2, "gas burst goods cap exact under scale 2: " + gas.maxCells);
            var gasLow = KbLookup.Apply(g, new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 0.25f);
            c.T(gasLow.maxCells == 2, "and under scale 0.25");
            var neg = KbLookup.Apply(g, new KbConfig { impactFactor = -3f }, 6, 1f); c.T(neg.impactFactor == 0f, "negative impact factor -> 0");
            Row("K_CAPS_PER_WEAPON_AND_GAS", new[] { "inv_kernel", "per_weapon_tuning", "gas_goes_clump_by_clump", "inv_weapon_ext_fields" }, "fixed", c.Ok, c.cases,
                c.D("own max 0 = global, own max x cap scale (never under 1), gas goods cap 2 never rescaled, Apply copies"));
        }
        // ---------------- blast power ----------------
        {
            var c = new Check();
            c.T(RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true) == 1f, "normal damage = 1");
            c.T(RM_KnockbackMath.DamageRatio(10f, 10f, 100f, true) == 1f, "flame at its normal 10 = 1, keeps its half");
            c.T(RM_KnockbackMath.DamageRatio(100f, 50f, 200f, true) == 1f, "ref percent 200 halves");
            c.T(RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true) == 0f, "negative damage = 0");
            c.T(RM_KnockbackMath.DamageRatio(80f, 0f, 100f, true) == 1f && RM_KnockbackMath.DamageRatio(80f, 50f, 0f, true) == 1f, "no usable reference = 1");
            c.T(RM_KnockbackMath.DamageRatio(80f, float.NaN, 100f, true) == 1f, "NaN ref = 1");
            for (float pct = 25f; pct <= 400f; pct += 25f)
            {
                float r = RM_KnockbackMath.DamageRatio(100f, 50f, pct, true);
                c.T(Math.Abs(r - 200f / pct) < 1e-4, "pct " + pct + " " + F(r));
                c.T(RM_KnockbackMath.DamageRatio(100f, 50f, pct, false) == 1f, "off at pct " + pct);
            }
            Row("K_BLAST_POWER_FROM_DAMAGE", new[] { "inv_kernel", "heavier_flies_less", "inv_blast_power_damage", "settings_scale_and_switch" }, "sweep", c.Ok, c.cases,
                c.D("ratio = damage / (type default x percent/100), 1 at the type's normal damage or with no reference, off = 1 (damage ignored), swept 25-400%"));
        }
        // ---------------- the path: random grids ----------------
        {
            int seed = 50506; var rng = new Random(seed); var c = new Check(); string shrunk = "";
            KbCell[] kinds = { KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Open, KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water };
            for (int t = 0; t < 40000; t++)
            {
                var g = new G(15, 15);
                for (int x = 0; x < 15; x++) for (int z = 0; z < 15; z++) { var k = kinds[rng.Next(kinds.Length)]; if (k != KbCell.Open) g.Set(x, z, k); }
                int sx = rng.Next(15), sz = rng.Next(15); double ang = rng.NextDouble() * Math.PI * 2;
                float dx = (float)Math.Cos(ang), dz = (float)Math.Sin(ang); int cells = rng.Next(11);
                var kind = (KbKind)rng.Next(3); float mass = 1f + (float)rng.NextDouble() * 140f;
                var s = new KbSettings { sandbagsStop = rng.Next(4) == 0, intoPits = rng.Next(4) != 0, impactEnabled = rng.Next(5) != 0, impactFactor = rng.Next(5) == 0 ? 0f : 1f };
                string why = PathViolation(g, sx, sz, dx, dz, cells, kind, mass, s);
                c.T(why == null, "t" + t + " " + why);
                if (why != null && shrunk == "") shrunk = Shrink(g, sx, sz, dx, dz, cells, kind, mass, s);
            }
            Row("K_PATH_RANDOM_PROPERTIES", new[] { "inv_kernel", "no_teleport", "wall_stops_dead", "thrown_into_pit_falls", "doors_and_deep_water_stop", "pawn_hits_pawn_stops" }, "random", c.Ok, c.cases,
                c.D("seed " + seed + ", 40000 random 15x15 grids: travelled <= planned, the landing is the travelled count of grid steps away, every cell up to it passable, no wall corner cut, never rests on wall/door/water/edge/sandbag (pawn: on a pawn), never past an open pit, impact only for pawns and >= 0, 0 under factor 0, deterministic")
                + (shrunk == "" ? "" : " SHRUNK " + shrunk));
        }
        // ---------------- the line ----------------
        {
            int seed = 50507; var rng = new Random(seed); var c = new Check();
            for (int t = 0; t < 20000; t++)
            {
                double ang = rng.NextDouble() * Math.PI * 2; int cells = rng.Next(15);
                var p = RM_KnockbackMath.Line(0, 0, (float)Math.Cos(ang), (float)Math.Sin(ang), cells);
                c.T(p.Count == cells, "len " + p.Count + " vs " + cells);
                int px = 0, pz = 0; foreach (var q in p) { c.T(Math.Max(Math.Abs(q.x - px), Math.Abs(q.z - pz)) == 1, "step"); px = q.x; pz = q.z; }
                if (cells > 0) { double dot = p[p.Count - 1].x * Math.Cos(ang) + p[p.Count - 1].z * Math.Sin(ang); c.T(dot > 0, "goes away from the blast"); }
            }
            c.T(RM_KnockbackMath.Line(0, 0, 0f, 0f, 3).Count == 0, "no direction, no path");
            Row("K_LINE_GRID_STEPS", new[] { "inv_kernel", "no_teleport" }, "random", c.Ok, c.cases, c.D("seed " + seed + ": the path is exactly `cells` king-steps, contiguous, away along the ray"));
        }
        // ---------------- epicentre direction ----------------
        {
            var c = new Check();
            for (int e = 0; e < 50; e++) for (int th = 0; th < 50; th++)
                {
                    RM_KnockbackMath.EpicentreDir(e, th, out float dx, out float dz); RM_KnockbackMath.EpicentreDir(e, th, out float dx2, out float dz2);
                    c.T(Math.Abs(dx * dx + dz * dz - 1f) < 1e-4 && dx == dx2 && dz == dz2, "unit and deterministic");
                }
            Row("K_EPICENTRE_DIRECTION", new[] { "inv_kernel" }, "fixed", c.Ok, c.cases, c.D("a thing on the blast cell gets a deterministic unit direction"));
        }
        // ---------------- explosion ledger: one request per thing per explosion ----------------
        {
            int seed = 50508; var rng = new Random(seed); var c = new Check();
            for (int t = 0; t < 2000; t++)
            {
                var L = new KbExplosionLedger(600); int t0 = rng.Next(-5000, 1000000); int id = rng.Next(), thing = rng.Next();
                c.T(L.TryAdd(id, thing, t0), "first add");
                int later = t0 + rng.Next(600);
                c.T(!L.TryAdd(id, thing, later), "repeat inside the window at +" + (later - t0) + " from " + t0);
                int n = rng.Next(1, 30); for (int i = 0; i < n; i++) L.AddLaunched(id, t0);
                c.T(L.Launched(id, t0 + rng.Next(600)) == n, "launch count kept inside the window");
                c.T(L.TryAdd(id, thing + 1, later) && L.TryAdd(id + 1, thing, later), "other pairs are new");
            }
            Row("K_ONE_REQUEST_PER_THING_PER_BLAST", new[] { "inv_kernel", "every_good_moves" }, "random", c.Ok, c.cases,
                c.D("seed " + seed + ": a repeat callback for the same (explosion, thing) inside the 600-tick window enqueues nothing; launch counts survive the window"));
        }
        // ---------------- the frame probe and the barrage bar ----------------
        {
            var c = new Check();
            float[] Frames(int n, float ms) => Enumerable.Repeat(ms, n).ToArray();
            bool[] P(int n) => new bool[n]; int[] A(int n) => new int[n];
            int N = 600; var ms = Frames(N, 16f);  // 9.6 s of 16 ms frames
            var g = KbFrameStats.Summarize(ms, P(N), A(N), N, 9.6f, 0.9f, 8.25f);
            c.T(KbFrameStats.WithinBudget(g, 50f, out string why), "smooth passes: " + why);
            var one = (float[])ms.Clone(); one[300] = 151.3f;
            g = KbFrameStats.Summarize(one, P(N), A(N), N, 9.6f, 0.9f, 8.25f);
            c.T(KbFrameStats.WithinBudget(g, 50f, out why) && g.worstMs == 151.3f, "a single stall is reported (" + F(g.worstMs) + ") not judged: " + why);
            var stretch = (float[])ms.Clone(); for (int i = 200; i < 220; i++) stretch[i] = 60f;
            g = KbFrameStats.Summarize(stretch, P(N), A(N), N, 9.6f, 0.9f, 8.25f);
            c.T(!KbFrameStats.WithinBudget(g, 50f, out why), "a stretch of 20 slow frames fails: p99 " + F(g.windowP99Ms));
            var outside = (float[])ms.Clone(); for (int i = 0; i < 20; i++) outside[i] = 60f;  // the first 1.2 s: 20 x 60 = 1.2 s before the window opens at 0.9? no: check by time
            g = KbFrameStats.Summarize(outside, P(N), A(N), N, 9.6f, 0.9f, 8.25f);
            // frames 0..14 end at <= 0.9 s (15 x 60 = 0.9 s); frames 15..19 are inside the window: 5 slow of ~465 rows
            List<float> win = new List<float>(); double tt = 0; for (int i = 0; i < N; i++) { tt += outside[i]; if (tt >= 900 && tt <= 8250) win.Add(outside[i]); }
            var sorted = win.OrderBy(x => x).ToList(); float myP99 = sorted[Math.Max(0, (int)Math.Ceiling(0.99 * sorted.Count) - 1)];
            c.T(g.windowRows == win.Count && g.windowP99Ms == myP99, "window rows " + g.windowRows + "/" + win.Count + " p99 " + F(g.windowP99Ms) + "/" + F(myP99));
            var shortRun = Frames(300, 16f);  // 4.8 s: stops before the window closes
            g = KbFrameStats.Summarize(shortRun, P(300), A(300), 300, 4.8f, 0.9f, 8.25f);
            c.T(!KbFrameStats.WithinBudget(g, 50f, out why), "a probe that stopped early fails: " + why);
            var paused = P(N); for (int i = 0; i < 100; i++) paused[i] = true;
            g = KbFrameStats.Summarize(ms, paused, A(N), N, 9.6f, 0.9f, 8.25f);
            c.T(!KbFrameStats.WithinBudget(g, 50f, out why), "a paused run fails: " + why);
            var pausedSlow = (float[])ms.Clone(); var pz = P(N); for (int i = 300; i < 330; i++) { pausedSlow[i] = 200f; pz[i] = true; }
            g = KbFrameStats.Summarize(pausedSlow, pz, A(N), N, 9.6f + 30 * 0.184f, 0.9f, 8.25f);
            c.T(g.windowP99Ms == 16f, "paused rows never judged: p99 " + F(g.windowP99Ms));
            // exactly at budget passes, just over fails
            var at = Frames(N, 50f); g = KbFrameStats.Summarize(at, P(N), A(N), N, 30f, 0.9f, 8.25f);
            c.T(KbFrameStats.WithinBudget(g, 50f, out why), "50 ms passes (at most 50): " + why);
            var over = Frames(N, 50.01f); g = KbFrameStats.Summarize(over, P(N), A(N), N, 30f, 0.9f, 8.25f);
            c.T(!KbFrameStats.WithinBudget(g, 50f, out why), "50.01 ms fails");
            // percentile sanity, random
            int seed = 50509; var rng = new Random(seed);
            for (int t = 0; t < 2000; t++)
            {
                int n = 1 + rng.Next(800); var v = new List<float>(); for (int i = 0; i < n; i++) v.Add((float)rng.NextDouble() * 100f);
                float p = KbFrameStats.Percentile(v, 99f); var s2 = v.OrderBy(x => x).ToList();
                int atOrBelow = s2.Count(x => x <= p);
                c.T(atOrBelow >= 0.99 * n && s2.Count(x => x < p) < 0.99 * n, "nearest rank n=" + n);
            }
            // probe self-check: the slept frame shows
            var slept = (float[])ms.Clone(); slept[100] = 100f; double sum = slept.Sum() / 1000.0;
            g = KbFrameStats.Summarize(slept, P(N), A(N), N, (float)sum);
            c.T(KbFrameStats.SelfCheck(g, 100f, out why), "self-check passes with the 100 ms sleep: " + why);
            g = KbFrameStats.Summarize(ms, P(N), A(N), N, 9.6f);
            c.T(!KbFrameStats.SelfCheck(g, 100f, out why), "self-check fails when the slept frame is missing");
            g = KbFrameStats.Summarize(slept, P(N), A(N), 2 * N, (float)sum);
            c.T(!KbFrameStats.SelfCheck(g, 100f, out why), "self-check fails when rows miss frames");
            Row("K_BARRAGE_P99_AND_PROBE", new[] { "barrage_frame_budget", "frame_time_probe", "inv_perf_all_fly" }, "fixed", c.Ok, c.cases,
                c.D("p99 (nearest rank, unpaused) inside 0.9-8.25 s probe time at most 50 ms; one stall reported not judged; a slow stretch, an early stop or a paused run fails; seed " + seed + " for the percentile; the probe's own check sees a 100 ms sleep"));
        }
        // ---------------- shipped settings swept through their ranges ----------------
        {
            int seed = 50510; var rng = new Random(seed); var c = new Check(); string shrunk = "";
            for (int t = 0; t < 30000; t++)
            {
                var s = new KbSettings
                {
                    globalMultiplier = (float)rng.NextDouble() * 3f, maxCells = 1 + rng.Next(10), creatureMassLimit = 20f + rng.Next(481), lightMassLimit = 5f + (float)rng.NextDouble() * 195f,
                    impactPerCell = (float)rng.NextDouble() * 15f, impactEnabled = rng.Next(2) == 0, sandbagsStop = rng.Next(2) == 0, intoPits = rng.Next(2) == 0,
                };
                float ownScale = 0.25f + (float)rng.NextDouble() * 1.75f; int ownCap = rng.Next(8);
                var a = KbLookup.Apply(s, new KbConfig { ownCap = ownCap, impactFactor = (float)rng.NextDouble() * 2f }, s.maxCells, ownScale);
                float d = (float)rng.NextDouble() * 6f, r = 0.9f + (float)rng.NextDouble() * 8f, f = (float)rng.NextDouble() * 2f, m = 0.5f + (float)rng.NextDouble() * 200f;
                int cells = RM_KnockbackMath.ThrowCells(d, r, f, m, a);
                int want = RM_KnockbackMath.CapFor(ownCap, s.maxCells, ownScale);
                bool ok = cells >= 0 && cells <= want && a.maxCells == want;
                if (s.globalMultiplier == 0f || f == 0f) ok &= cells == 0;
                var res = RM_KnockbackMath.Resolve(new G(30, 30).Set(15 + Math.Min(cells, 3), 15, KbCell.Wall), 15, 15, 1f, 0f, cells, KbKind.Pawn, m, a);
                ok &= res.impact >= 0f && (a.impactEnabled || res.impact == 0f) && (a.impactPerCell > 0f || res.impact == 0f);
                int sg = 1 + rng.Next(6); var gas = KbLookup.Apply(s, new KbConfig { ownCap = sg, scaleOwnCap = false }, s.maxCells, ownScale);
                ok &= gas.maxCells == sg;
                int win = rng.Next(601); ok &= KbImmunity.CanLaunch(1000 + win, 1000, 900, win) && (win == 0 || !KbImmunity.CanLaunch(999 + win, 1000, 900, win));
                float keep = (float)rng.Next(101); int left = rng.Next(12); int rb = RM_KnockbackMath.ReboundCells(left, keep);
                ok &= rb >= 0 && rb <= left && (keep >= 100f || left == 0 || rb < left);
                float cml = 20f + rng.Next(981); float cm = (float)rng.NextDouble() * 1100f;
                ok &= RM_KnockbackMath.ContainerThrowCells(true, cm, cml, 1f, MORTAR_R, 1f, s) == 0 || cm <= cml;
                float hmin = 1f + rng.Next(75), dmin = rng.Next(21), dmax = Math.Max(dmin, rng.Next(21)); int stag = rng.Next(181);
                bool hk = RM_KnockbackMath.HeavyKnock(true, KbKind.Item, true, hmin, hmin, dmin, dmax, (float)rng.NextDouble(), stag, out float hd, out int hs);
                ok &= hk && hd >= dmin && hd <= dmax && hs == stag;
                c.T(ok, "t" + t);
                if (!ok && shrunk == "") shrunk = "mult " + F(s.globalMultiplier) + " max " + s.maxCells + " own " + ownCap + "x" + F(ownScale) + " cells " + cells + " want<=" + want;
            }
            Row("K_SETTINGS_SWEEP_RANGES", new[] { "inv_kernel", "settings_scale_and_switch", "inv_settings" }, "sweep", c.Ok, c.cases,
                c.D("seed " + seed + ": every kernel-read setting swept through its shipped slider range (strength 0-3, max 1-10, cap scale 0.25-2, creature 20-500, goods 5-200, impact 0-15 and off, sandbags, pits, recovery 0-600, rebound 0-100, container 20-1000, heavy 1-75 kg / 0-20 dmg / 0-180 ticks, gas cap 1-6): caps hold, strength 0 throws nothing, impact off/0 hurts nobody, gas cap never rescaled")
                + (shrunk == "" ? "" : " SHRUNK " + shrunk));
        }
    }

    static string PathViolation(G g, int sx, int sz, float dx, float dz, int cells, KbKind kind, float mass, KbSettings s)
    {
        var r = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
        var r2 = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, mass, s);
        if (r.destX != r2.destX || r.destZ != r2.destZ || r.stop != r2.stop || r.impact != r2.impact) return "not deterministic";
        if (r.cellsTravelled > Math.Max(0, cells)) return "travelled " + r.cellsTravelled + " > planned " + cells;
        if (Math.Max(Math.Abs(r.destX - sx), Math.Abs(r.destZ - sz)) != r.cellsTravelled) return "landing " + r.destX + "," + r.destZ + " not " + r.cellsTravelled + " steps out";
        var path = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
        bool pawn = kind == KbKind.Pawn;
        int px = sx, pz = sz;
        for (int i = 0; i < r.cellsTravelled; i++)
        {
            var (x, z) = path[i]; var k = g.At(x, z);
            if (k == KbCell.Wall || k == KbCell.Door || k == KbCell.OutOfBounds || k == KbCell.Water) return "entered " + k + " at step " + (i + 1);
            if (pawn && k == KbCell.Pawn) return "a pawn passed through a pawn at step " + (i + 1);
            if (pawn && s.sandbagsStop && k == KbCell.Partial) return "passed sandbags with sandbagsStop on";
            if (k == KbCell.Pit && (i < r.cellsTravelled - 1)) return "crossed an open pit at step " + (i + 1);
            if (k == KbCell.Pit && !s.intoPits) return "entered a pit with into-pits off";
            if (x != px && z != pz)
            {
                var a = g.At(x, pz); var b = g.At(px, z);
                if (a == KbCell.Wall || a == KbCell.Door || a == KbCell.OutOfBounds || b == KbCell.Wall || b == KbCell.Door || b == KbCell.OutOfBounds) return "cut a wall corner at step " + (i + 1);
            }
            px = x; pz = z;
        }
        if (r.cellsTravelled > 0)
        {
            var land = g.At(r.destX, r.destZ);
            if (land == KbCell.Partial) return "rests on sandbags";
            if (pawn && land == KbCell.Pawn) return "rests on a pawn";
        }
        if (r.stop == KbStop.Pit && g.At(r.destX, r.destZ) != KbCell.Pit) return "stop Pit not in a pit";
        if (r.impact < 0f || r.otherImpact < 0f) return "negative impact";
        if (!pawn && (r.impact != 0f || r.hitOther)) return "goods took pawn impact";
        if ((s.impactFactor == 0f || !s.impactEnabled) && (r.impact != 0f || r.otherImpact != 0f)) return "impact under factor 0 / off";
        if (r.hitOther && r.impact != r.otherImpact) return "pawn impact not split equally";
        return null;
    }

    static string Shrink(G g, int sx, int sz, float dx, float dz, int cells, KbKind kind, float mass, KbSettings s)
    {
        var cur = g.Clone(); int cc = cells;
        bool progress = true;
        while (progress)
        {
            progress = false;
            while (cc > 1 && PathViolation(cur, sx, sz, dx, dz, cc - 1, kind, mass, s) != null) { cc--; progress = true; }
            foreach (var key in cur.c.Keys.ToList())
            {
                var t = cur.Clone(); t.c.Remove(key);
                if (PathViolation(t, sx, sz, dx, dz, cc, kind, mass, s) != null) { cur = t; progress = true; }
            }
        }
        return "start " + sx + "," + sz + " dir " + F(dx) + "," + F(dz) + " cells " + cc + " kind " + kind + " grid {" + cur.Dump() + "} -> " + PathViolation(cur, sx, sz, dx, dz, cc, kind, mass, s);
    }
}
