// Selftest for mandrake.rm.atmosphericbase (ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 1-4).
//
// REAL, compiled from production source:
//   RM_AtmosphericKernel.Classify - the hard exclusion list (pawn, plant, worn/equipment, hologram) beating
//     capability, and capability (glower + building + owned + spawned) deciding the rest.
//   RM_GlowAccess - snapshot / drive / restore against a REAL Verse.CompGlower from the shipped Assembly-CSharp.
//     The CompGlower's parent is a new, never-spawned ThingWithComps, so ShouldBeLitNow is false and
//     SetGlowColorInternal writes the override without touching a GlowGrid. That is the same branch an unlit lamp
//     takes in game; the lit branch (DeRegister/Register) is the live proof's business.
// NOT covered: anything that needs a Map (discovery over listerBuildings, the buttons, pruning, Scribe).
using System;
using System.Collections.Generic;
using RimMandrake.AtmosphericBase;
using RimWorld;
using Verse;

internal static class Program
{
    internal static readonly List<string> Fails = new List<string>();

    internal static void Check(string name, bool ok, string detail = "")
    {
        Console.WriteLine((ok ? "ok    " : "FAIL  ") + name + (ok ? "" : "  " + detail));
        if (!ok) Fails.Add(name);
    }

    private static RM_EmitterFacts Lamp()
    {
        return new RM_EmitterFacts { hasGlower = true, isBuilding = true, playerOwned = true, spawned = true,
                                     defName = "StandingLamp", thingClassName = "Building" };
    }

    private static CompGlower Glower(ColorInt color, float radius)
    {
        var g = new CompGlower();
        g.parent = new ThingWithComps();
        g.props = new CompProperties_Glower { glowColor = color, glowRadius = radius };
        return g;
    }

    // ================================================================== Phase 2: schemes, pattern, changed-only
    // REAL: RM_SchemeKernel (validation, the pattern, flasher choice, default groups) and RM_ChangeTracker, plus the
    // SHIPPED Defs/RM_AtmosphericSchemes.xml read off disk and validated by the same kernel the def's ConfigErrors uses.
    // NOT covered: the game-side loop (rooms, CompGlower.Glows, the regrid) -- ProofCompositor's business.

    private static RM_SchemeData Pal(params int[] rgb)
    {
        int n = rgb.Length / 3;
        var s = new RM_SchemeData { r = new int[n], g = new int[n], b = new int[n], pattern = RM_PatternKind.RoomBreath,
                                    massPeriodSeconds = 120f, sparkSeconds = 2f, sparkOneIn = 2 };
        for (int i = 0; i < n; i++) { s.r[i] = rgb[3 * i]; s.g[i] = rgb[3 * i + 1]; s.b[i] = rgb[3 * i + 2]; }
        return s;
    }

    internal static string FindUp(string rel)
    {
        string d = AppDomain.CurrentDomain.BaseDirectory;
        for (int i = 0; i < 14 && d != null; i++)
        {
            string p = System.IO.Path.Combine(d, rel);
            if (System.IO.File.Exists(p)) return p;
            d = System.IO.Path.GetDirectoryName(d.TrimEnd('\\', '/'));
        }
        return null;
    }

    private static List<KeyValuePair<string, RM_SchemeData>> ShippedSchemes(string path)
    {
        var outp = new List<KeyValuePair<string, RM_SchemeData>>();
        var doc = new System.Xml.XmlDocument();
        doc.Load(path);
        foreach (System.Xml.XmlNode n in doc.DocumentElement.ChildNodes)
        {
            if (n.NodeType != System.Xml.XmlNodeType.Element) continue;
            var rs = new List<int>(); var gs = new List<int>(); var bs = new List<int>();
            foreach (System.Xml.XmlNode li in n["palette"].ChildNodes)
            {
                if (li.NodeType != System.Xml.XmlNodeType.Element) continue;
                // ParseHelper.ParseColorInt calls a String.Split overload .NET Framework lacks (MissingMethodException
                // here; Unity's Mono has it), so the "(r,g,b,a)" integer form the file uses is split by hand.
                string[] parts = li.InnerText.Trim().TrimStart('(').TrimEnd(')').Split(',');
                rs.Add(int.Parse(parts[0].Trim())); gs.Add(int.Parse(parts[1].Trim())); bs.Add(int.Parse(parts[2].Trim()));
            }
            Func<string, string, string> v = (k, def) => n[k]?.InnerText ?? def;
            var s = new RM_SchemeData
            {
                r = rs.ToArray(), g = gs.ToArray(), b = bs.ToArray(),
                pattern = (RM_PatternKind)Enum.Parse(typeof(RM_PatternKind), v("pattern", "Steady")),
                massPeriodSeconds = float.Parse(v("massPeriodSeconds", "120"), System.Globalization.CultureInfo.InvariantCulture),
                sparkSeconds = float.Parse(v("sparkSeconds", "2"), System.Globalization.CultureInfo.InvariantCulture),
                sparkOneIn = int.Parse(v("sparkOneIn", "2")),
                mayGoDark = v("mayGoDark", "false") == "true",
                flasherCount = int.Parse(v("flasherCount", "0")),
                flasherPeriodSeconds = float.Parse(v("flasherPeriodSeconds", "0"), System.Globalization.CultureInfo.InvariantCulture),
            };
            outp.Add(new KeyValuePair<string, RM_SchemeData>(n["defName"].InnerText, s));
        }
        return outp;
    }

