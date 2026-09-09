using RimMandrake.Property;
using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.RaidRedesigner
{
    // Verified against src/RimMandrake/Property/Source/PropertyEngine.cs:
    // `public static TakingEvent Fire(TakingEvent evt)` is the fabric's one
    // event-spine entry point. It fills in `evt.PriorClaim` and
    // `evt.WasAuthorized` itself and RETURNS THE SAME `evt` INSTANCE (the
    // Harmony __result IS evt) -- see TakingEvent.cs: "Filled in by
    // PropertyEngine.Fire and are readable afterward."
    //
    // design/Jawa/proposals/plot_mechanisms_wave.md §1.4's row: "a
    // caravan/visitor is robbed | mandrake.rm.property's TakingEvent resolved
    // against a non-player pawn ... | BETRAYED_TRADER". Read literally
    // against PropertyEngine.Fire's actual switch: an unauthorized Take or
    // Strip against a claim held by a Pawn whose Faction is not the player's
    // is exactly "we took from a visitor without their leave" -- the
    // BETRAYED_TRADER moment. Property ships NO Harmony hooks of its own (its
    // own About.xml: "No Harmony hooks auto-fire TakingEvents from vanilla
    // actions"), so nothing else in the mod stack observes Fire() calls; this
    // patch is additive, not a duplicate.
    //
    // RAIDREDESIGNER_HARD_PROPERTY_REF_1: mandrake.rm.property is only a soft
    // `loadAfter` in this mod's About.xml, not a hard <modDependencies> entry
    // -- and the other seven capture hooks in this assembly have nothing to
    // do with Property, so making it a hard dependency would force players
    // to enable an unrelated mod just to get FledRaider/Captain/prisoner/
    // kidnap tracking. So this patch is applied MANUALLY (via TryPatch,
    // called from RaidRedesignerMod's static constructor) instead of the
    // usual [HarmonyPatch] attribute + PatchAll autodiscovery. An attribute
    // reference is resolved eagerly -- Harmony's PatchAll must read every
    // type's custom attributes to find patch classes, which would force the
    // CLR to load RimMandrakeProperty.dll right there and throw
    // (TypeLoadException/FileNotFoundException) for the WHOLE assembly's
    // PatchAll call if Property is inactive, killing all eight hooks, not
    // just this one. TryPatch is only ever called after confirming
    // ModsConfig.IsActive("mandrake.rm.property"), so PropertyEngine is only
    // ever touched when the mod that ships it is actually active.
    public static class Patch_CaravanRobbed
    {
        public static void TryPatch(Harmony harmony)
        {
            harmony.Patch(
                AccessTools.Method(typeof(PropertyEngine), nameof(PropertyEngine.Fire)),
                postfix: new HarmonyMethod(typeof(Patch_CaravanRobbed), nameof(Postfix)));
        }

        public static void Postfix(TakingEvent __result)
        {
            TakingEvent evt = __result;
            if (evt == null || evt.WasAuthorized) return;
            if (evt.Act != TakingAct.Take && evt.Act != TakingAct.Strip) return;
            if (!evt.PriorClaim.HasValue) return;

            ClaimantRef claimant = evt.PriorClaim.Value.Claimant;
            if (claimant.Kind != ClaimantKind.Pawn || claimant.Pawn == null) return;

            Faction victimFaction = claimant.Pawn.Faction;
            if (victimFaction == null || victimFaction == Faction.OfPlayer) return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            roster.RecordEncounter(claimant.Pawn, victimFaction, RoleTag.BetrayedTrader,
                evt.Tick, "we took from them without their leave",
                grudgeDelta: 15, notabilityDelta: 5, pin: false);
        }
    }
}
