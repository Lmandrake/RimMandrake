using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Puts the company on the ground.
    ///
    /// THE MUTATOR PLACES THE SET; THIS PLACES THE COMPANY. The whole link chain
    /// is shipped and needs no patch:
    ///
    ///     TileMutatorDef.extraGenSteps  ->  this GenStep  ->  LordMaker.MakeNewLord
    ///           (the PLACE)                  (the bridge)          (the CAST)
    ///
    /// MapGenerator.GenerateMap concatenates every active mutator's extraGenSteps
    /// into the step list before sorting by order, so naming this step's GenStepDef
    /// in a mutator is the entire wiring. Seven shipped GenSteps already call
    /// MakeNewLord in exactly this shape; GenStep_SitePawns is the closest model
    /// and this follows its spawn-then-AddPawn sequence rather than passing a
    /// startingPawns list.
    ///
    /// Nothing here generates a place. If no WorldObject_Inhabited sits on this
    /// tile, the step does nothing and says nothing -- a map with no cast is a
    /// perfectly ordinary map.
    /// </summary>
    public class GenStep_InhabitedCast : GenStep
    {
        /// <summary>Any stable value unique among GenSteps; it only seeds the RNG.</summary>
        public override int SeedPart => 1104459301;

        public override void Generate(Map map, GenStepParams parms)
        {
            WorldObject_Inhabited place = Find.WorldObjects.WorldObjectAt<WorldObject_Inhabited>(map.Tile);
            if (place == null)
            {
                return;
            }
            if (!place.castInstantiated)
            {
                place.InstantiateCast();
            }
            SpawnCast(place, map);
        }

        private static void SpawnCast(WorldObject_Inhabited place, Map map)
        {
            ThingOwner<Pawn> roster = place.roster;
            if (roster == null || roster.Count == 0)
            {
                place.state = InhabitedState.Abandoned;
                return;
            }

            IntVec3 work = WorkSpot(map);
            IntVec3 home = HomeSpot(map, work);

            Lord lord = LordMaker.MakeNewLord(place.Faction,
                new LordJob_Inhabited(home, work, place.placeDef), map);

            // Copy first: spawning removes each pawn from the owner we are reading.
            List<Pawn> arriving = roster.InnerListForReading.ToList();
            for (int i = 0; i < arriving.Count; i++)
            {
                Pawn p = arriving[i];
                if (p == null || p.Dead)
                {
                    continue;
                }
                if (!roster.Remove(p))
                {
                    continue;
                }
                IntVec3 cell = CellFinder.RandomSpawnCellForPawnNear(work, map);
                GenSpawn.Spawn(p, cell, map);
                lord.AddPawn(p);
            }
        }

        /// <summary>
        /// Where the day is spent. A placeholder anchor until the PLACE layer --
        /// the tile mutator that actually builds the refinery -- can hand over the
        /// real one.
        /// </summary>
        private static IntVec3 WorkSpot(Map map)
        {
            IntVec3 c = map.Center;
            return c.Standable(map) ? c : CellFinder.RandomNotEdgeCell(12, map);
        }

        /// <summary>Where the night is spent.</summary>
        private static IntVec3 HomeSpot(Map map, IntVec3 work)
        {
            return CellFinder.TryRandomClosewalkCellNear(work, map, 18, out IntVec3 result)
                ? result
                : work;
        }
    }
}
