using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 3 (alpha_family_source_review.md §4.3).
    //
    // The source review's finding, verbatim in substance: "the 'accuracy in
    // darkness' effect is not a bespoke comp — it's vanilla's own systems,
    // unlocked by patching one glow-multiplier method." Vanilla's existing
    // darkness chain (shooting accuracy, mood, plant growth, light-gated
    // work) all reads from GenCelestial.CurCelestialSunGlow, so multiplying
    // that one number for a biome buys every downstream effect for free.
    //
    // Generalized past the donor's hardcoded single-biome check: any BiomeDef
    // in any mod opts in by carrying this extension, so every dark-biome
    // sheet gets its own tuned darkness with no new patch per biome. A
    // multiplier of 0.6-0.8 reads as permanent overcast rather than night
    // (source review §5) — that whole range is available here.
    //
    //   <BiomeDef>
    //     <defName>RM_ExampleDarkBiome</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.BiomeGlowMultiplierExtension">
    //         <glowMultiplier>0.34</glowMultiplier>
    //         <suppressSunlightStatAffecter>true</suppressSunlightStatAffecter>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class BiomeGlowMultiplierExtension : DefModExtension
    {
        // Multiplied into GenCelestial.CurCelestialSunGlow for any map on
        // this biome. 1.0 is a no-op; 0.0 is permanent night.
        public float glowMultiplier = 1f;

        // When true, ConditionalStatAffecter_InSunlight reads false for any
        // Thing on this biome's maps — so sunlight-gated stat effects
        // (Biotech's sun-sensitivity chief among them) treat the biome as
        // permanently sunless rather than merely dim. Separate from the glow
        // number on purpose: a 0.7 "overcast" biome should normally still
        // count as sunlit, and only a true dark biome should not.
        public bool suppressSunlightStatAffecter;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (glowMultiplier < 0f || glowMultiplier > 1f)
            {
                yield return "BiomeGlowMultiplierExtension glowMultiplier must be within 0..1 (it multiplies a 0..1 sun glow).";
            }
        }
    }
}
