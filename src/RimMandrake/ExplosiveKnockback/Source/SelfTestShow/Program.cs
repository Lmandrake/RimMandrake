using System;
using System.Collections.Generic;
using RimMandrake.ExplosiveKnockback;

// Offline selftest of the blast show's kernel (RM_KnockbackShowPlan.cs, as shipped). It generates the situations a blast
// can be in and reads every plan with the bars' own checks. Run through
// src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blast_show.py (it stages and builds this project).
//
// THE RANGE (declared): kind {Bomb, Flame, OtherHarmful, NoShow} x ground {Soil, Stone, Floor, Water} x radius {0, 0.5,
// 0.9, 1.1, 1.9, 2.9, 3.5, 5, 7.2, 8.9, 14.9, 25} (vanilla's grenade, shell and antigrain radii, and both ends) x damage
// ratio {-1, 0, 0.25, 0.5, 1, 2, 4, 11} (11 = antigrain's 550 over Bomb's 50) x camera distance {0, 5, 15, 30, 45, 60,
// 100, 200} x shake slider {0, 0.5, 1, 2} x screenShakeFactor {0, 1, 2} x {in view, off view, other map} x switch sets
// {all on, all off, each part alone off, each part alone on} x power-from-damage {on, off}.
// LEFT OUT, and why: the frames the game draws (the live scene sc_blast_show reads those and the art judge judges them);
// the game's shake cap (0.2 x the player's preference, applied by CameraShaker after us: a cap the player sets); the
// random spread of lobes, sparks and bits (Verse.Rand in RM_KnockbackShow.cs, not decision logic); the reference percent
// is fixed at 100 because it only rescales the damage ratio, which the range already sweeps.
internal static class Program
{
    private static int fails;
    private static readonly List<string> lines = new List<string>();

    private static void Check(string id, bool ok, string what, string worst, string limit, int cases)
    {
        string l = string.Format("{0} {1}: {2} | worst {3} | limit {4} | cases {5}", ok ? "PASS" : "FAIL", id, what, worst, limit, cases);
        lines.Add(l);
        Console.WriteLine(l);
        if (!ok) fails++;
    }

    private static readonly float[] Radii = { 0f, 0.5f, 0.9f, 1.1f, 1.9f, 2.9f, 3.5f, 5f, 7.2f, 8.9f, 14.9f, 25f };
    private static readonly float[] Ratios = { -1f, 0f, 0.25f, 0.5f, 1f, 2f, 4f, 11f };
    private static readonly float[] Dists = { 0f, 5f, 15f, 30f, 45f, 60f, 100f, 200f };
    private static readonly float[] Strengths = { 0f, 0.5f, 1f, 2f };
    private static readonly float[] Factors = { 0f, 1f, 2f };
    private static readonly KbShowKind[] Kinds = { KbShowKind.Bomb, KbShowKind.Flame, KbShowKind.OtherHarmful, KbShowKind.NoShow };
    private static readonly KbShowGround[] Grounds = { KbShowGround.Soil, KbShowGround.Stone, KbShowGround.Floor, KbShowGround.Water };
    private static readonly string[] Parts = { "fireAndFlash", "screenShake", "airRipple", "craterScars", "smoke", "sootOnThings", "sootOnPawns" };

    private static KbShowSwitches With(KbShowSwitches s, string part, bool on)
    {
        switch (part)
        {
            case "fireAndFlash": s.fireAndFlash = on; break;
            case "screenShake": s.screenShake = on; break;
            case "airRipple": s.airRipple = on; break;
            case "craterScars": s.craterScars = on; break;
            case "smoke": s.smoke = on; break;
            case "sootOnThings": s.sootOnThings = on; break;
            case "sootOnPawns": s.sootOnPawns = on; break;
        }
        return s;
    }

    private static KbShowBlast Blast(KbShowKind k, KbShowGround g, float radius, float ratio, float dist, float factor, int view)
    {
        return new KbShowBlast
        {
            kind = k, ground = g, radius = radius, damage = 50f * ratio, refDamage = 50f, screenShakeFactor = factor,
            cameraDistance = dist, onCurrentMap = view != 2, inView = view == 0,
        };
    }

