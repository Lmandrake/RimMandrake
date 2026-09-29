using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_SUIT_CLASS_1. wasteland.md §7: "a dead Junker in an
    // adjusted warcasket is a sealed salvage-within-salvage: suit, tools,
    // and the half-extracted core still in its grips."
    //
    // This is the SUIT-SIDE hook only. This mod is RM tier (franchise/
    // campaign-free, Q11a) and does not know what a Junker is, what a
    // "half-extracted core" item defName is, or what the corpse
    // interaction should do — that is a biome cast's own scope
    // (WASTELAND_MECHANICS_BUILD_1's listed scope does not cover it
    // either; see WARCASKET_CASK_BAY_AND_SARCOPHAGI_1, filed alongside
    // this build). What this gives that later work is a stable, named
    // way to FIND the right corpse:
    //
    //   ThingDef apparelDef = RM_WarcasketDefOfLikeThing; // e.g. corpse's worn apparel
    //   RM_JunkerSarcophagusExtension ext = apparelDef.GetModExtension<RM_JunkerSarcophagusExtension>();
    //   if (ext != null && ext.isSealedSarcophagus) { /* build the corpse interaction here */ }
    //
    // Carried by RM_WarcasketJunker (RM_Warcasket.xml). Any future
    // Junker-specific warcasket variant should carry it too, rather than
    // a fresh ad-hoc marker, so one check finds every sarcophagus-eligible
    // suit.
    public class RM_JunkerSarcophagusExtension : DefModExtension
    {
        // True on every Junker-variant warcasket ThingDef; a field rather
        // than presence-only so a future non-sarcophagus use of the class
        // (if one is ever needed) can carry the extension and opt out.
        public bool isSealedSarcophagus = true;

        // Free-text hook for whichever build actually constructs the
        // corpse interaction. Deliberately not a ThingDef reference to a
        // "half-extracted core" resource — this mod does not own or guess
        // at that item.
        public string flavorNote = "A dead Junker, sealed. Whatever they were hauling out is still in here with them.";
    }
}
