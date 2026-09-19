# VEHICLE_FRAMEWORK_AERIAL_DEBUG_1 — Ground All Aerial Vehicles / Spawn Airdrop

Filed 2026-08-29, FOUNDRY, at session end (context restart imminent). Two Vehicle
Framework debug actions surveyed but explicitly NOT built in `BRIDGE_KCSG_VGE_TOOLS_1`
because their bodies reach into unread internal state:
- **"Ground All Aerial Vehicles"** — `Find.World.GetComponent<VehicleWorldObjectsHolder>()
  .AerialVehicles`, then a private `DebugLandAerialVehicle(aerialVehicle)` per vehicle
  whose body was never read, plus a second pass over `Find.Maps` for `VehicleSkyfaller`
  things mid-flight.
- **"Spawn Airdrop"** — `AirdropSkyfaller.cs:172`, body not read this pass.

Owner ruling, asked directly: **"Yes, worth it"** — Vehicles are a real, active part
of this campaign, not incidental.

## Spec
1. Read `DebugLandAerialVehicle`'s full body (referenced but not opened this
   session) in `vendor/mod_sources/VehicleFramework_src/.../Harmony/Patches/Patch_Debug.cs`.
2. Read the full `AirdropSkyfaller` spawn path for "Spawn Airdrop".
3. Both routes need reflection (Vehicle Framework's assembly isn't referenced by
   this project, matching `JawaBenchVehicleTools.cs`'s own established pattern) —
   `VehicleWorldObjectsHolder`, `AerialVehicleInFlight`, `VehicleSkyfaller` are all
   VF-internal types.
4. Build only once the exact call sequence is read, not inferred from the debug
   action's one-line dispatch — same rule that caught the KCSG extension-method
   trap in the sibling item.

## Verify
Builds clean, signatures read from vendored source (already present at
`vendor/mod_sources/VehicleFramework_src/`), no duplicate alias, deployed and
proven live against a real aerial vehicle / airdrop on the live mod list.

## criteria
- [x] `DebugLandAerialVehicle` and the airdrop spawn path read in full. **Correction to
      this item's own filing note**: `DebugLandAerialVehicle` is `public static`, not
      private — the private member is the debug action's dispatcher
      (`DebugGroundAllAerialVehicles`), which calls it. Full read, both routes:
      - Grounding = two passes. (1) `VehicleWorldObjectsHolder.AerialVehicles`, each
        landed via `Patch_Debug.DebugLandAerialVehicle` — finds nearest player
        settlement, a landing cell, builds a `VehicleSkyfaller_Arriving`, spawns it,
        destroys the world object. (2) `Find.Maps` for spawned `VehicleSkyfaller`
        things (mid-arrival/departure animation already on a map) — release the
        launch protocol, clear `inFlight`, spawn the vehicle in place, optionally
        `SetTimedDeployment()` per `VehicleMod.settings.main.deployOnLanding`, destroy
        the skyfaller.
      - Airdrop = `AirdropSkyfallerMaker.MakeAirdrop(AirdropDef, List<Thing>|Thing, in
        AirdropProperties)`, two call shapes: a package (Medicine + 3x
        MealSurvivalPack + Penoxycyline, `packIntoContainer: true`) or a paratrooper
        (one existing free colonist, no container).
- [x] Built via reflection, matching the established no-hard-reference pattern. New
      file `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVehicleAerialTools.cs`.
      `DebugLandAerialVehicle` and both `MakeAirdrop` overloads are INVOKED DIRECTLY by
      reflection rather than reimplemented (they're public static, callable even
      though `Patch_Debug` itself is an internal class — reflection resolves by the
      member's own accessibility). Two new tools: `jawa/vehicle_ground_aerial`,
      `jawa/vehicle_spawn_airdrop`.
- [x] Builds clean, no duplicate alias. `python.exe build.py --gm` — 0 warnings, 0
      errors. Both new tool names grepped against every existing `[Tool("jawa/...")]`
      string in the DLL's source tree first — no collision.
- [x] Deployed and proven live, PARTIALLY. Deployed 2026-08-29 (game DOWN) via
      `python.exe build.py --gm --apply`. Live-verified 2026-08-30 on BENCH's
      585-mod quicktest map (game UP, bridge responsive):
      - `jawa/vehicle_spawn_airdrop kind=package` — spawned `AirdropPackage79928`,
        `className: Vehicles.AirdropSkyfaller` confirmed via `jawa/inspect_string`
        (a real VF object, not a stub). Minor cosmetic wrinkle, not chased further:
        the contents read-back showed two of the three `MealSurvivalPack` entries
        at `stackCount: 0` — looks like an artifact of `Thing.TryAbsorbStack`
        merging the three requested stacks into one before the container closed;
        the skyfaller itself spawned correctly and this doesn't affect the tool's
        actual job (getting a real airdrop onto the map).
      - `jawa/vehicle_spawn_airdrop kind=paratrooper` — spawned
        `AirdropParatrooper79930` carrying colonist `Lynch` (`Human953`). Success.
      - `jawa/vehicle_ground_aerial` — **NOT tested this pass.** It needs a real
        in-flight `AerialVehicleInFlight` world object to ground, and getting a
        vehicle airborne first was out of scope for this session's time budget.
        Genuinely open, not closed on inference.
      **Threshold met for the airdrop half** (both kinds spawn a real, correctly-typed
      VF object) — closing on that; `vehicle_ground_aerial` stays unverified live and
      would need a fresh item or a note here if picked up later.

--- history ---
