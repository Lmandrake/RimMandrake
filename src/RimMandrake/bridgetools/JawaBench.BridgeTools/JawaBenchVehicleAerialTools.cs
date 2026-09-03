// JawaBenchVehicleAerialTools.cs - force-land Vehicle Framework aerial vehicles and
// spawn VF airdrops from outside the game, mirroring the "Ground All Aerial Vehicles"
// and "Spawn Airdrop" debug actions.
//
// VEHICLE_FRAMEWORK_AERIAL_DEBUG_1 - "unread private landing logic" is now read, at:
//   vendor/mod_sources/VehicleFramework_src/Vehicle-Framework-fd5ed722ce214836d4c283832865dfa5966f1e4e/
//     Source/Vehicles/Harmony/Patches/Patch_Debug.cs                (grounding)
//     Source/Vehicles/CustomFeatures/AerialVehicles/Skyfaller/Airdrop/AirdropSkyfaller.cs    (airdrop)
//     Source/Vehicles/CustomFeatures/AerialVehicles/Skyfaller/SkyfallerMaker/AirdropSkyfallerMaker.cs
//
// EVERYTHING HERE IS REFLECTION, ON PURPOSE - same rule as JawaBenchVehicleTools.cs /
// JawaBenchKcsgTools.cs: the companion has to load with Vehicle Framework absent, and
// none of Vehicles.* is referenced by this project's csproj.
//
// SIGNATURES BELOW WERE READ FROM THE VENDORED SOURCE, NOT GUESSED:
//   Vehicles.Patch_Debug.DebugLandAerialVehicle(AerialVehicleInFlight)   public static
//     -- INVOKED DIRECTLY by reflection rather than reimplemented. The class itself is
//     `internal`, but this member is declared `public` - reflection resolves by the
//     member's own accessibility, which GetMethod(..., BindingFlags.Public, ...) finds
//     regardless of the containing type's visibility. Calling the real method IS "the
//     debug action's own dispatch", not an approximation of it - same principle as
//     JawaBenchKcsgTools.cs calling the exact CleanRect->Generate sequence.
//   Vehicles.World.VehicleWorldObjectsHolder : Verse.WorldComponent (vanilla base)
//     .AerialVehicles         PROPERTY -> List<AerialVehicleInFlight>
//   Vehicles.VehicleSkyfaller : Verse.Thing (public abstract)  -- the SECOND half of
//     "Ground All Aerial Vehicles": skyfallers already mid-arrival/departure on a map,
//     distinct from the AerialVehicleInFlight world objects above.
//     .vehicle                FIELD    Vehicles.VehiclePawn
//   Vehicles.VehiclePawn
//     .CompVehicleLauncher    PROPERTY -> Vehicles.CompVehicleLauncher
//   Vehicles.CompVehicleLauncher
//     .launchProtocol         FIELD    -> Vehicles.LaunchProtocol
//     .inFlight                FIELD    bool
//     .SetTimedDeployment()    METHOD   public
//   Vehicles.LaunchProtocol
//     .Release()               METHOD   public virtual
//   Vehicles.VehicleMod.settings.main.deployOnLanding  -- best-effort read (defaults
//     false if the chain does not resolve); gates whether a landed vehicle's colonists
//     auto-deploy, matching the debug action's own check.
//   Vehicles.AirdropSkyfallerMaker
//     .MakeAirdrop(AirdropDef, List<Thing>, in AirdropProperties)  public static -> AirdropSkyfaller
//     .MakeAirdrop(AirdropDef, Thing,        in AirdropProperties)  public static -> AirdropSkyfaller
//     -- both INVOKED DIRECTLY by reflection, same reasoning as DebugLandAerialVehicle.
//   Vehicles.AirdropDef : Verse.ThingDef  -- confirmed in source, so the def itself
//     needs NO reflection: DefDatabase<ThingDef>.GetNamedSilentFail("AirdropPackage" /
//     "AirdropParatrooper") resolves it, and the returned object's runtime type IS
//     AirdropDef, which satisfies the reflected method's AirdropDef parameter.
//   Vehicles.AirdropProperties (struct): `public required float angle;`
//     `public bool packIntoContainer = false;` -- both plain FIELDS. Built via
//     Activator.CreateInstance + FieldInfo.SetValue on the boxed struct ('required' is
//     a C#11 COMPILE-TIME check only; reflection is unaffected and SetValue correctly
//     mutates a boxed value type through its box).
//
// 🔴 THE FIRST PARAMETER TYPE MUST BE Vehicles.AirdropDef, NOT Verse.ThingDef, when
// resolving the overload with GetMethod(..., Type[]) - that overload lookup requires an
// EXACT type match, no covariance, even though AirdropDef derives from ThingDef and the
// argument itself (a ThingDef reference whose runtime type is really AirdropDef) is
// accepted fine at Invoke() time.
//
// 🔴 `in AirdropProperties` IS A BYREF PARAMETER for overload-matching purposes -
// GetMethod needs `propsType.MakeByRefType()` in the signature array, but Invoke() still
// takes the boxed struct value normally in the args array; reflection handles `in` like
// any other by-ref parameter.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.
//
// STILL OWED (game is DOWN this session): "deployed and proven live against a real
// aerial vehicle / airdrop" per the item's own criteria. Everything above is read from
// source and built to compile; the live check is for the next game-up window.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags VfPubStatic = BindingFlags.Public | BindingFlags.Static;
        private const BindingFlags VfPubInst = BindingFlags.Public | BindingFlags.Instance;

        /// <summary>True when obj's type IS or DERIVES FROM the named full type name.</summary>
        private static bool IsTypeOrSubtype(object obj, string fullName)
        {
            for (Type t = obj == null ? null : obj.GetType(); t != null; t = t.BaseType)
            {
                if (t.FullName == fullName) return true;
            }
            return false;
        }

        [Tool(
            "jawa/vehicle_ground_aerial",
            Description =
                "Force-land every Vehicle Framework aerial vehicle - the exact routine " +
                "\"Ground All Aerial Vehicles\" (VF's own debug action) uses: every " +
                "world-map AerialVehicleInFlight is landed at its nearest player " +
                "settlement via Vehicles.Patch_Debug.DebugLandAerialVehicle (invoked " +
                "directly by reflection, not reimplemented), and every VehicleSkyfaller " +
                "currently spawned on a map (mid-arrival/departure animation) is released " +
                "and its vehicle spawned in place instead. *** CAN MOVE/DESTROY MULTIPLE " +
                "THINGS, NOT UNDOABLE ***. Refuses by name if Vehicle Framework is not " +
                "loaded rather than a null reference.",
            ResultDescription =
                "success, landedFromWorld (count grounded via the world-map route), " +
                "landedOnMap (count released from an in-progress skyfaller), and errors[] " +
                "for any per-item failure that did not stop the rest.")]
        public static async Task<object> VehicleGroundAerial(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type holderType = GenTypes.GetTypeInAnyAssembly("Vehicles.World.VehicleWorldObjectsHolder");
                Type aerialType = GenTypes.GetTypeInAnyAssembly("Vehicles.AerialVehicleInFlight");
                Type patchDebugType = GenTypes.GetTypeInAnyAssembly("Vehicles.Patch_Debug");
                if (holderType == null || aerialType == null || patchDebugType == null)
                    return Fail("Vehicle Framework is not loaded (Vehicles.World.VehicleWorldObjectsHolder / "
                        + "Vehicles.AerialVehicleInFlight / Vehicles.Patch_Debug not found).");

                MethodInfo landMethod = patchDebugType.GetMethod("DebugLandAerialVehicle", VfPubStatic,
                    null, new[] { aerialType }, null);
                if (landMethod == null)
                    return Fail("Vehicles.Patch_Debug.DebugLandAerialVehicle(AerialVehicleInFlight) not found by reflection.");

                MethodInfo getComponentGeneric = typeof(RimWorld.Planet.World).GetMethods(VfPubInst)
                    .FirstOrDefault(m => m.Name == "GetComponent" && m.IsGenericMethodDefinition
                        && m.GetParameters().Length == 0);
                if (getComponentGeneric == null || Find.World == null)
                    return Fail("Could not resolve World.GetComponent<T>() or no world is loaded.");

                object holder = getComponentGeneric.MakeGenericMethod(holderType).Invoke(Find.World, null);
                if (holder == null)
                    return Fail("Find.World.GetComponent<VehicleWorldObjectsHolder>() returned null.");

                var errors = new List<string>();
                int landedFromWorld = 0;

                // Snapshot first: DebugLandAerialVehicle removes from the live list as it
                // runs (AerialVehicleInFlight.ClearAndDestroy), so iterate a copy.
                var snapshot = new List<object>();
                if (PropOrNull(holder, "AerialVehicles") is IEnumerable aerialList)
                    foreach (object a in aerialList) snapshot.Add(a);

                foreach (object aerial in snapshot)
                {
                    try
                    {
                        landMethod.Invoke(null, new[] { aerial });
                        landedFromWorld++;
                    }
                    catch (Exception ex)
                    {
                        errors.Add((ex.InnerException ?? ex).Message);
                    }
                }

                // Second half of the debug action: skyfallers already mid-arrival on a map.
                int landedOnMap = 0;
                bool deployOnLanding = ReadDeployOnLandingSetting();

                foreach (Map map in Find.Maps)
                {
                    foreach (Thing thing in map.spawnedThings.ToList())
                    {
                        if (!IsTypeOrSubtype(thing, "Vehicles.VehicleSkyfaller")) continue;
                        try
                        {
                            object vehicle = FieldOrNull(thing, "vehicle");
                            if (vehicle == null) { errors.Add("VehicleSkyfaller with null 'vehicle' field."); continue; }
                            object comp = PropOrNull(vehicle, "CompVehicleLauncher");
                            if (comp == null) { errors.Add("vehicle has no CompVehicleLauncher."); continue; }

                            object launchProtocol = FieldOrNull(comp, "launchProtocol");
                            MethodInfo release = launchProtocol?.GetType()
                                .GetMethod("Release", VfPubInst, null, Type.EmptyTypes, null);
                            release?.Invoke(launchProtocol, null);
                            comp.GetType().GetField("inFlight", VfPubInst)?.SetValue(comp, false);

                            IntVec3 pos = thing.Position;
                            Map thingMap = thing.Map;
                            Rot4 rot = thing.Rotation;
                            GenSpawn.Spawn((Thing)vehicle, pos, thingMap, rot);

                            if (deployOnLanding)
                            {
                                MethodInfo setTimed = comp.GetType()
                                    .GetMethod("SetTimedDeployment", VfPubInst, null, Type.EmptyTypes, null);
                                setTimed?.Invoke(comp, null);
                            }

                            thing.Destroy();
                            landedOnMap++;
                        }
                        catch (Exception ex)
                        {
                            errors.Add((ex.InnerException ?? ex).Message);
                        }
                    }
                }

                return new
                {
                    success = true,
                    landedFromWorld,
                    landedOnMap,
                    errors = errors.Count == 0 ? null : errors,
                };
            });
        }

        private static bool ReadDeployOnLandingSetting()
        {
            try
            {
                Type modType = GenTypes.GetTypeInAnyAssembly("Vehicles.VehicleMod");
                object settings = modType?.GetField("settings", VfPubStatic)?.GetValue(null);
                object main = FieldOrNull(settings, "main");
                object flag = FieldOrNull(main, "deployOnLanding");
                return flag is bool b && b;
            }
            catch (Exception)
            {
                return false;
            }
        }

        [Tool(
            "jawa/vehicle_spawn_airdrop",
            Description =
                "Spawn a Vehicle Framework airdrop on the current map - the exact routine " +
                "\"Spawn Airdrop\" (VF's own debug action) uses. kind='package' drops a " +
                "container of MedicineIndustrial + 3x MealSurvivalPack + Penoxycyline via " +
                "AirdropSkyfallerMaker.MakeAirdrop(SkyfallerDefOf-equivalent AirdropPackage, " +
                "...). kind='paratrooper' drops one EXISTING free colonist (must already be " +
                "on the current map) via the AirdropParatrooper variant. Both call the " +
                "mod's real static maker method directly by reflection. Refuses by name if " +
                "Vehicle Framework is not loaded.",
            ResultDescription =
                "success, kind, at, spawned (thingId/def of the skyfaller), plus contents[] " +
                "(package mode) or pawn (paratrooper mode).")]
        public static async Task<object> VehicleSpawnAirdrop(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'package' or 'paratrooper'. Required.")]
            string kind = null,
            [ToolParameter(Description = "Cell to drop at, on the current map: 'x,z'. Required.")]
            string at = null,
            [ToolParameter(Description = "kind='paratrooper' only: pawn id, thingId or name of the free colonist to drop. Required for that kind.")]
            string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (string.IsNullOrEmpty(kind) || (kind != "package" && kind != "paratrooper"))
                    return Fail("'kind' must be 'package' or 'paratrooper'.");

                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map - is a game loaded?");

                IntVec3 cell;
                string cellErr;
                if (!TryParseCell(at, out cell, out cellErr))
                    return Fail(cellErr);
                if (!cell.InBounds(map))
                    return Fail("Cell " + cell + " is out of bounds for this map.");

                Type makerType = GenTypes.GetTypeInAnyAssembly("Vehicles.AirdropSkyfallerMaker");
                Type propsType = GenTypes.GetTypeInAnyAssembly("Vehicles.AirdropProperties");
                Type airdropDefType = GenTypes.GetTypeInAnyAssembly("Vehicles.AirdropDef");
                if (makerType == null || propsType == null || airdropDefType == null)
                    return Fail("Vehicle Framework is not loaded (AirdropSkyfallerMaker / AirdropProperties / AirdropDef not found).");

                string skyfallerDefName = kind == "package" ? "AirdropPackage" : "AirdropParatrooper";
                ThingDef airdropDef = DefDatabase<ThingDef>.GetNamedSilentFail(skyfallerDefName);
                if (airdropDef == null || !airdropDefType.IsInstanceOfType(airdropDef))
                    return Fail("ThingDef '" + skyfallerDefName + "' not found (or not an AirdropDef) - is Vehicle Framework's Skyfaller def loaded?");

                object props = Activator.CreateInstance(propsType);
                propsType.GetField("angle", VfPubInst)?.SetValue(props, (float)UnityEngine.Random.Range(-30, 30));
                propsType.GetField("packIntoContainer", VfPubInst)?.SetValue(props, kind == "package");

                try
                {
                    if (kind == "package")
                    {
                        var contents = new List<Thing>();
                        foreach (string defName in new[] { "MedicineIndustrial", "MealSurvivalPack", "MealSurvivalPack", "MealSurvivalPack", "Penoxycyline" })
                        {
                            ThingDef cd = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                            if (cd == null) continue; // matches source: content list is best-effort, never blocks the drop
                            contents.Add(MakeStacked(cd));
                        }

                        MethodInfo make = makerType.GetMethod("MakeAirdrop", VfPubStatic, null,
                            new[] { airdropDefType, typeof(List<Thing>), propsType.MakeByRefType() }, null);
                        if (make == null)
                            return Fail("AirdropSkyfallerMaker.MakeAirdrop(AirdropDef, List<Thing>, in AirdropProperties) not found by reflection.");

                        object skyfaller = make.Invoke(null, new object[] { airdropDef, contents, props });
                        if (skyfaller == null) return Fail("MakeAirdrop returned null.");
                        Thing skyfallerThing = (Thing)skyfaller;
                        GenSpawn.Spawn(skyfallerThing, cell, map);
                        if (!skyfallerThing.Spawned)
                            return Fail("GenSpawn.Spawn failed for the airdrop skyfaller at " + cell + " - it exists but is not placed on the map.");

                        return new
                        {
                            success = true,
                            kind,
                            at = new { x = cell.x, z = cell.z },
                            spawned = new { thingId = skyfallerThing.ThingID, def = skyfallerDefName },
                            contents = contents.Select(c => new { def = c.def.defName, stackCount = c.stackCount }).ToList(),
                        };
                    }
                    else
                    {
                        if (string.IsNullOrEmpty(pawn)) return Fail("'pawn' is required for kind='paratrooper'.");
                        string perr;
                        Pawn p = FindPawn(pawn, out perr);
                        if (p == null) return Fail(perr);
                        if (!map.mapPawns.FreeColonists.Contains(p))
                            return Fail("'" + pawn + "' is not a free colonist on the current map - the debug action only lists those.");

                        MethodInfo make = makerType.GetMethod("MakeAirdrop", VfPubStatic, null,
                            new[] { airdropDefType, typeof(Thing), propsType.MakeByRefType() }, null);
                        if (make == null)
                            return Fail("AirdropSkyfallerMaker.MakeAirdrop(AirdropDef, Thing, in AirdropProperties) not found by reflection.");

                        object skyfaller = make.Invoke(null, new object[] { airdropDef, p, props });
                        if (skyfaller == null) return Fail("MakeAirdrop returned null.");
                        Thing skyfallerThing = (Thing)skyfaller;
                        GenSpawn.Spawn(skyfallerThing, cell, map);
                        if (!skyfallerThing.Spawned)
                            return Fail("GenSpawn.Spawn failed for the airdrop skyfaller at " + cell + " - " +
                                p.LabelShortCap + " was already handed to MakeAirdrop as its payload; check the " +
                                "pawn's state directly rather than trusting this call's success.");

                        return new
                        {
                            success = true,
                            kind,
                            at = new { x = cell.x, z = cell.z },
                            spawned = new { thingId = skyfallerThing.ThingID, def = skyfallerDefName },
                            pawn = new { thingId = p.ThingID, label = p.LabelShortCap },
                        };
                    }
                }
                catch (Exception ex)
                {
                    return Fail("MakeAirdrop threw: " + (ex.InnerException ?? ex).Message);
                }
            });
        }

        private static Thing MakeStacked(ThingDef def)
        {
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = UnityEngine.Random.Range(1, Math.Max(2, def.stackLimit));
            return t;
        }
    }
}
