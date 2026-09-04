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

    // Fixed 2026-09-02 (opus code review): "there are zero Log. calls in the
    // whole of Graffiti/Source/" - every mis-wire in this extension's data was
    // silent by construction, the exact "a patch that matches nothing logs
    // nothing" shape CLAUDE.md warns about. DefModExtension has no ConfigErrors
    // hook of its own, so this walks every ThingDef carrying one at startup and
    // names the two known mis-wire shapes instead of leaving them to be
    // discovered by a mark that quietly never reacts to anything.
    [StaticConstructorOnStartup]
    internal static class ModExtension_Graffiti_Validator
    {
        static ModExtension_Graffiti_Validator()
        {
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
                if (ext == null) continue;

                if (ext.visibility == GraffitiVisibility.ClanOnly && ext.viewerReactionThought == null)
                {
                    Log.Warning("[RimMandrake.Graffiti] " + def.defName +
                        " sets visibility=ClanOnly but has no viewerReactionThought - " +
                        "the gate has nothing to grant and will never do anything.");
                }

                // Third mis-wire shape: ThoughtWorker_ViewedGraffitiMark.CurrentStateInternal
                // is only ever invoked for a ThoughtDef whose <workerClass> IS that class
                // (ThoughtDef.IsSituational / .Worker gate on workerClass, not thoughtClass -
                // verified against RimWorld/ThoughtDef.cs). Pointing viewerReactionThought at
                // any other ThoughtDef compiles and loads clean but the reaction never fires.
                if (ext.viewerReactionThought != null &&
                    ext.viewerReactionThought.workerClass != typeof(ThoughtWorker_ViewedGraffitiMark))
                {
                    Log.Warning("[RimMandrake.Graffiti] " + def.defName +
                        " sets viewerReactionThought=" + ext.viewerReactionThought.defName +
                        " but that ThoughtDef's workerClass is not ThoughtWorker_ViewedGraffitiMark - " +
                        "it will never fire from viewing this mark.");
                }
            }
            foreach (ThoughtDef td in DefDatabase<ThoughtDef>.AllDefsListForReading)
            {
                if (td.workerClass != typeof(ThoughtWorker_ViewedGraffitiMark)) continue;
                bool anyMarkPointsHere = false;
                foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
                    if (ext != null && ext.viewerReactionThought == td) { anyMarkPointsHere = true; break; }
                }
                if (!anyMarkPointsHere)
                {
                    Log.Warning("[RimMandrake.Graffiti] " + td.defName +
                        " uses ThoughtWorker_ViewedGraffitiMark but no mark's " +
                        "ModExtension_Graffiti.viewerReactionThought points at it - unreachable.");
                }
            }
        }
    }
}
