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
            scarLinger = float.Parse(v("scarLinger", "0"), inv),
            scarKeeps = v("scarKeeps", "false") == "true",
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

    // ---------------------------------------------------------------- build step 4: the graph substrate
    private static RM_RoomFacts R(int id, int cells = 20, bool th = false, bool shrine = false, bool power = false)
        => new RM_RoomFacts { id = id, cells = cells, threshold = th, shrine = shrine, power = power };
    private static KeyValuePair<int, int> D(int a, int b) => new KeyValuePair<int, int>(a, b);

    private static string Dist(RM_RoomGraph g, RM_Anchor a)
    {
        var p = new List<string>();
        for (int i = 0; i < g.Count; i++) p.Add(g.roomIds[i] + ":" + g.Distance(a, i));
        return string.Join(",", p);
    }

    private static RM_FixtureSet Fx(int n, Func<int, int> roomOf)
    {
        var e = new List<int>(); var r = new List<int>(); var x = new List<float>(); var z = new List<float>();
        for (int i = 0; i < n; i++) { e.Add(1000 + (i * 7919) % 997); r.Add(roomOf(i)); x.Add(i % 5); z.Add(i / 5); }
        return new RM_FixtureSet(e, r, x, z);
    }

    private static void Step4()
    {
        // ring of 6: 10-11-12-13-14-15-10, threshold at 10
        var ringRooms = new List<RM_RoomFacts> { R(10, 30, th: true), R(11), R(12), R(13), R(14), R(15) };
        var ringDoors = new List<KeyValuePair<int, int>> { D(10, 11), D(11, 12), D(12, 13), D(13, 14), D(14, 15), D(15, 10) };
        RM_RoomGraph ring = RM_RoomGraph.Build(ringRooms, ringDoors);
        Check("step 4 ring: hop distances from the threshold wrap both ways", Dist(ring, RM_Anchor.Threshold) == "10:0,11:1,12:2,13:3,14:2,15:1", Dist(ring, RM_Anchor.Threshold));
        Check("step 4 ring: the far room is 3 hops (max distance)", ring.MaxDistance(RM_Anchor.Threshold) == 3);
        Check("step 4 ring: every room is equally central, Core ties to the lowest id", ring.AnchorNodes(RM_Anchor.Core)[0] == ring.Node(10));

        // branch (tree): hall 1 with wings 2-3-4 and 5-6, and a dead end 7 off 1
        var brRooms = new List<RM_RoomFacts> { R(1, 60), R(2), R(3), R(4, 10, th: true), R(5), R(6, 90), R(7, 8, shrine: true) };
        var brDoors = new List<KeyValuePair<int, int>> { D(1, 2), D(2, 3), D(3, 4), D(1, 5), D(5, 6), D(1, 7) };
        RM_RoomGraph br = RM_RoomGraph.Build(brRooms, brDoors);
        Check("step 4 branch: Core is the hall (least eccentric)", br.roomIds[br.AnchorNodes(RM_Anchor.Core)[0]] == 1);
        Check("step 4 branch: Medoid is the hall (least total distance)", br.roomIds[br.AnchorNodes(RM_Anchor.Medoid)[0]] == 1);
        Check("step 4 branch: Open is the room with most doors", br.roomIds[br.AnchorNodes(RM_Anchor.Open)[0]] == 1);
        Check("step 4 branch: Grandest is the most cells", br.roomIds[br.AnchorNodes(RM_Anchor.Grandest)[0]] == 6);
        Check("step 4 branch: Shrine is the flagged room", br.roomIds[br.AnchorNodes(RM_Anchor.Shrine)[0]] == 7);
        Check("step 4 branch: no power room falls back to Core", br.roomIds[br.AnchorNodes(RM_Anchor.Power)[0]] == 1);
        Check("step 4 branch: distances from the threshold", Dist(br, RM_Anchor.Threshold) == "1:3,2:2,3:1,4:0,5:4,6:5,7:4", Dist(br, RM_Anchor.Threshold));

        // open plan: one big room and two closets; and a single room; and an empty map
        RM_RoomGraph open = RM_RoomGraph.Build(new List<RM_RoomFacts> { R(1, 400, th: true), R(2, 4), R(3, 4) }, new List<KeyValuePair<int, int>> { D(1, 2), D(1, 3) });
        Check("step 4 open plan: max distance 1", open.MaxDistance(RM_Anchor.Core) == 1 && open.MaxDistance(RM_Anchor.Threshold) == 1);
        RM_RoomGraph one = RM_RoomGraph.Build(new List<RM_RoomFacts> { R(5) }, null);
        Check("step 4 single room: every anchor is it, distance 0", one.Distance(RM_Anchor.Threshold, 0) == 0 && one.Distance(RM_Anchor.Grandest, 0) == 0 && one.MaxDistance(RM_Anchor.Core) == 0);
        RM_RoomGraph none = RM_RoomGraph.Build(null, null);
        Check("step 4 no rooms: an outdoor fixture sits at distance 1, nothing throws", none.Count == 0 && none.Distance(RM_Anchor.Core, -1) == 1);
        Check("step 4 an unknown room (outdoors) sits one past the farthest", br.Distance(RM_Anchor.Threshold, -1) == 6 && br.Distance(RM_Anchor.Threshold, br.Node(999)) == 6);

        // islands: an unreached room sits past the farthest too, never Unreached
        RM_RoomGraph isl = RM_RoomGraph.Build(new List<RM_RoomFacts> { R(1, th: true), R(2), R(3) }, new List<KeyValuePair<int, int>> { D(1, 2) });
        Check("step 4 island room is reachable-last, not lost", isl.Distance(RM_Anchor.Threshold, isl.Node(3)) == 2);

        // determinism: permuted input, duplicate and reversed doors, self-loops and unknown rooms change nothing
        var perm = new List<RM_RoomFacts>(brRooms); perm.Reverse();
        var pd = new List<KeyValuePair<int, int>>(brDoors) { D(2, 1), D(3, 3), D(4, 99), D(1, 2) }; pd.Reverse();
        RM_RoomGraph br2 = RM_RoomGraph.Build(perm, pd);
        Check("step 4 input order, duplicate/reversed doors, self-loops, unknown rooms: same key, same fields",
              br2.TopologyKey == br.TopologyKey && Dist(br2, RM_Anchor.Threshold) == Dist(br, RM_Anchor.Threshold));

        // invalidation: a wall edit (door added/removed, room split) moves the key; a fixture change does not touch the graph
        var cut = new List<KeyValuePair<int, int>>(ringDoors); cut.RemoveAt(2);
        Check("step 4 a door removed (wall edit) moves the topology key", RM_RoomGraph.Build(ringRooms, cut).TopologyKey != ring.TopologyKey);
        var more = new List<KeyValuePair<int, int>>(ringDoors) { D(10, 13) };
        Check("step 4 a door added moves the topology key", RM_RoomGraph.Build(ringRooms, more).TopologyKey != ring.TopologyKey);
        var split = new List<RM_RoomFacts>(ringRooms) { R(16) };
        Check("step 4 a room split off moves the topology key", RM_RoomGraph.Build(split, ringDoors).TopologyKey != ring.TopologyKey);
        var grown = new List<RM_RoomFacts>(ringRooms); grown[1] = R(11, 40);
        Check("step 4 a room resized moves the topology key", RM_RoomGraph.Build(grown, ringDoors).TopologyKey != ring.TopologyKey);
        int built = br.FieldsBuilt;
        for (int i = 0; i < 100; i++) { br.Field(RM_Anchor.Threshold); br.Distance(RM_Anchor.Threshold, i % br.Count); }
        Check("step 4 an anchor field is computed once and cached", br.FieldsBuilt == built);

        // fixture sets at 0/1/2/7/11/25: key moves with membership only, slot lookup is total, the graph is never rebuilt
        int[] counts = { 0, 1, 2, 7, 11, 25 };
        var keys = new HashSet<ulong>(); bool slotsOk = true, centroidOk = true; string why = "";
        foreach (int n in counts)
        {
            RM_FixtureSet fs = Fx(n, i => 1 + i % 7);
            keys.Add(fs.Key);
            for (int k = 0; k < fs.Count; k++) if (fs.Slot(fs.ids[k]) != k) { slotsOk = false; why += n + "/" + k + " "; }
            if (fs.Slot(-5) != -1) slotsOk = false;
            if (n == 0 && (fs.cx != 0 || fs.cz != 0)) centroidOk = false;
            if (n == 1 && (fs.cx != 0 || fs.cz != 0)) centroidOk = false;
            if (n == 25 && (Math.Abs(fs.cx - 2f) > 1e-5 || Math.Abs(fs.cz - 2f) > 1e-5)) centroidOk = false;
            for (int k = 1; k < fs.Count; k++) if (fs.ids[k] <= fs.ids[k - 1]) slotsOk = false;
            RM_PatternCtx c = RM_PatternCtx.Of(n > 0 ? fs.ids[0] : 7, 1, br, fs);
            if (n > 0 && (c.slot != 0 || c.node != br.Node(1))) slotsOk = false;
        }
        Check("step 4 fixture sets of 0/1/2/7/11/25: sorted, every slot found, unknown = -1", slotsOk, why);
        Check("step 4 fixture-set centroids", centroidOk);
        Check("step 4 fixture-set keys differ with membership", keys.Count == counts.Length);
        Check("step 4 the same membership in any order gives the same key",
              new RM_FixtureSet(new[] { 3, 1, 2 }, new[] { 1, 1, 2 }, new[] { 0f, 1f, 2f }, new[] { 0f, 0f, 0f }).Key
              == new RM_FixtureSet(new[] { 1, 2, 3 }, new[] { 1, 2, 1 }, new[] { 1f, 2f, 0f }, new[] { 0f, 0f, 0f }).Key);
        Check("step 4 a fixture moved to another room moves the key",
              new RM_FixtureSet(new[] { 1, 2 }, new[] { 1, 1 }, new[] { 0f, 1f }, new[] { 0f, 0f }).Key
              != new RM_FixtureSet(new[] { 1, 2 }, new[] { 1, 2 }, new[] { 0f, 1f }, new[] { 0f, 0f }).Key);
        Check("step 4 the graph-free ctx (old PaletteIndex call) still evaluates bit-identically",
              RM_SchemeKernel.PaletteIndex(One("<layers><li><primitive>Breath</primitive></li></layers>"), 42, 3, 17.25, false)
              == RM_SchemeKernel.PaletteIndex(One("<layers><li><primitive>Breath</primitive></li></layers>"), ref Ctx(42, 3, br), 17.25, false));

        // cost: a 400-room grid builds and fields every anchor quickly (the compositor caps the base at 400 rooms)
        var gr = new List<RM_RoomFacts>(); var gd = new List<KeyValuePair<int, int>>();
        for (int i = 0; i < 400; i++) { gr.Add(R(i, 10 + i % 13, th: i < 20)); if (i % 20 != 19) gd.Add(D(i, i + 1)); if (i + 20 < 400) gd.Add(D(i, i + 20)); }
        var sw = System.Diagnostics.Stopwatch.StartNew();
        RM_RoomGraph big = RM_RoomGraph.Build(gr, gd);
        foreach (RM_Anchor a in Enum.GetValues(typeof(RM_Anchor))) big.Field(a);
        sw.Stop();
        Check("step 4 400-room grid: build + all 7 anchor fields under 2 s (" + sw.ElapsedMilliseconds + " ms)", sw.ElapsedMilliseconds < 2000);
        Check("step 4 400-room grid: threshold row 0, far row 19 hops", big.MaxDistance(RM_Anchor.Threshold) == 19);
    }

    // ---------------------------------------------------------------- build step 5: P3 TIDE (as a layer)
    private static RM_RoomGraph Branch()
    {
        var rooms = new List<RM_RoomFacts> { R(1, 60), R(2), R(3), R(4, 10, th: true), R(5), R(6, 90), R(7, 8), R(8), R(9) };
        var doors = new List<KeyValuePair<int, int>> { D(1, 2), D(2, 3), D(3, 4), D(1, 5), D(5, 6), D(1, 7), D(1, 8), D(1, 9) };
        return RM_RoomGraph.Build(rooms, doors);
    }

    private static void Step5()
    {
        const string tide = "<layers><li><primitive>Tide</primitive><period>300</period><anchor>Threshold</anchor>{0}</li></layers>";
        string two = "<li>(40,20,8,0)</li><li>(220,158,96,0)</li>";
        RM_RoomGraph g = Branch();
        Func<int, RM_PatternCtx> onGraph = i => RM_PatternCtx.Of(i, i % 11 == 10 ? -1 : g.roomIds[i % 11 % g.Count], g, null);
        RM_SchemeData t3 = One(string.Format(tide, ""));
        RM_SchemeData t2 = One(string.Format(tide, ""), two);
        NextChangeAgrees("step 5 tide, 3 entries, branch graph", t3, true, 300, 0.05, 330, onGraph);
        NextChangeAgrees("step 5 tide, 2 entries, ragged 0.2, hold 0", One(string.Format(tide, "<ragged>0.2</ragged><hold>0</hold>"), two), true, 300, 0.05, 330, onGraph, 9);
        NextChangeAgrees("step 5 tide, low 0.2 high 0.7 band 2", One(string.Format(tide, "<low>0.2</low><high>0.7</high><band>2</band>"), "<li>(40,20,8,0)</li><li>(90,50,20,0)</li><li>(150,90,40,0)</li><li>(220,158,96,0)</li>"), true, 300, 0.05, 330, onGraph, 11);

        // the flood runs outward from the anchor by door-distance; each room enters once and leaves once per period
        var enter = new Dictionary<int, double>(); var flips = new Dictionary<int, int>();
        var last = new Dictionary<int, int>();
        int sameInstant = 0, maxAtOnce = 0;
        for (double t = 0; t < 300; t += 0.02)
        {
            int now = 0;
            for (int i = 0; i < g.Count; i++)
            {
                RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null);
                int v = RM_PatternEvaluator.Index(t2, ref c, t, false);
                if (last.TryGetValue(i, out int pv) && pv != v) { flips[i] = (flips.TryGetValue(i, out int f) ? f : 0) + 1; now++; if (v == 1 && !enter.ContainsKey(i)) enter[i] = t; }
                last[i] = v;
            }
            if (now > 1) sameInstant++;
            if (now > maxAtOnce) maxAtOnce = now;
        }
        bool ordered = enter.Count == g.Count; string ord = "";
        for (int i = 0; i < g.Count && ordered; i++)
            for (int j = 0; j < g.Count; j++)
                if (g.Distance(RM_Anchor.Threshold, i) < g.Distance(RM_Anchor.Threshold, j) && enter[i] >= enter[j]) { ordered = false; ord = g.roomIds[i] + " after " + g.roomIds[j]; break; }
        Check("step 5 tide floods outward: a nearer room always enters before a farther one (ragged 0.04)", ordered, ord + " entered=" + enter.Count);
        bool once = true;
        for (int i = 0; i < g.Count; i++) if (!flips.TryGetValue(i, out int f) || f != 2) once = false;
        Check("step 5 tide: every room flips exactly twice per period (in once, out once: no chatter at the front)", once);
        Check("step 5 tide: equal-distance rooms never flip in the same 20 ms (the tie-break), at most one room at a time", sameInstant == 0 && maxAtOnce == 1, "same=" + sameInstant + " max=" + maxAtOnce);

        // hold: the water stands; full flood lights all, full ebb darkens all; an outdoor fixture is reached last
        bool held = true;
        for (int i = 0; i < 11; i++)
        {
            RM_PatternCtx c = onGraph(i);
            if (RM_PatternEvaluator.Index(t3, ref c, 0.45 * 300, false) != 2 || RM_PatternEvaluator.Index(t3, ref c, 0.95 * 300, false) != 0) held = false;
        }
        Check("step 5 tide: full flood stands at hi for every fixture, full ebb at lo (hold 0.1)", held);
        RM_PatternCtx outd = RM_PatternCtx.Of(77, -1, g, null);
        double uOut = RM_TidePrimitive.Position(t3.layers[0], ref outd);
        bool lastIn = true;
        for (int i = 0; i < g.Count; i++) { RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null); if (RM_TidePrimitive.Position(t3.layers[0], ref c) >= uOut) lastIn = false; }
        Check("step 5 tide: an outdoor fixture sits past every room", lastIn);

        // front size: rooms caught mid-step (strictly between lo and hi) span at most band+1 shells
        bool narrow = true;
        for (double t = 0; t < 300 && narrow; t += 0.5)
        {
            int dmin = int.MaxValue, dmax = -1;
            for (int i = 0; i < g.Count; i++)
            {
                RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null);
                int v = RM_PatternEvaluator.Index(t3, ref c, t, false);
                if (v == 1) { int d = g.Distance(RM_Anchor.Threshold, i); dmin = Math.Min(dmin, d); dmax = Math.Max(dmax, d); }
            }
            if (dmax >= 0 && dmax - dmin > 2) narrow = false;
        }
        Check("step 5 tide: the front (rooms mid-step) is never wider than band + 1 shells", narrow);

        // one room: the tide goes round it in angle order about the fixtures' centroid (degenerates to a wedge)
        RM_RoomGraph one = RM_RoomGraph.Build(new List<RM_RoomFacts> { R(1, 100) }, null);
        var ems = new List<int>(); var rs = new List<int>(); var xs = new List<float>(); var zs = new List<float>();
        for (int i = 0; i < 11; i++) { double a = 2 * Math.PI * (i + 0.5) / 11 - Math.PI; ems.Add(500 + i); rs.Add(1); xs.Add((float)(10 + 5 * Math.Cos(a))); zs.Add((float)(10 + 5 * Math.Sin(a))); }
        var fs = new RM_FixtureSet(ems, rs, xs, zs);
        var en1 = new double[11];
        for (int i = 0; i < 11; i++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(500 + i, 1, one, fs);
            en1[i] = -1;
            for (double t = 0; t < 150; t += 0.02) if (RM_PatternEvaluator.Index(t2, ref c, t, false) == 1) { en1[i] = t; break; }
        }
        int descents = 0; bool round = true;
        for (int i = 0; i < 11; i++) { if (en1[i] < 0) round = false; if (!(en1[(i + 1) % 11] > en1[i])) descents++; }
        round &= descents == 1;   // cyclic angle order: one wrap, wherever the sweep starts
        Check("step 5 tide in one room: fixtures enter in angle order round the centroid (wedge degeneration)", round, string.Join(",", Array.ConvertAll(en1, v => v.ToString("F1"))));
        RM_PatternCtx bare = new RM_PatternCtx { emitter = 3, group = 9, node = -1, slot = -1 };
        Check("step 5 tide without a graph (old call shape) evaluates without throwing",
              RM_PatternEvaluator.Index(t3, ref bare, 10, false) >= 0 && RM_PatternEvaluator.NextChange(t3, ref bare, 10, false) > 10);

        Check("step 5 tide cost class is Front", RM_PatternKernel.Cost(t3.layers) == RM_CostClass.Front);
        Check("step 5 tide is motion for L8", RM_SchemeKernel.Errors(One("<mayGoDark>true</mayGoDark>" + string.Format(tide, ""), "<li>(0,0,0,0)</li><li>(64,26,8,0)</li>")).Count == 0);
        Check("step 5 tide: period under 240 s refused", HasError(One("<layers><li><primitive>Tide</primitive><period>120</period></li></layers>"), "240"));
        Check("step 5 tide: ragged 0.3 refused", HasError(One(string.Format(tide, "<ragged>0.3</ragged>")), "ragged"));
        Check("step 5 tide: hold 0.5 refused", HasError(One(string.Format(tide, "<hold>0.5</hold>")), "hold"));
        Check("step 5 tide: low >= high refused", HasError(One(string.Format(tide, "<low>0.6</low><high>0.6</high>")), "low and high"));
        Check("step 5 tide: band 0 refused", HasError(One(string.Format(tide, "<band>0</band>")), "band"));
        Check("step 5 tide: an unknown anchor is refused by the loader", Throws(() => One(string.Format(tide, "").Replace("Threshold", "Nowhere"))));
        Check("step 5 tide: a clean tide has no errors", RM_SchemeKernel.Errors(t3).Count == 0, string.Join("; ", RM_SchemeKernel.Errors(t3)));
    }

    // first time in [0, horizon) a fixture's index leaves lo (-1 = never)
    private static double FirstLit(RM_SchemeData s, ref RM_PatternCtx c, double horizon, double dt)
    {
        for (double t = 0; t < horizon; t += dt) if (RM_PatternEvaluator.Index(s, ref c, t, false) != 0) return t;
        return -1;
    }

    private static void Step6()
    {
        const string rip = "<layers><li><primitive>Ripple</primitive><period>60</period><anchor>Core</anchor>{0}</li></layers>";
        const string swp = "<layers><li><primitive>Sweep</primitive><period>40</period>{0}</li></layers>";
        string three = "<li>(40,20,8,0)</li><li>(130,90,40,0)</li><li>(220,158,96,0)</li>";
        string two = "<li>(40,20,8,0)</li><li>(220,158,96,0)</li>";
        RM_RoomGraph g = Branch();
        var ems = new List<int>(); var rs = new List<int>(); var xs = new List<float>(); var zs = new List<float>();
        for (int i = 0; i < 22; i++) { ems.Add(700 + i); rs.Add(g.roomIds[i % g.Count]); xs.Add(3 * (i % 7) + 0.5f * i); zs.Add(2 * (i / 7) + (i % 3)); }
        var fs = new RM_FixtureSet(ems, rs, xs, zs);
        Func<int, RM_PatternCtx> onGraph = i => RM_PatternCtx.Of(700 + i % 22, i % 13 == 12 ? -1 : g.roomIds[i % 22 % g.Count], g, fs);

        NextChangeAgrees("step 6 ripple shell, 3 entries", One(string.Format(rip, ""), three), true, 300, 0.05, 130, onGraph);
        NextChangeAgrees("step 6 ripple bloom, 3 entries, hold 3", One(string.Format(rip, "<fill>Bloom</fill><holdSeconds>3</holdSeconds><width>2</width>"), three), true, 300, 0.05, 130, onGraph, 5);
        NextChangeAgrees("step 6 ripple in, fixture seed", One(string.Format(rip, "<seed>Fixture</seed><direction>In</direction><speed>1</speed>"), two), true, 300, 0.05, 130, onGraph, 7);
        NextChangeAgrees("step 6 ripple hull, oneShot", One(string.Format(rip, "<seed>Hull</seed><oneShot>true</oneShot>"), three), true, 200, 0.05, 40, onGraph, 8);
        NextChangeAgrees("step 6 sweep axis, 3 entries", One(string.Format(swp, "<angle>30</angle>"), three), true, 300, 0.02, 90, onGraph);
        NextChangeAgrees("step 6 sweep turn, lit 0.5", One(string.Format(swp, "<field>Turn</field><lit>0.5</lit>"), two), true, 300, 0.02, 90, onGraph, 3);
        NextChangeAgrees("step 6 sweep toward, lit 1", One(string.Format(swp, "<field>Toward</field><lit>1</lit>"), three), true, 300, 0.02, 90, onGraph, 4);

        // ripple is monotone in graph distance: a farther room never lights before a nearer one
        RM_SchemeData r3 = One(string.Format(rip, ""), three);
        var first = new double[g.Count]; bool mono = true; string why = "";
        for (int i = 0; i < g.Count; i++) { RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null); first[i] = FirstLit(r3, ref c, 60, 0.01); }
        for (int i = 0; i < g.Count; i++) for (int j = 0; j < g.Count; j++)
            if (g.Distance(RM_Anchor.Core, i) < g.Distance(RM_Anchor.Core, j) && !(first[i] >= 0 && first[i] < first[j])) { mono = false; why = g.roomIds[i] + " vs " + g.roomIds[j]; }
        Check("step 6 ripple: first-lit time strictly increases with door-distance from the seed", mono, why);
        RM_SchemeData rIn = One(string.Format(rip, "<direction>In</direction>"), three);
        bool monoIn = true;
        for (int i = 0; i < g.Count; i++) { RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null); first[i] = FirstLit(rIn, ref c, 60, 0.01); }
        for (int i = 0; i < g.Count; i++) for (int j = 0; j < g.Count; j++)
            if (g.Distance(RM_Anchor.Core, i) > g.Distance(RM_Anchor.Core, j) && !(first[i] < first[j])) monoIn = false;
        Check("step 6 ripple In: the ring closes on the seed (farthest room first)", monoIn);

        // one shot fires once; bloom stands
        RM_SchemeData once = One(string.Format(rip, "<oneShot>true</oneShot>"), three);
        bool fired = true;
        for (int i = 0; i < g.Count; i++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null);
            if (FirstLit(once, ref c, 30, 0.02) < 0) fired = false;
            for (double t = 30; t < 400; t += 0.5) if (RM_PatternEvaluator.Index(once, ref c, t, false) != 0) fired = false;
            if (!double.IsPositiveInfinity(RM_PatternEvaluator.NextChange(once, ref c, 31, false))) fired = false;
        }
        Check("step 6 ripple oneShot: every room lights once, then lo for good and NextChange is Never", fired);
        RM_SchemeData bloom = One(string.Format(rip, "<fill>Bloom</fill><holdSeconds>5</holdSeconds>"), three);
        double tg = (g.MaxDistance(RM_Anchor.Core) + 1 + 1) / 0.5;
        bool stands = true;
        for (int i = 0; i < 13; i++) { RM_PatternCtx c = onGraph(i); for (double t = tg + 0.01; t < tg + 5; t += 0.1) if (RM_PatternEvaluator.Index(bloom, ref c, t, false) != 2) stands = false; }
        Check("step 6 ripple bloom: the whole base stands at hi for holdSeconds", stands);

        // sweep toward: within a wave, an inner room never lights after its outward neighbour
        RM_SchemeData tw = One(string.Format(swp, "<field>Toward</field><lit>0.3</lit>"), two);
        bool outward = true;
        for (int i = 0; i < g.Count; i++) { RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null); first[i] = FirstLit(tw, ref c, 40, 0.01); }
        for (int i = 0; i < g.Count; i++) foreach (int j in g.adj[i])
            if (g.Distance(RM_Anchor.Threshold, j) < g.Distance(RM_Anchor.Threshold, i) && !(first[i] < first[j])) outward = false;
        Check("step 6 sweep Toward: the wave runs outward (deeper room lights before its rim-side neighbour)", outward);

        // sweep turn: one room of fixtures on a circle goes round in angle order
        RM_RoomGraph one = RM_RoomGraph.Build(new List<RM_RoomFacts> { R(1, 100) }, null);
        var e2 = new List<int>(); var r2 = new List<int>(); var x2 = new List<float>(); var z2 = new List<float>();
        for (int i = 0; i < 11; i++) { double a = 2 * Math.PI * (i + 0.5) / 11 - Math.PI; e2.Add(500 + i); r2.Add(1); x2.Add((float)(10 + 5 * Math.Cos(a))); z2.Add((float)(10 + 5 * Math.Sin(a))); }
        var f2 = new RM_FixtureSet(e2, r2, x2, z2);
        RM_SchemeData turn = One(string.Format(swp, "<field>Turn</field><lit>0.2</lit>"), two);
        var en = new double[11]; int desc = 0; bool all = true;
        for (int i = 0; i < 11; i++) { RM_PatternCtx c = RM_PatternCtx.Of(500 + i, 1, one, f2); en[i] = FirstLit(turn, ref c, 40, 0.01); if (en[i] < 0) all = false; }
        for (int i = 0; i < 11; i++) if (!(en[(i + 1) % 11] > en[i])) desc++;
        Check("step 6 sweep Turn: the beam goes round the fixtures in angle order", all && desc == 1, string.Join(",", Array.ConvertAll(en, v => v.ToString("F2"))));
        RM_PatternCtx bare = new RM_PatternCtx { emitter = 3, group = 9, node = -1, slot = -1 };
        Check("step 6 ripple and sweep without a graph evaluate without throwing",
              RM_PatternEvaluator.Index(r3, ref bare, 10, false) >= 0 && RM_PatternEvaluator.NextChange(tw, ref bare, 10, false) > 10);

        Check("step 6 ripple and sweep cost class is Front", RM_PatternKernel.Cost(r3.layers) == RM_CostClass.Front && RM_PatternKernel.Cost(tw.layers) == RM_CostClass.Front);
        Check("step 6 ripple: speed 0 refused", HasError(One(string.Format(rip, "<speed>0</speed>")), "speed"));
        Check("step 6 ripple: width 0 refused", HasError(One(string.Format(rip, "<width>0</width>")), "width"));
        Check("step 6 ripple: negative holdSeconds refused", HasError(One(string.Format(rip, "<holdSeconds>-1</holdSeconds>")), "holdSeconds"));
        Check("step 6 sweep: lit 0 refused", HasError(One(string.Format(swp, "<lit>0</lit>")), "lit"));
        Check("step 6 sweep: lit 1.5 refused", HasError(One(string.Format(swp, "<lit>1.5</lit>")), "lit"));
        Check("step 6 sweep: an unknown field is refused by the loader", Throws(() => One(string.Format(swp, "<field>Sideways</field>"))));
        Check("step 6 clean ripple and sweep have no errors", RM_SchemeKernel.Errors(r3).Count == 0 && RM_SchemeKernel.Errors(tw).Count == 0,
              string.Join("; ", RM_SchemeKernel.Errors(r3)) + string.Join("; ", RM_SchemeKernel.Errors(tw)));
    }

    private static void Step7Review()
    {
        // review fix: a def pre-builds its one-pattern form once (s.legacy); the pre-built path equals the per-call path
        RM_SchemeData sp = One("<pattern>Sparks</pattern><massPeriodSeconds>12</massPeriodSeconds><sparkSeconds>2</sparkSeconds><sparkOneIn>2</sparkOneIn>");
        RM_SchemeData pre = sp; pre.legacy = RM_PatternKernel.LegacyLayers(sp);
        int d = 0;
        for (int i = 0; i < 3000; i++) { double t = i * 0.9; if (RM_SchemeKernel.PaletteIndex(sp, i, i % 7, t, false) != RM_SchemeKernel.PaletteIndex(pre, i, i % 7, t, false)) d++; }
        Check("review: the pre-built legacy layers (no per-tick allocation) give the same index as the per-call build", d == 0, "diff=" + d);
        // large t (a long session, 10^7 s): fronts stay finite, NextChange stays after t and finite-or-Never
        RM_RoomGraph g = Branch();
        string three = "<li>(40,20,8,0)</li><li>(130,90,40,0)</li><li>(220,158,96,0)</li>";
        string[] bodies = {
            "<layers><li><primitive>Tide</primitive><period>300</period><anchor>Threshold</anchor></li></layers>",
            "<layers><li><primitive>Ripple</primitive><period>60</period></li></layers>",
            "<layers><li><primitive>Ripple</primitive><period>60</period><fill>Bloom</fill></li></layers>",
            "<layers><li><primitive>Sweep</primitive><period>40</period><field>Toward</field></li></layers>" };
        int bad = 0; string first = "";
        foreach (string b in bodies)
        {
            RM_SchemeData s = One(b, three);
            for (int i = 0; i < g.Count; i++)
                foreach (double t0 in new[] { 1e7, 3.3e7 + 0.37 })
                {
                    RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null);
                    int v = RM_PatternEvaluator.Index(s, ref c, t0, false);
                    double nc = RM_PatternEvaluator.NextChange(s, ref c, t0, false);
                    if (v < 0 || v > 2 || double.IsNaN(nc) || !(nc > t0) || nc > t0 + 1000)
                    { bad++; if (first == "") first = b.Substring(0, 60) + " room " + i + " t=" + t0 + " v=" + v + " nc=" + nc; }
                }
        }
        Check("review: tide, ripple and sweep at t = 1e7..3e7 s: index in range, NextChange after t and within a period", bad == 0, "bad=" + bad + " " + first);
    }

    // ---------------------------------------------------------------- review R1: sweep islands, topology key behaviour
    private static void StepR1()
    {
        // an island room (no door to any threshold room) is lit by Sweep Toward after every reachable room and after
        // outdoors, at the same place every time
        var rooms = new List<RM_RoomFacts> { R(1, 60), R(2), R(3), R(4, 10, th: true), R(5), R(6, 90), R(7, 8), R(8), R(9), R(20, 30) };
        var doors = new List<KeyValuePair<int, int>> { D(1, 2), D(2, 3), D(3, 4), D(1, 5), D(5, 6), D(1, 7), D(1, 8), D(1, 9) };
        RM_RoomGraph g = RM_RoomGraph.Build(rooms, doors);
        RM_SchemeData tw = One("<layers><li><primitive>Sweep</primitive><period>40</period><field>Toward</field><lit>0.02</lit></li></layers>",
                               "<li>(40,20,8,0)</li><li>(220,158,96,0)</li>");
        int isl = g.Node(20);
        RM_PatternCtx ci = RM_PatternCtx.Of(20, 20, g, null);
        double tIsl = FirstLit(tw, ref ci, 40, 0.005), tIsl2 = FirstLit(tw, ref ci, 40, 0.005);
        RM_PatternCtx co = RM_PatternCtx.Of(99, -1, g, null);
        double tOut = FirstLit(tw, ref co, 40, 0.005);
        bool lastAll = tIsl > tOut;
        string why = "island=" + tIsl.ToString("F3") + " outdoors=" + tOut.ToString("F3");
        for (int i = 0; i < g.Count; i++)
        {
            if (i == isl) continue;
            RM_PatternCtx c = RM_PatternCtx.Of(i, g.roomIds[i], g, null);
            double ti = FirstLit(tw, ref c, 40, 0.005);
            if (!(ti >= 0 && ti < tIsl)) { lastAll = false; why += " room " + g.roomIds[i] + "=" + ti.ToString("F3"); }
        }
        Check("R1 sweep Toward: a room unreachable from any threshold room is lit after every reachable room and after outdoors", lastAll && tIsl >= 0, why);
        Check("R1 sweep Toward: the island's place is deterministic (same first-lit time on a second pass)", tIsl == tIsl2);
        NextChangeAgrees("R1 sweep toward with an island room", tw, true, 200, 0.02, 90, i => RM_PatternCtx.Of(i, i % 12 == 11 ? -1 : g.roomIds[i % 12 % g.Count], g, null), 13);

        // the keep-or-replace rule the compositor runs (RM_GraphCache.Refresh): a fixture change never rebuilds the
        // graph or touches its cached fields; a door edit does
        var ems = new List<int> { 501, 502, 503, 504 }; var rid = new List<int> { 1, 3, 6, 77 };
        var xs = new List<float> { 1, 5, 9, 30 }; var zs = new List<float> { 2, 2, 7, 30 };
        RM_GraphRefresh a = RM_GraphCache.Refresh(null, null, rooms, doors, ems, rid, xs, zs);
        Check("R1 cache: the first pass builds both the graph and the fixture set", a.graphRebuilt && a.fixturesRebuilt && a.graph != null && a.fixtures != null);
        Check("R1 cache: a fixture in a room outside the graph is outdoors (-1)", a.fixtures.room[a.fixtures.Slot(504)] == -1 && a.fixtures.room[a.fixtures.Slot(502)] == 3);
        a.graph.Field(RM_Anchor.Threshold); a.graph.Field(RM_Anchor.Core); a.graph.FieldFrom(2);
        int built = a.graph.FieldsBuilt;
        var rev = new List<RM_RoomFacts>(rooms); rev.Reverse();
        var ems2 = new List<int> { 501, 503, 505, 506 }; var rid2 = new List<int> { 1, 6, 3, 9 };          // 502 released, 505/506 taken
        var xs2 = new List<float> { 1.5f, 9, 4, 12 }; var zs2 = new List<float> { 2, 7.5f, 3, 1 };         // 501 and 503 moved
        RM_GraphRefresh b = RM_GraphCache.Refresh(a.graph, a.fixtures, rev, doors, ems2, rid2, xs2, zs2);
        Check("R1 cache: lamps taken, released and moved inside the base keep the SAME graph instance (no rebuild)", !b.graphRebuilt && ReferenceEquals(b.graph, a.graph));
        Check("R1 cache: ... and rebuild no cached field (FieldsBuilt unchanged after re-reading every field)",
              Fields(b.graph) == built, "before=" + built + " after=" + b.graph.FieldsBuilt);
        Check("R1 cache: ... while the fixture set IS replaced (membership key moved)", b.fixturesRebuilt && b.fixtures.Key != a.fixtures.Key);
        RM_GraphRefresh c2 = RM_GraphCache.Refresh(b.graph, b.fixtures, rooms, doors, ems2, rid2, xs2, zs2);
        Check("R1 cache: an unchanged pass replaces nothing", !c2.graphRebuilt && !c2.fixturesRebuilt && ReferenceEquals(c2.fixtures, b.fixtures));
        var cut = new List<KeyValuePair<int, int>>(doors); cut.RemoveAt(0);
        RM_GraphRefresh d = RM_GraphCache.Refresh(c2.graph, c2.fixtures, rooms, cut, ems2, rid2, xs2, zs2);
        Check("R1 cache: a door edit (same fixtures) replaces the graph", d.graphRebuilt && !ReferenceEquals(d.graph, c2.graph) && !d.fixturesRebuilt);
        var flagged = new List<RM_RoomFacts>(rooms); flagged[5] = R(6, 90, shrine: true);
        Check("R1 cache: a room gaining a shrine flag replaces the graph (flags are topology)", RM_GraphCache.Refresh(c2.graph, c2.fixtures, flagged, doors, ems2, rid2, xs2, zs2).graphRebuilt);
    }

    private static int Fields(RM_RoomGraph g) { g.Field(RM_Anchor.Threshold); g.Field(RM_Anchor.Core); g.FieldFrom(2); return g.FieldsBuilt; }

    private static bool Throws(Action a) { try { a(); return false; } catch (Exception) { return true; } }

    private static RM_PatternCtx ctxBox;
    private static ref RM_PatternCtx Ctx(int e, int g, RM_RoomGraph graph) { ctxBox = RM_PatternCtx.Of(e, g, graph, null); return ref ctxBox; }

    internal static void Run()
    {
        Step2And3();
        Step4();
        Step5();
        Step6();
        Step7Review();
        StepR1();
        WalkerTests.Run();
        ModifierTests.Run();
        TerritoryTests.Run();
    }
}
