using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1. design/Jawa/divine_satiation_engine.md
    // §4c: "Side WITH the neutral droids (welcome them, bring them online,
    // integrate them) -> Ohm grows more pleased and harmonious." This hook
    // covers the "bring online" half only (a droid joining the player) --
    // the "side against / keep offline" half has no single choke point to
    // hook (it is an absence of action, not an event) and is out of scope
    // here.
    //
    // Verified against decompiled source (RimSage): `Pawn.SetFaction(Faction
    // newFaction, Pawn recruiter)` is vanilla's single choke point for a pawn
    // changing allegiance, used by every recruitment/reprogramming path in
    // this campaign (e.g. JobDriver_DWDataSpike.cs's own
    // `target.SetFaction(Faction.OfPlayer, pawn)`). Deliberately does NOT
    // reference Droidworks (RimStarWars tier) directly -- this stays a
    // self-contained observer on the vanilla API, filtered by the same
    // `Humanlike && !IsFlesh` race-property test
    // Patch_RelationsForNonFleshHumanlike (Droidworks) already uses to
    // identify a droid pawn, so it needs no compile-time dependency on that
    // mod's assembly.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.SetFaction))]
    public static class Patch_DroidOnline
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn __instance, Faction newFaction)
        {
            if (newFaction != Faction.OfPlayer) return;
            if (__instance?.RaceProps == null) return;
            if (!__instance.RaceProps.Humanlike) return;
            if (__instance.RaceProps.IsFlesh) return; // not a droid by this campaign's convention

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Ohm, EventMagnitude.Large,
                "droid brought online: " + __instance.LabelCap);
        }
    }
}
