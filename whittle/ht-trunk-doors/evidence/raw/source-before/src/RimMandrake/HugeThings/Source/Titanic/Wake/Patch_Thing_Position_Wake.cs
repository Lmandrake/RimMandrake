using HarmonyLib;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The wake's one and only hook into movement. Patches the Thing.Position
    /// SETTER (Verse/Thing.cs) rather than any PathFollower method: vanilla's
    /// PathFollower changes position by plain assignment
    /// ("this.pawn.Position = nextCell;" - confirmed by reading
    /// Pawn_PathFollower.TryEnterNextPathCell), so this fires on every real
    /// cell-to-cell step regardless of Large Pawns' presence or its own
    /// PathFollower patches, and needs zero knowledge of either.
    ///
    /// Also fires once on initial spawn placement (Position is set before
    /// Spawned becomes true in that call, so the pawn.Spawned guard in
    /// CompTitanicWake.Notify_EnteredCell skips that one harmlessly) and on any
    /// teleport - both acceptable, neither is the steady-state case this exists
    /// for.
    ///
    /// A Harmony target that has moved fails loudly at startup (PatchAll throws
    /// if the property is gone), which is the desired behaviour here.
    /// </summary>
    [HarmonyPatch(typeof(Thing))]
    [HarmonyPatch(nameof(Thing.Position), MethodType.Setter)]
    internal static class Patch_Thing_Position_Wake
    {
        // TITAN_WAKE_FIXES_1 (B3.7): the 1.6 setter returns early when the value is unchanged, but a Postfix runs anyway, so the old
        // position and map are captured here and the wake fires only on a real move on the same map. (B2.4): the settings gate is
        // read before any per-pawn work, so with the wake off a pawn move costs one static read.
        internal struct Before
        {
            public IntVec3 pos;
            public Map map;
        }

        private static void Prefix(Thing __instance, out Before __state)
        {
            __state = default;
            if (!RimMandrake.HugeThings.RM_HugeThingsSettings.WakeActive) return;
            if (__instance is Pawn pawn && pawn.Spawned)
            {
                __state.pos = pawn.Position;
                __state.map = pawn.Map;
            }
        }

        private static void Postfix(Thing __instance, Before __state)
        {
            if (__state.map == null) return;
            if (__instance is Pawn pawn && pawn.Spawned && pawn.Map == __state.map && pawn.Position != __state.pos)
            {
                pawn.TryGetComp<CompTitanicWake>()?.Notify_EnteredCell();
            }
        }
    }
}
