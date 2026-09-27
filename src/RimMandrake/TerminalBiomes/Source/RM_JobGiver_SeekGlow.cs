using System.Collections.Generic;
using RimWorld;
using Verse;
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
            if (!RM_TerminalBiomesSettings.SuulkActive)
            {
                return null; // mod option: suulk grazing disabled
            }
            RM_SeekGlowExtension ext = pawn.def?.GetModExtension<RM_SeekGlowExtension>();
            if (ext == null || pawn.Map == null)
            {
                return null;
            }
            if (!Rand.Chance(ext.seekChancePerCheck))
            {
                return null;
            }

            Thing best = FindBrightestPlayerGlower(pawn, ext);
            if (best == null)
            {
                return null;
            }
            return JobMaker.MakeJob(RM_TerminalBiomesJobDefOf.RM_FeedOnGlow, best);
        }

        // Map-wide scan: the population of things carrying a live CompGlower
        // on one map is a handful of lamps, not thousands of things, so this
        // is cheap even at this JobGiver's own rare-fire rate (gated above by
        // seekChancePerCheck).
        private static Thing FindBrightestPlayerGlower(Pawn pawn, RM_SeekGlowExtension ext)
        {
            Map map = pawn.Map;
            List<Thing> allThings = map.listerThings.AllThings;
            Thing best = null;
            float bestRadius = ext.minGlowRadiusToTarget;
            for (int i = 0; i < allThings.Count; i++)
            {
                Thing t = allThings[i];
                if (t.Faction != Faction.OfPlayer)
                {
                    continue;
                }
                CompGlower glower = t.TryGetComp<CompGlower>();
                if (glower == null || glower.GlowRadius <= bestRadius)
                {
                    continue;
                }
                if (t.IsForbidden(pawn) || !pawn.CanReach(t, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                best = t;
                bestRadius = glower.GlowRadius;
            }
            return best;
        }
    }
}
