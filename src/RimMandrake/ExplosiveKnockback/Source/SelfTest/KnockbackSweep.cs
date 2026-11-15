using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.ExplosiveKnockback;

// T_SETTINGS_SWEEP_OFFLINE (RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING): sc_settings_sweep's lane as
// kernel inputs, run once at default and once per kernel-side setting. Each change may alter only its own outcomes and
// must alter them the way the scene expects. A mutant that couples two settings must go red. The game-side settings
// (kind filters, flight look, stun, doors, overlay, gas tuning) are named in selftest_explosiveknockback_settings_sweep.py
// with the scene that proves them. The mod's Kernel() mapping and defaults are checked there against RM_KnockbackMod.cs.
internal sealed class Sw
{
    public float strength = 1f;
    public int maxThrowCells = 6;
    public float ownCapScale = 1f;
    public float unpatchedHarmfulPercent = 100f;
    public float creatureMassLimit = 150f;
    public bool blastPowerFromDamage = true;
    public float blastPowerRefPercent = 100f;
    public float lightMassLimit = 75f;
    public float goodsReboundKeepPercent = 70f;
    public bool openStorageProtectsGoods = false;
    public bool shoveClosedContainers = true;
    public float closedContainerMassLimit = 250f;
    public bool heavyGoodsKnock = true;
    public float heavyGoodsMinMass = 10f;
    public float heavyGoodsDamageMin = 2f;
    public float heavyGoodsDamageMax = 5f;
    public int heavyGoodsStaggerTicks = 30;
    public bool sandbagsStopThrow = false;
    public bool impactDamageEnabled = true;
    public float impactDamagePerCell = 4f;
    public bool throwIntoPits = true;
    public int recoveryWindowTicks = 120;
    public float shieldDebitPerForce = 10f;

    public Sw With(string field, string value)
    {
        var c = (Sw)MemberwiseClone();
        var f = typeof(Sw).GetField(field) ?? throw new ArgumentException("no sweep field " + field);
        f.SetValue(c, Convert.ChangeType(value, f.FieldType, System.Globalization.CultureInfo.InvariantCulture));
        return c;
    }
}

internal static class KnockbackSweep
{
    private const float Radius = 1.9f, Dist = 1f, BombRef = 50f;

    /// <summary>As RimMandrakeExplosiveKnockbackSettings.Kernel(ownCap) builds it (the Python half checks that mapping).</summary>
    private static KbSettings Kernel(Sw w, int ownCap, int mutant)
    {
        float lightLimit = mutant == 1 ? Math.Min(w.lightMassLimit, w.creatureMassLimit / 2f) : w.lightMassLimit; // mutant 1: limits coupled
        int globalCap = mutant == 2 ? Math.Max(1, (int)(w.maxThrowCells * w.ownCapScale)) : w.maxThrowCells;      // mutant 2: own-cap scale leaks to the global cap
        return new KbSettings
        {
            globalMultiplier = w.strength,
            maxCells = RM_KnockbackMath.CapFor(ownCap, globalCap, w.ownCapScale),
            creatureMassLimit = w.creatureMassLimit,
            lightMassLimit = lightLimit,
            impactEnabled = w.impactDamageEnabled,
            impactPerCell = w.impactDamagePerCell,
            sandbagsStop = w.sandbagsStopThrow,
            intoPits = w.throwIntoPits,
        };
    }

    private static string Resolve(KbCell what, KbKind kind, float mass, Sw w, int mutant)
    {
        var g = new Grid(12, 3).Set(3, 1, what);
        KbSettings s = Kernel(w, 0, mutant);
        int cells = Math.Max(3, RM_KnockbackMath.ThrowCells(0f, 2.9f, 1f, mass, s));
        KbResult r = RM_KnockbackMath.Resolve(g, 1, 1, 1f, 0f, cells, kind, mass, s);
        return r.destX + "," + r.stop + "," + r.impact.ToString("0.###");
    }

