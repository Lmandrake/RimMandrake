// PIT_COVER_SOD (bar pit_covered_invisible: "the same patch of ground looks the same at play zoom in the BEFORE frame (undug)
// and the AFTER frame (a covered superdeep excavation)"): a lid that prints ground also prints the low wild plant the ground
// round it carries, laid out as vanilla Plant.Print lays it. Offline checks on the pure rules (RM_PitCoverSodMath) and on the
// production call sites. Each case has a can-fail.
// NOT proven here: the live look (a covered pit in a grassy field reads as grass at play zoom; the sod above the lid's ground
// print and below pawns), nor that vanilla PlantPosIndices still builds its lists the way RM_PitCoverSodMath copies.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitCoverSodChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(System.IO.Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitCoverSod_rings_and_census", () =>
            {
                for (int r = 1; r <= RM_PitCoverSodMath.MaxRing; r++)
                {
                    int[] o = RM_PitCoverSodMath.RingOffsets(r);
                    Assert(o.Length == 16 * r, "ring " + r + " holds 8r squares");
                    var seen = new HashSet<long>();
                    for (int i = 0; i < o.Length; i += 2)
                    {
                        Assert(Math.Max(Math.Abs(o[i]), Math.Abs(o[i + 1])) == r, "ring " + r + " square at Chebyshev distance r");
                        Assert(seen.Add(o[i] * 1000L + o[i + 1]), "can-fail: ring " + r + " repeats no square");
                    }
                }
                Assert(RM_PitCoverSodMath.RingOffsets(0).Length == 0, "no ring 0");
                // 3 of 8 neighbours carrying grass grows a lawn on the lid; 2 of 8 is a stray tuft
                Assert(RM_PitCoverSodMath.Enough(3, 8), "3 of 8 grassy neighbours: sod");
                Assert(!RM_PitCoverSodMath.Enough(2, 8), "can-fail: 2 of 8 is not enough");
                Assert(!RM_PitCoverSodMath.Enough(0, 8), "can-fail: bare ground round it, bare lid");
                Assert(!RM_PitCoverSodMath.Enough(0, 0), "can-fail: no ground sampled, no sod");
                Assert(RM_PitCoverSodMath.Enough(6, 16), "the same share of a wider census (6 of 16)");
                Assert(!RM_PitCoverSodMath.Enough(5, 16), "can-fail: 5 of 16 is under 3 of 8");
                // the commonest plant wins, ties to the first seen; -1 carries none
                int[] keys = { 0, 0, 1, -1, 0, -1, 1, -1 };
                Assert(RM_PitCoverSodMath.Commonest(keys, keys.Length, out int c) == 0 && c == 3, "grass (3) beats dandelion (2)");
                Assert(RM_PitCoverSodMath.Commonest(new[] { 2, 1, 1, 2 }, 4, out c) == 2 && c == 2, "a tie goes to the first seen");
                Assert(RM_PitCoverSodMath.Commonest(new[] { 0, 1, 1, 1 }, 1, out c) == 0 && c == 1, "can-fail: only the first n count");
                Assert(RM_PitCoverSodMath.Commonest(new[] { -1, -1 }, 2, out c) == -1 && c == 0, "can-fail: none carries, no winner");
                Assert(RM_PitCoverSodMath.Commonest(null, 3, out c) == -1, "no keys, no winner");
            });

            Case("PitCoverSod_vanilla_layout", () =>
            {
                Assert(RM_PitCoverSodMath.MeshCount(0f, 9) == 1, "a seedling still draws one mesh");
                Assert(RM_PitCoverSodMath.MeshCount(0.5f, 9) == 5, "half grown: ceil(4.5)");
                Assert(RM_PitCoverSodMath.MeshCount(1f, 9) == 9, "fully grown: every mesh");
                Assert(RM_PitCoverSodMath.MeshCount(1.5f, 9) == 9 && RM_PitCoverSodMath.MeshCount(float.NaN, 9) == 1, "can-fail: clamped, NaN-safe");
                Assert(RM_PitCoverSodMath.GridSide(1) == 1 && RM_PitCoverSodMath.GridSide(4) == 2 && RM_PitCoverSodMath.GridSide(9) == 3
                    && RM_PitCoverSodMath.GridSide(25) == 5, "perfect squares give their side");
                Assert(RM_PitCoverSodMath.GridSide(7) == 1, "can-fail: not a square falls back to 1, as vanilla");
                RM_PitCoverSodMath.SubSquareCentre(0, 3, out float dx, out float dz);
                Assert(Math.Abs(dx - 1f / 6f) < 1e-5f && Math.Abs(dz - 1f / 6f) < 1e-5f, "sub-square 0 sits south-west");
                RM_PitCoverSodMath.SubSquareCentre(5, 3, out dx, out dz);
                Assert(Math.Abs(dx - 0.5f) < 1e-5f && Math.Abs(dz - 5f / 6f) < 1e-5f, "can-fail: index / side columns east, index % side rows north");
                Assert(Math.Abs(RM_PitCoverSodMath.JitterMax(3) - 0.1f) < 1e-5f, "jitter 0.3 of a sub-square");
                // vanilla PlantPosIndices: n slots, 0..n-2 and a second 0, shuffled
                int[] a = RM_PitCoverSodMath.PositionOrder(9, 12345);
                int[] b = RM_PitCoverSodMath.PositionOrder(9, 12345);
                Assert(a.Length == 9, "one slot per mesh");
                int zeros = 0, last = 0;
                var once = new HashSet<int>();
                for (int i = 0; i < a.Length; i++)
                {
                    Assert(a[i] == b[i], "can-fail: the same lid lays its tufts the same way every print");
                    zeros += a[i] == 0 ? 1 : 0;
                    last += a[i] == 8 ? 1 : 0;
                    Assert(a[i] >= 0 && a[i] < 8 && (a[i] == 0 || once.Add(a[i])), "every slot is a sub-square, 1..7 once each");
                }
                Assert(zeros == 2 && last == 0, "vanilla's quirk kept: 0 twice, the last sub-square never");
                bool differs = false;
                for (int s = 1; s < 20 && !differs; s++)
                {
                    int[] o = RM_PitCoverSodMath.PositionOrder(9, 12345 + s * 7919);
                    for (int i = 0; i < o.Length && !differs; i++)
                    {
                        differs = o[i] != a[i];
                    }
                }
                Assert(differs, "can-fail: another lid lays them another way");
                Assert(RM_PitCoverSodMath.PositionOrder(1, 7).Length == 1 && RM_PitCoverSodMath.PositionOrder(1, 7)[0] == 0, "a single-mesh plant has one slot");
                Assert(Math.Abs(RM_PitCoverSodMath.ClampSingleZ(10.2f, 10f, 0.8f, out bool up) - 10.4f) < 1e-4f && up, "a low single mesh is lifted onto its square");
                Assert(RM_PitCoverSodMath.ClampSingleZ(10.5f, 10f, 0.8f, out up) == 10.5f && !up, "can-fail: one that sits inside stays");
            });

            Case("PitCoverSod_wired_to_the_ground_print", () =>
            {
                string cover = Src("Pits", "Building_PitCover.cs");
                string print = Between(cover, "public override void Print(SectionLayer layer)", "protected override void DrawAt(");
                int art = print.IndexOf("RM_PitCoverUtility.LidShowsArt(map, Position)", StringComparison.Ordinal);
                int artReturn = print.IndexOf("return;", art, StringComparison.Ordinal);
                int sod = print.IndexOf("RM_PitCoverSod.TryPrint(this, layer, surface);", StringComparison.Ordinal);
                Assert(art >= 0 && artReturn > art, "the plank-art branch returns");
                Assert(sod > artReturn, "can-fail: the sod prints after the art branch has returned (a plank lid grows nothing)");
                Assert(sod > print.IndexOf("TerrainMimicPrinter.PrintTerrainMimic(this, layer);", StringComparison.Ordinal)
                    && sod > print.IndexOf("Printer_Plane.PrintPlane(layer, center, Vector2.one, mat);", StringComparison.Ordinal),
                    "can-fail: after either ground print, so it draws over it");
                string sodSrc = Src("Pits", "RM_PitCoverSod.cs");
                string isSod = Between(sodSrc, "public static bool IsSod(", "private static bool HiddenAt(");
                foreach (string rule in new[] { "pp.IsTree", "p.sown", "RM_PitCoverSodMath.MaxVisualSize", "HiddenAt(p.def, p.Position, map)" })
                {
                    Assert(isSod.Contains(rule), "can-fail: sod is a low wild drawn plant: " + rule);
                }
                string census = Between(sodSrc, "public static bool TryPrint(", "private static void Print(");
                foreach (string rule in new[] { "RimMandrakeFlowWorksSettings.pitCoverSodEnabled", "eng.HollowDepthAt(g) != 0",
                    "RM_PitCoverUtility.CoverAt(map, g) != null", "RM_PitCoverSodMath.Enough(carriers, n)" })
                {
                    Assert(census.Contains(rule), "can-fail: the census reads " + rule);
                }
                string draw = Between(sodSrc, "private static void Print(", "public static void RedrawAllLids()");
                foreach (string rule in new[] { "centre.y = def.Altitude;", "Rand.PushState();", "Rand.PopState();", "Rand.Seed = c.GetHashCode();",
                    "GetSnowDepth(map) > 0.8f", "PlantUtility.SetWindExposureColors(windColors, rep);" })
                {
                    Assert(draw.Contains(rule), "can-fail: drawn as vanilla Plant.Print: " + rule);
                }
                Assert(!draw.Contains("DrawPos.y"), "can-fail: the sod draws at the plant's altitude, not the lid's");
                Assert(Src("RimMandrake_FlowWorks.csproj").Contains(@"Pits\RM_PitCoverSod.cs")
                    && Src("RimMandrake_FlowWorks.csproj").Contains(@"Pits\RM_PitCoverSodMath.cs"), "can-fail: both files compile into the mod");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("appliedSod != pitCoverSodEnabled") && mod.Contains("RM_PitCoverSod.RedrawAllLids();")
                    && mod.Contains("appliedSod = pitCoverSodEnabled;"), "can-fail: toggling the setting re-prints every lid");
            });
        }
    }
}
