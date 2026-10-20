using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TheForge
{
    // FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND — the ummisk (owner's pick, 2026-10-20):
    // "Riding on a steam cushion where it touches the lava ... slowly wandering the edge of the
    // lava forever." Two small pieces, nothing else:
    //   1. RM_JobGiver_UmmiskLavaEdge (inserted at Animal_PreWander by
    //      Defs/ThinkTreeDefs/RM_ThinkTree_UmmiskLavaEdge.xml) — the RM_JobGiver_WanderInShadeGrid
    //      shape: a JobGiver_Wander whose wanderDestValidator only offers lava-edge cells (standable,
    //      not lava, 8-adjacent to LavaDeep). Off the edge it walks back to the nearest reachable edge
    //      cell. No lava within reach: returns null and vanilla wander runs (rechecked on a cooldown).
    //      Because the edge is read from the live terrain, the cycle's crust (temp layer over the
    //      lava) moves the edge and the ummisk follows it.
    //   2. RM_CompUmmiskSteam — the steam cushion, as a look only: while on the edge it puffs
    //      steam (vanilla FleckMaker.ThrowAirPuffUp). No terrain change, no glass trail.
    // Returns no job for any pawn without RM_UmmiskExtension, so the global insert is safe.
    // Toggles: "Ummisk keeps to the lava edge", "Ummisk steam cushion" (RM_TheForgeMod.cs).
    // All numbers PROVISIONAL (first guesses, unmeasured in play).

    public class RM_UmmiskExtension : DefModExtension
    {
        public int edgeSearchRadius = 40;          // PROVISIONAL; GenRadial caps near 56
        public int noEdgeRecheckTicks = 2500;      // PROVISIONAL; one in-game hour
    }

    public static class RM_UmmiskUtility
    {
        public static bool EdgeOn => RM_TheForgeSettings.Active(RM_TheForgeSettings.ummiskLavaEdgeEnabled);
        public static bool SteamOn => RM_TheForgeSettings.Active(RM_TheForgeSettings.ummiskSteamEnabled);

        public static bool IsLava(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.GetTerrain(map) == TerrainDefOf.LavaDeep;
        }

        public static bool IsLavaEdge(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map) || IsLava(c, map) || !c.Standable(map))
            {
                return false;
            }
            for (int i = 0; i < 8; i++)
            {
                if (IsLava(c + GenAdj.AdjacentCells[i], map))
                {
                    return true;
                }
            }
            return false;
        }

        public static bool TryFindEdgeCell(Pawn pawn, int radius, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            Map map = pawn.Map;
            int n = GenRadial.NumCellsInRadius(Mathf.Min(radius, 56));
            int reachChecks = 0;
            for (int i = 1; i < n; i++)
            {
                IntVec3 c = pawn.Position + GenRadial.RadialPattern[i];
                if (!IsLavaEdge(c, map))
                {
                    continue;
                }
                if (pawn.CanReach(c, PathEndMode.OnCell, Danger.Some))
                {
                    cell = c;
                    return true;
                }
                if (++reachChecks >= 8)
                {
                    return false;
                }
            }
            return false;
        }
    }

    public class RM_JobGiver_UmmiskLavaEdge : JobGiver_Wander
    {
        public RM_JobGiver_UmmiskLavaEdge()
        {
            wanderRadius = 7f;                                  // PROVISIONAL
            ticksBetweenWandersRange = new IntRange(400, 1200); // PROVISIONAL: slow, long pauses
            expiryInterval = 600;
            wanderDestValidator = (p, c, root) => RM_UmmiskUtility.IsLavaEdge(c, p.Map);
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_UmmiskUtility.EdgeOn || pawn?.Map == null)
            {
                return null;
            }
            RM_UmmiskExtension ext = pawn.def.GetModExtension<RM_UmmiskExtension>();
            if (ext == null)
            {
                return null;
            }
            if (RM_UmmiskUtility.IsLavaEdge(pawn.Position, pawn.Map))
            {
                return base.TryGiveJob(pawn);
            }
            RM_CompUmmiskSteam comp = pawn.GetComp<RM_CompUmmiskSteam>();
            int now = Find.TickManager.TicksGame;
            if (comp != null && now < comp.noEdgeUntilTick)
            {
                return null;
            }
            if (RM_UmmiskUtility.TryFindEdgeCell(pawn, ext.edgeSearchRadius, out IntVec3 cell))
            {
                Job go = JobMaker.MakeJob(JobDefOf.GotoWander, cell);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                go.expiryInterval = 2000;
                go.checkOverrideOnExpire = true;
                return go;
            }
            if (comp != null)
            {
                comp.noEdgeUntilTick = now + ext.noEdgeRecheckTicks;
            }
            return null;
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            return pawn.Position;
        }
    }

    public class CompProperties_UmmiskSteam : CompProperties
    {
        public int steamIntervalTicks = 90;   // PROVISIONAL

        public CompProperties_UmmiskSteam()
        {
            compClass = typeof(RM_CompUmmiskSteam);
        }
    }

    public class RM_CompUmmiskSteam : ThingComp
    {
        // Not saved: a cooldown for the no-lava case; losing it on load costs one extra scan.
        public int noEdgeUntilTick;

        public CompProperties_UmmiskSteam Props => (CompProperties_UmmiskSteam)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(Props.steamIntervalTicks) || !RM_UmmiskUtility.SteamOn)
            {
                return;
            }
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                return;
            }
            if (!RM_UmmiskUtility.IsLavaEdge(pawn.Position, pawn.Map) || !pawn.Position.ShouldSpawnMotesAt(pawn.Map))
            {
                return;
            }
            FleckMaker.ThrowAirPuffUp(pawn.DrawPos, pawn.Map);
        }
    }
}
