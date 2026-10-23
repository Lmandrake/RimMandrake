using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16): "The pipe needs connectors that show where it's connecting. Same
    /// thing if you build a pipe alongside a tank but not under it: the pipe looks like it doesn't even connect, but it should."
    /// The draw hooks for every liquid join, matching the net's own attach rules (RM_LiquidNetKernel: a pipe attaches to a tank
    /// 8-way around or under it, tank and machine alike (owner 2026-10-20); a machine touches a tank 8-way):
    ///   * pipeLinksIntoMachines (on): a pipe cell beside a tank or machine runs its arm on to the shared edge (the linked
    ///     atlas's join tile) instead of ending in a cap short of it. Pure mesh, no art of its own.
    ///   * joinFittings (ON: owner card 2026-10-22, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID): a flange where a pipe meets a tank or machine, a coupler where a
    ///     machine shares an edge with a tank, and a saddle (hose on a pipe) / flange (hose beside a pipe) at a hose's port.
    ///     Art: RimMandrake/FlowWorks/Joins/&lt;Look&gt;/{Flange,Coupler,Saddle}, installed for all four looks 2026-10-22; a
    ///     missing piece would draw the hose's Coupling_Bare as a placeholder.
    /// Geometry: LiquidJoinRule (Verse-free, selftested).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_LiquidJoins
    {
        public const string ArtRoot = "RimMandrake/FlowWorks/Joins/";
        public static readonly string[] Pieces = { "Flange", "Coupler", "Saddle" };
        private static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();

        /// <summary>State read: pieces drawn as the placeholder because their art is not installed.</summary>
        public static int placeholderPieces;

        /// <summary>The material of one piece in one look: the owned art when installed, else the hose coupling placeholder.</summary>
        public static Material Mat(string piece, string look)
        {
            look = PipeStyles.DefaultLook(look);
            string key = piece + "/" + look;
            if (mats.TryGetValue(key, out Material m)) return m;
            Texture2D t = ContentFinder<Texture2D>.Get(ArtRoot + look + "/" + piece, reportFailure: false);
            if (t == null)
            {
                placeholderPieces++;
                t = ContentFinder<Texture2D>.Get(Hose.HoseStyles.PathFor(look, "Coupling_Bare"), reportFailure: false)
                    ?? ContentFinder<Texture2D>.Get(Hose.HoseStyles.PathFor(Hose.HoseStyles.Scrapper, "Coupling_Bare"), reportFailure: false);
            }
            m = t == null ? null : MaterialPool.MatFrom(t, ShaderDatabase.Cutout, Color.white);
            mats[key] = m;
            return m;
        }

        /// <summary>A tank or liquid machine (never a pipe) a pipe joins, standing on cell c; null when none.</summary>
        public static Thing PartnerAt(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map)) return null;
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++)
            {
                RM_NetRole r = RM_LiquidNet.RoleOfKind(l[i]);
                if (r == RM_NetRole.Tank || r == RM_NetRole.Machine) return l[i];
            }
            return null;
        }

        /// <summary>PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID: true when the pipe on <paramref name="c"/> meets <paramref name="b"/> (the
        /// partner on c + d) as a riser onto the drawn flange: a 2x2 universal tank on the pipe's west or east (the one tank whose
        /// ports are measured, TankPortGeometry, as the hose's PortEnd). portZ = the flange's height, the hose's end point.</summary>
        public static bool RiserInto(IntVec3 c, IntVec3 d, Thing b, out double portZ)
        {
            portZ = 0;
            if (b == null || d.z != 0 || d.x == 0 || b.def.defName != Hose.TankPortGeometry.TankDef) return false;
            CellRect r = b.OccupiedRect();
            if (!Hose.TankPortGeometry.PortPoint(PipeLook.LookOfThing(b), r.minX, r.minZ, r.Width, r.Height, d.x, d.z, out var port)) return false;
            if (c.z < r.minZ || c.z > r.maxZ) return false;
            portZ = port.Z;
            return true;
        }

        /// <summary>D5 (joints study 2026-10-22): a built pipe pole (never its blueprint or frame) on cell c. The net already joins
        /// a pipe beside it (RM_PipePoles.JoinCells); without this the ground pipe ended in a cap half a cell short of the pole.</summary>
        public static bool PipePoleAt(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map)) return false;
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++)
            {
                if (IsPipePole(l[i])) return true;
            }
            return false;
        }

        public static bool IsPipePole(Thing t) =>
            t is Building && t.def.GetModExtension<RM_LineKindExtension>()?.kind == LineKind.PipePole;

        /// <summary>HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES (audit D6: a pipe ending beside a reel drew its dead-end cap in the gap
        /// and the reel's link stopped short of it): true when a hose reel on <paramref name="c"/> is coupled to
        /// <paramref name="pipe"/> (CompHoseReel.Port, re-read), so the pipe's arm runs on to the shared edge and the reel's link
        /// (HoseJoints.ReelFeed) carries it on from the pipe's centre line.</summary>
        public static bool ReelCoupledTo(IntVec3 c, Thing pipe)
        {
            Map map = pipe?.Map;
            if (map == null || !c.InBounds(map)) return false;
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++)
                if (l[i] is ThingWithComps tw && tw.GetComp<Hose.CompHoseReel>() is Hose.CompHoseReel r && r.Port(true) == pipe) return true;
            return false;
        }

        public static bool IsHoseReel(Thing t) => t is ThingWithComps tw && tw.GetComp<Hose.CompHoseReel>() != null;

        public static bool IsPartner(Thing t)
        {
            RM_NetRole r = RM_LiquidNet.RoleOfKind(t);
            return r == RM_NetRole.Tank || r == RM_NetRole.Machine;
        }

        /// <summary>The look a join on this thing draws in: a pipe's or tank's picked look, else the pipes' default.</summary>
        public static string LookOf(Thing t)
        {
            if (t != null && PipeLook.IsStyled(t.def)) return PipeLook.LookOfThing(t);
            return PipeLook.DefaultLook;
        }

        /// <summary>Redraw the join meshes round a tank's or machine's footprint (its partners may sit in a neighbouring section).</summary>
        public static void DirtyAround(Map map, CellRect rect)
        {
            if (map == null) return;
            foreach (IntVec3 c in rect.ExpandedBy(1).EdgeCells)
            {
                if (c.InBounds(map)) map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings, false, false);
            }
        }

        /// <summary>RM_MapComponent_Hoses.DrawEnds: the pipe-side fitting of a hose end coupled to a pipe. On the pipe (side 0,0):
        /// a saddle across the pipe cell, along the pipe's run. Beside it: a flange on the pipe cell's edge facing the hose end.</summary>
        public static void DrawHosePortFitting(Thing port, int sideX, int sideZ, float y)
        {
            if (!RM_MachinerySettings.joinFittings || port == null || !port.Spawned || !RM_LiquidNet.IsPipe(port)) return;
            Material m = Mat(sideX == 0 && sideZ == 0 ? "Saddle" : "Flange", LookOf(port));
            if (m == null) return;
            Vector3 c = port.Position.ToVector3Shifted();
            c.y = y;
            if (sideX == 0 && sideZ == 0)
            {
                Map map = port.Map;
                bool eastWest = RM_LiquidNet.HasPipe(port.Position + IntVec3.East, map) || RM_LiquidNet.HasPipe(port.Position + IntVec3.West, map);
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(c, Quaternion.Euler(0f, eastWest ? 0f : 90f, 0f),
                    new Vector3((float)LiquidJoinRule.SaddleLength, 1f, (float)LiquidJoinRule.SaddleWidth)), m, 0);
                return;
            }
            // the flange faces from the pipe toward the hose end: the end is at port - side, so the flange faces -side
            LiquidJoinRule.Flange(-sideX, -sideZ, out double ox, out double oz, out double ang);
            float s = (float)LiquidJoinRule.FlangeSize;
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(c + new Vector3((float)ox, 0f, (float)oz), Quaternion.Euler(0f, -(float)ang, 0f),
                new Vector3(s, 1f, s)), m, 0);
        }
    }

    /// <summary>The static join fittings: pipe-to-tank/machine flanges and machine-to-tank couplers, printed into the section
    /// mesh (rebuilt when a building in or beside the section changes). Nothing at all while joinFittings is off.</summary>
    public class SectionLayer_RM_LiquidJoins : SectionLayer
    {
        public SectionLayer_RM_LiquidJoins(Section section) : base(section)
        {
            relevantChangeTypes = MapMeshFlagDefOf.Buildings;
        }

        public override bool Visible => RM_MachinerySettings.joinFittings;

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            if (!RM_MachinerySettings.joinFittings)
            {
                FinalizeMesh(MeshParts.All);
                return;
            }
            Map map = Map;
            float yPipe = AltitudeLayer.FloorEmplacement.AltitudeFor() + 0.02f;
            float yTop = AltitudeLayer.BuildingOnTop.AltitudeFor();
            float s = (float)LiquidJoinRule.FlangeSize;
            foreach (IntVec3 c in section.CellRect)
            {
                List<Thing> l = c.GetThingList(map);
                for (int i = 0; i < l.Count; i++)
                {
                    Thing t = l[i];
                    if (RM_LiquidNet.IsPipe(t))
                    {
                        if (RM_LiquidJoins.PartnerAt(c, map) != null) continue;   // a pipe under a tank or machine: hidden, no flange
                        foreach (IntVec3 d in GenAdj.CardinalDirections)
                        {
                            if (RM_LiquidJoins.PartnerAt(c + d, map) == null) continue;
                            Material m = RM_LiquidJoins.Mat("Flange", RM_LiquidJoins.LookOf(t));
                            if (m == null) continue;
                            LiquidJoinRule.Flange(d.x, d.z, out double ox, out double oz, out double ang);
                            Vector3 p = c.ToVector3Shifted() + new Vector3((float)ox, 0f, (float)oz);
                            if (RM_MachinerySettings.pipeLinksIntoMachines && RM_LiquidJoins.RiserInto(c, d, RM_LiquidJoins.PartnerAt(c + d, map), out double pz))
                                p.z = (float)pz;   // PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID: on the riser's end, the drawn flange
                            p.y = yPipe;
                            Printer_Plane.PrintPlane(this, p, new Vector2(s, s), m, -(float)ang);
                        }
                    }
                    else if (t.Position == c && RM_LiquidNet.RoleOfKind(t) == RM_NetRole.Machine)
                    {
                        // a machine prints once (at its own position) a coupler on each edge it shares with a tank
                        CellRect a = t.OccupiedRect();
                        var seen = new HashSet<Thing>();
                        foreach (IntVec3 n in a.ExpandedBy(1).EdgeCells)
                        {
                            if (!n.InBounds(map)) continue;
                            List<Thing> nl = n.GetThingList(map);
                            for (int j = 0; j < nl.Count; j++)
                            {
                                Thing b = nl[j];
                                if (!(b is Building_LiquidTank) || !seen.Add(b)) continue;
                                CellRect br = b.OccupiedRect();
                                if (!LiquidJoinRule.SharedEdge(a.minX, a.minZ, a.Width, a.Height, br.minX, br.minZ, br.Width, br.Height,
                                        out double mx, out double mz, out int sx, out int sz)) continue;
                                Material m = RM_LiquidJoins.Mat("Coupler", RM_LiquidJoins.LookOf(b));
                                if (m == null) continue;
                                Printer_Plane.PrintPlane(this, new Vector3((float)mx, yTop, (float)mz), new Vector2(s, s), m,
                                    sx != 0 ? 0f : 90f);
                            }
                        }
                    }
                }
            }
            FinalizeMesh(MeshParts.All);
        }
    }

    /// <summary>
    /// PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (owner 2026-10-18): "draw pipes as though they are connected into the centers of all
    /// pipe-receiving items even if the actual pipe ends at the edge of their graphic (so that it appears to continue beneath
    /// them through any transparent boundaries they might have)." A pipe cell beside a tank or liquid machine (RM_LiquidJoins
    /// .PartnerAt: the net's own Tank/Machine roles, read from class and comps) prints its own straight tile on from the shared
    /// edge to the centre of the partner's footprint (LiquidJoinRule.CentreStub), at the pipe's altitude -- far below the
    /// building layer, so the building's opaque body hides it and its transparent margins show it. Section mesh: built once
    /// per change, nothing per frame. The pipe's arm to the edge is the link patch below (pipeLinksIntoMachines).
    /// </summary>
    public class SectionLayer_RM_PipeCentreStubs : SectionLayer
    {
        public SectionLayer_RM_PipeCentreStubs(Section section) : base(section)
        {
            relevantChangeTypes = MapMeshFlagDefOf.Buildings;
        }

        public override bool Visible => RM_MachinerySettings.pipesUnderToCentre || RM_MachinerySettings.pipeLinksIntoMachines;

        /// <summary>State read: riser polylines printed by the last regeneration of any section (PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID).</summary>
        public static int lastRisers;

        /// <summary>State read: stub pieces printed by the last regeneration of any section (probe / live look).</summary>
        public static int lastPieces;

        private static readonly Vector2[] uvs = new Vector2[4];

        /// <summary>The pipe's straight tile (east-west or north-south) from its own linked atlas, in its own look; null when the
        /// pipe's graphic is not an atlas.</summary>
        public static Material StraightMat(Thing pipe, bool eastWest)
        {
            Graphic g = pipe.Graphic;
            Material atlas = g is Graphic_Linked gl && gl.SubGraphic != null ? gl.SubGraphic.MatSingleFor(pipe) : g?.MatSingleFor(pipe);
            if (atlas == null) return null;
            return MaterialAtlasPool.SubMaterialFromAtlas(atlas, eastWest ? LinkDirections.Left | LinkDirections.Right : LinkDirections.Up | LinkDirections.Down);
        }

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            bool under = RM_MachinerySettings.pipesUnderToCentre, risers = RM_MachinerySettings.pipeLinksIntoMachines;
            if (!under && !risers)
            {
                FinalizeMesh(MeshParts.All);
                return;
            }
            Map map = Map;
            float y = AltitudeLayer.FloorEmplacement.AltitudeFor() - 0.002f;
            int n = 0, nr = 0;
            foreach (IntVec3 c in section.CellRect)
            {
                List<Thing> l = c.GetThingList(map);
                for (int i = 0; i < l.Count; i++)
                {
                    Thing t = l[i];
                    if (!RM_LiquidNet.IsPipe(t)) continue;
                    if (RM_LiquidJoins.PartnerAt(c, map) != null) break;   // a pipe under a tank or machine is hidden already
                    // FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE: a pipe joins any tank or machine across a corner too (the net is
                    // 8-way for every member), so it draws its under-run to the centre from there as well (CornerStub)
                    for (int di = 0; di < 8; di++)
                    {
                        IntVec3 d = di < 4 ? GenAdj.CardinalDirections[di] : GenAdj.DiagonalDirections[di - 4];
                        Thing b = RM_LiquidJoins.PartnerAt(c + d, map);
                        if (b == null) continue;
                        CellRect r = b.OccupiedRect();
                        double[] poly;
                        if (di < 4 && risers && RM_LiquidJoins.RiserInto(c, d, b, out double portZ))
                        {
                            poly = LiquidJoinRule.RiserStub(c.x, c.z, d.x, d.z, r.minX, r.minZ, r.Width, r.Height, portZ, under);
                            nr++;
                        }
                        else if (!under) continue;
                        else poly = di < 4 ? LiquidJoinRule.CentreStub(c.x, c.z, d.x, d.z, r.minX, r.minZ, r.Width, r.Height)
                            : LiquidJoinRule.CornerStub(c.x, c.z, d.x, d.z, r.minX, r.minZ, r.Width, r.Height);
                        foreach (LiquidJoinRule.StubPiece p in LiquidJoinRule.StubPieces(poly))
                        {
                            Material m = StraightMat(t, p.EastWest);
                            if (m == null) continue;
                            float u0 = (float)p.U0, u1 = (float)p.U1, len = (float)p.Length;
                            if (p.EastWest)
                            {
                                uvs[0] = new Vector2(u0, 0f); uvs[1] = new Vector2(u0, 1f); uvs[2] = new Vector2(u1, 1f); uvs[3] = new Vector2(u1, 0f);
                            }
                            else
                            {
                                uvs[0] = new Vector2(0f, u0); uvs[1] = new Vector2(0f, u1); uvs[2] = new Vector2(1f, u1); uvs[3] = new Vector2(1f, u0);
                            }
                            Printer_Plane.PrintPlane(this, new Vector3((float)p.X, y, (float)p.Z),
                                p.EastWest ? new Vector2(len, 1f) : new Vector2(1f, len), m, 0f, false, uvs, null, 0f);
                            n++;
                        }
                    }
                    break;
                }
            }
            lastPieces = n;
            lastRisers = nr;
            FinalizeMesh(MeshParts.All);
        }
    }

    /// <summary>pipeLinksIntoMachines: a pipe's linked atlas also links toward a tank or liquid machine beside it, so its arm
    /// reaches the shared edge (the net already counts that pipe as attached). D5 (2026-10-22): and toward a pipe pole.</summary>
    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Graphic_Linked), nameof(Graphic_Linked.ShouldLinkWith))]
    internal static class Patch_Pipe_LinksIntoMachines
    {
        private static void Postfix(IntVec3 c, Thing parent, ref bool __result)
        {
            if (__result || !RM_MachinerySettings.pipeLinksIntoMachines || parent == null || !parent.Spawned) return;
            if (!RM_LiquidNet.IsPipe(parent)) return;
            Thing partner = RM_LiquidJoins.PartnerAt(c, parent.Map);
            // PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID: a pipe meeting a 2x2 tank's flange stops its own arm at its centre; the riser
            // (SectionLayer_RM_PipeCentreStubs) carries it to the flange's height and on to the flange
            if (partner != null && RM_LiquidJoins.RiserInto(parent.Position, c - parent.Position, partner, out _)) return;
            if (RM_LiquidJoins.PartnerAt(c, parent.Map) != null
                || (RM_MachinerySettings.pipePolesEnabled && RM_LiquidJoins.PipePoleAt(c, parent.Map))
                || RM_LiquidJoins.ReelCoupledTo(c, parent)) __result = true;
        }
    }

    /// <summary>A tank or machine spawning or leaving redraws the joins round it (the pipe arms and fittings beside it).</summary>
    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Building), nameof(Building.SpawnSetup))]
    internal static class Patch_Joins_Spawn
    {
        private static void Postfix(Building __instance, Map map)
        {
            if (RM_LiquidJoins.IsPartner(__instance) || RM_LiquidJoins.IsPipePole(__instance) || RM_LiquidJoins.IsHoseReel(__instance)) RM_LiquidJoins.DirtyAround(map, __instance.OccupiedRect());
        }
    }

    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Building), nameof(Building.DeSpawn))]
    internal static class Patch_Joins_Despawn
    {
        private static void Prefix(Building __instance, out (Map map, CellRect rect) __state)
        {
            __state = RM_LiquidJoins.IsPartner(__instance) || RM_LiquidJoins.IsPipePole(__instance) || RM_LiquidJoins.IsHoseReel(__instance) ? (__instance.Map, __instance.OccupiedRect()) : (null, default(CellRect));
        }

        private static void Postfix((Map map, CellRect rect) __state)
        {
            if (__state.map != null) RM_LiquidJoins.DirtyAround(__state.map, __state.rect);
        }
    }
}
