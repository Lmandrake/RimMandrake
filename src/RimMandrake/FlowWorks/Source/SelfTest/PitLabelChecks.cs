// RIMMANDRAKE_LABEL_PIT_DEPTH_EXACT_ONE_WORD (owner 2026-11-12, live look: "Why is there a label of "Canal 1m" at the central
// northern wall of the pit and "Pit 2m or more" elsewhere? It's supposed to show the precise depth no matter what, and Pit and
// Canal are totally interchangeable."). The cause: a dug square was named by one of four per-depth-band TerrainDefs
// (RM_Channel_Empty/Mid/Deep "canal (0.5/1/1.5 m)", RM_Channel_Superdeep "pit (2 m or more)" for every depth from 2 m to
// 125 m), and the cell readout printed that label. The fix names a dug square from the true depth grid (RM_Volume.PitLabel,
// via RM_MapComponent_Excavation.PitLabelAt and the mouseover prefix) and strips the band from every shipped label.
// Arithmetic is the PRODUCTION Verse-free RM_Volume; the wiring and the wording are read from production source and Defs.
// What this cannot see: the label drawn on a live map (the item's live row).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitLabelChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string FlowWorksDir()
        {
            return Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("FluidDef.cs")));
        }

        /// <summary>Why a piece of player text breaks the ruling, or null: a depth band ("or more", "about 1 m",
        /// "under 0.75 m") or the word "canal" for a dug square.</summary>
        internal static string Offence(string text)
        {
            if (text == null) return null;
            if (Regex.IsMatch(text, @"\bor more\b", RegexOptions.IgnoreCase)) return "a depth band ('or more')";
            if (Regex.IsMatch(text, @"\((about|under) [0-9.]+ ?m\)", RegexOptions.IgnoreCase)) return "a depth band ('about/under N m')";
            if (Regex.IsMatch(text, @"\bcanals?\b", RegexOptions.IgnoreCase)) return "the word 'canal'";
            return null;
        }

        private static string M(double metres) => metres.ToString("0.0", CultureInfo.InvariantCulture) + " m";

        /// <summary>Every label/description/report/gerund/keyed text a player reads in FlowWorks' Defs and English keys
        /// (comments stripped), with where it came from.</summary>
        private static IEnumerable<(string where, string text)> ShippedTexts()
        {
            string root = FlowWorksDir();
            var files = Directory.GetFiles(Path.Combine(root, "Defs"), "*.xml", SearchOption.AllDirectories)
                .Concat(Directory.GetFiles(Path.Combine(root, "Languages", "English"), "*.xml", SearchOption.AllDirectories));
            string[] read = { "label", "description", "reportString", "gerund", "verb", "labelShort", "jobString" };
            foreach (string f in files)
            {
                XDocument doc = XDocument.Load(f);
                bool keyed = f.Contains(Path.DirectorySeparatorChar + "Keyed" + Path.DirectorySeparatorChar);
                foreach (XElement e in doc.Descendants())
                {
                    if (e.HasElements) continue;
                    if (keyed || read.Contains(e.Name.LocalName))
                    {
                        yield return (Path.GetFileName(f) + " <" + e.Name.LocalName + ">", e.Value);
                    }
                }
            }
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitLabel_dry_every_half_metre_to_the_deepest_hole", () =>
            {
                Assert(RM_Volume.MetresPerNotch == 0.5f, "a notch is half a metre");
                for (int n = 1; n <= RM_BedMath.MaxStorableDepth; n++)
                {
                    string got = RM_Volume.PitLabel(n, 0.0, null);
                    string want = "Pit, " + M(n * 0.5) + " deep";
                    Assert(got == want, n + " notches: '" + got + "' != '" + want + "'");
                    Assert(Offence(got) == null, n + " notches: " + Offence(got));
                }
                Assert(RM_Volume.PitLabel(0, 0.0, null) == null, "an undug square has no pit label");
            });

            Case("PitLabel_wet_names_exact_liquid_depth_and_kind_in_exact_hole", () =>
            {
                double perNotch = RM_Volume.UnitsPerLevel;
                for (int n = 1; n <= RM_BedMath.MaxStorableDepth; n++)
                {
                    foreach (int w in new[] { 1, n })
                    {
                        string got = RM_Volume.PitLabel(n, w * perNotch, "water");
                        string want = "Pit, " + M(w * 0.5) + " water in " + M(n * 0.5);
                        Assert(got == want, n + "/" + w + ": '" + got + "' != '" + want + "'");
                    }
                }
                Assert(RM_Volume.PitLabel(8, 3 * perNotch, "chemfuel") == "Pit, 1.5 m chemfuel in 4.0 m", "the brief's example");
                Assert(RM_Volume.PitLabel(8, perNotch * 0.04, "water") == "Pit, 0.02 m water in 4.0 m",
                    "a thin film reads in centimetres, never 0.0 m: " + RM_Volume.PitLabel(8, perNotch * 0.04, "water"));
                Assert(RM_Volume.PitLabel(4, 3 * perNotch, null) == "Pit, 1.5 m liquid in 2.0 m", "an unknown liquid still reads");
            });

            Case("PitLabel_notch_cell_reads_its_own_depth_not_a_band", () =>
            {
                // The owner's cell: the 1 m notch at the middle of a 4 m pit's north wall read "Canal 1m" while the floor
                // read "Pit 2m or more". Both are dug squares; both name "Pit" and their own exact depth.
                Assert(RM_Volume.PitLabel(2, 0.0, null) == "Pit, 1.0 m deep", "the 1 m notch: " + RM_Volume.PitLabel(2, 0.0, null));
                Assert(RM_Volume.PitLabel(8, 0.0, null) == "Pit, 4.0 m deep", "the 4 m floor");
                Assert(RM_Volume.PitLabel(1, 0.0, null) == "Pit, 0.5 m deep" && RM_Volume.PitLabel(3, 0.0, null) == "Pit, 1.5 m deep",
                    "the ramp steps between read their own half-metres");
                Assert(RM_Volume.PitLabel(2, perNotchOf(1), "water") == "Pit, 0.5 m water in 1.0 m", "a wet notch");
            });

            Case("PitLabel_the_label_comes_from_the_true_depth_grid_and_the_prefix_prints_it", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Match m = Regex.Match(ex, @"public string PitLabelAt\(IntVec3 c\) \{(.*?)return RM_Volume\.PitLabel\(hole, water, kind\);");
                Assert(m.Success, "RM_MapComponent_Excavation.PitLabelAt(IntVec3) returns RM_Volume.PitLabel(hole, water, kind)");
                Assert(m.Groups[1].Value.Contains("int hole = depthGrid[i];") && m.Groups[1].Value.Contains("double water = WaterDl(i);"),
                    "PitLabelAt reads the hole from depthGrid and the liquid from WaterDl, the source RM_SubmergeDraw/RM_UnderLiquid read");
                string mo = RiverSwitchFlipChecks.Src("RM_MouseoverDepth.cs");
                Assert(mo.Contains("?.PitLabelAt(c)"), "the mouseover prefix asks PitLabelAt for the square");
                Assert(mo.Contains("string label = pit ??"), "the pit label replaces the terrain label on a dug square");
                Assert(Regex.IsMatch(mo, @"if \(suffix == null && pit == null\)"), "a dug square is labelled even with the depth readout setting off");
            });

            Case("PitLabel_shipped_text_has_no_band_and_no_canal", () =>
            {
                var bad = ShippedTexts().Select(t => (t.where, t.text, why: Offence(t.text))).Where(t => t.why != null).ToList();
                Assert(bad.Count == 0, bad.Count + " shipped text(s) break the ruling, first: " +
                    string.Join(" | ", bad.Take(4).Select(b => b.where + " " + b.why + ": " + b.text.Substring(0, Math.Min(80, b.text.Length)))));
                var dug = ShippedTexts().Count(t => t.where.StartsWith("FlowWorks_Terrain.xml <label>") && t.text == "pit");
                Assert(dug >= 4, "the four dug-depth terrains are all labelled 'pit' (" + dug + ")");
                foreach ((string file, string lit) in new[] { ("Designator_DigCanal.cs", "\"Dig pit\""), ("Designator_FillInCanal.cs", "\"Fill in pit\"") })
                {
                    Assert(RiverSwitchFlipChecks.Src(file).Contains(lit), file + " shows " + lit);
                }
            });

            Case("PitLabel_mutant_planted_or_more_is_refused", () =>
            {
                // The checker must see what it guards: each planted string is one the owner saw, or one the old Defs held.
                foreach (string planted in new[] { "pit (2 m or more)", "Pit, 2 m or more", "Canal 1m", "canal (1 m)",
                                                   "deep water (2 m or more)", "shallow tar (about 1 m)", "knee-deep oil (under 0.75 m)" })
                {
                    Assert(Offence(planted) != null, "the checker passed a planted '" + planted + "'");
                }
                Assert(Offence("Pit, 2.5 m deep") == null && Offence("Pit, 1.5 m water in 4.0 m") == null, "the checker passes the ruled wording");
            });
        }

        private static double perNotchOf(int notches) => notches * (double)RM_Volume.UnitsPerLevel;
    }
}
