using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // WORLDMAP_IN_GAME_AUDIT 2026-10-20: the seabed layer must not draw through the planet.
    //
    // RM_SeabedLayer is a geometric twin of the surface: same origin, same radius (100), same
    // tiles. Vanilla draws every planet layer's Terrain and Hills even when that layer is not
    // the selected one (WorldDrawLayerBase.VisibleWhenLayerNotSelected defaults to true; it is
    // how the orbit layer shows behind the planet). Vanilla's other layers never share a radius,
    // so this never mattered before. Ours does: two terrain meshes on one sphere, and the depth
    // test picks a winner tile by tile. Seen in game (2026-10-20) as the "honeycomb": hexes of
    // RM_SeabedBedrock (the grey texture with rings) and RM_SeabedFloor (olive stripes) printed
    // over the surface biomes, a second set of hill blots, and surface edits that did not show
    // where the floor won. Measured: repainting surface tile 8024 to RM_Contagion changed
    // nothing on screen; its hill blot did change.
    //
    // Rule: a draw layer is hidden while ANOTHER layer that occupies the same sphere is the
    // selected one. Surface view hides the floor; floor view hides the surface. Layers on other
    // radii (orbit) keep vanilla behaviour.
    [HarmonyPatch(typeof(WorldDrawLayer), nameof(WorldDrawLayer.Visible), MethodType.Getter)]
    public static class Patch_SeabedLayerCoplanarHide
    {
        public static void Postfix(WorldDrawLayer __instance, ref bool __result)
        {
            if (!__result) return;
            if (HiddenByCoplanarSelection(__instance)) __result = false;
        }

        public static bool HiddenByCoplanarSelection(WorldDrawLayer layer)
        {
            PlanetLayer mine = layer.planetLayer;
            PlanetLayer selected = PlanetLayer.Selected;
            if (mine == null || selected == null || mine == selected) return false;
            if (Mathf.Abs(mine.Radius - selected.Radius) > 0.01f) return false;
            if ((mine.Origin - selected.Origin).sqrMagnitude > 0.0001f) return false;
            return true;
        }
    }

    // MEASURED 2026-10-20 (first load with the patch above): the planet drew black and every
    // world view sat in a "GeneratingPlanet" long event for ~10 minutes, over and over.
    // WorldRenderer.ShouldRegenerateDirtyLayersInLongEvent asks only whether the PLANET layer is
    // visible and a terrain draw layer on it is Dirty; RegenerateDirtyLayersNow_Async then skips
    // draw layers whose Visible is false. A hidden floor terrain layer therefore stays dirty for
    // ever, DrawWorldLayers queues a fresh long event every frame and returns before rendering.
    // Rule: a dirty terrain layer that the coplanar rule hides does not ask for a long event.
    // It regenerates the first time it is shown (its planet layer selected).
    [HarmonyPatch(typeof(WorldRenderer), "ShouldRegenerateDirtyLayersInLongEvent", MethodType.Getter)]
    public static class Patch_WorldRenderer_RegenIgnoresHiddenCoplanar
    {
        public static void Postfix(ref bool __result)
        {
            if (!__result || Find.WorldGrid == null) return;
            foreach (var kv in Find.WorldGrid.PlanetLayers)
            {
                PlanetLayer planetLayer = kv.Value;
                if (!planetLayer.Visible) continue;
                foreach (WorldDrawLayer d in planetLayer.WorldDrawLayers)
                {
                    if (d.Dirty && d is WorldDrawLayer_Terrain && !Patch_SeabedLayerCoplanarHide.HiddenByCoplanarSelection(d))
                        return;
                }
            }
            __result = false;
        }
    }
}
