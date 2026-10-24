// HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16): offline halves of the liquid-join draw hooks -- LiquidJoinRule's
// geometry, the hose thickness scale, and the shipped wiring (settings defaults, the section layer, the link patch).
// NOT proven here: the meshes on a map (validation.py rows owed when the art lands).
using System;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LiquidJoinChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Near(double a, double b) => Math.Abs(a - b) < 1e-9;

        public static void Run(Action<string, Action> Case)
        {
            Case("LiquidJoin_flange_face_on_the_shared_edge", () =>
            {
                foreach (var (dx, dz, ang) in new[] { (1, 0, 0.0), (0, 1, 90.0), (-1, 0, 180.0), (0, -1, 270.0) })
                {
                    LiquidJoinRule.Flange(dx, dz, out double ox, out double oz, out double a);
                    // the flange's face = centre + half its size along the facing direction = the cell edge (0.5 from centre)
                    // signed: a flange on the opposite edge (same |offset|) must fail
                    Assert(Near(ox + dx * LiquidJoinRule.FlangeSize / 2, dx * 0.5) && Near(oz + dz * LiquidJoinRule.FlangeSize / 2, dz * 0.5),
                        $"flange ({dx},{dz}) face on the cell edge, got ({ox},{oz})");
                    Assert(Near(a, ang), $"flange ({dx},{dz}) faces {ang}, got {a}");
                }
                bool threw = false;
                try { LiquidJoinRule.Flange(1, 1, out _, out _, out _); } catch (ArgumentException) { threw = true; }
                Assert(threw, "can-fail: a diagonal flange is refused");
            });
            Case("LiquidJoin_on_pipe_fixture_is_not_a_partner", () =>
            {
                // SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW: a sprinkler head on a pipe is part of the run (no flange band beside it)
                Assert(!LiquidJoinRule.JoinsAsPartner(true, true), "a head standing on its pipe is not a join partner");
                Assert(LiquidJoinRule.JoinsAsPartner(true, false), "can-fail: a head whose pipe is gone still reads as a partner");
                Assert(LiquidJoinRule.JoinsAsPartner(false, true) && LiquidJoinRule.JoinsAsPartner(false, false),
                    "a tank or machine is a partner whether or not a pipe runs under it");
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(joins.Contains("LiquidJoinRule.JoinsAsPartner(IsOnPipeFixture(l[i]), RM_LiquidNet.HasPipe(c, map))")
                       && joins.Contains("typeof(Sprinklers.PlaceWorker_RM_OnPipe)"), "PartnerAt applies the rule to on-pipe fixtures");
            });
            Case("LiquidJoin_shared_edge", () =>
            {
                // pump 1x1 at (5,5), 2x2 tank east of it at (6,5): shared edge x=6, z 5..6, side east
                Assert(LiquidJoinRule.SharedEdge(5, 5, 1, 1, 6, 5, 2, 2, out double mx, out double mz, out int sx, out int sz)
                       && Near(mx, 6) && Near(mz, 5.5) && sx == 1 && sz == 0, $"east edge, got ({mx},{mz}) side ({sx},{sz})");
                // tank north of a 2x1 pump, offset by one: overlap x 6..7
                Assert(LiquidJoinRule.SharedEdge(5, 5, 2, 1, 6, 6, 2, 2, out mx, out mz, out sx, out sz)
                       && Near(mx, 6.5) && Near(mz, 6) && sx == 0 && sz == 1, $"north edge, got ({mx},{mz}) side ({sx},{sz})");
                Assert(LiquidJoinRule.SharedEdge(6, 5, 2, 2, 5, 5, 1, 1, out mx, out _, out sx, out _) && sx == -1 && Near(mx, 6), "west edge");
                Assert(LiquidJoinRule.SharedEdge(5, 7, 1, 1, 5, 5, 2, 2, out _, out mz, out _, out sz) && sz == -1 && Near(mz, 7), "south edge");
                // can-fail: corner-only touch, a gap, an overlap
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 1, 1, 6, 6, 2, 2, out _, out _, out _, out _), "corner touch has no edge");
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 1, 1, 7, 5, 2, 2, out _, out _, out _, out _), "a gap has no edge");
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 2, 2, 6, 6, 2, 2, out _, out _, out _, out _), "an overlap has no edge");
            });
            Case("LiquidJoin_hose_thickness_scale", () =>
            {
                double was = HoseMath.WidthScale;
                try
                {
                    HoseMath.WidthScale = 1.0;
                    double w0 = HoseMath.VisibleWidth(0, 1), w1 = HoseMath.VisibleWidth(1, 1);
                    // owner 2026-10-22: "Hoses need to be twice as thick" -- the default hose is 0.16-0.20 cell flat
                    Assert(w0 >= 0.16 && w0 <= 0.20, "the default flat hose is 0.16-0.20 cell (" + w0.ToString("0.000") + ")");
                    Assert(w1 > w0 && w1 < 0.26, "the default plump hose is swollen over flat, under 0.26 (" + w1.ToString("0.000") + ")");
                    HoseMath.WidthScale = 0.75;
                    Assert(Near(HoseMath.VisibleWidth(0, 1), w0 * 0.75) && Near(HoseMath.VisibleWidth(1, 1), w1 * 0.75), "the scale reaches every width");
                }
                finally { HoseMath.WidthScale = was; }
            });
            Case("LiquidJoin_wiring_shipped", () =>
            {
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                string set = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_MachinerySettings.cs"));
                string hs = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_HoseSettings.cs"));
                string draw = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                Assert(set.Contains("public static bool joinFittings = true;") && set.Contains("\"joinFittings\", true"),
                    "connector fittings ship ON (owner card 2026-10-22: fittings installed)");
                Assert(set.Contains("public static bool pipeLinksIntoMachines = true;"), "pipes link into tanks/machines by default");
                Assert(hs.Contains("public static float thickness = 1f;") && hs.Contains("\"hose_thickness\", 1f"), "hose thickness ships at 1");
                Assert(hs.Contains("\"|T\" + thickness"), "a thickness change re-lays every hose (ShapeFingerprint)");
                Assert(joins.Contains("class SectionLayer_RM_LiquidJoins : SectionLayer") && joins.Contains("nameof(Graphic_Linked.ShouldLinkWith)"),
                    "the section layer and the pipe link patch are shipped");
                Assert(draw.Contains("RM_LiquidJoins.DrawHosePortFitting(fe.Port"), "the hose port draws the pipe's fitting");
            });
            // PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (owner 2026-10-18): a pipe or hose beside a tank or machine is drawn on beneath it
            // to the centre of its footprint
            Case("PipeStub_1x1_runs_edge_to_centre", () =>
            {
                foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    // pipe at (5,5), 1x1 pump on its (dx,dz) side
                    double[] p = LiquidJoinRule.CentreStub(5, 5, dx, dz, 5 + dx, 5 + dz, 1, 1);
                    Assert(p != null && p.Length == 4, $"({dx},{dz}): a straight 2-point stub");
                    Assert(Near(p[0], 5.5 + dx * 0.5) && Near(p[1], 5.5 + dz * 0.5), $"({dx},{dz}): starts on the shared edge, got ({p[0]},{p[1]})");
                    Assert(Near(p[2], 5.5 + dx) && Near(p[3], 5.5 + dz), $"({dx},{dz}): ends at the pump's centre, got ({p[2]},{p[3]})");
                    var pcs = LiquidJoinRule.StubPieces(p);
                    Assert(pcs.Count == 1 && Near(pcs[0].Length, 0.5) && pcs[0].EastWest == (dx != 0)
                           && Near(pcs[0].U0, 0.25) && Near(pcs[0].U1, 0.75), $"({dx},{dz}): one half-cell slice of the straight tile");
                }
            });
            Case("PipeStub_multicell_enters_at_edge_then_turns_to_centre", () =>
            {
                // 2x2 tank at (6,5)-(7,6); pipe at (5,5) west of its lower-left cell: in to x=7 at z=5.5, then up to (7,6)
                double[] p = LiquidJoinRule.CentreStub(5, 5, 1, 0, 6, 5, 2, 2);
                Assert(p != null && p.Length == 6, "off the centre line: 3-point stub");
                Assert(Near(p[0], 6) && Near(p[1], 5.5) && Near(p[2], 7) && Near(p[3], 5.5) && Near(p[4], 7) && Near(p[5], 6),
                    $"edge (6,5.5) -> (7,5.5) -> centre (7,6), got {string.Join(",", p)}");
                var pcs = LiquidJoinRule.StubPieces(p);
                Assert(pcs.Count == 2 && pcs[0].EastWest && Near(pcs[0].Length, 1) && !pcs[1].EastWest && Near(pcs[1].Length, 0.5),
                    "one full east-west tile then a half north-south slice");
                // 3x1 converter south of a pipe at (4,8): pipe over the middle cell, straight down to (4.5, 7.5)
                double[] q = LiquidJoinRule.CentreStub(4, 8, 0, -1, 3, 7, 3, 1);
                Assert(q != null && q.Length == 4 && Near(q[2], 4.5) && Near(q[3], 7.5), "on the centre line: straight in");
                // a 3x3 entered from the west: 1.5 cells deep = a full tile and a half slice
                var r = LiquidJoinRule.StubPieces(LiquidJoinRule.CentreStub(0, 1, 1, 0, 1, 0, 3, 3));
                Assert(r.Count == 2 && Near(r[0].Length + r[1].Length, 1.5), "1.5 cells deep in two pieces");
                // can-fail: an end that does not face the footprint draws nothing
                Assert(LiquidJoinRule.CentreStub(5, 5, 1, 0, 6, 7, 2, 2) == null, "can-fail: not facing the footprint -> null");
                bool threw = false;
                try { LiquidJoinRule.CentreStub(5, 5, 1, 1, 6, 6, 1, 1); } catch (ArgumentException) { threw = true; }
                Assert(threw, "can-fail: a diagonal stub is refused");
            });
            // FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE (he typed 2026-10-20: "A solid pipe must only be adjacent and is then drawn
            // undernead to the center of the object as ruled previously."): a pipe joined across a corner runs under to the centre too
            Case("PipeStub_corner_adjacent_runs_under_to_centre", () =>
            {
                // 1x1 pump at (6,6); pipe at (5,5) on its south-west corner: east to x=6.5, then north to the centre (6.5,6.5)
                double[] p = LiquidJoinRule.CornerStub(5, 5, 1, 1, 6, 6, 1, 1);
                Assert(p != null && p.Length == 6, "an elbow: 3 points");
                Assert(Near(p[0], 6) && Near(p[1], 5.5) && Near(p[2], 6.5) && Near(p[3], 5.5) && Near(p[4], 6.5) && Near(p[5], 6.5),
                    $"(6,5.5) -> (6.5,5.5) -> centre (6.5,6.5), got {string.Join(",", p)}");
                // every corner of a 1x1 ends at its centre
                foreach (var (dx, dz) in new[] { (1, 1), (1, -1), (-1, 1), (-1, -1) })
                {
                    double[] q = LiquidJoinRule.CornerStub(5, 5, dx, dz, 5 + dx, 5 + dz, 1, 1);
                    Assert(q != null && Near(q[q.Length - 2], 5.5 + dx) && Near(q[q.Length - 1], 5.5 + dz), $"({dx},{dz}): ends at the centre");
                }
                // a 2x2 machine at (6,6)-(7,7), pipe at its south-west corner (5,5): elbow then sideways to (7,7)
                double[] m = LiquidJoinRule.CornerStub(5, 5, 1, 1, 6, 6, 2, 2);
                Assert(m != null && m.Length == 8 && Near(m[6], 7) && Near(m[7], 7), "multi-cell: on to the footprint's centre");
                Assert(LiquidJoinRule.CornerStub(5, 5, 1, 1, 6, 5, 2, 2) == null, "edge-adjacent too: CentreStub draws it, not the corner");
                Assert(LiquidJoinRule.CornerStub(5, 5, 1, 1, 8, 8, 1, 1) == null, "not touching: nothing");
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(joins.Contains(": LiquidJoinRule.CornerStub(c.x, c.z, d.x, d.z, r.minX, r.minZ, r.Width, r.Height);"), "can-fail: the layer prints corner stubs");
            });
            // the same ruling for every object, tanks included: "A solid pipe must only be adjacent and is then drawn undernead
            // to the center of the object"
            Case("PipeStub_tank_corner_joins_and_runs_under", () =>
            {
                string net = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidNet.cs"));
                Assert(net.Contains("IEnumerable<IntVec3> around = GenAdj.CellsAdjacent8Way(t);"), "every member, tank included, attaches 8-way");
                Assert(!net.Contains("RM_NetRole.Tank ? GenAdj.CellsAdjacentCardinal(t)"), "can-fail: a tank is no longer cardinal-only");
                Assert(net.Contains("return ThingsIn(GenAdj.CellsAdjacent8Way(c, Rot4.North, IntVec2.One).Concat(new[] { c }), null, RM_NetRole.Tank).Distinct();"),
                    "a pipe finds a tank across a corner (the mirror)");
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(!joins.Contains("RoleOfKind(b) != RM_NetRole.Machine) continue;"), "can-fail: the corner run is drawn for tanks too");
                // a 2x2 tank at (6,6): a pipe at its north-east corner (8,8) elbows west then south to (7,7)
                double[] t = LiquidJoinRule.CornerStub(8, 8, -1, -1, 6, 6, 2, 2);
                Assert(t != null && Near(t[t.Length - 2], 7) && Near(t[t.Length - 1], 7), "a tank's corner pipe runs under to its centre");
            });
            // TANK_FLANGE_FIX_HOVERS_MID_PIPE (live 2026-10-22, C3 north: the flange of a pipe entering the universal tank from the
            // south hung ~0.46 cell below the drawn skid, mid-pipe): every tank, look, side and lane puts the flange's face on the
            // DRAWN outline (TankArtEdges, pinned to the art by FlowWorks/selftest_tank_art_edges.py), or draws none when the
            // sprite covers the whole pipe cell
            Case("TankFlange_sits_on_the_drawn_edge_every_tank_look_side_lane", () =>
            {
                int checkedN = 0, hidden = 0;
                foreach (string tank in TankArtEdges.Tanks)
                    foreach (string look in TankArtEdges.Looks)
                        foreach (var (dx, dz) in new[] { (0, 1), (0, -1), (1, 0), (-1, 0) })
                            for (int lane = 0; lane < 2; lane++)
                            {
                                // a 2x2 tank at (10,10)-(11,11); the pipe cell on the side the step (dx,dz) enters, on this lane
                                int cx = dz != 0 ? 10 + lane : dx == 1 ? 9 : 12, cz = dx != 0 ? 10 + lane : dz == 1 ? 9 : 12;
                                Assert(TankArtEdges.TryInset(tank, look, dx, dz, lane, out double inset), $"{tank} {look}: measured");
                                // the drawn outline on the pipe's centre line, world cells
                                double edgeX = dx == 1 ? 10 : dx == -1 ? 12 : 0, edgeZ = dz == 1 ? 10 : dz == -1 ? 12 : 0;
                                double artX = edgeX + dx * inset, artZ = edgeZ + dz * inset;
                                bool drawn = LiquidJoinRule.FlangeOnArt(dx, dz, inset, out double ox, out double oz, out double ang);
                                if (!drawn)
                                {
                                    // hidden only when the outline lies at or beyond the pipe cell's far side
                                    Assert(inset <= -1 + 1e-6, $"{tank} {look} ({dx},{dz}) lane {lane}: no flange though the outline is in the pipe cell (inset {inset:0.000})");
                                    hidden++;
                                    continue;
                                }
                                double fx = cx + 0.5 + ox + dx * LiquidJoinRule.FlangeSize / 2, fz = cz + 0.5 + oz + dz * LiquidJoinRule.FlangeSize / 2;
                                Assert(dx != 0 ? Near(fx, artX) && Near(fz, cz + 0.5) : Near(fz, artZ) && Near(fx, cx + 0.5),
                                    $"{tank} {look} ({dx},{dz}) lane {lane}: face ({fx:0.000},{fz:0.000}) on the drawn edge ({(dx != 0 ? artX : cx + 0.5):0.000},{(dz != 0 ? artZ : cz + 0.5):0.000})");
                                Assert(Near(ang, dx == 1 ? 0 : dz == 1 ? 90 : dx == -1 ? 180 : 270), "faces the tank");
                                checkedN++;
                            }
                Assert(checkedN + hidden == 4 * 4 * 4 * 2, "every tank x look x side x lane");
                // can-fail, pinned to the live capture: the Scrapper universal tank's skid is ~0.46 above its footprint, so the
                // south flange's centre sits 0.5 + 0.46 - 0.25 from the pipe's centre -- the old footprint-edge rule put it at 0.25
                Assert(TankArtEdges.TryInset("RM_LiquidTank", "Scrapper", 0, 1, 0, out double sc) && sc > 0.40 && sc < 0.50, "Scrapper south inset ~0.46");
                LiquidJoinRule.FlangeOnArt(0, 1, sc, out _, out double soz, out _);
                LiquidJoinRule.Flange(0, 1, out _, out double oldOz, out _);
                Assert(soz > oldOz + 0.4, $"can-fail: the south flange moved up onto the skid ({soz:0.000} vs the footprint edge's {oldOz:0.000})");
                // the extra-tall tank overhangs its north pipe cell entirely: no flange there
                Assert(TankArtEdges.TryInset("RM_UniversalCargoTankXTall", "Scrapper", 0, -1, 0, out double xn) && !LiquidJoinRule.FlangeOnArt(0, -1, xn, out _, out _, out _),
                    "XTall north: the sprite covers the pipe cell, no flange");
                Assert(!TankArtEdges.TryInset("RM_LiquidPump", "Scrapper", 0, 1, 0, out _), "can-fail: an unmeasured building keeps the footprint edge");
                // an unstyled tank reads the def's own (Scrapper) art
                Assert(TankArtEdges.TryInset("RM_LiquidTank", null, 0, 1, 0, out double un) && Near(un, sc), "unstyled = Scrapper");
                // without the under-run, the arm reaches on to the outline; nothing when the outline is on/outside the edge
                double[] reach = LiquidJoinRule.ReachStub(10, 9, 0, 1, sc);
                Assert(reach != null && Near(reach[1], 10) && Near(reach[3], 10 + sc) && Near(reach[0], 10.5) && Near(reach[2], 10.5), "reach: edge to outline");
                Assert(LiquidJoinRule.ReachStub(10, 12, 0, -1, -0.6) == null, "no reach into an overhang");
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(joins.Contains("LiquidJoinRule.FlangeOnArt(d.x, d.z, riser ? 0 : RM_LiquidJoins.DrawnInset(c, d, b)"),
                    "can-fail: the section layer prints the flange on the drawn outline");
                Assert(joins.Contains("poly = LiquidJoinRule.ReachStub(c.x, c.z, d.x, d.z, RM_LiquidJoins.DrawnInset(c, d, b));"), "the stub layer carries the arm to it");
            });
            // C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE (map R C1, 2026-10-22): a pipe past a tank's corner whose own run already meets
            // the tank along an edge drew a second, dead-end elbow under the tall tank's see-through margin
            Case("PipeStub_corner_elbow_only_when_not_joined_beside", () =>
            {
                Assert(LiquidJoinRule.CornerStubWanted(false, false), "a pipe touching only the corner draws its elbow (owner 2026-10-20)");
                Assert(!LiquidJoinRule.CornerStubWanted(false, true) && !LiquidJoinRule.CornerStubWanted(true, false),
                    "can-fail: a pipe beside it on the tank's edge already draws the join");
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(joins.Contains("di >= 4 && !LiquidJoinRule.CornerStubWanted(PipeOn(new IntVec3(c.x + d.x, 0, c.z), map),"),
                    "the stub layer asks before printing an elbow");
            });
            Case("PipeStub_wiring_shipped", () =>
            {
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                string set = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_MachinerySettings.cs"));
                string draw = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                Assert(set.Contains("public static bool pipesUnderToCentre = true;") && set.Contains("\"pipesUnderToCentre\", true"),
                    "the under-building run ships ON");
                Assert(joins.Contains("class SectionLayer_RM_PipeCentreStubs : SectionLayer") && joins.Contains("LiquidJoinRule.CentreStub("),
                    "pipes: the section layer prints the stub");
                Assert(draw.Contains("DrawPortStub(r, fe,") && draw.Contains("stubMeshes"), "hoses: the port stub is drawn from a cached mesh");
            });
        }
    }
}
