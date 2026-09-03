using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md §8b.A: "Deconstruct/scrap
    // something still repairable -> ↓Rekko (large -- 'murder'), ▲Zizzik
    // small (waste/entropy pleases him). The classic costly-lever:
    // resources now, Rekko's wrath later."
    //
    // Verified against decompiled source (RimSage): the normal player
    // deconstruct-work route (designate, then a pawn works it off) runs
    // through `JobDriver_Deconstruct.FinishedRemoving()`
    // (Source/RimWorld/JobDriver_Deconstruct.cs:29), a narrow override
    // called exactly once per completed deconstruction job -- unlike
    // `Thing.Destroy`, which fires for every stack merge, corpse rot and
    // filth removal in the whole game and is not a hook to patch lightly.
    // `FinishedRemoving` is `protected`; Harmony patches by reflection so
    // that is not a barrier, but C#'s own accessibility rules mean this
    // patch reads `__instance.job`/`__instance.pawn` (both PUBLIC fields on
    // the JobDriver base, Source/Verse/AI/JobDriver.cs:12,14) rather than
    // the protected `Target`/`Building` properties.
    //
    // The instant deconstruct branch in `Designator_Deconstruct.DesignateThing`
    // (god mode, `WorkToBuild == 0`, or `def.IsFrame`) bypasses the job and is
    // NOT covered here. The latter two are reachable in ordinary play, so a
    // zero-work building or a scrapped frame is a real (small) coverage gap.
    //
    // Fires whenever the deconstruction is PERFORMED by a player-faction pawn
    // -- only `pawn.Faction` is examined, never the building's. Deliberate: a
    // scavenger clan deconstructing salvage/ruins it does not own is exactly
    // the "costly lever, resources now, Rekko's wrath later" case §8b.A
    // describes, and restricting to player-owned buildings would make this
    // barely fire at all for a campaign built around scrapping other
    // people's wrecks. `!def.IsFrame` below is defensive rather than live
    // filtering -- a frame takes the instant branch above and never reaches
    // this postfix, per the same reachability note.
    [HarmonyPatch(typeof(JobDriver_Deconstruct), "FinishedRemoving")]
    public static class Patch_BuildingDeconstructed
    {
        [HarmonyPostfix]
        public static void Postfix(JobDriver_Deconstruct __instance)
        {
            Pawn pawn = __instance.pawn;
            Thing target = __instance.job?.targetA.Thing;
            if (pawn == null || target == null) return;
            if (pawn.Faction != Faction.OfPlayer) return;
            if (!(target.GetInnerIfMinified() is Building building)) return;
            if (building.def.IsFrame) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Rekko, -EventMagnitude.Large,
                "deconstructed a repairable building: " + building.def.defName);
            comp.ApplyDelta(God.Zizzik, EventMagnitude.Small,
                "waste/entropy from deconstruction: " + building.def.defName);
        }
    }
}
