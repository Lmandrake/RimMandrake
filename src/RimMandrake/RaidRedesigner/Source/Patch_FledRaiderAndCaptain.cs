using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.RaidRedesigner
{
    // Verified against 1.6 source (RimSage):
    //   - Verse/Pawn.cs: `public virtual void ExitMap(bool allowedToJoinOrCreateCaravan, Rot4 exitDir)`
    //     (lines ~3763-3855) fires for every pawn leaving a map by this route,
    //     hostile raiders included, and already calls
    //     `Find.WorldPawns.PassToWorld(this)` at its own tail -- our Postfix
    //     runs strictly after that (see WorldPawnPinning.cs).
    //   - Source/RimWorld/IncidentWorker_RaidEnemy.cs:131 detects the raid's
    //     own leader-present pawn with `pawns.Find((Pawn x) => x.Faction.leader == x)`
    //     -- the same check is reused here for CAPTAIN, matching design/Jawa/
    //     proposals/plot_mechanisms_wave.md §1.4's "Faction.leader == pawn (or
    //     our own captain flag)" note; not an invented flag.
    //   - RimWorld/FactionUtility.cs: `public static bool HostileTo(this Faction fac, Faction other)`.
    //   - Verse/Map.cs: `public bool IsPlayerHome`.
    //   - Verse/RaceProperties.cs: `public bool Humanlike => (int)intelligence >= 2;`.
    //
    // A Prefix captures the pawn's Map BEFORE the method runs, because
    // ExitMap despawns the pawn partway through its own body -- by Postfix
    // time `__instance.Map` is already null.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.ExitMap))]
    public static class Patch_FledRaiderAndCaptain
    {
        [HarmonyPrefix]
        public static void Prefix(Pawn __instance, out Map __state)
        {
            __state = __instance.Map;
        }

        [HarmonyPostfix]
        public static void Postfix(Pawn __instance, Map __state)
        {
            Pawn pawn = __instance;
            Map map = __state;
            if (map == null || !map.IsPlayerHome) return;
            if (pawn.Dead) return; // a corpse leaving the map is not "fled alive"
            if (pawn.RaceProps == null || !pawn.RaceProps.Humanlike) return;
            if (pawn.Faction == null || !pawn.Faction.HostileTo(Faction.OfPlayer)) return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            bool isCaptain = pawn.Faction.leader == pawn;
            RoleTag role = isCaptain ? RoleTag.Captain : RoleTag.FledRaider;
            int tick = Find.TickManager.TicksGame;
            string summary = isCaptain
                ? "led a raid on us and left the field alive"
                : "raided us and fled the field alive";

            roster.RecordEncounter(pawn, pawn.Faction, role, tick, summary,
                grudgeDelta: isCaptain ? 10 : 5,
                notabilityDelta: isCaptain ? 20 : 5,
                pin: true);
        }
    }
}