    // what each part draws, as one comparable record: zero means the part shows nothing
    private static float[] FirePart(KbShowPlan p) => new[] { p.flashScale, p.fireballLobes, p.fireballScale, p.sparks, p.debris };
    private static float[] ShakePart(KbShowPlan p) => new[] { p.shakeMag, p.shakeHoldTicks };
    private static float[] RipplePart(KbShowPlan p) => new[] { p.rippleDiameter, p.rippleSeconds, p.rippleAlpha };
    private static float[] ScarPart(KbShowPlan p) => new[] { (float)p.scarKind, p.scarSize };
    private static float[] SmokePart(KbShowPlan p) => new[] { p.smokePuffs, p.smokeSeconds };

    private static bool AllZero(float[] a) { foreach (float x in a) if (x != 0f) return false; return true; }
    private static bool Same(float[] a, float[] b) { for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) return false; return true; }

    // ---- --sweep-dump OUT SCENARIO... (T_SETTINGS_SWEEP_OFFLINE's show half, T_SETTINGS_SWEEP_SHOW in
    // selftest_explosiveknockback_settings_sweep.py): no judgement here. Each SCENARIO is "name:field=value,..." over
    // KbShowSwitches' fields (the Python side builds them from RM_KnockbackShow.Switches() and the mod's settings); this
    // writes every public field of the shipped Plan() for every blast of the sweep's range, once per scenario, and the
    // Python side decides. THE SWEEP'S RANGE (declared): kind x ground (all four each) x Radii x Ratios (above) x camera
    // distance {0, 15, 45} x screenShakeFactor {0, 1} x {in view, off view, other map}. Left out: power from damage off
    // and the reference percent (they only rescale the damage ratio, which Ratios sweeps: S_ONE_MEASURE), a shake factor
    // of 2 (a straight multiplier, S_SHAKE), and the frames the game draws (the live scene sc_settings_sweep_show_switches).
    private static int SweepDump(string[] args)
    {
        var fields = typeof(KbShowPlan).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
        var sfields = typeof(KbShowSwitches).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
        using var w = new System.IO.StreamWriter(args[1]);
        w.WriteLine("FIELDS " + string.Join(",", Array.ConvertAll(fields, f => f.Name)));
        w.WriteLine("SWITCHFIELDS " + string.Join(",", Array.ConvertAll(sfields, f => f.Name)));
        int rows = 0;
        for (int a = 2; a < args.Length; a++)
        {
            string[] head = args[a].Split(new[] { ':' }, 2);
            object box = new KbShowSwitches();
            int set = 0;
            foreach (string kv in head[1].Split(','))
            {
                string[] p = kv.Split('=');
                var f = typeof(KbShowSwitches).GetField(p[0]);
                if (f == null) { w.WriteLine("BADFIELD " + head[0] + " " + p[0]); continue; }
                f.SetValue(box, f.FieldType == typeof(bool) ? (object)(p[1] == "1" || p[1] == "True" || p[1] == "true")
                                                            : float.Parse(p[1], System.Globalization.CultureInfo.InvariantCulture));
                set++;
            }
            var s = (KbShowSwitches)box;
            w.WriteLine("SCENARIO " + head[0] + " set=" + set);
            foreach (var k in Kinds) foreach (var g in Grounds) foreach (float r in Radii) foreach (float q in Ratios)
            foreach (float d in new[] { 0f, 15f, 45f }) foreach (float sf in new[] { 0f, 1f }) foreach (int view in new[] { 0, 1, 2 })
            {
                var pl = RM_KnockbackShowPlan.Plan(Blast(k, g, r, q, d, sf, view), s);
                object pb = pl;
                var vals = new string[fields.Length];
                for (int i = 0; i < fields.Length; i++)
                {
                    object v = fields[i].GetValue(pb);
                    vals[i] = v is bool bv ? (bv ? "1" : "0") : v is float fv ? fv.ToString("R", System.Globalization.CultureInfo.InvariantCulture)
                        : v is Enum ? Convert.ToInt32(v).ToString() : Convert.ToString(v, System.Globalization.CultureInfo.InvariantCulture);
                }
                w.WriteLine(head[0] + "\t" + k + "/" + g + "/r" + r.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/x"
                            + q.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/d" + d + "/f" + sf + "/v" + view + "\t" + string.Join("\t", vals));
                rows++;
            }
        }
        w.WriteLine("END rows=" + rows);
        Console.WriteLine("SWEEP DUMP " + rows + " rows");
        return 0;
    }

    private static int Main(string[] args)
    {
        if (args.Length >= 2 && args[0] == "--sweep-dump")
        {
            return SweepDump(args);
        }
        var all = KbShowSwitches.AllOn();
        int n;

        // ---- S_SCALE (bar blast_show_scales_with_damage): a blast with at least twice the power is plainly the bigger
        // show in every part with a size: each width, the fireball, the flash, the ripple, the scar, the smoke's time, the
        // soot's reach and the shake (below the floor and beyond the reach a blast adds no shake by its own bar) ----
        n = 0;
        double worstRatio = double.MaxValue; string worstAt = "-";
        int countDrops = 0; string countAt = "-";
        foreach (var k in new[] { KbShowKind.Bomb, KbShowKind.Flame, KbShowKind.OtherHarmful })
        foreach (var g in Grounds)
        foreach (float d in new[] { 0f, 5f, 15f })
        {
            var pts = new List<(float power, KbShowPlan plan, string at)>();
            foreach (float r in Radii) foreach (float q in Ratios)
            {
                var pl = RM_KnockbackShowPlan.Plan(Blast(k, g, r, q, d, 1f, 0), all);
                if (pl.show) pts.Add((pl.power, pl, string.Format("{0}/{1} r{2} x{3} d{4}", k, g, r, q, d)));
            }
            foreach (var a in pts) foreach (var b in pts)
            {
                if (!(b.power >= 2f * a.power)) continue;
                n++;
                var sizes = new List<(string name, float lo, float hi)>
                {
                    ("ripple width", a.plan.rippleDiameter, b.plan.rippleDiameter),
                    ("smoke time", a.plan.smokeSeconds, b.plan.smokeSeconds),
                    ("soot reach on things", a.plan.sootThingsReach, b.plan.sootThingsReach),
                    ("soot reach on pawns", a.plan.sootPawnsReach, b.plan.sootPawnsReach),
                };
                if (k != KbShowKind.OtherHarmful)
                {
                    sizes.Add(("flash", a.plan.flashScale, b.plan.flashScale));
                    sizes.Add(("fireball", a.plan.fireballScale, b.plan.fireballScale));
                }
                if (g != KbShowGround.Water) sizes.Add(("scar", a.plan.scarSize, b.plan.scarSize));
                if (a.plan.shakeMag > 0f) sizes.Add(("shake", a.plan.shakeMag, b.plan.shakeMag));
                foreach (var s in sizes)
                {
                    double ratio = s.lo > 0f ? s.hi / s.lo : (s.hi > 0f ? double.PositiveInfinity : 0.0);
                    if (ratio < worstRatio) { worstRatio = ratio; worstAt = s.name + " " + a.at + " vs " + b.at; }
                }
                // counts never fall for a bigger blast (they cap per blast: §3.3 "capped per blast")
                var ca = new[] { a.plan.fireballLobes, a.plan.sparks, a.plan.debris, a.plan.smokePuffs, a.plan.scarSizeClass };
                var cb = new[] { b.plan.fireballLobes, b.plan.sparks, b.plan.debris, b.plan.smokePuffs, b.plan.scarSizeClass };
                for (int i = 0; i < ca.Length; i++) if (cb[i] < ca[i]) { countDrops++; countAt = a.at + " vs " + b.at; }
            }
        }
        // 1.2: at twice the power every width grows by sqrt(2) = 1.41 (the square-root law), so 1.2 leaves room for the
        // shake's distance falloff, which also grows with power; a part that grew less than a fifth is not "plainly bigger"
        Check("S_SCALE", worstRatio >= 1.2, "every sized part at least 1.2x for twice the power", worstRatio.ToString("0.000") + " at " + worstAt, ">= 1.2", n);
        Check("S_SCALE_COUNTS", countDrops == 0, "no count (lobes, sparks, bits, puffs, scar class) falls for a bigger blast", countDrops + (countDrops > 0 ? " at " + countAt : ""), "0", n);

        // the scar as DRAWN (six widths): twice the power never draws a smaller scar; four times the power draws a larger
        // one, between the smallest and the largest width (a scar smaller than 3 cells draws at 3, one larger than 20 at 20:
        // the two ends of the drawn range, declared here)
        n = 0; int scarBad = 0; string scarAt = "-";
        int last = RM_KnockbackShowPlan.ScarDrawSizes.Length - 1;
        foreach (float r in Radii) foreach (float q in Ratios)
        {
            float pw = RM_KnockbackShowPlan.Power(50f * q, 50f, r, true, 100f);
            if (!(pw > 0f)) continue;
            foreach (float mult in new[] { 2f, 4f, 8f })
            {
                n++;
                float sizeA = RM_KnockbackShowPlan.ScarPerRadius * RM_KnockbackShowPlan.EffectiveRadius(pw);
                int a = RM_KnockbackShowPlan.ScarClass(sizeA);
                int b = RM_KnockbackShowPlan.ScarClass(RM_KnockbackShowPlan.ScarPerRadius * RM_KnockbackShowPlan.EffectiveRadius(pw * mult));
                if (b < a || (mult >= 4f && a < last && sizeA >= RM_KnockbackShowPlan.ScarDrawSizes[0] && b <= a)) { scarBad++; scarAt = "power " + pw + " x" + mult + ": class " + a + " -> " + b; }
            }
        }
        Check("S_SCAR_DRAWN", scarBad == 0, "the drawn scar: never smaller at twice the power, larger at four times (inside the drawn range of 3 to 20 cells)", scarBad + " " + scarAt, "0", n);

        // the big-versus-small pair of the bar itself: a frag grenade beside an antigrain shell (radius 14.9, 550/50)
        var gren = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Bomb, KbShowGround.Soil, 1.9f, 1f, 10f, 1f, 0), all);
        var anti = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Bomb, KbShowGround.Soil, 14.9f, 11f, 10f, 1f, 0), all);
        bool pairOk = anti.flashScale > gren.flashScale && anti.fireballScale > gren.fireballScale && anti.fireballLobes > gren.fireballLobes
            && anti.shakeMag > gren.shakeMag && anti.shakeHoldTicks > gren.shakeHoldTicks && anti.rippleDiameter > gren.rippleDiameter && anti.rippleAlpha > gren.rippleAlpha
            && anti.scarSize > gren.scarSize && anti.scarSizeClass > gren.scarSizeClass && anti.smokeSeconds > gren.smokeSeconds
            && anti.sootThingsReach > gren.sootThingsReach && anti.sootPawnsReach > gren.sootPawnsReach;
        Check("S_PAIR", pairOk, "grenade vs antigrain: the antigrain is bigger in every part",
            string.Format("flash {0:0.0}/{1:0.0} lobes {2}/{3} shake {4:0.000}/{5:0.000} ring {6:0.0}/{7:0.0} scar {8:0.0}/{9:0.0} class {10}/{11}",
                gren.flashScale, anti.flashScale, gren.fireballLobes, anti.fireballLobes, gren.shakeMag, anti.shakeMag,
                gren.rippleDiameter, anti.rippleDiameter, gren.scarSize, anti.scarSize, gren.scarSizeClass, anti.scarSizeClass), "all bigger", 2);

        // ---- S_SHAKE (bar blast_show_screen_shake) ----
        n = 0; int bad = 0; string badAt = "-"; float farWorst = 0f;
        foreach (float r in Radii) foreach (float q in Ratios) foreach (float st in Strengths) foreach (float f in Factors)
        {
            float prev = float.MaxValue;
            float power = RM_KnockbackShowPlan.Power(50f * q, 50f, r, true, 100f);
            float reach = RM_KnockbackShowPlan.ShakeReachAtPowerOne * (float)Math.Sqrt(Math.Max(0f, power));
            foreach (float d in Dists)
            {
                n++;
                float m = RM_KnockbackShowPlan.ShakeMag(power, d, st, f);
                if (m < 0f || float.IsNaN(m)) { bad++; badAt = "negative/NaN " + r + "/" + q + "/" + d; }
                if (m > prev + 1e-7f) { bad++; badAt = "grows with distance r" + r + " x" + q + " d" + d; }
                if ((st == 0f || f == 0f || !(power > 0f)) && m != 0f) { bad++; badAt = "shakes at slider none / factor 0 / no power"; }
                if (d >= reach && m != 0f) { bad++; badAt = "shakes beyond its reach r" + r + " x" + q + " d" + d; }
                if (power <= 1f && d >= RM_KnockbackShowPlan.ShakeReachAtPowerOne) farWorst = Math.Max(farWorst, m);
                prev = m;
                float m2 = RM_KnockbackShowPlan.ShakeMag(power, d, 2f * st, f);
                if (m > 0f && Math.Abs(m2 - 2f * m) > 1e-5f) { bad++; badAt = "the slider is not a straight multiplier at r" + r + " d" + d; }
            }
        }
        // the hold: a bigger blast holds its shake at least as long; no hold without a kick
        foreach (float d in Dists) foreach (float r in Radii)
        {
            float pa = RM_KnockbackShowPlan.Power(50f, 50f, r, true, 100f), pb = 4f * pa;
            float ma = RM_KnockbackShowPlan.ShakeMag(pa, d, 1f, 1f), mb = RM_KnockbackShowPlan.ShakeMag(pb, d, 1f, 1f);
            int ha = RM_KnockbackShowPlan.ShakeHoldTicks(pa, ma), hb = RM_KnockbackShowPlan.ShakeHoldTicks(pb, mb);
            n++;
            if ((ma == 0f && ha != 0) || hb < ha || ha < 0 || hb > 120) { bad++; badAt = "hold r" + r + " d" + d + ": " + ha + " -> " + hb; }
            if (ma > 0f && pa >= 1f && !(hb > ha)) { bad++; badAt = "four times the power holds no longer r" + r + " d" + d; }
        }
        Check("S_SHAKE", bad == 0, "shake >= 0, falls with distance, none beyond reach, none at slider none, slider multiplies", bad + " " + badAt, "0", n);
        Check("S_SHAKE_FAR_SMALL", farWorst == 0f, "a blast of power <= 1 at 30 cells or more adds no shake", farWorst.ToString("0.0000"), "0", n);
        // harder for a bigger and a nearer blast, read on two vanilla blasts at 10 cells and one at 0 vs 20
        float sG = RM_KnockbackShowPlan.ShakeMag(1f, 10f, 1f, 1f), sM = RM_KnockbackShowPlan.ShakeMag(RM_KnockbackShowPlan.Power(50f, 50f, 2.9f, true, 100f), 10f, 1f, 1f);
        float sNear = RM_KnockbackShowPlan.ShakeMag(1f, 0f, 1f, 1f), sFar = RM_KnockbackShowPlan.ShakeMag(1f, 20f, 1f, 1f);
        Check("S_SHAKE_ORDER", sM > sG && sNear > sFar && sFar > 0f, "mortar shakes harder than grenade at 10 cells; a grenade at 0 harder than at 20",
            string.Format("grenade {0:0.0000} mortar {1:0.0000} near {2:0.0000} far {3:0.0000}", sG, sM, sNear, sFar), "mortar > grenade, near > far > 0", 4);

        // the trauma rule: one blast alone adds its whole kick; added to a shake it adds less than its kick and the total
        // is at least the larger of the two; ten equal kicks sum to sqrt(10) kicks, not ten
        n = 0; bad = 0; badAt = "-";
        foreach (float cur in new[] { 0f, 0.01f, 0.05f, 0.1f, 0.2f, 1f }) foreach (float kick in new[] { -1f, 0f, 0.005f, 0.05f, 0.1f, 0.5f })
        {
            n++;
            float add = RM_KnockbackShowPlan.ShakeToAdd(cur, kick);
            float tot = cur + add;
            if (add < 0f || (kick > 0f && (tot + 1e-6f < Math.Max(cur, kick) || add > kick + 1e-6f)) || (kick <= 0f && add != 0f)) { bad++; badAt = cur + "+" + kick + " adds " + add; }
            if (cur == 0f && kick > 0f && Math.Abs(add - kick) > 1e-6f) { bad++; badAt = "a lone blast does not get its whole kick"; }
        }
        float acc = 0f; for (int i = 0; i < 10; i++) acc += RM_KnockbackShowPlan.ShakeToAdd(acc, 0.05f);
        n++;
        if (Math.Abs(acc - 0.05f * (float)Math.Sqrt(10)) > 1e-4f) { bad++; badAt = "ten kicks of 0.05 total " + acc; }
        Check("S_SHAKE_TRAUMA", bad == 0, "shakes add by the root of their squares: a lone kick whole, a barrage not summed", bad + " " + badAt + "; ten kicks of 0.05 -> " + acc.ToString("0.0000"), "0; 0.1581", n);

        // ---- S_SWITCH (bar blast_show_switches_off_clean, the kernel's share): a part off shows nothing of that part and
        // changes no other part; every part off touches nothing of the vanilla blast ----
        n = 0; bad = 0; badAt = "-";
        foreach (var k in Kinds) foreach (var g in Grounds) foreach (float r in new[] { 1.9f, 2.9f, 14.9f }) foreach (float q in new[] { 0.5f, 1f, 11f })
        foreach (int view in new[] { 0, 1, 2 })
        {
            var b = Blast(k, g, r, q, 10f, 1f, view);
            var on = RM_KnockbackShowPlan.Plan(b, all);
            var off = RM_KnockbackShowPlan.Plan(b, KbShowSwitches.AllOff());
            n++;
            if (off.suppressVanillaVisuals || off.zeroVanillaShake || off.suppressVanillaBlastMark || off.replayVanillaShake || off.replayWaterSplash
                || !AllZero(FirePart(off)) || !AllZero(ShakePart(off)) || !AllZero(RipplePart(off)) || !AllZero(ScarPart(off)) || !AllZero(SmokePart(off)) || off.sootThingsReach != 0f || off.sootPawnsReach != 0f)
            { bad++; badAt = "all off still changes the blast at " + k + "/" + g + "/" + r; }
            foreach (string part in Parts)
            {
                var p = RM_KnockbackShowPlan.Plan(b, With(all, part, false));
                n++;
                bool fireSame = Same(FirePart(p), FirePart(on)), shakeSame = Same(ShakePart(p), ShakePart(on)),
                     ripSame = Same(RipplePart(p), RipplePart(on)), scarSame = Same(ScarPart(p), ScarPart(on)), smokeSame = Same(SmokePart(p), SmokePart(on)),
                     thingsSame = p.sootThingsReach == on.sootThingsReach, pawnsSame = p.sootPawnsReach == on.sootPawnsReach;
                bool ok = part switch
                {
                    "fireAndFlash" => AllZero(FirePart(p)) && !p.suppressVanillaVisuals && !p.replayWaterSplash && shakeSame && ripSame && scarSame && smokeSame && thingsSame && pawnsSame,
                    "screenShake" => AllZero(ShakePart(p)) && !p.zeroVanillaShake && fireSame && ripSame && scarSame && smokeSame
                                     && p.replayVanillaShake == on.suppressVanillaVisuals && thingsSame && pawnsSame,
                    "airRipple" => AllZero(RipplePart(p)) && fireSame && shakeSame && scarSame && smokeSame && thingsSame && pawnsSame,
                    "craterScars" => AllZero(ScarPart(p)) && !p.suppressVanillaBlastMark && fireSame && shakeSame && ripSame && smokeSame && thingsSame && pawnsSame,
                    "smoke" => AllZero(SmokePart(p)) && fireSame && shakeSame && ripSame && scarSame && thingsSame && pawnsSame,
                    "sootOnThings" => p.sootThingsReach == 0f && fireSame && shakeSame && ripSame && scarSame && smokeSame && pawnsSame,
                    "sootOnPawns" => p.sootPawnsReach == 0f && fireSame && shakeSame && ripSame && scarSame && smokeSame && thingsSame,
                    _ => false,
                };
                if (!ok) { bad++; badAt = part + " off at " + k + "/" + g + "/r" + r + "/x" + q + "/view" + view; }
            }
        }
        Check("S_SWITCH", bad == 0, "each part off shows none of that part and leaves the rest; all off leaves the vanilla blast whole", bad + " " + badAt, "0", n);

        // ---- S_KIND and S_GROUND (bars blast_show_fire_and_flash and blast_show_crater_scar) ----
        n = 0; bad = 0; badAt = "-";
        foreach (var g in Grounds) foreach (float r in Radii) foreach (float q in Ratios) foreach (int view in new[] { 0, 1, 2 })
        {
            n++;
            var none = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.NoShow, g, r, q, 0f, 1f, view), all);
            if (none.show || none.suppressVanillaVisuals || none.zeroVanillaShake || none.suppressVanillaBlastMark) { bad++; badAt = "a harmless type is touched"; }
            var fl = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Flame, g, r, q, 0f, 1f, view), all);
            if (fl.debris != 0 || (fl.scarKind != KbScarKind.None && fl.scarKind != KbScarKind.Scorch)) { bad++; badAt = "a flame blast throws dirt or digs a crater"; }
            var ot = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.OtherHarmful, g, r, q, 0f, 1f, view), all);
            if (ot.suppressVanillaVisuals || !AllZero(FirePart(ot))) { bad++; badAt = "another mod's harmful type loses its own flecks"; }
            var bo = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Bomb, g, r, q, 0f, 1f, view), all);
            if (bo.show)
            {
                if (g == KbShowGround.Water && (bo.scarKind != KbScarKind.None || bo.debris != 0)) { bad++; badAt = "a scar or dirt on water"; }
                if (g == KbShowGround.Soil && bo.scarKind != KbScarKind.Crater) { bad++; badAt = "no crater on soil"; }
                if ((g == KbShowGround.Stone || g == KbShowGround.Floor) && bo.scarKind != KbScarKind.Scorch) { bad++; badAt = "a pit dug in stone or a floor"; }
                if (view == 0 && g != KbShowGround.Water && (bo.debris == 0 || bo.debrisIsStone != (g != KbShowGround.Soil))) { bad++; badAt = "wrong or no bits at " + g; }
                if (view == 0 && (bo.flashScale <= 0f || bo.fireballLobes < 3 || bo.fireballLobes > 6 || bo.sparks <= 0)) { bad++; badAt = "no flash, fireball or sparks in view r" + r + " x" + q; }
                if (view != 0 && !AllZero(FirePart(bo))) { bad++; badAt = "fire drawn off view"; }
                if (view != 0 && g != KbShowGround.Water && bo.scarKind == KbScarKind.None) { bad++; badAt = "no scar off view (a scar endures)"; }
                if (!bo.suppressVanillaVisuals || !bo.replayWaterSplash) { bad++; badAt = "our fire does not replace vanilla's, or the splash is lost"; }
            }
            else if (!AllZero(FirePart(bo)) || bo.scarKind != KbScarKind.None) { bad++; badAt = "a powerless blast shows something"; }
        }
        Check("S_KIND_GROUND", bad == 0, "harmless types untouched; flame: no dirt, no crater; others keep their flecks; water: no scar; stone and floor: scorch; soil: crater; off view: no fire, still a scar", bad + " " + badAt, "0", n);

        // ---- S_ANCHOR: at its type's normal damage a blast's flash is vanilla's size (radius x 6), and a mortar's scar is
        // vanilla's 7-cell mark ----
        float worstFlash = 0f; n = 0;
        foreach (float r in Radii)
        {
            if (r <= 0f) continue;
            n++;
            var p = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Bomb, KbShowGround.Soil, r, 1f, 0f, 1f, 0), all);
            worstFlash = Math.Max(worstFlash, Math.Abs(p.flashScale - 6f * r));
        }
        var mortar = RM_KnockbackShowPlan.Plan(Blast(KbShowKind.Bomb, KbShowGround.Soil, 2.9f, 1f, 0f, 1f, 0), all);
        Check("S_ANCHOR", worstFlash < 1e-3f && Math.Abs(mortar.scarSize - 7f) < 1e-3f && RM_KnockbackShowPlan.ScarDrawSizes[mortar.scarSizeClass] == 7f,
            "flash = vanilla's radius x 6 at normal damage; a mortar's scar is 7 cells (vanilla's mark), drawn at 7",
            string.Format("flash off by {0:0.0000}; mortar scar {1:0.000} class {2}", worstFlash, mortar.scarSize, mortar.scarSizeClass), "0 and 7, drawn at 7", n + 1);

        // ---- S_THROW_APART: the throw's damage ratio switch reaches the show the same way (one measure) ----
        float pOn = RM_KnockbackShowPlan.Power(100f, 50f, 1.9f, true, 100f), pOff = RM_KnockbackShowPlan.Power(100f, 50f, 1.9f, false, 100f);
        float rOn = RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true);
        Check("S_ONE_MEASURE", Math.Abs(pOn - rOn) < 1e-5f && Math.Abs(pOff - 1f) < 1e-5f, "power is the throw's own damage ratio times area",
            string.Format("power(on) {0:0.000} ratio {1:0.000} power(off) {2:0.000}", pOn, rOn, pOff), "equal; 1", 2);

        Console.WriteLine(fails == 0 ? "ALL PASS show kernel (" + lines.Count + " checks)" : "FAIL show kernel: " + fails + " of " + lines.Count + " checks");
        return fails == 0 ? 0 : 1;
    }
}
