using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_KIT_BUILD_1, mechanic 6 (webwork_kit_spec.md §6, "margin creep")
    // — "a biome's contents advance from a map edge on maps adjacent to that
    // biome." Generic and name-blind: it reads an RM_FrontCreepExtension off
    // a NEIGHBOR world tile's biome (never off this map's own biome, and this
    // class names no biome of its own), so any future biome can opt in by
    // adding the extension to its own BiomeDef — nothing here is Webwork-
    // specific except the extension the owner will actually attach.
    //
    // World map is never repainted (map.Biome is untouched) — the encroachment
    // is map-local scatter only, honoring the no-worldgen ruling (CLAUDE.md).
    //
    // Feeds SHOKKWEAVE_SOLE_SOURCE_1's ruled-in border creep-web harvest route
    // (owner card 4, 2026-09-11: "yields, with teeth") — that item's own
    // patch attaches the yield/emergent-spawn comp to the spawned Things;
    // this component only places them, carrying no yield of its own (the
    // sole-source guard: a chewed/destroyed sense-web node drops nothing).
    public class RM_MapComponent_FrontCreep : MapComponent
    {
        private static readonly List<PlanetTile> tmpNeighbors = new List<PlanetTile>();

        private RM_FrontCreepExtension activeFront;
        private Rot4 frontEdge;
        private bool checkedForFront;
        private int currentDepth;
        private int ticksUntilAdvance;

        public RM_MapComponent_FrontCreep(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            FindFront();
        }

        private void FindFront()
        {
            if (checkedForFront)
            {
                return;
            }
            checkedForFront = true;

            if (map?.Tile == null || !map.Tile.Valid)
            {
                return;
            }

            tmpNeighbors.Clear();
            Find.WorldGrid.GetTileNeighbors(map.Tile, tmpNeighbors);

            RM_FrontCreepExtension found = null;
            List<float> headings = new List<float>();
            foreach (PlanetTile neighbor in tmpNeighbors)
            {
                BiomeDef neighborBiome = Find.WorldGrid[neighbor]?.PrimaryBiome;
                RM_FrontCreepExtension ext = neighborBiome?.GetModExtension<RM_FrontCreepExtension>();
                if (ext == null)
                {
                    continue;
                }
                found = ext;
                headings.Add(Find.WorldGrid.GetHeadingFromTo(map.Tile, neighbor));
            }

            if (found == null || headings.Count == 0)
            {
                return; // no bordering front biome; this map never creeps
            }

            activeFront = found;
            // Rot4.FromAngleFlat buckets a 0=N/clockwise heading to the
            // nearest cardinal exactly as vanilla map-facing code does
            // elsewhere; a local square map has no literal correspondence to
            // a world tile's hex-neighbor direction, so this is the same
            // order-of-magnitude compromise TileMutatorWorker_MixedBiome
            // makes when it turns a heading into a map-local band axis.
            // ❓INVENTED simplification — the spec names no exact geometry.
            frontEdge = Rot4.FromAngleFlat(GenMath.MeanAngle(headings));
            if (ticksUntilAdvance <= 0)
            {
                ticksUntilAdvance = activeFront.advanceIntervalTicks;
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!RM_CreatureBehaviorsSettings.frontCreepEnabled)
            {
                return;
            }
            if (activeFront == null)
            {
                return;
            }

            ticksUntilAdvance--;
            if (ticksUntilAdvance > 0)
            {
                return;
            }
            ticksUntilAdvance = activeFront.advanceIntervalTicks;

            Advance();
        }

        private void Advance()
        {
            if (currentDepth >= activeFront.maxBandDepth)
            {
                return;
            }
            currentDepth++;
            SpawnBand(currentDepth);
        }

        private void SpawnBand(int depth)
        {
            if (activeFront.frontThingDefNames.NullOrEmpty())
            {
                return;
            }

            CellRect rect = CellRect.WholeMap(map);
            CellRect bandRect = InsetFromEdge(rect, frontEdge, depth);

            foreach (IntVec3 cell in bandRect.GetEdgeCells(frontEdge))
            {
                if (!cell.InBounds(map) || !cell.Standable(map))
                {
                    continue;
                }
                if (!Rand.Chance(RM_CreatureBehaviorsSettings.frontCreepRateMultiplier * activeFront.spawnDensity))
                {
                    continue;
                }

                string defName = activeFront.frontThingDefNames.RandomElement();
                ThingDef thingDef = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                if (thingDef == null)
                {
                    continue;
                }
                if (cell.GetThingList(map).Any(t => t.def == thingDef))
                {
                    continue;
                }

                GenSpawn.Spawn(thingDef, cell, map);
            }
        }

        // The rect whose near edge sits `depth` cells in from the map's true
        // edge on the front's side — SpawnBand walks that rect's own edge,
        // so successive calls trace successively deeper bands rather than
        // re-spawning on the same row.
        private static CellRect InsetFromEdge(CellRect whole, Rot4 edge, int depth)
        {
            int inset = depth - 1;
            return edge.AsInt switch
            {
                0 => new CellRect(whole.minX, whole.maxZ - inset, whole.Width, 1), // North
                1 => new CellRect(whole.maxX - inset, whole.minZ, 1, whole.Height), // East
                2 => new CellRect(whole.minX, whole.minZ + inset, whole.Width, 1), // South
                _ => new CellRect(whole.minX + inset, whole.minZ, 1, whole.Height), // West
            };
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // activeFront/frontEdge/checkedForFront are re-derived fresh by
            // FinalizeInit on every load (idempotent, cheap); only the
            // progress counters need to survive a save.
            Scribe_Values.Look(ref currentDepth, "currentDepth", 0);
            Scribe_Values.Look(ref ticksUntilAdvance, "ticksUntilAdvance", 0);
        }
    }
}
