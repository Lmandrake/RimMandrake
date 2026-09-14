using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M12 build (greentide_kit_spec.md M12, "The
    // Greatbole — mineable living tower"). Generic on purpose, same idiom as
    // RM_GradientAxisExtension: a BiomeDef opts in by carrying this
    // extension; RM_GenStep_LivingBoles reads it and is a harmless no-op on
    // any biome that doesn't. "Any future living-dungeon wants it" (the kit
    // spec's own words for RM_MapComponent_LivingRegrowth) extends to this
    // extension too — nothing below names Greentide or the Greatbole.
    //
    //   <BiomeDef>
    //     <defName>RUT_Greentide</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_LivingBoleBiomeExtension">
    //         <heartwoodThing>RUT_GreatboleHeartwood</heartwoodThing>
    //         <coreMarkerThing>RUT_GreatboleCore</coreMarkerThing>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_LivingBoleBiomeExtension : DefModExtension
    {
        // What the blob and its marker are built from. Required — a biome
        // that carries this extension but leaves either null is a config
        // error, not a silent no-op (unlike the GenStep's own absent-
        // extension no-op, which IS silent by design).
        public ThingDef heartwoodThing;
        public ThingDef coreMarkerThing;

        // How many boles a single map gets, and how big each one's blob is
        // (radius in cells around its center). INVENTED, kit spec gives no
        // number for either.
        public IntRange boleCountRange = new IntRange(1, 2);
        public IntRange boleRadius = new IntRange(4, 6);

        // Site-picking guards: kept far from each other and from the map
        // edge so a blob never straddles the edge or swallows another
        // bole's footprint. INVENTED.
        public float minSpacing = 30f;
        public int edgeMargin = 12;

        // Roof painted over the whole footprint (the "natural-roof patch"
        // the spec's own text calls for). Defaults to vanilla
        // RoofDefOf.RoofRockThick in code when left unset — see
        // RM_GenStep_LivingBoles.Generate.
        public RoofDef roofDef;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (heartwoodThing == null)
            {
                yield return "RM_LivingBoleBiomeExtension has no heartwoodThing — RM_GenStep_LivingBoles would have nothing to paint.";
            }

            if (coreMarkerThing == null)
            {
                yield return "RM_LivingBoleBiomeExtension has no coreMarkerThing — a bole would have nothing to register itself with.";
            }

            if (boleCountRange.max <= 0)
            {
                yield return "RM_LivingBoleBiomeExtension.boleCountRange has no positive count — it would place nothing.";
            }
        }
    }
}