    public static Dictionary<string, string> Outcomes(Sw w, int mutant = 0)
    {
        var o = new Dictionary<string, string>();
        KbSettings s = Kernel(w, 0, mutant);
        float x2 = RM_KnockbackMath.DamageRatio(100f, BombRef, w.blastPowerRefPercent, w.blastPowerFromDamage);
        float x1 = RM_KnockbackMath.DamageRatio(50f, BombRef, w.blastPowerRefPercent, w.blastPowerFromDamage);
        void Subject(string key, KbKind kind, float mass)
        {
            bool ok = RM_KnockbackMath.Eligible(kind, mass, s);
            o[key + ".eligible"] = ok.ToString();
            o[key + ".cells"] = ok ? RM_KnockbackMath.ThrowCells(Dist, Radius, x1, mass, s).ToString() : "-";
            o[key + ".cells_x2"] = ok ? RM_KnockbackMath.ThrowCells(Dist, Radius, x2, mass, s).ToString() : "-";
        }
        Subject("colonist", KbKind.Pawn, 70f);
        Subject("animal", KbKind.Pawn, 40f);
        Subject("animal2", KbKind.Pawn, 130f);
        Subject("mech", KbKind.Pawn, 80f);
        Subject("good50", KbKind.Item, 50f);
        Subject("good65", KbKind.Item, 65f);
        Subject("good100", KbKind.Item, 100f);
        Subject("corpse", KbKind.Corpse, 60f);
        o["ratio_x2"] = x2.ToString("0.###");
        // own cap: a grenade with maxThrowCells 4 of its own, at its centre; the plain grenade beside it
        o["owncap.cells"] = RM_KnockbackMath.ThrowCells(0f, 2.9f, 1f, 70f, Kernel(w, 4, mutant)).ToString();
        o["plain_centre.cells"] = RM_KnockbackMath.ThrowCells(0f, 2.9f, 1f, 70f, s).ToString();
        // an explosion of a damage type with no knockback extension anywhere
        KbConfig un = KbLookup.Resolve(null, null, null, true, w.unpatchedHarmfulPercent / 100f);
        o["unpatched.force"] = un.force.ToString("0.###");
        o["unpatched.cells"] = RM_KnockbackMath.ThrowCells(0f, 2.9f, un.force, 70f, s).ToString();
        // the weapons locker (1x1, 8 kg, free behind) and an over-limit locker
        o["locker.shove"] = !w.shoveClosedContainers ? "None"
            : RM_KnockbackMath.ContainerThrowCells(true, 8f, w.closedContainerMassLimit, 1f, 2.9f, 1f, s) > 0 ? "Thrown" : "Jolt";
        o["shelf.held"] = RM_KnockbackMath.GoodsHeld(true, false, w.openStorageProtectsGoods).ToString();
        // the heavy stack (15 kg) aimed at a pawn
        bool hit = RM_KnockbackMath.HeavyKnock(w.heavyGoodsKnock, KbKind.Item, true, 15f, w.heavyGoodsMinMass, w.heavyGoodsDamageMin,
            w.heavyGoodsDamageMax, 0.5f, w.heavyGoodsStaggerTicks, out float hd, out int hs);
        o["heavy.hit"] = hit.ToString();
        o["heavy.damage"] = hd.ToString("0.###");
        o["heavy.stun"] = hs.ToString();
        // a sandbag line, a wall and an open pit on three rays
        o["sandbag.result"] = Resolve(KbCell.Partial, KbKind.Pawn, 70f, w, mutant);
        o["wall.result"] = Resolve(KbCell.Wall, KbKind.Pawn, 70f, w, mutant);
        o["pit.result"] = Resolve(KbCell.Pit, KbKind.Item, 10f, w, mutant);
        // a second grenade 10 ticks after landing (stun already over); a charged belt; a good rebounding with 4 cells left
        o["second_grenade.launch"] = KbImmunity.CanLaunch(1010, 1000, 1000, w.recoveryWindowTicks).ToString();
        o["belt.drop"] = (1f - KbShield.EnergyAfter(1f, 1f, w.shieldDebitPerForce, 0.033f)).ToString("0.####");
        o["rebound.cells"] = RM_KnockbackMath.ReboundCells(4, w.goodsReboundKeepPercent).ToString();
        return o;
    }

    private static int I(string v) => v == "-" ? -1 : int.Parse(v);
    private static float F(string v) => float.Parse(v, System.Globalization.CultureInfo.InvariantCulture);
    private static string[] Rs(string v) => v.Split(',');

