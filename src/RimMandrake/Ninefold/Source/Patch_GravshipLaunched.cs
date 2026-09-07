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
        // TryLaunch has several early-return failure paths (unspawned, no
        // fuel, over mass, on cooldown, under roof) that still run to
        // completion with no exception -- a bare Postfix would credit
        // Ta'Baa on every failed launch ATTEMPT, not just real ones.
        //
        // 🔴 First fix (CanLaunch()-gated __state) was itself too shallow --
        // caught by adversarial review, 2026-09-07: CanLaunch() checks
        // AllLaunchablesInGroupHaveFuelForLaunch (group has ANY fuel), but
        // TryLaunch has its OWN later, stricter guard: the actual
        // destination distance against MaxLaunchDistanceAtFuelLevel(
        // MinFuelLevelInGroup, ...) -- a group with unevenly-fueled pods can
        // pass CanLaunch() and still bail at that distance check with zero
        // fuel spent and nothing spawned. Replicating vanilla's full guard
        // chain here would just be a second, drift-prone copy of it.
        //
        // Instead: gate on vanilla's OWN success marker. `lastLaunchTick`
        // (public field on CompLaunchable) is assigned unconditionally
        // immediately after EVERY guard clause passes (Spawned, group,
        // CanLaunch, AND the distance/fuel check) and BEFORE any pod is
        // processed -- it is the exact moment vanilla itself commits to the
        // launch, and CanLaunch()'s own cooldown check reads it right back,
        // so it is not an incidental field, it is vanilla's canonical
        // "did a launch actually happen" flag. Capture it before the call,
        // credit Ta'Baa only if it changed.
        [HarmonyPrefix]
        public static void Prefix(CompLaunchable __instance, out int __state)
        {
            __state = __instance.lastLaunchTick;
        }

        [HarmonyPostfix]
        public static void Postfix(CompLaunchable __instance, int __state)
        {
            if (__instance.lastLaunchTick != __state)
            {
                GameComponent_Ninefold.Instance?.Notify_Launched("launch/relocation");
            }
        }
    }
}
