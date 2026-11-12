// SUMP_SINKING_RITE_BUILD_1: the Sinking's Harmony patches. Each class's Prepare() returns false when its target (a soft
// dependency) is not loaded, so a missing mod costs only that effect; PatchFeature turns the matching setting off if a
// patch fails to apply. Nothing here touches Imperial Heat: the hold-off only delays and refuses Imperial incidents.
using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    internal static class SinkingPatchUtil
    {
        public static MethodBase Find(string typeName, string method)
        {
            Type t = AccessTools.TypeByName(typeName);
            return t == null ? null : AccessTools.DeclaredMethod(t, method);
        }
    }

    // ---------------------------------------------------------------- beast lull (pitch rider)

    /// <summary>Dig cause: a deep lottery roll's BeastWakeRequested relay is refused while the beast lull holds.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: beast lull refuses the dig wake", typeof(RM_NinefoldSettings), "sinkingBeastLullEnabled")]
    public static class Patch_Sinking_DigWake
    {
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RimMandrake.EnvironmentalHazards.RM_CompBeastWakeRelay", "OnBeastWakeRequested"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static bool Prefix(Map map) => SinkingGlue.WakeAllowed(map, SinkingWakeCause.Dig);
    }

    /// <summary>Pump cause: the bulge's working-pump wake poll is skipped while the beast lull holds.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: beast lull refuses the pump wake", typeof(RM_NinefoldSettings), "sinkingBeastLullEnabled")]
    public static class Patch_Sinking_PumpWake
    {
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RimMandrake.EnvironmentalHazards.RM_CompBulgePumpWake", "CompTick"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static bool Prefix(ThingComp __instance) => SinkingGlue.WakeAllowed(__instance?.parent?.MapHeld, SinkingWakeCause.Pump);
    }

    /// <summary>Construction cause: vanilla CompWakeUpDormant.TickRareWorker holds the wakeUpOnThingConstructedRadius check;
    /// it is skipped for RM_BeastBulge only, while the lull holds. Damage and explosions wake through PostPostApplyDamage,
    /// which is not touched, so a GenExplosion still wakes the bulge.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: beast lull refuses the construction wake", typeof(RM_NinefoldSettings), "sinkingBeastLullEnabled")]
    public static class Patch_Sinking_ConstructionWake
    {
        private static MethodBase target;
        public static bool Prepare()
        {
            if (AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_CompBulgePumpWake") == null) return false;
            target = AccessTools.DeclaredMethod(typeof(CompWakeUpDormant), "TickRareWorker");
            return target != null;
        }
        public static MethodBase TargetMethod() => target;
        public static bool Prefix(CompWakeUpDormant __instance)
        {
            Thing p = __instance?.parent;
            if (p?.def == null || p.def.defName != SinkingGlue.BulgeDef) return true;
            return SinkingGlue.WakeAllowed(p.MapHeld, SinkingWakeCause.Construction);
        }
    }

    // ---------------------------------------------------------------- trap fizzle (dig-find rider)

    /// <summary>A trap roll while the counter holds fizzles: no fuse, no explosion, one charge spent, and the click, hiss
    /// and puff of tar to read it by.</summary>
    [HarmonyPatch]
    // Review item 8 skipped on purpose: not calling ArmTrap (the find fizzles instead of arming) IS the spec's "disarm".
    [RimMandrake.Shared.PatchFeature("Sinking: dig-find trap fizzle", typeof(RM_NinefoldSettings), "sinkingTrapFizzleEnabled")]
    public static class Patch_Sinking_TrapFizzle
    {
        private static MethodBase target;
        private static PropertyInfo armedP;
        public static bool Prepare()
        {
            target = SinkingPatchUtil.Find("RimMandrake.EnvironmentalHazards.RM_CompWorkedLottery", "ArmTrap");
            armedP = target == null ? null : AccessTools.Property(target.DeclaringType, "TrapArmed");
            return target != null && armedP != null;
        }
        public static MethodBase TargetMethod() => target;
        public static int Fizzled;
        public static bool Prefix(ThingComp __instance)
        {
            if (__instance?.parent == null || !__instance.parent.Spawned) return true;
            if ((bool)armedP.GetValue(__instance)) return true; // already burning: vanilla returns early anyway
            Map map = __instance.parent.Map;
            MapComponent_SinkingTraps comp = MapComponent_SinkingTraps.For(map);
            if (comp == null || !comp.TryFizzle()) return true;
            Fizzled++;
            Vector3 v = __instance.parent.TrueCenter();
            FleckMaker.ThrowMicroSparks(v, map);
            FleckMaker.ThrowSmoke(v, map, 0.8f);
            FleckMaker.ThrowSmoke(v, map, 1.1f);
            Messages.Message("Click... a hiss, and a puff of tar. The trap in the shaft fizzled (" + comp.Remaining + " more the tar will spoil).",
                             new TargetInfo(__instance.parent.Position, map), MessageTypeDefOf.NeutralEvent, false);
            return false;
        }
    }

    /// <summary>The counter on the dig shaft's inspect pane.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: trap counter on the shaft", typeof(RM_NinefoldSettings), "sinkingTrapFizzleEnabled")]
    public static class Patch_Sinking_TrapInspect
    {
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RimMandrake.EnvironmentalHazards.RM_CompWorkedLottery", "CompInspectStringExtra"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static void Postfix(ThingComp __instance, ref string __result)
        {
            int n = MapComponent_SinkingTraps.For(__instance?.parent?.MapHeld)?.Remaining ?? 0;
            if (n <= 0) return;
            string line = "Sunk for the dig: the next " + n + " trap" + (n == 1 ? "" : "s") + " will fizzle";
            __result = string.IsNullOrEmpty(__result) ? line : __result + "\n" + line;
        }
    }

    // ---------------------------------------------------------------- the Imperial hold-off

    /// <summary>While the hold-off holds on the target map, no Imperial faction may be picked as a raid source.</summary>
    [HarmonyPatch(typeof(IncidentWorker_RaidEnemy), "FactionCanBeGroupSource")]
    [RimMandrake.Shared.PatchFeature("Sinking: Imperial hold-off refuses Imperial raid sources", typeof(RM_NinefoldSettings), "sinkingHoldOffEnabled")]
    public static class Patch_Sinking_ImperialSource
    {
        public static void Postfix(Faction f, IncidentParms parms, ref bool __result)
        {
            if (!__result || !RM_NinefoldSettings.sinkingEnabled || !RM_NinefoldSettings.sinkingHoldOffEnabled) return;
            if (SinkingGlue.IsImperial(f) && SinkingGlue.Active(parms?.target as Map, SinkingGlue.HoldOffDef)) __result = false;
        }
    }

    /// <summary>When EmpirePursuit reschedules its ladder during a hold-off, the fresh schedule is moved out again.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: Imperial hold-off follows a rescheduled ladder", typeof(RM_NinefoldSettings), "sinkingHoldOffEnabled")]
    public static class Patch_Sinking_LadderReschedule
    {
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids", "ScheduleLadder"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static void Postfix(Map map)
        {
            if (!RM_NinefoldSettings.sinkingEnabled || !RM_NinefoldSettings.sinkingHoldOffEnabled) return;
            if (SinkingGlue.Active(map, SinkingGlue.HoldOffDef))
                SinkingGlue.MoveImperialTimers(map, RM_NinefoldSettings.sinkingHoldOffMultiplier);
        }
    }

    /// <summary>EmpirePursuit's own clock: its raids are fired with parms.forced (FireRaid_NewTemp), which TryFire and
    /// FactionCanBeGroupSource both let through. So on every pursuit tick, before the scenpart reads its timers, each held
    /// map's pending raid and warning timers are pushed to after the hold-off's end (kernel ShiftPastHoldOff: never
    /// lost, never sooner, the warning-to-raid gap kept).</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: Imperial hold-off holds EmpirePursuit's timers", typeof(RM_NinefoldSettings), "sinkingHoldOffEnabled")]
    public static class Patch_Sinking_PursuitTick
    {
        public static int Moved;
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids", "Tick"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static void Prefix(object __instance)
        {
            if (!RM_NinefoldSettings.sinkingEnabled || !RM_NinefoldSettings.sinkingHoldOffEnabled) return;
            if (Find.TickManager.TicksGame % SinkingGlue.PursuitInterval != 0) return;
            Moved += SinkingGlue.GuardPursuitTimers(__instance);
        }
    }

    /// <summary>The waves the timers do not hold (the second raid and endless waves fire off a past raid tick): a pursuit
    /// raid on a held map is not fired but kept in MapComponent_SinkingHeldRaids, which fires it once the hold-off ends.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: Imperial hold-off defers EmpirePursuit's raids", typeof(RM_NinefoldSettings), "sinkingHoldOffEnabled")]
    public static class Patch_Sinking_PursuitRaid
    {
        public static int Deferred;
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids", "FireRaid_NewTemp"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static bool Prefix(Map map, float pointsMultiplier, float minPoints)
        {
            if (!SinkingGlue.HeldOff(map)) return true;
            MapComponent_SinkingHeldRaids held = map.GetComponent<MapComponent_SinkingHeldRaids>();
            if (held == null) return true; // no keeper on this map: never lose the raid
            held.Hold(pointsMultiplier, minPoints);
            Deferred++;
            return false;
        }
    }

    /// <summary>The ladder (MapComponent_EmpireSearch.FireNextRung: probe, spotter, bombardment, raid rung): on a held map
    /// the rung does not fire; it returns a postpone to one pursuit tick past the hold-off, which TickLadder writes into
    /// the raid and warning timers.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Sinking: Imperial hold-off postpones the ladder's rungs", typeof(RM_NinefoldSettings), "sinkingHoldOffEnabled")]
    public static class Patch_Sinking_LadderRung
    {
        public static int Postponed;
        private static MethodBase target;
        public static bool Prepare() { target = SinkingPatchUtil.Find("RuthlessPursuingMechanoids.MapComponent_EmpireSearch", "FireNextRung"); return target != null; }
        public static MethodBase TargetMethod() => target;
        public static bool Prefix(object __instance, ref int __result)
        {
            Map map = (__instance as MapComponent)?.map;
            int end = SinkingGlue.HoldOffEnd(map);
            if (end < 0) return true;
            long wait = (long)end - Find.TickManager.TicksGame + SinkingGlue.PursuitInterval;
            __result = wait > int.MaxValue / 2 ? int.MaxValue / 2 : (int)Math.Max(SinkingGlue.PursuitInterval, wait);
            Postponed++;
            return false;
        }
    }

    /// <summary>The storyteller's door: Imperial incidents aimed at a held map are refused (they come later, never
    /// sooner); ordinary non-Imperial enemy raids pass at the lowered chance while the tar lull holds. Queued, forced and
    /// quest incidents always pass.</summary>
    [HarmonyPatch(typeof(Storyteller), nameof(Storyteller.TryFire))]
    [RimMandrake.Shared.PatchFeature("Sinking: hold-off and raid lull at the storyteller", typeof(RM_NinefoldSettings), "sinkingRaidLullEnabled")]
    public static class Patch_Sinking_TryFire
    {
        public static int LullRefused, HoldOffRefused;

        public static bool Prefix(FiringIncident fi, bool queued, ref bool __result)
        {
            if (!RM_NinefoldSettings.sinkingEnabled || queued || fi?.parms == null || fi.def == null) return true;
            IncidentParms parms = fi.parms;
            if (parms.forced || parms.quest != null || fi.sourceQuestPart != null) return true;
            Map map = parms.target as Map;
            if (map == null) return true;
            bool imperial = SinkingGlue.IsImperial(parms.faction);
            if (imperial)
            {
                if (RM_NinefoldSettings.sinkingHoldOffEnabled && SinkingGlue.Active(map, SinkingGlue.HoldOffDef))
                {
                    HoldOffRefused++;
                    __result = false;
                    return false;
                }
                return true;
            }
            if (!typeof(IncidentWorker_RaidEnemy).IsAssignableFrom(fi.def.workerClass)) return true;
            float mult = SinkingKernel.RaidChanceMultiplier(SinkingGlue.Config(), SinkingGlue.Active(map, SinkingGlue.RaidLullDef));
            if (mult >= 1f || SinkingKernel.RaidRollFires(Rand.Value, mult)) return true; // no lull: no roll, the RNG stream untouched
            LullRefused++;
            __result = false;
            return false;
        }
    }
}
