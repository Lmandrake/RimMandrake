using Verse;

namespace RimMandrake.DivingInteraction
{
    // Shared surface between the float menu provider and both job drivers.
    // Whether a cell IS a dive site is entirely terrain-tag-driven — no
    // ThingDef, no building, no zone (see About.xml). Any biome kit wires in
    // by tagging its own hazardous-but-Standable water terrain with
    // DiveEligibleTag; this mod never names a biome.
    public static class RM_DiveUtility
    {
        public const string DiveEligibleTag = "RM_DiveEligible";

        public static bool CellIsDiveSite(IntVec3 cell, Map map)
        {
            if (map == null || !cell.InBounds(map) || cell.Fogged(map))
            {
                return false;
            }
            TerrainDef terrain = cell.GetTerrain(map);
            if (terrain == null || terrain.tags == null || !terrain.tags.Contains(DiveEligibleTag))
            {
                return false;
            }
            // Ban 4 (the_scald.md): nothing stands on the boiling SURFACE
            // itself. Impassable terrain (the true deep water) can never be
            // tagged into eligibility in the first place — this check is the
            // mod's own belt-and-braces against a future biome tagging its
            // deep terrain by mistake.
            return cell.Standable(map);
        }
    }
}
