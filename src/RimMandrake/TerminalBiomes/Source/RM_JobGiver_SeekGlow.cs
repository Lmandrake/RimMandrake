using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.Shared;
using Verse.AI;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D2c/§D4c — "build it once as
    // RM_JobGiver_SeekGlow, shared." Finds the brightest player-owned glower
    // on the map (a lamp, a cultivated light, a sun-sphere — anything at all
    // with a live CompGlower, so a future "dearest lamp" def is covered for
    // free per the C4 ruling: "the dearest lamp needs a guard, not an
    // exemption") and returns a feed job on it.
    //
    // Inserted GLOBALLY via RM_ThinkTree_SeekGlow (insertTag Animal_PreMain —
    // the same vanilla extension point CreatureBehaviors' own
    // RM_ThinkTree_VerminBehaviors already proves safe for this exact
    // shape): no-ops instantly for any pawn whose race lacks
    // RM_SeekGlowExtension, so only the suulk is ever affected.
    public class RM_JobGiver_SeekGlow : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_SeekGlowExtension ext = pawn.def?.GetModExtension<RM_SeekGlowExtension>();
            if (ext == null || pawn.Map == null)
            {
                return null;
            }
            // GREYSEA_LAMP_RESPONSE_BUILD_1 delta 1: the gate is per race now,
            // not the suulk's toggle for everyone.
            if (!GateOpen(ext.gate))
            {
                return null;
            }
            if (!ext.onlyBiome.NullOrEmpty() && pawn.Map.Biome?.defName != ext.onlyBiome)
            {
                return null;
            }
            if (!Rand.Chance(ext.seekChancePerCheck))
            {
                return null;
            }

            Thing best = FindBrightestPlayerGlower(pawn, ext, out bool deepfire);
            if (best == null)
            {
                return null;
            }
            // DEEPFIRE_WORLD_LIGHT_1 (a): drawn to deepfire, never grazing it (a fed-out proxy would only respawn)
            if (ext.mode == "drawn" || deepfire)
            {
                JobDef bask = DefDatabase<JobDef>.GetNamedSilentFail("RM_BaskInGlow");
                return bask == null ? null : JobMaker.MakeJob(bask, best);
            }
            return JobMaker.MakeJob(RM_TerminalBiomesJobDefOf.RM_FeedOnGlow, best);
        }

        private static bool GateOpen(string gate)
        {
            switch (gate)
            {
                case "greyDrawn":
                    return RM_TerminalBiomesSettings.GreyLampDrawnActive;
                default:
                    return RM_TerminalBiomesSettings.SuulkActive;
            }
        }

        // Map-wide scan: the population of things carrying a live CompGlower
        // on one map is a handful of lamps, not thousands of things, so this
        // is cheap even at this JobGiver's own rare-fire rate (gated above by
        // seekChancePerCheck). DEEPFIRE_WORLD_LIGHT_1 (a): a lit deepfire light
        // counts whoever owns it — its proxies are factionless — read from the
        // shared light ledger's "deepfire" tag (LuminousPigment sets it).
        private static Thing FindBrightestPlayerGlower(Pawn pawn, RM_SeekGlowExtension ext, out bool bestIsDeepfire)
        {
            Map map = pawn.Map;
            List<Thing> allThings = map.listerThings.AllThings;
            Thing best = null;
            bestIsDeepfire = false;
            float bestRadius = ext.minGlowRadiusToTarget;
            bool deepfireDraws = RM_TerminalBiomesSettings.seekGlowDrawnToDeepfire;
            for (int i = 0; i < allThings.Count; i++)
            {
                Thing t = allThings[i];
                bool player = t.Faction == Faction.OfPlayer;
                if (!player && !deepfireDraws)
                {
                    continue;
                }
                CompGlower glower = t.TryGetComp<CompGlower>();
                if (glower == null || glower.GlowRadius <= bestRadius)
                {
                    continue;
                }
                bool deepfire = deepfireDraws && LightLedger.HasTag(glower, "deepfire");
                if (!player && !deepfire)
                {
                    continue;
                }
                if ((ext.mode == "drawn" || deepfire) && !glower.Glows)
                {
                    continue;
                }
                if (t.IsForbidden(pawn) || !pawn.CanReach(t, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                best = t;
                bestRadius = glower.GlowRadius;
                bestIsDeepfire = deepfire;
            }
            return best;
        }
    }
}
