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
    /// cardinal to or under it, to a machine 8-way or under it; a machine touches a tank 8-way):
    ///   * pipeLinksIntoMachines (on): a pipe cell beside a tank or machine runs its arm on to the shared edge (the linked
    ///     atlas's join tile) instead of ending in a cap short of it. Pure mesh, no art of its own.
    ///   * joinFittings (OFF until the owner rules on the art): a flange where a pipe meets a tank or machine, a coupler where a
    ///     machine shares an edge with a tank, and a saddle (hose on a pipe) / flange (hose beside a pipe) at a hose's port.
    ///     Art: RimMandrake/FlowWorks/Joins/&lt;Look&gt;/{Flange,Coupler,Saddle}; until it is installed every piece draws the hose's
    ///     Coupling_Bare as a placeholder.
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

    /// <summary>pipeLinksIntoMachines: a pipe's linked atlas also links toward a tank or liquid machine beside it, so its arm
    /// reaches the shared edge (the net already counts that pipe as attached).</summary>
    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Graphic_Linked), nameof(Graphic_Linked.ShouldLinkWith))]
    internal static class Patch_Pipe_LinksIntoMachines
    {
        private static void Postfix(IntVec3 c, Thing parent, ref bool __result)
        {
            if (__result || !RM_MachinerySettings.pipeLinksIntoMachines || parent == null || !parent.Spawned) return;
            if (!RM_LiquidNet.IsPipe(parent)) return;
            if (RM_LiquidJoins.PartnerAt(c, parent.Map) != null) __result = true;
        }
    }

    /// <summary>A tank or machine spawning or leaving redraws the joins round it (the pipe arms and fittings beside it).</summary>
    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Building), nameof(Building.SpawnSetup))]
    internal static class Patch_Joins_Spawn
    {
        private static void Postfix(Building __instance, Map map)
        {
            if (RM_LiquidJoins.IsPartner(__instance)) RM_LiquidJoins.DirtyAround(map, __instance.OccupiedRect());
        }
    }

    [RimMandrake.Shared.PatchFeature("Universal pipe: joins", typeof(RM_MachinerySettings), "pipeLinksIntoMachines")]
    [HarmonyPatch(typeof(Building), nameof(Building.DeSpawn))]
    internal static class Patch_Joins_Despawn
    {
        private static void Prefix(Building __instance, out (Map map, CellRect rect) __state)
        {
            __state = RM_LiquidJoins.IsPartner(__instance) ? (__instance.Map, __instance.OccupiedRect()) : (null, default(CellRect));
        }

        private static void Postfix((Map map, CellRect rect) __state)
        {
            if (__state.map != null) RM_LiquidJoins.DirtyAround(__state.map, __state.rect);
        }
    }
}
