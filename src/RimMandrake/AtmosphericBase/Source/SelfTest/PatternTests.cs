// Selftest for the pattern grammar (design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §4-§6), kernel only.
// REAL, compiled from production source: RM_PatternKernel (primitives, evaluator, layer validation) through
// RM_SchemeKernel.PaletteIndex / Errors. The scheme XML is read with a reflection loader that fills RM_Layer's public
// fields by element name, the way RimWorld's DirectXmlToObject fills them in game.
// NOT covered: the game-side loop (rooms, doors, CompGlower) -- the compositor's and the live proof's business.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Xml;
using RimMandrake.AtmosphericBase;

internal static class PatternTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    // ---------------------------------------------------------------- a frozen copy of the pre-grammar PaletteIndex
    // (RM_SchemeKernel.cs before the layer port). Do not edit: it is the bit-identity oracle of build step 2.
    private static int LegacyPaletteIndex(RM_SchemeData s, int emitter, int group, double time, bool flasher)
    {
        int n = s.Count;
        if (n <= 1) return 0;
        if (flasher)
        {
            double fp = s.flasherPeriodSeconds;
            long fstep = (long)Math.Floor(time / fp + RM_SchemeKernel.Frac01(emitter, 3) * n);
            return (int)(fstep % n);
        }
        switch (s.pattern)
        {
            case RM_PatternKind.RoomBreath:
            {
                int len = 2 * n - 2;
                double u = time / s.massPeriodSeconds + RM_SchemeKernel.Frac01(group, 1);
                long step = (long)Math.Floor(u * len);
                return RM_SchemeKernel.PingPong(n, (int)(step % len));
            }
            case RM_PatternKind.Sparks:
            {
                double p = s.massPeriodSeconds;
                double shifted = time + RM_SchemeKernel.Frac01(emitter, 2) * p;
                long slot = (long)Math.Floor(shifted / p);
                if (RM_SchemeKernel.Mix(emitter, unchecked((int)slot)) % (uint)s.sparkOneIn != 0) return 0;
                double within = shifted - slot * p;
                if (within >= s.sparkSeconds) return 0;
                int len = 2 * n - 1;
                int k = Math.Min(len - 1, (int)Math.Floor(within / s.sparkSeconds * len));
                return k < n ? k : len - 1 - k;
            }
            default:
                return 0;
        }
    }

    // ---------------------------------------------------------------- reflection loader (RimWorld's shape)
    internal static RM_Layer LayerFrom(XmlNode li)
    {
        var l = new RM_Layer();
        foreach (XmlNode f in li.ChildNodes)
        {
            if (f.NodeType != XmlNodeType.Element) continue;
            FieldInfo fi = typeof(RM_Layer).GetField(f.Name, BindingFlags.Public | BindingFlags.Instance);
            if (fi == null) throw new FormatException("RM_Layer has no field <" + f.Name + ">");
            string v = f.InnerText.Trim();
            object o;
            if (fi.FieldType.IsEnum) o = Enum.Parse(fi.FieldType, v);
            else if (fi.FieldType == typeof(string)) o = v;
            else if (fi.FieldType == typeof(bool)) o = v.ToLowerInvariant() == "true";
            else o = Convert.ChangeType(v, fi.FieldType, CultureInfo.InvariantCulture);
            fi.SetValue(l, o);
        }
        return l;
    }

    internal static RM_SchemeData SchemeFrom(XmlNode n)
    {
        var rs = new List<int>(); var gs = new List<int>(); var bs = new List<int>();
        if (n["palette"] != null)
            foreach (XmlNode li in n["palette"].ChildNodes)
            {
                if (li.NodeType != XmlNodeType.Element) continue;
                string[] parts = li.InnerText.Trim().TrimStart('(').TrimEnd(')').Split(',');
                rs.Add(int.Parse(parts[0].Trim())); gs.Add(int.Parse(parts[1].Trim())); bs.Add(int.Parse(parts[2].Trim()));
            }
        Func<string, string, string> v = (k, def) => n[k]?.InnerText ?? def;
        var inv = CultureInfo.InvariantCulture;
        var s = new RM_SchemeData
        {
            r = rs.ToArray(), g = gs.ToArray(), b = bs.ToArray(),
            pattern = (RM_PatternKind)Enum.Parse(typeof(RM_PatternKind), v("pattern", "Steady")),
            massPeriodSeconds = float.Parse(v("massPeriodSeconds", "120"), inv),
            sparkSeconds = float.Parse(v("sparkSeconds", "2"), inv),
            sparkOneIn = int.Parse(v("sparkOneIn", "2")),
            mayGoDark = v("mayGoDark", "false") == "true",
            flasherCount = int.Parse(v("flasherCount", "0")),
            flasherPeriodSeconds = float.Parse(v("flasherPeriodSeconds", "0"), inv),
        };
        if (n["layers"] != null)
        {
            var ls = new List<RM_Layer>();
            foreach (XmlNode li in n["layers"].ChildNodes) if (li.NodeType == XmlNodeType.Element) ls.Add(LayerFrom(li));
            s.layers = ls.ToArray();
        }
        return s;
    }

    /// <summary>Every RM_AtmosphericSchemeDef in an XML text, by defName.</summary>
    internal static Dictionary<string, RM_SchemeData> Schemes(string xml)
    {
        var doc = new XmlDocument();
        doc.LoadXml(xml);
        var outp = new Dictionary<string, RM_SchemeData>();
        foreach (XmlNode n in doc.DocumentElement.ChildNodes)
            if (n.NodeType == XmlNodeType.Element && n.Name.EndsWith("RM_AtmosphericSchemeDef")) outp[n["defName"].InnerText] = SchemeFrom(n);
        return outp;
    }

    internal static RM_SchemeData One(string body, string palette = "<li>(182,118,62,0)</li><li>(220,158,96,0)</li><li>(255,210,148,0)</li>")
    {
        var d = Schemes("<Defs><RimMandrake.AtmosphericBase.RM_AtmosphericSchemeDef><defName>T</defName><palette>" + palette
                        + "</palette>" + body + "</RimMandrake.AtmosphericBase.RM_AtmosphericSchemeDef></Defs>");
        return d["T"];
    }

    internal static bool HasError(RM_SchemeData s, string needle) => RM_SchemeKernel.Errors(s).Exists(e => e.Contains(needle));
    internal static string Errs(RM_SchemeData s) => string.Join("; ", RM_SchemeKernel.Errors(s));

    // ---------------------------------------------------------------- NextChange against a brute evaluator (§5a)
    /// <summary>For `trials` random (fixture, t0): NextChange &gt; t0; the index holds on [t0, nc) at fine steps and just
    /// below nc; and, when exact, it has changed just above nc (or by the next brute step). Conservative primitives may
    /// return an nc where nothing changes; they must never return one LATER than the true change.</summary>
    internal static void NextChangeAgrees(string name, RM_SchemeData s, bool exact, int trials, double dt, double horizon,
                                          Func<int, RM_PatternCtx> ctxOf, int seed = 5)
    {
        var rng = new Random(seed);
        int late = 0, early = 0, notAfter = 0, checkedN = 0;
        string first = "";
        for (int i = 0; i < trials; i++)
        {
            RM_PatternCtx c = ctxOf(rng.Next(0, 100000));
            double t0 = rng.NextDouble() * 5000.0;
            int v0 = RM_PatternEvaluator.Index(s, ref c, t0, false);
            double nc = RM_PatternEvaluator.NextChange(s, ref c, t0, false);
            if (!(nc > t0)) { notAfter++; continue; }
            // brute: the first change after t0, in steps of dt
            double tc = double.PositiveInfinity;
            for (double t = t0 + dt; t <= t0 + horizon; t += dt)
                if (RM_PatternEvaluator.Index(s, ref c, t, false) != v0) { tc = t; break; }
            checkedN++;
            if (tc < nc - 1e-6 && RM_PatternEvaluator.Index(s, ref c, Math.Max(t0, nc - 1e-6), false) != v0)
            { late++; if (first == "") first = "t0=" + t0 + " nc=" + nc + " brute=" + tc; }
            else if (tc < nc - dt) { late++; if (first == "") first = "t0=" + t0 + " nc=" + nc + " brute=" + tc; }
            if (exact && !double.IsInfinity(nc) && nc < t0 + horizon)
            {
                bool changedAfter = RM_PatternEvaluator.Index(s, ref c, nc + 1e-6, false) != v0;
                if (!changedAfter) { early++; if (first == "") first = "early t0=" + t0 + " nc=" + nc; }
            }
        }
        Check(name + ": NextChange is after t, never later than the brute change" + (exact ? ", and exact at the boundary +-1e-6" : " (conservative)"),
              late == 0 && early == 0 && notAfter == 0 && checkedN > trials / 2,
              "late=" + late + " early=" + early + " notAfter=" + notAfter + " checked=" + checkedN + " " + first);
    }

    // ---------------------------------------------------------------- build step 2-3: interface, Breath, Spark, <layers>
    private static void Step2And3()
    {
        // (2) bit-identity with the frozen pre-grammar function: the same 60,000-sample harness shape as Phase 2
        var rng = new Random(20261024);
        int mismatch = 0; string firstMis = "";
        RM_PatternKind[] kinds = { RM_PatternKind.Steady, RM_PatternKind.RoomBreath, RM_PatternKind.Sparks };
        for (int i = 0; i < 60000; i++)
        {
            int n = 1 + rng.Next(4);
            var s = new RM_SchemeData { r = new int[n], g = new int[n], b = new int[n], pattern = kinds[i % 3],
                                        massPeriodSeconds = 10f + (float)rng.NextDouble() * 200f, sparkSeconds = 1f + (float)rng.NextDouble() * 4f,
                                        sparkOneIn = 1 + rng.Next(4), flasherPeriodSeconds = 0.5f + (float)rng.NextDouble() };
            int e = rng.Next(), gr = rng.Next(-1, 500);
            double t = rng.NextDouble() * 1e6;
            bool fl = i % 7 == 0;
            int a = LegacyPaletteIndex(s, e, gr, t, fl), b = RM_SchemeKernel.PaletteIndex(s, e, gr, t, fl);
            if (a != b) { mismatch++; if (firstMis == "") firstMis = s.pattern + " n=" + n + " t=" + t + " " + a + "!=" + b; }
        }
        Check("step 2: the layered evaluator is bit-identical to the pre-grammar PaletteIndex over 60,000 samples", mismatch == 0, mismatch + " " + firstMis);

        // an authored <layers> Breath equals the old <pattern>RoomBreath</pattern>
        RM_SchemeData old = One("<pattern>RoomBreath</pattern><massPeriodSeconds>120</massPeriodSeconds>");
        RM_SchemeData lay = One("<layers><li><primitive>Breath</primitive><scope>Room</scope><period>120</period></li></layers>");
        int diff = 0;
        for (int i = 0; i < 5000; i++) { double t = i * 0.37; if (RM_SchemeKernel.PaletteIndex(old, 9, i % 31, t, false) != RM_SchemeKernel.PaletteIndex(lay, 9, i % 31, t, false)) diff++; }
        Check("step 3: <layers><li>Breath</li></layers> runs exactly as the old <pattern>RoomBreath</pattern>", diff == 0, "diff=" + diff);

        // NextChange vs brute
        Func<int, RM_PatternCtx> ctx = k => new RM_PatternCtx { emitter = k, group = k % 37 };
        NextChangeAgrees("Breath", lay, true, 300, 0.05, 200, ctx);
        RM_SchemeData fast = One("<layers><li><primitive>Breath</primitive><scope>Fixture</scope><period>7</period><entries>1~2</entries></li></layers>");
        NextChangeAgrees("Breath (fixture scope, entries 1~2)", fast, true, 300, 0.01, 20, ctx);
        RM_SchemeData sp = One("<layers><li><primitive>Spark</primitive><period>12</period><rise>2.5</rise><oneIn>2</oneIn></li></layers>");
        NextChangeAgrees("Spark", sp, false, 300, 0.01, 60, ctx);
        RM_SchemeData flash = One("<flasherCount>1</flasherCount><flasherPeriodSeconds>0.9</flasherPeriodSeconds>");
        int fl0 = 0; double worst = 0;
        for (int i = 0; i < 200; i++)
        {
            var c = new RM_PatternCtx { emitter = i * 13 };
            double t0 = i * 3.1, nc = RM_PatternEvaluator.NextChange(flash, ref c, t0, true);
            if (RM_PatternEvaluator.Index(flash, ref c, nc - 1e-6, true) != RM_PatternEvaluator.Index(flash, ref c, t0, true)
                || RM_PatternEvaluator.Index(flash, ref c, nc + 1e-6, true) == RM_PatternEvaluator.Index(flash, ref c, t0, true)) fl0++;
            worst = Math.Max(worst, nc - t0);
        }
        Check("flasher NextChange is exact and within one flasher period", fl0 == 0 && worst <= 0.9 + 1e-6, "bad=" + fl0 + " worst=" + worst);

        // Breath own properties: spread 0 at Field = all rooms in sync; spread 1 = rooms differ; entries respected
        RM_SchemeData field = One("<layers><li><primitive>Breath</primitive><scope>Field</scope><period>60</period></li></layers>");
        bool sync = true;
        for (int g = 0; g < 50; g++) sync &= RM_SchemeKernel.PaletteIndex(field, g * 7, g, 33.3, false) == RM_SchemeKernel.PaletteIndex(field, 0, 0, 33.3, false);
        Check("Breath scope Field: every room and fixture in sync", sync);
        var phases = new HashSet<int>();
        for (int g = 0; g < 50; g++)
        {
            var c = new RM_PatternCtx { group = g };
            phases.Add((int)Math.Round(RM_PatternEvaluator.NextChange(lay, ref c, 0, false) * 1000));
        }
        Check("Breath scope Room, spread 1: room phases are distinct (>= 49 of 50 rooms, to the ms)", phases.Count >= 49, "distinct=" + phases.Count);
        RM_SchemeData half = One("<layers><li><primitive>Breath</primitive><period>60</period><phaseSpread>0</phaseSpread></li></layers>");
        bool sync0 = true;
        for (int g = 0; g < 50; g++) sync0 &= RM_SchemeKernel.PaletteIndex(half, 1, g, 41.0, false) == RM_SchemeKernel.PaletteIndex(half, 1, 0, 41.0, false);
        Check("Breath phaseSpread 0: rooms breathe together", sync0);
        bool inRange = true; int seenLo = 9, seenHi = -1;
        for (int i = 0; i < 4000; i++) { int x = RM_SchemeKernel.PaletteIndex(fast, i, i % 9, i * 0.11, false); inRange &= x >= 1 && x <= 2; seenLo = Math.Min(seenLo, x); seenHi = Math.Max(seenHi, x); }
        Check("Breath entries 1~2: only entries 1 and 2, both visited", inRange && seenLo == 1 && seenHi == 2, seenLo + ".." + seenHi);
        // Spark own property: rate within +-10% of 1/oneIn
        int sparkSlots = 0, slots = 0;
        for (int e = 0; e < 400; e++)
            for (int k = 0; k < 50; k++)
            {
                var c = new RM_PatternCtx { emitter = e };
                double t = k * 12.0 + 12.0 - RM_SchemeKernel.Frac01(e, 2) * 12.0 + 1.0;   // 1 s into slot k
                slots++;
                if (RM_PatternEvaluator.Index(sp, ref c, t, false) != 0) sparkSlots++;
            }
        double rate = sparkSlots / (double)slots;
        Check("Spark: slots that spark within +-10% of 1/oneIn (0.5)", Math.Abs(rate - 0.5) <= 0.05, "rate=" + rate.ToString("F3"));

        // composition: Over replaces, Max keeps the higher index
        RM_SchemeData over = One("<layers><li><primitive>Breath</primitive><period>60</period></li><li><primitive>Steady</primitive><entries>1</entries></li></layers>");
        RM_SchemeData max = One("<layers><li><primitive>Breath</primitive><period>60</period></li><li><primitive>Steady</primitive><entries>1</entries><combine>Max</combine></li></layers>");
        RM_SchemeData b60 = One("<layers><li><primitive>Breath</primitive><period>60</period></li></layers>");
        bool overOk = true, maxOk = true, maxSaw2 = false;
        for (int i = 0; i < 2000; i++)
        {
            double t = i * 0.23;
            int b0 = RM_SchemeKernel.PaletteIndex(b60, 1, 3, t, false);
            overOk &= RM_SchemeKernel.PaletteIndex(over, 1, 3, t, false) == 1;
            int m = RM_SchemeKernel.PaletteIndex(max, 1, 3, t, false);
            maxOk &= m == Math.Max(1, b0);
            maxSaw2 |= m == 2;
        }
        Check("combine Over: the top layer replaces what is below", overOk);
        Check("combine Max: the higher index wins (and the lower layer still shows through above it)", maxOk && maxSaw2);
        Check("cost class: Breath+Spark is Light; Steady alone is Still",
              RM_PatternKernel.Cost(sp.layers) == RM_CostClass.Light && RM_PatternKernel.Cost(One("<layers><li><primitive>Steady</primitive></li></layers>").layers) == RM_CostClass.Still);

        // (3) ConfigErrors cases for bad entries, combine and params
        Check("a clean layered scheme validates", RM_SchemeKernel.Errors(lay).Count == 0 && RM_SchemeKernel.Errors(sp).Count == 0 && RM_SchemeKernel.Errors(max).Count == 0, Errs(lay) + Errs(sp) + Errs(max));
        Check("entries outside the palette are refused", HasError(One("<layers><li><primitive>Breath</primitive><entries>1~5</entries></li></layers>"), "outside the palette"));
        Check("entries that do not parse are refused", HasError(One("<layers><li><primitive>Breath</primitive><entries>a~b</entries></li></layers>"), "is not 'lo~hi'"));
        Check("entries lo > hi are refused", HasError(One("<layers><li><primitive>Breath</primitive><entries>2~1</entries></li></layers>"), "outside the palette"));
        Check("an empty <layers/> is refused", HasError(One("<layers></layers>"), "at least one layer"));
        Check("Breath period 0 is refused", HasError(One("<layers><li><primitive>Breath</primitive><period>0</period></li></layers>"), "period must be > 0"));
        Check("Breath phaseSpread 2 is refused", HasError(One("<layers><li><primitive>Breath</primitive><phaseSpread>2</phaseSpread></li></layers>"), "phaseSpread"));
        Check("Spark rise longer than its slot is refused", HasError(One("<layers><li><primitive>Spark</primitive><period>2</period><rise>3</rise></li></layers>"), "rise"));
        Check("Spark oneIn 0 is refused", HasError(One("<layers><li><primitive>Spark</primitive><oneIn>0</oneIn></li></layers>"), "oneIn"));
        var badCombine = One("<layers><li><primitive>Breath</primitive></li></layers>"); badCombine.layers[0].combine = (RM_Combine)7;
        Check("an unknown combine is refused", HasError(badCombine, "combine"));
        foreach (RM_Primitive p in Enum.GetValues(typeof(RM_Primitive)))
            if (!RM_Primitives.Built(p))
            {
                Check("a primitive not built yet (" + p + ") is refused at load, never silently Steady",
                      HasError(One("<layers><li><primitive>" + p + "</primitive></li></layers>"), "not built"));
                break;
            }
        Check("L8 still holds for layers: a Steady-only layered scheme may not hold black",
              HasError(One("<mayGoDark>true</mayGoDark><layers><li><primitive>Steady</primitive></li></layers>", "<li>(0,0,0,0)</li><li>(64,26,8,0)</li>"), "L8"));
        Check("L8: black under a moving layer with mayGoDark is allowed",
              RM_SchemeKernel.Errors(One("<mayGoDark>true</mayGoDark><layers><li><primitive>Breath</primitive></li></layers>", "<li>(0,0,0,0)</li><li>(64,26,8,0)</li>")).Count == 0);
        Check("L11 still holds for layers: a near-white entry is refused", HasError(One("<layers><li><primitive>Breath</primitive></li></layers>", "<li>(182,118,62,0)</li><li>(240,240,235,0)</li>"), "L11"));
        bool threw = false;
        try { One("<layers><li><primitve>Breath</primitve></li></layers>"); } catch (FormatException) { threw = true; }
        Check("a misspelt layer field is refused by the loader (as RimWorld's loader reports it)", threw);

        // shipped defs load unchanged under the grammar
        string xml = Program.FindUp(System.IO.Path.Combine("Defs", "RM_AtmosphericSchemes.xml"));
        var shipped = xml == null ? new Dictionary<string, RM_SchemeData>() : Schemes(System.IO.File.ReadAllText(xml));
        bool allClean = shipped.Count > 0; string why = "";
        foreach (var kv in shipped) { var er = RM_SchemeKernel.Errors(kv.Value); if (er.Count > 0) { allClean = false; why += kv.Key + ": " + string.Join("; ", er) + " "; } }
        Check("step 3: every shipped scheme def loads and validates under the grammar (" + shipped.Count + ")", allClean, why);
    }

    internal static void Run()
    {
        Step2And3();
    }
}