    private static void Phase2()
    {
        // ---- validation: each law the kernel enforces, by a planted bad scheme
        RM_SchemeData ok = Pal(204, 150, 92, 224, 168, 104, 244, 188, 118);
        Check("a warm three-entry RoomBreath scheme validates clean", RM_SchemeKernel.Errors(ok).Count == 0, string.Join("; ", RM_SchemeKernel.Errors(ok)));
        Check("L11: a bright-white entry is refused", RM_SchemeKernel.Errors(Pal(204, 150, 92, 217, 217, 208)).Exists(e => e.Contains("L11")));
        // §9.5: one reserved-token distance from the Narrator's white, not "every channel >= 200"
        Check("L11: the Narrator's white itself is refused", RM_SchemeKernel.Errors(Pal(204, 150, 92, 255, 255, 255)).Exists(e => e.Contains("L11")));
        Check("L11: a cream (255,240,199) that the old all-channels test let through is refused",
              RM_SchemeKernel.Errors(Pal(204, 150, 92, 255, 240, 199)).Exists(e => e.Contains("L11")));
        Check("L11: a cool white (199,230,255) that the old all-channels test let through is refused",
              RM_SchemeKernel.Errors(Pal(204, 150, 92, 199, 230, 255)).Exists(e => e.Contains("L11")));
        Check("L11: a warm bright (255,210,148) lies outside the reserved distance and is admitted",
              !RM_SchemeKernel.Errors(Pal(204, 150, 92, 255, 210, 148)).Exists(e => e.Contains("L11")));
        Check("L11: the reserved token is pure white at a distance of 100 (provisional)",
              RM_SchemeKernel.NarratorWhiteR == 255 && RM_SchemeKernel.NarratorWhiteG == 255 && RM_SchemeKernel.NarratorWhiteB == 255
              && RM_SchemeKernel.ReservedWhiteDistance == 100 && RM_SchemeKernel.NearNarratorWhite(198, 198, 198)
              && !RM_SchemeKernel.NearNarratorWhite(197, 197, 197));
        Check("L8: full black without mayGoDark is refused", RM_SchemeKernel.Errors(Pal(204, 150, 92, 0, 0, 0)).Exists(e => e.Contains("mayGoDark")));
        var dark = Pal(204, 150, 92, 0, 0, 0); dark.mayGoDark = true;
        Check("L8: full black WITH mayGoDark and motion is allowed", RM_SchemeKernel.Errors(dark).Count == 0, string.Join("; ", RM_SchemeKernel.Errors(dark)));
        dark.pattern = RM_PatternKind.Steady;
        Check("L8: a Steady (motionless) scheme may not hold full black", RM_SchemeKernel.Errors(dark).Exists(e => e.Contains("L8")));
        Check("L4: more than MaxPalette entries is refused", RM_SchemeKernel.Errors(Pal(1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9)).Exists(e => e.Contains("L4")));
        Check("a repeated entry is refused", RM_SchemeKernel.Errors(Pal(10, 20, 30, 10, 20, 30)).Exists(e => e.Contains("repeats")));
        var fl = ok; fl.flasherCount = 2;
        Check("L7: flashers without a flasher period are refused", RM_SchemeKernel.Errors(fl).Exists(e => e.Contains("flasherPeriodSeconds")));
        Check("an empty palette is refused", RM_SchemeKernel.Errors(new RM_SchemeData()).Count > 0);

        // ---- L4: the pattern only ever points into the palette, at any time, for any emitter, any kind
        bool inRange = true; int visited = 0;
        var kinds = new[] { RM_PatternKind.Steady, RM_PatternKind.RoomBreath, RM_PatternKind.Sparks };
        var rng = new Random(7);
        foreach (RM_PatternKind k in kinds)
        {
            var s = ok; s.pattern = k; s.flasherPeriodSeconds = 0.7f;
            for (int i = 0; i < 20000; i++)
            {
                int idx = RM_SchemeKernel.PaletteIndex(s, rng.Next(), rng.Next(-1, 500), rng.NextDouble() * 1e6, i % 5 == 0);
                if (idx < 0 || idx >= s.Count) inRange = false;
                visited |= 1 << idx;
            }
        }
        Check("L4: 60,000 pattern samples (all kinds, flashers too) are all valid palette indices", inRange);
        Check("the pattern visits every palette entry (it is not stuck)", visited == 0b111, Convert.ToString(visited, 2));

        // ---- RoomBreath: a room steps only between neighbours (no jump across the palette), and rooms are out of phase
        bool smooth = true; int prev = RM_SchemeKernel.PaletteIndex(ok, 1, 42, 0, false), changes = 0;
        for (double t = 0.25; t < 600; t += 0.25)
        {
            int idx = RM_SchemeKernel.PaletteIndex(ok, 1, 42, t, false);
            if (Math.Abs(idx - prev) > 1) smooth = false;
            if (idx != prev) changes++;
            prev = idx;
        }
        Check("RoomBreath steps one level at a time (Tallow-Lamp-Hearth-Lamp)", smooth);
        Check("RoomBreath: 5 cycles of a 120 s scheme change a room's index 19-21 times (4 per cycle)", changes >= 19 && changes <= 21, "got " + changes);
        int differ = 0;
        for (int room = 0; room < 40; room++)
            if (RM_SchemeKernel.PaletteIndex(ok, 1, room, 500, false) != RM_SchemeKernel.PaletteIndex(ok, 1, room + 1, 500, false)) differ++;
        Check("RoomBreath: neighbouring rooms are on their own phase (some differ at one instant)", differ > 5, "differ=" + differ);
        Check("RoomBreath: the emitter does not matter, only its room", RM_SchemeKernel.PaletteIndex(ok, 1, 9, 77, false) == RM_SchemeKernel.PaletteIndex(ok, 99999, 9, 77, false));

        // ---- Sparks: rests at [0] most of the time, rises and falls when it sparks
        var sp = ok; sp.pattern = RM_PatternKind.Sparks; sp.massPeriodSeconds = 40f; sp.sparkSeconds = 2.5f; sp.sparkOneIn = 2;
        int atRest = 0, samples = 0;
        bool sparked = false;
        for (int e = 0; e < 50; e++)
            for (double t = 0; t < 400; t += 0.5)
            {
                int idx = RM_SchemeKernel.PaletteIndex(sp, e, 0, t, false);
                samples++;
                if (idx == 0) atRest++;
                if (idx == sp.Count - 1) sparked = true;
            }
        Check("Sparks: a fixture rests at the first entry most of the time (>90%)", atRest > samples * 0.9, atRest + "/" + samples);
        Check("Sparks: fixtures do reach the spark entry", sparked);

        // ---- flashers: the framework picks, stably, and exactly the asked count
        var ids = new List<int> { 5, 9, 13, 77, 1001, 4 };
        HashSet<int> f1 = RM_SchemeKernel.PickFlashers(ids, 2);
        ids.Reverse();
        HashSet<int> f2 = RM_SchemeKernel.PickFlashers(ids, 2);
        Check("L7: exactly flasherCount fixtures flash", f1.Count == 2);
        Check("L7: the choice does not depend on list order", f1.SetEquals(f2));
        Check("L7: zero flashers when the scheme asks none", RM_SchemeKernel.PickFlashers(ids, 0).Count == 0);

        // ---- default groups
        Check("no room -> exterior", RM_SchemeKernel.PlaceOf(false, false, null) == RM_SchemeKernel.RM_Place.Exterior);
        Check("an outdoors room -> exterior", RM_SchemeKernel.PlaceOf(true, true, "Bedroom") == RM_SchemeKernel.RM_Place.Exterior);
        Check("a role-less indoor room (vanilla corridor) -> hall", RM_SchemeKernel.PlaceOf(true, false, "Room") == RM_SchemeKernel.RM_Place.Hall
              && RM_SchemeKernel.PlaceOf(true, false, "None") == RM_SchemeKernel.RM_Place.Hall);
        Check("a bedroom -> room", RM_SchemeKernel.PlaceOf(true, false, "Bedroom") == RM_SchemeKernel.RM_Place.Room);
        Check("'ship' holds every place; 'rooms' only rooms", RM_SchemeKernel.InDefaultGroup("ship", RM_SchemeKernel.RM_Place.Exterior)
              && !RM_SchemeKernel.InDefaultGroup("rooms", RM_SchemeKernel.RM_Place.Hall) && !RM_SchemeKernel.InDefaultGroup("nosuch", RM_SchemeKernel.RM_Place.Room));

        // ---- §2.6 step 6: changed-only. 200 fixtures in 40 rooms, 10 evaluations a second for 10 minutes.
        var tr = new RM_ChangeTracker();
        long evals = 0, writes = 0, transitions = 0;
        var lastIdx = new Dictionary<int, int>();
        for (int step = 0; step < 6000; step++)
        {
            double t = step * 0.1;
            for (int e = 0; e < 200; e++)
            {
                int idx = RM_SchemeKernel.PaletteIndex(ok, e, e % 40, t, false);
                evals++;
                if (tr.Want(e, RM_ChangeTracker.Pack(1, idx))) writes++;
                if (!lastIdx.TryGetValue(e, out int li) || li != idx) { transitions++; lastIdx[e] = idx; }
            }
        }
        Check("changed-only: writes == index changes exactly (" + writes + " of " + evals + " evaluations)", writes == transitions);
        Check("changed-only: under 0.5% of evaluations write", writes * 200 < evals, writes + "/" + evals);
        Check("changed-only: re-asking the value just written writes nothing", !tr.Want(3, tr.Shows(3, out long cur3) ? cur3 : 0));
        Check("a scheme change rewrites (same index, different scheme)", tr.Want(3, RM_ChangeTracker.Pack(2, (int)(cur3 & 0xFF))));
        Check("an emitter never seen is written once even for the substrate (a reload leaves the driven colour)",
              tr.Want(123456, RM_ChangeTracker.Substrate) && !tr.Want(123456, RM_ChangeTracker.Substrate));

        // ---- the SHIPPED schemes
        string xml = FindUp(System.IO.Path.Combine("src", "RimMandrake", "AtmosphericBase", "Defs", "RM_AtmosphericSchemes.xml"))
                  ?? FindUp(System.IO.Path.Combine("Defs", "RM_AtmosphericSchemes.xml"));
        Check("the shipped scheme file is found from the selftest exe", xml != null);
        if (xml == null) return;
        List<KeyValuePair<string, RM_SchemeData>> shipped = ShippedSchemes(xml);
        Check("the shipped file holds Lamplight (the default) and Fireflies", shipped.Exists(p => p.Key == "RM_Scheme_Lamplight") && shipped.Exists(p => p.Key == "RM_Scheme_Fireflies"));
        // §9.3: the default palette is WIDER than the old (204,150,92)-(244,188,118) lamplight range, both ways
        RM_SchemeData lamp = shipped.Find(p => p.Key == "RM_Scheme_Lamplight").Value;
        int lo = int.MaxValue, hi = 0;
        for (int i = 0; i < lamp.Count; i++) { int m = Math.Max(lamp.r[i], Math.Max(lamp.g[i], lamp.b[i])); lo = Math.Min(lo, m); hi = Math.Max(hi, m); }
        Check("default Lamplight reaches deeper than the old low end (max channel < 204)", lo < 204, "lowest max channel = " + lo);
        Check("default Lamplight reaches brighter than the old high end (max channel > 244)", hi > 244, "highest max channel = " + hi);
        foreach (var p in shipped)
        {
            List<string> errs = RM_SchemeKernel.Errors(p.Value);
            Check("shipped " + p.Key + " validates clean", errs.Count == 0, string.Join("; ", errs));
            int minMax = int.MaxValue;
            for (int i = 0; i < p.Value.Count; i++) minMax = Math.Min(minMax, Math.Max(p.Value.r[i], Math.Max(p.Value.g[i], p.Value.b[i])));
            Check("shipped " + p.Key + ": every entry keeps a working-light max channel (>= 176)", minMax >= 176, "min of max channels = " + minMax);
            bool warm = true;
            for (int i = 0; i < p.Value.Count; i++) warm &= p.Value.r[i] >= p.Value.g[i] && p.Value.g[i] >= p.Value.b[i];
            Check("shipped " + p.Key + ": every entry is warm (r >= g >= b)", warm);
            Check("shipped " + p.Key + " has no flashers (a gentle scheme; L7's fast role is not the default)", p.Value.flasherCount == 0);
        }
    }

