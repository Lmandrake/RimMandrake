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
    // The instant god-mode deconstruct branch in
    // `Designator_Deconstruct.DesignateThing` bypasses the job entirely and
    // is deliberately NOT covered here -- it is a debug-only path.
    //
    // Filtered to the player's own, non-blueprint buildings (`!def.IsFrame`
    // excludes an in-progress construction frame, which was never a
    // "repairable" thing to begin with).
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
