using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Vehicles;
using Verse;

namespace JawaIonWeapons
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
                Log.Warning("[JawaIonWeapons] Vehicle Framework is not loaded; the vehicle ion "
                    + "tier is skipped. Pawn/droid/mech tiers are unaffected.");
                return;
            }

            try
            {
                VehicleIonPatches.Apply(new Harmony("mandrake.jawaionweapons.vehicletier"));
            }
            catch (Exception ex)
            {
                Log.Error("[JawaIonWeapons] Failed to patch the vehicle ion tier: " + ex);
            }
        }
    }

    /// <summary>
    /// VEHICLE_ION_TIER_1 - closes the gap found reading VF's own damage pipeline:
    /// firing JawaIon_Damage at a Vehicle Framework vehicle currently does plain
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
    /// JawaIon_Damage is a distinct DamageDef, so that path never fires for it
    /// either.
    ///
    /// THE FIX mirrors DamageWorker_IonBuildup.ApplyMachineTier's own trick for
    /// pawns exactly: after the vehicle's real damage has been applied (so raw
    /// component damage is unaffected), fire a SECOND, synthetic hit built from
    /// literal DamageDefOf.EMP straight at statHandler.TakeDamage - that is a
    /// genuine EMP DamageInfo by identity, so ElectrifyAllComponents runs for
    /// real, using VF's own stun/adaptation machinery rather than reimplementing
    /// it.
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
    /// hard reference to JawaIonWeapons.dll's own IonDamageDef type - this
    /// assembly targets net48 (Vehicles.dll/SmashTools.dll are net48; the main
    /// JawaIonWeapons.csproj stays net472, matching DesertVehicleReskin's own
    /// reason for splitting a Harmony/Vehicles-dependent patch into its own
    /// sub-project) and reflection keeps the two build outputs load-order
    /// independent - this one does not need JawaIonWeapons.dll to have built
    /// first. A miss REFUSES (falls back to the def's own default, matching
    /// IonDamageDef's field initializer) rather than silently reading zero.
    /// </summary>
    public static class VehicleIonPatches
    {
        private const string IonDamageDefName = "JawaIon_Damage";
        private const float FallbackEmpAmountDroid = 24f;

        public static void Apply(Harmony harmony)
        {
            MethodInfo preApplyDamage = AccessTools.Method(typeof(VehiclePawn),
                nameof(VehiclePawn.PreApplyDamage));
            if (preApplyDamage == null)
            {
                Log.Error("[JawaIonWeapons] VehiclePawn.PreApplyDamage not found by reflection - "
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

            float empAmountDroid = ReadFloatField(def, "empAmountDroid", FallbackEmpAmountDroid);
            if (empAmountDroid <= 0f) return;

            IntVec2 size = vehicleDef.Size;
            float footprintArea = Math.Max(1, size.x * size.z);
            float amount = empAmountDroid / footprintArea;
            if (amount <= 0f) return;

            DamageInfo emp = new DamageInfo(
                DamageDefOf.EMP,
                amount,
                0f,
                dinfo.Angle,
                dinfo.Instigator,
                null,
                dinfo.Weapon,
                DamageInfo.SourceCategory.ThingOrUnknown,
                dinfo.IntendedTarget);
            emp.SetIgnoreArmor(true);

            // Directly at the stat handler, NOT __instance.TakeDamage(...) - that
            // would re-enter Thing.TakeDamage -> PreApplyDamage -> THIS postfix.
            // dinfo.Def is genuinely DamageDefOf.EMP here (not JawaIon_Damage), so
            // the defName guard above would already stop a re-entry from looping,
            // but going straight to the stat handler skips the round trip entirely.
            statHandler.TakeDamage(emp);
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
