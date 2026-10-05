// Per-build style, stage 3 (design/RimMandrake/messyconduit_style_per_build_design.md section 5 stage 3): the hose takes
// its REEL's look. Checks the Verse-free rules in ../Hose/HoseStyles.cs that HoseMaterials.For(reel) and the reel's
// ThingStyleDefs are built from. Each property has a can-fail beside it. (Art on disk is checked by
// validation_style_hose.py --offline: this selftest runs from a staging dir with no Textures.)
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Aerial;
using RimMandrake.MessyConduit.Hose;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class StyleStage3Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "style3: " + msg);

        public static void Run()
        {
            Naming();
            Paths();
            HoseTakesReelLook();
            Wrap();
        }

        private static void Naming()
        {
            var n = AerialStyles.Looks.Select(HoseStyles.StyleDefName).ToList();
            Check(n.Distinct().Count() == 4 && n.SequenceEqual(new[] { "RM_HoseReel_Scrapper", "RM_HoseReel_Industrial", "RM_HoseReel_Modern", "RM_HoseReel_Futuristic" })
                  && HoseStyles.StyledDefs.SequenceEqual(new[] { "RM_HoseReel" }) && !AerialStyles.StyledDefs.Contains("RM_HoseReel"),
                  "naming: 4 reel style defs RM_HoseReel_<Look> in menu order; the reel registers through HoseStyles, not the anchors' list");
        }

        private static void Paths()
        {
            var all = new HashSet<string>();
            var bad = new List<string>();
            foreach (string l in AerialStyles.Looks)
                foreach (string p in HoseStyles.Pieces)
                {
                    string path = HoseStyles.PathFor(l, p);
                    all.Add(path);
                    string want = l == "Scrapper" ? "RimMandrake/MessyConduit/Hose/" + p : "RimMandrake/MessyConduit/Hose/Styles/" + l + "/" + p;
                    if (path != want) bad.Add(path);
                }
            Check(bad.Count == 0 && all.Count == 4 * HoseStyles.Pieces.Length && HoseStyles.Pieces.Length == 7,
                  $"paths: 7 hose pieces x 4 looks = {all.Count} distinct paths, Scrapper = the root files, others = Styles/<Look>/" + (bad.Count > 0 ? ": wrong " + string.Join(", ", bad) : ""));
            var shadows = AerialStyles.Looks.Select(l => HoseStyles.PathFor(l, HoseStyles.SharedShadow)).Distinct().ToList();
            Check(shadows.Count == 1 && shadows[0] == "RimMandrake/MessyConduit/Hose/Strand_Shadow", "the strand shadow is ONE shared path for every look");
            // the reel's stored texPath per look, and the laid art Graphic_HoseReel finds BESIDE it (same folder + Reel_Deployed)
            var stored = AerialStyles.Looks.Select(HoseStyles.ReelTexPath).ToList();
            var laid = stored.Select(s => s.Substring(0, s.LastIndexOf('/') + 1) + "Reel_Deployed").ToList();
            Check(stored.Distinct().Count() == 4 && laid.Distinct().Count() == 4 && stored[0] == "RimMandrake/MessyConduit/Hose/Reel_PumpHookup"
                  && laid[2] == "RimMandrake/MessyConduit/Hose/Styles/Modern/Reel_Deployed",
                  "reel art: each look's stored texPath has its OWN laid (empty drum) sibling, so the swap never crosses looks");
            Check(HoseStyles.PathFor("Gold", "Binding") == HoseStyles.PathFor("Scrapper", "Binding") && HoseStyles.PathFor(null, "Mouth") == HoseStyles.PathFor("Scrapper", "Mouth"),
                  "can fail: an unknown or null look reads Scrapper's root art, never a made-up Styles/Gold/ folder");
        }

        private static void HoseTakesReelLook()
        {
            int pairs = 0, ok = 0, globalAgrees = 0;
            foreach (string reel in AerialStyles.Looks)
                foreach (string def in AerialStyles.Looks)
                {
                    pairs++;
                    string got = HoseStyles.HoseLook(reel, def);
                    if (got == reel) ok++;
                    if (def == reel) globalAgrees++;          // what a rule reading the global setting would draw correctly
                }
            Check(pairs == 16 && ok == 16, $"hose look: for every (reel look, default setting) pair the hose draws the REEL's look ({ok}/{pairs})");
            Check(globalAgrees == 4, "can fail: a hose reading the global setting would be right in only 4 of 16 pairs, so the check above can tell them apart");
            Check(HoseStyles.HoseLook(null, "Modern") == "Modern" && HoseStyles.HoseLook("Gold", "Industrial") == "Industrial" && HoseStyles.HoseLook(null, null) == "Scrapper",
                  "legacy: a reel with no look draws the default look; no default at all draws Scrapper");
            // the selection the draw code makes per look returns that look's folder for every piece (the material set's source)
            bool sel = AerialStyles.Looks.All(l => HoseStyles.Pieces.All(p => HoseStyles.PathFor(HoseStyles.HoseLook(l, "Scrapper"), p) == HoseStyles.Folder(l) + p));
            Check(sel, "material selection: a reel in look L under any default draws every hose piece from L's folder");
        }

        private static void Wrap()
        {
            Check(HoseStyles.AgedClothWrap("Scrapper") && AerialStyles.Looks.Count(HoseStyles.AgedClothWrap) == 1,
                  "binding: only Scrapper's sack-cloth wrap takes the aged-cloth brown tint");
        }
    }
}
