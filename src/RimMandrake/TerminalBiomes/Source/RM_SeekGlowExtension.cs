using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1, design doc §D2c/§D4c: "build it once as
    // RM_JobGiver_SeekGlow, shared." Tunables for the shared light-brain —
    // RM_JobGiver_SeekGlow finds the target, RM_JobDriver_FeedOnGlow does the
    // feeding. Attach to a RACE ThingDef (not the PawnKindDef): the JobGiver
    // is inserted GLOBALLY via RM_ThinkTree_SeekGlow (insertTag
    // Animal_PreMain, the same vanilla extension point CreatureBehaviors'
    // RM_ThinkTree_VerminBehaviors already uses) and no-ops instantly for
    // every race but the suulk — same "no-op without the extension" shape as
    // RM_SeekShadeExtension/RM_GnawTargetExtension.
    public class RM_SeekGlowExtension : DefModExtension
    {
        // Chance per AI check that this pawn actually looks for a glower at
        // all (RM_JobGiver_SeekShade's own shape) — keeps the map-wide scan
        // in RM_JobGiver_SeekGlow rare-fire even though it walks every
        // player-owned Thing on the map.
        public float seekChancePerCheck = 0.05f;

        // Below this GlowRadius a glower is not worth crossing the map for —
        // a guttering stub, already nearly fed out.
        public float minGlowRadiusToTarget = 1.5f;

        // Feeding cadence: every ticksBetweenFeeds, the target's GlowRadius
        // drops by glowRadiusLossPerFeed. Design D2b: "dims it as it feeds
        // (radius shrinking over minutes — visible)." Shipped defaults (180
        // ticks ~= 3 real seconds, 0.15 loss) empty a radius-12 lamp over a
        // few real-time minutes of uninterrupted feeding.
        public int ticksBetweenFeeds = 180;
        public float glowRadiusLossPerFeed = 0.15f;

        // Below this radius the target is destroyed outright — design D2b,
        // "destroys it if left."
        public float destroyBelowRadius = 0.3f;

        // GREYSEA_LAMP_RESPONSE_BUILD_1 (danger pass §2.1 deltas 1-2):
        // "feed" = the suulk's RM_FeedOnGlow; "drawn" = RM_BaskInGlow (go
        // near, linger, wander off — the lamp is bait, not food).
        public string mode = "feed";
        // Which Mod Settings switch gates this race's light-brain:
        // "suulk" (Twilight, the original) or "greyDrawn" (the Grey's layer 1).
        public string gate = "suulk";
        // When set, the brain only acts on a map of this biome.
        public string onlyBiome;
    }
}
