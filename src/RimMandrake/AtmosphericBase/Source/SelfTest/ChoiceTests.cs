// Selftest for the player's pattern choice off the Utinni (Kernel/RM_PatternChoice.cs), kernel only.
// REAL, compiled from production source. NOT covered: the settings screen and the compositor reading the choice
// (Verse); the XML neutral set's palettes are held by proof_atmosphere.py D11 against the same floor.
using System;
using RimMandrake.AtmosphericBase;

internal static class ChoiceTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    private static RM_SchemeData Pal(params int[] rgb)
    {
        int n = rgb.Length / 3;
        var s = new RM_SchemeData { r = new int[n], g = new int[n], b = new int[n], pattern = RM_PatternKind.RoomBreath, massPeriodSeconds = 60f };
        for (int i = 0; i < n; i++) { s.r[i] = rgb[3 * i]; s.g[i] = rgb[3 * i + 1]; s.b[i] = rgb[3 * i + 2]; }
        return s;
    }

    private static int Changes(RM_SchemeData s, int tempo, double span, double dt)
    {
        int c = 0, last = -1;
        for (double t = 0; t <= span; t += dt)
        {
            int i = RM_SchemeKernel.PaletteIndex(s, 7, 3, RM_PatternChoice.TempoTime(t, tempo), false);
            if (last >= 0 && i != last) c++;
            last = i;
        }
        return c;
    }

    internal static void Run()
    {
        // the shipped default is the shipped default
        Check("choice: pattern set 0 is Lamplight and an out-of-range pick falls back to it",
              RM_PatternChoice.NeutralScheme(0) == "RM_Scheme_Lamplight" && RM_PatternChoice.NeutralScheme(-1) == "RM_Scheme_Lamplight"
              && RM_PatternChoice.NeutralScheme(99) == "RM_Scheme_Lamplight" && RM_PatternChoice.NeutralSchemes.Length >= 4);
        bool distinct = true;
        for (int i = 0; i < RM_PatternChoice.NeutralSchemes.Length; i++)
            for (int j = 0; j < i; j++) distinct &= RM_PatternChoice.NeutralSchemes[i] != RM_PatternChoice.NeutralSchemes[j];
        Check("choice: the neutral set names no scheme twice", distinct);

        // tempo
        Check("tempo: Slow x1.5, Shipped x1, Lively x0.67, anything else x1",
              RM_PatternChoice.TempoFactor(0) == 1.5 && RM_PatternChoice.TempoFactor(1) == 1.0 && RM_PatternChoice.TempoFactor(2) == 0.67
              && RM_PatternChoice.TempoFactor(7) == 1.0 && RM_PatternChoice.TempoFactor(-1) == 1.0);
        RM_SchemeData lamp = Pal(182, 118, 62, 220, 158, 96, 255, 210, 148);
        bool same = true;
        for (double t = 0; t < 400; t += 0.37)
            same &= RM_SchemeKernel.PaletteIndex(lamp, 7, 3, RM_PatternChoice.TempoTime(t * 1.5, 0), false)
                    == RM_SchemeKernel.PaletteIndex(lamp, 7, 3, t, false);
        Check("tempo: Slow at 1.5 t shows what Shipped shows at t (periods stretched, nothing else)", same);
        int cs = Changes(lamp, 0, 1800, 0.25), c1 = Changes(lamp, 1, 1800, 0.25), cl = Changes(lamp, 2, 1800, 0.25);
        Check("tempo: over 30 min Slow changes least and Lively most", cs < c1 && c1 < cl && c1 > 0, "slow " + cs + " shipped " + c1 + " lively " + cl);
        Check("tempo: Shipped is the clock itself", RM_PatternChoice.TempoTime(123.5, 1) == 123.5);

        // intensity
        bool lampSame = true;
        for (int i = 0; i < lamp.Count; i++) lampSame &= RM_PatternChoice.Apply(lamp, i, 0) == i;
        Check("intensity: Gentle leaves Lamplight exactly as shipped", lampSame);
        RM_SchemeData four = Pal(148, 94, 48, 190, 126, 68, 228, 166, 102, 255, 214, 152);
        RM_PatternChoice.GentleRange(four, out int lo4, out int hi4);
        Check("intensity: Gentle plays a four-entry neutral palette's inner two (no dim floor entry, no flare)",
              lo4 == 1 && hi4 == 2 && RM_PatternChoice.Apply(four, 0, 0) == 1 && RM_PatternChoice.Apply(four, 3, 0) == 2
              && RM_PatternChoice.Apply(four, 2, 0) == 2, "range " + lo4 + "~" + hi4);
        bool full = true;
        for (int i = 0; i < four.Count; i++) full &= RM_PatternChoice.Apply(four, i, 1) == i;
        Check("intensity: Full is as authored", full);
        RM_SchemeData dark = Pal(0, 0, 0, 90, 20, 10, 200, 60, 30, 255, 120, 60);
        dark.mayGoDark = true;
        bool neverBlack = true;
        for (int i = 0; i < dark.Count; i++) { int k = RM_PatternChoice.Apply(dark, i, 0); neverBlack &= dark.r[k] + dark.g[k] + dark.b[k] > 0 && Math.Max(dark.r[k], Math.Max(dark.g[k], dark.b[k])) >= RM_PatternChoice.WorkingFloor; }
        Check("intensity: Gentle keeps a working-light floor on a dark palette (never black), Full reaches black",
              neverBlack && RM_PatternChoice.Apply(dark, 0, 1) == 0);
        RM_SchemeData dim = Pal(40, 20, 10, 120, 60, 30, 90, 50, 20);
        RM_PatternChoice.GentleRange(dim, out int lod, out int hid);
        Check("intensity: a palette with no working light holds its brightest entry under Gentle", lod == 1 && hid == 1);
        RM_SchemeData one = Pal(200, 150, 90);
        Check("intensity: a one-entry palette is untouched", RM_PatternChoice.Apply(one, 0, 0) == 0);
        Check("intensity: Gentle shows only working light on the neutral palettes",
              RM_PatternChoice.GentleIsWorking(lamp) && RM_PatternChoice.GentleIsWorking(four) && !RM_PatternChoice.GentleIsWorking(dim));
    }
}
