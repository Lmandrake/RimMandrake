using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M5 build (greentide_kit_spec.md "M5. Breaklight
    // — clarity as the disaster"). A DefModExtension on a GameConditionDef
    // (unlike BiomeGlowMultiplierExtension, which lives on a BiomeDef) —
    // while a condition carrying this is active on a map,
    // BiomeGlowPatches.CurCelestialSunGlow_Postfix multiplies the map's
    // natural sun glow by THIS value instead of the biome's own
    // BiomeGlowMultiplierExtension.glowMultiplier, undoing (or further
    // altering) a dark biome's permanent dimming for the duration of a
    // "clearing" event.
    //
    // Deliberately generic — nothing here names Greentide or Breaklight, per
    // the kit spec's own framing ("benefits every future dark biome with a
    // clearing event"). Any future GameConditionDef, on any biome, opts in
    // the same way BiomeGlowMultiplierExtension already lets any BiomeDef
    // opt in.
    //
    //   <GameConditionDef>
    //     <defName>RUT_ExampleClearing</defName>
    //     <conditionClass>...</conditionClass>
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_GlowMultiplierOverrideExtension">
    //         <glowMultiplier>1.0</glowMultiplier>
    //       </li>
    //     </modExtensions>
    //   </GameConditionDef>
    public class RM_GlowMultiplierOverrideExtension : DefModExtension
    {
        // Multiplied into GenCelestial.CurCelestialSunGlow for any map
        // where this condition is active, in place of (not stacked with)
        // the biome's own BiomeGlowMultiplierExtension.glowMultiplier. 1.0
        // reads as ordinary, undimmed daylight — the usual "clearing event"
        // case.
        public float glowMultiplier = 1f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (glowMultiplier < 0f || glowMultiplier > 1f)
            {
                yield return "RM_GlowMultiplierOverrideExtension glowMultiplier must be within 0..1 (it multiplies a 0..1 sun glow).";
            }
        }
    }
}
