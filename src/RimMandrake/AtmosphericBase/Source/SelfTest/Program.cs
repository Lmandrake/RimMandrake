// Selftest for mandrake.rm.atmosphericbase (ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 1-2).
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
    private static readonly List<string> Fails = new List<string>();

    private static void Check(string name, bool ok, string detail = "")
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

    private static string FindUp(string rel)
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
        foreach (var p in shipped)
        {
            List<string> errs = RM_SchemeKernel.Errors(p.Value);
            Check("shipped " + p.Key + " validates clean", errs.Count == 0, string.Join("; ", errs));
            int minMax = int.MaxValue;
            for (int i = 0; i < p.Value.Count; i++) minMax = Math.Min(minMax, Math.Max(p.Value.r[i], Math.Max(p.Value.g[i], p.Value.b[i])));
            Check("shipped " + p.Key + ": every entry keeps a working-light max channel (>= 200)", minMax >= 200, "min of max channels = " + minMax);
            Check("shipped " + p.Key + " has no flashers (a gentle scheme; L7's fast role is not the default)", p.Value.flasherCount == 0);
        }
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
        var props = new ColorInt(217, 217, 208, 0);
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

        Phase2();

        if (Fails.Count > 0)
        {
            Console.WriteLine("\n" + Fails.Count + " AtmosphericBase kernel selftest(s) FAILED");
            return 1;
        }
        Console.WriteLine("\nall AtmosphericBase kernel selftests passed");
        return 0;
    }
}
