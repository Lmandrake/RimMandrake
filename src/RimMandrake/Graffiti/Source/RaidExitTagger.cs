using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 4 (placers) / fork F3 (ruled 2026-10-09, "raid tagging on exit only" - not on
    // arrival, not mid-raid): a departing hostile gang leaves its marks near where each member stood when the raid turned to
    // leave, tinted by its own faction/ideo via Filth_Mark's ordinary provenance stamp.
    //
    // Hook point: Verse.AI.Group.Lord.GotoToil(LordToil), the one place every lord changes toil. A raid "exits" the moment its
    // lord moves from a non-leaving toil onto a leaving one (RM_GraffitiKernel's IsLeavingToil list: the ExitMap family and
    // PanicFlee) - the raiders are still on the map, standing where the assault left them, beside the colony's walls.
    //
    // GRAFFITI_V1_LIVE_PROOF_1: the hook used to be CaravanExitMapUtility.ExitMapAndCreateCaravan, which a hostile raider never
    // reaches: Pawn.ExitMap routes there only if CanExitMapAndJoinOrCreateCaravanNow, and that needs a colonist or a player
    // caravan to join (FindCaravanToJoinFor returns null for any other faction) - decomp rw16 Verse/Pawn.cs ExitMap,
    // RimWorld.Planet/CaravanExitMapUtility.cs. Raiders walking off the edge are simply despawned, so no raid ever tagged.
    [StaticConstructorOnStartup]
    public static class RaidExitTaggerMod
    {
        static RaidExitTaggerMod()
        {
            var harmony = new Harmony("mandrake.rm.graffiti.raidexittagger");
            harmony.Patch(
                AccessTools.Method(typeof(Lord), nameof(Lord.GotoToil), new[] { typeof(LordToil) }),
                prefix: new HarmonyMethod(typeof(RaidExitTaggerMod), nameof(Prefix)),
                postfix: new HarmonyMethod(typeof(RaidExitTaggerMod), nameof(Postfix)));
        }

        /// <summary>The leaving toils, by their vanilla class (RimWorld + Verse.AI.Group, rw16); a modded subclass counts too.</summary>
        public static bool IsLeavingToil(LordToil toil)
        {
            return toil is LordToil_ExitMap || toil is LordToil_ExitMapAndDefendSelf || toil is LordToil_ExitMapAndEscortCarriers
                || toil is LordToil_ExitMapRandom || toil is LordToil_ExitMapNear || toil is LordToil_ExitMapTraderFighting
                || toil is LordToil_PanicFlee;
        }

        public static void Prefix(Lord __instance, out bool __state)
        {
            __state = __instance != null && IsLeavingToil(__instance.CurLordToil);
        }

        public static void Postfix(Lord __instance, LordToil newLordToil, bool __state)
        {
            if (__instance == null || __instance.Map == null)
            {
                return;
            }
            Faction faction = __instance.faction;
            if (!RM_GraffitiKernel.RaidExitTags(RM_GraffitiSettings.paintingEnabled, RM_GraffitiSettings.raidExitTaggingEnabled, faction != null,
                faction != null && faction == Faction.OfPlayer, faction != null && faction.HostileTo(Faction.OfPlayer)))
            {
                return;
            }
            if (!RM_GraffitiKernel.TurnsToLeave(__state, IsLeavingToil(newLordToil)))
            {
                return;
            }
            // a copy: a tag never changes the lord's pawns, but MakeMark's going-over destroys things and this must not care
            foreach (Pawn pawn in __instance.ownedPawns.ToArray())
            {
                if (pawn == null || !pawn.Spawned || pawn.Map != __instance.Map || pawn.Downed || pawn.Dead
                    || pawn.RaceProps == null || !pawn.RaceProps.Humanlike)
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
            ThingDef markDef = GraffitiPool.PickForRaidExit(pawn, GraffitiJobUtility.WallRoom(cell, map));
            if (markDef == null)
            {
                return;
            }
            Filth_Mark.MakeMark(cell, map, markDef, pawn);
        }
    }
}