    // ================================================================== Phase 3: territory (L5) -- RM_TerritoryKernel
    // REAL: ordering by rank, the wedge allocation, its own clock. NOT covered: the union over game groups and the
    // write loop (ProofTerritory's business).

    private static void Scatter(int n, int seed, List<int> ids, List<float> xs, List<float> zs)
    {
        var rng = new Random(seed);
        for (int i = 0; i < n; i++) { ids.Add(1000 + i * 7 + seed); xs.Add((float)(rng.NextDouble() * 60)); zs.Add((float)(rng.NextDouble() * 25)); }
    }

    private static int Count(bool[] a) { int c = 0; foreach (bool b in a) if (b) c++; return c; }

    private static void Phase3()
    {
        var tun = new RM_TerritoryTuning { periodSeconds = 900f, leadShare = 0.6f, ragged = 0.08f };
        // rank is only ordered: higher first, ties by claimant ordinal, never by push order
        int[] o1 = RM_TerritoryKernel.RankOrder(new float[] { 1f, 5f, 5f, -2f }, new[] { "d", "b", "a", "c" });
        int[] o2 = RM_TerritoryKernel.RankOrder(new float[] { 5f, -2f, 1f, 5f }, new[] { "a", "c", "d", "b" });
        Check("rank order: loudest first, ties by claimant ordinal", o1[0] == 2 && o1[1] == 1 && o1[2] == 0 && o1[3] == 3, string.Join(",", o1));
        Check("rank order does not depend on push order", o2[0] == 0 && o2[1] == 3 && o2[2] == 2 && o2[3] == 1, string.Join(",", o2));

        // exact shares; both claimants always hold ground
        bool shares = true;
        for (int n = 2; n <= 60; n++)
            for (float sh = 0.5f; sh <= 0.8f; sh += 0.05f)
            {
                int k = RM_TerritoryKernel.LeadCount(n, sh);
                if (k < 1 || k > n - 1 || k < Math.Ceiling(n * sh - 1e-6) - 0 && k != n - 1) shares = false;
            }
        Check("lead count = ceil(share * N), and the quieter claimant always keeps at least one fixture", shares
              && RM_TerritoryKernel.LeadCount(11, 0.6f) == 7 && RM_TerritoryKernel.LeadCount(2, 0.8f) == 1 && RM_TerritoryKernel.LeadCount(1, 0.6f) == 1);

        // the irregular 11-fixture canvas: both sides at every step of a turn, share exact, every fixture changes hands
        var ids = new List<int>(); var xs = new List<float>(); var zs = new List<float>();
        Scatter(11, 3, ids, xs, zs);
        int salt = RM_TerritoryKernel.PairSalt("god.a", "god.b");
        bool[] first = RM_TerritoryKernel.Allocate(ids, xs, zs, 0, salt, tun);
        var flipsOf = new int[11];
        bool exact = true; int maxStepFlips = 0, stepsWithChange = 0;
        bool[] prev = first;
        for (long st = 1; st <= RM_TerritoryKernel.StepsPerTurn; st++)
        {
            bool[] a = RM_TerritoryKernel.Allocate(ids, xs, zs, st, salt, tun);
            if (Count(a) != 7) exact = false;
            int f = 0;
            for (int i = 0; i < 11; i++) if (a[i] != prev[i]) { f++; flipsOf[i]++; }
            if (f > 0) stepsWithChange++;
            maxStepFlips = Math.Max(maxStepFlips, f);
            prev = a;
        }
        int minFlips = int.MaxValue; foreach (int f in flipsOf) minFlips = Math.Min(minFlips, f);
        Check("11 irregular fixtures: the louder claimant holds exactly 7 at every step of a turn", exact);
        Check("the boundary moves: every fixture changes hands at least twice per turn (no static heartland)", minFlips >= 2, "min=" + minFlips);
        Check("the boundary moves a little at a time: at most 2 fixtures change per step, and not every step", maxStepFlips <= 2 && stepsWithChange < RM_TerritoryKernel.StepsPerTurn,
              "max=" + maxStepFlips + " changing steps=" + stepsWithChange);
        bool[] same = RM_TerritoryKernel.Allocate(ids, xs, zs, 0, salt, tun);
        bool identical = true; for (int i = 0; i < 11; i++) identical &= same[i] == first[i];
        bool[] quarter = RM_TerritoryKernel.Allocate(ids, xs, zs, RM_TerritoryKernel.StepsPerTurn / 4, salt, tun);
        bool differs = false; for (int i = 0; i < 11; i++) differs |= quarter[i] != first[i];
        Check("same step -> identical allocation; a quarter turn later -> a different one", identical && differs);
        bool[] turned = RM_TerritoryKernel.Allocate(ids, xs, zs, RM_TerritoryKernel.StepsPerTurn, salt, tun);
        bool periodic = true; for (int i = 0; i < 11; i++) periodic &= turned[i] == first[i];
        Check("one full turn returns the boundary where it started", periodic);

        // ragged = 0: the louder claimant's fixtures are exactly contiguous in bearing (a clean wedge)
        var straight = new RM_TerritoryTuning { periodSeconds = 900f, leadShare = 0.6f, ragged = 0f };
        var big = new List<int>(); var bx = new List<float>(); var bz = new List<float>();
        Scatter(200, 11, big, bx, bz);
        int[] ord = RM_TerritoryKernel.BearingOrder(big, bx, bz, 0f);
        bool contiguous = true; int maxBig = 0;
        bool[] pb = RM_TerritoryKernel.Allocate(big, bx, bz, 0, salt, straight);
        for (long st = 0; st < RM_TerritoryKernel.StepsPerTurn; st += 7)
        {
            bool[] a = RM_TerritoryKernel.Allocate(big, bx, bz, st, salt, straight);
            int runs = 0;
            for (int i = 0; i < 200; i++) if (a[ord[i]] && !a[ord[(i + 199) % 200]]) runs++;
            if (runs != 1) contiguous = false;
        }
        for (long st = 1; st <= 40; st++)
        {
            bool[] a = RM_TerritoryKernel.Allocate(big, bx, bz, st, salt, tun);
            int f = 0; for (int i = 0; i < 200; i++) if (a[i] != pb[i]) f++;
            maxBig = Math.Max(maxBig, f); pb = a;
        }
        Check("ragged 0: the louder claimant holds one contiguous wedge in bearing order", contiguous);
        Check("200 fixtures: one clock step changes only the fixtures the fronts crossed (<= 4)", maxBig <= 4, "max=" + maxBig);

        // its own slow clock
        Check("clock: 240 steps per period, floor", RM_TerritoryKernel.ClockStep(899.9, 900f) == 239 && RM_TerritoryKernel.ClockStep(900, 900f) == 240
              && RM_TerritoryKernel.ClockStep(3.74, 900f) == 0 && RM_TerritoryKernel.ClockStep(3.76, 900f) == 1);
        RM_TerritoryTuning c = RM_TerritoryTuning.Clamp(new RM_TerritoryTuning { periodSeconds = 5f, leadShare = 0.99f, ragged = 9f });
        RM_TerritoryTuning cn = RM_TerritoryTuning.Clamp(new RM_TerritoryTuning { periodSeconds = float.NaN, leadShare = float.NaN, ragged = float.NaN });
        Check("tuning clamps: a fast boundary is refused, the quieter claimant keeps a fifth, NaN is harmless",
              c.periodSeconds == RM_TerritoryKernel.MinPeriodSeconds && c.leadShare == RM_TerritoryKernel.MaxLeadShare && c.ragged == RM_TerritoryKernel.MaxRagged
              && cn.periodSeconds == RM_TerritoryKernel.MinPeriodSeconds && cn.leadShare == 0.5f && cn.ragged == 0f);
        Check("pair salt is stable and order-sensitive", RM_TerritoryKernel.PairSalt("a", "b") == RM_TerritoryKernel.PairSalt("a", "b")
              && RM_TerritoryKernel.PairSalt("a", "b") != RM_TerritoryKernel.PairSalt("b", "a"));
        Check("empty and single-fixture unions allocate without error", RM_TerritoryKernel.Allocate(new int[0], new float[0], new float[0], 3, salt, tun).Length == 0
              && RM_TerritoryKernel.Allocate(new[] { 5 }, new[] { 1f }, new[] { 1f }, 3, salt, tun)[0]);
    }

