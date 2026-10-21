// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 6 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P5):
// offline checks on the hose's band-aware routing: the production cord geometry (_Shared/SlackGeometry CordWorld bands,
// CordPlanner, compiled in), the production hose planner (HoseMath, compiled in), the pure band rules (HoseBandMath, compiled
// in) and the game adapter's wiring (RM_HoseBands, RM_MapComponent_Hoses, HosePorts, HoseEnds, read as text). L1 of the
// item's phase-6 verify: a route refuses a dug square without a ramp or ladder; routes lip -> ramp -> floor and lip -> ladder
// -> floor; endpoint reach respects band; a raised ladder leaves the hose hanging (not cut); a newly dug square on a laid route
// re-plans or retracts once. Each case has a can-fail. NOT proven here: a hose carried down a real ramp in a running game
// (L2 live row, owed).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseBandChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(System.IO.Path.Combine(rel));

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        private const int W = 30, H = 16, PitBand = 4;

        /// <summary>A flat world with a trench of band 4 running the full height at x = x0..x1 (no way round it).</summary>
        private static CordWorld Trench(int x0, int x1)
        {
            var w = new CordWorld(W, H);
            for (int x = x0; x <= x1; x++) for (int z = 0; z < H; z++) w.SetBand(new Cell(x, z), PitBand);
            return w;
        }

        /// <summary>A flat world with a square pit of band 4 (x0..x1, z0..z1): open ground round it.</summary>
        private static CordWorld Pit(int x0, int x1, int z0, int z1)
        {
            var w = new CordWorld(W, H);
            for (int x = x0; x <= x1; x++) for (int z = z0; z <= z1; z++) w.SetBand(new Cell(x, z), PitBand);
            return w;
        }

        /// <summary>Every step along a polyline (sampled at 0.05 cell) is one CordWorld.StepAllowed accepts; the band
        /// changes it makes, as (from, to) cell pairs.</summary>
        private static List<(Cell, Cell)> BandSteps(CordWorld w, IList<V2> pts, out bool legal)
        {
            legal = true;
            var steps = new List<(Cell, Cell)>();
            Cell prev = pts[0].Floor;
            for (int i = 1; i < pts.Count; i++)
            {
                int k = Math.Max(1, (int)Math.Ceiling(V2.Dist(pts[i - 1], pts[i]) / 0.05));
                for (int j = 0; j <= k; j++)
                {
                    Cell c = (pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k)).Floor;
                    if (c == prev) continue;
                    if (!w.StepAllowed(prev, c)) legal = false;
                    if (w.BandAt(prev) != w.BandAt(c)) steps.Add((prev, c));
                    prev = c;
                }
            }
            return steps;
        }

        private static readonly HoseReelRect Reel = new HoseReelRect(2, 7, 1, 1);
        private const double Len = 40;

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseBand_P5_refuses_a_dug_square_without_ramp_or_ladder", () =>
            {
                CordWorld w = Trench(10, 13);
                // the floor of the trench, and the far lip across it: no way in, no way over
                Assert(HoseMath.CheckInstall(w, Reel, new Cell(11, 7), Len) == "no route", "a hose reached the trench floor over a sheer wall");
                Assert(HoseMath.CheckInstall(w, Reel, new Cell(18, 7), Len) == "no route", "a hose crossed the trench with no ramp or ladder");
                Assert(!HoseMath.SegmentClear(w, new Cell(8, 7).Centre, new Cell(11, 7).Centre), "the lay's clip test let a hose drop down the wall");
                Assert(!w.StepAllowed(new Cell(9, 7), new Cell(10, 8)), "a diagonal step slipped down the wall");
                // can-fail: the same layout with no bands (the pre-ruling hose, and every Gimme Some Slack world) routes straight over
                var flat = new CordWorld(W, H);
                Assert(HoseMath.CheckInstall(flat, Reel, new Cell(18, 7), Len) == null, "can-fail: the flat world refused a plain route");
                Assert(!flat.HasBands && flat.StepAllowed(new Cell(9, 7), new Cell(10, 7)), "can-fail: a world with no bands refuses a step");
            });

            Case("HoseBand_P5_routes_lip_ramp_floor", () =>
            {
                CordWorld w = Trench(10, 13);
                // a ramp on the trench floor at (10,4), facing west up onto the lip (9,4): RM_PitRamp.Joins -> one link
                w.LinkBands(new Cell(9, 4), new Cell(10, 4));
                Cell floor = new Cell(12, 10);
                Assert(HoseMath.CheckInstall(w, Reel, floor, Len) == null, "the hose would not go down the ramp");
                List<V2> taut = HoseMath.RoutePulled(w, Reel, floor, Len, false);
                List<(Cell, Cell)> steps = BandSteps(w, taut, out bool legal);
                // the one band change leaves the lip at the ramp's top, onto the ramp or diagonally past its corner (a 0.05-cell sample
                // can skip the corner cell; StepAllowed admits that diagonal only through the ramp)
                Assert(legal && steps.Count == 1 && steps[0].Item1 == new Cell(9, 4) && steps[0].Item2.X == 10 && Math.Abs(steps[0].Item2.Z - 4) <= 1,
                    "the taut route did not go lip -> ramp -> floor: " + string.Join(" ", steps.Select(s => s.Item1 + ">" + s.Item2)));
                HoseLay lay = HoseMath.Lay(w, Reel.Mouth, floor.Centre, new HoseShapeParams { MaxLength = Len }, 7);
                Assert(lay.Ok, "the hose would not lay down the ramp: " + lay.Reason);
                BandSteps(w, lay.Flat, out bool layLegal);
                BandSteps(w, lay.Plump, out bool plumpLegal);
                Assert(layLegal && plumpLegal, "the laid (flat or plump) hose left the ramp over the wall");
                // and across: down the ramp, over the floor, up a second ramp at (13,12) facing east
                w.LinkBands(new Cell(13, 12), new Cell(14, 12));
                Assert(HoseMath.CheckInstall(w, Reel, new Cell(18, 12), Len) == null, "the hose would not cross by two ramps");
                // can-fail: the ramp removed, the floor is out of reach again
                CordWorld noRamp = Trench(10, 13);
                Assert(HoseMath.CheckInstall(noRamp, Reel, floor, Len) == "no route", "can-fail: the floor was reached with no ramp");
            });

            Case("HoseBand_P5_routes_lip_ladder_floor_and_raised_ladder_leaves_it_hanging", () =>
            {
                // the ladder rule: carried while it hangs on that wall and spans the drop, RAISED OR NOT (review answer 7)
                Assert(HoseBandMath.LadderCarriesHose(true, true, true, false) && HoseBandMath.LadderCarriesHose(true, true, true, true),
                    "raising the ladder changed whether it carries the hose");
                Assert(!HoseBandMath.LadderCarriesHose(true, false, true, false), "can-fail: a ladder on another wall carried the hose");
                Assert(!HoseBandMath.LadderCarriesHose(true, true, false, false), "can-fail: a ladder too short for its wall carried the hose");
                Assert(!HoseBandMath.LadderCarriesHose(false, true, true, false), "can-fail: no ladder carried the hose");
                CordWorld[] worlds = new CordWorld[2];
                ulong[] hash = new ulong[2];
                HoseLay[] lays = new HoseLay[2];
                for (int raised = 0; raised < 2; raised++)
                {
                    CordWorld w = Pit(10, 15, 3, 12);
                    // a ladder on the pit floor at (10,7) hung on the west wall (lip (9,7))
                    if (HoseBandMath.StepLinked(PitBand, 0, false, HoseBandMath.LadderCarriesHose(true, true, true, raised == 1)))
                        w.LinkBands(new Cell(10, 7), new Cell(9, 7));
                    Cell floor = new Cell(13, 7);
                    HoseLay lay = HoseMath.Lay(w, Reel.Mouth, floor.Centre, new HoseShapeParams { MaxLength = Len }, 11);
                    Assert(lay.Ok, "the hose would not hang down the ladder (raised " + raised + "): " + lay.Reason);
                    List<(Cell, Cell)> steps = BandSteps(w, lay.Flat, out bool legal);
                    Assert(legal && steps.Count == 1 && steps[0].Item1 == new Cell(9, 7) && steps[0].Item2.X == 10 && Math.Abs(steps[0].Item2.Z - 7) <= 1,
                        "the hose did not go lip -> ladder -> floor (raised " + raised + ")");
                    worlds[raised] = w;
                    lays[raised] = lay;
                    hash[raised] = Corridor(w, lay);
                }
                // hanging, not cut: raising the ladder leaves the corridor signature (and so the 250-tick check) untouched
                Assert(hash[0] == hash[1] && Corridor(worlds[1], lays[0]) == hash[0], "raising the ladder moved the hose's corridor (it would re-plan or cut)");
                // production: the adapter passes the raised state only to the rule that ignores it
                string bands = Src("Hose", "RM_HoseBands.cs");
                string linked = Body(bands, "public static bool Linked(");
                Assert(linked.Contains("HoseBandMath.LadderCarriesHose(") && linked.Contains("RM_PitRamp.Joins(") && !linked.Contains("EffectivelyRaised")
                    && !linked.Contains("LadderLetsOut"), "RM_HoseBands.Linked does not read the ladder through the hose rule (raised state or climb rule leaks in)");
                // can-fail: with the link gone the pit floor is closed (no other way down)
                CordWorld closed = Pit(10, 15, 3, 12);
                Assert(HoseMath.CheckInstall(closed, Reel, new Cell(13, 7), Len) == "no route", "can-fail: the pit floor was reached with no ladder");
            });

            Case("HoseBand_P5_endpoint_reach_respects_band", () =>
            {
                Assert(HoseBandMath.EndReaches(PitBand, PitBand) && HoseBandMath.EndReaches(0, 0), "an end on its own band did not reach");
                Assert(!HoseBandMath.EndReaches(PitBand, 0) && !HoseBandMath.EndReaches(0, PitBand), "can-fail: a pump on the lip took a hose end on the floor");
                Assert(HoseBandMath.Band(false, PitBand) == 0 && HoseBandMath.Band(true, PitBand) == PitBand, "the band ignores the rules switch");
                string ports = Body(Src("Hose", "HosePorts.cs"), "private static Thing RawFindAt(");
                int gate = ports.IndexOf("HoseBandMath.EndReaches(endBand, RM_HoseBands.BandAt(map, c))", StringComparison.Ordinal);
                Assert(gate > 0 && gate > ports.IndexOf("foreach (Cell pc in rect.Perimeter())", StringComparison.Ordinal)
                    && gate < ports.IndexOf("Classify(t)", ports.IndexOf("foreach (Cell pc", StringComparison.Ordinal), StringComparison.Ordinal),
                    "HosePorts.RawFindAt does not gate each beside-the-end port by band before it classifies it");
                string water = Body(Src("Hose", "HoseEnds.cs"), "public static TerrainDef WaterAt(");
                Assert(water.Contains("HoseBandMath.EndReaches(band, RM_HoseBands.BandAt(map, n))"), "HoseEnds.WaterAt touches water across a sheer wall");
            });

            Case("HoseBand_P5_newly_dug_square_replans_or_retracts_once", () =>
            {
                // re-plan: a laid hose across open ground; a 3x3 pit is dug on its line, open ground round it
                var before = new CordWorld(W, H);
                Cell far = new Cell(20, 7);
                HoseLay lay = HoseMath.Lay(before, Reel.Mouth, far.Centre, new HoseShapeParams { MaxLength = Len }, 5);
                Assert(lay.Ok, "the open lay failed: " + lay.Reason);
                CordWorld dug = Pit(10, 12, 6, 8);
                ulong h0 = Corridor(before, lay), h1 = Corridor(dug, lay);
                Assert(h0 != h1, "a square dug under the hose did not move its corridor hash (the 250-tick check would never see it)");
                Assert(HoseMath.CheckReplan(dug, Reel, far, Len, false, null) == null, "the hose with a way round the pit was reeled in");
                HoseLay again = HoseMath.Lay(dug, Reel.Mouth, far.Centre, new HoseShapeParams { MaxLength = Len }, 5);
                Assert(again.Ok && again.Flat.All(p => dug.BandAt(p.Floor) == 0), "the re-planned hose still runs over the pit");
                // once: the re-laid hose's corridor is stable on the same world, so the next check does nothing
                HoseLay third = HoseMath.Lay(dug, Reel.Mouth, far.Centre, new HoseShapeParams { MaxLength = Len }, 5);
                Assert(third.Ok && Corridor(dug, third) == Corridor(dug, again) && Corridor(dug, again) != Corridor(before, again)
                    && HoseMath.CheckReplan(dug, Reel, far, Len, false, null) == null, "the re-plan is not idempotent (a second check would move it again)");
                // retract: a full-height trench dug across it with no ramp or ladder -> the reason to reel it in
                CordWorld trench = Trench(10, 12);
                Assert(Corridor(trench, lay) != h0, "the trench did not move the corridor hash");
                Assert(HoseMath.CheckReplan(trench, Reel, far, Len, false, null) == "no route", "a hose cut off by the trench was left laid");
                // production wiring: World() writes bands, the live per-cell read folds band + links, the tick's corridor branch
                // is the one that re-plans (layKey cleared) or retracts (CheckReplan -> Retract)
                string comp = Src("Hose", "RM_MapComponent_Hoses.cs");
                Assert(Body(comp, "internal CordWorld World(").Contains("RM_HoseBands.Apply(map, cw)"), "World() does not read depth");
                string live = Body(comp, "internal ulong LiveCellSig(");
                Assert(live.Contains("RM_HoseBands.BandAt(map, c)") && live.Contains("RM_HoseBands.LinkMask(map, c, band)"), "LiveCellSig ignores band or links");
                Assert(comp.Contains("CordSig.Of(walkable, door, extra, band, linkMask)"), "SigOf is not the shared CordSig.Of formula");
                string tick = Body(comp, "public override void MapComponentTick(");
                Assert(tick.Contains("CorridorHashLive(r.lay) != r.corridorHash") && tick.Contains("HoseMath.CheckReplan(World()") && tick.Contains("r.Retract(why)"),
                    "the 250-tick corridor branch is not the re-plan-or-retract");
                Assert(Body(Src("Hose", "CompHoseReel.cs"), "internal bool TrailWalkable(").Contains("w.StepAllowed(prev.Value, k)"),
                    "a walked trail over a newly dug square still reads walkable");
                // can-fail: a dig away from the corridor (its box padded 2) does not move the hash
                CordWorld away = Pit(10, 12, 13, 15);
                Assert(Corridor(away, lay) == h0 || lay.Flat.Any(p => p.Z > 10), "can-fail: a dig far off the corridor moved the hash");
            });

            Case("HoseBand_P5_no_bands_leaves_gss_signatures_unchanged", () =>
            {
                var w = new CordWorld(8, 8);
                w.SetExtraCost(new Cell(2, 2), 1.5f);
                w.SetDoor(new Cell(3, 3));
                w.SetBlocked(new Cell(4, 4), BlockKind.Wall);
                w.SetBand(new Cell(5, 5), 0);   // a zero band allocates nothing
                Assert(!w.HasBands, "setting band 0 allocated the band layer");
                foreach (var c in new[] { new Cell(1, 1), new Cell(2, 2), new Cell(3, 3), new Cell(4, 4) })
                {
                    ulong old = (ulong)(w.IsWalkable(c) ? 1 : 2) ^ (w.IsDoor(c) ? 4UL : 0UL) ^ ((ulong)Math.Round(w.ExtraCost(c) * 16) << 3);
                    Assert(CordSig.CellSig(w, c) == old, "a world with no bands changed a corridor signature at " + c);
                }
                w.SetBand(new Cell(1, 1), 2);
                Assert(CordSig.CellSig(w, new Cell(1, 1)) != CordSig.CellSig(new CordWorld(8, 8), new Cell(1, 1)), "can-fail: a band left the signature unchanged");
                w.LinkBands(new Cell(1, 1), new Cell(1, 2));
                Assert(w.LinkMask(new Cell(1, 2)) == 1 << 2 && w.LinkMask(new Cell(1, 1)) == 1, "the link mask is not numbered N,E,S,W");
            });
        }

        /// <summary>The production corridor hash (RM_MapComponent_Hoses.CorridorHash: the lay's box padded 2, CordSig.CellSig per cell).</summary>
        private static ulong Corridor(CordWorld w, HoseLay lay)
        {
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            foreach (V2 p in lay.Flat) { Cell c = p.Floor; x0 = Math.Min(x0, c.X); z0 = Math.Min(z0, c.Z); x1 = Math.Max(x1, c.X); z1 = Math.Max(z1, c.Z); }
            ulong h = 1469598103934665603UL;
            for (int z = z0 - 2; z <= z1 + 2; z++)
                for (int x = x0 - 2; x <= x1 + 2; x++)
                    h = (h ^ CordSig.CellSig(w, new Cell(x, z))) * 1099511628211UL;
            return h;
        }
    }
}
