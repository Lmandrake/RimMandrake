using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F5 build — closes the hard-ban gap flagged and
    // explicitly declined to guess through by this item's own continuation
    // pass (2026-09-13, "Not done: F5 point 1... Fixing it means authoring
    // real marsh terrain... genuine unspecified design, not touched this
    // pass to avoid inventing it or breaking the shipped, FROZEN-sheet
    // biome's terrain table blind"). RUT_FeverWood.xml's own
    // terrainsByFertility lists only vanilla Soil/SoilRich, both
    // Heavy-affordance terrains, so hard ban 4 (`the_fever_wood.md` §6.4:
    // "No heavy structures on the ground — the marsh refuses them (donor,
    // kept); building means the trees, the boughways, or stilts") was not
    // actually enforced anywhere on a generated map.
    //
    // Deliberately NOT fixed by editing RUT_FeverWood.xml's own
    // terrainsByFertility table — `FEVERWOOD_BOUGH_SOIL_TERRAIN_1`'s own
    // "Watch out" section (same file, same day, 2026-09-24) rules that
    // table off-limits pending the terminal biome-paint pass
    // (`BIOME_PAINT_ONCE_AT_THE_END_1`) and names the GenStep route as the
    // correct one instead: "Paint via the GenStep; do not reach for the
    // fertility table." Same posture as every other biome-gated painter in
    // this assembly: a BiomeDef opts in by carrying this extension;
    // RM_GenStep_GroundRefusal reads it and is a harmless no-op on any
    // biome that doesn't. Generic, not Fever-Wood-specific — nothing below
    // names the Fever Wood.
    //
    // refusalTerrain reuses vanilla MarshyTerrain (Data/Core/Defs/
    // TerrainDefs/Terrain_Natural.xml) rather than a bespoke RUT_ def —
    // MEASURED this pass (direct read of the shipped Core XML):
    // affordances Light + GrowSoil + Diggable + Bridgeable, NO Medium, NO
    // Heavy — exactly the affordance ceiling hard ban 4 demands — plus
    // pathCost 14 against Soil's 2, which independently matches the
    // sheet's own §0 donor line ("near-impassable ground movement," kept
    // from the donor inventory). No MayRequire needed (Core, always
    // loaded); no invented texture or fertility value; no new art debt.
    //
    //   <BiomeDef>
    //     <defName>RUT_FeverWood</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_GroundRefusalBiomeExtension">
    //         <refusalTerrain>MarshyTerrain</refusalTerrain>
    //         <convertFromTerrains>
    //           <li>Soil</li>
    //           <li>SoilRich</li>
    //         </convertFromTerrains>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_GroundRefusalBiomeExtension : DefModExtension
    {
        // What every matching cell becomes. Required.
        public TerrainDef refusalTerrain;

        // Which currently-painted terrains are eligible for conversion.
        // Anything NOT in this list (a boughway/causeway/bough-soil lane, a
        // mirror pool, bare rock, a road) is left exactly as an earlier
        // GenStep painted it — see RM_GenStep_GroundRefusal's own ordering
        // note for why this needs no cross-extension bookkeeping.
        public List<TerrainDef> convertFromTerrains = new List<TerrainDef>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (refusalTerrain == null)
            {
                yield return "RM_GroundRefusalBiomeExtension has no refusalTerrain — RM_GenStep_GroundRefusal would have nothing to paint.";
            }

            if (convertFromTerrains == null || convertFromTerrains.Count == 0)
            {
                yield return "RM_GroundRefusalBiomeExtension has no convertFromTerrains — it would convert nothing.";
            }
        }
    }
}
