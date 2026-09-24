using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // WATER_TRUCE_RETRIBUTION_1 (caused_by WEEPING_STONES_DESIGN_SITTING_1).
    // Opt-in marker for a BiomeDef whose standing water is a truce site
    // (weeping_stones.md §4, owner near-verbatim 2026-09-06: "At the water,
    // the truce holds — completely... Water is always MAD, or peace.").
    //
    // This extension carries the RADIUS the whole water-truce system reads
    // — both the retribution half this item ships (RM_MapComponent_WaterTruce
    // below) and the suppression half the fauna roster still owes
    // (weeping_stones_fauna_roster_2026-09-24.md row §2f: "same radius, one
    // system: suppression inward, retribution outward"). Deliberately one
    // extension, not two, so that owed work reads the identical field
    // instead of authoring a second DefModExtension with its own radius that
    // could drift from this one.
    //
    //   <BiomeDef>
    //     <defName>RUT_WeepingStones</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_WaterTruceExtension">
    //         <radius>10</radius>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_WaterTruceExtension : DefModExtension
    {
        // INVENTED — no owner-ruled number exists for this. Cells outward
        // from any standing-water cell (TerrainDef.IsWater) that count as
        // "at the water" for truce purposes.
        public float radius = 10f;
    }
}