    // (setting, value, the outcome keys it owns (regex), the scene's expectation on its own outcomes)
    private static readonly (string f, string v, string own, Func<Dictionary<string, string>, Dictionary<string, string>, bool> expect, string says)[] Rows =
    {
        ("strength", "0.5", @"\.cells|cells_x2|\.result$", (d, n) => I(n["colonist.cells_x2"]) * 2 <= I(d["colonist.cells_x2"]) + 1 && I(n["colonist.cells"]) < I(d["colonist.cells"]), "cells halved"),
        ("maxThrowCells", "2", @"\.cells|cells_x2|\.result$", (d, n) => n.Where(kv => (kv.Key.EndsWith("cells") || kv.Key.EndsWith("cells_x2")) && kv.Key != "owncap.cells" && kv.Key != "rebound.cells").All(kv => I(kv.Value) <= 2)
            && n["owncap.cells"] == d["owncap.cells"], "at most 2 cells (a weapon's own cap is its own)"),
        ("ownCapScale", "0.5", @"^owncap\.", (d, n) => I(d["owncap.cells"]) == 4 && I(n["owncap.cells"]) == 2, "own-cap grenade 2 cells, plain unchanged"),
        ("unpatchedHarmfulPercent", "50", @"^unpatched\.", (d, n) => F(d["unpatched.force"]) == 1f && F(n["unpatched.force"]) == 0.5f, "unpatched at full by default, half at 50"),
        ("creatureMassLimit", "90", @"^animal2\.", (d, n) => d["animal2.eligible"] == "True" && n["animal2.eligible"] == "False", "the second animal thrown at default, spared at 90"),
        ("closedContainerMassLimit", "5", @"^locker\.", (d, n) => d["locker.shove"] == "Thrown" && n["locker.shove"] == "Jolt", "the locker is thrown at default, jolts at 5"),
        ("shoveClosedContainers", "False", @"^locker\.", (d, n) => n["locker.shove"] == "None", "with the shove off the locker stays put"),
        ("blastPowerFromDamage", "False", @"cells_x2|ratio_x2", (d, n) => F(d["ratio_x2"]) == 2f && F(n["ratio_x2"]) == 1f
            && new[] { "colonist", "animal", "animal2", "mech" }.All(k => I(d[k + ".cells_x2"]) > I(d[k + ".cells"]) || I(d[k + ".cells_x2"]) == 6)
            && new[] { "colonist", "animal", "animal2", "mech" }.All(k => n[k + ".cells_x2"] == n[k + ".cells"]), "farther under double damage at default, as far when off"),
        ("blastPowerRefPercent", "50", @"cells_x2|ratio_x2|\.cells$", (d, n) => Math.Abs(F(n["ratio_x2"]) - 2f * F(d["ratio_x2"])) < 1e-3f, "a reference percent of 50 doubles the damage ratio"),
        ("lightMassLimit", "60", @"^good65\.", (d, n) => d["good65.eligible"] == "True" && n["good65.eligible"] == "False" && d["good100.eligible"] == "False", "65 kg thrown at default, spared at 60; 100 kg spared at default"),
        ("lightMassLimit", "20", @"^good(50|65)\.|^corpse\.", (d, n) => n["colonist.eligible"] == "True" && n["good50.eligible"] == "False", "the mass lane: the colonist still thrown at 20 (goods limit weighs goods and corpses only)"),
        ("heavyGoodsMinMass", "20", @"^heavy\.", (d, n) => d["heavy.hit"] == "True" && n["heavy.hit"] == "False", "the stack no longer knocks"),
        ("heavyGoodsKnock", "False", @"^heavy\.", (d, n) => n["heavy.hit"] == "False" && F(n["heavy.damage"]) == 0f, "heavy knock off"),
        ("heavyGoodsDamageMax", "9", @"^heavy\.damage$", (d, n) => F(n["heavy.damage"]) > F(d["heavy.damage"]), "a bigger hit range"),
        ("heavyGoodsDamageMin", "3", @"^heavy\.damage$", (d, n) => F(n["heavy.damage"]) > F(d["heavy.damage"]), "a higher floor"),
        ("heavyGoodsStaggerTicks", "60", @"^heavy\.stun$", (d, n) => I(n["heavy.stun"]) == 60, "the stagger is the setting"),
        ("sandbagsStopThrow", "True", @"^sandbag\.", (d, n) => Rs(d["sandbag.result"])[1] != "PartialCover" && Rs(n["sandbag.result"])[1] == "PartialCover", "the sandbagged colonist stops at the sandbags"),
        ("impactDamageEnabled", "False", @"\.result$", (d, n) => F(Rs(d["wall.result"])[2]) > 0f && F(Rs(n["wall.result"])[2]) == 0f, "the wall impact is 0 with impact off"),
        ("impactDamagePerCell", "8", @"\.result$", (d, n) => Math.Abs(F(Rs(n["wall.result"])[2]) - 2f * F(Rs(d["wall.result"])[2])) < 0.01f, "the wall impact doubled at 8"),
        ("throwIntoPits", "False", @"^pit\.", (d, n) => Rs(d["pit.result"])[1] == "Pit" && Rs(n["pit.result"])[1] != "Pit", "the good on the pit ray lands on the rim"),
        ("recoveryWindowTicks", "0", @"^second_grenade\.", (d, n) => d["second_grenade.launch"] == "False" && n["second_grenade.launch"] == "True", "the just-landed colonist thrown at window 0, not at default"),
        ("shieldDebitPerForce", "20", @"^belt\.", (d, n) => Math.Abs(F(n["belt.drop"]) - 2f * F(d["belt.drop"])) < 1e-3f, "the belt's energy drop doubles at 20"),
        ("goodsReboundKeepPercent", "35", @"^rebound\.", (d, n) => I(n["rebound.cells"]) < I(d["rebound.cells"]), "a rebound keeps less"),
        ("openStorageProtectsGoods", "True", @"^shelf\.", (d, n) => d["shelf.held"] == "False" && n["shelf.held"] == "True", "the old rule back on: a shelf holds its goods"),
    };

