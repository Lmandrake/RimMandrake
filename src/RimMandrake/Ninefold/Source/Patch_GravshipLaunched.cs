using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1. design/Jawa/divine_satiation_engine.md:
    // "Ta'Baa's satiation erodes purely with time rooted... each launch/
    // relocation resets his erosion and spikes satiation" (§, "Ta'Baa's
    // independent clock"). The erosion half lives in GameComponent_Ninefold's
    // own tick (StepRootedErosion); this hook is only the launch/relocation
    // half, via Notify_Launched (which resets the clock AND spikes satiation
    // in one call, so nothing can do one without the other).
    //
    // Verified against decompiled source (RimSage): `CompLaunchable.TryLaunch
    // (PlanetTile destinationTile, TransportersArrivalAction arrivalAction)`
    // is vanilla's single entry point for every launch this comp can make --
    // shuttle, transport pod, and gravship alike (Odyssey's gravship uses the
    // same CompLaunchable). This deliberately does NOT try to distinguish a
    // full-colony gravship relocation from a routine shuttle/pod hop: "leaving"
    // is Ta'Baa's whole domain (flight, the refusal to root), so any launch
    // reasonably fits it, even if a full-colony move would ideally warrant a
    // larger spike than a routine trade run -- a first-pass simplification,
    // not a design decision about which launches "count".
    [HarmonyPatch(typeof(CompLaunchable), nameof(CompLaunchable.TryLaunch))]
    public static class Patch_GravshipLaunched
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            GameComponent_Ninefold.Instance?.Notify_Launched("launch/relocation");
        }
    }
}
