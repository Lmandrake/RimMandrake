using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;

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
            PlanetLayer mine = __instance.planetLayer;
            PlanetLayer selected = PlanetLayer.Selected;
            if (mine == null || selected == null || mine == selected) return;
            if (Mathf.Abs(mine.Radius - selected.Radius) > 0.01f) return;
            if ((mine.Origin - selected.Origin).sqrMagnitude > 0.0001f) return;
            __result = false;
        }
    }
}
