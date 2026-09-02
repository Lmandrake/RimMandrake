using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_FRAMEWORK_BUILD_1 §2's "RM_GraffitiDef (new def class):
    // category ... quality support ... maker + subject records ...
    // viewer-reaction spec ... faction-reaction spec ... visibility class".
    //
    // Built as a DefModExtension on the graffiti ThingDef itself, not a
    // parallel Def hierarchy - RimWorld's own idiom for "annotate an
    // existing def with a data bundle a system reads" (the same shape
    // SWCP_Core uses for ModExtension_FactionPermanentlyHostileTo, read
    // this session while fixing EMPIRE_WHITELIST_OVERRIDDEN_1). A mark
    // ThingDef (sacred/mural/jest/taunt/cant) carries one of these in its
    // <modExtensions> list; nothing here invents a new Def XML tag.
    //
    // WHAT IS WIRED: viewerReactionThought is read by
    // ThoughtWorker_ViewedGraffitiMark; breachLure is read by
    // BreachBiasHook. Both are mechanism only - no content ThingDef/
    // ThoughtDef ships with them (owner-voice work, a separate item). See
    // infrastructure/state/items/GRAFFITI_FRAMEWORK_BUILD_1.md.
    public class ModExtension_Graffiti : DefModExtension
    {
        public GraffitiCategory category;

        public GraffitiVisibility visibility = GraffitiVisibility.Public;

        // §1 Mural: "positive Beauty, quality-tiered like sculpture
        // (Awful->Legendary)". False for Sacred/Jest/Taunt/Cant, which are
        // fixed single-quality marks per the spec's own art plan (§3: "the
        // marks ARE the livery, painted" - no quality roll).
        public bool supportsQuality;

        // §1 Jest "The Caricature" / §1b THE SHAMING TIER: a mark can name
        // a specific colonist. Null for marks with no subject (most Sacred/
        // Cant/Taunt marks).
        public bool hasSubject;

        // §1 Taunt / §1b Shaming: "painting either is a hostile social act
        // ... the colony reads who painted what (marks carry authorship,
        // like art)."
        public bool tracksMaker = true;

        // ThoughtDef the viewer ThoughtWorker (not yet built) should grant
        // on sighting this mark, once one exists. Null = no reaction wired
        // yet for this mark.
        public ThoughtDef viewerReactionThought;

        // §4 "Theology rows": which god's satiation this mark's placement/
        // defacement should move, and by how much (S/M/L per
        // divine_satiation_engine.md §8b's own vocabulary). String, not an
        // enum reference to RimMandrake.Ninefold.God, because this mod
        // (RM tier, engine-generic) must not hard-depend on the RUT-tier
        // pantheon - a content pack wires the two together by reading this
        // field and calling Ninefold's GameComponent_Ninefold.ApplyDelta.
        public string godSatiationHook;

        // §1 Taunt "Come And Take It": raiders bias toward breaching AT
        // this mark's location - the raid-AI breach-bias hook
        // (BreachBiasHook.cs) reads this flag generically. False for
        // every family except a taunt mark built to funnel a breach.
        public bool breachLure;
    }
}
