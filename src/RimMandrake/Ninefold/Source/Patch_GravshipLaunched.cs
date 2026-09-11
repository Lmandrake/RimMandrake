using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1. design/Jawa/divine_satiation_engine.md:
    // "Ta'Baa's satiation erodes purely with time rooted... each launch/
    // relocation resets his erosion and spikes satiation" (§, "Ta'Baa's
    // independent clock"). The erosion half lives in GameComponent_Ninefold's
    // own tick (StepRootedErosion); these hooks are only the launch/relocation
    // half, via Notify_Launched (which resets the clock AND spikes satiation
    // in one call, so nothing can do one without the other).
    //
    // "Leaving" is Ta'Baa's whole domain (flight, the refusal to root), so any
    // departure feeds him. RimWorld has TWO structurally separate departure
    // paths and they share no code, so there are two patches here:
    //
    //   * CompLaunchable.TryLaunch       -- transport pods and shuttles
    //   * WorldComponent_GravshipController.InitiateTakeoff
    //                                    -- Odyssey's gravship
    //
    // Verified against decompiled source (RimSage): Building_GravEngine is
    // `: Building, IRenameable` with NO CompLaunchable, and
    // CompProperties_Launchable appears only on AncientTransportPod /
    // AncientTransportPod_Special / TransportPod / Shuttle -- never on the
    // gravship. A gravship departure therefore never reaches TryLaunch, and a
    // pod launch never reaches InitiateTakeoff, so the two patches cannot
    // double-feed one departure.
    //
    // Neither patch distinguishes a full-colony relocation from a routine
    // shuttle hop by magnitude -- a first-pass simplification, not a design
    // decision about which launches "count".

    // ---- transport pods / shuttles -----------------------------------------
    [HarmonyPatch(typeof(CompLaunchable), nameof(CompLaunchable.TryLaunch))]
    public static class Patch_TransporterLaunched
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

    // ---- the gravship -------------------------------------------------------
    // NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1, owner ruling: hook the gravship at
    // its own takeoff entry point rather than scoping this feature to pods.
    //
    // The real symbol is WorldComponent_GravshipController.InitiateTakeoff(
    // Building_GravEngine engine, PlanetTile targetTile) -- Building_GravEngine
    // itself has no InitiateTakeoff (verified via RimSage; the engine exposes
    // CanLaunch(CompPilotConsole), not a takeoff call).
    //
    // Failure semantics, read from the decompiled source rather than assumed:
    // InitiateTakeoff is `void`, takes no ref/out parameter and has no throw
    // path, so nothing about the CALL can report success or failure. Its whole
    // body is wrapped in `if (ModsConfig.OdysseyActive)` -- with Odyssey off it
    // silently does nothing. Every real launch-failure condition is checked
    // BEFORE the call and prevents it entirely: CompPilotConsole.CanUseNow() ->
    // Building_GravEngine.CanLaunch() (no substructure / disconnected / not
    // enough fuel / no thrusters / on cooldown / pocket map) gates the console
    // job, and the tile-picker's own validator rejects an unreachable or
    // invalid destination by returning false and continuing to target. The one
    // player call site invokes InitiateTakeoff immediately after
    // engine.ConsumeFuel(tile), i.e. after vanilla has already spent the fuel;
    // the only other call site is the skipGravshipTileSelection dev path. Once
    // InitiateTakeoff runs, the takeoff is committed.
    //
    // So the only thing a patch here must still distinguish is "the body ran"
    // from "Odyssey is inactive and it no-opped". Gate on vanilla's own
    // synchronous commit marker, the same way the pod patch gates on
    // lastLaunchTick: `cutsceneInProgress` is set true inside that Odyssey
    // block and exposed as the public static CutsceneInProgress, which the
    // rest of the engine (TickManager, UIRoot, GameEnder, save-blocking)
    // already treats as "a gravship cutscene is running". Capture it before,
    // credit Ta'Baa only on a false->true flip.
    //
    // NOT IsGravshipTravelling: the `gravship` field it reads is assigned much
    // later, in the OnGravshipCaptureComplete -> LongEventHandler callback, so
    // it is still false when this Postfix runs and would never fire.
    [HarmonyPatch(typeof(WorldComponent_GravshipController),
                  nameof(WorldComponent_GravshipController.InitiateTakeoff))]
    public static class Patch_GravshipLaunched
    {
        [HarmonyPrefix]
        public static void Prefix(out bool __state)
        {
            __state = WorldComponent_GravshipController.CutsceneInProgress;
        }

        [HarmonyPostfix]
        public static void Postfix(bool __state)
        {
            if (!__state && WorldComponent_GravshipController.CutsceneInProgress)
            {
                GameComponent_Ninefold.Instance?.Notify_Launched("gravship takeoff");
            }
        }
    }
}
