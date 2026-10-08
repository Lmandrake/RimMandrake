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
        private static void Postfix(Thing __instance)
        {
            if (__instance is Pawn pawn && pawn.Spawned)
            {
                pawn.TryGetComp<CompTitanicWake>()?.Notify_EnteredCell();
            }
        }
    }
}
