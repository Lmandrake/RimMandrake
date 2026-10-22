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
using RimMandrake.FlowWorks.Machinery;
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

        // northstar/scenarios/c10_rain_basin.py's closed ledger (plot cells; keep in step): the two tanks, the reel's footprint
        // corner (built West one square east, so this is its footprint), and the hose end beside the far tank
        private static readonly (int, int)[] C10LedgerTanks = { (32, 5), (40, 3) };
        private static readonly (int, int) C10LedgerReel = (40, 5), C10LedgerEnd = (34, 5);
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

            Case("HoseBand_swim_split_pool_stays_one_floor", () =>
            {
                // LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM: a pit (floor 8) holding 2 m reads band 4 (the swim surface); the pump's
                // intake square drawn a hair under 2 m reads band 8 until the next levelling pulse. Same floor: still one floor.
                Assert(HoseBandMath.FloorJoined(8, 8, false, false), "one floor split by the swim surface was not joined");
                Assert(!HoseBandMath.FloorJoined(8, 4, false, false), "can-fail: two different floors were joined");
                Assert(!HoseBandMath.FloorJoined(8, 8, true, false), "can-fail: a covered square was joined");
                Assert(!HoseBandMath.FloorJoined(0, 0, false, false), "can-fail: undug ground was joined");
                Cell intake = new Cell(13, 7);
                for (int joined = 0; joined < 2; joined++)
                {
                    CordWorld w = Pit(10, 15, 3, 12);
                    w.LinkBands(new Cell(10, 7), new Cell(9, 7));   // the ladder
                    w.SetBand(intake, 8);
                    if (joined == 1)
                        for (int r = 0; r < 4; r++)
                        {
                            var n = new Cell(intake.X + CordWorld.CardX[r], intake.Z + CordWorld.CardZ[r]);
                            if (HoseBandMath.FloorJoined(8, 8, false, false)) w.LinkBands(intake, n);
                        }
                    string why = HoseMath.CheckInstall(w, Reel, intake, Len);
                    if (joined == 1) Assert(why == null, "the hose lost the intake square to a swim-surface split: " + why);
                    else Assert(why == "no route", "can-fail: the split square was reached with no floor join: " + why);
                }
                string bands = Src("Hose", "RM_HoseBands.cs");
                Assert(Body(bands, "public static bool Linked(").Contains("FloorJoined(map, a, b)"), "RM_HoseBands.Linked does not join one floor");
                Assert(Body(bands, "private static void Count(").Contains("FloorJoined(map, a, b)"), "the readout counts a floor join as a ladder");
            });

            Case("Scenario_C4_C10_hoses_lay_offline", () =>
            {
                // The review scenarios' hoses (northstar/scenarios c04/c10), rebuilt as the hose world sees them, laid by the
                // production planner from the turned reel's outlet (RM_MapComponent_Hoses.LayFrom: its own footprint held solid).
                // OX shifts plot x so C4's drain (plot x -12) is on the grid. A fail names the scenario and the planner's reason.
                const int OX = 15;
                Cell C(int x, int z) => new Cell(x + OX, z);
                var sp = new HoseShapeParams { MinBendRadius = 1.2, MaxLength = HoseMath.DefaultMaxLength };
                string LayAll(CordWorld w, HoseReelRect reel, Cell target)
                {
                    string why = HoseMath.CheckInstall(w, reel, target, sp.MaxLength);
                    if (why != null) return "install: " + why;
                    var held = new List<(Cell, BlockKind)>();
                    for (int x = reel.X0; x < reel.X0 + reel.W; x++)
                        for (int z = reel.Z0; z < reel.Z0 + reel.H; z++) { held.Add((new Cell(x, z), w.BlockAt(new Cell(x, z)))); w.SetBlocked(new Cell(x, z), BlockKind.Device); }
                    try
                    {
                        for (ulong seed = 17; seed < 17 + 7919UL * 40; seed += 7919UL)
                        {
                            HoseLay lay = HoseMath.Lay(w, reel.Mouth, target.Centre, sp, seed, null, reel.Outward);
                            if (!lay.Ok) return "seed " + seed + ": " + lay.Reason;
                        }
                    }
                    finally { foreach (var (c, k) in held) w.SetBlocked(c, k); }
                    return null;
                }
                void Rect(CordWorld w, int x0, int z0, int wd, int ht, int band) { for (int x = x0; x < x0 + wd; x++) for (int z = z0; z < z0 + ht; z++) w.SetBand(C(x, z), band); }
                // C4: benches D1 > D2 > D3 (increments), the sump, the drain off the west edge; ramps carry the hose up each step
                var q = new CordWorld(70, 45);
                Rect(q, 4, 4, 32, 30, 1); Rect(q, 7, 7, 26, 24, 2); Rect(q, 10, 10, 20, 18, 3); Rect(q, 14, 14, 4, 4, 6); Rect(q, -12, 36, 16, 1, 1);
                q.SetExtraCost(C(13, 16), HoseMath.BuildingCrossCost);                      // the pump
                foreach (var (x, z) in new[] { (12, 12), (12, 13), (17, 17), (21, 12), (22, 12), (23, 12) }) q.SetBlocked(C(x, z), BlockKind.Wall);
                var reel4 = new HoseReelRect(11 + OX, 16, 2, 2) { Rot = 3, Look = "Industrial" };
                for (int x = 11; x <= 12; x++) for (int z = 16; z <= 17; z++) q.SetExtraCost(C(x, z), HoseMath.BuildingCrossCost);
                string noRamps = LayAll(q, reel4, C(3, 36));
                Assert(noRamps != null && noRamps.Contains("no route"), "can-fail: C4's hose climbed the benches with no ramps (" + (noRamps ?? "laid") + ")");
                foreach (var (lx, lz, hx, hz) in new[] { (10, 16, 9, 16), (7, 16, 6, 16), (4, 16, 3, 16), (3, 36, 3, 35), (20, 33, 20, 34) })
                    q.LinkBands(C(lx, lz), C(hx, hz));
                string c4 = LayAll(q, reel4, C(3, 36));
                Assert(c4 == null, "C4: the quarry hose did not lay up the ramps to the drain canal: " + c4);
                // C10: the pond hose (reel 14,37 to the pond at 10,33) and the fenced closed ledger (reel 39,5 to beside tank 33,3)
                var b = new CordWorld(70, 45);
                for (int x = 1; x < 13; x++) for (int z = 28; z < 36; z++) b.SetExtraCost(C(x, z), 3f);   // the pond: a hose floats
                foreach (var (x, z) in new[] { (8, 36), (9, 36), (8, 37), (9, 37) }) b.SetBlocked(C(x, z), BlockKind.Wall);
                b.SetExtraCost(C(6, 36), HoseMath.BuildingCrossCost);
                var reelPond = new HoseReelRect(14 + OX, 37, 2, 2) { Rot = 3 };
                string pond = LayAll(b, reelPond, C(10, 33));
                Assert(pond == null, "C10: the pond hose did not lay: " + pond);
                for (int x = 31; x <= 42; x++) { b.SetBlocked(C(x, 1), BlockKind.Wall); b.SetBlocked(C(x, 9), BlockKind.Wall); }
                for (int z = 1; z <= 9; z++) { b.SetBlocked(C(31, z), BlockKind.Wall); b.SetBlocked(C(42, z), BlockKind.Wall); }
                b.SetBlocked(C(36, 1), BlockKind.None);
                foreach (var (tx, tz) in C10LedgerTanks) for (int x = tx; x < tx + 2; x++) for (int z = tz; z < tz + 2; z++) b.SetBlocked(C(x, z), BlockKind.Wall);
                var reelLedger = new HoseReelRect(C10LedgerReel.Item1 + OX, C10LedgerReel.Item2, 2, 2) { Rot = 3 };
                string ledger = LayAll(b, reelLedger, C(C10LedgerEnd.Item1, C10LedgerEnd.Item2));
                Assert(ledger == null, "C10: the closed-ledger hose did not lay: " + ledger);
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

            Case("HoseBand_P2_pit_cover_carries_no_hose", () =>
            {
                // phase 7, the cover gap: StepDepthAt reads an intact cover as ground (band 0), so a hose was laid over it. The
                // rule is the P2 table's own Hose row: only a surface it REFUSES closes the square
                Assert(HoseBandMath.SurfaceClosed(true, LineSurface.Cover), "an intact pit cover carried a hose");
                foreach (LineSurface ok in new[] { LineSurface.SolidGround, LineSurface.Deck, LineSurface.RopeDeck, LineSurface.DrawbridgeLeaf, LineSurface.Excavated })
                    Assert(!HoseBandMath.SurfaceClosed(true, ok), "a hose was closed off " + ok + " (decks carry hoses; a dug square is the ramp/ladder rule)");
                Assert(!HoseBandMath.SurfaceClosed(false, LineSurface.Cover), "can-fail: the rules switch off still closed a cover");
                // routing: a covered trench (cover = closed, its pit under it band 4) full height, no ramp: no route over it
                CordWorld covered = Trench(10, 13);
                for (int x = 10; x <= 13; x++) for (int z = 0; z < H; z++) covered.SetBlocked(new Cell(x, z), BlockKind.Wall);
                Assert(HoseMath.CheckInstall(covered, Reel, new Cell(18, 7), Len) == "no route", "a hose crossed a covered trench");
                // can-fail: the pre-fix world (a cover read as band-0 ground, open) routes straight over it
                Assert(HoseMath.CheckInstall(new CordWorld(W, H), Reel, new Cell(18, 7), Len) == null, "can-fail: the old cover-as-ground world refused");
                // a laid hose that a new cover is built under: its corridor hash moves, so the 250-tick check re-plans or retracts
                var open0 = new CordWorld(W, H);
                HoseLay lay = HoseMath.Lay(open0, Reel.Mouth, new Cell(20, 7).Centre, new HoseShapeParams { MaxLength = Len }, 3);
                Assert(lay.Ok, "the open lay failed: " + lay.Reason);
                var cov = new CordWorld(W, H);
                for (int x = 10; x <= 12; x++) for (int z = 6; z <= 8; z++) { cov.SetBand(new Cell(x, z), 0); cov.SetBlocked(new Cell(x, z), BlockKind.Wall); }
                Assert(Corridor(open0, lay) != Corridor(cov, lay), "a cover built under a laid hose did not move its corridor");
                Assert(HoseMath.CheckReplan(cov, Reel, new Cell(20, 7), Len, false, null) == null, "a hose with a way round the cover was reeled in");
                // production wiring: the snapshot and the live per-cell read close the same squares
                string bands = Src("Hose", "RM_HoseBands.cs");
                string apply = Body(bands, "internal static void Apply(");
                Assert(apply.Contains("HoseBandMath.SurfaceClosed(true, RM_LineCrossing.SurfaceAt(map, c))") && apply.Contains("w.SetBlocked(new Cell(x, z), BlockKind.Wall)"),
                    "World() (RM_HoseBands.Apply) does not close a pit cover");
                Assert(Body(bands, "public static bool Closed(").Contains("HoseBandMath.SurfaceClosed(true, RM_LineCrossing.SurfaceAt(map, c))"), "RM_HoseBands.Closed is not the table rule");
                string live = Body(Src("Hose", "RM_MapComponent_Hoses.cs"), "internal ulong LiveCellSig(");
                Assert(live.Contains("RM_HoseBands.Closed(map, c)) walk = false"), "LiveCellSig does not close a pit cover (live and snapshot hashes would drift)");
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
