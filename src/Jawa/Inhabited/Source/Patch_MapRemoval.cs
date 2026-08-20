using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace Inhabited
{
    /// <summary>
    /// The survivors go back into the world. The dead do not.
    ///
    /// WHY A PATCH AND NOT A HOOK. MapParent has Notify_MyMapAboutToBeRemoved,
    /// which is exactly the right moment -- but a WorldObject_Inhabited is a plain
    /// WorldObject by design, and the map a player lands on belongs to whatever
    /// else owns that tile. So we take the moment itself.
    ///
    /// WHY THIS EXACT MOMENT AND NOT ONE STEP LATER. Game.DeinitAndRemoveMap runs:
    ///
    ///     map.Parent.Notify_MyMapAboutToBeRemoved()
    ///     MapDeiniter.Deinit(map, notifyPlayer)      &lt;- FIRST ACT: PassPawnsToWorld
    ///     maps.Remove(map) ... map.Dispose()
    ///
    /// and PassPawnsToWorld despawns every pawn on the map and hands it to
    /// WorldPawns. After that the cast is no longer enumerable as "the people
    /// standing at this place", and WorldPawnGC is free to collect them. A prefix
    /// on DeinitAndRemoveMap is the last instant at which they are all still
    /// spawned, alive and identifiable by their Lord.
    ///
    /// A Harmony patch that matches nothing throws at startup, unlike an XML one.
    /// That is the desired behaviour here: if this target is ever renamed, the
    /// mod must fail loudly rather than quietly forget everybody.
    /// </summary>
    [HarmonyPatch(typeof(Game), nameof(Game.DeinitAndRemoveMap))]
    public static class Patch_Game_DeinitAndRemoveMap
    {
        [HarmonyPrefix]
        public static void RecallInhabitants(Map map)
        {
            if (map == null)
            {
                return;
            }
            WorldObject_Inhabited place = Find.WorldObjects?.WorldObjectAt<WorldObject_Inhabited>(map.Tile);
            if (place == null || place.roster == null)
            {
                return;
            }

            List<Pawn> ours = map.mapPawns.AllPawnsSpawned
                .Where(p => p != null
                            && !p.Dead
                            && p.GetLord() != null
                            && p.GetLord().LordJob is LordJob_Inhabited)
                .ToList();

            for (int i = 0; i < ours.Count; i++)
            {
                Pawn p = ours[i];
                p.DeSpawnOrDeselect();
                if (!place.roster.TryAdd(p, canMergeWithExistingStacks: false))
                {
                    Log.Warning("[Inhabited] could not return " + p.LabelShort + " to the roster of "
                                + place.LabelCap + "; they are left to the world.");
                }
            }

            // No death record, no memorial, no ledger, no counter. The roster IS
            // the survivors and the absence is the memory.
            if (place.SoulCount == 0 && place.state == InhabitedState.Inhabited)
            {
                place.state = InhabitedState.Abandoned;
            }
        }
    }
}
