using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;
using HarmonyLib;

namespace RimMandrake.GravshipCrushLanding
{
    // GRAVSHIP_LANDING_CRUSH_1. Owner, 2026-09-05, verbatim: "We absolutely
    // need mods that let the ship just plop down on top of small barriers
    // and blockages or a ship that size will never find clear landing.
    // Major mountains should be a no no as is deep water or lava but
    // otherwise it should just crush stuff and be done with it. Also we
    // should let it take off even if the thrusters are blocked. The grav
    // engine just goes straight up before the thrusters are even needed."
    //
    // Checked an existing candidate first (Steam WS 3525655208, "Just
    // F*King Landing") by decompile before writing this: its landing patch
    // makes EVERY cell valid with no distinction at all -- it would also let
    // a gravship land in lava, deep water or on a mountain, which the owner
    // explicitly wants kept as hard refusals. Its takeoff patch is a no-op
    // (reads a settings bool and does nothing with it). Not a fit; this mod
    // repatches from scratch against the ACTUAL vanilla mechanism, decompiled
    // from the live Assembly-CSharp.dll:
    //
    //   RimWorld.Designator_MoveGravship.IsValidCell(IntVec3, Map) [private
    //   static] refuses on, in order: out of bounds; no-build-edge-area;
    //   inside a map.landingBlockers CellRect; roofed (this is what actually
    //   catches "major mountain" -- natural rock roof); fogged; a Thing on
    //   the cell that is a Building without canLandGravshipOn (or any thing
    //   flagged preventGravshipLandingOn), UNLESS it's the only path to the
    //   final "hostile/humanlike pawn" check; then CanBuildOnTerrain against
    //   TerrainDefOf.Substructure -- THIS is what already refuses deep water
    //   and lava (Substructure cannot be built on either in vanilla), with
    //   no code of ours needed to keep that behaviour.
    //
    // So the fix is narrow: only the "blocking Thing" branch changes, from a
    // hard refusal into "let it through, and destroy that thing when the
    // landing actually happens" -- mirroring what vanilla ALREADY does for
    // trees (WorldComponent_GravshipController.InitiateLanding calls
    // DestroyTreesAroundSubstructure unconditionally; trees never trigger
    // the Thing-refusal branch to begin with because they aren't Buildings).
    // Every other refusal (bounds, no-build-edge, landingBlockers, roofed,
    // fogged, terrain, hostile/humanlike pawns) is left completely
    // untouched, so mountains/deep water/lava/raiders still block exactly
    // as before.
    [StaticConstructorOnStartup]
    public static class GravshipCrushLandingMod
    {
        public const string HarmonyId = "mandrake.rm.gravshipcrushlanding";

