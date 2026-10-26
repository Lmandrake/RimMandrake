using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FIRE_BAN_1 — the real engine hook points, read off the
    // decompiled 1.6 source (RimSage), not assumed:
    //
    // 1) Every `Fire` Thing spawns through one of TWO methods (grep of
    //    `ThingMaker.MakeThing(ThingDefOf.Fire)` in decompiled 1.6 finds
    //    exactly FireUtility.cs:85 and :115):
    //    a) FireUtility.TryStartFireIn(IntVec3, Map, float, Thing, SimpleCurve)
    //       — a fire in a cell: DamageWorker_Flame / DamageWorker_Vaporize
    //       explosion cells, Explosion.cs's own spread, PowerBeam,
    //       Verb_ShootBeam, Bullet (incendiary ammo), Bombardment,
    //       Verb_Ignite, FlameThrower, SteadyEnvironmentEffects (lightning),
    //       Spark, ShortCircuitUtility, Fire.cs's TrySpread/TryBurnFloor.
    //    b) FireUtility.TryAttachFire(this Thing, float, Thing) — a fire on
    //       a pawn (CanEverAttachFire: pawns only): DamageWorker_Flame's
    //       victim, Thing.TakeDamage's igniteChanceByTargetFlammability,
    //       FlameThrower and Verb_ShootBeam hits, HediffGiver_Terrain,
    //       Fire.cs's attach to pawns in its cell
    //       (CHILLFIREBAN_FIX_ATTACHED_FIRE_UNGATED: without this second
    //       prefix an incendiary still set pawns alight on the seabed).
    //    Those are vanilla's only doors, not every mod's: a Fire a mod makes
    //    and spawns itself is caught at Fire.SpawnSetup and put out on its
    //    first tick (Patch_Fire_SpawnSetup, CHILLFIREBAN_FIX_MODDED_DIRECT_FIRE_SPAWN).
    //    Both prefixes ask with the INSTIGATOR, so Fuselight's own
    //    explosion still burns (RM_SelfOxidizingExtension) and a fission
    //    Genetron's meltdown flame does not (RM_NonCombustionExtension is
    //    not an oxidizer: CHILLFIREBAN_FIX_MELTDOWN_FIRE_ESCAPES_BAN). The fire Fuselight's
    //    flash lights does not inherit its oxidizer (Patch_Fire_TickInterval, Patch_Spark_Impact,
    //    Patch_Pawn_Kill_CorpseFire), and an explosion is named for the thing that explodes, not for
    //    whoever set it off (Patch_CompExplosive_Detonate).
    //
    // 2) CompRefuelable.ShouldBeLitNow() is NOT wired through
    //    TryStartFireIn at all — a campfire/torch/brazier never spawns a
    //    `Fire` Thing; "lit" is a pure `HasFuel` read, polled live wherever
    //    it's asked. It IS what CompGlower checks (CompGlower.ShouldBeLitNow
    //    loops every IThingGlower comp on the parent and calls its
    //    ShouldBeLitNow(), and CompRefuelable declares
    //    `: ThingComp_VacuumAware, IThingGlower` precisely so that loop
    //    reaches it) — so this postfix is what actually turns the light/
    //    glow off, and by extension what starves FocusStrengthOffset_Lit's
    //    meditation bonus. Postfixing this one non-virtual method also
    //    answers BOTH halves of the item's open question at once, because
    //    nothing here is a cached flag: a fuel-burning building never
    //    lights on the Chill seabed, AND one already burning when the map
    //    is entered/loaded goes dark on its very next query — there is no
    //    separate "already lit" state to chase down and clear.
    //
    // 3) CompHeatPusherPowered.ShouldPushHeatNow reads refuelableComp.HasFuel
    //    DIRECTLY (not ShouldBeLitNow()), so patch (2) alone does NOT stop
    //    a fuel-burning heater's actual heat output — confirmed by reading
    //    CompHeatPusherPowered.cs itself. This third postfix is what makes
    //    "heat becomes electric-only" literally true: it only fires when
    //    the comp is fuel-driven (refuelableComp present via
    //    parent.TryGetComp<CompRefuelable>()); a pure CompPowerTrader-driven
    //    (electric) heater is untouched, on the Chill seabed or anywhere
    //    else — that's the whole point CHILL_THERMAL_ENGINE_1 needs to
    //    hold.
    //
    // 4) CompFireOverlay.PostDraw ALSO reads refuelableComp.HasFuel
    //    DIRECTLY, bypassing ShouldBeLitNow() a second time — confirmed by
    //    reading CompFireOverlay.cs itself (its PostDraw and CompTick both
    //    check `refuelableComp == null || refuelableComp.HasFuel`, never
    //    ShouldBeLitNow()). Without this fourth prefix a campfire that is
    //    genuinely unlit (no glow, no heat, patch 2/3 both firing) would
    //    still visually draw its flame sprite every frame — a real
    //    fizzle has no flame to look at either, so this prefix skips the
    //    draw call outright on a banned cell.
    //
    // All of them route through RM_ChillFireGate.IsIgnitionAllowed, so the
    // map-identity check (RM_TheChill AND IsPocketMap), the settings
    // toggles, the oxygenated-zone override and the self-oxidizing
    // (Fuselight) exemption all live in exactly one place.
    // ════════════════════════════════════════════════════════════════════

    [HarmonyPatch(typeof(FireUtility), nameof(FireUtility.TryStartFireIn))]
    public static class Patch_FireUtility_TryStartFireIn
    {
        public static bool Prefix(IntVec3 c, Map map, Thing instigator, ref bool __result, out bool __state)
        {
            __state = RM_ChillFireGate.IsIgnitionAllowed(map, c, instigator);
            if (__state)
            {
                RM_ChillFireGate.admittingFire++; // the Fire this spawns was asked for (Patch_Fire_SpawnSetup)
                return true; // run the vanilla method normally
            }
            __result = false; // no oxygen down here — the fire simply never catches
            return false;
        }

        public static void Finalizer(bool __state)
        {
            if (__state)
            {
                RM_ChillFireGate.admittingFire--;
            }
        }
    }

    // Hook (1b). A pawn's attached fire is asked at the pawn's cell; nothing to return, so skipping the body is the ban.
    [HarmonyPatch(typeof(FireUtility), nameof(FireUtility.TryAttachFire))]
    public static class Patch_FireUtility_TryAttachFire
    {
        public static bool Prefix(Thing t, Thing instigator, out bool __state)
        {
            __state = t == null || !t.Spawned || RM_ChillFireGate.IsIgnitionAllowed(t.Map, t.Position, instigator);
            if (__state)
            {
                RM_ChillFireGate.admittingFire++; // (t unspawned: vanilla decides; CanEverAttachFire refuses it anyway)
            }
            return __state;
        }

        public static void Finalizer(bool __state)
        {
            if (__state)
            {
                RM_ChillFireGate.admittingFire--;
            }
        }
    }

    // CHILLFIREBAN_FIX_MODDED_DIRECT_FIRE_SPAWN. The two prefixes above are the only doors vanilla uses, but a mod can
    // make a Fire itself: an IL scan of the owner's 320 active mods (wave 62) found VEF's FlamethrowProjectile.DoDamage
    // and TeslaProjectile.Impact doing MakeThing(Fire) + GenSpawn + AttachTo with no gate asked and no instigator set.
    // Every Fire passes Fire.SpawnSetup, so a seabed Fire that no gate admitted is judged there by the same rule
    // (RM_ChillFireBanKernel.PutOutUngatedFire) and, if refused, marked; its first TickInterval (below) destroys it
    // before it spreads or damages anything. It is not destroyed inside SpawnSetup: the mod's own AttachTo follows the
    // spawn. A Fire loaded from a save is left alone.
    [HarmonyPatch(typeof(Fire), nameof(Fire.SpawnSetup))]
    public static class Patch_Fire_SpawnSetup
    {
        internal static readonly HashSet<Fire> ungated = new HashSet<Fire>();

        public static void Postfix(Fire __instance, Map map, bool respawningAfterLoad)
        {
            if (respawningAfterLoad || RM_ChillFireGate.admittingFire > 0 || !RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return;
            }
            RM_MapComponent_ChillOxygenation oxygenation = map.GetComponent<RM_MapComponent_ChillOxygenation>();
            if (RM_ChillFireBanKernel.PutOutUngatedFire(true,
                RM_DivingSettings.masterEnabled && RM_DivingSettings.chillFireBanEnabled, false, false,
                RM_ChillFireGate.IsSelfOxidizing(__instance.instigator), RM_ChillFireGate.insideBurningFire > 0,
                oxygenation != null && oxygenation.IsCellOxygenated(__instance.Position)))
            {
                ungated.Add(__instance);
            }
        }
    }

    [HarmonyPatch(typeof(Fire), nameof(Fire.DeSpawn))]
    public static class Patch_Fire_DeSpawn
    {
        public static void Postfix(Fire __instance)
        {
            Patch_Fire_SpawnSetup.ungated.Remove(__instance);
        }
    }

    // CHILLFIREBAN_FIX_FUSELIGHT_FIRE_SPREADS. A Fire passes its instigator on: TrySpread (Fire.cs:403), the attach to a
    // pawn in its cell (:272) and DoFireDamage (`instigator ?? this`, whose Flame damage attaches via DamageWorker_Flame and
    // Thing.TakeDamage) all run inside Fire.TickInterval. Marking that scope keeps a Fuselight flash's fire from carrying
    // the flash's oxidizer into the tar and wax plants around it. Prefix + finalizer, so a throw inside the tick cannot
    // leave it raised. A Fire marked by Patch_Fire_SpawnSetup is put out here, before its first spread or damage; the
    // counter is raised first so the finalizer stays balanced when the body is skipped.
    [HarmonyPatch(typeof(Fire), "TickInterval")]
    public static class Patch_Fire_TickInterval
    {
        public static bool Prefix(Fire __instance)
        {
            RM_ChillFireGate.insideBurningFire++;
            if (Patch_Fire_SpawnSetup.ungated.Count > 0 && Patch_Fire_SpawnSetup.ungated.Remove(__instance))
            {
                if (!__instance.Destroyed)
                {
                    __instance.Destroy();
                }
                return false;
            }
            return true;
        }

        public static void Finalizer()
        {
            RM_ChillFireGate.insideBurningFire--;
        }
    }

    // CHILLFIREBAN_FIX_SPARK_CARRIES_OXIDIZER. The fifth of TrySpread's spreads (radius 10-20, Fire.cs:398)
    // goes by Spark, which lands outside the Fire's tick and re-reads the instigator (Spark.Impact: `launcher is Fire
    // fire` -> `fire.instigator`), so it would hand TryStartFireIn the Fuselight again. A Spark launched by a Fire is
    // marked like the Fire's own tick; any other launcher stays as it was.
    [HarmonyPatch(typeof(Spark), "Impact")]
    public static class Patch_Spark_Impact
    {
        public static void Prefix(Spark __instance, out bool __state)
        {
            __state = __instance.Launcher is Fire;
            if (__state)
            {
                RM_ChillFireGate.insideBurningFire++;
            }
        }

        public static void Finalizer(bool __state)
        {
            if (__state)
            {
                RM_ChillFireGate.insideBurningFire--;
            }
        }
    }

    // CHILLFIREBAN_FIX_DETONATION_INSTIGATOR_SWAP. CompExplosive.Detonate (CompExplosive.cs:252, decompiled 1.6) names its
    // explosion's instigator `(instigator == null || instigator.HostileTo(parent.Faction) && ...) ? parent : instigator`,
    // the stored instigator being whoever damaged it (StartWick(dinfo.Instigator), :175). A Fuselight has no faction, so a
    // pawn cutting one made the PAWN the instigator and the flash's own fire was banned; a chemfuel stack or shell set off
    // by the flash took the FUSELIGHT as instigator and its fire was exempt. Dropping the stored instigator first makes the
    // explosion the exploding thing itself (RM_ChillFireBanKernel.DropDetonationInstigator decides when).
    [HarmonyPatch(typeof(CompExplosive), "Detonate")]
    public static class Patch_CompExplosive_Detonate
    {
        private static readonly AccessTools.FieldRef<CompExplosive, Thing> instigatorRef =
            AccessTools.FieldRefAccess<CompExplosive, Thing>("instigator");

        public static void Prefix(CompExplosive __instance, Map map)
        {
            Thing parent = __instance.parent;
            Thing stored = instigatorRef(__instance);
            if (stored == null || parent == null || !RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return;
            }
            if (RM_ChillFireBanKernel.DropDetonationInstigator(true,
                RM_DivingSettings.masterEnabled && RM_DivingSettings.chillFireBanEnabled,
                RM_ChillFireGate.IsSelfOxidizing(parent), RM_ChillFireGate.IsSelfOxidizing(stored)))
            {
                instigatorRef(__instance) = null;
            }
        }
    }

    // CHILLFIREBAN_FIX_CORPSE_FIRE_KEEPS_OXIDIZER. Pawn.Kill (Pawn.cs:2208) relights a dying burning pawn's fire on its
    // corpse with `fire.instigator`. Outside the Fire's own tick (a bullet, bleeding out) that handed TryStartFireIn the
    // Fuselight whose flash set the pawn alight. That fire is the flash's fire burning on, not the flash: marked like
    // the Fire's tick. Inside the tick the counter is already raised; nesting is harmless.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    public static class Patch_Pawn_Kill_CorpseFire
    {
        public static void Prefix(Pawn __instance, out bool __state)
        {
            __state = __instance.Spawned && __instance.HasAttachment(ThingDefOf.Fire);
            if (__state)
            {
                RM_ChillFireGate.insideBurningFire++;
            }
        }

        public static void Finalizer(bool __state)
        {
            if (__state)
            {
                RM_ChillFireGate.insideBurningFire--;
            }
        }
    }

    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.ShouldBeLitNow))]
    public static class Patch_CompRefuelable_ShouldBeLitNow
    {
        public static void Postfix(CompRefuelable __instance, ref bool __result)
        {
            if (!__result)
            {
                return; // already unlit (out of fuel etc) — nothing to override
            }
            // Gate(): only a flame building goes dark. A fuelled powered machine's glow is an electric status light
            // (KoltoTank; CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL) and a non-combustion plant keeps its glow while it
            // keeps making power (RUT_VaultHeart; CHILLFIREBAN_FIX_NONCOMBUSTION_PLANT_BANNED).
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance.parent, __result);
        }
    }

    // Patch (3) covers CompHeatPusher.ShouldPushHeatNow AND every loaded override of it (ChillFireBanTargets), not
    // CompHeatPusherPowered's alone: VQE The Generator's CompHeatPusherPowered_Overdrive derives from CompHeatPusher and
    // never reaches CompHeatPusherPowered's getter (IL read of the owner's assemblies, CHILLFIREBAN_FIX_MODDED_OVERRIDES_BYPASS;
    // VFE Tribals' CompHeatPusher_LargeFire does call base, so it was always covered). Only a FLAME building is gated (Gate): an electric
    // heater has no CompRefuelable and keeps working — heat becomes electric-only, not nothing.
    [HarmonyPatch]
    public static class Patch_CompHeatPusherPowered_ShouldPushHeatNow
    {
        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.PropertyGetter(typeof(CompHeatPusher), nameof(CompHeatPusher.ShouldPushHeatNow)));
        }

        public static void Postfix(CompHeatPusher __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance.parent, __result);
        }
    }

    /// <summary>
    /// A vanilla method plus every override of it in the loaded assemblies. A Harmony patch on a virtual method patches
    /// that one body: an override that does not call base never runs it. The owner's list has such overrides on all three
    /// methods the ban gates (CHILLFIREBAN_FIX_MODDED_OVERRIDES_BYPASS): VQE The Generator's CompPowerPlantGenetron
    /// replaces UpdateDesiredPowerOutput and CompRefuelableWithOverdrive replaces CompTick, so a wood-fired Genetron on the
    /// seabed had its fuel frozen (CompRefuelable.CompTick, patched) while it kept making power (the override, unpatched).
    /// Patching an override that does call base runs the postfix twice; every postfix here is idempotent. Runs at mod
    /// construction, after every mod assembly is loaded.
    /// </summary>
    internal static class ChillFireBanTargets
    {
        internal static IEnumerable<MethodBase> WithOverrides(MethodInfo root)
        {
            yield return root;
            Type rootType = root.DeclaringType;
            Type baseDeclarer = root.GetBaseDefinition().DeclaringType;
            Type[] parameters = Array.ConvertAll(root.GetParameters(), p => p.ParameterType);
            foreach (Type t in AccessTools.AllTypes())
            {
                MethodInfo m;
                try
                {
                    if (t == rootType || t.ContainsGenericParameters || !rootType.IsAssignableFrom(t))
                    {
                        continue;
                    }
                    m = AccessTools.DeclaredMethod(t, root.Name, parameters);
                    if (m == null || m.IsAbstract || m.GetBaseDefinition().DeclaringType != baseDeclarer)
                    {
                        continue; // not declared here, or a `new` method that hides rather than overrides
                    }
                }
                catch (Exception)
                {
                    continue; // a type whose dependencies did not load: it cannot be instantiated either
                }
                yield return m;
            }
        }
    }

    // CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER (delegated: design, follows CHILL_FIRE_BAN_1's card ruling "total ban —
    // no flame works on the Chill seabed map. Campfires fizzle, chemfuel won't light"). A fuelled bill-giver (campfire,
    // fuelled stove, fuelled smithy) cannot work bills while the ban holds. Building_WorkTable.CurrentlyUsableForBills and
    // UsableForBillsAfterFueling both read refuelableComp.HasFuel, never ShouldBeLitNow, so patch (2) alone left them
    // cooking. BOTH are gated: WorkGiver_DoBill offers the job on UsableForBillsAfterFueling and JobDriver_DoBill drops it
    // on CurrentlyUsableForBills — gating only the second would loop pawns into a job that fails every tick. With both
    // gated a pawn never takes the bill, and never hauls fuel to it (the refuel giver is fed by the same bill scan).
    // An electric stove has no CompRefuelable and is untouched. Pumped air lifts the gate (IsIgnitionAllowed).
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.CurrentlyUsableForBills))]
    public static class Patch_BuildingWorkTable_CurrentlyUsableForBills
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance, __result);
        }
    }

    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsableForBillsAfterFueling))]
    public static class Patch_BuildingWorkTable_UsableForBillsAfterFueling
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance, __result);
        }
    }

    // Same item: a fuelled generator (wood-fired, chemfuel) makes no power while the ban holds.
    // CompPowerPlant.UpdateDesiredPowerOutput reads refuelableComp.HasFuel directly and runs every CompTick. No vanilla
    // subclass overrides it, but modded ones do (VQE's CompPowerPlantGenetron, without a base call), so the postfix goes
    // on every override too (ChillFireBanTargets). Solar, wind, geothermal, watermill, aurora collector: no CompRefuelable,
    // untouched.
    [HarmonyPatch]
    public static class Patch_CompPowerPlant_UpdateDesiredPowerOutput
    {
        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.Method(typeof(CompPowerPlant), nameof(CompPowerPlant.UpdateDesiredPowerOutput)));
        }

        public static void Postfix(CompPowerPlant __instance)
        {
            if (__instance.PowerOutput <= 0f)
            {
                return;
            }
            if (!Patch_ChillFireBan_Fuelled.Gate(__instance.parent, true))
            {
                __instance.PowerOutput = 0f;
            }
        }
    }

    // Same item: the player sees WHY the stove, campfire or generator is dead — a line on its inspect pane.
    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.CompInspectStringExtra))]
    public static class Patch_CompRefuelable_CompInspectStringExtra
    {
        public static void Postfix(CompRefuelable __instance, ref string __result)
        {
            ThingWithComps parent = __instance.parent;
            if (parent == null || !parent.Spawned)
            {
                return;
            }
            bool usesFlame = Patch_ChillFireBan_Fuelled.UsesFlame(parent);
            if (!usesFlame)
            {
                return; // cheap reject first: the gate is only asked about flame buildings
            }
            if (RM_ChillFireBanKernel.ShowNoAirNote(usesFlame,
                RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent)))
            {
                string note = "RM_ChillFireBan_NoAir".Translate();
                __result = string.IsNullOrEmpty(__result) ? note : __result + "\n" + note;
            }
        }
    }

    internal static class Patch_ChillFireBan_Fuelled
    {
        private static readonly System.Collections.Generic.Dictionary<ThingDef, bool> usesFlame =
            new System.Collections.Generic.Dictionary<ThingDef, bool>();

        /// <summary>Per-def cache of RM_ChillFireBanKernel.UsesFlame (a def's comps are fixed).</summary>
        internal static bool UsesFlame(ThingWithComps thing)
        {
            ThingDef def = thing.def;
            if (!usesFlame.TryGetValue(def, out bool result))
            {
                CompPowerTrader trader = thing.GetComp<CompPowerTrader>();
                result = RM_ChillFireBanKernel.UsesFlame(
                    thing.GetComp<CompRefuelable>() != null,
                    thing.GetComp<CompGlower>() != null,
                    thing.GetComp<CompHeatPusher>() != null,
                    thing.GetComp<CompFireOverlay>() != null,
                    def.IsWorkTable,
                    trader is CompPowerPlant,
                    trader != null,
                    def.HasModExtension<RM_NonCombustionExtension>());
                usesFlame[def] = result;
            }
            return result;
        }

        /// <summary>Gate one vanilla output of a building by the ban; anything that is not a flame building passes through.</summary>
        internal static bool Gate(ThingWithComps thing, bool vanillaOn)
        {
            if (!vanillaOn || thing?.Map == null || !Patch_ChillFireBan_Fuelled.UsesFlame(thing))
            {
                return vanillaOn;
            }
            return RM_ChillFireBanKernel.Output(vanillaOn, true,
                RM_ChillFireGate.IsIgnitionAllowed(thing.Map, thing.Position, thing));
        }
    }

    // CHILLFIREBAN_FIX_UNLIT_REFUELABLE_BURNS_FUEL: patch (2) puts the flame out, but
    // CompRefuelable.CompTick still burns ConsumptionRatePerTick whenever it is switched on — it
    // never asks ShouldBeLitNow. So a dark, cold torch, brazier or fuelled heater on the seabed
    // emptied itself and pawns hauled wood to it forever. While the ban holds, the passive burn of a
    // flame building is skipped (RM_ChillFireBanKernel.UsesFlame): a fuelled generator, or an unpowered
    // building that glows, heats, draws a flame or works bills. Work tables and generators joined the set with
    // CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER — they no longer cook or make power while banned (patches
    // above), so freezing their fuel gives nothing away. A powered consumer (kolto tank, autobong, fuel
    // processor: CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL) is a machine, not a fire, and keeps burning.
    // The skip is done at ConsumeFuel, scoped to this comp during its own CompTick, so the fuel never
    // reaches 0 and Notify_RanOutOfFuel (destroyOnNoFuel) cannot fire from a burn that did not happen.
    // Every override of CompTick is patched too (VQE's CompRefuelableWithOverdrive burns fuel in its own CompTick and never
    // calls base). An override that DOES call base (VGE's CompRefuelable_IgnoreFlickableComp) nests one tick inside the
    // other, so the finalizer restores the outer scope (__state) instead of clearing it: clearing would let the override's
    // own ConsumeFuel calls after base.CompTick() burn fuel the ban froze.
    [HarmonyPatch]
    public static class Patch_CompRefuelable_CompTick
    {
        internal static CompRefuelable suppressing;

        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.Method(typeof(CompRefuelable), nameof(CompRefuelable.CompTick)));
        }

        public static void Prefix(CompRefuelable __instance, out CompRefuelable __state)
        {
            __state = suppressing;
            ThingWithComps parent = __instance.parent;
            if (parent == null || !parent.Spawned || !IsFireOnly(parent))
            {
                return;
            }
            if (RM_ChillFireBanKernel.SkipFuelBurn(true,
                RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent)))
            {
                suppressing = __instance;
            }
        }

        public static void Finalizer(CompRefuelable __state)
        {
            suppressing = __state;
        }

        private static bool IsFireOnly(ThingWithComps parent)
        {
            return Patch_ChillFireBan_Fuelled.UsesFlame(parent);
        }
    }

    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.ConsumeFuel))]
    public static class Patch_CompRefuelable_ConsumeFuel
    {
        public static bool Prefix(CompRefuelable __instance)
        {
            return !ReferenceEquals(__instance, Patch_CompRefuelable_CompTick.suppressing);
        }
    }

    [HarmonyPatch(typeof(CompFireOverlay), nameof(CompFireOverlay.PostDraw))]
    public static class Patch_CompFireOverlay_PostDraw
    {
        public static bool Prefix(CompFireOverlay __instance)
        {
            Thing parent = __instance.parent;
            if (parent?.Map == null)
            {
                return true;
            }
            if (!RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent))
            {
                return false; // it really is out — no flame sprite to draw
            }
            return true;
        }
    }
}
