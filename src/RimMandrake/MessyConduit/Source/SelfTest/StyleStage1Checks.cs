// Per-build style, stage 1 (design/RimMandrake/messyconduit_style_per_build_design.md, architecture B, poles alone):
// the Verse-free rules in ../Aerial/AerialStyles.cs and the per-look geometry lookups over the PRODUCTION tables
// (../Aerial/PoleGeometryTable.cs, ../Aerial/BracketGeometryTable.cs). Each property has a can-fail beside it.
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Aerial;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class StyleStage1Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "style1: " + msg);

        public static void Run()
        {
            Naming();
            Geometry();
            Spans();
            Picker();
        }

        private static void Naming()
        {
            var names = new HashSet<string>();
            bool round = true;
            foreach (string d in AerialStyles.StyledDefs)
                foreach (string l in AerialStyles.Looks)
                {
                    string n = AerialStyles.StyleDefName(d, l);
                    names.Add(n);
                    round &= AerialStyles.LookOfStyleDefName(n) == l;
                }
            Check(names.Count == 12 && round && AerialStyles.Looks.SequenceEqual(new[] { "Scrapper", "Industrial", "Modern", "Futuristic" }),
                  $"naming: 3 anchors x 4 looks = {names.Count} distinct style defs, each parses back to its look; menu order Scrapper/Industrial/Modern/Futuristic");
            Check(AerialStyles.LookOfStyleDefName("RM_AerialMast_Gold") == null && AerialStyles.LookOfStyleDefName("PowerConduit_Modern") == null
                  && AerialStyles.LookOfStyleDefName(null) == null && AerialStyles.LookOfStyleDefName("Modern") == null,
                  "can fail: a non-look suffix, a def that is not ours, null and a bare look all read as no look");
        }

        private static void Geometry()
        {
            Dictionary<string, UnityEngine.Vector2> pole = PoleGeometryTable.Build();
            Dictionary<string, UnityEngine.Vector2[]> ins = PoleGeometryTable.Insulators();
            Dictionary<string, P2> br = BracketGeometryTable.Build();
            var bad = new List<string>();
            var attach = new HashSet<float>();
            foreach (string l in AerialStyles.Looks)
            {
                foreach (string d in new[] { "RM_AerialMast", "RM_AerialLampMast" })
                {
                    if (!AerialStyles.TryLookup(pole, l, d, out UnityEngine.Vector2 g) || g.x < 2.5f || g.x > 3.6f) bad.Add("pole " + l + "/" + d);
                    else attach.Add(g.x);
                    if (!AerialStyles.TryLookup(ins, l, d, out UnityEngine.Vector2[] xs) || xs.Length != 3) bad.Add("insulators " + l + "/" + d);
                }
                foreach (string r in new[] { "North", "East", "South", "West" })
                    if (!AerialStyles.TryLookup(br, l, r, out P2 _)) bad.Add("bracket " + l + "/" + r);
            }
            Check(bad.Count == 0 && attach.Count >= 3, $"geometry: every look has its own mast + lamp-mast row (3 insulators) and 4 bracket facings; {attach.Count} distinct insulator heights" +
                  (bad.Count > 0 ? ": missing " + string.Join(", ", bad) : ""));
            Check(!AerialStyles.TryLookup(pole, "Gold", "RM_AerialMast", out UnityEngine.Vector2 _) && !AerialStyles.TryLookup(pole, null, "RM_AerialMast", out UnityEngine.Vector2 _)
                  && !AerialStyles.TryLookup(pole, "Modern", "RM_AerialWallBracket", out UnityEngine.Vector2 _),
                  "can fail: an unknown look, no look, and a def with no row MISS (the caller falls back to the def's own numbers, never another look's)");
            AerialStyles.TryLookup(ins, "Scrapper", "RM_AerialMast", out UnityEngine.Vector2[] s0);
            AerialStyles.TryLookup(ins, "Futuristic", "RM_AerialMast", out UnityEngine.Vector2[] s3);
            Check(s0 != null && s3 != null && System.Math.Abs(s0[0].x - s3[0].x) > 0.05f,
                  "per look, not shared: the Scrapper and Futuristic masts' left insulators differ (the lookup keys on the look)");
        }

        private static void Spans()
        {
            string D = "Scrapper";
            bool same = AerialStyles.SpanLook("Modern", 50, "Modern", 10, D) == "Modern";
            bool older = AerialStyles.SpanLook("Industrial", 10, "Futuristic", 50, D) == "Industrial" && AerialStyles.SpanLook("Futuristic", 50, "Industrial", 10, D) == "Industrial";
            bool legacy = AerialStyles.SpanLook(null, 5, null, 9, "Modern") == "Modern" && AerialStyles.SpanLook(null, 5, "Futuristic", 9, "Modern") == "Modern"
                          && AerialStyles.SpanLook(null, 9, "Futuristic", 5, "Modern") == "Futuristic";
            Check(same && older && legacy, "spans: one look -> that look; two looks -> the OLDER pole's (lower id), whichever end asks; an unstyled pole counts as the default look");
            Check(AerialStyles.SpanLook("Industrial", 10, "Futuristic", 50, D) != "Futuristic", "can fail: a newer-pole-wins rule would draw this span Futuristic");
        }

        private static void Picker()
        {
            string def0 = "Scrapper";
            string fresh = AerialStyles.Resolve(null, def0, false, null);
            string picked = AerialStyles.Resolve("Modern", def0, false, null);
            string pickedDefaultMoved = AerialStyles.Resolve("Modern", "Industrial", false, null);
            string copy = AerialStyles.Resolve("Modern", def0, true, "Futuristic");
            string afterDeselect = AerialStyles.Resolve("Modern", def0, false, "Futuristic");    // Deselected() clears styleOverridden
            string copyLegacy = AerialStyles.Resolve("Modern", "Industrial", true, null);
            Check(fresh == "Scrapper" && picked == "Modern" && pickedDefaultMoved == "Modern" && copy == "Futuristic" && afterDeselect == "Modern" && copyLegacy == "Industrial",
                  $"picker: fresh {fresh}, picked {picked}, default moved {pickedDefaultMoved}, copy {copy}, after deselect {afterDeselect}, copy of legacy {copyLegacy}");
            // vanilla's getter on our defs, outside classic mode: neither the pick nor a copy ever reaches the building
            Check(AerialStyles.VanillaResolve(false, false, "Modern") == null && AerialStyles.VanillaResolve(false, true, "Futuristic") == null
                  && AerialStyles.VanillaResolve(true, true, "Futuristic") == "Futuristic",
                  "can fail: vanilla's rule drops the pick and the copy outside classic mode (why the getter patch exists)");
        }
    }
}
