using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 4 (placers) / fork F2
    // (recommendation stands, "raid tagging on exit only" - not on arrival,
    // not mid-raid): a departing hostile pawn leaves its gang's mark near
    // where it stood, tinted by its own faction/ideo via Filth_Mark's
    // ordinary provenance stamp.
    //
    // Hook point: RimWorld.Planet.CaravanExitMapUtility.
    // ExitMapAndCreateCaravan(IEnumerable<Pawn> pawns, Faction faction,
    // PlanetTile exitFromTile, PlanetTile directionTile, PlanetTile
    // destinationTile, bool sendMessage) - RimSage-verified this pass to be
    // the CORE implementation (the other overload, taking a Direction8Way,
    // just computes a directionTile and calls this one - patching the core
    // overload catches every caller regardless of which one they used). A
    // PREFIX, not a postfix: `pawns` are still spawned with valid
    // Position/Map when this runs - the method's own body is what calls
    // pawn.ExitMap() partway through, despawning them - the same "capture
    // before the real call mutates state" shape BreachBiasHook.cs uses on
    // its own hook point, just on the other side (before instead of after).
    [StaticConstructorOnStartup]
    public static class RaidExitTaggerMod
    {
        static RaidExitTaggerMod()
        {
            var harmony = new Harmony("mandrake.rm.graffiti.raidexittagger");
            harmony.Patch(
                AccessTools.Method(typeof(CaravanExitMapUtility), nameof(CaravanExitMapUtility.ExitMapAndCreateCaravan),
                    new[] { typeof(IEnumerable<Pawn>), typeof(Faction), typeof(PlanetTile), typeof(PlanetTile), typeof(PlanetTile), typeof(bool) }),
                prefix: new HarmonyMethod(typeof(RaidExitTaggerMod), nameof(Prefix)));
        }

        public static void Prefix(IEnumerable<Pawn> pawns, Faction faction)
        {
            if (!RM_GraffitiSettings.paintingEnabled || !RM_GraffitiSettings.raidExitTaggingEnabled)
            {
                return;
            }
            if (faction == null || faction == Faction.OfPlayer || !faction.HostileTo(Faction.OfPlayer))
            {
                return;
            }
            foreach (Pawn pawn in pawns)
            {
                if (pawn == null || !pawn.Spawned || pawn.Map == null)
                {
                    continue;
                }
                TryTagNear(pawn);
            }
        }

        private static void TryTagNear(Pawn pawn)
        {
            Map map = pawn.Map;
            IntVec3 cell;
            if (!GraffitiJobUtility.TryFindWallMarkCellNear(pawn.Position, map, out cell))
            {
                return;
            }
            ThingDef markDef = GraffitiPool.PickForRaidExit(pawn);
            if (markDef == null)
            {
                return;
            }
            Filth_Mark.MakeMark(cell, map, markDef, pawn);
        }
    }
}