    /// <summary>Faults of one full sweep (empty = pass).</summary>
    public static List<string> Sweep(int mutant)
    {
        var faults = new List<string>();
        var d = Outcomes(new Sw(), mutant);
        foreach (var row in Rows)
        {
            var n = Outcomes(new Sw().With(row.f, row.v), mutant);
            var changed = d.Keys.Where(k => d[k] != n[k]).ToList();
            var foreign = changed.Where(k => !Regex.IsMatch(k, row.own)).ToList();
            if (foreign.Count > 0)
            {
                faults.Add(row.f + "=" + row.v + " changed outcomes it does not own: " + string.Join(", ", foreign.Select(k => k + " " + d[k] + "->" + n[k])));
            }
            if (!row.expect(d, n))
            {
                faults.Add(row.f + "=" + row.v + " expected '" + row.says + "': " + string.Join(", ", changed.Select(k => k + " " + d[k] + "->" + n[k])));
            }
        }
        var again = Outcomes(new Sw(), mutant);
        if (d.Any(kv => again[kv.Key] != kv.Value))
        {
            faults.Add("the default run before and after the sweep differ");
        }
        return faults;
    }

    public static int Run()
    {
        var faults = Sweep(0);
        foreach (string f in faults)
        {
            Console.WriteLine("FAIL " + f);
        }
        int caught = 0;
        for (int m = 1; m <= 2; m++)
        {
            if (Sweep(m).Count > 0)
            {
                caught++;
            }
            else
            {
                Console.WriteLine("FAIL coupling mutant " + m + " NOT CAUGHT");
            }
        }
        Console.WriteLine("SWEPT " + string.Join(",", Rows.Select(r => r.f).Distinct()));
        Console.WriteLine("DEFAULTS " + string.Join(" ", typeof(Sw).GetFields().Select(f => f.Name + "=" + Convert.ToString(f.GetValue(new Sw()), System.Globalization.CultureInfo.InvariantCulture))));
        Console.WriteLine("explosive knockback settings sweep: " + (faults.Count == 0 && caught == 2 ? "PASS" : "FAIL") + " (" + Rows.Length
            + " runs, " + faults.Count + " faults, " + caught + "/2 coupling mutants caught)");
        return faults.Count == 0 && caught == 2 ? 0 : 1;
    }
}
