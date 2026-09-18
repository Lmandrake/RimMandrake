using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M9 build (greentide_kit_spec.md M9, "Root
    // causeways — map-gen"). Same idiom as RM_GradientAxisExtension /
    // RM_LivingBoleBiomeExtension: a BiomeDef opts in by carrying this
    // extension; RM_GenStep_RootCauseways reads it and is a harmless no-op
    // on any biome that doesn't. Generic, not Greentide-hardcoded, per the
    // build brief.
    //
    //   <BiomeDef>
    //     <defName>RUT_Greentide</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_RootCausewayBiomeExtension">
    //         <causewayTerrain>RUT_RootCauseway</causewayTerrain>
    //         <basinTerrains><li>RM_GreentideChurnmud</li></basinTerrains>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_RootCausewayBiomeExtension : DefModExtension
    {
        // What gets painted. Required.
        public TerrainDef causewayTerrain;

        // Restrict painting to cells CURRENTLY on one of these terrains
        // (the kit spec's "over the churnmud basins"). Empty/null means
        // unrestricted — paint over whatever is there, for a biome with no
        // basin hazard of its own to route around.
        public List<TerrainDef> basinTerrains;

        // Splines traced outward per anchor, and their width. INVENTED, kit
        // spec's own numbers ("3-6... 1-2 wide").
        public IntRange pathsPerAnchorRange = new IntRange(3, 6);
        public IntRange laneWidthRange = new IntRange(1, 2);
        public IntRange pathLengthRange = new IntRange(20, 40);
        public float turnChancePerStep = 0.35f;

        // Fallback anchor picking, used only when no
        // RM_MapComponent_LivingRegrowth boles are registered on this map
        // (M9 running standalone, before or without M12's Greatbole) —
        // "a configurable anchor-selection strategy so M9 can run standalone
        // or paired with M12", per the build brief. INVENTED counts/spacing.
        public IntRange fallbackAnchorCountRange = new IntRange(1, 3);
        public float fallbackMinAnchorSpacing = 25f;
        public int fallbackEdgeMargin = 10;

        // FEVER_WOOD_MECHANICS_1 F6 build. Optional additional lane
        // networks, run over the SAME anchor set after the primary profile
        // above (causewayTerrain/basinTerrains/pathsPerAnchorRange/
        // laneWidthRange/pathLengthRange/turnChancePerStep), each with its
        // own terrain and tuning. Generic, not Fever-Wood-specific: "any
        // biome wanting more than one lane tier (e.g. an elevated network
        // plus a cheaper ground-level alternative) opts in via extra
        // entries" — null/empty means exactly what it always meant, a
        // single pass (Greentide's own existing profile, unchanged).
        //
        // Real correction against the fever_wood_kit_spec.md's own framing:
        // the spec describes the ground causeway as "the same GenStep's
        // second call... zero extra code, just a second GenStepDef
        // instance with different tuning" — but RM_GenStep_RootCauseways
        // reads its whole profile off the ONE RM_RootCausewayBiomeExtension
        // instance a BiomeDef carries (GetModExtension<T>() returns only
        // the first match of a type), so a second GenStepDef of the same
        // class would read the identical extension and repaint the
        // identical lanes — not a second, differently-tuned network. This
        // field is the minimal, generic fix.
        public List<RM_RootCausewayPass> additionalPasses;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (causewayTerrain == null)
            {
                yield return "RM_RootCausewayBiomeExtension has no causewayTerrain — RM_GenStep_RootCauseways would have nothing to paint.";
            }

            if (additionalPasses != null)
            {
                for (int i = 0; i < additionalPasses.Count; i++)
                {
                    if (additionalPasses[i]?.causewayTerrain == null)
                    {
                        yield return "RM_RootCausewayBiomeExtension.additionalPasses[" + i + "] has no causewayTerrain — RM_GenStep_RootCauseways would have nothing to paint for it.";
                    }
                }
            }
        }
    }

    // One additional lane-network profile (see RM_RootCausewayBiomeExtension.additionalPasses
    // above) — the same per-pass fields the primary profile carries, minus
    // the anchor-selection fields, since anchors are shared across every
    // pass on one map.
    public class RM_RootCausewayPass
    {
        public TerrainDef causewayTerrain;
        public List<TerrainDef> basinTerrains;
        public IntRange pathsPerAnchorRange = new IntRange(3, 6);
        public IntRange laneWidthRange = new IntRange(1, 2);
        public IntRange pathLengthRange = new IntRange(20, 40);
        public float turnChancePerStep = 0.35f;
    }
}
