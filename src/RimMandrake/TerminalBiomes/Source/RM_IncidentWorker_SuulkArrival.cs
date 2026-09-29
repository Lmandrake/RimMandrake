using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D2c. "Arrives... on a several-day incident
    // cadence (frequency scaling with the player's mobile-glower count —
    // one-line hook, per the light-economy spec)." Same CanFireNowSub/
    // TryExecuteWorker seam RUT_IncidentWorker_WalkerSurfacing already proves
    // in this repo. The frequency-scaling hook lives in CanFireNowSub: more
    // player-owned glowers on the map raises the chance this particular roll
    // actually passes, on top of the storyteller's own base chance/refire
    // timer — the "one-line hook" the spec calls for, without inventing a
    // second cadence system.
    //
    // "Never a swarm: one, sometimes two" (design D2b) — TryExecuteWorker
    // spawns a second suulk only once the same glower count clears a second,
    // higher threshold.
    public class RM_IncidentWorker_SuulkArrival : IncidentWorker
    {
        private const int PairGlowerThreshold = 4;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_TerminalBiomesSettings.SuulkActive)
            {
                return false;
            }
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            Map map = parms.target as Map;
            if (map?.Biome == null)
            {
                return false;
            }
            int glowers = CountPlayerGlowers(map);
            if (glowers <= 0)
            {
                return false; // nothing to graze yet
            }
            float chance = Mathf.Clamp01(RM_TerminalBiomesSettings.suulkFrequencyMultiplier
                * Mathf.Min(1f, 0.4f + glowers * 0.15f));
            return Rand.Chance(chance);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            PawnKindDef kindDef = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Suulk");
            if (kindDef == null)
            {
                return false;
            }
            if (!CellFinder.TryFindRandomEdgeCellWith((IntVec3 c) => c.Standable(map) && !c.Fogged(map),
                map, CellFinder.EdgeRoadChance_Ignore, out IntVec3 cell))
            {
                return false;
            }

            int count = CountPlayerGlowers(map) >= PairGlowerThreshold && Rand.Bool ? 2 : 1;
            List<Pawn> spawned = new List<Pawn>(count);
            for (int i = 0; i < count; i++)
            {
                IntVec3 spawnCell = (i == 0) ? cell : CellFinder.RandomClosewalkCellNear(cell, map, 3);
                Pawn suulk = PawnGenerator.GeneratePawn(kindDef);
                GenSpawn.Spawn(suulk, spawnCell, map);
                spawned.Add(suulk);
            }

            // Jump target must cover every suulk spawned, not just the last
            // one -- a two-suulk letter that only points at the second pawn
            // strands the first from the letter's own click-to-jump.
            Find.LetterStack.ReceiveLetter("RM_SuulkArrivalLabel".Translate(),
                "RM_SuulkArrivalText".Translate(), LetterDefOf.NeutralEvent, new LookTargets(spawned));
            return true;
        }

        private static int CountPlayerGlowers(Map map)
        {
            List<Thing> allThings = map.listerThings.AllThings;
            int count = 0;
            for (int i = 0; i < allThings.Count; i++)
            {
                Thing t = allThings[i];
                if (t.Faction != Faction.OfPlayer)
                {
                    continue;
                }
                CompGlower glower = t.TryGetComp<CompGlower>();
                if (glower != null && glower.GlowRadius > 0f)
                {
                    count++;
                }
            }
            return count;
        }
    }
}
