// HOSE_MOUTH_FIX_FACE_ON_DISC (art brief C6, owner card 2026-10-23: "Keep the pipe in the proper perspective plane"):
//   a hose lying flat never shows its opening to the camera, so the open free end draws its Mouth piece edge-on, a lip
//   line at the wrap's outer face, never the 0.30 x 0.86 squashed disc that read as the end turned up (three art redraw
//   rounds failed because the code, not the texture, made the oval).
// HOSE_REEL_SHADOW_FIX_FULL_TILE_SQUARE: every reel look casts the same sub-tile shadow box (all four looks share one
//   drum footprint, measured 0.85 cell wide side-on), not the full-tile 1.23 x 1.04 square three of them had.
// HoseMath is compiled in; the draw call and the defs are read as text. NOT proven here: the picture (live look owed).
using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Hose;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseEndLipChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Above this along/across ratio the drawn opening reads as an oval, i.e. turned toward the camera.</summary>
        private const double EdgeOnMaxRatio = 0.12;

        private static string Def(string file) => Regex.Replace(File.ReadAllText(Path.Combine(
            Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"))), "Defs", "Hose", file)), @"\s+", " ");

        public static void Run(Action<string, Action> Case)
        {
            Case("HOSE_MOUTH_FIX_FACE_ON_DISC: the open free end's lip is edge-on and sits at the wrap's outer face", () =>
            {
                foreach (double vis in new[] { 0.15, 0.22, 0.30, 0.40 })
                {
                    HoseMath.OpenEndLip(vis, out double along, out double across, out double back);
                    Assert(along > 0 && across > 0, "lip has a size on hose " + vis);
                    Assert(along / across <= EdgeOnMaxRatio, "lip edge-on on hose " + vis + ": along/across " + (along / across).ToString("0.000"));
                    // outer edge of the lip = the wrap's outer face (the wrap runs WrapOverCut past the cut), so nothing pokes out
                    Assert(Math.Abs((along / 2 - back) - HoseMath.WrapOverCut) < 1e-9, "lip's outer edge on the wrap's face, hose " + vis);
                    Assert(across <= HoseMath.WrapWidth(vis) + 1e-9, "lip no wider than the wrap, hose " + vis);
                }
            });

            Case("HOSE_MOUTH_FIX_FACE_ON_DISC: the draw uses HoseMath.OpenEndLip, not a fixed squashed disc", () =>
            {
                string mc = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(mc, @"HoseMath\.OpenEndLip\(vis, out double lipAlong, out double lipAcross, out double lipBack\);"
                    + @" PieceXZ\(hm\.Mouth, e - d1 \* lipBack, d1, \(float\)lipAlong, \(float\)lipAcross,", "open end lip");
                Assert(!mc.Contains("0.30f * vis, 0.86f * vis"), "the old face-on 0.30 x 0.86 disc is gone");
                RiverSwitchFlipChecks.Has(mc, @"Wrap\(hm, e - d1 \* \(HoseMath\.WrapLength / 2 - HoseMath\.WrapOverCut\)", "open end wrap to the cut");
            });

            Case("HOSE_REEL_SHADOW_FIX_FULL_TILE_SQUARE: every reel look and the base reel share one square sub-tile shadow", () =>
            {
                string all = Def("RM_HoseReelStyles.xml") + Def("RM_HoseReel.xml");
                var vols = Regex.Matches(all, @"<shadowData> ?<volume>\(([^)]*)\)</volume>").Cast<Match>()
                    .Select(m => m.Groups[1].Value.Split(',').Select(s => double.Parse(s.Trim(), CultureInfo.InvariantCulture)).ToArray()).ToList();
                Assert(vols.Count == 5, "five reel shadow volumes (4 looks + base), found " + vols.Count);
                foreach (double[] v in vols)
                {
                    Assert(v[0] < 1 && v[2] < 1, "sub-tile shadow, got " + string.Join(",", v));
                    Assert(Math.Abs(v[0] - v[2]) < 1e-9, "square (the engine swaps x/z per rotation), got " + string.Join(",", v));
                    Assert(v.SequenceEqual(vols[0]), "all looks equal, got " + string.Join(",", v) + " vs " + string.Join(",", vols[0]));
                }
            });
        }
    }
}