    // ================================================================== Phase 4: tremor (L6) -- RM_TremorKernel
    private static void Phase4()
    {
        var tu = new RM_TremorTuning { cap = 3, slotSeconds = 30f, flickerSeconds = 0.8f, oneIn = 4, maxFraction = 0.04f };
        var srcs = new List<RM_TremorSource>();
        int[] pals = { 3, 2, 4, 3, 2 };
        for (int s = 0; s < 5; s++)
        {
            var m = new List<int>();
            for (int i = 0; i < 300; i++) m.Add(5000 + i);
            srcs.Add(new RM_TremorSource { paletteCount = pals[s], salt = RM_TerritoryKernel.PairSalt("tremor" + s, "tremor"), members = m });
        }
        bool capOk = true, fracOk = true, ownPal = true, everyone = true;
        int seen = 0, maxNow = 0;
        var contrib = new HashSet<int>();
        var flickerLen = new Dictionary<int, double>(); double maxLen = 0; var startAt = new Dictionary<int, double>();
        double dt = 0.1;
        for (double t = 100; t < 400; t += dt)
        {
            Dictionary<int, KeyValuePair<int, int>> a = RM_TremorKernel.Assign(srcs, t, 300, tu);
            if (a.Count > RM_TremorKernel.InstantCap(300, tu.maxFraction)) fracOk = false;
            maxNow = Math.Max(maxNow, a.Count);
            seen += a.Count;
            foreach (KeyValuePair<int, KeyValuePair<int, int>> kv in a)
            {
                if (kv.Value.Key >= 3) capOk = false;
                contrib.Add(kv.Value.Key);
                if (kv.Value.Value < 0 || kv.Value.Value >= pals[kv.Value.Key]) ownPal = false;
            }
        }
        Check("tremor: never more than three contributors though five are given (L6)", capOk && contrib.Count <= 3, "contributors=" + contrib.Count);
        Check("tremor: every flicker is an index into its own contributor's palette", ownPal);
        Check("tremor: at most 4% of 300 driven fixtures flicker at one instant (never reads as territory)", fracOk && maxNow <= 12, "max=" + maxNow);
        Check("tremor is present: flickers happen, from more than one contributor", seen > 0 && contrib.Count >= 2, "seen=" + seen + " contributors=" + contrib.Count);

        // one flicker is brief: a fixture's continuous flicker never outlasts flickerSeconds
        bool brief = true;
        for (int id = 0; id < 400; id++)
        {
            double run = 0;
            for (double t = 0; t < 120; t += 0.05)
            {
                if (RM_TremorKernel.Flickers(id, 77, 3, t, RM_TremorTuning.Clamp(tu), out int ix)) { run += 0.05; if (run > tu.flickerSeconds + 0.051) brief = false; }
                else run = 0;
            }
        }
        Check("tremor: one flicker lasts no longer than flickerSeconds", brief);

        RM_TremorTuning cl = RM_TremorTuning.Clamp(new RM_TremorTuning { cap = 9, slotSeconds = 0.5f, flickerSeconds = 50f, oneIn = 0, maxFraction = 0.9f });
        Check("tremor clamps: cap <= 3, fraction <= 10%, slot >= 4 s, flicker <= a quarter slot and <= 2 s",
              cl.cap == RM_TremorKernel.LawCap && cl.maxFraction == RM_TremorKernel.MaxFraction && cl.slotSeconds == RM_TremorKernel.MinSlotSeconds
              && cl.flickerSeconds <= 1f && cl.oneIn == 1);
        Check("tremor instant cap: at least one fixture, none on an empty ship", RM_TremorKernel.InstantCap(11, 0.04f) == 1
              && RM_TremorKernel.InstantCap(0, 0.04f) == 0 && RM_TremorKernel.InstantCap(300, 0.04f) == 12);
        Check("tremor switched to cap 0 or fraction 0 flickers nothing", RM_TremorKernel.Assign(srcs, 123, 300, new RM_TremorTuning { cap = 0, slotSeconds = 30, flickerSeconds = 0.8f, oneIn = 1, maxFraction = 0.04f }).Count == 0
              && RM_TremorKernel.Assign(srcs, 123, 300, new RM_TremorTuning { cap = 3, slotSeconds = 30, flickerSeconds = 0.8f, oneIn = 1, maxFraction = 0f }).Count == 0);

        // a fixture two contributors want goes to the louder; the choice is stable
        var both = new List<RM_TremorSource> { new RM_TremorSource { paletteCount = 2, salt = 9, members = new[] { 1, 2, 3 } },
                                               new RM_TremorSource { paletteCount = 2, salt = 9, members = new[] { 1, 2, 3 } } };
        bool louder = true;
        var loose = new RM_TremorTuning { cap = 3, slotSeconds = 4, flickerSeconds = 1f, oneIn = 1, maxFraction = 0.1f };
        for (double t = 0; t < 40; t += 0.25)
            foreach (KeyValuePair<int, KeyValuePair<int, int>> kv in RM_TremorKernel.Assign(both, t, 3, loose))
                if (kv.Value.Key != 0) louder = false;
        Check("tremor: a fixture two contributors want goes to the louder", louder);

        // territory + tremor union: every driven fixture shows exactly one palette (the walk's step 3)
        var ids = new List<int>(); var xs = new List<float>(); var zs = new List<float>();
        Scatter(11, 5, ids, xs, zs);
        var tun = new RM_TerritoryTuning { periodSeconds = 900f, leadShare = 0.6f, ragged = 0.08f };
        bool exactlyOne = true;
        var tsrc = new List<RM_TremorSource> { new RM_TremorSource { paletteCount = 3, salt = 4, members = ids } };
        for (double t = 0; t < 900; t += 1.7)
        {
            bool[] lead = RM_TerritoryKernel.Allocate(ids, xs, zs, RM_TerritoryKernel.ClockStep(t, 900f), 31, tun);
            Dictionary<int, KeyValuePair<int, int>> tr = RM_TremorKernel.Assign(tsrc, t, 11, tu);
            if (tr.Count > 1) exactlyOne = false;
            int a = 0, b = 0;
            for (int i = 0; i < 11; i++) { if (tr.ContainsKey(ids[i])) continue; if (lead[i]) a++; else b++; }
            if (a + b + tr.Count != 11 || a == 0 || b == 0) exactlyOne = false;
        }
        Check("11 fixtures, two territory moods and a tremor: each fixture one palette, both presences always hold ground, one flicker at most", exactlyOne);
    }

