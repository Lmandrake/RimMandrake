using System.Collections.Generic;
using Verse;

namespace RimMandrake.Warcasket
{
    // wasteland.md §7, verbatim: "a dead Junker in an adjusted warcasket is
    // a sealed salvage-within-salvage: suit, tools, and the half-extracted
    // core still in its grips."
    //
    // Carried by RM_WarcasketJunker (RM_Warcasket.xml). Any future
    // Junker-specific warcasket variant should carry it too, rather than a
    // fresh ad-hoc marker, so one check finds every sarcophagus-eligible suit.
    //
    // What reads it (WARCASKET_CASK_BAY_AND_SARCOPHAGI_1, RM_Sarcophagus.cs):
    //   - RM_CompSarcophagusSeal locks the suit onto its wearer at death, so
    //     vanilla Strip leaves it on the body ("sealed");
    //   - FloatMenuOptionProvider_CrackSarcophagus offers "crack open" on the
    //     corpse, and JobDriver_RM_CrackSarcophagus drops the suit and spawns
    //     `salvage` ("tools, and the half-extracted core").
    public class RM_JunkerSarcophagusExtension : DefModExtension
    {
        // A field rather than presence-only so a future non-sarcophagus use
        // of the class can carry the extension and opt out.
        public bool isSealedSarcophagus = true;

        public string flavorNote = "A dead Junker, sealed. Whatever they were hauling out is still in here with them.";

        // Work ticks to cut the sealed suit open (progress bar on the corpse).
        public int crackOpenTicks = 1200;

        // What is "still in its grips" besides the suit itself: the welded
        // extraction tooling and the half-extracted core. Authored per suit
        // def in XML.
        public List<ThingDefCountClass> salvage = new List<ThingDefCountClass>();
    }
}
