using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Vehicles;
using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons
{
    /// <summary>
    /// Harmony bootstrap for the Vehicle Framework ion tier. Deliberately mentions
    /// no Vehicles type at the module level beyond what the AppDomain probe needs -
    /// same reasoning as DesertVehicleReskinMod: if Vehicle Framework is absent the
    /// JIT never has to resolve one, so this assembly degrades to a no-op instead
    /// of throwing a TypeLoadException at startup.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class JawaIonVehicleTierMod
    {
        static JawaIonVehicleTierMod()
        {
            bool vehiclesLoaded = AppDomain.CurrentDomain.GetAssemblies()
                .Any(assembly => assembly.GetName().Name == "Vehicles");
            if (!vehiclesLoaded)
            {
                Log.Warning("[RimMandrake.StarWars.JawaIonWeapons] Vehicle Framework is not loaded; the vehicle ion "
                    + "tier is skipped. Pawn/droid/mech tiers are unaffected.");
                return;
            }

            try
            {
                VehicleIonPatches.Apply(new Harmony("mandrake.rsw.ionweapons.vehicletier"));
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.JawaIonWeapons] Failed to patch the vehicle ion tier: " + ex);
            }
        }
    }

    /// <summary>
    /// VEHICLE_ION_TIER_1 - closes the gap found reading VF's own damage pipeline:
    /// firing RSW_JawaIon_Damage at a Vehicle Framework vehicle currently does plain
    /// component damage and NOTHING ELSE. Traced end to end, not guessed:
    ///
    ///   Verse.Thing.TakeDamage(DamageInfo)   <- normal combat calls THIS overload
    ///     -> Pawn.PreApplyDamage(ref dinfo, out absorbed)   <- virtual hook
    ///          VehiclePawn OVERRIDES this and unconditionally sets absorbed=true
    ///          after routing everything into statHandler.TakeDamage(dinfo).
    ///          "absorbed=true" makes Thing.TakeDamage return BEFORE it ever
    ///          reaches dinfo.Def.Worker.Apply(...) - which is where
    ///          DamageWorker_IonBuildup (machine/droid/flesh tiering) lives.
    ///          So that worker NEVER RUNS on a vehicle, full stop.
    ///
    /// VehicleStatHandler.TakeDamage has its OWN EMP-specific path -
    /// ElectrifyAllComponents, which stuns the vehicle via the same
    /// vehicle.stances.stunner.StunFor(...) call a pawn's stunner uses - but it is
    /// gated on `defApplied == DamageDefOf.EMP` by literal object identity, and
    /// RSW_JawaIon_Damage is a distinct DamageDef, so that path never fires for it
    /// either.
    ///
    /// 🔴 CORRECTED 2026-08-30, first live test (quicktest, game UP): the original
    /// version of this file routed a synthetic EMP hit through
    /// statHandler.TakeDamage(emp) to reach ElectrifyAllComponents - registered
    /// fine (confirmed via jawa/harmony_patches) but produced NO stun on a
    /// VVE_Mule. Traced why with a CONTROL: firing genuine vanilla DamageDefOf.EMP
    /// at the same vehicle via jawa/damage ALSO produced zero stun - so the gap was
    /// never this patch, it is VehicleComponent.ApplyEMPDamage itself
    /// (Source/Vehicles/Components/Vehicles/Health/VehicleComponent.cs:153-166):
    /// `if (!vehicle.VehicleDef.properties.empStuns) return 0;` - a per-VehicleDef
    /// XML OPT-IN, unset (default false) on every vehicle in Vanilla Vehicles
    /// Expanded (grepped the whole mod, zero hits for "empStuns" - confirmed, not
    /// assumed). Even with it set, the stun is further gated behind
    /// `Rand.Chance(chanceToStun)` per component. Riding VF's own mechanism would
    /// have meant "the ion gun never stuns any real vehicle in this campaign,"
    /// which fails the actual ask.
    ///
    /// THE FIX now stuns directly: vehicle.stances.stunner.StunFor(...), the exact
    /// vanilla StunHandler API (RimWorld/StunHandler.cs, read via RimSage: `public
    /// void StunFor(int ticks, Thing instigator, ...)`) VF's own
    /// ElectrifyAllComponents calls internally - same primitive, no dependency on
    /// VF's opt-in flag or its per-component chance roll. Ticks computed the same
    /// "amount * 30" convention DamageWorker_IonBuildup.ApplyMachineTier documents
    /// for pawns. ⚠️ NOT resistance-adjusted: the pawn tiers reach StunFor through
    /// vanilla's own damage->CanBeStunnedByDamage->StunHandler pathway, which folds
    /// in StatDefOf.EMPResistance before calling StunFor; calling StunFor directly
    /// here skips that computation entirely. Whether a vehicle even HAS a
    /// meaningful EMPResistance value was not checked - flagged as an open
    /// question, not asserted either way.
    ///
    /// 🔴 ROOT CAUSE FOUND 2026-08-30, live trace logging: StunFor was called with the
    /// right ticks and had NO effect (StunTicksLeft read back 0 immediately after).
    /// VF prefixes RimWorld.StunHandler.StunFor with its OWN Harmony patch,
    /// Patch_HealthAndStats.StunVehicle (Vehicles.dll, priority 400):
    ///     if (___parent is VehiclePawn vehicle) return vehicle.statHandler.OverrideStunPatch;
    /// i.e. a vehicle can NEVER be stunned by ANY caller - vanilla, modded, or ours -
    /// unless VehicleStatHandler.OverrideStunPatch is true. It is `{ get; private set; }`
    /// (VehicleStatHandler.cs:75); ElectrifyAllComponents is the only place that ever sets
    /// it, true immediately before its own StunFor call and back to false in a finally
    /// (VehicleStatHandler.cs:750/793, comment: "EMP Damage may stun, disable stun patch
    /// temporarily to allow for StunFor to pass through"). This postfix now does exactly
    /// that around its own StunFor call, via the property's private setter (reflection,
    /// since it is private) - no new mechanism, the vendored source is the template.
    /// Trace logging removed now that the cause is confirmed and fixed.
    ///
    /// TIER AND SCALING - owner ruling, 2026-08-29 (ION vehicle follow-up to
    /// ION_STUN_IGNORES_BODY_SIZE_1): vehicles sit at the DROID tier
    /// (empAmountDroid - "droids & vehicles: strong" is D1's own wording), scaled
    /// by an ESTIMATE of the vehicle's volume difference from a droid, applied
    /// LINEARLY (not squared like the flesh/body-size tier - a droid and a
    /// gravship-scale vehicle are compared by rough size, not by the same curve
    /// that makes a 32x-bodySize creature nearly unstunnable by hand fire).
    /// RimWorld has no per-Thing height dimension, so footprint AREA
    /// (VehicleDef.Size.x * Size.z) is the volume estimate - the reference point
    /// is a droid's own measured footprint, 1x1 (OuterRim_BattleDroid, def dump
    /// 2026-08-29T20-07-29Z: size 1x1, baseBodySize 1), so a droid's area is 1
    /// and the divisor is the vehicle's footprint area directly:
    ///
    ///     amount = empAmountDroid / (VehicleDef.Size.x * VehicleDef.Size.z)
    ///
    /// Worked examples off the live def dump's actual VF/VVE vehicle footprints:
    ///   VVE_Dirtbike        1x1  (area 1)   amount = 24    (same as a droid)
    ///   VVE_Mule/Highwayman 2x4  (area 8)   amount = 3     (~8x the hits)
    ///   VVE_Warbird         5x5  (area 25)  amount = 0.96  (~25x the hits)
    ///
    /// empAmountDroid ITSELF IS READ BY REFLECTION, not hardcoded here and not a
    /// hard reference to RimMandrake.StarWars.JawaIonWeapons.dll's own IonDamageDef type - this
    /// assembly targets net48 (Vehicles.dll/SmashTools.dll are net48; the main
    /// RimMandrake.StarWars.JawaIonWeapons.csproj stays net472, matching RimMandrake.DesertVehicleReskin's own
    /// reason for splitting a Harmony/Vehicles-dependent patch into its own
    /// sub-project) and reflection keeps the two build outputs load-order
    /// independent - this one does not need RimMandrake.StarWars.JawaIonWeapons.dll to have built
    /// first. A miss REFUSES (falls back to the def's own default, matching
    /// IonDamageDef's field initializer) rather than silently reading zero.
    /// </summary>
    public static class VehicleIonPatches
    {
        private const string IonDamageDefName = "RSW_JawaIon_Damage";
        private const float FallbackEmpAmountDroid = 24f;

        public static void Apply(Harmony harmony)
        {
            MethodInfo preApplyDamage = AccessTools.Method(typeof(VehiclePawn),
                nameof(VehiclePawn.PreApplyDamage));
            if (preApplyDamage == null)
            {
                Log.Error("[RimMandrake.StarWars.JawaIonWeapons] VehiclePawn.PreApplyDamage not found by reflection - "
                    + "Vehicle Framework's API has moved. Vehicle ion tier not applied.");
                return;
            }

            harmony.Patch(preApplyDamage,
                postfix: new HarmonyMethod(typeof(VehicleIonPatches), nameof(Postfix)));
        }

        /// <summary>
        /// Runs AFTER VehiclePawn's own PreApplyDamage, so the vehicle has already
        /// taken its real component damage from this same hit. Non-ref/out
        /// parameters here are read-only views on purpose - this never changes
        /// what the original method decided.
        /// </summary>
        public static void Postfix(VehiclePawn __instance, DamageInfo dinfo, bool absorbed)
        {
            if (!absorbed) return;

            DamageDef def = dinfo.Def;
            if (def == null || def.defName != IonDamageDefName) return;

            VehicleStatHandler statHandler = __instance?.statHandler;
            VehicleDef vehicleDef = __instance?.VehicleDef;
            if (statHandler == null || vehicleDef == null) return;

            if (__instance.stances?.stunner == null) return;

            float empAmountDroid = ReadFloatField(def, "empAmountDroid", FallbackEmpAmountDroid);
            if (empAmountDroid <= 0f) return;

            IntVec2 size = vehicleDef.Size;
            float footprintArea = Math.Max(1, size.x * size.z);
            float amount = empAmountDroid / footprintArea;
            if (amount <= 0f) return;

            int stunTicks = Mathf.RoundToInt(amount * 30f);
            if (stunTicks <= 0) return;

            // VEHICLE_ION_TIER_1 - VF's own Patch_HealthAndStats.StunVehicle prefixes
            // RimWorld.StunHandler.StunFor and skips the original call for any VehiclePawn
            // unless VehicleStatHandler.OverrideStunPatch is true. ElectrifyAllComponents is
            // VF's only caller that sets it, true right before its own StunFor and back to
            // false in a finally - mirrored here exactly, via the property's private setter.
            if (OverrideStunPatchSetter == null)
            {
                Log.Error("[RimMandrake.StarWars.JawaIonWeapons] VehicleStatHandler.OverrideStunPatch setter not found by "
                    + "reflection - Vehicle Framework's API has moved. Vehicle stun skipped.");
                return;
            }

            SetOverrideStunPatch(statHandler, true);
            try
            {
                __instance.stances.stunner.StunFor(stunTicks, dinfo.Instigator);
            }
            finally
            {
                SetOverrideStunPatch(statHandler, false);
            }
        }

        private static readonly MethodInfo OverrideStunPatchSetter = AccessTools.PropertySetter(
            typeof(VehicleStatHandler), nameof(VehicleStatHandler.OverrideStunPatch));

        private static void SetOverrideStunPatch(VehicleStatHandler statHandler, bool value)
        {
            OverrideStunPatchSetter.Invoke(statHandler, new object[] { value });
        }

        private static float ReadFloatField(object obj, string fieldName, float fallback)
        {
            if (obj == null) return fallback;
            try
            {
                FieldInfo fi = obj.GetType().GetField(fieldName, BindingFlags.Public | BindingFlags.Instance);
                if (fi == null) return fallback;
                object value = fi.GetValue(obj);
                return value is float f ? f : fallback;
            }
            catch (Exception)
            {
                return fallback;
            }
        }
    }
}
