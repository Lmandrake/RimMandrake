using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RUT_RuthlessPursuingMechanoids
{
    /* EMPIRE_PURSUIT_SURVEY_SHADOW_1 — added 2026-08-29, not part of upstream.
     * Carries the owner-editable survey-shadow biome list as data on the def, per
     * owner-rules-must-be-data: the list lives in XML (ScenParts_EmpirePursuit.xml),
     * never hardcoded in this class. */
    public class ScenPartDef_RuthlessPursuit : ScenPartDef
    {
        public List<BiomeDef> surveyShadowBiomes = new List<BiomeDef>();
        public float surveyShadowMultiplier = 4f;
    }
}
