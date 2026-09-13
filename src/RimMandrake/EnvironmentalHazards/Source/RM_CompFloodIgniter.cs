using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S1 spike (sump_kit_spec.md "the poured moat + command
    // ignition"). Generic terrain-flood ignition: props name which
    // TerrainDefs conduct (the sump's tar moat today; any future flammable-
    // line content reuses this unchanged, per the spec's own framing).
    //
    // Flood-fill uses map.floodFiller (Verse/FloodFiller.cs, verified,
    // decompile) seeded from the conducting cells adjacent to the parent
    // building — the fuse post's own cell need not itself be a conducting
    // terrain. Ignition is staggered by queueing matched cells and draining
    // a few per tick (INVENTED rate, cellsPerSecond) rather than igniting
    // the whole flood-filled area in one tick, matching the sheet's "a
    // staggered ignition front."
    //
    // ❓ resolved (item verify section, S1's own named engine claim — "verify
    // raider pathfinding actually prices fire cells high enough to refuse
    // crossing"): CONFIRMED, and it sharpens the spec's plan. Read directly
    // from the 1.6 decompile, Verse.AI/PathGrid.cs:179-204
    // (CalculatedCostAt, perceivedStatic branch): for a cell and its 8
    // neighbours, a live ground Fire (`Fire` with `parent == null`, i.e. not
    // a pawn-attached fire) adds +1000 path cost on its own cell and +150 on
    // each adjacent cell, against a 10000 impassable threshold
    // (PathGrid.ImpassableCost). This IS vanilla's real fire-avoidance
    // mechanism — pawns strongly prefer routing around a burning cell and
    // will only cross if no better path exists — and it needs NO comp code
    // to work.
    //
    // BUT it only fires for Things whose runtime type is exactly
    // RimWorld.Fire (the `fire = list[k] as Fire` check at PathGrid.cs:193).
    // The spec's own "burning wall" (RUT_TarBlaze, "a short-lived Thing:
    // fire graphic + stock CompReleaseGas") as sketched is a plain custom
    // Thing, not a Fire subclass — it would get NONE of this avoidance
    // automatically. This is therefore a real, load-bearing build decision
    // the spec did not have before: RUT_TarBlaze must either (a) subclass
    // Fire (or wrap/keep a genuine vanilla Fire instance alive on the cell
    // for the full 12-24h burn), or (b) carry its own pathCost/impassable-
    // while-alive exactly as the spec's own stated fallback already
    // proposed. Flagged here rather than assumed; this comp only starts the
    // real vanilla Fire via FireUtility.TryStartFireIn (which the pathing
    // bonus DOES cover) — RUT_TarBlaze's own class is content/build work,
    // out of this spike's scope.
    public class CompProperties_FloodIgniter : CompProperties
    {
        /// <summary>Which TerrainDefs this igniter's flood-fill crosses.
        /// Generic by design — the sump's tar moat is the first content
        /// user, not the only one.</summary>
        public List<TerrainDef> conductingTerrains = new List<TerrainDef>();

        /// <summary>INVENTED (spec S1: "~10 cells/sec").</summary>
        public float cellsPerSecond = 10f;

        public float fireSize = 1f;

        /// <summary>Flood-fill safety cap — an engineering guard against a
        /// pathological map, not a lore/tuning number.</summary>
        public int maxCells = 4000;

        public CompProperties_FloodIgniter()
        {
            compClass = typeof(RM_CompFloodIgniter);
        }
    }

    public class RM_CompFloodIgniter : ThingComp
    {
        private readonly Queue<IntVec3> pendingIgnition = new Queue<IntVec3>();
        private float cellAccumulator;

        public CompProperties_FloodIgniter Props => (CompProperties_FloodIgniter)props;

        public bool Igniting => pendingIgnition.Count > 0;

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }

            if (parent.Faction == Faction.OfPlayer)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RM_IgniteMoat".Translate(),
                    defaultDesc = "RM_IgniteMoatDesc".Translate(),
                    action = BeginIgnition
                };
            }
        }

        public void BeginIgnition()
        {
            if (parent.Map == null || Props.conductingTerrains.NullOrEmpty())
            {
                return;
            }

            bool PassCheck(IntVec3 c)
            {
                if (!c.InBounds(parent.Map))
                {
                    return false;
                }
                TerrainDef terrain = c.GetTerrain(parent.Map);
                return terrain != null && Props.conductingTerrains.Contains(terrain);
            }

            List<IntVec3> starts = GenAdj.CardinalDirections
                .Select(d => parent.Position + d)
                .Where(PassCheck)
                .ToList();

            if (starts.Count == 0)
            {
                return;
            }

            parent.Map.floodFiller.FloodFill(
                IntVec3.Invalid,
                PassCheck,
                (IntVec3 c) => pendingIgnition.Enqueue(c),
                Props.maxCells,
                rememberParents: false,
                extraRoots: starts);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (pendingIgnition.Count == 0 || parent.Map == null)
            {
                cellAccumulator = 0f;
                return;
            }

            cellAccumulator += Props.cellsPerSecond / 60f; // GenTicks.TicksPerRealSecond
            while (cellAccumulator >= 1f && pendingIgnition.Count > 0)
            {
                cellAccumulator -= 1f;
                IntVec3 cell = pendingIgnition.Dequeue();
                FireUtility.TryStartFireIn(cell, parent.Map, Props.fireSize, parent);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!Igniting)
            {
                return null;
            }
            return "RM_MoatIgniting".Translate() + ": " + pendingIgnition.Count;
        }
    }
}
