using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_POOL_DEFENCE_1 — the trigger half.
    //
    // Owner, 2026-09-26: "Touching a brine pool directly does the same
    // thing." And, RULED the same day (Q2, sheet §4b): "salt chimneys ALSO
    // crystallise, at shorter range — the plume is a standing hazard cluster
    // … chimneys are the visible teacher of a mechanism the pools deliver
    // invisibly."
    //
    // ⇒ Two triggers, one consequence (RM_Building_BrineEncasement):
    //     POOL    — standing on terrain tagged RM_GreyBrinePool: certain.
    //     CHIMNEY — within ChimneyHazardRadius of an RM_SaltChimney: a roll
    //               per sweep, so a pawn gets a beat to walk out, which is
    //               exactly what "the visible teacher" means. The sheet's own
    //               principle for this biome is "the tell that lets the
    //               observant survive."
    //
    // ════════════════════════════════════════════════════════════════════
    // 🔴 ONLY HUMANLIKES AND MECHS ARE ENCASED. Animals are not, and that is
    // a decision, not an omission.
    // ════════════════════════════════════════════════════════════════════
    // His sentence is about "the player". Encasing wildlife as well would be
    // fictionally tidy and mechanically ruinous: RM_Essarn and RM_Oomal are
    // waterSeeker animals on this very floor, they path into standing water
    // by design, and within a season the basin would be a wall of jackets
    // that also walls the loot in. So a wild animal that enters a pool simply
    // dies of it — which is still "everything that enters dies", the sheet's
    // §3 line — and the statuary the player finds is the one the map
    // generator placed (GenStep_GreySeaFloorDressing's jacket ring), not a
    // live accumulation.
    //
    // ════════════════════════════════════════════════════════════════════
    // SCOPE AND COST
    // ════════════════════════════════════════════════════════════════════
    // ⚠️ A MapComponent is instantiated on EVERY map in the game, so the
    // first line of the sweep is a biome check and the second is a settings
    // check. On any map that is not a Grey Sea floor this component costs one
    // string comparison every 60 ticks and nothing else.
    //
    // ⛔ It deliberately does NOT read the terrain by defName. The tag
    // RM_GreyBrinePool is the contract (RM_GreySeaTerrains.xml puts it on
    // both pool grades and on nothing else), so a later pass can add a third
    // pool terrain without touching this file.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_BrineCrystallisation : MapComponent
    {
        private const int SweepInterval = 60;
        private const string PoolTag = "RM_GreyBrinePool";
        private const float ChimneyHazardRadius = 2.4f;
        private const float ChimneyChancePerSweep = 0.10f;

        private static readonly List<Pawn> tmpPawns = new List<Pawn>();

        public MapComponent_BrineCrystallisation(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % SweepInterval != 0)
            {
                return;
            }
            if (!RM_SeaFloorIdentity.IsFloorOf(map, "RM_GreySea"))
            {
                return;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyPoolDefenceEnabled)
            {
                return;
            }

            ThingDef jacketDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BrineEncasement");
            if (jacketDef == null)
            {
                return;
            }
            ThingDef chimneyDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SaltChimney");

            // Copy: encasing despawns a pawn, which mutates the live list.
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);

            foreach (Pawn p in tmpPawns)
            {
                if (p == null || !p.Spawned || p.Dead)
                {
                    continue;
                }

                bool inPool = p.Position.GetTerrain(map).HasTag(PoolTag);
                bool inPlume = !inPool && chimneyDef != null && NearChimney(p.Position, chimneyDef);

                if (!inPool && !inPlume)
                {
                    continue;
                }

                // Wildlife is killed by the brine, never jacketed — see the
                // header for why this is deliberate.
                if (!p.RaceProps.Humanlike && !p.RaceProps.IsMechanoid)
                {
                    if (inPool)
                    {
                        p.Kill(null);
                    }
                    continue;
                }

                if (inPlume && !Rand.Chance(ChimneyChancePerSweep))
                {
                    continue;
                }

                BrineEncasementUtility.TryEncase(p, map);
            }
            tmpPawns.Clear();
        }

        private bool NearChimney(IntVec3 c, ThingDef chimneyDef)
        {
            foreach (Thing t in map.listerThings.ThingsOfDef(chimneyDef))
            {
                if (c.DistanceTo(t.Position) <= ChimneyHazardRadius)
                {
                    return true;
                }
            }
            return false;
        }

        // GREYSEA_RULED_CONTENT_1: the encasement call itself moved to
        // BrineEncasementUtility.TryEncase, shared with
        // RM_CompPoolSentinelSquirt's third trigger — see that file's header.
    }
}