        static GravshipCrushLandingMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());
            Log.Message("[RimMandrake.GravshipCrushLanding] ready: crush-landing + unblockable-thrust patches active.");
        }
    }

    internal static class CrushLandingUtility
    {
        // True for exactly the Things that vanilla's IsValidCell would have
        // refused the landing over. Pawns are excluded on purpose -- vanilla
        // already only refuses on hostile-or-humanlike pawns there, and the
        // owner's ask was about "small barriers and blockages", not pawns;
        // we leave that branch's refusal behaviour alone.
        public static bool IsCrushableBlocker(Thing thing)
        {
            if (thing is Pawn) return false;
            if (thing.def.preventGravshipLandingOn) return true;
            BuildingProperties building = thing.def.building;
            if (building != null && !building.canLandGravshipOn) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(Designator_MoveGravship), "IsValidCell", new System.Type[] { typeof(IntVec3), typeof(Map) })]
    public static class Patch_GravshipIsValidCell
    {
        [HarmonyPrefix]
        public static bool Prefix(ref AcceptanceReport __result, IntVec3 cell, Map map)
        {
            if (!cell.InBounds(map))
            {
                __result = "GravshipOutOfBounds".Translate();
                return false;
            }
            if (!cell.InBounds(map, 1) || cell.InNoBuildEdgeArea(map))
            {
                __result = "GravshipInNoBuildArea".Translate();
                return false;
            }
            if (map.landingBlockers != null)
            {
                foreach (CellRect landingBlocker in map.landingBlockers)
                {
                    if (landingBlocker.Contains(cell))
                    {
                        __result = "GravshipInBlockedArea".Translate();
                        return false;
                    }
                }
            }
            if (cell.Roofed(map))
            {
                __result = "GravshipBlockedByRoof".Translate();
                return false;
            }
            if (cell.Fogged(map))
            {
                __result = "GravshipBlockedByFog".Translate();
                return false;
            }
            foreach (Thing thing in cell.GetThingList(map))
            {
                if (CrushLandingUtility.IsCrushableBlocker(thing))
                {
                    // Owner ruling: small barriers and blockages get crushed,
                    // not refused. The actual destruction happens at landing
                    // time (Patch_GravshipInitiateLanding_CrushObstacles),
                    // not here -- this is only the placement check.
                    continue;
                }
                if (!thing.def.preventGravshipLandingOn)
                {
                    BuildingProperties building = thing.def.building;
                    if (building == null || building.canLandGravshipOn)
                    {
                        if (thing is Pawn pawn && (pawn.RaceProps.Humanlike || pawn.HostileTo(Faction.OfPlayer)))
                        {
                            __result = "GravshipBlockedBy".Translate(pawn);
                            return false;
                        }
                        continue;
                    }
                }
                // Unreachable in practice (IsCrushableBlocker already caught
                // every non-pawn refusal case above) -- kept only so a future
                // vanilla refusal case we haven't accounted for still refuses
                // instead of silently passing.
                __result = "GravshipBlockedBy".Translate(thing);
                return false;
            }
            if (!GenConstruct.CanBuildOnTerrain(TerrainDefOf.Substructure, cell, map, Rot4.North))
            {
                __result = "GravshipBlockedByTerrain".Translate(cell.GetTerrain(map));
                return false;
            }
            __result = true;
            return false;
        }
    }

    [HarmonyPatch(typeof(WorldComponent_GravshipController), "InitiateLanding")]
    public static class Patch_GravshipInitiateLanding_CrushObstacles
    {
        private static readonly FieldInfo LandingMarkerField =
            AccessTools.Field(typeof(WorldComponent_GravshipController), "landingMarker");

        [HarmonyPrefix]
        public static void Prefix(WorldComponent_GravshipController __instance, Map map, IntVec3 landingPos)
        {
            GravshipLandingMarker marker = LandingMarkerField.GetValue(__instance) as GravshipLandingMarker;
            if (marker == null || map == null) return;

            List<IntVec3> footprint = marker.GravshipCells.Select(c => c + landingPos).ToList();
            foreach (IntVec3 cell in footprint)
            {
                if (!cell.InBounds(map)) continue;
                // Snapshot: destroying a Thing mutates the cell's thing list,
                // so iterate a copy, not the live list.
                foreach (Thing thing in cell.GetThingList(map).ToList())
                {
                    if (!CrushLandingUtility.IsCrushableBlocker(thing)) continue;
                    if (thing.Destroyed) continue;
                    FleckMaker.ThrowDustPuff(cell.ToVector3Shifted(), map, 1.5f);
                    thing.Destroy(DestroyMode.Deconstruct);
                }
            }
        }
    }

    // Owner: "we should let it take off even if the thrusters are blocked.
    // The grav engine just goes straight up before the thrusters are even
    // needed." CompGravshipThruster.CanBeActive (which gates whether a
    // thruster counts toward launch readiness) short-circuits to false the
    // moment Blocked is true, so patching Blocked itself is the single,
    // narrowest point that makes every downstream consumer (launch
    // readiness, CanLink, the inspect-string warning) agree a thruster is
    // never blocked, rather than chasing each consumer separately.
    [HarmonyPatch(typeof(CompGravshipThruster), nameof(CompGravshipThruster.Blocked), MethodType.Getter)]
    public static class Patch_GravshipThruster_NeverBlocked
    {
        [HarmonyPrefix]
        public static bool Prefix(ref bool __result)
        {
            __result = false;
            return false;
        }
    }
}
