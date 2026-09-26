using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // BIOME_ARRIVAL_NARRATION_1 (owner card 2026-09-24, from his own prompt:
    // "I'm wondering if the narrator should announce each biome when the ship
    // lands to give some hints"). Opt-in marker for a BiomeDef that ships one
    // survival-reads letter, fired the first time a gravship lands in that
    // biome per save (RM_GameComponent_BiomeArrivalLetters below).
    //
    // RM tier: plain text, no character, no narrator -- this mod knows nothing
    // about any campaign. The Utinni voice layer
    // (src/RimUtinni/UtinniPatches/Patches/BiomeArrivalLetters_*.xml) replaces
    // letterLabel/letterText wholesale via PatchOperationReplace to speak in
    // the campaign Narrator's voice (infrastructure/state/canon.yml
    // `narrator`) instead -- flavor replacement, not new machinery, per the
    // item's own spec. Deliberately raw strings, not translation keys: two
    // plain XML nodes are the whole "voice swap", with nothing to keep in
    // sync across a Keyed-translation indirection between two mods.
    //
    //   <BiomeDef>
    //     <defName>RM_TheSump</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_BiomeArrivalLetterExtension">
    //         <letterLabel>The Sump</letterLabel>
    //         <letterText>...</letterText>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    //
    // A BiomeDef with no extension (every biome this pass did not reach) is
    // simply never introduced -- silent no-op, same posture as every other
    // opt-in extension in this kit.
    public class RM_BiomeArrivalLetterExtension : DefModExtension
    {
        public string letterLabel;
        public string letterText;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }
            if (letterLabel.NullOrEmpty())
            {
                yield return "RM_BiomeArrivalLetterExtension has no letterLabel.";
            }
            if (letterText.NullOrEmpty())
            {
                yield return "RM_BiomeArrivalLetterExtension has no letterText.";
            }
        }
    }
}
