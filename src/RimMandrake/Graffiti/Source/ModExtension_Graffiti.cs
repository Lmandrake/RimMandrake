using System.Collections.Generic;
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

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 §1.2: the FORM axis, beside this
        // FUNCTION axis above. Defaults Scrawl (today's Vandal shape) so a
        // def that never sets it keeps behaving exactly as before.
        public GraffitiForm form = GraffitiForm.Scrawl;

        // GraffitiPool's weighted pick, within whichever placer's eligible
        // set. 0 = never picked by a weighted pool (still placeable by name,
        // e.g. tier-A's single IdeoSigil def, or a Designator that names a
        // def directly).
        public float poolWeight = 1f;

        // Placers this mark is eligible for - design §1.2's "placers"
        // column. Spree/Joy reads the punk pool via GraffitiPool; a player
        // Designator only offers marks with designatorEligible=true;
        // RaidExitTagger only offers marks with raidExitEligible=true.
        public bool designatorEligible;
        public bool raidExitEligible;

        // Tier C (design §3.2): a meme-affinity glyph, offered only to an
        // ideo holding at least one of these memes. Null/empty = not
        // meme-gated (every punk mark and every tier-A/B sigil). MemeDef is
        // a core RimWorld.dll type present whether or not Ideology's XML is
        // active - content authors still wrap the owning ThingDef in
        // MayRequire="Ludeon.RimWorld.Ideology" (or Biotech/Anomaly/Odyssey
        // for their own memes) so the def itself never half-loads without
        // its meme.
        public List<MemeDef> requiresAnyMeme;

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave 2, design §1.2 ("minArtistic
        // int - designator/joy gating by skill") and §3
        // ("RM_Mark_ThrowUp_A/B ... Joy (skill >= 6)"): a mark's minimum
        // Artistic skill for the placing pawn. 0 (default) = ungated - every
        // mark shipped before this wave keeps behaving exactly as before.
        // Read by GraffitiPool.SkillGateAllows against SkillDefOf.Artistic;
        // a pawn with no skills tracker (most raiders/animals do carry one,
        // but the check is null-safe) is treated as skill 0.
        public int minArtistic;

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave 2, design §2.2's own table
        // entry for RM_Graffiti_Stencil_Crown ("requiresAnyMeme none;
        // requiresHostile to Empire") - the half of that gate wave 1 shipped
        // ungated. A FactionDef defName (string, not a FactionDef reference,
        // for the same reason godSatiationHook below is a string: this mark
        // must not hard cross-reference a DLC's FactionDef XML - a mod list
        // without Royalty simply never resolves the def and the gate is a
        // no-op). Null/empty = ungated (every mark before this field, and
        // this mark itself on a Royalty-less mod list). Read by
        // GraffitiPool.HostilityGateAllows: if the named FactionDef exists
        // AND a Faction instance of it exists in the current game, the
        // placing pawn's own faction must be HostileTo it, or the mark is
        // not offered; if either lookup comes back empty (no Royalty, or
        // Royalty active but no Empire spawned this game), the gate falls
        // open rather than closed - the mark stays available exactly as
        // wave 1 shipped it, never silently disappears from the pool.
        public string requiresHostileToFactionDef;

        // Tier A (design §3.1): this mark's Graphic is built at runtime from
        // the placing pawn's Ideo.Icon tinted Ideo.Color, drawn over the
        // frame texture named below. Filth_Mark.SpawnSetup reads both.
        public bool sigilTierA;
        public string sigilFrameTexPath;

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

        // ThoughtDef the viewer ThoughtWorker grants on sighting this mark
        // when none of the relation-keyed thoughts below apply to the
        // viewer (or none are set at all) - the flat, "everyone reacts the
        // same way" reaction this field always meant. Null = no reaction.
        public ThoughtDef viewerReactionThought;

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 §1.5, relation-keyed viewer
        // reactions: ThoughtWorker_ViewedGraffitiMark checks the viewing
        // pawn's relation to the mark's Filth_Mark provenance (maker,
        // makerFaction, makerIdeo, subject) against these, in this priority
        // order, and falls back to viewerReactionThought if none match or
        // the mark carries no provenance (e.g. it predates this pass, or
        // its placer never stamped a maker). All null-safe: a mark with no
        // relation fields set behaves exactly as it did before this item.
        public ThoughtDef onViewSubject;         // I am the named subject (shaming tier)
        public ThoughtDef onViewOwnFaction;      // maker is my own faction
        public ThoughtDef onViewSameIdeo;        // maker's ideo == my ideo
        public ThoughtDef onViewOtherIdeo;       // maker has a different ideo than mine
        public ThoughtDef onViewHostileMaker;    // maker's faction is hostile to mine

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

        // §2.3 / fork F6 (recommendation stands): "protect own+Devotional
        // from auto-clean". AutoCleanProtection.cs's Harmony prefix on
        // WorkGiver_CleanFilth.HasJobOnThing reads this OR checks
        // category==Devotional - true for either means the home-area
        // ambient clean scan skips this mark; a player's explicit
        // right-click "Clean now" (forced=true) always still works, which
        // is this engine's "scrub designator override" (no separate
        // designator needed - vanilla's own forced-clean path already is
        // one).
        public bool protectedFromAutoClean;
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

                bool anyReaction = ext.viewerReactionThought != null || ext.onViewSubject != null ||
                    ext.onViewOwnFaction != null || ext.onViewSameIdeo != null ||
                    ext.onViewOtherIdeo != null || ext.onViewHostileMaker != null;

                if (ext.visibility == GraffitiVisibility.ClanOnly && !anyReaction)
                {
                    Log.Warning("[RimMandrake.Graffiti] " + def.defName +
                        " sets visibility=ClanOnly but has no reaction ThoughtDef (flat or " +
                        "relation-keyed) - the gate has nothing to grant and will never do anything.");
                }

                // Third mis-wire shape: ThoughtWorker_ViewedGraffitiMark.CurrentStateInternal
                // is only ever invoked for a ThoughtDef whose <workerClass> IS that class
                // (ThoughtDef.IsSituational / .Worker gate on workerClass, not thoughtClass -
                // verified against RimWorld/ThoughtDef.cs). Pointing any reaction field at
                // any other ThoughtDef compiles and loads clean but the reaction never fires.
                foreach (ThoughtDef reaction in new[] { ext.viewerReactionThought, ext.onViewSubject,
                    ext.onViewOwnFaction, ext.onViewSameIdeo, ext.onViewOtherIdeo, ext.onViewHostileMaker })
                {
                    if (reaction != null && reaction.workerClass != typeof(ThoughtWorker_ViewedGraffitiMark))
                    {
                        Log.Warning("[RimMandrake.Graffiti] " + def.defName +
                            " points a reaction field at " + reaction.defName +
                            " but that ThoughtDef's workerClass is not ThoughtWorker_ViewedGraffitiMark - " +
                            "it will never fire from viewing this mark.");
                    }
                }

                // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 verify step 5: "every Sigil-form mark has
                // a frame texture."
                if (ext.form == GraffitiForm.Sigil && ext.sigilTierA && string.IsNullOrEmpty(ext.sigilFrameTexPath))
                {
                    Log.Warning("[RimMandrake.Graffiti] " + def.defName +
                        " is form=Sigil, sigilTierA=true but names no sigilFrameTexPath - " +
                        "it will render with no frame.");
                }
            }
            foreach (ThoughtDef td in DefDatabase<ThoughtDef>.AllDefsListForReading)
            {
                if (td.workerClass != typeof(ThoughtWorker_ViewedGraffitiMark)) continue;
                bool anyMarkPointsHere = false;
                foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
                    if (ext == null) continue;
                    if (ext.viewerReactionThought == td || ext.onViewSubject == td ||
                        ext.onViewOwnFaction == td || ext.onViewSameIdeo == td ||
                        ext.onViewOtherIdeo == td || ext.onViewHostileMaker == td)
                    {
                        anyMarkPointsHere = true;
                        break;
                    }
                }
                if (!anyMarkPointsHere)
                {
                    Log.Warning("[RimMandrake.Graffiti] " + td.defName +
                        " uses ThoughtWorker_ViewedGraffitiMark but no mark's " +
                        "ModExtension_Graffiti reaction field points at it - unreachable.");
                }
            }
        }
    }
}
