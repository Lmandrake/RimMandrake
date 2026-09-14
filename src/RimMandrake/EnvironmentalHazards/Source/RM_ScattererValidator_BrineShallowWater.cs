using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M6 build (miasma_kit_spec.md M6): "N sites chosen
    // on brine-side shallow water (validator reads M1's axis — strict
    // ordering after RM_GenStep_GradientAxis)". XML `Class=`-instantiated
    // per RM_GenStep_PlacedSetPieces's own `validators` list — that class's
    // own header comment names exactly this pattern (Verse.
    // ScattererValidator's own one-method contract, per-kit subclass).
    //
    // Gated on RM_GradientAxisExtension PRESENCE, not on bare biome
    // identity: "brine-side shallow water" is meaningless without a
    // fresh->brine axis to read at all, and this keeps the validator
    // genuinely reusable — any future biome that adopts M1's axis system
    // (that class's own header: "any future two-water biome does") gets
    // correct crèche-site gating for free, with zero Miasma-specific
    // coupling anywhere in this file. On a map whose biome carries no such
    // extension (i.e. every non-Miasma map in the game, since only
    // RUT_Miasma.xml carries RM_GradientAxisExtension today), every cell
    // fails outright — RUT_GenStep_CrecheScatterer is registered globally
    // onto Base_Player (same "safe for every biome, gate internally"
    // pattern RUT_GenStep_GradientAxis's own header already established),
    // so this early-out is what keeps it a harmless no-op everywhere else.
    public class RM_ScattererValidator_BrineShallowWater : ScattererValidator
    {
        // INVENTED (M6): "brine-side" reads as unambiguously brine, not
        // merely > 0.5 — RM_MapComponent_GradientAxis.SaltLineCells' own
        // band is +/-0.05 around the 0.5 salt line, so 0.6 sits a full
        // salt-line-band clear of it.
        public float minSalinity = 0.6f;

        // Mod Settings: MOD_OPTIONS_RETROFIT_1's own worldgen-affecting
        // toggle for this mechanism (RM_EnvironmentalHazardsSettings.
        // wardenCrecheScattererEnabled). Off: no cell is ever valid, so
        // RUT_GenStep_CrecheScatterer places nothing — same "disabled
        // mechanism spawns nothing, everything else untouched" shape every
        // other toggle in that file already follows.
        public override bool Allows(IntVec3 c, Map map)
        {
            if (!RM_EnvironmentalHazardsSettings.wardenCrecheScattererEnabled)
            {
                return false;
            }

            if (map?.Biome == null || map.Biome.GetModExtension<RM_GradientAxisExtension>() == null)
            {
                return false;
            }

            RM_MapComponent_GradientAxis axis = map.GetComponent<RM_MapComponent_GradientAxis>();
            if (axis == null || axis.SalinityAt(c) < minSalinity)
            {
                return false;
            }

            TerrainDef terrain = map.terrainGrid.TerrainAt(c);
            return terrain != null && terrain.IsWater && IsShallowWater(terrain);
        }

        // Mirrors RM_GenStep_GradientAxis.IsShallowWater exactly (that
        // method is private to an already-shipped, code-review-clean file
        // this pass deliberately does not touch for a cosmetic dedupe) —
        // WaterShallowBase-derived terrain carries the ShallowWater
        // affordance; WaterDeepBase-derived does not. Heuristic, not a
        // stored engine flag, same caveat that file's own comment gives.
        private static bool IsShallowWater(TerrainDef terrain)
        {
            if (terrain.affordances == null)
            {
                return false;
            }

            for (int i = 0; i < terrain.affordances.Count; i++)
            {
                if (terrain.affordances[i].defName == "ShallowWater")
                {
                    return true;
                }
            }

            return false;
        }
    }
}