    private static int Main()
    {
        // ---- the kernel
        Check("a player-owned spawned building with a glower is Eligible", RM_AtmosphericKernel.Classify(Lamp()) == RM_EmitterVerdict.Eligible);
        var f = Lamp(); f.isPawn = true;
        Check("a glowing pawn (animal) is ExcludedPawn even with every capability", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedPawn);
        f = Lamp(); f.isPlant = true;
        Check("a glowing plant is ExcludedPlant", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedPlant);
        f = Lamp(); f.isApparelOrEquipment = true;
        Check("worn gear / equipment is ExcludedWornOrEquipment", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedWornOrEquipment);
        f = Lamp(); f.hologramMarked = true;
        Check("a def marked RM_AtmosphericExcluded is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.defName = "RUT_GodHologram";
        Check("a defName naming a hologram is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.thingClassName = "Building_HoloEmitter";
        Check("a thingClass naming a holo emitter is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.defName = "HollowWallLamp";
        Check("'Hollow' is not 'holo' (no false hologram)", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.Eligible);
        f = Lamp(); f.hasGlower = false;
        Check("no glower: NoGlower", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NoGlower);
        f = Lamp(); f.isBuilding = false;
        Check("a glowing item on the floor: NotABuilding", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotABuilding);
        f = Lamp(); f.playerOwned = false;
        Check("someone else's lamp: NotPlayerOwned", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotPlayerOwned);
        f = Lamp(); f.spawned = false;
        Check("a minified lamp: NotSpawned", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotSpawned);
        int hard = 0;
        foreach (RM_EmitterVerdict v in Enum.GetValues(typeof(RM_EmitterVerdict)))
            if (RM_AtmosphericKernel.IsHardExclusion(v)) hard++;
        Check("exactly four hard exclusions (animal, gear, plant, hologram)", hard == 4, "got " + hard);

        // ---- glow access against the real CompGlower
        Check("the three CompGlower members resolve against the shipped Assembly-CSharp", RM_GlowAccess.Bound);
        if (!RM_GlowAccess.Bound)
        {
            Console.WriteLine("\nCompGlower changed shape; restore cannot be tested");
            return 1;
        }
        // SetGlowColorInternal cannot run in this process (see RM_GlowAccess.ColorWriterForSelfTest); the field-only
        // writer stands in for it, so what is proven here is the snapshot/restore logic over the REAL fields.
        RM_GlowAccess.ColorWriterForSelfTest = RM_GlowAccess.WriteColorFieldOnly;
        var props = new ColorInt(214, 148, 94, 0);   // the vanilla StandingLamp (Core Buildings_Furniture.xml)
        var drive = new ColorInt(23, 201, 117, 0);

        CompGlower g = Glower(props, 12f);
        RM_GlowSnapshot before = RM_GlowAccess.Snapshot(g);
        Check("a stock lamp has no colour override", !before.hadColor, before.ToString());
        RM_GlowAccess.WriteColor(g, drive);
        Check("driving writes the override the game reads", g.GlowColor == drive && g.HasGlowColorOverride);
        RM_GlowAccess.Restore(g, before);
        Check("release on a stock lamp leaves NO override (not the effective value)", !g.HasGlowColorOverride && RM_GlowAccess.Snapshot(g).SameAs(before),
              RM_GlowAccess.Snapshot(g).ToString());
        Check("release on a stock lamp: effective colour is the def's again, radius never touched", g.GlowColor == props && g.GlowRadius == 12f);

        CompGlower p = Glower(props, 12f);
        var picked = new ColorInt(180, 40, 40, 0);
        RM_GlowAccess.WriteColor(p, picked);   // the player's colour picker
        RM_GlowSnapshot pBefore = RM_GlowAccess.Snapshot(p);
        RM_GlowAccess.WriteColor(p, drive);
        RM_GlowAccess.Restore(p, pBefore);
        Check("release keeps the player's picked colour; radius never touched", p.GlowColor == picked && p.GlowRadius == 12f
              && RM_GlowAccess.Snapshot(p).SameAs(pBefore), RM_GlowAccess.Snapshot(p).ToString());

        // The defect the snapshot exists to catch: restoring the EFFECTIVE value instead of the override.
        CompGlower e = Glower(props, 12f);
        RM_GlowSnapshot eBefore = RM_GlowAccess.Snapshot(e);
        RM_GlowAccess.WriteColor(e, e.GlowColor);
        Check("an explicit override equal to the def colour is NOT the same state as no override",
              !RM_GlowAccess.Snapshot(e).SameAs(eBefore));

        var a = new RM_GlowSnapshot { hadColor = true, color = drive };
        var b = new RM_GlowSnapshot { hadColor = true, color = picked };
        Check("snapshots with different colours differ", !a.SameAs(b));

        // ---- §9.9: an external colour edit releases the lamp and keeps the edit; aboard the Utinni it displeases gods
        CompGlower x = Glower(props, 12f);
        RM_GlowSnapshot left = RM_GlowAccess.Snapshot(x).Copy();          // take-over: lastLeft = prior
        Check("a lamp just handed over is not edited", !RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(x), left));
        RM_GlowAccess.WriteColor(x, drive); left = RM_GlowSnapshot.Of(drive);   // the framework drives it
        Check("the framework's own write is not an edit", !RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(x), left));
        RM_GlowAccess.WriteColor(x, picked);                              // another mod / the colour picker
        Check("another writer's colour on a held lamp is an edit", RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(x), left));
        RM_GlowAccess.WriteColor(x, null);
        Check("another writer CLEARING the override is an edit too", RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(x), left));
        Check("a save from before the rule (nothing known left) is never read as an edit",
              !RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(x), null));
        Check("an external edit releases the lamp", RM_HeldLampPolicy.Releases(RM_HeldLampEvent.ColourEditedExternally));
        Check("aboard the Utinni an external edit displeases the gods", RM_HeldLampPolicy.DispleasesGods(RM_HeldLampEvent.ColourEditedExternally, true));
        Check("off the Utinni an external edit is silent", !RM_HeldLampPolicy.DispleasesGods(RM_HeldLampEvent.ColourEditedExternally, false));
        // §9.6 / L17: a lamp switched off by hand is silent, everywhere, and stays held
        Check("L17: a hand switch-off never displeases the gods, aboard the Utinni or not",
              !RM_HeldLampPolicy.DispleasesGods(RM_HeldLampEvent.SwitchedOffByHand, true) && !RM_HeldLampPolicy.DispleasesGods(RM_HeldLampEvent.SwitchedOffByHand, false));
        Check("L17: a hand switch-off does not release the lamp", !RM_HeldLampPolicy.Releases(RM_HeldLampEvent.SwitchedOffByHand));

        Phase2();
        Phase3();
        Phase4();
        PatternTests.Run();

        if (Fails.Count > 0)
        {
            Console.WriteLine("\n" + Fails.Count + " AtmosphericBase kernel selftest(s) FAILED");
            return 1;
        }
        Console.WriteLine("\nall AtmosphericBase kernel selftests passed");
        return 0;
    }
}
