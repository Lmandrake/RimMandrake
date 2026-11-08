using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Patches
{
    [StaticConstructorOnStartup]
    public static class SouthDrawsFrontStartup
    {
        static SouthDrawsFrontStartup() => SouthDrawsFrontPatches.Install();
    }

    // The Harmony half of RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES (math and measurements: SouthDrawsFrontKernel.cs).
    //   * Pawns: Pawn_DrawTracker.DrawPos's read of SeededYOffset is routed to SouthDrawsFrontPawn.OrderedYOffset.
    //   * Buildings and plants: SectionLayer_ThingsGeneral.TakePrintFrom names the thing being printed; every
    //     Printer_Plane.PrintPlane call it makes is lifted by how far south the thing stands, flat (no tilt).
    //     Map-mesh rebuilds only, never per frame. Moved here from BiomesShell's RM_PlantDrawOrder (which applied to
    //     plants in our biomes only); this is the one home of the rule.
    // NOT covered: a pawn against a tall building or tree. Pawns sit on the Pawn layer, two layers above every
    // building and plant, so a pawn standing north of a tree still draws over its canopy (vanilla's choice).
    public static class SouthDrawsFrontPatches
    {
        public const string HarmonyId = "mandrake.rm.patches.southdrawsfront";
        public const string LogTag = "[RimMandrake Patches] south draws front:";

        private static bool installed;
        private static bool pawnRouted, printRouted;
        private static readonly float commonAltitude = ((AltitudeLayer)SouthDrawsFrontKernel.CommonLayer).AltitudeFor();

        // The thing SectionLayer_ThingsGeneral is printing, and what its quads get. ThreadStatic: a print on another
        // thread never reads this one's thing.
        [ThreadStatic] private static Thing printing;
        [ThreadStatic] private static bool printingPlant;
        [ThreadStatic] private static float printingLift;
        [ThreadStatic] private static int printingMapZ;

        public static string Status
        {
            get
            {
                if (!RM_PatchesSettings.southDrawsFront)
                    return "Off: vanilla draw order (pawns by a random seed, printed things by their size).";
                return "Pawns " + (pawnRouted ? "ordered" : "NOT patched") + "; buildings and plants "
                    + (printRouted ? "ordered" : "NOT patched") + ".";
            }
        }

        public static void Install()
        {
            if (installed)
                return;
            installed = true;
            var harmony = new Harmony(HarmonyId);
            try
            {
                MethodInfo drawPos = AccessTools.PropertyGetter(typeof(Pawn_DrawTracker), nameof(Pawn_DrawTracker.DrawPos));
                harmony.Patch(drawPos, transpiler: new HarmonyMethod(typeof(SouthDrawsFrontPatches), nameof(DrawPosTranspiler)));
            }
            catch (Exception e)
            {
                Log.Error(LogTag + " could not patch Pawn_DrawTracker.DrawPos: " + e.Message + ". Pawns keep vanilla order.");
            }
            try
            {
                harmony.Patch(AccessTools.Method(typeof(SectionLayer_ThingsGeneral), "TakePrintFrom"),
                    prefix: new HarmonyMethod(typeof(SouthDrawsFrontPatches), nameof(TakePrintFromPrefix)),
                    postfix: new HarmonyMethod(typeof(SouthDrawsFrontPatches), nameof(TakePrintFromPostfix)));
                harmony.Patch(AccessTools.Method(typeof(Printer_Plane), nameof(Printer_Plane.PrintPlane)),
                    prefix: new HarmonyMethod(typeof(SouthDrawsFrontPatches), nameof(PrintPlanePrefix)));
                printRouted = true;
            }
            catch (Exception e)
            {
                Log.Error(LogTag + " could not patch the thing printer: " + e.Message + ". Buildings and plants keep vanilla order.");
            }
            Log.Message(LogTag + " " + Status);
        }

        public static IEnumerable<CodeInstruction> DrawPosTranspiler(IEnumerable<CodeInstruction> instructions)
        {
            MethodInfo seeded = AccessTools.PropertyGetter(typeof(Pawn_DrawTracker), nameof(Pawn_DrawTracker.SeededYOffset));
            FieldInfo pawnField = AccessTools.Field(typeof(Pawn_DrawTracker), "pawn");
            MethodInfo ours = AccessTools.Method(typeof(SouthDrawsFrontPawn), nameof(SouthDrawsFrontPawn.OrderedYOffset));
            int replaced = 0;
            foreach (CodeInstruction ins in instructions)
            {
                if (pawnField != null && ins.Calls(seeded))
                {
                    // Stack holds the tracker; add its pawn and call ours (tracker, pawn) -> float, as the getter did.
                    yield return new CodeInstruction(OpCodes.Ldarg_0) { labels = ins.labels, blocks = ins.blocks };
                    yield return new CodeInstruction(OpCodes.Ldfld, pawnField);
                    yield return new CodeInstruction(OpCodes.Call, ours);
                    replaced++;
                    continue;
                }
                yield return ins;
            }
            pawnRouted = replaced == 1;
            if (replaced != 1)
                Log.Error(LogTag + " expected one SeededYOffset read in Pawn_DrawTracker.DrawPos, found " + replaced
                    + (pawnField == null ? " (no pawn field)" : "") + ". Pawns keep vanilla order.");
        }

        public static void TakePrintFromPrefix(Thing t)
        {
            printing = null;
            if (!RM_PatchesSettings.southDrawsFront || t?.def == null)
                return;
            Map map = t.Map;
            if (map == null)
                return;
            int layer = (int)t.def.altitudeLayer;
            if (t is Plant)
            {
                if (layer < SouthDrawsFrontKernel.PlantMinLayer || layer > SouthDrawsFrontKernel.CommonLayer)
                    return;
                printingPlant = true;
            }
            else
            {
                if (layer < SouthDrawsFrontKernel.BuildingMinLayer || layer > SouthDrawsFrontKernel.CommonLayer)
                    return;
                printingPlant = false;
                // Every quad of one building shares its footprint's south edge, so its own parts keep their order.
                printingLift = SouthDrawsFrontKernel.PrintOffset(t.OccupiedRect().minZ, map.Size.z);
            }
            printingMapZ = map.Size.z;
            printing = t;
        }

        public static void TakePrintFromPostfix()
        {
            printing = null;
        }

        public static void PrintPlanePrefix(ref Vector3 center, Vector2 size, ref float topVerticesAltitudeBias)
        {
            Thing t = printing;
            if (t == null)
                return;
            if (printingPlant)
            {
                // A plant prints each quad on the common layer at the depth of that quad's own foot, whatever its
                // donor layer and size (the 2026-10-16 plant rule, now game-wide).
                float carried = center.y - t.def.Altitude;
                if (carried > SouthDrawsFrontKernel.MaxCarriedOffset || carried < -SouthDrawsFrontKernel.MaxCarriedOffset)
                    carried = 0f;
                float foot = SouthDrawsFrontKernel.PlantFoot(center.z, size.y, t.def.graphicData?.drawSize.x ?? 1f);
                center.y = commonAltitude + SouthDrawsFrontKernel.PrintOffset(foot, printingMapZ) + carried;
            }
            else
            {
                center.y += printingLift;
            }
            topVerticesAltitudeBias = 0f;
        }

        /// <summary>Read-only live probe (prove_draw_order_live.py, by jawa/static_call): the setting, the routing, and
        /// for every pair of large pawns on the current map that stand close enough to overlap (|dx| &lt;= 1.5,
        /// 0 &lt; dz &lt;= 2.5), "south|north|zS|zN|yS|yN|seedS|seedN" with y = DrawPos.y. Allocates; never per frame.</summary>
        public static string Probe()
        {
            var sb = new System.Text.StringBuilder();
            sb.Append("setting=").Append(RM_PatchesSettings.southDrawsFront ? 1 : 0)
              .Append(";pawnRouted=").Append(pawnRouted ? 1 : 0).Append(";printRouted=").Append(printRouted ? 1 : 0);
            Map map = Find.CurrentMap;
            if (map == null)
                return sb.Append(";map=none").ToString();
            var big = new List<Pawn>();
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                if (p.BodySize >= 1.5f || (p.ageTracker?.CurKindLifeStage?.bodyGraphicData?.drawSize.y ?? 1f) > 1.5f)
                    big.Add(p);
            sb.Append(";big=").Append(big.Count);
            int pairs = 0;
            foreach (Pawn a in big)
                foreach (Pawn b in big)
                {
                    if (a == b || pairs >= 40) continue;
                    Vector3 pa = a.Drawer.tweener.TweenedPos, pb = b.Drawer.tweener.TweenedPos;
                    float dz = pb.z - pa.z;
                    if (dz <= 0f || dz > 2.5f || Mathf.Abs(pb.x - pa.x) > 1.5f) continue;
                    sb.Append(";pair=").Append(a.LabelShortCap).Append('|').Append(b.LabelShortCap).Append('|')
                      .Append(pa.z.ToString("F3")).Append('|').Append(pb.z.ToString("F3")).Append('|')
                      .Append(a.DrawPos.y.ToString("F5")).Append('|').Append(b.DrawPos.y.ToString("F5")).Append('|')
                      .Append(a.Drawer.SeededYOffset.ToString("F5")).Append('|').Append(b.Drawer.SeededYOffset.ToString("F5"));
                    pairs++;
                }
            return sb.ToString();
        }

        /// <summary>Settings changed: reprint every map's things so the switch shows at once (pawns follow by themselves).</summary>
        public static void Reprint()
        {
            if (Current.Game?.Maps == null) return;
            foreach (Map map in Current.Game.Maps)
                map?.mapDrawer?.WholeMapChanged(MapMeshFlagDefOf.Things);
        }
    }
}
