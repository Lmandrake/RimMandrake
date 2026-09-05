using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.RaidRedesigner
{
    // Verified against 1.6 source (RimSage), Source/RimWorld/KidnappedPawnsTracker.cs:33:
    // `public void Kidnap(Pawn pawn, Pawn kidnapper)` on `KidnappedPawnsTracker`
    // (the type of `Faction.kidnapped`, RimWorld/Faction.cs:28). The design
    // doc's literal citation, "Faction.kidnapped.Kidnap", is the real call --
    // e.g. Verse/Pawn.cs:3784, `base.Faction.kidnapped.Kidnap(pawn, this)`,
    // fired mid-way through the KIDNAPPER's own Pawn.ExitMap call, before
    // that call reaches its own PassToWorld tail. `kidnapper` can be null
    // (e.g. Verse/MapDeiniter.cs:158's map-abandonment path, or
    // IncidentWorker_CaravanDemand.cs:246) -- those have no roster subject.
    //
    // Not pinned here: at the moment this fires the kidnapper is still mid-
    // ExitMap (see WorldPawnPinning's comment) and typically still Spawned,
    // so PinForever would correctly no-op anyway; Patch_FledRaiderAndCaptain's
    // own postfix on that same outer ExitMap call pins it once safe.
    [HarmonyPatch(typeof(KidnappedPawnsTracker), nameof(KidnappedPawnsTracker.Kidnap))]
    public static class Patch_ColonistKidnapped
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn pawn, Pawn kidnapper)
        {
            if (kidnapper?.Faction == null) return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            string victimName = pawn?.LabelShortCap ?? "one of ours";
            roster.RecordEncounter(kidnapper, kidnapper.Faction, RoleTag.Kidnapper,
                Find.TickManager.TicksGame, "kidnapped " + victimName,
                grudgeDelta: 25, notabilityDelta: 15, pin: false);
        }
    }
}
