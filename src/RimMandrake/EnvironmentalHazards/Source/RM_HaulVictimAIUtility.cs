using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F9. The victim-finder RUT_HaulPawnAndExit.cs's
    // own header names as owed: "RimWorld/KidnapAIUtility.cs's
    // TryFindGoodKidnapVictim filters pawn.RaceProps.Humanlike in its own
    // validator - not reusable for thornbugs as written... a new predicate
    // (crib StealAIUtility's targeting shape, generalized to downed
    // tamed/wild animals) is needed for the ants' LordJob."
    //
    // This generalizes KidnapAIUtility.TryFindGoodKidnapVictim
    // (RimWorld/KidnapAIUtility.cs:10, confirmed real, re-verified against
    // the live 1.6/Odyssey decompile this pass) by replacing its hardcoded
    // "pawn.RaceProps.Humanlike" filter with a caller-supplied predicate,
    // so the exact same reservation/reachability/downed/hostility shape
    // works for a non-humanlike target - a thornbug clamped to a tree, not
    // a colonist. Kept RM_-tier (this kit knows nothing about thornbugs or
    // Fever Wood) per the fever_wood_kit_spec.md's own naming rule:
    // "generic mechanisms are RM_, content defs exposing them are RUT_".
    //
    // Callers require the victim to already be Downed (the ants' own
    // "unclamp stun" job runs first, per the spec - not built this pass)
    // because RUT_HaulPawnAndExit reuses JobDriver_Kidnap's exact FailOn
    // ("!Takee.Downed && Takee.Awake()"), so an awake, undowned victim
    // would immediately fail the haul job it is handed to.
    //
    // SPIKE SCOPE: proves the utility compiles against the real 1.6 API
    // (Faction.OfPlayer, Faction.HostileTo, PawnCapacityDefOf.Manipulation,
    // GenClosest.ClosestThingReachable - all confirmed real at the same
    // call shape KidnapAIUtility itself uses). NOT done here: the LordJob/
    // LordToil that would actually call this (crib RimWorld/
    // LordToil_KidnapCover.cs's shape), the ants' FactionDef, and the
    // "unclamp stun" attack job that downs the victim before this finder
    // is asked to locate one.
    public static class RM_HaulVictimAIUtility
    {
        /// <summary>Finds the nearest reachable, already-downed,
        /// player-owned pawn matching victimFilter within maxDist of
        /// hauler - the same shape KidnapAIUtility.TryFindGoodKidnapVictim
        /// uses for a colonist, generalized so the caller decides what
        /// counts as a valid species/kind (a thornbug PawnKindDef check,
        /// once that def exists).</summary>
        public static bool TryFindGoodHaulVictim(Pawn hauler, float maxDist, Predicate<Pawn> victimFilter, out Pawn victim, List<Thing> disallowed = null)
        {
            if (victimFilter == null)
            {
                throw new ArgumentNullException(nameof(victimFilter));
            }
            if (!hauler.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || !hauler.Map.reachability.CanReachMapEdge(hauler.Position, TraverseParms.For(hauler, Danger.Some)))
            {
                victim = null;
                return false;
            }
            Predicate<Thing> validator = delegate (Thing t)
            {
                Pawn pawn = t as Pawn;
                if (pawn == null || !victimFilter(pawn))
                {
                    return false;
                }
                if (!pawn.Downed)
                {
                    return false;
                }
                if (pawn.Faction != Faction.OfPlayer)
                {
                    return false;
                }
                if (!pawn.Faction.HostileTo(hauler.Faction))
                {
                    return false;
                }
                if (!hauler.CanReserve(pawn))
                {
                    return false;
                }
                if (disallowed != null && disallowed.Contains(pawn))
                {
                    return false;
                }
                return true;
            };
            victim = (Pawn)GenClosest.ClosestThingReachable(hauler.Position, hauler.Map, ThingRequest.ForGroup(ThingRequestGroup.Pawn), PathEndMode.OnCell, TraverseParms.For(TraverseMode.NoPassClosedDoors, Danger.Some), maxDist, validator);
            return victim != null;
        }
    }
}
